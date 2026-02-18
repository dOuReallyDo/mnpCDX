# Release Notes mnpCDX

## v0.5.0 - Portfolio Convergence Baseline (2026-02-18)
- Aggiornata analisi critica portfolio in `project_overview.md` su sottocartelle attive.
- Definito super-progetto `mnpCDX Next` in `mnpCDX_nextgen_project.md`.
- Aggiunta spec tecnica dettagliata in `mnpCDX_detailed_spec.md`.
- Aggiunto piano sviluppo + revisione critica in `mnpCDX_development_plan_critical_review.md`.
- Aggiornato blueprint team multi-agent e backlog milestone fino a `v1.0.0-mvp`.
- Introdotto manifesto team machine-readable in `docs/agent_team_manifest.yaml`.
- Potenziato modulo `main_architect` per sintesi/validazione backlog+team.

## v0.4.2 - API Error Hardening
- Hardening endpoint `/template/analyze` e `/template/ingest` con gestione eccezioni inattese e reference id.
- Migliorato parser errori nella Web UI (`static/app.js`) per messaggi utente leggibili.
- Aggiunti test API su percorsi 500 strutturati in `tests/test_api_error_handling.py`.

## v0.4.1 - Portfolio Governance Token-Minimal
- Definito modello operativo token-minimal in `docs/token_minimal_operating_model.md`.
- Definito piano di distribuzione team e sequenza portfolio in `docs/portfolio_team_distribution_plan.md`.
- Formalizzato ruolo obbligatorio `Context Steward` per coerenza e memoria critica.

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
