# Andrea AI Playbook - Operating Repository v5.0

Repository operativo per il sistema multi-agent OpenClaw di Andrea Sassi.

La GitHub Page resta la vetrina pubblica del progetto:

- Page root: https://as76.github.io/andrea-ai-playbook/
- Dashboard source: [docs/index.html](docs/index.html)

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

## File principali

- [docs/identity.md](docs/identity.md): identita narrativa e visuale derivata dal sito v4.3.
- [docs/architecture.md](docs/architecture.md): architettura hub-and-spoke e lifecycle operativo.
- [docs/operating-model.md](docs/operating-model.md): modello operativo v5.0.
- [configs/routing.yaml](configs/routing.yaml): routing machine-readable.
- [configs/openclaw.agents.yaml](configs/openclaw.agents.yaml): inventario agenti da verificare contro OpenClaw reale.
- [policies/autonomy.md](policies/autonomy.md): livelli L0-L4.
- [policies/vault-schema.md](policies/vault-schema.md): regole hard-rule scrittura vault Obsidian (6 lesson dal fix 2026-06-21).
- [evals/routing-tests.md](evals/routing-tests.md): test cases end-to-end.

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
