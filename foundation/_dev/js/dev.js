/*---------------------------------------
   Replete Core
   http://replete.nu
ˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍˍ
˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭˭*/

//loadCss
$.loadCss=function(css){$('head').append('<link rel="stylesheet" type="text/css" href="'+css+'">')};

$.urlParam = function (d) { var c = new RegExp("[\\?&]" + d + "=([^&#]*)").exec(window.location.href); if (!c) { return 0 } return c[1] || 0 };

function getFilename() {
    var filename = document.location.href,
        end = (filename.indexOf("?") == -1) ? filename.length : filename.indexOf("?");
    return filename.substring(filename.lastIndexOf("/") + 1, end);
}

function devAlert(message) {
    $("#dev-alert")
        .html(message)
        .show()
        .delay(300)
        .fadeOut("fast");
}

$(function () {

	//TODO: Refactor loads of this!

    //Load Dev-specific CSS
	$.loadCss("/_dev/css/dev.css");

    //Firebug
    if ($.browser.msie || $.urlParam('firebug')) {
    	Modernizr.load("/_dev/js/firebug-lite.js"); //http://getfirebug.com/firebug-lite.js
    }

    //Page-specific reference images
    referenceImageOverlay();

    //Setup Dev UI
    $("body")
        .append($("<div id='dev-alert'/>"))
        .append($("<div id='dev-title'>Dev<br/><div class='help'>?</div></div>"));

    //Hide Alerts initially
    $("#dev-alert").hide();
    $("#dev-title .help").click(function () {
        $(this).load("/_dev/js/dev.html", function () {
            $("#dev-title .help").unbind();
            $(this).click(function () {
                $("#dev-title .help .content").toggle();
            });
        });
    });

});


function referenceImageOverlay() {

    //Settings
    var fileType = ".png", //including extension
        folder = "/_dev/screenshots/", //relative to root
        defaultOpacity = .5,
        ref = "dev-ref-visual",
        refId = "#" + ref;

    //Get filename
    var page = getFilename(); //get everything after '/'
    if (page == "") { page = "home.html"; } //give '/' root page a name
    page = page + fileType; 

    //Load image on top of page
    var obj = $("<div id='"+ ref+ "' style='background:url(" + folder + page + ") top center no-repeat'/>");
    $("body").append(obj);

    //Set defaults
    $(refId).css("opacity", defaultOpacity);

    //Page-specific reference images
    if (!$.urlParam('showVisual')) {
        $(refId).hide();
    }

    //Add some events to control display
    var isCtrl = false;
    $(document.documentElement).keydown(function (e) {

        //http://www.cambiaresearch.com/c4/702b8cd1-e5b0-42e6-83ac-25f0306e3e25/javascript-char-codes-key-codes.aspx

        if (e.keyCode == 48) {
            change("1");
            $(refId).toggle();
            if ($(refId).is(":visible")) { devAlert("Show Overlay"); }
            else { devAlert("Hide Overlay"); }
        }
        if (e.keyCode == 49) { change(".1") }
        if (e.keyCode == 50) { change(".2") }
        if (e.keyCode == 51) { change(".3") }
        if (e.keyCode == 52) { change(".4") }
        if (e.keyCode == 53) { change(".5") }
        if (e.keyCode == 54) { change(".6") }
        if (e.keyCode == 55) { change(".7") }
        if (e.keyCode == 56) { change(".8") }
        if (e.keyCode == 57) { change(".9") }

        if (e.which == 17) isCtrl = true;
        if (e.which == 72 && isCtrl == true) {
        //CTRL+H
            $(refId).toggle();
            if ($(refId).is(":visible")) { devAlert("Show Overlay"); }
            else { devAlert("Hide Overlay"); }
        return false;
        }

        //TODO: Write some code to move pixels left/right and remember the tweaking via cookie

        function change(op) {
            $(refId).css("opacity", op);
        }

    }).keyup(function (e) {
        if (e.which == 17) {isCtrl = false;}
    });

}
