"""
Raw Data Extraction Agent for extracting transaction data from various file formats.
"""

import logging
import os
import tempfile
from typing import List, Optional
import PyPDF2
import csv
from io import StringIO, BytesIO
from pathlib import Path
from docx import Document
import pandas as pd
from pdf2image import convert_from_path

from afsp_app.app.schemas import RawTransactionData
from afsp_app.app.tools.ocr_tool import perform_ocr

# Configure logging
logger = logging.getLogger(__name__)


class RawDataExtractionAgent:
    """
    Agent responsible for extracting raw transaction data from various file types.
    Orchestrates the appropriate extraction tool based on file type.
    """
    
    def extract_from_file(self, file_path: str, file_type: str) -> List[RawTransactionData]:
        """
        Extract raw transaction data from a file.
        
        Args:
            file_path: Path to the file
            file_type: Type of the file (CSV, PDF, DOCX, JPEG, PNG)
            
        Returns:
            List of RawTransactionData objects
        """
        try:
            logger.info(f"Extracting data from {file_path} (type: {file_type})")
            
            # Ensure file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return []
            
            # Extract based on file type
            if file_type == "CSV":
                return self._extract_from_csv(file_path)
            elif file_type == "PDF":
                return self._extract_from_pdf(file_path)
            elif file_type == "DOCX":
                return self._extract_from_docx(file_path)
            elif file_type in ["JPEG", "PNG"]:
                return self._extract_from_image(file_path)
            else:
                logger.error(f"Unsupported file type: {file_type}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            return []
    
    def _extract_from_csv(self, file_path: str) -> List[RawTransactionData]:
        """
        Extract data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of RawTransactionData objects
        """
        result = []
        source_file_name = os.path.basename(file_path)
        
        try:
            # Try to determine dialect and encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                
                # Try different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252']
                content = None
                
                for encoding in encodings:
                    try:
                        content = raw_data.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if not content:
                    logger.error(f"Could not decode {file_path} with any of the tried encodings")
                    return []
                
                # Try to use pandas to read the CSV which is more robust with various formats
                try:
                    df = pd.read_csv(StringIO(content))
                    
                    # Convert each row to RawTransactionData
                    for i, row in df.iterrows():
                        # Store the original row as a JSON string to preserve structure
                        raw_text = row.to_json()
                        
                        raw_data_item = RawTransactionData(
                            raw_text=raw_text,
                            source_file_name=source_file_name,
                            source_file_type="CSV",
                            line_number=i+1
                        )
                        result.append(raw_data_item)
                        
                except Exception as e:
                    logger.warning(f"Pandas failed to parse CSV, falling back to csv module: {str(e)}")
                    
                    # Fall back to csv module if pandas fails
                    csv_reader = csv.reader(StringIO(content))
                    for i, row in enumerate(csv_reader):
                        raw_text = ','.join(row)
                        
                        raw_data_item = RawTransactionData(
                            raw_text=raw_text,
                            source_file_name=source_file_name,
                            source_file_type="CSV",
                            line_number=i+1
                        )
                        result.append(raw_data_item)
        
        except Exception as e:
            logger.error(f"Error extracting from CSV: {str(e)}")
        
        return result
    
    def _extract_from_pdf(self, file_path: str) -> List[RawTransactionData]:
        """
        Extract data from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of RawTransactionData objects
        """
        result = []
        source_file_name = os.path.basename(file_path)
        
        try:
            # Open the PDF file
            with open(file_path, 'rb') as file:
                # Create a PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    logger.error(f"PDF is encrypted: {file_path}")
                    return []
                
                # Process each page
                for i, page in enumerate(pdf_reader.pages):
                    try:
                        # Extract text from page
                        text = page.extract_text()
                        
                        # If text extraction failed or returned very little text,
                        # the PDF may be scanned/image-based, try OCR
                        if not text or len(text.strip()) < 100:
                            logger.info(f"Page {i+1} has little or no extractable text, attempting OCR")
                            
                            try:
                                # Use pdf2image to convert the PDF page to an image
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    # Convert the specific page to an image
                                    images = convert_from_path(
                                        file_path, 
                                        output_folder=temp_dir, 
                                        first_page=i+1, 
                                        last_page=i+1
                                    )
                                    
                                    if images:
                                        # Convert the image to bytes and perform OCR
                                        with BytesIO() as image_bytes:
                                            images[0].save(image_bytes, format='PNG')
                                            image_bytes.seek(0)
                                            ocr_text = perform_ocr(image_bytes.read())
                                            
                                            if ocr_text and len(ocr_text.strip()) > 0:
                                                text = ocr_text
                                                logger.info(f"OCR successful on page {i+1}")
                                            else:
                                                logger.warning(f"OCR failed to extract text from page {i+1}")
                            except Exception as ocr_error:
                                logger.error(f"Error during OCR processing: {str(ocr_error)}")
                                                            
                            raw_data_item = RawTransactionData(
                                raw_text=text or f"[OCR FAILED] No text could be extracted from page {i+1}",
                                source_file_name=source_file_name,
                                source_file_type="PDF",
                                page_number=i+1
                            )
                        else:
                            # Create RawTransactionData for this page
                            raw_data_item = RawTransactionData(
                                raw_text=text,
                                source_file_name=source_file_name,
                                source_file_type="PDF",
                                page_number=i+1
                            )
                        
                        result.append(raw_data_item)
                        
                    except Exception as e:
                        logger.error(f"Error processing page {i+1}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error extracting from PDF: {str(e)}")
        
        return result
    
    def _extract_from_docx(self, file_path: str) -> List[RawTransactionData]:
        """
        Extract data from a DOCX file.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            List of RawTransactionData objects
        """
        result = []
        source_file_name = os.path.basename(file_path)
        
        try:
            # Open the DOCX file
            doc = Document(file_path)
            
            # Process each paragraph
            for i, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                
                # Skip empty paragraphs
                if not text:
                    continue
                
                # Create RawTransactionData for this paragraph
                raw_data_item = RawTransactionData(
                    raw_text=text,
                    source_file_name=source_file_name,
                    source_file_type="DOCX",
                    line_number=i+1
                )
                result.append(raw_data_item)
                
        except Exception as e:
            logger.error(f"Error extracting from DOCX: {str(e)}")
        
        return result
    
    def _extract_from_image(self, file_path: str) -> List[RawTransactionData]:
        """
        Extract data from an image file using OCR.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            List of RawTransactionData objects
        """
        result = []
        source_file_name = os.path.basename(file_path)
        source_file_type = Path(file_path).suffix.upper().lstrip('.')
        
        if source_file_type == "JPG":
            source_file_type = "JPEG"
        
        try:
            # Read the image file
            with open(file_path, 'rb') as file:
                image_bytes = file.read()
                
                # Perform OCR on the image
                ocr_text = perform_ocr(image_bytes)
                
                if ocr_text:
                    # Create RawTransactionData for the OCR result
                    raw_data_item = RawTransactionData(
                        raw_text=ocr_text,
                        source_file_name=source_file_name,
                        source_file_type=source_file_type
                    )
                    result.append(raw_data_item)
                else:
                    logger.error(f"OCR failed for image: {file_path}")
                
        except Exception as e:
            logger.error(f"Error extracting from image: {str(e)}")
        
        return result
