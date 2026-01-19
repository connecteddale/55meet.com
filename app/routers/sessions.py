"""
The 55 App - Sessions Router

Session management and control endpoints for facilitator.
"""

from datetime import datetime
from typing import Optional

import json

from fastapi import APIRouter, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import joinedload

from app.dependencies import AuthDep, DbDep
from app.db.models import Team, Member, Session, Response, SessionState
from app.services.synthesis import run_synthesis_task

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


@router.get("/history")
async def session_history(request: Request, auth: AuthDep, db: DbDep):
    """View all sessions across all teams."""
    sessions = db.query(Session).options(
        joinedload(Session.team)
    ).order_by(Session.month.desc()).all()

    return templates.TemplateResponse(
        "admin/sessions/history.html",
        {"request": request, "sessions": sessions}
    )


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

    # Parse synthesis data
    synthesis_statements = None
    if session.synthesis_statements:
        try:
            synthesis_statements = json.loads(session.synthesis_statements)
        except (json.JSONDecodeError, TypeError):
            synthesis_statements = []

    # Synthesis is pending if CLOSED state and no synthesis_themes yet
    synthesis_pending = (
        session.state == SessionState.CLOSED and
        session.synthesis_themes is None
    )

    return templates.TemplateResponse(
        "admin/sessions/view.html",
        {
            "request": request,
            "session": session,
            "team": team,
            "member_status": member_status,
            "total_members": len(members),
            "submitted_count": len(responded_member_ids),
            "synthesis_themes": session.synthesis_themes,
            "synthesis_statements": synthesis_statements,
            "synthesis_gap_type": session.synthesis_gap_type,
            "synthesis_pending": synthesis_pending
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


@router.post("/{session_id}/synthesize")
async def trigger_synthesis(
    session_id: int,
    background_tasks: BackgroundTasks,
    auth: AuthDep,
    db: DbDep
):
    """Trigger synthesis generation for a closed session."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state != SessionState.CLOSED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot generate synthesis. Session is in '{session.state.value}' state. Must be 'closed'."
        )

    # Check if synthesis already exists and succeeded
    if session.synthesis_themes is not None:
        # If it's an error message, allow retry
        if "failed" not in session.synthesis_themes.lower() and "insufficient" not in session.synthesis_themes.lower():
            # Already have valid synthesis, just redirect
            return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)

    # Add background task to generate synthesis
    background_tasks.add_task(run_synthesis_task, session_id)

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

    # Synthesis status for CLOSED state polling
    has_synthesis = session.synthesis_themes is not None
    synthesis_pending = (
        session.state == SessionState.CLOSED and
        session.synthesis_themes is None
    )

    return JSONResponse({
        "session_id": session_id,
        "state": session.state.value,
        "total_members": len(members),
        "submitted_count": len(responded_member_ids),
        "members": member_status,
        "has_synthesis": has_synthesis,
        "synthesis_pending": synthesis_pending
    })


@router.post("/{session_id}/notes")
async def update_session_notes(
    session_id: int,
    auth: AuthDep,
    db: DbDep,
    facilitator_notes: Optional[str] = Form(None),
    recalibration_action: Optional[str] = Form(None)
):
    """Save facilitator notes and recalibration action text."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state != SessionState.REVEALED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot save notes. Session must be in 'revealed' state, but is '{session.state.value}'."
        )

    # Update facilitator notes if provided
    if facilitator_notes is not None:
        cleaned = facilitator_notes.strip()
        session.facilitator_notes = cleaned if cleaned else None

    # Update recalibration action if provided
    if recalibration_action is not None:
        cleaned = recalibration_action.strip()
        session.recalibration_action = cleaned if cleaned else None

    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


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


@router.get("/{session_id}/present")
async def present_session(request: Request, session_id: int, auth: AuthDep, db: DbDep):
    """Projector-friendly presentation view of synthesis."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state != SessionState.REVEALED:
        return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)

    # Parse synthesis statements
    synthesis_statements = None
    if session.synthesis_statements:
        try:
            synthesis_statements = json.loads(session.synthesis_statements)
        except (json.JSONDecodeError, TypeError):
            synthesis_statements = []

    return templates.TemplateResponse(
        "admin/sessions/present.html",
        {
            "request": request,
            "session": session,
            "team": session.team,
            "synthesis_themes": session.synthesis_themes,
            "synthesis_statements": synthesis_statements,
            "synthesis_gap_type": session.synthesis_gap_type
        }
    )


@router.get("/{session_id}/export")
async def export_session(session_id: int, auth: AuthDep, db: DbDep):
    """Export session data as JSON."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team
    responses = db.query(Response).filter(Response.session_id == session_id).all()

    # Build response data
    response_data = []
    for r in responses:
        member = db.query(Member).filter(Member.id == r.member_id).first()
        response_data.append({
            "participant": member.name if member else "Unknown",
            "image_number": r.image_number,
            "bullets": json.loads(r.bullets) if r.bullets else [],
            "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None
        })

    # Parse synthesis statements
    synthesis_statements = None
    if session.synthesis_statements:
        try:
            synthesis_statements = json.loads(session.synthesis_statements)
        except (json.JSONDecodeError, TypeError):
            synthesis_statements = []

    export_data = {
        "session": {
            "id": session.id,
            "month": session.month,
            "state": session.state.value,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "closed_at": session.closed_at.isoformat() if session.closed_at else None,
            "revealed_at": session.revealed_at.isoformat() if session.revealed_at else None
        },
        "team": {
            "company_name": team.company_name,
            "team_name": team.team_name,
            "strategy_statement": team.strategy_statement
        },
        "responses": response_data,
        "synthesis": {
            "themes": session.synthesis_themes,
            "statements": synthesis_statements,
            "gap_type": session.synthesis_gap_type
        },
        "facilitator": {
            "notes": session.facilitator_notes,
            "recalibration_action": session.recalibration_action,
            "recalibration_completed": session.recalibration_completed
        }
    }

    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": f"attachment; filename=session-{session.month}-{team.team_name}.json"}
    )
