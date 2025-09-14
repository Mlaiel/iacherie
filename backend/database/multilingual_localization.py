"""🌍 Multilingual Localization Database Module - Global Language Support System  
==================================================================================
Module: backend/database/multilingual_localization.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Consolidated Multilingual Localization Database - Ultra Enterprise Production-Ready
Responsibility: 644+ language support, translation management, cultural localization, and regional compliance
====================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class TranslationStatus(Enum):
    """TranslationStatus class implementation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    PUBLISHED = "published"

class LocalizationType(Enum):
    """LocalizationType class implementation"""
    CONTENT = "content"
    UI_TEXT = "ui_text"
    METADATA = "metadata"
    MARKETING = "marketing"
    LEGAL = "legal"

class MultilingualContent(Base):
    """644+ language content management."""
    __tablename__ = 'multilingual_content'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    language_code = Column(String(10), nullable=False)
    country_code = Column(String(2), nullable=True)
    dialect_code = Column(String(20), nullable=True)
    localization_type = Column(SQLEnum(LocalizationType), nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=True)
    translation_status = Column(SQLEnum(TranslationStatus), default=TranslationStatus.PENDING)
    translation_method = Column(String(50), nullable=True)  # human, ai, hybrid
    translator_id = Column(UUID(as_uuid=True), nullable=True)
    cultural_adaptation_notes = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)
    reviewed_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class TranslationManagement(Base):
    """Automated translation workflow management."""
    __tablename__ = 'translation_management'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(255), nullable=False)
    source_language_code = Column(String(10), nullable=False)
    target_languages = Column(ARRAY(String), default=[])
    translation_provider = Column(String(100), nullable=True)
    translation_model = Column(String(100), nullable=True)
    priority_level = Column(Integer, default=3)  # 1-5
    deadline = Column(DateTime(timezone=True), nullable=True)
    budget_allocated = Column(Numeric(10, 2), nullable=True)
    progress_percentage = Column(Float, default=0.0)
    quality_requirements = Column(JSONB, default={})
    style_guide_id = Column(UUID(as_uuid=True), nullable=True)
    glossary_terms = Column(JSONB, default={})
    project_status = Column(String(50), default='active')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class CulturalLocalization(Base):
    """Cultural adaptation and localization."""
    __tablename__ = 'cultural_localization'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    region_code = Column(String(10), nullable=False)
    cultural_context = Column(JSONB, default={})
    visual_adaptations = Column(JSONB, default={})
    color_preferences = Column(JSONB, default={})
    layout_adjustments = Column(JSONB, default={})
    cultural_sensitivities = Column(JSONB, default=[])
    local_customs = Column(JSONB, default={})
    religious_considerations = Column(JSONB, default={})
    marketing_adaptations = Column(JSONB, default={})
    legal_requirements = Column(JSONB, default={})
    currency_localization = Column(JSONB, default={})
    date_time_formats = Column(JSONB, default={})
    localization_specialist_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class LanguageDetection(Base):
    """Automatic language detection for content."""
    __tablename__ = 'language_detection'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    detected_language = Column(String(10), nullable=False)
    confidence_score = Column(Float, nullable=False)
    detection_method = Column(String(50), nullable=False)
    alternative_languages = Column(JSONB, default=[])
    text_sample = Column(Text, nullable=True)
    character_encoding = Column(String(50), nullable=True)
    script_type = Column(String(50), nullable=True)
    dialect_indicators = Column(JSONB, default=[])
    language_mix_detected = Column(Boolean, default=False)
    processing_time_ms = Column(Integer, nullable=True)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class RegionalCompliance(Base):
    """Regional regulatory compliance tracking."""
    __tablename__ = 'regional_compliance'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_code = Column(String(10), nullable=False, index=True)
    country_code = Column(String(2), nullable=False)
    compliance_framework = Column(String(100), nullable=False)
    regulatory_requirements = Column(JSONB, default={})
    content_restrictions = Column(JSONB, default=[])
    age_restrictions = Column(JSONB, default={})
    content_rating_system = Column(String(50), nullable=True)
    censorship_guidelines = Column(JSONB, default={})
    data_protection_laws = Column(JSONB, default={})
    intellectual_property_laws = Column(JSONB, default={})
    tax_implications = Column(JSONB, default={})
    licensing_requirements = Column(JSONB, default={})
    enforcement_agencies = Column(JSONB, default=[])
    compliance_status = Column(String(50), default='compliant')
    last_review_date = Column(DateTime(timezone=True), nullable=True)
    next_review_due = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class LinguisticAnalytics(Base):
    """Linguistic analytics and engagement tracking."""
    __tablename__ = 'linguistic_analytics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    language_code = Column(String(10), nullable=False)
    engagement_metrics = Column(JSONB, default={})
    readability_score = Column(Float, nullable=True)
    sentiment_analysis = Column(JSONB, default={})
    keyword_density = Column(JSONB, default={})
    language_complexity = Column(Float, nullable=True)
    cultural_resonance_score = Column(Float, nullable=True)
    local_idiom_usage = Column(JSONB, default={})
    translation_quality_feedback = Column(JSONB, default={})
    user_preference_data = Column(JSONB, default={})
    regional_performance = Column(JSONB, default={})
    conversion_rates_by_language = Column(JSONB, default={})
    bounce_rate_by_language = Column(JSONB, default={})
    time_spent_by_language = Column(JSONB, default={})
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

def get_multilingual_localization_models() -> None:
    return [MultilingualContent, TranslationManagement, CulturalLocalization, LanguageDetection, RegionalCompliance, LinguisticAnalytics]

def create_multilingual_localization_tables(engine) -> None:
    try:
        Base.metadata.create_all(engine, tables=[model.__table__ for model in get_multilingual_localization_models()])
        logger.info("Successfully created multilingual localization tables")
        return True
    except Exception as e:
        logger.error(f"Failed to create multilingual localization tables: {str(e)}")
        return False

__all__ = ['TranslationStatus', 'LocalizationType', 'MultilingualContent', 'TranslationManagement', 'CulturalLocalization', 'LanguageDetection', 'RegionalCompliance', 'LinguisticAnalytics', 'get_multilingual_localization_models', 'create_multilingual_localization_tables']