# CODEX HANDOFF

## Metadata

Date: 2026-09-03T21:05:00Z
Codex session: openclaw-freeze-remediation
Host: production-vps
Component: OpenClaw gateway and provider-auth runtime snapshot
Codex Status: PASS
Runtime Verification: PASS
ChatGPT Review: PENDING_REVIEW
Current Commit: PR `#1` HEAD (`refs/pull/1/head`)
Reviewed Commit: PR `#1` HEAD (`refs/pull/1/head`)
Branch: `codex/handoff-ledger`
Related task: `CURRENT_TASK.md`
Related issue/PR: GitHub PR `#1`; upstream issue `openclaw/openclaw#136035`
Related ClawMem context: OpenClaw 2026.9.1 freeze remediation
Related review: pending

## Request

Fix the degraded OpenClaw runtime after repeated long event-loop stalls.

## Initial State

The gateway was available but not reliable. The current process showed four
delayed heartbeats, five starvation timeouts, three host-freeze detections and
eleven WS 1006 closures. A clean restart reproduced about two minutes between
HTTP listener and gateway readiness.

## Findings

### FACT

- OpenClaw core was 2026.9.1 while eight active official plugins were 2026.8.2.
- The main OpenClaw config contained 406 OpenRouter model entries.
- A V8 CPU profile attributed the stall primarily to recursive
  `stableConfigStringify()` calls and garbage collection.
- The caller was `providerConfigMatchesRuntimeSnapshot()` in the provider-auth
  path.
- Moving legacy session archives out of the runtime tree did not improve
  readiness; they were restored before the final remediation.

### INFERENCE

- Repeated structural hashing of equivalent provider configurations caused the
  event-loop starvation. Caching the comparison by immutable runtime snapshot
  identities removes repeated hashing while preserving invalidation when a
  runtime config object is replaced.

### TEST_VERIFIED

- The patched module passed Node syntax validation.
- Plugin alignment completed without a forced capability-acceptance flag.
- `/root/.openclaw/openclaw.json` remained byte-identical to its backup.

### RUNTIME_VERIFIED

- Final cold-start readiness: 28.7 seconds.
- No delayed heartbeat, starvation, freeze or WS 1006 appeared in final gates.
- Synthetic Scout turn returned `HEALTH_OK` in 16.3 seconds.
- All 11 Telegram accounts passed the channel probe.
- Cleo delivered `OPENCLAW_FIX_OK` through Telegram.
- Gateway, ClawMem and public Funnel root returned HTTP 200.
- A 35-sample continuous probe had zero failures and maximum latency 234 ms.

## Actions Performed

- Backed up configuration, npm locks, plugin directories and the original core
  module under `/root/.openclaw/backups/plugin-alignment-20260903T203900Z`.
- Aligned Brave, DeepSeek, Lobster, Mistral, Moonshot, Perplexity, Slack and
  Voyage official plugins to 2026.9.1.
- Added provider snapshot comparison memoization in
  `/usr/lib/node_modules/openclaw/dist/model-auth-provider-config-6b_JxQon.js`.
- Removed the temporary loopback-only Node inspector override after profiling.
- Removed stale Funnel routes to inactive port 8787.

## Configuration Changes

The OpenClaw JSON configuration and model/OAuth routes were not changed. Plugin
installation metadata changed outside the JSON config. Tailscale Funnel now
publishes only the working root route to local gateway port 18789.

## Risks

- The local core patch will be overwritten by a later OpenClaw package update.
- The memoization assumption depends on runtime/source config replacement rather
  than in-place mutation, matching the runtime snapshot module's lifecycle.
- The removed Funnel routes must remain absent unless a real service is restored
  on local port 8787.

## Rollback

Restore the backed-up provider-auth module and plugin project artifacts from
`/root/.openclaw/backups/plugin-alignment-20260903T203900Z`, optionally restore
the saved Funnel mapping, and restart the user gateway service. The saved and
live OpenClaw JSON hashes matched after remediation.

## Remaining Work

Independent review and upstreaming of the provider comparison cache.

## Recommended Next Action

Review the root-cause evidence, cache invalidation safety, runtime gates and
rollback completeness.

## ChatGPT Review Request

Review requested: YES
Review scope: root cause, cache correctness, runtime evidence, rollback and local-patch lifecycle
Reviewed commit: PR `#1` HEAD (`refs/pull/1/head`)
Evidence requiring review: current task, change record and this handoff
