# Phase 29: PDF Export - Research

**Researched:** 2026-01-22
**Domain:** Python PDF Generation for FastAPI
**Confidence:** HIGH

## Summary

This research evaluates Python PDF generation libraries for creating presentation-ready session reports in The 55 App. The key requirements are: clean minimal design matching the Apple-inspired aesthetic, no external system dependencies (for deployment simplicity), and integration with the existing FastAPI/Jinja2 stack.

After evaluating ReportLab, WeasyPrint, and fpdf2, the clear recommendation is **fpdf2** for this use case. It offers the best balance of simplicity, deployment ease (pure Python, no system dependencies), active maintenance, and sufficient styling capabilities for professional minimal reports.

**Primary recommendation:** Use fpdf2 2.8.x for PDF generation. It requires no system dependencies, integrates cleanly with FastAPI, and supports custom TTF fonts (Inter) for design consistency.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fpdf2 | 2.8.5 | PDF generation | Pure Python, no system deps, actively maintained, FastAPI examples in docs |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Inter font TTF | Variable | Custom font embedding | Match existing design system |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| fpdf2 | WeasyPrint | HTML/CSS approach but requires system deps (Pango, Cairo) - deployment complexity |
| fpdf2 | ReportLab | More powerful but steeper learning curve, overkill for minimal reports |
| fpdf2 | xhtml2pdf | HTML-to-PDF but less actively maintained |

**Installation:**
```bash
pip install fpdf2
```

No additional system packages required. Inter font files need to be downloaded and placed in static/fonts/.

## Architecture Patterns

### Recommended Project Structure
```
app/
  routers/
    sessions.py          # Add export_pdf endpoint here (alongside export_markdown)
  services/
    pdf_export.py        # NEW: PDF generation service
static/
  fonts/
    Inter-Regular.ttf    # Custom font files
    Inter-Bold.ttf
    Inter-Italic.ttf
```

### Pattern 1: FastAPI PDF Response
**What:** Return PDF bytes directly from FastAPI endpoint
**When to use:** PDF export endpoint
**Example:**
```python
# Source: https://py-pdf.github.io/fpdf2/UsageInWebAPI.html
from fastapi import Response
from fpdf import FPDF

@router.get("/{session_id}/export/pdf")
async def export_pdf(session_id: int, auth: AuthDep, db: DbDep):
    # ... fetch session data ...

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Inter", size=24)
    pdf.cell(text="Session Report")

    # Clean filename: team-name-YYYY-MM-session-report.pdf
    filename = f"{safe_team}-{session.month}-session-report.pdf"

    return Response(
        content=bytes(pdf.output()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

### Pattern 2: Subclass FPDF for Custom Headers/Footers
**What:** Extend FPDF class for consistent report template
**When to use:** Multi-page reports with headers/footers
**Example:**
```python
# Source: https://py-pdf.github.io/fpdf2/Tutorial.html (Tuto 2)
from fpdf import FPDF

class SessionReportPDF(FPDF):
    def __init__(self, team_name: str, session_date: str):
        super().__init__()
        self.team_name = team_name
        self.session_date = session_date

    def header(self):
        self.set_font("Inter", style="B", size=10)
        self.set_text_color(110, 110, 115)  # --color-text-secondary
        self.cell(0, 10, f"The 55 | {self.team_name}", align="L")
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Inter", style="I", size=8)
        self.set_text_color(134, 134, 139)  # --color-text-tertiary
        self.cell(0, 10, f"{self.session_date} | Page {self.page_no()}", align="C")
```

### Pattern 3: Font Registration at App Startup
**What:** Register custom fonts once, use throughout
**When to use:** Custom TTF fonts like Inter
**Example:**
```python
# Source: https://py-pdf.github.io/fpdf2/Unicode.html
from fpdf import FPDF
from pathlib import Path

FONT_DIR = Path("static/fonts")

def create_pdf_with_fonts():
    pdf = FPDF()
    # Register Inter font family
    pdf.add_font("Inter", style="", fname=str(FONT_DIR / "Inter-Regular.ttf"))
    pdf.add_font("Inter", style="b", fname=str(FONT_DIR / "Inter-Bold.ttf"))
    pdf.add_font("Inter", style="i", fname=str(FONT_DIR / "Inter-Italic.ttf"))
    return pdf
