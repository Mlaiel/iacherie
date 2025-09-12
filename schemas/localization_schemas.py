"""IA Influencer Agent Platform - Localization and Internationalization Schemas
Multi-language and localization support for global content distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides localization schemas for:
- Multi-language content management
- Cultural adaptation and localization
- Regional preferences and settings
- Translation workflows and management
- Internationalization configuration
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, UUIDSchema, TimestampSchema
from .primitive_types import LanguageCodeType, CountryCodeType, CurrencyAmountType


class LocalizationStatus(str, Enum):
    """Localization status levels."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    NEEDS_UPDATE = "needs_update"
    DEPRECATED = "deprecated"


class TranslationQuality(str, Enum):
    """Translation quality levels."""
    MACHINE = "machine"
    HUMAN_DRAFT = "human_draft"
    PROFESSIONAL = "professional"
    NATIVE_REVIEWED = "native_reviewed"
    CERTIFIED = "certified"


class CulturalAdaptation(str, Enum):
    """Cultural adaptation levels."""
    NONE = "none"
    BASIC = "basic"
    MODERATE = "moderate"
    FULL = "full"
    NATIVE = "native"


class ContentDirection(str, Enum):
    """Text direction for different languages."""
    LTR = "ltr"  # Left to Right
    RTL = "rtl"  # Right to Left
    TTB = "ttb"  # Top to Bottom


class NumberFormat(str, Enum):
    """Number formatting conventions."""
    DECIMAL_POINT = "decimal_point"    # 1,234.56
    DECIMAL_COMMA = "decimal_comma"    # 1.234,56
    SPACE_COMMA = "space_comma"        # 1 234,56
    APOSTROPHE_POINT = "apostrophe_point"  # 1'234.56


class DateFormat(str, Enum):
    """Date formatting conventions."""
    MDY = "mdy"        # MM/DD/YYYY
    DMY = "dmy"        # DD/MM/YYYY
    YMD = "ymd"        # YYYY/MM/DD
    ISO = "iso"        # YYYY-MM-DD


# =================== LANGUAGE AND LOCALE ===================

class Locale(BaseSchema):
    """Locale definition with language and regional settings."""
    
    language: LanguageCodeType = Field(..., description="Primary language code")
    country: Optional[CountryCodeType] = Field(None, description="Country/region code")
    script: Optional[str] = Field(None, description="Script code (e.g., Latn, Cyrl)")
    variant: Optional[str] = Field(None, description="Language variant")
    
    # Display names
    display_name: str = Field(..., description="Human-readable locale name")
    native_name: str = Field(..., description="Native language name")
    english_name: str = Field(..., description="English language name")
    
    # Text properties
    text_direction: ContentDirection = Field(ContentDirection.LTR, description="Text reading direction")
    is_pluralization_complex: bool = Field(False, description="Complex pluralization rules")
    
    # Formatting preferences
    number_format: NumberFormat = Field(NumberFormat.DECIMAL_POINT, description="Number formatting")
    date_format: DateFormat = Field(DateFormat.MDY, description="Date formatting")
    time_format: str = Field("12h", pattern="^(12h|24h)$", description="Time format preference")
    currency_symbol: Optional[str] = Field(None, description="Default currency symbol")
    currency_position: str = Field("before", pattern="^(before|after)$", description="Currency symbol position")
    
    # Regional settings
    first_day_of_week: int = Field(1, ge=1, le=7, description="First day of week (1=Monday)")
    decimal_separator: str = Field(".", description="Decimal separator character")
    thousands_separator: str = Field(",", description="Thousands separator character")
    
    @property
    def locale_code(self) -> str:
        """Generate full locale code."""
        code = self.language
        if self.country:
            code += f"_{self.country}"
        if self.script:
            code += f"_{self.script}"
        if self.variant:
            code += f"_{self.variant}"
        return code


class SupportedLocale(UUIDSchema, TimestampSchema):
    """Supported locale configuration."""
    
    locale: Locale = Field(..., description="Locale definition")
    is_active: bool = Field(True, description="Whether locale is active")
    is_default: bool = Field(False, description="Whether this is the default locale")
    priority: int = Field(0, description="Display priority")
    
    # Feature support
    translation_available: bool = Field(False, description="Translation available")
    ai_translation_enabled: bool = Field(True, description="AI translation enabled")
    human_translation_required: bool = Field(False, description="Human translation required")
    
    # Content coverage
    content_coverage: float = Field(0.0, ge=0, le=1, description="Percentage of content localized")
    ui_coverage: float = Field(0.0, ge=0, le=1, description="Percentage of UI localized")
    help_coverage: float = Field(0.0, ge=0, le=1, description="Percentage of help content localized")
    
    # Quality metrics
    translation_quality: TranslationQuality = Field(TranslationQuality.MACHINE, description="Overall translation quality")
    last_quality_review: Optional[datetime] = Field(None, description="Last quality review date")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Quality assessment score")


