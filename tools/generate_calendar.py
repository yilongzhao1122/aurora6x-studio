"""Generate bounded calendar tables from lunar-python (MIT), 2020-2040 inclusive."""
from pathlib import Path
from lunar_python import Solar,LunarYear
import datetime as dt,json,importlib.metadata
P=Path(__file__).resolve().parents[1]
EPOCH=dt.date(1970,1,1)
terms='小寒 大寒 立春 雨水 惊蛰 春分 清明 谷雨 立夏 小满 芒种 夏至 小暑 大暑 立秋 处暑 白露 秋分 寒露 霜降 立冬 小雪 大雪 冬至'.split()
months={};solar={}
for y in range(2019,2042):
 for m in LunarYear.fromYear(y).getMonths():
  s=Solar.fromJulianDay(m.getFirstJulianDay());d=dt.date(s.getYear(),s.getMonth(),s.getDay());day=(d-EPOCH).days
  months[day]=abs(m.getMonth())+(16 if m.getMonth()<0 else 0)
 for name,s in Solar.fromYmd(y,6,1).getLunar().getJieQiTable().items():
  if name not in terms:continue
  day=(dt.date(s.getYear(),s.getMonth(),s.getDay())-EPOCH).days;solar[day]=terms.index(name)
months=sorted(months.items());solar=sorted(solar.items())
# One packed int per entry; low 5 bits hold lunar month/leap or solar term index.
mt=[day*32+m for day,m in months];st=[day*32+n for day,n in solar]
text='''import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Lang;
// Generated calendar dates, local Gregorian date; terms use Chinese civil dates.
class CalendarData {
 var months as Lang.Array<Lang.Number> = MONTHS;
 var terms as Lang.Array<Lang.Number> = TERMS;
 var names as Lang.Array<Lang.String> = NAMES;
 var lastDay=-1;
 var lunar="--";
 var lunarEn="--";
 var term="--";
 var termEn="--";
 function initialize() {}
 function refresh() {
  var n=Time.now();var g=Gregorian.info(n,Time.FORMAT_SHORT);
  // UTC noon for this local civil date avoids timezone offsets at midnight.
  var day=Gregorian.moment({:year=>g.year,:month=>g.month,:day=>g.day,:hour=>12}).value()/86400;
  if(day==lastDay){return;}lastDay=day;lunar="--";term="--";lunarEn="--";termEn="--";
  if(g.year<2020 || g.year>2040){return;}
  var m=0;var start=0;
  for(var i=0;i<months.size();i++){var d=months[i]/32;if(d>day){break;}m=months[i]%32;start=d;}
  var dd=day-start+1;var leap=m>=16;if(leap){m-=16;}
  var mn=["正","二","三","四","五","六","七","八","九","十","冬","腊"];
  var nn=["一","二","三","四","五","六","七","八","九","十"];
  var dn="";
  if(dd<=10){dn="初"+nn[dd-1];}else if(dd<20){dn="十"+nn[dd-11];}else if(dd==20){dn="二十";}else if(dd<30){dn="廿"+nn[dd-21];}else{dn="三十";}
  lunar=(leap?"闰":"")+mn[m-1]+"月"+dn;
  lunarEn=(leap?"L* ":"L ")+m.toString()+"/"+dd.toString();
  for(var j=0;j<terms.size();j++){var td=terms[j]/32;if(td>=day){var ix=terms[j]%32;term=(td==day?"":"+"+(td-day).toString()+"天 ")+names[ix];termEn="ST"+(ix+1).toString()+" +"+(td-day).toString()+"d";break;}}
 }
}
'''.replace('MONTHS',json.dumps(mt)).replace('TERMS',json.dumps(st)).replace('NAMES',json.dumps(terms,ensure_ascii=False))
(P/'source/CalendarData.mc').write_text(text)
(P/'tools/calendar-tables.json').write_text(json.dumps({'range':[2020,2040],'months':mt,'terms':st,'names':terms,'generator':'lunar-python '+importlib.metadata.version('lunar-python')},ensure_ascii=False))
print('Calendar:',len(mt),'lunar months,',len(st),'solar terms')

from ephemeris_resources import partition_calendar
partition_calendar(P,mt,st)
