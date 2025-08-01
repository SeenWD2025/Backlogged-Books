"""
Amount Parser Tool for extracting and normalizing monetary amounts from text.
"""

import re
import logging
from typing import Optional, Tuple, Literal

# Configure logging
logger = logging.getLogger(__name__)


def parse_amount_and_type(
    potential_amount_str: Optional[str] = None,
    potential_credit_str: Optional[str] = None,
    potential_debit_str: Optional[str] = None
) -> Tuple[Optional[float], Optional[Literal["Credit", "Debit"]]]:
    """
    Parse amount and determine transaction type from various input formats.
    
    Args:
        potential_amount_str: Combined amount string (positive or negative)
        potential_credit_str: Credit amount string (positive only)
        potential_debit_str: Debit amount string (positive only)
        
    Returns:
        Tuple of (parsed_amount, transaction_type)
        Amount is positive for Credit and negative for Debit
    """
    # First check if we have separate credit/debit columns
    if potential_credit_str:
        try:
            amount = extract_numeric_amount(potential_credit_str)
            if amount is not None and amount != 0:
                return abs(amount), "Credit"
        except ValueError:
            pass
    
    if potential_debit_str:
        try:
            amount = extract_numeric_amount(potential_debit_str)
            if amount is not None and amount != 0:
                return -abs(amount), "Debit"
        except ValueError:
            pass
    
    # If no credit/debit specific columns, try the combined amount
    if potential_amount_str:
        try:
            # Check for indicators of credit/debit type
            is_credit = contains_credit_indicators(potential_amount_str)
            is_debit = contains_debit_indicators(potential_amount_str)
            
            # Extract the numeric value
            amount = extract_numeric_amount(potential_amount_str)
            
            if amount is None:
                return None, None
            
            # Determine sign and type based on indicators or sign
            if amount < 0 or is_debit:
                return -abs(amount), "Debit"
            elif is_credit:
                return abs(amount), "Credit"
            else:
                # Check if this is from a structured CSV file
                if potential_amount_str and potential_amount_str.startswith("CSV:"):
                    # Extract the actual amount from the CSV prefix format
                    csv_amount_str = potential_amount_str.replace("CSV:", "")
                    try:
                        csv_amount = float(csv_amount_str.replace(",", ""))
                        # For CSV files with structured data, respect the sign
                        # Positive values are typically credits, negative are debits
                        if csv_amount > 0:
                            return csv_amount, "Credit"  # Keep as Credit
                        else:
                            return csv_amount, "Debit"  # Already negative, keep as Debit
                    except ValueError:
                        # If we can't parse the CSV amount, fall back to the extracted amount
                        if amount > 0:
                            return amount, "Credit"
                        else:
                            return amount, "Debit"
                else:
                    # For unstructured text, we default to Debit for positive amounts
                    # since most transactions are expenses
                    if amount > 0:
                        return -amount, "Debit"  # Invert and mark as Debit
                    else:
                        return amount, "Debit"
                    
        except ValueError:
            pass
    
    return None, None


def extract_numeric_amount(amount_str: str) -> Optional[float]:
    """
    Extract numeric value from a string, handling currency symbols, commas, etc.
    
    Args:
        amount_str: String containing a monetary amount
        
    Returns:
        Float value of the amount or None if extraction failed
    """
    if not amount_str or not isinstance(amount_str, str):
        return None
    
    # Clean up the string
    cleaned = amount_str.strip()
    
    # Check if it contains parentheses which often indicate negative numbers
    is_negative = "(" in cleaned and ")" in cleaned
    if is_negative:
        cleaned = cleaned.replace("(", "").replace(")", "")
    
    # Remove currency symbols and other non-numeric characters except . and ,
    # Keep - for negative numbers
    cleaned = re.sub(r'[^\d\.\,\-]', '', cleaned)
    
    # Handle European vs US number formatting (1.234,56 vs 1,234.56)
    if ',' in cleaned and '.' in cleaned:
        # Determine which is the decimal separator based on position
        last_comma = cleaned.rindex(',')
        last_dot = cleaned.rindex('.')
        
        if last_comma > last_dot:
            # European format: 1.234,56
            cleaned = cleaned.replace('.', '')  # Remove thousand separators
            cleaned = cleaned.replace(',', '.')  # Convert decimal separator
        else:
            # US format: 1,234.56
            cleaned = cleaned.replace(',', '')  # Remove thousand separators
    elif ',' in cleaned and '.' not in cleaned:
        # Could be either 1,234 (US) or 1,23 (European)
        if len(cleaned) - cleaned.rindex(',') <= 3:
            # Likely European decimal: 1,23
            cleaned = cleaned.replace(',', '.')
        else:
            # Likely US thousands: 1,234
            cleaned = cleaned.replace(',', '')
    
    try:
        amount = float(cleaned)
        
        # Apply negative if it was in parentheses
        if is_negative:
            amount = -abs(amount)
            
        return amount
    except ValueError:
        logger.warning(f"Failed to convert '{amount_str}' to a number")
        return None


def contains_credit_indicators(text: str) -> bool:
    """
    Check if text contains indicators that it's a credit transaction.
    
    Args:
        text: Text to check
        
    Returns:
        True if it contains credit indicators, False otherwise
    """
    indicators = [
        'credit', 'deposit', 'refund', 'payment received', 'cr', 'incoming',
        'salary', 'interest', 'reimbursement'
    ]
    
    lower_text = text.lower()
    return any(indicator in lower_text for indicator in indicators)


def contains_debit_indicators(text: str) -> bool:
    """
    Check if text contains indicators that it's a debit transaction.
    
    Args:
        text: Text to check
        
    Returns:
        True if it contains debit indicators, False otherwise
    """
    indicators = [
        'debit', 'payment', 'withdrawal', 'purchase', 'dr', 'outgoing',
        'fee', 'charge', 'bill', 'invoice'
    ]
    
    lower_text = text.lower()
    return any(indicator in lower_text for indicator in indicators)
