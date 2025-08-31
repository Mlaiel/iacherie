"""Entity Extraction Module - IA Influencer Agent

Advanced entity extraction module for comprehensive content analysis and AI-powered
entity recognition with business intelligence and monetization insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de

Module Overview:
- Named Entity Recognition (NER) with specialized models
- Platform-specific entity extraction (YouTube, Instagram, TikTok, Spotify)
- Business entity processing for monetization analysis
- Content quality assessment and SEO optimization
- Collaboration opportunity detection
- Relationship extraction and knowledge graph construction
- Real-time entity tracking and monitoring
- Advanced metadata parsing and rights detection
"""# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."

# Import main services
from .index import EntityExtractionService, EntityExtractionOrchestrator

# Import specialized extractors
from .named_entity_recognizer import NamedEntityRecognizer
from .platform_entity_extractor import PlatformEntityExtractor
from .business_entity_processor import BusinessEntityProcessor
from .collaboration_entity_tracker import CollaborationEntityTracker
from .content_entity_analyzer import ContentEntityAnalyzer
from .metadata_entity_parser import MetadataEntityParser
from .relationship_extractor import RelationshipExtractor
from .entity_linker import EntityLinker

# Import utilities and configuration
from .utils import (
    TextProcessor, SimilarityCalculator, PerformanceTimer,
    DataValidator, CacheManager, EntityDeduplicator,
    text_processor, similarity_calculator, performance_timer,
    data_validator, cache_manager, entity_deduplicator
)
from .config import EntityExtractionConfig
from .exceptions import (
    EntityExtractionError, ModelLoadError, ModelInferenceError,
    InvalidInputError, APIConnectionError, RateLimitError,
    DataProcessingError, ConfigurationError, ResourceNotFoundError,
    TimeoutError, CacheError, ValidationError, SecurityError,
    MemoryError, DependencyError, DataQualityError, ConcurrencyError,
    EntityNotFoundError, ExtractionQualityError, ErrorHandler,
    EntityExtractionContext, error_handler
)

# Define public API
__all__ = [
    # Main services
    'EntityExtractionService',
    'EntityExtractionOrchestrator',
    
    # Specialized extractors
    'NamedEntityRecognizer',
    'PlatformEntityExtractor',
    'BusinessEntityProcessor',
    'CollaborationEntityTracker',
    'ContentEntityAnalyzer',
    'MetadataEntityParser',
    'RelationshipExtractor',
    'EntityLinker',
    
    # Utilities
    'TextProcessor',
    'SimilarityCalculator',
    'PerformanceTimer',
    'DataValidator',
    'CacheManager',
    'EntityDeduplicator',
    'text_processor',
    'similarity_calculator',
    'performance_timer',
    'data_validator',
    'cache_manager',
    'entity_deduplicator',
    
    # Configuration
    'EntityExtractionConfig',
    
    # Exceptions
    'EntityExtractionError',
    'ModelLoadError',
    'ModelInferenceError',
    'InvalidInputError',
    'APIConnectionError',
    'RateLimitError',
    'DataProcessingError',
    'ConfigurationError',
    'ResourceNotFoundError',
    'TimeoutError',
    'CacheError',
    'ValidationError',
    'SecurityError',
    'MemoryError',
    'DependencyError',
    'DataQualityError',
    'ConcurrencyError',
    'EntityNotFoundError',
    'ExtractionQualityError',
    'ErrorHandler',
    'EntityExtractionContext',
    'error_handler',
    
    # Module metadata
    '__version__',
    '__author__',
    '__email__',
    '__copyright__'
]

# Module-level configuration
DEFAULT_CONFIG = None

def get_default_config() -> EntityExtractionConfig:
    """Get the default module configuration"""    global DEFAULT_CONFIG
    if DEFAULT_CONFIG is None:
        DEFAULT_CONFIG = EntityExtractionConfig()
    return DEFAULT_CONFIG

