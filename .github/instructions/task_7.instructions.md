Excellent! With our core application solidified, configured for local persistence, and ready for deployment with clear instructions, we're now in a fantastic position to enhance its capabilities.
Let's dive into Compartment 7: Receipt Processing Add-on (Enhancement).
Compartment 7: Receipt Processing Add-on (Enhancement)
Objective: Extend the application's functionality to specifically handle receipt images (JPEG/PNG) by introducing a dedicated processing pipeline for structured receipt data extraction and integration into the existing financial data flow. This will leverage the ReceiptData schema we previously defined.
Developer Genius Note: This add-on isn't just about OCR; it's about structured extraction. A raw OCR dump isn't enough. We need to identify key fields like vendor, total, date, and line items. This will likely involve more sophisticated pattern matching (or even a small, specialized local ML model if the rules become too complex, though we'll start with robust regex). The output should still seamlessly feed into the NormalizedTransaction schema for QuickBooks CSV generation.
Task 7.1: Develop ReceiptExtractorAgent
Goal: Create a new agent responsible for taking the raw OCR text from a receipt and extracting structured data into the ReceiptData schema.
Steps:
 * Create app/agents/receipt_extractor_agent.py.
 * Implement extract_receipt_data method:
   * Takes raw OCR text as input.
   * Uses regex patterns or simple keyword matching to find vendor_name, transaction_date, total_amount, currency, and potentially line_items.
   * Returns a ReceiptData object. Handle cases where data isn't found gracefully.
