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
                 content_id: str,
                 fingerprint_type: str,
                 algorithm: str,
                 fingerprint_data: Dict[str, Any],
                 confidence_score: float,
                 processing_time: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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
                 content_id: str,
                 analysis_type: str,
                 analysis_results: Dict[str, Any],
                 confidence_scores: Dict[str, float],
                 detected_features: List[str],
                 processing_duration: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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
                 content_id: str,
                 classification_model: str,
                 predicted_categories: List[Dict[str, Any]],
                 confidence_threshold: float,
                 model_version: str,
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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
                 content_id: str,
                 enhancement_type: str,
                 enhancement_config: Dict[str, Any],
                 quality_metrics: Dict[str, float],
                 enhancement_results: Dict[str, Any],
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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
                 content_id: str,
                 detection_type: str,
                 detected_issues: List[Dict[str, Any]],
                 severity_level: str,
                 action_required: bool,
                 detection_confidence: float,
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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
                 content_id: str,
                 recommendation_type: str,
                 recommendations: List[Dict[str, Any]],
                 recommendation_scores: Dict[str, float],
                 reasoning: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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
                 model_id: str,
                 model_type: str,
                 version: str,
                 update_type: str,
                 performance_metrics: Dict[str, float],
                 training_data_size: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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
                 content_id: str,
                 processing_type: AIProcessingType,
                 error_code: str,
                 error_message: str,
                 retry_count: int,
                 max_retries: int,
                 metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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