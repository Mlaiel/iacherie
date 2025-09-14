"""Audio Events Module Index - Central Entry Point
from typing import Dict, List, Optional, Union, Tuple

==============================================

This module provides centralized access to all audio event classes and handlers
for the IA Influencer Agent platform's event-driven architecture.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Usage:
    from backend.events.audio_events import (
        AudioUploadStartedEvent,
        AudioProcessingCompletedEvent,
        AudioFingerprintingEventHandler,
        # ... other imports
    )
"""# Import all event classes for easy access
from .upload_events import (
    AudioUploadStartedEvent,
    AudioUploadProgressEvent,
    AudioUploadCompletedEvent,
    AudioUploadFailedEvent,
    AudioUploadValidationEvent,
    AudioUploadVirusScanEvent,
    AudioUploadMetadataExtractedEvent,
    AudioUploadDuplicateDetectedEvent,
    AudioUploadQuotaExceededEvent
)

from .processing_events import (
    AudioProcessingStartedEvent,
    AudioProcessingProgressEvent,
    AudioProcessingCompletedEvent,
    AudioProcessingFailedEvent,
    AudioQualityAnalysisEvent,
    AudioFormatConversionEvent,
    AudioNormalizationEvent,
    AudioCompressionEvent,
    AudioSpectrumAnalysisEvent,
    ProcessingStage,
    ProcessingQuality
)

from .fingerprinting_events import (
    AudioFingerprintingStartedEvent,
    AudioFingerprintingProgressEvent,
    AudioFingerprintingCompletedEvent,
    AudioFingerprintingFailedEvent,
    AudioMatchFoundEvent,
    AudioCopyrightViolationEvent,
    AudioSimilarityAnalysisEvent,
    AudioFingerprintDatabaseUpdatedEvent,
    AudioFingerprintSearchEvent,
    FingerprintingMethod,
    MatchConfidence,
    ViolationType
)

from .analysis_events import (
    AudioAnalysisStartedEvent,
    AudioAnalysisProgressEvent,
    AudioAnalysisCompletedEvent,
    AudioAnalysisFailedEvent,
    AudioGenreDetectionEvent,
    AudioMoodAnalysisEvent,
    AudioBPMDetectionEvent,
    AudioKeyDetectionEvent,
    AudioInstrumentRecognitionEvent,
    AudioVocalAnalysisEvent,
    AnalysisType,
    MusicalKey,
    TimeSignature
)

from .enhancement_events import (
    AudioEnhancementStartedEvent,
    AudioEnhancementProgressEvent,
    AudioEnhancementCompletedEvent,
    AudioEnhancementFailedEvent,
    AudioNoiseReductionEvent,
    AudioMasteringEvent,
    AudioRestorationEvent,
    AudioSpatialEnhancementEvent,
    AudioVocalEnhancementEvent,
    EnhancementType,
    NoiseType,
    MasteringPreset
)

from .collaboration_events import (
    AudioCollaborationRequestEvent,
    AudioCollaborationAcceptedEvent,
    AudioCollaborationRejectedEvent,
    AudioRemixCreatedEvent,
    AudioVersionCreatedEvent,
    AudioCollaborationFeedbackEvent,
    AudioCollaborationMilestoneEvent,
    AudioCollaborationCompletedEvent,
    AudioSampleUsageEvent,
    CollaborationType,
    CollaborationStatus,
    RemixType
)

from .monetization_events import (
    AudioMonetizationStartedEvent,
    AudioLicenseCreatedEvent,
    AudioRevenueGeneratedEvent,
    AudioRoyaltyDistributedEvent,
    AudioSaleCompletedEvent,
    AudioStreamingRevenueEvent,
    AudioSyncLicenseRequestEvent,
    AudioPerformanceRoyaltyEvent,
    AudioMonetizationAnalyticsEvent,
    LicenseType,
    RevenueSource,
    PaymentStatus
)

