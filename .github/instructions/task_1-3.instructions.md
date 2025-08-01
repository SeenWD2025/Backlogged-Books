AI-Powered Bookkeeping Reconciliation App: The Genius Developer's Playbook
Core Principle for Copilot Interaction:
 * Atomic Prompts: Each prompt focuses on one distinct function, class, or logical block.
 * Schema-First: Always reference the pre-defined schemas explicitly in prompts.
 * Contextual Clarity: Provide necessary context within the prompt (e.g., "based on the NormalizedTransaction schema...").
 * Error Prevention: Include explicit instructions for error handling, logging, and edge cases.
 * No Implicit Logic: If a piece of logic is needed, describe it in the prompt, don't expect Copilot to infer it.
Compartment 1: Project Setup & Schema Foundation
Objective: Establish the project directory structure, create the requirements.txt with all necessary libraries, and define all data schemas (app/schemas.py) using Pydantic. This forms the bedrock upon which all other components will be built.
Developer Genius Note: Starting with schemas is paramount. They act as the "API contracts" between our future modules, ensuring data consistency and preventing integration headaches later. Pydantic enforces this strongly.
Task 1.1: Initialize Project & Define Dependencies
Goal: Create the project root, the app directory, and the initial requirements.txt.
Steps:
 * Create Project Root Directory: afsp_app
 * Create app Directory: Inside afsp_app.
 * Create requirements.txt: Add core dependencies.
 * Create app/__init__.py: An empty file to mark app as a Python package.
Copilot Prompts (Execute in VS Code, targeting the specific files):
 * Prompt for requirements.txt (within afsp_app/requirements.txt):
   # requirements.txt
# Please add the following core Python libraries, one per line:
# - FastAPI (web framework)
# - Uvicorn (ASGI server for FastAPI)
# - Pydantic (data validation and settings management)
# - python-dateutil (robust date parsing)
# - pytesseract (Python wrapper for Tesseract OCR)
# - opencv-python (for image processing, required by some OCR pre-processing)
# - PyPDF2 (for basic PDF text extraction)
# - python-docx (for DOCX file parsing)
# - python-multipart (for file uploads in FastAPI)
# - python-dotenv (for environment variables)
# - pandas (for data manipulation, especially with CSVs)

 * Prompt for directory creation (Conceptual, as this is manual):
   * mkdir afsp_app
   * cd afsp_app
   * mkdir app
   * touch app/__init__.py
Task 1.2: Define Data Schemas
Goal: Implement all Pydantic models in app/schemas.py precisely as outlined in the high-level design.
Developer Genius Note: Be extremely pedantic about types (Optional, List, Literal, exact datetime/date objects). This is where Copilot shines if given clear instructions, but can hallucinate if left to infer.
Steps:
 * Create app/schemas.py.
 * Add necessary imports (Pydantic, datetime, date, Optional, List, Literal, Tuple).
 * Define each schema sequentially with precise field names and types.
Copilot Prompts (Execute inside app/schemas.py):
 * Initial Imports Prompt:
   # app/schemas.py
# Add necessary imports:
# - BaseModel from pydantic
# - datetime, date from datetime
# - Optional, List, Literal, Tuple from typing

 * RawTransactionData Schema Prompt:
   # Define the Pydantic model `RawTransactionData`.
# It should represent the initial unstructured data extracted from source documents.
# Fields:
# - `raw_text`: str (entire block of text/OCR output)
# - `source_file_name`: str (original file name)
# - `source_file_type`: Literal["CSV", "PDF", "DOCX", "JPEG", "PNG"] (exact file type)
# - `page_number`: Optional[int] (for multi-page docs)
# - `line_number`: Optional[int] (approximate for text-based extraction)
# - `bounding_box`: Optional[Tuple[float, float, float, float]] (x_min, y_min, x_max, y_max for image-based)
# - `timestamp_extracted`: datetime (when this data was extracted)

 * ExtractedTransaction Schema Prompt:
   # Define the Pydantic model `ExtractedTransaction`.
