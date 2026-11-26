# Basket preservation and Patterns migration baseline

## Start here

- Basket integrated baseline [7eb29bbae71614559f41ec283908753e9a677a55](https://github.com/whiterosecoffee/_BASKET/commit/7eb29bbae71614559f41ec283908753e9a677a55). GitHub Actions reported success for [shared validation](https://github.com/whiterosecoffee/_BASKET/actions/runs/44958864188) and the [OpenAI strict gate](https://github.com/whiterosecoffee/_BASKET/actions/runs/44958864226). Main includes the approved worker contract #164 and the versioned closeout increment #179.
- Patterns comparison baseline [5b9a0810f5d3a0428a8c1b1a4bababe4c6e88761](https://github.com/whiterosecoffee/_PATTERNS/commit/5b9a0810f5d3a0428a8c1b1a4bababe4c6e88761). Use [live Snapshot.json](https://github.com/whiterosecoffee/_PATTERNS/blob/main/Snapshot.json) for component discovery, then follow each receipt to its exact revision and state.
- The historical master archive is [OneDrive state-index.json](https://github.com/whiterosecoffee/_PATTERNS/blob/57e058c9070974642f7a554f9d145a37135448b3/state-index.json) on `archive/onedrive/index-20261116`. The [_REPO_CONSOLIDATION guide](https://github.com/whiterosecoffee/_PATTERNS/blob/ba6e719581fb401dff8586b81d8f6bd8918a7efe/CONSOLIDATION.md) explains the dated inventory. The [Advance Basket source closeout](https://github.com/whiterosecoffee/_PATTERNS/blob/7e4ede73805f2ca0f655bcc5e46da811fbe3b2a3/_TOOLS/_EXPLODE_SESSION/closeout/FINAL.md) records unresolved exact-package acknowledgment and dispositions for 15 proposals. Keep these historical gates visible.
- Basket's work and decision authority remains [B00 queue #136](https://github.com/whiterosecoffee/_BASKET/issues/136), with ownership scopes in [sparks.json](../../../orchestration/sparks.json) and claims/results in the existing issues. This audit is tracked in [#324](https://github.com/whiterosecoffee/_BASKET/issues/324).

## Publication and review

The workstation's clean full clone tracks `origin/main`. Git object verification passed. The captured GitHub inventory contains 156 branch refs and no tags before the new audit branch. All 106 existing open PR heads matched their named GitHub branches. Keep the 105 drafts with their current owners. Eleven drafts were UNSTABLE in the captured inventory and need head-specific check inspection before promotion. PR #271 is the sole ready-for-review PR. Its shared checks passed at `6f3715f62980bf98009722e967e5f2b289345312`, and B09/B00 evidence review is still pending. [PR #271](https://github.com/whiterosecoffee/_BASKET/pull/271)

| Workstation source | Preservation and remaining work |
| --- | --- |
| B00 #243 clean-template work | Exact source tip `17c44fcc36501aa30d80ef64e40240103b2ebf49` on `archive/basket-243-workstation-20261126`. Existing owner branch remains available separately. |
| B00 #243 detached receiver preview | Three changed files archived at `e563863df6825c48623dbd39ba89192ce7fc1f66` on `archive/basket-243-receiver-preview-20261126`. All 43 focused receiver tests passed. Compare with current #243 before adopting. |
| B06 #108 maturity packet | Functional files plus redacted local metadata at `387e7916ce8d3cd79d612426914914e1d47db0ab` on `archive/basket-108-workstation-20261126`. All 19 focused tests passed with pinned source objects in the audit clone. The original history remains local. |
| NVDA portable FETCH routing | Two structural files with the private session identifier omitted at `35002869c712e944198cba972305b35e03b5519f` on `archive/basket-nvda-routing-20261126`. Parsed and checked the read-only consumer boundary. |
| #169 controller and #207 receiving | Local tips already reachable from the corresponding GitHub branches. No duplicate publication. |
| Historical main and pre-sync pin | Both commits reachable from current GitHub main. |
| Local NVDA analyst branch | Contains workstation-specific delivery metadata. Keep the original local pending the existing NVDA/FETCH owners' decision on a portable projection. |
| Melissa trajectory prototype | Source remains local under its recorded publication boundary. Patterns already has the registered repair handoff referencing exact original `6be558d6` and a separately published synthetic successor. [Repair receipt](https://github.com/whiterosecoffee/_PATTERNS/blob/main/_HANDOFF_RECEIPTS/6af642ae-e840-8191-9a89-f25a7214400c.json) |
| EWZ temporary JSONL, generated caches and private transfer folders | Left at source. Licensing, source classification or owner confirmation is required before transferring market data. Caches are regenerable. Separate hosts and unregistered workspaces remain outside this inventory. |

## Capability delta

The reproducible tree scan compared 256 tracked Basket entries with 193,681 Patterns default-branch entries. It found 252 with no exact match, two with the same path and a different object, and two exact blobs at other paths. Those counts identify review candidates. Capability coverage also requires opening registered component branches and checking the interface, fixtures, dependency pins and acceptance evidence.

| Basket capability and accountable lane | Patterns evidence and next acceptance |
| --- | --- |
| B00 orchestration, worker contracts and closeout; B01 guards and CI | _BASKET_B00_RECONCILIATION, _HANDOFF_LOOP, _EXECUTION_ADMISSION_SOURCE, _CI_DISCOVERY, _BRANCH_OWNERSHIP and _SCHEMA_QUALIFICATION are candidate counterparts. Compare schemas and rejection behavior, including ownership collision, resumability and stale/test evidence. Confirm workflow discovery on the receiving commit. |
| B02/_FETCH acquisition, provenance, qualified partitions and replay | _MASSIVE, _MASSIVE_FETCH_UBUNTU, _BASKET_CLOSE_AUDIT and _NVDA_STORE_QUALIFICATION provide preserved evidence. Verify that resolver, writer, day boundaries, corrections and coverage are compatible with #148/#183/#207. Keep licensed inputs under the data owner. |
| B06 traversal, geometry, historical-state and market-event gate | _TRAVERSAL_B06 and published captures for #149, #154 and #155 preserve references or research. Establish executable parity with Basket's traversal entry points and candidate branches. Run #155's 15 synthetic tests and then qualify replay separately. |
| B03 issuer events, B05 relationships, B04 valuation and domain research | Retain Basket's contracts, provenance rules, fixtures and open work at exact pins. Search receiving components item by item and record whether their outputs are adopted, retained as references or missing. No parity established in this pass. |
| B17/B19 monitoring, group coverage and market consumers | _GROUP_MONITORING, _BASKET_B19_COVERAGE and _TRAJECTORY are registered evidence. Check operating prerequisites and repeatable acceptance before claiming runtime continuity. |

B00 coordinates policy and migration dispositions. B01 owns independent build validation. Existing domain owners retain implementation scope. A PR author's account, a spark hint, a branch, and an active writer are different records. The inventory makes no active-session claims.

## Instruction to carry forward

> Use GitHub as the shared source for code, ownership, decisions and evidence. Pin Basket's integrated baseline, all candidate PR heads and the Patterns comparison revision. Keep existing work with its owner. Preserve pending or divergent work on verified archive branches and retain restricted originals at their approved source. Leave open PRs with their existing owners and do not start session handlers.
>
> For each capability, record the source revision and entry point, its existing issue and owner, the receiving component and revision, the expected behavior, the evidence and one disposition. Use adopted, reference-only, intentionally retained, deferred or uncovered. Require the corresponding acceptance evidence before marking adopted. Record the specific missing dependency or test when coverage is incomplete.
>
> Apply Microsoft's Azure Repos review practices: link the work item, resolve review comments, verify the build and scoped tests at the exact head, and recheck the target before integration. Require the existing owner's acceptance and explicit merge approval. Record post-merge checks and a rollback reference when integration is authorized. Retain Basket until the receiving owner has signed off on the capability map, restricted items and remaining gaps.

[Microsoft Learn · Git repository settings and branch policies](https://learn.microsoft.com/en-us/azure/devops/repos/git/repository-settings?view=azure-devops#branch-policies)

## Reproduce the tree scan

Run from this folder with both repositories locally available and the two exact commits fetched. A tree-only fetch is sufficient for the comparison. The report intentionally emits no private Patterns path listing.

```text
python compare_trees.py <basket-clone> 7eb29bbae71614559f41ec283908753e9a677a55 <patterns-clone> 5b9a0810f5d3a0428a8c1b1a4bababe4c6e88761
```

See [tree-delta.json](tree-delta.json) and [github-inventory.json](github-inventory.json). The next audit pass is to resolve the highest-risk B00/B01 and B02 source-to-target interfaces, attach paired acceptance evidence, and classify the remaining capabilities. Patterns and any Beyond cutover stay pending until those dispositions are reviewed.
