# Architecture Patterns: UX Refinement Integration

**Project:** The 55 App
**Focus:** Integrating UX changes into existing FastAPI/Jinja2 architecture
**Researched:** 2026-01-24
**Overall Confidence:** HIGH

## Executive Summary

The 55 App uses a classic server-rendered MPA (Multi-Page Application) architecture with FastAPI + Jinja2 templates, SQLite database, and client-side polling for real-time updates. The proposed UX refinements fit naturally into this architecture with minimal structural changes:

1. **State machine simplification** (removing DRAFT) requires only model enum changes and route updates
2. **Auto-synthesize/auto-reveal** leverages existing background task infrastructure with polling-based state detection
3. **View Transitions API** works natively with server-rendered MPAs through CSS-only opt-in
4. **Image subset randomization** is already implemented server-side (session-seeded shuffling)
5. **Enhanced polling** extends existing `/status` endpoints with additional metadata
6. **Progressive inputs** use existing client-side patterns (no framework changes)

**Key finding:** The architecture already supports these patterns. Changes are additive, not transformative.

## Current Architecture Analysis

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    nginx (static files)                      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application (Gunicorn/Uvicorn)          │
├─────────────────────────────────────────────────────────────┤
│  Routers:                                                    │
│  • participant.py - Public join flow                        │
│  • sessions.py    - Admin session management                │
│  • admin.py       - Dashboard                               │
│  • images.py      - Image API                               │
├─────────────────────────────────────────────────────────────┤
│  Services:                                                   │
│  • synthesis.py   - Background Claude API synthesis         │
│  • images.py      - ImageLibrary (session-seeded shuffle)   │
├─────────────────────────────────────────────────────────────┤
│  Templates: Jinja2 (server-rendered HTML)                   │
│  Static JS: Polling (2.5-3s intervals), no build tools      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              SQLite Database (app.db)                        │
│  Models: Team, Member, Session, Response                    │
│  State Machine: DRAFT → CAPTURING → CLOSED → REVEALED       │
└─────────────────────────────────────────────────────────────┘
```

### State Machine (Current)

```
DRAFT
  │ POST /admin/sessions/{id}/start
  ↓
CAPTURING (participants can respond)
  │ POST /admin/sessions/{id}/close
  ↓
CLOSED (synthesis generation)
  │ POST /admin/sessions/{id}/reveal (manual)
  ↓
REVEALED (results visible)
```

**Observations:**
- DRAFT state exists but is rarely used (sessions immediately start capturing)
- Synthesis is manually triggered via POST `/synthesize`
- Reveal is manually triggered via POST `/reveal`
- Polling endpoints: `/status` returns state + member counts every 2.5s

## Recommended Architecture: UX Changes Integration

### 1. State Machine Modification

**Change:** Remove DRAFT state, sessions start in CAPTURING

**Impact Assessment:**
- **Database migration:** Add new enum value, update existing rows
- **Route changes:** Remove `/start` endpoint, update `/create` to set CAPTURING
- **Template changes:** Remove "Start Capturing" button from admin UI
- **Backward compatibility:** Existing DRAFT sessions can be migrated to CAPTURING

**Implementation Pattern:**

```python
# app/db/models.py
class SessionState(enum.Enum):
    """Session lifecycle states."""
    CAPTURING = "capturing"  # Entry state (was DRAFT)
    CLOSED = "closed"
    REVEALED = "revealed"
    # DRAFT removed