# This holds initially identified but not yet fully normalized transaction fields.
# Fields:
# - `unique_id`: str (UUID for tracking this specific extraction attempt)
# - `raw_text_reference`: str (reference back to the raw text block)
# - `potential_date_str`: Optional[str] (raw string of the date)
# - `potential_description_str`: Optional[str] (raw string of the description)
# - `potential_amount_str`: Optional[str] (raw string of the amount, can be signed)
# - `potential_credit_str`: Optional[str] (raw string of credit amount, if separate)
# - `potential_debit_str`: Optional[str] (raw string of debit amount, if separate)
# - `confidence_score`: Dict[str, float] (dictionary mapping field name to confidence 0.0-1.0)
# - `extraction_errors`: List[str] (list of any errors during this extraction phase)

 * NormalizedTransaction Schema Prompt:
   # Define the Pydantic model `NormalizedTransaction`.
# This represents clean, validated, and categorized financial transaction data, ready for final formatting.
# Fields:
# - `transaction_id`: str (UUID, carried over or newly generated)
# - `date`: date (Python date object, YYYY-MM-DD strictly)
# - `description`: str (cleaned, consolidated description)
# - `amount`: float (single float, positive for income/credit, negative for expense/debit)
# - `transaction_type`: Literal["Credit", "Debit"] (explicitly categorized)
# - `original_source_file`: str (name of the file it came from)
# - `processing_notes`: List[str] (any notes about corrections or specific processing)

 * QuickBooksCSVRow Schema Prompts (Conceptual for Copilot - as it's for CSV generation, not a Pydantic model for internal use, but useful for clarity):
   * Developer Genius Note: We won't make this a Pydantic model in schemas.py because it's purely for the output CSV format, not an internal data object. But knowing its structure is key. Copilot will be prompted to generate code that produces this structure.
   * 3-Column Format Details for Copilot: Date: str (MM/DD/YYYY or DD/MM/YYYY), Description: str, Amount: str (e.g., "-123.45", "78.90")
   * 4-Column Format Details for Copilot: Date: str (MM/DD/YYYY or DD/MM/YYYY), Description: str, Credit: str (positive or empty), Debit: str (positive or empty)
 * ReceiptData Schema Prompt:
   # Define the Pydantic model `ReceiptData` for the add-on feature.
# Fields:
# - `receipt_id`: str (UUID for the receipt)
# - `vendor_name`: str
# - `transaction_date`: date
# - `total_amount`: float
# - `currency`: str (e.g., "USD")
# - `line_items`: List[Dict[str, Any]] (list of dictionaries for item, price, etc.)
# - `category_suggestion`: Optional[str] (e.g., "Meals & Entertainment")
# - `image_path`: str (path to the stored receipt image)
# - `ocr_raw_text`: str (full OCR output for auditing/debugging)

Compartment 2: Core Tools Implementation
Objective: Develop the atomic, single-responsibility functions/classes (tools) that the AI agents will utilize. Each tool should be independently testable.
Developer Genius Note: These are the building blocks. Each one must be robust and handle its specific task flawlessly. We're explicitly telling Copilot what library to use where relevant to prevent it from inventing its own solutions.
Task 2.1: Implement CSV Parser Tool
Goal: Create app/tools/csv_parser.py to extract RawTransactionData from CSV content.
Steps:
 * Create app/tools/csv_parser.py.
 * Implement parse_csv_to_raw_data function.
Copilot Prompt (Execute inside app/tools/csv_parser.py):
# app/tools/csv_parser.py
# Import necessary types and schemas: List, RawTransactionData, datetime, uuid
import csv
from io import StringIO
from typing import List
from datetime import datetime
import uuid
from app.schemas import RawTransactionData

# Define a function `parse_csv_to_raw_data`.
# It takes `csv_content: str` (the full CSV file content as a string) and `source_file_name: str`.
# It should return a `List[RawTransactionData]`.
# Logic:
# - Use `csv.reader` to parse the `csv_content`.
# - For each row, treat the entire row as `raw_text`.
# - Generate a unique `uuid` for each entry (or use row index if simpler, but UUID is better for tracing).
# - Set `source_file_type` to "CSV".
# - Set `timestamp_extracted` to `datetime.now()`.
# - No need for `page_number`, `line_number`, `bounding_box` for CSVs. Set them to None.
# - Include basic error handling for `csv.Error`. If a row causes an error, skip it and log a warning.
# - Provide clear docstrings.

Task 2.2: Implement PDF Extractor Tool
Goal: Create app/tools/pdf_extractor.py to extract text from PDF files.
Steps:
 * Create app/tools/pdf_extractor.py.
 * Implement extract_pdf_to_raw_data function.
Copilot Prompt (Execute inside app/tools/pdf_extractor.py):
# app/tools/pdf_extractor.py
# Import necessary types and schemas: List, RawTransactionData, datetime
import PyPDF2
from typing import List
from datetime import datetime
import uuid
from app.schemas import RawTransactionData

# Define a function `extract_pdf_to_raw_data`.
# It takes `pdf_bytes: bytes` (the raw bytes of the PDF file) and `source_file_name: str`.
# It should return a `List[RawTransactionData]`.
# Logic:
# - Use `PyPDF2.PdfReader` to read the PDF bytes.
# - Iterate through each page of the PDF.
# - For each page, extract text using `page.extract_text()`.
# - Create a `RawTransactionData` object for each page's extracted text.
# - Set `source_file_type` to "PDF".
# - Set `timestamp_extracted` to `datetime.now()`.
# - Set `page_number` for each entry.
# - Handle `PyPDF2.errors.PdfReadError` (e.g., corrupted PDFs) gracefully by logging and returning an empty list or partial data.
# - Add docstrings.

Task 2.3: Implement DOCX Extractor Tool
Goal: Create app/tools/docx_extractor.py to extract text from DOCX files.
Steps:
 * Create app/tools/docx_extractor.py.
 * Implement extract_docx_to_raw_data function.
Copilot Prompt (Execute inside app/tools/docx_extractor.py):
# app/tools/docx_extractor.py
# Import necessary types and schemas: List, RawTransactionData, datetime
from docx import Document
from io import BytesIO
from typing import List
from datetime import datetime
import uuid
from app.schemas import RawTransactionData

# Define a function `extract_docx_to_raw_data`.
# It takes `docx_bytes: bytes` (the raw bytes of the DOCX file) and `source_file_name: str`.
# It should return a `List[RawTransactionData]`.
# Logic:
# - Use `Document(BytesIO(docx_bytes))` to load the DOCX content.
# - Iterate through paragraphs in the document.
# - Concatenate text from all paragraphs into a single `raw_text` string for the document, or create an entry per paragraph/section if deemed more granular. For simplicity, let's aim for one `RawTransactionData` entry per significant text block (e.g., paragraph or entire document).
# - Set `source_file_type` to "DOCX".
# - Set `timestamp_extracted` to `datetime.now()`.
# - Handle potential `docx.opc.exceptions.PackageNotFoundError` or other errors, logging and returning empty list.
# - Add docstrings.

Task 2.4: Implement General OCR Tool
Goal: Create app/tools/ocr_tool.py for image-to-text conversion (JPEG, PNG, image-based PDFs).
Steps:
 * Create app/tools/ocr_tool.py.
 * Implement perform_ocr function.
Developer Genius Note: OCR can be tricky. Explicitly tell Copilot to use pytesseract and consider basic image preprocessing if it's struggling. Mention error handling for TesseractNotFoundError.
Copilot Prompt (Execute inside app/tools/ocr_tool.py):
# app/tools/ocr_tool.py
# Import necessary types: Optional, Tuple, bytes, str
import pytesseract
from PIL import Image
from io import BytesIO
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function `perform_ocr`.
# It takes `image_bytes: bytes` (raw image data) and returns `Optional[str]` (extracted text).
# Logic:
# - Use `PIL.Image.open(BytesIO(image_bytes))` to open the image.
# - Use `pytesseract.image_to_string()` to extract text.
# - Implement robust error handling:
#   - Catch `pytesseract.TesseractNotFoundError`: Log a critical error and return None, indicating Tesseract isn't installed or configured.
#   - Catch generic `Exception`: Log the error and return None.
# - Add docstrings.
# - Optionally, suggest adding basic image pre-processing (e.g., converting to grayscale, enhancing contrast) before OCR if simple `image_to_string` is insufficient, but keep it simple for now.

Task 2.5: Implement Date Parser Tool
Goal: Create app/tools/date_parser.py for robust date string parsing.
Steps:
 * Create app/tools/date_parser.py.
 * Implement parse_date_robustly function.
Developer Genius Note: dateutil.parser is excellent here for its flexibility. Emphasize handling various formats and returning None on failure.
Copilot Prompt (Execute inside app/tools/date_parser.py):
# app/tools/date_parser.py
# Import necessary types: date, Optional
from datetime import date
from dateutil.parser import parse, ParserError
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function `parse_date_robustly`.
# It takes `date_str: str` and returns `Optional[date]` (Python date object).
# Logic:
# - Use `dateutil.parser.parse()` to attempt parsing.
# - Try parsing with `dayfirst=False` (MM/DD/YYYY) first, then `dayfirst=True` (DD/MM/YYYY).
# - Handle `ParserError` if the string cannot be parsed into a date. Log the error and return `None`.
# - Ensure it strictly returns a `datetime.date` object, not `datetime.datetime`.
# - Add docstrings.

Task 2.6: Implement Amount Parser Tool
Goal: Create app/tools/amount_parser.py for extracting numeric amounts and determining transaction type.
Steps:
 * Create app/tools/amount_parser.py.
 * Implement parse_amount_and_type function.
Developer Genius Note: This requires careful regex and logic to handle currency symbols, commas, negative signs, and distinct credit/debit columns. Ensure a single float output.
Copilot Prompt (Execute inside app/tools/amount_parser.py):
# app/tools/amount_parser.py
# Import necessary types: Optional, Tuple, Literal
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function `parse_amount_and_type`.
# It takes:
# - `potential_amount_str: Optional[str]`
# - `potential_credit_str: Optional[str]`
# - `potential_debit_str: Optional[str]`
# It returns a `Tuple[Optional[float], Optional[Literal["Credit", "Debit"]]]`.
# Logic:
# - Prioritize `potential_credit_str` and `potential_debit_str` first.
#   - If `potential_credit_str` has a valid number, convert it to float (positive), type "Credit".
#   - Else if `potential_debit_str` has a valid number, convert it to float (positive), type "Debit".
# - If neither separate credit/debit is found, use `potential_amount_str`.
#   - Use regex to extract numeric value, ignoring currency symbols ($, £, €, etc.) and commas.
#   - Convert the extracted string to a float.
#   - Determine type ("Credit" or "Debit") based on:
#     - Presence of negative sign (-)
#     - Keywords in surrounding text (though this tool focuses on the string itself, agent will provide context)
#   - If no clear sign, default to 'Debit' for expenses unless explicitly 'Credit'. *For this app, most single amounts without +/- are debits*.
# - Handle `ValueError` if string is not a valid number. Log error and return (None, None).
# - Example: "$1,234.56" -> 1234.56; "-50.00" -> -50.00 (and "Debit")
# - Add docstrings.

Task 2.7: Implement Description Cleaner Tool
Goal: Create app/tools/description_cleaner.py to clean and standardize transaction descriptions.
Steps:
 * Create app/tools/description_cleaner.py.
 * Implement clean_description function.
Developer Genius Note: This is often rule-based. Provide examples of common bank statement junk to remove.
Copilot Prompt (Execute inside app/tools/description_cleaner.py):
# app/tools/description_cleaner.py
# Import necessary types: str
import re

# Define a function `clean_description`.
# It takes `description: str` and returns a `str` (cleaned description).
# Logic:
# - Remove common bank statement prefixes/suffixes/artifacts:
#   - "POS TRANSACTION", "DEBIT CARD PURCHASE", "ATM WITHDRAWAL", "ONLINE PAYMENT", "E-TRANSFER"
#   - Trailing transaction IDs or dates if they appear in the description text.
#   - Extra whitespace, leading/trailing spaces.
# - Normalize common variations (e.g., "AMZN" -> "Amazon"). Provide a few examples.
# - Convert to title case or sentence case if desired, but keep it simple for now.
# - Add docstrings.

Task 2.8: Implement CSV Generation Tool
Goal: Create app/tools/csv_generator.py for generating the final QuickBooks CSV content.
Steps:
 * Create app/tools/csv_generator.py.
 * Implement generate_quickbooks_csv function.
Developer Genius Note: Pay close attention to the specific QuickBooks formats (3-column vs. 4-column) and date formatting. Use Python's csv module for proper CSV escaping.
Copilot Prompt (Execute inside app/tools/csv_generator.py):
# app/tools/csv_generator.py
# Import necessary types and schemas: List, Literal, NormalizedTransaction, StringIO, csv
import csv
from io import StringIO
from typing import List, Literal
from app.schemas import NormalizedTransaction
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function `generate_quickbooks_csv`.
# It takes:
# - `transactions: List[NormalizedTransaction]` (list of normalized data)
# - `format_type: Literal["3-column", "4-column"]` (user's choice of CSV format)
# - `date_format_str: str` (e.g., "MM/DD/YYYY", "DD/MM/YYYY")
# It returns `str` (the full CSV content as a string).
# Logic:
# - Initialize `StringIO` to write CSV content to memory.
# - Use `csv.writer`.
# - **For "3-column" format:**
#   - Header: "Date", "Description", "Amount"
#   - For each transaction:
#     - Date: Format `transaction.date` using `strftime(date_format_str)`.
#     - Description: `transaction.description`.
#     - Amount: `transaction.amount`. If it's a credit, ensure it's positive. If it's a debit, ensure it's negative. Convert to string, no currency symbols. e.g., "-123.45" or "78.90".
# - **For "4-column" format:**
#   - Header: "Date", "Description", "Credit", "Debit"
#   - For each transaction:
#     - Date: Format `transaction.date` using `strftime(date_format_str)`.
#     - Description: `transaction.description`.
#     - Credit: If `transaction.transaction_type == "Credit"`, `str(abs(transaction.amount))`. Else, empty string `""`.
#     - Debit: If `transaction.transaction_type == "Debit"`, `str(abs(transaction.amount))`. Else, empty string `""`.
# - Handle any potential `ValueError` during number or date formatting by logging and potentially skipping the row or marking it.
# - Add docstrings.

Compartment 3: Orchestration Agents Implementation
Objective: Build the AI agents (app/agents/) that orchestrate the individual tools, manage the flow of data between schemas, and implement the core AI logic (data extraction, interpretation).
Developer Genius Note: These agents are the "brains." They are designed to call the tools, not to re-implement the tools' logic. This separation is key to maintainability and testability. Prompts here will focus on flow control and data transformation.
Task 3.1: Implement Raw Data Extraction Agent
Goal: Create app/agents/raw_data_extraction_agent.py to intelligently extract raw fields from RawTransactionData into ExtractedTransaction.
Steps:
 * Create app/agents/raw_data_extraction_agent.py.
 * Implement RawDataExtractionAgent class with extract_fields method.
Developer Genius Note: This agent is where the "intelligence" of mapping raw text to structured fields begins. For this initial version, use robust regex as a primary method. If performance isn't sufficient, this is the module to enhance with more advanced NLP models or a small, fine-tuned LLM. Explicitly define what regex patterns to look for.
Copilot Prompt (Execute inside app/agents/raw_data_extraction_agent.py):
# app/agents/raw_data_extraction_agent.py
# Import necessary types and schemas: List, RawTransactionData, ExtractedTransaction, Optional, uuid
import re
from typing import List, Optional
import uuid
from app.schemas import RawTransactionData, ExtractedTransaction
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RawDataExtractionAgent:
    """
    Orchestrates the initial extraction of potential transaction fields
    from raw text data into ExtractedTransaction schema.
    This agent uses rule-based extraction (regex) for robustness.
    """

    def extract_fields(self, raw_data_list: List[RawTransactionData]) -> List[ExtractedTransaction]:
        """
        Processes a list of RawTransactionData to extract potential date, description,
        amount, credit, and debit strings.
        """
        extracted_transactions: List[ExtractedTransaction] = []
        for raw_data in raw_data_list:
            errors = []
            
            # Use defined helper methods for extraction
            potential_date = self._extract_date_str(raw_data.raw_text)
            potential_description = self._extract_description_str(raw_data.raw_text)
            potential_amount = self._extract_amount_str(raw_data.raw_text)
            potential_credit = self._extract_credit_str(raw_data.raw_text)
            potential_debit = self._extract_debit_str(raw_data.raw_text)

            # Basic confidence scoring (can be enhanced with regex match quality)
            confidence = {
                "date": 1.0 if potential_date else 0.0,
                "description": 1.0 if potential_description else 0.0,
                "amount": 1.0 if potential_amount or potential_credit or potential_debit else 0.0
            }

            extracted_transactions.append(ExtractedTransaction(
                unique_id=str(uuid.uuid4()),
                raw_text_reference=raw_data.raw_text, # Store the full raw text for context/debugging
                potential_date_str=potential_date,
                potential_description_str=potential_description,
                potential_amount_str=potential_amount,
                potential_credit_str=potential_credit,
                potential_debit_str=potential_debit,
                confidence_score=confidence,
                extraction_errors=errors
            ))
        return extracted_transactions

    # --- Helper methods for robust regex-based extraction ---

    def _extract_date_str(self, text: str) -> Optional[str]:
        """Extracts a date string using common patterns."""
        # MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD, Month DD, YYYY
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YY or DD-MM-YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b', # Month DD, YYYY
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b', # DD Month YYYY
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_description_str(self, text: str) -> Optional[str]:
        """
        Extracts a potential description string. This is heuristic and may need refinement.
        Often, descriptions are lines between date/amount or specific fields.
        For now, let's try to capture a significant line or a section of text.
        A simple approach: take a line that doesn't look like date/amount.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines:
            # Skip lines that look like pure dates or amounts
            if re.fullmatch(r'[\d,\.]+', line): continue
            if re.fullmatch(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', line): continue
            # If it's not primarily a date or amount, consider it a description
            if len(line) > 5 and not any(re.search(p, line, re.IGNORECASE) for p in [r'\b(?:CR|DB|CREDIT|DEBIT)\b', r'\$\s*\d+']):
                return line
        # Fallback: return the first non-empty line or the entire text if nothing specific found
        return lines[0] if lines else text

    def _extract_amount_str(self, text: str) -> Optional[str]:
        """Extracts a general amount string (e.g., $123.45, -50.00)."""
        # Patterns for amounts, possibly with currency symbols, commas, negative signs
        patterns = [
            r'[\$£€]?\s*(-?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b', # Handles $1,234.56, -50.00
            r'\b(\d{1,3}(?: \d{3})*(?:,\d{2})?)\s*€\b' # Euro style 1 234,56 €
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).replace(',', '') # Remove commas for consistent parsing later
        return None

    def _extract_credit_str(self, text: str) -> Optional[str]:
        """Extracts credit amounts, often followed by CR or in a credit column context."""
        patterns = [
            r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:CR|CREDIT)\b', # Amount followed by CR
            r'(?<=Credit\s*)\s*([\d,\.]+\.\d{2})' # After a "Credit" label
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).replace(',', '')
        return None

    def _extract_debit_str(self, text: str) -> Optional[str]:
        """Extracts debit amounts, often followed by DB or in a debit column context."""
        patterns = [
            r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:DB|DEBIT)\b', # Amount followed by DB
            r'(?<=Debit\s*)\s*([\d,\.]+\.\d{2})' # After a "Debit" label
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).replace(',', '')
        return None

Task 3.2: Implement Transaction Interpretation Agent
Goal: Create app/agents/transaction_interpretation_agent.py to convert ExtractedTransaction into NormalizedTransaction.
Steps:
 * Create app/agents/transaction_interpretation_agent.py.
 * Implement TransactionInterpretationAgent class with process_extracted_transactions method.
Developer Genius Note: This agent is a sequential processor. It applies the robust parsing tools one by one. Crucially, it handles errors during parsing by logging and potentially adding notes to processing_notes, but it must produce a NormalizedTransaction if possible, or omit the transaction if critical data (date/amount) is missing.
Copilot Prompt (Execute inside app/agents/transaction_interpretation_agent.py):
# app/agents/transaction_interpretation_agent.py
# Import necessary types and schemas: List, ExtractedTransaction, NormalizedTransaction, Optional, uuid
# Import specific tools: parse_date_robustly, parse_amount_and_type, clean_description
from typing import List, Optional
import uuid
from datetime import datetime
from app.schemas import ExtractedTransaction, NormalizedTransaction
from app.tools.date_parser import parse_date_robustly
from app.tools.amount_parser import parse_amount_and_type
from app.tools.description_cleaner import clean_description
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TransactionInterpretationAgent:
    """
    Orchestrates the interpretation and normalization of ExtractedTransaction data
    into the consistent NormalizedTransaction schema.
    """

    def process_extracted_transactions(self, extracted_transactions: List[ExtractedTransaction]) -> List[NormalizedTransaction]:
        """
        Takes a list of ExtractedTransaction objects, applies parsing and cleaning tools,
        and returns a list of NormalizedTransaction objects.
        Transactions that cannot be fully normalized due to critical missing data will be skipped.
        """
        normalized_transactions: List[NormalizedTransaction] = []
        for ext_tx in extracted_transactions:
            processing_notes = []
            
            # Use date parsing tool
            parsed_date = parse_date_robustly(ext_tx.potential_date_str) if ext_tx.potential_date_str else None
            if not parsed_date:
                processing_notes.append(f"Date parsing failed for '{ext_tx.potential_date_str}'")
                logging.warning(f"Skipping transaction {ext_tx.unique_id}: Date parsing failed.")
                continue # Skip this transaction if date is critical and missing

            # Use amount parsing tool
            amount_val, tx_type = parse_amount_and_type(
                ext_tx.potential_amount_str,
                ext_tx.potential_credit_str,
                ext_tx.potential_debit_str
            )
            if amount_val is None or tx_type is None:
                processing_notes.append(f"Amount/type parsing failed for amount='{ext_tx.potential_amount_str}', credit='{ext_tx.potential_credit_str}', debit='{ext_tx.potential_debit_str}'")
                logging.warning(f"Skipping transaction {ext_tx.unique_id}: Amount parsing failed.")
                continue # Skip if amount is critical and missing

            # Use description cleaning tool
            cleaned_desc = clean_description(ext_tx.potential_description_str) if ext_tx.potential_description_str else "No Description Provided"
            if not cleaned_desc or cleaned_desc == "No Description Provided":
                processing_notes.append("Description was missing or became empty after cleaning.")
                # Don't skip, but log a warning as description is less critical than date/amount

            # Create NormalizedTransaction
            normalized_transactions.append(NormalizedTransaction(
                transaction_id=ext_tx.unique_id, # Re-use unique_id for traceability
                date=parsed_date,
                description=cleaned_desc,
                amount=amount_val,
                transaction_type=tx_type,
                original_source_file=ext_tx.source_file_name, # This needs to come from RawTransactionData, ensure it's propagated correctly
                                                              # For now, assume it's available or pass it from higher level
                processing_notes=processing_notes
            ))
            
        return normalized_transactions

Task 3.3: Implement QuickBooks Formatter Agent
Goal: Create app/agents/quickbooks_formatter_agent.py to prepare NormalizedTransaction data and generate the final CSV.
Steps:
 * Create app/agents/quickbooks_formatter_agent.py.
 * Implement QuickBooksFormatterAgent class with format_to_quickbooks_csv method.
Developer Genius Note: This agent directly uses the csv_generator tool. Its main role is to pass the correct parameters (format type, date format) from the API request to the tool.
Copilot Prompt (Execute inside app/agents/quickbooks_formatter_agent.py):
# app/agents/quickbooks_formatter_agent.py
# Import necessary types and schemas: List, Literal, NormalizedTransaction
# Import specific tool: generate_quickbooks_csv
from typing import List, Literal
from app.schemas import NormalizedTransaction
from app.tools.csv_generator import generate_quickbooks_csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QuickBooksFormatterAgent:
    """
    Orchestrates the final formatting of NormalizedTransaction data into
    a QuickBooks-compatible CSV string.
    """

    def format_to_quickbooks_csv(
        self,
        transactions: List[NormalizedTransaction],
        format_type: Literal["3-column", "4-column"],
        date_format_str: str
    ) -> str:
        """
        Takes a list of NormalizedTransaction objects and generates
        a QuickBooks-ready CSV string using the CSV generation tool.
        """
        if not transactions:
            logging.warning("No transactions provided for CSV generation. Returning empty CSV.")
            return ""

        # Directly call the CSV generation tool
        try:
            csv_content = generate_quickbooks_csv(transactions, format_type, date_format_str)
            return csv_content
        except Exception as e:
            logging.error(f"Error during QuickBooks CSV generation: {e}")
            raise # Re-raise to be handled by the main application logic

Next Steps for You (and the next compartment):
After completing these compartments, the next crucial phase will be:
 * Compartment 4: Service Layer & Main Application (FastAPI): This is where the web API is built, connecting the file ingestion, agent orchestration, and job status tracking.
 * Compartment 5: Testing Infrastructure: Setting up pytest and writing unit/integration/end-to-end tests for all components.
 * Compartment 6: Dockerization & Deployment: Packaging the application for easy deployment.
 * Compartment 7: Add-on Feature (Receipt Processing): Building out the receipt functionality.
Let me know when you're ready to dive into Compartment 4! We're building a robust, hiccup-free system!
