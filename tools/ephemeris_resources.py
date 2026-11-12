"""Write small, year-scoped resource tables. No full arrays in executable code."""
import json,bisect,datetime

def xml_index(P):
 r=P/'resources/ephemeris'
 (r/'resources.xml').write_text('<resources>'+''.join(f'<jsonData id="{f.stem}" filename="{f.name}"/>' for f in sorted(r.glob('*.json')) )+'</resources>')

def bounds(year):
 return [int(datetime.datetime(y,1,1,tzinfo=datetime.timezone.utc).timestamp()) for y in (year,year+1)]

def partition_moon(P,events):
 r=P/'resources/ephemeris';r.mkdir(parents=True,exist_ok=True)
 for year in range(2020,2041):
  start,end=bounds(year)
  lo=bisect.bisect_right(events,(start-86400-1577836800)/60)-1
  hi=bisect.bisect_left(events,(end+86400-1577836800)/60)+1
  (r/f'Moon{year}.json').write_text(json.dumps([lo]+events[lo:hi],separators=(',',':')))
 (P/'source/MoonData.mc').write_text(MOON_SOURCE)
 xml_index(P)

def partition_calendar(P,months,terms):
 r=P/'resources/ephemeris';r.mkdir(parents=True,exist_ok=True)
 for year in range(2020,2041):
  start,end=bounds(year);ds=start//86400;de=end//86400
  ml=bisect.bisect_right([v//32 for v in months],ds)-1
  mh=bisect.bisect_left([v//32 for v in months],de)+1
  tl=bisect.bisect_left([v//32 for v in terms],ds)
  th=bisect.bisect_left([v//32 for v in terms],de)+1
  row={'months':months[ml:mh],'terms':terms[tl:th]}
  (r/f'Calendar{year}.json').write_text(json.dumps(row,separators=(',',':')))
 (P/'source/CalendarData.mc').write_text(CALENDAR_SOURCE)
 xml_index(P)

MOON_SOURCE='import Toybox.Lang;\nimport Toybox.Application;\nimport Toybox.Time;\nimport Toybox.Time.Gregorian;\nclass MoonData {\n var events as Lang.Array<Lang.Number> or Null=null;\n var loadedYear=-1;\n function initialize(){}\n function phase(now){\n  var minute=(now-1577836800)/60.0;\n  if(minute<0 || minute>=11046240){events=null;loadedYear=-1;return null;}\n  // Use local year; each resource has >=24h overlap for UTC/local year boundaries.\n  var year=Gregorian.info(new Time.Moment(now),Time.FORMAT_SHORT).year;\n  if(year<2020){year=2020;}if(year>2040){year=2040;}\n  if(events==null || loadedYear!=year){\n   events=null;\n   var ids=[Rez.JsonData.Moon2020,Rez.JsonData.Moon2021,Rez.JsonData.Moon2022,Rez.JsonData.Moon2023,Rez.JsonData.Moon2024,Rez.JsonData.Moon2025,Rez.JsonData.Moon2026,Rez.JsonData.Moon2027,Rez.JsonData.Moon2028,Rez.JsonData.Moon2029,Rez.JsonData.Moon2030,Rez.JsonData.Moon2031,Rez.JsonData.Moon2032,Rez.JsonData.Moon2033,Rez.JsonData.Moon2034,Rez.JsonData.Moon2035,Rez.JsonData.Moon2036,Rez.JsonData.Moon2037,Rez.JsonData.Moon2038,Rez.JsonData.Moon2039,Rez.JsonData.Moon2040];\n   events=Application.loadResource(ids[year-2020]) as Lang.Array<Lang.Number>;loadedYear=year;\n  }\n  var lo=1;var hi=events.size()-1;\n  while(hi-lo>1){var mid=((lo+hi)/2).toNumber();if(events[mid]<=minute){lo=mid;}else{hi=mid;}}\n  return (((events[0]+lo-1)%8)+(minute-events[lo])/(events[hi]-events[lo]))/8.0;\n }\n}\n'
CALENDAR_SOURCE='import Toybox.Application;\nimport Toybox.Time;\nimport Toybox.Lang;\nimport Toybox.Time.Gregorian;\n// Generated calendar dates, local Gregorian date; terms use Chinese civil dates.\nclass CalendarData {\n var months as Lang.Array<Lang.Number> or Null=null;\n var terms as Lang.Array<Lang.Number> or Null=null;\n var loadedYear=-1;\n var names as Lang.Array<Lang.String> = ["小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"];\n var lastDay=-1;\n var lunar="--";\n var lunarEn="--";\n var term="--";\n var termEn="--";\n function initialize() {}\n function refresh() {\n  var n=Time.now();var g=Gregorian.info(n,Time.FORMAT_SHORT);\n  // UTC noon for this local civil date avoids timezone offsets at midnight.\n  var day=Gregorian.moment({:year=>g.year,:month=>g.month,:day=>g.day,:hour=>12}).value()/86400;\n  if(day==lastDay){return;}lastDay=day;lunar="--";term="--";lunarEn="--";termEn="--";\n  if(g.year<2020 || g.year>2040){return;}\n  if(loadedYear!=g.year){\n   months=null;terms=null;\n   var ids=[Rez.JsonData.Calendar2020,Rez.JsonData.Calendar2021,Rez.JsonData.Calendar2022,Rez.JsonData.Calendar2023,Rez.JsonData.Calendar2024,Rez.JsonData.Calendar2025,Rez.JsonData.Calendar2026,Rez.JsonData.Calendar2027,Rez.JsonData.Calendar2028,Rez.JsonData.Calendar2029,Rez.JsonData.Calendar2030,Rez.JsonData.Calendar2031,Rez.JsonData.Calendar2032,Rez.JsonData.Calendar2033,Rez.JsonData.Calendar2034,Rez.JsonData.Calendar2035,Rez.JsonData.Calendar2036,Rez.JsonData.Calendar2037,Rez.JsonData.Calendar2038,Rez.JsonData.Calendar2039,Rez.JsonData.Calendar2040];\n   var row=Application.loadResource(ids[g.year-2020]) as Lang.Dictionary;months=row["months"] as Lang.Array<Lang.Number>;terms=row["terms"] as Lang.Array<Lang.Number>;loadedYear=g.year;\n  }\n  var m=0;var start=0;\n  for(var i=0;i<months.size();i++){var d=months[i]/32;if(d>day){break;}m=months[i]%32;start=d;}\n  var dd=day-start+1;var leap=m>=16;if(leap){m-=16;}\n  var mn=["正","二","三","四","五","六","七","八","九","十","冬","腊"];\n  var nn=["一","二","三","四","五","六","七","八","九","十"];\n  var dn="";\n  if(dd<=10){dn="初"+nn[dd-1];}else if(dd<20){dn="十"+nn[dd-11];}else if(dd==20){dn="二十";}else if(dd<30){dn="廿"+nn[dd-21];}else{dn="三十";}\n  lunar=(leap?"闰":"")+mn[m-1]+"月"+dn;\n  lunarEn=(leap?"L* ":"L ")+m.toString()+"/"+dd.toString();\n  for(var j=0;j<terms.size();j++){var td=terms[j]/32;if(td>=day){var ix=terms[j]%32;term=(td==day?"":"+"+(td-day).toString()+"天 ")+names[ix];termEn="ST"+(ix+1).toString()+" +"+(td-day).toString()+"d";break;}}\n }\n}\n'
