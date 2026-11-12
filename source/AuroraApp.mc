import Toybox.Application;
import Toybox.WatchUi;
class AuroraApp extends Application.AppBase {
    var face;
    function initialize() { AppBase.initialize(); }
    function getInitialView() { face = new AuroraView(); return [face]; }
    function getSettingsView() {
        if(face!=null){face.releaseGraphics();}
        var editor=new AuroraSettingsView();
        return [editor,new AuroraSettingsDelegate(editor)];
    }
    function onSettingsChanged() {
        if (face != null) { face.loadSettings(); }
        WatchUi.requestUpdate();
    }
}
