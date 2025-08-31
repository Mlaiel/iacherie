"""Audio Format Conversion Module - Professional Multi-Format Processing Engine

Ultra-advanced audio format conversion and optimization system designed for the IA Influencer Agent platform.
Provides professional-grade format conversion, quality preservation, and metadata handling capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from .converter import (
    AudioFormatConverter,
    ConversionEngine,
    BatchConverter
)
from .quality import (
    QualityController,
    QualityMetrics,
    QualityOptimizer
)
from .metadata import (
    MetadataManager,
    MetadataExtractor,
    MetadataInjector
)
from .formats import (
    FormatRegistry,
    FormatValidator,
    SupportedFormats
)
from .processors import (
    ProcessorChain,
    AudioProcessor,
    EffectsProcessor
)
from .utils import (
    ConversionUtils,
    FileUtils,
    CompressionUtils
)
from .models import (
    ConversionRequest,
    ConversionResult,
    FormatSpecification,
    QualityProfile,
    ProcessingOptions
)
from .config import (
    ConversionConfig,
    QualityConfig,
    FormatConfig
)

__all__ = [
    # Core Conversion Classes
    'AudioFormatConverter',
    'ConversionEngine', 
    'BatchConverter',
    
    # Quality Management
    'QualityController',
    'QualityMetrics',
    'QualityOptimizer',
    
    # Metadata Handling
    'MetadataManager',
    'MetadataExtractor',
    'MetadataInjector',
    
    # Format Management
    'FormatRegistry',
    'FormatValidator',
    'SupportedFormats',
    
    # Processing
    'ProcessorChain',
    'AudioProcessor',
    'EffectsProcessor',
    
    # Utilities
    'ConversionUtils',
    'FileUtils',
    'CompressionUtils',
    
    # Models
    'ConversionRequest',
    'ConversionResult',
    'FormatSpecification',
    'QualityProfile',
    'ProcessingOptions',
    
    # Configuration
    'ConversionConfig',
    'QualityConfig',
    'FormatConfig'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
