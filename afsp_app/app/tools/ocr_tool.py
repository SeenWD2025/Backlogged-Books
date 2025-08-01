"""
OCR Tool for extracting text from images.
Uses pytesseract as the OCR engine.
"""

import logging
import io
from typing import Optional
import pytesseract
from PIL import Image, ImageEnhance

from afsp_app.app.config import TESSERACT_PATH

# Configure logging
logger = logging.getLogger(__name__)

# Configure pytesseract path if provided
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def perform_ocr(image_bytes: bytes) -> Optional[str]:
    """
    Extracts text from an image using OCR.
    
    Args:
        image_bytes: Raw image data as bytes
        
    Returns:
        Extracted text or None if extraction failed
    """
    try:
        # Open image using PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Apply basic image preprocessing to improve OCR quality
        image = preprocess_image(image)
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        if not text.strip():
            logger.warning("OCR extracted empty text")
            return None
            
        return text
    
    except pytesseract.TesseractNotFoundError:
        logger.critical("Tesseract OCR is not installed or not configured properly")
        return None
    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        return None


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess the image to improve OCR quality.
    
    Args:
        image: PIL Image object
        
    Returns:
        Preprocessed PIL Image object
    """
    try:
        # Convert to grayscale
        image = image.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        return image
    except Exception as e:
        logger.error(f"Image preprocessing failed: {str(e)}")
        return image  # Return original image if preprocessing fails
