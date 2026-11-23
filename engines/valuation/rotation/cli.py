"""python -m engines.valuation.rotation.cli {report,ingest-ratios,ingest-prices,ingest-estimates} ..."""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from . import anchors as an
from . import cohort as co
from . import models as mdl
from . import multiplepoints as mp
from . import pointcompare as pc
from . import history as hist
from . import portfolio as pf
from . import profile as prof
from . import store
from .implied import implied_growth
from .macro import load_yields, multiple_factor
from .tape import tape_stats
from .metrics import YEARS, add_growth_adjusted_residuals, build_view, ratio_stats
from .rotation import Params, decide

DEFAULT_DATA = Path(__file__).resolve().parents[3] / "research" / "models" / "rotation"
RATIO_FIELDS = ["ticker", "date", "price", "market_cap", "enterprise_value", "earnings_per_share",
                "price_to_earnings", "ev_to_sales", "ev_to_ebitda", "free_cash_flow", "ingested_at"]


def _f(x, w=6, nd=1, pct=False):
    if x is None:
        return "NM".rjust(w)
    return (f"{x*100:.{nd}f}%" if pct else f"{x:.{nd}f}").rjust(w)


def cmd_report(a) -> int:
    data, asof = Path(a.data), date.fromisoformat(a.asof) if a.asof else date.today()
    snaps = store.load_ratios(data / "ratios.csv", asof)
    ests = store.load_estimates(data / "estimates.csv", asof)
    earn = store.load_events(data / "events.csv", asof)
    pos = store.load_positions(data / "positions.csv")
    views = [build_view(t, s, ests, asof) for t, s in sorted(snaps.items())]
    add_growth_adjusted_residuals(views)
    tapes = {}
    for v in views:
        t = tape_stats(store.load_bars(data / "prices" / f"{v.ticker}.csv", asof))
        if t:
            tapes[v.ticker] = t
            v.flags += t["flags"]
    print(f"As of {asof}  |  prices: Massive ratios snapshot, calendarized USD, forward EPS basis as stored\n")
    print("TICKER   PRICE  NTM_PE " + " ".join(f"PE{y}".rjust(6) for y in YEARS) + "   CAGR   PEG  EV/S  RESID  NEXT_EPS  FLAGS")
    for v in sorted(views, key=lambda v: (v.ntm_pe is None, v.ntm_pe or 0)):
        print(f"{v.ticker:<6} {v.price:>7.2f} {_f(v.ntm_pe,7)} " + " ".join(_f(v.pe(y)) for y in YEARS)
              + f" {_f(v.cagr,6,0,True)} {_f(v.peg,5,2)} {_f(v.ev_sales_ntm,5)} {_f(v.resid,6)}  "
              f"{str(earn.get(v.ticker) or '-'):>10}  {' '.join(v.flags)}")
    guide = store.load_guidance(data / "guidance.csv", asof)
    if guide:
        print("\nCOMPANY GUIDANCE (primary sources; per-share split-adjusted; annualized = x factor, NOT a forecast)")
        print("TICKER  PERIOD       METRIC                  LOW      HIGH     ANNUALIZED  PRICE/ANN_EPS  EV/ANN_REV  BASIS     AS_OF")
        by = {v.ticker: v for v in views}
        for (t, m), g in sorted(guide.items()):
            v, ann = by.get(t), g["mid"] * g["annualize"]
            pe = f"{v.price / ann:>13.2f}x" if m == "eps" and v and ann > 0 else " " * 14
            evs = f"{v.ev / 1e9 / ann:>10.2f}x" if m == "revenue" and v and v.ev and ann > 0 else " " * 11
            print(f"{t:<7} {g['period']:<12} {m:<20} {g['low']:>8.3f} {g['high']:>8.3f} {ann:>12.2f}  {pe} {evs}  {g['basis']:<8}  {g['as_of']}")
    ys = load_yields(data / "macro" / "treasury_yields.csv", asof)
    if ys:
        (d1, y1), (d0, y0) = ys[-1], ys[max(0, len(ys) - 6)]
        print(f"\nRATES {d1}: 2y {y1['yield_2_year']}  10y {y1['yield_10_year']}  30y {y1['yield_30_year']}  "
              f"(vs {d0}: 10y {float(y1['yield_10_year'])-float(y0['yield_10_year']):+.2f}pp, 2y {float(y1['yield_2_year'])-float(y0['yield_2_year']):+.2f}pp)")
    if ys:
        r_disc = float(ys[-1][1]["yield_10_year"]) / 100 + a.erp
        print(f"\nIMPLIED EXPECTATIONS (reverse DCF on TTM FCF; r = 10y {ys[-1][1]['yield_10_year']}% + ERP {a.erp:.1%} = {r_disc:.2%}, terminal g {a.g_term:.1%}, {a.years}y)")
        print("TICKER  MKT_CAP($B)  TTM_FCF($B)  FCF_YIELD  IMPLIED_FCF_CAGR")
        for v in views:
            fcf = v.fcf_yield * v.market_cap if v.fcf_yield is not None and v.market_cap else None
            g = implied_growth(v.market_cap, fcf, r_disc, a.years, a.g_term) if v.market_cap else None
            print(f"{v.ticker:<6} {v.market_cap/1e9:>11.1f} {(fcf or 0)/1e9:>12.1f} {_f(v.fcf_yield,9,1,True)} "
                  + (f"{g*100:>15.1f}%" if g is not None else "      n/m (FCF<=0 or outside solvable range)"))
    print("\nRATE SENSITIVITY  (multiple change = -duration x shock; duration ~ 1/FCF yield, capped 3-40y)")
    print("TICKER  FCF_YIELD  DURATION   +25bp   +50bp  +100bp")
    for v in views:
        print(f"{v.ticker:<6} {_f(v.fcf_yield,9,1,True)} {v.duration:>9.1f} " + " ".join(_f(multiple_factor(v.duration, b) - 1, 7, 1, True) for b in (25, 50, 100))
              + ("   (capped)" if any(f.endswith("CAPPED") for f in v.flags) else ""))
    if tapes:
        print("\nTAPE (daily bars; volume averages exclude the last bar)")
        print("TICKER  CLOSE  1D%    5D%   10D%  LOW_52W  ON_DATE     VOL_ON_LOW  %>LOW  %<HIGH  LOWEST_LOW  ON_DATE     LAST_VOL  x20D  x50D")
        for tk, t in tapes.items():
            print(f"{tk:<6} {t['close']:>7.2f} {_f(t['chg_1d'],6,1,True)} {_f(t['ret_5d'],6,1,True)} {_f(t['ret_10d'],6,1,True)} "
                  f"{t['low_win']:>8.2f}  {t['low_win_date']}  {t['low_win_vol']/1e6:>8.1f}M {_f(t['pct_above_low'],6,1,True)} "
                  f"{_f(t['pct_below_high'],7,0,True)} {t['low_ever']:>10.2f}  {t['low_ever_date']}  {t['vol_last']/1e6:>7.1f}M "
                  f"{t['vol_ratio_20d']:>4.1f}x {t['vol_last']/t['vol_50d']:>4.1f}x")
    if a.hold:
        by = {v.ticker: v for v in views}
        held = by.get(a.hold.upper())
        if not held:
            print(f"\n{a.hold} has no snapshot.")
            return 1
        p = Params(horizon_months=a.horizon, hurdle=a.hurdle, rate_shock_bp=a.rate_shock_bp, tax_rate=a.tax, round_trip_cost=a.cost,
                   rerate={k.upper(): float(x) for k, x in (kv.split("=") for kv in a.rerate)})
        print(f"\nRotation from {held.ticker} (horizon {p.horizon_months}m, rate shock {p.rate_shock_bp:+.0f}bp, hurdle {p.hurdle:.0%}, cost {p.round_trip_cost:.2%}, tax {p.tax_rate:.0%})")
        print("CAND    SIGNAL            EXP_EDGE  BEAR   BASE   BULL  ROBUST  RESID_GAP  NOTES")
        for v in views:
            if v is held:
                continue
            r = decide(held, v, p, pos.get(held.ticker, {}).get("entry_price"), earn)
            e = r.get("edge")
            print(f"{v.ticker:<7} {r['signal']:<17} " + (" ".join(_f(e[k], 8, 1, True) for k in ("exp", "bear", "base", "bull"))
                  + f"  {str(r['robust']):<6} {_f(r['resid_gap'],8)}  " if e else " " * 44) + "; ".join(r["notes"]))
    return 0


