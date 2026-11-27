"""Tape facts from daily bars: lowest lows, drawdowns and volume context. Facts only; no forecasts."""
from __future__ import annotations

WINDOW = 252  # trading days ~ 52 weeks


def tape_stats(bars: list[dict], window: int = WINDOW) -> dict | None:
    """Window low/high, all-history lowest low, volume vs prior 20/50-day averages. Needs >= 21 bars.

    Volume averages EXCLUDE the last bar so a spike day is compared with its own baseline.
    """
    if len(bars) < 21:
        return None
    last, prior, win = bars[-1], bars[:-1], bars[-window:]
    lo = min(win, key=lambda b: b["low"])
    hi = max(win, key=lambda b: b["high"])
    ever = min(bars, key=lambda b: b["low"])
    heavy = max(bars, key=lambda b: b["volume"])
    v20 = sum(b["volume"] for b in prior[-20:]) / len(prior[-20:])
    v50 = sum(b["volume"] for b in prior[-50:]) / len(prior[-50:])
    chg1 = last["close"] / prior[-1]["close"] - 1
    ret = lambda n: last["close"] / bars[-1 - n]["close"] - 1 if len(bars) > n else None
    flags = []
    if last["low"] <= lo["low"] * 1.0000001:
        flags.append("TAPE:NEW_52W_LOW")
    elif last["close"] <= lo["low"] * 1.02:
        flags.append("TAPE:NEAR_52W_LOW")
    if last["volume"] > 2 * v20:
        flags.append("TAPE:HEAVY_VOLUME")
    if chg1 <= -0.10:
        flags.append("TAPE:GAP_DOWN_10PCT")
    return {
        "as_of": last["date"], "close": last["close"], "chg_1d": chg1, "ret_5d": ret(5), "ret_10d": ret(10),
        "low_win": lo["low"], "low_win_date": lo["date"], "low_win_vol": lo["volume"],
        "high_win": hi["high"], "high_win_date": hi["date"],
        "pct_above_low": last["close"] / lo["low"] - 1, "pct_below_high": last["close"] / hi["high"] - 1,
        "low_ever": ever["low"], "low_ever_date": ever["date"], "first_bar": bars[0]["date"], "n": len(bars),
        "vol_last": last["volume"], "vol_20d": v20, "vol_50d": v50, "vol_ratio_20d": last["volume"] / v20,
        "vol_max": heavy["volume"], "vol_max_date": heavy["date"], "flags": flags,
    }
