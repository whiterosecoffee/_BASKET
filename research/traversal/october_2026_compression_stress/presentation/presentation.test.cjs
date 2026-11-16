'use strict';
// Synthetic offline checks; no recorded ticker history or browser claim.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {qualifyDensityDataset,selectDensityWindow,densitySwingStructure}=require('./controller.js');
let count=0;function test(name,fn){fn();count++;console.log('PASS '+name);}
const bar=(i,c=10)=>({t:Date.UTC(2026,0,2,14,30)+i*60000,o:c,h:c+.25,l:c-.25,c,v:100+i,vw:c});
const minute=Array.from({length:80},(_,i)=>bar(i,10+Math.sin(i/3)));
const daily=Array.from({length:260},(_,i)=>({...bar(i,10+Math.sin(i/9)),t:Date.UTC(2025,0,2)+i*86400000}));
test('ordered input and source arrays stay unchanged',()=>{const a={daily,minute},before=JSON.stringify(a);assert.equal(qualifyDensityDataset(a).daily.length,260);assert.equal(JSON.stringify(a),before);});
test('empty input rejected',()=>assert.throws(()=>qualifyDensityDataset({daily:[],minute:[]})));
test('duplicate timestamp rejected',()=>assert.throws(()=>qualifyDensityDataset({minute:[bar(0),bar(0)]})));
test('unordered timestamp rejected',()=>assert.throws(()=>qualifyDensityDataset({minute:[bar(1),bar(0)]})));
test('negative volume rejected',()=>assert.throws(()=>qualifyDensityDataset({minute:[{...bar(0),v:-1}]})));
test('invalid OHLC rejected',()=>assert.throws(()=>qualifyDensityDataset({minute:[{...bar(0),l:12}]})));
test('numeric strings rejected',()=>assert.throws(()=>qualifyDensityDataset({minute:[{...bar(0),c:'10'}]})));
test('misaligned minute rejected',()=>assert.throws(()=>qualifyDensityDataset({minute:[{...bar(0),t:bar(0).t+1}]})));
test('anomalous VWAP retained for quality accounting',()=>assert.equal(qualifyDensityDataset({minute:[{...bar(0),vw:99}]}).minute[0].vw,99));
test('unknown VWAP remains null',()=>assert.equal(qualifyDensityDataset({minute:[{...bar(0),vw:null}]}).minute[0].vw,null));
test('paging changes selected observations',()=>{const d=qualifyDensityDataset({daily,minute});assert.equal(selectDensityWindow(d,'21').at(-1).t,daily.at(-1).t);assert.equal(selectDensityWindow(d,'21',21).at(-1).t,daily.at(-22).t);assert.equal(selectDensityWindow(d,'pm').length,80);});
test('invalid window rejected',()=>assert.throws(()=>selectDensityWindow({daily},'bad')));
const swingBars=[10,12,15,12,11,10,13,11,9,8,11,10,7,9,12,14,13,12].map((c,i)=>bar(i,c));
test('pivots require future confirmation bars',()=>{const s=densitySwingStructure(swingBars,1);assert(s.pivots.length>0);for(const p of s.pivots){assert.equal(p.knownIndex,p.pivotIndex+1);assert(p.knownAt>p.pivotAt);}assert.equal(densitySwingStructure(swingBars.slice(0,3),1).pivots.length,0);});
test('earlier events identical under prefix replay',()=>{const full=densitySwingStructure(swingBars,1);for(let n=1;n<=swingBars.length;n++){const s=densitySwingStructure(swingBars.slice(0,n),1);assert.deepEqual(s.pivots,full.pivots.filter(p=>p.knownIndex<n));assert.deepEqual(s.breaks,full.breaks.filter(p=>p.knownIndex<n));}});
test('lower structure followed by upward break is a candidate',()=>assert(densitySwingStructure(swingBars,1).breaks.some(b=>b.direction==='up')));
test('flat ties do not fabricate pivots',()=>assert.equal(densitySwingStructure([0,1,2,3,4].map(i=>bar(i)),1).pivots.length,0));
test('dual high-low outside candle is ambiguous',()=>{const b=[bar(0),{...bar(1),h:12,l:8},bar(2)];assert.equal(densitySwingStructure(b,1).pivots[0].kind,'ambiguous');});
// Native-SVG construction smoke checks at phone and desktop widths.
let doc;class Element{constructor(){this.children=[];this.namespaceURI='http://www.w3.org/2000/svg';this.ownerDocument=doc;this.attrs={};}setAttribute(k,v){this.attrs[k]=String(v);}appendChild(e){this.children.push(e);return e;}append(...e){this.children.push(...e);}replaceChildren(){this.children=[];}get firstChild(){return this.children[0];}removeChild(e){this.children.splice(this.children.indexOf(e),1);}}
doc={createElementNS:()=>new Element()};const context={document:doc,Intl,Math,Number,Map,Date};vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/density.js','utf8'),context);
const names=['drawVolumeRails','drawRollingRibbons','drawRevisitThreads','drawDensityHeatmap','drawNestedProfiles'];
test('five renderers construct at two widths and five windows',()=>{for(const width of [320,736])for(const data of [minute,daily.slice(-5),daily.slice(-21),daily.slice(-63),daily.slice(-252)])for(const name of names){const svg=new Element(),r=context[name](svg,data,width,320);assert(r.scale&&typeof r.scale.x==='function'&&typeof r.scale.y==='function');assert(svg.children.length>0);}});
test('three explicit allocation models conserve volume',()=>{const data=[bar(0),{...bar(1),vw:99},bar(2)];for(const name of ['drawVolumeRails','drawRevisitThreads','drawDensityHeatmap']){const r=context[name](new Element(),data,320,320);const good=r.allocatedVolume??r.allocated,bad=r.unallocatedVolume??r.unallocated;assert.equal(good,202);assert.equal(bad,101);}});
test('no network or embedded source history',()=>{for(const file of ['density.js','controller.js','index.html']){const s=fs.readFileSync(__dirname+'/'+file,'utf8');assert(!/fetch\s*\(|XMLHttpRequest|WebSocket|https?:\/\//.test(s.replace(/http:\/\/www\.w3\.org\/2000\/svg/g,'')));}assert(!/<script[^>]+type=["']application\/json/.test(fs.readFileSync(__dirname+'/index.html','utf8')));});
console.log(`${count} synthetic checks passed; 50 renderer calls. No browser layout, real-market, canonical-integration or independent-CI acceptance implied.`);