def _names(a, asof, data):
    """Build Name objects from targets.csv (preferred) or the EPS x multiple model."""
    from .rotation import Params, scenarios
    snaps = store.load_ratios(data / "ratios.csv", asof)
    ests = store.load_estimates(data / "estimates.csv", asof)
    probs = (0.25, 0.5, 0.25)
    tg = pf.load_targets(data / "targets.csv", asof, a.horizon, probs)
    out = []
    for t, s in sorted(snaps.items()):
        v = build_view(t, s, ests, asof)
        bars = store.load_bars(data / "prices" / f"{t}.csv", asof)
        tp = tape_stats(bars)
        flags = v.flags + (tp["flags"] if tp else [])
        sig = pf.realised_vol(bars, a.horizon)
        if t in tg:
            ret = pf.normalise_returns(tg[t]["raw"], s["price"], asof, a.horizon)
            src = " ".join(r["source"] for r in tg[t]["raw"].values())
            auto = src.startswith("auto:")
            out.append(pf.Name(t, s["price"], ret, sum(w * ret[k] for w, k in zip(probs, pf.SCEN)), sig, "auto_anchors" if auto else "user_target",
                               flags + tg[t]["flags"] + (["ANCHOR_DISAGREE"] if "ANCHOR_DISAGREE" in src else [])))
        elif v.usable and (sc := scenarios(v, Params(horizon_months=a.horizon))):
            ret = {k: sc[k] for k in pf.SCEN}
            out.append(pf.Name(t, s["price"], ret, sc["exp"], sig, "model", flags))
        else:
            print(f"skip {t}: no targets and model not usable ({','.join(v.flags) or 'no data'})", file=sys.stderr)
    return out


