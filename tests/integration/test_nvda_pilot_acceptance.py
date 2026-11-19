"""Independent B01 black-box acceptance for #148's NVDA-only resolver pilot.

All fixture market/financial values and documents below are SYNTHETIC. No network,
provider credentials or private source package is required for these regressions.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from runtime.ticker_data import TickerStore
from orchestration.nvda_pilot.store import Pilot, PilotError, canonical, freeze

EARLY = '2026-11-01T12:00:00Z'
LATE = '2026-11-02T12:00:00Z'
FROZEN = '2026-11-04T02:00:00Z'


def file_hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class NvdaPilotIndependentAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.make_source('source')
        self.pilot = Pilot(self.base / 'destination')
        self.manifest = freeze(self.source, FROZEN)

    def make_source(self, name, first_close=101):
        source = self.base / name
        source.mkdir()
        reports = source / 'reports'
        reports.mkdir()
        # Build proper immutable identities using the accepted existing adapter.
        building = TickerStore(self.base / (name + '-writer'))
        market = {
            'schema': 'basket.ticker_observation@1', 'entity_id': 'NVDA',
            'kind': 'market_bar', 'source': 'SYNTHETIC_TEST_ONLY',
            'source_record_id': 'NVDA:1m:synthetic-first:unadjusted',
            'observed_at': '2026-10-30T13:30:00Z',
            'available_at': '2026-11-01T10:00:00Z',
            'ingested_at': '2026-11-01T10:01:00Z',
            'currency': 'USD', 'ttd_seconds': 0,
            'value': {'interval': '1m', 'adjustment_basis': 'unadjusted',
                      'open': 100, 'high': 110, 'low': 99,
                      'close': first_close, 'volume': 1000, 'vwap': 100.5,
                      'transactions': 10}}
        r = building.put(market)
        self.assertEqual(r['status'], 'created')
        first = r['records'][0]
        correction = copy.deepcopy(market)
        correction['value']['close'] = first_close + 1
        correction['available_at'] = '2026-11-02T10:00:00Z'
        correction['ingested_at'] = '2026-11-02T10:01:00Z'
        correction['supersedes'] = first['record_id']
        self.assertEqual(building.put(correction, first['record_id'])['status'], 'revised')
        documents = []
        for number, retrieved in [(1, '2026-11-01T11:00:00Z'), (2, '2026-11-02T11:00:00Z')]:
            name = f'FY2026-Q{number}.md'
            text = f'# SYNTHETIC NVDA acceptance report {number}\nNot a real issuer disclosure.\n'
            (reports / name).write_text(text)
            documents.append({
                'schema': 'basket.source_document@1', 'entity_id': 'NVDA',
                'document_type': 'quarterly_earnings_release',
                'fiscal_quarter': f'FY2026-Q{number}', 'period_end': '2026-07-26',
                'published_on': '2026-08-26', 'retrieved_at': retrieved,
                'source_url': f'https://nvidianews.nvidia.com/news/synthetic-test-only-{number}',
                'local_file': name, 'representation': 'synthetic_markdown',
                'content_sha256': hashlib.sha256(text.encode()).hexdigest(),
                'verification': 'SYNTHETIC_TEST_ONLY'})
        (reports / 'manifest.jsonl').write_text(''.join(json.dumps(d) + '\n' for d in documents))
        fact = {
            'schema': 'basket.ticker_observation@1', 'entity_id': 'NVDA',
            'kind': 'financial_fact', 'source': 'SYNTHETIC_TEST_ONLY',
            'source_record_id': 'NVDA:synthetic-revenue',
            'observed_at': '2026-07-26T00:00:00Z',
            'available_at': '2026-11-01T11:00:00Z',
            'ingested_at': '2026-11-01T11:01:00Z',
            'currency': 'USD', 'ttd_seconds': 0,
            'value': {'concept': 'Revenue', 'taxonomy': 'synthetic_test',
                      'period_start': None, 'period_end': '2026-07-26', 'unit': 'USD',
                      'amount': 10, 'basis': 'reported', 'source_url': documents[0]['source_url'],
                      'excerpt': 'SYNTHETIC TEST ONLY: revenue ten dollars'}}
        self.assertEqual(building.put(fact)['status'], 'created')
        shutil.copyfile(building.path, source / 'observations.jsonl')
        return source

    def activate(self):
        staged = self.pilot.stage(self.source, self.manifest)
        self.assertEqual(staged['status'], 'staged')
        self.pilot.activate(self.manifest['manifest_id'])
        return self.pilot.report(EARLY)

    def test_manifest_is_repeatable_and_source_hashed(self):
        again = freeze(self.source, FROZEN)
        self.assertEqual(canonical(self.manifest), canonical(again))
        self.assertEqual(len(self.manifest['manifest_id']), 64)
        for entry in self.manifest['files']:
            payload = (self.source / entry['path']).read_bytes()
            self.assertEqual(entry['sha256'], hashlib.sha256(payload).hexdigest())
            self.assertEqual(entry['size'], len(payload))

    def test_nondestructive_stage_and_idempotent_retry(self):
        before = file_hashes(self.source)
        self.activate()
        retry = self.pilot.stage(self.source, self.manifest)
        self.assertEqual(retry['status'], 'unchanged')
        self.assertEqual(before, file_hashes(self.source))
        self.assertEqual(self.pilot.report(EARLY)['market']['observations'], 1)

    def test_two_reads_and_new_process_object_are_canonical_identical(self):
        first = self.activate()
        second = Pilot(self.base / 'destination').report(EARLY)
        self.assertEqual(canonical(first), canonical(second))
        self.assertEqual(first['source_manifest_id'], self.manifest['manifest_id'])
        self.assertEqual(first['logical_path'], '_TICKERS/NVDA')
        self.assertNotIn(str(self.base), canonical(first).decode())

    def test_asof_uses_ingestion_and_report_retrieval_not_publication(self):
        early = self.activate()
        late = self.pilot.report(LATE)
        self.assertEqual(len(early['source_reports']), 1)
        self.assertEqual(len(late['source_reports']), 2)
        self.assertEqual(len(early['financial_facts']), 1)
        self.assertNotEqual(early['observation_ids_sha256'], late['observation_ids_sha256'])
        self.assertEqual(self.pilot.report('2026-10-31T23:59:59Z')['status'], 'no_data')
        self.assertEqual(canonical(early), canonical(self.pilot.report(EARLY)))

    def test_resolver_is_nvda_only_and_read_only(self):
        self.activate()
        resolved = self.pilot.resolve('NVDA', 'observations', 'read', EARLY)
        self.assertEqual(resolved['manifest_id'], self.manifest['manifest_id'])
        self.assertTrue(Path(resolved['physical_path']).is_file())
        for symbol, kind, mode in [('MU', 'observations', 'read'),
                                   ('NVDA', 'observations', 'write'),
                                   ('NVDA', 'arbitrary', 'read')]:
            with self.assertRaises(PilotError):
                self.pilot.resolve(symbol, kind, mode, EARLY)

    def test_resolved_report_files_are_usable_relative_to_returned_directory(self):
        self.activate()
        resolved = self.pilot.resolve('NVDA', 'source_reports', 'read', EARLY)
        self.assertEqual(len(resolved['files']), 1)
        for name in resolved['files']:
            document = Path(resolved['physical_path']) / name
            self.assertTrue(document.is_file(), f'Resolver returned unusable document path: {document}')
            self.assertIn('SYNTHETIC NVDA', document.read_text())

    def test_missing_active_root_has_no_silent_legacy_fallback(self):
        legacy = TickerStore(self.base / 'destination')
        legacy.path.parent.mkdir(parents=True)
        shutil.copyfile(self.source / 'observations.jsonl', legacy.path)
        with self.assertRaises(PilotError):
            self.pilot.report(EARLY)

    def test_source_hash_mismatch_prevents_staging(self):
        (self.source / 'reports/FY2026-Q1.md').write_text('corrupt source')
        with self.assertRaises(PilotError):
            self.pilot.stage(self.source, self.manifest)
        with self.assertRaises(PilotError):
            self.pilot.report(EARLY)

    def test_staged_observation_corruption_blocks_reads(self):
        self.activate()
        resolved = self.pilot.resolve('NVDA', 'observations', 'read', EARLY)
        Path(resolved['physical_path']).write_text('{partial-json')
        with self.assertRaises(PilotError):
            self.pilot.report(EARLY)

    def test_staged_document_corruption_blocks_read_and_reactivation(self):
        self.activate()
        resolved = self.pilot.resolve('NVDA', 'source_reports', 'read', EARLY)
        directory = Path(resolved['physical_path'])
        (directory / 'FY2026-Q1.md').write_text('corrupt staged report')
        with self.assertRaises(PilotError):
            self.pilot.report(EARLY)
        with self.assertRaises(PilotError):
            self.pilot.activate(self.manifest['manifest_id'], expected_current=self.manifest['manifest_id'])

    def test_stale_activation_does_not_replace_current(self):
        baseline = self.activate()
        other = self.make_source('second', first_close=103)
        manifest = freeze(other, FROZEN)
        self.pilot.stage(other, manifest)
        with self.assertRaises(PilotError):
            self.pilot.activate(manifest['manifest_id'], expected_current='f' * 64)
        self.assertEqual(canonical(baseline), canonical(self.pilot.report(EARLY)))

    def test_failed_atomic_activation_preserves_current_report(self):
        baseline = self.activate()
        other = self.make_source('second', first_close=103)
        manifest = freeze(other, FROZEN)
        self.pilot.stage(other, manifest)
        with patch('orchestration.nvda_pilot.store.os.replace', side_effect=OSError('simulated interrupted pointer write')):
            with self.assertRaises(PilotError):
                self.pilot.activate(manifest['manifest_id'], expected_current=self.manifest['manifest_id'])
        self.assertEqual(canonical(baseline), canonical(self.pilot.report(EARLY)))

    def test_explicit_rollback_restores_prior_frozen_report(self):
        baseline = self.activate()
        other = self.make_source('second', first_close=103)
        manifest = freeze(other, FROZEN)
        self.pilot.stage(other, manifest)
        self.pilot.activate(manifest['manifest_id'], expected_current=self.manifest['manifest_id'])
        self.assertNotEqual(canonical(baseline), canonical(self.pilot.report(EARLY)))
        self.pilot.rollback(expected_current=manifest['manifest_id'])
        self.assertEqual(canonical(baseline), canonical(self.pilot.report(EARLY)))

    def test_interrupted_stage_keeps_active_and_retry_recovers(self):
        baseline = self.activate()
        other = self.make_source('second', first_close=103)
        manifest = freeze(other, FROZEN)
        copyfile = shutil.copyfile
        calls = []
        def interrupted(source, destination, *args, **kwargs):
            calls.append(str(destination))
            if len(calls) == 2:
                Path(destination).write_bytes(b'partial staging bytes')
                raise OSError('simulated interrupted file copy')
            return copyfile(source, destination, *args, **kwargs)
        with patch('orchestration.nvda_pilot.store.shutil.copyfile', side_effect=interrupted):
            with self.assertRaises(PilotError):
                self.pilot.stage(other, manifest)
        self.assertGreaterEqual(len(calls), 2)
        self.assertEqual(canonical(baseline), canonical(self.pilot.report(EARLY)))
        versions = self.base / 'destination/_TICKERS/NVDA/versions'
        self.assertFalse((versions / manifest['manifest_id']).exists())
        self.assertEqual(list(versions.glob('.stage-*')), [])
        self.assertEqual(self.pilot.stage(other, manifest)['status'], 'staged')

    def test_stale_lock_is_explicit_and_not_auto_deleted(self):
        self.activate()
        lock = self.base / 'destination/_TICKERS/NVDA/.pilot.lock'
        lock.write_text('stale owner requires inspection')
        with self.assertRaises(PilotError) as caught:
            self.pilot.stage(self.source, self.manifest)
        self.assertEqual(caught.exception.code, 'LOCKED')
        self.assertTrue(lock.exists())

    def test_corrupt_pointer_is_not_empty_data(self):
        self.activate()
        pointer = self.base / 'destination/_TICKERS/NVDA/active.json'
        pointer.write_text('{partial-pointer')
        with self.assertRaises(PilotError) as caught:
            self.pilot.report(EARLY)
        self.assertEqual(caught.exception.code, 'INVALID_POINTER')

    def test_failed_rollback_keeps_new_version_active(self):
        self.activate()
        other = self.make_source('second', first_close=103)
        manifest = freeze(other, FROZEN)
        self.pilot.stage(other, manifest)
        self.pilot.activate(manifest['manifest_id'], expected_current=self.manifest['manifest_id'])
        current = self.pilot.report(EARLY)
        old_version = self.base / 'destination/_TICKERS/NVDA/versions' / self.manifest['manifest_id']
        (old_version / 'observations.jsonl').write_text('corrupted prior version')
        with self.assertRaises(PilotError):
            self.pilot.rollback(expected_current=manifest['manifest_id'])
        self.assertEqual(canonical(current), canonical(self.pilot.report(EARLY)))

    def test_corrupt_manifest_type_is_structured_rejection(self):
        self.activate()
        version = self.base / 'destination/_TICKERS/NVDA/versions' / self.manifest['manifest_id']
        (version / 'SOURCE_MANIFEST.json').write_text('[]')
        with self.assertRaises(PilotError):
            self.pilot.report(EARLY)

    def test_cli_missing_root_error_is_structured(self):
        proc = subprocess.run([sys.executable, '-m', 'orchestration.nvda_pilot.cli',
            '--root', str(self.base / 'not-active'), 'report', '--as-of', EARLY],
            capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 1)
        error = json.loads(proc.stdout)
        self.assertEqual(error['schema'], 'basket.nvda_pilot_error@1')
        self.assertEqual(error['status'], 'error')
        self.assertEqual(error['code'], 'BLOCKED_CANONICAL_DATA')

    def test_cli_metadata_output_symlink_cannot_overwrite_source(self):
        original = (self.source / 'observations.jsonl').read_bytes()
        output = self.base / 'SOURCE_MANIFEST.json'
        output.symlink_to(self.source / 'observations.jsonl')
        proc = subprocess.run([sys.executable, '-m', 'orchestration.nvda_pilot.cli',
            '--root', str(self.base / 'destination'), 'freeze', '--source', str(self.source),
            '--frozen-at', FROZEN, '--output', str(output)],
            capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(json.loads(proc.stdout)['status'], 'error')
        self.assertEqual((self.source / 'observations.jsonl').read_bytes(), original)

    def test_manifest_role_mismatch_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        entry = next(x for x in manifest['files'] if x['path'] == 'observations.jsonl')
        entry['role'] = 'supporting_evidence'
        del manifest['manifest_id']
        manifest['manifest_id'] = hashlib.sha256(canonical(manifest)).hexdigest()
        with self.assertRaises(PilotError):
            self.pilot.stage(self.source, manifest)

    def test_supporting_warnings_do_not_leak_into_earlier_replay(self):
        warning = {'code': 'SYNTHETIC_LATER_FINDING', 'detail': 'Known only at the later verification time.'}
        (self.source / 'reports/retrieval-result.json').write_text(json.dumps({
            'verified_at': '2026-11-02T11:00:00Z', 'reconciliation_warnings': [warning]}))
        manifest = freeze(self.source, FROZEN)
        self.pilot.stage(self.source, manifest)
        self.pilot.activate(manifest['manifest_id'])
        self.assertEqual(self.pilot.report(EARLY)['source_reconciliation_warnings'], [])
        self.assertEqual(self.pilot.report(LATE)['source_reconciliation_warnings'], [warning])

    def test_manifest_path_traversal_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['files'][0]['path'] = '../outside.jsonl'
        del manifest['manifest_id']
        manifest['manifest_id'] = hashlib.sha256(canonical(manifest)).hexdigest()
        with self.assertRaises(PilotError):
            self.pilot.stage(self.source, manifest)

    def test_symlink_source_is_rejected(self):
        outside = self.base / 'outside.jsonl'
        shutil.copyfile(self.source / 'observations.jsonl', outside)
        (self.source / 'observations.jsonl').unlink()
        (self.source / 'observations.jsonl').symlink_to(outside)
        with self.assertRaises(PilotError):
            freeze(self.source, FROZEN)


if __name__ == '__main__':
    unittest.main()
