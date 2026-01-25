# Phase 27: Unified Meeting Screen - Research

**Researched:** 2026-01-21
**Domain:** Projectable UI, State Transitions, CSS Animations, Real-time Updates
**Confidence:** HIGH

## Summary

Phase 27 unifies the existing capture screen (`capture.html`) and presentation screen (`present.html`) into a single projectable meeting screen. This eliminates tab-switching during facilitated sessions and creates a seamless flow from response collection through synthesis reveal.

The existing codebase provides all necessary building blocks:
1. **Capture view** (Phase 21): QR code + participant status with 2.5s polling
2. **Presentation view** (Phase 22): Three-level synthesis display with 1/2/3 keyboard navigation
3. **Polling infrastructure** (`polling.js`): State-aware updates with auto-reload on state change
4. **Design system** (Phase 23): Premium tokens, Inter font, Apple-inspired palette

The key technical challenges are:
1. **State-driven layout**: Single template that renders differently based on session state
2. **Animated transitions**: Status collapse and synthesis reveal with "ceremony moment"
3. **Mode separation**: Clear visual distinction between capture and presentation modes
4. **Projector optimization**: Large fonts, high contrast, responsive to viewport

**Primary recommendation:** Create a new `/admin/sessions/{id}/meeting` endpoint with a unified template that combines capture and presentation components, using CSS grid for layout transformation and JavaScript for state-driven animations.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | existing | Endpoint routing | Project standard |
| Jinja2 | existing | Template rendering | Project standard |
| Vanilla JS | ES6+ | State management, animations | Project avoids frameworks |
| CSS Grid | native | Layout transformation | Browser-native, no dependencies |

### Supporting (Already in Project)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| CSS transitions | native | Smooth state changes | All animated elements |
| CSS @keyframes | native | Complex animations | Ceremony reveal moment |
| fetch API | native | Polling | Real-time status updates |

### No New Dependencies Required
This phase requires NO new libraries. All functionality builds on existing patterns.

## Architecture Patterns

### Recommended Endpoint Structure
```
/admin/sessions/{session_id}/meeting  -> Unified meeting screen (NEW)
/admin/sessions/{session_id}/status   -> JSON status endpoint (EXISTS)
/admin/sessions/{session_id}/capture  -> (DEPRECATED but keep for backwards compat)
/admin/sessions/{session_id}/present  -> (DEPRECATED but keep for backwards compat)
```

### Template Organization
```
app/templates/admin/sessions/
├── view.html          # Existing control panel (facilitator's laptop)
├── capture.html       # Deprecated (redirect to meeting)
├── present.html       # Deprecated (redirect to meeting)
├── meeting.html       # NEW: Unified meeting screen for projection
└── ...
```

### Pattern 1: State-Driven Template Rendering
**What:** Single template that shows different content based on session state
**When to use:** Unified views that need to handle multiple states
**Example:**
```html
<!-- Source: Unified meeting template pattern -->
<div class="meeting-screen meeting-{{ session.state.value }}"
     data-session-id="{{ session.id }}"
     data-state="{{ session.state.value }}">

    {% if session.state.value in ['draft', 'capturing'] %}
    <!-- CAPTURE MODE -->
    <div class="capture-section" id="capture-section">
        {% include "admin/sessions/_capture_content.html" %}
    </div>
    {% endif %}

    {% if session.state.value in ['closed', 'revealed'] %}
    <!-- SYNTHESIS SECTION (shown after all submit OR reveal) -->
    <div class="synthesis-section {% if session.state.value == 'revealed' %}revealed{% endif %}"
         id="synthesis-section">
        {% include "admin/sessions/_synthesis_content.html" %}
    </div>
    {% endif %}
</div>
```

### Pattern 2: CSS Grid Layout Transformation
**What:** Use CSS grid to animate layout changes without JavaScript
**When to use:** When sections need to expand/collapse smoothly
**Example:**
```css
/* Source: Modern CSS pattern for animated collapse */
.meeting-screen {
    display: grid;
    min-height: 100vh;
}

/* Capture mode: Two columns */
.meeting-capturing {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr auto;
}

/* All submitted: Status collapses */
.meeting-capturing.all-submitted .capture-section {
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.6s var(--ease-out);
}

/* Revealed mode: Full width synthesis */
.meeting-revealed {
    grid-template-columns: 1fr;
}
```

