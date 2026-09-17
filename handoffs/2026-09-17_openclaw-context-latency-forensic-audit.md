# OpenClaw 48h context and latency forensic audit — review handoff

Date: 2026-09-17 UTC. Status: **REVIEW_REQUIRED / PENDING_REVIEW**. Audit mode: retrospective, read only. No production implementation is proposed for this commit.

## Question and verdict

Cleo's 48-hour token load is dominated by accumulated conversation in one long-lived Telegram session: 202.9M of 210.4M derived prompt tokens. A pre-existing reset boundary was followed by a drop in that session's median prompt load from 231k to 34.6k tokens while the historical transcript remained stored. Provider/model, tool work and repeated calls contributed to wall-clock latency; exact provider versus assembly percentages are unavailable without complete historical spans. Optimisation can preserve memory and retrieval.

## Artifacts

- `evidence/2026-09-17-openclaw-context-latency/openclaw-context-latency-forensic-audit.md` — findings, scope, hypotheses, memory distinction, risks and three proposals only.
- `evidence/2026-09-17-openclaw-context-latency/openclaw-turn-metrics-48h.csv` — 1,034 sanitized model-turn rows.
- `evidence/2026-09-17-openclaw-context-latency/evidence-manifest.json` — source and conclusion references.
- `evidence/2026-09-17-openclaw-context-latency/extract_turns.py` — finite read-only parser.
- `evidence/2026-09-17-openclaw-context-latency/analysis-summary.json` — sanitized aggregate calculations.

## Verification and limits

The parser opens Cleo SQLite in read-only mode and does not call the Gateway or network. The report uses a frozen 48-hour window ending 2026-09-17 16:14:20 UTC. Target: 2026-09-17 10:03 Europe/Rome. Gateway rolling logs are partial; OTel exported traces were not active/persisted; historical context reports are partial. CSV UNKNOWNs are deliberate. The remote repository is public, so no raw transcripts, prompts, credentials or personal content are included.

No OpenClaw configuration, Cleo bootstrap/memory, session, log, model, plugin, process, telemetry or scheduler was changed. The primary ledger checkout contained unrelated uncommitted work; this audit was created in a detached linked worktree to keep the commit isolated. Independent review should assess the derivation of prompt tokens, before/after reset interpretation, target timing and privacy of exported metadata. No remediation should be inferred as approved by this audit.
