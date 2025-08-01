Excellent! Now that our core application structure, services, and agents are in place, it's absolutely critical to ensure their flawless operation. This brings us to Compartment 5: Testing Infrastructure.
Developer Genius Note: For a "no stubs, no TODOs" development, testing isn't an afterthought; it's woven into the very fabric of the design. We will define explicit tests for each module and the integrated pipeline. By creating a robust testing suite, we catch issues early, ensuring confidence in every line of code, especially critical when dealing with AI's inherent variability. We'll use pytest as our testing framework.
Compartment 5: Testing Infrastructure
Objective: Set up pytest and create a comprehensive suite of unit, integration, and end-to-end tests to validate the functionality and robustness of the entire application.
Task 5.1: Configure Pytest & Create Test Directory
Goal: Establish the tests/ directory and add a basic conftest.py for shared fixtures/configurations if needed later.
Steps:
 * Create tests Directory: In the project root (afsp_app).
 * Create tests/__init__.py: An empty file to mark tests as a Python package.
 * Create tests/conftest.py: Initially empty, but useful for future shared fixtures (e.g., test data paths, mock objects).
Copilot Prompts (Conceptual, as these are manual steps initially):
 * mkdir tests
 * touch tests/__init__.py
 * touch tests/conftest.py
Task 5.2: Write Unit Tests for Schemas
Goal: Ensure Pydantic schemas correctly validate and handle data.
Steps:
 * Create tests/test_schemas.py.
 * Write test cases to verify schema instantiation, data validation (e.g., incorrect types causing errors), and optional fields.
Copilot Prompt (Execute inside tests/test_schemas.py):
# tests/test_schemas.py
# Import necessary modules: pytest, BaseModel from pydantic, and all schemas from app.schemas
import pytest
from pydantic import ValidationError
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple, Literal

# Import all schemas directly
from app.schemas import (
    RawTransactionData,
    ExtractedTransaction,
    NormalizedTransaction,
    ReceiptData
)

# Test RawTransactionData schema
def test_raw_transaction_data_valid():
    """Test valid instantiation of RawTransactionData."""
    data = RawTransactionData(
        raw_text="Test transaction details",
        source_file_name="bank_statement.pdf",
        source_file_type="PDF",
        page_number=1,
        timestamp_extracted=datetime.now()
    )
    assert data.raw_text == "Test transaction details"
    assert data.source_file_type == "PDF"
    assert data.page_number == 1
    assert isinstance(data.timestamp_extracted, datetime)

def test_raw_transaction_data_minimal_valid():
    """Test minimal valid instantiation."""
    data = RawTransactionData(
        raw_text="Simple text",
        source_file_name="receipt.jpeg",
        source_file_type="JPEG",
        timestamp_extracted=datetime.now()
    )
    assert data.raw_text == "Simple text"
    assert data.source_file_name == "receipt.jpeg"
    assert data.source_file_type == "JPEG"
    assert data.page_number is None # Ensure optional fields default to None

def test_raw_transaction_data_invalid_type():
    """Test invalid source_file_type raises ValidationError."""
    with pytest.raises(ValidationError):
        RawTransactionData(
            raw_text="Invalid type test",
            source_file_name="unsupported.xyz",
            source_file_type="UNSUPPORTED_TYPE", # Invalid literal
            timestamp_extracted=datetime.now()
        )

# Test ExtractedTransaction schema
def test_extracted_transaction_valid():
    """Test valid instantiation of ExtractedTransaction."""
    data = ExtractedTransaction(
        unique_id="123e4567-e89b-12d3-a456-426614174000",
        raw_text_reference="Some raw text line",
        potential_date_str="07/26/2025",
        potential_description_str="Coffee Shop",
        potential_amount_str="-15.50",
        confidence_score={"date": 0.9, "amount": 0.8},
        extraction_errors=[]
    )
    assert data.unique_id == "123e4567-e89b-12d3-a456-426614174000"
    assert data.potential_date_str == "07/26/2025"
    assert data.potential_amount_str == "-15.50"
    assert data.confidence_score["date"] == 0.9

def test_extracted_transaction_optional_fields():
    """Test ExtractedTransaction with optional fields missing."""
    data = ExtractedTransaction(
        unique_id="some-uuid",
        raw_text_reference="Another raw text",
        confidence_score={"date": 0.5, "description": 0.5, "amount": 0.5}
    )
    assert data.potential_date_str is None
    assert data.potential_credit_str is None

# Test NormalizedTransaction schema
def test_normalized_transaction_valid():
    """Test valid instantiation of NormalizedTransaction."""
    data = NormalizedTransaction(
        transaction_id="abc-123",
        date=date(2025, 7, 26),
        description="Amazon Purchase",
        amount=-55.75,
        transaction_type="Debit",
        original_source_file="invoice.pdf",
        processing_notes=["Cleaned description"]
    )
    assert data.date == date(2025, 7, 26)
    assert data.amount == -55.75
    assert data.transaction_type == "Debit"
    assert "Cleaned description" in data.processing_notes

def test_normalized_transaction_invalid_amount_type():
    """Test NormalizedTransaction with invalid amount type."""
    with pytest.raises(ValidationError):
        NormalizedTransaction(
            transaction_id="abc-123",
            date=date(2025, 7, 26),
            description="Invalid test",
            amount="not_a_number", # Invalid type
            transaction_type="Debit",
            original_source_file="file.csv"
        )

