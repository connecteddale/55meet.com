---
phase: 13
plan: 03
subsystem: participant-entry
tags: [qr-code, team-join, png-generation]
dependencies:
  requires: [10-01, 10-02]
  provides: [qr-code-generation, team-join-url]
  affects: [13-01, 13-02]
tech-stack:
  added: [qrcode, pillow]
  patterns: [streaming-response, proxy-aware-urls]
key-files:
  created:
    - the55/app/routers/qr.py
  modified:
    - the55/requirements.txt
    - the55/app/routers/__init__.py
    - the55/app/main.py
    - the55/app/templates/admin/teams/edit.html
    - the55/app/static/css/main.css
decisions:
  - id: qr-error-correction
    choice: ERROR_CORRECT_M for display, ERROR_CORRECT_H for print
    reason: Higher error correction for printed QR codes ensures scanning reliability
metrics:
  duration: 4m
  completed: 2026-01-18
---

# Phase 13 Plan 03: QR Code Generation Summary

QR code generation for team join URLs with proxy-aware URL construction and two output sizes.

## What Was Built

1. **QR Code Router** (`/var/www/the55/app/routers/qr.py`)
   - GET `/admin/qr/team/{team_id}` - Returns inline PNG for display
   - GET `/admin/qr/team/{team_id}/download` - Returns attachment PNG for printing

2. **Team Edit Page Integration**
   - QR code displayed on team edit page
   - Team code shown prominently below QR
   - Download button for printable version

3. **Dependencies**
   - qrcode[pil]==8.2 added to requirements.txt
   - Pillow included for PNG generation

## Technical Details

### QR Code Configuration

**Display QR (inline):**
- box_size=10, border=4
- ERROR_CORRECT_M (15% error correction)
- Cache-Control: max-age=3600

**Print QR (download):**
- box_size=15, border=4
- ERROR_CORRECT_H (30% error correction)
- Content-Disposition: attachment

### Proxy-Aware URL Construction

```python
def get_base_url(request: Request) -> str:
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.url.netloc)
    return f"{proto}://{host}"
```

Handles nginx reverse proxy headers for correct HTTPS URLs.

## Key Commits

| Commit | Description |
|--------|-------------|
| c0efbb3 | Add qrcode library to requirements |
| fb49930 | Create QR code router |
| 53462de | Register router and update team edit page |

## Verification Results

- [x] qrcode library installed and imports correctly
- [x] QR code endpoint returns valid PNG image
- [x] QR code encodes /join?code={CODE} URL
- [x] Team edit page displays QR code
- [x] Download endpoint provides larger QR for printing

## Deviations from Plan

None - plan executed exactly as written.

## Integration Points

- QR encodes `/join?code={CODE}` URL (implemented in 13-01)
- Displayed on team edit page (extends 10-03 team management)
- Auth protected via AuthDep (uses 10-04 auth system)

## Next Steps

QR code generation complete. Facilitators can now:
1. View QR code on team edit page
2. Download printable QR for display
3. Participants scan to reach join page (13-01)
