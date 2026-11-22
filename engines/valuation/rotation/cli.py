"""python -m engines.valuation.rotation.cli {report,ingest-ratios,ingest-prices,ingest-estimates} ..."""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from . import store
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
    ys = load_yields(data / "macro" / "treasury_yields.csv", asof)
    if ys:
        (d1, a), (d0, b) = ys[-1], ys[max(0, len(ys) - 6)]
        print(f"\nRATES {d1}: 2y {a['yield_2_year']}  10y {a['yield_10_year']}  30y {a['yield_30_year']}  "
              f"(vs {d0}: 10y {float(a['yield_10_year'])-float(b['yield_10_year']):+.2f}pp, 2y {float(a['yield_2_year'])-float(b['yield_2_year']):+.2f}pp)")
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
    r.add_argument("--tax", type=float, default=0.0); r.add_argument("--cost", type=float, default=0.002)
    r.add_argument("--rerate", nargs="*", default=[], help="TICKER=1.10 expected re-rating factor")
    r.set_defaults(fn=cmd_report)
    for n, fn in (("ingest-ratios", cmd_ingest_ratios), ("ingest-estimates", cmd_ingest_estimates)):
        s = sub.add_parser(n); s.add_argument("file"); s.set_defaults(fn=fn)
    s = sub.add_parser("ingest-prices"); s.add_argument("ticker"); s.add_argument("file"); s.set_defaults(fn=cmd_ingest_prices)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
