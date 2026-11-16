'use strict';
function contextEtDay(t){
 const p=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(t);
 return ['year','month','day'].map(k=>p.find(d=>d.type===k).value).join('-');
}
function projectNestedContext(dataset,{selected,minute=false,pivotNeighbors=2,selectedRequested=null,structureFn}={}){
 if(!Array.isArray(selected)||!selected.length)throw Error('No selected backdrop for nested context.');
 if(!Number.isInteger(pivotNeighbors)||pivotNeighbors<1||pivotNeighbors>10)throw Error('Invalid structure confirmation span.');
 const asOf=selected.at(-1).t,price=selected.at(-1).c,cutoffDay=contextEtDay(asOf);
 const minuteHistory=(dataset.minute||[]).filter(r=>r.t<=asOf),dailyHistory=(dataset.daily||[]).filter(r=>r.t<=asOf&&(!minute||contextEtDay(r.t)<cutoffDay&&new Date(r.t).toISOString().slice(0,10)<cutoffDay));
 const out=[],seen=new Set();
 function add(label,history,n,grain,isSelected=false){
  const bars=history.slice(-n);if(!bars.length){out.push({label,grain,requested:n,count:0,status:'missing',selected:isSelected});return;}
  const identity=grain+':'+bars[0].t+':'+bars.at(-1).t+':'+n;
  if(seen.has(identity)){const existing=out.find(r=>r.reference===identity);if(isSelected)existing.selected=true;return;}seen.add(identity);
  const low=Math.min(...bars.map(r=>r.l)),high=Math.max(...bars.map(r=>r.h)),mid=(low+high)/2,shares=bars.reduce((s,r)=>s+r.v,0),delta=bars.at(-1).c-bars[0].o;
  const widthPct=100*(high-low)/mid,prior=history.length>=2*n?history.slice(-2*n,-n):null;
  let widthChangePct=null;if(prior){const pl=Math.min(...prior.map(r=>r.l)),ph=Math.max(...prior.map(r=>r.h)),pw=100*(ph-pl)/((ph+pl)/2);if(pw>0)widthChangePct=100*(widthPct/pw-1);}
  const structure=typeof structureFn==='function'?structureFn(bars,pivotNeighbors):null;
  const highs=structure?.pivots.filter(p=>p.kind==='high')||[],lows=structure?.pivots.filter(p=>p.kind==='low')||[];
  const structureLabel=highs.length>=2&&lows.length>=2?highs.at(-1).label+' / '+lows.at(-1).label:'insufficient confirmed pairs';
  const gaps=grain==='minute'?bars.slice(1).filter((r,i)=>r.t-bars[i].t!==60000).length:null;
  out.push({label,grain,reference:identity,selected:isSelected,requested:n,count:bars.length,status:bars.length<n?'partial':'supplied count met',from:bars[0].t,to:bars.at(-1).t,low,high,price,positionPct:high>low?100*(price-low)/(high-low):null,fromHigh:price-high,fromHighPct:100*(price/high-1),fromLow:price-low,fromLowPct:100*(price/low-1),delta,returnPct:100*(bars.at(-1).c/bars[0].o-1),velocity:delta/bars.length,shares,movePerMillion:shares>0?delta/(shares/1e6):null,widthPct,widthChangePct,structureLabel,pivotNeighbors,gaps,lagged:bars.at(-1).t<asOf});
 }
 add('Selected backdrop',minute?minuteHistory:dailyHistory,selectedRequested||selected.length,minute?'minute':'daily',true);
 if(minute){for(const n of [15,60])add(n+' minute bars',minuteHistory,n,'minute');}
 for(const n of [5,21,63,252])add(n+' daily bars',dailyHistory,n,'daily');
 return{version:'nested-context.research@1',asOf,price,rows:out,source:dataset.source||'unspecified',inputManifestHash:null,pivotNeighbors,completion:'caller-supplied; not certified',pmDailyPolicy:minute?'Both UTC and ET label dates strictly before selected minute ET date (conservative, completion not certified)':'Supplied daily labels through selected end'};
}
function renderNestedContext(container,p){
 const doc=container.ownerDocument;container.replaceChildren();const make=(tag,text,parent=container)=>{const e=doc.createElement(tag);if(text!==undefined)e.textContent=text;parent.appendChild(e);return e;};
 const signed=(n,d=2)=>n===null?'unknown':(n<0?'-':n>0?'+':'')+Math.abs(n).toFixed(d),plain=n=>n===null?'unknown':n.toFixed(2);
 const stamp=t=>new Date(t).toLocaleString('en-US',{timeZone:'America/New_York',month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'});
 const table=make('table');make('caption','Common reference $'+p.price.toFixed(2)+' · selected end '+stamp(p.asOf)+' ET',table);
 const header=make('tr',undefined,make('thead',undefined,table));
 for(const label of ['Horizon / source end','Range USD / position %','From high USD / %','From low USD / %','Window net Δ USD / %','Net speed USD / supplied bar','Shares / net USD per 1M','Width % / change %','Confirmed highs / lows','Source status'])make('th',label,header).setAttribute('scope','col');
 const body=make('tbody',undefined,table);
 for(const r of p.rows){const tr=make('tr',undefined,body);make('th',r.label+(r.selected?' · selected':''),tr).setAttribute('scope','row');
  if(!r.count){const td=make('td','Missing supplied history',tr);td.setAttribute('colspan','9');continue;}
  const th=tr.children[0];make('div',stamp(r.to)+' ET'+(r.lagged?' · earlier context':''),th);
  const values=['$'+r.low.toFixed(2)+'–'+r.high.toFixed(2)+' / '+plain(r.positionPct)+'%',signed(r.fromHigh)+' / '+signed(r.fromHighPct)+'%',signed(r.fromLow)+' / '+signed(r.fromLowPct)+'%',signed(r.delta)+' / '+signed(r.returnPct)+'%',signed(r.velocity,4)+' / '+r.grain+' bar',r.shares.toLocaleString('en-US',{maximumFractionDigits:3})+' / '+signed(r.movePerMillion,4),plain(r.widthPct)+'% / '+signed(r.widthChangePct)+'%',r.structureLabel+' · '+r.pivotNeighbors+' neighbors EACH side',r.count+'/'+r.requested+' · '+r.status+' · '+(r.gaps===null?'daily continuity unknown':r.gaps+' minute gaps')];
  for(const text of values)make('td',text,tr);
 }
 return table;
}
if(typeof module!=='undefined')module.exports={contextEtDay,projectNestedContext,renderNestedContext};
