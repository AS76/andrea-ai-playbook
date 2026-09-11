# CURRENT TASK

Request: apply one supported minimal lifecycle correction for MCP runtimes created by isolated Cleo heartbeats, then validate it across one natural heartbeat with a detached observer.
Overall status: COMPLETE
ChatGPT Review: APPROVED_WITH_NOTES
Engineering acceptance: PASS_WITH_ACCEPTED_NOTES

Confirmed initial state: Cleo's 30-minute isolated heartbeat creates a fresh session-scoped three-server MCP cohort; completed cohorts remain because `mcp.sessionIdleTtlMs` is absent and resolves to zero. `memory-probe.sh` remains suspended.

Authorized scope: first determine whether run-end MCP cleanup is supported and heartbeat-scoped. Use it only if supported; otherwise configure only `mcp.sessionIdleTtlMs = 900000`. Stream and verify an encrypted rollback directly to established S3 before mutation. Do not patch source, alter heartbeat cadence, re-enable memory-probe, change models, or add secondary hardening.

Result: installed 2026.9.3 exposes `cleanupBundleMcpOnRunEnd` only as an internal run parameter, not as a supported heartbeat-scoped configuration option. Applied only `mcp.sessionIdleTtlMs = 900000` after a verified encrypted S3 rollback. One controlled Gateway restart loaded the setting. A detached observer captured one natural heartbeat, its three local MCP runtime groups, and complete reclamation at 11:54:21 UTC after the configured TTL. The Gateway PID remained unchanged, OOM counters stayed zero, and ten consecutive isolated heartbeats completed with fresh session IDs without leaving a retained cohort.

Evidence: `evidence/2026-09-11-mcp-heartbeat-lifecycle/`. Handoff: `handoffs/2026-09-11_1635_mcp-heartbeat-lifecycle.md`.

Review outcome: the user supplied `APPROVED_WITH_NOTES` for exact reviewed commit `24cd1f75483fd7a958dd30a7eec5358c0de975b4`. Notes are accepted and non-blocking: TTL is global rather than heartbeat-scoped, the five-hour validation is bounded, and an upstream run-end cleanup remains preferable. Review preserved in `reviews/2026-09-11_1640_mcp-heartbeat-lifecycle.md`. This closure changes ledger and PR metadata only; no runtime action was taken.

Closure commit: current PR #1 HEAD, resolved after push. The PR metadata must identify the fixed reviewed commit above separately from the later closure commit.

Prior task preserved: `handoffs/2026-09-10_0812_scout-v41-flash.md` and `evidence/2026-09-10-scout-v41/` remain unchanged with their pending review history.
