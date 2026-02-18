# Team Multi-Agent mnpCDX Next (coordinato da Main Architect)

## Governance principale
- **Main Architect (Program Lead)**
  - owner di architettura, scope, decisioni tecniche, release gates.
  - unica autorita per stop/go milestone.

## Team completo di agenti

| Agente | Missione | KPI di responsabilita |
|---|---|---|
| Main Architect | Orchestrazione programma e decision log | milestone on-time, risk burn-down |
| Product Strategy Agent | allineamento obiettivi business/tech | outcome adoption, scope clarity |
| Ingestion Agent | pipeline input, dedup, replay | ingest success rate, latency ingest |
| Parser Reliability Agent | robustezza parser/template contracts | parser regression pass rate |
| Data Platform Agent | schema, lineage, data quality store | query p95, data confidence score |
| Analytics Agent | KPI/trend/anomaly engine | KPI correctness, query accuracy |
| Simulation Agent | motore what-if economico/operativo | scenario consistency, explainability |
| API Agent | API contract-first, versioning endpoint | contract stability, error rate |
| Frontend Ops Agent | dashboard executive+operativa | task completion UX, load p95 |
| AI Governance Agent | copilot evidence-first + guardrail | hallucination rate, citation coverage |
| QA Agent | test architecture, release validation | pass rate, escaped defects |
| Security Agent | RBAC, secrets, hardening, audit | vulnerabilities open, policy compliance |
| SRE/DevOps Agent | CI/CD, monitoring, runbook | MTTR, deploy success rate |
| Release Manager Agent | semver, notes, tag policy | release quality, rollback readiness |

## Modalita di coordinamento
- Sprint tecnici settimanali con review Main Architect.
- Checkpoint rischio/qualita ogni 2 settimane.
- DoD obbligatoria per ogni task:
  - codice/documentazione aggiornati;
  - test e evidenze;
  - rollback note;
  - impatto security dichiarato.

## Quality gates obbligatori
1. Parser Gate: regression suite verde.
2. Data Gate: quality score sopra soglia definita.
3. API Gate: contract tests e backward compatibility.
4. Security Gate: zero secret leak + baseline scan.
5. Ops Gate: monitoring e runbook aggiornati.
6. Release Gate: changelog/version tag + smoke check finale.

## Sequenza release fino al primo MVP
- `v0.5.0` Portfolio Convergence Baseline
- `v0.6.0` Data Reliability Core
- `v0.7.0` Analytics + Simulation Core
- `v0.8.0` Operations & Security Hardening
- `v0.9.0-rc1` Pilot Readiness Candidate
- `v1.0.0-mvp` First Business MVP

## Regola operativa del Main Architect
Se un gate critico fallisce, la release non avanza: si apre remediation track con priorita assoluta.
