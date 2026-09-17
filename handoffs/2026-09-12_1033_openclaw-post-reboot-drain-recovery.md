# OpenClaw post-reboot drain recovery

Date: 2026-09-12
Status: REVIEW_REQUIRED / PENDING_REVIEW
Component: OpenClaw 2026.9.3 user Gateway

## Request and boundary

Diagnose OpenClaw after an OS-upgrade reboot and a user-invoked `doctor --fix` appeared stuck. Recovery was limited to evidence-led service handling. No Doctor rerun, updater, configuration edit, plugin repair, routing change, database change, or delivery message was authorized or performed.

## Evidence

- RUNTIME_VERIFIED: no `doctor` process remained in the host process table.
- RUNTIME_VERIFIED: Gateway PID 1242 was in systemd `deactivating (stop-sigterm)` and repeatedly reported a restart drain blocked by `activeTasks=1`.
- RUNTIME_VERIFIED: the unit declared `TimeoutStopSec=330`, `KillMode=control-group`, and `Restart=always`.
- RUNTIME_VERIFIED: the stop timed out; systemd terminated the old Gateway and marked the unit failed.
- CONFIG_VERIFIED: `/root/.openclaw/openclaw.json` had not been modified during the incident and `config validate` passed with only three pre-existing disabled-plugin configuration warnings.
- RUNTIME_VERIFIED: one `systemctl --user start openclaw-gateway.service` started PID 4900 via the reviewed isolated Node 24.21.0 / OpenClaw 2026.9.3 runtime.
- RUNTIME_VERIFIED: service became `active/running`; localhost listener 18789 was owned by PID 4900; Gateway health returned `ok: true`; event-loop degradation was false; plugin health had no errors or unavailable entries.
- RUNTIME_VERIFIED: Telegram lifecycle was ready/running/connected and each configured account probe returned success.

## Limits and residual findings

- NOT PROVEN: no outbound Telegram delivery marker was sent, so end-to-end agent execution and delivery were not tested.
- ACCEPTED LIMIT: startup reported an event-loop warning while `sidecars.control-ui-assets` consumed about 71 seconds; health was non-degraded after readiness.
- OPEN FOLLOW-UP: startup Doctor warnings reported missing package directories for Discord, Qwen, and WhatsApp. They were not shown to cause this drain and were deliberately not repaired.
- INFERENCE: the apparent Doctor hang was the requested restart waiting on one active Gateway task, not a still-running Doctor process.

## Rollback

No persistent configuration or code change was made. The only operational action was starting the failed user service after its prior stop timed out. Stopping the recovered service would reverse availability and is not recommended as rollback.

## Review request

Confirm that the evidence supports the drain diagnosis, that the one-time service start was appropriately bounded, and that acceptance is correctly limited because message delivery was not exercised.
