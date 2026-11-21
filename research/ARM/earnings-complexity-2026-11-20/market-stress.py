"""Unweighted revenue-to-earnings sensitivities; not guidance or intrinsic value."""
from pathlib import Path
from datetime import date
from copy import deepcopy
import json, hashlib, csv, io

p=Path(__file__).resolve().parent
raw=(p/'market-stress-inputs.json').read_bytes(); d=json.loads(raw); a=d['common_assumptions']
years=(date.fromisoformat(d['period_end'])-date.fromisoformat(d['as_of_date'])).days/365.25

def earnings(s):
    assert s['diluted_shares_b']>0 and 0<=s['chip_gross_margin']<=1
    assert all(s[k]>=0 for k in ['ip_revenue_b','chip_revenue_b','non_sbc_opex_b','sbc_b','employer_tax_b','acquisition_b'])
    revenue=s['ip_revenue_b']+s['chip_revenue_b']
    gross=s['ip_revenue_b']*a['ip_gross_margin_before_restored_costs']+s['chip_revenue_b']*s['chip_gross_margin']
    pre_exclusions=gross-s['non_sbc_opex_b']-a['extra_development_b']
    restored=s['sbc_b']+s['employer_tax_b']+s['acquisition_b']
    pretax=pre_exclusions-restored+a['net_interest_b']+a['equity_gains_b']
    # No tax benefit assumed for a loss; these cases all have positive pretax income.
    net=pretax-max(pretax,0)*a['tax_rate']; eps=net/s['diluted_shares_b']
    adj=(pre_exclusions+a['net_interest_b']+a['equity_gains_b'])*(1-a['tax_rate'])/s['diluted_shares_b']
    future=eps*a['terminal_gaap_pe'] if eps>0 else None
    return {'id':s['id'],'label':s['label'],'ip_revenue_b':s['ip_revenue_b'],'chip_revenue_b':s['chip_revenue_b'],
      'total_revenue_b':revenue,'gross_profit_before_restored_costs_b':gross,'non_sbc_opex_b':s['non_sbc_opex_b'],
      'restored_compensation_other_b':restored,'gaap_style_pretax_b':pretax,'gaap_style_net_income_b':net,
      'adjusted_style_eps_same_assumptions':adj,'gaap_style_eps':eps,'reference_pe':d['reference_price']/eps if eps>0 else None,
      'future_price_at_30x_gaap':future,'future_price_cagr':(future/d['reference_price'])**(1/years)-1 if future else None,
      'discounted_terminal_price_at_required_return':future/(1+a['required_return'])**years if future else None,
      'classification':a['classification']}

rows=[earnings(s) for s in d['scenarios']]; base=d['scenarios'][2]; b=rows[2]
independent=((10*.99+15*.5-5.6-2.5-.3-.05)*.85)/1.2
assert abs(b['gaap_style_eps']-independent)<1e-10
assert 4<years<5 and len(rows)==4
sens=[]
for key,delta,label in [('chip_revenue_b',-5,'Chip revenue $5B lower'),('chip_gross_margin',-.10,'Chip gross margin 10 percentage points lower'),('sbc_b',1,'SBC $1B higher'),('non_sbc_opex_b',1,'Development/SG&A $1B higher')]:
    s=deepcopy(base);s[key]+=delta;e=earnings(s)['gaap_style_eps'];assert e<b['gaap_style_eps']
    sens.append({'change':label,'gaap_style_eps':e,'eps_change':e-b['gaap_style_eps']})
s=deepcopy(base);s['diluted_shares_b']*=1.05
assert abs(earnings(s)['gaap_style_eps']/b['gaap_style_eps']-1/1.05)<1e-10
sens.append({'change':'Diluted shares 5% higher','gaap_style_eps':earnings(s)['gaap_style_eps'],'eps_change':earnings(s)['gaap_style_eps']-b['gaap_style_eps']})
r={'model_version':d['model_version'],'input_sha256':hashlib.sha256(raw).hexdigest(),'years':years,'scenarios':rows,'one_variable_sensitivities':sens,
 'edge_tam_annualized_growth':1.4**.2-1,'fy28_to_fy31_chip_cagr_using_generous_2b_fy28_anchor':(15/2)**(1/3)-1,
 'gaap_eps_required_for_12pct_annual_return_at_30x':d['reference_price']*(1.12)**years/30,
 'note':'$2B is actually combined FY27–FY28 up-to revenue, not a FY28 annual forecast; assigning all to FY28 is a generous ramp illustration, not a rigorous growth bound.'}
