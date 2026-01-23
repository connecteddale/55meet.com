#!/usr/bin/env python3
"""Generate 55 placeholder SVG images for development."""

import os
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "app" / "static" / "images" / "55"

# SVG template - clean, numbered placeholder
SVG_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="{bg_color}"/>
  <text x="200" y="200" font-family="Arial, sans-serif" font-size="120" font-weight="bold"
        fill="{text_color}" text-anchor="middle" dominant-baseline="central">{number}</text>
  <text x="200" y="280" font-family="Arial, sans-serif" font-size="24"
        fill="{text_color}" text-anchor="middle" opacity="0.6">placeholder</text>
</svg>'''

# Color palette for variety
COLORS = [
    ("#e0f2fe", "#0369a1"),  # Sky blue
    ("#dbeafe", "#1d4ed8"),  # Blue
    ("#e0e7ff", "#4338ca"),  # Indigo
    ("#ede9fe", "#6d28d9"),  # Violet
    ("#fae8ff", "#a21caf"),  # Fuchsia
    ("#fce7f3", "#be185d"),  # Pink
    ("#fee2e2", "#b91c1c"),  # Red
    ("#ffedd5", "#c2410c"),  # Orange
    ("#fef3c7", "#b45309"),  # Amber
    ("#fef9c3", "#a16207"),  # Yellow
    ("#ecfccb", "#4d7c0f"),  # Lime
    ("#dcfce7", "#15803d"),  # Green
    ("#d1fae5", "#047857"),  # Emerald
    ("#ccfbf1", "#0f766e"),  # Teal
    ("#cffafe", "#0e7490"),  # Cyan
]

def generate_placeholders():
    """Generate 55 placeholder SVG images."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(1, 56):
        # Cycle through colors
        bg_color, text_color = COLORS[(i - 1) % len(COLORS)]

        # Format number with leading zero
        number_str = f"{i:02d}"

        # Generate SVG
        svg_content = SVG_TEMPLATE.format(
            bg_color=bg_color,
            text_color=text_color,
            number=number_str
        )

        # Write file
        output_path = OUTPUT_DIR / f"{number_str}.svg"
        output_path.write_text(svg_content)
        print(f"Created {output_path.name}")

    print(f"\nGenerated 55 placeholder images in {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_placeholders()
