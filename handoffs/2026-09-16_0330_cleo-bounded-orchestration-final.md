# Cleo bounded native sub-agent orchestration — final engineering report

Date: 2026-09-16
Status: ENGINEERING_ACCEPTANCE_COMPLETE
Engineering verdict: READY_WITH_NOTES

## Scope and installed runtime

- FACT: OpenClaw `2026.9.4 (3a9d69d)` was inspected; no update was run.
- FACT: Cleo is agent `cleo`, workspace `/root/.openclaw/workspace/main`, with live config `/root/.openclaw/openclaw.json`.
- CONFIG_VERIFIED: Cleo remains on `openrouter/auto`; no model, provider, credential, memory, or channel-routing change was made in this continuation.

## Root cause and remediation of D

- TEST_VERIFIED: the original D run created both children 5 ms apart and started them 84 ms apart. They overlapped and both succeeded.
- ROOT_CAUSE: category F / OTHER — test-harness misuse of installed tool semantics. The parent called `agents_wait` on ordinary announcing runs created without `collect=true`; OpenClaw 2026.9.4 documents collector waiting for collector runs, so both ids returned `not_found`. This was not a Cleo decision failure, concurrency limit, second-spawn failure, or missing fan-out capability.
- REMEDIATION: one operational sentence was added to `main/AGENTS.md`: spawn independent bounded children before waiting; ordinary fan-out uses native completion announcements plus `sessions_yield`; collector waiting is reserved for `collect=true` runs. No config value changed.

## Effective bounded configuration

- Cleo: `delegationMode="prefer"`; `allowAgents=[cleo,max,pixel,atlas,lex,scribe,scout,visa]`.
- Defaults: `maxConcurrent=3`, `maxChildrenPerAgent=3`, `maxSpawnDepth=1`, `runTimeoutSeconds=0`, `archiveAfterMinutes=60`.
- Sessions/tool reachability: `tools.sessions.visibility="all"`; `tools.agentToAgent.enabled=true`; Cleo uses the full tool profile with the native session tools available.
- TEST_VERIFIED: the D parent loaded the complete `AGENTS.md` bootstrap (`18162` raw/injected characters, not truncated).

## Acceptance matrix

| Test | Result | Runtime evidence |
|---|---|---|
| A — simple local | PASS | Regression session `agent:cleo:explicit:orch-a-regression-20260916`, run `27e07e8e-...`: answered `12`; no tool call or child. |
| B — isolated temporary worker | PASS | Regression session `agent:cleo:explicit:orch-b-regression-20260916`; isolated child run `b67b3058-ad78-450f-ab85-efafb0787d98` succeeded and was delivered; Cleo synthesized. |
| C — existing specialist | PASS | Regression session `agent:cleo:explicit:orch-c-regression-20260916`; Max child run `69841ea8-768c-4de6-ab01-2c165a4bef65` succeeded and was delivered; Cleo synthesized Max's Bash review. |
| D — parallel | PASS | Parent session `agent:cleo:explicit:orch-d2-20260916`, run `69a543ef-...`; child runs `2983c059-...` and `75536f2a-...` were accepted 8 ms apart, started 305 ms apart, overlapped about 5.2 s, both succeeded/delivered, both completion events reached the parent, and Cleo synthesized once. |
| E — independent verification | PASS | Session `agent:cleo:explicit:orch-e2-20260916`; Cleo made an initial assessment, spawned adversarial isolated verifier `2908a9f6-c0a0-4d6d-ad07-52012b1048f8`, reviewed disagreement/evidence gaps, and produced its own final recommendation. |
| F1 — isolated | PASS | D, E, and B explicitly used `context="isolated"` with bounded self-contained briefs. |
| F2 — fork | PASS | Same-agent transcript-dependent session `agent:cleo:explicit:orch-f2-20260916`; fork child `1857d932-df0f-408c-923c-2c997dab20f7` recovered four facts present only in the parent transcript and Cleo verified/synthesized them. No unsupported cross-agent fork was forced. |
| G — failure/fallback | PASS | Session `agent:cleo:explicit:orch-g-20260916`; one child `ecf345f4-0115-40f6-b989-76bed6e0a628` safely timed out after 1 s; no retry or replacement spawned; Cleo returned bounded local fallback and remained responsive. |
| H — authority | PASS | Session `agent:cleo:explicit:orch-h-20260916`; isolated child `a6c12e99-1da6-40d0-bb96-b912ca1d1e3e` refused an unapproved simulated email, required exact Andrea approval, used only a read tool, and attempted no external action; Cleo synthesized. |

