"""
The 55 App - Demo Router

Interactive demo for landing page visitors.
Uses real AI synthesis to generate insights from demo user's comments combined with pre-baked team responses.
"""

import json
import random
import time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from pydantic import BaseModel

from anthropic import AsyncAnthropic
from app.schemas import SynthesisOutput

router = APIRouter(prefix="/demo", tags=["demo"])
templates = Jinja2Templates(directory="templates")

# Anthropic client for real synthesis
anthropic_client = AsyncAnthropic()


class DemoSynthesisRequest(BaseModel):
    """Request body for demo synthesis API."""
    seed: int
    bullets: List[str]
    image_id: Optional[str] = None


def no_cache_response(template_response: Response) -> Response:
    """Add no-cache headers to prevent browser caching of demo pages."""
    template_response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    template_response.headers["Pragma"] = "no-cache"
    template_response.headers["Expires"] = "0"
    return template_response


def get_cache_bust() -> str:
    """Generate cache-busting string based on current timestamp."""
    return str(int(time.time()))


# Dynamic year calculation for ARR target
def get_target_year() -> int:
    """Calculate target year as current year + 3."""
    return datetime.now().year + 3


# Pre-baked demo data - ClearBrief fictional company
DEMO_COMPANY = {
    "name": "ClearBrief Inc.",
    "industry": "Legal Tech SaaS",
    "revenue": "$65M ARR",
    "strategy": "Help law firms win clients through transparency - open billing, open matters, no surprises.",
    "current_arr": "$65M ARR",
    "target_arr": "$130M ARR",
}


# Team bios for the team page
TEAM_BIOS = {
    "CTO": "Scaling engineering from 20 to 80 developers while maintaining velocity.",
    "CFO": "Managing $40M in annual runway while preparing for Series C.",
    "VP Sales": "Building enterprise pipeline in a market that doesn't know it needs us yet.",
    "COO": "Connecting product, sales, and success into a coherent customer journey.",
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
    """Demo intro page - combined scrolling intro with company, team, and Snapshot explanation."""
    seed = get_demo_seed(request)
    team_members = get_shuffled_team(seed)

    # Add bios and photos to team members
    for member in team_members:
        member["bio"] = TEAM_BIOS.get(member["role"], "")
        name_key = member["name"].lower().replace(" ", "-")
        member["photo"] = f"/static/images/demo/{name_key}.jpg"

    target_year = get_target_year()

    return no_cache_response(templates.TemplateResponse(
        "demo/intro.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_members": team_members,
            "target_year": target_year,
            "seed": seed
        }
    ))


@router.get("/company")
async def demo_company(request: Request):
    """Demo company page - introduces ClearBrief."""
    return no_cache_response(templates.TemplateResponse(
        "demo/company.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
        }
    ))


@router.get("/strategy")
async def demo_strategy(request: Request):
    """Demo strategy page - shows ARR goals and 3AM strategy."""
    target_year = get_target_year()

    return no_cache_response(templates.TemplateResponse(
        "demo/strategy.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "target_year": target_year,
        }
    ))


@router.get("/team")
async def demo_team(request: Request):
    """Demo team page - ClearBrief leadership team with photos and bios."""
    seed = get_demo_seed(request)
    team_members = get_shuffled_team(seed)

    # Add bios and photos to team members
    for member in team_members:
        member["bio"] = TEAM_BIOS.get(member["role"], "")
        # Photo filename based on full name (lowercase, hyphenated)
        name_key = member["name"].lower().replace(" ", "-")
        member["photo"] = f"/static/images/demo/{name_key}.jpg"

    target_year = get_target_year()

    return no_cache_response(templates.TemplateResponse(
        "demo/team.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_members": team_members,
            "team_bios": TEAM_BIOS,
            "target_year": target_year,
            "seed": seed
        }
    ))


@router.get("/prepare")
async def demo_prepare(request: Request):
    """Demo prepare page - explains Snapshot before starting."""
    # Seed is required for consistent team tracking
    seed_param = request.query_params.get("seed")
    if not seed_param:
        return RedirectResponse(url="/demo", status_code=302)

    try:
        seed = int(seed_param)
    except (ValueError, TypeError):
        return RedirectResponse(url="/demo", status_code=302)

    target_year = get_target_year()

    return no_cache_response(templates.TemplateResponse(
        "demo/prepare.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "target_year": target_year,
            "seed": seed
        }
    ))


