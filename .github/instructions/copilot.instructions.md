---
applyTo: '**'
---
AI Assistant Context & Instructions (copilot_instructions.md)
Objective: Create a canonical source of truth for AI assistants, providing essential project context, standards, and constraints to guide their behavior and maintain code quality and consistency.
Developer Genius Note: This file acts as an externalized "brain" for the AI, capturing the implicit knowledge you've built throughout this development process. It's a living document that should be updated as the project evolves. The "no stubs, no TODOs" principle applies here: we're defining clear, actionable guidance.

# AFSP Project AI Assistant Instructions

## Project Summary

**Project Name:** Automated Financial Statement Processor (AFSP)

**Core Function:** Convert diverse financial documents (bank statements: CSV, PDF, DOCX; receipts: JPEG, PNG) into QuickBooks-ready CSV files. The application operates as a containerized local web service, processing files, storing job statuses in a local SQLite database, and providing downloadable results. No cloud storage or external services are used for core operations.

**Mission:** Streamline financial data management for individuals and small businesses by automating data extraction, interpretation, and formatting into a universally compatible accounting format.

**Deployment Architecture:** Fully containerized using Docker Compose with separate backend (FastAPI) and frontend (React) services, ensuring consistent development and deployment environments across all platforms.

## Core Principles & Development Philosophy

1.  **"No Stubs, No TODOs":** All generated code MUST be complete, functional, and production-ready. Avoid placeholder comments or incomplete logic. If a feature is not fully implementable, it should not be generated.
2.  **Developer Genius Mindset:** Focus on robust, efficient, and well-structured code. Prioritize maintainability, readability, and testability.
3.  **Local-First Design:** The application is designed to run entirely on the user's local machine using Docker containers. Avoid any reliance on cloud services, external APIs (unless explicitly added and configured by the user, e.g., for optional payment processors), or rented digital storage for core functionality.
4.  **Security & Privacy:** Given sensitive financial data, prioritize secure coding practices. Avoid logging sensitive data unnecessarily. Container isolation provides additional security boundaries.
5.  **User Experience (Containerized):** The primary user interaction is via the containerized web interface (React frontend) and API documentation (Swagger UI). Setup and usage should be as straightforward as running `docker-compose up`.
6.  **Extensibility:** Design components (agents, services) with clear responsibilities to facilitate future additions (e.g., more document types, different output formats).
7.  **Platform Independence:** Docker containerization ensures consistent behavior across Windows, macOS, and Linux development environments.

## Canonical Locations & File Structure

### Backend (Python/FastAPI)
* **Project Root:** `afsp_app/` (backend application directory).
* **Main Application Entry Point:** `afsp_app/app/main.py`
* **Application Logic (Modules):** `afsp_app/app/`
    * `app/agents/`: Core AI/logic modules (e.g., `raw_data_extraction_agent.py`, `transaction_interpretation_agent.py`, `quickbooks_formatter_agent.py`, `receipt_extractor_agent.py`).
    * `app/services/`: Utility services (e.g., `file_ingestion_service.py`).
    * `app/tools/`: Helper functions (e.g., `ocr_tool.py`, `date_parser.py`, `amount_parser.py`, `description_cleaner.py`).
    * `app/schemas.py`: Pydantic models for data validation and API schemas.
    * `app/config.py`: Centralized application configuration (paths, settings).
    * `app/database.py`: SQLite database management.
* **Tests:** `afsp_app/tests/`

### Frontend (React)
* **Project Root:** `frontend/` (frontend application directory).
* **Main Entry Point:** `frontend/src/index.js`
* **Application Structure:** `frontend/src/`
    * `src/components/`: Reusable UI components (e.g., `FileUpload.js`, `Header.js`, `Footer.js`).
    * `src/pages/`: Page components (e.g., `HomePage.js`, `UploadPage.js`, `JobsPage.js`, `JobDetailsPage.js`, `SettingsPage.js`).
    * `src/services/`: API and other services (e.g., `api.js`, `errorTracker.js`).
    * `src/context/`: React context providers.
    * `src/App.js`: Main application component.

