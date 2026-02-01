"""
The 55 App - Sessions Router

Session management and control endpoints for facilitator.
"""

from datetime import datetime
from typing import Optional

import json

from fastapi import APIRouter, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import joinedload

from app.dependencies import AuthDep, DbDep
from app.db.models import Team, Member, Session, Response as ResponseModel, SessionState
from app.services.synthesis import run_synthesis_task
from app.services.pdf_export import generate_session_pdf

router = APIRouter(prefix="/admin/sessions", tags=["sessions"])
templates = Jinja2Templates(directory="templates")


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

    # Create session in capturing state (immediately active)
    session = Session(
        team_id=team_id,
        month=month,
        state=SessionState.CAPTURING
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
async def view_session(request: Request, session_id: int, auth: AuthDep, db: DbDep, error: str = None):
    """View session details and control panel."""
    from app.services.images import get_image_library

    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        return RedirectResponse(url="/admin/teams", status_code=303)

    team = session.team
    members = db.query(Member).filter(Member.team_id == team.id).order_by(Member.name).all()
    member_by_id = {m.id: m for m in members}

    # Get response status for each member
    responses = db.query(ResponseModel).filter(ResponseModel.session_id == session_id).all()
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

    # Synthesis status: pending (not started), generating (in progress), or complete
    synthesis_pending = (
        session.state == SessionState.CLOSED and
        session.synthesis_themes is None
    )
    synthesis_generating = (
        session.state == SessionState.CLOSED and
        session.synthesis_themes is not None and
        session.synthesis_themes.lower() == "generating..."
    )

    # Build participant responses with images for display
    image_library = get_image_library()
    participant_responses = []
    for r in responses:
        member = member_by_id.get(r.member_id)
        # Get actual filename from opaque ID
        filename = image_library.get_filename_by_id(r.image_id)
        if filename:
            image_url = f"/static/images/library/reducedlive/{filename}"
        else:
            image_url = None

        bullets = []
        if r.bullets:
            try:
                bullets = json.loads(r.bullets)
            except (json.JSONDecodeError, TypeError):
                bullets = []

        participant_responses.append({
            "name": member.name if member else "Unknown",
            "image_url": image_url,
            "bullets": bullets
        })

    # Don't pass "GENERATING..." as actual themes to display
    display_themes = None
    if session.synthesis_themes and session.synthesis_themes.lower() != "generating...":
        display_themes = session.synthesis_themes

    # Parse suggested recalibrations
    suggested_recalibrations = None
    if session.suggested_recalibrations:
        try:
            suggested_recalibrations = json.loads(session.suggested_recalibrations)
        except (json.JSONDecodeError, TypeError):
            suggested_recalibrations = []

    return templates.TemplateResponse(
        "admin/sessions/view.html",
        {
            "request": request,
            "session": session,
            "team": team,
            "member_status": member_status,
            "total_members": len(members),
            "submitted_count": len(responded_member_ids),
            "synthesis_themes": display_themes,
            "synthesis_statements": synthesis_statements,
            "synthesis_gap_type": session.synthesis_gap_type,
            "synthesis_gap_reasoning": session.synthesis_gap_reasoning,
            "suggested_recalibrations": suggested_recalibrations,
            "synthesis_pending": synthesis_pending,
            "synthesis_generating": synthesis_generating,
            "participant_responses": participant_responses,
            "error": error
        }
    )



@router.post("/{session_id}/close")
async def close_capture(session_id: int, background_tasks: BackgroundTasks, auth: AuthDep, db: DbDep):
    """Transition session from capturing to closed, then auto-trigger synthesis."""
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

    # Auto-trigger synthesis: set marker and queue background task
    session.synthesis_themes = "GENERATING..."
    db.commit()

    background_tasks.add_task(run_synthesis_task, session_id)

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.post("/{session_id}/reopen")
async def reopen_capture(session_id: int, auth: AuthDep, db: DbDep):
    """Transition session from closed or revealed back to capturing (for latecomers)."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state not in (SessionState.CLOSED, SessionState.REVEALED):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reopen. Session is in '{session.state.value}' state."
        )

    # Clear synthesis data (will need regeneration)
    session.synthesis_themes = None
    session.synthesis_statements = None
    session.synthesis_gap_type = None

    session.state = SessionState.CAPTURING
    session.closed_at = None  # Reset close timestamp
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.post("/{session_id}/member/{member_id}/clear")
async def clear_member_submission(
    session_id: int,
    member_id: int,
    auth: AuthDep,
    db: DbDep
):
    """Clear a specific participant's submission to allow resubmit."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Only allow clearing during CAPTURING state
    if session.state != SessionState.CAPTURING:
        raise HTTPException(
            status_code=400,
            detail="Can only clear submissions while capturing."
        )

    # Delete the response (hard delete, no audit trail needed)
    response = db.query(ResponseModel).filter(
        ResponseModel.session_id == session_id,
        ResponseModel.member_id == member_id
    ).first()

    if not response:
        raise HTTPException(status_code=404, detail="No submission found")

    db.delete(response)
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.post("/{session_id}/members/add")
async def add_member_from_session(
    session_id: int,
    auth: AuthDep,
    db: DbDep,
    name: str = Form(...)
):
    """Add a new member to the team from the session view."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get the team
    team = db.query(Team).filter(Team.id == session.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check member limit
    member_count = db.query(Member).filter(Member.team_id == team.id).count()
    if member_count >= 55:
        from urllib.parse import quote
        return RedirectResponse(
            url=f"/admin/sessions/{session_id}?error={quote('Maximum 55 members per team')}",
            status_code=303
        )

    # Add member
    name = name.strip()
    if not name:
        return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)

    # Check for duplicate name (case-insensitive)
    from sqlalchemy import func
    existing = db.query(Member).filter(
        Member.team_id == team.id,
        func.lower(Member.name) == name.lower()
    ).first()
    if existing:
        from urllib.parse import quote
        return RedirectResponse(
            url=f"/admin/sessions/{session_id}?error={quote(f'{name} already exists')}",
            status_code=303
        )

    member = Member(team_id=team.id, name=name)
    db.add(member)
    db.commit()

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.post("/{session_id}/members/{member_id}/remove")
async def remove_member_from_session(
    session_id: int,
    member_id: int,
    auth: AuthDep,
    db: DbDep
):
    """Remove a member from the team from the session view."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.team_id == session.team_id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Also delete any responses for this member in this session
    db.query(ResponseModel).filter(
        ResponseModel.session_id == session_id,
        ResponseModel.member_id == member_id
    ).delete()

    db.delete(member)
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

    # Check if synthesis already in progress or completed
    if session.synthesis_themes is not None:
        themes_lower = session.synthesis_themes.lower()
        # If generating, don't start another
        if themes_lower == "generating...":
            return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)
        # If it's an error message, allow retry
        if "failed" not in themes_lower and "insufficient" not in themes_lower:
            # Already have valid synthesis, just redirect
            return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)

    # Set marker to indicate synthesis is in progress (prevents double-click)
    session.synthesis_themes = "GENERATING..."
    db.commit()

    # Add background task to generate synthesis
    background_tasks.add_task(run_synthesis_task, session_id)

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.post("/{session_id}/synthesize/retry")
async def retry_synthesis(
    session_id: int,
    background_tasks: BackgroundTasks,
    auth: AuthDep,
    db: DbDep
):
    """Force regeneration of synthesis, clearing existing data first."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.state not in (SessionState.CLOSED, SessionState.REVEALED):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry synthesis. Session is in '{session.state.value}' state. Must be 'closed' or 'revealed'."
        )

    # Clear existing synthesis data to force regeneration
    session.synthesis_themes = None
    session.synthesis_statements = None
    session.synthesis_gap_type = None
    db.commit()

    # Add background task to generate synthesis
    background_tasks.add_task(run_synthesis_task, session_id)

    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)


@router.get("/{session_id}/synthesis-status")
async def get_synthesis_status(session_id: int, auth: AuthDep, db: DbDep):
    """Get synthesis progress status for polling."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Determine synthesis status
    if session.synthesis_themes is None:
        status = "pending"
        has_error = False
        error_message = None
    elif session.synthesis_themes.lower() == "generating...":
        status = "generating"
        has_error = False
        error_message = None
    elif "failed" in session.synthesis_themes.lower() or "insufficient" in session.synthesis_themes.lower():
        status = "failed"
        has_error = True
        error_message = session.synthesis_themes
    else:
        status = "complete"
        has_error = False
        error_message = None

    return JSONResponse({
        "status": status,
        "has_error": has_error,
        "error_message": error_message
    })


