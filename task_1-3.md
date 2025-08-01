Alright, this is an exciting challenge! Developing with VS Code and GitHub Copilot, aiming for a "no stubs, no TODOs" flawless process, means we need extreme clarity and explicit definitions from the start. We'll leverage Copilot's strengths for code generation and refactoring by providing exceptionally detailed prompts and structured inputs.
Given your goal of cost-effectiveness and time-saving, Python is an excellent choice for this, with its rich ecosystem of AI/ML and data processing libraries. We'll design this modularly, but with a strong emphasis on seamless integration.
Let's dive into the detailed, explicit development guide!
AI-Powered Bookkeeping Reconciliation App: Flawless Development Guide
Project Name: Automated Financial Statement Processor (AFSP)
Development Environment: VS Code, Python 3.9+, GitHub Copilot (with Agent Mode and paid membership)
Core Principle: Explicit Design, Modular Agents, Data-Driven Development, Continuous Integration/Deployment (CI/CD) Ready.
Phase 1: Foundational Design & Schema Definition
The goal here is to define every piece of data, every interaction, and every module's responsibility before writing significant code. This upfront clarity will minimize rework and "TODOs."
1.1. Data Schemas & Models
Define the exact structure of all data throughout the application. This will serve as the contract between different modules/agents.
1.1.1. RawTransactionData Schema (Input from various files)
This will be the initial, unstructured data extracted from source documents.
 * Purpose: To capture all potential fields from diverse bank statements and receipts before normalization.
 * Fields:
   * raw_text: str (Entire block of text/OCR output from a section)
   * source_file_name: str
   * source_file_type: Literal["CSV", "PDF", "DOCX", "JPEG", "PNG"]
   * page_number: Optional[int] (For multi-page documents)
   * line_number: Optional[int] (Approximation for text-based extraction)
   * bounding_box: Optional[Tuple[float, float, float, float]] (For image-based extraction: x_min, y_min, x_max, y_max)
   * timestamp_extracted: datetime
1.1.2. ExtractedTransaction Schema (After initial extraction, before interpretation)
This is the first structured output, where fields are identified but not yet fully normalized or categorized.
 * Purpose: To hold raw extracted values, allowing for later validation and interpretation.
 * Fields:
   * unique_id: str (UUID for tracking)
   * raw_text_reference: str (Link back to RawTransactionData.raw_text)
   * potential_date_str: Optional[str]
   * potential_description_str: Optional[str]
   * potential_amount_str: Optional[str] (Can be positive or negative, or just a number string)
   * potential_credit_str: Optional[str]
   * potential_debit_str: Optional[str]
   * confidence_score: Dict[str, float] (Confidence for each extracted field, e.g., {"date": 0.95, "amount": 0.88})
   * extraction_errors: List[str] (List of any issues encountered during extraction)
1.1.3. NormalizedTransaction Schema (Interpreted and standardized data)
This is the clean, validated, and categorized financial transaction data.
 * Purpose: To provide a consistent format for all transactions, ready for CSV generation.
 * Fields:
   * transaction_id: str (UUID, possibly carried over from unique_id or newly generated)
   * date: date (Python date object, strictly YYYY-MM-DD)
   * description: str (Cleaned, consolidated description)
   * amount: float (Strictly a single float, positive for income/credit, negative for expense/debit)
   * transaction_type: Literal["Credit", "Debit"]
   * original_source_file: str
   * processing_notes: List[str] (Any notes about manual corrections or specific processing steps)
1.1.4. QuickBooksCSVRow Schema (Final output format)
Defines the exact structure for QuickBooks-compatible CSV rows.
 * 3-Column Format:
   * Date: str (Format: MM/DD/YYYY or DD/MM/YYYY - User selects during upload)
   * Description: str
   * Amount: str (Negative for debits/expenses, positive for credits/income. No currency symbols. e.g., -123.45, 78.90)
 * 4-Column Format:
   * Date: str (Format: MM/DD/YYYY or DD/MM/YYYY - User selects during upload)
   * Description: str
   * Credit: str (Positive number for credits/income, empty string if debit. e.g., 78.90, ``)
   * Debit: str (Positive number for debits/expenses, empty string if credit. e.g., 123.45, ``)
