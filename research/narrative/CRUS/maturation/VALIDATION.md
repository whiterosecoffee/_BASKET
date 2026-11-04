# Validation and review maturity

Local execution on 2026-11-04; independent CI is pending B01 #193.

Executed from repository-relative root:

```sh
python -m unittest discover -s research/narrative/CRUS/maturation -p 'test_*.py' -v
python research/narrative/CRUS/maturation/audit.py research/narrative/CRUS/maturation/snapshot-2026-11-04.json --as-of 2026-11-04T23:33:21Z
```

22 tests pass, none skipped. First local run passed 19 tests. Manual code review
then identified malformed nested input and availability/ingestion chronology gaps;
three additional tests and strict validation were added, all 22 pass. No failed test
run was hidden. The first successful suite alone did not establish those guarantees.
Synthetic fixtures test behavior, not issuer economics or predictive performance.

Real snapshot audit returns `blocked`, CLI exit 2, all eight required metrics
blocked, valuation null and investment_score null. This expected research blocker
is not a failed implementation test and must not be rewritten as financial readiness.
Only four historical source-reviewed metrics are present; four current inputs are
explicitly missing. Hypotheses remain unvalidated.

Post-increment self-assessment using the same PLAN.md rubric:

| Dimension | Before | After | Remaining deduction |
|---|---:|---:|---|
| Scope compliance /20 | 2 | 18 | Canonical CRUS home pending B00; only staging scope implemented |
| Test evidence /25 | 0 | 15 | Local adversarial tests; independent exact-head CI absent |
| Source/provenance /20 | 12 | 12 | Field-level gaps now explicit, but current source coverage still incomplete |
| Dependency discipline /15 | 3 | 10 | Owner handoffs published, receiver acceptance unverified |
| Reproducibility /10 | 2 | 8 | Deterministic input/code fingerprints; no canonical financial replay |
| Reporting clarity /10 | 7 | 8 | Plan/contracts/states clear; end-to-end financial outcome pending |
| **Total /100** | **26** | **71** | Research engineering maturity only; not stock quality |

Financial coverage has not been promoted by passing software tests. No 2027/2028
price target, AI revenue estimate or current investment rating was calculated.

Baseline discovery: main b4910122a4c3f6ade747f2e4d59bd2d2e84b3c95;
59 open PR file lists checked with zero overlap. PR38 B21 precedent and PR127 B04
valuation code paths read; existing engine reviewed. Current calendar date is
2026-11-04. SEC August shareholder letter re-read; November issuer page re-open
failed. Historical earlier retrieval remains in conversation, not current validation.
No Massive calls or market-data writes occurred. Network-policy file was absent
in this local executor; connected GitHub/web tools were used, no network bypass.

Published commit, PR-head comparison and CI state belong to the issue/PR resolution
comment because committing a file containing its own Git SHA is circular. Hashes
inside audit-result bind the exact input and implementation bytes instead.
