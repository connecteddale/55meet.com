---
status: testing
phase: 25-interactive-demo
source: 25-01-SUMMARY.md, 25-02-SUMMARY.md, 25-03-SUMMARY.md, 25-04-SUMMARY.md
started: 2026-01-28T00:00:00Z
updated: 2026-01-28T00:00:00Z
---

## Current Test

number: 1
name: Landing Page to Demo Link
expected: |
  From the landing page (/), clicking "See how it works" or similar CTA navigates to /demo
awaiting: user response

## Tests

### 1. Landing Page to Demo Link
expected: From the landing page (/), clicking "See how it works" or similar CTA navigates to /demo
result: [pending]

### 2. Demo Intro - ClearBrief Context
expected: /demo shows ClearBrief company name, "$65M legal tech SaaS" context, and strategy statement about helping law firms
result: [pending]

### 3. Demo Intro - Team Members Display
expected: /demo shows 4 leadership team members (CTO, CFO, VP Sales, COO) with names. Names should change on different visits (hourly shuffle)
result: [pending]

### 4. Demo Intro - Signal Capture CTA
expected: /demo has a CTA button that navigates to /demo/signal for the Signal Capture experience
result: [pending]

### 5. Signal Capture - Image Browser
expected: /demo/signal shows an image browser with pagination. Should display 60 images across 3 pages (20 per page)
result: [pending]

### 6. Signal Capture - Image Selection
expected: Clicking an image selects it (visual indicator appears). Can browse pages and select any image from the 60 available
result: [pending]

### 7. Signal Capture - Bullet Inputs
expected: After selecting an image, bullet inputs appear. Progressive reveal: starts with 1 input, expands to up to 5 as you fill them
result: [pending]

### 8. Signal Capture - Submit Flow
expected: After selecting image and entering at least one bullet, clicking submit navigates to /demo/responses
result: [pending]

### 9. Responses Page - Visitor Response
expected: /demo/responses shows your response (the image you selected and bullets you entered) highlighted differently from team responses
result: [pending]

### 10. Responses Page - Team Responses
expected: /demo/responses shows 4 team member responses with their images and bullets showing alignment gap signals
result: [pending]

### 11. Responses Page - Synthesis CTA
expected: /demo/responses has a "See What We Found" button that navigates to /demo/synthesis
result: [pending]

### 12. Synthesis Page - Gap Reveal
expected: /demo/synthesis shows the identified gap type (Alignment) with themes and team member attributions
result: [pending]

### 13. Synthesis Page - CTAs
expected: /demo/synthesis has clear CTAs: Book Session (or contact), Learn More, and Restart Demo options
result: [pending]

### 14. Demo Restart - Clean State
expected: Clicking "Restart Demo" clears previous selections and returns to /demo for a fresh experience
result: [pending]

## Summary

total: 14
passed: 0
issues: 0
pending: 14
skipped: 0

## Gaps

[none yet]
