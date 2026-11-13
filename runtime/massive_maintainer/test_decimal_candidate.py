import base64
import copy
import unittest
from unittest.mock import patch
from runtime.massive_maintainer import decimal_candidate as c


class DecimalCandidateTests(unittest.TestCase):
    def setUp(self):
        self.raw = (b'{"ticker":"NVDA","t":1790841600000,"grain":"1min",'
                    b'"o":1.000000000000000001,"h":2,"l":1,"c":1,'
                    b'"vol":112276.024927,"vw":1.1000,"n":3}\n')
        self.basis = {'volume_unit':'shares','adjustment':'split_adjusted',
                      'adjustment_as_of':'2026-10-09','timezone':'America/New_York',
                      'grain':'1m','evidence_status':'source_bound',
                      'evidence_sha256':'a'*64}

    def item(self, raw=None, vintage='fixture-a', basis=None):
        raw = self.raw if raw is None else raw
        return {'data':raw,'sha256':c.sha(raw),'vintage':vintage,
                'basis':self.basis if basis is None else basis}

    def test_exact_decimal_and_raw_bytes(self):
        result=c.build_candidate([self.item()]); r=result['records'][0]
        self.assertEqual(r['values']['vol'],'112276.024927')
        self.assertEqual(r['values']['o'],'1.000000000000000001')
        self.assertEqual(r['values']['vw'],'1.1000')
        self.assertEqual(base64.b64decode(r['raw_base64']),self.raw)
        self.assertFalse(result['promotable'])
        self.assertEqual(result['qualification'],'unqualified_candidate')
        self.assertEqual(r['session']['exchange_date'],'2026-10-01')
        self.assertEqual(r['session']['window'],'pre_0930')

    def test_replay_permutation_and_nonmutation(self):
        a=self.item(); b=self.item(vintage='fixture-b'); before=copy.deepcopy([a,b])
        expected=c.encode(c.build_candidate([a,b]))
        self.assertEqual(expected,c.encode(c.build_candidate([b,a,a])))
        self.assertEqual([a,b],before)
        self.assertEqual(c.build_candidate([a,b])['groups'][0]['state'],'identical_duplicate')
        self.assertEqual(len(c.build_candidate([a,b])['records']),2)

    def test_conflicts_preserve_both_vintages(self):
        changed=self.raw.replace(b'112276.024927',b'112276.024928')
        result=c.build_candidate([self.item(),self.item(changed,'fixture-b')])
        self.assertEqual(result['groups'][0]['state'],'conflicting_vintages')
        self.assertIsNone(result['groups'][0]['selected_vintage'])
        self.assertEqual(len(result['records']),2)
        self.assertTrue(all(r['disposition']=='quarantine' for r in result['records']))
        self.assertEqual({r['values']['vol'] for r in result['records']},
                         {'112276.024927','112276.024928'})

    def test_unknown_and_incompatible_basis_quarantine(self):
        result=c.build_candidate([self.item(basis={})])
        self.assertIn('unknown_or_unsupported_basis',result['records'][0]['reasons'])
        other=dict(self.basis,adjustment='unadjusted')
        result=c.build_candidate([self.item(),self.item(vintage='b',basis=other)])
        self.assertEqual(result['groups'][0]['state'],'incompatible_or_unreconciled_basis')
        self.assertTrue(all(r['disposition']=='quarantine' for r in result['records']))

    def test_input_hash_rejected(self):
        item=self.item();item['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'input checksum mismatch'):
            c.build_candidate([item])

    def test_invalid_rows_retained_without_invention(self):
        for raw in (b'not-json\n',self.raw.replace(b'112276.024927',b'NaN'),
                    self.raw.replace(b'112276.024927',b'true'),
                    self.raw.replace(b'1min',b'1day'),
                    self.raw.replace(b'1790841600000',b'1790841600001')):
            with self.subTest(raw=raw):
                result=c.build_candidate([self.item(raw)])
                self.assertIn('invalid_record',result['records'][0]['reasons'])
                self.assertEqual(base64.b64decode(result['records'][0]['raw_base64']),raw)

    def test_no_io(self):
        with patch('builtins.open',side_effect=AssertionError('filesystem access')):
            with patch('urllib.request.urlopen',side_effect=AssertionError('network access')):
                result=c.build_candidate([self.item()])
        self.assertEqual(len(result['records']),1)


if __name__=='__main__': unittest.main()
