---
phase: 26-facilitator-dashboard
plan: 01
subsystem: backend/admin
tags: [dashboard, sessions, settings, password, admin]

dependency_graph:
  requires: []
  provides: [sessions-first-dashboard-data, settings-endpoints, password-change]
  affects: [26-02-dashboard-ui]

tech_stack:
  added: []
  patterns:
    - Sessions-first dashboard queries (active + recent)
    - Self-service password management
    - .env file password hash update

file_tracking:
  created: []
  modified:
    - the55/app/routers/admin.py
    - the55/app/services/auth.py

decisions:
  - Dashboard shows active sessions (current month, not revealed) first
  - Recent sessions limited to 5 most recently revealed
  - Password changes update .env file directly (requires restart for settings cache)
  - Minimum password length of 8 characters

metrics:
  duration: ~3m
  completed: 2026-01-21
---

# Phase 26 Plan 01: Dashboard Backend Summary

Sessions-first dashboard data queries and self-service password change endpoints for the facilitator command center.

## Objective

Create backend endpoints that support a sessions-first dashboard (matching facilitator's mental model) and enable self-service password management.

## What Was Built

### Dashboard Endpoint Updates (`the55/app/routers/admin.py`)

Updated `admin_dashboard` to provide sessions-first data:

**Queries added:**
- `active_sessions`: Current month sessions NOT in REVEALED state, with team data via joinedload, ordered by created_at desc
- `recent_sessions`: Last 5 REVEALED sessions, with team data, ordered by revealed_at desc
- `teams`: All teams (existing query, preserved for team management)

**Template context:**
- `active_sessions` - for "Today's Sessions" section
- `recent_sessions` - for "Recent History" section
- `teams` - for team management access
- `current_month` - for one-click session creation links

**Helper function:**
- `get_current_month()` - Returns YYYY-MM format for current month

### Settings Endpoints (`the55/app/routers/admin.py`)

**GET /admin/settings**
- Renders password change form template
- Protected by AuthDep

**POST /admin/settings/password**
- Validates current password against stored hash
- Validates new password minimum length (8 characters)
- Validates new password matches confirmation
- Generates Argon2 hash for new password
- Updates .env file with new hash
- Returns success message noting restart requirement

### Password Hash Update (`the55/app/services/auth.py`)

**update_password_hash(new_hash, env_path=".env")**
- Reads .env file content
- Uses regex to replace FACILITATOR_PASSWORD_HASH value
- Writes updated content back to file
- Returns bool success indicator

## Code Snippets

### Dashboard Query Pattern

```python
active_sessions = db.query(Session).options(
    joinedload(Session.team)
).filter(
    Session.month == current_month,
    Session.state != SessionState.REVEALED
).order_by(Session.created_at.desc()).all()
```

### Password Validation Flow

```python
# Verify current password
if not verify_password(current_password, settings.facilitator_password_hash):
    return error("Current password is incorrect")

# Validate length
if len(new_password) < 8:
    return error("Password must be at least 8 characters")

# Validate match
if new_password != confirm_password:
    return error("Passwords do not match")

# Generate and store
new_hash = hash_password(new_password)
update_password_hash(new_hash)
```

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| 43d14fd | feat | Sessions-first dashboard and settings endpoints |

## Verification Results

- Admin router imports successfully
- Auth service imports successfully
- App starts without errors
- All endpoint functions defined correctly

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

Plan 26-01 complete. Ready for:
- **Plan 26-02: Dashboard UI** - Templates that consume the new data context
