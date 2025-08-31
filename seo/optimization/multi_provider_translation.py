#!/usr/bin/env python3
"""
Multi-Provider Translation APIs Manager
=======================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides unified access to multiple translation providers:
- Google Translate: 100+ languages neural MT
- DeepL: Superior quality EU, 31 languages  
- Microsoft Translator: Enterprise, 100+ languages
- Amazon Translate: Auto scaling, 75 languages

Features:
- Unified API interface
- Provider failover and load balancing
- Quality-based provider selection
- Cost optimization
- Rate limiting and caching
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple
import hashlib
import requests
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class TranslationProvider(Enum):
    """Available translation providers"""
    GOOGLE = "google"
    DEEPL = "deepl"
    MICROSOFT = "microsoft"
    AMAZON = "amazon"
    OPENAI = "openai"  # Bonus provider


class TranslationQuality(Enum):
    """Translation quality tiers"""
    BASIC = "basic"           # Fast, cost-effective
    STANDARD = "standard"     # Balanced quality/speed
    PROFESSIONAL = "professional"  # High quality
    PREMIUM = "premium"       # Best available quality


class ProviderCapability(Enum):
    """Provider capabilities"""
    NEURAL_MT = "neural_mt"
    DOCUMENT_TRANSLATION = "document_translation"
    REAL_TIME = "real_time"
    BULK_TRANSLATION = "bulk_translation"
    CUSTOM_MODELS = "custom_models"
    GLOSSARY_SUPPORT = "glossary_support"
    FORMALITY_CONTROL = "formality_control"


@dataclass
class TranslationRequest:
    """Translation request structure"""
    text: str
    source_language: str
    target_language: str
    quality: TranslationQuality = TranslationQuality.STANDARD
    context: Optional[str] = None
    domain: Optional[str] = None
    formality: Optional[str] = None  # formal/informal for DeepL
    preserve_formatting: bool = True
    detect_language: bool = False


@dataclass
class TranslationResponse:
    """Translation response structure"""
    translated_text: str
    source_language: str
    target_language: str
    provider: TranslationProvider
    confidence: float
    processing_time: float
    cost: float = 0.0
    detected_language: Optional[str] = None
    alternatives: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class ProviderConfig:
    """Provider configuration"""
    name: TranslationProvider
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    endpoint: Optional[str] = None
    region: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    cost_per_char: float = 0.00002  # cost per character
    supported_languages: List[str] = None
    capabilities: List[ProviderCapability] = None
    quality_score: float = 0.8  # base quality score
    enabled: bool = True


class BaseTranslationProvider(ABC):
    """Base class for translation providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.request_count = 0
        self.last_request_time = 0
        self.cache = {}  # Simple in-memory cache
        
    @abstractmethod
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using this provider"""
        pass
    
    @abstractmethod
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported by this provider"""
        pass
    
    def can_handle_request(self, request: TranslationRequest) -> bool:
        """Check if provider can handle the request"""
        if not self.config.enabled:
            return False
        
        # Check language support
        if not self.is_language_supported(request.source_language):
            return False
        if not self.is_language_supported(request.target_language):
            return False
        
        # Check rate limits
        current_time = time.time()
        if current_time - self.last_request_time < 60:  # Within last minute
            if self.request_count >= self.config.rate_limit:
                return False
        else:
            self.request_count = 0  # Reset count for new minute
        
        return True
    
    def _get_cache_key(self, request: TranslationRequest) -> str:
        """Generate cache key for request"""
        text_hash = hashlib.md5(request.text.encode()).hexdigest()
        return f"{request.source_language}_{request.target_language}_{text_hash}_{request.quality.value}"
    
    def _update_rate_limit(self):
        """Update rate limiting counters"""
        current_time = time.time()
        if current_time - self.last_request_time >= 60:
            self.request_count = 0
        self.request_count += 1
        self.last_request_time = current_time


