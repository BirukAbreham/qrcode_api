from fastapi import APIRouter

from qrcode_api.app.api.v1.endpoints import auth, users, qrcodes
from qrcode_api.app.core.config import settings

router = APIRouter(prefix=f"/{settings.API_V1_STR}")

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(qrcodes.router, prefix="/qrcode", tags=["QR Codes"])
