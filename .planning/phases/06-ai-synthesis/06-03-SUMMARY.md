---
phase: 15-ai-synthesis
plan: 03
subsystem: participant-ui
tags: [synthesis, participant, jinja2, css]
dependency-graph:
  requires: [15-01-synthesis-service]
  provides: [participant-synthesis-view]
  affects: []
tech-stack:
  added: []
  patterns: [state-based-routing, json-parsing-templates]
key-files:
  created:
    - the55/app/templates/participant/synthesis.html
  modified:
    - the55/app/routers/participant.py
    - the55/app/static/css/main.css
decisions:
  - id: synthesis-redirect-on-non-revealed
    choice: "Redirect non-REVEALED access to waiting page or join"
    why: "Prevents direct URL access to incomplete synthesis"
metrics:
  duration: 3m
  completed: 2026-01-19
---

# Phase 15 Plan 03: Participant Synthesis Display Summary

Participant-facing synthesis view that displays team themes, attributed insights, and gap diagnosis when session is REVEALED.

## Outcome

Created complete participant synthesis viewing experience:
- GET endpoint with state validation redirects
- Jinja2 template with conditional sections
- CSS styles with color-coded gap indicators

## Tasks Completed

| # | Task | Commit | Key Files |
|---|------|--------|-----------|
| 1 | Add synthesis view endpoint | 706efab | app/routers/participant.py |
| 2 | Create synthesis template | a329936 | app/templates/participant/synthesis.html |
| 3 | Add synthesis page styles | 29468d8 | app/static/css/main.css |

## Decisions Made

**Redirect non-REVEALED access to waiting:**
- DRAFT state redirects to /join (session not active)
- CAPTURING/CLOSED redirects to waiting page (synthesis not ready)
- Only REVEALED state shows synthesis content
- Handles direct URL access gracefully

## Technical Details

**Synthesis endpoint flow:**
1. Validate team code and session
2. Check session state:
   - DRAFT: redirect to /join
   - CAPTURING/CLOSED: redirect to waiting page
   - REVEALED: render synthesis template
3. Parse synthesis_statements JSON
4. Pass synthesis data to template

**Template sections:**
- Header: session month and company name
- Themes: paragraph text of synthesized themes
- Gap indicator: color-coded badge with description
  - Direction (blue): lack of shared goals
  - Alignment (orange): disconnected work
  - Commitment (green): individual vs collective
- Insights: list with participant attribution
- Footer: team discussion prompt

**CSS implementation:**
- Mobile-first, max-width 600px
- Uses CSS custom properties for consistency
- Card-based section layout
- Admin preview styles included for future use

## Deviations from Plan

None - plan executed exactly as written.

## Files Changed

**Created:**
- `the55/app/templates/participant/synthesis.html` - 72 lines
  - Extends base.html with participant-header
  - Conditional sections for themes, gap, insights
  - Empty state handling

**Modified:**
- `the55/app/routers/participant.py` - Added 59 lines
  - view_synthesis() endpoint function
  - State validation and redirects
  - JSON parsing for statements

- `the55/app/static/css/main.css` - Added 137 lines
  - Synthesis page container styles
  - Gap indicator color variants
  - Insights list formatting
  - Admin preview styles

## Verification

All verification criteria passed:
- Synthesis route exists at /join/{code}/session/{session_id}/synthesis
- Template renders without Jinja errors (tested with full and empty data)
- CSS contains all required styles (synthesis-page, gap-direction/alignment/commitment)
- Waiting page already has redirect to synthesis on REVEALED state

## Next Phase Readiness

Phase 15 (AI Synthesis) is now complete:
- 15-01: Synthesis service with Claude integration
- 15-02: Synthesis router (trigger endpoint, status polling)
- 15-03: Synthesis display (this plan)

Ready for Phase 16 (Facilitator Features):
- Presentation mode
- History view
- Notes and export
