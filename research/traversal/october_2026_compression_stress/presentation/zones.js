'use strict';
// Research-only projection. No inferred intrabar paths, dwell time or trade signs.
function projectZoneParticipation(rows,{width=2,blocks=4,cadenceMs=null}={}){
 if(!Number.isFinite(width)||width<.01||width>10000)throw Error('Invalid fixed USD zone width.');
 if(!Number.isInteger(blocks)||blocks<1||blocks>8)throw Error('Invalid time-block count.');
 if(cadenceMs!==null&&(!Number.isFinite(cadenceMs)||cadenceMs<=0))throw Error('Invalid expected cadence.');
 const count=Math.min(blocks,rows.length),parts=Array.from({length:count},(_,i)=>{const a=Math.floor(i*rows.length/count),b=Math.floor((i+1)*rows.length/count);return{from:rows[a].t,to:rows[b-1].t,samples:b-a,total:0,unallocated:0,invalidSamples:0};});
 const zones=new Map();let total=0,unallocated=0,invalidSamples=0,discontinuities=0,previous=null,priorKey=null;
 for(let i=0;i<rows.length;i++){
  const r=rows[i];if(!Number.isFinite(r.t)||!Number.isFinite(r.v)||r.v<0||(previous&&r.t<=previous.t))throw Error('Invalid or unordered zone input.');
  const partIndex=Math.min(count-1,Math.ceil((i+1)*count/rows.length)-1),part=parts[partIndex];
  total+=r.v;part.total+=r.v;
  const gap=previous&&cadenceMs!==null&&r.t-previous.t!==cadenceMs;
  if(gap){discontinuities++;priorKey=null;}
  const valid=Number.isFinite(r.vw)&&Number.isFinite(r.l)&&Number.isFinite(r.h)&&r.vw>=r.l&&r.vw<=r.h;
  if(!valid){unallocated+=r.v;invalidSamples++;part.unallocated+=r.v;part.invalidSamples++;priorKey=null;previous=r;continue;}
  // Zero-origin grid persists across backdrops. Epsilon resolves binary boundary noise only.
  const ratio=r.vw/width,key=Math.floor(ratio+Number.EPSILON*Math.max(1,Math.abs(ratio))*4);
  if(!Number.isSafeInteger(key))throw Error('Zone index outside safe precision.');
  if(!zones.has(key)){if(zones.size>=200)throw Error('More than 200 occupied zones; choose a wider zone.');zones.set(key,{key,low:key*width,high:(key+1)*width,shares:0,samples:0,episodes:0,lastAt:r.t,cells:Array.from({length:count},()=>({shares:0,samples:0}))});}
  const z=zones.get(key);z.shares+=r.v;z.samples++;z.lastAt=r.t;z.cells[partIndex].shares+=r.v;z.cells[partIndex].samples++;if(priorKey!==key)z.episodes++;
  priorKey=key;previous=r;
 }
 const pct=(a,b)=>b>0?100*a/b:null;
 for(const z of zones.values()){
  z.sharePct=pct(z.shares,total);z.samplePct=pct(z.samples,rows.length);
  z.cells.forEach((c,i)=>{c.sharePct=pct(c.shares,parts[i].total);c.samplePct=pct(c.samples,parts[i].samples);});
 }
 return{version:'zone-participation.research@1',width,origin:0,parts,zones:[...zones.values()].sort((a,b)=>b.key-a.key),total,unallocated,invalidSamples,samples:rows.length,discontinuities,cadenceMs,coverage:'not certified',unallocatedPct:pct(unallocated,total)};
}
function renderZoneParticipation(container,projection,{mode='shares',selected=null,onSelect=()=>{}}={}){
 const doc=container.ownerDocument;container.replaceChildren();
 const make=(tag,text,parent=container)=>{const n=doc.createElement(tag);if(text!==undefined)n.textContent=text;parent.appendChild(n);return n;};
 const pct=n=>n===null?'unknown':n.toFixed(1)+'%',shares=n=>n.toLocaleString('en-US',{maximumFractionDigits:3});
 const table=make('table'),caption=make('caption','Fixed USD zones · [low, high) · whole-bar VWAP allocation estimate',table),head=make('thead',undefined,table),header=make('tr',undefined,head);
 const fmt=t=>new Date(t).toLocaleString('en-US',{timeZone:'America/New_York',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
 for(const label of ['USD zone','Shares · window %','Samples · window %','Episodes',...projection.parts.map(p=>fmt(p.from)+' – '+fmt(p.to)+' ET')])make('th',label,header).setAttribute('scope','col');
 const body=make('tbody',undefined,table);
 for(const z of projection.zones){
  const tr=make('tr',undefined,body);tr.setAttribute('data-zone-row',z.key);
  const th=make('th',undefined,tr);th.setAttribute('scope','row');const button=make('button','$'+z.low.toFixed(2)+'–'+z.high.toFixed(2),th);button.setAttribute('type','button');button.setAttribute('aria-pressed',String(selected===z.key));button.addEventListener('click',()=>onSelect(z.key));
  make('td',shares(z.shares)+' · '+pct(z.sharePct),tr);make('td',z.samples+' · '+pct(z.samplePct),tr);make('td',String(z.episodes),tr);
  z.cells.forEach(c=>make('td',mode==='share'?pct(c.sharePct):mode==='samples'?c.samples+' · '+pct(c.samplePct):shares(c.shares),tr));
 }
 const tr=make('tr',undefined,body);make('th','Unallocated',tr).setAttribute('scope','row');make('td',shares(projection.unallocated)+' · '+pct(projection.unallocatedPct),tr);make('td',String(projection.invalidSamples),tr);make('td','—',tr);
 projection.parts.forEach(p=>make('td',mode==='share'?pct(p.total>0?100*p.unallocated/p.total:null):mode==='samples'?String(p.invalidSamples):shares(p.unallocated),tr));
 const foot=make('tfoot',undefined,table),totals=make('tr',undefined,foot);make('th','Total',totals).setAttribute('scope','row');make('td',shares(projection.total),totals);make('td',String(projection.samples),totals);make('td','—',totals);
 projection.parts.forEach(p=>make('td',mode==='shares'?shares(p.total):mode==='samples'?String(p.samples):p.total>0?'100.0%':'unknown',totals));
 return{table,caption};
}
function highlightParticipationZone(svg,scale,zone){
 const old=svg.querySelector('[data-zone-highlight]');if(old)old.remove();if(!zone||!scale)return false;
 const frame=svg.querySelector('[data-chart-frame]')||svg.querySelector('[data-movement-frame]');if(!frame)return false;
 const x=Number(frame.getAttribute('x')),top=Number(frame.getAttribute('y')),bottom=top+Number(frame.getAttribute('height'));
 const a=Math.max(top,scale.y(zone.high)),b=Math.min(bottom,scale.y(zone.low));if(b<=a)return false;
 const rect=svg.ownerDocument.createElementNS('http://www.w3.org/2000/svg','rect');
 Object.entries({'data-zone-highlight':'',x,y:a,width:frame.getAttribute('width'),height:b-a,fill:'var(--viz-series-2)','fill-opacity':.16,'pointer-events':'none'}).forEach(([k,v])=>rect.setAttribute(k,String(v)));svg.appendChild(rect);return true;
}
if(typeof module!=='undefined')module.exports={projectZoneParticipation,renderZoneParticipation,highlightParticipationZone};
