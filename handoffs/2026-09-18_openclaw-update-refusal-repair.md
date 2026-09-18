# OpenClaw failed-update repair — 2026-09-18

## Scope and baseline

- Requested target: this host's OpenClaw 2026.9.4, Node 24.21.0, existing state and configuration.
- Original update run `8eab31b2-12dc-48a8-8e5f-e6dcfa8479c2` failed at `requested`: `package manager owner is unknown; no changes were made`. No package installation step was recorded.
- The systemd user Gateway was explicitly stopped at 09:39:45 UTC, before that update attempt. It exited 0 and remained inactive. Initial `openclaw health --json` returned `ECONNREFUSED` at loopback port 18789.
- The shell's npm global shim and the isolated service package shim both reported npm ownership through `openclaw update status --json`. The failed invocation's exact executable path was not recorded, so its ownership mismatch is an inference.

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
