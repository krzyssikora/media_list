(function() {
    "use strict";

    const button_submit = document.getElementById('btn-submit');
    button_submit.addEventListener('click', function() {
        document.getElementById('query').innerHTML = '<span style="color:var(--colour-dark-magenta)">Data is downloaded. Please wait...</span>'
    });

})();

