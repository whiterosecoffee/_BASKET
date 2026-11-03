"""Offline deterministic tests for the B06 market geometry core."""
import unittest
from datetime import datetime, timedelta, timezone
from engines.traversal.market_geometry.core import compute_market_geometry, render_compact


AT = datetime(2026, 10, 30, 19, 0, tzinfo=timezone.utc)
ISO = lambda t: t.isoformat().replace("+00:00", "Z")


def bars(price, n=61):
    return [{"t": ISO(AT - timedelta(minutes=i)), "close": price - i * .01,
             "low": price - i * .01 - .005,
             "high": price - i * .01 + .005, "complete": True}
            for i in range(n, -1, -1)]


class MarketGeometryTests(unittest.TestCase):
    def test_synchronized_windows_and_ratios(self):
        s = {"SPY": bars(750), "QQQ": bars(690),
             "RSP": bars(215), "IWM": bars(270), "SMH": bars(520)}
        r = compute_market_geometry(s, ISO(AT), {"SPY": 760, "QQQ": 700})
        self.assertAlmostEqual(r["instruments"]["SPY"]["day_pct"], (750/760-1)*100, places=5)
        self.assertAlmostEqual(r["instruments"]["QQQ"]["returns_pct"]["5"], (690/689.95-1)*100, places=5)
        self.assertIsNotNone(r["relatives"]["SMH/QQQ"]["returns_pct"]["15"])
        self.assertEqual(r["macro_regime"], "unknown")
        self.assertIn("SPY", render_compact(r))

    def test_gap_is_null_not_lookahead(self):
        s = {"SPY": bars(750, 4)}
        r = compute_market_geometry(s, ISO(AT))
        self.assertIsNone(r["instruments"]["SPY"]["returns_pct"]["5"])
        self.assertIsNone(r["instruments"]["QQQ"])
        self.assertIn("SPY:missing_5m", r["gaps"])

    def test_unsynchronized_last_bar_not_used(self):
        s = {"SPY": bars(750, 10)}
        s["SPY"] = [b for b in s["SPY"] if b["t"] != ISO(AT)]
        r = compute_market_geometry(s, ISO(AT))
        self.assertIsNone(r["instruments"]["SPY"])

    def test_duplicate_future_and_invalid_prices(self):
        s = bars(750, 1)
        with self.assertRaises(ValueError):
            compute_market_geometry({"SPY": s + [s[-1]]}, ISO(AT))
        future = dict(s[-1], t=ISO(AT + timedelta(minutes=1)))
        with self.assertRaises(ValueError):
            compute_market_geometry({"SPY": s + [future]}, ISO(AT))
        bad = dict(s[-1], close=9999)
        with self.assertRaises(ValueError):
            compute_market_geometry({"SPY": s[:-1] + [bad]}, ISO(AT))

    def test_partial_bar_not_eligible(self):
        s = bars(750, 2)
        s[-1]["complete"] = False
        r = compute_market_geometry({"SPY": s}, ISO(AT))
        self.assertIsNone(r["instruments"]["SPY"])

    def test_not_fabricated_from_two_assets(self):
        r = compute_market_geometry({"SPY": bars(750), "QQQ": bars(690)}, ISO(AT))
        self.assertIsNone(r["relatives"]["SMH/QQQ"])
        self.assertIsNone(r["instruments"]["SMH"]["day_pct"] if r["instruments"]["SMH"] else None)


if __name__ == "__main__":
    unittest.main()
