var saved_query_message;
var queries_table_header;
var queries_table;
var query_dicts;


(function() {
    "use strict";

    function sendQueryToPython(the_query) {
		var request = new XMLHttpRequest();
		var query_str = JSON.stringify(the_query);
		request.open('POST', `/use_query/${query_str}`)
		request.send();        
	};

    $.getScript('/static/js/module.js', function(){
        saved_query_message = document.getElementById('hidden-saved-query-message').innerHTML;
        queries_table_header = getHiddenData('hidden-queries-table-header', 'html');
        queries_table = getHiddenData('hidden-queries-table', 'object');
        var clean_queries_table = [];
        for (let line of queries_table) {
            for (let repl of ['\[', '\]', '\'']) {
                line = line.replaceAll(repl, '');
            };
            clean_queries_table.push(line);
        };
        query_dicts = getHiddenData('hidden-query-dicts', 'object');
        document.getElementById('new_query_message').innerHTML = saved_query_message;
        document.getElementById('queries_table').innerHTML = queries_table_header + clean_queries_table.join(' ');
        makeKeywordsBold('queries_table');
        
        // add buttons
        const delete_buttons = [];
        const use_buttons = [];
        for (let i=0; i<queries_table.length; i++) {
            var query_id = i + 1;
            var query_id_str = query_id.toString();
            var queries_row = document.getElementById('query_' + query_id_str);
            
            var use_button = document.createElement('button');
            use_button.id = 'use_' + query_id_str;
            use_button.className = 'query_button';
            use_button.innerHTML = 'use'
            queries_row.appendChild(use_button);
            use_buttons.push(use_button);

            var delete_button = document.createElement('button');
            delete_button.id = 'delete_' + query_id_str;
            delete_button.className = 'query_button';
            delete_button.innerHTML = 'delete'
            queries_row.appendChild(delete_button);
            delete_buttons.push(delete_button);
        };

        // add use button actions
        for (let use_button of use_buttons) {
            use_button.addEventListener('click', function(){
                var query_id = use_buttons.indexOf(use_button);
                var the_query = query_dicts[query_id];
                // window.location.href = '/query'
                // sendQueryToPython(the_query);
                var request = new XMLHttpRequest();
                var query_str = JSON.stringify(the_query);
                request.open('POST', `/use_query/${query_str}`)
                request.send();
                window.location.href = '/query_from_saved'
            })
        };

        // add delete button actions
        for (let delete_button of delete_buttons) {
            delete_button.addEventListener('click', function(){
                var query_id = delete_buttons.indexOf(delete_button);
                var the_query = query_dicts[query_id];
                delete the_query.id;
                document.getElementById('hidden-filter').innerHTML = JSON.stringify(the_query);
                console.log(document.getElementById('hidden-filter').innerHTML)
            })
        };
    });
})();