# Migration approach (manual SQL or Alembic)
UPDATE sessions SET state = 'capturing' WHERE state = 'draft';
```

**Files to modify:**
- `app/db/models.py` - Remove DRAFT from enum
- `app/routers/sessions.py` - Update `create_session()` to set CAPTURING, remove `/start` endpoint
- `app/routers/participant.py` - Update validation logic (remove DRAFT checks)
- `templates/admin/sessions/view.html` - Remove "Start Capturing" button
- Migration script to update existing sessions

**Risk:** Low. DRAFT state is barely used; can migrate all DRAFT → CAPTURING automatically.

### 2. Auto-Synthesize on Close

**Change:** Trigger synthesis automatically when session closes (background task)

**Integration Point:** Existing `BackgroundTasks` in `/close` endpoint

**Implementation Pattern:**

```python
# app/routers/sessions.py
@router.post("/{session_id}/close")
async def close_capture(
    session_id: int,
    background_tasks: BackgroundTasks,  # Add dependency
    auth: AuthDep,
    db: DbDep
):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404)

    if session.state != SessionState.CAPTURING:
        raise HTTPException(status_code=400)

    session.state = SessionState.CLOSED
    session.closed_at = datetime.utcnow()
    session.synthesis_themes = None  # Clear any previous attempts
    db.commit()

    # AUTO-TRIGGER SYNTHESIS (NEW)
    background_tasks.add_task(run_synthesis_task, session_id)

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)
```

**Files to modify:**
- `app/routers/sessions.py` - Modify `/close` endpoint to trigger synthesis
- Remove manual `/synthesize` endpoint (or keep as "retry" fallback)

**Polling integration:** Existing `/status` endpoint already returns synthesis status via `has_synthesis` field. No changes needed.

**Risk:** None. Background task infrastructure already exists and is tested.

### 3. Auto-Reveal on Synthesis Complete

**Change:** Automatically transition CLOSED → REVEALED when synthesis completes

**Two architectural approaches:**

#### Option A: Synthesis service updates state directly (RECOMMENDED)

```python
# app/services/synthesis.py
async def _generate_and_store_synthesis(session_id: int) -> None:
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        # ... synthesis logic ...

        # Store results
        session.synthesis_themes = result.themes
        session.synthesis_statements = json.dumps([s.model_dump() for s in result.statements])
        session.synthesis_gap_type = result.gap_type

        # AUTO-REVEAL (NEW)
        if session.state == SessionState.CLOSED:
            session.state = SessionState.REVEALED
            session.revealed_at = datetime.utcnow()

        db.commit()
    finally:
        db.close()
```

**Pros:**
- Single atomic transaction (synthesis + reveal)
- No polling delay for reveal
- Simpler logic

**Cons:**
- Service layer directly modifies application state (couples concerns)

#### Option B: Polling-based auto-reveal (client-side trigger)

Admin dashboard polls `/status`, detects synthesis completion, auto-POSTs to `/reveal`.

**Pros:**
- Separation of concerns (service only writes synthesis, controller handles state)
- Existing polling infrastructure

**Cons:**
- Adds polling delay (2.5s max)
- More complex client logic

**Recommendation:** Use Option A (synthesis service auto-reveals). Cleaner, faster, and synthesis is already tightly coupled to state lifecycle.

**Files to modify:**
- `app/services/synthesis.py` - Add auto-reveal logic
- Remove `/reveal` endpoint or keep as manual override
- `templates/admin/sessions/view.html` - Remove "Reveal" button

**Risk:** Low. Synthesis service already has database access and modifies session.

### 4. View Transitions API Integration

**Background:** View Transitions API for MPAs enables smooth animations between server-rendered pages with minimal code.

**How it works:**
1. Add `@view-transition { navigation: auto; }` to CSS (both current and destination pages)
2. Browser automatically captures snapshots during same-origin navigation
3. Animates between old/new page states
4. **No JavaScript required** for basic transitions

**Requirements:**
- Same-origin navigation (✓ already met)
- Both pages include `@view-transition` CSS rule
- Navigation completes in <4 seconds (✓ FastAPI responses are fast)

**Implementation Pattern:**

```css
/* static/css/main.css */
@view-transition {
  navigation: auto;
}

/* Customize slide animations */
::view-transition-old(root) {
  animation: 0.3s ease-in both slide-out;
}

::view-transition-new(root) {
  animation: 0.3s ease-in both slide-in;
}

@keyframes slide-out {
  from { transform: translateX(0%); }
  to { transform: translateX(-100%); }
}

