"""Backend Configuration Module - Consolidated Configuration Management
=====================================================================

Consolidated configuration system for IA-Influencer Agent Platform.
This module consolidates all configuration modules from the main config/ directory
into 12 focused configuration files organized by domain.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

# Import consolidated configuration modules
try:
    from . import database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

try:
    from . import cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from . import ai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Additional modules will be imported as they are created
# from . import api  
# from . import security
# from . import monetization
# from . import monitoring
# from . import storage
# from . import deployment
# from . import integrations
# from . import business

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - All rights reserved"

# Export available modules
available_modules = []
if DATABASE_AVAILABLE:
    available_modules.append("database")
if CACHE_AVAILABLE:
    available_modules.append("cache")
if AI_AVAILABLE:
    available_modules.append("ai")

__all__ = available_modules