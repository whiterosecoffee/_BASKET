import tempfile
import unittest
from datetime import date
from pathlib import Path

from engines.valuation.rotation import cli, store
from engines.valuation.rotation.calendarize import calendarize, extend, ntm
from engines.valuation.rotation.metrics import View, add_growth_adjusted_residuals, build_view, ratio_stats
from engines.valuation.rotation import portfolio as pf
from engines.valuation.rotation import anchors as an, history as hist, profile as prof, trading as trd
from engines.valuation.rotation.implied import implied_growth, pv
from engines.valuation.rotation.macro import equity_duration, multiple_factor
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

    def test_duration_inverse_of_fcf_yield_and_capped(self):
        self.assertAlmostEqual(equity_duration(0.05)[0], 20.0)
        self.assertEqual(equity_duration(-0.1), (40.0, "NEG_FCF_DURATION_CAPPED"))
        self.assertEqual(equity_duration(0.5)[0], 3.0)
        self.assertAlmostEqual(multiple_factor(20.0, 50), 0.90)

    def test_rate_shock_favours_short_duration_candidate(self):
        h, c = self._pair({2026: 4, 2027: 4.6, 2028: 5.3}, {2026: 4, 2027: 4.4, 2028: 4.8})
        h.duration, c.duration = 30.0, 5.0
        base = decide(h, c, Params(), None, {})
        shock = decide(h, c, Params(rate_shock_bp=100), None, {})
        self.assertGreater(shock["edge"]["base"], base["edge"]["base"])

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