# =================== TRANSLATION MANAGEMENT ===================

class TranslationKey(BaseSchema):
    """Translation key definition."""
    
    key: str = Field(..., description="Unique translation key")
    namespace: str = Field("default", description="Translation namespace")
    description: Optional[str] = Field(None, description="Key description for translators")
    context: Optional[str] = Field(None, description="Usage context")
    
    # Metadata
    max_length: Optional[int] = Field(None, description="Maximum translation length")
    is_html: bool = Field(False, description="Contains HTML markup")
    variables: List[str] = Field(default=[], description="Variable placeholders")
    plural_forms: Optional[int] = Field(None, description="Number of plural forms")
    
    # Management
    is_critical: bool = Field(False, description="Critical for functionality")
    tags: List[str] = Field(default=[], description="Organizational tags")
    
    @validator('key')
    def validate_key(cls, v):
        """Validate translation key format."""
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9._-]*$', v):
            raise ValueError('Invalid translation key format')
        return v


class Translation(UUIDSchema, TimestampSchema):
    """Individual translation record."""
    
    key: str = Field(..., description="Translation key")
    locale: str = Field(..., description="Target locale code")
    value: str = Field(..., description="Translated text")
    
    # Translation metadata
    translator_id: Optional[str] = Field(None, description="Translator user ID")
    translator_name: Optional[str] = Field(None, description="Translator name")
    translation_method: str = Field("human", description="Translation method")
    quality_level: TranslationQuality = Field(..., description="Translation quality")
    
    # Review process
    status: LocalizationStatus = Field(LocalizationStatus.DRAFT, description="Translation status")
    reviewer_id: Optional[str] = Field(None, description="Reviewer user ID")
    review_notes: Optional[str] = Field(None, description="Review notes")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    
    # Version control
    version: int = Field(1, description="Translation version")
    source_version: str = Field(..., description="Source text version/hash")
    is_current: bool = Field(True, description="Whether this is the current version")
    
    # Quality metrics
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Translation confidence")
    similarity_score: Optional[float] = Field(None, ge=0, le=1, description="Similarity to source")
    readability_score: Optional[float] = Field(None, ge=0, le=1, description="Readability score")


class TranslationMemory(UUIDSchema, TimestampSchema):
    """Translation memory for reusing translations."""
    
    source_text: str = Field(..., description="Source text")
    target_text: str = Field(..., description="Target text")
    source_locale: str = Field(..., description="Source locale")
    target_locale: str = Field(..., description="Target locale")
    
    # Context information
    domain: Optional[str] = Field(None, description="Domain/subject area")
    context: Optional[str] = Field(None, description="Usage context")
    tags: List[str] = Field(default=[], description="Contextual tags")
    
    # Quality and usage
    quality_rating: Optional[float] = Field(None, ge=0, le=5, description="Quality rating")
    usage_count: int = Field(0, ge=0, description="Number of times used")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    
    # Metadata
    created_by: Optional[str] = Field(None, description="Creator user ID")
    source_project: Optional[str] = Field(None, description="Source project")
    is_verified: bool = Field(False, description="Verified by human translator")


