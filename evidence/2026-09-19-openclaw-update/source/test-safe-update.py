#!/usr/bin/env python3
"""Exercise the real guarded shell flow using isolated synthetic command fixtures."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import tempfile

SCRIPT = Path(__file__).with_name('openclaw-safe-update.sh')
MOCK = r'''#!/usr/bin/python3
import json,os,sys
from pathlib import Path
name=Path(sys.argv[0]).name; a=sys.argv[1:]
s=os.environ['SCENARIO']; root=Path(os.environ['FIXTURE']); updated=root/'updated'
def out(x): print(json.dumps(x))
if name=='sleep': sys.exit(0)
if name=='systemctl':
 print('123' if 'show' in a else ('inactive' if s=='inactive' else 'active')); sys.exit(0)
if name=='df':
 print('Filesystem 1024-blocks Used Available Capacity Mounted on')
 print('/dev/mock 99999999 1 '+('1' if s=='disk' else '99999998')+' 1% /'); sys.exit(0)
if name=='backup':
 (root/'backup-called').touch()
 if s=='backup-exit': sys.exit(9)
 key=a[a.index('--key')+1]
 out(dict(status='PASS',local_archive_created=False,object='wrong' if s=='backup-object' else key,
 bytes=1,sha256=None if s=='backup-hash' else 'a'*64,
 verification='producer exit, encryption exit, full remote SHA-256 readback')); sys.exit(0)
if a[:2]==['--log-level','silent']: a=a[2:]
target='2026.9.6' if s=='future' else '2026.9.5'
if a==['--version']:
 v=target if updated.exists() or s=='noop' else '2026.9.4'
 print('OpenClaw '+v+' (fixture)')
elif a[:2]==['config','file']:
 if s=='unexpected': sys.exit(6)
 print(root/'config.json')
elif a[:2]==['config','validate']:
 sys.exit(2 if s=='invalid-config' else 0)
elif a and a[0]=='health': out({'ok':s!='health','channels':{'telegram':{'accounts':{'default':{'configured':True}}}}})
elif a[:2]==['update','status']:
 out({'activeRun':{'status':'running'} if s=='active-update' else None,
 'update':{'installKind':'package','packageManager':'unknown' if s=='owner' else 'npm','registry':{'latestVersion':target}},
 'availability':{'available':s!='noop','latestVersion':target}})
elif a and a[0]=='update' and '--dry-run' in a:
 out({'mode':'npm'}); sys.exit(1 if s=='dry-refused' else 0)
elif a and a[0]=='update':
 updated.touch()
 if s=='config-change': (root/'config.json').write_text('{"models":{"changed":true}}')
 out({'status':'error' if s in ('native-failure','native-json-error') else 'ok',
 'steps':[{'name':'candidate migration rehearsal','command':'openclaw doctor --fix --non-interactive','exitCode':0}]})
 sys.exit(7 if s=='native-failure' else 0)
elif a and a[0]=='doctor': out({'findings':[{'severity':'error'}] if s=='lint-error' else []})
elif a and a[0]=='status':
 v=target if updated.exists() or s=='noop' else '2026.9.4'
 out({'collection':{'source':'local' if s=='offline-status' else 'gateway'},'runtimeVersion':'2026.9.4' if s=='gateway-version' else v,'gateway':{'reachable':True}})
elif a[:2]==['channels','status']:
 out({'statusIssues':[], 'channelAccounts':{'telegram':[] if s=='missing-channel' else [{'accountId':'default','connected':True,'probe':{'ok':s!='channel'},'lastError':None}]}})
else: sys.exit(3)
'''

def run_case(scenario, args, status, rc, should_update=False):
    with tempfile.TemporaryDirectory(prefix='safe-update-test-') as temp:
        root=Path(temp); bindir=root/'bin'; bindir.mkdir()
        (root/'config.json').write_text('{}')
        for name in ('openclaw','systemctl','df','sleep','backup'):
            path=bindir/name; path.write_text(MOCK); path.chmod(0o700)
        env=dict(os.environ,PATH=f'{bindir}:'+os.environ['PATH'],FIXTURE=str(root),SCENARIO=scenario,
                 OPENCLAW_SAFE_UPDATE_RUN_ROOT=str(root/'runs'),OPENCLAW_SAFE_UPDATE_LOCK_FILE=str(root/'lock'),
                 OPENCLAW_SAFE_UPDATE_S3_STREAM=str(bindir/'backup'),OPENCLAW_SAFE_UPDATE_BACKUP_PRODUCER='/bin/true')
        holder=None
        if scenario=='locked':
            holder=(root/'lock').open('w'); fcntl.flock(holder,fcntl.LOCK_EX|fcntl.LOCK_NB)
        result=subprocess.run(['bash',str(SCRIPT),*args],env=env,capture_output=True,text=True,timeout=20)
        reports=list((root/'runs').glob('*/result.json')) if (root/'runs').exists() else []
        report=json.loads(reports[-1].read_text()) if reports else {}
        assert result.returncode==rc,(scenario,result.returncode,result.stdout,result.stderr)
        assert report.get('final_status')==status,(scenario,report,result.stderr)
        assert (root/'updated').exists()==should_update,(scenario,'unexpected update execution')
        if scenario.startswith('native-'):
            assert report['doctor_fix_execution']=='attempted'
        if scenario in ('health','owner','active-update','inactive','disk','invalid-config','locked'):
            assert not (root/'backup-called').exists()
        if holder: holder.close()
        print(f'PASS {scenario} {" ".join(args)} -> {status or "argument/lock rejection"}')

apply=['--apply','openclaw@2026.9.5']
cases=[
 ('noop',['--check','latest'],'NO_UPDATE',0,False),
 ('noop',apply,'NO_UPDATE',0,False),
 ('normal',['--dry-run','openclaw@2026.9.5'],'READY',0,False),
 ('future',['--check','latest'],'MANUAL_REVIEW_REQUIRED',20,False),
 ('future',['--apply','2026.9.6','--approve-bundled-doctor'],'SUCCESS',0,True),
 ('normal',apply,'SUCCESS',0,True),
 ('health',apply,'PRECHECK_FAILED',10,False),
 ('owner',apply,'MANUAL_REVIEW_REQUIRED',20,False),
 ('inactive',apply,'PRECHECK_FAILED',10,False),
 ('active-update',apply,'PRECHECK_FAILED',10,False),
 ('offline-status',apply,'PRECHECK_FAILED',10,False),
 ('disk',apply,'PRECHECK_FAILED',10,False),
 ('invalid-config',apply,'PRECHECK_FAILED',10,False),
 ('dry-refused',apply,'MANUAL_REVIEW_REQUIRED',20,False),
 ('backup-hash',apply,'PRECHECK_FAILED',10,False),
 ('backup-object',apply,'PRECHECK_FAILED',10,False),
 ('backup-exit',apply,'PRECHECK_FAILED',10,False),
 ('native-failure',apply,'RECOVERY_REQUIRED',10,True),
 ('native-json-error',apply,'RECOVERY_REQUIRED',10,True),
 ('config-change',apply,'MANUAL_REVIEW_REQUIRED',20,True),
 ('gateway-version',apply,'RECOVERY_REQUIRED',10,True),
 ('lint-error',apply,'RECOVERY_REQUIRED',10,True),
 ('channel',apply,'RECOVERY_REQUIRED',10,True),
 ('missing-channel',apply,'RECOVERY_REQUIRED',10,True),
 ('unexpected',apply,'FAILED',6,False),
 ('locked',apply,None,10,False),
 ('normal',['--apply','latest'],None,2,False),
 ('normal',['--apply','invalid'],None,2,False),
]
for case in cases: run_case(*case)
print(f'PASS all {len(cases)} isolated flow tests; no production command executed')
