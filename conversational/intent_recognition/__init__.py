"""Intent Recognition Module - Initialization

Advanced intent recognition system for creative industry professionals
including musicians, influencers, photographers, bloggers, and content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
from .intent_classifier import (
    IntentClassifier,
    IntentCategory,
    IntentConfidence,
    ClassificationResult
)

from .intent_detector import (
    IntentDetector,
    DetectionMode,
    RealTimeIntentProcessor
)

from .conversation_intent_tracker import (
    ConversationIntentTracker,
    IntentSessionManager,
    ConversationContext
)

from .multi_intent_resolver import (
    MultiIntentResolver,
    IntentConflictResolver,
    IntentPriorityManager
)

from .intent_confidence_scorer import (
    IntentConfidenceScorer,
    ConfidenceMetrics,
    UncertaintyQuantifier,
    ConfidenceLevel,
    UncertaintyType
)

from .contextual_intent_processor import (
    ContextualIntentProcessor,
    ContextualEnhancer,
    ConversationContext,
    UserProfileContext,
    TemporalContext,
    BusinessContext,
    ContextualEnhancement
)

from .business_intent_analyzer import (
    BusinessIntentAnalyzer,
    BusinessIntentAnalysis,
    MonetizationOpportunity,
    BusinessIntentCategory,
    RevenueStreamType,
    BusinessPriority
)

from .platform_specific_intents import (
    PlatformSpecificIntentProcessor,
    PlatformIntentAnalysis,
    Platform,
    PlatformIntentType,
    ContentType,
    PlatformSpecification
)

from .semantic_intent_analyzer import (
    SemanticIntentAnalyzer
)

from .creative_workflow_intents import (
    CreativeWorkflowIntents,
    ContentCreationIntents,
    CollaborationIntents
)

from .monetization_intent_handler import (
    MonetizationIntentHandler,
    RevenueIntentClassifier,
    LicensingIntentProcessor
)

from .collaboration_intent_manager import (
    CollaborationIntentManager,
    TeamWorkflowIntents,
    PermissionIntentHandler
)

from .config import (
    IntentRecognitionConfig,
    ModelConfiguration,
    PerformanceSettings
)

from .exceptions import (
    IntentRecognitionError,
    ClassificationError,
    ConfigurationError,
    ModelLoadError
)

from .utils import (
    intent_preprocessing,
    confidence_calibration,
    performance_monitoring
)

# Version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced Intent Recognition for Creative Industry"

# Module configuration
__all__ = [
    # Core Components
    "IntentClassifier",
    "IntentDetector", 
    "ConversationIntentTracker",
    "MultiIntentResolver",
    "IntentConfidenceScorer",
    "ContextualIntentProcessor",
    
    # Specialized Handlers
    "CreativeWorkflowIntents",
    "MonetizationIntentHandler",
    "CollaborationIntentManager",
    
    # Data Types
    "IntentCategory",
    "IntentConfidence",
    "ClassificationResult",
    "DetectionMode",
    "ConversationContext",
    "ConfidenceMetrics",
    
    # Configuration
    "IntentRecognitionConfig",
    "ModelConfiguration",
    "PerformanceSettings",
    
    # Exceptions
    "IntentRecognitionError",
    "ClassificationError",
    "ConfigurationError",
    "ModelLoadError",
    
    # Utilities
    "intent_preprocessing",
    "confidence_calibration", 
    "performance_monitoring"
]

# Module initialization logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Intent Recognition Module v{__version__} initialized")
logger.info(f"Author: {__author__} ({__email__})")
logger.info("Ready for advanced conversational intent processing")
