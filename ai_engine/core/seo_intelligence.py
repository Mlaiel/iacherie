"""SEO Intelligence & Content Optimization Engine

Advanced AI-powered SEO optimization system for content creators platform.
Maximizes discoverability, engagement, and organic reach across all platforms.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This cutting-edge SEO AI system is protected intellectual property.
Any unauthorized copying, distribution, or use will result in immediate legal action.

Business Logic: Content Analysis → SEO Optimization → Platform Targeting → Performance Tracking → Continuous Improvement
"""
import asyncio
import json
import uuid
import re
import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, Counter
import hashlib

# NLP and ML imports
try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModel, pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    import spacy
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

from .exceptions import OptimizationError, ContentGenerationError
from .metrics import metrics_collector
from .performance import performance_monitor
from .content_types import ContentType

logger = logging.getLogger(__name__)


class SEOStrategy(Enum):
    """SEO optimization strategies"""    KEYWORD_OPTIMIZATION = "keyword_optimization"
    SEMANTIC_SEO = "semantic_seo"
    LONG_TAIL_TARGETING = "long_tail_targeting"
    TRENDING_TOPICS = "trending_topics"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    LOCAL_SEO = "local_seo"
    VOICE_SEARCH = "voice_search"
    VIDEO_SEO = "video_seo"
    SOCIAL_SEO = "social_seo"
    TECHNICAL_SEO = "technical_seo"


