"""
The 55 App - Admin Router

Protected dashboard routes for facilitator.
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.dependencies import AuthDep, DbDep
from app.db.models import Team

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
async def admin_dashboard(request: Request, auth: AuthDep, db: DbDep):
    """Admin dashboard - requires authentication."""
    teams = db.query(Team).order_by(Team.company_name, Team.team_name).all()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "teams": teams}
    )
