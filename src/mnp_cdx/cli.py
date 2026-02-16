"""CLI entrypoint for mnpCDX."""

from __future__ import annotations

from pathlib import Path
import subprocess

import typer
import uvicorn

from mnp_cdx.analytics.kpi import AnalyticsService
from mnp_cdx.config import Settings
from mnp_cdx.db.repository import DBRepository
from mnp_cdx.ingest.operator_mapping import OperatorMapper
from mnp_cdx.ingest.parser import MNPParser
from mnp_cdx.ingest.service import IngestionService
from mnp_cdx.reporting import generate_markdown_report

app = typer.Typer(help="mnpCDX CLI")


def build_services() -> tuple[Settings, DBRepository, IngestionService, AnalyticsService]:
    settings = Settings.load()
    repo = DBRepository(settings.db_path)
    repo.init_schema()
    parser = MNPParser(include_self_flows=False)
    mapper = OperatorMapper(settings.mapping_path)
    ingest = IngestionService(repo=repo, parser=parser, mapper=mapper)
    analytics = AnalyticsService(repo)
    return settings, repo, ingest, analytics


@app.command("init-db")
def init_db() -> None:
    settings, repo, _, _ = build_services()
    typer.echo(f"Database initialized at: {settings.db_path}")
    repo.close()


@app.command("ingest")
def ingest(file_path: Path, force: bool = False) -> None:
    _, repo, ingest_service, _ = build_services()
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


@app.command("kpi")
def kpi(operator: str = "WINDTRE", period: str = "MONTHLY") -> None:
    _, repo, _, analytics = build_services()
    snapshot = analytics.kpi_snapshot(operator, period)
    typer.echo(snapshot)
    repo.close()


@app.command("quality")
def quality() -> None:
    _, repo, _, analytics = build_services()
    typer.echo(analytics.quality_report())
    repo.close()


@app.command("report")
def report(
    operator: str = "WINDTRE",
    period: str = "MONTHLY",
    output: Path = Path("reports") / "mnp_cdx_report.md",
) -> None:
    _, repo, _, analytics = build_services()
    report_path = generate_markdown_report(analytics, operator, period, output)
    typer.echo(f"Report generated: {report_path}")
    repo.close()


@app.command("api")
def run_api(host: str = "127.0.0.1", port: int = 8080) -> None:
    uvicorn.run("mnp_cdx.api.app:app", host=host, port=port, reload=False)


@app.command("dashboard")
def dashboard() -> None:
    module_file = Path(__file__).with_name("dashboard.py")
    subprocess.run(["streamlit", "run", str(module_file)], check=False)


if __name__ == "__main__":  # pragma: no cover
    app()
