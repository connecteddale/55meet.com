---
phase: 12-session-infrastructure
plan: 01
subsystem: sessions
tags: [fastapi, sessions, state-machine, crud]

dependency_graph:
  requires:
    - "10-01 (FastAPI foundation)"
    - "10-02 (ORM models with Session, SessionState)"
    - "10-04 (Auth dependency)"
    - "11-01 (Team model)"
    - "11-02 (Member model)"
  provides:
    - "Session CRUD endpoints"
    - "Session state machine API"
    - "Session status polling endpoint"
  affects:
    - "12-02 (Session templates)"
    - "13-xx (Participant flow)"
    - "14-xx (AI synthesis)"

tech_stack:
  added: []
  patterns:
    - "State machine via enum transitions"
    - "JSON status endpoint for polling"
    - "HTTPException for state violation errors"

key_files:
  created:
    - the55/app/routers/sessions.py
  modified:
    - the55/app/routers/__init__.py
    - the55/app/main.py

decisions:
  - key: "State enforcement at router level"
    choice: "HTTPException 400 on invalid state transitions"
    rationale: "Fail fast, clear error messages for debugging"
  - key: "Recalibration as separate endpoint"
    choice: "POST /{session_id}/recalibration with bool form field"
    rationale: "Decoupled from state machine, can toggle at any time"

metrics:
  duration: "3m"
  completed: "2026-01-18"
---

# Phase 12 Plan 01: Session CRUD and Control Summary

**One-liner:** Session router with CRUD, state machine (draft->capturing->closed->revealed), and JSON status polling for facilitator control panel.

## What Was Built

### Session Router (`the55/app/routers/sessions.py`)

Complete session management API with 9 endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/sessions/team/{team_id}` | GET | List all sessions for a team |
| `/admin/sessions/team/{team_id}/create` | GET | Show create session form |
| `/admin/sessions/team/{team_id}/create` | POST | Create new session |
| `/admin/sessions/{session_id}` | GET | View session details + control panel |
| `/admin/sessions/{session_id}/start` | POST | Transition draft -> capturing |
| `/admin/sessions/{session_id}/close` | POST | Transition capturing -> closed |
| `/admin/sessions/{session_id}/reveal` | POST | Transition closed -> revealed |
| `/admin/sessions/{session_id}/status` | GET | JSON status for polling |
| `/admin/sessions/{session_id}/recalibration` | POST | Mark recalibration complete |

### State Machine Enforcement

Each state transition validates current state:
- `start_capturing`: Only from DRAFT
- `close_capture`: Only from CAPTURING
- `reveal_synthesis`: Only from CLOSED

Invalid transitions return HTTP 400 with descriptive message:
```
"Cannot close capture. Session is in 'draft' state."
```

### Status Polling Endpoint

Returns JSON for facilitator real-time view:
```json
{
  "session_id": 1,
  "state": "capturing",
  "total_members": 6,
  "submitted_count": 4,
  "members": [
    {"id": 1, "name": "Alice", "submitted": true},
    {"id": 2, "name": "Bob", "submitted": false}
  ]
}
```

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- [x] Sessions router created with CRUD endpoints
- [x] State transitions enforced (draft -> capturing -> closed -> revealed)
- [x] Status polling endpoint returns JSON with member counts
- [x] Recalibration completion endpoint works
- [x] Router registered in main app

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 3470b34 | feat | Create sessions router with CRUD and state control |
| e8ef2e0 | feat | Register sessions router in main app |

## Next Phase Readiness

Ready for 12-02 (Session Templates):
- All session endpoints functional
- State machine enforced at API level
- Status polling ready for JavaScript integration
- Templates directory structure from 10-03 available

Templates needed:
- `admin/sessions/list.html` - Team session history
- `admin/sessions/create.html` - New session form
- `admin/sessions/view.html` - Session control panel
