"""
QuickBooks Formatter Agent for generating QuickBooks-compatible CSV files.
"""

import logging
import csv
from typing import List, Literal
from io import StringIO
from datetime import date

from afsp_app.app.schemas import NormalizedTransaction
from afsp_app.app.tools.date_parser import normalize_date_format

# Configure logging
logger = logging.getLogger(__name__)


class QuickBooksFormatterAgent:
    """
    Agent responsible for formatting normalized transactions into QuickBooks-compatible CSV format.
    Handles both 3-column and 4-column formats.
    """
    
    def generate_csv(
        self, 
        transactions: List[NormalizedTransaction], 
        csv_format: Literal["3-column", "4-column"] = "3-column",
        date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = "MM/DD/YYYY"
    ) -> str:
        """
        Generate a QuickBooks-compatible CSV string from normalized transactions.
        
        Args:
            transactions: List of NormalizedTransaction objects
            csv_format: Format for QuickBooks CSV (3-column or 4-column)
            date_format: Format for dates in CSV (MM/DD/YYYY or DD/MM/YYYY)
            
        Returns:
            CSV string in the specified format
        """
        try:
            logger.info(f"Generating {csv_format} CSV with {date_format} date format")
            
            if csv_format == "3-column":
                return self._generate_three_column_csv(transactions, date_format)
            else:
                return self._generate_four_column_csv(transactions, date_format)
                
        except Exception as e:
            logger.error(f"Error generating CSV: {str(e)}")
            return ""
    
    def _generate_three_column_csv(
        self, 
        transactions: List[NormalizedTransaction],
        date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"]
    ) -> str:
        """
        Generate a 3-column QuickBooks CSV.
        Format: Date, Description, Amount
        
        Args:
            transactions: List of NormalizedTransaction objects
            date_format: Format for dates in CSV
            
        Returns:
            CSV string in 3-column format
        """
        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        writer.writerow(["Date", "Description", "Amount"])
        
        # Write transactions
        for transaction in transactions:
            # Format date according to specified format
            formatted_date = normalize_date_format(transaction.date, date_format)
            
            # In 3-column format:
            # - Credits (income) are positive
            # - Debits (expenses) are negative
            amount = transaction.amount
            
            writer.writerow([
                formatted_date,
                transaction.description,
                amount
            ])
        
        return output.getvalue()
    
    def _generate_four_column_csv(
        self, 
        transactions: List[NormalizedTransaction],
        date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"]
    ) -> str:
        """
        Generate a 4-column QuickBooks CSV.
        Format: Date, Description, Debit, Credit
        
        Args:
            transactions: List of NormalizedTransaction objects
            date_format: Format for dates in CSV
            
        Returns:
            CSV string in 4-column format
        """
        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        writer.writerow(["Date", "Description", "Debit", "Credit"])
        
        # Write transactions
        for transaction in transactions:
            # Format date according to specified format
            formatted_date = normalize_date_format(transaction.date, date_format)
            
            # In 4-column format:
            # - For Debit (expense): amount goes in Debit column, Credit column is empty
            # - For Credit (income): amount goes in Credit column, Debit column is empty
            debit_amount = ""
            credit_amount = ""
            
            if transaction.transaction_type == "Debit":
                debit_amount = abs(transaction.amount)
            else:
                credit_amount = abs(transaction.amount)
            
            writer.writerow([
                formatted_date,
                transaction.description,
                debit_amount,
                credit_amount
            ])
        
        return output.getvalue()
    
    def write_csv_to_file(
        self, 
        transactions: List[NormalizedTransaction], 
        output_path: str,
        csv_format: Literal["3-column", "4-column"] = "3-column",
        date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = "MM/DD/YYYY"
    ) -> bool:
        """
        Write transactions to a CSV file.
        
        Args:
            transactions: List of NormalizedTransaction objects
            output_path: Path to write the CSV file
            csv_format: Format for QuickBooks CSV (3-column or 4-column)
            date_format: Format for dates in CSV (MM/DD/YYYY or DD/MM/YYYY)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            csv_content = self.generate_csv(transactions, csv_format, date_format)
            
            with open(output_path, 'w', newline='') as f:
                f.write(csv_content)
            
            logger.info(f"CSV file written to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing CSV file: {str(e)}")
            return False
