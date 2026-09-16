# CURRENT TASK

Request: remove Claude Code and OpenCode and their dedicated dependencies.
Overall status: REVIEW_REQUIRED
ChatGPT Review: PENDING_REVIEW
Engineering acceptance: PASS
Scope: standalone installations and app-specific configuration/data for root and codexuser.
Initial state: neither CLI appeared on root PATH, but OpenCode had a standalone binary and Claude Code remained installed in codexuser's npm prefix. App-specific package trees and data directories remained.
Change: after encrypted S3 rollback verification, removed the dedicated installs, Node package trees, app settings/data, and Claude Code desktop handler. Shared Claude SDK binaries bundled with the ClawMem MCP cache and active OpenClaw source checkout were preserved.
Verification: exact removed paths absent; root and codexuser global npm inventories show neither package; root PATH resolves neither CLI; no matching CLI process found.
Rollback: encrypted S3 object `maintenance/2026-09-16/claude-opencode-uninstall-20260916T1700Z.tar.gpg`; SHA-256 `c7e311020824c57bc4f6427198beb1b8f414ee4814ddc1bef622b92062016865`; full remote encrypted-object readback passed. Decryption and restore were not exercised.
Handoff: `handoffs/2026-09-16_claude-opencode-cleanup.md`.
Next action: independent ChatGPT evidence review.
