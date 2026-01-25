# Phase 22: Synthesis Presentation - Research

**Researched:** 2026-01-19
**Domain:** Presentation UI, Keyboard Navigation, Data Transformation, Synthesis Reliability
**Confidence:** HIGH

## Summary

This phase enhances the existing presentation mode with three distinct view levels and fixes synthesis reliability issues. Research examined the current codebase to understand:

1. **Synthesis data structure** - Already stored: themes (text), statements (JSON array of {statement, participants[]}), gap_type (string). No schema changes needed.
2. **Presentation template** - exists at `present.html`, currently shows a single-level view of synthesis.
3. **Synthesis failure cause** - The "Synthesis generation failed" message is stored when Claude API errors occur or JSON parsing fails (line 154 of synthesis.py).
4. **Level 2 data requirement** - Requires grouping similar statements. Currently, statements are already attributed - Level 2 just needs UI grouping, not new AI processing.
5. **Level 3 data requirement** - Raw responses exist in the Response table - can be queried directly (no AI involved).

**Primary recommendation:** Enhance `present.html` with three tabbed sections using vanilla JS keyboard listener. Add retry logic for synthesis failures with better error messaging. Add three level-specific export endpoints.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.109+ | Web framework | Already in use |
| Jinja2 | 3.1+ | Templates | Already in use |
| Vanilla JS | ES6+ | Keyboard navigation | Project decision: no build step |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| anthropic | 0.45+ | Claude API client | Already configured |
| Pydantic | 2.x | Schema validation | Already validating SynthesisOutput |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vanilla JS keyboard | AlpineJS | Adds dependency, project uses vanilla JS |
| Server-side level switching | Client-side tabs | Server-side adds latency, client-side is instant |

**Installation:**
No new packages required.

## Architecture Patterns

### Current Data Flow
```
Response (raw) --> Claude API --> Session (synthesis_themes, synthesis_statements, synthesis_gap_type)
                                      |
                                      v
                              present.html (single view)
```

### Proposed Data Flow
```
Response (raw) -----> Level 3: Raw statements per person (no AI)
                |
                v
synthesis_statements --> Level 2: Attributed grouped insights (UI grouping)
                |
                v
synthesis_themes --> Level 1: High-level themes (AI synthesis)
```

### Recommended Project Structure
```
app/
├── routers/
│   └── sessions.py     # Add level-specific export endpoints
├── templates/
│   └── admin/sessions/
│       └── present.html  # Enhance with three levels + keyboard nav
└── static/
    └── js/
        └── presentation.js  # New: keyboard navigation handler
```

### Pattern 1: Keyboard Navigation
**What:** Listen for keydown events on 1/2/3 keys to switch views
**When to use:** Presentation mode with discrete view levels
**Example:**
```javascript
// Vanilla JS keyboard listener for presentation levels
document.addEventListener('keydown', function(e) {
    if (e.key === '1' || e.key === '2' || e.key === '3') {
        const level = parseInt(e.key);
        showLevel(level);
    }
});

function showLevel(level) {
    // Hide all levels
    document.querySelectorAll('.level-content').forEach(el => {
        el.classList.remove('active');
    });
    // Show selected level
    document.querySelector(`[data-level="${level}"]`).classList.add('active');
    // Update level indicator
    updateLevelIndicator(level);
}
```

### Pattern 2: Tab-Style Level Switching
**What:** Visual tab buttons that also respond to keyboard
**When to use:** Multi-view presentations
**Example:**
```html
<div class="level-tabs">
    <button class="level-tab active" data-level="1" aria-selected="true">Themes</button>
    <button class="level-tab" data-level="2" aria-selected="false">Insights</button>
    <button class="level-tab" data-level="3" aria-selected="false">Raw</button>
</div>
<div class="level-content active" data-level="1">...</div>
<div class="level-content" data-level="2">...</div>
<div class="level-content" data-level="3">...</div>
```

### Anti-Patterns to Avoid
- **Separate routes per level:** Would reload page on level switch, disrupting presentation flow
- **New Claude call for Level 2:** Already have statements - just need UI grouping
- **localStorage for level state:** Levels should reset on page load for fresh presentations

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Keyboard shortcuts | Custom event system | Standard keydown listener | Well-understood, no edge cases |
| Tab switching | Full framework | CSS class toggling | Simple show/hide suffices |
| JSON export | Custom serializer | JSONResponse with Content-Disposition | FastAPI handles encoding |

**Key insight:** The three-level display is primarily UI work - the data already exists in appropriate forms.

## Common Pitfalls

### Pitfall 1: Synthesis Timeout
**What goes wrong:** Claude API takes >30 seconds, request times out
**Why it happens:** Large responses or Claude latency
**How to avoid:** Already using BackgroundTasks + polling pattern - synthesis runs async
**Warning signs:** "Synthesis generation failed" appearing consistently

### Pitfall 2: JSON Parsing Errors
**What goes wrong:** Claude returns malformed JSON, synthesis fails
**Why it happens:** Claude occasionally wraps JSON in markdown code blocks
**Current handling:** Code already strips ```json and ``` wrappers (lines 134-137 of synthesis.py)
**How to avoid:** Keep the existing parser logic; it handles common cases

### Pitfall 3: Keyboard Event Conflicts
**What goes wrong:** Number keys trigger browser or OS shortcuts
**Why it happens:** Some browsers use number keys for tab switching
**How to avoid:** Only listen on presentation page; use `e.preventDefault()` if key matches
**Warning signs:** Level doesn't change on keypress

### Pitfall 4: Empty Synthesis Display
**What goes wrong:** Presentation page shows empty content
**Why it happens:** Session accessed before REVEALED state, or synthesis generation failed
**Current handling:** Redirect to session view if not REVEALED (line 472-473 of sessions.py)
**How to avoid:** Keep redirect; enhance with error message for failed synthesis

