"""Bounded, restartable Massive US-equity minute ingestion and local qualification.

Decimal values are encoded as strings, never converted through binary float.
Legacy archives are evidence only, never promoted without source confirmation.
"""
import argparse
import contextlib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import time
import threading
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

UTC = timezone.utc
ET = ZoneInfo('America/New_York')
SCHEMA = 'basket.massive.minute@1'
OWNER = 'work/local-20261112-massive-maintainer'
_WRITER_CONTEXT = threading.local()
_EXPECTED_UNSET = object()
MAX_CURRENT_AGE_SECONDS = 1200

class FreshnessContractError(ValueError):
    code='invalid_freshness_budget'
    field='max_age_seconds'

    def __init__(self):
        super().__init__('max_age_seconds must be a finite int or float in (0, 1200]')


def validate_freshness(value):
    # Check the bounded range before isfinite: huge integers must not overflow
    # during implicit conversion. Booleans and numeric subclasses are excluded.
    if type(value) not in (int,float) or not 0<value<=MAX_CURRENT_AGE_SECONDS or not math.isfinite(value):
        raise FreshnessContractError()
    return value


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
        previous=getattr(_WRITER_CONTEXT,'root',None)
        _WRITER_CONTEXT.root=root.resolve()
        try:
            yield
        finally:
            _WRITER_CONTEXT.root=previous
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


def quarantine_response(root, reason, evidence, ticker=None, day=None, error_type=None):
    """Immutable disposition over verified raw bytes and sanitized request scope.

    Observation timestamps remain in raw-receipts; excluding them here makes the
    same rejection of the same bytes/request idempotent across refetch attempts.
    """
    proofs={}
    for ev in evidence:
        if ev is None: continue
        sha=ev['sha256']
        if not isinstance(sha,str) or not re.fullmatch(r'[0-9a-f]{64}',sha):
            raise ValueError('invalid quarantine raw identity')
        rel='raw/'+sha+'.json'
        if digest((root/rel).read_bytes())!=sha:
            raise ValueError('quarantine raw checksum mismatch')
        proof={k:ev[k] for k in ('endpoint','request_params','method','source') if k in ev}
        proof.update(sha256=sha,path=rel)
        proofs[digest(encode(proof))]=proof
    if not proofs: return None
    receipt={'schema':'basket.massive.quarantine@1','status':'quarantined',
             'reason':reason,'error_type':error_type,'ticker':ticker,'date':day,
             'raw':[proofs[k] for k in sorted(proofs)]}
    path=root/'quarantine'/('response-'+digest(encode(receipt))+'.json')
    immutable(path,encode(receipt))
    return path


class RetryDeferred(RuntimeError):
    """Durable retry disposition; callers must not treat it as a fresh attempt."""


def retry_minimum(headers, received_at):
    value=headers.get('Retry-After')
    if value is None: return 0.0
    value=value.strip()
    if re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',value):
        seconds=float(value)
        if seconds<float('inf'): return seconds
        raise ValueError('invalid retry header')
    target=parsedate_to_datetime(value)
    if target.tzinfo is None: raise ValueError('invalid retry date')
    seconds=max(0.0,(target-received_at).total_seconds())
    # Server Date protects against a local clock running ahead of the server.
    if headers.get('Date'):
        server=parsedate_to_datetime(headers['Date'])
        if server.tzinfo is None: raise ValueError('invalid server date')
        seconds=max(seconds,(target-server).total_seconds())
    return seconds


