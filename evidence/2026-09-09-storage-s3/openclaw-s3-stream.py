#!/usr/bin/python3
"""Encrypt a producer stream directly into S3; commit only after producer success."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import boto3
BUCKET='cleo';ENDPOINT='https://s3.eu-central-1.idrivee2.com';RECIPIENT='1AEED7ACD9CF6627577B12BF1C23E7EB1F1DAD90'
def client():
 v={}
 for line in Path('/root/.openclaw/secrets/apikeys.env').read_text().splitlines():
  if '=' in line:
   k,x=line.split('=',1)
   if k in ['S3_ACCESS_KEY','S3_SECRET_KEY']:v[k]=x.strip().strip('\"\x27')
 return boto3.client('s3',endpoint_url=ENDPOINT,region_name='eu-central-1',aws_access_key_id=v['S3_ACCESS_KEY'],aws_secret_access_key=v['S3_SECRET_KEY'])
def main():
 a=argparse.ArgumentParser();a.add_argument('--key',required=True);a.add_argument('command',nargs=argparse.REMAINDER);args=a.parse_args()
 cmd=args.command[1:] if args.command[:1]==['--'] else args.command
 if not cmd:raise SystemExit('Producer command required')
 s=client();upload=s.create_multipart_upload(Bucket=BUCKET,Key=args.key,ContentType='application/octet-stream')['UploadId'];parts=[];sha=hashlib.sha256();size=0;source=None;enc=None;complete=False
 try:
  source=subprocess.Popen(cmd,stdout=subprocess.PIPE)
  enc=subprocess.Popen(['gpg','--batch','--trust-model','always','--recipient',RECIPIENT,'--compress-algo','none','--encrypt'],stdin=source.stdout,stdout=subprocess.PIPE)
  source.stdout.close()
  while True:
   chunk=enc.stdout.read(16*1024*1024)
   if not chunk:break
   size+=len(chunk);sha.update(chunk)
   n=len(parts)+1;part=s.upload_part(Bucket=BUCKET,Key=args.key,UploadId=upload,PartNumber=n,Body=chunk)
   parts.append({'PartNumber':n,'ETag':part['ETag']})
  er=enc.wait();sr=source.wait()
  if er or sr or not size:raise RuntimeError('Producer or encryption failed; incomplete upload aborted')
  s.complete_multipart_upload(Bucket=BUCKET,Key=args.key,UploadId=upload,MultipartUpload={'Parts':parts});complete=True
  remote=s.get_object(Bucket=BUCKET,Key=args.key)['Body'];rh=hashlib.sha256();rs=0
  while chunk:=remote.read(4*1024*1024):rh.update(chunk);rs+=len(chunk)
  remote.close()
  if rs!=size or rh.hexdigest()!=sha.hexdigest():raise RuntimeError('Remote readback mismatch; backup not accepted')
  s.put_object(Bucket=BUCKET,Key=args.key+'.sha256',Body=(sha.hexdigest()+'\n').encode())
  result={'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'PASS','bytes':size,'sha256':sha.hexdigest(),'object':args.key,'local_archive_created':False,'verification':'producer exit, encryption exit, full remote SHA-256 readback'}
  s.put_object(Bucket=BUCKET,Key=args.key+'.manifest.json',Body=json.dumps(result).encode());print(json.dumps(result),flush=True)
 finally:
  for p in [source,enc]:
   if p and p.poll() is None:p.terminate();p.wait()
  if not complete:s.abort_multipart_upload(Bucket=BUCKET,Key=args.key,UploadId=upload)
if __name__=='__main__':main()
