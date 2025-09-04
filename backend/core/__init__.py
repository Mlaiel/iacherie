"""Backend Core Module - Consolidated Database and Core Components

Central backend core components for the IA Influencer Agent Platform.
This module now includes consolidated database migrations, schemas, and seeds.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core Models
try:
    from .models import *
except ImportError:
    pass

# Consolidated Database Components
try:
    from . import database
except ImportError:
    database = None

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "database"
]