#!/usr/bin/env python3
"""Repository-only acceptance: no production access or mutations."""
import hashlib, json, re, subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[2]
def git(*args):
    return subprocess.check_output(['git', '-C', str(root), *args])
accepted = '47fb3826c21f22d4c69d0fc2a3ad53acfb1e1d1e'
main = '9d575348b80485647b6fc9a0369b3da9f4f3fa1b'
files = git('ls-tree', '-r', '--name-only', accepted).decode().splitlines()
preserved = {}
for name in files:
    if name in ('README.md', 'STATUS.md', 'CURRENT_TASK.md'):
        continue
    original = git('show', f'{accepted}:{name}')
    assert (root/name).read_bytes() == original, name
    preserved[name] = hashlib.sha256(original).hexdigest()
for name in ('CHANGELOG.md', 'docs/architecture.md', 'policies/vault-schema.md'):
    assert (root/name).read_bytes() == git('show', f'{main}:{name}'), name
# Both README contributions survive, apart from their common introduction.
readme = (root/'README.md').read_text()
for ref in (accepted, main):
    original = git('show', f'{ref}:README.md').decode()
    for line in original.splitlines():
        if line.startswith('# '):
            continue  # main updates the historical v4.3 title to Operating Repository v5.0
        line = line.replace('[docs/index.html](docs/index.html)', '[index.html](index.html)')
        for name in ('docs/identity.md','docs/operating-model.md','configs/routing.yaml','configs/openclaw.agents.yaml','policies/autonomy.md','evals/routing-tests.md'):
            line = line.replace(f'[{name}]({name})', f'`{name}` (previsto; non presente nel repository)')
        assert line in readme, (ref, line)
names = set(git('ls-files', '--cached', '--others', '--exclude-standard').decode().splitlines())
links = 0
reviews = {}
for name in sorted(names):
    path = root/name
    if not path.is_file():
        continue
    text = path.read_text()
    assert not re.search(r'^(?:<{7}|={7}|>{7})(?: |$)', text, re.M), name
    if path.suffix == '.md':
        for target in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^)]+)\)', text):
            target = target.strip('<>').split('#')[0]
            if not target or '://' in target or target.startswith(('mailto:', '/')):
                continue
            assert (path.parent/target).exists(), (name, target)
            links += 1
    if name.startswith('reviews/') and path.name != 'README.md':
        commit = re.search(r'^Reviewed Commit:\s*`?([0-9a-f]{40})', text, re.M)
        verdict = re.search(r'^## VERDICT\s*\n+([A-Z_]+)', text, re.M)
        assert commit and verdict, name
        assert commit[1] not in reviews, ('duplicate/conflicting review target', name)
        git('cat-file', '-e', commit[1]+'^{commit}')
        reviews[commit[1]] = verdict[1]
assert reviews[accepted] == 'APPROVED_WITH_NOTES'
assert not git('diff', '--name-only', '--diff-filter=U').strip()
git('merge-base', '--is-ancestor', accepted, 'HEAD')
print(json.dumps({'result':'PASS', 'accepted_commit':accepted, 'main':main,
 'accepted_files_byte_identical':preserved, 'main_files_byte_identical':3,
 'readme_both_contributions_preserved':True, 'relative_markdown_links_checked':links,
 'unique_review_targets':reviews, 'conflict_markers':0}, indent=2))