1.1.5. ReceiptData Schema (Add-on feature)
 * Purpose: To capture key fields from receipts for expense tracking.
 * Fields:
   * receipt_id: str (UUID)
   * vendor_name: str
   * transaction_date: date
   * total_amount: float
   * currency: str (e.g., "USD")
   * line_items: List[Dict[str, Any]] (e.g., [{"item": "Coffee", "price": 4.50}, {"item": "Pastry", "price": 3.00}])
   * category_suggestion: Optional[str] (e.g., "Meals & Entertainment")
   * image_path: str (Path to the stored receipt image)
   * ocr_raw_text: str (Full OCR output for debugging/audit)
1.2. Core Module & Agent Definitions
Each module will encapsulate specific functionality and can be considered a "micro-agent" or a tool for a higher-level orchestration agent.
1.2.1. FileIngestionService (Module)
 * Responsibility: Handles file uploads, validation, and dispatches to appropriate parsing agents.
 * Methods:
   * upload_file(file_data: bytes, file_name: str) -> str: Stores file, returns unique ID.
   * validate_file_type(file_name: str) -> Literal["CSV", "PDF", "DOCX", "JPEG", "PNG", "UNSUPPORTED"]: Determines file type.
   * dispatch_to_parser(file_id: str, file_type: str) -> List[RawTransactionData]: Routes files to relevant raw data extraction agents.
1.2.2. RawDataExtractionAgent (Orchestration Agent)
 * Responsibility: Orchestrates specific parsing tools based on file type to get RawTransactionData.
 * Internal Tools/Sub-Agents:
   * CSVParserTool:
     * Input: Raw CSV content.
     * Output: List of RawTransactionData (each row/relevant cell).
     * Logic: Basic row/column parsing.
   * PDFExtractorTool:
     * Input: PDF file content.
     * Output: List of RawTransactionData (text blocks, table data).
     * Logic: Uses a library like pdfplumber or PyPDF2 for text/table extraction. For image-based PDFs, will route to OCRTool.
   * DOCXExtractorTool:
     * Input: DOCX file content.
     * Output: List of RawTransactionData (text blocks).
     * Logic: Uses python-docx for text extraction.
   * OCRTool:
     * Input: Image bytes (JPEG, PNG, or image from PDF).
     * Output: List of RawTransactionData (text lines/words with bounding boxes).
     * Logic: Utilizes Tesseract (via pytesseract) or a cloud OCR service (e.g., Google Cloud Vision API for higher accuracy on diverse layouts, if budget allows for API calls). Explicitly choose one or provide a clear configuration for both.
1.2.3. TransactionInterpretationAgent (Orchestration Agent)
 * Responsibility: Takes RawTransactionData and transforms it into ExtractedTransaction and then NormalizedTransaction. This is where the core AI intelligence resides.
 * Internal Tools/Sub-Agents:
   * DateParsingTool:
     * Input: potential_date_str from ExtractedTransaction.
     * Output: date object.
     * Logic: Robust date parsing (e.g., dateutil.parser), handling multiple formats (MM/DD/YYYY, DD-MM-YY, etc.).
   * AmountParsingTool:
     * Input: potential_amount_str, potential_credit_str, potential_debit_str.
     * Output: amount: float, transaction_type: Literal["Credit", "Debit"].
     * Logic: Regex for currency extraction, handling commas/periods, identifying debit/credit based on column presence, negative signs, or keywords.
   * DescriptionCleaningTool:
     * Input: potential_description_str.
     * Output: Cleaned description: str.
     * Logic: Remove common bank statement artifacts (e.g., "POS TRANSACTIONS", "DEBIT CARD PURCHASE"), normalize common vendor names if a lookup dictionary is available.
   * CategorizationSuggesterTool (Optional, Advanced AI):
     * Input: description, amount.
     * Output: category_suggestion: Optional[str].
     * Logic: Could use a pre-trained text classification model (e.g., simple Naive Bayes, or fine-tuned BERT/DistilBERT if data is sufficient) on known transaction categories. Initial version can omit this, but the schema allows for it.