@router.get("/{session_id}/status")
async def get_session_status(session_id: int, auth: AuthDep, db: DbDep):
    """Get session status for polling (JSON endpoint)."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team
    members = db.query(Member).filter(Member.team_id == team.id).all()
    responses = db.query(ResponseModel).filter(ResponseModel.session_id == session_id).all()
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

    # Allow notes in closed (after synthesis) or revealed state
    if session.state not in (SessionState.CLOSED, SessionState.REVEALED):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot save notes. Session must be in 'closed' or 'revealed' state, but is '{session.state.value}'."
        )

    # Update facilitator notes if provided
    if facilitator_notes is not None:
        cleaned = facilitator_notes.strip()
        session.facilitator_notes = cleaned if cleaned else None
        session.facilitator_notes_updated_at = datetime.utcnow()

    # Update recalibration action if provided
    if recalibration_action is not None:
        cleaned = recalibration_action.strip()
        session.recalibration_action = cleaned if cleaned else None
        session.recalibration_action_updated_at = datetime.utcnow()

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


@router.get("/{session_id}/capture")
async def capture_session(request: Request, session_id: int, auth: AuthDep, db: DbDep):
    """Projector-friendly capture view with QR code and status."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Only show in CAPTURING state (redirect otherwise)
    if session.state != SessionState.CAPTURING:
        return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=303)

    team = session.team
    members = db.query(Member).filter(Member.team_id == team.id).order_by(Member.name).all()

    # Get response status for each member
    responses = db.query(ResponseModel).filter(ResponseModel.session_id == session_id).all()
    responded_member_ids = {r.member_id for r in responses}

    member_status = []
    for member in members:
        member_status.append({
            "id": member.id,
            "name": member.name,
            "submitted": member.id in responded_member_ids
        })

    return templates.TemplateResponse(
        "admin/sessions/capture.html",
        {
            "request": request,
            "session": session,
            "team": team,
            "member_status": member_status,
            "total_members": len(members),
            "submitted_count": len(responded_member_ids)
        }
    )


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

    # Query raw responses with image URLs
    responses = db.query(ResponseModel).filter(ResponseModel.session_id == session_id).all()
    raw_responses = []
    for r in responses:
        member = db.query(Member).filter(Member.id == r.member_id).first()
        # Build image URL from image_id (filename stem)
        # Try common extensions in order of preference
        image_url = f"/static/images/library/{r.image_id}.jpg"
        raw_responses.append({
            "participant": member.name if member else "Unknown",
            "image_id": r.image_id,
            "image_url": image_url,
            "bullets": json.loads(r.bullets) if r.bullets else []
        })

    # Check for synthesis failure (for retry UI)
    synthesis_failed = False
    if session.synthesis_themes:
        themes_lower = session.synthesis_themes.lower()
        synthesis_failed = "failed" in themes_lower or "insufficient" in themes_lower

    return templates.TemplateResponse(
        "admin/sessions/present.html",
        {
            "request": request,
            "session": session,
            "team": session.team,
            "synthesis_themes": session.synthesis_themes,
            "synthesis_statements": synthesis_statements,
            "synthesis_gap_type": session.synthesis_gap_type,
            "synthesis_gap_reasoning": session.synthesis_gap_reasoning,
            "raw_responses": raw_responses,
            "synthesis_failed": synthesis_failed
        }
    )