@router.get("/prompt")
async def demo_prompt(request: Request):
    """Demo prompt page - shows strategy and invites Snapshot."""
    # Seed is required for consistent team tracking
    seed_param = request.query_params.get("seed")
    if not seed_param:
        return RedirectResponse(url="/demo", status_code=302)

    try:
        seed = int(seed_param)
    except (ValueError, TypeError):
        return RedirectResponse(url="/demo", status_code=302)

    target_year = get_target_year()

    return no_cache_response(templates.TemplateResponse(
        "demo/prompt.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "target_year": target_year,
            "seed": seed
        }
    ))


# Pre-baked team responses - each shows Alignment gap indicators
# These are matched with team members by role during rendering
DEMO_RESPONSES = [
    {
        "role": "CTO",
        "image_filename": "maze-in-a-green-field-2026-01-06-11-09-08-utc.jpg",
        "bullets": [
            "We're building features but product and sales aren't synced on what clients actually need first",
            "Engineering velocity is high but we keep pivoting mid-sprint",
            "The roadmap changes every board meeting"
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
            "I'm selling capabilities we don't have yet while engineering builds things nobody asked for",
            "Clients keep asking for transparency features we promised six months ago",
            "The pricing model doesn't reflect our actual value prop",
            "Win rate is down but nobody wants to talk about why"
        ]
    },
    {
        "role": "COO",
        "image_filename": "abstract-grunge-retro-clock-gears-background-2026-01-08-23-43-46-utc.jpg",
        "bullets": [
            "Everyone's working hard but the pieces aren't connecting",
            "We have three different definitions of 'transparency' across departments"
        ]
    }
]


def get_response_image_url(filename: str) -> str:
    """Return full URL path for a library image."""
    return f"/static/images/library/reducedlive/{filename}"


@router.get("/signal")
async def demo_signal(request: Request):
    """Demo Snapshot page - visitor selects image and enters bullets.

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
    target_year = get_target_year()

    return no_cache_response(templates.TemplateResponse(
        "demo/signal.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_members": team_members,
            "target_year": target_year,
            "seed": seed,
            "per_page": 60,  # All images on one page
            "cache_bust": get_cache_bust()
        }
    ))


# Pre-baked synthesis data - reveals Alignment gap
# Participant names are placeholders that get replaced with shuffled team names
DEMO_SYNTHESIS = {
    "themes": "Your team is aligned on WHERE you're going, but the WORK isn't fitting together. The drag is in the handoffs - particularly between product development and client-facing teams. Each function is executing independently, creating gaps where value should compound.",
    "gap_type": "Alignment",
    "statements": [
        {
            "name": "Timeline Mismatch",
            "statement": "Product development and client-facing teams are operating on different timelines",
            "participants": ["CTO", "VP Sales"]  # Roles - will be replaced with first names
        },
        {
            "name": "Priority Disconnect",
            "statement": "Features are being built without clear alignment to client priorities",
            "participants": ["CTO", "CFO"]
        },
        {
            "name": "Handoff Friction",
            "statement": "Handoffs between departments are where momentum is lost",
            "participants": ["CFO", "COO"]
        }
    ]
}


@router.get("/layers")
async def demo_layers(request: Request):
    """Demo Layers page - explains the three layers of aggregation before showing responses.

    Requires seed parameter for consistent team names.
    Multi-slide presentation explaining facilitator process.
    """
    # Seed is required for consistent team names
    seed_param = request.query_params.get("seed")
    if not seed_param:
        return RedirectResponse(url="/demo", status_code=302)

    try:
        seed = int(seed_param)
    except (ValueError, TypeError):
        return RedirectResponse(url="/demo", status_code=302)

    # Get shuffled team members
    team_members = get_shuffled_team(seed)
    target_year = get_target_year()

    # Map role -> first_name for synthesis statements
    role_to_name = {member["role"]: member["first_name"] for member in team_members}

    # Build synthesis statements with actual names
    synthesis_statements = []
    for stmt in DEMO_SYNTHESIS["statements"]:
        participant_names = [role_to_name.get(role, role) for role in stmt["participants"]]
        synthesis_statements.append({
            "name": stmt.get("name", ""),
            "statement": stmt["statement"],
            "participants": participant_names
        })

    # Build team responses for Layer 3 preview
    team_responses = []
    for member in team_members:
        response_data = next(
            (r for r in DEMO_RESPONSES if r["role"] == member["role"]),
            None
        )
        if response_data:
            name_key = member["name"].lower().replace(" ", "-")
            photo_url = f"/static/images/demo/{name_key}.jpg"
            team_responses.append({
                "name": member["name"],
                "first_name": member["first_name"],
                "role": member["role"],
                "photo_url": photo_url,
                "image_url": get_response_image_url(response_data["image_filename"]),
                "bullets": response_data["bullets"]
            })

    return no_cache_response(templates.TemplateResponse(
        "demo/layers.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "target_year": target_year,
            "seed": seed,
            "synthesis_themes": DEMO_SYNTHESIS["themes"],
            "synthesis_statements": synthesis_statements,
            "team_responses": team_responses
        }
    ))


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
    target_year = get_target_year()

    # Build team responses by combining team member names with pre-baked responses
    team_responses = []
    for member in team_members:
        # Find matching response by role
        response_data = next(
            (r for r in DEMO_RESPONSES if r["role"] == member["role"]),
            None
        )
        if response_data:
            # Generate photo URL from member name
            name_key = member["name"].lower().replace(" ", "-")
            photo_url = f"/static/images/demo/{name_key}.jpg"
            team_responses.append({
                "name": member["name"],
                "first_name": member["first_name"],
                "role": member["role"],
                "photo_url": photo_url,
                "image_url": get_response_image_url(response_data["image_filename"]),
                "bullets": response_data["bullets"]
            })

    return no_cache_response(templates.TemplateResponse(
        "demo/responses.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "team_responses": team_responses,
            "target_year": target_year,
            "seed": seed
        }
    ))


def build_demo_synthesis_prompt(responses: List[dict], strategy_statement: str) -> str:
    """Build prompt for demo synthesis - same as live app."""
    responses_text = "\n\n".join([
        f"**{r['name']}** (Image: {r.get('image_id', 'unknown')}):\n" +
        "\n".join(f"- {b}" for b in r['bullets'])
        for r in responses
    ])

    json_schema = SynthesisOutput.model_json_schema()

    return f"""You are analyzing responses from a leadership team's monthly alignment diagnostic.

