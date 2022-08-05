(function() {
    "use strict";

    const medium_buttons_div = document.getElementById('medium-buttons');
	const media = ['CD', 'DVD', 'vinyl', 'ebook', 'book'];
	var active_media = ['CD', 'DVD', 'vinyl'];

	// add buttons
	// make some of them active
	for (var medium of media) {
		var button = document.createElement('button');
		button.innerHTML = medium;
		button.setAttribute('id', `button-${medium}`);
		if (active_media.includes(medium)) {
			button.setAttribute('class', 'medium-button clicked')
		} else {
			button.setAttribute('class', 'medium-button');
		};
		button.setAttribute('type', 'button');
		medium_buttons_div.appendChild(button);
	};

	// make them clickable
	var medium_buttons = document.getElementsByClassName('medium-button');
	for (let medium_button of medium_buttons) {
		medium_button.addEventListener('click', function(evt) {
			evt.preventDefault();
			medium_button.classList.toggle("clicked");
			var button_text = medium_button.innerHTML;
			if (active_media.includes(button_text)) {
				active_media = active_media.filter(elt => elt != button_text);
			} else {
				active_media.push(button_text);
			};
		})
	};

	function sendChosenMedia() {
		console.log('sending choice of media..')
		var request = new XMLHttpRequest()
		var active_media_str = JSON.stringify(active_media)
		request.open('POST', `/get_active_media/${active_media_str}`)
		request.send();        
	};

	document.getElementById('btn-submit').addEventListener('click', function() {
		sendChosenMedia();
	})
})();

