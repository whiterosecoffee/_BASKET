import copy
import unittest
from core import analyze, timestamp, markdown

SAMPLE = {
 "as_of":"2026-11-04T17:30:00-05:00",
 "session":{"status":"completed","date":"2026-11-04","calendar_id":"XNYS","rth_end_at":"2026-11-04T16:00:00-05:00"},
 "instruments":[{"ticker":"QQQ","rth":{"session":"RTH","source":"synthetic-fixture","currency":"USD",
  "observed_at":"2026-11-04T16:00:00-05:00","available_at":"2026-11-04T16:00:05-05:00",
  "ingested_at":"2026-11-04T16:00:10-05:00","expires_at":"2026-11-04T18:00:00-05:00",
  "close_usd":100,"previous_close_usd":98},
 "ah":{"session":"AH","kind":"trade","source":"synthetic-fixture","currency":"USD",
  "observed_at":"2026-11-04T17:00:00-05:00","available_at":"2026-11-04T17:00:03-05:00",
  "ingested_at":"2026-11-04T17:00:05-05:00","expires_at":"2026-11-04T17:45:00-05:00",
  "price_usd":99.5},
 "levels":[{"kind":"observed","lower_usd":95,"upper_usd":96,"evidence_ids":[]}]}],
 "events":[{"name":"fixture","scheduled_at":"2026-11-04T08:30:00-05:00","actual":3.1,"consensus":3.0,
  "units":"pct","consensus_available_at":"2026-11-03T10:00:00-05:00",
  "actual_available_at":"2026-11-04T08:30:00-05:00"}],
 "scenarios":[{"name":"continuation","trigger":"break","invalidation":"reclaim"}]
}