# Test ReceiptData schema (Add-on feature)
def test_receipt_data_valid():
    """Test valid instantiation of ReceiptData."""
    data = ReceiptData(
        receipt_id="receipt-001",
        vendor_name="Coffee Emporium",
        transaction_date=date(2025, 7, 25),
        total_amount=7.50,
        currency="USD",
        line_items=[{"item": "Latte", "price": 4.50}, {"item": "Muffin", "price": 3.00}],
        image_path="/path/to/receipt.jpeg",
        ocr_raw_text="Coffee Emporium\nLatte $4.50\nMuffin $3.00\nTotal $7.50"
    )
    assert data.vendor_name == "Coffee Emporium"
    assert data.total_amount == 7.50
    assert len(data.line_items) == 2

def test_receipt_data_missing_required_field():
    """Test ReceiptData missing a required field."""
    with pytest.raises(ValidationError):
        ReceiptData(
            receipt_id="receipt-002",
            # vendor_name missing
            transaction_date=date(2025, 7, 25),
            total_amount=10.00,
            currency="USD",
            image_path="/path/to/receipt2.jpeg",
            ocr_raw_text="Some text"
        )

# QuickBooksCSVRow is not a Pydantic model for internal use, so no direct schema test here.
# Its structure is verified by the csv_generator tool tests.

Task 5.3: Write Unit Tests for Core Tools
Goal: Thoroughly test each function/method in app/tools/.
Steps:
 * Create tests/test_tools.py (or separate files like test_csv_parser.py, test_date_parser.py etc., for better organization).
 * Write test cases for each tool, covering:
   * Valid Inputs: Expected behavior.
   * Edge Cases: Empty strings, unusual but valid formats, zero amounts, descriptions with special characters.
   * Invalid Inputs: Non-numeric amounts, unparsable dates, corrupted files (for file extractors).
   * Error Handling: Verify that tools log errors and return None or raise specific exceptions as designed.
Developer Genius Note: Mocking external dependencies (like pytesseract or file system operations) is crucial for true unit tests. However, for a "no stubs" approach and given Copilot's capabilities, we'll aim for integration-like unit tests where the tool actually attempts its work, expecting the environment to be set up (e.g., Tesseract installed).
Copilot Prompts (Execute inside tests/test_tools.py for a consolidated file, or respective test_*.py files):
 * Initial Imports for test_tools.py:
   # tests/test_tools.py
import pytest
from datetime import date, datetime
from unittest.mock import patch, mock_open # For file operations and external calls
import os
import io # For StringIO, BytesIO

# Import all tools
from app.tools.csv_parser import parse_csv_to_raw_data
from app.tools.pdf_extractor import extract_pdf_to_raw_data
from app.tools.docx_extractor import extract_docx_to_raw_data
from app.tools.ocr_tool import perform_ocr
from app.tools.date_parser import parse_date_robustly
from app.tools.amount_parser import parse_amount_and_type
from app.tools.description_cleaner import clean_description
from app.tools.csv_generator import generate_quickbooks_csv

# Import schemas for type checking and assertions
from app.schemas import RawTransactionData, NormalizedTransaction

 * Tests for csv_parser.py (parse_csv_to_raw_data):
   # Test cases for parse_csv_to_raw_data
def test_parse_csv_simple():
    csv_content = "Date,Description,Amount\n07/26/2025,Coffee,5.00\n07/27/2025,Groceries,-50.00"
    results = parse_csv_to_raw_data(csv_content, "simple.csv")
    assert len(results) == 3 # Including header as raw_text initially
    assert results[1].raw_text == "07/26/2025,Coffee,5.00"
    assert results[1].source_file_type == "CSV"

def test_parse_csv_empty_content():
    results = parse_csv_to_raw_data("", "empty.csv")
    assert len(results) == 0

def test_parse_csv_malformed_row(caplog):
    # caplog fixture from pytest helps capture logs
    csv_content = "Date,Desc,Amt\n07/26/2025,Valid,-10.00\n\"malformed, row" # Unclosed quote
    with caplog.at_level(logging.WARNING):
        results = parse_csv_to_raw_data(csv_content, "malformed.csv")
    assert len(results) == 2 # Only header and first valid row
    assert "Error reading CSV row" in caplog.text

 * Tests for pdf_extractor.py (extract_pdf_to_raw_data):
   # Test cases for extract_pdf_to_raw_data
@pytest.fixture
def mock_pdf_bytes():
    # Create a dummy PDF in memory using a simple library or just mock PyPDF2 later
    # For actual testing, you'd load a small, real PDF file.
    # This mocks PyPDF2's behavior.
    class MockPage:
        def extract_text(self):
            return "Page 1 Content\nDate: 07/26/2025\nAmount: $100.00"
    class MockPdfReader:
        pages = [MockPage(), MockPage()]
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
    with patch('PyPDF2.PdfReader', return_value=MockPdfReader()) as mock_reader:
        yield b"dummy pdf bytes"

def test_extract_pdf_valid(mock_pdf_bytes):
    results = extract_pdf_to_raw_data(mock_pdf_bytes, "test.pdf")
    assert len(results) == 2
    assert "Page 1 Content" in results[0].raw_text
    assert results[0].source_file_type == "PDF"
    assert results[0].page_number == 0 # PyPDF2 pages are 0-indexed

