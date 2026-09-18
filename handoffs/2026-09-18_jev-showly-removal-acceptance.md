# Jev plugin and Showly MCP removal — 2026-09-18

Status: **PARTIAL / DEGRADED**. Both removals and the bounded Gateway acceptance passed; Scout runtime remains above its historical range and unrelated pre-existing integrations remain degraded.

## Scope and baseline

- Andrea explicitly authorized removal of `jev-decision-gate` and `showly` only. Prior handoffs, including `2026-09-18_jev-disable-observation-plugin-inventory.md`, remain historical evidence.
- PR #3 was open, ready for review, `mergeable_state=clean` at head `78b124dc9f9b6cbacca1a30fce72e76b174a7934` before this continuation. OpenClaw CLI and Gateway were version `2026.9.4`.
- Before change, Gateway was active at PID `457327`, `NRestarts=0`, health RPC passed, Jev was disabled but discovered from a configured local path, and Showly was listed among eight MCP servers as remote streamable HTTP. The previous Scout run had succeeded in 290,528 ms, compared with preceding ~20–29 second runs; prior acceptance was `PARTIAL / DEGRADED`.
- Read-only SQLite `PRAGMA quick_check` returned `ok` for `state/openclaw.sqlite`, `state/cron.db`, and `state/sessions.db`. Config validation passed with two pre-existing disabled-memory-plugin warnings. No active update, Doctor, or repair process was observed; no new updater transaction was found.

## Upstream precedents and supported removal path

