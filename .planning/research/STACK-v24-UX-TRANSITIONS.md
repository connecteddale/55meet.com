# Technology Stack: UX Refinement (Page Transitions & Animations)

**Project:** The 55 App
**Researched:** 2026-01-24
**Confidence:** HIGH
**Focus:** Page transitions, progressive inputs, selection animations for existing FastAPI/Jinja2/vanilla JS stack

## Executive Summary

This stack research focuses exclusively on CSS/JS techniques for smooth multi-page transitions, progressive disclosure inputs, and subtle animations WITHOUT requiring a build step or SPA framework. The 55 App uses server-rendered FastAPI/Jinja2 pages with vanilla JavaScript, and this research identifies modern browser APIs that enable SPA-like experiences while maintaining that architecture.

**Key Finding:** View Transitions API for cross-document (multi-page) transitions is now production-ready in Chrome 126+, Safari 18+, and Firefox 144+ (85%+ browser coverage as of 2026). Combined with @starting-style and transition-behavior (Baseline 2024), these enable smooth page-to-page navigation, progressive inputs, and selection feedback entirely through CSS with JavaScript progressive enhancement.

## Recommended Stack

### Core Animation APIs

| Technology | Version/Status | Purpose | Why |
|------------|---------------|---------|-----|
| **View Transitions API** | Chrome 126+, Safari 18+, Firefox 144+ | Cross-document page transitions | Native browser support for SPA-like navigation between server-rendered pages with zero JavaScript required for basic fade/slide |
| **@starting-style** | Baseline 2024 (Aug 2024) | Entry animations for progressive disclosure | Enables CSS-only transitions on first render and display: none → visible changes |
| **transition-behavior: allow-discrete** | Baseline 2024 (Aug 2024) | Display property transitions | Allows smooth transitions of discrete properties like display, making progressive inputs purely CSS |
| **Intersection Observer API** | Baseline 2019 (widely available) | Scroll-based reveals, lazy loading | Async, main-thread-efficient detection of element visibility for staggered animations |
| **CSS Transforms & Transitions** | Universal support | Selection feedback animations | Hardware-accelerated scale, border, and opacity changes for touch feedback |
| **Fisher-Yates Shuffle** | Vanilla JS algorithm | Random image subset selection | O(n) performance for selecting 60 from 200+ images, statistically unbiased |

### Browser Support Matrix (2026)

| API | Chrome/Edge | Safari | Firefox | Mobile Support | Fallback Required |
|-----|-------------|--------|---------|----------------|-------------------|
| View Transitions (cross-doc) | 126+ ✓ | 18+ ✓ | 144+ ✓ | iOS 18+, Android Chrome 126+ | YES - graceful degradation |
| @starting-style | 117+ ✓ | 17.4+ ✓ | 129+ ✓ | Full mobile support | NO - progressive enhancement |
| transition-behavior | 117+ ✓ | 17.4+ ✓ | 129+ ✓ | Full mobile support | NO - progressive enhancement |
| Intersection Observer | 51+ ✓ | 12.1+ ✓ | 55+ ✓ | Universal mobile support | NO - 97%+ coverage |
| CSS Container Queries | 105+ ✓ | 16+ ✓ | 110+ ✓ | 93.92% browser support | Optional - use for card grids |

**Coverage:** 85%+ for View Transitions, 95%+ for other features. Remaining 15% get functional fallback (instant page loads, no animations).

## Implementation Guide

### 1. Cross-Document Page Transitions

**Purpose:** Smooth fade/slide between server-rendered pages (scan → pick name → browse images → results)

**Implementation:**

```css
/* Add to global stylesheet - both pages opt-in */
@view-transition {
  navigation: auto;
}

/* Customize animation (optional) */
::view-transition-old(root) {
  animation: 300ms ease-out fade-out;
}

::view-transition-new(root) {
  animation: 300ms ease-in fade-in;
}

@keyframes fade-out {
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
}

/* Slide animation for forward navigation */
@view-transition {
  types: slide;
}

html.forward::view-transition-old(root) {
  animation: 300ms ease-out slide-out-left;
}

html.forward::view-transition-new(root) {
  animation: 300ms ease-in slide-in-right;
}
```

**JavaScript (Progressive Enhancement):**

```javascript
// Feature detection - set navigation direction class
if (document.startViewTransition) {
  // Optional: add direction hints to <html> for custom animations
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href]');
    if (link && link.href.includes('next-step')) {
      document.documentElement.classList.add('forward');
    }
  });
}

// Fallback: browsers without support just navigate normally (instant)
```

