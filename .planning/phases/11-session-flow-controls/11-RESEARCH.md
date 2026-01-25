# Phase 20: Session Flow Controls - Research

**Researched:** 2026-01-19
**Domain:** Session state management, FastAPI routing, SQLAlchemy operations
**Confidence:** HIGH

## Summary

Phase 20 adds three facilitator controls for real-world session flexibility: close early, reopen capture, and clear individual submissions. The existing codebase has solid foundations - polling infrastructure, state enforcement patterns, and participant state handling are already in place. The implementation requires adding new state transitions and a submission deletion endpoint.

The primary challenge is maintaining data integrity when reopening sessions (synthesis data must be cleared) and ensuring participants are properly notified via the existing polling mechanism.

**Primary recommendation:** Extend existing state machine with CLOSED->CAPTURING transition and add member-specific submission clearing endpoint. Reuse existing polling patterns for participant notification.

## Standard Stack

The phase uses the existing technology stack with no new dependencies.

### Core (Already in Use)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | existing | HTTP routing, form handling | Already powers all session endpoints |
| SQLAlchemy | existing | Database operations | ORM layer for Response deletion |
| Jinja2 | existing | Template rendering | Admin UI templates |

### Supporting (Already in Use)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| None new | - | - | All dependencies already present |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| New WebSocket | Existing polling | Polling adequate for 25 users, simpler |
| Soft delete | Hard delete | Hard delete simpler, no audit trail needed |

**Installation:**
```bash
# No new dependencies required
```

## Architecture Patterns

### Current State Machine
```
State transitions (current):
  DRAFT -> CAPTURING (start_capturing)
  CAPTURING -> CLOSED (close_capture)
  CLOSED -> REVEALED (reveal_synthesis)

State transitions (to add):
  CLOSED -> CAPTURING (reopen_capture)
```

### Recommended Project Structure
No structural changes needed. New endpoints fit existing patterns:

```
app/routers/sessions.py        # Add reopen endpoint, modify close confirmation
app/templates/admin/sessions/  # Update view.html with new controls
app/static/js/polling.js       # Handle reopen state notification
```

### Pattern 1: State Transition with Data Cleanup
**What:** When reopening a session, clear synthesis data to prevent stale results
**When to use:** Any state transition that invalidates derived data
**Example:**
```python
# Source: Existing pattern in sessions.py close_capture()
@router.post("/{session_id}/reopen")
async def reopen_capture(session_id: int, auth: AuthDep, db: DbDep):
    """Transition session from closed to capturing (for latecomers)."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state != SessionState.CLOSED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reopen. Session is in '{session.state.value}' state."
        )

    # Clear any existing synthesis (will need regeneration)
    session.synthesis_themes = None
    session.synthesis_statements = None
    session.synthesis_gap_type = None

    session.state = SessionState.CAPTURING
    session.closed_at = None  # Reset close timestamp
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)
```

### Pattern 2: Member-Specific Resource Deletion
**What:** Delete a specific participant's response to allow resubmission
**When to use:** When clearing individual submissions without affecting others
**Example:**
```python
# Source: Follow existing member-scoped query patterns
@router.post("/{session_id}/member/{member_id}/clear")
async def clear_member_submission(
    session_id: int,
    member_id: int,
    auth: AuthDep,
    db: DbDep
):
    """Clear a specific participant's submission to allow resubmit."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Only allow clearing during CAPTURING state
    if session.state != SessionState.CAPTURING:
        raise HTTPException(
            status_code=400,
            detail="Can only clear submissions while capturing."
        )

    # Delete the response
    response = db.query(Response).filter(
        Response.session_id == session_id,
        Response.member_id == member_id
    ).first()

    if not response:
        raise HTTPException(status_code=404, detail="No submission found")

    db.delete(response)
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)
```

### Anti-Patterns to Avoid
- **Soft delete for responses:** Don't add `deleted_at` column - hard delete is simpler and no audit trail is needed for this use case
- **Client-side state changes:** Don't show/hide controls via JavaScript based on state - use server-rendered conditional buttons (existing pattern)
- **Multiple state transitions in one endpoint:** Don't combine reopen+clear - keep endpoints focused

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Real-time notification | Custom WebSocket layer | Existing polling infrastructure | 2.5s polling proven adequate for 25 users |
| State validation | Per-endpoint checks | Existing HTTPException pattern | Consistent error handling established |
| UI updates | Complex JS state management | Auto-reload on state change | Existing polling.js triggers reload |

**Key insight:** The existing polling infrastructure (2.5s facilitator, 3s participant) handles all real-time needs. Participants already see state changes and auto-reload.

## Common Pitfalls

### Pitfall 1: Stale Synthesis After Reopen
**What goes wrong:** Session reopened, new responses added, old synthesis still displayed
**Why it happens:** Synthesis data not cleared when transitioning CLOSED->CAPTURING
**How to avoid:** Always clear synthesis_themes, synthesis_statements, synthesis_gap_type when reopening
**Warning signs:** Synthesis data present after reopen

### Pitfall 2: Clear Button on Wrong States
**What goes wrong:** Facilitator tries to clear submission after capture is closed
**Why it happens:** Clear button shown regardless of session state
**How to avoid:** Only show clear button during CAPTURING state
**Warning signs:** HTTPException 400 when clicking clear button

