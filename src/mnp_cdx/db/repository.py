"""DuckDB repository and schema management."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Any
import json

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
            CREATE SEQUENCE IF NOT EXISTS seq_template_id START 1;
            CREATE SEQUENCE IF NOT EXISTS seq_ingest_event_id START 1;

            CREATE TABLE IF NOT EXISTS ingest_file (
                file_id BIGINT PRIMARY KEY,
                filename VARCHAR NOT NULL,
                checksum_sha256 VARCHAR(64) NOT NULL UNIQUE,
                parser_version VARCHAR(40) NOT NULL,
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

            CREATE TABLE IF NOT EXISTS excel_template (
                template_id BIGINT PRIMARY KEY,
                template_name VARCHAR NOT NULL,
                template_version INTEGER NOT NULL,
                workbook_signature VARCHAR(64) NOT NULL UNIQUE,
                schema_json TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(template_name, template_version)
            );

            CREATE TABLE IF NOT EXISTS excel_row_fact (
                file_id BIGINT NOT NULL,
                template_id BIGINT NOT NULL,
                sheet_name VARCHAR NOT NULL,
                row_number BIGINT NOT NULL,
                event_date DATE,
                metrics_json TEXT,
                dimensions_json TEXT,
                raw_json TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS excel_ingest_event (
                event_id BIGINT PRIMARY KEY,
                file_id BIGINT NOT NULL,
                template_id BIGINT NOT NULL,
                status VARCHAR(20) NOT NULL,
                row_count BIGINT NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_flow_period ON mnp_flow_fact(period_type, period_date);
            CREATE INDEX IF NOT EXISTS idx_flow_donor ON mnp_flow_fact(donor_operator_id, period_date);
            CREATE INDEX IF NOT EXISTS idx_flow_recipient ON mnp_flow_fact(recipient_operator_id, period_date);

            CREATE INDEX IF NOT EXISTS idx_excel_row_template_date ON excel_row_fact(template_id, event_date);
            CREATE INDEX IF NOT EXISTS idx_excel_row_sheet ON excel_row_fact(sheet_name);
            CREATE INDEX IF NOT EXISTS idx_excel_ingest_template ON excel_ingest_event(template_id, created_at);

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

    def next_id(self, sequence_name: str) -> int:
        return int(self.con.execute(f"SELECT nextval('{sequence_name}')").fetchone()[0])

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

    def delete_generic_rows_for_file_id(self, file_id: int) -> None:
        self.con.execute("DELETE FROM excel_row_fact WHERE file_id = ?", [file_id])
        self.con.execute("DELETE FROM excel_ingest_event WHERE file_id = ?", [file_id])

    def delete_file_everywhere_by_checksum(self, checksum: str) -> None:
        file_id = self.get_file_id_by_checksum(checksum)
        if file_id is None:
            return
        self.delete_flows_for_file_id(file_id)
        self.delete_generic_rows_for_file_id(file_id)
        self.con.execute("DELETE FROM ingest_file WHERE file_id = ?", [file_id])

    def delete_file_and_flows_by_checksum(self, checksum: str) -> None:
        # backward-compatible alias
        self.delete_file_everywhere_by_checksum(checksum)

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

    # ------------------------
    # Template Engine methods
    # ------------------------
    def get_template_by_signature(self, signature: str) -> dict[str, Any] | None:
        row = self.con.execute(
            """
            SELECT template_id, template_name, template_version, workbook_signature, schema_json, status, created_at
            FROM excel_template
            WHERE workbook_signature = ?
            LIMIT 1
            """,
            [signature],
        ).fetchone()
        if not row:
            return None
        return {
            "template_id": int(row[0]),
            "template_name": row[1],
            "template_version": int(row[2]),
            "workbook_signature": row[3],
            "schema": json.loads(row[4]),
            "status": row[5],
            "created_at": str(row[6]),
        }

    def get_template_by_id(self, template_id: int) -> dict[str, Any] | None:
        row = self.con.execute(
            """
            SELECT template_id, template_name, template_version, workbook_signature, schema_json, status, created_at
            FROM excel_template
            WHERE template_id = ?
            LIMIT 1
            """,
            [template_id],
        ).fetchone()
        if not row:
            return None
        return {
            "template_id": int(row[0]),
            "template_name": row[1],
            "template_version": int(row[2]),
            "workbook_signature": row[3],
            "schema": json.loads(row[4]),
            "status": row[5],
            "created_at": str(row[6]),
        }

    def list_templates(self) -> list[dict[str, Any]]:
        rows = self.con.execute(
            """
            SELECT template_id, template_name, template_version, workbook_signature, status, created_at
            FROM excel_template
            ORDER BY template_name, template_version DESC
            """
        ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            result.append(
                {
                    "template_id": int(row[0]),
                    "template_name": row[1],
                    "template_version": int(row[2]),
                    "workbook_signature": row[3],
                    "status": row[4],
                    "created_at": str(row[5]),
                }
            )
        return result

    def _next_template_version(self, template_name: str) -> int:
        row = self.con.execute(
            "SELECT COALESCE(MAX(template_version), 0) FROM excel_template WHERE template_name = ?",
            [template_name],
        ).fetchone()
        return int(row[0]) + 1

    def create_template(self, template_name: str, signature: str, schema: dict[str, Any]) -> dict[str, Any]:
        version = self._next_template_version(template_name)
        template_id = self.next_id("seq_template_id")
        self.con.execute(
            """
            INSERT INTO excel_template(template_id, template_name, template_version, workbook_signature, schema_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            [template_id, template_name, version, signature, json.dumps(schema, ensure_ascii=False)],
        )
        return self.get_template_by_id(template_id)  # type: ignore[return-value]

    def create_or_reuse_template(
        self,
        signature: str,
        schema: dict[str, Any],
        template_name: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        existing = self.get_template_by_signature(signature)
        if existing:
            return existing, False

        name = template_name.strip() if template_name else f"AUTO_{signature[:8]}"
        created = self.create_template(name, signature, schema)
        return created, True

    def insert_generic_row_dataframe(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0

        self.con.register("df_generic", df)
        self.con.execute(
            """
            INSERT INTO excel_row_fact(
                file_id,
                template_id,
                sheet_name,
                row_number,
                event_date,
                metrics_json,
                dimensions_json,
                raw_json
            )
            SELECT
                file_id,
                template_id,
                sheet_name,
                row_number,
                event_date,
                metrics_json,
                dimensions_json,
                raw_json
            FROM df_generic
            """
        )
        self.con.unregister("df_generic")
        return int(len(df))

    def insert_excel_ingest_event(
        self,
        file_id: int,
        template_id: int,
        status: str,
        row_count: int,
        notes: str | None = None,
    ) -> int:
        event_id = self.next_id("seq_ingest_event_id")
        self.con.execute(
            """
            INSERT INTO excel_ingest_event(event_id, file_id, template_id, status, row_count, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [event_id, file_id, template_id, status, row_count, notes],
        )
        return event_id

    def list_template_metrics(self, template_id: int) -> list[str]:
        rows = self.con.execute(
            "SELECT metrics_json FROM excel_row_fact WHERE template_id = ? LIMIT 1000",
            [template_id],
        ).fetchall()
        metrics: set[str] = set()
        for row in rows:
            raw = row[0]
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except Exception:
                continue
            for key in payload.keys():
                metrics.add(str(key))
        return sorted(metrics)

    def query_template_trend(
        self,
        template_id: int,
        metric_name: str,
        sheet_name: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        query = """
        SELECT
            event_date,
            SUM(COALESCE(CAST(json_extract_string(metrics_json, ?) AS DOUBLE), 0)) AS metric_value,
            COUNT(*) AS rows_included
        FROM excel_row_fact
        WHERE template_id = ?
          AND event_date IS NOT NULL
          AND (? IS NULL OR sheet_name = ?)
          AND (? IS NULL OR event_date >= ?)
          AND (? IS NULL OR event_date <= ?)
        GROUP BY event_date
        ORDER BY event_date
        """
        json_path = f"$.{metric_name}"
        return self.query_df(
            query,
            [
                json_path,
                template_id,
                sheet_name,
                sheet_name,
                start_date,
                start_date,
                end_date,
                end_date,
            ],
        )
