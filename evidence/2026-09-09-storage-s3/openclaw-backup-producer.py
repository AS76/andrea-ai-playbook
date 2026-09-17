#!/usr/bin/python3
"""Produce gzip tar on stdout, with consistent SQLite copies held only in RAM."""
import io,os,sqlite3,subprocess,sys,tarfile,time
from pathlib import Path
ROOT=Path('/root/.openclaw')
def memory_entry(tar,name,data):
 i=tarfile.TarInfo(name);i.size=len(data);i.mode=0o600;i.mtime=int(time.time());tar.addfile(i,io.BytesIO(data))
def main():
 names=['openclaw.json','secrets','workspace/main/AGENTS.md','workspace/main/SOUL.md','workspace/main/IDENTITY.md','workspace/main/USER.md','workspace/main/MEMORY.md','workspace/main/LESSONS.md','workspace/main/ARCHITECTURE.md','workspace/main/memory','workspace/main/vault','workspace/main/reports']
 with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz',compresslevel=1) as t:
  for name in names:
   p=ROOT/name
   if not p.exists():raise RuntimeError('Required canonical backup source missing')
   for f in [p,*p.rglob('*')] if p.is_dir() else [p]:
    before=f.lstat();t.add(str(f),arcname=str(f).lstrip('/'),recursive=False);after=f.lstat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise RuntimeError('Source changed during backup; retry required')
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
