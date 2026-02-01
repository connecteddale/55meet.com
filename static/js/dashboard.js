/**
 * The 55 - Dashboard Tab Navigation & Dynamic Content
 *
 * Manages three tabs: Companies, Teams, Sessions
 * Each tab loads data dynamically from API endpoints
 * Search filters content on the active tab
 */
(function() {
    'use strict';

    // DOM Elements
    const searchInput = document.getElementById('dashboard-search');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Content containers
    const companyList = document.getElementById('company-list');
    const teamList = document.getElementById('team-list');
    const sessionsList = document.getElementById('sessions-list');

    // Early exit if essential elements are missing
    if (!companyList || !teamList || !sessionsList) {
        console.error('Dashboard: Missing required DOM elements');
        return;
    }

    // State
    let currentTab = 'companies';
    let companiesData = null;
    let teamsData = null;
    let sessionsData = null;
    let debounceTimer;

    // ========================================
    // Tab Switching
    // ========================================

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.dataset.tab;
            switchTab(tab);
        });
    });

    function switchTab(tab) {
        currentTab = tab;

        // Update button states
        tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });

        // Update content visibility
        tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `tab-${tab}`);
        });

        // Update search placeholder
        if (searchInput) {
            const placeholders = {
                companies: 'Search companies...',
                teams: 'Search teams...',
                sessions: 'Search sessions...'
            };
            searchInput.placeholder = placeholders[tab] || 'Search...';
        }

        // Load data if not already loaded
        if (tab === 'companies' && !companiesData) {
            loadCompanies();
        } else if (tab === 'teams' && !teamsData) {
            loadTeams();
        } else if (tab === 'sessions' && !sessionsData) {
            loadSessions();
        }

        // Apply current search filter
        if (searchInput && searchInput.value) {
            filterCurrentTab(searchInput.value);
        }
    }

    // ========================================
    // Data Loading
    // ========================================

    async function loadCompanies() {
        try {
            const response = await fetch('/admin/api/companies');
            if (!response.ok) throw new Error('Failed to load companies');
            companiesData = await response.json();
            renderCompanies(companiesData);
        } catch (error) {
            console.error('Error loading companies:', error);
            companyList.innerHTML = '<div class="empty-state">Failed to load companies. Please refresh.</div>';
        }
    }

    async function loadTeams() {
        try {
            const response = await fetch('/admin/api/teams');
            if (!response.ok) throw new Error('Failed to load teams');
            teamsData = await response.json();
            renderTeams(teamsData);
        } catch (error) {
            console.error('Error loading teams:', error);
            teamList.innerHTML = '<div class="empty-state">Failed to load teams. Please refresh.</div>';
        }
    }

    async function loadSessions() {
        try {
            const response = await fetch('/admin/api/sessions');
            if (!response.ok) throw new Error('Failed to load sessions');
            sessionsData = await response.json();
            renderSessions(sessionsData);
        } catch (error) {
            console.error('Error loading sessions:', error);
            sessionsList.innerHTML = '<div class="empty-state">Failed to load sessions. Please refresh.</div>';
        }
    }

    // ========================================
    // Rendering
    // ========================================

    function renderCompanies(companies) {
        if (!companies || companies.length === 0) {
            companyList.innerHTML = '<div class="empty-state">No companies found.</div>';
            return;
        }

        const html = companies.map(company => {
            const companyName = company.name || 'Unknown';
            const searchText = companyName.toLowerCase();
            const teamsList = company.teams || [];

            return `
            <div class="company-item" data-search="${escapeAttr(searchText)}">
                <div class="company-header" onclick="this.parentElement.classList.toggle('expanded')">
                    <span class="company-name">${escapeHtml(companyName)}</span>
                    <span class="company-team-count">${teamsList.length} team${teamsList.length !== 1 ? 's' : ''}</span>
                </div>
                <div class="company-teams">
                    ${teamsList.map(team => `
                        <a href="/admin/sessions/team/${team.id}" class="company-team-link">
                            <div style="font-weight: 500;">${escapeHtml(team.team_name || '')}</div>
                            <div style="font-size: var(--text-xs); color: var(--color-text-secondary);">
                                ${escapeHtml(team.code || '')} &bull; ${team.member_count || 0} members
                            </div>
                        </a>
                    `).join('')}
                </div>
            </div>
        `}).join('');

        companyList.innerHTML = html;
    }

    function renderTeams(teams) {
        if (!teams || teams.length === 0) {
            teamList.innerHTML = '<div class="empty-state">No teams found.</div>';
            return;
        }

        const html = teams.map(team => {
            const companyName = team.company_name || '';
            const teamName = team.team_name || '';
            const code = team.code || '';
            const searchText = `${companyName} ${teamName} ${code}`.toLowerCase();

            return `
            <div class="team-row" data-search="${escapeAttr(searchText)}">
                <a href="/admin/sessions/team/${team.id}" class="team-info">
                    <div class="team-company">${escapeHtml(companyName)}</div>
                    <div class="team-name">${escapeHtml(teamName)}</div>
                    <div class="team-meta">
                        <span class="team-code">${escapeHtml(code)}</span>
                        <span class="team-members">${team.member_count || 0} members</span>
                    </div>
                </a>
                <div class="team-actions">
                    <a href="/admin/sessions/team/${team.id}/create" class="btn btn-primary btn-small">New Session</a>
                    <a href="/admin/teams/${team.id}" class="btn btn-ghost btn-small">Edit</a>
                </div>
            </div>
        `}).join('');

        teamList.innerHTML = html;
    }

    function renderSessions(sessions) {
        if (!sessions || sessions.length === 0) {
            sessionsList.innerHTML = '<div class="empty-state">No sessions found.</div>';
            return;
        }

        const html = sessions.map(session => {
            const companyName = session.company_name || '';
            const teamName = session.team_name || '';
            const month = session.month || '';
            const state = session.state || 'draft';
            const searchText = `${companyName} ${teamName} ${month}`.toLowerCase();

            return `
            <a href="/admin/sessions/${session.id}" class="session-list-item" data-search="${escapeAttr(searchText)}">
                <div class="session-list-info">
                    <div class="session-list-company">${escapeHtml(companyName)}</div>
                    <div class="session-list-team">${escapeHtml(teamName)}</div>
                    <div class="session-list-meta">${escapeHtml(month)}</div>
                </div>
                <span class="session-state state-${escapeAttr(state)}">${escapeHtml(state)}</span>
            </a>
        `}).join('');

        sessionsList.innerHTML = html;
    }

    // ========================================
    // Search & Filter
    // ========================================

    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                filterCurrentTab(e.target.value);
            }, 150);
        });
    }

    function filterCurrentTab(searchTerm) {
        const term = (searchTerm || '').toLowerCase().trim();

        let container;
        let selector;

        switch (currentTab) {
            case 'companies':
                container = companyList;
                selector = '.company-item';
                break;
            case 'teams':
                container = teamList;
                selector = '.team-row';
                break;
            case 'sessions':
                container = sessionsList;
                selector = '.session-list-item';
                break;
        }

        if (!container) return;

        const items = container.querySelectorAll(selector);
        let visibleCount = 0;

        items.forEach(item => {
            const searchText = item.dataset.search || '';
            const isVisible = !term || searchText.includes(term);
            item.style.display = isVisible ? '' : 'none';
            if (isVisible) visibleCount++;
        });

        // Show empty state if no results
        let emptyState = container.querySelector('.search-empty-state');
        if (visibleCount === 0 && term) {
            if (!emptyState) {
                emptyState = document.createElement('div');
                emptyState.className = 'empty-state search-empty-state';
                emptyState.textContent = 'No results match your search.';
                container.appendChild(emptyState);
            }
            emptyState.style.display = 'block';
        } else if (emptyState) {
            emptyState.style.display = 'none';
        }
    }

    // ========================================
    // Utility
    // ========================================

    function escapeHtml(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }

    function escapeAttr(text) {
        if (text == null) return '';
        return String(text).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // ========================================
    // Initialization
    // ========================================

    // Load initial tab (companies)
    loadCompanies();
})();
