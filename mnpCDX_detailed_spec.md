# mnpCDX Next - Detailed Technical Spec

## 1. Product scope
Piattaforma enterprise single-tenant (fase MVP) per ingestion, analytics, simulation e AI explainable su dati business critici.

## 2. Functional Requirements (FR)

### FR-1 Data Ingestion Hub
- Upload/API/scheduler per dataset strutturati.
- checksum + idempotency + replay controllato.
- validazione schema e quarantena input malformati.

### FR-2 Canonical Data Model
- layer `raw`, `staging`, `gold`.
- dimensioni principali: operator, product, channel, time.
- fatti principali: flows, pricing scenarios, campaign signals.

### FR-3 Quality & Lineage
- regole qualità per completezza, coerenza, anomalie.
- lineage record-level: source_file -> transformed_row -> KPI/report.
- data confidence score per dataset e per insight.

### FR-4 KPI & Analytics Engine
- KPI standard (in/out/net, mix, deltas, volatility).
- anomaly detection basata su soglie + modelli statistici.
- query API-first con filtri multi-dimensione.

### FR-5 Scenario Simulation Engine
- simulator what-if su parametri economici/commerciali.
- calcolo impatto KPI, margine, rischio, payback.
- confronto baseline vs scenario con diff explainable.

### FR-6 AI Evidence Copilot
- prompt policy: solo dati interni certificati.
- output con evidenze, confidence e limiti espliciti.
- fallback deterministic report se AI non disponibile.

### FR-7 Operator UX
- dashboard executive (north-star KPI, risk map).
- dashboard operativa (drill-down, filtri, export).
- vista incident/quality per supporto operations.

### FR-8 API & Integration
- REST OpenAPI versionata.
- endpoint principali: health/readiness, ingest, kpi, trends, simulation, reports.
- webhook/event hooks per pipeline esterne.

### FR-9 Governance & Access
- autenticazione e ruoli (`viewer`, `analyst`, `admin`).
- audit log delle azioni critiche (ingest, approval, publish).
- workflow di approvazione report in ambienti regolati.

## 3. Non-Functional Requirements (NFR)

### NFR-1 Reliability
- API availability target: >= 99.5% (MVP pilot).
- ingest success su input validi: >= 99%.

### NFR-2 Performance
- ingest file standard: p95 < 90s.
- query KPI principali: p95 < 2s.
- dashboard initial load: p95 < 3s su LAN.

### NFR-3 Security
- secrets solo da env/vault, mai in repository.
- encryption at rest per storage sensibile.
- hardening dependency e vulnerability scan periodico.

### NFR-4 Observability
- logging strutturato con request_id/correlation_id.
- metrics + tracing endpoint critici.
- alerting su error budget e quality regressions.

### NFR-5 Maintainability
- coverage minima target: 70% core logic.
- architettura modulare con boundary chiari.
- changelog + ADR obbligatori per release major/minor.

## 4. Architecture (MVP)
- `Ingestion Service`: parsing, validation, dedup.
- `Data Platform`: DuckDB (MVP) con adapter astratto verso PostgreSQL/ClickHouse post-MVP.
- `Analytics Service`: KPI/trend/anomaly query.
- `Simulation Service`: scenario engine economico/operativo.
- `AI Service`: summarization evidence-first.
- `API Layer`: FastAPI contract-first.
- `Web App`: dashboard operativa.

## 5. Data contracts essenziali

### `ingest_file`
- id, filename, checksum, source, parser_version, ingested_at, status.

### `fact_flow`
- period_date, donor_operator_id, recipient_operator_id, value, quality_flag, lineage_ref.

### `fact_scenario`
- scenario_id, dimension_keys, assumptions_hash, output_kpi_json, created_by, approved_by.

### `quality_event`
- dataset_id, rule_id, severity, message, detected_at, resolved_at.

## 6. API surface (MVP target)
- `GET /health`
- `GET /readiness`
- `POST /ingest`
- `GET /operators`
- `GET /kpi/{operator}`
- `GET /trend/{operator}`
- `POST /simulation/run`
- `GET /simulation/{scenario_id}`
- `GET /quality-report`
- `POST /report/generate`

## 7. Test strategy
- unit tests: parser, mapping, KPI, simulation math.
- integration tests: ingest->storage->analytics->report.
- contract tests: OpenAPI compatibility per versione.
- e2e tests: dataset reale anonimizzato + scenario business.
- non-functional tests: load baseline + failure injection su ingest/API.

## 8. Acceptance criteria MVP
- 3 run consecutivi senza regressioni su dataset reali.
- report executive e operativo approvati da stakeholder business.
- tempi e SLO minimi rispettati in ambiente pilota.
- security baseline e audit trail verificati.
