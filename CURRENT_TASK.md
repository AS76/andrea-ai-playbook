# CURRENT TASK

Request: surgically refactor Cleo's orchestration layer so Cleo chooses among local work, existing specialists, bounded isolated temporary workers, limited parallel work, and independent verification while retaining final synthesis ownership.

Overall status: REVIEW_REQUIRED
ChatGPT Review: NOT_STARTED
Engineering acceptance: PASS — A-H complete, including F1 and F2

Scope: active Cleo workspace orchestration instructions and only the supported OpenClaw 2026.9.4 sub-agent controls required to bound Cleo's native spawning. No model, provider, credential, Telegram/channel, memory architecture, permanent-agent, package, or unrelated runtime changes.

Discovery: active agent id `cleo`; workspace `/root/.openclaw/workspace/main`; agent directory `/root/.openclaw/agents/cleo/agent`; active workspace bootstrap includes AGENTS.md, SOUL.md, USER.md, IDENTITY.md and runtime-selected memory/context. Existing policy duplicates delegation-first rules in AGENTS.md and SOUL.md, including an arbitrary two-tool cutoff. No configured Manager agent exists.

Planned config delta: Cleo-specific `subagents.delegationMode=prefer`, add `cleo` to Cleo's existing specialist allowlist, set `maxConcurrent=3`, `maxChildrenPerAgent=3`, and `maxSpawnDepth=1`. Preserve model routing and all unrelated bytes.

Rollback: S3 object `backups/openclaw/2026-09-16/cleo-orchestration-prechange-20260916T024218Z.tar.gpg`, SHA-256 `b661a5b66854c19c765784376b919f7a123eef5055c24793fe3a5347dc931db1`; restore only listed files after remote download/decryption, validate config, then restart only if the config restore requires runtime reload.

Current evidence: A-C passed again without regression. D proved two children overlapped and Cleo collected both before one synthesis. E proved adversarial independent verification. F1 proved isolated work and F2 proved a legitimate same-agent transcript fork. G proved bounded timeout fallback without retry storm. H proved delegated authority did not expand.

Handoff: `handoffs/2026-09-16_0330_cleo-bounded-orchestration-final.md`.

Next action: independent ChatGPT evidence review. The workspace commit is intentionally withheld because the heavily dirty pre-existing tree prevents proving a complete task-only commit without absorbing unrelated user changes. Do not push.
