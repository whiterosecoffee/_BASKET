"""Offline structural qualification, never verification of evidence truth."""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / 'receipt.schema.json').read_text())
FORMATS = FormatChecker()


@FORMATS.checks('date-time', raises=(ValueError, TypeError))
def _date_time(value):
    # Supply this checker explicitly: jsonschema's optional RFC3339 dependency
    # is not guaranteed to exist in an offline Python environment.
    if not isinstance(value, str):
        return True  # Type validation is the schema's responsibility.
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})', value):
        return False
    return _time(value).utcoffset() is not None


VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FORMATS)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def _time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00').replace('z', '+00:00'))


def validate(receipts):
    """Validate one receipt or a batch; duplicates are compared within this batch only."""
    batch = receipts if isinstance(receipts, list) else [receipts]
    errors, seen = [], {}
    if not batch:
        errors.append('batch: must contain at least one receipt')
    for index, receipt in enumerate(batch):
        prefix = f'receipts[{index}]'
        structural = sorted(VALIDATOR.iter_errors(receipt), key=lambda e: (str(list(e.path)), e.message))
        for error in structural:
            errors.append(f'{prefix}/{"/".join(map(str, error.path))}: {error.message}')
        if structural:
            continue
        run_id = receipt['run_id']
        encoded = canonical(receipt)
        if run_id in seen and seen[run_id] != encoded:
            errors.append(f'{prefix}: conflicting duplicate run_id {run_id}')
        seen[run_id] = encoded
        sources = [source['source_id'] for source in receipt['sources']]
        if len(set(sources)) != len(sources):
            errors.append(f'{prefix}: duplicate source_id')
        for source in receipt['sources']:
            if _time(source['checked_at']) > _time(receipt['checked_at']):
                errors.append(f'{prefix}: source checked after receipt')
        for delta in receipt['new_deltas']:
            if delta['source_id'] not in sources:
                errors.append(f'{prefix}: delta names unchecked source')
        evidence = {item['id']: item for item in receipt['evidence']}
        if len(evidence) != len(receipt['evidence']):
            errors.append(f'{prefix}: duplicate evidence id')
        for item in receipt['evidence']:
            if item['revision'] is not None and item['revision'] != receipt['subject_revision']:
                errors.append(f'{prefix}: evidence revision differs from subject_revision')
        for field, kind in [('test_evidence', 'test'), ('acceptance_evidence', 'acceptance')]:
            for evidence_id in receipt[field]:
                item = evidence.get(evidence_id)
                if item is None or item['kind'] != kind or item['result'] != 'pass':
                    errors.append(f'{prefix}: {field} must reference passing {kind} evidence: {evidence_id}')
    return {'valid': not errors, 'validation_scope': 'structural_only',
            'claims_verified': False, 'receipt_count': len(batch),
            'unique_run_count': len(seen), 'errors': errors}


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def _constant(value):
    raise ValueError(f'non-JSON numeric constant: {value}')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=_pairs, parse_constant=_constant)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSON receipt or array of receipts; read only')
    args = parser.parse_args()
    try:
        raw = Path(args.input).read_bytes()
        data = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
        result = validate(data)
        result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    except (OSError, UnicodeError, ValueError) as error:
        result = {'valid': False, 'validation_scope': 'structural_only', 'claims_verified': False,
                  'errors': [str(error)]}
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
