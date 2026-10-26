"""Composition only: immutable external domain outputs, never trading calculations."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import html
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlparse

CONFIG = Path(__file__).with_name('orcl.json')


def stamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be an ISO string')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timestamp needs timezone')
    return result.astimezone(timezone.utc)


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def config():
    return json.loads(CONFIG.read_text())


class Tracker:
    def __init__(self, path, clock=utcnow):
        self.clock = clock
        self.db = sqlite3.connect(path)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS revisions (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            revision_id TEXT UNIQUE NOT NULL,
            payload TEXT NOT NULL
          );
          CREATE TRIGGER IF NOT EXISTS immutable_update BEFORE UPDATE ON revisions
          BEGIN SELECT RAISE(ABORT, 'append-only'); END;
          CREATE TRIGGER IF NOT EXISTS immutable_delete BEFORE DELETE ON revisions
          BEGIN SELECT RAISE(ABORT, 'append-only'); END;
        ''')
        self.panels = {p['id']: p for p in config()['panels']}

    def close(self):
        self.db.close()

    def all(self):
        return [json.loads(row[0]) for row in self.db.execute(
            'SELECT payload FROM revisions ORDER BY sequence')]

    def append(self, incoming):
        """One immutable panel revision; ingestion time assigned by this process."""
        item = json.loads(canonical(incoming))
        required = {'schema', 'ticker', 'panel', 'effective_at', 'observed_at',
                    'available_at', 'expires_at', 'classification', 'verification',
                    'sources', 'data', 'method_version', 'supersedes', 'input_revisions'}
        if set(item) != required:
            raise ValueError('unexpected/missing fields: ' + str(set(item) ^ required))
        if item['schema'] != 'basket.ticker_panel@1' or item['ticker'] != 'ORCL':
            raise ValueError('unsupported schema or ticker')
        if item['panel'] not in self.panels:
            raise ValueError('unknown panel')
        if item['classification'] not in ('source_fact', 'issuer_statement', 'derived', 'hypothesis', 'scenario'):
            raise ValueError('unknown classification')
        if item['verification'] not in ('verified', 'unverified', 'disputed'):
            raise ValueError('unknown verification')
        if not isinstance(item['data'], dict) or not item['data']:
            raise ValueError('data must be a nonempty object')
        if not isinstance(item['method_version'], str) or not item['method_version'].strip():
            raise ValueError('method_version required')
        now = stamp(self.clock())
        times = {k: stamp(item[k]) for k in ('effective_at', 'observed_at', 'available_at', 'expires_at')}
        if times['observed_at'] > now or times['available_at'] > now:
            raise ValueError('future observation/availability')
        if times['expires_at'] <= times['observed_at']:
            raise ValueError('expiry must follow observation')
        if not isinstance(item['sources'], list) or not item['sources']:
            raise ValueError('provenance required')
        for source in item['sources']:
            if not isinstance(source, dict) or set(source) != {'url', 'label'}:
                raise ValueError('source requires url and label')
            parsed = urlparse(source['url'])
            if parsed.scheme != 'https' or not parsed.netloc or not source['label']:
                raise ValueError('source must have an HTTPS URL and label')
        if not isinstance(item['input_revisions'], list) or any(not isinstance(i, str) for i in item['input_revisions']):
            raise ValueError('input_revisions must be IDs')
        # Domain owners verify financial payloads. This gate validates composition,
        # provenance and temporal integrity, not the truth of publisher assertions.
        identity = hashlib.sha256(canonical(item).encode()).hexdigest()
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            existing = self.db.execute('SELECT revision_id FROM revisions WHERE revision_id=?', (identity,)).fetchone()
            if existing:
                return identity
            records = {r['revision_id']: r for r in self.all()}
            for dep in item['input_revisions']:
                if dep not in records:
                    raise ValueError('unknown dependency revision')
                if stamp(records[dep]['available_at']) > times['available_at']:
                    raise ValueError('dependency not available at output availability')
            prior = item['supersedes']
            if prior is not None:
                if prior not in records or records[prior]['panel'] != item['panel']:
                    raise ValueError('supersedes must reference same-panel revision')
                if any(r['supersedes'] == prior for r in records.values()):
                    raise ValueError('revision already superseded; correct its successor')
                if times['available_at'] < stamp(records[prior]['available_at']):
                    raise ValueError('correction predates original availability')
            item['revision_id'] = identity
            item['ingested_at'] = now.isoformat()
            self.db.execute('INSERT INTO revisions(revision_id,payload) VALUES (?,?)', (identity, canonical(item)))
        return identity

    def snapshot(self, as_of=None):
        at = stamp(as_of or self.clock())
        if at > stamp(self.clock()):
            raise ValueError('future as-of not supported')
        visible = [r for r in self.all() if max(stamp(r['available_at']), stamp(r['ingested_at'])) <= at]
        by_id = {r['revision_id']: r for r in visible}
        superseded = {r['supersedes'] for r in visible if r['supersedes']}

        def status(r, visiting=None):
            visiting = set() if visiting is None else visiting
            rid = r['revision_id']
            if rid in visiting:
                return 'dependency_invalid'
            if rid in superseded:
                return 'superseded'
            if r['verification'] != 'verified':
                return r['verification']
            ttl = self.panels[r['panel']]['max_age_seconds']
            deadline = min(stamp(r['expires_at']), stamp(r['observed_at']) + timedelta(seconds=ttl))
            if at >= deadline:
                return 'stale'
            if r['panel'] != 'catalysts' and stamp(r['effective_at']) > at:
                return 'future_effective'
            if any(dep not in by_id or status(by_id[dep], visiting | {rid}) != 'current' for dep in r['input_revisions']):
                return 'dependency_invalid'
            if r['classification'] == 'scenario' and r['panel'] == 'valuation':
                if r['data'].get('data_mode') == 'synthetic':
                    return 'synthetic'
                if not r['data'].get('eligible', False):
                    return 'scenario_incomplete'
            if r['classification'] in ('hypothesis', 'scenario'):
                return r['classification']
            return 'current'

        panels, work = [], []
        for name, spec in self.panels.items():
            history = [r for r in visible if r['panel'] == name]
            candidates = [r for r in history if r['revision_id'] not in superseded]
            latest = max(candidates, key=lambda r: (stamp(r['observed_at']), stamp(r['available_at']), stamp(r['ingested_at'])), default=None)
            state = status(latest) if latest else 'missing'
            previous = next((r for r in reversed(history) if latest and r['revision_id'] != latest['revision_id'] and stamp(r['observed_at']) <= stamp(latest['observed_at'])), None)
            changes = []
            if latest:
                old = previous['data'] if previous else {}
                for key in sorted(set(old) | set(latest['data'])):
                    before, after = old.get(key), latest['data'].get(key)
                    if before != after:
                        changes.append({'field': key, 'before': before, 'after': after})
            panels.append({**spec, 'status': state, 'latest': latest,
                           'current_data': latest['data'] if state == 'current' else None,
                           'conditional_data': latest['data'] if state in ('scenario', 'synthetic', 'scenario_incomplete') else None,
                           'changes': changes, 'revision_count': len(history)})
            if state not in ('current', 'scenario'):
                work.append({'panel': name, 'owner': spec['owner'], 'priority': spec['priority'],
                             'reason': state, 'required_metrics': spec['metrics']})
        return {'schema': 'basket.ticker_tracker_snapshot@1', 'ticker': 'ORCL', 'currency': 'USD',
                'as_of': at.isoformat(), 'continuous_feed': False, 'panels': panels,
                'refresh_work': sorted(work, key=lambda w: (w['priority'], w['panel'])),
                'history': visible, 'baseline': config()['baseline']}


def valuation_table(report):
    esc = lambda v: html.escape(str(v), quote=True)
    def money(value):
        return 'Unavailable' if value is None else '$' + format(value, ',.2f')
    target = report.get('target') or {}
    stats = target.get('stats', {})
    prefix = 'SYNTHETIC DEMONSTRATION — no actual market figures' if report.get('data_mode') == 'synthetic' else 'CONDITIONAL SCENARIO — not a verified price target'
    body = '<p>' + prefix + '</p><p>Forward EPS: ' + money(stats.get('eps')) + '</p>'
    body += '<table><tr><th>Scenario</th><th>EPS</th><th>P/E value</th><th>EV/EBITDA value</th></tr>'
    for name, case in report.get('scenarios', {}).items():
        prices = case.get('implied_prices', {})
        body += '<tr><td>'+esc(name)+'</td><td>'+money(case.get('eps'))+'</td><td>'+money(prices.get('pe',{}).get('price_usd'))+'</td><td>'+money(prices.get('ev_ebitda',{}).get('price_usd'))+'</td></tr>'
    body += '</table><p>Peer-reference P/E value: ' + money(report.get('comparisons',{}).get('pe',{}).get('implied_price_usd')) + '</p>'
    if report.get('gaps'):
        body += '<p>Incomplete inputs: '+str(len(report['gaps']))+' gaps; affected methods suppressed.</p>'
    return body


def dashboard(snapshot):
    esc = lambda v: html.escape(str(v), quote=True)
    cards = []
    for panel in snapshot['panels']:
        last = panel['latest']
        sources = '' if not last else ' · '.join('<a href="'+esc(s['url'])+'">'+esc(s['label'])+'</a>' for s in last['sources'])
        payload = json.dumps(panel['current_data'], indent=2) if panel['current_data'] is not None else 'No eligible current signal. See historical evidence below.'
        if panel.get('conditional_data') is not None:
            payload = ('SYNTHETIC DEMONSTRATION — no actual market figures\n' if panel['status'] == 'synthetic' else 'CONDITIONAL SCENARIO — not a verified price target\n') + json.dumps(panel['conditional_data'], indent=2)
        history = '' if not last else '<details><summary>Latest evidence (may be stale) and changes</summary><pre>'+esc(json.dumps({'latest':last,'changes':panel['changes']},indent=2))+'</pre></details>'
        payload_html = valuation_table(panel['conditional_data']) if panel['id']=='valuation' and panel.get('conditional_data') else '<pre>'+esc(payload)+'</pre>'
        cards.append('<article><small>'+esc(panel['owner'])+' · '+str(panel['revision_count'])+' revisions</small><h2>'+esc(panel['title'])+'</h2><b class="'+esc(panel['status'])+'">'+esc(panel['status'].upper())+'</b>'+payload_html+'<p>'+sources+'</p>'+history+'<details><summary>Tracking contract</summary><p>'+esc(panel['contract'])+'</p><p>'+esc(', '.join(panel['metrics']))+'</p></details></article>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ORCL evolving tracker</title>
<style>body{background:#101925;color:#e8eef6;font:16px system-ui;margin:0 auto;padding:32px;max-width:1400px}h1{font-size:38px}h2{font-size:21px}small,p{color:#b6c6da}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px}article{background:#1a2737;padding:22px;border:1px solid #3b4e66;border-radius:14px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}a,.current{color:#66e1ba}b{color:#f7c66a}table{width:100%;font-size:12px;border-collapse:collapse}td,th{text-align:left;padding:6px 2px;border-bottom:1px solid #3b4e66}summary{cursor:pointer;margin:16px 0}footer{margin-top:30px}</style>
<h1>ORCL / evolving ticker tracker</h1><p>USD · As of '''+esc(snapshot['as_of'])+''' · Evidence snapshot, not a live feed</p><p>Current signals are suppressed when missing, stale, disputed, hypothetical or dependent on expired evidence.</p><main>'''+''.join(cards)+'</main><footer><h2>Refresh queue</h2><pre>'+esc(json.dumps(snapshot['refresh_work'],indent=2))+'</pre><details><summary>Weighted baseline policy</summary><pre>'+esc(json.dumps(snapshot['baseline'],indent=2))+'</pre></details></footer></html>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True, help='SQLite path on durable data-plane storage, outside repository')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init')
    ingest = commands.add_parser('ingest')
    ingest.add_argument('file', type=Path, help='one basket.ticker_panel@1 JSON object')
    for name in ('snapshot', 'html', 'history', 'refresh'):
        command = commands.add_parser(name)
        command.add_argument('--as-of')
    args = parser.parse_args()
    tracker = Tracker(args.db)
    try:
        if args.command == 'init':
            print('Initialized ORCL tracker; no feed connected.')
        elif args.command == 'ingest':
            print(tracker.append(json.loads(args.file.read_text())))
        else:
            snapshot = tracker.snapshot(args.as_of)
            if args.command == 'html':
                print(dashboard(snapshot))
            else:
                result = snapshot if args.command == 'snapshot' else snapshot['history' if args.command == 'history' else 'refresh_work']
                print(json.dumps(result, indent=2, allow_nan=False))
    finally:
        tracker.close()


if __name__ == '__main__':
    main()
