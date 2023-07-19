from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import EmailStr

from app import schemas
from app.api.v1.deps import get_current_active_user
from app.core.security import get_password_hash
from app.models.user import User


router = APIRouter()


def user_not_found_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The user with this username does not exist",
    )


@router.get("/me", response_model=schemas.User)
def get_current_user(user: User = Depends(get_current_active_user)):
    """Get current active user details"""
    return user


@router.put("/me", response_model=schemas.User)
async def update_current_user(
    password: str | None = Body(None),
    email: EmailStr | None = Body(None),
    user: User = Depends(get_current_active_user),
) -> User:
    """Update current user using provided data."""
    if password is not None:
        user.hashed_password = get_password_hash(password)

    if email is not None:
        user.email = email

    await user.save_changes()

    return user
