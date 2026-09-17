import os,sys,json,hashlib,secrets,subprocess,shutil,time
from pathlib import Path
import boto3
BASE=Path(__file__).parent
BUCKET='cleo'; PREFIX='openclaw-cold-storage/20260909'; RECIPIENT='1AEED7ACD9CF6627577B12BF1C23E7EB1F1DAD90'
os.umask(0o077)
os.nice(10)
v={}
for line in Path('/root/.openclaw/secrets/apikeys.env').read_text().splitlines():
 if '=' in line:
  k,x=line.split('=',1)
  if k in ['S3_ACCESS_KEY','S3_SECRET_KEY']:v[k]=x.strip().strip('\"\x27')
s3=boto3.client('s3',endpoint_url='https://s3.eu-central-1.idrivee2.com',region_name='eu-central-1',aws_access_key_id=v['S3_ACCESS_KEY'],aws_secret_access_key=v['S3_SECRET_KEY'])
def snapshot(paths):
 result={}
 for top in paths:
  p=Path(top)
  for f in [p,*p.rglob('*')] if p.is_dir() else [p]:
   st=f.lstat();result[str(f)]=(st.st_mode,st.st_size,st.st_mtime_ns,st.st_ino)
 return result

def open_handles(paths):
 hits=[]
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
  try:
   for fd in [proc/'cwd',*(proc/'fd').iterdir()]:
    try:t=os.readlink(fd)
    except OSError:continue
    if any(t==p or t.startswith(p+'/') for p in paths):hits.append(proc.name)
  except OSError:pass
 return sorted(set(hits))
def gpg(pw,args,**kwargs):
 rd,wr=os.pipe();os.write(wr,pw+b'\n');os.close(wr)
 try:return subprocess.Popen(['gpg','--batch','--no-symkey-cache','--pinentry-mode','loopback','--passphrase-fd',str(rd),*args],pass_fds=(rd,),**kwargs)
 finally:os.close(rd)

def run(name,paths):
 manifest=BASE/(name+'.json')
 if manifest.exists():raise RuntimeError('Existing manifest: review before retry')
 if not paths or any(not Path(p).exists() or Path(p).is_symlink() for p in paths):raise RuntimeError('Target missing or symlink')
 if open_handles(paths):raise RuntimeError('Open target file descriptors: defer group')
 before=snapshot(paths);pw=secrets.token_hex(32).encode();key=PREFIX+'/'+name+'.tar.gz.gpg';cipherbytes=0
 print(name,'ARCHIVING',len(before),'entries',flush=True)
 with (BASE/(name+'.log')).open('wb') as err:
  tar=subprocess.Popen(['tar','--acls','--xattrs','--numeric-owner','-I','gzip -1','-cf','-','-C','/',*[p.lstrip('/') for p in paths]],stdout=subprocess.PIPE,stderr=err)
  enc=gpg(pw,['--compress-algo','none','--cipher-algo','AES256','--symmetric'],stdin=tar.stdout,stdout=subprocess.PIPE,stderr=err)
  tar.stdout.close()
  sealed=subprocess.run(['gpg','--batch','--trust-model','always','--recipient',RECIPIENT,'--encrypt'],input=pw+b'\n',stdout=subprocess.PIPE,stderr=err,check=True).stdout
  upload=s3.create_multipart_upload(Bucket=BUCKET,Key=key)['UploadId'];parts=[];ch=hashlib.sha256();completed=False
  try:
   while chunk:=enc.stdout.read(16*1024*1024):
    ch.update(chunk);cipherbytes+=len(chunk);n=len(parts)+1
    part=s3.upload_part(Bucket=BUCKET,Key=key,UploadId=upload,PartNumber=n,Body=chunk)
    parts.append({'PartNumber':n,'ETag':part['ETag']})
   er=enc.wait();tr=tar.wait()
   if er or tr:raise RuntimeError('Archive/encryption failed; sources retained')
   s3.complete_multipart_upload(Bucket=BUCKET,Key=key,UploadId=upload,MultipartUpload={'Parts':parts});completed=True
  finally:
   if not completed:
    for proc in [tar,enc]:
     if proc.poll() is None:proc.terminate();proc.wait()
    s3.abort_multipart_upload(Bucket=BUCKET,Key=key,UploadId=upload)
  cipherhash=ch.hexdigest()
  s3.put_object(Bucket=BUCKET,Key=key+'.key.gpg',Body=sealed)
  assert s3.get_object(Bucket=BUCKET,Key=key+'.key.gpg')['Body'].read()==sealed
  print(name,'UPLOADED; VERIFYING FULL READBACK AND TAR CONTENT',flush=True)
  dec=gpg(pw,['--decrypt'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err)
  compare=subprocess.Popen(['tar','--compare','--gzip','--file=-','--directory=/'],stdin=dec.stdout,stdout=err,stderr=err)
  dec.stdout.close();remote=s3.get_object(Bucket=BUCKET,Key=key)['Body'];h=hashlib.sha256()
  try:
   while chunk:=remote.read(4*1024*1024):h.update(chunk);dec.stdin.write(chunk)
  finally:dec.stdin.close();remote.close()
  dr=dec.wait();cr=compare.wait()
  if dr or cr or h.hexdigest()!=cipherhash:raise RuntimeError('Remote decrypt/content/hash comparison failed; sources retained')
 if snapshot(paths)!=before or open_handles(paths):raise RuntimeError('Source changed or opened; sources retained')
 record={'group':name,'paths':paths,'object':key,'sealed_key_object':key+'.key.gpg','cipher_sha256':cipherhash,'cipher_bytes':cipherbytes,'local_archive_created':False,'entries':len(before),'verified':'full remote ciphertext hash, successful decryption, tar compare against every source entry','source_removal':'PENDING','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 manifest.write_text(json.dumps(record,indent=2)+'\n');s3.put_object(Bucket=BUCKET,Key=key+'.manifest.json',Body=manifest.read_bytes())
 # This is the authorized move: remove only the exact verified source paths.
 for p in paths:
  target=Path(p)
  if target.is_dir():
   mode=target.stat().st_mode & 0o777
   shutil.rmtree(target)
   if name in ['desktop-trash','npm-cache','build-caches','drive-downloads']:target.mkdir(mode=mode)
  else:target.unlink()
 record['source_removal']='DONE';manifest.write_text(json.dumps(record,indent=2)+'\n');s3.put_object(Bucket=BUCKET,Key=key+'.manifest.json',Body=manifest.read_bytes())
 print(name,'VERIFIED_AND_MOVED',flush=True)

if __name__=='__main__':
 groups=json.loads((BASE/'targets.json').read_text())
 for name in sys.argv[1:]:run(name,groups[name])