**Fallback Strategy:**
- Browsers without View Transitions API: instant page load (current behavior)
- No JavaScript errors, no polyfills needed
- Progressive enhancement approach

**Performance Notes:**
- 4-second timeout: transitions exceeding this are skipped with TimeoutError
- Keep animations under 300ms for mobile
- Avoid blocking render unless critical elements needed

**Sources:**
- [View Transition API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)
- [Cross-document view transitions - Chrome Developers](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document)
- [View Transitions API browser support - Can I Use](https://caniuse.com/view-transitions)
- [View Transitions misconceptions - Chrome Blog](https://developer.chrome.com/blog/view-transitions-misconceptions)

### 2. Progressive Disclosure Input Fields

**Purpose:** Grow participant input fields from 1 to 5 as user fills them (waiting screen → results transition)

**Implementation:**

```css
/* Container setup */
.participant-inputs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Input field base styles */
.participant-input {
  opacity: 1;
  transform: scale(1);
  display: block;
  transition:
    opacity 0.3s ease-out,
    transform 0.3s ease-out,
    display 0.3s allow-discrete;

  /* Smooth height change */
  max-height: 60px;
  transition: max-height 0.3s ease-out;
}

/* Starting state for hidden inputs */
@starting-style {
  .participant-input {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
}

/* Hidden state */
.participant-input.hidden {
  display: none;
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

/* Show next input when previous has :valid */
.participant-input:valid + .participant-input.hidden {
  display: block;
}
```

**JavaScript (Progressive Enhancement):**

```javascript
// Optional: Add classes for better control
document.querySelectorAll('.participant-input').forEach((input, index) => {
  if (index > 0) input.classList.add('hidden');

  input.addEventListener('input', () => {
    if (input.value.trim().length > 0) {
      const nextInput = input.nextElementSibling;
      if (nextInput?.classList.contains('hidden')) {
        nextInput.classList.remove('hidden');
      }
    }
  });
});
```

**Alternative: Pure CSS with :has() selector (2026)**

```css
/* Modern approach using :has() */
.participant-inputs:has(.input-1:valid) .input-2 { display: block; }
.participant-inputs:has(.input-2:valid) .input-3 { display: block; }
.participant-inputs:has(.input-3:valid) .input-4 { display: block; }
.participant-inputs:has(.input-4:valid) .input-5 { display: block; }
```

**Fallback Strategy:**
- Without @starting-style: inputs appear instantly (no animation)
- Without transition-behavior: display changes snap (no fade)
- All browsers: inputs still show/hide correctly

**Sources:**
- [@starting-style - MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@starting-style)
- [transition-behavior - MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/transition-behavior)
- [Baseline: animating entry effects - web.dev](https://web.dev/blog/baseline-entry-animations)
- [Progressive Disclosure with CSS - Silo Creativo](https://www.silocreativo.com/en/progressive-disclosure-with-css/)

### 3. Selection Feedback Animations

**Purpose:** Scale + border animations for image/name selection on mobile (touch-friendly)

**Implementation:**

```css
/* Card/chip base styles */
.selectable-card {
  position: relative;
  border: 2px solid transparent;
  border-radius: 8px;
  transition:
    transform 0.15s ease-out,
    border-color 0.15s ease-out,
    box-shadow 0.15s ease-out;
  cursor: pointer;

  /* Touch-friendly sizing (min 44×44px iOS) */
  min-height: 44px;
  min-width: 44px;
}

/* Active state (touch feedback) */
.selectable-card:active {
  transform: scale(0.97);
}

/* Selected state */
.selectable-card.selected {
  border-color: var(--accent-color);
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Hover for desktop (avoid on touch) */
@media (hover: hover) and (pointer: fine) {
  .selectable-card:hover {
    transform: scale(1.01);
    border-color: var(--accent-color-light);
  }
}

/* Remove sticky hover on touch devices */
@media (hover: none) and (pointer: coarse) {
  .selectable-card:hover {
    transform: none;
    border-color: transparent;
  }
}
```

**JavaScript (State Management):**

```javascript
// Toggle selection on tap
document.querySelectorAll('.selectable-card').forEach(card => {
  card.addEventListener('click', (e) => {
    // Remove from others if single-select
    if (card.dataset.singleSelect === 'true') {
      document.querySelectorAll('.selectable-card.selected')
        .forEach(c => c.classList.remove('selected'));
    }

    // Toggle this card
    card.classList.toggle('selected');

    // Optional: haptic feedback on mobile
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  });
});
```

**Mobile-Specific Considerations:**
- Use @media (hover: hover) to avoid sticky hover states on touch
- Min 44×44px touch targets (iOS Human Interface Guidelines)
- Keep animations under 150ms for instant feel
- Use transform/opacity for hardware acceleration
- Test on 375px viewport (iPhone SE baseline)

**Fallback Strategy:**
- All browsers: selection state works (border/color change)
- Older browsers: animations snap instead of smooth
- No JavaScript: visual feedback still works with CSS :active

**Sources:**
- [Handle Hover on Mobile - Lexo](https://www.lexo.ch/blog/2024/12/handling-hover-on-mobile-devices-with-html-css-and-javascript/)
- [CSS hover on touch screens - Medium](https://arturocreates.medium.com/handle-hover-css-on-mobile-touch-screen-69142ea79fe7)
- [CSS Border Animation Examples - WP Dean](https://wpdean.com/css-border-animation/)
- [CSS Transitions - MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_transitions/Using_CSS_transitions)

### 4. Smooth Waiting → Results Transition

**Purpose:** Poll for completion, replace content smoothly without hard redirect

**Implementation:**

```javascript
// Polling with View Transitions
async function pollForResults(sessionId) {
  const pollInterval = 2500; // Match existing 2.5s interval

  const poll = async () => {
    try {
      const response = await fetch(`/api/session/${sessionId}/status`);
      const data = await response.json();

      if (data.status === 'complete') {
        // Smooth transition to results
        await transitionToResults(sessionId);
        return; // Stop polling
      }

      // Update live participant list
      updateParticipantList(data.participants);

      // Continue polling
      setTimeout(poll, pollInterval);

    } catch (error) {
      console.error('Polling error:', error);
      setTimeout(poll, pollInterval); // Retry
    }
  };

  poll();
}

// Transition to results with View Transitions API
async function transitionToResults(sessionId) {
  const resultsUrl = `/session/${sessionId}/results`;

  // Feature detection
  if (document.startViewTransition) {
    // Use View Transitions API
    document.startViewTransition(async () => {
      const response = await fetch(resultsUrl);
      const html = await response.text();

      // Parse and extract body content
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newContent = doc.body.innerHTML;

      // Replace content
      document.body.innerHTML = newContent;

      // Re-run scripts if needed
      initializeResults();
    });
  } else {
    // Fallback: direct navigation
    window.location.href = resultsUrl;
  }
}

// Update participant list without transition
function updateParticipantList(participants) {
  const list = document.getElementById('participant-list');

  participants.forEach(p => {
    const existing = list.querySelector(`[data-id="${p.id}"]`);
    if (!existing && p.checked_in) {
      // New participant - add with animation
      const item = document.createElement('div');
      item.className = 'participant-item';
      item.dataset.id = p.id;
      item.textContent = p.name;

      // Will animate in via @starting-style
      list.appendChild(item);
    }
  });
}
```

**Alternative: Server-Sent Events (SSE) instead of Polling**

```javascript
// More efficient for one-way server→client updates
const eventSource = new EventSource(`/api/session/${sessionId}/stream`);

eventSource.addEventListener('participant_joined', (e) => {
  const data = JSON.parse(e.data);
  updateParticipantList([data]);
});

eventSource.addEventListener('session_complete', async (e) => {
  eventSource.close();
  await transitionToResults(sessionId);
});
```

**Fallback Strategy:**
- No View Transitions API: hard redirect to results (current behavior)
- No EventSource: polling still works universally
- Progressive enhancement at every level

**Performance Notes:**
- Keep polling interval at 2.5s (current rate)
- SSE is more efficient but requires server changes
- Close EventSource when navigating away

**Sources:**
- [Real-time Updates: Polling, SSE and WebSockets - DEV](https://dev.to/thesanjeevsharma/real-time-updates-polling-sse-and-web-sockets-277i)
- [Page Transitions in Vanilla JavaScript - Medium](https://medium.com/@dylanconnor4/page-transitions-in-vanilla-javascript-d71f4331dcf6)
- [Modern JavaScript Polling - Medium](https://medium.com/tech-pulse-by-collatzinc/modern-javascript-polling-adaptive-strategies-that-actually-work-part-1-9909f5946730)

### 5. Intersection Observer for Scroll Reveals

**Purpose:** Stagger image grid animations as user scrolls (200+ images, reveal as they enter viewport)

**Implementation:**

```javascript
// Setup observer with early trigger
const imageObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Add reveal class (CSS handles animation)
        entry.target.classList.add('revealed');

        // Optional: lazy load image if using data-src
        if (entry.target.dataset.src) {
          entry.target.src = entry.target.dataset.src;
        }

        // Stop observing (one-time animation)
        imageObserver.unobserve(entry.target);
      }
    });
  },
  {
    root: null, // viewport
    rootMargin: '50px 0px', // trigger 50px before entering viewport
    threshold: 0.1 // 10% visible
  }
);

// Observe all image cards
document.querySelectorAll('.image-card').forEach((card, index) => {
  // Stagger delay based on position
  card.style.transitionDelay = `${index * 0.03}s`;
  imageObserver.observe(card);
});
```

**CSS Animation:**

```css
/* Initial hidden state */
.image-card {
  opacity: 0;
  transform: translateY(20px);
  transition:
    opacity 0.4s ease-out,
    transform 0.4s ease-out;
}

/* Revealed state */
.image-card.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  .image-card {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
```

**Performance Benefits:**
- 43% more main thread availability vs scroll listeners (on slow mobile)
- Async operation, no layout thrashing
- Single observer for multiple elements
- No getBoundingClientRect() calls

**Fallback Strategy:**
- Without Intersection Observer: images load immediately, no stagger
- 97%+ browser support means fallback rarely needed
- Polyfill available for legacy browsers (not recommended for 2026)

**Sources:**
- [Intersection Observer API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [Mastering Intersection Observer API 2026 - Future Forem](https://future.forem.com/sherry_walker_bba406fb339/mastering-the-intersection-observer-api-2026-a-complete-guide-561k)
- [Scroll listener vs Intersection Observer performance - ITNEXT](https://itnext.io/1v1-scroll-listener-vs-intersection-observers-469a26ab9eb6)

### 6. Name Picker Card Grid

**Purpose:** Tappable name cards in responsive grid (375px mobile-first)

**Implementation:**

```css
/* Mobile-first grid (375px baseline) */
.name-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  padding: 1rem;

  /* Tablet+ */
  @media (min-width: 640px) {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1.5rem;
  }

  /* Desktop */
  @media (min-width: 1024px) {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

/* Name card */
.name-card {
  aspect-ratio: 3 / 2;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;

  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 12px;

  font-size: clamp(0.875rem, 1vw + 0.5rem, 1.125rem);
  font-weight: 500;
  text-align: center;

  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;

  /* Touch feedback */
  transition:
    transform 0.15s ease-out,
    border-color 0.15s ease-out,
    background-color 0.15s ease-out;
}

/* Active/selected states (from section 3) */
```

**Optional: Container Queries (2026)**

```css
/* More granular control - component-responsive */
.name-grid {
  container-type: inline-size;
  container-name: name-grid;
}

@container name-grid (min-width: 500px) {
  .name-card {
    aspect-ratio: 4 / 3;
    font-size: 1.125rem;
  }
}
```

**Fallback Strategy:**
- Container queries not supported: falls back to media queries
- Grid auto-fit ensures responsive at any viewport
- Works from 320px to 4K displays

**Sources:**
- [CSS Grid Masterclass 2025 - FrontendTools](https://www.frontendtools.tech/blog/mastering-css-grid-2025)
- [Responsive Design Best Practices 2026 - PxlPeak](https://pxlpeak.com/blog/web-design/responsive-design-best-practices)
- [Container queries 2026 - LogRocket](https://blog.logrocket.com/container-queries-2026/)
- [Look Ma, No Media Queries! - CSS-Tricks](https://css-tricks.com/look-ma-no-media-queries-responsive-layouts-using-css-grid/)

### 7. Random Image Subset Selection

**Purpose:** Select ~60 random images from 200+ image pool

**Implementation:**

```javascript
/**
 * Fisher-Yates shuffle - O(n) performance, statistically unbiased
 * Better than Array.sort(() => Math.random() - 0.5) which is O(n log n) and biased
 */
function getRandomSubset(array, count) {
  // Clone array to avoid mutating original
  const shuffled = [...array];

  // Fisher-Yates shuffle (in-place)
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }

  // Return first N elements
  return shuffled.slice(0, count);
}

// Usage: select 60 from 200+ images
const allImages = [/* 200+ image objects */];
const selectedImages = getRandomSubset(allImages, 60);
```

**Alternative: Optimized for Large Arrays**

```javascript
/**
 * Partial Fisher-Yates - only shuffle what we need
 * More efficient when selecting small subset from large array
 */
function getRandomSubsetOptimized(array, count) {
  const result = [];
  const used = new Set();

  while (result.length < count) {
    const index = Math.floor(Math.random() * array.length);
    if (!used.has(index)) {
      used.add(index);
      result.push(array[index]);
    }
  }

  return result;
}
```

**Server-Side vs Client-Side:**

```javascript
// Option 1: Server-side selection (recommended for consistency)
// FastAPI route returns 60 pre-selected images

// Option 2: Client-side selection (more dynamic, per-user variety)
fetch('/api/images/all')
  .then(res => res.json())
  .then(images => {
    const subset = getRandomSubset(images, 60);
    renderImageGrid(subset);
  });
```

**Performance Characteristics:**
- Fisher-Yates: O(n) time, O(n) space
- Optimized partial: O(k) where k = selection count
- For 60 from 200: both are ~instant (<1ms)
- Fisher-Yates recommended for statistical purity

**Fallback Strategy:**
- All browsers support this (ES6+ spread, destructuring)
- No polyfills needed
- Vanilla JavaScript, no dependencies

**Sources:**
- [Sampling, shuffling and weighted selection - 30 Seconds of Code](https://www.30secondsofcode.org/js/s/array-sample-shuffle-weighted-selection/)
- [How to shuffle an array in JavaScript - DEV](https://dev.to/codebubb/how-to-shuffle-an-array-in-javascript-2ikj)
- [Shuffling Arrays in JavaScript - Stack Abuse](https://stackabuse.com/shuffling-arrays-in-javascript/)

## Alternatives Considered (and Rejected)

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Page Transitions | View Transitions API | Barba.js, Swup | Requires build tools, unnecessary library weight when native API exists |
| Animation | CSS Transitions | GSAP, Anime.js | Build tools, 50KB+ overhead for simple scale/fade animations |
| Component Framework | Vanilla JS | Alpine.js, Petite Vue | Adds dependency, violates no-framework constraint |
| Build Tools | None | Vite, esbuild | Not needed for native ES6+ modules and modern CSS |
| Polling | Native fetch + setTimeout | Socket.io | WebSocket overkill for 2.5s polling; SSE better alternative if needed |
| Grid Layout | CSS Grid | Flexbox only | Grid better for 2D card layouts, has universal support |

## Anti-Patterns to Avoid

### 1. jQuery for Animation
**Why bad:** 20KB+ for features now native in CSS/JS
**Instead:** Use CSS transitions with vanilla JS class toggles

### 2. Sort-Based Shuffle
```javascript
// BAD: Biased, O(n log n) performance
array.sort(() => Math.random() - 0.5);

// GOOD: Fisher-Yates, O(n), unbiased
// (see implementation above)
```

### 3. Scroll Listeners for Visibility
```javascript
// BAD: Main thread blocking, layout thrashing
window.addEventListener('scroll', () => {
  elements.forEach(el => {
    if (el.getBoundingClientRect().top < window.innerHeight) {
      el.classList.add('visible');
    }
  });
});

// GOOD: Intersection Observer
// (see implementation above)
```

### 4. Hover States on Mobile
```css
/* BAD: Sticky hover on touch devices */
.card:hover {
  transform: scale(1.05);
}

/* GOOD: Desktop-only hover */
@media (hover: hover) and (pointer: fine) {
  .card:hover {
    transform: scale(1.05);
  }
}
```

### 5. Hard-Coded Breakpoints
```css
/* BAD: Fixed breakpoints, many media queries */
@media (max-width: 768px) { /* ... */ }
@media (max-width: 992px) { /* ... */ }

/* GOOD: Auto-responsive grid */
.grid {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}
```

## Integration with Existing Stack

### FastAPI Backend
- No changes required for View Transitions API
- Optional: Add SSE endpoint for real-time updates instead of polling
- Random image selection can be server-side (recommended) or client-side

### Jinja2 Templates
- Add `@view-transition { navigation: auto; }` to base.css
- Add data attributes for progressive disclosure (data-src for lazy loading)
- No template restructuring required

### Vanilla JavaScript
- Feature detection wrappers: `if (document.startViewTransition)`
- Progressive enhancement: features layer on top of working base
- No modules/imports needed: all inline or simple script tags

### CSS Design System
- Leverage existing CSS custom properties for animation colors
- Use Inter font stack (already loaded)
- Match existing clamp() typography approach
- Apple-inspired timing: ease-out (0.15-0.3s) for interactions

### Polling Architecture
- Keep existing 2.5s interval
- Enhance with View Transitions when available
- Consider SSE upgrade in future milestone (not required now)

## Installation

**NO INSTALLATION REQUIRED** - All features are native browser APIs.

### Optional: Feature Detection Utility

```javascript
// Add to main.js (vanilla, no build)
const features = {
  viewTransitions: 'startViewTransition' in document,
  intersectionObserver: 'IntersectionObserver' in window,
  containerQueries: CSS.supports('container-type', 'inline-size'),
  startingStyle: CSS.supports('@starting-style')
};

// Log for debugging
console.log('Feature support:', features);

// Export for use in components
window.AppFeatures = features;
```

### HTML Meta Tags

```html
<!-- Optimize for mobile (existing, confirm present) -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#007aff">
<meta name="apple-mobile-web-app-capable" content="yes">
```

### CSS Entry Point

```css
/* Add to base.css or main.css */
@import url('animations.css'); /* New file with all animation styles */
@import url('transitions.css'); /* New file with View Transitions config */
```

## Performance Implications

### Positive Impacts

| Technique | Performance Gain | Notes |
|-----------|------------------|-------|
| Intersection Observer vs Scroll | +43% main thread availability | On slow mobile (6× CPU throttle) |
| CSS transitions vs JS animation | GPU-accelerated | Hardware compositing for transform/opacity |
| View Transitions API | Native browser optimization | No JS runtime overhead |
| Fisher-Yates O(n) | Faster than sort O(n log n) | Negligible for 200 items but cleaner |
| Auto-fit grid | No JS layout calculations | Browser handles responsive breakpoints |

### Negative Impacts (Minimal)

| Technique | Performance Cost | Mitigation |
|-----------|------------------|------------|
| 200+ DOM nodes | Initial render time | Use Intersection Observer for lazy image loading |
| View Transitions memory | Snapshot old/new page | 4s timeout, browser manages memory |
| Polling at 2.5s | Network requests | Consider SSE in future; current rate acceptable |

### Mobile-Specific Optimizations

1. **Hardware Acceleration**
   ```css
   .animated {
     will-change: transform, opacity; /* Hint to browser */
     transform: translateZ(0); /* Force GPU layer */
   }
   ```

2. **Reduce Motion**
   ```css
   @media (prefers-reduced-motion: reduce) {
     * {
       animation-duration: 0.01ms !important;
       transition-duration: 0.01ms !important;
     }
   }
   ```

3. **Touch Performance**
   ```css
   .interactive {
     touch-action: manipulation; /* Disable double-tap zoom */
     -webkit-tap-highlight-color: transparent; /* Remove tap flash */
   }
   ```

4. **Image Loading Strategy**
   - Lazy load below fold: Intersection Observer with rootMargin: '200px'
   - Use WebP with fallback: `<picture>` element
   - Proper sizing: provide width/height attributes to prevent layout shift

## Testing Strategy

### Browser Testing

**High Priority (85%+ coverage):**
- Chrome 126+ (Android/Desktop)
- Safari 18+ (iOS 18, macOS)
- Firefox 144+ (Android/Desktop)
- Edge 126+ (Desktop)

**Medium Priority (fallback verification):**
- Safari 17 (iOS 17) - no cross-doc transitions
- Chrome 110-125 - no cross-doc transitions
- Firefox 130-143 - experimental support

**Low Priority (functional fallback only):**
- Safari 16 and below
- Chrome 100 and below

### Device Testing Matrix

| Device Category | Viewport | Test Cases |
|----------------|----------|------------|
| **Mobile** | 375px (iPhone SE) | Touch interactions, card selection, progressive inputs |
| **Mobile Large** | 414px (iPhone Pro Max) | Grid layout, font scaling |
| **Tablet** | 768px (iPad) | Two-column layouts, hybrid touch/pointer |
| **Desktop** | 1024px+ | Hover states, larger grids |

### Performance Budgets

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint | <1.5s | Lighthouse |
| Largest Contentful Paint | <2.5s | Lighthouse |
| Cumulative Layout Shift | <0.1 | Lighthouse |
| Total Blocking Time | <200ms | Lighthouse |
| Animation frame rate | 60fps | Chrome DevTools Performance |
| Main thread idle (with IO) | >40% | Chrome DevTools Performance |

### Manual Test Checklist

- [ ] View Transitions work on Chrome 126+ (fade between pages)
- [ ] Fallback works on Safari 17 (instant navigation, no errors)
- [ ] Progressive inputs animate on Chrome/Safari/Firefox latest
- [ ] Touch feedback on mobile (scale, no sticky hover)
- [ ] Image grid lazy loads (check Network tab)
- [ ] 60 random images selected from 200+ pool
- [ ] Polling updates participant list without flicker
- [ ] Reduced motion preference respected
- [ ] Works offline (after initial load, with service worker)
- [ ] No console errors on any browser

## Accessibility Considerations

### Motion Sensitivity

```css
/* Respect user preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Focus Management

```javascript
// Maintain focus during View Transitions
document.addEventListener('click', (e) => {
  const link = e.target.closest('a[href]');
  if (link && document.startViewTransition) {
    // Store focused element
    const activeElement = document.activeElement;
    sessionStorage.setItem('lastFocusedId', activeElement?.id);
  }
});

// Restore focus after transition
window.addEventListener('pageshow', () => {
  const lastFocusedId = sessionStorage.getItem('lastFocusedId');
  if (lastFocusedId) {
    document.getElementById(lastFocusedId)?.focus();
    sessionStorage.removeItem('lastFocusedId');
  }
});
```

### Keyboard Navigation

```css
/* Visible focus indicators */
.selectable-card:focus-visible {
  outline: 3px solid var(--accent-color);
  outline-offset: 2px;
}

/* Match selection visual for keyboard users */
.selectable-card[aria-selected="true"] {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2);
}
```

```javascript
// Keyboard selection support
document.querySelectorAll('.selectable-card').forEach(card => {
  card.setAttribute('tabindex', '0');
  card.setAttribute('role', 'button');
  card.setAttribute('aria-selected', 'false');

  card.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      card.click();
      card.setAttribute('aria-selected',
        card.classList.contains('selected') ? 'true' : 'false'
      );
    }
  });
});
```

### Screen Reader Announcements

```html
<!-- Live region for dynamic updates -->
<div aria-live="polite" aria-atomic="true" class="sr-only">
  <span id="status-message"></span>
</div>
```

```javascript
// Announce participant joins
function updateParticipantList(participants) {
  // ... update UI ...

  // Announce to screen readers
  const message = `${participants.length} participants ready`;
  document.getElementById('status-message').textContent = message;
}
```

## Migration Path

### Phase 1: Foundation (Current Milestone)
1. Add `@view-transition { navigation: auto; }` to CSS
2. Test cross-document transitions on Chrome/Safari/Firefox
3. Add feature detection utility

### Phase 2: Progressive Inputs
1. Implement @starting-style for input fields
2. Add transition-behavior for display animations
3. Test progressive disclosure pattern

### Phase 3: Selection Feedback
1. Add touch-friendly card styles
2. Implement hover media queries
3. Test on mobile devices (375px)

### Phase 4: Scroll Animations
1. Add Intersection Observer for image grid
2. Implement lazy loading with data-src
3. Optimize with rootMargin

### Phase 5: Polish
1. Add haptic feedback (navigator.vibrate)
2. Optimize polling with View Transitions integration
3. Consider SSE upgrade (optional, future milestone)

### Phase 6: Accessibility & Performance
1. Add reduced motion support
2. Implement focus management
3. Add performance monitoring
4. Conduct accessibility audit

Each phase builds on the previous, maintains backward compatibility, and can be deployed independently.

## Key Takeaways

1. **View Transitions API is production-ready** (85%+ browser support) for smooth multi-page navigation
2. **@starting-style + transition-behavior** enable CSS-only progressive disclosure (Baseline 2024)
3. **Intersection Observer** is the standard for scroll-based reveals (97%+ support, 43% better performance)
4. **No build tools required** - all features are native browser APIs
5. **Progressive enhancement** at every level - features layer on top of working baseline
6. **Mobile-first with 375px baseline** - iPhone SE is minimum viable viewport
7. **Fisher-Yates shuffle** for statistically unbiased random selection
8. **Touch-specific considerations** - hover media queries, min 44×44px targets, no sticky states

## Confidence Assessment

| Area | Confidence | Reason |
|------|-----------|--------|
| View Transitions API | **HIGH** | Official MDN/Chrome docs, browser support verified via Can I Use |
| @starting-style/transition-behavior | **HIGH** | Baseline 2024 status, universal modern browser support |
| Intersection Observer | **HIGH** | Baseline 2019, 97%+ support, production-proven |
| Touch/mobile patterns | **HIGH** | Web search verified with multiple current sources (2024-2026) |
| Fisher-Yates algorithm | **HIGH** | Computer science standard, well-documented |
| Integration approach | **MEDIUM** | Based on research, but project-specific implementation may vary |

## Open Questions for Implementation

1. **Server-side vs client-side image selection?**
   - Server: consistent subset per session
   - Client: per-user variety
   - Recommendation: Server-side for consistency, client-side if personalization desired

2. **Polling vs SSE for real-time updates?**
   - Current: 2.5s polling works fine
   - SSE: more efficient but requires backend changes
   - Recommendation: Keep polling now, consider SSE in future milestone

3. **View Transitions on form submissions?**
   - Can wrap form.submit() in startViewTransition
   - Requires client-side handling of POST
   - Recommendation: Start with GET navigation, enhance forms later

4. **Container queries vs media queries for card grid?**
   - Container queries: 93.92% support, more component-responsive
   - Media queries: universal support
   - Recommendation: Use both (container queries with media query fallback)

## Sources Summary

**View Transitions API:**
- [MDN: View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)
- [Chrome Developers: Cross-document view transitions](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document)
- [Can I Use: View Transitions](https://caniuse.com/view-transitions)
- [Chrome Blog: View Transitions in 2025](https://developer.chrome.com/blog/view-transitions-in-2025)

**CSS Animation Features:**
- [MDN: @starting-style](https://developer.mozilla.org/en-US/docs/Web/CSS/@starting-style)
- [MDN: transition-behavior](https://developer.mozilla.org/en-US/docs/Web/CSS/transition-behavior)
- [web.dev: Baseline entry animations](https://web.dev/blog/baseline-entry-animations)
- [CSS-Tricks: @starting-style](https://css-tricks.com/almanac/rules/s/starting-style/)

**Intersection Observer:**
- [MDN: Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [Future Forem: Mastering Intersection Observer 2026](https://future.forem.com/sherry_walker_bba406fb339/mastering-the-intersection-observer-api-2026-a-complete-guide-561k)
- [ITNEXT: Scroll listener vs Intersection Observer](https://itnext.io/1v1-scroll-listener-vs-intersection-observers-469a26ab9eb6)

**Mobile/Touch Patterns:**
- [Lexo: Handle Hover on Mobile](https://www.lexo.ch/blog/2024/12/handling-hover-on-mobile-devices-with-html-css-and-javascript/)
- [Medium: CSS hover on touch screens](https://arturocreates.medium.com/handle-hover-css-on-mobile-touch-screen-69142ea79fe7)
- [PxlPeak: Responsive Design Best Practices 2026](https://pxlpeak.com/blog/web-design/responsive-design-best-practices)
- [WP Dean: CSS Border Animation](https://wpdean.com/css-border-animation/)

**Responsive Layout:**
- [FrontendTools: CSS Grid Masterclass 2025](https://www.frontendtools.tech/blog/mastering-css-grid-2025)
- [LogRocket: Container queries 2026](https://blog.logrocket.com/container-queries-2026/)
- [CSS-Tricks: Look Ma, No Media Queries!](https://css-tricks.com/look-ma-no-media-queries-responsive-layouts-using-css-grid/)

**JavaScript Techniques:**
- [30 Seconds of Code: Array sampling and shuffling](https://www.30secondsofcode.org/js/s/array-sample-shuffle-weighted-selection/)
- [DEV: Real-time Updates: Polling, SSE and WebSockets](https://dev.to/thesanjeevsharma/real-time-updates-polling-sse-and-web-sockets-277i)
- [Medium: Page Transitions in Vanilla JavaScript](https://medium.com/@dylanconnor4/page-transitions-in-vanilla-javascript-d71f4331dcf6)
- [Stack Abuse: Shuffling Arrays in JavaScript](https://stackabuse.com/shuffling-arrays-in-javascript/)

All sources accessed 2026-01-24. Total sources: 30+ (see inline citations throughout document).
