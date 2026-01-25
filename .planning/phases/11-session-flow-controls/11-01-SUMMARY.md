---
phase: 20-session-flow-controls
plan: 01
subsystem: session-management
tags: [fastapi, endpoints, state-machine, facilitator]

dependency_graph:
  requires: [13-session-state-machine]
  provides: [reopen-capture-endpoint, clear-submission-endpoint]
  affects: [20-02-admin-ui]

tech_stack:
  added: []
  patterns: [state-reversal, submission-deletion]

key_files:
  created: []
  modified:
    - /var/www/the55/app/routers/sessions.py

decisions: []

metrics:
  duration: 2m
  completed: 2026-01-19
---

# Phase 20 Plan 01: Session Flow Backend Summary

Backend endpoints for facilitator session control - reopen capture and clear individual submissions.

## What Was Built

### reopen_capture Endpoint
- `POST /admin/sessions/{id}/reopen`
- Transitions CLOSED -> CAPTURING state
- Clears all synthesis data (themes, statements, gap_type)
- Resets closed_at timestamp
- Returns 400 if session not in CLOSED state

### clear_member_submission Endpoint
- `POST /admin/sessions/{id}/member/{mid}/clear`
- Deletes specific member's response
- Only works during CAPTURING state
- Returns 404 if no submission found
- Hard delete (no audit trail needed)

## Commit History

| Task | Commit | Description |
|------|--------|-------------|
| 1 | 5bc4cb5 | feat(20-01): add reopen_capture endpoint |
| 2 | acff5d4 | feat(20-01): add clear_member_submission endpoint |

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

1. Module imports successfully
2. Both endpoints have correct decorators at lines 226 and 251

## Next Phase Readiness

Phase 20 Plan 02 can proceed:
- Backend endpoints ready for admin UI integration
- reopen_capture enables "Reopen for Latecomers" button
- clear_member_submission enables per-participant clear action