```

### Anti-Patterns to Avoid
- **Reusing FPDF instances:** Create new instance per request - "FPDF instance objects are not designed to be reusable: content cannot be added once output() has been called"
- **Inline styles everywhere:** Use a subclass pattern for consistent styling
- **Hardcoded colors:** Use constants matching CSS variables for design system consistency

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Text wrapping | Manual line splitting | `pdf.multi_cell()` | Handles word wrap, page breaks automatically |
| Tables | Manual cell positioning | `pdf.table()` context manager | Handles borders, alignment, spanning |
| Page breaks | Manual tracking | `set_auto_page_break()` | Automatic breaks with header/footer restoration |
| Font subsetting | Full font embedding | fpdf2 default | Automatically subsets fonts to reduce file size |
| Unicode text | Character encoding | fpdf2 with TTF fonts | Full Unicode support with add_font() |

**Key insight:** fpdf2 handles all the fiddly PDF layout complexity (page breaks, text wrapping, font embedding) - leverage these built-ins rather than fighting the library.

## Common Pitfalls

### Pitfall 1: Font Not Found Errors
**What goes wrong:** `fpdf2.errors.FPDFException: TTF Font file not found`
**Why it happens:** Font path is relative to working directory, not module location
**How to avoid:** Use absolute paths via `Path(__file__).parent` or configure font directory
**Warning signs:** Works locally, fails in production

### Pitfall 2: Instance Reuse
**What goes wrong:** Empty PDF or corrupted output
**Why it happens:** Calling `output()` marks instance as consumed
**How to avoid:** Create fresh FPDF instance for each request
**Warning signs:** First PDF works, subsequent ones fail

### Pitfall 3: Missing Font Styles
**What goes wrong:** Bold/italic text renders as regular
**Why it happens:** Only registered the regular weight, not bold/italic variants
**How to avoid:** Register all four styles (regular, bold, italic, bold-italic) for each font family
**Warning signs:** `set_font("Inter", style="B")` has no effect

### Pitfall 4: Header/Footer Not Appearing
**What goes wrong:** Custom header/footer methods never called
**Why it happens:** Must subclass FPDF and call `add_page()` after setting up instance
**How to avoid:** Always use subclass pattern, ensure `add_page()` triggers header
**Warning signs:** Plain pages despite header/footer overrides

### Pitfall 5: Large PDF Files
**What goes wrong:** PDFs are 10x expected size
**Why it happens:** Embedding full font files instead of subsets, or high-res images
**How to avoid:** fpdf2 subsets by default; use appropriate image sizes
**Warning signs:** Simple text PDF is several MB

## Code Examples

Verified patterns from official sources:

### Complete Session Report Structure
```python
# Source: Combined from https://py-pdf.github.io/fpdf2/Tutorial.html
from fpdf import FPDF
from pathlib import Path
from typing import List, Dict, Optional

FONT_DIR = Path(__file__).parent.parent / "static" / "fonts"

class SessionReportPDF(FPDF):
    """PDF generator for The 55 session reports."""

    def __init__(self, team_name: str, session_date: str):
        super().__init__()
        self.team_name = team_name
        self.session_date = session_date
        self._setup_fonts()
        self.set_auto_page_break(auto=True, margin=20)

    def _setup_fonts(self):
        """Register Inter font family."""
        self.add_font("Inter", style="", fname=str(FONT_DIR / "Inter-Regular.ttf"))
        self.add_font("Inter", style="b", fname=str(FONT_DIR / "Inter-Bold.ttf"))
        self.add_font("Inter", style="i", fname=str(FONT_DIR / "Inter-Italic.ttf"))

    def header(self):
        """Page header with branding."""
        self.set_font("Inter", style="B", size=10)
        self.set_text_color(110, 110, 115)
        self.cell(0, 10, f"The 55 | {self.team_name}", align="L")
        self.ln(10)
        self.set_draw_color(210, 210, 215)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        """Page footer with date and page number."""
        self.set_y(-15)
        self.set_font("Inter", size=8)
        self.set_text_color(134, 134, 139)
        self.cell(0, 10, f"{self.session_date} | Page {self.page_no()}", align="C")

    def add_title(self, text: str):
        """Add main title."""
        self.set_font("Inter", style="B", size=24)
        self.set_text_color(29, 29, 31)  # --color-text
        self.cell(0, 15, text, align="L")
        self.ln(20)

    def add_section_header(self, text: str):
        """Add section header."""
        self.set_font("Inter", style="B", size=14)
        self.set_text_color(29, 29, 31)
        self.cell(0, 10, text, align="L")
        self.ln(8)

    def add_body_text(self, text: str):
        """Add body paragraph."""
        self.set_font("Inter", size=11)
        self.set_text_color(29, 29, 31)
        self.multi_cell(0, 6, text)
        self.ln(5)

    def add_attributed_insight(self, statement: str, participants: List[str]):
        """Add insight with attribution."""
        self.set_font("Inter", size=11)
        self.set_text_color(29, 29, 31)
        # Bullet point
        self.cell(5, 6, chr(8226), align="L")  # bullet character
        self.multi_cell(0, 6, statement)
        # Attribution in secondary color
        self.set_font("Inter", style="I", size=10)
        self.set_text_color(110, 110, 115)
        self.cell(5)  # indent
        self.cell(0, 5, f"({', '.join(participants)})")
        self.ln(8)
