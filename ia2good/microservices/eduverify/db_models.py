"""
SQLAlchemy ORM models for EduVerify - ALL MODELS IN ONE FILE
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
import uuid
import enum

from eduverify_database import Base


# Enums
class ContentTypeEnum(str, enum.Enum):
    TEXT = "text"
    URL = "url"
    PDF = "pdf"
    VIDEO = "video"
    AUDIO = "audio"


class ProcessingStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DifficultyEnum(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"


class QuestionTypeEnum(str, enum.Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    OPEN_ENDED = "open_ended"
    FILL_IN_BLANK = "fill_in_blank"


class MessageTypeEnum(str, enum.Enum):
    TEXT = "text"
    VOICE = "voice"
    QUESTION = "question"
    ANSWER = "answer"
    SYSTEM = "system"


# Models
class ContentModel(Base):
    """Educational content table"""
    __tablename__ = "eduverify_content"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Content metadata
    title = Column(String(255), nullable=False, index=True)
    content_text = Column(Text, nullable=True)
    content_type = Column(SQLEnum(ContentTypeEnum), nullable=False)
    file_url = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)
    
    # Classification
    subject = Column(String(100), nullable=True, index=True)
    topic = Column(String(255), nullable=True)
    language = Column(String(10), default="fr", index=True)
    dialect = Column(String(50), nullable=True)
    academic_level = Column(String(50), nullable=True)
    processing_mode = Column(String(50), default="standard")
    
    # AI Analysis
    ai_analysis = Column(JSON, nullable=True)
    word_count = Column(Integer, nullable=True)
    processing_status = Column(
        SQLEnum(ProcessingStatusEnum), 
        default=ProcessingStatusEnum.PENDING,
        index=True
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    quizzes = relationship("QuizModel", back_populates="content", cascade="all, delete-orphan")
    progress_records = relationship("UserProgressModel", back_populates="content", cascade="all, delete-orphan")


class QuizModel(Base):
    """Quiz table"""
    __tablename__ = "eduverify_quizzes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_content.id"), nullable=True)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Quiz metadata
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=True, index=True)
    topic = Column(String(255), nullable=True)
    difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM)
    language = Column(String(10), default="fr")
    
    # Settings
    total_questions = Column(Integer, nullable=False)
    total_points = Column(Integer, nullable=True)
    time_limit_minutes = Column(Integer, nullable=True)
    passing_score = Column(Integer, default=60)
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    content = relationship("ContentModel", back_populates="quizzes")
    questions = relationship("QuestionModel", back_populates="quiz", cascade="all, delete-orphan")
    submissions = relationship("QuizSubmissionModel", back_populates="quiz", cascade="all, delete-orphan")


class QuestionModel(Base):
    """Quiz question table"""
    __tablename__ = "eduverify_questions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_quizzes.id"), nullable=False)
    
    # Question data
    question_id = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(SQLEnum(QuestionTypeEnum), nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=True)
    references = Column(JSON, nullable=True)
    points = Column(Integer, default=1)
    difficulty = Column(SQLEnum(DifficultyEnum), nullable=True)
    order_index = Column(Integer, default=0)
    
    # Relationships
    quiz = relationship("QuizModel", back_populates="questions")
    answers = relationship("AnswerModel", back_populates="question", cascade="all, delete-orphan")


class AnswerModel(Base):
    """User answer to a question"""
    __tablename__ = "eduverify_answers"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_quiz_submissions.id"), nullable=False)
    question_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_questions.id"), nullable=False)
    
    # Answer data
    user_answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    points_earned = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, nullable=True)
    
    # Relationships
    submission = relationship("QuizSubmissionModel", back_populates="answers")
    question = relationship("QuestionModel", back_populates="answers")


class QuizSubmissionModel(Base):
    """Quiz submission/result table"""
    __tablename__ = "eduverify_quiz_submissions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_quizzes.id"), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Results
    score = Column(Float, nullable=False)
    points_earned = Column(Integer, nullable=False)
    total_points = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    incorrect_answers = Column(Integer, nullable=False)
    skipped_answers = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    detailed_results = Column(JSON, nullable=True)
    
    # Timestamps
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    quiz = relationship("QuizModel", back_populates="submissions")
    answers = relationship("AnswerModel", back_populates="submission", cascade="all, delete-orphan")


class FactCheckModel(Base):
    """Fact-checking results table"""
    __tablename__ = "eduverify_fact_checks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    content_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    # Claim
    claim = Column(Text, nullable=False)
    language = Column(String(10), default="fr")
    
    # Verification result
    verification_result = Column(String(50), nullable=False)
    verification_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)
    sources = Column(JSON, nullable=True)
    num_sources = Column(Integer, default=0)
    
    # Context
    context = Column(Text, nullable=True)
    related_topics = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserProgressModel(Base):
    """User learning progress tracking"""
    __tablename__ = "eduverify_user_progress"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_content.id"), nullable=False)
    
    # Progress metrics
    completion_percentage = Column(Float, default=0.0)
    quiz_score = Column(Float, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Activity
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    content = relationship("ContentModel", back_populates="progress_records")


class ChatroomModel(Base):
    """Educational chatroom table"""
    __tablename__ = "eduverify_chatrooms"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Room metadata
    name = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=True, index=True)
    topic = Column(String(255), nullable=True)
    language = Column(String(10), default="fr")
    
    # Settings
    max_participants = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    creator_id = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    messages = relationship("ChatMessageModel", back_populates="chatroom", cascade="all, delete-orphan")


class ChatMessageModel(Base):
    """Chat message table"""
    __tablename__ = "eduverify_chat_messages"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_chatrooms.id"), nullable=False, index=True)
    
    # Message data
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    user_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageTypeEnum), default=MessageTypeEnum.TEXT)
    
    # Voice/accessibility
    audio_url = Column(String(500), nullable=True)
    transcription = Column(Text, nullable=True)
    
    # Metadata
    language = Column(String(10), default="fr")
    is_question = Column(Boolean, default=False)
    is_answer = Column(Boolean, default=False)
    reply_to_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    chatroom = relationship("ChatroomModel", back_populates="messages")
