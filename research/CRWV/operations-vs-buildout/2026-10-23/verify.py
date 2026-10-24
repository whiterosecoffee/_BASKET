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
print("verify.py: all derived figures reproduce")

# ---- addendum-replacement-cost-and-rates.json ----
a = json.loads((pathlib.Path(__file__).parent / "addendum-replacement-cost-and-rates.json").read_text())
A, ad = a["assumptions"], a["derived_arithmetic"]
gw = A["active_power_gw"]
for k, m in (("at_30m_per_mw",30),("at_40m_per_mw",40),("at_50m_per_mw",50)):
    assert abs(gw*m - ad["replacement_cost_active_fleet_usd_b"][k]) < 0.05, k
for k, key in (("debt_only","debt_only_2026_06_30"),("pro_forma","pro_forma_third_party"),("including_leases","including_leases_2026_06_30")):
    ev = A["market_cap_usd_b"] + A["debt_cases_usd_b"][key] - A["cash_usd_b"] - A["cip_usd_b"]
    assert abs(ev/(gw*1000)*1000 - ad["ev_net_of_cip_per_active_mw_usd_m"][k]) < 0.06, k
assert abs(40/1.375 - ad["implied_pre_increase_rate_usd_m_per_mw"]["if_both_increases_apply"]) < 0.06
assert abs(40/1.25 - ad["implied_pre_increase_rate_usd_m_per_mw"]["if_only_25pct_applies"]) < 0.06
assert abs(18.5/1.85 - ad["exit_arr_per_mw_usd_m"]["low_18_5b"]) < 0.06
assert abs(19.5/1.85 - ad["exit_arr_per_mw_usd_m"]["high_19_5b"]) < 0.06
assert abs(8*6.16*8760/A["node_power_kw_8gpu_h100"]*1000/1e6 - ad["list_price_equivalent_usd_m_per_mw_h100"]) < 0.06
eb40 = 40*A["ebitda_margin_pct"]/100
assert abs(eb40 - ad["ebitda_per_mw_usd_m_at_40m_revenue"]) < 0.06
assert abs(30/eb40 - ad["gross_payback_years_at_40m_revenue"]["vs_30m_build"]) < 0.01
assert abs(50/eb40 - ad["gross_payback_years_at_40m_revenue"]["vs_50m_build"]) < 0.01
assert abs(30/(19.5/1.85*A["ebitda_margin_pct"]/100) - ad["gross_payback_years_at_legacy_arr"]["low"]) < 0.01
assert abs(50/(18.5/1.85*A["ebitda_margin_pct"]/100) - ad["gross_payback_years_at_legacy_arr"]["high"]) < 0.01
assert abs(i["d_and_a_usd_m"]*(1-6/8) - ad["d_and_a_sensitivity_6_to_8_year_life"]["usd_m_per_quarter_upper_bound"]) < 0.01
print("verify.py: addendum figures reproduce")
sys.exit(0)
