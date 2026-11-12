import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

// A single View owns the three navigation levels: no growing stack of menus.
// Fonts and choices are separate resources; the watchface never loads these.
class AuroraSettingsView extends WatchUi.View {
    var font=null;var language=0;var level=0;var group=0;var row=0;var choice=0;
    var rows as Lang.Array<Lang.Array<Lang.String or Lang.Number>> or Null=null;
    var options as Lang.Array<Lang.Array<Lang.String>> or Null=null;
    var key="";var selected=-1;var notice=0;
    function initialize(){
        View.initialize();
        var l=Application.Properties.getValue("Language");if(l==1){language=1;}
    }
    function onLayout(dc){font=WatchUi.loadResource(Rez.Fonts.Menu);}
    function onShow(){WatchUi.requestUpdate();}
    function onHide(){font=null;}
    function name(zh,en){return language==0?zh:en;}
    function groupName(n){
        if(n==0){return name("顶部与图标","Top & icons");}
        if(n==1){return name("下方数据","Lower fields");}
        return name("时间与外观","Time & style");
    }
    function loadGroup(){
        var ids=[Rez.JsonData.MenuGroup0,Rez.JsonData.MenuGroup1,Rez.JsonData.MenuGroup2];
        rows=Application.loadResource(ids[group]);
    }
    function loadOptions(){
        // Clear the previous resource before decoding another list.
        options=null;
        if(key.equals("SecondOffset")){return true;}
        // Resource-loaded strings require content equality in Monkey C.
        // Only the four metric cells may open the shared 29-item list.
        var id=null;
        if(key.equals("A0")){id=Rez.JsonData.MenuOptionsA0;}
        else if(key.equals("A1")){id=Rez.JsonData.MenuOptionsA1;}
        else if(key.equals("A2")){id=Rez.JsonData.MenuOptionsA2;}
        else if(key.equals("A3")){id=Rez.JsonData.MenuOptionsA3;}
        else if(key.equals("A4")){id=Rez.JsonData.MenuOptionsA4;}
        else if(key.equals("C0")){id=Rez.JsonData.MenuOptionsC0;}
        else if(key.equals("C1")){id=Rez.JsonData.MenuOptionsC1;}
        else if(key.equals("C6")){id=Rez.JsonData.MenuOptionsC6;}
        else if(key.equals("B2")){id=Rez.JsonData.MenuOptionsB2;}
        else if(key.equals("Language")){id=Rez.JsonData.MenuOptionsLanguage;}
        else if(key.equals("TimeTypeface")){id=Rez.JsonData.MenuOptionsTimeTypeface;}
        else if(key.equals("DataTypeface")){id=Rez.JsonData.MenuOptionsDataTypeface;}
        else if(key.equals("Backdrop")){id=Rez.JsonData.MenuOptionsBackdrop;}
        else if(key.equals("C2") || key.equals("C3") || key.equals("C4") || key.equals("C5")){id=Rez.JsonData.MenuOptionsMetrics;}
        if(id==null){System.println("AURORA unknown settings key: "+key);return false;}
        options=Application.loadResource(id);
        return true;
    }
    function metricField(){return key.equals("C2") || key.equals("C3") || key.equals("C4") || key.equals("C5");}
    function count(){
        if(level==0){return 3;}if(level==1){return rows.size();}
        return key.equals("SecondOffset")?47:options.size();
    }
    function index(){return level==0?group:(level==1?row:choice);}
    function move(delta){
        notice=0;
        var n=(index()+delta+count())%count();
        if(level==0){group=n;}else if(level==1){row=n;}else{choice=n;}
        WatchUi.requestUpdate();return true;
    }
    function choose(){
        notice=0;
        if(level==0){loadGroup();row=0;level=1;}
        else if(level==1){
            key=rows[row][0];
            if(!loadOptions()){notice=2;WatchUi.requestUpdate();return true;}
            level=2;
            var v=Application.Properties.getValue(key);
            selected=-1;
            if(v instanceof Lang.Number){selected=key.equals("SecondOffset")?v+23:v;}
            if(metricField()){if(selected==17){selected=3;}else if(selected>17){selected-=1;}}
            if(selected<0 || selected>=count()){selected=-1;}
            choice=selected<0?0:selected;
        }else{
            if(choice<0 || choice>=count()){notice=2;WatchUi.requestUpdate();return true;}
            var value=key.equals("SecondOffset")?choice-23:choice;
            if(metricField() && value>=17){value+=1;}
            try{
                Application.Properties.setValue(key,value);
                // Show success only after the persistent property reads back.
                if(Application.Properties.getValue(key)==value){
                    selected=choice;notice=1;
                    if(key.equals("Language")){language=value;}
                    Application.getApp().onSettingsChanged();
                }else{notice=2;}
            }catch(e){notice=2;System.println("AURORA settings save failed: "+key);}
        }
        WatchUi.requestUpdate();return true;
    }
    function back(){
        notice=0;
        if(level==2){options=null;key="";level=1;}
        else if(level==1){rows=null;level=0;}
        else{return false;} // Delegate pops this settings view at the root.
        WatchUi.requestUpdate();return true;
    }
    function fit(dc,x,y,s,color,width){
        var text=s;
        if(dc.getTextWidthInPixels(text,font)>width){
            while(text.length()>0 && dc.getTextWidthInPixels(text+"..",font)>width){text=text.substring(0,text.length()-1);}
            text+="..";
        }
        dc.setColor(color,Graphics.COLOR_TRANSPARENT);
        dc.drawText(x,y,font,text,Graphics.TEXT_JUSTIFY_CENTER);
    }
    function onUpdate(dc){
        if(font==null){onLayout(dc);}
        dc.setColor(0xFFFFFF,0);dc.clear();
        var title=level==0?name("表盘设置","Watch face settings"):(level==1?groupName(group):key);
        fit(dc,140,27,title,0x55FFFF,180);
        var n=count();var at=index();
        fit(dc,140,49,(at+1).toString()+" / "+n.toString(),0xAAAAAA,160);
        var start=at-1;if(start<0){start=0;}if(start>n-3){start=n-3;}if(start<0){start=0;}
        for(var i=0;i<3;i++){
            var item=start+i;if(item>=n){break;}
            var y=79+i*48;var focused=item==at;
            if(focused){dc.setColor(0x005555,Graphics.COLOR_TRANSPARENT);dc.fillRectangle(26,y-3,228,46);dc.setColor(0x55FFFF,Graphics.COLOR_TRANSPARENT);dc.fillRectangle(26,y-3,3,46);}
            var top="";var sub="";
            if(level==0){top=groupName(item);sub=item==0?"A0 - A4":(item==1?"C0 - C6":"B2 / Language / Style");}
            else if(level==1){top=rows[item][0]+" "+rows[item][language==0?1:2];sub=name("START 选择","START to choose");}
            else if(key.equals("SecondOffset")){
                var h=item-23;top=(h>0?"+":"")+h.toString()+name(" 小时"," hours");sub=name("相对本地时间","Relative to local time");
            }else{
                top=options[item][language];sub=language==0?options[item][1]:"START to save";
            }
            fit(dc,140,y,top,focused?0xFFFFFF:0xAAAAAA,194);
            fit(dc,140,y+22,sub,0xAAAAAA,194);
            if(level==2 && item==selected){dc.setColor(0x55FFFF,Graphics.COLOR_TRANSPARENT);dc.fillCircle(244,y+8,3);}
        }
        var footer=name("START 选择","START choose");
        if(level==2){footer=name("START 保存","START save");}
        if(notice==1){footer=name("已保存","Saved");}
        if(notice==2){footer=name("保存失败 请重试","Save failed - retry");}
        fit(dc,140,222,footer,notice==2?0xFF5555:0x55FFFF,185);
        fit(dc,140,242,name("BACK 返回","BACK back"),0xAAAAAA,128);
    }
}
