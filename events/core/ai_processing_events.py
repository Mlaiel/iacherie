"""AI Processing Events Module

AI-powered content analysis, fingerprinting, and enhancement events.
Handles all AI-related processing operations for content protection and optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from .base_event import BaseEvent
from .event_priority import EventPriority
from .event_status import EventStatus

logger = logging.getLogger(__name__)


class AIProcessingType(Enum):
    """AI processing type enumeration"""
    FINGERPRINTING = "fingerprinting"
    ANALYSIS = "analysis" 
    CLASSIFICATION = "classification"
    ENHANCEMENT = "enhancement"
    DETECTION = "detection"
    RECOMMENDATION = "recommendation"
    TRANSCRIPTION = "transcription"
    TRANSLATION = "translation"


class AIFingerprintingEvent(BaseEvent):
    """Event triggered when AI generates content fingerprint"""
    
    def __init__(self,
                 content_id -> None: str,
                 fingerprint_type -> None: str,
                 algorithm -> None: str,
                 fingerprint_data -> None: Dict[str, Any],
                 confidence_score -> None: float,
                 processing_time -> None: Optional[float] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'fingerprint_type': fingerprint_type,
            'algorithm': algorithm,
            'fingerprint_data': fingerprint_data,
            'confidence_score': confidence_score,
            'processing_time': processing_time,
            'fingerprint_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="ai.fingerprinting.completed",
            data=data,
            priority=EventPriority.HIGH,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class AIAnalysisEvent(BaseEvent):
    """Event triggered when AI analyzes content"""
    
    def __init__(self,
                 content_id -> None: str,
                 analysis_type -> None: str,
                 analysis_results -> None: Dict[str, Any],
                 confidence_scores -> None: Dict[str, float],
                 detected_features -> None: List[str],
                 processing_duration -> None: Optional[float] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'analysis_type': analysis_type,
            'analysis_results': analysis_results,
            'confidence_scores': confidence_scores,
            'detected_features': detected_features,
            'processing_duration': processing_duration,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="ai.analysis.completed",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class AIClassificationEvent(BaseEvent):
    """Event triggered when AI classifies content"""
    
    def __init__(self,
                 content_id -> None: str,
                 classification_model -> None: str,
                 predicted_categories -> None: List[Dict[str, Any]],
                 confidence_threshold -> None: float,
                 model_version -> None: str,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'classification_model': classification_model,
            'predicted_categories': predicted_categories,
            'confidence_threshold': confidence_threshold,
            'model_version': model_version,
            'classification_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="ai.classification.completed",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class AIEnhancementEvent(BaseEvent):
    """Event triggered when AI enhances content quality"""
    
    def __init__(self,
                 content_id -> None: str,
                 enhancement_type -> None: str,
                 enhancement_config -> None: Dict[str, Any],
                 quality_metrics -> None: Dict[str, float],
                 enhancement_results -> None: Dict[str, Any],
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'enhancement_type': enhancement_type,
            'enhancement_config': enhancement_config,
            'quality_metrics': quality_metrics,
            'enhancement_results': enhancement_results,
            'enhancement_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="ai.enhancement.completed",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class AIDetectionEvent(BaseEvent):
    """Event triggered when AI detects violations or issues"""
    
    def __init__(self,
                 content_id -> None: str,
                 detection_type -> None: str,
                 detected_issues -> None: List[Dict[str, Any]],
                 severity_level -> None: str,
                 action_required -> None: bool,
                 detection_confidence -> None: float,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'detection_type': detection_type,
            'detected_issues': detected_issues,
            'severity_level': severity_level,
            'action_required': action_required,
            'detection_confidence': detection_confidence,
            'detection_timestamp': datetime.utcnow().isoformat()
        }
        
        priority_map = {
            'low': EventPriority.LOW,
            'medium': EventPriority.MEDIUM,
            'high': EventPriority.HIGH,
            'critical': EventPriority.CRITICAL,
            'emergency': EventPriority.EMERGENCY
        }
        
        super().__init__(
            event_type="ai.detection.completed",
            data=data,
            priority=priority_map.get(severity_level.lower(), EventPriority.MEDIUM),
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class AIRecommendationEvent(BaseEvent):
    """Event triggered when AI generates recommendations"""
    
    def __init__(self,
                 content_id -> None: str,
                 recommendation_type -> None: str,
                 recommendations -> None: List[Dict[str, Any]],
                 recommendation_scores -> None: Dict[str, float],
                 reasoning -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'recommendation_type': recommendation_type,
            'recommendations': recommendations,
            'recommendation_scores': recommendation_scores,
            'reasoning': reasoning,
            'recommendation_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="ai.recommendation.generated",
            data=data,
            priority=EventPriority.LOW,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class AIModelUpdateEvent(BaseEvent):
    """Event triggered when AI models are updated or retrained"""
    
    def __init__(self,
                 model_id -> None: str,
                 model_type -> None: str,
                 version -> None: str,
                 update_type -> None: str,
                 performance_metrics -> None: Dict[str, float],
                 training_data_size -> None: Optional[int] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'model_id': model_id,
            'model_type': model_type,
            'version': version,
            'update_type': update_type,
            'performance_metrics': performance_metrics,
            'training_data_size': training_data_size,
            'update_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="ai.model.updated",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class AIProcessingFailedEvent(BaseEvent):
    """Event triggered when AI processing fails"""
    
    def __init__(self,
                 content_id -> None: str,
                 processing_type -> None: AIProcessingType,
                 error_code -> None: str,
                 error_message -> None: str,
                 retry_count -> None: int,
                 max_retries -> None: int,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'content_id': content_id,
            'processing_type': processing_type.value,
            'error_code': error_code,
            'error_message': error_message,
            'retry_count': retry_count,
            'max_retries': max_retries,
            'failure_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="ai.processing.failed",
            data=data,
            priority=EventPriority.HIGH,
            status=EventStatus.FAILED,
            error_message=error_message,
            metadata=metadata or {},
            **kwargs
        )


# Export all AI processing event classes
__all__ = [
    'AIProcessingType',
    'AIFingerprintingEvent',
    'AIAnalysisEvent',
    'AIClassificationEvent',
    'AIEnhancementEvent',
    'AIDetectionEvent',
    'AIRecommendationEvent',
    'AIModelUpdateEvent',
    'AIProcessingFailedEvent'
]

logger.info("AI processing events module initialized successfully")