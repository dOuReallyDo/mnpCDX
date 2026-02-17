from datetime import date
from pathlib import Path

import openpyxl

from mnp_cdx.db.repository import DBRepository
from mnp_cdx.generic.template_engine import GenericTemplateEngine


def _build_sample_workbook(path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales"
    ws.append(["Data", "Region", "Revenue", "Cost"])
    ws.append([date(2025, 1, 1), "North", 1000, 600])
    ws.append([date(2025, 1, 2), "North", 1100, 650])
    ws.append([date(2025, 1, 3), "South", 900, 550])

    ws2 = wb.create_sheet("Inventory")
    ws2.append(["Date", "SKU", "Stock"])
    ws2.append([date(2025, 1, 1), "A1", 50])
    ws2.append([date(2025, 1, 2), "A1", 48])

    wb.save(path)


def test_analyze_and_ingest_generic_excel(tmp_path) -> None:
    db_path = tmp_path / "generic.duckdb"
    file_path = tmp_path / "sample_20250103.xlsx"
    _build_sample_workbook(file_path)

    repo = DBRepository(db_path)
    repo.init_schema()
    engine = GenericTemplateEngine(repo)

    analyzed = engine.analyze(file_path)
    assert analyzed.workbook_signature
    assert analyzed.schema["sheets"]

    ingest_result = engine.ingest(file_path, template_name="SALES_TEMPLATE", force=False)
    assert ingest_result.inserted_rows > 0
    assert ingest_result.template_name == "SALES_TEMPLATE"

    templates = repo.list_templates()
    assert len(templates) == 1

    metrics = repo.list_template_metrics(ingest_result.template_id)
    assert "Revenue" in metrics or "Stock" in metrics

    trend_df = repo.query_template_trend(ingest_result.template_id, metric_name="Revenue")
    assert not trend_df.empty

    repo.close()
