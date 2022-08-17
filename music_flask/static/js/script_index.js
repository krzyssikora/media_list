(function() {
    "use strict";

    function getCursorPosition(canvas, event) {
        const rect = canvas.getBoundingClientRect()
        const x = event.clientX - rect.left
        const y = event.clientY - rect.top
        return [x, y]
    }
    
    var canvas = document.getElementById("index_image");
    canvas.addEventListener('mousedown', function(e) {
        var coordinates = getCursorPosition(canvas, e)
        var x = coordinates[0]
        var y = coordinates[1]
        var timeout = document.getElementById('vinyl');
        timeout.style.display = 'inline'
        timeout.style.opacity = 1
        timeout.style.top = (y-(timeout.clientHeight)/2).toString() + 'px'
        timeout.style.left = (x-(timeout.clientWidth)/2).toString() + 'px'
        function everySecond(){
            var newDate = new Date();
            var ms = newDate.getMilliseconds();
            var degreesToRotate = ms / 10;
            timeout.style.transform = 'rotate(' + degreesToRotate + 'deg)';
        };
        setInterval(everySecond, 5);
        function hideElement() {
            timeout.style.display = 'none'
        };
        
        var fadeEffect = setInterval(function () {
            if (!timeout.style.opacity) {
                timeout.style.opacity = 1;
            };
            if (timeout.style.opacity > 0.6) {
                timeout.style.opacity -= 0.1;
            } else if (timeout.style.opacity > 0.3) {
                timeout.style.opacity -= 0.2
            } else {
                clearInterval(fadeEffect);
                timeout.style.display = 'none'
            };
        }, 200);
    });
    
})();

