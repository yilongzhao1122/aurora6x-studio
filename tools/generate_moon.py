"""Offline ephemeris for display only. pip install astronomy-engine==2.1.19.
45-degree geocentric phase events, linearly interpolated. Not a local sky orientation.
No runtime Internet or phone service required. Valid UTC 2020-01-01..2040-12-31.
"""
from pathlib import Path
import astronomy as a,json,datetime,bisect,math
P=Path(__file__).resolve().parents[1]
epoch=1577836800
start=a.Time.Make(2019,12,1,0,0,0)
t=a.SearchMoonPhase(0,start,40);events=[];i=0
while t.Utc().year<2042:
 events.append(round((t.Utc().replace(tzinfo=datetime.timezone.utc).timestamp()-epoch)/60))
 i+=1;t=a.SearchMoonPhase((i%8)*45,t.AddDays(1),8)
 assert t is not None
# Generate compact integer minutes; enough coverage beyond year 2038 without signed Unix-seconds overflow.
s='import Toybox.Lang;\nclass MoonData {\n var events as Lang.Array<Lang.Number> = '+json.dumps(events)+';\n'
s+=''' function initialize(){}
 function phase(now){
  var minute=(now-1577836800)/60.0;
  if(minute<0 || minute>=11046240){return null;}
  var lo=0;var hi=events.size()-1;
  while(hi-lo>1){var mid=((lo+hi)/2).toNumber();if(events[mid]<=minute){lo=mid;}else{hi=mid;}}
  return ((lo%8)+(minute-events[lo])/(events[hi]-events[lo]))/8.0;
 }
}
'''
(P/'source/MoonData.mc').write_text(s)
# Compare interpolation with independent direct phase evaluation each day at UTC noon.
errors=[]
for day in range(7671):
 sec=epoch+day*86400+43200;m=(sec-epoch)/60;i=bisect.bisect_right(events,m)-1
 calc=((i%8)+(m-events[i])/(events[i+1]-events[i]))*45
 exact=a.MoonPhase(a.Time.Make(2020,1,1,12,0,0).AddDays(day))
 errors.append(abs((calc-exact+180)%360-180))
report={'generator':'astronomy-engine 2.1.19','events':len(events),'checked_days':len(errors),'maximum_phase_angle_error_degrees':max(errors),'mean_phase_angle_error_degrees':sum(errors)/len(errors),'valid_utc':'2020-01-01 through 2040-12-31','note':'offline table interpolation; visual illumination/orientation schematic, no local horizon rotation'}
(P/'docs/moon_validation.json').write_text(json.dumps(report,indent=2));print(report)

from ephemeris_resources import partition_moon
partition_moon(P,events)
