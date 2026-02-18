# mnpCDX

mnpCDX e una piattaforma production-oriented con interfaccia web moderna per ingestion e analisi trend di file Excel anche eterogenei.

## Stato
- Versione target corrente: `v0.5.0`
- Scope: decision intelligence platform con ingestion affidabile, analytics, simulation e governance fino a `v1.0.0-mvp`.

## Componenti principali
- `src/mnp_cdx/generic`: motore template-aware per Excel eterogenei (analisi struttura, versioning template, ingest append-only).
- `src/mnp_cdx/ingest`: parser e servizio ingest MNP specifico.
- `src/mnp_cdx/db`: schema e repository DuckDB.
- `src/mnp_cdx/analytics`: KPI, trend e quality checks.
- `src/mnp_cdx/api`: API FastAPI + Web UI SPA (`/`).
- `src/mnp_cdx/cli.py`: comandi operativi.
- `src/mnp_cdx/dashboard.py`: dashboard Streamlit (opzionale).

## Quick start
```bash
cd mnpCDX
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
# per tool dev su zsh: pip install -e '.[dev]'

# Inizializza DB
mnp-cdx init-db

# Avvia Web UI moderna (API + frontend)
mnp-cdx web --host 127.0.0.1 --port 8080
# poi apri http://127.0.0.1:8080

# Analisi struttura template da CLI
mnp-cdx generic-analyze "/path/to/any_workbook.xlsx"

# Ingestion template-aware (auto template o template_name)
mnp-cdx generic-ingest "/path/to/any_workbook.xlsx" --template-name MY_TEMPLATE

# Ingest file xlsx
mnp-cdx ingest "/path/to/MNP MATRIX 20251127.xlsx"

# KPI rapido
mnp-cdx kpi --operator WINDTRE --period DAILY

# Avvia API (solo backend)
mnp-cdx api --host 0.0.0.0 --port 8080

# Avvia dashboard
mnp-cdx dashboard
```

## API endpoint (MVP)
- `GET /health`
- `GET /` (Web UI moderna)
- `POST /ingest`
- `GET /operators`
- `GET /kpi/{operator}`
- `GET /trend/{operator}`
- `GET /top-donors/{operator}`
- `GET /top-recipients/{operator}`
- `GET /quality-report`
- `POST /template/analyze`
- `POST /template/ingest`
- `GET /templates`
- `GET /template/{template_id}`
- `GET /template/{template_id}/metrics`
- `GET /template/{template_id}/trend`

## Versioning progressivo
- `v0.1.0`: foundation ingest + schema + parser.
- `v0.2.0`: analytics + API + reporting.
- `v0.3.0-mvp`: dashboard + AI summary opzionale + quality gate report.
- `v0.4.x`: web studio template-aware + hardening error handling API/UI.
- `v0.5.0`: portfolio convergence baseline e piano multi-agent fino a MVP.
- `v0.6.0`: data reliability core.
- `v0.7.0`: analytics + simulation core.
- `v0.8.0`: operations + security hardening.
- `v0.9.0-rc1`: pilot readiness candidate.
- `v1.0.0-mvp`: first business MVP.

Dettagli in `docs/release_notes.md`.

## Documenti chiave programma Next
- `project_overview.md`
- `mnpCDX_nextgen_project.md`
- `mnpCDX_detailed_spec.md`
- `mnpCDX_development_plan_critical_review.md`
- `agents_team_blueprint.md`
- `docs/agent_backlog.yaml`
- `docs/agent_team_manifest.yaml`

## Governance operativa portfolio
- Modello token/context minimal: `docs/token_minimal_operating_model.md`
- Distribuzione team e sequenza progetto-per-progetto: `docs/portfolio_team_distribution_plan.md`