### Pitfall 3: Race Condition on Submission Clear
**What goes wrong:** Facilitator clears submission while participant is mid-edit
**Why it happens:** Participant has draft in localStorage, submits after clear
**How to avoid:** This is acceptable behavior - participant can still submit fresh response
**Warning signs:** None - this is expected flow

### Pitfall 4: Participant Sees Old "Submitted" Badge
**What goes wrong:** Name selection shows "Already responded" after their submission was cleared
**Why it happens:** Page cached or user navigated back
**How to avoid:** Name selection page queries fresh from DB on each load (already does this)
**Warning signs:** Participant can't select their name - but refresh fixes it

### Pitfall 5: Reopen Without Confirmation
**What goes wrong:** Facilitator accidentally reopens, needs to re-close and regenerate synthesis
**Why it happens:** Single-click reopen with no confirmation
**How to avoid:** Add JavaScript confirm() like existing close_capture pattern
**Warning signs:** Support requests about accidental reopen

## Code Examples

Verified patterns from existing codebase:

### State Transition with Validation (Existing Pattern)
```python
# Source: /var/www/the55/app/routers/sessions.py:206-223
@router.post("/{session_id}/close")
async def close_capture(session_id: int, auth: AuthDep, db: DbDep):
    """Transition session from capturing to closed."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state != SessionState.CAPTURING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot close capture. Session is in '{session.state.value}' state."
        )

    session.state = SessionState.CLOSED
    session.closed_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)
```

### Conditional UI Button Rendering (Existing Pattern)
```html
<!-- Source: /var/www/the55/app/templates/admin/sessions/view.html:36-51 -->
{% if session.state.value == 'draft' %}
<form method="post" action="/admin/sessions/{{ session.id }}/start">
    <button type="submit" class="btn btn-primary btn-large">
        Start Capturing
    </button>
</form>

{% elif session.state.value == 'capturing' %}
<form method="post" action="/admin/sessions/{{ session.id }}/close"
      onsubmit="return confirm('Close capture? Participants will no longer be able to submit.');">
    <button type="submit" class="btn btn-warning btn-large">
        Close Capture
    </button>
</form>
```

### Response Query by Session and Member (Existing Pattern)
```python
# Source: /var/www/the55/app/routers/participant.py:460-464
existing = db.query(Response).filter(
    Response.session_id == session_id,
    Response.member_id == member_id
).first()
```

### Status Endpoint JSON Response (Existing Pattern)
```python
# Source: /var/www/the55/app/routers/sessions.py:277-312
@router.get("/{session_id}/status")
async def get_session_status(session_id: int, auth: AuthDep, db: DbDep):
    """Get session status for polling (JSON endpoint)."""
    # ... query session, members, responses ...
    return JSONResponse({
        "session_id": session_id,
        "state": session.state.value,
        "total_members": len(members),
        "submitted_count": len(responded_member_ids),
        "members": member_status,
        "has_synthesis": has_synthesis,
        "synthesis_pending": synthesis_pending
    })
```

### Participant Polling Handles State Change (Existing Pattern)
```javascript
// Source: /var/www/the55/app/templates/participant/waiting.html:62-87
if (data.state === 'revealed') {
    window.location.href = `/join/${teamCode}/session/${sessionId}/synthesis`;
    return;
} else if (data.state === 'closed') {
    messageEl.textContent = 'Capture is closed. Waiting for facilitator to reveal synthesis.';
    actionsEl.innerHTML = '';  // Hide edit button
} else if (data.state === 'capturing') {
    messageEl.textContent = `Your response has been saved. Waiting for others...`;
    // Show edit button if hidden
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Linear state machine | Bidirectional CLOSED<->CAPTURING | Phase 20 | Allows reopening for latecomers |

**Deprecated/outdated:**
- N/A - this is a new feature extending existing patterns

## Open Questions

Things that couldn't be fully resolved:

1. **Should synthesis data be cleared silently or with warning?**
   - What we know: When reopening, synthesis must be cleared (data integrity)
   - What's unclear: Should confirm dialog warn about losing synthesis?
   - Recommendation: Include warning in confirm dialog: "This will clear existing synthesis."

2. **Should there be a limit on reopens?**
   - What we know: No technical constraint
   - What's unclear: Business logic around multiple reopens
   - Recommendation: No limit - trust the facilitator

3. **Should cleared submissions be logged?**
   - What we know: No audit trail currently exists
   - What's unclear: Compliance/debugging needs
   - Recommendation: No logging for v2.1 - simple hard delete is sufficient

## Sources

### Primary (HIGH confidence)
- /var/www/the55/app/routers/sessions.py - All session state transitions
- /var/www/the55/app/routers/participant.py - Participant submission handling
- /var/www/the55/app/db/models.py - Session state enum, Response model
- /var/www/the55/app/templates/admin/sessions/view.html - Facilitator control UI
- /var/www/the55/app/static/js/polling.js - Real-time update mechanism
- /var/www/the55/app/templates/participant/waiting.html - Participant state handling

### Secondary (MEDIUM confidence)
- /var/www/.planning/STATE.md - Prior design decisions
- /var/www/.planning/ROADMAP.md - Phase dependencies and requirements

### Tertiary (LOW confidence)
- None - all findings verified against existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - No new dependencies, using existing patterns
- Architecture: HIGH - Follows established state transition patterns
- Pitfalls: HIGH - Identified from code analysis and realistic scenarios

**Research date:** 2026-01-19
**Valid until:** Indefinite (internal codebase patterns)
