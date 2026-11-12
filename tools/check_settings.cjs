// Validate the actual settings HTML's script with a minimal DOM/canvas stub.
// This checks behavior, not browser rendering.
const fs=require('fs'),vm=require('vm'),path=require('path');
const P=path.resolve(__dirname,'..');const defaults=JSON.parse(fs.readFileSync(P+'/config.json'));const schema=JSON.parse(fs.readFileSync(P+'/tools/settings-schema.json'));
const html=fs.readFileSync(P+'/设置助手.html','utf8');const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
let blob,clicks=0;const ctx2d=new Proxy({},{get:(o,k)=>k==='drawImage'?((img)=>{if(!img)throw Error("Missing rendered font/bitmap asset")}):()=>{}});const els={};
for(const k of [...Object.keys(defaults),'sleep','missing','twelve','face','status','download','savepng','reset'])els[k]={value:'',checked:false,textContent:'',addEventListener(){},getContext:()=>ctx2d};
const context={console,Blob,URL:{createObjectURL:b=>{blob=b;return 'blob:test'},revokeObjectURL(){}},setTimeout(){},Image:class{set src(v){this.onload()}},document:{getElementById:k=>els[k],querySelectorAll:()=>[],createElement:tag=>tag==='a'?{click(){clicks++}}:{getContext:()=>ctx2d}}};
vm.runInNewContext(script,context);
(async()=>{
 await new Promise(r=>setImmediate(r));
 if(!els.status.textContent.includes('示例数据'))throw Error('Preview initialization: '+els.status.textContent);
 els.Backdrop.value='0';els.C3.value='12';els.SecondOffset.value='-8';els.download.onclick();let got=JSON.parse(await blob.text());
 if(got.Backdrop!==0||got.C3!==12||got.SecondOffset!==-8)throw Error('Export types');
 const n=clicks;els.CustomText.value='中文';els.download.onclick();if(clicks!==n)throw Error('ASCII guard');
 els.reset.onclick();if(Number(els.Backdrop.value)!==defaults.Backdrop)throw Error('Reset');
 els.C2.value=29;els.download.onclick();if(clicks!==n)throw Error('Field bound');
 els.reset.onclick();els.BackgroundColor.value=16777216;els.download.onclick();if(clicks!==n)throw Error('RGB bound');
 els.reset.onclick();els.SecondOffset.value=0.5;els.download.onclick();if(clicks!==n)throw Error('Integer bound');
 const xml=fs.readFileSync(P+'/resources/settings/properties.xml','utf8');for(const[k,v]of Object.entries(defaults)){if(!xml.includes('id="'+k+'" type="'+(typeof v==='string'?'string':'number')+'">'+v+'</property>'))throw Error('Property mismatch '+k);}
 for(const [key,opts]of Object.entries(schema.options)){if(key.startsWith('C')&&['C2','C3','C4','C5'].includes(key)&&opts.length!==29)throw Error('Missing options');}
 console.log('PASS actual HTML: preview initialization, export numeric types, reset, ASCII guard, all ranges, XML/config consistency, four x 28 visible metrics (legacy IDs preserved).');
})().catch(e=>{console.error(e);process.exitCode=1});
