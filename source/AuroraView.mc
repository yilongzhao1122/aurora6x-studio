import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

class AuroraView extends WatchUi.WatchFace {
    var data; var calendar;var icons;
    var smallPlus;var ringFont;
    var small;var medium;var loadedTimeFace=-1;var loadedDataFace=-1;var timeFont;var secFont;var panelImage=null;var loadedBackdrop=-1;
    var panelFallback=false;var memoryReported=false;
    var settings as Lang.Dictionary={};var sleeping=false;var ink=0xFFFFFF;
    var progressColors as Lang.Array<Lang.Number> = [0x55FFFF,0x00FFFF,0x55AAFF,0xFF5500,0xAAAAAA];
    var fieldIcons as Lang.Array<Lang.Number> =[0,1,2,3,4,5,27,28,26,9,10,11,12,13,14,10,10,3,29,30,30,6,15,31,33,17,15,18,19];
    function initialize(){WatchFace.initialize();data=new Metrics();calendar=new CalendarData();icons=new FaceIcons();loadSettings();}
    function loadSettings(){
        var keys=["Language","A0","A1","A2","A3","A4","B2","C0","C1","C2","C3","C4","C5","C6","CustomText","SecondOffset","Backdrop","BackgroundColor","DataColor","DebugLog"];
        var defs=[0,0,0,1,1,0,0,0,0,0,12,1,3,2,"AURORA",-8,2,16777215,16777215,0];
        // Validate the enum settings before indexing arrays. Older menus could save
        // a 29-item metric index into a 3/4-item field. Keep valid saved choices.
        var bounds=[1,6,3,4,3,2,1,3,3,28,28,28,28,6];
        for(var i=0;i<keys.size();i++){
            var v=Application.Properties.getValue(keys[i]);
            if(i<bounds.size()){
                if(!(v instanceof Lang.Number) || v<0 || v>bounds[i]){v=defs[i];}
            }
            if(i==15){if(!(v instanceof Lang.Number) || v<(-23) || v>23){v=defs[i];}}
            if(i==16){if(!(v instanceof Lang.Number) || v<0 || v>32){v=defs[i];}}
            settings[keys[i]]=v==null?defs[i]:v;
        }
        var tf=Application.Properties.getValue("TimeTypeface");var df=Application.Properties.getValue("DataTypeface");
        if(!(tf instanceof Lang.Number) || tf<0 || tf>5){tf=0;}
        if(!(df instanceof Lang.Number) || df<0 || df>5){df=2;}
        settings["TimeTypeface"]=tf;settings["DataTypeface"]=df;
        if(tf!=loadedTimeFace || df!=loadedDataFace){releaseGraphics();}
        ink=settings["DataColor"];
        if(data!=null){data.lastRead=-1000;data.lastFast=-1000;data.debug=settings["DebugLog"]==1;}
        if(loadedBackdrop!=settings["Backdrop"]){panelImage=null;loadedBackdrop=-1;panelFallback=false;}
    }
    function onLayout(dc){
        icons.load();
        smallPlus=WatchUi.loadResource(Rez.Fonts.SmallPlus);
        var ringFonts=[Rez.Fonts.Ring0,Rez.Fonts.Ring1,Rez.Fonts.Ring2,Rez.Fonts.Ring3,Rez.Fonts.Ring4,Rez.Fonts.Ring5];
        ringFont=WatchUi.loadResource(ringFonts[settings["DataTypeface"]]);
        small=WatchUi.loadResource(Rez.Fonts.Small);var dataFonts=[Rez.Fonts.Data0,Rez.Fonts.Data1,Rez.Fonts.Data2,Rez.Fonts.Data3,Rez.Fonts.Data4,Rez.Fonts.Data5];
        medium=WatchUi.loadResource(dataFonts[settings["DataTypeface"]]);
        var timeFonts=[Rez.Fonts.Time0,Rez.Fonts.Time1,Rez.Fonts.Time2,Rez.Fonts.Time3,Rez.Fonts.Time4,Rez.Fonts.Time5];
        var secondFonts=[Rez.Fonts.Sec0,Rez.Fonts.Sec1,Rez.Fonts.Sec2,Rez.Fonts.Sec3,Rez.Fonts.Sec4,Rez.Fonts.Sec5];
        timeFont=WatchUi.loadResource(timeFonts[settings["TimeTypeface"]]);secFont=WatchUi.loadResource(secondFonts[settings["TimeTypeface"]]);
        loadedTimeFace=settings["TimeTypeface"];loadedDataFace=settings["DataTypeface"];
    }
    function releaseGraphics(){
        panelImage=null;loadedBackdrop=-1;panelFallback=false;
        small=null;medium=null;timeFont=null;secFont=null;
        smallPlus=null;ringFont=null;
        if(icons!=null){icons.small=null;icons.large=null;}
    }
    function onShow(){loadSettings();}
    function onEnterSleep(){sleeping=true;}
    function onExitSleep(){sleeping=false;WatchUi.requestUpdate();}
    function label(dc,x,y,text,color,font){dc.setColor(color,Graphics.COLOR_TRANSPARENT);dc.drawText(x,y,font,text,Graphics.TEXT_JUSTIFY_CENTER);}
    function fit(dc,x,y,text,color,font,maxWidth){
        var shown=text;
        if(dc.getTextWidthInPixels(shown,font)>maxWidth){
            while(shown.length()>0 && dc.getTextWidthInPixels(shown+"..",font)>maxWidth){shown=shown.substring(0,shown.length()-1);}shown+="..";
        }
        label(dc,x,y,shown,color,font);
    }
    function line(dc,x1,y1,x2,y2,color){dc.setColor(color,Graphics.COLOR_TRANSPARENT);dc.drawLine(x1,y1,x2,y2);}
    function secondTime(){
        var t=System.getClockTime();var minutes=t.hour*60+t.min+settings["SecondOffset"]*60;
        while(minutes<0){minutes+=1440;}minutes=minutes%1440;
        return (minutes/60).format("%02d")+":"+(minutes%60).format("%02d");
    }
    function tempText(){return data.text(22)+"°C "+data.text(27)+"°/"+data.text(28)+"°";}
    function lunarText(){return settings["Language"]==0?calendar.lunar:calendar.lunarEn;}
    function termText(){return settings["Language"]==0?calendar.term:calendar.termEn;}
    function stripText(mode){
        if(mode==2){return tempText();}if(mode==3){return lunarText();}if(mode==4){return termText();}
        if(mode==5){return secondTime();}if(mode==6){return data.sunText(data.nextSun);}
        if(mode==7){return settings["CustomText"];}return "";
    }
    function statusIcons(dc,cx,y){
        var d=System.getDeviceSettings();
        icons.draw(dc,20,cx-37,y,d.phoneConnected?ink:0x555555);
        var silent=false;if(d has :doNotDisturb){silent=d.doNotDisturb;}
        icons.draw(dc,23,cx-17,y,silent?ink:0x555555);
        var alarm=false;if(d has :alarmCount){alarm=d.alarmCount>0;}
        icons.draw(dc,21,cx+3,y,alarm?ink:0x555555);
        icons.draw(dc,22,cx+23,y,d.notificationCount>0?ink:0x555555);
    }
    function strip(dc,mode,y,width){
        if(mode==0){icons.draw(dc,6,110,y+2,0x55FF00);fit(dc,155,y,data.text(21)+"%",ink,smallPlus,58);}
        else if(mode==1){statusIcons(dc,140,y);}
        else if(mode==6){icons.draw(dc,data.nextSunIsRise?24:25,105,y+1,ink);label(dc,150,y,stripText(mode),ink,smallPlus);}
        else{fit(dc,140,y,stripText(mode),ink,smallPlus,width);}
    }
    function miniIcon(dc,mode,x,y){
        var cyan=0x55FFFF;
        if(mode==0){
            var id=37;
            if(data.weather!=null){
                var c=data.weather.condition;
                if(c==0 || c==40){id=39;}
                else if(c==1 || c==22 || c==23 || c==52){id=32;}
                else if(c==2 || c==20){id=16;}
                else if(c==5 || c==32 || c==36 || c==41 || c==42){id=17;}
                else if(c==6 || c==12 || c==28){id=35;}
                else if(c==4 || c==7 || c==10 || c==16 || c==17 || c==18 || c==19 || c==21 || c==34 || c==43 || c==44 || c==46 || c==47 || c==48 || c==49 || c==50 || c==51){id=34;}
                else if(c==3 || c==11 || c==13 || c==14 || c==15 || c==24 || c==25 || c==26 || c==27 || c==31 || c==45){id=33;}
                else if(c==8 || c==9 || c==29 || c==30 || c==33 || c==35 || c==37 || c==38 || c==39){id=36;}
            }
            icons.drawBig(dc,id,x-4,y-4,cyan);
        }else if(mode==1){
            if(data.weather==null || data.weather.windBearing==null){icons.drawBig(dc,37,x-4,y-4,0xAAAAAA);return;}
            var a=data.weather.windBearing*Math.PI/180;
            var pts=[];var vx=[0,-7,0,7];var vy=[-10,8,4,8];
            for(var j=0;j<4;j++){pts.add([x+8+(vx[j]*Math.cos(a)-vy[j]*Math.sin(a)).toNumber(),y+8+(vx[j]*Math.sin(a)+vy[j]*Math.cos(a)).toNumber()]);}
            dc.setColor(cyan,Graphics.COLOR_TRANSPARENT);dc.fillPolygon(pts);
            dc.setColor(0,Graphics.COLOR_TRANSPARENT);dc.drawLine(x+8,y+8,x+8+(10*Math.sin(a)).toNumber(),y+8-(10*Math.cos(a)).toNumber());
        }else if(mode==2){
            icons.drawBig(dc,38,x-4,y-5,data.moveLevel>0?0xFFAA00:cyan);
            for(var i=0;i<5;i++){line(dc,x-1+i*4,y+19,x+1+i*4,y+19,data.moveLevel>i?0xFFAA00:0x555555);}
        }else{
            if(data.moonPhase==null){icons.drawBig(dc,37,x-4,y-4,0xAAAAAA);return;}
            var phase=data.moonPhase;var k=Math.cos(phase*2*Math.PI);
            dc.setColor(0x555555,Graphics.COLOR_TRANSPARENT);dc.fillCircle(x+8,y+8,10);
            dc.setColor(ink,Graphics.COLOR_TRANSPARENT);
            for(var yy=-9;yy<=9;yy++){
                var h=Math.sqrt(100-yy*yy);
                var l=phase<0.5?(h*k).toNumber():-h.toNumber();
                var r=phase<0.5?h.toNumber():-(h*k).toNumber();
                if(r>=l){dc.drawLine(x+8+l,y+8+yy,x+8+r,y+8+yy);}
            }
            dc.setColor(0xAAAAAA,Graphics.COLOR_TRANSPARENT);dc.drawCircle(x+8,y+8,10);
        }
    }
    function drawPanel(dc){
        var b=settings["Backdrop"];
        if(b!=4){
            if(panelImage==null && !panelFallback){
                var st=System.getSystemStats();
                System.println("AURORA 3.3.2 before panel: used="+st.usedMemory+" free="+st.freeMemory+" total="+st.totalMemory);
                // Conservative reserve: largest indexed panel is ~14.5KB, allow transfer/VM overhead.
                if(st.freeMemory<48000){
                    panelFallback=true;System.println("AURORA: low memory; using geometric panel fallback");
                }else{
                    var ids=[Rez.Drawables.Panel0,Rez.Drawables.Panel1,Rez.Drawables.Panel2,Rez.Drawables.Panel3,null,Rez.Drawables.Panel5,Rez.Drawables.Panel6,Rez.Drawables.Panel7,Rez.Drawables.Panel8,Rez.Drawables.Panel9,Rez.Drawables.Panel10,Rez.Drawables.Panel11,Rez.Drawables.Panel12,Rez.Drawables.Panel13,Rez.Drawables.Panel14,Rez.Drawables.Panel15,Rez.Drawables.Panel16,Rez.Drawables.Panel17,Rez.Drawables.Panel18,Rez.Drawables.Panel19,Rez.Drawables.Panel20,Rez.Drawables.Panel21,Rez.Drawables.Panel22,Rez.Drawables.Panel23,Rez.Drawables.Panel24,Rez.Drawables.Panel25,Rez.Drawables.Panel26,Rez.Drawables.Panel27,Rez.Drawables.Panel28,Rez.Drawables.Panel29,Rez.Drawables.Panel30,Rez.Drawables.Panel31,Rez.Drawables.Panel32];
                    panelImage=WatchUi.loadResource(ids[b]);loadedBackdrop=b;
                    st=System.getSystemStats();System.println("AURORA 3.3.2 after panel: used="+st.usedMemory+" free="+st.freeMemory);
                }
            }
            if(panelImage!=null){dc.drawBitmap(16,64,panelImage);}else{fallbackPanel(dc,b);}
        }else{
            var points=[[18,157],[18,109],[22,91],[38,67],[116,67],[138,94],[260,94],[264,108],[264,135],[207,135],[179,174],[115,174],[104,159]];
            dc.setColor(settings["BackgroundColor"],Graphics.COLOR_TRANSPARENT);dc.fillPolygon(points);
            dc.setColor(0xAAAAAA,Graphics.COLOR_TRANSPARENT);for(var pi=0;pi<points.size();pi++){var pj=(pi+1)%points.size();dc.drawLine(points[pi][0],points[pi][1],points[pj][0],points[pj][1]);}
            line(dc,22,92,116,92,0);line(dc,116,92,138,95,0);
            line(dc,116,174,116,157,0);line(dc,116,157,178,157,0);line(dc,178,157,187,163,0);
            line(dc,207,97,211,102,0);line(dc,211,102,211,132,0);
        }
    }
    function fallbackPanel(dc,b){
        // No bitmap allocation. Keep the same panel contour and black clock readability.
        var colors=[0xFFAAFF,0xAAAAFF,0xAAFFFF,0xFFFFAA,0xFFFFFF,0xAAFFAA,0xFFAAAA,0xAAAAFF,0xFFFFAA,0xAAFFFF,0xFFAAAA,0xFFFFFF,0xFFAAFF];
        var points=[[18,157],[18,109],[22,91],[38,67],[116,67],[138,94],[260,94],[264,108],[264,135],[207,135],[179,174],[115,174],[104,159]];
        dc.setColor(0xFFFFFF,Graphics.COLOR_TRANSPARENT);dc.fillPolygon(points);
        dc.setColor(colors[b%colors.size()],Graphics.COLOR_TRANSPARENT);
        dc.fillPolygon([[24,93],[116,93],[132,111],[79,156],[19,156],[19,109]]);
        dc.fillRectangle(213,97,48,36);
        line(dc,22,92,116,92,0);line(dc,116,92,138,95,0);
        line(dc,116,157,178,157,0);line(dc,207,97,211,102,0);line(dc,211,102,211,132,0);
    }
    function progress(dc){
        var key=[21,0,6,7][settings["C0"]];var cur=data.get(key);var goal=settings["C0"]==1?data.get(1):100;
        var ratio=0.0;if(cur!=null && goal!=null && goal>0){ratio=cur.toFloat()/goal;}
        if(ratio<0){ratio=0.0;}if(ratio>1){ratio=1.0;}
        for(var i=0;i<5;i++){
            var x=207+i*9;dc.setColor(ratio>i/5.0?progressColors[i]:0x333333,Graphics.COLOR_TRANSPARENT);
            dc.fillPolygon([[x,151],[x+8,139],[x+13,139],[x+5,151]]);
        }
        var text=(cur==null || goal==null || goal<=0)?"--":(ratio*100).format("%.0f")+"%";
        fit(dc,229,153,text,ink,medium,40);icons.draw(dc,settings["C0"]==0?7:fieldIcons[key],250,153,ink);
    }
    function hrRing(dc){
        // Garmin arc angles: zero=east, ninety=north.
        var mode=settings["C1"];
        dc.setPenWidth(7);dc.setColor(0xFFFFFF,Graphics.COLOR_TRANSPARENT);dc.drawArc(73,210,27,Graphics.ARC_CLOCKWISE,90,180);
        dc.setPenWidth(5);dc.setColor(0x000000,Graphics.COLOR_TRANSPARENT);dc.drawArc(73,210,27,Graphics.ARC_CLOCKWISE,90,180);
        dc.setPenWidth(3);
        dc.setColor(mode==0?0xFFFF00:(mode==2?0x00FF55:0xFF0000),Graphics.COLOR_TRANSPARENT);dc.drawArc(73,210,27,Graphics.ARC_CLOCKWISE,88,2);
        dc.setColor(mode==0?0x00FF55:0xFFFF00,Graphics.COLOR_TRANSPARENT);dc.drawArc(73,210,27,Graphics.ARC_CLOCKWISE,358,272);
        dc.setColor(mode==0 || mode==2?0xFF0000:0x00FF55,Graphics.COLOR_TRANSPARENT);dc.drawArc(73,210,27,Graphics.ARC_CLOCKWISE,268,182);
        dc.setPenWidth(1);
        var key=[5,6,7,21][mode];var value=data.get(key);
        var c=0xAAAAAA;
        if(value!=null){
            if(mode==0){c=value<60?0xFFFF00:(value<=100?0x00FF55:0xFF0055);}
            else if(mode==2){c=value<34?0x00FF55:(value<67?0xFFFF00:0xFF0055);}
            else{c=value<20?0xFF0055:(value<50?0xFFFF00:0x00FF55);}
        }
        fit(dc,47,180,data.text(key),ink,ringFont,38);icons.draw(dc,fieldIcons[key],65,202,c);
        if(value!=null){
            var maximum=mode==0?150:100;
            var hr=value;if(hr>maximum){hr=maximum;}if(hr<0){hr=0;}
            var a=(90-hr*270/maximum.toFloat())*Math.PI/180;
            var pts=[];var rr=[22,32,32];var aa=[a,a+0.17,a-0.17];
            for(var j=0;j<3;j++){pts.add([73+(rr[j]*Math.cos(aa[j])).toNumber(),210-(rr[j]*Math.sin(aa[j])).toNumber()]);}
            dc.setColor(c,Graphics.COLOR_TRANSPARENT);dc.fillPolygon(pts);
        }
    }
    function field(dc,key,x,y){
        icons.draw(dc,fieldIcons[key],x,y+1,ink);
        var text=data.text(key);var maxWidth=(x>180 && y>210)?40:56;var font=medium;
        if(dc.getTextWidthInPixels(text,font)>maxWidth){font=small;}
        if(dc.getTextWidthInPixels(text,font)>maxWidth){
            var v=data.get(key);
            if(v!=null && v>=1000000){text=(v/1000000.0).format("%.1f")+"M";}
            else if(v!=null && v>=10000){text=(v/1000.0).format("%.0f")+"k";}
        }
        // A compact value may still be too wide (e.g. an unusual negative value).
        // Keep a hard pixel boundary so thicker glyphs cannot reach the next slot.
        if(dc.getTextWidthInPixels(text,font)>maxWidth){
            while(text.length()>0 && dc.getTextWidthInPixels(text+"..",font)>maxWidth){text=text.substring(0,text.length()-1);}
            text+="..";
        }
        dc.setColor(ink,Graphics.COLOR_TRANSPARENT);dc.drawText(x+19,y,font,text,Graphics.TEXT_JUSTIFY_LEFT);
    }
    function onUpdate(dc){
        if(small==null){onLayout(dc);}
        data.refresh(false);calendar.refresh();
        dc.setColor(ink,0x000000);dc.clear();
        drawPanel(dc);
        line(dc,86,18,94,35,0xAAAAAA);line(dc,94,35,186,35,0xAAAAAA);line(dc,186,35,194,18,0xAAAAAA);
        strip(dc,settings["A0"],17,127);
        miniIcon(dc,settings["A1"],54,44);miniIcon(dc,settings["A3"],217,44);
        var upper="";var a2=settings["A2"];
        if(a2==0){upper=data.text(23)+"% / "+data.text(24)+"%";}else if(a2==1){upper=tempText();}else if(a2==2){upper=lunarText();}else if(a2==3){upper=termText();}else{upper=secondTime();}
        fit(dc,140,44,upper,ink,smallPlus,133);
        line(dc,39,64,118,64,0xAAAAAA);line(dc,118,64,139,91,0xAAAAAA);line(dc,139,91,257,91,0xAAAAAA);line(dc,137,65,240,65,0x555555);
        var paired="";var pairIcon=5;
        if(settings["A4"]==0){paired=data.integer(data.hrLow)+"/"+data.integer(data.hrHigh);}
        else if(settings["A4"]==1){paired=data.text(0)+"/"+data.text(1);pairIcon=0;}
        else{paired=data.text(3);pairIcon=3;}
        icons.draw(dc,pairIcon,156,73,ink);fit(dc,210,72,paired,ink,smallPlus,77);
        var clock=System.getClockTime();var date=Gregorian.info(Time.now(),Time.FORMAT_SHORT);
        var dateText=date.month.toString()+"/"+date.day.toString();var week=["SUN","MON","TUE","WED","THU","FRI","SAT"];
        if(settings["Language"]==0){dateText=date.month.toString()+"月"+date.day.toString()+"日";week=["星期日","星期一","星期二","星期三","星期四","星期五","星期六"];}
        var timeInk=0x000000;
        if(settings["Backdrop"]==4){var bg=settings["BackgroundColor"];var luminance=((bg>>16)&255)*299+((bg>>8)&255)*587+(bg&255)*114;if(luminance<120000){timeInk=0xFFFFFF;}}
        label(dc,80,69,dateText,timeInk,smallPlus);
        var h=clock.hour;
        if(!System.getDeviceSettings().is24Hour){h=h%12;if(h==0){h=12;}}
        label(dc,h>=10?111:119,96,h.toString()+":"+clock.min.format("%02d"),timeInk,timeFont);
        label(dc,148,156,week[date.day_of_week-1],timeInk,small);
        if(settings["B2"]==0 && !sleeping){label(dc,237,98,clock.sec.format("%02d"),timeInk,secFont);}
        if(!memoryReported){var st=System.getSystemStats();System.println("AURORA 3.3.2 first draw: used="+st.usedMemory+" free="+st.freeMemory);memoryReported=true;}
        progress(dc);
        line(dc,106,180,254,180,0x555555);line(dc,104,207,247,207,0x555555);line(dc,104,234,226,234,0x555555);
        line(dc,184,185,184,204,0x333333);line(dc,184,211,184,231,0x333333);
        hrRing(dc);
        field(dc,settings["C2"],106,184);field(dc,settings["C4"],189,184);
        field(dc,settings["C3"],106,210);field(dc,settings["C5"],189,210);
        strip(dc,settings["C6"]+1,241,153);
    }
}
