"""Verified local archive placement; no vendor calls or data qualification.

Staging is retired only after original/staging/final SHA-256 equality and durable
publication evidence. Original source files are never deleted. Local manifests are
private data-plane artifacts, not Git source files.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from runtime.massive_maintainer.maintain import atomic,encode,read,now,writer

SCHEMA='fetch.legacy-placement@1'

def sha(path):
    before=path.stat()
    with path.open('rb') as stream: result=hashlib.file_digest(stream,'sha256').hexdigest()
    after=path.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        raise ValueError('file changed during hash')
    return result

def within(path,root):
    value=path.resolve()
    if not value.is_relative_to(root.resolve()):raise ValueError('path outside declared root')
    return value

def append(path,record):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('ab') as stream:
        stream.write(encode(record));stream.flush();os.fsync(stream.fileno())

def plan(manifest,source_root,staging_root,target_root):
    if target_root.name!='_TICKERS':raise ValueError('explicit top-level _TICKERS target required')
    original=read(manifest)
    rows=original['files'];items=[];seen=set()
    for row in rows:
        ticker=row['ticker']
        if not isinstance(ticker,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',ticker):raise ValueError('invalid ticker path')
        if ticker.casefold() in seen:raise ValueError('ticker collision')
        seen.add(ticker.casefold())
        source=within(Path(row['source']),source_root)
        staging=within(Path(row['destination']),staging_root)
        target=within(target_root/ticker/(ticker+'.jsonl'),target_root)
        if source.name!=ticker+'.jsonl' or staging.name!=ticker+'.jsonl':raise ValueError('filename mismatch')
        if source==staging or source==target or staging==target:raise ValueError('paths must be distinct')
        if not source.is_file() or source.stat().st_size!=row['bytes']:raise ValueError('original unavailable or size changed')
        items.append({'ticker':ticker,'source':str(source),'staging':str(staging),'target':str(target),'bytes':row['bytes'],'prior_sha256':row.get('sha256')})
    if len(items)!=original['discovered'] or not original['complete']:raise ValueError('incomplete input manifest')
    return sorted(items,key=lambda x:({'NVDA':0,'AAOI':1,'CRWV':2,'SFTBY':3}.get(x['ticker'],4),x['ticker']))

def execute(manifest,source_root,staging_root,target_root,authority_root,journal_root):
    with writer(authority_root):
        items=plan(manifest,source_root,staging_root,target_root)
        journal=journal_root/'placement.journal.jsonl'
        history=[json.loads(line) for line in journal.read_bytes().splitlines()] if journal.exists() else []
        prepared={r['ticker']:r for r in history if r.get('event')=='prepared'}
        # No overwrite: only this journal's exact previous target may resume.
        for item in items:
            target=Path(item['target']);staging=Path(item['staging'])
            partial=target.with_suffix('.jsonl.fetch-placement.partial')
            if target.exists() and (item['ticker'] not in prepared or prepared[item['ticker']]['target']!=str(target)):
                raise FileExistsError('unowned target collision: '+item['ticker'])
            if partial.exists():raise FileExistsError('preserved partial requires inspection: '+item['ticker'])
            if not staging.exists() and not target.exists():raise FileNotFoundError('staging and destination absent: '+item['ticker'])
        target_root.mkdir(parents=True,exist_ok=True);journal_root.mkdir(parents=True,exist_ok=True)
        output=read(journal_root/'placement.json',{'schema':SCHEMA,'root':str(target_root.resolve()),'owner':'_FETCH/B02','files':{},'complete':False})
        if output['root']!=str(target_root.resolve()):raise ValueError('journal root binding mismatch')
        for item in items:
            source,staging,target=(Path(item[k]) for k in ('source','staging','target'))
            original_sha=sha(source)
            if item['prior_sha256'] and item['prior_sha256']!=original_sha:raise ValueError('prior source hash mismatch: '+item['ticker'])
            if staging.exists() and sha(staging)!=original_sha:raise ValueError('staging differs from original: '+item['ticker'])
            evidence=dict(item,sha256=original_sha,event='prepared',at=now())
            append(journal,evidence)
            if not target.exists():
                if shutil.disk_usage(target_root).free<item['bytes']+1024**3:raise OSError('insufficient safe copy space')
                target.parent.mkdir(parents=True,exist_ok=True)
                partial=target.with_suffix('.jsonl.fetch-placement.partial')
                with staging.open('rb') as inp,partial.open('xb') as out:
                    shutil.copyfileobj(inp,out,1024*1024);out.flush();os.fsync(out.fileno())
                if partial.stat().st_size!=item['bytes'] or sha(partial)!=original_sha:raise ValueError('partial copy mismatch')
                # Windows rename refuses an existing destination; preflight is not an overwrite license.
                os.rename(partial,target)
            if target.stat().st_size!=item['bytes'] or sha(target)!=original_sha:raise ValueError('final identity mismatch')
            append(journal,dict(evidence,event='published_verified',at=now()))
            result=dict(item,sha256=original_sha,path=str(target.relative_to(target_root)),qualification='unqualified_legacy_archive',original_preserved=True,staging_retired=False,verified_at=now())
            output['files'][item['ticker']]=result;output['at']=now()
            atomic(journal_root/'placement.json',encode(output))
            # Exact checked staging path only. Rollback can restore this path from
            # either verified final bytes or the untouched original.
            if staging.exists():
                if sha(staging)!=original_sha or sha(source)!=original_sha:raise ValueError('preserved input changed before retirement')
                within(staging,staging_root).unlink()
            append(journal,dict(evidence,event='staging_retired',at=now()))
            result['staging_retired']=True
            atomic(journal_root/'placement.json',encode(output))
            print(json.dumps({'ticker':item['ticker'],'verified':len(output['files']),'total':len(items),'sha256':original_sha}),flush=True)
        output.update(complete=True,at=now(),count=len(items),bytes=sum(x['bytes'] for x in items),rollback='Restore each old staging path from final or preserved original only after matching recorded SHA256; no originals deleted')
        atomic(journal_root/'placement.json',encode(output))
        atomic(target_root/'_FETCH-placement.json',encode(output))
        return output

def resolve_archive(manifest,ticker,verify_bytes=True):
    obj=read(manifest)
    if obj.get('schema')!=SCHEMA or obj.get('complete') is not True:raise ValueError('incomplete placement')
    entry=obj['files'][ticker];root=Path(obj['root']);path=within(root/entry['path'],root)
    if path!=root/ticker/(ticker+'.jsonl') or not path.is_file() or path.stat().st_size!=entry['bytes']:raise ValueError('archive lookup mismatch')
    if verify_bytes and sha(path)!=entry['sha256']:raise ValueError('archive checksum mismatch')
    return {'ticker':ticker,'path':str(path),'sha256':entry['sha256'],'status':'archive_available_not_qualified'}

def main():
    p=argparse.ArgumentParser()
    for name in ('manifest','source-root','staging-root','target-root','authority-root','journal-root'):p.add_argument('--'+name,required=True,type=Path)
    p.add_argument('--execute',action='store_true');a=p.parse_args()
    if a.execute:
        result=execute(a.manifest,a.source_root,a.staging_root,a.target_root,a.authority_root,a.journal_root)
        print(json.dumps({'complete':result['complete'],'count':result['count'],'bytes':result['bytes']}))
    else:
        items=plan(a.manifest,a.source_root,a.staging_root,a.target_root)
        print(json.dumps({'count':len(items),'bytes':sum(i['bytes'] for i in items),'target_collisions':[i['ticker'] for i in items if Path(i['target']).exists()],'plan':items},indent=2))

if __name__=='__main__':main()