def test_extract_pdf_corrupted(caplog):
    with patch('PyPDF2.PdfReader', side_effect=PyPDF2.errors.PdfReadError("Corrupted PDF")):
        with caplog.at_level(logging.ERROR):
            results = extract_pdf_to_raw_data(b"corrupted bytes", "corrupted.pdf")
    assert len(results) == 0
    assert "Error opening PDF" in caplog.text

   Developer Genius Note: For pdf_extractor, docx_extractor, and ocr_tool, you'll likely need to use unittest.mock.patch to simulate the library's behavior (e.g., PyPDF2.PdfReader, docx.Document, pytesseract.image_to_string) rather than requiring actual files and Tesseract installation during unit tests. This isolates the tool's logic.
 * Tests for ocr_tool.py (perform_ocr):
   # Test cases for perform_ocr
@pytest.fixture
def dummy_image_bytes():
    # Create a tiny dummy image in memory
    from PIL import Image
    img_byte_arr = io.BytesIO()
    Image.new('RGB', (1, 1), color = 'red').save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_perform_ocr_valid(dummy_image_bytes):
    with patch('pytesseract.image_to_string', return_value="Extracted text"):
        result = perform_ocr(dummy_image_bytes)
    assert result == "Extracted text"

def test_perform_ocr_tesseract_not_found(dummy_image_bytes, caplog):
    with patch('pytesseract.image_to_string', side_effect=pytesseract.TesseractNotFoundError("Tesseract not found")):
        with caplog.at_level(logging.CRITICAL):
            result = perform_ocr(dummy_image_bytes)
    assert result is None
    assert "Tesseract executable not found" in caplog.text

def test_perform_ocr_generic_error(dummy_image_bytes, caplog):
    with patch('pytesseract.image_to_string', side_effect=Exception("OCR failed")):
        with caplog.at_level(logging.ERROR):
            result = perform_ocr(dummy_image_bytes)
    assert result is None
    assert "Error during OCR" in caplog.text

 * Tests for date_parser.py (parse_date_robustly):
   # Test cases for parse_date_robustly
def test_parse_date_robustly_mm_dd_yyyy():
    assert parse_date_robustly("07/26/2025") == date(2025, 7, 26)

def test_parse_date_robustly_dd_mm_yyyy():
    assert parse_date_robustly("26-07-2025") == date(2025, 7, 26)

def test_parse_date_robustly_text_month():
    assert parse_date_robustly("Jul 26, 2025") == date(2025, 7, 26)
    assert parse_date_robustly("26-July-2025") == date(2025, 7, 26)

def test_parse_date_robustly_invalid_format(caplog):
    with caplog.at_level(logging.INFO): # Assuming warning level for parse failures
        assert parse_date_robustly("not a date string") is None
    assert "Could not parse date string" in caplog.text

def test_parse_date_robustly_empty_string():
    assert parse_date_robustly("") is None

 * Tests for amount_parser.py (parse_amount_and_type):
   # Test cases for parse_amount_and_type
def test_parse_amount_and_type_positive_amount():
    amount, tx_type = parse_amount_and_type(potential_amount_str="123.45", potential_credit_str=None, potential_debit_str=None)
    assert amount == 123.45
    assert tx_type == "Debit" # Default for positive single amount (expense)

def test_parse_amount_and_type_negative_amount():
    amount, tx_type = parse_amount_and_type(potential_amount_str="-50.00", potential_credit_str=None, potential_debit_str=None)
    assert amount == -50.00
    assert tx_type == "Debit"

def test_parse_amount_and_type_credit_column():
    amount, tx_type = parse_amount_and_type(potential_amount_str=None, potential_credit_str="75.20", potential_debit_str=None)
    assert amount == 75.20
    assert tx_type == "Credit"

def test_parse_amount_and_type_debit_column():
    amount, tx_type = parse_amount_and_type(potential_amount_str=None, potential_credit_str=None, potential_debit_str="150.00")
    assert amount == -150.00 # Debit amounts from column should be negative
    assert tx_type == "Debit"

def test_parse_amount_and_type_with_currency_and_commas():
    amount, tx_type = parse_amount_and_type(potential_amount_str="$1,234.56", potential_credit_str=None, potential_debit_str=None)
    assert amount == 1234.56
    assert tx_type == "Debit"

def test_parse_amount_and_type_invalid_string(caplog):
    with caplog.at_level(logging.WARNING):
        amount, tx_type = parse_amount_and_type(potential_amount_str="not_a_number", potential_credit_str=None, potential_debit_str=None)
    assert amount is None
    assert tx_type is None
    assert "Could not parse amount" in caplog.text

def test_parse_amount_and_type_empty_strings():
    amount, tx_type = parse_amount_and_type(potential_amount_str="", potential_credit_str="", potential_debit_str="")
    assert amount is None
    assert tx_type is None

 * Tests for description_cleaner.py (clean_description):
   # Test cases for clean_description
def test_clean_description_basic():
    assert clean_description("  Online Payment - Electricity Bill  ") == "Electricity Bill"

def test_clean_description_removes_pos_transaction():
    assert clean_description("POS TRANSACTION - Starbucks #1234") == "Starbucks"

