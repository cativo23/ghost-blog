/**
 * Code Blocks Enhancement
 * Adds copy button, line numbers, and language labels to code blocks
 */

(function() {
    'use strict';

    const codeBlocks = document.querySelectorAll('pre[class*="language-"]');

    // Helper to create SVG icon
    function createCopyIcon() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '12');
        svg.setAttribute('height', '12');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', '9');
        rect.setAttribute('y', '9');
        rect.setAttribute('width', '13');
        rect.setAttribute('height', '13');
        rect.setAttribute('rx', '2');
        rect.setAttribute('ry', '2');

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1');

        svg.appendChild(rect);
        svg.appendChild(path);
        return svg;
    }

    function createCheckIcon() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '12');
        svg.setAttribute('height', '12');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');

        const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
        polyline.setAttribute('points', '20 6 9 17 4 12');

        svg.appendChild(polyline);
        return svg;
    }

    codeBlocks.forEach((pre) => {
        // Extract language from class (e.g., "language-javascript" -> "javascript")
        const langClass = Array.from(pre.classList).find(cls => cls.startsWith('language-'));
        const lang = langClass ? langClass.replace('language-', '') : 'text';

        // Add language label
        const langLabel = document.createElement('span');
        langLabel.className = 'code-lang-label';
        langLabel.textContent = lang;
        pre.appendChild(langLabel);

        // Add copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'code-copy-btn';
        copyBtn.appendChild(createCopyIcon());

        const copyText = document.createElement('span');
        copyText.textContent = 'Copy';
        copyBtn.appendChild(copyText);

        copyBtn.addEventListener('click', async () => {
            const code = pre.querySelector('code');
            if (!code) return;

            try {
                await navigator.clipboard.writeText(code.textContent);
                copyBtn.classList.add('copied');

                // Clear and rebuild button content
                copyBtn.textContent = '';
                copyBtn.appendChild(createCheckIcon());
                const copiedText = document.createElement('span');
                copiedText.textContent = 'Copied!';
                copyBtn.appendChild(copiedText);

                setTimeout(() => {
                    copyBtn.classList.remove('copied');
                    copyBtn.textContent = '';
                    copyBtn.appendChild(createCopyIcon());
                    const resetText = document.createElement('span');
                    resetText.textContent = 'Copy';
                    copyBtn.appendChild(resetText);
                }, 2000);
            } catch (err) {
                console.error('Failed to copy code:', err);
            }
        });

        pre.appendChild(copyBtn);

        // Add line numbers
        const code = pre.querySelector('code');
        if (!code) return;

        const lines = code.textContent.split('\n');
        if (lines[lines.length - 1] === '') lines.pop();

        const lineNumbersWrapper = document.createElement('div');
        lineNumbersWrapper.className = 'line-numbers-wrapper';

        lines.forEach((_, index) => {
            const lineNumber = document.createElement('span');
            lineNumber.className = 'line-number';
            lineNumber.textContent = index + 1;
            lineNumbersWrapper.appendChild(lineNumber);
        });

        pre.appendChild(lineNumbersWrapper);
        pre.classList.add('has-line-numbers');
    });
})();
