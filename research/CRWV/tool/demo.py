"""Deterministic end-to-end acceptance run, scenarios, revisions, lifecycle."""
import copy
import json
import argparse
from pathlib import Path
from model import evaluate,lifecycle,digest
from history import append_record,bridge
from run import readable

ROOT=Path(__file__).parent
ASOF='2026-10-27T14:30:00Z'


def run(out):
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    snapshot=json.loads((ROOT/'fixtures/snapshot.json').read_text())
    results={}
    for name in ['slow','base','bull','unfunded']:
        s=json.loads((ROOT/'fixtures/unfunded-snapshot.json').read_text()) if name=='unfunded' else copy.deepcopy(snapshot)
        config=json.loads((ROOT/'fixtures'/f'{name}.json').read_text())
        result=evaluate(s,config,ASOF)
        results[name]=result
        (out/f'{name}.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        (out/f'{name}.txt').write_text(readable(result))
        append_record(out/'valuation-history.jsonl',result,s,config,'Synthetic acceptance '+name)
    base=json.loads((ROOT/'fixtures/base.json').read_text())
    revised=dict(base,price_multiplier=1.1)
    revision=bridge(snapshot,base,snapshot,revised,ASOF,12)
    (out/'revision-bridge.json').write_text(json.dumps(revision,indent=2)+'\n')
    sensitivities={}
    for label,changes in [('accounting_1.5x',{'depreciation_life_multiplier':1.5}),('earning_7y',{'earning_life_multiplier':7/9}),('earning_9y',{}),('acceptance_delay_6m',{'acceptance_delay_months':6}),('benchmark_plus_200bp',{'benchmark_shock':.02})]:
        r=evaluate(snapshot,dict(base,**changes),ASOF)
        sensitivities[label]=dict(first_month_eps=r['operating_forecast'][0]['eps'],first_month_ocf=r['operating_forecast'][0]['operating_cash'],lifetime_cash_collections=sum(x['cash_collections'] for x in r['operating_forecast']),valuation=r['valuation_curve'][0],funding=r['funding_waterfall'])
    sensitivities['tradein_hypothetical']=lifecycle([100_000]*24,.12,100_000,2_000_000,200_000,[150_000]*36,2)
    (out/'sensitivities.json').write_text(json.dumps(sensitivities,indent=2)+'\n')
    summary={name:dict(funding=r['funding_waterfall'],present_per_share=r['valuation_curve'][0]['conditional_value_per_share'],input_hash=r['input_hash'],config_hash=r['config_hash']) for name,r in results.items()}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    run(p.parse_args().output)
