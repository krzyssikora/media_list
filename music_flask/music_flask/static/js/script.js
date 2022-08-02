(function() {
    "use strict";

    window.addEventListener("load", function() {
        // DOM elements
        // pages-control
        var pages_controls = document.getElementById('pages-controls');
        var pages_controls_bottom = document.getElementById('pages-controls-bottom');
        
        // table content
        var table_str = document.getElementById("hidden-table").innerHTML;
        var table = JSON.parse(table_str);
        // table position
        const query_table = this.document.getElementById('results');
        // conditional
        var page_number
        var page_number_bottom
        var pageCount
        // data properties
        const items_per_page = 10;
        const table_length = table.length - 1
        const number_of_pages = Math.ceil(table_length / items_per_page);
        const last_page_length = table_length % items_per_page;
        var counter = 1;
        query_table.innerHTML = getQueryTable();

        if (number_of_pages > 1) {
            // upper div for pages controls
            pages_controls.innerHTML = `<a href="#" id="prev" class="slide">Previous</a> <a id="page-info"><span id="page-number">${counter}</span>/<span id="pages">${number_of_pages}</span> </a> <a href="#" id="next" class="slide">Next</a>`
            // lower div for pages controls
            pages_controls_bottom.innerHTML = `<a href="#" id="prev-bottom" class="slide">Previous</a> <a id="page-info"><span id="page-number-bottom">${counter}</span>/<span id="pages-bottom">${number_of_pages}</span> </a> <a href="#" id="next-bottom" class="slide">Next</a>`
            // next buttons
            const next = document.getElementById("next");
            const next_bottom = document.getElementById("next-bottom");
            // previous buttons
            const previous = document.getElementById("prev");
            const previous_bottom = document.getElementById("prev-bottom");
        
            // page number
            page_number = document.querySelector("#page-number");
            page_number_bottom = document.querySelector("#page-number-bottom");
            // number of pages
            pageCount = document.querySelector("#pages");
            pageCount.innerHTML = number_of_pages;

            next.addEventListener("click", function(evt){
                evt.preventDefault();
                changePage(1);
            })
        
            next_bottom.addEventListener("click", function(evt){
                evt.preventDefault();
                changePage(1);
            })
        
            previous.addEventListener("click", function(evt){
                evt.preventDefault();
                changePage(-1);
            })
    
            previous_bottom.addEventListener("click", function(evt){
                evt.preventDefault();
                changePage(-1);
            })
        };

        function updatePagesControls() {
            pages_controls_text = `<a href="#" id="prev" class="slide">Previous</a> <a id="page-info"><span id="page-number">${counter}</span>/<span id="pages">${number_of_pages}</span>  </a> <a href="#" id="next" class="slide">Next</a>`
            pages_controls.innerHTML = pages_controls_text
        };

        function changePage(change) {
            counter += change;
            if(counter > number_of_pages){
                counter = 1;
            } else if(counter < 1){
                counter = number_of_pages;
            };
            page_number.innerHTML = counter;
            page_number_bottom.innerHTML = counter;
            query_table.innerHTML = getQueryTable();
        };

        // function sendPageNumber() {
        //     var request = new XMLHttpRequest()
        //     var counter_str = JSON.stringify(counter)
        //     request.open('POST', `/get_page_number/${counter_str}`)
        //     request.send();        
        // };
        
        function getQueryTable() {
            if (counter == number_of_pages) {
                var number_of_items = last_page_length;
            } else {
                var number_of_items = 10
            };
            var table_str = '<table>';
            table_str += add_top_row();
            for (let i = 0; i < number_of_items; i++) {
                table_str += add_row(counter * 10 + i - 9);
            };
            table_str += '</table>';
            return table_str;
        };

        function add_top_row() {
            var ret_str = '<tr>';
            for (const elt of table[0]) {
                ret_str += '<th>' + elt + '</th>';
            };
            ret_str += '</tr>'
            return ret_str
        };

        function add_row(row) {
            var ret_str = '<tr>';
            for (const elt of table[row]) {
                ret_str += '<td>' + elt + '</td>';
            };
            ret_str += '</tr>'
            return ret_str
        };
    });
})();

