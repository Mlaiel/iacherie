"""Trend Analyzer
==============

Advanced trend detection and social media analytics system.
Implements real-time trend monitoring and predictive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
from collections import Counter, defaultdict
import json
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd

logger = logging.getLogger(__name__)

class TrendCategory(Enum):
    """Trend category types."""    VIRAL_CONTENT = "viral_content"
    HASHTAG_TREND = "hashtag_trend"
    TOPIC_TREND = "topic_trend"
    CELEBRITY_TREND = "celebrity_trend"
    BRAND_TREND = "brand_trend"
    EVENT_TREND = "event_trend"
    MUSIC_TREND = "music_trend"
    TECHNOLOGY_TREND = "technology_trend"
    SPORTS_TREND = "sports_trend"
    NEWS_TREND = "news_trend"
    MEME_TREND = "meme_trend"
    FASHION_TREND = "fashion_trend"

class TrendVelocity(Enum):
    """Trend velocity levels."""    EXPLOSIVE = "explosive"      # Sudden spike
    RAPID = "rapid"             # Fast growth
    STEADY = "steady"           # Consistent growth
    SLOW = "slow"               # Gradual growth
    DECLINING = "declining"     # Decreasing
    STABLE = "stable"           # Plateaued

class TrendScope(Enum):
    """Trend geographical scope."""    GLOBAL = "global"
    CONTINENTAL = "continental"
    NATIONAL = "national"
    REGIONAL = "regional"
    LOCAL = "local"
    NICHE = "niche"

@dataclass
class TrendMetrics:
    """Trend analysis metrics."""    volume: int                     # Number of mentions/posts
    engagement_rate: float          # Average engagement per post
    reach_estimate: int            # Estimated total reach
    velocity: TrendVelocity        # Growth velocity
    acceleration: float            # Change in velocity
    virality_coefficient: float    # Virality measure
    
    # Time-based metrics
    peak_time: Optional[datetime] = None
    duration_hours: float = 0.0
    growth_rate_hourly: float = 0.0
    
    # Social metrics
    unique_users: int = 0
    influencer_participation: float = 0.0
    cross_platform_presence: float = 0.0
    
    # Quality metrics
    sentiment_score: float = 0.0
    authenticity_score: float = 0.0  # Bot detection
    spam_ratio: float = 0.0

@dataclass
class TrendItem:
    """Individual trending item."""    trend_id: str
    keyword: str
    category: TrendCategory
    scope: TrendScope
    metrics: TrendMetrics
    
    # Content analysis
    related_keywords: List[str] = field(default_factory=list)
    sample_content: List[str] = field(default_factory=list)
    dominant_language: str = "en"
    
    # Temporal data
    first_detected: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    prediction_confidence: float = 0.0
    
    # Context
    trigger_events: List[str] = field(default_factory=list)
    related_trends: List[str] = field(default_factory=list)
    demographics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrendAnalysisResult:
    """Complete trend analysis result."""    content_id: str
    detected_trends: List[TrendItem]
    
    # Content trend scoring
    trend_participation_score: float = 0.0
    trend_originality_score: float = 0.0
    trend_timing_score: float = 0.0
    viral_potential_score: float = 0.0
    
    # Recommendations
    recommended_hashtags: List[str] = field(default_factory=list)
    optimal_posting_time: Optional[datetime] = None
    trend_recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    data_freshness: float = 0.0  # How recent is the trend data

class TrendAnalyzer:
    """    Advanced trend detection and social media analytics system.
    
    Features:
    - Real-time trend detection across multiple platforms
    - Predictive trend analytics with ML
    - Viral potential assessment
    - Topic modeling and clustering
    - Temporal trend analysis
    - Geographic trend mapping
    - Influencer trend participation tracking
    - Bot and spam detection
    """    
    def __init__(
        self,
        enable_realtime: bool = True,
        trend_window_hours: int = 24,
        min_volume_threshold: int = 100,
        enable_predictive: bool = True
    ):
        """        Initialize trend analyzer.
        
        Args:
            enable_realtime: Enable real-time trend monitoring
            trend_window_hours: Time window for trend analysis
            min_volume_threshold: Minimum volume to consider as trend
            enable_predictive: Enable predictive trend analytics
        """        self.enable_realtime = enable_realtime
        self.trend_window_hours = trend_window_hours
        self.min_volume_threshold = min_volume_threshold
        self.enable_predictive = enable_predictive
        
        # Trend tracking
        self.active_trends = {}
        self.trend_history = []
        self.keyword_mentions = defaultdict(list)
        self.hashtag_mentions = defaultdict(list)
        
        # Analytics
        self.analysis_count = 0
        self.trend_detection_count = 0
        self.processing_times = []
        
        # ML models
        self.topic_model = None
        self.clustering_model = None
        self.tfidf_vectorizer = None
        
        # Initialize components
        self._initialize_trend_keywords()
        self._initialize_ml_models()
        
        logger.info(f"TrendAnalyzer initialized with {trend_window_hours}h window")
    
    def _initialize_trend_keywords(self) -> None:
        """Initialize trending keywords and patterns."""        self.trend_keywords = {
            TrendCategory.VIRAL_CONTENT: [
                'viral', 'trending', 'going viral', 'breaking the internet',
                'everyone is talking about', 'viral sensation', 'internet famous'
            ],
            TrendCategory.HASHTAG_TREND: [
                'trending hashtag', 'viral hashtag', 'new hashtag',
                'hashtag challenge', 'tag yourself', 'hashtag game'
            ],
            TrendCategory.CELEBRITY_TREND: [
                'celebrity', 'famous', 'star', 'actor', 'singer', 'influencer',
                'red carpet', 'award show', 'premiere', 'scandal'
            ],
            TrendCategory.MUSIC_TREND: [
                'new song', 'hit song', 'chart topper', 'music video',
                'album release', 'concert', 'festival', 'dance challenge'
            ],
            TrendCategory.TECHNOLOGY_TREND: [
                'new tech', 'innovation', 'breakthrough', 'ai', 'artificial intelligence',
                'blockchain', 'crypto', 'metaverse', 'vr', 'ar'
            ],
            TrendCategory.SPORTS_TREND: [
                'championship', 'playoffs', 'world cup', 'olympics',
                'record breaking', 'victory', 'defeat', 'trade'
            ],
            TrendCategory.NEWS_TREND: [
                'breaking news', 'developing story', 'headlines',
                'crisis', 'politics', 'election', 'announcement'
            ],
            TrendCategory.MEME_TREND: [
                'meme', 'funny', 'hilarious', 'joke', 'comedy',
                'viral video', 'reaction', 'parody', 'satire'
            ]
        }
        
        # Platform-specific patterns
        self.platform_patterns = {
            'twitter': r'#\w+|@\w+|\b(RT|via)\b',
            'instagram': r'#\w+|@\w+',
            'tiktok': r'#\w+|@\w+|\b(fyp|foryou|viral)\b',
            'youtube': r'#\w+|\b(subscribe|like|comment)\b'
        }
        
        # Time-sensitive keywords
        self.temporal_keywords = {
            'now': ['now', 'right now', 'currently', 'at the moment'],
            'urgent': ['urgent', 'breaking', 'alert', 'emergency'],
            'new': ['new', 'latest', 'fresh', 'just dropped', 'recently'],
            'hot': ['hot', 'trending', 'popular', 'buzzing', 'viral']
        }
    
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for trend analysis."""        try:
            # TF-IDF vectorizer for text analysis
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.95
            )
            
            # Topic modeling
            self.topic_model = LatentDirichletAllocation(
                n_components=20,
                random_state=42,
                max_iter=10
            )
            
            # Clustering for trend grouping
            self.clustering_model = KMeans(
                n_clusters=10,
                random_state=42,
                n_init=10
            )
            
            logger.info("ML models initialized for trend analysis")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def analyze_trends(
        self,
        content_id: str,
        text_content: str,
        metadata: Optional[Dict[str, Any]] = None,
        platform: str = "general"
    ) -> TrendAnalysisResult:
        """        Analyze trends in content and detect trending elements.
        
        Args:
            content_id: Unique content identifier
            text_content: Content text to analyze
            metadata: Additional content metadata
            platform: Platform where content appears
            
        Returns:
            TrendAnalysisResult: Complete trend analysis
        """        start_time = datetime.now()
        
        try:
            metadata = metadata or {}
            
            # Extract trending elements
            hashtags = self._extract_hashtags(text_content)
            mentions = self._extract_mentions(text_content)
            keywords = self._extract_keywords(text_content)
            
            # Update mention tracking
            timestamp = datetime.now()
            self._update_mention_tracking(hashtags, mentions, keywords, timestamp)
            
            # Detect active trends
            detected_trends = await self._detect_trends(
                text_content, hashtags, mentions, keywords, platform
            )
            
            # Calculate trend scores
            trend_participation_score = self._calculate_trend_participation(detected_trends, hashtags)
            trend_originality_score = self._calculate_trend_originality(keywords, hashtags)
            trend_timing_score = self._calculate_trend_timing(detected_trends)
            viral_potential_score = self._calculate_viral_potential(
                text_content, detected_trends, metadata
            )
            
            # Generate recommendations
            recommended_hashtags = self._recommend_hashtags(keywords, detected_trends)
            optimal_posting_time = self._calculate_optimal_timing(detected_trends)
            trend_recommendations = self._generate_trend_recommendations(detected_trends)
            
            # Calculate data freshness
            data_freshness = self._calculate_data_freshness()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_times.append(processing_time)
            
            result = TrendAnalysisResult(
                content_id=content_id,
                detected_trends=detected_trends,
                trend_participation_score=trend_participation_score,
                trend_originality_score=trend_originality_score,
                trend_timing_score=trend_timing_score,
                viral_potential_score=viral_potential_score,
                recommended_hashtags=recommended_hashtags,
                optimal_posting_time=optimal_posting_time,
                trend_recommendations=trend_recommendations,
                processing_time=processing_time,
                data_freshness=data_freshness
            )
            
            # Update analytics
            self.analysis_count += 1
            self.trend_detection_count += len(detected_trends)
            
            logger.info(f"Trend analysis completed for {content_id}: {len(detected_trends)} trends detected")
            return result
            
        except Exception as e:
            logger.error(f"Trend analysis failed for {content_id}: {e}")
            
            return TrendAnalysisResult(
                content_id=content_id,
                detected_trends=[],
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _detect_trends(
        self,
        text_content: str,
        hashtags: List[str],
        mentions: List[str],
        keywords: List[str],
        platform: str
    ) -> List[TrendItem]:
        """Detect active trends in content."""        detected_trends = []
        
        try:
            # Hashtag trend detection
            for hashtag in hashtags:
                trend_item = await self._analyze_hashtag_trend(hashtag, platform)
                if trend_item:
                    detected_trends.append(trend_item)
            
            # Keyword trend detection
            for keyword in keywords[:10]:  # Limit to top 10 keywords
                trend_item = await self._analyze_keyword_trend(keyword, text_content)
                if trend_item:
                    detected_trends.append(trend_item)
            
            # Topic trend detection
            topic_trends = await self._detect_topic_trends(text_content)
            detected_trends.extend(topic_trends)
            
            # Viral content detection
            viral_trend = await self._detect_viral_content(text_content, hashtags)
            if viral_trend:
                detected_trends.append(viral_trend)
            
            # Remove duplicates and sort by confidence
            detected_trends = self._deduplicate_trends(detected_trends)
            detected_trends.sort(key=lambda x: x.prediction_confidence, reverse=True)
            
            return detected_trends[:20]  # Return top 20 trends
            
        except Exception as e:
            logger.error(f"Trend detection failed: {e}")
            return []
    
    async def _analyze_hashtag_trend(self, hashtag: str, platform: str) -> Optional[TrendItem]:
        """Analyze if a hashtag is trending."""        try:
            # Get hashtag mention history
            mentions = self.hashtag_mentions.get(hashtag.lower(), [])
            
            if len(mentions) < 5:  # Not enough data
                return None
            
            # Calculate trend metrics
            recent_mentions = [m for m in mentions 
                             if m > datetime.now() - timedelta(hours=self.trend_window_hours)]
            
            if len(recent_mentions) < self.min_volume_threshold:
                return None
            
            # Calculate velocity
            velocity = self._calculate_velocity(recent_mentions)
            
            # Estimate metrics
            volume = len(recent_mentions)
            engagement_rate = 0.05  # Default estimate
            reach_estimate = volume * 50  # Rough estimate
            
            metrics = TrendMetrics(
                volume=volume,
                engagement_rate=engagement_rate,
                reach_estimate=reach_estimate,
                velocity=velocity,
                acceleration=0.0,  # Would need more historical data
                virality_coefficient=min(1.0, volume / 1000),
                unique_users=int(volume * 0.8),  # Estimate
                growth_rate_hourly=len(recent_mentions) / max(1, self.trend_window_hours)
            )
            
            trend_id = hashlib.md5(f"hashtag_{hashtag}_{platform}".encode()).hexdigest()[:16]
            
            return TrendItem(
                trend_id=trend_id,
                keyword=hashtag,
                category=TrendCategory.HASHTAG_TREND,
                scope=TrendScope.GLOBAL,  # Default
                metrics=metrics,
                related_keywords=[hashtag],
                dominant_language="en",  # Default
                prediction_confidence=min(1.0, volume / 500)
            )
            
        except Exception as e:
            logger.debug(f"Hashtag trend analysis failed for {hashtag}: {e}")
            return None
    
    async def _analyze_keyword_trend(self, keyword: str, context: str) -> Optional[TrendItem]:
        """Analyze if a keyword is trending."""        try:
            # Get keyword mention history
            mentions = self.keyword_mentions.get(keyword.lower(), [])
            
            if len(mentions) < 10:  # Not enough data
                return None
            
            recent_mentions = [m for m in mentions 
                             if m > datetime.now() - timedelta(hours=self.trend_window_hours)]
            
            if len(recent_mentions) < self.min_volume_threshold:
                return None
            
            # Determine category based on keyword
            category = self._categorize_keyword(keyword, context)
            
            # Calculate metrics
            velocity = self._calculate_velocity(recent_mentions)
            volume = len(recent_mentions)
            
            metrics = TrendMetrics(
                volume=volume,
                engagement_rate=0.04,  # Default estimate
                reach_estimate=volume * 30,
                velocity=velocity,
                acceleration=0.0,
                virality_coefficient=min(1.0, volume / 1500),
                unique_users=int(volume * 0.7),
                growth_rate_hourly=len(recent_mentions) / max(1, self.trend_window_hours)
            )
            
            trend_id = hashlib.md5(f"keyword_{keyword}".encode()).hexdigest()[:16]
            
            return TrendItem(
                trend_id=trend_id,
                keyword=keyword,
                category=category,
                scope=TrendScope.GLOBAL,
                metrics=metrics,
                related_keywords=[keyword],
                prediction_confidence=min(1.0, volume / 800)
            )
            
        except Exception as e:
            logger.debug(f"Keyword trend analysis failed for {keyword}: {e}")
            return None
    
    async def _detect_topic_trends(self, text_content: str) -> List[TrendItem]:
        """Detect trending topics using topic modeling."""        try:
            if not self.topic_model or len(text_content.split()) < 10:
                return []
            
            # Simple topic detection based on keyword clusters
            words = text_content.lower().split()
            
            # Technology topics
            tech_words = {'ai', 'artificial', 'intelligence', 'blockchain', 'crypto', 'nft', 'metaverse'}
            tech_count = sum(1 for word in words if word in tech_words)
            
            if tech_count >= 2:
                trend_id = hashlib.md5(f"topic_technology_{datetime.now().date()}".encode()).hexdigest()[:16]
                
                metrics = TrendMetrics(
                    volume=tech_count * 100,  # Estimate
                    engagement_rate=0.06,
                    reach_estimate=tech_count * 1000,
                    velocity=TrendVelocity.STEADY,
                    virality_coefficient=0.3
                )
                
                return [TrendItem(
                    trend_id=trend_id,
                    keyword="technology_trend",
                    category=TrendCategory.TECHNOLOGY_TREND,
                    scope=TrendScope.GLOBAL,
                    metrics=metrics,
                    related_keywords=list(tech_words & set(words)),
                    prediction_confidence=0.7
                )]
            
            return []
            
        except Exception as e:
            logger.debug(f"Topic trend detection failed: {e}")
            return []
    
    async def _detect_viral_content(self, text_content: str, hashtags: List[str]) -> Optional[TrendItem]:
        """Detect if content has viral characteristics."""        try:
            viral_indicators = []
            
            # Check for viral keywords
            viral_keywords = {'viral', 'trending', 'breaking', 'everyone', 'omg', 'wow', 'amazing'}
            text_lower = text_content.lower()
            viral_keyword_count = sum(1 for keyword in viral_keywords if keyword in text_lower)
            viral_indicators.append(viral_keyword_count)
            
            # Check for emotional intensity
            exclamation_count = text_content.count('!')
            caps_ratio = sum(1 for c in text_content if c.isupper()) / max(1, len(text_content))
            viral_indicators.extend([min(1, exclamation_count / 3), caps_ratio * 5])
            
            # Check for hashtag density
            hashtag_density = len(hashtags) / max(1, len(text_content.split()) / 10)
            viral_indicators.append(min(1, hashtag_density))
            
            # Calculate viral score
            viral_score = np.mean(viral_indicators)
            
            if viral_score > 0.3:  # Threshold for viral content
                trend_id = hashlib.md5(f"viral_{text_content[:50]}".encode()).hexdigest()[:16]
                
                metrics = TrendMetrics(
                    volume=int(viral_score * 1000),
                    engagement_rate=viral_score * 0.1,
                    reach_estimate=int(viral_score * 10000),
                    velocity=TrendVelocity.EXPLOSIVE if viral_score > 0.7 else TrendVelocity.RAPID,
                    virality_coefficient=viral_score
                )
                
                return TrendItem(
                    trend_id=trend_id,
                    keyword="viral_content",
                    category=TrendCategory.VIRAL_CONTENT,
                    scope=TrendScope.GLOBAL,
                    metrics=metrics,
                    prediction_confidence=viral_score
                )
            
            return None
            
        except Exception as e:
            logger.debug(f"Viral content detection failed: {e}")
            return None
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""        hashtags = re.findall(r'#(\w+)', text)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""        mentions = re.findall(r'@(\w+)', text)
        return [mention.lower() for mention in mentions]
    
    def _extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract keywords from text."""        # Remove stop words and extract meaningful keywords
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'a', 'an', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Count frequency and return most common
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _update_mention_tracking(
        self,
        hashtags: List[str],
        mentions: List[str],
        keywords: List[str],
        timestamp: datetime
    ) -> None:
        """Update mention tracking for trend detection."""        # Update hashtag mentions
        for hashtag in hashtags:
            self.hashtag_mentions[hashtag].append(timestamp)
        
        # Update keyword mentions
        for keyword in keywords:
            self.keyword_mentions[keyword].append(timestamp)
        
        # Cleanup old mentions (keep only recent data)
        cutoff_time = timestamp - timedelta(days=7)
        
        for hashtag in list(self.hashtag_mentions.keys()):
            self.hashtag_mentions[hashtag] = [
                t for t in self.hashtag_mentions[hashtag] if t > cutoff_time
            ]
            if not self.hashtag_mentions[hashtag]:
                del self.hashtag_mentions[hashtag]
        
        for keyword in list(self.keyword_mentions.keys()):
            self.keyword_mentions[keyword] = [
                t for t in self.keyword_mentions[keyword] if t > cutoff_time
            ]
            if not self.keyword_mentions[keyword]:
                del self.keyword_mentions[keyword]
    
    def _calculate_velocity(self, timestamps: List[datetime]) -> TrendVelocity:
        """Calculate trend velocity based on timestamps."""        if len(timestamps) < 2:
            return TrendVelocity.STABLE
        
        # Sort timestamps
        sorted_times = sorted(timestamps)
        
        # Calculate time intervals
        intervals = [
            (sorted_times[i] - sorted_times[i-1]).total_seconds() / 3600
            for i in range(1, len(sorted_times))
        ]
        
        # Calculate average interval
        avg_interval = np.mean(intervals)
        
        # Determine velocity
        if avg_interval < 0.5:  # Less than 30 minutes
            return TrendVelocity.EXPLOSIVE
        elif avg_interval < 2:   # Less than 2 hours
            return TrendVelocity.RAPID
        elif avg_interval < 6:   # Less than 6 hours
            return TrendVelocity.STEADY
        elif avg_interval < 24:  # Less than 24 hours
            return TrendVelocity.SLOW
        else:
            return TrendVelocity.STABLE
    
    def _categorize_keyword(self, keyword: str, context: str) -> TrendCategory:
        """Categorize keyword into trend category."""        keyword_lower = keyword.lower()
        context_lower = context.lower()
        
        # Check against category keywords
        for category, keywords in self.trend_keywords.items():
            if any(kw in keyword_lower or kw in context_lower for kw in keywords):
                return category
        
        # Default categorization
        if any(word in keyword_lower for word in ['music', 'song', 'album', 'artist']):
            return TrendCategory.MUSIC_TREND
        elif any(word in keyword_lower for word in ['tech', 'ai', 'crypto', 'blockchain']):
            return TrendCategory.TECHNOLOGY_TREND
        elif any(word in keyword_lower for word in ['sport', 'game', 'match', 'team']):
            return TrendCategory.SPORTS_TREND
        elif any(word in keyword_lower for word in ['news', 'politics', 'election']):
            return TrendCategory.NEWS_TREND
        elif any(word in keyword_lower for word in ['meme', 'funny', 'joke']):
            return TrendCategory.MEME_TREND
        else:
            return TrendCategory.TOPIC_TREND
    
    def _deduplicate_trends(self, trends: List[TrendItem]) -> List[TrendItem]:
        """Remove duplicate trends based on similarity."""        if not trends:
            return []
        
        deduplicated = []
        seen_keywords = set()
        
        for trend in trends:
            keyword_lower = trend.keyword.lower()
            
            # Check for exact duplicates
            if keyword_lower in seen_keywords:
                continue
            
            # Check for similar keywords (simple similarity)
            is_similar = False
            for seen_keyword in seen_keywords:
                if (keyword_lower in seen_keyword or seen_keyword in keyword_lower) and \
                   abs(len(keyword_lower) - len(seen_keyword)) <= 3:
                    is_similar = True
                    break
            
            if not is_similar:
                deduplicated.append(trend)
                seen_keywords.add(keyword_lower)
        
        return deduplicated
    
    def _calculate_trend_participation(self, trends: List[TrendItem], hashtags: List[str]) -> float:
        """Calculate how much the content participates in current trends."""        if not trends:
            return 0.0
        
        participation_scores = []
        
        for trend in trends:
            # Check if content uses trending hashtags
            hashtag_participation = any(
                hashtag in trend.keyword.lower() for hashtag in hashtags
            )
            
            if hashtag_participation:
                participation_scores.append(trend.prediction_confidence)
            else:
                participation_scores.append(trend.prediction_confidence * 0.5)
        
        return np.mean(participation_scores) if participation_scores else 0.0
    
    def _calculate_trend_originality(self, keywords: List[str], hashtags: List[str]) -> float:
        """Calculate content originality vs trend following."""        if not keywords and not hashtags:
            return 0.5
        
        all_terms = keywords + hashtags
        unique_terms = len(set(all_terms))
        total_terms = len(all_terms)
        
        # Higher uniqueness ratio = higher originality
        uniqueness_ratio = unique_terms / max(1, total_terms)
        
        # Check against common trending terms
        common_trending = {'viral', 'trending', 'breaking', 'new', 'hot', 'latest'}
        common_count = sum(1 for term in all_terms if term.lower() in common_trending)
        
        # Lower common term usage = higher originality
        originality_factor = max(0.0, 1.0 - (common_count / max(1, len(all_terms))))
        
        return (uniqueness_ratio + originality_factor) / 2
    
    def _calculate_trend_timing(self, trends: List[TrendItem]) -> float:
        """Calculate timing score based on trend lifecycle stage."""        if not trends:
            return 0.5
        
        timing_scores = []
        
        for trend in trends:
            # Estimate trend lifecycle stage based on velocity
            if trend.metrics.velocity == TrendVelocity.EXPLOSIVE:
                # Early stage - good timing
                timing_scores.append(0.9)
            elif trend.metrics.velocity == TrendVelocity.RAPID:
                # Growth stage - good timing
                timing_scores.append(0.8)
            elif trend.metrics.velocity == TrendVelocity.STEADY:
                # Peak stage - moderate timing
                timing_scores.append(0.6)
            elif trend.metrics.velocity == TrendVelocity.SLOW:
                # Late stage - poor timing
                timing_scores.append(0.3)
            else:
                # Declining/stable - poor timing
                timing_scores.append(0.2)
        
        return np.mean(timing_scores)
    
    def _calculate_viral_potential(
        self,
        text_content: str,
        trends: List[TrendItem],
        metadata: Dict[str, Any]
    ) -> float:
        """Calculate viral potential score."""        factors = []
        
        # Trend participation factor
        if trends:
            max_trend_confidence = max(trend.prediction_confidence for trend in trends)
            factors.append(max_trend_confidence)
        else:
            factors.append(0.2)
        
        # Content characteristics
        text_length = len(text_content.split())
        if 10 <= text_length <= 50:
            factors.append(0.8)  # Optimal length for virality
        elif text_length < 10:
            factors.append(0.4)  # Too short
        else:
            factors.append(0.6)  # Might be too long
        
        # Emotional content
        emotional_words = {'amazing', 'incredible', 'unbelievable', 'shocking', 'wow'}
        emotional_count = sum(1 for word in emotional_words if word in text_content.lower())
        factors.append(min(1.0, emotional_count * 0.3))
        
        # Visual content indicator
        has_visual = metadata.get('has_image', False) or metadata.get('has_video', False)
        factors.append(0.8 if has_visual else 0.4)
        
        # Call to action
        cta_words = {'share', 'retweet', 'tag', 'comment', 'like', 'follow'}
        cta_count = sum(1 for word in cta_words if word in text_content.lower())
        factors.append(min(1.0, cta_count * 0.4))
        
        return np.mean(factors)
    
    def _recommend_hashtags(
        self,
        keywords: List[str],
        trends: List[TrendItem],
        max_recommendations: int = 10
    ) -> List[str]:
        """Recommend hashtags based on content and trends."""        recommendations = []
        
        # Add trending hashtags
        for trend in trends:
            if trend.category == TrendCategory.HASHTAG_TREND:
                recommendations.append(f"#{trend.keyword}")
        
        # Add keyword-based hashtags
        for keyword in keywords[:5]:
            recommendations.append(f"#{keyword}")
        
        # Add category-based trending hashtags
        trending_hashtags = [
            "#viral", "#trending", "#new", "#hot", "#popular",
            "#content", "#creator", "#amazing", "#mustwatch"
        ]
        
        recommendations.extend(trending_hashtags)
        
        # Remove duplicates and return limited results
        seen = set()
        unique_recommendations = []
        for hashtag in recommendations:
            if hashtag.lower() not in seen:
                unique_recommendations.append(hashtag)
                seen.add(hashtag.lower())
        
        return unique_recommendations[:max_recommendations]
    
    def _calculate_optimal_timing(self, trends: List[TrendItem]) -> Optional[datetime]:
        """Calculate optimal posting time based on trends."""        if not trends:
            return None
        
        # Simple heuristic: recommend posting during peak social media hours
        now = datetime.now()
        
        # Peak hours: 6-9 AM, 12-1 PM, 7-9 PM
        peak_hours = [7, 8, 12, 19, 20]
        
        next_peak = None
        for hour in peak_hours:
            potential_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if potential_time > now:
                next_peak = potential_time
                break
        
        if not next_peak:
            # Next day's first peak
            next_peak = (now + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        
        return next_peak
    
    def _generate_trend_recommendations(self, trends: List[TrendItem]) -> List[str]:
        """Generate trend-based content recommendations."""        recommendations = []
        
        if not trends:
            return ["Create original content to start new trends"]
        
        for trend in trends[:5]:  # Top 5 trends
            if trend.category == TrendCategory.VIRAL_CONTENT:
                recommendations.append(f"Join the viral trend around '{trend.keyword}'")
            elif trend.category == TrendCategory.HASHTAG_TREND:
                recommendations.append(f"Use trending hashtag #{trend.keyword}")
            elif trend.category == TrendCategory.MUSIC_TREND:
                recommendations.append(f"Create content around trending music: {trend.keyword}")
            elif trend.category == TrendCategory.TECHNOLOGY_TREND:
                recommendations.append(f"Discuss trending tech topic: {trend.keyword}")
            else:
                recommendations.append(f"Engage with trending topic: {trend.keyword}")
        
        # Add timing recommendations
        if any(trend.metrics.velocity == TrendVelocity.EXPLOSIVE for trend in trends):
            recommendations.append("Act fast - explosive trends detected!")
        
        return recommendations[:10]
    
    def _calculate_data_freshness(self) -> float:
        """Calculate how fresh the trend data is."""        # Simple metric based on recent analysis activity
        recent_analyses = [
            t for t in self.processing_times[-100:] 
            if t is not None
        ]
        
        if len(recent_analyses) > 50:
            return 1.0  # Very fresh
        elif len(recent_analyses) > 20:
            return 0.8  # Fresh
        elif len(recent_analyses) > 5:
            return 0.6  # Moderately fresh
        else:
            return 0.3  # Stale
    
    async def get_trending_topics(
        self,
        category: Optional[TrendCategory] = None,
        scope: Optional[TrendScope] = None,
        limit: int = 20
    ) -> List[TrendItem]:
        """Get current trending topics with optional filtering."""        try:
            # For now, return simulated trending topics
            # In real implementation, this would query the trend database
            
            current_trends = []
            
            # Generate some sample trends based on current data
            for keyword, mentions in list(self.keyword_mentions.items())[:limit]:
                if len(mentions) >= self.min_volume_threshold:
                    
                    velocity = self._calculate_velocity(mentions)
                    
                    metrics = TrendMetrics(
                        volume=len(mentions),
                        engagement_rate=0.05,
                        reach_estimate=len(mentions) * 50,
                        velocity=velocity,
                        virality_coefficient=min(1.0, len(mentions) / 1000)
                    )
                    
                    trend_category = self._categorize_keyword(keyword, "")
                    
                    # Apply filters
                    if category and trend_category != category:
                        continue
                    
                    trend_id = hashlib.md5(f"trending_{keyword}".encode()).hexdigest()[:16]
                    
                    trend_item = TrendItem(
                        trend_id=trend_id,
                        keyword=keyword,
                        category=trend_category,
                        scope=scope or TrendScope.GLOBAL,
                        metrics=metrics,
                        prediction_confidence=min(1.0, len(mentions) / 500)
                    )
                    
                    current_trends.append(trend_item)
            
            # Sort by volume and confidence
            current_trends.sort(
                key=lambda x: (x.metrics.volume, x.prediction_confidence),
                reverse=True
            )
            
            return current_trends[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get trending topics: {e}")
            return []
    
    async def predict_trend_future(
        self,
        trend_id: str,
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """Predict trend future performance."""        try:
            # Simple trend prediction based on current velocity
            # In real implementation, this would use ML models
            
            prediction = {
                "trend_id": trend_id,
                "hours_ahead": hours_ahead,
                "predicted_volume_change": 0.0,
                "predicted_peak_time": None,
                "confidence": 0.0,
                "recommendation": "monitor"
            }
            
            # Find trend in current data
            trend_found = False
            for keyword, mentions in self.keyword_mentions.items():
                if hashlib.md5(f"trending_{keyword}".encode()).hexdigest()[:16] == trend_id:
                    trend_found = True
                    
                    if len(mentions) >= 2:
                        # Calculate growth rate
                        recent_mentions = sorted(mentions)[-10:]  # Last 10 mentions
                        time_span = (recent_mentions[-1] - recent_mentions[0]).total_seconds() / 3600
                        growth_rate = len(recent_mentions) / max(1, time_span)
                        
                        # Predict future volume
                        predicted_volume = growth_rate * hours_ahead
                        current_volume = len([m for m in mentions 
                                            if m > datetime.now() - timedelta(hours=24)])
                        
                        volume_change = (predicted_volume - current_volume) / max(1, current_volume)
                        
                        prediction.update({
                            "predicted_volume_change": volume_change,
                            "predicted_peak_time": datetime.now() + timedelta(hours=hours_ahead/2),
                            "confidence": min(1.0, len(mentions) / 100),
                            "recommendation": "invest" if volume_change > 0.5 else "monitor"
                        })
                    
                    break
            
            if not trend_found:
                prediction["recommendation"] = "trend_not_found"
            
            return prediction
            
        except Exception as e:
            logger.error(f"Trend prediction failed for {trend_id}: {e}")
            return {
                "trend_id": trend_id,
                "error": str(e),
                "recommendation": "error"
            }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get trend analysis analytics and performance metrics."""        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        # Calculate trend categories distribution
        trend_categories = {}
        for trends in []:  # Would iterate through stored trends
            # This would be implemented with proper trend storage
            pass
        
        return {
            "total_analyses": self.analysis_count,
            "total_trends_detected": self.trend_detection_count,
            "average_processing_time": avg_processing_time,
            "active_trends_count": len(self.active_trends),
            "tracked_keywords": len(self.keyword_mentions),
            "tracked_hashtags": len(self.hashtag_mentions),
            "trend_window_hours": self.trend_window_hours,
            "min_volume_threshold": self.min_volume_threshold,
            "realtime_enabled": self.enable_realtime,
            "predictive_enabled": self.enable_predictive,
            "processing_time_percentiles": {
                "p50": np.percentile(self.processing_times, 50) if self.processing_times else 0,
                "p90": np.percentile(self.processing_times, 90) if self.processing_times else 0,
                "p99": np.percentile(self.processing_times, 99) if self.processing_times else 0
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and clear caches."""        # Clear tracking data
        self.active_trends.clear()
        self.trend_history.clear()
        self.keyword_mentions.clear()
        self.hashtag_mentions.clear()
        
        # Clear analytics
        self.processing_times.clear()
        
        logger.info("TrendAnalyzer cleanup completed")
