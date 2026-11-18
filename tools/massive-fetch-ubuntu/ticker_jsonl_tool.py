#!/usr/bin/env python3
"""Standing process for the per-ticker .jsonl stock-basket stores:
CRUD + gap analysis + QA.

Lives alongside the data it operates on, not in the `prompts` repo --
this data and its tooling are their own thing, headed for their own repo
later, not a part of that project.

STORES
------
Each store is one directory of one <TICKER>.jsonl file per ticker, rows
sorted by `t` ascending, no duplicate `t`:

  Massive-daily/          bar,    grain=1day, src=massive-aggs-v2-1day
  basket-parts-minute/    bar,    grain=1min, src=massive-aggs-v2-1min
  snap-v1-minute-moment/  moment, grain=1min, src=massive-rest-v2

Bar row    (OHLC):     ticker, t, ts, px, vol, o, h, l, c, vw, n, src, class, grain
Moment row (price pt): ticker, t, ts, px, vol, src, class, grain

CRUD -- one ticker's file at a time
------------------------------------
InitializeTickerFile(store, ticker, rows)
    First-time creation of a ticker's file. Fails loudly (FileExistsError)
    if the file is already there, so a typo'd re-run can never silently
    clobber real history -- use AppendNewBars for every call after the
    first.

AppendNewBars(store, ticker, new_rows)
    The steady-state "fetched more data, add it" operation. Only adds
    rows whose `t` isn't already in the file; a `t` that's already present
    is left completely untouched, so calling this twice with overlapping
    data is always safe (idempotent) and this function can never be used
    to silently correct an existing row -- that's ReviseExistingBar's job,
    on purpose, so a code-review of "what changed" can tell the difference
    between new history arriving and old history being corrected.

LoadTickerHistory(store, ticker)
    Read every row for a ticker, already sorted by `t`. Returns `[]` for a
    ticker with no file yet rather than raising, since "nothing recorded
    yet" is a normal state to ask about, not an error.

ReviseExistingBar(store, ticker, t, corrected_row)
    Overwrite the one existing row at `t` -- the vendor restated a bar
    (a late print correction), not "we have new data." Raises KeyError if
    `t` isn't already present, since a revision to a bar that was never
    recorded is actually a missed AppendNewBars, not a revision.

RemoveBar(store, ticker, t)
    Delete exactly one row by its `t`. Does not touch the rest of the
    file. For removing a single bad/erroneous data point -- always a rare,
    deliberate action, never part of routine ingestion.

RetireTickerFile(store, ticker)
    Delete the entire file for a ticker (the ticker was wrong, delisted,
    or the file needs to be rebuilt from scratch via InitializeTickerFile).
    Split out from RemoveBar on purpose -- "delete one data point" and
    "delete this ticker's entire history" are different enough in blast
    radius that they should never share one function signature where a
    missing/None argument silently picks the destructive one.

ListTickersInStore(store)
    The tickers that currently have a file in a given store, sorted.

QUALITY CHECKS -- five named, independently answerable questions
--------------------------------------------------------------------
("QA" alone didn't say what was being tested; these do.)

CheckRequiredFieldsPresent(rows, shape)        -- does every row have every field its shape requires?
CheckTickerFieldMatchesFilename(rows, ticker)  -- does every row's own ticker field match the file?
CheckChronologicalOrderNoDuplicates(rows)      -- is t strictly increasing, zero duplicates?
CheckBarPriceConsistency(rows, shape)          -- (bar only) l<=min(o,c), h>=max(o,c), px==c?
CheckForBlankOrMissingValues(rows, shape, ticker) -- is any required field null/""/NaN?
                                                      (distinct from AnalyzeTradingDayCoverage:
                                                      this is blank DATA INSIDE rows we have;
                                                      that is MISSING WHOLE DAYS we don't.)
ValidateTickerQuality(store, ticker)           -- runs all five, keyed by check name.

SANITIZE / STANDARDIZE -- fixes representation, never fabricates data
--------------------------------------------------------------------
SanitizeRow(row, shape)                        -- "" -> null, numeric-string -> number,
                                                     trims string fields. Never invents a
                                                     value for a genuinely missing tick.
StandardizeTickerFile(store, ticker, dry_run)  -- SanitizeRow over a whole ticker file,
                                                     rewrites it, reports every change made.
StandardizeAllTickersInStore(store, dry_run)   -- drives StandardizeTickerFile across a
                                                     whole store, one ticker at a time.

QUALITY AND COVERAGE -- per ticker, then audited across a whole store
------------------------------------------------------------------------
ValidateTickerQuality(store, ticker)
    Schema-shape, ordering, and sanity checks for one ticker's file:
    every row has the fields its store shape requires; `ticker` field
    matches the filename; `t` is strictly increasing with no duplicates;
    for bar rows, `l <= min(o,c)`, `h >= max(o,c)`, and `px == c` (the
    same identities the original Massive/daily conversion verified).
    Returns a problem list, empty when clean -- never raises, since a QA
    pass should report every issue it finds in one run, not stop at the
    first one.

AnalyzeTradingDayCoverage(store, ticker, window_start, window_end)
    Builds the real NYSE trading-day calendar for the window (weekdays
    minus holidays -- New Year's, MLK, Presidents, Good Friday, Memorial
    Day, Juneteenth, Independence Day, Labor Day, Thanksgiving, Christmas,
    each with weekend-observed shifting), and diffs it against the set of
    trading days this ticker's file actually has a row on (derived from
    each row's `ts` date, not a minute-by-minute density check -- see
    note below). Reports missing days, not just a missing count, so a
    downstream fetch plan can be built directly from the result.

    Deliberately day-level, not minute-level: a 24-month, ~350-ticker,
    ~390-minutes-per-session density check is a different, much larger
    question ("how complete is each traded minute") than this one ("does
    this ticker have the day at all") -- conflating them would hide a
    100%-day-coverage, mostly-untraded-minutes ticker and a genuinely
    missing week behind the same number.

EvaluateTicker(store, ticker, window_start, window_end, force=False)
    Runs ValidateTickerQuality + AnalyzeTradingDayCoverage for one ticker
    and persists the combined result immediately under
    `_qa-gap-results/<store>/<ticker>.json`. Skips re-computation if that
    result file already exists, unless `force=True` -- this is what makes
    RunCoverageAudit resumable: an interrupted run picks back up without
    redoing finished tickers.

RunCoverageAudit(months=24, stores=None, force=False)
    Drives EvaluateTicker across every ticker in the given store(s)
    (default: all three), **one ticker at a time**, printing progress
    every 25 tickers. Never holds more than one ticker's rows in memory
    at once -- this is the standing protocol for QA/coverage work on
    these stores, chosen specifically over a single monolithic
    read-everything pass, which does not scale past one store before it
    becomes a multi-minute black box with no visible progress and no
    partial result if it's interrupted.

SummarizeCoverageAudit()
    Aggregates the small per-ticker result files RunCoverageAudit already
    wrote into one report per store: tickers processed, total
    expected/missing ticker-days, coverage percentage, every ticker with
    a QA problem, and the 15 tickers with the worst gaps. Reads only
    those small result files, never the underlying multi-gigabyte data
    files again -- aggregation should be fast and repeatable without
    re-paying the cost of the audit itself.
"""
from __future__ import annotations
import json, os, glob
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
# Where the central per-ticker files live. Override with TICKER_DATA_ROOT; the default is
# the sibling data folder after the project was reorganised into separate concerns.
DATA_DIR = os.environ.get("TICKER_DATA_ROOT") or os.path.join(ROOT, "_DATA Ticker Basket")
STORES = {
    "Massive-daily": {"shape": "bar", "grain": "1day"},
    "basket-parts-minute": {"shape": "bar", "grain": "1min"},
    "snap-v1-minute-moment": {"shape": "moment", "grain": "1min"},
}
# The merged, cross-store, one-file-per-ticker view (see MergeAllTickersAcrossStores
# below). "shape": "bar" because the merged row is always the union schema (moment rows
# just carry null o/h/l/c/vw/n) -- callers should branch on each row's own "class", not
# on this store's declared shape, the way CheckBarPriceConsistency already does.
MERGED_STORE = "tickers"
STORES[MERGED_STORE] = {"shape": "bar", "grain": "mixed"}
SOURCE_STORES = ["Massive-daily", "basket-parts-minute", "snap-v1-minute-moment"]

