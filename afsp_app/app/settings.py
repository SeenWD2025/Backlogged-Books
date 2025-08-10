"""
Settings management for the AFSP application using pydantic-settings.
This centralizes all configuration and makes it easier to load from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Dict, List

class Settings(BaseSettings):
    """
    Application settings that can be loaded from environment variables or .env file.
    """
    # Base directories
    BASE_DIR: Path = Path(__file__).parent.parent.absolute()
    APP_DIR: Path = Path(__file__).parent.absolute()
    
    # File storage paths
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    DOWNLOAD_DIR: str = str(BASE_DIR / "downloads")
    DATABASE_PATH: str = str(BASE_DIR / "afsp.db")
    
    # OCR settings
    TESSERACT_PATH: str = "tesseract"
    
    # Processing settings
    MAX_FILE_SIZE_MB: int = 10
    
    # MIME type mapping
    ALLOWED_EXTENSIONS: Dict[str, str] = {
        "pdf": "application/pdf",
        "csv": "text/csv",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
    }
    
    # Security settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # API settings
    API_TITLE: str = "Automated Financial Statement Processor"
    API_DESCRIPTION: str = "Convert bank statements and receipts to QuickBooks-compatible CSV formats"
    API_VERSION: str = "1.0.0"
    
    # Secret key for JWT token generation
    SECRET_KEY: str = "7b438f49eb134d49419c9e0c423f465cc651237ad8f3c12c43aa26f7821dcc14"
    
    # Environment settings
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Email verification settings
    REQUIRE_EMAIL_VERIFICATION: bool = True  # Always true for production security
    AUTO_VERIFY_IN_DEVELOPMENT: bool = True  # Bypass for development only
    
    # Email server configuration (for production)
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    
    # Email content settings
    EMAIL_FROM: str = "noreply@afsp.local"
    EMAIL_FROM_NAME: str = "AFSP - Financial Processor"
    EMAIL_VERIFICATION_SUBJECT: str = "Verify your AFSP account"
    
    # Frontend URL for verification links
    FRONTEND_URL: str = "http://localhost:3000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="AFSP_"
    )

# Create a global settings instance
settings = Settings()

# Create required directories
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
