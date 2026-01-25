# Stack Research: v2.2 World Class UX

**Researched:** 2026-01-21
**Focus:** Premium minimalist design (Duarte/Jobs style) for existing FastAPI/Jinja2 app
**Constraint:** No build step, vanilla JS, server-rendered templates
**Supplements:** STACK.md (v2.0 foundation) - this doc adds UX layer

## Executive Summary

The existing stack (Inter font, CSS custom properties, vanilla JS) is an excellent foundation for premium UX. The path forward is **refinement, not replacement**. Modern CSS features (scroll-driven animations, view transitions, fluid typography) now have broad browser support and align perfectly with the "no build step" constraint.

**Key insight:** Apple's premium feel comes from typography discipline, generous whitespace, and restrained animation - not from frameworks or complex tooling.

---

## CSS Approach

### Recommendation: Extend Current Vanilla CSS with Design Tokens

The existing `thestyle.css` already uses Inter font and clean styling. Extend it with a systematic design token layer.

**Why NOT use a CSS framework:**
- Tailwind requires Node.js build step (violates constraint)
- Bootstrap/Foundation add bloat and fight against minimalist aesthetic
- Current CSS is already clean and maintainable
- CSS custom properties provide the same token benefits as Tailwind's @theme

**Design Token System:**

```css
:root {
  /* Spacing scale (4px base, 2x multiplier) */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 1rem;      /* 16px */
  --space-4: 1.5rem;    /* 24px */
  --space-5: 2rem;      /* 32px */
  --space-6: 3rem;      /* 48px */
  --space-7: 4rem;      /* 64px */
  --space-8: 6rem;      /* 96px */

  /* Colors - Apple-inspired minimal palette */
  --color-text: #1d1d1f;
  --color-text-secondary: #6e6e73;
  --color-text-tertiary: #86868b;
  --color-background: #ffffff;
  --color-background-secondary: #f5f5f7;
  --color-accent: #0066cc;
  --color-border: #d2d2d7;

  /* Typography scale */
  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --text-sm: clamp(0.875rem, 0.8rem + 0.35vw, 1rem);
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg: clamp(1.125rem, 1rem + 0.6vw, 1.375rem);
  --text-xl: clamp(1.5rem, 1.25rem + 1.25vw, 2rem);
  --text-2xl: clamp(2rem, 1.5rem + 2.5vw, 3rem);
  --text-3xl: clamp(2.5rem, 1.75rem + 3.75vw, 4rem);

  /* Animation timing */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
}
```