def test_clean_description_removes_debit_card_purchase():
    assert clean_description("DEBIT CARD PURCHASE - Walmart") == "Walmart"

def test_clean_description_whitespace_only():
    assert clean_description("   ") == ""

def test_clean_description_empty_string():
    assert clean_description("") == ""

def test_clean_description_no_match():
    assert clean_description("Monthly Subscription Service") == "Monthly Subscription Service"

 * Tests for csv_generator.py (generate_quickbooks_csv):
   # Test cases for generate_quickbooks_csv
@pytest.fixture
def sample_normalized_transactions():
    return [
        NormalizedTransaction(
            transaction_id="tx1", date=date(2025, 7, 26), description="Coffee Shop",
            amount=-5.50, transaction_type="Debit", original_source_file="test.pdf"
        ),
        NormalizedTransaction(
            transaction_id="tx2", date=date(2025, 7, 27), description="Freelance Income",
            amount=250.00, transaction_type="Credit", original_source_file="test.pdf"
        )
    ]

def test_generate_quickbooks_csv_3_column(sample_normalized_transactions):
    csv_content = generate_quickbooks_csv(sample_normalized_transactions, "3-column", "MM/DD/YYYY")
    expected_lines = [
        "Date,Description,Amount",
        "07/26/2025,Coffee Shop,-5.50",
        "07/27/2025,Freelance Income,250.00"
    ]
    assert csv_content.strip().split('\n') == expected_lines

def test_generate_quickbooks_csv_4_column(sample_normalized_transactions):
    csv_content = generate_quickbooks_csv(sample_normalized_transactions, "4-column", "DD/MM/YYYY")
    expected_lines = [
        "Date,Description,Credit,Debit",
        "26/07/2025,Coffee Shop,,5.50", # Debit is positive in this column
        "27/07/2025,Freelance Income,250.00," # Credit is positive in this column
    ]
    assert csv_content.strip().split('\n') == expected_lines

def test_generate_quickbooks_csv_empty_transactions():
    csv_content = generate_quickbooks_csv([], "3-column", "MM/DD/YYYY")
    assert csv_content == "" # Should return empty string for no transactions

def test_generate_quickbooks_csv_different_date_format():
    transactions = [
        NormalizedTransaction(
            transaction_id="tx1", date=date(2025, 1, 1), description="Test",
            amount=-10.00, transaction_type="Debit", original_source_file="test.pdf"
        )
    ]
    csv_content = generate_quickbooks_csv(transactions, "3-column", "YYYY-MM-DD")
    assert "2025-01-01,Test,-10.00" in csv_content

Task 5.4: Write Integration Tests for Agents
Goal: Verify that agents correctly orchestrate and pass data between tools and transform schemas.
Steps:
 * Create tests/test_agents.py.
 * Write test cases that simulate the flow through an agent, providing inputs in the expected _In_ schema and asserting outputs match the _Out_ schema.
 * Mock external dependencies or lower-level tools where appropriate to focus on the agent's orchestration logic.
Copilot Prompt (Execute inside tests/test_agents.py):
# tests/test_agents.py
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, date
import uuid

# Import agents
from app.agents.raw_data_extraction_agent import RawDataExtractionAgent
from app.agents.transaction_interpretation_agent import TransactionInterpretationAgent
from app.agents.quickbooks_formatter_agent import QuickBooksFormatterAgent

# Import schemas for creating mock data and assertions
from app.schemas import RawTransactionData, ExtractedTransaction, NormalizedTransaction

# --- Tests for RawDataExtractionAgent ---
def test_raw_data_extraction_agent_extracts_fields():
    """
    Test that RawDataExtractionAgent correctly extracts fields from raw text
    into ExtractedTransaction objects using its internal logic/regex.
    """
    agent = RawDataExtractionAgent()
    raw_data_list = [
        RawTransactionData(
            raw_text="2025-07-26 Deposit: Salary $5000.00",
            source_file_name="salary.csv",
            source_file_type="CSV",
            timestamp_extracted=datetime.now()
        ),
        RawTransactionData(
            raw_text="07/27/25 Purchase: Walmart -123.45",
            source_file_name="receipt.jpeg",
            source_file_type="JPEG",
            timestamp_extracted=datetime.now()
        )
    ]

    extracted_transactions = agent.extract_fields(raw_data_list)

    assert len(extracted_transactions) == 2
    
    # Test first transaction (deposit)
    tx1 = extracted_transactions[0]
    assert tx1.potential_date_str == "2025-07-26"
    assert "Salary" in tx1.potential_description_str # Description extraction can be heuristic
    assert tx1.potential_amount_str == "5000.00"
    assert tx1.potential_credit_str is None
    assert tx1.potential_debit_str is None

    # Test second transaction (purchase)
    tx2 = extracted_transactions[1]
    assert tx2.potential_date_str == "07/27/25"
    assert "Walmart" in tx2.potential_description_str
    assert tx2.potential_amount_str == "-123.45"
    assert tx2.potential_credit_str is None
    assert tx2.potential_debit_str is None

def test_raw_data_extraction_agent_no_data():
    """Test agent handles empty input list."""
    agent = RawDataExtractionAgent()
    results = agent.extract_fields([])
    assert len(results) == 0

# --- Tests for TransactionInterpretationAgent ---

