# CODEX FINAL REMEDIATION AND ACCEPTANCE

## Metadata

Date: 2026-09-06T05:30:00Z
Host: production-vps
Component: OpenClaw 2026.9.2 recovery
Acceptance Verdict: PASS_WITH_ACCEPTED_WARNINGS
Runtime Verification: PASS_WITH_ACCEPTED_WARNINGS
ChatGPT Review: PENDING_REVIEW
Current Commit: PR `#1` HEAD (`refs/pull/1/head`)
Reviewed Commit: PR `#1` HEAD (`refs/pull/1/head`)
Previous review target: `60e9833570173b06e7564fd6bf9374a129d607da`
Branch: `codex/handoff-ledger`
Repository: `AS76/andrea-ai-playbook`
Related task: `CURRENT_TASK.md`

The PR description records the resolved exact SHA after the normal branch push; in-tree HEAD fields intentionally use the current PR ref to avoid a self-referential commit hash. This is operational acceptance, not a claim of independent ChatGPT approval.

## Request and initial state

Resolve the reviewed cache assumption, Max migration, Lex token parameter, plugin drift and update-safety lifecycle; then verify production from the final generation. Core 2026.9.2 was serving with the previous local identity cache, a Max migration ERROR, a Lex warning and eight enabled official plugins pinned to 2026.9.1.

## FACT: provider lifecycle and correction

The actual snapshot getter returns the module-scoped metadata object directly. Every publication constructs new metadata and increments revision; source-only publication also republishes; reset clears the object and resets revision. Exact source locations and tests are in `lifecycle-and-lex.md` and `provider-regression.mjs`.

The reviewed metadata identity assumption was correct. A separate defect was reproduced: configuration objects are not frozen, and an in-place credential mutation without publication left the old cached true result valid incorrectly. The final mitigation removes retained result caching entirely and directly compares the canonical structure using the same scalar/object/array rules as stableConfigStringify for supported acyclic configuration data. It does not weaken credential comparison, skip provider resolution or retain results across mutations/publications. It has no cache growth.

An initial stateless strict-equality fast path preserved correctness but still hashed negative comparisons and failed startup performance acceptance. That candidate is superseded. The final canonical comparator passed 16 regression groups against actual distribution modules, including metadata identity/publication/reset, prior-bug reproduction, mutation without publication, replacement, multiple/missing providers, scalar normalization, sparse arrays and 1000 generated differential cases. A 100-comparison equivalent-config benchmark measured 61.7ms upstream hashing versus 5.7ms direct comparison in one sample; this is a local benchmark, not a general performance guarantee.

## FACT: Max migration

Before: workspace TOOLS.md linked to `/root/.openclaw/agents/max/TOOLS.md`; workspace AGENTS.md linked to the corresponding Max AGENTS file. These point to Max's own legacy directory, not another agent's shared tool instructions. The compatibility purpose is inferred from the layout; the historical creation command was not recovered.

After: original tool notes are retained exactly once under the canonical AGENTS Tools section. Workspace AGENTS alias remains; the workspace legacy TOOLS symlink was archived intact. The old agent-directory TOOLS path now aliases AGENTS, so it cannot diverge. Original files and symlink are in protected rollback storage. No broken alias or duplicate independent source remains. The resulting file is about 7.4 KiB, below the configured 80,000-character per-file limit. Final lint no longer reports the Max ERROR. Private instruction text is not in GitHub.

## FACT: Lex accepted warning

`agents.entries.lex.params.maxOutputTokens=16384` remains unchanged. The actual ordinary transport resolver accepts maxTokens/max_completion_tokens/max_tokens, not this authored spelling, and returns no limit for Lex's current key. maxTokens is an alternative only for OpenClaw transports. The actual native-route resolver selects OpenClaw for Anthropic/DeepSeek and native Codex for the OpenAI fallback; the native route has no supported equivalent authored request cap. The doctor explicitly says automatic migration changes behavior/runtime.

