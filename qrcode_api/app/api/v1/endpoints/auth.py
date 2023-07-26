from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from qrcode_api.app import schemas
from qrcode_api.app.core.config import settings
from qrcode_api.app.core.security import create_access_token, create_api_key
from qrcode_api.app.api.v1.deps import get_current_active_user
from qrcode_api.app.models import User

router = APIRouter(
    responses={
        401: {
            "description": "Unauthorized, invalid credentials or access token",
        },
    },
)


@router.post(
    "/access-token",
    response_model=schemas.AuthToken,
    description="Retrieve an access token for the given username and password.",
)
async def generate_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Get an access token for future requests."""
    user = await User.authenticate(
        username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    expires_in = timedelta(minutes=settings.EXPIRE_MINUTES)

    return {
        "access_token": create_access_token(user.id, expires_delta=expires_in),
        "token_type": "bearer",
    }


@router.post(
    "/api-key",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
)
async def generate_new_api_key(user: User = Depends(get_current_active_user)) -> User:
    """Create a new API key for current user."""
    user.api_key = create_api_key()
    await user.save_changes()
    return user