class GoogleTranslateProvider(BaseTranslationProvider):
    """Google Translate API provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.endpoint = config.endpoint or "https://translation.googleapis.com/language/translate/v2"
        self.supported_languages = {
            "af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "ny", "zh", "zh-cn", "zh-tw",
            "co", "hr", "cs", "da", "nl", "en", "eo", "et", "tl", "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht",
            "ha", "haw", "he", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn", "kk", "km", "ko", "ku",
            "ky", "lo", "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "or",
            "ps", "fa", "pl", "pt", "pa", "ro", "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so", "es",
            "su", "sw", "sv", "tg", "ta", "te", "th", "tr", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi", "yo", "zu"
        }
    
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate using Google Translate API"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(request)
            if cache_key in self.cache:
                cached_response = self.cache[cache_key]
                cached_response.processing_time = time.time() - start_time
                return cached_response
            
            # Prepare API request
            params = {
                "key": self.config.api_key,
                "q": request.text,
                "target": request.target_language,
                "source": request.source_language if not request.detect_language else None,
                "format": "text"
            }
            
            # Make API call (simulated for demo)
            response_data = await self._make_api_call(params)
            
            # Parse response
            translated_text = response_data.get("data", {}).get("translations", [{}])[0].get("translatedText", "")
            detected_language = response_data.get("data", {}).get("translations", [{}])[0].get("detectedSourceLanguage")
            
            # Calculate confidence based on text length and provider quality
            confidence = min(0.95, 0.7 + (len(request.text) / 1000) * 0.2)
            
            # Calculate cost
            cost = len(request.text) * self.config.cost_per_char
            
            response = TranslationResponse(
                translated_text=translated_text,
                source_language=detected_language or request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.GOOGLE,
                confidence=confidence,
                processing_time=time.time() - start_time,
                cost=cost,
                detected_language=detected_language,
                metadata={
                    "model": "neural_mt",
                    "api_version": "v2",
                    "quality": request.quality.value
                }
            )
            
            # Cache response
            self.cache[cache_key] = response
            self._update_rate_limit()
            
            return response
            
        except Exception as e:
            logger.error(f"Google Translate error: {str(e)}")
            return TranslationResponse(
                translated_text=f"[Translation Error: {str(e)}]",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.GOOGLE,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def _make_api_call(self, params: Dict) -> Dict:
        """Make API call to Google Translate (simulated)"""
        # In real implementation, this would make actual HTTP request
        # For demo purposes, we'll simulate a response
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return {
            "data": {
                "translations": [{
                    "translatedText": f"[GOOGLE_TRANSLATED] {params['q']}",
                    "detectedSourceLanguage": params.get("source", "en")
                }]
            }
        }
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported by Google Translate"""
        return language_code.lower() in self.supported_languages


class DeepLProvider(BaseTranslationProvider):
    """DeepL API provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.endpoint = config.endpoint or "https://api-free.deepl.com/v2/translate"
        # DeepL supports fewer languages but with higher quality
        self.supported_languages = {
            "bg", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr", "hu", "id", "it", "ja", "ko", "lt", "lv",
            "nb", "nl", "pl", "pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "zh"
        }
        
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate using DeepL API"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(request)
            if cache_key in self.cache:
                cached_response = self.cache[cache_key]
                cached_response.processing_time = time.time() - start_time
                return cached_response
            
            # Prepare API request
            data = {
                "auth_key": self.config.api_key,
                "text": request.text,
                "target_lang": request.target_language.upper(),
                "source_lang": request.source_language.upper() if not request.detect_language else None,
                "preserve_formatting": "1" if request.preserve_formatting else "0",
                "formality": request.formality if request.formality else "default"
            }
            
            # Make API call (simulated for demo)
            response_data = await self._make_api_call(data)
            
            # Parse response
            translations = response_data.get("translations", [])
            if translations:
                translated_text = translations[0].get("text", "")
                detected_language = translations[0].get("detected_source_language", "").lower()
            else:
                translated_text = ""
                detected_language = None
            
            # DeepL typically has higher confidence
            confidence = min(0.98, 0.85 + (len(request.text) / 1000) * 0.1)
            
            # Calculate cost (DeepL is more expensive but higher quality)
            cost = len(request.text) * (self.config.cost_per_char * 1.5)
            
            response = TranslationResponse(
                translated_text=translated_text,
                source_language=detected_language or request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.DEEPL,
                confidence=confidence,
                processing_time=time.time() - start_time,
                cost=cost,
                detected_language=detected_language,
                metadata={
                    "model": "neural_transformer",
                    "api_version": "v2",
                    "formality": request.formality,
                    "quality": request.quality.value
                }
            )
            
            # Cache response
            self.cache[cache_key] = response
            self._update_rate_limit()
            
            return response
            
        except Exception as e:
            logger.error(f"DeepL error: {str(e)}")
            return TranslationResponse(
                translated_text=f"[Translation Error: {str(e)}]",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.DEEPL,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def _make_api_call(self, data: Dict) -> Dict:
        """Make API call to DeepL (simulated)"""
        # In real implementation, this would make actual HTTP request
        await asyncio.sleep(0.15)  # Simulate slightly longer processing for higher quality
        
        return {
            "translations": [{
                "text": f"[DEEPL_TRANSLATED] {data['text']}",
                "detected_source_language": data.get("source_lang", "EN").upper()
            }]
        }
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported by DeepL"""
        return language_code.lower() in self.supported_languages


