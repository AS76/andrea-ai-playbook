# OpenClaw failed-update repair — 2026-09-18

## Scope and baseline

- Requested target: this host's OpenClaw 2026.9.4, Node 24.21.0, existing state and configuration.
- Original update run `8eab31b2-12dc-48a8-8e5f-e6dcfa8479c2` failed at `requested`: `package manager owner is unknown; no changes were made`. No package installation step was recorded.
- The systemd user Gateway was explicitly stopped at 09:39:45 UTC, before that update attempt. It exited 0 and remained inactive. Initial `openclaw health --json` returned `ECONNREFUSED` at loopback port 18789.
- The shell's npm global shim and the isolated service package shim both reported npm ownership through `openclaw update status --json`. Subsequent process inspection established that the still-live original updater parent invoked `/opt/openclaw-2026.9.4/node_modules/openclaw/openclaw.mjs update` directly, outside the npm global shim.

## Protection and repair

- Pre-repair config and shared SQLite database with sidecars streamed encrypted directly to S3 object `openclaw/rollback/2026-09-18-update-refusal-pre-repair.tar.gpg`. Producer and encryption exited successfully; full remote readback SHA-256 matched `8d8b6760e75b797947007bf570408abcb4e88e4ca645821d386e07e34950e499`. No local archive was created. Decryption and restore were not tested.
- Ran `openclaw update repair --json` from the npm global shim. It selected full finalization, including its internal Doctor repair. Result: exit 0, `status: warning`, `restart: false`; Doctor reported that it left the stopped Gateway unchanged.
- The repair recorded Doctor warnings for two preserved legacy Skill Workshop backup roots whose workspaces have no configured owner, and a plugin finalization warning. No backup roots were removed and no capability consent was supplied.
- Current `openclaw.json` matches OpenClaw's local pre-update copy byte for byte (SHA-256 `478aa15c727ba84d9a777ee88aa98e9e010c69b6305890e16bd492ac75114a58`). `openclaw config validate` passed with two disabled-plugin warnings.

## Verification and limits

- `openclaw update status --json`: current CLI root is npm-owned; installed and registry latest versions are 2026.9.4; latest repair run `cd5b7057-fd79-47c0-b92d-98ab4f108c46` is finished/succeeded. The original failure remains in history.
- `openclaw status --all`: version 2026.9.4, npm up to date; Gateway unreachable with `ECONNREFUSED`. `systemctl --user show` still reports inactive/dead, last exit 0, unchanged inactive timestamp 09:39:45 UTC.
- No Gateway restart was attempted because it would override the prior explicit stop. Running version, Gateway RPC, channels, and symptom reproduction on an active runtime are **UNVERIFIED**. Engineering acceptance is **PARTIAL**.
- The service uses an operator-owned isolated runtime drop-in, separate from the npm global CLI. Doctor identified its entrypoint and PATH as nonstandard. No service definition was rewritten.

## Review request

Review whether the update refusal and repair are characterized accurately, whether the stopped-service decision respects the operator stop, and whether any additional evidence is needed before a separate operator resumes the Gateway. This review is evidence review, not runtime verification.

## 2026-09-18 bounded acceptance — FACT

- CLI: `command -v openclaw` is `/opt/node-v24.21.0-linux-x64/bin/openclaw`; its real path is `/opt/node-v24.21.0-linux-x64/lib/node_modules/openclaw/openclaw.mjs`. CLI banner and package manifest both identify `2026.9.4 (3a9d69d)`; the shell Node is `/opt/node-v24.21.0-linux-x64/bin/node`, `v24.21.0`. `npm prefix -g` is `/opt/node-v24.21.0-linux-x64`; `npm root -g` is its `lib/node_modules`; `npm ls -g openclaw --depth=0` identifies the installed package.
- Gateway service: systemd user unit `openclaw-gateway.service` has an operator-owned drop-in. Effective `ExecStart` uses the same Node binary but `/opt/openclaw-2026.9.4/node_modules/openclaw/dist/index.js`, a distinct physical package whose manifest says `2026.9.4`. Its read-only source guard checked eight files and passed. The unit is enabled, inactive/dead, not failed; last exit 0 and stop timestamp 09:39:45 UTC. Journal shows systemd stop, SIGTERM, and completed active-work drain. The initiating operator identity is not established.
- Original update executable: the original updater parent is still live and its process command is `/opt/node-v24.21.0-linux-x64/bin/node /opt/openclaw-2026.9.4/node_modules/openclaw/openclaw.mjs update`. Its child `openclaw-update` is also live in triage. The corresponding DB run is finished/failed at admission, and a later repair run is finished/succeeded; zero unfinished update rows were found. The live process remains a separate operational hazard despite the finished DB row.
- Service environment: the unit reads `gateway.systemd.env`; expected gateway and provider key *names* are present. `OPENCLAW_SERVICE_REPAIR_POLICY` is absent from that file. No value was copied to this ledger. The service is a user unit with a drop-in, not a root-owned systemd template unit.
- Pre-start checks: `openclaw config validate` passes with disabled `active-memory` and `memory-core` warnings. Current and `openclaw.json.pre-update` SHA-256 both equal `478aa15c727ba84d9a777ee88aa98e9e010c69b6305890e16bd492ac75114a58`. Shared SQLite `quick_check=ok`, `user_version=17`; all 13 discovered agent stores returned `quick_check=ok`, `user_version=19`. This checks logical SQLite integrity, not a full restore or semantic session-history audit. Port 18789 and ClawMem port 7438 have no listener. `openclaw health --json` returns `ECONNREFUSED`; `openclaw gateway status --deep` reports the stopped user service.
- Plugin inventory: `openclaw plugins list --json` reports a persisted registry with 81 discovered plugins and no registry diagnostics. This is not live load proof. The last real Gateway startup logged that enabled `jev-decision-gate` failed to initialize: its built entrypoint imports `createSecretRefResolver`, which the running 2026.9.4 plugin SDK does not export. Doctor lint returned an error for the configured `idrivee2` MCP server lacking OAuth authorization, plus a warning for two preserved Skill Workshop legacy backup roots without configured owners. The previous update repair also reported a plugin finalization warning.

