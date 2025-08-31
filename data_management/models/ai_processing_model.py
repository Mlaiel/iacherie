"""AI Processing Models - IA Influencer Agent Platform Enterprise
© 2025 Fahed Mlaiel. All Rights Reserved.

Advanced AI processing models for content analysis and ML workflows.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class ProcessingStatus(str, Enum):
    """AI processing status tracking."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AIModelType(str, Enum):
    """AI model types for content processing."""
    FINGERPRINT = "fingerprint"
    CLASSIFICATION = "classification"
    TRANSCRIPTION = "transcription"
    GENERATION = "generation"
    ANALYSIS = "analysis"

@dataclass
class AIProcessingJobModel:
    """AI processing job model."""
    job_id: str
    creator_id: str
    content_id: str
    model_type: AIModelType
    status: ProcessingStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

# Alias for backward compatibility
AIProcessingJob = AIProcessingJobModel
ModelType = AIModelType

@dataclass
class ProcessingResult:
    """Processing result model."""
    result_id: str
    job_id: str
    status: ProcessingStatus
    output_data: Dict[str, Any]
    confidence_score: Optional[float]
    processing_time_ms: int
    created_at: datetime

@dataclass
class ModelMetrics:
    """Model performance metrics."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    processing_time_avg_ms: float
    memory_usage_mb: float
    last_updated: datetime

@dataclass
class ProcessingPipeline:
    """Processing pipeline configuration."""
    pipeline_id: str
    name: str
    model_types: List[AIModelType]
    configuration: Dict[str, Any]
    is_active: bool
    created_at: datetime

@dataclass
class QualityAssessment:
    """Quality assessment for processed content."""
    assessment_id: str
    job_id: str
    quality_score: float
    quality_metrics: Dict[str, float]
    recommendations: List[str]
    created_at: datetime

@dataclass
class MLModelVersionModel:
    """ML model version tracking."""
    version_id: str
    model_name: str
    version: str
    model_type: AIModelType
    performance_metrics: Dict[str, float]
    is_active: bool
    created_at: datetime
