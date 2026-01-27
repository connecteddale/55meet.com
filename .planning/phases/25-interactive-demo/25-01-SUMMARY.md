---
phase: 25-interactive-demo
plan: 01
subsystem: demo
tags: [fastapi, jinja2, demo, interactive]

# Dependency graph
requires: []
provides:
  - Demo router foundation at /demo prefix
  - Pre-baked ClearBrief company data
  - Team member name shuffling with hourly seed
  - Demo intro page with company context and team cards
affects: [25-02, 25-03, 25-04] # Signal capture, synthesis, and other demo pages

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Demo router with pre-baked data constants
    - Seeded randomization for deterministic shuffling
    - View transition names for demo flow

key-files:
  created:
    - app/routers/demo.py
    - templates/demo/intro.html
  modified:
    - app/routers/__init__.py
    - app/main.py

key-decisions:
  - "Hourly seed for team name shuffling - consistent experience for returning visitors within an hour"
  - "Pre-baked data in Python constants - no database or AI calls for demo"
  - "View transition names added for future cross-page animations"

patterns-established:
  - "Demo routes use /demo prefix with seed query param for deterministic behavior"
  - "Demo templates in templates/demo/ directory extending base.html"

# Metrics
duration: 4min
completed: 2026-01-27
---

# Phase 25 Plan 01: Demo Router Foundation Summary

**Demo router with ClearBrief pre-baked company data and intro page showing team members with hourly-seeded name shuffling**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-27T06:34:10Z
- **Completed:** 2026-01-27T06:37:53Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Created demo router foundation at /demo with pre-baked ClearBrief company data
- Implemented team name shuffling with hourly-changing seed for consistent visitor experience
- Built intro page showing company context, strategy statement, and 4 leadership team members
- Added CTA button linking to signal capture with seed parameter for deterministic flow

## Task Commits

Each task was committed atomically:

1. **Task 1: Create demo router with pre-baked data and intro route** - `c50f3b7` (feat)
2. **Task 2: Create demo intro template with company context and team cards** - `b4ab0a9` (feat)

## Files Created/Modified
- `app/routers/demo.py` - Demo router with DEMO_COMPANY, NAME_POOLS, get_demo_seed(), get_shuffled_team()
- `app/routers/__init__.py` - Added demo_router export
- `app/main.py` - Included demo_router in app
- `templates/demo/intro.html` - Demo intro page with company context, team grid, and CTA

## Decisions Made
- Hourly seed (time // 3600) ensures consistent experience for returning visitors within an hour while still showing variety
- Pre-baked data constants keep demo completely stateless - no database queries needed
- Used existing design system CSS variables for consistent styling

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Initial verification used wrong port (8000 instead of 8055) - the55 service runs on port 8055 behind nginx

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Demo router foundation complete with /demo route responding
- Ready for 25-02 which adds /demo/signal route for image selection
- Seed parameter flow established for deterministic team generation across pages

---
*Phase: 25-interactive-demo*
*Completed: 2026-01-27*
