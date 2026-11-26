"""Local adapter boundaries. No provider requests or persistent scheduling."""
import importlib.util
from pathlib import Path
from model import digest, instant


def factor_adapter(script, csv_path, expected_script_sha256):
    """Run audited #69 implementation from a caller-supplied pinned local checkout."""
    import hashlib
    path=Path(script)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected_script_sha256:
        raise ValueError('Factor implementation hash mismatch')
    spec=importlib.util.spec_from_file_location('crwv_pinned_factor',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run(csv_path)


def accept_attribution(result, as_of):
    if result.get('schema')!='crwv.factor-research@1':
        raise ValueError('Unsupported attribution contract')
    for model in result['models'].values():
        for r in model['history']:
            if r['trained_through']>=r['date'] or r['date']>as_of[:10]:
                raise ValueError('Factor lookahead')
            if abs(r['intercept']+sum(r['contributions'].values())+r['residual']-r['actual_return'])>1e-8:
                raise ValueError('Attribution does not reconcile')
    return dict(status='historical_ex_post_diagnostic',source_hash=digest(result),result=result,limitations=['Residual is unexplained return, not mispricing','HYG/IEF/USO are proxies, not issuer spreads/SOFR/spot oil'])


def turnover(bars, as_of, anchor='2026-10-07', session='regular', exchange='XNAS', windows=(5,20,60)):
    """Approximate notional from bar VWAP. No inferred volume-at-price/touches."""
    valid=[]
    for b in bars:
        if b['session']!=session:
            continue
        if not b.get('available_at') or instant(b['available_at'])>instant(as_of):
            continue
        if not b.get('completed') or b['date']>as_of[:10]:
            continue
        if b['volume']<0 or min(b['vwap'],b['close'])<=0 or b['high']<b['low']:
            raise ValueError('Invalid bar')
        valid.append(b)
    if [b['date'] for b in valid]!=sorted(set(b['date'] for b in valid)):
        raise ValueError('Duplicate/unsorted sessions')
    def calc(rows, required=None):
        if not rows or required and len(rows)<required:
            return dict(status='missing',n=len(rows),required=required)
        vol=sum(b['volume'] for b in rows)
        notional=sum(b['volume']*b['vwap'] for b in rows)
        ret=rows[-1]['close']/rows[0]['open']-1
        gross=sum((b['high']-b['low'])/b['open'] for b in rows)
        return dict(status='descriptive',n=len(rows),dollar_turnover=notional,volume=vol,anchored_vwap=notional/vol if vol else None,net_return=ret,signed_return_per_billion_usd=ret/(notional/1e9) if notional else None,gross_intrabar_range_sum=gross,unique_holder_replacement=None,net_capital_flow=None)
    anchored=[b for b in valid if b['date']>=anchor]
    return dict(schema='crwv.turnover-adapter@1',session=session,exchange=exchange,anchor=anchor,adjustment_basis='caller supplied; all bars must match',windows={str(n):calc(valid[-n:],n) for n in windows},anchored=calc(anchored) if anchored and anchored[0]['date']==anchor else dict(status='missing_anchor'),input_hash=digest(bars),touches=None,transition_probabilities=None,limitations=['Bar VWAP times volume approximation, not unique owners or net flows','No intrabar ordering or precise volume-at-price','Band/held-out/cost calibration remains B06/B07 via #70'])


def adapt_research_turnover(research, available_at, as_of):
    """Minimum transformation of #69 raw_daily; unknown publication blocks import."""
    from datetime import datetime, timezone
    bars=[]
    for b in research['raw_daily']:
        bars.append(dict(date=datetime.fromtimestamp(b['t']/1000,timezone.utc).date().isoformat(),open=b['o'],close=b['c'],high=b['h'],low=b['l'],volume=b['v'],vwap=b['vw'],session='regular',completed=True,available_at=available_at))
    return turnover(bars,as_of)