class MicrosoftTranslatorProvider(BaseTranslationProvider):
    """Microsoft Translator API provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.endpoint = config.endpoint or "https://api.cognitive.microsofttranslator.com/translate"
        self.supported_languages = {
            "af", "am", "ar", "as", "az", "ba", "bg", "bn", "bo", "bs", "ca", "cs", "cy", "da", "de", "dv", "el", "en",
            "es", "et", "eu", "fa", "fi", "fj", "fo", "fr", "fr-ca", "ga", "gl", "gu", "ha", "he", "hi", "hr", "hsb",
            "ht", "hu", "hy", "id", "ig", "is", "it", "iu", "ja", "ka", "kk", "km", "kn", "ko", "ku", "ky", "lo", "lt",
            "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "mww", "my", "nb", "ne", "nl", "nn", "nso", "or", "pa",
            "pl", "prs", "ps", "pt", "pt-pt", "ro", "ru", "sk", "sl", "sm", "so", "sq", "sr-cyrl", "sr-latn", "sv", "sw",
            "ta", "te", "th", "ti", "tk", "tlh", "tn", "to", "tr", "tt", "ty", "ug", "uk", "ur", "uz", "vi", "xh", "yo",
            "yua", "yue", "zh-hans", "zh-hant", "zu"
        }
    
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate using Microsoft Translator API"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(request)
            if cache_key in self.cache:
                cached_response = self.cache[cache_key]
                cached_response.processing_time = time.time() - start_time
                return cached_response
            
            # Prepare API request
            headers = {
                "Ocp-Apim-Subscription-Key": self.config.api_key,
                "Ocp-Apim-Subscription-Region": self.config.region or "global",
                "Content-Type": "application/json"
            }
            
            params = {
                "api-version": "3.0",
                "to": request.target_language
            }
            
            if not request.detect_language:
                params["from"] = request.source_language
            
            body = [{"text": request.text}]
            
            # Make API call (simulated for demo)
            response_data = await self._make_api_call(headers, params, body)
            
            # Parse response
            if response_data and len(response_data) > 0:
                translation = response_data[0]
                translated_text = translation.get("translations", [{}])[0].get("text", "")
                detected_language = translation.get("detectedLanguage", {}).get("language")
            else:
                translated_text = ""
                detected_language = None
            
            # Microsoft typically has good confidence
            confidence = min(0.92, 0.75 + (len(request.text) / 1000) * 0.15)
            
            # Calculate cost
            cost = len(request.text) * self.config.cost_per_char
            
            response = TranslationResponse(
                translated_text=translated_text,
                source_language=detected_language or request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.MICROSOFT,
                confidence=confidence,
                processing_time=time.time() - start_time,
                cost=cost,
                detected_language=detected_language,
                metadata={
                    "model": "neural_mt",
                    "api_version": "3.0",
                    "quality": request.quality.value
                }
            )
            
            # Cache response
            self.cache[cache_key] = response
            self._update_rate_limit()
            
            return response
            
        except Exception as e:
            logger.error(f"Microsoft Translator error: {str(e)}")
            return TranslationResponse(
                translated_text=f"[Translation Error: {str(e)}]",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.MICROSOFT,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def _make_api_call(self, headers: Dict, params: Dict, body: List) -> List:
        """Make API call to Microsoft Translator (simulated)"""
        await asyncio.sleep(0.12)  # Simulate network delay
        
        return [{
            "translations": [{
                "text": f"[MICROSOFT_TRANSLATED] {body[0]['text']}",
                "to": params["to"]
            }],
            "detectedLanguage": {
                "language": params.get("from", "en"),
                "score": 0.95
            }
        }]
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported by Microsoft Translator"""
        return language_code.lower() in self.supported_languages