## Code Examples

Verified patterns from the existing codebase:

### Current Synthesis Data Retrieval
```python
# From sessions.py line 476-481
synthesis_statements = None
if session.synthesis_statements:
    try:
        synthesis_statements = json.loads(session.synthesis_statements)
    except (json.JSONDecodeError, TypeError):
        synthesis_statements = []
```

### Current Presentation Template Structure
```html
<!-- From present.html -->
<div class="presentation-container">
    <div class="presentation-header">...</div>
    {% if synthesis_themes %}
    <div class="presentation-section">
        <h2 class="presentation-label">What We Heard</h2>
        <p class="presentation-themes">{{ synthesis_themes }}</p>
    </div>
    {% endif %}
    <!-- ... more sections ... -->
</div>
```

### Response Query for Level 3 (Raw Data)
```python
# Pattern from sessions.py export endpoint (lines 504-515)
responses = db.query(Response).filter(Response.session_id == session_id).all()
response_data = []
for r in responses:
    member = db.query(Member).filter(Member.id == r.member_id).first()
    response_data.append({
        "participant": member.name if member else "Unknown",
        "image_number": r.image_number,
        "bullets": json.loads(r.bullets) if r.bullets else [],
        "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None
    })
```

### Synthesis Retry Logic Trigger
```python
# From sessions.py lines 324-331 - already supports retry
if session.synthesis_themes is not None:
    # If it's an error message, allow retry
    if "failed" not in session.synthesis_themes.lower() and "insufficient" not in session.synthesis_themes.lower():
        # Already have valid synthesis, just redirect
        return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)
# Proceed to regenerate...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single presentation view | Single presentation view | Phase 16 | Works but lacks depth |
| No retry on failure | Implicit retry support | Phase 15 | Retry via re-trigger |

**Deprecated/outdated:**
- None for this phase

## Data Structure Analysis

### Existing Session Synthesis Fields
```python
# From models.py
synthesis_themes = Column(Text, nullable=True)     # Level 1: AI themes
synthesis_statements = Column(Text, nullable=True)  # Level 2: JSON [{statement, participants}]
synthesis_gap_type = Column(String(50), nullable=True)  # Gap diagnosis
```

### Level 1 Data (Themes)
- Source: `session.synthesis_themes`
- Format: Free text (2-4 sentences)
- Contains: High-level summary of team experience

### Level 2 Data (Attributed Insights)
- Source: `session.synthesis_statements`
- Format: JSON array of `{statement: string, participants: string[]}`
- Contains: Specific insights with attribution
- Note: Already grouped by the AI - just need display

### Level 3 Data (Raw Statements)
- Source: `Response` table
- Format: Per-participant bullets
- Contains: Unprocessed participant input
- Query: `db.query(Response).filter(Response.session_id == session_id).all()`

### Export Endpoints Design
```
GET /admin/sessions/{session_id}/export/level1  -> themes + gap_type
GET /admin/sessions/{session_id}/export/level2  -> statements array
GET /admin/sessions/{session_id}/export/level3  -> raw responses
```

## Synthesis Reliability (SYNTH-04, SYNTH-05)

### Current Failure Points
1. **Claude API error** - Network issues, rate limits
2. **JSON parse error** - Invalid response format
3. **Insufficient responses** - Less than 3 participants

### Current Error Handling
```python
# synthesis.py lines 150-161
except Exception as e:
    print(f"Synthesis error for session {session_id}: {e}")
    try:
        session.synthesis_themes = "Synthesis generation failed. Please try again."
        session.synthesis_statements = "[]"
        session.synthesis_gap_type = None
        db.commit()
```

### Recommended Improvements
1. **Explicit error type in UI** - Show "API Error" vs "Parse Error" vs "Insufficient Data"
2. **Retry button in presentation** - Allow retry without returning to session view
3. **Better JSON extraction** - Handle more edge cases in response parsing

### Reliability Pattern
The current async pattern (BackgroundTasks + polling) is sound:
1. Facilitator triggers synthesis
2. Task runs in background
3. UI polls for completion
4. Result stored in database

No architectural changes needed - just better error messaging.

## Open Questions

Things that couldn't be fully resolved:

1. **Level 2 grouping logic**
   - What we know: Statements are already attributed
   - What's unclear: Should Level 2 cluster similar statements visually?
   - Recommendation: Display as-is initially; clustering is future enhancement

2. **Keyboard hint visibility**
   - What we know: Users need to know 1/2/3 keys work
   - What's unclear: Permanent hint vs first-time hint
   - Recommendation: Small persistent hint in footer

## Sources

### Primary (HIGH confidence)
- `/var/www/the55/app/services/synthesis.py` - Synthesis generation logic
- `/var/www/the55/app/routers/sessions.py` - Presentation endpoint, export endpoint
- `/var/www/the55/app/templates/admin/sessions/present.html` - Current template
- `/var/www/the55/app/db/models.py` - Data structure
- `/var/www/the55/app/schemas/__init__.py` - Pydantic schemas
- `/var/www/the55/app/static/css/main.css` - Presentation styles

### Secondary (MEDIUM confidence)
- STATE.md decisions: "Standard messages API with JSON prompt (not beta structured outputs)"
- STATE.md decisions: "Polling for synthesis completion (reuse existing pattern, auto-reload on complete)"

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All components exist in codebase
- Architecture: HIGH - Follows existing patterns
- Data structure: HIGH - Verified from models.py and sessions.py
- Pitfalls: MEDIUM - Based on code analysis, not production observation

**Research date:** 2026-01-19
**Valid until:** No expiry - internal codebase analysis
