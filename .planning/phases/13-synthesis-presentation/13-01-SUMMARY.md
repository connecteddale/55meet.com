---
phase: 22
plan: 01
title: "Level-Specific Export and Retry Endpoints"
subsystem: synthesis-api
tags: [export, synthesis, retry, api-endpoints]

dependency_graph:
  requires: [21-01]  # Combined QR + Status
  provides: [level-specific-exports, synthesis-retry, synthesis-status-polling]
  affects: []

tech_stack:
  added: []
  patterns: [level-specific-data-slices, forced-regeneration]

key_files:
  created: []
  modified:
    - the55/app/routers/sessions.py

decisions:
  - id: PRES-05
    title: "Level-specific export endpoints"
    choice: "Three separate GET endpoints for each level"
    rationale: "Clean API, download-ready JSON for presentation integration"

  - id: SYNTH-04
    title: "Explicit retry endpoint"
    choice: "POST with data clearing before regeneration"
    rationale: "Differs from trigger which skips valid synthesis"

metrics:
  duration: "~2m"
  completed: "2026-01-19"
---

# Phase 22 Plan 01: Level-Specific Export and Retry Endpoints Summary

Four new API endpoints enabling level-specific JSON export for presentations and explicit retry mechanism for failed synthesis.

## What Was Done

### Task 1: Add level-specific export endpoints
- Added `GET /{session_id}/export/level1` returning themes and gap_type only
- Added `GET /{session_id}/export/level2` returning attributed statements array
- Added `GET /{session_id}/export/level3` returning raw participant responses
- All endpoints include Content-Disposition header for download
- Filename pattern: `session-{month}-{team_name}-level{N}.json`

### Task 2: Add synthesis retry endpoint
- Added `POST /{session_id}/synthesize/retry` to force regeneration
- Clears synthesis_themes, synthesis_statements, synthesis_gap_type before triggering
- Only works in CLOSED state (matches existing synthesize endpoint)
- Added `GET /{session_id}/synthesis-status` for polling:
  - Returns status: "pending" | "complete" | "failed"
  - Includes has_error boolean and error_message for failed state

## Decisions Made

| ID | Decision | Choice | Rationale |
|----|----------|--------|-----------|
| PRES-05 | Export granularity | Three separate endpoints per level | Clean separation, client picks needed depth |
| SYNTH-04 | Retry behavior | Clear data then regenerate | Distinguishes from trigger which respects existing valid synthesis |

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- All five new endpoints import successfully
- Syntax validation passes
- Level endpoints return appropriate JSON structures
- Retry endpoint clears data before background task

## Success Criteria Met

- [x] Level 1 export returns only themes and gap_type
- [x] Level 2 export returns attributed statements array
- [x] Level 3 export returns raw participant responses
- [x] Retry endpoint forces synthesis regeneration
- [x] Synthesis status endpoint returns proper status values

## Files Changed

| File | Change |
|------|--------|
| `the55/app/routers/sessions.py` | Added 5 new endpoints (+135 lines) |

## Commits

1. `c71b306` feat(22-01): add level-specific export endpoints
2. `8b02158` feat(22-01): add synthesis retry and status endpoints

## Next Phase Readiness

Phase 22 Plan 01 complete. This concludes the v2.1 Facilitator Experience milestone.
