# Source and lifecycle acceptance

## Provider snapshot lifecycle (FACT)

Installed OpenClaw 2026.9.2 `runtime-snapshot-BaQikjTR.js`:

- Lines 27-32: module-scoped snapshot, source, metadata and revision variables.
- Lines 53-61: createRuntimeConfigSnapshotMetadata increments revision and constructs a fresh object.
- Lines 62-70: setRuntimeConfigSnapshot publishes config/source and assigns newly constructed metadata.
- Lines 81-85: source-only publication calls setRuntimeConfigSnapshot, even when the runtime config object is reused.
- Lines 87-98: reset clears the metadata to null and revision to zero.
- Lines 99-107: getters return stored config/source/metadata directly, without cloning.

The metadata identity assumption was correct for this exact implementation. Actual-module tests prove stable identity across reads, replacement on publication/source-only publication, and reset. However, publication does not freeze configuration objects. An actual-module-backed reproduction shows the prior identity cache incorrectly returning true after an in-place credential change without publication.

The final mitigation removes persistent result caching. It compares canonical structure directly, following stableConfigStringify semantics for supported acyclic configuration data: object key order is irrelevant, array order and sparse slots matter, and scalar JSON/null normalization is preserved. Missing providers remain false. Every call resolves both providers anew; no result survives mutation, replacement or publication and no cache can grow. Unlike the first attempted strict-equality fast path, unequal configurations do not trigger repeated full serialization/hashing.

Sixteen regression groups run against the actual installed distribution and real snapshot publisher/getters. They include 1000 generated differential cases, scalar normalization and sparse arrays. The previous identity-cache mutation bug is reproduced in an isolated VM with the actual resolver/hash/lifecycle dependencies. Packaged upstream test files for these modules are absent; the full upstream Vitest suite was not available or claimed as run.

An initial stateless strict-equality fast path passed equivalence tests but failed startup performance acceptance because negative comparisons still hashed the complete provider. That candidate was superseded by the attached canonical structural comparator. This required a second controlled restart attempt during this task; the final generation is reported separately, with no claim of a single total restart.


## Lex transport (FACT)

Authored intent remains `agents.entries.lex.params.maxOutputTokens = 16384`.

- `@openclaw/ai/dist/transports.mjs:1171-1185` accepts only maxTokens, max_completion_tokens and max_tokens. The actual resolver returns undefined for Lex's authored key, and 16384 for maxTokens.
- `extra-params` invokes that resolver and forwards the supported result as streamParams.maxTokens.
- The actual native-route resolver reports false for Lex's Anthropic primary and DeepSeek fallback, true for its OpenAI GPT-5.6 Sol fallback.
- `codex-route-warnings-BVqoTxlz.js:1905-1961` scans those native routes and explicitly identifies unrepresentable authored transport parameters. It states migration requires changing behavior or runtime.

Consequently the authored 16384 cap is not currently effective through the ordinary token-limit resolver; native Codex also has no equivalent supported authored request cap. maxTokens is a supported alternative on the OpenClaw transports only, not a behavior-preserving all-route migration. Changing the native fallback runtime would change the accepted routing/auth architecture. No key was silently deleted or reinterpreted. The warning is accepted as non-actionable within this task's routing-preservation constraint; this is not a claim that the 16384 cap is enforced.

## Max provenance and semantics (FACT / INFERENCE)

The workspace AGENTS and TOOLS entries both linked into Max's own legacy agent directory; TOOLS did not target another specialist or shared global file. This layout predates the current update. Its role as a compatibility view onto one Max-owned source is inferred from those matching paths, not from a recovered original creation command.

The original workspace TOOLS symlink was archived intact, not dereferenced or blindly repaired. Its original content was merged exactly once into the canonical AGENTS Tools section, with the obsolete instruction to edit TOOLS redirected there. The workspace AGENTS alias remains. The old agent-directory TOOLS pathname is a compatibility symlink to AGENTS, so it cannot become a divergent source. All archived and active aliases resolve. Private instruction text stays solely in the protected local rollback directory.

Native 2026.9.2 migration code requires an unlinked regular workspace TOOLS file, merges customized notes into AGENTS and archives the old entry. The final layout follows that convention while preserving the existing canonical Max directory and workspace alias. The resulting AGENTS is about 7.4 KiB and below the configured per-file bootstrap limit.
