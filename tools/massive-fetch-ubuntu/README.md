# Massive Fetch Ubuntu

Standalone Python port of the existing Massive fetcher. See [state.json](state.json) for development status and [AGENTS.md](AGENTS.md) for ownership and continuation instructions. [SOURCE-SHA256.txt](SOURCE-SHA256.txt) records the original source fingerprints.

Python 3.12 and system time-zone data were used for the offline verification.

| Script | Contract |
| --- | --- |
| `fetch_plan.py` | Turns existing session scan JSON in `SESSION_SCAN_DIR` into a plan. |
| `fetch_run.py` | Uses a trusted plan and `MASSIVE_KEY_FILE` to stage adjusted minute bars. This is a live call path reserved for authorized owner use. |
| `verify_apply.py` | Reads staged data and existing archives, then writes a dry-run report. |
| `inspect_roster.py` | Prints endpoint and coverage advisories for the existing archive roster. |

Run `python3 -B inspect_roster.py --root /path/to/_TICKERS --required-through 2026-11-16T19:59:00-05:00` with the actual cutoff and placed archive root. The roster comes from the existing placement manifest. Endpoint observations do not establish continuous coverage. Review stale or unavailable endpoints with the canonical owner.

Use a fresh relative `RAW_DIR` for each trusted plan because the legacy resume marker is ticker-scoped. Keep key files, histories, plans and operational receipts out of source control.
