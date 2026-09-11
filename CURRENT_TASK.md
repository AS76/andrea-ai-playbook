# CURRENT TASK

Request: apply one supported minimal lifecycle correction for MCP runtimes created by isolated Cleo heartbeats, then validate it across one natural heartbeat with a detached observer.
Overall status: REVIEW_REQUIRED
ChatGPT Review: PENDING_REVIEW
Engineering acceptance: RUNTIME_VERIFIED

Confirmed initial state: Cleo's 30-minute isolated heartbeat creates a fresh session-scoped three-server MCP cohort; completed cohorts remain because `mcp.sessionIdleTtlMs` is absent and resolves to zero. `memory-probe.sh` remains suspended.

Authorized scope: first determine whether run-end MCP cleanup is supported and heartbeat-scoped. Use it only if supported; otherwise configure only `mcp.sessionIdleTtlMs = 900000`. Stream and verify an encrypted rollback directly to established S3 before mutation. Do not patch source, alter heartbeat cadence, re-enable memory-probe, change models, or add secondary hardening.

Result: installed 2026.9.3 exposes `cleanupBundleMcpOnRunEnd` only as an internal run parameter, not as a supported heartbeat-scoped configuration option. Applied only `mcp.sessionIdleTtlMs = 900000` after a verified encrypted S3 rollback. One controlled Gateway restart loaded the setting. A detached observer captured one natural heartbeat, its three local MCP runtime groups, and complete reclamation at 11:54:21 UTC after the configured TTL. The Gateway PID remained unchanged, OOM counters stayed zero, and ten consecutive isolated heartbeats completed with fresh session IDs without leaving a retained cohort.

Evidence: `evidence/2026-09-11-mcp-heartbeat-lifecycle/`. Handoff: `handoffs/2026-09-11_1635_mcp-heartbeat-lifecycle.md`. Independent review remains required; no additional hardening was applied.

Prior task preserved: `handoffs/2026-09-10_0812_scout-v41-flash.md` and `evidence/2026-09-10-scout-v41/` remain unchanged with their pending review history.
