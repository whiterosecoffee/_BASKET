# _BASKET — Standard module structure

**Owned by:** B00. A module is a directory under `engines/<name>/` (or a service under `services/<name>/`). Every module has the same layout:

```
engines/<name>/
  README.md        # required sections below
  <name>.py        # entry point with a main()/run() function (stdlib only unless approved)
  contract.json    # input/output contract (see schemas/ and architecture/ for black-box contracts)
  fixtures/        # small offline inputs and expected outputs
tests/test_<name>.py   # offline tests, owned by the module's spark
```

`README.md` sections, in order: `Purpose`, `Owner spark`, `Inputs`, `Outputs`, `Run`, `Tests`, `Evidence and limits`.

Rules: the owner spark is the only writer; inputs and outputs carry provenance and as-of timestamps and report USD; no network in tests; a module never writes outside its spark's `write_paths`.

## Enforcement
`python orchestration/validate_module_structure.py` lists the gaps per module. Existing modules are owned by other sparks, so the gaps are reported (exit 0) and handed to each owner as a handoff issue; add `--strict` to fail on gaps once they are fixed.
