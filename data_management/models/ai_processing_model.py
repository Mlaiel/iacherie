"""
AI Processing Models - IA Influencer Agent Platform Enterprise
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