class P(unittest.TestCase):
    def nm(self, t, price, bear, base, bull, sigma=0.4, flags=None):
        ret = {"bear": bear, "base": base, "bull": bull}
        return pf.Name(t, price, ret, 0.25 * bear + 0.5 * base + 0.25 * bull, sigma, "user_target", flags or [])

    def test_swap_identity_no_costs(self):
        a, b = self.nm("A", 200, 0.0, 0.10, 0.20), self.nm("B", 100, 0.2, 0.60, 1.0)
        r = pf.swap(a, b, 10, None, pf.Costs(0.0, 0.0))
        self.assertAlmostEqual(r["share_multiplier"], 2.0)             # P_A/P_B
        self.assertAlmostEqual(r["edge_base"], 1.60 / 1.10 - 1)        # (1+rB)/(1+rA)-1
        self.assertAlmostEqual(r["rich_pct"], r["spot_ratio"] / r["fair_ratio"] - 1)
        self.assertEqual(r["signal"], "SWAP")

    def test_tax_and_cost_reduce_shares(self):
        a, b = self.nm("A", 200, 0.0, 0.1, 0.2), self.nm("B", 100, 0.2, 0.6, 1.0)
        r = pf.swap(a, b, 10, 100.0, pf.Costs(0.002, 0.25))
        gross = 2000.0
        fric = gross * 0.002 + 0.25 * (100 * 10)
        self.assertAlmostEqual(r["shares_b"], (gross - fric) / 100)
        self.assertLess(r["share_multiplier"], 2.0)

    def test_contested_when_bear_case_loses(self):
        a, b = self.nm("A", 100, 0.1, 0.2, 0.3), self.nm("B", 100, -0.5, 0.6, 1.5)
        r = pf.swap(a, b, 1, None, pf.Costs(0, 0))
        self.assertEqual(r["signal"], "CONTESTED")

    def test_weights_cap_and_sum(self):
        ns = [self.nm("A", 1, 0, 1.0, 0, 0.3), self.nm("B", 1, 0, 0.2, 0, 0.3), self.nm("C", 1, 0, -0.1, 0, 0.3)]
        w = pf.target_weights(ns, max_w=0.5)
        self.assertAlmostEqual(sum(w.values()), 1.0)
        self.assertLessEqual(max(w.values()), 0.5 + 1e-9)
        self.assertEqual(w["C"], 0.0)

    def test_propose_self_financing_and_band(self):
        ns = [self.nm("A", 100, 0, 0.0, 0, 0.3), self.nm("B", 50, 0, 0.5, 0, 0.3)]
        hold = {"A": {"shares": 10.0, "basis_price": 100.0}, "B": {"shares": 0.0, "basis_price": 50.0}}
        r = pf.propose(ns, hold, pf.Costs(0.0, 0.0), max_w=1.0, band=0.10)
        sell = sum(o["shares"] * o["price"] for o in r["orders"] if o["side"] == "SELL")
        buy = sum(o["shares"] * o["price"] for o in r["orders"] if o["side"] == "BUY")
        self.assertAlmostEqual(sell, buy)
        self.assertAlmostEqual(buy, 1000.0)
        hold2 = {"A": {"shares": 0.05, "basis_price": 100.0}, "B": {"shares": 19.9, "basis_price": 50.0}}
        self.assertEqual(pf.propose(ns, hold2, pf.Costs(0, 0), max_w=1.0, band=0.10)["orders"], [])

    def test_staging_limits_buy_into_new_low(self):
        ns = [self.nm("A", 100, 0, 0.0, 0, 0.3), self.nm("B", 50, 0, 0.5, 0, 0.3, ["TAPE:NEW_52W_LOW"])]
        hold = {"A": {"shares": 10.0, "basis_price": 100.0}, "B": {"shares": 0.0, "basis_price": 50.0}}
        r = pf.propose(ns, hold, pf.Costs(0, 0), max_w=1.0, band=0.10, stage=0.33)
        buy = sum(o["shares"] * o["price"] for o in r["orders"] if o["side"] == "BUY")
        self.assertAlmostEqual(buy, 330.0)

    def test_horizon_normalisation_and_targets_point_in_time(self):
        row = {s: {"target_price": "121", "horizon_date": "2028-07-01"} for s in pf.SCEN}
        r = pf.normalise_returns(row, 100.0, date(2026, 7, 1), 12)
        self.assertAlmostEqual(r["base"], 0.10, places=3)              # 21% over ~2y -> ~10% per 12m
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.csv"
            p.write_text("ticker,scenario,target_price,horizon_date,source,as_of\n"
                         "AAA,base,150,2027-07-01,me,2026-06-01\nAAA,base,999,2027-07-01,me,2026-09-01\n")
            tg = pf.load_targets(p, date(2026, 7, 1), 12)
            self.assertEqual(tg["AAA"]["raw"]["base"]["target_price"], "150")
            self.assertIn("BEAR_MISSING_USING_BASE", tg["AAA"]["flags"])

    def test_holdings_ledger_replay_average_cost(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "h.csv").write_text("ticker,shares,basis_price,as_of\nAAA,10,100,2026-01-01\n")
            (d / "l.csv").write_text("date,ticker,delta_shares,price,fee,reason\n2026-02-01,AAA,10,50,0,x\n2026-03-01,AAA,-5,70,0,x\n2026-12-01,AAA,100,1,0,future\n")
            h = pf.load_holdings(d / "h.csv", d / "l.csv", date(2026, 6, 1))
            self.assertAlmostEqual(h["AAA"]["shares"], 15)
            self.assertAlmostEqual(h["AAA"]["basis_price"], 75.0)

    def test_simulate_pair_runs_and_counts(self):
        import math
        a = [(date.fromordinal(738000 + i), 100 * math.exp(0.2 * math.sin(i / 6))) for i in range(300)]
        b = [(t, 100.0) for t, _ in a]
        r = pf.simulate_pair(a, b, lookback=30, band=0.05)
        self.assertGreater(r["swaps"], 2)
        self.assertGreater(r["rotator_A_units"], 1.0)                  # oscillating ratio: rotation accumulates A-share units


