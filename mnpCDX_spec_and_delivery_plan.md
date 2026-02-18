# `mnpCDX` Spec Dettagliata, Piano di Sviluppo e Revisione Critica

> Nota: questo documento resta come baseline storica. La versione corrente del programma e in:
> `mnpCDX_detailed_spec.md` e `mnpCDX_development_plan_critical_review.md`.

## 1. Obiettivo di prodotto
Realizzare una piattaforma enterprise per ingestion, normalizzazione, analisi e reporting MNP, capace di produrre insight affidabili e tracciabili per decisioni business settimanali e mensili.

## 2. Scope MVP (Release target: `v0.3.0-mvp`)
- Ingestion file `.xlsx` MNP con dedup idempotente.
- Parsing `Monthly details` e `Daily details` con mapping operatori e controlli qualità.
- Persistenza su DuckDB con schema raw+gold e lineage minimo.
- API REST per KPI, trend, top donors/recipients, health.
- Report Markdown automatico per operatore focus.
- Dashboard operativa (streamlit) con filtro periodo e confronto competitivo base.
- AI summary opzionale con provider configurabile.

### Non-goal MVP
- Multi-tenant completo.
- Orchestrazione distribuita (Kubernetes-native).
- Real-time streaming (ingest batch weekly/daily sufficiente).

## 3. Requisiti funzionali (FR)

### FR-1 Ingestion & Idempotency
- Upload manuale o API endpoint.
- Calcolo SHA-256 file e blocco duplicati.
- Possibilità di reprocessing con versione parser esplicita.

### FR-2 Parsing robusto MNP
- Riconoscimento blocchi recipient/donor.
- Gestione merged cells e header periodi.
- Estrazione campi: file_id, period_type, period_date, donor, recipient, value, sheet_name, quality_flag.

### FR-3 Normalizzazione operatori
- Canonical mapping alias→operatore standard.
- Supporto a gruppi brand (es. WINDTRE + VERY MOBILE).
- Quarantena per operatori non mappati.

### FR-4 Analytics core
- Port-in, port-out, net flow per operatore e periodo.
- Top donors e top recipients.
- Trend e delta period-over-period.
- Indicatori base anomalia (volatilità / spike).

### FR-5 Reporting
- Generazione report Markdown con sezione executive.
- Tabelle KPI e competitor dynamics.
- Export JSON/CSV per BI.

### FR-6 AI executive summary (opzionale)
- Generazione testo solo da dataset calcolato.
- Prompt guardrail anti-hallucination.
- Fallback senza bloccare il flusso operativo.

## 4. Requisiti non funzionali (NFR)

### NFR-1 Affidabilità
- SLO ingestion success > 99% (su file validi).
- SLO API availability > 99.5% (in ambiente target).

### NFR-2 Performance
- Parsing file settimanale standard < 90s su host baseline.
- Query KPI principali < 2s percentile 95.

### NFR-3 Qualità dati
- Validazioni consistenza donor-sum vs recipient-total con tolleranza configurabile.
- Evidenza esplicita record imputati e scarti parser.

### NFR-4 Sicurezza
- Secret management fuori dal codice sorgente.
- Nessuna persistenza plaintext di API key in repository.

### NFR-5 Auditabilità
- Tracciabilità metrica → query → record sorgente.
- Logging strutturato per ingestion, parser warning, API.

## 5. Architettura logica

1. **Ingestion Service**
- Riceve file, valida checksum, salva metadata.

2. **Parser Engine**
- Estrae record monthly/daily, applica mapping operatori e quality flags.

3. **Data Layer**
- DuckDB con tabelle:
  - `ingest_file`
  - `operator_dim`
  - `mnp_flow_fact`
  - viste `v_operator_period`, `v_matrix`, `v_data_quality`

4. **Analytics Layer**
- KPI service e anomaly primitives.

5. **API Layer (FastAPI)**
- Endpoint read-only analytics + endpoint ingest trigger.

6. **Experience Layer**
- CLI + dashboard + report generator.

7. **AI Orchestrator**
- Adapter provider (OpenAI/Anthropic/Gemini/local) con policy prompt.

## 6. API contract (MVP)
- `GET /health`
- `POST /ingest` (file upload)
- `GET /operators`
- `GET /kpi/{operator}`
- `GET /trend/{operator}`
- `GET /top-donors/{operator}`
- `GET /top-recipients/{operator}`
- `GET /quality-report`

## 7. Strategia test
- Unit test parser helper (date parsing, value cleaning, alias mapping).
- Integration test ingest→db→kpi.
- Contract test API endpoint principali.
- Regression test su file reale campione versionato nel testdata index (non nel repo se sensibile).

## 8. Piano di delivery e versioning progressivo

### Release `v0.1.0` (Foundation)
- Struttura progetto, DB schema base, parser monthly/daily, CLI ingest.
- Output: dataset caricabile e query KPI elementari.

### Release `v0.2.0` (Analytics + API)
- KPI engine completo, API FastAPI, report markdown generator.
- Output: consumabilità via endpoint + report automatico.

### Release `v0.3.0-mvp` (Business MVP)
- Dashboard, AI summary opzionale, quality report, hardening sicurezza/logging.
- Output: piattaforma end-to-end utilizzabile in scenario business pilota.

## 9. Revisione critica del piano

### Criticità 1: rischio “parser correctness gap”
- Problema: senza ground truth certificata, KPI possono essere formalmente corretti ma semanticamente sbagliati.
- Impatto: **alto**.
- Mitigazione:
  - golden dataset minimo con expected counts per period/sheet.
  - regression gate obbligatorio in CI prima di ogni release.

### Criticità 2: DuckDB single-node limite crescita
- Problema: buono per MVP, potenziale collo di bottiglia su multi-utente.
- Impatto: medio.
- Mitigazione:
  - separare repository query da storage adapter;
  - pianificare path PostgreSQL/ClickHouse post-MVP.

### Criticità 3: AI overtrust
- Problema: summary AI potrebbe essere percepita come “verità” senza sufficiente evidenza.
- Impatto: alto (decision risk).
- Mitigazione:
  - report AI con sezione “Evidence used”; 
  - disabilitazione automatica se coverage dati insufficiente;
  - policy “AI as commentary, never as source of truth”.

### Criticità 4: gestione segreti locale
- Problema: storage locale cifrato non basta in ambienti enterprise.
- Impatto: medio-alto.
- Mitigazione:
  - integrazione Key Vault/Secrets Manager in target deployment.

### Criticità 5: assenza team process rigoroso
- Problema: delivery frammentata senza ownership esplicita.
- Impatto: medio.
- Mitigazione:
  - modello multi-agent con architect centrale + quality gates.

## 10. Piano post-review (versione corretta)
Il piano è **approvato con condizioni**:
1. introdurre subito test di regressione parser nel `v0.1.0` (non posticipare a `v0.2.0`);
2. bloccare merge senza quality report minimo;
3. rendere obbligatoria la sezione “Data Confidence” in ogni report;
4. mantenere roadmap a tre release ma con gate formali per passaggio fase.

Con queste correzioni, il percorso è considerato robusto per arrivare a un MVP business-usable.
