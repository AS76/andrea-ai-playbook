# CURRENT TASK

Request: safely remediate the reported OpenClaw startup/state migration issue, then implement a reusable conservative safe-update transaction with backup, Doctor gating, lifecycle control, acceptance, rollback distinctions, locking, structured logs, and a runbook.
Overall status: REVIEW_REQUIRED
ChatGPT Review: PENDING_REVIEW
Engineering acceptance: PASS_WITH_WARNINGS

Confirmed initial state: not yet established. The reported 2026.9.3 version, healthy user Gateway, pending migration, Telegram allowlist gap, task/audit counts, and no-update result are being treated as untrusted until independently verified.

Authorized scope: read-only discovery; verified encrypted S3 recovery point; minimal supported migration remediation from an independent shell with the Gateway stopped; post-start acceptance; evidence-based Telegram allowlist correction only if trusted IDs and supported keys are proven; and implementation/testing of the permanent safe-update workflow. Model routing, topology, ClawMem, Vault, MCP, OpenRouter, Codex, unrelated services, cleanup, and broad audit remediation are excluded.

Plan: analyze -> document intended narrow changes and rollback -> stream/verify backup -> remediate only if Doctor scope is understood -> restart and validate -> implement and simulate/test the reusable workflow -> publish sanitized evidence for independent review.

Result: no migration was present in either Doctor mode, so no Doctor fix or Gateway restart was justified. Telegram account allowlists were already populated and healthy. A 2026.9.4 candidate exists, but official dry-run refuses package-manager ownership and installed updater source can invoke Doctor fix; update was stopped before mutation. The wrapper/runbook now provide locking, verified S3 backup, explicit status JSON, preflight/no-update/failure gates, and a conservative manual-review boundary. Handoff: `handoffs/2026-09-12_0705_openclaw-safe-update.md`.

Prior task preserved: `handoffs/2026-09-10_0812_scout-v41-flash.md` and `evidence/2026-09-10-scout-v41/` remain unchanged with their pending review history.
