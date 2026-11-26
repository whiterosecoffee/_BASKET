"""Presentation math for captured Massive premarket snapshots and 15m bars."""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def percent(value, base):
    return round(100 * (value / base - 1), 4) if base > 0 else None


def build(snapshot, bars, as_of, config):
    cutoff = dt.datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    if cutoff.tzinfo is None:
        raise ValueError("as-of must include timezone")
    eastern = ZoneInfo(config["session_timezone"])
    day = cutoff.astimezone(eastern).date()
    quotes = {row["ticker"]: row for row in csv.DictReader(snapshot.open())}
    instruments = list(dict.fromkeys(t for group in config["roles"].values() for t in group))
    result = []
    for ticker in instruments:
        row = quotes.get(ticker)
        item = {"ticker": ticker, "quote_status": "missing" if row is None else "freshness_unverified"}
        if row is not None and row.get("session_price"):
            price = float(row["session_price"])
            item.update(price=price, prior_close_pct=percent(price, float(row["session_previous_close"])),
                        source_time=row.get("last_trade_last_updated"), session=row.get("market_status"))
        windows = []
        path = bars / (ticker + ".csv")
        if path.exists():
            for bar in csv.DictReader(path.open()):
                start = dt.datetime.fromtimestamp(int(bar["t"]) / 1000, eastern)
                if start.date() != day or not dt.time(4) <= start.time() < dt.time(9, 30):
                    continue
                if start > cutoff:
                    continue
                if start.minute % 15 or start.second:
                    raise ValueError("input must contain aligned 15-minute bars")
                windows.append({"start_et": start.isoformat(), "high": float(bar["h"]),
                                "low": float(bar["l"]), "close": float(bar["c"]),
                                "volume": float(bar["v"]),
                                "partial": start + dt.timedelta(minutes=15) > cutoff})
        item["windows"] = windows
        if windows and "price" in item:
            item.update(from_premarket_peak_pct=percent(item["price"], max(w["high"] for w in windows)),
                        from_premarket_low_pct=percent(item["price"], min(w["low"] for w in windows)))
        result.append(item)
    return {"config_version": config["version"], "as_of": cutoff.isoformat(),
            "exchange_date": str(day), "instruments": result,
            "news_status": "not_checked", "freshness_status": "requires_existing_context_engine"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--bars", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args()
    config = json.loads(Path(__file__).with_name("universe.json").read_text())
    print(json.dumps(build(args.snapshot, args.bars, args.as_of, config), indent=2))
