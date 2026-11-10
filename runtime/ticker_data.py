#!/usr/bin/env python3
"""NVDA pilot: local repository adapter over the existing observation contract.

One revision journal, no server/scheduler. Public methods return typed results.
The recovered observations module supplies validation, identity and replay.
"""
import argparse
import csv
import hashlib
import io
import copy
import datetime as dt
import json
import os
from pathlib import Path
import tempfile

from jsonschema import Draft202012Validator, FormatChecker
try:
    from . import observations as journal
except ImportError:
    import observations as journal

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / 'schemas/ticker-data.v1.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


class StoreError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def result(status, records=(), snapshot=None, errors=()):
    return {'schema': 'basket.ticker_data_result@1', 'entity_id': 'NVDA',
            'status': status, 'records': list(records), 'snapshot_sha256': snapshot,
            'errors': list(errors)}


def failure(exc):
    return result('conflict' if isinstance(exc, StoreError) and exc.code in
                  ('HEAD_CHANGED', 'LOCKED') else 'rejected',
                  errors=[{'code': getattr(exc, 'code', 'INVALID_DATA'), 'message': str(exc)}])


def validate(row):
    # JSON Schema's number accepts non-finite Python floats; canonical JSON does not.
    journal.canonical(row)
    errors = sorted(VALIDATOR.iter_errors(row), key=lambda e: str(list(e.path)))
    if errors:
        raise StoreError('INVALID_DATA', errors[0].message)
    journal.validate(row)
    if journal.timestamp(row['observed_at']) > journal.timestamp(row['available_at']):
        raise StoreError('INVALID_TIME', 'availability cannot precede observation time')
    if row.get('retracted'):
        return row
    v = row['value']
    if row['kind'] == 'market_bar':
        if not v['low'] <= min(v['open'], v['close']) <= max(v['open'], v['close']) <= v['high']:
            raise StoreError('INVALID_OHLC', 'low <= open/close <= high required')
    elif v['period_start'] and v['period_start'] > v['period_end']:
        raise StoreError('INVALID_PERIOD', 'period_start exceeds period_end')
    return row


def key(row):
    return row['entity_id'], row['kind'], row['source_record_id']


def content(row):
    # Retrieval time and revision pointers are not economic changes.
    return {k: v for k, v in row.items() if k not in
            ('record_id', 'ingested_at', 'available_at', 'source_fingerprint', 'supersedes')}


