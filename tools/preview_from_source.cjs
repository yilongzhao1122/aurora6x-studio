/* Lightweight drawing harness: executes the view's translated draw logic with
 * fixture data and records draw commands. NOT the Garmin VM or a runtime test. */
const fs=require('fs'),path=require('path');
const P=path.resolve(__dirname,'..');
const defaults=JSON.parse(fs.readFileSync(P+'/config.json'));
const fonts=JSON.parse(fs.readFileSync(P+'/tools/font-metrics.json'));
Number.prototype.toNumber=function(){return Math.trunc(this.valueOf())};
Number.prototype.toFloat=function(){return this.valueOf()};
Number.prototype.format=function(fmt){let n=this.valueOf(); if(fmt==='%.0f')return n.toFixed(0);if(fmt==='%.1f')return n.toFixed(1);if(fmt==='%02d')return String(Math.trunc(n)).padStart(2,'0');return String(n)};
Array.prototype.add=Array.prototype.push;
String.prototype.equals=function(other){return other!=null && (typeof other==='string' || other instanceof String) && this.toString()===other.toString()};
const Graphics={COLOR_TRANSPARENT:-1,TEXT_JUSTIFY_CENTER:1,TEXT_JUSTIFY_LEFT:0,ARC_CLOCKWISE:1};
const Rewrite=s=>s.replace(/\b(\w+) instanceof Lang\.Number/g,'(typeof $1 === \"number\" && Number.isInteger($1))').replace(/(?<!=)==(?!=)/g,'===').replace(/!=(?!=)/g,'!==').replace(/:(\w+)\s*=>/g,'"$1":').replace(/\bnull\b/g,'null').replace(/\.size\(\)/g,'.length').replace(/\.length\(\)/g,'.length').replace(/\b(\w+) has :(\w+)/g,'("$2" in $1)');
function build(file,globals,sourceOverride){
 let src=(sourceOverride??fs.readFileSync(P+'/source/'+file,'utf8')).replace(/\/\/[^\n]*/g,'').replace(/ as Lang\.[^;=\n]+/g,'');src=src.slice(src.indexOf('{')+1,src.lastIndexOf('}'));
 let obj={};let pos=0;const methods=[];
 while(pos<src.length){
  while(/\s/.test(src[pos]||'')&&pos<src.length)pos++;
  if(pos>=src.length)break;
  if(src.startsWith('var ',pos)){const end=src.indexOf(';',pos);const v=src.slice(pos+4,end);let eq=v.indexOf('=');let k=eq<0?v.trim():v.slice(0,eq).trim();obj[k]=eq<0?null:Function('return '+v.slice(eq+1))();pos=end+1;}
  else if(src.startsWith('function ',pos)){
   const m=/function\s+(\w+)\(([^)]*)\)\s*\{/.exec(src.slice(pos));if(!m)throw Error('parse');let start=pos+m[0].length,depth=1,i=start,quote=null;
   for(;i<src.length&&depth;i++){let c=src[i];if(quote){if(c===quote&&src[i-1]!=='\\')quote=null;}else if(c==='"'||c==="'")quote=c;else if(c==='{')depth++;else if(c==='}')depth--;}
   methods.push([m[1],m[2],src.slice(start,i-1)]);pos=i;
  }else throw Error('parse near '+src.slice(pos,pos+60));
 }
 for(const [name,args,body] of methods){obj[name]=Function(...Object.keys(globals),'return function('+args+'){with(this){'+Rewrite(body)+'}}')(...Object.values(globals));}
 return obj;
}
function render(overrides={},extra={}){
 const cfg={...defaults,...overrides};
 const values=[5680,8200,2.335,2253,6,68,75,28,98,14,12,1013,2335,65,35,45,175,2253,52,49,32.8,98,22,58,15,3.2,23,15,24,58];
 
 if(extra.missing)for(let i=0;i<values.length;i++)values[i]=null;
 if(extra.large)for(let i=0;i<values.length;i++)values[i]=123456;
 const fixture={refresh(){},lastRead:0,hr:values[5],hrLow:extra.missing?null:58,hrHigh:extra.missing?null:105,moonPhase:extra.phase??0.18,moveLevel:2,nextSun:1,nextSunIsRise:false,weather:extra.missing?null:{condition:extra.condition??3,windBearing:225},get(k){return values[k]},integer(v){return v==null?'--':v.toFixed(0)},text(k){return values[k]==null?'--':values[k].toFixed([2,13,20,25].includes(k)?1:0)},sunText(){return extra.missing?'--:--':'18:40'}};
 const System={println(){},getSystemStats:()=>({usedMemory:32000,freeMemory:extra.lowMemory?20000:80000,totalMemory:131072}),getClockTime:()=>({hour:extra.hour??8,min:52,sec:11}),getDeviceSettings:()=>({is24Hour:extra.is24??true,phoneConnected:true,doNotDisturb:false,alarmCount:1,notificationCount:2})};
 const Rez={Fonts:Object.fromEntries(Object.keys(fonts).map(k=>[k,k])),Drawables:Object.fromEntries(Array.from({length:33},(_,i)=>i).filter(i=>i!==4).map(k=>['Panel'+k,'panel'+k]))};
 const WatchUi={loadResource:x=>x,requestUpdate(){}};
 const Application={Properties:{getValue:k=>cfg[k]}};
 const Gregorian={info:()=>({year:2025,month:1,day:8,day_of_week:4})};const Time={now:()=>0};
 const global={Graphics,Math,System,WatchUi,Rez,Application,Gregorian,Time};
 global.FaceIcons=function(){return build('FaceIcons.mc',global)};
 global.Metrics=function(){return fixture};global.CalendarData=function(){return {refresh(){},lunar:'腊月初二',lunarEn:'L 12/2',term:'+5天 小寒',termEn:'ST1 +5d'}};
 const view=build('AuroraView.mc',global);view.WatchFace={initialize(){}};
 const commands=[];const dc={color:0,bg:0,pen:1,setColor(c,b){this.color=c;this.bg=b},setPenWidth(w){this.pen=w},getTextWidthInPixels(text,f){return [...text].reduce((s,c)=>s+(fonts[f].chars[c]?.a||0),0)},clear(){commands.push({op:'clear',color:this.bg})}};
 for(const name of ['drawText','drawLine','fillCircle','drawCircle','drawArc','fillRectangle','drawRectangle','fillEllipse','fillPolygon','drawPoint','drawBitmap'])dc[name]=function(...args){commands.push({op:name,args,color:this.color,pen:this.pen})};
 view.initialize();view.onLayout(dc);if(extra.sleep)view.onEnterSleep();view.onUpdate(dc);
 return {commands,cfg,extra};
}
if(require.main===module){
 fs.mkdirSync(P+'/docs/render',{recursive:true});
 for(const t of Array.from({length:33},(_,i)=>i).filter(i=>i!==4))fs.writeFileSync(P+'/docs/render/theme'+t+'.json',JSON.stringify(render({Backdrop:t},{hour:t===0?6:8})));
 fs.writeFileSync(P+'/docs/render/sleep.json',JSON.stringify(render({}, {sleep:true})));
 fs.writeFileSync(P+'/docs/render/missing.json',JSON.stringify(render({}, {missing:true})));
 let count=0;const schema=JSON.parse(fs.readFileSync(P+'/tools/settings-schema.json'));
 for(const [key,opts] of Object.entries(schema.options))for(let i=0;i<opts.length;i++){render({[key]:i});render({[key]:i},{missing:true,sleep:true});count+=2;}
 for(let h=0;h<24;h++){render({},{hour:h});render({},{hour:h,is24:false});count+=2;}
 for(const key of ['C2','C3','C4','C5'])for(let i=0;i<29;i++){render({[key]:i},{large:true});count++;}
 for(const rgb of [0,0xffffff,0x110044]){render({Backdrop:4,BackgroundColor:rgb});count++;}
 console.log('Drawing harness checks:',count,'states. This is not Garmin runtime validation.');
}
module.exports={render,build};
