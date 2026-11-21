# Component-export qualification tool

Problem: a connected repository can expose immutable files while a local full
Git checkout is unavailable. Manual copying and a green shared workflow can
obscure which bytes and named tests were actually exercised. A component-only
export needs a narrower, explicit integrity claim.

Parent: [existing B01 source gates](../DOMAIN_SOURCE_GATE.md). This variant reuses
their `revision` and `strict_result` helpers through `project_sync_gate.py`.
Prefer the existing `domain_source_gate.py` for complete clean Git checkouts;
it verifies more repository context. Do not fork its implementation or claim
equivalence between a component export and a full repository checkout.

## Contract and execution

Input: an independently retrieved immutable revision, a reviewed manifest with
one component's repository-relative paths and Git blob IDs, explicitly named
unittest modules, a minimum executed count, a clean export root containing
exactly those files, and a new output directory outside the inputs. The manifest
is local to this draft capability; it is not an approved shared project schema.

Output: `evidence.json` and `suite.log`. Evidence carries source revision,
manifest SHA256, every file SHA256, tool/helper hashes, named modules, counts,
errors, failures, skips, input preservation and pass/fail. The Git blob check is
SHA1(`blob ` + byte length + NUL + file bytes), matching Git's object identity.
The `source_revision` claim depends on trusted retrieval: a caller-created
manifest alone cannot prove that a blob belongs to a GitHub commit.

Method: validate paths/pins/modules -> verify every blob and exact inventory ->
freeze manifest -> execute named tests in a bounded subprocess -> apply the
existing strict result rule -> recheck inputs -> retain evidence. Fail on
missing/extra/mutated files, symlinks, changed reviewer inputs, insufficient
discovery, assertion/import errors, skips, expected failures or timeout. Output
creation is exclusive so a repeat cannot overwrite an earlier result.

This is intended for trusted reviewed Python source, not adversarial code.
Installed dependencies, the operating system and Python runtime remain trusted;
hashes and subprocesses do not provide execution isolation. No credentials,
retrieval, scheduler, dispatch, merge or automatic repair are implemented.
`semantic_acceptance`, `integrated` and `operational` always remain false in this
tool's result. An independent reviewer decides meaning separately.

First concrete instance: [PR264 manifest](source-manifest.json), source
`48356290d402f0c47b89f84ddaa728c7e72d951e`, 24 files and six modules / 81 tests.
The separate [consumer probe](probe_handoff.py) preserves one observed failure;
it is a diagnostic against an unmerged external source, not part of this tool's
own green regression suite. Its expected behavior is never rewritten to hide
that source defect. [review.md](review.md) controls the source verdict.

From a reviewed acceptance checkout, prepare the export by fetching exactly the
manifest paths at its immutable revision. Then:

```sh
PYTHONDONTWRITEBYTECODE=1 python tests/integration/handoff_loop_review_20261119/qualify.py --source /absolute/path/component-export --manifest tests/integration/handoff_loop_review_20261119/source-manifest.json --output /absolute/path/new-evidence
```

Exit 0: integrity + named suite passed. Exit 1: execution/preflight evidence
records a failure. Exit 2: CLI/output admission failed. For independent probes:

```sh
PYTHONDONTWRITEBYTECODE=1 python tests/integration/handoff_loop_review_20261119/probe_handoff.py /absolute/path/component-export
```

At the recorded source revision this exits 1, with five passes and the boolean
timestamp failure. A newer source needs a fresh explicit manifest and review;
historical success cannot certify it. Tool regression command:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/integration/handoff_loop_review_20261119 -p 'test_*.py' -v
```

## Microsoft methods and project-specific application

These public methods inform the design; Microsoft does not endorse this tool.
Sources were checked November 19, 2026. The project retains its own authority,
ownership, source-truth and no-merge contracts.

| Microsoft source | Mechanism used here | Boundary |
| --- | --- | --- |
| [Engineering Fundamentals: testing](https://microsoft.github.io/code-with-engineering-playbook/automated-testing/) | Parameterized test inputs; explicit configuration; unit and integration results answer different questions. | No coverage percentage or end-to-end service claim from test counts. |
| [Consumer-driven contract testing](https://microsoft.github.io/code-with-engineering-playbook/automated-testing/cdc-testing/) | Consumer probes state expectations independently of the producer suite; one exposes the timestamp gap. | A local direct-call probe is a contract-testing application, not a deployed distributed CDC system. |
| [Design for evolution](https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/design-for-evolution) | Reuse parent integrity helpers; keep transport and source-domain logic separate; evaluate invariants as fitness checks. | Component file hashes do not evaluate economic correctness or live ownership. |
| [Testing and quality gates](https://learn.microsoft.com/en-us/azure/well-architected/design-guides/testing) | Stage evidence: source identity, named tests, independent meaning, integration, then operations. | Only the first two run in the tool. Later stages require existing owners and real evidence. |

Alternatives: a second GitHub client, scheduler or generic orchestration service
would add unrelated authority and dependencies. Merely recording a test count
would lose byte provenance and negative evidence. Extending the shared runner
directly would cross its current owner's file scope. The bounded sibling
variant keeps those contracts addressable and can later be consolidated by B01
if a second real use justifies it. No such consolidation is claimed now.

Falsifiers: changing one source byte, adding an input module, skipping a test or
mutating source during a green test must prevent pass. A pinned suite may still
miss a semantic defect, as the independent boolean probe demonstrates. No
measured speed/cost benefit or generalized source acceptance is claimed.
