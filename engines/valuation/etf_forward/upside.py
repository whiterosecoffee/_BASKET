"""Conditional price appreciation; scenarios are NOT predictions."""
from engine import dec
MODEL_VERSION = "etf-upside@0.1.0"

def project_case(earnings_change, multiple_change, annual_fee=0, trading_cost=0):
    e,m,fee,cost=map(dec,(earnings_change,multiple_change,annual_fee,trading_cost))
    if e<=-1 or m<=-1 or not 0<=fee<1 or not 0<=cost<1:
        raise ValueError("invalid factors")
    gross=(1+e)*(1+m)-1
    net=(1+gross)*(1-fee)*(1-cost)-1
    return {"earnings":str(e),"multiple":str(m),"interaction":str(e*m),
            "gross_price_return":str(gross),"net_price_return":str(net)}

def rank_candidates(candidates,scenarios,*,max_single_weight="0.5",min_stress_return="-0.5"):
    """Rank scenario resilience, not probabilistic expected performance."""
    if "stress" not in scenarios or "expansion" not in scenarios:
        raise ValueError("stress and expansion required")
    limit,floor=map(dec,(max_single_weight,min_stress_return))
    if not 0<limit<=1 or floor<-1:
        raise ValueError("invalid constraints")
    results=[]
    for candidate in candidates:
        weights={k:dec(v) for k,v in candidate["weights"].items()}
        if not weights or any(w<=0 or w>limit for w in weights.values()):
            raise ValueError("invalid concentration")
        if abs(sum(weights.values())-1)>dec("0.000001"):
            raise ValueError("weights must sum to one")
        fee,cost=map(dec,(candidate.get("fee","0"),candidate.get("trading_cost","0")))
        if not 0<=fee<1 or not 0<=cost<1:
            raise ValueError("invalid costs")
        returns={}
        for scenario_name,assumptions in scenarios.items():
            total=dec(0)
            for ticker,w in weights.items():
                if ticker not in assumptions:
                    raise ValueError("missing scenario ticker: "+ticker)
                x=assumptions[ticker]
                gross=dec(project_case(x["earnings_change"],x["multiple_change"])["gross_price_return"])
                total+=w*gross
            returns[scenario_name]=(1+total)*(1-fee)*(1-cost)-1
        results.append({"name":candidate["name"],"eligible":returns["stress"]>=floor,
                        "max_weight":str(max(weights.values())),
                        "stress_return":str(returns["stress"]),
                        "expansion_return":str(returns["expansion"]),
                        "worst_case_return":str(min(returns.values())),
                        "scenario_returns":{k:str(v) for k,v in returns.items()},
                        "quality":"synthetic_scenario_not_prediction"})
    return sorted(results,key=lambda z:(z["eligible"],dec(z["worst_case_return"]),
                                        dec(z["expansion_return"])),reverse=True)

def break_even_earnings_change(multiple_change,annual_fee=0,trading_cost=0):
    m,fee,cost=map(dec,(multiple_change,annual_fee,trading_cost))
    if m<=-1 or not 0<=fee<1 or not 0<=cost<1:
        raise ValueError("invalid assumptions")
    return str(1/((1+m)*(1-fee)*(1-cost))-1)
