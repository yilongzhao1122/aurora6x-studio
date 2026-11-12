import Toybox.WatchUi;
class AuroraSettingsDelegate extends WatchUi.BehaviorDelegate {
    var editor;
    function initialize(view){BehaviorDelegate.initialize();editor=view;}
    function onPreviousPage(){return editor.move(-1);}
    function onNextPage(){return editor.move(1);}
    function onSelect(){return editor.choose();}
    function onBack(){
        if(editor.back()){return true;}
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        return true;
    }
}
