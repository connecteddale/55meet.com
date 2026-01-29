---
phase: 27
plan: 01
subsystem: demo-intro
tags: [snapshot-explanation, perception-capture, demo-ux, conversion-optimization]
requires: [26-01]
provides:
  - Enhanced Snapshot™ explanation in demo intro
  - Perception capture mechanism explanation
  - WHY/HOW/WHEN framework for Snapshot understanding
affects: [27-02]
tech-stack:
  added: []
  patterns: [progressive-disclosure, education-before-action]
key-files:
  created: []
  modified:
    - templates/demo/intro.html
decisions:
  - id: SNAP-03-explanation-structure
    choice: "Three-paragraph WHY/HOW/WHEN structure"
    rationale: "Visitors need to understand mechanism before participating"
    date: 2026-01-29
  - id: SNAP-03-trademark-usage
    choice: "™ on first use only (headline)"
    rationale: "Follows Phase 26-01 trademark pattern for readability"
    date: 2026-01-29
metrics:
  tasks: 2
  commits: 1
  duration: 55s
  completed: 2026-01-29
---

# Phase 27 Plan 01: Demo Intro Snapshot™ Explanation Summary

**One-liner:** Enhanced demo intro to explain Snapshot™ as perception capture mechanism (bypasses internal editor, image+bullets, first 5 minutes)

## What Was Built

Enhanced the Snapshot™ explanation section in demo intro to clearly communicate WHY, HOW, and WHEN Snapshot works as a perception capture process.

**Key improvements:**
1. **Headline changed:** "The 55 plus Snapshot™" → "Snapshot™ Perception Capture" (more descriptive of mechanism)
2. **WHY it works:** Explicitly states it captures thoughts "before the internal editor kicks in, before meeting-safe answers, before consensus softens the truth"
3. **HOW it works:** Clear process description - "select an image... then explain why in bullet points"
4. **WHEN it happens:** Timing context - "first 5 minutes, before anyone knows what anyone else said"
5. **Trademark notation:** ™ on first use (headline) only, consistent with Phase 26-01 pattern

## Requirements Satisfied

**SNAP-03:** Demo intro explains Snapshot™ as perception capture before filtering
- ✅ Visitor understands WHY (bypasses internal editor)
- ✅ Visitor understands HOW (image selection + bullet points)
- ✅ Visitor understands WHEN (first 5 minutes, private/blind)
- ✅ Trademark notation follows Phase 26 pattern

## Technical Implementation

**File modified:** templates/demo/intro.html (lines 394-401)

**Section structure:**
```html
<section id="process" class="demo-section">
  <div class="demo-content reveal">
    <p class="demo-eyebrow">The Process</p>
    <h2 class="demo-headline">Snapshot™ Perception Capture</h2>
    <p class="demo-body">[WHY: bypasses internal editor...]</p>
    <p class="demo-body">[HOW: image + bullets...]</p>
    <p class="demo-body">[WHEN: first 5 minutes, blind...]</p>
  </div>
  <a href="#team" class="demo-scroll-cue">...</a>
</section>
```

**Design consistency:**
- Used existing demo-section CSS classes
- Maintained scroll navigation pattern (href="#team")
- Preserved reveal animation behavior
- No styling changes required

## User Experience Impact

**Before:** Demo intro mentioned Snapshot™ exists but didn't explain the mechanism
**After:** Visitors understand the perception capture process before they're asked to participate

**Flow improvement:**
1. Visitor reads about bypassing internal editor (WHY)
2. Learns exact process: image selection + bullet points (HOW)
3. Understands privacy: first 5 minutes, blind (WHEN)
4. Then sees team has completed Snapshot
5. Call to action: "Add Your Signal" makes sense in context

**Expected outcome:** Higher demo conversion as visitors understand WHY the process works before being asked to complete it.

## Decisions Made

**Decision 1: Three-paragraph WHY/HOW/WHEN structure**
- **Context:** Original text was vague ("unique team process that bypasses internal editor")
- **Choice:** Break into three distinct paragraphs addressing WHY, HOW, WHEN
- **Rationale:** Progressive disclosure - each paragraph answers a different visitor question
- **Impact:** Clearer education, visitor feels informed before action

**Decision 2: Trademark pattern consistency**
- **Context:** Phase 26-01 established ™ on first use only
- **Choice:** Apply same pattern - "Snapshot™" in headline, plain "Snapshot" in body
- **Rationale:** Readability, brand consistency across site
- **Impact:** Professional trademark usage without visual clutter

## Testing Results

**Page load:** ✅ 200 status, no errors
**Content verification:** ✅ All key concepts present (internal editor, bullet points, 5 minutes)
**Trademark notation:** ✅ Exactly 1 occurrence of "Snapshot™" (first use)
**Navigation:** ✅ Scroll cue links to #team section
**Styling:** ✅ Existing demo-section styles work correctly

**Verified concepts in rendered HTML:**
- "internal editor" - present
- "bullet points" - present
- "first 5 minutes" - present
- "before anyone knows what anyone else said" - present

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

**Phase 27-02 dependencies:**
Plan 27-02 (Demo Ending Personalization) will add personalized ending based on visitor's Snapshot response. This plan established the education foundation - visitors now understand WHAT Snapshot is before completing it, which makes the personalized ending more meaningful.

**No blockers for 27-02.**

## Key Files Modified

**templates/demo/intro.html**
- Lines 394-401: Snapshot™ explanation section
- Changed headline from "The 55 plus Snapshot™" to "Snapshot™ Perception Capture"
- Replaced 2 generic paragraphs with 3 specific WHY/HOW/WHEN paragraphs
- Maintained all existing CSS classes and navigation structure

## Session Notes

**Execution:** Straightforward content enhancement, no technical complexity
**Time:** Under 1 minute execution (Task 1: content update, Task 2: verification)
**Quality:** All verification checks passed on first attempt

**Pattern established:** WHY/HOW/WHEN framework for explaining processes before asking for participation. This pattern could be applied to other conversion points (e.g., explaining why email signup works before showing form).

---

**Plan 27-01 complete.** Snapshot™ explanation now clearly communicates perception capture mechanism. Ready for Plan 27-02 (personalized demo ending).