### Pattern 3: Ceremony Reveal Animation
**What:** Multi-step animation for synthesis reveal that builds anticipation
**When to use:** High-impact UI moments
**Example:**
```css
/* Source: Apple-style reveal pattern */
@keyframes ceremony-reveal {
    0% {
        opacity: 0;
        transform: translateY(40px) scale(0.95);
    }
    60% {
        opacity: 1;
        transform: translateY(-10px) scale(1.02);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.synthesis-section.revealing {
    animation: ceremony-reveal 0.8s var(--ease-out) forwards;
    animation-delay: 0.3s; /* Brief pause to build anticipation */
}
```

### Pattern 4: Mode-Aware Polling
**What:** Polling that adapts behavior based on current mode
**When to use:** When different states need different update behavior
**Example:**
```javascript
// Source: Extended polling.js pattern
async function pollMeetingStatus() {
    const data = await fetch(`/admin/sessions/${sessionId}/status`);
    const currentState = container.dataset.state;

    // Capture mode: Update member status
    if (currentState === 'capturing') {
        updateMemberStatus(data.members);
        updateProgressCounter(data.submitted_count, data.total_members);

        // All submitted: Trigger collapse animation
        if (data.submitted_count === data.total_members) {
            triggerStatusCollapse();
        }
    }

    // State changed: Trigger transition animation
    if (data.state !== currentState) {
        if (data.state === 'revealed') {
            triggerCeremonyReveal();
        } else {
            window.location.reload();
        }
    }
}
```

### Anti-Patterns to Avoid
- **Separate templates for each state:** Creates code duplication, inconsistent behavior
- **innerHTML replacement for transitions:** Causes flicker, loses animation state
- **Auto-collapsing status without facilitator control:** MS-5 pitfall - facilitator may want to reference who submitted
- **Showing admin controls on projected view:** MS-3 pitfall - reduces professional appearance
- **Jarring state transitions:** MS-2 pitfall - animate between states smoothly

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| QR code generation | Custom QR library | Existing `/admin/qr/team/{team_id}` | Already tested, 400px optimized |
| Status polling | New polling mechanism | Extend existing polling.js | 2.5s interval proven reliable |
| Dark theme | New CSS variables | Existing `.capture-mode` styles | Consistency with existing projector views |
| Keyboard shortcuts | Custom event system | Extend existing presentation.js | 1/2/3 already working |
| Synthesis data parsing | Custom JSON handling | Existing sessions.py logic | Error handling already implemented |

**Key insight:** This phase is primarily about COMBINING existing components with smooth transitions, not building new functionality.

## Common Pitfalls

### Pitfall 1: Mode Confusion (MS-1)
**What goes wrong:** Capture UI and presentation UI shown together; facilitator clicks wrong button
**Why it happens:** Single screen with all controls visible
**How to avoid:**
- Clear visual mode separation: different background colors for capture vs present
- Never show capture controls during presentation mode
- Use explicit state indicators in header
**Warning signs:** Participants see "Close Capture" button on projected display

### Pitfall 2: Jarring Transitions (MS-2)
**What goes wrong:** Screen jumps between states; facilitator loses orientation
**Why it happens:** Instant visibility changes without animation
**How to avoid:**
- CSS transitions for all state changes (0.3-0.6s duration)
- Content fades/slides, doesn't jump
- Consider brief pause before major transitions
**Warning signs:** Participants startled when synthesis appears

### Pitfall 3: Status Collapse Too Soon (MS-5)
**What goes wrong:** "All submitted" triggers immediate collapse; facilitator loses context
**Why it happens:** Auto-collapse based only on count
**How to avoid:**
- Show "All submitted" state but DON'T auto-collapse
- Provide facilitator button: "Continue to Reveal"
- Keep participant names visible until facilitator explicitly advances
**Warning signs:** Facilitator says "Wait, who submitted?"

### Pitfall 4: Anticlimactic Reveal (MS-6)
**What goes wrong:** Click "Reveal" and synthesis just appears; missed opportunity
**Why it happens:** Treating reveal like any other state change
**How to avoid:**
- Multi-step animation: brief anticipation pause, then elegant reveal
- Visual "curtain rise" effect
- Synthesis appears with gentle scale/fade animation
**Warning signs:** Reveal feels like a page load, not a moment

### Pitfall 5: Font Sizing for Projection (MS-7)
**What goes wrong:** Text readable on laptop is too small on projector
**Why it happens:** Testing only on development screen
**How to avoid:**
- Minimum 24px body text for projection
- Headings 48px+ for visibility from back of room
- Test from 20 feet away (or simulate)
**Warning signs:** Participants squinting at projected display