Copilot Prompt (Execute inside app/agents/receipt_extractor_agent.py):
# app/agents/receipt_extractor_agent.py
import re
import logging
from typing import Optional, List, Dict, Any
from datetime import date
from app.schemas import ReceiptData, RawTransactionData # Import ReceiptData and RawTransactionData
from app.tools.date_parser import parse_date_robustly # Re-use existing date parser
from app.tools.amount_parser import parse_amount_and_type # Re-use amount parser utility

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReceiptExtractorAgent:
    """
    Agent responsible for extracting structured data from raw OCR text of a receipt.
    """
    def __init__(self):
        # Define common regex patterns for extraction
        self.date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',  # MM/DD/YY, DD-MM-YYYY
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\b', # Month DD, YYYY
            r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b' # DD Month YYYY
        ]
        self.total_patterns = [
            r'(?:TOTAL|AMOUNT DUE|BALANCE|GRAND TOTAL)\s*[:\$€£]?\s*([\d,]+\.\d{2})\b', # TOTAL $XX.XX
            r'(\$€£)\s*([\d,]+\.\d{2})\b', # $XX.XX without explicit label
            r'\b([\d,]+\.\d{2})\s*(?:USD|EUR|GBP)\b' # XX.XX USD
        ]
        self.currency_patterns = [r'\$|USD', r'€|EUR', r'£|GBP']
        self.line_item_pattern = r'(\d+\.?\d*)\s*x?\s*([A-Za-z0-9\s]+?)\s+\$?([\d,]+\.\d{2})\b' # Qty Item Price

    def extract_receipt_data(self, raw_ocr_text: str, source_file_name: str, receipt_id: str) -> Optional[ReceiptData]:
        """
        Extracts structured data from raw OCR text to form a ReceiptData object.
        """
        vendor_name: Optional[str] = None
        transaction_date: Optional[date] = None
        total_amount: Optional[float] = None
        currency: Optional[str] = None
        line_items: List[Dict[str, Any]] = []

        # 1. Extract Vendor Name (heuristic: often first non-date/amount line, or above a certain keyword)
        # This is highly heuristic. For a real app, often done with ML or more robust template matching.
        # For now, let's try to get the first significant line.
        lines = [line.strip() for line in raw_ocr_text.split('\n') if line.strip()]
        if lines:
            # Simple heuristic: often the first or second line, excluding common headers/footers
            candidate_vendor_lines = [l for l in lines if not re.search(r'\b(Date|Total|Amount|Tax|VAT)\b', l, re.IGNORECASE) and len(l) > 5 and len(l) < 50]
            if candidate_vendor_lines:
                # Take the first plausible line as a simple heuristic for vendor name
                vendor_name = candidate_vendor_lines[0]
                # Further refine by removing common receipt boilerplate at the end of lines
                vendor_name = re.sub(r'(?:RECEIPT|INVOICE|ORDER|BILL)\s*(?:#|NO\.)?\s*\d*$', '', vendor_name, flags=re.IGNORECASE).strip()
                vendor_name = re.sub(r'TEL\s*[:\s]*\+?\d[\d\s-]*\d|\b(?:VAT|TAX)\s*NO\s*[:\s]*[A-Z0-9]+\b', '', vendor_name, flags=re.IGNORECASE).strip()


        # 2. Extract Transaction Date
        for pattern in self.date_patterns:
            match = re.search(pattern, raw_ocr_text, re.IGNORECASE)
            if match:
                parsed_date = parse_date_robustly(match.group(0))
                if parsed_date:
                    transaction_date = parsed_date
                    break
        if not transaction_date:
            logging.warning(f"ReceiptExtractorAgent: Could not find transaction date in {source_file_name}")

        # 3. Extract Total Amount and Currency
        for pattern in self.total_patterns:
            match = re.search(pattern, raw_ocr_text, re.IGNORECASE)
            if match:
                amount_str = match.group(match.lastindex) # Get the last captured group which should be the amount
                # Use amount_parser to clean and convert
                total_amount, _ = parse_amount_and_type(potential_amount_str=amount_str.replace(',', ''))
                if total_amount is not None:
                    # Try to infer currency from total line or surrounding text
                    for c_pattern in self.currency_patterns:
                        if re.search(c_pattern, match.group(0)): # Check the matched total string first
                            currency = c_pattern.replace('\\', '') # Remove regex escapes for display
                            if currency == '$': currency = 'USD' # Normalize
                            elif currency == '€': currency = 'EUR'
                            elif currency == '£': currency = 'GBP'
                            break
                    if not currency: # If not found in the total line, try entire text
                        for c_pattern in self.currency_patterns:
                            if re.search(c_pattern, raw_ocr_text):
                                currency = c_pattern.replace('\\', '')
                                if currency == '$': currency = 'USD'
                                elif currency == '€': currency = 'EUR'
                                elif currency == '£': currency = 'GBP'
                                break
                    currency = currency or "USD" # Default to USD if none found
                    break
        if total_amount is None:
             logging.warning(f"ReceiptExtractorAgent: Could not find total amount in {source_file_name}")

        # 4. Extract Line Items (optional, more complex)
        for line in lines:
            match = re.search(self.line_item_pattern, line, re.IGNORECASE)
            if match:
                try:
                    qty = float(match.group(1)) if match.group(1) else 1.0
                    item_desc = match.group(2).strip()
                    item_price_str = match.group(3).replace(',', '')
                    item_price, _ = parse_amount_and_type(potential_amount_str=item_price_str)
                    if item_price is not None:
                        line_items.append({"item": item_desc, "quantity": qty, "price": item_price})
                except Exception as e:
                    logging.debug(f"Could not parse line item '{line}': {e}")
        
        if not vendor_name or not transaction_date or total_amount is None:
            logging.warning(f"ReceiptExtractorAgent: Missing critical fields (vendor, date, total) for {source_file_name}. Skipping ReceiptData creation.")
            return None

        try:
            receipt_data = ReceiptData(
                receipt_id=receipt_id,
                vendor_name=vendor_name,
                transaction_date=transaction_date,
                total_amount=total_amount,
                currency=currency or "USD", # Ensure currency is set, default to USD
                line_items=line_items,
                image_path=source_file_name, # Storing filename as path for reference
                ocr_raw_text=raw_ocr_text
            )
            logging.info(f"Successfully extracted receipt data for {source_file_name}")
            return receipt_data
        except Exception as e:
            logging.error(f"Failed to create ReceiptData object for {source_file_name}: {e}", exc_info=True)
            return None


Task 7.2: Integrate ReceiptExtractorAgent into TransactionInterpretationAgent and main.py
Goal: Modify the interpretation agent to handle ReceiptData and convert it into a NormalizedTransaction object. Update the main processing pipeline to pass OCR'd receipt data to this new flow.
Steps:
 * Modify TransactionInterpretationAgent:
   * Add a new method, process_receipt_data, that takes ReceiptData as input.
   * This method will map ReceiptData fields (vendor, total, date) to NormalizedTransaction fields (description, amount, date, type).
   * It will return a NormalizedTransaction object.
 * Modify app/main.py:
   * In _process_statement_background, check the source_file_type of RawTransactionData.
   * If source_file_type is "JPEG" (or "PNG"), pass the RawTransactionData.raw_text (which is the OCR output) to the new ReceiptExtractorAgent.
   * Then, pass the resulting ReceiptData to the TransactionInterpretationAgent's new method.
   * Combine the NormalizedTransaction from receipts with those from other sources for the final CSV.
