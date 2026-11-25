# _BASKET black-box component boundary v1

**Owner:** B00 #103 / PR104. **Consumer acceptance:** B01 #105 plus the domain owners below. This increment specifies and structurally validates an opt-in reference boundary. It is not an execution runner, resolved domain API, qualified live source, deployment or evidence of integration. GitHub PR/main receipts establish publication separately.

Every reusable component has a versioned boundary: declared inputs, assumptions and effects → execution → declared outputs/guarantees or a typed failure. Internal algorithms remain replaceable. Do not create another ticker store, registry, scheduler or general-purpose orchestration framework to adopt this boundary.

## Compatibility and implemented definitions

`schemas/component-blackbox.v1.json` still validates the original `basket.component_contract@1` manifest without new required fields. Existing v1 manifests retain their meaning; absence of a profile proves no qualified boundary. Opt in with `boundary_profile: qualified_refs_v1` and declare `assumptions`, `guarantees` and `effects` (an empty effects list means no declared effects). Every input/output then also requires the referenced schema's SHA-256, freshness policy and source class. These declarations do not grant permissions or prove behavior. Dynamic/stochastic agent reproducibility is not added by this change.

The same schema now contains resolvable local `$defs`, not another schema family:

- `artifact_ref`: an immutable content reference plus SHA-256 of its bytes. A URI/path or valid-looking hash is not proof that bytes exist or access is allowed.
- `source_evidence`: source/artifact identity, subject and record type, separate observed/available/ingested/effective/publication times, period/session, units/currency, freshness, entitlement and optional `supersedes` reference.
- `port_binding`: payload schema reference/hash, payload artifact reference/hash and nonempty source evidence. Payloads stay with their authorized owner. Raw licensed data is not copied into a manifest or GitHub evidence report.
- `call`: `basket.component_call@1`, component/version/run identity, as-of, nonempty named input bindings, pinned method/config artifact and offline/seed options.
- `result`: `basket.component_result@1`, the same identities/as-of, status, output bindings, input hash/method/code revision/generated time, quality and typed error.

Validate a definition by constructing a Draft 2020-12 schema containing this file's `$defs` and `$ref: #/$defs/call` (or `result`). A pinned offline JSON Schema registry may instead resolve the full file URI plus fragment. Do not fetch arbitrary schema URLs or files supplied by an untrusted payload. Validate the resolved payload separately against its pinned port schema; envelope conformance does not do this automatically.

The earlier call/result pseudo-objects were prose proposals, not a registered wire format. The new definitions use references rather than embedded domain values and per-source rather than global timestamps. Existing source payloads are not rewritten. `contract_version` denotes the selected component boundary version and must match the approved manifest/consumer compatibility decision; it is not the version of this shared schema.

## Fail-closed and evidence rules

`ok` requires nonempty outputs/sources, no typed error, no missing inputs or conflicts, qualified/not-applicable aggregate freshness, and output evidence without stale/unknown freshness or unknown/denied entitlement. A source claiming `qualified` must have observed and available timestamps. Unknown timestamps remain explicit null when evidence is not qualified. `error` and `insufficient_evidence` require a typed `{code,message,retryable}` error and empty outputs. Preserve diagnostics in quality/error; never smuggle a successful result into a failure payload.

`not_applicable` is for genuinely non-temporal inputs such as an immutable method specification or explicitly synthetic scenario. It cannot exempt a market observation or expectation vintage from point-in-time checks. `authorized` is a source-access assertion that must be verified, not permission granted by the manifest. `as_of` and ingestion time never substitute for observation/publication time. TTD expiry limits current use, not historical truth.

Schema validation enforces **shape and selected local state rules only**. The following semantic gates remain mandatory before a component can be qualified:

1. Resolve allowed references, verify actual schema/payload/source bytes against their hashes, then validate payloads. Match named ports, required/optional ports, component/version and request/result identity against the manifest. Reject undeclared ports and unsupported dependency versions. A schema reference string is not proof of a resolvable typed port.
2. Compare availability to as-of, require the appropriate time/period/session/calendar/adjustment basis for the record type, compute freshness from the accepted policy and verify entitlement. Preserve publication, first-observed and ingestion distinctions. Do not upgrade an unknown timestamp to `not_applicable`.
3. Check dimensional units, original currency and dated FX basis, stable instrument/venue or macro-measure identity, source class, correction lineage and conflicts. Envelope `unit` is descriptive; two valid strings do not prove compatible quantities. One currency field does not implement currency conversion.
4. Validate dependency versions, schema compatibility and the declared effects against actual authorization/ownership. Do not execute `test_command`, follow arbitrary references or grant access just because an untrusted manifest declares them.
5. Hash canonical semantic outputs using the consumer's documented serialization. Fix code/config/input/seed and compare two executions, excluding only declared run metadata. A serialization fixture test is not domain replay or proof of deterministic execution. The output artifact must already be persisted by its authorized writer before capture is called complete.

