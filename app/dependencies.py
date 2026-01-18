"""
The 55 App - Shared dependencies

FastAPI dependency injection definitions.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.config import Settings


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]


# Database session dependency will be added in Plan 02
# SessionDep = Annotated[Session, Depends(get_session)]
