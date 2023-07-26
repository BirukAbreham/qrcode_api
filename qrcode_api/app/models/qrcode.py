from datetime import datetime
from typing import Optional, TYPE_CHECKING

from beanie import Document, PydanticObjectId
from pydantic.fields import Field

if TYPE_CHECKING:
    from qrcode_api.app.schemas import PaginationParams, SortingParams


class QRCode(Document):
    qrcode_file: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[PydanticObjectId] = None

    @classmethod
    async def get_by_user(
        cls,
        *,
        user_id: PydanticObjectId,
        paging: "PaginationParams",
        sorting: "SortingParams"
    ) -> list["QRCode"]:
        return (
            await cls.find(cls.user_id == user_id)
            .skip(paging.skip)
            .limit(paging.limit)
            .sort((sorting.sort, sorting.order.direction))
            .to_list()
        )

    @classmethod
    async def get_by_id(cls, *, qrcode_id: PydanticObjectId) -> Optional["QRCode"]:
        return await cls.find_one(cls.id == qrcode_id)

    @classmethod
    async def get_by_file_name(cls, *, file_name: str) -> Optional["QRCode"]:
        return await cls.find_one(cls.qrcode_file == file_name)

    class Settings:
        name = "qr_codes"
        use_state_management = True
