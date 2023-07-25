import os
import logging
import secrets
from hashlib import md5
from typing import TYPE_CHECKING

import segno
from segno import helpers
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi_utils.cbv import cbv

from app import schemas
from app.api.v1.deps import get_current_active_user, get_current_active_superuser
from app.core.config import settings
from app.models.user import User
from app.models.qrcode import QRCode
from app.utils import paginate

if TYPE_CHECKING:
    from app.utils.types import PaginationDict

router = APIRouter()

logger = logging.getLogger(__name__)


def qrcode_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="QRCode with the file name cannot be found",
    )


@cbv(router)
class BasicUserViews:
    user: User = Depends(get_current_active_user)

    @staticmethod
    def generate_random_str() -> str:
        return md5(secrets.token_bytes(32)).hexdigest()

    @router.post("/", response_model=schemas.QRCode)
    async def basic_qrcode(self, payload: schemas.QRCodeBasicCreate) -> QRCode:
        file_name = f"{self.generate_random_str()}.{payload.file_format}"
        return await self.__generate_qrcode(
            file_name=file_name, data=payload.data, payload=payload
        )

    @router.post("/location", response_model=schemas.QRCode)
    async def location_qrcode(self, payload: schemas.QRCodeLocationCreate) -> QRCode:
        file_name = f"{self.generate_random_str()}.{payload.file_format}"
        geo_uri = helpers.make_geo_data(lat=payload.latitude, lng=payload.longitude)
        return await self.__generate_qrcode(
            file_name=file_name, data=geo_uri, payload=payload
        )

    @router.post("/wifi", response_model=schemas.QRCode)
    async def wifi_qrcode(self, payload: schemas.QRCodeWiFiCreate) -> QRCode:
        file_name = f"{self.generate_random_str()}.{payload.file_format}"
        wifi_data = helpers.make_wifi_data(
            ssid=payload.ssid, password=payload.password, security=payload.security
        )
        return await self.__generate_qrcode(
            file_name=file_name, data=wifi_data, payload=payload
        )

    @router.post("/vCard", response_model=schemas.QRCode)
    async def vCard_qrcode(self, payload: schemas.QRCodeContactCardCreate) -> QRCode:
        file_name = f"{self.generate_random_str()}.{payload.file_format}"
        vCard_data = helpers.make_vcard_data(
            name=payload.name,
            displayname=payload.displayname,
            phone=payload.phone_number,
            email=payload.email,
            url=payload.url,
        )
        return await self.__generate_qrcode(
            file_name=file_name, data=vCard_data, payload=payload
        )

    @router.post("/meCard", response_model=schemas.QRCode)
    async def meCard_qrcode(self, payload: schemas.QRCodeContactCardCreate) -> QRCode:
        file_name = f"{self.generate_random_str()}.{payload.file_format}"
        meCard_data = helpers.make_mecard_data(
            name=payload.name,
            phone=payload.phone_number,
            email=payload.email,
            url=payload.url,
        )
        return await self.__generate_qrcode(
            file_name=file_name, data=meCard_data, payload=payload
        )

    async def __generate_qrcode(self, file_name, data, payload) -> QRCode:
        try:
            qrcode = segno.make(data, micro=payload.micro, error=payload.error_level)
            qrcode.save(
                f"{settings.STATIC_PATH}/{file_name}",
                scale=payload.scale,
                border=payload.border,
                dark=payload.dark.as_hex(),
                light=payload.light.as_hex(),
            )
            new_qrcode = await QRCode(
                qrcode_file=file_name,
                user_id=self.user.id,
            ).insert()
            return schemas.QRCode(**new_qrcode.dict())
        except Exception as error:
            logger.error("QR Code serialization failure", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal Server Error",
            )


@cbv(router)
class SuperuserViews:
    superuser: User = Depends(get_current_active_superuser)

    @router.get("/", response_model=schemas.Paginated[schemas.QRCode])
    async def get_qrcodes(
        self,
        paging: schemas.PaginationParams = Depends(),
        sorting: schemas.SortingParams = Depends(),
    ) -> "PaginationDict":
        return await paginate(QRCode, paging, sorting)

    @router.delete("/{qrcode_file_name}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_qrcode(self, qrcode_file_name: str) -> None:
        qrcode = await QRCode.get_by_file_name(qrcode_file_name)

        if not qrcode:
            raise qrcode_not_found()
        
        file_name = f"{settings.STATIC_PATH}/{qrcode.qrcode_file}"
        if os.path.isfile(file_name):
            os.remove(file_name)

        await qrcode.delete()


@router.get("/{qrcode_file_name}", response_class=FileResponse)
async def fetch_qrcode_file(qrcode_file_name: str):
    return FileResponse(f"{settings.STATIC_PATH}/{qrcode_file_name}")
