# Feature design: source-gated traversal tool

**Problem.** The merged B06 metric calculator is callable, but a stable entrypoint needs explicit input validity and conservative readiness. A generic ticker name or timestamp must not make a stale snapshot appear current.

**Parent / composition.** Reuse merged `engines.traversal.metrics.evaluate` unchanged. Keep B10 #95/PR99 frozen-band/event journal and B17 #100/PR101 context outside this pure read adapter. Source resolution, calendars and provider entitlements belong to B00/B02. B00 owns shared registration. This node adds only the interface and fail-closed validation.

**Input `basket.traversal.request@1`.** `instrument`, `as_of_ms` UTC, ordered `observations`, `source` with `provider/source_id/interval_minutes/currency/adjustment_basis/session/sha256`. Bar timestamps are UTC START ms, OHLCV are completed; source may explicitly report known/unknown availability, received_at, TTD, entitlement and calendar certification. No implicit data fetching.

**Output `basket.traversal.tool@1`.** Descriptive historical `metrics` delegates exact formulas to B06. `status`, `reasons`, `as_of_ms`, `completed_at_ms`, `observation_sha256`, `alerts_emitted=0`. Current mode always reports `blocked_current` until a trusted independently attested resolver is integrated. This is deliberate: a self-authored JSON cannot prove real-time provider entitlement or a correct calendar. CLI returns code 2 for that gate.

**Algorithm and formulas.** Validate schema, symbol, USD-only, supported 1/5/15-minute interval, source identity, digest over compact sorted-key JSON observations, timestamp and strict ordering, complete tail and no future available_at/received_at; report gap/TTD/calendar/completeness states. The digest establishes content identity within the request, not independent source authenticity. The parent B06 metric method defines positions, return, sampled path, $10M effort and unknown horizons. This tool does not fit models, estimate event probabilities, or reconstruct within-bar paths.

**Exceptions / limits.** Non-USD requires upstream FX; missing/ambiguous source fields fail or remain explicit; legitimate no-trade bars cannot be fabricated; current never claims qualification. Historical descriptive output may carry explicit quality warnings. No persistence, revision journal, delivery cursor or live process here.

**Prior art.** #108/merged #109 read-only metrics; #95/PR99 event journal, #149/PR150 geometry; #144/PR145 T01–T16 falsification cases; #148 canonical resolver and #152 B02 source quality. Reuse through explicit adapters after owner gates, not parallel implementations.

**Evidence.** Isolated local prototype checks: seven synthetic contract tests passing after correcting one fixture error; test invokes a mocked existing core. Shared PR-head CI and named traversal CI are distinct and do not currently establish this new adapter suite's execution. Exact tool source and test acceptance remain B01 #98. No real CRWV/ORCL M1 replay established.

**Ghost nodes / downstream interfaces (planned only).** B00 verified resolver binding; B10 durable journal adapter; B17 context adapter; B01 exact-head domain qualification; B08 hosted delivery. Each retains its own owner/contract and is not developed in this node.
