//--
// Initial javascript code from Oliver Tse:
//   http://skypoetsworld.blogspot.com/2007/11/igoogle-and-newsvine-dashboards.html
//--

var Dom = YAHOO.util.Dom

var marker = document.createElement("div");
Dom.addClass(marker, "marker")

function start_drag(x, y) {
    var el = this.getEl();
    var dragEl = this.getDragEl();
    var region = Dom.getRegion(el);

    dragEl.innerHTML = el.innerHTML;

    Dom.setStyle(dragEl, "opacity", 0.5);
    Dom.setStyle(dragEl, "font-size", "12px");
    Dom.setStyle(dragEl, "height", region.height-10+"px");
    Dom.setStyle(dragEl, "width", region.width-10+"px");
    Dom.setStyle(dragEl, "border", "0");

    Dom.setStyle(marker, "height", region.height-14+"px");
    Dom.setStyle(marker, "width", region.width-14+"px");

    el.parentNode.replaceChild(marker, el);
}

function end_drag(e, id) {
    var dragEl = this.getDragEl()
    Dom.batch(Dom.getChildren(dragEl), function (c) { dragEl.removeChild(c) })

    marker.parentNode.replaceChild(this.getEl(), marker);
}

function init_portlet(p) {
    var handler = Dom.getElementsByClassName("portlet_handle", "div", p)[0];

    if(handler) {
        var drag = new YAHOO.util.DDProxy(p);

        drag.setHandleElId(handler);

        drag.startDrag = start_drag;
        drag.onDragEnter = function (e, id) { Dom.insertBefore(marker, id) };
        drag.endDrag = end_drag;
    }
}

function init_portal() {
    Dom.batch(Dom.getElementsByClassName("drop_zone"), function (zone) { new YAHOO.util.DDTarget(zone) });
    Dom.batch(Dom.getElementsByClassName("portlet"), init_portlet);
}

/* -------------------------------------------------------------------------- */

function set_description_display(description, display) {
    Dom.setStyle(Dom.get("description_"+description), "display", display);
}

function init_sourceviewer() {
    var markers = Dom.getElementsByClassName("highlight_block_marker");

    YAHOO.util.Event.on(markers, "mouseover", function (e) {
        var name = this.getAttribute("name");

        Dom.addClass(Dom.getElementsByClassName("block_"+name), "highlighted_line");
        set_description_display(name, "block");
    });

    YAHOO.util.Event.on(markers, "mouseout", function (e) {
        var name = this.getAttribute("name");

        Dom.removeClass(Dom.getElementsByClassName("block_"+name), "highlighted_line");
        set_description_display(name, "none");
    });
}
