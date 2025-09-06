"""Core Event System Module

Foundational classes and utilities for the enterprise event processing system.
Provides base classes, common enums, and core functionality for event handling.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
      Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de)
is strictly prohibited and may result in legal action.

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging

from typing import Dict, Any, Optional, List

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."

# Configure module logging
logger = logging.getLogger(__name__)

# Import core components
from .base_event import BaseEvent
from .base_event_handler import BaseEventHandler
from .event_priority import EventPriority
from .event_status import EventStatus
from .exceptions import (
    EventProcessingError,
    EventValidationError,
    EventSourcingError,
    HandlerNotFoundError,
    ProcessingTimeoutError,
    EventStreamingError
)

# Import business event modules
from .content_events import (
    ContentType,
    ContentUploadEvent,
    ContentValidationEvent,
    ContentProcessingEvent,
    ContentEnrichmentEvent,
    ContentPublishEvent,
    ContentModificationEvent,
    ContentDeletedEvent
)

from .ai_processing_events import (
    AIProcessingType,
    AIFingerprintingEvent,
    AIAnalysisEvent,
    AIClassificationEvent,
    AIEnhancementEvent,
    AIDetectionEvent,
    AIRecommendationEvent,
    AIModelUpdateEvent,
    AIProcessingFailedEvent
)

from .monetization_events import (
    PaymentMethod,
    RevenueType,
    PaymentStatus,
    RevenueGeneratedEvent,
    PaymentProcessedEvent,
    CommissionCalculatedEvent,
    PayoutScheduledEvent,
    SubscriptionEvent,
    RefundProcessedEvent,
    FinancialReportGeneratedEvent,
    FraudDetectedEvent,
    TaxCalculatedEvent
)

# Import infrastructure components
from .event_dispatcher import (
    EventDispatcher,
    EventDispatchMetrics,
    HandlerRegistration
)

from .event_lifecycle import (
    EventLifecycle,
    LifecycleStage,
    EventLifecycleMetadata,
    ValidationRule
)

# Export main classes and enums
__all__ = [
    # Core components
    'BaseEvent',
    'BaseEventHandler',
    'EventPriority',
    'EventStatus',
    'EventProcessingError',
    'EventValidationError',
    'EventSourcingError',
    'HandlerNotFoundError',
    'ProcessingTimeoutError',
    'EventStreamingError',
    'logger',
    
    # Content events
    'ContentType',
    'ContentUploadEvent',
    'ContentValidationEvent',
    'ContentProcessingEvent',
    'ContentEnrichmentEvent',
    'ContentPublishEvent',
    'ContentModificationEvent',
    'ContentDeletedEvent',
    
    # AI processing events
    'AIProcessingType',
    'AIFingerprintingEvent',
    'AIAnalysisEvent',
    'AIClassificationEvent',
    'AIEnhancementEvent',
    'AIDetectionEvent',
    'AIRecommendationEvent',
    'AIModelUpdateEvent',
    'AIProcessingFailedEvent',
    
    # Monetization events
    'PaymentMethod',
    'RevenueType',
    'PaymentStatus',
    'RevenueGeneratedEvent',
    'PaymentProcessedEvent',
    'CommissionCalculatedEvent',
    'PayoutScheduledEvent',
    'SubscriptionEvent',
    'RefundProcessedEvent',
    'FinancialReportGeneratedEvent',
    'FraudDetectedEvent',
    'TaxCalculatedEvent',
    
    # Infrastructure components
    'EventDispatcher',
    'EventDispatchMetrics',
    'HandlerRegistration',
    'EventLifecycle',
    'LifecycleStage',
    'EventLifecycleMetadata',
    'ValidationRule'
]

logger.info("Core event system module initialized successfully")