Copilot Prompts:
 * Modify app/agents/transaction_interpretation_agent.py:
   # app/agents/transaction_interpretation_agent.py (add this class/method)
import logging
from typing import List, Optional
import re
from datetime import date

from app.schemas import ExtractedTransaction, NormalizedTransaction, ReceiptData # Import ReceiptData
from app.tools.date_parser import parse_date_robustly
from app.tools.amount_parser import parse_amount_and_type
from app.tools.description_cleaner import clean_description

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TransactionInterpretationAgent:
    """
    Agent responsible for interpreting extracted transaction fields into a normalized format.
    Now also handles structured receipt data.
    """
    def process_extracted_transactions(self, extracted_transactions: List[ExtractedTransaction]) -> List[NormalizedTransaction]:
        """
        Processes a list of ExtractedTransaction objects into NormalizedTransaction objects.
        """
        normalized_transactions: List[NormalizedTransaction] = []
        for ext_tx in extracted_transactions:
            transaction_id = ext_tx.unique_id
            processing_notes: List[str] = ext_tx.extraction_errors[:] # Start with any existing errors

            # 1. Parse Date
            parsed_date = parse_date_robustly(ext_tx.potential_date_str)
            if parsed_date is None:
                processing_notes.append(f"Date parsing failed for '{ext_tx.potential_date_str}'. Skipping transaction.")
                logging.warning(f"Date parsing failed for '{ext_tx.potential_date_str}'. Skipping transaction {transaction_id}.")
                continue # Skip this transaction if date is critical and failed

            # 2. Parse Amount and Type
            amount, tx_type = parse_amount_and_type(
                potential_amount_str=ext_tx.potential_amount_str,
                potential_credit_str=ext_tx.potential_credit_str,
                potential_debit_str=ext_tx.potential_debit_str
            )
            if amount is None or tx_type is None:
                processing_notes.append(f"Amount parsing failed for '{ext_tx.potential_amount_str}'. Skipping transaction.")
                logging.warning(f"Amount parsing failed for '{ext_tx.potential_amount_str}'. Skipping transaction {transaction_id}.")
                continue # Skip if amount is critical and failed

            # 3. Clean Description
            cleaned_description = clean_description(ext_tx.potential_description_str or ext_tx.raw_text_reference)
            if not cleaned_description:
                processing_notes.append("Description was empty after cleaning.")
                cleaned_description = "Unknown Transaction" # Default description

            normalized_transactions.append(
                NormalizedTransaction(
                    transaction_id=transaction_id,
                    date=parsed_date,
                    description=cleaned_description,
                    amount=amount,
                    transaction_type=tx_type,
                    original_source_file=ext_tx.raw_text_reference, # Use raw_text_reference for now
                    processing_notes=processing_notes
                )
            )
        logging.info(f"Successfully processed {len(normalized_transactions)} from extracted transactions.")
        return normalized_transactions

    def process_receipt_data(self, receipt_data: ReceiptData) -> Optional[NormalizedTransaction]:
        """
        Processes a single ReceiptData object into a NormalizedTransaction object.
        """
        processing_notes: List[str] = []

        # Use existing data from ReceiptData
        transaction_id = receipt_data.receipt_id
        parsed_date = receipt_data.transaction_date
        amount = -receipt_data.total_amount # Receipts are typically expenses, so make amount negative
        tx_type = "Debit" # Default for receipts

        # Description can be vendor name + first line item or just vendor
        description = receipt_data.vendor_name or "Unknown Vendor"
        if receipt_data.line_items:
            first_item = receipt_data.line_items[0].get("item")
            if first_item:
                description = f"{description} - {first_item}"

        # Add notes if line items were found or other details
        if receipt_data.line_items:
            processing_notes.append(f"Extracted {len(receipt_data.line_items)} line items.")
        if receipt_data.currency != "USD": # Add note if currency is not USD
             processing_notes.append(f"Original currency: {receipt_data.currency}")

        if not parsed_date or amount is None or description is None:
            processing_notes.append("Missing critical data for receipt normalization (date, amount, description).")
            logging.warning(f"Skipping receipt {receipt_data.receipt_id} due to missing critical data.")
            return None

        try:
            normalized_tx = NormalizedTransaction(
                transaction_id=transaction_id,
                date=parsed_date,
                description=description,
                amount=amount,
                transaction_type=tx_type,
                original_source_file=receipt_data.image_path, # Use image_path for receipts
                processing_notes=processing_notes
            )
            logging.info(f"Successfully normalized receipt {receipt_data.receipt_id}")
            return normalized_tx
        except Exception as e:
            logging.error(f"Error normalizing receipt {receipt_data.receipt_id}: {e}", exc_info=True)
            return None

 * Modify app/main.py (Copilot Prompt for the _process_statement_background function):
   # app/main.py (modifications within _process_statement_background)
