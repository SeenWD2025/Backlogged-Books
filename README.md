# Backlogged-Books
Accounting application that converts receipts, bank statements and other transaction data sources into 3 columns or 4 columns CSV formatted for quickbooks upload. 

Master Developer Guide: Automated Financial Statement Processor (AFSP)
Version: 1.0
Date: July 31, 2025
1. Project Overview
The Automated Financial Statement Processor (AFSP) is a robust, local-first desktop application that functions as a web service. Its primary purpose is to automate the conversion of various financial documents—including bank statements (PDF, DOCX, CSV) and receipts (JPEG, PNG)—into a standardized QuickBooks-compatible CSV format. The application is designed to be entirely self-contained, running on a user's machine without relying on any cloud services or external data storage.
Core Principles:
 * "No Stubs, No TODOs": All code must be complete, functional, and production-ready.
 * Local-First: All data processing and storage occur on the user's local machine using a local web service and a SQLite database.
 * Modularity: The codebase is organized into distinct, single-responsibility components (agents, services, tools) for maintainability and extensibility.
 * Robustness: The application is built with comprehensive error handling, logging, and automated testing to ensure reliability.
2. Technology Stack
 * Framework: FastAPI
 * Asynchronous Tasks: asyncio
 * Data Validation: Pydantic
 * Database: SQLite (local persistence)
 * OCR: Tesseract OCR (with pytesseract Python wrapper)
 * File Handling: Python's standard libraries, PyPDF2, python-docx, Pillow
 * Testing: pytest with pytest-asyncio
3. Project Structure (Canonical Locations)
The project adheres to a clean, modular structure. All files should be placed in their designated directories.
afsp_app/
├── app/
│   ├── agents/
│   │   ├── quickbooks_formatter_agent.py
│   │   ├── raw_data_extraction_agent.py
│   │   ├── receipt_extractor_agent.py      # NEW
│   │   └── transaction_interpretation_agent.py
│   ├── services/
│   │   └── file_ingestion_service.py
│   ├── tools/
│   │   ├── amount_parser.py
│   │   ├── date_parser.py
│   │   ├── description_cleaner.py
│   │   └── ocr_tool.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_main_e2e.py
│   ├── test_receipt_agent.py            # NEW
│   └── test_tools.py
├── .gitignore
├── .pre-commit-config.yaml
├── copilot_instructions.md
├── pyproject.toml
├── README.md
├── requirements-dev.txt
└── requirements.txt

4. Key Components & Their Responsibilities
 * app/main.py: The FastAPI application entry point. It defines API endpoints (/upload, /status, /download), manages job IDs, and orchestrates the background processing pipeline by calling the agents and services. It interacts directly with DatabaseManager.
 * app/schemas.py: Contains all Pydantic models (e.g., RawTransactionData, ExtractedTransaction, NormalizedTransaction, ReceiptData, StatusResponse) that define the data structures for agents and API communication.
 * app/config.py: A central hub for all application-wide configurations, including file paths (UPLOAD_DIR, DOWNLOAD_DIR, DATABASE_PATH) and OCR settings (TESSERACT_PATH).
 * app/database.py: Encapsulates all SQLite database logic. The DatabaseManager class provides methods to initialize the database and perform CRUD operations on job statuses, ensuring data persistence.
 * app/services/file_ingestion_service.py: The first step in the pipeline. It identifies the file type (PDF, CSV, image, etc.) and performs the initial raw text extraction, including calling the ocr_tool for images and PDFs.
 * app/tools/ocr_tool.py: A simple wrapper around pytesseract to perform OCR on images. It is called by file_ingestion_service.
 * app/agents/raw_data_extraction_agent.py: Processes raw text data from bank statements (CSV, PDF, DOCX) and uses a set of rules and heuristics to identify and extract transactional fields (date, description, amount, credit/debit).
 * app/agents/receipt_extractor_agent.py: A specialized agent that uses regex and pattern matching to extract structured fields (vendor name, date, total amount, line items) from the raw OCR text of receipt images.
 * app/agents/transaction_interpretation_agent.py: The "brain" of the operation. It takes extracted fields from either a bank statement or a receipt and converts them into a final, standardized NormalizedTransaction schema, ready for formatting.
 * app/agents/quickbooks_formatter_agent.py: The final-stage agent. It takes a list of NormalizedTransaction objects and generates a CSV string formatted for QuickBooks, handling 3-column and 4-column variants.
5. Installation & Setup Guide
This guide covers setting up a development environment. Refer to the README.md for end-user instructions.
 * Prerequisites:
   * Python 3.8+: Ensure a recent version of Python is installed.
   * Tesseract OCR: Tesseract must be installed on your system and its executable must be in your system's PATH.
 * Clone the Repository:
   git clone https://github.com/your-repo/afsp_app.git
cd afsp_app

 * Setup Virtual Environment:
   python -m venv venv
source venv/bin/activate  # Or `.\venv\Scripts\activate` on Windows

 * Install Dependencies:
   pip install -r requirements.txt
pip install -r requirements-dev.txt # For testing and development tools

 * Install Pre-commit Hooks:
   pre-commit install

6. Development Workflow
 * Code Formatting: All code must be formatted using black and imports sorted with isort. The pre-commit hooks automate this, so you don't have to run them manually.
 * Testing: Run tests frequently during development. All new features and bug fixes must have corresponding tests.
   pytest

 * Running the Application (for testing):
   uvicorn app.main:app --reload

 * Access the API: The Swagger UI is available at http://127.0.0.1:8000/docs.
7. "No Stubs, No TODOs" Checklist
Before committing any code, ensure all work adheres to this checklist:
 * All functions and methods have clear docstrings.
 * All variables and parameters have type hints.
 * All API endpoints are fully documented with summary and description attributes.
 * All try...except blocks handle specific exceptions, not a generic Exception.
 * Logging is used to track progress and flag errors, not print statements.
 * New features include corresponding unit and/or E2E tests.
 * The code is formatted correctly (automated by pre-commit).
 * No code is commented out or left as a placeholder.
This Master Developer Guide, combined with the detailed instructions in copilot_instructions.md, gives you a solid, well-defined foundation. You now have everything you need to start building the application with confidence and consistency.

