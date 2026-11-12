# Callable clean-seed probe

This is the smallest worker-input adaptation of the existing seed boundary,
not a worker launcher, FETCH implementation, data-flow validator or template factory.

Input: one object with `seed` and an explicit JSON array `available_capabilities`.
Output: `state`, `errors`, `missing_capabilities`. Invalid envelopes raise
`ValueError("INVALID_REQUEST: ...")`; invalid seeds return `state=invalid`.
Missing capabilities return `blocked`; structurally ready seeds return
`ready_for_local_probe`, never accepted or authorized.

```python
import json
from pathlib import Path
from orchestration.clean_templates.component import probe
seed = json.loads(Path("orchestration/clean_templates/seed.json").read_text())
print(probe({"seed": seed, "available_capabilities": []}))
```

`component.json` reuses the existing component manifest schema. Its local request
and readiness schemas describe these ports; this is not the qualified-reference
runtime envelope. Callers still must establish capability truth and permissions.
No references are opened, inputs mutated, worker dispatched, or market data read.

Acceptance declared before adaptation: manifest/schema validation; ready,
missing/supplied capability and invalid-seed outputs; malformed/duplicate inputs;
deterministic no-mutation repeat; no archived reference access. Eight additional
tests plus twelve seed tests are discovered by the existing hosted bridge.
