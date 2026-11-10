# Independent ETF and traversal source gates

B01 receiver #214 serves existing #129 and #98. These are five independent
component jobs, never composed M1, source-data, calibration or live-service
acceptance. B04/B06/B10 keep implementation ownership; this receiver adds only
this document, `domain_source_gate.py`, its test file and its dedicated workflow.
Shared CI and the merged #212 Project/Copier gate stay unchanged. The runner
reuses #212's revision, Git, fingerprint and strict-result helpers read-only.

## Named suites and reviewed source revisions

| Job | Producer | Source SHA | Minimum tests |
| --- | --- | --- | --- |
| domain-etf | PR127 / B04 #126 | 76710defee89171c905f9f90f5b683ecc84c80b0 | 66 |
| domain-ticker-patterns | PR99 / B10 #95 | f8e83f440023bcbf123687fc6c24248f1baf88c9 | 26 |
| domain-traversal | PR109 / B06 #108 | 318b24aaae49e50bbe4d242c73f0a757b72f6f34 | 10 |
| domain-market-geometry | PR150 / B06 #149 | eade884d4423e5f7e6a899387e5f62bc3b24045a | 8 |
| domain-daily-state | PR160 / B06 #154 | 62e41633434602fd481b8a3ed7a1a92f3f628fcb | 22 |

Full `test_*.py` discovery runs independently for each directory. ETF discovery
covers all seven modules, not the historical seven-test command. Canonical
traversal has ten current tests; the earlier six-test result is historical.
The daily-state oracle is research-only and its fixtures are synthetic. This
workflow does not replay the separate PR69 historical corpus or establish
provider entitlement, calendar integration, real ETF holdings/estimates/FX,
canonical market-data persistence or predictive usefulness.

## Revision and failure rules

The candidate is the actual PR head or main push SHA, never a synthetic merge
source. The acceptance checkout uses the exact workflow revision. If a domain's
markers exist, its candidate source must pass; partial source never selects a
fallback. If every marker is absent, complete Git history must also show no prior
marker. Only then is the reviewed exact source above selected and explicitly
labeled `unmerged_dependency_only`. Removed previously integrated source fails.
The legacy `engines/traversal/range.py` is not the new metrics component marker.

Normal runs cannot select an arbitrary moving branch or dispatch override. Each
job has a fixed producer pin. A newer producer head needs review and a pin update;
older success never certifies a newer producer revision. After source integration,
normal runs test actual head. A local diagnostic `--requested` exact SHA remains
available on `select`, labeled `explicit_exact_revision`.

Checkouts do not persist credentials. Only contents-read permission is requested;
no secrets, live API, dependency installation, polling or deployment is needed.
Each source suite runs in a bounded child with bytecode disabled. Empty/reduced
discovery, import errors, skips, expected failures, unexpected successes, failed
assertions, timeout, dirty/untracked source or acceptance inputs, wrong revisions,
and tracked-input mutation fail. This is integrity checking, not hostile-code
sandboxing. Before/after complete tracked-source hashes and acceptance fingerprints
must match. Evidence is written outside both clean input checkouts.

Artifacts retain individual `evidence.json`, `source-files.json`, and `suite.log`.
Failure artifacts are uploaded with `always()` and absent artifacts are errors.
Evidence includes exact source and acceptance SHAs, producer PR, mode, executed
count, failed/error/skip counts, manifest hash and immutability result. Shared
strict checks run separately. No repository required-check settings are changed.

## Local reproduction

Run gate regressions:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/integration -p test_domain_source_gate.py -v
```

Use clean independent Git source/acceptance checkouts and exact SHAs:

```sh
python acceptance/tests/integration/domain_source_gate.py run --source source --expected-source FULL_SOURCE_SHA --acceptance acceptance --expected-acceptance FULL_GATE_SHA --suite etf --mode unmerged_dependency_only --output evidence/etf
```

Repeat with each named suite, using its own source checkout. Local results are not
hosted CI. Hosted results do not establish integration or release until main
integration and its checks are independently verified.