class Massive:
    def __init__(self, root, key_file, wait_budget_seconds=30):
        self.root, self.key_file, self.calls = root, key_file, 0
        self.last = 0
        if type(wait_budget_seconds) not in (int,float) or not 0<=wait_budget_seconds<=30:
            raise ValueError('wait budget must be between zero and 30 seconds')
        self.wait_remaining=wait_budget_seconds
        self.retry_until_monotonic=0

    def defer(self, request, seconds, status='retry_deferred'):
        received=datetime.fromisoformat(now())
        try:
            until=(received+timedelta(seconds=seconds)).isoformat() if seconds is not None else None
        except OverflowError:
            until=None; status='retry_header_review_required'
        receipt=dict(request,status=status,received_at=received.isoformat(),
                     minimum_wait_seconds=seconds,retry_not_before=until)
        immutable(self.root/'retry-receipts'/(digest(encode(receipt))+'.json'),encode(receipt))
        atomic(self.root/'retry-after.json',encode(receipt))
        if seconds is not None: self.retry_until_monotonic=time.monotonic()+seconds
        raise RetryDeferred('Massive request deferred; see retry-after.json')

    def check_deferred(self):
        receipt=read(self.root/'retry-after.json')
        if receipt is None: return
        until=receipt.get('retry_not_before')
        if until is None or time.monotonic()<self.retry_until_monotonic or datetime.fromisoformat(now())<datetime.fromisoformat(until):
            raise RetryDeferred('Massive request deferred; see retry-after.json')


    def get(self, path):
        self.last_evidence=None
        url = 'https://api.massive.com' + path if path.startswith('/') else path
        u = urllib.parse.urlsplit(url)
        if u.scheme != 'https' or u.netloc != 'api.massive.com':
            raise ValueError('unapproved provider URL')
        q = [(k,v) for k,v in urllib.parse.parse_qsl(u.query,keep_blank_values=True) if k.lower() != 'apikey']
        allowed={'adjusted','sort','limit','date','cursor','order','timestamp','timestamp.gte','timestamp.gt','timestamp.lte','timestamp.lt'}
        if any(k not in allowed for k,v in q):
            raise ValueError('unapproved request parameter; no request sent')
        url = urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,urllib.parse.urlencode(q),''))
        key = self.key_file.read_text(encoding='utf-8-sig').strip()
        if not key:
            raise ValueError('empty credential')
        if key in urllib.parse.unquote(u.path) or any(key in k or key in v for k,v in q):
            raise ValueError('credential in request scope; no request sent')
        request_evidence={'endpoint':u.path,'request_params':[[k,v] for k,v in q],
                          'method':'GET','source':'Massive'}
        self.check_deferred()
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
                received_at=now()
                evidence=dict(request_evidence,sha256=sha,path='raw/'+sha+'.json',
                              fetched_at=received_at,response_received_at=received_at,
                              response_identity='sha256:'+sha)
                self.last_evidence=evidence
                immutable(self.root/'raw-receipts'/(digest(encode(evidence))+'.json'),encode(evidence))
                try:
                    body = json.loads(raw, parse_float=Decimal)
                except (ValueError,UnicodeError) as exc:
                    quarantine_response(self.root,'response_parse_invalid',[evidence],error_type=type(exc).__name__)
                    raise
                return body, evidence
            except urllib.error.HTTPError as e:
                if e.code not in (429,500,502,503,504):
                    raise RuntimeError('Massive HTTP '+str(e.code)) from None
                try:
                    seconds=max(2**attempt,retry_minimum(e.headers,datetime.fromisoformat(now())))
                except (ValueError,TypeError,OverflowError):
                    self.defer(request_evidence,None,'retry_header_review_required')
                if attempt==3 or seconds>self.wait_remaining:
                    self.defer(request_evidence,seconds)
                self.wait_remaining-=seconds
                time.sleep(seconds)
            except (urllib.error.URLError, TimeoutError):
                if attempt == 3:
                    raise RuntimeError('Massive network retry exhausted') from None
                seconds=2**attempt
                if seconds>self.wait_remaining: self.defer(request_evidence,seconds)
                self.wait_remaining-=seconds
                time.sleep(seconds)

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

