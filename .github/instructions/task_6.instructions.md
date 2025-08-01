Refined Task 6.1: Finalize Local Configuration and Database Integration
Goal: Ensure app/config.py correctly defines all local paths, app/database.py handles SQLite operations, and most importantly, app/main.py fully leverages app/database.py for all job status management, removing the old in-memory dictionary.
Specific Focus for app/main.py: Replacing job_status_db with db_manager.
Here's the detailed walkthrough of changes required in app/main.py:
1. Remove the Old job_status_db Dictionary:
* Locate and delete this line:
python # REMOVE THIS LINE: # job_status_db: Dict[str, Dict] = {} # In-memory storage for job statuses 
2. Import DatabaseManager and Instantiate it Globally:
* Add this import at the top (if not already there):
python from app.database import DatabaseManager 
* Replace the removed job_status_db line with the instantiation of db_manager:
python # Global instance of DatabaseManager db_manager = DatabaseManager() logging.info("SQLite DatabaseManager initialized.") 
3. Modify the /upload_statement Endpoint:
* This endpoint now needs to create the initial job entry in the database.
* Old code snippet (how it used job_status_db):
python # Old way: # job_status_db[job_id] = { #     "status": "QUEUED", #     "progress": 0.0, #     "download_url": None, #     "errors": [], #     "preview_data": [] # } 
* New code snippet (using db_manager):
```python
# In @app.post("/upload_statement")
job_id = str(uuid.uuid4())
    # Create initial job status in DB
    db_manager.update_job_status(
        job_id,
        status="QUEUED",
        progress=0.0,
        download_url=None,
        errors=[],
        preview_data=[] # Even if empty, explicitly pass for schema consistency
    )
    logging.info(f"Job {job_id} created and QUEUED for file: {file.filename}")
    ```

4. Modify the _process_statement_background Function:
* This is where most of the job_status_db accesses will be replaced. Each stage of processing will now update the database.
* Initial status update:
* Old: (often just assumed set by upload_statement)
* New:
python async def _process_statement_background(...): current_errors: List[str] = [] # Ensure the job status is marked as PROCESSING_INGESTION and progress is updated db_manager.update_job_status(job_id, "PROCESSING_INGESTION", 0.1, errors=current_errors) logging.info(f"Job {job_id}: Starting background processing for {file_name}") 
* After Raw Ingestion:
* Old: job_status_db[job_id]["progress"] = 0.3
* New:
python # After raw_transactions are obtained db_manager.update_job_status(job_id, "PROCESSING_EXTRACTED_FIELDS", 0.3, errors=current_errors) 
* After Field Extraction:
* Old: job_status_db[job_id]["progress"] = 0.6
* New:
python # After extracted_transactions are obtained db_manager.update_job_status(job_id, "PROCESSING_INTERPRETATION", 0.6, errors=current_errors) 
* After Transaction Interpretation (including preview_data):
* Old:
python # job_status_db[job_id]["preview_data"] = normalized_transactions[:min(5, len(normalized_transactions))] # job_status_db[job_id]["progress"] = 0.9 
* New:
python # After normalized_transactions are obtained db_manager.update_job_status( job_id, "PROCESSING_FORMATTING", # Or "PROCESSING_INTERPRETATION" if this is the final step for that stage 0.9, errors=current_errors, preview_data=normalized_transactions[:min(5, len(normalized_transactions))] ) 
* After CSV Formatting and Saving (final COMPLETED state):
* Old:
python # job_status_db[job_id]["status"] = "COMPLETED" # job_status_db[job_id]["progress"] = 1.0 # job_status_db[job_id]["download_url"] = f"/download/{job_id}" 
* New (Crucial change for download_url):
python # After csv_content is written to output_file_path # Store ONLY the filename in the DB; the download endpoint will reconstruct the full URL db_manager.update_job_status( job_id, "COMPLETED", 1.0, download_url=output_file_name, # <-- Store just the filename, NOT the full URL path errors=current_errors, preview_data=normalized_transactions[:min(5, len(normalized_transactions))] ) logging.info(f"Job {job_id}: CSV generated and saved to {output_file_path}") 
* Error Handling (in except Exception as e: block):
* Old:
python # job_status_db[job_id]["status"] = "FAILED" # job_status_db[job_id]["progress"] = 1.0 # job_status_db[job_id]["errors"].append(str(e)) 
* New:
python # In the final except block of _process_statement_background current_errors.append(f"Critical processing error: {e}") # Ensure the specific error is added db_manager.update_job_status(job_id, "FAILED", 1.0, errors=current_errors) logging.critical(f"Job {job_id} FAILED with unhandled exception: {e}", exc_info=True) 
5. Modify the /status/{job_id} Endpoint:
* This endpoint will now fetch job data directly from the database.
* Old code snippet:
python # Old way: # status_info = job_status_db.get(job_id) # if not status_info: #    raise HTTPException(status_code=404, detail="Job ID not found.") 
* New code snippet:
```python
# In @app.get("/status/{job_id}")
status_info = db_manager.get_job_status(job_id)
if not status_info:
logging.warning(f"Status request for unknown Job ID: {job_id}")
raise HTTPException(status_code=404, detail="Job ID not found.")
    # Ensure download_url is reconstructed for the client from the stored filename
    download_url_for_client = f"/download/{status_info['job_id']}" if status_info.get('download_url') else None
    
    return StatusResponse(
        job_id=job_id,
        status=status_info.get("status", "UNKNOWN"),
        progress=status_info.get("progress", 0.0),
        download_url=download_url_for_client, # Use the reconstructed URL
        errors=status_info.get("errors", []),
        preview_data=status_info.get("preview_data", [])
    )
    ```

