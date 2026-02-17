# Release Notes mnpCDX

## v0.4.0 - Web Studio + Template Engine
- Nuova Web UI moderna su `GET /` per operare senza CLI.
- Motore template-aware per Excel eterogenei:
  - analisi struttura workbook/sheet/colonne;
  - firma strutturale e matching template;
  - versioning template evolutivo;
  - ingestion append-only in `excel_row_fact`.
- Trend explorer generico per metrica/template via API e UI.

## v0.1.0 - Foundation
- Setup package Python e CLI.
- Schema DuckDB iniziale con tabelle ingest + fact flows.
- Parser MNP monthly/daily con mapping operatori e dedup ingest.

## v0.2.0 - Analytics + API
- KPI engine con trend/top donors/top recipients.
- Quality report base.
- FastAPI endpoint per consultazione analytics.
- Report markdown automatico per operatore focus.

## v0.3.0-mvp - Business MVP
- Dashboard Streamlit operativa.
- AI summary opzionale (safe fallback se non configurato).
- Gate qualitativi minimi e documentazione team multi-agent.
