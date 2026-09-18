# Jev remediation prepared; updater ownership gate closed

Date: 2026-09-18. Status: **BLOCKED** for production promotion and Gateway runtime acceptance. This records only an isolated test, encrypted rollback copy, and repeated read-only gate. The Gateway remained stopped.

## FACT

- The original 2026.9.4 `openclaw.mjs update` process and its `openclaw-update` child remain live. This Codex session is a descendant of that child. The Gateway user service remains `inactive/dead`, `MainPID=0`, with last exit status 0 at 09:39:45 UTC. Terminating the updater from this child would cancel the active triage ownership chain.
- The deployed Jev `src/index.ts` SHA-256 remained `4f72997437ab016a358b81f4b7a101d1c6954202255e854e659681f3d2490792`; `dist/index.js` remained `5e9d5b640132edfb391e010d98b4bc174cfd0c0794ebfb3e616b500190fe5d44`. Neither production file was changed.
- The isolated three-edit proposal compiled against the installed 2026.9.4 SDK, imported under Node 24.21.0, registered `before_agent_finalize`, `before_tool_call`, `after_tool_call`, and `agent_end`, and each hook returned `undefined` with its guards disabled. The finalize hook registered only supported `{ timeoutMs: 8000 }` options. The check used a temporary telemetry path and no Gateway process.
- The affected plugin source, build, manifest, and test were streamed as a tar producer into the established encrypted S3 backup tool. The producer and encryption exited successfully; full remote SHA-256 readback matched `77ca74f73d31ead59455a5ff90fc21c1591e4e6b7254c7cf96996821ffc9cfd8` (92,763 encrypted bytes). No local archive was created. Object: `openclaw/rollback/2026-09-18-jev-decision-gate-prepatch-1055UTC.tar.gpg`.
- The OpenClaw config SHA-256 remained `478aa15c727ba84d9a777ee88aa98e9e010c69b6305890e16bd492ac75114a58`, byte-identical to the documented pre-update copy. Prior shared and 13 agent SQLite read-only quick checks passed; no DB check was rerun in this step.

## INFERENCE

- The isolated registration result reduces risk of a syntax or hook-option failure. It does not prove live Gateway plugin initialization, Jev API behavior, Telegram operation, RPC, or database behavior after start.

## UNVERIFIED / remaining gate

- The original updater must exit through its owning terminal or supervisor. An independent session must then verify that process and its triage child have exited and that no update lease remains. Only then should it review/promote the scoped plugin source/build change using the completed rollback copy, repeat pre-start acceptance, and consider the existing systemd start mechanism.
- The plugin's enabled behavioral flags remain false in source defaults; whether Andrea intends to enable Jev guards is not established by this episode. Do not change feature flags during this repair.
- Gateway health JSON, status, RPC, agent registry, plugin/channel state, Telegram delivery, sustained liveness, and post-start config/database checks remain unverified. Do not call this runtime acceptance.
- Draft PR #3 remains based on PR #1's ledger lineage and conflicts with newer PR #1 commits. Preserve the history; reconcile separately after PR #1's base decision.

## Next action

Close this triage session through its owning terminal, then start a new independent session to verify updater exit before any production Jev promotion or Gateway start. Do not signal the parent updater from this child.
