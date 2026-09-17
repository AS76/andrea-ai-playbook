# CODEX HANDOFF

## Metadata

Date: 2026-09-06T04:54:00Z
Host: production-vps
Component: OpenClaw 2026.9.2 update recovery and Gateway
Codex Status: PARTIAL
Runtime Verification: PASS_WITH_WARNINGS
ChatGPT Review: PENDING_REVIEW
Current Commit: PR `#1` HEAD (`refs/pull/1/head`)
Reviewed Commit: PR `#1` HEAD (`refs/pull/1/head`)
Branch: `codex/handoff-ledger`
Related task: `CURRENT_TASK.md`
Related issue/PR: upstream openclaw/openclaw#136035; ledger PR #1

## Request and initial state

Finish the interrupted update, check coherence, restart and health-check.
Core 2026.9.2 (3928bad) was already installed; service inactive, listener absent,
and original updater plus parent suspended on their terminal by SIGTTOU.

## FACT

- Configuration differences versus pre-update copy were restricted to three metadata fields: meta.lastTouchedVersion, wizard.lastRunAt and wizard.lastRunVersion.
- Recovery itself left openclaw.json byte-identical, including all agent/model/auth routes.
- Native startup refreshed the stale Codex plugin to 2026.9.2 and deliberately exited for migration convergence; systemd restarted it once.
- The following unpatched generation remained pre-ready for roughly five minutes, with ~98% sampled CPU, Recv-Q reaching 10, RPC timeouts and 3/3 HTTP timeouts.
- New distribution again contained uncached structural hashing in providerConfigMatchesRuntimeSnapshot. Prior mitigation and V8 root-cause evidence are preserved in the 2026-09-03 handoff.
- A new strace summary showed heavy mapping/allocation syscalls. A new V8 profile could not be obtained: SIGUSR1 did not make an inspector available on the unresponsive process. This turn does not claim new CPU-stack attribution.

## INFERENCE

Loss of the previous provider-comparison mitigation caused or materially contributed to the renewed startup stall. Source inspection and before/after runtime behavior support this; no controlled repeated A/B experiment or fresh V8 profile was obtained.

## Actions and changes

1. Protected backup under `/root/.openclaw/update-runs/recovery-20260906T044546Z` containing config/pre-update/last-good copies and service definition.
2. Confirmed identities and stopped state, then TERM+CONT terminated the exact two suspended updater PIDs. The original updater did not finish with a successful exit; recovery completed the operational installation/startup manually.
3. Started the user Gateway service and observed its automatic Codex plugin convergence.
4. Tightened existing service `.bak` permissions from 0644 to 0600; final service config audit passes. Service content was not changed.
5. Backed up original 2026.9.2 `model-auth-provider-config-C_kr_q2g.js`, then applied the attached narrow cache patch. Results are keyed by input/runtime config identity and provider; published snapshot metadata identity resets the whole cache. Identical provider objects avoid hashing.
6. Requested service stop; the unresponsive main process did not complete SIGTERM, so issued SIGKILL to that service main process and started the service. No ready/serving agent activity was observed in that stuck generation.
7. Ran final runtime checks without sending a new external message.

## Tests and runtime evidence

- Node syntax check PASS.
- Attached isolated behavioral test PASS: missing providers, equivalent snapshots, same identity, 1000 repeated cache hits, changed input/runtime identity, publication invalidation, reset and 100 reference comparisons with 406-model fixtures.
- Patched generation started 04:51:38 UTC and declared ready 04:52:23.169 UTC (45.2 seconds). Final NRestarts=0.
- Initial probes during startup had three timeouts; these are preserved locally and excluded explicitly from the post-ready window.
- Final authenticated operator.read RPC PASS, server version/build 2026.9.2.
- 11/11 configured Telegram accounts running/connected/polling, probe.ok=true, no lastError.
- Existing production Cleo outbound delivery was observed at 04:52:44 UTC. This is passive journal evidence, not a newly initiated synthetic end-to-end test.
- Post-ready HTTP 20/20 status 200, max 32 ms. Public Gateway HTTP 200. Listener restricted to loopback with Recv-Q=0.
- Final sampled CPU about 3-4%; RSS about 1.44 GiB. No new inspector listener or override remains.
- Doctor exited 0 but its earlier health check timed out during startup; exit zero is not represented as healthy. Doctor lint exited 1 with the findings below.
- Config validate PASS. Service config audit PASS after permission tightening.

## Residual findings and limits

- Lint ERROR: Max TOOLS.md is an existing symlink, blocking automatic TOOLS-to-AGENTS migration. Preserved rather than invoking blanket repair.
- Lint WARNING: Lex maxOutputTokens cannot be migrated to native Codex transport automatically. Preserved authored behavior.
- Disabled active-memory/memory-core residual configuration warnings remain.
- Existing conversation-hook and escaped-skill access restrictions remain enforced.
- Eight official external plugins remain explicitly pinned at 2026.9.1 and loaded without registry diagnostics; Codex is now 2026.9.2. Dry-run confirms pins; no broad or forced-capability update was performed. Version uniformity is not claimed.
- Slack is enabled but unconfigured; it is excluded from configured Telegram health acceptance.
- One EPIPE to an old connection appeared immediately after ready; no later sustained heartbeat/starvation/freeze warning was found in the observed final window.
- Cache correctness assumes input configuration objects are not mutated in place within a published snapshot revision. New snapshot publication resets the cache, including publication reusing a config object. Long-duration stability and every model provider are not proven.

## Rollback

Original module is stored in the protected recovery directory with suffix `.original`.
Restore that file to its documented distribution path and restart the user Gateway to remove the mitigation (the unpatched stall may recur).
Config and service copies are available there; no config restore is currently required.
The automated Codex plugin migration used retained npm generations; a package/plugin downgrade was not tested and is not claimed as a verified rollback.
Do not restore the unsafe backup-file permission merely to match previous state.

## Review request

Review the cache's auth-sensitive equivalence semantics and invalidation assumptions, recovery boundaries, accurate separation of observed and inferred causality, preserved lint findings, and the local-patch lifecycle risk. Current PR head is the review target; previous reviews are preserved.
