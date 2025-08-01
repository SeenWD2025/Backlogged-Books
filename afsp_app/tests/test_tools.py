"""
Tests for the tools module.
Tests functionality of the individual tools used by agents.
"""

import pytest
from datetime import date, datetime
import os
from pathlib import Path

from app.tools.date_parser import parse_date_robustly, extract_dates_from_text, normalize_date_format
from app.tools.amount_parser import parse_amount_and_type, extract_numeric_amount
from app.tools.description_cleaner import clean_description, categorize_description


class TestDateParser:
    """Test suite for date parser tool."""
    
    def test_parse_date_robustly(self):
        """Test parsing dates in various formats."""
        # Test standard formats
        assert parse_date_robustly("07/31/2025") == date(2025, 7, 31)
        assert parse_date_robustly("31/07/2025") == date(2025, 7, 31)
        assert parse_date_robustly("2025-07-31") == date(2025, 7, 31)
        
        # Test with text
        assert parse_date_robustly("Date: July 31, 2025") == date(2025, 7, 31)
        assert parse_date_robustly("31 Jul 2025") == date(2025, 7, 31)
        
        # Test invalid dates
        assert parse_date_robustly("not a date") is None
        assert parse_date_robustly("") is None
        assert parse_date_robustly(None) is None
    
    def test_extract_dates_from_text(self):
        """Test extracting date strings from text."""
        text = "Transaction date: 07/31/2025. Posted on 08/01/2025. Receipt from January 15, 2025."
        dates = extract_dates_from_text(text)
        
        assert len(dates) == 3
        assert "07/31/2025" in dates
        assert "08/01/2025" in dates
        assert "January 15, 2025" in dates
        
        # Test with no dates
        assert extract_dates_from_text("No dates in this text") == []
        
        # Test with empty text
        assert extract_dates_from_text("") == []
        assert extract_dates_from_text(None) == []
    
    def test_normalize_date_format(self):
        """Test normalizing date format."""
        test_date = date(2025, 7, 31)
        
        # Test MM/DD/YYYY format
        assert normalize_date_format(test_date, "MM/DD/YYYY") == "07/31/2025"
        
        # Test DD/MM/YYYY format
        assert normalize_date_format(test_date, "DD/MM/YYYY") == "31/07/2025"
        
        # Test invalid format
        assert normalize_date_format(test_date, "invalid") == "07/31/2025"
        
        # Test None date
        assert normalize_date_format(None, "MM/DD/YYYY") == ""


class TestAmountParser:
    """Test suite for amount parser tool."""
    
    def test_parse_amount_and_type(self):
        """Test parsing amounts and determining transaction type."""
        # Test with combined amount string
        amount, type_ = parse_amount_and_type("$123.45")
        assert amount == -123.45  # Default to debit
        assert type_ == "Debit"
        
        # Test with negative amount string
        amount, type_ = parse_amount_and_type("-$123.45")
        assert amount == -123.45
        assert type_ == "Debit"
        
        # Test with credit indicators
        amount, type_ = parse_amount_and_type("Credit: $123.45")
        assert amount == 123.45
        assert type_ == "Credit"
        
        # Test with debit indicators
        amount, type_ = parse_amount_and_type("Debit: $123.45")
        assert amount == -123.45
        assert type_ == "Debit"
        
        # Test with separate credit/debit columns
        amount, type_ = parse_amount_and_type(None, "$123.45", None)
        assert amount == 123.45
        assert type_ == "Credit"
        
        amount, type_ = parse_amount_and_type(None, None, "$123.45")
        assert amount == -123.45
        assert type_ == "Debit"
        
        # Test with invalid inputs
        amount, type_ = parse_amount_and_type("not an amount")
        assert amount is None
        assert type_ is None
    
    def test_extract_numeric_amount(self):
        """Test extracting numeric amounts from strings."""
        # Test US format
        assert extract_numeric_amount("$123.45") == 123.45
        assert extract_numeric_amount("$1,234.56") == 1234.56
        
        # Test European format
        assert extract_numeric_amount("123,45") == 123.45
        assert extract_numeric_amount("1.234,56") == 1234.56
        
        # Test negative amounts
        assert extract_numeric_amount("-123.45") == -123.45
        assert extract_numeric_amount("($123.45)") == -123.45
        
        # Test invalid inputs
        assert extract_numeric_amount("not a number") is None
        assert extract_numeric_amount("") is None
        assert extract_numeric_amount(None) is None


class TestDescriptionCleaner:
    """Test suite for description cleaner tool."""
    
    def test_clean_description(self):
        """Test cleaning transaction descriptions."""
        # Test removing prefixes
        assert clean_description("POS TRANSACTION Amazon") == "Amazon"
        assert clean_description("DEBIT CARD PURCHASE WALMART") == "Walmart"
        
        # Test normalizing merchant names
        assert clean_description("AMZN MKTP US") == "Amazon Marketplace Us"
        assert clean_description("WM SUPERCENTER") == "Walmart"
        
        # Test removing transaction IDs
        assert clean_description("STARBUCKS #12345") == "Starbucks"
        assert clean_description("UBER EATS REF #987654") == "Uber Eats"
        
        # Test with empty input
        assert clean_description("") == ""
        assert clean_description(None) == ""
    
    def test_categorize_description(self):
        """Test categorizing descriptions."""
        # Test grocery category
        assert categorize_description("Walmart Grocery") == "Groceries"
        assert categorize_description("Kroger") == "Groceries"
        
        # Test dining category
        assert categorize_description("Starbucks") == "Dining"
        assert categorize_description("McDonald's") == "Dining"
        
        # Test transportation category
        assert categorize_description("Shell Gas") == "Transportation"
        assert categorize_description("Uber") == "Transportation"
        
        # Test uncategorized
        assert categorize_description("Some Random Store") == "Uncategorized"
        assert categorize_description("") == "Uncategorized"
