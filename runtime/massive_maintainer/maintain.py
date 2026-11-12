"""Bounded, restartable Massive US-equity minute ingestion and local qualification.

Decimal values are encoded as strings, never converted through binary float.
Legacy archives are evidence only, never promoted without source confirmation.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

UTC = timezone.utc
ET = ZoneInfo('America/New_York')
SCHEMA = 'basket.massive.minute@1'
OWNER = 'work/local-20261112-massive-maintainer'

def now():
    return datetime.now(UTC).isoformat()

def encode(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'), default=str) + '\n').encode()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path, default=None):
    return json.loads(path.read_bytes()) if path.exists() else default

def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    if tmp.read_bytes() != data:
        raise ValueError('readback mismatch')
    os.replace(tmp, path)

def immutable(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('immutable collision')
    else:
        atomic(path, data)

@contextlib.contextmanager
def writer(root):
    root.mkdir(parents=True, exist_ok=True)
    lock = root / 'WRITER.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, encode({'pid': os.getpid(), 'started': now(), 'owner': OWNER}))
        os.close(fd)
        yield
    finally:
        lock.unlink()

def symbol(value):
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9.\-]{0,20}', value):
        raise ValueError('unsupported symbol; explicit mapping required')
    return value

def date_of(t):
    if type(t) is not int or t % 60000:
        raise ValueError('timestamp not integral minute milliseconds')
    return datetime.fromtimestamp(t // 1000, UTC).astimezone(ET).date().isoformat()

def normalize(row, ticker, day):
    t = row['t']
    if date_of(t) != day:
        raise ValueError('mixed exchange date')
    values = {}
    for k in ('o', 'h', 'l', 'c', 'v', 'vw'):
        if k == 'vw' and row.get(k) is None:
            values[k] = None
            continue
        v = row[k]
        if isinstance(v, (bool, float)):
            raise ValueError('unsafe numeric representation')
        d = Decimal(str(v))
        if not d.is_finite() or d < 0:
            raise ValueError('invalid numeric value')
        values[k] = str(d)
    o, h, l, c = (Decimal(values[k]) for k in ('o','h','l','c'))
    if not l <= min(o,c) <= max(o,c) <= h:
        raise ValueError('OHLC inconsistency')
    n = row.get('n')
    if n is not None and (type(n) is not int or n < 0):
        raise ValueError('invalid count')
    return dict(values, t=t, n=n, ticker=ticker, session_date=day,
                timezone='America/New_York', grain='1m', schema=SCHEMA,
                source='Massive', adjustment='split_adjusted', currency='USD',
                available_at=None)

class Massive:
    def __init__(self, root, key_file):
        self.root, self.key_file, self.calls = root, key_file, 0
        self.last = 0

    def get(self, path):
        url = 'https://api.massive.com' + path if path.startswith('/') else path
        u = urllib.parse.urlsplit(url)
        if u.scheme != 'https' or u.netloc != 'api.massive.com':
            raise ValueError('unapproved provider URL')
        q = [(k,v) for k,v in urllib.parse.parse_qsl(u.query) if k.lower() != 'apikey']
        url = urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,urllib.parse.urlencode(q),''))
        key = self.key_file.read_text(encoding='utf-8-sig').strip()
        if not key:
            raise ValueError('empty credential')
        for attempt in range(4):
            if (self.root / 'STOP').exists():
                raise RuntimeError('STOP requested')
            time.sleep(max(0, 1 - (time.monotonic()-self.last)))
            self.last = time.monotonic()
            req = urllib.request.Request(url, headers={'Authorization':'Bearer '+key})
            self.calls += 1
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    raw = response.read()
                if key.encode() in raw:
                    raise ValueError('credential reflected; response not archived')
                sha = digest(raw)
                immutable(self.root / 'raw' / (sha+'.json'), raw)
                body = json.loads(raw, parse_float=Decimal)
                return body, {'sha256':sha, 'path':'raw/'+sha+'.json', 'fetched_at':now(), 'endpoint':u.path}
            except urllib.error.HTTPError as e:
                if e.code not in (429,500,502,503,504):
                    raise RuntimeError('Massive HTTP '+str(e.code)) from None
                if attempt == 3:
                    raise RuntimeError('Massive retry exhausted HTTP '+str(e.code)) from None
                time.sleep(min(30, max(2**attempt, float(e.headers.get('Retry-After','0')))))
            except (urllib.error.URLError, TimeoutError):
                if attempt == 3:
                    raise RuntimeError('Massive network retry exhausted') from None
                time.sleep(2**attempt)

def inventory(root, legacy):
    records = []
    for p in sorted(legacy.glob('*.jsonl')):
        st = p.stat()
        boundary = {'first_t':None,'last_t':None,'status':'unreadable_boundary'}
        try:
            with p.open('rb') as f:
                first = f.readline()
                f.seek(max(0,st.st_size-16384))
                last = f.read().splitlines()[-1]
            boundary={'first_t':json.loads(first).get('t'),'last_t':json.loads(last).get('t'),
                      'status':'boundary_only_not_full_scan'}
        except (ValueError,IndexError,AttributeError): pass
        # All files discovered, content audit is explicitly separate and resumable.
        records.append({'ticker':p.stem,'path':str(p),'bytes':st.st_size,
                        'mtime_ns':st.st_mtime_ns,'qualification':'unverified','boundary':boundary})
    result = {'at':now(),'files':records,'count':len(records),'bytes':sum(x['bytes'] for x in records)}
    atomic(root/'inventory.json',encode(result))
    return records

def audit(root, record):
    p = Path(record['path'])
    before = p.stat()
    tmp = root/'archive'/(p.name+'.partial')
    tmp.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    counts = {'rows':0,'invalid':0,'duplicate_identical':0,'duplicate_conflict':0}
    days, sources, grains, adjustments = set(), set(), set(), set()
    seen, rejected = {}, []
    low = high = None
    with p.open('rb') as source, tmp.open('wb') as archive:
        for line_no, raw in enumerate(source,1):
            h.update(raw); archive.write(raw); counts['rows'] += 1
            try:
                row = json.loads(raw, parse_float=Decimal)
                if not isinstance(row,dict) or row.get('ticker') != p.stem:
                    raise ValueError('identity/schema')
                t = row['t']; day = date_of(t)
                audit_row=dict(row)
                if 'v' not in audit_row and 'vol' in audit_row:
                    audit_row['v']=audit_row['vol']
                normalize(audit_row,p.stem,day)
                if row.get('grain') not in ('1m','1min'):
                    raise ValueError('grain')
                days.add(day); sources.add(str(row.get('src')))
                grains.add(str(row.get('grain'))); adjustments.add(str(row.get('adjustment','unknown')))
                low = t if low is None else min(low,t)
                high = t if high is None else max(high,t)
                row_hash = digest(encode(row))
                if t in seen:
                    counts['duplicate_identical' if seen[t] == row_hash else 'duplicate_conflict'] += 1
                seen[t] = row_hash
            except (ValueError,KeyError,TypeError,ArithmeticError):
                counts['invalid'] += 1
                rejected.append({'line':line_no,'raw_sha256':digest(raw),'reason':'schema/identity/grain/value validation'})
        archive.flush(); os.fsync(archive.fileno())
    after = p.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        raise RuntimeError('source changed during archive')
    sha = h.hexdigest()
    with tmp.open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=sha:
            raise ValueError('archive hash mismatch')
    dest = root/'archive'/(sha+'.jsonl')
    if dest.exists():
        with dest.open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=sha: raise ValueError('archive collision')
        tmp.unlink()
    else:
        os.replace(tmp,dest)
    ts = sorted(seen)
    gap_count = sum(1 for a,b in zip(ts,ts[1:]) if b-a>60000 and date_of(a)==date_of(b))
    result = dict(record, **counts, sha256=sha, archive=str(dest), first_t=low,last_t=high,
                  session_dates=sorted(days), sources=sorted(sources),grains=sorted(grains),
                  adjustment_basis=sorted(adjustments),gap_intervals=gap_count,
                  gap_classification='unresolved: calendar/no-trade/vendor-absence not inferred',
                  confirmed_ranges=[], corrections=[], audit_schema=2,
                  audit_mapping={'vol':'v (validation only; archive bytes unchanged)'},audited_at=now())
    atomic(root/'quarantine'/(sha+'.json'),encode({'archive':str(dest),'invalid_rows':rejected}))
    atomic(root/'audits'/(p.stem+'.json'),encode(result))
    return result

def promote(root, ticker, day, bars, evidence, metadata):
    by_t = {}
    for bar in bars:
        row = normalize(bar,ticker,day)
        if row['t'] in by_t and by_t[row['t']] != row:
            atomic(root/'quarantine'/('conflict-'+ticker+'-'+day+'.json'),encode({'raw':evidence,'reason':'duplicate conflict'}))
            raise ValueError('conflicting provider duplicate')
        by_t[row['t']] = row
    rows = [by_t[t] for t in sorted(by_t)]
    if not rows:
        raise ValueError('empty vendor range; calendar/no-trade/absence unresolved')
    data = b''.join(encode(r) for r in rows)
    sha = digest(data)
    rel = Path('generations')/sha/'tickers'/ticker/'intraday'/(day+'.1m.jsonl')
    immutable(root/rel,data)
    back = [json.loads(line) for line in (root/rel).read_bytes().splitlines()]
    if back != rows or digest((root/rel).read_bytes())!=sha:
        raise ValueError('canonical readback failed')
    index = read(root/'index.json',{'schema':SCHEMA,'source':'Massive','owner':OWNER,'partitions':{}})
    key = ticker+'/'+day
    old = index['partitions'].get(key)
    gaps = [{'after_t':a['t'],'before_t':b['t'],'status':'vendor_absence_unclassified'}
            for a,b in zip(rows,rows[1:]) if b['t']-a['t']>60000]
    entry = {'path':str(rel),'sha256':sha,'rows':len(rows),'first_t':rows[0]['t'],
             'last_t':rows[-1]['t'],'fetched_at':evidence[-1]['fetched_at'],
             'source_confirmed_query':{'ticker':ticker,'date':day,'grain':'1m','adjusted':True},
             'raw':evidence,'reference':metadata,'gaps':gaps,'conflicts':0,
             'qualification':'source_confirmed_returned_bars','continuous_coverage':False,
             'supersedes':old['sha256'] if old and old['sha256']!=sha else (old or {}).get('supersedes')}
    # Retain every observation/revision receipt, then atomically expose complete index.
    receipt = dict(entry, ticker=ticker,day=day,outcome='unchanged' if old and old['sha256']==sha else 'published')
    immutable(root/'receipts'/(digest(encode(receipt))+'.json'),encode(receipt))
    index['partitions'][key]=entry
    atomic(root/'index.json',encode(index))
    return receipt

def fetch_day(client, ticker, day):
    symbol(ticker)
    datetime.fromisoformat(day)
    reference, ref_evidence = client.get('/v3/reference/tickers/'+urllib.parse.quote(ticker,safe=''))
    ref = reference.get('results',{})
    if ref.get('ticker')!=ticker or ref.get('market')!='stocks' or ref.get('locale')!='us' or ref.get('currency_name','').lower()!='usd':
        raise ValueError('unsupported/unverified instrument identity')
    path = '/v2/aggs/ticker/'+urllib.parse.quote(ticker,safe='')+'/range/1/minute/'+day+'/'+day+'?adjusted=true&sort=asc&limit=50000'
    bars, evidence, urls = [], [], set()
    while path:
        if path in urls or len(urls)>=10: raise ValueError('pagination loop/limit')
        urls.add(path)
        body, ev = client.get(path); evidence.append(ev)
        if body.get('status') not in ('OK','DELAYED') or body.get('ticker')!=ticker or body.get('adjusted') is not True:
            raise ValueError('unqualified vendor response')
        bars.extend(body.get('results',[]))
        path=body.get('next_url')
    return promote(client.root,ticker,day,bars,evidence,ref_evidence)

def validate_partition(root, entry, ticker, day):
    """Bind one checksum-verified byte snapshot to its requested partition."""
    query=entry.get('source_confirmed_query')
    expected={'ticker':ticker,'date':day,'grain':'1m','adjusted':True}
    if not isinstance(query,dict) or any(query.get(k)!=v for k,v in expected.items()) or query.get('adjusted') is not True:
        raise ValueError('partition query mismatch')
    path=(root/entry['path']).resolve()
    if not path.is_relative_to(root.resolve()): raise ValueError('escaped root')
    data=path.read_bytes()
    if digest(data)!=entry['sha256']: raise ValueError('checksum mismatch')
    try:
        rows=[json.loads(line) for line in data.splitlines()]
        if type(entry.get('rows')) is not int or entry['rows']<=0 or len(rows)!=entry['rows']:
            raise ValueError('partition row count mismatch')
        previous=None
        for row in rows:
            if not isinstance(row,dict) or row.get('ticker')!=ticker or row.get('session_date')!=day:
                raise ValueError('partition row identity mismatch')
            # Exact canonical shape binds schema, source, currency, grain,
            # adjustment and timezone as well as decimal-safe values and date.
            if row!=normalize(row,ticker,day):
                raise ValueError('partition row schema mismatch')
            if previous is not None and row['t']<=previous:
                raise ValueError('partition timestamps not strictly increasing')
            previous=row['t']
        if any(type(entry.get(k)) is not int for k in ('first_t','last_t')) or (rows[0]['t'],rows[-1]['t'])!=(entry['first_t'],entry['last_t']):
            raise ValueError('partition bounds mismatch')
    except (KeyError,TypeError,ArithmeticError) as exc:
        raise ValueError('invalid partition row or manifest') from exc
    return path

def resolve(pointer, ticker, day, required_through=None, max_age_seconds=1200):
    """Local-only resolution. The consumer cannot fetch or pretend missing data is fresh."""
    symbol(ticker)
    cfg=read(Path(pointer))
    if not isinstance(cfg,dict) or cfg.get('schema')!=SCHEMA:
        raise ValueError('incompatible resolver pointer')
    root=Path(cfg['root'])
    index=read(root/'index.json')
    if index is not None and (not isinstance(index,dict) or index.get('schema')!=SCHEMA or index.get('source')!='Massive' or not isinstance(index.get('partitions'),dict)):
        raise ValueError('incompatible partition index')
    entry=index['partitions'].get(ticker+'/'+day) if index is not None else None
    reason=None
    if not entry: reason='missing'
    elif entry['conflicts'] or entry['qualification']!='source_confirmed_returned_bars': reason='unqualified'
    else:
        path=validate_partition(root,entry,ticker,day)
        if required_through is not None and (entry['last_t']<required_through or (datetime.now(UTC)-datetime.fromisoformat(entry['fetched_at'])).total_seconds()>max_age_seconds): reason='stale'
    if reason:
        request={'ticker':ticker,'date':day,'reason':reason,'required_through':required_through,'owner':OWNER}
        payload=encode(request)
        # Content-addressed requests avoid overwriting another consumer's request.
        target=root/'requests'/(digest(payload)+'.json')
        target.parent.mkdir(parents=True,exist_ok=True)
        try:
            with target.open('xb') as f: f.write(payload)
        except FileExistsError: pass
        return {'status':'refresh_required','request':str(target),'reason':reason}
    return dict(entry,status='qualified_historical' if required_through is None else 'qualified_current',path=str(path))

def run(args):
    root=Path(args.root)
    with writer(root):
        records=inventory(root,Path(args.legacy))
        done=[]
        for record in sorted(records,key=lambda r:(r['ticker']!='NVDA',r['ticker'])):
            previous=read(root/'audits'/(record['ticker']+'.json'))
            if previous and previous.get('audit_schema')==2 and previous['bytes']==record['bytes'] and previous['mtime_ns']==record['mtime_ns']: continue
            if len(done)>=args.audit_batch: break
            if (root/'STOP').exists(): break
            done.append(audit(root,record)['ticker'])
        pointer={'schema':SCHEMA,'root':str(root.resolve()),'source':'Massive','owner':OWNER,
                 'resolver':'runtime.massive_maintainer.maintain.resolve','index':'index.json',
                 'freshness':'explicit required_through and max_age_seconds; no silent fallback',
                 'refresh_interface':'requests/*.json; resume same branch entrypoint',
                 'coverage':'index.json partitions only; all other dates unverified',
                 'legacy_root':args.legacy,'automatic_refresh_enabled':False}
        atomic(root/'_MAP'/'massive-local.json',encode(pointer))
        client=Massive(root,Path(args.key_file))
        results=[]
        plans=[(args.ticker,d) for d in args.dates.split(',') if d]
        requests=[]
        for path in sorted((root/'requests').glob('*.json')):
            if (root/'fulfilled' / path.name).exists(): continue
            request=read(path)
            requests.append((path,request))
            plans.append((request['ticker'],request['date']))
            if len(requests)>=2: break
        index=read(root/'index.json',{'partitions':{}})
        history_count=0
        for path in sorted((root/'audits').glob('*.json'),key=lambda p:(p.stem!='NVDA',p.stem)):
            audit_record=read(path)
            for day in audit_record['session_dates']:
                key=path.stem+'/'+day
                if key in index['partitions']: continue
                if history_count>=args.history_batch: break
                plans.append((path.stem,day)); history_count+=1
        for ticker,day in dict.fromkeys(plans):
            try:
                result=fetch_day(client,ticker,day)
                results.append(result)
                for path,request in requests:
                    if (request['ticker'],request['date'])==(ticker,day) and (request.get('required_through') is None or result['last_t']>=request['required_through']):
                        atomic(root/'fulfilled'/path.name,encode({'request':request,'result':result['sha256'],'at':now()}))
            except Exception as exc:
                results.append({'ticker':ticker,'day':day,'status':'blocked','error_type':type(exc).__name__,
                                'reason':str(exc) if isinstance(exc,(ValueError,RuntimeError)) else 'OS/network error; no secrets logged'})
                break
        receipt={'at':now(),'owner':OWNER,'inventory_files':len(records),'audited_this_run':done,
                 'provider_calls':client.calls,'results':results,'pointer':str(root/'_MAP'/'massive-local.json'),
                 'full_history_confirmed':False,'next_batch':'resume unaudited roster and first unconfirmed audited session; review absent session dates separately'}
        atomic(root/'progress.json',encode(receipt))
        immutable(root/'runs'/(digest(encode(receipt))+'.json'),encode(receipt))
        print(json.dumps(receipt,indent=2))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',required=True); p.add_argument('--legacy',required=True)
    p.add_argument('--key-file',required=True); p.add_argument('--ticker',default='NVDA')
    today=datetime.now(ET).date()
    p.add_argument('--dates',default=','.join([(today-timedelta(days=1)).isoformat(),today.isoformat()]))
    p.add_argument('--audit-batch',type=int,default=2)
    p.add_argument('--history-batch',type=int,default=1)
    run(p.parse_args())

if __name__=='__main__': main()
