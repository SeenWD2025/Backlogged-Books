---
applyTo: '**'
---
AI Assistant Context & Instructions (copilot_instructions.md)
Objective: Create a canonical source of truth for AI assistants, providing essential project context, standards, and constraints to guide their behavior and maintain code quality and consistency.
Developer Genius Note: This file acts as an externalized "brain" for the AI, capturing the implicit knowledge you've built throughout this development process. It's a living document that should be updated as the project evolves. The "no stubs, no TODOs" principle applies here: we're defining clear, actionable guidance.
Task 9.1: Draft copilot_instructions.md
Goal: Write a concise yet comprehensive set of instructions covering project overview, core principles, technical specifics, and behavioral guidelines for AI assistants.
Copilot Prompt (Create copilot_instructions.md at the project root afsp_app/copilot_instructions.md):
# AFSP Project AI Assistant Instructions

## Project Summary

**Project Name:** Automated Financial Statement Processor (AFSP)

**Core Function:** Convert diverse financial documents (bank statements: CSV, PDF, DOCX; receipts: JPEG, PNG) into QuickBooks-ready CSV files. The application operates as a local web service on the user's desktop, processing files, storing job statuses in a local SQLite database, and providing downloadable results. No cloud storage or external droplets are used for core operations.

**Mission:** Streamline financial data management for individuals and small businesses by automating data extraction, interpretation, and formatting into a universally compatible accounting format.

## Core Principles & Development Philosophy

1.  **"No Stubs, No TODOs":** All generated code MUST be complete, functional, and production-ready. Avoid placeholder comments or incomplete logic. If a feature is not fully implementable, it should not be generated.
2.  **Developer Genius Mindset:** Focus on robust, efficient, and well-structured code. Prioritize maintainability, readability, and testability.
3.  **Local-First Design:** The application is designed to run entirely on the user's local machine. Avoid any reliance on cloud services, external APIs (unless explicitly added and configured by the user, e.g., for optional payment processors), or rented digital storage for core functionality.
4.  **Security & Privacy:** Given sensitive financial data, prioritize secure coding practices. Avoid logging sensitive data unnecessarily.
5.  **User Experience (Local Focus):** The primary user interaction is via the local web API (Swagger UI). Setup and usage should be as straightforward as possible, relying on clear documentation.
6.  **Extensibility:** Design components (agents, services) with clear responsibilities to facilitate future additions (e.g., more document types, different output formats).

## Canonical Locations & File Structure

* **Project Root:** `afsp_app/` (this directory).
* **Main Application Entry Point:** `afsp_app/app/main.py`
* **Application Logic (Modules):** `afsp_app/app/`
    * `app/agents/`: Core AI/logic modules (e.g., `raw_data_extraction_agent.py`, `transaction_interpretation_agent.py`, `quickbooks_formatter_agent.py`, `receipt_extractor_agent.py`).
    * `app/services/`: Utility services (e.g., `file_ingestion_service.py`).
    * `app/tools/`: Helper functions (e.g., `ocr_tool.py`, `date_parser.py`, `amount_parser.py`, `description_cleaner.py`).
    * `app/schemas.py`: Pydantic models for data validation and API schemas.
    * `app/config.py`: Centralized application configuration (paths, settings).
    * `app/database.py`: SQLite database management.
* **Tests:** `afsp_app/tests/`
* **Documentation:** `afsp_app/README.md`, `afsp_app/CHANGELOG.md` (if applicable), `afsp_app/CONTRIBUTING.md` (if applicable).
* **Configuration Files:**
    * `afsp_app/requirements.txt`: Python runtime dependencies.
    * `afsp_app/pyproject.toml`: Project metadata and build configuration.
    * `afsp_app/.pre-commit-config.yaml`: Automated code quality hooks.
    * `afsp_app/.gitignore`: Version control exclusions.
* **Data Directories (managed by `app/config.py`):**
    * `APP_DATA_DIR/temp_uploads/`
    * `APP_DATA_DIR/processed_downloads/`
    * `APP_DATA_DIR/afsp.db` (SQLite database)