Use a validator with an enabled RFC 3339 date-time format checker; `format` may otherwise be only an annotation. A lexical timestamp pattern provides a basic safeguard but cannot reject every impossible calendar date or compare times. Test that the configured checker rejects invalid dates and offsets. The regression validator explicitly registers a standard-library date-time checker rather than assuming optional format dependencies exist. This profile uses timezone-aware timestamps without leap-second notation; a domain must normalize or explicitly version any different convention. No runner enforcing these semantic gates is introduced here.

## Representative mapping and disposition (2026-11-10)

The sources below were read at pinned commits. They are compatibility examples, not newly acquired market evidence. Only schema/test fixtures explicitly labelled synthetic are executed by this increment.

### Options/HIRO: accept reference mapping; defer qualified market use

Source: B02 #124 / PR125 at `bd3ee61fedbee97499ac73579fc703b815d459d8`, `runtime/spotgamma_hiro/examples/user_snapshots.jsonl` (SHA-256 `4dbe7b2f5e92c003191699129af993d2f70bdb9ffa252ccc14afed660ed6283d`). The supplied QQQ/NVDA/AMD records contain HIRO USD and some prices/walls but no observed time. Read the B02 README with that source: unknown provider capture time must remain null and licensed data may not be publicly redistributed.

Map an authorized resolver reference to the payload artifact; provider/source reference to source evidence; `ticker` to resolved instrument/venue identity; `hiro_usd` to an `options_flow` observation measured in USD. Preserve price/wall fields in their existing payload with their own USD-per-share semantics. A flow observation is not a quote, aggregate bar or trade. Missing observation/session/entitlement stays unknown; the case cannot return a current-market `ok` result. A receiving adapter must emit `insufficient_evidence` with the appropriate missing-time/access reasons. No artificial source capture time or current-flow inference is permitted.

**Receiver:** B02 #124 owns its local payload schema/adapter and licensed data destination; B06/B17 consume only qualified references. This decision allocates no B02 writes and does not assert receipt, entitlement or live operation.

### Company/ETF: accept reference mapping; defer domain schema qualification

Source: B04 #126 / PR127 at `76710defee89171c905f9f90f5b683ecc84c80b0`, `engines/valuation/etf_forward/test_engine.py` (SHA-256 `c46ca7fda4e673a463367c7dc3692ebb3e6ffc8301f4c9c25b99f86e27d57dc7`). Its `BASE` is explicitly synthetic and includes a placeholder source digest `not-external-evidence`. That placeholder **fails** the new artifact SHA-256 shape and must never be relabelled verified evidence. A separately hashed synthetic fixture remains synthetic.

Bind complete holdings and dated estimates as distinct payload/source references, preserving holding availability, 2027/2028 period/calendarization, USD units, coverage and model version. Bind the existing output artifact to the exact selected module-local output contract: `basket.etf_forward_output@1` and `basket.etf_lookthrough@1` are different candidates, not interchangeable approved APIs. Typed port schema bytes and their independent acceptance remain B04 work. The existing reciprocal-yield P/E behavior must still suppress results on partial/invalid coverage. No dated real holdings/consensus/FX acceptance follows from synthetic tests.

**Receivers:** B04 #126 owns the local payload/output schemas and adapter; #128 B02/B03 retains source/identity/FX qualification; B01 #129 retains domain CI. #105 covers this shared boundary, not ETF financial truth.

### Macro release: accept semantic boundary; defer persistence ownership

Source: B17 #141 / PR142 at `d9d7d23e3a3cc780fdd03eb634f6186903003ed8`, `research/composites/macro_backdrop/macros.v1.json`, plus the #103 macro request. This is a static register, not dated official releases or saved pre-release expectations.