def _anchor_run(a, asof, data):
    snaps = store.load_ratios(data / "ratios.csv", asof)
    ests = store.load_estimates(data / "estimates.csv", asof)
    guide = store.load_guidance(data / "guidance.csv", asof)
    ind = an.load_industry(data / "industry.csv", asof)
    cmap = an.load_map(data / "anchor_map.json")
    w = {"F": a.w_f, "I": a.w_i, "R": a.w_r}
    prices = {t: store.load_prices(data / "prices" / f"{t}.csv", asof) for t in snaps}
    ratio = an.anchor_R({t: p for t, p in prices.items() if p}, lam=a.lam)
    out = {}
    for t, s in sorted(snaps.items()):
        cfg = cmap.get(t, {})
        v = build_view(t, s, ests, asof)
        ev_info = {"ev": s["enterprise_value"], "mcap": s["market_cap"]}
        bars = store.load_bars(data / "prices" / f"{t}.csv", asof)
        rows = hist.load_fund(data / "fundamentals" / f"{t}_quarterly.csv")
        mh = hist.multiple_history(bars, rows) if rows and bars else {"pe": []}
        st = hist.stats(mh["pe"])
        ok = bool(st) and hist.eps_regime_ok(rows, asof)
        sig = pf.realised_vol(bars, a.horizon)
        band_i = a.band if a.band is not None else (min(0.5, max(0.15, sig)) if sig else 0.15)
        tn = hist.ttm_at(rows, asof) if rows else None
        trailing_now = s["price"] / tn["eps"] if tn and tn["eps"] > 0 else None
        anch = {"F": an.anchor_F(t, v, cfg, guide, st, ok, trailing_now, a.horizon, a.rerate, band_i, ev_info),
                "I": an.anchor_I(t, v, cfg, ind, guide, ev_info), "R": ratio.get(t)}
        if anch["F"]:
            anch["F"]["flags"].append(f"BAND={band_i:.0%}{'(auto=realised vol, clamp 15-50%)' if a.band is None else ''}")
        out[t] = {"price": s["price"], "anchors": anch, "blend": an.blend(anch, w), "view": v, "hist": st}
    return out


