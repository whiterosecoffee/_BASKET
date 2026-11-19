"""Offline contract checks; mocked existing core only, not source-to-journal acceptance."""
import sys
import types
import unittest
from unittest.mock import patch
from .tool import REQUEST, digest, run


def fixture(symbol="CRWV", count=15):
    bars = [dict(t=i*60000, o=100+i, h=101+i, l=100+i,
                 c=101+i, v=100, vw=100.5+i) for i in range(count)]
    source = dict(provider="synthetic_fixture", source_id="offline:v1",
                  currency="USD", adjustment_basis="none", session="regular",
                  interval_minutes=1, quality="verified", completeness="complete",
                  calendar_verified=True, entitlement="realtime",
                  available_at_ms=count*60000, received_at_ms=count*60000,
                  ttd_ms=120000, sha256=digest(bars))
    return dict(schema=REQUEST, instrument=symbol, observations=bars,
                as_of_ms=count*60000, source=source)


class ToolContractTests(unittest.TestCase):
    def test_digest_rejects_edited_observations(self):
        r = fixture()
        r["observations"][0]["c"] += .1
        with self.assertRaisesRegex(ValueError, "SHA256"):
            run(r)

    def test_current_always_requires_independent_attestation(self):
        r = fixture()
        out = run(r, "current")
        self.assertEqual(out["status"], "blocked_current")
        self.assertIn("independent_resolver_attestation_missing", out["reasons"])
        self.assertIsNone(out["metrics"])
        self.assertEqual(out["alerts_emitted"], 0)

    def test_negative_gate_cases(self):
        for name, value in (
            ("entitlement", "historical"), ("quality", "unknown"),
            ("calendar_verified", False), ("ttd_ms", None),
            ("available_at_ms", None), ("completeness", "partial")
        ):
            with self.subTest(field=name):
                r = fixture()
                r["source"][name] = value
                self.assertEqual(run(r, "current")["status"], "blocked_current")

    def test_gap_is_not_filled(self):
        r = fixture()
        r["observations"][-1]["t"] += 60000
        r["as_of_ms"] += 60000
        r["source"]["received_at_ms"] += 60000
        r["source"]["sha256"] = digest(r["observations"])
        out = run(r, "current")
        self.assertIn("continuity_unverified_or_gapped", out["reasons"])

    def test_future_information_and_partial_bar_rejected(self):
        r = fixture()
        r["source"]["available_at_ms"] += 1
        with self.assertRaisesRegex(ValueError, "later than"):
            run(r)
        r = fixture()
        r["as_of_ms"] -= 1
        r["source"]["available_at_ms"] -= 1
        r["source"]["received_at_ms"] -= 1
        with self.assertRaisesRegex(ValueError, "incomplete"):
            run(r)

    def test_historical_uses_existing_metrics_core_for_both_tickers(self):
        stub = types.ModuleType("engines.traversal.metrics")
        stub.evaluate = lambda instrument, observations, **kw: {
            "instrument": instrument, "count": len(observations),
            "interval": kw["interval_minutes"]
        }
        with patch.dict(sys.modules, {"engines.traversal.metrics": stub}):
            x = run(fixture("CRWV"))
            y = run(fixture("ORCL"))
        self.assertEqual(x["metrics"]["instrument"], "CRWV")
        self.assertEqual(y["metrics"]["instrument"], "ORCL")
        self.assertEqual(x["metrics"]["count"], 15)
        self.assertEqual(x["alerts_emitted"], 0)

    def test_unsupported_currency_and_duplicate_rejected(self):
        r = fixture()
        r["source"]["currency"] = "EUR"
        with self.assertRaisesRegex(ValueError, "FX"):
            run(r)
        r = fixture()
        r["observations"][-1]["t"] = r["observations"][-2]["t"]
        r["source"]["sha256"] = digest(r["observations"])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            run(r)


if __name__ == "__main__":
    unittest.main()
