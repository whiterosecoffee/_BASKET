"""Stable local interface: capture/replay/show/export; no provider network calls."""
import argparse
import json
import time
from pathlib import Path
from patterns import clock, stamp
from store import capture, export, latest, export_input


def matrix(s, now=None):
    if not s:
        return 'No completed regular-session bars stored.'
    z = s['active_range']
    f = s['flow_15m']
    def n(v):
        return 'null' if v is None else f'{v:.3f}'
    b = z['definition'] if z else None
    age = (now-s['as_of'])/1000 if now is not None else None
    lines = [f"{s['ticker']} last={s['last_price']:.4f} {stamp(s['as_of'])} | {s['freshness']} | current age s={n(age)} | {s['classification']}",
             'lower | upper | pos | S up/down | Q net/path | $15m | shares15m | ADV% | clock RVOL',
             f"{b['lower'] if b else 'null'} | {b['upper'] if b else 'null'} | {n(s['range_position'])} | {n(f['ratio'] if f else None)} | {n(s['path_15m']['signed_efficiency'])} | {s['activity_15m']['dollars']:.0f} | {s['activity_15m']['shares']:.0f} | {n(s['volume_pct_adv20'])} | {n(s['same_time_rvol']['ratio'])}"]
    if z:
        lines.append('contacts upper/lower='+str(z['boundaries']['upper']['contacts'])+'/'+str(z['boundaries']['lower']['contacts'])+' | close traversals='+str(z['traversals'])+' | range '+z['id'][:12])
        if f:
            lines.append('directional evidence up/down bars='+str(f['sides']['up']['bars'])+'/'+str(f['sides']['down']['bars'])+' | score state='+f['state'])
    lines.append('Events: '+', '.join(e['kind'] for e in s['events']))
    lines.append('OHLCV approximation; S is descriptive; no signed flow or probabilities.')
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('capture', 'replay', 'show', 'export', 'export-input'))
    p.add_argument('--input'); p.add_argument('--db', required=True); p.add_argument('--ticker')
    p.add_argument('--as-of'); p.add_argument('--out'); p.add_argument('--rebuild', action='store_true')
    p.add_argument('--retrospective-matches', action='store_true')
    a = p.parse_args()
    if a.command in ('capture', 'replay'):
        batch = json.loads(Path(a.input).read_text())
        asof = clock(a.as_of) if a.as_of else max(b['t']+60000 for b in batch['bars'])
        result = capture(a.db, batch, asof, a.rebuild, a.retrospective_matches)
        print(json.dumps({'new_signals': result['new_signals'], 'generation': result['generation']}))
        print(matrix(result['latest'], int(time.time()*1000)))
    elif a.command == 'export-input':
        export_input(a.db, a.ticker, a.out)
    elif a.command == 'export':
        export(a.db, a.ticker, a.out)
    else:
        print(matrix(latest(a.db, a.ticker), int(time.time()*1000)))


if __name__ == '__main__':
    main()
