# CRWV daily capture candidate

Issue121 / PR122; B02/B01 acceptance handoff186. Research implementation only.
Canonical `tickers/CRWV/intraday/**` files are unchanged by this upgrade.

The old CSV command's monthly writer is replaced with an external staging tool:

```bash
python research/CRWV/market-research-2026-10-29/backfill_minutes.py --source-dir /path/to/captures --month 2026-10 --output /external/new-generation
python -m unittest discover -s research/CRWV/market-research-2026-10-29 -p 'test_*.py' -v
```

`--root` is intentionally removed. Existing canonical README instructions refer
to the superseded command; B02 must update that README when adopting the contract.

Every generated JSONL contains one America/New_York calendar date only. UTC
minute-start times remain unchanged; local dates handle DST. Each daily JSONL
has a metadata sidecar with SHA256, count, start/end cutoff, anomaly count,
source capture lineage and historical-only/coverage-unverified status. Missing
minutes stay absent. Unknown retrieval and first-availability times remain null.

For byte-preserving migration of the existing monthly JSONL, use
`prepare_daily_shards.py --source /path/to/month.1m.jsonl --output /external/split`.
If paired source metadata exists, its SHA256 must match before staging. Source
metadata recorded_at is retained as source_recorded_at, never first availability.

CSV replay of the identical capture changes no files. A different capture,
including new bars, revisions or older gap fills, requires a new staging
generation; this tool does not perform production appends. Exact source duplicate
rows collapse; conflicting duplicates fail. All output collisions are checked
before writes. Never infer entitlement or a live service from this offline tool.

Single writer only. After an interrupted CSV materialization, use a fresh staging
directory; unidentified nonempty directories fail closed. This candidate does
not claim multi-file transaction atomicity, concurrent writer support or deployed
restart recovery. B02 owns those production requirements.

Local evidence: `daily-capture-validation.json`. Six test methods passed,
including real October byte equivalence, repeat-capture no-op, DST fold/midnight,
source conflict and wrong-month rejection, malformed OHLC/nonfinite/duplicate
timestamps, collision preservation and repository output guards. The real CSV
roundtrip reproduced all19,186 original rows byte-for-byte into22 daily pairs,
retaining2,374 VWAP-vs-OHLC anomalies. October30 still ends12:10ET; splitting
does not complete that session. No fresh market capture was performed here.

Remaining adoption gates: B02 explicit canonical path acceptance and review of
paired metadata/revision/TTD semantics, independent B01 CI at the final candidate
head, then explicit user merge authorization. Existing shared CI alone is not
minute-domain acceptance. Ownership stays with the original workers; #186 is
a posted request, not proof they have retrieved it.