class TickerStore:
    """Root is an explicitly selected local data directory; pilot accepts NVDA only."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.path = self.root / 'tickers' / 'NVDA' / 'observations.jsonl'

    def _safe(self):
        if self.path.is_symlink() or not self.path.resolve().is_relative_to(self.root):
            raise StoreError('UNSAFE_PATH', 'journal must remain within the local data root')

    def _load(self):
        self._safe()
        rows = journal.read_journal(self.path)
        ids = set()
        heads = {}
        for row in rows:
            if not isinstance(row, dict):
                raise StoreError('CORRUPT_JOURNAL', 'expected JSON object per line')
            validate({k: v for k, v in row.items() if k != 'record_id'})
            if row.get('record_id') != journal.digest({k: v for k, v in row.items() if k != 'record_id'}):
                raise StoreError('CORRUPT_JOURNAL', 'record content hash mismatch')
            if row['record_id'] in ids:
                raise StoreError('CORRUPT_JOURNAL', 'duplicate revision')
            prior = heads.get(key(row))
            if (prior and row.get('supersedes') != prior['record_id']) or (not prior and row.get('supersedes')):
                raise StoreError('CORRUPT_JOURNAL', 'revision chain is not linear')
            if prior and (journal.timestamp(row['available_at']) < journal.timestamp(prior['available_at']) or
                          journal.timestamp(row['ingested_at']) < journal.timestamp(prior['ingested_at'])):
                raise StoreError('CORRUPT_JOURNAL', 'revision timestamps move backwards')
            ids.add(row['record_id'])
            heads[key(row)] = row
        return rows, heads

    def put(self, observation, expected_head=None):
        return self.put_many([observation], [expected_head])

    def put_many(self, observations, expected_heads=None):
        """Retry-safe create/update/retract. Updates require the current record SHA.

        Uses a lock and atomic file replacement, so interrupted writes preserve
        the previous complete journal. Stale locks fail closed and need inspection.
        """
        lock = None
        acquired = False
        staged = None
        try:
            incoming = copy.deepcopy(list(observations))
            expected_heads = list(expected_heads) if expected_heads is not None else [None] * len(incoming)
            if len(expected_heads) != len(incoming):
                raise StoreError('INVALID_DATA', 'one expected_head per observation required')
            if not incoming:
                raise StoreError('INVALID_DATA', 'empty write batch')
            for row, expected_head in zip(incoming, expected_heads):
                validate(row)
                if expected_head != row.get('supersedes'):
                    raise StoreError('HEAD_CHANGED', 'expected_head must match supersedes')
            self._safe()
            self.path.parent.mkdir(parents=True, exist_ok=True)
            lock = self.path.with_suffix('.lock')
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError as exc:
                raise StoreError('LOCKED', 'another writer or stale lock requires inspection') from exc
            acquired = True
            os.close(fd)
            rows, heads = self._load()
            accepted, statuses = [], []
            for row, expected_head in zip(incoming, expected_heads):
                prior = heads.get(key(row))
                if prior and content(prior) == content(row):
                    # An identical retry may refer to the preceding revision, but a
                    # wholly unrelated expected head is still a conflict.
                    if expected_head not in (None, prior['record_id'], prior.get('supersedes')):
                        raise StoreError('HEAD_CHANGED', 'retry refers to unrelated revision')
                    accepted.append(prior)
                    statuses.append('unchanged')
                    continue
                if (prior and expected_head != prior['record_id']) or (not prior and expected_head):
                    raise StoreError('HEAD_CHANGED', 'revision requires current record_id')
                if prior and (journal.timestamp(row['available_at']) < journal.timestamp(prior['available_at']) or
                              journal.timestamp(row['ingested_at']) < journal.timestamp(prior['ingested_at'])):
                    raise StoreError('INVALID_TIME', 'revision timestamps cannot move backwards')
                row['record_id'] = journal.digest(row)
                rows.append(row)
                heads[key(row)] = row
                accepted.append(row)
                statuses.append('retracted' if row.get('retracted') else 'revised' if prior else 'created')
            if all(status == 'unchanged' for status in statuses):
                return result('unchanged', accepted, journal.digest(rows))
            with tempfile.NamedTemporaryFile(mode='wb', dir=self.path.parent, prefix='.nvda-', delete=False) as out:
                staged = Path(out.name)
                for item in rows:
                    out.write(journal.canonical(item) + b'\n')
                out.flush()
                os.fsync(out.fileno())
            os.replace(staged, self.path)
            return result(statuses[0] if len(set(statuses)) == 1 else 'updated',
                          accepted, journal.digest(rows))
        except (ValueError, TypeError, OSError, KeyError) as exc:
            return failure(exc)
        finally:
            if staged is not None:
                staged.unlink(missing_ok=True)
            if acquired:
                lock.unlink(missing_ok=True)

    def read(self, as_of, kind=None, start=None, end=None, include_retracted=False):
        """As-of respects both public availability and local ingestion.

        Start inclusive, end exclusive; no implied calendar/session completeness.
        """
        try:
            cutoff = journal.timestamp(as_of)
            if kind is not None and kind not in ('market_bar', 'financial_fact'):
                raise StoreError('INVALID_QUERY', 'unknown dataset')
            lower = journal.timestamp(start) if start else None
            upper = journal.timestamp(end) if end else None
            if lower and upper and lower >= upper:
                raise StoreError('INVALID_QUERY', 'start must precede end')
            rows, _ = self._load()
            selected = journal.replay(rows, as_of)
            selected = [r for r in selected if (kind is None or r['kind'] == kind)
                        and (include_retracted or not r.get('retracted'))
                        and (lower is None or journal.timestamp(r['observed_at']) >= lower)
                        and (upper is None or journal.timestamp(r['observed_at']) < upper)]
            return result('ok' if selected else 'no_data', selected,
                          journal.snapshot(rows, cutoff.isoformat())['snapshot_sha256'])
        except (ValueError, TypeError, OSError, KeyError) as exc:
            return failure(exc)


def massive_bar(response, index, *, interval, adjustment_basis, available_at, ingested_at):
    """Normalize one archived Massive aggregate; never treats a bar as a trade.

    The caller supplies availability and explicit query interval/basis; do not
    invent publication time or infer complete coverage from one response.
    """
    if response.get('ticker') != 'NVDA' or response.get('status') not in ('OK', 'DELAYED'):
        raise StoreError('SOURCE_FAILURE', 'successful NVDA response required')
    if response.get('next_url'):
        raise StoreError('INCOMPLETE_PAGE', 'fetch remaining pages before importing')
    if response.get('adjusted') is not (adjustment_basis == 'split_adjusted'):
        raise StoreError('ADJUSTMENT_MISMATCH', 'response does not match requested basis')
    bar = response['results'][index]
    observed = dt.datetime.fromtimestamp(bar['t'] / 1000, dt.timezone.utc).isoformat()
    row = {'schema': 'basket.ticker_observation@1', 'entity_id': 'NVDA', 'kind': 'market_bar',
           'source': 'Massive', 'source_record_id': f'NVDA:{interval}:{bar["t"]}:{adjustment_basis}',
           'observed_at': observed, 'available_at': available_at, 'ingested_at': ingested_at,
           'currency': 'USD', 'ttd_seconds': 0,
           'value': {'interval': interval, 'adjustment_basis': adjustment_basis,
                     **{name: bar[alias] for name, alias in
                        [('open','o'),('high','h'),('low','l'),('close','c'),('volume','v')]},
                     'vwap': bar.get('vw'), 'transactions': bar.get('n')}}
    return validate(row)


def massive_csv_observations(text, *, adjustment_basis, retrieved_at):
    """Adapter for the connected Massive tool's aggregate CSV output.

    Use retrieval as the conservative first-verified availability bound. This
    does not claim to recover the original publication time or full coverage.
    """
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != ['v', 'vw', 'o', 'c', 'h', 'l', 't', 'n']:
        raise StoreError('INVALID_SOURCE', 'unexpected Massive aggregate columns')
    fingerprint = hashlib.sha256(text.encode()).hexdigest()
    rows = []
    for raw in reader:
        if None in raw or any(v is None for v in raw.values()):
            raise StoreError('INVALID_SOURCE', 'incomplete CSV row')
        item = {k: int(raw[k]) if k in ('t', 'n') else float(raw[k]) for k in raw}
        row = massive_bar({'ticker': 'NVDA', 'status': 'OK',
                           'adjusted': adjustment_basis == 'split_adjusted', 'results': [item]},
                          0, interval='1m', adjustment_basis=adjustment_basis,
                          available_at=retrieved_at, ingested_at=retrieved_at)
        row['source_fingerprint'] = fingerprint
        rows.append(row)
    if not rows:
        raise StoreError('NO_SOURCE_DATA', 'empty response does not establish coverage')
    return rows


def legacy_bars(path, metadata):
    """Read existing eight-field market.daily@1 rows without reinterpreting them.

    Preserve source metadata. Missing availability means these cannot silently
    become point-in-time verified observations.
    """
    if metadata.get('entity_id') != 'NVDA' or metadata.get('schema') != 'market.daily@1':
        raise StoreError('INVALID_LEGACY', 'NVDA market.daily@1 metadata required')
    rows = journal.read_journal(path)
    schema = json.loads((Path(__file__).resolve().parents[1] / 'schemas/history/market.daily.v1.json').read_text())
    check = Draft202012Validator(schema)
    for row in rows:
        check.validate(row)
        if not row[3] <= min(row[1], row[4]) <= max(row[1], row[4]) <= row[2]:
            raise StoreError('INVALID_OHLC', 'invalid legacy OHLC')
        journal.canonical(row)
    return {'schema': 'basket.legacy_history_result@1', 'entity_id': 'NVDA',
            'status': 'ok' if rows else 'no_data', 'records': rows,
            'metadata': copy.deepcopy(metadata), 'point_in_time_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='explicit durable local data root')
    sub = parser.add_subparsers(dest='action', required=True)
    put = sub.add_parser('put')
    put.add_argument('--input', required=True)
    put.add_argument('--expected-head')
    read = sub.add_parser('read')
    read.add_argument('--as-of', required=True)
    read.add_argument('--kind', choices=['market_bar', 'financial_fact'])
    imp = sub.add_parser('import-massive')
    imp.add_argument('--input', required=True)
    imp.add_argument('--retrieved-at', required=True)
    imp.add_argument('--adjustment-basis', required=True, choices=['unadjusted', 'split_adjusted'])
    args = parser.parse_args()
    store = TickerStore(args.root)
    try:
        if args.action == 'put':
            value = store.put(json.loads(Path(args.input).read_text()), args.expected_head)
        elif args.action == 'import-massive':
            rows = massive_csv_observations(Path(args.input).read_text(), adjustment_basis=args.adjustment_basis, retrieved_at=args.retrieved_at)
            value = store.put_many(rows)
        else:
            value = store.read(args.as_of, args.kind)
    except (ValueError, OSError) as exc:
        value = failure(exc)
    print(json.dumps(value, allow_nan=False))
    return 1 if value['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
