import logging
from datetime import datetime

from qrcode_api.app.core.config import settings

LOG_DIR = settings.LOG_DIR
LOG_CONFIG_FILE = settings.LOG_CONFIG_FILE


def setup_logging() -> None:
    """Load logging configuration"""
    log_date = datetime.now().strftime("%Y-%m-%d")

    logging.config.fileConfig(
        LOG_CONFIG_FILE,
        disable_existing_loggers=False,
        defaults={"logfilename": f"{LOG_DIR}/{log_date}.log"},
    )
