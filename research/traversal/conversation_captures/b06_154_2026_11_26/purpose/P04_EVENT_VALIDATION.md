# P04 — Frozen Episodes, Analogues and Incremental Information

**Status:** statistical research plan, not a validated trading model. **Owners:** B06 #144/#108 for observed event morphology; B07 #93 for outcome validation; B01 for independently accepted integrated checks.

## Problem
Several consecutive qualifying days can be one market episode. Reordered price paths may have identical aggregate endpoints and different slopes, but mathematical distinctness alone does not prove predictive value.

## Experimental method
1. B02 provides qualified as-of data and completed-session timeline; B06 freezes event IDs, first knowable timestamps, independent range boundaries, onset, confirmation, resolution, ambiguity and censoring before observing later returns.
2. Pre-register control = existing B06 #109/#145 traversal/turnover/path measurements; treatment = precisely control plus prior-completed-session SMA30 five-session slope.
3. Hold identical eligible episodes, cutoffs, labels, alert budgets, training procedure and horizon. Chronological purged/embargoed holdouts; cluster by event, not daily row; avoid tailoring thresholds after observing Nov4 NVDA.
4. Report independent n, class precision/recall, false-reversal confirmations, time-to-detection, censored outcomes, adverse excursion and date-block uncertainty; preserve negative results.
5. Consider ATR normalization, persistence, rank and B17 factor context only after the first experiment supplies interpretable evidence, one feature at a time.

## Falsifiers
No robust held-out lift, performance dependent on overlap, sparse episodes, unstable regimes, source-vintage uncertainty or increased false reversal cost => do not promote as predictive tool. Trade utility after costs and missed rebounds is a separate study.

## Smallest next action
B06 #144 freezes minimal source-qualified historical cohort; B07 #93 runs the paired comparison; B01 tests exact-head integration only when model promotion is requested. No invented probabilities.