# Assisted OpenClaw 2026.9.3 update and native time

## Metadata

Date: 2026-09-09
Host: production VPS
Component: OpenClaw core, isolated Node runtime, native temporal context
Codex Status: PARTIAL
Runtime Verification: PARTIAL (core RPC and native-time test PASS; known limitations below)
ChatGPT Review: PENDING_REVIEW
Commit: current PR #1 HEAD, exact SHA verified after push
Branch: codex/handoff-ledger
Related issue/PR: as76/andrea-ai-playbook#1
Related ClawMem context: Codex technical diary, 2026-09-09
Related review: prior 2026.9.2 review is historical and does not approve this change
Evidence: ../evidence/2026-09-09-assisted-update/

## Request and resulting behavior

The user requested an assisted update, approved an isolated installation after the existing guarded wrapper was found to invoke bundled doctor repair, then explicitly approved native Europe/Rome time and disabling time-inject. The VPS now runs OpenClaw 2026.9.3 on dedicated Node 24.21.0. Exact time is obtained through session_status; the optional detailed automatic time-inject hook is disabled. Context-vault is assessed separately and has not received new conversation access permission.

## Initial state and findings

FACT: original runtime was OpenClaw 2026.9.2 with Node 22.23.2. Official v2026.9.3 release and local metadata require Node >=24.16.0 on 24.x or >=26.1.0. Node 24.21.0 was downloaded and its official checksum verified in the implementation session.

FACT: the existing safe-update wrapper delegates to bundled update, whose inspected policy enabled doctor --fix. The approved alternative avoids that command. Startup itself nevertheless ran built-in migrations: SQLite schemas, official plugin reconciliation (including Codex), and proven legacy Workshop relocation. No claim is made that startup was side-effect-free.

FACT: upstream provider comparison code passed 15 regression groups including identity, credential mutation, publication/reset lifecycle, and differential canonical comparisons. No old core patch was re-applied. An exact-source guard accepts the inspected build and rejects a deliberately altered manifest. Guard wording PASS_REVIEWED_UPSTREAM_SOURCE denotes local engineering source inspection, not independent ChatGPT approval.

FACT: the resumed checks found native userTimezone absent and host timezone UTC. The installed native functions support calendar date and timezone context, session_status exact time, and heartbeat/cron current-time refresh. Actual-code tests now verify Europe/Rome, local date rollover and replacing stale heartbeat/cron time without duplicate blocks.

FACT: time-inject uses ctx.pluginConfig even though typed hook configuration is on api.pluginConfig. With a synthetic filesystem it ignored useTravelTimezone=false. Context-vault separately reads event.context instead of the supported event.messages; a synthetic standard event produced no saved directive. These tests diagnose code contracts, not real production conversation extraction. Its shared vault path also needs isolation review before prompt-hook reactivation.

## Actions and files changed

- Dedicated installations: /opt/node-v24.21.0-linux-x64 and /opt/openclaw-2026.9.3. Original Node 22 and old OpenClaw package retained.
- CLI points to /root/.openclaw/scripts/openclaw-isolated-cli; service drop-in 50-isolated-runtime.conf selects matching Node/core and the exact-source guard.
- Main configuration changes are exactly agents.defaults.userTimezone=Europe/Rome and plugins.entries.time-inject.enabled=false. The initial core installation left the authored config byte-identical.
- The config CLI unexpectedly normalized six OpenRouter catalog keys and updated metadata. That intermediate file was preserved locally, then the pre-change configuration plus exactly the two approved changes was written before restart. Semantic comparison proves no routing or new hook consent change remains.
- Gateway intentionally restarted once for this authorized configuration change; final generation PID 1987594, no automatic restarts.
- Retained time-inject config causes an expected disabled-plugin warning; retaining it permits reversal without reconstructing settings.

## Tests and runtime evidence

