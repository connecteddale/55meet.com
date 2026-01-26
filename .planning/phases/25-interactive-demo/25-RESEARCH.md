# Phase 25: Interactive Demo - Research

**Researched:** 2026-01-27
**Domain:** Interactive product demos, FastAPI server-rendered flow, View Transitions
**Confidence:** HIGH

## Summary

This research investigates how to implement a compelling interactive demo for The 55 that lets visitors experience the complete flow: ClearBrief context, Signal Capture, team responses, and synthesis reveal. The demo must reuse existing UI patterns (image browser, synthesis display, View Transitions) while operating in a stateless, pre-baked mode without database writes.

The existing codebase provides excellent foundations: a working image browser with seeded randomization, synthesis display templates, and View Transitions CSS. The demo needs a parallel route structure (`/demo/*`) that mirrors the real participant flow but uses in-memory/sessionStorage state and pre-baked content.

Key technical decisions: Use sessionStorage for visitor response state (survives refresh, tab-isolated), seed the demo's image shuffle with a timestamp-based value for variety, and structure the demo as a linear wizard flow with 5-6 steps matching the "4-8 steps ideal" UX guideline.

**Primary recommendation:** Create a dedicated `/demo` route with a linear flow (intro > context > signal-capture > team-responses > synthesis > CTA), reusing existing templates with minimal modifications and storing visitor state in sessionStorage.

## Standard Stack

### Core (Existing - Reuse)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | existing | Route handling | Already in use |
| Jinja2 | existing | Server-side templates | Already in use |
| Vanilla JS | N/A | Client-side interactions | No framework needed |
| View Transitions API | CSS-based | Page transitions | Already implemented |

### Supporting (Existing - Reuse)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sessionStorage | Browser API | Visitor state persistence | Store image selection + bullets |
| CSS Custom Properties | existing | Design system | Consistent styling |
| Inter font | existing | Typography | Brand consistency |

### New Additions (Minimal)
| Library | Version | Purpose | Why Needed |
|---------|---------|---------|------------|
| None | N/A | N/A | All requirements met by existing stack |

**Installation:**
No new dependencies required.

## Architecture Patterns

### Recommended Route Structure
```
/demo                     # Entry point - intro/context
/demo/signal              # Signal Capture experience (image browser)
/demo/responses           # Show visitor + team responses
/demo/synthesis           # Reveal synthesis + CTA
```

### Recommended File Structure
```
templates/
  demo/
    intro.html            # ClearBrief context, team intro, "experience Signal Capture" tease
    signal.html           # Image browser (adapted from participant/respond.html)
    responses.html        # Visitor response + 4 pre-baked team responses
    synthesis.html        # Pre-baked synthesis + CTA

app/
  routers/
    demo.py               # Demo routes (no DB writes, pre-baked content)

static/
  css/
    demo.css              # Demo-specific styles (minimal additions)
  images/
    demo/                 # Pre-selected images for team responses (4 images)
```

### Pattern 1: Linear Wizard Flow
**What:** Demo progresses through fixed steps, no branching, visitor can only move forward
**When to use:** Product demos where you control the narrative
**Example:**
```python
# app/routers/demo.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/demo", tags=["demo"])
templates = Jinja2Templates(directory="templates")

# Pre-baked demo data
DEMO_COMPANY = {
    "name": "ClearBrief",
    "industry": "Legal Tech SaaS",
    "revenue": "$65M ARR",
    "strategy": "Help law firms win clients through transparency — open billing, open matters, no surprises."
}

TEAM_NAME_POOL = [
    "Sarah Chen", "Sarah Martinez", "Sarah Williams",
    "James Park", "James Thompson", "James Rivera",
    "Michael Lee", "Michael Johnson", "Michael Okafor",
    "Rachel Kim", "Rachel Garcia", "Rachel Patel"
]

DEMO_TEAM_ROLES = ["CTO", "CFO", "VP Sales", "COO"]

@router.get("", response_class=HTMLResponse)
async def demo_intro(request: Request):
    """Demo entry point - company context and team intro."""
    # Shuffle names using timestamp for variety
    import random
    import time
    seed = int(time.time()) // 3600  # Changes hourly
    rng = random.Random(seed)

    # Pick one name per role from corresponding pool section
    team_members = []
    for i, role in enumerate(DEMO_TEAM_ROLES):
        name = rng.choice(TEAM_NAME_POOL[i*3:(i+1)*3])
        team_members.append({"name": name, "role": role})

    return templates.TemplateResponse(
        "demo/intro.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_members": team_members,
            "seed": seed  # Pass to client for consistent experience
        }
    )
```