1.2.4. QuickBooksFormatterAgent (Orchestration Agent)
 * Responsibility: Takes NormalizedTransaction data and generates the QuickBooks-compatible CSV.
 * Internal Tools/Sub-Agents:
   * CSVGenerationTool:
     * Input: List of NormalizedTransaction, csv_format_preference: Literal["3-column", "4-column"], date_format_preference: str.
     * Output: CSV file content (string).
     * Logic: Maps NormalizedTransaction fields to QuickBooksCSVRow based on chosen format, applies date formatting, handles credit/debit column logic, ensures no header/footer.
1.2.5. ReceiptProcessingAgent (Add-on, Orchestration Agent)
 * Responsibility: Processes receipt images into structured ReceiptData.
 * Internal Tools/Sub-Agents:
   * ReceiptOCRTool: (Specialized OCRTool if needed for receipts, or re-use general OCRTool with specific post-processing).
   * ReceiptKeyInformationExtractorTool:
     * Input: Raw OCR text from receipt.
     * Output: Initial ReceiptData fields.
     * Logic: Uses advanced NLP techniques (e.g., Named Entity Recognition fine-tuned for receipt data) or prompt engineering with a strong LLM to identify vendor, date, total, etc.
   * ExpenseCategorizationTool: (Similar to CategorizationSuggesterTool but for expenses).
1.3. Service-Level Design & API Endpoints
The user will interact with the app via a simple web interface.
 * POST /upload_statement
   * Input: file (multipart/form-data), quickbooks_csv_format (e.g., "3-column", "4-column"), date_format (e.g., "MM/DD/YYYY", "DD/MM/YYYY")
   * Output (JSON):
     * job_id: str (UUID to track processing)
     * status: str (e.g., "Processing", "Failed", "Completed")
     * message: str
 * GET /status/{job_id}
   * Input: job_id: str
   * Output (JSON):
     * job_id: str
     * status: str
     * progress: float (0.0 to 1.0)
     * download_url: Optional[str] (If completed)
     * errors: List[str] (If failed or partially failed)
     * preview_data: Optional[List[NormalizedTransaction]] (First few rows for review)
 * GET /download/{job_id}
   * Input: job_id: str
   * Output: CSV file content (application/csv)
 * POST /upload_receipt (Add-on)
   * Input: file (multipart/form-data)
   * Output (JSON):
     * receipt_id: str
     * status: str
     * extracted_data: ReceiptData (for immediate display/review)
     * errors: List[str]
1.4. Database & Storage Considerations
 * Temporary File Storage: For uploaded files and generated CSVs (e.g., a local temp/ directory, or cloud storage like S3 for scalability). Files should be cleaned up after a certain period or download.
 * Job Status Database: A lightweight database (e.g., SQLite for simplicity, PostgreSQL for scalability) to store job_id, status, errors, and the path to the generated CSV.
 * No long-term user data storage. The philosophy is to process and provide the file for download, then remove source data.
Phase 2: Explicit Development & Agent Implementation (No Stubs!)
This phase translates the design into executable code, leveraging Copilot extensively.
2.1. Project Structure (Python)
/afsp_app
├── /app
│   ├── __init__.py
│   ├── main.py                    # FastAPI/Flask entry point, API routes
│   ├── schemas.py                 # Pydantic models for all data schemas
│   ├── config.py                  # Configuration settings (paths, API keys)
│   ├── /services
│   │   ├── file_ingestion_service.py # Implements FileIngestionService logic
│   ├── /agents
│   │   ├── __init__.py
│   │   ├── raw_data_extraction_agent.py # Orchestrates extraction tools
│   │   ├── transaction_interpretation_agent.py # Orchestrates interpretation tools
│   │   ├── quickbooks_formatter_agent.py # Orchestrates CSV generation
│   │   ├── receipt_processing_agent.py # Add-on agent
│   ├── /tools                    # Specific, atomic functionalities for agents
│   │   ├── __init__.py
│   │   ├── csv_parser.py
│   │   ├── pdf_extractor.py
│   │   ├── docx_extractor.py
│   │   ├── ocr_tool.py             # General OCR
│   │   ├── date_parser.py
│   │   ├── amount_parser.py
│   │   ├── description_cleaner.py
│   │   ├── csv_generator.py
│   │   ├── receipt_key_extractor.py # Receipt-specific extraction
│   │   └── categorization_suggester.py # Optional
├── /tests
│   ├── test_schemas.py
│   ├── test_file_ingestion.py
│   ├── test_raw_data_extraction.py
│   ├── test_transaction_interpretation.py
│   ├── test_quickbooks_formatter.py
│   ├── test_receipt_processing.py
├── /data                        # For sample training/testing data
│   ├── /bank_statements
│   ├── /receipts
│   ├── /annotated
├── requirements.txt
├── Dockerfile
├── README.md

