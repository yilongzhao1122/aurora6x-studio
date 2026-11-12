// Execute the actual Monkey C navigation and drawing source with API doubles.
// This is NOT a Garmin VM, device firmware, or runtime memory measurement.
const {build}=require('./preview_from_source.cjs');
const fs=require('fs'),path=require('path'),assert=require('assert');
const P=path.resolve(__dirname,'..');
const schema=JSON.parse(fs.readFileSync(P+'/tools/settings-schema.json'));
const catalog=JSON.parse(fs.readFileSync(P+'/tools/onwatch-catalog.json'));
const metrics=JSON.parse(fs.readFileSync(P+'/tools/font-metrics.json'));
const Rez={JsonData:Object.fromEntries(Object.keys(catalog.resources).map(k=>[k,k])),Fonts:{Menu:'Menu'}};
// JSON/resource strings are separate objects, not JS primitive strings.
// Together with strict reference equality in build(), this exposes the old == bug.
const boxStrings=v=>typeof v==='string'?new String(v):(Array.isArray(v)?v.map(boxStrings):v);
const readResource=id=>boxStrings(JSON.parse(fs.readFileSync(P+'/resources/onwatch/'+id+'.json','utf8')));
const expectedCounts={A0:7,A1:4,A2:5,A3:4,A4:3,C0:4,C1:4,C2:28,C3:28,C4:28,C5:28,C6:7,B2:2,Language:2,Backdrop:33,SecondOffset:47,TimeTypeface:6,DataTypeface:6};
let props={...schema.defaults},saved=0,fail=false,ignoreWrite=false,updates=0;
let commands=[];const graphics={COLOR_TRANSPARENT:-1,TEXT_JUSTIFY_CENTER:1};
const Application={Properties:{getValue:k=>props[k]??null,setValue(k,v){if(fail)throw Error('disk');if(!ignoreWrite){props[k]=v;saved++}}},loadResource:readResource,getApp:()=>({onSettingsChanged(){updates++}})};
const WatchUi={loadResource:id=>id,requestUpdate(){}};
const env={Application,WatchUi,Rez,Graphics:graphics,System:{println(){}}};
function editor(sourceOverride){const v=build('AuroraSettingsView.mc',env,sourceOverride);v.View={initialize(){}};v.initialize();return v;}
const dc={color:0,bg:0,setColor(c,b){this.color=c;this.bg=b},getTextWidthInPixels(s,f){return [...s].reduce((n,c)=>{assert(metrics[f].chars[c],`Missing glyph ${c}`);return n+metrics[f].chars[c].a},0)},clear(){commands.push({op:'clear',color:this.bg})}};
for(const k of ['drawText','fillRectangle','fillCircle'])dc[k]=function(...args){commands.push({op:k,args,color:this.color,pen:1})};
function draw(v){commands=[];v.onUpdate(dc);for(const c of commands){if(c.op==='drawText'){const[x,y,f,s]=c.args;let w=dc.getTextWidthInPixels(s,f);assert(x-w/2>=20 && x+w/2<=260,`Text width ${s}`);assert(y>=20 && y+22<=264);}}return {commands:structuredClone(commands)};}
const R=P+'/docs/render';fs.mkdirSync(R,{recursive:true});
function snap(v,n){fs.writeFileSync(R+'/menu-'+n+'.json',JSON.stringify(draw(v)));}
// Mutation check: restore the old string comparisons, then reproduce the defect.
const currentSource=fs.readFileSync(P+'/source/AuroraSettingsView.mc','utf8');
const oldComparisons=currentSource.replace(/key\.equals\(("[^"\n]+")\)/g,'key==$1').replace('var id=null;','var id=Rez.JsonData.MenuOptionsMetrics;');
let broken=editor(oldComparisons);broken.choose();broken.choose();
assert.equal(String(broken.key),'A0');assert.equal(broken.count(),28,'Old A0 must reproduce 29-list bug');
assert.notEqual(broken.count(),expectedCounts.A0);
console.log('REPRODUCED old bug: allocated resource key A0 incorrectly opens the generic metric options.');
let fixed=editor();fixed.choose();fixed.choose();assert.equal(fixed.count(),7);
fixed.key=new String('UnknownField');assert.equal(fixed.loadOptions(),false);assert.equal(fixed.options,null);
let checks=0;
for(const lang of [0,1]){
 props.Language=lang;let v=editor();snap(v,'root-'+lang);
 for(let group=0;group<3;group++){
  v.group=group;v.choose();assert.equal(v.level,1);assert.equal(v.rows.length,catalog.groups[group].length);draw(v);
  for(let row=0;row<v.rows.length;row++){
   v.row=row;const key=v.rows[row][0].toString();v.choose();assert.equal(v.level,2);
   const metric=['C2','C3','C4','C5'].includes(key);const encode=i=>metric&&i>=17?i+1:i;const decode=v=>metric?(v===17?3:v>17?v-1:v):v;
   const expected=expectedCounts[key];assert.equal(v.count(),expected,key);assert.equal(v.count(),expectedCounts[key],key+' independent contract');
   if(key!=='SecondOffset'){
    const list=['C2','C3','C4','C5'].includes(key)?'Metrics':key;
    assert.deepEqual(v.options.map(row=>row.map(String)),catalog.resources['MenuOptions'+list],key+' content');
   }
   const old=props[key];assert.equal(v.choice,key==='SecondOffset'?old+23:decode(old));
   // Merely browsing then BACK must not write.
   let n=saved;v.move(1);v.back();assert.equal(saved,n);assert.equal(props[key],old);assert.equal(v.row,row);
   v.choose();
   for(let i=0;i<expected;i++){
    v.choice=i;draw(v);v.choose();assert.equal(v.notice,1);assert.equal(props[key],key==='SecondOffset'?i-23:encode(i));assert.equal(v.selected,i);draw(v);checks++;
   }
   // Wrapping and re-entry use the persistent property.
   v.choice=0;v.move(-1);assert.equal(v.choice,expected-1);v.move(1);assert.equal(v.choice,0);
   v.back();v.choose();assert.equal(v.choice,expected-1);v.back();assert.equal(v.options,null);
  }
  v.back();assert.equal(v.level,0);assert.equal(v.rows,null);assert.equal(v.group,group);
 }
 assert.equal(v.back(),false);assert.equal(v.level,0);
}
// Save errors and failed readback never show a false success/current marker.
props={...schema.defaults};let v=editor();v.group=1;v.choose();v.row=2;v.choose();assert.equal(v.key,'C2');snap(v,'metrics');
v.choice=8;fail=true;v.choose();assert.equal(v.notice,2);assert.equal(props.C2,0);assert.equal(v.selected,0);fail=false;
ignoreWrite=true;v.choose();assert.equal(v.notice,2);assert.equal(v.selected,0);ignoreWrite=false;
v.choose();assert.equal(v.notice,1);assert.equal(props.C2,8);snap(v,'saved');
v.onHide();assert.equal(v.font,null);draw(v);assert.equal(v.font,'Menu');
let fresh=editor();fresh.group=1;fresh.choose();fresh.row=2;fresh.choose();assert.equal(fresh.choice,8);
// Corrupt/out-of-range choice recovers without crashing or marking a wrong value.
props.C2=100;fresh=editor();fresh.group=1;fresh.choose();fresh.row=2;fresh.choose();assert.equal(fresh.selected,-1);assert.equal(fresh.choice,0);draw(fresh);
// Missing/wrong-type values must not crash, and illegal choice must never write.
for(const bad of [null,'bad',2.5,-1,100]){
 props.C2=bad;const safe=editor();safe.group=1;safe.choose();safe.row=2;safe.choose();
 assert.equal(safe.selected,-1);assert.equal(safe.choice,0);
 const before=saved;safe.choice=29;safe.choose();assert.equal(safe.notice,2);assert.equal(saved,before);
}
// Offset and Language must use the same content comparison, including immediate change.
props={...schema.defaults};const offset=editor();offset.group=2;offset.choose();offset.row=3;offset.choose();
assert.equal(offset.count(),47);offset.choice=0;offset.choose();assert.equal(props.SecondOffset,-23);
offset.choice=46;offset.choose();assert.equal(props.SecondOffset,23);offset.back();offset.row=1;offset.choose();
offset.choice=1;offset.choose();assert.equal(offset.language,1);
// Real delegate mappings.
let popped=0;const d=build('AuroraSettingsDelegate.mc',{WatchUi:{SLIDE_IMMEDIATE:0,popView(){popped++}}});d.BehaviorDelegate={initialize(){}};d.initialize(fresh);d.onNextPage();assert.equal(fresh.choice,1);d.onPreviousPage();assert.equal(fresh.choice,0);d.onBack();assert.equal(fresh.level,1);d.onBack();assert.equal(fresh.level,0);assert.equal(popped,0);d.onBack();assert.equal(popped,1);
// Face resource release and reload use source, not a duplicated implementation.
const face=build('AuroraView.mc',{WatchUi:{loadResource:x=>x},Rez:{Fonts:{Small:'small',SmallPlus:'smallPlus',Ring2:'ring',Data2:'medium',Time0:'time',Sec0:'seconds'}}});
face.settings={TimeTypeface:0,DataTypeface:2};face.icons={small:'is',large:'il',load(){this.small='is';this.large='il'}};face.panelImage={};face.small='small';face.smallPlus='smallPlus';face.ringFont='ring';face.releaseGraphics();
assert.equal(face.panelImage,null);assert.equal(face.small,null);assert.equal(face.smallPlus,null);assert.equal(face.ringFont,null);assert.equal(face.icons.large,null);face.onLayout(dc);assert.equal(face.smallPlus,'smallPlus');assert.equal(face.ringFont,'ring');assert.equal(face.timeFont,'time');assert.equal(face.icons.large,'il');
console.log(`PASS ${checks} bilingual option saves/draws; persistence, BACK cancel, re-entry, wrapping, readback/errors, delegate buttons, missing glyphs, text bounds, resource release/reload. Not Garmin runtime validation.`);

const {render}=require('./preview_from_source.cjs');
function faceSettings(overrides){const f=build('AuroraView.mc',{Application:{Properties:{getValue:k=>({...schema.defaults,...overrides})[k]}}});f.loadSettings();return f.settings;}
for(const key of Object.keys(expectedCounts).filter(k=>!['TimeTypeface','DataTypeface'].includes(k))){
 for(const bad of [-999,999,null,'bad',1.5]){
  const r=render({[key]:bad});assert(r.commands.length>0,key+' handles legacy invalid setting');assert.equal(faceSettings({[key]:bad})[key],schema.defaults[key],key+' invalid choice fallback');
 }
}
for(const key of ['A0','A1','A2','A3','A4','C0','C1','C6','B2','Language','Backdrop']){
 const list=catalog.resources['MenuOptions'+key];
 for(let i=0;i<list.length;i++){assert.equal(faceSettings({[key]:i})[key],i,key+' preserves valid setting');}
}
console.log('PASS explicit per-field option counts/content, allocated strings, legacy invalid values, offset/language, unknown-key and invalid-save protection.');

props={...schema.defaults,C5:17};let legacy=editor();legacy.group=1;legacy.choose();legacy.row=5;legacy.choose();assert.equal(String(legacy.key),'C5');assert.equal(legacy.selected,3);legacy.choose();assert.equal(props.C5,3);
console.log('PASS old active-calorie slot maps to Total; metric choices omit old ID17 and preserve all remaining IDs.');