def cmd_anchors(a) -> int:
    data, asof = Path(a.data), date.fromisoformat(a.asof) if a.asof else date.today()
    res = _anchor_run(a, asof, data)
    print(f"Anchors as of {asof}, horizon {a.horizon}m, weights F{a.w_f:.0%} I{a.w_i:.0%} R{a.w_r:.0%}, rerate toward hist median {a.rerate:.0%}, multiple band {'auto' if a.band is None else format(a.band, '.0%')}\n")
    print("TICKER  ANCHOR  BEAR     BASE     BULL    FLAGS")
    for t, r in res.items():
        for k in ("F", "I", "R"):
            x = r["anchors"][k]
            print(f"{t:<7} {k:<7} " + (" ".join(_f(x['ret'][s], 7, 1, True) for s in an.SC) + "  " + " ".join(x["flags"]) if x else "   n/a (no inputs)"))
        b = r["blend"]
        print(f"{t:<7} BLEND   " + " ".join(_f(b['ret'][s], 7, 1, True) for s in an.SC) + f"  -> targets {', '.join(f'{r['price']*(1+b['ret'][s]):.2f}' for s in an.SC)}  " + " ".join(b["flags"]))
        if r["hist"]:
            h = r["hist"]
            print(f"        hist P/E {h['first']}..{h['last']}: p25 {h['p25']:.1f} median {h['median']:.1f} p75 {h['p75']:.1f}  (now {r['view'].ntm_pe or float('nan'):.1f} NTM)")
        print()
    if a.write:
        when = (asof + timedelta(days=round(30.4375 * a.horizon))).isoformat()
        rows = []
        for t, r in res.items():
            for s in an.SC:
                rows.append({"ticker": t, "scenario": s, "target_price": round(r["price"] * (1 + r["blend"]["ret"][s]), 4), "horizon_date": when,
                             "source": f"auto:build-targets w=F{a.w_f}/I{a.w_i}/R{a.w_r} " + " ".join(r["blend"]["flags"]), "as_of": asof.isoformat()})
        print(f"appended {store.append_csv(data / 'targets.csv', pf.TARGET_FIELDS, rows)} auto-generated targets (override by appending your own rows with a later as_of)")
    return 0


def cmd_profile(a) -> int:
    data, asof = Path(a.data), date.fromisoformat(a.asof) if a.asof else date.today()
    paths = prof.write_all(data, asof, not a.no_provisional, a.hurdle, a.cost)
    for p in paths:
        print(f"wrote {p.relative_to(data.parent.parent.parent) if data.parent.parent.parent in p.parents else p}")
    return 0


def cmd_cohort(a) -> int:
    d_ = Path(a.data) / "cohort"
    rows, shots, themes = co.load(d_)
    ms = co.metrics(rows, shots, themes)
    cs = co.cross_section(ms)
    print("CROSS-SECTION (benchmarks excluded; Monday intraday, provisional)")
    print(f"  n {cs['n']}  corr(Fri change, Mon change) {cs['pearson_fri_vs_mon']:.2f}  Spearman {cs['spearman_fri_vs_mon']:.2f}  slope {cs['slope_mon_on_fri']:.2f}  "
          f"median Fri {cs['median_fri']:+.1%} Mon {cs['median_mon']:+.1%}  above Thursday close {cs['share_above_thu_close' if False else 'share_above_thursday_close']:.0%}  gap unfilled {cs['share_gap_unfilled']:.0%}\n")
    print("THEME            N  MEAN_FRI  MEAN_MON  MEAN_RECOVERY")
    for t in co.theme_table(ms):
        print(f"{t['theme']:<22}{t['n']:>2}  {t['mean_fri']:+8.1%}  {t['mean_mon']:+8.1%}  {t['mean_recovery']:>8.0%}   {' '.join(t['tickers'])}")
    print("\nTICKER   THEME                 FRI      MON    RECOVERY  FRI_CLOSE_LOC  GAP_UNFILLED  ABOVE_THU")
    for m in sorted(ms, key=lambda m: -m["mon_change"]):
        if a.only and m["ticker"] not in a.only.upper().split(","):
            continue
        print(f"{m['ticker']:<8} {m['theme']:<20} {m['fri_change']:+7.1%} {m['mon_change']:+8.1%} {m['recovery_of_fri_drop'] or 0:>9.0%} {m['fri_close_location'] or 0:>13.2f}  {str(m['gap_unfilled']):<12}  {m['above_thu_close']}")
    return 0