### Pattern 2: SessionStorage State Management
**What:** Store visitor's demo response (image selection + bullets) in sessionStorage
**When to use:** Temporary state that survives page refresh but is tab-isolated
**Why:** No database writes, frictionless, works offline after initial load
**Example:**
```javascript
// Demo state management
const DEMO_STATE_KEY = 'demo-response';

function saveDemoState(imageId, imageUrl, bullets) {
    sessionStorage.setItem(DEMO_STATE_KEY, JSON.stringify({
        imageId,
        imageUrl,
        bullets,
        timestamp: Date.now()
    }));
}

function loadDemoState() {
    try {
        const saved = sessionStorage.getItem(DEMO_STATE_KEY);
        return saved ? JSON.parse(saved) : null;
    } catch (e) {
        return null;
    }
}

function clearDemoState() {
    sessionStorage.removeItem(DEMO_STATE_KEY);
}
```

### Pattern 3: View Transitions Between Demo Steps
**What:** Use existing View Transitions CSS with programmatic navigation
**When to use:** Moving between demo steps for smooth, app-like feel
**Example:**
```javascript
// Wrap navigation in View Transition
function navigateWithTransition(url) {
    if (document.startViewTransition) {
        document.startViewTransition(() => {
            window.location.href = url;
        });
    } else {
        window.location.href = url;
    }
}
```

### Pattern 4: Seeded Name Shuffling
**What:** Shuffle team names deterministically so they're consistent during a visit
**When to use:** DEMO-06 requires names shuffled on each visit
**Example:**
```python
def get_shuffled_team(seed: int) -> list:
    """Generate consistent team for a demo session."""
    import random
    rng = random.Random(seed)

    # Name pools per role (3 options each)
    name_pools = {
        "CTO": ["Sarah Chen", "Sarah Martinez", "Sarah Williams"],
        "CFO": ["James Park", "James Thompson", "James Rivera"],
        "VP Sales": ["Michael Lee", "Michael Johnson", "Michael Okafor"],
        "COO": ["Rachel Kim", "Rachel Garcia", "Rachel Patel"]
    }

    team = []
    for role, names in name_pools.items():
        team.append({
            "name": rng.choice(names),
            "role": role
        })

    # Optionally shuffle order too
    rng.shuffle(team)
    return team
```

### Anti-Patterns to Avoid
- **Database writes in demo:** Demo must be stateless - no Response, Session, or Team records
- **Sharing real session logic:** Create parallel templates, don't modify production ones
- **Complex state machines:** Demo is linear, don't over-engineer state transitions
- **Heavy client-side frameworks:** Vanilla JS + sessionStorage is sufficient

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image browser UI | New image grid component | Existing `respond.html` pattern | Already tested, responsive, accessible |
| Synthesis display | New synthesis layout | Existing `synthesis.html` template | Matches real app exactly |
| View Transitions | Custom animations | Existing `transitions.css` | Already working with fallbacks |
| Seeded randomization | Custom PRNG | Python `random.Random(seed)` | Deterministic, well-tested |
| State persistence | Custom solution | sessionStorage API | Browser-native, tab-isolated |

**Key insight:** The demo is primarily a curation exercise - selecting pre-baked content and arranging it in a compelling flow. Nearly all UI components already exist.

## Common Pitfalls

### Pitfall 1: Demo Database Leaks
**What goes wrong:** Demo creates real database records, polluting production data
**Why it happens:** Reusing participant routes directly instead of creating parallel demo routes
**How to avoid:** Create dedicated `/demo/*` routes that never touch the database
**Warning signs:** Any `db.add()` or `db.commit()` in demo router

### Pitfall 2: Broken State on Browser Back
**What goes wrong:** Visitor uses browser back button, demo state becomes inconsistent
**Why it happens:** sessionStorage persists but server doesn't know visitor went back
**How to avoid:**
1. Each demo page reads state from sessionStorage on load
2. Redirect if state is missing (send back to beginning)
3. Consider disabling browser back or showing "restart demo" prompt
**Warning signs:** "undefined" appearing in template, missing image preview

