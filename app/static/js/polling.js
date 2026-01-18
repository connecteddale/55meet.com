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

    // Get session ID from data attribute
    const sessionControl = document.querySelector('.session-control');
    if (!sessionControl) return;

    const sessionId = sessionControl.dataset.sessionId;
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

            const indicator = memberEl.querySelector('.status-indicator');
            if (!indicator) return;

            if (member.submitted) {
                indicator.classList.remove('waiting');
                indicator.classList.add('submitted');
                indicator.textContent = 'Submitted';
            } else {
                indicator.classList.remove('submitted');
                indicator.classList.add('waiting');
                indicator.textContent = 'Waiting...';
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
