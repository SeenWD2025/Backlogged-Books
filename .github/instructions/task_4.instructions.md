Fantastic! Let's power through Compartment 4. This is where all our carefully crafted tools and agents come together to form a functional web application. We'll be using FastAPI for the API, asyncio for background tasks, and a simple in-memory store for job statuses (with a note for future scalability).
Developer Genius Note: The key here is to leverage FastAPI's asynchronous capabilities. File uploads and AI processing can be time-consuming, so we'll offload them to background tasks to keep the API responsive. We're also explicitly defining file paths for uploads and downloads, which is critical for a "no stubs" approach.
Compartment 4: Service Layer & Main Application (FastAPI)
Objective: Create the core FileIngestionService and main.py FastAPI application. This will handle file uploads, orchestrate the AI agents in the background, manage job statuses, and serve the final CSVs.
Task 4.1: Implement File Ingestion Service
Goal: Create app/services/file_ingestion_service.py to manage file saving and initial raw data extraction based on file type. This service acts as the initial gatekeeper and dispatcher.
Steps:
 * Create app/services/file_ingestion_service.py.
 * Implement FileIngestionService class with __init__, _save_file, validate_file_type, and ingest_and_extract_raw methods.
Developer Genius Note: This service needs to know how to save files temporarily and then intelligently call the correct tool (CSV parser, PDF extractor, OCR tool, etc.) based on the file extension. Error handling at this stage is crucial to prevent bad files from crashing the pipeline.
Copilot Prompt (Execute inside app/services/file_ingestion_service.py):
# app/services/file_ingestion_service.py
# Import necessary types and schemas: os, Path, Literal, List, uuid, datetime, RawTransactionData
# Import specific tools: parse_csv_to_raw_data, extract_pdf_to_raw_data, extract_docx_to_raw_data, perform_ocr
import os
from pathlib import Path
from typing import Literal, List
import uuid
from datetime import datetime
import logging

