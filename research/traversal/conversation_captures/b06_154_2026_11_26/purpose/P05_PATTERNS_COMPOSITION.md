# P05 — Hierarchy, Prior Art and Microsoft Implementation

**Status:** design reconciliation packet already recorded in B06 #154 and routed to _PATTERNS #5; independent System Design acceptance pending. **Owners:** _PATTERNS _SYSTEM_DESIGN and _BASKET B00 for cross-domain policy.

## Problem
Repeated conversation-derived prompts, scripts and dashboards can silently copy inherited instructions, claim incomplete implementation, conflict across branches or lose unique decisions. Reusable intelligence needs explicit source/owner/version pointers, not additional giant prompt copies.

## Existing parent and sibling capabilities
Live _PATTERNS Snapshot.json registers _BASKET_B06_154_HISTORICAL_STATE, _SYSTEM_DESIGN, _AGENT_FRAMEWORK, _BASKET_TRAVERSAL_TOOL_20261119, _BASKET_B06_149_MARKET_GEOMETRY, _BASKET_B06_155_MARKET_FLOW_WATCH and _MARKET_TRAJECTORY_OPERATOR. _PATTERNS receipt _HANDOFF_RECEIPTS/6ae9e667-464c-83ea-a7a5-ee62ad095614.json pins the saved historical-state capture, independent receiver was pending at audit. Existing B06 reconciliation is at PR160 file PATTERNS_SYSTEM_DESIGN_RECONCILIATION_2026-11-21.md.

## Generalizable method
Parent System Design separates evidence trust (VALID/PARTIAL/STALE/CONFLICTING/MISSING/REJECTED), state/hypothesis impact (for/against/unknown, novel vs continuing), and decision value (NONE/WATCH/MATERIAL, SUPPRESS/REVIEW/NOTIFY). B06 owns exact math and market transitions. A low historical percentile is neither evidence of buyers nor an automatic trade decision.

Apply Microsoft principles: deterministic functions for math, source validators for provenance, versioned state machines for event transitions; use agents for ambiguous semantic extraction and competing explanations; use workflows/checkpoints only for real coordination or approval requirements. Checkpoints are not licensed data custody; human approval is needed for source ownership/schema promotion, new cross-domain writes, merges/releases.

## Prior-art mechanisms
Statistical process control/change point; momentum and empirical ranks; event studies/survival; causal falsification; signal detection/error costs; multiple testing and backtest overfitting; bitemporal event sourcing, CQRS/ports/adapters; design by contract; traceable review/postmortem. Families are mechanisms and test suggestions, not evidence of alpha.

## Smallest next action
Existing _PATTERNS System Design owner reviews a bounded market example (valid extreme displacement with insufficient analogues) and project example (green synthetic CI but no source replay/contract approval) against simple thresholds, stateful thresholds and EDCI. Accept/revise/defer links only; do not start another general agent framework or second engine. Source branch and saved receipt remain independently addressable.