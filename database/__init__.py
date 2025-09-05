"""Database Package for Ainflue Platform
Database connections, models, and utilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

# Import commonly used database utilities
try:
    from .schema import *
except ImportError:
    pass

__all__ = []