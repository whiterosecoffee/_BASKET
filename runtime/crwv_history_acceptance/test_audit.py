import json
import unittest
from datetime import datetime
from audit import inspect, verify_meta


def payload(*rows):
    return ''.join(json.dumps(r) + '\n' for r in rows).encode()


def row(instant):
    return [int(datetime.fromisoformat(instant).timestamp() * 1000), 10, 12, 9, 11, 100, 13, 2]


class AuditTests(unittest.TestCase):
    def test_dst_fold_preserves_distinct_minutes_and_anomalies(self):
        a = row('2026-11-01T01:30:00-04:00')
        b = row('2026-11-01T01:30:00-05:00')
        info = inspect(payload(a, b), '2026-11-01')
        self.assertEqual(info['records'], 2)
        self.assertEqual(info['vwap_outside_ohlc'], 2)
        self.assertEqual(info['coverage_end_exclusive'], '2026-11-01T01:31:00-05:00')

    def test_utc_midnight_stays_on_exchange_date(self):
        info = inspect(payload(row('2026-11-04T00:00:00+00:00')), '2026-11-03')
        self.assertEqual(info['last_bar_start'], '2026-11-03T19:00:00-05:00')

    def test_mixed_date_rejected(self):
        with self.assertRaises(ValueError):
            inspect(payload(row('2026-11-03T19:00:00-05:00'), row('2026-11-04T04:00:00-05:00')), '2026-11-03')

    def test_duplicate_and_conflicting_duplicate_rejected(self):
        a = row('2026-11-04T17:42:00-05:00')
        for b in (a, a[:4] + [10] + a[5:]):
            with self.assertRaises(ValueError):
                inspect(payload(a, b))

    def test_invalid_observations_rejected(self):
        a = row('2026-11-04T17:42:00-05:00')
        for index, value in [(0, a[0] + 1), (1, True), (2, 8), (5, -1), (6, float('nan')), (7, 1.5)]:
            b = a.copy()
            b[index] = value
            with self.assertRaises(ValueError):
                inspect(payload(b))
        with self.assertRaises(ValueError):
            inspect(payload(a).rstrip())

    def test_hash_count_cutoff_identity_and_anomaly_tampering(self):
        info = inspect(payload(row('2026-11-04T17:42:00-05:00')), '2026-11-04')
        meta = dict(entity_id='CRWV', source='Massive', currency='USD', timezone='America/New_York',
                    timeframe='1m', adjusted=True, records=1, sha256=info['sha256'],
                    as_of_last_bar=info['coverage_end_exclusive'], session_date='2026-11-04', vwap_outside_ohlc=1)
        verify_meta(meta, info, '2026-11-04')
        for key, value in [('records', 2), ('sha256', 'wrong'), ('currency', 'JPY'),
                           ('as_of_last_bar', info['last_bar_start']), ('session_date', '2026-11-03'),
                           ('vwap_outside_ohlc', 0)]:
            with self.assertRaises(ValueError):
                verify_meta({**meta, key: value}, info, '2026-11-04')


if __name__ == '__main__':
    unittest.main()
