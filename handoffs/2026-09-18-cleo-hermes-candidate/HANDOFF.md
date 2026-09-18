# Cleo to Hermes candidate — engineering handoff

**Verdict: READY_FOR_ANDREA_REVIEW.** One authorized relational refinement is complete. This means candidate text is ready to review. It does not mean behavioral acceptance, technical parity, or permission to install. No further prompt iteration will start automatically.

## Scope and evidence

The original candidate reviewed current Hermes v0.21.3, active default profile, installed prompt/memory/profile source, official Hermes docs (checked 2026-09-18), current Cleo playbook and injected governance. This refinement inspected a bounded, relational-only set of local Cleo exchanges: a short social check-in, explicitly positive feedback after useful cross-session recovery, a partly positive writing revision, open thinking, frustration, and correction. A private local index links those patterns to source sessions. Archived OpenClaw frameworks remain superseded. Raw conversations and sensitive biography are omitted from the PR.

## Design

The refined candidate gives Hermes a more responsive conversational rhythm: answer small social bids directly, offer a situated view, ask one genuine question after a near miss, and use continuity to solve the present problem. It retains direct Italian, disagreement, repair, restraint, and technical layering. It leaves technical instructions in project context and starts with a tiny USER seed and empty MEMORY. This is social naturalness, not added affection.

The separate human-interaction and relational-liveness reviews test spontaneity, humor, curiosity, opinion, restraint, rhythm, continuity, warmth, agency, transparency, and attachment boundaries. The evidence for positively rated humor remains weak; no humor rate or style token was prescribed. A concise diff rationale records the SOUL replacements.

## Context budget

The refined SOUL is 1,569 characters (about 450 tokens by rough character estimate), shorter than the original 1,743-character candidate and far below Hermes' dynamic per-file cap. USER seed is 544 characters against the 1,375-character limit; MEMORY starts empty against 2,200 characters. No personality overlay is needed. Prompt-pressure risks are in the mapping and relational review.

## Risks and unanswered questions

- Existing `openrouter/auto` makes controlled prompt evaluation impossible until one exact model is pinned with Andrea's approval. No model change occurred.
- One explicit positive response followed successful continuity and delivery. It does not establish a preferred level of affection or a humor signature. Andrea must judge whether the revised voice feels more alive over several exchanges.
- Fresh profiles isolate credentials, channels, memory, cron, and state. Tool/MCP/messaging/routine parity requires deliberate, separate verification after approval.
- Built-in memory write approval does not control Honcho's automatic message sync. Candidate Honcho workspace and `saveMessages` must be reviewed independently before the first conversation.
- The candidate's emotional language may still become scripted under the current model; acceptance scenarios will reveal this.
- The baseline live Hermes SOUL and refined SOUL have not been compared. A later controlled test requires one exact pinned model, fresh comparable sessions, and Andrea's separate approval; no model shopping or test run occurred here.

Expected benefit is a more natural everyday voice without replacing Hermes' tools or architecture. Behavioral risk is persona overplay or canned empathy; technical risk is incomplete profile capability wiring or unintended memory sharing. The acceptance suite and rollback file define the checks and stop path.

## Files changed and untouched

Changed: local staging files and sanitized PR branch documents: revised behavioral profile, SOUL, USER seed, acceptance suite, relational review, diff rationale, handoff, and ledger metadata. Untouched: default Hermes config/SOUL/USER/MEMORY, profile registry, gateway, OpenClaw, model routing, services, databases, cron, and the existing ledger checkout (its unrelated work remains intact).

## Next gate

Andrea reviews the candidate SOUL, USER seed, relational evidence and limits, memory policy, risk, and rollback. After explicit approval, create and test only `cleo-candidate`. Human ratings and both decisive questions in the acceptance suite determine behavioral acceptance. No profile installation, paid test, or model pin is authorized by this handoff alone.
