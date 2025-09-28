"""
Multilingual SEO AI for Ainflue Platform
========================================

Advanced multilingual SEO optimization system with cultural adaptation,
cross-language semantic analysis, and localized search intent optimization.

Features:
- Multilingual keyword research and optimization
- Cultural content adaptation with AI
- Hreflang implementation and optimization
- Cross-language semantic analysis
- Localized search intent analysis
- Creator-specific multilingual strategies

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + ML Engineer + Backend Senior expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import re
import openai
# from transformers import AutoTokenizer, AutoModel, MarianMTModel, MarianTokenizer
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import pycountry
from googletrans import Translator
import langdetect
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

class LanguageCode(Enum):
    """Supported language codes."""
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
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
    DANISH = "da"
    FINNISH = "fi"

class CulturalContext(Enum):
    """Cultural context types."""
    WESTERN = "western"
    EASTERN = "eastern"
    MIDDLE_EASTERN = "middle_eastern"
    LATIN_AMERICAN = "latin_american"
    NORDIC = "nordic"
    ASIAN = "asian"
    AFRICAN = "african"

class ContentAdaptationType(Enum):
    """Content adaptation types."""
    LINGUISTIC = "linguistic"
    CULTURAL = "cultural"
    LOCALIZED = "localized"
    TRANSCREATION = "transcreation"
    TECHNICAL = "technical"

class SearchBehaviorType(Enum):
    """Search behavior patterns by region."""
    FORMAL = "formal"
    INFORMAL = "informal"
    DIRECT = "direct"
    CONTEXTUAL = "contextual"
    VISUAL_ORIENTED = "visual_oriented"
    TEXT_ORIENTED = "text_oriented"

@dataclass
class LanguageMarket:
    """Language market information."""
    language_code: LanguageCode
    country_codes: List[str]
    market_size: int
    search_volume_factor: float
    competition_level: float
    cultural_context: CulturalContext
    search_behavior: SearchBehaviorType
    preferred_content_length: int
    local_search_engines: List[str]

@dataclass
class MultilingualKeyword:
    """Multilingual keyword data."""
    original_keyword: str
    translations: Dict[str, str]
    transliterations: Dict[str, str]
    search_volumes: Dict[str, int]
    competition_levels: Dict[str, float]
    cultural_relevance: Dict[str, float]
    local_variations: Dict[str, List[str]]

@dataclass
class MultilingualKeywords:
    """Collection of multilingual keywords."""
    base_language: LanguageCode
    target_languages: List[LanguageCode]
    keyword_set: List[MultilingualKeyword]
    total_global_volume: int
    market_opportunities: Dict[str, float]
    priority_markets: List[str]

@dataclass
class CulturalAdaptation:
    """Cultural adaptation requirements."""
    target_culture: CulturalContext
    adaptation_requirements: List[str]
    content_modifications: Dict[str, str]
    visual_considerations: List[str]
    tone_adjustments: List[str]
    taboo_topics: List[str]
    preferred_formats: List[str]

@dataclass
class AdaptedContent:
    """Culturally adapted content."""
    original_content: str
    adapted_content: str
    target_language: LanguageCode
    target_culture: CulturalContext
    adaptation_type: ContentAdaptationType
    cultural_adaptations: CulturalAdaptation
    localization_score: float
    cultural_sensitivity_score: float

@dataclass
class HreflangStructure:
    """Hreflang implementation structure."""
    base_url: str
    language_versions: Dict[str, str]
    hreflang_tags: List[str]
    canonical_urls: Dict[str, str]
    sitemap_structure: Dict[str, List[str]]
    implementation_priority: List[str]
    technical_requirements: List[str]

@dataclass
class SemanticAlignment:
    """Cross-language semantic alignment."""
    concept_mappings: Dict[str, Dict[str, float]]
    semantic_gaps: List[str]
    cross_language_similarity: float
    concept_coverage: Dict[str, float]
    alignment_opportunities: List[str]

@dataclass
class LocalizedIntent:
    """Localized search intent analysis."""
    query: str
    language: LanguageCode
    region: str
    local_intent: str
    cultural_context: str
    search_behavior_pattern: SearchBehaviorType
    local_competition: float
    opportunity_score: float
    content_recommendations: List[str]

class MultilingualSEOAI:
    """Advanced multilingual SEO optimization with AI and cultural intelligence."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize multilingual SEO AI system.
        
        Args:
            config: Configuration dictionary with API keys and model settings
        """
        self.config = config or {}
        self.openai_api_key = self.config.get('openai_api_key')
        self.model_name = self.config.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        
        # Initialize translation and language models
        self.translator = None
        self.tokenizer = None
        self.model = None
        self.openai_client = None
        self.translation_models = {}
        
        # Supported languages and their characteristics
        self.language_markets = self._initialize_language_markets()
        self.cultural_mappings = self._initialize_cultural_mappings()
        
        # Caching for performance
        self._translation_cache: Dict[str, str] = {}
        self._keyword_cache: Dict[str, MultilingualKeywords] = {}
        self._adaptation_cache: Dict[str, AdaptedContent] = {}
        
        logger.info("MultilingualSEOAI initialized")

    async def initialize_models(self) -> None:
        """Initialize translation and AI models."""
        try:
            # Initialize Google Translator
            self.translator = Translator()
            
            # Initialize transformer model for semantic analysis
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # Initialize OpenAI
            if self.openai_api_key:
                openai.api_key = self.openai_api_key
                self.openai_client = openai
            
            # Initialize specialized translation models for key languages
            await self._initialize_translation_models()
            
            logger.info("Multilingual SEO models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize multilingual models: {e}")
            raise

    async def multilingual_keyword_research(self, keywords: List[str], 
                                          languages: List[str], 
                                          base_language: str = "en") -> MultilingualKeywords:
        """Research keywords across multiple languages and markets.
        
        Args:
            keywords: Base keywords for research
            languages: Target languages for expansion
            base_language: Base language of the keywords
            
        Returns:
            MultilingualKeywords with comprehensive multilingual analysis
        """
        cache_key = f"{hash(str(keywords))}_{hash(str(languages))}_{base_language}"
        if cache_key in self._keyword_cache:
            return self._keyword_cache[cache_key]
            
        if not self.translator:
            await self.initialize_models()
            
        try:
            base_lang = LanguageCode(base_language)
            target_languages = [LanguageCode(lang) for lang in languages]
            
            # Process each keyword
            multilingual_keywords = []
            for keyword in keywords:
                multilingual_keyword = await self._process_multilingual_keyword(
                    keyword, base_lang, target_languages
                )
                multilingual_keywords.append(multilingual_keyword)
            
            # Calculate market opportunities
            market_opportunities = await self._calculate_market_opportunities(
                multilingual_keywords, target_languages
            )
            
            # Identify priority markets
            priority_markets = await self._identify_priority_markets(market_opportunities)
            
            # Calculate total global volume
            total_volume = self._calculate_total_global_volume(multilingual_keywords)
            
            result = MultilingualKeywords(
                base_language=base_lang,
                target_languages=target_languages,
                keyword_set=multilingual_keywords,
                total_global_volume=total_volume,
                market_opportunities=market_opportunities,
                priority_markets=priority_markets
            )
            
            # Cache result
            self._keyword_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Multilingual keyword research failed: {e}")
            raise

    async def cultural_content_adaptation(self, content: str, culture: str, 
                                        target_language: str = "en") -> AdaptedContent:
        """Adapt content for specific cultural context.
        
        Args:
            content: Original content to adapt
            culture: Target cultural context
            target_language: Target language for adaptation
            
        Returns:
            AdaptedContent with cultural adaptations
        """
        cache_key = f"{hash(content)}_{culture}_{target_language}"
        if cache_key in self._adaptation_cache:
            return self._adaptation_cache[cache_key]
            
        try:
            target_lang = LanguageCode(target_language)
            target_culture = CulturalContext(culture)
            
            # Analyze cultural requirements
            cultural_adaptation = await self._analyze_cultural_requirements(target_culture)
            
            # Determine adaptation type needed
            adaptation_type = await self._determine_adaptation_type(content, target_culture)
            
            # Perform content adaptation
            adapted_content = await self._adapt_content_culturally(
                content, target_culture, cultural_adaptation, adaptation_type
            )
            
            # Translate if needed
            if target_language != "en":
                adapted_content = await self._translate_content(adapted_content, target_language)
            
            # Calculate adaptation scores
            localization_score = await self._calculate_localization_score(
                content, adapted_content, target_culture
            )
            cultural_sensitivity_score = await self._calculate_cultural_sensitivity_score(
                adapted_content, target_culture
            )
            
            result = AdaptedContent(
                original_content=content,
                adapted_content=adapted_content,
                target_language=target_lang,
                target_culture=target_culture,
                adaptation_type=adaptation_type,
                cultural_adaptations=cultural_adaptation,
                localization_score=localization_score,
                cultural_sensitivity_score=cultural_sensitivity_score
            )
            
            # Cache result
            self._adaptation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Cultural content adaptation failed: {e}")
            raise

    async def hreflang_optimization(self, content_map: Dict[str, str], 
                                  base_domain: str) -> HreflangStructure:
        """Optimize hreflang implementation for multilingual content.
        
        Args:
            content_map: Mapping of language codes to content URLs
            base_domain: Base domain for the website
            
        Returns:
            HreflangStructure with implementation guidelines
        """
        try:
            # Generate hreflang tags
            hreflang_tags = await self._generate_hreflang_tags(content_map, base_domain)
            
            # Determine canonical URLs
            canonical_urls = await self._determine_canonical_urls(content_map)
            
            # Create sitemap structure
            sitemap_structure = await self._create_multilingual_sitemap_structure(content_map)
            
            # Prioritize implementation
            implementation_priority = await self._prioritize_hreflang_implementation(content_map)
            
            # Generate technical requirements
            technical_requirements = await self._generate_hreflang_technical_requirements()
            
            return HreflangStructure(
                base_url=base_domain,
                language_versions=content_map,
                hreflang_tags=hreflang_tags,
                canonical_urls=canonical_urls,
                sitemap_structure=sitemap_structure,
                implementation_priority=implementation_priority,
                technical_requirements=technical_requirements
            )
            
        except Exception as e:
            logger.error(f"Hreflang optimization failed: {e}")
            raise

    async def cross_language_semantic_analysis(self, content: Dict[str, str]) -> SemanticAlignment:
        """Analyze semantic alignment across languages.
        
        Args:
            content: Dictionary mapping language codes to content
            
        Returns:
            SemanticAlignment with cross-language analysis
        """
        try:
            if not self.model:
                await self.initialize_models()
            
            # Generate embeddings for each language version
            language_embeddings = {}
            for lang_code, text in content.items():
                embedding = await self._generate_multilingual_embeddings(text, lang_code)
                language_embeddings[lang_code] = embedding
            
            # Calculate concept mappings
            concept_mappings = await self._calculate_concept_mappings(language_embeddings)
            
            # Identify semantic gaps
            semantic_gaps = await self._identify_semantic_gaps(concept_mappings)
            
            # Calculate cross-language similarity
            cross_language_similarity = await self._calculate_cross_language_similarity(
                language_embeddings
            )
            
            # Calculate concept coverage
            concept_coverage = await self._calculate_concept_coverage(concept_mappings)
            
            # Identify alignment opportunities
            alignment_opportunities = await self._identify_alignment_opportunities(
                semantic_gaps, concept_coverage
            )
            
            return SemanticAlignment(
                concept_mappings=concept_mappings,
                semantic_gaps=semantic_gaps,
                cross_language_similarity=cross_language_similarity,
                concept_coverage=concept_coverage,
                alignment_opportunities=alignment_opportunities
            )
            
        except Exception as e:
            logger.error(f"Cross-language semantic analysis failed: {e}")
            raise

    async def localized_search_intent_analysis(self, query: str, region: str, 
                                             language: str = "en") -> LocalizedIntent:
        """Analyze search intent in specific localized context.
        
        Args:
            query: Search query to analyze
            region: Target region/country
            language: Language of the query
            
        Returns:
            LocalizedIntent with localized analysis
        """
        try:
            lang_code = LanguageCode(language)
            
            # Analyze local intent
            local_intent = await self._analyze_local_intent(query, region, lang_code)
            
            # Determine cultural context
            cultural_context = await self._determine_cultural_context(region)
            
            # Analyze search behavior pattern
            search_behavior = await self._analyze_search_behavior_pattern(query, region)
            
            # Calculate local competition
            local_competition = await self._calculate_local_competition(query, region)
            
            # Calculate opportunity score
            opportunity_score = await self._calculate_localized_opportunity_score(
                query, region, local_competition
            )
            
            # Generate content recommendations
            content_recommendations = await self._generate_localized_content_recommendations(
                query, region, cultural_context
            )
            
            return LocalizedIntent(
                query=query,
                language=lang_code,
                region=region,
                local_intent=local_intent,
                cultural_context=cultural_context,
                search_behavior_pattern=search_behavior,
                local_competition=local_competition,
                opportunity_score=opportunity_score,
                content_recommendations=content_recommendations
            )
            
        except Exception as e:
            logger.error(f"Localized search intent analysis failed: {e}")
            raise

    # Private helper methods

    def _initialize_language_markets(self) -> Dict[LanguageCode, LanguageMarket]:
        """Initialize language market data."""
        return {
            LanguageCode.ENGLISH: LanguageMarket(
                language_code=LanguageCode.ENGLISH,
                country_codes=["US", "GB", "CA", "AU", "NZ"],
                market_size=1500000000,
                search_volume_factor=1.0,
                competition_level=0.9,
                cultural_context=CulturalContext.WESTERN,
                search_behavior=SearchBehaviorType.DIRECT,
                preferred_content_length=1500,
                local_search_engines=["Google", "Bing", "DuckDuckGo"]
            ),
            LanguageCode.SPANISH: LanguageMarket(
                language_code=LanguageCode.SPANISH,
                country_codes=["ES", "MX", "AR", "CO", "PE"],
                market_size=500000000,
                search_volume_factor=0.7,
                competition_level=0.6,
                cultural_context=CulturalContext.LATIN_AMERICAN,
                search_behavior=SearchBehaviorType.CONTEXTUAL,
                preferred_content_length=1200,
                local_search_engines=["Google", "Yahoo"]
            ),
            LanguageCode.FRENCH: LanguageMarket(
                language_code=LanguageCode.FRENCH,
                country_codes=["FR", "CA", "BE", "CH"],
                market_size=280000000,
                search_volume_factor=0.6,
                competition_level=0.7,
                cultural_context=CulturalContext.WESTERN,
                search_behavior=SearchBehaviorType.FORMAL,
                preferred_content_length=1400,
                local_search_engines=["Google", "Bing", "Qwant"]
            ),
            LanguageCode.GERMAN: LanguageMarket(
                language_code=LanguageCode.GERMAN,
                country_codes=["DE", "AT", "CH"],
                market_size=100000000,
                search_volume_factor=0.8,
                competition_level=0.8,
                cultural_context=CulturalContext.WESTERN,
                search_behavior=SearchBehaviorType.FORMAL,
                preferred_content_length=1600,
                local_search_engines=["Google", "Bing"]
            ),
            LanguageCode.CHINESE_SIMPLIFIED: LanguageMarket(
                language_code=LanguageCode.CHINESE_SIMPLIFIED,
                country_codes=["CN"],
                market_size=900000000,
                search_volume_factor=1.2,
                competition_level=0.9,
                cultural_context=CulturalContext.ASIAN,
                search_behavior=SearchBehaviorType.VISUAL_ORIENTED,
                preferred_content_length=800,
                local_search_engines=["Baidu", "Sogou", "360 Search"]
            ),
            LanguageCode.JAPANESE: LanguageMarket(
                language_code=LanguageCode.JAPANESE,
                country_codes=["JP"],
                market_size=125000000,
                search_volume_factor=0.9,
                competition_level=0.8,
                cultural_context=CulturalContext.ASIAN,
                search_behavior=SearchBehaviorType.FORMAL,
                preferred_content_length=1000,
                local_search_engines=["Google", "Yahoo Japan"]
            ),
            LanguageCode.ARABIC: LanguageMarket(
                language_code=LanguageCode.ARABIC,
                country_codes=["SA", "AE", "EG", "MA"],
                market_size=400000000,
                search_volume_factor=0.5,
                competition_level=0.5,
                cultural_context=CulturalContext.MIDDLE_EASTERN,
                search_behavior=SearchBehaviorType.CONTEXTUAL,
                preferred_content_length=1200,
                local_search_engines=["Google", "Bing"]
            )
        }

    def _initialize_cultural_mappings(self) -> Dict[CulturalContext, Dict[str, Any]]:
        """Initialize cultural context mappings."""
        return {
            CulturalContext.WESTERN: {
                'direct_communication': True,
                'individualistic': True,
                'time_sensitive': True,
                'formal_distance': 'low',
                'visual_preferences': ['clean', 'minimal', 'professional'],
                'content_tone': 'direct',
                'taboo_topics': ['politics', 'religion'],
                'preferred_formats': ['articles', 'lists', 'how-to']
            },
            CulturalContext.ASIAN: {
                'direct_communication': False,
                'individualistic': False,
                'time_sensitive': False,
                'formal_distance': 'high',
                'visual_preferences': ['detailed', 'colorful', 'hierarchical'],
                'content_tone': 'respectful',
                'taboo_topics': ['politics', 'personal_criticism'],
                'preferred_formats': ['detailed_guides', 'step-by-step', 'visual']
            },
            CulturalContext.MIDDLE_EASTERN: {
                'direct_communication': False,
                'individualistic': False,
                'time_sensitive': False,
                'formal_distance': 'high',
                'visual_preferences': ['traditional', 'respectful', 'family-oriented'],
                'content_tone': 'respectful',
                'taboo_topics': ['religion_criticism', 'alcohol', 'inappropriate_imagery'],
                'preferred_formats': ['informative', 'family-focused', 'traditional']
            },
            CulturalContext.LATIN_AMERICAN: {
                'direct_communication': True,
                'individualistic': False,
                'time_sensitive': False,
                'formal_distance': 'medium',
                'visual_preferences': ['vibrant', 'family-oriented', 'community-focused'],
                'content_tone': 'warm',
                'taboo_topics': ['politics'],
                'preferred_formats': ['community-focused', 'family-oriented', 'social']
            }
        }

    async def _initialize_translation_models(self) -> None:
        """Initialize specialized translation models for key languages."""
        try:
            # Initialize key translation pairs
            key_pairs = [
                ("en", "es"), ("en", "fr"), ("en", "de"), 
                ("en", "zh"), ("en", "ja"), ("en", "ar")
            ]
            
            for source, target in key_pairs:
                try:
                    model_name = f"Helsinki-NLP/opus-mt-{source}-{target}"
                    tokenizer = MarianTokenizer.from_pretrained(model_name)
                    model = MarianMTModel.from_pretrained(model_name)
                    
                    self.translation_models[f"{source}-{target}"] = {
                        'tokenizer': tokenizer,
                        'model': model
                    }
                except Exception as e:
                    logger.warning(f"Could not load translation model {source}-{target}: {e}")
                    
        except Exception as e:
            logger.warning(f"Translation model initialization failed: {e}")

    async def _process_multilingual_keyword(self, keyword: str, base_lang: LanguageCode, 
                                          target_languages: List[LanguageCode]) -> MultilingualKeyword:
        """Process a single keyword for multilingual optimization."""
        try:
            translations = {}
            transliterations = {}
            search_volumes = {}
            competition_levels = {}
            cultural_relevance = {}
            local_variations = {}
            
            for target_lang in target_languages:
                # Translate keyword
                translation = await self._translate_keyword(keyword, base_lang.value, target_lang.value)
                translations[target_lang.value] = translation
                
                # Generate transliteration if needed
                transliteration = await self._transliterate_keyword(translation, target_lang.value)
                if transliteration != translation:
                    transliterations[target_lang.value] = transliteration
                
                # Estimate search volume
                search_volume = await self._estimate_multilingual_search_volume(
                    translation, target_lang.value
                )
                search_volumes[target_lang.value] = search_volume
                
                # Calculate competition level
                competition = await self._calculate_multilingual_competition(
                    translation, target_lang.value
                )
                competition_levels[target_lang.value] = competition
                
                # Assess cultural relevance
                cultural_rel = await self._assess_cultural_relevance(
                    translation, target_lang.value
                )
                cultural_relevance[target_lang.value] = cultural_rel
                
                # Generate local variations
                variations = await self._generate_local_variations(
                    translation, target_lang.value
                )
                local_variations[target_lang.value] = variations
            
            return MultilingualKeyword(
                original_keyword=keyword,
                translations=translations,
                transliterations=transliterations,
                search_volumes=search_volumes,
                competition_levels=competition_levels,
                cultural_relevance=cultural_relevance,
                local_variations=local_variations
            )
            
        except Exception as e:
            logger.error(f"Multilingual keyword processing failed: {e}")
            return MultilingualKeyword(keyword, {}, {}, {}, {}, {}, {})

    async def _translate_keyword(self, keyword: str, source_lang: str, target_lang: str) -> str:
        """Translate keyword using best available method."""
        cache_key = f"{keyword}_{source_lang}_{target_lang}"
        if cache_key in self._translation_cache:
            return self._translation_cache[cache_key]
            
        try:
            # Try specialized translation model first
            model_key = f"{source_lang}-{target_lang}"
            if model_key in self.translation_models:
                translation = await self._translate_with_marian(
                    keyword, self.translation_models[model_key]
                )
                if translation:
                    self._translation_cache[cache_key] = translation
                    return translation
            
            # Fallback to Google Translate
            if self.translator:
                try:
                    result = self.translator.translate(keyword, src=source_lang, dest=target_lang)
                    translation = result.text
                    self._translation_cache[cache_key] = translation
                    return translation
                except Exception as e:
                    logger.warning(f"Google Translate failed: {e}")
            
            # Ultimate fallback
            return keyword
            
        except Exception as e:
            logger.error(f"Keyword translation failed: {e}")
            return keyword

    async def _translate_with_marian(self, text: str, model_dict: Dict) -> Optional[str]:
        """Translate using Marian model."""
        try:
            tokenizer = model_dict['tokenizer']
            model = model_dict['model']
            
            inputs = tokenizer(text, return_tensors="pt")
            translated = model.generate(**inputs)
            translation = tokenizer.decode(translated[0], skip_special_tokens=True)
            
            return translation
            
        except Exception as e:
            logger.warning(f"Marian translation failed: {e}")
            return None

    async def _transliterate_keyword(self, keyword: str, target_lang: str) -> str:
        """Transliterate keyword for languages requiring it."""
        # Simplified transliteration - in production use specialized libraries
        if target_lang in ['ar', 'zh', 'ja', 'ko', 'hi']:
            # For languages with different scripts, transliteration might be needed
            # This is a placeholder - implement actual transliteration logic
            return keyword
        
        return keyword

    async def _estimate_multilingual_search_volume(self, keyword: str, language: str) -> int:
        """Estimate search volume for keyword in specific language."""
        try:
            # Get market data for language
            lang_code = LanguageCode(language)
            market_data = self.language_markets.get(lang_code)
            
            if not market_data:
                return 1000  # Default estimate
            
            # Base volume estimate (simplified)
            base_volume = len(keyword.split()) * 500
            
            # Apply market factor
            market_volume = int(base_volume * market_data.search_volume_factor)
            
            # Apply keyword length factor
            length_factor = max(0.5, 1 - (len(keyword.split()) - 2) * 0.1)
            
            final_volume = int(market_volume * length_factor)
            
            return max(final_volume, 10)
            
        except Exception:
            return 1000

    async def _calculate_multilingual_competition(self, keyword: str, language: str) -> float:
        """Calculate competition level for keyword in specific language."""
        try:
            # Get market data
            lang_code = LanguageCode(language)
            market_data = self.language_markets.get(lang_code)
            
            if not market_data:
                return 0.5  # Default competition
            
            # Base competition from market
            base_competition = market_data.competition_level
            
            # Adjust for keyword characteristics
            word_count = len(keyword.split())
            if word_count >= 3:
                competition_adjustment = -0.2  # Long-tail keywords have lower competition
            elif word_count == 1:
                competition_adjustment = 0.2   # Single words have higher competition
            else:
                competition_adjustment = 0.0
            
            final_competition = max(0.0, min(1.0, base_competition + competition_adjustment))
            
            return final_competition
            
        except Exception:
            return 0.5

    async def _assess_cultural_relevance(self, keyword: str, language: str) -> float:
        """Assess cultural relevance of keyword in target market."""
        try:
            # Get cultural context for language
            lang_code = LanguageCode(language)
            market_data = self.language_markets.get(lang_code)
            
            if not market_data:
                return 0.5
            
            cultural_context = market_data.cultural_context
            cultural_data = self.cultural_mappings.get(cultural_context, {})
            
            # Check for taboo topics
            taboo_topics = cultural_data.get('taboo_topics', [])
            keyword_lower = keyword.lower()
            
            for taboo in taboo_topics:
                if taboo in keyword_lower:
                    return 0.1  # Very low relevance for taboo topics
            
            # Base relevance
            relevance = 0.7
            
            # Adjust based on cultural preferences
            if cultural_data.get('direct_communication', True):
                if any(word in keyword_lower for word in ['how', 'what', 'guide']):
                    relevance += 0.2
            else:
                if any(word in keyword_lower for word in ['respectful', 'traditional']):
                    relevance += 0.2
            
            return min(1.0, relevance)
            
        except Exception:
            return 0.5

    async def _generate_local_variations(self, keyword: str, language: str) -> List[str]:
        """Generate local variations of keyword."""
        variations = []
        
        try:
            # Get language market data
            lang_code = LanguageCode(language)
            market_data = self.language_markets.get(lang_code)
            
            if not market_data:
                return [keyword]
            
            # Generate country-specific variations
            for country_code in market_data.country_codes:
                country_name = self._get_country_name(country_code, language)
                if country_name:
                    variations.extend([
                        f"{keyword} {country_name}",
                        f"{keyword} in {country_name}",
                        f"{country_name} {keyword}"
                    ])
            
            # Add formal/informal variations based on cultural context
            cultural_context = market_data.cultural_context
            cultural_data = self.cultural_mappings.get(cultural_context, {})
            
            if cultural_data.get('formal_distance') == 'high':
                # Add more formal variations
                variations.extend([
                    f"professional {keyword}",
                    f"official {keyword}",
                    f"formal {keyword}"
                ])
            else:
                # Add more casual variations
                variations.extend([
                    f"best {keyword}",
                    f"top {keyword}",
                    f"popular {keyword}"
                ])
            
            return variations[:10]  # Limit variations
            
        except Exception:
            return [keyword]

    def _get_country_name(self, country_code: str, language: str) -> Optional[str]:
        """Get country name in target language."""
        try:
            country = pycountry.countries.get(alpha_2=country_code)
            if country:
                # In production, translate country name to target language
                return country.name
            return None
        except Exception:
            return None

    async def _calculate_market_opportunities(self, keywords: List[MultilingualKeyword], 
                                            languages: List[LanguageCode]) -> Dict[str, float]:
        """Calculate market opportunities for each language."""
        opportunities = {}
        
        for lang in languages:
            lang_code = lang.value
            total_volume = 0
            avg_competition = 0
            avg_relevance = 0
            
            for keyword in keywords:
                total_volume += keyword.search_volumes.get(lang_code, 0)
                avg_competition += keyword.competition_levels.get(lang_code, 0.5)
                avg_relevance += keyword.cultural_relevance.get(lang_code, 0.5)
            
            if keywords:
                avg_competition /= len(keywords)
                avg_relevance /= len(keywords)
            
            # Calculate opportunity score
            # High volume + low competition + high relevance = high opportunity
            volume_score = min(total_volume / 50000, 1.0)  # Normalize volume
            competition_score = 1 - avg_competition  # Invert competition
            relevance_score = avg_relevance
            
            opportunity_score = (volume_score * 0.4 + competition_score * 0.3 + relevance_score * 0.3)
            opportunities[lang_code] = opportunity_score
        
        return opportunities

    async def _identify_priority_markets(self, opportunities: Dict[str, float]) -> List[str]:
        """Identify priority markets based on opportunities."""
        # Sort by opportunity score
        sorted_markets = sorted(opportunities.items(), key=lambda x: x[1], reverse=True)
        
        # Return top markets with score > 0.6
        priority_markets = [market for market, score in sorted_markets if score > 0.6]
        
        return priority_markets[:5]  # Limit to top 5

    def _calculate_total_global_volume(self, keywords: List[MultilingualKeyword]) -> int:
        """Calculate total global search volume."""
        total_volume = 0
        
        for keyword in keywords:
            # Sum volumes across all languages
            keyword_total = sum(keyword.search_volumes.values())
            total_volume += keyword_total
        
        return total_volume

    # Cultural adaptation methods
    async def _analyze_cultural_requirements(self, culture: CulturalContext) -> CulturalAdaptation:
        """Analyze cultural adaptation requirements."""
        cultural_data = self.cultural_mappings.get(culture, {})
        
        adaptation_requirements = []
        content_modifications = {}
        visual_considerations = []
        tone_adjustments = []
        
        # Communication style adaptations
        if not cultural_data.get('direct_communication', True):
            adaptation_requirements.append("Use indirect communication style")
            tone_adjustments.append("Soften direct statements")
            content_modifications['communication_style'] = 'indirect'
        
        # Formality level
        formal_distance = cultural_data.get('formal_distance', 'medium')
        if formal_distance == 'high':
            adaptation_requirements.append("Use formal language and respectful tone")
            tone_adjustments.append("Increase formality level")
            content_modifications['formality'] = 'high'
        
        # Visual preferences
        visual_prefs = cultural_data.get('visual_preferences', [])
        visual_considerations.extend(visual_prefs)
        
        # Content tone
        preferred_tone = cultural_data.get('content_tone', 'neutral')
        tone_adjustments.append(f"Adapt to {preferred_tone} tone")
        
        return CulturalAdaptation(
            target_culture=culture,
            adaptation_requirements=adaptation_requirements,
            content_modifications=content_modifications,
            visual_considerations=visual_considerations,
            tone_adjustments=tone_adjustments,
            taboo_topics=cultural_data.get('taboo_topics', []),
            preferred_formats=cultural_data.get('preferred_formats', [])
        )

    async def _determine_adaptation_type(self, content: str, culture: CulturalContext) -> ContentAdaptationType:
        """Determine the type of adaptation needed."""
        cultural_data = self.cultural_mappings.get(culture, {})
        
        # Check if deep cultural adaptation is needed
        taboo_topics = cultural_data.get('taboo_topics', [])
        content_lower = content.lower()
        
        has_taboo = any(topic in content_lower for topic in taboo_topics)
        
        if has_taboo:
            return ContentAdaptationType.TRANSCREATION
        
        # Check communication style mismatch
        is_direct_content = any(indicator in content_lower 
                               for indicator in ['you should', 'must', 'directly', 'simply'])
        cultural_is_direct = cultural_data.get('direct_communication', True)
        
        if is_direct_content and not cultural_is_direct:
            return ContentAdaptationType.CULTURAL
        
        # Check formality mismatch
        is_informal_content = any(indicator in content_lower 
                                 for indicator in ['hey', 'guys', 'awesome', 'cool'])
        required_formality = cultural_data.get('formal_distance', 'medium')
        
        if is_informal_content and required_formality == 'high':
            return ContentAdaptationType.CULTURAL
        
        # Default to localized adaptation
        return ContentAdaptationType.LOCALIZED

    async def _adapt_content_culturally(self, content: str, culture: CulturalContext, 
                                      cultural_adaptation: CulturalAdaptation, 
                                      adaptation_type: ContentAdaptationType) -> str:
        """Adapt content for cultural context."""
        try:
            adapted_content = content
            
            if adaptation_type == ContentAdaptationType.TRANSCREATION:
                # Major content rewrite needed
                adapted_content = await self._transcreate_content(content, culture)
            
            elif adaptation_type == ContentAdaptationType.CULTURAL:
                # Moderate cultural adjustments
                adapted_content = await self._apply_cultural_adjustments(content, cultural_adaptation)
            
            elif adaptation_type == ContentAdaptationType.LOCALIZED:
                # Minor localization adjustments
                adapted_content = await self._apply_localization_adjustments(content, cultural_adaptation)
            
            return adapted_content
            
        except Exception as e:
            logger.error(f"Cultural content adaptation failed: {e}")
            return content

    async def _transcreate_content(self, content: str, culture: CulturalContext) -> str:
        """Transcreate content for major cultural differences."""
        try:
            if self.openai_client:
                cultural_context = self.cultural_mappings.get(culture, {})
                
                prompt = f"""Transcreate the following content for {culture.value} cultural context:

Cultural considerations:
- Communication style: {'indirect' if not cultural_context.get('direct_communication', True) else 'direct'}
- Formality level: {cultural_context.get('formal_distance', 'medium')}
- Tone: {cultural_context.get('content_tone', 'neutral')}
- Avoid topics: {', '.join(cultural_context.get('taboo_topics', []))}

Original content:
{content}

Transcreated content:"""

                response = await self.openai_client.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=len(content.split()) * 2,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
            
            return content
            
        except Exception as e:
            logger.error(f"Content transcreation failed: {e}")
            return content

    async def _apply_cultural_adjustments(self, content: str, 
                                        adaptation: CulturalAdaptation) -> str:
        """Apply cultural adjustments to content."""
        adjusted_content = content
        
        # Apply tone adjustments
        for adjustment in adaptation.tone_adjustments:
            if 'formal' in adjustment.lower():
                # Make content more formal
                adjusted_content = re.sub(r'\byou\b', 'you (formal)', adjusted_content, flags=re.IGNORECASE)
                adjusted_content = re.sub(r'\bawesome\b', 'excellent', adjusted_content, flags=re.IGNORECASE)
                adjusted_content = re.sub(r'\bcool\b', 'impressive', adjusted_content, flags=re.IGNORECASE)
            
            elif 'indirect' in adjustment.lower():
                # Make communication more indirect
                adjusted_content = re.sub(r'\byou should\b', 'it might be beneficial to', adjusted_content, flags=re.IGNORECASE)
                adjusted_content = re.sub(r'\bmust\b', 'it is recommended to', adjusted_content, flags=re.IGNORECASE)
        
        return adjusted_content

    async def _apply_localization_adjustments(self, content: str, 
                                            adaptation: CulturalAdaptation) -> str:
        """Apply minor localization adjustments."""
        # Minor adjustments for localization
        localized_content = content
        
        # Add cultural sensitivity where needed
        if adaptation.target_culture == CulturalContext.MIDDLE_EASTERN:
            # Ensure family-friendly language
            localized_content = re.sub(r'\balcohol\b', 'beverages', localized_content, flags=re.IGNORECASE)
        
        return localized_content

    async def _translate_content(self, content: str, target_language: str) -> str:
        """Translate content to target language."""
        try:
            if self.translator:
                # Split content into chunks for better translation
                chunks = self._split_content_for_translation(content)
                translated_chunks = []
                
                for chunk in chunks:
                    result = self.translator.translate(chunk, dest=target_language)
                    translated_chunks.append(result.text)
                
                return ' '.join(translated_chunks)
            
            return content
            
        except Exception as e:
            logger.error(f"Content translation failed: {e}")
            return content

    def _split_content_for_translation(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        """Split content into chunks for translation."""
        sentences = re.split(r'[.!?]+', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    async def _calculate_localization_score(self, original: str, adapted: str, 
                                          culture: CulturalContext) -> float:
        """Calculate localization quality score."""
        try:
            # Compare adaptation depth
            adaptation_ratio = len(adapted) / max(len(original), 1)
            
            # Check cultural appropriateness
            cultural_data = self.cultural_mappings.get(culture, {})
            taboo_topics = cultural_data.get('taboo_topics', [])
            
            # Penalty for taboo topics
            taboo_penalty = 0
            adapted_lower = adapted.lower()
            for taboo in taboo_topics:
                if taboo in adapted_lower:
                    taboo_penalty += 0.2
            
            # Base score
            base_score = 0.8
            
            # Adjust for adaptation completeness
            if 0.8 <= adaptation_ratio <= 1.2:
                adaptation_score = 0.1
            else:
                adaptation_score = 0.0
            
            final_score = max(0.0, base_score + adaptation_score - taboo_penalty)
            
            return min(1.0, final_score)
            
        except Exception:
            return 0.5

    async def _calculate_cultural_sensitivity_score(self, content: str, 
                                                  culture: CulturalContext) -> float:
        """Calculate cultural sensitivity score."""
        try:
            cultural_data = self.cultural_mappings.get(culture, {})
            score = 0.7  # Base score
            
            # Check communication style appropriateness
            direct_communication = cultural_data.get('direct_communication', True)
            content_lower = content.lower()
            
            if direct_communication:
                # Direct communication preferred
                if any(indicator in content_lower for indicator in ['clearly', 'directly', 'simply']):
                    score += 0.1
            else:
                # Indirect communication preferred
                if any(indicator in content_lower for indicator in ['perhaps', 'might', 'could']):
                    score += 0.1
            
            # Check formality level
            formal_distance = cultural_data.get('formal_distance', 'medium')
            if formal_distance == 'high':
                if any(indicator in content_lower for indicator in ['respectfully', 'honored', 'pleased']):
                    score += 0.1
                if any(indicator in content_lower for indicator in ['hey', 'guys', 'awesome']):
                    score -= 0.2
            
            # Check for taboo topics
            taboo_topics = cultural_data.get('taboo_topics', [])
            for taboo in taboo_topics:
                if taboo in content_lower:
                    score -= 0.3
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5

    # Hreflang optimization methods
    async def _generate_hreflang_tags(self, content_map: Dict[str, str], 
                                    base_domain: str) -> List[str]:
        """Generate hreflang tags for multilingual content."""
        hreflang_tags = []
        
        for lang_code, url in content_map.items():
            # Generate proper hreflang format
            if url.startswith('http'):
                full_url = url
            else:
                full_url = f"https://{base_domain}{url}"
            
            # Handle language-country combinations
            if '-' in lang_code:
                hreflang_code = lang_code.lower()
            else:
                hreflang_code = lang_code.lower()
            
            hreflang_tag = f'<link rel="alternate" hreflang="{hreflang_code}" href="{full_url}" />'
            hreflang_tags.append(hreflang_tag)
        
        # Add x-default if English exists
        if 'en' in content_map:
            default_url = content_map['en']
            if not default_url.startswith('http'):
                default_url = f"https://{base_domain}{default_url}"
            
            x_default_tag = f'<link rel="alternate" hreflang="x-default" href="{default_url}" />'
            hreflang_tags.append(x_default_tag)
        
        return hreflang_tags

    async def _determine_canonical_urls(self, content_map: Dict[str, str]) -> Dict[str, str]:
        """Determine canonical URLs for each language version."""
        canonical_urls = {}
        
        for lang_code, url in content_map.items():
            # Each language version should be canonical for itself
            canonical_urls[lang_code] = url
        
        return canonical_urls

    async def _create_multilingual_sitemap_structure(self, content_map: Dict[str, str]) -> Dict[str, List[str]]:
        """Create sitemap structure for multilingual content."""
        sitemap_structure = {
            'main_sitemap': ['sitemap-index.xml'],
            'language_sitemaps': []
        }
        
        for lang_code in content_map.keys():
            lang_sitemap = f"sitemap-{lang_code}.xml"
            sitemap_structure['language_sitemaps'].append(lang_sitemap)
        
        return sitemap_structure

    async def _prioritize_hreflang_implementation(self, content_map: Dict[str, str]) -> List[str]:
        """Prioritize hreflang implementation steps."""
        return [
            "Implement hreflang tags on all pages",
            "Add language sitemaps",
            "Set up proper URL structure",
            "Configure server-side language detection",
            "Test hreflang implementation",
            "Monitor in Google Search Console"
        ]

    async def _generate_hreflang_technical_requirements(self) -> List[str]:
        """Generate technical requirements for hreflang implementation."""
        return [
            "Bidirectional hreflang tags (each page must reference all others)",
            "Consistent URL structure across languages",
            "Proper language code format (ISO 639-1)",
            "Self-referencing hreflang tags",
            "X-default implementation for global users",
            "Sitemap integration with hreflang annotations",
            "Server response header configuration",
            "CDN configuration for language-specific content delivery"
        ]

    # Cross-language semantic analysis methods
    async def _generate_multilingual_embeddings(self, text: str, language: str) -> np.ndarray:
        """Generate embeddings for multilingual content."""
        try:
            if not self.model or not self.tokenizer:
                await self.initialize_models()
            
            # Preprocess text for the specific language
            processed_text = await self._preprocess_multilingual_text(text, language)
            
            # Generate embeddings
            inputs = self.tokenizer(processed_text, return_tensors='pt', 
                                  truncation=True, padding=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Multilingual embedding generation failed: {e}")
            return np.zeros(384)

    async def _preprocess_multilingual_text(self, text: str, language: str) -> str:
        """Preprocess text for specific language characteristics."""
        # Basic preprocessing - can be enhanced for specific languages
        processed_text = text.strip()
        
        # Language-specific preprocessing
        if language in ['zh', 'ja']:
            # For CJK languages, might need special tokenization
            pass
        elif language == 'ar':
            # For Arabic, might need RTL handling
            pass
        
        return processed_text

    async def _calculate_concept_mappings(self, embeddings: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
        """Calculate concept mappings across languages."""
        concept_mappings = {}
        
        language_codes = list(embeddings.keys())
        
        for i, lang1 in enumerate(language_codes):
            concept_mappings[lang1] = {}
            
            for j, lang2 in enumerate(language_codes):
                if i != j:
                    # Calculate cosine similarity between language embeddings
                    similarity = cosine_similarity(
                        embeddings[lang1].reshape(1, -1),
                        embeddings[lang2].reshape(1, -1)
                    )[0][0]
                    
                    concept_mappings[lang1][lang2] = float(similarity)
        
        return concept_mappings

    async def _identify_semantic_gaps(self, concept_mappings: Dict[str, Dict[str, float]]) -> List[str]:
        """Identify semantic gaps across languages."""
        gaps = []
        
        for lang1, mappings in concept_mappings.items():
            for lang2, similarity in mappings.items():
                if similarity < 0.6:  # Low similarity threshold
                    gaps.append(f"Semantic gap between {lang1} and {lang2}: {similarity:.2f}")
        
        return gaps

    async def _calculate_cross_language_similarity(self, embeddings: Dict[str, np.ndarray]) -> float:
        """Calculate overall cross-language similarity."""
        similarities = []
        
        language_codes = list(embeddings.keys())
        
        for i, lang1 in enumerate(language_codes):
            for j, lang2 in enumerate(language_codes[i+1:], i+1):
                similarity = cosine_similarity(
                    embeddings[lang1].reshape(1, -1),
                    embeddings[lang2].reshape(1, -1)
                )[0][0]
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0

    async def _calculate_concept_coverage(self, concept_mappings: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate concept coverage for each language."""
        coverage = {}
        
        for lang, mappings in concept_mappings.items():
            if mappings:
                avg_similarity = np.mean(list(mappings.values()))
                coverage[lang] = avg_similarity
            else:
                coverage[lang] = 0.0
        
        return coverage

    async def _identify_alignment_opportunities(self, gaps: List[str], 
                                             coverage: Dict[str, float]) -> List[str]:
        """Identify opportunities for semantic alignment improvement."""
        opportunities = []
        
        # Based on gaps
        if len(gaps) > 5:
            opportunities.append("Improve content consistency across languages")
        
        # Based on coverage
        low_coverage_languages = [lang for lang, score in coverage.items() if score < 0.6]
        if low_coverage_languages:
            opportunities.append(f"Enhance semantic alignment for: {', '.join(low_coverage_languages)}")
        
        # General opportunities
        opportunities.extend([
            "Implement cross-language content review process",
            "Use consistent terminology across languages",
            "Develop multilingual style guide"
        ])
        
        return opportunities

    # Localized search intent analysis methods
    async def _analyze_local_intent(self, query: str, region: str, language: LanguageCode) -> str:
        """Analyze local search intent."""
        try:
            query_lower = query.lower()
            
            # Local intent indicators
            local_indicators = ['near', 'local', 'nearby', 'in', 'at', region.lower()]
            
            if any(indicator in query_lower for indicator in local_indicators):
                return "local_business"
            
            # Informational intent
            info_indicators = ['what', 'how', 'why', 'when', 'where']
            if any(indicator in query_lower for indicator in info_indicators):
                return "informational"
            
            # Transactional intent
            trans_indicators = ['buy', 'purchase', 'order', 'book', 'reserve']
            if any(indicator in query_lower for indicator in trans_indicators):
                return "transactional"
            
            # Commercial intent
            commercial_indicators = ['best', 'top', 'review', 'compare', 'vs']
            if any(indicator in query_lower for indicator in commercial_indicators):
                return "commercial"
            
            return "general"
            
        except Exception:
            return "general"

    async def _determine_cultural_context(self, region: str) -> str:
        """Determine cultural context for region."""
        # Mapping of regions to cultural contexts
        region_culture_map = {
            'US': 'western', 'GB': 'western', 'CA': 'western', 'AU': 'western',
            'DE': 'western', 'FR': 'western', 'ES': 'western', 'IT': 'western',
            'CN': 'asian', 'JP': 'asian', 'KR': 'asian', 'TH': 'asian',
            'SA': 'middle_eastern', 'AE': 'middle_eastern', 'EG': 'middle_eastern',
            'MX': 'latin_american', 'BR': 'latin_american', 'AR': 'latin_american',
            'SE': 'nordic', 'NO': 'nordic', 'DK': 'nordic', 'FI': 'nordic'
        }
        
        return region_culture_map.get(region.upper(), 'western')

    async def _analyze_search_behavior_pattern(self, query: str, region: str) -> SearchBehaviorType:
        """Analyze search behavior pattern for region."""
        # Regional search behavior patterns
        region_behavior_map = {
            'DE': SearchBehaviorType.FORMAL,
            'JP': SearchBehaviorType.FORMAL,
            'CN': SearchBehaviorType.VISUAL_ORIENTED,
            'US': SearchBehaviorType.DIRECT,
            'GB': SearchBehaviorType.DIRECT,
            'FR': SearchBehaviorType.CONTEXTUAL,
            'ES': SearchBehaviorType.CONTEXTUAL,
            'AR': SearchBehaviorType.CONTEXTUAL
        }
        
        return region_behavior_map.get(region.upper(), SearchBehaviorType.DIRECT)

    async def _calculate_local_competition(self, query: str, region: str) -> float:
        """Calculate local competition level."""
        # Simplified local competition calculation
        # In production, use actual local SEO APIs
        
        base_competition = 0.5
        
        # Adjust based on region market size
        large_markets = ['US', 'GB', 'DE', 'FR', 'JP', 'CN']
        if region.upper() in large_markets:
            base_competition += 0.2
        
        # Adjust based on query characteristics
        if len(query.split()) <= 2:
            base_competition += 0.1  # Short queries more competitive
        
        return min(1.0, base_competition)

    async def _calculate_localized_opportunity_score(self, query: str, region: str, 
                                                   competition: float) -> float:
        """Calculate localized opportunity score."""
        # Base opportunity
        opportunity = 0.7
        
        # Lower competition = higher opportunity
        opportunity += (1 - competition) * 0.2
        
        # Regional factors
        emerging_markets = ['IN', 'BR', 'MX', 'ID', 'PH']
        if region.upper() in emerging_markets:
            opportunity += 0.1  # Higher opportunity in emerging markets
        
        return min(1.0, opportunity)

    async def _generate_localized_content_recommendations(self, query: str, region: str, 
                                                        cultural_context: str) -> List[str]:
        """Generate localized content recommendations."""
        recommendations = [
            f"Create region-specific content for {region}",
            f"Include local cultural references for {region}",
            f"Use local language variations and dialects",
            f"Include local business hours and contact information",
            f"Reference local events and seasonal considerations"
        ]
        
        # Cultural context specific recommendations
        if cultural_context == 'asian':
            recommendations.extend([
                "Use respectful and formal language",
                "Include family and community references",
                "Consider visual content preferences"
            ])
        elif cultural_context == 'middle_eastern':
            recommendations.extend([
                "Ensure cultural sensitivity in imagery",
                "Use appropriate formal language",
                "Consider religious considerations"
            ])
        elif cultural_context == 'latin_american':
            recommendations.extend([
                "Include community and family focus",
                "Use warm and personal tone",
                "Reference local festivals and traditions"
            ])
        
        return recommendations