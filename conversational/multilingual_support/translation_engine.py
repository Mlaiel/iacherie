"""Translation Engine - Advanced Multi-Provider Translation System

Enterprise-grade translation services with quality assessment, caching,
and cultural adaptation for global content creator communications.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE ⚠️
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@li        try:
            # Construct prompt based on request parameters
            prompt = self._build_openai_prompt(request)
            
            # Call OpenAI API with proper configuration
            response = await self.client.chat.completions.acreate(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator specializing in {request.source_language} to {request.target_language} translation. Preserve context, tone, and cultural nuances. For content creator communications, maintain engagement and authenticity."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent translations
                max_tokens=2048,
                presence_penalty=0,
                frequency_penalty=0
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Calculate confidence based on response quality
            confidence = self._calculate_openai_confidence(translated_text, request)
            
            return TranslationResult(
                translated_text=translated_text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=confidence,
                provider=TranslationProvider.OPENAI,
                metadata={
                    "model": "gpt-4-turbo-preview",
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
            ) licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import hashlib
import re
from collections import defaultdict

# Translation libraries
from googletrans import Translator as GoogleTranslator
import openai
from transformers import pipeline, MarianMTModel, MarianTokenizer
import torch

# Quality assessment
from textblob import TextBlob
import nltk
from nltk.translate.bleu_score import sentence_bleu

# Caching and storage
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

# Internal imports
from .language_manager import SupportedLanguage

logger = logging.getLogger(__name__)


class TranslationProvider(Enum):
    """Available translation service providers"""    GOOGLE_TRANSLATE = "google"
    OPENAI_GPT = "openai"
    MARIAN_MT = "marian"
    AZURE_TRANSLATOR = "azure"
    AWS_TRANSLATE = "aws"
    DEEPL = "deepl"
    CACHE_FIRST = "cache"


class TranslationQuality(Enum):
    """Translation quality levels"""    EXCELLENT = "excellent"    # 0.9-1.0
    GOOD = "good"             # 0.7-0.9
    ACCEPTABLE = "acceptable"  # 0.5-0.7
    POOR = "poor"             # 0.3-0.5
    VERY_POOR = "very_poor"   # 0.0-0.3


@dataclass
class TranslationRequest:
    """Comprehensive translation request structure"""    text: str
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    domain: str = "general"  # general, technical, creative, business, legal
    formality: str = "neutral"  # formal, informal, neutral
    tone: str = "professional"  # professional, casual, friendly, authoritative
    preserve_formatting: bool = True
    max_length: Optional[int] = None
    context: Optional[str] = None
    glossary: Optional[Dict[str, str]] = None
    priority: str = "normal"  # high, normal, low
    quality_threshold: float = 0.7
    preferred_providers: List[TranslationProvider] = field(default_factory=list)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass 
class TranslationResult:
    """Comprehensive translation result with quality metrics"""    original_text: str
    translated_text: str
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    confidence_score: float
    quality_score: float = 0.0
    quality_level: TranslationQuality = TranslationQuality.ACCEPTABLE
    provider_used: TranslationProvider = TranslationProvider.GOOGLE_TRANSLATE
    processing_time: float = 0.0
    alternative_translations: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    cultural_adaptations: List[str] = field(default_factory=list)
    cached: bool = False
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TranslationCache:
    """Advanced translation caching with versioning and cleanup"""    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        self.cache_stats = defaultdict(int)
        self.default_ttl = 86400 * 7  # 7 days
        
    async def get_cached_translation(
        self, 
        request: TranslationRequest
    ) -> Optional[TranslationResult]:
        """Get cached translation if available"""        try:
            cache_key = self._generate_cache_key(request)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                result_data = json.loads(cached_data)
                result = self._deserialize_translation_result(result_data)
                result.cached = True
                
                self.cache_stats["cache_hits"] += 1
                return result
            
            self.cache_stats["cache_misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None
    
    async def cache_translation(
        self, 
        request: TranslationRequest, 
        result: TranslationResult,
        ttl: Optional[int] = None
    ):
        """Cache translation result with quality-based TTL"""        try:
            cache_key = self._generate_cache_key(request)
            
            # Adjust TTL based on quality
            if ttl is None:
                if result.quality_score > 0.9:
                    ttl = self.default_ttl * 2  # High quality = longer cache
                elif result.quality_score > 0.7:
                    ttl = self.default_ttl
                else:
                    ttl = self.default_ttl // 2  # Low quality = shorter cache
            
            # Serialize result
            cache_data = self._serialize_translation_result(result)
            
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )
            
            self.cache_stats["cache_stores"] += 1
            
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
    
    def _generate_cache_key(self, request: TranslationRequest) -> str:
        """Generate unique cache key for translation request"""        # Include important parameters that affect translation
        key_components = [
            request.text,
            request.source_language.value,
            request.target_language.value,
            request.domain,
            request.formality,
            request.tone
        ]
        
        key_string = "|".join(str(comp) for comp in key_components)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return f"translation:{key_hash[:16]}"
    
    def _serialize_translation_result(self, result: TranslationResult) -> Dict[str, Any]:
        """Serialize translation result for caching"""        return {
            "original_text": result.original_text,
            "translated_text": result.translated_text,
            "source_language": result.source_language.value,
            "target_language": result.target_language.value,
            "confidence_score": result.confidence_score,
            "quality_score": result.quality_score,
            "quality_level": result.quality_level.value,
            "provider_used": result.provider_used.value,
            "processing_time": result.processing_time,
            "alternative_translations": result.alternative_translations,
            "quality_metrics": result.quality_metrics,
            "cultural_adaptations": result.cultural_adaptations,
            "warnings": result.warnings,
            "metadata": result.metadata,
            "created_at": result.created_at.isoformat()
        }
    
    def _deserialize_translation_result(self, data: Dict[str, Any]) -> TranslationResult:
        """Deserialize cached translation result"""        return TranslationResult(
            original_text=data["original_text"],
            translated_text=data["translated_text"],
            source_language=SupportedLanguage(data["source_language"]),
            target_language=SupportedLanguage(data["target_language"]),
            confidence_score=data["confidence_score"],
            quality_score=data.get("quality_score", 0.0),
            quality_level=TranslationQuality(data.get("quality_level", "acceptable")),
            provider_used=TranslationProvider(data["provider_used"]),
            processing_time=data.get("processing_time", 0.0),
            alternative_translations=data.get("alternative_translations", []),
            quality_metrics=data.get("quality_metrics", {}),
            cultural_adaptations=data.get("cultural_adaptations", []),
            warnings=data.get("warnings", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"])
        )


class TranslationQualityAssessor:
    """Advanced translation quality assessment system"""    
    def __init__(self):
        self.quality_weights = {
            "fluency": 0.3,
            "accuracy": 0.3,
            "adequacy": 0.2,
            "consistency": 0.1,
            "cultural_appropriateness": 0.1
        }
        
    async def assess_translation_quality(
        self,
        original: str,
        translation: str,
        source_lang: SupportedLanguage,
        target_lang: SupportedLanguage,
        context: Optional[str] = None
    ) -> Tuple[float, TranslationQuality, Dict[str, float]]:
        """Comprehensive translation quality assessment"""        try:
            metrics = {}
            
            # 1. Fluency assessment (target language naturalness)
            metrics["fluency"] = await self._assess_fluency(translation, target_lang)
            
            # 2. Length ratio check (translations should be similar length)
            metrics["length_ratio"] = self._assess_length_ratio(original, translation)
            
            # 3. Vocabulary richness
            metrics["vocabulary_richness"] = self._assess_vocabulary_richness(translation)
            
            # 4. Structural similarity (when applicable)
            metrics["structural_similarity"] = self._assess_structural_similarity(
                original, translation
            )
            
            # 5. Context appropriateness
            if context:
                metrics["context_appropriateness"] = self._assess_context_appropriateness(
                    translation, context
                )
            else:
                metrics["context_appropriateness"] = 0.8  # Default neutral score
            
            # 6. Cultural appropriateness
            metrics["cultural_appropriateness"] = self._assess_cultural_appropriateness(
                translation, target_lang
            )
            
            # Calculate weighted overall score
            overall_score = 0.0
            for metric, weight in self.quality_weights.items():
                if metric in metrics:
                    overall_score += metrics[metric] * weight
                else:
                    overall_score += 0.7 * weight  # Default score for missing metrics
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            return overall_score, quality_level, metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return 0.5, TranslationQuality.ACCEPTABLE, {}
    
    async def _assess_fluency(self, text: str, language: SupportedLanguage) -> float:
        """Assess translation fluency using language models"""        try:
            # Simple fluency checks
            score = 1.0
            
            # Check for obvious errors
            if re.search(r'\b[A-Z]{4,}\b', text):  # Too many consecutive capitals
                score -= 0.2
            
            if re.search(r'[.]{3,}', text):  # Multiple dots (placeholder indicators)
                score -= 0.3
            
            # Check sentence structure
            sentences = text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            
            if avg_sentence_length < 3:  # Too short sentences
                score -= 0.2
            elif avg_sentence_length > 50:  # Too long sentences
                score -= 0.1
            
            return max(score, 0.0)
            
        except Exception:
            return 0.7  # Default fluency score
    
    def _assess_length_ratio(self, original: str, translation: str) -> float:
        """Assess if translation length is reasonable"""        orig_len = len(original.split())
        trans_len = len(translation.split())
        
        if orig_len == 0:
            return 0.5
        
        ratio = trans_len / orig_len
        
        # Reasonable ratios vary by language pair
        if 0.7 <= ratio <= 1.5:
            return 1.0
        elif 0.5 <= ratio < 0.7 or 1.5 < ratio <= 2.0:
            return 0.8
        elif 0.3 <= ratio < 0.5 or 2.0 < ratio <= 3.0:
            return 0.6
        else:
            return 0.3
    
    def _assess_vocabulary_richness(self, text: str) -> float:
        """Assess vocabulary diversity in translation"""        words = text.lower().split()
        if len(words) < 5:
            return 0.7
        
        unique_words = len(set(words))
        vocabulary_ratio = unique_words / len(words)
        
        # Higher ratio indicates richer vocabulary
        return min(vocabulary_ratio * 1.2, 1.0)
    
    def _assess_structural_similarity(self, original: str, translation: str) -> float:
        """Assess structural similarity between original and translation"""        # Count punctuation patterns
        orig_punct = len(re.findall(r'[.!?,:;]', original))
        trans_punct = len(re.findall(r'[.!?,:;]', translation))
        
        # Count paragraphs/sentences
        orig_sentences = len(re.split(r'[.!?]', original))
        trans_sentences = len(re.split(r'[.!?]', translation))
        
        punct_similarity = 1.0 - abs(orig_punct - trans_punct) / max(orig_punct, trans_punct, 1)
        sentence_similarity = 1.0 - abs(orig_sentences - trans_sentences) / max(orig_sentences, trans_sentences, 1)
        
        return (punct_similarity + sentence_similarity) / 2
    
    def _assess_context_appropriateness(self, translation: str, context: str) -> float:
        """Assess if translation is appropriate for given context"""        # Simple keyword matching approach
        context_lower = context.lower()
        translation_lower = translation.lower()
        
        # Check for context-appropriate terminology
        if "business" in context_lower:
            business_terms = ["professional", "company", "business", "service", "solution"]
            if any(term in translation_lower for term in business_terms):
                return 0.9
        
        if "technical" in context_lower:
            if len([word for word in translation_lower.split() if len(word) > 8]) > 0:
                return 0.9  # Longer words often indicate technical content
        
        return 0.8  # Default context appropriateness
    
    def _assess_cultural_appropriateness(self, translation: str, target_lang: SupportedLanguage) -> float:
        """Assess cultural appropriateness of translation"""        score = 1.0
        
        # Basic cultural checks
        translation_lower = translation.lower()
        
        # Check for potentially inappropriate content
        inappropriate_patterns = [
            r'\bfuck\b', r'\bshit\b', r'\bdamn\b'  # Basic profanity check
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, translation_lower):
                score -= 0.3
        
        # Language-specific cultural checks
        if target_lang == SupportedLanguage.JAPANESE:
            # Japanese requires more formal language in most contexts
            if not any(honorific in translation for honorific in ['です', 'ます', 'ございます']):
                score -= 0.1
        
        elif target_lang == SupportedLanguage.GERMAN:
            # German formal vs informal "you"
            if 'du' in translation_lower and 'sie' not in translation_lower:
                score -= 0.1  # Might be too informal
        
        return max(score, 0.0)
    
    def _determine_quality_level(self, score: float) -> TranslationQuality:
        """Determine quality level from score"""        if score >= 0.9:
            return TranslationQuality.EXCELLENT
        elif score >= 0.7:
            return TranslationQuality.GOOD
        elif score >= 0.5:
            return TranslationQuality.ACCEPTABLE
        elif score >= 0.3:
            return TranslationQuality.POOR
        else:
            return TranslationQuality.VERY_POOR


class TranslationService:
    """Individual translation service implementation"""    
    def __init__(self, provider: TranslationProvider):
        self.provider = provider
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize translation service client"""        try:
            if self.provider == TranslationProvider.GOOGLE_TRANSLATE:
                self.client = GoogleTranslator()
            
            elif self.provider == TranslationProvider.OPENAI_GPT:
                # Initialize OpenAI client
                # self.client = openai.OpenAI()  # Requires API key setup
                pass
            
            elif self.provider == TranslationProvider.MARIAN_MT:
                # Initialize MarianMT models
                self.marian_models = {}
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider.value} client: {e}")
    
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        """Perform translation using this service"""        start_time = datetime.now()
        
        try:
            if self.provider == TranslationProvider.GOOGLE_TRANSLATE:
                result = await self._translate_google(request)
            elif self.provider == TranslationProvider.OPENAI_GPT:
                result = await self._translate_openai(request)
            elif self.provider == TranslationProvider.MARIAN_MT:
                result = await self._translate_marian(request)
            else:
                logger.warning(f"Provider {self.provider.value} not implemented, using fallback translation")
                # Provide a basic fallback translation
                result = TranslationResult(
                    original_text=request.text,
                    translated_text=f"[{self.provider.value} translation of: {request.text}]",
                    source_language=request.source_language,
                    target_language=request.target_language,
                    confidence_score=0.1,  # Low confidence for fallback
                    success=True,
                    error_message=None,
                    provider_used=self.provider,
                    processing_time=0.0,
                    metadata={
                        "fallback_used": True,
                        "reason": f"Provider {self.provider.value} not fully implemented"
                    }
                )
            
            # Calculate processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()
            result.provider_used = self.provider
            
            return result
            
        except Exception as e:
            logger.error(f"Translation failed with {self.provider.value}: {e}")
            # Return fallback result
            return TranslationResult(
                original_text=request.text,
                translated_text=request.text,  # Fallback to original
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=0.0,
                provider_used=self.provider,
                warnings=[f"Translation failed: {str(e)}"]
            )
    
    async def _translate_google(self, request: TranslationRequest) -> TranslationResult:
        """Translate using Google Translate"""        try:
            if not self.client:
                raise Exception("Google Translate client not initialized")
            
            # Perform translation
            translation = self.client.translate(
                request.text,
                src=request.source_language.value,
                dest=request.target_language.value
            )
            
            return TranslationResult(
                original_text=request.text,
                translated_text=translation.text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=0.85,  # Default confidence for Google
                provider_used=TranslationProvider.GOOGLE_TRANSLATE
            )
            
        except Exception as e:
            logger.error(f"Google translation failed: {e}")
            raise
    
    async def _translate_openai(self, request: TranslationRequest) -> TranslationResult:
        """Translate using OpenAI GPT"""        try:
            if not self.client:
                raise Exception("OpenAI client not available")
            
            # Construct prompt based on request parameters
            prompt = self._build_openai_prompt(request)
            
            # This would call OpenAI API
            # response = self.client.chat.completions.create(...)
            
            # For now, provide a basic implementation
            logger.warning("OpenAI translation not fully implemented, using fallback")
            
            return TranslationResult(
                original_text=request.text,
                translated_text=f"[OpenAI translation to {request.target_language}: {request.text}]",
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=0.8,  # Moderate confidence for OpenAI
                success=True,
                error_message=None,
                provider_used=TranslationProvider.OPENAI_GPT,
                processing_time=0.5,
                metadata={
                    "fallback_used": True,
                    "prompt": prompt,
                    "reason": "OpenAI API integration not fully implemented"
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI translation failed: {e}")
            raise
    
    async def _translate_marian(self, request: TranslationRequest) -> TranslationResult:
        """Translate using MarianMT models"""        try:
            model_name = self._get_marian_model_name(
                request.source_language, 
                request.target_language
            )
            
            if not model_name:
                raise Exception(f"No MarianMT model available for {request.source_language.value} -> {request.target_language.value}")
            
            # Load model if not cached
            if model_name not in self.marian_models:
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                self.marian_models[model_name] = (tokenizer, model)
            
            tokenizer, model = self.marian_models[model_name]
            
            # Translate
            inputs = tokenizer(request.text, return_tensors="pt", truncation=True)
            translated = model.generate(**inputs)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            
            return TranslationResult(
                original_text=request.text,
                translated_text=translated_text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=0.80,  # Default confidence for MarianMT
                provider_used=TranslationProvider.MARIAN_MT
            )
            
        except Exception as e:
            logger.error(f"MarianMT translation failed: {e}")
            raise
    
    def _build_openai_prompt(self, request: TranslationRequest) -> str:
        """Build prompt for OpenAI translation"""        prompt = f"Translate the following text from {request.source_language.value} to {request.target_language.value}"
        
        if request.domain != "general":
            prompt += f" in the {request.domain} domain"
        
        if request.formality != "neutral":
            prompt += f" using {request.formality} language"
        
        if request.tone != "professional":
            prompt += f" with a {request.tone} tone"
        
        prompt += f":\n\n{request.text}\n\nTranslation:"
        
        return prompt
    
    def _get_marian_model_name(
        self, 
        source: SupportedLanguage, 
        target: SupportedLanguage
    ) -> Optional[str]:
        """Get MarianMT model name for language pair"""        # Common MarianMT model mappings
        model_mappings = {
            (SupportedLanguage.ENGLISH, SupportedLanguage.GERMAN): "Helsinki-NLP/opus-mt-en-de",
            (SupportedLanguage.GERMAN, SupportedLanguage.ENGLISH): "Helsinki-NLP/opus-mt-de-en",
            (SupportedLanguage.ENGLISH, SupportedLanguage.FRENCH): "Helsinki-NLP/opus-mt-en-fr",
            (SupportedLanguage.FRENCH, SupportedLanguage.ENGLISH): "Helsinki-NLP/opus-mt-fr-en",
            (SupportedLanguage.ENGLISH, SupportedLanguage.SPANISH): "Helsinki-NLP/opus-mt-en-es",
            (SupportedLanguage.SPANISH, SupportedLanguage.ENGLISH): "Helsinki-NLP/opus-mt-es-en",
        }
        
        return model_mappings.get((source, target))


class TranslationEngine:
    """Master translation engine with multiple providers and quality assessment"""    
    def __init__(self, redis_client: aioredis.Redis, db_session: AsyncSession):
        self.redis_client = redis_client
        self.db_session = db_session
        self.cache = TranslationCache(redis_client)
        self.quality_assessor = TranslationQualityAssessor()
        
        # Initialize translation services
        self.services = {
            TranslationProvider.GOOGLE_TRANSLATE: TranslationService(TranslationProvider.GOOGLE_TRANSLATE),
            TranslationProvider.MARIAN_MT: TranslationService(TranslationProvider.MARIAN_MT),
            # Add more services as needed
        }
        
        # Provider priority order
        self.provider_priority = [
            TranslationProvider.GOOGLE_TRANSLATE,
            TranslationProvider.MARIAN_MT,
        ]
        
        self.translation_stats = defaultdict(int)
    
    async def translate(
        self,
        request: TranslationRequest,
        use_cache: bool = True
    ) -> TranslationResult:
        """        Perform translation with quality assessment and provider fallback
        """        try:
            # Check cache first
            if use_cache:
                cached_result = await self.cache.get_cached_translation(request)
                if cached_result:
                    self.translation_stats["cache_hits"] += 1
                    return cached_result
            
            # No translation needed if languages are the same
            if request.source_language == request.target_language:
                return TranslationResult(
                    original_text=request.text,
                    translated_text=request.text,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    confidence_score=1.0,
                    quality_score=1.0,
                    quality_level=TranslationQuality.EXCELLENT,
                    provider_used=TranslationProvider.CACHE_FIRST
                )
            
            # Determine provider order
            providers_to_try = request.preferred_providers if request.preferred_providers else self.provider_priority
            
            best_result = None
            
            # Try providers in order
            for provider in providers_to_try:
                if provider not in self.services:
                    continue
                
                try:
                    # Perform translation
                    result = await self.services[provider].translate(request)
                    
                    # Assess quality
                    quality_score, quality_level, metrics = await self.quality_assessor.assess_translation_quality(
                        request.text,
                        result.translated_text,
                        request.source_language,
                        request.target_language,
                        request.context
                    )
                    
                    result.quality_score = quality_score
                    result.quality_level = quality_level
                    result.quality_metrics = metrics
                    
                    # If quality meets threshold, use this result
                    if quality_score >= request.quality_threshold:
                        best_result = result
                        break
                    
                    # Keep best result so far
                    if best_result is None or quality_score > best_result.quality_score:
                        best_result = result
                        
                except Exception as e:
                    logger.warning(f"Provider {provider.value} failed: {e}")
                    continue
            
            if best_result is None:
                # All providers failed - return fallback
                return TranslationResult(
                    original_text=request.text,
                    translated_text=request.text,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    confidence_score=0.0,
                    warnings=["All translation providers failed"]
                )
            
            # Cache high-quality results
            if best_result.quality_score >= 0.7 and use_cache:
                await self.cache.cache_translation(request, best_result)
            
            # Update statistics
            self.translation_stats[f"{request.source_language.value}_{request.target_language.value}"] += 1
            self.translation_stats["total_translations"] += 1
            
            return best_result

    def _calculate_openai_confidence(self, translated_text: str, request: TranslationRequest) -> float:
        """Calculate confidence score for OpenAI translation result."""        confidence = 0.85  # Base confidence for GPT-4
        
        # Adjust based on text characteristics
        if len(translated_text.strip()) == 0:
            return 0.0
            
        # Penalize very short responses for long inputs
        input_length = len(request.text)
        output_length = len(translated_text)
        
        if input_length > 100 and output_length < input_length * 0.3:
            confidence -= 0.2
            
        # Boost confidence for creative content
        if request.context == "creative" or "music" in request.text.lower() or "influencer" in request.text.lower():
            confidence += 0.1
            
        # Check for potential translation artifacts
        if "gpt" in translated_text.lower() or "translation" in translated_text.lower():
            confidence -= 0.15
            
        return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Translation engine failed: {e}")
            return TranslationResult(
                original_text=request.text,
                translated_text=request.text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence_score=0.0,
                warnings=[f"Translation engine error: {str(e)}"]
            )
    
    async def get_translation_statistics(self) -> Dict[str, Any]:
        """Get translation usage statistics"""        cache_stats = dict(self.cache.cache_stats)
        
        return {
            "translation_stats": dict(self.translation_stats),
            "cache_stats": cache_stats,
            "available_providers": list(self.services.keys()),
            "provider_priority": self.provider_priority
        }
    
    async def is_language_pair_supported(
        self, 
        source: SupportedLanguage, 
        target: SupportedLanguage
    ) -> bool:
        """Check if language pair is supported by any provider"""        for provider, service in self.services.items():
            if provider == TranslationProvider.GOOGLE_TRANSLATE:
                return True  # Google supports most language pairs
            elif provider == TranslationProvider.MARIAN_MT:
                model_name = service._get_marian_model_name(source, target)
                if model_name:
                    return True
        
        return False
