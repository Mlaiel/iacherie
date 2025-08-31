"""Natural Language Processing (NLP) Module

Advanced NLP capabilities for content analysis, text processing, and language understanding.
Supports multi-format content processing for the IA Influencer Agent Platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de

Team Specialties:
- Lead AI Developer: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- AI Prompt Engineer: Fahed Mlaiel
"""# Core NLP modules
from . import core
from . import processors
from . import analyzers
from . import generators
from . import fingerprinting
from . import seo
from . import translation
from . import sentiment
from . import classification
from . import extraction
from . import monitoring
from . import models
from . import utils

# Advanced professional modules
from . import content_intelligence
from . import creator_recommendations  
from . import content_protection
from . import revenue_optimization
from . import performance_intelligence
from . import market_insights
from . import brand_voice
from . import collaborative_matching
from . import multiformat_processing

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__platform__ = "IA Influencer Agent Platform"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    # Core modules
    "core",
    "processors", 
    "analyzers",
    "generators",
    "fingerprinting",
    "seo",
    "translation",
    "sentiment",
    "classification",
    "extraction",
    "monitoring",
    "models",
    "utils",
    
    # Professional modules
    "content_intelligence",
    "creator_recommendations",
    "content_protection", 
    "revenue_optimization",
    "performance_intelligence",
    "market_insights",
    "brand_voice",
    "collaborative_matching",
    "multiformat_processing"
]

# Module level constants
SUPPORTED_LANGUAGES = ["en", "fr", "de", "ar"]
SUPPORTED_FORMATS = ["text", "audio", "video", "image_captions"]
DEFAULT_ENCODING = "utf-8"
MAX_TEXT_LENGTH = 1000000  # 1MB text limit
PROCESSING_TIMEOUT = 300   # 5 minutes timeout

# Performance settings
BATCH_SIZE = 100
WORKER_PROCESSES = 4
CACHE_TTL = 3600  # 1 hour cache

# Security settings
MAX_REQUESTS_PER_MINUTE = 1000
CONTENT_FILTERING_ENABLED = True
AUDIT_LOGGING_ENABLED = True