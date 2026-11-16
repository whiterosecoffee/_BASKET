'use strict';
function qualifyDensityDataset(input) {
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Expected an observation-view object.');
 const out={ticker:typeof input.ticker==='string'?input.ticker:'Supplied instrument',source:typeof input.source==='string'?input.source:'Source unspecified'};
 for(const key of ['daily','minute']){
  const rows=input[key]===undefined?[]:input[key];if(!Array.isArray(rows)||rows.length>10000)throw Error(key+': expected at most 10,000 bars.');
  let prior=-Infinity;out[key]=rows.map(d=>{
   if(!d||!['t','o','h','l','c','v'].every(k=>typeof d[k]==='number'&&Number.isFinite(d[k])))throw Error(key+': nonnumeric observation.');
   if(!Number.isSafeInteger(d.t)||d.t<0||d.t<=prior)throw Error(key+': duplicate or unordered timestamp.');
   if(key==='minute'&&d.t%60000!==0)throw Error('Minute timestamp is not aligned.');
   if(d.l<=0||d.h<d.l||d.o<d.l||d.o>d.h||d.c<d.l||d.c>d.h||d.v<0)throw Error(key+': invalid OHLC or volume.');
   if(d.vw!==null&&d.vw!==undefined&&(typeof d.vw!=='number'||!Number.isFinite(d.vw)))throw Error(key+': invalid VWAP type.');
   prior=d.t;return{t:d.t,o:d.o,h:d.h,l:d.l,c:d.c,v:d.v,vw:d.vw??null};
  });
 }
 if(!out.daily.length&&!out.minute.length)throw Error('No observations supplied.');return out;
}
function selectDensityWindow(dataset,windowSize,offset=0){
 if(windowSize==='pm')return dataset.minute.slice();const count=Number(windowSize);
 if(!Number.isInteger(count)||count<1||!Number.isInteger(offset)||offset<0)throw Error('Invalid backdrop selection.');
 const end=Math.max(0,dataset.daily.length-offset);return dataset.daily.slice(Math.max(0,end-count),end);
}
function densitySwingStructure(rows,k=2){
 if(!Number.isInteger(k)||k<1)throw Error('Invalid pivot confirmation span.');
 const pivots=[],breaks=[];let lastHigh=null,lastLow=null,trend='unknown',broken=new Set();
 for(let known=0;known<rows.length;known++){
  const i=known-k;if(i>=k){const c=rows[i],neighbors=rows.slice(i-k,i+k+1).filter((_,j)=>j!==k);
   const high=neighbors.every(r=>c.h>r.h),low=neighbors.every(r=>c.l<r.l);
   // Both extremes in one candle have unknowable intrabar order.
   if(high&&low){pivots.push({kind:'ambiguous',label:'?',pivotIndex:i,knownIndex:known,price:c.c,pivotAt:c.t,knownAt:rows[known].t});}
   else if(high||low){const previous=high?lastHigh:lastLow;const price=high?c.h:c.l;
    const label=previous?(high?(price>previous.price?'HH':price<previous.price?'LH':'EH'):(price>previous.price?'HL':price<previous.price?'LL':'EL')):(high?'H':'L');
    const p={kind:high?'high':'low',label,price,pivotIndex:i,knownIndex:known,pivotAt:c.t,knownAt:rows[known].t};pivots.push(p);if(high)lastHigh=p;else lastLow=p;
    if(lastHigh&&lastLow){if(lastHigh.label==='LH'&&lastLow.label==='LL')trend='down';else if(lastHigh.label==='HH'&&lastLow.label==='HL')trend='up';}
   }
  }
  const r=rows[known];if(trend==='down'&&lastHigh&&r.c>lastHigh.price&&!broken.has(lastHigh.pivotAt+'up')){breaks.push({direction:'up',knownIndex:known,knownAt:r.t,price:r.c,reference:lastHigh.price,label:'Upturn candidate'});broken.add(lastHigh.pivotAt+'up');trend='unknown';}
  else if(trend==='up'&&lastLow&&r.c<lastLow.price&&!broken.has(lastLow.pivotAt+'down')){breaks.push({direction:'down',knownIndex:known,knownAt:r.t,price:r.c,reference:lastLow.price,label:'Downturn candidate'});broken.add(lastLow.pivotAt+'down');trend='unknown';}
 }
 return{pivots,breaks,trend,confirmationBars:k};
}
function densityMultiTrends(rows,spans=[5,15,45]){
 const models=spans.map(span=>{
  if(!Number.isInteger(span)||span<2)throw Error('Invalid trend span.');
  const points=[];let seed=0,ema=null,lastDirection=null;
  for(let i=0;i<rows.length;i++){
   const r=rows[i];seed+=r.c;
   if(i<span-1)continue;
   const previous=ema;ema=ema===null?seed/span:ema+(2/(span+1))*(r.c-ema);
   const delta=previous===null?null:ema-previous;
   const direction=delta===null?'unknown':Math.abs(delta)<1e-10?'flat':delta>0?'up':'down';
   const turn=(direction==='up'||direction==='down')&&lastDirection&&direction!==lastDirection?lastDirection+'_to_'+direction:null;
   points.push({t:r.t,index:i,value:ema,direction,change:delta,knownAt:r.t,turn});
   if(direction==='up'||direction==='down')lastDirection=direction;
  }
  return{span,points,latest:points.at(-1)?.direction??'insufficient'};
 });
 return{models,method:'past-only EMA seeded with first span closes; direction is EMA change per supplied bar; no future observations'};
}
function densityDetailControl(model,overlay){
 const labels={compression:'Range lookback',swings:'Pivot neighbors on EACH side',movement:'Completed movement block'};
 return{label:labels[model]||'EMA smoothing span',enabled:Boolean(labels[model]||overlay)};
}
function initializeDensityPresentation(){
 const root=document.getElementById('battle-presentation');if(!root)return;let dataset=null,offset=0,selectedZone=null;
 const file=root.querySelector('#data-file'),model=root.querySelector('#model'),win=root.querySelector('#window'),back=root.querySelector('#earlier'),next=root.querySelector('#later'),svg=root.querySelector('#plot'),structure=root.querySelector('#structure'),granularity=root.querySelector('#granularity'),slices=root.querySelector('#slices');
 const functions={rails:drawVolumeRails,ribbons:drawRollingRibbons,threads:drawRevisitThreads,heatmap:drawDensityHeatmap,nested:drawNestedProfiles,compression:drawCompressionExpansion,swings:drawSwingStructure,movement:drawMovementPerShares};
 const descriptions={rails:'Full-window profile; rail thickness and opacity encode allocated shares.',ribbons:'Central 60% / 20% weighted price bands in equal observation-count slices. Retrospective distribution, not a confidence interval.',threads:'Sampled visit nodes; node size grows with volume. Dotted connectors mark returns, not intervening occupancy.',heatmap:'Time-by-price cells; intensity compares allocated shares within the selected backdrop.',nested:'Full / recent / shortest profile shapes; each width normalized to its own largest band, not comparable absolute volume.',compression:'Envelope width measures range compression/expansion, separate from price direction. Compare the selected bar span with the preceding disjoint equal-span window. No breakout forecast.'};
 const fmt=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'});
 function draw(){if(!dataset)return;const data=selectDensityWindow(dataset,win.value,offset);if(!data.length){root.querySelector('#detail').textContent='No observations for this backdrop.';svg.replaceChildren();back.disabled=next.disabled=true;return;}
  const pm=win.value==='pm',end=dataset.daily.length-offset,count=Number(win.value);back.disabled=pm||end<=count;next.disabled=pm||offset===0;
  const separate=model.value==='swings'||model.value==='movement';structure.disabled=separate;
  const width=Math.max(280,root.getBoundingClientRect().width),height=model.value==='movement'?430:width<450?320:340;svg.style.height=height+'px';const history=pm?dataset.minute:dataset.daily.slice(0,end),span=Number(granularity.value);const result=functions[model.value](svg,data,width,height,{span,history,sliceCount:Number(slices.value),structure:model.value==='swings'?densitySwingStructure(history,span):undefined});
  root.querySelector('#model-title').textContent=dataset.ticker+' · '+model.options[model.selectedIndex].text;
  root.querySelector('#dates').textContent=fmt.format(data[0].t)+' – '+fmt.format(data.at(-1).t)+' ET · '+data.length+' supplied '+(pm?'minute':'daily')+' bars';
  const total=data.reduce((s,d)=>s+d.v,0),bad=data.filter(d=>!Number.isFinite(d.vw)||d.vw<d.l||d.vw>d.h).reduce((s,d)=>s+d.v,0);
  root.querySelector('#detail').textContent=(total/1e6).toFixed(2)+'M shares · '+(bad/1e6).toFixed(2)+'M unallocated · source: '+dataset.source;
  root.querySelector('#method').textContent=descriptions[model.value]||'';
  if(model.value==='compression'){const p=result.latest;root.querySelector('#method').textContent+=p?` Latest ${p.phase}: width $${p.width.toFixed(2)} (${p.widthPct.toFixed(2)}% of midpoint); change ${p.widthChangePct===null?'unavailable':(p.widthChangePct>=0?'+':'')+p.widthChangePct.toFixed(1)+'%'}; shares ${p.volumeRatio===null?'unavailable':p.volumeRatio.toFixed(2)+'×'} prior window.`:' Insufficient warmup for this range span.';}
  if(model.value==='swings')root.querySelector('#method').textContent=`Separate structure only: no trading-price line or EMA overlay. ${span} bars either side confirm a pivot; connected highs/lows are placed at first confirmation time. ${result.pivots.length} confirmed visible pivots. With too few pivots, reduce the detail window.`;
  if(model.value==='movement'){const b=result.latest;root.querySelector('#method').textContent=b?`${span}-bar completed blocks · latest ${b.reversal?'block-direction switch':b.phase} ${b.direction} · net Δ$${b.delta.toFixed(3)} / ${(b.shares/1e6).toFixed(3)}M shares = ${b.movePerMillion===null?'unknown':b.movePerMillion.toFixed(3)} USD/1M shares · velocity ${b.velocity.toFixed(4)} USD/bar · acceleration ${b.acceleration===null?'unknown':b.acceleration.toFixed(5)} USD/bar². ◆ completed-block direction switch; ○ price speed increasing in the same direction. ${result.unclosedBars} incomplete trailing bars omitted. Not signed flow or causal price impact.`:'Insufficient completed blocks. Choose a smaller detail window.';}
  const trends=densityMultiTrends(pm?dataset.minute:dataset.daily.slice(0,end),[Number(granularity.value)]);
  const control=densityDetailControl(model.value,structure.checked);
  granularity.disabled=!control.enabled;granularity.setAttribute('aria-label',control.label);root.querySelector('#granularity-label').textContent=control.label;root.querySelector('#granularity-value').textContent=granularity.value+' supplied bars';
  slices.disabled=model.value!=='ribbons'&&model.value!=='heatmap';
  if(!slices.disabled)root.querySelector('#method').textContent+=` ${Number(slices.value)} requested slices (${Math.min(Number(slices.value),data.length)} with this input); fixed across screen sizes. `+(model.value==='ribbons'?'Equal observation-count slices.':'Equal elapsed-axis slices; not equal shares.');
  root.querySelector('#trend-state').textContent=structure.checked&&!separate?trendStateText(trends,data[0].t):'';
  if(structure.checked&&!separate)drawSwingOverlay(svg,data,trends,result.scale);
  const matrix=root.querySelector('#zone-matrix'),summary=root.querySelector('#zone-summary'),selection=root.querySelector('#zone-selection');
  try{
   const zoneWidth=Number(root.querySelector('#zone-width').value),projection=projectZoneParticipation(data,{width:zoneWidth,blocks:Number(root.querySelector('#zone-blocks').value),cadenceMs:pm?60000:null});
   renderZoneParticipation(matrix,projection,{mode:root.querySelector('#zone-mode').value,selected:selectedZone,onSelect:key=>{selectedZone=selectedZone===key?null:key;draw();}});
   summary.textContent=`${projection.zones.length} occupied zones · ${(projection.total/1e6).toFixed(3)}M total shares · ${(projection.unallocated/1e6).toFixed(3)}M unallocated · ${projection.discontinuities} detected minute discontinuities · coverage not certified.`;
   const z=projection.zones.find(z=>z.key===selectedZone),reference=selectedZone===null?null:{low:selectedZone*zoneWidth,high:(selectedZone+1)*zoneWidth};
   const visible=highlightParticipationZone(svg,result.scale,reference);
   selection.textContent=reference?`Selected $${reference.low.toFixed(2)}–$${reference.high.toFixed(2)} · `+(z?`${z.shares.toLocaleString('en-US',{maximumFractionDigits:3})} shares · ${z.episodes} sampled episodes · last sample ${fmt.format(z.lastAt)} ET.`:'No qualified samples in this backdrop.')+(visible?'':' Outside the visible price axis.'):'Select a zone row to inspect its price interval.';
  }catch(e){matrix.replaceChildren();summary.textContent=e.message;selection.textContent='';}

 }
 file.addEventListener('change',async()=>{const chosen=file.files[0];if(!chosen)return;try{if(chosen.size>5000000)throw Error('Input exceeds 5 MB.');const candidate=qualifyDensityDataset(JSON.parse(await chosen.text()));dataset=candidate;offset=0;selectedZone=null;win.querySelector('[value="pm"]').disabled=!dataset.minute.length;if(!dataset.daily.length)win.value='pm';else if(win.value==='pm'&&!dataset.minute.length)win.value='21';root.querySelector('#error').textContent='';draw();}catch(e){dataset=null;svg.replaceChildren();root.querySelector('#zone-matrix').replaceChildren();root.querySelector('#zone-summary').textContent='No qualified data loaded.';root.querySelector('#zone-selection').textContent='';back.disabled=next.disabled=true;root.querySelector('#model-title').textContent='No qualified data loaded';root.querySelector('#dates').textContent='';root.querySelector('#detail').textContent='';root.querySelector('#method').textContent='';root.querySelector('#error').textContent=e.message;}});
 root.querySelector('#zone-width').addEventListener('change',()=>{selectedZone=null;draw();});root.querySelector('#zone-blocks').addEventListener('change',draw);root.querySelector('#zone-mode').addEventListener('change',draw);
 model.addEventListener('change',draw);structure.addEventListener('change',draw);slices.addEventListener('change',draw);granularity.addEventListener('input',()=>{root.querySelector('#granularity-value').textContent=granularity.value+' bars';draw();});win.addEventListener('change',()=>{offset=0;draw();});back.addEventListener('click',()=>{offset+=Number(win.value);draw();});next.addEventListener('click',()=>{offset=Math.max(0,offset-Number(win.value));draw();});new ResizeObserver(draw).observe(root);
}
function trendStateText(state,visibleStart=-Infinity){
 const symbols={up:'↑',down:'↓',flat:'→',unknown:'warming',insufficient:'insufficient'};
 return state.models.map(m=>{const turn=m.points.filter(p=>p.turn).at(-1);return `${m.span}-bar EMA slope ${symbols[m.latest]}`+(turn?` · latest slope turn ${turn.t<visibleStart?'[before visible window] ':''}${turn.direction==='up'?'↑':'↓'} ${new Date(turn.t).toLocaleString('en-US',{timeZone:'America/New_York'})} ET`:' · no slope turn observed');}).join(' · ');
}
function drawSwingOverlay(svg,rows,state,scale){
 const ns='http://www.w3.org/2000/svg',frame=svg.querySelector('[data-chart-frame]');if(!frame)return;
 if(!scale||!rows.length)return;
 const make=(tag,attrs,parent=svg)=>{const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));parent.appendChild(e);return e;};
 const clipId=(svg.id||'density')+'-trend-clip',defs=make('defs',{}),clip=make('clipPath',{id:clipId},defs);
 make('rect',{x:frame.getAttribute('x'),y:frame.getAttribute('y'),width:frame.getAttribute('width'),height:frame.getAttribute('height')},clip);
 const group=make('g',{'clip-path':`url(#${clipId})`,'data-trend-overlay':''});
 // Exactly one selected granularity is displayed; reversals are the emphasis.
 state.models.slice(0,1).forEach(m=>{
  const points=m.points.filter(p=>p.t>=rows[0].t&&p.t<=rows.at(-1).t),width=2.6;
  for(let i=1;i<points.length;i++){
   const a=points[i-1],b=points[i],color=b.direction==='up'?'var(--green)':b.direction==='down'?'var(--red)':'var(--foreground)';
   make('line',{x1:scale.x(a.t),y1:scale.y(a.value),x2:scale.x(b.t),y2:scale.y(b.value),stroke:color,'stroke-width':width,'stroke-opacity':.95,'stroke-dasharray':b.direction==='flat'?'2 3':'none','data-trend-scale':m.span,'data-direction':b.direction,'data-tooltip':`${m.span}-bar smoothed trend ${b.direction}; $${b.value.toFixed(2)} at ${new Date(b.t).toLocaleString('en-US',{timeZone:'America/New_York'})} ET. Descriptive slope, not a forecast.`},group);
  }
  for(const b of points.filter(p=>p.turn).slice(-6)){const x=scale.x(b.t),y=scale.y(b.value),color=b.direction==='up'?'var(--green)':'var(--red)';make('polygon',{points:`${x},${y-6} ${x+5},${y} ${x},${y+6} ${x-5},${y}`,fill:color,'data-trend-turn':m.span,'data-tooltip':`${b.turn.replaceAll('_',' ')} · ${m.span}-bar trend · completion-bar label ${new Date(b.t).toLocaleString('en-US',{timeZone:'America/New_York'})} ET · smoothed value $${b.value.toFixed(2)}. A slope reversal, not a guaranteed price reversal.`},group);}
 });
}
if(typeof module!=='undefined')module.exports={qualifyDensityDataset,selectDensityWindow,densitySwingStructure,densityMultiTrends,densityDetailControl,trendStateText,drawSwingOverlay};
if(typeof document!=='undefined')initializeDensityPresentation();
