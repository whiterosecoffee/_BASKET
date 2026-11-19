# _BASKET — GitHub Project board runbook

**Owned by:** B00. Projects, labels and branch rules are GitHub settings; they cannot be changed from a worker branch, so the repo owner runs these steps. Board state is a view; GitHub issues, PRs and CI remain the evidence (see `AGENTS.md`).

## 1. Create the project
Profile → Projects → New project → Board, name `_BASKET Orchestration`, then link repository `whiterosecoffee/_BASKET`.

## 2. Fields
- Status: Queued, Claimed, In PR, CI Gate, Needs Authorization, Done.
- Spark (single select): B00, B01, B02, B03, B04, B05, B06, B07, B08, B09, B10, B11, B12, B13, B14, B15, B16, B17, B18, B19, B20, B21.
- Tool (single select): ChatGPT, Claude Code, Visual Studio/Copilot, Human (defaults in `orchestration/planner/agent-routing.json`).

## 3. Load work
Add open issues and PRs; set Spark from the `[Bxx]` title tag. Move a PR to CI Gate or Needs Authorization only when CI passed on its exact head SHA. Put PRs idle for about a week with no CI evidence in a Triage view and close or hand them off.

## 4. Project workflows
Enable: auto-add new issues/PRs from the repo, item closed → Done, PR merged → Done.

## 5. Spark labels
`orchestration/spark_claims.py` reads `spark:Bxx` labels. Create them:

```bash
gh label create "spark:B00" --repo whiterosecoffee/_BASKET --color 1d76db --description "Orchestrator & Contracts" --force
gh label create "spark:B01" --repo whiterosecoffee/_BASKET --color 1d76db --description "Integrity & CI Rescue" --force
gh label create "spark:B02" --repo whiterosecoffee/_BASKET --color 1d76db --description "Market Feeds, FX & TTD" --force
gh label create "spark:B03" --repo whiterosecoffee/_BASKET --color 1d76db --description "Earnings & Event Ledger" --force
gh label create "spark:B04" --repo whiterosecoffee/_BASKET --color 1d76db --description "Company Economics & Valuation" --force
gh label create "spark:B05" --repo whiterosecoffee/_BASKET --color 1d76db --description "Ownership & Economic Graph" --force
gh label create "spark:B06" --repo whiterosecoffee/_BASKET --color 1d76db --description "Traversal & Cycle Engine" --force
gh label create "spark:B07" --repo whiterosecoffee/_BASKET --color 1d76db --description "Calibration, Falsification & Risk" --force
gh label create "spark:B08" --repo whiterosecoffee/_BASKET --color 1d76db --description "Service & Tool Deployment" --force
gh label create "spark:B09" --repo whiterosecoffee/_BASKET --color 1d76db --description "SFTBY Parent NAV & Holdings" --force
gh label create "spark:B10" --repo whiterosecoffee/_BASKET --color 1d76db --description "CRWV GPU Lifecycle" --force
gh label create "spark:B11" --repo whiterosecoffee/_BASKET --color 1d76db --description "AAOI Optical Manufacturing" --force
gh label create "spark:B12" --repo whiterosecoffee/_BASKET --color 1d76db --description "ARM Royalties & Compute Mix" --force
gh label create "spark:B13" --repo whiterosecoffee/_BASKET --color 1d76db --description "OpenAI & Anthropic Private Value" --force
gh label create "spark:B14" --repo whiterosecoffee/_BASKET --color 1d76db --description "NVIDIA Compute Moat & Capital Loop" --force
gh label create "spark:B15" --repo whiterosecoffee/_BASKET --color 1d76db --description "Optical Bottlenecks: LITE/COHR" --force
gh label create "spark:B16" --repo whiterosecoffee/_BASKET --color 1d76db --description "Telco Edge: CHTR/TMUS/NOK" --force
gh label create "spark:B17" --repo whiterosecoffee/_BASKET --color 1d76db --description "Cross-Market Signal Composite" --force
gh label create "spark:B18" --repo whiterosecoffee/_BASKET --color 1d76db --description "MU Memory Contract Economics" --force
gh label create "spark:B19" --repo whiterosecoffee/_BASKET --color 1d76db --description "AI Supply Chain & Profit Pools" --force
gh label create "spark:B20" --repo whiterosecoffee/_BASKET --color 1d76db --description "CHTR Cable Edge Economics" --force
gh label create "spark:B21" --repo whiterosecoffee/_BASKET --color 1d76db --description "Narrative, Claims & Falsification Engine" --force
```

## 6. Enforce lanes
Repo Settings → Rules → new branch ruleset for `main`: require a PR, require 1 review, require the `validate` check, block direct pushes. A CI check mapping PR changed files to `sparks.json` write_paths is a B01 handoff (`.github/workflows/**` is B01-owned).

## 7. Routine
Export fresh open issues/PRs, then:

```bash
gh issue list --repo whiterosecoffee/_BASKET --state open --limit 200 --json number,title,labels,state > /tmp/issues.json
python orchestration/spark_claims.py /tmp/issues.json
python orchestration/planner.py --help
```

Keep 3–5 active workers, judged from issue/PR/CI evidence rather than open PR counts.