def cmd_compare(a) -> int:
    d_ = Path(a.data) / "cohort"
    out = Path(a.out) if a.out else Path(a.data) / "comparisons" / f"{a.a}__vs__{a.b}__2026-11-23.json"
    doc = pc.write(d_, out, a.a, a.b)
    cs = doc["cohort_summary"]
    print(f"wrote {out}  ({cs['n_excluding_benchmarks']} names, as of {doc['as_of_et']} ET, provisional={doc['provisional']})")
    for t, s in doc["subjects"].items():
        c = s["comparison"]
        print(f"  {t}: {c['a']:.2f} -> {c['b']:.2f} ({c['change']:+.1%}); recovered {c.get('share_of_friday_drop_recovered_at_b', float('nan')):.0%} of Fri drop at peak; "
              f"last is {c.get('giveback_from_b_to_last', float('nan')):+.1%} from peak (gave back {c.get('giveback_share_of_move', float('nan')):.0%} of the move)")
    return 0


def cmd_multiples(a) -> int:
    import json
    data, asof = Path(a.data), date.fromisoformat(a.asof) if a.asof else date.today()
    doc = mp.build(data, asof)
    out = Path(a.out) if a.out else data / "comparisons" / "multiples_at_compression_and_rebound_2026-11-23.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, default=str) + "\n")
    print(f"wrote {out}")
    for t, s in doc["subjects"].items():
        f = s.get("fundamentals_gaap_norm_ttm"); fw = s.get("forward"); ev = s.get("ev_to_guided_annualised_revenue")
        print(f"{t}: low {s['points']['fri_low']:.2f} -> peak {s['points']['mon_high']:.2f}")
        if f: print(f"   trailing GAAP-norm P/E {f['pe']['fri_low']:.1f} -> {f['pe']['mon_high']:.1f} (52w peak {f['pe_52w_peak_price_on_current_eps']:.1f} on today's EPS; {f['pe_at_52w_peak_point_in_time']:.1f} on EPS then)")
        if fw: print(f"   forward P/E {fw['pe']['fri_low']:.1f} -> {fw['pe']['mon_high']:.1f} ({fw['basis'][:40]})")
        if ev: print(f"   EV/guided-annualised revenue {ev['ev_s']['fri_low']:.2f}x -> {ev['ev_s']['mon_high']:.2f}x")
    return 0


def cmd_models(a) -> int:
    res = mdl.write_all(Path(a.data))
    rel = res["relativity"]
    print(f"wrote {res['models']} models to models/ and the relativity tracker to relativity/")
    print(f"hit a new 52-week low on Friday: {len(rel['hit_52w_low_on_friday'])}/{rel['n_equities']} -> {' '.join(rel['hit_52w_low_on_friday'])}")
    for k, v in rel["group_stats"].items():
        print(f"  {k}: recovery of Fri drop (median) {v['recovery_of_friday_drop_at_last'].get('median', float('nan')):.0%}, of 52w range {v['recovery_of_52w_range_at_last'].get('median', float('nan')):.1%}, rebound {v['rebound_fri_close_to_last'].get('median', float('nan')):+.1%}")
    return 0


def cmd_swap(a) -> int:
    data, asof = Path(a.data), date.fromisoformat(a.asof) if a.asof else date.today()
    names = {n.ticker: n for n in _names(a, asof, data)}
    hold = pf.load_holdings(data / "holdings.csv", data / "ledger.csv", asof)
    c = pf.Costs(a.cost, a.tax)
    if a.src.upper() not in names:
        print(f"{a.src}: no targets/model; add rows to targets.csv", file=sys.stderr)
        return 1
    src = names[a.src.upper()]
    sh = hold.get(src.ticker, {}).get("shares", 1.0)
    basis = hold.get(src.ticker, {}).get("basis_price")
    print(f"Swap from {src.ticker} ({sh:g} sh @ {src.price:.2f}, basis {basis}) | horizon {a.horizon}m | hurdle {a.hurdle:.0%} | cost {c.round_trip:.2%} tax {c.tax_rate:.0%}")
    print("TO      SIGNAL     SHARES_OUT  MULT   SPOT_R  FAIR_R  RICH%   EDGE_EXP  BEAR   BASE   BULL   TRIG_A>B  TRIG_B>A  BASIS")
    for t, n in names.items():
        if t == src.ticker:
            continue
        r = pf.swap(src, n, sh, basis, c, a.hurdle)
        print(f"{t:<7} {r['signal']:<10} {r['shares_b']:>10.3f} {r['share_multiplier']:>5.2f} {r['spot_ratio']:>7.3f} {r['fair_ratio']:>7.3f} "
              f"{_f(r['rich_pct'],6,1,True)} {_f(r['edge_exp'],8,1,True)} {_f(r['edge_bear'],6,1,True)} {_f(r['edge_base'],6,1,True)} {_f(r['edge_bull'],6,1,True)} "
              f"{r['trigger_a_to_b']:>8.3f} {r['trigger_b_to_a']:>9.3f}  {n.basis} {' '.join(n.flags)}")
    return 0


