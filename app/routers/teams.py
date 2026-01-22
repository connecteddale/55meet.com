"""
The 55 App - Teams Router

Team management endpoints for facilitator.
"""

import secrets
import string
from typing import Optional

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func

from app.dependencies import AuthDep, DbDep
from app.db.models import Team

router = APIRouter(prefix="/admin/teams", tags=["teams"])
templates = Jinja2Templates(directory="templates")


def generate_team_code() -> str:
    """Generate a unique 6-character team code."""
    chars = string.ascii_uppercase + string.digits
    # Exclude confusing characters: 0, O, I, 1, L
    chars = chars.replace('0', '').replace('O', '').replace('I', '').replace('1', '').replace('L', '')
    return ''.join(secrets.choice(chars) for _ in range(6))


@router.get("")
async def list_teams(request: Request, auth: AuthDep, db: DbDep):
    """List all teams."""
    teams = db.query(Team).order_by(Team.company_name, Team.team_name).all()
    return templates.TemplateResponse(
        "admin/teams/list.html",
        {"request": request, "teams": teams}
    )


@router.get("/create")
async def create_team_form(request: Request, auth: AuthDep):
    """Show create team form."""
    return templates.TemplateResponse(
        "admin/teams/create.html",
        {"request": request, "error": None}
    )


@router.post("/create")
async def create_team(
    request: Request,
    auth: AuthDep,
    db: DbDep,
    company_name: str = Form(...),
    team_name: str = Form(...),
    code: Optional[str] = Form(None),
    strategy_statement: Optional[str] = Form(None)
):
    """Create a new team."""
    # Generate code if not provided
    if not code:
        code = generate_team_code()

    # Normalize code to uppercase
    code = code.upper().strip()

    # Check for duplicate code (case-insensitive)
    existing = db.query(Team).filter(func.upper(Team.code) == code).first()
    if existing:
        return templates.TemplateResponse(
            "admin/teams/create.html",
            {"request": request, "error": f"Team code '{code}' already exists"}
        )

    # Create team
    team = Team(
        company_name=company_name.strip(),
        team_name=team_name.strip(),
        code=code,
        strategy_statement=strategy_statement.strip() if strategy_statement else None
    )
    db.add(team)
    db.commit()

    return RedirectResponse(url="/admin/teams", status_code=303)


@router.get("/{team_id}")
async def edit_team_form(request: Request, team_id: int, auth: AuthDep, db: DbDep):
    """Show edit team form."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return RedirectResponse(url="/admin/teams", status_code=303)

    return templates.TemplateResponse(
        "admin/teams/edit.html",
        {"request": request, "team": team, "error": None}
    )


@router.post("/{team_id}")
async def update_team(
    request: Request,
    team_id: int,
    auth: AuthDep,
    db: DbDep,
    company_name: str = Form(...),
    team_name: str = Form(...),
    code: str = Form(...),
    strategy_statement: Optional[str] = Form(None),
    image_prompt: Optional[str] = Form(None),
    bullet_prompt: Optional[str] = Form(None)
):
    """Update team details."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return RedirectResponse(url="/admin/teams", status_code=303)

    # Normalize code
    code = code.upper().strip()

    # Check for duplicate code (excluding current team)
    existing = db.query(Team).filter(
        func.upper(Team.code) == code,
        Team.id != team_id
    ).first()
    if existing:
        return templates.TemplateResponse(
            "admin/teams/edit.html",
            {"request": request, "team": team, "error": f"Team code '{code}' already exists"}
        )

    # Update team
    team.company_name = company_name.strip()
    team.team_name = team_name.strip()
    team.code = code
    team.strategy_statement = strategy_statement.strip() if strategy_statement else None
    team.image_prompt = image_prompt.strip() if image_prompt else None
    team.bullet_prompt = bullet_prompt.strip() if bullet_prompt else None
    db.commit()

    return RedirectResponse(url="/admin/teams", status_code=303)


@router.post("/{team_id}/delete")
async def delete_team(team_id: int, auth: AuthDep, db: DbDep):
    """Delete a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if team:
        db.delete(team)
        db.commit()

    return RedirectResponse(url="/admin/teams", status_code=303)
