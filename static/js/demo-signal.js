/**
 * Demo Signal Capture JavaScript
 *
 * Handles image browser, selection, and bullet input for demo experience.
 * Stores response in sessionStorage (no database writes for demo).
 */
(function() {
    'use strict';

    // ========================================
    // Constants
    // ========================================

    const DEMO_STATE_KEY = 'the55-demo-response';
    const MAX_PAGES = 1;  // All 60 images on one page

    // Get configuration from DOM
    const imageBrowser = document.querySelector('.image-browser');
    const seed = imageBrowser ? parseInt(imageBrowser.dataset.seed, 10) : 0;
    const perPage = imageBrowser ? parseInt(imageBrowser.dataset.perPage, 10) : 20;

    // ========================================
    // State
    // ========================================

    let currentPage = 1;
    let totalPages = MAX_PAGES;
    let selectedImageId = null;
    let selectedImageUrl = null;
    let selectedImagePage = null;
    let loadedPages = new Map();

    // ========================================
    // DOM Elements
    // ========================================

    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const pageIndicator = document.getElementById('page-indicator');
    const imagePage = document.getElementById('image-page');
    const jumpSection = document.getElementById('jump-to-selection');
    const jumpBtn = document.getElementById('jump-btn');
    const submitBtn = document.getElementById('submit-btn');
    const selectionHint = document.getElementById('selection-hint');
    const bulletSection = document.getElementById('bullet-section');
    const selectedImagePreview = document.getElementById('selected-image-preview');
    const bulletInputs = [
        document.getElementById('bullet-1'),
        document.getElementById('bullet-2'),
        document.getElementById('bullet-3'),
        document.getElementById('bullet-4'),
        document.getElementById('bullet-5')
    ];

    // ========================================
    // State Management (sessionStorage)
    // ========================================

    function saveDemoState(imageId, imageUrl, bullets) {
        try {
            const state = {
                seed: seed,
                imageId: imageId,
                imageUrl: imageUrl,
                bullets: bullets,
                timestamp: Date.now()
            };
            sessionStorage.setItem(DEMO_STATE_KEY, JSON.stringify(state));
        } catch (e) {
            console.warn('Failed to save demo state:', e);
        }
    }

    function loadDemoState() {
        try {
            const saved = sessionStorage.getItem(DEMO_STATE_KEY);
            if (!saved) return null;

            const state = JSON.parse(saved);

            // Only return if same seed (same demo session)
            if (state.seed !== seed) {
                clearDemoState();
                return null;
            }

            return state;
        } catch (e) {
            console.warn('Failed to load demo state:', e);
            return null;
        }
    }

    function clearDemoState() {
        try {
            sessionStorage.removeItem(DEMO_STATE_KEY);
        } catch (e) {
            console.warn('Failed to clear demo state:', e);
        }
    }

    // ========================================
    // Page Loading (AJAX)
    // ========================================

    async function loadPage(pageNum) {
        // Clamp to max pages
        if (pageNum > MAX_PAGES) {
            pageNum = MAX_PAGES;
        }

        // Show loading state
        imagePage.innerHTML = '<div class="image-page-loading"><div class="spinner"></div></div>';
        imagePage.classList.remove('active');

        try {
            const url = `/api/images?page=${pageNum}&per_page=${perPage}&seed=${seed}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to load images');

            const data = await response.json();

            // Limit total pages to MAX_PAGES
            totalPages = Math.min(data.total_pages, MAX_PAGES);

            // Cache the page
            loadedPages.set(pageNum, data.images);

            // Render images
            renderPage(data.images);

            // Update pagination
            updatePagination(pageNum);

        } catch (error) {
            console.error('Error loading images:', error);
            imagePage.innerHTML = '<p class="error" style="text-align: center; color: var(--color-text-secondary); padding: var(--space-8);">Failed to load images. Please refresh the page.</p>';
        }
    }

    function renderPage(images) {
        const html = images.map((img, idx) => {
            const isSelected = img.id === selectedImageId;
            const imageNum = idx + 1 + ((currentPage - 1) * perPage);
            return `
                <div class="image-card ${isSelected ? 'selected' : ''}"
                     data-image-id="${img.id}"
                     data-image-url="${img.url}"
                     role="button"
                     tabindex="0"
                     aria-label="Image option ${imageNum}${isSelected ? ' (selected)' : ''}">
                    <img src="${img.url}"
                         alt="Image option"
                         loading="${idx < 6 ? 'eager' : 'lazy'}">
                </div>
            `;
        }).join('');

        imagePage.innerHTML = html;

        // Trigger reflow then add active class for transition
        void imagePage.offsetWidth;
        imagePage.classList.add('active');

        // Attach event handlers to new cards
        attachCardHandlers();
    }

    function attachCardHandlers() {
        const cards = imagePage.querySelectorAll('.image-card');
        cards.forEach(card => {
            card.addEventListener('click', function() {
                selectImage(this.dataset.imageId, this.dataset.imageUrl);
            });
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selectImage(this.dataset.imageId, this.dataset.imageUrl);
                }
            });
        });
    }

    function updatePagination(pageNum) {
        currentPage = pageNum;
        pageIndicator.textContent = `Page ${pageNum} of ${totalPages}`;
        prevBtn.disabled = pageNum <= 1;
        nextBtn.disabled = pageNum >= totalPages;

        // Show "jump to selection" if selection is on different page
        if (selectedImagePage && selectedImagePage !== pageNum) {
            jumpSection.classList.add('visible');
        } else {
            jumpSection.classList.remove('visible');
        }
    }

    // ========================================
    // Image Selection
    // ========================================

    function selectImage(imageId, imageUrl) {
        selectedImageId = imageId;
        selectedImageUrl = imageUrl;
        selectedImagePage = currentPage;

        // Update visual selection
        const cards = imagePage.querySelectorAll('.image-card');
        cards.forEach(card => {
            const isSelected = card.dataset.imageId === imageId;
            card.classList.toggle('selected', isSelected);
            card.setAttribute('aria-label',
                card.getAttribute('aria-label').replace(' (selected)', '') +
                (isSelected ? ' (selected)' : '')
            );
        });

        // Update the preview with selected image
        selectedImagePreview.innerHTML = `<img src="${imageUrl}" alt="Your selected image">`;

        // Show bullet section and scroll to show the selected image preview
        bulletSection.style.display = 'block';
        setTimeout(() => {
            selectedImagePreview.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);

        // Save state with current bullets
        const bullets = getBullets();
        saveDemoState(imageId, imageUrl, bullets);

        updateSubmitButton();

        // Hide jump button since we're on selection page
        jumpSection.classList.remove('visible');
    }

    function jumpToSelection() {
        if (selectedImagePage && selectedImagePage !== currentPage) {
            loadPage(selectedImagePage);
        }
    }

    // ========================================
    // Bullet Points
    // ========================================

    function getBullets() {
        return bulletInputs.map(input => input.value.trim()).filter(b => b);
    }

    function setBullets(bullets) {
        if (!bullets || !Array.isArray(bullets)) return;

        bullets.forEach((bullet, idx) => {
            if (bulletInputs[idx]) {
                bulletInputs[idx].value = bullet;
            }
        });
    }

    function hasAtLeastTwoWords(text) {
        // Split on whitespace and filter out empty strings
        const words = text.trim().split(/\s+/).filter(word => {
            // A "recognizable word" has at least 2 letters
            return word.length >= 2 && /[a-zA-Z]{2,}/.test(word);
        });
        return words.length >= 2;
    }

    function updateSubmitButton() {
        const hasImage = selectedImageId !== null;
        const bulletText = bulletInputs[0].value.trim();
        const hasValidBullet = hasAtLeastTwoWords(bulletText);
        submitBtn.disabled = !(hasImage && hasValidBullet);

        if (hasImage && hasValidBullet) {
            selectionHint.textContent = 'Ready to see what the team chose';
        } else if (hasImage && bulletText.length > 0) {
            selectionHint.textContent = 'Please enter at least two words';
        } else if (hasImage) {
            selectionHint.textContent = 'Enter at least one bullet point';
        } else {
            selectionHint.textContent = 'Select an image to continue';
        }
    }

    function onBulletInput() {
        updateSubmitButton();

        // Save state on every bullet change
        if (selectedImageId) {
            const bullets = getBullets();
            saveDemoState(selectedImageId, selectedImageUrl, bullets);
        }
    }

    // ========================================
    // Navigation
    // ========================================

    async function navigateToResponses() {
        const bullets = getBullets();

        // Validate at least 1 bullet with 2+ words
        if (bullets.length === 0 || !hasAtLeastTwoWords(bullets[0])) {
            bulletInputs[0].focus();
            return;
        }

        // Save final state
        saveDemoState(selectedImageId, selectedImageUrl, bullets);

        // Show loading state on button
        const submitBtn = document.getElementById('submit-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = 'Analyzing responses... <span class="loading-spinner-small"></span>';
        submitBtn.disabled = true;

        // Pre-generate synthesis before navigating
        try {
            const response = await fetch('/demo/api/synthesize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    seed: seed,
                    bullets: bullets,
                    image_id: selectedImageId || null
                })
            });

            if (response.ok) {
                const synthesis = await response.json();
                // Cache the result for the layers page
                sessionStorage.setItem('the55-demo-synthesis', JSON.stringify(synthesis));
            }
        } catch (e) {
            console.warn('Pre-synthesis failed, will generate on layers page:', e);
        }

        // Navigate with View Transition if supported
        const url = `/demo/layers?seed=${seed}`;

        if (document.startViewTransition) {
            document.startViewTransition(() => {
                window.location.href = url;
            });
        } else {
            window.location.href = url;
        }
    }

    // ========================================
    // Event Handlers
    // ========================================

    prevBtn.addEventListener('click', function() {
        if (currentPage > 1) {
            loadPage(currentPage - 1);
        }
    });

    nextBtn.addEventListener('click', function() {
        if (currentPage < totalPages) {
            loadPage(currentPage + 1);
        }
    });

    jumpBtn.addEventListener('click', jumpToSelection);

    bulletInputs.forEach(input => {
        input.addEventListener('input', onBulletInput);
    });

    submitBtn.addEventListener('click', navigateToResponses);

    // ========================================
    // Initialization
    // ========================================

    function init() {
        // Try to restore saved state
        const savedState = loadDemoState();

        if (savedState) {
            selectedImageId = savedState.imageId;
            selectedImageUrl = savedState.imageUrl;

            // Restore bullets
            if (savedState.bullets && savedState.bullets.length > 0) {
                setBullets(savedState.bullets);

                // Show bullet section
                bulletSection.style.display = 'block';

                // Update preview
                if (selectedImageUrl) {
                    selectedImagePreview.innerHTML = `<img src="${selectedImageUrl}" alt="Your selected image">`;
                }

                updateSubmitButton();
            }

            // We need to find which page has the selected image
            // For now, just load page 1 and let user navigate or use jump
            // The selection will be highlighted when they reach that page
        }

        // Load first page
        loadPage(1);
    }

    // Start
    if (imageBrowser) {
        init();
    }
})();