def set_default_config(config: EntityExtractionConfig):
    """Set the default module configuration"""    global DEFAULT_CONFIG
    DEFAULT_CONFIG = config

# Initialize module-level services
_service_instance = None
_orchestrator_instance = None

def get_extraction_service(config: EntityExtractionConfig = None) -> EntityExtractionService:
    """Get a shared EntityExtractionService instance"""    global _service_instance
    if _service_instance is None or config is not None:
        _service_instance = EntityExtractionService(config or get_default_config())
    return _service_instance

def get_extraction_orchestrator(config: EntityExtractionConfig = None) -> EntityExtractionOrchestrator:
    """Get a shared EntityExtractionOrchestrator instance"""    global _orchestrator_instance
    if _orchestrator_instance is None or config is not None:
        _orchestrator_instance = EntityExtractionOrchestrator(config or get_default_config())
    return _orchestrator_instance

# Convenience functions for quick access
async def extract_entities(
    text: str,
    entity_types: list = None,
    include_relationships: bool = False,
    config: EntityExtractionConfig = None
) -> dict:
    """    Quick entity extraction function
    
    Args:
        text: Input text to analyze
        entity_types: Specific entity types to extract (optional)
        include_relationships: Whether to extract relationships
        config: Configuration to use (optional)
    
    Returns:
        Dictionary with extracted entities and metadata
    """    service = get_extraction_service(config)
    
    if include_relationships:
        return await service.extract_with_relationships(text, entity_types)
    else:
        return await service.extract_all_entities(text, entity_types)

async def extract_platform_entities(
    content: str,
    platform: str,
    config: EntityExtractionConfig = None
) -> dict:
    """    Quick platform-specific entity extraction
    
    Args:
        content: Content to analyze
        platform: Platform name (youtube, instagram, tiktok, spotify)
        config: Configuration to use (optional)
    
    Returns:
        Dictionary with platform-specific entities
    """    service = get_extraction_service(config)
    return await service.extract_platform_entities(content, platform)

async def analyze_business_entities(
    content: str,
    include_monetization: bool = True,
    config: EntityExtractionConfig = None
) -> dict:
    """    Quick business entity analysis
    
    Args:
        content: Content to analyze
        include_monetization: Whether to include monetization analysis
        config: Configuration to use (optional)
    
    Returns:
        Dictionary with business analysis results
    """    service = get_extraction_service(config)
    return await service.extract_business_entities(content, include_monetization)

# Module initialization
def initialize_module(config: EntityExtractionConfig = None):
    """Initialize the entity extraction module with configuration"""    if config:
        set_default_config(config)
    
    # Pre-load critical models for better performance
    try:
        get_extraction_service()
        print(f"Entity Extraction Module v{__version__} initialized successfully")
    except Exception as e:
        print(f"Warning: Entity Extraction Module initialization failed: {e}")

# Cleanup function
def cleanup_module():
    """Cleanup module resources"""    global _service_instance, _orchestrator_instance
    
    # Clear service instances
    _service_instance = None
    _orchestrator_instance = None
    
    # Clear caches
    cache_manager.clear()
    
    print("Entity Extraction Module cleaned up")

# Module feature flags
FEATURES = {
    'named_entity_recognition': True,
    'platform_entity_extraction': True,
    'business_entity_processing': True,
    'collaboration_tracking': True,
    'content_analysis': True,
    'metadata_parsing': True,
    'relationship_extraction': True,
    'entity_linking': True,
    'real_time_monitoring': True,
    'advanced_caching': True,
    'quality_assessment': True,
    'seo_optimization': True,
    'monetization_analysis': True,
    'rights_detection': True,
    'performance_monitoring': True
}

