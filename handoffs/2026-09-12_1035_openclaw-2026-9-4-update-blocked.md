# OpenClaw 2026.9.4 guarded update blocked before mutation

Date: 2026-09-12
Status: REVIEW_REQUIRED / PENDING_REVIEW
Engineering result: BLOCKED_BEFORE_MUTATION

## Request

Execute an OpenClaw update on the production VPS under the established guarded-update and S3-only recovery policy.

## Execution

Ran `/root/.openclaw/scripts/openclaw-safe-update.sh --check latest` from the healthy 2026.9.3 runtime. This performs config, service, health and update-status preflight, resolves the exact candidate, and invokes the official updater dry-run before any backup or mutation.

## Evidence

- CONFIG_VERIFIED: preflight configuration validation passed.
- RUNTIME_VERIFIED: preflight required the user Gateway to be active and healthy.
- TEST_VERIFIED: update status resolved registry candidate 2026.9.4 for a package/npm installation.
- TEST_VERIFIED: official updater dry-run refused with package-manager owner unknown and explicitly reported no changes.
- TEST_VERIFIED: guarded result was `MANUAL_REVIEW_REQUIRED` with update blocked before mutation, Doctor not run, restart not run, rollback not attempted, and current runtime unchanged.
- SOURCE_VERIFIED: the installed 2026.9.3 update runner Doctor policy contains `fix: true`; bypassing the guard could therefore invoke Doctor repair without a reviewed exact delta.
- RUNTIME_VERIFIED: OpenClaw remained 2026.9.3 and the Gateway remained active/running on the preflight PID.

## Safety outcome

No update package was installed. No local backup archive or database dump was created. The backup phase was not reached because the official dry-run failed first. No Doctor, restart, config change, plugin repair, routing change, or database mutation occurred.

## Blocker and next authority

The isolated installation is not owned by a recognized active npm/pnpm/Bun global shim. Proceeding requires a separately reviewed installation/migration method and an exact preview/approval of any Doctor repair delta. The existing wrapper must not be bypassed merely to force 2026.9.4.

## Review request

Confirm the classification as blocked before mutation and whether a follow-up should adapt the isolated installation transaction while preserving direct encrypted S3 backup, source acceptance, Node compatibility, rollback constraints, and explicit Doctor-delta approval.
