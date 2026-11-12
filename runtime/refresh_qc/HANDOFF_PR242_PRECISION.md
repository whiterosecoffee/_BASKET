# Prepared owner handoff: PR242 decimal precision

Disposition: prepared locally and delivered to the parent B00 controller; not posted to GitHub and no receiver implementation claimed. This preserves prior publication boundaries. Do not create a second issue/workstream or duplicate this report if it is later posted.

## Verified destination and scope

Existing owner: B00-241, issue https://github.com/whiterosecoffee/_BASKET/issues/241, draft PR https://github.com/whiterosecoffee/_BASKET/pull/242, branch work/241-json-data-flow-objects. Fresh metadata read confirmed current head d103a99486589aa4aee24d4fa978532f1b288ac1, open/unmerged. The claim at issue comment 6809980295 owns orchestration/data_flow_objects/**; comment 6810133059 additionally allocates orchestration/tests/test_data_flow_objects.py. No new ownership or schema-wide scope is inferred.

Established route: continue that issue/PR and existing B00 controller. A distinct reachable owner chat was not verified from available listings. The reachable Advance Basket session identifies itself as B00-236 review-only, not B00-241, so no implementation request was sent there.

## Narrow request to B00-241

The receiving #207 qualification reproduced silent loss of exact decimal volume at your current reference head. Please fix this in the existing owner branch, or explicitly fail closed on unsupported source precision, and return a new exact revision for qualification. Preserve existing ordinary fractional-volume behavior and immutable original probe evidence. Do not modify B02 files, legacy FETCH or original data.

Source: orchestration/data_flow_objects/flow.py at d103a99486589aa4aee24d4fa978532f1b288ac1. strict_load uses standard JSON floating-point parsing; sanitize accepts int/float; encoded serializes the rounded float. A synthetic source volume token 1.250000000000000000000000000001 reaches bars.jsonl as 1.25. The source is schema-shaped and all other fields satisfy the reference's existing checks.

Reproduction: receiving qualify_reference.py test_guard_exposes_reference_precision_loss constructs a synthetic TEST capture with one 2026-10-08 minute bar (timestamp 1791468000000, o=2, h=3, l=1, c=2, vw=2, n=2), explicit adjusted=true/minute/USD reference semantics and captured_at 2026-10-09T00:00:00Z. flow.build returns v=1.25. Receiving verify_volume_preservation rejects that source/candidate pair with volume_changed. No provider data is involved.

Evidence: local #207 commit f94ecf689e3ca29f0be00a30fc9726c724cdfdc5; runtime/refresh_qc/qualify_reference.py and reference-qualification-2026-11-12.json. Seven exact-pinned reference tests passed, including this expected loss detection; independently rerun. This is NOT a statement that decimal preservation passed. The local commit is unpublished, so do not advertise a GitHub artifact link for it.

Acceptance for the owner correction:
1. High-precision source volume must survive parse/transform/serialization exactly, or the entire unsupported capture must reject before any artifact publication.
2. Existing representable fractional volumes remain supported; no integer rounding, silent string coercion, or reinterpretation of count units.
3. New regression includes at least the failing decimal token plus decimal/exponent boundary cases, unchanged-input replay and source/partition pin checks.
4. If numeric serialization or schema meaning changes, version and explain compatibility. Do not relabel old evidence or select old reader code implicitly.
5. Return exact commit and named test results, preserving B02 ownership and source privacy. No merge or activation is requested.

## Existing generation/reader handoff remains with #207

These are previously recorded design gaps, not a second defect report or demand that B00 implement a store: changed capture for an occupied partition rejects, and changed reader/schema/transform identities make prior receipts unreadable. #207 retains immutable generation, durable root and FETCH/read binding; use existing TickerStore expected_head/supersedes and replay principles. B00 decisions are only needed for shared schema/routing and the distinct _MAP external-availability versus local-capture policy. Do not open competing generation work in PR242.

The parent can route this once to the verified existing B00 owner when available, or explicitly continue that owner branch under its own authority. No public comment has been attempted by this worker, so there is no uncertain send to retry.
