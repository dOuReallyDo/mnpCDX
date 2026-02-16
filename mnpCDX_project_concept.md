# Progetto `mnpCDX`: Visione Superiore

## Missione
Costruire una **MNP Intelligence Platform production-grade** che converta i file settimanali MNP in decision intelligence affidabile, auditabile e azionabile per scenari enterprise telco.

## Tesi di valore
`mnpCDX` combina:
- la profondità architetturale di `mnpC`;
- l’usabilità operativa di `mnpG`;
- la disciplina di versioning/reproducibility assente nei progetti attuali.

Risultato: una piattaforma pronta a supportare **decisioni commerciali, competitive e di retention** con qualità dati verificabile e time-to-insight ridotto.

## Ambizione (oltre i progetti esistenti)
1. **Single source of truth certificata**
- ingestione idempotente con lineage completo cella→record→KPI→report.

2. **Decision intelligence multi-livello**
- KPI standard + segnali avanzati (anomalie, mix shift, corridor dynamics, rischio churn competitivo).

3. **Copertura enterprise end-to-end**
- parser robusto, API, dashboard, orchestration AI, monitoraggio qualità, release governance.

4. **Production readiness reale**
- test automatici, quality gate CI, segreti gestiti in modo sicuro, artefatti versionati, rollback strategy.

## Capability set target
- Ingestion hub (upload/API/scheduler) con dedup checksum e replay storico.
- Parser MNP con validazioni strutturali, normalizzazione operatori e gestione merged/header complessi.
- Data platform con layer raw/staging/gold e metric store.
- Analytics engine per KPI port-in/out/net, quote, corridoi competitivi, early warnings.
- AI Insight Orchestrator con prompt governance e output citabile sui dati disponibili.
- API contract-first per integrazione BI/CRM/decision platform.
- Dashboard executive + operational (drill-down per operatore, periodo, competitor).

## Standard qualitativo richiesto
- **Affidabilità**: SLO parsing e API definiti.
- **Auditabilità**: ogni numero nel report deve essere tracciabile.
- **Sicurezza**: segregazione credenziali, cifratura at-rest per secret material.
- **Manutenibilità**: architettura modulare, test coverage minima obbligatoria.
- **Scalabilità**: crescita multi-anno senza degrado analitico percepibile.

## Outcome business attesi
- Riduzione tempo analisi settimanale da ore manuali a minuti.
- Migliore capacità di intercettare segnali deboli di perdita/acquisizione.
- Maggiore affidabilità decisionale in war-room commerciale e planning retention.
- Base pronta per estensione cross-country/cross-brand.

## Posizionamento
`mnpCDX` non è un tool “di reportistica”, ma un **sistema operativo decisionale MNP** per uso reale in contesti business critici.
