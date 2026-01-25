# Phase 34 Plan 02: Auto-Synthesize and Auto-Reveal Pipeline Summary

---
phase: 34
plan: 02
subsystem: session-lifecycle
tags: [state-machine, background-tasks, synthesis, automation]
depends_on:
  requires: [34-01]
  provides: [automated-close-synthesize-reveal-pipeline, synthesis-progress-polling]
  affects: [37-participant-ui]
tech-stack:
  added: []
  patterns: [background-task-chaining, state-auto-transition, progress-polling]
key-files:
  created: []
  modified:
    - sites/55meet.com/app/routers/sessions.py
    - sites/55meet.com/app/services/synthesis.py
    - sites/55meet.com/app/routers/participant.py
decisions:
  - Auto-reveal only on success; failures keep CLOSED state for manual retry
  - Manual /synthesize and /reveal endpoints preserved as fallback
  - synthesis_progress is null for non-CLOSED states (clean API contract)
metrics:
  duration: 2m
  completed: 2026-01-24
---

**One-liner:** Automated close-to-reveal pipeline via BackgroundTasks with participant-visible synthesis progress polling

## What Was Done

### Task 1: Auto-synthesize on close and auto-reveal on complete
- Modified `close_capture()` to accept `BackgroundTasks` and auto-trigger `run_synthesis_task`
- Sets "GENERATING..." marker before queuing background task (prevents double-trigger)
- Modified `_generate_and_store_synthesis()` to auto-transition CLOSED -> REVEALED on success
- Sets `revealed_at` timestamp when auto-revealing
- Error path intentionally does NOT auto-reveal (facilitator uses retry endpoint)

### Task 2: Enhanced participant status with synthesis progress
- Added `synthesis_progress` object to participant status JSON endpoint
- Four statuses: `pending`, `generating`, `failed`, `complete` with user-facing messages
- Returns `null` for non-CLOSED states (CAPTURING, REVEALED)
- Enables future frontend polling UI without page changes now

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 6793efb | feat | Auto-synthesize on close and auto-reveal on complete |
| 5658b12 | feat | Add synthesis_progress to participant status endpoint |

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- [x] Close endpoint triggers synthesis automatically (BackgroundTasks in signature)
- [x] Synthesis service sets REVEALED state on success
- [x] Synthesis service does NOT set REVEALED on failure
- [x] Participant status includes synthesis_progress
- [x] Manual /synthesize and /reveal endpoints still work as fallbacks
- [x] Application imports cleanly (all modules verified)

## Architecture Notes

The automated pipeline now works as:
1. Facilitator clicks "Close Capture"
2. `close_capture()` sets state=CLOSED, marks "GENERATING...", queues background synthesis
3. Background task calls Claude API, stores results
4. On success: auto-sets state=REVEALED with timestamp
5. On failure: stays CLOSED with error message, facilitator can retry
6. Participants poll status endpoint and see progress updates

Manual endpoints remain for error recovery:
- POST `/{session_id}/synthesize` - manual trigger
- POST `/{session_id}/synthesize/retry` - force regeneration
- POST `/{session_id}/reveal` - manual reveal

## Next Phase Readiness

No blockers. Phase 34-03 can proceed to test the full pipeline integration.
