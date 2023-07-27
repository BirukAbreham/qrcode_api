import logging

import yaml
from qrcode_api.app.core.config import settings

LOG_CONFIG_FILE = settings.LOG_CONFIG_FILE


def setup_logging() -> None:
    """Load logging configuration"""
    with open(LOG_CONFIG_FILE, "r") as stream:
        config = yaml.load(stream=stream, Loader=yaml.FullLoader)

    logging.config.dictConfig(config)