- [OpenClaw issue #127392](https://github.com/openclaw/openclaw/issues/127392), open, describes plugin uninstall deleting managed bytes before durable ownership removal; [merged PR #140322](https://github.com/openclaw/openclaw/pull/140322) shares CLI/management uninstall ownership but does not eliminate that reported failure window.
- The installed `openclaw plugins uninstall jev-decision-gate --dry-run --force` refused with `no authoritative package-owner metadata`. Live plugin inventory identified Jev's origin as `config`, source under `workspace/main/plugins/jev-decision-gate`, and `plugins.installs` had no Jev entry. No managed uninstall was forced and no Doctor repair was run. The bounded config-origin removal therefore removed its explicit allowlist, load path and entry, then moved only its local plugin directory out of the active path.
- The installed CLI offers `openclaw mcp unset <name>`; its source routes through a per-server lifecycle lease and canonical MCP config mutation. `openclaw mcp unset showly` removed the single server registration. Showly had no local installation artifact; its transport was remote HTTP.
- Focused OpenClaw GitHub issue/PR searches for `mcp unset`, server removal, and stale MCP config found no direct defect governing this Showly removal. The installed 2026.9.4 CLI and its source were used as the authority for this operation.
- A new exact `jev-decision-gate` search found [OpenClaw issue #151690](https://github.com/openclaw/openclaw/issues/151690), a closed feature proposal for optional Jev/OpenJev support, with no removal procedure. No exact Showly issue was found; [issue #137379](https://github.com/openclaw/openclaw/issues/137379) concerns the same 1500 ms `tools/list` timeout for a different MCP server. No new issue was opened.

## Rollback and exact changes

- Before mutation, streamed only `openclaw.json` and the Jev plugin directory directly to encrypted S3 object `openclaw/rollback/2026-09-18-jev-showly-pre-removal-1235UTC.tar.gpg`. Producer and encryption succeeded; full remote readback matched SHA-256 `cedd070f950bad579e7a02215f4bfe8329428bead5d08c3387f0c3ed456ebe64` (129,179,179 encrypted bytes). No plaintext archive was created. Decrypt/restore was not exercised.
- `mcp unset showly` removed only `mcp.servers.showly`. Removed only `jev-decision-gate` from `plugins.allow`, `plugins.load.paths`, and `plugins.entries`. A semantic comparison against the pre-change config confirmed exactly those four changes. Removed the CLI-created plaintext auto-backup immediately after comparison because the encrypted S3 rollback copy is authoritative.
- Moved the untracked, config-origin Jev directory from the active workspace plugin path to the user Trash, verified its exact Trash metadata, then purged only that directory and metadata after the S3 rollback passed. It is absent from both the active path and `openclaw plugins list --json`; no local Jev Trash copy remains. No other plugin, MCP server, routing entry, model, auth, cron, service definition, or database schema was changed.
- `gateway.reload.mode=off` required a restart to apply both removals. Executed exactly one `systemctl --user restart openclaw-gateway.service` at 12:37:52 UTC. New PID `494575`, `NRestarts=0`. Initial startup had one RPC timeout before Gateway logged `ready` at 12:39:41 UTC; a later RPC passed.

## Acceptance evidence

- **CONFIG:** `openclaw config validate` passed with the same two unrelated warnings. Jev was absent from configured allowlist, load paths, entry, and `plugins list`; Showly was absent from `mcp.servers` and `openclaw mcp list` (seven other server names retained).
- **GATEWAY:** service active; loopback listener on port 18789; `gateway status --deep` connectivity probe passed. Live health loaded 16 plugins, without Jev or new plugin errors. Pre-existing Composio `missing-openclaw-peer-link` remains unrelated.
- **CHANNELS:** eight enabled Telegram accounts were running with successful bot probes; three previously disabled accounts remained disabled. A fresh inbound Telegram update `503142625` was received and spooled at 12:42:07 UTC; Cleo's bot sent a same-chat outbound reply, message ID `64445`, at 12:42:17 UTC. Andrea confirmed receiving `CLEANUP-OK-1240`. This verifies the real inbound→Cleo→outbound delivery path; the exact inbound text was not captured in the sanitized evidence.
- **SCOUT:** exactly one real existing `sync-refresh-batch` run began at 12:40:53 UTC and completed `ok`/`succeeded` in **78,284 ms**. This is 72.6% shorter than the prior 290,528 ms but still about 2.7–3.9 times the previous ~20–29 second range: **IMPROVED BUT DEGRADED**. No cron logic, cadence, routing, or SQLite setting changed.
- **MODEL / SQLITE OBSERVATION:** a journal window spanning the prior run showed 53 OpenRouter `openrouter/auto` model-fetch starts/responses, eight slow SQLite transaction/reclamation messages, 12 MCP startup errors, and four Showly mentions. The post-removal run window through the Telegram inbound showed 21 corresponding model-fetch starts/responses, zero slow SQLite messages, three MCP startup errors (all `idrivee2`), and zero Showly mentions. These are time-window observations, not causal or per-agent model accounting. SQLite logs did not expose individual operation durations. Read-only `PRAGMA quick_check` remained `ok` for the same three stores after the run.
- **RUNTIME:** a temporary 15-second monitor ran from 12:40:13 through 12:51:58 UTC and terminated automatically after 48 samples. **48/48 health RPCs passed**, with no timeout, event-loop degradation, Jev load, or live plugin error; maximum sampled `delayP99Ms` was 93.7 ms. The Gateway remained PID `494575`, active with `NRestarts=0`. The initial bootstrap RPC timeout occurred before `ready` and before this acceptance window. After restart, the journal contained no Jev or Showly load/startup mention and no new plugin error. It did record five `idrivee2` MCP startup errors, a known unrelated condition.

## Inference and unresolved items

- **FACT:** the post-removal config and CLI inventories no longer contain Jev or Showly; the Jev directory and its Trash copy are absent; the Gateway ran at PID `494575` after exactly one controlled restart and completed the bounded checks above.
- **INFERENCE:** removing Jev and Showly reduces their discovery/startup surface; it does not by itself establish the cause of the prior long Scout run or event-loop spikes.
- Existing context-vault and Composio findings remain outside this removal scope. No unrelated remediation was attempted.
- **Acceptance classification:** `JEV_REMOVAL=PASS`; `SHOWLY_REMOVAL=PASS`; `CONFIG_VALIDATION=PASS`; `GATEWAY_ACCEPTANCE=PASS`; `TELEGRAM_E2E=PASS`; `SCOUT_CRON_RUNTIME=78.284 seconds`; `SCOUT_CRON_COMPARISON=IMPROVED_BUT_DEGRADED`; `EVENT_LOOP_STATUS=STABLE` for the bounded post-ready window; `FINAL_VERDICT=PARTIAL_DEGRADED`.
- **Unresolved:** Scout remains above the prior 20–29 second runtime and a single run cannot attribute improvement to either removal. Historical transient event-loop spikes under other loads are not disproven by this clean window. Composio, iDrive e2 and context-vault remain at their previously documented states; the startup service PATH and disabled-memory-plugin warnings also predated this cleanup. No follow-up repair was attempted here.

## Review request

Review the exact bounded cleanup, rollback evidence, runtime acceptance, and any remaining degradation. Do not infer full incident closure from a successful component removal alone.
