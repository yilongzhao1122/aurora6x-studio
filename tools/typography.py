"""Offline bitmap subsets, 6 selectable digit families and CJK/English UI.
Source fonts and their OFL licenses are bundled outside watch resources.
"""
from pathlib import Path
from PIL import Image,ImageFont,ImageDraw,ImageChops
import math,json
FAMILIES=['BebasNeue.ttf','Rajdhani.ttf','Roboto.ttf','Nunito.ttf',None,'JetBrainsMono.ttf']
def face(path,size):
 f=ImageFont.truetype(str(path),size)
 try:
  axes=f.get_variation_axes();f.set_variation_by_axes([700 if b'Weight' in a['name'] else a['default'] for a in axes])
 except (OSError,AttributeError):pass
 return f

def seven(ch,height):
 # Original seven-segment glyphs, not a copy of a proprietary Digital Clock font.
 w=32;h=54;m=Image.new('L',(w,h));d=ImageDraw.Draw(m);t=5
 seg={'a':(6,0,25,4),'b':(27,6,31,24),'c':(27,29,31,47),'d':(6,49,25,53),'e':(0,29,4,47),'f':(0,6,4,24),'g':(6,25,25,29)}
 codes=['ab cdef'.replace(' ',''),'bc','abged','abgcd','fgbc','afgcd','afgecd','abc','abcdefg','abfgcd']
 if ch.isdigit():
  for s in codes[int(ch)]:d.rectangle(seg[s],fill=255)
 elif ch==':':m=Image.new('L',(9,h));d=ImageDraw.Draw(m);d.rectangle((2,15,6,19),fill=255);d.rectangle((2,35,6,39),fill=255)
 elif ch=='-':d.rectangle(seg['g'],fill=255)
 elif ch=='.':d.rectangle((20,48,25,53),fill=255)
 else:
  f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',40) if Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf').exists() else ImageFont.load_default()
  # Replaced by the bundled UI source in build(), for symbols outside segment alphabet.
  d.text((0,0),ch,font=f,fill=255)
 return m

def build_typography(P,meta,menu_chars):
 R=P/'resources/fonts';S=P/'artwork/font-sources';ui=S/'NotoSansCJKSC-Bold.otf'
 def emit(name,characters,size,lineh,base,digit=False,source=None,kind=None):
  f=face(source or ui,size);chars=list(dict.fromkeys(characters));cw=40 if lineh>40 else 24;cols=16
  atlas=Image.new('RGBA',(cw*cols,math.ceil(len(chars)/cols)*(lineh+2)),(255,255,255,0));entries={};lines=[]
  for i,c in enumerate(chars):
   b=f.getbbox(c,anchor='ls');w=max(1,b[2]-b[0]);h=max(1,b[3]-b[1]);mask=Image.new('L',(w,h));ImageDraw.Draw(mask).text((-b[0],-b[1]),c,font=f,fill=255,anchor='ls')
   advance=round(f.getlength(c));xo=b[0];yo=base+b[1]
   if digit:
    cap={'Time':58,'Sec':33,'Data':20}[kind]+(2 if name.startswith('Ring') else 0);maxw={'Time':36,'Sec':20,'Data':9}[kind];adv={'Time':39,'Sec':22,'Data':10}[kind]
    if source is None and (c.isdigit() or c in ':-.'):mask=seven(c,cap);w,h=mask.size
    # Scale relative to zero's ink height; preserve punctuation baseline.
    zero=f.getbbox('0',anchor='ls');den=max(1,zero[3]-zero[1]);scale=cap/den
    if source is None and (c.isdigit() or c in ':-.'):scale=cap/h
    nh=cap if c.isdigit() else max(1,min(cap,round(h*scale)))
    nw=max(1,min(maxw,round(w*scale)))
    if c==':':nw={'Time':6,'Sec':4,'Data':3}[kind]
    mask=mask.resize((nw,nh),Image.Resampling.LANCZOS)
    advance=adv if c!=':' else {'Time':13,'Sec':8,'Data':5}[kind]
    xo=(advance-nw)//2;yo=1 if c.isdigit() else (cap-nh+1 if c in '.-' else (cap-nh)//2+1)
   mask=mask.point(lambda v:255 if v>=128 else 0);w,h=mask.size
   assert w<=cw and yo>=0 and yo+h<=lineh,(name,c,w,h,yo,lineh)
   x=i%cols*cw;y=i//cols*(lineh+2);tile=Image.new('RGBA',(w,h),'white');tile.putalpha(mask);atlas.paste(tile,(x,y))
   entries[c]={'x':x,'y':y,'w':w,'h':h,'xo':xo,'yo':yo,'a':advance}
   lines.append(f'char id={ord(c)} x={x} y={y} width={w} height={h} xoffset={xo} yoffset={yo} xadvance={advance} page=0 chnl=15')
  header=[f'info face="AuroraSubset{name}" size={size} bold=1 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0',f'common lineHeight={lineh} base={base} scaleW={atlas.width} scaleH={atlas.height} pages=1 packed=0',f'page id=0 file="{name}.png"',f'chars count={len(chars)}']
  atlas.save(R/(name+'.png'));(R/(name+'.fnt')).write_text('\n'.join(header+lines));meta[name]={'height':lineh,'chars':entries}
 smallchars=''.join(meta['Small']['chars'])
 emit('Small',smallchars,14,19,15)
 emit('SmallPlus',smallchars,16,22,17)
 emit('Menu',menu_chars,16,22,17)
 for i,f in enumerate(FAMILIES):
  for kind,size,lineh,base in [('Time',82,61,59),('Sec',45,36,34),('Data',28,23,21)]:
   emit(kind+str(i),'0123456789:.-%~/kM',size,lineh,base,True,S/f if f else None,kind)
  emit('Ring'+str(i),'0123456789:.-%~/kM',28,24,22,True,S/f if f else None,'Data')
 (P/'tools/typefaces.json').write_text(json.dumps({'names':['Bebas Neue','Rajdhani Bold','Roboto Bold','Nunito Bold','Aurora Digital','JetBrains Mono Bold'],'ui':'Noto Sans CJK SC Bold, 16px binary menu rasterization'},indent=2))
