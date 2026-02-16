# Overview Critica Progetti `mnp*`

Data analisi: **2026-02-16**  
Ambito: `mnpC`, `mnpG`, `mnpJ` (sottocartelle in `/Volumes/HD esterno/Progetti`)

## Metodo di valutazione
- Revisione requisiti/documentazione (`README`, `USER_GUIDE`, `MNP_Matrix_Analyzer_Requirements.md`).
- Ispezione codice sorgente (parser, analytics, UI, DB, packaging, sicurezza).
- Smoke check tecnico (`compileall`) su tutti i sorgenti.
- Test parser su file reale `MNP MATRIX 20251127.xlsx` con misure quantitative.

## Sintesi comparativa

| Progetto | Obiettivo dichiarato | Stato reale sviluppo | Punti forti | Gap critici | Maturità attuale |
|---|---|---|---|---|---|
| `mnpC` | Piattaforma end-to-end (ingestion robusta, analytics, highlights, API/GUI, AI multi-provider) | Codice più ampio e architettura più ricca (schema DB dimensionale, parser avanzato, API Flask) | Data model evoluto, mapping operatori YAML, lineage, motore highlights articolato | Parser daily incompleto su file reale; CLI ingest usa parser XML mentre flusso principale è XLSX; nessun test; repo non governata da git al root | **Prototype avanzato / pre-production** |
| `mnpG` | Tool operativo CLI+Streamlit per ingestion/reporting con AI | Variante più “usabile” e attivamente modificata, UI Streamlit ricca, flusso ingest semplice | Copertura temporale daily migliore su file reale, UX migliore, integrazione AI e filtri periodo | Data model troppo minimale, self-flows non filtrati, alta quota valori zero, assenza test, gestione segreti fragile, branch sporco | **MVP funzionale ma non production-grade** |
| `mnpJ` | Versione precedente del framework `mnpG` | Sostanzialmente fork/snapshot di `mnpG` con meno feature | Struttura pulita e baseline CLI | Meno evoluto di `mnpG`, nessun vantaggio distintivo, assenza test, bassa progressione | **Snapshot tecnico / baseline storica** |

## Evidenze tecniche oggettive

### 1) Integrità codice
- `mnpC`, `mnpG`, `mnpJ`: `python3 -m compileall` **OK**.
- Nessuno dei tre ha una suite test effettiva utilizzabile (in `mnpC` directory test presente ma vuota; in `mnpG`/`mnpJ` assente).

### 2) Parser su file reale (`MNP MATRIX 20251127.xlsx`)

#### `mnpG` / `mnpJ`
- Record totali: **295,200** (`56,880` monthly + `238,320` daily)
- Periodi monthly: **35** (`2023-01-01` → `2025-11-01`)
- Periodi daily: **331** (`2025-01-01` → `2025-11-27`)
- Self-flows (`donor == recipient`): **17,220**
- Valori a zero: **96,868** (**32.81%**)

#### `mnpC`
- Record totali: **145,575** (`48,375` monthly + `97,200` daily)
- Periodi monthly: **36** (`2023-01-01` → `2025-12-01`) 
- Periodi daily: **144** (`2025-01-01` → `2025-05-24`)
- Self-flows: **0**
- Valori a zero: **33,768** (**23.2%**)

### 3) Interpretazione critica dei dati parser
- `mnpG/mnpJ` sembrano coprire meglio il calendario daily (fino a novembre), ma introducono rumore analitico (self-flows + moltissimi zero).
- `mnpC` filtra meglio alcune distorsioni, ma mostra probabile perdita/copertura incompleta del daily (stop a maggio) e un monthly che estende a dicembre in modo da verificare.
- Nessuno dei parser attuali può essere considerato “golden parser” senza un test harness con ground truth.

### 4) Stato repository e governance
- `mnpG` è l’unico root con git attivo, ma è **dirty** con modifiche non committate e file sensibili (`.master.key`, `api_keys.enc`) presenti in working tree.
- `mnpJ` contiene repo git annidata (`MNP-Analyzer`) ma appare come branch secondario.
- `mnpC` non ha git al root progetto principale.

## Valutazione per obiettivi e business readiness

### Ambizione
- Più alta: **`mnpC`** (modello enterprise-oriented, FR/NFR più completi).

### Capacità attuali
- Più immediate in UX e operatività: **`mnpG`**.

### Qualità architetturale di base
- Migliore base dati/governance: **`mnpC`**.

### Prontezza produzione
- Nessuno dei tre è production-grade oggi.
- Bloccanti comuni:
  - assenza test automatici e quality gate CI;
  - parsing non validato con baseline certificata;
  - sicurezza segreti insufficiente;
  - governance rilascio/versioning incompleta.

## Cosa prendere “il meglio” da ciascuno
- Da `mnpC`: schema dati robusto, operator mapping e impostazione NFR/traceability.
- Da `mnpG`: dashboard Streamlit e flusso operativo orientato all’utente.
- Da `mnpJ`: utilità come baseline storica per regression check.

## Conclusione
I progetti `mnp*` rappresentano tre stadi dello stesso percorso: **visione ambiziosa (`mnpC`) + MVP usabile (`mnpG`) + snapshot precedente (`mnpJ`)**. Nessuno singolarmente soddisfa lo standard richiesto per scenari business reali. Serve una convergenza strutturata in un nuovo progetto unificato con testabilità, sicurezza, governance e rilascio progressivo.
