"""
Core Logging Configuration
"""

import logging
import sys
from typing import Optional

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create module logger
logger = logging.getLogger("ainflue")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance"""
    if name:
        return logging.getLogger(f"ainflue.{name}")
    return logger

def set_log_level(level: str) -> None:
    """Set logging level"""
    logger.setLevel(getattr(logging, level.upper()))

__all__ = ["logger", "get_logger", "set_log_level"]