# Mock tools for TransactionInterpretationAgent to isolate its orchestration logic
@pytest.fixture
def mock_interpretation_tools():
    with patch('app.tools.date_parser.parse_date_robustly') as mock_date_parser, \
         patch('app.tools.amount_parser.parse_amount_and_type') as mock_amount_parser, \
         patch('app.tools.description_cleaner.clean_description') as mock_description_cleaner:
        
        # Configure mocks for expected successful parsing
        mock_date_parser.return_value = date(2025, 7, 26)
        mock_amount_parser.return_value = (-50.00, "Debit")
        mock_description_cleaner.return_value = "Cleaned Description"
        
        yield {
            "date_parser": mock_date_parser,
            "amount_parser": mock_amount_parser,
            "description_cleaner": mock_description_cleaner
        }

def test_transaction_interpretation_agent_processes_successfully(mock_interpretation_tools):
    """
    Test that TransactionInterpretationAgent calls its tools correctly
    and produces NormalizedTransaction data.
    """
    agent = TransactionInterpretationAgent()
    extracted_transactions = [
        ExtractedTransaction(
            unique_id="tx_id_1",
            raw_text_reference="Raw text 1",
            potential_date_str="26/07/2025",
            potential_description_str="Dirty Desc 1",
            potential_amount_str="-50.00",
            confidence_score={"date": 1.0, "description": 1.0, "amount": 1.0},
            extraction_errors=[]
        )
    ]
    
    normalized_transactions = agent.process_extracted_transactions(extracted_transactions)

    assert len(normalized_transactions) == 1
    assert normalized_transactions[0].date == date(2025, 7, 26)
    assert normalized_transactions[0].description == "Cleaned Description"
    assert normalized_transactions[0].amount == -50.00
    assert normalized_transactions[0].transaction_type == "Debit"
    
    # Verify that tools were called
    mock_interpretation_tools["date_parser"].assert_called_once_with("26/07/2025")
    mock_interpretation_tools["amount_parser"].assert_called_once() # Args depend on internal logic
    mock_interpretation_tools["description_cleaner"].assert_called_once_with("Dirty Desc 1")

def test_transaction_interpretation_agent_skips_on_date_failure(mock_interpretation_tools, caplog):
    """Test agent skips transaction if date parsing fails."""
    mock_interpretation_tools["date_parser"].return_value = None # Simulate date parsing failure
    agent = TransactionInterpretationAgent()
    extracted_transactions = [
        ExtractedTransaction(
            unique_id="tx_id_fail",
            raw_text_reference="Raw text for fail",
            potential_date_str="Invalid Date",
            potential_description_str="Desc",
            potential_amount_str="10.00",
            confidence_score={}, extraction_errors=[]
        )
    ]
    
    with caplog.at_level(logging.WARNING):
        normalized_transactions = agent.process_extracted_transactions(extracted_transactions)
    
    assert len(normalized_transactions) == 0
    assert "Date parsing failed for 'Invalid Date'" in caplog.text
    assert "Skipping transaction" in caplog.text

# --- Tests for QuickBooksFormatterAgent ---
def test_quickbooks_formatter_agent_calls_csv_generator():
    """
    Test that QuickBooksFormatterAgent correctly calls the csv_generator tool.
    """
    agent = QuickBooksFormatterAgent()
    mock_transactions = [
        NormalizedTransaction(
            transaction_id="mock1", date=date(2025, 1, 1), description="Test Tx",
            amount=-10.00, transaction_type="Debit", original_source_file="mock.pdf"
        )
    ]
    
    with patch('app.tools.csv_generator.generate_quickbooks_csv', return_value="CSV Content") as mock_csv_generator:
        csv_output = agent.format_to_quickbooks_csv(mock_transactions, "3-column", "MM/DD/YYYY")
        
        assert csv_output == "CSV Content"
        mock_csv_generator.assert_called_once_with(mock_transactions, "3-column", "MM/DD/YYYY")

def test_quickbooks_formatter_agent_empty_transactions():
    """Test formatter agent handles empty transaction list."""
    agent = QuickBooksFormatterAgent()
    with patch('app.tools.csv_generator.generate_quickbooks_csv') as mock_csv_generator:
        csv_output = agent.format_to_quickbooks_csv([], "3-column", "MM/DD/YYYY")
        assert csv_output == ""
        mock_csv_generator.assert_not_called()

def test_quickbooks_formatter_agent_propagates_error():
    """Test formatter agent re-raises errors from CSV generator."""
    agent = QuickBooksFormatterAgent()
    mock_transactions = [
        NormalizedTransaction(
            transaction_id="mock1", date=date(2025, 1, 1), description="Test Tx",
            amount=-10.00, transaction_type="Debit", original_source_file="mock.pdf"
        )
    ]
    with patch('app.tools.csv_generator.generate_quickbooks_csv', side_effect=ValueError("Bad format")) as mock_csv_generator:
        with pytest.raises(ValueError, match="Bad format"):
            agent.format_to_quickbooks_csv(mock_transactions, "3-column", "MM/DD/YYYY")
        mock_csv_generator.assert_called_once()

Task 5.5: Write Integration Tests for Services
Goal: Test FileIngestionService's ability to save files, validate types, and dispatch to raw extraction tools.
Steps:
 * Create tests/test_services.py.
 * Write test cases for FileIngestionService, using unittest.mock.patch to control file system operations and the underlying raw extraction tools.
