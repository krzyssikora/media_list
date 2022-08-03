(function() {
    "use strict";


    // TODO highlight the number of items per page
    
    window.addEventListener("load", function() {
        // data properties
        var items_per_page = 10;
        var counter = 1;
        // DOM elements
        // submit query button
        const button_submit = document.getElementById('btn-submit');
        // table position
        var query_table = this.document.getElementById('results');
        // table content
        var table_str = document.getElementById("hidden-table").innerHTML;
        var table = JSON.parse(table_str);
        const table_length = table.length - 1
        var number_of_pages = Math.ceil(table_length / items_per_page);
        var last_page_length = table_length % items_per_page;
        var counter = 1;
        query_table.innerHTML = getQueryTable();
        
        // pages-controls
        var pages_controls = document.getElementById('pages-controls');
        var pages_controls_bottom = document.getElementById('pages-controls-bottom');
        // upper div for pages controls
        pages_controls.innerHTML = 
        `<a href="#" id="first" class="slide">\<\<</a>
         <a href="#" id="prev" class="slide">\<</a> 
         <a id="page-info"><span id="page-number">${counter}</span>
         /<span id="pages">${number_of_pages}</span></a> 
         <button type="submit" id="btn-5">5</button>
         <button type="submit" id="btn-10">10</button>
         <button type="submit" id="btn-20">20</button>
         <button type="submit" id="btn-50">50</button>
         <a href="#" id="next" class="slide">\></a>
         <a href="#" id="last" class="slide">\>\></a>`
        // lower div for pages controls
        pages_controls_bottom.innerHTML = 
        `<a href="#" id="first-bottom" class="slide">\<\<</a>
         <a href="#" id="prev-bottom" class="slide">\<</a> 
         <a id="page-info"><span id="page-number-bottom">${counter}</span>
         /<span id="pages-bottom">${number_of_pages}</span></a> 
         <a href="#" id="next-bottom" class="slide">\></a>
         <a href="#" id="last-bottom" class="slide">\>\></a>`
        // forward buttons
        const next = document.getElementById("next");
        const next_bottom = document.getElementById("next-bottom");
        const last = document.getElementById('last');
        const last_bottom = document.getElementById('last-bottom');
        // backward buttons
        const first = document.getElementById('first');
        const first_bottom = document.getElementById('first-bottom');
        const previous = document.getElementById("prev");
        const previous_bottom = document.getElementById("prev-bottom");
        // page number
        var page_number = document.querySelector("#page-number");
        var page_number_bottom = document.querySelector("#page-number-bottom");
        // number of pages buttons
        const page_numbers = [5, 10, 20, 50];
        const page_number_buttons = {};
        for (let num of page_numbers) {
            page_number_buttons[num] = document.getElementById(`btn-${num}`);
        };
        // number of pages
        var pages_total = document.querySelector("#pages");
        var pages_total_bottom = document.querySelector("#pages-bottom");
        pages_total.innerHTML = number_of_pages;
        pages_total_bottom.innerHTML = number_of_pages;

        addAllListeners();

        // function updatePagesControls() {
        //     if (number_of_pages == 1) {
        //         // hide pages controls
        //         pages_controls.style.display = 'none';
        //         pages_controls_bottom.style.display = 'none';
        //     } else {
        //         // show pages controls
        //         pages_controls.style.display = 'grid';
        //         pages_controls_bottom.style.display = 'grid';
        //     };
        // };

        function changePage() {
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
                var number_of_items = items_per_page
            };
            var table_str = '<table>';
            table_str += add_top_row();
            for (let i = 0; i < number_of_items; i++) {
                table_str += add_row(counter * items_per_page + i + 1 - items_per_page);
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
        function addAllListeners() {
            for (let btn of page_numbers) {
                page_number_buttons[btn].addEventListener("click", function(evt){
                    evt.preventDefault();
                    items_per_page = btn;
                    number_of_pages = Math.ceil(table_length / items_per_page);
                    last_page_length = table_length % items_per_page;
                    // updatePagesControls();
                    pages_total.innerHTML = number_of_pages;
                    pages_total_bottom.innerHTML = number_of_pages;
                    changePage();
                    query_table.innerHTML = getQueryTable();
                })
            };
    
            next.addEventListener("click", function(evt){
                evt.preventDefault();
                counter ++;
                changePage();
            });
        
            next_bottom.addEventListener("click", function(evt){
                evt.preventDefault();
                counter ++;
                changePage();
            });
    
            last.addEventListener("click", function(evt){
                evt.preventDefault();
                counter = number_of_pages;
                changePage();
            });
    
            last_bottom.addEventListener("click", function(evt){
                evt.preventDefault();
                counter = number_of_pages;
                changePage();
            });
        
            previous.addEventListener("click", function(evt){
                evt.preventDefault();
                counter --;
                changePage();
            });
    
            previous_bottom.addEventListener("click", function(evt){
                evt.preventDefault();
                counter --;
                changePage();
            });
    
            first.addEventListener("click", function(evt){
                evt.preventDefault();
                counter = 1;
                changePage();
            });
    
            first_bottom.addEventListener("click", function(evt){
                evt.preventDefault();
                counter = 1;
                changePage();
            });
        };
    });

    
})();

