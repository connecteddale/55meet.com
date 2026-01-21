/**
 * The 55 - Meeting Screen Controller
 *
 * Handles unified meeting screen functionality:
 * - Status polling during capture phase
 * - All-submitted detection and status collapse
 * - State change detection and ceremony reveal
 * - Keyboard navigation for synthesis levels (1/2/3)
 */

(function() {
    'use strict';

    const POLL_INTERVAL = 2500; // 2.5 seconds
    let pollTimer = null;
    let previousSubmittedCount = 0;

    // Get meeting screen element
    const meetingScreen = document.querySelector('.meeting-screen');
    if (!meetingScreen) return;

    const sessionId = meetingScreen.dataset.sessionId;
    let currentState = meetingScreen.dataset.state;

    /**
     * Initialize level tab switching for synthesis view
     */
    function initLevelTabs() {
        const levelTabs = document.querySelectorAll('.level-tab');
        const levelContents = document.querySelectorAll('.level-content');

        if (!levelTabs.length || !levelContents.length) return;

        levelTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const level = tab.dataset.level;
                switchToLevel(level, levelTabs, levelContents);
            });
        });
    }

    /**
     * Switch to specific level
     */
    function switchToLevel(level, tabs, contents) {
        // Get tabs and contents if not provided
        tabs = tabs || document.querySelectorAll('.level-tab');
        contents = contents || document.querySelectorAll('.level-content');

        // Update tabs
        tabs.forEach(t => {
            if (t.dataset.level === level) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        // Update content
        contents.forEach(c => {
            if (c.dataset.level === level) {
                c.classList.add('active');
            } else {
                c.classList.remove('active');
            }
        });
    }

    /**
     * Initialize keyboard shortcuts
     */
    function initKeyboardShortcuts() {
        // Only enable shortcuts in revealed state (when synthesis is shown)
        if (currentState !== 'revealed') return;

        document.addEventListener('keydown', (e) => {
            // Ignore if typing in input field
            if (e.target.matches('input, textarea, select')) return;

            // Level shortcuts: 1, 2, 3
            if (e.key === '1') {
                switchToLevel('1');
            } else if (e.key === '2') {
                switchToLevel('2');
            } else if (e.key === '3') {
                switchToLevel('3');
            }
        });
    }

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

            // State transition detection
            if (data.state !== currentState) {
                handleStateTransition(currentState, data.state, data);
                return;
            }

            // Update UI for capture mode
            if (currentState === 'draft' || currentState === 'capturing') {
                updateCaptureUI(data);
                checkAllSubmitted(data);
            }
        } catch (error) {
            console.error('Status poll error:', error);
        }
    }

    /**
     * Handle state transitions (MEET-04, MEET-07)
     */
    function handleStateTransition(fromState, toState, data) {
        console.log(`Meeting state transition: ${fromState} -> ${toState}`);
        stopPolling();

        if (toState === 'revealed') {
            // Trigger ceremony reveal animation before reload
            triggerCeremonyReveal();
        } else {
            // Other transitions - reload immediately
            window.location.reload();
        }
    }

    /**
     * Check if all participants have submitted (MEET-03)
     */
    function checkAllSubmitted(data) {
        if (data.submitted_count === data.total_members && data.total_members > 0) {
            const captureSection = document.getElementById('capture-section');
            if (captureSection && !captureSection.classList.contains('all-submitted')) {
                captureSection.classList.add('all-submitted');
                showAllSubmittedMessage();
            }
        }
    }

    /**
     * Show "All Responses Received" visual indicator
     */
    function showAllSubmittedMessage() {
        const progress = document.querySelector('.meeting-progress');
        if (progress) {
            progress.innerHTML = '<span class="all-submitted-text">All Responses Received</span>';
        }
    }

    /**
     * Trigger ceremony reveal animation (MEET-07)
     */
    function triggerCeremonyReveal() {
        // Add transition class to body
        document.body.classList.add('meeting-transitioning');

        // Collapse capture section if visible
        const captureSection = document.getElementById('capture-section');
        if (captureSection) {
            captureSection.classList.add('collapsing');
        }

        // After collapse animation, reload to show synthesis
        setTimeout(() => {
            window.location.reload();
        }, 800); // Match CSS transition duration
    }

    /**
     * Update capture mode UI with status data
     */
    function updateCaptureUI(data) {
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
                indicator.innerHTML = '&#10003;';  // Checkmark
            } else {
                indicator.classList.remove('submitted');
                indicator.classList.add('waiting');
                indicator.textContent = '...';
            }
        });
    }

    /**
     * Start polling
     */
    function startPolling() {
        if (pollTimer) return;
        pollTimer = setInterval(pollStatus, POLL_INTERVAL);
        console.log('Meeting status polling started');
    }

    /**
     * Stop polling
     */
    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
            console.log('Meeting status polling stopped');
        }
    }

    /**
     * Initialize based on current state
     */
    function init() {
        // Initialize level tabs for revealed state
        if (currentState === 'revealed') {
            initLevelTabs();
            initKeyboardShortcuts();
        }

        // Start polling for draft, capturing, and closed states
        // (to detect state changes and auto-reload)
        if (currentState === 'draft' || currentState === 'capturing' || currentState === 'closed') {
            startPolling();
        }
    }

    // Initialize on page load
    init();

    // Clean up on page unload
    window.addEventListener('beforeunload', stopPolling);
})();
