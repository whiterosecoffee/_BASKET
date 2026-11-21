# Adjusted margin sensitivity

Parent: feature-design.md and root AGENTS.md by reference. Existing planned node STX_NORMALIZED_MARGIN_BRIDGE is implemented only as an adjusted sensitivity, not a normalized GAAP model.

Input: dated revenue/EPS pairs and explicit margin, expense, tax and diluted-share assumptions. Output: internally consistent EPS and reverse-solved required gross margin; preserve vendor data conflicts. See margin-sensitivity.json for units and formula.

Prior art: conventional income-statement bridge and reverse valuation/sensitivity analysis. Operating margin cannot exceed gross margin under the same positive-OpEx basis. Aggregated consensus cohorts may differ; flag the conflict, do not infer the vendor's cause.

Review: independently replay round trips; verify accounting basis and fiscal periods; keep assumptions separate from management guidance. Missing GAAP reconciliation, analyst coverage, price/TB contracts and share-count forecast block promotion to an accepted valuation input.
