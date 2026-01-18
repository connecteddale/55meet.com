"""
The 55 App - Shared dependencies

FastAPI dependency injection definitions.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.database import get_db


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
DbDep = Annotated[Session, Depends(get_db)]
