# Separate remediation assessment — live updater tree and Jev plugin

Date: 2026-09-18. Scope: read-only production inspection and an isolated `/tmp` build proposal. No production repair, Gateway start, process termination, configuration change, or database write was performed.

## FACT — updater ownership

- The failed update row is `finished/failed`; a later repair row is `finished/succeeded`; the shared database has zero unfinished update rows.
- The original updater remains a live process. Its parent command invoked the isolated OpenClaw 2026.9.4 `openclaw.mjs update` directly. Its `openclaw-update` child launched a Codex triage child; the current Codex session is descended from that child. The updater and child are waiting in event polling. A finished database row therefore does not establish process exit.
- The Gateway user service is still inactive/dead with last exit 0 and the same 09:39:45 UTC stop timestamp. No listener exists on Gateway port 18789.

## FACT — Jev build mismatch

- The configured `jev-decision-gate` plugin entry is enabled. Its inner feature flags are absent, and the current source defaults its behavioral guards to disabled. The last real Gateway startup nevertheless logged plugin initialization failure because deployed `dist/index.js` imports `createSecretRefResolver` from `openclaw/plugin-sdk/plugin-entry`.
- The installed 2026.9.4 service package does not export that symbol from `plugin-entry`. Its focused `secret-ref-readonly` subpath exports `resolveReadOnlyEnvSecretRef` instead. The TypeScript source, modified later than `dist/index.js`, no longer imports either missing helper and uses a vault reader. The source tree is untracked in the surrounding workspace Git repository, so a tracked review history is unavailable there.
- Compiling the unmodified source against its pinned 2026.9.4 SDK failed on five TypeScript errors: duplicate telemetry timestamp order, three records missing required `ts`, and unsupported `allowConversationAccess` in a `before_agent_finalize` hook registration option. The checked-in unit test imports a `JevDecisionGatePlugin` symbol absent from the current source and uses older config fields; it is not current behavioral proof.
- An isolated `/tmp` proposal made `TelemetryRecord.ts` optional, ensured `logTelemetry` supplies the timestamp after the record spread, and removed the unsupported hook option. That copy compiled with exit 0 and its generated plugin entry imported successfully under Node 24.21.0. The plugin-local SDK `plugin-entry.js` is byte-identical to the isolated service package's SDK entry. This is compile/import proof only; hook behavior and production Gateway loading remain unverified. The production `dist/index.js` hash stayed `5e9d5b640132edfb391e010d98b4bc174cfd0c0794ebfb3e616b500190fe5d44`.

## Upstream precedent and inference

- OpenClaw [#55533](https://github.com/openclaw/openclaw/issues/55533) documents external plugin breakage when SDK exports change; [#135776](https://github.com/openclaw/openclaw/issues/135776) documents a core/plugin version skew with a missing SDK export. No exact upstream issue for this local `jev-decision-gate` source/build mismatch was found in the searched issues and PRs. The direct evidence here points to an older deployed build relative to the current source, rather than a proven OpenClaw core regression.
- Upstream [update guidance](https://docs.openclaw.ai/cli/update) says a registered live child or process group excludes a new update. The live triage ancestry is the current session's ownership boundary; terminating it from inside this session would cancel the assessment and risks interrupting the owner's cleanup. No signal was sent.

## Repeated pre-start gate

- Current config validates and its SHA-256 still equals the documented pre-update copy. Shared and 13 discovered agent SQLite `quick_check` results remain `ok`. Zero unfinished update rows. Gateway port 18789 remains free. Systemd still reports inactive/dead, last exit 0, no restart count increase. Original updater and its triage descendants are still live. Deployed Jev build is unchanged.
- Verdict: **BLOCKED**. No controlled start. The previous runtime acceptance remains unverified.

## Exact proposed remediation phase

1. Let the original update/triage session finish through its owning terminal or supervisor. From an independent shell, verify the specific process tree has exited, no update lease/run remains active, and the Gateway is still stopped. Do not terminate the current fixing subtree to force progress.
2. Review Jev's current hook contracts and replace the stale test with a bounded load/registration test against the isolated 2026.9.4 runtime. The isolated three-edit proposal is a starting point, not approved production bytes. Resolve feature-flag intent before promotion.
3. Before any production plugin mutation, stream an encrypted rollback copy of the plugin source, deployed build, and relevant manifest directly to S3 and verify full remote SHA-256 readback. Apply only the reviewed plugin build; leave OpenClaw core, config, databases, service definitions, and unrelated plugins untouched.
4. Repeat the pre-start gate. If clear, start through the existing systemd user service and run `openclaw health --json`, `openclaw status --all`, `openclaw gateway status --deep`, RPC, plugin, channel, Telegram, config-hash, and sustained-liveness checks. Stop through the same service owner on a fail-closed trigger.

Steps 3 and 4 were not performed; the repeated pre-start gate is still blocked.
