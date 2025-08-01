"""
Receipt Extractor Agent for processing receipt images.
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from afsp_app.app.schemas import RawTransactionData, ReceiptData
from afsp_app.app.tools.date_parser import parse_date_robustly, extract_dates_from_text
from afsp_app.app.tools.amount_parser import extract_numeric_amount

# Configure logging
logger = logging.getLogger(__name__)


class ReceiptExtractorAgent:
    """
    Agent responsible for extracting structured data from receipt OCR text.
    Uses regex and pattern matching to identify receipt fields.
    """
    
    def process_receipt(self, raw_data: RawTransactionData, image_path: str) -> Optional[ReceiptData]:
        """
        Process a receipt from raw OCR data.
        
        Args:
            raw_data: RawTransactionData containing OCR text
            image_path: Path to the receipt image
            
        Returns:
            ReceiptData object or None if extraction failed
        """
        try:
            ocr_text = raw_data.raw_text
            
            # Extract vendor name
            vendor_name = self._extract_vendor_name(ocr_text)
            
            # Extract date
            transaction_date = self._extract_date(ocr_text)
            
            # Extract total amount
            total_amount = self._extract_total_amount(ocr_text)
            
            # Extract line items
            line_items = self._extract_line_items(ocr_text)
            
            # Extract currency
            currency = self._extract_currency(ocr_text)
            
            # Suggest category
            category = self._suggest_category(vendor_name, line_items)
            
            # Create ReceiptData object
            if vendor_name and transaction_date and total_amount:
                return ReceiptData(
                    vendor_name=vendor_name,
                    transaction_date=transaction_date,
                    total_amount=total_amount,
                    currency=currency,
                    line_items=line_items,
                    category_suggestion=category,
                    image_path=image_path,
                    ocr_raw_text=ocr_text
                )
            else:
                logger.warning("Missing required fields for receipt data")
                return None
                
        except Exception as e:
            logger.error(f"Error processing receipt: {str(e)}")
            return None
    
    def _extract_vendor_name(self, text: str) -> str:
        """
        Extract vendor name from receipt text.
        
        Args:
            text: OCR text from receipt
            
        Returns:
            Vendor name or default value if not found
        """
        # Vendor name is usually at the top of the receipt
        # Try to find it in the first few lines
        lines = text.split('\n')
        
        # Look for the first non-empty line that's not a date
        for i in range(min(5, len(lines))):
            line = lines[i].strip()
            
            # Skip empty lines or lines that might be dates
            if not line or re.search(r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}', line):
                continue
            
            # Skip if line is just numbers (like a phone number)
            if re.match(r'^[\d\-\.\(\)\s]+$', line):
                continue
                
            return line
        
        # If no good candidate found in first few lines, check for common patterns
        vendor_patterns = [
            r'(?i)(?:store|merchant|vendor)[:\s]+([^\n]+)',
            r'(?i)(?:welcome to|thank you for shopping at)[:\s]+([^\n]+)'
        ]
        
        for pattern in vendor_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return "Unknown Vendor"
    
    def _extract_date(self, text: str) -> datetime.date:
        """
        Extract transaction date from receipt text.
        
        Args:
            text: OCR text from receipt
            
        Returns:
            Transaction date or today's date if not found
        """
        # Extract potential dates
        dates = extract_dates_from_text(text)
        
        if dates:
            # Try to parse each potential date
            for date_str in dates:
                parsed_date = parse_date_robustly(date_str)
                if parsed_date:
                    return parsed_date
        
        # If no date found, look for specific patterns
        date_patterns = [
            r'(?i)(?:date|time)[:\s]+([^\n]+)',
            r'(?i)(?:receipt|invoice|transaction)[:\s]+([^\n]+)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                potential_date = match.group(1).strip()
                parsed_date = parse_date_robustly(potential_date)
                if parsed_date:
                    return parsed_date
        
        # If still no date found, use today's date
        logger.warning("No date found in receipt, using today's date")
        return datetime.now().date()
    
    def _extract_total_amount(self, text: str) -> float:
        """
        Extract total amount from receipt text.
        
        Args:
            text: OCR text from receipt
            
        Returns:
            Total amount or 0.0 if not found
        """
        # Look for common patterns for total amount
        total_patterns = [
            r'(?i)total[:\s]+[\$£€]?([0-9,]+\.[0-9]{2})',
            r'(?i)(?:amount|sum|grand total|payment)[:\s]+[\$£€]?([0-9,]+\.[0-9]{2})',
            r'(?i)(?:total|amount|sum)[:\s]+[\$£€]?([0-9,]+\.[0-9]{2})',
            # Common misspellings or OCR errors
            r'(?i)(?:totai|totol|t0tal|tota1)[:\s]+[\$£€]?([0-9,]+\.[0-9]{2})',
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).strip()
                amount = extract_numeric_amount(amount_str)
                if amount is not None:
                    return amount
        
        # If no patterns matched, look for amount at the end of the receipt
        # Total is usually one of the last numbers on the receipt
        amount_matches = re.findall(r'[\$£€]?([0-9,]+\.[0-9]{2})', text)
        if amount_matches:
            # Try amounts from the last quarter of the receipt first
            last_quarter = amount_matches[-max(len(amount_matches)//4, 1):]
            for amount_str in last_quarter:
                amount = extract_numeric_amount(amount_str)
                if amount is not None and amount > 0:
                    return amount
        
        logger.warning("No total amount found in receipt")
        return 0.0
    
    def _extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract line items from receipt text.
        
        Args:
            text: OCR text from receipt
            
        Returns:
            List of line item dictionaries
        """
        line_items = []
        
        # This is a complex task and varies greatly by receipt format
        # For a basic implementation, we'll look for patterns like:
        # Item name followed by price, possibly with quantity
        
        # Split text into lines
        lines = text.split('\n')
        
        # Look for lines that match item pattern
        item_pattern = r'(.*?)\s+(\d+(?:\.\d+)?)\s*[xX]\s*[\$£€]?(\d+(?:\.\d+)?)\s*[\$£€]?(\d+(?:\.\d+)?)'
        simple_pattern = r'(.*?)\s+[\$£€]?(\d+(?:\.\d+)?)\s*$'
        
        in_items_section = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this line indicates the start of items section
            if re.search(r'(?i)(?:item|description|qty|quantity|price|amount)', line):
                in_items_section = True
                continue
            
            # Check if this line indicates the end of items section
            if in_items_section and re.search(r'(?i)(?:subtotal|tax|total|balance|payment)', line):
                in_items_section = False
                continue
            
            # Try to match item patterns
            match = re.match(item_pattern, line)
            if match:
                item_name = match.group(1).strip()
                quantity = float(match.group(2))
                unit_price = float(match.group(3))
                total_price = float(match.group(4))
                
                line_items.append({
                    "item": item_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price
                })
                continue
            
            # Try simpler pattern (just item and price)
            if in_items_section or len(line_items) > 0:
                match = re.match(simple_pattern, line)
                if match:
                    item_name = match.group(1).strip()
                    price = float(match.group(2))
                    
                    line_items.append({
                        "item": item_name,
                        "quantity": 1,
                        "unit_price": price,
                        "total_price": price
                    })
        
        return line_items
    
    def _extract_currency(self, text: str) -> str:
        """
        Extract currency from receipt text.
        
        Args:
            text: OCR text from receipt
            
        Returns:
            Currency code or "USD" if not found
        """
        # Look for currency symbols
        currency_map = {
            '$': 'USD',
            '£': 'GBP',
            '€': 'EUR',
            '¥': 'JPY',
            'CHF': 'CHF',
            'CAD': 'CAD',
            'AUD': 'AUD',
        }
        
        for symbol, code in currency_map.items():
            if symbol in text:
                return code
        
        # Default to USD
        return "USD"
    
    def _suggest_category(self, vendor_name: str, line_items: List[Dict[str, Any]]) -> str:
        """
        Suggest a category based on vendor name and line items.
        
        Args:
            vendor_name: Name of the vendor
            line_items: List of line items
            
        Returns:
            Suggested category
        """
        # Convert to lowercase for matching
        vendor_lower = vendor_name.lower()
        
        # Define category mappings based on keywords
        category_mapping = {
            "Groceries": ["grocery", "market", "food", "kroger", "walmart", "target", 
                          "trader joe", "whole foods", "safeway", "costco", "aldi", 
                          "supermarket"],
            "Dining": ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "burger", 
                       "pizza", "taco", "sushi", "doordash", "uber eats", "grubhub"],
            "Transportation": ["gas", "fuel", "uber", "lyft", "taxi", "transit", "parking", 
                              "tolls", "metro", "subway", "train", "bus"],
            "Utilities": ["electric", "water", "gas bill", "utility", "internet", "phone", 
                         "mobile", "wifi", "cable"],
            "Entertainment": ["movie", "theatre", "theater", "cinema", "concert", "ticket", 
                             "show", "game", "entertainment"],
            "Shopping": ["amazon", "ebay", "etsy", "clothing", "fashion", "apparel", 
                        "electronics", "department store"],
            "Health": ["doctor", "medical", "pharmacy", "prescription", "dental", "vision", 
                      "fitness", "gym", "healthcare", "drugstore", "walgreens", "cvs"],
            "Education": ["tuition", "school", "college", "university", "course", "class", 
                         "book", "education"],
            "Office Supplies": ["office", "supplies", "staples", "paper", "ink", "printer", 
                              "toner"]
        }
        
        # Check vendor name against category keywords
        for category, keywords in category_mapping.items():
            if any(keyword in vendor_lower for keyword in keywords):
                return category
        
        # If no match by vendor, check line items
        if line_items:
            all_items = " ".join([item.get("item", "").lower() for item in line_items])
            
            for category, keywords in category_mapping.items():
                if any(keyword in all_items for keyword in keywords):
                    return category
        
        # Default category if no match
        return "Uncategorized"