from .streaming_events import (
    AudioStreamStartedEvent,
    AudioStreamEndedEvent,
    AudioStreamQualityChangedEvent,
    AudioLiveStreamStartedEvent,
    AudioLiveStreamEndedEvent,
    AudioStreamListenerJoinedEvent,
    AudioStreamListenerLeftEvent,
    AudioStreamBufferingEvent,
    AudioStreamAnalyticsEvent,
    AudioStreamErrorEvent,
    StreamingProtocol,
    StreamQuality,
    StreamingPlatform
)

from .event_handlers import (
    AudioUploadEventHandler,
    AudioProcessingEventHandler,
    AudioFingerprintingEventHandler,
    AudioAnalysisEventHandler,
    AudioEnhancementEventHandler,
    AudioCollaborationEventHandler,
    AudioMonetizationEventHandler,
    AudioStreamingEventHandler
)

# Export version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Define what gets imported with "from audio_events import *"
__all__ = [
    # Upload Events
    "AudioUploadStartedEvent",
    "AudioUploadProgressEvent",
    "AudioUploadCompletedEvent",
    "AudioUploadFailedEvent",
    "AudioUploadValidationEvent",
    "AudioUploadVirusScanEvent",
    "AudioUploadMetadataExtractedEvent",
    "AudioUploadDuplicateDetectedEvent",
    "AudioUploadQuotaExceededEvent",
    
    # Processing Events
    "AudioProcessingStartedEvent",
    "AudioProcessingProgressEvent",
    "AudioProcessingCompletedEvent",
    "AudioProcessingFailedEvent",
    "AudioQualityAnalysisEvent",
    "AudioFormatConversionEvent",
    "AudioNormalizationEvent",
    "AudioCompressionEvent",
    "AudioSpectrumAnalysisEvent",
    "ProcessingStage",
    "ProcessingQuality",
    
    # Fingerprinting Events
    "AudioFingerprintingStartedEvent",
    "AudioFingerprintingProgressEvent",
    "AudioFingerprintingCompletedEvent",
    "AudioFingerprintingFailedEvent",
    "AudioMatchFoundEvent",
    "AudioCopyrightViolationEvent",
    "AudioSimilarityAnalysisEvent",
    "AudioFingerprintDatabaseUpdatedEvent",
    "AudioFingerprintSearchEvent",
    "FingerprintingMethod",
    "MatchConfidence",
    "ViolationType",
    
    # Analysis Events
    "AudioAnalysisStartedEvent",
    "AudioAnalysisProgressEvent",
    "AudioAnalysisCompletedEvent",
    "AudioAnalysisFailedEvent",
    "AudioGenreDetectionEvent",
    "AudioMoodAnalysisEvent",
    "AudioBPMDetectionEvent",
    "AudioKeyDetectionEvent",
    "AudioInstrumentRecognitionEvent",
    "AudioVocalAnalysisEvent",
    "AnalysisType",
    "MusicalKey",
    "TimeSignature",
    
    # Enhancement Events
    "AudioEnhancementStartedEvent",
    "AudioEnhancementProgressEvent",
    "AudioEnhancementCompletedEvent",
    "AudioEnhancementFailedEvent",
    "AudioNoiseReductionEvent",
    "AudioMasteringEvent",
    "AudioRestorationEvent",
    "AudioSpatialEnhancementEvent",
    "AudioVocalEnhancementEvent",
    "EnhancementType",
    "NoiseType",
    "MasteringPreset",
    
    # Collaboration Events
    "AudioCollaborationRequestEvent",
    "AudioCollaborationAcceptedEvent",
    "AudioCollaborationRejectedEvent",
    "AudioRemixCreatedEvent",
    "AudioVersionCreatedEvent",
    "AudioCollaborationFeedbackEvent",
    "AudioCollaborationMilestoneEvent",
    "AudioCollaborationCompletedEvent",
    "AudioSampleUsageEvent",
    "CollaborationType",
    "CollaborationStatus",
    "RemixType",
    
    # Monetization Events
    "AudioMonetizationStartedEvent",
    "AudioLicenseCreatedEvent",
    "AudioRevenueGeneratedEvent",
    "AudioRoyaltyDistributedEvent",
    "AudioSaleCompletedEvent",
    "AudioStreamingRevenueEvent",
    "AudioSyncLicenseRequestEvent",
    "AudioPerformanceRoyaltyEvent",
    "AudioMonetizationAnalyticsEvent",
    "LicenseType",
    "RevenueSource",
    "PaymentStatus",
    
    # Streaming Events
    "AudioStreamStartedEvent",
    "AudioStreamEndedEvent",
    "AudioStreamQualityChangedEvent",
    "AudioLiveStreamStartedEvent",
    "AudioLiveStreamEndedEvent",
    "AudioStreamListenerJoinedEvent",
    "AudioStreamListenerLeftEvent",
    "AudioStreamBufferingEvent",
    "AudioStreamAnalyticsEvent",
    "AudioStreamErrorEvent",
    "StreamingProtocol",
    "StreamQuality",
    "StreamingPlatform",
    
    # Event Handlers
    "AudioUploadEventHandler",
    "AudioProcessingEventHandler",
    "AudioFingerprintingEventHandler",
    "AudioAnalysisEventHandler",
    "AudioEnhancementEventHandler",
    "AudioCollaborationEventHandler",
    "AudioMonetizationEventHandler",
    "AudioStreamingEventHandler"
]


