"""
The 55 App - Configuration

Settings loaded from environment variables and .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "The 55"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///db/the55.db"

    # Auth
    secret_key: str  # Required - for session signing
    facilitator_password_hash: str  # Required - argon2 hash

    # Claude API
    anthropic_api_key: str = ""  # Optional for dev

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
