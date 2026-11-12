from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from preview_fonts import caption_font
import json,re,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1]
fonts=json.loads((P/'tools/font-metrics.json').read_text(encoding='utf-8'))
for name,meta in fonts.items():
 im=Image.open(P/f'resources/fonts/{name}.png').convert('RGBA')
 for c,m in meta['chars'].items():
  assert 0<=m['x'] and m['x']+m['w']<=im.width and 0<=m['y'] and m['y']+m['h']<=im.height,(name,c,m)
 assert set(im.getchannel('A').getdata())<={0,255}
for i in [i for i in range(33) if i!=4]:
 im=Image.open(P/f'resources/drawables/panel{i}.png');assert im.size==(250,115)
 assert all(all(v in (0,85,170,255) for v in rgb) for rgb in im.convert('RGB').getdata())
for p in (P/'resources').rglob('*.xml'):ET.parse(p)
names=json.loads((P/'tools/icons.json').read_text(encoding='utf-8'))['names']
canvas=Image.new('RGB',(1120,910),'#10141d');d=ImageDraw.Draw(canvas)
font=caption_font(16)
big=caption_font(24)
d.text((24,20),'40 ICONS / 6 PNG IMPORTS + WEATHER SUN / 16px + 24px',font=big,fill='white');d.text((24,57),'Nearest-neighbour enlargement for inspection / actual watch has 280 x 280 pixels',font=font,fill='#93a8bd')
for i,n in enumerate(names):
 x=24+i%8*138;y=104+i//8*148
 for size,dx,scale in [(16,0,3),(24,61,2)]:
  key='Icons'+str(size);m=fonts[key]['chars'][chr(0xe000+i)];atlas=Image.open(P/f'resources/fonts/{key}.png').convert('RGBA')
  tile=atlas.crop((m['x'],m['y'],m['x']+size,m['y']+size)).resize((48,48),Image.Resampling.NEAREST)
  canvas.paste(tile,(x+dx,y),tile)
 d.text((x,y+58),str(i)+' '+n,font=font,fill='#d3e7f5')
canvas.save(P/'docs/icons-preview.png')
for p in P.rglob('*.html'):
 for ref in re.findall(r'(?:href|src)="([^"#]+)"',p.read_text(encoding='utf-8')):
  if not any(ref.startswith(t) for t in ('http','data:','blob:')):assert (p.parent/ref).exists(),(p,ref)
print('PASS font atlas/alpha bounds; 32 native MIP palettes; resource XML; local HTML links; generated icon inspection sheet.')
