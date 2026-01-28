# Requirements: The 55 App

**Defined:** 2026-01-28
**Core Value:** The 55 catches alignment problems before they become execution problems.

## v2.6 Requirements

Requirements for POC Ready milestone. Each maps to roadmap phases.

### Landing Page Trust Signals

- [ ] **LAND-01**: Landing page has "What finding the drag looks like" section
- [ ] **LAND-02**: Section displays 3 client example cards with concrete scenarios
- [ ] **LAND-03**: Cards show before/after transformation (problem → outcome)
- [ ] **LAND-04**: Card design matches existing design system (Inter font, Apple colors)

### Landing Page Outcomes

- [ ] **LAND-05**: Landing page has benefit-focused outcomes section
- [ ] **LAND-06**: Outcomes describe what changes after finding the drag
- [ ] **LAND-07**: Language is specific (faster execution, clearer priorities, less wasted work)

### Landing Page CTA

- [ ] **LAND-08**: Final CTA section uses "You've felt the drag. Now find it"
- [ ] **LAND-09**: Demo button prominent as primary action
- [ ] **LAND-10**: Secondary email link to Dale (connectedworld@gmail.com)

### Demo Ending Experience

- [ ] **DEMO-22**: Synthesis page replaces current CTAs with "imagine your team" challenge
- [ ] **DEMO-23**: Challenge is visceral and personal ("What would finding YOUR drag be worth?")
- [ ] **DEMO-24**: Challenge references specific quarter/time being lost
- [ ] **DEMO-25**: Challenge uses synthesis gap type (Direction/Alignment/Commitment) to personalize
- [ ] **DEMO-26**: Email CTA to connectedworld@gmail.com with pre-filled subject

### SEO/Meta

- [ ] **META-01**: Landing page meta description mentions Signal Capture
- [ ] **META-02**: Meta description mentions three gap types (Direction, Alignment, Commitment)

### Conversion Tracking

- [ ] **TRACK-01**: ConversionEvent SQLite model logs CTA interactions
- [ ] **TRACK-02**: Demo completion events logged (reached synthesis page)
- [ ] **TRACK-03**: Email CTA click events logged
- [ ] **TRACK-04**: Landing page → demo click events logged
- [ ] **TRACK-05**: Admin can query conversion metrics (direct SQLite or simple endpoint)

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
| LAND-01 | Phase 26 | Pending |
| LAND-02 | Phase 26 | Pending |
| LAND-03 | Phase 26 | Pending |
| LAND-04 | Phase 26 | Pending |
| LAND-05 | Phase 26 | Pending |
| LAND-06 | Phase 26 | Pending |
| LAND-07 | Phase 26 | Pending |
| LAND-08 | Phase 26 | Pending |
| LAND-09 | Phase 26 | Pending |
| LAND-10 | Phase 26 | Pending |
| DEMO-22 | Phase 26 | Pending |
| DEMO-23 | Phase 26 | Pending |
| DEMO-24 | Phase 26 | Pending |
| DEMO-25 | Phase 26 | Pending |
| DEMO-26 | Phase 26 | Pending |
| META-01 | Phase 26 | Pending |
| META-02 | Phase 26 | Pending |
| TRACK-01 | Phase 26 | Pending |
| TRACK-02 | Phase 26 | Pending |
| TRACK-03 | Phase 26 | Pending |
| TRACK-04 | Phase 26 | Pending |
| TRACK-05 | Phase 26 | Pending |

**Coverage:**
- v2.6 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0

---
*Requirements defined: 2026-01-28*
*Last updated: 2026-01-28 after initial definition*
