import unittest
from virtual_etf_policy import allocate, COMPONENT_WEIGHTS

SCORES = dict.fromkeys(COMPONENT_WEIGHTS, 0.8)

def row(ticker,segment='agents',available='2026-11-01T00:00:00Z',exp='2026-11-30T00:00:00Z'):
    return dict(ticker=ticker,segment=segment,observed_at='2026-10-31T00:00:00Z',
                available_at=available,expires_at=exp,price_usd=30,eligible=True,scores=SCORES.copy())

class PolicyTest(unittest.TestCase):
    def setUp(self):
        self.base={'cutoff':'2026-11-03T14:00:00Z'}

    def test_empty_all_cash(self):
        x=allocate(dict(self.base,rows=[]))
        self.assertEqual(x['cash_weight'],1)

    def test_cap_and_cash(self):
        x=allocate(dict(self.base,rows=[row('A'),row('B'),row('C','eng')]))
        self.assertAlmostEqual(sum(r['weight'] for r in x['weights'])+x['cash_weight'],1,8)
        self.assertTrue(all(r['weight']<=.15000001 for r in x['weights']))
        self.assertAlmostEqual(x['cash_weight'],.55)

    def test_segment_limits(self):
        rows=[row(str(i), 'agents' if i<5 else 'eng') for i in range(10)]
        x=allocate(dict(self.base,rows=rows))
        self.assertLessEqual(sum(r['weight'] for r in x['weights'] if r['segment']=='agents'),.35000001)
        self.assertAlmostEqual(x['cash_weight'],.30)

    def test_future_information_rejected(self):
        x=allocate(dict(self.base,rows=[row('A',available='2026-11-04T00:00:00Z')]))
        self.assertEqual(x['rejected'][0]['reason'],'not_point_in_time_valid')

    def test_expired_rejected(self):
        x=allocate(dict(self.base,rows=[row('A',exp='2026-11-02T00:00:00Z')]))
        self.assertEqual(x['cash_weight'],1)

    def test_missing_and_nonfinite(self):
        a=row('A'); a['scores']['forward_return']=float('nan')
        x=allocate(dict(self.base,rows=[a]))
        self.assertEqual(x['cash_weight'],1)

    def test_duplicate_fails(self):
        with self.assertRaises(ValueError):
            allocate(dict(self.base,rows=[row('A'),row('A')]))

    def test_deterministic_order(self):
        rows=[row(str(i),str(i%3)) for i in range(9)]
        x=allocate(dict(self.base,rows=rows));y=allocate(dict(self.base,rows=list(reversed(rows))))
        self.assertEqual(x,y)

if __name__=='__main__': unittest.main()
