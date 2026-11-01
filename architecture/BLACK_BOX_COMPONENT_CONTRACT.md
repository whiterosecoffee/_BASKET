# _BASKET black-box component contract v1 (B00 proposal)

Every reusable component is a **versioned boundary**: validated typed input → deterministic or explicitly external execution → validated typed output or typed error. The internal algorithm is replaceable without changing its public contract. The contract manifest conforms to `schemas/component-blackbox.v1.json`; the port `schema_ref` names an independently versioned JSON Schema. No component may silently accept undeclared inputs, fabricate missing observations, or turn missing evidence into a successful valuation.

## Execution envelope (proposal for B00 arbitration)

Request: `{contract:"basket.component_call@1",component_id,contract_version,run_id,as_of,inputs,provenance:{source_ids,observed_at,available_at,ingested_at,content_hash},options:{offline,seed}}`.

Response: `{contract:"basket.component_result@1",component_id,contract_version,run_id,status:"ok"|"error"|"insufficient_evidence",outputs,provenance:{input_hash,source_ids,as_of,generated_at,code_sha,fixture_sha},quality:{freshness,missing_inputs,warnings},error:{code,message,retryable}|null}`.

Rules: `status=ok` requires validated inputs/outputs and mandatory source/provenance; `insufficient_evidence` must not contain a tradable live conclusion. `error` is typed and never disguised as an empty successful output. `as_of` is not an assertion of live freshness. Time-dependent adapters must record effective, observed, first-available and ingested times separately; original currency and USD conversion basis remain explicit. Output validation and acceptance are independent of financial correctness. For external observations, record entitlement, provider, clock and TTD. Stable input canonicalization and hashes enable replay; do not hash secrets. No unrestricted filesystem or network access implied by the interface.

## Required component acceptance

1. JSON Schema validation of manifest, request, response, and each port payload; strict unknown-field rejection where feasible.
2. Golden offline fixture: same pinned code/config/input/seed → same semantic outputs and content hash (ignore run metadata timestamps).
3. Negative fixtures: missing source, expired data, invalid schema, unavailable provider, mismatched contract major version, insufficient funding where applicable; fail closed.
4. B01 CI runs **actual tests** with a minimum test-count gate; records exact implementation SHA, workflow SHA, fixture hashes, run URL and outcomes. Skipped/zero tests fail. Shared green validation is not domain acceptance.
5. Dependency contracts are semver-pinned, owner-approved; schema-breaking changes require B00 review, B01 independent test handoff, and consumer compatibility checks.
6. Distinguish component-verified, integrated-on-main-with-main-CI, and operational-with-entitled-persistent-runtime. Never infer any of these from a draft PR alone.

## Retrofit matrix (handoff only; no domain writes by B00)

| Owner | Proposed black box | Inputs | Outputs | Special gate |
|---|---|---|---|---|
| B02 | `market.observation_replay` | symbol, as-of, immutable JSONL revisions, FX, TTD | replayed point-in-time bars, gaps, snapshot hash | entitled/live vs historical |
| B03 | `issuer.event_ledger` | source documents, effective/available times, revisions | canonical events and evidence lineage | source verification, dedup |
| B04 | `valuation.forward_multiple` | EPS quarter path, share count, assumptions | forward EPS, multiples, scenarios | no implied market price |
| B06 | `market.range_traversal` | timestamped bars, volume, benchmark | zones, touches, efficiency, regime | no predictive claims without calibration |
| B07 | `signal.calibration` | out-of-sample outcomes, signals, regime | calibration scores, uncertainty | leakage checks |
| B08 | `runtime.snapshot_service` | authenticated request, snapshot ID | versioned read-only response | actual deployment separate |
| B10 | `crwv.operating_valuation` | contracted/active/billable MW, price, debt, capex | monthly revenue, funding gap, EPS, dilution, value | unfunded scenario explicit |
| B17 | `basket.market_context` | timestamp-aligned basket and macro series | deltas, weights, missing coverage | cross-ticker as-of alignment |
| B19 | `research.revenue_pool` | issuer/source evidence, market definitions | revenue-pool map and uncertainty | sourced vs inferred |
| B21 | `narrative.falsification` | evidence graph, hypotheses, observations | claims, counterevidence, confidence | never call speculation verified |

**Migration:** B00 approves manifest and port schema IDs first; domain owners add adapters/fixtures inside their existing exclusive paths; B01 adds contract validation and mandatory CI in `.github/workflows/**` and `tests/integration/**`; B00 registers dependency edges only after evidence. Do not retrofit by editing another owner's PR, and do not rewrite the planner queue owned by PR #25.

**Status:** This is a proposed B00 design, not a merged or operational API. Actual request/response JSON Schemas and reference runner are follow-up B00/B01 work; no claim of executable validation until implemented and independently tested.