BAR_FIELDS = ["ticker", "t", "ts", "px", "vol", "o", "h", "l", "c", "vw", "n", "src", "class", "grain"]
MOMENT_FIELDS = ["ticker", "t", "ts", "px", "vol", "src", "class", "grain"]
RESULTS_DIR = os.path.join(ROOT, "_TOOL Perform Gap Analysis", "per-ticker-legacy")


# ---------- NYSE trading calendar ----------

def _nth_weekday(year, month, weekday, n):
    """The date of the n-th given weekday (0=Mon) in a month, e.g. 3rd Monday of January."""
    d = date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    return d + timedelta(days=offset + 7 * (n - 1))

def _last_weekday(year, month, weekday):
    """The date of the last given weekday (0=Mon) in a month, e.g. last Monday of May."""
    d = date(year, 12, 31) if month == 12 else date(year, month + 1, 1) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)

def _easter(year):
    """Gregorian Easter Sunday (Gauss's algorithm) -- Good Friday is 2 days before this."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def nyse_holidays(year):
    """The 10 fixed/floating NYSE market holidays for a calendar year, weekend-observed-shifted."""
    def observed(d):
        if d.weekday() == 5: return d - timedelta(days=1)  # Sat holiday observed Fri
        if d.weekday() == 6: return d + timedelta(days=1)  # Sun holiday observed Mon
        return d
    return {
        observed(date(year, 1, 1)), _nth_weekday(year, 1, 0, 3), _nth_weekday(year, 2, 0, 3),
        _easter(year) - timedelta(days=2), _last_weekday(year, 5, 0), observed(date(year, 6, 19)),
        observed(date(year, 7, 4)), _nth_weekday(year, 9, 0, 1), _nth_weekday(year, 11, 3, 4),
        observed(date(year, 12, 25)),
    }

def expected_trading_days(start: date, end: date):
    """Every NYSE trading day (weekday, non-holiday) in [start, end], inclusive."""
    holidays = set()
    for y in range(start.year, end.year + 1):
        holidays |= nyse_holidays(y)
    out, d = [], start
    while d <= end:
        if d.weekday() < 5 and d not in holidays:
            out.append(d)
        d += timedelta(days=1)
    return out


# ---------- CRUD ----------

def _store_dir(store):
    return DATA_DIR if store == MERGED_STORE else os.path.join(ROOT, store)

def _path(store, ticker):
    return os.path.join(_store_dir(store), "%s.jsonl" % ticker)

def LoadTickerHistory(store, ticker):
    """Read a ticker's full row list, sorted by t. [] if the file doesn't exist yet."""
    p = _path(store, ticker)
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]

def _write_all(store, ticker, rows):
    """Atomic full rewrite: sort by t, write to a .tmp file, then rename over the real one."""
    rows = sorted(rows, key=lambda r: r["t"])
    p = _path(store, ticker)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    os.replace(tmp, p)

def InitializeTickerFile(store, ticker, rows):
    """Create a brand-new ticker file. Raises FileExistsError if one is already there --
    use AppendNewBars for every subsequent call. Returns the row count written."""
    p = _path(store, ticker)
    if os.path.exists(p):
        raise FileExistsError("InitializeTickerFile: %s/%s already exists -- use AppendNewBars" % (store, ticker))
    _write_all(store, ticker, rows)
    return len(rows)

def AppendNewBars(store, ticker, new_rows):
    """Add rows whose t isn't already present; rows with a t already on file are left
    untouched (idempotent -- safe to call repeatedly with overlapping fetches). Raises
    FileNotFoundError if the ticker has no file yet (use InitializeTickerFile first).
    Returns the count of rows actually added."""
    if not os.path.exists(_path(store, ticker)):
        raise FileNotFoundError("AppendNewBars: %s/%s does not exist -- use InitializeTickerFile" % (store, ticker))
    existing = {r["t"]: r for r in LoadTickerHistory(store, ticker)}
    added = 0
    for r in new_rows:
        if r["t"] not in existing:
            existing[r["t"]] = r
            added += 1
    _write_all(store, ticker, list(existing.values()))
    return added

def ReviseExistingBar(store, ticker, t, corrected_row):
    """Overwrite the one row at t with corrected_row -- for a vendor restatement of an
    already-recorded bar, never for adding data that wasn't there before. Raises KeyError
    if t isn't already present."""
    rows = {r["t"]: r for r in LoadTickerHistory(store, ticker)}
    if t not in rows:
        raise KeyError("ReviseExistingBar: t=%s not present for %s/%s" % (t, store, ticker))
    rows[t] = corrected_row
    _write_all(store, ticker, list(rows.values()))

