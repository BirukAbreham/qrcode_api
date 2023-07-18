from pydantic import BaseSettings, MongoDsn

from qrcode_api import __version__

# This adds support for 'mongodb+srv' connection schemas when using e.g. MongoDB Atlas
MongoDsn.allowed_schemes.add("mongodb+srv")


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "QR Code API"
    PROJECT_VERSION: str = __version__
    API_V1_STR: str = "v1"
    DEBUG: bool = True

    # Development Settings
    UVICORN_HOST: str
    UVICORN_PORT: int

    # Database Configuration
    MONGO_DB: str
    MONGO_URI: MongoDsn
    MAX_DB_CONN_COUNT: int
    MIN_DB_CONN_COUNT: int

    # Security Configuration
    SECRET_KEY: str
    EXPIRE_MINUTES: int
    ALGORITHM: str

    # Logger Configuration
    LOG_DIR: str
    LOG_CONFIG_FILE: str

    class Config:
        # Place your .env file under this path
        env_file = ".env"
        env_prefix = "QR_CODE_API_"
        case_sensitive = True


settings = Settings()
