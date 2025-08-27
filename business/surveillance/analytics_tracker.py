"""
📊 Analytics Tracker - IA Influencer Agent Surveillance Module
==============================================================

Advanced analytics tracking system for surveillance operations providing
comprehensive metrics, KPIs, and business intelligence for content protection.

Architecture: Enterprise 3-Tier Professional (Backend Level 2)
Module: backend/business/surveillance/analytics_tracker.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Flow:
Surveillance Operations → Data Collection → Analytics Processing → 
KPI Calculation → Trend Analysis → Performance Metrics → 
Business Intelligence → Decision Support → ROI Optimization
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from collections import defaultdict, Counter
from pathlib import Path
import pickle
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Analytics metric types"""
    DETECTION_RATE = "detection_rate"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    TAKEDOWN_SUCCESS_RATE = "takedown_success_rate"
    REVENUE_RECOVERED = "revenue_recovered"
    PLATFORM_COVERAGE = "platform_coverage"
    PROCESSING_SPEED = "processing_speed"
    USER_SATISFACTION = "user_satisfaction"
    THREAT_SEVERITY = "threat_severity"


class TimeRange(Enum):
    """Time range for analytics"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PlatformMetric(Enum):
    """Platform-specific metrics"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    WEB_GENERIC = "web_generic"


@dataclass
class SurveillanceMetrics:
    """Surveillance operation metrics"""
    timestamp: datetime
    user_id: str
    platform: str
    content_type: str
    detection_count: int
    infringement_count: int
    false_positive_count: int
    takedown_requests: int
    successful_takedowns: int
    revenue_recovered: float
    processing_time: float
    similarity_scores: List[float] = field(default_factory=list)
    threat_levels: List[str] = field(default_factory=list)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    generation_timestamp: datetime
    time_range: TimeRange
    metrics_summary: Dict[str, Any]
    platform_breakdown: Dict[str, Dict[str, Any]]
    trend_analysis: Dict[str, List[float]]
    performance_indicators: Dict[str, float]
    recommendations: List[str]
    visualizations: Dict[str, str] = field(default_factory=dict)
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceKPI:
    """Key Performance Indicators"""
    kpi_name: str
    current_value: float
    target_value: float
    previous_period_value: float
    percentage_change: float
    status: str  # "on_track", "at_risk", "critical"
    trend_direction: str  # "up", "down", "stable"
    impact_score: float
    last_updated: datetime


