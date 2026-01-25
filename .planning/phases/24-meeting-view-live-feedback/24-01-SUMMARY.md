# Phase 37 Plan 01: Live Progress & View Transition Summary

## One-liner
Live member name chips on waiting screen with View Transitions API redirect to synthesis.

## Changes Made

### Task 1: Add submitted member names to participant status endpoint
- Built `submitted_members` array from existing responses query (names only, no IDs)
- Added to JSONResponse after `submitted_count`
- Privacy maintained: only `{"name": "..."}` objects exposed

### Task 2: Live names display and View Transition redirect
- Added submitted-names container with flex-wrap chip layout below status badge
- JavaScript populates name chips from `data.submitted_members` on each poll
- Redirect to synthesis wrapped in `document.startViewTransition()` with fallback
- Capturing state message updated to show `(N/M)` count

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Hash | Message |
|------|---------|
| 717f0e5 | feat(37-01): add live member names to waiting screen |

## Files Modified

- `sites/55meet.com/app/routers/participant.py` - added submitted_members to status endpoint
- `sites/55meet.com/templates/participant/waiting.html` - names chips, View Transition redirect, count message

## Duration
~1 minute

## Completed
2026-01-24
