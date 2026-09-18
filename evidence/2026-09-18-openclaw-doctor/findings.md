# OpenClaw Doctor repair outcome — 2026-09-18

## Source and boundaries

- Local source inspected in full: `/root/.openclaw/tmp/doctor-fix3.log`, 335 lines, 33,882 bytes, last modified 2026-09-18 16:22:16 UTC. SHA-256: `283bd762f911398560ee4c621e7c2893486e5884d6b5b91aa83bee9455af4d7d`.
- This is a sanitized transcription of all distinct findings. The raw log remains local; repeated ClawMem registration and skill warning lines are summarized here.
- The log begins `OpenClaw doctor` and says `Stopped the managed Gateway for Doctor repair.` The exact invoking shell command and process exit code were not preserved in this file.
- This report covers the observed 2026.9.4 run. No new Doctor invocation was made for this ledger entry.

## Exact terminal outcome

> Doctor could not complete maintenance. Check the reported service state and resolve the failure.
>
> Gateway service ownership or manager identity changed; inspect it before restarting manually.

The log says Gateway health would be checked *after* repair; no successful post-repair Gateway health result appears in the log. It reports one change: `Cron store normalized at ~/.openclaw/cron/jobs.json.` At read-only inspection after the run, `/root/.openclaw/cron/jobs.json` did not exist. Only older `.bak`, `.backup-*`, and `.migrated` files were visible in that directory. Therefore the claimed normalization cannot be accepted as a verified persisted result.

## Findings by Doctor section

| Section | Complete distinct finding | Interpretation limit |
|---|---|---|
| Startup optimization | `NODE_COMPILE_CACHE` unset; `OPENCLAW_NO_RESPAWN` not 1. Suggested low-power-host environment settings. | Suggestions only. |
| Update history and state migrations | Two Skill Workshop legacy collection backup roots retained for manual review. Workspaces `counsel` and `mark` mapped to no configured agent. Zero proposal targets outside agent directories. | Recorded update warnings may predate this run; Doctor also repeated the migration warnings live. Preserved roots must be reviewed, not deleted merely to clear warnings. |
| Config | Disabled plugins `active-memory` and `memory-core` still have config present. A slow SQLite transaction hold was logged. | No cause or duration was established for the transaction warning. |
| Provider metadata | `models.providers.google.models[1]`, `[2]`, `[3]`, `[5]`, `[7]`, `[8]`, `[9]` match a historical generated fingerprint, but their API route is not owned by the shipped catalog; all were left unchanged. | No model-route repair is proved. |
| Telegram group policy | `channels.telegram.groupPolicy=allowlist` with empty `groupAllowFrom` and `allowFrom`; group messages will be dropped under that policy. | A configuration warning, not a direct delivery test. |
| Plugin registry | 48 of 80 enabled plugins indexed. ClawMem registration messages repeated. | Count is Doctor's report, not an independent plugin acceptance test. |
| Channel ingress | Four dead-lettered Telegram events for `default`, one for `max`. | Contents and delivery impact not inspected. |
| State integrity | Five agent directories lacked `agents.list` entries; examples `counsel`, `mark`, `openclaw` and two others. Retained unconfigured SQLite databases for `lex`, `max`, `pixel`, `visa`. | Doctor did not remove databases. No inference that these agents should be removed. |
| Backups | `No successful backup is recorded` in OpenClaw's native backup record. | This does not establish the state of the separate encrypted S3 backup process. |
| Cron | Fourteen isolated automations use shell/process tools from prompts. Doctor labels this supported and informational. Thirty-three tool-bearing cron jobs retain restrictive legacy sender-policy resolution because account authority is unprovable. Two automations have finite inherited default tool caps recorded before final MCP provenance. | Doctor did not convert the 14 jobs, infer authority for the 33, or widen the two caps. |
| Host desktop | Desktop lab disabled. | Informational. |
| GitHub projects | Gateway-owned private project access would need a Gateway token or shared process token; otherwise search is public-only. | Informational. |
| Browser relay | Legacy authentication enabled; Doctor recommends moving paired clients to v2 before disabling it. | No client migration performed. |
| MCP | `idrivee2` could not expose runtime tools for schema validation because OAuth authorization is required. ClawMem's `__IMPORTANT` tool was renamed internally to a provider-safe tool name. | `idrivee2` tool startup remains unverified. |
| Skill Workshop | Two retained legacy backup roots require workspace ownership and manifest review. | Doctor left them untouched. |
| Skills and bootstrap | Symlink escape warnings for `typesafe-ai`, `reddit`, `team-delegation`; precedence collisions for `blogwatcher` and `webwright`; Max `AGENTS.md` and `USER.md` bootstrap unreadable due to a symlink path component. | Summarizes repeated per-workspace warnings; no repair is shown. |

## Separate post-run read-only observations

- `systemctl --user show openclaw-gateway.service` returned `ActiveState=active`, `SubState=running`, `MainPID=615820`, `NRestarts=0` at inspection on 2026-09-18 shortly before 16:40 UTC. This does not establish Gateway RPC, sustained liveness, Telegram transport, or delivery.
- `/root/.openclaw/openclaw.json` modification time was 13:08:17 UTC, before this Doctor log's completion. That timestamp alone does not prove byte identity or absence of all configuration changes.
- The Doctor log's warning about changed service ownership/manager identity remains unresolved in this evidence. Do not restart the Gateway based solely on `active/running`.

## Review questions

1. Does the evidence support a failed/partial Doctor repair outcome rather than successful maintenance?
2. Is the missing `cron/jobs.json` reported clearly as a contradiction to Doctor's change line?
3. Are runtime health and backup scope kept distinct from Doctor's diagnostic text?
4. Are any findings overstated as causes or completed fixes?
