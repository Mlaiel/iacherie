"""Infrastructure Storage Module - IA-Influencer-Agent Platform
==============================================================
Storage adapters and management for infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved

This module provides storage services:
- Database adapters (PostgreSQL, MongoDB)
- File storage management
- Redis caching
- Object storage integration
"""

# Import storage modules
try:
    from .database_adapter import *
except ImportError:
    pass

try:
    from .file_storage import *
except ImportError:
    pass

try:
    from .mongodb_adapter import *
except ImportError:
    pass

try:
    from .redis_adapter import *
except ImportError:
    pass

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Collect all exports from storage submodules
__all__ = []

try:
    from . import database_adapter
    if hasattr(database_adapter, '__all__'):
        __all__.extend(database_adapter.__all__)
except ImportError:
    pass

try:
    from . import file_storage
    if hasattr(file_storage, '__all__'):
        __all__.extend(file_storage.__all__)
except ImportError:
    pass

try:
    from . import mongodb_adapter
    if hasattr(mongodb_adapter, '__all__'):
        __all__.extend(mongodb_adapter.__all__)
except ImportError:
    pass

try:
    from . import redis_adapter
    if hasattr(redis_adapter, '__all__'):
        __all__.extend(redis_adapter.__all__)
except ImportError:
    pass