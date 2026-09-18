# Cleo to Hermes candidate — engineering handoff

**Verdict: READY_FOR_ANDREA_REVIEW.** This means candidate text is ready to review. It does not mean behavioral acceptance, technical parity, or permission to install.

## Scope and evidence

Reviewed current Hermes v0.21.3, active default profile, installed prompt/memory/profile source, official Hermes docs (checked 2026-09-18), current Cleo playbook and injected governance, selected local Cleo exchanges, and a narrowly retrieved ClawMem communication preference note. Archived OpenClaw frameworks were treated as superseded. Raw conversations and sensitive biography are omitted.

## Design

The candidate gives Hermes a trusted-colleague stance, direct Italian voice, context-sensitive warmth, quiet continuity, frank disagreement, and calm repair. It leaves technical instructions in project context and starts with a tiny USER seed and empty MEMORY. See behavioral profile, mapping, and SOUL candidate.

The separate human-interaction review tests warmth, agency, conversational repair, transparency, and attachment boundaries. It identifies three concrete overplay risks for Andrea to judge.

## Context budget

The SOUL is 1,743 characters (about 500 tokens by rough character estimate), far below Hermes' dynamic per-file cap. USER seed is 493 characters against the 1,375-character limit; MEMORY starts empty against 2,200 characters. No personality overlay is needed. Prompt-pressure risks are in the mapping.

## Risks and unanswered questions

- Existing `openrouter/auto` makes controlled prompt evaluation impossible until one exact model is pinned with Andrea's approval. No model change occurred.
- Sampled conversations did not establish a strong set of positively rated casual Cleo exchanges. Andrea should judge the candidate's voice directly; a single refinement round may be needed.
- Fresh profiles isolate credentials, channels, memory, cron, and state. Tool/MCP/messaging/routine parity requires deliberate, separate verification after approval.
- Built-in memory write approval does not control Honcho's automatic message sync. Candidate Honcho workspace and `saveMessages` must be reviewed independently before the first conversation.
- The candidate's emotional language may still become scripted under the current model; acceptance scenarios will reveal this.

Expected benefit is a more natural everyday voice without replacing Hermes' tools or architecture. Behavioral risk is persona overplay or canned empathy; technical risk is incomplete profile capability wiring or unintended memory sharing. The acceptance suite and rollback file define the checks and stop path.

## Files changed and untouched

Changed: local staging files and sanitized ledger review branch documents. Untouched: default Hermes config/SOUL/USER/MEMORY, profile registry, gateway, OpenClaw, model routing, services, databases, cron, and the existing ledger checkout (its unrelated work remains intact).

## Next gate

Andrea reviews the candidate SOUL, USER seed, memory policy, technical findings, risk, and rollback. After explicit approval, create and test only `cleo-candidate`. Human ratings and the decisive choice question determine behavioral acceptance. No profile installation, paid test, or model pin is authorized by this handoff alone.