| Check | Result | Evidence |
|---|---|---|
| Candidate provider comparison | PASS, 15 groups | provider-test.log and regression source |
| Exact-source guard | PASS; negative manifest rejected | source-guard-test.log and gate source |
| State backup | PASS: stopped gateway, 10,374,574,080 bytes, required members | backup-verification.json |
| SQLite checks after core activation | PASS, four main and twelve agent DBs | sqlite-after.json; agent-sqlite-after.json |
| Config validation | PASS with disabled-plugin warnings | implementation command output; exact semantic delta in verification-summary.json |
| Native time functions | PASS: configuration, rollover, session_status instruction, refresh | native-time-test.json and actual-import test |
| Local plugin contract probe | Reproduced failures; no production data read | hook-contract-probe.json and probe source |
| Authenticated health after readiness | PASS | verification-summary.json |
| HTTP after readiness | PASS 10/10; max 67.5 ms in this sample | http-native-time-ready.json |
| Cleo runtime test | PASS; returned Europe/Rome 7:26 AM using session_status | sanitized agentTest in verification-summary.json |
| Plugin listing | 46 loaded, 30 disabled, zero load errors; time-inject disabled | verification-summary.json |
| Service and socket | active/running, NRestarts=0, loopback, Recv-Q=0 | verification-summary.json |
| Telegram | 12 running; findmy conflict persists; delivery not tested | verification-summary.json |

The Cleo run used the ordinary configured OpenRouter route, with no fallback. Tool summary records tool_search, session_status and tool_call, zero failures. No Telegram delivery was requested. Its response and tool trace support exact-time access; they are not a full prompt capture proving every temporal rendering path.

The gateway announced ready at 05:26:15.961Z. Earlier startup checks timed out (health RPC after 10 seconds and HTTP after 5 seconds). Those unfavorable results are retained and excluded from steady-state success. Startup responsiveness remains a limitation.

## Upstream startup claims versus observed restart

The [2026.9.3 release notes](https://github.com/openclaw/openclaw/releases/tag/v2026.9.3) announce more responsive startup database/chat-metadata work and lower native hook startup overhead. The specific [startup-stall issue #136035](https://github.com/openclaw/openclaw/issues/136035) remains OPEN, confirmed through GitHub API on 2026-09-09. Its historical diagnostic comment names repeated provider configuration serialization; the installed comparison optimization passes the functional tests included here. Neither this nor the release wording proves elimination of the full startup delay.

Latest local timestamps: process start 05:24:54 UTC, listener 05:25:19.012 UTC, ready 05:26:15.961 UTC: approximately 82 seconds process-to-ready and 57 seconds listener-to-ready. RPC/HTTP probes timed out during that window. No new CPU profile was captured, so the residual blocking owner is NOT PROVEN. This is not a controlled before/after performance benchmark and does not establish causality or a regression relative to another boot.

## Risks and remaining work

- Overall acceptance remains PARTIAL. The user-authorized native-time change is implemented and verified; independent review remains pending.
- context-vault before_prompt_build is still denied by the new conversation gate. Permission alone does not fix its event/config contract issues. Separate compatibility and isolation remediation is required before requesting consent; no time-based retirement conclusion applies to it.
- findmy getUpdates conflict appears in both pre-update health and current logs. A snapshot with no lastError did not prove resolution. No duplicate process was stopped and no Telegram account was reconfigured in this scope.
- Doctor/lint from the core update retain warnings for a pre-existing plaintext secret-bearing config field and two preserved ambiguous legacy Workshop backups. Disabled discord, qwen and whatsapp also emit post-core payload smoke warnings at startup; disabled plugins are not claimed upgraded/accepted.
- Source gating is release-specific. Do not run the old updater against this isolated installation without reviewing installation layout and repair semantics.
- Automatic memory injection provenance remains unsupported in the selected memory runtime; explicit lookup is a separate capability. No memory architecture change was made here.

## Rollback

Native-time-only reversal: preserve any newer config edits, remove userTimezone if it remains this task's Europe/Rome addition, restore time-inject.enabled=true, validate and restart. This restores authored pre-change settings but does not grant conversation access. The precise pre-change config backup is retained locally as openclaw.json.before-native-time-20260909T052419Z.

Core downgrade is not an automatic rollback: SQLite schemas migrated (main 15 to 16). rollback-runtime.sh deliberately blocks the runtime-only downgrade. Review data compatibility and preserve all new writes before any reverse migration or restore. The stopped-service state backup and old installation remain intact; do not overwrite newer sessions from the snapshot.

## Review request

Review requested: current exact PR #1 head after publication.
Review scope: isolated core/Node activation evidence, source gate/regression checks, precise native-time config delta, rollback constraints, and honest PARTIAL classification with separate context-vault findings.
Recommended next action: independent evidence review. Review is not VPS runtime verification and must not silently accept or repair remaining issues.
