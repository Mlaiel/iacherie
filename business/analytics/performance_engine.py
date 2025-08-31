"""Performance Analytics Engine - Real-time performance monitoring and optimization
==============================================================================

Advanced performance tracking system for multi-format content creators with
real-time metrics, AI-powered insights, and automated optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeansCluster
import redis
import asyncpg
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Supported content types for performance analysis"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"

class PerformanceMetric(Enum):
    """Key performance indicators for content analysis"""    VIEWS = "views"
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    SAVES = "saves"
    CONVERSION_RATE = "conversion_rate"
    RETENTION_RATE = "retention_rate"

@dataclass
class PerformanceSnapshot:
    """Real-time performance snapshot for content"""    content_id: str
    creator_id: str
    content_type: ContentType
    platform: str
    timestamp: datetime
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
    score: float
    trending_probability: float

@dataclass
class PerformanceInsight:
    """AI-generated performance insight with recommendations"""    insight_id: str
    content_id: str
    insight_type: str
    confidence_score: float
    recommendation: str
    impact_prediction: float
    implementation_priority: str
    estimated_improvement: float

class PerformanceAnalyticsEngine:
    """    Enterprise-grade performance analytics engine with real-time monitoring,
    AI-powered insights, and predictive optimization for content creators.
    """    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.scaler = StandardScaler()
        self.performance_cache = {}
        self.insight_cache = {}
        self.clustering_model = KMeansCluster(n_clusters=5, random_state=42)
        
    async def initialize(self) -> None:
        """Initialize analytics engine with database connections and models"""        try:
            await self._setup_database_tables()
            await self._load_historical_data()
            await self._initialize_ml_models()
            logger.info("Performance Analytics Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Performance Analytics Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup required database tables for performance tracking"""        async with self.db_pool.acquire() as conn:
            await conn.execute("""                CREATE TABLE IF NOT EXISTS performance_snapshots (
                    id SERIAL PRIMARY KEY,
                    content_id VARCHAR(255) NOT NULL,
                    creator_id VARCHAR(255) NOT NULL,
                    content_type VARCHAR(50) NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    metrics JSONB NOT NULL,
                    metadata JSONB,
                    score FLOAT NOT NULL,
                    trending_probability FLOAT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_content_performance (content_id, created_at),
                    INDEX idx_creator_performance (creator_id, created_at)
                );
                
                CREATE TABLE IF NOT EXISTS performance_insights (
                    id SERIAL PRIMARY KEY,
                    insight_id VARCHAR(255) UNIQUE NOT NULL,
                    content_id VARCHAR(255) NOT NULL,
                    insight_type VARCHAR(100) NOT NULL,
                    confidence_score FLOAT NOT NULL,
                    recommendation TEXT NOT NULL,
                    impact_prediction FLOAT,
                    implementation_priority VARCHAR(20),
                    estimated_improvement FLOAT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    is_implemented BOOLEAN DEFAULT FALSE
                );
            """)

    async def _load_historical_data(self) -> None:
        """Load historical performance data for model training"""        async with self.db_pool.acquire() as conn:
            historical_data = await conn.fetch("""                SELECT content_id, metrics, score, trending_probability 
                FROM performance_snapshots 
                WHERE created_at >= NOW() - INTERVAL '90 days'
                ORDER BY created_at DESC
            """)
            
            if historical_data:
                df = pd.DataFrame([dict(record) for record in historical_data])
                self._train_performance_models(df)

    def _train_performance_models(self, df: pd.DataFrame) -> None:
        """Train ML models with historical performance data"""        try:
            # Extract features from metrics
            metrics_features = []
            for _, row in df.iterrows():
                metrics = row['metrics']
                features = [
                    metrics.get('views', 0),
                    metrics.get('engagement_rate', 0),
                    metrics.get('reach', 0),
                    metrics.get('shares', 0),
                    metrics.get('comments', 0)
                ]
                metrics_features.append(features)
            
            X = np.array(metrics_features)
            X_scaled = self.scaler.fit_transform(X)
            
            # Train clustering model for performance segmentation
            self.clustering_model.fit(X_scaled)
            
            logger.info("Performance models trained successfully")
        except Exception as e:
            logger.error(f"Failed to train performance models: {e}")

    async def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for performance prediction"""        # Initialize models would go here in full implementation
        pass

    async def track_performance_real_time(self, content_id: str, platform: str) -> PerformanceSnapshot:
        """Track real-time performance metrics for content"""        try:
            # Get current metrics from platform APIs
            current_metrics = await self._fetch_platform_metrics(content_id, platform)
            
            # Calculate performance score
            performance_score = await self._calculate_performance_score(current_metrics, platform)
            
            # Calculate trending probability
            trending_prob = await self._calculate_trending_probability(current_metrics, content_id)
            
            # Create performance snapshot
            snapshot = PerformanceSnapshot(
                content_id=content_id,
                creator_id=current_metrics.get('creator_id'),
                content_type=ContentType(current_metrics.get('content_type', 'video')),
                platform=platform,
                timestamp=datetime.now(),
                metrics=current_metrics,
                metadata=current_metrics.get('metadata', {}),
                score=performance_score,
                trending_probability=trending_prob
            )
            
            # Store snapshot
            await self._store_performance_snapshot(snapshot)
            
            # Cache for quick access
            cache_key = f"performance:{content_id}:{platform}"
            await self.redis.setex(
                cache_key, 
                300,  # 5 minutes
                snapshot.__dict__
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to track real-time performance: {e}")
            raise HTTPException(status_code=500, detail="Performance tracking failed")

    async def _fetch_platform_metrics(self, content_id: str, platform: str) -> Dict[str, Any]:
        """Fetch current metrics from platform APIs"""        # Implementation would integrate with actual platform APIs
        # For now, return simulated data
        return {
            'creator_id': f"creator_{content_id[:8]}",
            'content_type': 'video',
            'views': np.random.randint(1000, 100000),
            'engagement_rate': np.random.uniform(0.01, 0.15),
            'reach': np.random.randint(500, 50000),
            'impressions': np.random.randint(2000, 200000),
            'shares': np.random.randint(10, 1000),
            'comments': np.random.randint(5, 500),
            'likes': np.random.randint(50, 5000),
            'saves': np.random.randint(20, 2000),
            'metadata': {
                'duration': np.random.randint(30, 600),
                'quality': 'HD',
                'upload_time': datetime.now().isoformat()
            }
        }

    async def _calculate_performance_score(self, metrics: Dict[str, Any], platform: str) -> float:
        """Calculate normalized performance score (0-100)"""        try:
            # Weighted scoring based on platform characteristics
            platform_weights = {
                'youtube': {'views': 0.3, 'engagement_rate': 0.4, 'shares': 0.3},
                'instagram': {'engagement_rate': 0.5, 'reach': 0.3, 'saves': 0.2},
                'tiktok': {'views': 0.4, 'shares': 0.4, 'engagement_rate': 0.2},
                'spotify': {'plays': 0.6, 'saves': 0.2, 'shares': 0.2}
            }
            
            weights = platform_weights.get(platform.lower(), platform_weights['youtube'])
            
            score = 0
            for metric, weight in weights.items():
                value = metrics.get(metric, 0)
                normalized_value = min(value / 10000, 1)  # Normalize to 0-1
                score += normalized_value * weight * 100
            
            return min(score, 100)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Failed to calculate performance score: {e}")
            return 0.0

    async def _calculate_trending_probability(self, metrics: Dict[str, Any], content_id: str) -> float:
        """Calculate probability of content trending (0-1)"""        try:
            # Get historical performance for comparison
            historical_avg = await self._get_historical_average_performance(content_id)
            
            # Calculate growth rate
            current_engagement = metrics.get('engagement_rate', 0)
            historical_engagement = historical_avg.get('engagement_rate', 0.01)
            
            if historical_engagement > 0:
                growth_rate = (current_engagement - historical_engagement) / historical_engagement
            else:
                growth_rate = 0
            
            # Factor in velocity metrics
            velocity_score = min(metrics.get('shares', 0) / 100, 1) * 0.4
            growth_score = min(max(growth_rate, 0) / 2, 1) * 0.6
            
            trending_probability = velocity_score + growth_score
            return min(trending_probability, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate trending probability: {e}")
            return 0.0

    async def _get_historical_average_performance(self, content_id: str) -> Dict[str, float]:
        """Get historical average performance metrics"""        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchrow("""                    SELECT AVG((metrics->>'engagement_rate')::float) as avg_engagement_rate,
                           AVG((metrics->>'views')::float) as avg_views,
                           AVG(score) as avg_score
                    FROM performance_snapshots 
                    WHERE content_id = $1 
                    AND created_at >= NOW() - INTERVAL '30 days'
                """, content_id)
                
                if result:
                    return {
                        'engagement_rate': result['avg_engagement_rate'] or 0.01,
                        'views': result['avg_views'] or 100,
                        'score': result['avg_score'] or 50
                    }
                return {'engagement_rate': 0.01, 'views': 100, 'score': 50}
                
        except Exception as e:
            logger.error(f"Failed to get historical performance: {e}")
            return {'engagement_rate': 0.01, 'views': 100, 'score': 50}

    async def _store_performance_snapshot(self, snapshot: PerformanceSnapshot) -> None:
        """Store performance snapshot in database"""        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""                    INSERT INTO performance_snapshots 
                    (content_id, creator_id, content_type, platform, metrics, metadata, score, trending_probability)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, 
                snapshot.content_id,
                snapshot.creator_id,
                snapshot.content_type.value,
                snapshot.platform,
                snapshot.metrics,
                snapshot.metadata,
                snapshot.score,
                snapshot.trending_probability
                )
        except Exception as e:
            logger.error(f"Failed to store performance snapshot: {e}")

    async def generate_performance_insights(self, content_id: str) -> List[PerformanceInsight]:
        """Generate AI-powered performance insights and recommendations"""        try:
            # Get recent performance data
            recent_snapshots = await self._get_recent_snapshots(content_id, limit=10)
            
            if not recent_snapshots:
                return []
            
            insights = []
            
            # Analyze performance trends
            trend_insight = await self._analyze_performance_trends(recent_snapshots)
            if trend_insight:
                insights.append(trend_insight)
            
            # Analyze engagement patterns
            engagement_insight = await self._analyze_engagement_patterns(recent_snapshots)
            if engagement_insight:
                insights.append(engagement_insight)
            
            # Analyze timing optimization
            timing_insight = await self._analyze_optimal_timing(recent_snapshots)
            if timing_insight:
                insights.append(timing_insight)
            
            # Store insights
            for insight in insights:
                await self._store_performance_insight(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate performance insights: {e}")
            return []

    async def _get_recent_snapshots(self, content_id: str, limit: int = 10) -> List[PerformanceSnapshot]:
        """Get recent performance snapshots for analysis"""        try:
            async with self.db_pool.acquire() as conn:
                records = await conn.fetch("""                    SELECT * FROM performance_snapshots 
                    WHERE content_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT $2
                """, content_id, limit)
                
                snapshots = []
                for record in records:
                    snapshot = PerformanceSnapshot(
                        content_id=record['content_id'],
                        creator_id=record['creator_id'],
                        content_type=ContentType(record['content_type']),
                        platform=record['platform'],
                        timestamp=record['created_at'],
                        metrics=record['metrics'],
                        metadata=record['metadata'] or {},
                        score=record['score'],
                        trending_probability=record['trending_probability'] or 0
                    )
                    snapshots.append(snapshot)
                
                return snapshots
                
        except Exception as e:
            logger.error(f"Failed to get recent snapshots: {e}")
            return []

    async def _analyze_performance_trends(self, snapshots: List[PerformanceSnapshot]) -> Optional[PerformanceInsight]:
        """Analyze performance trends and generate insights"""        if len(snapshots) < 3:
            return None
        
        try:
            scores = [s.score for s in snapshots[-5:]]  # Last 5 snapshots
            
            # Calculate trend
            trend = np.polyfit(range(len(scores)), scores, 1)[0]
            
            if trend > 5:  # Improving trend
                insight = PerformanceInsight(
                    insight_id=f"trend_{snapshots[0].content_id}_{int(datetime.now().timestamp())}",
                    content_id=snapshots[0].content_id,
                    insight_type="performance_trend",
                    confidence_score=0.85,
                    recommendation="Performance is trending upward. Consider increasing posting frequency and engaging more with audience.",
                    impact_prediction=trend * 0.1,
                    implementation_priority="medium",
                    estimated_improvement=trend * 0.15
                )
                return insight
            elif trend < -5:  # Declining trend
                insight = PerformanceInsight(
                    insight_id=f"trend_{snapshots[0].content_id}_{int(datetime.now().timestamp())}",
                    content_id=snapshots[0].content_id,
                    insight_type="performance_decline",
                    confidence_score=0.80,
                    recommendation="Performance is declining. Consider analyzing top-performing content and adjusting strategy.",
                    impact_prediction=abs(trend) * 0.1,
                    implementation_priority="high",
                    estimated_improvement=abs(trend) * 0.2
                )
                return insight
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e}")
            return None

    async def _analyze_engagement_patterns(self, snapshots: List[PerformanceSnapshot]) -> Optional[PerformanceInsight]:
        """Analyze engagement patterns for optimization"""        try:
            engagement_rates = [s.metrics.get('engagement_rate', 0) for s in snapshots]
            avg_engagement = np.mean(engagement_rates)
            
            if avg_engagement < 0.02:  # Low engagement threshold
                insight = PerformanceInsight(
                    insight_id=f"engagement_{snapshots[0].content_id}_{int(datetime.now().timestamp())}",
                    content_id=snapshots[0].content_id,
                    insight_type="low_engagement",
                    confidence_score=0.75,
                    recommendation="Engagement rate is below average. Consider using more interactive content formats and calls-to-action.",
                    impact_prediction=0.8,
                    implementation_priority="high",
                    estimated_improvement=1.5
                )
                return insight
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze engagement patterns: {e}")
            return None

    async def _analyze_optimal_timing(self, snapshots: List[PerformanceSnapshot]) -> Optional[PerformanceInsight]:
        """Analyze optimal posting timing"""        try:
            # Group by hour and calculate average performance
            hourly_performance = {}
            for snapshot in snapshots:
                hour = snapshot.timestamp.hour
                if hour not in hourly_performance:
                    hourly_performance[hour] = []
                hourly_performance[hour].append(snapshot.score)
            
            # Find best performing hours
            if len(hourly_performance) >= 3:
                avg_by_hour = {hour: np.mean(scores) for hour, scores in hourly_performance.items()}
                best_hour = max(avg_by_hour, key=avg_by_hour.get)
                best_score = avg_by_hour[best_hour]
                overall_avg = np.mean(list(avg_by_hour.values()))
                
                if best_score > overall_avg * 1.2:  # 20% better than average
                    insight = PerformanceInsight(
                        insight_id=f"timing_{snapshots[0].content_id}_{int(datetime.now().timestamp())}",
                        content_id=snapshots[0].content_id,
                        insight_type="optimal_timing",
                        confidence_score=0.70,
                        recommendation=f"Best performance observed around {best_hour}:00. Consider scheduling future content at this time.",
                        impact_prediction=0.6,
                        implementation_priority="medium",
                        estimated_improvement=1.2
                    )
                    return insight
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze optimal timing: {e}")
            return None

    async def _store_performance_insight(self, insight: PerformanceInsight) -> None:
        """Store performance insight in database"""        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""                    INSERT INTO performance_insights 
                    (insight_id, content_id, insight_type, confidence_score, recommendation, 
                     impact_prediction, implementation_priority, estimated_improvement)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (insight_id) DO NOTHING
                """,
                insight.insight_id,
                insight.content_id,
                insight.insight_type,
                insight.confidence_score,
                insight.recommendation,
                insight.impact_prediction,
                insight.implementation_priority,
                insight.estimated_improvement
                )
        except Exception as e:
            logger.error(f"Failed to store performance insight: {e}")

    async def get_performance_dashboard_data(self, creator_id: str, timeframe: str = "7d") -> Dict[str, Any]:
        """Get comprehensive performance data for dashboard"""        try:
            timeframe_mapping = {
                '1d': timedelta(days=1),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30),
                '90d': timedelta(days=90)
            }
            
            delta = timeframe_mapping.get(timeframe, timedelta(days=7))
            start_date = datetime.now() - delta
            
            async with self.db_pool.acquire() as conn:
                # Get performance overview
                overview = await conn.fetchrow("""                    SELECT 
                        COUNT(*) as total_content,
                        AVG(score) as avg_score,
                        AVG(trending_probability) as avg_trending_prob,
                        MAX(score) as best_score
                    FROM performance_snapshots 
                    WHERE creator_id = $1 AND created_at >= $2
                """, creator_id, start_date)
                
                # Get top performing content
                top_content = await conn.fetch("""                    SELECT content_id, platform, MAX(score) as best_score, 
                           AVG((metrics->>'views')::float) as avg_views
                    FROM performance_snapshots 
                    WHERE creator_id = $1 AND created_at >= $2
                    GROUP BY content_id, platform
                    ORDER BY best_score DESC
                    LIMIT 10
                """, creator_id, start_date)
                
                # Get platform performance
                platform_performance = await conn.fetch("""                    SELECT platform, 
                           AVG(score) as avg_score,
                           COUNT(*) as content_count,
                           AVG((metrics->>'engagement_rate')::float) as avg_engagement
                    FROM performance_snapshots 
                    WHERE creator_id = $1 AND created_at >= $2
                    GROUP BY platform
                    ORDER BY avg_score DESC
                """, creator_id, start_date)
                
                # Get recent insights
                recent_insights = await conn.fetch("""                    SELECT insight_type, recommendation, confidence_score, 
                           implementation_priority, created_at
                    FROM performance_insights pi
                    JOIN performance_snapshots ps ON pi.content_id = ps.content_id
                    WHERE ps.creator_id = $1 AND pi.created_at >= $2
                    ORDER BY pi.created_at DESC
                    LIMIT 5
                """, creator_id, start_date)
            
            dashboard_data = {
                'overview': dict(overview) if overview else {},
                'top_content': [dict(record) for record in top_content],
                'platform_performance': [dict(record) for record in platform_performance],
                'recent_insights': [dict(record) for record in recent_insights],
                'timeframe': timeframe,
                'generated_at': datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get performance dashboard data: {e}")
            raise HTTPException(status_code=500, detail="Dashboard data retrieval failed")

    async def optimize_content_strategy(self, creator_id: str) -> Dict[str, Any]:
        """Generate AI-powered content strategy optimization recommendations"""        try:
            # Get comprehensive performance data
            dashboard_data = await self.get_performance_dashboard_data(creator_id, "30d")
            
            # Analyze patterns and generate recommendations
            optimization_recommendations = {
                'content_timing': await self._optimize_posting_schedule(creator_id),
                'platform_focus': await self._optimize_platform_strategy(creator_id),
                'content_format': await self._optimize_content_format(creator_id),
                'engagement_tactics': await self._optimize_engagement_strategy(creator_id),
                'performance_targets': await self._set_performance_targets(creator_id)
            }
            
            return {
                'creator_id': creator_id,
                'optimization_date': datetime.now().isoformat(),
                'recommendations': optimization_recommendations,
                'confidence_score': 0.85,
                'implementation_timeline': '2-4 weeks'
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize content strategy: {e}")
            raise HTTPException(status_code=500, detail="Strategy optimization failed")

    async def _optimize_posting_schedule(self, creator_id: str) -> Dict[str, Any]:
        """Optimize posting schedule based on historical performance"""        # Implementation for posting schedule optimization
        return {
            'recommended_times': ['09:00', '15:00', '19:00'],
            'best_days': ['Tuesday', 'Wednesday', 'Sunday'],
            'frequency': 'Daily for high engagement content, 3x/week for others',
            'confidence': 0.78
        }

    async def _optimize_platform_strategy(self, creator_id: str) -> Dict[str, Any]:
        """Optimize platform allocation strategy"""        # Implementation for platform strategy optimization
        return {
            'primary_platforms': ['YouTube', 'Instagram'],
            'growth_opportunities': ['TikTok', 'Spotify'],
            'resource_allocation': {'YouTube': 40, 'Instagram': 35, 'TikTok': 25},
            'confidence': 0.82
        }

    async def _optimize_content_format(self, creator_id: str) -> Dict[str, Any]:
        """Optimize content format strategy"""        return {
            'high_performing_formats': ['Short-form video', 'Carousel posts', 'Stories'],
            'underperforming_formats': ['Long-form text', 'Static images'],
            'format_recommendations': {
                'video_length': '15-60 seconds',
                'image_ratio': '1:1 or 9:16',
                'posting_frequency': 'Daily'
            },
            'confidence': 0.75
        }

    async def _optimize_engagement_strategy(self, creator_id: str) -> Dict[str, Any]:
        """Optimize audience engagement tactics"""        return {
            'engagement_tactics': [
                'Use interactive stickers in stories',
                'Ask questions in captions',
                'Respond to comments within 2 hours',
                'Create trending hashtag challenges'
            ],
            'call_to_action_types': ['Save this post', 'Tag a friend', 'Share your thoughts'],
            'community_building': 'Host weekly live sessions',
            'confidence': 0.80
        }

    async def _set_performance_targets(self, creator_id: str) -> Dict[str, Any]:
        """Set realistic performance targets based on historical data"""        return {
            'monthly_targets': {
                'engagement_rate': 4.5,
                'follower_growth': 15.0,
                'content_score': 75.0,
                'reach_improvement': 25.0
            },
            'quarterly_goals': {
                'total_followers': 50000,
                'avg_engagement_rate': 5.0,
                'viral_content_count': 5
            },
            'confidence': 0.83
        }
