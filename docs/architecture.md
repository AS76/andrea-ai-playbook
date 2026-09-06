# Architecture

## Pattern

Andrea AI Playbook usa una architettura hub-and-spoke.

- Hub: Cleo riceve, classifica e instrada.
- Spoke: agenti specializzati eseguono entro il loro dominio.
- Control plane: policy, routing, autonomy levels e confidence framework.
- Evaluation layer: test cases in `evals/`.

## Lifecycle

1. Intake: ricezione richiesta utente.
2. Classification: dominio, rischio, tool necessari, output atteso.
3. Routing: selezione agente primario e secondario.
4. Autonomy check: limite massimo L0-L4 per il task.
5. Execution: produzione analisi, draft, modifica interna o richiesta approvazione.
6. Verification: controllo fonti, test, diff o QA gate.
7. Delivery: output sintetico con assunzioni, TODO e rischi residui.

## Boundaries

- Legal, immigration, financial and external commitments stop at draft/recommendation unless explicitly approved.
- Software and config changes can reach L3 only for internal files and with review.
- External side effects are always L4.

## Source of truth

1. User instruction.

## Vault writing policy

Every agent that writes into the Obsidian vault (`/root/.openclaw/workspace/main/vault/`) MUST follow the 6 hard rules in [policies/vault-schema.md](../policies/vault-schema.md). Detector script is reusable (`/tmp/scanner_violations.py`). Cron `vault-lint-daily` is pending Cleo approval (planned 23:50 Europe/Rome, 21:50 UTC).
2. Repository policy files.
3. Machine-readable config files.
4. Agent files.
5. Narrative site content.

If sources conflict, the stricter safety rule wins.