### Containerization
* **Docker Configuration:**
    * `Dockerfile` (backend): Python 3.11-slim with system dependencies (libmagic1, tesseract-ocr, pkg-config).
    * `frontend/Dockerfile` (frontend): Node.js 18 for React development server.
    * `docker-compose.yml`: Orchestrates both services with proper networking and volume mounts.
    * `.dockerignore` & `frontend/.dockerignore`: Exclude unnecessary files from container builds.

### Configuration Files
* **Backend:**
    * `afsp_app/requirements.txt`: Python runtime dependencies.
    * `afsp_app/pyproject.toml`: Project metadata and build configuration.
* **Frontend:**
    * `frontend/package.json`: Node.js dependencies and scripts.
    * `frontend/package-lock.json`: Locked dependency versions.
* **Development:**
    * `afsp_app/.pre-commit-config.yaml`: Automated code quality hooks.
    * `afsp_app/.gitignore`: Version control exclusions.

### Data Directories (Container Volumes)
* **Backend Volumes:**
    * `afsp_app/uploads/`: Temporary file uploads (mounted as volume).
    * `afsp_app/downloads/`: Processed output files (mounted as volume).
    * `afsp_app/afsp.db`: SQLite database (persisted via volume mount).

## Vital Project Specifics

### Backend Technology Stack
* **Framework:** FastAPI for the web API.
* **Runtime:** Python 3.11 in Docker container.
* **Asynchronous Operations:** Leverage `asyncio` for background tasks to keep the API responsive.
* **OCR Engine:** Tesseract OCR (installed via system packages in Docker container; `pytesseract` is the Python wrapper).
* **Database:** SQLite for local, persistent job status and metadata storage.
* **Data Models:** Pydantic for strict data validation and clear API schemas (e.g., `RawTransactionData`, `ExtractedTransaction`, `NormalizedTransaction`, `ReceiptData`).
* **Logging:** Use Python's `logging` module for informative output.
* **Testing:** Pytest for unit and E2E testing. Mock external dependencies (like `pytesseract`) where necessary in tests.

### Frontend Technology Stack
* **Framework:** React 18 with Create React App.
* **Runtime:** Node.js 18 in Docker container.
* **Styling:** Tailwind CSS for responsive design.
* **HTTP Client:** Axios for API communication.
* **Routing:** React Router DOM for navigation.
* **Development Server:** Webpack dev server with hot reloading.
* **Accessibility:** @axe-core/react for development-time accessibility testing.

### Container Architecture
* **Backend Container:**
  - Base Image: `python:3.11-slim`
  - System Dependencies: `libmagic1`, `tesseract-ocr`, `pkg-config`
  - Exposed Port: 8000
  - Volume Mounts: Application code, uploads, downloads, database
* **Frontend Container:**
  - Base Image: `node:18`
  - Exposed Port: 3000
  - Development Mode: Hot reloading enabled
  - Volume Mounts: Application code for live development
* **Networking:** Docker Compose internal network for service communication
* **CORS Configuration:** Backend configured to accept requests from frontend container

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

### Prerequisites
- Docker and Docker Compose installed on your system
- No additional dependencies required (everything runs in containers)

### Quick Start
1. **Start the application:**
   ```bash
   docker-compose up -d
   ```
   This command will:
   - Build both backend and frontend containers (if not already built)
   - Start the FastAPI backend on port 8000
   - Start the React development server on port 3000
   - Set up internal networking between services

2. **Access the application:**
   - **Frontend UI:** http://localhost:3000
   - **Backend API:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs (Swagger UI)