@keyframes slide-in {
  from { transform: translateX(100%); }
  to { transform: translateX(0%); }
}
```

**For state-specific transitions** (waiting → synthesis reveal):

```javascript
// templates/participant/waiting.html (enhanced)
window.addEventListener("pagereveal", (e) => {
  if (e.viewTransition && document.querySelector('.synthesis-view')) {
    // Fade in synthesis view
    document.body.style.animation = "fadeIn 0.5s ease-in";
  }
});
```

**Files to modify:**
- `static/css/main.css` - Add `@view-transition` rule and custom animations
- Optionally: `templates/participant/waiting.html` - Add `pagereveal` handler for custom animation

**Browser support:** Chrome 126+, Safari 18.2+ (as of 2026). Graceful degradation: unsupported browsers get instant page change (no animation).

**Risk:** None. Progressive enhancement—fails gracefully in unsupported browsers.

### 5. Enhanced Polling Responses

**Change:** Add synthesis progress and state transition metadata to `/status` endpoint

**Current response:**
```json
{
  "session_id": 123,
  "state": "capturing",
  "total_members": 8,
  "submitted_count": 5,
  "members": [...],
  "has_synthesis": false,
  "synthesis_pending": false
}
```

**Enhanced response for CLOSED state:**
```json
{
  "session_id": 123,
  "state": "closed",
  "total_members": 8,
  "submitted_count": 8,
  "members": [...],
  "has_synthesis": false,
  "synthesis_pending": true,
  "synthesis_progress": {
    "status": "generating",  // "pending" | "generating" | "complete" | "failed"
    "message": "Analyzing team responses...",
    "estimated_seconds": 15  // Optional: time remaining estimate
  }
}
```

**For REVEALED transition:**
```json
{
  "session_id": 123,
  "state": "revealed",  // State changed—client should redirect
  "transition": "closed_to_revealed",  // Trigger animation
  ...
}
```

**Implementation:**

```python
# app/routers/participant.py - Enhance /join/{code}/session/{id}/status
@router.get("/{code}/session/{session_id}/status")
async def get_participant_status(...):
    # ... existing code ...

    response_data = {
        "session_id": session_id,
        "state": session.state.value,
        "total_members": len(members),
        "submitted_count": len(responses),
        "can_edit": session.state == SessionState.CAPTURING
    }

    # Add synthesis progress for CLOSED/REVEALED states
    if session.state == SessionState.CLOSED:
        if session.synthesis_themes is None:
            status = "pending"
            message = "Waiting to start synthesis..."
        elif session.synthesis_themes.lower() == "generating...":
            status = "generating"
            message = "Analyzing team responses..."
        else:
            status = "complete"
            message = "Synthesis complete"

        response_data["synthesis_progress"] = {
            "status": status,
            "message": message
        }

    return JSONResponse(response_data)
```

**Client-side integration (waiting screen):**

```javascript
// templates/participant/waiting.html
async function checkStatus() {
    const data = await fetch(`/join/${teamCode}/session/${sessionId}/status`).then(r => r.json());

    if (data.state === 'revealed') {
        window.location.href = `/join/${teamCode}/session/${sessionId}/synthesis`;
        return;
    }

    // Update waiting message based on synthesis progress
    if (data.synthesis_progress) {
        messageEl.textContent = data.synthesis_progress.message;

        // Optionally show progress indicator
        if (data.synthesis_progress.status === 'generating') {
            spinnerEl.classList.add('active');
        }
    }
}
```

**Files to modify:**
- `app/routers/participant.py` - Enhance `/status` endpoint
- `app/routers/sessions.py` - Enhance admin `/status` endpoint (same pattern)
- `templates/participant/waiting.html` - Update polling logic
- `static/js/meeting.js` - Update meeting screen polling

**Risk:** Low. Additive change to existing endpoint (backward compatible).

### 6. Image Subset Implementation

**Current state:** Already implemented!

The `ImageLibrary` service in `app/services/images.py` uses session-seeded shuffling:

```python
# app/services/images.py (existing)
def get_shuffled_images(self, seed: int = None) -> List[ImageMetadata]:
    """Return shuffled copy of library. Seed ensures consistency."""
    shuffled = self.images.copy()
    if seed is not None:
        random.seed(seed)
    random.shuffle(shuffled)
    return shuffled
```

**Usage in respond route:**

```python
# app/routers/participant.py (existing)
shuffled_images = library.get_shuffled_images(seed=session.id)
```

**To limit to ~60 images from 200+:**

```python
# app/services/images.py - Modify get_shuffled_images
def get_shuffled_images(self, seed: int = None, limit: int = None) -> List[ImageMetadata]:
    """Return shuffled copy of library. Seed ensures consistency."""
    shuffled = self.images.copy()
    if seed is not None:
        random.seed(seed)
    random.shuffle(shuffled)

    # NEW: Apply limit
    if limit is not None:
        shuffled = shuffled[:limit]

    return shuffled