class CoreTests(unittest.TestCase):
 def test_event_values_reject_coercion(self):
  for field in ("actual", "consensus"):
   for value in (True, False, "3.1"):
    with self.subTest(field=field, value=value):
     b=copy.deepcopy(SAMPLE); b["events"][0][field]=value
     with self.assertRaises(ValueError): analyze(b)
 def test_event_difference_overflow_rejected(self):
  b=copy.deepcopy(SAMPLE)
  b["events"][0].update(actual=1e308, consensus=-1e308)
  with self.assertRaises(ValueError): analyze(b)
 def test_event_large_integer_rejected_cleanly(self):
  b=copy.deepcopy(SAMPLE); b["events"][0]["actual"]=10**400
  with self.assertRaises(ValueError): analyze(b)
 def test_event_zero_and_negative_values_retained(self):
  b=copy.deepcopy(SAMPLE); b["events"][0].update(actual=0, consensus=-1)
  self.assertEqual(analyze(b)["events"][0]["surprise"], 1.0)
 def test_determinism(self):
  a=analyze(SAMPLE); self.assertEqual(a,analyze(copy.deepcopy(SAMPLE)))
  self.assertAlmostEqual(a["instruments"][0]["rth_return_pct"],2.0408)
  self.assertEqual(a["events"][0]["surprise"],0.1)
  self.assertIn("AH-MRI",markdown(a))
  self.assertFalse(a["readiness"]["production_ready"])
  self.assertIn("Validation readiness", markdown(a))
  self.assertIsNone(a["scenarios"][0]["probability"])
 def test_unproven_observed_level_downgraded(self):
  self.assertEqual(analyze(SAMPLE)["instruments"][0]["levels"][0]["kind"],"reference")
 def test_no_quote_as_trade(self):
  b=copy.deepcopy(SAMPLE); b["instruments"][0]["ah"]["kind"]="quote"
  self.assertIsNone(analyze(b)["instruments"][0]["ah_mark_usd"])
 def test_expired_ah(self):
  b=copy.deepcopy(SAMPLE); b["instruments"][0]["ah"]["expires_at"]="2026-11-04T17:10:00-05:00"
  self.assertIsNone(analyze(b)["instruments"][0]["ah_mark_usd"])
 def test_future_ingestion(self):
  b=copy.deepcopy(SAMPLE); b["instruments"][0]["rth"]["ingested_at"]="2026-11-05T00:00:00-05:00"
  self.assertIsNone(analyze(b)["instruments"][0]["rth_close_usd"])
 def test_missing_provider(self):
  b=copy.deepcopy(SAMPLE); b["instruments"][0]["rth"].pop("source")
  self.assertIsNone(analyze(b)["instruments"][0]["rth_close_usd"])
 def test_late_consensus(self):
  b=copy.deepcopy(SAMPLE); b["events"][0]["consensus_available_at"]="2026-11-04T09:00:00-05:00"
  self.assertIsNone(analyze(b)["events"][0]["surprise"])
 def test_timezone(self):
  with self.assertRaises(ValueError): timestamp("2026-11-04T16:00:00")
 def test_incomplete_session(self):
  b=copy.deepcopy(SAMPLE); b["session"]["status"]="open"
  with self.assertRaises(ValueError): analyze(b)
 def test_duplicate(self):
  b=copy.deepcopy(SAMPLE); b["instruments"].append(copy.deepcopy(b["instruments"][0]))
  with self.assertRaises(ValueError): analyze(b)
 def test_reversed_level(self):
  b=copy.deepcopy(SAMPLE); b["instruments"][0]["levels"][0]["lower_usd"]=97
  with self.assertRaises(ValueError): analyze(b)
 def test_future_AH_trade(self):
  b=copy.deepcopy(SAMPLE); b["as_of"]="2026-11-04T16:30:00-05:00"
  self.assertIsNone(analyze(b)["instruments"][0]["ah_mark_usd"])

 def test_intraday_not_close(self):
  b=copy.deepcopy(SAMPLE); b["instruments"][0]["rth"]["observed_at"]="2026-11-04T15:59:00-05:00"
  self.assertIsNone(analyze(b)["instruments"][0]["rth_close_usd"])
 def test_ah_outside_session(self):
  b=copy.deepcopy(SAMPLE)
  b["instruments"][0]["ah"]["observed_at"]="2026-11-04T20:01:00-05:00"
  b["instruments"][0]["ah"]["available_at"]="2026-11-04T20:02:00-05:00"
  b["instruments"][0]["ah"]["ingested_at"]="2026-11-04T20:03:00-05:00"
  b["as_of"]="2026-11-04T20:15:00-05:00"
  b["instruments"][0]["ah"]["expires_at"]="2026-11-04T20:30:00-05:00"
  self.assertIsNone(analyze(b)["instruments"][0]["ah_mark_usd"])
 def test_wrong_session_date(self):
  b=copy.deepcopy(SAMPLE); b["session"]["date"]="2026-11-03"
  with self.assertRaises(ValueError): analyze(b)
 def test_early_close_ah_end(self):
  b=copy.deepcopy(SAMPLE); b["session"]["ah_end_at"]="2026-11-04T16:30:00-05:00"
  self.assertIsNone(analyze(b)["instruments"][0]["ah_mark_usd"])

 def test_self_claimed_observed_never_certified(self):
  b=copy.deepcopy(SAMPLE)
  z=b["instruments"][0]["levels"][0]
  z.update({"evidence_ids":["untrusted-id"],"calculation":"claimed volume-density",
            "sample_window":"2026-11-01/2026-11-04"})
  out=analyze(b)
  self.assertEqual(out["instruments"][0]["levels"][0]["kind"],"reference")
  self.assertTrue(any("independent" in x for x in out["unknowns"]))
 def test_expiry_before_ingestion_invalid(self):
  b=copy.deepcopy(SAMPLE)
  b["instruments"][0]["ah"]["expires_at"]="2026-11-04T17:00:04-05:00"
  self.assertIsNone(analyze(b)["instruments"][0]["ah_mark_usd"])
 def test_mismatched_surprise_units(self):
  b=copy.deepcopy(SAMPLE)
  b["events"][0]["actual_units"]="pct"
  b["events"][0]["consensus_units"]="basis_points"
  self.assertIsNone(analyze(b)["events"][0]["surprise"])
 def test_consensus_after_as_of(self):
  b=copy.deepcopy(SAMPLE)
  b["as_of"]="2026-11-04T08:40:00-05:00"
  b["session"]["rth_end_at"]="2026-11-03T16:00:00-05:00"
  b["session"]["date"]="2026-11-03"
  b["events"][0]["consensus_available_at"]="2026-11-04T09:00:00-05:00"
  self.assertIsNone(analyze(b)["events"][0]["surprise"])

if __name__=="__main__": unittest.main()

