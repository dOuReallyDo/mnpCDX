# Team Multi-Agent `mnpCDX` (coordinato da Main Architect)

## Governance
- **Main Architect (Lead Agent)**: ownership di architettura, priorità, decision log, gate di rilascio.
- Tutti gli agenti lavorano su backlog condiviso con Definition of Done unificata.
- Nessuna feature può entrare in release senza validazione QA + Security check minimo.

## Team completo

| Agente | Responsabilità primaria | Deliverable |
|---|---|---|
| Main Architect | Disegno target architecture, slicing release, risk governance | ADR, release gates, roadmap aggiornata |
| Ingestion Engineer | Pipeline upload, dedup, metadata, replay | modulo ingestion + test integrazione |
| Parsing Specialist | Robustezza estrazione monthly/daily, merged/header logic | parser engine + regression fixtures |
| Data Model Engineer | Schema DB, viste analytics, lineage | migration/schema + query contracts |
| Analytics Engineer | KPI, anomaly signals, quality score | analytics service + metric tests |
| API Engineer | FastAPI, DTO, error handling, contract stability | endpoint REST + OpenAPI |
| Dashboard Engineer | UI Streamlit/BI-ready views | dashboard MVP + usability checklist |
| AI Orchestrator Engineer | provider adapters, prompt policy, evidence-first summaries | ai service + guardrail tests |
| QA Lead | test strategy, regression gates, release readiness | test plan + test reports |
| Security Engineer | secrets handling, data protection, threat review | security baseline + remediation log |
| DevOps/SRE Engineer | packaging, CI/CD, observability, release automation | pipeline CI + runbook |

## Modello di coordinamento

### Cadence
- Daily sync asincrono (stato, blocker, rischi).
- Release review a fine milestone (`v0.1.0`, `v0.2.0`, `v0.3.0-mvp`).

### Artefatti obbligatori per ogni task
- scope tecnico;
- test evidence;
- risk note;
- rollback note.

### Quality gates
1. `Parser Gate`: regression suite pass + no silent parsing errors.
2. `Data Gate`: KPI consistency checks pass.
3. `API Gate`: contract tests pass.
4. `Security Gate`: nessun secret in repo + baseline scan pass.
5. `Release Gate`: changelog/version tag + smoke test report.

## Sequenza operativa fino al primo MVP
1. **Foundation Sprint** (`v0.1.0`)
- Ingestion Engineer + Parsing Specialist + Data Model Engineer.
2. **Analytics/API Sprint** (`v0.2.0`)
- Analytics Engineer + API Engineer + QA Lead.
3. **Business MVP Sprint** (`v0.3.0-mvp`)
- Dashboard Engineer + AI Engineer + Security + DevOps + QA.

## Decision rule del Main Architect
- Favorire affidabilità e tracciabilità su velocità quando in conflitto.
- Consentire scope cut solo se non riduce correctness dei KPI.
- Bloccare release se quality gate incompleti.
