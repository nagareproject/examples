//--
// Initial javascript code from Oliver Tse:
//   http://skypoetsworld.blogspot.com/2007/11/igoogle-and-newsvine-dashboards.html
//--

var container;
var marker = document.createElement("div");

function startDrag(x, y) {
	var dragEl = this.getDragEl();
	var el = this.getEl();
	container = el.parentNode;

	el.style.display = "none";

	dragEl.style.zIndex = 1;
	dragEl.innerHTML = el.innerHTML;
	dragEl.style.backgroundColor = "#fff";

	marker.style.display = "none";
	marker.style.height = YAHOO.util.Dom.getStyle(dragEl, "height");
	marker.style.width = YAHOO.util.Dom.getStyle(dragEl, "width");
	marker.style.margin = "5px";
	marker.style.marginBottom = "20px";
	marker.style.border = "2px dashed #7e7e7e";
	marker.style.display= "block";

	container.insertBefore(marker, el);
}

function onDragEnter(e, id) {
	var el = document.getElementById(id);

	if (YAHOO.util.Dom.hasClass(el, "portletColumn")) {
		el.appendChild(marker);
	} else {
		container = el.parentNode;
		container.insertBefore(marker, el);
	}
}

function endDrag(e, id) {
	var el = this.getEl();
	
	var dragEl = this.getDragEl();
	while(dragEl.hasChildNodes()) dragEl.removeChild(dragEl.firstChild);
	
	try {
		marker = container.replaceChild(el, marker);
	} catch(err) {
		marker = marker.parentNode.replaceChild(el, marker);
	}
	el.style.display = "block";
}

function initColumn(c) {
	new YAHOO.util.DDTarget(c, "Group1");
}

function initPortlet(p) {
	var drag = new YAHOO.util.DDProxy(p, "Group1");
	drag.setHandleElId(YAHOO.util.Dom.getElementsByClassName("portletHandle", "div", p)[0]);
	
	drag.startDrag = startDrag;
	drag.onDragEnter = onDragEnter;
	//drag.onDragOut = onDragOut;
	drag.endDrag = endDrag;
}

function portalInit(p) {
	YAHOO.util.Dom.batch(YAHOO.util.Dom.getElementsByClassName("portletColumn", "div", p), initColumn);
	YAHOO.util.Dom.batch(YAHOO.util.Dom.getElementsByClassName("portlet", "div", p), initPortlet);
}
