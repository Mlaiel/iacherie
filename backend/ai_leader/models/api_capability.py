"""
API Capability Model
Represents a learned capability that can replace external APIs
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class CapabilityType(str, Enum):
    """
        Types of capabilities the AI can learn"""
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    AUDIO_GENERATION = "audio_generation"
    TRANSLATION = "translation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    IMAGE_ANALYSIS = "image_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SUMMARIZATION = "summarization"
    CODE_GENERATION = "code_generation"


class APICapability(BaseModel):
    """Represents a learned capability from an external API"""
    
    capability_type: CapabilityType
    name: str
    description: str
    
    # Learning progress
    training_samples: int = 0
    accuracy: float = 0.0
    confidence: float = 0.0
    
    # API information
    original_api: str
    api_cost: float = 0.0
    
    # Model information
    model_path: Optional[str] = None
    model_size_mb: float = 0.0
    inference_time_ms: float = 0.0
    
    # Status
    is_trained: bool = False
    can_replace_api: bool = False
    last_trained: Optional[datetime] = None
    
    # Performance metrics
    success_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    total_requests: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "capability_type": "text_generation",
                "name": "Text Generation",
                "description": "Generate human-like text responses",
                "original_api": "OpenAI GPT-4",
                "api_cost": 0.03,
                "training_samples": 10000,
                "accuracy": 0.92,
                "confidence": 0.88,
                "is_trained": True,
                "can_replace_api": True
            }
        }
