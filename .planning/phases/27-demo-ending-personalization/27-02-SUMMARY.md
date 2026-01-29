---
phase: 27
plan: 02
subsystem: demo-conversion
tags: [personalization, email-cta, gap-types, conversion-optimization]
requires:
  - "26-03: Dual CTA pattern (demo button + email link)"
  - "25-01: Demo synthesis with gap_type context variable"
provides:
  - "Gap-type personalized conversion section on synthesis page"
  - "Email CTA to connectedworld@gmail.com with pre-filled subject"
  - "Visceral personal challenge replacing generic footer"
affects:
  - "28-02: Conversion tracking (email clicks and demo completions)"
tech-stack:
  added: []
  patterns:
    - "Jinja2 conditional personalization based on gap_type"
    - "Email mailto links with pre-filled subject parameters"
key-files:
  created: []
  modified:
    - templates/demo/synthesis.html
decisions:
  - id: CONV-01
    choice: "Replace generic footer with conversion-focused section"
    rationale: "Peak emotional moment after gap reveal needs conversion focus, not navigation distractions"
  - id: CONV-02
    choice: "Email CTA instead of calendar link as primary action"
    rationale: "Lower friction, matches POC conversion path (email inquiry before booking)"
  - id: CONV-03
    choice: "Three personalized challenges by gap type"
    rationale: "Alignment personalizes conversion message to specific pain point visitor just experienced"
metrics:
  duration: "2 minutes"
  completed: "2026-01-29"
---

# Phase 27 Plan 02: Synthesis Conversion Personalization Summary

**One-liner:** Gap-type personalized conversion section with email CTA replaces generic footer on synthesis page.

## What Was Built

Transformed the synthesis page footer from generic navigation links into a personalized conversion section that:

1. **Personalizes by gap type** - Three distinct messages (Direction/Alignment/Commitment)
2. **Visceral personal challenge** - "What would finding YOUR [gap] drag be worth? A quarter? Two?"
3. **Email CTA** - connectedworld@gmail.com with pre-filled subject including gap type
4. **Removes competing CTAs** - Calendar link, "More about Dale", "Back to top" removed
5. **Subtle restart** - "Start a new demo" link kept but de-emphasized

### Personalized Messages

**Direction Gap:**
- Headline: "Imagine your team pulling in the same direction."
- Challenge: "What would finding YOUR direction drag be worth? A quarter? Two?"
- Context: "Your team may lack shared understanding of goals or priorities."

**Alignment Gap:**
- Headline: "Imagine your team's work actually fitting together."
- Challenge: "What would finding YOUR alignment drag be worth? A quarter? Two?"
- Context: "Your team's work may be disconnected or uncoordinated."

**Commitment Gap:**
- Headline: "Imagine everyone rowing the same boat."
- Challenge: "What would finding YOUR commitment drag be worth? A quarter? Two?"
- Context: "Individual interests may be overriding collective success."

### Email CTA

```html
<a href="mailto:connectedworld@gmail.com?subject=About%20The%2055%20-%20{{ synthesis_gap_type }}%20Gap%20Demo">
  Email Dale about my {{ synthesis_gap_type }} gap
</a>
```

**Pre-filled subjects:**
- "About The 55 - Direction Gap Demo"
- "About The 55 - Alignment Gap Demo"
- "About The 55 - Commitment Gap Demo"

## Requirements Satisfied

- **DEMO-22**: "imagine your team" challenge immediately after gap reveal ✓
- **DEMO-23**: Visceral personal challenge ("What would finding YOUR drag be worth?") ✓
- **DEMO-24**: Quarter/time reference ("A quarter? Two?") ✓
- **DEMO-25**: Personalized by gap type (Direction/Alignment/Commitment) ✓
- **DEMO-26**: Email CTA to connectedworld@gmail.com with pre-filled subject ✓
- **SNAP-03**: Email replaces calendar as primary conversion path ✓

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Replace generic footer with personalized conversion section | bcea13e | templates/demo/synthesis.html |
| 2 | Add conversion section CSS styles | e8dc3e9 | templates/demo/synthesis.html |
| 3 | Test personalization with all gap types | - | (verification only) |

## Technical Implementation

### HTML Structure

