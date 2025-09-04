"""Backend Core Database Module - Consolidated Database Components

This module consolidates all database-related functionality including:
- Migrations (from database/migrations/)
- Data Migrations (from data_management/migrations/) 
- Schemas (from database/schemas/)
- Seeds (from data_management/seeds/)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Make submodules available
import os
import sys
from pathlib import Path

# Add current directory to Python path for submodule imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Optional imports - don't fail if dependencies are missing
try:
    from . import migrations
    from . import data_migrations
    from . import schemas
    from . import seeds
except ImportError as e:
    # Log the import error but don't fail
    import logging
    logging.getLogger(__name__).warning(f"Some database modules unavailable: {e}")
    migrations = None
    data_migrations = None
    schemas = None
    seeds = None

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "migrations",
    "data_migrations", 
    "schemas",
    "seeds"
]