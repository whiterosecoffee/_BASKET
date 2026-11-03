import unittest
from holdings_audit import audit_holdings
T={"ticker":"QQQ","as_of":"2026-10-29","available_at":"2026-10-30T00:00:00Z","source_class":"issuer_primary","source_url":"https://www.invesco.com/qqq-etf/en/about.html","full_issuer_file":False,"holdings":[{"id":"NVDA","weight_pct":"8.08"},{"id":"AAPL","weight_pct":"7.99"}]}
class AuditTests(unittest.TestCase):
 def test_partial_blocked(self):
  x=audit_holdings(T,"2026-11-03T12:00:00Z")
  self.assertFalse(x["full_fund_valuation_eligible"])
  self.assertEqual(x["verified_weight_fraction"],"0.1607")
 def test_full_allowed(self):
  x={**T,"full_issuer_file":True,"holdings":[{"id":"ALL","weight_pct":"100"}]}
  self.assertTrue(audit_holdings(x,"2026-11-03T12:00:00Z")["full_fund_valuation_eligible"])
 def test_future_blocked(self):
  with self.assertRaises(ValueError): audit_holdings(T,"2026-10-29T12:00:00Z")
 def test_duplicates_blocked(self):
  x={**T,"holdings":T["holdings"]*2}
  with self.assertRaises(ValueError):audit_holdings(x,"2026-11-03T12:00:00Z")
 def test_overweight_blocked(self):
  x={**T,"holdings":[{"id":"a","weight_pct":"101"}]}
  with self.assertRaises(ValueError):audit_holdings(x,"2026-11-03T12:00:00Z")
if __name__=="__main__":unittest.main()
