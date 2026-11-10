# Independent named component source gates

B01 receiver #214 serves existing #129 and #98; #221 extends the same runner
for canonical #102 and the #100/101 → #217/218 → #219/220 chain. These are eight
named component jobs, never composed M1, source-data, calibration or live-service
acceptance. Domain owners keep implementation ownership; B01 owns only
this document, `domain_source_gate.py`, its test file and its dedicated workflow.
Shared CI and the merged #212 Project/Copier gate stay unchanged. The runner
reuses #212's revision, Git, fingerprint and strict-result helpers read-only.

## Named suites and reviewed source revisions

| Job | Producer | Source SHA | Minimum tests |
| --- | --- | --- | --- |
| domain-etf | PR127 / B04 #126 | 76710defee89171c905f9f90f5b683ecc84c80b0 | 66 |
| domain-ticker-patterns | PR99 / B10 #95 | f8e83f440023bcbf123687fc6c24248f1baf88c9 | 26 |
| domain-traversal | PR109 / B06 #108 | a235ff05bcb649e82fc97e3bd86db7645d49246d | 13 |
| domain-market-geometry | PR150 / B06 #149 | eade884d4423e5f7e6a899387e5f62bc3b24045a | 8 |
| domain-daily-state | PR160 / B06 #154 | 62e41633434602fd481b8a3ed7a1a92f3f628fcb | 22 |
| domain-market-context | PR101 / B17 #100 | 1517dc3cf549c4e2dd7695781bf01485b9dc6db6 | 38 |
| domain-ticker-comparison | PR218 / B17 #217 | 37f6bfe0ef8cc243cfe319526cc7471bc0b77f5f | 5 |
| domain-ticker-component | PR220 / B17 #219 | 4c64f0927c7e9858dbf266aafc1b069821c41911 | 5 |

Full `test_*.py` discovery runs independently for each directory. ETF discovery
covers all seven modules, not the historical seven-test command. Canonical
traversal has thirteen current tests after the B06 source repair; the earlier
six-test result and ten-test failing head are historical.
The daily-state oracle is research-only and its fixtures are synthetic. This
workflow does not replay the separate PR69 historical corpus or establish
provider entitlement, calendar integration, real ETF holdings/estimates/FX,
canonical market-data persistence or predictive usefulness.

The component adapter consumes the actual context `change()` and comparison
`compare()` files from two explicit read-only checkouts. Both dependencies use
the same actual-candidate-or-reviewed-pin selection, including removed-source
rejection. Their exact revisions, modes and tracked-file hashes are recorded and
checked before and after execution. Missing/duplicate/unexpected dependencies,
wrong revisions, falsely labeled fallback pins, absent tracked files and mutations
fail before acceptance. Caller environment paths are replaced with these checked
inputs. The adapter itself also enforces its reviewed code-byte hashes.
This is a bounded composition test, not verification of all #102 macro or provider
obligations. Comparison unit tests use an independent arithmetic oracle; the
adapter suite is what exercises real cross-component code. Shared conformance
regressions remain in orchestration CI and are not copied into domain suites.
Only synthetic offline fixtures execute in hosted CI; no private capture is uploaded.

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

Both source and acceptance preflight reject ignored untracked files and tracked
symlinks escaping their checkout, including inputs that Git status otherwise hides.
The same checks repeat after execution.

Checkouts do not persist credentials. Only contents-read permission is requested;
no secrets, live API, polling or deployment is needed. The ETF and ticker-component jobs install
`jsonschema==4.23.0`, the existing repository validator dependency, before suite
execution. Other domain jobs retain their standard-library-only environment.
Each source suite runs in a bounded child with bytecode disabled. Empty/reduced
discovery, import errors, skips, expected failures, unexpected successes, failed
assertions, timeout, dirty/untracked source or acceptance inputs, wrong revisions,
and tracked-input mutation fail. This is integrity checking, not hostile-code
sandboxing. Before/after complete tracked-source hashes and acceptance fingerprints
must match. Evidence is written outside both clean input checkouts.

Artifacts retain individual `evidence.json`, `source-files.json`, and `suite.log`,
plus named dependency file manifests for the adapter job.
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

For the composed adapter, additionally pass both explicitly selected dependencies:

```sh
python acceptance/tests/integration/domain_source_gate.py run --source component-source --expected-source FULL_COMPONENT_SHA --acceptance acceptance --expected-acceptance FULL_GATE_SHA --suite ticker-component --mode unmerged_dependency_only --output evidence/component --dependency market-context context-source FULL_CONTEXT_SHA unmerged_dependency_only --dependency ticker-comparison comparison-source FULL_COMPARISON_SHA unmerged_dependency_only
```

Use actual selection modes when source is integrated. `select --root candidate
--suite ticker-component` emits the component SHA/mode and both dependency
SHA/mode pairs. Dependencies cannot be omitted or silently inferred from the
machine's environment. Evidence must remain outside every input checkout.
The existing source suites still test actual candidate code after integration;
a future incompatible dependency correctly fails the adapter's approved hash
contract until its owner reviews and updates that contract.
