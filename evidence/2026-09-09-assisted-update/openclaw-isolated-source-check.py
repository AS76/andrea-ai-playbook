#!/usr/bin/env python3
"""Read-only exact-source gate for the reviewed isolated OpenClaw installation."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--manifest', type=Path, default=Path('/root/.openclaw/scripts/openclaw-isolated-source-manifest.json'))
a = p.parse_args()
try:
    manifest = json.loads(a.manifest.read_text())
    files = manifest['files']
    if not files:
        raise ValueError('empty manifest')
    failures = [str(path) for path, expected in files.items()
                if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected]
    if failures:
        print(json.dumps({'status': 'REVIEW_REQUIRED_SOURCE_CHANGED', 'files': failures}))
        raise SystemExit(1)
    print(json.dumps({'status': 'PASS_REVIEWED_UPSTREAM_SOURCE', 'version': manifest['version'], 'checked_files': len(files)}))
except Exception as exc:
    print(json.dumps({'status': 'REVIEW_REQUIRED_INSPECTION_FAILED', 'error_type': type(exc).__name__}))
    raise SystemExit(1)
