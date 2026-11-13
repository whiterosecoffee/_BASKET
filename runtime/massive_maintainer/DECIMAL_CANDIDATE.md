# Decimal-preserving candidate contract

Owner: existing _FETCH/B02. Scope: representation experiment only, not a canonical
schema change, resolver integration, data migration or promotion. Source checkpoint:
`745b9c8f49222ecb4c2c53d86f8aa6c7cf92a868`.

## Predetermined acceptance

1. Preserve decimal numeric values exactly and retain original line bytes, including
   lexical precision. Never convert volume through float or round it to an integer.
2. Replay produces identical output, independent of input-artifact ordering. Repeating
   an identical artifact descriptor does not duplicate it.
3. No mutation of caller inputs or original files. The pure transformer has no IO API.
4. Explicit exchange-date/timezone/session-window and caller-declared basis metadata.
5. Unknown/unsupported basis and conflicting/incompatible observations are quarantined.
   Every result remains `unqualified_candidate`, `promotable=false`.

## Interface and reconciliation rules

`decimal_candidate.build_candidate(inputs)` accepts small byte artifacts with expected
SHA-256, explicit vintage ID, basis dictionary and optional parent-artifact provenance.
It parses numbers as Decimal and stores numeric values as decimal strings. The exact
raw line is retained as base64 with its own hash; decoded values alone are not an
original vendor response. Provenance may record the retained parent file hash and line.

The key is ticker plus integral minute timestamp. Source-artifact replay is deduplicated
by descriptor hash. Distinct occurrences remain present. Same values and basis are
reported as identical duplicates; different values are conflicting vintages. Different
basis declarations, including incompatible evidence, remain unreconciled. No selected
vintage is produced. Unknown basis and all members of conflicting/incompatible groups
are quarantined rather than dropped. Invalid records retain their exact bytes.

Complete basis declarations require shares, a supported adjustment label, explicit
adjustment-as-of, America/New_York, 1m, and source-bound evidence hash. These are caller
claims, not independent verification. Even complete declarations permit representation
only. Session windows classify clock times, not verified exchange calendars or complete
trading sessions. This module is not wired to the production resolver or publisher.

## Local evidence and tests

`python -B -m unittest runtime.massive_maintainer.test_maintain runtime.massive_maintainer.test_decimal_candidate -v`
passed 26 offline tests: 19 existing resolver/maintenance tests plus 7 candidate tests.
They cover exact decimal/raw preservation, immutable inputs, deterministic replay,
duplicate retention, conflicting vintages, unknown/incompatible basis, hash rejection,
invalid records and a no-IO control. The pure representation positive control is not
qualification evidence.

An isolated two-record experiment on retained October 1 vintages kept the differing
close values and exact fractional volumes separately. Both records were quarantined;
reversing input order produced identical bytes. Both small parent artifacts were
rehashed unchanged. The private candidate and receipt remain outside Git and all data
stores; no original or staged history was changed. The experiment does not duplicate
the archive, resolve the vintage conflict or establish current turnover readiness.

## Authoritative documentation versus row-specific evidence

Read on 2026-11-13:
- [Custom Bars](https://massive.com/docs/rest/stocks/aggregates/custom-bars): t is an
  aggregate-window start in Unix milliseconds; v is volume; adjusted selects split
  adjustment; aggregates may include premarket and after-hours observations.
- [Decimal volume](https://massive.com/knowledge-base/article/why-does-volume-return-as-a-decimal-value-from-the-aggregates-endpoint): fractional-share trades can
  produce decimal volume; preserve it as decimal rather than integer. Fractionality
  itself is not evidence of split adjustment.
- [Split/dividend adjustment](https://massive.com/knowledge-base/article/is-massives-stock-data-adjusted-for-splits-or-dividends): historical aggregates support
  split adjustment, not dividend adjustment.

These sources clarify general units/representation. They do not authenticate the
retained normalized rows or supply their exact adjustment vintage. Still required:
- Original response envelope/request ID and adjusted flag bound to each retained
  artifact, with request parameters, receipt time and immutable hash lineage.
- The executed transformation revision connecting provider v to retained vol, and
  confirmation no preceding float conversion changed its original numeric lexeme.
- Row-specific split/share basis and adjustment-as-of/factors needed for cross-vintage
  comparison, plus a compatible dated shares-outstanding denominator for turnover.
- Explicit vintage-selection policy backed by source evidence; retained October 1
  price/VWAP changes must not be silently overwritten or averaged.
- Comparable session coverage and independently accepted consumer contract. Missing
  minutes are not automatically missing trades or missing vendor observations.

Existing fetch code requests adjusted=true and retained ledger/hash lineage provides
local support, but cannot substitute for the missing original response binding.
Unknown actual-vintage basis remains quarantined despite the general documentation.

## Status and next action

Owner-run tests and the small representation experiment passed. Independent candidate
acceptance is pending; do not dispatch a duplicate of the existing resolver review.
No claim of qualified history, current data, consumer adoption or operational refresh.
Next: existing _FETCH assembles the missing response/transform/basis evidence from
retained artifacts without acquisition. _MAP contract reconciliation is a recommendation
to its existing owner, not permission for this lane to edit shared files. Migration,
history fetch, scheduling, merge and deployment remain outside this increment.
