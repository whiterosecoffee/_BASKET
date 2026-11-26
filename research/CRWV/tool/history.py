"""Immutable valuation records and ordered fixed-horizon attribution."""
import copy
import json
from pathlib import Path
from model import digest, evaluate

GROUPS = [
    ('capacity_delivery', ['cohorts']),
    ('price_mix', ['contracts']),
    ('operating_margin', ['costs']),
    ('life_residual', []),
    ('funding_interest', ['facilities','opening']),
    ('dilution', ['capitalization']),
    ('discount_multiple', []),
]


def bridge(old_snapshot, old_config, new_snapshot, new_config, as_of, horizon=12):
    """Ordered replacement decomposition; interaction is order dependent, not causal."""
    if old_snapshot['start'] != new_snapshot['start']:
        raise ValueError('Align fixed target date/forecast start before comparison')
    def value(s,c):
        r = evaluate(s,c,as_of,[horizon])
        return r['valuation_curve'][-1]['conditional_value_per_share']
    s,c = copy.deepcopy(old_snapshot),copy.deepcopy(old_config)
    initial = last = value(s,c)
    if initial is None:
        return dict(status='blocked_unfunded_baseline',components=None)
    parts=[]
    config_keys = dict(capacity_delivery=['acceptance_delay_months'],price_mix=['price_multiplier'], operating_margin=[], life_residual=['depreciation_life_multiplier','earning_life_multiplier'],funding_interest=['benchmark','benchmark_shock'],dilution=['equity_issues'],discount_multiple=['discount_rate','terminal_growth','pe_multiple','terminal_continuation_approved'])
    for name, keys in GROUPS:
        for key in keys:
            s[key]=copy.deepcopy(new_snapshot[key])
        for key in config_keys[name]:
            if key in new_config:
                c[key]=copy.deepcopy(new_config[key])
            else:
                c.pop(key,None)
        now=value(s,c)
        if now is None:
            return dict(status='blocked_unfunded_revision',components=None)
        parts.append(dict(factor=name,change=now-last))
        last=now
    final=value(new_snapshot,new_config)
    if final is None:
        return dict(status='blocked_unfunded_revision',components=None)
    parts.append(dict(factor='reconciliation_interactions',change=final-last))
    return dict(status='comparable',horizon_months=horizon,as_of=as_of,method='ordered replacement in listed order; residual captures unallocated changes; no time roll for fixed target',original_value=initial,revised_value=final,components=parts,reconciliation_error=final-initial-sum(p['change'] for p in parts))


def append_record(path, result, snapshot, config, reason, actuals=None):
    record=dict(schema='crwv.valuation-revision@1',reason=reason,original_inputs=snapshot,config=config,result=result,actuals=actuals or [],supersedes=None)
    path=Path(path)
    prior=[json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    record['supersedes']=prior[-1]['record_id'] if prior else None
    record['record_id']=digest(record)
    # Exclusive append protects other processes and never rewrites existing records.
    import os
    lock=path.with_suffix(path.suffix+'.lock')
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        # Check prior did not change before lock acquisition.
        current=[json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
        if current != prior:
            raise RuntimeError('History changed; retry from fresh history')
        with path.open('a',encoding='utf-8') as f:
            f.write(json.dumps(record,sort_keys=True,allow_nan=False)+'\n')
            f.flush()
            os.fsync(f.fileno())
    finally:
        os.close(fd)
        lock.unlink()
    return record
