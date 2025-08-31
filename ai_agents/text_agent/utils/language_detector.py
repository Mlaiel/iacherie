"""Language Detector - Advanced Multi-language Detection and Translation Engine

Industrial-grade language detection and translation system for global content creators
with enterprise-level accuracy and comprehensive language support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from langdetect import detect, detect_langs, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import polyglot
from polyglot.detect import Detector as PolyglotDetector
from polyglot.detect.base import UnknownLanguage
import fasttext
from googletrans import Translator
import requests
import json
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import spacy
from textblob import TextBlob
import re

# Ensure consistent language detection results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class LanguageConfidence(Enum):
    """Language detection confidence levels"""    VERY_HIGH = "very_high"    # > 0.95
    HIGH = "high"              # > 0.85
    MEDIUM = "medium"          # > 0.70
    LOW = "low"                # > 0.50
    VERY_LOW = "very_low"      # <= 0.50

class TranslationQuality(Enum):
    """Translation quality levels"""    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"

@dataclass
class LanguageDetectionResult:
    """Language detection result with confidence and alternatives"""    language: str
    language_name: str
    confidence: float
    confidence_level: LanguageConfidence
    alternatives: List[Dict[str, Any]]
    detector_used: str
    text_length: int
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TranslationResult:
    """Translation result with quality assessment"""    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    translation_confidence: float
    quality_assessment: TranslationQuality
    translator_used: str
    processing_time: float
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class LanguageDetector:
    """    Advanced multi-language detection system with ensemble methods
    """    
    def __init__(self):
        self.supported_languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
            'ko': 'Korean', 'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)',
            'ar': 'Arabic', 'hi': 'Hindi', 'nl': 'Dutch', 'sv': 'Swedish',
            'no': 'Norwegian', 'da': 'Danish', 'fi': 'Finnish', 'pl': 'Polish',
            'cs': 'Czech', 'hu': 'Hungarian', 'ro': 'Romanian', 'bg': 'Bulgarian',
            'hr': 'Croatian', 'sk': 'Slovak', 'sl': 'Slovenian', 'et': 'Estonian',
            'lv': 'Latvian', 'lt': 'Lithuanian', 'el': 'Greek', 'tr': 'Turkish',
            'th': 'Thai', 'vi': 'Vietnamese', 'id': 'Indonesian', 'ms': 'Malay',
            'tl': 'Filipino', 'sw': 'Swahili', 'he': 'Hebrew', 'fa': 'Persian',
            'ur': 'Urdu', 'bn': 'Bengali', 'ta': 'Tamil', 'te': 'Telugu',
            'ml': 'Malayalam', 'kn': 'Kannada', 'gu': 'Gujarati', 'pa': 'Punjabi'
        }
        
        # Initialize detection models
        self._init_detection_models()
        
        # Detection statistics
        self.detection_stats = {
            "total_detections": 0,
            "successful_detections": 0,
            "average_confidence": 0.0,
            "language_distribution": {},
            "detector_usage": {}
        }
        
        logger.info(f"LanguageDetector initialized with {len(self.supported_languages)} supported languages")
    
    def _init_detection_models(self):
        """Initialize language detection models"""        try:
            # Initialize Google Translator (includes detection)
            self.google_translator = Translator()
            
            # Try to load FastText model for language detection
            try:
                self.fasttext_model = fasttext.load_model('lid.176.bin')
                self.fasttext_available = True
            except:
                logger.warning("FastText model not available")
                self.fasttext_available = False
            
            logger.info("Language detection models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing detection models: {e}")
    
    async def detect_language(
        self,
        text: str,
        method: str = "ensemble",
        min_length: int = 10
    ) -> LanguageDetectionResult:
        """        Detect language of input text using specified or ensemble method
        
        Args:
            text: Input text for language detection
            method: Detection method ('ensemble', 'langdetect', 'polyglot', 'fasttext', 'google')
            min_length: Minimum text length for reliable detection
            
        Returns:
            LanguageDetectionResult: Comprehensive detection results
        """        start_time = time.time()
        
        try:
            # Validate input
            if not text or len(text.strip()) < min_length:
                raise ValueError(f"Text too short for reliable detection (minimum {min_length} characters)")
            
            # Clean text for better detection
            cleaned_text = await self._preprocess_text_for_detection(text)
            
            if method == "ensemble":
                result = await self._ensemble_detection(cleaned_text)
            else:
                result = await self._single_method_detection(cleaned_text, method)
            
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.text_length = len(text)
            
            # Update statistics
            await self._update_detection_stats(result)
            
            logger.debug(f"Language detected: {result.language} ({result.confidence:.3f}) in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            # Return default English detection
            return LanguageDetectionResult(
                language="en",
                language_name="English",
                confidence=0.1,
                confidence_level=LanguageConfidence.VERY_LOW,
                alternatives=[],
                detector_used="fallback",
                text_length=len(text),
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def detect_multiple_languages(
        self,
        text: str,
        threshold: float = 0.3
    ) -> List[LanguageDetectionResult]:
        """        Detect multiple languages in mixed-language text
        
        Args:
            text: Input text potentially containing multiple languages
            threshold: Minimum confidence threshold for language detection
            
        Returns:
            List of LanguageDetectionResult for detected languages
        """        try:
            # Split text into segments
            segments = await self._segment_text_for_multilang_detection(text)
            
            detected_languages = []
            for segment in segments:
                if len(segment.strip()) > 10:  # Only process meaningful segments
                    result = await self.detect_language(segment, method="ensemble")
                    if result.confidence >= threshold:
                        detected_languages.append(result)
            
            # Remove duplicate languages and sort by confidence
            unique_languages = {}
            for result in detected_languages:
                if result.language not in unique_languages or result.confidence > unique_languages[result.language].confidence:
                    unique_languages[result.language] = result
            
            return sorted(unique_languages.values(), key=lambda x: x.confidence, reverse=True)
            
        except Exception as e:
            logger.error(f"Multi-language detection failed: {e}")
            return []
    
    async def _preprocess_text_for_detection(self, text: str) -> str:
        """Preprocess text to improve detection accuracy"""        # Remove URLs, emails, and social media handles
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remove excessive whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove numbers and special characters that don't contribute to language detection
        text = re.sub(r'\b\d+\b', '', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        return text.strip()
    
    async def _ensemble_detection(self, text: str) -> LanguageDetectionResult:
        """Use ensemble of multiple detection methods"""        detections = {}
        
        # LangDetect
        try:
            lang_result = await self._langdetect_detection(text)
            detections['langdetect'] = lang_result
        except:
            pass
        
        # Polyglot
        try:
            poly_result = await self._polyglot_detection(text)
            detections['polyglot'] = poly_result
        except:
            pass
        
        # FastText
        if self.fasttext_available:
            try:
                fasttext_result = await self._fasttext_detection(text)
                detections['fasttext'] = fasttext_result
            except:
                pass
        
        # Google Translate
        try:
            google_result = await self._google_detection(text)
            detections['google'] = google_result
        except:
            pass
        
        # Combine results using weighted voting
        return await self._combine_detection_results(detections, text)
    
    async def _single_method_detection(self, text: str, method: str) -> LanguageDetectionResult:
        """Use single detection method"""        if method == "langdetect":
            return await self._langdetect_detection(text)
        elif method == "polyglot":
            return await self._polyglot_detection(text)
        elif method == "fasttext" and self.fasttext_available:
            return await self._fasttext_detection(text)
        elif method == "google":
            return await self._google_detection(text)
        else:
            # Fallback to langdetect
            return await self._langdetect_detection(text)
    
    async def _langdetect_detection(self, text: str) -> LanguageDetectionResult:
        """Detect language using langdetect library"""        try:
            # Get top language
            detected_lang = detect(text)
            
            # Get all possible languages with probabilities
            lang_probs = detect_langs(text)
            
            # Extract main result
            main_prob = lang_probs[0].prob
            alternatives = [
                {"language": lang.lang, "confidence": lang.prob, "name": self.supported_languages.get(lang.lang, lang.lang)}
                for lang in lang_probs[1:5]  # Top 4 alternatives
            ]
            
            confidence_level = self._determine_confidence_level(main_prob)
            
            return LanguageDetectionResult(
                language=detected_lang,
                language_name=self.supported_languages.get(detected_lang, detected_lang),
                confidence=main_prob,
                confidence_level=confidence_level,
                alternatives=alternatives,
                detector_used="langdetect",
                text_length=len(text),
                processing_time=0.0  # Will be set by caller
            )
            
        except LangDetectException as e:
            logger.warning(f"LangDetect failed: {e}")
            raise
    
    async def _polyglot_detection(self, text: str) -> LanguageDetectionResult:
        """Detect language using polyglot library"""        try:
            detector = PolyglotDetector(text)
            
            confidence = detector.confidence
            detected_lang = detector.language.code
            language_name = detector.language.name
            
            confidence_level = self._determine_confidence_level(confidence)
            
            return LanguageDetectionResult(
                language=detected_lang,
                language_name=language_name,
                confidence=confidence,
                confidence_level=confidence_level,
                alternatives=[],  # Polyglot doesn't provide alternatives easily
                detector_used="polyglot",
                text_length=len(text),
                processing_time=0.0
            )
            
        except (UnknownLanguage, Exception) as e:
            logger.warning(f"Polyglot detection failed: {e}")
            raise
    
    async def _fasttext_detection(self, text: str) -> LanguageDetectionResult:
        """Detect language using FastText model"""        try:
            # Predict language
            predictions = self.fasttext_model.predict(text, k=5)  # Top 5 predictions
            
            # Extract results
            languages = [label.replace('__label__', '') for label in predictions[0]]
            scores = predictions[1]
            
            main_lang = languages[0]
            main_score = float(scores[0])
            
            # Create alternatives
            alternatives = [
                {
                    "language": lang,
                    "confidence": float(score),
                    "name": self.supported_languages.get(lang, lang)
                }
                for lang, score in zip(languages[1:], scores[1:])
            ]
            
            confidence_level = self._determine_confidence_level(main_score)
            
            return LanguageDetectionResult(
                language=main_lang,
                language_name=self.supported_languages.get(main_lang, main_lang),
                confidence=main_score,
                confidence_level=confidence_level,
                alternatives=alternatives,
                detector_used="fasttext",
                text_length=len(text),
                processing_time=0.0
            )
            
        except Exception as e:
            logger.warning(f"FastText detection failed: {e}")
            raise
    
    async def _google_detection(self, text: str) -> LanguageDetectionResult:
        """Detect language using Google Translate"""        try:
            detection = self.google_translator.detect(text)
            
            detected_lang = detection.lang
            confidence = detection.confidence
            
            confidence_level = self._determine_confidence_level(confidence)
            
            return LanguageDetectionResult(
                language=detected_lang,
                language_name=self.supported_languages.get(detected_lang, detected_lang),
                confidence=confidence,
                confidence_level=confidence_level,
                alternatives=[],  # Google doesn't provide alternatives in detection
                detector_used="google",
                text_length=len(text),
                processing_time=0.0
            )
            
        except Exception as e:
            logger.warning(f"Google detection failed: {e}")
            raise
    
    async def _combine_detection_results(
        self,
        detections: Dict[str, LanguageDetectionResult],
        text: str
    ) -> LanguageDetectionResult:
        """Combine multiple detection results using weighted voting"""        if not detections:
            raise ValueError("No detection results to combine")
        
        # Weights for different detectors
        detector_weights = {
            'langdetect': 1.0,
            'polyglot': 0.8,
            'fasttext': 1.2,
            'google': 0.9
        }
        
        # Vote for languages
        language_votes = {}
        for detector, result in detections.items():
            weight = detector_weights.get(detector, 1.0)
            weighted_confidence = result.confidence * weight
            
            if result.language in language_votes:
                language_votes[result.language] += weighted_confidence
            else:
                language_votes[result.language] = weighted_confidence
        
        # Find winning language
        winning_lang = max(language_votes, key=language_votes.get)
        winning_score = language_votes[winning_lang]
        
        # Normalize score to 0-1 range
        max_possible_score = sum(detector_weights.values())
        normalized_score = winning_score / max_possible_score
        
        # Create alternatives from other languages
        alternatives = []
        for lang, score in sorted(language_votes.items(), key=lambda x: x[1], reverse=True)[1:5]:
            alternatives.append({
                "language": lang,
                "confidence": score / max_possible_score,
                "name": self.supported_languages.get(lang, lang)
            })
        
        confidence_level = self._determine_confidence_level(normalized_score)
        
        return LanguageDetectionResult(
            language=winning_lang,
            language_name=self.supported_languages.get(winning_lang, winning_lang),
            confidence=normalized_score,
            confidence_level=confidence_level,
            alternatives=alternatives,
            detector_used="ensemble",
            text_length=len(text),
            processing_time=0.0,
            metadata={
                "detectors_used": list(detections.keys()),
                "raw_votes": language_votes
            }
        )
    
    def _determine_confidence_level(self, confidence: float) -> LanguageConfidence:
        """Determine confidence level based on score"""        if confidence > 0.95:
            return LanguageConfidence.VERY_HIGH
        elif confidence > 0.85:
            return LanguageConfidence.HIGH
        elif confidence > 0.70:
            return LanguageConfidence.MEDIUM
        elif confidence > 0.50:
            return LanguageConfidence.LOW
        else:
            return LanguageConfidence.VERY_LOW
    
    async def _segment_text_for_multilang_detection(self, text: str) -> List[str]:
        """Segment text for multi-language detection"""        # Simple segmentation by sentences and paragraphs
        segments = []
        
        # Split by paragraphs
        paragraphs = text.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                # Split long paragraphs by sentences
                sentences = paragraph.split('.')
                current_segment = ""
                
                for sentence in sentences:
                    if len(current_segment + sentence) > 200:  # Max segment size
                        if current_segment:
                            segments.append(current_segment.strip())
                        current_segment = sentence
                    else:
                        current_segment += sentence + "."
                
                if current_segment.strip():
                    segments.append(current_segment.strip())
        
        return segments
    
    async def _update_detection_stats(self, result: LanguageDetectionResult):
        """Update detection statistics"""        self.detection_stats["total_detections"] += 1
        
        if result.confidence > 0.5:
            self.detection_stats["successful_detections"] += 1
        
        # Update average confidence
        total_conf = (
            self.detection_stats["average_confidence"] * 
            (self.detection_stats["total_detections"] - 1) +
            result.confidence
        )
        self.detection_stats["average_confidence"] = total_conf / self.detection_stats["total_detections"]
        
        # Update language distribution
        lang = result.language
        self.detection_stats["language_distribution"][lang] = (
            self.detection_stats["language_distribution"].get(lang, 0) + 1
        )
        
        # Update detector usage
        detector = result.detector_used
        self.detection_stats["detector_usage"][detector] = (
            self.detection_stats["detector_usage"].get(detector, 0) + 1
        )
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics"""        return {
            **self.detection_stats,
            "supported_languages_count": len(self.supported_languages),
            "success_rate": (
                self.detection_stats["successful_detections"] / 
                max(1, self.detection_stats["total_detections"])
            )
        }


