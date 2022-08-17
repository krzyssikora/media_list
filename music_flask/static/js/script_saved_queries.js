var saved_query_message;
var queries_table_header;
var queries_table;
var query_dicts;


(function() {
    "use strict";

    function sendQueryToPython(the_query, action) {
		var request = new XMLHttpRequest();
        var query_str = JSON.stringify(the_query);
        request.open('POST', `/saved_query/${action}/${query_str}`)
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
        if (queries_table.length > 0) {
            document.getElementById('new_query_message').innerHTML = saved_query_message;
            document.getElementById('queries_table').innerHTML = queries_table_header + clean_queries_table.join(' ');
            makeKeywordsBold('queries_table');
            // add query editor
            const query_editor = document.getElementById('query-editor');
            const query_editor_text_field = document.createElement('input');
            query_editor_text_field.id = 'query-editor-text-field'
            query_editor.appendChild(query_editor_text_field);
        } else {
            document.getElementById('new_query_message').innerHTML = 'There are no queries saved.'
        };
        
        // add buttons
        var buttons_ids = [];
        for (let query_dict of query_dicts) {
            buttons_ids.push(query_dict.id)
        };
        const delete_buttons = [];
        const use_buttons = [];
        for (let i=0; i<queries_table.length; i++) {
            var query_id = buttons_ids[i];
            var query_id_str = query_id.toString();
            var queries_row = document.getElementById('query_' + query_id_str);
            
            var use_button = document.createElement('button');
            use_button.id = 'use_' + query_id_str;
            use_button.className = 'query_button';
            use_button.innerHTML = 'use';
            queries_row.appendChild(use_button);
            use_buttons.push(use_button);

            var delete_button = document.createElement('button');
            delete_button.id = 'delete_' + query_id_str;
            delete_button.className = 'query_button';
            delete_button.innerHTML = 'delete';
            queries_row.appendChild(delete_button);
            delete_buttons.push(delete_button);

        };

        // add use button actions
        for (let i=0; i<use_buttons.length; i++) {
            use_buttons[i].addEventListener('click', function(){
                var query_id = buttons_ids[i];
                var the_query = query_dicts[i];
                sendQueryToPython(the_query, 'use');
                window.location.href = '/query_from_saved'
            })
        };

        // add delete button actions
        for (let delete_button of delete_buttons) {
            delete_button.addEventListener('click', function(){
                var query_id = delete_buttons.indexOf(delete_button);
                var the_query = query_dicts[query_id];
                sendQueryToPython(the_query, 'delete');
                window.location.href = '/saved_queries'
            })
        };
    });
})();
