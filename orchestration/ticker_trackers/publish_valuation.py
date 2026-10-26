"""Read current owned panels, calculate a conditional valuation, append its revision."""
import argparse
import copy
import json
from datetime import timedelta

from engines.valuation.orcl_bridge.engine import evaluate, VERSION
from orchestration.ticker_trackers.tracker import Tracker, stamp


def publish(tracker):
    snapshot = tracker.snapshot()
    panels = {p['id']:p for p in snapshot['panels']}
    required = ('market','fundamentals','financing')
    missing = [name for name in required if panels[name]['status']!='current']
    if missing:
        return {'status':'blocked','reason':'Missing or ineligible dependencies','panels':missing}
    records = {key:panels[key]['latest'] for key in required}

    def wrap(panel, data):
        r = records[panel]
        return {key:r[key] for key in ('effective_at','observed_at','available_at','ingested_at','expires_at','verification','classification')} | {
            'source_id':r['revision_id'], 'sources':[s['url'] for s in r['sources']], 'data':copy.deepcopy(data)}

    data = records['fundamentals']['data']
    try:
        bundle = {'schema':'basket.valuation_input@1','data_mode':data['data_mode'], 'target':'ORCL',
                  'peer_weights':data['peer_weights'], 'scenarios':data['scenarios'],
                  'companies':copy.deepcopy(data['peers'])}
        bundle['companies']['ORCL'] = {'ticker':'ORCL','currency':'USD',
            'quote':wrap('market',{'price':records['market']['data']['last_usd']}),
            'forecast':wrap('fundamentals',data['forecast']),
            'balance':wrap('financing',records['financing']['data']['balance'])}
        result = evaluate(bundle,snapshot['as_of'])
    except (KeyError,TypeError,ValueError) as exc:
        return {'status':'blocked','reason':str(exc)}
    if result['target'] is None:
        return {'status':'blocked','reason':'Target inputs failed validation','gaps':result['gaps']}
    # Peer-specific expiry constrains the entire published valuation too.
    expiries = [stamp(snapshot['as_of'])+timedelta(seconds=120)]
    for name,r in records.items():
        expiries.extend([stamp(r['expires_at']),stamp(r['observed_at'])+timedelta(seconds=panels[name]['max_age_seconds'])])
    for peer in bundle['companies'].values():
        for kind in ('quote','forecast','balance'):
            expiries.extend([stamp(peer[kind]['expires_at']),stamp(peer[kind]['observed_at'])+timedelta(seconds=300 if kind=='quote' else 86400)])
    if min(expiries) <= stamp(snapshot['as_of']):
        return {'status':'blocked','reason':'Expired valuation input'}
    sources = {s['url']:s for r in records.values() for s in r['sources']}
    for peer in bundle['companies'].values():
        for kind in ('quote','forecast','balance'):
            for url in peer[kind]['sources']:
                sources.setdefault(url,{'url':url,'label':'Valuation evidence'})
    # Same source revisions + same result must not create a new duplicate merely
    # because the user requested another refresh a few seconds later.
    prior = panels['valuation']['latest']
    dependencies = [records[k]['revision_id'] for k in required]
    if prior and prior['input_revisions']==dependencies and prior['data'].get('input_sha256')==result['input_sha256'] and panels['valuation']['status'] in ('scenario','synthetic','scenario_incomplete'):
        return {'status':'unchanged','revision_id':prior['revision_id']}
    envelope = {'schema':'basket.ticker_panel@1','ticker':'ORCL','panel':'valuation',
        'effective_at':snapshot['as_of'],'observed_at':snapshot['as_of'],
        'available_at':snapshot['as_of'],'expires_at':min(expiries).isoformat(),
        'classification':'scenario','verification':'verified','sources':list(sources.values()),
        'data':result,'method_version':VERSION,'supersedes':prior['revision_id'] if prior else None,
        'input_revisions':dependencies}
    rid = tracker.append(envelope)
    return {'status':'published_conditional','revision_id':rid,'eligible':result['eligible'],'gaps':result['gaps']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True)
    args = parser.parse_args()
    tracker = Tracker(args.db)
    try:
        print(json.dumps(publish(tracker),indent=2))
    finally:
        tracker.close()


if __name__=='__main__':
    main()
