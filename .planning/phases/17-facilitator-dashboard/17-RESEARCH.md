# Phase 26: Facilitator Dashboard - Research

**Researched:** 2026-01-21
**Domain:** FastAPI dashboard patterns, password management, client-side search
**Confidence:** HIGH

## Summary

Research into the existing codebase reveals a clear path forward for the Facilitator Dashboard phase. The current dashboard at `/admin` is minimal - showing teams in a grid and a single link to session history. The v2.2 goal is a "command center" that puts today's sessions first, enables one-click session creation, and adds search/filter capabilities.

The existing design system (Phase 23) provides all necessary tokens for premium styling. The auth system uses pwdlib with Argon2 for password hashing and already has a `hash_password()` function ready for the password change feature. The patterns established in sessions.py for querying and joining data provide templates for the dashboard queries.

**Primary recommendation:** Restructure `/admin` dashboard template with sessions-first layout, add `/admin/settings` route for password change, implement client-side search/filter using vanilla JavaScript.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Use)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | - | Web framework | Already in use, Depends() for auth |
| Jinja2 | - | Template rendering | Already in use, established patterns |
| SQLAlchemy | - | ORM queries | Already in use, joinedload for sessions |
| pwdlib | - | Password hashing | Already in use, has hash_password() |

### Supporting (No New Dependencies Needed)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Vanilla JS | ES6+ | Client-side search | Dashboard search/filter - no framework needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vanilla JS | Alpine.js | Adds 15KB dependency for simple filter - not worth it |
| Client-side search | Server-side | Small dataset (teams/sessions) makes client-side simpler |

**Installation:**
```bash
# No new dependencies required
```

## Architecture Patterns

### Recommended Dashboard Structure
```
the55/app/
├── routers/
│   ├── admin.py          # Expand with dashboard + settings routes
│   └── auth.py           # Add password change endpoint
├── templates/admin/
│   ├── dashboard.html    # Redesigned sessions-first layout
│   └── settings.html     # New - password change form
└── static/js/
    └── dashboard.js      # New - client-side search/filter
```

### Pattern 1: Sessions-First Query
**What:** Query today's/current month's sessions prominently
**When to use:** Dashboard landing view
**Example:**
```python
# Source: Existing sessions.py patterns
from datetime import datetime
from sqlalchemy.orm import joinedload

def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.utcnow().strftime("%Y-%m")

# Dashboard query - sessions with team data
current_month = get_current_month()
active_sessions = db.query(Session).options(
    joinedload(Session.team)
).filter(
    Session.month == current_month,
    Session.state.in_([SessionState.DRAFT, SessionState.CAPTURING, SessionState.CLOSED])
).order_by(Session.created_at.desc()).all()
```

### Pattern 2: Password Change with Verification
**What:** Require current password before allowing change
**When to use:** Settings page password update
**Example:**
```python
# Source: Existing auth.py patterns
from app.services.auth import verify_password, hash_password

@router.post("/settings/password")
async def change_password(
    request: Request,
    settings: SettingsDep,
    db: DbDep,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    # Verify current password
    if not verify_password(current_password, settings.facilitator_password_hash):
        return templates.TemplateResponse(...)

    # Validate new password
    if new_password != confirm_password:
        return templates.TemplateResponse(...)

    # Hash and store - requires updating settings storage
    new_hash = hash_password(new_password)
    # Store new_hash (see implementation notes)
```

### Pattern 3: Client-Side Search Filter
**What:** Filter displayed items without server roundtrip
**When to use:** Team list and session list filtering
**Example:**
```javascript
// Source: Standard vanilla JS pattern
function filterItems(searchTerm) {
    const term = searchTerm.toLowerCase();
    const items = document.querySelectorAll('[data-searchable]');

    items.forEach(item => {
        const text = item.dataset.searchable.toLowerCase();
        item.style.display = text.includes(term) ? '' : 'none';
    });
}

// HTML pattern
<input type="search" id="search" placeholder="Search teams...">
<div class="team-card" data-searchable="Acme Corp Engineering">...</div>
```

### Anti-Patterns to Avoid
- **Server roundtrip for small filters:** With <100 teams/sessions, client-side is faster
- **Complex JS frameworks:** Vanilla JS is sufficient for search/filter
- **Storing password hash in session:** Store in .env or database, not in-memory

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | bcrypt/sha256 | pwdlib (Argon2) | Already in use, battle-tested |
| Date formatting | Custom strftime | Template filters | Jinja2 handles this well |
| Search highlighting | Regex replace | CSS class toggle | Simpler, no regex edge cases |
| Form validation | Custom JS | HTML5 required/pattern | Built-in validation works |

**Key insight:** The existing codebase has established patterns. Follow them rather than introducing new approaches.

## Common Pitfalls

### Pitfall 1: Password Storage Location
**What goes wrong:** Storing new password hash without persistence
**Why it happens:** Current hash is in environment variable (FACILITATOR_PASSWORD_HASH)
**How to avoid:** Either:
- Update .env file directly (requires file write permission)
- Store hash in database with a Settings table
- Document that password change requires restart
**Warning signs:** Testing password change but old password still works

