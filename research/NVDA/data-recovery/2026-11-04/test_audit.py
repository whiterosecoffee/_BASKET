"""Synthetic boundary fixtures only; no licensed market observations."""
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import audit


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def rows(self, day='2026-11-02'):
        start = datetime.fromisoformat(day + 'T09:30:00').replace(tzinfo=ZoneInfo('America/New_York'))
        rows = []
        for i in range(390):
            t = start + timedelta(minutes=i)
            rows.append({'entity_id': 'NVDA', 'kind': 'market_bar', 'currency': 'USD',
                         'source': 'Massive', 'observed_at': t.isoformat(),
                         'available_at': '2026-11-04T23:00:00Z', 'ingested_at': '2026-11-04T23:00:00Z',
                         'source_record_id': f'NVDA:1m:{int(t.timestamp()*1000)}:unadjusted',
                         'ttd_seconds': 0, 'value': {'interval': '1m', 'adjustment_basis': 'unadjusted',
                         'open': 100, 'high': 101, 'low': 99, 'close': 100, 'volume': 10,
                         'vwap': 100, 'transactions': 2}})
        return rows

    def write(self, rows, day='2026-11-02'):
        for r in rows:
            r['record_id'] = hashlib.sha256(audit.canonical({k:v for k,v in r.items() if k != 'record_id'})).hexdigest()
        raw = b''.join(audit.canonical(r) + b'\n' for r in rows)
        p = self.root / (day + '.1m.jsonl')
        p.write_bytes(raw)
        manifest = {'partition_timezone': 'America/New_York', 'days': [{
            'date_et': day, 'file': p.name, 'sha256': hashlib.sha256(raw).hexdigest(),
            'records': len(rows), 'regular_minutes': 390,
            'vwap_flags': sum(not r['value']['low'] <= r['value']['vwap'] <= r['value']['high'] for r in rows)}]}
        (self.root / 'manifest.json').write_text(json.dumps(manifest))
        return p

    def rejected(self, rows, code):
        self.write(rows)
        result = audit.audit(self.root)
        self.assertEqual(result['status'], 'rejected')
        self.assertIn(code, str(result['errors']))

    def test_valid_readonly_deterministic(self):
        p = self.write(self.rows())
        before = p.read_bytes()
        self.assertEqual(audit.audit(self.root)['status'], 'qualified')
        self.assertEqual(audit.audit(self.root), audit.audit(self.root))
        self.assertEqual(p.read_bytes(), before)

    def test_missing_minute(self):
        self.rejected(self.rows()[1:], 'regular_minute_coverage_mismatch')

    def test_duplicate_source_key(self):
        r = self.rows(); r.append(copy.deepcopy(r[-1]))
        self.rejected(r, 'duplicate_record_or_source_key')

    def test_bad_ohlc(self):
        r = self.rows(); r[0]['value']['low'] = 102
        self.rejected(r, 'invalid_ohlc')

    def test_negative_volume(self):
        r = self.rows(); r[0]['value']['volume'] = -1
        self.rejected(r, 'invalid_volume_count_or_vwap')

    def test_boolean_volume(self):
        r = self.rows(); r[0]['value']['volume'] = True
        self.rejected(r, 'nonfinite_or_nonnumeric_bar')

    def test_vwap_flag_preserved(self):
        r = self.rows(); r[0]['value']['vwap'] = 102
        p = self.write(r); before = p.read_bytes()
        result = audit.audit(self.root)
        self.assertEqual(result['status'], 'qualified_with_warnings')
        self.assertEqual(result['days'][0]['vwap_flags'], 1)
        self.assertEqual(before, p.read_bytes())

    def test_file_hash(self):
        p = self.write(self.rows());p.write_bytes(p.read_bytes().replace(b'"close":100', b'"close":101', 1))
        self.assertIn('file_hash_mismatch', str(audit.audit(self.root)['errors']))

    def test_record_hash_even_if_manifest_updated(self):
        p = self.write(self.rows());p.write_bytes(p.read_bytes().replace(b'"close":100', b'"close":101', 1))
        m = json.loads((self.root/'manifest.json').read_text());m['days'][0]['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
        (self.root/'manifest.json').write_text(json.dumps(m))
        self.assertIn('record_hash_mismatch', str(audit.audit(self.root)['errors']))

    def test_wrong_date(self):
        self.rejected(self.rows('2026-11-03'), 'mixed_session_date')

    def test_pre_and_post_dst(self):
        for day in ('2026-10-30', '2026-11-02'):
            for p in self.root.glob('*.jsonl'):
                p.unlink()
            self.write(self.rows(day), day)
            self.assertEqual(audit.audit(self.root)['status'], 'qualified')

    def test_afterhours_utc_midnight_stays_prior_et_day(self):
        r = self.rows();x = copy.deepcopy(r[-1]);x['observed_at'] = '2026-11-03T00:59:00Z'
        t = audit.timestamp(x['observed_at']);x['source_record_id'] = f'NVDA:1m:{int(t.timestamp()*1000)}:unadjusted'
        r.append(x);self.write(r)
        self.assertEqual(audit.audit(self.root)['status'], 'qualified')

    def test_future_availability(self):
        r = self.rows();r[0]['available_at'] = '2026-11-05T00:00:00Z'
        self.rejected(r, 'invalid_temporal_order')

    def test_adjustment_basis_mismatch(self):
        r = self.rows();r[0]['value']['adjustment_basis'] = 'split_adjusted'
        self.rejected(r, 'identity_or_basis_mismatch')

    def test_duplicate_json_properties(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON property'):
            audit.strict_json('{"x":1,"x":2}')

    def test_nonfinite_json(self):
        with self.assertRaises(ValueError):
            audit.strict_json('{"x":NaN}')

    def test_missing_partition(self):
        p = self.write(self.rows());p.unlink()
        self.assertEqual(audit.audit(self.root)['status'], 'rejected')

    def test_manifest_duplicate_day(self):
        self.write(self.rows());p=self.root/'manifest.json';m=json.loads(p.read_text());m['days']*=2;p.write_text(json.dumps(m))
        self.assertIn('duplicate manifest', str(audit.audit(self.root)['errors']))

    def test_partial_last_line(self):
        p = self.write(self.rows());p.write_bytes(p.read_bytes().rstrip(b'\n'))
        self.assertIn('truncated', str(audit.audit(self.root)['errors']))

    def test_unlisted_partition(self):
        self.write(self.rows());(self.root/'unexpected.jsonl').write_text('{}\n')
        self.assertIn('unlisted_partitions', str(audit.audit(self.root)['errors']))

    def test_unaligned_minute(self):
        r=self.rows();r[0]['observed_at']=r[0]['observed_at'].replace('09:30:00','09:30:01')
        self.rejected(r,'unordered_or_unaligned_minute')


class QuantityTests(unittest.TestCase):
    def pair(self):
        a={'metric':'adjusted_eps','unit':'USD/share','scale':'per_share','instrument':'NVDA',
           'provider':'synthetic','method':'consensus','scope':'FY2028','period_end':'2028-01-30',
           'basis':'adjusted_sbc_included','window_start':'not_applicable','window_end':'not_applicable',
           'source_ref':'synthetic_a','value':10,'as_of':'2026-11-01T00:00:00Z',
           'available_at':'2026-11-01T00:00:00Z'}
        b=dict(a,value=11,as_of='2026-11-02T00:00:00Z',available_at='2026-11-02T00:00:00Z',source_ref='synthetic_b')
        return a,b

    def test_same_period_revision(self):
        r=audit.compare(*self.pair());self.assertEqual(r['change'],1);self.assertAlmostEqual(r['relative_change'],.1)

    def test_gamma_not_hiro_premium_or_oi(self):
        for metric in ('hiro_delta_flow','premium_flow','open_interest'):
            a,b=self.pair();a['metric']='net_gex';b['metric']=metric
            self.assertEqual(audit.compare(a,b)['status'],'incompatible')

    def test_units_scale_scope_basis_provider_window(self):
        for field in ('unit','scale','scope','basis','provider','window_start','window_end','method','instrument','period_end'):
            a,b=self.pair();b[field]='different'
            self.assertIn('mismatch_'+field,audit.compare(a,b)['reasons'])

    def test_missing_units_rejected(self):
        a,b=self.pair();del b['scale'];self.assertEqual(audit.compare(a,b)['status'],'incompatible')

    def test_unknown_scale_rejected(self):
        a,b=self.pair();a['scale']=b['scale']='unknown'
        self.assertIn('unknown_scale',audit.compare(a,b)['reasons'])

    def test_lookahead_rejected(self):
        a,b=self.pair();b['available_at']='2026-11-03T00:00:00Z'
        self.assertIn('lookahead',audit.compare(a,b)['reasons'])

    def test_reversed_asof(self):
        a,b=self.pair();self.assertIn('reversed_asof',audit.compare(b,a)['reasons'])

    def test_no_invented_probability_or_neutrality(self):
        r=audit.compare(*self.pair());self.assertIsNone(r['probability']);self.assertEqual(r['dealer_neutrality'],'not_inferred')

    def test_zero_baseline(self):
        a,b=self.pair();a['value']=0;self.assertIsNone(audit.compare(a,b)['relative_change'])


if __name__ == '__main__':
    unittest.main()