def partition_snapshot(root, ticker, day):
    path=root/'index.json'
    raw=path.read_bytes() if path.exists() else None
    index=json.loads(raw) if raw is not None else {'schema':SCHEMA,'source':'Massive','owner':OWNER,'partitions':{}}
    if not isinstance(index,dict) or index.get('schema')!=SCHEMA or index.get('source')!='Massive' or not isinstance(index.get('partitions'),dict):
        raise ValueError('invalid publication index')
    entry=index['partitions'].get(ticker+'/'+day)
    if entry is None: return raw,index,None
    if not isinstance(entry,dict) or not isinstance(entry.get('sha256'),str) or not re.fullmatch(r'[0-9a-f]{64}',entry['sha256']):
        raise ValueError('invalid current partition head')
    return raw,index,entry['sha256']


def partition_head(root, ticker, day):
    return partition_snapshot(root,ticker,day)[2]


def promote(root, ticker, day, bars, evidence, metadata, *, expected_head=_EXPECTED_UNSET, source_status="unknown", pagination_complete=False):
    if expected_head is _EXPECTED_UNSET or (expected_head is not None and (not isinstance(expected_head,str) or not re.fullmatch(r'[0-9a-f]{64}',expected_head))):
        raise ValueError('explicit expected head required: null absence or SHA-256')
    # Reuse only this thread's existing writer authority; direct callers acquire
    # the same lock, never a second independent publication lock.
    guard=contextlib.nullcontext() if getattr(_WRITER_CONTEXT,'root',None)==root.resolve() else writer(root)
    with guard:
        return _promote_owned(root,ticker,day,bars,evidence,metadata,expected_head=expected_head,
                              source_status=source_status,pagination_complete=pagination_complete)


def _promote_owned(root, ticker, day, bars, evidence, metadata, *, expected_head, source_status, pagination_complete):
    index_bytes,index,current=partition_snapshot(root,ticker,day)
    if current!=expected_head: raise ValueError('expected head mismatch')
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
    key = ticker+'/'+day
    old = index['partitions'].get(key)
    gaps = [{'after_t':a['t'],'before_t':b['t'],'status':'vendor_absence_unclassified'}
            for a,b in zip(rows,rows[1:]) if b['t']-a['t']>60000]
    entry = {'path':str(rel),'sha256':sha,'rows':len(rows),'first_t':rows[0]['t'],
             'last_t':rows[-1]['t'],'fetched_at':evidence[-1]['fetched_at'],
             'source_confirmed_query':{'ticker':ticker,'date':day,'grain':'1m','adjusted':True},
             'raw':evidence,'reference':metadata,'gaps':gaps,'conflicts':0,
             'source_status':source_status,'pagination_complete':pagination_complete,
             'instrument_identity':metadata.get('instrument_identity'),
             'qualification':'source_confirmed_returned_bars','continuous_coverage':False,
             'supersedes':old['sha256'] if old and old['sha256']!=sha else (old or {}).get('supersedes')}
    # Retain every observation/revision receipt, then atomically expose complete index.
    receipt = dict(entry, ticker=ticker,day=day,outcome='unchanged' if old and old['sha256']==sha else 'published')
    prepared=dict(receipt,outcome='prepared',expected_head=expected_head)
    immutable(root/'receipts'/(digest(encode(prepared))+'.json'),encode(prepared))
    latest_bytes,latest,current=partition_snapshot(root,ticker,day)
    if current!=expected_head or latest_bytes!=index_bytes:
        raise ValueError('publication index changed after staging')
    latest['partitions'][key]=entry
    atomic(root/'index.json',encode(latest))
    return receipt

