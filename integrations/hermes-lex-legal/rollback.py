#!/usr/bin/env python3
"""Rollback UK/NL profile files only. Archive data and shared services are preserved."""
import argparse, pathlib, shutil, datetime
p=argparse.ArgumentParser();p.add_argument("--apply",action="store_true");a=p.parse_args()
home=pathlib.Path("/root/.hermes/profiles/lex")
backup=home/"backups/uk-nl-20261011"
files=["SOUL.md","skills/lex-legal-research/SKILL.md","skills/lex-legal-research/references/protocol.md"]
for f in files:
    if not (backup/f).is_file():raise SystemExit("missing backup: "+f)
print("Restore:",files)
added=["tools/lex-legal-research/lex_international.py","tools/lex-legal-research/test_international.py","skills/lex-legal-research/references/international.md"]
print("Move added files into timestamped rollback archive:",added)
print("Keep lex_intl_records and snapshots; no gateway restart, no database deletion.")
if a.apply:
    disabled=backup/("disabled-"+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    disabled.mkdir()
    for f in files:shutil.copy2(backup/f,home/f)
    for f in added:
        src=home/f
        if src.exists():
            dst=disabled/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(src),str(dst))
    print("Applied; start a fresh Lex session to load restored instructions.")
else:print("DRY RUN only; no files changed.")
