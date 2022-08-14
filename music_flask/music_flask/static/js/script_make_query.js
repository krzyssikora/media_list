var active_media = [];
const query_pattern_start = /\([0-9]+ items found/;
const query_pattern_end = / items found/;

(function() {
    "use strict";

	var all_media = ['CD', 'vinyl', 'DVD', 'ebook', 'book']
	


	// make the buttons for choice of media clickable
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

	// create crosses in input boxes
	$('input.deletable').wrap('<span class="deleteicon"></span>').after($('<span>x</span>').click(function() {
		$(this).prev('input').val('').trigger('change').focus();
	}));

	function sendChosenMedia() {
		var request = new XMLHttpRequest()
		var active_media_str = JSON.stringify(active_media)
		request.open('POST', `/get_active_media/${active_media_str}`)
		request.send();        
	};

	function sendQueryToDatabase() {
		var request = new XMLHttpRequest()
		var query_str = JSON.stringify(user_filter)
		request.open('POST', `/get_query_to_save/${query_str}`)
		request.send();        
	};

	document.getElementById('btn-submit').addEventListener('click', function() {
		sendChosenMedia();
	});

	// change keywords in query displayed to strong
	var query = document.getElementById('query');
	var query_str = query.innerHTML;
	const keywords = ['media:', 'title:', 'artist:', 'publisher:'];
	for (let keyword of keywords) {
		if (query_str.includes(keyword)) {
			query_str = query_str.replace(keyword.slice(0,-1), `<strong>${keyword.slice(0,-1)}</strong>`)
		};
	};
	query.innerHTML = query_str;
	var first_found = query_pattern_start.exec(query_str);
	if (first_found) {
		var second_found = query_pattern_end.exec(query_str);
		var id_1 = first_found.index;
		var id_2 = second_found.index;
		var number_of_items_found = parseInt(query_str.slice(id_1 + 1, id_2));
		if (number_of_items_found > 0) {
			const save_query_button = document.createElement('button');
			save_query_button.innerHTML = 'save query';
			save_query_button.id = 'save_query_button'
			query.appendChild(save_query_button);
			save_query_button.addEventListener('click', function() {
				query.click();
				window.location.href = '/save_query'
				sendQueryToDatabase();
			})
		};
	};

	var artist_field = document.getElementById('artist_name'); 
	var title_field = document.getElementById('album_title'); 
	var publisher_field = document.getElementById('publisher');
	var user_filter;
    $.getScript('/static/js/module.js', function(){
		user_filter = getHiddenData('hidden-filter', 'object');
		if (user_filter == '') {
			artist_field.value = '';
			title_field.value = '';
		} else {
			if (user_filter.artist.length > 0) {
				artist_field.value = user_filter.artist
			};
			if (user_filter.title.length > 0) {
				title_field.value = user_filter.album
			};
			if (user_filter.publisher.length > 0) {
				publisher_field.value = user_filter.publisher
			};
			for (var medium of user_filter.media) {
				document.getElementById(`button-${medium}`).setAttribute('class', 'medium-button clicked');
			};
		};

		var media_clicked = document.getElementsByClassName('clicked');
		for( var i=0; i < media_clicked.length; i++) {
			if (!active_media.includes(media_clicked[i].innerHTML)) {
				active_media.push(media_clicked[i].innerHTML)
			};
		};
    });
	
})();