def fetch_day(client, ticker, day):
    symbol(ticker)
    datetime.fromisoformat(day)
    retained=[]
    expected_head=partition_head(client.root,ticker,day)
    stage='reference_request_incomplete'
    try:
        reference, ref_evidence = client.get('/v3/reference/tickers/'+urllib.parse.quote(ticker,safe='')+'?date='+day)
        retained.append(ref_evidence)
        stage='reference_identity_or_schema_invalid'
        if not isinstance(reference,dict) or not isinstance(reference.get('results'),dict):
            raise ValueError('invalid reference schema')
        ref = reference['results']
        if ref.get('ticker')!=ticker or ref.get('market')!='stocks' or ref.get('locale')!='us' or not isinstance(ref.get('currency_name'),str) or ref['currency_name'].lower()!='usd':
            raise ValueError('unsupported/unverified instrument identity')
        identity={k:ref.get(k) for k in ('cik','composite_figi','share_class_figi','primary_exchange','type')}
        if not any(isinstance(identity[k],str) and identity[k].strip() for k in ('cik','composite_figi','share_class_figi')):
            raise ValueError('stable instrument identity unavailable')
        if any(v is not None and (not isinstance(v,str) or not v.strip()) for v in identity.values()):
            raise ValueError('invalid instrument identity')
        prior=read(client.root/'index.json',{'partitions':{}})
        for key,entry in prior['partitions'].items():
            if key.startswith(ticker+'/') and entry.get('instrument_identity')!=identity:
                raise ValueError('instrument identity continuity unresolved')
        ref_evidence=dict(ref_evidence,instrument_identity=identity,reference_date=day)
        path = '/v2/aggs/ticker/'+urllib.parse.quote(ticker,safe='')+'/range/1/minute/'+day+'/'+day+'?adjusted=true&sort=asc&limit=50000'
        bars, evidence, urls, statuses = [], [], set(), []
        while path:
            stage='pagination_incomplete'
            if not isinstance(path,str) or path in urls or len(urls)>=10: raise ValueError('pagination loop/limit/schema')
            urls.add(path)
            body, ev = client.get(path); evidence.append(ev); retained.append(ev)
            stage='aggregate_identity_or_schema_invalid'
            if not isinstance(body,dict) or body.get('status') not in ('OK','DELAYED') or body.get('ticker')!=ticker or body.get('adjusted') is not True:
                raise ValueError('unqualified vendor response')
            statuses.append(body['status'])
            rows=body.get('results',[])
            if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows):
                raise ValueError('invalid aggregate results schema')
            bars.extend(rows)
            path=body.get('next_url')
            if path is not None and not isinstance(path,str):
                raise ValueError('invalid pagination schema')
        stage='partition_validation_or_publication_failed'
        return promote(client.root,ticker,day,bars,evidence,ref_evidence,expected_head=expected_head,source_status="OK" if all(x=="OK" for x in statuses) else "DELAYED",pagination_complete=True)
    except (ValueError,KeyError,TypeError,AttributeError,ArithmeticError,RuntimeError,OSError) as exc:
        # A page may have persisted but failed parsing before get() returned.
        retained.append(getattr(client,'last_evidence',None))
        quarantine_response(client.root,stage,retained,ticker,day,type(exc).__name__)
        raise


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



PURPOSES=('historical','historical_interval','as_of','latest_complete')


def purpose_contract(purpose, required, as_of=None):
    purpose=('historical' if required is None else 'latest_complete') if purpose is None else purpose
    if not isinstance(purpose,str) or purpose not in PURPOSES:
        raise ValueError('invalid data purpose')
    if (purpose=='historical')!=(required is None):
        raise ValueError('purpose requires matching interval contract')
    if purpose=='as_of':
        if not isinstance(as_of,str): raise ValueError('as_of requires an aware ISO timestamp')
        try: cutoff=datetime.fromisoformat(as_of)
        except ValueError: raise ValueError('as_of requires an aware ISO timestamp') from None
        if cutoff.tzinfo is None: raise ValueError('as_of requires an aware ISO timestamp')
    elif as_of is not None:
        raise ValueError('as_of cutoff requires as_of purpose')
    return purpose


