/**
 * The 55 - Session Status Polling
 *
 * Polls session status endpoint and updates UI in real-time.
 * Used in both CAPTURING state (member submissions) and CLOSED state (synthesis generation).
 */

(function() {
    'use strict';

    const POLL_INTERVAL = 2500; // 2.5 seconds
    const container = document.querySelector('.session-control') || document.querySelector('.capture-control');

    if (!container) return;

    const sessionId = container.dataset.sessionId;
    if (!sessionId) return;

    let lastState = null;
    let lastSynthesisStatus = null;

    /**
     * Poll session status
     */
    async function pollStatus() {
        try {
            const response = await fetch(`/admin/sessions/${sessionId}/status`);
            if (!response.ok) return;

            const data = await response.json();

            // Check for state change - reload page if changed
            if (lastState !== null && lastState !== data.state) {
                window.location.reload();
                return;
            }
            lastState = data.state;

            // Check for synthesis completion (CLOSED state)
            if (data.state === 'closed') {
                // If synthesis just completed (has_synthesis changed to true), reload
                if (lastSynthesisStatus !== null && !lastSynthesisStatus && data.has_synthesis) {
                    window.location.reload();
                    return;
                }
                lastSynthesisStatus = data.has_synthesis;
            }

            // Update member status (CAPTURING state)
            if (data.members && data.state === 'capturing') {
                updateMemberStatus(data.members);
                updateStats(data.submitted_count, data.total_members);
            }

        } catch (error) {
            console.error('Polling error:', error);
        }
    }

    /**
     * Update member submission status indicators
     */
    function updateMemberStatus(members) {
        const list = document.getElementById('member-status-list');
        if (!list) return;

        // Detect if we're in capture mode (checkmark style) or control mode (text style)
        const isCaptureMode = document.body.classList.contains('capture-mode');

        members.forEach(member => {
            const item = list.querySelector(`[data-member-id="${member.id}"]`);
            if (!item) return;

            const indicator = item.querySelector('.status-indicator');
            if (!indicator) return;

            if (member.submitted) {
                indicator.classList.remove('waiting');
                indicator.classList.add('submitted');
                indicator.textContent = isCaptureMode ? '\u2713' : 'Submitted';
            } else {
                indicator.classList.remove('submitted');
                indicator.classList.add('waiting');
                indicator.textContent = isCaptureMode ? '...' : 'Waiting...';
            }
        });
    }

    /**
     * Update submission count stats
     */
    function updateStats(submitted, total) {
        const submittedEl = document.getElementById('submitted-count');
        const totalEl = document.getElementById('total-members');

        if (submittedEl) submittedEl.textContent = submitted;
        if (totalEl) totalEl.textContent = total;
    }

    // Start polling
    pollStatus();
    setInterval(pollStatus, POLL_INTERVAL);

})();
