"""CRWV domain component. Pure local USD scenario arithmetic; no network calls."""
from __future__ import annotations
import copy
import hashlib
import json
import math
from datetime import datetime, timezone

VERSION = 'crwv-economics@0.1.0'
SOURCE_SHA = '29463811e8f77eac9d05b631fcb1c6190bf3f3ff'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def instant(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timezone required')
    return dt.astimezone(timezone.utc)


def month_add(value, count):
    dt = instant(value)
    n = dt.year * 12 + dt.month - 1 + count
    return dt.replace(year=n // 12, month=n % 12 + 1, day=1).isoformat()


def number(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name}: finite number >= {minimum} required')
    return value


def require(obj, keys):
    for key in keys:
        if key not in obj or obj[key] is None:
            raise ValueError(f'Missing required input: {key}')


def validate(snapshot, config, as_of):
    require(snapshot, ['schema', 'currency', 'start', 'sources', 'opening', 'cohorts', 'contracts', 'facilities', 'costs', 'capitalization'])
    if snapshot['schema'] != 'crwv.snapshot@1' or snapshot['currency'] != 'USD':
        raise ValueError('Expected crwv.snapshot@1 in USD')
    allowed={'schema','synthetic','currency','start','sources','opening','cohorts','contracts','facilities','costs','capitalization','quote','market_observations','unsupported_features'}
    if set(snapshot)-allowed:
        raise ValueError('Unknown snapshot groups: '+str(set(snapshot)-allowed))
    cut = instant(as_of)
    if instant(snapshot['start']) < cut or instant(snapshot['start']).day != 1:
        raise ValueError('Forecast start must be a month boundary at/after as_of')
    require(config, ['months', 'discount_rate', 'terminal_growth', 'benchmark', 'equity_issues', 'changes'])
    if config['changes']:
        raise ValueError('Mid-forecast estimate changes require a new revision; changes must be empty in v1')
    if config['months'] < 36 or config['months'] != int(config['months']):
        raise ValueError('At least 36 monthly periods required')
    number(config['discount_rate'], 'discount_rate')
    if not -1 < config['terminal_growth'] < config['discount_rate']:
        raise ValueError('Terminal growth must be below discount rate and above -1')
    sources = {}
    if snapshot.get('unsupported_features'):
        raise ValueError('Unsupported requested features: '+str(snapshot['unsupported_features']))
    for src in snapshot['sources']:
        require(src, ['id', 'revision', 'source_class', 'observed_at', 'ingested_at'])
        if src['id'] in sources:
            raise ValueError('Duplicate source ID')
        if not src.get('available_at') or instant(src['available_at']) > cut:
            raise ValueError('Required source unavailable at cutoff: ' + src['id'])
        sources[src['id']] = src
    # Every required economic group has explicit provenance; assumptions are sources too.
    groups = [snapshot['opening'], snapshot['costs'], snapshot['capitalization']] + snapshot['cohorts'] + snapshot['contracts'] + snapshot['facilities']
    for group in groups:
        if not group.get('source_ids') or any(s not in sources for s in group['source_ids']):
            raise ValueError('Missing/unknown source IDs')
    for key in ['cash', 'restricted_cash', 'shares']:
        number(snapshot['opening'].get(key), key)
    if snapshot['opening']['shares'] == 0:
        raise ValueError('Positive shares required')
    for group, keys in [(snapshot['costs'], ['direct_fraction', 'corporate_monthly', 'sbc_monthly', 'tax_rate', 'sustaining_monthly']), (snapshot['capitalization'], ['sbc_share_price'])]:
        for key in keys:
            number(group.get(key), key)
    if snapshot['costs']['direct_fraction'] > 1 or snapshot['costs']['tax_rate'] > 1 or snapshot['capitalization']['sbc_share_price'] == 0:
        raise ValueError('Invalid cost/tax/issue-price bounds')
    for collection in ['cohorts', 'contracts', 'facilities']:
        ids = [x['id'] for x in snapshot[collection]]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate ' + collection)
    contracts = {c['id']: c for c in snapshot['contracts']}
    for c in snapshot['contracts']:
        if c.get('cash_lag_months',0) < 0 or int(c.get('cash_lag_months',0)) != c.get('cash_lag_months',0):
            raise ValueError('Cash lag must be a nonnegative integer')
        require(c, ['start_month', 'end_month', 'annual_usd_per_it_mw', 'rpo_remaining', 'pool', 'minimum_utilization'])
        for k in ['annual_usd_per_it_mw', 'rpo_remaining', 'minimum_utilization']:
            number(c[k], k)
        if c['minimum_utilization'] > 1 or c['start_month'] > c['end_month']:
            raise ValueError('Invalid contract')
    for c in snapshot['cohorts']:
        require(c, ['contract_id', 'power_basis', 'contracted_mw', 'energized_month', 'installed_month', 'accepted_month', 'billable_month', 'utilization', 'capex_month', 'growth_capex', 'book_value', 'accounting_months_remaining', 'earning_months_remaining', 'residual', 'generation'])
        if c['contract_id'] not in contracts or c['power_basis'] != 'IT_MW':
            raise ValueError('Contract reference or comparable IT power basis missing')
        for k in ['contracted_mw', 'utilization', 'growth_capex', 'book_value', 'residual']:
            number(c[k], k)
        if c['utilization'] > 1 or not 0 <= c['energized_month'] <= c['installed_month'] <= c['accepted_month'] <= c['billable_month']:
            raise ValueError('Invalid cohort chronology/utilization')
        for k in ['accounting_months_remaining', 'earning_months_remaining']:
            if c[k] <= 0 or c[k] != int(c[k]):
                raise ValueError('Positive integral remaining life required')
        if c['billable_month']+config.get('acceptance_delay_months',0)+round(c['earning_months_remaining']*config.get('earning_life_multiplier',1)) >= config['months']:
            raise ValueError('Extend forecast through equipment earning life and disposal')
        if c['residual'] > c['book_value'] + c['growth_capex']:
            raise ValueError('Residual exceeds depreciable basis')
    for f in snapshot['facilities']:
        require(f, ['balance', 'commitment', 'eligible_undrawn', 'draws', 'principal', 'rate_type', 'coupon', 'spread', 'floor', 'hedge_fraction', 'hedge_rate', 'fee_fraction', 'capitalized_fraction', 'restricted', 'maturity_month', 'conditions_met', 'minimum_cash'])
        for k in ['balance', 'commitment', 'eligible_undrawn', 'coupon', 'spread', 'floor', 'hedge_fraction', 'hedge_rate', 'fee_fraction', 'capitalized_fraction', 'minimum_cash']:
            number(f[k], k)
        if f['balance'] + f['eligible_undrawn'] > f['commitment'] or f['rate_type'] not in ['fixed', 'floating'] or max(f['hedge_fraction'], f['capitalized_fraction']) > 1:
            raise ValueError('Invalid facility bounds')
        for schedule in ['draws', 'principal']:
            for v in f[schedule].values():
                number(v, schedule)
    for e in config['equity_issues']:
        require(e, ['month', 'amount', 'price', 'fee_fraction', 'approved'])
        if number(e['price'], 'equity price') == 0 or number(e['fee_fraction'], 'equity fee') >= 1:
            raise ValueError('Invalid equity terms')
        number(e['amount'], 'equity amount')
    weights = config.get('weights')
    if weights is not None and (config.get('weight_class') != 'subjective' or any(v < 0 for v in weights.values()) or abs(sum(weights.values()) - 1) > 1e-9):
        raise ValueError('Weights must sum to one and remain subjective; calibration not implemented')
    for k in ['price_multiplier','depreciation_life_multiplier','earning_life_multiplier']:
        if k in config and number(config[k],k) <= 0:
            raise ValueError('Positive multiplier required')
    for k in ['acceptance_delay_months']:
        if k in config and (number(config[k],k) != int(config[k])):
            raise ValueError('Integral delay required')
    if config.get('capitalized_interest_amortization_months',72) <= 0:
        raise ValueError('Positive capitalized-interest life required')
    return sources


def forecast(snapshot, config):
    """Accrual revenue collected same month; no implicit funding, WC or tax-loss assets."""
    s = copy.deepcopy(snapshot)
    contracts = {c['id']: c for c in s['contracts']}
    cash = s['opening']['cash']
    restricted = s['opening']['restricted_cash']
    shares = s['opening']['shares']
    rows, first_gap = [], None
    remaining_rpo = {c['id']: c['rpo_remaining'] for c in s['contracts']}
    assets = {c['id']: c['book_value'] for c in s['cohorts']}
    interest_assets = []
    collections = {}
    capitalized = 0
    for m in range(config['months']):
        old_cash, old_restricted, old_shares = cash, restricted, shares
        revenue = active = billable = contracted = capex = depreciation = residual_cash = disposal_loss = 0
        deferred_receipts = prepayments = 0
        cohorts = []
        for c in s['cohorts']:
            delay = config.get('acceptance_delay_months', 0)
            spend_m = c['capex_month'] + delay if c['capex_month'] >= 0 else c['capex_month']
            ready = c['billable_month'] + delay
            accepted = c['accepted_month'] + delay
            installed = c['installed_month'] + delay
            energized = c['energized_month'] + delay
            ct = contracts[c['contract_id']]
            contracted += c['contracted_mw']
            active += c['contracted_mw'] if m >= energized else 0
            if m == spend_m:
                capex += c['growth_capex']
                assets[c['id']] += c['growth_capex']
            earning_end = ready + round(c['earning_months_remaining'] * config.get('earning_life_multiplier', 1))
            eligible = max(ready, ct['start_month']) <= m < min(earning_end, ct['end_month'])
            mw = c['contracted_mw'] * max(c['utilization'], ct['minimum_utilization']) if eligible else 0
            rev = mw * ct['annual_usd_per_it_mw'] * config.get('price_multiplier', 1) / 12
            rev = min(rev, remaining_rpo[ct['id']])
            remaining_rpo[ct['id']] -= rev
            revenue += rev
            lag = ct.get('cash_lag_months', 0)
            collections[m+lag] = collections.get(m+lag, 0) + rev
            prepayments += ct.get('prepayments', {}).get(str(m), 0)
            billable += mw
            life = max(1, round(c['accounting_months_remaining'] * config.get('depreciation_life_multiplier', 1)))
            if m == earning_end:
                disposal_loss += max(0,assets[c['id']]-c['residual'])
                assets[c['id']] = 0
            dep = min(max(0, assets[c['id']] - c['residual']), (c['book_value'] + c['growth_capex'] - c['residual']) / life) if installed <= m < earning_end else 0
            assets[c['id']] -= dep
            depreciation += dep
            if m == earning_end:
                residual_cash += c['residual']
            cohorts.append(dict(id=c['id'], contracted_it_mw=c['contracted_mw'], energized_it_mw=c['contracted_mw'] if m >= energized else 0, installed_it_mw=c['contracted_mw'] if installed <= m < earning_end else 0, accepted_it_mw=c['contracted_mw'] if m >= accepted else 0, billable_it_mw=mw, revenue=rev, contract_pool=ct['pool'], rpo_remaining=remaining_rpo[ct['id']]))
        if prepayments:
            raise ValueError('Prepayment schedules require deferred-revenue reconciliation; not supported by contract v1')
        collection = collections.pop(m, 0)
        for asset in interest_assets:
            d = min(asset['balance'], asset['monthly'])
            asset['balance'] -= d
            depreciation += d
        costs = s['costs']
        direct = revenue * costs['direct_fraction']
        corporate, sbc = costs['corporate_monthly'], costs['sbc_monthly']
        sustaining = costs['sustaining_monthly']
        draws = fees = interest = interest_expensed = principal_due = principal_paid = 0
        instruments = []
        for f in s['facilities']:
            opening = f['balance']
            # Check covenant on opening unrestricted cash; restricted funds cannot cure it.
            allowed = f['conditions_met'] and old_cash >= f['minimum_cash'] and m < f['maturity_month']
            requested = f['draws'].get(str(m), 0)
            draw = min(requested, f['eligible_undrawn'], f['commitment'] - opening) if allowed else 0
            f['eligible_undrawn'] -= draw
            fee = draw * f['fee_fraction']
            if f['restricted']:
                restricted += draw - fee
            else:
                cash += draw - fee
            rate = f['coupon'] if f['rate_type'] == 'fixed' else f['spread'] + (1 - f['hedge_fraction']) * max(f['floor'], config['benchmark'] + config.get('benchmark_shock', 0)) + f['hedge_fraction'] * f['hedge_rate']
            accrued = (opening + draw) * rate / 12
            due = opening + draw if m >= f['maturity_month'] else min(opening + draw, f['principal'].get(str(m), 0))
            instruments.append(dict(id=f['id'], opening=opening, draw=draw, requested_draw=requested, annual_rate=rate, cash_interest=accrued, expensed_interest=accrued*(1-f['capitalized_fraction']), capitalized_interest=accrued*f['capitalized_fraction'], fee=fee, principal_due=due, restricted=f['restricted']))
            f['balance'] += draw
            draws += draw
            fees += fee
            interest += accrued
            interest_expensed += accrued*(1-f['capitalized_fraction'])
            principal_due += due
        ebitda = revenue - direct - corporate
        ebit = ebitda - sbc - depreciation - disposal_loss
        pretax = ebit - interest_expensed - fees
        tax = max(0, pretax) * costs['tax_rate']
        net_income = pretax - tax
        ocf = net_income + depreciation + disposal_loss + sbc + interest_expensed - interest + fees + collection - revenue
        added_interest_asset = interest - interest_expensed
        if added_interest_asset:
            interest_assets.append(dict(balance=added_interest_asset, monthly=added_interest_asset/config.get('capitalized_interest_amortization_months',72)))
        # SBC is expensed and adds shares; no fictional cash proceeds.
        sbc_shares = sbc / s['capitalization']['sbc_share_price']
        equity_net = equity_gross = equity_shares = 0
        for e in config['equity_issues']:
            if e['approved'] and e['month'] == m:
                equity_gross += e['amount']
                equity_net += e['amount']*(1-e['fee_fraction'])
                equity_shares += e['amount']/e['price']
        shares += sbc_shares + equity_shares
        cash += ocf + equity_net + residual_cash
        # Restricted project cash may pay only growth capex, never general debt service.
        restricted_spend = min(restricted, capex)
        restricted -= restricted_spend
        cash -= capex - restricted_spend + sustaining
        for f, item in zip(s['facilities'], instruments):
            paid = min(max(0, cash), item['principal_due'])
            cash -= paid
            f['balance'] -= paid
            item['principal_paid'] = paid
            item['closing'] = f['balance']
            item['unpaid_principal'] = item['principal_due'] - paid
            principal_paid += paid
        gap = max(0, -cash) + principal_due - principal_paid
        if gap > 1e-8 and first_gap is None:
            first_gap = m
        # Negative cash is an explicitly unfunded conditional plan, never a financing source.
        capitalized = sum(a['balance'] for a in interest_assets)
        weighted_shares = (old_shares + shares)/2
        row = dict(month=m, period=month_add(s['start'], m), cohorts=cohorts, contracted_it_mw=contracted, active_it_mw=active, billable_it_mw=billable, revenue=revenue, direct_cost=direct, corporate_cost=corporate, adjusted_ebitda=ebitda, sbc=sbc, depreciation=depreciation, disposal_loss=disposal_loss, ebit=ebit, cash_interest=interest, expensed_interest=interest_expensed, capitalized_interest=interest-interest_expensed, capitalized_interest_asset=capitalized, fees=fees, taxes=tax, net_income=net_income, eps=net_income/weighted_shares, operating_cash=ocf, cash_collections=collection, receivables=sum(collections.values()), growth_capex=capex, sustaining_capex=sustaining, residual_cash=residual_cash, instruments=instruments, debt_draws=draws, principal_due=principal_due, principal_paid=principal_paid, closing_debt=sum(f['balance'] for f in s['facilities']), opening_cash=old_cash, closing_cash=cash, restricted_cash=restricted, opening_restricted_cash=old_restricted, restricted_capex_paid=restricted_spend, equity_gross=equity_gross, equity_net=equity_net, equity_shares=equity_shares, sbc_shares=sbc_shares, diluted_shares=shares, weighted_shares=weighted_shares, funding_gap=gap, funding_state='unfunded_conditional_plan' if first_gap is not None else 'funded', fcfe_after_net_borrowing=ocf-capex-sustaining+residual_cash+draws-fees-principal_due)
        row['cash_conservation_error'] = cash + restricted - (old_cash + old_restricted + draws - fees + ocf + equity_net + residual_cash - capex - sustaining - principal_paid)
        row['debt_conservation_error'] = row['closing_debt'] - sum(i['opening'] + i['draw'] - i['principal_paid'] for i in instruments)
        rows.append(row)
    return rows, first_gap


def valuation(rows, config, as_of, start, horizons):
    """Runoff equity DCF: retained cash, explicit issues and terminal liquidation.

    No hypothetical distributions while the same cash funds the build. The last
    balance includes funding receipts, all cash uses and debt service; subtract
    only outstanding terminal debt, never opening debt a second time. One share
    remains one share; new issues dilute the terminal claim.
    """
    if config.get('terminal_continuation_approved', False):
        raise ValueError('Perpetual terminal continuation requires a replacement-capital contract; v1 supports finite runoff')
    r = config['discount_rate']
    curve = []
    final = rows[-1]
    terminal_equity = final['closing_cash'] + final['restricted_cash'] - final['closing_debt']
    # Restricted cash available only after repaying all modeled project claims.
    for h in [0] + list(horizons):
        if h >= len(rows)-12:
            raise ValueError('Need a full annual forecast after each valuation horizon')
        shares = rows[h-1]['diluted_shares'] if h else config['_opening_shares']
        per_share = terminal_equity/final['diluted_shares']/(1+r)**((len(rows)-h)/12)
        # Current market-cap equivalent and terminal share convention are explicit.
        equity = per_share * shares
        future_ni = sum(x['net_income'] for x in rows[h:h+12])
        annual_eps = future_ni/(sum(x['weighted_shares'] for x in rows[h:h+12])/12)
        curve.append(dict(valuation_as_of=as_of, target_date=as_of if h == 0 else month_add(start,h), financial_forecast_period=[rows[h]['period'],rows[h+11]['period']], horizon_months=h, method='finite_runoff_equity_DCF_retained_cash_terminal_liquidation_after_outstanding_debt', equity_value=equity, diluted_shares=shares, terminal_diluted_shares=final['diluted_shares'], conditional_value_per_share=max(0,per_share), forward_12m_eps=annual_eps, pe_value_per_share=max(0,annual_eps)*config.get('pe_multiple',0) if annual_eps>0 and config.get('pe_multiple') is not None else None, terminal_equity=terminal_equity, status='conditional_scenario_not_price_prediction'))
    return curve


def reverse_valuation(row, quote, multiple, tax_rate, annual_price_per_mw):
    """One-variable-at-a-time solutions; not an identified joint market forecast."""
    for v in [quote,multiple,annual_price_per_mw]:
        if v <= 0:
            raise ValueError('Positive reverse valuation basis required')
    shares = row['diluted_shares']
    required_ni = quote * shares/multiple
    pretax = required_ni/(1-tax_rate)
    fixed = 12*(row['corporate_cost']+row['sbc']+row['depreciation']+row['expensed_interest']+row['fees'])
    direct_fraction = row['direct_cost']/row['revenue'] if row['revenue'] else None
    revenue = (pretax+fixed)/(1-direct_fraction) if direct_fraction is not None and direct_fraction<1 else None
    required_margin = (pretax + 12*(row['expensed_interest']+row['fees']))/(12*row['revenue']) if row['revenue'] else None
    return dict(method='P/E inverse holding all other inputs fixed independently', quote_usd=quote, required_net_income=required_ni, required_revenue=revenue, required_billable_it_mw=revenue/annual_price_per_mw if revenue is not None else None, required_annual_revenue_per_it_mw=revenue/row['billable_it_mw'] if revenue is not None and row['billable_it_mw'] else None, required_ebit_margin=required_margin, maximum_net_interest=12*row['ebit']-pretax, maximum_diluted_shares=12*row['net_income']*multiple/quote, caveat='Quote does not uniquely determine capacity, pricing, margin, interest or dilution')


def lifecycle(keep_cashflows, discount_rate, resale, invoice, credit, upgrade_cashflows, downtime_months=0):
    """Mutually exclusive keep/surrender branches; credit is hypothetical input."""
    for v in [resale, invoice, credit]:
        number(v, 'lifecycle')
    if credit > invoice:
        raise ValueError('Credit exceeds invoice')
    pv = lambda flows: sum(v/(1+discount_rate)**((i+1)/12) for i,v in enumerate(flows))
    keep = pv(keep_cashflows) + resale/(1+discount_rate)**(len(keep_cashflows)/12)
    upgrade = -invoice + credit + pv([0]*downtime_months + list(upgrade_cashflows))
    return dict(keep_npv=keep, upgrade_npv=upgrade, incremental_upgrade_npv=upgrade-keep, credit_class='hypothetical_not_verified_NVIDIA_guarantee', old_fleet_earnings_in_upgrade=0)


def evaluate(snapshot, scenario_config, as_of, horizons=(3,6,12,24)):
    config = copy.deepcopy(scenario_config)
    sources = validate(snapshot, config, as_of)
    config['_opening_shares'] = snapshot['opening']['shares']
    rows, gap = forecast(snapshot, config)
    curve = valuation(rows, config, as_of, snapshot['start'], horizons)
    if gap is not None:
        for point in curve:
            point['conditional_value_per_share'] = None
            point['pe_value_per_share'] = None
            point['status'] = 'blocked_unfunded_plan'
    stale = [s['id'] for s in sources.values() if not s.get('expires_at') or instant(s['expires_at']) <= instant(as_of)]
    dependencies = sorted(sources)
    metadata = dict(units='USD, shares, IT_MW, monthly periods; rates annual decimals', period=[rows[0]['period'],rows[-1]['period']], status='synthetic_scenario' if snapshot.get('synthetic') else 'dated_conditional_scenario', source_ids=dependencies, dependencies=['snapshot:'+digest(snapshot),'config:'+digest(scenario_config)], method_version=VERSION, expires_at=min((s['expires_at'] for s in sources.values() if s.get('expires_at')),default=None))
    reverse = None
    if snapshot.get('quote') is not None:
        q = snapshot['quote']
        if q.get('available_at') and instant(q['available_at'])<=instant(as_of) and q.get('expires_at') and instant(q['expires_at'])>instant(as_of):
            reverse = reverse_valuation(rows[0],q['usd'],config['pe_multiple'],snapshot['costs']['tax_rate'],config['reverse_annual_price_per_it_mw'])
    return dict(schema='crwv.analysis@1',engine_version=VERSION,source_spec_commit=SOURCE_SHA,implementation_commit=scenario_config.get('implementation_commit'),input_hash=digest(snapshot),config_hash=digest(scenario_config),valuation_as_of=as_of,classification='scenario',metric_metadata=metadata,freshness=dict(stale_source_ids=stale,current_claim_allowed=not stale and not snapshot.get('synthetic',False)),coverage=dict(required_inputs='validated',market='missing' if reverse is None else 'dated_quote'),operating_forecast=rows,funding_waterfall=dict(earliest_gap_month=gap,status='unfunded' if gap is not None else 'funded_under_explicit_inputs',capacity_consequence='Deployment plan and all valuation outputs conditional on unresolved funding; no funded capacity promised' if gap is not None else 'No gap in modeled window'),valuation_curve=curve,reverse_valuation=reverse,attribution=None,traversal=None,changes_since_prior=None,unknowns=['Current reconciled CRWV balances and billable capacity not established by synthetic fixture','NVIDIA trade-in/residual guarantee not verified','GPU earning-life and scenario probabilities not calibrated','Prepayments/refunds, leases, deferred tax and convertibles require additional explicit contract support; v1 rejects declared unsupported features','Capitalized interest amortized from following month over explicit scenario life; actual asset allocation unknown'])


def analyze(snapshot, scenario_config, as_of, horizons=(3,6,12,24)):
    """Partial-output facade: missing finance inputs never suppress valid market output."""
    try:
        result=evaluate(snapshot,scenario_config,as_of,horizons)
    except (ValueError,KeyError,TypeError) as error:
        result=dict(schema='crwv.analysis@1',engine_version=VERSION,valuation_as_of=as_of,classification='blocked',input_hash=None,config_hash=None,coverage=dict(required_inputs='missing_or_invalid',reason=str(error)),operating_forecast=None,funding_waterfall=None,valuation_curve=None,reverse_valuation=None,attribution=None,traversal=None,unknowns=[str(error)])
    from market import accept_attribution,turnover
    market=snapshot.get('market_observations',{})
    for key,call in [('attribution',lambda:accept_attribution(market['attribution'],as_of)),('bars',lambda:turnover(market['bars'],as_of))]:
        if key in market:
            target='traversal' if key=='bars' else key
            try:
                result[target]=call()
            except (ValueError,KeyError,TypeError) as error:
                result[target]=dict(value=None,status='blocked',reason=str(error))
    return result