6. Modify the /download/{job_id} Endpoint:
* This endpoint also needs to fetch job data from the database and construct the full file path.
* Old code snippet:
python # Old way: # status_info = job_status_db.get(job_id) # if not status_info or status_info["status"] != "COMPLETED" or not status_info.get("download_url"): #     # ... existing error handling ... # file_path = Path(DOWNLOAD_DIR) / status_info["download_url"].split('/')[-1] # Assuming URL was /download/filename 
* New code snippet:
```python
# In @app.get("/download/{job_id}")
status_info = db_manager.get_job_status(job_id)
    # Check if job exists, is completed, and has a filename stored for download
    if not status_info or status_info["status"] != "COMPLETED" or not status_info.get("download_url"):
        logging.warning(f"Download request for Job ID {job_id} failed: Not completed or URL missing. Status: {status_info.get('status') if status_info else 'N/A'}")
        raise HTTPException(status_code=404, detail="File not ready for download or job not found. Please check status.")
    
    filename_from_db = status_info["download_url"] # This is now JUST the filename, not a URL
    file_path = DOWNLOAD_DIR / filename_from_db # Construct full path using DOWNLOAD_DIR from config
    
    if not file_path.exists():
        logging.error(f"Download file not found on server for Job ID {job_id} at path: {file_path}")
        raise HTTPException(status_code=404, detail="File not found on server. It might have been deleted or an internal error occurred.")

    logging.info(f"Serving file {file_path} for Job ID {job_id}")
    return FileResponse(path=file_path, filename=filename_from_db, media_type="text/csv")
    ```

By meticulously going through these replacements, app/main.py will fully rely on the SQLite DatabaseManager, ensuring job persistence across restarts.
I've provided the full modified app/main.py code in the previous response, but this breakdown should clarify why and how those changes replace the job_status_db dict.
Please take your time to implement these changes, and let me know if any part remains unclear. Once this is done, we can proceed to Task 6.2: Finalize Local Configuration and Database Integration, which will focus on ensuring the SQLite database is correctly set up and integrated with the FastAPI application.

