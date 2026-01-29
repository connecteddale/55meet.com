---
phase: 28
plan: 02
subsystem: analytics
tags: [conversion-tracking, privacy-first, sqlalchemy, sqlilte, funnel-analytics]
requires: [28-01]
provides: [conversion-event-model, demo-funnel-tracking, email-cta-tracking]
affects: [28-03]
tech-stack:
  added: []
  patterns: [privacy-first-analytics, fire-and-forget-tracking]
key-files:
  created: []
  modified: [app/db/models.py, app/routers/demo.py, app/main.py, templates/demo/synthesis.html, templates/landing.html]
decisions:
  - id: no-session-hash
    choice: Deferred session_hash field from model
    rationale: Research showed unclear value for mobile networks, privacy-first design avoids fingerprinting
  - id: sendbeacon-for-mailto
    choice: Use navigator.sendBeacon for email click tracking
    rationale: Fires reliably even if page unloads immediately after mailto opens
  - id: no-landing-view-tracking
    choice: Do not log landing page views
    rationale: Prevents excessive events - only log intentional CTA actions
metrics:
  duration: 3m 20s
  completed: 2026-01-29
---

# Phase 28 Plan 02: Conversion Event Tracking Summary

**One-liner:** Privacy-first SQLite conversion tracking for demo funnel (click, completion, email CTA) without cookies or external analytics.

## What Was Built

Added ConversionEvent model and implemented end-to-end conversion tracking across the demo funnel and landing page CTAs.

**Core Components:**

1. **ConversionEvent SQLAlchemy Model** (app/db/models.py)
   - EventType enum: DEMO_CLICK, DEMO_COMPLETION, EMAIL_CLICK
   - Fields: id, event_type, event_data (JSON), created_at
   - Indexed on event_type and created_at for query performance
   - Privacy-first: no PII, no session_hash, no cookies

2. **Server-Side Event Logging** (app/routers/demo.py, app/main.py)
   - DEMO_CLICK: Logged when visitor hits /demo (captures referrer header)
   - DEMO_COMPLETION: Logged when visitor reaches synthesis page (captures seed for team consistency)
   - POST /api/track-email endpoint: Receives client-side email click events

3. **Client-Side Email Tracking** (templates/demo/synthesis.html, templates/landing.html)
   - navigator.sendBeacon onclick handler on synthesis email CTA
   - navigator.sendBeacon onclick handler on landing page email link
   - Tracks source (synthesis vs landing) and gap type
   - Fire-and-forget: doesn't block mailto from opening

**Database Schema:**
```sql
CREATE TABLE conversion_events (
    id INTEGER NOT NULL,
    event_type VARCHAR(15) NOT NULL,
    event_data TEXT,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX ix_conversion_events_event_type ON conversion_events (event_type);
CREATE INDEX ix_conversion_events_created_at ON conversion_events (created_at);
```

## Key Technical Decisions

### 1. Privacy-First Design
**Decision:** Use SQLite local storage, no cookies, no session fingerprinting, no external analytics.

**Rationale:**
- Data ownership: all conversion data stays in our database
- No GDPR cookie consent needed
- No external dependencies (Google Analytics, Mixpanel, etc.)
- Visitor privacy preserved while still tracking funnel effectiveness

**Implementation:**
- ConversionEvent model stores only event type, timestamp, and minimal context
- No user_id or PII fields
- Session_hash deferred after research showed unclear value for mobile networks

### 2. Fire-and-Forget Tracking Pattern
**Decision:** Use navigator.sendBeacon for email click tracking instead of fetch/XHR.

**Rationale:**
- sendBeacon fires reliably even if user navigates away immediately
- Specifically designed for analytics/logging use cases
- No need for async/await handling
- mailto opens without delay

**Alternative Considered:** fetch() with fire-and-forget - rejected because less reliable on page unload.

### 3. Selective Event Logging
**Decision:** Only log intentional CTA actions, not landing page views.

**Rationale:**
- Landing page views would create excessive events (every visitor)
- Focus on funnel conversion points: demo click, demo completion, email CTA clicks
- More actionable data for funnel optimization

**Events Tracked:**
- DEMO_CLICK: User interest (clicked "Try the Demo")
- DEMO_COMPLETION: User engagement (completed full demo to synthesis)
- EMAIL_CLICK: Conversion intent (clicked email CTA)

