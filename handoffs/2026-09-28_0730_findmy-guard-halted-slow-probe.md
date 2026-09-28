# FindMy scraper guard: autonomous slow probe inside `halted`

Date: 2026-09-28
Status: REVIEW_REQUIRED / PENDING_REVIEW
Engineering result: IMPLEMENTED_AND_TESTED / UPSTREAM_BLOCKER_OPEN

## Request

Andrea asked (Telegram, 2026-09-28 07:22 CEST) what he had to do about the FindMy portal, then "Riprova ora" at 07:32 CEST after signing in interactively. The scraper had stopped delivering positions at 07:10 CEST and the guard had alerted him twice.

## Initial verified state

- RUNTIME_VERIFIED: the wrapper `/root/.hermes/scripts/icloud-findmy-scraper.sh` was in `MODE=halted`; in that mode it returns before invoking the scraper, so no Apple authentication was attempted after 05:20:31Z.
- RUNTIME_VERIFIED: `/root/.hermes/logs/icloud/events.log` held a continuous clean series `event=ok` from 2026-09-26T13:00:11Z to 2026-09-28T05:05:31Z: 482 cycles, 350 of them in the last 24 h. The only non-ok entries were the anomaly at 05:10:31Z, a cooldown skip at 05:15:31Z and a failed probe at 05:20:31Z.
- RUNTIME_VERIFIED: one single session-free pyicloud login (no stored cookie jar at the default directory) returned HTTP 403 with Apple code `-20209`, message "This Apple Account has been locked for security reasons. Visit iForgot to reset your account"; pyicloud surfaced it as `PyiCloudFailedLoginException: Invalid email/password combination`.
- RUNTIME_VERIFIED: Andrea reported that the interactive sign-in path (iForgot / Apple ID panel) lets him in without any unlock or verification request, and that no application tells him the account is blocked.
- FACT: no Apple security or lock notification arrived in the account mailbox in the preceding three days.
- RUNTIME_VERIFIED: the portal answered HTTP 200 on the tailnet bind; last stored position 2026-09-28T05:01:28Z, last successful scrape 05:05:36Z, 1,970 positions in 24 h, 11,845 total, 14 devices, 2 tracked persons.
- CONFIG_VERIFIED: the owning cron entry remained `*/5` with its next run scheduled normally.

## Actions

1. Performed exactly one controlled retry (the login above). No retry loop was entered.
2. Changed the wrapper: in `halted` it now attempts one probe every `ICLOUD_SLOW_PROBE_SECS` (default 21600 s, four attempts per day instead of roughly 288 password logins per day). A passing probe restores the normal cadence by itself and alerts; a failing probe stays halted, refreshes the timestamp, and alerts only when the error signature changes. New state fields `LAST_PROBE_TS` and `LAST_SIG`. The pre-existing stop-at-first-anomaly, one-probe-then-halt and cooldown logic is unchanged.
3. Hardened the signature extraction to be space-free and quoted the persisted value, after the sandbox suite exposed a real sourcing defect: `state.env` is sourced by bash, so an unquoted value containing a space splits at the assignment and attempts to execute the remainder.
4. Required exit code 0 on the slow-probe path in addition to marker detection, so an unrecognised failure cannot be read as a recovery and resume the cadence on top of a broken scraper. The normal path keeps marker-only detection deliberately, so a benign non-fatal error cannot start halting the job.
5. Initialised the production state to `MODE=halted`, `LAST_PROBE_TS=<now>`, `LAST_SIG="invalid_email_password"` so the first slow probe lands at 2026-09-28T11:37Z (13:37 CEST) rather than immediately.
6. Recorded the durable reasoning in the `personal-location-tracker` skill and archived the regression suite under that skill.

## Causal evidence

- RUNTIME_VERIFIED: two independent authentication paths return the same HTTP 403 / `-20209`: the scraper's stored-session path and a session-free clean login with no cookie jar present. A corrupt or stale local session store is therefore excluded.
- INFERENCE: Apple is refusing the automated password authentication path from this datacenter host rather than locking the account. Supporting facts: the same stored credentials authenticated 482 consecutive cycles up to five minutes before the failure, the owner signs in interactively without any lock prompt, and no lock notification was delivered. This is a client/IP scoped flag.
- RUNTIME_VERIFIED: recurring `-20209` on 21/09, 26/09 and 28/09. The wrapper's hardening comment dates the first occurrence, and the credential file update of 26/09 12:52Z preceded the clean series by about eight minutes.
- UNVERIFIED: the exact Apple subsystem and the exact trigger (login volume, IP reputation, session re-authentication frequency). No source-level or vendor-side evidence is available for this.
- UNVERIFIED: whether a password reset or an explicit unlock would clear the flag faster. Apple's own error text is the only guidance and it points at iForgot.

## Acceptance

- TEST_VERIFIED: sandbox suite, 11 scenarios and 32 assertions, 0 failures. It re-seds the real wrapper into a scratch state directory and drives it with fake scraper commands, so it performs no Apple calls and does not touch production state. Covered: halted with a recent probe makes no call; an expired probe with an unchanged signature stays halted without alerting; a changed signature alerts; a successful probe self-resumes and alerts; the cooldown skip and the ten-minute probe behave as before; an unrecognised failure and a missing scraper command do not resume.
- RUNTIME_VERIFIED: the production wrapper, driven with the real state file and a tripwire in place of the scraper, exited 0 immediately and produced no output, proving no scraper invocation. The state file was unchanged afterwards.
- RUNTIME_VERIFIED: the production `state.env` sources cleanly with no stray command execution.
- CONFIG_VERIFIED: `bash -n` clean on the wrapper; cron entry unchanged at `*/5`.

## Residual risk and excluded work

- The Apple flag is unresolved and outside the workspace's control. The scraper stays halted until Apple reopens the path, so position history keeps a gap for the duration. The 6-hour interval bounds detection lag to about six hours.
- The proposed cadence reduction (5 minutes to 15) was NOT applied. It is a decision for Andrea once the path is working again, and it is the only remaining structural mitigation for the recurrence.
- The account password was not changed, no session was destroyed, and no interactive re-authentication was attempted, because the evidence points to a client-scoped flag rather than a credential problem.
- No attempt was made to circumvent Apple's control (no client-signature spoofing, no alternate egress, no proxy). That is deliberate and should stay deliberate.
- The unrelated pre-existing tool false-positive class in the owning cron entry (run budget exhaustion recorded as `completed`) is documented elsewhere and is out of scope here.

## Rollback

Restore `/root/.hermes/backups/scripts/icloud-findmy-scraper.sh.bak-20260928-053359-pre-slow-probe` over the wrapper and `/root/.hermes/backups/scripts/state.env.bak-20260928-053359-pre-slow-probe` over the state file. The previous wrapper treated `halted` as permanent, which is a safe state, so rollback only restores the need for manual recovery.

## Review request

Confirm three points. First, that discriminating a client/IP scoped flag from an account-wide lock on this evidence is sound, and that declining a password reset was correct. Second, that granting the guard autonomy to retry an authentication path with a three-times-in-one-week lock history is proportionate at four attempts per day, given that every failure re-arms the halt. Third, that requiring a clean exit code only on the recovery path is the right boundary rather than applying it to the normal path as well.
