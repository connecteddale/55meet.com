/**
 * The 55 - Dashboard Client-Side Search
 *
 * Filters team cards and session cards based on search input.
 * Uses data-searchable attributes for search text.
 * Supports filtering by team name OR date (month/year).
 */
(function() {
    'use strict';

    const searchInput = document.getElementById('dashboard-search');
    if (!searchInput) return;

    let debounceTimer;

    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            filterItems(e.target.value);
        }, 150);
    });

    function filterItems(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        const items = document.querySelectorAll('[data-searchable]');
        let visibleCount = 0;

        items.forEach(item => {
            const searchText = item.dataset.searchable.toLowerCase();
            const isVisible = !term || searchText.includes(term);
            item.classList.toggle('hidden', !isVisible);
            if (isVisible) visibleCount++;
        });

        // Update empty state visibility
        const emptyState = document.getElementById('search-empty-state');
        if (emptyState) {
            emptyState.classList.toggle('hidden', visibleCount > 0 || !term);
        }

        // Update visible count badge
        const countBadge = document.getElementById('teams-count');
        if (countBadge) {
            const totalCount = items.length;
            countBadge.textContent = term ? `${visibleCount} of ${totalCount}` : totalCount;
        }
    }
})();
