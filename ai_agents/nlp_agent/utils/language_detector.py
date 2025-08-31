"""Language Detector - Multi-Language Detection System
==================================================

Advanced language detection system supporting 100+ languages with
high accuracy using transformer models and fallback methods.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Language detection will use fallback methods.")

try:
    import langdetect
    from langdetect import detect, detect_langs, DetectorFactory
    LANGDETECT_AVAILABLE = True
    # Set seed for reproducible results
    DetectorFactory.seed = 0
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import spacy
    from spacy.lang.en import English
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class LanguageScore:
    """Individual language detection score"""    language: str
    language_name: str
    confidence: float
    iso_code: str
    script: Optional[str] = None

@dataclass
class LanguageResult:
    """Complete language detection result"""    text: str
    primary_language: str
    primary_language_name: str
    confidence: float
    language_scores: List[LanguageScore] = field(default_factory=list)
    is_multilingual: bool = False
    detected_languages: List[str] = field(default_factory=list)
    script_type: Optional[str] = None
    text_direction: str = "ltr"  # ltr, rtl
    character_encoding: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class LanguageDetector:
    """    Advanced language detection system supporting 100+ languages with
    high accuracy using transformer models and fallback methods.
    """    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Language Detector"""        self.config = config or default_config
        self.models = {}
        self.pipelines = {}
        
        # Language mappings
        self.iso_to_name = self._load_language_mappings()
        self.script_patterns = self._load_script_patterns()
        
        self._initialize_models()
    
    def _load_language_mappings(self) -> Dict[str, str]:
        """Load ISO language code to name mappings"""        return {
            'af': 'Afrikaans', 'ar': 'Arabic', 'bg': 'Bulgarian', 'bn': 'Bengali',
            'ca': 'Catalan', 'cs': 'Czech', 'cy': 'Welsh', 'da': 'Danish',
            'de': 'German', 'el': 'Greek', 'en': 'English', 'es': 'Spanish',
            'et': 'Estonian', 'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French',
            'gu': 'Gujarati', 'he': 'Hebrew', 'hi': 'Hindi', 'hr': 'Croatian',
            'hu': 'Hungarian', 'id': 'Indonesian', 'it': 'Italian', 'ja': 'Japanese',
            'kn': 'Kannada', 'ko': 'Korean', 'lt': 'Lithuanian', 'lv': 'Latvian',
            'mk': 'Macedonian', 'ml': 'Malayalam', 'mr': 'Marathi', 'ne': 'Nepali',
            'nl': 'Dutch', 'no': 'Norwegian', 'pa': 'Punjabi', 'pl': 'Polish',
            'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian', 'sk': 'Slovak',
            'sl': 'Slovenian', 'so': 'Somali', 'sq': 'Albanian', 'sv': 'Swedish',
            'sw': 'Swahili', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai',
            'tl': 'Filipino', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu',
            'vi': 'Vietnamese', 'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)',
            'zh': 'Chinese'
        }
    
    def _load_script_patterns(self) -> Dict[str, re.Pattern]:
        """Load regex patterns for script detection"""        return {
            'latin': re.compile(r'[a-zA-Z]'),
            'cyrillic': re.compile(r'[а-яё]', re.IGNORECASE),
            'arabic': re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'),
            'chinese': re.compile(r'[\u4e00-\u9fff]'),
            'japanese_hiragana': re.compile(r'[\u3040-\u309f]'),
            'japanese_katakana': re.compile(r'[\u30a0-\u30ff]'),
            'korean': re.compile(r'[\uac00-\ud7af]'),
            'hindi': re.compile(r'[\u0900-\u097F]'),
            'thai': re.compile(r'[\u0e00-\u0e7f]'),
            'hebrew': re.compile(r'[\u0590-\u05FF]'),
            'greek': re.compile(r'[\u0370-\u03FF]')
        }
    
    def _initialize_models(self):
        """Initialize language detection models"""        try:
            # Primary transformer model
            if TRANSFORMERS_AVAILABLE:
                model_name = self.config.language_detection.model_name
                logger.info(f"Loading language detection model: {model_name}")
                
                self.pipelines["primary"] = pipeline(
                    "text-classification",
                    model=model_name,
                    device=self._get_device(),
                    return_all_scores=True
                )
                
                logger.info("Transformer language detection model loaded")
            
            # Fallback models
            self._setup_fallback_models()
            
        except Exception as e:
            logger.error(f"Failed to initialize language detection models: {e}")
            self._setup_fallback_models()
    
    def _setup_fallback_models(self):
        """Setup fallback language detection methods"""        self.fallback_methods = []
        
        if LANGDETECT_AVAILABLE:
            self.fallback_methods.append("langdetect")
            logger.info("Langdetect fallback available")
        
        if SPACY_AVAILABLE:
            self.fallback_methods.append("spacy")
            logger.info("spaCy fallback available")
        
        # Always available rule-based detection
        self.fallback_methods.append("rule_based")
        logger.info("Rule-based fallback available")
    
    def _get_device(self) -> int:
        """Get optimal device for model execution"""        if self.config.performance.enable_gpu and TRANSFORMERS_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    return 0  # Use first GPU
            except:
                pass
        return -1  # Use CPU
    
    async def detect_language(
        self,
        text: Union[str, List[str]],
        max_languages: Optional[int] = None
    ) -> Union[LanguageResult, List[LanguageResult]]:
        """        Detect language(s) in text
        
        Args:
            text: Text or list of texts to analyze
            max_languages: Maximum number of languages to detect
        
        Returns:
            LanguageResult or list of results
        """        start_time = asyncio.get_event_loop().time()
        
        # Handle batch processing
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        
        max_languages = max_languages or self.config.language_detection.max_languages
        
        results = []
        
        try:
            for single_text in texts:
                result = await self._detect_single_text(single_text, max_languages)
                results.append(result)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            for result in results:
                result.processing_time = processing_time / len(results)
            
            return results if is_batch else results[0]
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            raise
    
    async def _detect_single_text(
        self,
        text: str,
        max_languages: int
    ) -> LanguageResult:
        """Detect language for a single text"""        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        result = LanguageResult(
            text=text,
            primary_language="unknown",
            primary_language_name="Unknown",
            confidence=0.0
        )
        
        try:
            # Preprocess text
            clean_text = self._preprocess_text(text)
            
            if len(clean_text.strip()) < 5:
                result.primary_language = "unknown"
                result.primary_language_name = "Unknown (text too short)"
                result.confidence = 0.0
                return result
            
            # Try transformer model first
            if "primary" in self.pipelines:
                detected = await self._detect_with_transformer(clean_text, max_languages)
                if detected:
                    self._populate_result_from_detection(result, detected, max_languages)
                    if result.confidence >= self.config.language_detection.confidence_threshold:
                        # Add script and direction analysis
                        self._analyze_text_properties(text, result)
                        return result
            
            # Try fallback methods
            for method in self.fallback_methods:
                try:
                    detected = await self._detect_with_fallback(clean_text, method, max_languages)
                    if detected:
                        self._populate_result_from_detection(result, detected, max_languages)
                        if result.confidence >= self.config.language_detection.confidence_threshold:
                            break
                except Exception as e:
                    logger.warning(f"Fallback method {method} failed: {e}")
                    continue
            
            # Analyze text properties
            self._analyze_text_properties(text, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Single text language detection failed: {e}")
            result.metadata["error"] = str(e)
            return result
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for language detection"""        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove mentions and hashtags for better detection
        text = re.sub(r'[@#]\w+', '', text)
        
        return text.strip()
    
    async def _detect_with_transformer(
        self,
        text: str,
        max_languages: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Detect language using transformer model"""        try:
            pipeline_obj = self.pipelines["primary"]
            
            predictions = await asyncio.get_event_loop().run_in_executor(
                None,
                pipeline_obj,
                text
            )
            
            if predictions and isinstance(predictions, list):
                # Sort by confidence and take top languages
                sorted_predictions = sorted(predictions, key=lambda x: x["score"], reverse=True)
                top_predictions = sorted_predictions[:max_languages]
                
                # Convert to standard format
                results = []
                for pred in top_predictions:
                    lang_code = pred["label"]
                    confidence = pred["score"]
                    
                    # Map to standard format
                    results.append({
                        "language": lang_code,
                        "confidence": confidence
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Transformer language detection failed: {e}")
            return None
    
    async def _detect_with_fallback(
        self,
        text: str,
        method: str,
        max_languages: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Detect language using fallback methods"""        if method == "langdetect" and LANGDETECT_AVAILABLE:
            try:
                detected_langs = detect_langs(text)
                results = []
                
                for lang_obj in detected_langs[:max_languages]:
                    results.append({
                        "language": lang_obj.lang,
                        "confidence": lang_obj.prob
                    })
                
                return results
                
            except Exception as e:
                logger.warning(f"Langdetect failed: {e}")
                return None
        
        elif method == "rule_based":
            return await self._detect_with_rules(text, max_languages)
        
        return None
    
    async def _detect_with_rules(
        self,
        text: str,
        max_languages: int
    ) -> List[Dict[str, Any]]:
        """Rule-based language detection using script patterns"""        script_scores = {}
        total_chars = len(text)
        
        if total_chars == 0:
            return [{"language": "unknown", "confidence": 0.0}]
        
        # Count characters by script
        for script_name, pattern in self.script_patterns.items():
            matches = len(pattern.findall(text))
            if matches > 0:
                script_scores[script_name] = matches / total_chars
        
        # Map scripts to languages
        script_to_lang = {
            'latin': 'en',  # Default to English for Latin script
            'cyrillic': 'ru',
            'arabic': 'ar',
            'chinese': 'zh',
            'japanese_hiragana': 'ja',
            'japanese_katakana': 'ja',
            'korean': 'ko',
            'hindi': 'hi',
            'thai': 'th',
            'hebrew': 'he',
            'greek': 'el'
        }
        
        results = []
        for script, score in sorted(script_scores.items(), key=lambda x: x[1], reverse=True):
            if script in script_to_lang and len(results) < max_languages:
                lang_code = script_to_lang[script]
                results.append({
                    "language": lang_code,
                    "confidence": min(score * 2, 1.0)  # Boost confidence but cap at 1.0
                })
        
        # Default to English if no script detected
        if not results:
            results = [{"language": "en", "confidence": 0.3}]
        
        return results
    
    def _populate_result_from_detection(
        self,
        result: LanguageResult,
        detected: List[Dict[str, Any]],
        max_languages: int
    ):
        """Populate result object from detection data"""        if not detected:
            return
        
        # Primary language
        primary = detected[0]
        result.primary_language = primary["language"]
        result.primary_language_name = self.iso_to_name.get(
            primary["language"], 
            primary["language"].upper()
        )
        result.confidence = primary["confidence"]
        
        # All detected languages
        result.language_scores = []
        result.detected_languages = []
        
        for detection in detected[:max_languages]:
            lang_code = detection["language"]
            confidence = detection["confidence"]
            
            result.language_scores.append(LanguageScore(
                language=lang_code,
                language_name=self.iso_to_name.get(lang_code, lang_code.upper()),
                confidence=confidence,
                iso_code=lang_code
            ))
            
            result.detected_languages.append(lang_code)
        
        # Multilingual detection
        significant_languages = [
            lang for lang in result.language_scores
            if lang.confidence > 0.1
        ]
        result.is_multilingual = len(significant_languages) > 1
    
    def _analyze_text_properties(self, text: str, result: LanguageResult):
        """Analyze additional text properties"""        # Script type detection
        result.script_type = self._detect_primary_script(text)
        
        # Text direction (RTL languages)
        rtl_languages = {'ar', 'he', 'fa', 'ur'}
        if result.primary_language in rtl_languages:
            result.text_direction = "rtl"
        else:
            result.text_direction = "ltr"
        
        # Character encoding analysis
        result.character_encoding = self._analyze_encoding(text)
        
        # Additional metadata
        result.metadata.update({
            "text_length": len(text),
            "unique_characters": len(set(text)),
            "script_diversity": len([
                script for script, pattern in self.script_patterns.items()
                if pattern.search(text)
            ]),
            "detection_method": "transformer" if "primary" in self.pipelines else "fallback"
        })
    
    def _detect_primary_script(self, text: str) -> Optional[str]:
        """Detect the primary script used in text"""        script_counts = {}
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                for script_name, pattern in self.script_patterns.items():
                    if pattern.match(char):
                        script_counts[script_name] = script_counts.get(script_name, 0) + 1
                        break
        
        if total_chars == 0:
            return None
        
        # Find dominant script
        max_script = max(script_counts.items(), key=lambda x: x[1]) if script_counts else None
        return max_script[0] if max_script and max_script[1] / total_chars > 0.3 else None
    
    def _analyze_encoding(self, text: str) -> str:
        """Analyze character encoding of text"""        try:
            # Check for common encodings
            if all(ord(char) < 128 for char in text):
                return "ascii"
            elif all(ord(char) < 256 for char in text):
                return "latin-1"
            else:
                return "utf-8"
        except:
            return "unknown"
    
    async def detect_language_confidence(
        self,
        text: str,
        target_language: str
    ) -> float:
        """Get confidence that text is in a specific language"""        result = await self.detect_language(text)
        
        # Find confidence for target language
        for lang_score in result.language_scores:
            if lang_score.language == target_language:
                return lang_score.confidence
        
        return 0.0
    
    async def is_multilingual(self, text: str, threshold: float = 0.15) -> bool:
        """Check if text contains multiple languages"""        result = await self.detect_language(text)
        
        significant_languages = [
            lang for lang in result.language_scores
            if lang.confidence > threshold
        ]
        
        return len(significant_languages) > 1
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""        return [
            {"code": code, "name": name}
            for code, name in self.iso_to_name.items()
        ]
    
    def get_language_info(self, language_code: str) -> Dict[str, Any]:
        """Get detailed information about a language"""        if language_code not in self.iso_to_name:
            return {"error": "Language not supported"}
        
        rtl_languages = {'ar', 'he', 'fa', 'ur'}
        
        return {
            "code": language_code,
            "name": self.iso_to_name[language_code],
            "direction": "rtl" if language_code in rtl_languages else "ltr",
            "script": self._get_primary_script_for_language(language_code),
            "supported": True
        }
    
    def _get_primary_script_for_language(self, language_code: str) -> str:
        """Get primary script for a language"""        script_mapping = {
            'ar': 'arabic', 'he': 'hebrew', 'fa': 'arabic', 'ur': 'arabic',
            'zh': 'chinese', 'ja': 'japanese', 'ko': 'korean',
            'hi': 'hindi', 'th': 'thai', 'el': 'greek',
            'ru': 'cyrillic', 'bg': 'cyrillic', 'mk': 'cyrillic', 'uk': 'cyrillic'
        }
        
        return script_mapping.get(language_code, 'latin')
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""        status = {
            "status": "healthy",
            "models_loaded": len(self.pipelines),
            "fallback_methods": len(self.fallback_methods),
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "langdetect_available": LANGDETECT_AVAILABLE,
            "supported_languages": len(self.iso_to_name)
        }
        
        # Test basic functionality
        try:
            if "primary" in self.pipelines:
                # Quick test with transformer model
                test_pipeline = self.pipelines["primary"]
                test_result = test_pipeline("This is a test sentence in English.")
                status["test_result"] = "passed"
            elif LANGDETECT_AVAILABLE:
                # Test with langdetect
                test_result = detect("This is a test sentence in English.")
                status["test_result"] = "fallback_passed"
            else:
                status["test_result"] = "rule_based_only"
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the language detector"""        logger.info("Shutting down Language Detector")
        
        # Clear models
        self.models.clear()
        self.pipelines.clear()
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def normalize_language_code(lang_code: str) -> str:
    """Normalize language code to ISO 639-1 format"""    # Handle common variations
    code_mappings = {
        'zh-cn': 'zh',
        'zh-tw': 'zh',
        'zh-hans': 'zh',
        'zh-hant': 'zh',
        'en-us': 'en',
        'en-gb': 'en',
        'pt-br': 'pt',
        'pt-pt': 'pt',
        'es-es': 'es',
        'es-mx': 'es'
    }
    
    normalized = lang_code.lower()
    return code_mappings.get(normalized, normalized[:2])

def get_language_family(language_code: str) -> str:
    """Get language family for a given language code"""    families = {
        'romance': ['es', 'fr', 'it', 'pt', 'ro', 'ca'],
        'germanic': ['en', 'de', 'nl', 'sv', 'da', 'no'],
        'slavic': ['ru', 'pl', 'cs', 'sk', 'bg', 'hr', 'sl', 'mk', 'uk'],
        'sino_tibetan': ['zh', 'th'],
        'semitic': ['ar', 'he'],
        'indo_iranian': ['hi', 'ur', 'fa', 'bn', 'gu', 'pa', 'ne'],
        'dravidian': ['ta', 'te', 'kn', 'ml'],
        'japonic': ['ja'],
        'koreanic': ['ko'],
        'finno_ugric': ['fi', 'hu', 'et'],
        'turkic': ['tr'],
        'niger_congo': ['sw'],
        'austronesian': ['id', 'tl']
    }
    
    for family, languages in families.items():
        if language_code in languages:
            return family
    
    return 'other'
