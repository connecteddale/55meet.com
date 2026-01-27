"""
The 55 App - Demo Router

Interactive demo for landing page visitors.
Pre-baked content simulates the full 55 experience without database or AI calls.
"""

import random
import time
from typing import Optional

from fastapi import APIRouter, Request
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