assert r['fy28_to_fy31_chip_cagr_using_generous_2b_fy28_anchor']>.95
(p/'market-stress-results.json').write_text(json.dumps(r,indent=2)+'\n')
buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);(p/'market-stress.csv').write_text(buf.getvalue())
md=['# ARM revenue streams, market expansion and earnings stress test','','As of November 20, 2026. USD. FY2031 ends March 31, 2031. Scenario horizon about 4.36 years. Same reference close $152.20; no live quote feed.','','The growth mechanisms are identifiable; the investment question is realized profit per share after development, manufacturing, stock compensation and dilution. Consensus already includes significant expansion; undisclosed incremental upside has not been established.','','## Revenue routes and partner evidence','','| Revenue route | Economics | Partner/evidence status |','|---|---|---|']
for x in d['streams']:md.append(f"| {x['stream']} | {x['economics']} | {x['partners']} {x['status']} [{x['source']}] |")
md+=['','Latest Q2 FY2027: royalties $670M (+8%); license/other $773M (+50%). Datacenter royalties doubled and physical AI royalties grew 50%, while edge was roughly flat. Licensing is an earlier design cohort; growth will transmit only when products ship under monetizable terms. No exact segment-weighted royalty bridge is available. [results, november_call]','','## TAM and timing','','Data-center CPU opportunity: issuer estimate above $100B by 2030. The $15B FY2031 direct-chip objective would represent roughly 15% of $100B, with a fiscal/calendar timing mismatch. It is an aggressive share objective, not a royalty entitlement. Edge TAM +40% over five years is only about 7% annual growth. Physical AI compute is a management-estimated $200B annual opportunity in the 2030s, without an exact year. These measures overlap and cannot be added into Arm revenue. [long_term, physical]','','Near-term CPU outlook is up to $2B across FY2027 AND FY2028, versus $15B in FY2031 alone. Even granting all $2B to FY2028 for illustration requires about 96% annual chip growth over the following three years. Purchase orders are reported but individual order dollars, acceptance and cancellation terms are not verified. [results]','','## Emerging technologies and expansion','','CSS N4 enables configurable custom CPUs, networking, security and DPUs, with LPDDR6/PCIe Gen7 and higher memory bandwidth. The economic opportunity is richer IP content and quicker deployment, not automatic payment per core. [n4]','','Armv9, SME2, Mobile CSS 2 and new GPU IP expand on-device agent/inference capability across phones and PCs. KleidiAI and software integrations support adoption; no incremental SaaS stream is assumed. Zena CSS, safety and real-time processing support automotive and robotics; long qualification cycles and unspecified robotics volumes constrain the near-term earnings bridge. [results, physical]','','Meta confirms multigeneration CPU co-development. AWS confirms strong Graviton commitments, supporting the IP route rather than proving purchases of Arm-designed CPUs. OCI availability is planned for fall 2027. Customer-specific agreement economics remain undisclosed. Software and OEM ecosystem membership is not a chip purchase order. [meta, aws, oracle]','','## FY2031 earnings sensitivities','','Four unweighted scenarios, not consensus, company GAAP guidance or price targets. IP gross margin 99%; chip margins 35/45/50/55%. Non-SBC development/SG&A $5.6B in the first three cases and $6.3B in strong execution; SBC $2.5B/$3B plus employer payroll taxes $0.30B/$0.35B and acquisition costs $0.05B. Diluted shares 1.20B/1.25B, tax 15%, no interest or equity gains. Expenses are retained once. Manufacturing/packaging are in gross margin; ordinary R&D is in opex. [scenario assumptions]','','| Scenario | IP revenue | Chip revenue | Total revenue | GAAP-style EPS | P/E at $152.20 | March 2031 price at assumed 30x GAAP | Annual price return |','|---|---:|---:|---:|---:|---:|---:|---:|']
for x in rows:md.append(f"| {x['label']} | ${x['ip_revenue_b']:.0f}B | ${x['chip_revenue_b']:.0f}B | ${x['total_revenue_b']:.0f}B | ${x['gaap_style_eps']:.2f} | {x['reference_pe']:.1f}x | ${x['future_price_at_30x_gaap']:.0f} | {x['future_price_cagr']:.1%} |")
md+=['',f"The $25B revenue case yields ${b['adjusted_style_eps_same_assumptions']:.2f} adjusted-style EPS and ${b['gaap_style_eps']:.2f} after restored costs under these assumptions. It is not a reconstruction of the issuer >$9 adjusted EPS target or the $10.40 vendor forecast. Those require different margins, costs, taxes, revenue or shares. At 30x GAAP EPS, a 12% annual price-return hurdle requires about ${r['gaap_eps_required_for_12pct_annual_return_at_30x']:.2f} FY2031 EPS.",'','## One-variable stress versus the $25B revenue case','','| Change | GAAP-style EPS | EPS difference |','|---|---:|---:|']
for x in sens:md.append(f"| {x['change']} | ${x['gaap_style_eps']:.2f} | ${x['eps_change']:.2f} |")
md+=['','## What would strengthen or weaken the case','','Strengthen: commercial deliveries in January–March 2027; accepted and recognized silicon revenue, expanding customer breadth; sustained growth in absolute datacenter royalties; chip gross margin rising on later generations; total recurring costs and diluted shares growing slower than gross profit.','','Weaken: design/licensing growth without royalty conversion; chip revenue below the outlook; first-generation margins persisting; higher R&D/SBC; more customer overlap/cannibalization; supply or qualification delays. x86 and RISC-V remain competitive alternatives; customers also build their own chips. [annual]','','The same partner can buy IP, use cloud instances and co-develop silicon; do not count its spending three times. Hardware mix lowers consolidated percentage gross margin but can still add profit dollars. Capital expenditure, purchase commitments, working capital, net cash and one-off tax effects remain outside this earnings model. SBC is noncash expense, not equal cash paid out; dilution is separately modeled without a second buyback charge.','','## Sources']
for k,v in d['sources'].items():md.append(f"- {k}: {v['url']} ({v['class']}, available date {v['available_date']})")
md+=['','Unknowns:']+['- '+x for x in d['unknowns']]
(p/'MARKET_STRESS.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'scenario_eps':[round(x['gaap_style_eps'],3) for x in rows],'required_eps':r['gaap_eps_required_for_12pct_annual_return_at_30x'],'sensitivities':sens},indent=2))