The 16384 cap is therefore NOT claimed as enforced. Renaming it would newly enforce a limit on some routes while still not supporting the native fallback; changing that fallback runtime violates the routing-preservation scope. No intent was silently deleted, no unsupported equivalent invented, and the one remaining lint warning is accepted on that basis.

## FACT: official external plugin coherence

`plugin-matrix.json` records every installed official external package, old/final versions, exact dependency pin, release availability, enablement, contract/schema checks, official repository and registry integrity verification.

| Plugins | Final version | Decision |
|---|---|---|
| Brave, DeepSeek, Lobster, Mistral, Moonshot, Perplexity, Slack, Voyage | 2026.9.2 | Updated individually to exact pins; capability contracts and plugin config schemas unchanged; catalog/icon/help changes inspected; no forced acceptance |
| Codex | 2026.9.2 | Already current; registry manifest matches |
| Discord | 2026.5.27, disabled | 2026.9.2 has channel schema and transcript capability changes; no active configured channel requires this migration |
| WhatsApp | 2026.5.27, disabled | 2026.9.2 introduces tool/skill/state-migration contracts and extensive channel schema changes; dormant configuration preserved |

All eleven candidate 2026.9.2 tarballs match registry SHA-512 integrity. All nine enabled official external plugins are now 2026.9.2 and registry diagnostics are empty. Bundled plugins follow core 2026.9.2. Local non-official plugins were not upgraded. No enabled official plugin remains on 2026.9.1.

## FACT: final-generation acceptance

- Exact core version: 2026.9.2 (`3928bad`). Authenticated server build: `2026.9.2-release-3928bad9badf-2026-09-05T15-22-41.651Z`.
- Final generation started 05:22:47 UTC and declared ready 05:23:30.106 UTC (43.1s). Systemd active/running, NRestarts=0, loopback port 18789, Recv-Q=0.
- Authenticated operator.read RPC passes; service config audit passes.
- Local HTTP 30/30 success, maximum 894.4ms while acceptance diagnostics ran. Public Funnel HTTP 3/3 success. Event loop not degraded: sampled p99/max delay 23.6ms, utilization 0.023.
- After diagnostics, 30s resource sample: mean CPU 4.57%, mean RSS 1,092,011 KiB (about 1.04 GiB).
- Final-generation journal scan: no delayed heartbeat, starvation, WS1006 or crash loop observed. This is a bounded observation, not a long-duration reliability guarantee.
- Telegram 11/11 configured accounts running, connected, polling, probe healthy and no current errors.
- No qualifying passive delivery appeared after the final restart during the initial observation. One isolated active Cleo E2E test was therefore run under the acceptance request: OpenRouter Auto Router produced the expected fixed marker and Telegram deliverySucceeded=true in 7.331s. The destination was the existing default account's recent delivery peer, checked against that account's allowlist. No recipient identity, prompt context or transcript is published. This is ACTIVE E2E evidence, not passive evidence.
- Config validate passes; doctor exits 0; lint exits 1 with only the accepted Lex warning and no ERROR. Doctor's non-repair notices and the pre-existing disabled-plugin residual config warnings are not represented as a perfectly clean doctor run.

## FACT: routing and configuration preservation

Main openclaw.json remained byte-identical throughout the task. The actual target-model resolver was tested for all twelve configured agents: each inherits its own primary when selected; no global child model exists. Cleo/Scout/Tutor remain OpenRouter Auto Router; Worker retains DeepSeek Flash with Gemini fallback; all specialist primaries/fallbacks remain unchanged; no Qwen fallback was restored. Hermes remains OpenRouter Auto Router with DeepSeek Flash fallback, and its config bytes are unchanged. No model, auth profile, token, provider endpoint or routing configuration was edited.

## Update-safety mechanism

