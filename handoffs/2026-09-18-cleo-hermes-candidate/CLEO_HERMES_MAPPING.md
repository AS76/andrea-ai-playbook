# Mapping and technical findings

## Verified current state (2026-09-18)

- Installed Hermes Agent v0.21.3 (2026.9.14), git `e83b1d51`; default profile is active, worker is another profile. `HERMES_HOME` for default is `/root/.hermes`. Gateway service is active. This does not prove messaging delivery or tool reliability.
- Current default model is `openrouter/auto` via OpenRouter, with a configured DeepSeek fallback. Downstream AutoRouter choice is opaque. `display.personality` is empty. Current memory write approval is false; Honcho is configured as external memory provider.
- Current relevant files: `config.yaml`, `SOUL.md`, `memories/USER.md`, `memories/MEMORY.md` in default home. Baseline SHA-256 values are in CHANGELOG.md. Active files were read only.

## Native layer mapping

Before assigning files, the source material separates into four buckets: **A identity** (voice, calm competence); **B relationship** (familiarity, rapport, direct challenge); **C operating principles** (evidence, agency, proportionate initiative, repair); **D OpenClaw implementation** (agent routing, hooks, plugin and session syntax). A and B drive SOUL; only stable, general parts of C belong there. D stays out.

| Cleo material | Hermes layer | Decision |
|---|---|---|
| Identity, voice, warmth, disagreement, repair | Profile `SOUL.md` | Candidate file, concise and durable. |
| Stable interaction preferences | Profile `memories/USER.md` | Small seed, review before installation. |
| Verified learned facts | Profile `memories/MEMORY.md` | Empty initially; approved writes only. |
| Project conventions, coding, GitHub, OpenClaw rules | Project `AGENTS.md` or `HERMES.md` | Existing project files govern; no global copy. |
| Session-specific modes | `/personality` overlay | Not needed for normal Cleo-like conversation. |
| OpenClaw agent names, routing, hooks, sessions | None | Excluded from persona. |

## Official and installed behavior

- SOUL is read from the profile's `HERMES_HOME`, placed once in the identity slot, and subject to scanning and context-file truncation. A temporary personality overlay is separate. [Official personality guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/personality).
- USER and MEMORY are bounded at 1,375 and 2,200 characters in current docs and installed config/tool; writes can be approval gated. Their prompt snapshots freeze at session start. Messaging conversations may persist across restarts, so a new session boundary matters. [Official memory guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory).
- Project context files have precedence and discovery rules; a startup file is capped dynamically with a 20,000-character floor and 500,000-character ceiling unless `context_file_max_chars` is set. Source check: `agent/prompt_builder.py` in installed git `e83b1d51`. [Official context guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files).
- Profiles isolate config, credentials, memory, sessions, skills, cron and gateway state. `--clone` copies curated memories and credentials but omits messaging channels and cron; a fresh profile lacks current tool/credential wiring. A future isolated installation must deliberately preserve needed capabilities without sharing a messaging token. [Official profiles guide](https://hermes-agent.nousresearch.com/docs/user-guide/profiles).
- Bot Mode adds a persistent named chat and permits a per-Bot model pin; it is a presentation of a profile, not the identity layer. [Official Bot Mode guide](https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode).

## Conflicts and limits

The old Hermes SOUL explicitly positions Hermes as terse and Cleo as warmer. The proposed persona changes that relationship framing **only inside a future isolated profile**. The current USER and MEMORY files are near their limits and contain unrelated material; they must not be cloned wholesale. The current model is AutoRouter, which prevents a controlled prompt-only comparison. Recommend Andrea approve one exact model pin before evaluation, using the model presently selected for normal Hermes if it can be observed reliably. Otherwise record the first trial as exploratory, not controlled. No model or provider is changed in this stage.

The archived OpenClaw frameworks conflict with current Cleo delegation policy (old time thresholds and unsafe repair advice). They are historical evidence only. The official website and installed v0.21.3 docs agree on the mechanisms above; no material difference was found in those checked paths. This is not a full code audit of all gateway and Honcho internals.

One cross-layer caveat matters: the documented built-in memory approval gate does not cover Honcho's own automatic transcript sync. Installed Honcho documentation says `saveMessages: false` skips its automatic writes and that profiles sharing a workspace can see shared identity/memory. Candidate Honcho scoping and consent are therefore a separate installation gate, not solved by `memory.write_approval`.

## Prompt pressure review

SOUL has five short paragraphs and no task-specific routing, credential, or file-path rules. It uses one correction principle and one uncertainty principle. Risks: the phrase “collega fidata” could be overplayed as intimacy; “prendi iniziativa” could be overread as broad autonomy; emotional guidance could become a canned acknowledgment. Acceptance tests target those failure modes. The model may still produce generic empathy or excessive progress messages despite the prompt.
