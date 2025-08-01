"""Main application file for the Automated Financial Statement Processor (AFSP).
Contains FastAPI application setup and API endpoints.
"""

import os
import uuid
from typing import List, Literal
from datetime import datetime
from pathlib import Path
import shutil
import magic
from werkzeug.utils import secure_filename

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from afsp_app.app.config import (
    API_TITLE, API_DESCRIPTION, API_VERSION, ALLOWED_ORIGINS,
    UPLOAD_DIR, DOWNLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS
)
from afsp_app.app.database import DatabaseManager
from afsp_app.app.schemas import StatusResponse, UploadResponse
from afsp_app.app.logging_config import get_logger

# Initialize structured logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Create a single instance of the DatabaseManager
db_manager = DatabaseManager()

def get_db_manager():
    """Dependency to get the shared database manager instance."""
    return db_manager

@app.on_event("startup")
def startup_event():
    """Create necessary directories on application startup."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory ensured at {UPLOAD_DIR}")
    logger.info(f"Download directory ensured at {DOWNLOAD_DIR}")
    # Initialize the database
    db_manager._initialize_db()


@app.get("/health")
def health_check():
    """Health check endpoint to verify if the service is running."""
    return {"status": "up", "timestamp": datetime.now().isoformat()}

@app.get("/")
def root():
    """Root endpoint that returns basic application information."""
    return {
        "app": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "docs_url": "/docs",
    }

@app.post("/upload", response_model=UploadResponse)
def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    csv_format: Literal["3-column", "4-column"] = Form("3-column"),
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = Form("MM/DD/YYYY"),
    db: DatabaseManager = Depends(get_db_manager),
):
    """
    Upload a financial document (bank statement or receipt) for processing.
    """
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension. Supported types: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )

    content_chunk = file.file.read(2048)
    file.file.seek(0)
    detected_type = magic.Magic(mime=True).from_buffer(content_chunk)

    allowed_mime_types = set(ALLOWED_EXTENSIONS.values())
    if detected_type not in allowed_mime_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file content detected: {detected_type}. Expected one of {', '.join(allowed_mime_types)}"
        )

    job_id = str(uuid.uuid4())
    safe_filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{safe_filename}")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            os.remove(file_path)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
            )

        file_type = file_ext.upper()
        if file_type in ("JPG", "JPEG"):
            file_type = "JPEG"

        db.create_job(job_id, file_path, file_type, date_format, csv_format)
        background_tasks.add_task(process_file, job_id, file_path, file_type, date_format, csv_format)

        return UploadResponse(
            job_id=job_id,
            message="File uploaded successfully. Processing started.",
            status="PENDING"
        )
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Upload failed for file {safe_filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during file upload: {str(e)}"
        )

@app.get("/status/{job_id}", response_model=StatusResponse)
def get_status(job_id: str, db: DatabaseManager = Depends(get_db_manager)):
    """Check the status of a processing job."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    response_data = {
        "job_id": job["job_id"],
        "status": job["status"],
        "source_file": job["source_file"],
        "created_at": datetime.fromisoformat(job["created_at"]),
        "updated_at": datetime.fromisoformat(job["updated_at"]),
        "output_file": job["output_file"],
        "error_message": job["error_message"],
    }

    if job["status"] == "COMPLETED":
        transactions = db.get_job_transactions(job_id)
        response_data["preview_data"] = transactions[:5]

    return StatusResponse(**response_data)

@app.get("/download/{job_id}")
def download_file(job_id: str, db: DatabaseManager = Depends(get_db_manager)):
    """Download the processed CSV file for a completed job."""
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if job["status"] != "COMPLETED":
        raise HTTPException(status_code=400, detail="Job processing is not complete.")
    if not job["output_file"] or not os.path.exists(job["output_file"]):
        raise HTTPException(status_code=404, detail="Output file not found.")

    return FileResponse(
        job["output_file"],
        filename=f"quickbooks_import_{job_id}.csv",
        media_type="text/csv"
    )

@app.get("/jobs", response_model=List[StatusResponse])
def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: DatabaseManager = Depends(get_db_manager),
):
    """List all processing jobs with pagination."""
    jobs = db.get_all_jobs(limit, offset)
    return [StatusResponse(**job) for job in jobs]

def process_file(
    job_id: str,
    file_path: str,
    file_type: str,
    date_format: str,
    csv_format: str,
) -> None:
    """Background task to process the uploaded file."""
    job_logger = get_logger(__name__, job_id=job_id)
    db = get_db_manager()
    db.update_job_status(job_id, "PROCESSING")
    job_logger.info(f"Starting processing for job {job_id}")

    try:
        from afsp_app.app.agents.raw_data_extraction_agent import RawDataExtractionAgent
        from afsp_app.app.agents.transaction_interpretation_agent import TransactionInterpretationAgent
        from afsp_app.app.agents.quickbooks_formatter_agent import QuickBooksFormatterAgent

        output_file = os.path.join(DOWNLOAD_DIR, f"{job_id}_output.csv")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        extraction_agent = RawDataExtractionAgent()
        raw_transactions = extraction_agent.extract_from_file(file_path, file_type)
        if not raw_transactions:
            raise ValueError("No transaction data could be extracted.")
        job_logger.info(f"Extracted {len(raw_transactions)} raw transactions.")

        interpretation_agent = TransactionInterpretationAgent()
        normalized_transactions = interpretation_agent.process_raw_transactions(raw_transactions)
        if not normalized_transactions:
            raise ValueError("Failed to interpret any transactions.")
        job_logger.info(f"Interpreted {len(normalized_transactions)} normalized transactions.")

        formatter_agent = QuickBooksFormatterAgent()
        formatter_agent.write_csv_to_file(normalized_transactions, output_file, csv_format, date_format)
        job_logger.info(f"Generated QuickBooks CSV file: {output_file}")

        transaction_dicts = [t.model_dump() for t in normalized_transactions]
        db.add_transactions(job_id, transaction_dicts)
        job_logger.info(f"Added {len(transaction_dicts)} transactions to the database.")

        db.update_job_status(job_id, "COMPLETED", output_file=output_file)
        job_logger.info(f"Processing completed for job {job_id}")

    except Exception as e:
        job_logger.error(f"Processing failed for job {job_id}: {str(e)}", exc_info=True)
        db.update_job_status(job_id, "FAILED", error_message=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            job_logger.info(f"Cleaned up source file: {file_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("afsp_app.app.main:app", host="0.0.0.0", port=8000, reload=True)
