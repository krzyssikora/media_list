(function() {
    "use strict";

    window.addEventListener("load", function() {
        // DOM elements
        // page number
        const page_number = document.querySelector("#page-number");
        const page_number_bottom = document.querySelector("#page-number-bottom");
        // how many pages?
        const pageCount = document.querySelector("#pages");
        // next button
        const next = document.getElementById("next");
        const next_bottom = document.getElementById("next-bottom");
        // previous button
        const previous = document.getElementById("prev");
        const previous_bottom = document.getElementById("prev-bottom");
        // table content
        var table_str = document.getElementById("hidden-table").innerHTML;
        var table = JSON.parse(table_str);
        // table position
        const query_table = this.document.getElementById('results');
        // data properties
        const items_per_page = 10;
        const table_length = table.length - 1
        const number_of_pages = Math.ceil(table_length / items_per_page);
        const last_page_length = table_length % items_per_page;
        var counter = 1;
        query_table.innerHTML = getQueryTable();
        pageCount.innerHTML = number_of_pages;

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

