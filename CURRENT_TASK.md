# CURRENT TASK

Request: remove unused Jev plugin and Showly MCP only, with upstream precedent, scoped encrypted S3 rollback, one controlled restart if needed, runtime acceptance, and one real Scout cron comparison.

Overall status: REVIEW_REQUIRED
ChatGPT Review: PENDING_REVIEW for this removal continuation
Engineering acceptance: PARTIAL / DEGRADED

Prior continuation baseline: OpenClaw 2026.9.4; Gateway active at that continuation's start. Prior Jev source/build repair loaded successfully, but two later health RPCs timed out before recovery. Telegram bot probes and an isolated Cleo reply passed; a new Telegram delivered reply was then unverified. PR #3 was draft, based on `codex/handoff-ledger`, and conflicted with four newer base commits. Its body then claimed the Gateway was stopped and Jev unchanged.

Prior continuation result: merged the advanced ledger base without rewriting incident history; corrected PR #3; verified an encrypted S3 config rollback; disabled Jev in one config line and restarted once. A command cron and Scout agent cron completed, Telegram E2E delivery passed, and 72/72 RPCs passed over 18 minutes. Three transient event-loop degradations and the Scout cron's 290.5-second duration made that acceptance PARTIAL / DEGRADED. Its sanitized inventory, GitHub precedents, limits, and rollback are in `handoffs/2026-09-18_jev-disable-observation-plugin-inventory.md`.

Current continuation: after a verified encrypted S3 rollback, removed only Jev's explicit config registrations and local plugin directory and used the supported MCP CLI to unset Showly. Official Jev uninstall dry-run refused because this config-origin plugin lacked authoritative package-owner metadata. One controlled restart applied both changes. Config, Gateway, Telegram E2E, and 48/48 monitored RPCs passed; Scout cron completed in 78.284 seconds versus 290.528 seconds immediately prior, but remains above the historical 20–29 second range. See `handoffs/2026-09-18_jev-showly-removal-acceptance.md` for exact changes, upstream precedents, rollback hash, evidence, and unresolved limits.

Scope boundary: no Doctor fix, OpenClaw update, service rewrite, provider/auth/model change, Scout/cron/SQLite redesign, or automatic repair of unrelated components.

Prior handoffs: `handoffs/2026-09-18_openclaw-update-refusal-repair.md`, `handoffs/2026-09-18_jev-updater-remediation-assessment.md`, `handoffs/2026-09-18_jev-remediation-prepared-gate.md`, and `handoffs/2026-09-18_jev-gateway-controlled-acceptance.md`. These are chronological records, not current status.
