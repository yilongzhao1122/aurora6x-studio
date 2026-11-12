from pathlib import Path
import json,datetime,bisect,xml.etree.ElementTree as E,math
from PIL import Image
P=Path(__file__).resolve().parents[1];master=json.loads((P/'tools/ephemeris-master.json').read_text());events=master['moon']
max_entries=0
for year in range(2020,2041):
 row=json.loads((P/f'resources/ephemeris/Moon{year}.json').read_text());cal=json.loads((P/f'resources/ephemeris/Calendar{year}.json').read_text())
 max_entries=max(max_entries,len(row)+len(cal['months'])+len(cal['terms']))
 assert row[1:]==events[row[0]:row[0]+len(row)-1]
 start=datetime.date(year,1,1);end=datetime.date(year+1,1,1)
 for d in range((end-start).days):
  day=(start+datetime.timedelta(days=d)-datetime.date(1970,1,1)).days
  oldm=max(v for v in master['months'] if v//32<=day);newm=max(v for v in cal['months'] if v//32<=day)
  oldt=min(v for v in master['terms'] if v//32>=day);newt=min(v for v in cal['terms'] if v//32>=day)
  assert (oldm,oldt)==(newm,newt)
 # UTC/local year transitions, offset up to +/-14 h.
 for sec in [int(datetime.datetime(year,1,1,tzinfo=datetime.timezone.utc).timestamp())+delta for delta in (-50400,0,50400)]+[int(datetime.datetime(year+1,1,1,tzinfo=datetime.timezone.utc).timestamp())+delta for delta in (-50400,0,50400)]:
  m=(sec-1577836800)/60;i=bisect.bisect_right(events,m)-1;j=bisect.bisect_right(row[1:],m)
  old=(i%8+(m-events[i])/(events[i+1]-events[i]))/8
  new=((row[0]+j-1)%8+(m-row[j])/(row[j+1]-row[j]))/8
  assert abs(old-new)<1e-12
for filename,name in [('MoonData.mc','events'),('CalendarData.mc','months'),('CalendarData.mc','terms')]:
 text=(P/'source'/filename).read_text();assert not ('var '+name+' as Lang.Array<Lang.Number> = [') in text
panels=[]
for b in E.parse(P/'resources/drawables/drawables.xml').getroot():
 if not b.attrib['id'].startswith('Panel'):continue
 colors={tuple(bytes.fromhex(c.text)) for c in b.find('palette')};image=Image.open(P/'resources/drawables'/b.attrib['filename']).convert('RGB')
 assert set(image.getdata())==colors;assert b.find('palette').attrib['disableTransparency']=='true'
 bits=1 if len(colors)<=2 else 2 if len(colors)<=4 else 4 if len(colors)<=16 else 8
 panels.append({'id':b.attrib['id'],'colors':len(colors),'nominal_indexed_pixel_bytes':math.ceil(image.width*bits/8)*image.height})
report={'previous_entries':sum(map(len,master.values())),'maximum_current_year_entries':max_entries,'calendar_days_checked':7671,'utc_local_year_boundary_cases':126,'panels':panels,'note':'Counts and nominal bitmap payloads are not measured device memory. Runtime logs must confirm used/free/total.'}
(P/'docs/memory_fix_validation.json').write_text(json.dumps(report,indent=2))
print('PASS exact table partitions: 7671 days and 126 boundary cases; entries',report['previous_entries'],'->',max_entries,'; exact-colour indexed palettes for 12 panels.')