class AmazonTranslateProvider(BaseTranslationProvider):
    """Amazon Translate provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.region = config.region or "us-east-1"
        self.supported_languages = {
            "af", "sq", "am", "ar", "hy", "az", "bn", "bs", "bg", "ca", "zh", "zh-tw", "hr", "cs", "da", "fa-af", "nl",
            "en", "et", "fa", "tl", "fi", "fr", "fr-ca", "ka", "de", "el", "gu", "ht", "ha", "he", "hi", "hu", "is", "id",
            "ga", "it", "ja", "kn", "kk", "ko", "lv", "lt", "mk", "ms", "ml", "mt", "mn", "no", "ps", "pl", "pt", "pt-pt",
            "pa", "ro", "ru", "sr", "si", "sk", "sl", "so", "es", "es-mx", "sw", "sv", "ta", "te", "th", "tr", "uk", "ur",
            "uz", "vi", "cy", "zu"
        }
    
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate using Amazon Translate"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(request)
            if cache_key in self.cache:
                cached_response = self.cache[cache_key]
                cached_response.processing_time = time.time() - start_time
                return cached_response
            
            # Prepare request for AWS API (simulated)
            translate_request = {
                "Text": request.text,
                "SourceLanguageCode": request.source_language if not request.detect_language else "auto",
                "TargetLanguageCode": request.target_language,
                "Settings": {
                    "Formality": request.formality if request.formality else "INFORMAL"
                }
            }
            
            # Make API call (simulated for demo)
            response_data = await self._make_api_call(translate_request)
            
            # Parse response
            translated_text = response_data.get("TranslatedText", "")
            detected_language = response_data.get("SourceLanguageCode")
            
            # Amazon Translate confidence
            confidence = min(0.90, 0.72 + (len(request.text) / 1000) * 0.18)
            
            # Calculate cost (Amazon is typically cost-effective)
            cost = len(request.text) * (self.config.cost_per_char * 0.8)
            
            response = TranslationResponse(
                translated_text=translated_text,
                source_language=detected_language or request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.AMAZON,
                confidence=confidence,
                processing_time=time.time() - start_time,
                cost=cost,
                detected_language=detected_language if request.detect_language else None,
                metadata={
                    "model": "neural_mt",
                    "region": self.region,
                    "quality": request.quality.value
                }
            )
            
            # Cache response
            self.cache[cache_key] = response
            self._update_rate_limit()
            
            return response
            
        except Exception as e:
            logger.error(f"Amazon Translate error: {str(e)}")
            return TranslationResponse(
                translated_text=f"[Translation Error: {str(e)}]",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.AMAZON,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def _make_api_call(self, request_data: Dict) -> Dict:
        """Make API call to Amazon Translate (simulated)"""
        await asyncio.sleep(0.08)  # Simulate fast AWS processing
        
        return {
            "TranslatedText": f"[AMAZON_TRANSLATED] {request_data['Text']}",
            "SourceLanguageCode": request_data.get("SourceLanguageCode", "en").replace("auto", "en"),
            "TargetLanguageCode": request_data["TargetLanguageCode"]
        }
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported by Amazon Translate"""
        return language_code.lower() in self.supported_languages


