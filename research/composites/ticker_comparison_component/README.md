# Reuse the ticker comparison through the component boundary

B17 #219 applies the merged [component kit](../../../architecture/COMPONENT_QUICKSTART.md)
to existing #217/PR218, with latest #100/PR101 `change()`. This is an adapter, not a
second calculation engine, registry, runner or canonical market store. All six new
files stay outside the original owners' subtrees. Main baseline: `beaa94e`.

## Useful boundary

`adapter.run(request, compare_path=..., context_path=..., run_id=...,
generated_at=...)` returns `(manifest, call, result, supplied_bytes)`. The manifest
is `component.json`; request/output schemas are local, self-contained Draft 2020-12
contracts. The shared `check_exchange` performs envelope, port and content checks.

- Request: aligned `t` (integer milliseconds, midnight Eastern) and nullable
  NVDA/CRWV/SMH/QQQ split-adjusted USD close prices; previous completed cutoff date,
  evaluation time, positive session windows, correlation length >=2, source ID,
  synthetic/captured classification and explicit permitted-use assertion.
- Output: the **unchanged existing comparison result**, with common-window price
  returns, QQQ-relative percentage points, daily-return correlations and null/missing
  states. `status=ok` means the diagnostic calculation succeeded, not complete data.
- Structurally invalid requests raise before source loading. Duplicate/future or
  otherwise semantically invalid histories return declared `invalid_history` with
  no outputs. Different dependency bytes fail before either source executes.
- All bytes are supplied locally. No source is fetched, no manifest command is run,
  and no prices, reports or journals are written by the adapter.

Code is reused from these exact files and checked by SHA-256 before execution:

| Existing owner | Commit | Source |
|---|---|---|
| #217/PR218 | `37f6bfe0ef8cc243cfe319526cc7471bc0b77f5f` | `research/composites/market_context/ticker_comparison/compare.py` |
| #100/PR101 | `1517dc3cf549c4e2dd7695781bf01485b9dc6db6` | `engines/composites/market_context/context.py` |

Caller-supplied filesystem paths only locate these **approved bytes**. The adapter
executes the already checked bytes rather than reopening a file or trusting cached
bytecode. The comparison's old `context_change()` loader is not invoked: it pins an
older source. Instead, existing `compare()` explicitly receives latest `change()`.
`provenance.code_sha` identifies the existing comparison commit. `method.json`
records both domain commits/source hashes and adapter bytes; this is not a claim
that the adapter existed in the comparison commit. Adapter release identity belongs
in the exact PR-head test/review evidence.

The input fingerprint policy is SHA-256 of canonical JSON **request bytes**:
UTF-8, sorted keys, separators `(',', ':')`, no nonfinite numbers. It includes
windows, cutoff, evaluation time and source metadata, not only prices. Consumers
compute this independently before invoking shared conformance. This policy is local
to this boundary, not a new repository-wide serialization rule.

## Run the existing domain, not mocks

Use the repository's pinned `jsonschema==4.23.0` environment. From this repository
root, provide the two authorized exact source files from read-only dependency
checkouts (until those PRs integrate). Tests fail if dependencies are missing or
changed; they never skip or fetch a replacement.

```sh
export BASKET_COMPARE_PATH=/absolute/path/to/PR218/compare.py
export BASKET_CONTEXT_PATH=/absolute/path/to/PR101/context.py
python -m unittest discover -s research/composites/ticker_comparison_component -p test_adapter.py -v
```

The five focused tests cover a hand-computed consumed outcome, identical replay and
no mutation, missing interior observations versus genuine unchanged daily prices,
typed date/range failures, and schema/dependency rejection. Shared conformance edge cases
remain in the existing 19-case shared suite, rather than being copied here.

A consumer calls `run`, checks the returned manifest/call/result with
`check_exchange(..., expected_input_sha256=its_request_digest)`, then reads the JSON
bytes named by `result['outputs']['comparison']['artifact']['ref']`. It must check
`result['status']` before requesting an output port. Request schemas and this example
are not instructions to publish licensed input prices.

## Real captured-input proof

On 2026-11-10 the private 92-date capture from #217 was replayed through this adapter
with latest PR101 source. The complete decoded result matched the existing
[derived result](https://github.com/whiterosecoffee/_BASKET/blob/37f6bfe0ef8cc243cfe319526cc7471bc0b77f5f/research/composites/market_context/ticker_comparison/result-2026-11-09.json):
16 returns and six correlation records, unchanged on a second identical execution.
Raw bars remain private; their existing source manifest is not duplicated.

- Private CSV SHA-256: `9a7a7fc26f35b13b1f179f1dff3eb664b64087c0d1dc13e13fe9e6f4f4874788`.
- Existing result file SHA-256: `3710fb24f03b49ab4829e26d2cfc63f36a7d2eb04de6ef6aa1a05a8e7a9ef815`.
- Canonical decoded result SHA-256: `086fed59eca9fe52ead28d3c90897bf4a24f903f0e66bb6a065665b70843f97a`.

This is local replay evidence, not independent provider retrieval or a newly
verified price dataset. Existing source dates, current-revision caveats, missing
calendar certification and price-return-not-total-return meaning remain intact.
Neither the unchanged-input replay nor an identical new daily price implies a new
live observation. Historical diagnostics mark freshness `not_applicable`; they do
not promote unknown observation/availability/revision timestamps to qualified.
Source rights, currency and adjustment basis remain caller assertions requiring
owner verification. No attribution, prediction or trading instruction is produced.

## Evidence and remaining work

Local focused tests, affected existing domain suites, aggregate tests and private
replay are recorded in #219's resolution with exact revision. Hosted shared CI does
not automatically discover this new domain suite. B01 #102 retains independent
named domain acceptance; PR101/PR218 integration remains separate. A main-based
checkout needs those explicit source paths until its dependencies integrate.

Measured adoption milestones and the corrected test assertion and independently found timestamp-overflow fix are in #219,
not another metrics ledger. Active work, review waiting, cost and comparable prior
build baselines were not captured; no speed improvement is claimed. Reuse verified:
one shared conformance helper and two existing calculation functions. Stop here
unless another real consumer demonstrates a missing shared capability.
