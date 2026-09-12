#!/bin/bash
# Run vendor package maintenance with /var/backups in service-private RAM.
set -euo pipefail
umask 077
MODE=${1:?mode required}
[[ "$(findmnt -n -o FSTYPE --target /var/backups)" == tmpfs ]] || { echo 'Refusing package backup without RAM-only /var/backups' >&2; exit 1; }
rc=0
case "$MODE" in
  apt-update) /usr/lib/apt/apt.systemd.daily update || rc=$? ;;
  apt-install) /usr/lib/apt/apt.systemd.daily install || rc=$? ;;
  dpkg) /usr/libexec/dpkg/dpkg-db-backup || rc=$? ;;
  self-test) printf 'synthetic RAM-only backup test\n' > /var/backups/synthetic-test ;;
  *) echo 'Unsupported mode' >&2; exit 2 ;;
esac
if [[ -n "$(find /var/backups -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  STAMP=$(date -u +%Y%m%dT%H%M%SZ)
  /usr/local/bin/openclaw-s3-stream.py --key "openclaw-backup/package-state/$MODE-$STAMP.tar.gz.gpg" -- tar -czf - -C /var/backups .
fi
exit "$rc"
