(function () {
    'use strict';

    // === Theme Toggle ===
    var STORAGE_KEY = 'cativo-theme';
    var html = document.documentElement;

    function getSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            return 'light';
        }
        return 'dark';
    }

    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }

    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            // localStorage unavailable
        }
    }

    // Apply theme immediately to prevent flash
    var storedTheme = getStoredTheme();
    var initialTheme = storedTheme || getSystemPreference();
    html.setAttribute('data-theme', initialTheme);

    // Listen for system preference changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', function (e) {
            if (!getStoredTheme()) {
                html.setAttribute('data-theme', e.matches ? 'light' : 'dark');
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', function () {
                var current = html.getAttribute('data-theme');
                var next = current === 'dark' ? 'light' : 'dark';
                setTheme(next);
            });
        }

        // === Mobile Menu ===
        var hamburgerBtn = document.getElementById('hamburger-btn');
        var mobileMenu = document.getElementById('mobile-menu');
        var mobileClose = document.getElementById('mobile-close');
        var body = document.body;

        // Create overlay element
        var overlay = document.createElement('div');
        overlay.className = 'mobile-overlay';
        overlay.id = 'mobile-overlay';
        body.appendChild(overlay);

        function openMenu() {
            mobileMenu.classList.add('open');
            overlay.classList.add('open');
            mobileMenu.setAttribute('aria-hidden', 'false');
            hamburgerBtn.setAttribute('aria-expanded', 'true');
            body.style.overflow = 'hidden';
        }

        function closeMenu() {
            mobileMenu.classList.remove('open');
            overlay.classList.remove('open');
            mobileMenu.setAttribute('aria-hidden', 'true');
            hamburgerBtn.setAttribute('aria-expanded', 'false');
            body.style.overflow = '';
        }

        if (hamburgerBtn) {
            hamburgerBtn.addEventListener('click', function () {
                var isOpen = mobileMenu.classList.contains('open');
                if (isOpen) {
                    closeMenu();
                } else {
                    openMenu();
                }
            });
        }

        if (mobileClose) {
            mobileClose.addEventListener('click', closeMenu);
        }

        overlay.addEventListener('click', closeMenu);

        // Close on Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && mobileMenu.classList.contains('open')) {
                closeMenu();
            }
        });

        // === Giscus Theme Sync ===
        function syncGiscusTheme(theme) {
            var giscusFrame = document.querySelector('iframe.giscus-frame');
            if (giscusFrame) {
                var giscusTheme = theme === 'dark' ? 'noborder_dark' : 'noborder_light';
                giscusFrame.contentWindow.postMessage(
                    { giscus: { setConfig: { theme: giscusTheme } } },
                    'https://giscus.app'
                );
            }
        }

        // Observe theme changes to sync Giscus
        var themeObserver = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.attributeName === 'data-theme') {
                    var newTheme = html.getAttribute('data-theme');
                    syncGiscusTheme(newTheme);
                }
            });
        });

        themeObserver.observe(html, { attributes: true, attributeFilter: ['data-theme'] });
    });
})();
