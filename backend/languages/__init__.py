"""Backend Languages Module - Multilingual Support Infrastructure
================================================================================
Module: backend/languages/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Language Support Module - 644 Languages Support
Responsibility: Comprehensive multilingual backend services and language processing
Technologies: Python, NLP, Translation APIs, Cultural Intelligence, RTL Support
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Language detection → Translation processing → Cultural adaptation → 
RTL/BiDi support → Locale management → Multilingual content delivery

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

from .translations import (
    TranslationEngine,
    TranslationRequest, 
    TranslationResult,
    TranslationProvider,
    TranslationQuality
)

from .detector import (
    LanguageDetector,
    DetectionResult,
    LanguageCandidate, 
    DetectionEngine,
    DetectionConfidence
)

from .cultural_adapter import (
    CulturalAdapter,
    CulturalProfile,
    AdaptationRequest,
    AdaptationResult,
    CulturalDimension,
    CommunicationStyle,
    AdaptationLevel
)

from .rtl_support import (
    RTLProcessor,
    RTLProcessingResult,
    RTLProcessingOptions,
    BiDiSpan,
    TextDirection,
    RTLLanguage,
    BiDiType
)

from .locale_manager import (
    LocaleManager,
    LocaleInfo,
    LocaleRequest,
    LocaleResult,
    LocaleCategory,
    DateFormat,
    TimeFormat,
    NumberFormat
)

from .language_models import (
    LanguageModelEngine,
    ModelRequest,
    ModelResult,
    SimilarityRequest,
    SimilarityResult,
    ModelType,
    TaskType,
    ModelLanguageSupport
)

from .translation_quality import (
    TranslationQualityEngine,
    QualityRequest,
    QualityResult,
    HumanFeedback,
    QualityImprovement,
    QualityMetric,
    QualityLevel,
    ErrorType,
    ErrorAnalysis,
    ImprovementArea
)

from .content_localizer import (
    ContentLocalizer,
    ContentLocalizationRequest,
    LocalizationResult,
    MediaElement,
    SEOOptimization,
    ContentAdaptation,
    ContentType,
    LocalizationLevel,
    MediaType,
    SEOStrategy,
    AdaptationAspect
)

# Export all public classes and functions
__all__ = [
    # Translation Engine
    "TranslationEngine",
    "TranslationRequest", 
    "TranslationResult",
    "TranslationProvider",
    "TranslationQuality",
    
    # Language Detector
    "LanguageDetector",
    "DetectionResult",
    "LanguageCandidate", 
    "DetectionEngine",
    "DetectionConfidence",
    
    # Cultural Adapter
    "CulturalAdapter",
    "CulturalProfile",
    "AdaptationRequest",
    "AdaptationResult",
    "CulturalDimension",
    "CommunicationStyle",
    "AdaptationLevel",
    
    # RTL Support
    "RTLProcessor",
    "RTLProcessingResult",
    "RTLProcessingOptions",
    "BiDiSpan",
    "TextDirection",
    "RTLLanguage",
    "BiDiType",
    
    # Locale Manager
    "LocaleManager",
    "LocaleInfo",
    "LocaleRequest",
    "LocaleResult",
    "LocaleCategory",
    "DateFormat",
    "TimeFormat",
    "NumberFormat",
    
    # Language Models Engine
    "LanguageModelEngine",
    "ModelRequest",
    "ModelResult", 
    "SimilarityRequest",
    "SimilarityResult",
    "ModelType",
    "TaskType",
    "ModelLanguageSupport",
    
    # Translation Quality Engine
    "TranslationQualityEngine",
    "QualityRequest",
    "QualityResult",
    "HumanFeedback",
    "QualityImprovement",
    "QualityMetric",
    "QualityLevel",
    "ErrorType",
    "ErrorAnalysis",
    "ImprovementArea",
    
    # Content Localizer
    "ContentLocalizer",
    "ContentLocalizationRequest",
    "LocalizationResult",
    "MediaElement",
    "SEOOptimization", 
    "ContentAdaptation",
    "ContentType",
    "LocalizationLevel",
    "MediaType",
    "SEOStrategy",
    "AdaptationAspect"
]

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced multilingual support module for 644+ languages"
__license__ = "Proprietary - Fahed Mlaiel"

# Module configuration defaults
DEFAULT_CONFIG = {
    "translation": {
        "default_provider": "openai",
        "quality_threshold": 0.85,
        "cache_enabled": True,
        "cache_size": 10000
    },
    "detection": {
        "engines": ["statistical", "neural", "pattern"],
        "confidence_threshold": 0.7,
        "cache_enabled": True
    },
    "cultural_adaptation": {
        "default_level": "moderate",
        "sensitivity_enabled": True,
        "cache_enabled": True
    },
    "rtl_support": {
        "bidi_algorithm": True,
        "mirror_characters": True,
        "generate_css": True,
        "layout_adjustments": True
    },
    "locale_management": {
        "fallback_locale": "en-US",
        "auto_detect": True,
        "cache_enabled": True
    }
}


class LanguageServiceManager:
    """
    Unified manager for all language services with integrated workflows
    """
    
    def __init__(self, config=None):
        """Initialize all language services"""
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # Initialize service components
        self.translation_engine = TranslationEngine(self.config.get("translation"))
        self.language_detector = LanguageDetector(self.config.get("detection"))
        self.cultural_adapter = CulturalAdapter(self.config.get("cultural_adaptation"))
        self.rtl_processor = RTLProcessor(self.config.get("rtl_support"))
        self.locale_manager = LocaleManager(self.config.get("locale_management"))
        
        # Initialize new Tier 1 critical modules
        self.language_model_engine = LanguageModelEngine(self.config.get("language_models"))
        self.translation_quality_engine = TranslationQualityEngine(self.config.get("translation_quality"))
        self.content_localizer = ContentLocalizer(self.config.get("content_localization"))
        
    async def process_multilingual_content(self, content: str, target_language: str, 
                                         source_language: str = None, 
                                         adaptation_level: AdaptationLevel = AdaptationLevel.MODERATE) -> dict:
        """
        Complete multilingual content processing pipeline
        
        Args:
            content: Source content to process
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            adaptation_level: Level of cultural adaptation
            
        Returns:
            Comprehensive processing result dictionary
        """
        result = {
            "original_content": content,
            "target_language": target_language,
            "processing_steps": []
        }
        
        try:
            # Step 1: Language Detection (if source not provided)
            if not source_language:
                detection_result = await self.language_detector.detect_language(content)
                source_language = detection_result.primary_language.language_code
                result["detected_language"] = source_language
                result["detection_confidence"] = detection_result.overall_confidence.value
                result["processing_steps"].append("language_detection")
            
            # Step 2: Translation
            translation_request = TranslationRequest(
                text=content,
                source_language=source_language,
                target_language=target_language
            )
            translation_result = await self.translation_engine.translate(translation_request)
            result["translated_content"] = translation_result.translated_text
            result["translation_quality"] = translation_result.quality_level.value
            result["processing_steps"].append("translation")
            
            # Step 3: Cultural Adaptation
            adaptation_request = AdaptationRequest(
                content=translation_result.translated_text,
                source_culture=source_language,
                target_culture=target_language,
                adaptation_level=adaptation_level
            )
            adaptation_result = await self.cultural_adapter.adapt_content(adaptation_request)
            result["culturally_adapted_content"] = adaptation_result.adapted_content
            result["cultural_adaptations"] = adaptation_result.adaptations_made
            result["cultural_notes"] = adaptation_result.cultural_notes
            result["processing_steps"].append("cultural_adaptation")
            
            # Step 4: RTL Processing (if target language is RTL)
            rtl_language = await self.rtl_processor.detect_rtl_language(adaptation_result.adapted_content)
            if rtl_language:
                rtl_result = await self.rtl_processor.process_text(adaptation_result.adapted_content)
                result["rtl_processed_content"] = rtl_result.processed_text
                result["text_direction"] = rtl_result.detected_direction.value
                result["css_styles"] = rtl_result.css_styles
                result["layout_adjustments"] = rtl_result.layout_adjustments
                result["processing_steps"].append("rtl_processing")
            
            # Step 5: Locale Formatting
            locale_request = LocaleRequest(
                content=result.get("rtl_processed_content", result["culturally_adapted_content"]),
                target_locale=target_language
            )
            locale_result = await self.locale_manager.format_content(locale_request)
            result["final_content"] = locale_result.formatted_content
            result["locale_used"] = locale_result.locale_used
            result["processing_steps"].append("locale_formatting")
            
            result["success"] = True
            result["total_steps"] = len(result["processing_steps"])
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            result["final_content"] = content  # Fallback to original
        
        return result
    
    async def get_language_capabilities(self) -> dict:
        """Get comprehensive information about language capabilities"""
        return {
            "supported_languages": await self.language_detector.get_supported_languages(),
            "translation_providers": [provider.value for provider in TranslationProvider],
            "cultural_profiles": len(self.cultural_adapter.cultural_profiles),
            "rtl_languages": [lang.value for lang in RTLLanguage],
            "supported_locales": await self.locale_manager.get_supported_locales(),
            "total_language_support": 644
        }


# Export the unified manager
__all__.append("LanguageServiceManager")