def get_all_audio_event_types() -> None:
    """
    Returns a list of all audio event types for registration purposes.
    
    Returns:
        List[type]: List of all audio event classes
    """
    return [
        # Upload Events
        AudioUploadStartedEvent,
        AudioUploadProgressEvent,
        AudioUploadCompletedEvent,
        AudioUploadFailedEvent,
        AudioUploadValidationEvent,
        AudioUploadVirusScanEvent,
        AudioUploadMetadataExtractedEvent,
        AudioUploadDuplicateDetectedEvent,
        AudioUploadQuotaExceededEvent,
        
        # Processing Events
        AudioProcessingStartedEvent,
        AudioProcessingProgressEvent,
        AudioProcessingCompletedEvent,
        AudioProcessingFailedEvent,
        AudioQualityAnalysisEvent,
        AudioFormatConversionEvent,
        AudioNormalizationEvent,
        AudioCompressionEvent,
        AudioSpectrumAnalysisEvent,
        
        # Fingerprinting Events
        AudioFingerprintingStartedEvent,
        AudioFingerprintingProgressEvent,
        AudioFingerprintingCompletedEvent,
        AudioFingerprintingFailedEvent,
        AudioMatchFoundEvent,
        AudioCopyrightViolationEvent,
        AudioSimilarityAnalysisEvent,
        AudioFingerprintDatabaseUpdatedEvent,
        AudioFingerprintSearchEvent,
        
        # Analysis Events
        AudioAnalysisStartedEvent,
        AudioAnalysisProgressEvent,
        AudioAnalysisCompletedEvent,
        AudioAnalysisFailedEvent,
        AudioGenreDetectionEvent,
        AudioMoodAnalysisEvent,
        AudioBPMDetectionEvent,
        AudioKeyDetectionEvent,
        AudioInstrumentRecognitionEvent,
        AudioVocalAnalysisEvent,
        
        # Enhancement Events
        AudioEnhancementStartedEvent,
        AudioEnhancementProgressEvent,
        AudioEnhancementCompletedEvent,
        AudioEnhancementFailedEvent,
        AudioNoiseReductionEvent,
        AudioMasteringEvent,
        AudioRestorationEvent,
        AudioSpatialEnhancementEvent,
        AudioVocalEnhancementEvent,
        
        # Collaboration Events
        AudioCollaborationRequestEvent,
        AudioCollaborationAcceptedEvent,
        AudioCollaborationRejectedEvent,
        AudioRemixCreatedEvent,
        AudioVersionCreatedEvent,
        AudioCollaborationFeedbackEvent,
        AudioCollaborationMilestoneEvent,
        AudioCollaborationCompletedEvent,
        AudioSampleUsageEvent,
        
        # Monetization Events
        AudioMonetizationStartedEvent,
        AudioLicenseCreatedEvent,
        AudioRevenueGeneratedEvent,
        AudioRoyaltyDistributedEvent,
        AudioSaleCompletedEvent,
        AudioStreamingRevenueEvent,
        AudioSyncLicenseRequestEvent,
        AudioPerformanceRoyaltyEvent,
        AudioMonetizationAnalyticsEvent,
        
        # Streaming Events
        AudioStreamStartedEvent,
        AudioStreamEndedEvent,
        AudioStreamQualityChangedEvent,
        AudioLiveStreamStartedEvent,
        AudioLiveStreamEndedEvent,
        AudioStreamListenerJoinedEvent,
        AudioStreamListenerLeftEvent,
        AudioStreamBufferingEvent,
        AudioStreamAnalyticsEvent,
        AudioStreamErrorEvent
    ]


