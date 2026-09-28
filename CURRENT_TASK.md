# CURRENT TASK

Request: retry the FindMy scraper authentication after the owner signed in interactively, then tell him what he has to do on his side.

Overall status: REVIEW_REQUIRED
ChatGPT Review: NOT_STARTED
Engineering acceptance: PASS — implementation, sandbox suite and runtime verification complete; the upstream Apple blocker stays open

Scope: the Hermes-owned cron wrapper `/root/.hermes/scripts/icloud-findmy-scraper.sh` and its `state.env`. No credential change, no session destruction, no interactive re-authentication, no cadence change, and no portal, database, cron-schedule, unit or Apple-side action.

Discovery: the wrapper was in `MODE=halted`, a state that previously meant "stopped until a human notices", so a flag that lifts on Apple's side stayed invisible and could only be cleared by the owner telling the agent to retry. The state file is sourced by bash, which makes any value containing an unquoted space unsafe.

Planned delta: in `halted`, attempt one probe every `ICLOUD_SLOW_PROBE_SECS` (default 21600 s) instead of never; resume the normal cadence automatically on success; alert on recovery and on a changed error signature only; add `LAST_PROBE_TS` and `LAST_SIG`; require exit code 0 on the recovery path in addition to marker detection. Preserve the existing stop-at-first-anomaly, one-probe-then-halt and cooldown behaviour byte for byte.

Diagnosis: Apple returns HTTP 403 code `-20209` to the automated password authentication path on two independent attempts, including a session-free clean login, while the account stays usable interactively and delivered no lock notification. The stored credentials authenticated 482 consecutive cycles up to five minutes before the failure, so the credential set is good and the flag is scoped to the automated path from this host.

Rollback: `/root/.hermes/backups/scripts/icloud-findmy-scraper.sh.bak-20260928-053359-pre-slow-probe` and `/root/.hermes/backups/scripts/state.env.bak-20260928-053359-pre-slow-probe`. The previous behaviour was fail-safe, so rollback only restores the need for manual recovery.

Evidence: sandbox suite 11 scenarios / 32 assertions at 0 failures with no Apple calls; production wrapper with the real state file exits immediately with a tripwire in place of the scraper; `state.env` sources cleanly; `bash -n` clean; cron entry unchanged.

Handoff: `handoffs/2026-09-28_0730_findmy-guard-halted-slow-probe.md`.

Next action: independent evidence review. Open decisions left with Andrea: the cadence reduction (5 to 15 minutes) once Apple reopens, and whether to revisit the design if the flag recurs.
