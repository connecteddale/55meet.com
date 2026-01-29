# Requirements: The 55 App

**Defined:** 2026-01-28
**Core Value:** The 55 catches alignment problems before they become execution problems.

## v2.6 Requirements

Requirements for POC Ready milestone. Each maps to roadmap phases.

### Landing Page Trust Signals

- [x] **LAND-01**: Landing page has "What finding the drag looks like" section
- [x] **LAND-02**: Section displays 3 client example cards with concrete scenarios
- [x] **LAND-03**: Cards show before/after transformation (problem → outcome)
- [x] **LAND-04**: Card design matches existing design system (Inter font, Apple colors)

### Landing Page Outcomes

- [x] **LAND-05**: Landing page has benefit-focused outcomes section
- [x] **LAND-06**: Outcomes describe what changes after finding the drag
- [x] **LAND-07**: Language is specific (faster execution, clearer priorities, less wasted work)

### Landing Page CTA

- [x] **LAND-08**: Final CTA section uses "You've felt the drag. Now find it"
- [x] **LAND-09**: Demo button prominent as primary action
- [x] **LAND-10**: Secondary email link to Dale (connectedworld@gmail.com)

### Demo Ending Experience

- [ ] **DEMO-22**: Synthesis page replaces current CTAs with "imagine your team" challenge
- [ ] **DEMO-23**: Challenge is visceral and personal ("What would finding YOUR drag be worth?")
- [ ] **DEMO-24**: Challenge references specific quarter/time being lost
- [ ] **DEMO-25**: Challenge uses synthesis gap type (Direction/Alignment/Commitment) to personalize
- [ ] **DEMO-26**: Email CTA to connectedworld@gmail.com with pre-filled subject

### Snapshot™ Rebrand

- [x] **SNAP-01**: All "Signal Capture" references renamed to "Snapshot™" across entire app
- [x] **SNAP-02**: Landing page links to connecteddale.com/releases/Snapshot.html article
- [x] **SNAP-03**: Demo intro explains Snapshot™ (perception capture before filtering)
- [x] **SNAP-04**: Consistent trademark notation (Snapshot™ on first use, Snapshot thereafter)

### SEO/Meta

- [x] **META-01**: Landing page meta description mentions Snapshot™
- [x] **META-02**: Meta description mentions three gap types (Direction, Alignment, Commitment)

### Conversion Tracking

- [x] **TRACK-01**: ConversionEvent SQLite model logs CTA interactions
- [x] **TRACK-02**: Demo completion events logged (reached synthesis page)
- [x] **TRACK-03**: Email CTA click events logged
- [x] **TRACK-04**: Landing page → demo click events logged
- [x] **TRACK-05**: Admin can query conversion metrics (direct SQLite or simple endpoint)

## Future Requirements

Deferred to future milestones.

### Additional Capture Techniques

- **CAPT-01**: The Score technique implementation
- **CAPT-02**: Three Questions technique implementation
- **CAPT-03**: Headline technique implementation
- **CAPT-04**: One Word technique implementation

### Multi-Facilitator

- **MULTI-01**: Architect for multiple facilitators (do not build yet)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Contact form | Research shows mailto: outperforms forms by 50%+ |
| A/B testing infrastructure | Manual observation sufficient for POC volume |
| External analytics (GA, Plausible) | Server-side tracking sufficient, privacy-first |
| Newsletter signup | Single CTA focus — multiple CTAs reduce conversion |
| Calendar booking integration | Email-first, Dale handles scheduling manually |
| Client testimonial videos | Text examples sufficient for POC |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| LAND-01 | Phase 26 | Complete |
| LAND-02 | Phase 26 | Complete |
| LAND-03 | Phase 26 | Complete |
| LAND-04 | Phase 26 | Complete |
| LAND-05 | Phase 26 | Complete |
| LAND-06 | Phase 26 | Complete |
| LAND-07 | Phase 26 | Complete |
| LAND-08 | Phase 26 | Complete |
| LAND-09 | Phase 26 | Complete |
| LAND-10 | Phase 26 | Complete |
| DEMO-22 | Phase 27 | Complete |
| DEMO-23 | Phase 27 | Complete |
| DEMO-24 | Phase 27 | Complete |
| DEMO-25 | Phase 27 | Complete |
| DEMO-26 | Phase 27 | Complete |
| SNAP-01 | Phase 26 | Complete |
| SNAP-02 | Phase 26 | Complete |
| SNAP-03 | Phase 27 | Complete |
| SNAP-04 | Phase 26 | Complete |
| META-01 | Phase 28 | Complete |
| META-02 | Phase 28 | Complete |
| TRACK-01 | Phase 28 | Complete |
| TRACK-02 | Phase 28 | Complete |
| TRACK-03 | Phase 28 | Complete |
| TRACK-04 | Phase 28 | Complete |
| TRACK-05 | Phase 28 | Complete |

**Coverage:**
- v2.6 requirements: 26 total
- Mapped to phases: 26
- Unmapped: 0
- Coverage: 100%

---
*Requirements defined: 2026-01-28*
*Last updated: 2026-01-29 — v2.6 POC Ready milestone complete (all 26 requirements)*