```html
<section class="demo-conversion-section">
  {% if synthesis_gap_type == 'Direction' %}
    <!-- Direction personalization -->
  {% elif synthesis_gap_type == 'Alignment' %}
    <!-- Alignment personalization -->
  {% elif synthesis_gap_type == 'Commitment' %}
    <!-- Commitment personalization -->
  {% else %}
    <!-- Generic fallback -->
  {% endif %}

  <div class="conversion-cta-container">
    <a href="mailto:connectedworld@gmail.com?subject=...">
      Email Dale about my {{ synthesis_gap_type }} gap
    </a>
  </div>
</section>
```

### CSS Styling

- **Gradient background**: Same pattern as Layer 1 (high level insights)
- **Responsive typography**: Smaller text on mobile
- **Hover effects**: Button lift + shadow on hover
- **Design system**: Uses CSS variables for consistency

### Gap Type Context

The `synthesis_gap_type` template variable is already available from:
- Phase 25: Demo synthesis with pre-baked Alignment gap
- Routes: `/demo/synthesis` passes gap_type from DEMO_SYNTHESIS constant

## Conversion Flow

**Before (generic footer):**
1. User sees gap reveal
2. Footer offers: Calendar link, More about Dale, Back to top, Restart demo
3. Multiple competing CTAs dilute conversion

**After (personalized conversion):**
1. User sees gap reveal
2. Personalized challenge: "Imagine your team's work actually fitting together"
3. Visceral question: "What would finding YOUR alignment drag be worth?"
4. Single clear CTA: Email Dale
5. Subtle restart option (not competing)

## Decisions Made

### CONV-01: Replace Footer with Conversion Section

**Choice:** Remove generic footer navigation, replace with conversion-focused section

**Rationale:**
- Synthesis reveal is peak emotional moment (just saw their team's gap)
- Generic navigation dilutes conversion intent
- User attention should focus on one decision: take action or not

**Impact:** Single-purpose page ending, no navigation distractions

### CONV-02: Email CTA as Primary Action

**Choice:** Email to connectedworld@gmail.com instead of calendar booking

**Rationale:**
- POC conversion path: email inquiry → conversation → booking
- Calendar link assumes too much (commitment to 55-minute session)
- Email allows Dale to qualify and respond personally
- Lower friction = higher conversion

**Impact:** Matches consultative sales approach, reduces commitment barrier

### CONV-03: Three Personalized Challenges

**Choice:** Different headline and challenge for each gap type

**Rationale:**
- Visitor just experienced specific gap type in demo
- Generic message loses emotional connection
- Personalized message reinforces "this is about MY team's problem"

**Impact:**
- Direction: "pulling in the same direction"
- Alignment: "work actually fitting together"
- Commitment: "everyone rowing the same boat"

Each message mirrors the gap they just saw.

## Deviations from Plan

None - plan executed exactly as written.

## Testing & Verification

### Template Validation

- ✓ Three gap type conditionals present (Direction, Alignment, Commitment)
- ✓ Email mailto link includes gap_type variable dynamically
- ✓ Page loads without errors (302 redirect for demo flow protection)
- ✓ Calendar link removed (count: 0)
- ✓ "Start a new demo" link present but subtle

### Personalization Verification

The demo uses pre-baked synthesis with **Alignment** gap type, so production visitors see:
- Headline: "Imagine your team's work actually fitting together."
- Challenge: "What would finding YOUR alignment drag be worth?"
- Email subject: "About The 55 - Alignment Gap Demo"

Template conditionals tested for all three gap types (Direction/Alignment/Commitment) with proper fallback.

## Next Phase Readiness

### Blockers
None.

### Concerns
None.

### Phase 28 Dependencies

Phase 28 (SEO & Conversion Tracking) will track:
- Email CTA clicks (connectedworld@gmail.com)
- Demo completion rates (reaching synthesis page)
- Gap type distribution (which gaps visitors see most)

The email CTA is now in place and ready for tracking implementation.

## User Experience Impact

**Before:** "I just saw my team's gap. Now what? Multiple links... I'll think about it later."

**After:** "I just saw my team's Alignment gap. What would finding that drag be worth? A quarter? Two? [Email Dale about my Alignment gap]"

The personalized challenge transforms passive information consumption into urgent personal decision.

---

**Phase 27 Plan 02 complete.** Synthesis page now converts with personalized urgency instead of generic navigation.
