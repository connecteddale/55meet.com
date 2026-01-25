---
phase: 15-ai-synthesis
plan: 02
subsystem: admin-ui
tags: [synthesis, polling, background-tasks, fastapi]
dependency-graph:
  requires: [15-01-synthesis-service]
  provides: [synthesis-trigger-endpoint, synthesis-ui]
  affects: [15-03-synthesis-display]
tech-stack:
  added: []
  patterns: [background-tasks-pattern, polling-for-async-completion]
key-files:
  created:
    - the55/static/js/polling.js
  modified:
    - the55/app/routers/sessions.py
    - the55/app/templates/admin/sessions/view.html
    - the55/app/static/css/main.css
decisions:
  - id: polling-for-synthesis
    choice: "Poll status endpoint during synthesis generation"
    why: "Simpler than WebSockets, auto-reload on completion provides good UX"
metrics:
  duration: 3m
  completed: 2026-01-19
---

# Phase 15 Plan 02: Synthesis Router Summary

POST endpoint for triggering synthesis generation with BackgroundTasks, plus UI controls for facilitator to generate and preview synthesis before revealing to participants.

## Outcome

Created synthesis trigger flow with:
- POST /{session_id}/synthesize endpoint with state validation
- Synthesis preview card showing themes, gap type, and attributed statements
- Polling-based auto-reload when synthesis completes
- Clear state transitions: Generate -> Generating -> Preview -> Reveal

## Tasks Completed

| # | Task | Commit | Key Files |
|---|------|--------|-----------|
| 1 | Add synthesis trigger endpoint to sessions router | 7c2b69e | app/routers/sessions.py |
| 2 | Update session view template for synthesis controls | 1093694 | app/templates/admin/sessions/view.html, static/js/polling.js |

## Decisions Made

**Polling for synthesis completion:**
- Reuse existing polling.js pattern from CAPTURING state
- Poll every 2.5 seconds in CLOSED state
- Auto-reload page when has_synthesis becomes true
- Simple and reliable, no WebSocket complexity needed

## Technical Details

**Trigger endpoint flow:**
1. POST /admin/sessions/{session_id}/synthesize
2. Validate session exists (404 if not)
3. Validate state is CLOSED (400 if not)
4. Check if synthesis already exists
   - If valid synthesis exists, skip and redirect
   - If failed/insufficient, allow retry
5. Add background task: run_synthesis_task(session_id)
6. Redirect to session view (303)

**View session template states:**
- `synthesis_pending`: True when CLOSED and no synthesis_themes yet
  - Shows "Generate Synthesis" button
- Synthesis generating: Not pending, not complete
  - Shows spinner with "Generating synthesis..."
- `synthesis_themes` exists:
  - Shows synthesis preview card
  - Shows "Reveal to Participants" button

**Status endpoint additions:**
- `has_synthesis: bool` - True when synthesis_themes is not None
- `synthesis_pending: bool` - True when CLOSED and no synthesis

**Polling behavior:**
- Enabled in CAPTURING and CLOSED states
- Tracks lastSynthesisStatus to detect completion
- Reloads page when has_synthesis transitions to true
- 2.5 second interval

## Deviations from Plan

None - plan executed exactly as written.

## Files Changed

**Created:**
- `the55/static/js/polling.js` - 88 lines
  - pollStatus() function for status endpoint
  - updateMemberStatus() for CAPTURING state
  - Synthesis completion detection for CLOSED state
  - Auto-reload on state/synthesis changes

**Modified:**
- `the55/app/routers/sessions.py` - +64 lines
  - Added json import
  - Added BackgroundTasks import
  - Added run_synthesis_task import
  - Updated view_session with synthesis data parsing
  - Added trigger_synthesis endpoint
  - Updated get_session_status with synthesis fields

- `the55/app/templates/admin/sessions/view.html` - +39 lines
  - Conditional synthesis controls in CLOSED state
  - Synthesis preview card with themes/gap/statements
  - Updated scripts block for CLOSED state polling

- `the55/app/static/css/main.css` - +45 lines
  - Synthesis preview styles
  - Synthesis statements list
  - Synthesis generating spinner

## Verification

All verification criteria met:
- Synthesis trigger only available in CLOSED state
- Background task does not block HTTP response (uses add_task)
- Synthesis preview displays themes, gap type, and statements
- Reveal button only shows after synthesis is complete (synthesis_themes exists)

## Next Phase Readiness

Ready for 15-03 (Synthesis Display):
- Synthesis data stored in session model
- Status endpoint provides synthesis existence flag
- Participant view will need to poll for REVEALED state
- Synthesis display components styled in main.css

Dependencies for next plan:
- Participant synthesis view page
- Poll for session.state === 'revealed'
- Read synthesis data from session
