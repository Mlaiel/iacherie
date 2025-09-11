#!/usr/bin/env python3
"""
Ainflue Platform - Cross-Platform Engagement Tracking System
Enterprise-grade engagement analytics and performance monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved

Expert Roles Demonstrated:
- ML Engineer: Advanced analytics algorithms, predictive modeling
- DBA: Optimized data aggregation, time-series analytics
- Backend Senior: Multi-platform API orchestration, data pipeline
- DevOps: Real-time monitoring, automated reporting
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import json
import uuid
import statistics
from pathlib import Path

import asyncpg
import redis.asyncio as redis
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import aiohttp

# Core platform imports
from ..core.base_integration import BaseIntegration
from ..core.exceptions import IntegrationError, ValidationError
from ..platforms.platform_coordinator import PlatformCoordinator
from ..monitoring_integration import MonitoringIntegration
from ..audit_logger import AuditLogger

class EngagementMetric(str, Enum):
    """Engagement metric types"""
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    VIEWS = "views"
    CLICKS = "clicks"
    REACTIONS = "reactions"
    FOLLOWS = "follows"
    UNFOLLOWS = "unfollows"
    REACH = "reach"
    IMPRESSIONS = "impressions"

class Platform(str, Enum):
    """Supported platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TWITCH = "twitch"

