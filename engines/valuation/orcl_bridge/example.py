"""Entirely synthetic fixture generator. No figures are actual ORCL/peer observations."""
from datetime import timedelta
from engines.valuation.orcl_bridge.engine import timestamp, METRICS


def fixture(as_of='2026-10-26T14:00:00Z'):
    at = timestamp(as_of)
    horizon = at.replace(hour=0,minute=0,second=0,microsecond=0)
    forecast = {'horizon_start':horizon.isoformat(), 'horizon_end':(horizon+timedelta(days=365)).isoformat(),
        'earnings_basis':'GAAP','lease_basis':'included_consistent','revenue':1_000_000_000,
        'ebit':300_000_000,'da':50_000_000,'capex':100_000_000,'delta_nwc':20_000_000,
        'cash_interest':20_000_000,'tax_rate':0.2,'diluted_shares':100_000_000}
    balance = {'debt':200_000_000,'cash':50_000_000,'leases':10_000_000,'preferred':0,'minority':0}
    def record(data, key):
        return {'source_id':'SYNTHETIC-'+key,'sources':['https://example.com/synthetic-only'],
            'effective_at':as_of,'observed_at':as_of,'available_at':as_of,'ingested_at':as_of,
            'expires_at':(at+timedelta(hours=1)).isoformat(),'verification':'verified',
            'classification':'source_fact','data':dict(data)}
    companies = {ticker:{'ticker':ticker,'currency':'USD','quote':record({'price':price},ticker+'quote'),
        'forecast':record(forecast,ticker+'forecast'),'balance':record(balance,ticker+'balance')}
        for ticker,price in [('ORCL',50),('IBM',60),('MSFT',80)]}
    def case(change,pe):
        return {'rationale':'SYNTHETIC sensitivity only; not an investment forecast',
            'falsifiers':['Replace all fabricated inputs before evaluating ORCL'],
            'revenue_change':change,'margin_change':0,'capex_change':0,'delta_nwc_change':0,
            'da_change':0,'new_debt':0,'equity_raise':0,'additional_shares':0,'retained_funding_cash':0,
            'new_debt_rate':0,'new_debt_year_fraction':1,'issue_price':50,'repricing':[],
            'multiples':{'pe':pe,'ev_ebitda':15,'ev_sales':5,'price_equity_fcf':30,'ev_fcff':30}}
    return {'schema':'basket.valuation_input@1','data_mode':'synthetic','target':'ORCL',
            'peer_weights':{'IBM':0.5,'MSFT':0.5},'companies':companies,
            'scenarios':{'bear':case(-0.1,18),'base':case(0,22),'bull':case(0.1,26)}}


if __name__=='__main__':
    import json
    print(json.dumps(fixture(),indent=2))
