#!/bin/bash
# S3-only backup: no archive, dump or SQLite snapshot is written to VPS storage.
set -euo pipefail
umask 077
STATUS=/root/.openclaw/workspace/main/state/cron-health/nightly-backup.status
trap 'printf "%s fail streaming_s3=true\n" "$(date -u +%FT%TZ)" > "$STATUS"' ERR
exec 9>/run/lock/openclaw-nightly-backup.lock
flock -n 9 || { echo 'Backup already running' >&2; exit 1; }
TS=$(date -u +%Y%m%dT%H%M%SZ)
KEY="openclaw-backup/oc-backup-$TS.tar.gz.gpg"
/usr/local/bin/openclaw-s3-stream.py --key "$KEY" -- /usr/local/bin/openclaw-backup-producer.py
printf '%s ok streaming_s3=true object=%s\n' "$(date -u +%FT%TZ)" "$KEY" > /root/.openclaw/workspace/main/state/cron-health/nightly-backup.status
