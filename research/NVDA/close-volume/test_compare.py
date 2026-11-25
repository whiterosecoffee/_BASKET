import unittest
from compare import decompose

class ComparisonExamples(unittest.TestCase):
    def pair(self):
        b = dict(metric='synthetic_gamma', unit='synthetic_units', settings_id='fixed',
                 source_ref='synthetic:before', universe_id='with_expiry',
                 observed_at='2026-01-02T20:00:00+00:00', value=-100)
        a = dict(b, source_ref='synthetic:after', universe_id='without_expiry',
                 observed_at='2026-01-02T21:00:00+00:00', value=15)
        return b, a

    def test_decomposition_and_replay(self):
        b, a = self.pair()
        result = decompose(b, a, -110)
        self.assertEqual(result['counterfactual_remaining'], '10')
        self.assertEqual(result['unattributed_residual'], '5')
        self.assertEqual(result['new_positioning'], 'not_determined')
        self.assertEqual(result, decompose(b, a, -110))
        self.assertEqual(b['value'], -100)

    def test_invalid_inputs(self):
        for key, value in [('metric','delta'), ('unit','contracts'),
                           ('settings_id','changed'), ('observed_at','2026-01-02'),
                           ('observed_at','2026-01-01T00:00:00+00:00'),
                           ('source_ref',''), ('universe_id',''), ('value','NaN')]:
            with self.subTest(key=key, value=value):
                b, a = self.pair()
                a[key] = value
                with self.assertRaises(ValueError):
                    decompose(b, a, -110)

    def test_positive_expiry_and_zero_residual(self):
        b, a = self.pair()
        b['value'], a['value'] = 40, 10
        result = decompose(b, a, 30)
        self.assertEqual(result['unattributed_residual'], '0')
        self.assertEqual(result['new_positioning'], 'not_determined')

if __name__ == '__main__':
    unittest.main()
