import json
import unittest
from volume_guard import verify_volume_preservation, VolumeError

class VolumeGuardTests(unittest.TestCase):
    def data(self, volume='1.250000000000000000000000000001', t=1791468000000):
        return ('{"ticker":"TEST","t":%d,"class":"bar","grain":"1min","vol":%s}\n' % (t,volume)).encode()

    def check(self,a,b):
        return verify_volume_preservation(a,b,source_unit='shares',candidate_unit='shares')

    def test_high_precision_fraction_preserved(self):
        a=self.data(); before=a[:]
        r=self.check(a,a)
        self.assertEqual(r['fractional_volume_rows'],1)
        self.assertEqual(a,before)
        self.assertFalse(r['canonical_eligible'])
        self.assertFalse(r['units_verified'])
        self.assertEqual(r,self.check(a,a))

    def test_equivalent_numeric_strings_and_exponents(self):
        for a,b in [('1.25','"1.250"'),('1.25','125e-2'),('0','-0.0'),('2','"2.00"')]:
            with self.subTest(a=a,b=b):
                self.check(self.data(a),self.data(b))
                self.check(self.data(b),self.data(b))

    def test_rounding_detected(self):
        for candidate in ['1','1.25','1.250000000000000000000000000002']:
            with self.subTest(candidate=candidate):
                with self.assertRaisesRegex(VolumeError,'volume_changed'):
                    self.check(self.data(),self.data(candidate))

    def test_negative_nonfinite_missing_boolean_rejected(self):
        for bad in ['-1','NaN','Infinity','null','true','"NaN"','" 1.25 "']:
            with self.subTest(bad=bad):
                with self.assertRaises(VolumeError):self.check(self.data(bad),self.data(bad))

    def test_unbounded_precision_rejected(self):
        with self.assertRaisesRegex(VolumeError,'unsupported_volume_precision'):
            self.check(self.data('1e99999999'),self.data('1e99999999'))

    def test_duplicate_source_or_candidate_rejected(self):
        a=self.data()
        for source,candidate in [(a+a,a),(a,a+a)]:
            with self.assertRaisesRegex(VolumeError,'duplicate_identity'):self.check(source,candidate)

    def test_changed_identity_rejected(self):
        with self.assertRaisesRegex(VolumeError,'identity_set_mismatch'):
            self.check(self.data(),self.data(t=1791468060000))

    def test_units_fail_closed(self):
        with self.assertRaisesRegex(VolumeError,'unsupported_or_mismatched_units'):
            verify_volume_preservation(self.data(),self.data(),source_unit='shares',candidate_unit='lots')

    def test_duplicate_keys_rejected(self):
        a=self.data().replace(b'"vol":',b'"vol":0,"vol":')
        with self.assertRaisesRegex(VolumeError,'invalid_json'):self.check(a,a)

    def test_binary_float_input_rejected(self):
        with self.assertRaisesRegex(VolumeError,'invalid_jsonl_size_or_type'):self.check(1.25,1.25)

    def test_empty_or_wrong_grain_rejected(self):
        for a in [b'\n', self.data().replace(b'1min',b'1day'),b'[]']:
            with self.assertRaises(VolumeError):self.check(a,a)

    def test_reordering_preserves_identity_based_comparison(self):
        a,b=self.data(),self.data('2.5',1791468060000)
        r=self.check(a+b,b+a)
        self.assertEqual(r['rows'],2)
        self.assertNotEqual(r['source_sha256'],r['candidate_sha256'])

if __name__=='__main__': unittest.main()
