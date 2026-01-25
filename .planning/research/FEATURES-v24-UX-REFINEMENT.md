# Feature Landscape: Mobile-First UX Refinement Patterns

**Domain:** Leadership alignment session flow (The 55 App)
**Researched:** 2026-01-24
**Context:** v2.4 Effortless milestone — reducing 7 participant screens to 4, streamlining facilitator actions from 4 to 2

## Executive Summary

This research focuses on six specific UX refinement patterns for The 55 App's mobile-first session flow. The goal is to make every remaining interaction feel intentional and polished by implementing modern mobile patterns that reduce friction while maintaining accessibility.

The patterns investigated:
1. Auto-join from QR (skip entry when code in URL)
2. Tappable name cards (replacing radio buttons)
3. Progressive bullet inputs (1 grows to 5)
4. Live progress waiting screen (showing submissions)
5. Image subset browsing (~60 images, mobile grid)
6. Meeting projector view with control strip
7. Auto-synthesize and auto-reveal patterns

Research reveals clear table stakes (minimum requirements), differentiators (what makes experiences extraordinary), and anti-features (things to deliberately avoid) for each pattern.

**Overall confidence:** HIGH for mobile patterns, MEDIUM for projector-specific UI (limited 2026 research)

---

## Pattern 1: Auto-Join from QR Code

### Table Stakes

| Feature | Why Expected | Implementation Notes |
|---------|--------------|---------------------|
| QR code encodes full URL with team code | Users expect QR scan to "just work" | Format: `https://55meet.com/join/{code}` |
| URL parameter detection on page load | No manual code entry after scanning | Check for code in path, skip join screen if present |
| Works with all QR readers | Native camera apps on iOS/Android | Standard URL encoding, test with Camera app (iOS), Google Lens (Android) |
| Validates team code exists | Graceful error if invalid code | Redirect to generic join page with error message |
| Works with dynamic QR codes | Allow tracking without changing printed codes | Support UTM parameters: `?utm_source=meeting&utm_medium=qr` |

**WCAG Considerations:**
- Provide text alternative for QR code (display team code as text: "Or enter code: ABC123")
- Error messages must be announced to screen readers
- Manual entry fallback always available

### Differentiators

| Feature | Why Extraordinary | Complexity |
|---------|-------------------|------------|
| Silent auto-advance | No "Joining..." intermediate screen — QR scan lands directly on month/name selection | Low |
| Session-aware routing | If only one CAPTURING session exists, skip month selection too — QR → name picker | Medium |
| Deep linking with state | Encode session_id in QR for returning participants: `/join/{code}/session/{id}` | Medium |
| Smart error recovery | If code invalid, show "Did you mean these teams?" with fuzzy match | Medium |
| Analytics-ready | Track QR vs manual entry via URL parameters for facilitation insights | Low |

**Why these matter:**
- Silent auto-advance eliminates perceived loading states — users experience instant gratification
- Session-aware routing reduces 7 screens to potentially 2 for returning participants
- Analytics help facilitators understand which teams need printed QR codes vs verbal codes

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Forcing QR-only entry | Excludes users with non-smartphone devices or QR issues | Always provide manual code entry option prominently |
| Complex QR encoding (JSON, base64) | Breaks standard QR readers, creates long ugly codes | Use simple URLs only |
| Auto-joining without confirmation | User might scan wrong code, no way to back out | Show team name immediately after join: "Welcome to {team_name}" |
| Tracking parameters in printed QRs | Privacy concern, codes get shared/reused | Use dynamic QR service if tracking needed, or embed in URL structure |
| Redirecting to app store | Breaks web-first promise, adds friction | Stay in browser, PWA if needed later |

**Critical:** The QR experience must be faster than manual entry, or users will skip it. Target: scan to name picker in under 2 seconds.

### Sources

