import logging
from typing import Set

from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse

from app import api
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import connect_and_init_db, close_db_connect


tags_metadata = [
    {
        "name": "Authentication",
        "description": "Get authentication token",
    },
    {
        "name": "Users",
        "description": "User registration and management",
    },
]

# Common response codes
responses: Set[int] = {
    status.HTTP_400_BAD_REQUEST,
    status.HTTP_401_UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN,
    status.HTTP_404_NOT_FOUND,
    status.HTTP_500_INTERNAL_SERVER_ERROR,
}


app = FastAPI(
    debug=settings.DEBUG,
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="QR Code API generator",
    default_response_class=ORJSONResponse,
    openapi_tags=tags_metadata,
    license_info={
        "name": "GNU General Public License v3.0",
        "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
    },
)

# Add the router responsible for all /api/ endpoint requests
app.include_router(api.router)

# Setup logging configuration
setup_logging()

logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up")
    await connect_and_init_db()


@app.on_event("shutdown")
async def shutdown_events():
    logger.info("Clean up before shutting down the server")
    await close_db_connect()
    logger.info("Application shutting down")
