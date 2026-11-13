# Purpose-specific temporal options (local proposal)

Historical event timestamps do not expire merely because time passes. This
profile selects policy explicitly from request purpose, never from event age.
It is a pure synthetic qualification example, not a _FETCH repair, shared-schema
change, entitlement checker, or operational acceptance gate.

## Choose and adopt

| Explicit option | Use when | Required evidence / rejection | Governing adoption |
|---|---|---|---|
| `current` | Consumer needs latest/current observations | Event watermark and source-observation age within separate budgets; matching last successful generation and known watermark coverage. Stale evidence fails. | _FETCH owner selects meaningful market/session budgets; #103 reconciles request contract. |
| `historical_as_of` + `as_of_visible` | Reproduce information available at a fixed cutoff | Pinned generation, requested half-open interval, session and adjustment basis, provenance, known coverage, entitlement, revision available by cutoff. Visible supersession/conflict invalidates; later corrections cannot leak into this view. | #103/#105 qualify point-in-time semantics; _FETCH supplies complete source revision evidence. |
| `historical_as_of` + `invalidate_on_known_correction` | Consumer requires requalification after any known correction | Same historical checks, plus rejection when a known correction supersedes the pinned generation, even after cutoff. It blocks the old result; it does not substitute later data into the old cutoff. | Consumer and _FETCH owner agree correction invalidation policy; #105 verifies it. |
| Cache refresh advisory | Local cache housekeeping, independent of data purpose | `cache_refresh_due` is reported separately; old cache age never alone invalidates historical truth. | Runtime/_FETCH owner manages cache persistence and retrieval. |

`temporal.examples.json` has four complete synthetic packets, including explicit
no-trade coverage. All modes use provider-neutral requests. `_FETCH` remains the
master; Massive adapter identity/capabilities stay in the existing
`semantic.data-example.json` dependency metadata. Consumers read qualified local
data; only an existing owner may acquire, refresh, persist or repair it.

## Contract and reuse

`temporal.py` reuses lifecycle request identity/revision field definitions and
canonical component artifact references/hashing. It composes the existing local
shape helpers, without changing worker/lifecycle schemas or introducing a shared
status authority. It deliberately does **not** send historical packets through
the older lifecycle snapshot's blanket `qualified_until` check. Canonical adoption
must select this purpose-specific qualification at the data boundary; old accepted
lifecycle fixtures retain their original, narrower semantics.

Call `evaluate(packet, expected_request=retained_request, now=explicit_clock)`.
The caller must retain the expected request independently: it pins purpose,
interval, cutoff, session, basis, revision policy and input generation digest.
Changing both request and expected request creates a different declaration; this
function cannot authenticate that change or prove the real source's availability.
The CLI uses each static fixture request as its expected request for demonstration.

The entire generation content (identity, revision, provenance, coverage, session,
basis and watermark) is hashed and matched to request `input_revision`. Missing
provenance, integrity mismatch, unknown range, overlaps, future-visible revision,
pinned generation mismatch, conflicting applicable revision, session/basis mismatch
or denied entitlement reject historical use. No-trade is explicit evidence, never
inferred from an empty or missing range. Session/calendar correctness, source
entitlements and correction-ledger completeness remain owner-attested facts.

Observation/retrieval time, cache storage age and the point-in-time cutoff are
separate. Observation timestamps cannot be in the future or precede the selected
revision's availability. Historical observation age has no TTL rejection. Current
requests apply their explicit watermark and observation budgets. Supplied coverage
beyond the historical cutoff rejects; post-cutoff correction records under
`as_of_visible` are excluded from the view and are not emitted as data.

An optional acceptance binding includes request, generation and applicable
correction-view hashes. Correcting a selected generation requires new qualification
and acceptance. `acceptance_current` means that supplied binding still matches the
selected policy, not that an independent reviewer is authenticated. Clock advance
alone leaves valid historical acceptance intact. Corrections unrelated to the
selected generation can conservatively invalidate the correction-view fingerprint;
the owner may design a more selective authenticated ledger during integration.

A stale current packet may produce `owner_refresh_request` only if freshness is
the sole failure, the request's attempt budget remains, and its deadline has not
passed. It is a proposal addressed to `_FETCH`, not an invocation. There is no
retry counter persistence or scheduler. Every result remains
`execution_authorized=false`; historical invalidation never dispatches refresh.

## Reproduce and integrate

```powershell
python -B -m orchestration.clean_templates.temporal
python -B -m unittest discover -s orchestration/clean_templates/tests -p test_temporal.py -v
python -B -m unittest orchestration.tests.test_clean_template_seed -v
```

Named tests cover historical validity through 2099, unknown versus no-trade,
missing range/provenance, visible and post-cutoff corrections, new acceptance
for corrected generations, forward-looking revisions/coverage, fixed cutoff,
session/basis/entitlement/integrity, stale current watermark and observation age,
bounded owner refresh, deterministic nonmutation and no network/archive/dispatch.
See `temporal.validation.json` for executed counts and source/log hashes.

The accepted semantic predecessor is `47bd018671f8f56165d0815570595707b85b03d0`;
its 20/99 tests and independent bounded acceptance remain historical. This temporal
increment needs separate exact-revision independent review. Adoption remains 0/8.
The appended `temporal_options` in `semantic.adoption.json` routes #230 map,
#134 Copier, #201 instructions, #103 shared contracts, #105 semantic acceptance,
and existing runtime/_FETCH owner gates through the parent. No duplicate dispatch,
other-owner edit, publication retry, hosted claim, merge or deployment occurs.
