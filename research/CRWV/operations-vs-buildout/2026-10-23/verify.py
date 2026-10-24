"""Re-run derived arithmetic in findings.json from its own stated inputs. Exit 1 on mismatch."""
import json, sys, pathlib
f = json.loads((pathlib.Path(__file__).parent / "findings.json").read_text())
i = f["claims"]["issuer_statements_q2_2026"]
d = f["derived_arithmetic"]
rev, eb, da, intr, nl = (i[k] for k in ("revenue_usd_m","adj_ebitda_usd_m","d_and_a_usd_m","net_interest_expense_usd_m","net_loss_usd_m"))
chk = {
 "adj_ebitda": round(eb/rev*100,2), "d_and_a": round(da/rev*100,2), "net_interest": round(intr/rev*100,2),
 "other_stock_comp_tax_etc": round((-nl-(eb-da-intr))/rev*100,2),   # net_loss is a positive loss figure
 "net_loss": round(-nl/rev*100,2)}
exp = d["per_100_revenue_q2_2026"]
bad = [k for k in chk if abs(chk[k]-exp[k]) > 0.011]
assert not bad, ("per-100 mismatch", bad, chk, exp)
assert abs((da+intr)/rev*100 - d["buildout_cost_pct_of_revenue"]) < 0.011
ratio = intr/eb
assert abs(ratio*100 - d["interest_to_adj_ebitda_q2_pct"]) < 0.011
for k,v in (("low_interest_860",860),("mid_interest_900",900),("high_interest_940",940)):
    assert abs(v/ratio - d["q3_adj_ebitda_needed_to_hold_interest_ratio_usd_m"][k]) < 1.0, k
h1 = 6.8 + i["capex_q2_usd_b"]
assert abs(h1 - d["capex_h1_usd_b"]) < 0.05
mid = (35+39)/2
assert abs(mid-h1 - d["capex_h2_implied_midpoint_usd_b"]) < 0.05
q3mid = (11.5+13.5)/2
assert abs(mid-h1-q3mid - d["capex_q4_implied_usd_b"]["midpoint"]) < 0.05
assert abs(35-h1-13.5 - d["capex_q4_implied_usd_b"]["low"]) < 0.05
assert abs(39-h1-11.5 - d["capex_q4_implied_usd_b"]["high"]) < 0.05
a = d["active_over_contracted_pct"]
assert abs(1.5/3.7*100 - a["vs_3_7gw_at_2026_06_30"]) < 0.06
assert abs(1.5/4.2*100 - a["vs_4_2gw_at_2026_08_11"]) < 0.06
assert abs(1.85/4.2*100 - a["year_end_target_vs_4_2gw"]) < 0.06
assert abs(4.2-1.85 - d["contracted_not_active_after_year_end_target_gw"]) < 0.001
c = d["capex_funding_ratios_pct"]
assert abs(32/mid*100 - c["secured_capital_over_fy_capex_midpoint"]) < 0.06
assert abs(6.91/mid*100 - c["ttm_operating_cash_flow_over_fy_capex_midpoint"]) < 0.06
t = f["tape"]["closes_usd"]
assert abs((t["2026-10-23"]/t["2026-10-12"]-1)*100 - d["cumulative_move_2026_10_12_to_10_23_pct"]) < 0.011
print("verify.py: all derived figures reproduce"); sys.exit(0)
