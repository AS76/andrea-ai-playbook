#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PYSCHEMA'
import sqlite3
c=sqlite3.connect('file:/root/.openclaw/state/openclaw.sqlite?mode=ro',uri=True)
v=c.execute('PRAGMA user_version').fetchone()[0]
if v > 15:
    raise SystemExit('BLOCKED: live schema exceeds old runtime schema 15. Review reverse migration and preserve all newer data before rollback; do not blindly restore backup.')
PYSCHEMA
systemctl --user stop openclaw-gateway.service
python3 - <<'PYRESTORE'
import os
from pathlib import Path
p=Path('/root/.openclaw/update-runs/assisted-20260909T045302Z')
f=Path('/root/.config/systemd/user/openclaw-gateway.service.d/50-isolated-runtime.conf')
if f.exists(): f.rename(p/'50-isolated-runtime.disabled')
link=Path('/usr/bin/openclaw.rollback-link')
if link.exists() or link.is_symlink(): raise SystemExit('temporary rollback link already exists')
os.symlink('../lib/node_modules/openclaw/openclaw.mjs',link)
os.replace(link,'/usr/bin/openclaw')
PYRESTORE
systemctl --user daemon-reload
systemctl --user start openclaw-gateway.service
# Package/runtime rollback only. Never overwrite newer databases or sessions.
