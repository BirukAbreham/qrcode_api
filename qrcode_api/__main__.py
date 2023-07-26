import uvicorn

import yaml
from qrcode_api.app.core.config import settings

LOG_CONFIG_FILE = settings.LOG_CONFIG_FILE

def run_dev_server() -> None:
    """Run the uvicorn server in development environment"""
    with open(LOG_CONFIG_FILE, 'r') as stream:
        config = yaml.load(stream=stream, Loader=yaml.FullLoader)
    
    uvicorn.run(
        "qrcode_api.app.main:app",
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        reload=settings.DEBUG,
        log_config=config,
    )


if __name__ == "__main__":
    run_dev_server()