def coverage_ineligibility(root, entry, day, required, coverage, *, latest=False):
    """Coverage and basis checks have no wall-clock expiration."""
    if not isinstance(coverage,dict): return 'coverage_unknown'
    try:
        start,end=coverage['start_t'],coverage['end_t']
        if type(start) is not int or type(end) is not int or start>end or end!=required or date_of(start)!=day or date_of(end)!=day:
            return 'coverage_unknown'
        if coverage.get('completion')!='all_minutes_present' or coverage.get('timezone')!='America/New_York' or coverage.get('adjustment')!='split_adjusted':
            return 'coverage_unknown'
        windows={'PRE':(240,570),'RTH':(570,960),'AH':(960,1200)}
        low,high=windows[coverage['session']]
        for stamp in (start,end):
            local=datetime.fromtimestamp(stamp/1000,UTC).astimezone(ET)
            if not low<=local.hour*60+local.minute<high: return 'coverage_unknown'
    except (ValueError,KeyError,TypeError,OverflowError):
        return 'coverage_unknown'
    if latest and entry.get('source_status')=='DELAYED': return 'source_delayed'
    if entry.get('source_status') not in ('OK','DELAYED') or entry.get('pagination_complete') is not True: return 'source_status_unknown'
    rows=[json.loads(line) for line in (root/entry['path']).read_bytes().splitlines()]
    stamps=[r['t'] for r in rows if start<=r['t']<=end]
    if stamps!=list(range(start,end+60000,60000)): return 'coverage_unresolved'
    return None


def current_ineligibility(root, entry, day, required, max_age, coverage):
    """Recency is a policy for latest use, not the lifetime of historical truth."""
    validate_freshness(max_age)
    reason=coverage_ineligibility(root,entry,day,required,coverage,latest=True)
    if reason: return reason
    end=coverage['end_t']
    clock=datetime.fromisoformat(now())
    observation_age=clock.timestamp()-(end+60000)/1000
    if observation_age<0: return 'observation_not_complete'
    if observation_age>max_age: return 'stale_observation'
    fetch_age=(clock-datetime.fromisoformat(entry['fetched_at'])).total_seconds()
    if not 0<=fetch_age<=max_age: return 'stale'
    return None


def purpose_ineligibility(root, entry, day, required, max_age, coverage, purpose, as_of=None):
    purpose=purpose_contract(purpose,required,as_of)
    if purpose=='historical': return None
    if purpose=='latest_complete':
        return current_ineligibility(root,entry,day,required,max_age,coverage)
    reason=coverage_ineligibility(root,entry,day,required,coverage)
    if reason or purpose=='historical_interval': return reason
    cutoff=datetime.fromisoformat(as_of)
    # The returned file exposes the entire partition: reject any later event,
    # not only later events inside the requested subinterval.
    if datetime.fromtimestamp((entry['last_t']+60000)/1000,UTC)>cutoff:
        return 'event_after_as_of'
    try:
        evidence=entry['raw']
        if not isinstance(evidence,list) or not evidence: return 'vintage_availability_unknown'
        values=[entry['fetched_at']]+[ev['fetched_at'] for ev in evidence]
        reference=entry.get('reference')
        if isinstance(reference,dict) and 'fetched_at' in reference: values.append(reference['fetched_at'])
        observed=[datetime.fromisoformat(value) for value in values]
        if any(value.tzinfo is None for value in observed): return 'vintage_availability_unknown'
    except (KeyError,ValueError,TypeError):
        return 'vintage_availability_unknown'
    if max(observed)>cutoff: return 'vintage_after_as_of'
    return None