- `/root/.openclaw/scripts/openclaw-provider-mitigation-check.py` is read-only and compares the package version, exact provider module and its actually imported lifecycle module against reviewed hashes.
- Known unmitigated 2026.9.2 source returns FAIL_MITIGATION_MISSING. Unknown version/structure/hash returns REVIEW_REQUIRED_SOURCE_CHANGED. Inspection errors fail closed. No candidate code is executed and no patch is ever applied by the checker.
- Reviewed upstream fixes have a separate explicit allowlist; its current production list is empty. A future fixed release must be inspected/diffed and tested before adding its exact source token, at which point the gate reports PASS_UPSTREAM_FIXED_NO_LOCAL_PATCH. No unknown upstream code is heuristically called fixed.
- The guarded updater calls this gate after package update and returns failure before claiming acceptance if source is missing/unknown.
- A systemd ExecCondition checks the same source before future Gateway starts, including starts after an unguarded package replacement. Exit 1 skips startup without a restart loop. The drop-in was loaded after the final start; the source had already passed the direct pre-start gate. Equivalent isolated systemd tests prove approved source executes the main command and unknown source skips it. No third Gateway restart was introduced merely to test the condition.
- Guard unit tests cover approved local, missing mitigation, reviewed upstream fix fixture, changed lifecycle/source and no-write behavior. The upstream-fixed case is a test fixture, not a claim of an available production upstream fix.

## Restart deviation

Two task restart attempts were required, rather than the requested single attempt. The first candidate failed performance acceptance; it was stopped through normal systemd shutdown and superseded. No forced termination was needed in this task. Only the second generation supplies final acceptance. This deviation is retained explicitly rather than hiding the failed candidate or claiming first-attempt success.

## Files and rollback

Protected local rollback root: `/root/.openclaw/update-runs/final-acceptance-20260906T050909Z`.

Changed runtime files: provider comparison module; Max canonical AGENTS plus TOOLS compatibility/retired workspace entries; eight plugin install records/generations; guarded updater; checker and policy files; systemd `25-provider-source-acceptance.conf` drop-in. No main config or Hermes changes.

Rollback preserves user data:

1. For Max, restore backed-up AGENTS and original TOOLS bytes, move the compatibility alias aside, and restore the archived workspace symlink. Do not merge duplicate note copies.
2. Plugin rollback uses the exact previous package pins through the normal plugin manager, with the retained old generations available. The protected SQLite snapshot is forensic backup; do NOT restore the whole live state database over newer sessions or credentials.
3. Source/wrapper originals are in the protected root. Reverting to the previous cache reintroduces its documented mutation defect; do so only as an explicit emergency rollback. Coordinate the source guard/policy with any reviewed rollback so the next start does not incorrectly claim acceptance.
4. To remove this task's future-start guard, archive its added drop-in and checker/policy, restore the saved updater, daemon-reload and perform a controlled restart only when needed. No deletion of user data is required.

## Remaining accepted risks and review

- Lex's authored cap is not enforced; a cross-runtime equivalent does not exist in this release.
- Two disabled legacy channel plugins remain deferred because their upgrades change capability/schema semantics.
- The local comparison mitigation is release-specific. The guard deliberately blocks unfamiliar source pending review; operators must inspect an upstream change before accepting it.
- Correctness is tested for supported acyclic configuration data, including valid in-place mutations. Arbitrary cyclic/accessor-bearing plugin-created objects are outside the supported configuration domain.
- Full upstream Vitest test sources are absent from the installed npm distribution; actual installed-module regression tests were run instead.
- Long-duration reliability and all model/provider execution paths are not proven. Final health, routing resolution and one real Cleo E2E are proven.

Review the current PR head, source equivalence semantics, migration preservation, accepted Lex limitation, plugin matrix, source guard behavior and final-generation evidence. Prior reviews/handoffs remain immutable. Ledger verify and secret scan must pass before normal branch push; local/remote/PR heads must agree afterward.
