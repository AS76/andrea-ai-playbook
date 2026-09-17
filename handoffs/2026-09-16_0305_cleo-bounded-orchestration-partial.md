# Cleo bounded native sub-agent orchestration — partial engineering report

Date: 2026-09-16
Status: RUNNING / ENGINEERING_ACCEPTANCE_INCOMPLETE
Engineering result: PARTIAL

## Request

Surgically refactor Cleo's live orchestration policy so she chooses local work, a configured specialist, or bounded temporary worker(s) by material benefit, while retaining final synthesis and existing approval boundaries.

## Discovery

- FACT: the active runtime is OpenClaw 2026.9.4 (`3a9d69d`) from `/opt/openclaw-2026.9.4`.
- FACT: Cleo's active agent id is `cleo`; workspace is `/root/.openclaw/workspace/main`; agent directory is `/root/.openclaw/agents/cleo/agent`.
- SOURCE_VERIFIED: OpenClaw 2026.9.4 injects workspace bootstrap context including `AGENTS.md`, `SOUL.md`, `USER.md`, and `IDENTITY.md` when eligible. The essential orchestration contract therefore belongs in `AGENTS.md`.
- CONFIG_VERIFIED: no configured Manager agent exists. The normal topology is Cleo directly to a specialist or temporary child and back to Cleo synthesis.

## Implemented state

- `AGENTS.md` now contains the authoritative invariant: **Cleo owns the answer, not necessarily all the work.** It defines local execution, persistent-specialist routing, isolated temporary workers, exceptional fork use, bounded parallelism, independent verification, Cleo synthesis, failure handling, no permanent-agent creation, and unchanged external-action authority.
- `SOUL.md` retains only the identity-level orchestration principle and points operational routing to `AGENTS.md`.
- `00_INDEX.md`, `01_TEAM_ROSTER.md`, `02_CLEO_OPERATIONS.md`, `B_BINDINGS.md`, and `AGENTS_CONFIG.md` align the canonical playbook with material-benefit routing and mark the Manager pattern exceptional.
- CONFIG_VERIFIED: Cleo has `subagents.delegationMode="prefer"` and may target `cleo`, `max`, `pixel`, `atlas`, `lex`, `scribe`, `scout`, and `visa`.
- CONFIG_VERIFIED: global native-child limits are `maxConcurrent=3`, `maxChildrenPerAgent=3`, and `maxSpawnDepth=1`; direct children are leaves.
- CONFIG_VERIFIED: Cleo's configured model remains `openrouter/auto`; no channel binding, credential, provider, or memory architecture change is part of this refactor.

## Rollback

- BACKUP_VERIFIED: the pre-change bundle was streamed encrypted directly to S3 as `backups/openclaw/2026-09-16/cleo-orchestration-prechange-20260916T024218Z.tar.gpg`.
- BACKUP_VERIFIED: full remote SHA-256 readback was `b661a5b66854c19c765784376b919f7a123eef5055c24793fe3a5347dc931db1`.
- Rollback procedure: restore only the listed workspace/config files from that object, validate `openclaw.json`, and restart only if restoring the configuration requires a runtime reload.

## Validation

- CONFIG_VERIFIED: `openclaw config validate --json` returned `valid: true`. It reported only pre-existing disabled-plugin configuration warnings.
- RUNTIME_VERIFIED: Gateway RPC health returned `ok: true`; the event loop was not degraded, all expected plugins loaded without errors, and the default Telegram account was running and connected.
- RUNTIME_VERIFIED: configured agents enumerated after the change and native `sessions_spawn` accepted both same-agent and Max-targeted isolated children.
- OBSERVED: dynamic routing selected configured runtime routes during child execution; no persisted model/provider configuration change was observed.

## Acceptance results

| Test | Result | Evidence |
|---|---|---|
| A — simple local | PASS | `orch-a-20260916` answered `2 + 2 = 4` directly with no child/tool call. |
| B — isolated temporary worker | PASS | `orch-b-20260916` spawned a same-agent child with explicit `context="isolated"`, yielded without polling, received the result, and synthesized it. |
| C — existing specialist | PASS | `orch-c-20260916` enumerated configured agents, targeted `agentId="max"` with isolated context, yielded, and synthesized Max's review. |
| D — parallel | FAIL | Cleo spawned exactly two isolated children, but then called `agents_wait` on ordinary non-collector runs. Both ids returned `not_found`; Cleo answered locally instead of collecting child results. |
| E — independent verifier | INCOMPLETE | `orch-e-20260916` announced verification and discovered the spawn tool, but no verifier spawn or synthesized final response was recorded. |
| F — fork discipline | PARTIAL | B–D explicitly used isolated context and no fork was observed. No genuine transcript-dependent fork case was executed. |
| G — failure handling | NOT_RUN | No dedicated harmless child-failure acceptance case was completed. D demonstrated no retry storm, but it was not the specified failure test. |
| H — authority | NOT_RUN | The written contract preserves authority, but no runtime denial/approval-boundary test was completed. |

## Git state

- The workspace repository was already heavily dirty with unrelated tracked and untracked user content before this task.
- The orchestration files include both task changes and pre-existing user changes relative to repository HEAD; a clean task-only local commit has not been proven safe.
- No workspace commit was created, and nothing was pushed.

## Risks and required remediation

1. Correct the parallel collection flow using the installed tool semantics. Ordinary announcing runs should complete through native completion/yield; `agents_wait` is documented for collector runs.
2. Rerun D and complete E–H with transcript evidence.
3. Reconfirm Gateway/RPC, Telegram connectivity, agent enumeration, config validity, and unchanged persisted routing after the final test run.
4. Isolate only the task-owned workspace changes before creating the requested local commit; do not absorb unrelated dirty-tree changes.

## Verdict

The runtime is stable, but the mission's non-negotiable acceptance gate has not passed. The task must remain `RUNNING`; it is not ready for independent ChatGPT review.

**Current verdict: NOT_READY — REMEDIATION_REQUIRED.**
