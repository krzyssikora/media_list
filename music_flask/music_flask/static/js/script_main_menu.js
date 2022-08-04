(function() {
    "use strict";

    // find name of html file that calls the script
	var path = window.location.pathname;
    var page = path.split("/").pop();
	// make edit tab active and other non-active
	if (page.length > 0) {
        $('.menu-item').each(function(idx, elt) {
            elt.removeAttribute('id');
            if (elt.innerHTML == page) {
                $(elt).attr('id', 'menu-item-active');
            };
        });
    };
    
})();

