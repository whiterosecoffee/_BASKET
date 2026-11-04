# Validation evidence — 2026-10-29

Local Python 3 standard-library runner actually executed:

```
python3 -m unittest discover -s engines/composites/market_context/tests -v
Ran 27 tests
OK
```

These tests include the checked-in captured Massive responses, not just synthetic
values. At the full capture cutoff 2026-10-29T16:44:33.698484Z, research mode
admits 65 of 66 configured company candidates (98.48% coverage). PAYP is unresolved
and remains missing in the denominator. Equal-weight covered price-return mean
is approximately -1.6525%, with 26 advancers and 39 decliners. This is provisional
research-basket performance, not a personal portfolio or canonical whole-universe
index. All quote entitlement metadata is unknown in the captured API response;
strict mode withholds the corresponding price aggregates. The full macro score
remains null: no macro observations were silently filled from unrelated quotes.

The earlier 12:38 ET snapshot contains only four of these company candidates.
It cannot establish a 66-company interval return. Matched-interval aggregate is
withheld even when the latest capture has broad coverage. CRWV's move from the
08:27 price $59.20 to $63.58 at 12:38 is reproduced as +7.39865%, and its
QQQ-relative recovery is separately described. No earnings causality is inferred.

## Attempt log

1. Initial 23-test prototype passed.
2. Added two admission/fresh-trade tests and optional gross-turnover output.
   The 25-test run failed with 12 `KeyError: volume` errors: fixtures without an
   optional volume field reached a branch that treated missing volume as zero.
3. Corrected presence check before reading optional volume. The actual 25-test
   rerun passed. Original failure is preserved here rather than called skipped.
4. Added two captured-session acceptance tests. Actual final 27-test run passed.

## What has not passed

- Independent B01 execution of this domain suite at exact PR head.
- Merge and post-merge main validation.
- Production source-to-worker-to-journal integration and operational entitlement.
- Authoritative B00 basket admission/group mapping and B06 traversal bridge.
- Full macro-series acquisition, publication-calendar validation, and matched
  five-session macro impulse baselines.
- Statistical forecasting or probability calibration. None is claimed.

Static captures are historical and cannot be presented as a working live feed.
No shared CI, schema, canonical registry, ticker market store, runtime adapter,
or deployment file was modified. Related ORCL integration request #76 is read
as a dependency, not a grant to edit another owner's tracker.
