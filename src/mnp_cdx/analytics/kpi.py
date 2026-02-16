"""Analytics and KPI services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from mnp_cdx.db.repository import DBRepository


@dataclass
class KPIRecord:
    period_date: date
    port_in: float
    port_out: float
    net_flow: float


class AnalyticsService:
    def __init__(self, repo: DBRepository) -> None:
        self.repo = repo

    def operators(self) -> list[str]:
        return self.repo.list_operators()

    def trend(
        self,
        operator: str,
        period_type: str = "MONTHLY",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        query = """
        WITH target AS (
            SELECT operator_id FROM operator_dim WHERE canonical_name = ?
        ),
        in_flow AS (
            SELECT f.period_date, SUM(f.value) AS port_in
            FROM mnp_flow_fact f
            JOIN target t ON t.operator_id = f.recipient_operator_id
            WHERE f.period_type = ?
              AND (? IS NULL OR f.period_date >= ?)
              AND (? IS NULL OR f.period_date <= ?)
            GROUP BY f.period_date
        ),
        out_flow AS (
            SELECT f.period_date, SUM(f.value) AS port_out
            FROM mnp_flow_fact f
            JOIN target t ON t.operator_id = f.donor_operator_id
            WHERE f.period_type = ?
              AND (? IS NULL OR f.period_date >= ?)
              AND (? IS NULL OR f.period_date <= ?)
            GROUP BY f.period_date
        )
        SELECT
          COALESCE(i.period_date, o.period_date) AS period_date,
          COALESCE(i.port_in, 0) AS port_in,
          COALESCE(o.port_out, 0) AS port_out,
          COALESCE(i.port_in, 0) - COALESCE(o.port_out, 0) AS net_flow
        FROM in_flow i
        FULL OUTER JOIN out_flow o ON i.period_date = o.period_date
        ORDER BY period_date
        """
        return self.repo.query_df(
            query,
            [
                operator,
                period_type,
                start_date,
                start_date,
                end_date,
                end_date,
                period_type,
                start_date,
                start_date,
                end_date,
                end_date,
            ],
        )

    def kpi_snapshot(
        self,
        operator: str,
        period_type: str = "MONTHLY",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        df = self.trend(operator, period_type, start_date=start_date, end_date=end_date)
        if df.empty:
            return {
                "operator": operator,
                "period_type": period_type,
                "total_port_in": 0.0,
                "total_port_out": 0.0,
                "net_balance": 0.0,
                "latest_period": None,
                "latest_net": 0.0,
            }

        total_in = float(df["port_in"].sum())
        total_out = float(df["port_out"].sum())
        latest = df.iloc[-1]
        return {
            "operator": operator,
            "period_type": period_type,
            "total_port_in": total_in,
            "total_port_out": total_out,
            "net_balance": total_in - total_out,
            "latest_period": str(latest["period_date"]),
            "latest_net": float(latest["net_flow"]),
        }

    def top_donors(
        self,
        operator: str,
        period_type: str = "MONTHLY",
        limit: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        query = """
        WITH target AS (
          SELECT operator_id FROM operator_dim WHERE canonical_name = ?
        )
        SELECT d.canonical_name AS donor_operator, SUM(f.value) AS total_in
        FROM mnp_flow_fact f
        JOIN target t ON t.operator_id = f.recipient_operator_id
        JOIN operator_dim d ON d.operator_id = f.donor_operator_id
        WHERE f.period_type = ?
          AND (? IS NULL OR f.period_date >= ?)
          AND (? IS NULL OR f.period_date <= ?)
        GROUP BY d.canonical_name
        ORDER BY total_in DESC
        LIMIT ?
        """
        return self.repo.query_df(
            query,
            [operator, period_type, start_date, start_date, end_date, end_date, limit],
        )

    def top_recipients(
        self,
        operator: str,
        period_type: str = "MONTHLY",
        limit: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        query = """
        WITH target AS (
          SELECT operator_id FROM operator_dim WHERE canonical_name = ?
        )
        SELECT r.canonical_name AS recipient_operator, SUM(f.value) AS total_out
        FROM mnp_flow_fact f
        JOIN target t ON t.operator_id = f.donor_operator_id
        JOIN operator_dim r ON r.operator_id = f.recipient_operator_id
        WHERE f.period_type = ?
          AND (? IS NULL OR f.period_date >= ?)
          AND (? IS NULL OR f.period_date <= ?)
        GROUP BY r.canonical_name
        ORDER BY total_out DESC
        LIMIT ?
        """
        return self.repo.query_df(
            query,
            [operator, period_type, start_date, start_date, end_date, end_date, limit],
        )

    def quality_report(self) -> dict:
        counts = self.repo.query_df(
            """
            SELECT
                COUNT(*) AS total_rows,
                SUM(CASE WHEN quality_flag = 'IMPUTED' THEN 1 ELSE 0 END) AS imputed_rows,
                SUM(CASE WHEN value = 0 THEN 1 ELSE 0 END) AS zero_rows
            FROM mnp_flow_fact
            """
        )
        periods = self.repo.query_df(
            """
            SELECT period_type, MIN(period_date) AS min_date, MAX(period_date) AS max_date,
                   COUNT(DISTINCT period_date) AS distinct_periods
            FROM mnp_flow_fact
            GROUP BY period_type
            ORDER BY period_type
            """
        )
        row = counts.iloc[0] if not counts.empty else None
        if row is None:
            return {"total_rows": 0, "imputed_rows": 0, "zero_rows": 0, "coverage": []}

        coverage = periods.to_dict(orient="records")
        for c in coverage:
            c["min_date"] = str(c["min_date"])
            c["max_date"] = str(c["max_date"])

        total_rows_raw = row["total_rows"]
        imputed_rows_raw = row["imputed_rows"]
        zero_rows_raw = row["zero_rows"]

        total_rows = int(total_rows_raw) if pd.notna(total_rows_raw) else 0
        imputed_rows = int(imputed_rows_raw) if pd.notna(imputed_rows_raw) else 0
        zero_rows = int(zero_rows_raw) if pd.notna(zero_rows_raw) else 0

        return {
            "total_rows": total_rows,
            "imputed_rows": imputed_rows,
            "zero_rows": zero_rows,
            "imputed_ratio": (imputed_rows / total_rows) if total_rows else 0,
            "zero_ratio": (zero_rows / total_rows) if total_rows else 0,
            "coverage": coverage,
        }