class TranslationProject(UUIDSchema, TimestampSchema):
    """Translation project management."""
    
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    source_locale: str = Field(..., description="Source locale")
    target_locales: List[str] = Field(..., description="Target locales")
    
    # Project scope
    translation_keys: List[str] = Field(..., description="Keys to translate")
    estimated_words: int = Field(0, ge=0, description="Estimated word count")
    estimated_hours: float = Field(0, ge=0, description="Estimated translation hours")
    
    # Project management
    project_manager_id: Optional[str] = Field(None, description="Project manager user ID")
    translators: List[str] = Field(default=[], description="Assigned translator IDs")
    reviewers: List[str] = Field(default=[], description="Assigned reviewer IDs")
    
    # Timeline
    start_date: Optional[datetime] = Field(None, description="Project start date")
    due_date: Optional[datetime] = Field(None, description="Project due date")
    completion_date: Optional[datetime] = Field(None, description="Actual completion date")
    
    # Progress tracking
    progress: float = Field(0, ge=0, le=1, description="Overall progress percentage")
    status: LocalizationStatus = Field(LocalizationStatus.NOT_STARTED, description="Project status")
    
    # Quality requirements
    required_quality: TranslationQuality = Field(TranslationQuality.PROFESSIONAL, description="Required quality level")
    cultural_adaptation: CulturalAdaptation = Field(CulturalAdaptation.BASIC, description="Cultural adaptation level")
    
    # Budget and costs
    budget: Optional[CurrencyAmountType] = Field(None, description="Project budget")
    actual_cost: Optional[CurrencyAmountType] = Field(None, description="Actual cost")
    currency: Optional[str] = Field(None, description="Currency code")


# =================== CONTENT LOCALIZATION ===================

class LocalizedContent(UUIDSchema, TimestampSchema):
    """Localized version of content."""
    
    source_content_id: str = Field(..., description="Original content ID")
    locale: str = Field(..., description="Target locale")
    content_type: str = Field(..., description="Type of content")
    
    # Localized data
    title: Optional[str] = Field(None, description="Localized title")
    description: Optional[str] = Field(None, description="Localized description")
    content: Optional[str] = Field(None, description="Localized content body")
    metadata: Dict[str, Any] = Field(default={}, description="Localized metadata")
    
    # Localization process
    status: LocalizationStatus = Field(..., description="Localization status")
    translation_method: str = Field("human", description="Translation method used")
    cultural_adaptation_level: CulturalAdaptation = Field(..., description="Cultural adaptation applied")
    
    # Quality assurance
    quality_level: TranslationQuality = Field(..., description="Quality level achieved")
    reviewed_by: Optional[str] = Field(None, description="Reviewer user ID")
    review_date: Optional[datetime] = Field(None, description="Review completion date")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Quality assessment score")
    
    # Publishing
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    is_published: bool = Field(False, description="Whether content is published")
    publication_url: Optional[str] = Field(None, description="Published content URL")
    
    # Synchronization
    source_version: str = Field(..., description="Source content version")
    sync_status: str = Field("synced", description="Synchronization status")
    last_sync: Optional[datetime] = Field(None, description="Last synchronization")
    needs_update: bool = Field(False, description="Needs update from source")


class LocalizationRule(UUIDSchema, TimestampSchema):
    """Rules for content localization."""
    
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    locale: str = Field(..., description="Target locale")
    content_type: Optional[str] = Field(None, description="Applicable content type")
    
    # Rule definition
    field_mappings: Dict[str, str] = Field(..., description="Field mapping rules")
    transformation_rules: List[Dict[str, Any]] = Field(default=[], description="Content transformation rules")
    validation_rules: List[Dict[str, Any]] = Field(default=[], description="Validation rules")
    
    # Cultural adaptations
    date_format_override: Optional[DateFormat] = Field(None, description="Date format override")
    number_format_override: Optional[NumberFormat] = Field(None, description="Number format override")
    currency_display_rules: Dict[str, Any] = Field(default={}, description="Currency display rules")
    
    # Content guidelines
    tone_guidelines: Optional[str] = Field(None, description="Tone and style guidelines")
    cultural_considerations: List[str] = Field(default=[], description="Cultural considerations")
    prohibited_content: List[str] = Field(default=[], description="Prohibited content types")
    
    # Processing
    is_active: bool = Field(True, description="Whether rule is active")
    priority: int = Field(0, description="Rule priority")
    applies_to_ai: bool = Field(True, description="Applies to AI translation")


# =================== USER PREFERENCES ===================

