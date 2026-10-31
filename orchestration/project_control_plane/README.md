# GitHub Project control plane (B00, issue #132)

This module is **not** a deployed controller or a second state database. It accepts a dated GitHub export, emits an advisory report, and returns exit code 2 for path collisions. Actual GitHub issues, PRs, head SHAs, Actions and Projects remain authoritative. Never infer a live claim or a successful deployed service from this script.

## First-time Project setup — blocked on Projects v2 API access

The current connected GitHub integration lacks Projects v2 list/create/update/view GraphQL methods, so project creation, ID, URLs, field configuration and auto-add **have not been verified**. Avoid claiming existence. With an authorized GitHub CLI login that has `project` scope, check existing projects first:

```bash
gh auth status
gh project list --owner whiterosecoffee --format json
# Only if no suitable _BASKET project exists:
gh project create --owner whiterosecoffee --title "_BASKET — Intelligence & Execution" --format json
# Copy returned numeric project number and URL; verify:
gh project view NUMBER --owner whiterosecoffee --format json
gh project link NUMBER --owner whiterosecoffee --repo whiterosecoffee/_BASKET
```

Document verified project ID/URL in issue #132 before adding items. Add existing repository issues/PRs as project items, not duplicates; use `gh project item-list NUMBER --owner whiterosecoffee --format json` and compare issue/PR URL before `gh project item-add`. Project status automation and views require separate authenticated setup and observed verification. Suggested logical views: Executive, Active Execution, Dependencies, CI, Market Data, Valuation, Traversal, Company Research, Release, Roadmap. Suggested fields: Status, Priority, Domain, Spark ID, Worker, Branch, Validation, Acceptance, Last Verified, Execution Mode. Use native title/assignee/milestone and issue links where possible.

## Offline reducer

Prepare a dated normalized JSON export with `as_of`, `issues[]` containing GitHub `number,state,task`, and `pull_requests[]` containing `number,headRefName,headRefOid,isDraft,changedFiles,checks`. `task` is parsed from the existing `basket.worker_task@1` issue claim; do not mistake an unparsed issue for an active worker. Each `checks[]` member must include exact `head_sha` and conclusion. Data must come from GitHub live API at export time. This first version does not perform network retrieval, schema validation, writes, or dispatch. Run:

```bash
cd orchestration/project_control_plane
python -m unittest -v test_reconcile.py
python reconcile.py snapshot.json report.json
```

A complete Project adapter needs a GitHub GraphQL credential and minimum permissions to list and mutate user Projects v2. Project creation and automated item onboarding remain BLOCKED until this is available and tested. B01 owns any Actions workflows or independent CI integration. Existing B00 PR #123 owns the board runbook and spark claim validator; do not overwrite or duplicate them.

## Recovery and implementation boundaries

A branch claim requires `task_id + spark_id + issue + branch + worker + allowed paths`. Collision flags require manual B00 arbitration; they do not transfer ownership. A green PR head is `head_passed_not_integrated`; only independently verified main CI after authorized merge supports integration verification. Preserve issue/PR identity and attempt evidence. The October 30 intraday reversal detector is a **dependency**: B02 source-minute tape (PR #125 is historical HIRO intake, not a validated detector) → B06 replay signal → B01 independent validation; B00 only coordinates. No scheduled agent, real-time tape poller, or automatically created ChatGPT chat is provided here.
