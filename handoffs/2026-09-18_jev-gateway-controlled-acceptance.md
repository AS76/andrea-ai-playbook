# Jev repair and controlled Gateway acceptance — 2026-09-18

Status: **RUNTIME_VERIFIED for the scoped Jev load and Gateway recovery; PARTIAL for full channel delivery.** Review required.

## FACT — checkpoint and protection

- The previous session ended with the Gateway stopped, the original updater still owning its triage child, and an isolated Jev candidate. This independent session found no original updater or triage process. `openclaw update status --json` showed the latest repair run `finished/succeeded`; the shared SQLite update ledger had zero `running` rows.
- Before mutation, deployed Jev source and build hashes matched the prior handoff. The prior encrypted S3 rollback object `openclaw/rollback/2026-09-18-jev-decision-gate-prepatch-1055UTC.tar.gpg` had passed full remote SHA-256 readback (`77ca74f73d31ead59455a5ff90fc21c1591e4e6b7254c7cf96996821ffc9cfd8`). No local backup archive was made. Restore/decryption remains untested.
- The Gateway was inactive/dead, `MainPID=0`; port 18789 was free. Config SHA-256 matched the documented pre-update copy (`478aa15c727ba84d9a777ee88aa98e9e010c69b6305890e16bd492ac75114a58`). Read-only SQLite `quick_check` returned `ok` for the shared state and 13 agent stores.

## FACT — narrow repair and tests

- In `/root/.openclaw/workspace/main/plugins/jev-decision-gate/src/index.ts`, made telemetry `ts` optional at call sites while `logTelemetry` writes the current timestamp last, and removed the unsupported `allowConversationAccess` option from the `before_agent_finalize` hook registration. No feature flags, OpenClaw core files, config, database schema, service files, or other plugins were deliberately changed.
- `npm run build` passed against the plugin's pinned 2026.9.4 SDK. Generated `dist/index.js` SHA-256 is `4dc942973c254d27eed989afc2b4cbb2e21b04a00e3f8a10acbffc44681197e2`, byte identical to the isolated candidate. A direct Node import/registration check found all four hooks, supported finalize options, and `undefined` responses from all four disabled hooks.
- The existing `test/unit.test.ts` targets an older API and was not used as passing behavioral evidence. Jev behavioral guards remain disabled by their current defaults; active guard decisions were not tested.

## FACT — live acceptance

- Started `openclaw-gateway.service` through its existing systemd user unit. The unit stayed `active/running` on one MainPID with `NRestarts=0`. Loopback port 18789 listened with `Recv-Q=0`. `openclaw gateway status --deep` reported CLI/Gateway version 2026.9.4 and a successful connectivity probe.
- The live Gateway logged Jev registration with `enabled=false, completion=false, progress=false`; `openclaw health --json` listed `jev-decision-gate` among loaded plugins and had no plugin errors. The plugin's own version probe reported `runtime=unknown`, a warning that limits its version self-check; the Gateway runtime itself reported 2026.9.4.
- Startup briefly timed out and reported event-loop degradation during initialization. Subsequent and sustained RPC health reported `ok=true`, `eventLoop.degraded=false`, no liveness reasons, and no service restart. A Gateway-routed Cleo turn in an isolated acceptance session returned exactly `GATEWAY_ACCEPTANCE_OK`; its terminal receipt showed requested route `openrouter/auto`, effective OpenRouter response model `z-ai/glm-5.3-flash`, with no fallback attempt. No Telegram delivery was requested.
- `openclaw channels status --probe --json` returned successful Telegram bot probes. All configured enabled Telegram accounts reached `connected=true`, `lifecycle=ready`; disabled accounts remained disabled. Post-start config hash still matched the pre-update copy, and all 14 SQLite read-only quick checks remained `ok`.

## Remaining limits and warnings

- Telegram transport/probe and an agent reply passed, but a new end-to-end inbound Telegram message and delivered reply were not observed. Full delivery acceptance is **UNVERIFIED**.
- Startup logged an automatic repair of 12 managed npm plugin peer links and a Composio peer-link warning; live health lists Composio `configured-unavailable`. It also logged a blocked `context-vault` `before_prompt_build` hook, a captured `models.json` OpenRouter `apiKey` schema warning, and `idrivee2` OAuth / `showly` tool-listing errors. These were not changed under this Jev repair and require separate investigation before claiming every capability healthy.
- Startup reported preserved Skill Workshop backup roots without configured owners. No Doctor fix was invoked in this session. The original update repair's separate Doctor pass is documented in the earlier handoff.
- Draft PR #3 is based on the PR #1 ledger branch and remains conflicting with newer PR #1 commits. Do not rewrite the historical review branch until the base lineage is decided.

## Rollback and review request

The encrypted S3 object above contains the prior plugin source, build, manifest, and test. If Jev load regresses, stop the Gateway through its user service, restore only that plugin from the verified object after a controlled decrypt/restore rehearsal, and repeat runtime acceptance. Review the scoped repair, exact runtime evidence, and the PARTIAL delivery classification. ChatGPT review is evidence review, not a substitute for a live Telegram exchange.