Copilot Prompt (Execute inside tests/test_services.py):
# tests/test_services.py
import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import os
import io
from datetime import datetime

# Import service
from app.services.file_ingestion_service import FileIngestionService

# Import schemas
from app.schemas import RawTransactionData

# Setup a temporary directory for tests that need actual file operations
@pytest.fixture
def temp_upload_dir(tmp_path):
    temp_dir = tmp_path / "test_uploads"
    temp_dir.mkdir()
    yield str(temp_dir)
    # Cleanup is handled by tmp_path fixture

# --- Tests for FileIngestionService ---
def test_file_ingestion_service_init(tmp_path):
    """Test service initializes and creates upload directory."""
    service = FileIngestionService(upload_dir=str(tmp_path / "test_init_dir"))
    assert (tmp_path / "test_init_dir").is_dir()

def test_file_ingestion_service_save_file(temp_upload_dir):
    """Test _save_file correctly saves bytes to disk."""
    service = FileIngestionService(upload_dir=temp_upload_dir)
    file_data = b"test file content"
    file_name = "test.txt"
    
    saved_path = service._save_file(file_data, file_name)
    
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_data
    assert saved_path.parent == Path(temp_upload_dir)
    # Check that a UUID is part of the filename
    assert len(saved_path.stem) > 8 and saved_path.stem != Path(file_name).stem
    os.remove(saved_path) # Clean up

def test_file_ingestion_service_validate_file_type():
    """Test validate_file_type categorizes extensions correctly."""
    service = FileIngestionService()
    assert service.validate_file_type("report.pdf") == "PDF"
    assert service.validate_file_type("data.csv") == "CSV"
    assert service.validate_file_type("document.docx") == "DOCX"
    assert service.validate_file_type("image.jpeg") == "JPEG"
    assert service.validate_file_type("photo.png") == "JPEG" # Grouped
    assert service.validate_file_type("unknown.xyz") == "UNSUPPORTED"
    assert service.validate_file_type("report.doc") == "DOCX" # Handles .doc as well for simplicity

# Test ingest_and_extract_raw by mocking underlying tool calls
def test_ingest_and_extract_raw_csv(temp_upload_dir):
    """Test ingest_and_extract_raw dispatches to CSV parser."""
    service = FileIngestionService(upload_dir=temp_upload_dir)
    file_bytes = b"header1,header2\ndata1,data2"
    file_name = "test.csv"
    
    with patch('app.tools.csv_parser.parse_csv_to_raw_data', return_value=[
        RawTransactionData(raw_text="mock CSV data", source_file_name=file_name, source_file_type="CSV", timestamp_extracted=datetime.now())
    ]) as mock_parser:
        results = service.ingest_and_extract_raw(file_bytes, file_name)
        assert len(results) == 1
        assert "mock CSV data" in results[0].raw_text
        mock_parser.assert_called_once()
    
    # Assert temporary file is cleaned up
    assert not any(Path(temp_upload_dir).iterdir())

def test_ingest_and_extract_raw_pdf(temp_upload_dir):
    """Test ingest_and_extract_raw dispatches to PDF extractor."""
    service = FileIngestionService(upload_dir=temp_upload_dir)
    file_bytes = b"%PDF-1.4\n..."
    file_name = "test.pdf"
    
    with patch('app.tools.pdf_extractor.extract_pdf_to_raw_data', return_value=[
        RawTransactionData(raw_text="mock PDF data", source_file_name=file_name, source_file_type="PDF", timestamp_extracted=datetime.now())
    ]) as mock_extractor:
        results = service.ingest_and_extract_raw(file_bytes, file_name)
        assert len(results) == 1
        assert "mock PDF data" in results[0].raw_text
        mock_extractor.assert_called_once()

def test_ingest_and_extract_raw_jpeg(temp_upload_dir):
    """Test ingest_and_extract_raw dispatches to OCR tool for JPEG."""
    service = FileIngestionService(upload_dir=temp_upload_dir)
    file_bytes = b"JPEG_BYTES_HERE"
    file_name = "test.jpeg"
    
    with patch('app.tools.ocr_tool.perform_ocr', return_value="OCR Text from Image") as mock_ocr:
        results = service.ingest_and_extract_raw(file_bytes, file_name)
        assert len(results) == 1
        assert results[0].raw_text == "OCR Text from Image"
        assert results[0].source_file_type == "JPEG"
        mock_ocr.assert_called_once_with(file_bytes) # Ensure it passes original bytes

def test_ingest_and_extract_raw_unsupported_type(temp_upload_dir, caplog):
    """Test ingest_and_extract_raw raises error for unsupported types."""
    service = FileIngestionService(upload_dir=temp_upload_dir)
    file_bytes = b"some content"
    file_name = "test.unsupported"
    
    with pytest.raises(ValueError, match="Unsupported file type"), caplog.at_level(logging.WARNING):
        service.ingest_and_extract_raw(file_bytes, file_name)
    assert "Unsupported file type detected" in caplog.text

