# FETCH data purposes v1

Machine-readable option set: PURPOSES.json (`fetch.data-purpose-options@1`).
This is the source lane's portable contract for adoption, not a shared schema release.

Timestamped observations do not become false or unusable because the clock advances.
Historical truth and suitability for a latest/current question are separate concerns.
Corrections preserve earlier bytes/vintages; they do not justify silently treating a
later correction as information available at an earlier analysis cutoff.

| Purpose | Eligibility | Time policy |
|---|---|---|
| historical | Validated returned bars for exact symbol/date/grain/basis | No age expiry; no completeness claim |
| historical_interval | Exact declared session interval, basis and every minute present | No age expiry |
| as_of | Historical interval plus selected vintage availability and all exposed event ends at/before cutoff | Cutoff, not TTL |
| latest_complete | Declared completed interval, OK source, complete pagination and all minutes present | Explicit finite recency policy |

API: `resolve(pointer, ticker, day, required_through=None, max_age_seconds=1200,
coverage=None, purpose=None, as_of=None)`; the last three arguments are keyword-only.
Historical returned bars omit required_through; other purposes specify interval end
and coverage. If purpose is omitted, the legacy required_through distinction selects
historical or latest_complete. Historical purposes ignore max_age_seconds and queued
requests normalize it to null. Invalid latest budgets still reject before data IO.

Massive t is the UTC epoch-millisecond start of a minute. Its completion is t+60000;
partition date is the exchange-local America/New_York date. Never map a UTC date or
another ticker's partition into the requested component. Split-adjusted USD bars
and stable dated instrument identity remain this adapter's supported basis. A
consumer requiring another basis receives no automatic conversion or invented data.

The as_of implementation checks the currently indexed vintage only. All exposed
partition event ends must precede the cutoff. Entry/raw retrieval timestamps must
be known and at/before it; recorded reference retrieval also participates. Retrieval
is a conservative known-by bound, not a claim about exact first market availability.
If a later correction is indexed, refuse it for the earlier cutoff even when an old
generation exists. Selecting and validating older generations is separate work;
this change does not search them or overwrite quality manifests. Raw metadata and
producer primitives remain the reviewed cooperative trust boundary, not proof of
authenticated provenance. Existing historical provenance gaps remain unresolved.

Sparse intervals remain coverage_unresolved; unknown/no-trade/calendar statuses are
not inferred from absent minutes. DELAYED data can remain historical observations
but cannot qualify latest. Historical reconciliation requests do not authorize
acquisition, and age alone never generates historical refresh demand.

## Ready-to-use shared-owner handoff

B00/existing template owner: adopt fetch.data-purpose-options@1 from this existing
B02 source lane into the existing worker-library/compiled scope and launch-template
contracts under your ownership. Ask ticker components for purpose, exact instrument,
date/grain/session/adjustment, interval/completion and (only for latest) recency;
for as_of also require cutoff/vintage evidence. Route unmet requirements to the
existing FETCH owner, never a ticker-owned vendor client. Preserve separate code
acceptance, dataset qualification and runner evidence in receipts.

Before changing a generic FETCH master implementation, identify its actual existing
owner and branch and confirm disjoint paths. This lane has not created or claimed
such a branch. The generic master remains a design role; Massive is the implemented
provider adapter here. Do not infer a second writer from this contract.

Adoption acceptance: historical data stays eligible across wall-clock advancement
without refresh; later correction/availability cannot leak into earlier as_of;
latest invalid budgets and sparse/delayed intervals fail closed; exact ticker and
exchange-date mapping hold; request/receipt purpose survives dispatch. Run through
the existing independent B01 reviewer. No shared template or master-branch adoption
is claimed until its owner retrieves and verifies this handoff.
