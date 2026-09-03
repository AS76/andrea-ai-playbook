# CODEX HANDOFF

## Metadata

Date: 2026-09-03T06:35:56Z
Codex session: persistent-review-workflow
Host: production-vps
Component: Codex Handoff Ledger operational policy
Codex Status: PASS
Runtime Verification: PASS
ChatGPT Review: PENDING_REVIEW
Current Commit: PR `#1` HEAD (`refs/pull/1/head`)
Reviewed Commit: PR `#1` HEAD (`refs/pull/1/head`)
Branch: `codex/handoff-ledger`
Related task: `CURRENT_TASK.md`
Related issue/PR: GitHub PR `#1`
Related ClawMem context: GitHub handoff ledger deployment and approval
Related review: `reviews/2026-09-03_0624_github-handoff-ledger.md`

## Request

Make the existing ledger the automatic default for future significant Codex
tasks, including review ingestion and approval, remediation and evidence loops.

## Initial State

The ledger and review history were operational and approved. Persistent Codex
instructions did not yet trigger it automatically, and the helper lacked state,
review-selection and three-head checks.

## Findings

### FACT

- `/root/AGENTS.md` is the persistent instruction source applicable to future
  Codex work under `/root`.
- The real APPROVED review remains immutable at
  `reviews/2026-09-03_0624_github-handoff-ledger.md` and applies to exact commit
  `0a372451ca9014b7e2ffc9dccbf2d9084af40c18`.
- Current and closure commits are already modeled separately.

### INFERENCE

- A concise rule in the existing instruction authority plus executable helper
  checks is the minimum mechanism that makes the workflow persistent.

### UNVERIFIED

- Automatic direct ChatGPT GitHub writes remain environment-dependent; relay
  mode remains supported.

## Actions Performed

- Added a significant-task ledger rule to `/root/AGENTS.md`.
- Added one operational policy under the existing architecture directory.
- Extended the existing helper with synthetic state-machine tests, strict latest
  review parsing and local/remote/PR head comparison.
- Preserved all earlier review files without modification.

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `/root/AGENTS.md` | modified | Persistent automatic trigger for future Codex tasks |
| `README.md` | modified | Link the operational policy |
| `architecture/operational-workflow.md` | created | Canonical execution and verdict-handling procedure |
| `changes/2026-09-03_persistent-review-workflow.md` | created | Durable operational change record |
| `tools/codex-handoff` | modified | State, review and head validation |
| `STATUS.md` | modified | Current significant-task state |
| `CURRENT_TASK.md` | modified | Current task scope and execution record |
| this handoff | created | Review package |

## Configuration Changes

Codex instruction/documentation only. No OpenClaw, ClawMem, Vault, cron,
systemd, agent or runtime-service configuration changed.

## Tests Executed

| Test | Result | Evidence |
|---|---|---|
| Approval lifecycle | PASS | `RUNNING -> REVIEW_REQUIRED -> PENDING_REVIEW -> APPROVED -> COMPLETE` |
| Changes-requested lifecycle | PASS | `PENDING_REVIEW -> CHANGES_REQUESTED -> REMEDIATION -> PENDING_REVIEW` |
| Blocked evidence lifecycle | PASS | `PENDING_REVIEW -> BLOCKED -> EVIDENCE_COLLECTION -> PENDING_REVIEW` |
| Illegal direct closure | PASS | `RUNNING -> COMPLETE` rejected |
| Persistent activation | PASS | `/root/AGENTS.md` contained all seven required policy markers |
| Latest review selection | PASS | Selected preserved APPROVED review for PR `#1`, exact SHA `0a372451ca9014b7e2ffc9dccbf2d9084af40c18` |
| Three-head equality | PENDING | Must match after final push |
| Review immutability | PASS | Both historical review blob hashes unchanged from current HEAD |
| Structure and secrets | PASS | Verify and secret-scan returned zero findings |

## Runtime Verification

This change affects persistent Codex behavior, not OpenClaw runtime. Runtime
verification consists of invoking the installed `/root/AGENTS.md` policy and the
actual ledger helper from this worktree. No production service restart is
required or authorized. Installed `/root/AGENTS.md` SHA-256 after policy
activation: `0dd8565e79e6f5f9b2a25a28a142be14837b82232b70725d20bdf9b8a07e9f17`.

## Git Diff Summary

One persistent instruction block, one existing-ledger policy, helper validation
extensions, and the required current task/handoff metadata.

## Risks

- Direct ChatGPT review write capability remains dependent on connector identity.
- Codex must still apply judgment when classifying borderline tasks as significant.

## Rollback

Revert the ledger implementation commit and remove only the “Significant-Task
GitHub Review Ledger” section appended to `/root/AGENTS.md`. No service or data
rollback is required.

## Remaining Work

Commit, push, verify final heads and obtain independent review.

## Recommended Next Action

ChatGPT review of the current PR head after publication.

## ChatGPT Review Request

Review requested: YES
Review scope: persistent activation, significance boundary, state-machine paths,
review applicability, commit identity, emergency priority and memory/security separation
Reviewed commit: PR `#1` HEAD (`refs/pull/1/head`)
Evidence requiring review: policy, helper diff, tests, persistent instruction and
preserved review history
