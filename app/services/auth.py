"""
The 55 App - Authentication Service

Password verification and session token management.
"""

from pwdlib import PasswordHash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.config import Settings

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return password_hash.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return password_hash.hash(password)


def create_session_token(settings: Settings) -> str:
    """Create a signed session token."""
    serializer = URLSafeTimedSerializer(settings.secret_key)
    return serializer.dumps({"facilitator": True})


def verify_session_token(token: str, settings: Settings, max_age: int = 86400) -> bool:
    """Verify a session token (default 24h expiry)."""
    serializer = URLSafeTimedSerializer(settings.secret_key)
    try:
        data = serializer.loads(token, max_age=max_age)
        return data.get("facilitator") is True
    except (BadSignature, SignatureExpired):
        return False
