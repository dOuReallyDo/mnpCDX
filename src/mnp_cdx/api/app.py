"""FastAPI application for mnpCDX."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile

from mnp_cdx.analytics.kpi import AnalyticsService
from mnp_cdx.api.schemas import HealthResponse, IngestResponse
from mnp_cdx.config import Settings
from mnp_cdx.db.repository import DBRepository
from mnp_cdx.ingest.operator_mapping import OperatorMapper
from mnp_cdx.ingest.parser import MNPParser
from mnp_cdx.ingest.service import IngestionService


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or Settings.load()

    repo = DBRepository(cfg.db_path)
    repo.init_schema()
    parser = MNPParser(include_self_flows=False)
    mapper = OperatorMapper(cfg.mapping_path)
    ingest_service = IngestionService(repo=repo, parser=parser, mapper=mapper)
    analytics = AnalyticsService(repo)

    app = FastAPI(title="mnpCDX API", version="0.3.0")

    @app.on_event("shutdown")
    def _shutdown() -> None:  # pragma: no cover
        repo.close()

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/ingest", response_model=IngestResponse)
    async def ingest(file: UploadFile = File(...), force: bool = False) -> IngestResponse:
        if not file.filename:
            raise HTTPException(status_code=400, detail="filename missing")

        suffix = Path(file.filename).suffix or ".xlsx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = Path(tmp.name)

        try:
            result = ingest_service.ingest_file(tmp_path, force=force)
            return IngestResponse(**result.__dict__)
        finally:
            tmp_path.unlink(missing_ok=True)

    @app.get("/operators")
    def operators() -> list[str]:
        return analytics.operators()

    @app.get("/kpi/{operator}")
    def kpi(operator: str, period_type: str = "MONTHLY") -> dict:
        return analytics.kpi_snapshot(operator, period_type)

    @app.get("/trend/{operator}")
    def trend(
        operator: str,
        period_type: str = "MONTHLY",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        df = analytics.trend(operator, period_type, start_date=start_date, end_date=end_date)
        return df.to_dict(orient="records")

    @app.get("/top-donors/{operator}")
    def top_donors(
        operator: str,
        period_type: str = "MONTHLY",
        limit: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        df = analytics.top_donors(
            operator,
            period_type,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )
        return df.to_dict(orient="records")

    @app.get("/top-recipients/{operator}")
    def top_recipients(
        operator: str,
        period_type: str = "MONTHLY",
        limit: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        df = analytics.top_recipients(
            operator,
            period_type,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )
        return df.to_dict(orient="records")

    @app.get("/quality-report")
    def quality_report() -> dict:
        return analytics.quality_report()

    return app


app = create_app()
