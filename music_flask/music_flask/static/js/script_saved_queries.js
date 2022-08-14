var saved_query_message;
var queries_table_header;
var queries_table;
var query_dicts;


(function() {
    "use strict";
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
    });
})();