# ... (existing imports)
from app.agents.receipt_extractor_agent import ReceiptExtractorAgent # NEW IMPORT
# ... (rest of imports)

# Global instance for new agent
receipt_extractor_agent = ReceiptExtractorAgent() # NEW GLOBAL INSTANCE

# ... (rest of global instances)

async def _process_statement_background(
    job_id: str,
    file_bytes: bytes,
    file_name: str,
    quickbooks_csv_format: Literal["3-column", "4-column"],
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"]
):
    current_errors: List[str] = []
    all_normalized_transactions: List[NormalizedTransaction] = [] # Collect all normalized transactions here

    try:
        logging.info(f"Job {job_id}: Starting background processing for {file_name}")
        db_manager.update_job_status(job_id, "PROCESSING_INGESTION", 0.1, errors=current_errors)

        raw_transactions: List[RawTransactionData] = []
        try:
            raw_transactions = file_ingestion_service.ingest_and_extract_raw(file_bytes, file_name)
            if not raw_transactions:
                raise ValueError("No raw transactions extracted. File might be empty or unreadable.")
            logging.info(f"Job {job_id}: Raw data extracted. Found {len(raw_transactions)} entries.")
        except Exception as e:
            current_errors.append(f"Ingestion/Raw Extraction Error: {e}")
            logging.error(f"Job {job_id}: Ingestion/Raw Extraction failed: {e}")
            raise

        db_manager.update_job_status(job_id, "PROCESSING_EXTRACTED_FIELDS", 0.3, errors=current_errors)

        # --- Differentiate processing based on source file type ---
        for raw_tx_data in raw_transactions:
            if raw_tx_data.source_file_type in ["JPEG", "PNG"]:
                logging.info(f"Job {job_id}: Processing image file as receipt: {raw_tx_data.source_file_name}")
                # Use a unique ID for the receipt, perhaps based on transaction_id or a new UUID
                receipt_id = f"receipt-{job_id}-{str(uuid.uuid4())}"

                receipt_data = receipt_extractor_agent.extract_receipt_data(
                    raw_tx_data.raw_text, # OCR text is here
                    raw_tx_data.source_file_name,
                    receipt_id
                )
                if receipt_data:
                    normalized_tx = transaction_interpretation_agent.process_receipt_data(receipt_data)
                    if normalized_tx:
                        all_normalized_transactions.append(normalized_tx)
                    else:
                        current_errors.append(f"Failed to normalize receipt from {raw_tx_data.source_file_name}")
                else:
                    current_errors.append(f"Failed to extract structured data from receipt {raw_tx_data.source_file_name}")

            else: # CSV, PDF, DOCX - process as regular transactions
                # Create a single ExtractedTransaction object per raw_tx_data if needed,
                # or ensure raw_data_extraction_agent handles the list for these types
                logging.info(f"Job {job_id}: Processing {raw_tx_data.source_file_type} file as general transaction: {raw_tx_data.source_file_name}")

                # NOTE: raw_data_extraction_agent.extract_fields expects a LIST of RawTransactionData.
                # We should probably refactor it to take a single RawTransactionData if processing one by one,
                # or collect all non-image raw_tx_data and pass them once.
                # For simplicity now, let's create a temporary list to pass to the agent for this specific type.
                extracted_transactions_for_type = raw_data_extraction_agent.extract_fields([raw_tx_data]) # Pass single item in a list

                if extracted_transactions_for_type:
                    normalized_from_extracted = transaction_interpretation_agent.process_extracted_transactions(extracted_transactions_for_type)
                    all_normalized_transactions.extend(normalized_from_extracted)
                else:
                    current_errors.append(f"No extracted fields from {raw_tx_data.source_file_name} of type {raw_tx_data.source_file_type}")
                    logging.warning(f"No extracted fields from {raw_tx_data.source_file_name} of type {raw_tx_data.source_file_type}")

        if not all_normalized_transactions:
            raise ValueError("No normalized transactions produced from any input file.")

        logging.info(f"Job {job_id}: Total normalized transactions: {len(all_normalized_transactions)}")
        db_manager.update_job_status(
            job_id,
            "PROCESSING_INTERPRETATION", # Updated status after all interpretations
            0.6,
            errors=current_errors,
            preview_data=all_normalized_transactions[:min(5, len(all_normalized_transactions))] # Preview overall data
        )
        # ... (rest of the formatting and completion logic) ...

        db_manager.update_job_status(job_id, "PROCESSING_FORMATTING", 0.9, errors=current_errors)

        csv_content: str = ""
        output_file_name: str = ""
        output_file_path: Path

        try:
            csv_content = quickbooks_formatter_agent.format_to_quickbooks_csv(
                all_normalized_transactions, quickbooks_csv_format, date_format
            )

            output_file_name = f"quickbooks_export_{Path(file_name).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{job_id[:8]}.csv"
            output_file_path = DOWNLOAD_DIR / output_file_name

            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(csv_content)

            db_manager.update_job_status(job_id, "COMPLETED", 1.0, 
                                        download_url=output_file_name,
                                        errors=current_errors, 
                                        preview_data=all_normalized_transactions[:min(5, len(all_normalized_transactions))]
                                        )
            logging.info(f"Job {job_id}: CSV generated and saved to {output_file_path}")
        except Exception as e:
            current_errors.append(f"CSV Formatting/Saving Error: {e}")
            logging.error(f"Job {job_id}: CSV Formatting/Saving failed: {e}")
            raise

        logging.info(f"Job {job_id} COMPLETED successfully.")

    except Exception as e:
        current_errors.append(f"Critical processing error: {e}")
        db_manager.update_job_status(job_id, "FAILED", 1.0, errors=current_errors)
        logging.critical(f"Job {job_id} FAILED with unhandled exception: {e}", exc_info=True)

   Developer Genius Note: Notice the loop over raw_transactions and the conditional logic (if raw_tx_data.source_file_type in ["JPEG", "PNG"]). This allows us to route different file types through their appropriate processing paths (receipt-specific vs. general transaction extraction). I've temporarily handled raw_data_extraction_agent.extract_fields expecting a list by wrapping raw_tx_data in [raw_tx_data]. A more elegant long-term solution might involve modifying that agent's extract_fields method to handle a single RawTransactionData or a list and calling it once. For now, this gets the job done without complex refactoring.
