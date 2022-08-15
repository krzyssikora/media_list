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
    } else {
        ret_object = elt_string;
    };
    if (Object.keys(ret_object).includes('medium')) {
        if (typeof(ret_object.medium) == 'string') {
            ret_object.medium = JSON5.parse(ret_object.medium)
        }
    };
    dom_elt.style.display = 'none';
    return ret_object;
};

// change keywords in query displayed to strong
function makeKeywordsBold(elt_id) {
    var query = document.getElementById(elt_id);
    var query_str = query.innerHTML;
    const keywords = ['medium:', 'title:', 'artist:', 'publisher:'];
    for (let keyword of keywords) {
        if (query_str.includes(keyword)) {
            query_str = query_str.replaceAll(keyword.slice(0,-1), `<strong>${keyword.slice(0,-1)}</strong>`)
        };
    };
    query.innerHTML = query_str;
};
