# Massive REST API: documentation research for a local connection

Spark B02 | issue #151 | research record, 2026-11-25. Docs were read from massive.com pages and the Massive connector's endpoint documentation. **Nothing here was run against the live API from this environment** (no key). Local code was read, not executed. Labels: **doc** = stated on a fetched page; **code** = read in source; **unverified** = not established.

## 1. What the documentation says
| Topic | Statement | Label / source |
|---|---|---|
| Base URL, auth | `https://api.massive.com`; key as `?apiKey=` or `Authorization: Bearer <key>` | doc: massive.com/docs/rest/quickstart |
| Aggregates | `GET /v2/aggs/ticker/{ticker}/range/{mult}/{timespan}/{from}/{to}`; `from`/`to` inclusive dates or ms timestamps; `adjusted` defaults **true**; `sort`; `limit` max 50,000, default 5,000 | doc: connector endpoint docs; custom-bars page |
| Bar semantics | `t` = Unix ms **start** of window; no eligible trade means **no bar** (no empty bar); response has `status`, `adjusted`, `queryCount`, `resultsCount`, `next_url`; `otc` only when true | doc |
| Empty minutes | KB example: AAPL produced 885 minute bars in a 960-minute (04:00-20:00) session | doc: knowledge-base FAQ |
| Sessions | No session parameter; select extended hours with timestamps; far fewer extended-hours bars (odd lots cannot set a price) | doc: knowledge base |
| Pagination | JSON `next_url` (cursor); Arrow responses carry `Link: <url>; rel="next"` instead | doc: quickstart |
| Arrow | `Accept: application/vnd.apache.arrow.file` on supporting endpoints | doc: quickstart |
| Delay by plan | Plan recency is end-of-day, 15-minute delayed or real-time; a delayed key gets `"status":"DELAYED"` (HTTP 200) when the range includes today | doc: custom-bars page; KB article on real-time vs delayed |
| Rate limit | Counted **per asset class**; subscribed class has no limit; unsubscribed class 5/min; error text "exceeded the maximum requests per minute"; extra keys do not change it | doc: KB request-limit article |
| Late trades | Trades can be reported minutes after they happen; Massive holds bars open and rebroadcasts when a late trade changes one (WebSocket article). **REST revision horizon is not documented.** | doc: KB WebSocket late-bar article |
| Flat files | `https://files.massive.com`, bucket `flatfiles`, S3 keys **separate from the REST key**; `us_stocks_sip/minute_aggs_v1` is one file per day for all US equities; updated 11a ET with the previous day; history Starter 5 y, Developer 10 y, Advanced all; Basic not included; a 403 does not say why | doc: flat-files quickstart and minute-aggregates page |
| Reference data | `GET /v1/marketstatus/upcoming` (upcoming holidays and open/close times, forward only); `GET /stocks/v1/splits` (execution date, ratio, type); `GET /stocks/v1/dividends`. The quickstart still shows `/v3/reference/dividends`, so endpoint versions differ across pages | doc |
| Tooling | Official Python, Go, JVM and JS clients; remote MCP server; every doc page has a `.md` twin | doc |

## 2. What exists locally (source pinned: `_PATTERNS` main `5eeacd9c0c1bd3a707044c9820e7e32490781ae6`; code read, not run)
- `_TOOLS/ticker_tail.py` (blob `f8fc88e5`): key read from a local key file outside any repository (BOM tolerant; path omitted here on purpose); `Authorization: Bearer`; `/range/1/minute/...?adjusted=false&sort=desc&limit=50000`; 5 attempts, `2**i` backoff on 429 and 5xx; **raises if `next_url` is present**; 0.25 s pause between tickers; appends through `ticker_rows.add_rows` (read afterwards, see below). No raw-response retention, hash or `fetched_at` visible in this file.
- `_TICKERS/_MASSIVE-API/source/runtime/massive_maintainer/maintain.py` (blob `1eb92a1f`, a pinned source copy): host allowlist, parameter allowlist (`adjusted, sort, limit, date, cursor, order, timestamp.*`), Bearer from a `--key-file`, guard against the key appearing in the URL or the response, immutable raw responses named by sha256 with receipts, `Retry-After` deferral receipts, `STOP` file, 1 request per second, quarantine receipts, tests for transport.
- `_TOOLS/ticker_rows.py` (read 2026-11-25): writes named-field rows, one New York session date per file, to `_TICKERS/<T>/snapshots/<YYYY-MM-DD>.jsonl`; dedupes on `t`; appends under a lock; never rewrites a line; skips frozen (all-`verified`) days. Its `sanitize` accepts `vol >= 0` and `n >= 0`, whereas the B02 design drops `v <= 0` and `n < 1`; it allows rows that carry only `px` and `vol` ("moments"); it records `src` per row but no per-row hash or fetch time. These are divergences to reconcile, not defects established.
- Where either runs, how often, and which one produced the Oct 9 to Nov 23 backfill are **unverified**.

## 3. Missing or divergent components
| # | Gap | Evidence | Smallest fix | Natural owner |
|---|---|---|---|---|
| 1 | `next_url` not followed | `ticker_tail.py` raises; docs return cursors | Follow `next_url`, re-sending the auth header; verify whether the URL carries the key (doc sample does not) | _TICKERS/_MASSIVE-API owner |
| 2 | Response `status`, `adjusted` echo and counts not checked in the fast path | docs; code read | Record `status`; refuse a range with `DELAYED` as settled; assert `adjusted == false`; compare `resultsCount` with rows | same |
| 3 | Plan and entitlement unrecorded | docs: recency depends on plan; B00 asked for limit=1 probes (#207) | One `limit=1` request over a range including today; record `status`, not rows | B00 records in `massive_workers.json` |
| 4 | Raw retention and provenance in the fast path | `maintain.py` has them, `ticker_tail.py` does not show them | Reuse the maintainer transport; do not write a third client | same |
| 5 | Settlement lag unmeasured | late trades are minutes (WebSocket doc); REST horizon undocumented | Keep next-ET-day cutoff and double-pull verification; measure repeated pulls over several days | _FETCH owner |
| 6 | Calendar | docs give only upcoming holidays; `gap_analysis.py` hard-codes holidays | One calendar module, checked against zero-result days; refreshed from `/v1/marketstatus/upcoming` | QC app owner |
| 7 | Corporate actions | `/stocks/v1/splits` exists; data stored unadjusted | Split ledger for the continuity check and for consumers | _FETCH owner |
| 8 | Bulk path unused | flat files hold one file per day for all tickers | Evaluate for backfill and gap fill; needs plan, separate S3 keys and a check of the basis | B00 and owner |
| 9 | Key handling differs from the task-start rule | task text: key only from `MASSIVE_API_KEY`; local code: key files | **Resolved 2026-11-25 by the owner:** local key file outside any repository; the env-only rule is superseded. Keep the key out of repositories, URLs, logs and archived responses | resolved |
| 10 | Arrow responses | optional | Not needed at about 960 rows per day | none |

## 4. Not verified
The key's plan tier; whether flat files are included; the flat-file adjustment basis and column layout (the "Documentation" tab was not read); `ticker_rows.py` behavior; whether `next_url` needs the key re-attached; the REST revision horizon; which splits and dividends endpoint version is current; the correct file name pattern for `minute_aggs_v1` (inferred from the trades example).
