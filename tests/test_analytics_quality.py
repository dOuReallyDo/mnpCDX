from datetime import date

import pandas as pd

from mnp_cdx.analytics.kpi import AnalyticsService
from mnp_cdx.db.repository import DBRepository


def test_quality_report_and_snapshot(tmp_path) -> None:
    db_path = tmp_path / "test.duckdb"
    repo = DBRepository(db_path)
    repo.init_schema()

    donor_id = repo.get_or_create_operator("TIM", "TIM_GROUP", "MNO")
    recipient_id = repo.get_or_create_operator("WINDTRE", "WINDTRE_GROUP", "MNO")

    file_id = repo.insert_ingest_file("sample.xlsx", "abc123", "test")

    df = pd.DataFrame(
        [
            {
                "file_id": file_id,
                "period_type": "MONTHLY",
                "period_date": date(2025, 1, 1),
                "donor_operator_id": donor_id,
                "recipient_operator_id": recipient_id,
                "value": 100.0,
                "sheet_name": "Monthly details",
                "quality_flag": "OK",
                "donor_raw": "TIM",
                "recipient_raw": "WINDTRE",
            },
            {
                "file_id": file_id,
                "period_type": "MONTHLY",
                "period_date": date(2025, 2, 1),
                "donor_operator_id": donor_id,
                "recipient_operator_id": recipient_id,
                "value": 0.0,
                "sheet_name": "Monthly details",
                "quality_flag": "IMPUTED",
                "donor_raw": "TIM",
                "recipient_raw": "WINDTRE",
            },
        ]
    )

    inserted = repo.insert_flow_dataframe(df)
    repo.update_ingest_status(file_id, "OK", inserted)

    analytics = AnalyticsService(repo)
    snapshot = analytics.kpi_snapshot("WINDTRE", "MONTHLY")
    quality = analytics.quality_report()

    assert snapshot["total_port_in"] == 100.0
    assert quality["total_rows"] == 2
    assert quality["imputed_rows"] == 1

    repo.close()
