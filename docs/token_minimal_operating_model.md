# Token-Minimal Operating Model

Data: 2026-02-17

## Obiettivo
Ridurre al minimo token e contesto mantenendo coerenza operativa alta su portfolio multi-progetto.

## Principi
- WIP globale: un solo progetto in esecuzione attiva per volta.
- Team distribuiti: un team dedicato per progetto, attivazione sequenziale.
- Contesto minimo: aprire solo file strettamente necessari al task corrente.
- Decisioni tracciate: ogni scelta tecnica deve avere una nota breve e referenziabile.

## Budget di contesto (hard limits)
- `Startup brief` per progetto: massimo 120 righe.
- `Session delta`: massimo 12 bullet per avanzamento.
- File attivi contemporanei: massimo 5 file di progetto + 2 file portfolio.
- Nessuna rilettura completa della codebase: usare indice file + ricerca mirata (`rg`).
- Nessun log verboso in chat: solo outcome, hash commit, rischi aperti.

## Artefatti minimi obbligatori per progetto
- `docs/PROJECT_STATE.md`: stato corrente, milestone, blocker.
- `docs/DECISIONS.md`: ADR sintetiche (ID, scelta, motivazione, impatto).
- `docs/HANDOFF.md`: cosa e stato fatto, cosa manca, next action.
- `docs/WORK_QUEUE.yaml`: backlog breve e prioritizzato.

## Flusso sequenziale standard
1. `Activate`: il Main Architect attiva un solo progetto.
2. `Load`: Context Steward carica solo `PROJECT_STATE`, `DECISIONS`, `WORK_QUEUE`.
3. `Execute`: engineering slice piccole (1 scope, 1 commit).
4. `Validate`: smoke test minimo + quality gate.
5. `Document`: aggiornamento `PROJECT_STATE` e `HANDOFF`.
6. `Commit/Push`: commit semantico e push remoto.
7. `Freeze`: chiusura contesto e passaggio al progetto successivo.

## Ruolo obbligatorio: Context Steward
Responsabilità:
- mantenere memoria critica e coerenza lessicale/tecnica;
- comprimere il contesto in note operative brevi;
- evitare duplicazioni e drift tra backlog, codice e documentazione;
- validare che ogni handoff sia autosufficiente.

## Regole anti-drift
- Ogni ticket deve referenziare un ID decisione o una voce backlog.
- Nessun task parte senza entry in `WORK_QUEUE.yaml`.
- Nessun merge senza update di `PROJECT_STATE.md`.
- Se il contesto supera i limiti: stop, sintesi, ripartenza da snapshot.
