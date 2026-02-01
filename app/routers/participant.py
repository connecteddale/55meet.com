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
from app.services.images import get_image_library
from app.config import get_settings

router = APIRouter(prefix="/join", tags=["participant"])
templates = Jinja2Templates(directory="templates")

# Database dependency without auth
DbDep = Annotated[Session, Depends(get_db)]


@router.get("")
async def join_form(request: Request, code: str = None):
    """Show team code entry form. Optionally pre-fill from QR code URL."""
    return templates.TemplateResponse(
        "participant/join.html",
        {"request": request, "error": None, "prefill_code": code}
    )


@router.get("/{code}")
async def auto_join(
    request: Request,
    code: str,
    db: DbDep
):
    """Auto-join from URL (e.g. QR code scan). Validates code and skips to appropriate step."""
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

    # Auto-skip month picker if only one session active
    if len(sessions) == 1:
        return RedirectResponse(
            url=f"/join/{code}/session/{sessions[0].id}/name",
            status_code=303
        )

    # Multiple sessions - show month picker
    return RedirectResponse(
        url=f"/join/{code}/session",
        status_code=303
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
            {"request": request, "error": "Team code not found. Please check and try again.", "prefill_code": code}
        )

    # Get sessions in CAPTURING state
    active_sessions = db.query(SessionModel).filter(
        SessionModel.team_id == team.id,
        SessionModel.state == SessionState.CAPTURING
    ).order_by(SessionModel.month.desc()).all()

    if not active_sessions:
        return templates.TemplateResponse(
            "participant/join.html",
            {"request": request, "error": "No active sessions for this team. Please wait for your facilitator.", "prefill_code": code}
        )

    # Auto-skip month picker if only one session active
    if len(active_sessions) == 1:
        return RedirectResponse(
            url=f"/join/{team.code}/session/{active_sessions[0].id}/name",
            status_code=303
        )

    # Multiple sessions - show month picker
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

    # Auto-skip month picker if only one session active
    if len(sessions) == 1:
        return RedirectResponse(
            url=f"/join/{code}/session/{sessions[0].id}/name",
            status_code=303
        )

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

    # Redirect directly to respond page (strategy screen bypassed)
    return RedirectResponse(
        url=f"/join/{code}/session/{session_id}/member/{member_id}/respond",
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
    """Redirect to respond page (strategy screen bypassed for reduced flow)."""
    code = code.strip().upper()

    # Redirect directly to respond - keeps old bookmarks/links working
    return RedirectResponse(
        url=f"/join/{code}/session/{session_id}/member/{member_id}/respond",
        status_code=303
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
        if existing_response:
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

    # Get shuffled images using session ID as seed for consistent ordering
    settings = get_settings()
    library = get_image_library()
    per_page = settings.images_per_page  # Default 20

    shuffled_images = library.get_shuffled_images(seed=session.id, limit=60)
    total_images = len(shuffled_images)

    # Generate page ranges based on image indices (0-indexed)
    image_pages = []
    for start_idx in range(0, total_images, per_page):
        end_idx = min(start_idx + per_page - 1, total_images - 1)
        image_pages.append((start_idx, end_idx))

    # Backward compatibility: if using old 55-image set with numbered IDs,
    # keep numbered approach for current template
    if total_images == 55 and all(img.id.isdigit() for img in shuffled_images[:5]):
        shuffled_numbers = [int(img.id) for img in shuffled_images]
        image_pages = []
        for start_idx in range(0, 55, 6):
            end_idx = min(start_idx + 5, 54)
            # Page contains these image numbers
            page_numbers = shuffled_numbers[start_idx:end_idx + 1]
            image_pages.append((start_idx, end_idx, page_numbers))

    return templates.TemplateResponse(
        "participant/respond.html",
        {
            "request": request,
            "team": team,
            "session": session,
            "member": member,
            "existing_response": existing_response,
            "image_pages": image_pages,
            "images": shuffled_images,
            "total_images": total_images,
            "per_page": per_page,
        }
    )


@router.post("/{code}/session/{session_id}/member/{member_id}/respond")
async def submit_response(
    request: Request,
    code: str,
    session_id: int,
    member_id: int,
    db: DbDep,
    image_id: str = Form(...),
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

    # Validate image_id (non-empty string)
    image_id = image_id.strip()
    if not image_id:
        raise HTTPException(status_code=400, detail="Image selection required")

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
        existing.image_id = image_id
        existing.bullets = bullets_json
    else:
        # Insert new response
        response = Response(
            session_id=session_id,
            member_id=member_id,
            image_id=image_id,
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


@router.get("/{code}/session/{session_id}/synthesis")
async def view_synthesis(
    request: Request,
    code: str,
    session_id: int,
    db: DbDep
):
    """Show synthesis results when session is revealed."""
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

    # Validate session state
    if session.state in (SessionState.CAPTURING, SessionState.CLOSED):
        # Synthesis not ready yet - redirect to waiting
        # Find a member to redirect with (use first response's member)
        response = db.query(Response).filter(Response.session_id == session_id).first()
        if response:
            return RedirectResponse(
                url=f"/join/{code}/session/{session_id}/member/{response.member_id}/waiting",
                status_code=303
            )
        # No responses yet - back to join
        return RedirectResponse(url="/join", status_code=303)

    # Session is REVEALED - show synthesis
    # Parse synthesis_statements from JSON
    synthesis_statements = []
    if session.synthesis_statements:
        try:
            synthesis_statements = json.loads(session.synthesis_statements)
        except json.JSONDecodeError:
            synthesis_statements = []

    # Fetch individual responses with member names and images
    responses = db.query(Response).filter(Response.session_id == session_id).all()
    image_library = get_image_library()
    individual_responses = []
    for resp in responses:
        member = db.query(Member).filter(Member.id == resp.member_id).first()
        if member:
            try:
                bullets = json.loads(resp.bullets) if resp.bullets else []
            except json.JSONDecodeError:
                bullets = []
            # Get image URL from image_id
            filename = image_library.get_filename_by_id(resp.image_id)
            image_url = f"/static/images/library/reducedlive/{filename}" if filename else None
            individual_responses.append({
                "name": member.name,
                "image_url": image_url,
                "bullets": bullets
            })

    return templates.TemplateResponse(
        "participant/synthesis.html",
        {
            "request": request,
            "team": team,
            "session": session,
            "synthesis_themes": session.synthesis_themes,
            "synthesis_statements": synthesis_statements,
            "synthesis_gap_type": session.synthesis_gap_type,
            "individual_responses": individual_responses
        }
    )


@router.get("/{code}/session/{session_id}/status")
async def get_participant_status(
    code: str,
    session_id: int,
    member_id: int = None,
    db: Session = Depends(get_db)
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

    # Build synthesis progress for CLOSED state
    synthesis_progress = None
    if session.state == SessionState.CLOSED:
        if session.synthesis_themes is None:
            synthesis_progress = {
                "status": "pending",
                "message": "Preparing analysis..."
            }
        elif session.synthesis_themes.lower() == "generating...":
            synthesis_progress = {
                "status": "generating",
                "message": "Analyzing team responses..."
            }
        elif "failed" in session.synthesis_themes.lower():
            synthesis_progress = {
                "status": "failed",
                "message": "Analysis encountered an issue. Your facilitator will retry."
            }
        else:
            synthesis_progress = {
                "status": "complete",
                "message": "Analysis complete!"
            }

    # Build submitted member names (privacy: names only, no IDs)
    submitted_ids = {r.member_id for r in responses}
    submitted_members = [
        {"name": m.name}
        for m in members
        if m.id in submitted_ids
    ]

    # Build unsubmitted member names
    unsubmitted_members = [
        {"name": m.name}
        for m in members
        if m.id not in submitted_ids
    ]

    # Build member's own response data when closed (for display on waiting screen)
    my_response = None
    if member_id and session.state == SessionState.CLOSED:
        response = db.query(Response).filter(
            Response.session_id == session_id,
            Response.member_id == member_id
        ).first()
        if response:
            import json
            bullets = json.loads(response.bullets) if response.bullets else []
            my_response = {
                "image_url": f"/images/full/{response.image_id}.webp",
                "bullets": bullets,
                "strategy_statement": team.strategy_statement or "",
                "image_prompt": team.image_prompt or "Choose the image that best represents how you as a team are executing your strategy.",
                "bullet_prompt": team.bullet_prompt or "Describe why this image describes how you are executing your strategy"
            }

    return JSONResponse({
        "session_id": session_id,
        "state": session.state.value,
        "total_members": len(members),
        "submitted_count": len(responses),
        "submitted_members": submitted_members,
        "unsubmitted_members": unsubmitted_members,
        "can_edit": session.state == SessionState.CAPTURING,
        "synthesis_progress": synthesis_progress,
        "my_response": my_response
    })
