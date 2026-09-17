# OpenClaw 2026.9.4 skill-watcher starvation containment

Date: 2026-09-12
Status: REVIEW_REQUIRED / PENDING_REVIEW
Engineering result: RUNTIME_RECOVERED_WITH_CONTAINMENT

## Request

Recover the production OpenClaw Gateway after the 2026.9.4 update path left an updater diagnostic subtree running and the Gateway entered sustained main-thread starvation, became RPC-unreachable, and failed during a timed-out stop.

## Initial verified state

- FACT: isolated OpenClaw 2026.9.4 and service Node 24.21.0 were active installation targets.
- RUNTIME_VERIFIED: the Gateway was failed with no MainPID and no listener on port 18789.
- RUNTIME_VERIFIED: the prior Gateway recorded event-loop utilization near 1, 65-120 second delays, growing accept backlog, and a five-minute stop timeout ending in SIGKILL.
- RUNTIME_VERIFIED: the update, updater wrapper, and embedded diagnostic child remained alive after the supplied report.

## Actions

1. Terminated only the explicitly authorized update/diagnostic subtree with SIGTERM; all target processes exited without SIGKILL.
2. Started the intended user Gateway once and reproduced the fault on a new PID: cumulative CPU approached wall time, health timed out, RSS exceeded 1.3 GiB, and accept backlog grew.
3. Created an encrypted direct-to-S3 configuration rollback object. The streaming tool reported producer/encryption success, full remote SHA-256 readback, and no local archive.
4. A/B test 1 disabled only `skill-hub`; the fault reproduced. Restored the plugin. This rules out SkillHub as the primary cause.
5. A/B test 2 set the documented core setting `skills.load.watch=false`; restarted the already-starved process through systemd and retained SkillHub enabled.

## Causal evidence

- SOURCE_VERIFIED: the 2026.9.4 loader includes a configuration fingerprint based on stable serialization and SHA-256, plus a synchronous skill discovery/cache path keyed by skill snapshot version.
- TEST_VERIFIED: local isolated microbenchmark measured 100 fingerprint calls at about 48 ms for the same config object versus about 2008 ms for cloned config objects.
- RUNTIME_VERIFIED: baseline and SkillHub-disabled runs continued accumulating CPU toward one full core and timed out health calls.
- RUNTIME_VERIFIED: with only the core watcher disabled, the initial scan completed and cumulative CPU then increased by about four seconds over 95 seconds instead of tracking wall time. Listener backlog remained zero.
- INFERENCE: the 2026.9.4 core watcher/snapshot invalidation path repeatedly invalidated expensive multi-workspace skill snapshots. The exact upstream function producing every invalidation was not instrumented, so this is a causally isolated containment rather than a source-level upstream fix.

## Acceptance

- CONFIG_VERIFIED: JSON parses; relative to the pre-update snapshot, the only changed JSON path is `/skills/load`.
- RUNTIME_VERIFIED: Gateway PID 60844 active/running on OpenClaw 2026.9.4 and Node 24.21.0.
- RUNTIME_VERIFIED: health completed in 29 ms; event loop not degraded, utilization 0.04, P99 delay 23.2 ms, CPU-core ratio 0.041.
- RUNTIME_VERIFIED: listener backlog zero; `status --all` reported the Gateway reachable and 11/11 Telegram accounts OK.
- RUNTIME_VERIFIED: telemetry recorded one inbound message, one processed turn, and a completed Telegram delivery during the recovered generation.
- RUNTIME_VERIFIED: all expected plugins loaded without plugin errors; SkillHub remained enabled.

## Residual risk and excluded work

- Automatic skill-directory watching is disabled. Skill changes require an explicit Gateway restart or another supported manual refresh until upstream fixes the invalidation behavior.
- `doctor --fix` was not run. The reported startup-migration, context-vault capability, service PATH, and KillMode findings remain separate review items and were not necessary for recovery.
- No model routing, database, session, capability, unit, package, or plugin-permission change was made.

## Rollback

Remove `skills.load.watch=false` (or restore the verified S3 configuration object) and restart the Gateway. Rollback is expected to restore the starvation condition on 2026.9.4, so it should only be used after an upstream fix or during a bounded diagnostic test.

## Review request

Confirm that the A/B evidence supports the core skill watcher as the containment boundary, that retaining `watch=false` is proportionate, and that unrelated Doctor/service/capability findings correctly remain outside this incident change.
