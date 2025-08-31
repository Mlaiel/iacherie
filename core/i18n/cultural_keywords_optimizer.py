"""
Cultural Keywords Optimizer - Ainflue Platform
================================================================================
Module: core/i18n/cultural_keywords_optimizer.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Cultural Keywords Adaptation Engine - Trending and Regional Keywords
Responsibility: Keyword cultural adaptation, trending analysis, and regional optimization
Technologies: Python, Cultural Analysis, Trending Keywords, Regional SEO
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Content analysis → Cultural keyword detection → Regional trends integration → 
Trending keywords analysis → Cultural mapping → SEO optimization → Regional adaptation
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import defaultdict, Counter
import hashlib

# Language processing
from langdetect import detect, DetectorFactory
import pycountry

# Internal imports
try:
    from .cultural_localization import CulturalContext, CulturalLocalization
    from .language_manager import SupportedLanguage
except ImportError:
    # Fallback for development
    SupportedLanguage = None
    CulturalContext = None
    CulturalLocalization = None

logger = logging.getLogger(__name__)

# Set seed for consistent language detection
DetectorFactory.seed = 0


class KeywordCategory(Enum):
    """Keyword categories for cultural adaptation"""
    TRENDING = "trending"
    CULTURAL = "cultural"
    BUSINESS = "business"
    SOCIAL = "social"
    SEASONAL = "seasonal"
    RELIGIOUS = "religious"
    POLITICAL = "political"
    SPORTS = "sports"
    FOOD = "food"
    TECHNOLOGY = "technology"


class TrendingPlatform(Enum):
    """Social media and content platforms for trend analysis"""
    GLOBAL = "global"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    WEIBO = "weibo"  # China
    KAKAO = "kakao"  # Korea
    LINE = "line"  # Japan
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class RegionalPlatformPreference(Enum):
    """Regional platform popularity preferences"""
    PRIMARY = "primary"      # Most popular platform
    SECONDARY = "secondary"  # Secondary platform
    EMERGING = "emerging"    # Growing platform
    DECLINING = "declining"  # Losing popularity
    NICHE = "niche"         # Specific audience


@dataclass
class CulturalKeyword:
    """Cultural keyword information"""
    keyword: str
    original_keyword: str
    category: KeywordCategory
    cultural_relevance: float  # 0-1 score
    trending_score: float     # 0-1 score
    regional_popularity: Dict[str, float]  # country_code -> popularity
    cultural_context: List[str]
    alternative_keywords: List[str]
    seasonal_relevance: Optional[Tuple[int, int]] = None  # (start_month, end_month)
    platform_performance: Dict[TrendingPlatform, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RegionalPlatformConfig:
    """Regional platform configuration"""
    country_code: str
    region: str
    primary_platforms: List[Tuple[TrendingPlatform, RegionalPlatformPreference]]
    content_preferences: Dict[str, Any]
    hashtag_style: str  # "casual", "formal", "business"
    optimal_posting_times: List[str]  # ["09:00-11:00", "19:00-21:00"]
    content_length_preferences: Dict[str, Tuple[int, int]]  # platform -> (min, max) chars
    emoji_acceptance: float  # 0-1 acceptance level
    trending_hashtag_patterns: List[str]
    local_influencer_types: List[str]


@dataclass
class KeywordOptimizationResult:
    """Result of keyword optimization process"""
    original_keywords: List[str]
    optimized_keywords: List[CulturalKeyword]
    cultural_adaptations: List[str]
    trending_enhancements: List[str]
    platform_optimizations: Dict[TrendingPlatform, List[str]]
    regional_recommendations: List[str]
    confidence_score: float
    metadata: Dict[str, Any]


class CulturalKeywordsOptimizer:
    """Advanced cultural keywords optimization and trending analysis engine"""
    
    def __init__(self, cultural_localization: Optional[CulturalLocalization] = None):
        self.cultural_localization = cultural_localization
        self.keyword_cache: Dict[str, CulturalKeyword] = {}
        self.trending_cache: Dict[str, Dict[str, Any]] = {}
        self.regional_platforms: Dict[str, RegionalPlatformConfig] = {}
        self.cultural_keywords_db: Dict[str, Dict[str, List[str]]] = {}
        
        # Initialize system components
        self._initialize_cultural_keywords()
        self._initialize_regional_platforms()
        self._initialize_trending_patterns()
        
        logger.info("Cultural Keywords Optimizer initialized")
    
    def _initialize_cultural_keywords(self):
        """Initialize cultural keywords database"""
        
        # Cultural keywords by language/region
        self.cultural_keywords_db = {
            "ar": {  # Arabic
                "business": ["أعمال", "تجارة", "استثمار", "ريادة", "نجاح", "إنجاز"],
                "technology": ["تقنية", "ذكي", "رقمي", "ابتكار", "تطوير", "برمجة"],
                "culture": ["ثقافة", "تراث", "عادات", "تقاليد", "هوية", "أصالة"],
                "trending": ["ترند", "رائج", "شائع", "فيرال", "منتشر", "مشهور"],
                "islamic": ["إسلامي", "حلال", "بركة", "خير", "نعمة", "فضل"],
                "family": ["عائلة", "أسرة", "أهل", "عشيرة", "قبيلة", "أقارب"],
                "respect": ["احترام", "تقدير", "إجلال", "توقير", "هيبة", "مكانة"]
            },
            
            "amazigh": {  # Berber/Amazigh
                "culture": ["amawal", "tamazight", "imazighen", "taghrifet", "asarag"],
                "nature": ["adrar", "asif", "tafukt", "ayur", "tala", "azalag"],
                "family": ["tawacult", "tayemmatt", "agellid", "tameghurt", "argaz"],
                "wisdom": ["timnadin", "tamusni", "timenna", "taghri", "asilegh"],
                "celebration": ["timechret", "aseggas", "tafaska", "amenzu", "aselway"]
            },
            
            "he": {  # Hebrew
                "business": ["עסקים", "מסחר", "השקעה", "יזמות", "הצלחה", "הישג"],
                "technology": ["טכנולוגיה", "חכם", "דיגיטלי", "חדשנות", "פיתוח", "תכנות"],
                "culture": ["תרבות", "מורשת", "מנהגים", "מסורת", "זהות", "מקוריות"],
                "jewish": ["יהודי", "כשר", "ברכה", "טוב", "מזל", "שבת"],
                "family": ["משפחה", "בית", "הורים", "ילדים", "קרובים", "דורות"],
                "respect": ["כבוד", "הערכה", "יקר", "נכבד", "מכובד", "מעמד"]
            },
            
            "fr": {  # French
                "business": ["affaires", "commerce", "investissement", "entreprise", "succès", "réussite"],
                "technology": ["technologie", "intelligent", "numérique", "innovation", "développement", "programmation"],
                "culture": ["culture", "patrimoine", "traditions", "coutumes", "identité", "authenticité"],
                "trending": ["tendance", "viral", "populaire", "branché", "mode", "buzz"],
                "elegance": ["élégance", "raffinement", "sophistication", "classe", "style", "chic"],
                "intellectual": ["intellectuel", "philosophie", "littérature", "art", "pensée", "réflexion"]
            },
            
            "de": {  # German  
                "business": ["Geschäft", "Handel", "Investition", "Unternehmen", "Erfolg", "Leistung"],
                "technology": ["Technologie", "intelligent", "digital", "Innovation", "Entwicklung", "Programmierung"],
                "culture": ["Kultur", "Erbe", "Traditionen", "Bräuche", "Identität", "Authentizität"],
                "efficiency": ["Effizienz", "Präzision", "Qualität", "Perfektion", "Gründlichkeit", "Ordnung"],
                "engineering": ["Ingenieurwesen", "Technik", "Konstruktion", "Entwicklung", "Präzision", "Mechanik"]
            },
            
            "ja": {  # Japanese
                "business": ["ビジネス", "商業", "投資", "企業", "成功", "達成"],
                "technology": ["技術", "スマート", "デジタル", "革新", "開発", "プログラミング"],
                "culture": ["文化", "遺産", "伝統", "習慣", "アイデンティティ", "真正性"],
                "respect": ["尊敬", "敬意", "礼儀", "丁寧", "謙虚", "思いやり"],
                "harmony": ["調和", "平和", "バランス", "統一", "協調", "共存"],
                "seasonal": ["季節", "春", "夏", "秋", "冬", "桜"]
            },
            
            "ko": {  # Korean
                "business": ["비즈니스", "상업", "투자", "기업", "성공", "성취"],
                "technology": ["기술", "스마트", "디지털", "혁신", "개발", "프로그래밍"],
                "culture": ["문화", "유산", "전통", "관습", "정체성", "진정성"],
                "respect": ["존경", "예의", "공손", "겸손", "배려", "인사"],
                "k-culture": ["한류", "케이팝", "드라마", "한국어", "한식", "전통"]
            },
            
            "zh": {  # Chinese
                "business": ["商业", "贸易", "投资", "企业", "成功", "成就"],
                "technology": ["技术", "智能", "数字", "创新", "开发", "编程"],
                "culture": ["文化", "遗产", "传统", "习俗", "身份", "真实性"],
                "harmony": ["和谐", "平衡", "统一", "协调", "共存", "团结"],
                "prosperity": ["繁荣", "富裕", "兴旺", "发达", "昌盛", "兴盛"],
                "wisdom": ["智慧", "知识", "学问", "见识", "才华", "聪明"]
            }
        }
        
        logger.info(f"Initialized cultural keywords for {len(self.cultural_keywords_db)} languages")
    
    def _initialize_regional_platforms(self):
        """Initialize regional platform preferences"""
        
        # Regional platform configurations
        regional_configs = [
            # Middle East/North Africa
            RegionalPlatformConfig(
                country_code="AE",
                region="Gulf",
                primary_platforms=[
                    (TrendingPlatform.INSTAGRAM, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.TIKTOK, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.YOUTUBE, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.WHATSAPP, RegionalPlatformPreference.PRIMARY)
                ],
                content_preferences={
                    "visual_content": 0.8,
                    "video_content": 0.7,
                    "story_format": 0.9,
                    "live_streaming": 0.6
                },
                hashtag_style="formal",
                optimal_posting_times=["09:00-11:00", "19:00-22:00"],
                content_length_preferences={
                    "instagram": (100, 300),
                    "tiktok": (50, 150),
                    "youtube": (200, 500)
                },
                emoji_acceptance=0.7,
                trending_hashtag_patterns=["#الإمارات", "#دبي", "#تطوير", "#نجاح"],
                local_influencer_types=["business", "lifestyle", "cultural", "religious"]
            ),
            
            RegionalPlatformConfig(
                country_code="MA",
                region="Maghreb",
                primary_platforms=[
                    (TrendingPlatform.FACEBOOK, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.INSTAGRAM, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.YOUTUBE, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.WHATSAPP, RegionalPlatformPreference.PRIMARY)
                ],
                content_preferences={
                    "visual_content": 0.7,
                    "video_content": 0.8,
                    "text_content": 0.6,
                    "cultural_content": 0.9
                },
                hashtag_style="casual",
                optimal_posting_times=["10:00-12:00", "20:00-23:00"],
                content_length_preferences={
                    "facebook": (150, 400),
                    "instagram": (100, 250),
                    "youtube": (300, 800)
                },
                emoji_acceptance=0.8,
                trending_hashtag_patterns=["#المغرب", "#الرباط", "#ثقافة", "#تراث"],
                local_influencer_types=["cultural", "entertainment", "food", "travel"]
            ),
            
            # East Asia
            RegionalPlatformConfig(
                country_code="JP",
                region="East Asia",
                primary_platforms=[
                    (TrendingPlatform.YOUTUBE, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.TWITTER, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.INSTAGRAM, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.LINE, RegionalPlatformPreference.PRIMARY)
                ],
                content_preferences={
                    "video_content": 0.9,
                    "seasonal_content": 0.8,
                    "kawaii_culture": 0.7,
                    "respectful_tone": 0.9
                },
                hashtag_style="formal",
                optimal_posting_times=["07:00-09:00", "18:00-20:00"],
                content_length_preferences={
                    "youtube": (500, 1000),
                    "twitter": (50, 140),
                    "instagram": (100, 300)
                },
                emoji_acceptance=0.9,
                trending_hashtag_patterns=["#日本", "#東京", "#文化", "#技術"],
                local_influencer_types=["tech", "culture", "anime", "food", "fashion"]
            ),
            
            RegionalPlatformConfig(
                country_code="KR",
                region="East Asia",
                primary_platforms=[
                    (TrendingPlatform.YOUTUBE, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.INSTAGRAM, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.TIKTOK, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.KAKAO, RegionalPlatformPreference.PRIMARY)
                ],
                content_preferences={
                    "k_culture": 0.9,
                    "beauty_content": 0.8,
                    "tech_content": 0.7,
                    "music_content": 0.9
                },
                hashtag_style="casual",
                optimal_posting_times=["08:00-10:00", "19:00-21:00"],
                content_length_preferences={
                    "youtube": (300, 600),
                    "instagram": (80, 200),
                    "tiktok": (30, 100)
                },
                emoji_acceptance=0.9,
                trending_hashtag_patterns=["#한국", "#서울", "#케이팝", "#한류"],
                local_influencer_types=["kpop", "beauty", "tech", "food", "gaming"]
            ),
            
            RegionalPlatformConfig(
                country_code="CN",
                region="East Asia",
                primary_platforms=[
                    (TrendingPlatform.WEIBO, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.TIKTOK, RegionalPlatformPreference.SECONDARY),  # Douyin locally
                    (TrendingPlatform.YOUTUBE, RegionalPlatformPreference.DECLINING)  # Blocked
                ],
                content_preferences={
                    "video_content": 0.8,
                    "educational_content": 0.7,
                    "business_content": 0.8,
                    "cultural_harmony": 0.9
                },
                hashtag_style="formal",
                optimal_posting_times=["09:00-11:00", "20:00-22:00"],
                content_length_preferences={
                    "weibo": (100, 300),
                    "tiktok": (50, 150)
                },
                emoji_acceptance=0.6,
                trending_hashtag_patterns=["#中国", "#北京", "#创新", "#发展"],
                local_influencer_types=["business", "tech", "culture", "education"]
            ),
            
            # Western Europe
            RegionalPlatformConfig(
                country_code="DE",
                region="Western Europe",
                primary_platforms=[
                    (TrendingPlatform.YOUTUBE, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.INSTAGRAM, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.LINKEDIN, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.FACEBOOK, RegionalPlatformPreference.DECLINING)
                ],
                content_preferences={
                    "professional_content": 0.8,
                    "educational_content": 0.9,
                    "quality_focus": 0.9,
                    "privacy_conscious": 0.8
                },
                hashtag_style="business",
                optimal_posting_times=["08:00-10:00", "17:00-19:00"],
                content_length_preferences={
                    "youtube": (500, 1200),
                    "linkedin": (200, 600),
                    "instagram": (100, 300)
                },
                emoji_acceptance=0.4,
                trending_hashtag_patterns=["#Deutschland", "#Innovation", "#Qualität", "#Technologie"],
                local_influencer_types=["business", "tech", "engineering", "sustainability"]
            ),
            
            RegionalPlatformConfig(
                country_code="FR",
                region="Western Europe",
                primary_platforms=[
                    (TrendingPlatform.YOUTUBE, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.INSTAGRAM, RegionalPlatformPreference.PRIMARY),
                    (TrendingPlatform.TIKTOK, RegionalPlatformPreference.SECONDARY),
                    (TrendingPlatform.LINKEDIN, RegionalPlatformPreference.SECONDARY)
                ],
                content_preferences={
                    "artistic_content": 0.9,
                    "intellectual_content": 0.8,
                    "fashion_content": 0.8,
                    "cultural_content": 0.9
                },
                hashtag_style="casual",
                optimal_posting_times=["09:00-11:00", "18:00-20:00"],
                content_length_preferences={
                    "youtube": (400, 800),
                    "instagram": (150, 350),
                    "tiktok": (80, 200)
                },
                emoji_acceptance=0.7,
                trending_hashtag_patterns=["#France", "#Paris", "#Culture", "#Art"],
                local_influencer_types=["fashion", "culture", "food", "lifestyle", "intellectual"]
            )
        ]
        
        # Store configurations
        for config in regional_configs:
            self.regional_platforms[config.country_code] = config
        
        logger.info(f"Initialized {len(regional_configs)} regional platform configurations")
    
    def _initialize_trending_patterns(self):
        """Initialize trending keywords patterns and detection"""
        
        self.trending_patterns = {
            "temporal_indicators": [
                r"2025", r"новый", r"nouveau", r"nuevo", r"جديد", r"新しい", r"새로운", r"新的"
            ],
            "viral_indicators": [
                r"viral", r"trending", r"buzz", r"популярный", r"populaire", r"popular", 
                r"شائع", r"رائج", r"バイラル", r"인기", r"热门", r"火爆"
            ],
            "technology_trends": [
                r"AI", r"IA", r"الذكاء الاصطناعي", r"人工知能", r"인공지능", r"人工智能",
                r"blockchain", r"crypto", r"NFT", r"metaverse", r"Web3"
            ],
            "cultural_movements": [
                r"sustainability", r"durabilité", r"sostenibilidad", r"استدامة", r"持続可能性", r"지속가능성", r"可持续性",
                r"diversity", r"diversité", r"diversidad", r"تنوع", r"多様性", r"다양성", r"多样性"
            ]
        }
    
    async def optimize_keywords_culturally(
        self,
        keywords: List[str],
        target_language: str,
        country_code: str,
        platform: Optional[TrendingPlatform] = None,
        content_type: str = "general"
    ) -> KeywordOptimizationResult:
        """
        Optimize keywords for cultural context and trending relevance
        """
        try:
            # Detect source language if needed
            if keywords:
                detected_lang = detect(' '.join(keywords))
                logger.info(f"Detected keyword language: {detected_lang}")
            
            optimized_keywords = []
            cultural_adaptations = []
            trending_enhancements = []
            platform_optimizations = defaultdict(list)
            regional_recommendations = []
            
            # Get regional platform config
            platform_config = self.regional_platforms.get(country_code)
            
            # Process each keyword
            for keyword in keywords:
                # Get cultural adaptation
                cultural_keyword = await self._adapt_keyword_culturally(
                    keyword, target_language, country_code
                )
                
                # Add trending analysis
                cultural_keyword = await self._enhance_with_trending_data(
                    cultural_keyword, target_language, country_code
                )
                
                # Platform-specific optimization
                if platform:
                    cultural_keyword = await self._optimize_for_platform(
                        cultural_keyword, platform, platform_config
                    )
                
                optimized_keywords.append(cultural_keyword)
                
                # Track adaptations
                if cultural_keyword.keyword != cultural_keyword.original_keyword:
                    cultural_adaptations.append(
                        f"{cultural_keyword.original_keyword} → {cultural_keyword.keyword}"
                    )
                
                # Track trending enhancements
                if cultural_keyword.trending_score > 0.6:
                    trending_enhancements.append(
                        f"{cultural_keyword.keyword} (trending: {cultural_keyword.trending_score:.2f})"
                    )
            
            # Generate platform-specific recommendations
            if platform_config:
                for platform_tuple in platform_config.primary_platforms:
                    platform_type, preference = platform_tuple
                    if preference in [RegionalPlatformPreference.PRIMARY, RegionalPlatformPreference.SECONDARY]:
                        platform_optimizations[platform_type] = await self._generate_platform_keywords(
                            optimized_keywords, platform_type, platform_config
                        )
            
            # Generate regional recommendations
            regional_recommendations = await self._generate_regional_recommendations(
                optimized_keywords, country_code, content_type
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_optimization_confidence(
                keywords, optimized_keywords, cultural_adaptations, trending_enhancements
            )
            
            return KeywordOptimizationResult(
                original_keywords=keywords,
                optimized_keywords=optimized_keywords,
                cultural_adaptations=cultural_adaptations,
                trending_enhancements=trending_enhancements,
                platform_optimizations=dict(platform_optimizations),
                regional_recommendations=regional_recommendations,
                confidence_score=confidence_score,
                metadata={
                    "target_language": target_language,
                    "country_code": country_code,
                    "platform": platform.value if platform else None,
                    "content_type": content_type,
                    "optimization_timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Keyword optimization failed: {e}")
            return KeywordOptimizationResult(
                original_keywords=keywords,
                optimized_keywords=[],
                cultural_adaptations=[],
                trending_enhancements=[],
                platform_optimizations={},
                regional_recommendations=[f"Optimization failed: {str(e)}"],
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    async def _adapt_keyword_culturally(
        self,
        keyword: str,
        target_language: str,
        country_code: str
    ) -> CulturalKeyword:
        """Adapt a single keyword culturally"""
        try:
            # Check cache
            cache_key = f"{keyword}_{target_language}_{country_code}"
            if cache_key in self.keyword_cache:
                return self.keyword_cache[cache_key]
            
            # Initialize cultural keyword
            cultural_keyword = CulturalKeyword(
                keyword=keyword,
                original_keyword=keyword,
                category=KeywordCategory.TRENDING,  # Default
                cultural_relevance=0.5,
                trending_score=0.0,
                regional_popularity={country_code: 0.5},
                cultural_context=[],
                alternative_keywords=[]
            )
            
            # Get cultural keywords for target language
            target_lang_keywords = self.cultural_keywords_db.get(target_language, {})
            
            # Find cultural adaptations
            best_match = None
            best_score = 0.0
            
            for category, keywords_list in target_lang_keywords.items():
                for cultural_kw in keywords_list:
                    # Simple similarity check (in production, use more sophisticated matching)
                    similarity = self._calculate_keyword_similarity(keyword, cultural_kw)
                    if similarity > best_score:
                        best_score = similarity
                        best_match = (cultural_kw, category)
            
            # Apply cultural adaptation if good match found
            if best_match and best_score > 0.3:
                adapted_keyword, category = best_match
                cultural_keyword.keyword = adapted_keyword
                cultural_keyword.category = KeywordCategory(category)
                cultural_keyword.cultural_relevance = best_score
                cultural_keyword.cultural_context.append(f"culturally_adapted_from_{category}")
                
                # Add alternatives
                category_keywords = target_lang_keywords.get(category, [])
                cultural_keyword.alternative_keywords = [
                    kw for kw in category_keywords if kw != adapted_keyword
                ][:3]  # Top 3 alternatives
            
            # Enhance with regional context
            cultural_keyword = await self._add_regional_context(
                cultural_keyword, country_code
            )
            
            # Cache result
            self.keyword_cache[cache_key] = cultural_keyword
            
            return cultural_keyword
            
        except Exception as e:
            logger.error(f"Cultural keyword adaptation failed: {e}")
            return CulturalKeyword(
                keyword=keyword,
                original_keyword=keyword,
                category=KeywordCategory.TRENDING,
                cultural_relevance=0.0,
                trending_score=0.0,
                regional_popularity={country_code: 0.0},
                cultural_context=[f"adaptation_error: {str(e)}"],
                alternative_keywords=[]
            )
    
    def _calculate_keyword_similarity(self, keyword1: str, keyword2: str) -> float:
        """Calculate similarity between keywords (simple implementation)"""
        # Convert to lowercase for comparison
        k1 = keyword1.lower()
        k2 = keyword2.lower()
        
        # Exact match
        if k1 == k2:
            return 1.0
        
        # Substring match
        if k1 in k2 or k2 in k1:
            return 0.7
        
        # Character overlap (simplified)
        overlap = len(set(k1) & set(k2))
        total_chars = len(set(k1) | set(k2))
        
        if total_chars == 0:
            return 0.0
        
        return overlap / total_chars
    
    async def _add_regional_context(
        self,
        cultural_keyword: CulturalKeyword,
        country_code: str
    ) -> CulturalKeyword:
        """Add regional context to cultural keyword"""
        
        regional_contexts = {
            "AE": ["luxury", "innovation", "future", "excellence", "global"],
            "MA": ["heritage", "tradition", "family", "community", "authentic"],
            "JP": ["quality", "precision", "respect", "harmony", "seasonal"],
            "KR": ["modern", "trend", "technology", "beauty", "culture"],
            "DE": ["quality", "engineering", "efficiency", "reliability", "sustainability"],
            "FR": ["elegance", "art", "sophistication", "culture", "luxury"],
            "CN": ["harmony", "prosperity", "innovation", "development", "wisdom"]
        }
        
        if country_code in regional_contexts:
            cultural_keyword.cultural_context.extend(regional_contexts[country_code])
            # Boost cultural relevance for regional matches
            cultural_keyword.cultural_relevance = min(1.0, cultural_keyword.cultural_relevance + 0.2)
        
        return cultural_keyword
    
    async def _enhance_with_trending_data(
        self,
        cultural_keyword: CulturalKeyword,
        target_language: str,
        country_code: str
    ) -> CulturalKeyword:
        """Enhance keyword with trending data (simulated)"""
        
        # Simulate trending analysis (in production, integrate with real APIs)
        trending_indicators = {
            "AI": 0.9, "IA": 0.9, "الذكاء الاصطناعي": 0.9,
            "sustainability": 0.8, "استدامة": 0.8, "durabilité": 0.8,
            "technology": 0.7, "تقنية": 0.7, "technologie": 0.7,
            "innovation": 0.8, "ابتكار": 0.8, "innovation": 0.8,
            "culture": 0.6, "ثقافة": 0.6, "culture": 0.6
        }
        
        # Check if keyword matches trending patterns
        keyword_lower = cultural_keyword.keyword.lower()
        for pattern_category, patterns in self.trending_patterns.items():
            for pattern in patterns:
                if re.search(pattern.lower(), keyword_lower):
                    cultural_keyword.trending_score = min(1.0, cultural_keyword.trending_score + 0.3)
                    cultural_keyword.cultural_context.append(f"trending_{pattern_category}")
        
        # Check direct trending indicators
        for trending_kw, score in trending_indicators.items():
            if trending_kw.lower() in keyword_lower:
                cultural_keyword.trending_score = max(cultural_keyword.trending_score, score)
                cultural_keyword.cultural_context.append("trending_high_relevance")
        
        # Simulate seasonal relevance
        current_month = datetime.now().month
        seasonal_keywords = {
            "رمضان": (9, 9),  # Ramadan (varies, using September as example)
            "christmas": (12, 12),
            "新年": (1, 1),  # New Year
            "桜": (3, 4),  # Cherry blossoms
        }
        
        for seasonal_kw, (start_month, end_month) in seasonal_keywords.items():
            if seasonal_kw in cultural_keyword.keyword.lower():
                cultural_keyword.seasonal_relevance = (start_month, end_month)
                if start_month <= current_month <= end_month:
                    cultural_keyword.trending_score = min(1.0, cultural_keyword.trending_score + 0.4)
                    cultural_keyword.cultural_context.append("seasonal_peak")
        
        return cultural_keyword
    
    async def _optimize_for_platform(
        self,
        cultural_keyword: CulturalKeyword,
        platform: TrendingPlatform,
        platform_config: Optional[RegionalPlatformConfig]
    ) -> CulturalKeyword:
        """Optimize keyword for specific platform"""
        
        # Platform-specific optimizations
        platform_optimizations = {
            TrendingPlatform.TIKTOK: {
                "hashtag_style": "casual",
                "trending_boost": 0.3,
                "youth_appeal": 0.4
            },
            TrendingPlatform.LINKEDIN: {
                "hashtag_style": "professional",
                "business_boost": 0.3,
                "formal_tone": 0.2
            },
            TrendingPlatform.INSTAGRAM: {
                "hashtag_style": "lifestyle",
                "visual_boost": 0.3,
                "aesthetic_appeal": 0.2
            },
            TrendingPlatform.YOUTUBE: {
                "hashtag_style": "descriptive",
                "educational_boost": 0.2,
                "searchability": 0.3
            }
        }
        
        if platform in platform_optimizations:
            optimization = platform_optimizations[platform]
            
            # Apply platform-specific boosts
            if "trending_boost" in optimization:
                cultural_keyword.trending_score = min(1.0, 
                    cultural_keyword.trending_score + optimization["trending_boost"])
            
            # Record platform performance
            cultural_keyword.platform_performance[platform] = cultural_keyword.trending_score
            cultural_keyword.cultural_context.append(f"optimized_for_{platform.value}")
        
        return cultural_keyword
    
    async def _generate_platform_keywords(
        self,
        optimized_keywords: List[CulturalKeyword],
        platform: TrendingPlatform,
        platform_config: RegionalPlatformConfig
    ) -> List[str]:
        """Generate platform-specific keyword recommendations"""
        
        platform_keywords = []
        
        # Add platform-specific hashtags
        if hasattr(platform_config, 'trending_hashtag_patterns'):
            platform_keywords.extend(platform_config.trending_hashtag_patterns)
        
        # Add optimized keywords formatted for platform
        for keyword_obj in optimized_keywords:
            if keyword_obj.platform_performance.get(platform, 0) > 0.5:
                formatted_keyword = self._format_keyword_for_platform(
                    keyword_obj.keyword, platform, platform_config
                )
                platform_keywords.append(formatted_keyword)
        
        return platform_keywords[:10]  # Top 10 recommendations
    
    def _format_keyword_for_platform(
        self,
        keyword: str,
        platform: TrendingPlatform,
        platform_config: RegionalPlatformConfig
    ) -> str:
        """Format keyword appropriately for platform"""
        
        # Remove special characters for hashtags
        clean_keyword = re.sub(r'[^\w\s]', '', keyword)
        clean_keyword = clean_keyword.replace(' ', '')
        
        # Platform-specific formatting
        if platform in [TrendingPlatform.INSTAGRAM, TrendingPlatform.TIKTOK, TrendingPlatform.TWITTER]:
            return f"#{clean_keyword}"
        elif platform == TrendingPlatform.YOUTUBE:
            return clean_keyword  # YouTube doesn't use hashtags in titles
        else:
            return keyword
    
    async def _generate_regional_recommendations(
        self,
        optimized_keywords: List[CulturalKeyword],
        country_code: str,
        content_type: str
    ) -> List[str]:
        """Generate regional optimization recommendations"""
        
        recommendations = []
        
        # Regional specific recommendations
        regional_advice = {
            "AE": [
                "Use Arabic keywords for local audience engagement",
                "Include luxury and innovation themes",
                "Respect Islamic cultural values",
                "Optimal posting during Ramadan requires special consideration"
            ],
            "MA": [
                "Include French and Arabic keywords for bilingual audience",
                "Emphasize cultural heritage and tradition",
                "Family-oriented content performs well",
                "Use Darija (Moroccan Arabic) for authenticity"
            ],
            "JP": [
                "Include seasonal references (四季 - shiki)",
                "Use respectful honorific language",
                "Consider kawaii (cute) culture elements",
                "Optimal timing considers work culture"
            ],
            "DE": [
                "Emphasize quality and engineering excellence",
                "Use precise, technical language",
                "Sustainability themes are trending",
                "Avoid overly casual tone in business content"
            ]
        }
        
        if country_code in regional_advice:
            recommendations.extend(regional_advice[country_code])
        
        # Content type specific recommendations
        if content_type == "business":
            recommendations.append("Include industry-specific keywords for B2B audience")
        elif content_type == "entertainment":
            recommendations.append("Use trending cultural references and popular themes")
        
        # High-performing keyword recommendations
        high_performing = [kw for kw in optimized_keywords if kw.cultural_relevance > 0.7]
        if high_performing:
            recommendations.append(
                f"Focus on high-relevance keywords: {', '.join([kw.keyword for kw in high_performing[:3]])}"
            )
        
        return recommendations
    
    async def _calculate_optimization_confidence(
        self,
        original_keywords: List[str],
        optimized_keywords: List[CulturalKeyword],
        cultural_adaptations: List[str],
        trending_enhancements: List[str]
    ) -> float:
        """Calculate confidence score for optimization"""
        
        confidence = 0.5  # Base confidence
        
        # Boost for successful adaptations
        if cultural_adaptations:
            confidence += 0.2
        
        # Boost for trending enhancements
        if trending_enhancements:
            confidence += 0.2
        
        # Boost for high cultural relevance
        avg_cultural_relevance = sum(kw.cultural_relevance for kw in optimized_keywords) / len(optimized_keywords)
        confidence += avg_cultural_relevance * 0.3
        
        # Cap at 1.0
        return min(1.0, confidence)
    
    async def get_trending_keywords(
        self,
        language: str,
        country_code: str,
        platform: Optional[TrendingPlatform] = None,
        category: Optional[KeywordCategory] = None
    ) -> List[CulturalKeyword]:
        """Get trending keywords for specific context"""
        
        try:
            # Simulated trending keywords (in production, integrate with real APIs)
            trending_keywords = []
            
            # Get base keywords for language
            lang_keywords = self.cultural_keywords_db.get(language, {})
            
            for cat, keywords in lang_keywords.items():
                if category and category.value != cat:
                    continue
                
                for keyword in keywords[:3]:  # Top 3 from each category
                    cultural_keyword = CulturalKeyword(
                        keyword=keyword,
                        original_keyword=keyword,
                        category=KeywordCategory(cat),
                        cultural_relevance=0.8,
                        trending_score=0.7 + (hash(keyword) % 30) / 100,  # Simulated trending
                        regional_popularity={country_code: 0.8},
                        cultural_context=[f"trending_{cat}"],
                        alternative_keywords=[]
                    )
                    
                    trending_keywords.append(cultural_keyword)
            
            # Sort by trending score
            trending_keywords.sort(key=lambda x: x.trending_score, reverse=True)
            
            return trending_keywords[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Error getting trending keywords: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Health check for cultural keywords optimizer"""
        try:
            # Check if cultural keywords database is loaded
            if not self.cultural_keywords_db:
                return False
            
            # Check if regional platforms are configured
            if not self.regional_platforms:
                return False
            
            # Test optimization
            test_result = await self.optimize_keywords_culturally(
                ["test", "business"], "ar", "AE"
            )
            
            return test_result.confidence_score > 0
            
        except Exception as e:
            logger.error(f"Cultural keywords optimizer health check failed: {e}")
            return False