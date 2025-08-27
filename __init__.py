# Core application initialization
from .config import settings
from .core.database import database_manager
from .core.security import security_manager
from .core.cache import cache_manager

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__title__ = "Ainflue"
__description__ = "AI-Powered Content Protection & Monetization Platform"

# Core services
__all__ = [
    "settings",
    "database_manager", 
    "security_manager",
    "cache_manager"
]