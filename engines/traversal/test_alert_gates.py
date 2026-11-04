"""Run: python -m unittest discover -s engines/traversal -p 'test_alert_gates.py' -v"""
import unittest
from engines.traversal.alert_gates import evaluate

NOW = "2026-10-16T18:21:00Z"
def quote(price, prior, ticker="x", **kw):
    return dict(price=price, previous_close=prior, observed_at=NOW,
                available_at=NOW, source_id=ticker, currency="USD",
                quote_status="delayed", **kw)

class AlertGateTests(unittest.TestCase):
    def test_daily_move_and_divergence(self):
        data = {"as_of": NOW, "observations": {
            "SFTBY": quote(15.07, 16.30, "sftby"),
            "ARM": quote(230.62, 244.79, "arm"),
            "PAYP": quote(15.56, 14.65, "payp")}}
        result = evaluate(data)
        self.assertEqual(result["status"], "review")
        self.assertIn("daily_move", [x["type"] for x in result["triggers"]])
        self.assertEqual([x["peer"] for x in result["triggers"]
                          if x["type"] == "relative_divergence"], ["PAYP"])

    def test_quiet(self):
        result = evaluate({"as_of": NOW, "observations": {
            "SFTBY": quote(100, 100, "s"), "ARM": quote(101, 100, "a")}})
        self.assertEqual(result["status"], "quiet")

    def test_stale_and_future_rejected(self):
        old = quote(90, 100, "s")
        old["observed_at"] = "2026-10-15T18:21:00Z"
        result = evaluate({"as_of": NOW, "observations": {"SFTBY": old}})
        self.assertIn("SFTBY", result["rejected"])
        future = quote(90, 100, "s")
        future["available_at"] = "2026-10-17T18:21:00Z"
        self.assertEqual(evaluate({"as_of": NOW, "observations": {"SFTBY": future}})["status"], "quiet")

    def test_no_tokyo_break_from_adr(self):
        result = evaluate({"as_of": NOW, "observations": {"SFTBY": quote(15.07, 16.30, "s")}})
        self.assertFalse(any(x["type"].startswith("tokyo_") for x in result["triggers"]))

    def test_tokyo_crossings(self):
        result = evaluate({"as_of": NOW, "observations": {},
            "tokyo_threshold": {"previous": 4990, "current": 5010,
                "observed_at": NOW, "available_at": NOW, "source_id": "tokyo"}})
        self.assertEqual(result["triggers"][0]["level_jpy"], 5000)
        self.assertEqual(result["triggers"][0]["type"], "tokyo_reclaim")

    def test_duplicate_inputs_deterministic(self):
        payload = {"as_of": NOW, "observations": {"SFTBY": quote(90, 100, "s")}}
        self.assertEqual(evaluate(payload), evaluate(payload))

    def test_missing_provenance_and_invalid_price(self):
        x = quote(90, 100, "s"); x.pop("source_id")
        y = quote(float("nan"), 100, "a")
        r = evaluate({"as_of": NOW, "observations": {"SFTBY": x, "ARM": y}})
        self.assertEqual(len(r["rejected"]), 2)
        self.assertEqual(r["status"], "quiet")

if __name__ == "__main__":
    unittest.main()
