# The 55 App - Routers package

from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.images import router as images_router
from app.routers.teams import router as teams_router
from app.routers.members import router as members_router

__all__ = ["auth_router", "admin_router", "images_router", "teams_router", "members_router"]