class I(unittest.TestCase):
    def test_implied_growth_roundtrip(self):
        mcap = pv(100.0, 0.07, 0.095, 10, 0.03)
        self.assertAlmostEqual(implied_growth(mcap, 100.0, 0.095, 10, 0.03), 0.07, places=6)

    def test_implied_growth_guards(self):
        self.assertIsNone(implied_growth(1000, -5.0, 0.095))
        self.assertIsNone(implied_growth(1000, 10.0, 0.02, g_term=0.03))      # r <= terminal g
        self.assertIsNone(implied_growth(1e9, 1.0, 0.095))                    # price far above any solvable growth

    def test_guidance_split_adjusts_eps_only_and_is_point_in_time(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "g.csv"
            p.write_text("ticker,period,metric,low,high,basis,split_factor,annualize,source,as_of\n"
                         "ZZZ,Q2,eps,55,57,non_gaap,8,4,x,2026-10-29\nZZZ,Q2,revenue,12.2,12.6,gaap,8,4,x,2026-10-29\n"
                         "ZZZ,Q3,eps,100,100,non_gaap,8,4,x,2027-01-01\n")
            g = store.load_guidance(p, date(2026, 11, 20))
            self.assertAlmostEqual(g[("ZZZ", "eps")]["mid"], 7.0)             # 56/8
            self.assertAlmostEqual(g[("ZZZ", "revenue")]["mid"], 12.4)        # split never applied to revenue
            self.assertEqual(g[("ZZZ", "eps")]["period"], "Q2")               # later guidance excluded

    def test_actual_kind_outranks_consensus(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "e.csv"
            p.write_text("ticker,metric,fiscal_year,value,basis,kind,source,as_of,fye_month\n"
                         "AAA,eps,2026,4.0,non_gaap,consensus,x,2026-06-01,12\nAAA,eps,2026,4.77,non_gaap,actual,x,2026-06-01,12\n")
            self.assertEqual(store.load_estimates(p, ASOF)[("AAA", "eps")][2026].value, 4.77)


class A(unittest.TestCase):
    def test_memory_pnl_matches_hand_calc(self):
        cfg = {"industry": {"type": "memory_pnl", "gm": 0.85, "opex": 0.045, "opex_growth": 0.10, "cost_per_bit_change": -0.10,
                            "bits": "b", "asp": "a"}}
        ind = {"b": {"bear": .1, "base": .2, "bull": .3}, "a": {"bear": -.35, "base": -.2, "bull": -.05}}
        r = an.anchor_I("X", None, cfg, ind, {}, {})["ret"]
        op0 = 1 - 0.15 - 0.045
        base = (1.2 * 0.8 - 0.15 * 1.2 * 0.9 - 0.045 * 1.1) / op0 - 1
        self.assertAlmostEqual(r["base"], base)
        self.assertLess(r["bear"], r["base"])
        self.assertLess(r["base"], r["bull"])

    def test_std_factors_default_is_flat_and_hist_is_like_for_like(self):
        f, _ = an.std_factors(16.0, {"median": 44.0, "p25": 33.0, "p75": 50.0}, True, 0.0, 0.2)
        self.assertEqual(f, {"bear": 0.8, "base": 1.0, "bull": 1.2})
        f2, _ = an.std_factors(16.0, {"median": 32.0, "p25": 24.0, "p75": 40.0}, True, 0.5, 0.2)
        self.assertAlmostEqual(f2["base"], 1.5)             # halfway to a median that is 2x today's trailing multiple
        self.assertEqual(an.std_factors(16.0, None, True, 0.5, 0.2)[0]["base"], 1.0)

    def test_blend_renormalises_and_flags_disagreement(self):
        a = {"ret": {"bear": -.2, "base": 0.0, "bull": .2}, "flags": []}
        b = {"ret": {"bear": .3, "base": .9, "bull": 1.5}, "flags": []}
        r = an.blend({"F": a, "I": b, "R": None}, {"F": .5, "I": .3, "R": .2})
        self.assertAlmostEqual(r["weights"]["F"], 0.5 / 0.8)
        self.assertAlmostEqual(r["ret"]["base"], 0.3 / 0.8 * 0.9)
        self.assertTrue(any(f.startswith("ANCHOR_DISAGREE") for f in r["flags"]))
        self.assertTrue(any(f.startswith("MISSING_ANCHOR") for f in r["flags"]))

    def test_ratio_anchor_rich_name_gets_negative_return(self):
        a = [(date.fromordinal(738000 + i), 100.0 + (50 if i > 280 else 0)) for i in range(300)]
        b = [(t, 100.0) for t, _ in a]
        r = an.anchor_R({"A": a, "B": b}, lookback=250, lam=0.5)
        self.assertLess(r["A"]["ret"]["base"], 0)
        self.assertGreater(r["B"]["ret"]["base"], 0)

    def test_history_normalises_split_and_bad_filing_dates(self):
        mk = lambda pe, fd, ni, sh: {"period_end": pe, "filing": fd, "revenue": 1.0, "ni": ni, "sh": sh}
        rows = [mk(date(2026, 1, 2), date(2026, 1, 30), 800.0, 1248.0), mk(date(2026, 7, 3), date(2026, 8, 17), 6903.0, 158.0),
                mk(date(2025, 6, 27), date(2026, 8, 17), -23.0, 145.0), mk(date(2026, 10, 2), date(2026, 10, 30), 8101.0, 1232.0)]
        rows.sort(key=lambda r: r["period_end"])
        out = hist.normalise(rows)
        by = {r["period_end"]: r for r in out}
        self.assertEqual(by[date(2026, 7, 3)]["split_k"], 8.0)
        self.assertAlmostEqual(by[date(2026, 7, 3)]["eps_norm"], 6903 / (158 * 8))
        self.assertEqual(by[date(2026, 1, 2)]["split_k"], 1.0)
        self.assertEqual(by[date(2025, 6, 27)]["avail"], date(2025, 6, 27) + __import__("datetime").timedelta(days=45))  # filing date a year late
        self.assertEqual(by[date(2026, 1, 2)]["avail"], date(2026, 1, 30))

    def test_disagreeing_anchors_halve_the_weight_cap(self):
        a = pf.Name("A", 1, {"bear": 0, "base": 1, "bull": 2}, 1.0, 0.3, "auto_anchors", ["ANCHOR_DISAGREE"])
        b = pf.Name("B", 1, {"bear": 0, "base": .1, "bull": .2}, 0.1, 0.3, "auto_anchors", [])
        w = pf.target_weights([a, b], max_w=0.8)
        self.assertAlmostEqual(w["A"], 0.4)


class T2(unittest.TestCase):
    def _cl(self, vals, start=738000):
        return [(date.fromordinal(start + i), v) for i, v in enumerate(vals)]

    def test_zone_dwell_visits_and_entry_direction(self):
        vals = [100, 100.5, 120, 100.2, 120.5, 119.8]
        z = {(round(x["low"]), round(x["high"])): x for x in trd.zones(self._cl(vals), [1.0] * 6, top=10)}
        lo = next(v for v in z.values() if v["low"] <= 100 < v["high"])
        self.assertEqual(lo["dwell_days"], 3)
        self.assertEqual(lo["visits"], 2)
        self.assertEqual(lo["entries_from_above"], 1)
        self.assertAlmostEqual(sum(x["volume_share"] for x in z.values()), 1.0)

    def test_level_crossings_counts_sign_changes(self):
        r = trd.level_crossings(self._cl([90, 110, 90, 110, 110, 90]), 100)
        self.assertEqual(r["crossings"], 4)

    def _bars(self, n=30, last=None):
        bars = [{"date": date.fromordinal(738000 + i), "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 10.0} for i in range(n)]
        if last:
            bars[-1] = {"date": bars[-1]["date"], **last}
        return bars

    def test_extremes_flags_new_low_and_volume_multiple(self):
        bars = self._bars(last={"open": 90.0, "high": 92.0, "low": 80.0, "close": 81.0, "volume": 30.0})
        e = trd.extremes_and_rebound(bars, None)
        self.assertTrue(e["last_final_bar"]["made_52w_low"])
        self.assertAlmostEqual(e["last_final_bar"]["volume_vs_prior20d"], 3.0)
        self.assertAlmostEqual(e["last_final_bar"]["close_location_in_range"], (81 - 80) / (92 - 80))

    def test_provisional_gap_unfilled_only_when_session_low_clears_prior_high(self):
        bars = self._bars(last={"open": 90.0, "high": 92.0, "low": 80.0, "close": 81.0, "volume": 30.0})
        filled = trd.extremes_and_rebound(bars, {"open": 95.0, "high": 99.0, "low": 90.0, "close": 98.0})["provisional_next_session"]
        self.assertTrue(filled["session_low_above_prior_low"])
        self.assertFalse(filled["gap_unfilled_vs_prior_high"])             # session low 90 <= prior high 92
        full = trd.extremes_and_rebound(bars, {"open": 95.0, "high": 99.0, "low": 93.0, "close": 98.0})["provisional_next_session"]
        self.assertTrue(full["gap_unfilled_vs_prior_high"])                # session low 93 > prior high 92
        self.assertAlmostEqual(full["last_vs_prior_close"], 98 / 81 - 1)

    def test_relationship_x_and_relative_return(self):
        a = self._cl([100.0 + i for i in range(80)])
        b = self._cl([50.0] * 80)
        r = trd.relationship(a, b)
        self.assertAlmostEqual(r["x_now"], 179.0 / 50.0)
        self.assertGreater(r["relative_return"]["20d"], 0)

    def test_event_reaction_amc_uses_next_day(self):
        cl = self._cl([100, 100, 110, 121])
        m = prof._react(cl, date.fromordinal(738001), "AMC")
        self.assertEqual(m["day"], date.fromordinal(738002))
        self.assertAlmostEqual(m["modifier"], 1.10)
        m2 = prof._react(cl, date.fromordinal(738003), "INTRADAY")
        self.assertAlmostEqual(m2["modifier"], 1.10)


if __name__ == "__main__":
    unittest.main()
