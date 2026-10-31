# Shared engineering bootstrap with Copier

Copier **9.19.1** is the selected template engine. It is an MIT-licensed development
tool, free to use, and introduces no hosted service or runtime dependency. Its
native Git provenance, answer storage and update algorithm manage the template;
there is no custom scaffolding engine or task database.

The repository-root `copier.yml` selects **only** `orchestration/bootstrap/template`.
Cloning this repository as a template does not copy market data, orchestration
state, source code, worker instructions or GitHub workflows into another project.

## Standard baseline

The same source produces five files for any project:

- `.editorconfig`: editor formatting conventions.
- `pyproject.toml`: standard Ruff/pytest configuration, not packaging metadata.
- `.pre-commit-config.yaml`: optional upstream validation hooks, including conflict checks.
- `README.md`: repository/maintainer links, existing unittest command and update instructions.
- `.copier-answers.yml`: generated source revision and answers for native updates.

Required inputs are project name, GitHub owner/repository, maintainer login and a
relative test directory. `basket.yml` is the _BASKET input profile. It is **not**
a manually fabricated answers file. Configurations do not install or execute
Ruff, pytest or pre-commit; development dependency pinning and workflow adoption
are separate reviewed steps. Existing unittest tests remain supported.

There are no Copier tasks, Jinja extensions, migrations, secret inputs, GitHub
mutations, paid invocations, auto-merges or release hooks in this template.

## Agent-operated generation

The owner can review the draft PR from a phone. The agent/CI handles these commands;
no terminal action or credential entry is required from the owner for rendering.

Install the pinned development tool in an isolated environment using the
repository's approved package installer and `requirements.txt`. Generate a new,
empty project directory from an **exact reviewed template commit**:

```sh
copier copy --defaults --vcs-ref=<reviewed-commit> \
  --data project_name='Example Project' \
  --data repository=example/example-project \
  --data maintainer=example \
  --data test_directory=tests \
  gh:whiterosecoffee/_BASKET /tmp/example-project
```

To preview _BASKET configuration from a checkout, use the input profile:

```sh
copier copy --defaults --vcs-ref=<reviewed-commit> \
  --data-file orchestration/bootstrap/basket.yml \
  gh:whiterosecoffee/_BASKET /tmp/basket-bootstrap-preview
```

Add `--pretend` for a no-write preview. Do not point first-time generation at an
existing repository root: `README.md`, `pyproject.toml` and hook configuration may
already have owners and custom settings. Render into staging, review the diff,
and have the authorized domain owners integrate compatible configuration.

`adoption/` is a real rendered _BASKET preview committed for review, **not** an
installed root toolchain. Its answers pin the actual remote template commit.
Its files apply only in that preview directory; it installs no CI/hook behavior.
Follow the generated README's test command from the _BASKET repository root.

## Native updates

Generated projects should commit their answers and files into Git. With a clean
worktree, run `copier update --defaults --vcs-ref=<new-reviewed-commit>`, review
the diff/conflicts, run tests, and open a PR. Do not edit `.copier-answers.yml`
by hand. Without an explicit ref, Copier can select the latest version tag;
use explicit commit SHAs here because no shared-template release is authorized.

Real copy/update integration tests use temporary Git repositories and local fixture
tags only. They exercise generation for _BASKET and an unrelated repository,
valid TOML/YAML, recorded provenance, deterministic output, invalid inputs,
no-write preview, preservation of local changes, and repeated-update idempotency:

```sh
python -m unittest discover -s orchestration/bootstrap/tests -p 'test_*.py' -v
```

These tests require the isolated Copier requirements environment; existing runtime
and schema tests remain unchanged. GitHub-native tasks and acceptance evidence
remain authoritative. Template generation is not a claim of integrated validation.

## Ownership and B01 handoff

B00 owns root `copier.yml` and `orchestration/bootstrap/**`. Catalog 1.6.1 assigns
the root file, with the version manifest kept aligned. No application/core release
is created. Same-conversation worker #134 / draft PR #135 owns this increment;
all other active worker files remain untouched.

B01 receiver prompt (tracked on #134, pending): independently install the pinned
Copier development tool, run the bootstrap tests and existing B00 suites at the
exact PR head, and wire the bootstrap tests into B01-owned CI on your own branch.
Review root tool configuration separately before adopting generated settings.
Do not overwrite existing project README, packaging metadata, CI or ownership.
No merge, release or production Project configuration is authorized by this handoff.

Sources: [Copier configuration](https://copier.readthedocs.io/en/v9.19.1/configuring/)
and [native updates](https://copier.readthedocs.io/en/v9.19.1/updating/).
