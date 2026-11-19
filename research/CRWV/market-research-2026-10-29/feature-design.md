# Earnings-to-price review

Parent guidance is referenced in AGENTS.md and state.json. This specializes the existing CRWV research pack for one dated earnings update.

The consumer is the ticker reviewer deciding whether a price decline is explained by changed operating or financing assumptions. Inputs are the preceding report, issuer release and 10-Q, guidance and transcript, analyst estimates and timestamped Massive observations. Output is a JSON report with observations, calculations, chosen scenarios, invalidation gates, source status and next actions.

Follow the existing sequence. Freeze a price and prior expectation, compare reported results on matching definitions, map contracted/energized/accepted/billable capacity, reconcile cash and debt obligations, calculate equity earnings sensitivity, compare price with market references, and review the result. Read only the source sections required by the current question. Preserve the earlier report for the revision comparison.

Revenue guidance implied for Q4 equals full-year guidance minus nine-month reported revenue. Adjusted operating income follows the same subtraction. Interest coverage uses consistent periods and retains the GAAP/non-GAAP distinction.

Enterprise-value proxy equals reference price times observed common shares plus carrying debt minus unrestricted cash and securities. Report operating and finance leases separately and state their treatment. A current trade combined with quarter-end balances is a dated proxy. Forecast equity earnings require a separately declared diluted-share scenario.

Scenario pretax earnings equal revenue times GAAP operating margin minus interest. Apply the assumed tax rate only to positive earnings, divide net income by explicit shares, and return null P/E for nonpositive EPS. For a chosen P/E, required margin equals [(price/P-E times shares)/(1-tax) + interest]/revenue. Include depreciation, rent and share compensation in the assumed operating margin. Funding still requires a monthly principal and capex waterfall.

The examples in post-earnings-price-review-2026-11-19.json use current 2027 analyst revenue and independently chosen margins and interest. The 2028 examples are wholly assumed sensitivities. A management adjusted-profit target supplies no GAAP EPS forecast. Keep expected deposits, undrawn facilities, actual cash and recognized revenue addressable separately. Reconcile renewal cohorts before adding their revenue to consensus or ARR.

Reuse research/CRWV/tool from PR87 for any future monthly funding model and the existing market-context comparison from PR218 for wider peer reporting. The next planned funding-cohort child needs project-level inputs before development. This pack adds research interpretation and a dated calculation record. It inherits canonical data handling and independent validation from B02/B01.

Prior art includes expectation-versus-actual earnings bridges, project-finance draw and debt-service waterfalls, reverse earnings valuation and event-study price paths. Each contributes a different check. They do not provide calibrated rebound odds.
