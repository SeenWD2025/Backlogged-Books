# Enhancement Checklist for Backlogged-Books

This checklist outlines all the necessary actions to address the issues identified in the application review and implement the recommended enhancements. Each task is categorized by component and includes installation commands where applicable.

## Backend Enhancements

### Security Fixes

- [ ] **Fix CORS Configuration**
  ```python
  # Update in afsp_app/app/main.py
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],  # Replace with specific origins in production
      allow_credentials=True,
      allow_methods=["GET", "POST"],
      allow_headers=["*"],
  )
  ```

- [ ] **Secure File Upload Handling**
  ```python
  # Update in afsp_app/app/main.py
  file_name = Path(file.filename).name  # Get just the name, not the path
  safe_filename = secure_filename(file_name)  # Use werkzeug's secure_filename
  file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{safe_filename}")
  
  # Install dependency
  pip install werkzeug
  ```

- [ ] **Implement Robust File Validation**
  ```bash
  # Install python-magic for better file type detection
  pip install python-magic
  ```
  ```python
  # Add to afsp_app/app/main.py
  import magic
  
  # In upload_file function
  file_content = await file.read(1024)  # Read first 1KB for type detection
  mime = magic.Magic(mime=True)
  detected_type = mime.from_buffer(file_content)
  
  if detected_type not in ALLOWED_EXTENSIONS.values():
      raise HTTPException(
          status_code=400,
          detail=f"Invalid file type detected: {detected_type}. Supported types: {', '.join(ALLOWED_EXTENSIONS.values())}"
      )
  
  # Reset file pointer
  await file.seek(0)
  ```

### Code Quality & Performance

- [ ] **Improve Exception Handling**
  ```python
  # Update process_file in afsp_app/app/main.py to use specific exceptions
  try:
      # Specific operation
  except FileNotFoundError as e:
      logger.error(f"File not found: {str(e)}")
      db_manager.update_job_status(job_id, "FAILED", error_message=f"File not found: {str(e)}")
  except (ValueError, TypeError) as e:
      logger.error(f"Data parsing error: {str(e)}")
      db_manager.update_job_status(job_id, "FAILED", error_message=f"Data parsing error: {str(e)}")
  except Exception as e:
      logger.error(f"Unexpected error: {str(e)}")
      db_manager.update_job_status(job_id, "FAILED", error_message=f"Processing failed: {str(e)}")
  ```

- [ ] **Fix Missing Agent Issue**
  ```bash
  # Implement the missing transaction_interpretation_agent.py
  ```
  
- [ ] **Implement Configuration Management**
  ```bash
  # Install pydantic-settings
  pip install pydantic-settings
  ```
  ```python
  # Create afsp_app/app/settings.py
  from pydantic_settings import BaseSettings, SettingsConfigDict
  from pathlib import Path
  
  class Settings(BaseSettings):
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
      
      # Security settings
      ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
      
      # API settings
      API_TITLE: str = "Automated Financial Statement Processor"
      API_DESCRIPTION: str = "Convert bank statements and receipts to QuickBooks-compatible CSV formats"
      API_VERSION: str = "1.0.0"
      
      model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
      
  # Create settings instance
  settings = Settings()
  ```

- [ ] **Implement Structured Logging**
  ```python
  # Update logging in afsp_app/app/main.py
  import json
  import logging
  import sys
  from datetime import datetime
  
  class StructuredFormatter(logging.Formatter):
      def format(self, record):
          log_record = {
              "timestamp": datetime.utcnow().isoformat(),
              "level": record.levelname,
              "message": record.getMessage(),
              "module": record.module,
              "function": record.funcName,
          }
          
          # Add job_id if available in record
          if hasattr(record, "job_id"):
              log_record["job_id"] = record.job_id
              
          # Add exception info if available
          if record.exc_info:
              log_record["exception"] = str(record.exc_info[1])
              
          return json.dumps(log_record)
  
  # Create handler with the formatter
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(StructuredFormatter())
  
  # Configure logger
  logger = logging.getLogger("afsp")
  logger.setLevel(logging.INFO)
  logger.addHandler(handler)
  ```

- [ ] **Improve PDF Processing**
  ```bash
  # Install pdf2image for converting PDF pages to images
  pip install pdf2image
  ```
  ```python
  # Update _extract_from_pdf in afsp_app/app/agents/raw_data_extraction_agent.py
  from pdf2image import convert_from_path
  import tempfile
  
  # In _extract_from_pdf
  if not text or len(text.strip()) < 100:
      logger.info(f"Page {i+1} has little or no extractable text, attempting OCR")
      # Convert PDF page to image
      with tempfile.TemporaryDirectory() as path:
          images = convert_from_path(file_path, output_folder=path, first_page=i+1, last_page=i+1)
          if images:
              # Process the image with OCR
              with tempfile.NamedTemporaryFile(suffix='.png') as temp:
                  images[0].save(temp.name)
                  with open(temp.name, 'rb') as img_file:
                      ocr_text = perform_ocr(img_file.read())
                  text = ocr_text or text
  ```

- [ ] **Implement Asynchronous Database Operations**
  ```bash
  # Install aiosqlite
  pip install aiosqlite
  ```
  ```python
  # Update database.py to use async operations
  import aiosqlite
  
  class DatabaseManager:
      # Update methods to be async
      async def _initialize_db(self) -> None:
          # ...
          async with aiosqlite.connect(self.db_path) as conn:
              await conn.execute('''
              CREATE TABLE IF NOT EXISTS jobs (
                  # ...
              ''')
              # ...
              await conn.commit()
      
      # Update other methods similarly
  ```

