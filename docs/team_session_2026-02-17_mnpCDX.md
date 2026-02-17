# Team Session - mnpCDX (2026-02-17)

## Team ex novo
- Chief Architect: Data Platform lead
- Context Steward: memoria decisioni, handoff e coerenza backlog
- Implementation Engineer: hardening API/UI template workflow
- QA/Release Engineer: test regressione e quality gate

## Scope incremento
- Eliminare errori 500 opachi nella pipeline template analyze/ingest.
- Fornire messaggi errore operativi con reference id.
- Migliorare handling errore lato Web UI.

## Definition of Done
- API template endpoints restituiscono errore esplicativo in caso di eccezioni inattese.
- Web UI mostra messaggio leggibile (non dump JSON).
- Test automatici coprono i nuovi percorsi di errore.
- Release note aggiornate.

## Outcome
- Hardening applicato su backend e frontend.
- Nuovi test API aggiunti e validati localmente.