def test_ingest_and_extract_raw_empty_extraction(temp_upload_dir, caplog):
    """Test ingest_and_extract_raw logs warning if extraction yields no data."""
    service = FileIngestionService(upload_dir=temp_upload_dir)
    file_bytes = b"header1,header2" # A CSV with only header might yield no transactions
    file_name = "empty_data.csv"
    
    with patch('app.tools.csv_parser.parse_csv_to_raw_data', return_value=[]):
        with caplog.at_level(logging.WARNING):
            results = service.ingest_and_extract_raw(file_bytes, file_name)
            assert len(results) == 0
            assert "No raw data extracted" in caplog.text
    ```

#### **Task 5.6: Write End-to-End Tests for FastAPI Application**

**Goal:** Test the full API flow: upload, status check, download.

**Steps:**

1.  **Create `tests/test_main_e2e.py`**.
2.  **Use `pytest-asyncio`** (add to `requirements.txt`) for testing async FastAPI routes.
3.  **Use `httpx`** (add to `requirements.txt`) for making HTTP requests to the test client.
4.  **Mock external dependencies (agents/services)** to isolate the FastAPI logic if necessary, or let them run if you want true end-to-end integration. For a robust e2e, we want them running!
5.  **Create dummy files** for testing uploads.

**Developer Genius Note:** These are the most comprehensive tests. They verify the entire pipeline from user request to final output. It's perfectly fine for these tests to rely on the *actual* implementations of the services and agents. You will need to install `pytest-asyncio` and `httpx`.

**Copilot Prompt (Execute inside `tests/test_main_e2e.py`):**
```python
# tests/test_main_e2e.py
import pytest
from httpx import AsyncClient
from app.main import app, job_status_db, UPLOAD_DIR, DOWNLOAD_DIR # Import app and global vars
import os
from pathlib import Path
import asyncio
from datetime import date, datetime # For creating realistic test data

# Fixture to clear the job_status_db before each test
@pytest.fixture(autouse=True)
def clean_job_status_db():
    job_status_db.clear()
    yield
    # Ensure temp files are cleaned after each test
    for f in Path(UPLOAD_DIR).iterdir():
        if f.is_file(): os.remove(f)
    for f in Path(DOWNLOAD_DIR).iterdir():
        if f.is_file(): os.remove(f)

# Fixture for asynchronous test client
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Dummy CSV content for testing
DUMMY_CSV_CONTENT = """Date,Description,Amount
01/15/2024,Sample Transaction One,100.00
01/16/2024,Sample Transaction Two,-50.25
01/17/2024,Sample Income,200.00"""

# Dummy PDF content (requires a real, small PDF file for actual content, mocking for this example)
@pytest.fixture
def dummy_pdf_bytes():
    # In a real scenario, load a small test.pdf from a 'data' directory
    # For this prompt, we'll create a very minimal "mock" PDF content
    return b"%PDF-1.4\n1 0 obj<<>>endobj\nxref\n0 2\n0000000000 65535 f\n0000000010 00000 n\ntrailer<<>>startxref\n10\n%%EOF"

# Dummy image bytes (requires a real, small JPEG for actual content, mocking for this example)
@pytest.fixture
def dummy_jpeg_bytes():
    # In a real scenario, load a small test.jpeg from a 'data' directory
    # For this prompt, creating minimal dummy bytes
    from PIL import Image
    import io
    img_byte_arr = io.BytesIO()
    Image.new('RGB', (10, 10), color = 'blue').save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()


# --- E2E Tests ---

