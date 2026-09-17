# OpenClaw safe update runbook

Use `/root/.openclaw/scripts/openclaw-safe-update.sh` as the production entrypoint. It is fail-closed, serialized by `/run/lock/openclaw-safe-update.lock`, stores mode-0700 evidence below `/root/.openclaw/update-runs`, and emits an explicit final state in `result.json`.

## Usage

```bash
/root/.openclaw/scripts/openclaw-safe-update.sh --check latest
/root/.openclaw/scripts/openclaw-safe-update.sh --backup-only
/root/.openclaw/scripts/openclaw-safe-update.sh --apply 2026.X.Y
```

`--check` validates config, the user Gateway, health, disk, installation method, update status, and the official dry-run. It returns `NO_UPDATE` without reinstalling the current version. `--backup-only` exercises encrypted direct-to-S3 recovery. `--apply` stops with `MANUAL_REVIEW_REQUIRED` before package mutation whenever the installed updater would run Doctor repair internally or refuses ownership of the isolated package installation.

## Preconditions and backup

The active config must validate, the Gateway must be active and pass the 90-second health gate, `/opt` must have at least 5 GiB free, the installation must resolve as an npm package, and no other workflow may own the lock. Backup uses `/usr/local/bin/openclaw-backup-producer.py` piped into `/usr/local/bin/openclaw-s3-stream.py`; only successful production, encryption, multipart commit, and full remote SHA-256 readback is accepted. No local archive is created.

The recovery object includes the effective configuration and canonical state selected by the established producer, consistent SQLite snapshots, agent stores, and PostgreSQL data. The systemd unit/drop-ins and updater scripts must additionally be copied into the reviewed recovery manifest before a future activation.

## Doctor and acceptance gates

Doctor is read-only first. Automatic `doctor --fix` is permitted only when the exact update-generated migration, affected state, verified backup, and absence of unrelated findings are proven, with the Gateway stopped. OpenClaw 2026.9.3's package updater does not expose that boundary, so this wrapper refuses apply. Do not bypass it; use a separately reviewed staged upgrade or wait for a supported no-fix update boundary.

Success requires the expected version, valid config, active service without a restart loop, 90-second Gateway health, no mandatory migration, unchanged routing unless explicitly migrated, expected agents and readable sessions, all Telegram accounts running/probing, heartbeat/cron loaded, and no material new startup error. Process start alone is insufficient.

## Rollback and emergency recovery

Package, configuration, and state rollback are separate. Repoint to an older package only after source/runtime checks and state-schema compatibility pass. Restore configuration only from the verified encrypted S3 object after reviewing the exact diff. Never overwrite newer SQLite state merely because an older binary was restored; schema 16 is not proven compatible with the older schema-15 runtime.

If package readiness, source acceptance, or state compatibility is uncertain, leave the Gateway stopped. Inspect `result.json`, verify the S3 manifest/readback hash, preflight a copied database with `openclaw database preflight`, and activate only through the reviewed systemd drop-in. Start with `systemctl --user start openclaw-gateway.service`, then run the full acceptance gate above.

Update mutation and rollback paths are **NOT YET PRODUCTION-EXERCISED**.
