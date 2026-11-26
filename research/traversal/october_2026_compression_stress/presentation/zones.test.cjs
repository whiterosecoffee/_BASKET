'use strict';
const assert=require('node:assert/strict');
const {projectZoneParticipation,renderZoneParticipation,highlightParticipationZone}=require('./zones.js');
let count=0;function test(name,fn){fn();count++;console.log('PASS '+name);}
const bar=(i,p=10,v=100)=>({t:i*60000,l:p-.1,h:p+.1,vw:p,v});
test('zone and block shares conserve total including invalid VWAP',()=>{
 const rows=[bar(0,10,1.25),bar(1,12,2.5),{...bar(2,11,3),vw:null},bar(3,10,4)],p=projectZoneParticipation(rows,{blocks:2});
 assert.equal(p.total,10.75);assert.equal(p.unallocated,3);assert.equal(p.zones.reduce((s,z)=>s+z.shares,0)+p.unallocated,p.total);
 p.parts.forEach((b,i)=>assert.equal(p.zones.reduce((s,z)=>s+z.cells[i].shares,0)+b.unallocated,b.total));
 assert.equal(p.zones.reduce((s,z)=>s+z.sharePct,0)+p.unallocatedPct,100);
});
test('fixed grid boundaries persist across backdrops and upper bound is exclusive',()=>{
 const rows=[bar(0,9.99),bar(1,10),bar(2,12)];const p=projectZoneParticipation(rows),q=projectZoneParticipation(rows.slice(1));
 assert.deepEqual(p.zones.find(z=>z.key===5).low,q.zones.find(z=>z.key===5).low);assert.equal(p.zones.find(z=>z.key===6).samples,1);
 assert.equal(p.zones.find(z=>z.key===4).samples,1);
});
test('binary price boundary noise does not place exact cents in lower zone',()=>{const p=projectZoneParticipation([bar(0,.3)],{width:.1});assert.equal(p.zones[0].key,3);});
test('minute gaps and invalid samples split episodes',()=>{
 const rows=[bar(0),bar(1),bar(3),{...bar(4),vw:99},bar(5)],p=projectZoneParticipation(rows,{cadenceMs:60000});
 assert.equal(p.discontinuities,1);assert.equal(p.zones[0].episodes,3);assert.equal(p.invalidSamples,1);
});
test('empty and zero-share denominators remain unknown',()=>{assert.equal(projectZoneParticipation([]).parts.length,0);const p=projectZoneParticipation([bar(0,10,0)]);assert.equal(p.zones[0].sharePct,null);assert.equal(p.zones[0].samplePct,100);});
test('uneven time partitions cover each observation once',()=>{
 for(let n=1;n<19;n++)for(let blocks=1;blocks<=8;blocks++){
  const p=projectZoneParticipation(Array.from({length:n},(_,i)=>bar(i,10+i%3,i+1)),{blocks});
  assert.equal(p.parts.reduce((s,b)=>s+b.samples,0),n);p.parts.forEach((b,i)=>assert.equal(p.zones.reduce((s,z)=>s+z.cells[i].samples,0)+b.invalidSamples,b.samples));
 }
});
test('invalid config and unordered input fail explicitly',()=>{
 for(const width of [0,-1,NaN,Infinity])assert.throws(()=>projectZoneParticipation([],{width}));
 assert.throws(()=>projectZoneParticipation([],{blocks:9}));assert.throws(()=>projectZoneParticipation([bar(1),bar(0)]));
 assert.throws(()=>projectZoneParticipation(Array.from({length:201},(_,i)=>bar(i,i+1)),{width:1}));
});
test('projection is deterministic and does not mutate source',()=>{const rows=[bar(0),bar(1,12)],before=JSON.stringify(rows);assert.deepEqual(projectZoneParticipation(rows),projectZoneParticipation(rows));assert.equal(JSON.stringify(rows),before);});
class Node{
 constructor(tag,doc){this.tag=tag;this.ownerDocument=doc;this.children=[];this.attrs={};this.events={};this.textContent='';}
 appendChild(n){this.children.push(n);return n;}replaceChildren(){this.children=[];}setAttribute(k,v){this.attrs[k]=String(v);}getAttribute(k){return this.attrs[k];}addEventListener(k,f){this.events[k]=f;}
 querySelector(selector){const attr=selector.slice(1,-1);for(const n of this.children){if(attr in n.attrs)return n;const hit=n.querySelector(selector);if(hit)return hit;}return null;}
 remove(){this.removed=true;}
}
const doc={createElement:tag=>new Node(tag,doc),createElementNS:(ns,tag)=>new Node(tag,doc)};
test('matrix selection is keyboard-native and invokes the exact zone key',()=>{
 const p=projectZoneParticipation([bar(0,10,0),bar(1,12,2)]),root=doc.createElement('div');let key=null;
 renderZoneParticipation(root,p,{selected:6,onSelect:k=>key=k});
 const walk=n=>[n,...n.children.flatMap(walk)],nodes=walk(root),button=nodes.find(n=>n.tag==='button');
 assert.equal(button.getAttribute('type'),'button');assert.equal(button.getAttribute('aria-pressed'),'true');button.events.click();assert.equal(key,6);
 assert(nodes.some(n=>n.textContent==='Unallocated'));assert(nodes.some(n=>n.textContent==='Total'));
 for(const mode of ['share','samples'])renderZoneParticipation(root,p,{mode});
});
test('selected zone highlight clips to chart frame and omits outside intervals',()=>{
 const svg=doc.createElement('svg'),frame=doc.createElement('rect');Object.entries({'data-chart-frame':'',x:64,y:20,width:200,height:100}).forEach(([k,v])=>frame.setAttribute(k,v));svg.appendChild(frame);
 const scale={y:p=>120-(p-10)*10};assert.equal(highlightParticipationZone(svg,scale,{low:8,high:12}),true);
 const r=svg.children.at(-1);assert.equal(r.getAttribute('y'),'100');assert.equal(r.getAttribute('height'),'20');
 assert.equal(highlightParticipationZone(svg,scale,{low:30,high:32}),false);assert.equal(r.removed,true);
});
console.log(`${count} zone projection/DOM checks passed. No actual browser or market-source acceptance implied.`);
