---
phase: 21
plan: 01
title: "Combined QR + Status Projectable"
subsystem: facilitator-ui
tags: [qr-code, real-time, projector, capture-view]

dependency_graph:
  requires: [20-02]  # Session flow controls
  provides: [combined-capture-view, projector-optimized-status]
  affects: []

tech_stack:
  added: []
  patterns: [dual-panel-layout, mode-aware-polling]

key_files:
  created:
    - the55/app/templates/admin/sessions/capture.html
  modified:
    - the55/app/routers/sessions.py
    - the55/app/static/css/main.css
    - the55/app/templates/admin/sessions/view.html
    - the55/static/js/polling.js

decisions:
  - id: CAP-1
    title: "Dual-panel layout"
    choice: "Grid layout with QR left, status right"
    rationale: "Natural eye flow, balances visual weight"

  - id: CAP-2
    title: "Mode-aware polling"
    choice: "Detect body class for indicator format"
    rationale: "Single polling.js serves both views with appropriate display"

  - id: CAP-3
    title: "400px QR code"
    choice: "Fixed 400px with white padding"
    rationale: "Scannable from back of room per FAC-10 requirement"

metrics:
  duration: "~3m"
  completed: "2026-01-19"
---

# Phase 21 Plan 01: Combined QR + Status Projectable Summary

Combined QR code display with real-time participant status in single projectable capture view for facilitators.

## What Was Done

### Task 1: Create capture endpoint and template
- Added `/admin/sessions/{id}/capture` endpoint to sessions.py
- Created `capture.html` with dual-panel layout
- Redirects to session view if not in CAPTURING state
- Includes polling.js for real-time updates

### Task 2: Add capture mode CSS styles
- 400px QR code with white background and padding (FAC-10)
- High-contrast green checkmark (#22c55e) for submitted status
- Dimmed waiting indicator (rgba white 0.3)
- Large 4rem progress counter visible from distance
- Dark theme (#1a1a2e) matching presentation mode
- Responsive stacking on screens < 900px

### Task 3: Add capture view link and update polling
- Added "Capture View (Project)" button in CAPTURING state
- Updated polling.js to find `.session-control` OR `.capture-control`
- Mode-aware status updates: checkmark in capture mode, text in control mode

## Decisions Made

| ID | Decision | Choice | Rationale |
|----|----------|--------|-----------|
| CAP-1 | Panel layout | Grid 50/50 split | Natural eye flow, QR draws attention first then status |
| CAP-2 | Polling support | Single file, mode-aware | No code duplication, consistent 2.5s interval |
| CAP-3 | QR size | 400px fixed | FAC-10: scannable from back of room |

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- Capture endpoint returns 200 for CAPTURING state
- Non-CAPTURING state redirects to session view (303)
- QR code displays at 400x400px with white background
- Status indicators show checkmark vs ellipsis correctly
- Polling.js updates both views in real-time

## Success Criteria Met

- [x] FAC-09: QR code and participant status on single screen
- [x] FAC-10: QR code 400px+ and scannable
- [x] FAC-11: Status shows submitted/not-submitted with visual indicators
- [x] Real-time updates without flicker (2.5s polling)

## Files Changed

| File | Change |
|------|--------|
| `the55/app/routers/sessions.py` | Added capture_session endpoint (+37 lines) |
| `the55/app/templates/admin/sessions/capture.html` | New dual-panel template (55 lines) |
| `the55/app/static/css/main.css` | Capture mode styles (+138 lines) |
| `the55/app/templates/admin/sessions/view.html` | Added capture view button (+6 lines) |
| `the55/static/js/polling.js` | Mode-aware container and indicator support (+10 lines) |

## Commits

1. `23417e1` feat(21-01): add capture endpoint and dual-panel template
2. `1534989` style(21-01): add capture mode CSS for projectable view
3. `e088c13` feat(21-01): add capture view link and update polling for dual-mode

## Next Phase Readiness

Phase 21 complete. Ready for Phase 22 (final phase in v2.1 milestone).
