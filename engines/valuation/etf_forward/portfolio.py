"""ETF/custom basket conditional return engine; no market-data fetching."""
import hashlib,json
from datetime import datetime
from decimal import Decimal
from engine import dec
from upside import project_case
VERSION="etf-portfolio@0.1.0"

def instant(value):
    t=datetime.fromisoformat(value.replace("Z","+00:00"))
    if t.tzinfo is None: raise ValueError("timezone required")
    return t

def compare(data):
    asof=instant(data["as_of"])
    if data.get("data_kind") not in ("synthetic_test","verified_observation"):
        raise ValueError("data_kind required")
    if not isinstance(data["source_manifest"],list) or not data["source_manifest"]:
        raise ValueError("source_manifest required")
    scenarios=data["scenarios"]
    if not {"stress","base","expansion"}.issubset(scenarios):
        raise ValueError("stress/base/expansion required")
    for x in scenarios.values():
        if instant(x["available_at"])>asof: raise ValueError("scenario lookahead")
    securities={}
    for s in data["securities"]:
        if s["id"] in securities: raise ValueError("duplicate security")
        if instant(s["available_at"])>asof: raise ValueError("security lookahead")
        if s["currency"]!="USD": raise ValueError("explicit USD inputs required")
        securities[s["id"]]=s
    output=[]
    for p in data["portfolios"]:
        if instant(p["holdings_available_at"])>asof: raise ValueError("holdings lookahead")
        weights={k:dec(v) for k,v in p["weights"].items()}
        if not weights or any(v<0 or v>1 for v in weights.values()):
            raise ValueError("invalid weights")
        if abs(sum(weights.values())-Decimal(1))>Decimal("0.000001"):
            raise ValueError("weights do not reconcile")
        if not set(weights).issubset(securities): raise ValueError("unknown constituent")
        fee=dec(p.get("holding_period_fees","0"))
        cost=dec(p.get("round_trip_cost","0"))
        if not 0<=fee<1 or not 0<=cost<1: raise ValueError("invalid costs")
        returns, attribution={},{}
        for name,scenario in scenarios.items():
            contrib={}
            for ticker,w in weights.items():
                if ticker not in scenario["constituents"]: raise ValueError("missing scenario constituent")
                a=scenario["constituents"][ticker]
                if instant(a["available_at"])>asof: raise ValueError("estimate lookahead")
                ret=dec(project_case(a["earnings_change"],a["multiple_change"])["gross_price_return"])
                contrib[ticker]=w*ret
            gross=sum(contrib.values())
            attribution[name]={k:str(v) for k,v in contrib.items()}
            returns[name]=str((1+gross)*(1-fee)*(1-cost)-1)
        output.append({"name":p["name"],"max_weight":str(max(weights.values())),
          "scenario_returns":returns,"contributions":attribution,
          "worst_scenario_return":str(min(map(dec,returns.values()))),
          "expansion_return":returns["expansion"]})
    output.sort(key=lambda x:(dec(x["worst_scenario_return"]),dec(x["expansion_return"])),reverse=True)
    digest=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {"schema":"basket.etf_portfolio_scenarios@1","version":VERSION,"data_kind":data["data_kind"],
       "as_of":data["as_of"],"sha256":digest,"source_manifest":data["source_manifest"],
       "portfolios":output,"interpretation":"Conditional snapshot model; fixed starting weights, no rebalancing or calibrated probabilities."}
