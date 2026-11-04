import unittest
from decimal import Decimal
from return_bridge import bridge

class TestReturnBridge(unittest.TestCase):
 def test_attribution_reconciles(self):
  r=bridge('0.5','0.6','2')
  self.assertEqual(Decimal(r['gross_price_return']),Decimal('-0.10'))
  self.assertEqual(sum(Decimal(r[x]) for x in ('earnings_component','multiple_component','interaction')),Decimal(r['gross_price_return']))
 def test_separate_2027_2028_fee_periods(self):
  x=bridge('0','1','1',annual_expense_rate='0.01')
  y=bridge('0','1','2',annual_expense_rate='0.01')
  self.assertEqual(Decimal(x['net_conditional_price_return']),Decimal('-0.01'))
  self.assertEqual(Decimal(y['net_conditional_price_return']),Decimal('-0.0199'))
 def test_one_time_transaction_cost(self):
  x=bridge('0','1','2',round_trip_cost='0.02')
  self.assertEqual(Decimal(x['net_conditional_price_return']),Decimal('-0.02'))
 def test_observed_etf_prices_deny_double_fee(self):
  with self.assertRaises(ValueError):bridge('0','1','2',return_basis='observed_etf_nav')
 def test_multiple_must_be_positive(self):
  with self.assertRaises(ValueError):bridge('0','0','1')
 def test_no_negative_price_factor(self):
  with self.assertRaises(ValueError):bridge('-1.2','1','1')
 def test_invalid_annual_fee_rejected(self):
  with self.assertRaises(ValueError):bridge('0','1','1',annual_expense_rate='1')
 def test_nonpositive_horizon_rejected(self):
  with self.assertRaises(ValueError):bridge('0','1','0')
 def test_nonfinite_rejected(self):
  with self.assertRaises(ValueError):bridge('nan','1','1')
 def test_no_false_total_return(self):
  self.assertNotIn('total_return',bridge('0.3','0.8','2'))
if __name__=='__main__':unittest.main()