## Frontend Enhancements

### Security Fixes

- [ ] **Check for Dependency Vulnerabilities**
  ```bash
  # Run npm audit and fix issues
  cd frontend
  npm audit
  npm audit fix
  ```

- [ ] **Ensure Input Sanitization**
  ```bash
  # Install DOMPurify for sanitizing HTML
  cd frontend
  npm install dompurify
  ```
  ```javascript
  // Example usage in components that might render HTML
  import DOMPurify from 'dompurify';
  
  // When rendering user-generated content
  const sanitizedContent = DOMPurify.sanitize(userGeneratedContent);
  ```

### Feature Enhancements

- [ ] **Implement Advanced State Management**
  ```bash
  # Install Redux Toolkit
  cd frontend
  npm install @reduxjs/toolkit react-redux
  ```

- [ ] **Add Granular Processing Feedback**
  ```javascript
  // Update the JobDetailsPage.js to display more detailed status
  // Requires backend changes to provide more granular status updates
  
  // Example status mapping
  const statusMessages = {
    "PROCESSING": "Processing your file...",
    "EXTRACTING_DATA": "Extracting transaction data...",
    "INTERPRETING_TRANSACTIONS": "Interpreting transactions...",
    "FORMATTING_CSV": "Formatting data for QuickBooks..."
  };
  
  // Display the appropriate message based on the job status
  <div className="status-message">
    {statusMessages[job.status] || job.status}
  </div>
  ```

- [ ] **Implement Optimistic UI Updates**
  ```javascript
  // Example for deleting a job in JobsPage.js
  
  const deleteJob = async (jobId) => {
    // Store the job being deleted
    const jobToDelete = jobs.find(job => job.job_id === jobId);
    
    // Optimistically remove from UI
    setJobs(jobs.filter(job => job.job_id !== jobId));
    
    try {
      // Actually perform the deletion
      await api.deleteJob(jobId);
    } catch (error) {
      // If it fails, restore the job to the list with an error flag
      console.error('Failed to delete job', error);
      jobToDelete.deleteError = true;
      setJobs([...jobs.filter(job => job.job_id !== jobId), jobToDelete]);
      setError('Failed to delete job. Please try again.');
    }
  };
  ```

## Testing Suite Implementation

### Backend Testing

- [ ] **Set Up Backend Testing Framework**
  ```bash
  # Install pytest and related packages
  pip install pytest pytest-asyncio pytest-mock httpx
  ```

- [ ] **Implement Unit Tests for Tools**
  ```bash
  # Create tests for each tool
  touch afsp_app/tests/test_amount_parser.py
  touch afsp_app/tests/test_date_parser.py
  touch afsp_app/tests/test_description_cleaner.py
  touch afsp_app/tests/test_ocr_tool.py
  ```

- [ ] **Implement Agent Tests with Mock Data**
  ```bash
  # Create tests for agents
  touch afsp_app/tests/test_raw_data_extraction_agent.py
  touch afsp_app/tests/test_transaction_interpretation_agent.py
  touch afsp_app/tests/test_quickbooks_formatter_agent.py
  ```

- [ ] **Implement Database Tests**
  ```bash
  # Create tests for database operations
  touch afsp_app/tests/test_database.py
  ```

- [ ] **Create End-to-End API Tests**
  ```bash
  # Create E2E tests
  touch afsp_app/tests/test_api_e2e.py
  ```

### Frontend Testing

- [ ] **Set Up Frontend Testing Framework**
  ```bash
  # Install testing libraries
  cd frontend
  npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest
  ```

- [ ] **Create Component Unit Tests**
  ```bash
  # Create test files for components
  touch frontend/src/components/__tests__/Header.test.js
  touch frontend/src/components/__tests__/Footer.test.js
  ```

- [ ] **Create Service Unit Tests**
  ```bash
  # Create test for the API service
  touch frontend/src/services/__tests__/api.test.js
  ```

- [ ] **Set Up End-to-End Testing with Cypress**
  ```bash
  # Install Cypress
  cd frontend
  npm install --save-dev cypress
  
  # Initialize Cypress
  npx cypress open
  ```

- [ ] **Create E2E Test Scenarios**
  ```bash
  # Create test files for key user flows
  touch frontend/cypress/integration/upload_flow.spec.js
  touch frontend/cypress/integration/error_handling.spec.js
  ```

## Production Readiness

- [ ] **Set Up CI/CD Pipeline**
  ```yaml
  # Create .github/workflows/ci-cd.yml
  name: CI/CD Pipeline
  
  on:
    push:
      branches: [ main ]
    pull_request:
      branches: [ main ]
  
  jobs:
    backend-tests:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.12'
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
            pip install -r requirements-dev.txt
        - name: Run tests
          run: pytest
  
    frontend-tests:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Set up Node.js
          uses: actions/setup-node@v3
          with:
            node-version: '18'
        - name: Install dependencies
          working-directory: ./frontend
          run: npm ci
        - name: Run tests
          working-directory: ./frontend
          run: npm test
  ```

- [ ] **Create Environment Configuration Files**
  ```bash
  # Create example .env file
  touch .env.example
  ```

- [ ] **Update Documentation for Production Deployment**
  ```bash
  # Create production deployment guide
  touch production_deployment_guide.md
  ```

- [ ] **Create Backup and Restore Scripts**
  ```bash
  # Update backup_restore.sh to include new database tables and configurations
  ```

By completing all items in this checklist, the Backlogged-Books application will be ready for a secure, robust, and maintainable production deployment.
