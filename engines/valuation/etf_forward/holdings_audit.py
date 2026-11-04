"""Fail-closed issuer holdings coverage audit for ETF forward valuation."""
from decimal import Decimal
from engine import dec, known_by
def audit_holdings(snapshot,as_of,minimum_coverage="0.999"):
    if snapshot.get("source_class")!="issuer_primary":
        raise ValueError("issuer primary holdings required")
    if not snapshot.get("source_url") or not snapshot.get("as_of") or not snapshot.get("available_at"):
        raise ValueError("dated source URL and availability required")
    known_by(snapshot["available_at"],as_of)
    if snapshot["as_of"]>as_of[:10]:
        raise ValueError("future holdings")
    rows=snapshot.get("holdings",[])
    if not rows: raise ValueError("no holdings")
    if len({r["id"] for r in rows})!=len(rows): raise ValueError("duplicate holding")
    weights=[dec(r["weight_pct"]) for r in rows]
    if any(w<0 for w in weights): raise ValueError("negative holding weights require explicit liability treatment")
    total=sum(weights,Decimal("0"))
    if total>Decimal("100.01"): raise ValueError("weights exceed fund assets")
    coverage=total/100
    threshold=dec(minimum_coverage)
    if not Decimal("0")<threshold<=1:raise ValueError("invalid coverage threshold")
    missing=Decimal("1")-coverage
    ready=coverage>=threshold and total<=Decimal("100.01") and snapshot.get("full_issuer_file") is True
    return {"ticker":snapshot["ticker"],"as_of":snapshot["as_of"],"rows":len(rows),
            "verified_weight_fraction":str(coverage),"missing_weight_fraction":str(max(missing,Decimal("0"))),
            "full_fund_valuation_eligible":ready,
            "reason":"complete issuer snapshot" if ready else "partial issuer holdings or insufficient weight coverage"}
