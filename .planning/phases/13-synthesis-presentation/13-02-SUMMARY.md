---
phase: 22
plan: 02
title: "Three-Level Presentation View with Keyboard Navigation"
subsystem: presentation-ui
tags: [presentation, keyboard-navigation, tabs, export, jinja2]

dependency_graph:
  requires: [22-01]  # Level-specific export endpoints
  provides: [three-level-presentation, keyboard-switching, synthesis-retry-ui]
  affects: []

tech_stack:
  added: []
  patterns: [tab-navigation, keyboard-shortcuts, progressive-disclosure]

key_files:
  created:
    - the55/app/static/js/presentation.js
  modified:
    - the55/app/routers/sessions.py
    - the55/app/templates/admin/sessions/present.html
    - the55/app/static/css/main.css

decisions:
  - id: PRES-01
    title: "Level tab navigation"
    choice: "Button tabs with data-level attributes"
    rationale: "Simple, accessible, keyboard-friendly"

  - id: PRES-02
    title: "Keyboard shortcuts for presentation"
    choice: "1/2/3 keys switch levels"
    rationale: "Facilitator can control with minimal distraction"

  - id: PRES-03
    title: "Level 3 content organization"
    choice: "Group by participant with image reference"
    rationale: "Natural mapping to who said what"

metrics:
  duration: "~2m"
  completed: "2026-01-19"
---

# Phase 22 Plan 02: Three-Level Presentation View with Keyboard Navigation Summary

Professional three-level presentation interface with keyboard shortcuts for seamless facilitator control during synthesis reveal.

## What Was Done

### Task 1: Update sessions router for Level 3 data
- Added raw_responses list to present_session template context
- Query Response records joined with Member names
- Build response data with participant, image_number, bullets
- Added synthesis_failed boolean for retry UI visibility

### Task 2: Create three-level presentation template
- Restructured present.html with tabbed navigation
- Level 1: Themes and gap type (default view)
- Level 2: Attributed insights with participant names
- Level 3: Raw responses grouped by participant
- Each level has its own export button
- Synthesis failure shows error with retry button
- Keyboard hint in fixed position

### Task 3: Create keyboard navigation JavaScript
- IIFE pattern to avoid global namespace pollution
- ES5 syntax for maximum browser compatibility
- Handles 1/2/3 keypresses to switch levels
- Click handlers for tab buttons
- Ignores keyboard when focused on input fields

### Task 4: Add presentation level CSS
- Tab navigation with active state highlighting
- Level content visibility toggle
- Raw participant cards for Level 3
- Export button styling
- Fixed keyboard hint
- Synthesis error state with retry button

## Decisions Made

| ID | Decision | Choice | Rationale |
|----|----------|--------|-----------|
| PRES-01 | Tab structure | Button tabs with data-level | Simple, accessible, aria-compatible |
| PRES-02 | Keyboard control | 1/2/3 keys | Fast facilitator control |
| PRES-03 | Level 3 layout | Participant grouping | Natural attribution view |

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- Template contains data-level attributes (6 instances)
- JavaScript contains keydown event listener
- CSS contains level-tab styling rules
- All patterns from must_haves satisfied

## Success Criteria Met

- [x] Three tabs visible at top of presentation
- [x] Clicking tabs switches content
- [x] Pressing 1/2/3 keys switches content
- [x] Level 1 shows themes, gap type, export button
- [x] Level 2 shows attributed statements, export button
- [x] Level 3 shows raw responses by participant, export button
- [x] Failed synthesis shows error with retry button
- [x] Keyboard hint visible in corner

## Files Changed

| File | Change |
|------|--------|
| `the55/app/routers/sessions.py` | Added raw_responses and synthesis_failed to context (+20 lines) |
| `the55/app/templates/admin/sessions/present.html` | Complete restructure with three-level tabs (+72 lines) |
| `the55/app/static/js/presentation.js` | New file for keyboard navigation (77 lines) |
| `the55/app/static/css/main.css` | Level styling and error state (+137 lines) |

## Commits

1. `8fb53c6` feat(22-02): pass raw_responses and synthesis_failed to present template
2. `08de6f4` feat(22-02): add three-level tabbed presentation view
3. `72d2d5a` feat(22-02): add keyboard navigation for presentation levels
4. `1f0402c` style(22-02): add presentation level tab and content styling

## Next Phase Readiness

Phase 22 Plan 02 complete. This concludes Phase 22 and the v2.1 Facilitator Experience milestone.

All synthesis presentation requirements implemented:
- PRES-01: Level 1 high-level themes
- PRES-02: Level 2 attributed insights
- PRES-03: Level 3 raw responses
- PRES-04: Keyboard navigation
- PRES-05: Level-specific export (from 22-01)