## Upstream comparison — INFERENCE

- `OWNER_BUG_MATCH=PARTIAL`: [#146038](https://github.com/openclaw/openclaw/issues/146038) describes the same admission refusal with a nonstandard npm layout; [#146091](https://github.com/openclaw/openclaw/pull/146091) fixed custom-prefix owner detection after the 2026.9.4 release build. This host's original invocation used an isolated package entrypoint directly, while its npm global CLI and isolated shim currently report npm ownership. The recorded refusal matches the symptom; the exact resolver branch that failed is not established.
- `REPAIR_BUG_MATCH=PARTIAL`: [#151081](https://github.com/openclaw/openclaw/issues/151081) and merged [#151132](https://github.com/openclaw/openclaw/pull/151132) establish a published-2026.9.4 fresh-Doctor policy regression for stopped, externally supervised systemd template services. This host also had a stopped, isolated service, but it is a managed user unit with an operator drop-in; local repair completed with warnings. The upstream fix is not treated as present in this installation.

## Pre-start classification and decision

| Finding | Classification | Reason |
| --- | --- | --- |
| Live original updater parent and `openclaw-update` triage child | START_BLOCKER | A still-running maintenance tree can resume after triage; a finished DB row does not prove process quiescence. |
| Enabled Jev decision gate failed on the last Gateway startup | START_BLOCKER | The configured completion/verification guard does not initialize with this 2026.9.4 SDK. The persisted registry's `loaded` label conflicts with live journal evidence. |
| `idrivee2` MCP OAuth/schema lint error | REQUIRES_INVESTIGATION | Assistant tool startup cannot be relied on for that configured server; no credential change was attempted. |
| Skill Workshop backup roots without configured owners | REQUIRES_INVESTIGATION | Doctor preserved both roots; no evidence of data loss, but ownership remains unresolved. |
| Repair plugin finalization warning | REQUIRES_INVESTIGATION | Repair exit 0 did not establish all runtime plugins healthy. |
| Isolated service entrypoint and nonstandard PATH | ACCEPTABLE_FOR_START | The effective path, package version, and eight-file source guard are known; the layout must remain operator-owned. Other blockers prevent start. |
| Disabled-plugin config warnings | ACCEPTABLE_FOR_START | Both plugins are explicitly disabled; config validation passes. |
| SQLite quick checks and config hash | ACCEPTABLE_FOR_START | Read-only integrity and byte comparison pass within their stated limits. |

Pre-start verdict: **BLOCKED**. The controlled-start gate was not reached. No Gateway start, repair, migration, config edit, service rewrite, or database mutation was performed during this acceptance. Runtime health, RPC, channels, Telegram delivery, and live plugin status remain **UNVERIFIED**.

## PR #3 topology and next action

- Before correction, PR #3 targeted `main` and displayed 32 historical ledger commits. PR #1 is still open and carries the ledger lineage; PR #2 already targets that lineage. PR #3 was created from an earlier PR #1 commit.
- PR #3's base was changed through the GitHub REST API to `codex/handoff-ledger`. At retargeting it showed one incident commit and three incident files: `STATUS.md`, `CURRENT_TASK.md`, and this handoff. This acceptance adds a second incident commit touching the same files. No branch history or reviewed commit was rewritten; PR #1 and PR #2 remain intact.
- PR #3 is still draft and GitHub reports `CONFLICTING` against the current PR #1 head, which advanced four commits after PR #3 branched. Resolve that status after PR #1's review/merge decision; do not force-push the historical branch merely to make the PR mergeable. `PR #3 Git topology=NEEDS_RECONCILIATION` for merge, with the review diff now scoped cleanly.
- Recommended operational action: let the original updater/triage process exit through its owning workflow, then separately authorize investigation of the enabled Jev plugin failure before a new controlled-start acceptance. This record does not authorize remediation.
