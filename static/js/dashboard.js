/**
 * The 55 - Dashboard Search & Sort
 *
 * Filters team rows based on search input.
 * Sorts team rows by company, team name, or recently used.
 * Uses data-searchable attributes for search text.
 */
(function() {
    'use strict';

    const searchInput = document.getElementById('dashboard-search');
    const sortSelect = document.getElementById('team-sort');
    const teamList = document.getElementById('team-list');
    const visibleCountEl = document.getElementById('visible-count');
    const emptyState = document.getElementById('search-empty-state');

    if (!searchInput) return;

    let debounceTimer;

    // Search functionality
    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            filterItems(e.target.value);
        }, 150);
    });

    function filterItems(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        const items = document.querySelectorAll('.team-row[data-searchable]');
        let visibleCount = 0;

        items.forEach(item => {
            const searchText = item.dataset.searchable.toLowerCase();
            const isVisible = !term || searchText.includes(term);
            item.classList.toggle('hidden', !isVisible);
            if (isVisible) visibleCount++;
        });

        // Update empty state visibility
        if (emptyState) {
            emptyState.classList.toggle('hidden', visibleCount > 0 || !term);
        }

        // Update visible count
        if (visibleCountEl) {
            visibleCountEl.textContent = visibleCount;
        }
    }

    // Sort functionality
    if (sortSelect && teamList) {
        sortSelect.addEventListener('change', function() {
            sortTeams(this.value);
        });
    }

    function sortTeams(sortBy) {
        const rows = Array.from(teamList.querySelectorAll('.team-row'));

        rows.sort((a, b) => {
            let aVal, bVal;

            switch (sortBy) {
                case 'company':
                    aVal = a.dataset.company || '';
                    bVal = b.dataset.company || '';
                    break;
                case 'team':
                    aVal = a.dataset.team || '';
                    bVal = b.dataset.team || '';
                    break;
                case 'recent':
                    // For now, reverse order (assumes server returns by created_at)
                    return 0;
                default:
                    return 0;
            }

            return aVal.localeCompare(bVal);
        });

        // Re-append in sorted order
        rows.forEach(row => teamList.appendChild(row));
    }
})();
