"""CRWV research-only walk-forward attribution. Requires numpy. No live ingestion."""
import csv,json,sys,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent

def run(path):
    rows=list(csv.DictReader(Path(path).open()))
    names=['CRWV','QQQ','NVDA','HYG','IEF','USO']
    assert len({r['date'] for r in rows})==len(rows)
    assert [r['date'] for r in rows]==sorted(r['date'] for r in rows)
    prices=np.array([[float(r[k]) for k in names] for r in rows])
    assert np.isfinite(prices).all() and (prices>0).all()
    returns=prices[1:]/prices[:-1]-1
    dates=[r['date'] for r in rows[1:]]
    models={}
    for label,cols in [('market',[1]),('market_ai',[1,2]),('five_factor',[1,2,3,4,5])]:
        records=[]
        for t in range(60,len(returns)):
            train=returns[t-60:t]
            x=train[:,cols]; y=train[:,0]
            mu=x.mean(0); sd=x.std(0,ddof=1)
            assert (sd>0).all()
            z=(x-mu)/sd
            design=np.column_stack([np.ones(60),z])
            coef,_,rank,_=np.linalg.lstsq(design,y,rcond=None)
            assert rank==len(cols)+1
            beta=coef[1:]/sd; intercept=coef[0]-mu@beta
            contributions=returns[t,cols]*beta
            predicted=intercept+sum(contributions)
            fit=design@coef; errors=y-fit
            residual=returns[t,0]-predicted
            error_sd=float(np.sqrt(sum(errors**2)/(60-len(cols)-1)))
            records.append({'date':dates[t],'trained_through':dates[t-1],
              'actual_return':float(returns[t,0]),'expected_conditional_return':float(predicted),
              'residual':float(residual),'residual_training_sigma':float(residual/error_sd),
              'intercept':float(intercept),'betas':dict(zip([names[i] for i in cols],map(float,beta))),
              'standardized_effect_per_one_factor_sd':dict(zip([names[i] for i in cols],map(float,coef[1:]))),
              'contributions':dict(zip([names[i] for i in cols],map(float,contributions))),
              'training_r2':float(1-sum(errors**2)/sum((y-y.mean())**2)),
              'standardized_design_condition_number':float(np.linalg.cond(design))})
            assert records[-1]['trained_through']<records[-1]['date']
            assert abs(intercept+sum(contributions)+residual-returns[t,0])<1e-10
        errors=np.array([r['residual'] for r in records]); actual=np.array([r['actual_return'] for r in records])
        models[label]={'walk_forward_n':len(records),'rmse':float(np.sqrt(np.mean(errors**2))),
          'zero_return_baseline_rmse':float(np.sqrt(np.mean(actual**2))),
          'latest':records[-1],'history':records}
    return {'schema':'crwv.factor-research@1','as_of':dates[-1],'currency':'USD',
      'source':'Massive daily aggregates retrieved 2026-10-23; split-adjusted price closes, not dividend-adjusted total returns',
      'input_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
      'window':60,'method':'OLS fitted only to preceding 60 daily returns; same-day factors explain same-day CRWV return ex post',
      'limitations':['QQQ and NVDA overlap; coefficients conditional and unstable, not causal portfolio weights',
      'HYG is not a pure credit-spread series; IEF is not SOFR; USO is not Brent spot',
      'Residual is unexplained return, not proof of company news or mispricing',
      'No live worker, scheduled refresh or continuous monitoring is deployed',
      'Exploratory comparison without held-out model-selection test; ETF ex-dividend effects remain'],
      'models':models}
if __name__=='__main__':
    path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'factor-closes-2026-10-22.csv'
    out=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'factor-attribution-2026-10-22.json'
    result=run(path)
    # Prefix replay: future observations must not alter earlier predictions.
    rows=list(csv.DictReader(path.open())); tmp=ROOT/'_prefix_test.csv'
    try:
        with tmp.open('w') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows[:-5])
        earlier=run(tmp)
        for k in result['models']:
            assert earlier['models'][k]['latest']==result['models'][k]['history'][-6]
    finally: tmp.unlink(missing_ok=True)
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:{'rmse':v['rmse'],'baseline':v['zero_return_baseline_rmse'],'latest':v['latest']} for k,v in result['models'].items()},indent=2))
