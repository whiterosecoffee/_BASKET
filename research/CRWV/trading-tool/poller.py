"""Separately hosted REST polling adapter. No embedded credentials or background launch.
Requires MASSIVE_API_KEY on the HOST; the ChatGPT connector doesn't expose it.
Consumes qualifying aggregates, not full tape/NBBO. Corrected history fails closed.
"""
import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from patterns import ET, MINUTE, session, validate_bars
from store import capture, connect

HOST = 'https://api.massive.com'


def get_json(path, params, key):
    # Header auth avoids credentials in query strings, stored manifests and logs.
    url = HOST+path+'?'+urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer '+key})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        raise RuntimeError('Massive HTTP '+str(e.code)) from None
    except urllib.error.URLError:
        raise RuntimeError('Massive network error') from None


def aggregates(ticker, start, end, key, fetch=get_json, max_pages=20):
    ticker = urllib.parse.quote(ticker, safe='')
    path = f'/v2/aggs/ticker/{ticker}/range/1/minute/{start}/{end}'
    params = {'adjusted': 'true', 'sort': 'asc', 'limit': 50000}
    rows = []
    seen = set()
    for _ in range(max_pages):
        page = fetch(path, params, key)
        if page.get('status') in ('ERROR', 'NOT_AUTHORIZED', 'NOT_ENTITLED'):
            raise RuntimeError('Massive provider access/error state')
        rows.extend(page.get('results', []))
        next_url = page.get('next_url')
        if not next_url:
            break
        parsed = urllib.parse.urlparse(next_url)
        if parsed.scheme != 'https' or parsed.netloc != 'api.massive.com' or not parsed.path.startswith('/v2/aggs/ticker/'):
            raise ValueError('untrusted pagination destination')
        if next_url in seen:
            raise ValueError('pagination loop')
        seen.add(next_url)
        path, params = parsed.path, dict(urllib.parse.parse_qsl(parsed.query))
        params.pop('apiKey', None)
    else:
        raise ValueError('bounded pagination exceeded')
    # Reject conflicting duplicate vendor bars instead of silently overwriting.
    unique = {}
    for b in rows:
        out = {k: b[k] for k in ('t', 'o', 'h', 'l', 'c', 'v', 'vw')}
        if out['t'] in unique and unique[out['t']] != out:
            raise ValueError('conflicting duplicate bar')
        unique[out['t']] = out
    result = sorted(unique.values(), key=lambda b: b['t'])
    validate_bars(result)
    return result


def health(now, market_open, latest_end, feed_mode, threshold=120):
    age = (now-latest_end)/1000 if latest_end is not None else None
    state = 'market_closed' if not market_open else 'missing' if age is None else 'fresh' if age <= threshold and feed_mode == 'realtime_verified' else 'delayed_or_stale'
    return {'state': state, 'as_of': latest_end, 'observed_at': now, 'lag_seconds': age,
            'fresh_for_current_inference': state == 'fresh', 'feed_mode': feed_mode}


def cycle(db_path, ticker, key, feed_mode, context, now=None, fetch=get_json):
    now = now or int(time.time()*1000)
    market = fetch('/v1/marketstatus/now', {}, key)
    market_open = market.get('market') == 'open'
    # At most one current ET day; checkpointed local history supplies older prefix.
    # Weekend/holiday detection comes from provider market status, not weekdays.
    day = session(now)
    data = aggregates(ticker, day, day, key, fetch)
    completed = [b for b in data if b['t']+MINUTE <= now]
    end = max((b['t']+MINUTE for b in completed), default=None)
    health_state = health(now, market_open, end, feed_mode)
    if not completed:
        return health_state
    with connect(db_path) as db:
        old = db.execute('SELECT generation FROM checkpoints WHERE ticker=? ORDER BY seq DESC LIMIT 1', (ticker,)).fetchone()
        stored = [json.loads(r[0]) for r in db.execute('SELECT payload FROM observations WHERE ticker=? AND generation=? ORDER BY t', (ticker, old[0]))] if old else []
    merged = {b['t']: b for b in stored}
    for b in completed:
        if b['t'] in merged and merged[b['t']] != b:
            raise ValueError('vendor revision: halt; audit and explicit rebuild required')
        merged[b['t']] = b
    source = {'source_id': 'massive-rest-minute-v1', 'provider': 'Massive',
              'entitlement': feed_mode, 'observation_kind': 'realtime' if feed_mode == 'realtime_verified' else 'delayed',
              'retrieved_at': datetime.fromtimestamp(now/1000, timezone.utc).isoformat(),
              'available_at': None, 'adjustment': 'split-adjusted'}
    batch = dict(context, ticker=ticker, bars=sorted(merged.values(), key=lambda b: b['t']), source=source)
    result = capture(db_path, batch, now)
    return dict(health_state, new_signals=result['new_signals'], generation=result['generation'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ticker', required=True); p.add_argument('--db', required=True)
    p.add_argument('--context', required=True, help='JSON daily/profiles/patterns; pin before a generation')
    p.add_argument('--feed-mode', choices=('delay_unknown', 'delayed', 'realtime_verified'), default='delay_unknown')
    p.add_argument('--interval', type=float, default=60); p.add_argument('--cycles', type=int, default=1)
    p.add_argument('--health', required=True)
    a = p.parse_args()
    if a.interval < 15 or a.cycles < 0:
        p.error('interval >=15; cycles >=0 (0 means service loop)')
    key = os.environ.get('MASSIVE_API_KEY')
    if not key:
        p.error('host MASSIVE_API_KEY required; connector credentials are unavailable')
    context = json.loads(Path(a.context).read_text())
    count = 0
    while a.cycles == 0 or count < a.cycles:
        try:
            status = cycle(a.db, a.ticker, key, a.feed_mode, context)
        except Exception as e:
            # Preserve failed source; do not carry an old healthy state forward.
            status = {'state': 'error', 'fresh_for_current_inference': False,
                      'error_class': type(e).__name__, 'observed_at': int(time.time()*1000)}
            Path(a.health).write_text(json.dumps(status))
            print(json.dumps(status), flush=True)
            raise SystemExit(1) from None
        Path(a.health).write_text(json.dumps(status))
        print(json.dumps(status), flush=True)
        count += 1
        if a.cycles == 0 or count < a.cycles:
            time.sleep(a.interval)


if __name__ == '__main__':
    main()