```

**Configuration:**

```python
# app/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    images_subset_size: int = 60  # Limit images per session
```

**Route update:**

```python
# app/routers/participant.py
settings = get_settings()
shuffled_images = library.get_shuffled_images(
    seed=session.id,
    limit=settings.images_subset_size
)
```

**Recommendation:** Server-side selection (current approach) is optimal:
- Consistent subset per session (all participants see same 60 images)
- No client-side filtering overhead
- Reduces page weight (fewer images to render)
- Session-seeded = deterministic but varied across sessions

**Files to modify:**
- `app/services/images.py` - Add `limit` parameter
- `app/config.py` - Add `images_subset_size` setting
- `app/routers/participant.py` - Pass limit to `get_shuffled_images()`

**Risk:** None. Backward compatible (limit is optional).

### 7. Progressive Input Patterns

**Current:** Client-side validation in respond form (vanilla JS)

**Pattern to extend:**

```javascript
// static/js/respond.js (example—doesn't exist yet, but pattern is inline in templates)
class ProgressiveInput {
    constructor(formElement) {
        this.form = formElement;
        this.initValidation();
    }

    initValidation() {
        // Real-time bullet validation
        this.form.querySelectorAll('textarea.bullet-input').forEach(textarea => {
            textarea.addEventListener('input', (e) => {
                this.validateBullet(e.target);
            });
        });
    }

    validateBullet(textarea) {
        const length = textarea.value.length;
        const counter = textarea.nextElementSibling; // Character counter

        if (length > 500) {
            textarea.classList.add('error');
            counter.textContent = `${length}/500 (too long)`;
        } else {
            textarea.classList.remove('error');
            counter.textContent = `${length}/500`;
        }
    }
}

// Initialize on respond page
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#response-form');
    if (form) new ProgressiveInput(form);
});
```

**No architectural changes needed.** This is pure client-side enhancement using existing patterns.

**Files to create/modify:**
- `static/js/progressive-inputs.js` - Reusable input validation
- `templates/participant/respond.html` - Include script

**Risk:** None. Progressive enhancement.

### 8. Meeting View Auto-Transitions

**Current:** Meeting view (`/admin/sessions/{id}/meeting`) uses single template with state-driven sections:

```jinja2
{% if session.state.value in ['draft', 'capturing'] %}
  <!-- Show QR code and status -->
{% elif session.state.value == 'closed' %}
  <!-- Show "Analyzing..." waiting state -->
{% elif session.state.value == 'revealed' %}
  <!-- Show synthesis levels -->
{% endif %}
```

**Enhancement:** Use polling to detect state changes and trigger View Transitions

```javascript
// static/js/meeting.js (existing file)
async function pollStatus() {
    const data = await fetch(`/admin/sessions/${sessionId}/status`).then(r => r.json());

    // State transition detection (ALREADY EXISTS)
    if (data.state !== currentState) {
        handleStateTransition(currentState, data.state);
        return;
    }
    // ... update UI ...
}

function handleStateTransition(fromState, toState) {
    if (toState === 'revealed') {
        // Add View Transition enhancement
        if (document.startViewTransition) {
            document.startViewTransition(() => {
                window.location.reload();
            });
        } else {
            window.location.reload();
        }
    } else {
        window.location.reload();
    }
}
```

**Current implementation already:**
- Polls `/status` every 2.5s
- Detects state changes
- Reloads page on transition

**Enhancement:** Use `document.startViewTransition()` for SPA-like reload animation (View Transitions API Level 1).

**Files to modify:**
- `static/js/meeting.js` - Add View Transition wrapper (already has polling)

**Risk:** None. Progressive enhancement (falls back to instant reload).

## Data Flow Changes

### Current Flow (Participant Response)

```
1. Participant submits response
   POST /join/{code}/session/{id}/member/{mid}/respond
   ↓
2. Save to database, redirect to waiting
   GET /join/{code}/session/{id}/member/{mid}/waiting
   ↓
3. Polling starts (every 3s)
   GET /join/{code}/session/{id}/status
   ↓
4. Facilitator manually closes session
   POST /admin/sessions/{id}/close
   ↓