3. **View logs (optional):**
   ```bash
   docker-compose logs frontend  # Frontend logs
   docker-compose logs backend   # Backend logs
   docker-compose logs -f        # Follow all logs
   ```

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Development Workflow
- **Code Changes:** Both frontend and backend code changes are reflected immediately via volume mounts
- **Rebuild after dependency changes:**
  ```bash
  docker-compose up --build -d
  ```
- **Container status:**
  ```bash
  docker-compose ps
  ```

### Troubleshooting
- **Port conflicts:** Ensure ports 3000 and 8000 are available
- **Container build issues:** Check Docker logs with `docker-compose logs [service]`
- **Volume permissions:** Ensure Docker has access to the project directory

## Key Features

1. **File Upload Interface**
   - Drag-and-drop file uploads
   - Support for multiple file formats (CSV, PDF, DOCX, JPEG, PNG)
   - Format selection options
   - Real-time upload progress

2. **Job Status Dashboard**
   - Real-time status updates
   - Job history tracking
   - Pagination for large job lists
   - Error reporting and retry capabilities

3. **Results Viewer**
   - Preview of processed data
   - Download functionality for QuickBooks CSV
   - Data validation summaries

4. **Settings/Configuration**
   - User preferences for CSV formats
   - Date format customization
   - Auto-refresh settings
   - Processing options

5. **Containerized Architecture**
   - Consistent development environment
   - Easy deployment and scaling
   - Isolated dependencies
   - Cross-platform compatibility

## Documentation

### Project Documentation
- `README.md` - Project overview and setup instructions
- `thisdocument.md` - Comprehensive AI assistant instructions (this file)
- `CHANGELOG.md` - Version history and updates
- `CONTRIBUTING.md` - Development contribution guidelines

### Technical Documentation
- `docker-compose.yml` - Container orchestration configuration
- `Dockerfile` & `frontend/Dockerfile` - Container build specifications
- API documentation available at http://localhost:8000/docs when running

### Development Resources
- Frontend implementation follows React best practices with hooks and functional components
- Backend follows FastAPI patterns with async/await and dependency injection
- Both services include comprehensive error handling and logging
- Container logs provide detailed debugging information

These documents provide a comprehensive overview of the containerized implementation and usage instructions.


## Behavioral Guidelines for AI Assistant

* **Context Retention:** Remember all previous instructions, code snippets, and discussions throughout the conversation.
* **Clarity & Conciseness:** Provide clear, direct, and actionable responses. Avoid verbose explanations unless specifically requested.
* **Code Generation:** When generating code, provide complete, runnable snippets. Indicate new files, modifications to existing files, and relevant imports.
* **Error Handling:** Always include robust error handling (try/except blocks, logging) in generated code.
* **Parameter Naming:** Use clear, descriptive, and consistent parameter and variable names (snake_case for Python, camelCase for JavaScript).
* **Type Hinting:** Utilize Python type hints (`List[str]`, `Optional[int]`, etc.) for all function signatures and complex variables.
* **Imports:** Ensure all necessary imports are at the top of the file.
* **Testing Focus:** Always consider how new features can be tested. If proposing a new feature, be prepared to outline test cases or generate test code.
* **Questioning for Clarity:** If a request is ambiguous, ask clarifying questions before generating code or detailed plans.
* **Container Awareness:** When making changes, consider whether container rebuilds are needed and provide appropriate Docker commands.
* **Service Communication:** Understand that frontend and backend communicate via HTTP within the Docker network.
* **Adherence to Principles:** Every response and generated piece of code MUST adhere to the "no stubs, no TODOs," "Developer Genius," and "Local-First" principles. Do not propose or generate solutions that require cloud resources unless explicitly overridden by the user.
* **No Placeholders:** Do not use `TODO`, `FIXME`, `[YOUR_REPLACE_HERE]`, or similar placeholders in generated code or documentation. Provide real values or specific instructions for the user to provide them.
* **Platform Independence:** Ensure all solutions work consistently across Windows, macOS, and Linux via containerization.





