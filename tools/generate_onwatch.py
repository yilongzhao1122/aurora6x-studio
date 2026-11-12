"""Generate compact bilingual settings resources and a settings-only bitmap font.
Run this instead of generate_assets.py, then run generate_icons.py.
Only the current group's rows and current field's choices are loaded on watch.
"""
from pathlib import Path
import json,runpy
P=Path(__file__).resolve().parents[1]
base=runpy.run_path(str(P/'tools/generate_assets.py'))
schema=base['spec']
# Short labels fit a native 280px round screen; English is on a separate line.
labels={
 'A0':['顶部数据','Top strip'],'A1':['左侧图标','Left icon'],'A2':['上方中央数据','Upper center'],
 'A3':['右侧图标','Right icon'],'A4':['右上组合数据','Paired data'],'C0':['彩条进度','Progress bars'],
 'C1':['左下圆环','Lower left ring'],'C2':['第一行左侧','Row 1 left'],'C4':['第一行右侧','Row 1 right'],
 'C3':['第二行左侧','Row 2 left'],'C5':['第二行右侧','Row 2 right'],'C6':['底部数据','Bottom strip'],
 'B2':['秒钟显示','Seconds'],'Language':['界面语言','Language'],'Backdrop':['表盘背景','Backdrop'],
 'SecondOffset':['第二时间时差','Second time offset'],'TimeTypeface':['时间数字字体','Time typeface'],'DataTypeface':['数据数字字体','Data typeface']}
strip=[['电池电量','Battery'],['系统图标','System icons'],['天气气温','Temperature'],['农历','Lunar date'],['节气','Solar terms'],['第二时间','Second time'],['下个日出日落','Next sunrise / sunset']]
icons=[['天气','Weather'],['风向','Wind direction'],['久坐提醒','Move bar'],['月相','Moon phase']]
metrics=[['步数','Steps'],['目标步数','Steps goal'],['里程','Distance (km)'],['总热量','Total calories'],['台阶','Floors'],['心率','Heart rate'],['身体电量','Body Battery'],['压力','Stress'],['血氧','Oxygen (%)'],['呼吸频率','Respiration'],['恢复时间','Recovery (hours)'],['海平面气压','Sea-level pressure'],['海拔','Altitude (m)'],['体重','Weight (kg)'],['太阳能强度','Solar intensity'],['当天活动分钟','Active minutes today'],['本周活动分钟','Active minutes week'],['总消耗热量','Total calories'],['骑行最大摄氧量','Cycling VO2max'],['跑步最大摄氧量','Running VO2max'],['月跑量已有记录','Month run: known records'],['电池电量','Battery (%)'],['天气气温','Temperature'],['湿度','Humidity (%)'],['降水概率','Rain probability'],['风速','Wind (m/s)'],['体感温度','Feels like'],['最低气温','Low temperature'],['最高气温','High temperature']]
opts={'A0':strip,'A1':icons,'A2':[['湿度与降水概率','Humidity / Rain']]+strip[2:6], 'A3':icons,
 'A4':[['最低最高心率','Heart rate low / high'],['步数与目标','Steps / Goal'],['总消耗热量','Total calories']],
 'C0':[strip[0],metrics[0],metrics[6],metrics[7]],'C1':[metrics[5],metrics[6],metrics[7],strip[0]],
 'Metrics':metrics[:17]+metrics[18:],'C6':strip[1:]+[['用户自定义内容','Custom text']],
 'B2':[['抬手显示秒钟','Seconds while awake'],['隐藏秒钟','Hide seconds']],
 'Language':[['中文','Chinese'],['英文','English']],
 'Backdrop':[[a,b] for a,b in zip(['玫红渐变','冰蓝折面','银白流线','香槟渐变','自定义背景色','薄荷切片','珊瑚色块','紫晶轨道','柠檬赛道','冰川网格','落日拼色','纸白蓝图','青紫双翼'],['Rose','Ice facets','Silver lines','Champagne','Custom color','Mint slices','Coral blocks','Amethyst','Citrus track','Glacier grid','Sunset blocks','Paper blueprint','Cyan lilac'])]}
opts['Backdrop'] += [['AI'+str(t['id'])+' '+t['zh'],t['en']] for t in json.loads((P/'tools/ai-theme-catalog.json').read_text())]
opts.update({'TimeTypeface':[[x,x] for x in schema['options']['TimeTypeface']],'DataTypeface':[[x,x] for x in schema['options']['DataTypeface']]})
groups=[['A0','A1','A2','A3','A4'],['C0','C1','C2','C4','C3','C5','C6'],['B2','Language','Backdrop','SecondOffset','TimeTypeface','DataTypeface']]
R=P/'resources/onwatch';R.mkdir(exist_ok=True)
resources={}
for i,keys in enumerate(groups):resources['MenuGroup'+str(i)]=[[k,*labels[k],schema['defaults'][k]] for k in keys]
for k,v in opts.items():resources['MenuOptions'+k]=v
for k,v in resources.items():(R/(k+'.json')).write_text(json.dumps(v,ensure_ascii=False,separators=(',',':')))
(R/'resources.xml').write_text('<resources>\n'+''.join(f'<jsonData id="{k}" filename="{k}.json"/>\n' for k in resources)+'</resources>')
extra=(P/'source/AuroraSettingsView.mc').read_text()+'表盘设置顶部与图标下方数据时间与外观选择返回保存已保存失败重试当前中文英文小时上次成功生效按键栏目'
chars=''.join(chr(i) for i in range(32,127))+''.join(sorted({c for c in json.dumps(resources,ensure_ascii=False)+extra if ord(c)>127}))
from typography import build_typography
build_typography(P,base['font_meta'],chars)
meta=base['font_meta']
(P/'resources/fonts/fonts.xml').write_text('<fonts>'+''.join(f'<font id="{n}" filename="{n}.fnt"/>' for n in meta)+'</fonts>')
(P/'tools/font-metrics.json').write_text(json.dumps(meta,ensure_ascii=False))
(P/'tools/onwatch-catalog.json').write_text(json.dumps({'groups':groups,'resources':resources},ensure_ascii=False,indent=2))
print('On-watch catalog:',len(labels),'settings;',len(metrics),'shared metrics;',len(chars),'menu glyphs')