2.2. Implementation Steps (Sequential, Explicit)
Step 2.2.1: Define Schemas (in app/schemas.py)
 * Action: Write all Pydantic models for RawTransactionData, ExtractedTransaction, NormalizedTransaction, QuickBooksCSVRow, ReceiptData.
 * Copilot Prompt Example: "Create a Pydantic model for RawTransactionData with fields: raw_text (str), source_file_name (str), source_file_type (Literal of 'CSV', 'PDF', 'DOCX', 'JPEG', 'PNG'), optional page_number (int), optional line_number (int), optional bounding_box (Tuple[float, float, float, float]), and timestamp_extracted (datetime)." 
 * Verification: Ensure all fields match the schema definitions exactly.
Step 2.2.2: Implement Core Tools (in app/tools/)
 * Focus: Each tool is a standalone function or class method that performs one specific, well-defined task with clear inputs and outputs as defined in the schemas.
 * Example: app/tools/date_parser.py
   from datetime import date
from typing import Optional
from dateutil.parser import parse, ParserError

def parse_date_robustly(date_str: str) -> Optional[date]:
    """
    Parses a date string into a datetime.date object.
    Handles various common date formats.
    Returns None if parsing fails.
    """
    try:
        # Attempt to parse with dayfirst=False (MM/DD/YYYY) then dayfirst=True (DD/MM/YYYY)
        # This order can be refined based on common input.
        parsed_date = parse(date_str, dayfirst=False)
        return parsed_date.date()
    except ParserError:
        try:
            parsed_date = parse(date_str, dayfirst=True)
            return parsed_date.date()
        except ParserError:
            # Log the parsing failure explicitly
            print(f"ERROR: Could not parse date string: '{date_str}'")
            return None

# Example usage (for testing, will be called by agents)
# print(parse_date_robustly("07/26/2025"))
# print(parse_date_robustly("26-07-2025"))

 * Copilot Prompt Example (ocr_tool.py): "Write a Python function perform_ocr(image_bytes: bytes) -> strthat usespytesseractto extract text from an image. Include error handling forTesseractNotFoundError and return an empty string on failure, logging the error."
 * Copilot Prompt Example (csv_generator.py): "Create a Python function generate_quickbooks_csv(transactions: List[NormalizedTransaction], format_type: Literal['3-column', '4-column'], date_format_str: str) -> strthat generates a CSV string. Handle the specific logic for 3-column (Amount as signed float) and 4-column (Credit/Debit separate, positive) formats, ensuring the header row is correct and no extra rows are present. Use thecsv module for proper CSV handling."
 * Verification: Unit tests for each tool (in tests/). Each tool should be independently testable and cover edge cases (invalid inputs, missing data, etc.).
Step 2.2.3: Implement Services (in app/services/)
 * Example: app/services/file_ingestion_service.py
   import os
from typing import Literal, List
from pathlib import Path
import uuid
from app.schemas import RawTransactionData
from app.tools.csv_parser import parse_csv_to_raw_data # Assume this exists
from app.tools.pdf_extractor import extract_pdf_to_raw_data # Assume this exists
from app.tools.docx_extractor import extract_docx_to_raw_data # Assume this exists
from app.tools.ocr_tool import perform_ocr # Assume this exists
from datetime import datetime

