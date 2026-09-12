# CURRENT TASK

Request: recover OpenClaw after the 2026.9.4 update path left the Gateway starved and then failed; user explicitly authorized interruption of the still-running updater/diagnostic subtree and controlled recovery.

Overall status: REVIEW_REQUIRED
ChatGPT Review: PENDING_REVIEW
Engineering acceptance: RUNTIME_RECOVERED_WITH_CONTAINMENT

Result: terminated only the authorized updater subtree, independently reproduced the starvation, ruled out SkillHub with an A/B run, and isolated the core skill watcher as the effective containment boundary. The persistent delta is only `skills.load.watch=false`; SkillHub is enabled.

Recovery evidence: Gateway active/running on OpenClaw 2026.9.4 and Node 24.21.0; health 29 ms; event-loop utilization 0.04 and P99 23.2 ms; listener backlog zero; status reachable; Telegram 11/11 accounts OK; recovered-generation telemetry includes successful inbound processing and completed outbound delivery.

Safety: encrypted configuration rollback streamed directly to S3 with full SHA-256 readback and no local archive. No Doctor fix, capability grant, unit reinstall, routing change, database mutation, or package operation was performed.

Operational tradeoff: automatic skill-directory watching is disabled. Restart or a supported manual refresh is required after deliberate skill changes until the upstream invalidation behavior is corrected.

Current handoff: `handoffs/2026-09-12_1310_openclaw-skill-watch-containment.md`.

Prior records remain preserved, including `handoffs/2026-09-12_1035_openclaw-2026-9-4-update-blocked.md` and `handoffs/2026-09-12_1033_openclaw-post-reboot-drain-recovery.md`.
