from datetime import datetime
from enum import Enum
from typing import Any

from beanie import PydanticObjectId
from pydantic import AnyUrl, BaseModel, EmailStr, HttpUrl
from pydantic.color import Color


class FileFormats(str, Enum):
    svg = "svg"
    png = "png"
    pdf = "pdf"


class ErrorLevel(str, Enum):
    L = "L"
    M = "M"
    Q = "Q"
    H = "H"


class Mode(str, Enum):
    numeric = "numeric"
    alphanumeric = "alphanumeric"
    byte = "byte"
    kanji = "kanji"
    hanzi = "hanzi"


class IQRCodeCreate(BaseModel):
    scale: int = 1
    border: int = 1
    mode: Mode = None
    micro: bool = False
    dark: Color = Color("black")
    light: Color = Color("white")
    error_level: ErrorLevel = None
    file_format: FileFormats = FileFormats.png

    class Config:
        json_encoders = {Color: lambda color: color.as_hex()}


class QRCodeBasicCreate(IQRCodeCreate):
    data: Any


class QRCodeWiFiCreate(IQRCodeCreate):
    ssid: str
    password: str
    security: str


class QRCodeLocationCreate(IQRCodeCreate):
    latitude: float
    longitude: float


class QRCodeVCardCreate(IQRCodeCreate):
    name: str
    displayname: str
    email: list[EmailStr]
    url: list[HttpUrl]


class QRCode(BaseModel):
    qrcode_url: AnyUrl
    created_at: datetime
    user_id: PydanticObjectId

    class Config:
        orm_mod = True
