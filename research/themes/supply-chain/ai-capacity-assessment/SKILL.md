---
name: ai-capacity-assessment
description: Assess whether domestic AI accelerator supply can support local demand, sustained exports, and displacement of an incumbent. Replay inference economics at full utilization.
---

## Scope and entry point

Inherit the repository AGENTS.md and B19 supply-chain ownership. Use for domestic capacity, sovereign AI procurement, inference economics or supplier displacement. Read the [historical case](../china-ai-inference-2026-11-20.md) only for provenance or replay. Latest dated corrections take precedence over earlier forecasts.

1. Identify buyer, geography, workload, incumbent, decision horizon and evidence cutoff. Refresh dated evidence before making current claims.
2. Compare annual production with annual production and installed stock with installed stock. Keep chip designer, physical location and remote access separate. Record domestic deliveries, backlog and usable replacement inventory. If demand is unmeasured, return coverage unknown.
3. For economics run `python3 assess.py < china-example.json` from this directory, substituting a sourced JSON input matching the example. The calculator assumes 8,760 hours at the supplied rate. USD includes equipment amortization, recurring operations and electricity. Financing and construction require separate inputs outside this version. Preserve input alongside output.
4. Compare model, quality, input/output lengths, latency, precision and power boundary. When unmatched, report scenario only. Never infer tokens per watt from peak FLOPS.
5. Classify export evidence as model adoption, sales outreach, contracted hardware, installed system or reorder. For lost revenue identify displaced allocation, incumbent guidance and ability to sell elsewhere. Report unknown where evidence ends.
6. Return dated conclusion, observations with sources, assumptions, scenario output, gaps and the specific observation that would change the conclusion. No automatic trading or publishing.

## Evaluation and improvement

Replay expected costs $0.16732 and $0.15466 per million within $0.00001. Zero throughput must fail. Unlike latency targets must remain a scenario. A model download alone yields no demonstrated hardware displacement. Improve next with a second independent buyer case and a fresh-agent discovery test before promoting the skill to a shared catalog.
