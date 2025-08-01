"""
Tests for the agents module.
Tests functionality of the agents that orchestrate the processing pipeline.
"""

import pytest
from datetime import date, datetime
import os
from pathlib import Path
import tempfile

from app.schemas import RawTransactionData, NormalizedTransaction
from app.agents.raw_data_extraction_agent import RawDataExtractionAgent
from app.agents.transaction_interpretation_agent import TransactionInterpretationAgent
from app.agents.quickbooks_formatter_agent import QuickBooksFormatterAgent
from app.agents.receipt_extractor_agent import ReceiptExtractorAgent


class TestRawDataExtractionAgent:
    """Test suite for RawDataExtractionAgent."""
    
    def test_extract_from_csv(self):
        """Test extracting data from a CSV file."""
        agent = RawDataExtractionAgent()
        
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp.write(b"Date,Description,Amount\n07/31/2025,Test Transaction,123.45")
            temp_path = temp.name
        
        try:
            # Extract data
            results = agent._extract_from_csv(temp_path)
            
            # Validate results
            assert len(results) > 0
            assert isinstance(results[0], RawTransactionData)
            assert results[0].source_file_type == "CSV"
            assert "Test Transaction" in results[0].raw_text
            
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_extract_from_non_existent_file(self):
        """Test extracting data from a non-existent file."""
        agent = RawDataExtractionAgent()
        
        # Create a non-existent file path
        non_existent_file = "non_existent_file.csv"
        
        # Extract data
        results = agent.extract_from_file(non_existent_file, "CSV")
        
        # Validate results
        assert len(results) == 0


class TestTransactionInterpretationAgent:
    """Test suite for TransactionInterpretationAgent."""
    
    def test_process_raw_transactions(self):
        """Test processing raw transactions into normalized transactions."""
        agent = TransactionInterpretationAgent()
        
        # Create sample raw data
        raw_data = RawTransactionData(
            raw_text="Date: 07/31/2025 Description: Test Transaction Amount: $123.45",
            source_file_name="test.csv",
            source_file_type="CSV"
        )
        
        # Process raw data
        results = agent.process_raw_transactions([raw_data])
        
        # Validate results
        assert len(results) > 0
        assert isinstance(results[0], NormalizedTransaction)
        assert results[0].date == date(2025, 7, 31)
        assert "Test Transaction" in results[0].description
        assert results[0].amount == -123.45  # Default to debit
        assert results[0].transaction_type == "Debit"
    
    def test_process_invalid_raw_transactions(self):
        """Test processing invalid raw transactions."""
        agent = TransactionInterpretationAgent()
        
        # Create sample invalid raw data
        raw_data = RawTransactionData(
            raw_text="No valid transaction data here",
            source_file_name="test.csv",
            source_file_type="CSV"
        )
        
        # Process raw data
        results = agent.process_raw_transactions([raw_data])
        
        # Validate results
        assert len(results) == 0


