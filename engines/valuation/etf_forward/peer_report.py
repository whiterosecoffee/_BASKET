"""Markdown view over the versioned SMH/SOXX forward-comparison result."""

def render_peer_markdown(result):
    if result.get('schema') != 'basket.etf_peer_comparison_output@1':
        raise ValueError('unsupported result contract')
    if result.get('data_kind') not in ('synthetic_test','verified_observation'):
        raise ValueError('evidence kind missing')
    lines=['# SMH versus SOXX — forward valuation comparison', '',
           '**Evidence kind:** '+result['data_kind'],
           '**As of:** '+result['as_of'],
           '**Holdings effective date:** '+result['holdings_effective_date'],
           '**Market-cap snapshot:** '+result['equity_market_cap_as_of'], '',
           '| Calendar year | SMH P/E | SOXX P/E | SMH earnings yield | SOXX earnings yield | SMH coverage | SOXX coverage | Status |',
           '|---|---:|---:|---:|---:|---:|---:|---|']
    for year in ('2027','2028'):
        value=result['years'][year]
        def show(x): return str(x) if x is not None else 'N/M'
        def pct(x): return (f'{float(x)*100:.2f}%' if x is not None else 'N/A')
        pe=value['forward_pe']; ey=value['earnings_yield']; cov=value['equity_estimate_coverage']
        lines.append(f"| {year} | {show(pe['SMH'])} | {show(pe['SOXX'])} | {pct(ey['SMH'])} | {pct(ey['SOXX'])} | {pct(cov['SMH'])} | {pct(cov['SOXX'])} | {value['status']} |")
    lines.extend(['', '**No risk-adjusted winner established.**', '', result['disclosure'],
                  '', 'Source input SHA-256: `'+result['input_sha256']+'`'])
    if result['data_kind']=='synthetic_test':
        lines.insert(2, '**SYNTHETIC TEST DATA — NOT OBSERVED ETF FUNDAMENTALS**')
    return '\n'.join(lines)+'\n'
