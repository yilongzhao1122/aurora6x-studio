import Toybox.ActivityMonitor;
import Toybox.Activity;
import Toybox.SensorHistory;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.UserProfile;
import Toybox.Weather;
import Toybox.Math;
import Toybox.Lang;

// Values use explicit units. Missing/stale data remains null, never invented.
class Metrics {
    var values as Lang.Dictionary = {};
    var weather = null;
    var lastRead = -1000;
    var lastActivityScan=-100000;
    var activityMonth=-1;
    var monthKm=null;
    var hr = null;
    var hrLow=null;
    var hrHigh=null;
    var moveLevel=0;
    var moonPhase=null;
    var moon;
    var lastFast=-1000;
    var debug=false;
    var lastLog=-1000;
    var sources as Lang.Dictionary={};
    var sampleTime=null;
    var weatherAge=null;
    var weatherStatus="not read";
    var nextSun=null;
    var nextSunIsRise=true;
    var rise = null;
    var set = null;
    var labels as Lang.Array<Lang.String> = ["STEPS","GOAL","KM","KCAL","FLOOR","HR","BODY","STRESS",
        "SpO2","RESP","REC h","hPa","ALT m","KG","SOLAR%","DAY min",
        "WK min","ACT KC","BIKE VO2","RUN VO2","MONTH km","BAT%","TEMP C",
        "HUM%","RAIN%","WIND m/s","FEEL C","LOW C","HIGH C","REST HR"];

