"""
The 55 App - Admin Router

Protected dashboard routes for facilitator.
"""

from datetime import datetime

from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import joinedload

from app.dependencies import AuthDep, DbDep, SettingsDep
from app.db.models import Team, Session, SessionState
from app.services.auth import verify_password, hash_password, update_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")


def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.utcnow().strftime("%Y-%m")


@router.get("")
async def admin_dashboard(request: Request, auth: AuthDep, db: DbDep):
    """Admin dashboard - sessions-first command center."""
    current_month = get_current_month()

    active_sessions = db.query(Session).options(
        joinedload(Session.team)
    ).filter(
        Session.month == current_month,
        Session.state != SessionState.REVEALED
    ).order_by(Session.created_at.desc()).all()

    recent_sessions = db.query(Session).options(
        joinedload(Session.team)
    ).filter(
        Session.state == SessionState.REVEALED
    ).order_by(Session.revealed_at.desc()).limit(5).all()

    teams = db.query(Team).order_by(Team.company_name, Team.team_name).all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "active_sessions": active_sessions,
            "recent_sessions": recent_sessions,
            "teams": teams,
            "current_month": current_month
        }
    )


@router.get("/settings")
async def settings_page(request: Request, auth: AuthDep):
    """Facilitator settings page."""
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "success": None, "error": None}
    )


@router.post("/settings/password")
async def change_password(
    request: Request,
    auth: AuthDep,
    settings: SettingsDep,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Process password change."""
    # Verify current password
    if not verify_password(current_password, settings.facilitator_password_hash):
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "error": "Current password is incorrect", "success": None}
        )

    # Validate new password length
    if len(new_password) < 8:
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "error": "Password must be at least 8 characters", "success": None}
        )

    # Validate passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "error": "Passwords do not match", "success": None}
        )

    # Generate and store new hash
    new_hash = hash_password(new_password)
    if not update_password_hash(new_hash):
        return templates.TemplateResponse(
            "admin/settings.html",
            {"request": request, "error": "Failed to update password file", "success": None}
        )

    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "success": "Password updated successfully. Changes take effect on next restart.", "error": None}
    )


@router.get("/api/companies")
async def api_companies(auth: AuthDep, db: DbDep):
    """Get unique company names with their teams, alphabetically sorted."""
    from sqlalchemy.orm import joinedload as jl
    teams = db.query(Team).options(jl(Team.members)).order_by(Team.company_name, Team.team_name).all()

    # Group teams by company
    companies = {}
    for team in teams:
        company_name = team.company_name or "Unknown"
        if company_name not in companies:
            companies[company_name] = []
        companies[company_name].append({
            "id": team.id,
            "team_name": team.team_name,
            "code": team.code,
            "member_count": len(team.members) if team.members else 0
        })

    # Convert to sorted list
    result = [
        {"name": name, "teams": teams}
        for name, teams in sorted(companies.items())
    ]

    return JSONResponse(result)


@router.get("/api/teams")
async def api_teams(
    auth: AuthDep,
    db: DbDep,
    search: str = Query(default="", description="Search term for filtering teams")
):
    """Get all teams, alphabetically sorted, with optional search."""
    from sqlalchemy.orm import joinedload as jl
    query = db.query(Team).options(jl(Team.members)).order_by(Team.company_name, Team.team_name)

    teams = query.all()

    # Filter by search term if provided
    if search:
        search_lower = search.lower()
        teams = [
            t for t in teams
            if search_lower in (t.company_name or '').lower()
            or search_lower in (t.team_name or '').lower()
            or search_lower in (t.code or '').lower()
        ]

    result = [
        {
            "id": team.id,
            "company_name": team.company_name or '',
            "team_name": team.team_name or '',
            "code": team.code or '',
            "member_count": len(team.members) if team.members else 0
        }
        for team in teams
    ]

    return JSONResponse(result)


@router.get("/api/sessions")
async def api_sessions(
    auth: AuthDep,
    db: DbDep,
    search: str = Query(default="", description="Search term for filtering sessions")
):
    """Get all sessions, sorted by created_at DESC, with optional search."""
    sessions = db.query(Session).options(
        joinedload(Session.team)
    ).order_by(Session.created_at.desc()).all()

    # Filter by search term if provided
    if search:
        search_lower = search.lower()
        sessions = [
            s for s in sessions
            if search_lower in (s.team.company_name or '').lower()
            or search_lower in (s.team.team_name or '').lower()
            or search_lower in (s.month or '')
        ]

    result = [
        {
            "id": session.id,
            "month": session.month or '',
            "state": session.state.value if session.state else 'draft',
            "company_name": session.team.company_name if session.team else '',
            "team_name": session.team.team_name if session.team else '',
            "team_id": session.team.id if session.team else None,
            "created_at": session.created_at.isoformat() if session.created_at else None
        }
        for session in sessions
    ]

    return JSONResponse(result)
