# OpenClaw gateway freeze remediation

Date: 2026-09-03
Component: OpenClaw 2026.9.1 gateway
Status: REVIEW_REQUIRED

## Change

Added a process-local memoization layer to the provider runtime-snapshot match
path. Results are cached by input config identity, runtime config identity and
provider id. Runtime config replacement naturally creates a new identity and
therefore cannot reuse results from the previous snapshot.

Eight official external plugins were aligned from 2026.8.2 to 2026.9.1 without
forcing capability consent. The main OpenClaw configuration remained
byte-identical. Stale Tailscale Funnel routes to inactive local port 8787 were
removed, leaving the working root route to the gateway.

## Evidence

- CPU profile: dominant samples were `stableConfigStringify` called by
  `providerConfigMatchesRuntimeSnapshot`, with heavy garbage collection.
- Before: listener-to-ready about 120 seconds; heartbeat delay up to 111 seconds.
- After: cold-start readiness 28.7 seconds with no delayed heartbeat.
- Synthetic Scout turn returned `HEALTH_OK` in 16.3 seconds.
- All configured Telegram accounts passed channel probe and Cleo delivered the
  explicit `OPENCLAW_FIX_OK` acceptance message.
- 35 continuous local probes had zero failures and maximum latency 234 ms.

## Risk and lifecycle

This is a local patch to installed OpenClaw distribution code and will be
overwritten by package replacement. Retire it when upstream includes an
equivalent provider-comparison cache. No credential, model route or OAuth state
was changed.

## Rollback

The original module, configuration, npm lock files and plugin project archive
are stored under the timestamped local backup directory documented in the
handoff. Restore the original provider-auth module and restart the gateway.
