"""Research-only frozen-input expiry decomposition; no IO or trading inference."""
from datetime import datetime
from decimal import Decimal

def decompose(before, after, expired_before):
    for key in ('metric', 'unit', 'settings_id'):
        if not before.get(key) or before[key] == 'unknown' or before[key] != after.get(key):
            raise ValueError('incompatible or unknown ' + key)
    times = []
    for snapshot in (before, after):
        if not snapshot.get('source_ref') or not snapshot.get('universe_id'):
            raise ValueError('missing provenance/universe')
        stamp = datetime.fromisoformat(snapshot['observed_at'])
        if stamp.utcoffset() is None:
            raise ValueError('timezone required')
        times.append(stamp)
    if times[1] <= times[0]:
        raise ValueError('after must follow before')
    values = [Decimal(str(x)) for x in (before['value'], after['value'], expired_before)]
    if not all(x.is_finite() for x in values):
        raise ValueError('finite values required')
    b, a, e = values
    return dict(unit=before['unit'], observed_change=str(a-b),
                removal_only_change=str(-e), counterfactual_remaining=str(b-e),
                unattributed_residual=str(a-(b-e)), new_positioning='not_determined')