Task 6.2: Create Comprehensive Setup and Running Instructions
Goal: Provide a README.md (or a separate SETUP.md) that guides users from a fresh system to a running application.
Steps:
 * Create/Update README.md: This will be the primary source of truth for users.
 * Cover Prerequisites: Python installation, Tesseract OCR installation (with OS-specific commands).
 * Provide Setup Commands: Cloning the repo, creating a virtual environment, installing dependencies (pip install -r requirements.txt).
 * Provide Running Commands: How to start the FastAPI server (uvicorn).
 * Explain Usage: How to access the Swagger UI, upload files, check status, and download.
 * Detail Local Data Storage: Inform users where their processed files and database will reside.
Developer Genius Note: Anticipate common user pitfalls. Use clear, numbered steps. Include troubleshooting tips for common issues (e.g., "Tesseract not found").
Copilot Prompt (Create/Update README.md at the project root afsp_app/README.md):
# Automated Financial Statement Processor (AFSP)

## Overview

The Automated Financial Statement Processor (AFSP) is a powerful, local desktop application designed to streamline your financial data management. It uses advanced AI and OCR (Optical Character Recognition) to convert various financial documents (bank statements, receipts, invoices) into QuickBooks-ready CSV files.

**Key Features:**
* **Multi-Format Support:** Process CSV, PDF, DOCX, and image files (JPEG, PNG).
* **Intelligent Extraction:** Extracts dates, descriptions, and amounts from unstructured financial data.
* **Transaction Interpretation:** Normalizes extracted data and identifies transaction types (debit/credit).
* **QuickBooks CSV Generation:** Formats processed transactions into 3-column or 4-column QuickBooks-compatible CSVs.
* **Local Storage:** All processed data and job statuses are stored securely on your local machine, no cloud storage required.
* **Web API Interface:** Access the application's features through a local web API (Swagger UI) accessible via your browser.

## Getting Started

This application runs as a local web service on your machine. You will need to install Python and Tesseract OCR.

### Prerequisites

