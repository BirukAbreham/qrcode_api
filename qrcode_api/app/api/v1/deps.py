from typing import cast

from beanie import PydanticObjectId
from pydantic import ValidationError
from jose import jwt, JWTError
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyQuery, OAuth2PasswordBearer

from app import schemas
from app.core.config import settings
from app.models import User


bearer_token = OAuth2PasswordBearer(
    tokenUrl=f"/api/{settings.API_V1_STR}/auth/access-token",
    auto_error=False,
)

api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def authenticate_bearer_token(token: str) -> User | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        data = schemas.AuthTokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
    else:
        return await User.get(cast(PydanticObjectId, data.sub))


async def get_current_user(
    api_key: str | None = Depends(api_key_query),
    token: str | None = Depends(bearer_token),
) -> User:
    """Gets the current user from the database."""
    if api_key:  # API Key has priority over Bearer token
        user = await User.get_by_api_key(api_key=api_key)
    elif token:
        user = await authenticate_bearer_token(token)
    else:
        # This is the exception that is raised by the Depends() call
        # when the user is not authenticated and auto_error is True.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )

    if not user:
        if api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Gets the current active user from the database."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return current_user
