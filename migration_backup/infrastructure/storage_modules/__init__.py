"""Infrastructure Storage Module - Ainflue Enterprise Platform
==============================================================
Comprehensive storage services for enterprise infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue Infrastructure Enterprise
License: Proprietary - All rights reserved

This module provides storage services:
- Core storage functionality
- Database adapters (PostgreSQL, MongoDB)
- File storage management
- Redis caching
- Object storage integration
- Block storage management
- Content caching
"""

# Core storage functionality (from root storage.py)
try:
    from .core_storage import *
except ImportError:
    pass

# Database adapters
try:
    from .database_adapter import *
except ImportError:
    pass

# File storage
try:
    from .file_storage import *
except ImportError:
    pass

# MongoDB adapter
try:
    from .mongodb_adapter import *
except ImportError:
    pass

# Redis adapter
try:
    from .redis_adapter import *
except ImportError:
    pass

# Block storage
try:
    from .block_storage import *
except ImportError:
    pass

# Object storage
try:
    from .object_storage import *
except ImportError:
    pass

# Content cache
try:
    from .content_cache import *
except ImportError:
    pass

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Collect all exports from storage submodules
__all__ = []

for module_name in ['core_storage', 'database_adapter', 'file_storage', 'mongodb_adapter', 
                   'redis_adapter', 'block_storage', 'object_storage', 'content_cache']:
    try:
        module = getattr(__import__(__name__ + '.' + module_name, fromlist=[module_name]), module_name)
        if hasattr(module, '__all__'):
            __all__.extend(module.__all__)
    except (ImportError, AttributeError):
        pass