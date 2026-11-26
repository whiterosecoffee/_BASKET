"""Re-run derived arithmetic in findings.json from its own stated inputs. Exit 1 on mismatch."""
import json, sys, pathlib
a = json.loads((pathlib.Path(__file__).parent / "findings.json").read_text())
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
assert abs(A["q2_d_and_a_usd_m"]*(1-6/8) - ad["d_and_a_sensitivity_6_to_8_year_life"]["usd_m_per_quarter_upper_bound"]) < 0.01
print("verify.py: all figures reproduce"); sys.exit(0)