def cmd_rebalance(a) -> int:
    data, asof = Path(a.data), date.fromisoformat(a.asof) if a.asof else date.today()
    names = _names(a, asof, data)
    hold = pf.load_holdings(data / "holdings.csv", data / "ledger.csv", asof)
    if not hold or not names:
        print("need holdings.csv and at least one name with targets/model", file=sys.stderr)
        return 1
    res = pf.propose(names, hold, pf.Costs(a.cost, a.tax), a.max_weight, a.band, a.stage)
    print(f"Virtual ETF NAV ${res['nav']:,.2f} at {asof}  (horizon {a.horizon}m, band {a.band:.0%}, max weight {a.max_weight:.0%})")
    print("TICKER  CUR_W   TGT_W   E[RET]   SIGMA   BASIS")
    for n in names:
        print(f"{n.ticker:<6} {_f(res['current'][n.ticker],6,1,True)} {_f(res['target'][n.ticker],7,1,True)} {_f(n.exp,8,1,True)} {_f(n.sigma,7,1,True)}  {n.basis}")
    for o in res["orders"]:
        print(f"  {o['side']:<4} {o['ticker']:<6} {o['shares']:>12.4f} sh @ {o['price']:.2f}")
    for note in res["notes"]:
        print("  note:", note)
    if a.record and res["orders"]:
        rows = [{"date": asof.isoformat(), "ticker": o["ticker"], "delta_shares": (o["shares"] if o["side"] == "BUY" else -o["shares"]),
                 "price": o["price"], "fee": 0, "reason": "rebalance"} for o in res["orders"]]
        print(f"recorded {store.append_csv(data / 'ledger.csv', pf.LEDGER_FIELDS, rows)} ledger rows (paper trades)")
    return 0


def cmd_simulate(a) -> int:
    data, asof = Path(a.data), date.fromisoformat(a.asof) if a.asof else date.today()
    pa, pb = (store.load_prices(data / "prices" / f"{t.upper()}.csv", asof) for t in (a.a, a.b))
    r = pf.simulate_pair(pa, pb, a.lookback, a.band, a.cost)
    if not r:
        print("not enough overlapping history")
        return 1
    print(f"{a.a}/{a.b}  {r['start']} -> {r['end']}  lookback {a.lookback}d band {a.band:.0%} cost {a.cost:.2%}  swaps {r['swaps']}  ends in {r['end_holding']}")
    print(f"  USD multiple: rotator {r['rotator_usd_x']:.2f}x | hold {a.a} {r['hold_A_usd_x']:.2f}x | hold {a.b} {r['hold_B_usd_x']:.2f}x")
    print(f"  in {a.a}-share units: rotator {r['rotator_A_units']:.2f} | hold {a.a} 1.00 | hold {a.b} {r['hold_B_A_units']:.2f}")
    return 0


def cmd_ingest_ratios(a) -> int:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(a.file, newline="") as f:
        rows = [{**r, "ingested_at": now} for r in csv.DictReader(f)]
    print(f"appended {store.append_csv(Path(a.data) / 'ratios.csv', RATIO_FIELDS, rows)} ratio rows")
    return 0


def cmd_ingest_prices(a) -> int:
    path = Path(a.data) / "prices" / f"{a.ticker.upper()}.csv"
    have = dict(store.load_prices(path, date.max)) if path.exists() else {}
    new = dict(store.load_prices(Path(a.file), date.max))
    merged = {**have, **new}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "close"])
        w.writerows(sorted(merged.items()))
    print(f"{path.name}: {len(merged)} closes ({len(new)} from file)")
    return 0