### Pitfall 6: Polling During Presentation (MS-9)
**What goes wrong:** Late submission update during synthesis reveal
**Why it happens:** Polling continues in all states
**How to avoid:**
- Stop polling when state becomes REVEALED
- Freeze display state during presentation mode
- Only facilitator device receives updates
**Warning signs:** Screen flickers during synthesis discussion

## Code Examples

Verified patterns from existing codebase:

### Existing Capture View Structure
```html
<!-- Source: /var/www/the55/app/templates/admin/sessions/capture.html -->
<div class="capture-control" data-session-id="{{ session.id }}">
    <div class="capture-container">
        <!-- QR Panel (left) -->
        <div class="capture-qr-panel">
            <img src="/admin/qr/team/{{ team.id }}" class="capture-qr-code">
            <div class="capture-join-code">{{ team.code }}</div>
        </div>
        <!-- Status Panel (right) -->
        <div class="capture-status-panel">
            <div class="capture-progress">
                <span id="submitted-count">{{ submitted_count }}</span>/<span id="total-members">{{ total_members }}</span>
            </div>
            <div class="capture-member-list" id="member-status-list">
                {% for member in member_status %}
                <div class="capture-member" data-member-id="{{ member.id }}">...</div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
```

### Existing Presentation View Structure
```html
<!-- Source: /var/www/the55/app/templates/admin/sessions/present.html -->
<div class="results-page">
    <div class="results-header">
        <h1>{{ team.team_name }}</h1>
        <p class="results-meta">{{ team.company_name }} &middot; {{ session.month }}</p>
    </div>

    <div class="card">
        <h2>What We Heard</h2>
        <p class="results-themes">{{ synthesis_themes }}</p>

        {% if synthesis_gap_type %}
        <h2>Suggested Gap</h2>
        <div class="results-gap">
            <span class="gap-badge gap-{{ synthesis_gap_type|lower }}">{{ synthesis_gap_type }}</span>
        </div>
        {% endif %}
    </div>

    {% if synthesis_statements %}
    <div class="card">
        <h2>Key Insights</h2>
        <ul class="results-insights">
            {% for stmt in synthesis_statements %}
            <li>{{ stmt.statement }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</div>
```

### Existing Polling Pattern
```javascript
// Source: /var/www/the55/static/js/polling.js
const POLL_INTERVAL = 2500; // 2.5 seconds

async function pollStatus() {
    const response = await fetch(`/admin/sessions/${sessionId}/status`);
    const data = await response.json();
    updateUI(data);

    // State change detection - triggers reload
    if (data.state !== 'capturing') {
        stopPolling();
        window.location.reload();
    }
}
```

### CSS Transition Variables
```css
/* Source: /var/www/the55/app/static/css/variables.css */
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--duration-fast: 150ms;
--duration-normal: 300ms;
--duration-slow: 500ms;
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate capture/present views | Unified meeting screen | Phase 27 | Single URL, no tab switching |
| Instant state changes | Animated transitions | Phase 27 | Professional presentation feel |
| Auto-reload on state change | In-page transitions | Phase 27 | No jarring page loads |
| Same font size laptop/projector | Projection-optimized sizes | Phase 27 | Readable from back of room |

**CSS Animation Best Practices (2025):**
- **CSS Grid `grid-template-rows: 0fr` to `1fr`** for smooth collapse/expand
- **`transition-behavior: allow-discrete`** for animating to/from `display: none`
- **`prefers-reduced-motion`** support for accessibility
- **GPU-accelerated properties** (transform, opacity) for 60fps

## Implementation Strategy

### Task Breakdown (Recommended)

**Wave 1: Foundation**
1. Create unified meeting endpoint and basic template structure
2. Implement state-driven rendering (capture vs presentation modes)
3. Add projector-optimized CSS (larger fonts, enhanced contrast)

**Wave 2: Transitions**
4. Implement status collapse animation (CSS grid transition)
5. Add ceremony reveal animation (multi-step keyframes)
6. Create transition triggers based on polling data

**Wave 3: Polish**
7. Integrate keyboard navigation (1/2/3 for levels)
8. Add facilitator controls (minimal, context-appropriate)
9. Handle edge cases (synthesis failure, late submissions)

### Key Template Sections

```html
<!-- Unified Meeting Template Structure -->
{% extends "base.html" %}
{% block body_class %} class="meeting-mode meeting-{{ session.state.value }}"{% endblock %}
{% block header %}{% endblock %}

