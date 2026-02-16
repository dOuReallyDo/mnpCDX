# mnpCDX

mnpCDX e una piattaforma MNP production-oriented che unifica ingestion, parsing, analytics, reporting, API e dashboard per scenari business reali.

## Stato
- Versione target corrente: `v0.3.0-mvp`
- Scope: weekly batch ingestion, KPI operator-focused, report markdown, API REST e dashboard operativa.

## Componenti principali
- `src/mnp_cdx/ingest`: parser e servizio ingest idempotente.
- `src/mnp_cdx/db`: schema e repository DuckDB.
- `src/mnp_cdx/analytics`: KPI, trend e quality checks.
- `src/mnp_cdx/api`: API FastAPI.
- `src/mnp_cdx/cli.py`: comandi operativi.
- `src/mnp_cdx/dashboard.py`: dashboard Streamlit.

## Quick start
```bash
cd mnpCDX
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Inizializza DB
mnp-cdx init-db

# Ingest file xlsx
mnp-cdx ingest "/path/to/MNP MATRIX 20251127.xlsx"

# KPI rapido
mnp-cdx kpi --operator WINDTRE --period DAILY

# Avvia API
mnp-cdx api --host 0.0.0.0 --port 8080

# Avvia dashboard
mnp-cdx dashboard
```

## API endpoint (MVP)
- `GET /health`
- `POST /ingest`
- `GET /operators`
- `GET /kpi/{operator}`
- `GET /trend/{operator}`
- `GET /top-donors/{operator}`
- `GET /top-recipients/{operator}`
- `GET /quality-report`

## Versioning progressivo
- `v0.1.0`: foundation ingest + schema + parser.
- `v0.2.0`: analytics + API + reporting.
- `v0.3.0-mvp`: dashboard + AI summary opzionale + quality gate report.

Dettagli in `docs/release_notes.md`.