def get_feature_status() -> dict:
    """Get the status of all module features"""    return FEATURES.copy()

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a specific feature is enabled"""    return FEATURES.get(feature_name, False)

# Module statistics
def get_module_stats() -> dict:
    """Get comprehensive module statistics"""    return {
        'version': __version__,
        'author': __author__,
        'features_enabled': sum(FEATURES.values()),
        'total_features': len(FEATURES),
        'cache_stats': cache_manager.get_stats(),
        'performance_stats': performance_timer.get_stats(),
        'services_initialized': {
            'extraction_service': _service_instance is not None,
            'orchestrator': _orchestrator_instance is not None
        }
    }

# Development utilities (only available in development mode)
try:
    import os
    if os.getenv('ENVIRONMENT') == 'development':
        def debug_entity_extraction(text: str, verbose: bool = True):
            """Debug utility for entity extraction development"""            import asyncio
            
            async def debug_extract():
                service = get_extraction_service()
                result = await service.extract_all_entities(text)
                
                if verbose:
                    print(f"Input: {text}")
                    print(f"Entities found: {len(result.get('entities', []))}")
                    for entity in result.get('entities', []):
                        print(f"  - {entity}")
                
                return result
            
            return asyncio.run(debug_extract())
        
        __all__.append('debug_entity_extraction')

except ImportError:
    pass  # Development utilities not available in production

# Module health check
def health_check() -> dict:
    """Perform module health check"""    health_status = {
        'module': 'entity_extraction',
        'version': __version__,
        'status': 'healthy',
        'checks': {}
    }
    
    try:
        # Check configuration
        config = get_default_config()
        health_status['checks']['configuration'] = 'ok'
        
        # Check cache
        cache_stats = cache_manager.get_stats()
        health_status['checks']['cache'] = 'ok' if cache_stats['size'] >= 0 else 'warning'
        
        # Check services
        health_status['checks']['services'] = 'ok' if _service_instance else 'not_initialized'
        
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['error'] = str(e)
    
    return health_status

# Export convenience functions
__all__.extend([
    'extract_entities',
    'extract_platform_entities',
    'analyze_business_entities',
    'initialize_module',
    'cleanup_module',
    'get_feature_status',
    'is_feature_enabled',
    'get_module_stats',
    'health_check',
    'get_default_config',
    'set_default_config',
    'get_extraction_service',
    'get_extraction_orchestrator'
])

# Module banner
BANNER = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║                    IA Influencer Agent - Entity Extraction                  ║
║                                Version {__version__}                                 ║
║                                                                              ║
║  Advanced AI-powered entity extraction for content creators and influencers ║
║  with business intelligence, monetization analysis, and collaboration tools  ║
║                                                                              ║
║  Author: {__author__}                                           ║
║  Copyright: {__copyright__}                     ║
║                                                                              ║
║  ⚠️  WARNING: This is proprietary software. Unauthorized use prohibited.    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""# Print banner on import (only in development)
import os
if os.getenv('ENVIRONMENT') == 'development' and os.getenv('SHOW_BANNER', '').lower() == 'true':
    print(BANNER)

from .entity_extractor import EntityExtractor
from .named_entity_recognizer import NamedEntityRecognizer  
from .entity_linker import EntityLinker
from .relationship_extractor import RelationshipExtractor
from .content_entity_analyzer import ContentEntityAnalyzer
from .business_entity_processor import BusinessEntityProcessor
from .creative_entity_detector import CreativeEntityDetector
from .metadata_entity_parser import MetadataEntityParser
from .platform_entity_extractor import PlatformEntityExtractor
from .collaboration_entity_tracker import CollaborationEntityTracker

__all__ = [
    'EntityExtractor',
    'NamedEntityRecognizer',
    'EntityLinker', 
    'RelationshipExtractor',
    'ContentEntityAnalyzer',
    'BusinessEntityProcessor',
    'CreativeEntityDetector',
    'MetadataEntityParser',
    'PlatformEntityExtractor',
    'CollaborationEntityTracker'
]

__version__ = '2.0.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
