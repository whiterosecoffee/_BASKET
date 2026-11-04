"""Read-only NVDA recovery preflight; research prototype, not an ingestion writer.

Run against the retained v2 directory. Main ticker_data remains the schema and
write authority. No probabilities, dealer-inventory inference or quote service.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

VERSION = 'nvda-recovery-preflight@0.1.0'
ET = ZoneInfo('America/New_York')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate JSON property: ' + key)
        result[key] = value
    return result


def strict_json(text):
    def reject(value):
        raise ValueError('non-finite JSON constant: ' + value)
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=reject)


def timestamp(value):
    t = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if t.tzinfo is None:
        raise ValueError('timezone required')
    return t


def audit(directory):
    """Audit declared partitions only; never infer missing sessions or bar paths.

    390 regular minutes is limited to this eight-full-session NVDA fixture.
    Exchange holidays/half-days must come from B02's future calendar contract.
    """
    root = Path(directory).resolve()
    errors, warnings, reports = [], [], []
    seen_dates, seen_files, seen_keys, seen_ids = set(), set(), set(), set()
    try:
        manifest = strict_json((root / 'manifest.json').read_text())
        declarations = manifest['days']
        if not isinstance(declarations, list) or not declarations:
            raise ValueError('nonempty days required')
        if manifest.get('partition_timezone') != 'America/New_York':
            raise ValueError('wrong partition timezone')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return {'algorithm_version': VERSION, 'status': 'rejected',
                'errors': [str(exc)], 'warnings': [], 'days': []}

    for entry in declarations:
        label = str(entry.get('date_et')) if isinstance(entry, dict) else 'invalid'
        local_errors, local_warnings = [], []
        count, regular, vwap_flags = 0, set(), 0
        try:
            date, name = entry['date_et'], entry['file']
            datetime.strptime(date, '%Y-%m-%d')
            if date in seen_dates or name in seen_files:
                raise ValueError('duplicate manifest date or file')
            seen_dates.add(date)
            seen_files.add(name)
            if name != date + '.1m.jsonl':
                raise ValueError('filename must match session date')
            path = root / name
            if path.is_symlink() or path.resolve().parent != root:
                raise ValueError('unsafe partition path')
            raw = path.read_bytes()
            if not raw or not raw.endswith(b'\n'):
                raise ValueError('empty or truncated partition')
            if hashlib.sha256(raw).hexdigest() != entry['sha256']:
                local_errors.append('file_hash_mismatch')
            previous = None
            for line in raw.splitlines():
                count += 1
                r = strict_json(line)
                if not isinstance(r, dict):
                    raise ValueError('object record required')
                rid = r['record_id']
                if rid != hashlib.sha256(canonical({k: v for k, v in r.items() if k != 'record_id'})).hexdigest():
                    local_errors.append('record_hash_mismatch')
                key = (r['entity_id'], r['kind'], r['source_record_id'])
                if rid in seen_ids or key in seen_keys:
                    local_errors.append('duplicate_record_or_source_key')
                seen_ids.add(rid)
                seen_keys.add(key)
                t = timestamp(r['observed_at'])
                available, ingested = timestamp(r['available_at']), timestamp(r['ingested_at'])
                if not t <= available <= ingested:
                    local_errors.append('invalid_temporal_order')
                if t.second or t.microsecond or previous is not None and t <= previous:
                    local_errors.append('unordered_or_unaligned_minute')
                previous = t
                local = t.astimezone(ET)
                if local.date().isoformat() != date:
                    local_errors.append('mixed_session_date')
                v = r['value']
                if (r['entity_id'], r['kind'], r['currency'], r['source'],
                    v['interval'], v['adjustment_basis']) != (
                    'NVDA', 'market_bar', 'USD', 'Massive', '1m', 'unadjusted'):
                    local_errors.append('identity_or_basis_mismatch')
                if r['ttd_seconds'] != 0:
                    local_errors.append('historical_capture_has_live_ttd')
                expected_key = f'NVDA:1m:{int(t.timestamp()*1000)}:unadjusted'
                if r['source_record_id'] != expected_key:
                    local_errors.append('source_key_time_mismatch')
                values = [v[k] for k in ('open', 'high', 'low', 'close', 'volume', 'vwap', 'transactions')]
                if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
                    raise ValueError('nonfinite_or_nonnumeric_bar')
                if not 0 < v['low'] <= min(v['open'], v['close']) <= max(v['open'], v['close']) <= v['high']:
                    local_errors.append('invalid_ohlc')
                if v['volume'] < 0 or v['transactions'] < 0 or int(v['transactions']) != v['transactions'] or v['vwap'] <= 0:
                    local_errors.append('invalid_volume_count_or_vwap')
                if not v['low'] <= v['vwap'] <= v['high']:
                    vwap_flags += 1
                if time(9, 30) <= local.time() < time(16):
                    regular.add((local.hour, local.minute))
            expected = {(m // 60, m % 60) for m in range(570, 960)}
            if regular != expected:
                local_errors.append('regular_minute_coverage_mismatch')
            if count != entry['records'] or len(regular) != entry['regular_minutes']:
                local_errors.append('manifest_count_mismatch')
            if vwap_flags != entry['vwap_flags']:
                local_errors.append('manifest_quality_count_mismatch')
            if vwap_flags:
                local_warnings.append('vwap_outside_ohlc_review_required')
        except (ValueError, KeyError, TypeError, OSError, AttributeError, OverflowError) as exc:
            local_errors.append(str(exc))
        errors.extend(label + ': ' + e for e in sorted(set(local_errors)))
        warnings.extend(label + ': ' + e for e in local_warnings)
        reports.append({'date_et': label, 'records': count, 'regular_minutes': len(regular),
                        'vwap_flags': vwap_flags, 'errors': sorted(set(local_errors))})
    unexpected = sorted(p.name for p in root.glob('*.jsonl') if p.name not in seen_files)
    if unexpected:
        errors.append('unlisted_partitions: ' + ', '.join(unexpected))
    return {'algorithm_version': VERSION,
            'input_manifest_sha256': hashlib.sha256((root / 'manifest.json').read_bytes()).hexdigest(),
            'checker_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'coverage_policy': 'eight_declared_full_US_equity_sessions_390_minutes',
            'status': 'rejected' if errors else 'qualified_with_warnings' if warnings else 'qualified',
            'errors': errors, 'warnings': warnings, 'days': reports,
            'predictive_probability': None, 'canonical_integration': False}


def compare(a, b):
    """Permit arithmetic only on explicitly homogeneous research quantities.

    Does not infer inventory, ownership or causal effects. No unit conversion.
    Even a qualified subtraction is only a difference of supplied quantities.
    """
    fields = ('metric', 'unit', 'scale', 'instrument', 'provider', 'method',
              'scope', 'period_end', 'basis', 'window_start', 'window_end')
    reasons = []
    for key in fields:
        if key not in a or key not in b or a[key] is None or b[key] is None:
            reasons.append('missing_' + key)
        elif a[key] in ('', 'unknown', 'unverified') or b[key] in ('', 'unknown', 'unverified'):
            reasons.append('unknown_' + key)
        elif a[key] != b[key]:
            reasons.append('mismatch_' + key)
    if not a.get('source_ref') or not b.get('source_ref'):
        reasons.append('missing_source')
    try:
        ta, tb = timestamp(a['as_of']), timestamp(b['as_of'])
        if ta == tb:
            reasons.append('same_asof_not_revision')
        if tb < ta:
            reasons.append('reversed_asof')
        for item in (a, b):
            if timestamp(item['available_at']) > timestamp(item['as_of']):
                reasons.append('lookahead')
        for item in (a, b):
            value = item['value']
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                reasons.append('invalid_value')
    except (ValueError, KeyError, TypeError, AttributeError):
        reasons.append('invalid_or_missing_time_or_value')
    if reasons:
        return {'status': 'incompatible', 'reasons': sorted(set(reasons)), 'change': None}
    return {'status': 'comparable', 'reasons': [], 'change': b['value'] - a['value'],
            'relative_change': None if a['value'] == 0 else b['value'] / a['value'] - 1,
            'dealer_neutrality': 'not_inferred', 'probability': None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory')
    parser.add_argument('--output')
    args = parser.parse_args()
    report = audit(args.directory)
    text = json.dumps(report, indent=2, allow_nan=False) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text, end='')
    raise SystemExit(1 if report['errors'] else 0)
