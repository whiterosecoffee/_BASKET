"""Rebuild explicitly synthetic fixtures. Nothing here is a CRWV balance estimate."""
import json
from pathlib import Path
root=Path(__file__).parent
source=dict(id='SYNTHETIC',revision='demo-v1',source_class='scenario_assumption',available_at='2026-10-26T12:00:00Z',effective_at='2026-10-26T12:00:00Z',observed_at='2026-10-26T12:00:00Z',ingested_at='2026-10-26T12:00:00Z',period_end=None,expires_at='2027-01-01T00:00:00Z')
prov=dict(source_ids=['SYNTHETIC'])
contracts=[dict(id='old',start_month=0,end_month=120,annual_usd_per_it_mw=12_000_000,rpo_remaining=1_200_000_000,pool='old_RPO',minimum_utilization=0,**prov),dict(id='new',start_month=3,end_month=120,annual_usd_per_it_mw=15_000_000,rpo_remaining=1_500_000_000,pool='new_booking_not_old_RPO',minimum_utilization=0,**prov)]
cohorts=[]
for name,ready in [('legacy',0),('addition',3)]:
    cohorts.append(dict(id=name,contract_id='old' if ready==0 else 'new',power_basis='IT_MW',contracted_mw=10,energized_month=max(0,ready-2),installed_month=max(0,ready-1),accepted_month=ready,billable_month=ready,utilization=.8,capex_month=-1 if ready==0 else 1,growth_capex=0 if ready==0 else 60_000_000,book_value=60_000_000 if ready==0 else 0,accounting_months_remaining=72,earning_months_remaining=108,residual=0,generation='hypothetical_GPU',**prov))
facilities=[]
for name,kind,balance in [('fixed','fixed',12_000_000),('floating','floating',12_000_000)]:
    facilities.append(dict(id=name,balance=balance,commitment=30_000_000,eligible_undrawn=18_000_000,draws={'1':10_000_000},principal={},rate_type=kind,coupon=.06,spread=.03,floor=.02,hedge_fraction=.5 if kind=='floating' else 0,hedge_rate=.04,fee_fraction=.01,capitalized_fraction=0,restricted=False,maturity_month=90,conditions_met=True,minimum_cash=0,**prov))
snapshot=dict(schema='crwv.snapshot@1',synthetic=True,currency='USD',start='2026-11-01T00:00:00Z',sources=[source],opening=dict(cash=100_000_000,restricted_cash=0,shares=10_000_000,**prov),cohorts=cohorts,contracts=contracts,facilities=facilities,costs=dict(direct_fraction=.35,corporate_monthly=1_000_000,sbc_monthly=100_000,tax_rate=.21,sustaining_monthly=500_000,**prov),capitalization=dict(sbc_share_price=10,**prov),quote=dict(usd=20,available_at='2026-10-27T14:00:00Z',expires_at='2026-10-28T14:00:00Z',source_ids=['SYNTHETIC']))
base=dict(months=120,discount_rate=.12,terminal_growth=.02,benchmark=.04,equity_issues=[],changes=[],pe_multiple=15,reverse_annual_price_per_it_mw=12_000_000,terminal_continuation_approved=False,weights={'slow':.3,'base':.5,'bull':.2},weight_class='subjective')
configs={'base':base,'slow':dict(base,price_multiplier=.8,acceptance_delay_months=6),'bull':dict(base,price_multiplier=1.2),'unfunded':dict(base,benchmark_shock=.05)}
for name,obj in [('snapshot',snapshot)]+list(configs.items()):
    (root/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
unfunded=json.loads(json.dumps(snapshot))
unfunded['opening']['cash']=0
for f in unfunded['facilities']:
    f['conditions_met']=False
(root/'unfunded-snapshot.json').write_text(json.dumps(unfunded,indent=2)+'\n')
