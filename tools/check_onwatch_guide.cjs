// Test the actual guide script using DOM doubles; this is not browser layout validation.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const P=path.resolve(__dirname,'..');const html=fs.readFileSync(P+'/手表端设置.html','utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
const entries=JSON.parse(fs.readFileSync(P+'/docs/field-map-data.json','utf8'));
const catalog=JSON.parse(fs.readFileSync(P+'/tools/onwatch-catalog.json','utf8'));
function el(tag='div',cl=[],key){const classes=new Set(cl);return {tagName:tag,dataset:{key},children:[],textContent:'',attrs:{'aria-pressed':'false'},handlers:{},className:'',classList:{contains:k=>classes.has(k),toggle(k,on){on?classes.add(k):classes.delete(k)}},hasAttribute:k=>k==='aria-pressed',setAttribute(k,v){this.attrs[k]=v},append(x){this.children.push(x)},replaceChildren(){this.children=[]},addEventListener(k,v){this.handlers[k]=v},scrollIntoView(){this.scrolled=true}}}
const ids=Object.fromEntries(['detail-title','detail-tag','detail-position','detail-path','detail-options','detail-note','map'].map(k=>[k,el()]));
const nodes=entries.flatMap(e=>[el('g',['slot'],e.key),el('button',['key-chip'],e.key),el('button',['table-key'],e.key)]);
const rows=entries.map(e=>el('tr',[],e.key));rows.forEach(r=>r.dataset.row=r.dataset.key);
const document={getElementById:k=>ids[k],querySelectorAll:q=>q==='[data-key]'?nodes:rows,createElement:tag=>el(tag),createTextNode:text=>({textContent:text})};
vm.runInNewContext(script,{document});
for(const e of entries){
 const key=nodes.find(n=>n.dataset.key===e.key&&n.classList.contains('key-chip'));key.handlers.click();
 assert.equal(ids['detail-title'].textContent,e.key+' · '+e.name);assert.equal(ids['detail-options'].children.length,e.options.length);
 assert.equal(nodes.filter(n=>n.attrs['aria-pressed']==='true').length,3);
 if(!e.fixed){const name=['C2','C3','C4','C5'].includes(e.key)?'Metrics':e.key;assert.deepEqual(e.options,catalog.resources['MenuOptions'+name]);}
 assert(html.includes('data-row="'+e.key+'"'));assert(html.includes('aria-label="'+e.key+' '+e.name+'"'));
}
const a1=nodes.find(n=>n.dataset.key==='A1'&&n.tagName==='g');let prevented=false;a1.handlers.keydown({key:'Enter',preventDefault(){prevented=true}});assert(prevented);assert.equal(ids['detail-options'].children.length,4);
nodes.find(n=>n.dataset.key==='C5'&&n.classList.contains('table-key')).handlers.click();assert(ids.map.scrolled);assert.equal(ids['detail-options'].children.length,28);
assert.equal(entries.filter(e=>e.fixed).map(e=>e.key).join(','),'B0,B1,B3');
assert.equal(entries.filter(e=>e.options.length===28).map(e=>e.key).sort().join(','),'C2,C3,C4,C5');
console.log('PASS actual guide script: 16 fields, click/key navigation, active states, exact menu-resource options, fixed fields, table-to-map link. DOM doubles only; no browser layout claim.');
