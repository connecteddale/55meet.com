# The 55 App

## What This Is

A digital companion for monthly leadership alignment diagnostics. The 55 captures team responses through image selection, surfaces patterns through AI synthesis, and builds accountability through persistent session history.

## Core Value

**The 55 catches alignment problems before they become execution problems.** 55 minutes. Once a month. The truth about where the team actually is.

## Requirements

### Validated

<!-- Shipped and confirmed valuable -->

**v2.0 The 55 Foundation:**
- Separate app at 55.connecteddale.com / 55meet.com — v2.0
- FastAPI backend with SQLite database — v2.0
- Server-rendered templates + vanilla JS frontend — v2.0
- Password-protected admin login (single facilitator) — v2.0
- Team management: create team with company name, team name, unique code — v2.0
- Member management: add/remove members (names only, max 25 per team) — v2.0
- Strategy statement: set 3AM strategy statement per team — v2.0
- Session control: view real-time submission status — v2.0
- Close capture: lock submissions when ready — v2.0
- Reveal toggle: show AI synthesis to participants — v2.0
- History viewing: access any team's past sessions — v2.0
- Frictionless entry: team code only (no account creation) — v2.0
- Month selection: stepper control, defaults to current — v2.0
- Name picker: select from team member list — v2.0
- Strategy display: see 3AM statement before proceeding — v2.0
- Image browser: browse images with pagination — v2.0
- Image selection: tap to select image representing current state — v2.0
- Bullet input: 1-5 bullet points explaining choice — v2.0
- Edit until close: can modify submission until facilitator closes — v2.0
- Waiting state: clear feedback while waiting for reveal — v2.0
- Results view: see AI synthesis when revealed — v2.0
- Claude API integration for response synthesis — v2.0
- Mobile-first responsive design — v2.0
- Real-time polling for submission status — v2.0
- Session state machine: draft → capturing → closed → revealed — v2.0

**v2.1 Facilitator Experience & Presentation:**
- Combined QR code + participant status on single projectable screen — v2.1
- QR code prominently displayed alongside submission status — v2.1
- Real-time status shows who has/hasn't submitted — v2.1
- Close capture early (before all submitted) — v2.1
- Reopen capture after closing — v2.1
- Clear individual submission — v2.1
- Paginated image display (~20 images per page) — v2.1
- Sticky Next/Previous navigation at top — v2.1
- Fixed progress indicator (Page X of Y) — v2.1
- Fixed instruction at top — v2.1
- 200+ images with auto-discovery — v2.1
- Random display order seeded by session — v2.1
- Level 1 Themes view — v2.1
- Level 2 Attributed insights view — v2.1
- Level 3 Raw statements view — v2.1
- Keyboard navigation (1/2/3 keys) — v2.1
- Per-level JSON export — v2.1
- Synthesis retry with clear error UI — v2.1
- Landing page for 55meet.com — v2.1

**v2.2 World Class UX:**
- Design tokens: CSS custom properties for colors, spacing, typography — v2.2
- Fluid typography using clamp() with Apple-style tight letter-spacing — v2.2
- Component patterns (buttons, cards, inputs) with premium feel — v2.2
- Marketing landing page with Duarte/Jobs minimalism — v2.2
- Problem-stakes-solution narrative structure — v2.2
- Full-viewport sections on desktop, natural height on mobile — v2.2
- Facilitator dashboard with sessions-first layout — v2.2
- Client-side search by team name or date — v2.2
- Self-service password change — v2.2
- Unified meeting screen for capture AND presentation — v2.2
- State-driven template with auto-reload on state change — v2.2
- Ceremony reveal animation with projector-optimized typography — v2.2
- WCAG 2.1 AA accessibility (skip link, focus-visible, color-independent status) — v2.2
- Custom 404/500 error pages with graceful degradation — v2.2
- Consistent admin navigation across all pages — v2.2

**v2.3 PDF Export:**
- PDF export button alongside existing JSON/MD exports — v2.3
- Presentation-ready report format (client handout quality) — v2.3
- Clean and minimal design (simple typography, white background) — v2.3
- Report contents: team name, date, strategy statement, synthesis themes, key insights — v2.3

**v2.4 Effortless:**
- Auto-join from QR scan, auto-skip month, strategy merged into browser — v2.4
- Name picker as card grid, image selection animation, progressive bullet inputs — v2.4
- View Transitions API page transitions with prefers-reduced-motion — v2.4
- Random 60-image subset per session from library — v2.4
- Automated lifecycle: DRAFT removed, auto-synthesize, auto-reveal — v2.4
- Meeting control strip with Close Capture and contextual state hints — v2.4
- Live waiting screen: member name chips + View Transition redirect — v2.4

### Active

<!-- Current scope. Building toward these. -->

**v2.5 Interactive Demo:**
- Self-guided demo experience for landing page visitors
- Fictional company context: ClearBrief ($65M legal tech SaaS)
- Pre-defined strategy statement (no user input to get stuck on)
- Team of 4 fictional members with shuffled names from pool
- Signal Capture tease before visitor experiences it
- Visitor completes real Signal Capture (image selection + bullets)
- Visitor's response shown alongside pre-baked team responses
- Pre-crafted synthesis revealing Alignment gap (handoff/coordination)
- No AI API calls — all content pre-generated except visitor's input
- Matches existing app UX patterns and design system

### Out of Scope

<!-- Explicit boundaries -->

