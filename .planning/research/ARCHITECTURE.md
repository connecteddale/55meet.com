# Architecture Patterns: Conversion Optimization Integration

**Domain:** Landing page and demo conversion improvements
**Researched:** 2026-01-28
**Confidence:** HIGH

## Executive Summary

The conversion optimization work extends two existing HTML templates with new sections. The architecture follows established patterns: static landing sections with scroll-snap behavior, and demo pages with sessionStorage state management. No new backend routes needed—all changes are template and CSS additions.

## Current Architecture (Verified)

### Landing Page (`/`)
- **Route:** `app/main.py:102` - Direct HTMLResponse, no template engine
- **Template:** `templates/landing.html` - Static HTML file served directly
- **CSS:** `static/css/landing.css` - Dedicated landing styles + `static/css/variables.css` design tokens
- **Pattern:** Full-viewport sections with scroll-snap-type mandatory
- **Interaction:** Intersection Observer for `.reveal` animations, scroll-cue navigation

### Demo Flow (`/demo/*`)
- **Router:** `app/routers/demo.py` - Dedicated demo router
- **State:** sessionStorage keys `the55-demo-response` and `the55-demo-synthesis`
- **Routes:**
  - `/demo` → `demo/intro.html` (scrolling sections)
  - `/demo/signal` → `demo/signal.html` (Signal Capture)
  - `/demo/responses` → `demo/responses.html` (team responses grid)
  - `/demo/synthesis` → `demo/synthesis.html` (AI synthesis/3 layers)
- **Pattern:** View Transitions API (`transitions.css`) for page-to-page navigation
- **Data:** Pre-baked team responses in `DEMO_RESPONSES`, deterministic name shuffling via seed

### Design System
- **Variables:** `static/css/variables.css` - CSS custom properties (colors, spacing, typography)
- **Typography:** Inter font, fluid clamp() sizing, Apple-style tight letter-spacing
- **Components:** Shared patterns (`.btn-primary`, `.brand-badge-floating`, `.demo-cta`)
- **Accessibility:** WCAG 2.1 AA compliant, reduced-motion support

## Integration Points for v2.6 Changes

### 1. Landing Page Additions

**Location:** `templates/landing.html` (lines 1-190)

**Existing structure:**
```
Hero → Problem → Evidence → Drift → Solution →
Emerges → Stats → Rhythm → Facilitator → Contrast → CTA → Footer
```

**New sections to insert:**

