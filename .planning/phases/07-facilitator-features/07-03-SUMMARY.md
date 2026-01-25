---
phase: 16-facilitator-features
plan: 03
subsystem: facilitator-ui
tags: [presentation, export, projector, json]
dependency-graph:
  requires: [16-01, 16-02]
  provides: [presentation-mode, session-export]
  affects: []
tech-stack:
  added: []
  patterns: [presentation-view, json-export, dark-theme]
key-files:
  created:
    - the55/app/templates/admin/sessions/present.html
  modified:
    - the55/app/routers/sessions.py
    - the55/app/templates/admin/sessions/view.html
    - the55/app/static/css/main.css
decisions: []
metrics:
  duration: 2m
  completed: 2026-01-19
---

# Phase 16 Plan 03: Presentation Mode and Export Summary

Projector-friendly presentation view and JSON export for completed sessions.

## What Was Built

### Presentation Endpoint
- GET `/admin/sessions/{id}/present` returns projector-optimized view
- Redirects to session view if state is not REVEALED
- Parses synthesis statements JSON for display
- Passes team, themes, gap type, statements, and recalibration action

### Export Endpoint
- GET `/admin/sessions/{id}/export` returns JSON download
- Content-Disposition header triggers file download
- Filename: `session-{month}-{team_name}.json`
- Includes: session metadata, team info, all responses, synthesis, facilitator notes

### Presentation Template
- Dark theme (#1a1a2e background) for projector readability
- Hides standard header for clean presentation
- Large text sizes: themes (1.5rem), gap (2rem), insights (1.25rem)
- Color-coded gap badges: Direction (blue), Alignment (orange), Commitment (green)
- Gap descriptions explain what each gap type means
- Recalibration action displayed with accent styling
- Exit link returns to admin session view

### Session View Integration
- "Presentation Mode" button links to present endpoint
- "Export JSON" button triggers download
- Only visible when session state is REVEALED

### CSS Styles
- `.presentation-mode` body class for dark theme
- `.presentation-container` with 1000px max-width
- `.presentation-gap.gap-{type}` colored badges
- `.presentation-insights` list with subtle borders
- `.presentation-action` with green left border accent
- `.exit-presentation` subtle footer link

## Technical Decisions

None required - followed existing patterns.

## Files Changed

| File | Change |
|------|--------|
| `the55/app/routers/sessions.py` | Added present and export endpoints |
| `the55/app/templates/admin/sessions/present.html` | New presentation template |
| `the55/app/templates/admin/sessions/view.html` | Added presentation and export buttons |
| `the55/app/static/css/main.css` | Added presentation mode styles |

## Commits

| Hash | Message |
|------|---------|
| 560e2ba | feat(16-03): add presentation and export endpoints |
| f15d23e | feat(16-03): create presentation template |
| 828ffbd | style(16-03): add presentation mode styles |
| 6b6683e | feat(16-03): add presentation and export links to session view |

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- [x] /admin/sessions/{id}/present returns presentation view for revealed sessions
- [x] /admin/sessions/{id}/present redirects for non-revealed sessions
- [x] /admin/sessions/{id}/export returns JSON with session data
- [x] Presentation mode displays synthesis clearly with large text
- [x] Export includes all session data (team, responses, synthesis, facilitator notes)
- [x] Session view shows buttons to access both features

## Next Phase Readiness

Phase 16 complete. Ready for Phase 17 (Integration & Deploy).