5. Facilitator manually triggers synthesis
   POST /admin/sessions/{id}/synthesize (background task)
   ↓
6. Polling detects synthesis complete (has_synthesis=true)
   ↓
7. Facilitator manually reveals
   POST /admin/sessions/{id}/reveal
   ↓
8. Polling detects state=revealed, redirects to synthesis view
```

### New Flow (Auto-Synthesize + Auto-Reveal)

```
1. Participant submits response
   POST /join/{code}/session/{id}/member/{mid}/respond
   ↓
2. Save to database, redirect to waiting
   GET /join/{code}/session/{id}/member/{mid}/waiting
   ↓
3. Polling starts (every 3s) with enhanced progress
   GET /join/{code}/session/{id}/status
   Response: { state: "capturing", submitted_count: 5/8 }
   ↓
4. Facilitator closes session
   POST /admin/sessions/{id}/close
   ⚡ AUTOMATICALLY triggers background synthesis task
   ↓
5. Polling detects synthesis in progress
   GET /join/{code}/session/{id}/status
   Response: { state: "closed", synthesis_progress: { status: "generating", ... }}
   Waiting screen updates: "Analyzing team responses..."
   ↓
6. Synthesis completes
   Background task writes synthesis + ⚡ AUTO-REVEALS (state → REVEALED)
   ↓
7. Polling detects state=revealed
   Response: { state: "revealed" }
   ↓
8. Client redirects to synthesis view with View Transition animation
   window.location.href = `/join/.../synthesis` (smooth animation)
```

**Key differences:**
- Steps 5-7 (manual synthesis + reveal) → Single automatic step
- Enhanced polling provides live progress feedback
- View Transitions add smooth animations (no behavioral change)

## Build Order and Dependencies

### Phase 1: Foundation (Independent Changes)

**Can be built and tested in parallel:**

1. **Remove DRAFT state**
   - Files: `models.py`, `sessions.py`, `participant.py`, templates
   - Migration: SQL script to update existing sessions
   - Test: Create new session → should start in CAPTURING
   - Risk: Low

2. **Image subset limit**
   - Files: `images.py`, `config.py`, `participant.py`
   - Test: Verify ~60 images shown, consistent per session
   - Risk: None

3. **View Transitions CSS**
   - Files: `main.css`
   - Test: Navigate between pages, verify animation (Chrome/Safari)
   - Risk: None (progressive enhancement)

4. **Progressive input validation**
   - Files: `progressive-inputs.js`, `respond.html`
   - Test: Type in bullet inputs, verify character counter
   - Risk: None

### Phase 2: State Machine Changes (Sequential)

**Build in this order (dependencies):**

5. **Auto-synthesize on close** (depends on Phase 1.1)
   - Files: `sessions.py` (/close endpoint)
   - Test: Close session → verify background task fires, synthesis_themes="GENERATING..."
   - Risk: Low

6. **Enhanced polling responses** (independent, but pairs with 5)
   - Files: `participant.py`, `sessions.py` (/status endpoints)
   - Test: Poll during synthesis → verify synthesis_progress object
   - Risk: Low

7. **Auto-reveal on synthesis complete** (depends on Phase 2.5)
   - Files: `synthesis.py`
   - Test: Complete synthesis → verify state=REVEALED, revealed_at set
   - Risk: Low

### Phase 3: Client Integration (Sequential)

**Build in this order:**

8. **Update waiting screen polling** (depends on Phase 2.6)
   - Files: `waiting.html` (JS polling logic)
   - Test: Wait on waiting screen → see "Analyzing..." → auto-redirect to synthesis
   - Risk: Low

9. **Update meeting screen polling** (depends on Phase 2.6-7)
   - Files: `meeting.js`
   - Test: Admin meeting view → close session → see analyzing state → auto-transition to synthesis
   - Risk: Low

10. **View Transition enhancements** (depends on all previous)
    - Files: `waiting.html`, `meeting.js` (pagereveal handlers)
    - Test: State transitions trigger smooth animations
    - Risk: None

### Testing Strategy at Each Stage

**Phase 1 testing:**
- Unit tests for image service limit
- Manual test: Create session, verify CAPTURING state
- Visual test: Page transitions show animations (Chrome/Safari)

**Phase 2 testing:**
- Integration test: Close → auto-synthesize → auto-reveal flow
- API test: Poll `/status` during each state, verify response structure
- Error test: Synthesis failure → verify error states in polling

**Phase 3 testing:**
- E2E test: Participant submits → waits → sees synthesis (full flow)
- E2E test: Admin meeting view → close → sees analyzing → sees synthesis
- Cross-browser: Test View Transitions fallback in unsupported browsers

## Migration Path

### Database Migration

**Step 1: Add REVEALED to enum (if not exists)**
Already exists—no change needed.

**Step 2: Remove DRAFT from enum**

Option A: SQL migration (simple)
```sql
-- Update existing DRAFT sessions to CAPTURING
UPDATE sessions SET state = 'capturing' WHERE state = 'draft';

