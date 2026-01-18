"""
The 55 App - Participant Router

Public endpoints for participant session entry flow.
No authentication required - participants join via team code.
"""

from typing import Annotated

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Team, Member, Session as SessionModel, SessionState, Response

router = APIRouter(prefix="/join", tags=["participant"])
templates = Jinja2Templates(directory="app/templates")

# Database dependency without auth
DbDep = Annotated[Session, Depends(get_db)]


@router.get("")
async def join_form(request: Request, code: str = None):
    """Show team code entry form. Optionally pre-fill from QR code URL."""
    return templates.TemplateResponse(
        "participant/join.html",
        {"request": request, "error": None, "prefill_code": code}
    )


@router.post("")
async def join_team(
    request: Request,
    db: DbDep,
    code: str = Form(...)
):
    """Process team code and redirect to session selection."""
    # Normalize code (uppercase, strip whitespace)
    code = code.strip().upper()

    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return templates.TemplateResponse(
            "participant/join.html",
            {"request": request, "error": "Team code not found. Please check and try again."}
        )

    # Get sessions in CAPTURING state
    active_sessions = db.query(SessionModel).filter(
        SessionModel.team_id == team.id,
        SessionModel.state == SessionState.CAPTURING
    ).order_by(SessionModel.month.desc()).all()

    if not active_sessions:
        return templates.TemplateResponse(
            "participant/join.html",
            {"request": request, "error": "No active sessions for this team. Please wait for your facilitator."}
        )

    # Redirect to session selection
    return RedirectResponse(
        url=f"/join/{team.code}/session",
        status_code=303
    )


@router.get("/{code}/session")
async def select_session_form(
    request: Request,
    code: str,
    db: DbDep
):
    """Show session selection (month stepper)."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return RedirectResponse(url="/join", status_code=303)

    # Get CAPTURING sessions
    sessions = db.query(SessionModel).filter(
        SessionModel.team_id == team.id,
        SessionModel.state == SessionState.CAPTURING
    ).order_by(SessionModel.month.desc()).all()

    if not sessions:
        return RedirectResponse(url="/join", status_code=303)

    return templates.TemplateResponse(
        "participant/select_session.html",
        {
            "request": request,
            "team": team,
            "sessions": sessions,
            "current_session": sessions[0]  # Default to most recent
        }
    )


@router.post("/{code}/session")
async def select_session(
    request: Request,
    code: str,
    db: DbDep,
    session_id: int = Form(...)
):
    """Process session selection and redirect to name selection."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return RedirectResponse(url="/join", status_code=303)

    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.team_id == team.id,
        SessionModel.state == SessionState.CAPTURING
    ).first()

    if not session:
        return RedirectResponse(url=f"/join/{code}/session", status_code=303)

    return RedirectResponse(
        url=f"/join/{code}/session/{session.id}/name",
        status_code=303
    )


@router.get("/{code}/session/{session_id}/name")
async def select_name_form(
    request: Request,
    code: str,
    session_id: int,
    db: DbDep
):
    """Show name selection from team members."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return RedirectResponse(url="/join", status_code=303)

    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.team_id == team.id,
        SessionModel.state == SessionState.CAPTURING
    ).first()

    if not session:
        return RedirectResponse(url=f"/join/{code}/session", status_code=303)

    # Get team members sorted by name
    members = db.query(Member).filter(
        Member.team_id == team.id
    ).order_by(Member.name).all()

    # Get members who already responded
    responded_ids = {
        r.member_id for r in
        db.query(Response.member_id).filter(Response.session_id == session_id).all()
    }

    return templates.TemplateResponse(
        "participant/select_name.html",
        {
            "request": request,
            "team": team,
            "session": session,
            "members": members,
            "responded_ids": responded_ids
        }
    )


@router.post("/{code}/session/{session_id}/name")
async def select_name(
    request: Request,
    code: str,
    session_id: int,
    db: DbDep,
    member_id: int = Form(...)
):
    """Process name selection and redirect to strategy/response."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return RedirectResponse(url="/join", status_code=303)

    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.team_id == team.id,
        SessionModel.state == SessionState.CAPTURING
    ).first()

    if not session:
        return RedirectResponse(url=f"/join/{code}/session", status_code=303)

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.team_id == team.id
    ).first()

    if not member:
        return RedirectResponse(
            url=f"/join/{code}/session/{session_id}/name",
            status_code=303
        )

    # Redirect to strategy confirmation page
    return RedirectResponse(
        url=f"/join/{code}/session/{session_id}/member/{member_id}/strategy",
        status_code=303
    )


@router.get("/{code}/session/{session_id}/member/{member_id}/strategy")
async def show_strategy(
    request: Request,
    code: str,
    session_id: int,
    member_id: int,
    db: DbDep
):
    """Show strategy statement before proceeding to response."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return RedirectResponse(url="/join", status_code=303)

    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.team_id == team.id,
        SessionModel.state == SessionState.CAPTURING
    ).first()

    if not session:
        return RedirectResponse(url=f"/join/{code}/session", status_code=303)

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.team_id == team.id
    ).first()

    if not member:
        return RedirectResponse(
            url=f"/join/{code}/session/{session_id}/name",
            status_code=303
        )

    return templates.TemplateResponse(
        "participant/strategy.html",
        {
            "request": request,
            "team": team,
            "session": session,
            "member": member
        }
    )


@router.get("/{code}/session/{session_id}/member/{member_id}/waiting")
async def waiting_state(
    request: Request,
    code: str,
    session_id: int,
    member_id: int,
    db: DbDep
):
    """Show waiting state while session is being processed."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return RedirectResponse(url="/join", status_code=303)

    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.team_id == team.id
    ).first()

    if not session:
        return RedirectResponse(url=f"/join/{code}/session", status_code=303)

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.team_id == team.id
    ).first()

    if not member:
        return RedirectResponse(url="/join", status_code=303)

    # Check if session is revealed - redirect to synthesis view
    if session.state == SessionState.REVEALED:
        return RedirectResponse(
            url=f"/join/{code}/session/{session_id}/synthesis",
            status_code=303
        )

    return templates.TemplateResponse(
        "participant/waiting.html",
        {
            "request": request,
            "team": team,
            "session": session,
            "member": member
        }
    )


@router.get("/{code}/session/{session_id}/status")
async def get_participant_status(
    code: str,
    session_id: int,
    db: DbDep
):
    """Get session status for participant polling (JSON endpoint)."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.team_id == team.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get member counts
    members = db.query(Member).filter(Member.team_id == team.id).all()
    responses = db.query(Response).filter(Response.session_id == session_id).all()

    return JSONResponse({
        "session_id": session_id,
        "state": session.state.value,
        "total_members": len(members),
        "submitted_count": len(responses)
    })
