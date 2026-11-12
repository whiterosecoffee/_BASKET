# Verification receipt, 2026-11-12

Scope: read-only ledger correlation only. No canonical write, provider fetch, original-source modification or publication.

- 21 synthetic regression tests passed locally. Independent reviewer reran all 21 successfully.
- Independent reviewer reproduced prior failure cases (scalar ledger, object timestamp and invalid dates), then confirmed sanitized rejection after correction. Provider symbol and binder-identity checks reviewed.
- Reviewed ledger_binding.py SHA256: 9a4359704d4b12fb389ed06a693a041d665c0da97085475293401b84f9c8795f.
- Final binder ran twice on previously pinned real artifacts with identical receipts. 5673 staged bars, 5670 fractional-volume rows; current output matches historical apply hash; canonical_eligible=false.
- Independent assessment review rehashed both source files and recomputed date/count and October 8 overlap results. All 941 selected legacy volumes equal staged values rounded half-up; 940 differ from retained fractional values.
- Existing sanitizer pure-function behavior was independently tested in memory: representation dependent and non-idempotent. Original module entrypoints were not run.
- git diff --check passed. No repository-wide or hosted CI run claimed; this is an isolated local increment based on the existing owner branch, not integrated main.
- No blocking review finding remains within this bounded evidence-correlation scope. Historical code/source authenticity and production generation acceptance remain explicitly unverified.

## Volume-guard increment

- Independently reviewed volume_guard.py SHA256: 94d23fa6e351b3d204a8012cd8a54f065d2122b27080a67f3c555eaf71698853.
- All 33 tests passed locally and independently (21 ledger + 12 volume guard).
- Independent additional negatives rejected extreme exponents, excessive precision, boolean identities, duplicate keys and nested malformed JSON.
- Independent reduced-Decimal-context check (precision 2) still detected exact differences and accepted equal high-precision values.
- No blocking finding within pure volume-equality scope. Units remain assertions; canonical eligibility remains false. No original data accessed or changed by this increment.
