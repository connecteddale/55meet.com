"""
The 55 App - Shared dependencies

FastAPI dependency injection definitions.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.database import get_db


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
DbDep = Annotated[Session, Depends(get_db)]


async def require_auth(request: Request, settings: SettingsDep):
    """Dependency that requires facilitator authentication."""
    from app.services.auth import verify_session_token

    token = request.cookies.get("session")
    if not token or not verify_session_token(token, settings):
        raise HTTPException(
            status_code=303,
            headers={"Location": "/admin/login"}
        )
    return True


AuthDep = Annotated[bool, Depends(require_auth)]
