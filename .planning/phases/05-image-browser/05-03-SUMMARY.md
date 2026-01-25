---
phase: 14-image-browser
plan: 03
completed: 2026-01-19
duration: ~2m
subsystem: participant
tags: [edit-flow, state-validation, participant-ux]

dependency-graph:
  requires: ["14-02"]
  provides: ["edit-flow", "state-validation", "graceful-errors"]
  affects: ["15-ai-synthesis"]

tech-stack:
  patterns:
    - State-conditional UI rendering
    - Polling-based UI updates
    - Graceful error handling

key-files:
  modified:
    - the55/app/routers/participant.py
    - the55/app/templates/participant/waiting.html
    - the55/app/templates/participant/strategy.html
  created:
    - the55/app/templates/participant/session_closed.html

decisions:
  - name: Edit button visibility via JS
    choice: Dynamic show/hide based on polling
    why: Responsive to state changes without page reload

metrics:
  tasks: 3/3
  commits: 3
---

# Phase 14 Plan 03: Edit Flow Summary

Edit flow allowing participants to modify responses until capture closes, with graceful state handling.

## What Was Built

### Task 1: Edit Link on Waiting Page
- Added "Edit Response" button visible during CAPTURING state
- Updated status messages for clarity
- JavaScript polling hides button when state changes to CLOSED
- Dynamic message shows submitted count

### Task 2: Strategy Page Re-entry Handling
- Router passes `has_response` flag to template
- Button text changes to "Edit Response" if already submitted
- Edit notice replaces instructions for returning users

### Task 3: State Validation
- GET /respond validates session state with appropriate redirects:
  - DRAFT: redirects to /join
  - CLOSED/REVEALED with response: redirects to waiting
  - CLOSED/REVEALED without response: shows session_closed.html
- POST /respond shows friendly error if session closed during submission
- Status endpoint returns `can_edit` flag for polling
- New session_closed.html template for graceful error display

## Key Files

**Modified:**
- `/var/www/the55/app/routers/participant.py` - State validation logic, can_edit flag
- `/var/www/the55/app/templates/participant/waiting.html` - Edit button, updated messages
- `/var/www/the55/app/templates/participant/strategy.html` - Re-entry handling

**Created:**
- `/var/www/the55/app/templates/participant/session_closed.html` - Graceful error template

## Deviations from Plan

None - plan executed exactly as written.

## Commits

1. `1c14603` - feat(14-03): add edit button to waiting page
2. `1edcdb3` - feat(14-03): handle re-entry on strategy page
3. `1cdfddb` - feat(14-03): add state validation to participant endpoints

## Verification

- [x] Waiting page shows Edit button when CAPTURING
- [x] Edit button hidden when CLOSED
- [x] Clicking Edit loads respond page with existing data
- [x] Strategy page shows "Edit Response" if already submitted
- [x] Accessing /respond when CLOSED redirects to waiting
- [x] Status endpoint returns can_edit flag
- [x] No errors when state changes during user interaction

## Next Phase Readiness

Phase 14 complete. Ready for Phase 15 (AI Synthesis).

All participant flows implemented:
- Join via team code
- Session/name selection
- Strategy display
- Image browser with response form
- Edit capability during capture
- Graceful state transition handling
