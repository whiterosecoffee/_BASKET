"""Point-in-time loaders. Inputs are append-only CSVs; nothing is read that was unknown at `as_of`."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

KIND_PRIORITY = ("actual", "consensus", "house", "guidance")
EST_FIELDS = ["ticker", "metric", "fiscal_year", "value", "basis", "kind", "source", "as_of", "fye_month", "currency"]


def d(s: str) -> date:
    return date.fromisoformat(s[:10])


@dataclass
class Est:
    ticker: str
    metric: str
    fy: int
    value: float
    basis: str
    kind: str
    source: str
    as_of: date
    fye_month: int


def _rows(path: Path):
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return [r for r in csv.DictReader(f) if r and r.get(next(iter(r)), "").strip()
                and not r[next(iter(r))].startswith("#")]


def load_estimates(path: Path, as_of: date, prefer=KIND_PRIORITY) -> dict[tuple[str, str], dict[int, Est]]:
    """Latest estimate known at as_of per (ticker, metric, fy); higher-priority kind wins ties on freshness class."""
    best: dict[tuple[str, str, int], Est] = {}
    for r in _rows(path):
        e = Est(r["ticker"].upper(), r["metric"], int(r["fiscal_year"]), float(r["value"]),
                r.get("basis") or "non_gaap", r["kind"], r.get("source", ""), d(r["as_of"]),
                int(r.get("fye_month") or 12))
        if e.as_of > as_of or e.kind not in prefer:
            continue
        k = (e.ticker, e.metric, e.fy)
        cur = best.get(k)
        rank = lambda x: (prefer.index(x.kind), -x.as_of.toordinal())
        if cur is None or rank(e) < rank(cur):
            best[k] = e
    out: dict[tuple[str, str], dict[int, Est]] = {}
    for (t, m, y), e in best.items():
        out.setdefault((t, m), {})[y] = e
    return out


def load_ratios(path: Path, as_of: date) -> dict[str, dict]:
    """Latest Massive /stocks/financials/v1/ratios row per ticker with date <= as_of."""
    snap: dict[str, dict] = {}
    for r in _rows(path):
        if d(r["date"]) > as_of:
            continue
        t = r["ticker"].upper()
        if t not in snap or r["date"] >= snap[t]["date"]:
            snap[t] = {**r, "price": float(r["price"]), "market_cap": float(r["market_cap"]),
                       "enterprise_value": float(r["enterprise_value"] or 0) or None,
                       "asof": d(r["date"])}
    return snap


def load_prices(path: Path, as_of: date) -> list[tuple[date, float]]:
    """Daily closes from `date,close` or raw Massive aggs (`t` ms, `c`)."""
    out = []
    for r in _rows(path):
        if "t" in r and "c" in r:
            dt = datetime.fromtimestamp(int(float(r["t"])) / 1000, tz=timezone.utc).date()
            px = float(r["c"])
        else:
            dt, px = d(r["date"]), float(r["close"])
        if dt <= as_of:
            out.append((dt, px))
    return sorted(set(out))


def load_bars(path: Path, as_of: date) -> list[dict]:
    """Daily OHLCV bars (date,open,high,low,close,volume) known at as_of, oldest first."""
    out = []
    for r in _rows(path):
        if "low" not in r or d(r["date"]) > as_of:
            continue
        out.append({"date": d(r["date"]), **{k: float(r[k]) for k in ("open", "high", "low", "close", "volume")}})
    return sorted(out, key=lambda b: b["date"])


def load_guidance(path: Path, as_of: date) -> dict[tuple[str, str], dict]:
    """Latest company guidance per (ticker, metric) known at as_of. Per-share values are split-adjusted to today's shares."""
    out: dict[tuple[str, str], dict] = {}
    for r in _rows(path):
        if d(r["as_of"]) > as_of:
            continue
        k = (r["ticker"].upper(), r["metric"])
        if k not in out or r["as_of"] >= out[k]["as_of_s"]:
            sp = float(r.get("split_factor") or 1) if r["metric"] == "eps" else 1.0
            lo, hi = float(r["low"]) / sp, float(r["high"]) / sp
            out[k] = {"period": r["period"], "low": lo, "high": hi, "mid": (lo + hi) / 2, "annualize": float(r["annualize"] or 1),
                      "basis": r["basis"], "source": r["source"], "as_of": d(r["as_of"]), "as_of_s": r["as_of"]}
    return out


def load_events(path: Path, as_of: date) -> dict[str, date]:
    """Next earnings date on/after as_of per ticker."""
    nxt: dict[str, date] = {}
    for r in _rows(path):
        dt = d(r["date"])
        if dt >= as_of and (r["ticker"].upper() not in nxt or dt < nxt[r["ticker"].upper()]):
            nxt[r["ticker"].upper()] = dt
    return nxt


def load_positions(path: Path) -> dict[str, dict]:
    return {r["ticker"].upper(): {"entry_price": float(r["entry_price"]), "entry_date": r.get("entry_date", "")}
            for r in _rows(path)}


def append_csv(path: Path, fields: list[str], rows: list[dict]) -> int:
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerows(rows)
    return len(rows)