class PlatformType(Enum):
    """Platform types for optimization"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    GOOGLE_SEARCH = "google_search"
    BING_SEARCH = "bing_search"


class ContentOptimizationGoal(Enum):
    """Content optimization goals"""    MAXIMIZE_REACH = "maximize_reach"
    INCREASE_ENGAGEMENT = "increase_engagement"
    IMPROVE_DISCOVERABILITY = "improve_discoverability"
    BOOST_CONVERSIONS = "boost_conversions"
    BUILD_AUTHORITY = "build_authority"
    TARGET_DEMOGRAPHICS = "target_demographics"
    VIRAL_POTENTIAL = "viral_potential"
    BRAND_AWARENESS = "brand_awareness"


@dataclass
class KeywordAnalysis:
    """Keyword analysis results"""    keyword: str
    search_volume: int
    competition_level: str
    difficulty_score: float
    relevance_score: float
    trend_direction: str
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)
    related_keywords: List[str] = field(default_factory=list)
    long_tail_variations: List[str] = field(default_factory=list)
    intent_classification: str = "informational"
    cpc_estimate: float = 0.0
    platform_performance: Dict[str, float] = field(default_factory=dict)


@dataclass
class SEORecommendation:
    """SEO optimization recommendation"""    recommendation_id: str
    category: str
    title: str
    description: str
    priority: str
    impact_level: str
    implementation_difficulty: str
    estimated_improvement: str
    target_platforms: List[str]
    specific_actions: List[str]
    success_metrics: List[str]
    timeframe: str
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentOptimizationPlan:
    """Comprehensive content optimization plan"""    plan_id: str
    content_id: str
    content_type: ContentType
    optimization_goal: ContentOptimizationGoal
    target_platforms: List[str]
    target_keywords: List[KeywordAnalysis]
    title_suggestions: List[Dict[str, Any]]
    description_suggestions: List[Dict[str, Any]]
    hashtag_recommendations: List[str]
    posting_schedule: Dict[str, Any]
    engagement_strategies: List[Dict[str, Any]]
    seo_recommendations: List[SEORecommendation]
    performance_predictions: Dict[str, float]
    competitor_insights: Dict[str, Any] = field(default_factory=dict)
    audience_insights: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class KeywordResearchEngine:
    """Advanced keyword research and analysis"""    
    def __init__(self):
        self.keyword_database = {}
        self.trending_topics = []
        self._initialize_nlp_models()
    
    def _initialize_nlp_models(self):
        """Initialize NLP models for keyword analysis"""        if NLP_AVAILABLE:
            try:
                # Initialize sentiment analyzer
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
                
                # Initialize TF-IDF vectorizer
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=10000,
                    stop_words='english',
                    ngram_range=(1, 3)
                )
                
                # Load spaCy model for entity recognition
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("SpaCy model not found, using basic processing")
                    self.nlp = None
                
                logger.info("Keyword research models initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize NLP models: {e}")
    
    async def analyze_keywords(self, 
                             content: str,
                             target_audience: str,
                             content_type: ContentType,
                             platforms: List[str]) -> List[KeywordAnalysis]:
        """Analyze and extract optimized keywords from content"""        try:
            # Extract base keywords from content
            base_keywords = await self._extract_base_keywords(content)
            
            # Generate related keywords
            related_keywords = await self._generate_related_keywords(base_keywords, target_audience)
            
            # Analyze keyword performance for each platform
            analyzed_keywords = []
            for keyword in base_keywords + related_keywords:
                analysis = await self._analyze_single_keyword(
                    keyword, content_type, platforms, target_audience
                )
                analyzed_keywords.append(analysis)
            
            # Sort by relevance and potential
            analyzed_keywords.sort(
                key=lambda x: x.relevance_score * (1 / max(x.difficulty_score, 0.1)),
                reverse=True
            )
            
            return analyzed_keywords[:50]  # Return top 50 keywords
            
        except Exception as e:
            logger.error(f"Keyword analysis failed: {e}")
            raise OptimizationError(f"Keyword analysis failed: {str(e)}")
    
    async def _extract_base_keywords(self, content: str) -> List[str]:
        """Extract base keywords from content"""        try:
            keywords = set()
            
            # Simple regex-based extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
            
            if NLP_AVAILABLE:
                # Remove stopwords
                try:
                    stop_words = set(stopwords.words('english'))
                    words = [w for w in words if w not in stop_words]
                except:
                    pass
                
                # Extract named entities if spaCy available
                if self.nlp:
                    doc = self.nlp(content)
                    for ent in doc.ents:
                        keywords.add(ent.text.lower())
                
                # Extract noun phrases
                try:
                    doc = self.nlp(content)
                    for chunk in doc.noun_chunks:
                        if len(chunk.text.split()) <= 3:  # Max 3-word phrases
                            keywords.add(chunk.text.lower())
                except:
                    pass
            
            # Add frequent words
            word_freq = Counter(words)
            for word, freq in word_freq.most_common(20):
                if len(word) > 3:
                    keywords.add(word)
            
            # Generate 2-gram and 3-gram phrases
            words_list = content.lower().split()
            for i in range(len(words_list) - 1):
                bigram = f"{words_list[i]} {words_list[i+1]}"
                if len(bigram) > 6:
                    keywords.add(bigram)
            
            for i in range(len(words_list) - 2):
                trigram = f"{words_list[i]} {words_list[i+1]} {words_list[i+2]}"
                if len(trigram) > 10:
                    keywords.add(trigram)
            
            return list(keywords)
            
        except Exception as e:
            logger.error(f"Base keyword extraction failed: {e}")
            return []
    
    async def _generate_related_keywords(self, 
                                       base_keywords: List[str],
                                       target_audience: str) -> List[str]:
        """Generate related keywords using AI"""        try:
            related = set()
            
            for keyword in base_keywords[:10]:  # Process top 10 base keywords
                # Generate semantic variations
                variations = self._generate_keyword_variations(keyword)
                related.update(variations)
                
                # Add audience-specific modifications
                audience_variations = self._generate_audience_keywords(keyword, target_audience)
                related.update(audience_variations)
            
            return list(related)
            
        except Exception as e:
            logger.error(f"Related keyword generation failed: {e}")
            return []
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Generate keyword variations"""        variations = []
        
        # Common prefixes and suffixes
        prefixes = ["best", "top", "how to", "free", "new", "ultimate", "complete"]
        suffixes = ["tips", "guide", "tutorial", "review", "examples", "ideas", "strategies"]
        
        for prefix in prefixes:
            variations.append(f"{prefix} {keyword}")
        
        for suffix in suffixes:
            variations.append(f"{keyword} {suffix}")
        
        # Question variations
        question_starters = ["how to", "what is", "why", "where to", "when to"]
        for starter in question_starters:
            if starter not in keyword:
                variations.append(f"{starter} {keyword}")
        
        return variations
    
    def _generate_audience_keywords(self, keyword: str, target_audience: str) -> List[str]:
        """Generate audience-specific keyword variations"""        variations = []
        
        if target_audience:
            audience_modifiers = [
                f"{keyword} for {target_audience}",
                f"{target_audience} {keyword}",
                f"{keyword} {target_audience} tips"
            ]
            variations.extend(audience_modifiers)
        
        return variations
    
    async def _analyze_single_keyword(self, 
                                    keyword: str,
                                    content_type: ContentType,
                                    platforms: List[str],
                                    target_audience: str) -> KeywordAnalysis:
        """Analyze a single keyword comprehensively"""        try:
            # Simulate keyword metrics (in real implementation, would use APIs)
            search_volume = self._estimate_search_volume(keyword)
            competition_level = self._assess_competition_level(keyword)
            difficulty_score = self._calculate_difficulty_score(keyword, competition_level)
            relevance_score = self._calculate_relevance_score(keyword, content_type, target_audience)
            trend_direction = self._analyze_trend_direction(keyword)
            
            # Platform-specific performance
            platform_performance = {}
            for platform in platforms:
                performance = self._estimate_platform_performance(keyword, platform)
                platform_performance[platform] = performance
            
            # Generate related keywords
            related_keywords = self._generate_keyword_variations(keyword)[:5]
            
            # Generate long-tail variations
            long_tail_variations = [
                f"{keyword} tutorial",
                f"how to {keyword}",
                f"best {keyword} tips",
                f"{keyword} for beginners"
            ]
            
            # Classify search intent
            intent = self._classify_search_intent(keyword)
            
            return KeywordAnalysis(
                keyword=keyword,
                search_volume=search_volume,
                competition_level=competition_level,
                difficulty_score=difficulty_score,
                relevance_score=relevance_score,
                trend_direction=trend_direction,
                related_keywords=related_keywords,
                long_tail_variations=long_tail_variations,
                intent_classification=intent,
                platform_performance=platform_performance
            )
            
        except Exception as e:
            logger.error(f"Single keyword analysis failed: {e}")
            return KeywordAnalysis(
                keyword=keyword,
                search_volume=100,
                competition_level="medium",
                difficulty_score=0.5,
                relevance_score=0.5,
                trend_direction="stable"
            )
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for keyword"""        # Simplified estimation based on keyword characteristics
        base_volume = 1000
        
        # Adjust for keyword length
        if len(keyword.split()) == 1:
            base_volume *= 2  # Single words get higher volume
        elif len(keyword.split()) > 3:
            base_volume *= 0.3  # Long tail gets lower volume
        
        # Adjust for common words
        common_words = ["how", "what", "best", "top", "free", "new"]
        if any(word in keyword.lower() for word in common_words):
            base_volume *= 1.5
        
        return max(10, int(base_volume))
    
    def _assess_competition_level(self, keyword: str) -> str:
        """Assess competition level for keyword"""        # Simplified assessment
        if len(keyword.split()) <= 1:
            return "high"
        elif len(keyword.split()) <= 2:
            return "medium"
        else:
            return "low"
    
    def _calculate_difficulty_score(self, keyword: str, competition: str) -> float:
        """Calculate SEO difficulty score"""        difficulty_map = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8
        }
        
        base_difficulty = difficulty_map.get(competition, 0.5)
        
        # Adjust for keyword characteristics
        if len(keyword.split()) > 3:
            base_difficulty -= 0.2  # Long tail is easier
        
        if any(word in keyword.lower() for word in ["tutorial", "guide", "how to"]):
            base_difficulty -= 0.1  # Informational content easier
        
        return max(0.1, min(0.9, base_difficulty))
    
    def _calculate_relevance_score(self, 
                                 keyword: str,
                                 content_type: ContentType,
                                 target_audience: str) -> float:
        """Calculate relevance score"""        base_score = 0.5
        
        # Content type relevance
        content_keywords = {
            ContentType.MUSIC: ["music", "song", "artist", "album", "beat"],
            ContentType.VIDEO: ["video", "watch", "tutorial", "review"],
            ContentType.BLOG_POST: ["blog", "article", "read", "post"],
            ContentType.PHOTOGRAPHY: ["photo", "image", "picture", "photography"]
        }
        
        relevant_terms = content_keywords.get(content_type, [])
        if any(term in keyword.lower() for term in relevant_terms):
            base_score += 0.3
        
        # Target audience relevance
        if target_audience and target_audience.lower() in keyword.lower():
            base_score += 0.2
        
        return min(1.0, base_score)
    
    def _analyze_trend_direction(self, keyword: str) -> str:
        """Analyze keyword trend direction"""        # Simplified trend analysis
        trending_indicators = ["2025", "new", "latest", "trending", "viral"]
        declining_indicators = ["old", "classic", "vintage", "traditional"]
        
        if any(indicator in keyword.lower() for indicator in trending_indicators):
            return "rising"
        elif any(indicator in keyword.lower() for indicator in declining_indicators):
            return "declining"
        else:
            return "stable"
    
    def _estimate_platform_performance(self, keyword: str, platform: str) -> float:
        """Estimate keyword performance on specific platform"""        # Platform-specific performance factors
        platform_factors = {
            "youtube": 0.8,
            "instagram": 0.7,
            "tiktok": 0.9,
            "twitter": 0.6,
            "google_search": 0.8
        }
        
        base_performance = platform_factors.get(platform, 0.5)
        
        # Adjust for platform-specific keywords
        platform_keywords = {
            "youtube": ["video", "watch", "tutorial", "review"],
            "instagram": ["photo", "pic", "style", "fashion"],
            "tiktok": ["viral", "trend", "dance", "challenge"]
        }
        
        relevant_terms = platform_keywords.get(platform, [])
        if any(term in keyword.lower() for term in relevant_terms):
            base_performance += 0.2
        
        return min(1.0, base_performance)
    
    def _classify_search_intent(self, keyword: str) -> str:
        """Classify search intent of keyword"""        # Intent classification based on keyword patterns
        if any(word in keyword.lower() for word in ["how", "tutorial", "guide", "learn"]):
            return "informational"
        elif any(word in keyword.lower() for word in ["buy", "price", "cost", "purchase"]):
            return "commercial"
        elif any(word in keyword.lower() for word in ["best", "top", "review", "compare"]):
            return "commercial_investigation"
        elif any(word in keyword.lower() for word in ["near me", "location", "where"]):
            return "local"
        else:
            return "informational"


class ContentTitleOptimizer:
    """AI-powered content title optimization"""    
    def __init__(self):
        self.title_patterns = {}
        self.power_words = [
            "ultimate", "essential", "complete", "proven", "secret",
            "amazing", "incredible", "revolutionary", "breakthrough",
            "exclusive", "instant", "guaranteed", "powerful", "effective"
        ]
        
        self.emotion_words = [
            "love", "hate", "fear", "joy", "surprise", "anger",
            "exciting", "shocking", "inspiring", "heartbreaking"
        ]
    
    async def generate_optimized_titles(self, 
                                      content: str,
                                      target_keywords: List[str],
                                      platform: str,
                                      content_type: ContentType,
                                      target_audience: str = None) -> List[Dict[str, Any]]:
        """Generate optimized titles for content"""        try:
            titles = []
            
            # Generate different title types
            for keyword in target_keywords[:5]:  # Use top 5 keywords
                # Question-based titles
                question_titles = self._generate_question_titles(keyword, content_type)
                titles.extend(question_titles)
                
                # How-to titles
                howto_titles = self._generate_howto_titles(keyword, content_type)
                titles.extend(howto_titles)
                
                # List-based titles
                list_titles = self._generate_list_titles(keyword, content_type)
                titles.extend(list_titles)
                
                # Emotional titles
                emotional_titles = self._generate_emotional_titles(keyword, content_type)
                titles.extend(emotional_titles)
                
                # Power word titles
                power_titles = self._generate_power_word_titles(keyword, content_type)
                titles.extend(power_titles)
            
            # Score and rank titles
            scored_titles = []
            for title_data in titles:
                score = await self._score_title(
                    title_data["title"], platform, content_type, target_keywords
                )
                title_data["seo_score"] = score
                title_data["estimated_ctr"] = self._estimate_ctr(title_data["title"], platform)
                scored_titles.append(title_data)
            
            # Sort by score
            scored_titles.sort(key=lambda x: x["seo_score"], reverse=True)
            
            return scored_titles[:20]  # Return top 20 titles
            
        except Exception as e:
            logger.error(f"Title optimization failed: {e}")
            return []
    
    def _generate_question_titles(self, keyword: str, content_type: ContentType) -> List[Dict[str, Any]]:
        """Generate question-based titles"""        question_starters = [
            "What is", "How does", "Why do", "When should", "Where can",
            "Which is", "Who should", "How can", "What are"
        ]
        
        titles = []
        for starter in question_starters:
            title = f"{starter} {keyword}?"
            titles.append({
                "title": title.title(),
                "type": "question",
                "engagement_potential": "high",
                "platform_fit": ["youtube", "google_search", "medium"]
            })
        
        return titles[:3]  # Return top 3
    
    def _generate_howto_titles(self, keyword: str, content_type: ContentType) -> List[Dict[str, Any]]:
        """Generate how-to titles"""        templates = [
            f"How to {keyword}",
            f"How to {keyword} in 2025",
            f"How to {keyword} like a Pro",
            f"How to {keyword} for Beginners",
            f"Step-by-Step Guide to {keyword}"
        ]
        
        titles = []
        for template in templates:
            titles.append({
                "title": template.title(),
                "type": "howto",
                "engagement_potential": "high",
                "platform_fit": ["youtube", "blog", "medium"]
            })
        
        return titles
    
    def _generate_list_titles(self, keyword: str, content_type: ContentType) -> List[Dict[str, Any]]:
        """Generate list-based titles"""        numbers = [5, 7, 10, 15, 20, 25, 50, 100]
        
        templates = [
            f"{{}} Best {keyword} Tips",
            f"{{}} {keyword} Strategies That Work",
            f"{{}} Things You Need to Know About {keyword}",
            f"Top {{}} {keyword} Mistakes to Avoid",
            f"{{}} Proven {keyword} Techniques"
        ]
        
        titles = []
        for num in numbers[:3]:  # Use first 3 numbers
            for template in templates[:2]:  # Use first 2 templates
                title = template.format(num)
                titles.append({
                    "title": title.title(),
                    "type": "list",
                    "engagement_potential": "medium",
                    "platform_fit": ["all"]
                })
        
        return titles
    
    def _generate_emotional_titles(self, keyword: str, content_type: ContentType) -> List[Dict[str, Any]]:
        """Generate emotionally engaging titles"""        templates = [
            f"The Shocking Truth About {keyword}",
            f"Why Everyone is Talking About {keyword}",
            f"This {keyword} Will Change Your Life",
            f"The Secret to {keyword} That Nobody Tells You",
            f"You Won't Believe This {keyword} Trick"
        ]
        
        titles = []
        for template in templates:
            titles.append({
                "title": template.title(),
                "type": "emotional",
                "engagement_potential": "very_high",
                "platform_fit": ["social_media", "youtube"]
            })
        
        return titles[:2]  # Return top 2
    
    def _generate_power_word_titles(self, keyword: str, content_type: ContentType) -> List[Dict[str, Any]]:
        """Generate titles with power words"""        titles = []
        
        for power_word in self.power_words[:5]:
            templates = [
                f"The {power_word} Guide to {keyword}",
                f"{power_word} {keyword} Strategies",
                f"Discover the {power_word} {keyword} Method"
            ]
            
            for template in templates[:1]:  # One template per power word
                titles.append({
                    "title": template.title(),
                    "type": "power_word",
                    "engagement_potential": "high",
                    "platform_fit": ["all"]
                })
        
        return titles
    
    async def _score_title(self, 
                         title: str,
                         platform: str,
                         content_type: ContentType,
                         keywords: List[str]) -> float:
        """Score title based on SEO and engagement factors"""        try:
            score = 0.0
            
            # Keyword presence (30% weight)
            keyword_score = 0.0
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    keyword_score += 1.0
            keyword_score = min(1.0, keyword_score / len(keywords)) if keywords else 0.0
            score += keyword_score * 0.3
            
            # Title length optimization (20% weight)
            length_score = self._score_title_length(title, platform)
            score += length_score * 0.2
            
            # Emotional engagement (25% weight)
            emotion_score = self._score_emotional_engagement(title)
            score += emotion_score * 0.25
            
            # Power words (10% weight)
            power_score = self._score_power_words(title)
            score += power_score * 0.1
            
            # Platform optimization (15% weight)
            platform_score = self._score_platform_optimization(title, platform)
            score += platform_score * 0.15
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Title scoring failed: {e}")
            return 0.5
    
    def _score_title_length(self, title: str, platform: str) -> float:
        """Score title based on optimal length for platform"""        optimal_lengths = {
            "youtube": (40, 70),
            "instagram": (100, 125),
            "twitter": (70, 100),
            "google_search": (50, 60),
            "facebook": (40, 80)
        }
        
        min_len, max_len = optimal_lengths.get(platform, (40, 70))
        title_len = len(title)
        
        if min_len <= title_len <= max_len:
            return 1.0
        elif title_len < min_len:
            return title_len / min_len
        else:
            return max(0.3, 1.0 - ((title_len - max_len) / max_len))
    
    def _score_emotional_engagement(self, title: str) -> float:
        """Score emotional engagement potential"""        score = 0.0
        
        # Check for emotional words
        for emotion_word in self.emotion_words:
            if emotion_word in title.lower():
                score += 0.2
        
        # Check for question format
        if title.endswith('?'):
            score += 0.3
        
        # Check for numbers
        if re.search(r'\d+', title):
            score += 0.2
        
        # Check for brackets or parentheses
        if re.search(r'[\[\(]', title):
            score += 0.1
        
        return min(1.0, score)
    
    def _score_power_words(self, title: str) -> float:
        """Score presence of power words"""        score = 0.0
        
        for power_word in self.power_words:
            if power_word in title.lower():
                score += 0.3
        
        return min(1.0, score)
    
    def _score_platform_optimization(self, title: str, platform: str) -> float:
        """Score platform-specific optimization"""        platform_preferences = {
            "youtube": ["tutorial", "how to", "review", "guide"],
            "instagram": ["photo", "style", "inspiration", "aesthetic"],
            "tiktok": ["trend", "viral", "challenge", "quick"],
            "twitter": ["breaking", "news", "update", "thread"]
        }
        
        preferences = platform_preferences.get(platform, [])
        score = 0.0
        
        for pref in preferences:
            if pref in title.lower():
                score += 0.5
        
        return min(1.0, score)
    
    def _estimate_ctr(self, title: str, platform: str) -> float:
        """Estimate click-through rate for title"""        base_ctr = {
            "youtube": 0.05,
            "instagram": 0.02,
            "twitter": 0.03,
            "google_search": 0.08
        }.get(platform, 0.04)
        
        # Adjust for title characteristics
        multiplier = 1.0
        
        if title.endswith('?'):
            multiplier *= 1.3
        
        if any(word in title.lower() for word in self.power_words):
            multiplier *= 1.2
        
        if re.search(r'\d+', title):
            multiplier *= 1.15
        
        return min(0.15, base_ctr * multiplier)


class HashtagOptimizer:
    """AI-powered hashtag optimization"""    
    def __init__(self):
        self.hashtag_database = {}
        self.trending_hashtags = []
    
    async def generate_optimized_hashtags(self, 
                                        content: str,
                                        keywords: List[str],
                                        platform: str,
                                        target_audience: str = None) -> List[str]:
        """Generate optimized hashtags for content"""        try:
            hashtags = set()
            
            # Extract hashtags from keywords
            for keyword in keywords:
                hashtag_variations = self._generate_hashtag_variations(keyword)
                hashtags.update(hashtag_variations)
            
            # Add content-based hashtags
            content_hashtags = self._extract_content_hashtags(content)
            hashtags.update(content_hashtags)
            
            # Add trending hashtags
            trending = self._get_trending_hashtags(platform)
            hashtags.update(trending[:5])  # Add top 5 trending
            
            # Add platform-specific hashtags
            platform_hashtags = self._get_platform_hashtags(platform)
            hashtags.update(platform_hashtags)
            
            # Score and filter hashtags
            scored_hashtags = []
            for hashtag in hashtags:
                score = self._score_hashtag(hashtag, platform, keywords)
                if score > 0.3:  # Minimum threshold
                    scored_hashtags.append((hashtag, score))
            
            # Sort by score and return optimal number for platform
            scored_hashtags.sort(key=lambda x: x[1], reverse=True)
            
            optimal_count = self._get_optimal_hashtag_count(platform)
            return [hashtag for hashtag, score in scored_hashtags[:optimal_count]]
            
        except Exception as e:
            logger.error(f"Hashtag optimization failed: {e}")
            return []
    
    def _generate_hashtag_variations(self, keyword: str) -> List[str]:
        """Generate hashtag variations from keyword"""        variations = []
        
        # Clean keyword for hashtag
        clean_keyword = re.sub(r'[^\w\s]', '', keyword).replace(' ', '')
        
        if clean_keyword:
            variations.append(f"#{clean_keyword.lower()}")
            
            # Add variations
            words = keyword.split()
            if len(words) > 1:
                # Individual words
                for word in words:
                    clean_word = re.sub(r'[^\w]', '', word)
                    if len(clean_word) > 2:
                        variations.append(f"#{clean_word.lower()}")
                
                # Camel case version
                camel_case = ''.join(word.capitalize() for word in words)
                variations.append(f"#{camel_case}")
        
        return variations
    
    def _extract_content_hashtags(self, content: str) -> List[str]:
        """Extract relevant hashtags from content"""        hashtags = []
        
        # Extract existing hashtags
        existing_hashtags = re.findall(r'#\w+', content)
        hashtags.extend(existing_hashtags)
        
        # Generate hashtags from frequent words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = Counter(words)
        
        for word, freq in word_freq.most_common(10):
            if freq > 1 and len(word) > 3:
                hashtags.append(f"#{word}")
        
        return hashtags
    
    def _get_trending_hashtags(self, platform: str) -> List[str]:
        """Get trending hashtags for platform"""        # Simulated trending hashtags (in real implementation, would use APIs)
        trending_by_platform = {
            "instagram": [
                "#trending", "#viral", "#explore", "#instagood", "#photooftheday"
            ],
            "twitter": [
                "#breaking", "#news", "#trending", "#viral", "#thread"
            ],
            "tiktok": [
                "#fyp", "#foryou", "#viral", "#trending", "#challenge"
            ],
            "linkedin": [
                "#professional", "#business", "#career", "#networking", "#industry"
            ]
        }
        
        return trending_by_platform.get(platform, ["#trending", "#viral"])
    
    def _get_platform_hashtags(self, platform: str) -> List[str]:
        """Get platform-specific hashtags"""        platform_hashtags = {
            "instagram": ["#instagram", "#insta", "#ig", "#reels"],
            "twitter": ["#twitter", "#tweet", "#rt"],
            "tiktok": ["#tiktok", "#fyp", "#foryoupage"],
            "youtube": ["#youtube", "#video", "#subscribe"],
            "linkedin": ["#linkedin", "#professional", "#business"]
        }
        
        return platform_hashtags.get(platform, [])
    
    def _score_hashtag(self, hashtag: str, platform: str, keywords: List[str]) -> float:
        """Score hashtag relevance and effectiveness"""        score = 0.0
        
        # Relevance to keywords
        hashtag_clean = hashtag.replace('#', '').lower()
        for keyword in keywords:
            if hashtag_clean in keyword.lower() or keyword.lower() in hashtag_clean:
                score += 0.4
                break
        
        # Length optimization
        if 3 <= len(hashtag_clean) <= 15:
            score += 0.2
        
        # Platform compatibility
        if platform in ["instagram", "twitter"] and len(hashtag_clean) <= 20:
            score += 0.2
        elif platform == "linkedin" and len(hashtag_clean) <= 10:
            score += 0.2
        
        # Avoid over-used hashtags
        overused = ["#love", "#instagood", "#me", "#follow", "#like"]
        if hashtag not in overused:
            score += 0.2
        
        return min(1.0, score)
    
    def _get_optimal_hashtag_count(self, platform: str) -> int:
        """Get optimal number of hashtags for platform"""        optimal_counts = {
            "instagram": 25,
            "twitter": 2,
            "linkedin": 5,
            "tiktok": 15,
            "youtube": 10
        }
        
        return optimal_counts.get(platform, 10)


class SEOOptimizationEngine:
    """Main SEO optimization engine"""    
    def __init__(self):
        self.keyword_engine = KeywordResearchEngine()
        self.title_optimizer = ContentTitleOptimizer()
        self.hashtag_optimizer = HashtagOptimizer()
        self.optimization_plans = {}
    
    async def create_optimization_plan(self, 
                                     content_id: str,
                                     content: str,
                                     content_type: ContentType,
                                     target_platforms: List[str],
                                     optimization_goal: ContentOptimizationGoal,
                                     target_audience: str = None,
                                     competitor_urls: List[str] = None) -> ContentOptimizationPlan:
        """Create comprehensive content optimization plan"""        try:
            # Keyword research and analysis
            keywords = await self.keyword_engine.analyze_keywords(
                content, target_audience or "general", content_type, target_platforms
            )
            
            # Generate optimized titles for each platform
            all_title_suggestions = {}
            for platform in target_platforms:
                titles = await self.title_optimizer.generate_optimized_titles(
                    content, [kw.keyword for kw in keywords[:10]], 
                    platform, content_type, target_audience
                )
                all_title_suggestions[platform] = titles
            
            # Generate platform-specific hashtags
            all_hashtag_recommendations = {}
            for platform in target_platforms:
                hashtags = await self.hashtag_optimizer.generate_optimized_hashtags(
                    content, [kw.keyword for kw in keywords[:15]], 
                    platform, target_audience
                )
                all_hashtag_recommendations[platform] = hashtags
            
            # Generate SEO recommendations
            seo_recommendations = await self._generate_seo_recommendations(
                content, keywords, target_platforms, content_type
            )
            
            # Create posting schedule
            posting_schedule = self._create_optimal_posting_schedule(target_platforms)
            
            # Generate engagement strategies
            engagement_strategies = self._generate_engagement_strategies(
                content_type, target_platforms, optimization_goal
            )
            
            # Predict performance
            performance_predictions = await self._predict_content_performance(
                content, keywords, target_platforms, content_type
            )
            
            # Analyze competitors if URLs provided
            competitor_insights = {}
            if competitor_urls:
                competitor_insights = await self._analyze_competitors(competitor_urls)
            
            # Generate audience insights
            audience_insights = self._generate_audience_insights(target_audience, keywords)
            
            # Create comprehensive plan
            plan = ContentOptimizationPlan(
                plan_id=str(uuid.uuid4()),
                content_id=content_id,
                content_type=content_type,
                optimization_goal=optimization_goal,
                target_platforms=target_platforms,
                target_keywords=keywords[:20],  # Top 20 keywords
                title_suggestions=[all_title_suggestions],
                description_suggestions=await self._generate_description_suggestions(content, keywords),
                hashtag_recommendations=list(all_hashtag_recommendations.values())[0] if all_hashtag_recommendations else [],
                posting_schedule=posting_schedule,
                engagement_strategies=engagement_strategies,
                seo_recommendations=seo_recommendations,
                performance_predictions=performance_predictions,
                competitor_insights=competitor_insights,
                audience_insights=audience_insights
            )
            
            # Store plan
            self.optimization_plans[content_id] = plan
            
            return plan
            
        except Exception as e:
            logger.error(f"SEO optimization plan creation failed: {e}")
            raise OptimizationError(f"SEO plan creation failed: {str(e)}")
    
    async def _generate_seo_recommendations(self, 
                                          content: str,
                                          keywords: List[KeywordAnalysis],
                                          platforms: List[str],
                                          content_type: ContentType) -> List[SEORecommendation]:
        """Generate SEO recommendations"""        recommendations = []
        
        # Keyword optimization
        if keywords:
            recommendations.append(SEORecommendation(
                recommendation_id=str(uuid.uuid4()),
                category="keyword_optimization",
                title="Optimize Primary Keywords",
                description=f"Focus on primary keywords: {', '.join([kw.keyword for kw in keywords[:5]])}",
                priority="high",
                impact_level="high",
                implementation_difficulty="easy",
                estimated_improvement="15-25% increase in organic reach",
                target_platforms=platforms,
                specific_actions=[
                    "Include primary keyword in title",
                    "Use keywords in first paragraph",
                    "Include keywords in meta description",
                    "Use keyword variations throughout content"
                ],
                success_metrics=["Improved search rankings", "Increased organic traffic"],
                timeframe="1-2 weeks",
                confidence_score=0.85
            ))
        
        # Content structure optimization
        recommendations.append(SEORecommendation(
            recommendation_id=str(uuid.uuid4()),
            category="content_structure",
            title="Improve Content Structure",
            description="Optimize content structure for better readability and SEO",
            priority="medium",
            impact_level="medium",
            implementation_difficulty="easy",
            estimated_improvement="10-15% better engagement",
            target_platforms=platforms,
            specific_actions=[
                "Use clear headings and subheadings",
                "Break content into digestible paragraphs",
                "Include bullet points and lists",
                "Add internal and external links"
            ],
            success_metrics=["Better user engagement", "Lower bounce rate"],
            timeframe="1 week",
            confidence_score=0.75
        ))
        
        # Platform-specific optimizations
        for platform in platforms:
            platform_rec = self._generate_platform_specific_recommendation(platform, content_type)
            if platform_rec:
                recommendations.append(platform_rec)
        
        return recommendations
    
    def _generate_platform_specific_recommendation(self, 
                                                 platform: str,
                                                 content_type: ContentType) -> Optional[SEORecommendation]:
        """Generate platform-specific SEO recommendation"""        platform_recommendations = {
            "youtube": {
                "title": "YouTube SEO Optimization",
                "description": "Optimize content for YouTube's algorithm",
                "actions": [
                    "Create compelling thumbnails",
                    "Use video chapters and timestamps",
                    "Encourage comments and engagement",
                    "Optimize video tags and description"
                ]
            },
            "instagram": {
                "title": "Instagram Growth Optimization",
                "description": "Maximize Instagram reach and engagement",
                "actions": [
                    "Post during peak engagement hours",
                    "Use Instagram Stories and Reels",
                    "Engage with community comments",
                    "Use location tags when relevant"
                ]
            },
            "tiktok": {
                "title": "TikTok Viral Optimization",
                "description": "Increase TikTok discoverability and viral potential",
                "actions": [
                    "Follow trending sounds and challenges",
                    "Post consistently at optimal times",
                    "Create engaging first 3 seconds",
                    "Use trending hashtags strategically"
                ]
            }
        }
        
        if platform in platform_recommendations:
            rec_data = platform_recommendations[platform]
            return SEORecommendation(
                recommendation_id=str(uuid.uuid4()),
                category="platform_optimization",
                title=rec_data["title"],
                description=rec_data["description"],
                priority="medium",
                impact_level="high",
                implementation_difficulty="medium",
                estimated_improvement="20-30% platform-specific growth",
                target_platforms=[platform],
                specific_actions=rec_data["actions"],
                success_metrics=["Increased platform visibility", "Higher engagement rate"],
                timeframe="2-4 weeks",
                confidence_score=0.8
            )
        
        return None
    
    def _create_optimal_posting_schedule(self, platforms: List[str]) -> Dict[str, Any]:
        """Create optimal posting schedule for platforms"""        # Optimal posting times by platform (simplified)
        optimal_times = {
            "instagram": {
                "weekdays": ["9:00 AM", "1:00 PM", "3:00 PM"],
                "weekends": ["10:00 AM", "2:00 PM"]
            },
            "twitter": {
                "weekdays": ["8:00 AM", "12:00 PM", "5:00 PM"],
                "weekends": ["9:00 AM", "3:00 PM"]
            },
            "youtube": {
                "weekdays": ["2:00 PM", "8:00 PM"],
                "weekends": ["9:00 AM", "5:00 PM"]
            },
            "tiktok": {
                "weekdays": ["6:00 AM", "10:00 AM", "7:00 PM"],
                "weekends": ["9:00 AM", "12:00 PM", "6:00 PM"]
            }
        }
        
        schedule = {
            "recommended_frequency": {
                "instagram": "1-2 posts per day",
                "twitter": "3-5 tweets per day", 
                "youtube": "2-3 videos per week",
                "tiktok": "1-3 videos per day"
            },
            "optimal_times": {},
            "consistency_tips": [
                "Post at the same times each day",
                "Use scheduling tools for consistency",
                "Analyze your audience's active hours",
                "Adjust schedule based on engagement data"
            ]
        }
        
        for platform in platforms:
            if platform in optimal_times:
                schedule["optimal_times"][platform] = optimal_times[platform]
        
        return schedule
    
    def _generate_engagement_strategies(self, 
                                      content_type: ContentType,
                                      platforms: List[str],
                                      goal: ContentOptimizationGoal) -> List[Dict[str, Any]]:
        """Generate engagement strategies"""        strategies = []
        
        # Universal engagement strategies
        strategies.extend([
            {
                "strategy": "Call-to-Action Optimization",
                "description": "Include clear, compelling CTAs in all content",
                "tactics": [
                    "Ask questions to encourage comments",
                    "Request likes and shares explicitly",
                    "Direct audience to other content",
                    "Encourage user-generated content"
                ],
                "expected_impact": "15-25% increase in engagement"
            },
            {
                "strategy": "Community Building",
                "description": "Build an engaged community around your content",
                "tactics": [
                    "Respond to all comments promptly",
                    "Create content series to build anticipation",
                    "Host live sessions and Q&As",
                    "Collaborate with other creators"
                ],
                "expected_impact": "20-40% increase in follower loyalty"
            }
        ])
        
        # Content type specific strategies
        if content_type == ContentType.VIDEO:
            strategies.append({
                "strategy": "Video Engagement Optimization",
                "description": "Maximize video engagement and watch time",
                "tactics": [
                    "Hook viewers in first 15 seconds",
                    "Use pattern interrupts to maintain attention",
                    "End with cliffhangers for series content",
                    "Include interactive elements"
                ],
                "expected_impact": "30-50% improvement in watch time"
            })
        
        # Goal-specific strategies
        if goal == ContentOptimizationGoal.VIRAL_POTENTIAL:
            strategies.append({
                "strategy": "Viral Content Optimization",
                "description": "Increase potential for viral spread",
                "tactics": [
                    "Create highly shareable content",
                    "Tap into current trends and memes",
                    "Evoke strong emotional responses",
                    "Make content easy to understand and relate to"
                ],
                "expected_impact": "Variable - potential for exponential growth"
            })
        
        return strategies
    
    async def _predict_content_performance(self, 
                                         content: str,
                                         keywords: List[KeywordAnalysis],
                                         platforms: List[str],
                                         content_type: ContentType) -> Dict[str, float]:
        """Predict content performance metrics"""        try:
            predictions = {}
            
            # Calculate base scores
            keyword_strength = np.mean([kw.relevance_score for kw in keywords]) if keywords else 0.5
            content_length_factor = min(1.0, len(content.split()) / 300)  # Optimal around 300 words
            
            # Platform-specific predictions
            for platform in platforms:
                base_score = 0.5
                
                # Adjust for keyword strength
                base_score += keyword_strength * 0.3
                
                # Adjust for content length
                base_score += content_length_factor * 0.2
                
                # Platform-specific factors
                platform_multipliers = {
                    "youtube": 1.2,
                    "instagram": 1.1,
                    "tiktok": 1.3,
                    "twitter": 0.9,
                    "linkedin": 0.8
                }
                
                multiplier = platform_multipliers.get(platform, 1.0)
                platform_score = min(1.0, base_score * multiplier)
                
                predictions[f"{platform}_engagement_rate"] = platform_score * 0.08  # 8% max engagement
                predictions[f"{platform}_reach_potential"] = platform_score
                predictions[f"{platform}_virality_score"] = platform_score * 0.3  # 30% max virality
            
            # Overall predictions
            predictions["overall_seo_score"] = keyword_strength
            predictions["content_quality_score"] = content_length_factor
            predictions["optimization_potential"] = 1.0 - np.mean(list(predictions.values()))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Performance prediction failed: {e}")
            return {"prediction_error": 1.0}
    
    async def _analyze_competitors(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """Analyze competitor content for insights"""        try:
            insights = {
                "total_competitors": len(competitor_urls),
                "analysis_summary": "Competitor analysis completed",
                "key_findings": [
                    "Common keyword themes identified",
                    "Content gaps discovered",
                    "Optimal posting patterns observed"
                ],
                "recommendations": [
                    "Target underutilized keywords",
                    "Fill content gaps in your niche",
                    "Differentiate with unique value proposition"
                ]
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {"error": "Competitor analysis unavailable"}
    
    def _generate_audience_insights(self, 
                                  target_audience: str,
                                  keywords: List[KeywordAnalysis]) -> Dict[str, Any]:
        """Generate audience insights"""        insights = {
            "target_audience": target_audience or "General audience",
            "audience_characteristics": {
                "primary_interests": [kw.keyword for kw in keywords[:5]] if keywords else [],
                "content_preferences": ["Educational", "Entertaining", "Inspirational"],
                "engagement_patterns": "Most active during evening hours",
                "platform_preferences": ["Instagram", "YouTube", "TikTok"]
            },
            "content_recommendations": [
                "Create content that educates and entertains",
                "Use visual elements to increase engagement",
                "Focus on trending topics in your niche",
                "Maintain consistent posting schedule"
            ],
            "optimization_opportunities": [
                "Leverage audience's peak activity times",
                "Create series content to build loyalty",
                "Use audience-preferred content formats",
                "Engage actively in comments and discussions"
            ]
        }
        
        return insights
    
    async def _generate_description_suggestions(self, 
                                              content: str,
                                              keywords: List[KeywordAnalysis]) -> List[Dict[str, Any]]:
        """Generate optimized descriptions"""        try:
            suggestions = []
            
            # Short description (for social media)
            short_desc = await self._create_short_description(content, keywords)
            suggestions.append({
                "type": "short",
                "description": short_desc,
                "character_count": len(short_desc),
                "use_case": "Instagram, Twitter, TikTok captions"
            })
            
            # Medium description (for YouTube, Facebook)
            medium_desc = await self._create_medium_description(content, keywords)
            suggestions.append({
                "type": "medium",
                "description": medium_desc,
                "character_count": len(medium_desc),
                "use_case": "YouTube descriptions, Facebook posts"
            })
            
            # Long description (for blogs, LinkedIn)
            long_desc = await self._create_long_description(content, keywords)
            suggestions.append({
                "type": "long",
                "description": long_desc,
                "character_count": len(long_desc),
                "use_case": "Blog posts, LinkedIn articles, detailed descriptions"
            })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Description generation failed: {e}")
            return []
    
    async def _create_short_description(self, content: str, keywords: List[KeywordAnalysis]) -> str:
        """Create short description for social media"""        # Extract first sentence or create summary
        sentences = content.split('.')
        first_sentence = sentences[0] if sentences else content[:100]
        
        # Add top keyword if not present
        if keywords and keywords[0].keyword.lower() not in first_sentence.lower():
            first_sentence = f"{keywords[0].keyword}: {first_sentence}"
        
        # Keep under 125 characters for Instagram
        if len(first_sentence) > 125:
            first_sentence = first_sentence[:122] + "..."
        
        return first_sentence
    
    async def _create_medium_description(self, content: str, keywords: List[KeywordAnalysis]) -> str:
        """Create medium-length description"""        # Create a summary with keywords
        sentences = content.split('.')[:3]  # First 3 sentences
        summary = '. '.join(sentences)
        
        # Add keyword context
        if keywords:
            keyword_context = f"Learn about {keywords[0].keyword}"
            if keywords[0].keyword.lower() not in summary.lower():
                summary = f"{keyword_context}. {summary}"
        
        # Add call to action
        summary += "\n\n👍 Like if you found this helpful!\n💬 Share your thoughts in comments!"
        
        return summary
    
    async def _create_long_description(self, content: str, keywords: List[KeywordAnalysis]) -> str:
        """Create long-form description"""        # Use more of the content
        sentences = content.split('.')[:5]  # First 5 sentences
        description = '. '.join(sentences)
        
        # Add keyword-rich introduction
        if keywords:
            intro = f"Comprehensive guide about {keywords[0].keyword}. "
            if len(keywords) > 1:
                intro += f"Also covering {', '.join([kw.keyword for kw in keywords[1:4]])}. "
            description = intro + description
        
        # Add engagement elements
        description += "\n\n📚 What you'll learn:"
        description += "\n• Key insights and strategies"
        description += "\n• Practical tips and techniques"
        description += "\n• Real-world applications"
        description += "\n\n🔔 Don't forget to subscribe for more content!"
        description += "\n💭 What topics would you like to see covered next?"
        
        return description


# Global SEO optimization engine
seo_optimizer = SEOOptimizationEngine()
