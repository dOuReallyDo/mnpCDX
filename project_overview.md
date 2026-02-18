# Overview Critica Progetti nelle Sottocartelle

Data analisi: **2026-02-18**  
Ambito: `Bdump`, `mcv`, `nql`, `tcm`, `tiC`, `tss`, baseline `mnpCDX`  
Escluso: `deprecated` (storico non target)

## Metodo usato
- Revisione documentazione (`README`, spec, changelog, piani).
- Ispezione codice reale (entrypoint, architettura, moduli core).
- Verifica segnali di maturita: test presenti, versioning, stato git, packaging.
- Smoke test locale dove possibile (suite `mnpCDX` eseguita: **7 passed**).

## Sintesi comparativa critica

| Progetto | Obiettivo | Stato reale sviluppo | Punti forti | Gap critici | Readiness business |
|---|---|---|---|---|---|
| `Bdump` | Second brain multi-canale (Telegram/LLM/Notion) | Prototype early-stage | idea prodotto chiara, pipeline end-to-end minima | zero test, dipendenza forte API esterne, governance operativa debole | **Bassa** |
| `mcv` | App iOS multi-camera low-latency | Base code + test iOS presenti; roadmap iniziale | architettura Swift MVVM pulita, focus UX/streaming, test unitari mirati | bootstrap recente, RTSP solo via relay, assenza CI release mobile | **Media-bassa** |
| `nql` | Laboratorio didattico ML trading | Single-file Streamlit educativo | ottima didattica interattiva, time-to-demo rapido | monolite, no test, no separazione training/inference, non production-safe | **Bassa** |
| `tcm` | Monitor campagne locali con AI grounding | Prototype frontend centrico | UX immediata, integrazione GenAI veloce | backend/storage enterprise mancanti, no test, sicurezza e auditing deboli | **Bassa** |
| `tiC` | Cockpit economics CVM con export operativo | MVP avanzato con API reali e packaging locale | forte valore business, motore economico consistente, API utili | test coverage minima (1 test), osservabilita/security da irrobustire | **Media-alta** |
| `tss` | Piattaforma ML trading end-to-end | Ambiziosa, ampia ma eterogenea | stack completo (data, ML, API, GUI), documentazione ricca, test presenti | complessita elevata, setup non uniforme, rischio dispersione scope | **Media** |
| `mnpCDX` | Piattaforma analytics MNP production-oriented | MVP tecnico attivo con API/UI/CLI + test | base architetturale solida, template engine, quality gate iniziale, release notes | servono SLO, sicurezza enterprise, CI piu dura, E2E su dataset realistici | **Media-alta** |

## Valutazione degli assi richiesti

### 1) Ambiziosita obiettivi
- Piu ambiziosi: `tss` (piattaforma ML completa), `mnpCDX` (decision platform verticale), `tiC` (DSS operativo enterprise).

### 2) Features gia previste/pianificate con valore reale
- Miglior combinazione pragmatico-business: `tiC` + `mnpCDX`.
- Miglior profondita tecnica di sistema: `tss`.
- Miglior attenzione UX specialistica: `mcv`.
- Miglior velocita prototipale: `tcm`, `Bdump`, `nql`.

### 3) Qualita e production-readiness
- Nessun progetto e ancora pienamente production-grade enterprise.
- I piu vicini: `mnpCDX` e `tiC`.
- Gap comuni ricorrenti:
  - test coverage non sufficiente o non eseguibile ovunque;
  - assenza quality gates CI/CD omogenei;
  - security hardening incompleto (secret governance, audit trails, RBAC);
  - mancanza di SLO/SLA formali con monitoring operativo.

## “Best-of” da assorbire nel nuovo progetto
- Da `mnpCDX`: ingestion strutturata, analytics API-first, template intelligence.
- Da `tiC`: focus su scenario business reale, simulazione/what-if, export operativo.
- Da `tss`: MLOps e pipeline modello multi-stadio, approccio quantitativo avanzato.
- Da `mcv`: disciplina UX orientata all’operatore in tempo reale.
- Da `tcm`: rapidita di acquisizione insight da fonti esterne.
- Da `Bdump`: flusso capture->classify->route estremamente pratico.
- Da `nql`: explainability didattica e trasparenza del ragionamento numerico.

## Conclusione critica
Il portafoglio mostra idee forti ma frammentate. La strategia corretta non e creare un altro prototipo, ma convergere in un unico programma **mnpCDX Next**: piattaforma decisionale production-grade che unisce ingestion affidabile, simulazione business, AI governance, quality engineering e operabilita enterprise.