Task 7.3: Update Tests for Receipt Processing
Goal: Add unit and integration tests to cover the new ReceiptExtractorAgent and the TransactionInterpretationAgent's new process_receipt_data method. Also, update E2E tests to include an image (JPEG/PNG) upload.
Steps:
 * Create tests/test_receipt_agent.py: Test ReceiptExtractorAgent's extraction logic.
 * Update tests/test_agents.py: Add tests for TransactionInterpretationAgent.process_receipt_data.
 * Update tests/test_main_e2e.py: Add an E2E test case for uploading a JPEG/PNG.
Copilot Prompts:
 * Prompt for tests/test_receipt_agent.py:
   # tests/test_receipt_agent.py
import pytest
from datetime import date
from app.agents.receipt_extractor_agent import ReceiptExtractorAgent
from app.schemas import ReceiptData

def test_receipt_extractor_agent_basic_receipt():
    ocr_text = """
    Coffee Shop
    123 Main St
    Date: 07/26/2025
    Latte $4.50
    Muffin $3.00
    TOTAL: $7.50
    """
    agent = ReceiptExtractorAgent()
    receipt_id = "test_receipt_1"
    source_name = "coffee_receipt.jpeg"
    receipt_data = agent.extract_receipt_data(ocr_text, source_name, receipt_id)

    assert receipt_data is not None
    assert receipt_data.receipt_id == receipt_id
    assert receipt_data.vendor_name == "Coffee Shop"
    assert receipt_data.transaction_date == date(2025, 7, 26)
    assert receipt_data.total_amount == 7.50
    assert receipt_data.currency == "USD"
    assert len(receipt_data.line_items) == 2 # "Latte" and "Muffin"
    assert receipt_data.line_items[0]["item"] == "Latte"
    assert receipt_data.line_items[1]["price"] == 3.00
    assert receipt_data.image_path == source_name
    assert "TOTAL: $7.50" in receipt_data.ocr_raw_text

