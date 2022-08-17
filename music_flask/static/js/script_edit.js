(function() {
    "use strict";

    const tabs = document.querySelectorAll("#tabs > ul > li > a");

	resizeTabs();

	/*for ( let eachTab of tabs){ eachTab.addEventListener("click", selectTab);}*/

	tabs.forEach(tab => {
		tab.addEventListener("click", selectTab);
	});

	function selectTab(event){
		event.preventDefault();

		tabs.forEach(tab => {
			tab.removeAttribute("class");
		});

		event.target.className = "edit-active";

		const thisTab = event.target.getAttribute("href");
		const thisContent = document.querySelector(thisTab);

		const oldContent = document.querySelector(".visible");
		oldContent.className = "visuallyhidden";
		oldContent.addEventListener("transitionend", function(){
			oldContent.className = "hidden";
			thisContent.className = "visible visuallyhidden";
			setTimeout(function(){
				thisContent.classList.remove("visuallyhidden")
			}, 20);
		}, {capture:false, once:true, passive:false});
	};
	
	function resizeTabs() {
		var width = window.innerWidth;
		if (width > 1100) {
			tabs.forEach(function(elt){
				elt.style.height = '30px'
			})
		} else if (width > 600) {
			tabs.forEach(function(elt){
				elt.style.height = '60px'
			})
		} else if (width > 500) {
			tabs.forEach(function(elt){
				elt.style.height = '90px'
			})
		} else {
			tabs.forEach(function(elt){
				elt.style.height = '120px'
			})
		};
	}

	window.onresize = function() {
		resizeTabs();
	};

})();