@router.get("/{session_id}/export")
async def export_session(session_id: int, auth: AuthDep, db: DbDep):
    """Export session data as JSON."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team
    responses = db.query(ResponseModel).filter(ResponseModel.session_id == session_id).all()

    # Build response data
    response_data = []
    for r in responses:
        member = db.query(Member).filter(Member.id == r.member_id).first()
        response_data.append({
            "participant": member.name if member else "Unknown",
            "image_id": r.image_id,
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


@router.get("/{session_id}/export/level1")
async def export_level1(session_id: int, auth: AuthDep, db: DbDep):
    """Export Level 1 synthesis data (themes and gap type only)."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team
    export_data = {
        "themes": session.synthesis_themes,
        "gap_type": session.synthesis_gap_type
    }

    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": f"attachment; filename=session-{session.month}-{team.team_name}-level1.json"}
    )


@router.get("/{session_id}/export/level2")
async def export_level2(session_id: int, auth: AuthDep, db: DbDep):
    """Export Level 2 synthesis data (attributed statements)."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team

    # Parse synthesis statements
    statements = []
    if session.synthesis_statements:
        try:
            statements = json.loads(session.synthesis_statements)
        except (json.JSONDecodeError, TypeError):
            statements = []

    export_data = {
        "statements": statements
    }

    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": f"attachment; filename=session-{session.month}-{team.team_name}-level2.json"}
    )


@router.get("/{session_id}/export/level3")
async def export_level3(session_id: int, auth: AuthDep, db: DbDep):
    """Export Level 3 raw data (participant responses)."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team
    responses = db.query(ResponseModel).filter(ResponseModel.session_id == session_id).all()

    # Build response data
    response_data = []
    for r in responses:
        member = db.query(Member).filter(Member.id == r.member_id).first()
        response_data.append({
            "participant": member.name if member else "Unknown",
            "image_id": r.image_id,
            "bullets": json.loads(r.bullets) if r.bullets else [],
            "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None
        })

    export_data = {
        "responses": response_data
    }

    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": f"attachment; filename=session-{session.month}-{team.team_name}-level3.json"}
    )


