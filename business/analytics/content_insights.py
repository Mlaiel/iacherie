"""Content Insights Analyzer - Advanced content performance and optimization analytics
=================================================================================

Comprehensive content analytics system with AI-powered insights, performance tracking,
and optimization recommendations for multi-format content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import redis
import asyncpg
from fastapi import HTTPException
import re
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class ContentFormat(Enum):
    """Supported content formats for analysis"""    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    BLOG_POST = "blog_post"

class ContentTheme(Enum):
    """Content theme categories"""    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    INSPIRATIONAL = "inspirational"
    BEHIND_SCENES = "behind_scenes"
    PROMOTIONAL = "promotional"
    TRENDING = "trending"
    PERSONAL = "personal"
    COLLABORATIVE = "collaborative"

class PerformanceMetric(Enum):
    """Content performance metrics"""    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICK_THROUGH_RATE = "click_through_rate"
    COMPLETION_RATE = "completion_rate"

@dataclass
class ContentMetrics:
    """Comprehensive content performance metrics"""    content_id: str
    creator_id: str
    platform: str
    content_format: ContentFormat
    content_theme: ContentTheme
    title: str
    description: str
    hashtags: List[str]
    publish_date: datetime
    metrics: Dict[PerformanceMetric, float]
    audience_demographics: Dict[str, Any]
    engagement_timeline: Dict[str, float]
    virality_score: float
    quality_score: float
    optimization_potential: float

@dataclass
class ContentInsight:
    """AI-generated content insight with actionable recommendations"""    insight_id: str
    creator_id: str
    content_id: Optional[str]
    insight_category: str
    key_finding: str
    recommendation: str
    supporting_data: Dict[str, Any]
    confidence_score: float
    impact_potential: float
    implementation_effort: str
    expected_improvement: float
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ContentOptimization:
    """Content optimization recommendation"""    optimization_id: str
    creator_id: str
    content_type: ContentFormat
    current_performance: Dict[str, float]
    optimization_areas: List[str]
    specific_recommendations: List[str]
    expected_improvements: Dict[str, float]
    implementation_priority: str
    effort_required: str
    success_probability: float

class ContentInsightsAnalyzer:
    """    Enterprise-grade content insights analyzer with AI-powered performance analysis,
    optimization recommendations, and predictive content strategy guidance.
    """    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.content_clusterer = KMeans(n_clusters=8, random_state=42)
        self.performance_cache = {}
        self.insights_cache = {}
        
    async def initialize(self) -> None:
        """Initialize content insights analyzer"""        try:
            await self._setup_database_tables()
            await self._load_content_models()
            await self._initialize_analysis_algorithms()
            logger.info("Content Insights Analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Content Insights Analyzer: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup required database tables for content analysis"""        async with self.db_pool.acquire() as conn:
            await conn.execute("""                CREATE TABLE IF NOT EXISTS content_metrics (
                    id SERIAL PRIMARY KEY,
                    content_id VARCHAR(255) NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    content_format VARCHAR(30) NOT NULL,
                    content_theme VARCHAR(30) NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    hashtags TEXT[],
                    publish_date TIMESTAMP NOT NULL,
                    metrics JSONB NOT NULL,
                    audience_demographics JSONB,
                    engagement_timeline JSONB,
                    virality_score FLOAT DEFAULT 0,
                    quality_score FLOAT DEFAULT 0,
                    optimization_potential FLOAT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_content_performance (creator_id, publish_date),
                    INDEX idx_content_format_theme (content_format, content_theme),
                    INDEX idx_virality_score (virality_score DESC)
                );
                
                CREATE TABLE IF NOT EXISTS content_insights (
                    id SERIAL PRIMARY KEY,
                    insight_id VARCHAR(255) UNIQUE NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    content_id VARCHAR(255),
                    insight_category VARCHAR(100) NOT NULL,
                    key_finding TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    supporting_data JSONB,
                    confidence_score FLOAT NOT NULL,
                    impact_potential FLOAT NOT NULL,
                    implementation_effort VARCHAR(20),
                    expected_improvement FLOAT,
                    is_implemented BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS content_optimizations (
                    id SERIAL PRIMARY KEY,
                    optimization_id VARCHAR(255) UNIQUE NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    content_type VARCHAR(30) NOT NULL,
                    current_performance JSONB NOT NULL,
                    optimization_areas TEXT[] NOT NULL,
                    specific_recommendations TEXT[] NOT NULL,
                    expected_improvements JSONB,
                    implementation_priority VARCHAR(20),
                    effort_required VARCHAR(20),
                    success_probability FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def _load_content_models(self) -> None:
        """Load content analysis models and historical data"""        async with self.db_pool.acquire() as conn:
            # Load historical content data for model training
            content_data = await conn.fetch("""                SELECT title, description, metrics, virality_score, quality_score
                FROM content_metrics 
                WHERE created_at >= NOW() - INTERVAL '6 months'
                AND title IS NOT NULL AND description IS NOT NULL
                LIMIT 1000
            """)
            
            if content_data and len(content_data) > 50:
                await self._train_content_models(content_data)

    async def _train_content_models(self, content_data: List[Dict]) -> None:
        """Train content analysis models with historical data"""        try:
            # Prepare text data for clustering
            texts = []
            for record in content_data:
                text = f"{record['title']} {record['description'] or ''}"
                texts.append(text)
            
            if len(texts) > 20:
                # Train text vectorizer and clustering model
                text_features = self.vectorizer.fit_transform(texts)
                self.content_clusterer.fit(text_features.toarray())
                
                logger.info("Content analysis models trained successfully")
                
        except Exception as e:
            logger.error(f"Failed to train content models: {e}")

    async def _initialize_analysis_algorithms(self) -> None:
        """Initialize content analysis algorithms"""        # Additional algorithm initialization would go here
        pass

    async def analyze_content_comprehensive(self, content_id: str, platform: str) -> ContentMetrics:
        """Perform comprehensive content analysis with AI insights"""        try:
            # Fetch content data
            content_data = await self._fetch_content_data(content_id, platform)
            if not content_data:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Analyze performance metrics
            performance_metrics = await self._analyze_performance_metrics(content_id, platform)
            
            # Calculate advanced scores
            virality_score = await self._calculate_virality_score(content_data, performance_metrics)
            quality_score = await self._calculate_quality_score(content_data, performance_metrics)
            optimization_potential = await self._calculate_optimization_potential(content_data, performance_metrics)
            
            # Analyze audience demographics
            audience_demographics = await self._analyze_audience_demographics(content_id, platform)
            
            # Get engagement timeline
            engagement_timeline = await self._get_engagement_timeline(content_id, platform)
            
            # Create comprehensive metrics
            metrics = ContentMetrics(
                content_id=content_id,
                creator_id=content_data['creator_id'],
                platform=platform,
                content_format=ContentFormat(content_data['content_format']),
                content_theme=ContentTheme(content_data.get('content_theme', 'entertainment')),
                title=content_data['title'],
                description=content_data.get('description', ''),
                hashtags=content_data.get('hashtags', []),
                publish_date=content_data['publish_date'],
                metrics=performance_metrics,
                audience_demographics=audience_demographics,
                engagement_timeline=engagement_timeline,
                virality_score=virality_score,
                quality_score=quality_score,
                optimization_potential=optimization_potential
            )
            
            # Store metrics
            await self._store_content_metrics(metrics)
            
            # Cache for quick access
            cache_key = f"content_metrics:{content_id}:{platform}"
            await self.redis.setex(cache_key, 1800, metrics.__dict__)  # 30 minutes cache
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to analyze content: {e}")
            raise HTTPException(status_code=500, detail="Content analysis failed")

    async def _fetch_content_data(self, content_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Fetch content data from database or platform API"""        try:
            async with self.db_pool.acquire() as conn:
                record = await conn.fetchrow("""                    SELECT creator_id, content_format, content_theme, title, description, 
                           hashtags, publish_date
                    FROM content_metrics 
                    WHERE content_id = $1 AND platform = $2
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, content_id, platform)
                
                if record:
                    return dict(record)
                
                # If not in database, simulate fetching from platform API
                return {
                    'creator_id': f"creator_{content_id[:8]}",
                    'content_format': 'video',
                    'content_theme': 'entertainment',
                    'title': f"Content Title {content_id[:8]}",
                    'description': f"Description for content {content_id}",
                    'hashtags': ['#content', '#creator', '#viral'],
                    'publish_date': datetime.now() - timedelta(days=np.random.randint(1, 30))
                }
                
        except Exception as e:
            logger.error(f"Failed to fetch content data: {e}")
            return None

    async def _analyze_performance_metrics(self, content_id: str, platform: str) -> Dict[PerformanceMetric, float]:
        """Analyze comprehensive performance metrics"""        try:
            # This would integrate with actual platform APIs
            # For now, return realistic simulated data
            base_views = np.random.randint(1000, 100000)
            engagement_rate = np.random.uniform(0.02, 0.15)
            
            metrics = {
                PerformanceMetric.VIEWS: float(base_views),
                PerformanceMetric.LIKES: float(base_views * engagement_rate * 0.8),
                PerformanceMetric.SHARES: float(base_views * engagement_rate * 0.15),
                PerformanceMetric.COMMENTS: float(base_views * engagement_rate * 0.12),
                PerformanceMetric.SAVES: float(base_views * engagement_rate * 0.08),
                PerformanceMetric.ENGAGEMENT_RATE: engagement_rate,
                PerformanceMetric.REACH: float(base_views * np.random.uniform(0.7, 1.2)),
                PerformanceMetric.IMPRESSIONS: float(base_views * np.random.uniform(2.0, 5.0)),
                PerformanceMetric.CLICK_THROUGH_RATE: np.random.uniform(0.01, 0.08),
                PerformanceMetric.COMPLETION_RATE: np.random.uniform(0.45, 0.85)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to analyze performance metrics: {e}")
            return {}

    async def _calculate_virality_score(self, content_data: Dict, metrics: Dict[PerformanceMetric, float]) -> float:
        """Calculate content virality score (0-100)"""        try:
            # Factors that contribute to virality
            views = metrics.get(PerformanceMetric.VIEWS, 0)
            shares = metrics.get(PerformanceMetric.SHARES, 0)
            engagement_rate = metrics.get(PerformanceMetric.ENGAGEMENT_RATE, 0)
            completion_rate = metrics.get(PerformanceMetric.COMPLETION_RATE, 0.5)
            
            # Calculate share velocity
            publish_date = content_data['publish_date']
            hours_since_publish = (datetime.now() - publish_date).total_seconds() / 3600
            share_velocity = shares / max(hours_since_publish, 1)
            
            # Weighted virality score
            virality_components = {
                'share_velocity': min(share_velocity / 10, 1) * 30,  # 30% weight
                'engagement_rate': min(engagement_rate / 0.1, 1) * 25,  # 25% weight
                'completion_rate': completion_rate * 20,  # 20% weight
                'view_count': min(views / 50000, 1) * 15,  # 15% weight
                'hashtag_trending': self._calculate_hashtag_trending_score(content_data.get('hashtags', [])) * 10  # 10% weight
            }
            
            virality_score = sum(virality_components.values())
            return min(virality_score, 100)
            
        except Exception as e:
            logger.error(f"Failed to calculate virality score: {e}")
            return 0.0

    def _calculate_hashtag_trending_score(self, hashtags: List[str]) -> float:
        """Calculate trending score based on hashtags"""        # Simulate trending hashtag analysis
        trending_hashtags = ['#viral', '#trending', '#fyp', '#music', '#art', '#comedy']
        trending_score = 0
        
        for hashtag in hashtags:
            if hashtag.lower() in trending_hashtags:
                trending_score += 0.2
        
        return min(trending_score, 1.0)

    async def _calculate_quality_score(self, content_data: Dict, metrics: Dict[PerformanceMetric, float]) -> float:
        """Calculate content quality score (0-100)"""        try:
            # Quality factors
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            completion_rate = metrics.get(PerformanceMetric.COMPLETION_RATE, 0.5)
            engagement_rate = metrics.get(PerformanceMetric.ENGAGEMENT_RATE, 0)
            
            quality_components = {
                'title_quality': self._analyze_title_quality(title) * 20,
                'description_quality': self._analyze_description_quality(description) * 15,
                'completion_rate': completion_rate * 30,
                'sustained_engagement': min(engagement_rate / 0.08, 1) * 25,
                'content_length': self._analyze_content_length_quality(content_data) * 10
            }
            
            quality_score = sum(quality_components.values())
            return min(quality_score, 100)
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score: {e}")
            return 50.0

    def _analyze_title_quality(self, title: str) -> float:
        """Analyze title quality (0-1)"""        if not title:
            return 0.0
        
        quality_factors = 0
        total_factors = 5
        
        # Length check (optimal 30-60 characters)
        if 30 <= len(title) <= 60:
            quality_factors += 1
        
        # Contains numbers or specific details
        if re.search(r'\d+', title):
            quality_factors += 1
        
        # Contains action words
        action_words = ['learn', 'discover', 'create', 'build', 'make', 'get', 'find']
        if any(word in title.lower() for word in action_words):
            quality_factors += 1
        
        # Emotional words
        emotional_words = ['amazing', 'incredible', 'shocking', 'beautiful', 'awesome']
        if any(word in title.lower() for word in emotional_words):
            quality_factors += 1
        
        # Not all caps (good practice)
        if not title.isupper():
            quality_factors += 1
        
        return quality_factors / total_factors

    def _analyze_description_quality(self, description: str) -> float:
        """Analyze description quality (0-1)"""        if not description:
            return 0.3  # Basic score for having a description
        
        quality_factors = 0
        total_factors = 4
        
        # Length check (optimal 100-300 characters)
        if 100 <= len(description) <= 300:
            quality_factors += 1
        
        # Contains call-to-action
        cta_words = ['subscribe', 'like', 'share', 'comment', 'follow', 'check out']
        if any(word in description.lower() for word in cta_words):
            quality_factors += 1
        
        # Contains relevant keywords
        if len(description.split()) >= 10:
            quality_factors += 1
        
        # Proper formatting (not all one sentence)
        if '.' in description or '\n' in description:
            quality_factors += 1
        
        return quality_factors / total_factors

    def _analyze_content_length_quality(self, content_data: Dict) -> float:
        """Analyze content length quality based on format"""        content_format = content_data.get('content_format', 'video')
        
        # This would integrate with actual duration/length data
        # Return optimal score for now
        optimal_lengths = {
            'video': 0.8,  # Assume good length
            'audio': 0.9,
            'image': 1.0,
            'text': 0.7,
            'story': 1.0
        }
        
        return optimal_lengths.get(content_format, 0.75)

    async def _calculate_optimization_potential(self, content_data: Dict, metrics: Dict[PerformanceMetric, float]) -> float:
        """Calculate optimization potential score (0-100)"""        try:
            current_performance = metrics.get(PerformanceMetric.ENGAGEMENT_RATE, 0)
            views = metrics.get(PerformanceMetric.VIEWS, 0)
            completion_rate = metrics.get(PerformanceMetric.COMPLETION_RATE, 0.5)
            
            # Areas with optimization potential
            optimization_areas = []
            
            if current_performance < 0.05:  # Low engagement
                optimization_areas.append('engagement_improvement')
            
            if completion_rate < 0.6:  # Low completion
                optimization_areas.append('content_retention')
            
            if not content_data.get('description'):  # Missing description
                optimization_areas.append('metadata_optimization')
            
            if len(content_data.get('hashtags', [])) < 3:  # Few hashtags
                optimization_areas.append('hashtag_optimization')
            
            # Calculate potential based on number of optimization areas
            base_potential = len(optimization_areas) * 20  # 20 points per area
            
            # Adjust based on current performance
            if current_performance < 0.03:
                base_potential += 20  # High potential for low performers
            
            return min(base_potential, 100)
            
        except Exception as e:
            logger.error(f"Failed to calculate optimization potential: {e}")
            return 30.0

    async def _analyze_audience_demographics(self, content_id: str, platform: str) -> Dict[str, Any]:
        """Analyze audience demographics for the content"""        try:
            # This would integrate with actual audience data
            # Return simulated demographics for now
            return {
                'age_groups': {
                    '18-24': np.random.uniform(0.20, 0.40),
                    '25-34': np.random.uniform(0.25, 0.45),
                    '35-44': np.random.uniform(0.15, 0.25),
                    '45+': np.random.uniform(0.05, 0.15)
                },
                'gender_distribution': {
                    'female': np.random.uniform(0.40, 0.65),
                    'male': np.random.uniform(0.30, 0.55),
                    'other': np.random.uniform(0.02, 0.05)
                },
                'geographic_distribution': {
                    'US': np.random.uniform(0.30, 0.50),
                    'UK': np.random.uniform(0.10, 0.20),
                    'CA': np.random.uniform(0.05, 0.15),
                    'other': np.random.uniform(0.25, 0.45)
                },
                'interests': ['music', 'entertainment', 'lifestyle', 'art', 'technology']
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze audience demographics: {e}")
            return {}

    async def _get_engagement_timeline(self, content_id: str, platform: str) -> Dict[str, float]:
        """Get engagement timeline over hours since publish"""        try:
            # Simulate engagement timeline
            timeline = {}
            base_engagement = np.random.uniform(0.02, 0.12)
            
            for hour in range(0, 48, 2):  # Every 2 hours for 48 hours
                # Simulate viral curve - peaks early then declines
                if hour <= 4:
                    engagement = base_engagement * (1 + hour * 0.3)
                elif hour <= 12:
                    engagement = base_engagement * (1.2 - (hour - 4) * 0.05)
                else:
                    engagement = base_engagement * max(0.3, 1.2 - (hour - 4) * 0.03)
                
                timeline[f"hour_{hour}"] = engagement
            
            return timeline
            
        except Exception as e:
            logger.error(f"Failed to get engagement timeline: {e}")
            return {}

    async def _store_content_metrics(self, metrics: ContentMetrics) -> None:
        """Store content metrics in database"""        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""                    INSERT INTO content_metrics 
                    (content_id, creator_id, platform, content_format, content_theme,
                     title, description, hashtags, publish_date, metrics, 
                     audience_demographics, engagement_timeline, virality_score, 
                     quality_score, optimization_potential)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    ON CONFLICT (content_id) DO UPDATE SET
                    metrics = EXCLUDED.metrics,
                    audience_demographics = EXCLUDED.audience_demographics,
                    engagement_timeline = EXCLUDED.engagement_timeline,
                    virality_score = EXCLUDED.virality_score,
                    quality_score = EXCLUDED.quality_score,
                    optimization_potential = EXCLUDED.optimization_potential,
                    updated_at = NOW()
                """,
                metrics.content_id,
                metrics.creator_id,
                metrics.platform,
                metrics.content_format.value,
                metrics.content_theme.value,
                metrics.title,
                metrics.description,
                metrics.hashtags,
                metrics.publish_date,
                {k.value: v for k, v in metrics.metrics.items()},
                metrics.audience_demographics,
                metrics.engagement_timeline,
                metrics.virality_score,
                metrics.quality_score,
                metrics.optimization_potential
                )
        except Exception as e:
            logger.error(f"Failed to store content metrics: {e}")

    async def generate_content_insights(self, creator_id: str, timeframe: str = "30d") -> List[ContentInsight]:
        """Generate comprehensive AI-powered content insights"""        try:
            # Get content performance data
            content_data = await self._get_creator_content_data(creator_id, timeframe)
            
            if not content_data:
                return []
            
            insights = []
            
            # Analyze top performing content
            top_content_insight = await self._analyze_top_performing_content(creator_id, content_data)
            if top_content_insight:
                insights.append(top_content_insight)
            
            # Analyze content themes
            theme_insight = await self._analyze_content_themes(creator_id, content_data)
            if theme_insight:
                insights.append(theme_insight)
            
            # Analyze posting patterns
            timing_insight = await self._analyze_posting_patterns(creator_id, content_data)
            if timing_insight:
                insights.append(timing_insight)
            
            # Analyze format performance
            format_insight = await self._analyze_format_performance(creator_id, content_data)
            if format_insight:
                insights.append(format_insight)
            
            # Analyze audience preferences
            audience_insight = await self._analyze_audience_preferences(creator_id, content_data)
            if audience_insight:
                insights.append(audience_insight)
            
            # Store insights
            for insight in insights:
                await self._store_content_insight(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate content insights: {e}")
            return []

    async def _get_creator_content_data(self, creator_id: str, timeframe: str) -> List[Dict]:
        """Get creator's content data for analysis"""        try:
            timeframe_mapping = {
                '7d': timedelta(days=7),
                '30d': timedelta(days=30),
                '90d': timedelta(days=90)
            }
            
            delta = timeframe_mapping.get(timeframe, timedelta(days=30))
            start_date = datetime.now() - delta
            
            async with self.db_pool.acquire() as conn:
                records = await conn.fetch("""                    SELECT * FROM content_metrics 
                    WHERE creator_id = $1 AND publish_date >= $2
                    ORDER BY publish_date DESC
                """, creator_id, start_date)
                
                return [dict(record) for record in records]
                
        except Exception as e:
            logger.error(f"Failed to get creator content data: {e}")
            return []

    async def _analyze_top_performing_content(self, creator_id: str, content_data: List[Dict]) -> Optional[ContentInsight]:
        """Analyze top performing content patterns"""        try:
            if len(content_data) < 3:
                return None
            
            # Sort by engagement rate
            sorted_content = sorted(content_data, key=lambda x: x.get('metrics', {}).get('engagement_rate', 0), reverse=True)
            top_performers = sorted_content[:3]
            
            # Analyze common patterns
            common_themes = Counter([content['content_theme'] for content in top_performers])
            common_formats = Counter([content['content_format'] for content in top_performers])
            
            most_common_theme = common_themes.most_common(1)[0] if common_themes else ('entertainment', 1)
            most_common_format = common_formats.most_common(1)[0] if common_formats else ('video', 1)
            
            avg_engagement = np.mean([content.get('metrics', {}).get('engagement_rate', 0) for content in top_performers])
            
            insight = ContentInsight(
                insight_id=f"top_content_{creator_id}_{int(datetime.now().timestamp())}",
                creator_id=creator_id,
                content_id=None,
                insight_category="top_performing_analysis",
                key_finding=f"Top performing content shows {most_common_theme[0]} theme and {most_common_format[0]} format dominate with {avg_engagement:.1%} avg engagement",
                recommendation=f"Focus more on {most_common_theme[0]} content in {most_common_format[0]} format. Analyze successful elements for replication.",
                supporting_data={
                    'top_theme': most_common_theme[0],
                    'top_format': most_common_format[0],
                    'avg_engagement': avg_engagement,
                    'sample_size': len(top_performers)
                },
                confidence_score=0.85,
                impact_potential=0.80,
                implementation_effort="medium",
                expected_improvement=0.25
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Failed to analyze top performing content: {e}")
            return None

    async def _analyze_content_themes(self, creator_id: str, content_data: List[Dict]) -> Optional[ContentInsight]:
        """Analyze content theme performance"""        try:
            theme_performance = defaultdict(list)
            
            for content in content_data:
                theme = content['content_theme']
                engagement = content.get('metrics', {}).get('engagement_rate', 0)
                theme_performance[theme].append(engagement)
            
            # Calculate average performance by theme
            theme_averages = {}
            for theme, engagements in theme_performance.items():
                theme_averages[theme] = np.mean(engagements)
            
            if not theme_averages:
                return None
            
            best_theme = max(theme_averages, key=theme_averages.get)
            worst_theme = min(theme_averages, key=theme_averages.get)
            
            performance_gap = theme_averages[best_theme] - theme_averages[worst_theme]
            
            if performance_gap > 0.02:  # Significant difference
                insight = ContentInsight(
                    insight_id=f"theme_analysis_{creator_id}_{int(datetime.now().timestamp())}",
                    creator_id=creator_id,
                    content_id=None,
                    insight_category="content_theme_analysis",
                    key_finding=f"{best_theme.title()} content performs {performance_gap:.1%} better than {worst_theme} content",
                    recommendation=f"Increase {best_theme} content production and reduce {worst_theme} content. Consider improving {worst_theme} content quality.",
                    supporting_data={
                        'best_theme': best_theme,
                        'best_performance': theme_averages[best_theme],
                        'worst_theme': worst_theme,
                        'worst_performance': theme_averages[worst_theme],
                        'performance_gap': performance_gap
                    },
                    confidence_score=0.78,
                    impact_potential=0.65,
                    implementation_effort="low",
                    expected_improvement=performance_gap * 0.5
                )
                
                return insight
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze content themes: {e}")
            return None

    async def _analyze_posting_patterns(self, creator_id: str, content_data: List[Dict]) -> Optional[ContentInsight]:
        """Analyze posting timing patterns"""        try:
            posting_performance = defaultdict(list)
            
            for content in content_data:
                publish_date = content['publish_date']
                hour = publish_date.hour
                day_of_week = publish_date.weekday()
                engagement = content.get('metrics', {}).get('engagement_rate', 0)
                
                posting_performance[f"hour_{hour}"].append(engagement)
                posting_performance[f"day_{day_of_week}"].append(engagement)
            
            # Find best performing times
            hour_averages = {}
            day_averages = {}
            
            for key, engagements in posting_performance.items():
                if key.startswith('hour_'):
                    hour_averages[key] = np.mean(engagements)
                elif key.startswith('day_'):
                    day_averages[key] = np.mean(engagements)
            
            best_hour = max(hour_averages, key=hour_averages.get) if hour_averages else None
            best_day = max(day_averages, key=day_averages.get) if day_averages else None
            
            if best_hour and best_day:
                hour_num = int(best_hour.split('_')[1])
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_num = int(best_day.split('_')[1])
                day_name = day_names[day_num]
                
                best_hour_performance = hour_averages[best_hour]
                avg_performance = np.mean(list(hour_averages.values()))
                
                if best_hour_performance > avg_performance * 1.2:  # 20% better
                    insight = ContentInsight(
                        insight_id=f"timing_analysis_{creator_id}_{int(datetime.now().timestamp())}",
                        creator_id=creator_id,
                        content_id=None,
                        insight_category="posting_timing_analysis",
                        key_finding=f"Best posting time is {hour_num}:00 on {day_name} with {best_hour_performance:.1%} engagement",
                        recommendation=f"Schedule more content around {hour_num}:00 on {day_name}s to maximize engagement.",
                        supporting_data={
                            'best_hour': hour_num,
                            'best_day': day_name,
                            'best_performance': best_hour_performance,
                            'avg_performance': avg_performance,
                            'improvement_potential': best_hour_performance - avg_performance
                        },
                        confidence_score=0.72,
                        impact_potential=0.55,
                        implementation_effort="low",
                        expected_improvement=(best_hour_performance - avg_performance) * 0.3
                    )
                    
                    return insight
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze posting patterns: {e}")
            return None

    async def _analyze_format_performance(self, creator_id: str, content_data: List[Dict]) -> Optional[ContentInsight]:
        """Analyze content format performance"""        try:
            format_performance = defaultdict(list)
            
            for content in content_data:
                content_format = content['content_format']
                engagement = content.get('metrics', {}).get('engagement_rate', 0)
                format_performance[content_format].append(engagement)
            
            # Calculate average performance by format
            format_averages = {}
            for content_format, engagements in format_performance.items():
                if len(engagements) >= 2:  # Need at least 2 samples
                    format_averages[content_format] = np.mean(engagements)
            
            if len(format_averages) >= 2:
                best_format = max(format_averages, key=format_averages.get)
                worst_format = min(format_averages, key=format_averages.get)
                
                performance_gap = format_averages[best_format] - format_averages[worst_format]
                
                if performance_gap > 0.03:  # 3% difference
                    insight = ContentInsight(
                        insight_id=f"format_analysis_{creator_id}_{int(datetime.now().timestamp())}",
                        creator_id=creator_id,
                        content_id=None,
                        insight_category="content_format_analysis",
                        key_finding=f"{best_format.title()} format performs {performance_gap:.1%} better than {worst_format} format",
                        recommendation=f"Prioritize {best_format} content creation and optimize {worst_format} content strategy.",
                        supporting_data={
                            'best_format': best_format,
                            'best_performance': format_averages[best_format],
                            'worst_format': worst_format,
                            'worst_performance': format_averages[worst_format],
                            'performance_gap': performance_gap
                        },
                        confidence_score=0.80,
                        impact_potential=0.70,
                        implementation_effort="medium",
                        expected_improvement=performance_gap * 0.4
                    )
                    
                    return insight
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze format performance: {e}")
            return None

    async def _analyze_audience_preferences(self, creator_id: str, content_data: List[Dict]) -> Optional[ContentInsight]:
        """Analyze audience preferences and behavior"""        try:
            # Analyze completion rates and engagement patterns
            completion_rates = []
            engagement_rates = []
            
            for content in content_data:
                metrics = content.get('metrics', {})
                completion_rate = metrics.get('completion_rate', 0.5)
                engagement_rate = metrics.get('engagement_rate', 0)
                
                completion_rates.append(completion_rate)
                engagement_rates.append(engagement_rate)
            
            avg_completion = np.mean(completion_rates) if completion_rates else 0.5
            avg_engagement = np.mean(engagement_rates) if engagement_rates else 0.05
            
            # Generate insights based on patterns
            if avg_completion < 0.6:
                insight = ContentInsight(
                    insight_id=f"audience_pref_{creator_id}_{int(datetime.now().timestamp())}",
                    creator_id=creator_id,
                    content_id=None,
                    insight_category="audience_preferences",
                    key_finding=f"Low average completion rate ({avg_completion:.1%}) suggests content may be too long or less engaging",
                    recommendation="Consider shorter content formats, stronger openings, and more engaging storytelling techniques.",
                    supporting_data={
                        'avg_completion_rate': avg_completion,
                        'avg_engagement_rate': avg_engagement,
                        'sample_size': len(content_data)
                    },
                    confidence_score=0.75,
                    impact_potential=0.60,
                    implementation_effort="medium",
                    expected_improvement=0.20
                )
                
                return insight
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze audience preferences: {e}")
            return None

    async def _store_content_insight(self, insight: ContentInsight) -> None:
        """Store content insight in database"""        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""                    INSERT INTO content_insights 
                    (insight_id, creator_id, content_id, insight_category, key_finding,
                     recommendation, supporting_data, confidence_score, impact_potential,
                     implementation_effort, expected_improvement)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (insight_id) DO NOTHING
                """,
                insight.insight_id,
                insight.creator_id,
                insight.content_id,
                insight.insight_category,
                insight.key_finding,
                insight.recommendation,
                insight.supporting_data,
                insight.confidence_score,
                insight.impact_potential,
                insight.implementation_effort,
                insight.expected_improvement
                )
        except Exception as e:
            logger.error(f"Failed to store content insight: {e}")

    async def get_content_dashboard_data(self, creator_id: str, timeframe: str = "30d") -> Dict[str, Any]:
        """Get comprehensive content analytics data for dashboard"""        try:
            content_data = await self._get_creator_content_data(creator_id, timeframe)
            insights = await self.generate_content_insights(creator_id, timeframe)
            
            if not content_data:
                return {'error': 'No content data found'}
            
            # Calculate summary statistics
            total_content = len(content_data)
            avg_engagement = np.mean([content.get('metrics', {}).get('engagement_rate', 0) for content in content_data])
            avg_virality = np.mean([content.get('virality_score', 0) for content in content_data])
            avg_quality = np.mean([content.get('quality_score', 0) for content in content_data])
            
            # Top performing content
            top_content = sorted(content_data, key=lambda x: x.get('metrics', {}).get('engagement_rate', 0), reverse=True)[:5]
            
            # Format distribution
            format_distribution = Counter([content['content_format'] for content in content_data])
            theme_distribution = Counter([content['content_theme'] for content in content_data])
            
            dashboard_data = {
                'summary_stats': {
                    'total_content': total_content,
                    'avg_engagement_rate': avg_engagement,
                    'avg_virality_score': avg_virality,
                    'avg_quality_score': avg_quality,
                    'timeframe': timeframe
                },
                'top_performing_content': [
                    {
                        'content_id': content['content_id'],
                        'title': content['title'],
                        'engagement_rate': content.get('metrics', {}).get('engagement_rate', 0),
                        'virality_score': content.get('virality_score', 0),
                        'content_format': content['content_format'],
                        'content_theme': content['content_theme']
                    }
                    for content in top_content
                ],
                'format_distribution': dict(format_distribution),
                'theme_distribution': dict(theme_distribution),
                'ai_insights': [
                    {
                        'category': insight.insight_category,
                        'finding': insight.key_finding,
                        'recommendation': insight.recommendation,
                        'confidence': insight.confidence_score,
                        'impact': insight.impact_potential
                    }
                    for insight in insights
                ],
                'optimization_recommendations': await self._get_optimization_recommendations(creator_id, content_data),
                'generated_at': datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get content dashboard data: {e}")
            raise HTTPException(status_code=500, detail="Content dashboard data retrieval failed")

    async def _get_optimization_recommendations(self, creator_id: str, content_data: List[Dict]) -> List[Dict[str, Any]]:
        """Get content optimization recommendations"""        try:
            recommendations = []
            
            if content_data:
                # Analyze optimization potential
                high_potential_content = [c for c in content_data if c.get('optimization_potential', 0) > 50]
                
                if len(high_potential_content) > 0:
                    recommendations.append({
                        'type': 'content_optimization',
                        'priority': 'high',
                        'recommendation': f"{len(high_potential_content)} pieces of content have high optimization potential",
                        'action': 'Review and optimize metadata, descriptions, and hashtags'
                    })
                
                # Check posting frequency
                if len(content_data) < 10:  # Less than 10 posts in timeframe
                    recommendations.append({
                        'type': 'posting_frequency',
                        'priority': 'medium',
                        'recommendation': 'Consider increasing posting frequency for better audience engagement',
                        'action': 'Develop content calendar with consistent posting schedule'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return []