| Section | Insert After | Integration Approach |
|---------|--------------|----------------------|
| "What finding looks like" (3 cards) | Evidence section (#evidence) | New `#examples` section, reuses `.landing-section` + `.landing-content` pattern |
| Benefit outcomes | Stats section (#stats) | New `#outcomes` section with `.landing-section-headline` + `.landing-body` |
| Updated CTA | Replace existing #cta | Enhance copy, keep structure |

**Dependencies:**
- Reuse `.landing-section` wrapper (min-height: 100vh, scroll-snap-align)
- Reuse `.landing-content` max-width container (720px)
- Reuse `.reveal` / `.revealed` intersection observer (lines 176-187)
- Reuse `.landing-scroll-cue` for navigation arrows
- Add new component: `.examples-grid` (CSS pattern similar to `.landing-contrast-grid`)

### 2. Demo Synthesis Page Updates

**Location:** `templates/demo/synthesis.html` (lines 1-597)

**Current footer structure (lines 118-134):**
```html
<footer class="tools-footer">
    <div class="footer-links">
        <a href="[calendar]">Book your 1st session</a>
        <a href="[dale]">More about Dale</a>
        <a href="/">Back to top</a>
        <a href="/demo">Restart demo</a>
    </div>
</footer>
```

**Replacement structure:**
- Remove all current footer links
- Add new section before footer: `<section class="challenge-section">`
- Content: "Now imagine your team" challenge + email CTA form/link
- Keep footer structure but reduce to minimal links

**Dependencies:**
- Reuse `.demo-content` wrapper pattern
- Reuse `.demo-cta` button style for email CTA
- Add new: `.challenge-section` with centered layout
- Form submission → `mailto:connectedworld@gmail.com` (no backend needed)

### 3. Meta Tags Update

**Location:** Both files' `<head>` sections

**Current landing meta (line 7):**
```html
<meta name="description" content="The 55 - A monthly diagnostic that finds what's slowing your team down. 55 minutes. One recalibration. Facilitated by Dale Williams.">
```

**Updated meta:**
```html
<meta name="description" content="The 55 - Monthly leadership diagnostic using Signal Capture™ to find what's slowing your team. Reveals Direction, Alignment, or Commitment gaps. 55 minutes. One recalibration.">
```

**Files to update:**
- `templates/landing.html` (line 7)
- `templates/demo/intro.html` (if has meta description)

## Component Boundaries

### New Components Needed

| Component | Purpose | CSS Scope |
|-----------|---------|-----------|
| `.examples-grid` | 3-column card grid for client examples | `landing.css` |
| `.example-card` | Individual example card with before/after | `landing.css` |
| `.outcomes-list` | Benefit outcomes section styling | `landing.css` |
| `.challenge-section` | Demo end "imagine your team" content | Inline in `demo/synthesis.html` |
| `.challenge-cta` | Email CTA styling | Extends `.demo-cta` |

### Modified Components

| Component | Modification | Risk |
|-----------|--------------|------|
| `.landing-section` structure | Add 2 new sections | Low - reuses existing pattern |
| `#cta` section | Replace headline + subtext | Low - same structure |
| `.tools-footer` | Reduce link count | Low - layout unchanged |

## Data Flow

### Landing Page (Static)
```
Browser → nginx → Gunicorn → FastAPI (main.py:102)
                                ↓
                         landing.html read as string
                                ↓
                         HTMLResponse (no template context)
```

**Impact:** Changes to `landing.html` require no Python changes. Simple HTML edit.

### Demo Synthesis Page (Template)
```
Browser → /demo/synthesis?seed=X → FastAPI router (demo.py:666)
                                        ↓
                                  Jinja2 template render
                                  - team_members (shuffled)
                                  - synthesis data (pre-baked)
                                        ↓
                                  demo/synthesis.html
                                        ↓
                                  JavaScript loads CEO response
                                  from sessionStorage
```

**Impact:** CTA changes are template-only. No route/data changes needed.

## Suggested Build Order

### Phase 1: Landing Examples Section
**Why first:** Largest new component, establishes card pattern
**Components:** `.examples-grid`, `.example-card`
**Files:** `templates/landing.html`, `static/css/landing.css`
**Dependencies:** None - self-contained section

### Phase 2: Landing Outcomes Section
**Why second:** Simpler section, reuses typography patterns
**Components:** `.outcomes-list` (minimal CSS)
**Files:** `templates/landing.html`, `static/css/landing.css`
**Dependencies:** None

### Phase 3: Landing CTA Enhancement
**Why third:** Minimal change to existing section
**Files:** `templates/landing.html`
**Dependencies:** None - copy change only

### Phase 4: Demo Challenge Section
**Why fourth:** Isolated demo-only change
**Components:** `.challenge-section`, `.challenge-cta`
**Files:** `templates/demo/synthesis.html`
**Dependencies:** None - self-contained

### Phase 5: Meta Tags
**Why last:** Quick pass across files
**Files:** `templates/landing.html`, `templates/demo/intro.html`
**Dependencies:** None

## Scalability Considerations

| Concern | Current Scale | At 1K visitors/day | Mitigation |
|---------|---------------|-------------------|------------|
| Static file serving | Immediate | Immediate | nginx static file caching (already enabled) |
| Page size | ~25KB HTML + ~15KB CSS | Same | No dynamic content added |
| Mobile performance | Good (WCAG AA) | Same | Responsive CSS already optimized |

## Anti-Patterns to Avoid

### Don't Create Backend Routes
**Trap:** Adding `/api/contact` for email CTA
**Why bad:** Adds complexity, requires spam protection, email server config
**Instead:** Use `mailto:` link or form with `action="mailto:"`

### Don't Break Scroll Snap
**Trap:** Adding sections without `scroll-snap-align: start`
**Why bad:** Breaks landing page scroll navigation UX
**Instead:** Every new `.landing-section` must have proper scroll snap

### Don't Add New CSS Files
**Trap:** Creating `conversion.css` for new components
**Why bad:** Additional HTTP request, style scope confusion
**Instead:** Add to existing `landing.css` or inline in template

### Don't Duplicate Design Tokens
**Trap:** Hardcoding colors/spacing instead of using CSS variables
**Why bad:** Inconsistent with design system, harder to maintain
**Instead:** Always use `var(--color-primary)`, `var(--space-4)`, etc.

## Testing Integration Points

| Integration Point | Test Approach | Success Criteria |
|------------------|---------------|------------------|
| Scroll navigation | Scroll through landing, verify snap behavior | All sections snap correctly, scroll-cue works |
| Responsive breakpoints | Test at 640px, 768px, 1024px, 1440px | Cards stack properly, text remains readable |
| View Transitions | Navigate demo flow, verify page transitions | Smooth fade/slide transitions (or instant if reduced-motion) |
| sessionStorage | Complete demo, verify synthesis page loads | CEO response appears, team responses shown |
| Reveal animations | Scroll landing page sections | `.reveal` elements fade in on intersection |

## Architecture Decision Record

### Decision: Template-Only Changes
**Context:** Need to add conversion content to landing and demo
**Decision:** Extend existing HTML templates with new sections, no backend changes
**Rationale:**
- Landing page is static HTMLResponse (no template engine needed)
- Demo synthesis has all required data from existing context
- Email CTA via mailto: (no form processing needed)
**Consequences:**
- Faster implementation (no Python changes)
- Lower risk (no route/state changes)
- Easier testing (reload page to see changes)

### Decision: Reuse Existing Components
**Context:** New sections need styling
**Decision:** Extend `landing.css` with new classes following existing patterns
**Rationale:**
- Design system already established (variables.css)
- Component patterns proven (grids, cards, CTAs)
- Consistent UX across landing and demo
**Consequences:**
- Minimal CSS additions (~100 lines for 3 new components)
- No new CSS files to load
- Maintains design consistency

### Decision: No JavaScript for New Sections
**Context:** Static sections vs interactive components
**Decision:** New landing sections are pure CSS, no JS needed
**Rationale:**
- Intersection Observer already handles `.reveal` animations
- Scroll-snap is CSS-only
- Email CTA is `mailto:` link (browser handles)
**Consequences:**
- Simpler implementation
- Works without JS (progressive enhancement)
- Faster page load (no new JS files)

## Open Questions

**Q:** Should "imagine your team" challenge be a separate page or section?
**A:** Section within synthesis page. Visitor has completed full demo flow—keep them on same page for immediate CTA action.

**Q:** Should email CTA be form or mailto: link?
**A:** Mailto link initially. Form would require backend route, validation, spam protection. Can upgrade later if conversion data shows need.

**Q:** How to handle responsive layout for 3-card examples grid?
**A:** Follow `.landing-contrast-grid` pattern: 3 columns desktop, stack to 1 column mobile at 640px breakpoint.

## Implementation Checklist

Pre-implementation verification:

- [ ] Existing landing.html structure reviewed (sections, scroll-snap)
- [ ] Design system tokens documented (colors, spacing, typography)
- [ ] Demo synthesis template structure understood (footer replacement point)
- [ ] View Transitions API behavior confirmed (no JS coordination needed)
- [ ] Responsive breakpoints documented (640px, 1024px, 1200px)
- [ ] Intersection Observer for .reveal animations reviewed
- [ ] sessionStorage keys documented (no conflicts with new content)

## References

**Verified code locations:**
- Landing route: `app/main.py` lines 102-110
- Demo router: `app/routers/demo.py` lines 1-732
- Landing template: `templates/landing.html` lines 1-190
- Demo synthesis: `templates/demo/synthesis.html` lines 1-597
- Design tokens: `static/css/variables.css` lines 1-145
- Landing styles: `static/css/landing.css` lines 1-456
- Transitions: `static/css/transitions.css` lines 1-48

**Design patterns confirmed:**
- Scroll-snap sections (landing.css lines 59-69)
- Reveal animation (landing.css lines 31-41, landing.html lines 176-187)
- View Transitions API (transitions.css lines 1-47)
- Fluid typography (variables.css lines 44-51)
- Component buttons (main.css `.btn-primary`, landing.css `.landing-cta`)
