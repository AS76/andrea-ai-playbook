# CODEX HANDOFF

## Metadata

Date: 2026-09-11
Host: production VPS
Component: OpenClaw MCP session runtime lifecycle
Codex Status: PASS
Runtime Verification: PASS
ChatGPT Review: PENDING_REVIEW
Commit: current PR #1 HEAD, resolved after push
Branch: codex/handoff-ledger
Related issue/PR: openclaw/openclaw#143381; ledger PR #1

## Request

Apply exactly one minimal supported lifecycle correction for MCP runtime cohorts created by isolated Cleo heartbeats, validate one natural heartbeat with a detached observer, and stop without unrelated hardening.

## Initial State

OpenClaw 2026.9.3. Cleo runs an isolated heartbeat every 30 minutes with a fresh session ID. Each heartbeat materialized three local MCP groups during catalog discovery. `mcp.sessionIdleTtlMs` was absent and resolved to zero, so completed heartbeat cohorts remained cached indefinitely. A separate incident-amplifying `memory-probe.sh` cron was already suspended.

## Findings

### FACT

Installed `cleanupBundleMcpOnRunEnd` is an internal run option used by selected one-shot paths. It is absent from the supported configuration schema and cannot be enabled only for Cleo heartbeat without source changes. Installed `mcp.sessionIdleTtlMs` is supported, its sweep skips active leases and pending acquisitions, and a positive value bounds idle session runtimes. Upstream issue #143381 describes the same heartbeat lifecycle gap and recognizes finite TTL as the operator workaround.

### INFERENCE

Heartbeat-scoped run-end disposal remains the preferred upstream product fix because it retires ephemeral ownership immediately. On this installed release, the 15-minute TTL is the smallest supported configuration-only correction that preserves normal session caching while preventing indefinite accumulation.

### UNVERIFIED

An upstream heartbeat cleanup implementation is not yet available or tested on this VPS. Long-term behavior beyond the observed five-hour, ten-heartbeat period remains unproven.

## Actions Performed

Streamed and verified an encrypted rollback directly to S3. Added only `mcp.sessionIdleTtlMs = 900000` to the active configuration. Performed one controlled Gateway restart because reload mode is off. Started one detached transient-systemd observer and allowed one natural heartbeat to occur. No heartbeat was manually triggered and no second lifecycle control was configured.

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `/root/.openclaw/openclaw.json` | Added one property | Set 15-minute MCP session idle TTL |
| Ledger status, task, handoff and evidence | Updated/added | Sanitized audit and review evidence |

## Configuration Changes

```diff
 "mcp": {
+  "sessionIdleTtlMs": 900000,
   "servers": {
```

No heartbeat cadence, agent, provider, MCP server, source, circuit breaker, watchdog, or memory-probe configuration changed.

## Tests Executed

| Test | Result | Evidence |
|---|---|---|
| Encrypted S3 rollback full readback | PASS | `backup.json` |
| Installed schema/source acceptance | PASS | `config-change.md` |
| Gateway restart and health | PASS | `config-change.md` |
| One natural heartbeat completion | PASS | `runtime-validation.md` |
| Three-group cohort creation and ancestry | PASS | `runtime-validation.md` |
| TTL reclamation after idle period | PASS | `runtime-validation.md` |
| Gateway PID stable and OOM counters zero | PASS | `runtime-validation.md` |
| Ten consecutive later heartbeat sessions | PASS | `runtime-validation.md` |
| `memory-probe.sh` remains suspended | PASS | Disabled cron marker inspected after validation |

## Runtime Verification

The observed heartbeat ran from 11:39:17.651 to 11:39:35.825 UTC under session ID `50fae64e-39a9-4c9d-a8a0-e9daa1a9a151`. It created three relay/anchor/server groups. The entire nine-process cohort disappeared at 11:54:21.455 UTC and remained absent for the observer's 30-second confirmation interval. Gateway processes returned 14 to 2, tasks 76 to 24, and cgroup memory 2228.820 to 1700.375 MiB. Swap fell from 411 to 390 MiB; no OOM counter incremented. The same Gateway PID remained active through the later safety check, ten consecutive heartbeat sessions completed, and no cohort remained.

## Risks

TTL is global to OpenClaw session MCP runtimes, not heartbeat-scoped. A runtime idle for 15 minutes can be retired and recreated later; active leases and pending acquisitions are explicitly protected by installed code. The continuing `idrivee2` OAuth warning and a 12:09 initialization timeout burst are pre-existing/out-of-scope observations and were not repaired.

## Rollback

Encrypted object: `openclaw-rollbacks/2026-09-11/mcp-session-idle-ttl/openclaw-json-before-20260911T110720Z.tar.gz.gpg`. Full remote SHA-256 readback passed with digest `af8bbb32e1ea5ca9ef083bd713dd6c9b6c77dd00930e502b8c0dba0da770e43b`. A minimal rollback removes only `mcp.sessionIdleTtlMs`, validates configuration, and performs one controlled Gateway restart. Any future rollback operation requires fresh explicit authorization.

## Remaining Work

Independent review only. Do not add heartbeat cleanup, change the TTL, or apply any additional hardening as part of this task. A separate finite TTL is already the remediation; if a supported heartbeat-scoped run-end cleanup becomes available later, reassess whether TTL should remain as defense-in-depth in a separate approved change.

## ChatGPT Review Request

Review the exact current PR head, single-property scope, installed-source safety evidence, direct-to-S3 rollback proof, natural-heartbeat cohort tracking, reclamation timing, and post-validation safety checks.