## Requirements Met

- **TRACK-01:** ConversionEvent SQLite model logs CTA interactions ✓
- **TRACK-02:** Demo completion events logged (reached synthesis page) ✓
- **TRACK-03:** Email CTA click events logged ✓
- **TRACK-04:** Landing page to demo click events logged ✓

## Deviations from Plan

None - plan executed exactly as written.

## Testing Performed

1. **Model Creation:** Verified ConversionEvent model imports and table creation
2. **Database Schema:** Confirmed indexes created on event_type and created_at
3. **Server Syntax:** Validated Python imports work without errors
4. **Template Syntax:** Verified sendBeacon onclick handlers added to both templates

## Files Modified

### Created
- None (all modifications to existing files)

### Modified
- `app/db/models.py` - Added EventType enum and ConversionEvent model
- `app/routers/demo.py` - Added DEMO_CLICK and DEMO_COMPLETION logging
- `app/main.py` - Added POST /api/track-email endpoint
- `templates/demo/synthesis.html` - Added sendBeacon tracking to email CTA
- `templates/landing.html` - Added sendBeacon tracking to email link

## Commits

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Create ConversionEvent model | c25d912 | app/db/models.py |
| 2 | Add event logging to routes | 9212793 | app/routers/demo.py, app/main.py |
| 3 | Add client-side email tracking | 175602d | templates/demo/synthesis.html, templates/landing.html |

## Next Steps

**Immediate (Phase 28-03):**
- Query conversion_events table to analyze funnel metrics
- Calculate demo click-to-completion rate
- Measure email CTA click-through rate by source (landing vs synthesis)

**Future Enhancements:**
- Dashboard for viewing conversion funnel metrics
- A/B test tracking for CTA copy variations
- Session duration tracking (if session_hash added later)

## Learnings

**Privacy-First Analytics Pattern:**
- SQLite local storage eliminates external dependencies
- No cookies needed = simpler compliance
- sendBeacon provides reliable fire-and-forget tracking
- Selective event logging keeps database lean and actionable

**Fire-and-Forget Best Practice:**
- navigator.sendBeacon perfect for pre-navigation tracking
- No need to await response or handle errors
- Doesn't block user action (mailto opens immediately)

## Knowledge for Future Phases

**For Phase 28-03 (Meta Tags & Analytics Dashboard):**
- Query pattern: `SELECT event_type, COUNT(*), DATE(created_at) FROM conversion_events GROUP BY event_type, DATE(created_at)`
- Funnel metrics: DEMO_CLICK → DEMO_COMPLETION → EMAIL_CLICK
- Source attribution: Parse event_data JSON for referrer and source

**For Future Email CTA Optimization:**
- Gap-specific conversion rates available via event_data gap field
- Landing vs synthesis source comparison available
- Baseline metrics established for A/B testing

## Dependencies

**Required:**
- Phase 28-01 (Meta tags and robots.txt) - Technical foundation for SEO

**Enables:**
- Phase 28-03 (Analytics querying and dashboard) - Consumes conversion_events data

## Context for Future Claude

**What this phase achieved:**
You added privacy-first conversion tracking to The 55 demo funnel. All CTA interactions (demo clicks, demo completions, email clicks) are now logged to SQLite without cookies or external analytics. This provides funnel metrics for optimization while preserving visitor privacy.

**Key patterns established:**
- Privacy-first analytics: SQLite local storage, no PII
- Fire-and-forget tracking: navigator.sendBeacon for reliable pre-navigation logging
- Selective event logging: Only intentional actions, not page views

**If modifying conversion tracking:**
- ConversionEvent model is in app/db/models.py
- Server-side logging in app/routers/demo.py (DEMO_CLICK, DEMO_COMPLETION) and app/main.py (EMAIL_CLICK via /api/track-email)
- Client-side tracking via sendBeacon in templates
- Query with: `sqlite3 db/the55.db "SELECT * FROM conversion_events ORDER BY created_at DESC"`

**If adding new event types:**
1. Add to EventType enum in app/db/models.py
2. Add logging code where event occurs (server-side or client-side)
3. Update event_data JSON schema to include relevant context
4. Document in this summary for future reference