- [Power BI Mobile QR codes with parameters](https://community.fabric.microsoft.com/t5/Mobile-Apps/URL-Query-string-parameters-in-QR-Code/m-p/692954)
- [Tracking QR codes with UTM parameters](https://www.mwrresourcecenter.com/resources/marketing/sponsorship/tracking-qr-codes-utm-parameters-analytics)

---

## Pattern 2: Tappable Name Cards (Replacing Radio Buttons)

### Table Stakes

| Feature | Why Expected | Implementation Notes |
|---------|--------------|---------------------|
| Minimum 44x44pt touch targets | WCAG 2.1 AAA requirement, iOS/Android standards | Size cards to 44px minimum height, full-width tap area |
| Visual selection feedback | Must be obvious which card is selected | Change background color, add border, or show checkmark icon |
| Single-tap selection | One tap selects, submits form | No separate "Confirm" button needed — tap and go |
| Keyboard navigation support | Tab through cards, Enter/Space to select | Cards must have `tabindex="0"`, `role="button"`, proper ARIA |
| Clear focus indicator | 3:1 contrast ratio for focused state | Visible outline when keyboard-focused, distinct from selected state |

**Touch Target Sizing Research:**
- **WCAG 2.2 minimum:** 24x24 CSS pixels (Level AA)
- **iOS guideline:** 44x44pt minimum
- **Android guideline:** 48x48dp minimum
- **Rage tap prevention:** 42-46px ideal (11-12mm physical size)
- **Context matters:** Top of screen needs 42px, bottom needs 46px, center can go to 27px

**Accessibility Requirements:**
- `role="button"` or `role="radio"` with `aria-checked="true/false"`
- `aria-label="Select {name}"` for each card
- Keyboard users can Tab through cards and press Enter or Space to select
- Screen readers announce: "Selected, {name}, button" or "Not selected, {name}, button"

### Differentiators

| Feature | Why Extraordinary | Complexity |
|---------|-------------------|------------|
| Anticipatory loading | Pre-load next screen during selection animation (200-300ms window) | Low |
| Haptic feedback on select | Subtle vibration confirms selection (iOS/Android Vibration API) | Low |
| Smart alphabetical grouping | Divide into A-M and N-Z sections for teams >12 members | Low |
| Recent participants first | Show last 3 session participants at top of list | Medium |
| Visual card animation | Subtle scale (1.0 → 0.98 → 1.02) and elevation change on tap | Low |
| Generous tap targets | 56px minimum height (exceeds standards), full-width cards with internal padding | Low |

**Why these matter:**
- Haptic feedback creates tangible confirmation — particularly valuable on silent devices
- Smart grouping reduces scrolling for large teams (15-25 members)
- Recent participants optimization handles the 80% use case (same people each month)
- Anticipatory loading makes navigation feel instantaneous

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Tiny avatar thumbnails | Creates small tap targets, fails WCAG | Use text-only cards or large avatar circles (44px+) |
| Horizontal scrolling cards | Awkward on mobile, easy to mis-tap | Vertical stack always, even for 3-5 names |
| Radio buttons on mobile | 24px targets are minimum, not optimal | Full-width tappable cards with 44-56px height |
| Multi-select appearance | Checkboxes imply multiple selection | Use radio button styling or single highlight |
| Confirmation dialog | "Are you sure you want to select {name}?" — unnecessary friction | Allow immediate undo with back button or "Not you?" link |

**Critical:** Cards must feel more responsive than radio buttons. Target tap-to-visual-feedback: <100ms.

### Sources

- [Touch target size - Android Accessibility](https://support.google.com/accessibility/android/answer/7101858?hl=en)
- [Accessible Target Sizes Cheatsheet - Smashing Magazine](https://www.smashingmagazine.com/2023/04/accessible-tap-target-sizes-rage-taps-clicks/)
- [WCAG 2.5.5: Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [WCAG 2.5.8: Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- [Chip UI Design - Mobbin](https://mobbin.com/glossary/chip)
- [Chips - Material Design 3](https://m3.material.io/components/chips)

---

## Pattern 3: Progressive Bullet Inputs (1 → Grows to 5)

### Table Stakes

| Feature | Why Expected | Implementation Notes |
|---------|--------------|---------------------|
| Start with 1 input field | Reduces cognitive load, feels manageable | Hide inputs 2-5 initially |
| Reveal next on input | As user types in field N, show field N+1 | Event listener on `input` event, show when `value.length > 0` |
| Max 5 fields total | Constraint maintains focus (from existing design) | Stop revealing after field 5 appears |
| Optional fields 2-5 | Only first bullet required | Clear placeholder: "Bullet point 1 (required)" vs "Bullet point 2 (optional)" |
| Preserve entered content | Don't lose bullets if user scrolls away | Auto-save to localStorage on input (existing draft pattern) |

**Progressive Disclosure Timing:**
- **Conditional reveal:** Show next field when previous has content (not when focused)
- **Immediate reveal:** Show within 100ms of input (no animation delay that feels sluggish)
- **Graceful handling:** If user deletes content from field N, keep field N+1 visible (don't hide aggressively)

### Differentiators

| Feature | Why Extraordinary | Complexity |
|---------|-------------------|------------|
| Slide-in animation | New field slides in from below with 200ms ease-out | Low |
| Auto-focus next field | After 3 characters in field N, soft focus field N+1 (don't steal cursor) | Medium |
| Smart placeholders | Show contextual prompts: "Another reason?", "What else?", "One more?" | Low |
| Character counter | Show "X/500" for active field only | Low |
| Collapse empty fields | On submit, only show filled bullets (hide empty 2-5) | Low |
| Visual progress indicator | Subtle "1 of 5 bullets" or dot indicator | Low |

**Why these matter:**
- Slide-in animation signals "you unlocked something" — creates sense of achievement
- Smart placeholders reduce mental effort ("what should I write?")
- Collapsing on submit creates clean final view, reinforces "you're done"
- Auto-focus prevents friction of manual tapping for rapid entry

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Show all 5 fields upfront | Intimidating, implies all required | Progressive disclosure: 1 → 2 → 3 → 4 → 5 |
| Aggressive auto-focus | Stealing cursor mid-typing frustrates users | Soft focus: show next field but let user finish current thought |
| "+Add Another" button | Extra tap creates friction | Auto-reveal on input (zero-click disclosure) |
| Removing fields when emptied | User might be editing, creates jarring experience | Keep revealed fields visible even if emptied |
| Tiny text areas | 500-char max needs comfortable input size | Single-line inputs work if font-size 16px+ (prevents iOS zoom) |
| Field numbering in input | "1.", "2." prefixes clutter the input | Number via label or visual indicator outside input |

**Critical:** Progressive disclosure should feel like encouragement, not interrogation. Never show more than 2 empty fields at once.

**Multi-Step Form Research:**
- Forms with progressive disclosure show 14% higher completion rates
- Users perceive multi-step forms as easier even when field count is identical
- Start with easy questions, build to harder ones (commitment bias)

### Sources

- [Form UI/UX Design Best Practices 2026](https://www.designstudiouiux.com/blog/form-ux-design-best-practices/)
- [Form Input Design Best Practices - UXPin](https://www.uxpin.com/studio/blog/form-input-design-best-practices/)
- [Progressive Disclosure in UX - LogRocket](https://blog.logrocket.com/ux-design/progressive-disclosure-ux-types-use-cases/)
- [Progressive Disclosure - NN/G](https://www.nngroup.com/articles/progressive-disclosure/)
- [54 Input Field Design Examples](https://www.eleken.co/blog-posts/input-field-design)

---

## Pattern 4: Live Progress Waiting Screen

### Table Stakes

| Feature | Why Expected | Implementation Notes |
|---------|--------------|---------------------|
| Show who has submitted | Names appear in "Submitted" section | Use existing polling endpoint, render names dynamically |
| Show who hasn't submitted | Names appear in "Waiting for" section | Inverse of submitted list |
| Real-time updates | Poll every 2-3 seconds for status changes | Use existing pattern from v2.0 |
| Spinner or progress indicator | System is working, not frozen | Subtle spinner during polls, progress bar showing N/M completed |
| Estimated time remaining | "Waiting for 3 more submissions" | Calculate from team size and submission count |

**Queue Psychology Principles:**
- **Certainty reduces anxiety:** Show concrete progress (7 of 12 submitted) not vague "please wait"
- **Movement reduces perceived time:** Updating names list reinforces "line is moving"
- **Transparency builds trust:** Users can see they're not alone in waiting

### Differentiators

| Feature | Why Extraordinary | Complexity |
|---------|-------------------|------------|
| Name check-in animation | When someone submits, their name moves from "Waiting" to "Submitted" with subtle slide animation | Low |
| Friendly micro-copy | "Nice! 9 of 12 done" or "Almost there — waiting for 2 more" | Low |
| No pressure messaging | Avoid "Hurry up!" or countdown timers | Critical |
| Celebratory moment | When last person submits: "Everyone's in! Analyzing responses..." | Low |
| Contextual content | Show tips or quotes while waiting (reduces perceived time) | Medium |
| Smooth state transition | When facilitator closes capture, seamlessly transition to "Analyzing..." (no page reload) | Medium |
| Exit valve | "Not you? Update your response" link for wrong submissions | Low |

**Why these matter:**
- Check-in animation creates dopamine hit as team completes task together
- Friendly micro-copy reduces social pressure (waiting feels like progress, not judgment)
- Contextual content makes wait feel productive (users learn something)
- Smooth transitions eliminate jarring "refresh to see results" moments

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Countdown timer | Creates pressure, anxiety, shame | Use "N of M submitted" progress indicator |
| "Waiting for: Bob, Alice, Charlie..." | Public shaming, creates social pressure | Show count only: "Waiting for 3 more" or use submitted list |
| Percentage complete | 33% feels slower than "4 of 12" | Use N/M format with names checking in |
| Aggressive polling | <1 second creates server load and battery drain | 2-3 second intervals sufficient |
| Empty waiting state | Spinner with no context creates anxiety | Show team context, instructions, or helpful content |
| Auto-refresh on complete | Jarring page reload breaks experience | WebSocket or smooth DOM update |

**Critical:** Research shows users presented with progress bars tolerate median wait of 22.6 seconds vs 9 seconds with no indicator. Names checking in extends this further.

**Anxiety Reduction Patterns:**
- Use visual progress + text status together (reduces obsessive checking)
- Communicate flexibility ("You can close this tab and return later")
- Show discrete start and end (not infinite spinner)

### Sources

- [Status Trackers and Progress Updates - NN/G](https://www.nngroup.com/articles/status-tracker-progress-update/)
- [How to Design Better Progress Trackers - UXPin](https://www.uxpin.com/studio/blog/design-progress-trackers/)
- [Loading & Progress Indicators - UX Collective](https://uxdesign.cc/loading-progress-indicators-ui-components-series-f4b1fc35339a)
- [Progress Bar UX Examples](https://bricxlabs.com/blogs/progress-bar-ux-examples)
- [Queue Psychology - Queue-it](https://queue-it.com/blog/custom-waiting-room-experience/)
- [UX of Waiting Rooms - Medium](https://medium.com/design-bootcamp/where-time-becomes-the-interface-4be910af599c)

---

## Pattern 5: Image Subset Browsing (~60 Images)

### Table Stakes

| Feature | Why Expected | Implementation Notes |
|---------|--------------|---------------------|
| 2-column grid on mobile | Optimal for image selection, large tap targets | CSS Grid: `grid-template-columns: repeat(2, 1fr)` |
| Lazy loading | Performance essential for 60+ images | `loading="lazy"` for images beyond first 6 |
| Pagination or infinite scroll | Can't show 60 images at once | Pagination preferred (predictable, easier back-navigation) |
| Visual selection indicator | Selected image has clear highlight | Border, scale, or overlay — must be 3:1 contrast |
| Images load progressively | First 6 load immediately (eager), rest lazy | `loading="eager"` for above-fold, `lazy` for rest |

**Mobile Image Grid Research:**
- **2-column grid:** Optimal for image selection with touch (larger tap targets than 3-4 columns)
- **4-column grid:** Standard for general mobile UI, but too small for image browsing
- **Lazy loading support:** 92%+ browser support in 2026
- **Image sizing:** 320-720px width range covers most mobile devices
- **Grid gap:** 8-16px provides comfortable spacing without wasting screen space

### Differentiators

| Feature | Why Extraordinary | Complexity |
|---------|-------------------|------------|
| Smart subset selection | 60 images from 200+ library, seeded by session_id (existing pattern) | Low |
| Session-consistent ordering | Same 60 images, same order throughout one session | Low |
| Optimal image sizing | ~150-200px per image (comfortable viewing + identification) | Low |
| Instant selection feedback | Image scales (1.0 → 1.05) and border appears <100ms after tap | Low |
| Sticky pagination controls | Prev/Next always visible at top (existing pattern) | Low |
| Jump to selection | "Jump to your selection" appears when browsing away from selected page | Low |
| Thumbnail preview | Selected image shows in small preview above bullets section | Low |
| Bento grid layout | Varying image sizes (some full-width) for visual interest | Medium |

**Why these matter:**
- Smart subset prevents decision paralysis (60 vs 200+ choices)
- Instant feedback eliminates "did my tap register?" uncertainty
- Jump to selection prevents lost selections during exploration
- Bento grid (varied sizes) more engaging than uniform grid

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Tiny thumbnails in 4-5 columns | Fails WCAG, can't see image detail | 2-column grid with 150-200px images |
| Infinite scroll | Hard to navigate back, poor performance on mobile | Pagination with clear page indicators |
| Loading all 200+ images | Poor performance, decision paralysis | Smart 60-image subset per session |
| Horizontal scrolling | Awkward on mobile, easy to mis-swipe | Vertical grid only |
| Auto-advancing pagination | User loses control, frustrating if reviewing | Manual Prev/Next only |
| Overlay selection checkmark | Obscures image content | Border + subtle scale instead |
| Text-based image names | "sunset_ocean_1234.jpg" is meaningless | Images only, no filenames shown |

**Critical:** Images must be large enough to identify content without full-screen view. Target: recognize image meaning in 2-column thumbnail.

**Lazy Loading Best Practices:**
- Don't lazy-load above-the-fold content (first 6 images)
- Use spinner or skeleton while loading below-fold images
- Provide fade-in effect when lazy-loaded images arrive
- Consider IntersectionObserver for advanced loading strategies

### Sources

- [Optimizing Images for Mobile - LogRocket](https://blog.logrocket.com/ux-design/optimizing-images-mobile-browsers-ux-mindset/)
- [Mobile Image Grids vs Text Lists - NN/G](https://www.nngroup.com/articles/image-vs-list-mobile-navigation/)
- [Why 4-Column Grids Work Best for Mobile - Medium](https://medium.com/@wardharaheem/why-4-columns-work-best-for-mobile-ui-841f95a9eb20)
- [Lazy Loading Image Gallery Tutorial](https://primeinspire.com/blog/lazy-loading-image-gallery-tutorial)
- [Mobile UX/UI Design Patterns 2026](https://www.sanjaydey.com/mobile-ux-ui-design-patterns-2026-data-backed/)
- [Responsive Grids Guide - UX Design Institute](https://www.uxdesigninstitute.com/blog/guide-to-responsive-grids/)

---

## Pattern 6: Meeting Projector View with Control Strip

### Table Stakes

| Feature | Why Expected | Implementation Notes |
|---------|--------------|---------------------|
| Bottom control strip | Facilitator controls visible, not obstructing content | Fixed position, 60-80px height |
| Large touch targets | Facilitator often clicks from distance or with stylus | 56px+ button height, generous padding |
| High contrast controls | Visible in bright meeting rooms | Dark background (#1d1d1f), white text, 4.5:1+ contrast |
| Clear labeling | "Close Capture", "Reveal Results" — no ambiguity | Button text + icon for redundancy |
| Responsive to projector aspect | Works at 16:9, 16:10, 4:3 ratios | Test at 1024x768, 1920x1080, 1280x800 |

**Meeting Room Considerations:**
- Projectors typically 3000-6500 lumens (very bright environments)
- Control strip must be visible from facilitator's laptop screen
- Large fonts (18-24px) for readability from distance
- Consider wireless presentation constraints (Miracast, AirPlay)

### Differentiators

| Feature | Why Extraordinary | Complexity |
|---------|-------------------|------------|
| Semi-transparent controls | Overlays content without completely obscuring | Medium |
| Auto-hide after inactivity | Strip fades out after 10s, reappears on mouse movement | Low |
| Keyboard shortcuts | Space = Close/Reveal, R = Reveal, C = Close | Low |
| Dual-screen support | Controls on laptop, content on projector (via CSS media query) | Medium |
| Undo/Reopen capture | "Oops, wrong button" recovery without page refresh | Low |
| Loading state in controls | "Synthesizing..." indicator in control strip itself | Low |
| Color-coded states | Green = Capturing, Yellow = Analyzing, Blue = Revealed | Low |

**Why these matter:**
- Auto-hide maximizes screen real estate for projected content
- Keyboard shortcuts enable facilitator to control from laptop without touching projected screen
- Dual-screen support allows facilitator-only view of controls
- Undo prevents panic if facilitator clicks prematurely

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Top control strip | Awkward for touch, blocks important content | Bottom fixed position |
| Small buttons | Hard to click from distance or with stylus | 56px+ touch targets |
| Hover-only controls | Doesn't work with touch screens or stylus | Always visible or tap-to-reveal |
| Complex menus | Dropdown/nested controls slow facilitator | Flat, single-level controls only |
| Participant-visible controls | Creates confusion, breaks facilitation flow | Hide controls on participant phones |
| Auto-transitions without control | Facilitator loses ceremony control | Always require explicit "Reveal" action |

**Critical:** Control strip must be operable with one hand, from 3-6 feet away, in bright lighting. Test with non-mouse input (stylus, touch screen).

**Note:** Limited specific 2026 research found for projector control UIs. Recommendations based on general meeting room technology trends and touch interface guidelines.

### Sources

- [Meeting Room Projectors - Epson](https://epson.com/For-Work/Projectors/Meeting-Room/c/w320)
- [Best Meeting Room Tech 2026 - Awaio](https://awaio.com/meeting-room-technology/)
- [Touch Target Size Guidelines](https://www.smashingmagazine.com/2023/04/accessible-tap-target-sizes-rage-taps-clicks/) (applied to projector context)

---

## Pattern 7: Auto-Synthesize and Auto-Reveal

### Table Stakes

| Feature | Why Expected | Implementation Notes |
|---------|--------------|---------------------|
| Background processing | Synthesis happens without blocking UI | Async API call when capture closed |
| Clear status indicator | "Analyzing responses..." with spinner | Use existing polling pattern |
| Error handling | If synthesis fails, show retry option | Existing error UI from v2.1 |
| Completion notification | System indicates when synthesis ready | Facilitator view updates, participants poll |
| Manual reveal option | Facilitator decides when to show results | "Reveal Results" button remains |

**Auto-Triggering Patterns:**
- **Close Capture → Synthesize:** Immediately trigger Claude API call
- **Synthesis Complete → Reveal:** Option to auto-reveal OR require facilitator action
- **User Action → Background Task:** Close capture is user action, synthesis is background
- **Background Complete → Notify:** Update facilitator view, send signal to participant phones

### Differentiators

| Feature | Why Extraordinary | Complexity |
|---------|-------------------|------------|
| Optimistic UI | Immediately show "Analyzing..." state before synthesis starts | Low |
| Progress estimation | "Analyzing... typically takes 30-60 seconds" | Low |
| Facilitator preview | Show synthesis to facilitator before revealing to room | Medium |
| Auto-reveal with confirmation | "Synthesis ready. Reveal now?" modal with 5s auto-reveal timer | Medium |
| Retry with escalation | First retry uses same prompt, second retry uses fallback prompt | Medium |
| Partial results handling | If synthesis times out, show what's available + retry option | High |
| Contextual animations | Projected view shows subtle motion during analysis (reinforces "working") | Low |

**Why these matter:**
- Optimistic UI eliminates perceived delay between button click and action
- Facilitator preview prevents surprises (review before room sees it)
- Auto-reveal with confirmation balances automation with control
- Contextual animations keep room engaged during 30-60s wait

### Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Silent auto-reveal | Facilitator loses ceremony control | Require explicit "Reveal" or auto-reveal with confirmation |
| Blocking synthesis | "Please wait..." spinner locks entire UI | Background task, show progress but allow navigation |
| No retry option | Single failure means manual intervention | Automatic retry (3 attempts) before showing error |
| Vague progress | "Processing..." with no time estimate | "Analyzing... typically takes 30-60 seconds" |
| Immediate error display | Synthesis fails, shows error to participants | Show error to facilitator only, hide from participants |
| Auto-restart on error | Infinite retry loop drains API credits | Max 3 retries, then manual intervention required |

**Critical:** Auto-triggering must feel like intelligent assistance, not loss of control. Facilitator always has final say on reveal timing.

**Background Process Feedback Patterns (2026):**
- 77% of users abandon apps within 3 days if UX feels broken — feedback is critical
- Micro-interactions bridge gap between action and system response
- Non-time-critical work delegated to background, main process stays responsive
- Interfaces in 2026 emphasize "feeling alive" with motion, texture, subtle feedback

### Sources

- [7 Mobile UX/UI Design Patterns 2026](https://www.sanjaydey.com/mobile-ux-ui-design-patterns-2026-data-backed/)
- [AI Workflow Automation Trends 2026 - Kissflow](https://kissflow.com/workflow/7-workflow-automation-trends-every-it-leader-must-watch-in-2025/)
- [Customer Feedback Strategies 2026 - Qualaroo](https://qualaroo.com/blog/customer-feedback-saas/)
- [Background Process Handling - Android](https://source.android.com/docs/automotive/users_accounts/user_system)

---

## Cross-Pattern Design Principles

### Animation & Transition Standards

| Pattern | Duration | Easing | Purpose |
|---------|----------|--------|---------|
| Card selection | 200ms | ease-out | Confirm tap registered |
| Field reveal | 200-300ms | ease-out | Signal new content available |
| Name check-in | 300ms | ease-in-out | Celebrate progress |
| Image selection | 100ms | linear | Instant feedback |
| Control strip auto-hide | 300ms | ease-in | Graceful disappearance |
| Page transitions | 250ms | ease-in-out | Smooth navigation |

**Performance Target:** All animations must run at 60fps on 3-year-old Android devices. Use CSS `transform` and `opacity` only (GPU-accelerated).

### Accessibility Checklist

- [ ] All interactive elements ≥44px touch targets (preferably 56px)
- [ ] Keyboard navigation works for all interactions (Tab, Enter, Space)
- [ ] Focus indicators visible (3:1 contrast ratio minimum)
- [ ] Screen reader announcements for state changes
- [ ] Color-independent status indicators (use icons + text)
- [ ] Motion can be disabled via `prefers-reduced-motion`
- [ ] Error messages announced to assistive tech
- [ ] Skip links for long content sections

### Mobile Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial page load | <2s | Time to interactive |
| Tap to visual feedback | <100ms | Animation start |
| Auto-join (QR → name picker) | <2s | Full page render |
| Image lazy load | <500ms | Per batch |
| Polling interval | 2-3s | Status updates |
| Progressive field reveal | <100ms | Field appears |

### Error Recovery Patterns

| Error State | User Experience | Implementation |
|-------------|-----------------|----------------|
| Invalid QR code | Redirect to join page with error message | Show fuzzy matches if available |
| Network failure during submission | Show retry button, preserve draft | localStorage backup |
| Synthesis timeout | Facilitator sees error + retry, participants wait | Max 3 auto-retries |
| Image load failure | Show placeholder + retry button | Graceful degradation |
| Session closed while responding | "Session closed. Your response wasn't submitted." | Clear message, offer contact info |

---

## Implementation Priority Matrix

### Phase 1: Core Interactions (Week 1)

| Feature | Impact | Complexity | Priority |
|---------|--------|------------|----------|
| Auto-join from QR | High | Low | P0 |
| Tappable name cards | High | Low | P0 |
| 2-column image grid | High | Low | P0 |
| Progressive bullet inputs | High | Medium | P0 |

### Phase 2: Polish (Week 2)

| Feature | Impact | Complexity | Priority |
|---------|--------|------------|----------|
| Selection animations | Medium | Low | P1 |
| Live progress waiting screen | High | Medium | P1 |
| Bottom control strip | High | Low | P1 |
| Auto-synthesize trigger | High | Low | P1 |

### Phase 3: Delight (Week 3)

| Feature | Impact | Complexity | Priority |
|---------|--------|------------|----------|
| Haptic feedback | Low | Low | P2 |
| Name check-in animations | Medium | Low | P2 |
| Smart placeholders | Low | Low | P2 |
| Facilitator preview | Medium | Medium | P2 |
| Auto-reveal with confirmation | Medium | Medium | P2 |

### Deferred to Post-v2.4

| Feature | Why Defer | Revisit When |
|---------|-----------|--------------|
| Bento grid layout | Complex, lower impact | v2.5+ if user feedback requests |
| Dual-screen support | Limited use case | v2.5+ if facilitators request |
| Contextual tips during wait | Content creation required | v2.5+ with curated content |
| Smart alphabetical grouping | Only needed for teams >12 | Wait for real usage data |

---

## Quality Gates for v2.4

### Functional Requirements

- [ ] QR scan lands on correct screen (join or name picker) in <2s
- [ ] Name cards work with touch, keyboard, and screen reader
- [ ] Progressive bullets reveal smoothly, preserve drafts
- [ ] Live progress updates every 2-3s, shows names checking in
- [ ] Image grid loads progressively, selection is instant
- [ ] Control strip visible and operable from facilitator position
- [ ] Auto-synthesize triggers on close, shows clear progress

### Performance Requirements

- [ ] Lighthouse Mobile score ≥90
- [ ] Tap to visual feedback <100ms for all interactions
- [ ] All animations run at 60fps on 3-year-old devices
- [ ] Image lazy loading works (first 6 eager, rest lazy)
- [ ] Progressive field reveal <100ms

### Accessibility Requirements

- [ ] WCAG 2.1 AA compliance (minimum)
- [ ] All touch targets ≥44px (preferably 56px)
- [ ] Keyboard navigation complete
- [ ] Screen reader tested (iOS VoiceOver + Android TalkBack)
- [ ] Color-independent status indicators

### UX Quality Requirements

- [ ] Zero-friction QR join (no intermediate screens)
- [ ] Name selection feels faster than radio buttons
- [ ] Bullet inputs feel encouraging, not interrogating
- [ ] Waiting screen reduces anxiety (no public shaming)
- [ ] Image browsing feels responsive and discoverable
- [ ] Control strip doesn't obstruct projected content
- [ ] Auto-synthesize feels like intelligent assistance

---

## Known Gaps & Future Research

### Areas Requiring Phase-Specific Research

| Topic | Why Uncertain | When to Research |
|-------|---------------|------------------|
| Optimal image subset size | 60 is estimate, may need tuning | After 10+ sessions with analytics |
| Auto-reveal vs manual reveal | User preference unknown | A/B test in v2.5 |
| Bottom vs top control strip | Limited projector UI research | User testing with facilitators |
| Haptic feedback value | May annoy some users | Optional feature, gather feedback |
| Waiting screen content | Tips vs quotes vs blank | Content strategy phase |

### Technical Unknowns

- **QR code reliability across devices:** Test matrix needed (iOS Camera, Android Lens, WeChat, Line, WhatsApp QR scanners)
- **Projector aspect ratio support:** Need real-world testing at various meeting rooms
- **Mobile browser differences:** Haptic API support varies (iOS Safari vs Android Chrome vs Samsung Internet)
- **Lazy loading edge cases:** IntersectionObserver support on older devices

### Design Validation Needed

- **Tappable cards vs radio buttons:** A/B test completion rates
- **Progressive bullets completion:** Do users submit more/better content with progressive disclosure?
- **Waiting screen anxiety:** Measure via survey after sessions
- **Control strip discoverability:** Can facilitators find controls without training?

---

## Success Metrics for v2.4

### Quantitative Metrics

| Metric | Current (v2.3) | Target (v2.4) | Measurement |
|--------|----------------|---------------|-------------|
| Time from QR scan to submission | ~120s (7 screens) | <60s (4 screens) | Session analytics |
| Submission completion rate | ~85% | >90% | Completed vs started |
| Average bullets per response | ~2.3 | >2.5 | Response data |
| Facilitator actions per session | 4 (draft → capture → close → reveal) | 2 (close → reveal) | Click tracking |
| Mobile Lighthouse score | 87 | >90 | Automated testing |

### Qualitative Metrics

| Metric | Measurement Method | Target |
|--------|-------------------|--------|
| "Feels polished" perception | Post-session survey | >80% agree |
| "Easier than last month" | Returning participant survey | >70% agree |
| Facilitator confidence | Facilitator interview | No training needed |
| Accessibility satisfaction | Screen reader user testing | Zero blockers |

### Leading Indicators

- QR scans vs manual entry ratio (target: >70% QR)
- Name card selection time (target: <5s)
- Bullet field completion (target: 40%+ use 3+ bullets)
- Waiting screen engagement (target: <10% refresh rate)
- Image selection time (target: <30s)

---

## Final Recommendation

**Build all patterns.** Each addresses real friction in current flow:

1. **Auto-join** eliminates unnecessary screen
2. **Tappable cards** modernizes name selection
3. **Progressive bullets** encourages richer responses
4. **Live progress** reduces anxiety
5. **Image subset** improves performance and decision-making
6. **Control strip** streamlines facilitator actions
7. **Auto-synthesize** reduces manual steps

**Total effort:** ~3 weeks (based on v2.0-v2.3 velocity)

**Confidence:** HIGH for patterns 1-5 (mobile UX), MEDIUM for pattern 6 (projector UI — limited research)

**Risk mitigation:**
- Feature flag auto-reveal (allow manual toggle)
- Provide keyboard shortcuts for control strip (accessibility + power users)
- A/B test progressive bullets vs fixed 5 fields (measure completion)
- Monitor QR scan success rate (may need QR code size/placement tuning)

**Expected outcome:** Session flow that feels effortless, intentional, and polished — every remaining interaction serves clear purpose, executed with modern mobile UX standards.
