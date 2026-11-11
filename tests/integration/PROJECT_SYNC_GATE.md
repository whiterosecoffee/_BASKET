# Project adapter and Copier exact-source gate

B01 receiver #210 implements the existing #134 handoff. Source remains B00 PR135.
Only the dedicated workflow, this document and the two `project_sync_gate` Python
files are owned here. Shared CI and all source files remain unchanged.

The named `project-sync-adapter` and `project-sync-copier` jobs run on relevant
pull requests, main pushes, or explicit dispatch. Pull requests use their exact
head, not the synthetic merge source. The independent runner is checked out at
`github.workflow_sha`, separately from source, and both revisions are recorded.
There is no Project token, live API, event synchronizer, installed hook or runtime.
Checkout credentials are not persisted. Dependencies are pinned: Copier 9.19.1,
jsonschema 4.23.0 and PyYAML 6.0.2 on Python 3.12.

When none of the adapter/bootstrap markers exists on the candidate, the gate uses
reviewed PR135 SHA `743641f825dd7e5b7fe6b1e1958f634301cdcec4` and explicitly records
`unmerged_dependency_only`. This proves that source, not integration into main.
If any marker exists, partial source is tested and must fail rather than falling
back. Absent source requires complete candidate Git history and no historical
marker path; deletion of previously integrated source fails rather than using
the old pin. Explicit dispatch accepts only a full exact source SHA. After source merges,
normal runs use actual head. Update the dependency pin only after B00 review if
PR135 advances before integration; older passing evidence does not certify a
newer source revision.

Each suite runs in a separate bounded child process with bytecode disabled.
Adapter discovery must execute at least 88 tests; native Copier at least six.
Any error, failure, skip, expected failure, unexpected success, missing suite,
short discovery, mismatched checkout, changed/untracked input or timeout fails.
The complete tracked source file SHA-256 manifest is compared before/after, as
is the acceptance checkout. This is integrity checking, not a sandbox against
hostile tests. Domain source tests remain independently owned by B00.

Artifacts retain `evidence.json`, `source-files.json` and `suite.log` per named
suite, including failure results when execution starts. GitHub artifact retention
is finite; issue #210 records durable run URLs and source revisions. Missing
artifacts fail rather than claiming successful execution. Shared strict CI runs
separately and this workflow does not modify repository-required-check settings.

Local gate regression:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/integration -p 'test_project_sync_gate.py' -v
```

For a domain run, use separate clean source and acceptance Git checkouts, pass
exact SHAs, and place evidence outside both:

```sh
python acceptance/tests/integration/project_sync_gate.py run --source source --expected-source FULL_SHA --acceptance acceptance --expected-acceptance FULL_GATE_SHA --suite adapter --mode explicit_exact_revision --output evidence/adapter
```

Repeat with `--suite copier`. These offline suites do not satisfy #134 A5 full
live Project configuration, applied views/order or operational-cycle acceptance.
