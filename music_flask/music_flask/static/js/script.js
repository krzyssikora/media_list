(function() {
    "use strict";
    // TODOs:
    // links to other queries (i.e. artists - each artist is a link and publishers)
    // advanced filters
    // cascading filters
    
    function convert(elt) {
        return $("<span />", { html: elt }).text();
    };

    function getHiddenData(data_id, data_type) {
        // data_id (str): id from html
        // data_type (str): either 'int' or 'object'
        var dom_elt = document.getElementById(data_id);
        var elt_string = dom_elt.innerHTML;
        var ret_object;
        if (elt_string.length == 0) {
            ret_object = ''
        } else if (data_type == 'int') {
            ret_object = parseInt(elt_string)
        } else if (data_type == 'object') {
            elt_string = convert(elt_string);
            ret_object = JSON5.parse(elt_string);
        } else if (data_type == 'html') {
            ret_object = convert(elt_string)
        };
        dom_elt.style.display = 'hidden';
        return ret_object;
    };

    window.addEventListener("load", function() {
        // data properties and DOM elements
        var counter = 1;
        // submit query button ???

        const other_artists_checkbox = document.getElementById('other-artists-checkbox');
        const publishers = getHiddenData('hidden-publishers', 'object');
        var publishers_choice = document.getElementById('publisher_list');

        publishers.forEach(function(item){
            var option = document.createElement('option');
            option.value = item;
            publishers_choice.appendChild(option);
        })

        // table position
        var query_table = document.getElementById('results');
        // table content
        var table_header =getHiddenData('hidden-table-header', 'html');
        // var table_content = convert(document.getElementById('hidden-table-content'));
        var table_content = getHiddenData('hidden-table-content', 'object');
        var items_per_page = getHiddenData('hidden-items-per-page', 'int');
        // debug:
        // document.getElementById('empty').innerHTML = '<table>' + table_header + table_content.slice(0,3) + '</table>'

        // query table settings
        const table_length = table_content.length;
        var number_of_pages = Math.ceil(table_length / items_per_page);
        var last_page_length = table_length % items_per_page;
        if (last_page_length == 0) {
            last_page_length = items_per_page
        };
        var counter = 1;
        refreshQueryTable();
        // previous filter ???
        // var user_filter = getHiddenData('hidden-filter', 'object');
        
        // pages-controls
        var pages_controls = document.getElementById('pages-controls');
        var pages_controls_bottom = document.getElementById('pages-controls-bottom');
        // upper div for pages controls
        pages_controls.innerHTML = 
        `<a href="#" id="first" class="slide">\<\<</a>
         <a href="#" id="prev" class="slide">\<</a> 
         <a id="page-info"><span id="page-number">${counter}</span>
         /<span id="pages">${number_of_pages}</span></a> 
         <button class="button-off" type="submit" id="btn-5">5</button>
         <button class="button-off" type="submit" id="btn-10">10</button>
         <button class="button-off" type="submit" id="btn-20">20</button>
         <button class="button-off" type="submit" id="btn-50">50</button>
         <a href="#" id="next" class="slide">\></a>
         <a href="#" id="last" class="slide">\>\></a>` 
        // make 50 dissapear for small screens
        if (window.innerWidth < 420) {
            this.document.getElementById('btn-20').style.display = 'none'
        };
        if (window.innerWidth < 450) {
            this.document.getElementById('btn-50').style.display = 'none'
        };
        
        // get rid of some buttons if window too small
        window.onresize = function() {
            var width = window.innerWidth;
            if (width < 420) {
                document.getElementById('btn-20').style.display = 'none'
                document.getElementById('btn-50').style.display = 'none'
            };
            if (width >= 420 & width < 450) {
                document.getElementById('btn-20').style.display = 'inline'
                document.getElementById('btn-50').style.display = 'none'
            };
            if (width >= 450) {
                document.getElementById('btn-20').style.display = 'inline'
                document.getElementById('btn-50').style.display = 'inline'
            };
            adjustBottomBorder();
        };

        // lower div for pages controls
        pages_controls_bottom.innerHTML = 
        `<a href="#" id="first-bottom" class="slide">\<\<</a>
         <a href="#" id="prev-bottom" class="slide">\<</a> 
         <a id="page-info"><span id="page-number-bottom">${counter}</span>
         /<span id="pages-bottom">${number_of_pages}</span></a> 
         <button class="button-phantom"></button>
         <button class="button-phantom"></button>
         <button class="button-phantom"></button>
         <button class="button-phantom"></button>
         <a href="#" id="next-bottom" class="slide">\></a>
         <a href="#" id="last-bottom" class="slide">\>\></a>`
        // switch on the button for current number of items per page
        document.getElementById(`btn-${items_per_page}`).className = 'button-on';
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

        function changePage() {
            if(counter > number_of_pages){
                counter = 1;
            } else if(counter < 1){
                counter = number_of_pages;
            };
            page_number.innerHTML = counter;
            page_number_bottom.innerHTML = counter;
            refreshQueryTable();
        };

        function sendItemsPerPage() {
            var request = new XMLHttpRequest()
            var items_per_page_str = JSON.stringify(items_per_page)
            request.open('POST', `/get_items_per_page/${items_per_page_str}`)
            request.send();        
        };
        
        function adjustBottomBorder() {
            // adjust width of bottom border
            var width = document.getElementById('menu-bar').clientWidth;
            // var width = document.getElementById('menu-bar').offsetWidth;
            // var width = window.screen.width;
            var coll = document.getElementsByClassName("collapsible");
            var content;
            for (let i = 0; i < coll.length; i++) {
                content = coll[i].nextElementSibling;
            };
            coll[0].style.width = (width - 30) + 'px';
            content.style.width = (width - 40) + 'px';
        };
        

        function getQueryTable() {
            if (counter == number_of_pages) {
                var number_of_items = last_page_length;
            } else {
                var number_of_items = items_per_page
            };
            if (table_length <= 1) {
                return '';
            };
            var table_str = '<table>';
            table_str += table_header;
            table_str += table_content.slice(counter * items_per_page - items_per_page, 
                counter * items_per_page + number_of_items - items_per_page).join(' ');
            table_str += '</table>';
            adjustBottomBorder();
            return table_str;
        };

        function refreshQueryTable() {
            query_table.innerHTML = getQueryTable();
            addTableListeners();
        };


        function addAllListeners() {
            for (let btn of page_numbers) {
                page_number_buttons[btn].addEventListener("click", function(evt){
                    evt.preventDefault();
                    var old_items_per_page = items_per_page;
                    items_per_page = btn;
                    var hidden_items_per_page = document.getElementById('hidden-items-per-page');
                    hidden_items_per_page.innerHTML = items_per_page;
                    sendItemsPerPage();
                    // change all buttons' class to off
                    for (let nbr of page_numbers) {
                        page_number_buttons[nbr].className = 'button-off';
                    };
                    // change chosen button's class to on
                    page_number_buttons[btn].className = 'button-on';
                    // find new pages values
                    var first_item_on_page = (counter - 1) * old_items_per_page + 1;
                    counter = Math.ceil(first_item_on_page / items_per_page);
                    number_of_pages = Math.ceil(table_length / items_per_page);
                    last_page_length = table_length % items_per_page;
                    if (last_page_length == 0) {
                        last_page_length = items_per_page
                    };
                    // updatePagesControls();
                    pages_total.innerHTML = number_of_pages;
                    pages_total_bottom.innerHTML = number_of_pages;
                    changePage();
                    refreshQueryTable();
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

            other_artists_checkbox.addEventListener('click', function(){
                other_artists_checkbox.value = 1 - other_artists_checkbox.value;
                var other_artists = document.getElementsByClassName('other_artist');
                if (other_artists_checkbox.value == 1) {
                    for (var artist of other_artists) {
                        artist.style.display = 'inline';
                    }
                } else {
                    for (var artist of other_artists) {
                        artist.style.display = 'none';
                    }
                };
            })
        };

        function addTableListeners() {
            const query_elements = document.querySelectorAll(`[id^="query_"]`);
            for (let i=0; i<query_elements.length; i++) {
                const dom_element = query_elements[i];
                const query_data = dom_element.id.split("_");
                const db_name = query_data[2].replace("***", "_");
                const query_value = query_data[3].replaceAll("***", " ").replaceAll("@", "'");
                dom_element.addEventListener('click', function(evt) {
                    evt.preventDefault();
                    console.log(`query_value: ${query_value}, db_name: ${db_name}`);
                    if (db_name == 'medium') {
                        console.log(`link no ${i}, medium: ${query_value}, CLICKED!`)
                        var medium_buttons = document.getElementsByClassName('medium-button');
                        for (let medium_button of medium_buttons) {
                            medium_button.classList.remove('clicked');
                            var button_text = medium_button.innerHTML;
                            if (active_media.includes(button_text)) {
                                active_media = active_media.filter(elt => elt != button_text);
                            };
                            if (button_text == query_value) {
                                medium_button.classList.toggle("clicked");
                                active_media.push(button_text);
                            };
                        };
                    } else {
                        const query_text_field = document.getElementById(db_name);
                        query_text_field.value = query_value;
                        console.log(query_text_field)
                    };
                    document.getElementById('btn-submit').click();
                })
            };
        };
    });

    
})();

