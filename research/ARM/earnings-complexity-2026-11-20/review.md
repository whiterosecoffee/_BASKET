# Review

Check source vintage, fiscal versus calendar periods, GAAP versus adjusted EPS, cumulative versus annual sales, royalty versus hardware margin, contract-specific complexity transmission and no addition of already included growth to consensus. Run calculate.py and verify deterministic results/input digest. Confirm all changed paths lie in this subtree.

Observed attempts: Yahoo analysis page returned HTTP 429; Stock Analysis supplied dated S&P Global consensus. Initial connector calls for issue-comment and branch search used incorrect parameter names and returned argument errors before mutation; corrected using tool declarations. HTTPS git push failed without local credentials; publication uses authorized connector. No financial conclusion depends on these failures.

Local arithmetic and JSON parsing are required before publication. CI and independent review are separately reported on GitHub; this document does not claim integrated functionality. No shared schema, workflow, canonical ticker, or market runtime files changed.

## Forward GAAP bridge review

Local historical reconciliation, independent forward arithmetic, fiscal boundary, ordinary R&D retention, share and cost sensitivities, parsing and byte-identical replay passed; see gaap-validation.json. Reconciled original 376m cash-flow SBC to 377m P&L SBC including software amortization. The note discloses the 1m difference; no unexplained source variance remains. Higher compensation inputs are scenarios, not a schedule inferred by dividing award backlog by its weighted-average duration. Third-party net-income estimates are a separate aggregate cross-check. Model has no unsupported scenario probabilities or asserted fair-value multiple. Exact-head CI must be fetched after publication; independent financial review remains pending.

## Compensation/dilution second-method review

Read annual and interim award/tax notes and dated net-income aggregates separately. Unrecognized Omnibus costs rose 98.1% March to September. Actual historical SBC tax-effect ratios (about 16% FY26 and 21% H1 FY27) support a sensitivity rather than one guaranteed tax shield. H1 basic versus diluted denominator difference is 1.03%; that is distinct from the large GAAP versus adjusted numerator difference. SBC expense is not cash returned to the company. New report preserves original GAAP stress cases and separately labels consensus-derived EPS. This owning-worker review is not independent acceptance. All local checks and byte-identical output replay passed.

## Growth-horizon correction

Earlier near-term GAAP scenarios did not fully present the published FYE31 growth case. Added management-target, consensus and unpriced-upside distinctions; annual segment mix is not a quarter-matched royalty bridge. Verified royalties accrue in shipment quarter, so blanket reporting-lag explanations are invalid. Contract volume tiers and licensing treatment of buy-downs are sourced mechanisms, not quantified causes of this quarter. Long-term $9 is adjusted, not GAAP EPS; future dilution unresolved. Local growth/horizon arithmetic and byte-identical replay passed.

## Five-year EPS table

Used one ChartMill series with FY26 $1.77 base and FY27-FY31 $2.28/$3.10/$4.15/$6.20/$10.40; both search systems returned the full sequence. Near-year S&P estimates differ by about one cent; distant-source coverage is not verified. Growth rates recomputed from rounded figures. Table, CSV and JSON replay identically; period/basis/holding-period caveats retained. This series does not replace earlier vendor-specific or GAAP bridge inputs.
