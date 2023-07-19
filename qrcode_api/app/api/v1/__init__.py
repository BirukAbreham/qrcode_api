from fastapi import APIRouter

from app.api.v1.endpoints import auth, users
from app.core.config import settings

router = APIRouter(prefix=f"/{settings.API_V1_STR}")

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
