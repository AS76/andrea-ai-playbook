# CURRENT TASK

## Request

Make the approved Codex-GitHub-ChatGPT Handoff Ledger the persistent default
workflow for future significant Codex tasks, with autonomous review/remediation
handling and no ledger noise for trivial work.

## Objective

Future Codex sessions operating under `/root/AGENTS.md` automatically invoke the
existing ledger for significant work. The existing helper validates state
transitions, selects the newest applicable review and verifies local/remote/PR
head consistency.

## Scope

- Persistent Codex instruction in `/root/AGENTS.md`
- Existing ledger policy and helper behavior
- State-machine and review-selection tests
- Current task handoff and GitHub review request

## Out of Scope

- Redesigning the ledger
- Another memory system
- OpenClaw, ClawMem, Vault, cron, systemd or agent configuration
- Synthetic GitHub review creation

## Initial State

- The ledger implementation was approved and its review history was preserved.
- The workflow existed in repository documentation but was not referenced by the
  persistent VPS-level Codex instructions.
- The helper validated structure and secrets but did not simulate the complete
  verdict state machine, identify the latest valid review or compare three heads.

## Plan

1. Add a concise persistent trigger to `/root/AGENTS.md`.
2. Add one operational policy to the existing ledger architecture.
3. Extend `tools/codex-handoff` with state, review and head checks.
4. Test approval, remediation and blocked-evidence paths.
5. Validate, scan, commit, push and request ChatGPT review.

## Execution Status

- [x] Audit
- [x] Implementation
- [x] Tests
- [x] Runtime verification
- [x] Documentation
- [x] Handoff
- [ ] ChatGPT review
- [ ] Final closure

## Current Findings

- `/root/AGENTS.md` is the effective persistent instruction point for future
  Codex work under the VPS root.
- Review applicability requires PR, exact reviewed SHA, verdict and immutable
  review record; filename recency alone is insufficient.
- A later closure commit is correctly distinct from the commit ChatGPT reviewed.

## Blockers / Decisions

None. This significant policy change requires a fresh independent review before
closure.
