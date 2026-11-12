from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from theme_resources import lum
P=Path(__file__).resolve().parents[1];meta=json.loads((P/'tools/font-metrics.json').read_text());atlas={k:Image.open(P/f'resources/fonts/{k}.png').getchannel('A') for k in meta}
minimum=100;rows=[]
images={i:Image.open(P/f'resources/drawables/panel{i}.png').convert('RGB') for i in range(13,33)}
for scene in json.loads((P/'docs/theme-validation/text-scenes.json').read_text()):
 im=images[scene['theme']]
 for c in scene['text']:
  x,y,f,text,j=c['args'];m=meta[f]
  if j==1:x-=sum(m['chars'][a]['a'] for a in text)//2
  for char in text:
   q=m['chars'][char];mask=atlas[f].crop((q['x'],q['y'],q['x']+q['w'],q['y']+q['h']))
   for yy in range(q['h']):
    for xx in range(q['w']):
     if mask.getpixel((xx,yy)):
      px=x+q['xo']+xx-16;py=y+q['yo']+yy-64
      assert 0<=px<250 and 0<=py<115,(scene,char,px,py)
      contrast=(float(lum(im.getpixel((px,py))))+.05)/.05
      minimum=min(minimum,contrast);assert contrast>=7-1e-6,(scene['theme'],text,char,px,py,contrast)
   x+=q['a']
for i,im in images.items():
 assert im.size==(250,115);colors=set(im.getdata());assert len(colors)<=16
 assert all(all(c%85==0 for c in rgb) for rgb in colors)
 a=np.array(im)[40:86,45:188];colored=np.any(a!=255,axis=2);coverage=float(np.mean(colored));assert coverage>.10,(i,coverage)
 rows.append({'id':i,'palette':len(colors),'central_colored_fraction':round(coverage,4)})
assert len({hashlib.sha256(im.tobytes()).hexdigest() for im in images.values()})==20
report={'clock_scenes':960,'minimum_black_text_contrast':round(minimum,3),'all_palettes_at_most':16,'themes':rows,'scope':'Pixel/fixture checks, not Garmin simulator or device runtime'}
(P/'docs/theme-validation/contrast.json').write_text(json.dumps(report,indent=2));print('PASS theme conversion, 20 distinct central artworks, text contrast minimum',minimum)
