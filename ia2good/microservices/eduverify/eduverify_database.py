"""
Database configuration and session management + ALL ORM MODELS
Consolidated like IA2GOOD module
Supports both SQLite (dev) and PostgreSQL (prod)
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from typing import Generator
from config import settings
from datetime import datetime
import uuid
import enum

# Détecter si c'est SQLite ou PostgreSQL
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Engine configuration adaptée
if is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        echo=settings.DEBUG
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


# Helper pour UUID compatible SQLite et PostgreSQL
def uuid_column():
    """Retourne une colonne UUID compatible avec SQLite et PostgreSQL"""
    if is_sqlite:
        return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        return Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def uuid_foreign_key(foreign_key_ref, nullable=False):
    """Retourne une foreign key UUID compatible"""
    if is_sqlite:
        return Column(String(36), ForeignKey(foreign_key_ref), nullable=nullable)
    else:
        return Column(PGUUID(as_uuid=True), ForeignKey(foreign_key_ref), nullable=nullable)


def uuid_column_simple(nullable=False):
    """Colonne UUID simple (non primary key)"""
    if is_sqlite:
        return Column(String(36), nullable=nullable)
    else:
        return Column(PGUUID(as_uuid=True), nullable=nullable)


# ORM Models - PostgreSQL avec UUID natif
class ContentModel(Base):
    """Educational content table"""
    __tablename__ = "eduverify_content"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    content_text = Column(Text, nullable=True)
    content_type = Column(String(20), nullable=False)
    file_url = Column(String(500), nullable=True)
    subject = Column(String(100), nullable=True, index=True)
    topic = Column(String(255), nullable=True)
    language = Column(String(10), default="fr", index=True)
    dialect = Column(String(50), nullable=True)
    academic_level = Column(String(50), nullable=True)
    processing_mode = Column(String(50), default="standard")
    ai_analysis = Column(JSON, nullable=True)
    word_count = Column(Integer, nullable=True)
    processing_status = Column(String(20), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    quizzes = relationship("QuizModel", back_populates="content")
    progress_records = relationship("UserProgressModel", back_populates="content")


class QuizModel(Base):
    """Quiz/Assessment table"""
    __tablename__ = "eduverify_quizzes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_content.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    quiz_title = Column(String(255), nullable=False)
    quiz_description = Column(Text, nullable=True)
    quiz_type = Column(String(50), default="multiple_choice")
    difficulty_level = Column(String(20), nullable=True)
    total_questions = Column(Integer, nullable=False, default=0)
    passing_score = Column(Float, default=60.0)
    time_limit_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    content = relationship("ContentModel", back_populates="quizzes")
    questions = relationship("QuestionModel", back_populates="quiz", cascade="all, delete-orphan")
    submissions = relationship("QuizSubmissionModel", back_populates="quiz")


class QuestionModel(Base):
    """Quiz question table"""
    __tablename__ = "eduverify_questions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_quizzes.id"), nullable=False)
    question_id = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)  # Uses PostgreSQL ENUM questiontypeenum
    options = Column(JSON, nullable=True)
    correct_answer = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=True)
    references = Column(JSON, nullable=True)
    points = Column(Integer, default=1)
    difficulty = Column(String(20), nullable=True)  # Uses PostgreSQL ENUM difficultyenum
    order_index = Column(Integer, default=0)
    
    # Relationships
    quiz = relationship("QuizModel", back_populates="question_records")
    answers = relationship("AnswerModel", back_populates="question", cascade="all, delete-orphan")


class AnswerModel(Base):
    """User answer"""
    __tablename__ = "eduverify_answers"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_quiz_submissions.id"), nullable=False)
    question_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_questions.id"), nullable=False)
    user_answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    points_earned = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, nullable=True)
    
    submission = relationship("QuizSubmissionModel", back_populates="answers")
    question = relationship("QuestionModel", back_populates="answers")


class QuizSubmissionModel(Base):
    """Quiz submission"""
    __tablename__ = "eduverify_quiz_submissions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_quizzes.id"), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    score = Column(Float, nullable=False)
    points_earned = Column(Integer, nullable=False)
    total_points = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    incorrect_answers = Column(Integer, nullable=False)
    skipped_answers = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    detailed_results = Column(JSON, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    quiz = relationship("QuizModel", back_populates="submissions")
    answers = relationship("AnswerModel", back_populates="submission", cascade="all, delete-orphan")


class FactCheckModel(Base):
    """Fact-checking results"""
    __tablename__ = "eduverify_fact_checks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    content_id = Column(PGUUID(as_uuid=True), nullable=True)
    claim = Column(Text, nullable=False)
    language = Column(String(10), default="fr")
    verification_result = Column(String(50), nullable=False)
    verification_text = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)
    sources = Column(JSON, nullable=True)
    num_sources = Column(Integer, default=0)
    context = Column(Text, nullable=True)
    related_topics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserProgressModel(Base):
    """User learning progress"""
    __tablename__ = "eduverify_user_progress"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_content.id"), nullable=False)
    completion_percentage = Column(Float, default=0.0)
    quiz_score = Column(Float, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    content = relationship("ContentModel", back_populates="progress_records")


class ChatroomModel(Base):
    """Educational chatroom"""
    __tablename__ = "eduverify_chatrooms"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=True, index=True)
    topic = Column(String(255), nullable=True)
    language = Column(String(10), default="fr")
    max_participants = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    creator_id = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    messages = relationship("ChatMessageModel", back_populates="chatroom", cascade="all, delete-orphan")


class ChatMessageModel(Base):
    """Chat message"""
    __tablename__ = "eduverify_chat_messages"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(PGUUID(as_uuid=True), ForeignKey("eduverify_chatrooms.id"), nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    user_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageTypeEnum), default=MessageTypeEnum.TEXT)
    audio_url = Column(String(500), nullable=True)
    transcription = Column(Text, nullable=True)
    language = Column(String(10), default="fr")
    is_question = Column(Boolean, default=False)
    is_answer = Column(Boolean, default=False)
    reply_to_id = Column(PGUUID(as_uuid=True), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    chatroom = relationship("ChatroomModel", back_populates="messages")


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ EduVerify database tables created successfully")

