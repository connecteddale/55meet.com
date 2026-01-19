/**
 * Presentation Mode - Keyboard Navigation
 * Press 1, 2, or 3 to switch between presentation levels
 */

(function() {
    'use strict';

    /**
     * Show the specified level and update tab states
     * @param {number} level - Level number (1, 2, or 3)
     */
    function showLevel(level) {
        // Hide all level content
        document.querySelectorAll('.level-content').forEach(function(el) {
            el.classList.remove('active');
        });

        // Show selected level
        var target = document.querySelector('.level-content[data-level="' + level + '"]');
        if (target) {
            target.classList.add('active');
        }

        // Update tab active states
        document.querySelectorAll('.level-tab').forEach(function(tab) {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });

        var activeTab = document.querySelector('.level-tab[data-level="' + level + '"]');
        if (activeTab) {
            activeTab.classList.add('active');
            activeTab.setAttribute('aria-selected', 'true');
        }
    }

    /**
     * Handle keyboard events for level switching
     * @param {KeyboardEvent} e - Keyboard event
     */
    function handleKeydown(e) {
        // Only respond to 1, 2, 3 keys when not in an input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        if (e.key === '1' || e.key === '2' || e.key === '3') {
            e.preventDefault();
            showLevel(parseInt(e.key, 10));
        }
    }

    /**
     * Initialize tab click handlers
     */
    function initTabClicks() {
        document.querySelectorAll('.level-tab').forEach(function(tab) {
            tab.addEventListener('click', function() {
                var level = this.getAttribute('data-level');
                showLevel(parseInt(level, 10));
            });
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initTabClicks();
        });
    } else {
        initTabClicks();
    }

    // Keyboard listener
    document.addEventListener('keydown', handleKeydown);
})();
