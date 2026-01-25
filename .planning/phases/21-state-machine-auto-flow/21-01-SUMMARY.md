---
phase: 34
plan: 01
subsystem: session-lifecycle
tags: [state-machine, images, ux]
completed: 2026-01-24
duration: 2m
dependency-graph:
  requires: []
  provides: [clean-state-machine, image-limiting]
  affects: [34-02, 34-03]
tech-stack:
  added: []
  patterns: [state-enum-simplification, image-subset-limiting]
key-files:
  created: []
  modified:
    - sites/55meet.com/app/db/models.py
    - sites/55meet.com/app/routers/sessions.py
    - sites/55meet.com/app/routers/participant.py
    - sites/55meet.com/app/services/images.py
decisions:
  - id: "34-01-D1"
    decision: "Remove DRAFT state entirely rather than deprecating"
    rationale: "No value in keeping dead code path; sessions should start immediately"
  - id: "34-01-D2"
    decision: "60-image limit for participant browser"
    rationale: "Reduces cognitive load from 173 images while maintaining variety"
metrics:
  tasks: 2
  commits: 2
  duration: 2m
---

# Phase 34 Plan 01: Remove DRAFT State & Add Image Limit Summary

**One-liner:** Clean 3-state lifecycle (CAPTURING/CLOSED/REVEALED) with 60-image subset for participant browser.

## What Was Done

### Task 1: Remove DRAFT State and Update All References
- Removed `DRAFT = "draft"` from `SessionState` enum
- Changed Session model default from `SessionState.DRAFT` to `SessionState.CAPTURING`
- Updated `create_session()` to set state to CAPTURING immediately
- Removed the `start_capturing()` endpoint entirely (no longer needed)
- Removed DRAFT-specific checks from participant flow (`respond_form` and `view_synthesis`)
- Updated meeting endpoint docstring to remove DRAFT reference
- Migrated existing database sessions from 'draft' to 'capturing'

### Task 2: Add Limit Parameter to Image Shuffling
- Added `limit: int = None` parameter to `get_shuffled_images()`
- Added `limit: int = None` parameter to `get_paginated_images()` (pass-through)
- Updated participant `respond_form()` to pass `limit=60`
- Result: participants see 60 images (down from 173) per session

## Commits

| Hash | Message |
|------|---------|
| 82ca31c | feat(34-01): remove DRAFT state from session lifecycle |
| 5a8bea6 | feat(34-01): add limit parameter to image shuffling |

## Verification Results

- No DRAFT references in app/ directory
- SessionState enum: `['capturing', 'closed', 'revealed']`
- Session creation defaults to CAPTURING
- /start endpoint removed
- Image library returns exactly 60 images with limit=60 (173 total available)
- Database has 0 sessions in 'draft' state

## Deviations from Plan

None - plan executed exactly as written.

## Decisions Made

| ID | Decision | Rationale |
|----|----------|-----------|
| 34-01-D1 | Remove DRAFT state entirely | No value in dead code; sessions start immediately |
| 34-01-D2 | 60-image limit | Reduces cognitive load from 173 while maintaining variety |

## Next Phase Readiness

Ready for 34-02 (auto-close/auto-synthesize). The clean state machine provides a solid foundation for automated transitions.
