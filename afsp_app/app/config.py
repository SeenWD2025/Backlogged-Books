"""
Application-wide configurations for the Automated Financial Statement Processor (AFSP).
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent.absolute()
APP_DIR = Path(__file__).parent.absolute()

# File storage paths
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", os.path.join(BASE_DIR, "downloads"))
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "afsp.db"))

# Ensure directories exist
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

# OCR settings
TESSERACT_PATH = os.environ.get("TESSERACT_PATH", "tesseract")  # Path to tesseract executable

# Processing settings
MAX_FILE_SIZE_MB = 10  # Maximum file size in MB
ALLOWED_EXTENSIONS = {
    "pdf": "application/pdf",
    "csv": "text/csv",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
}

# API settings
API_TITLE = "Automated Financial Statement Processor"
API_DESCRIPTION = "Convert bank statements and receipts to QuickBooks-compatible CSV formats"
API_VERSION = "1.0.0"
