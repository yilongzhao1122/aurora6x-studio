import Toybox.Lang;
import Toybox.Application;
import Toybox.Time;
import Toybox.Time.Gregorian;
class MoonData {
 var events as Lang.Array<Lang.Number> or Null=null;
 var loadedYear=-1;
 function initialize(){}
 function phase(now){
  var minute=(now-1577836800)/60.0;
  if(minute<0 || minute>=11046240){events=null;loadedYear=-1;return null;}
  // Use local year; each resource has >=24h overlap for UTC/local year boundaries.
  var year=Gregorian.info(new Time.Moment(now),Time.FORMAT_SHORT).year;
  if(year<2020){year=2020;}if(year>2040){year=2040;}
  if(events==null || loadedYear!=year){
   events=null;
   var ids=[Rez.JsonData.Moon2020,Rez.JsonData.Moon2021,Rez.JsonData.Moon2022,Rez.JsonData.Moon2023,Rez.JsonData.Moon2024,Rez.JsonData.Moon2025,Rez.JsonData.Moon2026,Rez.JsonData.Moon2027,Rez.JsonData.Moon2028,Rez.JsonData.Moon2029,Rez.JsonData.Moon2030,Rez.JsonData.Moon2031,Rez.JsonData.Moon2032,Rez.JsonData.Moon2033,Rez.JsonData.Moon2034,Rez.JsonData.Moon2035,Rez.JsonData.Moon2036,Rez.JsonData.Moon2037,Rez.JsonData.Moon2038,Rez.JsonData.Moon2039,Rez.JsonData.Moon2040];
   events=Application.loadResource(ids[year-2020]) as Lang.Array<Lang.Number>;loadedYear=year;
  }
  var lo=1;var hi=events.size()-1;
  while(hi-lo>1){var mid=((lo+hi)/2).toNumber();if(events[mid]<=minute){lo=mid;}else{hi=mid;}}
  return (((events[0]+lo-1)%8)+(minute-events[lo])/(events[hi]-events[lo]))/8.0;
 }
}
