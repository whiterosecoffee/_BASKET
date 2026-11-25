"""Content-addressed NVDA source snapshots with a single controlled resolver.

Reuse runtime.ticker_data for observation validation, revisions and as-of reads.
Source files are never edited. A version becomes visible only by an atomic,
compare-and-swap activation pointer; immutable versions are read-only.
"""
from contextlib import contextmanager
from functools import wraps
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from zoneinfo import ZoneInfo

from runtime.ticker_data import TickerStore
from runtime.observations import canonical, digest, timestamp

META = 'SOURCE_MANIFEST.json'


class PilotError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def typed_errors(function):
    @wraps(function)
    def checked(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except PilotError:
            raise
        except OSError as exc:
            raise PilotError('IO_ERROR', str(exc)) from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise PilotError('INVALID_INPUT', str(exc)) from exc
    return checked


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instant(value):
    try:
        return timestamp(value).isoformat().replace('+00:00', 'Z')
    except (ValueError, TypeError, AttributeError) as exc:
        raise PilotError('INVALID_TIME', 'timezone-aware as_of/frozen_at required') from exc


def safe_path(root, name):
    if not isinstance(name, str) or '\\' in name or not name:
        raise PilotError('UNSAFE_PATH', 'relative POSIX path required')
    relative = PurePosixPath(name)
    if relative.is_absolute() or any(p in ('..', '.') for p in name.split('/')):
        raise PilotError('UNSAFE_PATH', 'unsafe relative path')
    target = root.joinpath(*relative.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise PilotError('UNSAFE_PATH', 'path escapes selected root')
    part = root
    for component in relative.parts:
        part = part / component
        if part.is_symlink():
            raise PilotError('UNSAFE_PATH', 'symlinks are not source evidence')
    return target


def files_under(root):
    if not root.is_dir():
        raise PilotError('SOURCE_MISSING', 'source/version directory unavailable')
    files = []
    for p in root.rglob('*'):
        rel = p.relative_to(root).as_posix()
        safe_path(root, rel)
        if p.is_file() and rel != META:
            files.append(rel)
    return sorted(files)


def reader(root):
    # Existing reader path adapted to the frozen package; no second journal logic.
    store = TickerStore(root)
    store.path = root / 'observations.jsonl'
    return store


def documents(root):
    p = safe_path(root, 'reports/manifest.jsonl')
    try:
        rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or row.get('entity_id') != 'NVDA':
                raise PilotError('SOURCE_MISMATCH', 'report identity must be NVDA')
            if not isinstance(row.get('source_url'), str) or not row['source_url'].startswith('https://'):
                raise PilotError('INVALID_SOURCE', 'source report requires explicit HTTPS provenance')
            name = row['local_file']
            if not isinstance(name, str) or PurePosixPath(name).name != name or name in seen:
                raise PilotError('SOURCE_MISMATCH', 'unique report basename required')
            seen.add(name)
            instant(row['retrieved_at'])
            report = safe_path(root, 'reports/' + name)
            if not report.is_file() or sha(report) != row['content_sha256']:
                raise PilotError('SOURCE_MISMATCH', 'report hash differs from source index')
        return rows
    except (KeyError, ValueError, OSError, TypeError) as exc:
        if isinstance(exc, PilotError):
            raise
        raise PilotError('INVALID_SOURCE', 'unreadable report index: ' + str(exc)) from exc


def validate_package(root):
    try:
        rows, _ = reader(root)._load()
        if not rows:
            raise PilotError('SOURCE_MISSING', 'nonempty observation journal required')
        raw = safe_path(root, 'source/massive.csv')
        if raw.is_file():
            fingerprint = sha(raw)
            if any(r['kind'] == 'market_bar' and r.get('source_fingerprint') != fingerprint for r in rows):
                raise PilotError('SOURCE_MISMATCH', 'market records do not reference the packaged raw source')
        return documents(root)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        if isinstance(exc, PilotError):
            raise
        raise PilotError('INVALID_SOURCE', str(exc)) from exc


def manifest_check(manifest):
    if not isinstance(manifest, dict) or set(manifest) != {'schema', 'entity_id', 'frozen_at', 'files', 'manifest_id'}:
        raise PilotError('INVALID_MANIFEST', 'unexpected manifest fields')
    if manifest['schema'] != 'basket.nvda_source_package@1' or manifest['entity_id'] != 'NVDA':
        raise PilotError('SOURCE_MISMATCH', 'NVDA source package required')
    instant(manifest['frozen_at'])
    claimed = manifest['manifest_id']
    if not isinstance(claimed, str) or not re.fullmatch('[0-9a-f]{64}', claimed):
        raise PilotError('INVALID_MANIFEST', 'content-addressed manifest ID required')
    if digest({k: v for k, v in manifest.items() if k != 'manifest_id'}) != claimed:
        raise PilotError('SOURCE_MISMATCH', 'manifest content hash mismatch')
    names = []
    if not isinstance(manifest['files'], list):
        raise PilotError('INVALID_MANIFEST', 'file array required')
    for item in manifest['files']:
        if not isinstance(item, dict) or set(item) != {'path', 'sha256', 'size', 'role', 'available_at'}:
            raise PilotError('INVALID_MANIFEST', 'unexpected file entry fields')
        if not isinstance(item['path'], str) or not isinstance(item['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', item['sha256']):
            raise PilotError('INVALID_MANIFEST', 'file identity/hash required')
        if type(item['size']) is not int or item['size'] < 0:
            raise PilotError('INVALID_MANIFEST', 'file size must be nonnegative integer')
        if item['role'] not in ('observations', 'source_report', 'source_index', 'supporting_evidence'):
            raise PilotError('INVALID_MANIFEST', 'unknown source file role')
        if item['available_at'] is not None:
            instant(item['available_at'])
        names.append(item['path'])
    if len(set(names)) != len(names) or 'observations.jsonl' not in names or 'reports/manifest.jsonl' not in names:
        raise PilotError('INVALID_MANIFEST', 'unique journal and report index required')
    return manifest


@typed_errors
def freeze(source_root, frozen_at):
    root = Path(source_root).resolve()
    available = {r['local_file']: r['retrieved_at'] for r in validate_package(root)}
    files = []
    for name in files_under(root):
        p = safe_path(root, name)
        role = ('observations' if name == 'observations.jsonl' else
                'source_index' if name == 'reports/manifest.jsonl' else
                'source_report' if name.startswith('reports/') and p.name in available else
                'supporting_evidence')
        files.append({'path': name, 'sha256': sha(p), 'size': p.stat().st_size,
                      'role': role, 'available_at': available.get(p.name) if role == 'source_report' else None})
    value = {'schema': 'basket.nvda_source_package@1', 'entity_id': 'NVDA',
             'frozen_at': instant(frozen_at), 'files': files}
    value['manifest_id'] = digest(value)
    return manifest_check(value)


@typed_errors
def verify(root, manifest):
    root = Path(root)
    manifest_check(manifest)
    if files_under(root) != sorted(f['path'] for f in manifest['files']):
        raise PilotError('SOURCE_MISMATCH', 'package file inventory changed')
    for item in manifest['files']:
        p = safe_path(root, item['path'])
        if p.stat().st_size != item['size'] or sha(p) != item['sha256']:
            raise PilotError('SOURCE_MISMATCH', 'source size/hash mismatch: ' + item['path'])
    docs = validate_package(root)
    file_map = {f['path']: f for f in manifest['files']}
    report_paths = {'reports/' + row['local_file'] for row in docs}
    for item in manifest['files']:
        name = item['path']
        expected = ('observations' if name == 'observations.jsonl' else
                    'source_index' if name == 'reports/manifest.jsonl' else
                    'source_report' if name in report_paths else 'supporting_evidence')
        if item['role'] != expected or (expected != 'source_report' and item['available_at'] is not None):
            raise PilotError('SOURCE_MISMATCH', 'file role/availability does not match package semantics')
    for row in docs:
        item = file_map.get('reports/' + row['local_file'])
        if not item or item['role'] != 'source_report' or item['available_at'] != row['retrieved_at']:
            raise PilotError('SOURCE_MISMATCH', 'report availability differs from source index')
    return manifest


class Pilot:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.home = self.root / '_TICKERS' / 'NVDA'

    def _safe(self):
        safe_path(self.root, '_TICKERS/NVDA')

    @contextmanager
    def _lock(self):
        self._safe()
        self.home.mkdir(parents=True, exist_ok=True)
        lock = self.home / '.pilot.lock'
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise PilotError('LOCKED', 'writer or stale lock requires inspection') from exc
        os.close(fd)
        try:
            yield
        finally:
            lock.unlink(missing_ok=True)

    def _version(self, manifest_id):
        if not isinstance(manifest_id, str) or not re.fullmatch('[0-9a-f]{64}', manifest_id):
            raise PilotError('INVALID_MANIFEST', 'invalid version ID')
        return safe_path(self.root, '_TICKERS/NVDA/versions/' + manifest_id)

    def _manifest(self, manifest_id):
        root = self._version(manifest_id)
        try:
            m = json.loads(safe_path(root, META).read_text())
            if not isinstance(m, dict):
                raise PilotError('INVALID_MANIFEST', 'stored manifest must be an object')
            if m.get('manifest_id') != manifest_id:
                raise PilotError('SOURCE_MISMATCH', 'version and source ID disagree')
            return verify(root, m)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            if isinstance(exc, PilotError):
                raise
            raise PilotError('INVALID_SOURCE', str(exc)) from exc

    def _active(self):
        p = safe_path(self.root, '_TICKERS/NVDA/active.json')
        if not p.exists():
            return None
        try:
            value = json.loads(p.read_text())
            if set(value) != {'manifest_id', 'previous_manifest_id'}:
                raise ValueError('unexpected pointer fields')
            self._version(value['manifest_id'])
            if value['previous_manifest_id'] is not None:
                self._version(value['previous_manifest_id'])
            return value
        except (ValueError, OSError, KeyError, TypeError) as exc:
            raise PilotError('INVALID_POINTER', str(exc)) from exc

    @typed_errors
    def stage(self, source_root, manifest):
        source = Path(source_root).resolve()
        with self._lock():
            verify(source, manifest)
            final = self._version(manifest['manifest_id'])
            if final.exists():
                self._manifest(manifest['manifest_id'])
                return {'status': 'unchanged', 'manifest_id': manifest['manifest_id']}
            final.parent.mkdir(parents=True, exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix='.stage-', dir=final.parent))
            try:
                for item in manifest['files']:
                    p = safe_path(stage, item['path'])
                    p.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(safe_path(source, item['path']), p)
                (stage / META).write_bytes(canonical(manifest) + b'\n')
                verify(stage, manifest)
                os.rename(stage, final)
            finally:
                if stage.exists():
                    shutil.rmtree(stage)
            return {'status': 'staged', 'manifest_id': manifest['manifest_id']}

    def _pointer(self, manifest_id, previous):
        staged = None
        try:
            with tempfile.NamedTemporaryFile(mode='wb', dir=self.home, prefix='.pointer-', delete=False) as out:
                staged = Path(out.name)
                out.write(canonical({'manifest_id': manifest_id, 'previous_manifest_id': previous}) + b'\n')
                out.flush()
                os.fsync(out.fileno())
            os.replace(staged, self.home / 'active.json')
        finally:
            if staged is not None:
                staged.unlink(missing_ok=True)

    @typed_errors
    def activate(self, manifest_id, expected_current=None):
        with self._lock():
            self._manifest(manifest_id)
            active = self._active()
            current = active['manifest_id'] if active else None
            if current == manifest_id and expected_current in (current, active['previous_manifest_id']):
                return {'status': 'unchanged', 'manifest_id': current}
            if current != expected_current:
                raise PilotError('HEAD_CHANGED', 'activation expected_current does not match')
            self._pointer(manifest_id, current)
            return {'status': 'activated', 'manifest_id': manifest_id, 'previous_manifest_id': current}

    @typed_errors
    def rollback(self, expected_current):
        with self._lock():
            active = self._active()
            if not active or active['manifest_id'] != expected_current:
                raise PilotError('HEAD_CHANGED', 'rollback expected_current does not match')
            previous = active['previous_manifest_id']
            if previous is None:
                raise PilotError('NO_ROLLBACK_TARGET', 'no prior activated version')
            self._manifest(previous)
            self._pointer(previous, active['manifest_id'])
            return {'status': 'rolled_back', 'manifest_id': previous}

    @typed_errors
    def resolve(self, instrument_id, data_kind, access_mode, as_of):
        self._safe()
        instant(as_of)
        if instrument_id != 'NVDA':
            raise PilotError('OUT_OF_SCOPE', 'NVDA-only pilot')
        if access_mode != 'read':
            raise PilotError('READ_ONLY_SNAPSHOT', 'use stage/activate for controlled snapshot writes')
        if data_kind not in ('observations', 'source_reports'):
            raise PilotError('UNKNOWN_DATA_KIND', 'unsupported pilot dataset')
        active = self._active()
        if active is None:
            raise PilotError('BLOCKED_CANONICAL_DATA', 'no approved active NVDA package')
        manifest = self._manifest(active['manifest_id'])
        version = self._version(manifest['manifest_id'])
        descriptor = {'logical_path': '_TICKERS/NVDA', 'manifest_id': manifest['manifest_id'],
                      'as_of': instant(as_of), 'data_kind': data_kind,
                      'physical_path': str(version / ('observations.jsonl' if data_kind == 'observations' else 'reports')),
                      'required_reader': 'TickerStore.read(as_of)' if data_kind == 'observations' else 'eligible files only'}
        if data_kind == 'source_reports':
            descriptor['files'] = [PurePosixPath(f['path']).name for f in manifest['files'] if f['role'] == 'source_report' and
                                   timestamp(f['available_at']) <= timestamp(as_of)]
        return descriptor

    @typed_errors
    def report(self, as_of):
        desc = self.resolve('NVDA', 'observations', 'read', as_of)
        version = self._version(desc['manifest_id'])
        result = reader(version).read(as_of)
        if result['errors']:
            raise PilotError('INVALID_SOURCE', str(result['errors']))
        rows = result['records']
        bars = sorted((r for r in rows if r['kind'] == 'market_bar'), key=lambda r: timestamp(r['observed_at']))
        counts = {}
        fractional = outside = 0
        for bar in bars:
            t = timestamp(bar['observed_at']).astimezone(ZoneInfo('America/New_York'))
            day = t.date().isoformat()
            count = counts.setdefault(day, {'session_date': day, 'bars': 0, 'regular_session_bars': 0})
            count['bars'] += 1
            count['regular_session_bars'] += int((9, 30) <= (t.hour, t.minute) < (16, 0))
            v = bar['value']
            fractional += int(v['volume'] % 1 != 0)
            outside += int(v.get('vwap') is not None and not v['low'] <= v['vwap'] <= v['high'])
        reports = sorted((r for r in documents(version) if timestamp(r['retrieved_at']) <= timestamp(as_of)),
                         key=lambda r: r['local_file'])
        warnings_path = version / 'reports/retrieval-result.json'
        warnings = []
        if warnings_path.exists():
            supporting = json.loads(warnings_path.read_text())
            if not isinstance(supporting, dict) or not isinstance(supporting.get('reconciliation_warnings', []), list):
                raise PilotError('INVALID_SOURCE', 'supporting warnings require an object with a warning list')
            # Preserve declared verification vintage; absent precision defaults
            # conservatively to this package's actual frozen availability.
            known_at = supporting.get('verified_at') or self._manifest(desc['manifest_id'])['frozen_at']
            instant(known_at)
            if timestamp(known_at) <= timestamp(as_of):
                warnings = supporting.get('reconciliation_warnings', [])
        code_root = Path(__file__).resolve().parents[2]
        code_paths = ['orchestration/nvda_pilot/store.py', 'runtime/ticker_data.py',
                      'runtime/observations.py', 'schemas/ticker-data.v1.json']
        return {'schema': 'basket.nvda_evidence_report@1', 'instrument_id': 'NVDA',
                'implementation': {'algorithm': 'nvda_evidence@1.0.0',
                                   'files_sha256': {p: sha(code_root / p) for p in code_paths}},
                'validation_scope': 'integrity_and_replay_only',
                'source_quality_status': 'SOURCE_QUALITY_AMBIGUOUS' if fractional or outside else 'NOT_INDEPENDENTLY_VERIFIED',
                'current_valuation_status': 'NOT_RUN', 'source_reconciliation_warnings': warnings,
                'logical_path': '_TICKERS/NVDA', 'as_of': instant(as_of),
                'source_manifest_id': desc['manifest_id'],
                'status': 'historical_evidence' if rows or reports else 'no_data',
                'market': {'observations': len(bars), 'first_observed_at': bars[0]['observed_at'] if bars else None,
                           'last_observed_at': bars[-1]['observed_at'] if bars else None,
                           'session_counts': [counts[k] for k in sorted(counts)],
                           'adjustment_bases': sorted({b['value']['adjustment_basis'] for b in bars}),
                           'intervals': sorted({b['value']['interval'] for b in bars}),
                           'quality': {'fractional_volume_bars': fractional, 'vwap_outside_ohlc_bars': outside}},
                'financial_facts': sorted((r for r in rows if r['kind'] == 'financial_fact'), key=lambda r: r['record_id']),
                'source_reports': reports, 'observation_snapshot_sha256': result['snapshot_sha256'],
                'observation_ids_sha256': digest(sorted(r['record_id'] for r in rows)),
                'limitations': ['Historical observations, not live data or a current valuation.',
                               'Session counts use ET clock windows; independent exchange-calendar completeness is not certified.',
                               'Fractional volume and VWAP/OHLC anomalies are preserved, not silently sanitized.',
                               'Issuer disclosures are not independently reconciled to SEC filings.',
                               'Availability and ingestion cutoffs are preserved; a later storage copy does not backdate new evidence.']}
