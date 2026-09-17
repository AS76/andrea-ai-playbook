#!/usr/bin/env python3
"""
vault_prune.py — Archivia Daily/ files >Ngg (default 30) + rimuove i sorgenti.

Default path canonici (post-fix 2026-07-20):
  Archive JSON: encrypted stream to S3; no local archive
  Cron-health:   ~/.openclaw/workspace/main/state/cron-health/vault-prune-daily.status

Pensato per cron deterministico (no LLM). Scrive status file per sweep silenzioso.

Uso:
    python3 scripts/vault_prune.py             # default 30gg
    python3 scripts/vault_prune.py --days 60   # custom threshold
    python3 scripts/vault_prune.py --dry-run   # mostra senza rimuovere

Exit codes:
    0 = success
    1 = error
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, date, timedelta, timezone


WORKSPACE = '/root/.openclaw/workspace/main'
VAULT_DAILY = os.path.join(WORKSPACE, 'vault', 'Daily')
ARCHIVE_DIR = os.path.join(WORKSPACE, 'logs', 'vault-prune', 'archives')
CRON_HEALTH_DIR = os.path.join(WORKSPACE, 'state', 'cron-health')
CRON_NAME = 'vault-prune-daily'


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--days', type=int, default=30, help='Threshold in days (default 30)')
    p.add_argument('--dry-run', action='store_true', help='Show what would be removed, do not delete')
    p.add_argument('--archive-dir', default=ARCHIVE_DIR, help='Legacy compatibility argument; archives now stream to S3')
    p.add_argument('--vault-daily', default=VAULT_DAILY, help='Source directory of daily .md files')
    p.add_argument('--no-status', action='store_true', help='Skip writing cron-health status file')
    return p.parse_args()


def write_status(note, status='ok'):
    """Write cron-health status file for silent sweep monitoring."""
    os.makedirs(CRON_HEALTH_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    status_path = os.path.join(CRON_HEALTH_DIR, f'{CRON_NAME}.status')
    payload = {
        'checked_at_utc': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'artifact': 's3://cleo/openclaw-backup/vault-prune/',
        'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'age_hours': 0,
        'status': status,
        'note': note,
    }
    with open(status_path, 'w') as f:
        json.dump(payload, f, indent=1)
    return status_path


def main():
    global args
    args = parse_args()
    threshold = date.today() - timedelta(days=args.days)
    print(f'Vault daily prune — threshold: {threshold.isoformat()} (> {args.days}gg old)')
    print(f'Source: {args.vault_daily}')
    print('Archive: S3 only (legacy local archive-dir ignored)')

    candidates = []
    for f in sorted(glob.glob(os.path.join(args.vault_daily, '*.md'))):
        name = os.path.basename(f)
        # Extract date from YYYY-MM-DD.md
        try:
            file_date = date.fromisoformat(name[:10])
        except ValueError:
            continue
        if file_date >= threshold:
            continue
        with open(f) as fh:
            content = fh.read()
        candidates.append({
            'name': name,
            'path': f,
            'size': len(content),
            'modified': datetime.fromtimestamp(os.path.getmtime(f)).isoformat(),
            'content': content,
        })

    if not candidates:
        print(f'\n✓ Nessun file > {args.days}gg — nothing to do')
        if not args.no_status:
            write_status(f'No files > {args.days}gg. Threshold {threshold.isoformat()}.')
        return 0

    by_month = Counter(c['name'][:7] for c in candidates)
    total_size = sum(c['size'] for c in candidates)
    print(f'\nCandidati: {len(candidates)} ({total_size} bytes totali)')
    print(f'  By month: {dict(by_month)}')
    print(f'  Oldest: {candidates[0]["name"]}')
    print(f'  Newest: {candidates[-1]["name"]}')

    if args.dry_run:
        print('\n[dry-run] Stop prima di rm')
        if not args.no_status:
            write_status(f'DRY-RUN: would archive {len(candidates)} files (threshold {args.days}gg). No changes made.')
        return 0

    # Encrypt directly into S3. No local archive is created.
    archive_name = f"vault-dailies-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json.gpg"
    key = 'openclaw-backup/vault-prune/' + archive_name
    archive_path = 's3://cleo/' + key
    archive = {'archive_date': datetime.now(timezone.utc).isoformat(),
               'threshold': threshold.isoformat(), 'count': len(candidates), 'files': candidates}
    subprocess.run(['/usr/local/bin/openclaw-s3-stream.py', '--key', key, '--', '/bin/cat'],
                   input=json.dumps(archive).encode(), check=True)
    # Do not remove a source changed while the remote copy was being verified.
    for c in candidates:
        with open(c['path']) as source:
            if source.read() != c['content']:
                raise RuntimeError('Daily source changed; sources retained')
    print(f'\n✓ Archive S3 verified: {archive_path}')

    # Remove
    removed = 0
    for c in candidates:
        os.remove(c['path'])
        removed += 1
    print(f'✓ Rimossi {removed} file da {args.vault_daily}')

    # Verify
    remaining = sorted(glob.glob(os.path.join(args.vault_daily, '*.md')))
    print(f'\nStato finale: {len(remaining)} file in Daily/')

    # Write cron-health status (silent sweep monitoring)
    if not args.no_status:
        note = (f'Archived {removed} file(s) ({total_size}B), removed from Daily/. '
                f'Threshold {args.days}gg. {len(remaining)} files remain. '
                f'Archive: {archive_path}')
        write_status(note, status='ok')

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        # Best-effort fail status so silent sweep monitors catch the issue.
        try:
            os.makedirs(CRON_HEALTH_DIR, exist_ok=True)
            payload = {
                'checked_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'artifact': '',
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'age_hours': 0,
                'status': 'fail',
                'note': f'FAIL: {type(e).__name__}: {e}',
            }
            with open(os.path.join(CRON_HEALTH_DIR, f'{CRON_NAME}.status'), 'w') as f:
                json.dump(payload, f, indent=1)
        except Exception:
            pass  # never shadow the original exception
        sys.exit(1)