def resolve(pointer, ticker, day, required_through=None, max_age_seconds=1200, *, coverage=None, purpose=None, as_of=None):
    """Local-only resolution. The consumer cannot fetch or pretend missing data is fresh."""
    purpose=purpose_contract(purpose,required_through,as_of)
    if purpose=='latest_complete': validate_freshness(max_age_seconds)
    symbol(ticker)
    cfg=read(Path(pointer))
    if not isinstance(cfg,dict) or cfg.get('schema')!=SCHEMA:
        raise ValueError('incompatible resolver pointer')
    root_value=cfg.get('root')
    if not isinstance(root_value,str) or not root_value.strip() or '\x00' in root_value or not Path(root_value).is_absolute():
        raise ValueError('invalid resolver root: expected an absolute non-empty path string')
    root=Path(root_value)
    index=read(root/'index.json')
    if index is not None and (not isinstance(index,dict) or index.get('schema')!=SCHEMA or index.get('source')!='Massive' or not isinstance(index.get('partitions'),dict)):
        raise ValueError('incompatible partition index')
    entry=index['partitions'].get(ticker+'/'+day) if index is not None else None
    reason=None
    if not entry: reason='missing'
    elif entry['conflicts'] or entry['qualification']!='source_confirmed_returned_bars': reason='unqualified'
    else:
        path=validate_partition(root,entry,ticker,day)
        reason=purpose_ineligibility(root,entry,day,required_through,max_age_seconds,coverage,purpose,as_of)
    if reason:
        request={'ticker':ticker,'date':day,'reason':reason,'required_through':required_through,'max_age_seconds':max_age_seconds if purpose=='latest_complete' else None,'coverage':coverage,'purpose':purpose,'as_of':as_of,'owner':OWNER}
        payload=encode(request)
        # Content-addressed requests avoid overwriting another consumer's request.
        target=root/'requests'/(digest(payload)+'.json')
        target.parent.mkdir(parents=True,exist_ok=True)
        try:
            with target.open('xb') as f: f.write(payload)
        except FileExistsError: pass
        return {'status':'refresh_required' if purpose=='latest_complete' else 'reconciliation_required','request':str(target),'reason':reason,'purpose':purpose}
    status='qualified_current' if purpose=='latest_complete' else 'qualified_as_of' if purpose=='as_of' else 'qualified_historical'
    return dict(entry,status=status,path=str(path),purpose=purpose,qualified_scope=coverage,as_of=as_of)


def fulfilled_request_is_current(root, request):
    """A fulfilment marker is history, not perpetual freshness authority.

    Recheck the actual local snapshot before suppressing repeated demand.
    Invalid indexed bytes fail closed; they do not authorize acquisition.
    Legacy requests retain the resolver's original 1200-second age default.
    """
    purpose=purpose_contract(request.get('purpose'),request.get('required_through'),request.get('as_of'))
    if purpose=='latest_complete': validate_freshness(request.get('max_age_seconds',1200))
    index=read(root/'index.json')
    if index is None:
        return False
    if not isinstance(index,dict) or index.get('schema')!=SCHEMA or index.get('source')!='Massive' or not isinstance(index.get('partitions'),dict):
        raise ValueError('incompatible partition index')
    ticker,day=request['ticker'],request['date']
    entry=index['partitions'].get(ticker+'/'+day)
    if not entry or entry.get('conflicts') or entry.get('qualification')!='source_confirmed_returned_bars':
        return False
    validate_partition(root,entry,ticker,day)
    required=request.get('required_through')
    max_age=request.get('max_age_seconds',1200)
    return purpose_ineligibility(root,entry,day,required,max_age,request.get('coverage'),purpose,request.get('as_of')) is None



def validate_request(request):
    if not isinstance(request,dict): raise ValueError('invalid request object')
    symbol(request.get('ticker',''))
    day=request.get('date')
    if not isinstance(day,str) or datetime.strptime(day,'%Y-%m-%d').strftime('%Y-%m-%d')!=day:
        raise ValueError('invalid request date')
    required=request.get('required_through')
    if required is not None and (type(required) is not int or date_of(required)!=day):
        raise ValueError('invalid required_through')
    purpose=purpose_contract(request.get('purpose'),required,request.get('as_of'))
    if purpose=='latest_complete': validate_freshness(request.get('max_age_seconds',1200))