### Pitfall 3: Image Mismatch in Team Responses
**What goes wrong:** Pre-baked team response images don't match Signal Capture browser images
**Why it happens:** Demo images not included in main image library, or IDs not matching
**How to avoid:**
1. Use 4 specific images from the existing library for team responses
2. Store team response images by filename, not opaque ID
3. Or add demo-specific images to `/static/images/demo/`
**Warning signs:** 404 errors on team response images

### Pitfall 4: Synthesis Doesn't Feel Real
**What goes wrong:** Pre-baked synthesis reads as generic marketing copy
**Why it happens:** Not written from perspective of actual tool output
**How to avoid:**
1. Write synthesis in exact format real AI would produce
2. Include specific attributions to team members
3. Reference their image choices explicitly
4. Match the three-level structure: themes, attributed insights, gap type
**Warning signs:** User feedback that demo feels "fake" or "salesy"

### Pitfall 5: Demo Completion Without CTA
**What goes wrong:** Visitor finishes demo but doesn't know what to do next
**Why it happens:** Weak or missing call-to-action at synthesis reveal
**How to avoid:**
1. Prominent CTA button at synthesis conclusion
2. Clear value proposition reminder
3. Multiple options: "Book a Session" (primary), "Learn More" (secondary)
**Warning signs:** High demo completion rate but low conversion

### Pitfall 6: Name Shuffling Too Random
**What goes wrong:** Same names appear multiple times, or names feel unnatural
**Why it happens:** Poor name pool design or insufficient variety
**How to avoid:**
1. Design name pools with cultural diversity
2. First names should match role stereotypes (Sarah=tech, James=finance, etc.)
3. Each pool has exactly 3 options, one per common surname type
4. Verify no duplicate first-last combinations across team
**Warning signs:** "Michael Kim, Michael Garcia, Michael Lee" on same team

## Code Examples

### Demo Route Handler with Seeded Team
```python
# Source: Adapted from existing participant.py patterns
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import random
import time

router = APIRouter(prefix="/demo", tags=["demo"])
templates = Jinja2Templates(directory="templates")

# Pre-baked demo content
DEMO_COMPANY = {
    "name": "ClearBrief",
    "industry": "Legal Tech SaaS",
    "revenue": "$65M ARR",
    "strategy": "Help law firms win clients through transparency — open billing, open matters, no surprises."
}

# Pre-baked team responses (image IDs from existing library)
DEMO_RESPONSES = [
    {
        "role": "CTO",
        "image_id": "tangled_cables_001",  # Use actual ID from library
        "image_url": "/static/images/library/reducedlive/tangled-cables.jpg",
        "bullets": [
            "We're building features but product and sales aren't synced on what clients actually need first"
        ]
    },
    {
        "role": "CFO",
        "image_id": "relay_handoff_002",
        "image_url": "/static/images/library/reducedlive/relay-handoff.jpg",
        "bullets": [
            "Projects start strong but stall at the handoff between dev and client success"
        ]
    },
    {
        "role": "VP Sales",
        "image_id": "broken_bridge_003",
        "image_url": "/static/images/library/reducedlive/broken-bridge.jpg",
        "bullets": [
            "I'm selling capabilities we don't have yet while engineering builds things nobody asked for"
        ]
    },
    {
        "role": "COO",
        "image_id": "puzzle_pieces_004",
        "image_url": "/static/images/library/reducedlive/puzzle-pieces.jpg",
        "bullets": [
            "Everyone's working hard but the pieces aren't connecting"
        ]
    }
]

DEMO_SYNTHESIS = {
    "themes": "Your team is aligned on WHERE you're going, but the WORK isn't fitting together. The drag is in the handoffs — particularly between product development and client-facing teams. Each function is executing independently, creating gaps where value should compound.",
    "statements": [
        {
            "statement": "Product development and client-facing teams are operating on different timelines",
            "participants": ["Sarah", "Michael"]
        },
        {
            "statement": "Features are being built without clear alignment to client priorities",
            "participants": ["Sarah", "James"]
        },
        {
            "statement": "Handoffs between departments are where momentum is lost",
            "participants": ["James", "Rachel"]
        }
    ],
    "gap_type": "Alignment"
}

def get_demo_seed(request: Request) -> int:
    """Get consistent seed for this demo session (from query or generate)."""
    # Try to get from query param first
    seed_param = request.query_params.get("seed")
    if seed_param:
        try:
            return int(seed_param)
        except ValueError:
            pass
    # Generate hourly-changing seed
    return int(time.time()) // 3600

def get_shuffled_team(seed: int) -> list:
    """Generate team with shuffled names."""
    rng = random.Random(seed)

    name_pools = {
        "CTO": ["Sarah Chen", "Sarah Martinez", "Sarah Williams"],
        "CFO": ["James Park", "James Thompson", "James Rivera"],
        "VP Sales": ["Michael Lee", "Michael Johnson", "Michael Okafor"],
        "COO": ["Rachel Kim", "Rachel Garcia", "Rachel Patel"]
    }

    team = []
    for role, names in name_pools.items():
        team.append({
            "name": rng.choice(names),
            "role": role,
            "first_name": rng.choice(names).split()[0]  # For synthesis attribution
        })
    return team

@router.get("", response_class=HTMLResponse)
async def demo_intro(request: Request):
    """Demo landing - company context and Signal Capture tease."""
    seed = get_demo_seed(request)
    team = get_shuffled_team(seed)

    return templates.TemplateResponse(
        "demo/intro.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_members": team,
            "seed": seed
        }
    )
```

