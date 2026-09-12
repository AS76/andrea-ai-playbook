# CHANGE RECORD

Component: Persistent Codex review workflow
Date: 2026-09-03
Owner: Codex implementation; Andrea final authority
Implementation commit: PR `#1` HEAD (`refs/pull/1/head`)
Reason: Make the approved ledger automatic for future significant Codex tasks.

## Before

The ledger was operational and approved, but the VPS-level Codex instructions
did not invoke it automatically. The helper covered structure, secrets and basic
commit identity only.

## After

`/root/AGENTS.md` triggers the ledger for significant work and excludes trivial
noise. The existing helper validates approval, remediation and blocked-evidence
paths; parses the latest review metadata; checks persistent-policy installation;
and compares local, remote and PR heads.

## Why

Andrea should initiate work once and act only at review or final-decision gates,
without repeatedly requesting handoff documentation or relaying transcripts.

## Files / Config

Codex instruction and ledger repository files only. No OpenClaw, ClawMem, Vault,
cron, systemd, agent or service configuration changed.

## Verification

See `handoffs/2026-09-03_0635_persistent-review-workflow.md`.

## Rollback

Revert the implementation commit and remove only the appended
“Significant-Task GitHub Review Ledger” section from `/root/AGENTS.md`.

## References

- `architecture/operational-workflow.md`
- `CURRENT_TASK.md`
- `STATUS.md`
