// Analytical aggregation is explicit and independent of viewport geometry.
function densitySliceCount(requested=8, rowCount){
 if(!Number.isInteger(requested)||requested<3||requested>20)throw Error('Slice count must be an integer from 3 to 20.');
 return Math.min(requested,rowCount);
}
/* Volume Rails: native-SVG presentation of bar-allocated volume by price.
 * Each source bar is {t,o,h,l,c,v,vw}; t is UTC milliseconds.
 * Call again after changing the selected time window. No network or storage.
 */
function drawVolumeRails(svg, data, width, height, options = {}) {
  if (!svg || svg.namespaceURI !== 'http://www.w3.org/2000/svg') {
    throw new TypeError('drawVolumeRails requires a native SVG element');
  }
  const ns = 'http://www.w3.org/2000/svg';
  const w = Math.max(280, Number(width) || 360);
  const h = Math.max(240, Number(height) || 320);
  const m = {left: 64, right: 14, top: 20, bottom: 52};
  const pw = w - m.left - m.right, ph = h - m.top - m.bottom;
  const valid = (data || []).filter(d => [d.t,d.o,d.h,d.l,d.c,d.v].every(Number.isFinite)
    && d.v >= 0 && d.l <= d.h).sort((a,b) => a.t-b.t);
  svg.replaceChildren();
  svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', String(h));
  svg.setAttribute('role', 'img');
  const el = (tag, attrs = {}, value) => {
    const node = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([key,val]) => node.setAttribute(key, String(val)));
    if (value !== undefined) node.textContent = value;
    return node;
  };
  const text = (x,y,value,attrs={}) => el('text', {x,y,fill:'var(--foreground)',
    'font-size':12,'font-weight':400,...attrs}, value);
  svg.appendChild(el('title', {}, 'Volume Rails: price through time over volume density levels'));
  if (!valid.length) {
    svg.appendChild(text(m.left,m.top+24,'No qualified bars in this window.'));
    return {totalVolume:0,allocatedVolume:0,unallocatedVolume:0,bands:[]};
  }
  const x0 = valid[0].t;
  const x1 = Math.max(x0+60000,valid[valid.length-1].t);
  const observedLo = Math.min(...valid.map(d=>d.l));
  const observedHi = Math.max(...valid.map(d=>d.h));
  const span = Math.max(.01,observedHi-observedLo);
  const y0 = observedLo-span*.08, y1 = observedHi+span*.08;
  const x = t => m.left+(t-x0)/(x1-x0)*pw;
  const y = price => m.top+(y1-price)/(y1-y0)*ph;
  const rawStep = span/12;
  const magnitude = Math.pow(10,Math.floor(Math.log10(rawStep)));
  const fraction = rawStep/magnitude;
  const step = Number(options.bandSize) > 0 ? Number(options.bandSize)
    : (fraction<=1?1:fraction<=2?2:fraction<=5?5:10)*magnitude;
  const bins = new Map();
  let totalVolume=0,allocatedVolume=0,unallocatedVolume=0;
  valid.forEach(d => {
    totalVolume+=d.v;
    if (!Number.isFinite(d.vw) || d.vw < d.l || d.vw > d.h) {
      unallocatedVolume+=d.v;
      return;
    }
    const index = Math.floor(d.vw/step), lo=index*step;
    if (!bins.has(index)) bins.set(index,{low:lo,high:lo+step,volume:0,samples:0});
    const band=bins.get(index); band.volume+=d.v; band.samples++;
    allocatedVolume+=d.v;
  });
  const bands=[...bins.values()].sort((a,b)=>a.low-b.low);
  const maxVolume=Math.max(1,...bands.map(d=>d.volume));
  const plot=el('g');
  svg.appendChild(plot);
  plot.appendChild(el('rect', {x:m.left,y:m.top,width:pw,height:ph,fill:'none',
    stroke:'var(--border)','stroke-width':1,'data-chart-frame':''}));
  const priceFormat = p => '$'+p.toFixed(step<1?2:0);
  const volFormat = v => v>=1e6?(v/1e6).toFixed(2)+'M':v>=1000?(v/1000).toFixed(0)+'K':v.toFixed(0);
  // Rails occupy the same full time backdrop. Their thickness and opacity,
  // rather than their x length, encode volume in each price band.
  bands.forEach(band => {
    const ratio=band.volume/maxVolume, mid=(band.low+band.high)/2;
    const yy=y(mid);
    const thickness=Math.min(Math.max(2,1+ratio*11),ph/12);
    if (yy-thickness/2<m.top || yy+thickness/2>m.top+ph) return;
    const rail=el('line',{x1:m.left+1,x2:m.left+pw-1,y1:yy,y2:yy,
      stroke:'var(--viz-series-2)','stroke-width':thickness,
      'stroke-opacity':.10+.38*ratio,
      'data-tooltip':`${priceFormat(band.low)}–${priceFormat(band.high)} · ${volFormat(band.volume)} shares · ${totalVolume ? (100*band.volume/totalVolume).toFixed(1):'0.0'}% of total selected-window volume`});
    plot.appendChild(rail);
  });
  // Five USD ticks, no implied support/resistance label.
  for(let i=0;i<5;i++) {
    const value=observedLo+(observedHi-observedLo)*i/4, yy=y(value);
    plot.appendChild(el('line',{x1:m.left,x2:m.left+pw,y1:yy,y2:yy,
      stroke:'var(--border)','stroke-width':1,'stroke-opacity':.5}));
    svg.appendChild(text(m.left-8,yy+4,'$'+value.toFixed(2),{'text-anchor':'end'}));
  }
  const path=valid.map((d,i)=>(i?'L':'M')+x(d.t).toFixed(2)+','+y(d.c).toFixed(2)).join(' ');
  plot.appendChild(el('path',{d:path,fill:'none',stroke:'var(--viz-series-1)',
    'stroke-width':2,'stroke-linejoin':'round'}));
  const last=valid[valid.length-1];
  plot.appendChild(el('circle',{cx:x(last.t),cy:y(last.c),r:3,fill:'var(--viz-series-1)'}));
  const isIntraday=x1-x0<2*86400000;
  const timeLabel=t=>new Intl.DateTimeFormat('en-US',isIntraday
    ? {hour:'numeric',minute:'2-digit',timeZone:'America/New_York'}
    : {month:'short',day:'numeric',timeZone:'America/New_York'}).format(new Date(t));
  const tickCount=w<420?3:4;
  for(let i=0;i<tickCount;i++) {
    const value=x0+(x1-x0)*i/(tickCount-1);
    svg.appendChild(text(x(value),m.top+ph+19,timeLabel(value),
      {'text-anchor':i===0?'start':i===tickCount-1?'end':'middle'}));
  }
  const xTitle=text(m.left+pw/2,h-6,isIntraday?'Time · ET':'Date · ET',
    {'text-anchor':'middle','class':'axis-title','data-axis':'x'});
  const yTitle=text(15,m.top+ph/2,'Price · USD',{'text-anchor':'middle',
    transform:`rotate(-90 15 ${m.top+ph/2})`,'class':'axis-title','data-axis':'y'});
  svg.append(xTitle,yTitle);
  const pct=totalVolume?100*unallocatedVolume/totalVolume:0;
  svg.setAttribute('aria-label',`Price line and volume rails for ${valid.length} bars. `+
    `Volume allocated by bar VWAP into ${step} dollar bands. ${pct.toFixed(1)} percent unallocated.`);
  return {totalVolume,allocatedVolume,unallocatedVolume,bandSize:step,bands,
    latestPrice:last.c,low:observedLo,high:observedHi,
    scale:{x,y},method:'whole-bar VWAP allocation; not exact volume at price'};
}