def test_receipt_extractor_agent_no_date_or_amount():
    ocr_text = """
    Grocery Store
    Bread
    Milk
    """
    agent = ReceiptExtractorAgent()
    receipt_id = "test_receipt_fail"
    source_name = "no_info.png"
    receipt_data = agent.extract_receipt_data(ocr_text, source_name, receipt_id)
    assert receipt_data is None # Should return None if critical data is missing

def test_receipt_extractor_agent_different_formats():
    ocr_text = """
    Walmart Store #123
    26-Jul-2025
    SUBTOTAL 88.99
    TAX 5.34
    GRAND TOTAL €94.33
    """
    agent = ReceiptExtractorAgent()
    receipt_id = "test_receipt_2"
    source_name = "walmart_receipt.jpeg"
    receipt_data = agent.extract_receipt_data(ocr_text, source_name, receipt_id)

    assert receipt_data is not None
    assert "Walmart Store" in receipt_data.vendor_name
    assert receipt_data.transaction_date == date(2025, 7, 26)
    assert receipt_data.total_amount == 94.33
    assert receipt_data.currency == "EUR"

def test_receipt_extractor_agent_vendor_cleanup():
    ocr_text = """
    STARBUCKS COFFEE RECEIPT #12345
    DATE 07/27/2025
    TOTAL $10.00
    """
    agent = ReceiptExtractorAgent()
    receipt_data = agent.extract_receipt_data(ocr_text, "starbucks.jpeg", "id1")
    assert receipt_data is not None
    assert receipt_data.vendor_name == "STARBUCKS COFFEE" # Should clean up "RECEIPT #12345"

 * Update tests/test_agents.py (Add a test for TransactionInterpretationAgent.process_receipt_data):
   # tests/test_agents.py (Add to existing tests)
# ... (existing imports)
from app.schemas import ExtractedTransaction, NormalizedTransaction, ReceiptData # Ensure ReceiptData is imported
from app.agents.receipt_extractor_agent import ReceiptExtractorAgent # Import new agent for mocking if needed

# ... (existing fixtures and tests for TransactionInterpretationAgent.process_extracted_transactions)

def test_transaction_interpretation_agent_processes_receipt_data():
    """
    Test that TransactionInterpretationAgent correctly converts ReceiptData
    into a NormalizedTransaction.
    """
    agent = TransactionInterpretationAgent()
    receipt_data = ReceiptData(
        receipt_id="rcpt-1",
        vendor_name="Bookworm Cafe",
        transaction_date=date(2025, 7, 28),
        total_amount=25.50,
        currency="USD",
        line_items=[{"item": "Book", "price": 20.00}, {"item": "Coffee", "price": 5.50}],
        image_path="bookworm_receipt.jpeg",
        ocr_raw_text="Some OCR text"
    )

    normalized_tx = agent.process_receipt_data(receipt_data)

    assert normalized_tx is not None
    assert normalized_tx.transaction_id == "rcpt-1"
    assert normalized_tx.date == date(2025, 7, 28)
    assert normalized_tx.description == "Bookworm Cafe - Book" # Vendor + first line item
    assert normalized_tx.amount == -25.50 # Should be negative for debit
    assert normalized_tx.transaction_type == "Debit"
    assert normalized_tx.original_source_file == "bookworm_receipt.jpeg"
    assert "Extracted 2 line items." in normalized_tx.processing_notes

def test_transaction_interpretation_agent_skips_invalid_receipt_data():
    """Test agent skips if critical receipt data is missing."""
    agent = TransactionInterpretationAgent()
    # Missing total_amount
    receipt_data = ReceiptData(
        receipt_id="rcpt-fail",
        vendor_name="No Total Store",
        transaction_date=date(2025, 7, 29),
        total_amount=None, # This should cause failure
        currency="USD",
        line_items=[],
        image_path="no_total.jpeg",
        ocr_raw_text="Text"
    )

    normalized_tx = agent.process_receipt_data(receipt_data)
    assert normalized_tx is None

 * Update tests/test_main_e2e.py (Add a test for JPEG/PNG upload):
   # tests/test_main_e2e.py (Add a new test case)
# ... (existing imports and fixtures)

