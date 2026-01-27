"""
The 55 App - Demo Router

Interactive demo for landing page visitors.
Pre-baked content simulates the full 55 experience without database or AI calls.
"""

import random
import time
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/demo", tags=["demo"])
templates = Jinja2Templates(directory="templates")


# Pre-baked demo data - ClearBrief fictional company
DEMO_COMPANY = {
    "name": "ClearBrief",
    "industry": "Legal Tech SaaS",
    "revenue": "$65M ARR",
    "strategy": "Help law firms win clients through transparency - open billing, open matters, no surprises."
}

# Name pools for team members - each role has 3 options
NAME_POOLS = {
    "CTO": ["Sarah Chen", "Sarah Martinez", "Sarah Williams"],
    "CFO": ["James Park", "James Thompson", "James Rivera"],
    "VP Sales": ["Michael Lee", "Michael Johnson", "Michael Okafor"],
    "COO": ["Rachel Kim", "Rachel Garcia", "Rachel Patel"]
}


def get_demo_seed(request: Request) -> int:
    """Get deterministic seed for demo shuffling.

    Uses query param if provided, otherwise generates hourly-changing seed.
    This ensures team names stay consistent within an hour for returning visitors.
    """
    # Check for explicit seed in query params
    seed_param = request.query_params.get("seed")
    if seed_param:
        try:
            return int(seed_param)
        except (ValueError, TypeError):
            pass

    # Default: hourly seed for consistent experience
    return int(time.time()) // 3600


def get_shuffled_team(seed: int) -> list:
    """Generate team members with deterministically shuffled names.

    Uses seeded random to ensure same seed always produces same team.
    Each role gets one name picked from its pool.
    """
    rng = random.Random(seed)

    team = []
    for role, names in NAME_POOLS.items():
        # Pick one name from the pool for this role
        name = rng.choice(names)
        first_name = name.split()[0]
        team.append({
            "name": name,
            "role": role,
            "first_name": first_name
        })

    return team


@router.get("")
async def demo_intro(request: Request):
    """Demo intro page - ClearBrief company context and team members."""
    seed = get_demo_seed(request)
    team_members = get_shuffled_team(seed)

    return templates.TemplateResponse(
        "demo/intro.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_members": team_members,
            "seed": seed
        }
    )


# Pre-baked team responses - each shows Alignment gap indicators
# These are matched with team members by role during rendering
DEMO_RESPONSES = [
    {
        "role": "CTO",
        "image_filename": "maze-in-a-green-field-2026-01-06-11-09-08-utc.jpg",
        "bullets": [
            "We're building features but product and sales aren't synced on what clients actually need first"
        ]
    },
    {
        "role": "CFO",
        "image_filename": "athlete-passing-relay-baton-2026-01-05-06-20-17-utc.jpg",
        "bullets": [
            "Projects start strong but stall at the handoff between dev and client success"
        ]
    },
    {
        "role": "VP Sales",
        "image_filename": "foggy-path-2026-01-06-08-58-05-utc.jpg",
        "bullets": [
            "I'm selling capabilities we don't have yet while engineering builds things nobody asked for"
        ]
    },
    {
        "role": "COO",
        "image_filename": "abstract-grunge-retro-clock-gears-background-2026-01-08-23-43-46-utc.jpg",
        "bullets": [
            "Everyone's working hard but the pieces aren't connecting"
        ]
    }
]


def get_response_image_url(filename: str) -> str:
    """Return full URL path for a library image."""
    return f"/static/images/library/reducedlive/{filename}"