    function initialize() { moon=new MoonData(); }
    function valid(v,low,high){return v!=null && v>=low && v<=high;}
    function sample(iterator,maxAge,low,high){
        sampleTime=null;
        if(iterator==null){return null;}
        var now=Time.now().value();var count=0;var s=iterator.next();
        while(s!=null && count<30){
            if(s.when!=null){
                var age=now-s.when.value();
                if(age>maxAge){return null;}
                if(age>=-60 && valid(s.data,low,high)){sampleTime=s.when.value();return s.data;}
            }
            s=iterator.next();count++;
        }
        return null;
    }
    function put(key,value){values[key]=value;}
    function record(key,value,source){values[key]=value;sources[key]=value==null?"missing":source;}
    function history(key,iterator,maxAge,low,high){
        var value=sample(iterator,maxAge,low,high);
        record(key,value,value==null?"missing":"history @"+sampleTime.toString());
    }
    function get(key){return values.hasKey(key)?values[key]:null;}
    function integer(value){return value==null?"--":value.format("%.0f");}
    function text(key){
        var v=get(key);if(v==null){return "--";}
        if(key==2 || key==13 || key==20 || key==25){return v.format("%.1f");}
        return integer(v);
    }
    function refresh(force){
        var now=Time.now().value();
        if(!force && now>=lastFast && now-lastFast<5){return;}
        lastFast=now;
        // Clear fast readings first: a failed/missing API must not retain yesterday's value.
        var fast=[0,1,2,3,4,5,8,9,10,11,12,14,15,16,21];
        for(var j=0;j<fast.size();j++){record(fast[j],null,"missing");}
        moveLevel=0;
        try{
            var a=ActivityMonitor.getInfo();
            record(0,a.steps,"ActivityMonitor.steps");record(1,a.stepGoal,"ActivityMonitor.stepGoal");record(3,a.calories,"ActivityMonitor.calories");
            if(a.distance!=null){record(2,a.distance/100000.0,"ActivityMonitor.distance cm -> km");}
            if(a has :moveBarLevel && a.moveBarLevel!=null){moveLevel=a.moveBarLevel;}
            if(a has :floorsClimbed){record(4,a.floorsClimbed,"ActivityMonitor.floorsClimbed");}
            if(a has :respirationRate){record(9,a.respirationRate,"ActivityMonitor.respirationRate");}
            if(a has :timeToRecovery){record(10,a.timeToRecovery,"ActivityMonitor.timeToRecovery hours");}
            if(a has :activeMinutesDay && a.activeMinutesDay!=null){record(15,a.activeMinutesDay.total,"ActivityMonitor.activeMinutesDay.total");}
            if(a has :activeMinutesWeek && a.activeMinutesWeek!=null){record(16,a.activeMinutesWeek.total,"ActivityMonitor.activeMinutesWeek.total");}
        }catch(e){if(debug){System.println("ActivityMonitor: "+e.getErrorMessage());}}
        record(17,get(3),"ActivityMonitor.calories (legacy active slot -> total)");
        try{
            var st=System.getSystemStats();record(21,st.battery,"System.battery");
            if(st has :solarIntensity && st.solarIntensity!=null){
                // Official API: negative = not currently charging, null = unsupported.
                if(st.solarIntensity<0){record(14,0,"System.solarIntensity negative: not charging");}
                else if(st.solarIntensity<=100){record(14,st.solarIntensity,"System.solarIntensity");}
            }
        }catch(e){if(debug){System.println("SystemStats: "+e.getErrorMessage());}}
        try{
            var info=Activity.getActivityInfo();
            if(valid(info.currentHeartRate,1,250)){record(5,info.currentHeartRate,"Activity.currentHeartRate");}
            if(info has :currentOxygenSaturation && valid(info.currentOxygenSaturation,1,100)){record(8,info.currentOxygenSaturation,"Activity.currentOxygenSaturation (API has no timestamp)");}
            if(valid(info.altitude,-1000,10000)){record(12,info.altitude,"Activity.altitude");}
            if(info has :meanSeaLevelPressure && valid(info.meanSeaLevelPressure,10000,120000)){record(11,info.meanSeaLevelPressure/100.0,"Activity.meanSeaLevelPressure Pa -> hPa");}
        }catch(e){if(debug){System.println("Activity: "+e.getErrorMessage());}}
        var opts={:period=>30,:order=>SensorHistory.ORDER_NEWEST_FIRST};
        if(get(5)==null){try{history(5,SensorHistory.getHeartRateHistory(opts),300,1,250);}catch(e){}}
        if(get(8)==null && SensorHistory has :getOxygenSaturationHistory){try{history(8,SensorHistory.getOxygenSaturationHistory(opts),86400,1,100);}catch(e){}}
        if(get(12)==null){try{history(12,SensorHistory.getElevationHistory(opts),3600,-1000,10000);}catch(e){}}
        hr=get(5);
        if(force || now<lastRead || now-lastRead>=60){
            lastRead=now;readSlow(now,opts);
        }
        if(debug && (now<lastLog || now-lastLog>=30)){
            lastLog=now;System.println("AURORA3 t="+now+" weather="+weatherStatus+" ageSec="+weatherAge+" moonPhase="+moonPhase);
            for(var i=0;i<29;i++){System.println(labels[i]+"="+text(i)+" source="+(sources.hasKey(i)?sources[i]:"unavailable"));}
        }
    }
    function readSlow(now,opts){
        var slow=[6,7,13,18,19,22,23,24,25,26,27,28,29];
        for(var j=0;j<slow.size();j++){record(slow[j],null,"missing");}
        hrLow=null;hrHigh=null;
        if(SensorHistory has :getBodyBatteryHistory){try{history(6,SensorHistory.getBodyBatteryHistory(opts),3600,0,100);}catch(e){}}
        if(SensorHistory has :getStressHistory){try{history(7,SensorHistory.getStressHistory(opts),3600,0,100);}catch(e){}}
        try{
            var p=UserProfile.getProfile();
            if(p.weight!=null){record(13,p.weight/1000.0,"UserProfile.weight g -> kg");}
            if(p has :vo2maxRunning){record(19,p.vo2maxRunning,"UserProfile.vo2maxRunning");}
            if(p has :vo2maxCycling){record(18,p.vo2maxCycling,"UserProfile.vo2maxCycling");}
            if(p has :averageRestingHeartRate){record(29,p.averageRestingHeartRate,"UserProfile.averageRestingHeartRate");}
        }catch(e){}
        moonPhase=moon.phase(now);
        readExtras();
        weather=null;weatherAge=null;weatherStatus="no cache";rise=null;set=null;nextSun=null;
        if(Toybox has :Weather){
            try{
                var w=Weather.getCurrentConditions();
                if(w!=null && w.observationTime!=null){
                    weatherAge=now-w.observationTime.value();
                    if(weatherAge>=-300 && weatherAge<=7200){weather=w;weatherStatus="cached conditions";}
                    else{weatherStatus="stale or future observation";}
                }else if(w!=null){weatherStatus="observation time missing";}
            }catch(e){weatherStatus="API error";}
            if(weather!=null){
                record(22,weather.temperature,"Weather.temperature C");record(23,weather.relativeHumidity,"Weather.relativeHumidity");
                record(24,weather.precipitationChance,"Weather.precipitationChance");record(25,weather.windSpeed,"Weather.windSpeed m/s");
                record(26,weather.feelsLikeTemperature,"Weather.feelsLikeTemperature");record(27,weather.lowTemperature,"Weather.lowTemperature");record(28,weather.highTemperature,"Weather.highTemperature");
                // Location/sun API failures must not discard valid temperature or weather icons.
                try{
                    if(weather.observationLocationPosition!=null && Weather has :getSunrise && Weather has :getSunset){
                        rise=Weather.getSunrise(weather.observationLocationPosition,Time.now());set=Weather.getSunset(weather.observationLocationPosition,Time.now());
                        if(rise!=null && rise.value()>now){nextSun=rise;nextSunIsRise=true;}
                        else if(set!=null && set.value()>now){nextSun=set;nextSunIsRise=false;}
                        else{nextSun=Weather.getSunrise(weather.observationLocationPosition,new Time.Moment(now+86400));nextSunIsRise=true;}
                    }
                }catch(e){nextSun=null;}
            }
        }
    }
    function readExtras(){
        // Extrema of available samples from today's local date, not a promise of all-day coverage.
        try {
            var today=Gregorian.info(Time.now(),Time.FORMAT_SHORT);
            var it=SensorHistory.getHeartRateHistory({:period=>new Time.Duration(86400),:order=>SensorHistory.ORDER_NEWEST_FIRST});
            var s=it.next();var count=0;
            while(s!=null && count<1500){
                if(s.when!=null && s.data!=null && s.data>0 && s.data<=250){
                    var date=Gregorian.info(s.when,Time.FORMAT_SHORT);
                    if(date.year!=today.year || date.month!=today.month || date.day!=today.day){break;}
                    if(hrLow==null || s.data<hrLow){hrLow=s.data;}
                    if(hrHigh==null || s.data>hrHigh){hrHigh=s.data;}
                }
                s=it.next();count++;
            }
        } catch(e) {}
        // Sum records exposed by the device. Garmin does not promise complete cloud history.
        var gd=Gregorian.info(Time.now(),Time.FORMAT_SHORT);var mk=gd.year*12+gd.month;
        if(mk==activityMonth && Time.now().value()>=lastActivityScan && Time.now().value()-lastActivityScan<1800){record(20,monthKm,"UserProfile exposed running records (may be incomplete)");return;}
        activityMonth=mk;lastActivityScan=Time.now().value();monthKm=null;
        if(UserProfile has :getUserActivityHistory){
            try {
                var today=Gregorian.info(Time.now(),Time.FORMAT_SHORT);
                var it=UserProfile.getUserActivityHistory();var a=it.next();var sum=0.0;var count=0;
                while(a!=null && count<500){
                    if(a.startTime!=null && a.distance!=null && a.type==Activity.SPORT_RUNNING){
                        var d=Gregorian.info(a.startTime,Time.FORMAT_SHORT);
                        if(d.year==today.year && d.month==today.month){sum+=a.distance/1000.0;}
                    }
                    a=it.next();count++;
                }
                monthKm=count>0?sum:null;record(20,monthKm,"UserProfile exposed running records (may be incomplete)");
            } catch(e) {}
        }
    }
    function sunText(moment) {
        if (moment == null) { return "--:--"; }
        var t = Gregorian.info(moment,Time.FORMAT_SHORT);
        return t.hour.format("%02d")+":"+t.min.format("%02d");
    }
    function windText() {
        if (weather == null || weather.windBearing == null) { return "--"; }
        var names=["N","NE","E","SE","S","SW","W","NW"];
        return names[((weather.windBearing+22.5)/45).toNumber()%8];
    }
}
