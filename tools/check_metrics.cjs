// Behavioral checks execute translated Metrics.mc with API doubles, NOT Garmin VM.
const {build}=require('./preview_from_source.cjs');const assert=require('assert');
Object.defineProperty(Object.prototype,'hasKey',{value:function(k){return Object.prototype.hasOwnProperty.call(this,k)},enumerable:false,configurable:true});
let now=1794398400;
const moment=n=>({value:()=>n});
const info={currentHeartRate:67,currentOxygenSaturation:97,altitude:88,meanSeaLevelPressure:101325};
const monitor={steps:1234,stepGoal:8000,calories:456,distance:123400,floorsClimbed:7,moveBarLevel:1,respirationRate:14,timeToRecovery:3,activeMinutesDay:{total:40},activeMinutesWeek:{total:100}};
const stats={battery:77.0,solarIntensity:23};
let weather={observationTime:moment(now-60),temperature:24,relativeHumidity:65,precipitationChance:30,windSpeed:2.4,feelsLikeTemperature:23,lowTemperature:18,highTemperature:26,condition:3,observationLocationPosition:null};
let hrSamples=[{data:80,when:moment(now-30)}],oxySamples=[{data:95,when:moment(now-100)}],altSamples=[{data:1372,when:moment(now-30)}];
const iterator=xs=>{let i=0;return {next:()=>xs[i++]??null}};
const SensorHistory={ORDER_NEWEST_FIRST:1,getHeartRateHistory:()=>iterator(hrSamples),getOxygenSaturationHistory:()=>iterator(oxySamples),getElevationHistory:()=>iterator(altSamples),getBodyBatteryHistory:()=>iterator([{data:70,when:moment(now-60)}]),getStressHistory:()=>iterator([{data:20,when:moment(now-60)}])};
const Time={now:()=>moment(now),FORMAT_SHORT:0,Duration:function(n){this.n=n},Moment:function(n){this.value=()=>n}};
const Gregorian={info:m=>{const d=new Date(m.value()*1000);return {year:d.getUTCFullYear(),month:d.getUTCMonth()+1,day:d.getUTCDate()}}};
const Activity={getActivityInfo:()=>info,SPORT_RUNNING:1};const Weather={getCurrentConditions:()=>weather,getSunrise:()=>{throw Error('location unsupported')},getSunset:()=>null};
const UserProfile={getProfile:()=>({weight:65000,vo2maxRunning:49,vo2maxCycling:52,averageRestingHeartRate:55}),getUserActivityHistory:()=>iterator([])};
const logs=[];const System={getSystemStats:()=>stats,println:s=>logs.push(s)};
const globals={Activity,ActivityMonitor:{getInfo:()=>monitor},System,SensorHistory,UserProfile,Time,Gregorian,Weather,Toybox:{Weather},MoonData:function(){return {phase:()=>.2}}};
let m=build('Metrics.mc',globals);m.initialize();m.refresh(true);
for(const [k,v] of Object.entries({0:1234,1:8000,2:1.234,3:456,5:67,8:97,11:1013.25,12:88,13:65,14:23,21:77,22:24,27:18,28:26}))assert.equal(m.get(Number(k)),v,'key '+k);
assert.equal(m.get(17),456);assert(m.sources[5].includes('Activity.current'));
monitor.calories=0;m.refresh(true);assert.equal(m.get(3),0);assert.equal(m.get(17),0);
monitor.calories=null;m.refresh(true);assert.equal(m.get(3),null);assert.equal(m.get(17),null);
monitor.calories=456;m.refresh(true);
// Current values take priority over the simulator's default 80/1372/95 histories.
info.currentHeartRate=null;info.currentOxygenSaturation=null;info.altitude=null;now+=6;m.refresh(false);
assert.equal(m.get(5),80);assert.equal(m.get(8),95);assert.equal(m.get(12),1372);assert(m.sources[8].includes('history @'));
// Skip invalid newest sample, keep valid recent sample, and do not resurrect old samples.
hrSamples=[{data:null,when:moment(now)},{data:73,when:moment(now-60)}];now+=6;m.refresh(false);assert.equal(m.get(5),73);
hrSamples=[{data:73,when:moment(now-301)}];oxySamples=[{data:95,when:moment(now-86401)}];altSamples=[{data:1,when:moment(now+120)}];now+=6;m.refresh(false);
assert.equal(m.get(5),null);assert.equal(m.get(8),null);assert.equal(m.get(12),null);
// Genuine zero values are preserved; a negative solar status means not charging.
stats.solarIntensity=-1;monitor.steps=0;stats.battery=0;now+=6;m.refresh(false);assert.equal(m.get(14),0);assert.equal(m.get(0),0);assert.equal(m.get(21),0);
stats.solarIntensity=null;now+=6;m.refresh(false);assert.equal(m.get(14),null);
// Weather freshness and sun calculation are independent; no stale retained temperature.
weather.observationTime=moment(now-7201);m.refresh(true);assert.equal(m.get(22),null);assert.equal(m.weather,null);
weather.observationTime=moment(now);weather.observationLocationPosition={};m.refresh(true);assert.equal(m.get(22),24);assert(m.weather);assert.equal(m.nextSun,null);
weather.observationTime=null;m.refresh(true);assert.equal(m.get(22),null);assert.equal(m.weatherStatus,'observation time missing');
// Five-second gate and rewinding the simulator clock.
info.currentHeartRate=60;m.refresh(true);info.currentHeartRate=61;now+=1;m.refresh(false);assert.equal(m.get(5),60);now-=1000;m.refresh(false);assert.equal(m.get(5),61);
m.debug=true;m.refresh(true);assert(logs.some(s=>s.includes('source=Activity.currentHeartRate')));
console.log('PASS Metrics.mc: live/history priority, units, missing/stale/future/invalid samples, zero/solar status, weather isolation, refresh gate, clock rewind, source logs.');
