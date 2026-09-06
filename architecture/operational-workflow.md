# Persistent Codex Review Workflow

This is the operational policy referenced by the VPS-level Codex instructions.
It extends the existing ledger without creating another memory mechanism.

## Applicability

Use the ledger automatically for significant production, architecture, security,
database, storage, migration, incident, automation, agent-routing, MCP, model,
Gateway, ClawMem or Vault work. Do not use it for conversation, inspection-only
work, trivial commands, typo fixes or minor documentation changes.

## Task lifecycle

1. **Start:** update `STATUS.md` and `CURRENT_TASK.md`; set overall state to
   `RUNNING`; record request, objective, scope, initial state and plan.
2. **Execute:** keep detailed semantic/session context in ClawMem. Add only
   material discoveries and sanitized engineering evidence to GitHub.
3. **High risk:** record intended change, affected component, backup and rollback
   before mutation. Emergency priority is data protection, stabilization,
   runtime verification, documentation, then review.
4. **Verify:** distinguish `FACT`, `INFERENCE`, `CONFIG_VERIFIED`,
   `TEST_VERIFIED`, `RUNTIME_VERIFIED` and `UNVERIFIED`.
5. **Handoff:** create or update a timestamped handoff with files, configuration,
   tests, runtime evidence, risk, rollback, remaining work and review request.
6. **Publish:** run `tools/codex-handoff verify` and
   `tools/codex-handoff secret-scan`; inspect the diff; commit; push normally;
   and use `tools/codex-handoff heads --pr NUMBER` where a PR exists.
7. **Review:** set `REVIEW_REQUIRED` / `PENDING_REVIEW`. The current PR head is
   authoritative. Tell Andrea only: “Ready for ChatGPT review. Tell ChatGPT:
   Controlla il ledger di Codex.”

## Verdict handling

- `APPROVED`: validate task, PR and exact reviewed SHA; preserve the review;
  record any later closure commit separately; validate, scan, commit and push
  closure metadata; set `COMPLETE` / `APPROVED`.
- `APPROVED_WITH_NOTES`: close unless a note is explicitly blocking; preserve
  notes and set `COMPLETE` / `APPROVED_WITH_NOTES`.
- `CHANGES_REQUESTED`: preserve the review; implement every required action;
  rerun affected tests/runtime verification; document, commit, push and return
  to `PENDING_REVIEW`. Tell Andrea only: “Remediation complete. Tell ChatGPT:
  Ricontrolla il ledger di Codex.”
- `BLOCKED`: preserve the review; collect exactly the missing VPS evidence;
  document, commit, push and return to `PENDING_REVIEW`. It is insufficient
  evidence, not an implementation failure.

The newest filename is not enough to establish applicability. Validate its
reviewed PR, exact commit, related handoff/task and place in review history.

## Commit identity

- Implementation commit: contains the implemented change.
- Reviewed PR head: exact commit evaluated by ChatGPT.
- Remediation commit: addresses a preserved review finding.
- Closure commit: later administrative commit recording an accepted verdict.

A closure commit after the reviewed commit is expected. Before review, in-tree
active fields use the current PR-head ref and the PR description records its
resolved exact SHA after push. After review, `Reviewed Commit` records the exact
approved SHA and `Closure Commit` records the later metadata commit/ref.

## Review transport

ChatGPT approval and GitHub-native PR approval are distinct. When GitHub rejects
self-approval with HTTP 422, record:

```text
ChatGPT Review: APPROVED
GitHub Native Approval: NOT_APPLICABLE_SELF_REVIEW
Transport Limitation: GitHub HTTP 422 self-approval restriction
```

Never represent this as a GitHub-native approval.

## Security and separation

ClawMem retains detailed semantic/session context. GitHub contains only
sanitized execution, evidence and review records. Never commit credentials,
tokens, cookies, private keys, raw environment files, memory dumps, private
correspondence or unnecessary personal data. A detected secret stops the push;
an already-published secret becomes a security incident.
