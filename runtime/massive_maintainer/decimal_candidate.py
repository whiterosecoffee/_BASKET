"""Pure, unqualified representation experiment. No IO, fetch, or promotion API."""
import base64
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

SCHEMA = 'basket.decimal-candidate@1'
ET = ZoneInfo('America/New_York')
NUMERIC = ('o', 'h', 'l', 'c', 'vol', 'vw', 'n', 'px')


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def reject_constant(value):
    raise ValueError('non-finite JSON number')


def build_candidate(inputs):
    """Inputs: bytes, vintage, expected sha256, and explicit basis dictionary.

    The caller supplies small retained artifacts. Exact input bytes remain embedded
    per line. A source hash binds bytes, not vendor authenticity. Even complete
    caller-declared basis evidence never upgrades this result to qualified data.
    """
    records = []
    sources = {}
    for item in inputs:
        data = item['data']
        if not isinstance(data, bytes) or sha(data) != item['sha256']:
            raise ValueError('input checksum mismatch')
        vintage = item['vintage']
        if not isinstance(vintage, str) or not vintage:
            raise ValueError('explicit vintage required')
        # Copy metadata through serialization: never mutate a caller's dictionary.
        basis = json.loads(encode(item['basis']))
        if not isinstance(basis, dict):
            raise ValueError('basis must be an explicit dictionary')
        descriptor = {'sha256': sha(data), 'vintage': vintage, 'basis': basis,
                      'source_kind': 'retained_normalized_rows',
                      'provenance': json.loads(encode(item.get('provenance', {})))}
        source_id = sha(encode(descriptor))
        if source_id in sources:
            continue  # Replaying the same artifact is idempotent.
        sources[source_id] = descriptor
        known = (basis.get('volume_unit') == 'shares'
                 and basis.get('adjustment') in ('split_adjusted', 'unadjusted')
                 and isinstance(basis.get('adjustment_as_of'), str)
                 and bool(basis['adjustment_as_of'])
                 and basis.get('timezone') == 'America/New_York'
                 and basis.get('grain') == '1m'
                 and basis.get('evidence_status') == 'source_bound'
                 and isinstance(basis.get('evidence_sha256'), str)
                 and len(basis['evidence_sha256']) == 64
                 and all(c in '0123456789abcdef' for c in basis['evidence_sha256']))
        for line_no, raw in enumerate(data.splitlines(keepends=True), 1):
            record = {'source_id': source_id, 'line': line_no,
                      'raw_sha256': sha(raw),
                      'raw_base64': base64.b64encode(raw).decode(),
                      'values': None, 'key': None, 'session': None,
                      'reasons': [] if known else ['unknown_or_unsupported_basis']}
            try:
                row = json.loads(raw, parse_float=Decimal,
                                 parse_constant=reject_constant)
                if not isinstance(row, dict) or not isinstance(row.get('ticker'), str) or not row['ticker']:
                    raise ValueError('identity')
                if row.get('grain') not in ('1min', '1m') or row.get('class', 'bar') != 'bar':
                    raise ValueError('incompatible record grain or class')
                t = row.get('t')
                if type(t) is not int or t % 60000:
                    raise ValueError('timestamp')
                utc = datetime.fromtimestamp(t // 1000, timezone.utc)
                if 'ts' in row and (not isinstance(row['ts'], str) or datetime.fromisoformat(row['ts'].replace('Z', '+00:00')) != utc):
                    raise ValueError('inconsistent timestamp')
                local = utc.astimezone(ET)
                record['key'] = [row['ticker'], t]
                minute = local.hour * 60 + local.minute
                record['session'] = {'exchange_date': local.date().isoformat(),
                    'timezone': 'America/New_York', 'grain': '1m',
                    'window': 'pre_0930' if minute < 570 else
                              '0930_to_before_1600' if minute < 960 else '1600_onward',
                    'calendar_verified': False}
                values = {}
                for field in NUMERIC:
                    value = row.get(field)
                    if value is None and field in ('vw', 'n', 'px'):
                        values[field] = None
                        continue
                    if type(value) not in (int, Decimal) or not Decimal(value).is_finite() or value < 0:
                        raise ValueError('numeric')
                    values[field] = str(value)  # No float conversion or rounding.
                record['values'] = values
            except (ValueError, TypeError, KeyError, ArithmeticError, OverflowError, OSError):
                record['reasons'].append('invalid_record')
            records.append(record)
    groups = {}
    for record in records:
        if record['key'] is not None and record['values'] is not None:
            groups.setdefault(tuple(record['key']), []).append(record)
    summaries = []
    for key, members in sorted(groups.items()):
        bases = {encode(sources[r['source_id']]['basis']) for r in members}
        values = {encode(r['values']) for r in members}
        if len(bases) > 1:
            state = 'incompatible_or_unreconciled_basis'
        elif len(values) > 1:
            state = 'conflicting_vintages'
        elif len(members) > 1:
            state = 'identical_duplicate'
        else:
            state = 'single'
        if state in ('incompatible_or_unreconciled_basis', 'conflicting_vintages'):
            for record in members:
                record['reasons'].append(state)
        summaries.append({'key': list(key), 'state': state, 'occurrences': len(members),
                          'selected_vintage': None})
    for record in records:
        record['reasons'] = sorted(set(record['reasons']))
        record['disposition'] = 'quarantine' if record['reasons'] else 'representation_only'
    return {'schema': SCHEMA, 'qualification': 'unqualified_candidate',
            'sources': dict(sorted(sources.items())),
            'records': sorted(records, key=lambda r: (r['source_id'], r['line'])),
            'groups': summaries, 'promotable': False}
