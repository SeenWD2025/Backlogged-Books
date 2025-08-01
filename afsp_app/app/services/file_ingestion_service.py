"""
File Ingestion Service for AFSP.
Handles file uploads, validation, and dispatches to appropriate parsing agents.
"""

import os
from typing import List, Optional, Tuple
from pathlib import Path
import logging
import uuid
from datetime import datetime

from afsp_app.app.schemas import RawTransactionData

# Configure logging
logger = logging.getLogger(__name__)


class FileIngestionService:
    """
    Service for handling file uploads and ingestion.
    Provides methods for storing files and extracting raw text based on file type.
    """
    
    def __init__(self, upload_dir: str):
        """
        Initialize the file ingestion service.
        
        Args:
            upload_dir: Directory to store uploaded files
        """
        self.upload_dir = upload_dir
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
    
    async def store_file(self, file_content: bytes, file_name: str, job_id: str) -> Tuple[str, str]:
        """
        Store an uploaded file in the upload directory.
        
        Args:
            file_content: Raw bytes of the file
            file_name: Original filename
            job_id: Unique identifier for the job
            
        Returns:
            Tuple containing the file path and file type
        """
        try:
            # Extract file extension to determine type
            file_ext = Path(file_name).suffix.lower().lstrip('.')
            if file_ext in ('jpg', 'jpeg'):
                file_type = 'JPEG'
            else:
                file_type = file_ext.upper()
                
            # Create file path with job ID
            file_path = os.path.join(self.upload_dir, f"{job_id}_{file_name}")
            
            # Write content to file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Stored file {file_name} as {file_path} with type {file_type}")
            return file_path, file_type
        
        except Exception as e:
            logger.error(f"Failed to store file {file_name}: {str(e)}")
            raise
    
    async def dispatch_to_extraction_agent(self, file_path: str, file_type: str, file_name: str) -> List[RawTransactionData]:
        """
        Dispatch the file to the appropriate extraction agent based on file type.
        This is a placeholder method that will be implemented with the actual agents.
        
        Args:
            file_path: Path to the stored file
            file_type: Type of the file (CSV, PDF, DOCX, JPEG, PNG)
            file_name: Original filename
            
        Returns:
            List of RawTransactionData objects
        """
        logger.info(f"Dispatching {file_path} of type {file_type} to extraction agent")
        
        # This will be implemented properly when we create the extraction agents
        # For now, return a placeholder RawTransactionData
        raw_data = RawTransactionData(
            raw_text="Sample raw text from file",
            source_file_name=file_name,
            source_file_type=file_type,
            timestamp_extracted=datetime.now()
        )
        
        return [raw_data]
    
    def validate_file_type(self, file_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the file type based on extension.
        
        Args:
            file_name: Name of the file to validate
            
        Returns:
            Tuple of (is_valid, file_type)
        """
        file_ext = Path(file_name).suffix.lower().lstrip('.')
        valid_extensions = {'csv', 'pdf', 'docx', 'jpg', 'jpeg', 'png'}
        
        if file_ext not in valid_extensions:
            return False, None
        
        if file_ext in ('jpg', 'jpeg'):
            return True, 'JPEG'
        
        return True, file_ext.upper()
    
    def clean_up_file(self, file_path: str) -> bool:
        """
        Delete a file after processing is complete.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
