const {render}=require('./preview_from_source.cjs'),fs=require('fs'),path=require('path'),assert=require('assert');
const P=path.resolve(__dirname,'..');const out=[];
for(let b=13;b<=32;b++)for(let h=0;h<24;h++)for(const is24 of [true,false]){
 const r=render({Backdrop:b},{hour:h,is24});const bitmaps=r.commands.filter(c=>c.op==='drawBitmap');assert.equal(bitmaps.length,1);assert.equal(bitmaps[0].args[2],'panel'+b);
 out.push({theme:b,hour:h,is24,text:r.commands.filter(c=>c.op==='drawText'&&c.color===0)});
 const f=render({Backdrop:b},{lowMemory:true});assert(!f.commands.some(c=>c.op==='drawBitmap'));
}
fs.writeFileSync(P+'/docs/theme-validation/text-scenes.json',JSON.stringify(out));console.log('PASS 960 theme/clock combinations; matching bitmap IDs and low-memory fallback. Not Garmin runtime validation.');
