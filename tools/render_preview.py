"""Rasterize drawing commands recorded from AuroraView.mc. Not a simulator capture."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from preview_fonts import caption_font
import json,math
P=Path(__file__).resolve().parents[1]
META=json.loads((P/'tools/font-metrics.json').read_text(encoding='utf-8'))
ATLAS={k:Image.open(P/f'resources/fonts/{k}.png').convert('RGBA') for k in META}
def rgb(c):return ((c>>16)&255,(c>>8)&255,c&255)
def render(file, atlas=None):
 commands=json.loads(file.read_text(encoding='utf-8'))['commands'];im=Image.new('RGB',(280,280));d=ImageDraw.Draw(im)
 for c in commands:
  op=c['op'];a=c.get('args',[]);col=rgb(c['color']);pen=max(1,int(c.get('pen',1)))
  if op=='clear':d.rectangle((0,0,279,279),fill=col)
  elif op=='drawBitmap':im.paste(Image.open(P/f'resources/drawables/{a[2]}.png'),(a[0],a[1]))
  elif op=='drawText':
   x,y,f,text,justify=a;meta=META[f];w=sum(meta['chars'].get(ch,{}).get('a',0) for ch in text)
   if justify==1:x-=w//2
   for ch in text:
    m=meta['chars'].get(ch)
    if not m:raise ValueError('Missing glyph '+repr(ch))
    crop=(atlas or ATLAS)[f].crop((m['x'],m['y'],m['x']+m['w'],m['y']+m['h']));mask=crop.getchannel('A')
    im.paste(col,(round(x+m['xo']),round(y+m['yo']),round(x+m['xo'])+m['w'],round(y+m['yo'])+m['h']),mask);x+=m['a']
  elif op=='drawLine':d.line(tuple(a),fill=col,width=pen)
  elif op=='drawPoint':d.point(tuple(a),fill=col)
  elif op in ['drawCircle','fillCircle']:
   x,y,r=a;d.ellipse((x-r,y-r,x+r,y+r),**({'fill':col} if op=='fillCircle' else {'outline':col,'width':pen}))
  elif op=='fillEllipse':x,y,rx,ry=a;d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=col)
  elif op in ['drawRectangle','fillRectangle']:
   x,y,w,h=a;d.rectangle((x,y,x+w-1,y+h-1),**({'fill':col} if op=='fillRectangle' else {'outline':col,'width':pen}))
  elif op=='fillPolygon':d.polygon([tuple(p) for p in a[0]],fill=col)
  elif op=='drawArc':
   x,y,r,di,start,end=a
   # Use a stroked polyline so the stroke is centered on the nominal radius.
   extent=(start-end)%360
   pts=[(round(x+r*math.cos(math.radians(start-extent*i/90))),round(y-r*math.sin(math.radians(start-extent*i/90)))) for i in range(91)]
   d.line(pts,fill=col,width=pen)
  else:raise ValueError(op)
 # Actual device clips its drawable area to the circular screen.
 mask=Image.new('L',(280,280));ImageDraw.Draw(mask).ellipse((0,0,279,279),fill=255)
 out=Image.new('RGB',(280,280),'#12151b');out.paste(im,(0,0),mask);return out
def main():
 for file in (P/'docs/render').glob('*.json'):render(file).save(P/'docs'/f'{file.stem}.png')
 card=Image.new('RGB',(1320,1175),'#10141d');d=ImageDraw.Draw(card)
 f=caption_font(25)
 sm=caption_font(15)
 d.text((36,25),'AURORA 6X / STUDIO 3.3.2',font=f,fill='#f1f6ff')
 d.text((36,64),'280 x 280 / 64-colour MIP / Source-based preview with sample data (not a simulator capture)',font=sm,fill='#93a8bd')
 ids=[0,1,2,3,5,6,7,8,9,10,11,12]
 names=['ROSE','ICE','SILVER','CHAMPAGNE','MINT CUT','CORAL BLOCK','AMETHYST','CITRUS TRACK','GLACIER GRID','SUNSET BLOCK','PAPER BLUEPRINT','CYAN / LILAC']
 for j,(i,name) in enumerate(zip(ids,names)):
  x=30+(j%4)*325;y=110+(j//4)*350
  card.paste(Image.open(P/f'docs/theme{i}.png'),(x,y))
  d.text((x+10,y+294),name,font=sm,fill='#d3e7f5')
 card.save(P/'docs/preview.png')
 print('Rendered source-based previews.')


if __name__ == '__main__':
 main()
