# JSON-first source-to-consumer reference objects

Issue [#241](https://github.com/whiterosecoffee/_BASKET/issues/241), B00. Exclusive scope: this directory plus the additive `orchestration/tests/test_data_flow_objects.py` discovery bridge (scope amendment on #241). Independent branch from main; no imports from legacy FETCH, `_MAP` or clone implementations.

## What exists

`objects.json` defines seven reusable boundaries, nested source-to-consumer/qualification compositions, semantic bindings, failure/recovery rules and prior-art rationale. `capture.schema.json` defines the explicit handoff envelope and bars. `flow.py` is a minimal executable reference binding, not a replacement ingestion service. `consumer.py` demonstrates access from a separate component/process. `test_flow.py` contains synthetic positives and negatives. `probe-evidence.json` records an actual Massive connector-projection replay, without raw bars or local paths.

Sequence: authorized Massive endpoint → connector table projection → capture JSON → raw local capture → sanitation into one exchange-local-date JSONL → recomputed verification receipt → source-pinned read-only consumer. The runner deliberately has no API client or credentials. The fetch step was actually performed with the connected Massive tools, not simulated; the reference runner starts at that explicit handoff. This does not execute the existing B02 FETCH implementation.

## Semantics and trust

Only USD stock 1-minute split-adjusted bars are supported by this first binding. Provider fractional volumes are retained, never converted to integers. Exact duplicate records collapse deterministically; conflicting duplicates reject the whole batch before any write. Missing minutes are not filled. The date partition is America/New_York local date, including observed extended-hours bars, not a calendar-certified complete exchange session. OHLC consistency, positive prices, nonnegative volume/count, finite numbers and minute grain are checked. Unexpected fields, mixed dates, empty data, malformed JSON and non-final bars at capture time reject.

Source bytes are immutable within a published artifact directory. The receipt binds source, partition, objects-contract, capture-schema and exact transform/verifier-code hashes. Verification independently reconstructs the partition from raw capture; consumer access verifies again, requires the expected source hash, ticker/date and as-of time, and hashes the exact returned partition bytes. Synthetic data is refused unless explicitly permitted. A copied or stale receipt cannot bless changed rows. These are integrity hashes, **not signatures or provider-authenticity proof**. The caller's source identity/capture time is an assertion backed by the separate connector execution evidence. A malicious actor replacing the entire source, pins and artifacts is outside this local trust boundary.

The connector capture is an explicit projection, not an original HTTP envelope. Provider request ID, original response bytes and historical first-available timestamps are unavailable. `captured_at`/`available_at` is the local materialization time after the call, conservatively later than retrieval, so it does not support earlier point-in-time claims. Historical truth is not advertised as current/live data. There is no freshness SLA, real-time entitlement certification or external price cross-check.

## Run

From the repository root:

```
python -m unittest discover -s orchestration/data_flow_objects -p 'test_*.py' -v
python orchestration/data_flow_objects/flow.py --capture /explicit/private/capture.json --root /explicit/private/probe
python orchestration/data_flow_objects/consumer.py /explicit/private/probe/NVDA.2026-11-10.1m.adjusted --ticker NVDA --session 2026-11-10 --as-of <capture-time-or-later> --expected-source-sha256 <capture-hash>
```

Capture matches `capture.schema.json`; caller must explicitly set endpoint, params, source mode, ticker, date, local materialization timestamp and exact projected rows. No implicit filesystem destination is selected. Do not put actual captures or resulting data directories in GitHub. Tests use generated synthetic rows only.

Same captured input returns `unchanged` and preserves bytes/mtimes. A different capture for the same partition rejects, even if economic rows match: revisions/supersession belong to the receiving storage owner. A staging interruption cleans up and never publishes a partial directory. This is a **single-writer transient probe**, not a multiwriter lock, crash-durable transaction, streaming writer or persistent local-authoritative deployment. Do not point it at a canonical production store. Immutable capture generations, raw/clean stage separation and full durability need the production owner's contract.

## Acceptance and next handoff

The committed sanitized evidence records 960 actual connector-projected NVDA bars on 2026-11-10; all 960 fractional volumes survive. Independent-process consumption and exact-input repeat passed. The endpoint is historical custom bars, not trades/quotes or a live feed. Synthetic tests prove rejection/recovery behavior separately. The additive B00 discovery bridge loads this folder through the existing shared CI command, without workflow changes. It refuses missing, empty, under-count, missing-original-test and skipped source suites, isolates imports, and executes the 17 original tests plus a schema/transform identity regression and six discovery negatives. Exact-head hosted logs, not shared-green alone, establish execution. Original probe evidence predates this discovery increment.

**B02 #207 requested receiving action:** identify/approve the real durable local-authoritative root and bind the existing FETCH output/QC entrypoint to these candidate handoff contracts; record one-day partition policy, adjustment/grain/unit semantics, observed-vs-expected coverage, calendar, revision/supersession, authentication/entitlement and retention. Then execute one actual durable fetch/write/read/repeat and negative QC cycle with a real downstream consumer, preserving raw-source lineage. Do not replace or overwrite existing FETCH/QC. No receiving claim or production acceptance is implied.

**B00 #230:** index the seven candidate IDs and contract needs from `objects.json`; map ports/adapters, W3C PROV/OpenLineage lineage, immutable artifacts and contract-first QC as *adapted pattern families*, not full standard implementations. `_MAP` stays its owner's scope. **B01:** independently inspect exact-head proof and decide hosted focused-gate adoption without creating a competing CI workflow.

### Revision identity boundary

Receipts now pin the exact `capture.schema.json` and `flow.py` bytes as well as the objects contract. Reads fail closed if any identity changes, including a code-only change that leaves output bytes unchanged. This intentionally does not select a historical implementation or make old receipts compatible. The first proof's original artifact is retained unchanged; a new isolated probe artifact demonstrates the stronger identity contract. A durable successor must supply immutable source/schema/transform bundles, explicitly supported reader revisions and append-only capture generations. Those broader choices remain B02-owned; no latest-version substitution or automatic canonical migration is implemented here.