class TestQuickBooksFormatterAgent:
    """Test suite for QuickBooksFormatterAgent."""
    
    def test_generate_three_column_csv(self):
        """Test generating a 3-column CSV."""
        agent = QuickBooksFormatterAgent()
        
        # Create sample normalized transactions
        transactions = [
            NormalizedTransaction(
                date=date(2025, 7, 31),
                description="Test Transaction 1",
                amount=-123.45,
                transaction_type="Debit",
                original_source_file="test.csv"
            ),
            NormalizedTransaction(
                date=date(2025, 8, 1),
                description="Test Transaction 2",
                amount=456.78,
                transaction_type="Credit",
                original_source_file="test.csv"
            )
        ]
        
        # Generate CSV
        csv_content = agent.generate_csv(transactions, "3-column", "MM/DD/YYYY")
        
        # Validate CSV content
        assert "Date,Description,Amount" in csv_content
        assert "07/31/2025,Test Transaction 1,-123.45" in csv_content
        assert "08/01/2025,Test Transaction 2,456.78" in csv_content
    
    def test_generate_four_column_csv(self):
        """Test generating a 4-column CSV."""
        agent = QuickBooksFormatterAgent()
        
        # Create sample normalized transactions
        transactions = [
            NormalizedTransaction(
                date=date(2025, 7, 31),
                description="Test Transaction 1",
                amount=-123.45,
                transaction_type="Debit",
                original_source_file="test.csv"
            ),
            NormalizedTransaction(
                date=date(2025, 8, 1),
                description="Test Transaction 2",
                amount=456.78,
                transaction_type="Credit",
                original_source_file="test.csv"
            )
        ]
        
        # Generate CSV
        csv_content = agent.generate_csv(transactions, "4-column", "MM/DD/YYYY")
        
        # Validate CSV content
        assert "Date,Description,Debit,Credit" in csv_content
        assert "07/31/2025,Test Transaction 1,123.45," in csv_content
        assert "08/01/2025,Test Transaction 2,,456.78" in csv_content
    
    def test_write_csv_to_file(self):
        """Test writing CSV to a file."""
        agent = QuickBooksFormatterAgent()
        
        # Create sample normalized transactions
        transactions = [
            NormalizedTransaction(
                date=date(2025, 7, 31),
                description="Test Transaction",
                amount=-123.45,
                transaction_type="Debit",
                original_source_file="test.csv"
            )
        ]
        
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Write CSV to file
            success = agent.write_csv_to_file(transactions, temp_path, "3-column", "MM/DD/YYYY")
            
            # Validate success
            assert success is True
            
            # Validate file content
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Date,Description,Amount" in content
                assert "07/31/2025,Test Transaction,-123.45" in content
                
        finally:
            # Clean up
            os.unlink(temp_path)


class TestReceiptExtractorAgent:
    """Test suite for ReceiptExtractorAgent."""
    
    def test_process_receipt(self):
        """Test processing a receipt from OCR text."""
        agent = ReceiptExtractorAgent()
        
        # Create sample raw data
        raw_data = RawTransactionData(
            raw_text="""WALMART
123 Main St
Date: 07/31/2025
Item         Qty   Price
Milk          1     3.99
Bread         2     2.50
Eggs          1     4.99
TOTAL       $13.98
Thank you for shopping at Walmart!
""",
            source_file_name="receipt.jpg",
            source_file_type="JPEG"
        )
        
        # Process receipt
        result = agent.process_receipt(raw_data, "path/to/receipt.jpg")
        
        # Validate result
        assert result is not None
        assert "Walmart" in result.vendor_name
        assert result.transaction_date == date(2025, 7, 31)
        assert result.total_amount == 13.98
        assert result.currency == "USD"
        assert result.category_suggestion == "Groceries"
    
    def test_extract_vendor_name(self):
        """Test extracting vendor name from receipt text."""
        agent = ReceiptExtractorAgent()
        
        # Test with vendor at top
        text = "WALMART\nReceipt\nDate: 07/31/2025"
        assert agent._extract_vendor_name(text) == "WALMART"
        
        # Test with welcome text
        text = "Welcome to Starbucks\nDate: 07/31/2025"
        assert "Starbucks" in agent._extract_vendor_name(text)
        
        # Test with no clear vendor
        text = "1234567890\nDate: 07/31/2025"
        assert agent._extract_vendor_name(text) == "Unknown Vendor"
    
    def test_extract_total_amount(self):
        """Test extracting total amount from receipt text."""
        agent = ReceiptExtractorAgent()
        
        # Test with total keyword
        text = "Subtotal: $10.00\nTax: $0.80\nTotal: $10.80"
        assert agent._extract_total_amount(text) == 10.80
        
        # Test with amount keyword
        text = "Amount due: $15.75"
        assert agent._extract_total_amount(text) == 15.75
        
        # Test with no clear total
        text = "No total amount here"
        assert agent._extract_total_amount(text) == 0.0