class FileIngestionService:
    def __init__(self, upload_dir: str = "temp_uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _save_file(self, file_data: bytes, file_name: str) -> Path:
        """Saves the uploaded file to a temporary directory."""
        file_extension = Path(file_name).suffix
        unique_id = str(uuid.uuid4())
        saved_path = self.upload_dir / f"{unique_id}{file_extension}"
        with open(saved_path, "wb") as f:
            f.write(file_data)
        return saved_path

    def validate_file_type(self, file_name: str) -> Literal["CSV", "PDF", "DOCX", "JPEG", "PNG", "UNSUPPORTED"]:
        """Determines the file type based on extension."""
        extension = Path(file_name).suffix.lower()
        if extension == ".csv": return "CSV"
        elif extension == ".pdf": return "PDF"
        elif extension in [".doc", ".docx"]: return "DOCX" # Handle .doc via conversion or specific library if needed
        elif extension in [".jpeg", ".jpg", ".png"]: return "JPEG" # Group images
        return "UNSUPPORTED"

    def ingest_and_extract_raw(self, file_data: bytes, file_name: str) -> List[RawTransactionData]:
        """
        Ingests a file, saves it, determines its type, and dispatches to the correct
        raw data extraction tool.
        """
        file_path = self._save_file(file_data, file_name)
        file_type = self.validate_file_type(file_name)

        raw_data_list: List[RawTransactionData] = []

        # This is where the service calls the 'tools' directly.
        # For more complex orchestration, an agent would be here.
        if file_type == "CSV":
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            raw_data_list = parse_csv_to_raw_data(csv_content, file_name)
        elif file_type == "PDF":
            # Check if PDF is image-based or text-based. This might require
            # a more advanced check within pdf_extractor or a pre-check with OCR.
            # For simplicity here, let's assume pdf_extractor handles both or
            # routes to OCR internally if it finds no text.
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            raw_data_list = extract_pdf_to_raw_data(pdf_bytes, file_name)
        elif file_type == "DOCX":
            with open(file_path, 'rb') as f:
                docx_bytes = f.read()
            raw_data_list = extract_docx_to_raw_data(docx_bytes, file_name)
        elif file_type == "JPEG":
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
            # OCR for image files directly
            ocr_text = perform_ocr(image_bytes)
            raw_data_list.append(RawTransactionData(
                raw_text=ocr_text,
                source_file_name=file_name,
                source_file_type="JPEG",
                timestamp_extracted=datetime.now()
            ))
        else:
            raise ValueError(f"Unsupported file type: {file_type} for file {file_name}")

        # Optionally clean up the temporary file after processing
        # os.remove(file_path) # Be careful with this, might need for debugging

        return raw_data_list


 * Copilot Prompt Example: "Develop a FileIngestionServiceclass with methods_save_file, validate_file_type, and ingest_and_extract_raw. The ingest_and_extract_rawmethod should takefile_dataandfile_name, save the file, call validate_file_type, and then dispatch to appropriate parsing tools (e.g., parse_csv_to_raw_data, extract_pdf_to_raw_data, perform_ocr) based on the file type. Ensure it returns a List[RawTransactionData]."
 * Verification: Unit tests for each service. Test file saving, type validation, and correct dispatching.
Step 2.2.4: Implement Orchestration Agents (in app/agents/)
 * Focus: These classes will coordinate the calls to the individual tools. They don't contain much core logic themselves, but rather manage the flow and error handling between tools.
 * Example: app/agents/transaction_interpretation_agent.py
   from typing import List, Optional
from app.schemas import RawTransactionData, ExtractedTransaction, NormalizedTransaction
from app.tools.date_parser import parse_date_robustly
from app.tools.amount_parser import parse_amount_and_type
from app.tools.description_cleaner import clean_description
from datetime import datetime
import uuid

class TransactionInterpretationAgent:
    def process_raw_transactions(self, raw_data_list: List[RawTransactionData]) -> List[NormalizedTransaction]:
        """
        Orchestrates the extraction and interpretation of raw transaction data.
        """
        extracted_transactions: List[ExtractedTransaction] = []
        normalized_transactions: List[NormalizedTransaction] = []

        # Step 1: Initial Extraction (this might be partially done by RawDataExtractionAgent,
        # but this agent refines it.)
        for raw_data in raw_data_list:
            # This is a simplified example. In a real scenario, you'd use
            # more advanced methods (e.g., LLM prompts, regex, rule-based)
            # to intelligently pull out potential_date_str, etc., from raw_data.raw_text

            # For Copilot, you'd prompt:
            # "From raw_data.raw_text, extract a potential date string, description string,
            # and amount string. Consider common bank statement patterns."

            # Placeholder for complex extraction logic that would live in a specialized tool
            potential_date = self._find_potential_date(raw_data.raw_text)
            potential_desc = self._find_potential_description(raw_data.raw_text)
            potential_amt = self._find_potential_amount(raw_data.raw_text)
            potential_credit = self._find_potential_credit(raw_data.raw_text)
            potential_debit = self._find_potential_debit(raw_data.raw_text)

            extracted_transactions.append(ExtractedTransaction(
                unique_id=str(uuid.uuid4()),
                raw_text_reference=raw_data.raw_text,
                potential_date_str=potential_date,
                potential_description_str=potential_desc,
                potential_amount_str=potential_amt,
                potential_credit_str=potential_credit,
                potential_debit_str=potential_debit,
                confidence_score={"date": 0.0, "description": 0.0, "amount": 0.0}, # Placeholder, would be actual scores
                extraction_errors=[]
            ))

        # Step 2: Normalize and Validate
        for ext_tx in extracted_transactions:
            parsed_date = parse_date_robustly(ext_tx.potential_date_str) if ext_tx.potential_date_str else None
            amount_val, tx_type = parse_amount_and_type(
                ext_tx.potential_amount_str, 
                ext_tx.potential_credit_str, 
                ext_tx.potential_debit_str
            )
            cleaned_desc = clean_description(ext_tx.potential_description_str) if ext_tx.potential_description_str else "No Description"

            if parsed_date and amount_val is not None and cleaned_desc:
                normalized_transactions.append(NormalizedTransaction(
                    transaction_id=ext_tx.unique_id,
                    date=parsed_date,
                    description=cleaned_desc,
                    amount=amount_val,
                    transaction_type=tx_type,
                    original_source_file=ext_tx.source_file_name, # Assuming this is passed or accessible
                    processing_notes=[]
                ))
            else:
                # Log errors for transactions that couldn't be fully normalized
                ext_tx.extraction_errors.append("Failed to fully normalize transaction.")
                print(f"WARNING: Skipping transaction due to parsing errors: {ext_tx.raw_text_reference}")

        return normalized_transactions

    # --- Helper methods for initial extraction (could be separate tools or part of this agent's logic) ---
    def _find_potential_date(self, text: str) -> Optional[str]:
        # This would use regex or a small LLM call for robust date finding
        import re
        match = re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text)
        return match.group(0) if match else None

    def _find_potential_description(self, text: str) -> Optional[str]:
        # More complex logic, possibly rule-based or LLM summarization
        lines = text.split('\n')
        if len(lines) > 1:
            return lines[1].strip() # Example: second line as description
        return text.strip()

    def _find_potential_amount(self, text: str) -> Optional[str]:
        # Regex for common currency formats. Will need refinement.
        import re
        match = re.search(r'[\$£€]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)', text)
        return match.group(1) if match else None

    def _find_potential_credit(self, text: str) -> Optional[str]:
        # Look for patterns indicating credit column, or positive amount with "CR"
        import re
        match = re.search(r'\b(?:CR|CREDIT)\s*([\d,\.]+\.\d{2})', text, re.IGNORECASE)
        return match.group(1) if match else None

    def _find_potential_debit(self, text: str) -> Optional[str]:
        # Look for patterns indicating debit column, or negative amount with "DB"
        import re
        match = re.search(r'\b(?:DB|DEBIT)\s*([\d,\.]+\.\d{2})', text, re.IGNORECASE)
        return match.group(1) if match else None


 * Copilot Prompt Example: "Create a class TransactionInterpretationAgentwith a methodprocess_raw_transactions(raw_data_list: List[RawTransactionData]) -> List[NormalizedTransaction]. This method should iterate through raw_data_list, call parse_date_robustly, parse_amount_and_type, and clean_descriptionfrom theapp.toolsmodule. It should constructExtractedTransactionandNormalizedTransactionobjects, including error handling and UUID generation fortransaction_id. Include placeholder find_potential*methods that use simple regex for initial extraction fromraw_text for date, description, amount, credit, and debit."
 * Verification: Integration tests for agents, ensuring they correctly use tools and pass data between steps, transforming input schemas to output schemas. Test with diverse RawTransactionData representing various file types.