@router.get("/{session_id}/export/markdown")
async def export_markdown(session_id: int, auth: AuthDep, db: DbDep):
    """Export session data as Markdown for easy viewing/copying."""
    from fastapi.responses import PlainTextResponse

    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team
    responses = db.query(ResponseModel).filter(ResponseModel.session_id == session_id).all()

    # Parse synthesis statements
    synthesis_statements = []
    if session.synthesis_statements:
        try:
            synthesis_statements = json.loads(session.synthesis_statements)
        except (json.JSONDecodeError, TypeError):
            pass

    # Build markdown content
    lines = []
    lines.append(f"# The 55 Session Report")
    lines.append(f"")
    lines.append(f"**Team:** {team.team_name}")
    lines.append(f"**Company:** {team.company_name}")
    lines.append(f"**Session:** {session.month}")
    lines.append(f"")

    if team.strategy_statement:
        lines.append(f"## Strategy Statement")
        lines.append(f"")
        lines.append(f"{team.strategy_statement}")
        lines.append(f"")

    # Facilitator notes section (if any)
    if session.facilitator_notes or session.recalibration_action:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## Facilitator Notes")
        lines.append(f"")
        if session.facilitator_notes:
            lines.append(f"{session.facilitator_notes}")
            lines.append(f"")
        if session.recalibration_action:
            status = "(Completed)" if session.recalibration_completed else "(Pending)"
            lines.append(f"**Recalibration Action** {status}")
            lines.append(f"")
            lines.append(f"{session.recalibration_action}")
            lines.append(f"")

    # Synthesis section
    if session.synthesis_themes:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## What We Heard")
        lines.append(f"")
        lines.append(f"{session.synthesis_themes}")
        lines.append(f"")

        if session.synthesis_gap_type:
            lines.append(f"### Gap Analysis")
            lines.append(f"")
            lines.append(f"**Gap Type:** {session.synthesis_gap_type}")
            if session.synthesis_gap_reasoning:
                lines.append(f"")
                lines.append(f"{session.synthesis_gap_reasoning}")
            lines.append(f"")

    # Key insights
    if synthesis_statements:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## Key Insights")
        lines.append(f"")
        for stmt in synthesis_statements:
            participants = ", ".join(stmt.get("participants", []))
            lines.append(f"- {stmt.get('statement', '')} *({participants})*")
        lines.append(f"")

    # Participant responses
    if responses:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## Participant Responses")
        lines.append(f"")

        for r in responses:
            member = db.query(Member).filter(Member.id == r.member_id).first()
            name = member.name if member else "Unknown"

            bullets = []
            if r.bullets:
                try:
                    bullets = json.loads(r.bullets)
                except (json.JSONDecodeError, TypeError):
                    pass

            lines.append(f"### {name}")
            lines.append(f"")
            for i, bullet in enumerate(bullets, 1):
                lines.append(f"{i}. {bullet}")
            lines.append(f"")

    markdown_content = "\n".join(lines)

    # Clean filename
    safe_team = team.team_name.replace(" ", "-").replace("/", "-")
    filename = f"session-{session.month}-{safe_team}.md"

    return PlainTextResponse(
        content=markdown_content,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/markdown; charset=utf-8"
        }
    )


