# Jev disable, controlled observation, and plugin inventory — 2026-09-18

Status: **PARTIAL / DEGRADED**. The planned health window and both real cron runs completed; agent-load event-loop stability remains unproven.

## Ledger reconciliation before production change

- PR #3's prior body described the Gateway as stopped and Jev as unchanged despite later published runtime evidence. Its branch was also behind four commits on its PR #1 ledger base.
- Merged `origin/codex/handoff-ledger` into the incident branch without rewriting historical commits. Preserved the base's forensic evidence and the incident's timestamped handoffs. Updated `STATUS.md`, `CURRENT_TASK.md`, PR title/body, and verified `MERGEABLE/CLEAN` with local, remote, and PR heads matching at reconciliation commit `f7c79c6d4141cbe3d114dc901365d7ef7c314188`.

## Production change and rollback

- Pre-change OpenClaw config SHA-256: `478aa15c727ba84d9a777ee88aa98e9e010c69b6305890e16bd492ac75114a58`. Streamed `openclaw.json` encrypted directly to S3 object `openclaw/rollback/2026-09-18-jev-disable-prechange-1145UTC.tar.gpg`; producer/encryption succeeded and full remote SHA-256 readback matched `9f5ee95a7c8fd4d00026677d22914d9aa74b8e7278a1f02b9463293daa0edd4c`. No local backup archive. Decrypt/restore was not exercised.
- Changed exactly `plugins.entries.jev-decision-gate.enabled` from `true` to `false`. Config validation passed. The plugin files remained installed; `openclaw plugins list --json` now reports `enabled=false`, `status=disabled` and the same plugin root.
- Executed one `systemctl --user restart openclaw-gateway.service` at 11:45 UTC. MainPID changed from `420209` to `457327`; `NRestarts=0`. No other restart, Doctor fix, updater, auth, provider, or unrelated plugin mutation was performed.

## Runtime checks so far

- Gateway reached `ready`; the live listener and RPC returned. Jev was absent from the 16 live loaded plugins, and live plugin errors were empty. Eight enabled Telegram accounts reached `connected=true` and passed bot probes. Startup CPU degradation cleared.
- The existing `icloud-findmy-scraper` cron ran at 11:49:54 UTC and completed `ok` at 11:49:59 UTC. Health samples before, during, and after it passed without event-loop degradation.
- A Gateway-routed Cleo turn produced `E2E-OK-1150`, and the live Telegram transport logged `outbound send ok` to the established Andrea chat with message ID `64439`. A prior plain test message was accepted as message ID `64438`.
- True Telegram inbound→agent→outbound was then observed twice. The polling worker received fresh update IDs `503142623` and `503142624`; Cleo's direct Telegram session gained corresponding user and assistant turns; the transport logged replies as message IDs `64441` and `64443` to the same chat. Andrea confirmed receiving the return message. This is **PASS** for the Telegram E2E transport/delivery path. The user supplied short markers rather than the full requested instruction, so exact-output instruction compliance was not measured.
- The 15-second health monitor ran from 11:48:12 through 12:05:57 UTC: **72/72 RPCs passed**, with no timeouts, Jev loads, or live plugin errors. Three samples reported transient event-loop degradation at 11:53:58, 12:01:43, and 12:05:43 (`delayP99Ms=1414.5`, `747.6`, and `902.8`); the next sample recovered each time. The first two coincided with Telegram/Cleo traffic; the third occurred during the Scout agent cron. This does not establish Jev as the cause of earlier Gateway timeouts or prove sustained event-loop stability under agent load.
- The real `sync-refresh-batch` Scout agent cron began at 12:04:24 UTC and completed `ok`/`succeeded` after 290,528 ms, versus its preceding ~20–29 second runs. RPCs passed during monitor overlap. The journal recorded repeated model requests and slow SQLite lifecycle/reclamation operations. A post-completion RPC passed with event-loop `degraded=false`, `delayP99Ms=22.2`; Gateway stayed active with PID `457327` and `NRestarts=0`. The unusually long run and transient degradation still need causal investigation.

## Plugin inventory (live evidence, not just persisted registry labels)

| Classification | Components | Evidence and limit |
| --- | --- | --- |
| Healthy load/registration | `anthropic`, `brave`, `clawmem`, `codex`, `context-lifecycle-guard`, `device-pair`, `elevenlabs`, `lobster`, `openai`, `orchestration-observer`, `secrets-vault`, `skill-hub`, `slack`, `telegram`, `time-inject` | Present in live `health.plugins.loaded`, no plugin error. This proves load/registration, not every feature; Slack channel is unconfigured. Telegram transport probes pass. |
| Degraded | `context-vault` | Live loaded, but `before_prompt_build` typed hook was blocked on startup. Its principal prompt injection behavior is not verified. |
| Unavailable | `composio` | Live health says `configured-unavailable`, reason `missing-openclaw-peer-link`; its local peer link resolves to the global npm OpenClaw instead of the isolated service package. Persisted `plugins list` says `loaded`, which is weaker than live health. |
| Disabled, retained | `jev-decision-gate` | Config and persisted registry say disabled; plugin root still exists; absent from live loaded list. |

