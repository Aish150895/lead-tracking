import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "${DATABASE_URL}")

    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY",
                                "${SECRET_KEY}")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email settings
    DEBUG_EMAIL: str = os.getenv("DEBUG_EMAIL", "true")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "${SMTP_SERVER}")
    SMTP_PORT: int
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "${SMTP_USERNAME}")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "${SMTP_PASSWORD}")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "${EMAIL_FROM}")
    ATTORNEY_EMAIL: str = os.getenv("ATTORNEY_EMAIL", "${ATTORNEY_EMAIL}")

    # Default attorney account
    DEFAULT_ATTORNEY_EMAIL: str = os.getenv("DEFAULT_ATTORNEY_EMAIL",
                                            "${DEFAULT_ATTORNEY_EMAIL}")
    DEFAULT_ATTORNEY_PASSWORD: str = os.getenv("DEFAULT_ATTORNEY_PASSWORD",
                                               "${DEFAULT_ATTORNEY_PASSWORD}")
    DEFAULT_ATTORNEY_NAME: str = os.getenv("DEFAULT_ATTORNEY_NAME",
                                           "${DEFAULT_ATTORNEY_NAME}")

    # Application settings
    APP_NAME: str = "Lead Management System"
    APP_DESCRIPTION: str = "A FastAPI-based lead management system with email notifications"
    APP_VERSION: str = "1.0.0"

    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    model_config = {"env_file": ".env"}


settings = Settings()
