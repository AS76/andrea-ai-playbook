# Guarded OpenClaw updates

Use the installed CLI/runtime, not an old PATH or historical configuration.

```sh
/root/.openclaw/scripts/openclaw-safe-update.sh --self-test
/root/.openclaw/scripts/openclaw-safe-update.sh --dry-run latest
/root/.openclaw/scripts/openclaw-safe-update.sh --apply openclaw@2026.9.5
```

The 2026.9.5 run was specifically approved. For a later exact version, inspect
its official release and bundled updater/Doctor semantics first. After explicit
operator approval of that run:

```sh
/root/.openclaw/scripts/openclaw-safe-update.sh --apply openclaw@YYYY.M.D --approve-bundled-doctor
```

The flag records the caller's per-run authorization; it is not a general policy
bypass. `latest` is deliberately prohibited for apply. Check accepts `latest`.
The native updater remains responsible for rehearsal, integrity, migration and
activation. Never suppress a validation/integrity check to make an update pass.

## Results

- `NO_UPDATE`: installed and serving versions match the target; RPC verified.
- `READY`: healthy preflight and native dry-run; target repair authority accepted.
- `MANUAL_REVIEW_REQUIRED` (20): unknown owner, unapproved target, refused dry-run,
  or changed routing/auth/channel configuration. No automatic repair of policy.
- `PRECHECK_FAILED` (10): rejected before native apply.
- `RECOVERY_REQUIRED` (10): apply or acceptance failed. Runtime is **unverified**,
  not assumed rolled back. Do not blindly restart or reapply.
- `SUCCESS`: native success JSON plus version, semantic config, lint, sustained
  same-PID RPC and Telegram probe gates passed.

Evidence is private under `/root/.openclaw/update-runs`. The producer streams
encrypted backups to S3 and checks a complete remote SHA-256 readback. It includes
SQLite-consistent state, PostgreSQL, canonical workspace material, deployment
scripts/unit, agent auth/model files, plugin manifests and local plugin/skill
sources. Reinstallable dependencies are not archived. Full restore is not yet
tested; a readback hash is not a restore test.

## 2026.9.4 to 2026.9.5 recovery facts

The 2026.9.4 launcher had a 300-second candidate cap and a 30-second integrity
reader cap. Both prevented this VPS update. Minimal timeout-only backports
preserved all checks and were superseded by the official 2026.9.5 package, whose
budget logic already removes those caps. Do not reapply these old patches to a
new package.

If a promoted package reports `state-migrated-no-rollback`, do not start the old
binary against migrated databases. Preserve encrypted state first. Inspect
plugin finalization after the parent updater has exited. On this exact incident,
standalone Doctor with external service policy converged the plugin packages;
it must not inherit the updater's plugin-defer flag. This is a reviewed recovery
operation, not an unconditional wrapper retry.

Codex's retained migration then waited for an `after-session-repair` inspection
which preflight refused to reach. The native `runPostSessionPluginDoctorStateRepairs`
was inspected first (no proposed deletions), then executed under the actual
Gateway/SQLite, agent-database and plugin lifecycle leases. It reported Codex
complete with no changes/warnings and an empty pending-plugin list. No fabricated
index, manual completion row, disabled guard, or deleted session was used.
The version-pinned script and exact checks are retained in the recovery evidence
and GitHub handoff. Do not generalize this workaround to another release or to
a diagnostic that proposes deletions.

After recovery, validate config, start the intended package's Gateway, and prove
runtime version over RPC, same-PID sustained health, channel probes and a delivery
test. Historical failed update records remain audit history; current runtime
acceptance must be reported separately. No promise is made that an unreviewed
future release cannot introduce another defect.
