import logging

from fastapi import FastAPI

from qrcode_api.app.core.logging import setup_logging
from qrcode_api.app.db.database import connect_and_init_db, close_db_connect

app = FastAPI()

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