/* Rolling Ribbons presentation. No retrieval or persistence side effects. */
function drawRollingRibbons(svg, data, width, height, options = {}) {
  const ns = 'http://www.w3.org/2000/svg';
  const doc = svg.ownerDocument;
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  const W = Math.max(280, Number(width) || 600);
  const H = Math.max(280, Number(height) || 360);
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', H);
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', 'Price over time with consecutive volume-weighted price ribbons. Bands estimate concentration using bar VWAP, not individual trades.');
  const make = (tag, attrs, text, parent = svg) => {
    const el = doc.createElementNS(ns, tag);
    Object.entries(attrs || {}).forEach(([k,v]) => el.setAttribute(k, String(v)));
    if (text !== undefined) el.textContent = text;
    parent.appendChild(el); return el;
  };
  make('title', {}, 'Rolling volume density ribbons');
  make('desc', {}, 'Successive time slices show volume-weighted 20–80 and 40–60 percentile price envelopes. Individual bar volume is assigned at reported VWAP. The foreground line is closing price.');
  const rows = data.map(r => ({...r, t:+r.t, c:+r.c, l:+r.l, h:+r.h, v:+r.v, vw:+r.vw}))
    .filter(r => Number.isFinite(r.t) && Number.isFinite(r.c) && Number.isFinite(r.l) && Number.isFinite(r.h))
    .sort((a,b) => a.t-b.t);
  if (!rows.length) { make('text', {x:20,y:40,fill:'var(--foreground)'}, 'No qualified price observations'); return {slices:[]}; }
  const pad = {left:64,right:20,top:36,bottom:61};
  const plotW = W-pad.left-pad.right, plotH = H-pad.top-pad.bottom;
  let minT=rows[0].t,maxT=rows[rows.length-1].t;
  if(minT===maxT) {minT-=30000;maxT+=30000;}
  let low=Math.min(...rows.map(r=>r.l)), high=Math.max(...rows.map(r=>r.h));
  const cushion=Math.max((high-low)*.08,Math.abs(high)*.0005,.01); low-=cushion;high+=cushion;
  const X=t=>pad.left+(t-minT)/(maxT-minT)*plotW;
  const Y=p=>pad.top+(high-p)/(high-low)*plotH;
  const label = (x,y,text,anchor='start',other={}) => make('text',{x,y,'text-anchor':anchor,fill:'var(--foreground)','font-size':12,...other},text);
  const count=densitySliceCount(options.sliceCount,rows.length);
  const slices=[];
  const quantile=(bucket,q)=>{
    const list=bucket.filter(r=>Number.isFinite(r.vw)&&r.vw>=r.l&&r.vw<=r.h&&r.v>0).sort((a,b)=>a.vw-b.vw);
    const total=list.reduce((s,r)=>s+r.v,0); if(!total)return null;
    let accum=0;for(const r of list){accum+=r.v;if(accum>=total*q)return r.vw;}return list[list.length-1].vw;
  };
  for(let i=0;i<count;i++){
    const start=Math.floor(i*rows.length/count),end=Math.floor((i+1)*rows.length/count);
    const bucket=rows.slice(start,end);
    if(!bucket.length)continue;
    const q20=quantile(bucket,.2);if(q20===null)continue;
    const qualified=bucket.filter(r=>Number.isFinite(r.vw)&&r.vw>=r.l&&r.vw<=r.h&&r.v>0);
    slices.push({t:(bucket[0].t+bucket[bucket.length-1].t)/2,from:bucket[0].t,to:bucket[bucket.length-1].t,q20,q40:quantile(bucket,.4),q60:quantile(bucket,.6),q80:quantile(bucket,.8),shares:qualified.reduce((s,r)=>s+r.v,0)});
  }
  for(let j=0;j<4;j++){
    const value=low+(high-low)*j/3,yy=Y(value);
    make('line',{x1:pad.left,x2:W-pad.right,y1:yy,y2:yy,stroke:'var(--border)','stroke-width':1});
    label(pad.left-8,yy+4,'$'+value.toFixed(high-low>40?0:2),'end');
  }
  const polygon=(upper,lower)=>slices.map(s=>`${X(s.t)},${Y(s[upper])}`).concat([...slices].reverse().map(s=>`${X(s.t)},${Y(s[lower])}`)).join(' ');
  if(slices.length>1){
    make('polygon',{points:polygon('q80','q20'),fill:'var(--viz-series-2)','fill-opacity':.18});
    make('polygon',{points:polygon('q60','q40'),fill:'var(--viz-series-2)','fill-opacity':.4});
    for(const key of ['q20','q80'])make('polyline',{points:slices.map(s=>`${X(s.t)},${Y(s[key])}`).join(' '),fill:'none',stroke:'var(--viz-series-2)','stroke-width':1.2,'stroke-opacity':.65});
  }
  make('polyline',{points:rows.map(r=>`${X(r.t)},${Y(r.c)}`).join(' '),fill:'none',stroke:'var(--viz-series-1)','stroke-width':2.1,'stroke-linejoin':'round','stroke-linecap':'round'});
  const date=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',month:'short',day:'numeric'});
  const intraday=maxT-minT<36*3600000;
  const clock=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',hour:'numeric',minute:'2-digit'});
  const tickCount=W<420?3:4;
  for(let i=0;i<tickCount;i++){
    const t=minT+(maxT-minT)*i/(tickCount-1);
    label(X(t),H-37,intraday?clock.format(t):date.format(t),i===0?'start':i===tickCount-1?'end':'middle');
  }
  label(pad.left,pad.top-15,'Rolling volume concentration');
  label(pad.left,H-11,'Time · ET','start',{'class':'axis-title','data-axis':'x'});
  make('rect',{'data-chart-frame':'',x:pad.left,y:pad.top,width:plotW,height:plotH,fill:'none',stroke:'var(--border)','stroke-width':1});
  make('text',{x:15,y:pad.top+plotH/2,transform:`rotate(-90 15 ${pad.top+plotH/2})`,fill:'var(--foreground)','font-size':12,'text-anchor':'middle','class':'axis-title','data-axis':'y'},'Price · USD');
  const last=rows[rows.length-1];
  make('circle',{cx:X(last.t),cy:Y(last.c),r:3.5,fill:'var(--viz-series-1)','data-tooltip':`Latest close $${last.c.toFixed(2)}`});
  slices.forEach(s=>make('circle',{cx:X(s.t),cy:Y((s.q40+s.q60)/2),r:17,fill:'transparent','data-tooltip':`Allocated shares ${Math.round(s.shares).toLocaleString()}; central 60% $${s.q20.toFixed(2)}–$${s.q80.toFixed(2)}; VWAP allocation estimate`}));
  return {scale:{x:X,y:Y},slices,low,high,allocation:'Entire bar volume allocated at qualified reported VWAP; rolling slices are equal observation counts, not equal elapsed duration.'};
}