class MultiProviderTranslationManager:
    """
    Unified manager for multiple translation providers with intelligent routing,
    failover, load balancing, and quality optimization.
    """
    
    def __init__(self):
        """Initialize multi-provider translation manager"""
        self.providers: Dict[TranslationProvider, BaseTranslationProvider] = {}
        self.provider_configs: Dict[TranslationProvider, ProviderConfig] = {}
        self.global_cache = {}
        self.performance_stats = {}
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default provider configurations"""
        self.provider_configs = {
            TranslationProvider.GOOGLE: ProviderConfig(
                name=TranslationProvider.GOOGLE,
                rate_limit=100,
                cost_per_char=0.00002,
                quality_score=0.85,
                capabilities=[
                    ProviderCapability.NEURAL_MT,
                    ProviderCapability.REAL_TIME,
                    ProviderCapability.BULK_TRANSLATION
                ]
            ),
            TranslationProvider.DEEPL: ProviderConfig(
                name=TranslationProvider.DEEPL,
                rate_limit=50,
                cost_per_char=0.00003,
                quality_score=0.95,
                capabilities=[
                    ProviderCapability.NEURAL_MT,
                    ProviderCapability.FORMALITY_CONTROL,
                    ProviderCapability.REAL_TIME
                ]
            ),
            TranslationProvider.MICROSOFT: ProviderConfig(
                name=TranslationProvider.MICROSOFT,
                rate_limit=200,
                cost_per_char=0.000015,
                quality_score=0.88,
                capabilities=[
                    ProviderCapability.NEURAL_MT,
                    ProviderCapability.DOCUMENT_TRANSLATION,
                    ProviderCapability.BULK_TRANSLATION,
                    ProviderCapability.CUSTOM_MODELS
                ]
            ),
            TranslationProvider.AMAZON: ProviderConfig(
                name=TranslationProvider.AMAZON,
                rate_limit=150,
                cost_per_char=0.000012,
                quality_score=0.82,
                capabilities=[
                    ProviderCapability.NEURAL_MT,
                    ProviderCapability.BULK_TRANSLATION,
                    ProviderCapability.REAL_TIME
                ]
            )
        }
    
    def configure_provider(self, provider: TranslationProvider, config: ProviderConfig):
        """Configure a specific provider"""
        self.provider_configs[provider] = config
        
        # Initialize provider instance
        if provider == TranslationProvider.GOOGLE:
            self.providers[provider] = GoogleTranslateProvider(config)
        elif provider == TranslationProvider.DEEPL:
            self.providers[provider] = DeepLProvider(config)
        elif provider == TranslationProvider.MICROSOFT:
            self.providers[provider] = MicrosoftTranslatorProvider(config)
        elif provider == TranslationProvider.AMAZON:
            self.providers[provider] = AmazonTranslateProvider(config)
        
        logger.info(f"Configured provider: {provider.value}")
    
    def initialize_all_providers(self, api_keys: Dict[TranslationProvider, str]):
        """Initialize all providers with API keys"""
        for provider, api_key in api_keys.items():
            if provider in self.provider_configs:
                config = self.provider_configs[provider]
                config.api_key = api_key
                self.configure_provider(provider, config)
    
    async def translate(self, request: TranslationRequest, 
                       preferred_provider: Optional[TranslationProvider] = None) -> TranslationResponse:
        """
        Translate text using the best available provider
        """
        # Check global cache first
        cache_key = self._get_global_cache_key(request)
        if cache_key in self.global_cache:
            cached_response = self.global_cache[cache_key]
            logger.info(f"Cache hit for translation request")
            return cached_response
        
        # Select best provider
        provider = self._select_best_provider(request, preferred_provider)
        
        if not provider:
            return TranslationResponse(
                translated_text="[No suitable provider available]",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=TranslationProvider.GOOGLE,  # Default fallback
                confidence=0.0,
                processing_time=0.0,
                metadata={"error": "No suitable provider available"}
            )
        
        try:
            # Attempt translation with selected provider
            response = await self.providers[provider].translate(request)
            
            # Update performance stats
            self._update_performance_stats(provider, response)
            
            # Cache successful response
            if response.confidence > 0.5:
                self.global_cache[cache_key] = response
            
            return response
            
        except Exception as e:
            logger.error(f"Translation failed with {provider.value}: {str(e)}")
            
            # Try fallback provider
            fallback_provider = self._get_fallback_provider(provider, request)
            if fallback_provider and fallback_provider != provider:
                try:
                    logger.info(f"Attempting fallback to {fallback_provider.value}")
                    response = await self.providers[fallback_provider].translate(request)
                    self._update_performance_stats(fallback_provider, response)
                    return response
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {str(fallback_error)}")
            
            # Return error response
            return TranslationResponse(
                translated_text=f"[Translation failed: {str(e)}]",
                source_language=request.source_language,
                target_language=request.target_language,
                provider=provider,
                confidence=0.0,
                processing_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _select_best_provider(self, request: TranslationRequest, 
                            preferred_provider: Optional[TranslationProvider] = None) -> Optional[TranslationProvider]:
        """Select the best provider for the request"""
        
        if preferred_provider and preferred_provider in self.providers:
            provider_instance = self.providers[preferred_provider]
            if provider_instance.can_handle_request(request):
                return preferred_provider
        
        # Score providers based on multiple factors
        provider_scores = {}
        
        for provider_type, provider_instance in self.providers.items():
            if not provider_instance.can_handle_request(request):
                continue
            
            config = self.provider_configs[provider_type]
            score = 0.0
            
            # Base quality score
            score += config.quality_score * 40
            
            # Quality tier preference
            if request.quality == TranslationQuality.PREMIUM and provider_type == TranslationProvider.DEEPL:
                score += 20
            elif request.quality == TranslationQuality.PROFESSIONAL and provider_type in [TranslationProvider.DEEPL, TranslationProvider.MICROSOFT]:
                score += 15
            elif request.quality == TranslationQuality.BASIC and provider_type == TranslationProvider.AMAZON:
                score += 10
            
            # Cost efficiency
            cost_factor = 1.0 / (config.cost_per_char * 1000000)  # Normalize cost
            score += cost_factor * 10
            
            # Performance history
            if provider_type in self.performance_stats:
                stats = self.performance_stats[provider_type]
                avg_confidence = stats.get("avg_confidence", 0.5)
                avg_speed = 1.0 / max(stats.get("avg_processing_time", 1.0), 0.1)
                score += avg_confidence * 15 + avg_speed * 5
            
            # Language pair optimization
            if self._is_optimal_language_pair(provider_type, request.source_language, request.target_language):
                score += 10
            
            provider_scores[provider_type] = score
        
        # Return provider with highest score
        if provider_scores:
            best_provider = max(provider_scores, key=provider_scores.get)
            logger.info(f"Selected provider: {best_provider.value} (score: {provider_scores[best_provider]:.2f})")
            return best_provider
        
        return None
    
    def _is_optimal_language_pair(self, provider: TranslationProvider, source: str, target: str) -> bool:
        """Check if provider is optimal for this language pair"""
        # DeepL is optimal for European languages
        if provider == TranslationProvider.DEEPL:
            european_langs = {"en", "de", "fr", "es", "it", "pt", "pl", "nl", "ru", "cs", "da", "sv", "no", "fi"}
            return source.lower() in european_langs and target.lower() in european_langs
        
        # Google is good for Asian languages
        if provider == TranslationProvider.GOOGLE:
            asian_langs = {"zh", "ja", "ko", "th", "vi", "hi", "ar", "fa"}
            return source.lower() in asian_langs or target.lower() in asian_langs
        
        # Microsoft is good for document translation
        if provider == TranslationProvider.MICROSOFT:
            return len(source) > 1000  # Longer texts
        
        return False
    
    def _get_fallback_provider(self, failed_provider: TranslationProvider, 
                             request: TranslationRequest) -> Optional[TranslationProvider]:
        """Get fallback provider when primary fails"""
        # Define fallback chains
        fallback_chains = {
            TranslationProvider.DEEPL: [TranslationProvider.GOOGLE, TranslationProvider.MICROSOFT],
            TranslationProvider.GOOGLE: [TranslationProvider.MICROSOFT, TranslationProvider.AMAZON],
            TranslationProvider.MICROSOFT: [TranslationProvider.GOOGLE, TranslationProvider.AMAZON],
            TranslationProvider.AMAZON: [TranslationProvider.GOOGLE, TranslationProvider.MICROSOFT]
        }
        
        if failed_provider in fallback_chains:
            for fallback in fallback_chains[failed_provider]:
                if fallback in self.providers and self.providers[fallback].can_handle_request(request):
                    return fallback
        
        return None
    
    def _get_global_cache_key(self, request: TranslationRequest) -> str:
        """Generate global cache key"""
        text_hash = hashlib.md5(request.text.encode()).hexdigest()
        return f"global_{request.source_language}_{request.target_language}_{text_hash}_{request.quality.value}"
    
    def _update_performance_stats(self, provider: TranslationProvider, response: TranslationResponse):
        """Update provider performance statistics"""
        if provider not in self.performance_stats:
            self.performance_stats[provider] = {
                "total_requests": 0,
                "total_confidence": 0.0,
                "total_processing_time": 0.0,
                "error_count": 0
            }
        
        stats = self.performance_stats[provider]
        stats["total_requests"] += 1
        
        if response.confidence > 0:
            stats["total_confidence"] += response.confidence
            stats["total_processing_time"] += response.processing_time
        else:
            stats["error_count"] += 1
        
        # Calculate averages
        if stats["total_requests"] > 0:
            stats["avg_confidence"] = stats["total_confidence"] / (stats["total_requests"] - stats["error_count"])
            stats["avg_processing_time"] = stats["total_processing_time"] / (stats["total_requests"] - stats["error_count"])
            stats["error_rate"] = stats["error_count"] / stats["total_requests"]
    
    async def translate_batch(self, requests: List[TranslationRequest]) -> List[TranslationResponse]:
        """Translate multiple texts in batch"""
        tasks = []
        for request in requests:
            task = asyncio.create_task(self.translate(request))
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                error_response = TranslationResponse(
                    translated_text=f"[Batch Error: {str(response)}]",
                    source_language=requests[i].source_language,
                    target_language=requests[i].target_language,
                    provider=TranslationProvider.GOOGLE,
                    confidence=0.0,
                    processing_time=0.0,
                    metadata={"batch_error": str(response)}
                )
                results.append(error_response)
            else:
                results.append(response)
        
        return results
    
    def get_provider_status(self) -> Dict[TranslationProvider, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}
        
        for provider_type, provider_instance in self.providers.items():
            config = self.provider_configs[provider_type]
            stats = self.performance_stats.get(provider_type, {})
            
            status[provider_type] = {
                "enabled": config.enabled,
                "rate_limit": config.rate_limit,
                "current_requests": provider_instance.request_count,
                "cost_per_char": config.cost_per_char,
                "quality_score": config.quality_score,
                "performance_stats": stats,
                "supported_languages": len(getattr(provider_instance, 'supported_languages', [])),
                "capabilities": [cap.value for cap in config.capabilities]
            }
        
        return status
    
    def optimize_costs(self, monthly_char_limit: int) -> Dict[str, Any]:
        """Optimize provider usage for cost efficiency"""
        recommendations = {
            "current_costs": {},
            "optimized_routing": {},
            "potential_savings": 0.0
        }
        
        # Calculate current costs
        for provider_type, config in self.provider_configs.items():
            if provider_type in self.performance_stats:
                stats = self.performance_stats[provider_type]
                estimated_chars = stats.get("total_requests", 0) * 100  # Estimate
                recommendations["current_costs"][provider_type.value] = {
                    "cost_per_month": estimated_chars * config.cost_per_char * 30,
                    "chars_per_month": estimated_chars * 30
                }
        
        # Suggest optimizations
        recommendations["optimized_routing"] = {
            "basic_quality": TranslationProvider.AMAZON.value,
            "standard_quality": TranslationProvider.GOOGLE.value,
            "professional_quality": TranslationProvider.MICROSOFT.value,
            "premium_quality": TranslationProvider.DEEPL.value
        }
        
        return recommendations


# Module exports
__all__ = [
    "MultiProviderTranslationManager",
    "TranslationRequest",
    "TranslationResponse",
    "TranslationProvider",
    "TranslationQuality",
    "ProviderConfig",
    "BaseTranslationProvider",
    "GoogleTranslateProvider",
    "DeepLProvider", 
    "MicrosoftTranslatorProvider",
    "AmazonTranslateProvider"
]

logger.info("Multi-provider translation system loaded successfully")