## Vital Project Specifics

* **Framework:** FastAPI for the web API.
* **Asynchronous Operations:** Leverage `asyncio` for background tasks to keep the API responsive.
* **OCR Engine:** Tesseract OCR (requires system-level installation; `pytesseract` is the Python wrapper).
* **Database:** SQLite for local, persistent job status and metadata storage.
* **Data Models:** Pydantic for strict data validation and clear API schemas (e.g., `RawTransactionData`, `ExtractedTransaction`, `NormalizedTransaction`, `ReceiptData`).
* **Logging:** Use Python's `logging` module for informative output.
* **Testing:** Pytest for unit and E2E testing. Mock external dependencies (like `pytesseract`) where necessary in tests.

# Automated Financial Statement Processor - Frontend

## Implementation Summary

We've successfully created a React-based frontend for the Automated Financial Statement Processor application. The frontend provides a user-friendly interface for uploading financial documents, tracking processing jobs, and downloading QuickBooks-compatible CSV files.

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── FileUpload.js
│   │   ├── Header.js
│   │   └── Footer.js
│   ├── pages/           # Page components
│   │   ├── HomePage.js
│   │   ├── UploadPage.js
│   │   ├── JobsPage.js
│   │   ├── JobDetailsPage.js
│   │   └── SettingsPage.js
│   ├── services/        # API and other services
│   │   └── api.js
│   ├── context/         # React context providers
│   ├── App.js           # Main application component
│   └── index.js         # Entry point
└── package.json         # Dependencies and scripts
```

## Running the Application

1. Make sure you have Node.js installed.
2. Run the start script:
   ```
   ./start_app.sh
   ```
   This script will:
   - Start the FastAPI backend on port 8000
   - Install frontend dependencies
   - Start the React development server on port 3000

3. Access the application at:
   ```
   http://localhost:3000
   ```

## Key Features

1. **File Upload Interface**
   - Drag-and-drop file uploads
   - Support for multiple file formats (CSV, PDF, DOCX, JPEG, PNG)
   - Format selection options

2. **Job Status Dashboard**
   - Real-time status updates
   - Job history tracking
   - Pagination for large job lists

3. **Results Viewer**
   - Preview of processed data
   - Download functionality for QuickBooks CSV

4. **Settings/Configuration**
   - User preferences for CSV formats
   - Date format customization
   - Auto-refresh settings

## Documentation

We've created several documentation files:

- `frontend_development_guide.md` - Development checklist with progress tracking
- `frontend_implementation_summary.md` - Technical implementation details
- `quick_start_guide.md` - User guide for the application

These documents provide a comprehensive overview of the frontend implementation and usage instructions.


## Behavioral Guidelines for AI Assistant

* **Context Retention:** Remember all previous instructions, code snippets, and discussions throughout the conversation.
* **Clarity & Conciseness:** Provide clear, direct, and actionable responses. Avoid verbose explanations unless specifically requested.
* **Code Generation:** When generating code, provide complete, runnable snippets. Indicate new files, modifications to existing files, and relevant imports.
* **Error Handling:** Always include robust error handling (try/except blocks, logging) in generated code.
* **Parameter Naming:** Use clear, descriptive, and consistent parameter and variable names (snake_case).
* **Type Hinting:** Utilize Python type hints (`List[str]`, `Optional[int]`, etc.) for all function signatures and complex variables.
* **Imports:** Ensure all necessary imports are at the top of the file.
* **Testing Focus:** Always consider how new features can be tested. If proposing a new feature, be prepared to outline test cases or generate test code.
* **Questioning for Clarity:** If a request is ambiguous, ask clarifying questions before generating code or detailed plans.
* **Adherence to Principles:** Every response and generated piece of code MUST adhere to the "no stubs, no TODOs," "Developer Genius," and "Local-First" principles. Do not propose or generate solutions that require cloud resources unless explicitly overridden by the user.
* **No Placeholders:** Do not use `TODO`, `FIXME`, `[YOUR_REPLACE_HERE]`, or similar placeholders in generated code or documentation. Provide real values or specific instructions for the user to provide them.





