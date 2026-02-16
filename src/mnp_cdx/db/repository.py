"""DuckDB repository and schema management."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import duckdb
import pandas as pd


@dataclass
class DBRepository:
    db_path: Path

    def __post_init__(self) -> None:
        self.db_path = Path(self.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.con = duckdb.connect(str(self.db_path))

    def close(self) -> None:
        self.con.close()

    def init_schema(self) -> None:
        self.con.execute(
            """
            CREATE SEQUENCE IF NOT EXISTS seq_file_id START 1;
            CREATE SEQUENCE IF NOT EXISTS seq_operator_id START 1;

            CREATE TABLE IF NOT EXISTS ingest_file (
                file_id BIGINT PRIMARY KEY,
                filename VARCHAR NOT NULL,
                checksum_sha256 VARCHAR(64) NOT NULL UNIQUE,
                parser_version VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'OK',
                record_count BIGINT NOT NULL DEFAULT 0,
                ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS operator_dim (
                operator_id BIGINT PRIMARY KEY,
                canonical_name VARCHAR NOT NULL UNIQUE,
                group_name VARCHAR,
                type VARCHAR,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS mnp_flow_fact (
                file_id BIGINT NOT NULL,
                period_type VARCHAR NOT NULL,
                period_date DATE NOT NULL,
                donor_operator_id BIGINT NOT NULL,
                recipient_operator_id BIGINT NOT NULL,
                value DOUBLE NOT NULL,
                sheet_name VARCHAR,
                quality_flag VARCHAR NOT NULL DEFAULT 'OK',
                donor_raw VARCHAR,
                recipient_raw VARCHAR,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_flow_period ON mnp_flow_fact(period_type, period_date);
            CREATE INDEX IF NOT EXISTS idx_flow_donor ON mnp_flow_fact(donor_operator_id, period_date);
            CREATE INDEX IF NOT EXISTS idx_flow_recipient ON mnp_flow_fact(recipient_operator_id, period_date);

            CREATE OR REPLACE VIEW v_operator_period AS
            WITH in_flow AS (
              SELECT period_type, period_date, recipient_operator_id AS operator_id, SUM(value) AS port_in
              FROM mnp_flow_fact
              GROUP BY 1,2,3
            ),
            out_flow AS (
              SELECT period_type, period_date, donor_operator_id AS operator_id, SUM(value) AS port_out
              FROM mnp_flow_fact
              GROUP BY 1,2,3
            )
            SELECT
              COALESCE(i.period_type, o.period_type) AS period_type,
              COALESCE(i.period_date, o.period_date) AS period_date,
              COALESCE(i.operator_id, o.operator_id) AS operator_id,
              COALESCE(i.port_in, 0) AS port_in,
              COALESCE(o.port_out, 0) AS port_out,
              COALESCE(i.port_in, 0) - COALESCE(o.port_out, 0) AS net_flow
            FROM in_flow i
            FULL OUTER JOIN out_flow o
              ON i.period_type = o.period_type
             AND i.period_date = o.period_date
             AND i.operator_id = o.operator_id;
            """
        )

    def file_exists(self, checksum: str) -> bool:
        row = self.con.execute(
            "SELECT 1 FROM ingest_file WHERE checksum_sha256 = ? LIMIT 1", [checksum]
        ).fetchone()
        return row is not None

    def get_file_id_by_checksum(self, checksum: str) -> int | None:
        row = self.con.execute(
            "SELECT file_id FROM ingest_file WHERE checksum_sha256 = ? LIMIT 1", [checksum]
        ).fetchone()
        if not row:
            return None
        return int(row[0])

    def next_id(self, sequence_name: str) -> int:
        return self.con.execute(f"SELECT nextval('{sequence_name}')").fetchone()[0]

    def insert_ingest_file(self, filename: str, checksum: str, parser_version: str) -> int:
        file_id = self.next_id("seq_file_id")
        self.con.execute(
            """
            INSERT INTO ingest_file(file_id, filename, checksum_sha256, parser_version)
            VALUES (?, ?, ?, ?)
            """,
            [file_id, filename, checksum, parser_version],
        )
        return file_id

    def update_ingest_status(self, file_id: int, status: str, record_count: int) -> None:
        self.con.execute(
            "UPDATE ingest_file SET status = ?, record_count = ? WHERE file_id = ?",
            [status, record_count, file_id],
        )

    def get_or_create_operator(self, canonical_name: str, group_name: str | None, op_type: str | None) -> int:
        row = self.con.execute(
            "SELECT operator_id FROM operator_dim WHERE canonical_name = ?", [canonical_name]
        ).fetchone()
        if row:
            return int(row[0])

        operator_id = self.next_id("seq_operator_id")
        self.con.execute(
            """
            INSERT INTO operator_dim(operator_id, canonical_name, group_name, type)
            VALUES (?, ?, ?, ?)
            """,
            [operator_id, canonical_name, group_name, op_type],
        )
        return operator_id

    def delete_flows_for_file_id(self, file_id: int) -> None:
        self.con.execute("DELETE FROM mnp_flow_fact WHERE file_id = ?", [file_id])

    def delete_file_and_flows_by_checksum(self, checksum: str) -> None:
        file_id = self.get_file_id_by_checksum(checksum)
        if file_id is None:
            return
        self.delete_flows_for_file_id(file_id)
        self.con.execute("DELETE FROM ingest_file WHERE file_id = ?", [file_id])

    def insert_flow_dataframe(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0
        self.con.register("df_flow", df)
        self.con.execute(
            """
            INSERT INTO mnp_flow_fact(
                file_id,
                period_type,
                period_date,
                donor_operator_id,
                recipient_operator_id,
                value,
                sheet_name,
                quality_flag,
                donor_raw,
                recipient_raw
            )
            SELECT
                file_id,
                period_type,
                period_date,
                donor_operator_id,
                recipient_operator_id,
                value,
                sheet_name,
                quality_flag,
                donor_raw,
                recipient_raw
            FROM df_flow
            """
        )
        self.con.unregister("df_flow")
        return int(len(df))

    def list_operators(self) -> list[str]:
        rows = self.con.execute("SELECT canonical_name FROM operator_dim ORDER BY 1").fetchall()
        return [row[0] for row in rows]

    def query_df(self, query: str, params: Iterable | None = None) -> pd.DataFrame:
        if params is None:
            return self.con.execute(query).fetchdf()
        return self.con.execute(query, list(params)).fetchdf()