### Pitfall 2: Empty State Handling
**What goes wrong:** Dashboard looks broken when no sessions exist
**Why it happens:** Only considering "has data" path
**How to avoid:** Design empty states first - "Create your first session" CTA
**Warning signs:** Blank sections, missing CTAs

### Pitfall 3: Search Performance with Large Lists
**What goes wrong:** Janky UI when filtering 100+ items
**Why it happens:** DOM manipulation without debouncing
**How to avoid:** Debounce search input (150ms), use CSS for visibility not DOM removal
**Warning signs:** Lag when typing in search field

### Pitfall 4: Sessions-First Complexity
**What goes wrong:** Complex query logic for "today's session" edge cases
**Why it happens:** Multiple time zones, sessions spanning days
**How to avoid:** Use current month as primary filter, not exact date. Sessions are monthly.
**Warning signs:** Wrong sessions appearing as "active"

## Code Examples

Verified patterns from existing codebase:

### Dashboard Data Query
```python
# Source: the55/app/routers/admin.py and sessions.py patterns
@router.get("")
async def admin_dashboard(request: Request, auth: AuthDep, db: DbDep):
    """Admin dashboard - sessions-first command center."""
    current_month = get_current_month()

    # Today's/active sessions (this month, not revealed)
    active_sessions = db.query(Session).options(
        joinedload(Session.team)
    ).filter(
        Session.month == current_month,
        Session.state != SessionState.REVEALED
    ).order_by(Session.created_at.desc()).all()

    # Recent sessions (last 5 revealed/completed)
    recent_sessions = db.query(Session).options(
        joinedload(Session.team)
    ).filter(
        Session.state == SessionState.REVEALED
    ).order_by(Session.revealed_at.desc()).limit(5).all()

    # All teams for quick access
    teams = db.query(Team).order_by(Team.company_name, Team.team_name).all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "active_sessions": active_sessions,
            "recent_sessions": recent_sessions,
            "teams": teams,
            "current_month": current_month
        }
    )
```

### Settings Page with Password Change
```python
# Source: Pattern from auth.py
@router.get("/settings")
async def settings_page(request: Request, auth: AuthDep):
    """Facilitator settings page."""
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "success": None, "error": None}
    )

@router.post("/settings/password")
async def change_password(
    request: Request,
    auth: AuthDep,
    settings: SettingsDep,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Process password change."""
    # Verify current password
    if not verify_password(current_password, settings.facilitator_password_hash):
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "error": "Current password is incorrect", "success": None}
        )

    # Validate new password
    if len(new_password) < 8:
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "error": "Password must be at least 8 characters", "success": None}
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "error": "Passwords do not match", "success": None}
        )

    # Generate new hash
    new_hash = hash_password(new_password)

    # Store new hash (implementation depends on storage strategy)
    # Option 1: Update .env file
    # Option 2: Add to database
    # Option 3: Print instructions to update manually

    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "success": "Password updated successfully", "error": None}
    )
```

### Client-Side Search JavaScript
```javascript
// Source: Standard vanilla JS pattern for dashboard
(function() {
    'use strict';

    const searchInput = document.getElementById('dashboard-search');
    if (!searchInput) return;

    let debounceTimer;

    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            filterItems(e.target.value);
        }, 150);
    });

    function filterItems(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        const items = document.querySelectorAll('[data-searchable]');
        let visibleCount = 0;

        items.forEach(item => {
            const searchText = item.dataset.searchable.toLowerCase();
            const isVisible = !term || searchText.includes(term);
            item.classList.toggle('hidden', !isVisible);
            if (isVisible) visibleCount++;
        });

        // Update empty state
        const emptyState = document.getElementById('search-empty-state');
        if (emptyState) {
            emptyState.classList.toggle('hidden', visibleCount > 0);
        }
    }
})();
```

