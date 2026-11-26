'use strict';
const assert=require('node:assert/strict');
const {projectNestedContext,renderNestedContext,contextEtDay}=require('./context.js');
const {densitySwingStructure}=require('./controller.js');
const bar=(i,c=10)=>({t:Date.UTC(2026,0,1,5)+i*86400000,o:c,h:c+1,l:c-1,c,v:1000,vw:c});
let count=0;function test(name,fn){fn();count++;console.log('PASS '+name);}
const project=(daily,selected=daily.slice(-5),options={})=>projectNestedContext({daily,minute:[],source:'synthetic'},{selected,structureFn:densitySwingStructure,...options});
test('range position and distances use one common selected price without clamping',()=>{
 const daily=Array.from({length:40},(_,i)=>bar(i,10));const minute=[{...bar(41,20),t:Date.UTC(2026,1,12,12)}];
 const p=projectNestedContext({daily,minute},{selected:minute,minute:true});const r=p.rows.find(r=>r.grain==='daily'&&r.requested===5);
 assert(r.positionPct>100);assert(r.fromHigh>0);assert.equal(r.price,20);
 minute[0].c=5;const q=projectNestedContext({daily,minute},{selected:minute,minute:true}).rows.find(r=>r.grain==='daily'&&r.requested===5);assert(q.positionPct<0);assert(q.fromHigh<0);assert(q.fromLow<0);
});
test('same-day daily labels in UTC or ET are excluded from premarket context',()=>{
 const asOf=Date.UTC(2026,10,16,12),minute=[{...bar(0),t:asOf}],daily=[{...bar(0),t:Date.UTC(2026,10,13,5)},{...bar(0,999),t:Date.UTC(2026,10,16,0)},{...bar(0,888),t:Date.UTC(2026,10,16,5)}];
 const p=projectNestedContext({daily,minute},{selected:minute,minute:true});const r=p.rows.find(r=>r.grain==='daily'&&r.requested===5);
 assert.equal(r.count,1);assert.equal(r.high,11);assert(r.lagged);assert.equal(p.inputManifestHash,null);
});
test('paging cutoff does not use future daily bars',()=>{
 const a=Array.from({length:70},(_,i)=>bar(i,10+i/10)),selected=a.slice(20,25),p=project(a,selected);
 assert(p.rows.filter(r=>r.count).every(r=>r.to<=selected.at(-1).t));assert(p.rows.find(r=>r.selected).high<14);
});
test('partial and missing histories are explicit instead of padded',()=>{
 const p=project([bar(0),bar(1)]);const r=p.rows.find(r=>r.requested===252);assert.equal(r.count,2);assert.equal(r.status,'partial');
 const minute=[{...bar(0),t:Date.UTC(2026,10,16,12)}],q=projectNestedContext({minute,daily:[]},{selected:minute,minute:true});assert(q.rows.some(r=>r.grain==='daily'&&r.status==='missing'));
});
test('disjoint width baseline and net/share arithmetic are independent',()=>{
 const a=Array.from({length:10},(_,i)=>({...bar(i,i<5?10:11),l:i<5?9:8,h:i<5?11:14,o:i===5?10:11,c:11}));
 const r=project(a).rows.find(r=>r.selected);assert.equal(r.delta,1);assert.equal(r.shares,5000);assert.equal(r.movePerMillion,200);assert.equal(r.velocity,.2);assert(r.widthChangePct>0);
});
test('zero shares, zero range and unavailable baselines remain unknown',()=>{
 const a=Array.from({length:5},(_,i)=>({...bar(i),l:10,h:10,v:0})),r=project(a).rows[0];assert.equal(r.movePerMillion,null);assert.equal(r.positionPct,null);assert.equal(r.widthChangePct,null);assert.equal(r.fromHigh,0);
});
test('source data is immutable and appending future observations does not alter prior cutoff',()=>{
 const a=Array.from({length:30},(_,i)=>bar(i)),selected=a.slice(-5),before=JSON.stringify(a),p=project(a,selected);assert.equal(JSON.stringify(a),before);
 assert.deepEqual(project([...a,bar(30,999)],selected),p);
});
test('minute gaps and daily unknown continuity remain distinct',()=>{
 const daily=Array.from({length:10},(_,i)=>bar(i)),minute=[0,1,3].map(i=>({...bar(0),t:Date.UTC(2026,1,16,12)+i*60000}));
 const p=projectNestedContext({daily,minute},{selected:minute,minute:true});assert.equal(p.rows[0].gaps,1);assert.equal(p.rows.find(r=>r.grain==='daily').gaps,null);
});
test('structure requires confirmed pairs and uses independently selected neighbors',()=>{
 const a=[10,12,15,12,11,10,13,11,9,8,11,10,7,9,12,14,13,12].map((c,i)=>bar(i,c));
 const r=project(a,a,{pivotNeighbors:1}).rows[0];assert.notEqual(r.structureLabel,'insufficient confirmed pairs');assert.equal(r.pivotNeighbors,1);
 assert.equal(project(a.slice(-3)).rows[0].structureLabel,'insufficient confirmed pairs');
});
test('duplicate selected horizon is not presented as independent evidence',()=>{
 const a=Array.from({length:30},(_,i)=>bar(i)),p=project(a);assert.equal(p.rows.filter(r=>r.requested===5).length,1);assert(p.rows[0].selected);
});
test('ET dates handle DST and UTC midnight explicitly',()=>{assert.equal(contextEtDay(Date.UTC(2026,10,16,0)),'2026-11-15');assert.equal(contextEtDay(Date.UTC(2026,6,16,4)),'2026-07-16');});
test('invalid selection or pivot span fails explicitly',()=>{assert.throws(()=>projectNestedContext({},{selected:[]}));assert.throws(()=>project([bar(0)],undefined,{pivotNeighbors:0}));});
test('matrix renders signed negatives, unknowns and all available horizons',()=>{
 class Node{constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.ownerDocument=doc;this.textContent='';}appendChild(n){this.children.push(n);return n;}replaceChildren(){this.children=[];}setAttribute(k,v){this.attrs[k]=v;}}
 const doc={createElement:tag=>new Node(tag)},root=new Node('div'),p=project(Array.from({length:6},(_,i)=>({...bar(i,10-i/10),v:0})));
 renderNestedContext(root,p);const all=n=>[n,...n.children.flatMap(all)],nodes=all(root);assert(nodes.some(n=>n.tag==='td'&&n.textContent.includes('-')));assert(nodes.some(n=>n.textContent.includes('unknown')));assert.equal(nodes.filter(n=>n.tag==='tr').length,p.rows.length+1);
});
console.log(`${count} nested-context checks passed. Synthetic arithmetic/DOM only; no browser, source-clock or inference acceptance implied.`);