{% block content %}
<div class="meeting-screen" data-session-id="{{ session.id }}" data-state="{{ session.state.value }}">

    <!-- CAPTURE SECTION: Visible in draft/capturing states -->
    {% if session.state.value in ['draft', 'capturing'] %}
    <section class="meeting-capture" id="capture-section">
        <!-- QR Panel -->
        <div class="meeting-qr">...</div>
        <!-- Status Panel -->
        <div class="meeting-status">...</div>
    </section>
    {% endif %}

    <!-- TRANSITION OVERLAY: Brief "preparing" state -->
    <div class="meeting-transition" id="transition-overlay" hidden>
        <div class="transition-message">Preparing synthesis...</div>
    </div>

    <!-- SYNTHESIS SECTION: Visible in revealed state -->
    {% if session.state.value == 'revealed' or synthesis_themes %}
    <section class="meeting-synthesis {% if session.state.value == 'revealed' %}active{% endif %}"
             id="synthesis-section">
        <!-- Level tabs -->
        <div class="level-tabs">...</div>
        <!-- Level 1: Themes -->
        <div class="level-content" data-level="1">...</div>
        <!-- Level 2: Insights -->
        <div class="level-content" data-level="2">...</div>
        <!-- Level 3: Raw -->
        <div class="level-content" data-level="3">...</div>
    </section>
    {% endif %}

    <!-- Footer: Minimal, context-aware -->
    <footer class="meeting-footer">
        <span class="keyboard-hint">Press 1, 2, 3 for detail levels</span>
        <a href="/admin/sessions/{{ session.id }}" class="exit-meeting">Exit to Control Panel</a>
    </footer>
</div>
{% endblock %}
```

### CSS Architecture

```css
/* Meeting Mode - Base */
.meeting-mode {
    background: #1a1a2e;  /* Match existing capture-mode */
    color: #eaeaea;
    min-height: 100vh;
}

.meeting-screen {
    display: grid;
    min-height: 100vh;
    transition: grid-template-rows 0.6s var(--ease-out);
}

/* Capture State: Two-column layout */
.meeting-capturing .meeting-screen {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr auto;
}

/* Revealed State: Full-width synthesis */
.meeting-revealed .meeting-screen {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
}

/* Status Collapse Animation */
.meeting-status.collapsing {
    grid-template-rows: 0fr;
    overflow: hidden;
    transition: grid-template-rows 0.6s var(--ease-out);
}