def require_admission(args, root, records, ticker, day):
    """Owner-supplied, one-day admission; consumer demand never grants access.

    Conservative scope: any discovered legacy file for this symbol blocks.
    Existing indexed dates require a separate refresh contract, not this permit.
    References are owner attestations, not cryptographic entitlement proof.
    """
    validate_request({'ticker':ticker,'date':day})
    if not Path(args.legacy).is_dir(): raise ValueError('legacy_inventory_unavailable')
    path=getattr(args,'admission_file',None)
    if not path: raise ValueError('admission_required')
    permit=read(Path(path))
    expected={'schema':'basket.massive.admission@1','owner':OWNER,'source':'Massive',
              'ticker':ticker,'date':day,'grain':'1m','adjustment':'split_adjusted',
              'purpose':'acquire_absent_day','legacy_root':str(Path(args.legacy).resolve())}
    if not isinstance(permit,dict) or any(permit.get(k)!=v for k,v in expected.items()):
        raise ValueError('admission_scope_mismatch')
    for key in ('authorization_ref','entitlement_ref'):
        if not isinstance(permit.get(key),str) or not permit[key].strip():
            raise ValueError('admission_evidence_missing')
    expires=datetime.fromisoformat(permit.get('expires_at',''))
    if expires.tzinfo is None or not 0<(expires-datetime.now(UTC)).total_seconds()<=3600:
        raise ValueError('admission_expired_or_unbounded')
    if permit.get('inventory_sha256')!=digest(encode(records)):
        raise ValueError('admission_inventory_changed')
    if any(r['ticker'].upper()==ticker for r in records):
        raise ValueError('existing_legacy_requires_reconciliation')
    # Recheck local inventory metadata immediately before dispatch, without audit
    # or source writes. Unknown local files are never interpreted as absent bars.
    current=[(str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in sorted(Path(args.legacy).glob('*.jsonl'))]
    observed=[(r['path'],r['bytes'],r['mtime_ns']) for r in records]
    if current!=observed: raise ValueError('admission_inventory_changed')
    index_path=root/'index.json'
    raw=index_path.read_bytes() if index_path.exists() else None
    if 'index_sha256' not in permit or permit['index_sha256']!=(digest(raw) if raw is not None else None):
        raise ValueError('admission_index_changed')
    index=json.loads(raw) if raw is not None else None
    if index is not None:
        if not isinstance(index,dict) or index.get('schema')!=SCHEMA or not isinstance(index.get('partitions'),dict):
            raise ValueError('incompatible partition index')
        if ticker+'/'+day in index['partitions']:
            raise ValueError('existing_partition_requires_refresh_contract')
    return digest(encode(permit))


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
            try:
                request=read(path)
                validate_request(request)
                if (root/'fulfilled' / path.name).exists() and fulfilled_request_is_current(root,request):
                    continue
            except (ValueError,KeyError,TypeError,OSError) as exc:
                raw=path.read_bytes()
                disposition={'status':'quarantined','request_sha256':digest(raw),
                             'request_file':path.name,'reason':'invalid_request_or_snapshot',
                             'error_type':type(exc).__name__,'contract_error':getattr(exc,'code',None)}
                immutable(root/'quarantine'/('request-'+digest(raw)+'.json'),encode(disposition))
                results.append(disposition)
                continue
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
                admission_sha=require_admission(args,root,records,ticker,day)
            except (ValueError,KeyError,TypeError,OSError):
                results.append({'ticker':ticker,'day':day,'status':'blocked',
                                'reason':'admission_missing_invalid_or_local_history_present'})
                continue
            try:
                result=fetch_day(client,ticker,day)
                result['admission_sha256']=admission_sha
                results.append(result)
                for path,request in requests:
                    if (request['ticker'],request['date'])==(ticker,day) and fulfilled_request_is_current(root,request):
                        atomic(root/'fulfilled'/path.name,encode({'request':request,'result':result['sha256'],'at':now()}))
            except RetryDeferred:
                results.append({'ticker':ticker,'day':day,'status':'deferred','retry_receipt':'retry-after.json'})
                break
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
    p.add_argument('--admission-file',help='owner-issued one-day absent-range permit; no implicit acquisition')
    today=datetime.now(ET).date()
    p.add_argument('--dates',default=','.join([(today-timedelta(days=1)).isoformat(),today.isoformat()]))
    p.add_argument('--audit-batch',type=int,default=2)
    p.add_argument('--history-batch',type=int,default=1)
    run(p.parse_args())

if __name__=='__main__': main()
