(function() {
    "use strict";

    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
        coll[i].classList.toggle("active");
        if (coll[i].style.borderBottom == 'none') {
            coll[i].style.borderBottom = '1px solid #666';
        } else {
            coll[i].style.borderBottom = 'none';
        };
        var content = coll[i].nextElementSibling;
        if (content.style.maxHeight){
            content.style.maxHeight = null;
            content.style.paddingBottom = 0;
            content.style.borderBottom = 'none';
            content.style.width = (coll[i].offsetWidth - 10) + 'px';
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
            content.style.paddingBottom = '10px';
            content.style.borderBottom = '1px solid #666';
            content.style.width = (coll[i].offsetWidth - 10) + 'px';
        };
    };
    
    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        if (this.style.borderBottom == 'none') {
            this.style.borderBottom = '1px solid #666';
        } else {
            this.style.borderBottom = 'none';
        };
        var content = this.nextElementSibling;
        if (content.style.maxHeight){
            content.style.maxHeight = null;
            content.style.paddingBottom = 0;
            content.style.borderBottom = 'none';
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
            content.style.paddingBottom = '10px';
            content.style.borderBottom = '1px solid #666';
            content.style.width = (this.offsetWidth - 10) + 'px';
        };
        });
    };
    
})();

