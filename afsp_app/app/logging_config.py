"""
Structured logging configuration for the AFSP application.
Provides formatted JSON logs with consistent fields and context.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON objects with consistent fields.
    """
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON object.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted JSON string
        """
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra attributes from record
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in log_record:
                continue
            if key == "exc_info" and value:
                # Format exception information
                if value[1]:  # If we have an exception object
                    log_record["exception"] = {
                        "type": value[0].__name__ if value[0] else None,
                        "message": str(value[1]),
                    }
                continue
            try:
                # Attempt to serialize the value to ensure it's JSON-compatible
                json.dumps({key: value})
                log_record[key] = value
            except (TypeError, ValueError):
                # If value can't be serialized, convert to string
                log_record[key] = str(value)
        
        return json.dumps(log_record)


def get_logger(name: str, job_id: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the structured formatter.
    
    Args:
        name: Logger name
        job_id: Optional job ID to include in all log records
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Only configure if no handlers exist to prevent duplicate handlers
    if not logger.handlers:
        # Create handler with the structured formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        
        # Configure logger
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False  # Prevent duplicate logs
    
    # Create filter to add job_id to all records
    if job_id:
        class JobIdFilter(logging.Filter):
            def filter(self, record):
                record.job_id = job_id
                return True
                
        for handler in logger.handlers:
            handler.addFilter(JobIdFilter())
    
    return logger
