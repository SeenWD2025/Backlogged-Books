"""
Date Parser Tool for extracting and normalizing dates from text.
Uses dateutil.parser for robust date extraction.
"""

from datetime import date
import logging
from typing import Optional
import re
from dateutil.parser import parse, ParserError

# Configure logging
logger = logging.getLogger(__name__)


def parse_date_robustly(date_str: str) -> Optional[date]:
    """
    Parse a date string into a date object, attempting multiple formats.
    
    Args:
        date_str: String containing a date
        
    Returns:
        Parsed date or None if parsing failed
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    # Clean up the input string
    date_str = date_str.strip()
    
    # Remove any non-alphanumeric characters from the end
    date_str = re.sub(r'[^\w\s/\-\.]+$', '', date_str)
    
    # Try parsing with dateutil.parser
    try:
        # Try MM/DD/YYYY format first (US format)
        parsed_date = parse(date_str, dayfirst=False)
        return parsed_date.date()
    except ParserError:
        try:
            # Try DD/MM/YYYY format (UK/Europe format)
            parsed_date = parse(date_str, dayfirst=True)
            return parsed_date.date()
        except ParserError:
            logger.warning(f"Could not parse date: {date_str}")
            return None
    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {str(e)}")
        return None


def extract_dates_from_text(text: str) -> list[str]:
    """
    Extract potential date strings from raw text using regex patterns.
    
    Args:
        text: Raw text that may contain dates
        
    Returns:
        List of potential date strings
    """
    if not text:
        return []
    
    # Common date patterns
    patterns = [
        # MM/DD/YYYY or DD/MM/YYYY
        r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b',
        # Month name formats: Jan 1, 2022 or January 1, 2022 or 1 Jan 2022
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b',
        # ISO format: YYYY-MM-DD
        r'\b\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2}\b',
    ]
    
    date_strings = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        date_strings.extend(matches)
    
    return date_strings


def normalize_date_format(date_obj: date, format_str: str) -> str:
    """
    Format a date object according to the specified format.
    
    Args:
        date_obj: Date object to format
        format_str: Format string ("MM/DD/YYYY" or "DD/MM/YYYY")
        
    Returns:
        Formatted date string
    """
    if not date_obj:
        return ""
    
    try:
        if format_str == "MM/DD/YYYY":
            return date_obj.strftime("%m/%d/%Y")
        elif format_str == "DD/MM/YYYY":
            return date_obj.strftime("%d/%m/%Y")
        else:
            logger.warning(f"Unsupported date format: {format_str}, using MM/DD/YYYY")
            return date_obj.strftime("%m/%d/%Y")
    except Exception as e:
        logger.error(f"Error formatting date {date_obj}: {str(e)}")
        return ""