@router.get("/signal")
async def demo_signal(request: Request):
    """Demo Signal Capture page - visitor selects image and enters bullets.

    Requires seed parameter for consistent image ordering.
    Stores response in sessionStorage (no database).
    """
    # Seed is required for consistent image ordering
    seed_param = request.query_params.get("seed")
    if not seed_param:
        # Must start from beginning to get proper context
        return RedirectResponse(url="/demo", status_code=302)

    try:
        seed = int(seed_param)
    except (ValueError, TypeError):
        return RedirectResponse(url="/demo", status_code=302)

    team_members = get_shuffled_team(seed)

    return templates.TemplateResponse(
        "demo/signal.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_members": team_members,
            "seed": seed,
            "per_page": 20  # Same as real app
        }
    )


# Pre-baked synthesis data - reveals Alignment gap
# Participant names are placeholders that get replaced with shuffled team names
DEMO_SYNTHESIS = {
    "themes": "Your team is aligned on WHERE you're going, but the WORK isn't fitting together. The drag is in the handoffs - particularly between product development and client-facing teams. Each function is executing independently, creating gaps where value should compound.",
    "gap_type": "Alignment",
    "statements": [
        {
            "statement": "Product development and client-facing teams are operating on different timelines",
            "participants": ["CTO", "VP Sales"]  # Roles - will be replaced with first names
        },
        {
            "statement": "Features are being built without clear alignment to client priorities",
            "participants": ["CTO", "CFO"]
        },
        {
            "statement": "Handoffs between departments are where momentum is lost",
            "participants": ["CFO", "COO"]
        }
    ]
}


@router.get("/responses")
async def demo_responses(request: Request):
    """Demo Responses page - shows visitor's response alongside pre-baked team responses.

    Requires seed parameter for consistent team names.
    Visitor response comes from sessionStorage (populated by JavaScript).
    """
    # Seed is required for consistent team names
    seed_param = request.query_params.get("seed")
    if not seed_param:
        # Must start from beginning to get proper context
        return RedirectResponse(url="/demo", status_code=302)

    try:
        seed = int(seed_param)
    except (ValueError, TypeError):
        return RedirectResponse(url="/demo", status_code=302)

    # Get shuffled team members
    team_members = get_shuffled_team(seed)

    # Build team responses by combining team member names with pre-baked responses
    team_responses = []
    for member in team_members:
        # Find matching response by role
        response_data = next(
            (r for r in DEMO_RESPONSES if r["role"] == member["role"]),
            None
        )
        if response_data:
            team_responses.append({
                "name": member["name"],
                "first_name": member["first_name"],
                "role": member["role"],
                "image_url": get_response_image_url(response_data["image_filename"]),
                "bullets": response_data["bullets"]
            })

    return templates.TemplateResponse(
        "demo/responses.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_responses": team_responses,
            "seed": seed
        }
    )


@router.get("/synthesis")
async def demo_synthesis(request: Request):
    """Demo Synthesis page - reveals the Alignment gap with pre-baked analysis.

    Requires seed parameter for consistent team names.
    Clears sessionStorage on load so next demo starts fresh.
    """
    # Seed is required for consistent team names
    seed_param = request.query_params.get("seed")
    if not seed_param:
        # Must start from beginning to get proper context
        return RedirectResponse(url="/demo", status_code=302)

    try:
        seed = int(seed_param)
    except (ValueError, TypeError):
        return RedirectResponse(url="/demo", status_code=302)

    # Get shuffled team to map role -> first_name
    team_members = get_shuffled_team(seed)
    role_to_name = {member["role"]: member["first_name"] for member in team_members}

    # Build synthesis data with actual team member names
    synthesis_statements = []
    for stmt in DEMO_SYNTHESIS["statements"]:
        # Replace role placeholders with actual first names
        participant_names = [role_to_name.get(role, role) for role in stmt["participants"]]
        synthesis_statements.append({
            "statement": stmt["statement"],
            "participants": participant_names
        })

    return templates.TemplateResponse(
        "demo/synthesis.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "synthesis_themes": DEMO_SYNTHESIS["themes"],
            "synthesis_gap_type": DEMO_SYNTHESIS["gap_type"],
            "synthesis_statements": synthesis_statements,
            "seed": seed
        }
    )
