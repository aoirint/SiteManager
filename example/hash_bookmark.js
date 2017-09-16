
(function() {
	window.onload = function() {
		mf = document.getElementById('main-frame');
		
		function to_path(url) {
			groups = url.match(/docs\/(.+).html$/);
			if (! groups) return null;
			return groups[1];
		}
		
		mf.addEventListener('load', function(e) {
			url = this.contentWindow.location.href;
			path = to_path(url);
			if (path) {
				// location.hash = path;
				history.replaceState(null, '', '#' + path);
			}
		});
		
		if (location.hash) {
			s_path = to_path(mf.src);
			h_path = location.hash.substr(1);
			
			if (s_path != h_path) {
				mf.src = 'docs/' + h_path + '.html';
			}
		}
		else {
			mf.src = 'docs/index.html';
		}
	};
})();
