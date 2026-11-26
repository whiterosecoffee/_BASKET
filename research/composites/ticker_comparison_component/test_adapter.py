"""Five outcome checks; shared conformance edge cases remain in the shared suite."""
import copy
from datetime import datetime
import json
import os
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from jsonschema import ValidationError
from adapter import run
from orchestration.component_conformance import canonical, check_exchange, digest

ROOT = Path(__file__).resolve().parents[3]
STAMP = '2026-11-10T12:00:00Z'


def request():
    days = ['2026-11-04', '2026-11-05', '2026-11-06', '2026-11-09']
    values = [(100, 100, 100, 100), (110, 90, 110, 100),
              (121, 99, 99, 100), (108.9, 108.9, 108.9, 100)]
    return dict(rows=[dict(t=int(datetime.fromisoformat(day).replace(
        tzinfo=ZoneInfo('America/New_York')).timestamp() * 1000),
        **dict(zip(('NVDA', 'CRWV', 'SMH', 'QQQ'), prices)))
        for day, prices in zip(days, values)], cutoff='2026-11-09',
        evaluated_at=STAMP, windows=[1, 3], correlation_window=3,
        source=dict(id='synthetic-boundary-fixture', kind='synthetic',
                    entitlement='not_required', currency='USD',
                    basis='split_adjusted_price_return_not_total_return'))


class AdapterTests(unittest.TestCase):
    def execute(self, data, **overrides):
        options = dict(
            compare_path=os.environ.get('BASKET_COMPARE_PATH', str(ROOT /
                'research/composites/market_context/ticker_comparison/compare.py')),
            context_path=os.environ.get('BASKET_CONTEXT_PATH', str(ROOT /
                'engines/composites/market_context/context.py')),
            run_id='test-replay', generated_at=STAMP)
        options.update(overrides)
        return run(data, **options)

    def consume(self, data):
        manifest, call, result, artifacts = self.execute(data)
        # Consumer independently computes the documented request serialization.
        check_exchange(manifest, call, result, artifacts,
                       expected_input_sha256=digest(canonical(data)))
        self.assertEqual(result['status'], 'ok')
        return json.loads(artifacts[result['outputs']['comparison']['artifact']['ref']])

    def test_actual_dependency_output_reaches_consumer(self):
        output = self.consume(request())
        self.assertAlmostEqual(output['windows'][1]['price_return_pct']['NVDA'], 8.9)
        self.assertAlmostEqual(output['windows'][0]['relative_to_qqq_pp']['NVDA'], -10)
        pair = output['correlation_window']['pairs'][0]
        self.assertEqual(pair['paired_returns'], 3)
        self.assertAlmostEqual(pair['pearson'], -0.5)
        self.assertEqual(output['replay_class'], 'current_revision_historical_diagnostic')

    def test_unchanged_input_replay_is_identical_and_does_not_mutate(self):
        data = request(); before = copy.deepcopy(data)
        first = self.execute(data); second = self.execute(data)
        self.assertEqual(first, second)
        self.assertEqual(data, before)
        self.assertEqual(first[2]['quality']['freshness'], 'not_applicable')

    def test_missing_interior_and_new_date_unchanged_price_keep_meaning(self):
        data = request(); data['rows'][1]['NVDA'] = None
        output = self.consume(data)
        self.assertIsNone(output['windows'][1]['price_return_pct']['NVDA'])
        self.assertEqual(output['correlation_window']['pairs'][0]['paired_returns'], 1)
        # QQQ's separately dated prices genuinely did not change, unlike polling
        # the same observation twice. Do not reinterpret this as stale/live data.
        self.assertEqual(output['windows'][0]['price_return_pct']['QQQ'], 0.0)
        self.assertEqual(output['correlation_window']['pairs'][4]['status'], 'constant_series')

    def test_duplicate_or_future_history_returns_typed_failure(self):
        for mutation in ('duplicate', 'future', 'overflow'):
            data = request()
            if mutation == 'duplicate': data['rows'].append(copy.deepcopy(data['rows'][-1]))
            elif mutation == 'future': data['evaluated_at'] = '2026-11-09T23:00:00Z'
            else: data['rows'][0]['t'] = 10**30
            with self.subTest(mutation=mutation):
                manifest, call, result, artifacts = self.execute(data)
                check_exchange(manifest, call, result, artifacts,
                               expected_input_sha256=digest(canonical(data)))
                self.assertEqual(result['status'], 'error')
                self.assertEqual(result['outputs'], {})
                self.assertEqual(result['error']['code'], 'invalid_history')

    def test_changed_dependency_and_invalid_contract_fail_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'wrong.py'
            source.write_text("raise AssertionError('unapproved code ran')\n")
            with self.assertRaisesRegex(ValueError, 'Unapproved compare'):
                self.execute(request(), compare_path=source)
        for key, value in [('currency', 'EUR'), ('entitlement', 'unknown')]:
            data = request(); data['source'][key] = value
            with self.subTest(key=key), self.assertRaises(ValidationError):
                self.execute(data, compare_path='/unreadable-if-preflight-failed')


if __name__ == '__main__':
    unittest.main()
