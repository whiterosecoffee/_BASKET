# Review gate for the read-only tool

Assess the **actual PR head**, not a reported local example. Check issue #278 exclusive paths, known main SHA, changes in other B06 PRs, and input/return contracts. Run `python -m unittest engines.traversal.tool.test_tool -v` against the exact source, with nonzero test count, no skips/failures, log URL and source hash; additionally invoke a historical synthetic fixture with the real merged `engines.traversal.metrics` module, not just the mocked test. Check CLI exit code 2 for current mode and confirm no alerts or persistent files created.

Negative cases: malformed input/digest, out-of-order bars, missing bar, future first availability, incomplete tail, unknown calendar/entitlement, unavailable TTD, non-USD and two isolated instruments. A test that simply checks the same result against itself does not prove replay equivalence. A passing shared workflow without these tests is insufficient.

Promote only the verified adapter criterion. Do not promote authoritative source coverage, B10 transactional restart, CRWV/ORCL M1 journal replay, independent point-in-time calendars, deployment or live-alert readiness. Route exact missing evidence through B01 #98, B00 #96/#148 and B02 #152; recommend the smallest corrective action. Do not claim merged integration until approved and independently checked main.
