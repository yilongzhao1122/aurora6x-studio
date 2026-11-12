const {render}=require('./preview_from_source.cjs');const fs=require('fs'),assert=require('assert'),path=require('path');
const P=path.resolve(__dirname,'..');const scenes=[];
for(let i=0;i<6;i++)for(let h=0;h<24;h++)for(const is24 of [true,false]){
 const r=render({TimeTypeface:i,DataTypeface:i,Backdrop:13},{hour:h,is24});
 assert(r.commands.some(c=>c.op==='drawText'&&c.args[2]==='Time'+i));
 assert(r.commands.some(c=>c.op==='drawText'&&c.args[2]==='Sec'+i));
 scenes.push({...r,label:'font'+i+' hour'+h+' '+is24});
}
for(let i=0;i<6;i++)for(let metric=0;metric<29;metric++)for(const large of [false,true]){
 scenes.push({...render({TimeTypeface:i,DataTypeface:i,C2:metric,C3:metric,C4:metric,C5:metric},{large}),label:'font'+i+' metric'+metric+' large'+large});
}
fs.mkdirSync(P+'/docs/v330',{recursive:true});fs.writeFileSync(P+'/docs/v330/font-scenes.json',JSON.stringify(scenes));console.log('PASS '+scenes.length+' font/hour/metric source scenes.');