```

### FastAPI Endpoint Integration
```python
# Source: https://py-pdf.github.io/fpdf2/UsageInWebAPI.html
from fastapi import Response

@router.get("/{session_id}/export/pdf")
async def export_pdf(session_id: int, auth: AuthDep, db: DbDep):
    """Export session data as presentation-ready PDF."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team

    # Create PDF
    pdf = SessionReportPDF(
        team_name=team.team_name,
        session_date=session.month
    )
    pdf.add_page()

    # Title section
    pdf.add_title("Session Report")

    # Strategy statement
    if team.strategy_statement:
        pdf.add_section_header("Strategy Statement")
        pdf.add_body_text(team.strategy_statement)

    # Synthesis themes
    if session.synthesis_themes:
        pdf.add_section_header("What We Heard")
        pdf.add_body_text(session.synthesis_themes)

    # Key insights with attribution
    if session.synthesis_statements:
        statements = json.loads(session.synthesis_statements)
        pdf.add_section_header("Key Insights")
        for stmt in statements:
            pdf.add_attributed_insight(
                stmt.get("statement", ""),
                stmt.get("participants", [])
            )

    # Generate filename
    safe_team = team.team_name.replace(" ", "-").replace("/", "-")
    filename = f"{safe_team}-{session.month}-session-report.pdf"

    return Response(
        content=bytes(pdf.output()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

### Table for Structured Data (if needed)
```python
# Source: https://py-pdf.github.io/fpdf2/Tables.html
def add_insights_table(self, statements: List[Dict]):
    """Add insights as a styled table."""
    self.set_font("Inter", size=10)

    with self.table(
        borders_layout="MINIMAL",
        cell_fill_color=(245, 245, 247),  # --color-bg-secondary
        cell_fill_mode="ROWS",
        text_align="LEFT",
        line_height=6,
        col_widths=(140, 50)
    ) as table:
        # Header row
        header = table.row()
        header.cell("Insight", style="B")
        header.cell("Participants", style="B")

        # Data rows
        for stmt in statements:
            row = table.row()
            row.cell(stmt.get("statement", ""))
            row.cell(", ".join(stmt.get("participants", [])))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| pyfpdf (unmaintained) | fpdf2 | 2020+ | Modern Python 3 support, active development |
| Full font embedding | Automatic subsetting | fpdf2 default | Smaller PDF files |
| Manual Unicode handling | Native TTF/OTF support | fpdf2 | Full Unicode without conversion |
| WeasyPrint system deps | fpdf2 pure Python | N/A (choice) | Simpler deployment |

**Deprecated/outdated:**
- pyfpdf: Unmaintained, use fpdf2 instead
- PyFPDF: Same library, renamed to fpdf2
- reportlab for simple reports: Overkill, fpdf2 is simpler

## Open Questions

Things that couldn't be fully resolved:

1. **Inter font licensing for embedding**
   - What we know: Inter is SIL Open Font License, allows embedding
   - What's unclear: Whether to download from Google Fonts or use official release
   - Recommendation: Download from Google Fonts, include in static/fonts/

2. **PDF/A compliance**
   - What we know: fpdf2 supports PDF/A for archival
   - What's unclear: Whether Dale needs archival-compliant PDFs
   - Recommendation: Start without PDF/A, add if requested

## Sources

### Primary (HIGH confidence)
- [fpdf2 Official Documentation](https://py-pdf.github.io/fpdf2/) - Tutorial, API reference, FastAPI examples
- [fpdf2 Usage in Web APIs](https://py-pdf.github.io/fpdf2/UsageInWebAPI.html) - FastAPI integration pattern
- [fpdf2 Unicode Fonts](https://py-pdf.github.io/fpdf2/Unicode.html) - Custom TTF font embedding
- [fpdf2 Tables](https://py-pdf.github.io/fpdf2/Tables.html) - Table creation and styling
- [fpdf2 PyPI](https://pypi.org/project/fpdf2/) - Current version 2.8.5

### Secondary (MEDIUM confidence)
- [Python PDF Generation Comparison 2025](https://templated.io/blog/generate-pdfs-in-python-with-libraries/) - Library comparison
- [Nutrient Top 10 PDF Libraries](https://www.nutrient.io/blog/top-10-ways-to-generate-pdfs-in-python/) - Use case recommendations

### Tertiary (LOW confidence)
- [WeasyPrint Installation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) - System dependency requirements (verified why NOT to use)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official documentation, PyPI stats, active maintenance
- Architecture: HIGH - Official examples in fpdf2 docs for FastAPI
- Pitfalls: HIGH - Documented in fpdf2 docs and GitHub issues

**Research date:** 2026-01-22
**Valid until:** 2026-03-22 (60 days - fpdf2 is stable, patterns well-established)
