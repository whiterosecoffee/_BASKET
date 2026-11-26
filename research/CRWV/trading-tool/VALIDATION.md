# Validation record

Local evidence, 2026-10-29 UTC. These are observed implementation checks; no financial forecast, trading edge or live-operation assertion.

- `python -m unittest discover -s research/CRWV/trading-tool/tests -v`: **26 tests passed**, no skips.
- Pinned parent corpus (`6d82bccacaaba9855ef6bd27c64d72eb0514c8c9`) minute and daily CSV hashes checked, pattern content checked against source manifest.
- `corpus.py` then `run.py replay --retrospective-matches`: **7,534 signals**, **20 sessions**, including final partial Oct28 session through **11:34 ET**.
- Same replay a second time: **0 new signals**, generation unchanged. Export contains 7,534 JSONL records. Local SQLite populated; ignored `local/patterns.sqlite` is the working copy, not a GitHub live database.
- Events: **277 frozen ranges**, **138 confirmed down breaks**, **128 confirmed up breaks**, **51 upward / 45 downward close traversals**, **57 candles touching both bands with unknown ordering**. These differ from the parent's 259 fixed-horizon historical candidates because the incremental lifecycle keeps a range until break/gap/session end and checks for successors every completed minute; it does not have the parent's 30-minute evaluation timeout or five-minute retry cadence. Counts are not independent event success rates.
- Last historical matrix: lower **60.3182–60.4218**, upper **60.7982–60.8518**, position **0.541**, S **0.825**, Q **−0.278**; **$79.33M / 1.307M shares** in last15m, **2.348% ADV20**, same-clock RVOL **0.801**; `drifting_lower_ceiling_untested_5m`. Source cutoff historical; not a present signal.
- 3,928 signal records carry frozen retrospective analogues. Overlapping repeated snapshots are not 3,928 independent matches. Strict available-at mode excludes this unknown-availability historical corpus; explicit retrospective mode is labeled.

Preserved failed attempts and corrections:

1. First 25-test run: 24 pass, 1 failed test (`close_traversal_has_elapsed_time` IndexError). The fixture closed just outside the narrow pivot bands; corrected it to enter the actual bands. No method change was needed for that test. Retest:25 pass.
2. First full corpus attempt rejected a vendor VWAP outside the OHLC envelope. Source has 2,206 such rows among all extended/RTH minute records. OHLC eligibility and VWAP coverage need not be identical. Removed that overly strict gate; retained finite positive VWAP, original OHLC, source values and explicit per-window discrepancy counts. No clamping or hidden repair. Full replay then passed.
3. Exact-head CI has not yet independently executed the domain suite; B01 #98 owns it. Existing shared repository green checks do not establish new domain coverage.

Entitlement probe at 2026-10-29 03:34 UTC: `/v2/last/trade/CRWV` and `/v2/last/nbbo/CRWV` each returned NOT_ENTITLED. `/v1/marketstatus/now` reported Nasdaq/NYSE closed, serverTime `2026-10-28T23:34:30-04:00`. Minute aggregate request returned latest bar start `1793231940000` = Oct28 19:59ET. In-session aggregate lag could not be verified overnight. This is a connector observation; a future hosted key must be verified independently.

The adapter's API pagination and restart tests use mock responses. No actual credentialed REST poller, daemon, remote disk or restart supervisor was run. No spread/NBBO, signed flow, earnings multiples, live options OI or issuer credit inference is present.
