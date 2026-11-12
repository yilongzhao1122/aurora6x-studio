from pathlib import Path
import json,base64,re
P=Path(__file__).resolve().parents[1]
schema=json.loads((P/'tools/settings-schema.json').read_text(encoding='utf-8'))
files={'/config.json':(P/'config.json').read_text(encoding='utf-8'),'/tools/font-metrics.json':(P/'tools/font-metrics.json').read_text(encoding='utf-8')}
for n in ['AuroraView.mc','FaceIcons.mc']:files['/source/'+n]=(P/'source'/n).read_text(encoding='utf-8')
harness=(P/'tools/preview_from_source.cjs').read_text(encoding='utf-8');harness=harness[harness.index('const defaults='):harness.index('if(require.main===module)')]
assets={n:base64.b64encode((P/f'resources/fonts/{n}.png').read_bytes()).decode() for n in json.loads(files['/tools/font-metrics.json'])}
assets.update({f'panel{i}':base64.b64encode((P/f'resources/drawables/panel{i}.png').read_bytes()).decode() for i in [i for i in range(33) if i!=4]})
controls=''
for k,v in schema['defaults'].items():
 controls+=f'<label class="setting" for="{k}"><span>{schema["titles"][k]}</span>'
 if k in schema['options']:
  controls+=f'<select id="{k}">'+''.join(f'<option value="{i}">{t}</option>' for i,t in enumerate(schema['options'][k]) if not(k in ['C2','C3','C4','C5'] and i==17))+'</select>'
 elif k=='CustomText':controls+=f'<input id="{k}" maxlength="18" type="text">'
 else:
  lo,hi=schema['ranges'][k];controls+=f'<div class="numberrow"><input id="{k}" type="number" step="1" min="{lo}" max="{hi}">'
  if 'Color' in k:controls+=f'<input aria-label="{k} color picker" type="color" data-for="{k}">'
  controls+='</div>'
 controls+='</label>'
