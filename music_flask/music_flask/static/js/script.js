(function() {
    "use strict";

    window.addEventListener("load", function() {
        // how many pages?
        const pageCount = 3;  // to be changed
        // DOM elements
        // page info
        const page_info = document.querySelector("#page-info");
        // next button
        const next = document.getElementById("next");
        // previous button
        const previous = document.getElementById("prev");
    
        let counter = 1;
    
        next.addEventListener("click", function(evt){
            evt.preventDefault();
            counter++;
            if(counter > pageCount){
                counter = 1;
            };
            console.log(counter);
            page_info.innerHTML = 'page ' + counter + '/' + pageCount;
        })
    
        previous.addEventListener("click", function(evt){
            evt.preventDefault();
            counter--;
            if(counter < 1){
                counter = pageCount;
            };
            console.log(counter);
            page_info.innerHTML = 'page ' + counter + '/' + pageCount;
        })
    });
})();
