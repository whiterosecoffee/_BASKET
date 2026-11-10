"""Price-return attribution with explicit holding period and cost basis.

Synthetic constituent price bridge only, not realized fund NAV total return.
"""
from decimal import Decimal, InvalidOperation

VERSION = "etf-return-bridge@0.1.0"

def num(value):
    if isinstance(value, bool) or value is None:
        raise ValueError('finite numeric input required')
    try:
        x=Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError('invalid numeric input') from None
    if not x.is_finite():
        raise ValueError('finite numeric input required')
    return x

def bridge(earnings_change, multiple_factor, horizon_years,
           annual_expense_rate='0', round_trip_cost='0', return_basis='constituent_price_model'):
    """Return conditional share-price appreciation, gross and after modeled drags.

    Cost multiplication is an approximation and is NOT suitable for actual ETF
    NAV/market returns where fund expenses and tracking are already embedded.
    """
    e,m,years,fee,cost=map(num,(earnings_change,multiple_factor,horizon_years,
                                     annual_expense_rate,round_trip_cost))
    if return_basis != 'constituent_price_model':
        raise ValueError('observed ETF prices already embed fee/tracking differences')
    if e<=-1 or m<=0 or years<=0 or not 0<=fee<1 or not 0<=cost<1:
        raise ValueError('invalid model parameters')
    earnings=e
    multiple=m-1
    interaction=earnings*multiple
    gross_factor=(1+earnings)*m
    gross_price_return=gross_factor-1
    fee_factor=(1-fee)**years
    cost_factor=1-cost
    net_factor=gross_factor*fee_factor*cost_factor
    return {'schema':'basket.etf_price_bridge@1','version':VERSION,
        'horizon_years':str(years),'return_basis':return_basis,
        'earnings_component':str(earnings),'multiple_component':str(multiple),
        'interaction':str(interaction),'gross_price_return':str(gross_price_return),
        'annual_fee_drag_factor':str(fee_factor),'round_trip_cost_factor':str(cost_factor),
        'net_conditional_price_return':str(net_factor-1),
        'note':'Conditional synthetic share-price return; dividends and taxes excluded.'}