class TranslationEngine:
    """    Advanced multi-service translation engine with quality assessment
    """    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.translators = {}
        
        # Initialize translation services
        self._init_translation_services()
        
        # Translation statistics
        self.translation_stats = {
            "total_translations": 0,
            "successful_translations": 0,
            "average_quality_score": 0.0,
            "language_pairs": {},
            "service_usage": {}
        }
        
        logger.info("TranslationEngine initialized with multiple services")
    
    def _init_translation_services(self):
        """Initialize translation services"""        try:
            # Google Translate
            self.translators['google'] = Translator()
            
            # Try to initialize Transformers-based translator
            try:
                self.translators['marian'] = pipeline(
                    "translation",
                    model="Helsinki-NLP/opus-mt-en-de",  # Example model
                    device=0 if torch.cuda.is_available() else -1
                )
            except:
                logger.warning("Marian translation model not available")
            
            logger.info(f"Translation services initialized: {list(self.translators.keys())}")
            
        except Exception as e:
            logger.error(f"Error initializing translation services: {e}")
    
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        service: str = "auto",
        assess_quality: bool = True
    ) -> TranslationResult:
        """        Translate text with quality assessment and multiple service support
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            service: Translation service to use ('auto', 'google', 'marian')
            assess_quality: Whether to assess translation quality
            
        Returns:
            TranslationResult: Comprehensive translation results
        """        start_time = time.time()
        
        try:
            # Detect source language if not provided
            if not source_language:
                detection_result = await self.language_detector.detect_language(text)
                source_language = detection_result.language
                source_detection_confidence = detection_result.confidence
            else:
                source_detection_confidence = 1.0
            
            # Select translation service
            if service == "auto":
                service = await self._select_best_service(source_language, target_language)
            
            # Perform translation
            translated_text, translation_confidence = await self._translate_with_service(
                text, source_language, target_language, service
            )
            
            # Assess translation quality
            quality_assessment = TranslationQuality.ACCEPTABLE
            if assess_quality:
                quality_assessment = await self._assess_translation_quality(
                    text, translated_text, source_language, target_language
                )
            
            # Generate alternatives if main translation quality is low
            alternatives = []
            if quality_assessment in [TranslationQuality.POOR] and len(self.translators) > 1:
                alternatives = await self._generate_translation_alternatives(
                    text, source_language, target_language, exclude_service=service
                )
            
            processing_time = time.time() - start_time
            
            result = TranslationResult(
                source_text=text,
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                translation_confidence=translation_confidence,
                quality_assessment=quality_assessment,
                translator_used=service,
                processing_time=processing_time,
                alternatives=alternatives,
                metadata={
                    'source_detection_confidence': source_detection_confidence,
                    'text_length': len(text),
                    'translated_length': len(translated_text),
                    'timestamp': time.time()
                }
            )
            
            # Update statistics
            await self._update_translation_stats(result)
            
            logger.debug(f"Translation completed: {source_language} -> {target_language} in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return fallback result
            return TranslationResult(
                source_text=text,
                translated_text=text,  # Fallback: return original text
                source_language=source_language or "unknown",
                target_language=target_language,
                translation_confidence=0.0,
                quality_assessment=TranslationQuality.POOR,
                translator_used="fallback",
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def _select_best_service(self, source_lang: str, target_lang: str) -> str:
        """Select best translation service for language pair"""        # Simple heuristic: prefer Google for most language pairs
        # In production, this could be based on historical quality scores
        
        if 'google' in self.translators:
            return 'google'
        elif 'marian' in self.translators and source_lang == 'en':
            return 'marian'
        else:
            return list(self.translators.keys())[0] if self.translators else 'google'
    
    async def _translate_with_service(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        service: str
    ) -> Tuple[str, float]:
        """Translate text using specified service"""        if service == 'google' and 'google' in self.translators:
            return await self._google_translate(text, source_lang, target_lang)
        elif service == 'marian' and 'marian' in self.translators:
            return await self._marian_translate(text, source_lang, target_lang)
        else:
            raise ValueError(f"Translation service '{service}' not available")
    
    async def _google_translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Tuple[str, float]:
        """Translate using Google Translate"""        try:
            result = self.translators['google'].translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            
            translated_text = result.text
            # Google doesn't provide confidence, so we estimate it
            confidence = 0.85  # Default confidence for Google Translate
            
            return translated_text, confidence
            
        except Exception as e:
            logger.error(f"Google translation failed: {e}")
            raise
    
    async def _marian_translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Tuple[str, float]:
        """Translate using Marian transformer model"""        try:
            # Note: This is simplified - in practice you'd need specific models for each language pair
            result = self.translators['marian'](text)
            
            if result and len(result) > 0:
                translated_text = result[0]['translation_text']
                confidence = 0.80  # Default confidence for Marian
                return translated_text, confidence
            else:
                raise ValueError("No translation result from Marian")
                
        except Exception as e:
            logger.error(f"Marian translation failed: {e}")
            raise
    
    async def _assess_translation_quality(
        self,
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationQuality:
        """Assess quality of translation"""        try:
            # Basic quality metrics
            length_ratio = len(translated_text) / len(source_text) if source_text else 0
            
            # Length-based quality assessment (simplified)
            if 0.3 <= length_ratio <= 3.0:  # Reasonable length ratio
                if len(translated_text.split()) > 0:  # Has actual content
                    # Additional checks could include:
                    # - Back-translation comparison
                    # - Semantic similarity using embeddings
                    # - Language-specific quality metrics
                    
                    # For now, use simple heuristics
                    if 0.5 <= length_ratio <= 2.0:
                        return TranslationQuality.GOOD
                    else:
                        return TranslationQuality.ACCEPTABLE
                else:
                    return TranslationQuality.POOR
            else:
                return TranslationQuality.POOR
                
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return TranslationQuality.ACCEPTABLE
    
    async def _generate_translation_alternatives(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        exclude_service: str,
        max_alternatives: int = 2
    ) -> List[str]:
        """Generate alternative translations using different services"""        alternatives = []
        
        for service_name, service in self.translators.items():
            if service_name != exclude_service and len(alternatives) < max_alternatives:
                try:
                    alt_text, _ = await self._translate_with_service(
                        text, source_lang, target_lang, service_name
                    )
                    if alt_text not in alternatives:
                        alternatives.append(alt_text)
                except:
                    continue
        
        return alternatives
    
    async def _update_translation_stats(self, result: TranslationResult):
        """Update translation statistics"""        self.translation_stats["total_translations"] += 1
        
        if result.quality_assessment != TranslationQuality.POOR:
            self.translation_stats["successful_translations"] += 1
        
        # Update language pairs
        lang_pair = f"{result.source_language}-{result.target_language}"
        self.translation_stats["language_pairs"][lang_pair] = (
            self.translation_stats["language_pairs"].get(lang_pair, 0) + 1
        )
        
        # Update service usage
        service = result.translator_used
        self.translation_stats["service_usage"][service] = (
            self.translation_stats["service_usage"].get(service, 0) + 1
        )
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """Get translation statistics"""        return {
            **self.translation_stats,
            "available_services": list(self.translators.keys()),
            "success_rate": (
                self.translation_stats["successful_translations"] / 
                max(1, self.translation_stats["total_translations"])
            )
        }
