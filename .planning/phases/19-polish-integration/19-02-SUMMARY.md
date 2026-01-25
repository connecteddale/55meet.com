---
phase: 28
plan: 02
subsystem: error-handling
tags: [fastapi, error-pages, ux, graceful-degradation]

dependency-graph:
  requires: [28-01]
  provides: [custom-error-pages, exception-handlers]
  affects: [all-user-facing-pages]

tech-stack:
  added: []
  patterns: [content-negotiation, standalone-templates]

key-files:
  created:
    - the55/app/templates/errors/404.html
    - the55/app/templates/errors/500.html
  modified:
    - the55/app/main.py
    - the55/app/static/css/main.css

decisions: []

metrics:
  duration: 3m
  completed: 2026-01-21
---

# Phase 28 Plan 02: Graceful Error Pages Summary

**One-liner:** Custom 404/500 pages with content negotiation returning HTML for browsers, JSON for API calls.

## What Was Built

### Custom Error Templates
Created standalone error templates that render even if base template has issues:

**404.html:**
- Friendly "Page Not Found" message
- Links to homepage and facilitator dashboard
- Standalone HTML (no base.html dependency for reliability)

**500.html:**
- Friendly "Something Went Wrong" message
- Try Again button (reloads page)
- Homepage link for escape path

### Exception Handlers
Added FastAPI exception handlers in main.py:

```python
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """Custom 404 page for browser requests."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse("errors/404.html", ...)
    return JSONResponse(status_code=404, content={"detail": "Not found"})
```

Content negotiation via Accept header:
- Browsers receive friendly HTML pages
- API clients receive JSON responses

### CSS Styling
Added `.error-page` styles:
- Centered layout with generous padding
- Responsive button actions with flex-wrap
- Uses existing design tokens for consistency

## Key Implementation Details

1. **Standalone templates** - Don't extend base.html to ensure they render even if there are template errors elsewhere

2. **Content negotiation** - Check Accept header to serve appropriate response format:
   - `text/html` -> Friendly HTML page
   - Other -> JSON error response

3. **Consistent styling** - Use existing `.btn-primary`, `.btn-secondary`, and design tokens

## Commits

| Hash | Type | Description |
|------|------|-------------|
| a53a7b3 | feat | add custom error page templates |
| 19a7963 | feat | add exception handlers for graceful errors |
| (bundled) | feat | add error page CSS styling |

Note: CSS was committed as part of 28-01 plan due to file staging timing.

## Verification

- [x] App loads successfully with exception handlers
- [x] Error templates exist in templates/errors/
- [x] CSS has .error-page styling
- [x] Exception handlers registered for 404 and 500

## Deviations from Plan

None - plan executed exactly as written.

## Files Changed

```
the55/app/templates/errors/404.html  (new - 23 lines)
the55/app/templates/errors/500.html  (new - 23 lines)
the55/app/main.py                    (+48 lines - exception handlers)
the55/app/static/css/main.css        (+20 lines - error page styles)
```

## Next Phase Readiness

Error handling is now graceful for browser users. Technical JSON errors still returned for API clients which is appropriate for programmatic access.
