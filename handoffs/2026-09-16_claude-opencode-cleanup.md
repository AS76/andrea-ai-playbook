# Claude Code and OpenCode standalone cleanup

Date: 2026-09-16 UTC
State: REVIEW_REQUIRED / PENDING_REVIEW

## Request and scope

Remove Claude Code and OpenCode and their dedicated dependencies from the VPS. Preserve shared packages used by OpenClaw and ClawMem.

## Initial evidence

- Root PATH and root global npm inventory did not show either CLI. This was insufficient to establish removal.
- OpenCode binary remained at `/root/.opencode/bin/opencode` with local plugin dependency trees.
- Claude Code package and binary remained under `/home/codexuser/npm-global`.
- Root and codexuser app configuration/data directories remained. No matching CLI process or user service was found.

## Change and rollback

- Before mutation, streamed the exact target tree as a tar producer through the established encrypted S3 tool. It reported producer success, encryption success, and full remote SHA-256 readback.
- Rollback object: `maintenance/2026-09-16/claude-opencode-uninstall-20260916T1700Z.tar.gpg`.
- Encrypted object SHA-256: `c7e311020824c57bc4f6427198beb1b8f414ee4814ddc1bef622b92062016865`.
- Removed the dedicated root and codexuser installation, Node dependencies, configuration, history/data, cache, and desktop handler paths. The host trash interface accepted the paths; only the new task-specific trash entries were then cleared. An unrelated pre-existing trash item was left untouched.
- Restore procedure: fetch the encrypted object from S3, verify its SHA-256, decrypt with the configured recovery key, inspect the tar listing, then restore selected relative paths to `/` with ownership preserved. Restore was not exercised.

## Verification and limits

- `RUNTIME_VERIFIED`: all listed target paths absent; root PATH has neither command; root and codexuser global npm inventories list neither package; no matching CLI process found.
- `CONFIG_VERIFIED`: no matching user service found. No shared OpenClaw configuration was edited.
- `FACT`: Claude SDK executables in a ClawMem MCP cache and an active OpenClaw source checkout remain because those trees are shared dependencies. OpenClaw documentation, provider references, and an inactive Claude Code runner source file also remain; they are not standalone CLI installations.
- `UNVERIFIED`: full host-wide absence of every historical reference, and offsite decrypt/restore.

## Review request

Check that the evidence supports standalone removal, that the S3 rollback is adequate for this scope, and that shared dependencies were preserved.
