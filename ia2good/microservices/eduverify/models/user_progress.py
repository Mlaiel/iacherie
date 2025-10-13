"""
User Progress Models for EduVerify
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class UserProgress(BaseModel):
    """User progress on a quiz"""
    id: UUID
    user_id: UUID
    quiz_id: UUID
    score: float
    points_earned: int
    total_points: int
    time_spent_seconds: int
    answers: Dict[str, Any]
    correct_answers: int
    incorrect_answers: int
    skipped_answers: int
    completed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ProgressStats(BaseModel):
    """User's overall progress statistics"""
    user_id: UUID
    total_quizzes_taken: int
    total_quizzes_passed: int
    average_score: float
    total_time_spent_seconds: int
    subjects_studied: List[str]
    topics_mastered: List[str]
    topics_need_review: List[str]
    difficulty_breakdown: Dict[str, int]  # easy: 10, medium: 5, hard: 2
    recent_activity: List[Dict[str, Any]]


class ProgressList(BaseModel):
    """List of progress records with pagination"""
    items: List[UserProgress]
    total: int
    page: int
    per_page: int
    pages: int


class ExplanationRequest(BaseModel):
    """Request for professional explanation"""
    topic: str = Field(..., min_length=1, max_length=255)
    academic_level: str = Field(..., max_length=20)
    field: Optional[str] = Field(None, max_length=100)
    language: str = Field(default="fr", max_length=10)
    include_analogies: bool = True
    include_examples: bool = True


class Explanation(BaseModel):
    """Professional explanation response"""
    id: UUID
    topic: str
    academic_level: str
    field: Optional[str]
    explanation: str
    simplified_explanation: Optional[str]
    analogies: Optional[List[str]]
    examples: Optional[List[str]]
    references: Optional[List[Dict[str, str]]]
    language: str
    upvotes: int
    downvotes: int
    created_at: datetime

    class Config:
        from_attributes = True
