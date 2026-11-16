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
function initializeDensityPresentation(){
 const root=document.getElementById('battle-presentation');if(!root)return;let dataset=null,offset=0;
 const file=root.querySelector('#data-file'),model=root.querySelector('#model'),win=root.querySelector('#window'),back=root.querySelector('#earlier'),next=root.querySelector('#later'),svg=root.querySelector('#plot'),structure=root.querySelector('#structure');
 const functions={rails:drawVolumeRails,ribbons:drawRollingRibbons,threads:drawRevisitThreads,heatmap:drawDensityHeatmap,nested:drawNestedProfiles};
 const descriptions={rails:'Full-window profile; rail thickness and opacity encode allocated shares.',ribbons:'Central 60% / 20% weighted price bands in equal observation-count slices. Retrospective distribution, not a confidence interval.',threads:'Sampled visit nodes; node area grows with volume. Dotted connectors mark returns, not intervening occupancy.',heatmap:'Time-by-price cells; intensity compares allocated shares within the selected backdrop.',nested:'Full / recent / shortest profile shapes; each width normalized to its own largest band, not comparable absolute volume.'};
 const fmt=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'});
 function draw(){if(!dataset)return;const data=selectDensityWindow(dataset,win.value,offset);if(!data.length){root.querySelector('#detail').textContent='No observations for this backdrop.';svg.replaceChildren();back.disabled=next.disabled=true;return;}
  const pm=win.value==='pm',end=dataset.daily.length-offset,count=Number(win.value);back.disabled=pm||end<=count;next.disabled=pm||offset===0;
  const width=Math.max(280,root.getBoundingClientRect().width),height=width<450?320:340;const result=functions[model.value](svg,data,width,height);
  root.querySelector('#model-title').textContent=dataset.ticker+' · '+model.options[model.selectedIndex].text;
  root.querySelector('#dates').textContent=fmt.format(data[0].t)+' – '+fmt.format(data.at(-1).t)+' ET · '+data.length+' supplied '+(pm?'minute':'daily')+' bars';
  const total=data.reduce((s,d)=>s+d.v,0),bad=data.filter(d=>!Number.isFinite(d.vw)||d.vw<d.l||d.vw>d.h).reduce((s,d)=>s+d.v,0);
  root.querySelector('#detail').textContent=(total/1e6).toFixed(2)+'M shares · '+(bad/1e6).toFixed(2)+'M unallocated · source: '+dataset.source;
  root.querySelector('#method').textContent=descriptions[model.value];
  if(structure.checked)drawSwingOverlay(svg,data,densitySwingStructure(data),result.scale);
 }
 file.addEventListener('change',async()=>{const chosen=file.files[0];if(!chosen)return;try{if(chosen.size>5000000)throw Error('Input exceeds 5 MB.');const candidate=qualifyDensityDataset(JSON.parse(await chosen.text()));dataset=candidate;offset=0;win.querySelector('[value="pm"]').disabled=!dataset.minute.length;if(!dataset.daily.length)win.value='pm';else if(win.value==='pm'&&!dataset.minute.length)win.value='21';root.querySelector('#error').textContent='';draw();}catch(e){dataset=null;svg.replaceChildren();back.disabled=next.disabled=true;root.querySelector('#model-title').textContent='No qualified data loaded';root.querySelector('#dates').textContent='';root.querySelector('#detail').textContent='';root.querySelector('#method').textContent='';root.querySelector('#error').textContent=e.message;}});
 model.addEventListener('change',draw);structure.addEventListener('change',draw);win.addEventListener('change',()=>{offset=0;draw();});back.addEventListener('click',()=>{offset+=Number(win.value);draw();});next.addEventListener('click',()=>{offset=Math.max(0,offset-Number(win.value));draw();});new ResizeObserver(draw).observe(root);
}
function drawSwingOverlay(svg,rows,state,scale){
 const ns='http://www.w3.org/2000/svg',frame=svg.querySelector('[data-chart-frame]');if(!frame)return;
 if(!scale)return;const xs=rows.map(r=>scale.x(r.t)),Y=scale.y;
 const top=+frame.getAttribute('y'),bottom=top+(+frame.getAttribute('height'));
 const append=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(text)e.textContent=text;svg.appendChild(e);};
 const fmt=t=>new Date(t).toLocaleString('en-US',{timeZone:'America/New_York'});
 // Last six confirmed pivots avoid dense unreadable labels on long backdrops.
 for(const p of state.pivots.slice(-6)){const xx=xs[p.knownIndex],yy=Math.max(top+12,Math.min(bottom-12,Y(p.price))),labelY=Math.max(top+12,Math.min(bottom-4,yy+(p.kind==='high'?-9:17)));
  append('circle',{cx:xx,cy:yy,r:4,fill:'var(--viz-series-4)','data-tooltip':`${p.label} $${p.price.toFixed(2)}; pivot ${fmt(p.pivotAt)}; confirmed ${fmt(p.knownAt)} ET`});append('text',{x:xx,y:labelY,'text-anchor':p.knownIndex>rows.length*.85?'end':'middle',fill:'var(--foreground)','font-size':12},p.label);
 }
 for(const b of state.breaks.slice(-2)){const xx=xs[b.knownIndex],yy=Y(b.price);append('circle',{cx:xx,cy:yy,r:7,fill:'none',stroke:'var(--viz-series-3)','stroke-width':2,'data-tooltip':`${b.label} at ${fmt(b.knownAt)} ET; close crossed $${b.reference.toFixed(2)}. Not a forecast.`});}
}
if(typeof module!=='undefined')module.exports={qualifyDensityDataset,selectDensityWindow,densitySwingStructure};
if(typeof document!=='undefined')initializeDensityPresentation();
