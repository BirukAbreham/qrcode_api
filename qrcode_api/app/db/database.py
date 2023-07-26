import sys
import logging
import asyncio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from qrcode_api.app.core.config import settings
from qrcode_api.app.core.security import get_password_hash
from qrcode_api.app.models import User, gather_documents


logger = logging.getLogger(__name__)

db_client: AsyncIOMotorClient = None


def get_db() -> AsyncIOMotorClient:
    return db_client[settings.MONGO_DB]


async def connect_and_init_db() -> None:
    global db_client

    db_client = AsyncIOMotorClient(
        str(settings.MONGO_URI),
        maxPoolSize=settings.MAX_DB_CONN_COUNT,
        minPoolSize=settings.MIN_DB_CONN_COUNT,
        uuidRepresentation="standard",
    )

    try:
        db_client.admin.command("ping")

        await init_beanie(
            database=getattr(db_client, settings.MONGO_DB),
            document_models=gather_documents(),
        )

        logger.info("Connected to MongoDB")
        logger.info(f"Connection string: {settings.MONGO_URI}/{settings.MONGO_DB}")

        if not await User.get_by_username(username=settings.SUPERUSER):
            await User(
                username=settings.SUPERUSER,
                email=settings.SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.SUPERUSER_PASSWORD),
                is_superuser=True,
            ).insert()
    except Exception as exception:
        logger.error(f"Could not connect to MongoDB", exc_info=True)
        asyncio.get_event_loop().close()
        sys.exit()


async def close_db_connect() -> None:
    global db_client

    if db_client is None:
        logger.warning("Connection is None, nothing to close")
        return

    db_client.close()
    db_client = None
    logger.info("MongoDB connection closed")