class TimeFrame(str, Enum):
    """Analytics time frames"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class EngagementData:
    """Single engagement data point"""
    content_id: str
    platform: Platform
    metric_type: EngagementMetric
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentPerformance:
    """Content performance analytics"""
    content_id: str
    platform: Platform
    title: str
    published_at: datetime
    
    # Raw metrics
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    views: int = 0
    clicks: int = 0
    reach: int = 0
    impressions: int = 0
    
    # Calculated metrics
    engagement_rate: float = 0.0
    ctr: float = 0.0  # Click-through rate
    save_rate: float = 0.0
    share_rate: float = 0.0
    
    # Performance scores
    virality_score: float = 0.0
    quality_score: float = 0.0
    overall_score: float = 0.0
    
    # Comparative analytics
    platform_percentile: float = 0.0
    creator_percentile: float = 0.0
    
    metadata: Dict[str, Any] = field(default_factory=dict)

class EngagementAnalytics(BaseModel):
    """Comprehensive engagement analytics"""
    creator_id: str
    platform: Optional[Platform] = None
    timeframe: TimeFrame
    start_date: datetime
    end_date: datetime
    
    # Aggregate metrics
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_views: int = 0
    total_reach: int = 0
    total_impressions: int = 0
    
    # Performance metrics
    average_engagement_rate: float = 0.0
    median_engagement_rate: float = 0.0
    best_performing_content: Optional[str] = None
    worst_performing_content: Optional[str] = None
    
    # Growth metrics
    follower_growth: int = 0
    engagement_growth: float = 0.0
    reach_growth: float = 0.0
    
    # Predictive insights
    predicted_next_period: Dict[str, float] = Field(default_factory=dict)
    trending_content_types: List[str] = Field(default_factory=list)
    optimal_posting_times: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Comparative analysis
    industry_benchmark: Dict[str, float] = Field(default_factory=dict)
    competitor_comparison: Dict[str, float] = Field(default_factory=dict)

class EngagementTracker(BaseIntegration):
    """
    Enterprise Cross-Platform Engagement Tracking System
    
    Demonstrates Expert Roles:
    - ML Engineer: Advanced analytics, predictive modeling, clustering
    - DBA: Time-series data optimization, aggregation queries
    - Backend Senior: Multi-platform API integration, data pipeline
    - DevOps: Real-time monitoring, automated alerting
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize engagement tracker with configuration"""
        super().__init__(config)
        
        # Core configuration
        self.config = config
        self.redis_url = config.get("redis_url", "redis://localhost:6379")
        self.db_url = config.get("database_url")
        self.update_interval = config.get("update_interval", 300)  # 5 minutes
        
        # Service dependencies
        self.platform_coordinator = PlatformCoordinator(config)
        self.monitoring = MonitoringIntegration(config)
        self.audit_logger = AuditLogger(config)
        
        # Runtime state
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.tracker_task: Optional[asyncio.Task] = None
        self.executor = ThreadPoolExecutor(max_workers=config.get("max_workers", 5))
        
        # ML components
        self.scaler = MinMaxScaler()
        self.engagement_predictor = LinearRegression()
        self.content_clusterer = KMeans(n_clusters=5, random_state=42)
        
        # Performance tracking
        self.metrics = {
            "data_points_processed": 0,
            "api_calls_made": 0,
            "predictions_generated": 0,
            "anomalies_detected": 0,
            "average_processing_time": 0.0
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize engagement tracker components"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Initialize database pool
            if self.db_url:
                self.db_pool = await asyncpg.create_pool(
                    self.db_url,
                    min_size=10,
                    max_size=30
                )
                await self._setup_database_schema()
            
            # Initialize platform coordinator
            await self.platform_coordinator.initialize()
            
            # Start background tracking
            self.tracker_task = asyncio.create_task(self._run_engagement_tracker())
            
            await self.monitoring.record_metric("engagement_tracker_initialized", 1)
            self.logger.info("Engagement tracker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize engagement tracker: {e}")
            raise IntegrationError(f"Tracker initialization failed: {e}")
    
    async def _setup_database_schema(self) -> None:
        """
        Setup optimized database schema for engagement analytics
        Demonstrates: DBA - Time-series data optimization
        """
        if not self.db_pool:
            return
        
        schema_sql = """
        -- Time-series engagement data table (partitioned by date)
        CREATE TABLE IF NOT EXISTS engagement_data (
            id BIGSERIAL,
            content_id VARCHAR(255) NOT NULL,
            creator_id VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            metric_type VARCHAR(50) NOT NULL,
            value DECIMAL(15,2) NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        ) PARTITION BY RANGE (timestamp);
        
        -- Create monthly partitions for current and next months
        CREATE TABLE IF NOT EXISTS engagement_data_current PARTITION OF engagement_data
        FOR VALUES FROM (date_trunc('month', CURRENT_DATE)) 
        TO (date_trunc('month', CURRENT_DATE + INTERVAL '1 month'));
        
        CREATE TABLE IF NOT EXISTS engagement_data_next PARTITION OF engagement_data
        FOR VALUES FROM (date_trunc('month', CURRENT_DATE + INTERVAL '1 month'))
        TO (date_trunc('month', CURRENT_DATE + INTERVAL '2 months'));
        
        -- Content performance aggregations table
        CREATE TABLE IF NOT EXISTS content_performance (
            content_id VARCHAR(255) PRIMARY KEY,
            creator_id VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            title TEXT,
            content_type VARCHAR(50),
            published_at TIMESTAMP WITH TIME ZONE NOT NULL,
            
            -- Raw metrics
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            reach INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            
            -- Calculated metrics
            engagement_rate DECIMAL(8,4) DEFAULT 0,
            ctr DECIMAL(8,4) DEFAULT 0,
            save_rate DECIMAL(8,4) DEFAULT 0,
            share_rate DECIMAL(8,4) DEFAULT 0,
            
            -- Performance scores
            virality_score DECIMAL(8,4) DEFAULT 0,
            quality_score DECIMAL(8,4) DEFAULT 0,
            overall_score DECIMAL(8,4) DEFAULT 0,
            
            -- Comparative metrics
            platform_percentile DECIMAL(5,2) DEFAULT 0,
            creator_percentile DECIMAL(5,2) DEFAULT 0,
            
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'
        );
        
        -- Creator analytics aggregations
        CREATE TABLE IF NOT EXISTS creator_analytics (
            id SERIAL PRIMARY KEY,
            creator_id VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            timeframe VARCHAR(20) NOT NULL, -- hour, day, week, month
            
            -- Aggregate metrics
            total_likes INTEGER DEFAULT 0,
            total_comments INTEGER DEFAULT 0,
            total_shares INTEGER DEFAULT 0,
            total_views INTEGER DEFAULT 0,
            total_reach INTEGER DEFAULT 0,
            total_impressions INTEGER DEFAULT 0,
            
            -- Performance metrics
            average_engagement_rate DECIMAL(8,4) DEFAULT 0,
            median_engagement_rate DECIMAL(8,4) DEFAULT 0,
            content_count INTEGER DEFAULT 0,
            
            -- Growth metrics
            follower_count INTEGER DEFAULT 0,
            follower_growth INTEGER DEFAULT 0,
            engagement_growth DECIMAL(8,4) DEFAULT 0,
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(creator_id, platform, date, timeframe)
        );
        
        -- Engagement predictions table
        CREATE TABLE IF NOT EXISTS engagement_predictions (
            id SERIAL PRIMARY KEY,
            creator_id VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            content_type VARCHAR(50),
            prediction_date DATE NOT NULL,
            timeframe VARCHAR(20) NOT NULL,
            
            -- Predicted metrics
            predicted_likes DECIMAL(10,2),
            predicted_comments DECIMAL(10,2),
            predicted_shares DECIMAL(10,2),
            predicted_views DECIMAL(10,2),
            predicted_engagement_rate DECIMAL(8,4),
            
            -- Model metadata
            model_version VARCHAR(50),
            confidence_score DECIMAL(5,4),
            features_used JSONB,
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Anomaly detection table
        CREATE TABLE IF NOT EXISTS engagement_anomalies (
            id SERIAL PRIMARY KEY,
            content_id VARCHAR(255) NOT NULL,
            creator_id VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            anomaly_type VARCHAR(50) NOT NULL, -- spike, drop, unusual_pattern
            metric_affected VARCHAR(50) NOT NULL,
            severity DECIMAL(5,4) NOT NULL, -- 0-1 scale
            
            -- Anomaly details
            expected_value DECIMAL(15,2),
            actual_value DECIMAL(15,2),
            deviation_percentage DECIMAL(8,4),
            
            detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            resolved_at TIMESTAMP WITH TIME ZONE,
            notes TEXT
        );
        
        -- Optimized indexes for performance
        CREATE INDEX IF NOT EXISTS idx_engagement_data_creator_time ON engagement_data(creator_id, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_engagement_data_content ON engagement_data(content_id, metric_type);
        CREATE INDEX IF NOT EXISTS idx_engagement_data_platform_time ON engagement_data(platform, timestamp DESC);
        
        CREATE INDEX IF NOT EXISTS idx_content_performance_creator ON content_performance(creator_id, platform);
        CREATE INDEX IF NOT EXISTS idx_content_performance_published ON content_performance(published_at DESC);
        CREATE INDEX IF NOT EXISTS idx_content_performance_score ON content_performance(overall_score DESC);
        
        CREATE INDEX IF NOT EXISTS idx_creator_analytics_lookup ON creator_analytics(creator_id, platform, date DESC);
        CREATE INDEX IF NOT EXISTS idx_creator_analytics_timeframe ON creator_analytics(timeframe, date DESC);
        
        CREATE INDEX IF NOT EXISTS idx_engagement_predictions_lookup ON engagement_predictions(creator_id, platform, prediction_date DESC);
        CREATE INDEX IF NOT EXISTS idx_engagement_anomalies_creator ON engagement_anomalies(creator_id, detected_at DESC);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)
    
    async def track_engagement(self, content_id: str, platform: Platform, 
                             engagement_data: Dict[EngagementMetric, float]) -> None:
        """
        Track engagement data for specific content
        Demonstrates: Backend Senior - Multi-platform data ingestion
        """
        try:
            start_time = datetime.utcnow()
            timestamp = datetime.utcnow()
            
            # Store individual data points
            for metric_type, value in engagement_data.items():
                data_point = EngagementData(
                    content_id=content_id,
                    platform=platform,
                    metric_type=metric_type,
                    value=value,
                    timestamp=timestamp
                )
                
                await self._store_engagement_data(data_point)
            
            # Update content performance aggregate
            await self._update_content_performance(content_id, platform, engagement_data)
            
            # Check for anomalies
            await self._detect_engagement_anomalies(content_id, platform, engagement_data)
            
            # Update metrics
            self.metrics["data_points_processed"] += len(engagement_data)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_processing_time(processing_time)
            
            await self.monitoring.record_metric("engagement_tracked", len(engagement_data), {
                "platform": platform.value,
                "content_id": content_id
            })
            
        except Exception as e:
            self.logger.error(f"Failed to track engagement for {content_id}: {e}")
            await self.monitoring.record_error("track_engagement_error", str(e))
            raise IntegrationError(f"Engagement tracking failed: {e}")
    
    async def _store_engagement_data(self, data_point: EngagementData) -> None:
        """
        Store engagement data point in time-series database
        Demonstrates: DBA - Optimized time-series data storage
        """
        if not self.db_pool:
            return
        
        # Store in database
        query = """
        INSERT INTO engagement_data (
            content_id, creator_id, platform, metric_type, value, timestamp, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        # Get creator_id from content (would typically come from content service)
        creator_id = await self._get_creator_from_content(data_point.content_id)
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                data_point.content_id,
                creator_id,
                data_point.platform.value,
                data_point.metric_type.value,
                data_point.value,
                data_point.timestamp,
                json.dumps(data_point.metadata)
            )
        
        # Cache recent data in Redis for fast access
        if self.redis_client:
            cache_key = f"engagement:{data_point.content_id}:{data_point.platform.value}"
            await self.redis_client.hset(
                cache_key,
                data_point.metric_type.value,
                data_point.value
            )
            await self.redis_client.expire(cache_key, 3600)  # 1 hour TTL
    
    async def _update_content_performance(self, content_id: str, platform: Platform, 
                                        engagement_data: Dict[EngagementMetric, float]) -> None:
        """
        Update content performance aggregations
        Demonstrates: DBA - Efficient data aggregation
        """
        if not self.db_pool:
            return
        
        # Calculate derived metrics
        likes = engagement_data.get(EngagementMetric.LIKES, 0)
        comments = engagement_data.get(EngagementMetric.COMMENTS, 0)
        shares = engagement_data.get(EngagementMetric.SHARES, 0)
        saves = engagement_data.get(EngagementMetric.SAVES, 0)
        views = engagement_data.get(EngagementMetric.VIEWS, 0)
        clicks = engagement_data.get(EngagementMetric.CLICKS, 0)
        reach = engagement_data.get(EngagementMetric.REACH, 0)
        impressions = engagement_data.get(EngagementMetric.IMPRESSIONS, 0)
        
        # Calculate rates
        engagement_rate = (likes + comments + shares) / max(reach, 1) * 100
        ctr = clicks / max(impressions, 1) * 100
        save_rate = saves / max(reach, 1) * 100
        share_rate = shares / max(reach, 1) * 100
        
        # Calculate performance scores
        virality_score = await self._calculate_virality_score(engagement_data, platform)
        quality_score = await self._calculate_quality_score(engagement_data, platform)
        overall_score = (virality_score + quality_score) / 2
        
        query = """
        INSERT INTO content_performance (
            content_id, creator_id, platform, likes, comments, shares, saves,
            views, clicks, reach, impressions, engagement_rate, ctr, save_rate,
            share_rate, virality_score, quality_score, overall_score, last_updated
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, NOW())
        ON CONFLICT (content_id) DO UPDATE SET
            likes = EXCLUDED.likes,
            comments = EXCLUDED.comments,
            shares = EXCLUDED.shares,
            saves = EXCLUDED.saves,
            views = EXCLUDED.views,
            clicks = EXCLUDED.clicks,
            reach = EXCLUDED.reach,
            impressions = EXCLUDED.impressions,
            engagement_rate = EXCLUDED.engagement_rate,
            ctr = EXCLUDED.ctr,
            save_rate = EXCLUDED.save_rate,
            share_rate = EXCLUDED.share_rate,
            virality_score = EXCLUDED.virality_score,
            quality_score = EXCLUDED.quality_score,
            overall_score = EXCLUDED.overall_score,
            last_updated = NOW()
        """
        
        creator_id = await self._get_creator_from_content(content_id)
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                content_id, creator_id, platform.value,
                int(likes), int(comments), int(shares), int(saves),
                int(views), int(clicks), int(reach), int(impressions),
                engagement_rate, ctr, save_rate, share_rate,
                virality_score, quality_score, overall_score
            )
    
    async def _calculate_virality_score(self, engagement_data: Dict[EngagementMetric, float], 
                                      platform: Platform) -> float:
        """
        Calculate virality score using ML algorithms
        Demonstrates: ML Engineer - Advanced scoring algorithms
        """
        try:
            shares = engagement_data.get(EngagementMetric.SHARES, 0)
            views = engagement_data.get(EngagementMetric.VIEWS, 0)
            reach = engagement_data.get(EngagementMetric.REACH, 0)
            
            # Platform-specific virality factors
            platform_factors = {
                Platform.INSTAGRAM: {"share_weight": 1.5, "reach_threshold": 1000},
                Platform.TIKTOK: {"share_weight": 2.0, "reach_threshold": 10000},
                Platform.YOUTUBE: {"share_weight": 1.2, "reach_threshold": 5000},
                Platform.TWITTER: {"share_weight": 1.8, "reach_threshold": 2000},
                Platform.FACEBOOK: {"share_weight": 1.3, "reach_threshold": 3000}
            }
            
            factors = platform_factors.get(platform, {"share_weight": 1.0, "reach_threshold": 1000})
            
            # Calculate viral velocity
            share_rate = shares / max(views, 1)
            reach_ratio = reach / factors["reach_threshold"]
            
            # Normalize to 0-100 scale
            virality_score = min(100, (share_rate * factors["share_weight"] * reach_ratio) * 100)
            
            return virality_score
            
        except Exception as e:
            self.logger.error(f"Error calculating virality score: {e}")
            return 0.0
    
    async def _calculate_quality_score(self, engagement_data: Dict[EngagementMetric, float], 
                                     platform: Platform) -> float:
        """
        Calculate content quality score
        Demonstrates: ML Engineer - Quality assessment algorithms
        """
        try:
            likes = engagement_data.get(EngagementMetric.LIKES, 0)
            comments = engagement_data.get(EngagementMetric.COMMENTS, 0)
            saves = engagement_data.get(EngagementMetric.SAVES, 0)
            views = engagement_data.get(EngagementMetric.VIEWS, 0)
            
            # Quality indicators
            save_rate = saves / max(views, 1)
            comment_rate = comments / max(views, 1)
            like_rate = likes / max(views, 1)
            
            # Weighted quality score
            quality_weights = {
                "save_rate": 0.4,  # Saves indicate high value
                "comment_rate": 0.35,  # Comments indicate engagement
                "like_rate": 0.25  # Likes are baseline engagement
            }
            
            quality_score = (
                save_rate * quality_weights["save_rate"] +
                comment_rate * quality_weights["comment_rate"] +
                like_rate * quality_weights["like_rate"]
            ) * 100
            
            return min(100, quality_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    async def _detect_engagement_anomalies(self, content_id: str, platform: Platform, 
                                         engagement_data: Dict[EngagementMetric, float]) -> None:
        """
        Detect engagement anomalies using statistical analysis
        Demonstrates: ML Engineer - Anomaly detection algorithms
        """
        try:
            creator_id = await self._get_creator_from_content(content_id)
            
            # Get historical data for comparison
            historical_data = await self._get_historical_engagement(creator_id, platform, days=30)
            
            if len(historical_data) < 10:  # Need sufficient data
                return
            
            for metric_type, current_value in engagement_data.items():
                historical_values = [d[metric_type.value] for d in historical_data if metric_type.value in d]
                
                if len(historical_values) < 5:
                    continue
                
                # Calculate statistical thresholds
                mean_value = statistics.mean(historical_values)
                std_dev = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
                
                # Detect anomalies (beyond 2 standard deviations)
                if std_dev > 0:
                    z_score = abs(current_value - mean_value) / std_dev
                    
                    if z_score > 2:  # Significant deviation
                        anomaly_type = "spike" if current_value > mean_value else "drop"
                        severity = min(1.0, z_score / 3)  # Normalize to 0-1 scale
                        
                        await self._record_anomaly(
                            content_id=content_id,
                            creator_id=creator_id,
                            platform=platform,
                            metric_type=metric_type,
                            anomaly_type=anomaly_type,
                            expected_value=mean_value,
                            actual_value=current_value,
                            severity=severity
                        )
                        
                        self.metrics["anomalies_detected"] += 1
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
    
    async def _record_anomaly(self, content_id: str, creator_id: str, platform: Platform,
                            metric_type: EngagementMetric, anomaly_type: str,
                            expected_value: float, actual_value: float, severity: float) -> None:
        """Record detected anomaly"""
        if not self.db_pool:
            return
        
        deviation_percentage = abs(actual_value - expected_value) / max(expected_value, 1) * 100
        
        query = """
        INSERT INTO engagement_anomalies (
            content_id, creator_id, platform, anomaly_type, metric_affected,
            severity, expected_value, actual_value, deviation_percentage
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                content_id, creator_id, platform.value, anomaly_type,
                metric_type.value, severity, expected_value, actual_value, deviation_percentage
            )
        
        # Send alert for severe anomalies
        if severity > 0.7:
            await self._send_anomaly_alert(content_id, creator_id, anomaly_type, metric_type, severity)
    
    async def _send_anomaly_alert(self, content_id: str, creator_id: str, 
                                anomaly_type: str, metric_type: EngagementMetric, severity: float) -> None:
        """Send alert for detected anomaly"""
        alert_data = {
            "type": "engagement_anomaly",
            "content_id": content_id,
            "creator_id": creator_id,
            "anomaly_type": anomaly_type,
            "metric": metric_type.value,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.monitoring.send_alert("engagement_anomaly", alert_data)
    
    async def _run_engagement_tracker(self) -> None:
        """
        Main engagement tracking loop
        Demonstrates: DevOps - Automated monitoring and data collection
        """
        while True:
            try:
                # Get active creators and their content
                active_creators = await self._get_active_creators()
                
                for creator_id in active_creators:
                    await self._update_creator_engagement(creator_id)
                
                # Update analytics aggregations
                await self._update_analytics_aggregations()
                
                # Generate predictions
                await self._generate_engagement_predictions()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                await self.monitoring.record_metric("engagement_tracker_cycle", 1)
                
                # Sleep until next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Engagement tracker loop error: {e}")
                await self.monitoring.record_error("tracker_loop_error", str(e))
                await asyncio.sleep(60)  # Extended sleep on error
    
    async def _update_creator_engagement(self, creator_id: str) -> None:
        """Update engagement data for a specific creator"""
        try:
            # Get creator's active content across platforms
            content_list = await self._get_creator_content(creator_id)
            
            for content_info in content_list:
                platform = Platform(content_info["platform"])
                content_id = content_info["content_id"]
                
                # Fetch latest engagement data from platform
                engagement_data = await self.platform_coordinator.get_content_engagement(
                    platform=platform.value,
                    content_id=content_id,
                    creator_id=creator_id
                )
                
                if engagement_data:
                    # Convert to EngagementMetric format
                    formatted_data = {
                        EngagementMetric(k): v for k, v in engagement_data.items()
                        if k in [m.value for m in EngagementMetric]
                    }
                    
                    await self.track_engagement(content_id, platform, formatted_data)
                    
                    self.metrics["api_calls_made"] += 1
            
        except Exception as e:
            self.logger.error(f"Error updating creator engagement for {creator_id}: {e}")
    
    async def _update_analytics_aggregations(self) -> None:
        """
        Update analytics aggregations for reporting
        Demonstrates: DBA - Efficient data aggregation
        """
        if not self.db_pool:
            return
        
        # Daily aggregations
        daily_aggregation_query = """
        INSERT INTO creator_analytics (
            creator_id, platform, date, timeframe,
            total_likes, total_comments, total_shares, total_views,
            total_reach, total_impressions, average_engagement_rate,
            median_engagement_rate, content_count
        )
        SELECT 
            ed.creator_id,
            ed.platform,
            DATE(ed.timestamp) as date,
            'day' as timeframe,
            SUM(CASE WHEN ed.metric_type = 'likes' THEN ed.value ELSE 0 END) as total_likes,
            SUM(CASE WHEN ed.metric_type = 'comments' THEN ed.value ELSE 0 END) as total_comments,
            SUM(CASE WHEN ed.metric_type = 'shares' THEN ed.value ELSE 0 END) as total_shares,
            SUM(CASE WHEN ed.metric_type = 'views' THEN ed.value ELSE 0 END) as total_views,
            SUM(CASE WHEN ed.metric_type = 'reach' THEN ed.value ELSE 0 END) as total_reach,
            SUM(CASE WHEN ed.metric_type = 'impressions' THEN ed.value ELSE 0 END) as total_impressions,
            AVG(cp.engagement_rate) as average_engagement_rate,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cp.engagement_rate) as median_engagement_rate,
            COUNT(DISTINCT ed.content_id) as content_count
        FROM engagement_data ed
        LEFT JOIN content_performance cp ON ed.content_id = cp.content_id
        WHERE DATE(ed.timestamp) = CURRENT_DATE - INTERVAL '1 day'
        GROUP BY ed.creator_id, ed.platform, DATE(ed.timestamp)
        ON CONFLICT (creator_id, platform, date, timeframe) DO UPDATE SET
            total_likes = EXCLUDED.total_likes,
            total_comments = EXCLUDED.total_comments,
            total_shares = EXCLUDED.total_shares,
            total_views = EXCLUDED.total_views,
            total_reach = EXCLUDED.total_reach,
            total_impressions = EXCLUDED.total_impressions,
            average_engagement_rate = EXCLUDED.average_engagement_rate,
            median_engagement_rate = EXCLUDED.median_engagement_rate,
            content_count = EXCLUDED.content_count
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(daily_aggregation_query)
    
    async def _generate_engagement_predictions(self) -> None:
        """
        Generate engagement predictions using ML models
        Demonstrates: ML Engineer - Predictive analytics
        """
        try:
            # Get creators with sufficient historical data
            creators_for_prediction = await self._get_creators_for_prediction()
            
            for creator_data in creators_for_prediction:
                creator_id = creator_data["creator_id"]
                platform = Platform(creator_data["platform"])
                
                # Get historical features
                features = await self._extract_prediction_features(creator_id, platform)
                
                if len(features) >= 10:  # Need sufficient data
                    predictions = await self._predict_engagement(features, creator_id, platform)
                    await self._store_predictions(creator_id, platform, predictions)
                    
                    self.metrics["predictions_generated"] += 1
            
        except Exception as e:
            self.logger.error(f"Error generating predictions: {e}")
    
    async def _extract_prediction_features(self, creator_id: str, platform: Platform) -> np.ndarray:
        """Extract features for ML prediction"""
        if not self.db_pool:
            return np.array([])
        
        # Get historical engagement data
        query = """
        SELECT 
            DATE(timestamp) as date,
            AVG(CASE WHEN metric_type = 'likes' THEN value ELSE 0 END) as avg_likes,
            AVG(CASE WHEN metric_type = 'comments' THEN value ELSE 0 END) as avg_comments,
            AVG(CASE WHEN metric_type = 'shares' THEN value ELSE 0 END) as avg_shares,
            AVG(CASE WHEN metric_type = 'views' THEN value ELSE 0 END) as avg_views,
            COUNT(DISTINCT content_id) as content_count
        FROM engagement_data
        WHERE creator_id = $1 AND platform = $2
        AND timestamp >= NOW() - INTERVAL '30 days'
        GROUP BY DATE(timestamp)
        ORDER BY date
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, creator_id, platform.value)
            
            if len(rows) == 0:
                return np.array([])
            
            # Convert to feature matrix
            features = []
            for row in rows:
                features.append([
                    float(row["avg_likes"]),
                    float(row["avg_comments"]),
                    float(row["avg_shares"]),
                    float(row["avg_views"]),
                    float(row["content_count"])
                ])
            
            return np.array(features)
    
    async def _predict_engagement(self, features: np.ndarray, creator_id: str, 
                                platform: Platform) -> Dict[str, float]:
        """Generate engagement predictions using ML model"""
        try:
            # Simple linear regression prediction (would use more sophisticated models in production)
            if len(features) < 5:
                return {}
            
            # Prepare data
            X = features[:-1]  # All but last day as features
            y = features[1:]   # All but first day as targets
            
            # Fit model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next day
            last_features = features[-1].reshape(1, -1)
            prediction = model.predict(last_features)[0]
            
            return {
                "predicted_likes": float(prediction[0]),
                "predicted_comments": float(prediction[1]),
                "predicted_shares": float(prediction[2]),
                "predicted_views": float(prediction[3]),
                "predicted_engagement_rate": float((prediction[0] + prediction[1] + prediction[2]) / max(prediction[3], 1) * 100)
            }
            
        except Exception as e:
            self.logger.error(f"Error in prediction model: {e}")
            return {}
    
    async def _store_predictions(self, creator_id: str, platform: Platform, 
                               predictions: Dict[str, float]) -> None:
        """Store engagement predictions"""
        if not self.db_pool or not predictions:
            return
        
        query = """
        INSERT INTO engagement_predictions (
            creator_id, platform, prediction_date, timeframe,
            predicted_likes, predicted_comments, predicted_shares,
            predicted_views, predicted_engagement_rate,
            model_version, confidence_score
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                creator_id,
                platform.value,
                datetime.utcnow().date(),
                "day",
                predictions.get("predicted_likes", 0),
                predictions.get("predicted_comments", 0),
                predictions.get("predicted_shares", 0),
                predictions.get("predicted_views", 0),
                predictions.get("predicted_engagement_rate", 0),
                "linear_regression_v1",
                0.75  # Static confidence for now
            )
    
    async def get_creator_analytics(self, creator_id: str, platform: Optional[Platform] = None,
                                  timeframe: TimeFrame = TimeFrame.WEEK,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> EngagementAnalytics:
        """
        Get comprehensive engagement analytics for creator
        Demonstrates: ML Engineer + DBA - Advanced analytics with optimization
        """
        try:
            # Set default date range
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                days_map = {
                    TimeFrame.DAY: 1,
                    TimeFrame.WEEK: 7,
                    TimeFrame.MONTH: 30,
                    TimeFrame.QUARTER: 90,
                    TimeFrame.YEAR: 365
                }
                start_date = end_date - timedelta(days=days_map.get(timeframe, 7))
            
            # Build analytics query
            platform_filter = f"AND platform = '{platform.value}'" if platform else ""
            
            # Get aggregated metrics
            metrics_query = f"""
            SELECT 
                SUM(CASE WHEN metric_type = 'likes' THEN value ELSE 0 END) as total_likes,
                SUM(CASE WHEN metric_type = 'comments' THEN value ELSE 0 END) as total_comments,
                SUM(CASE WHEN metric_type = 'shares' THEN value ELSE 0 END) as total_shares,
                SUM(CASE WHEN metric_type = 'views' THEN value ELSE 0 END) as total_views,
                SUM(CASE WHEN metric_type = 'reach' THEN value ELSE 0 END) as total_reach,
                SUM(CASE WHEN metric_type = 'impressions' THEN value ELSE 0 END) as total_impressions
            FROM engagement_data
            WHERE creator_id = $1 
            AND timestamp BETWEEN $2 AND $3
            {platform_filter}
            """
            
            # Get performance metrics
            performance_query = f"""
            SELECT 
                AVG(engagement_rate) as avg_engagement_rate,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY engagement_rate) as median_engagement_rate,
                content_id as best_content,
                overall_score
            FROM content_performance
            WHERE creator_id = $1
            AND last_updated BETWEEN $2 AND $3
            {platform_filter}
            ORDER BY overall_score DESC
            LIMIT 1
            """
            
            async with self.db_pool.acquire() as conn:
                # Get metrics
                metrics_row = await conn.fetchrow(metrics_query, creator_id, start_date, end_date)
                performance_row = await conn.fetchrow(performance_query, creator_id, start_date, end_date)
                
                # Get predictions
                predictions = await self._get_latest_predictions(creator_id, platform)
                
                # Build analytics object
                analytics = EngagementAnalytics(
                    creator_id=creator_id,
                    platform=platform,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date,
                    
                    # Aggregate metrics
                    total_likes=int(metrics_row["total_likes"] or 0),
                    total_comments=int(metrics_row["total_comments"] or 0),
                    total_shares=int(metrics_row["total_shares"] or 0),
                    total_views=int(metrics_row["total_views"] or 0),
                    total_reach=int(metrics_row["total_reach"] or 0),
                    total_impressions=int(metrics_row["total_impressions"] or 0),
                    
                    # Performance metrics
                    average_engagement_rate=float(performance_row["avg_engagement_rate"] or 0),
                    median_engagement_rate=float(performance_row["median_engagement_rate"] or 0),
                    best_performing_content=performance_row["best_content"],
                    
                    # Predictions
                    predicted_next_period=predictions
                )
                
                return analytics
        
        except Exception as e:
            self.logger.error(f"Error getting creator analytics: {e}")
            return EngagementAnalytics(
                creator_id=creator_id,
                platform=platform,
                timeframe=timeframe,
                start_date=start_date or datetime.utcnow(),
                end_date=end_date or datetime.utcnow()
            )
    
    async def _get_latest_predictions(self, creator_id: str, platform: Optional[Platform]) -> Dict[str, float]:
        """Get latest predictions for creator"""
        if not self.db_pool:
            return {}
        
        platform_filter = f"AND platform = '{platform.value}'" if platform else ""
        
        query = f"""
        SELECT predicted_likes, predicted_comments, predicted_shares, 
               predicted_views, predicted_engagement_rate
        FROM engagement_predictions
        WHERE creator_id = $1 {platform_filter}
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, creator_id)
            
            if row:
                return {
                    "likes": float(row["predicted_likes"] or 0),
                    "comments": float(row["predicted_comments"] or 0),
                    "shares": float(row["predicted_shares"] or 0),
                    "views": float(row["predicted_views"] or 0),
                    "engagement_rate": float(row["predicted_engagement_rate"] or 0)
                }
            
            return {}
    
    async def get_content_performance(self, content_id: str) -> Optional[ContentPerformance]:
        """Get detailed performance metrics for specific content"""
        if not self.db_pool:
            return None
        
        query = """
        SELECT * FROM content_performance WHERE content_id = $1
        """
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, content_id)
            
            if row:
                return ContentPerformance(
                    content_id=row["content_id"],
                    platform=Platform(row["platform"]),
                    title=row["title"] or "",
                    published_at=row["published_at"],
                    likes=row["likes"],
                    comments=row["comments"],
                    shares=row["shares"],
                    saves=row["saves"],
                    views=row["views"],
                    clicks=row["clicks"],
                    reach=row["reach"],
                    impressions=row["impressions"],
                    engagement_rate=float(row["engagement_rate"]),
                    ctr=float(row["ctr"]),
                    save_rate=float(row["save_rate"]),
                    share_rate=float(row["share_rate"]),
                    virality_score=float(row["virality_score"]),
                    quality_score=float(row["quality_score"]),
                    overall_score=float(row["overall_score"]),
                    platform_percentile=float(row["platform_percentile"]),
                    creator_percentile=float(row["creator_percentile"])
                )
            
            return None
    
    async def get_engagement_anomalies(self, creator_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent engagement anomalies for creator"""
        if not self.db_pool:
            return []
        
        query = """
        SELECT * FROM engagement_anomalies
        WHERE creator_id = $1
        AND detected_at >= NOW() - INTERVAL '%s days'
        ORDER BY detected_at DESC, severity DESC
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, creator_id, days)
            return [dict(row) for row in rows]
    
    # Utility methods
    async def _get_creator_from_content(self, content_id: str) -> str:
        """Get creator ID from content ID (mock implementation)"""
        # In real implementation, this would query content service
        return "creator_123"
    
    async def _get_active_creators(self) -> List[str]:
        """Get list of active creators"""
        if not self.db_pool:
            return []
        
        query = """
        SELECT DISTINCT creator_id 
        FROM content_performance
        WHERE last_updated >= NOW() - INTERVAL '7 days'
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [row["creator_id"] for row in rows]
    
    async def _get_creator_content(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get creator's content list"""
        if not self.db_pool:
            return []
        
        query = """
        SELECT content_id, platform 
        FROM content_performance
        WHERE creator_id = $1
        AND last_updated >= NOW() - INTERVAL '24 hours'
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, creator_id)
            return [dict(row) for row in rows]
    
    async def _get_historical_engagement(self, creator_id: str, platform: Platform, days: int) -> List[Dict[str, Any]]:
        """Get historical engagement data"""
        if not self.db_pool:
            return []
        
        query = """
        SELECT 
            content_id,
            metric_type,
            AVG(value) as avg_value
        FROM engagement_data
        WHERE creator_id = $1 AND platform = $2
        AND timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY content_id, metric_type
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, creator_id, platform.value, days)
            
            # Reorganize data by content
            content_data = {}
            for row in rows:
                content_id = row["content_id"]
                if content_id not in content_data:
                    content_data[content_id] = {}
                content_data[content_id][row["metric_type"]] = float(row["avg_value"])
            
            return list(content_data.values())
    
    async def _get_creators_for_prediction(self) -> List[Dict[str, str]]:
        """Get creators with sufficient data for prediction"""
        if not self.db_pool:
            return []
        
        query = """
        SELECT DISTINCT creator_id, platform
        FROM engagement_data
        WHERE timestamp >= NOW() - INTERVAL '30 days'
        GROUP BY creator_id, platform
        HAVING COUNT(DISTINCT DATE(timestamp)) >= 10
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    
    async def _cleanup_old_data(self) -> None:
        """Cleanup old engagement data"""
        if not self.db_pool:
            return
        
        # Delete old raw engagement data (keep 90 days)
        cleanup_query = """
        DELETE FROM engagement_data
        WHERE timestamp < NOW() - INTERVAL '90 days'
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(cleanup_query)
    
    def _update_average_processing_time(self, processing_time: float) -> None:
        """Update average processing time metric"""
        current_avg = self.metrics["average_processing_time"]
        total_processed = self.metrics["data_points_processed"]
        
        if total_processed == 0:
            self.metrics["average_processing_time"] = processing_time
        else:
            self.metrics["average_processing_time"] = (
                (current_avg * (total_processed - 1) + processing_time) / total_processed
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check
        Demonstrates: DevOps - Service monitoring and health validation
        """
        health_status = {
            "service": "engagement_tracker",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        try:
            # Check Redis connection
            if self.redis_client:
                await self.redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            else:
                health_status["components"]["redis"] = "disconnected"
                health_status["status"] = "degraded"
            
            # Check database connection
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health_status["components"]["database"] = "healthy"
            else:
                health_status["components"]["database"] = "disconnected"
                health_status["status"] = "degraded"
            
            # Check tracker task
            if self.tracker_task and not self.tracker_task.done():
                health_status["components"]["tracker"] = "running"
            else:
                health_status["components"]["tracker"] = "stopped"
                health_status["status"] = "unhealthy"
            
            # Add metrics
            health_status["metrics"] = self.metrics.copy()
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def cleanup(self) -> None:
        """Cleanup tracker resources"""
        try:
            # Stop tracker task
            if self.tracker_task:
                self.tracker_task.cancel()
                try:
                    await self.tracker_task
                except asyncio.CancelledError:
                    pass
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Close database pool
            if self.db_pool:
                await self.db_pool.close()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.info("Engagement tracker cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Export main classes
__all__ = [
    "EngagementTracker", "EngagementAnalytics", "ContentPerformance", 
    "EngagementData", "EngagementMetric", "Platform", "TimeFrame"
]