"""Deterministic research sensitivities; standard library only. No price prediction."""
from pathlib import Path
import json, hashlib
p = Path(__file__).resolve().parent
raw = (p / "inputs.json").read_bytes()
d = json.loads(raw)
a, o = d["assumptions"], d["observations"]
price = o["close"]
eps = d["consensus_adjusted_eps"]
y27, y28 = eps["FY27_ending_2027-03-31"], eps["FY28_ending_2028-03-31"]
scale = a["incremental_revenue_b"] * (1-a["tax_rate"]) / a["diluted_shares_b"]
r = {
 "model_version": d["model_version"], "input_sha256": hashlib.sha256(raw).hexdigest(),
 "close": price, "day_change_pct": (price/o["previous_close"]-1)*100,
 "pe_fy27": price/y27, "pe_fy28": price/y28,
 "fy27_eps_growth_pct": (y27/eps["FY26_actual"]-1)*100,
 "fy28_eps_growth_pct": (y28/y27-1)*100,
 "incremental_royalty_eps_range": [scale*m for m in a["incremental_royalty_operating_margin"]],
 "hardware_after_tax_gross_profit_per_share_before_incremental_opex": [scale*m for m in a["hardware_gross_margin"]],
 "license_share_of_q2_revenue_pct": o["q2_license_m"]/o["q2_revenue_m"]*100,
 "sbc_share_of_q2_revenue_pct": o["q2_sbc_m"]/o["q2_revenue_m"]*100,
 "valuation_grid": [{"fy28_eps_scenario": e, "pe_at_current_price": price/e,
   "price_at_40x": e*40, "price_at_50x": e*50} for e in a["fy28_eps_scenarios"]],
 "price_pe_fy28": [{"price": x, "pe": x/y28} for x in a["price_grid"]],
 "illustrative_stock_return_with_eps_growth_36pct_and_pe_80_to_50": (1.36*50/80-1)*100,
 "classification": "deterministic_sensitivity_not_prediction"
}
(p / "results.json").write_text(json.dumps(r, indent=2)+"\n")
print(json.dumps(r, indent=2))
