# Compensation and ownership interpretation review

Parent: feature-design-gaap-bridge.md; role/state from AGENTS.md and state.json. This variant composes the same gaap-bridge.py model rather than duplicating it. Input: annual/interim compensation, basic and diluted EPS denominators, historical tax effects and dated GAAP net-income aggregates in gaap-inputs.json. Output: assumptions_review in gaap-results.json and ASSUMPTIONS_REVIEW.md.

Method: compare March/September unrecognized awards without inventing a recognition schedule; calculate historical SBC-specific tax-effect ratios and apply only as a sensitivity; distinguish GAAP expense from cash outlay and current denominator dilution; derive EPS from already-GAAP forecast net income without deducting SBC again. FY29 assumes 1.13B diluted shares, not a known future share count. Preserve original scenario outputs and their classifications.

Review: reconcile $400M / 1068M basic shares and / 1079M diluted shares; check noncash grant values are not described as cash returned to Arm; label 23M outstanding awards as an overhang rather than annual dilution; retain ordinary development costs. Differentiate a second-method owning-worker review from independent acceptance. No fair-value precision or probabilities. Compare all source and model vintages before using the output as current evidence.
