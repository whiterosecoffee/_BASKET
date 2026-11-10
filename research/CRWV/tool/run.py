"""Usage: python research/CRWV/tool/run.py --input ... --config ... --as-of ..."""
import argparse
import json
from pathlib import Path
from model import analyze
from history import append_record


def readable(result):
    rows=result['operating_forecast']
    if rows is None:
        return 'CRWV finance blocked: '+result['coverage']['reason']+'\n'
    lines=[f"CRWV offline scenario | {result['valuation_as_of']} | {result['metric_metadata']['status']}",f"Funding: {result['funding_waterfall']['status']}; first gap month: {result['funding_waterfall']['earliest_gap_month']}",f"Month 1 revenue ${rows[0]['revenue']:,.2f}; billable IT MW {rows[0]['billable_it_mw']:,.2f}",f"Final cash ${rows[-1]['closing_cash']:,.2f}; debt ${rows[-1]['closing_debt']:,.2f}; shares {rows[-1]['diluted_shares']:,.2f}"]
    for v in result['valuation_curve']:
        price=v['conditional_value_per_share']
        lines.append(f"{v['target_date'][:10]}: "+(f"${price:.2f}/share conditional" if price is not None else 'valuation blocked: unfunded plan'))
    lines+=['No current CRWV valuation or calibrated probabilities asserted.','Unknowns: '+'; '.join(result['unknowns'])]
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--config',required=True)
    p.add_argument('--as-of',required=True)
    p.add_argument('--json-output')
    p.add_argument('--text-output')
    p.add_argument('--history')
    p.add_argument('--reason',default='Explicit local scenario evaluation')
    args=p.parse_args()
    try:
        snapshot=json.loads(Path(args.input).read_text())
        config=json.loads(Path(args.config).read_text())
        result=analyze(snapshot,config,args.as_of)
        import subprocess
        result['implementation_commit']=subprocess.run(['git','rev-parse','HEAD'],cwd=Path(__file__).parent,capture_output=True,text=True).stdout.strip() or None
    except (ValueError,KeyError,TypeError) as e:
        p.exit(2,f'Input rejected: {e}\n')
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if args.text_output:
        Path(args.text_output).write_text(readable(result))
    if args.history:
        append_record(args.history,result,snapshot,config,args.reason)
    print(readable(result),end='')

if __name__=='__main__':
    main()