/* Ceremony Reveal */
@keyframes ceremony-reveal {
    0% { opacity: 0; transform: translateY(60px) scale(0.9); }
    60% { opacity: 1; transform: translateY(-15px) scale(1.02); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

.meeting-synthesis.revealing {
    animation: ceremony-reveal 1s var(--ease-out) forwards;
}

/* Projector-Optimized Typography */
.meeting-mode h1 {
    font-size: clamp(3rem, 5vw, 4rem);  /* 48-64px */
    letter-spacing: var(--tracking-tight);
}

.meeting-mode h2 {
    font-size: clamp(2rem, 3.5vw, 2.5rem);  /* 32-40px */
}

.meeting-mode p,
.meeting-mode li {
    font-size: clamp(1.5rem, 2.5vw, 2rem);  /* 24-32px */
    line-height: 1.6;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    .meeting-synthesis.revealing {
        animation: none;
        opacity: 1;
        transform: none;
    }
}
```

### JavaScript Architecture

```javascript
// meeting.js - Unified meeting screen controller
(function() {
    'use strict';

    const POLL_INTERVAL = 2500;
    let currentState = null;
    let pollTimer = null;

    const container = document.querySelector('.meeting-screen');
    if (!container) return;

    const sessionId = container.dataset.sessionId;
    currentState = container.dataset.state;

    // State handlers
    const stateHandlers = {
        capturing: handleCapturingState,
        closed: handleClosedState,
        revealed: handleRevealedState
    };

    async function pollMeetingStatus() {
        const response = await fetch(`/admin/sessions/${sessionId}/status`);
        const data = await response.json();

        // State-specific updates
        if (stateHandlers[currentState]) {
            stateHandlers[currentState](data);
        }

        // State transition detection
        if (data.state !== currentState) {
            handleStateTransition(currentState, data.state, data);
        }
    }

    function handleCapturingState(data) {
        updateMemberStatus(data.members);
        updateProgressCounter(data.submitted_count, data.total_members);

        // All submitted - show "ready to reveal" state
        if (data.submitted_count === data.total_members) {
            showAllSubmittedState();
        }
    }

    function handleStateTransition(fromState, toState, data) {
        if (toState === 'revealed') {
            triggerCeremonyReveal();
        } else {
            // Other transitions: reload to get fresh template
            window.location.reload();
        }
    }

    function triggerCeremonyReveal() {
        stopPolling();

        // Collapse capture section
        const captureSection = document.getElementById('capture-section');
        if (captureSection) {
            captureSection.classList.add('collapsing');
        }

        // Show transition overlay briefly
        const overlay = document.getElementById('transition-overlay');
        if (overlay) {
            overlay.hidden = false;
        }

        // Reveal synthesis after brief pause
        setTimeout(() => {
            if (overlay) overlay.hidden = true;

            const synthesisSection = document.getElementById('synthesis-section');
            if (synthesisSection) {
                synthesisSection.classList.add('revealing');
                synthesisSection.classList.add('active');
            }

            currentState = 'revealed';
            container.dataset.state = 'revealed';
        }, 600); // Match collapse animation duration
    }

    // Keyboard navigation (reuse from presentation.js)
    document.addEventListener('keydown', function(e) {
        if (currentState !== 'revealed') return;
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.key === '1' || e.key === '2' || e.key === '3') {
            e.preventDefault();
            showLevel(parseInt(e.key, 10));
        }
    });

    // Start polling in capturing/closed states
    if (currentState === 'capturing' || currentState === 'closed') {
        pollTimer = setInterval(pollMeetingStatus, POLL_INTERVAL);
    }

    window.addEventListener('beforeunload', stopPolling);
})();
```

## Open Questions

Things that couldn't be fully resolved:

1. **Facilitator Control Visibility**
   - What we know: MS-3 says hide controls from projected view
   - What's unclear: Should meeting screen have ANY controls, or purely view-only?
   - Recommendation: Meeting screen is view-only. Facilitator uses separate tab (view.html) for controls. Add clear guidance: "Control from your laptop, project this screen."

2. **All-Submitted Behavior**
   - What we know: MS-5 warns against auto-collapse
   - What's unclear: What triggers the transition to synthesis?
   - Recommendation: When all submit, show "All responses received" message but keep status visible. Facilitator clicks "Generate Synthesis" in control panel, then "Reveal". Synthesis appears on meeting screen when revealed.

3. **Multi-Device Control (MS-10)**
   - What we know: Facilitator may want phone control while projecting from laptop
   - What's unclear: Scope for Phase 27 - is this required?
   - Recommendation: DEFER to Phase 28. For Phase 27, single-device model: laptop has both meeting screen (project) and control panel (different tab).

4. **Backwards Compatibility**
   - What we know: `/capture` and `/present` endpoints exist
   - What's unclear: Keep them or redirect to `/meeting`?
   - Recommendation: Keep existing endpoints functional (don't break bookmarks) but add `/meeting` as the primary view. Update view.html links to point to `/meeting`.

## Sources

### Primary (HIGH confidence)
- `/var/www/the55/app/templates/admin/sessions/capture.html` - Current capture template
- `/var/www/the55/app/templates/admin/sessions/present.html` - Current presentation template
- `/var/www/the55/app/routers/sessions.py` - Session endpoints, data queries
- `/var/www/the55/app/static/js/polling.js` - Polling implementation
- `/var/www/the55/app/static/css/main.css` - Capture/presentation styles (lines 1880-2012)
- `/var/www/the55/app/static/css/variables.css` - Design tokens, animation variables
- `/var/www/.planning/research/PITFALLS.md` - MS-1 through MS-10 pitfalls
- `/var/www/.planning/research/FEATURES-v22-UX.md` - Meeting screen differentiators

### Secondary (MEDIUM confidence)
- CSS-Tricks: Using CSS Transitions on Auto Dimensions
- Chrome Developers Blog: Building performant expand & collapse animations
- Web search: CSS ceremony reveal animations, progressive disclosure

### Tertiary (LOW confidence)
- None - all findings verified with codebase analysis

## Metadata

**Confidence breakdown:**
- Existing architecture: HIGH - Comprehensive codebase analysis
- Animation patterns: HIGH - CSS standard, tested approaches
- State management: HIGH - Extends proven polling.js pattern
- Pitfall prevention: HIGH - Documented MS-* pitfalls guide design

**Research date:** 2026-01-21
**Valid until:** 2026-02-21 (30 days - stable codebase, standard CSS patterns)
