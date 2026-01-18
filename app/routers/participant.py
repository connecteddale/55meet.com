"""
The 55 App - Participant Router

Public endpoints for participant session entry flow.
No authentication required - participants join via team code.
"""

import json
from typing import Annotated, Optional

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

    # Check if member already has a response
    existing_response = db.query(Response).filter(
        Response.session_id == session_id,
        Response.member_id == member_id
    ).first()

    return templates.TemplateResponse(
        "participant/strategy.html",
        {
            "request": request,
            "team": team,
            "session": session,
            "member": member,
            "has_response": existing_response is not None
        }
    )


@router.get("/{code}/session/{session_id}/member/{member_id}/respond")
async def respond_form(
    request: Request,
    code: str,
    session_id: int,
    member_id: int,
    db: DbDep
):
    """Show image browser for response selection."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return RedirectResponse(url="/join", status_code=303)

    # Get session (any state for now, check state separately)
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
        return RedirectResponse(
            url=f"/join/{code}/session/{session_id}/name",
            status_code=303
        )

    # Check for existing response
    existing_response = db.query(Response).filter(
        Response.session_id == session_id,
        Response.member_id == member_id
    ).first()

    # State validation: handle non-CAPTURING states gracefully
    if session.state != SessionState.CAPTURING:
        if session.state == SessionState.DRAFT:
            # Session not active yet
            return RedirectResponse(url="/join", status_code=303)
        elif existing_response:
            # CLOSED or REVEALED with existing response - go to waiting
            return RedirectResponse(
                url=f"/join/{code}/session/{session_id}/member/{member_id}/waiting",
                status_code=303
            )
        else:
            # CLOSED or REVEALED without response - show session closed message
            return templates.TemplateResponse(
                "participant/session_closed.html",
                {
                    "request": request,
                    "team": team,
                    "session": session,
                    "member": member
                }
            )

    # Generate pagination ranges: [(1,6), (7,12), ..., (49,54), (55,55)]
    image_pages = []
    for start in range(1, 56, 6):
        end = min(start + 5, 55)
        image_pages.append((start, end))

    return templates.TemplateResponse(
        "participant/respond.html",
        {
            "request": request,
            "team": team,
            "session": session,
            "member": member,
            "existing_response": existing_response,
            "image_pages": image_pages
        }
    )


@router.post("/{code}/session/{session_id}/member/{member_id}/respond")
async def submit_response(
    request: Request,
    code: str,
    session_id: int,
    member_id: int,
    db: DbDep,
    image_number: int = Form(...),
    bullets: str = Form(...)
):
    """Process response submission."""
    code = code.strip().upper()
    team = db.query(Team).filter(Team.code == code).first()
    if not team:
        return RedirectResponse(url="/join", status_code=303)

    # Get session (any state for now, check state separately)
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.team_id == team.id
    ).first()

    if not session:
        return RedirectResponse(url=f"/join/{code}/session", status_code=303)

    # Check if session is still accepting submissions
    if session.state != SessionState.CAPTURING:
        # Check if member already has a response
        existing_response = db.query(Response).filter(
            Response.session_id == session_id,
            Response.member_id == member_id
        ).first()

        if existing_response:
            # Response was saved before state changed
            return RedirectResponse(
                url=f"/join/{code}/session/{session_id}/member/{member_id}/waiting",
                status_code=303
            )
        else:
            # Session closed before submission could complete
            return templates.TemplateResponse(
                "participant/session_closed.html",
                {
                    "request": request,
                    "team": team,
                    "session": session,
                    "member": db.query(Member).filter(Member.id == member_id).first(),
                    "submission_error": "The session was closed before your response could be saved."
                }
            )

    member = db.query(Member).filter(
        Member.id == member_id,
        Member.team_id == team.id
    ).first()

    if not member:
        return RedirectResponse(url="/join", status_code=303)

    # Validate image_number (1-55)
    if not 1 <= image_number <= 55:
        raise HTTPException(status_code=400, detail="Invalid image number")

    # Parse and validate bullets JSON
    try:
        bullets_list = json.loads(bullets)
        if not isinstance(bullets_list, list):
            raise ValueError("Bullets must be a list")
        # Filter out empty strings and whitespace-only strings
        bullets_list = [b.strip() for b in bullets_list if b.strip()]
        if not 1 <= len(bullets_list) <= 5:
            raise ValueError("Must have 1-5 bullet points")
        # Validate each bullet max 500 chars
        for bullet in bullets_list:
            if len(bullet) > 500:
                raise ValueError("Each bullet point must be 500 characters or less")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid bullets format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Store validated bullets back as JSON
    bullets_json = json.dumps(bullets_list)

    # Check for existing response
    existing = db.query(Response).filter(
        Response.session_id == session_id,
        Response.member_id == member_id
    ).first()

    if existing:
        # Update existing response
        existing.image_number = image_number
        existing.bullets = bullets_json
    else:
        # Insert new response
        response = Response(
            session_id=session_id,
            member_id=member_id,
            image_number=image_number,
            bullets=bullets_json
        )
        db.add(response)

    db.commit()

    # Redirect to waiting page
    return RedirectResponse(
        url=f"/join/{code}/session/{session_id}/member/{member_id}/waiting",
        status_code=303
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
        "submitted_count": len(responses),
        "can_edit": session.state == SessionState.CAPTURING
    })
