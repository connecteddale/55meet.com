"""
The 55 App - Members Router

Team member management endpoints for facilitator.
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import AuthDep, DbDep
from app.db.models import Team, Member

router = APIRouter(prefix="/admin/teams", tags=["members"])
templates = Jinja2Templates(directory="templates")

MAX_MEMBERS = 25


@router.get("/{team_id}/members")
async def list_members(request: Request, team_id: int, auth: AuthDep, db: DbDep):
    """List team members."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return RedirectResponse(url="/admin/teams", status_code=303)

    members = db.query(Member).filter(Member.team_id == team_id).order_by(Member.name).all()
    member_count = len(members)
    can_add = member_count < MAX_MEMBERS

    return templates.TemplateResponse(
        "admin/teams/members.html",
        {
            "request": request,
            "team": team,
            "members": members,
            "member_count": member_count,
            "max_members": MAX_MEMBERS,
            "can_add": can_add,
            "error": None
        }
    )


@router.post("/{team_id}/members")
async def add_member(
    request: Request,
    team_id: int,
    auth: AuthDep,
    db: DbDep,
    name: str = Form(...)
):
    """Add a member to the team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return RedirectResponse(url="/admin/teams", status_code=303)

    # Check member limit
    member_count = db.query(Member).filter(Member.team_id == team_id).count()
    if member_count >= MAX_MEMBERS:
        members = db.query(Member).filter(Member.team_id == team_id).order_by(Member.name).all()
        return templates.TemplateResponse(
            "admin/teams/members.html",
            {
                "request": request,
                "team": team,
                "members": members,
                "member_count": member_count,
                "max_members": MAX_MEMBERS,
                "can_add": False,
                "error": f"Maximum of {MAX_MEMBERS} members reached"
            }
        )

    # Check for duplicate name in team (case-insensitive)
    from sqlalchemy import func
    name = name.strip()
    existing = db.query(Member).filter(
        Member.team_id == team_id,
        func.lower(Member.name) == name.lower()
    ).first()
    if existing:
        members = db.query(Member).filter(Member.team_id == team_id).order_by(Member.name).all()
        return templates.TemplateResponse(
            "admin/teams/members.html",
            {
                "request": request,
                "team": team,
                "members": members,
                "member_count": member_count,
                "max_members": MAX_MEMBERS,
                "can_add": True,
                "error": f"'{name}' is already a member of this team"
            }
        )

    # Add member
    member = Member(team_id=team_id, name=name)
    db.add(member)
    db.commit()

    return RedirectResponse(url=f"/admin/teams/{team_id}/members", status_code=303)


@router.post("/{team_id}/members/{member_id}/delete")
async def remove_member(team_id: int, member_id: int, auth: AuthDep, db: DbDep):
    """Remove a member from the team."""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.team_id == team_id
    ).first()

    if member:
        db.delete(member)
        db.commit()

    return RedirectResponse(url=f"/admin/teams/{team_id}/members", status_code=303)
