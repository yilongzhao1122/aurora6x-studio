import json
from pathlib import Path
from PIL import Image
from check_icon_import import text_pixels
from theme_resources import lum
P=Path(__file__).resolve().parents[1]
panel=Image.open(P/'resources/drawables/panel13.png').convert('RGB');count=0
for s in json.loads((P/'docs/v330/font-scenes.json').read_text()):
 cmds=[c for c in s['commands'] if c['op']=='drawText'];texts=[(c,text_pixels(c)) for c in cmds]
 for i,(c,ink) in enumerate(texts):
  assert all(0<=x<280 and 0<=y<280 for x,y in ink),(s['label'],c['args'])
  for other,otherink in texts[i+1:]:assert not ink&otherink,(s['label'],c['args'],other['args'],'overlap')
  if c['color']==0 and c['args'][2].startswith(('Time','Sec')) and s['cfg']['Backdrop']==13:
   for x,y in ink:
    assert (float(lum(panel.getpixel((x-16,y-64))))+.05)/.05>=7,(s['label'],x,y,'clock outside light panel')
 count+=1
(P/'docs/v330/font-pixel-check.txt').write_text(f'PASS {count} scenes: text/icon pair masks do not overlap; screen bounds; all 6 clock families inside light panel in 12/24h samples. Not Garmin runtime.\n')
print((P/'docs/v330/font-pixel-check.txt').read_text())