def get_all_audio_event_handlers() -> None:
    """
    Returns a list of all audio event handler classes.
    
    Returns:
        List[type]: List of all audio event handler classes
    """
    return [
        AudioUploadEventHandler,
        AudioProcessingEventHandler,
        AudioFingerprintingEventHandler,
        AudioAnalysisEventHandler,
        AudioEnhancementEventHandler,
        AudioCollaborationEventHandler,
        AudioMonetizationEventHandler,
        AudioStreamingEventHandler
    ]


def register_all_audio_event_handlers(event_bus, services) -> None:
    """
    Register all audio event handlers with the event bus.
    
    Args:
        event_bus: The event bus instance
        services: Dictionary containing all required services
        
    Returns:
        List: List of registered handler instances
    """
    handlers = []
    
    # Register upload event handler
    upload_handler = AudioUploadEventHandler(
        event_bus=event_bus,
        audio_service=services.get('audio_service'),
        storage_service=services.get('storage_service'),
        notification_service=services.get('notification_service')
    )
    handlers.append(upload_handler)
    
    # Register processing event handler
    processing_handler = AudioProcessingEventHandler(
        event_bus=event_bus,
        audio_service=services.get('audio_service'),
        enhancement_service=services.get('enhancement_service'),
        notification_service=services.get('notification_service')
    )
    handlers.append(processing_handler)
    
    # Register fingerprinting event handler
    fingerprinting_handler = AudioFingerprintingEventHandler(
        event_bus=event_bus,
        fingerprinting_service=services.get('fingerprinting_service'),
        copyright_service=services.get('copyright_service'),
        notification_service=services.get('notification_service')
    )
    handlers.append(fingerprinting_handler)
    
    # Register analysis event handler
    analysis_handler = AudioAnalysisEventHandler(
        event_bus=event_bus,
        analysis_service=services.get('analysis_service'),
        ai_service=services.get('ai_service'),
        recommendation_service=services.get('recommendation_service')
    )
    handlers.append(analysis_handler)
    
    # Register enhancement event handler
    enhancement_handler = AudioEnhancementEventHandler(
        event_bus=event_bus,
        enhancement_service=services.get('enhancement_service'),
        mastering_service=services.get('mastering_service'),
        quality_service=services.get('quality_service')
    )
    handlers.append(enhancement_handler)
    
    # Register collaboration event handler
    collaboration_handler = AudioCollaborationEventHandler(
        event_bus=event_bus,
        collaboration_service=services.get('collaboration_service'),
        version_control_service=services.get('version_control_service'),
        workflow_service=services.get('workflow_service')
    )
    handlers.append(collaboration_handler)
    
    # Register monetization event handler
    monetization_handler = AudioMonetizationEventHandler(
        event_bus=event_bus,
        monetization_service=services.get('monetization_service'),
        licensing_service=services.get('licensing_service'),
        payment_service=services.get('payment_service')
    )
    handlers.append(monetization_handler)
    
    # Register streaming event handler
    streaming_handler = AudioStreamingEventHandler(
        event_bus=event_bus,
        streaming_service=services.get('streaming_service'),
        analytics_service=services.get('analytics_service'),
        audience_service=services.get('audience_service')
    )
    handlers.append(streaming_handler)
    
    return handlers
