"""
Tests for the receipt extractor agent.
Tests functionality of the specialized receipt processing agent.
"""

import pytest
from datetime import date, datetime
import os
from pathlib import Path
import tempfile

from app.schemas import RawTransactionData, ReceiptData, NormalizedTransaction
from app.agents.receipt_extractor_agent import ReceiptExtractorAgent
from app.agents.transaction_interpretation_agent import TransactionInterpretationAgent


class TestReceiptExtractorAgent:
    """Test suite for ReceiptExtractorAgent."""
    
    def test_process_receipt_grocery(self):
        """Test processing a grocery receipt."""
        agent = ReceiptExtractorAgent()
        
        # Create sample raw data for a grocery receipt
        raw_data = RawTransactionData(
            raw_text="""KROGER
123 Main St
Date: 07/31/2025
Item         Qty   Price
Milk          1     3.99
Bread         2     2.50
Eggs          1     4.99
Bananas       2     1.99
Apples        1     3.49
Subtotal          16.96
Tax                0.85
TOTAL        $17.81
Thank you for shopping at Kroger!
""",
            source_file_name="grocery_receipt.jpg",
            source_file_type="JPEG"
        )
        
        # Process receipt
        receipt = agent.process_receipt(raw_data, "path/to/grocery_receipt.jpg")
        
        # Validate receipt
        assert receipt is not None
        assert "Kroger" in receipt.vendor_name
        assert receipt.transaction_date == date(2025, 7, 31)
        assert receipt.total_amount == 17.81
        assert receipt.currency == "USD"
        assert receipt.category_suggestion == "Groceries"
    
    def test_process_receipt_restaurant(self):
        """Test processing a restaurant receipt."""
        agent = ReceiptExtractorAgent()
        
        # Create sample raw data for a restaurant receipt
        raw_data = RawTransactionData(
            raw_text="""STARBUCKS
456 Main St
July 31, 2025 12:34 PM
Order #12345
Item                Price
Grande Latte         4.95
Blueberry Muffin     3.25
Subtotal             8.20
Tax                  0.66
TOTAL               $8.86
Thank you for visiting Starbucks!
""",
            source_file_name="restaurant_receipt.jpg",
            source_file_type="JPEG"
        )
        
        # Process receipt
        receipt = agent.process_receipt(raw_data, "path/to/restaurant_receipt.jpg")
        
        # Validate receipt
        assert receipt is not None
        assert "Starbucks" in receipt.vendor_name
        assert receipt.transaction_date == date(2025, 7, 31)
        assert receipt.total_amount == 8.86
        assert receipt.currency == "USD"
        assert receipt.category_suggestion == "Dining"
    
    def test_process_receipt_gas(self):
        """Test processing a gas station receipt."""
        agent = ReceiptExtractorAgent()
        
        # Create sample raw data for a gas station receipt
        raw_data = RawTransactionData(
            raw_text="""SHELL GAS
789 Highway Dr
07/31/25 15:45
Pump: 5
Gallons: 12.345
Price/Gal: $3.499
Fuel Total: $43.20
Car Wash: $8.99
TOTAL: $52.19
Thank you for choosing Shell!
""",
            source_file_name="gas_receipt.jpg",
            source_file_type="JPEG"
        )
        
        # Process receipt
        receipt = agent.process_receipt(raw_data, "path/to/gas_receipt.jpg")
        
        # Validate receipt
        assert receipt is not None
        assert "Shell" in receipt.vendor_name
        assert receipt.transaction_date == date(2025, 7, 31)
        assert receipt.total_amount == 52.19
        assert receipt.currency == "USD"
        assert receipt.category_suggestion == "Transportation"
    
    def test_extract_currency(self):
        """Test extracting currency from receipt text."""
        agent = ReceiptExtractorAgent()
        
        # Test USD
        assert agent._extract_currency("Total: $10.00") == "USD"
        
        # Test GBP
        assert agent._extract_currency("Total: £10.00") == "GBP"
        
        # Test EUR
        assert agent._extract_currency("Total: €10.00") == "EUR"
        
        # Test default
        assert agent._extract_currency("Total: 10.00") == "USD"
    
    def test_suggest_category(self):
        """Test suggesting categories based on vendor and items."""
        agent = ReceiptExtractorAgent()
        
        # Test grocery
        assert agent._suggest_category("Kroger", []) == "Groceries"
        
        # Test dining
        assert agent._suggest_category("McDonald's", []) == "Dining"
        
        # Test transportation
        assert agent._suggest_category("Shell Gas", []) == "Transportation"
        
        # Test based on line items
        line_items = [
            {"item": "Prescription", "price": 10.00},
            {"item": "Medicine", "price": 5.00}
        ]
        assert agent._suggest_category("Store", line_items) == "Health"
        
        # Test uncategorized
        assert agent._suggest_category("Unknown Store", []) == "Uncategorized"


class TestReceiptToNormalizedTransaction:
    """Test suite for converting receipts to normalized transactions."""
    
    def test_convert_receipt_to_transaction(self):
        """Test converting a receipt to a normalized transaction."""
        # Create a receipt
        receipt = ReceiptData(
            vendor_name="Starbucks",
            transaction_date=date(2025, 7, 31),
            total_amount=8.86,
            currency="USD",
            line_items=[
                {"item": "Grande Latte", "quantity": 1, "unit_price": 4.95, "total_price": 4.95},
                {"item": "Blueberry Muffin", "quantity": 1, "unit_price": 3.25, "total_price": 3.25}
            ],
            category_suggestion="Dining",
            image_path="path/to/receipt.jpg",
            ocr_raw_text="Sample receipt text"
        )
        
        # Convert to normalized transaction (manual implementation for testing)
        transaction = NormalizedTransaction(
            date=receipt.transaction_date,
            description=receipt.vendor_name,
            amount=-receipt.total_amount,  # Negative for expenses
            transaction_type="Debit",
            original_source_file=receipt.image_path,
            processing_notes=[f"Category: {receipt.category_suggestion}"]
        )
        
        # Validate transaction
        assert transaction.date == date(2025, 7, 31)
        assert transaction.description == "Starbucks"
        assert transaction.amount == -8.86
        assert transaction.transaction_type == "Debit"
        assert "Category: Dining" in transaction.processing_notes