A measure identity must include series/measure, reference period, unit and seasonal basis. Keep official calendar/status, consensus, nowcast, scenario, actual release, prior revision and market-window artifacts distinct. Reuse source evidence's publication/observed/available/ingested times and superseding references. Macro-specific definitions, forecast ranges/counts, scenario triggers and reaction windows remain inside B17's versioned payloads, not universal manifest fields.

Retrospective reconstruction and prospective freeze are different evidence classes. Prospective qualification requires the **actual saved packet** and freeze hash/time before actual publication (not merely its scheduled time), with sources available at freeze. Missing pre-release material stays missing. Compare actual-minus-frozen-expectation separately from prior-revision effects, using percentage points where appropriate. Newer-vintage data must not enter an earlier as-of replay. Unchanged observed input must report `no_new_observation` in the domain result, not a fresh zero.

**Ownership decision:** B17 #141/#100 owns static measure/method and analysis contracts. B02 #148/#11 is the receiving owner for a proposed immutable observation/resolver contract. Macro-event persistence is **deferred**, not assigned to issuer-only B03 #12 or to the NVDA-only pilot. B00 must approve an exact destination and writer after those receivers return their contracts. Until then, no macro canonical write is authorized by this decision. A future official-release packet, verified storage receipt and independent B01 #102/#105 replay remain open; no schedule is configured.

### Daily-state and CREDIT: retain, narrow, route

- **Daily-state #154 → B06 #108:** accept the architectural choice of one pure `compute_state` port composed with canonical traversal, not another engine/store. Retain the proposed SMA10/30/200, five-session slopes, Wilder ATR14, signed persistence/left-censor, strict prior-252 midrank (452 closes for SMA200), explicit units and null/warmup rules as **research specification pending exact method approval**. B02 #148/#183 owns calendar/resolver/one-session partition evidence; B06 owns any implementation; B01 #98 owns independent acceptance; B07 #93 owns predictive calibration. This revision does not approve the reference algorithm or modify the active traversal repair.
- **CREDIT #162:** accept reference-only composition through the same boundary, preserving source/instrument/pricing/peer/funding/exposure/calibration distinctions, as-of/TTD/FX and missing/error rules. Defer exact payload schema IDs until each owning domain supplies actual schemas and conformance evidence. Reuse B02 observations, B04 #175 and B07 #176; no new ledger, valuation or calibrated probability is implied.

## Independent acceptance and remaining implementation

B00 regression command: `python -m unittest discover -s orchestration/tests -p 'test_component_blackbox_contract.py' -v`. It checks legacy compatibility, local definition resolution, pins, strict fields, timestamp shape, explicit unknowns, typed fail-closed results, corrections and synthetic serialization. It deliberately demonstrates that structural validity does **not** validate units, hashes against actual bytes or availability-before-as-of. The first local run caught two absent date-time format enforcement cases; lexical guards were added. Independent review then demonstrated that impossible dates/times/offsets still passed with the optional format checker absent. An explicit standard-library checker and calendar/time/offset regressions corrected the test configuration without adding dependencies. A second review caught Python normalizing out-of-range offset minutes; explicit offset bounds and additional negatives close that case. Preserve the failed attempt in issue evidence.

B01 #105 receives the exact reviewed revision plus the existing integration-test/workflow scope, after collision checks. Independent acceptance must include nonzero tests, negative cases, schema/fixture hashes, actual source/workflow SHAs and hosted run URLs. For this structural increment it must independently verify the profile/definitions and schema-state rules; qualification of executable domain adapters requires the semantic gates above. Zero/skipped tests fail. Shared green CI is not proof of domain execution, source truth or deployment.

**Sequence:** independent structural acceptance → authorized integration with main CI → receiving domains implement the minimum needed payload adapters under their own claims → B01 verifies actual cross-component references/replay. No domain request is counted claimed or complete merely because this document routes it. No automatic retrofit, no writes outside #103's three recorded paths, no release/tag.

## Retained owner map

B02 market/FX observations and replay; B03 issuer-event ledger; B04 valuation; B06 descriptive traversal; B07 calibration; B08 authenticated hosted service; B10 CRWV operating economics; B17 market context/macro analysis; B19 revenue pools; B21 falsification. Each retains its domain schemas, financial semantics, fixtures and implementation. B00 owns only this shared boundary and arbitration; B01 owns independent CI. Component verification, integrated main with passing CI and entitled persistent operation remain separate states.