### Demo Image Browser (Client-Side)
```javascript
// Source: Adapted from existing respond.html
(function() {
    'use strict';

    const DEMO_STATE_KEY = 'the55-demo-state';
    const seed = parseInt(document.body.dataset.seed || Date.now());
    const perPage = 20;

    let currentPage = 1;
    let totalPages = 1;
    let selectedImageId = null;
    let selectedImageUrl = null;

    // State persistence
    function saveDemoState() {
        const bullets = Array.from(document.querySelectorAll('.bullet-input'))
            .map(input => input.value.trim())
            .filter(b => b);

        sessionStorage.setItem(DEMO_STATE_KEY, JSON.stringify({
            imageId: selectedImageId,
            imageUrl: selectedImageUrl,
            bullets: bullets,
            seed: seed
        }));
    }

    function loadDemoState() {
        try {
            const saved = sessionStorage.getItem(DEMO_STATE_KEY);
            return saved ? JSON.parse(saved) : null;
        } catch (e) {
            return null;
        }
    }

    // Image loading - reuse existing API
    async function loadPage(pageNum) {
        const response = await fetch(`/api/images?page=${pageNum}&per_page=${perPage}&seed=${seed}`);
        const data = await response.json();
        totalPages = data.total_pages;
        renderPage(data.images);
        updatePagination(pageNum);
    }

    function selectImage(imageId, imageUrl) {
        selectedImageId = imageId;
        selectedImageUrl = imageUrl;
        // Update visual selection
        document.querySelectorAll('.image-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.image === imageId);
        });
        // Show bullet section
        document.getElementById('bullet-section').style.display = 'block';
        document.getElementById('selected-image-preview').innerHTML =
            `<img src="${imageUrl}" alt="Your selected image">`;
        saveDemoState();
    }

    // Form submission - navigate to responses page
    document.getElementById('demo-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveDemoState();

        // Navigate with View Transition
        const nextUrl = `/demo/responses?seed=${seed}`;
        if (document.startViewTransition) {
            document.startViewTransition(() => {
                window.location.href = nextUrl;
            });
        } else {
            window.location.href = nextUrl;
        }
    });

    // Initialize
    const savedState = loadDemoState();
    if (savedState && savedState.seed === seed) {
        selectedImageId = savedState.imageId;
        selectedImageUrl = savedState.imageUrl;
        // Restore bullets
        savedState.bullets.forEach((bullet, idx) => {
            const input = document.getElementById(`bullet-${idx + 1}`);
            if (input) input.value = bullet;
        });
    }
    loadPage(1);
})();
```