### Dashboard HTML Structure
```html
<!-- Source: Based on existing dashboard.html patterns -->
{% extends "base.html" %}

{% block content %}
<div class="dashboard command-center">
    <!-- Active Sessions Section (Sessions-First) -->
    <section class="dashboard-section dashboard-section-primary">
        <div class="section-header">
            <h2>Active Sessions</h2>
            <span class="section-badge">{{ active_sessions | length }} this month</span>
        </div>

        {% if active_sessions %}
        <div class="session-cards">
            {% for session in active_sessions %}
            <a href="/admin/sessions/{{ session.id }}" class="card card-link session-card-active">
                <div class="session-team">{{ session.team.company_name }} - {{ session.team.team_name }}</div>
                <div class="session-month">{{ session.month }}</div>
                <span class="session-state state-{{ session.state.value }}">{{ session.state.value }}</span>
            </a>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <p>No active sessions this month.</p>
            <a href="#teams" class="btn btn-primary">Start a Session</a>
        </div>
        {% endif %}
    </section>

    <!-- Teams with One-Click Session -->
    <section class="dashboard-section" id="teams">
        <div class="section-header">
            <h2>Teams</h2>
            <input type="search" id="dashboard-search" placeholder="Search teams..." class="search-input">
        </div>

        <div class="team-grid">
            {% for team in teams %}
            <div class="team-card" data-searchable="{{ team.company_name }} {{ team.team_name }}">
                <div class="team-company">{{ team.company_name }}</div>
                <div class="team-name">{{ team.team_name }}</div>
                <div class="team-actions">
                    <a href="/admin/sessions/team/{{ team.id }}/create?month={{ current_month }}" class="btn btn-primary btn-small">New Session</a>
                    <a href="/admin/teams/{{ team.id }}" class="btn btn-ghost btn-small">Edit</a>
                </div>
            </div>
            {% endfor %}
        </div>
        <div id="search-empty-state" class="empty-state hidden">
            <p>No teams match your search.</p>
        </div>
    </section>

    <!-- Recent Activity -->
    <section class="dashboard-section">
        <div class="section-header">
            <h2>Recent Activity</h2>
            <a href="/admin/sessions/history" class="btn btn-ghost">View All</a>
        </div>

        {% if recent_sessions %}
        <div class="activity-list">
            {% for session in recent_sessions %}
            <a href="/admin/sessions/{{ session.id }}" class="activity-item">
                <span class="activity-icon">{{ session.state.value }}</span>
                <span class="activity-text">{{ session.team.team_name }} - {{ session.month }}</span>
            </a>
            {% endfor %}
        </div>
        {% else %}
        <p class="text-muted">No completed sessions yet.</p>
        {% endif %}
    </section>
</div>
{% endblock %}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Teams-first dashboard | Sessions-first layout | v2.2 | Matches facilitator mental model |
| No password change | Self-service settings | v2.2 | Reduces deployment friction |
| No search | Client-side filter | v2.2 | Scales to 50+ teams |

**Deprecated/outdated:**
- Current dashboard.html: Will be replaced with sessions-first layout

## Password Storage Strategy

**Critical implementation decision required:**

The current password hash is stored in environment variable `FACILITATOR_PASSWORD_HASH`. Three approaches for enabling self-service password change:

### Option A: .env File Update (Recommended for Single User)
**Pros:** Simple, matches current pattern
**Cons:** Requires file write permission, environment reload
**Implementation:**
```python
import os
from pathlib import Path

def update_env_password(new_hash: str) -> bool:
    """Update password hash in .env file."""
    env_path = Path(".env")
    if not env_path.exists():
        return False

    content = env_path.read_text()
    # Replace FACILITATOR_PASSWORD_HASH=... line
    import re
    new_content = re.sub(
        r'FACILITATOR_PASSWORD_HASH=.*',
        f'FACILITATOR_PASSWORD_HASH={new_hash}',
        content
    )
    env_path.write_text(new_content)
    return True
```

### Option B: Database Settings Table
**Pros:** Proper persistence, no file writes
**Cons:** Database migration, more complex
**Implementation:** Add `Settings` model with key-value storage

### Option C: Display Hash for Manual Update
**Pros:** Zero infrastructure change
**Cons:** Poor UX, requires restart
**Implementation:** Show new hash and instructions to update .env

**Recommendation:** Option A for v2.2 - single facilitator use case, minimal complexity.

## Open Questions

Things that couldn't be fully resolved:

1. **Password change persistence method**
   - What we know: Current hash in .env, pwdlib has hash_password()
   - What's unclear: Whether to update .env directly or use database
   - Recommendation: Use .env file update (Option A) - simplest for single-user

2. **Session activity definition**
   - What we know: Sessions have states (draft, capturing, closed, revealed)
   - What's unclear: What counts as "active" for dashboard display
   - Recommendation: Current month + not revealed = active session

3. **Navigation structure**
   - What we know: Current nav is minimal (just Logout link)
   - What's unclear: Whether to add persistent nav bar or keep minimal
   - Recommendation: Add minimal secondary nav (Dashboard | Settings | Logout)

## Sources

### Primary (HIGH confidence)
- `the55/app/routers/sessions.py` - Session query patterns, state management
- `the55/app/routers/admin.py` - Current dashboard implementation
- `the55/app/routers/auth.py` - Authentication patterns
- `the55/app/services/auth.py` - Password hash/verify functions
- `the55/app/db/models.py` - Session, Team model definitions
- `.planning/research/FEATURES-v22-UX.md` - Dashboard UX requirements

### Secondary (MEDIUM confidence)
- `the55/app/static/css/variables.css` - Design tokens (Phase 23)
- `the55/app/static/css/main.css` - Existing component patterns

### Tertiary (LOW confidence)
- None - all findings from codebase analysis

## Metadata

**Confidence breakdown:**
- Dashboard structure: HIGH - clear patterns in existing code
- Password change: HIGH - auth.py has all functions needed
- Search/filter: HIGH - standard vanilla JS pattern
- Password persistence: MEDIUM - .env update approach needs validation

**Research date:** 2026-01-21
**Valid until:** 2026-03-21 (90 days - stable codebase patterns)
