# Independent review and next owner action

Source: B00 #169 / draft PR264, exact head
`48356290d402f0c47b89f84ddaa728c7e72d951e`. Reviewer: B01 #272, separate main-based
branch `work/272-handoff-loop-independent-review`; base
`433d3574033a35f24910dc1ffee21ecbf27702dc`. Only this directory changes.

Verdict: existing focused suites pass; source acceptance requires rework of a
raw-kernel observation validation gap. Runtime remains unverified. The source
owner's claim is broader than its old 24-test PR description: current source
contains 81 tests across six modules. Do not replace its PR description or claim
the source writer received this review merely because a review file exists.

| Evidence | Result | Limit |
| --- | --- | --- |
| 24 Git blob identities at pinned source | Verified before final qualification | Component export, not complete Git checkout |
| Named producer suites | 81 run; 0 failures/errors/skips/expected failures | Local; [source-results.json](source-results.json), [source-suite.log](source-suite.log) |
| Independent consumer probes | 6 run; 5 pass, 1 failure | [probe-results.txt](probe-results.txt); local review-checkout prefix removed only |
| Tool regressions | 7 pass; no skips | Real subprocess success, failure, skip, timeout and mutation cases |
| Source shared CI run 43351579659 | Success | Retrieved worker-qc log lacks handoff-loop test names; no focused coverage inferred |
| New review/tool hosted CI | Pending at this artifact checkpoint | Check current review PR at exact head |

## F1: boolean epoch treated as fresh

`core.evaluate` validates six boolean flags strictly but uses `verified_at` in
arithmetic without validating its type. Python interprets `True` as 1. With the
published example state/claim, `verified_at=True` and `now=100`, all other
observations valid, the result is `continue` rather than `blocked`.

Reproduction: the sixth test in [probe_handoff.py](probe_handoff.py), using the
documented command in feature-design.md. This is a raw kernel contract gap; the
trusted production adapter does not exist, and the newer adapter's strict finite
number validation is not evidence that callers of the kernel are protected.
No real work, dispatch or exploit is claimed. This does not invalidate the five
independent confirmations of wake consumption, criterion preservation,
self-asserted dimension rejection, decision-only output and disabled live entry.

Minimal correction belongs to B00 #169 / PR264: validate `verified_at`, `now` and
`max_age` as finite int/float values excluding booleans; require an appropriate
positive age bound; return a blocked decision for malformed observations before
arithmetic, and make persistence reject it before invoking the callback. Preserve
existing state bytes, wake history and lock cleanup on rejection. Review type,
NaN/infinity, stale/future and boundary cases using the existing source suite;
do not add a runtime or migrate the private checkpoint to fix this gap.

## Sequence and ownership

1. B00 source owner reproduces F1 at the pin and implements the minimal owned fix.
2. Source owner runs all current focused tests, publishes its new exact head and
   retains the old failure evidence. No source branch is changed by this review.
3. B01 refreshes the explicit manifest, reruns qualification and all independent
   probes at that head. Original three repaired behaviors remain regression gates.
4. B00/B01 decide bounded component acceptance. Trusted observation/lease ports,
   scheduler-run binding, live execution, checkpoint migration and merge remain
   separate existing-owner gates; no acceptance inferred from synthetic fixtures.

Reusable knowledge: source identity and test meaning are separate contracts;
negative evidence must survive a passing suite; child capabilities record only
their variation and reuse parent checks. Microsoft's contract tests and fitness
functions supply mechanisms; project ownership and evidence gates determine
where those mechanisms can be used. Destination: existing B01 source-gate family,
source #169, and this bounded variant. No new queue or duplicated controller.

## Execution review

Strengths: current-main refresh, all 82 open PR file inventories checked before
claiming a disjoint path, separate B01 branch, actual focused execution,
independent defect reproduction and small reuse-based tool. Limits: this is one
real component and synthetic tool fixtures, no second real consumer or hosted
focused gate yet. That evidence does not justify a global standard or a maturity
percentage. Broad project and all-conversation coverage were not attempted.

Recovery retained: initial connector calls required corrected argument names;
oversized output was replaced with compact stored projections. Shell bulk-file
write exceeded argument length and clone returned HTTP400, so connector exports
were used. Patch creation added a terminal newline to each export; the mismatch
was detected and corrected by Git blob comparison. Preliminary tests on those
copies were not used as exact-byte evidence. Final qualification checks source
identity first and verifies all 24 exact blobs before executing tests.

Next action: B00 #169 reproduces and fixes F1 on its own PR264 branch.