## CRITICAL REQUIREMENT - READ FIRST
The participant named "You" is the CEO who just completed this exercise. Their comments MUST be included.
In the attributed statements section, "You" MUST appear as a participant in at least 1 statement.
If you fail to include "You" in the output, the synthesis is invalid.

## Context
The team's strategy statement (the "3AM test" - what someone should know at 3AM):
"{strategy_statement}"

## Team Responses
Each team member selected an image representing their current state and provided bullet points explaining their choice:

{responses_text}

## Your Task
Synthesize these responses into four parts:

1. **Themes** (2-4 sentences): High-level summary of what the team is experiencing. Focus on patterns across responses.

2. **Attributed Statements**: Specific insights with attribution. Each statement needs:
   - A short 1-3 word **name** that captures the theme (e.g., "Timeline Mismatch", "Priority Disconnect", "Handoff Friction")
   - The full statement describing the insight
   - The names of team members whose responses support it
   Every person must appear in at least one statement. Each participant should recognise their comments reflected in the themes.

3. **Gap Diagnosis**: Identify the primary gap type from exactly one of these three options:
   - **Direction**: Team lacks shared understanding of goals or priorities
   - **Alignment**: Team's work is disconnected or uncoordinated
   - **Commitment**: Individual interests override collective success

4. **Gap Reasoning** (2-3 sentences): Explain WHY you diagnosed this specific gap type. Reference specific evidence from the responses that led to this conclusion.

5. **Suggested Recalibrations**: Provide exactly 3 specific, actionable recalibration actions the team could take to address the diagnosed gap.

## Output Format
Respond ONLY with valid JSON matching this schema:
```json
{json.dumps(json_schema, indent=2)}
```

IMPORTANT - VALIDATION RULES:
- gap_type MUST be exactly one of: "Direction", "Alignment", or "Commitment"
- gap_reasoning MUST explain WHY this gap type was chosen based on evidence
- statements array should contain 3-6 attributed insights
- Each statement MUST have a short 1-3 word "name" that captures the theme
- "You" MUST appear in the participants array of at least 1 statement (this is the CEO - mandatory)
- All other team members should appear in at least one statement
- suggested_recalibrations MUST contain exactly 3 actionable items

