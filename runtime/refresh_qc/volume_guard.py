"""Pure pre-publication volume check. No fetching, sanitation, I/O or promotion.

The input boundary is JSON bytes so decimal precision is retained before any
binary float conversion. This is not a source-authenticity or full OHLC QC gate.
"""
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re

class VolumeError(ValueError):
    pass

MAX_BYTES = 32 * 1024 * 1024
MAX_ROWS = 100000
NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z')

def _constant(_):
    raise VolumeError('non_finite_json')

def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise VolumeError('duplicate_json_key')
        result[key] = value
    return result

def _volume(value):
    if isinstance(value, bool) or not isinstance(value, (int, Decimal, str)):
        raise VolumeError('invalid_volume_type')
    if isinstance(value, str):
        if len(value) > 1100 or not NUMBER.fullmatch(value):
            raise VolumeError('invalid_volume_encoding')
        value = Decimal(value)
    elif isinstance(value, int):
        value = Decimal(value)
    if not value.is_finite() or value < 0:
        raise VolumeError('invalid_volume_value')
    if len(value.as_tuple().digits) > 1000 or abs(value.adjusted()) > 308:
        raise VolumeError('unsupported_volume_precision')
    return value

def _records(data):
    if not isinstance(data, bytes) or not data or len(data) > MAX_BYTES:
        raise VolumeError('invalid_jsonl_size_or_type')
    result = {}
    for line in data.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line, parse_float=Decimal, parse_constant=_constant, object_pairs_hook=_object)
        except (ValueError, UnicodeError, RecursionError):
            raise VolumeError('invalid_json') from None
        if not isinstance(row, dict):
            raise VolumeError('non_object_record')
        ticker, timestamp = row.get('ticker'), row.get('t')
        if not isinstance(ticker, str) or not re.fullmatch(r'[A-Z][A-Z0-9_.:-]{0,31}', ticker) or not isinstance(timestamp, int) or isinstance(timestamp, bool) or not 0 <= timestamp < 2**63 or timestamp % 60000:
            raise VolumeError('invalid_identity')
        if row.get('class') != 'bar' or row.get('grain') != '1min':
            raise VolumeError('unsupported_class_or_grain')
        key = (ticker, timestamp)
        if key in result:
            raise VolumeError('duplicate_identity')
        result[key] = _volume(row.get('vol'))
        if len(result) > MAX_ROWS:
            raise VolumeError('too_many_rows')
    if not result:
        raise VolumeError('empty_records')
    return result

def verify_volume_preservation(source_jsonl, candidate_jsonl, *, source_unit, candidate_unit):
    """Compare exact volumes for identical unique ticker/minute keys.

Units are caller assertions, not proven by this guard. Currently supports shares
only. No input is changed and no canonical eligibility follows from success.
"""
    if source_unit != 'shares' or candidate_unit != 'shares':
        raise VolumeError('unsupported_or_mismatched_units')
    try:
        source, candidate = _records(source_jsonl), _records(candidate_jsonl)
    except (InvalidOperation, OverflowError):
        raise VolumeError('invalid_numeric_value') from None
    if source.keys() != candidate.keys():
        raise VolumeError('identity_set_mismatch')
    if any(source[key] != candidate[key] for key in source):
        raise VolumeError('volume_changed')
    return {
        'status': 'exact_volume_preserved',
        'guard_version': 1,
        'canonical_eligible': False,
        'source_sha256': hashlib.sha256(source_jsonl).hexdigest(),
        'candidate_sha256': hashlib.sha256(candidate_jsonl).hexdigest(),
        'rows': len(source),
        'fractional_volume_rows': sum(v != v.to_integral_value() for v in source.values()),
        'declared_unit': 'shares',
        'units_verified': False,
        'source_authenticity_verified': False,
        'scope': 'volume equality only; no OHLC, date-partition, entitlement, provenance or publication approval',
    }
