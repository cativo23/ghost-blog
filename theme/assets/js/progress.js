/**
 * Reading Progress Bar
 * Shows scroll progress through post content
 */

(function() {
    'use strict';

    const postContent = document.getElementById('post-content');
    if (!postContent) return;

    // Create progress bar element
    const progressBar = document.createElement('div');
    progressBar.id = 'reading-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
        z-index: 9999;
        transition: width 0.1s ease;
    `;
    document.body.appendChild(progressBar);

    let ticking = false;

    function updateProgress() {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrollTop = window.scrollY;

        const scrollableHeight = documentHeight - windowHeight;
        const progress = (scrollTop / scrollableHeight) * 100;

        progressBar.style.width = Math.min(Math.max(progress, 0), 100) + '%';

        ticking = false;
    }

    function onScroll() {
        if (!ticking) {
            window.requestAnimationFrame(updateProgress);
            ticking = true;
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    updateProgress();
})();
