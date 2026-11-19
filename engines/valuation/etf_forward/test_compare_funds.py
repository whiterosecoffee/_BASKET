import copy
import unittest
from decimal import Decimal
from compare_funds import compare_funds

A = '2026-10-30T20:00:00Z'
T = '2026-10-29T20:00:00Z'

def holding(name, weight, income27, income28):
    return {'id':name,'asset_type':'equity','available_at':T,'weight':weight,
     'equity_currency':'USD','market_cap_usd':'100','estimates':{
      '2027':{'calendar_year':2027,'available_at':T,'currency':'USD','net_income_usd':income27},
      '2028':{'calendar_year':2028,'available_at':T,'currency':'USD','net_income_usd':income28}}}

def fixture():
    base={'as_of':A,'holdings_available_at':T,'holdings_effective_date':'2026-10-29',
          'equity_market_cap_as_of':T,'currency':'USD','source_class':'issuer_primary',
          'data_kind':'synthetic_test','source_manifest':[{'id':'toy-only'}]}
    return {'schema':'basket.etf_peer_comparison_input@1','as_of':A,
       'holdings_effective_date':'2026-10-29','equity_market_cap_as_of':T,
       'funds':[
        {**base,'ticker':'SMH','holdings':[holding('NVDA','0.6','10','12'),holding('AMD','0.4','5','8')]},
        {**base,'ticker':'SOXX','holdings':[holding('NVDA','0.3','10','12'),holding('AMD','0.7','5','8')]}
       ]}

class TestPeerComparison(unittest.TestCase):
    def test_dual_year_separate(self):
        x=compare_funds(fixture())['years']
        self.assertEqual(Decimal(x['2027']['earnings_yield']['SMH']),Decimal('0.080'))
        self.assertEqual(Decimal(x['2027']['earnings_yield']['SOXX']),Decimal('0.065'))
        self.assertEqual(Decimal(x['2028']['earnings_yield']['SMH']),Decimal('0.104'))
        self.assertEqual(Decimal(x['2028']['earnings_yield']['SOXX']),Decimal('0.092'))
    def test_spread_attribution(self):
        x=compare_funds(fixture())['years']['2027']
        self.assertEqual(Decimal(x['yield_spread_smh_minus_soxx']), Decimal('0.015'))
        self.assertEqual(sum(map(Decimal,x['yield_spread_contributions'].values())),Decimal('0.015'))
    def test_forward_multiple_not_preference(self):
        x=compare_funds(fixture())
        self.assertEqual(x['years']['2027']['lower_forward_multiple_indicator'],'SMH')
        self.assertIn('not a risk-adjusted preference',x['disclosure'])
    def test_future_estimate_rejected(self):
        x=fixture();x['funds'][0]['holdings'][0]['estimates']['2027']['available_at']='2026-11-01T00:00:00Z'
        with self.assertRaises(ValueError):compare_funds(x)
    def test_holdings_vintage_mismatch(self):
        x=fixture();x['funds'][0]['holdings_effective_date']='2026-10-28'
        with self.assertRaises(ValueError):compare_funds(x)
    def test_price_vintage_mismatch(self):
        x=fixture();x['funds'][0]['equity_market_cap_as_of']='2026-10-29T21:00:00Z'
        with self.assertRaises(ValueError):compare_funds(x)
    def test_mixed_kind_rejected(self):
        x=fixture();x['funds'][0]['data_kind']='verified_observation'
        with self.assertRaises(ValueError):compare_funds(x)
    def test_incomplete_year_suppresses_peer_winner(self):
        x=fixture();del x['funds'][1]['holdings'][1]['estimates']['2028']
        result=compare_funds(x)['years']
        self.assertEqual(result['2027']['status'],'mathematically_comparable')
        self.assertIsNone(result['2028']['lower_forward_multiple_indicator'])
        self.assertIsNone(result['2028']['yield_spread_contributions'])
    def test_wrong_currency_rejected(self):
        x=fixture();x['funds'][0]['currency']='JPY'
        with self.assertRaises(ValueError):compare_funds(x)
    def test_wrong_source_class_rejected(self):
        x=fixture();x['funds'][0]['source_class']='third_party'
        with self.assertRaises(ValueError):compare_funds(x)
    def test_duplicate_ticker_rejected(self):
        x=fixture();x['funds'][1]['ticker']='SMH'
        with self.assertRaises(ValueError):compare_funds(x)
    def test_digest_reproducible(self):
        self.assertEqual(compare_funds(fixture())['input_sha256'],compare_funds(copy.deepcopy(fixture()))['input_sha256'])

if __name__=='__main__': unittest.main()