- User accounts for participants — frictionless entry is core to the experience
- Email/SMS notifications — manual facilitation for now
- Payment/billing — not a commercial product yet
- Multiple facilitators — Dale only for now (architect for multi-facilitator, don't build)
- Physical card printing integration — digital-first
- Other capture techniques (The Score, Three Questions, Headline, One Word) — architect for, don't build
- 30-day reminder emails — manual follow-up for now
- Benchmarking across teams — future feature
- Trend visualization across sessions — future feature

## Context

**Current state (post-v2.4):**
- Full facilitation tool at 55.connecteddale.com / 55meet.com
- Automated lifecycle: close → synthesize → reveal (no manual steps)
- Participant flow: 4 screens (QR scan → name → browse+select → waiting → results)
- View Transitions API: smooth animated page transitions throughout
- Touch-optimized: card grids, scale animations, progressive inputs
- Live feedback: waiting screen shows member names, meeting view has control strip
- PDF export: Presentation-ready session reports with fpdf2/Inter font
- Design system: Inter font, Apple-inspired colors, fluid typography
- WCAG 2.1 AA accessibility compliant
- ~9,000 LOC across Python/HTML/CSS/JS

**The 55 background:**
- Monthly alignment diagnostic Dale facilitates with leadership teams
- 55 minutes, once a month — catches drift before it compounds
- Four phases: Capture (5m) → Surface (10m) → Read (25m) → Set (15m)
- Three gap types: Direction, Alignment, Commitment
- Output: ONE recalibration action, owned, checkable, revisited in 30 days
- Now digital — full session history, AI synthesis, presentation mode

**Technical environment:**
- FastAPI/SQLite/Gunicorn/nginx at 55meet.com / 55.connecteddale.com
- Same server as connecteddale.com, separate app

**Who Dale is:**
- Strategy Coach (not consultant) — works WITH clients to discover their strategy
- Core approach: Clarity + Alignment, the "3am test", One Page Everything (OPE)
- Core beliefs: "People support what they create" / "Alignment means shared stories" / "Brevity beats verbosity"

## Constraints

- **Tech stack**: Python/FastAPI/SQLite — same server, separate app
- **Images**: 200+ images uploaded by Dale to server directory — auto-discovered by app
- **Domain**: 55meet.com and 55.connecteddale.com (both resolve to same app)
- **Single facilitator**: Dale only (architect for multi-facilitator, don't build)
- **Browser compatibility**: Must work on all major browsers (Chrome, Safari, Firefox, Samsung Internet) on Android, Huawei, iOS, and desktop — targeting last 3-4 years of devices

## Key Decisions

<!-- Decisions made during project lifecycle -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Separate app for The 55 | Different concerns, different stack needs, cleaner separation | Good — v2.0+ shipped |
| FastAPI over Flask for The 55 | Better async support for Claude API calls, modern Python | Good — clean async |
| SQLite for The 55 | Single facilitator, small teams (3-25), sufficient scale | Good — simple, reliable |
| Polling over WebSockets | Simpler, reliable for 25 users, 2-3 second refresh adequate | Good — works well |
| ES6+ vanilla JS (no build) | Modern syntax without framework or transpilation | Good — maintainable |
| Inter font via Google Fonts | Premium feel, SF Pro design DNA | Good — v2.2 shipped |
| Apple-inspired color palette | Minimalist, professional appearance | Good — v2.2 shipped |
| Fluid typography with clamp() | Responsive scaling without breakpoints | Good — works at all sizes |
| State-driven meeting screen | Single template, multiple modes via conditionals | Good — simpler than separate views |
| Defer Interactive Demo | Prioritize core experience over marketing demo | Pending |
| fpdf2 for PDF export | Pure Python, no system deps, active maintenance | Good — clean integration |
| Inter TTF font embedding | Matches design system, SIL license allows embedding | Good — consistent branding |
| Remove DRAFT state entirely | No value in dead code path; sessions start immediately | Good — simpler lifecycle |
| 60-image subset per session | Reduces cognitive load from 173 images | Good — sufficient variety |
| Auto-reveal on synthesis success only | Failures keep CLOSED for manual retry | Good — safe fallback |
| View Transitions API (no SPA) | Progressive enhancement, no build tools needed | Good — graceful degradation |
| @media (hover: hover) separation | Desktop hover vs mobile tap states | Good — no ghost hovers |
| No Reveal button in meeting view | Auto-reveal handles this; reduces facilitator actions | Good — simpler UX |

## Phase Renumbering Reference

Original phases (10-29, 34-37) renumbered to 1-24:

| Original | New | Name |
|----------|-----|------|
| 10 | 01 | foundation |
| 11 | 02 | team-management |
| 12 | 03 | session-infrastructure |
| 13 | 04 | participant-entry |
| 14 | 05 | image-browser |
| 15 | 06 | ai-synthesis |
| 16 | 07 | facilitator-features |
| 17 | 08 | integration-deploy |
| 18 | 09 | image-library-foundation |
| 19 | 10 | participant-image-browser |
| 20 | 11 | session-flow-controls |
| 21 | 12 | combined-qr-status |
| 22 | 13 | synthesis-presentation |
| 23 | 14 | design-foundation |
| 24 | 15 | landing-page |
| 25 | 16 | interactive-demo |
| 26 | 17 | facilitator-dashboard |
| 27 | 18 | unified-meeting-screen |
| 28 | 19 | polish-integration |
| 29 | 20 | pdf-export |
| 34 | 21 | state-machine-auto-flow |
| 35 | 22 | participant-flow-reduction |
| 36 | 23 | interaction-polish |
| 37 | 24 | meeting-view-live-feedback |

---
*Last updated: 2026-01-27 after v2.5 Interactive Demo milestone started*