def RemoveBar(store, ticker, t):
    """Delete exactly one row by its t. Leaves the rest of the file untouched."""
    rows = {r["t"]: r for r in LoadTickerHistory(store, ticker) if r["t"] != t}
    _write_all(store, ticker, list(rows.values()))

def RetireTickerFile(store, ticker):
    """Delete this ticker's entire file. Separate from RemoveBar on purpose: deleting one
    data point and deleting a whole ticker's history are different enough in blast radius
    that they should never share a signature where a missing argument picks the
    destructive one."""
    p = _path(store, ticker)
    if os.path.exists(p):
        os.remove(p)

def ListTickersInStore(store):
    """Tickers that currently have a file in this store, sorted."""
    return sorted(os.path.splitext(os.path.basename(f))[0]
                  for f in glob.glob(os.path.join(_store_dir(store), "*.jsonl")))


# ---------- cross-store merge: ONE central store, tickers/<TICKER>.jsonl ----------
# tickers/ is the one central location for all ticker data -- the three per-source
# folders (Massive-daily, basket-parts-minute, snap-v1-minute-moment) hold the raw
# vendor pulls that feed this merge, but a consumer of this data should only ever need
# to look in tickers/. Re-running the merge always regenerates a ticker's file from the
# three raw sources, never the other way around -- the raw stores are not deleted by
# this (pending separate confirmation once the merge is verified), they're just no
# longer "the" place to read from.
#
# "Finest grain available" means: pick ONE authoritative source PER CALENDAR DAY, by
# precedence, and take every row that source has for that day -- never keep two
# different grains covering the same day side by side (that's redundant, not a richer
# record: a day covered by 390 one-minute bars doesn't also need the single daily bar
# that summarizes the same session). Precedence, finest-and-fullest first:
#   1. basket-parts-minute   -- 1-minute bars, full OHLC: the richest signal available.
#   2. snap-v1-minute-moment -- 1-minute price-only snapshots: same grain as #1, used
#                                 only to fill a day #1 doesn't have at all.
#   3. Massive-daily          -- 1-day bars: used only as a last resort, for a day
#                                 neither minute-grain source covers at all.
# This also sidesteps the (t, src) collision problem entirely: because at most one
# source is ever used for a given day, there is never a second row competing for the
# same `t`.

