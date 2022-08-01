(function() {
    "use strict";

    window.addEventListener("load", function() {
        // how many pages?
        // const pageCount = 3;  // to be changed
        // DOM elements
        // page number
        const page_number = document.querySelector("#page-number");
        // pages
        const pageCount = parseInt(document.querySelector("#pages").innerHTML);
        // next button
        const next = document.getElementById("next");
        // previous button
        const previous = document.getElementById("prev");
        // table content
        var table_str = document.getElementById("hidden-table").innerHTML;
        var table = JSON.parse(table_str);
        // table position
        const query_table = this.document.getElementById('results');
        const items_per_page = 10;
        var number_of_pages = Math.ceil((table.length - 1)/items_per_page);
        var last_page_length = (table.length - 1)% items_per_page;
        var counter = 1;
        query_table.innerHTML = getQueryTable();
    
        next.addEventListener("click", function(evt){
            evt.preventDefault();
            counter++;
            if(counter > pageCount){
                counter = 1;
            };
            page_number.innerHTML = counter;
            query_table.innerHTML = getQueryTable();
        })
    
        previous.addEventListener("click", function(evt){
            evt.preventDefault();
            counter--;
            if(counter < 1){
                counter = pageCount;
            };
            page_number.innerHTML = counter;
            query_table.innerHTML = getQueryTable();
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