html=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Aurora 6X Studio · 设置与预览</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0c1119;color:#e5edf8;font:15px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1180px;margin:auto;padding:30px}header{margin-bottom:28px}h1{font-size:30px;letter-spacing:-1px;margin:4px 0}p{color:#adbbcd}.tag{color:#8fe8f0;letter-spacing:2px;font-size:12px}.layout{display:grid;grid-template-columns:410px 1fr;gap:32px}.preview{position:sticky;top:20px;align-self:start;background:#141c28;border:1px solid #273345;border-radius:22px;padding:24px;text-align:center}canvas{width:340px;height:340px;max-width:100%;border-radius:50%;border:12px solid #242e3a;box-shadow:0 0 0 1px #62707d,0 10px 35px #0009;image-rendering:pixelated;margin:18px 0}.controls{background:#141c28;border:1px solid #273345;border-radius:22px;padding:25px}.setting{display:block;margin-bottom:17px}.setting>span{display:block;color:#c9d5e5;font-size:13px;margin-bottom:6px}select,input{width:100%;padding:11px;border:1px solid #35465a;background:#0d1521;color:#f0f5fc;border-radius:9px;font:inherit}input[type=color]{width:52px;height:47px;padding:3px}.numberrow{display:flex;gap:8px}button{border:1px solid #405469;background:#213145;color:#edf6ff;border-radius:9px;padding:10px 14px;cursor:pointer;font:inherit}button:hover{background:#334962}.actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:12px 0}.primary{background:#9eeaf0;color:#10212b;font-weight:700;border:0}.primary:hover{background:#d1faff}.hint{font-size:12px;color:#93a7bf}.toggle{display:inline-flex;gap:6px;margin:4px 8px;font-size:13px}.toggle input{width:auto}.status{min-height:28px;color:#8fe8f0;font-size:13px}.warning{color:#ffcc8b;text-align:left;font-size:13px;border-top:1px solid #304057;padding-top:14px}a{color:#98e6f0}.legend{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:14px;font-size:11px;color:#a6b6cc}.legend b{color:#e9f2fc}@media(max-width:850px){main{padding:15px}.layout{grid-template-columns:1fr}.preview{position:static}canvas{width:300px;height:300px}}
</style><main><header><div class="tag">AURORA 6X · STUDIO 3.3.2</div><h1>把表盘调成你喜欢的样子</h1><p>按附件栏位组织全部选项。左侧是绘图源码驱动的示例预览，不是模拟器截图，也不是实时手表数据。</p></header><div class="layout"><section class="preview"><canvas id="face" width="280" height="280" aria-label="表盘预览"></canvas><div class="actions"><button data-preset="rose">玫红参考</button><button data-preset="silver">冰蓝参考</button><button data-preset="diagnostic">数据核对</button><button id="reset">恢复默认</button></div><div><label class="toggle"><input type="checkbox" id="sleep">低功耗</label><label class="toggle"><input type="checkbox" id="missing">无传感器数据</label><label class="toggle"><input type="checkbox" id="twelve">12小时制</label></div><div class="actions"><button class="primary" id="download">导出 config.json</button><button id="savepng">保存预览图</button></div><div class="status" id="status"></div><div class="hint">将下载的 config.json 放回项目文件夹，替换同名文件，再运行 01_Run_Simulator.cmd。已有模拟器设置可能覆盖编译默认值，详见 docs/使用说明.md。</div><div class="legend"><span><b>A0</b> 顶栏</span><span><b>A1 / A3</b> 左右图标</span><span><b>A2 / A4</b> 上方数据</span><span><b>B2</b> 秒数</span><span><b>C0</b> 斜条进度</span><span><b>C1</b> 可选数据圆环</span><span><b>C2 / C4</b> 数据第一行</span><span><b>C3 / C5</b> 数据第二行</span><span><b>C6</b> 底栏</span></div><p class="warning">部分数据取决于设备与权限；演示数字不保证实际手表可提供。热量只显示设备直接提供的当天总消耗；不计算运动或静息热量；月跑量只汇总设备公开的记录。中文自定义短句尚未开放，农历/日期/节气均支持中文。太阳能项对应官方 solarIntensity（0–100），不是电池增加的百分比。血氧优先当前值，否则显示最近有效测量；并非持续测量。</p><a href="docs/使用说明.md">打开详细操作教程 →</a> · <a href="手表端设置.html">手表按键设置 →</a></section><section class="controls">CONTROLS</section></div></main><script>
const FILES=FILES_JSON;const P='';const fs={readFileSync:p=>FILES[p]};
HARNESS
const SCHEMA=SCHEMA_JSON;const encoded=ASSETS_JSON;const images={};
const $=id=>document.getElementById(id);
function values(){const out={};for(const [k,v] of Object.entries(defaults)){out[k]=typeof v==='string'?$(k).value:Number($(k).value);}return out;}
function validate(c){for(const [k,v] of Object.entries(c)){if(k==='CustomText'){if(v.length>18||/[^\x20-\x7e]/.test(v))throw Error('自定义内容请使用 18 字符以内的英文、数字或标点。');continue;}if(!Number.isInteger(v))throw Error(k+' 必须是整数。');const r=SCHEMA.options[k]?[0,SCHEMA.options[k].length-1]:SCHEMA.ranges[k];if(v<r[0]||v>r[1])throw Error(k+' 超出范围。');}return c;}
function setValues(c){for(const [k,v]of Object.entries(c))$(k).value=(['C2','C3','C4','C5'].includes(k)&&v===17)?3:v;for(const cp of document.querySelectorAll('[data-for]'))cp.value='#'+Number($(cp.dataset.for).value).toString(16).padStart(6,'0');}
function css(c){return 'rgb('+[(c>>16)&255,(c>>8)&255,c&255].map(x=>Math.round(x/85)*85).join(',')+')'}
function paint(commands){const ctx=$('face').getContext('2d');ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,280,280);ctx.save();ctx.beginPath();ctx.arc(140,140,140,0,Math.PI*2);ctx.clip();
 for(const c of commands){let a=c.args||[];ctx.fillStyle=css(c.color);ctx.strokeStyle=css(c.color);ctx.lineWidth=c.pen||1;ctx.lineCap='butt';
  switch(c.op){case 'clear':ctx.fillRect(0,0,280,280);break;case 'drawBitmap':ctx.drawImage(images[a[2]],a[0],a[1]);break;
   case 'drawText':{let[x,y,f,text,j]=a;const meta=fonts[f];if(j===1)x-=Math.floor([...text].reduce((s,ch)=>s+(meta.chars[ch]?.a||0),0)/2);for(const ch of text){const m=meta.chars[ch];if(!m)continue;const tmp=document.createElement('canvas');tmp.width=m.w;tmp.height=m.h;const tc=tmp.getContext('2d');tc.drawImage(images[f],m.x,m.y,m.w,m.h,0,0,m.w,m.h);tc.globalCompositeOperation='source-in';tc.fillStyle=css(c.color);tc.fillRect(0,0,m.w,m.h);ctx.drawImage(tmp,Math.round(x+m.xo),Math.round(y+m.yo));x+=m.a;}break;}
   case 'drawLine':ctx.beginPath();ctx.moveTo(a[0]+.5,a[1]+.5);ctx.lineTo(a[2]+.5,a[3]+.5);ctx.stroke();break;
   case 'drawPoint':ctx.fillRect(a[0],a[1],1,1);break;
   case 'fillRectangle':ctx.fillRect(...a);break;case 'drawRectangle':ctx.strokeRect(a[0]+.5,a[1]+.5,a[2]-1,a[3]-1);break;
   case 'drawCircle':case 'fillCircle':ctx.beginPath();ctx.arc(a[0],a[1],a[2],0,Math.PI*2);c.op==='fillCircle'?ctx.fill():ctx.stroke();break;
   case 'fillEllipse':ctx.beginPath();ctx.ellipse(a[0],a[1],a[2],a[3],0,0,Math.PI*2);ctx.fill();break;
   case 'fillPolygon':ctx.beginPath();a[0].forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.fill();break;
   case 'drawArc':{let[x,y,r,di,start,end]=a;let ext=(start-end+360)%360;ctx.beginPath();ctx.arc(x,y,r,-start*Math.PI/180,(-start+ext)*Math.PI/180);ctx.stroke();break;}
  }
 }ctx.restore();}
