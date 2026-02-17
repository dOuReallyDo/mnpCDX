"""CLI entrypoint for mnpCDX."""

from __future__ import annotations

from pathlib import Path
import json
import subprocess

import typer
import uvicorn

from mnp_cdx.analytics.kpi import AnalyticsService
from mnp_cdx.config import Settings
from mnp_cdx.db.repository import DBRepository
from mnp_cdx.generic.template_engine import GenericTemplateEngine
from mnp_cdx.ingest.operator_mapping import OperatorMapper
from mnp_cdx.ingest.parser import MNPParser
from mnp_cdx.ingest.service import IngestionService
from mnp_cdx.reporting import generate_markdown_report

app = typer.Typer(help="mnpCDX CLI")


def build_services() -> tuple[Settings, DBRepository, IngestionService, AnalyticsService, GenericTemplateEngine]:
    settings = Settings.load()
    repo = DBRepository(settings.db_path)
    repo.init_schema()
    parser = MNPParser(include_self_flows=False)
    mapper = OperatorMapper(settings.mapping_path)
    ingest = IngestionService(repo=repo, parser=parser, mapper=mapper)
    analytics = AnalyticsService(repo)
    generic = GenericTemplateEngine(repo)
    return settings, repo, ingest, analytics, generic


@app.command("init-db")
def init_db() -> None:
    settings, repo, _, _, _ = build_services()
    typer.echo(f"Database initialized at: {settings.db_path}")
    repo.close()


@app.command("ingest")
def ingest(file_path: Path, force: bool = False) -> None:
    _, repo, ingest_service, _, _ = build_services()
    if not file_path.exists():
        raise typer.BadParameter(f"File not found: {file_path}")

    result = ingest_service.ingest_file(file_path, force=force)
    typer.echo(f"File: {result.filename}")
    typer.echo(f"Checksum: {result.checksum[:16]}...")
    typer.echo(f"Monthly parsed: {result.monthly_records}")
    typer.echo(f"Daily parsed: {result.daily_records}")
    typer.echo(f"Inserted records: {result.inserted_records}")
    typer.echo(f"Duplicate skipped: {result.skipped_duplicate}")
    if result.warnings:
        typer.echo("Warnings:")
        for warning in result.warnings:
            typer.echo(f"- {warning}")

    repo.close()


@app.command("generic-analyze")
def generic_analyze(file_path: Path) -> None:
    _, repo, _, _, generic = build_services()
    if not file_path.exists():
        raise typer.BadParameter(f"File not found: {file_path}")

    analyzed = generic.analyze(file_path)
    payload = {
        "workbook_signature": analyzed.workbook_signature,
        "matched_template": analyzed.matched_template,
        "schema": analyzed.schema,
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    repo.close()


@app.command("generic-ingest")
def generic_ingest(
    file_path: Path,
    template_name: str | None = None,
    template_id: int | None = None,
    force: bool = False,
) -> None:
    _, repo, _, _, generic = build_services()
    if not file_path.exists():
        raise typer.BadParameter(f"File not found: {file_path}")

    result = generic.ingest(
        file_path,
        template_id=template_id,
        template_name=template_name,
        force=force,
    )
    typer.echo(json.dumps(result.__dict__, ensure_ascii=False, indent=2, default=str))
    repo.close()


@app.command("templates")
def templates() -> None:
    _, repo, _, _, _ = build_services()
    typer.echo(json.dumps(repo.list_templates(), ensure_ascii=False, indent=2))
    repo.close()


@app.command("generic-trend")
def generic_trend(
    template_id: int,
    metric: str,
    sheet_name: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> None:
    _, repo, _, _, _ = build_services()
    df = repo.query_template_trend(
        template_id=template_id,
        metric_name=metric,
        sheet_name=sheet_name,
        start_date=start_date,
        end_date=end_date,
    )
    typer.echo(df.to_string(index=False))
    repo.close()


@app.command("kpi")
def kpi(operator: str = "WINDTRE", period: str = "MONTHLY") -> None:
    _, repo, _, analytics, _ = build_services()
    snapshot = analytics.kpi_snapshot(operator, period)
    typer.echo(snapshot)
    repo.close()


@app.command("quality")
def quality() -> None:
    _, repo, _, analytics, _ = build_services()
    typer.echo(analytics.quality_report())
    repo.close()


@app.command("report")
def report(
    operator: str = "WINDTRE",
    period: str = "MONTHLY",
    output: Path = Path("reports") / "mnp_cdx_report.md",
) -> None:
    _, repo, _, analytics, _ = build_services()
    report_path = generate_markdown_report(analytics, operator, period, output)
    typer.echo(f"Report generated: {report_path}")
    repo.close()


@app.command("api")
def run_api(host: str = "127.0.0.1", port: int = 8080) -> None:
    uvicorn.run("mnp_cdx.api.app:app", host=host, port=port, reload=False)


@app.command("web")
def run_web(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Alias esplicito per avviare API + Web UI."""
    uvicorn.run("mnp_cdx.api.app:app", host=host, port=port, reload=False)


@app.command("dashboard")
def dashboard() -> None:
    module_file = Path(__file__).with_name("dashboard.py")
    subprocess.run(["streamlit", "run", str(module_file)], check=False)


if __name__ == "__main__":  # pragma: no cover
    app()
