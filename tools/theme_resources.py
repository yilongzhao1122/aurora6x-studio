"""Convert Image-generated theme masters to native 64-colour, <=16-colour indexed panels.
This performs asset sizing, colour conversion and layout clipping for the Garmin compiler.
It does not invent replacement artwork. Run through generate_onwatch.py.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,xml.etree.ElementTree as ET
PANEL=[(18,157),(18,109),(22,91),(38,67),(116,67),(138,94),(260,94),(264,108),(264,135),(207,135),(179,174),(115,174),(104,159)]
def lum(c):
 v=np.asarray(c,dtype=float)/255;v=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
 return v@np.array([.2126,.7152,.0722])
def build_ai_themes(P):
 cand=np.array([(r,g,b) for r in (0,85,170,255) for g in (0,85,170,255) for b in (0,85,170,255)],dtype=np.int32)
 # Every colour under clock glyphs has black-text contrast >=7:1.
 cand=cand[lum(cand)>=.30]
 xml=P/'resources/drawables/drawables.xml';root=ET.parse(xml).getroot();rows=[]
 for t in json.loads((P/'tools/ai-theme-catalog.json').read_text()):
  i=t['id'];master=P/f'artwork/theme-masters/theme{i}.png'
  im=Image.open(master).convert('RGB').resize((250,115),Image.Resampling.LANCZOS)
  a=np.asarray(im,dtype=np.int32);flat=a.reshape(-1,3)
  nearest=np.argmin(((flat[:,None,:]-cand[None,:,:])**2).sum(axis=2),axis=1)
  counts=np.bincount(nearest,minlength=len(cand));colors=[(255,255,255),(170,170,170)]
  for ix in np.argsort(-counts):
   c=tuple(int(x) for x in cand[ix])
   if c not in colors:colors.append(c)
   if len(colors)==15:break
  pal=np.array(colors,dtype=np.int32);mapping=np.argmin(((flat[:,None,:]-pal[None,:,:])**2).sum(axis=2),axis=1)
  im=Image.fromarray(pal[mapping].reshape(115,250,3).astype('uint8'))
  mask=Image.new('L',(250,115));ImageDraw.Draw(mask).polygon([(x-16,y-64) for x,y in PANEL],fill=255)
  out=Image.new('RGB',(250,115));out.paste(im,(0,0),mask)
  d=ImageDraw.Draw(out)
  d.line([(x-16,y-64) for x,y in PANEL+[PANEL[0]]],fill=(170,170,170),width=1)
  # These borders belong to the UI panel, not the generated artwork.
  for pts in [[(22,92),(116,92),(138,95)],[(116,174),(116,157),(178,157),(187,163)],[(207,97),(211,102),(211,132)]]:d.line([(x-16,y-64) for x,y in pts],fill=(0,0,0),width=1)
  path=P/f'resources/drawables/panel{i}.png';out.save(path)
  actual=sorted(set(out.getdata()));assert len(actual)<=16
  for old in list(root):
   if old.attrib.get('id')==f'Panel{i}':root.remove(old)
  node=ET.SubElement(root,'bitmap',id=f'Panel{i}',filename=f'panel{i}.png',dithering='none');p=ET.SubElement(node,'palette',disableTransparency='true')
  for c in actual:ET.SubElement(p,'color').text='%02X%02X%02X'%c
  rows.append({'id':i,'name':t['zh'],'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'panel_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions':[250,115],'palette_colors':len(actual),'estimated_indexed_bytes':250*115//2,'generation':'ChatGPT Image, center-composition edit','black_text_contrast_min_target':7})
 ET.indent(root);ET.ElementTree(root).write(xml,encoding='unicode')
 (P/'docs/theme-validation/conversion.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('Built',len(rows),'Image themes, explicit <=16-colour palettes at 250x115.')
