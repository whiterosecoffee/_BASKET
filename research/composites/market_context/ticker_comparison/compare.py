"""Small research consumer of B17 change(); no provider, store, or live adapter."""
import argparse
import csv
import hashlib
import itertools
import json
import math
import statistics
from datetime import date, datetime, timezone
from pathlib import Path
from types import ModuleType
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
TICKERS = ("NVDA", "CRWV", "SMH", "QQQ")
# Preserve the original capture's replay while accepting the reviewed freshness
# repair now on main. New versions still need an explicit reviewed identity.
CONTEXT_BLOBS = frozenset({
    "bc64d48b690c36934e536a0e82644c61da95f0c5",  # original PR101 capture
    "97fcef9eb54dc3589ec5d958e151599c21ea987a",  # PR101 freshness repair
})


def context_change(path):
    data = Path(path).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if blob not in CONTEXT_BLOBS:
        raise ValueError("B17 dependency differs from pinned PR101 source blob")
    module = ModuleType("basket_context_101")
    module.__file__ = str(path)
    # Execute the checked bytes, not a second read or a cached bytecode file.
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module.change


def compare(rows, cutoff, evaluated_at, change, windows=(1, 5, 20, 60), correlation_window=60):
    """Same union-date window for every ticker. Missing prices are never filled.

    This is a current-revision historical diagnostic. Provider first availability
    and revision vintages are unknown, so it is not a point-in-time backtest.
    Calendar completeness is not asserted merely because every ticker aligns.
    """
    cutoff = date.fromisoformat(cutoff)
    evaluated = datetime.fromisoformat(evaluated_at.replace("Z", "+00:00"))
    if evaluated.utcoffset() is None or cutoff >= evaluated.astimezone(ET).date():
        raise ValueError("Use a previous completed date and timezone-aware evaluation")
    if any(type(n) is not int or n < 1 for n in (*windows, correlation_window)):
        raise ValueError("Positive integer windows required")
    parsed = []
    for raw in rows:
        stamp = datetime.fromtimestamp(int(raw["t"]) / 1000, timezone.utc).astimezone(ET)
        if stamp.hour or stamp.minute or stamp.second or stamp.microsecond:
            raise ValueError("Daily input must start at midnight Eastern Time")
        day = stamp.date()
        if day > cutoff or (parsed and day <= parsed[-1][0]):
            raise ValueError("Future, duplicate, or out-of-order date")
        prices = {}
        for ticker in TICKERS:
            value = raw.get(ticker)
            if value is None or value == "":
                prices[ticker] = None
            else:
                if isinstance(value, bool):
                    raise ValueError("Invalid price")
                value = float(value)
                if not math.isfinite(value) or value <= 0:
                    raise ValueError("Positive finite prices required")
                prices[ticker] = value
        parsed.append((day, prices))
    if not parsed or parsed[-1][0] != cutoff:
        raise ValueError("Requested cutoff date is absent; do not silently roll backward")
    periods = []
    for n in windows:
        sample = parsed[-n-1:]
        enough = len(sample) == n + 1
        returns = {t: change(sample[-1][1][t], sample[0][1][t])
                   if enough and all(r[1][t] is not None for r in sample) else None
                   for t in TICKERS}
        benchmark = returns["QQQ"]
        periods.append({"sessions": n, "start": sample[0][0].isoformat() if enough else None,
                        "end": cutoff.isoformat(), "price_return_pct": returns,
                        "relative_to_qqq_pp": {t: r-benchmark if r is not None and benchmark is not None else None
                                               for t, r in returns.items()}})
    sample = parsed[-correlation_window-1:]
    correlations = []
    for a, b in itertools.combinations(TICKERS, 2):
        pairs = [(change(right[1][a], left[1][a]), change(right[1][b], left[1][b]))
                 for left, right in zip(sample, sample[1:])
                 if all(r[1][t] is not None for r in (left, right) for t in (a, b))]
        complete = len(pairs) == correlation_window
        x, y = zip(*pairs) if pairs else ((), ())
        varying = len(pairs) > 1 and len(set(x)) > 1 and len(set(y)) > 1
        correlations.append({"a": a, "b": b, "paired_returns": len(pairs),
                             "pearson": statistics.correlation(x, y) if complete and varying else None,
                             "status": "complete" if complete and varying else
                                       "constant_series" if complete else "insufficient_paired_returns"})
    return {"schema": "basket.ticker_comparison_research@1", "currency": "USD",
            "price_cutoff_date": cutoff.isoformat(), "evaluated_at": evaluated_at,
            "replay_class": "current_revision_historical_diagnostic",
            "return_basis": "split_adjusted_price_return_not_total_return",
            "dates_supplied": len(parsed),
            "complete_common_dates": sum(all(p[t] is not None for t in TICKERS) for _, p in parsed),
            "missing_prices": {t: sum(p[t] is None for _, p in parsed) for t in TICKERS},
            "calendar_completeness": "not_independently_certified",
            "windows": periods,
            "correlation_window": {"requested_returns": correlation_window,
                "start": sample[0][0].isoformat(), "end": cutoff.isoformat(),
                "method": "Pearson correlation of arithmetic daily price returns, not price levels",
                "pairs": correlations}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="Private aligned t,NVDA,CRWV,SMH,QQQ input")
    parser.add_argument("--context-module", required=True, help="Read-only PR101 context.py")
    parser.add_argument("--cutoff", required=True)
    parser.add_argument("--evaluated-at", required=True)
    args = parser.parse_args()
    with open(args.csv, newline="") as handle:
        result = compare(list(csv.DictReader(handle)), args.cutoff, args.evaluated_at,
                         context_change(args.context_module))
    print(json.dumps(result, indent=2, allow_nan=False))