class UserLocalePreferences(UUIDSchema, TimestampSchema):
    """User locale and language preferences."""
    
    user_id: str = Field(..., description="User identifier")
    primary_locale: str = Field(..., description="Primary locale preference")
    secondary_locales: List[str] = Field(default=[], description="Secondary locale preferences")
    
    # Interface preferences
    ui_language: str = Field(..., description="User interface language")
    content_languages: List[str] = Field(default=[], description="Preferred content languages")
    auto_translate: bool = Field(True, description="Enable automatic translation")
    translation_quality_preference: TranslationQuality = Field(TranslationQuality.PROFESSIONAL, description="Preferred translation quality")
    
    # Regional preferences
    timezone: str = Field(..., description="Timezone preference")
    date_format: DateFormat = Field(..., description="Preferred date format")
    time_format: str = Field("12h", description="Preferred time format")
    number_format: NumberFormat = Field(..., description="Preferred number format")
    currency_display: str = Field(..., description="Preferred currency display")
    
    # Content preferences
    cultural_content_preference: CulturalAdaptation = Field(CulturalAdaptation.MODERATE, description="Cultural adaptation preference")
    show_original_with_translation: bool = Field(False, description="Show original with translation")
    fallback_to_english: bool = Field(True, description="Fallback to English if translation unavailable")
    
    # Accessibility
    font_size_adjustment: float = Field(1.0, ge=0.5, le=2.0, description="Font size multiplier")
    high_contrast_mode: bool = Field(False, description="High contrast mode preference")
    screen_reader_optimized: bool = Field(False, description="Screen reader optimization")


# =================== ANALYTICS AND REPORTING ===================

class LocalizationMetrics(UUIDSchema, TimestampSchema):
    """Localization performance metrics."""
    
    locale: str = Field(..., description="Target locale")
    period_start: datetime = Field(..., description="Metrics period start")
    period_end: datetime = Field(..., description="Metrics period end")
    
    # Coverage metrics
    total_keys: int = Field(..., ge=0, description="Total translation keys")
    translated_keys: int = Field(..., ge=0, description="Translated keys")
    reviewed_keys: int = Field(..., ge=0, description="Reviewed keys")
    approved_keys: int = Field(..., ge=0, description="Approved keys")
    
    # Quality metrics
    average_quality_score: float = Field(0, ge=0, le=1, description="Average quality score")
    human_translations: int = Field(0, ge=0, description="Human translations count")
    machine_translations: int = Field(0, ge=0, description="Machine translations count")
    review_failure_rate: float = Field(0, ge=0, le=1, description="Review failure rate")
    
    # Performance metrics
    translation_speed: float = Field(0, ge=0, description="Words per hour")
    review_speed: float = Field(0, ge=0, description="Reviews per hour")
    time_to_publish: float = Field(0, ge=0, description="Average time to publish (hours)")
    
    # User engagement
    user_feedback_score: Optional[float] = Field(None, ge=0, le=5, description="User feedback score")
    content_views: int = Field(0, ge=0, description="Localized content views")
    bounce_rate: Optional[float] = Field(None, ge=0, le=1, description="Bounce rate for locale")
    
    # Cost metrics
    translation_cost: Optional[CurrencyAmountType] = Field(None, description="Translation costs")
    cost_per_word: Optional[CurrencyAmountType] = Field(None, description="Cost per word")
    roi: Optional[float] = Field(None, description="Return on investment")


class LocalizationReport(UUIDSchema, TimestampSchema):
    """Comprehensive localization report."""
    
    report_name: str = Field(..., description="Report name")
    report_type: str = Field(..., description="Report type")
    generated_by: str = Field(..., description="Report generator user ID")
    
    # Report scope
    locales: List[str] = Field(..., description="Included locales")
    content_types: List[str] = Field(default=[], description="Included content types")
    date_range_start: datetime = Field(..., description="Report date range start")
    date_range_end: datetime = Field(..., description="Report date range end")
    
    # Summary metrics
    overall_coverage: float = Field(..., ge=0, le=1, description="Overall localization coverage")
    average_quality: float = Field(..., ge=0, le=1, description="Average quality score")
    total_translations: int = Field(..., ge=0, description="Total translations")
    active_translators: int = Field(..., ge=0, description="Active translators")
    
    # Detailed data
    locale_metrics: List[LocalizationMetrics] = Field(..., description="Per-locale metrics")
    top_performing_locales: List[str] = Field(default=[], description="Top performing locales")
    improvement_opportunities: List[str] = Field(default=[], description="Improvement opportunities")
    
    # Recommendations
    recommendations: List[str] = Field(default=[], description="Actionable recommendations")
    priority_actions: List[str] = Field(default=[], description="Priority actions")
    budget_requirements: Optional[CurrencyAmountType] = Field(None, description="Estimated budget requirements")
    
    # Export options
    export_format: str = Field("json", description="Export format")
    file_url: Optional[str] = Field(None, description="Generated file URL")
    is_scheduled: bool = Field(False, description="Whether this is a scheduled report")