@router.get("/{session_id}/export/pdf")
async def export_pdf(session_id: int, auth: AuthDep, db: DbDep):
    """Export session data as presentation-ready PDF."""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team

    # Generate PDF bytes
    pdf_bytes = generate_session_pdf(session, team)

    # Clean filename: TeamName-YYYY-MM.pdf
    safe_team = team.team_name.replace(" ", "-").replace("/", "-")
    filename = f"{safe_team}-{session.month}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{session_id}/meeting")
async def meeting_session(request: Request, session_id: int, auth: AuthDep, db: DbDep):
    """Unified meeting screen - combines capture and presentation into single projectable view.

    Works for ALL session states:
    - CAPTURING: Shows QR code and participant status
    - CLOSED: Shows "analyzing" waiting state
    - REVEALED: Shows synthesis with level navigation
    """
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    team = session.team
    members = db.query(Member).filter(Member.team_id == team.id).order_by(Member.name).all()

    # Get response status for each member
    responses = db.query(ResponseModel).filter(ResponseModel.session_id == session_id).all()
    responded_member_ids = {r.member_id for r in responses}

    member_status = []
    for member in members:
        member_status.append({
            "id": member.id,
            "name": member.name,
            "submitted": member.id in responded_member_ids
        })

    # Parse synthesis statements if available
    synthesis_statements = None
    if session.synthesis_statements:
        try:
            synthesis_statements = json.loads(session.synthesis_statements)
        except (json.JSONDecodeError, TypeError):
            synthesis_statements = []

    # Build raw responses with participant names for Level 3
    raw_responses = []
    for r in responses:
        member = db.query(Member).filter(Member.id == r.member_id).first()
        raw_responses.append({
            "participant": member.name if member else "Unknown",
            "bullets": json.loads(r.bullets) if r.bullets else []
        })

    # Check for synthesis failure
    synthesis_failed = False
    if session.synthesis_themes:
        themes_lower = session.synthesis_themes.lower()
        synthesis_failed = "failed" in themes_lower or "insufficient" in themes_lower

    return templates.TemplateResponse(
        "admin/sessions/meeting.html",
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
            "synthesis_gap_reasoning": session.synthesis_gap_reasoning,
            "raw_responses": raw_responses,
            "synthesis_failed": synthesis_failed
        }
    )
