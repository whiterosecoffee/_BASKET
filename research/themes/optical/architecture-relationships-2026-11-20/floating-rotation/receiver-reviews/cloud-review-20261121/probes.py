"""Offline review probes; imports the existing engine without modifying it."""
import argparse
import copy
import importlib.util
import json
from decimal import Decimal as D
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('engine_root', type=Path)
p.add_argument('output', type=Path)
args = p.parse_args()
spec = importlib.util.spec_from_file_location('rotation', args.engine_root / 'rotation.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
data = json.loads((args.engine_root / 'example.json').read_text())
rows = []

def record(name, kind, observation):
    rows.append(dict(name=name, kind=kind, observation=observation))

baseline = module.analyze(data)
assert baseline['NVDA']['whole_shares'] == 626
assert baseline['CRWV']['scenarios'][0]['status'] == 'P/E scenario unavailable'
record('parent fixture', 'supported', '626 NVDA shares; nonpositive CRWV EPS suppresses P/E scenarios')

for target in baseline['NVDA']['scenarios']:
    price = target['required_bid']
    for adjustment, expected in [(D(0), True), (D('-.01'), False)]:
        case = copy.deepcopy(data)
        case['paired_quotes'][1]['bid']['SNDK'] = str(price + adjustment)
        actual = module.analyze(case)['NVDA']['scenarios'][target['years'] - 1]['clears']
        assert actual == expected
record('three horizons tick boundaries', 'supported', 'All three required bids pass; one cent below fails (6 checks)')

for label, modify in [
    ('non-finite quote', lambda d: d['paired_quotes'][1]['bid'].update(SNDK='NaN')),
    ('lookahead forecast', lambda d: d['alternatives']['NVDA'][0].update(available_at='2030-01-01T00:00:00Z')),
]:
    changed = copy.deepcopy(data)
    modify(changed)
    try:
        module.analyze(changed)
    except ValueError:
        record(label, 'supported', 'Rejected with ValueError')
    else:
        raise AssertionError(label)

stale = copy.deepcopy(data)
stale.update(as_of='2026-11-21T07:00:00Z', quote_ttd_seconds=1)
assert module.analyze(stale)['NVDA']['scenarios'][2]['clears']
record('explicit expired quote metadata', 'gap', 'as_of/TTD fields ignored; historical quotes still emit clears=true')

basis = copy.deepcopy(data)
basis['alternatives']['NVDA'][0].update(held_basis='GAAP', candidate_basis='adjusted')
assert 'held_value' in module.analyze(basis)['NVDA']['scenarios'][0]
record('mixed earnings basis metadata', 'gap', 'GAAP/adjusted metadata ignored; upstream validation required')

horizon = copy.deepcopy(data)
horizon['alternatives']['CRWV'][2]['end'] = '2035-11-20'
assert module.analyze(horizon)['CRWV']['scenarios'][2]['end'] == '2035-11-20'
record('mismatched common horizon', 'gap', 'years=3 with 2035 endpoint accepted alongside 2029 candidate')

cash = dict(held='A', shares=1, terminal_edge=.1, cost_per_share=[0, 0],
    paired_quotes=[dict(at='2026-11-20T12:00:00Z', bid=dict(A=100), ask=dict(B=60)),
                   dict(at='2026-11-20T12:15:00Z', bid=dict(A=100), ask=dict(B=60))],
    alternatives=dict(B=[dict(name='cash review fixture', years=1, end='2027-11-20',
        source='synthetic', available_at='2026-11-19T00:00:00Z',
        eps_multiple_held_then_candidate=[10,10,10,10])]))
result = module.analyze(cash)['B']
assert result['whole_shares'] == 1 and result['scenarios'][0]['required_bid'] == D(120)
assert not result['scenarios'][0]['clears']
assert D(100) + D(40) > D(100) * D('1.1')
record('residual cash conservative exclusion', 'documented limitation',
       '1 B share plus $40 residual yields $140 vs $100 hold; engine excludes cash and requires $120 bid')

revision = copy.deepcopy(data)
revision['alternatives']['NVDA'][0]['eps_multiple_held_then_candidate'][2] = 7
assert module.analyze(revision)['NVDA']['scenarios'][0]['required_bid'] < baseline['NVDA']['scenarios'][0]['required_bid']
record('estimate revision', 'supported', 'Higher candidate EPS lowers threshold at unchanged quotes; forecast attribution/history absent')

fair = D(1)
forward = D(100) * (D(99)/D(101)) / fair
reverse = D(100) * (D(99)/D(101)) * fair
assert forward * reverse < D(10000)
assert D(10000)/D(110) < D(100)
assert D(100)*D(1)/D('.8') == D(125)
assert (D(100)/D(100))/(D(100)/D(100)) == (D(200)/D(200))/(D(100)/D(100))
record('design algebra', 'review arithmetic only',
       'Parity, directed spread, reciprocal 10% band, 100-to-125 share round trip and common price scaling checked; no implemented stateful index claimed')

args.output.write_text(json.dumps(dict(engine_revision='56e9e03693cfcd71cf0ca04d50470332110defda',
    probe_groups=len(rows), observations=rows), indent=2) + '\n')
print(json.dumps(dict(probe_groups=len(rows), observations=rows), indent=2))