def cmd_ingest_estimates(a) -> int:
    with open(a.file, newline="") as f:
        rows = list(csv.DictReader(f))
    bad = [r for r in rows if r.get("kind") not in store.KIND_PRIORITY or not r.get("as_of") or not r.get("source")]
    if bad:
        print(f"rejected: {len(bad)} rows lack kind/as_of/source (provenance is mandatory)", file=sys.stderr)
        return 2
    print(f"appended {store.append_csv(Path(a.data) / 'estimates.csv', store.EST_FIELDS, rows)} estimate rows")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="rotation")
    ap.add_argument("--data", default=str(DEFAULT_DATA))
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("--asof"); r.add_argument("--hold")
    r.add_argument("--horizon", type=int, default=12); r.add_argument("--hurdle", type=float, default=0.08)
    r.add_argument("--rate-shock-bp", type=float, default=0.0, help="parallel rate shock applied to all multiples via equity duration")
    r.add_argument("--erp", type=float, default=0.045, help="equity risk premium for the implied-expectations discount rate")
    r.add_argument("--g-term", type=float, default=0.03); r.add_argument("--years", type=int, default=10)
    r.add_argument("--tax", type=float, default=0.0); r.add_argument("--cost", type=float, default=0.002)
    r.add_argument("--rerate", nargs="*", default=[], help="TICKER=1.10 expected re-rating factor")
    r.set_defaults(fn=cmd_report)
    for nm, fn in (("swap", cmd_swap), ("rebalance", cmd_rebalance)):
        s = sub.add_parser(nm); s.set_defaults(fn=fn)
        s.add_argument("--asof"); s.add_argument("--horizon", type=int, default=12)
        s.add_argument("--hurdle", type=float, default=0.08); s.add_argument("--tax", type=float, default=0.0)
        s.add_argument("--cost", type=float, default=0.002)
        if nm == "swap":
            s.add_argument("src", help="ticker you hold and are considering selling")
        else:
            s.add_argument("--max-weight", type=float, default=0.5); s.add_argument("--band", type=float, default=0.10)
            s.add_argument("--stage", type=float, default=0.33); s.add_argument("--record", action="store_true", help="append paper trades to ledger.csv")
    s = sub.add_parser("anchors"); s.set_defaults(fn=cmd_anchors)
    s.add_argument("--asof"); s.add_argument("--horizon", type=int, default=12)
    s.add_argument("--w-f", type=float, default=0.5); s.add_argument("--w-i", type=float, default=0.3); s.add_argument("--w-r", type=float, default=0.2)
    s.add_argument("--rerate", type=float, default=0.0, help="fraction of the way multiples move toward their historical TRAILING P/E quartiles (default 0 = off)")
    s.add_argument("--band", type=float, default=None, help="multiple compression/expansion band; default auto = realised horizon vol clamped to 15-50%%"); s.add_argument("--lam", type=float, default=0.25, help="ratio reversion fraction")
    s.add_argument("--write", action="store_true", help="append blended targets to targets.csv")
    s = sub.add_parser("profile"); s.set_defaults(fn=cmd_profile)
    s.add_argument("--asof"); s.add_argument("--no-provisional", action="store_true")
    s.add_argument("--hurdle", type=float, default=0.08); s.add_argument("--cost", type=float, default=0.002)
    s = sub.add_parser("cohort"); s.set_defaults(fn=cmd_cohort); s.add_argument("--only", help="comma list of tickers to print")
    s = sub.add_parser("compare"); s.set_defaults(fn=cmd_compare); s.add_argument("--a", default="fri_close"); s.add_argument("--b", default="mon_high"); s.add_argument("--out")
    s = sub.add_parser("multiples"); s.set_defaults(fn=cmd_multiples); s.add_argument("--asof"); s.add_argument("--out")
    s = sub.add_parser("models"); s.set_defaults(fn=cmd_models)
    s = sub.add_parser("simulate"); s.set_defaults(fn=cmd_simulate)
    s.add_argument("a"); s.add_argument("b"); s.add_argument("--asof"); s.add_argument("--lookback", type=int, default=60)
    s.add_argument("--band", type=float, default=0.10); s.add_argument("--cost", type=float, default=0.002)
    for n, fn in (("ingest-ratios", cmd_ingest_ratios), ("ingest-estimates", cmd_ingest_estimates)):
        s = sub.add_parser(n); s.add_argument("file"); s.set_defaults(fn=fn)
    s = sub.add_parser("ingest-prices"); s.add_argument("ticker"); s.add_argument("file"); s.set_defaults(fn=cmd_ingest_prices)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