**Sources:**
- [CSS Design Tokens Guide](https://javascript.plainenglish.io/css-variables-as-design-tokens-your-frontends-best-friend-and-why-you-ll-wonder-how-you-lived-5cbc68dd6de8)
- [Fluid Typography with clamp()](https://www.smashingmagazine.com/2022/01/modern-fluid-typography-css-clamp/)

---

## Animation Patterns

### Recommendation: Native CSS First, GSAP for Complex Sequences

**Layer 1: CSS-Only (Most Cases)**

Modern CSS handles most animation needs without JavaScript:

```css
/* Fade-in on scroll using scroll-driven animations */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.reveal {
  animation: fade-in linear;
  animation-timeline: view();
  animation-range: entry 0% entry 30%;
}
```

**Browser Support (2025-2026):**
- Scroll-driven animations: Chrome 116+, Safari 26+, Firefox 144+
- View Transitions API: Chrome 111+, Safari 18+, Firefox 144+
- Both are now Baseline Newly Available (October 2025)

**Progressive Enhancement Pattern:**
```css
@supports (animation-timeline: view()) {
  .reveal {
    animation: fade-in linear;
    animation-timeline: view();
  }
}
```

**Layer 2: Intersection Observer (Fallback)**

For browsers without scroll-driven animation support:

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

**Layer 3: GSAP (Complex Sequences Only)**

Use GSAP via CDN only for:
- Staggered text reveals (SplitText)
- Timeline-based choreographed animations
- Interactive demo flows with precise control

```html
<!-- CDN - no build step required -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14/dist/ScrollTrigger.min.js"></script>
```

**Key insight (2025):** GSAP is now 100% free including all plugins (SplitText, MorphSVG, etc.) thanks to Webflow acquisition.

**Animation Timing Best Practices:**
- Duration: 150-400ms (sweet spot)
- Use `transform` and `opacity` only (GPU-accelerated)
- Always check `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Sources:**
- [CSS Scroll-Driven Animations MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)
- [WebKit Scroll Animation Guide](https://webkit.org/blog/17101/a-guide-to-scroll-driven-animations-with-just-css/)
- [GSAP Getting Started](https://gsap.com/resources/get-started/)
- [Chrome View Transitions 2025](https://developer.chrome.com/blog/view-transitions-in-2025)

---

## Typography & Spacing

### Recommendation: Keep Inter, Add Apple-Inspired Typography System

The existing Inter font is an excellent choice - it's the standard for premium web interfaces and shares design DNA with SF Pro.

**Typography Hierarchy (Duarte/Jobs Style):**

| Element | Size Token | Weight | Letter-spacing | Use |
|---------|------------|--------|----------------|-----|
| Hero headline | `--text-3xl` | 600 | -0.03em | Landing page hero |
| Section title | `--text-2xl` | 600 | -0.02em | Major sections |
| Subsection | `--text-xl` | 600 | -0.015em | Content divisions |
| Body large | `--text-lg` | 400 | normal | Key paragraphs |
| Body | `--text-base` | 400 | normal | Standard content |
| Caption | `--text-sm` | 400 | 0.01em | Secondary info |
| Label | `--text-xs` | 500 | 0.02em | UI labels |

**Key Typography Principles (Apple-style):**
1. **Tight letter-spacing for headlines** (-0.02 to -0.03em)
2. **Generous line-height for body** (1.5-1.7)
3. **Maximum ~65-75 characters per line** for readability
4. **Bold left-alignment** (Apple's new 2025 design system moved away from center)

**Fluid Typography Implementation:**

```css
html {
  font-size: clamp(1em, 17px + 0.24vw, 1.125em);
}

.hero-headline {
  font-size: var(--text-3xl);
  font-weight: 600;
  letter-spacing: -0.03em;
  line-height: 1.1;
}

.body-text {
  font-size: var(--text-base);
  line-height: 1.7;
  max-width: 65ch;
}
```

**Whitespace System (Presentation-Quality):**

Jobs/Duarte presentations use extreme whitespace. Translate to web:

```css
/* Section breathing room */
.hero-section { padding: var(--space-8) 0; }
.content-section { padding: var(--space-7) 0; }

/* Element spacing */
.section-title { margin-bottom: var(--space-5); }
.paragraph + .paragraph { margin-top: var(--space-4); }
```

**Sources:**
- [Apple Human Interface Guidelines - Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Apple WWDC 2025 Design System](https://www.geeky-gadgets.com/apple-design-system-wwdc25/)
- [Modern Web Typography 2025](https://www.frontendtools.tech/blog/modern-web-typography-techniques-2025-readability-guide)
- [Fluid Type Scale Calculator](https://www.fluid-type-scale.com/)

---

## What NOT to Use

### Tailwind CSS
**Why avoid:** Requires Node.js and build step. Violates the constraint directly. Also creates verbose HTML that's harder to read in Jinja2 templates.

### Heavy Animation Libraries (Anime.js, Motion One, Framer Motion)
**Why avoid:** GSAP covers all needs and is now completely free. Adding another library creates bundle bloat for no benefit.

### CSS Frameworks (Bootstrap, Bulma, Foundation)
**Why avoid:** They impose design opinions that fight against minimalist aesthetic. Current vanilla CSS is already cleaner.

### Parallax Scrolling Effects
**Why avoid:** Outdated pattern from 2015 era. Apple and premium sites now use subtle reveal animations, not parallax. Also causes performance issues on mobile.

### Complex Grid Systems
**Why avoid:** CSS Grid is native and sufficient. No need for grid frameworks.

### Web Fonts Beyond Inter
**Why avoid:** Inter already matches the premium aesthetic. Adding more fonts increases load time and creates visual inconsistency. Exception: a display font for the hero ONLY if it adds clear value.

### JavaScript Animation for Simple Effects
**Why avoid:** CSS handles fade-ins, slides, and reveals natively with better performance. Reserve JS for choreographed sequences only.

### Center-Aligned Text Blocks
**Why avoid:** Apple's 2025 design system explicitly moved to left-alignment for better readability. Center alignment is now considered dated for body content.

### Carousel/Slider Components
**Why avoid:** User research consistently shows carousels have poor engagement. Use single focal images or static galleries instead.

---

## Recommended Changes to Current Stack

### Add to CSS (`thestyle.css` or new files)

1. **Design token layer** (variables section at top)
2. **Fluid typography using clamp()**
3. **Scroll-driven animation utilities**
4. **Reduced motion media query**

### Add JavaScript Files

| File | Purpose | Size |
|------|---------|------|
| `reveal.js` | Intersection Observer fallback for animations | ~1KB |
| `demo-flow.js` | Interactive demo state management | ~3KB |

### Optional CDN Additions (Load Only When Needed)

| Library | CDN | When to Load |
|---------|-----|--------------|
| GSAP Core | `cdn.jsdelivr.net/npm/gsap@3.14/dist/gsap.min.js` | Landing page hero animation |
| GSAP ScrollTrigger | `cdn.jsdelivr.net/npm/gsap@3.14/dist/ScrollTrigger.min.js` | Scroll-based sequences |
| GSAP SplitText | `cdn.jsdelivr.net/npm/gsap@3.14/dist/SplitText.min.js` | Animated text reveals |

### File Organization

```
/var/www/statics/
  css/
    tokens.css          # Design tokens (new)
    thestyle.css        # Existing (enhanced)
    landing.css         # Landing page specific (new)
    dashboard.css       # Facilitator dashboard (new)
  js/
    c.js                # Existing comments
    reveal.js           # Animation reveal utility (new)
    demo-flow.js        # Interactive demo (new)
```

### Browser Support Target

| Feature | Chrome | Safari | Firefox | Fallback |
|---------|--------|--------|---------|----------|
| Scroll-driven animations | 116+ | 26+ | 144+ | Intersection Observer |
| View Transitions | 111+ | 18+ | 144+ | Standard page load |
| CSS Nesting | 120+ | 17.2+ | 117+ | Flat CSS |
| Container Queries | 105+ | 16+ | 110+ | Media queries |

---

## Implementation Priority

### Phase 1: Foundation
1. Add design tokens to existing CSS
2. Implement fluid typography
3. Add reduced motion support

### Phase 2: Animations
1. CSS scroll-driven animations with fallback
2. Intersection Observer utility
3. View Transitions for page navigation

### Phase 3: Premium Touches (If Needed)
1. GSAP for hero animation only
2. SplitText for headline reveals
3. Dashboard micro-interactions

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| CSS approach | HIGH | Based on official MDN docs and browser support data |
| Animation patterns | HIGH | Verified via Chrome DevRel, WebKit blog |
| Typography | HIGH | Apple HIG, WWDC 2025 announcements |
| What NOT to use | MEDIUM | Community consensus, may have edge cases |
| GSAP | HIGH | Official GSAP docs, verified free licensing |

---

*Research completed: 2026-01-21*
*Sources: MDN, Apple Developer, Chrome DevRel, WebKit, GSAP official*