function drawRevisitThreads(svg, data, width, height, config = {}) {
  const ns = 'http://www.w3.org/2000/svg';
  const el = (tag, attrs, text) => {
    const node = document.createElementNS(ns, tag);
    Object.entries(attrs || {}).forEach(([k, v]) => node.setAttribute(k, v));
    if (text != null) node.textContent = text;
    return node;
  };
  const rows = data.filter(d => Number.isFinite(d.t) && Number.isFinite(d.c)).slice().sort((a,b) => a.t-b.t);
  svg.replaceChildren();
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svg.setAttribute('role','img');
  svg.append(el('title', {}, 'Revisit threads: price path with volume-weighted returns to price bands'));
  svg.append(el('desc', {}, 'Horizontal segments show sampled visits to fixed price bands. Dotted connectors join separate visits. Circle area represents allocated share volume. Allocation uses bar VWAP; invalid VWAP is left unallocated.'));
  if (!rows.length) return {allocated:0,unallocated:0,visits:[]};
  const m = Object.assign({left:64,right:18,top:18,bottom:47},config.margins);
  const pw=Math.max(1,width-m.left-m.right), ph=Math.max(1,height-m.top-m.bottom);
  const lo = config.priceDomain ? config.priceDomain[0] : Math.min(...rows.map(d=>Number.isFinite(d.l)?d.l:d.c));
  const hi = config.priceDomain ? config.priceDomain[1] : Math.max(...rows.map(d=>Number.isFinite(d.h)?d.h:d.c));
  const pad=Math.max((hi-lo)*.06,.05), ymin=lo-pad, ymax=hi+pad;
  const tmin=rows[0].t, tmax=rows[rows.length-1].t;
  const x=t=>m.left+12+(t-tmin)/Math.max(1,tmax-tmin)*Math.max(1,pw-24);
  const y=p=>m.top+12+(ymax-p)/(ymax-ymin)*Math.max(1,ph-24);
  const step=config.binSize || ([.25,.5,1,2,5,10,20,50].find(s=>(hi-lo)/s<=14) || 100);
  const color=config.densityColor || 'var(--viz-series-2)';
  const lineColor=config.priceColor || 'var(--viz-series-1)';
  svg.append(el('rect',{'data-chart-frame':'',x:m.left,y:m.top,width:pw,height:ph,fill:'none',stroke:'var(--border)'}));
  for(let i=0;i<4;i++) {
    const price=ymin+(ymax-ymin)*i/3, yy=y(price);
    if(i>0 && i<3) svg.append(el('line',{x1:m.left,y1:yy,x2:width-m.right,y2:yy,stroke:'var(--border)','stroke-width':1}));
    svg.append(el('text',{x:m.left-8,y:yy+4,'text-anchor':'end',fill:'var(--foreground)','font-size':12},price.toFixed(2)));
  }
  const dateFormat = (t) => new Date(t).toLocaleString('en-US',{timeZone:'America/New_York',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
  const shortFormat = (t) => {
    const opts=tmax-tmin>86400000?{month:'short',day:'numeric'}:{hour:'numeric',minute:'2-digit'};
    return new Date(t).toLocaleString('en-US',{timeZone:'America/New_York',...opts});
  };
  const ticks=width<450?3:4;
  for(let i=0;i<ticks;i++) {
    const t=tmin+(tmax-tmin)*i/(ticks-1);
    svg.append(el('text',{x:x(t),y:height-m.bottom+21,'text-anchor':i===0?'start':i===ticks-1?'end':'middle',fill:'var(--foreground)','font-size':12},shortFormat(t)));
  }
  svg.append(el('text',{'class':'axis-title','data-axis':'x',x:m.left+pw/2,y:height-4,'text-anchor':'middle',fill:'var(--foreground)','font-size':12},'Time · ET'));
  svg.append(el('text',{'class':'axis-title','data-axis':'y',x:14,y:m.top+ph/2,transform:`rotate(-90 14 ${m.top+ph/2})`,'text-anchor':'middle',fill:'var(--foreground)','font-size':12},'Price · USD'));
  const episodes=[]; let current=null, allocated=0,unallocated=0;
  rows.forEach((d,i)=>{
    const volume=Number.isFinite(d.v)?Math.max(d.v,0):0;
    const valid=Number.isFinite(d.vw) && d.vw>=d.l && d.vw<=d.h;
    if(!valid){unallocated+=volume;current=null;return;}
    allocated+=volume;
    const bin=Math.floor(d.vw/step)*step;
    if(!current || current.bin!==bin || current.endIndex!==i-1){current={bin,start:d.t,end:d.t,startIndex:i,endIndex:i,volume:0,samples:0};episodes.push(current);}
    current.end=d.t;current.endIndex=i;current.volume+=volume;current.samples++;
  });
  const bands=new Map();episodes.forEach(e=>{if(!bands.has(e.bin))bands.set(e.bin,[]);bands.get(e.bin).push(e);});
  const volumeByBand=[...bands].map(([bin,visits])=>({bin,visits,total:visits.reduce((s,v)=>s+v.volume,0)})).sort((a,b)=>b.total-a.total);
  const shown=volumeByBand.slice(0,Math.min(7,Math.max(3,Math.floor(ph/32))));
  const maxEpisode=Math.max(1,...episodes.map(e=>e.volume));
  shown.forEach(({bin,visits})=>{
    const yy=y(bin+step/2);
    for(let j=1;j<visits.length;j++)svg.append(el('line',{x1:x(visits[j-1].end),x2:x(visits[j].start),y1:yy,y2:yy,stroke:color,'stroke-width':1,'stroke-dasharray':'2 5',opacity:.4}));
    visits.forEach(e=>{
      const xx=x((e.start+e.end)/2),radius=3+7*Math.sqrt(e.volume/maxEpisode);
      svg.append(el('line',{x1:x(e.start),x2:x(e.end),y1:yy,y2:yy,stroke:color,'stroke-width':2,opacity:.55}));
      const node=el('circle',{cx:xx,cy:yy,r:radius,fill:color,opacity:.45});
      node.setAttribute('data-tooltip',`$${bin.toFixed(2)}–$${(bin+step).toFixed(2)} · ${dateFormat(e.start)}–${dateFormat(e.end)} · ${(e.volume/1e6).toFixed(2)}M allocated shares · ${e.samples} bar samples`);
      svg.append(node);
    });
  });
  svg.append(el('path',{d:rows.map((d,i)=>`${i?'L':'M'}${x(d.t)},${y(d.c)}`).join(' '),fill:'none',stroke:lineColor,'stroke-width':2}));
  const last=rows.at(-1);svg.append(el('circle',{cx:x(last.t),cy:y(last.c),r:3.5,fill:lineColor}));
  return {scale:{x,y},allocated,unallocated,binSize:step,visits:episodes,bands:volumeByBand};
}

/* Two additional presentation-only models over supplied bars. */
function densityPlotBase(svg, data, width, height, name, options={}) {
 const ns='http://www.w3.org/2000/svg';svg.replaceChildren();svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.setAttribute('role','img');
 const e=(tag,attrs={},text)=>{const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));if(text!==undefined)n.textContent=text;svg.appendChild(n);return n;};
 e('title',{},name);const rows=data.slice(),m={l:64,r:18,t:20,b:52},pw=width-m.l-m.r,ph=height-m.t-m.b;
 if(!rows.length)return null;
 const extra=(options.extraPrices||[]).filter(Number.isFinite),low=Math.min(...rows.map(d=>d.l),...extra),high=Math.max(...rows.map(d=>d.h),...extra),pad=Math.max((high-low)*.08,.02),lo=low-pad,hi=high+pad,t0=rows[0].t,t1=Math.max(t0+60000,rows.at(-1).t);
 const x=t=>m.l+8+(t-t0)/(t1-t0)*(pw-16),y=p=>m.t+8+(hi-p)/(hi-lo)*(ph-16);
 e('rect',{x:m.l,y:m.t,width:pw,height:ph,fill:'none',stroke:'var(--border)','data-chart-frame':''});
 for(let i=0;i<4;i++){const p=low+(high-low)*i/3;e('line',{x1:m.l,x2:width-m.r,y1:y(p),y2:y(p),stroke:'var(--border)','stroke-width':1});e('text',{x:m.l-8,y:y(p)+4,'text-anchor':'end'},'$'+p.toFixed(2));}
 const intra=t1-t0<36*3600000,fmt=new Intl.DateTimeFormat('en-US',intra?{timeZone:'America/New_York',hour:'numeric',minute:'2-digit'}:{timeZone:'America/New_York',month:'short',day:'numeric'});
 for(let i=0;i<3;i++){const t=t0+(t1-t0)*i/2;e('text',{x:x(t),y:height-29,'text-anchor':i===0?'start':i===2?'end':'middle'},fmt.format(t));}
 e('text',{x:m.l+pw/2,y:height-6,'text-anchor':'middle','class':'axis-title','data-axis':'x'},'Time · ET');e('text',{x:14,y:m.t+ph/2,transform:`rotate(-90 14 ${m.t+ph/2})`,'text-anchor':'middle','class':'axis-title','data-axis':'y'},'Price · USD');
 const path=()=>{e('path',{d:rows.map((d,i)=>(i?'L':'M')+x(d.t)+','+y(d.c)).join(' '),fill:'none',stroke:'var(--viz-series-1)','stroke-width':2});e('circle',{cx:x(rows.at(-1).t),cy:y(rows.at(-1).c),r:3,fill:'var(--viz-series-1)'});};
 const valid=d=>Number.isFinite(d.vw)&&d.vw>=d.l&&d.vw<=d.h&&d.v>=0;
 const span=Math.max(.01,high-low),raw=span/14,mag=10**Math.floor(Math.log10(raw)),step=([1,2,5,10].find(n=>n>=raw/mag)||10)*mag;
 return {e,x,y,rows,m,pw,ph,t0,t1,lo,hi,low,high,step,valid,path};
}
function drawDensityHeatmap(svg,data,width,height,options={}){
 const b=densityPlotBase(svg,data,width,height,'Time–price heatmap: darker cells represent more allocated shares');if(!b)return{};
 const {e,x,y,rows,t0,t1,step,valid,path}=b,cols=densitySliceCount(options.sliceCount,rows.length),cells=new Map();
 let unallocated=0,allocated=0;
 for(const d of rows){if(!valid(d)){unallocated+=d.v;continue;}allocated+=d.v;const col=Math.min(cols-1,Math.floor((d.t-t0)/(t1-t0)*cols)),bin=Math.floor(d.vw/step),key=col+':'+bin;if(!cells.has(key))cells.set(key,{col,bin,v:0,n:0});const c=cells.get(key);c.v+=d.v;c.n++;}
 const max=Math.max(1,...[...cells.values()].map(c=>c.v));
 for(const c of cells.values()){const from=t0+c.col/cols*(t1-t0),to=t0+(c.col+1)/cols*(t1-t0),lower=Math.max(b.lo,c.bin*step),upper=Math.min(b.hi,(c.bin+1)*step);if(upper<=lower)continue;e('rect',{x:x(from),y:y(upper),width:Math.max(1,x(to)-x(from)-1),height:Math.max(1,y(lower)-y(upper)-1),fill:'var(--viz-series-2)','fill-opacity':.12+.65*Math.sqrt(c.v/max),'data-tooltip':`$${lower.toFixed(2)}–$${upper.toFixed(2)} · ${(c.v/1e6).toFixed(2)}M shares · ${c.n} bar samples`});}
 path();return{scale:{x,y},allocated,unallocated,cells:[...cells.values()],sliceCount:cols,bandSize:step};
}
function drawNestedProfiles(svg,data,width,height){
 const b=densityPlotBase(svg,data,width,height,'Nested profiles: full-window and recent volume distributions');if(!b)return{};
 const {e,x,y,rows,step,valid,path}=b,intra=b.t1-b.t0<36*3600000;
 const counts=intra?[rows.length,Math.min(60,rows.length),Math.min(15,rows.length)]:[rows.length,Math.min(21,rows.length),Math.min(5,rows.length)];
 const labels=intra?['Full window','Last 60 bars','Last 15 bars']:['Full window','Last 21 bars','Last 5 bars'];
 const colors=['var(--viz-series-2)','var(--viz-series-3)','var(--viz-series-4)'];
 const profiles=[];
 counts.forEach((n,i)=>{const subset=rows.slice(-n),bins=new Map();let allocated=0,unallocated=0;for(const d of subset){if(!valid(d)){unallocated+=d.v;continue;}allocated+=d.v;const k=Math.floor(d.vw/step);bins.set(k,(bins.get(k)||0)+d.v);}profiles.push({label:labels[i],allocated,unallocated,bins:[...bins]});const max=Math.max(1,...bins.values()),maxWidth=b.pw*.42,right=x(b.t1);
 for(const [k,v] of bins){const lower=Math.max(b.lo,k*step),upper=Math.min(b.hi,(k+1)*step);if(upper<=lower)continue;const yy=y((lower+upper)/2)+(i-1)*3;e('line',{x1:right-maxWidth*v/max,x2:right,y1:yy,y2:yy,stroke:colors[i],'stroke-width':i===0?8:i===1?4:2,'stroke-opacity':i===0?.18:.65,'data-tooltip':`${labels[i]} · $${(k*step).toFixed(2)}–$${((k+1)*step).toFixed(2)} · ${(v/1e6).toFixed(2)}M shares · ${allocated?(100*v/allocated).toFixed(1):0}% of qualified window`});}});
 path();return{scale:{x,y},profiles,bandSize:step,normalization:'Each profile normalized to its own largest band; widths compare shape, not absolute volume.'};
}
function densityRangeDynamics(rows,span=15){
 if(!Number.isInteger(span)||span<2)throw Error('Invalid range span.');
 const out=[];
 function windowStats(from,to){const a=rows.slice(from,to),low=Math.min(...a.map(r=>r.l)),high=Math.max(...a.map(r=>r.h)),mid=(low+high)/2;return{low,high,width:high-low,widthPct:100*(high-low)/mid,shares:a.reduce((s,r)=>s+r.v,0)};}
 for(let i=span-1;i<rows.length;i++){
  const current=windowStats(i-span+1,i+1),prior=i>=2*span-1?windowStats(i-2*span+1,i-span+1):null;
  const widthChangePct=prior&&prior.widthPct>0?100*(current.widthPct/prior.widthPct-1):null;
  const phase=widthChangePct===null?(prior&&prior.widthPct===0&&current.widthPct===0?'unchanged':'no baseline'):Math.abs(widthChangePct)<1e-10?'unchanged':widthChangePct>0?'expansion':'compression';
  out.push({t:rows[i].t,knownAt:rows[i].t,span,...current,prior,widthChangePct,phase,volumeRatio:prior&&prior.shares>0?current.shares/prior.shares:null});
 }
 return out;
}
function drawCompressionExpansion(svg,data,width,height,options={}){
 const span=options.span||15,history=(options.history||data).filter(r=>r.t<=data.at(-1).t);
 const series=densityRangeDynamics(history,span).filter(p=>p.t>=data[0].t),b=densityPlotBase(svg,data,width,height,'Compression and expansion: trailing range envelope through time',{extraPrices:series.flatMap(p=>[p.low,p.high])});if(!b)return{};
 const {e,x,y,path}=b;
 for(let i=1;i<series.length;i++){
  const a=series[i-1],c=series[i],color=c.phase==='compression'?'var(--viz-series-2)':c.phase==='expansion'?'var(--viz-series-4)':'var(--muted-foreground)';
  e('polygon',{points:`${x(a.t)},${y(a.high)} ${x(c.t)},${y(c.high)} ${x(c.t)},${y(c.low)} ${x(a.t)},${y(a.low)}`,fill:color,'fill-opacity':.14,'data-tooltip':`${span}-bar ${c.phase}; range $${c.low.toFixed(2)}–$${c.high.toFixed(2)}; width ${c.widthPct.toFixed(2)}% of midpoint; vs prior disjoint window ${c.widthChangePct===null?'unavailable':(c.widthChangePct>=0?'+':'')+c.widthChangePct.toFixed(1)+'%'}; volume ${c.volumeRatio===null?'unavailable':c.volumeRatio.toFixed(2)+'×'} prior window`});
 }
 for(const key of ['high','low'])if(series.length>1)e('polyline',{points:series.map(p=>`${x(p.t)},${y(p[key])}`).join(' '),fill:'none',stroke:'var(--viz-series-2)','stroke-width':1.3});
 path();
 return{scale:{x,y},series,latest:series.at(-1)??null,method:'Trailing high-low width as percent of midpoint; compared with the prior disjoint equal-bar window, not price direction.'};
}
function drawSwingStructure(svg,data,width,height,options={}){
 const history=(options.history||data).filter(r=>r.t<=data.at(-1).t),k=options.span||3;
 const structure=options.structure||(typeof densitySwingStructure==='function'?densitySwingStructure(history,k):{pivots:[],breaks:[]});
 const pivots=structure.pivots.filter(p=>p.knownAt>=data[0].t&&p.knownAt<=data.at(-1).t&&p.kind!=='ambiguous');
 const b=densityPlotBase(svg,data,width,height,'Separate swing structure: highs and lows without a trading-price line',{extraPrices:pivots.map(p=>p.price)});if(!b)return{};
 const {e,x,y}=b;
 for(const [kind,color] of [['high','var(--viz-series-4)'],['low','var(--viz-series-3)']]){
  const ps=pivots.filter(p=>p.kind===kind);if(ps.length>1)e('polyline',{points:ps.map(p=>`${x(p.knownAt)},${y(p.price)}`).join(' '),fill:'none',stroke:color,'stroke-width':2,'data-structure-line':kind});
  for(const p of ps)e('circle',{cx:x(p.knownAt),cy:y(p.price),r:3.5,fill:color,'data-tooltip':`${p.label} $${p.price.toFixed(2)} · swing ${new Date(p.pivotAt).toLocaleString('en-US',{timeZone:'America/New_York'})} · confirmed ${new Date(p.knownAt).toLocaleString('en-US',{timeZone:'America/New_York'})} ET · ${k} confirming bars each side`});
 }
 return{scale:{x,y},pivots,k,separate:true,latest:pivots.at(-1)??null};
}
function densityMovementBlocks(rows,span=15){
 if(!Number.isInteger(span)||span<2)throw Error('Invalid movement span.');
 const out=[];let lastNonflat=null;
 for(let start=0;start+span<=rows.length;start+=span){
  const block=rows.slice(start,start+span),first=block[0],last=block.at(-1),shares=block.reduce((s,r)=>s+r.v,0),delta=last.c-first.o,velocity=delta/span,direction=Math.abs(delta)<1e-10?'flat':delta>0?'up':'down',previous=out.at(-1);
  const reversal=direction!=='flat'&&lastNonflat!==null&&direction!==lastNonflat;
  const acceleration=previous?(velocity-previous.velocity)/span:null;
  const phase=reversal?'reversal':direction==='flat'?'flat':previous&&previous.direction===direction?(Math.abs(velocity)>Math.abs(previous.velocity)+1e-10?'accelerating':Math.abs(velocity)<Math.abs(previous.velocity)-1e-10?'decelerating':'steady'):'moving';
  out.push({start:first.t,t:last.t,knownAt:last.t,span,close:last.c,shares,delta,direction,reversal,velocity,acceleration,phase,movePerMillion:shares>0?delta/(shares/1e6):null});
  if(direction!=='flat')lastNonflat=direction;
 }
 return out;
}
function drawMovementPerShares(svg,data,width,height,options={}){
 const ns='http://www.w3.org/2000/svg';svg.replaceChildren();svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.setAttribute('role','img');
 const e=(tag,a={},text)=>{const n=document.createElementNS(ns,tag);Object.entries(a).forEach(([k,v])=>n.setAttribute(k,String(v)));if(text!==undefined)n.textContent=text;svg.appendChild(n);return n;};e('title',{},'Completed-block turns, speed changes and signed net movement per million shares');
 const span=options.span||15,history=(options.history||data).filter(r=>r.t<=data.at(-1).t),blocks=densityMovementBlocks(history,span).filter(b=>b.t>=data[0].t),left=64,right=18,plotW=width-left-right,t0=data[0].t,t1=Math.max(t0+60000,data.at(-1).t),X=t=>left+8+(t-t0)/(t1-t0)*(plotW-16);
 const low=Math.min(...data.map(d=>d.l)),high=Math.max(...data.map(d=>d.h)),pad=Math.max(.02,(high-low)*.08),top=26,topH=Math.round(height*.40),bottom=top+topH+46,bottomH=height-bottom-48,Y=p=>top+8+(high+pad-p)/(high-low+2*pad)*(topH-16);
 const values=blocks.map(b=>b.movePerMillion).filter(Number.isFinite),extent=Math.max(.01,...values.map(Math.abs))*1.1,Z=v=>bottom+bottomH/2-v/extent*(bottomH/2-8);
 for(const [y,h] of [[top,topH],[bottom,bottomH]])e('rect',{x:left,y,width:plotW,height:h,fill:'none',stroke:'var(--border)','data-movement-frame':''});
 e('text',{x:left,y:top-8},'Block turn ◆ / faster ○');e('text',{x:left,y:bottom-9},'Net movement per 1M shares');
 for(let i=0;i<3;i++){const p=low+(high-low)*i/2;e('text',{x:left-8,y:Y(p)+4,'text-anchor':'end'},'$'+p.toFixed(2));}
 for(const v of [-extent,0,extent]){const z=Z(v);e('line',{x1:left,x2:width-right,y1:z,y2:z,stroke:'var(--border)','stroke-width':1});e('text',{x:left-8,y:z+4,'text-anchor':'end'},v.toFixed(2));}
 e('text',{x:14,y:top+topH/2,transform:`rotate(-90 14 ${top+topH/2})`,'text-anchor':'middle','class':'axis-title','data-axis':'y'},'Price · USD');e('text',{x:14,y:bottom+bottomH/2,transform:`rotate(-90 14 ${bottom+bottomH/2})`,'text-anchor':'middle','class':'axis-title','data-axis':'y'},'USD / 1M shares');
 e('path',{d:data.map((r,i)=>(i?'L':'M')+X(r.t)+','+Y(r.c)).join(' '),fill:'none',stroke:'var(--muted-foreground)','stroke-width':1.4});
 const tooltip=b=>`${span}-bar ${b.reversal?'block-direction switch':b.phase} ${b.direction}; Δ$${b.delta.toFixed(3)} / ${(b.shares/1e6).toFixed(3)}M shares = ${b.movePerMillion===null?'unknown':b.movePerMillion.toFixed(3)} USD/1M; velocity ${b.velocity.toFixed(4)} USD/bar; acceleration ${b.acceleration===null?'unknown':b.acceleration.toFixed(5)} USD/bar²; completion-bar label ${new Date(b.knownAt).toLocaleString('en-US',{timeZone:'America/New_York'})} ET. Not causal price impact.`;
 let previous=null;
 for(const b of blocks){const color=b.direction==='up'?'var(--green)':b.direction==='down'?'var(--red)':'var(--foreground)';
  if(b.movePerMillion!==null){if(previous)e('line',{x1:X(previous.t),y1:Z(previous.movePerMillion),x2:X(b.t),y2:Z(b.movePerMillion),stroke:color,'stroke-width':1.8});e('circle',{cx:X(b.t),cy:Z(b.movePerMillion),r:3,fill:color,'data-tooltip':tooltip(b)});previous=b;}else previous=null;
 }
 for(const b of blocks.filter(b=>b.reversal||b.phase==='accelerating').slice(-8)){const x=X(b.t),y=Y(b.close),color=b.direction==='up'?'var(--green)':'var(--red)';if(b.reversal)e('polygon',{points:`${x},${y-6} ${x+5},${y} ${x},${y+6} ${x-5},${y}`,fill:color,'data-tooltip':tooltip(b)});else e('circle',{cx:x,cy:y,r:5,fill:'none',stroke:color,'stroke-width':1.8,'data-tooltip':tooltip(b)});}
 const intra=t1-t0<36*3600000,fmt=new Intl.DateTimeFormat('en-US',intra?{timeZone:'America/New_York',hour:'numeric',minute:'2-digit'}:{timeZone:'America/New_York',month:'short',day:'numeric'});for(let i=0;i<3;i++){const t=t0+(t1-t0)*i/2;e('text',{x:X(t),y:height-25,'text-anchor':i===0?'start':i===2?'end':'middle'},fmt.format(t));}e('text',{x:left+plotW/2,y:height-5,'text-anchor':'middle','class':'axis-title','data-axis':'x'},'Time · ET');
 return{scale:{x:X,y:Y},blocks,latest:blocks.at(-1)??null,separate:true,unclosedBars:history.length%span};
}
