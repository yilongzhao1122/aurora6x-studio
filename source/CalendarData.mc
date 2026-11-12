import Toybox.Application;
import Toybox.Time;
import Toybox.Lang;
import Toybox.Time.Gregorian;
// Generated calendar dates, local Gregorian date; terms use Chinese civil dates.
class CalendarData {
 var months as Lang.Array<Lang.Number> or Null=null;
 var terms as Lang.Array<Lang.Number> or Null=null;
 var loadedYear=-1;
 var names as Lang.Array<Lang.String> = ["小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"];
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
  if(loadedYear!=g.year){
   months=null;terms=null;
   var ids=[Rez.JsonData.Calendar2020,Rez.JsonData.Calendar2021,Rez.JsonData.Calendar2022,Rez.JsonData.Calendar2023,Rez.JsonData.Calendar2024,Rez.JsonData.Calendar2025,Rez.JsonData.Calendar2026,Rez.JsonData.Calendar2027,Rez.JsonData.Calendar2028,Rez.JsonData.Calendar2029,Rez.JsonData.Calendar2030,Rez.JsonData.Calendar2031,Rez.JsonData.Calendar2032,Rez.JsonData.Calendar2033,Rez.JsonData.Calendar2034,Rez.JsonData.Calendar2035,Rez.JsonData.Calendar2036,Rez.JsonData.Calendar2037,Rez.JsonData.Calendar2038,Rez.JsonData.Calendar2039,Rez.JsonData.Calendar2040];
   var row=Application.loadResource(ids[g.year-2020]) as Lang.Dictionary;months=row["months"] as Lang.Array<Lang.Number>;terms=row["terms"] as Lang.Array<Lang.Number>;loadedYear=g.year;
  }
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
