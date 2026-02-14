# CHECKPOINT_1_PROJECT_SETUP
"""
Logging Utilities
=================
Centralized logging configuration.
"""

import logging
import sys
from pathlib import Path
from backend.config import settings


def setup_logging() -> logging.Logger:
    """
    Configure application logging.
    Returns the root logger.
    """
    # Create logs directory if needed
    if settings.LOG_TO_FILE:
        log_dir = Path(settings.LOG_FILE_PATH).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Add file handler if enabled
    if settings.LOG_TO_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE_PATH)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
    
    logger = logging.getLogger("expense_tracker")
    logger.info("Logging configured successfully")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module"""
    return logging.getLogger(f"expense_tracker.{name}")
