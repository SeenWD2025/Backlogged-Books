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

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Query, Depends, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_users import FastAPIUsers, BaseUserManager
from fastapi_users.db import SQLAlchemyUserDatabase

from afsp_app.app.config import (
    API_TITLE, API_DESCRIPTION, API_VERSION, ALLOWED_ORIGINS,
    UPLOAD_DIR, DOWNLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS
)
from afsp_app.app.database import User, create_db_and_tables, get_async_session, get_user_db, Job, Transaction, async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from afsp_app.app.schemas import StatusResponse, UploadResponse, UserRead, UserCreate, UserUpdate
from afsp_app.app.logging_config import get_logger
from afsp_app.app.auth import get_user_manager, SECRET, auth_backend
from afsp_app.app.settings import settings

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
# db_manager = DatabaseManager()

# def get_db_manager():
#     """Dependency to get the shared database manager instance."""
#     return db_manager

fastapi_users = FastAPIUsers[User, str](
    get_user_manager,
    [auth_backend],
)

@app.on_event("startup")
async def on_startup():
    """Create necessary directories and database tables on application startup."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory ensured at {UPLOAD_DIR}")
    logger.info(f"Download directory ensured at {DOWNLOAD_DIR}")
    # Create database tables
    await create_db_and_tables()


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
        "environment": settings.ENVIRONMENT,
        "email_verification_required": settings.REQUIRE_EMAIL_VERIFICATION,
        "auto_verify_development": settings.AUTO_VERIFY_IN_DEVELOPMENT if settings.ENVIRONMENT == "development" else None,
    }

@app.post("/dev/auto-verify/{user_id}")
async def dev_auto_verify_user(user_id: str, db: AsyncSession = Depends(get_async_session)):
    """
    Development-only endpoint to auto-verify users.
    Only available in development environment.
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=404, detail="Endpoint not available in production")
    
    # Update user verification status
    result = await db.execute(
        update(User).where(User.id == user_id).values(is_verified=True)
    )
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": f"User {user_id} has been auto-verified (development mode)",
        "user_id": user_id,
        "verified": True
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    csv_format: Literal["3-column", "4-column"] = Form("3-column"),
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = Form("MM/DD/YYYY"),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(fastapi_users.current_user()),
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

    content_chunk = await file.read(2048)
    await file.seek(0)
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

        new_job = Job(
            job_id=job_id,
            user_id=user.id,
            status="PENDING",
            source_file=file_path,
            source_file_type=file_type,
            date_format=date_format,
            csv_format=csv_format,
        )
        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)

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
async def get_status(job_id: str, db: AsyncSession = Depends(get_async_session)):
    """Check the status of a processing job."""
    result = await db.execute(select(Job).where(Job.job_id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    preview_data = []
    if job.status == "COMPLETED":
        tran_result = await db.execute(select(Transaction).where(Transaction.job_id == job_id).limit(5))
        transactions = tran_result.scalars().all()
        preview_data = transactions

    return StatusResponse(
        job_id=job.job_id,
        status=job.status,
        source_file=job.source_file,
        created_at=job.created_at,
        updated_at=job.updated_at,
        output_file=job.output_file,
        error_message=job.error_message,
        preview_data=preview_data,
    )

@app.get("/download/{job_id}")
async def download_file(job_id: str, db: AsyncSession = Depends(get_async_session)):
    """Download the processed CSV file for a completed job."""
    result = await db.execute(select(Job).where(Job.job_id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if job.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Job processing is not complete.")
    if not job.output_file or not os.path.exists(job.output_file):
        raise HTTPException(status_code=404, detail="Output file not found.")

    return FileResponse(
        job.output_file,
        filename=f"quickbooks_import_{job_id}.csv",
        media_type="text/csv"
    )

@app.get("/jobs", response_model=List[StatusResponse])
async def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_session),
):
    """List all processing jobs with pagination."""
    result = await db.execute(select(Job).offset(offset).limit(limit))
    jobs = result.scalars().all()
    return [
        StatusResponse(
            job_id=job.job_id,
            status=job.status,
            source_file=job.source_file,
            created_at=job.created_at,
            updated_at=job.updated_at,
            output_file=job.output_file,
            error_message=job.error_message,
        ) for job in jobs
    ]

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Custom registration endpoint that handles development auto-verification
@app.post("/auth/register", response_model=UserRead)
async def register_user(
    user_data: UserCreate,
    request: Request,
    user_manager: BaseUserManager = Depends(get_user_manager),
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
):
    """Custom registration endpoint with development auto-verification."""
    try:
        # Create the user
        created_user = await user_manager.create(user_data, safe=True, request=request)
        
        # Development auto-verification
        if (settings.ENVIRONMENT == "development" and 
            settings.AUTO_VERIFY_IN_DEVELOPMENT and 
            not created_user.is_verified):
            
            print(f"Development mode: Auto-verifying user {created_user.id}")
            
            # Update user verification status
            async with async_session_maker() as db:
                await db.execute(
                    update(User).where(User.id == created_user.id).values(is_verified=True)
                )
                await db.commit()
            
            # Update the user object to reflect the change
            created_user.is_verified = True
        
        return created_user
        
    except Exception as e:
        if "REGISTER_USER_ALREADY_EXISTS" in str(e):
            raise HTTPException(status_code=400, detail="REGISTER_USER_ALREADY_EXISTS")
        raise HTTPException(status_code=400, detail=str(e))

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

async def process_file(
    job_id: str,
    file_path: str,
    file_type: str,
    date_format: str,
    csv_format: str,
) -> None:
    """Background task to process the uploaded file."""
    job_logger = get_logger(__name__, job_id=job_id)
    
    async with async_session_maker() as db:
        try:
            job_logger.info(f"Starting processing for job {job_id}")
            
            # Update job status to PROCESSING
            await db.execute(
                select(Job).where(Job.job_id == job_id).with_for_update()
            )
            job = await db.get(Job, job_id)
            if not job:
                job_logger.error(f"Job {job_id} not found in database for processing.")
                return
            job.status = "PROCESSING"
            await db.commit()

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

            # Add transactions to the database
            for t in normalized_transactions:
                db.add(Transaction(job_id=job_id, **t.model_dump()))
            job_logger.info(f"Added {len(normalized_transactions)} transactions to the database session.")

            # Update job status to COMPLETED
            job.status = "COMPLETED"
            job.output_file = output_file
            await db.commit()
            job_logger.info(f"Processing completed for job {job_id}")

        except Exception as e:
            job_logger.error(f"Processing failed for job {job_id}: {str(e)}", exc_info=True)
            await db.rollback()
            # Ensure job exists before trying to update it
            job = await db.get(Job, job_id)
            if job:
                job.status = "FAILED"
                job.error_message = str(e)
                await db.commit()
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                job_logger.info(f"Cleaned up source file: {file_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("afsp_app.app.main:app", host="0.0.0.0", port=8000, reload=True)
