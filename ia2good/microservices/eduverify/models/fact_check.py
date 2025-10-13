"""
Fact-Check Models for EduVerify
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field


class Verdict(str, Enum):
    """Fact-check verdict"""
    TRUE = "true"
    MOSTLY_TRUE = "mostly_true"
    HALF_TRUE = "half_true"
    MOSTLY_FALSE = "mostly_false"
    FALSE = "false"
    UNVERIFIED = "unverified"


class Source(BaseModel):
    """Source for fact-checking"""
    title: str
    url: str
    credibility_score: float = Field(ge=0, le=1)
    date: Optional[datetime] = None
    excerpt: Optional[str] = None


class FactCheckRequest(BaseModel):
    """Request to check a fact"""
    claim: str = Field(..., min_length=10, max_length=5000)
    context: Optional[str] = None
    content_id: Optional[UUID] = None
    language: str = Field(default="fr", max_length=10)


class FactCheck(BaseModel):
    """Fact-check result"""
    id: UUID
    content_id: Optional[UUID]
    user_id: Optional[UUID]
    claim: str
    verdict: Verdict
    confidence: float = Field(ge=0, le=1)
    sources: List[Source]
    explanation: str
    context: Optional[str]
    ai_reasoning: Optional[str]
    human_verified: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class FactCheckList(BaseModel):
    """List of fact-checks with pagination"""
    items: List[FactCheck]
    total: int
    page: int
    per_page: int
    pages: int


class LiveFactCheckAlert(BaseModel):
    """Real-time fact-check alert during live lecture"""
    timestamp: datetime
    claim: str
    verdict: Verdict
    confidence: float
    brief_correction: Optional[str]
    urgency: str  # "high", "medium", "low"
