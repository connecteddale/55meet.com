---
phase: 20-session-flow-controls
plan: 02
subsystem: admin-ui
tags: [templates, facilitator, session-controls, jinja2]

dependency_graph:
  requires: [20-01-session-flow-backend]
  provides: [reopen-capture-ui, clear-submission-ui]
  affects: []

tech_stack:
  added: []
  patterns: [confirm-dialog, conditional-button-rendering]

key_files:
  created: []
  modified:
    - /var/www/the55/app/templates/admin/sessions/view.html

decisions: []

metrics:
  duration: 2m
  completed: 2026-01-19
---

# Phase 20 Plan 02: Facilitator UI Controls Summary

Admin UI controls for reopening capture and clearing individual submissions - visual interface for backend endpoints from Plan 01.

## What Was Built

### Reopen Capture Button
- Appears in CLOSED state section below synthesis controls
- Secondary styling to distinguish from primary actions
- Confirm dialog warns: "This will clear any existing synthesis and allow new submissions"
- Posts to `/admin/sessions/{id}/reopen` endpoint

### Clear Button per Member
- Appears only during CAPTURING state for submitted members
- Inline form with `margin-left: auto` to push right in flex row
- Confirm dialog includes member name: "Clear {name}'s submission? They will need to resubmit."
- Posts to `/admin/sessions/{id}/member/{mid}/clear` endpoint
- Uses existing `.btn-danger` class for red destructive styling

### CSS (Pre-existing)
- `.btn-danger` class already existed in main.css (lines 381-388)
- No CSS changes required

## Commit History

| Task | Commit | Description |
|------|--------|-------------|
| 1 | c73e4c3 | feat(20-02): add Reopen Capture button for CLOSED state |
| 2 | bd4d3f7 | feat(20-02): add Clear button for member submissions |

## Deviations from Plan

**Task 3 - btn-danger CSS class:** Already existed in codebase. No changes required - the `.btn-danger` class was previously implemented (likely during team management UI development).

## Verification Results

1. Template syntax valid - Jinja2 compilation successful
2. Reopen form found at line 77
3. Clear form found at line 112
4. btn-danger CSS exists (2 occurrences: base + hover)

## Next Phase Readiness

Phase 20 complete. Session flow controls fully implemented:
- Backend: reopen_capture and clear_member_submission endpoints (Plan 01)
- Frontend: Reopen Capture and Clear buttons with confirm dialogs (Plan 02)
- Existing polling.js handles UI updates automatically
