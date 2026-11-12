import Toybox.Graphics;
import Toybox.WatchUi;
import Toybox.Lang;
class FaceIcons {
 var small; var large;
 var glyphs as Lang.Array<Lang.String> = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""];
 function initialize(){}
 function load(){small=WatchUi.loadResource(Rez.Fonts.Icons16);large=WatchUi.loadResource(Rez.Fonts.Icons24);}
 function draw(dc,id,x,y,color){dc.setColor(color,Graphics.COLOR_TRANSPARENT);dc.drawText(x,y,small,glyphs[id],Graphics.TEXT_JUSTIFY_LEFT);}
 function drawBig(dc,id,x,y,color){dc.setColor(color,Graphics.COLOR_TRANSPARENT);dc.drawText(x,y,large,glyphs[id],Graphics.TEXT_JUSTIFY_LEFT);}
}