-- Application code then removes DRAFT from enum (breaking change for old code)
```

Option B: Graceful migration (if old app versions still running)
```sql
-- Keep DRAFT in enum, add application logic to treat DRAFT as CAPTURING
-- Deploy new code that creates sessions in CAPTURING
-- After all instances updated, run cleanup migration
```

**Recommendation:** Option A (simple migration). DRAFT is barely used.

### Rollback Strategy

**If auto-synthesize causes issues:**
1. Keep manual `/synthesize` endpoint as fallback
2. Add feature flag: `AUTO_SYNTHESIZE_ENABLED=false` to disable auto-trigger
3. Revert `/close` endpoint to not trigger background task

**If auto-reveal causes issues:**
1. Add feature flag: `AUTO_REVEAL_ENABLED=false`
2. Modify synthesis service to skip auto-reveal when flag off
3. Keep manual `/reveal` endpoint

**If View Transitions cause UX issues:**
1. Remove `@view-transition` CSS rule
2. Unsupported browsers already ignore it (no rollback needed)

## Performance Considerations

### Polling Frequency

**Current:** 2.5-3 seconds (randomized to avoid thundering herd)

**Impact of changes:**
- Enhanced polling responses add ~100 bytes to JSON (negligible)
- Auto-reveal reduces polling duration (no waiting for manual reveal)
- Net effect: Slight improvement (fewer round-trips)

**Recommendation:** Keep 2.5-3s interval. No changes needed.

### Background Task Timeout

**Current:** Synthesis runs in background with new event loop (no worker timeout)

**Timeout considerations:**
- Claude API calls: typically 3-10 seconds for synthesis
- View Transitions timeout: 4 seconds for navigation
- Auto-reveal after synthesis: instant (same database transaction)

**Risk mitigation:**
- Synthesis already has error handling (stores "failed" message)
- Auto-reveal is atomic with synthesis (no additional timeout risk)

### Server-Side vs Client-Side Trade-offs

**Image subset selection:**
- ✅ Server-side (current): Consistent, performant, cacheable
- ❌ Client-side: Inconsistent across participants, higher bandwidth

**State transitions:**
- ✅ Server-side (auto-reveal in synthesis): Atomic, reliable
- ❌ Client-side (polling-based reveal): 2.5s delay, race conditions

**Validation:**
- ✅ Client-side (progressive inputs): Instant feedback, better UX
- ⚠️ Server-side: Always validate on submit (security)

**Recommendation:** Current architecture balance is optimal. Changes maintain this balance.

## Component Integration Points

### New Components

**None required.** All changes extend existing components.

### Modified Components

| Component | Change | Risk | Test Coverage |
|-----------|--------|------|---------------|
| `SessionState` enum | Remove DRAFT | Low | Unit tests |
| `sessions.py` `/close` | Add background task trigger | Low | Integration tests |
| `synthesis.py` | Add auto-reveal logic | Low | Integration tests |
| `/status` endpoints | Add synthesis_progress | Low | API tests |
| `waiting.html` polling | Enhance progress display | Low | E2E tests |
| `meeting.js` polling | Enhance progress display | Low | E2E tests |
| `main.css` | Add View Transitions | None | Manual testing |
| `images.py` | Add limit parameter | None | Unit tests |

### Integration Testing Strategy

**Critical paths to test:**

1. **Happy path:** Participant submits → facilitator closes → synthesis runs → auto-reveals → participant sees results
2. **Edge case:** Close with <3 responses → synthesis fails → error state displayed
3. **Edge case:** Synthesis Claude API fails → error state displayed → manual retry works
4. **Edge case:** Close → reopen → close again → synthesis re-runs correctly
5. **Cross-browser:** View Transitions work (Chrome/Safari) and gracefully degrade (Firefox)

## Quality Gates

### Backward Compatibility

✅ **No breaking changes to existing endpoints:**
- `/status` endpoint adds fields but doesn't remove any
- Participant flow routes unchanged
- Admin control panel routes unchanged (only button visibility changes)

✅ **Mid-session participants unaffected:**
- Participant in CAPTURING state can still submit response
- Polling continues to work (enhanced with extra data)
- Redirect logic on state change preserved

### Migration Safety

✅ **State machine changes are reversible:**
- Keep manual `/synthesize` and `/reveal` endpoints as fallback
- Feature flags allow disabling auto-synthesis/auto-reveal
- Database migration is simple UPDATE query (reversible)

✅ **Testing at each stage:**
- Phase 1: Test each independent change in isolation
- Phase 2: Test state machine flow end-to-end
- Phase 3: Test full participant + admin experience

### Performance Gates

✅ **No additional latency:**
- Auto-synthesize triggers immediately on close (no delay)
- Auto-reveal is atomic with synthesis (no polling delay)
- View Transitions add animation but don't block navigation

✅ **No thundering herd:**
- Polling intervals remain randomized (2.5-3s)
- Background tasks run in separate event loop (no worker blocking)

## Architectural Principles Preserved

### Server-Rendered First
✅ All pages remain Jinja2 templates (no SPA conversion)

### Progressive Enhancement
✅ View Transitions, progressive inputs are optional enhancements

### Stateless HTTP
✅ No WebSockets, no session state in memory (database is source of truth)

### Polling for Real-Time
✅ Existing polling strategy enhanced, not replaced

### Background Tasks for Long Operations
✅ Synthesis remains background task (now auto-triggered)

## Recommended Implementation Order

### Sprint 1: Foundation (1-2 days)
- Remove DRAFT state (migration + code changes)
- Add image subset limit
- Add View Transitions CSS
- Test: Create session, verify CAPTURING state, verify animations

### Sprint 2: Auto-Synthesis (2-3 days)
- Auto-trigger synthesis on close
- Enhance `/status` endpoints with synthesis_progress
- Update waiting screen polling
- Test: Close → synthesis runs → progress displayed

### Sprint 3: Auto-Reveal (1-2 days)
- Add auto-reveal to synthesis service
- Update meeting screen polling
- Test: Synthesis completes → auto-reveals → participants redirected

### Sprint 4: Polish (1 day)
- Add progressive input validation
- Fine-tune View Transition animations
- Cross-browser testing
- Performance testing

**Total estimated effort:** 5-8 days for full implementation

## Risk Summary

| Change | Risk Level | Mitigation |
|--------|-----------|------------|
| Remove DRAFT | Low | Simple migration, keep manual controls as fallback |
| Auto-synthesize | Low | Background task already tested, add feature flag |
| Auto-reveal | Low | Atomic with synthesis, keep manual reveal as fallback |
| View Transitions | None | Progressive enhancement, graceful degradation |
| Enhanced polling | Low | Additive change, backward compatible |
| Image subset | None | Optional parameter, backward compatible |
| Progressive inputs | None | Client-side only, no server impact |

**Overall risk assessment:** LOW

All changes are additive or isolated. No breaking changes to core participant flow. Rollback strategies exist for each change.

## Sources

Architecture patterns and integration approaches informed by:

- [View Transitions API - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using)
- [Cross-document view transitions - Chrome for Developers](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document)
- [FastAPI Background Tasks - Official Documentation](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Building State-Aware Applications with FSM and FastAPI - Medium](https://medium.com/@bitwise_insights/building-state-aware-applications-with-finite-state-machines-and-fastapi-11d9b2894f3a)
- [Server-Side vs Client-Side Filtering - DEV Community](https://dev.to/marmariadev/deciding-between-client-side-and-server-side-filtering-22l9)
- [Server-Side Rendering vs Client-Side Rendering - Web Peak](https://webpeak.org/blog/server-side-rendering-vs-client-side-rendering/)
