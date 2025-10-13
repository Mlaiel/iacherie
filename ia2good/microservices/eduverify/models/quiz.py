"""
Quiz Models for EduVerify
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    """Type of quiz question"""
    MCQ = "mcq"  # Multiple choice
    TRUE_FALSE = "true_false"
    OPEN_ENDED = "open_ended"
    FILL_IN_BLANK = "fill_in_blank"


class Difficulty(str, Enum):
    """Question difficulty level"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"


class QuizQuestion(BaseModel):
    """Individual quiz question"""
    question_id: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None  # For MCQ
    correct_answer: Any  # Can be string, int, bool, or list
    explanation: Optional[str] = None
    references: Optional[List[str]] = None  # Page numbers or URLs
    points: int = 1
    difficulty: Optional[Difficulty] = None


class QuizGenerate(BaseModel):
    """Request to generate a quiz"""
    content_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    difficulty: Difficulty = Difficulty.MEDIUM
    total_questions: int = Field(default=10, ge=5, le=50)
    question_types: Optional[List[QuestionType]] = None  # If None, mix of types
    language: str = Field(default="fr", max_length=10)
    time_limit_minutes: Optional[int] = Field(None, ge=5, le=180)
    passing_score: int = Field(default=60, ge=0, le=100)


class Quiz(BaseModel):
    """Quiz response model"""
    id: UUID
    content_id: Optional[UUID]
    user_id: UUID
    title: str
    description: Optional[str]
    subject: Optional[str]
    topic: Optional[str]
    difficulty: Difficulty
    language: str
    questions: List[QuizQuestion]
    total_questions: int
    total_points: Optional[int]
    time_limit_minutes: Optional[int]
    passing_score: int
    is_public: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizSubmit(BaseModel):
    """Submit quiz answers"""
    quiz_id: UUID
    answers: Dict[str, Any]  # question_id -> answer
    time_spent_seconds: int


class QuizResult(BaseModel):
    """Quiz result after submission"""
    id: UUID
    quiz_id: UUID
    user_id: UUID
    score: float  # Percentage 0-100
    points_earned: int
    total_points: int
    correct_answers: int
    incorrect_answers: int
    skipped_answers: int
    time_spent_seconds: int
    passed: bool
    detailed_results: List[Dict[str, Any]]  # Per-question results
    completed_at: datetime

    class Config:
        from_attributes = True


class QuizList(BaseModel):
    """List of quizzes with pagination"""
    items: List[Quiz]
    total: int
    page: int
    per_page: int
    pages: int
