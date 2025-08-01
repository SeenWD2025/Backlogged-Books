"""
End-to-end tests for the main application.
Tests the full processing pipeline from file upload to CSV generation.
"""

import pytest
import os
import tempfile
from pathlib import Path
import json
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.database import DatabaseManager


client = TestClient(app)


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
        temp.write(b"Date,Description,Amount\n07/31/2025,Test Transaction,123.45")
        temp_path = temp.name
    
    yield temp_path
    
    # Clean up
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_database():
    """Mock database manager for testing."""
    with patch('app.main.db_manager') as mock_db:
        # Mock database methods
        mock_db.create_job.return_value = True
        mock_db.update_job_status.return_value = True
        mock_db.get_job.return_value = {
            "job_id": "test-job-id",
            "status": "COMPLETED",
            "source_file": "test.csv",
            "created_at": "2025-07-31T12:00:00",
            "updated_at": "2025-07-31T12:05:00",
            "output_file": "/path/to/output.csv",
            "error_message": None
        }
        mock_db.get_job_transactions.return_value = []
        
        yield mock_db


@pytest.fixture
def mock_process_file():
    """Mock the background processing function for testing."""
    with patch('app.main.process_file') as mock_process:
        async def mock_async_process(*args, **kwargs):
            return
        
        mock_process.side_effect = mock_async_process
        yield mock_process


class TestAPI:
    """Test suite for the API endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "app" in response.json()
        assert "version" in response.json()
    
    def test_upload_endpoint(self, sample_csv_file, mock_database, mock_process_file):
        """Test the upload endpoint with a CSV file."""
        # Open sample file
        with open(sample_csv_file, 'rb') as f:
            file_content = f.read()
        
        # Send upload request
        response = client.post(
            "/upload",
            files={"file": ("test.csv", file_content, "text/csv")},
            data={
                "csv_format": "3-column",
                "date_format": "MM/DD/YYYY"
            }
        )
        
        # Validate response
        assert response.status_code == 200
        assert "job_id" in response.json()
        assert "status" in response.json()
        assert response.json()["status"] == "PROCESSING"
    
    def test_upload_invalid_file_type(self, mock_database):
        """Test the upload endpoint with an invalid file type."""
        # Create a temporary file with invalid extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(b"This is not a valid file type.")
            temp_path = temp.name
        
        try:
            # Open file
            with open(temp_path, 'rb') as f:
                file_content = f.read()
            
            # Send upload request
            response = client.post(
                "/upload",
                files={"file": ("test.txt", file_content, "text/plain")},
                data={
                    "csv_format": "3-column",
                    "date_format": "MM/DD/YYYY"
                }
            )
            
            # Validate response
            assert response.status_code == 400
            assert "Unsupported file type" in response.json()["detail"]
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_status_endpoint(self, mock_database):
        """Test the status endpoint."""
        # Mock database methods
        mock_database.get_job.return_value = {
            "job_id": "test-job-id",
            "status": "COMPLETED",
            "source_file": "test.csv",
            "created_at": "2025-07-31T12:00:00",
            "updated_at": "2025-07-31T12:05:00",
            "output_file": "/path/to/output.csv",
            "error_message": None
        }
        
        # Send status request
        response = client.get("/status/test-job-id")
        
        # Validate response
        assert response.status_code == 200
        assert response.json()["job_id"] == "test-job-id"
        assert response.json()["status"] == "COMPLETED"
    
    def test_status_not_found(self, mock_database):
        """Test the status endpoint with a non-existent job ID."""
        # Mock database methods
        mock_database.get_job.return_value = None
        
        # Send status request
        response = client.get("/status/non-existent-job")
        
        # Validate response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_download_endpoint(self, mock_database):
        """Test the download endpoint."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp.write(b"Date,Description,Amount\n07/31/2025,Test Transaction,123.45")
            temp_path = temp.name
        
        try:
            # Mock database methods
            mock_database.get_job.return_value = {
                "job_id": "test-job-id",
                "status": "COMPLETED",
                "source_file": "test.csv",
                "created_at": "2025-07-31T12:00:00",
                "updated_at": "2025-07-31T12:05:00",
                "output_file": temp_path,
                "error_message": None
            }
            
            # Send download request
            with patch('app.main.FileResponse', return_value=MagicMock()) as mock_file_response:
                response = client.get("/download/test-job-id")
                
                # Validate FileResponse was called with correct parameters
                mock_file_response.assert_called_once_with(
                    temp_path,
                    filename=f"quickbooks_import_test-job-id.csv",
                    media_type="text/csv"
                )
                
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_download_not_found(self, mock_database):
        """Test the download endpoint with a non-existent job ID."""
        # Mock database methods
        mock_database.get_job.return_value = None
        
        # Send download request
        response = client.get("/download/non-existent-job")
        
        # Validate response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_download_not_completed(self, mock_database):
        """Test the download endpoint with a job that's not completed."""
        # Mock database methods
        mock_database.get_job.return_value = {
            "job_id": "test-job-id",
            "status": "PROCESSING",
            "source_file": "test.csv",
            "created_at": "2025-07-31T12:00:00",
            "updated_at": "2025-07-31T12:05:00",
            "output_file": None,
            "error_message": None
        }
        
        # Send download request
        response = client.get("/download/test-job-id")
        
        # Validate response
        assert response.status_code == 400
        assert "not complete" in response.json()["detail"]


@pytest.mark.asyncio
async def test_process_file():
    """Test the background process_file function."""
    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize database
        db = DatabaseManager(temp_db_path)
        
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file.write(b"Date,Description,Amount\n07/31/2025,Test Transaction,123.45")
            file_path = temp_file.name
        
        try:
            # Create job
            job_id = "test-process-job"
            db.create_job(job_id, file_path, "CSV", "MM/DD/YYYY", "3-column")
            
            # Process file with real implementation
            from app.main import process_file
            await process_file(job_id, file_path, "CSV", "MM/DD/YYYY", "3-column")
            
            # Check job status
            job = db.get_job(job_id)
            assert job is not None
            assert job["status"] == "COMPLETED"
            assert job["output_file"] is not None
            
            # Check output file exists
            assert os.path.exists(job["output_file"])
            
            # Clean up output file
            os.unlink(job["output_file"])
            
        finally:
            # Clean up file
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    finally:
        # Clean up database
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
