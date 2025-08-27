"""
IA Influencer Agent - Audio Source Separation Module

Professional audio separation engine for content creators using advanced AI models.
Enables vocal isolation, instrument separation, and stem extraction for music production.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - Unauthorized use strictly prohibited
License: Proprietary - Contact for licensing

⚠️ WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or modification is strictly
prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.

🎵 PROFESSIONAL AUDIO SEPARATION SUITE 🎵
- Advanced AI-powered source separation
- Multi-format support (vocals, instruments, drums, bass)
- Real-time processing capabilities
- Professional quality analysis
- Batch processing for production workflows
- Industry-standard output formats
"""

from .core import (
    SeparationEngine, 
    SeparationConfig,
    SeparationModel,
    SeparationQuality,
    OutputFormat
)
from .models import (
    VocalSeparator, 
    InstrumentSeparator, 
    DrumSeparator, 
    BassSeparator,
    SeparationResult,
    create_separator
)
from .processors import (
    AudioProcessor, 
    StemProcessor, 
    QualityAnalyzer,
    ProcessingConfig,
    ProcessingResult
)
from .utils import (
    AudioValidator, 
    FormatConverter, 
    MetadataExtractor,
    AudioMetadata,
    ValidationResult,
    validate_and_convert_audio,
    calculate_audio_similarity
)
from .services import (
    SeparationService,
    BatchProcessor,
    RealtimeProcessor,
    SeparationRequest,
    SeparationResponse,
    ServiceRegistry,
    create_separation_service,
    create_batch_processor,
    create_realtime_processor,
    setup_default_services
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"
__copyright__ = "Copyright 2025 Fahed Mlaiel - All Rights Reserved"

# Team Expertise
__team_expertise__ = [
    "Lead Developer AI & Machine Learning - Fahed Mlaiel",
    "Senior Backend Architecture - Advanced Python/FastAPI",  
    "ML Engineer - Deep Learning & Audio Processing",
    "Database Administrator - PostgreSQL & Vector Databases",
    "Security Engineer - Enterprise Security & Authentication",
    "Microservices Architect - Scalable Distributed Systems",
    "Audio Engineer - Professional Audio Processing", 
    "DevOps Engineer - CI/CD & Cloud Infrastructure",
    "IA Prompt Engineer - Advanced AI Model Training"
]

__all__ = [
    # Core components
    "SeparationEngine",
    "SeparationConfig", 
    "SeparationModel",
    "SeparationQuality",
    "OutputFormat",
    
    # AI Models
    "VocalSeparator",
    "InstrumentSeparator", 
    "DrumSeparator",
    "BassSeparator",
    "SeparationResult",
    "create_separator",
    
    # Processors
    "AudioProcessor",
    "StemProcessor", 
    "QualityAnalyzer",
    "ProcessingConfig",
    "ProcessingResult",
    
    # Utilities
    "AudioValidator",
    "FormatConverter",
    "MetadataExtractor",
    "AudioMetadata",
    "ValidationResult", 
    "validate_and_convert_audio",
    "calculate_audio_similarity",
    
    # Services
    "SeparationService",
    "BatchProcessor",
    "RealtimeProcessor",
    "SeparationRequest",
    "SeparationResponse",
    "ServiceRegistry",
    "create_separation_service",
    "create_batch_processor", 
    "create_realtime_processor",
    "setup_default_services"
]

# Initialize default services on module import
try:
    setup_default_services()
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f"Failed to setup default services: {e}")

# Module information for introspection
def get_module_info():
    """Get comprehensive module information."""
    return {
        "name": "audio.separation",
        "version": __version__,
        "author": __author__, 
        "email": __email__,
        "license": __license__,
        "copyright": __copyright__,
        "team_expertise": __team_expertise__,
        "components": len(__all__),
        "description": "Professional AI-powered audio source separation suite"
    }
