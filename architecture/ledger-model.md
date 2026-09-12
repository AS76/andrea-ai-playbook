# Handoff Ledger Architecture

## Roles

```text
Andrea (final authority)
  -> Codex (execution and runtime verification)
  -> GitHub Handoff Ledger (sanitized engineering evidence)
  -> ChatGPT (independent review, no claimed runtime access)
  -> verdict / evidence request
  -> Codex remediation and runtime verification
```

ClawMem remains semantic working memory. The Obsidian Vault remains canonical
human-readable knowledge where applicable. The ledger contains neither layer's
full content.

## Evidence Classes

- `CLAIMED`: stated without independent evidence.
- `CONFIG_VERIFIED`: configuration parsed or inspected.
- `TEST_VERIFIED`: an identified test executed successfully.
- `RUNTIME_VERIFIED`: checked against the running production system by Codex.
- `UNVERIFIED`: evidence is unavailable or insufficient.

ChatGPT reviews the recorded evidence and diff. It does not convert a claim into
runtime verification merely by approving it.

## State Machine

```text
RUNNING -> REVIEW_REQUIRED -> APPROVED -> COMPLETE
                    |-> CHANGES_REQUESTED -> REMEDIATION -> REVIEW_REQUIRED
                    |-> BLOCKED -> evidence collection -> REVIEW_REQUIRED
```

Significant tasks close only after runtime PASS, a committed Git state, and a
ChatGPT verdict of APPROVED or APPROVED_WITH_NOTES with no unresolved critical
or major findings.

## Review Transport

- Direct mode: an authorized reviewer adds a new file under `reviews/`.
- Relay mode: Andrea provides the review and Codex imports it faithfully.

Every new review cycle creates a new file. Published history is never rewritten.
