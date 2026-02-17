"""FastAPI application for mnpCDX."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from mnp_cdx.analytics.kpi import AnalyticsService
from mnp_cdx.api.schemas import HealthResponse, IngestResponse
from mnp_cdx.config import Settings
from mnp_cdx.db.repository import DBRepository
from mnp_cdx.generic.template_engine import GenericTemplateEngine
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
    generic = GenericTemplateEngine(repo)

    app = FastAPI(title="mnpCDX API", version="0.4.0")

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.on_event("shutdown")
    def _shutdown() -> None:  # pragma: no cover
        repo.close()

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        index_path = static_dir / "index.html"
        if not index_path.exists():
            return HTMLResponse("mnpCDX UI non trovata", status_code=500)
        return HTMLResponse(index_path.read_text(encoding="utf-8"))

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    # ---------------------------
    # Legacy MNP-specific endpoints
    # ---------------------------
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

    # ---------------------------
    # Generic template endpoints
    # ---------------------------
    @app.post("/template/analyze")
    async def template_analyze(file: UploadFile = File(...)) -> dict:
        if not file.filename:
            raise HTTPException(status_code=400, detail="filename missing")

        suffix = Path(file.filename).suffix or ".xlsx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = Path(tmp.name)

        try:
            analyzed = generic.analyze(tmp_path)
            return {
                "filename": file.filename,
                "workbook_signature": analyzed.workbook_signature,
                "matched_template": analyzed.matched_template,
                "schema": analyzed.schema,
            }
        finally:
            tmp_path.unlink(missing_ok=True)

    @app.post("/template/ingest")
    async def template_ingest(
        file: UploadFile = File(...),
        template_name: str | None = Form(default=None),
        template_id: int | None = Form(default=None),
        force: bool = Form(default=False),
    ) -> dict:
        if not file.filename:
            raise HTTPException(status_code=400, detail="filename missing")

        suffix = Path(file.filename).suffix or ".xlsx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = Path(tmp.name)

        try:
            result = generic.ingest(
                tmp_path,
                template_id=template_id,
                template_name=template_name,
                force=force,
            )
            return result.__dict__
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            tmp_path.unlink(missing_ok=True)

    @app.get("/templates")
    def templates() -> list[dict]:
        return repo.list_templates()

    @app.get("/template/{template_id}")
    def template_detail(template_id: int) -> dict:
        tpl = repo.get_template_by_id(template_id)
        if tpl is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return tpl

    @app.get("/template/{template_id}/metrics")
    def template_metrics(template_id: int) -> dict:
        tpl = repo.get_template_by_id(template_id)
        if tpl is None:
            raise HTTPException(status_code=404, detail="Template not found")
        metrics = repo.list_template_metrics(template_id)
        return {"template_id": template_id, "metrics": metrics}

    @app.get("/template/{template_id}/trend")
    def template_trend(
        template_id: int,
        metric: str = Query(..., min_length=1),
        sheet_name: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        tpl = repo.get_template_by_id(template_id)
        if tpl is None:
            raise HTTPException(status_code=404, detail="Template not found")

        df = repo.query_template_trend(
            template_id=template_id,
            metric_name=metric,
            sheet_name=sheet_name,
            start_date=start_date,
            end_date=end_date,
        )
        return df.to_dict(orient="records")

    return app


app = create_app()