The persisted registry discovers 81 plugins (`48 loaded`, `33 disabled` in the CLI view), including provider catalog entries that were not all activated by this Gateway. It cannot by itself establish live health. No plugin was uninstalled.

## MCP services and other warnings (separate from plugin inventory)

- `idrivee2`: read-only `openclaw mcp probe idrivee2 --json` returned zero tools and `requires OAuth authorization`. This is **unavailable** as an MCP server. No login or token/config change was attempted.
- `showly`: a prior agent-start log showed `tools/list` timeout after 1500 ms; a fresh read-only probe returned 33 tools and no diagnostic. This is **intermittently degraded**, not proven unavailable. No timeout change was made.
- Captured `models.json` reported an OpenRouter `apiKey` schema warning, while the controlled Cleo model turn succeeded. Two Skill Workshop legacy backup roots remain preserved for manual owner review. Neither is a plugin repair in this task.

## Specific GitHub precedent search before any repair decision

| Local finding | Closest primary-source precedent | Applicability |
| --- | --- | --- |
| Composio wrong host peer link | [OpenClaw issue #107207](https://github.com/openclaw/openclaw/issues/107207) reports the same `missing-openclaw-peer-link` class after an update for WhatsApp; merged [PR #83794](https://github.com/openclaw/openclaw/pull/83794) addresses stale/wrong host peer links for managed npm plugins. | Same failure class, different plugin and host layout. Exact Composio issue not found in GitHub search. No repair applied. |
| Context-vault blocked prompt hook | [OpenClaw issue #137973](https://github.com/openclaw/openclaw/issues/137973) reports a blocked `before_prompt_build` hook in Hindsight; [issue #80114](https://github.com/openclaw/openclaw/issues/80114) distinguishes prompt injection and conversation access gates. | Analogous non-bundled hook policy; no exact issue for this local `context-vault` package found. No permission expansion applied. |
| iDrive e2 OAuth required | [OpenClaw issue #142333](https://github.com/openclaw/openclaw/issues/142333) reports a *different* Notion case where probe succeeds but agent startup rejects a valid OAuth token. | Here the iDrive probe also fails, so that bug is not established. No exact iDrive e2 GitHub issue found. No auth repair applied. |
| Showly 1500 ms tools listing timeout | [OpenClaw issue #137379](https://github.com/openclaw/openclaw/issues/137379) reports the same timeout text with a different large MCP server; it closed `not_planned`. | Our Showly probe passed once with 33 tools; exact Showly GitHub precedent was not found. No timeout/config change applied. |
| Jev local SDK/build mismatch | No `jev-decision-gate` issue found in the OpenClaw repository search. | Local plugin is retained but disabled. No uninstall decision until runtime stability and feature need are evaluated. |

No automatic repair or removal was attempted for Composio, iDrive e2, Showly, context-vault, or other components. The retention decision is **deferred**: keep Jev installed but disabled for rollback; keep currently loaded components and unresolved integrations unchanged while the prolonged Scout cron and event-loop behavior are investigated. No removal has enough stability or dependency evidence yet.

## Acceptance, rollback, and review request

- **TEST_VERIFIED:** one-line config validation; Telegram inbound→Cleo→outbound delivery with user-confirmed receipt; existing command and Scout agent cron completion; 72/72 monitored health RPCs.
- **RUNTIME_VERIFIED:** Gateway remained active after exactly one controlled restart; Jev stayed installed and disabled; 16 other plugins loaded, with no live plugin error. Three monitored event-loop degradations recovered on the next sample.
- **UNVERIFIED:** sustained event-loop stability under agent load, the Scout cron's downstream effects, exact-output Telegram instruction compliance, the root cause of the prior RPC timeouts, and feature-level health of every loaded plugin.
- **Risk:** the Scout cron took roughly ten times its recent duration and produced additional transient event-loop load. Do not treat the environment as fully stable or remove more plugins on this evidence.
- **Rollback:** the verified encrypted S3 pre-change config copy can restore Jev's prior enabled state, followed by config validation and a separately planned restart. Restore and decrypt were not exercised. No rollback is indicated while Gateway RPC and Telegram delivery continue to work.
- **Review request:** assess the narrow Jev disable and the partial runtime acceptance; preserve the open stability question and plugin decision gate. No claim of final incident closure is made.
