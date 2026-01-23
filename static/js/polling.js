/**
 * The 55 - Session Status Polling
 *
 * Polls session status API every 2-3 seconds during capturing state.
 * Updates member submission status in real-time.
 */

(function() {
    'use strict';

    const POLL_INTERVAL = 2500; // 2.5 seconds
    let pollTimer = null;

    // Get session ID from data attribute (supports session view and capture views)
    const sessionView = document.querySelector('.session-view, .session-control, .capture-control');
    if (!sessionView) return;

    const sessionId = sessionView.dataset.sessionId;
    if (!sessionId) return;

    /**
     * Fetch session status and update UI
     */
    async function pollStatus() {
        try {
            const response = await fetch(`/admin/sessions/${sessionId}/status`, {
                credentials: 'same-origin'
            });

            if (!response.ok) {
                console.error('Status poll failed:', response.status);
                return;
            }

            const data = await response.json();
            updateUI(data);

            // If state changed from capturing, stop polling and reload
            if (data.state !== 'capturing') {
                stopPolling();
                window.location.reload();
            }
        } catch (error) {
            console.error('Status poll error:', error);
        }
    }

    /**
     * Update UI with new status data
     */
    function updateUI(data) {
        // Update counts
        const submittedEl = document.getElementById('submitted-count');
        const totalEl = document.getElementById('total-members');

        if (submittedEl) submittedEl.textContent = data.submitted_count;
        if (totalEl) totalEl.textContent = data.total_members;

        // Update member status indicators
        const memberList = document.getElementById('member-status-list');
        if (!memberList || !data.members) return;

        data.members.forEach(member => {
            const memberEl = memberList.querySelector(`[data-member-id="${member.id}"]`);
            if (!memberEl) return;

            // Support both old (.status-indicator) and new (.member-status) class names
            const indicator = memberEl.querySelector('.status-indicator, .member-status');
            if (!indicator) return;

            if (member.submitted) {
                indicator.classList.remove('waiting');
                indicator.classList.add('submitted', 'done');
                // Update content for both old and new styles
                if (indicator.classList.contains('member-status')) {
                    indicator.innerHTML = '&#10003;';  // Checkmark
                } else {
                    indicator.textContent = 'Submitted';
                }

                // Add clear button if not already present (only during capturing)
                if (!memberEl.querySelector('.clear-form')) {
                    const clearForm = document.createElement('form');
                    clearForm.method = 'post';
                    clearForm.action = `/admin/sessions/${sessionId}/member/${member.id}/clear`;
                    clearForm.className = 'clear-form';
                    clearForm.onsubmit = function() {
                        return confirm(`Clear ${member.name}'s submission?`);
                    };
                    clearForm.innerHTML = `
                        <button type="submit" class="btn-clear" title="Clear submission">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                        </button>
                    `;
                    memberEl.appendChild(clearForm);
                }
            } else {
                indicator.classList.remove('submitted', 'done');
                indicator.classList.add('waiting');
                if (indicator.classList.contains('member-status')) {
                    indicator.innerHTML = '&hellip;';  // Ellipsis
                } else {
                    indicator.textContent = 'Waiting...';
                }

                // Remove clear button if present (submission was cleared)
                const existingForm = memberEl.querySelector('.clear-form');
                if (existingForm) {
                    existingForm.remove();
                }
            }
        });
    }

    /**
     * Start polling
     */
    function startPolling() {
        if (pollTimer) return;
        pollTimer = setInterval(pollStatus, POLL_INTERVAL);
        console.log('Status polling started');
    }

    /**
     * Stop polling
     */
    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
            console.log('Status polling stopped');
        }
    }

    // Start polling on page load
    startPolling();

    // Clean up on page unload
    window.addEventListener('beforeunload', stopPolling);
})();
