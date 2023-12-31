import os
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import EmailStr
from fastapi_utils.cbv import cbv

from qrcode_api.app import schemas
from qrcode_api.app.api.v1.deps import (
    get_current_active_user,
    get_current_active_superuser,
)
from qrcode_api.app.core.config import settings
from qrcode_api.app.core.security import get_password_hash
from qrcode_api.app.models.user import User
from qrcode_api.app.models.qrcode import QRCode
from qrcode_api.app.utils import paginate

if TYPE_CHECKING:
    from app.utils.types import PaginationDict

router = APIRouter()


def user_not_found_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The user with this username does not exist",
    )


@router.post(
    "/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
async def sign_up_user(user_sign_up: schemas.UserSignUp) -> User:
    """Sign up a user into the database."""
    user = await User.get_by_username(username=user_sign_up.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists"
        )

    user = await User.get_by_email(email=user_sign_up.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists"
        )

    data = user_sign_up.dict()
    data["hashed_password"] = get_password_hash(data.pop("password"))
    return await User(**data).insert()


@cbv(router)
class BasicUserViews:
    user: User = Depends(get_current_active_user)

    @router.get("/me", response_model=schemas.User)
    def get_current_user(self) -> User:
        """Get current active user details"""
        return self.user

    @router.put("/me", response_model=schemas.User)
    async def update_current_user(
        self,
        password: str | None = Body(None),
        email: EmailStr | None = Body(None),
    ) -> User:
        """Update current user using provided data."""
        if password is not None:
            self.user.hashed_password = get_password_hash(password)

        if email is not None:
            self.user.email = email

        await self.user.save_changes()

        return self.user

    @router.get("/me/qrcodes", response_model=schemas.Paginated[schemas.QRCode])
    async def get_current_user_qrcodes(
        self,
        paging: schemas.PaginationParams = Depends(),
        sorting: schemas.SortingParams = Depends(),
    ) -> dict[str, Any]:
        """Get current active user's qrcodes."""
        data = await QRCode.get_by_user(
            user_id=self.user.id,
            paging=paging,
            sorting=sorting,
        )
        return {
            "page": paging.page,
            "per_page": paging.per_page,
            "total": await QRCode.find(QRCode.user_id == self.user.id).count(),
            "data": data,
        }

    @router.delete(
        "/me/qrcodes/{qrcode_file_name}", status_code=status.HTTP_204_NO_CONTENT
    )
    async def delete_qrcode(self, qrcode_file_name: str) -> None:
        qrcode = await QRCode.get_by_file_name(file_name=qrcode_file_name)
        if not qrcode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QRCode with the file name cannot be found",
            )
        if qrcode.user_id != self.user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )

        file_name = f"{settings.STATIC_PATH}/{qrcode.qrcode_file}"
        if os.path.isfile(file_name):
            os.remove(file_name)

        await qrcode.delete()


@cbv(router)
class SuperuserViews:
    superuser: User = Depends(get_current_active_superuser)

    @router.get("/", response_model=schemas.Paginated[schemas.User])
    async def get_users(
        self,
        paging: schemas.PaginationParams = Depends(),
        sorting: schemas.SortingParams = Depends(),
    ) -> "PaginationDict":
        return await paginate(User, paging, sorting)

    @router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
    async def create_user(self, user_in: schemas.UserCreate) -> User:
        """Create new user in the database"""
        user = await User.get_by_username(username=user_in.username)

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user associated with this username already exists",
            )

        data = user_in.dict()
        data["hashed_password"] = get_password_hash(data.pop("password"))
        return await User(**data).insert()

    @router.get("/{username}", response_model=schemas.User)
    async def get_user_by_username(
        self,
        username: str,
    ) -> User:
        """Get a specific user by username."""
        user = await User.get_by_username(username=username)

        if not user:
            raise user_not_found_error

        return user

    @router.put("/{username}", response_model=schemas.User)
    async def update_user_by_username(
        self,
        username: str,
        user_in: schemas.UserUpdate,
    ) -> User:
        """Update a specific user by username."""
        user = await User.get_by_username(username=username)

        if not user:
            raise user_not_found_error()

        update_data = user_in.dict(exclude_unset=True)
        await user.set(update_data)
        return user
