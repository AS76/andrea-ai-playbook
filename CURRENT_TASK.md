# CURRENT TASK

## Request

Fix the degraded OpenClaw runtime observed on 2026-09-03.

## Objective

Restore reliable gateway operation while preserving model, OAuth, Telegram,
ClawMem and security configuration.

## Scope

- OpenClaw gateway runtime and provider-auth snapshot path
- Official plugin version alignment
- Telegram, local health and Tailscale Funnel verification
- Reversible production remediation and rollback evidence

## Out of Scope

- `openclaw doctor --fix`
- OpenClaw core package update or downgrade
- Model or authentication-route changes
- Broad configuration rewrites

## Initial State

- OpenClaw 2026.9.1 was active but repeatedly blocked for 83–111 seconds.
- Startup readiness took about 120 seconds after the HTTP listener appeared.
- Runtime logs showed event-loop starvation, Telegram fetch timeouts and WS 1006.
- Eight active official plugins remained at 2026.8.2.

## Root Cause

A CPU profile identified repeated `stableConfigStringify()` work from
`providerConfigMatchesRuntimeSnapshot()`. The large configured OpenRouter model
catalog was re-normalized and hashed for repeated auth/provider comparisons,
causing excessive garbage collection and blocking the Node event loop.

## Remediation

- Aligned eight active official plugins to 2026.9.1 without capability bypass.
- Added a process-local cache keyed by input/runtime config object identity and
  provider id around the expensive provider snapshot comparison.
- Removed stale Funnel routes targeting inactive local port 8787.
- Kept `/root/.openclaw/openclaw.json` byte-identical.

## Verification

- [x] Core syntax validation
- [x] Final cold-start readiness: 28.7 seconds
- [x] No delayed heartbeat, starvation, freeze or WS 1006 in final gates
- [x] Scout synthetic turn: `HEALTH_OK`, 16.3 seconds
- [x] All 11 Telegram accounts: configured, running, connected, works
- [x] Cleo real Telegram delivery: `OPENCLAW_FIX_OK`
- [x] Gateway, ClawMem and Funnel root: HTTP 200
- [x] 35 continuous probes: zero failures, maximum 234 ms
- [x] Inspector diagnostic override removed; no port 9229 listener

## Rollback

Restore the backed-up provider-auth module and plugin project artifacts from
`/root/.openclaw/backups/plugin-alignment-20260903T203900Z`, restore the saved
Funnel JSON mapping if the obsolete routes are intentionally needed, then
restart the gateway. Configuration backup SHA-256 matches the live file.

## Execution Status

- [x] Initial audit
- [x] Root-cause diagnosis
- [x] Backup and remediation
- [x] Runtime verification
- [x] Handoff prepared
- [ ] ChatGPT review
- [ ] Final closure

## Blockers / Decisions

None. The local core hotfix will be overwritten by a future package update and
must be retired when upstream ships an equivalent fix.
