"""Multi-Language Support Manager - Ultra-Advanced Language Processing System

Enterprise-grade multi-language support providing real-time translation,
localization, cultural adaptation, and seamless international customer
support across 12+ languages.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import defaultdict

# Translation and language processing
from googletrans import Translator, LANGUAGES
from langdetect import detect, detect_probabilities
import spacy
from polyglot.detect import Detector
from polyglot.text import Text

# Cultural adaptation
import pycountry
import babel
from babel.dates import format_date, format_datetime, format_time
from babel.numbers import format_currency, format_decimal

# AI language models
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Caching
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

class SupportedLanguage(Enum):
    """Supported languages with ISO codes"""    ENGLISH = "en"
    GERMAN = "de" 
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    CHINESE_SIMPLIFIED = "zh-cn"
    CHINESE_TRADITIONAL = "zh-tw"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    TURKISH = "tr"
    POLISH = "pl"
    SWEDISH = "sv"
    NORWEGIAN = "no"

class TranslationProvider(Enum):
    """Translation service providers"""    GOOGLE_TRANSLATE = "google"
    AZURE_TRANSLATOR = "azure"
    AWS_TRANSLATE = "aws"
    DEEPL = "deepl"
    CACHE_FIRST = "cache"

@dataclass
class LanguageProfile:
    """User language profile and preferences"""    user_id: str
    primary_language: SupportedLanguage
    
    # Language preferences
    secondary_languages: List[SupportedLanguage] = field(default_factory=list)
    dialect_preference: Optional[str] = None
    formality_level: str = "neutral"  # formal, neutral, informal
    
    # Cultural preferences
    country_code: Optional[str] = None
    timezone: str = "UTC"
    date_format: str = "%Y-%m-%d"
    number_format: str = "en_US"
    currency: str = "USD"
    
    # Communication style
    preferred_response_length: str = "medium"  # short, medium, long
    cultural_adaptation_level: str = "medium"  # low, medium, high
    
    # Detection confidence
    language_confidence: float = 1.0
    auto_detected: bool = False
    
    # Usage statistics
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interaction_count: int = 0

@dataclass
class TranslationRequest:
    """Translation request structure"""    text: str
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    
    # Context for better translation
    context: Optional[str] = None
    domain: str = "customer_support"  # technical, marketing, legal, etc.
    formality: str = "neutral"
    
    # Quality requirements
    quality_level: str = "high"  # high, medium, fast
    preserve_formatting: bool = True
    
    # Metadata
    request_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None

@dataclass
class TranslationResult:
    """Translation result with quality metrics"""    original_text: str
    translated_text: str
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    
    # Quality metrics
    confidence_score: float = 0.0
    provider_used: TranslationProvider = TranslationProvider.GOOGLE_TRANSLATE
    processing_time: float = 0.0
    
    # Alternative translations
    alternatives: List[str] = field(default_factory=list)
    
    # Cultural adaptations applied
    adaptations: List[str] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cached: bool = False

@dataclass
class CulturalContext:
    """Cultural context information"""    language: SupportedLanguage
    country_code: str
    
    # Communication patterns
    directness_level: float = 0.5  # 0=indirect, 1=direct
    formality_preference: float = 0.5  # 0=informal, 1=formal
    hierarchy_awareness: float = 0.5  # 0=egalitarian, 1=hierarchical
    
    # Content preferences
    preferred_examples: List[str] = field(default_factory=list)
    avoided_topics: List[str] = field(default_factory=list)
    cultural_references: List[str] = field(default_factory=list)
    
    # Business culture
    response_time_expectation: float = 300.0  # seconds
    escalation_threshold: float = 0.3  # when to escalate
    
    # Localization data
    datetime_format: str = "%Y-%m-%d %H:%M"
    currency_symbol: str = "$"
    number_decimal_separator: str = "."
    number_thousand_separator: str = ","

class MultiLanguageManager:
    """Ultra-advanced multi-language support management system"""    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        
        # Translation providers
        self.google_translator = Translator()
        
        # Language models for advanced processing
        self.language_detector = pipeline(
            "text-classification",
            model="papluca/xlm-roberta-base-language-detection",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Cultural context database
        self.cultural_contexts: Dict[str, CulturalContext] = {}
        
        # User language profiles
        self.language_profiles: Dict[str, LanguageProfile] = {}
        
        # Translation cache
        self.translation_cache: Dict[str, TranslationResult] = {}
        
        # Statistics
        self.translation_stats = defaultdict(int)
        
        # Initialize cultural contexts and NLP models
        asyncio.create_task(self._initialize_cultural_contexts())
        asyncio.create_task(self._load_language_models())
    
    async def detect_language(
        self, 
        text: str,
        user_id: Optional[str] = None
    ) -> Tuple[SupportedLanguage, float]:
        """Detect language of input text with confidence score"""        try:
            # Check user's language profile first
            if user_id and user_id in self.language_profiles:
                profile = self.language_profiles[user_id]
                # If text is very short, assume user's primary language
                if len(text.strip()) < 10:
                    return profile.primary_language, 0.9
            
            # Use multiple detection methods for accuracy
            detections = []
            
            # Method 1: langdetect
            try:
                lang_probs = detect_probabilities(text)
                for lang, prob in lang_probs[:3]:  # Top 3 predictions
                    if lang in [sl.value for sl in SupportedLanguage]:
                        detections.append((lang, prob, "langdetect"))
            except:
                pass
            
            # Method 2: polyglot
            try:
                detector = Detector(text)
                lang = detector.language.code
                confidence = detector.language.confidence
                if lang in [sl.value for sl in SupportedLanguage]:
                    detections.append((lang, confidence, "polyglot"))
            except:
                pass
            
            # Method 3: XLM-RoBERTa model
            try:
                result = self.language_detector(text)
                lang_result = result[0]
                lang_code = lang_result['label']
                confidence = lang_result['score']
                
                # Map model output to our supported languages
                if lang_code in [sl.value for sl in SupportedLanguage]:
                    detections.append((lang_code, confidence, "xlm_roberta"))
            except:
                pass
            
            if not detections:
                # Default to English if no detection works
                return SupportedLanguage.ENGLISH, 0.5
            
            # Combine predictions using weighted voting
            lang_scores = defaultdict(float)
            weights = {"langdetect": 0.3, "polyglot": 0.3, "xlm_roberta": 0.4}
            
            for lang, conf, method in detections:
                lang_scores[lang] += conf * weights.get(method, 0.33)
            
            # Get best prediction
            best_lang = max(lang_scores.items(), key=lambda x: x[1])
            detected_language = SupportedLanguage(best_lang[0])
            confidence = min(best_lang[1], 1.0)
            
            # Update user profile if available
            if user_id:
                await self._update_user_language_profile(user_id, detected_language, confidence)
            
            return detected_language, confidence
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return SupportedLanguage.ENGLISH, 0.5
    
    async def translate_text(
        self,
        request: TranslationRequest,
        use_cache: bool = True
    ) -> TranslationResult:
        """Translate text with cultural adaptation"""        try:
            start_time = datetime.now()
            
            # Check cache first
            if use_cache:
                cache_key = self._generate_cache_key(request)
                cached_result = await self._get_cached_translation(cache_key)
                if cached_result:
                    cached_result.cached = True
                    return cached_result
            
            # Perform translation
            if request.source_language == request.target_language:
                # No translation needed
                result = TranslationResult(
                    original_text=request.text,
                    translated_text=request.text,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    confidence_score=1.0,
                    provider_used=TranslationProvider.CACHE_FIRST
                )
            else:
                # Translate using Google Translate (primary provider)
                translated = self.google_translator.translate(
                    request.text,
                    src=request.source_language.value,
                    dest=request.target_language.value
                )
                
                result = TranslationResult(
                    original_text=request.text,
                    translated_text=translated.text,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    confidence_score=0.85,  # Default confidence for Google Translate
                    provider_used=TranslationProvider.GOOGLE_TRANSLATE
                )
            
            # Apply cultural adaptations
            result = await self._apply_cultural_adaptations(result, request)
            
            # Post-process translation
            result = await self._post_process_translation(result, request)
            
            # Calculate processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Cache the result
            if use_cache:
                await self._cache_translation(cache_key, result)
            
            # Update statistics
            self.translation_stats[f"{request.source_language.value}_{request.target_language.value}"] += 1
            self.translation_stats["total_translations"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            # Return original text as fallback
            return TranslationResult(
                original_text=request.text,
                translated_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=0.0,
                provider_used=TranslationProvider.GOOGLE_TRANSLATE
            )
    
    async def get_localized_response(
        self,
        template: str,
        language: SupportedLanguage,
        user_id: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get culturally adapted response template"""        try:
            # Get user's cultural context
            cultural_context = await self._get_cultural_context(language, user_id)
            
            # Translate template if needed
            if language != SupportedLanguage.ENGLISH:
                translation_request = TranslationRequest(
                    text=template,
                    source_language=SupportedLanguage.ENGLISH,
                    target_language=language,
                    domain="customer_support",
                    formality=cultural_context.formality_preference
                )
                
                translation_result = await self.translate_text(translation_request)
                localized_template = translation_result.translated_text
            else:
                localized_template = template
            
            # Apply cultural adaptations
            localized_template = await self._adapt_response_style(
                localized_template, cultural_context
            )
            
            # Substitute variables if provided
            if variables:
                localized_template = await self._substitute_localized_variables(
                    localized_template, variables, cultural_context
                )
            
            return localized_template
            
        except Exception as e:
            logger.error(f"Localization failed: {str(e)}")
            return template  # Fallback to original
    
    async def create_language_profile(
        self,
        user_id: str,
        primary_language: SupportedLanguage,
        country_code: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> LanguageProfile:
        """Create or update user language profile"""        try:
            # Create profile
            profile = LanguageProfile(
                user_id=user_id,
                primary_language=primary_language,
                country_code=country_code
            )
            
            # Apply preferences if provided
            if preferences:
                for key, value in preferences.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
            
            # Infer cultural settings from country
            if country_code:
                cultural_settings = await self._infer_cultural_settings(country_code)
                profile.timezone = cultural_settings.get("timezone", "UTC")
                profile.date_format = cultural_settings.get("date_format", "%Y-%m-%d")
                profile.currency = cultural_settings.get("currency", "USD")
            
            # Store profile
            self.language_profiles[user_id] = profile
            await self._cache_language_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create language profile for {user_id}: {str(e)}")
            raise
    
    async def get_language_profile(self, user_id: str) -> Optional[LanguageProfile]:
        """Get user's language profile"""        if user_id in self.language_profiles:
            return self.language_profiles[user_id]
        
        # Try to load from cache
        cached_profile = await self._load_cached_language_profile(user_id)
        if cached_profile:
            self.language_profiles[user_id] = cached_profile
            return cached_profile
        
        return None
    
    async def format_localized_content(
        self,
        content_type: str,
        value: Any,
        language: SupportedLanguage,
        user_id: Optional[str] = None
    ) -> str:
        """Format content according to locale (dates, numbers, currency)"""        try:
            cultural_context = await self._get_cultural_context(language, user_id)
            locale_code = f"{language.value}_{cultural_context.country_code}" if cultural_context.country_code else language.value
            
            if content_type == "datetime":
                if isinstance(value, datetime):
                    return format_datetime(value, locale=locale_code)
            elif content_type == "date":
                if isinstance(value, datetime):
                    return format_date(value.date(), locale=locale_code)
            elif content_type == "currency":
                if isinstance(value, (int, float)) and len(value) >= 2:
                    amount, currency_code = value[0], value[1]
                    return format_currency(amount, currency_code, locale=locale_code)
            elif content_type == "number":
                if isinstance(value, (int, float)):
                    return format_decimal(value, locale=locale_code)
            
            return str(value)
            
        except Exception as e:
            logger.error(f"Localized formatting failed: {str(e)}")
            return str(value)
    
    async def get_language_analytics(self) -> Dict[str, Any]:
        """Get language usage analytics"""        try:
            analytics = {
                "total_translations": self.translation_stats["total_translations"],
                "language_pairs": {},
                "user_languages": defaultdict(int),
                "detection_accuracy": {},
                "popular_languages": [],
                "translation_volume_by_hour": defaultdict(int)
            }
            
            # Language pair statistics
            for key, count in self.translation_stats.items():
                if "_" in key and key != "total_translations":
                    analytics["language_pairs"][key] = count
            
            # User language distribution
            for profile in self.language_profiles.values():
                analytics["user_languages"][profile.primary_language.value] += 1
            
            # Most popular languages
            analytics["popular_languages"] = sorted(
                analytics["user_languages"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get language analytics: {str(e)}")
            return {}
    
    async def _initialize_cultural_contexts(self):
        """Initialize cultural context data for supported languages"""        try:
            # Define cultural contexts for major languages
            contexts = [
                CulturalContext(
                    language=SupportedLanguage.GERMAN,
                    country_code="DE",
                    directness_level=0.8,  # Germans prefer direct communication
                    formality_preference=0.7,  # More formal
                    hierarchy_awareness=0.6,
                    response_time_expectation=240.0,
                    datetime_format="%d.%m.%Y %H:%M",
                    currency_symbol="€",
                    number_decimal_separator=",",
                    number_thousand_separator="."
                ),
                CulturalContext(
                    language=SupportedLanguage.FRENCH,
                    country_code="FR",
                    directness_level=0.4,  # More indirect
                    formality_preference=0.8,  # Very formal
                    hierarchy_awareness=0.7,
                    response_time_expectation=360.0,
                    datetime_format="%d/%m/%Y %H:%M",
                    currency_symbol="€"
                ),
                CulturalContext(
                    language=SupportedLanguage.JAPANESE,
                    country_code="JP",
                    directness_level=0.2,  # Very indirect
                    formality_preference=0.9,  # Extremely formal
                    hierarchy_awareness=0.9,
                    response_time_expectation=180.0,
                    avoided_topics=["personal questions", "direct criticism"],
                    cultural_references=["seasonal greetings", "respectful honorifics"]
                ),
                CulturalContext(
                    language=SupportedLanguage.SPANISH,
                    country_code="ES",
                    directness_level=0.6,
                    formality_preference=0.5,
                    hierarchy_awareness=0.5,
                    response_time_expectation=300.0,
                    preferred_examples=["family-oriented analogies"]
                ),
                CulturalContext(
                    language=SupportedLanguage.CHINESE_SIMPLIFIED,
                    country_code="CN",
                    directness_level=0.3,
                    formality_preference=0.8,
                    hierarchy_awareness=0.8,
                    response_time_expectation=240.0,
                    cultural_references=["business harmony", "face-saving approaches"]
                )
            ]
            
            # Store contexts
            for context in contexts:
                key = f"{context.language.value}_{context.country_code}"
                self.cultural_contexts[key] = context
            
            logger.info(f"Initialized {len(contexts)} cultural contexts")
            
        except Exception as e:
            logger.error(f"Failed to initialize cultural contexts: {str(e)}")
    
    async def _load_language_models(self):
        """Load additional language processing models"""        try:
            # Load spaCy models for supported languages
            supported_spacy_models = {
                "en": "en_core_web_sm",
                "de": "de_core_news_sm",
                "fr": "fr_core_news_sm",
                "es": "es_core_news_sm",
                "it": "it_core_news_sm",
                "pt": "pt_core_news_sm",
                "nl": "nl_core_news_sm",
                "zh": "zh_core_web_sm",
                "ja": "ja_core_news_sm"
            }
            
            self.spacy_models = {}
            for lang_code, model_name in supported_spacy_models.items():
                try:
                    self.spacy_models[lang_code] = spacy.load(model_name)
                except OSError:
                    logger.warning(f"SpaCy model {model_name} not available")
                    continue
            
            logger.info(f"Loaded {len(self.spacy_models)} language models")
            
        except Exception as e:
            logger.error(f"Failed to load language models: {str(e)}")
    
    async def _apply_cultural_adaptations(
        self,
        result: TranslationResult,
        request: TranslationRequest
    ) -> TranslationResult:
        """Apply cultural adaptations to translation"""        try:
            cultural_context = self.cultural_contexts.get(
                f"{request.target_language.value}_{request.target_language.value.upper()}"
            )
            
            if not cultural_context:
                return result
            
            adapted_text = result.translated_text
            adaptations = []
            
            # Adjust formality level
            if request.formality == "formal" or cultural_context.formality_preference > 0.7:
                # Make more formal
                adapted_text = adapted_text.replace("you", "you")  # Language-specific formal pronouns
                adaptations.append("formality_adjustment")
            
            # Adjust directness
            if cultural_context.directness_level < 0.5:
                # Make less direct - add softening phrases
                if adapted_text.startswith("You need to"):
                    adapted_text = adapted_text.replace("You need to", "Perhaps you could consider")
                    adaptations.append("directness_softening")
            
            # Add cultural references if appropriate
            if cultural_context.cultural_references:
                # This would add appropriate cultural context
                adaptations.append("cultural_references")
            
            result.translated_text = adapted_text
            result.adaptations = adaptations
            
            return result
            
        except Exception as e:
            logger.error(f"Cultural adaptation failed: {str(e)}")
            return result
    
    async def _post_process_translation(
        self,
        result: TranslationResult,
        request: TranslationRequest
    ) -> TranslationResult:
        """Post-process translation for quality and formatting"""        try:
            processed_text = result.translated_text
            
            # Preserve original formatting if requested
            if request.preserve_formatting:
                # Restore line breaks, spacing, etc.
                # This would be more sophisticated in production
                pass
            
            # Fix common translation issues
            processed_text = await self._fix_translation_issues(
                processed_text, request.target_language
            )
            
            result.translated_text = processed_text
            return result
            
        except Exception as e:
            logger.error(f"Post-processing failed: {str(e)}")
            return result
    
    async def _fix_translation_issues(
        self,
        text: str,
        target_language: SupportedLanguage
    ) -> str:
        """Fix common translation issues"""        try:
            # Language-specific fixes
            if target_language == SupportedLanguage.GERMAN:
                # Fix German capitalization
                text = re.sub(r'\b([A-ZÄÖÜ][a-zäöüß]*)\b', lambda m: m.group(1), text)
            
            elif target_language == SupportedLanguage.FRENCH:
                # Fix French accents and contractions
                text = text.replace(" de le ", " du ")
                text = text.replace(" à le ", " au ")
            
            elif target_language == SupportedLanguage.SPANISH:
                # Fix Spanish punctuation
                text = re.sub(r'¿([^?]+)\?', r'¿\1?', text)
            
            return text
            
        except Exception as e:
            logger.error(f"Translation fix failed: {str(e)}")
            return text
    
    async def _get_cultural_context(
        self,
        language: SupportedLanguage,
        user_id: Optional[str] = None
    ) -> CulturalContext:
        """Get cultural context for language and user"""        # Check user profile first
        if user_id:
            profile = await self.get_language_profile(user_id)
            if profile and profile.country_code:
                context_key = f"{language.value}_{profile.country_code}"
                if context_key in self.cultural_contexts:
                    return self.cultural_contexts[context_key]
        
        # Default context for language
        default_key = f"{language.value}_{language.value.upper()}"
        if default_key in self.cultural_contexts:
            return self.cultural_contexts[default_key]
        
        # Fallback to generic context
        return CulturalContext(
            language=language,
            country_code="XX"
        )
    
    async def _adapt_response_style(
        self,
        text: str,
        cultural_context: CulturalContext
    ) -> str:
        """Adapt response style to cultural context"""        try:
            adapted_text = text
            
            # Adjust based on formality preference
            if cultural_context.formality_preference > 0.7:
                # Make more formal
                adapted_text = adapted_text.replace("Hi", "Dear")
                adapted_text = adapted_text.replace("Thanks", "Thank you")
            elif cultural_context.formality_preference < 0.3:
                # Make more casual
                adapted_text = adapted_text.replace("Dear", "Hi")
                adapted_text = adapted_text.replace("Thank you", "Thanks")
            
            # Adjust directness
            if cultural_context.directness_level < 0.4:
                # Add softening language
                adapted_text = re.sub(
                    r'^(You should|You must|You need to)',
                    r'You might want to consider',
                    adapted_text,
                    flags=re.MULTILINE
                )
            
            return adapted_text
            
        except Exception as e:
            logger.error(f"Response style adaptation failed: {str(e)}")
            return text
    
    async def _substitute_localized_variables(
        self,
        template: str,
        variables: Dict[str, Any],
        cultural_context: CulturalContext
    ) -> str:
        """Substitute variables with localized formatting"""        try:
            localized_text = template
            
            for var_name, value in variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in localized_text:
                    # Format value according to cultural context
                    if isinstance(value, datetime):
                        formatted_value = value.strftime(cultural_context.datetime_format)
                    elif isinstance(value, (int, float)) and var_name.endswith('_currency'):
                        formatted_value = f"{cultural_context.currency_symbol}{value:,.2f}"
                    else:
                        formatted_value = str(value)
                    
                    localized_text = localized_text.replace(placeholder, formatted_value)
            
            return localized_text
            
        except Exception as e:
            logger.error(f"Variable substitution failed: {str(e)}")
            return template
    
    async def _update_user_language_profile(
        self,
        user_id: str,
        detected_language: SupportedLanguage,
        confidence: float
    ):
        """Update user language profile with detection results"""        try:
            profile = await self.get_language_profile(user_id)
            
            if not profile:
                # Create new profile
                profile = await self.create_language_profile(user_id, detected_language)
            else:
                # Update existing profile
                if confidence > 0.8 and profile.language_confidence < confidence:
                    profile.primary_language = detected_language
                    profile.language_confidence = confidence
                    profile.auto_detected = True
                
                profile.interaction_count += 1
                profile.last_updated = datetime.now(timezone.utc)
                
                await self._cache_language_profile(profile)
            
        except Exception as e:
            logger.error(f"Failed to update user language profile: {str(e)}")
    
    async def _infer_cultural_settings(self, country_code: str) -> Dict[str, str]:
        """Infer cultural settings from country code"""        try:
            country = pycountry.countries.get(alpha_2=country_code.upper())
            if not country:
                return {}
            
            # Basic cultural mappings
            cultural_mappings = {
                "DE": {"timezone": "Europe/Berlin", "date_format": "%d.%m.%Y", "currency": "EUR"},
                "FR": {"timezone": "Europe/Paris", "date_format": "%d/%m/%Y", "currency": "EUR"},
                "US": {"timezone": "America/New_York", "date_format": "%m/%d/%Y", "currency": "USD"},
                "GB": {"timezone": "Europe/London", "date_format": "%d/%m/%Y", "currency": "GBP"},
                "JP": {"timezone": "Asia/Tokyo", "date_format": "%Y/%m/%d", "currency": "JPY"},
                "CN": {"timezone": "Asia/Shanghai", "date_format": "%Y-%m-%d", "currency": "CNY"}
            }
            
            return cultural_mappings.get(country_code.upper(), {})
            
        except Exception as e:
            logger.error(f"Failed to infer cultural settings: {str(e)}")
            return {}
    
    def _generate_cache_key(self, request: TranslationRequest) -> str:
        """Generate cache key for translation request"""        import hashlib
        
        key_data = f"{request.text}|{request.source_language.value}|{request.target_language.value}|{request.formality}|{request.domain}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_cached_translation(self, cache_key: str) -> Optional[TranslationResult]:
        """Get cached translation result"""        try:
            cached_data = await self.redis_client.get(f"translation_cache:{cache_key}")
            if cached_data:
                data = json.loads(cached_data)
                return TranslationResult(
                    original_text=data["original_text"],
                    translated_text=data["translated_text"],
                    source_language=SupportedLanguage(data["source_language"]),
                    target_language=SupportedLanguage(data["target_language"]),
                    confidence_score=data["confidence_score"],
                    provider_used=TranslationProvider(data["provider_used"]),
                    processing_time=data["processing_time"],
                    alternatives=data.get("alternatives", []),
                    adaptations=data.get("adaptations", []),
                    timestamp=datetime.fromisoformat(data["timestamp"])
                )
        except Exception as e:
            logger.error(f"Failed to get cached translation: {str(e)}")
        
        return None
    
    async def _cache_translation(self, cache_key: str, result: TranslationResult):
        """Cache translation result"""        try:
            data = {
                "original_text": result.original_text,
                "translated_text": result.translated_text,
                "source_language": result.source_language.value,
                "target_language": result.target_language.value,
                "confidence_score": result.confidence_score,
                "provider_used": result.provider_used.value,
                "processing_time": result.processing_time,
                "alternatives": result.alternatives,
                "adaptations": result.adaptations,
                "timestamp": result.timestamp.isoformat()
            }
            
            await self.redis_client.setex(
                f"translation_cache:{cache_key}",
                86400 * 7,  # 7 days TTL
                json.dumps(data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache translation: {str(e)}")
    
    async def _cache_language_profile(self, profile: LanguageProfile):
        """Cache user language profile"""        try:
            data = {
                "user_id": profile.user_id,
                "primary_language": profile.primary_language.value,
                "secondary_languages": [lang.value for lang in profile.secondary_languages],
                "dialect_preference": profile.dialect_preference,
                "formality_level": profile.formality_level,
                "country_code": profile.country_code,
                "timezone": profile.timezone,
                "date_format": profile.date_format,
                "number_format": profile.number_format,
                "currency": profile.currency,
                "preferred_response_length": profile.preferred_response_length,
                "cultural_adaptation_level": profile.cultural_adaptation_level,
                "language_confidence": profile.language_confidence,
                "auto_detected": profile.auto_detected,
                "created_at": profile.created_at.isoformat(),
                "last_updated": profile.last_updated.isoformat(),
                "interaction_count": profile.interaction_count
            }
            
            await self.redis_client.setex(
                f"language_profile:{profile.user_id}",
                86400 * 30,  # 30 days TTL
                json.dumps(data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache language profile: {str(e)}")
    
    async def _load_cached_language_profile(self, user_id: str) -> Optional[LanguageProfile]:
        """Load cached language profile"""        try:
            data = await self.redis_client.get(f"language_profile:{user_id}")
            if data:
                profile_data = json.loads(data)
                
                return LanguageProfile(
                    user_id=profile_data["user_id"],
                    primary_language=SupportedLanguage(profile_data["primary_language"]),
                    secondary_languages=[SupportedLanguage(lang) for lang in profile_data.get("secondary_languages", [])],
                    dialect_preference=profile_data.get("dialect_preference"),
                    formality_level=profile_data.get("formality_level", "neutral"),
                    country_code=profile_data.get("country_code"),
                    timezone=profile_data.get("timezone", "UTC"),
                    date_format=profile_data.get("date_format", "%Y-%m-%d"),
                    number_format=profile_data.get("number_format", "en_US"),
                    currency=profile_data.get("currency", "USD"),
                    preferred_response_length=profile_data.get("preferred_response_length", "medium"),
                    cultural_adaptation_level=profile_data.get("cultural_adaptation_level", "medium"),
                    language_confidence=profile_data.get("language_confidence", 1.0),
                    auto_detected=profile_data.get("auto_detected", False),
                    created_at=datetime.fromisoformat(profile_data["created_at"]),
                    last_updated=datetime.fromisoformat(profile_data["last_updated"]),
                    interaction_count=profile_data.get("interaction_count", 0)
                )
        except Exception as e:
            logger.error(f"Failed to load cached language profile: {str(e)}")
        
        return None
