# Clean template boundary seed

This is a small JSON-first seed contract, not a new controller, FETCH implementation,
Copier replacement, or component kit. Copy and edit `seed.json` as a design input.
The validator imports no archived implementation and never opens reference locators.
Archived and candidate components can inform intent without gating a clean local probe.

`references` contain rationale and pointers only. `requires` names actual capabilities,
not issue numbers, archive paths or legacy branch state. Callers must establish capability
availability independently; supplying a name is not proof of implementation or permission.
`ready_for_local_probe` means the manifest boundary check passed, NOT tested component,
accepted outcome, authorized execution, merged code, or operational readiness.

Example from repository root:

```python
import json
from pathlib import Path
from orchestration.clean_templates.validate import validate_seed
seed = json.loads(Path('orchestration/clean_templates/seed.json').read_text())
print(validate_seed(seed, []))
```

Fixed suite:
`python -m unittest discover -s orchestration/clean_templates/tests -v`

Dependencies: existing repository `jsonschema` package. No network, credentials, source
copying, data-plane mutation or archived file availability is needed. This seed's local
schema stays inside its subtree; shared contracts and _MAP remain with existing owners.
Its acceptance list is a predeclared plan, not verification evidence. Source issues #103
and #226 are read-only design references. Canonical request #136; scoped owner #243.

Next: independently review this boundary, then adapt one real clean component's ports and
acceptance tests. No legacy integration or broad five-worker launch is implied.
