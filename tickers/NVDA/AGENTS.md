# _TICKER NVDA scope

This folder is the working directory for the NVDA analysis worker.
User-directed scope: only tickers/NVDA/**. Do not modify another ticker,
shared routing, ingestion code, schedules, or repository-wide contracts.
The active analyst remains on work/local-20261112-ticker-nvda. This sanitized publication snapshot is work/publish-20261112-nvda-analysis; it is not a second active writer.

## Data ownership
_FETCH owns Massive acquisition, validation, refresh, relocation and all writes
to Nvidia.jsonl, source-manifest.json and coverage.json. _TICKER reads them only.
Do not create an empty substitute, copy the historical corpus, run independent
Massive calls, or move the original archive from this analysis worker.

## Local analysis
Read data-location.json here first. Canonical data belongs under top-level _TICKERS; actual resolver and access remain pending owner verification. Nvidia.jsonl is an expected input name, not proof of delivery.
Read ./source-manifest.json and ./coverage.json for provenance, schema,
adjustment, units, session boundaries, source hash, freshness and missing ranges.
If absent, stale or unqualified, report the exact gap to the existing _FETCH owner.
Do not silently fall back to another folder or old snapshots as current data.
One-minute OHLCV bars are not individual trade ticks. Preserve distinctions
between bars, price-only observations and any daily fallback records.
Keep analysis outputs here. Do not commit raw market data or credentials.

## Coordination
fetch-request.json is the NVDA consumer handoff, not evidence that _FETCH accepted
or implemented the destination. Update readiness only after actual file and
manifest verification. Leave file placement and collision resolution to _FETCH.
