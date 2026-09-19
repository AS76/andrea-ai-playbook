#!/usr/bin/python3
"""Produce gzip tar on stdout, with consistent SQLite copies held only in RAM."""
import io,os,sqlite3,subprocess,sys,tarfile,time
from pathlib import Path
ROOT=Path('/root/.openclaw')
def memory_entry(tar,name,data):
 i=tarfile.TarInfo(name);i.size=len(data);i.mode=0o600;i.mtime=int(time.time());tar.addfile(i,io.BytesIO(data))
def add_stable(tar,p):
 before=p.lstat();tar.add(str(p),arcname=str(p).lstrip('/'),recursive=False);after=p.lstat()
 if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise RuntimeError('Source changed during backup; retry required')
def main():
 names=['openclaw.json','secrets','workspace/main/AGENTS.md','workspace/main/SOUL.md','workspace/main/IDENTITY.md','workspace/main/USER.md','workspace/main/MEMORY.md','workspace/main/LESSONS.md','workspace/main/ARCHITECTURE.md','workspace/main/memory','workspace/main/vault','workspace/main/reports']
 with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz',compresslevel=1) as t:
  for name in names:
   p=ROOT/name
   if not p.exists():raise RuntimeError('Required canonical backup source missing')
   for f in [p,*p.rglob('*')] if p.is_dir() else [p]:
    add_stable(t,f)
  # Deployment/auth artifacts are rollback inputs too, not only canonical DBs.
  extras=[ROOT/'scripts',ROOT/'gateway.systemd.env',Path('/usr/local/bin/openclaw-backup-producer.py'),Path('/usr/local/bin/openclaw-s3-stream.py'),Path('/root/.config/systemd/user/openclaw-gateway.service'),Path('/root/.config/systemd/user/openclaw-gateway.service.d')]
  extras+=sorted((ROOT/'agents').glob('*/agent/auth-profiles.json'))
  extras+=sorted((ROOT/'agents').glob('*/agent/models.json'))
  extras+=sorted((ROOT/'npm/projects').glob('*/package.json'))
  extras+=sorted((ROOT/'npm/projects').glob('*/package-lock.json'))
  package=Path('/opt/node-v24.21.0-linux-x64/lib/node_modules/openclaw/package.json')
  if package.exists():extras.append(package)
  for p in extras:
   if not p.exists():continue
   for f in [p,*p.rglob('*')] if p.is_dir() else [p]:add_stable(t,f)
  # Preserve local plugin and skill sources, excluding reinstallable dependencies
  # and historical backup directories. Never include live SQLite files this way.
  source_roots=[ROOT/'workspace/main/plugins',ROOT/'workspace/main/skills',ROOT/'workspace/main/.agents/skills',ROOT/'extensions']
  source_roots+=sorted((ROOT/'agents').glob('*/agent/workshop-skills'))
  for p in source_roots:
   if not p.exists():continue
   add_stable(t,p)
   for directory,dirs,files in os.walk(p,followlinks=False):
    dirs[:]=[x for x in dirs if x not in ('node_modules','.git','__pycache__','.openclaw-install-backups')]
    for name in dirs:add_stable(t,Path(directory)/name)
    for name in files:
     if '.sqlite' not in name:add_stable(t,Path(directory)/name)
  dbs=sorted((ROOT/'state').glob('*.sqlite'))+sorted((ROOT/'agents').glob('*/agent/openclaw-agent.sqlite'))
  if not dbs:raise RuntimeError('No SQLite stores found')
  for p in dbs:
   with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True,timeout=20) as source,sqlite3.connect(':memory:') as dest:
    source.backup(dest,pages=256,sleep=.05)
    if dest.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise RuntimeError('SQLite backup check failed')
    memory_entry(t,str(p).lstrip('/'),dest.serialize())
  names=subprocess.check_output(['runuser','-u','postgres','--','psql','-X','-Atc',"SELECT datname FROM pg_database WHERE NOT datistemplate AND datname <> 'postgres'"],text=True).splitlines()
  for name in names:
   proc=subprocess.Popen(['runuser','-u','postgres','--','pg_dump','-Fc',name],stdout=subprocess.PIPE)
   data=proc.stdout.read(512*1024*1024+1)
   if len(data)>512*1024*1024:proc.terminate();proc.wait();raise RuntimeError('Database exceeds RAM backup bound')
   if proc.wait():raise RuntimeError('PostgreSQL dump failed')
   memory_entry(t,'postgres/'+name+'.dump',data)
if __name__=='__main__':main()
