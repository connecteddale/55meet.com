"""
The 55 App - Sessions Router

Session management and control endpoints for facilitator.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import AuthDep, DbDep
from app.db.models import Team, Member, Session, Response, SessionState

router = APIRouter(prefix="/admin/sessions", tags=["sessions"])
templates = Jinja2Templates(directory="app/templates")


def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.utcnow().strftime("%Y-%m")


@router.get("/team/{team_id}")
async def list_team_sessions(request: Request, team_id: int, auth: AuthDep, db: DbDep):
    """List all sessions for a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return RedirectResponse(url="/admin/teams", status_code=303)

    sessions = db.query(Session).filter(
        Session.team_id == team_id
    ).order_by(Session.month.desc()).all()

    return templates.TemplateResponse(
        "admin/sessions/list.html",
        {"request": request, "team": team, "sessions": sessions}
    )


@router.get("/team/{team_id}/create")
async def create_session_form(request: Request, team_id: int, auth: AuthDep, db: DbDep):
    """Show create session form."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return RedirectResponse(url="/admin/teams", status_code=303)

    return templates.TemplateResponse(
        "admin/sessions/create.html",
        {
            "request": request,
            "team": team,
            "current_month": get_current_month(),
            "error": None
        }
    )


@router.post("/team/{team_id}/create")
async def create_session(
    request: Request,
    team_id: int,
    auth: AuthDep,
    db: DbDep,
    month: str = Form(...)
):
    """Create a new session for a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return RedirectResponse(url="/admin/teams", status_code=303)

    # Validate month format (YYYY-MM)
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        return templates.TemplateResponse(
            "admin/sessions/create.html",
            {
                "request": request,
                "team": team,
                "current_month": get_current_month(),
                "error": "Invalid month format. Use YYYY-MM."
            }
        )

    # Check for existing session
    existing = db.query(Session).filter(
        Session.team_id == team_id,
        Session.month == month
    ).first()
    if existing:
        return templates.TemplateResponse(
            "admin/sessions/create.html",
            {
                "request": request,
                "team": team,
                "current_month": get_current_month(),
                "error": f"Session for {month} already exists."
            }
        )

    # Create session in draft state
    session = Session(
        team_id=team_id,
        month=month,
        state=SessionState.DRAFT
    )
    db.add(session)
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session.id}", status_code=303)


@router.get("/{session_id}")
async def view_session(request: Request, session_id: int, auth: AuthDep, db: DbDep):
    """View session details and control panel."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        return RedirectResponse(url="/admin/teams", status_code=303)

    team = session.team
    members = db.query(Member).filter(Member.team_id == team.id).order_by(Member.name).all()

    # Get response status for each member
    responses = db.query(Response).filter(Response.session_id == session_id).all()
    responded_member_ids = {r.member_id for r in responses}

    member_status = []
    for member in members:
        member_status.append({
            "id": member.id,
            "name": member.name,
            "submitted": member.id in responded_member_ids
        })

    return templates.TemplateResponse(
        "admin/sessions/view.html",
        {
            "request": request,
            "session": session,
            "team": team,
            "member_status": member_status,
            "total_members": len(members),
            "submitted_count": len(responded_member_ids)
        }
    )


@router.post("/{session_id}/start")
async def start_capturing(session_id: int, auth: AuthDep, db: DbDep):
    """Transition session from draft to capturing."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state != SessionState.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start capturing. Session is in '{session.state.value}' state."
        )

    session.state = SessionState.CAPTURING
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.post("/{session_id}/close")
async def close_capture(session_id: int, auth: AuthDep, db: DbDep):
    """Transition session from capturing to closed."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state != SessionState.CAPTURING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot close capture. Session is in '{session.state.value}' state."
        )

    session.state = SessionState.CLOSED
    session.closed_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.post("/{session_id}/reveal")
async def reveal_synthesis(session_id: int, auth: AuthDep, db: DbDep):
    """Transition session from closed to revealed."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state != SessionState.CLOSED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reveal synthesis. Session is in '{session.state.value}' state."
        )

    session.state = SessionState.REVEALED
    session.revealed_at = datetime.utcnow()
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.get("/{session_id}/status")
async def get_session_status(session_id: int, auth: AuthDep, db: DbDep):
    """Get session status for polling (JSON endpoint)."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team
    members = db.query(Member).filter(Member.team_id == team.id).all()
    responses = db.query(Response).filter(Response.session_id == session_id).all()
    responded_member_ids = {r.member_id for r in responses}

    member_status = []
    for member in members:
        member_status.append({
            "id": member.id,
            "name": member.name,
            "submitted": member.id in responded_member_ids
        })

    return JSONResponse({
        "session_id": session_id,
        "state": session.state.value,
        "total_members": len(members),
        "submitted_count": len(responded_member_ids),
        "members": member_status
    })


@router.post("/{session_id}/recalibration")
async def mark_recalibration_complete(
    session_id: int,
    auth: AuthDep,
    db: DbDep,
    completed: bool = Form(...)
):
    """Mark recalibration action as completed."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.recalibration_completed = completed
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)
