"""
Transaction Interpretation Agent for processing extracted transaction data.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from datetime import date

from afsp_app.app.schemas import RawTransactionData, ExtractedTransaction, NormalizedTransaction
from afsp_app.app.tools.date_parser import parse_date_robustly, extract_dates_from_text
from afsp_app.app.tools.amount_parser import parse_amount_and_type
from afsp_app.app.tools.description_cleaner import clean_description, categorize_description

# Configure logging
logger = logging.getLogger(__name__)


class TransactionInterpretationAgent:
    """
    Agent responsible for interpreting raw transaction data into normalized transactions.
    Orchestrates date parsing, amount parsing, description cleaning, and categorization.
    """
    
    def process_raw_transactions(self, raw_data_list: List[RawTransactionData]) -> List[NormalizedTransaction]:
        """
        Process a list of raw transaction data into normalized transactions.
        
        Args:
            raw_data_list: List of RawTransactionData objects
            
        Returns:
            List of NormalizedTransaction objects
        """
        normalized_transactions = []
        
        for raw_data in raw_data_list:
            # First extract fields
            extracted_transaction = self._extract_transaction_fields(raw_data)
            
            if extracted_transaction is None:
                logger.warning(f"Could not extract transaction fields from raw data: {raw_data.raw_text[:100]}...")
                continue
            
            # Then normalize the extracted transaction
            normalized_transaction = self._normalize_transaction(extracted_transaction, raw_data)
            
            if normalized_transaction is not None:
                normalized_transactions.append(normalized_transaction)
        
        return normalized_transactions
    
    def _extract_transaction_fields(self, raw_data: RawTransactionData) -> Optional[ExtractedTransaction]:
        """
        Extract transaction fields from raw data.
        
        Args:
            raw_data: RawTransactionData object
            
        Returns:
            ExtractedTransaction object or None if extraction failed
        """
        try:
            raw_text = raw_data.raw_text
            extraction_errors = []
            confidence_scores = {}
            
            # Check if raw_text is in JSON format
            if raw_text.strip().startswith('{') and raw_text.strip().endswith('}'):
                try:
                    import json
                    json_data = json.loads(raw_text)
                    
                    # Handle structured data from CSV
                    potential_date_str = json_data.get("Date", None)
                    potential_description_str = json_data.get("Description", None)
                    potential_amount_str = json_data.get("Amount", None)
                    potential_credit_str = json_data.get("Credit", None)
                    potential_debit_str = json_data.get("Debit", None)
                    
                    confidence_scores["date"] = 0.95 if potential_date_str else 0.0
                    confidence_scores["description"] = 0.95 if potential_description_str else 0.0
                    confidence_scores["amount"] = 0.95 if potential_amount_str else 0.0
                    
                    if not potential_date_str:
                        extraction_errors.append("No date found in JSON data")
                    if not potential_description_str:
                        extraction_errors.append("No description found in JSON data")
                    if not potential_amount_str and not potential_credit_str and not potential_debit_str:
                        extraction_errors.append("No amount found in JSON data")
                    
                    # Create and return the extracted transaction
                    # Add CSV context to amount string to help the parser
                    amount_str = str(potential_amount_str) if potential_amount_str else None
                    if amount_str:
                        amount_str = f"CSV:{amount_str}"
                    
                    return ExtractedTransaction(
                        raw_text_reference=raw_text,
                        potential_date_str=potential_date_str,
                        potential_description_str=potential_description_str,
                        potential_amount_str=amount_str,
                        potential_credit_str=str(potential_credit_str) if potential_credit_str else None,
                        potential_debit_str=str(potential_debit_str) if potential_debit_str else None,
                        confidence_score=confidence_scores,
                        extraction_errors=extraction_errors
                    )
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, continue with regular text extraction
                    pass
            
            # Extract potential date from text
            potential_dates = extract_dates_from_text(raw_text)
            potential_date_str = potential_dates[0] if potential_dates else None
            
            if potential_date_str:
                confidence_scores["date"] = 0.8
            else:
                extraction_errors.append("No date found")
                confidence_scores["date"] = 0.0
            
            # Extract potential amounts
            # Look for patterns that might be amounts
            amount_patterns = [
                # Matches currency symbol followed by digits, optional decimal part
                r'[$£€¥]\s*[\d,]+\.?\d*',
                # Matches digits with optional commas and decimal part
                r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b',
                # Matches digits with optional thousands separators
                r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\b',
                # Matches negative amounts with parentheses
                r'\(\$?[\d,]+\.?\d*\)',
                # Matches negative amounts with minus sign
                r'-\$?[\d,]+\.?\d*',
            ]
            
            potential_amounts = []
            for pattern in amount_patterns:
                matches = re.findall(pattern, raw_text)
                potential_amounts.extend(matches)
            
            # Try to identify if separate credit/debit columns exist
            potential_credit_str = None
            potential_debit_str = None
            potential_amount_str = None
            
            # Check for debit/credit columns pattern
            debit_credit_pattern = r'(debit|dr)[\s:]*([^cr]*)(credit|cr)[\s:]*([^\n]*)'
            debit_credit_match = re.search(debit_credit_pattern, raw_text, re.IGNORECASE)
            
            if debit_credit_match:
                potential_debit_str = debit_credit_match.group(2).strip()
                potential_credit_str = debit_credit_match.group(4).strip()
                confidence_scores["amount"] = 0.9
            elif potential_amounts:
                potential_amount_str = potential_amounts[0]
                confidence_scores["amount"] = 0.7
            else:
                extraction_errors.append("No amount found")
                confidence_scores["amount"] = 0.0
            
            # Extract potential description
            # This is challenging as descriptions vary widely
            # Use some common patterns or just take text that's not a date or amount
            # For simplicity, we'll take the remaining text after removing dates and amounts
            description_text = raw_text
            
            # Remove dates
            for date_str in potential_dates:
                description_text = description_text.replace(date_str, "")
            
            # Remove amounts
            for amount_str in potential_amounts:
                description_text = description_text.replace(amount_str, "")
            
            # Clean up the description
            potential_description_str = re.sub(r'\s+', ' ', description_text).strip()
            
            if potential_description_str:
                confidence_scores["description"] = 0.6
            else:
                extraction_errors.append("No description found")
                confidence_scores["description"] = 0.0
            
            return ExtractedTransaction(
                raw_text_reference=raw_text,
                potential_date_str=potential_date_str,
                potential_description_str=potential_description_str,
                potential_amount_str=potential_amount_str,
                potential_credit_str=potential_credit_str,
                potential_debit_str=potential_debit_str,
                confidence_score=confidence_scores,
                extraction_errors=extraction_errors
            )
        
        except Exception as e:
            logger.error(f"Error extracting transaction fields: {str(e)}")
            return None
    
    def _normalize_transaction(self, extracted: ExtractedTransaction, raw_data: RawTransactionData) -> Optional[NormalizedTransaction]:
        """
        Normalize an extracted transaction into a standardized format.
        
        Args:
            extracted: ExtractedTransaction object
            raw_data: Original RawTransactionData object
            
        Returns:
            NormalizedTransaction object or None if normalization failed
        """
        try:
            processing_notes = []
            
            # Parse date
            parsed_date = None
            if extracted.potential_date_str:
                parsed_date = parse_date_robustly(extracted.potential_date_str)
                if parsed_date:
                    processing_notes.append(f"Date parsed from: {extracted.potential_date_str}")
                else:
                    processing_notes.append(f"Failed to parse date: {extracted.potential_date_str}")
            
            if not parsed_date:
                logger.warning("No valid date found in transaction")
                return None
            
            # Parse amount and determine transaction type
            amount, transaction_type = parse_amount_and_type(
                extracted.potential_amount_str,
                extracted.potential_credit_str,
                extracted.potential_debit_str
            )
            
            if amount is None or transaction_type is None:
                logger.warning("No valid amount found in transaction")
                processing_notes.append("Failed to parse amount")
                return None
            
            processing_notes.append(
                f"Amount parsed from: {extracted.potential_amount_str or extracted.potential_credit_str or extracted.potential_debit_str}"
            )
            
            # Clean description
            description = ""
            if extracted.potential_description_str:
                description = clean_description(extracted.potential_description_str)
                processing_notes.append(f"Description cleaned from: {extracted.potential_description_str}")
            
            if not description:
                description = "Unknown Transaction"
                processing_notes.append("Used default description due to missing or invalid description")
            
            # Create normalized transaction
            return NormalizedTransaction(
                date=parsed_date,
                description=description,
                amount=amount,
                transaction_type=transaction_type,
                original_source_file=raw_data.source_file_name,
                processing_notes=processing_notes
            )
        
        except Exception as e:
            logger.error(f"Error normalizing transaction: {str(e)}")
            return None