### Demo Synthesis Display
```html
<!-- Source: Adapted from participant/synthesis.html -->
{% extends "base.html" %}

{% block title %}Synthesis Reveal - The 55 Demo{% endblock %}

{% block content %}
<div class="synthesis-page demo-synthesis">
    <div class="synthesis-header">
        <p class="demo-label">Demo: ClearBrief Team Synthesis</p>
        <h2>What We Found</h2>
    </div>

    <div class="synthesis-section gap-section">
        <h3>Primary Gap</h3>
        <div class="gap-indicator gap-alignment">
            <span class="gap-type">{{ synthesis.gap_type }}</span>
        </div>
        <p class="gap-description">
            The team's work is disconnected or uncoordinated.
        </p>
    </div>

    <div class="synthesis-section themes-section">
        <h3>Team Themes</h3>
        <p class="themes-text">{{ synthesis.themes }}</p>
    </div>

    <div class="synthesis-section statements-section">
        <h3>Key Insights</h3>
        <ul class="insights-list">
            {% for stmt in synthesis.statements %}
            <li class="insight-item">
                <span class="insight-text">{{ stmt.statement }}</span>
                <span class="insight-attribution">({{ stmt.participants|join(', ') }})</span>
            </li>
            {% endfor %}
        </ul>
    </div>

    <div class="demo-cta-section">
        <h3>Ready to find your team's drag?</h3>
        <p>The 55 is a 55-minute monthly diagnostic that makes real divergence visible.</p>
        <a href="/#cta" class="btn btn-primary btn-large">Book Your First Session</a>
        <a href="/" class="btn btn-secondary">Learn More</a>
    </div>
</div>
{% endblock %}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Static screenshots | Interactive HTML/CSS demos | 2024-2025 | 2x engagement, 20-25% faster close |
| Video walkthroughs | Self-guided interactive tours | 2024-2025 | Higher completion, better lead quality |
| Gated demos | Ungated demos | 2025-2026 | Better conversion, trust-building |
| Long form demos | 4-8 step micro-demos | 2025-2026 | Higher completion rates |

**Deprecated/outdated:**
- Static product screenshots: Replaced by interactive demos (2x higher engagement)
- Video-only demos: Interactive outperforms by significant margin
- "Book a demo" as primary CTA: "Try the Demo" / "See How It Works" converts better

## Open Questions

1. **Which 4 images to use for pre-baked team responses?**
   - What we know: Need images that clearly represent the concepts (tangled cables, relay handoff, broken bridge, puzzle pieces)
   - What's unclear: Whether these specific images exist in the current library
   - Recommendation: Audit library for suitable images, or add 4 demo-specific images to `/static/images/demo/`

2. **Demo entry point from landing page**
   - What we know: Landing page already has "See how it works" CTA linking to `/demo`
   - What's unclear: Whether to keep as simple link or add more prominent demo teaser
   - Recommendation: Keep current CTA placement, test conversion after launch

3. **Should demo be replayable without clearing state?**
   - What we know: sessionStorage persists until tab close
   - What's unclear: User expectation when clicking "Try Demo" again
   - Recommendation: Clear demo state when entering `/demo` intro page (fresh start each time)

## Sources

### Primary (HIGH confidence)
- Existing codebase analysis: `app/routers/participant.py`, `templates/participant/respond.html`, `templates/participant/synthesis.html`
- Existing image service: `app/services/images.py` (seeded randomization)
- Existing CSS: `static/css/transitions.css`, `static/css/variables.css`
- MDN Web Docs - View Transitions API: https://developer.mozilla.org/en-US/docs/Web/API/Document/startViewTransition
- MDN Web Docs - sessionStorage: https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage

### Secondary (MEDIUM confidence)
- Navattic Interactive Demo Best Practices: https://www.navattic.com/blog/interactive-demos
- Stytch session management comparison: https://stytch.com/blog/localstorage-vs-sessionstorage-vs-cookies/
- Fisher-Yates shuffle (Wikipedia): https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle

### Tertiary (LOW confidence)
- WebSearch results on SaaS demo conversion (general industry trends, not specific implementations)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - using existing codebase patterns
- Architecture: HIGH - straightforward adaptation of existing participant flow
- Pitfalls: HIGH - based on direct codebase analysis and general web dev experience
- UX patterns: MEDIUM - based on industry research, not A/B tested

**Research date:** 2026-01-27
**Valid until:** 2026-02-27 (30 days - stable domain, no fast-moving dependencies)
