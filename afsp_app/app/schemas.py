"""
Pydantic models for data validation and serialization.
Defines the data structures used throughout the application.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Literal, Any
from pydantic import BaseModel, Field
import uuid


class RawTransactionData(BaseModel):
    """
    Initial unstructured data extracted from source documents.
    """
    raw_text: str
    source_file_name: str
    source_file_type: Literal["CSV", "PDF", "DOCX", "JPEG", "PNG"]
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    bounding_box: Optional[Tuple[float, float, float, float]] = None
    timestamp_extracted: datetime = Field(default_factory=datetime.now)


class ExtractedTransaction(BaseModel):
    """
    Holds initially identified but not yet fully normalized transaction fields.
    """
    unique_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    raw_text_reference: str
    potential_date_str: Optional[str] = None
    potential_description_str: Optional[str] = None
    potential_amount_str: Optional[str] = None
    potential_credit_str: Optional[str] = None
    potential_debit_str: Optional[str] = None
    confidence_score: Dict[str, float] = Field(default_factory=dict)
    extraction_errors: List[str] = Field(default_factory=list)


class NormalizedTransaction(BaseModel):
    """
    Clean, validated, and categorized financial transaction data.
    Ready for final formatting.
    """
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: date
    description: str
    amount: float  # Positive for income/credit, negative for expense/debit
    transaction_type: Literal["Credit", "Debit"]
    original_source_file: str
    processing_notes: List[str] = Field(default_factory=list)
    
    @classmethod
    def model_validate(cls, *args, **kwargs):
        obj = super().model_validate(*args, **kwargs)
        obj = cls.validate_amount_sign(obj)
        return obj
    
    @staticmethod
    def validate_amount_sign(obj):
        """Ensure amount sign matches transaction type"""
        if obj.transaction_type == 'Credit' and obj.amount < 0:
            obj.amount = abs(obj.amount)
        elif obj.transaction_type == 'Debit' and obj.amount > 0:
            obj.amount = -abs(obj.amount)
        return obj


class ReceiptData(BaseModel):
    """
    Structured data extracted from receipt images.
    """
    receipt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vendor_name: str
    transaction_date: date
    total_amount: float
    currency: str = "USD"
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    category_suggestion: Optional[str] = None
    image_path: str
    ocr_raw_text: str


class StatusResponse(BaseModel):
    """
    Response model for job status endpoint.
    """
    job_id: str
    status: str
    source_file: str
    created_at: datetime
    updated_at: datetime
    output_file: Optional[str] = None
    error_message: Optional[str] = None
    preview_data: Optional[List[Dict[str, Any]]] = None
    
    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    """
    Response model for file upload endpoint.
    """
    job_id: str
    message: str
    status: str
    
    model_config = {"from_attributes": True}


class QuickBooksFormatRequest(BaseModel):
    """
    Request model for specifying QuickBooks format preferences.
    """
    csv_format: Literal["3-column", "4-column"] = "3-column"
    date_format: Literal["MM/DD/YYYY", "DD/MM/YYYY"] = "MM/DD/YYYY"
