#!/usr/bin/env python3
"""
🔍 Protection Logger Module
===========================

Logging utilities for the protection system.

Author: Fahed Mlaiel (mlaiel@live.de)
Protection Logger Module
"""

import logging
import sys
from typing import Optional
from datetime import datetime

class ProtectionLogger:
    """Protection system logger."""
    
    def __init__(self, name: str = "protection", level: int = logging.INFO):
        """Initialize the logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)

# Default logger instance
logger = ProtectionLogger()

def get_logger(name: Optional[str] = None) -> ProtectionLogger:
    """Get a logger instance."""
    return ProtectionLogger(name or "protection")

def setup_crawler_logger(name: str = "crawler", level: int = logging.INFO) -> ProtectionLogger:
    """Setup crawler logger."""
    return ProtectionLogger(name, level)