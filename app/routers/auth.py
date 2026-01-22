"""
The 55 App - Authentication Router

Login and logout routes for facilitator access.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import SettingsDep
from app.services.auth import verify_password, create_session_token

router = APIRouter(prefix="/admin", tags=["auth"])
templates = Jinja2Templates(directory="templates")


@router.get("/login")
async def login_page(request: Request, error: str = None):
    """Render login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error}
    )


@router.post("/login")
async def login(
    request: Request,
    settings: SettingsDep,
    password: str = Form(...)
):
    """Process login form."""
    if not verify_password(password, settings.facilitator_password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid password"},
            status_code=401
        )

    # Create session token and set cookie
    token = create_session_token(settings)
    redirect = RedirectResponse(url="/admin", status_code=303)
    redirect.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400  # 24 hours
    )
    return redirect


@router.get("/logout")
async def logout():
    """Clear session and redirect to login."""
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("session")
    return response