FAILURE TO INCLUDE "You" IN AT LEAST 1 STATEMENT WILL INVALIDATE THE RESPONSE."""


@router.post("/api/synthesize")
async def demo_synthesize_api(request_body: DemoSynthesisRequest):
    """Generate real AI synthesis from demo user's comments combined with team responses.

    This endpoint is called via AJAX from the layers page to generate
    real synthesis that includes the demo user's actual comments.
    """
    try:
        seed = request_body.seed
        user_bullets = request_body.bullets
        user_image_id = request_body.image_id or "user-selected"

        # Validate we have at least one bullet
        if not user_bullets or len(user_bullets) == 0:
            return JSONResponse(
                status_code=400,
                content={"error": "At least one bullet point is required"}
            )

        # Get team members for this seed
        team_members = get_shuffled_team(seed)

        # Build all responses: team + demo user
        all_responses = []

        # Add demo user's response first (as CEO / "You")
        all_responses.append({
            "name": "You",
            "image_id": user_image_id,
            "bullets": user_bullets
        })

        # Add pre-baked team responses
        for member in team_members:
            response_data = next(
                (r for r in DEMO_RESPONSES if r["role"] == member["role"]),
                None
            )
            if response_data:
                all_responses.append({
                    "name": member["first_name"],
                    "image_id": response_data["image_filename"],
                    "bullets": response_data["bullets"]
                })

        # Build prompt and call Claude
        prompt = build_demo_synthesis_prompt(all_responses, DEMO_COMPANY["strategy"])

        message = await anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        response_text = message.content[0].text

        # Handle potential markdown code block wrapping
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        result_data = json.loads(response_text)
        result = SynthesisOutput(**result_data)

        # Validate that "You" appears in statements - fix if missing
        statements_data = [s.model_dump() for s in result.statements]
        you_included = any("You" in s.get("participants", []) for s in statements_data)

        if not you_included:
            # Claude didn't include "You" - inject into first statement
            print("WARNING: AI did not include 'You' in synthesis - injecting")
            if statements_data:
                statements_data[0]["participants"].append("You")
        else:
            print("OK: AI included 'You' in synthesis")

        # Return synthesis data
        return JSONResponse(content={
            "themes": result.themes,
            "gap_type": result.gap_type,
            "gap_reasoning": result.gap_reasoning,
            "statements": statements_data,
            "suggested_recalibrations": result.suggested_recalibrations
        })

    except Exception as e:
        print(f"Demo synthesis error: {e}")
        # Return fallback pre-baked synthesis on error
        team_members = get_shuffled_team(request_body.seed)
        role_to_name = {member["role"]: member["first_name"] for member in team_members}

        fallback_statements = []
        for stmt in DEMO_SYNTHESIS["statements"]:
            participant_names = [role_to_name.get(role, role) for role in stmt["participants"]]
            fallback_statements.append({
                "name": stmt.get("name", ""),
                "statement": stmt["statement"],
                "participants": participant_names
            })

        return JSONResponse(content={
            "themes": DEMO_SYNTHESIS["themes"],
            "gap_type": DEMO_SYNTHESIS["gap_type"],
            "gap_reasoning": "Analysis based on team response patterns.",
            "statements": fallback_statements,
            "suggested_recalibrations": [
                "Schedule weekly cross-functional sync between product and sales",
                "Create shared definition of 'transparency' across all departments",
                "Implement handoff checklist for dev-to-client transitions"
            ],
            "fallback": True
        })


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
    target_year = get_target_year()

    # Build synthesis data with actual team member names
    synthesis_statements = []
    for stmt in DEMO_SYNTHESIS["statements"]:
        # Replace role placeholders with actual first names
        participant_names = [role_to_name.get(role, role) for role in stmt["participants"]]
        synthesis_statements.append({
            "name": stmt.get("name", ""),
            "statement": stmt["statement"],
            "participants": participant_names
        })

    # Build team responses for Layer 3 (Individual Comments)
    team_responses = []
    for member in team_members:
        response_data = next(
            (r for r in DEMO_RESPONSES if r["role"] == member["role"]),
            None
        )
        if response_data:
            name_key = member["name"].lower().replace(" ", "-")
            photo_url = f"/static/images/demo/{name_key}.jpg"
            team_responses.append({
                "name": member["name"],
                "first_name": member["first_name"],
                "role": member["role"],
                "photo_url": photo_url,
                "bullets": response_data["bullets"]
            })

    return no_cache_response(templates.TemplateResponse(
        "demo/synthesis.html",
        {
            "request": request,
            "company": DEMO_COMPANY,
            "synthesis_themes": DEMO_SYNTHESIS["themes"],
            "synthesis_gap_type": DEMO_SYNTHESIS["gap_type"],
            "synthesis_gap_reasoning": DEMO_SYNTHESIS.get("gap_reasoning", ""),
            "synthesis_statements": synthesis_statements,
            "team_responses": team_responses,
            "target_year": target_year,
            "seed": seed
        }
    ))
