# mnpCDX Next - Development Plan + Revisione Critica

## 1. Piano di sviluppo progressivo fino al primo MVP

### Release `v0.5.0` - Portfolio Convergence Baseline
- deliverable:
  - analisi critica portfolio consolidata;
  - visione prodotto unificata e target architecture;
  - backlog agenti con ownership e gate.
- gate:
  - documentazione approvata da Main Architect;
  - roadmap e versioning allineati.

### Release `v0.6.0` - Data Reliability Core
- deliverable:
  - hardening parser/ingestion;
  - lineage minimo end-to-end;
  - quality checks strutturati.
- gate:
  - regression parser verde su dataset campione;
  - ingest idempotente verificato.

### Release `v0.7.0` - Analytics + Simulation Core
- deliverable:
  - KPI engine consolidato;
  - scenario simulation v1;
  - API contracts stabili.
- gate:
  - test integrazione ingest->kpi->simulation pass;
  - performance baseline p95 rispettata.

### Release `v0.8.0` - Operations & Security Hardening
- deliverable:
  - RBAC base, secret handling enterprise, audit log;
  - observability (metrics/logging/tracing) + runbook.
- gate:
  - security checklist pass;
  - alerting e incident playbook validati.

### Release `v0.9.0-rc1` - Pilot Readiness Candidate
- deliverable:
  - dashboard executive/operativa completa;
  - report generation + AI evidence copilot controllato.
- gate:
  - UAT stakeholder business positivo;
  - no blocker P0/P1 aperti.

### Release `v1.0.0-mvp` - First Business MVP
- deliverable:
  - deployment pilota;
  - quality e performance stabili;
  - governance rilascio operativa.
- gate:
  - 3 cicli business senza regressioni critiche;
  - approvazione congiunta Main Architect + Product Owner.

## 2. Revisione critica del piano

### Rischio A - Scope creep
- problema: progetto trasversale con molte capability rischia deriva continua.
- severita: alta.
- mitigazione: change control board guidata da Main Architect; scope lock per release.

### Rischio B - Dato sorgente instabile
- problema: input eterogenei e variabili possono rompere parser e KPI.
- severita: alta.
- mitigazione: contract tests su template, quarantena automatica, fallback safe.

### Rischio C - Overtrust AI
- problema: output linguistico percepito come verita assoluta.
- severita: alta.
- mitigazione: evidence-first policy, confidence score, blocco publish se confidence bassa.

### Rischio D - Debito operativo
- problema: accelerazione MVP senza observability/security adeguata.
- severita: medio-alta.
- mitigazione: release dedicata hardening (`v0.8.0`) non comprimibile.

### Rischio E - Team coordination failure
- problema: multi-agent execution senza ownership rigorosa.
- severita: media.
- mitigazione: RACI esplicita, decision log, quality gates obbligatori.

## 3. Esito revisione critica
Piano **approvato con condizioni vincolanti**:
1. nessun salto di milestone senza gate verdi;
2. security e observability non rinviabili oltre `v0.8.0`;
3. AI sempre opzionale e non bloccante;
4. versioning semantico rigoroso con changelog firmato dal Main Architect.

## 4. Piano post-review (valido per esecuzione)
- mantenere traiettoria `v0.5.0 -> v1.0.0-mvp`.
- introdurre checkpoint quindicinale di rischio/qualita.
- bloccare nuove feature se quality trend peggiora due sprint consecutivi.