Step 2.2.5: Implement the Main Application Logic (app/main.py)
 * Framework: Use FastAPI for its speed, automatic Pydantic schema validation, and Swagger UI for easy API testing.
 * Action: Define API endpoints (/upload_statement, /status/{job_id}, /download/{job_id}).
 * Orchestration: This file will instantiate the main agents and services and manage the overall flow. Asynchronous processing (asyncio) is crucial for handling file uploads and long-running AI tasks without blocking the API. Use a simple in-memory dictionary or a lightweight database for job status tracking.
   # app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import os
import asyncio
from pathlib import Path
from datetime import datetime

from app.schemas import NormalizedTransaction, QuickBooksCSVRow # Import schemas
from app.services.file_ingestion_service import FileIngestionService
from app.agents.transaction_interpretation_agent import TransactionInterpretationAgent
from app.agents.quickbooks_formatter_agent import QuickBooksFormatterAgent

app = FastAPI(
    title="Automated Financial Statement Processor (AFSP)",
    description="Convert bank statements and receipts into QuickBooks-ready CSVs using AI.",
    version="1.0.0"
)

# Global instances of services and agents
UPLOAD_DIR = "temp_uploads"
DOWNLOAD_DIR = "temp_downloads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

file_ingestion_service = FileIngestionService(upload_dir=UPLOAD_DIR)
transaction_interpretation_agent = TransactionInterpretationAgent()
quickbooks_formatter_agent = QuickBooksFormatterAgent()

