/**
 * Search — Nightwire edition
 * Uses the static modal from search-modal.hbs.
 */
(function () {
    'use strict';

    var searchBtn = document.getElementById('search-btn');
    if (!searchBtn) return;

    var overlay = document.getElementById('search-overlay');
    var searchInput = document.getElementById('search-input');
    var searchResults = document.getElementById('search-results');
    var searchClose = document.getElementById('search-close');
    var searchStats = document.getElementById('search-stats');

    if (!overlay || !searchInput || !searchResults) return;

    function openModal() {
        overlay.setAttribute('aria-hidden', 'false');
        searchInput.focus();
        searchInput.value = '';
        searchResults.textContent = '';
        if (searchStats) searchStats.textContent = '';
    }

    function closeModal() {
        overlay.setAttribute('aria-hidden', 'true');
    }

    searchBtn.addEventListener('click', openModal);
    if (searchClose) searchClose.addEventListener('click', closeModal);

    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) closeModal();
    });

    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            openModal();
        }
        if (e.key === 'Escape' && overlay.getAttribute('aria-hidden') === 'false') {
            closeModal();
        }
    });

    var searchTimeout;

    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        var query = searchInput.value.trim();
        if (query.length < 2) {
            searchResults.textContent = '';
            if (searchStats) searchStats.textContent = '';
            return;
        }
        searchTimeout = setTimeout(function () { performSearch(query); }, 300);
    });

    function performSearch(query) {
        searchResults.textContent = '';
        var loading = document.createElement('div');
        loading.className = 'search-loading';
        loading.textContent = 'Searching...';
        searchResults.appendChild(loading);

        var filter = "title:~'" + query + "'";
        var apiUrl = window.location.origin + '/ghost/api/content/posts/?key=' +
            (window.ghostContentApiKey || '') +
            '&limit=10&fields=title,slug,excerpt,published_at&filter=' +
            encodeURIComponent(filter);

        fetch(apiUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                searchResults.textContent = '';
                if (!data.posts || data.posts.length === 0) {
                    var none = document.createElement('div');
                    none.className = 'search-no-results';
                    none.textContent = 'No matches found';
                    searchResults.appendChild(none);
                    if (searchStats) searchStats.textContent = '';
                    return;
                }
                displayResults(data.posts, query);
                if (searchStats) {
                    searchStats.textContent = data.posts.length + ' result' + (data.posts.length !== 1 ? 's' : '');
                }
            })
            .catch(function (err) {
                console.error('Search error:', err);
                searchResults.textContent = '';
                var errDiv = document.createElement('div');
                errDiv.className = 'search-error';
                errDiv.textContent = 'Search failed — check API key';
                searchResults.appendChild(errDiv);
            });
    }

    function displayResults(posts, query) {
        posts.forEach(function (post) {
            var result = document.createElement('a');
            result.href = '/' + post.slug + '/';
            result.className = 'search-result';

            var line = document.createElement('div');
            line.className = 'search-result-line';

            var path = document.createElement('span');
            path.className = 'search-result-path stamp';
            path.textContent = post.slug;

            var sep = document.createElement('span');
            sep.className = 'text-muted';
            sep.textContent = '  ·  ';

            var title = document.createElement('span');
            title.className = 'search-result-match';
            title.textContent = post.title;

            line.appendChild(path);
            line.appendChild(sep);
            line.appendChild(title);

            var excerpt = document.createElement('div');
            excerpt.className = 'search-result-excerpt text-muted';
            excerpt.textContent = post.excerpt || '';

            result.appendChild(line);
            result.appendChild(excerpt);
            searchResults.appendChild(result);
        });
    }
})();
