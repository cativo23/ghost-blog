/**
 * Table of Contents Generator
 * Extracts h2/h3 headings, builds TOC nav, tracks scroll position
 */

(function() {
    'use strict';

    const tocNav = document.getElementById('toc-nav');
    const tocWrapper = document.getElementById('toc-wrapper');
    const tocToggle = document.getElementById('toc-toggle');
    const postContent = document.getElementById('post-content');

    if (!tocNav || !postContent) return;

    // Extract headings (h2, h3) from post content
    const headings = Array.from(postContent.querySelectorAll('h2, h3'));

    if (headings.length === 0) {
        if (tocWrapper) tocWrapper.style.display = 'none';
        return;
    }

    // Generate TOC links
    headings.forEach((heading, index) => {
        // Create ID if missing
        if (!heading.id) {
            heading.id = `heading-${index}`;
        }

        const link = document.createElement('a');
        link.href = `#${heading.id}`;
        link.textContent = heading.textContent;
        link.className = heading.tagName === 'H3' ? 'toc-link toc-link--sub' : 'toc-link';

        link.addEventListener('click', (e) => {
            e.preventDefault();
            heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
            history.pushState(null, '', `#${heading.id}`);
        });

        tocNav.appendChild(link);
    });

    // Scroll tracking - highlight active section
    let ticking = false;

    function updateActiveLink() {
        const scrollPos = window.scrollY + 100; // offset for header
        let activeHeading = null;

        for (let i = headings.length - 1; i >= 0; i--) {
            if (headings[i].offsetTop <= scrollPos) {
                activeHeading = headings[i];
                break;
            }
        }

        const links = tocNav.querySelectorAll('.toc-link');
        links.forEach(link => link.classList.remove('active'));

        if (activeHeading) {
            const activeLink = tocNav.querySelector(`a[href="#${activeHeading.id}"]`);
            if (activeLink) activeLink.classList.add('active');
        }

        ticking = false;
    }

    function onScroll() {
        if (!ticking) {
            window.requestAnimationFrame(updateActiveLink);
            ticking = true;
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    updateActiveLink(); // Initial highlight

    // Mobile collapse toggle
    if (tocToggle) {
        tocToggle.addEventListener('click', () => {
            tocNav.classList.toggle('toc-collapsed');
            const icon = tocToggle.querySelector('svg');
            if (icon) {
                icon.style.transform = tocNav.classList.contains('toc-collapsed')
                    ? 'rotate(-90deg)'
                    : 'rotate(0deg)';
            }
        });
    }

    // Highlight on page load if hash present
    if (window.location.hash) {
        const targetId = window.location.hash.substring(1);
        const targetLink = tocNav.querySelector(`a[href="#${targetId}"]`);
        if (targetLink) {
            setTimeout(() => targetLink.classList.add('active'), 100);
        }
    }
})();
