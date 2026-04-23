/**
 * Terminal Grep Search
 * Ghost Content API search with terminal aesthetic
 */

(function() {
    'use strict';

    const searchTrigger = document.getElementById('search-btn');
    if (!searchTrigger) return;

    // Create search modal
    const modal = document.createElement('div');
    modal.id = 'search-modal';
    modal.className = 'search-modal';
    modal.style.display = 'none';

    const modalContent = document.createElement('div');
    modalContent.className = 'search-modal-content';

    const searchHeader = document.createElement('div');
    searchHeader.className = 'search-header';

    // Build prompt safely
    const prompt = document.createElement('span');
    prompt.className = 'prompt';

    const promptUser = document.createElement('span');
    promptUser.className = 'prompt-user';
    promptUser.textContent = 'cativo';

    const promptSep1 = document.createElement('span');
    promptSep1.className = 'prompt-separator';
    promptSep1.textContent = '@';

    const promptPath = document.createElement('span');
    promptPath.className = 'prompt-path';
    promptPath.textContent = 'blog';

    const promptSep2 = document.createElement('span');
    promptSep2.className = 'prompt-separator';
    promptSep2.textContent = ':~$';

    prompt.appendChild(promptUser);
    prompt.appendChild(promptSep1);
    prompt.appendChild(promptPath);
    prompt.appendChild(promptSep2);

    const grepCmd = document.createElement('span');
    grepCmd.className = 'mono text-muted';
    grepCmd.textContent = ' grep -r "';

    searchHeader.appendChild(prompt);
    searchHeader.appendChild(grepCmd);

    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'search-input';
    searchInput.placeholder = 'search posts...';

    const closingQuote = document.createElement('span');
    closingQuote.className = 'mono text-muted';
    closingQuote.textContent = '" ./posts/';

    searchHeader.appendChild(searchInput);
    searchHeader.appendChild(closingQuote);

    const searchResults = document.createElement('div');
    searchResults.className = 'search-results';
    searchResults.id = 'search-results';

    modalContent.appendChild(searchHeader);
    modalContent.appendChild(searchResults);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    // Open/close modal
    function openModal() {
        modal.style.display = 'flex';
        searchInput.focus();
        searchInput.value = '';
        searchResults.textContent = '';
    }

    function closeModal() {
        modal.style.display = 'none';
    }

    searchTrigger.addEventListener('click', openModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            openModal();
        }
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            closeModal();
        }
    });

    // Search functionality
    let searchTimeout;

    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const query = searchInput.value.trim();

        if (query.length < 2) {
            searchResults.textContent = '';
            return;
        }

        searchTimeout = setTimeout(() => performSearch(query), 300);
    });

    async function performSearch(query) {
        searchResults.textContent = '';
        const loading = document.createElement('div');
        loading.className = 'search-loading mono text-muted';
        loading.textContent = 'Searching...';
        searchResults.appendChild(loading);

        try {
            const apiUrl = `${window.location.origin}/ghost/api/content/posts/?key=${window.ghostContentApiKey}&limit=10&fields=title,slug,excerpt,published_at&filter=title:~'${encodeURIComponent(query)}',excerpt:~'${encodeURIComponent(query)}'`;

            const response = await fetch(apiUrl);
            const data = await response.json();

            if (!data.posts || data.posts.length === 0) {
                searchResults.textContent = '';
                const noResults = document.createElement('div');
                noResults.className = 'search-no-results mono text-muted';
                noResults.textContent = 'grep: no matches found';
                searchResults.appendChild(noResults);
                return;
            }

            displayResults(data.posts);
        } catch (error) {
            console.error('Search error:', error);
            searchResults.textContent = '';
            const errorDiv = document.createElement('div');
            errorDiv.className = 'search-error mono text-muted';
            errorDiv.textContent = 'grep: search failed';
            searchResults.appendChild(errorDiv);
        }
    }

    function displayResults(posts) {
        searchResults.textContent = '';

        posts.forEach(post => {
            const result = document.createElement('a');
            result.href = `/${post.slug}/`;
            result.className = 'search-result';

            const resultLine = document.createElement('div');
            resultLine.className = 'search-result-line mono';

            const path = document.createElement('span');
            path.className = 'search-result-path';
            path.textContent = `./posts/${post.slug}.md`;

            const separator = document.createElement('span');
            separator.className = 'text-muted';
            separator.textContent = ':';

            const match = document.createElement('span');
            match.className = 'search-result-match';
            match.textContent = ` ${post.title}`;

            resultLine.appendChild(path);
            resultLine.appendChild(separator);
            resultLine.appendChild(match);

            const excerpt = document.createElement('div');
            excerpt.className = 'search-result-excerpt text-muted';
            excerpt.textContent = post.excerpt;

            result.appendChild(resultLine);
            result.appendChild(excerpt);
            searchResults.appendChild(result);
        });
    }
})();
