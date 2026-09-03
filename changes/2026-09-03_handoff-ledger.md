# CHANGE RECORD

Component: Codex-GitHub-ChatGPT Handoff Ledger
Date: 2026-09-03
Owner: Codex implementation; Andrea final authority
Commit: PENDING
Reason: Remove manual transcript copying while preserving independent review and runtime authority boundaries.

## Before

No repository-level entry point, standard evidence package, review verdict
archive, or secret-safe helper existed for Codex-to-ChatGPT review.

## After

The repository provides status/task entry points, immutable handoff and review
records, change/incident templates, an architecture contract and a validation
helper. Significant work is gated on independent review before final closure.

## Why

GitHub provides an asynchronous, inspectable engineering ledger without granting
ChatGPT SSH access or duplicating ClawMem and Vault content.

## Files / Config

Repository documentation and `tools/codex-handoff` only. No OpenClaw, ClawMem,
Vault, cron or systemd configuration changed.

## Verification

See `handoffs/2026-09-03_0611_github-handoff-ledger.md`.

## Rollback

Revert the ledger deployment commit. No runtime service rollback is required.

## References

- `architecture/ledger-model.md`
- `STATUS.md`
- `CURRENT_TASK.md`
