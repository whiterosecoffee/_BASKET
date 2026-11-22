import tempfile
import unittest
from datetime import date
from pathlib import Path

from engines.valuation.rotation import cli, store
from engines.valuation.rotation.calendarize import calendarize, extend, ntm
from engines.valuation.rotation.metrics import View, add_growth_adjusted_residuals, build_view, ratio_stats
from engines.valuation.rotation.tape import tape_stats
from engines.valuation.rotation.rotation import Params, decide

ASOF = date(2026, 7, 1)


def est(t, vals, fye=12, as_of="2026-06-15", kind="consensus"):
    return {(t, "eps"): {y: store.Est(t, "eps", y, v, "non_gaap", kind, "test", date.fromisoformat(as_of), fye)
                         for y, v in vals.items()}}


def snap(price=100.0):
    return {"price": price, "market_cap": 1e9, "enterprise_value": 1e9, "asof": ASOF, "earnings_per_share": "4"}


class T(unittest.TestCase):
    def test_calendarize_jan_fye(self):
        cy = calendarize({2026: 12.0, 2027: 24.0}, 1)
        self.assertAlmostEqual(cy[2026], 12 / 12 + 24 * 11 / 12)

    def test_calendarize_dec_identity(self):
        self.assertEqual(calendarize({2026: 5.0}, 12), {2026: 5.0})

    def test_extend_fades_growth_and_marks(self):
        v, e = extend({2026: 10.0, 2027: 20.0}, 2029)
        self.assertEqual(e, {2028, 2029})
        self.assertAlmostEqual(v[2028], 20 * (1 + 0.4))  # g capped 0.5 -> *0.8 = 0.4

    def test_ntm_blend(self):
        self.assertAlmostEqual(ntm({2026: 10, 2027: 20}, 2026, 0.5), 15)

    def test_point_in_time_excludes_future_and_prefers_kind(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "e.csv"
            p.write_text("ticker,metric,fiscal_year,value,basis,kind,source,as_of,fye_month\n"
                         "AAA,eps,2027,5,non_gaap,guidance,x,2026-06-01,12\n"
                         "AAA,eps,2027,6,non_gaap,consensus,x,2026-06-01,12\n"
                         "AAA,eps,2027,9,non_gaap,consensus,x,2026-09-01,12\n")
            self.assertEqual(store.load_estimates(p, ASOF)[("AAA", "eps")][2027].value, 6.0)

    def test_stale_and_missing_flags(self):
        v = build_view("AAA", snap(), est("AAA", {2026: 4, 2027: 5}, as_of="2025-01-01"), ASOF)
        self.assertIn("STALE_ESTIMATES", v.flags)
        self.assertFalse(v.usable)
        self.assertIn("NO_ESTIMATES", build_view("ZZZ", snap(), {}, ASOF).flags)

    def test_pe_and_cagr(self):
        v = build_view("AAA", snap(100), est("AAA", {2026: 4, 2027: 5, 2028: 6, 2029: 7, 2030: 8}), ASOF)
        self.assertAlmostEqual(v.pe(2026), 25.0)
        self.assertAlmostEqual(v.cagr, 2 ** 0.25 - 1)
        self.assertEqual(v.extrapolated, set())

    def test_residuals_need_four(self):
        vs = []
        for i, (pe, g) in enumerate([(20, 10), (30, 20), (40, 30), (50, 40)]):
            v = View(f"T{i}", pe, ASOF, ASOF, eps={2026: 1.0, 2030: (1 + g / 100) ** 4}, ntm_eps=1.0)
            vs.append(v)
        add_growth_adjusted_residuals(vs)
        self.assertTrue(all(abs(v.resid) < 1e-6 for v in vs))
        for v in vs[:3]:
            v.resid = None
        add_growth_adjusted_residuals(vs[:3])
        self.assertIsNone(vs[0].resid)

    def test_ratio_stats(self):
        a = [(date(2026, 1, 1).fromordinal(date(2026, 1, 1).toordinal() + i), 100 + i) for i in range(60)]
        b = [(t, 100.0) for t, _ in a]
        s = ratio_stats(a, b)
        self.assertGreater(s["z"], 1.0)
        self.assertEqual(s["pctile"], 1.0)

    def _bars(self, closes, vols=None):
        vols = vols or [100.0] * len(closes)
        return [{"date": date.fromordinal(738000 + i), "open": c, "high": c * 1.01, "low": c * 0.99, "close": c, "volume": v}
                for i, (c, v) in enumerate(zip(closes, vols))]

    def test_tape_new_low_heavy_volume_excludes_last_from_avg(self):
        closes = [100.0] * 60 + [80.0]
        vols = [100.0] * 60 + [300.0]
        t = tape_stats(self._bars(closes, vols))
        self.assertAlmostEqual(t["vol_ratio_20d"], 3.0)
        self.assertIn("TAPE:NEW_52W_LOW", t["flags"])
        self.assertIn("TAPE:HEAVY_VOLUME", t["flags"])
        self.assertIn("TAPE:GAP_DOWN_10PCT", t["flags"])
        self.assertAlmostEqual(t["low_win"], 80 * 0.99)
        self.assertAlmostEqual(t["pct_below_high"], 80 / 101 - 1)

    def test_tape_needs_history_and_lowest_low_is_all_history(self):
        self.assertIsNone(tape_stats(self._bars([1.0] * 10)))
        closes = [50.0] * 5 + [100.0] * 300
        t = tape_stats(self._bars(closes), window=252)
        self.assertAlmostEqual(t["low_ever"], 50 * 0.99)
        self.assertAlmostEqual(t["low_win"], 100 * 0.99)

    def test_ratio_half_life_mean_reverting(self):
        import math
        import random
        rng = random.Random(7)
        a, b, x = [], [], 0.0
        for i in range(250):
            x = 0.8 * x + rng.gauss(0, 0.05)
            a.append((date.fromordinal(738000 + i), 100 * math.exp(x)))
            b.append((date.fromordinal(738000 + i), 100.0))
        hl = ratio_stats(a, b)["half_life_days"]
        self.assertIsNotNone(hl)
        self.assertTrue(1.5 < hl < 8, hl)  # true AR(0.8) half-life ~3.1 days

    def _pair(self, held_eps, cand_eps):
        h = build_view("HLD", snap(100), est("HLD", held_eps), ASOF)
        c = build_view("CND", snap(100), est("CND", cand_eps), ASOF)
        return h, c

    def test_rotate_when_candidate_grows_faster(self):
        h, c = self._pair({2026: 4, 2027: 4.4, 2028: 4.8}, {2026: 4, 2027: 6, 2028: 8})
        r = decide(h, c, Params(), None, {})
        self.assertEqual(r["signal"], "ROTATE")
        self.assertTrue(r["robust"])

    def test_tax_and_cost_can_flip_to_hold(self):
        h, c = self._pair({2026: 4, 2027: 5, 2028: 6}, {2026: 4, 2027: 5.2, 2028: 6.4})
        self.assertEqual(decide(h, c, Params(tax_rate=0.4), 50.0, {})["signal"], "HOLD")

    def test_wait_for_print(self):
        h, c = self._pair({2026: 4, 2027: 4.4, 2028: 4.8}, {2026: 4, 2027: 5.0, 2028: 6.0})
        r = decide(h, c, Params(hurdle=0.10), None, {"HLD": date(2026, 7, 10)})
        self.assertEqual(r["signal"], "WAIT_FOR_PRINT")

    def test_stale_data_blocks_signal(self):
        h, c = self._pair({2026: 4, 2027: 5}, {2026: 4, 2027: 9})
        c.flags.append("STALE_ESTIMATES")
        self.assertEqual(decide(h, c, Params(), None, {})["signal"], "INSUFFICIENT_DATA")

    def test_cli_report_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "ratios.csv").write_text("ticker,date,price,market_cap,enterprise_value,earnings_per_share\n"
                                          "HLD,2026-06-30,100,1e9,1e9,4\nCND,2026-06-30,100,1e9,1e9,4\n")
            (d / "estimates.csv").write_text(",".join(store.EST_FIELDS) + "\n" + "".join(
                f"{t},eps,{y},{v},non_gaap,consensus,test,2026-06-15,12,USD\n"
                for t, vals in (("HLD", {2026: 4, 2027: 4.4, 2028: 4.8}), ("CND", {2026: 4, 2027: 6, 2028: 8}))
                for y, v in vals.items()))
            self.assertEqual(cli.main(["--data", str(d), "report", "--asof", "2026-07-01", "--hold", "HLD"]), 0)


if __name__ == "__main__":
    unittest.main()
