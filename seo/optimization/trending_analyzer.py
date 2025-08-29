"""
Trending Analyzer - AI-Powered Trending Content Analysis

This module provides intelligent analysis of trending content, topics, and keywords
across different platforms and industries with real-time trend detection and prediction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TrendType(Enum):
    """Types of trends"""
    VIRAL = "viral"
    EMERGING = "emerging"
    SEASONAL = "seasonal"
    SUSTAINED = "sustained"
    DECLINING = "declining"
    CYCLICAL = "cyclical"


class Platform(Enum):
    """Platforms for trend analysis"""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    REDDIT = "reddit"


class TimeFrame(Enum):
    """Time frames for trend analysis"""
    HOUR = "1h"
    DAY = "24h"
    WEEK = "7d"
    MONTH = "30d"
    QUARTER = "90d"
    YEAR = "365d"


@dataclass
class TrendMetrics:
    """Metrics for a trending topic"""
    volume: int
    growth_rate: float  # Percentage growth
    velocity: float  # Rate of change
    engagement_rate: float
    reach: int
    sentiment_score: float  # -1 to 1
    virality_index: float  # 0 to 100


@dataclass
class TrendingTopic:
    """Individual trending topic"""
    topic: str
    trend_type: TrendType
    platforms: List[Platform]
    metrics: TrendMetrics
    related_keywords: List[str]
    hashtags: List[str]
    peak_time: str
    predicted_duration: int  # Hours
    confidence_score: float


@dataclass
class TrendAnalysis:
    """Complete trend analysis result"""
    trending_topics: List[TrendingTopic]
    emerging_trends: List[TrendingTopic]
    declining_trends: List[TrendingTopic]
    seasonal_predictions: List[TrendingTopic]
    platform_trends: Dict[Platform, List[str]]
    industry_trends: Dict[str, List[str]]
    recommendation_score: float
    analysis_timestamp: str


class TrendingAnalyzer:
    """
    AI-powered trending content analyzer that identifies, analyzes, and predicts
    trending topics and content patterns across multiple platforms and industries.
    """

    def __init__(self, region: str = "US", industry: str = "general"):
        """
        Initialize the trending analyzer.
        
        Args:
            region: Target region for trend analysis
            industry: Primary industry focus
        """
        self.region = region
        self.industry = industry
        self.trend_data = self._initialize_trend_data()
        self.seasonal_patterns = self._initialize_seasonal_patterns()
        self.platform_weights = self._initialize_platform_weights()

    def analyze_trending_content(
        self,
        content: str = "",
        keywords: List[str] = None,
        target_platforms: List[Platform] = None,
        time_frame: TimeFrame = TimeFrame.DAY,
        include_predictions: bool = True,
        min_confidence: float = 0.6
    ) -> TrendAnalysis:
        """
        Analyze trending content and identify opportunities.
        
        Args:
            content: Content to analyze against trends
            keywords: Keywords to track for trending
            target_platforms: Platforms to analyze
            time_frame: Time frame for trend analysis
            include_predictions: Whether to include trend predictions
            min_confidence: Minimum confidence score for trends
            
        Returns:
            TrendAnalysis with comprehensive trend insights
        """
        try:
            logger.info(f"Starting trend analysis for {time_frame.value} timeframe")
            
            if target_platforms is None:
                target_platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.TIKTOK, Platform.YOUTUBE]
            
            if keywords is None:
                keywords = self._extract_keywords_from_content(content)
            
            # Identify trending topics
            trending_topics = self._identify_trending_topics(keywords, target_platforms, time_frame)
            
            # Analyze emerging trends
            emerging_trends = self._analyze_emerging_trends(keywords, target_platforms)
            
            # Identify declining trends
            declining_trends = self._identify_declining_trends(keywords, target_platforms)
            
            # Generate seasonal predictions
            seasonal_predictions = []
            if include_predictions:
                seasonal_predictions = self._generate_seasonal_predictions(keywords)
            
            # Analyze platform-specific trends
            platform_trends = self._analyze_platform_trends(target_platforms, keywords)
            
            # Analyze industry-specific trends
            industry_trends = self._analyze_industry_trends(self.industry, keywords)
            
            # Filter by confidence
            trending_topics = [t for t in trending_topics if t.confidence_score >= min_confidence]
            emerging_trends = [t for t in emerging_trends if t.confidence_score >= min_confidence]
            
            # Calculate recommendation score
            recommendation_score = self._calculate_recommendation_score(
                trending_topics, emerging_trends, content, keywords
            )
            
            return TrendAnalysis(
                trending_topics=trending_topics,
                emerging_trends=emerging_trends,
                declining_trends=declining_trends,
                seasonal_predictions=seasonal_predictions,
                platform_trends=platform_trends,
                industry_trends=industry_trends,
                recommendation_score=recommendation_score,
                analysis_timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            raise

    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """Extract keywords from content for trend analysis"""
        if not content:
            return []
        
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Filter out stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'has', 'his', 'how', 'man',
            'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its'
        }
        
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count frequency and extract top keywords
        word_freq = Counter(filtered_words)
        keywords = [word for word, freq in word_freq.most_common(10) if freq > 1]
        
        return keywords

    def _identify_trending_topics(
        self, 
        keywords: List[str], 
        platforms: List[Platform], 
        time_frame: TimeFrame
    ) -> List[TrendingTopic]:
        """Identify currently trending topics"""
        
        trending_topics = []
        
        # Get current trending topics from our trend data
        current_trends = self.trend_data.get("current_trends", {})
        
        # Match keywords with trending topics
        for keyword in keywords:
            for trend_topic, trend_data in current_trends.items():
                if keyword.lower() in trend_topic.lower() or any(
                    keyword.lower() in related.lower() for related in trend_data.get("related", [])
                ):
                    # Calculate metrics for this trend
                    metrics = self._calculate_trend_metrics(trend_topic, platforms, time_frame)
                    
                    # Determine trend type
                    trend_type = self._classify_trend_type(metrics)
                    
                    trending_topic = TrendingTopic(
                        topic=trend_topic,
                        trend_type=trend_type,
                        platforms=platforms,
                        metrics=metrics,
                        related_keywords=trend_data.get("related", []),
                        hashtags=trend_data.get("hashtags", []),
                        peak_time=trend_data.get("peak_time", "unknown"),
                        predicted_duration=trend_data.get("duration", 24),
                        confidence_score=self._calculate_confidence_score(metrics, keyword, trend_topic)
                    )
                    
                    trending_topics.append(trending_topic)
        
        # Add general trending topics for the industry
        industry_trends = self.trend_data.get("industries", {}).get(self.industry, [])
        for trend_topic in industry_trends[:5]:  # Top 5 industry trends
            if not any(t.topic == trend_topic for t in trending_topics):
                metrics = self._calculate_trend_metrics(trend_topic, platforms, time_frame)
                
                trending_topic = TrendingTopic(
                    topic=trend_topic,
                    trend_type=TrendType.SUSTAINED,
                    platforms=platforms,
                    metrics=metrics,
                    related_keywords=self._get_related_keywords(trend_topic),
                    hashtags=self._generate_hashtags_for_topic(trend_topic),
                    peak_time="ongoing",
                    predicted_duration=168,  # 1 week
                    confidence_score=0.8
                )
                
                trending_topics.append(trending_topic)
        
        # Sort by confidence score and metrics
        trending_topics.sort(
            key=lambda x: x.confidence_score * x.metrics.virality_index, 
            reverse=True
        )
        
        return trending_topics[:10]  # Top 10 trending topics

    def _analyze_emerging_trends(
        self, 
        keywords: List[str], 
        platforms: List[Platform]
    ) -> List[TrendingTopic]:
        """Analyze emerging trends that are just starting to gain momentum"""
        
        emerging_trends = []
        
        # Get emerging trends data
        emerging_data = self.trend_data.get("emerging_trends", [])
        
        for trend_topic in emerging_data[:8]:  # Top 8 emerging trends
            # Check if relevant to keywords
            relevance_score = self._calculate_keyword_relevance(trend_topic, keywords)
            
            if relevance_score > 0.3:  # Minimum relevance threshold
                metrics = self._calculate_trend_metrics(trend_topic, platforms, TimeFrame.DAY)
                # Boost growth rate for emerging trends
                metrics.growth_rate *= 1.5
                
                emerging_trend = TrendingTopic(
                    topic=trend_topic,
                    trend_type=TrendType.EMERGING,
                    platforms=platforms,
                    metrics=metrics,
                    related_keywords=self._get_related_keywords(trend_topic),
                    hashtags=self._generate_hashtags_for_topic(trend_topic),
                    peak_time="predicted_24h",
                    predicted_duration=48,  # 2 days
                    confidence_score=relevance_score * 0.8  # Emerging trends have lower confidence
                )
                
                emerging_trends.append(emerging_trend)
        
        # Look for emerging patterns in user keywords
        for keyword in keywords:
            # Check if this keyword is showing signs of emerging trend
            if self._is_emerging_keyword(keyword):
                metrics = self._calculate_trend_metrics(keyword, platforms, TimeFrame.HOUR)
                
                emerging_trend = TrendingTopic(
                    topic=keyword,
                    trend_type=TrendType.EMERGING,
                    platforms=platforms,
                    metrics=metrics,
                    related_keywords=self._get_related_keywords(keyword),
                    hashtags=self._generate_hashtags_for_topic(keyword),
                    peak_time="next_12h",
                    predicted_duration=36,
                    confidence_score=0.6
                )
                
                emerging_trends.append(emerging_trend)
        
        return emerging_trends[:5]  # Top 5 emerging trends

    def _identify_declining_trends(
        self, 
        keywords: List[str], 
        platforms: List[Platform]
    ) -> List[TrendingTopic]:
        """Identify trends that are declining"""
        
        declining_trends = []
        
        # Get declining trends data
        declining_data = self.trend_data.get("declining_trends", [])
        
        for trend_topic in declining_data[:5]:
            if any(keyword.lower() in trend_topic.lower() for keyword in keywords):
                metrics = self._calculate_trend_metrics(trend_topic, platforms, TimeFrame.WEEK)
                # Set negative growth rate for declining trends
                metrics.growth_rate = -abs(metrics.growth_rate)
                
                declining_trend = TrendingTopic(
                    topic=trend_topic,
                    trend_type=TrendType.DECLINING,
                    platforms=platforms,
                    metrics=metrics,
                    related_keywords=self._get_related_keywords(trend_topic),
                    hashtags=self._generate_hashtags_for_topic(trend_topic),
                    peak_time="past",
                    predicted_duration=72,  # 3 days until irrelevant
                    confidence_score=0.7
                )
                
                declining_trends.append(declining_trend)
        
        return declining_trends

    def _generate_seasonal_predictions(self, keywords: List[str]) -> List[TrendingTopic]:
        """Generate seasonal trend predictions"""
        
        seasonal_predictions = []
        current_month = datetime.now().month
        
        # Get seasonal patterns
        seasonal_data = self.seasonal_patterns.get(current_month, [])
        
        for seasonal_topic in seasonal_data:
            # Check relevance to keywords
            relevance = self._calculate_keyword_relevance(seasonal_topic, keywords)
            
            if relevance > 0.2:
                metrics = self._calculate_trend_metrics(seasonal_topic, [Platform.INSTAGRAM], TimeFrame.MONTH)
                
                seasonal_prediction = TrendingTopic(
                    topic=seasonal_topic,
                    trend_type=TrendType.SEASONAL,
                    platforms=[Platform.INSTAGRAM, Platform.FACEBOOK, Platform.PINTEREST],
                    metrics=metrics,
                    related_keywords=self._get_related_keywords(seasonal_topic),
                    hashtags=self._generate_hashtags_for_topic(seasonal_topic),
                    peak_time="seasonal_peak",
                    predicted_duration=720,  # 30 days
                    confidence_score=relevance * 0.9
                )
                
                seasonal_predictions.append(seasonal_prediction)
        
        return seasonal_predictions[:3]  # Top 3 seasonal predictions

    def _analyze_platform_trends(
        self, 
        platforms: List[Platform], 
        keywords: List[str]
    ) -> Dict[Platform, List[str]]:
        """Analyze trends specific to each platform"""
        
        platform_trends = {}
        
        platform_specific_trends = {
            Platform.TIKTOK: [
                "viral dance", "trending sound", "challenge", "duet", "transformation",
                "before after", "day in my life", "get ready with me", "cooking hack"
            ],
            Platform.INSTAGRAM: [
                "aesthetic", "lifestyle", "outfit of the day", "skincare routine",
                "travel photography", "food styling", "home decor", "fitness journey"
            ],
            Platform.YOUTUBE: [
                "tutorial", "review", "unboxing", "vlog", "how to", "reaction",
                "explained", "vs comparison", "top 10", "documentary"
            ],
            Platform.TWITTER: [
                "breaking news", "hot take", "thread", "quote tweet", "viral tweet",
                "trending topic", "debate", "announcement", "live updates"
            ],
            Platform.LINKEDIN: [
                "career advice", "industry insights", "thought leadership", "networking",
                "professional development", "business strategy", "innovation", "leadership"
            ]
        }
        
        for platform in platforms:
            platform_specific = platform_specific_trends.get(platform, [])
            
            # Filter based on keyword relevance
            relevant_trends = []
            for trend in platform_specific:
                relevance = self._calculate_keyword_relevance(trend, keywords)
                if relevance > 0.1:  # Lower threshold for platform-specific
                    relevant_trends.append(trend)
            
            # Add general trending topics for this platform
            if not relevant_trends:
                relevant_trends = platform_specific[:5]
            
            platform_trends[platform] = relevant_trends[:8]
        
        return platform_trends

    def _analyze_industry_trends(self, industry: str, keywords: List[str]) -> Dict[str, List[str]]:
        """Analyze industry-specific trends"""
        
        industry_specific_trends = {
            "technology": [
                "artificial intelligence", "machine learning", "blockchain", "web3",
                "cybersecurity", "cloud computing", "IoT", "5G", "automation"
            ],
            "marketing": [
                "influencer marketing", "content marketing", "social media marketing",
                "email marketing", "SEO", "PPC", "conversion optimization", "analytics"
            ],
            "business": [
                "remote work", "digital transformation", "sustainability", "ESG",
                "startup", "entrepreneurship", "leadership", "innovation", "growth hacking"
            ],
            "health": [
                "mental health", "wellness", "fitness", "nutrition", "mindfulness",
                "self care", "healthy lifestyle", "preventive care", "telemedicine"
            ],
            "education": [
                "online learning", "edtech", "skill development", "certification",
                "remote education", "lifelong learning", "STEM", "digital literacy"
            ]
        }
        
        industry_trends = {}
        
        # Get trends for specified industry
        main_industry_trends = industry_specific_trends.get(industry, [])
        relevant_main_trends = []
        
        for trend in main_industry_trends:
            relevance = self._calculate_keyword_relevance(trend, keywords)
            if relevance > 0.2:
                relevant_main_trends.append(trend)
        
        industry_trends[industry] = relevant_main_trends[:10]
        
        # Add related industries
        related_industries = {
            "technology": ["business", "marketing"],
            "marketing": ["business", "technology"],
            "business": ["marketing", "technology"],
            "health": ["lifestyle", "wellness"],
            "education": ["technology", "business"]
        }
        
        for related_industry in related_industries.get(industry, []):
            if related_industry in industry_specific_trends:
                related_trends = industry_specific_trends[related_industry][:5]
                industry_trends[f"{related_industry} (related)"] = related_trends
        
        return industry_trends

    def _calculate_trend_metrics(
        self, 
        topic: str, 
        platforms: List[Platform], 
        time_frame: TimeFrame
    ) -> TrendMetrics:
        """Calculate metrics for a trending topic (simulated data)"""
        
        # Simulate metrics based on topic characteristics
        topic_length = len(topic.split())
        
        # Base volume calculation
        base_volume = 10000
        if any(platform in [Platform.TIKTOK, Platform.TWITTER] for platform in platforms):
            base_volume *= 5  # Higher volume for viral platforms
        
        volume = base_volume * (5 - min(4, topic_length))
        
        # Growth rate simulation
        if time_frame == TimeFrame.HOUR:
            growth_rate = 150.0 + (topic_length * 10)
        elif time_frame == TimeFrame.DAY:
            growth_rate = 75.0 + (topic_length * 5)
        else:
            growth_rate = 25.0 + (topic_length * 2)
        
        # Engagement rate simulation
        engagement_rate = max(0.02, min(0.15, 0.08 - (topic_length * 0.01)))
        
        # Velocity calculation
        velocity = growth_rate / 100
        
        # Reach calculation
        reach = int(volume * engagement_rate * 20)
        
        # Sentiment score simulation (-1 to 1)
        sentiment_score = 0.3 + (hash(topic) % 7) / 10  # Pseudo-random positive sentiment
        
        # Virality index (0-100)
        virality_index = min(100, growth_rate + engagement_rate * 100 + volume / 1000)
        
        return TrendMetrics(
            volume=max(100, volume),
            growth_rate=round(growth_rate, 1),
            velocity=round(velocity, 2),
            engagement_rate=round(engagement_rate, 3),
            reach=max(1000, reach),
            sentiment_score=round(sentiment_score, 2),
            virality_index=round(virality_index, 1)
        )

    def _classify_trend_type(self, metrics: TrendMetrics) -> TrendType:
        """Classify the type of trend based on metrics"""
        
        if metrics.virality_index > 80 and metrics.growth_rate > 100:
            return TrendType.VIRAL
        elif metrics.growth_rate > 50 and metrics.volume < 50000:
            return TrendType.EMERGING
        elif metrics.growth_rate < -10:
            return TrendType.DECLINING
        elif metrics.velocity > 1.0:
            return TrendType.SUSTAINED
        else:
            return TrendType.CYCLICAL

    def _calculate_confidence_score(self, metrics: TrendMetrics, keyword: str, topic: str) -> float:
        """Calculate confidence score for trend prediction"""
        
        # Keyword relevance factor
        keyword_match = 1.0 if keyword.lower() in topic.lower() else 0.5
        
        # Metrics factor
        metrics_factor = (
            min(1.0, metrics.virality_index / 100) * 0.4 +
            min(1.0, metrics.growth_rate / 100) * 0.3 +
            metrics.engagement_rate * 5 * 0.2 +
            min(1.0, metrics.volume / 100000) * 0.1
        )
        
        confidence = keyword_match * metrics_factor
        return round(min(1.0, confidence), 2)

    def _calculate_keyword_relevance(self, topic: str, keywords: List[str]) -> float:
        """Calculate relevance of a topic to given keywords"""
        
        if not keywords:
            return 0.0
        
        topic_words = set(topic.lower().split())
        keyword_words = set()
        
        for keyword in keywords:
            keyword_words.update(keyword.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(topic_words.intersection(keyword_words))
        union = len(topic_words.union(keyword_words))
        
        return intersection / union if union > 0 else 0.0

    def _is_emerging_keyword(self, keyword: str) -> bool:
        """Check if a keyword shows signs of emerging trend"""
        
        # Simple heuristics for emerging keywords
        emerging_indicators = [
            "new", "latest", "2025", "trending", "viral", "breaking",
            "fresh", "innovative", "revolutionary", "game-changing"
        ]
        
        return any(indicator in keyword.lower() for indicator in emerging_indicators)

    def _get_related_keywords(self, topic: str) -> List[str]:
        """Get related keywords for a topic"""
        
        # Simplified related keywords generation
        topic_lower = topic.lower()
        
        related_mappings = {
            "ai": ["artificial intelligence", "machine learning", "automation", "neural networks"],
            "marketing": ["digital marketing", "social media", "advertising", "branding"],
            "fitness": ["workout", "exercise", "health", "wellness", "training"],
            "food": ["recipe", "cooking", "nutrition", "restaurant", "chef"],
            "travel": ["vacation", "tourism", "adventure", "explore", "destination"],
            "technology": ["innovation", "digital", "software", "hardware", "tech"],
            "business": ["entrepreneur", "startup", "corporate", "strategy", "growth"]
        }
        
        related_keywords = []
        for key, values in related_mappings.items():
            if key in topic_lower:
                related_keywords.extend(values[:3])
        
        # Add generic related terms
        if not related_keywords:
            generic_terms = ["guide", "tips", "best", "how to", "tutorial"]
            related_keywords = [f"{topic} {term}" for term in generic_terms[:3]]
        
        return related_keywords[:5]

    def _generate_hashtags_for_topic(self, topic: str) -> List[str]:
        """Generate hashtags for a topic"""
        
        # Convert topic to hashtag format
        main_hashtag = f"#{topic.replace(' ', '').lower()}"
        hashtags = [main_hashtag]
        
        # Add variations
        words = topic.split()
        if len(words) > 1:
            # Individual word hashtags
            for word in words:
                if len(word) > 2:
                    hashtags.append(f"#{word.lower()}")
        
        # Add trending modifiers
        trending_modifiers = ["trending", "viral", "2025", "new", "hot"]
        for modifier in trending_modifiers[:2]:
            modified_hashtag = f"#{topic.replace(' ', '').lower()}{modifier}"
            hashtags.append(modified_hashtag)
        
        return hashtags[:5]

    def _calculate_recommendation_score(
        self, 
        trending_topics: List[TrendingTopic], 
        emerging_trends: List[TrendingTopic], 
        content: str, 
        keywords: List[str]
    ) -> float:
        """Calculate overall recommendation score"""
        
        score = 0.0
        
        # Trending topics alignment (40 points)
        if trending_topics:
            avg_confidence = sum(t.confidence_score for t in trending_topics) / len(trending_topics)
            score += avg_confidence * 40
        
        # Emerging trends opportunity (30 points)
        if emerging_trends:
            emerging_score = len(emerging_trends) * 6  # 6 points per emerging trend
            score += min(30, emerging_score)
        
        # Content relevance (20 points)
        if content and keywords:
            content_words = set(content.lower().split())
            keyword_words = set()
            for kw in keywords:
                keyword_words.update(kw.lower().split())
            
            relevance = len(content_words.intersection(keyword_words)) / len(keyword_words) if keyword_words else 0
            score += relevance * 20
        
        # Timing score (10 points)
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            score += 10
        elif 18 <= current_hour <= 22:  # Peak social media hours
            score += 8
        else:
            score += 5
        
        return min(100.0, score)

    def _initialize_trend_data(self) -> Dict[str, Any]:
        """Initialize trend database"""
        
        return {
            "current_trends": {
                "artificial intelligence": {
                    "related": ["AI", "machine learning", "automation", "ChatGPT"],
                    "hashtags": ["#ai", "#artificialintelligence", "#tech", "#innovation"],
                    "peak_time": "2025-01-01T14:00:00Z",
                    "duration": 72
                },
                "sustainable living": {
                    "related": ["eco-friendly", "zero waste", "green lifestyle", "sustainability"],
                    "hashtags": ["#sustainable", "#ecofriendly", "#zerowaste", "#green"],
                    "peak_time": "2025-01-01T10:00:00Z",
                    "duration": 168
                },
                "remote work": {
                    "related": ["work from home", "digital nomad", "flexible work", "hybrid work"],
                    "hashtags": ["#remotework", "#workfromhome", "#digitalnomad", "#flexibility"],
                    "peak_time": "2025-01-01T09:00:00Z",
                    "duration": 336
                }
            },
            "emerging_trends": [
                "quantum computing", "web3 gaming", "AI art", "vertical farming",
                "space tourism", "cryptocurrency regulation", "metaverse retail",
                "green hydrogen", "personalized medicine", "neural interfaces"
            ],
            "declining_trends": [
                "NFT hype", "cryptocurrency boom", "pandemic restrictions",
                "fast fashion", "single-use plastics"
            ],
            "industries": {
                "technology": [
                    "artificial intelligence", "quantum computing", "blockchain",
                    "cybersecurity", "cloud computing", "edge computing", "5G"
                ],
                "marketing": [
                    "influencer marketing", "video marketing", "personalization",
                    "voice search", "chatbot marketing", "social commerce"
                ],
                "business": [
                    "remote work", "digital transformation", "sustainability",
                    "automation", "data analytics", "customer experience"
                ],
                "general": [
                    "sustainability", "health and wellness", "digital transformation",
                    "artificial intelligence", "remote work", "social media"
                ]
            }
        }

    def _initialize_seasonal_patterns(self) -> Dict[int, List[str]]:
        """Initialize seasonal trend patterns by month"""
        
        return {
            1: ["new year goals", "fitness", "detox", "organizing", "self-improvement"],
            2: ["valentine's day", "love", "relationships", "romantic", "dating"],
            3: ["spring cleaning", "renewal", "growth", "fresh start", "gardening"],
            4: ["easter", "spring", "outdoor activities", "fresh air", "renewal"],
            5: ["mother's day", "graduation", "spring fashion", "outdoor fitness"],
            6: ["summer prep", "vacation planning", "wedding season", "outdoor events"],
            7: ["summer vacation", "beach", "travel", "outdoor activities", "festivals"],
            8: ["back to school", "education", "learning", "preparation", "organization"],
            9: ["fall fashion", "autumn", "cozy", "harvest", "new season"],
            10: ["halloween", "spooky", "costume", "autumn", "pumpkin"],
            11: ["thanksgiving", "gratitude", "family", "comfort food", "holiday prep"],
            12: ["christmas", "holiday", "gift giving", "year-end", "celebration"]
        }

    def _initialize_platform_weights(self) -> Dict[Platform, float]:
        """Initialize platform weights for trend analysis"""
        
        return {
            Platform.TIKTOK: 1.5,  # High viral potential
            Platform.TWITTER: 1.3,  # Real-time trends
            Platform.INSTAGRAM: 1.2,  # Visual trends
            Platform.YOUTUBE: 1.1,  # Long-form content trends
            Platform.LINKEDIN: 0.9,  # Professional trends
            Platform.FACEBOOK: 0.8,  # Slower trend adoption
            Platform.PINTEREST: 0.7,  # Seasonal trends
            Platform.REDDIT: 1.0   # Community-driven trends
        }

    def get_trend_recommendations(self, analysis: TrendAnalysis) -> List[str]:
        """Get actionable recommendations based on trend analysis"""
        
        recommendations = []
        
        # Trending topic recommendations
        if analysis.trending_topics:
            top_trend = analysis.trending_topics[0]
            recommendations.append(
                f"Capitalize on '{top_trend.topic}' trend - confidence: {top_trend.confidence_score:.1%}"
            )
        
        # Emerging trend recommendations
        if analysis.emerging_trends:
            recommendations.append(
                f"Early adoption opportunity: {len(analysis.emerging_trends)} emerging trends identified"
            )
        
        # Platform-specific recommendations
        for platform, trends in analysis.platform_trends.items():
            if trends:
                recommendations.append(
                    f"For {platform.value}: Focus on {trends[0]} content"
                )
        
        # Timing recommendations
        if analysis.recommendation_score > 80:
            recommendations.append("Excellent timing for content release")
        elif analysis.recommendation_score > 60:
            recommendations.append("Good timing for content release")
        else:
            recommendations.append("Consider waiting for better trend alignment")
        
        return recommendations

    def export_trend_analysis(self, analysis: TrendAnalysis, format: str = "json") -> str:
        """Export trend analysis in specified format"""
        
        if format == "json":
            return self._export_to_json(analysis)
        elif format == "csv":
            return self._export_to_csv(analysis)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_to_json(self, analysis: TrendAnalysis) -> str:
        """Export analysis to JSON format"""
        
        export_data = {
            "recommendation_score": analysis.recommendation_score,
            "analysis_timestamp": analysis.analysis_timestamp,
            "trending_topics": [self._topic_to_dict(topic) for topic in analysis.trending_topics],
            "emerging_trends": [self._topic_to_dict(topic) for topic in analysis.emerging_trends],
            "declining_trends": [self._topic_to_dict(topic) for topic in analysis.declining_trends],
            "seasonal_predictions": [self._topic_to_dict(topic) for topic in analysis.seasonal_predictions],
            "platform_trends": {p.value: trends for p, trends in analysis.platform_trends.items()},
            "industry_trends": analysis.industry_trends
        }
        
        return json.dumps(export_data, indent=2)

    def _topic_to_dict(self, topic: TrendingTopic) -> Dict[str, Any]:
        """Convert TrendingTopic to dictionary"""
        
        return {
            "topic": topic.topic,
            "trend_type": topic.trend_type.value,
            "platforms": [p.value for p in topic.platforms],
            "volume": topic.metrics.volume,
            "growth_rate": topic.metrics.growth_rate,
            "engagement_rate": topic.metrics.engagement_rate,
            "virality_index": topic.metrics.virality_index,
            "sentiment_score": topic.metrics.sentiment_score,
            "confidence_score": topic.confidence_score,
            "related_keywords": topic.related_keywords,
            "hashtags": topic.hashtags,
            "predicted_duration": topic.predicted_duration
        }

    def _export_to_csv(self, analysis: TrendAnalysis) -> str:
        """Export analysis to CSV format"""
        
        csv_lines = ["Topic,Type,Volume,Growth Rate,Engagement Rate,Virality Index,Confidence"]
        
        all_topics = (
            analysis.trending_topics + analysis.emerging_trends + 
            analysis.declining_trends + analysis.seasonal_predictions
        )
        
        for topic in all_topics:
            line = f'"{topic.topic}",{topic.trend_type.value},{topic.metrics.volume},' \
                   f'{topic.metrics.growth_rate},{topic.metrics.engagement_rate},' \
                   f'{topic.metrics.virality_index},{topic.confidence_score}'
            csv_lines.append(line)
        
        return '\n'.join(csv_lines)


# Export for module usage
__all__ = [
    "TrendingAnalyzer",
    "TrendType",
    "Platform",
    "TimeFrame",
    "TrendMetrics",
    "TrendingTopic", 
    "TrendAnalysis"
]