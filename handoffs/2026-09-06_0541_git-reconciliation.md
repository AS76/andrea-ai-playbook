# Git reconciliation and acceptance provenance

Date: 2026-09-06
Scope: repository only. No production changes, probes, restarts or memory writes.

## Refreshed facts

- origin/main: `9d575348b80485647b6fc9a0369b3da9f4f3fa1b`.
- Initial local and origin/codex/handoff-ledger: `47fb3826c21f22d4c69d0fc2a3ad53acfb1e1d1e` (the accepted commit itself).
- Merge-base: `3afe11026dc684d7200acee7e010c0fe84930b50`.
- Initial GitHub PR #1 head: accepted SHA above; base ref main, API initially exposed base SHA `3afe11026dc684d7200acee7e010c0fe84930b50`; mergeable=false, mergeable_state=dirty, open. The fetched main ref was newer than that initial PR base snapshot.
- Operation: `git merge --no-ff --no-commit origin/main`, followed by manual resolution and a normal merge commit/push. Both histories remain ancestors; no reset or force push.
- Sole conflict: README.md. Retained the ledger introduction, workflow/authority/security guidance and all main playbook sections, links and configuration caveat. No whole-file ours/theirs selection.

## Semantic equivalence vs accepted engineering commit

All pre-existing files except README.md, STATUS.md and CURRENT_TASK.md are byte-identical to the accepted tree. This includes every handoff, review, evidence artifact, regression test and source guard. The validator emits SHA-256 evidence for every preserved file. This is stronger than keyword-only comparison: all engineering claims, negative findings and limitations survive verbatim.

Specifically preserved: OpenClaw 2026.9.2 (3928bad), PASS_WITH_ACCEPTED_WARNINGS; final Gateway generation, Telegram 11/11, HTTP/RPC/event-loop and active Cleo E2E; mutation-safe stateless canonical comparison with no retained result cache, regression evidence and fail-closed source guard without automatic patching; Max canonical AGENTS ownership and resolved migration ERROR without divergent TOOLS; Lex authored maxOutputTokens=16384 intent and explicitly unenforced accepted limitation; nine enabled official plugins at 2026.9.2 and disabled Discord/WhatsApp deferral; unchanged Routing V2, no global child override, Auto Router for Cleo/Scout/Tutor, specialist inheritance, Worker, no Qwen restoration and unchanged Hermes.

FACT: committed evidence is preserved. No inference of newly measured production health is made. ChatGPT review is user-supplied independent evidence review of the exact accepted SHA, not direct VPS inspection or approval of this later merge metadata.

## Complete substantive differences from accepted tree

- README.md: main updates the former v4.3 title to Operating Repository v5.0. Seven pre-existing broken main links were resolved: dashboard points to actual root index.html; six absent planned documents remain explicit path references marked not present, without inventing their contents. The planned tree is labeled accordingly. It combines both valid introductions and main's playbook navigation, policy links and historical configuration disclaimer.
- CHANGELOG.md, docs/architecture.md, policies/vault-schema.md: exact new main blobs preserved; documentation only. Their presence does not apply any policy/configuration to production.
- STATUS.md and CURRENT_TASK.md: current Git-only task, historical production acceptance and completed independent review are explicitly separated; supersede the former pending-review status without rewriting historical handoffs.
- New review: `reviews/2026-09-06_0541_openclaw-acceptance.md`, exact target 47fb3826..., protocol APPROVED_WITH_NOTES / engineering PASS_WITH_ACCEPTED_WARNINGS.
- This handoff and `evidence/2026-09-06-git-reconciliation/`: append-only reconciliation provenance, integrity/reference/review checks and their results.

## Validation and final identity

Repository verify, secret scan, state transitions, latest review, policy check, relative Markdown links, unique/nonconflicting review targets, historical blob identity, main blob identity, Git whitespace and conflict-marker checks are required before push. Results are recorded in the adjacent evidence directory. Existing runtime regression files are preserved, not re-executed against production for this Git-only task.

Closure Commit: PR #1 HEAD after normal push; exact SHA is resolved in the PR description and final acceptance report, avoiding a self-referential in-tree hash. Remote/local/PR equality and recalculated GitHub mergeability are checked after push. PR remains open; workflow does not require automatic merge. Production review target remains the exact accepted SHA, distinct from this Git closure commit.

## Rollback and accepted limitations

Both merge parents and the complete accepted commit remain reachable. If reconciliation metadata later needs correction, use a new corrective commit; do not reset published history or delete evidence. No runtime rollback is necessary because no runtime operation occurred.

Accepted engineering risks remain Lex's unenforced cap, disabled legacy channel migrations and the release-specific local mitigation lifecycle. The historical bounded health observation and absent full upstream Vitest distribution remain disclosed. No new engineering acceptance is inferred from Git mergeability.
