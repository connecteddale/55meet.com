"""
The 55 App - Admin Router

Protected dashboard routes for facilitator.
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.dependencies import AuthDep

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
async def admin_dashboard(request: Request, auth: AuthDep):
    """Admin dashboard - requires authentication."""
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request}
    )
