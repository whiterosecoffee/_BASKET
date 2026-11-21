#!/usr/bin/env python3
"""Strict, research-only B19 candidate and optional baseline-registry checker."""
import argparse
from datetime import date
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SYMBOL = re.compile(r"^[A-Z][A-Z0-9]*(?:[.-][A-Z0-9]+)*$")
DATE = re.compile(r"^20[0-9]{2}-[01][0-9]-[0-3][0-9]$")
PRIORITY = {"P0", "P1", "P2"}
FORBIDDEN = {"live_price", "price_now", "verified_current_price", "market_share", "valuation_usd"}

class CoverageError(ValueError):
    pass

def fail(message):
    raise CoverageError(message)

def date_from_iso(value):
    return date.fromisoformat(value)

def symbols(records, label):
    seen = set()
    if not isinstance(records, list) or not records:
        fail(f"{label}: expected nonempty list")
    for n, record in enumerate(records):
        if not isinstance(record, dict):
            fail(f"{label}[{n}]: not an object")
        ticker = record.get("ticker") if label == "candidates" else record.get("entity_id")
        if not isinstance(ticker, str) or not SYMBOL.fullmatch(ticker):
            fail(f"{label}[{n}]: invalid identifier {ticker!r}")
        if ticker in seen:
            fail(f"{label}: duplicate {ticker}")
        seen.add(ticker)
    return seen

def check(candidate_doc, registry_doc=None):
    if not isinstance(candidate_doc, dict):
        fail("candidate document is not an object")
    if candidate_doc.get("schema") != "basket.b19-underrepresented-coverage@1":
        fail("unsupported research schema")
    candidates = candidate_doc.get("candidates")
    ids = symbols(candidates, "candidates")
    for row in candidates:
        symbol = row["ticker"]
        if row.get("status") != "research_candidate" or row.get("canonical_membership") != "not_checked":
            fail(f"{symbol}: canonical or nonresearch promotion")
        if row.get("financial_metrics") != "not_ingested":
            fail(f"{symbol}: unverified financial payload")
        if row.get("priority") not in PRIORITY or not isinstance(row.get("layer"), str) or not row["layer"]:
            fail(f"{symbol}: invalid priority/layer")
        if FORBIDDEN.intersection(row):
            fail(f"{symbol}: unsourced live/valuation fields")
        evidence = row.get("evidence")
        if not isinstance(evidence, list):
            fail(f"{symbol}: evidence must be list")
        for entry in evidence:
            if not isinstance(entry, dict) or not isinstance(entry.get("class"), str) or not isinstance(entry.get("claim"), str):
                fail(f"{symbol}: invalid evidence")
            url = entry.get("url")
            parsed = urlparse(url) if isinstance(url, str) else None
            if not parsed or parsed.scheme != "https" or not parsed.netloc:
                fail(f"{symbol}: invalid evidence URL")
            date = entry.get("published_at")
            if date is not None:
                if not isinstance(date, str) or not DATE.fullmatch(date):
                    fail(f"{symbol}: malformed publication date")
                try:
                    parsed_date = date_from_iso(date)
                    as_of = date_from_iso(candidate_doc["as_of"])
                except (ValueError, KeyError, TypeError):
                    fail(f"{symbol}: invalid publication/cutoff date")
                if parsed_date > as_of:
                    fail(f"{symbol}: publication after research cutoff")
    result = {"candidates": len(ids), "candidate_symbols": sorted(ids), "canonical_promotion": False}
    if registry_doc is not None:
        if not isinstance(registry_doc, dict) or "tickers" not in registry_doc:
            fail("invalid baseline registry")
        baseline = symbols(registry_doc["tickers"], "tickers")
        overlap = ids & baseline
        if overlap:
            fail("research candidate duplicates baseline: " + ",".join(sorted(overlap)))
        if any(row.get("not_in_b19_working_watchlist") is not True for row in candidates):
            fail("membership assertion disagrees with baseline")
        result.update({"baseline": len(baseline), "overlap": 0, "combined": len(baseline | ids)})
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", type=Path)
    parser.add_argument("--registry", type=Path, help="Optional B19 PR #18 research registry")
    args = parser.parse_args(argv)
    try:
        candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
        baseline = json.loads(args.registry.read_text(encoding="utf-8")) if args.registry else None
        print(json.dumps(check(candidates, baseline), sort_keys=True))
        return 0
    except (CoverageError, OSError, json.JSONDecodeError, TypeError, AttributeError) as exc:
        print(f"COVERAGE FAIL: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