@pytest.mark.asyncio
async def test_e2e_csv_upload_process_download(async_client, caplog):
    """
    Tests the complete pipeline for a CSV file: upload -> check status -> download.
    """
    file_content = DUMMY_CSV_CONTENT.encode("utf-8")
    file_name = "test_bank_statement.csv"

    # Step 1: Upload the file
    response = await async_client.post(
        "/upload_statement",
        files={"file": (file_name, file_content, "text/csv")},
        data={"quickbooks_csv_format": "3-column", "date_format": "MM/DD/YYYY"}
    )
    assert response.status_code == 200
    upload_response = response.json()
    job_id = upload_response["job_id"]
    assert upload_response["status"] == "QUEUED"
    assert "queued for processing" in upload_response["message"]
    logging.info(f"E2E: Uploaded CSV, Job ID: {job_id}")

    # Step 2: Poll status until completion (with a timeout)
    timeout_seconds = 10 # Adjust based on expected processing time
    start_time = datetime.now()
    while True:
        status_response = await async_client.get(f"/status/{job_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        logging.info(f"E2E: Job {job_id} Status: {status_data['status']}, Progress: {status_data['progress']:.2f}")

        if status_data["status"] == "COMPLETED":
            assert status_data["progress"] == 1.0
            assert status_data["download_url"] is not None
            assert len(status_data["preview_data"]) > 0 # Expect some preview data
            logging.info(f"E2E: Job {job_id} COMPLETED. Download URL: {status_data['download_url']}")
            break
        elif status_data["status"] == "FAILED":
            pytest.fail(f"Job {job_id} FAILED: {status_data['errors']}")
            
        await asyncio.sleep(0.5) # Wait before polling again
        if (datetime.now() - start_time).total_seconds() > timeout_seconds:
            pytest.fail(f"Job {job_id} did not complete within {timeout_seconds} seconds. Current status: {status_data['status']}")

    # Step 3: Download the generated CSV
    download_url = status_data["download_url"]
    download_response = await async_client.get(download_url)
    assert download_response.status_code == 200
    assert "text/csv" in download_response.headers["content-type"]
    
    downloaded_content = download_response.text
    # Verify content structure (e.g., header and at least one transaction line)
    assert "Date,Description,Amount" in downloaded_content
    assert "01/15/2024,Sample Transaction One,100.00" in downloaded_content
    logging.info(f"E2E: Downloaded CSV content verified for Job ID: {job_id}")

@pytest.mark.asyncio
async def test_e2e_pdf_upload_process_download(async_client, caplog, dummy_pdf_bytes):
    """
    Tests the complete pipeline for a PDF file: upload -> check status -> download.
    NOTE: This test relies on PyPDF2 extracting *some* text and then OCR/Regex
    finding patterns. Actual success depends on the dummy_pdf_bytes containing
    parsable text.
    """
    file_content = dummy_pdf_bytes
    file_name = "test_statement.pdf"

    # Step 1: Upload the file
    response = await async_client.post(
        "/upload_statement",
        files={"file": (file_name, file_content, "application/pdf")},
        data={"quickbooks_csv_format": "4-column", "date_format": "DD/MM/YYYY"}
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    logging.info(f"E2E: Uploaded PDF, Job ID: {job_id}")

    # Step 2: Poll status
    timeout_seconds = 15 # PDF processing might take slightly longer
    start_time = datetime.now()
    while True:
        status_response = await async_client.get(f"/status/{job_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        logging.info(f"E2E: Job {job_id} Status: {status_data['status']}, Progress: {status_data['progress']:.2f}")

        if status_data["status"] == "COMPLETED":
            assert status_data["download_url"] is not None
            # Basic check for preview data, might be empty if PDF extraction is very poor
            logging.info(f"E2E: Job {job_id} COMPLETED for PDF. Preview: {status_data['preview_data']}")
            break
        elif status_data["status"] == "FAILED":
            pytest.fail(f"Job {job_id} FAILED: {status_data['errors']}")
            
        await asyncio.sleep(1) # Longer sleep for PDF
        if (datetime.now() - start_time).total_seconds() > timeout_seconds:
            pytest.fail(f"Job {job_id} did not complete within {timeout_seconds} seconds for PDF. Current status: {status_data['status']}")

    # Step 3: Download the generated CSV (only if preview data suggests success)
    if status_data["download_url"]:
        download_response = await async_client.get(status_data["download_url"])
        assert download_response.status_code == 200
        assert "text/csv" in download_response.headers["content-type"]
        downloaded_content = download_response.text
        assert "Date,Description,Credit,Debit" in downloaded_content # Check 4-column header
        logging.info(f"E2E: Downloaded PDF CSV content verified for Job ID: {job_id}")
    else:
        pytest.fail(f"PDF processing completed but no download URL: {status_data.get('errors')}")


@pytest.mark.asyncio
async def test_e2e_unsupported_file_type(async_client):
    """
    Tests uploading an unsupported file type results in a FAILED status.
    """
    file_content = b"This is some unsupported file content."
    file_name = "unsupported.zip"

    response = await async_client.post(
        "/upload_statement",
        files={"file": (file_name, file_content, "application/zip")},
        data={"quickbooks_csv_format": "3-column", "date_format": "MM/DD/YYYY"}
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    logging.info(f"E2E: Uploaded unsupported file, Job ID: {job_id}")

    timeout_seconds = 5
    start_time = datetime.now()
    while True:
        status_response = await async_client.get(f"/status/{job_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        logging.info(f"E2E: Job {job_id} Status: {status_data['status']}, Progress: {status_data['progress']:.2f}")

        if status_data["status"] == "FAILED":
            assert "Unsupported file type" in status_data["errors"][0]
            logging.info(f"E2E: Job {job_id} FAILED as expected for unsupported file.")
            break
            
        await asyncio.sleep(0.5)
        if (datetime.now() - start_time).total_seconds() > timeout_seconds:
            pytest.fail(f"Job {job_id} did not fail within {timeout_seconds} seconds for unsupported file. Current status: {status_data['status']}")

@pytest.mark.asyncio
async def test_e2e_get_status_non_existent_job(async_client):
    """Test requesting status for a non-existent job ID."""
    response = await async_client.get("/status/non-existent-job-id")
    assert response.status_code == 404
    assert "Job ID not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_e2e_download_non_completed_job(async_client):
    """Test attempting to download a non-completed job."""
    job_id = str(uuid.uuid4())
    job_status_db[job_id] = {"status": "QUEUED", "progress": 0.0, "download_url": None, "errors": [], "preview_data": []}
    response = await async_client.get(f"/download/{job_id}")
    assert response.status_code == 404
    assert "File not ready for download" in response.json()["detail"]


Final Steps for Testing:
 * Install Pytest and related libraries:
   * Add pytest, pytest-asyncio, httpx to requirements.txt.
   * Run pip install -r requirements.txt.
 * Run Tests: From your afsp_app root directory, execute pytest.
   * Observe the test results. Pay close attention to any failures and the associated logs.
   * Remember that for OCR and PDF/DOCX extraction, the success of tests for those tools and agents will depend on having actual (even small) test files in a data directory and Tesseract installed and configured correctly. The E2E tests for PDF/JPEG will likely require a functional Tesseract.
This comprehensive testing setup provides a high degree of confidence in the application's correctness. With these tests in place, we're ready to look at packaging and deployment!
Let me know when you're ready to proceed to Compartment 6: Dockerization & Deployment!