function refresh(){try{const c=validate(values());const result=render(c,{sleep:$('sleep').checked,missing:$('missing').checked,is24:!$('twelve').checked,hour:$('twelve').checked?20:8});paint(result.commands);$('status').textContent='示例数据 · 修改实时预览';}catch(e){$('status').textContent=e.message;}}
function save(blob,name){const u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
$('download').onclick=()=>{try{save(new Blob([JSON.stringify(validate(values()),null,2)+'\n'],{type:'application/json'}),'config.json');$('status').textContent='已导出。请替换项目中的 config.json。';}catch(e){$('status').textContent=e.message;}};
$('savepng').onclick=()=>$('face').toBlob(b=>save(b,'Aurora6X_preview.png'));
$('reset').onclick=()=>{setValues(defaults);refresh();};
for(const b of document.querySelectorAll('[data-preset]'))b.onclick=()=>{setValues({...defaults,...(b.dataset.preset==='diagnostic'?{Backdrop:5,A0:0,A1:0,A3:3,A4:1,C2:5,C3:12,C4:14,C5:8,C6:1,DebugLog:1}:b.dataset.preset==='rose'?{Backdrop:0,A0:1,C6:5}:{Backdrop:2,A0:0,C6:2})});refresh();};
for(const cp of document.querySelectorAll('[data-for]'))cp.oninput=()=>{$(cp.dataset.for).value=parseInt(cp.value.substring(1),16);if(cp.dataset.for==='BackgroundColor')$('Backdrop').value=4;refresh();};
for(const el of document.querySelectorAll('.controls input,.controls select,#sleep,#missing,#twelve'))el.addEventListener('input',refresh);
setValues(defaults);
Promise.all(Object.entries(encoded).map(([n,b])=>new Promise((resolve,reject)=>{let im=new Image();im.onload=()=>{images[n]=im;resolve()};im.onerror=reject;im.src='data:image/png;base64,'+b;}))).then(refresh).catch(()=>{$('status').textContent='预览资源载入失败，请重新打开完整 HTML 文件。'});
</script></html>'''
for a,b in [('CONTROLS',controls),('FILES_JSON',json.dumps(files,ensure_ascii=False)),('HARNESS',harness),('SCHEMA_JSON',json.dumps(schema,ensure_ascii=False)),('ASSETS_JSON',json.dumps(assets))]:html=html.replace(a,b)
(P/'设置助手.html').write_text(html,encoding='utf-8')
print('Created self-contained settings page:',len(html),'characters')
