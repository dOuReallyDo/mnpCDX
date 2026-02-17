# Portfolio Team Distribution Plan (Lean)

Data: 2026-02-17

## Strategia di esecuzione
- Sequenziale tra progetti: una sola lane attiva alla volta.
- Distribuzione stabile: ogni progetto ha il suo team già definito.
- Parallelismo interno minimo: al massimo 2 task tecnici in parallelo per progetto attivo.

## Composizione standard team (4 membri)
- Chief Architect: ownership architettura, priorità, gate tecnici.
- Context Steward: memoria critica, sintesi, handoff, coerenza.
- Implementation Engineer: sviluppo feature e refactor.
- QA/Release Engineer: test, qualità, packaging, release notes.

## Team assegnati
1. Team A (`mnpCDX`)
- Chief Architect: Data Platform Architect
- Context Steward: Product Memory Lead
- Focus: ingestion template-aware, UI operativa, stabilità API

2. Team B (`tiC`)
- Chief Architect: Mobile/Cloud Architect
- Context Steward: UX/Spec Memory Lead
- Focus: roadmap esecutiva e hardening release

3. Team C (`tss`)
- Chief Architect: ML/Trading Architect
- Context Steward: Experiment Tracking Lead
- Focus: convergenza branch, quality gate GUI/ML

4. Team D (`tcm`)
- Chief Architect: Platform Automation Architect
- Context Steward: Workflow Knowledge Lead
- Focus: affidabilità pipeline e operatività locale

5. Team E (`mcv`)
- Chief Architect: iOS Streaming Architect
- Context Steward: iOS Decision Log Lead
- Focus: baseline app e readiness test iOS

6. Team F (`nql`)
- Chief Architect: Backend Query Architect
- Context Steward: API Contract Memory Lead
- Focus: maturità API e qualità integrazione

7. Team G (`Bdump`)
- Chief Architect: Data Tooling Architect
- Context Steward: Data Retention Lead
- Focus: productizzazione e casi business reali

## Ordine operativo proposto (sequenza)
1. `mnpCDX`
2. `tiC`
3. `tss`
4. `tcm`
5. `mcv`
6. `nql`
7. `Bdump`

## Regole di handoff tra progetti
- Handoff massimo 1 pagina markdown.
- Stato obbligatorio: milestone, commit hash, rischi, prossima azione unica.
- Il progetto successivo si attiva solo dopo push e handoff validato.

## Revisione critica del modello
Punti deboli:
- rischio rallentamento con WIP=1 su incidenti urgenti;
- dipendenza forte dalla qualità del Context Steward.

Mitigazioni:
- fast lane eccezioni: massimo 1 hotfix parallelo con timebox 2h;
- checklist di qualità handoff standardizzata;
- rotazione periodica Context Steward tra team per ridurre bias.
