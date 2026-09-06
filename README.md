# Andrea AI Playbook - Operating Repository v5.0

Repository operativo per il sistema multi-agent OpenClaw di Andrea Sassi.

[Visualizza il Playbook](https://as76.github.io/andrea-ai-playbook/)

Multi-Agent Operating System — IT/EN bilingual.

## Codex Handoff Ledger

This repository also carries the asynchronous engineering-review ledger between
Codex CLI and ChatGPT. It is evidence and change history, not a memory store.

Start at [STATUS.md](STATUS.md), follow the current handoff, review the named
commit and diff, then preserve the review as a new file under `reviews/`.
The persistent default process is defined in
[architecture/operational-workflow.md](architecture/operational-workflow.md).

Authority remains explicit:

- Codex executes and verifies the production runtime.
- ChatGPT independently reviews architecture, diffs and evidence quality.
- ClawMem provides semantic working context; the Obsidian Vault remains the
  canonical knowledge layer where applicable.
- Andrea is the final authority.

Public-repository rule: never add secrets, raw logs, private correspondence,
memory dumps, real infrastructure identifiers or unnecessary personal data.

La GitHub Page resta la vetrina pubblica del progetto:

- Page root: https://as76.github.io/andrea-ai-playbook/
- Dashboard source: [index.html](index.html)

## Scopo

Questo repository separa identita, documentazione narrativa e contenuti operativi versionabili:

- agenti e responsabilita
- routing e fallback
- livelli di autonomia
- policy di tool, memoria, sicurezza e confidence
- test cases per routing, delega, tool use e rischio allucinazioni

Il README non e il playbook completo. La sorgente operativa primaria e nei file strutturati.

## Struttura

```text
/
├─ README.md
├─ docs/
│  ├─ index.html
│  ├─ architecture.md
│  ├─ identity.md
│  └─ operating-model.md
├─ agents/
├─ policies/
├─ configs/
├─ evals/
└─ CHANGELOG.md
```

La struttura sopra include percorsi pianificati; i riferimenti mancanti sono indicati esplicitamente sotto. Il dashboard attuale è `index.html` nella radice.

## File principali

- `docs/identity.md` (previsto; non presente nel repository): identita narrativa e visuale derivata dal sito v4.3.
- [docs/architecture.md](docs/architecture.md): architettura hub-and-spoke e lifecycle operativo.
- `docs/operating-model.md` (previsto; non presente nel repository): modello operativo v5.0.
- `configs/routing.yaml` (previsto; non presente nel repository): routing machine-readable.
- `configs/openclaw.agents.yaml` (previsto; non presente nel repository): inventario agenti da verificare contro OpenClaw reale.
- `policies/autonomy.md` (previsto; non presente nel repository): livelli L0-L4.
- [policies/vault-schema.md](policies/vault-schema.md): regole hard-rule scrittura vault Obsidian (6 lesson dal fix 2026-06-21).
- `evals/routing-tests.md` (previsto; non presente nel repository): test cases end-to-end.

## Regole operative base

- Le modifiche di questo repository restano dentro `andrea-ai-playbook`.
- Nessuna azione esterna senza approvazione esplicita.
- Nessuna email inviata senza conferma.
- Nessuna modifica distruttiva senza backup e approvazione.
- Nessuna memoria permanente senza consenso.
- Claim fattuali marcati come KNOWN / BELIEVED / ASSUMED quando rilevante.
- Se la confidence e bassa, delegare o chiedere conferma.

## Stato configurazione

I modelli e i provider presenti nei file `configs/` sono derivati dai contenuti del sito v4.3 o marcati come TODO. Non sostituiscono la configurazione reale OpenClaw finche non vengono verificati contro l'ambiente di produzione.
