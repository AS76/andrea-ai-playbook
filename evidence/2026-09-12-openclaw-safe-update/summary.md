# OpenClaw safe-update and migration evidence

Date: 2026-09-12 UTC

## Initial read-only facts

- Runtime: `OpenClaw 2026.9.3 (1391f7c)`, isolated npm package at `/opt/openclaw-2026.9.3`, Node 24.21.0, CLI wrapper `/root/.openclaw/scripts/openclaw-isolated-cli`.
- Service: user `openclaw-gateway.service`, PID 23838, active since 2026-09-11 11:15:19 UTC, `NRestarts=0`, loopback port 18789 with `Recv-Q=0`.
- Resources: 37 GiB free on `/`; 3.6 GiB memory available at discovery.
- Config: `/root/.openclaw/openclaw.json`, mode 0600, validates with three disabled-plugin config warnings.
- Doctor JSON/lint: no pending startup/state migration. One error (`core/doctor/runtime-tool-schemas`, idrivee2 OAuth unavailable) and one warning (`core/doctor/skill-workshop-relocation`, two preserved legacy backup roots). No Doctor repair was run.
- Update status: stable candidate 2026.9.4 exists. Official dry-run refuses the isolated install because package-manager ownership is unknown. Installed source confirms its package-update path can invoke Doctor `--fix`; update was not attempted.
- Runtime registry: eight configured agents and 116 readable sessions. Main state SQLite `quick_check=ok`, schema 16; eight agent SQLite stores `quick_check=ok`, schema 19.
- Telegram: global and all account policies remain `allowlist`. Eleven accounts have proven account-level `groupAllowFrom`; all eleven were running, connected, lifecycle-ready, and probe-OK. No Telegram config change was needed.
- Tasks audit: one stale running subagent error and fourteen historical delivery-failed warnings. Security audit: zero critical, eight warnings, two information findings. These were classified only, not repaired.

## Recovery evidence

- Full established producer backup: `openclaw/recovery/safe-update-migration-20260912T065509Z.tar.gz.gpg`; encrypted bytes 269318763; remote readback SHA-256 `b99820140428fb9edfa44990b170dfcf8300e58dac538cba3f4f956dd6fe7d42`; no local archive.
- Workflow backup-only test: successful encrypted direct-to-S3 production and full remote readback; result retained in the mode-0700 run directory.
- Operations-file bundle: `openclaw/recovery/safe-update-ops-files-20260912T070122Z.tar.gpg`; encrypted bytes 164451; remote readback SHA-256 `338593ba22421c2ce924250309c3e25e2563c2c9ebca0b67f6b3b1cefc968db8`; no local archive.

## Production changes

- Replaced `/root/.openclaw/scripts/openclaw-safe-update.sh` with a fail-closed controller.
- Replaced `/root/.openclaw/scripts/OPENCLAW-SAFE-UPDATE-RUNBOOK.md` with the corresponding recovery and acceptance runbook.
- No OpenClaw config, model route, agent topology, database, Telegram setting, service unit, package, Gateway process, ClawMem, Vault, MCP, cron, or unrelated service was changed.

## Tests

- `bash -n`: PASS.
- dependency detection: PASS; ShellCheck unavailable and not installed.
- self-test/decision fixture: PASS.
- lock contention: PASS, second invocation exited 10 with `PRECHECK_FAILED`.
- insufficient-disk failure injection: PASS, exited 10 with `PRECHECK_FAILED`.
- no-update path pinned to installed 2026.9.3: PASS, exited 0 with `NO_UPDATE`, no reinstall.
- real discovery for 2026.9.4: PASS fail-closed, exited 20 with `MANUAL_REVIEW_REQUIRED` because the official updater refused package ownership.
- backup-only path: PASS with S3 encryption and full remote SHA-256 readback.
- update mutation/Doctor-fix/restart/rollback branches: NOT YET PRODUCTION-EXERCISED.

## Review remediation for commit 7d7e463

The `BLOCKED` evidence review is preserved at `reviews/2026-09-12_7d7e463_openclaw-safe-update.md`; it is an evidence deficiency, not an implementation failure. This directory now includes byte-identical complete copies of the current production wrapper and runbook, sanitized test projections in `test-fixtures.json`, installed updater source locations and excerpts in `installed-updater-doctor-path.md`, and the dynamic registry acceptance contract in `agent-registry-acceptance.json`.

The effective production registry intentionally used as this task's acceptance baseline has eight entries: `atlas`, `cleo`, `lex`, `max`, `pixel`, `scout`, `scribe`, and `visa`. The same key set is present in the 2026-09-09 pre-update snapshot, the 2026-09-11 pre-MCP-change snapshot, and current config. “Eight” is an observed result, not an acceptance constant: a future transaction must capture `keys(.agents.entries)` before mutation and compare the post-update key set to that captured baseline. The broader workspace role catalog is not being redefined, and this task made no topology change.

Remediation QA confirms SHA-256 equality between each published complete copy and its production source. No OpenClaw update, Doctor fix, Gateway restart, new backup, topology change, or unrelated remediation was performed.
