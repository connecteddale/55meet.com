---
phase: 14
plan: 02
subsystem: image-browser
tags: [bullet-input, form-validation, draft-persistence, participant-flow]
requires: [14-01]
provides: [bullet-input-ui, response-persistence, draft-saving]
affects: [15-ai-synthesis]
tech-stack:
  added: []
  patterns: [localstorage-draft-persistence, json-form-fields, ios-safe-inputs]
key-files:
  created: []
  modified:
    - the55/app/templates/participant/respond.html
    - the55/app/routers/participant.py
    - the55/app/static/css/main.css
decisions:
  - "localStorage draft persistence with session+member key"
  - "16px font-size for iOS zoom prevention (BC-4)"
  - "5 visible inputs with first required, rest optional"
metrics:
  duration: 5m
  completed: 2026-01-19
---

# Phase 14 Plan 02: Bullet Point Input Summary

**One-liner:** 5-field bullet input form with localStorage draft persistence, 500-char validation, and iOS-safe 16px font-size.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Add bullet input section to template | 6cf6c51 | respond.html |
| 2 | Add 500 char limit validation | 1071151 | participant.py |
| 3 | Add bullet input CSS | 1d25ec4 | main.css |

## Implementation Details

### Bullet Input Form (respond.html)

**Form Structure:**
- Hidden after page load, shown when image selected
- 5 text inputs with maxlength="500"
- First bullet required, bullets 2-5 optional
- Hidden JSON field updated on each input change

**Draft Persistence (UX-3):**
```javascript
const draftKey = `draft-${sessionId}-${memberId}`;
// saveDraft(): stores {image, bullets} on every input
// loadDraft(): restores on page load if no existing response
// clearDraft(): removes on successful submit
```

**Edit Mode:**
- Pre-populates bullets from `existing_response.bullets` JSON
- Shows bullet section immediately
- Updates submit button state

**Submit Behavior:**
- Button disabled until image + at least 1 bullet
- On submit: disable button, show "Submitting..." text
- Client-side validation before POST

### Router Validation (participant.py)

**Bullet Validation:**
```python
bullets_list = json.loads(bullets)
bullets_list = [b.strip() for b in bullets_list if b.strip()]
if not 1 <= len(bullets_list) <= 5:
    raise ValueError("Must have 1-5 bullet points")
for bullet in bullets_list:
    if len(bullet) > 500:
        raise ValueError("Each bullet point must be 500 characters or less")
```

- Whitespace-only entries filtered out
- 1-5 non-empty bullets required
- Each bullet max 500 characters

### Bullet Input CSS (main.css)

**iOS-Safe Styling (BC-4):**
```css
.bullet-input {
    font-size: 16px;  /* Prevents iOS zoom on focus */
    min-height: var(--touch-target-min);  /* 44px */
}
```

**Submit Button States:**
```css
.btn-submit:disabled { background: var(--color-border); }
.btn-submit.loading { opacity: 0.7; cursor: wait; }
```

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- [x] Bullet inputs appear after image selection
- [x] At least 1 bullet required for submission
- [x] Draft saves to localStorage on typing
- [x] Draft restores on page reload
- [x] Submit button shows loading state
- [x] Valid submission redirects to waiting page
- [x] Response record created in database
- [x] Input font-size is 16px (no iOS zoom)

## Next Phase Readiness

**Dependencies satisfied for Phase 15 (AI Synthesis):**
- Response model stores image_number and bullets JSON
- All participant responses accessible via Response table
- Session workflow complete through REVEALED state

**Integration points:**
- Response.bullets contains JSON array of 1-5 strings
- Response.image_number is 1-55 integer
- Waiting page polls for session state changes