# Simple in-memory job store for demonstration. In production, use a database.
job_status_db: Dict[str, Dict] = {}

class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    download_url: Optional[str]
    errors: List[str]
    preview_data: Optional[List[NormalizedTransaction]]

@app.post("/upload_statement", response_model=UploadResponse, summary="Upload a bank statement for processing")
async def upload_statement(
    file: UploadFile = File(...),
    quickbooks_csv_format: Literal["3-column", "4-column"] = Form("3-column"),
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = Form("MM/DD/YYYY")
):
    job_id = str(uuid.uuid4())
    job_status_db[job_id] = {
        "status": "QUEUED",
        "progress": 0.0,
        "download_url": None,
        "errors": [],
        "preview_data": []
    }

    # Read file content asynchronously
    file_bytes = await file.read()
    file_name = file.filename

    # Run the processing in a background task to not block the API response
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
    try:
        job_status_db[job_id]["status"] = "PROCESSING_INGESTION"
        job_status_db[job_id]["progress"] = 0.1

        # 1. Ingest and Extract Raw Data
        raw_transactions = file_ingestion_service.ingest_and_extract_raw(file_bytes, file_name)
        if not raw_transactions:
            raise ValueError("No raw transactions extracted from file.")

        job_status_db[job_id]["status"] = "PROCESSING_INTERPRETATION"
        job_status_db[job_id]["progress"] = 0.4

        # 2. Interpret and Normalize Transactions
        normalized_transactions = transaction_interpretation_agent.process_raw_transactions(raw_transactions)
        if not normalized_transactions:
            raise ValueError("No normalized transactions after interpretation.")

        # Store preview data (first 5 for brevity)
        job_status_db[job_id]["preview_data"] = normalized_transactions[:5]

        job_status_db[job_id]["status"] = "PROCESSING_FORMATTING"
        job_status_db[job_id]["progress"] = 0.8

        # 3. Format to QuickBooks CSV
        csv_content = quickbooks_formatter_agent.format_to_quickbooks_csv(
            normalized_transactions, quickbooks_csv_format, date_format
        )

        output_file_name = f"quickbooks_export_{Path(file_name).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output_file_path = Path(DOWNLOAD_DIR) / output_file_name
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(csv_content)

        job_status_db[job_id]["status"] = "COMPLETED"
        job_status_db[job_id]["progress"] = 1.0
        job_status_db[job_id]["download_url"] = f"/download/{job_id}"

    except Exception as e:
        job_status_db[job_id]["status"] = "FAILED"
        job_status_db[job_id]["errors"].append(str(e))
        job_status_db[job_id]["progress"] = 1.0
        print(f"Job {job_id} failed: {e}")

@app.get("/status/{job_id}", response_model=StatusResponse, summary="Get the processing status of a job")
async def get_status(job_id: str):
    status_info = job_status_db.get(job_id)
    if not status_info:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    return StatusResponse(**status_info)