# Use the existing dummy_jpeg_bytes fixture if it's functional
# If not, create a very minimal JPEG byte string
@pytest.fixture
def tiny_jpeg_bytes():
    from PIL import Image
    import io
    # Create a tiny 1x1 red JPEG image
    img = Image.new('RGB', (1, 1), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

@pytest.mark.asyncio
async def test_e2e_jpeg_receipt_upload_process_download(async_client, caplog, tiny_jpeg_bytes):
    """
    Tests the complete pipeline for a JPEG receipt: upload -> check status -> download.
    This relies heavily on Tesseract OCR being functional in the test environment.
    For this test, we'll mock pytesseract.image_to_string to return a controlled
    receipt text so the extraction logic is tested robustly without external setup.
    """
    file_content = tiny_jpeg_bytes # Actual image bytes
    file_name = "test_receipt.jpeg"

    # MOCK PYTESSERACT to return a predictable receipt text
    mock_ocr_text = """
    GROCERY MART
    123 Market Street
    Date: 2025-07-29
    Milk $4.00
    Bread $3.50
    Eggs $2.00
    TOTAL $9.50
    """

    with patch('app.tools.ocr_tool.pytesseract.image_to_string', return_value=mock_ocr_text):
        logging.info("E2E: MOCKING pytesseract.image_to_string for JPEG receipt test.")

        # Step 1: Upload the file
        response = await async_client.post(
            "/upload_statement",
            files={"file": (file_name, file_content, "image/jpeg")},
            data={"quickbooks_csv_format": "3-column", "date_format": "MM/DD/YYYY"}
        )
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        logging.info(f"E2E: Uploaded JPEG, Job ID: {job_id}")

        # Step 2: Poll status until completion
        timeout_seconds = 10 
        start_time = datetime.now()
        while True:
            status_response = await async_client.get(f"/status/{job_id}")
            assert status_response.status_code == 200
            status_data = status_response.json()
            logging.info(f"E2E: Job {job_id} Status: {status_data['status']}, Progress: {status_data['progress']:.2f}")

            if status_data["status"] == "COMPLETED":
                assert status_data["download_url"] is not None
                assert len(status_data["preview_data"]) > 0 # Expect at least one transaction
                assert status_data["preview_data"][0]["description"] == "GROCERY MART - Milk" # Verify content from mock
                assert status_data["preview_data"][0]["amount"] == -9.50 # Verify total amount is negative
                logging.info(f"E2E: Job {job_id} COMPLETED for JPEG. Preview: {status_data['preview_data']}")
                break
            elif status_data["status"] == "FAILED":
                pytest.fail(f"Job {job_id} FAILED: {status_data['errors']}")

            await asyncio.sleep(0.5)
            if (datetime.now() - start_time).total_seconds() > timeout_seconds:
                pytest.fail(f"Job {job_id} did not complete within {timeout_seconds} seconds for JPEG. Current status: {status_data['status']}")

        # Step 3: Download the generated CSV
        download_url = status_data["download_url"]
        download_response = await async_client.get(download_url)
        assert download_response.status_code == 200
        assert "text/csv" in download_response.headers["content-type"]

        downloaded_content = download_response.text
        assert "Date,Description,Amount" in downloaded_content # Assuming 3-column format
        assert "GROCERY MART - Milk,-9.50" in downloaded_content # Check for extracted data in CSV
        logging.info(f"E2E: Downloaded JPEG CSV content verified for Job ID: {job_id}")

With these additions, your application will be capable of handling receipt images with structured extraction, seamlessly integrating them into your existing QuickBooks CSV generation pipeline.
Next Steps for You:
 * Implement app/agents/receipt_extractor_agent.py: Create the new file and add the content.
 * Update app/agents/transaction_interpretation_agent.py: Add the process_receipt_data method and import ReceiptData.
 * Update app/main.py: Add the ReceiptExtractorAgent global instance and modify _process_statement_background to include the conditional logic for image processing.
 * Create tests/test_receipt_agent.py: Add the unit tests for the new agent.
 * Update tests/test_agents.py: Add the new test for TransactionInterpretationAgent.process_receipt_data.
 * Update tests/test_main_e2e.py: Add the new end-to-end test for JPEG receipt processing (remembering the patch for pytesseract.image_to_string for reliable testing).
 * Run all tests (pytest) to ensure everything is working correctly and no regressions have been introduced.
Let me know when you've tackled these steps, and we'll be ready for the final touches!
