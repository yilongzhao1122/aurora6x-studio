const {render}=require('./preview_from_source.cjs'),assert=require('assert'),fs=require('fs'),path=require('path');
const P=path.resolve(__dirname,'..');let count=0;
for(let condition=0;condition<54;condition++){
 const r=render({A1:0,A3:0},{condition});
 for(const c of r.commands){assert(Number.isFinite(c.color),'undefined colour');if(c.op==='drawText')assert(typeof c.args[3]==='string');}
 const weatherIcons=r.commands.filter(c=>c.op==='drawText'&&c.args[2]==='Icons24');assert.equal(weatherIcons.length,2);
 if(condition===0)assert.equal(weatherIcons[0].args[3].codePointAt(0)-0xe000,39);
 if(condition===8)assert.equal(weatherIcons[0].args[3].codePointAt(0)-0xe000,36);
 if(condition===29)assert.equal(weatherIcons[0].args[3].codePointAt(0)-0xe000,36);
 if(condition===53)assert.equal(weatherIcons[0].args[3].codePointAt(0)-0xe000,37);
 count++;
}
for(let i=0;i<8;i++){const r=render({A3:3},{phase:i/8});fs.writeFileSync(P+'/docs/render/moon'+i+'.json',JSON.stringify(r));count++;}
let r=render();assert(r.commands.some(c=>c.op==='drawText'&&c.args[3]==='5680'&&c.color===0xffffff));
assert(!r.commands.some(c=>c.op==='fillEllipse'),'Icons must use bounded native glyphs');
console.log('PASS weather conditions / moon display cases:',count,'and visible metric ink.');

for(const b of Array.from({length:33},(_,i)=>i).filter(i=>i!==4)){const r=render({Backdrop:b},{lowMemory:true});assert(!r.commands.some(c=>c.op==='drawBitmap'));assert(r.commands.some(c=>c.op==='fillPolygon'));assert(r.commands.some(c=>c.op==='drawText'&&c.args[3]==='5680'));}
console.log('PASS 32 low-memory background fallback paths: no bitmap load/draw, data remains visible.');