MERGE_PRECEDENCE = ["basket-parts-minute", "snap-v1-minute-moment", "Massive-daily"]

def _normalize_to_merged_shape(row, source_shape):
    """Bar rows pass through unchanged. Moment rows are widened to the bar field
    superset with o/h/l/c/vw/n explicitly null -- not missing data, but "this class
    structurally has no OHLC," exactly like an index ticker's null vol/vw/n."""
    if source_shape == "bar":
        return dict(row)
    widened = {f: None for f in BAR_FIELDS}
    widened.update(row)
    return widened

def MergeTickerAcrossStores(ticker, force=False):
    """Builds/rebuilds tickers/<ticker>.jsonl as the ONE central record for this
    ticker: for every calendar day the ticker has data on anywhere, take all of that
    day's rows from the single highest-precedence source that covers it (see
    MERGE_PRECEDENCE above), never a mix of sources for the same day. Skips the
    rebuild if tickers/<ticker>.jsonl already exists, unless force=True.
    Returns {"ticker", "rows_written", "days_by_source": {store: day_count}}."""
    out_path = _path(MERGED_STORE, ticker)
    if os.path.exists(out_path) and not force:
        return {"ticker": ticker, "rows_written": None, "days_by_source": None, "skipped": True}

    rows_by_store = {}
    days_by_store = {}
    for store in MERGE_PRECEDENCE:
        rows = LoadTickerHistory(store, ticker)
        rows_by_store[store] = rows
        by_day = {}
        for r in rows:
            ts = r.get("ts")
            if ts:
                by_day.setdefault(ts[:10], []).append(r)
        days_by_store[store] = by_day

    claimed_days = set()
    merged_rows = []
    days_by_source_used = {}
    for store in MERGE_PRECEDENCE:  # precedence order: first claim wins each day
        shape = STORES[store]["shape"]
        by_day = days_by_store[store]
        new_days = [d for d in by_day if d not in claimed_days]
        if not new_days:
            continue
        days_by_source_used[store] = len(new_days)
        for d in new_days:
            claimed_days.add(d)
            merged_rows.extend(_normalize_to_merged_shape(r, shape) for r in by_day[d])

    merged_rows.sort(key=lambda r: r["t"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    _write_merged(out_path, merged_rows)
    return {"ticker": ticker, "rows_written": len(merged_rows), "days_by_source": days_by_source_used}

def _write_merged(out_path, rows):
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    os.replace(tmp, out_path)

def MergeAllTickersAcrossStores(force=False):
    """Drives MergeTickerAcrossStores over the union of every ticker appearing in any
    of the three raw source stores, one ticker at a time (same sequenced-protocol
    reasoning as RunCoverageAudit: bounded memory, resumable, visible progress) into
    the one central tickers/ store."""
    all_tickers = sorted(set().union(*(set(ListTickersInStore(s)) for s in SOURCE_STORES)))
    for i, tk in enumerate(all_tickers):
        result = MergeTickerAcrossStores(tk, force=force)
        if (i + 1) % 25 == 0 or (i + 1) == len(all_tickers):
            print("[tickers] %d/%d  last=%s" % (i + 1, len(all_tickers), result), flush=True)
    return {"tickers_merged": len(all_tickers)}


# ---------- quality checks (named, so "what does this test" is never a mystery) ----------
# "QA" was a meaningless bucket name -- these are the five concrete, independently
# answerable questions it used to hide. ValidateTickerQuality runs all five and returns
# the result keyed by check name, so a problem always says exactly which question failed.

# Fields that must never be null/blank regardless of ticker. vol/vw/n (bar) and vol
# (moment) are deliberately excluded here -- they are legitimately null for index
# tickers (no traded volume exists for an index) per Massive/daily/MANIFEST.md, so a
# null there is correct data, not a blank.
REQUIRED_NEVER_NULL = {
    "bar": ["ticker", "t", "ts", "px", "o", "h", "l", "c"],
    "moment": ["ticker", "t", "ts", "px"],
}
# Fields allowed to be null -- only meaningful for CheckForBlankOrMissingValues, which
# otherwise flags any null/empty-string value as a sanitization problem.
NULLABLE_FIELDS = {"bar": ["vol", "vw", "n"], "moment": ["vol"]}


def CheckRequiredFieldsPresent(rows, shape):
    """Does every row have every field its store shape requires (key present at all,
    regardless of value)? Returns a list of "row N missing fields: [...]" strings."""
    fields = BAR_FIELDS if shape == "bar" else MOMENT_FIELDS
    return ["row %d missing fields: %s" % (i, missing)
            for i, r in enumerate(rows)
            for missing in [[f for f in fields if f not in r]] if missing]

def CheckTickerFieldMatchesFilename(rows, ticker):
    """Does every row's own `ticker` field match the file it's stored in? Catches a row
    copy-pasted from the wrong ticker's fetch."""
    return ["row %d ticker field %r != filename %r" % (i, r.get("ticker"), ticker)
            for i, r in enumerate(rows) if r.get("ticker") != ticker]

def CheckChronologicalOrderNoDuplicates(rows):
    """Is `t` strictly increasing with zero duplicates? A duplicate or out-of-order `t`
    means AppendNewBars/ReviseExistingBar's invariants were bypassed (e.g. a direct file
    edit) or the vendor returned the same minute twice under different values."""
    problems, last_t, seen_t = [], None, set()
    for i, r in enumerate(rows):
        t = r.get("t")
        if t in seen_t:
            problems.append("row %d duplicate t=%s" % (i, t))
        seen_t.add(t)
        if last_t is not None and t is not None and t < last_t:
            problems.append("row %d t=%s out of order (prev %s)" % (i, t, last_t))
        last_t = t
    return problems

def CheckBarPriceConsistency(rows, shape):
    """Bar rows only: do o/h/l/c/px actually describe one consistent bar? l<=min(o,c),
    h>=max(o,c), and px==c (px is defined as the bar's close -- see Massive/daily
    MANIFEST.md). Skipped entirely for moment rows, which have no OHLC to check."""
    if shape != "bar":
        return []
    problems = []
    for i, r in enumerate(rows):
        if all(k in r and r[k] is not None for k in ("o", "h", "l", "c")):
            if r["l"] > min(r["o"], r["c"]) + 1e-9:
                problems.append("row %d l > min(o,c)" % i)
            if r["h"] < max(r["o"], r["c"]) - 1e-9:
                problems.append("row %d h < max(o,c)" % i)
            if abs(r["px"] - r["c"]) > 1e-6:
                problems.append("row %d px != c" % i)
    return problems

def CheckForBlankOrMissingValues(rows, shape, ticker):
    """Does any REQUIRED_NEVER_NULL field hold None, "", or NaN? This is the check that
    answers "is there blank/missing tick data inside rows we do have" -- a different
    question from AnalyzeTradingDayCoverage, which answers "are whole trading days
    missing." A null in a NULLABLE_FIELDS field (vol/vw/n for an index ticker) is correct
    data and never flagged here.

    Required fields are resolved PER ROW from that row's own `class`, not from the
    store's declared shape -- essential for the merged `tickers` store, whose declared
    shape is "bar" but which legitimately contains `class: "moment"` rows (from
    snap-v1-minute-moment-sourced days) with structurally-null o/h/l/c. Checking those
    rows against bar's required fields would flag every one of them as "blank," which is
    exactly backwards: a moment row's null o/h/l/c is correct data, not missing data."""
    problems = []
    for i, r in enumerate(rows):
        row_shape = "moment" if r.get("class") == "moment" else "bar"
        for f in REQUIRED_NEVER_NULL[row_shape]:
            v = r.get(f, None)
            if v is None or v == "" or (isinstance(v, float) and v != v):  # v!=v is NaN
                problems.append("row %d field %r is blank/missing (required, never null)" % (i, f))
    return problems

def ValidateTickerQuality(store, ticker):
    """Runs all five named checks above for one ticker's file and returns the result
    keyed by check name -- never a flat, unlabeled "problems" bag, so the output itself
    answers "what are you testing." A ticker is clean when every list is empty."""
    shape = STORES[store]["shape"]
    rows = LoadTickerHistory(store, ticker)
    checks = {
        "required_fields_present": CheckRequiredFieldsPresent(rows, shape),
        "ticker_field_matches_filename": CheckTickerFieldMatchesFilename(rows, ticker),
        "chronological_order_no_duplicates": CheckChronologicalOrderNoDuplicates(rows),
        "bar_price_consistency": CheckBarPriceConsistency(rows, shape),
        "blank_or_missing_values": CheckForBlankOrMissingValues(rows, shape, ticker),
    }
    all_problems = [p for probs in checks.values() for p in probs]
    return {"ticker": ticker, "rows": len(rows), "checks": checks, "problems": all_problems}


# ---------- sanitize / standardize ----------
# Fixes the blank/malformed-value class of problem CheckForBlankOrMissingValues can only
# detect, not repair -- e.g. a numeric field that arrived as the string "123.4" instead
# of a number, or an empty string "" where a value belongs vs. a legitimate null.
# Deliberately does NOT invent values for genuinely missing data (never forward-fills a
# missing px) -- sanitizing standardizes representation, it does not fabricate ticks.

# Fields the row schema defines as whole numbers.
INTEGER_FIELDS = {"t", "vol", "n"}
FLOAT_FIELDS = {"px", "o", "h", "l", "c", "vw"}
FLOAT_DECIMALS = 6

def SanitizeRow(row, shape):
    """Returns (cleaned_row, changes) for one row. changes is a list of human-readable
    strings describing every fix made, or [] if the row needed none.
    - "" (empty string) in any field becomes None (an empty string is never a
      meaningful value; it is indistinguishable sloppiness from a true null).
    - A numeric field holding a numeric-looking string (" 123.4 ", "123") is coerced to
      float/int -- this is standardization (consistent types), not data fabrication.
    - String fields (ticker, src, class, grain) are stripped of surrounding whitespace.
    """
    numeric_fields = {"t": int, "px": float, "vol": float, "o": float, "h": float,
                       "l": float, "c": float, "vw": float, "n": float}
    string_fields = ["ticker", "ts", "src", "class", "grain"]
    cleaned, changes = dict(row), []
    for f, v in row.items():
        if v == "":
            cleaned[f] = None
            changes.append("field %r: '' -> null" % f)
        elif f in numeric_fields and isinstance(v, str) and v.strip() != "":
            try:
                coerced = numeric_fields[f](v.strip())
                cleaned[f] = coerced
                changes.append("field %r: string %r -> %s" % (f, v, coerced))
            except ValueError:
                pass  # leave it for CheckForBlankOrMissingValues/schema checks to flag
        elif f in FLOAT_FIELDS and isinstance(v, float) and v == v and round(v, FLOAT_DECIMALS) != v:
            # Remove binary-float noise (155.25300000000001 -> 155.253). Six decimals is the
            # most precision any stored value carries, so no real digit is lost.
            cleaned[f] = round(v, FLOAT_DECIMALS)
            changes.append("field %r: float noise %r -> %r" % (f, v, cleaned[f]))
        elif f in INTEGER_FIELDS and isinstance(v, float) and v == v:
            # Vendor now returns fractional volume/trade counts (e.g. 7526.772129); the
            # schema stores whole numbers. Round half up, report it as a change.
            rounded = int(v + 0.5) if v >= 0 else int(v - 0.5)
            cleaned[f] = rounded
            changes.append("field %r: float %r -> %d (integer field)" % (f, v, rounded))
        elif f in string_fields and isinstance(v, str) and v != v.strip():
            cleaned[f] = v.strip()
            changes.append("field %r: trimmed whitespace" % f)
    if str(cleaned.get("ticker", "")).startswith("I_") and cleaned.get("vol", 0) is None and cleaned.get("class") == "bar":
        cleaned["vol"] = 0  # index rows carry vol=0 by class convention; vendor sends none
        changes.append("field 'vol': null -> 0 (index class convention)")
    return cleaned, changes

def StandardizeTickerFile(store, ticker, dry_run=False):
    """Runs SanitizeRow over every row in a ticker's file. Rewrites the file with the
    cleaned rows unless dry_run=True. Returns {"rows", "rows_changed", "changes"} so a
    standardization pass is auditable, not a silent rewrite."""
    rows = LoadTickerHistory(store, ticker)
    cleaned_rows, rows_changed, all_changes = [], 0, []
    for i, r in enumerate(rows):
        cleaned, changes = SanitizeRow(r, STORES[store]["shape"])
        cleaned_rows.append(cleaned)
        if changes:
            rows_changed += 1
            all_changes.append({"row": i, "t": r.get("t"), "changes": changes})
    if not dry_run and rows_changed:
        _write_all(store, ticker, cleaned_rows)
    return {"ticker": ticker, "rows": len(rows), "rows_changed": rows_changed, "changes": all_changes}

def StandardizeAllTickersInStore(store, dry_run=False):
    """Drives StandardizeTickerFile across every ticker in a store, one at a time
    (same sequenced-protocol reasoning as RunCoverageAudit). Returns a per-store
    summary; does not persist per-ticker results the way RunCoverageAudit does, since
    this is a corrective pass meant to be run to convergence (0 rows_changed), not
    tracked over time the way coverage is."""
    tickers = ListTickersInStore(store)
    total_rows_changed = 0
    tickers_with_changes = []
    for i, tk in enumerate(tickers):
        result = StandardizeTickerFile(store, tk, dry_run=dry_run)
        if result["rows_changed"]:
            total_rows_changed += result["rows_changed"]
            tickers_with_changes.append({"ticker": tk, "rows_changed": result["rows_changed"]})
        if (i + 1) % 25 == 0 or (i + 1) == len(tickers):
            print("[%s] %d/%d (dry_run=%s)" % (store, i + 1, len(tickers), dry_run), flush=True)
    return {"store": store, "tickers": len(tickers), "total_rows_changed": total_rows_changed,
            "tickers_with_changes": tickers_with_changes}


# ---------- gap analysis ----------

def _ticker_trading_days(store, ticker):
    return {r["ts"][:10] for r in LoadTickerHistory(store, ticker) if r.get("ts")}

def AnalyzeTradingDayCoverage(store, ticker, window_start: date, window_end: date):
    """Expected NYSE trading days in [window_start, window_end] vs. the days this
    ticker's file actually has a row on (day-level, not minute-level -- see module
    docstring). Returns missing days explicitly (not just a count) so a fetch plan
    can be built directly from the result."""
    expected = {d.isoformat() for d in expected_trading_days(window_start, window_end)}
    present = _ticker_trading_days(store, ticker)
    missing = sorted(expected - present)
    return {
        "ticker": ticker,
        "expected_days": len(expected),
        "present_days_in_window": len(expected & present),
        "missing_days": len(missing),
        "missing_sample": missing[:10],
        "missing_all": missing,
        "extra_days_outside_window": len(present - expected),
        "first_present": min(present) if present else None,
        "last_present": max(present) if present else None,
    }


# ---------- per-ticker sequenced protocol ----------

def EvaluateTicker(store, ticker, window_start, window_end, force=False):
    """ValidateTickerQuality + AnalyzeTradingDayCoverage for one ticker, persisted to
    _qa-gap-results/<store>/<ticker>.json immediately. Skips recomputation if that
    result already exists (force=True to redo it) -- this is what makes
    RunCoverageAudit resumable after an interruption."""
    out_path = os.path.join(RESULTS_DIR, store, "%s.json" % ticker)
    if os.path.exists(out_path) and not force:
        with open(out_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    result = {"store": store, "ticker": ticker,
              "qa": ValidateTickerQuality(store, ticker),
              "gap": AnalyzeTradingDayCoverage(store, ticker, window_start, window_end)}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(result, fh, default=str)
    os.replace(tmp, out_path)
    return result

def RunCoverageAudit(months=24, stores=None, force=False):
    """Drives EvaluateTicker across every ticker in the given store(s) (default: all
    three), one ticker at a time -- never a single pass over every row in a store, which
    doesn't scale and gives no visibility or partial result if interrupted. Prints
    progress every 25 tickers."""
    window_end = date.today()
    window_start = window_end - timedelta(days=months * 30)
    for store in (stores or list(STORES.keys())):
        tickers = ListTickersInStore(store)
        for i, tk in enumerate(tickers):
            EvaluateTicker(store, tk, window_start, window_end, force=force)
            if (i + 1) % 25 == 0 or (i + 1) == len(tickers):
                print("[%s] %d/%d" % (store, i + 1, len(tickers)), flush=True)

def SummarizeCoverageAudit():
    """Aggregates the small per-ticker results RunCoverageAudit already wrote --
    reads only those, never the underlying data files again."""
    report = {}
    for store in STORES:
        result_files = sorted(glob.glob(os.path.join(RESULTS_DIR, store, "*.json")))
        per_ticker, qa_problem_tickers = [], []
        total_expected = total_missing = 0
        for f in result_files:
            with open(f, "r", encoding="utf-8") as fh:
                r = json.load(fh)
            per_ticker.append(r["gap"])
            total_expected += r["gap"]["expected_days"]
            total_missing += r["gap"]["missing_days"]
            if r["qa"]["problems"]:
                qa_problem_tickers.append({"ticker": r["ticker"], "problems": r["qa"]["problems"][:5]})
        report[store] = {
            "tickers_processed": len(result_files),
            "total_expected_ticker_days": total_expected,
            "total_missing_ticker_days": total_missing,
            "coverage_pct": round(100 * (1 - total_missing / total_expected), 2) if total_expected else None,
            "qa_problem_tickers": qa_problem_tickers,
            "worst_gaps": sorted(per_ticker, key=lambda r: -r["missing_days"])[:15],
        }
    return report


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "merge":
        print(MergeAllTickersAcrossStores(force="--force" in sys.argv))
    elif mode == "standardize":
        dry_run = "--dry-run" in sys.argv
        for store in STORES:
            summary = StandardizeAllTickersInStore(store, dry_run=dry_run)
            print("%-25s tickers=%4d total_rows_changed=%d tickers_with_changes=%d" % (
                store, summary["tickers"], summary["total_rows_changed"], len(summary["tickers_with_changes"])))
    elif mode == "run":
        RunCoverageAudit(24)
    elif mode == "aggregate":
        report = SummarizeCoverageAudit()
        out_path = os.path.join(ROOT, "GAP-ANALYSIS-24MO.json")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, default=str)
        for store, r in report.items():
            print("%-25s tickers=%4d expected_ticker_days=%9d missing_ticker_days=%9d coverage=%s%%" % (
                store, r["tickers_processed"], r["total_expected_ticker_days"], r["total_missing_ticker_days"], r["coverage_pct"]))
        print("wrote", out_path)
