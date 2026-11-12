"""Build reproducible 280px artwork, bitmap fonts and screenshot-matched settings.
Requires Pillow; calendar generation additionally requires lunar-python 1.4.9.
No reference screenshot pixels are embedded in the watch resources.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
from xml.sax.saxutils import escape
import json, math, os
P=Path(__file__).resolve().parents[1]
LATIN=Path(os.environ.get('AURORA_LATIN_FONT',str(P/'artwork/font-sources/NotoSansCJKSC-Bold.otf')))
NARROW=Path(os.environ.get('AURORA_TIME_FONT',str(P/'artwork/font-sources/NotoSansCJKSC-Bold.otf')))
CJK=Path(os.environ.get('AURORA_CJK_FONT',str(P/'artwork/font-sources/NotoSansCJKSC-Bold.otf')))
PANEL=[(18,157),(18,109),(22,91),(38,67),(116,67),(138,94),(260,94),(264,108),(264,135),(207,135),(179,174),(115,174),(104,159)]
fields=['步数 Steps','目标步数 Steps Goal','里程 Distance (km)','热量 Total Calories','台阶 Floors','心率 Heart Rate','身体电量 Body Battery','压力 Stress','血氧 Oxygen (%)','呼吸 Respiration Rate','恢复时间 Recovery (h)','海平面气压 Sea-level pressure (hPa)','海拔 Altitude (m)','体重 Weight (kg)','太阳能强度 Solar intensity (%)','当天活动分钟 Active Minutes Today','本周活动分钟 Active Minutes Week','总消耗热量 Total Calories','骑行 VO2max Cycling','跑步 VO2max Running','月跑量 Monthly Run (km, 已有记录)','电池 Battery (%)','实时气温 Temperature','湿度 Humidity (%)','降水概率 Rain (%)','风速 Wind (m/s)','体感温度 Feels Like','最低气温 Low','最高气温 High']
strip=['电池电量 Battery','系统图标 System icons','实时气温 Temperature','农历 Lunar','节气 Solar terms','第二时间 Second time','下个日出日落 Next sunrise/sunset']
icon=['天气 Weather','风向 Wind direction','久坐提醒 Move bar','月相 Moon phase']
config={'Language':0,'A0':0,'A1':0,'A2':1,'A3':1,'A4':0,'B2':0,'C0':0,'C1':0,'C2':0,'C3':12,'C4':1,'C5':3,'C6':2,'CustomText':'AURORA','SecondOffset':-8,'Backdrop':2,'BackgroundColor':16777215,'DataColor':16777215,'DebugLog':0,'TimeTypeface':0,'DataTypeface':2}
options={'Language':['中文','English'],'A0':strip,'A1':icon,'A2':['湿度+降水概率 Humidity + Rain',strip[2],strip[3],strip[4],strip[5]],'A3':icon,'A4':['最低最高心率 HR range (可用历史)','步数及目标 Steps / Goal','总消耗热量 Total Calories'],'B2':['抬手显示秒钟 Seconds while awake','隐藏秒钟 Hide seconds'],'C0':['电池 Battery','步数 Steps','身体电量 Body Battery','压力 Stress'],'C1':['心率 Heart Rate','身体电量 Body Battery','压力 Stress','电池 Battery'],'C2':fields,'C3':fields,'C4':fields,'C5':fields,'C6':strip[1:]+['用户自定义 Custom text'],'Backdrop':['背景1 · 玫红渐变','背景2 · 冰蓝折面','背景3 · 银白流线','背景4 · 香槟渐变','自定义背景颜色','背景5 · 薄荷切片','背景6 · 珊瑚色块','背景7 · 紫晶轨道','背景8 · 柠檬赛道','背景9 · 冰川网格','背景10 · 落日拼色','背景11 · 纸白蓝图','背景12 · 青紫双翼'],'DebugLog':['关闭 Off','开启数据来源日志 On']}
titles={'Language':'语言 Language','A0':'A0 · 顶部数据 Top data','A1':'A1 · 左侧图标 Left icon','A2':'A2 · 上方数据 Upper data','A3':'A3 · 右侧图标 Right icon','A4':'A4 · 右上组合数据 Paired data','B2':'B2 · 秒钟 Seconds','C0':'C0 · 彩条进度 Progress','C1':'C1 · 左下圆环 Ring','C2':'C2 · 左上数据 Upper left','C3':'C3 · 左下数据 Lower left','C4':'C4 · 右上数据 Upper right','C5':'C5 · 右下数据 Lower right','C6':'C6 · 底部数据 Bottom data','CustomText':'自定义内容 Custom text (ASCII, 18 chars)','SecondOffset':'第二时间相对本地时差 Hours from local time','Backdrop':'背景 Backdrop','BackgroundColor':'自定义背景色 RGB decimal','DataColor':'数据颜色 RGB decimal','DebugLog':'诊断日志 Data source log'}
options.update({'TimeTypeface':['Bebas Neue','Rajdhani Bold','Roboto Bold','Nunito Bold','Aurora Digital','JetBrains Mono Bold'],'DataTypeface':['Bebas Neue','Rajdhani Bold','Roboto Bold','Nunito Bold','Aurora Digital','JetBrains Mono Bold'],})
titles.update({'TimeTypeface':'时间数字字体','DataTypeface':'数据数字字体'})
ai_themes=json.loads((P/'tools/ai-theme-catalog.json').read_text())
options['Backdrop'] += ['AI'+str(t['id'])+' · '+t['zh'] for t in ai_themes]
spec={'defaults':config,'options':options,'titles':titles,'ranges':{'SecondOffset':[-23,23],'BackgroundColor':[0,16777215],'DataColor':[0,16777215]}}
(P/'tools/settings-schema.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
existing=json.loads((P/'config.json').read_text()) if (P/'config.json').exists() else {}
(P/'config.json').write_text(json.dumps({**config,**{k:v for k,v in existing.items() if k in config}},ensure_ascii=False,indent=2))
strings={'AppName':'Aurora 6X Studio'};props=[];settings=[]
for k,v in config.items():
 typ='string' if isinstance(v,str) else 'number';props.append(f'<property id="{k}" type="{typ}">{escape(str(v))}</property>');strings[k+'Title']=titles[k]
 if k in options:
  entries=[]
  for i,label in enumerate(options[k]):
   if k in ["C2","C3","C4","C5"] and i==17:continue
   sid=k+'Opt'+str(i);strings[sid]=label;entries.append(f'<listEntry value="{i}">@Strings.{sid}</listEntry>')
  inp='<settingConfig type="list">'+''.join(entries)+'</settingConfig>'
 elif k in spec['ranges']:
  lo,hi=spec['ranges'][k];inp=f'<settingConfig type="numeric" min="{lo}" max="{hi}"/>'
 else:inp='<settingConfig type="alphaNumeric" maxLength="18"/>'
 settings.append(f'<setting propertyKey="@Properties.{k}" title="@Strings.{k}Title">{inp}</setting>')
(P/'resources/settings/properties.xml').write_text('<properties>\n'+'\n'.join(props)+'\n</properties>')
(P/'resources/settings/settings.xml').write_text('<settings>\n'+'\n'.join(settings)+'\n</settings>')
(P/'resources/strings/strings.xml').write_text('<strings>\n'+''.join(f'<string id="{k}">{escape(v)}</string>\n' for k,v in strings.items())+'</strings>')
def palette(im):
 # Ordered dithering to the actual 64-colour MIP palette.
 bayer=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
 im=im.convert('RGB'); pix=im.load()
 for y in range(im.height):
  for x in range(im.width):
   pix[x,y]=tuple(max(0,min(3,int(c/85+(bayer[y%4][x%4]+.5)/16)))*85 for c in pix[x,y])
 return im
def panel(style):
 im=Image.new('RGB',(280,280),'black');d=ImageDraw.Draw(im)
 for y in range(64,180):
  for x in range(16,266):
   u=(x-16)/250;v=(y-64)/116
   if style==0:c=(240-18*u,210-105*v+20*u,231-18*v+20*u)
   elif style==1:c=(255,255,255)
   elif style==2:c=(255,255,255)
   elif style==3:c=(254-10*u,243-65*v,207-90*v+30*u)
   else:c=(255,255,255)
   d.point((x,y),fill=tuple(int(max(0,min(255,z))) for z in c))
 if style in [1,2]:
  c1=(85,170,255) if style==1 else (170,255,255)
  for pts in [[(16,115),(130,76),(198,96),(100,91)],[(19,146),(119,113),(197,161),(125,126)],[(135,94),(223,110),(264,95),(221,119)],[(55,79),(158,93),(119,87),(88,71)],[(140,170),(222,123),(263,121),(201,139)]]:
   d.polygon(pts,fill=c1)
  for pts in [[(20,127),(132,97),(199,139),(130,112)],[(79,73),(158,91),(103,86)],[(156,160),(224,121),(257,128),(215,129)]]:d.polygon(pts,fill=(255,255,255))
 if style>=5:
  palettes={5:('#aaffaa','#aaffff','#55aaaa'),6:('#ffaaaa','#ffffaa','#ff5555'),7:('#aaaaff','#ffaaff','#aa55aa'),8:('#ffffaa','#aaffaa','#aaaa00'),9:('#aaffff','#aaaaff','#55aaff'),10:('#ffffaa','#ffaaaa','#ffaa00'),11:('#ffffff','#aaffff','#55aaff'),12:('#aaffff','#ffaaff','#aa55ff')}
  a,b,accent=palettes[style]
  if style in (5,6,10):
   d.polygon([(16,90),(140,90),(98,159),(16,159)],fill=a)
   d.polygon([(136,95),(265,95),(265,135),(211,135),(181,174),(125,174)],fill=b)
   d.polygon([(17,149),(80,149),(89,138),(26,138)],fill='white')
   d.line([(22,154),(95,154),(132,98)],fill=accent,width=2)
  elif style in (7,8,12):
   d.polygon([(16,96),(16,157),(82,157),(124,96)],fill=a)
   d.polygon([(180,96),(264,96),(264,135),(210,135),(185,165),(140,165)],fill=b)
   for shift in (0,6):d.line([(40,159-shift),(88,159-shift),(133,95-shift)],fill=accent,width=1)
   d.line([(155,96),(184,96),(208,130),(261,130)],fill=accent,width=2)
  else:
   if style==9:d.polygon([(20,92),(113,92),(168,156),(20,156)],fill=a)
   for xx in range(24,266,14):d.line([(xx,95),(xx,156)],fill=b,width=1)
   for yy in range(100,157,14):d.line([(20,yy),(264,yy)],fill=b,width=1)
   d.line([(20,147),(93,147),(155,98),(263,98)],fill=accent,width=2)
  # Distinct date and seconds blocks, with quiet white center for legibility.
  d.polygon([(22,91),(38,67),(116,67),(134,91)],fill=b)
  d.rectangle((212,96,264,133),fill=a)
  d.line([(215,130),(259,130)],fill=accent,width=2)
 mask=Image.new('L',(280,280));ImageDraw.Draw(mask).polygon(PANEL,fill=255)
 circle=Image.new('L',(280,280));ImageDraw.Draw(circle).ellipse((1,1,279,279),fill=255)
 from PIL import ImageChops
 mask=ImageChops.multiply(mask,circle);out=Image.new('RGB',(280,280),'black');out.paste(im,(0,0),mask)
 d=ImageDraw.Draw(out);d.line(PANEL+[PANEL[0]],fill=(170,170,170),width=1)
 d.line([(22,92),(116,92),(138,95)],fill=(0,0,0),width=1)
 d.line([(116,174),(116,157),(178,157),(187,163)],fill=(0,0,0),width=1)
 d.line([(207,97),(211,102),(211,132)],fill=(0,0,0),width=1)
 return palette(out.crop((16,64,266,179)))
for i in [0,1,2,3,5,6,7,8,9,10,11,12]:panel(i).save(P/f'resources/drawables/panel{i}.png')
font_meta={}
chars=''.join(chr(i) for i in range(32,127))+'°'+''.join(sorted(set('星期一二三四五六七八九日月正初十廿冬腊闰年月大小春夏秋冬分至立雨水惊蛰清明谷芒种暑处白露寒霜降雪满天')))
def makefont(name,size,chars,path,base,lineh,sx=1.0):
 latin=ImageFont.truetype(str(path),size);cjk=ImageFont.truetype(str(CJK),size-1)
 atlas=Image.new('RGBA',(512,math.ceil(len(chars)/16)*(lineh+2)),(0,0,0,0));d=ImageDraw.Draw(atlas);meta={}
 lines=[f'info face="AuroraStudio" size={size} bold=1 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0',f'common lineHeight={lineh} base={base} scaleW=512 scaleH={atlas.height} pages=1 packed=0',f'page id=0 file="{name}.png"',f'chars count={len(chars)}']
 # Large digits need a wider cell than the normal atlas.
 cw=16 if size<20 else 24 if size<40 else 40;cols=16;width=cw*cols
 atlas=Image.new('RGBA',(width,math.ceil(len(chars)/cols)*(lineh+2)),(0,0,0,0));d=ImageDraw.Draw(atlas)
 lines[1]=f'common lineHeight={lineh} base={base} scaleW={width} scaleH={atlas.height} pages=1 packed=0'
 for i,c in enumerate(chars):
  f=cjk if ord(c)>127 and c!='°' else latin;b=f.getbbox(c,anchor='ls');w=max(1,b[2]-b[0]);h=max(1,b[3]-b[1]);x=(i%cols)*cw;y=(i//cols)*(lineh+2)
  tile=Image.new('RGBA',(w,h));ImageDraw.Draw(tile).text((-b[0],-b[1]),c,font=f,fill='white',anchor='ls')
  w=max(1,round(w*sx));tile=tile.resize((w,h),Image.Resampling.LANCZOS)
  # A one-pixel horizontal emboldening, done OFF-device. Do not dilate vertically:
  # line height and all existing y positions stay fixed. Keep counters readable.
  mask=tile.getchannel('A').point(lambda a:255 if a>=110 else 0)
  if mask.getbbox():
   bold=Image.new('L',(w+1,h));bold.paste(mask,(0,0))
   shifted=Image.new('L',(w+1,h));shifted.paste(mask,(1,0))
   mask=ImageChops.lighter(bold,shifted);w+=1
  tile=Image.new('RGBA',(w,h),'white');tile.putalpha(mask)
  assert w<=cw,(name,c,w,cw)
  atlas.alpha_composite(tile,(x,y))
  xo=round(b[0]*sx);oldadv=round(f.getlength(c)*sx)
  # At least one clear column before the next glyph's cell. Spaces stay unchanged.
  adv=max(oldadv+1,xo+w+1) if mask.getbbox() else oldadv
  b=(xo,b[1],b[2],b[3])
  lines.append(f'char id={ord(c)} x={x} y={y} width={w} height={h} xoffset={b[0]} yoffset={base+b[1]} xadvance={adv} page=0 chnl=15')
  meta[c]={'x':x,'y':y,'w':w,'h':h,'xo':b[0],'yo':base+b[1],'a':adv}
 atlas.putalpha(atlas.getchannel('A').point(lambda a:255 if a>=110 else 0));atlas.save(P/f'resources/fonts/{name}.png');(P/f'resources/fonts/{name}.fnt').write_text('\n'.join(lines))
 font_meta[name]={'height':lineh,'chars':meta}
makefont('Small',14,chars,LATIN,14,17)
makefont('Medium',16,'0123456789.-%:/',LATIN,15,18)
makefont('Time',76,'0123456789:',NARROW,55,57,0.82)
makefont('Seconds',34,'0123456789-',NARROW,25,27,0.85)
(P/'resources/fonts/fonts.xml').write_text('<fonts>'+''.join(f'<font id="{n}" filename="{n}.fnt"/>' for n in font_meta)+'</fonts>')
(P/'tools/font-metrics.json').write_text(json.dumps(font_meta,ensure_ascii=False))
def bitmap_xml(i):
 colors=sorted(set(Image.open(P/f'resources/drawables/panel{i}.png').convert('RGB').getdata()))
 return f'<bitmap id="Panel{i}" filename="panel{i}.png" dithering="none"><palette disableTransparency="true">'+''.join('<color>%02X%02X%02X</color>'%c for c in colors)+'</palette></bitmap>'
(P/'resources/drawables/drawables.xml').write_text('<drawables><bitmap id="LauncherIcon" filename="icon.png"/>'+''.join(bitmap_xml(i) for i in [0,1,2,3,5,6,7,8,9,10,11,12])+'</drawables>')
print('Generated twelve 64-colour panels, fonts, and',len(config),'settings.')

from theme_resources import build_ai_themes
build_ai_themes(P)