1.  **Python 3.8+:**
    * **Windows/macOS:** Download the installer from the official Python website: [python.org/downloads](https://www.python.org/downloads/).
    * **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install python3 python3-pip`
    * **Verify Installation:** Open a terminal/command prompt and type `python --version` or `python3 --version`.

2.  **Tesseract OCR:** This is the optical character recognition engine used for image and PDF processing. It must be installed separately and added to your system's PATH.
    * **Windows:** Download the installer from [Tesseract-OCR GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki). **Crucially, during installation, ensure "Add tesseract to your PATH" is selected.**
    * **macOS:** `brew install tesseract` (requires [Homebrew](https://brew.sh/)).
    * **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install tesseract-ocr`
    * **Verify Installation:** Open a terminal/command prompt and type `tesseract --version`. If it shows version information, Tesseract is correctly installed and accessible.

### Installation

Follow these steps to set up the AFSP application on your local machine:

1.  **Clone the Repository:**
    Open your terminal or command prompt and run:
    ```bash
    git clone [https://github.com/your-repo/afsp_app.git](https://github.com/your-repo/afsp_app.git)  # Replace with your actual repo URL
    cd afsp_app
    ```

2.  **Create a Virtual Environment (Recommended):**
    It's best practice to install dependencies in a virtual environment to avoid conflicts with other Python projects.
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    * **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    (Your terminal prompt should now show `(venv)` indicating the environment is active.)

4.  **Install Dependencies:**
    With your virtual environment activated, install all required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Once installed, you can start the AFSP local server:

1.  **Activate Virtual Environment:** (If not already active)
    * **Windows:** `.\venv\Scripts\activate`
    * **macOS/Linux:** `source venv/bin/activate`

2.  **Start the FastAPI Server:**
    Run the following command from the `afsp_app` root directory:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    * `--reload`: Automatically reloads the server on code changes (useful for development). Remove for production-like local deployment.
    * `--host 0.0.0.0`: Makes the server accessible from your local network (if needed). Use `--host 127.0.0.1` for strictly local access.
    * `--port 8000`: Specifies the port the server will run on. You can change this if port 8000 is in use.

    You should see output indicating that Uvicorn is running.

## Using the Application Interface

The AFSP application provides a user-friendly web API interface via Swagger UI.

1.  **Open in Browser:** Once the server is running, open your web browser and navigate to:
    `http://localhost:8000/docs`

2.  **Explore Endpoints:**
    * **`/upload_statement` (POST):** Use this endpoint to upload your bank statement or receipt file. Select the file, choose your desired QuickBooks CSV format (3-column or 4-column), and specify the date format. This will return a `job_id`.
    * **`/status/{job_id}` (GET):** Enter the `job_id` obtained from the upload endpoint to monitor the processing progress and status. You will see updates on ingestion, interpretation, and formatting.
    * **`/download/{job_id}` (GET):** Once the job status is "COMPLETED", this endpoint will become active. Enter the `job_id` to download your QuickBooks-ready CSV file.

## Local Data Storage

All temporary uploads, processed download files, and the application's job status database are stored directly on your local machine.

* **Main Data Directory:**
    * **Windows:** `%APPDATA%\AFSP_App\` (e.g., `C:\Users\YourUser\AppData\Roaming\AFSP_App\`)
    * **macOS:** `~/Library/Application Support/AFSP_App/`
    * **Linux:** `~/.local/share/AFSP_App/`

* **Subdirectories:**
    * `temp_uploads/`: Stores files temporarily during processing.
    * `processed_downloads/`: Stores your final QuickBooks CSV files.
    * `afsp.db`: The SQLite database file containing all job statuses and history.

## Troubleshooting

* **"Tesseract executable not found" error:** Ensure Tesseract OCR is installed correctly and its installation directory is added to your system's PATH. Restart your terminal after installation.
* **Port 8000 is already in use:** Change the `--port` argument when running `uvicorn` (e.g., `uvicorn app.main:app --port 8001`).
* **"FileNotFoundError" for temporary files:** Ensure the `UPLOAD_DIR` and `DOWNLOAD_DIR` have proper write permissions for your user. Check the `app/config.py` definitions and the actual paths created.
* **Job fails with "Critical processing error":** Check the Uvicorn terminal output for detailed error messages and Python tracebacks. These will provide clues as to which agent or tool encountered an issue.

---

Task 6.3: Update requirements.txt
Goal: Ensure requirements.txt is accurate and only includes necessary Python packages.
Steps:
 * Generate a fresh requirements.txt: Use pip freeze > requirements.txt after activating the virtual environment and installing all current dependencies.
 * Manually review and clean: Remove any extraneous packages (e.g., development tools, or packages that aren't strict runtime dependencies for the core app).
Copilot Prompt (Conceptual - execute these commands in your terminal):
 * First, clean up any previous build-related dependencies if you added them for the PyInstaller attempt.
 * Then, from your afsp_app root, with your virtual environment activated:
   pip freeze > requirements.txt

 * Manual Review/Cleanup: Open requirements.txt and ensure it primarily lists:
   * fastapi
   * uvicorn
   * pydantic (and pydantic-settings if used)
   * python-multipart (for file uploads in FastAPI)
   * PyPDF2
   * python-docx
   * Pillow (PIL)
   * pytesseract
   * httpx (for testing, consider moving to requirements-dev.txt if not needed at runtime)
   * pytest (for testing, consider moving to requirements-dev.txt)
   * pytest-asyncio (for testing, consider moving to requirements-dev.txt)
   * No PyInstaller or auto-py-to-exe should be present now.
This adjusted Compartment 6 provides a clear, manageable, and highly effective way to deploy your application for local desktop use. It focuses on stability and user guidance, which are critical for any "no stubs, no TODOs" release.
Once you've made these updates and are confident in the local server setup and instructions, let me know! Then, we can look at the Receipt Processing Add-on.