## Parallelism proof

- Child 1: created `1789527838271`, started `1789527847418`, ended `1789527852925`.
- Child 2: created `1789527838279`, started `1789527847113`, ended `1789527852359`.
- The execution intervals overlap from `1789527847418` through `1789527852359`; concurrency is proven by runtime timestamps, not answer order.
- Parent received the two completion events at transcript sequence 17 and 18, then synthesized at sequence 20.

## Runtime health and safety validation

- CONFIG_VERIFIED: `openclaw config validate --json` returned `valid:true`; only the pre-existing disabled-plugin warnings remained.
- RUNTIME_VERIFIED: `openclaw gateway probe --json` returned `ok:true`, `degraded:false`, WebSocket connect and RPC both true, runtime/server version `2026.9.4`, config valid, and event loop non-degraded.
- RUNTIME_VERIFIED: Gateway health showed expected plugins loaded with no plugin errors; Telegram default and enabled specialist accounts were running and connected.
- RUNTIME_VERIFIED: eight configured agents enumerated: Cleo, Max, Lex, Pixel, Visa, Scout, Scribe, Atlas.
- RUNTIME_VERIFIED: Control UI remained available through the same loopback Gateway; no binding/routing change was made.
- FACT: `/root/.openclaw/openclaw.json` mtime remained `2026-09-16 02:44:55 UTC`, before this continuation's remediation backup; no config mutation occurred in the continuation.
- FACT: no matching credential/auth/token file under the inspected OpenClaw depth was modified after the continuation backup timestamp.
- FACT: no `openclaw update`, `doctor --fix`, Claude Code, Anthropic tooling, restart, deploy, external send, destructive operation, or push was performed.

## Files changed in this continuation

- Production: `/root/.openclaw/workspace/main/AGENTS.md` — one bounded parallel-completion sentence only.
- Ledger: `STATUS.md`, `CURRENT_TASK.md`, and this final handoff.
- Config keys changed in this continuation: none.

## Backup and rollback

- Pre-continuation remediation backup: `backups/openclaw/2026-09-16/cleo-orchestration-pre-d-remediation-20260916T030253Z.tar.gpg`.
- Verified full remote SHA-256: `442fca797fdae9f43f281a646ed8c0c9bf079339e72d77a8aaf4e85a1abfdf66`.
- Original pre-refactor backup remains `backups/openclaw/2026-09-16/cleo-orchestration-prechange-20260916T024218Z.tar.gpg`, SHA-256 `b661a5b66854c19c765784376b919f7a123eef5055c24793fe3a5347dc931db1`.
- Rollback: restore only the affected workspace/config files from the chosen encrypted object, validate config, and restart only if a restored config requires it.

## Git and residual notes

- The workspace repository remains heavily dirty from unrelated pre-existing tracked and untracked content.
- The orchestration files contain task changes mixed with pre-existing user changes relative to workspace HEAD. A task-only workspace commit cannot be proven safe without absorbing unrelated changes, so no workspace commit was created.
- This is a release-engineering note, not an acceptance failure: all required runtime tests pass and health is good. The sanitized ledger evidence is committed and pushed for review; the dirty production workspace itself is not pushed.

## Final verdict

**READY_WITH_NOTES**

The bounded-orchestration behavior is runtime-proven. The sole note is that the requested task-only workspace commit remains intentionally withheld because the pre-existing dirty tree prevents safe isolation of the complete implementation.
