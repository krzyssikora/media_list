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
        // var replacements = [
        //     ['\'\'', '""'],     // ''   -> ""
        //     [', \'', ', "'],    // , '  -> , "
        //     ['\',', '", '],     // ',   -> ",
        //     ['{\'', '{"'],      // {'   -> {"
        //     ['\'}', '"}'],      // '}   -> "}
        //     ['\':', '":'],      // ':   -> ":
        //     [': \'', ': "'],    // : '  -> : "
        //     ['\[\'', '\["'],    // ['   -> ["
        //     ['\'\]', '"\]']];   // ']   -> "]
        // for (var replacement of replacements) {
        //     elt_string = elt_string.replaceAll(replacement[0], replacement[1]);
        // };
        ret_object = JSON5.parse(elt_string); 
    };
    dom_elt.style.display = 'none';
    return ret_object;
};