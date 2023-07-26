import secrets
from hashlib import md5
from typing import Any, Union
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from qrcode_api.app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a hashed password and a plain password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: timedelta | None,
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(settings.EXPIRE_MINUTES)

    payload = {
        "exp": expire,
        "sub": str(subject),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_api_key() -> str:
    """Create a random API key."""
    return md5(secrets.token_bytes(32)).hexdigest()