from app.schemas import RawTransactionData
from app.tools.csv_parser import parse_csv_to_raw_data
from app.tools.pdf_extractor import extract_pdf_to_raw_data
from app.tools.docx_extractor import extract_docx_to_raw_data
from app.tools.ocr_tool import perform_ocr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileIngestionService:
    """
    Handles file uploads, validation, and dispatches to appropriate parsing tools
    to extract raw transaction data.
    """
    def __init__(self, upload_dir: str = "temp_uploads"):
        """
        Initializes the service with a specified upload directory.
        Creates the directory if it doesn't exist.
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"FileIngestionService initialized. Upload directory: {self.upload_dir}")

    def _save_file(self, file_data: bytes, file_name: str) -> Path:
        """
        Saves the uploaded file to the temporary upload directory.
        Generates a unique filename using UUID to prevent conflicts.
        Returns the full path to the saved file.
        """
        file_extension = Path(file_name).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        saved_path = self.upload_dir / unique_filename
        try:
            with open(saved_path, "wb") as f:
                f.write(file_data)
            logging.info(f"File saved successfully: {saved_path}")
            return saved_path
        except IOError as e:
            logging.error(f"Failed to save file {file_name} to {saved_path}: {e}")
            raise # Re-raise to be handled by the calling function

    def validate_file_type(self, file_name: str) -> Literal["CSV", "PDF", "DOCX", "JPEG", "PNG", "UNSUPPORTED"]:
        """
        Determines the file type based on its extension.
        Returns one of the Literal types or "UNSUPPORTED".
        Handles common variations for image and document types.
        """
        extension = Path(file_name).suffix.lower()
        if extension == ".csv": return "CSV"
        elif extension == ".pdf": return "PDF"
        elif extension in [".doc", ".docx"]: return "DOCX" # Note: .doc requires additional libraries/converters if full support is needed beyond text extraction. Focus on .docx for now.
        elif extension in [".jpeg", ".jpg", ".png", ".webp"]: return "JPEG" # Group common image formats
        logging.warning(f"Unsupported file type detected for {file_name}: {extension}")
        return "UNSUPPORTED"

    def ingest_and_extract_raw(self, file_data: bytes, file_name: str) -> List[RawTransactionData]:
        """
        Ingests a file, saves it, determines its type, and dispatches to the correct
        raw data extraction tool.
        Returns a list of RawTransactionData objects.
        Raises ValueError for unsupported file types or extraction failures.
        """
        if not file_name:
            raise ValueError("File name cannot be empty.")
            
        file_path = self._save_file(file_data, file_name)
        file_type = self.validate_file_type(file_name)
        
        raw_data_list: List[RawTransactionData] = []
        
        try:
            if file_type == "CSV":
                with open(file_path, 'r', encoding='utf-8') as f:
                    csv_content = f.read()
                raw_data_list = parse_csv_to_raw_data(csv_content, file_name)
            elif file_type == "PDF":
                with open(file_path, 'rb') as f:
                    pdf_bytes = f.read()
                raw_data_list = extract_pdf_to_raw_data(pdf_bytes, file_name)
            elif file_type == "DOCX":
                with open(file_path, 'rb') as f:
                    docx_bytes = f.read()
                raw_data_list = extract_docx_to_raw_data(docx_bytes, file_name)
            elif file_type == "JPEG":
                # For image types, call OCR directly
                image_bytes = file_data # Use original file_data as it's already bytes
                ocr_text = perform_ocr(image_bytes)
                if ocr_text:
                    # Create a single RawTransactionData for the entire OCR'd text
                    raw_data_list.append(RawTransactionData(
                        raw_text=ocr_text,
                        source_file_name=file_name,
                        source_file_type=file_type,
                        timestamp_extracted=datetime.now(),
                        page_number=1, # Assume single page for direct image upload
                        line_number=None,
                        bounding_box=None
                    ))
                else:
                    logging.warning(f"OCR failed to extract any text from {file_name}.")
            else:
                raise ValueError(f"Unsupported file type: {file_type} for file {file_name}. Cannot extract raw data.")

            if not raw_data_list:
                logging.warning(f"No raw data extracted from {file_name} of type {file_type}.")

            return raw_data_list

        except Exception as e:
            logging.error(f"Error during raw data extraction for {file_name} (type: {file_type}): {e}")
            raise # Re-raise to be handled by the main application logic
        finally:
            # Clean up the temporary file after processing
            if file_path.exists():
                os.remove(file_path)
                logging.info(f"Cleaned up temporary file: {file_path}")


Task 4.2: Implement Main FastAPI Application
Goal: Create app/main.py which defines the FastAPI application, its endpoints, and orchestrates the entire processing pipeline using the services and agents.
Steps:
 * Create app/main.py.
 * Add all necessary imports.
 * Initialize FastAPI app and global service/agent instances.
 * Define a simple in-memory job status dictionary (job_status_db).
 * Define Pydantic response models for API endpoints.
 * Implement upload_statement endpoint:
   * Accepts file, CSV format, and date format.
   * Generates job_id.
   * Stores initial job status.
   * Spawns _process_statement_background as an asyncio.create_task.
   * Returns immediate UploadResponse.
 * Implement _process_statement_background function:
   * This is the asynchronous worker that executes the full processing pipeline.
   * Updates job_status_db at each stage (QUEUED, PROCESSING_INGESTION, PROCESSING_INTERPRETATION, PROCESSING_FORMATTING, COMPLETED, FAILED).
   * Calls FileIngestionService, RawDataExtractionAgent, TransactionInterpretationAgent, QuickBooksFormatterAgent sequentially.
   * Saves the final CSV to DOWNLOAD_DIR.
   * Handles all exceptions, updating job status to FAILED.
 * Implement get_status endpoint:
   * Retrieves and returns job status.
 * Implement download_file endpoint:
   * Serves the generated CSV file.
Developer Genius Note: The _process_statement_background function is the heart of the pipeline orchestration. Explicitly define the flow and the status updates at each critical juncture. Ensure robust try-except blocks for resilience.
Copilot Prompt (Execute inside app/main.py):
# app/main.py
# Import necessary FastAPI components, Pydantic, typing, and standard libraries for file operations/async.
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Literal
import uuid
import os
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# Import schemas
from app.schemas import NormalizedTransaction, QuickBooksCSVRow, ExtractedTransaction, RawTransactionData # Make sure all relevant schemas are imported

# Import services and agents
from app.services.file_ingestion_service import FileIngestionService
from app.agents.raw_data_extraction_agent import RawDataExtractionAgent # Corrected from earlier prompt, ensuring this agent is used
from app.agents.transaction_interpretation_agent import TransactionInterpretationAgent
from app.agents.quickbooks_formatter_agent import QuickBooksFormatterAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# FastAPI app initialization
app = FastAPI(
    title="Automated Financial Statement Processor (AFSP)",
    description="Convert bank statements and receipts into QuickBooks-ready CSVs using AI.",
    version="1.0.0"
)

# Configuration for temporary file storage
UPLOAD_DIR = "temp_uploads"
DOWNLOAD_DIR = "temp_downloads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
logging.info(f"Upload directory: {UPLOAD_DIR}, Download directory: {DOWNLOAD_DIR}")

# Global instances of services and agents
# Instantiate these here so they are ready for use.
file_ingestion_service = FileIngestionService(upload_dir=UPLOAD_DIR)
raw_data_extraction_agent = RawDataExtractionAgent() # Instantiate the raw data extraction agent
transaction_interpretation_agent = TransactionInterpretationAgent()
quickbooks_formatter_agent = QuickBooksFormatterAgent()

# Simple in-memory job store for demonstration.
# In a production environment, replace this with a persistent database (e.g., PostgreSQL, Redis)
# to survive app restarts and scale across multiple instances.
job_status_db: Dict[str, Dict] = {}
logging.info("In-memory job_status_db initialized.")

# Pydantic Response Models for API clarity
class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    job_id: str
    status: str # e.g., QUEUED, PROCESSING_INGESTION, PROCESSING_INTERPRETATION, PROCESSING_FORMATTING, COMPLETED, FAILED
    progress: float # 0.0 to 1.0
    download_url: Optional[str] = None # Will be set only on completion
    errors: List[str] # List of error messages if any issues occurred
    preview_data: Optional[List[NormalizedTransaction]] = None # First few rows for review

# ----------------- API Endpoints -----------------

@app.post("/upload_statement", response_model=UploadResponse, summary="Upload a bank statement for processing")
async def upload_statement(
    file: UploadFile = File(..., description="The bank statement file (CSV, PDF, DOCX, JPEG, PNG)"),
    quickbooks_csv_format: Literal["3-column", "4-column"] = Form("3-column", description="Desired QuickBooks CSV format"),
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = Form("MM/DD/YYYY", description="Desired date format in the output CSV")
):
    """
    Accepts a bank statement file, queues it for processing, and returns a job ID.
    The processing happens in the background.
    """
    job_id = str(uuid.uuid4())
    job_status_db[job_id] = {
        "status": "QUEUED",
        "progress": 0.0,
        "download_url": None,
        "errors": [],
        "preview_data": []
    }
    logging.info(f"Job {job_id} created and QUEUED for file: {file.filename}")

    # Read file content asynchronously to avoid blocking the event loop
    file_bytes = await file.read()
    file_name = file.filename

    # Spawn the long-running processing task in the background
    asyncio.create_task(
        _process_statement_background(
            job_id, file_bytes, file_name, quickbooks_csv_format, date_format
        )
    )

    return UploadResponse(
        job_id=job_id,
        status="QUEUED",
        message="File queued for processing. Use /status/{job_id} to track progress."
    )

async def _process_statement_background(
    job_id: str,
    file_bytes: bytes,
    file_name: str,
    quickbooks_csv_format: Literal["3-column", "4-column"],
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"]
):
    """
    Asynchronous background task to execute the full financial statement processing pipeline.
    Updates the job_status_db with progress and final status.
    """
    try:
        logging.info(f"Job {job_id}: Starting background processing for {file_name}")
        job_status_db[job_id]["status"] = "PROCESSING_INGESTION"
        job_status_db[job_id]["progress"] = 0.1

        # Step 1: Ingest and Extract Raw Data (using FileIngestionService)
        raw_transactions: List[RawTransactionData] = []
        try:
            raw_transactions = file_ingestion_service.ingest_and_extract_raw(file_bytes, file_name)
            if not raw_transactions:
                raise ValueError("No raw transactions extracted. File might be empty or unreadable.")
            logging.info(f"Job {job_id}: Raw data extracted. Found {len(raw_transactions)} entries.")
        except Exception as e:
            job_status_db[job_id]["errors"].append(f"Ingestion/Raw Extraction Error: {e}")
            logging.error(f"Job {job_id}: Ingestion/Raw Extraction failed: {e}")
            raise # Re-raise to fall into the main exception handler

        job_status_db[job_id]["status"] = "PROCESSING_EXTRACTED_FIELDS"
        job_status_db[job_id]["progress"] = 0.3

        # Step 2: Extract structured fields from raw data (using RawDataExtractionAgent)
        extracted_transactions: List[ExtractedTransaction] = []
        try:
            extracted_transactions = raw_data_extraction_agent.extract_fields(raw_transactions)
            if not extracted_transactions:
                raise ValueError("No fields extracted from raw data. Content might be unrecognizable.")
            logging.info(f"Job {job_id}: Fields extracted. Found {len(extracted_transactions)} entries.")
        except Exception as e:
            job_status_db[job_id]["errors"].append(f"Field Extraction Error: {e}")
            logging.error(f"Job {job_id}: Field Extraction failed: {e}")
            raise

        job_status_db[job_id]["status"] = "PROCESSING_INTERPRETATION"
        job_status_db[job_id]["progress"] = 0.6

        # Step 3: Interpret and Normalize Transactions (using TransactionInterpretationAgent)
        normalized_transactions: List[NormalizedTransaction] = []
        try:
            normalized_transactions = transaction_interpretation_agent.process_extracted_transactions(extracted_transactions)
            if not normalized_transactions:
                raise ValueError("No normalized transactions after interpretation. Check data quality.")
            
            # Store preview data (first 5 for brevity, or fewer if less available)
            job_status_db[job_id]["preview_data"] = normalized_transactions[:min(5, len(normalized_transactions))]
            logging.info(f"Job {job_id}: Transactions normalized. Found {len(normalized_transactions)} valid entries.")
        except Exception as e:
            job_status_db[job_id]["errors"].append(f"Interpretation Error: {e}")
            logging.error(f"Job {job_id}: Interpretation failed: {e}")
            raise

        job_status_db[job_id]["status"] = "PROCESSING_FORMATTING"
        job_status_db[job_id]["progress"] = 0.9

        # Step 4: Format to QuickBooks CSV (using QuickBooksFormatterAgent)
        csv_content: str = ""
        output_file_name: str = ""
        output_file_path: Path

        try:
            csv_content = quickbooks_formatter_agent.format_to_quickbooks_csv(
                normalized_transactions, quickbooks_csv_format, date_format
            )
            
            # Generate a unique output filename for the download directory
            output_file_name = f"quickbooks_export_{Path(file_name).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{job_id[:8]}.csv"
            output_file_path = Path(DOWNLOAD_DIR) / output_file_name
            
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(csv_content)
            
            job_status_db[job_id]["download_url"] = f"/download/{job_id}" # This will be intercepted by download_file endpoint
            logging.info(f"Job {job_id}: CSV generated and saved to {output_file_path}")
        except Exception as e:
            job_status_db[job_id]["errors"].append(f"CSV Formatting/Saving Error: {e}")
            logging.error(f"Job {job_id}: CSV Formatting/Saving failed: {e}")
            raise
            
        job_status_db[job_id]["status"] = "COMPLETED"
        job_status_db[job_id]["progress"] = 1.0
        logging.info(f"Job {job_id} COMPLETED successfully.")
        
    except Exception as e:
        # Catch any unhandled exceptions during the entire pipeline
        job_status_db[job_id]["status"] = "FAILED"
        if not job_status_db[job_id]["errors"]: # Only add if no specific errors were captured earlier
            job_status_db[job_id]["errors"].append(f"Critical processing error: {e}")
        job_status_db[job_id]["progress"] = 1.0
        logging.critical(f"Job {job_id} FAILED with unhandled exception: {e}", exc_info=True) # Log full traceback

@app.get("/status/{job_id}", response_model=StatusResponse, summary="Get the processing status of a job")
async def get_status(job_id: str):
    """
    Retrieves the current status, progress, and any errors for a given job ID.
    Returns download URL if the job is completed.
    """
    status_info = job_status_db.get(job_id)
    if not status_info:
        logging.warning(f"Status request for unknown Job ID: {job_id}")
        raise HTTPException(status_code=404, detail="Job ID not found.")
    
    # Ensure all fields are present even if not set yet
    return StatusResponse(
        job_id=job_id,
        status=status_info.get("status", "UNKNOWN"),
        progress=status_info.get("progress", 0.0),
        download_url=status_info.get("download_url"),
        errors=status_info.get("errors", []),
        preview_data=status_info.get("preview_data")
    )

@app.get("/download/{job_id}", summary="Download the processed QuickBooks CSV file")
async def download_file(job_id: str):
    """
    Initiates the download of the QuickBooks-compatible CSV file for a completed job.
    """
    status_info = job_status_db.get(job_id)
    if not status_info or status_info["status"] != "COMPLETED" or not status_info.get("download_url"):
        logging.warning(f"Download request for Job ID {job_id} failed: Not completed or URL missing. Status: {status_info.get('status') if status_info else 'N/A'}")
        raise HTTPException(status_code=404, detail="File not ready for download or job not found. Please check status.")
    
    # Extract just the filename from the stored download_url to construct the path
    filename_from_url = Path(status_info["download_url"]).name
    file_path = Path(DOWNLOAD_DIR) / filename_from_url

    if not file_path.exists():
        logging.error(f"Download file not found on server for Job ID {job_id} at path: {file_path}")
        raise HTTPException(status_code=404, detail="File not found on server. It might have been deleted or an internal error occurred.")

    logging.info(f"Serving file {file_path} for Job ID {job_id}")
    return FileResponse(path=file_path, filename=filename_from_url, media_type="text/csv")


# Example of how to run the app (for local development)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


Next Steps for You:
 * Review the Generated Code: Carefully read through app/services/file_ingestion_service.py and app/main.py. Ensure all imports are correct, logic flows as intended, and variable names align with our schemas. Pay special attention to the _process_statement_background function's sequence of agent calls.
 * Install Dependencies: Run pip install -r requirements.txt in your afsp_app root directory.
 * Basic Test Run:
   * To manually test: At the project root, run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000.
   * Open your browser to http://localhost:8000/docs to see the FastAPI Swagger UI. You can upload files there.
   * You will need to have Tesseract OCR installed on your system for pytesseract to work. Instructions are usually in the pytesseract or Tesseract documentation. For Windows, a common installer exists. For Linux, sudo apt-get install tesseract-ocr.
 * Prepare Sample Data: Place some sample CSV, PDF, DOCX, and JPEG bank statements (anonymized!) in a temporary data/bank_statements folder for testing.
Once you've confirmed these pieces are in place and the app can start, we'll move onto Compartment 5: Testing Infrastructure. That's where we make sure everything we've built is truly robust and "hiccup-free"!