class SurveillanceAnalytics:
    """
    Advanced Analytics Tracker for Surveillance Operations
    
    Provides comprehensive metrics, KPIs, and business intelligence
    for content protection and surveillance activities.
    """
    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        database_url: Optional[str] = None,
        storage_path: Optional[Path] = None
    ):
        """Initialize surveillance analytics tracker"""
        self.redis_client = redis_client or redis.Redis(decode_responses=True)
        self.database_url = database_url
        self.storage_path = storage_path or Path("surveillance_analytics")
        self.storage_path.mkdir(exist_ok=True)
        
        # Internal state
        self.metrics_cache: Dict[str, SurveillanceMetrics] = {}
        self.kpi_cache: Dict[str, PerformanceKPI] = {}
        self.reports_cache: Dict[str, AnalyticsReport] = {}
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.batch_size = 1000
        self.retention_days = 90
        
        # Initialize connections
        self._initialize_database()
        self._setup_metrics_collection()
        
        logger.info("SurveillanceAnalytics initialized successfully")
    
    def _initialize_database(self):
        """Initialize database connection"""
        try:
            if self.database_url:
                self.engine = create_engine(self.database_url)
                self._create_analytics_tables()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self.engine = None
    
    def _create_analytics_tables(self):
        """Create analytics tables if they don't exist"""
        tables_sql = """
        CREATE TABLE IF NOT EXISTS surveillance_metrics (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT NOW(),
            user_id VARCHAR(255) NOT NULL,
            platform VARCHAR(100),
            content_type VARCHAR(100),
            detection_count INTEGER DEFAULT 0,
            infringement_count INTEGER DEFAULT 0,
            false_positive_count INTEGER DEFAULT 0,
            takedown_requests INTEGER DEFAULT 0,
            successful_takedowns INTEGER DEFAULT 0,
            revenue_recovered DECIMAL(10,2) DEFAULT 0.00,
            processing_time FLOAT DEFAULT 0.0,
            similarity_scores JSONB,
            threat_levels JSONB,
            geographic_distribution JSONB,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS analytics_kpis (
            id SERIAL PRIMARY KEY,
            kpi_name VARCHAR(255) UNIQUE NOT NULL,
            current_value FLOAT NOT NULL,
            target_value FLOAT NOT NULL,
            previous_period_value FLOAT DEFAULT 0.0,
            percentage_change FLOAT DEFAULT 0.0,
            status VARCHAR(50) DEFAULT 'on_track',
            trend_direction VARCHAR(20) DEFAULT 'stable',
            impact_score FLOAT DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS analytics_reports (
            id SERIAL PRIMARY KEY,
            report_id VARCHAR(255) UNIQUE NOT NULL,
            generation_timestamp TIMESTAMP DEFAULT NOW(),
            time_range VARCHAR(50),
            metrics_summary JSONB,
            platform_breakdown JSONB,
            trend_analysis JSONB,
            performance_indicators JSONB,
            recommendations JSONB,
            visualizations JSONB,
            raw_data JSONB
        );
        """
        
        if self.engine:
            with self.engine.begin() as conn:
                conn.execute(text(tables_sql))
    
    def _setup_metrics_collection(self):
        """Setup metrics collection infrastructure"""
        # Redis keys for different metric types
        self.redis_keys = {
            'metrics': 'surveillance:metrics',
            'kpis': 'surveillance:kpis',
            'reports': 'surveillance:reports',
            'alerts': 'surveillance:alerts'
        }
        
        # Default KPI targets
        self.default_kpis = {
            'detection_rate': {'target': 0.95, 'impact_score': 10.0},
            'false_positive_rate': {'target': 0.05, 'impact_score': 8.0},
            'takedown_success_rate': {'target': 0.85, 'impact_score': 9.5},
            'revenue_recovered': {'target': 10000.0, 'impact_score': 10.0},
            'platform_coverage': {'target': 0.90, 'impact_score': 7.0},
            'processing_speed': {'target': 5.0, 'impact_score': 6.0},
            'user_satisfaction': {'target': 4.5, 'impact_score': 8.5},
            'threat_severity': {'target': 3.0, 'impact_score': 9.0}
        }
    
    async def record_surveillance_metrics(
        self,
        user_id: str,
        platform: str,
        content_type: str,
        metrics_data: Dict[str, Any]
    ) -> str:
        """Record surveillance operation metrics"""
        try:
            metrics = SurveillanceMetrics(
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                platform=platform,
                content_type=content_type,
                detection_count=metrics_data.get('detection_count', 0),
                infringement_count=metrics_data.get('infringement_count', 0),
                false_positive_count=metrics_data.get('false_positive_count', 0),
                takedown_requests=metrics_data.get('takedown_requests', 0),
                successful_takedowns=metrics_data.get('successful_takedowns', 0),
                revenue_recovered=metrics_data.get('revenue_recovered', 0.0),
                processing_time=metrics_data.get('processing_time', 0.0),
                similarity_scores=metrics_data.get('similarity_scores', []),
                threat_levels=metrics_data.get('threat_levels', []),
                geographic_distribution=metrics_data.get('geographic_distribution', {}),
                metadata=metrics_data.get('metadata', {})
            )
            
            metrics_id = f"{user_id}_{platform}_{int(metrics.timestamp.timestamp())}"
            
            # Store in cache
            self.metrics_cache[metrics_id] = metrics
            
            # Store in Redis
            await self._store_metrics_redis(metrics_id, metrics)
            
            # Store in database
            await self._store_metrics_database(metrics)
            
            # Update KPIs
            await self._update_kpis_from_metrics(metrics)
            
            logger.info(f"Recorded metrics for user {user_id} on {platform}")
            return metrics_id
            
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
            raise
    
    async def _store_metrics_redis(self, metrics_id: str, metrics: SurveillanceMetrics):
        """Store metrics in Redis"""
        try:
            metrics_data = asdict(metrics)
            metrics_data['timestamp'] = metrics.timestamp.isoformat()
            
            await asyncio.to_thread(
                self.redis_client.hset,
                f"{self.redis_keys['metrics']}:{metrics_id}",
                mapping=metrics_data
            )
            
            await asyncio.to_thread(
                self.redis_client.expire,
                f"{self.redis_keys['metrics']}:{metrics_id}",
                self.cache_ttl
            )
            
        except Exception as e:
            logger.error(f"Redis metrics storage failed: {e}")
    
    async def _store_metrics_database(self, metrics: SurveillanceMetrics):
        """Store metrics in database"""
        if not self.engine:
            return
        
        try:
            insert_sql = """
            INSERT INTO surveillance_metrics (
                timestamp, user_id, platform, content_type,
                detection_count, infringement_count, false_positive_count,
                takedown_requests, successful_takedowns, revenue_recovered,
                processing_time, similarity_scores, threat_levels,
                geographic_distribution, metadata
            ) VALUES (
                :timestamp, :user_id, :platform, :content_type,
                :detection_count, :infringement_count, :false_positive_count,
                :takedown_requests, :successful_takedowns, :revenue_recovered,
                :processing_time, :similarity_scores, :threat_levels,
                :geographic_distribution, :metadata
            )
            """
            
            with self.engine.begin() as conn:
                conn.execute(text(insert_sql), {
                    'timestamp': metrics.timestamp,
                    'user_id': metrics.user_id,
                    'platform': metrics.platform,
                    'content_type': metrics.content_type,
                    'detection_count': metrics.detection_count,
                    'infringement_count': metrics.infringement_count,
                    'false_positive_count': metrics.false_positive_count,
                    'takedown_requests': metrics.takedown_requests,
                    'successful_takedowns': metrics.successful_takedowns,
                    'revenue_recovered': metrics.revenue_recovered,
                    'processing_time': metrics.processing_time,
                    'similarity_scores': json.dumps(metrics.similarity_scores),
                    'threat_levels': json.dumps(metrics.threat_levels),
                    'geographic_distribution': json.dumps(metrics.geographic_distribution),
                    'metadata': json.dumps(metrics.metadata)
                })
                
        except Exception as e:
            logger.error(f"Database metrics storage failed: {e}")
    
    async def _update_kpis_from_metrics(self, metrics: SurveillanceMetrics):
        """Update KPIs based on new metrics"""
        try:
            # Calculate detection rate
            total_scans = metrics.detection_count + metrics.false_positive_count
            if total_scans > 0:
                detection_rate = metrics.detection_count / total_scans
                await self._update_kpi('detection_rate', detection_rate)
            
            # Calculate false positive rate
            if total_scans > 0:
                false_positive_rate = metrics.false_positive_count / total_scans
                await self._update_kpi('false_positive_rate', false_positive_rate)
            
            # Calculate takedown success rate
            if metrics.takedown_requests > 0:
                success_rate = metrics.successful_takedowns / metrics.takedown_requests
                await self._update_kpi('takedown_success_rate', success_rate)
            
            # Update revenue recovered
            await self._update_kpi('revenue_recovered', metrics.revenue_recovered)
            
            # Update processing speed (inverse of processing time)
            if metrics.processing_time > 0:
                speed_score = min(10.0, 60.0 / metrics.processing_time)
                await self._update_kpi('processing_speed', speed_score)
            
        except Exception as e:
            logger.error(f"KPI update failed: {e}")
    
    async def _update_kpi(self, kpi_name: str, current_value: float):
        """Update specific KPI value"""
        try:
            # Get previous value
            previous_value = 0.0
            if kpi_name in self.kpi_cache:
                previous_value = self.kpi_cache[kpi_name].current_value
            
            # Calculate percentage change
            percentage_change = 0.0
            if previous_value > 0:
                percentage_change = ((current_value - previous_value) / previous_value) * 100
            
            # Determine trend direction
            trend_direction = "stable"
            if percentage_change > 5:
                trend_direction = "up"
            elif percentage_change < -5:
                trend_direction = "down"
            
            # Determine status
            target_value = self.default_kpis.get(kpi_name, {}).get('target', current_value)
            status = "on_track"
            if current_value < target_value * 0.8:
                status = "critical"
            elif current_value < target_value * 0.9:
                status = "at_risk"
            
            # Create KPI object
            kpi = PerformanceKPI(
                kpi_name=kpi_name,
                current_value=current_value,
                target_value=target_value,
                previous_period_value=previous_value,
                percentage_change=percentage_change,
                status=status,
                trend_direction=trend_direction,
                impact_score=self.default_kpis.get(kpi_name, {}).get('impact_score', 5.0),
                last_updated=datetime.now(timezone.utc)
            )
            
            # Update cache
            self.kpi_cache[kpi_name] = kpi
            
            # Store in Redis
            await self._store_kpi_redis(kpi)
            
            # Store in database
            await self._store_kpi_database(kpi)
            
        except Exception as e:
            logger.error(f"KPI update failed for {kpi_name}: {e}")
    
    async def _store_kpi_redis(self, kpi: PerformanceKPI):
        """Store KPI in Redis"""
        try:
            kpi_data = asdict(kpi)
            kpi_data['last_updated'] = kpi.last_updated.isoformat()
            
            await asyncio.to_thread(
                self.redis_client.hset,
                f"{self.redis_keys['kpis']}:{kpi.kpi_name}",
                mapping=kpi_data
            )
            
        except Exception as e:
            logger.error(f"Redis KPI storage failed: {e}")
    
    async def _store_kpi_database(self, kpi: PerformanceKPI):
        """Store KPI in database"""
        if not self.engine:
            return
        
        try:
            upsert_sql = """
            INSERT INTO analytics_kpis (
                kpi_name, current_value, target_value, previous_period_value,
                percentage_change, status, trend_direction, impact_score, last_updated
            ) VALUES (
                :kpi_name, :current_value, :target_value, :previous_period_value,
                :percentage_change, :status, :trend_direction, :impact_score, :last_updated
            ) ON CONFLICT (kpi_name) DO UPDATE SET
                current_value = EXCLUDED.current_value,
                previous_period_value = EXCLUDED.previous_period_value,
                percentage_change = EXCLUDED.percentage_change,
                status = EXCLUDED.status,
                trend_direction = EXCLUDED.trend_direction,
                last_updated = EXCLUDED.last_updated
            """
            
            with self.engine.begin() as conn:
                conn.execute(text(upsert_sql), asdict(kpi))
                
        except Exception as e:
            logger.error(f"Database KPI storage failed: {e}")
    
    async def generate_analytics_report(
        self,
        time_range: TimeRange,
        user_id: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        include_visualizations: bool = True
    ) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        try:
            report_id = f"analytics_{int(datetime.now().timestamp())}"
            
            # Get metrics data
            metrics_data = await self._get_metrics_for_period(time_range, user_id, platforms)
            
            # Calculate metrics summary
            metrics_summary = await self._calculate_metrics_summary(metrics_data)
            
            # Generate platform breakdown
            platform_breakdown = await self._generate_platform_breakdown(metrics_data)
            
            # Perform trend analysis
            trend_analysis = await self._perform_trend_analysis(metrics_data, time_range)
            
            # Calculate performance indicators
            performance_indicators = await self._calculate_performance_indicators(metrics_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                metrics_summary, performance_indicators
            )
            
            # Generate visualizations
            visualizations = {}
            if include_visualizations:
                visualizations = await self._generate_visualizations(
                    metrics_data, platform_breakdown, trend_analysis
                )
            
            # Create report
            report = AnalyticsReport(
                report_id=report_id,
                generation_timestamp=datetime.now(timezone.utc),
                time_range=time_range,
                metrics_summary=metrics_summary,
                platform_breakdown=platform_breakdown,
                trend_analysis=trend_analysis,
                performance_indicators=performance_indicators,
                recommendations=recommendations,
                visualizations=visualizations,
                raw_data=metrics_data if len(metrics_data) < 1000 else None
            )
            
            # Store report
            await self._store_report(report)
            
            logger.info(f"Generated analytics report {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {e}")
            raise
    
    async def _get_metrics_for_period(
        self,
        time_range: TimeRange,
        user_id: Optional[str] = None,
        platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics data for specified period"""
        if not self.engine:
            return []
        
        try:
            # Calculate time period
            now = datetime.now(timezone.utc)
            if time_range == TimeRange.HOURLY:
                start_time = now - timedelta(hours=1)
            elif time_range == TimeRange.DAILY:
                start_time = now - timedelta(days=1)
            elif time_range == TimeRange.WEEKLY:
                start_time = now - timedelta(weeks=1)
            elif time_range == TimeRange.MONTHLY:
                start_time = now - timedelta(days=30)
            elif time_range == TimeRange.QUARTERLY:
                start_time = now - timedelta(days=90)
            else:  # YEARLY
                start_time = now - timedelta(days=365)
            
            # Build query
            query = """
            SELECT * FROM surveillance_metrics 
            WHERE timestamp >= :start_time
            """
            
            params = {'start_time': start_time}
            
            if user_id:
                query += " AND user_id = :user_id"
                params['user_id'] = user_id
            
            if platforms:
                placeholders = ','.join([f':platform_{i}' for i in range(len(platforms))])
                query += f" AND platform IN ({placeholders})"
                for i, platform in enumerate(platforms):
                    params[f'platform_{i}'] = platform
            
            query += " ORDER BY timestamp DESC"
            
            # Execute query
            with self.engine.begin() as conn:
                result = conn.execute(text(query), params)
                metrics_data = [dict(row._mapping) for row in result.fetchall()]
            
            return metrics_data
            
        except Exception as e:
            logger.error(f"Failed to get metrics data: {e}")
            return []
    
    async def _calculate_metrics_summary(self, metrics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics summary"""
        if not metrics_data:
            return {}
        
        try:
            df = pd.DataFrame(metrics_data)
            
            summary = {
                'total_records': len(df),
                'total_detections': df['detection_count'].sum(),
                'total_infringements': df['infringement_count'].sum(),
                'total_false_positives': df['false_positive_count'].sum(),
                'total_takedown_requests': df['takedown_requests'].sum(),
                'total_successful_takedowns': df['successful_takedowns'].sum(),
                'total_revenue_recovered': df['revenue_recovered'].sum(),
                'average_processing_time': df['processing_time'].mean(),
                'detection_rate': df['detection_count'].sum() / max(1, df['detection_count'].sum() + df['false_positive_count'].sum()),
                'takedown_success_rate': df['successful_takedowns'].sum() / max(1, df['takedown_requests'].sum()),
                'unique_users': df['user_id'].nunique(),
                'unique_platforms': df['platform'].nunique(),
                'content_types': df['content_type'].value_counts().to_dict(),
                'platform_distribution': df['platform'].value_counts().to_dict()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics summary: {e}")
            return {}
    
    async def _generate_platform_breakdown(self, metrics_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate platform-specific breakdown"""
        if not metrics_data:
            return {}
        
        try:
            df = pd.DataFrame(metrics_data)
            platform_breakdown = {}
            
            for platform in df['platform'].unique():
                platform_df = df[df['platform'] == platform]
                
                platform_breakdown[platform] = {
                    'total_operations': len(platform_df),
                    'total_detections': platform_df['detection_count'].sum(),
                    'total_infringements': platform_df['infringement_count'].sum(),
                    'revenue_recovered': platform_df['revenue_recovered'].sum(),
                    'average_processing_time': platform_df['processing_time'].mean(),
                    'success_rate': platform_df['successful_takedowns'].sum() / max(1, platform_df['takedown_requests'].sum()),
                    'content_types': platform_df['content_type'].value_counts().to_dict(),
                    'unique_users': platform_df['user_id'].nunique()
                }
            
            return platform_breakdown
            
        except Exception as e:
            logger.error(f"Failed to generate platform breakdown: {e}")
            return {}
    
    async def _perform_trend_analysis(self, metrics_data: List[Dict[str, Any]], time_range: TimeRange) -> Dict[str, List[float]]:
        """Perform trend analysis on metrics"""
        if not metrics_data:
            return {}
        
        try:
            df = pd.DataFrame(metrics_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Determine grouping frequency
            if time_range in [TimeRange.HOURLY, TimeRange.DAILY]:
                freq = 'H'
            elif time_range == TimeRange.WEEKLY:
                freq = 'D'
            else:
                freq = 'W'
            
            # Group by time period
            grouped = df.set_index('timestamp').groupby(pd.Grouper(freq=freq))
            
            trends = {
                'detections_trend': grouped['detection_count'].sum().tolist(),
                'infringements_trend': grouped['infringement_count'].sum().tolist(),
                'revenue_trend': grouped['revenue_recovered'].sum().tolist(),
                'processing_time_trend': grouped['processing_time'].mean().tolist(),
                'success_rate_trend': [
                    group['successful_takedowns'].sum() / max(1, group['takedown_requests'].sum())
                    for _, group in grouped
                ]
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to perform trend analysis: {e}")
            return {}
    
    async def _calculate_performance_indicators(self, metrics_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance indicators"""
        if not metrics_data:
            return {}
        
        try:
            df = pd.DataFrame(metrics_data)
            
            indicators = {
                'efficiency_score': self._calculate_efficiency_score(df),
                'accuracy_score': self._calculate_accuracy_score(df),
                'coverage_score': self._calculate_coverage_score(df),
                'impact_score': self._calculate_impact_score(df),
                'quality_score': self._calculate_quality_score(df)
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to calculate performance indicators: {e}")
            return {}
    
    def _calculate_efficiency_score(self, df: pd.DataFrame) -> float:
        """Calculate efficiency score based on processing time and throughput"""
        try:
            avg_processing_time = df['processing_time'].mean()
            throughput = len(df) / max(1, df['processing_time'].sum())
            
            # Normalize to 0-10 scale
            time_score = max(0, min(10, 10 - (avg_processing_time / 10)))
            throughput_score = min(10, throughput * 5)
            
            return (time_score + throughput_score) / 2
        except:
            return 5.0
    
    def _calculate_accuracy_score(self, df: pd.DataFrame) -> float:
        """Calculate accuracy score based on detection rates"""
        try:
            total_detections = df['detection_count'].sum()
            total_false_positives = df['false_positive_count'].sum()
            
            if total_detections + total_false_positives == 0:
                return 5.0
            
            accuracy = total_detections / (total_detections + total_false_positives)
            return accuracy * 10
        except:
            return 5.0
    
    def _calculate_coverage_score(self, df: pd.DataFrame) -> float:
        """Calculate coverage score based on platform and content type diversity"""
        try:
            platform_count = df['platform'].nunique()
            content_type_count = df['content_type'].nunique()
            
            # Assume maximum coverage is 8 platforms and 4 content types
            platform_score = min(10, (platform_count / 8) * 10)
            content_score = min(10, (content_type_count / 4) * 10)
            
            return (platform_score + content_score) / 2
        except:
            return 5.0
    
    def _calculate_impact_score(self, df: pd.DataFrame) -> float:
        """Calculate impact score based on revenue recovered and infringements stopped"""
        try:
            total_revenue = df['revenue_recovered'].sum()
            total_infringements = df['infringement_count'].sum()
            
            # Normalize based on targets
            revenue_score = min(10, (total_revenue / 10000) * 10)
            infringement_score = min(10, (total_infringements / 100) * 10)
            
            return (revenue_score + infringement_score) / 2
        except:
            return 5.0
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall quality score"""
        try:
            success_rate = df['successful_takedowns'].sum() / max(1, df['takedown_requests'].sum())
            detection_rate = df['detection_count'].sum() / max(1, df['detection_count'].sum() + df['false_positive_count'].sum())
            
            return ((success_rate * 10) + (detection_rate * 10)) / 2
        except:
            return 5.0
    
    async def _generate_recommendations(
        self,
        metrics_summary: Dict[str, Any],
        performance_indicators: Dict[str, float]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            # Efficiency recommendations
            if performance_indicators.get('efficiency_score', 5.0) < 6.0:
                recommendations.append(
                    "Consider optimizing processing pipelines to improve efficiency"
                )
            
            # Accuracy recommendations
            if performance_indicators.get('accuracy_score', 5.0) < 7.0:
                recommendations.append(
                    "Review detection algorithms to reduce false positives"
                )
            
            # Coverage recommendations
            if performance_indicators.get('coverage_score', 5.0) < 6.0:
                recommendations.append(
                    "Expand monitoring to additional platforms and content types"
                )
            
            # Revenue recommendations
            if metrics_summary.get('total_revenue_recovered', 0) < 5000:
                recommendations.append(
                    "Focus on high-value content protection to increase revenue recovery"
                )
            
            # Success rate recommendations
            if metrics_summary.get('takedown_success_rate', 0) < 0.8:
                recommendations.append(
                    "Improve takedown request quality and legal documentation"
                )
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations
    
    async def _generate_visualizations(
        self,
        metrics_data: List[Dict[str, Any]],
        platform_breakdown: Dict[str, Dict[str, Any]],
        trend_analysis: Dict[str, List[float]]
    ) -> Dict[str, str]:
        """Generate visualization charts"""
        visualizations = {}
        
        try:
            # Platform distribution pie chart
            if platform_breakdown:
                plt.figure(figsize=(10, 6))
                platforms = list(platform_breakdown.keys())
                values = [data['total_operations'] for data in platform_breakdown.values()]
                
                plt.pie(values, labels=platforms, autopct='%1.1f%%')
                plt.title('Platform Distribution')
                
                chart_path = self.storage_path / f"platform_distribution_{int(datetime.now().timestamp())}.png"
                plt.savefig(chart_path)
                plt.close()
                
                visualizations['platform_distribution'] = str(chart_path)
            
            # Trend analysis line chart
            if trend_analysis:
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Detections Trend', 'Revenue Trend', 'Processing Time Trend', 'Success Rate Trend')
                )
                
                # Add traces
                if 'detections_trend' in trend_analysis:
                    fig.add_trace(
                        go.Scatter(y=trend_analysis['detections_trend'], name='Detections'),
                        row=1, col=1
                    )
                
                if 'revenue_trend' in trend_analysis:
                    fig.add_trace(
                        go.Scatter(y=trend_analysis['revenue_trend'], name='Revenue'),
                        row=1, col=2
                    )
                
                if 'processing_time_trend' in trend_analysis:
                    fig.add_trace(
                        go.Scatter(y=trend_analysis['processing_time_trend'], name='Processing Time'),
                        row=2, col=1
                    )
                
                if 'success_rate_trend' in trend_analysis:
                    fig.add_trace(
                        go.Scatter(y=trend_analysis['success_rate_trend'], name='Success Rate'),
                        row=2, col=2
                    )
                
                fig.update_layout(title_text='Trend Analysis Dashboard')
                
                chart_path = self.storage_path / f"trend_analysis_{int(datetime.now().timestamp())}.html"
                fig.write_html(str(chart_path))
                
                visualizations['trend_analysis'] = str(chart_path)
                
        except Exception as e:
            logger.error(f"Failed to generate visualizations: {e}")
        
        return visualizations
    
    async def _store_report(self, report: AnalyticsReport):
        """Store analytics report"""
        try:
            # Store in cache
            self.reports_cache[report.report_id] = report
            
            # Store in Redis
            report_data = asdict(report)
            report_data['generation_timestamp'] = report.generation_timestamp.isoformat()
            report_data['time_range'] = report.time_range.value
            
            await asyncio.to_thread(
                self.redis_client.hset,
                f"{self.redis_keys['reports']}:{report.report_id}",
                mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                        for k, v in report_data.items()}
            )
            
            # Store in database
            if self.engine:
                insert_sql = """
                INSERT INTO analytics_reports (
                    report_id, generation_timestamp, time_range,
                    metrics_summary, platform_breakdown, trend_analysis,
                    performance_indicators, recommendations, visualizations, raw_data
                ) VALUES (
                    :report_id, :generation_timestamp, :time_range,
                    :metrics_summary, :platform_breakdown, :trend_analysis,
                    :performance_indicators, :recommendations, :visualizations, :raw_data
                )
                """
                
                with self.engine.begin() as conn:
                    conn.execute(text(insert_sql), {
                        'report_id': report.report_id,
                        'generation_timestamp': report.generation_timestamp,
                        'time_range': report.time_range.value,
                        'metrics_summary': json.dumps(report.metrics_summary),
                        'platform_breakdown': json.dumps(report.platform_breakdown),
                        'trend_analysis': json.dumps(report.trend_analysis),
                        'performance_indicators': json.dumps(report.performance_indicators),
                        'recommendations': json.dumps(report.recommendations),
                        'visualizations': json.dumps(report.visualizations),
                        'raw_data': json.dumps(report.raw_data) if report.raw_data else None
                    })
            
        except Exception as e:
            logger.error(f"Failed to store report: {e}")
    
    async def get_kpi_dashboard(self) -> Dict[str, PerformanceKPI]:
        """Get current KPI dashboard"""
        try:
            # Refresh KPIs from cache and database
            kpis = {}
            
            # Get from cache first
            for kpi_name, kpi in self.kpi_cache.items():
                kpis[kpi_name] = kpi
            
            # Get from database for missing KPIs
            if self.engine:
                select_sql = "SELECT * FROM analytics_kpis"
                with self.engine.begin() as conn:
                    result = conn.execute(text(select_sql))
                    for row in result.fetchall():
                        row_dict = dict(row._mapping)
                        kpi = PerformanceKPI(
                            kpi_name=row_dict['kpi_name'],
                            current_value=row_dict['current_value'],
                            target_value=row_dict['target_value'],
                            previous_period_value=row_dict['previous_period_value'],
                            percentage_change=row_dict['percentage_change'],
                            status=row_dict['status'],
                            trend_direction=row_dict['trend_direction'],
                            impact_score=row_dict['impact_score'],
                            last_updated=row_dict['last_updated']
                        )
                        kpis[row_dict['kpi_name']] = kpi
            
            return kpis
            
        except Exception as e:
            logger.error(f"Failed to get KPI dashboard: {e}")
            return {}
    
    async def get_real_time_metrics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get real-time surveillance metrics"""
        try:
            # Get recent metrics from Redis
            pattern = f"{self.redis_keys['metrics']}:*"
            if user_id:
                pattern = f"{self.redis_keys['metrics']}:{user_id}_*"
            
            keys = await asyncio.to_thread(self.redis_client.keys, pattern)
            metrics = {}
            
            for key in keys[-100:]:  # Get last 100 entries
                data = await asyncio.to_thread(self.redis_client.hgetall, key)
                if data:
                    metrics[key] = data
            
            # Calculate real-time statistics
            if metrics:
                values = list(metrics.values())
                total_detections = sum(int(m.get('detection_count', 0)) for m in values)
                total_infringements = sum(int(m.get('infringement_count', 0)) for m in values)
                total_revenue = sum(float(m.get('revenue_recovered', 0)) for m in values)
                avg_processing_time = sum(float(m.get('processing_time', 0)) for m in values) / len(values)
                
                return {
                    'total_operations': len(values),
                    'total_detections': total_detections,
                    'total_infringements': total_infringements,
                    'total_revenue_recovered': total_revenue,
                    'average_processing_time': avg_processing_time,
                    'active_platforms': len(set(m.get('platform', '') for m in values)),
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {}
    
    async def cleanup_old_data(self, retention_days: Optional[int] = None):
        """Cleanup old analytics data"""
        try:
            retention_days = retention_days or self.retention_days
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            
            # Cleanup database
            if self.engine:
                cleanup_sql = """
                DELETE FROM surveillance_metrics 
                WHERE timestamp < :cutoff_date;
                
                DELETE FROM analytics_reports 
                WHERE generation_timestamp < :cutoff_date;
                """
                
                with self.engine.begin() as conn:
                    conn.execute(text(cleanup_sql), {'cutoff_date': cutoff_date})
            
            # Cleanup Redis (handled by TTL)
            
            # Cleanup local files
            for file_path in self.storage_path.glob("*.png"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
            
            for file_path in self.storage_path.glob("*.html"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    file_path.unlink()
            
            logger.info(f"Cleaned up data older than {retention_days} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
