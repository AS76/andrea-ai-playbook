#!/usr/bin/env python3
"""Read-only source gate. Never applies patches or executes candidate source."""
import argparse, hashlib, json, re
from pathlib import Path

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(dist, policy):
    version = json.loads((dist.parent / 'package.json').read_text())['version']
    modules = list(dist.glob('model-auth-provider-config-*.js'))
    if len(modules) != 1:
        return {'status': 'REVIEW_REQUIRED_SOURCE_CHANGED', 'version': version}, 1
    names = re.findall(r'from \"\./(runtime-snapshot-[A-Za-z0-9_-]+\.js)\"', modules[0].read_text())
    if len(set(names)) != 1:
        return {'status': 'REVIEW_REQUIRED_SOURCE_CHANGED', 'version': version}, 1
    lifecycle = [dist / names[0]]
    observed = {'version': version, 'provider_sha256': digest(modules[0]), 'lifecycle_sha256': digest(lifecycle[0])}
    if observed == policy['approved_local']:
        return {'status': 'PASS_LOCAL_MITIGATION', **observed}, 0
    if observed in policy.get('reviewed_upstream_fixes', []):
        return {'status': 'PASS_UPSTREAM_FIXED_NO_LOCAL_PATCH', **observed}, 0
    if observed == policy['known_unmitigated']:
        return {'status': 'FAIL_MITIGATION_MISSING', **observed}, 1
    return {'status': 'REVIEW_REQUIRED_SOURCE_CHANGED', **observed}, 1

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dist', type=Path, default=Path('/usr/lib/node_modules/openclaw/dist'))
    p.add_argument('--policy', type=Path, default=Path(__file__).with_name('openclaw-provider-mitigation-policy.json'))
    a = p.parse_args()
    try:
        result, rc = check(a.dist, json.loads(a.policy.read_text()))
    except Exception as e:
        result, rc = {'status': 'REVIEW_REQUIRED_INSPECTION_FAILED', 'error_type': type(e).__name__}, 1
    result['action'] = 'none; read-only comparison, never reapply an old patch'
    print(json.dumps(result, sort_keys=True))
    return rc

if __name__ == '__main__':
    raise SystemExit(main())