@app.get("/download/{job_id}", summary="Download the processed QuickBooks CSV file")
async def download_file(job_id: str):
    status_info = job_status_db.get(job_id)
    if not status_info or status_info["status"] != "COMPLETED" or not status_info["download_url"]:
        raise HTTPException(status_code=404, detail="File not ready for download or job not found.")

    file_path = Path(DOWNLOAD_DIR) / Path(status_info["download_url"]).name # Extract filename from URL
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server. It might have been deleted.")

    return FileResponse(path=file_path, filename=Path(status_info["download_url"]).name, media_type="text/csv")

# Add-on: Receipt Processing (similar structure)
# @app.post("/upload_receipt", response_model=...)
# async def upload_receipt(...):
#    ...


 * Copilot Prompt Example: "Create a FastAPI application in main.py. Define /upload_statementendpoint that accepts aFileupload,quickbooks_csv_format(Form, Literal '3-column'/'4-column'), anddate_format(Form, Literal 'MM/DD/YYYY'/'DD/MM/YYYY'). It should create a uniquejob_id, store initial status in job_status_db, and then run _process_statement_backgroundas anasyncio.create_task. Also define /status/{job_id}to retrieve job status and/download/{job_id}to serve the completed CSV file. Implement the_process_statement_backgroundfunction to sequentially callfile_ingestion_service.ingest_and_extract_raw, transaction_interpretation_agent.process_raw_transactions, and quickbooks_formatter_agent.format_to_quickbooks_csv, updating job_status_dbat each stage with progress and error handling. Store output CSV intemp_downloads."
 * Verification: Manual testing with Postman/cURL or FastAPI's integrated Swagger UI. Ensure full pipeline execution, correct status updates, and downloadable files.
Step 2.2.6: Dockerization
 * Action: Create a Dockerfile to containerize the application for consistent deployment.
 * Copilot Prompt Example: "Generate a Dockerfile for a Python FastAPI application. It should install dependencies from requirements.txt, expose port 8000, and use Gunicorn or Uvicorn to run app.main:app."
 * Verification: Build and run the Docker image locally.
Step 2.2.7: GitHub Actions for CI/CD (Optional but Recommended for Flawless)
 * Action: Set up a simple workflow to run tests on push and/or build the Docker image.
 * Copilot Prompt Example: "Create a GitHub Actions workflow YAML for a Python project. On push to main, it should install dependencies, run pytest, and then build a Docker image named 'afsp-app'."
 * Verification: Push code to GitHub and observe workflow execution.
Phase 3: Testing & Refinement (The "Flawless" Touch)
Since we are avoiding stubs and TODOs, testing is integrated throughout development.
3.1. Comprehensive Unit Tests (/tests/)
 * Every tool and service method must have dedicated unit tests.
 * Focus: Input-output validation, edge cases, error conditions (e.g., malformed dates, non-numeric amounts, empty files).
 * Testing Data: Use a diverse set of real (anonymized) bank statements and receipts in data/ for robust testing of the extraction and interpretation agents.
3.2. Integration Tests
 * Test the flow between agents (e.g., FileIngestionService -> RawDataExtractionAgent -> TransactionInterpretationAgent).
 * Focus: Data contract adherence between modules.
3.3. End-to-End Tests
 * Simulate a full user interaction (upload, check status, download).
 * Focus: Overall application correctness, API responsiveness, file generation.
3.4. Manual Testing & User Feedback Loop (Crucial for AI)
Even with Copilot, AI for data extraction is iterative.
 * Action: Design a simple feedback mechanism within the (minimal) UI for users to correct extracted data. This corrected data becomes valuable new training examples.
 * Goal: Continuously improve the accuracy of the TransactionInterpretationAgent's tools (especially DateParsingTool, AmountParsingTool, DescriptionCleaningTool, and potentially CategorizationSuggesterTool) by feeding back user corrections. This is where a small, internal "training loop" would be defined for periodic model updates.
This detailed guide, combined with strategic Copilot prompting, should allow for a highly explicit and "stub-free" development process. Remember to break down each step into very specific, small prompts for Copilot, guiding it towards the exact code you need based on the defined schemas and responsibilities. Good luck – this app will be a lifesaver!
