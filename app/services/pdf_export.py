"""
PDF Export Service for The 55 App.

Generates presentation-ready session reports using fpdf2.
"""

import json
from pathlib import Path
from typing import List

from fpdf import FPDF


# Design system colors (RGB tuples)
TEXT_PRIMARY = (29, 29, 31)      # #1d1d1f
TEXT_SECONDARY = (110, 110, 115)  # #6e6e73
TEXT_TERTIARY = (134, 134, 139)   # #86868b
DIVIDER = (210, 210, 215)         # #d2d2d7

# Font directory path
FONT_DIR = Path(__file__).parent.parent.parent / "static" / "fonts"


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
        self.set_text_color(*TEXT_SECONDARY)
        self.cell(0, 10, f"The 55 | {self.team_name}", align="L")
        self.ln(10)
        self.set_draw_color(*DIVIDER)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        """Page footer with date and page number."""
        self.set_y(-15)
        self.set_font("Inter", size=8)
        self.set_text_color(*TEXT_TERTIARY)
        self.cell(0, 10, f"{self.session_date} | Page {self.page_no()}", align="C")

    def add_title(self, text: str):
        """Add main title."""
        self.set_font("Inter", style="B", size=24)
        self.set_text_color(*TEXT_PRIMARY)
        self.cell(0, 15, text, align="L")
        self.ln(20)

    def add_section_header(self, text: str):
        """Add section header."""
        self.set_font("Inter", style="B", size=14)
        self.set_text_color(*TEXT_PRIMARY)
        self.cell(0, 10, text, align="L")
        self.ln(8)

    def add_body_text(self, text: str):
        """Add body paragraph with word wrapping."""
        self.set_font("Inter", size=11)
        self.set_text_color(*TEXT_PRIMARY)
        self.multi_cell(0, 6, text)
        self.ln(5)

    def add_attributed_insight(self, statement: str, participants: List[str]):
        """Add insight with bullet and attribution."""
        # Bullet point and statement
        self.set_font("Inter", size=11)
        self.set_text_color(*TEXT_PRIMARY)

        # Save x position for multi-line handling
        bullet_x = self.get_x()
        self.cell(5, 6, chr(8226), align="L")  # bullet character

        # Statement text with wrapping
        self.multi_cell(0, 6, statement)

        # Attribution in secondary color, italic
        self.set_font("Inter", style="I", size=10)
        self.set_text_color(*TEXT_SECONDARY)
        self.set_x(bullet_x + 5)  # indent under bullet
        self.cell(0, 5, f"({', '.join(participants)})")
        self.ln(8)


def generate_session_pdf(session, team) -> bytes:
    """
    Generate a PDF report for a session.

    Args:
        session: Session model instance with synthesis data
        team: Team model instance with team info

    Returns:
        PDF content as bytes
    """
    # Create fresh PDF instance (instances are not reusable)
    pdf = SessionReportPDF(
        team_name=team.team_name,
        session_date=session.month
    )
    pdf.add_page()

    # Title
    pdf.add_title("Session Report")

    # Strategy statement section
    if team.strategy_statement:
        pdf.add_section_header("Strategy Statement")
        pdf.add_body_text(team.strategy_statement)
        pdf.ln(5)

    # Synthesis themes (What We Heard)
    if session.synthesis_themes and session.synthesis_themes.lower() != "generating...":
        # Skip error messages
        themes_lower = session.synthesis_themes.lower()
        if "failed" not in themes_lower and "insufficient" not in themes_lower:
            pdf.add_section_header("What We Heard")
            pdf.add_body_text(session.synthesis_themes)
            pdf.ln(5)

    # Key Insights with attribution
    if session.synthesis_statements:
        try:
            statements = json.loads(session.synthesis_statements)
            if statements:
                pdf.add_section_header("Key Insights")
                for stmt in statements:
                    pdf.add_attributed_insight(
                        stmt.get("statement", ""),
                        stmt.get("participants", [])
                    )
        except (json.JSONDecodeError, TypeError):
            pass

    # Return PDF bytes
    return bytes(pdf.output())
