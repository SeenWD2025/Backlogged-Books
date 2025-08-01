"""
Database manager for the AFSP application.
Encapsulates all SQLite database logic and provides methods to perform CRUD operations.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from pathlib import Path

from afsp_app.app.config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages SQLite database operations for the AFSP application.
    Handles job statuses, error tracking, and file references.
    """
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Initialize the database manager with the given database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """
        Initialize the database schema if it doesn't exist.
        Creates tables for jobs and transactions.
        """
        try:
            # Ensure the directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create jobs table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    source_file TEXT NOT NULL,
                    source_file_type TEXT NOT NULL,
                    output_file TEXT,
                    date_format TEXT NOT NULL,
                    csv_format TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error_message TEXT
                )
                ''')
                
                # Create transactions table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    original_raw_text TEXT,
                    processing_notes TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def create_job(self, job_id: str, source_file: str, source_file_type: str, 
                  date_format: str, csv_format: str) -> bool:
        """
        Create a new job record in the database.
        
        Args:
            job_id: Unique identifier for the job
            source_file: Path to the source file
            source_file_type: Type of the source file (PDF, CSV, etc.)
            date_format: Format to use for dates (MM/DD/YYYY or DD/MM/YYYY)
            csv_format: Format to use for CSV output (3-column or 4-column)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = datetime.now().isoformat()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    INSERT INTO jobs (job_id, status, source_file, source_file_type, 
                                     date_format, csv_format, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (job_id, "PENDING", source_file, source_file_type, 
                     date_format, csv_format, now, now)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to create job {job_id}: {e}")
            return False
    
    def update_job_status(self, job_id: str, status: str, 
                         output_file: Optional[str] = None, 
                         error_message: Optional[str] = None) -> bool:
        """
        Update the status of an existing job.
        
        Args:
            job_id: The job's unique identifier
            status: New status (PENDING, PROCESSING, COMPLETED, FAILED)
            output_file: Path to the output file (if completed)
            error_message: Error message (if failed)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = datetime.now().isoformat()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build the query dynamically based on provided parameters
                query = "UPDATE jobs SET status = ?, updated_at = ?"
                params = [status, now]
                
                if output_file is not None:
                    query += ", output_file = ?"
                    params.append(output_file)
                
                if error_message is not None:
                    query += ", error_message = ?"
                    params.append(error_message)
                
                query += " WHERE job_id = ?"
                params.append(job_id)
                
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific job.
        
        Args:
            job_id: The job's unique identifier
            
        Returns:
            Optional[Dict[str, Any]]: Job information or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def add_transactions(self, job_id: str, transactions: List[Dict[str, Any]]) -> bool:
        """
        Add multiple transactions to the database for a specific job.
        
        Args:
            job_id: The job's unique identifier
            transactions: List of transaction dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for transaction in transactions:
                    # Serialize processing_notes as JSON
                    processing_notes = json.dumps(transaction.get('processing_notes', []))
                    
                    cursor.execute(
                        '''
                        INSERT INTO transactions (
                            transaction_id, job_id, date, description, amount,
                            transaction_type, original_raw_text, processing_notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''',
                        (
                            transaction['transaction_id'], job_id,
                            transaction['date'], transaction['description'],
                            transaction['amount'], transaction['transaction_type'],
                            transaction.get('original_raw_text', ''),
                            processing_notes
                        )
                    )
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to add transactions for job {job_id}: {e}")
            return False
    
    def get_job_transactions(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Get all transactions associated with a specific job.
        
        Args:
            job_id: The job's unique identifier
            
        Returns:
            List[Dict[str, Any]]: List of transaction dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM transactions WHERE job_id = ?", (job_id,))
                rows = cursor.fetchall()
                
                transactions = []
                for row in rows:
                    transaction = dict(row)
                    # Parse processing_notes from JSON
                    if transaction.get('processing_notes'):
                        transaction['processing_notes'] = json.loads(transaction['processing_notes'])
                    else:
                        transaction['processing_notes'] = []
                    transactions.append(transaction)
                
                return transactions
        except sqlite3.Error as e:
            logger.error(f"Failed to get transactions for job {job_id}: {e}")
            return []
    
    def get_all_jobs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get a list of all jobs, with pagination.
        
        Args:
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
            
        Returns:
            List[Dict[str, Any]]: List of job dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?", 
                    (limit, offset)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to get all jobs: {e}")
            return []
