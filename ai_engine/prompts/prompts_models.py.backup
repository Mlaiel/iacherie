#!/usr/bin/env python3
"""Advanced AI Prompts Models Module
Data models and schemas for the prompts system

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import uuid

class PromptType(Enum):
    """Types of prompts in the system"""
    CONTENT_CREATION = "content_creation"
    PROTECTION = "protection"
    SEO_OPTIMIZATION = "seo_optimization"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    DISTRIBUTION = "distribution"

class PromptStatus(Enum):
    """Status of prompt generation"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    OPTIMIZING = "optimizing"

@dataclass
class PromptContext:
    """Context information for prompt generation"""
    user_id: str
    creator_type: str
    content_format: str
    target_platforms: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PromptTemplate:
    """Template for prompt generation"""
    id: str
    name: str
    description: str
    template: str
    variables: List[str] = field(default_factory=list)
    category: str = ""
    tags: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class GeneratedPrompt:
    """Model for a generated prompt"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt_type: PromptType = PromptType.CONTENT_CREATION
    status: PromptStatus = PromptStatus.PENDING
    
    # Content
    content: str = ""
    template_id: Optional[str] = None
    variables_used: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    context: Optional[PromptContext] = None
    
    # Quality metrics
    quality_score: float = 0.0
    readability_score: float = 0.0
    relevance_score: float = 0.0
    creativity_score: float = 0.0
    
    # Performance metrics
    generation_time_ms: int = 0
    tokens_used: int = 0
    ai_model_used: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"
    
    def update_quality_scores(self, scores: Dict[str, float]) -> None:
        """Update quality scores"""
        self.quality_score = scores.get('overall', 0.0)
        self.readability_score = scores.get('readability', 0.0)
        self.relevance_score = scores.get('relevance', 0.0)
        self.creativity_score = scores.get('creativity', 0.0)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'prompt_type': self.prompt_type.value,
            'status': self.status.value,
            'content': self.content,
            'template_id': self.template_id,
            'variables_used': self.variables_used,
            'context': self.context.__dict__ if self.context else None,
            'quality_score': self.quality_score,
            'readability_score': self.readability_score,
            'relevance_score': self.relevance_score,
            'creativity_score': self.creativity_score,
            'generation_time_ms': self.generation_time_ms,
            'tokens_used': self.tokens_used,
            'ai_model_used': self.ai_model_used,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version
        }

@dataclass
class PromptOptimization:
    """Model for prompt optimization results"""
    original_prompt_id: str
    optimized_content: str
    optimization_type: str
    improvements: List[str] = field(default_factory=list)
    quality_improvement: float = 0.0
    performance_improvement: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PromptAnalytics:
    """Analytics data for prompts"""
    prompt_id: str
    usage_count: int = 0
    success_rate: float = 0.0
    average_quality_score: float = 0.0
    user_feedback_score: float = 0.0
    platform_performance: Dict[str, float] = field(default_factory=dict)
    trending_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PromptBatch:
    """Batch processing for multiple prompts"""
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompts: List[GeneratedPrompt] = field(default_factory=list)
    status: str = "pending"
    total_prompts: int = 0
    completed_prompts: int = 0
    failed_prompts: int = 0
    average_quality_score: float = 0.0
    total_processing_time_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def add_prompt(self, prompt: GeneratedPrompt) -> None:
        """Add prompt to batch"""
        self.prompts.append(prompt)
        self.total_prompts = len(self.prompts)
    
    def update_completion_stats(self) -> None:
        """Update completion statistics"""
        self.completed_prompts = sum(1 for p in self.prompts if p.status == PromptStatus.COMPLETED)
        self.failed_prompts = sum(1 for p in self.prompts if p.status == PromptStatus.FAILED)
        
        if self.completed_prompts > 0:
            self.average_quality_score = sum(
                p.quality_score for p in self.prompts 
                if p.status == PromptStatus.COMPLETED
            ) / self.completed_prompts
            
        if self.completed_prompts + self.failed_prompts == self.total_prompts:
            self.status = "completed"
            self.completed_at = datetime.utcnow()

# Export models
__all__ = [
    "PromptType",
    "PromptStatus", 
    "PromptContext",
    "PromptTemplate",
    "GeneratedPrompt",
    "PromptOptimization",
    "PromptAnalytics",
    "PromptBatch"
]
