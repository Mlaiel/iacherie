"""
IA Influencer Agent - Traffic Analytics Manager
Enterprise traffic analysis and optimization for content protection platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
Project: IA Influencer Agent Platform - Content Protection & Monetization
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  AVERTISSEMENT SÉVÈRE ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact autorisations: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import geoip2.database
import geoip2.errors
from user_agents import parse as parse_user_agent
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiohttp

from prometheus_client import Counter, Histogram, Gauge

# Metrics
traffic_requests_total = Counter('traffic_requests_total', 'Total traffic requests', ['method', 'status', 'path', 'country'])
traffic_bandwidth_bytes = Counter('traffic_bandwidth_bytes', 'Traffic bandwidth in bytes', ['direction', 'content_type'])
user_sessions_active = Gauge('user_sessions_active', 'Active user sessions')
content_popularity_score = Gauge('content_popularity_score', 'Content popularity score', ['content_id', 'content_type'])

logger = logging.getLogger(__name__)


class TrafficType(Enum):
    """Types of network traffic"""
    WEB_TRAFFIC = "web"
    API_TRAFFIC = "api"
    CONTENT_DELIVERY = "content"
    UPLOAD_TRAFFIC = "upload"
    STREAMING_TRAFFIC = "streaming"
    FINGERPRINT_TRAFFIC = "fingerprint"
    PROTECTION_TRAFFIC = "protection"


class AnalyticsMetric(Enum):
    """Available analytics metrics"""
    BANDWIDTH_USAGE = "bandwidth_usage"
    REQUEST_COUNT = "request_count"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    GEOGRAPHIC_DISTRIBUTION = "geographic_distribution"
    DEVICE_DISTRIBUTION = "device_distribution"
    CONTENT_POPULARITY = "content_popularity"
    USER_ENGAGEMENT = "user_engagement"


class TrafficPattern(Enum):
    """Traffic patterns for optimization"""
    PEAK_HOURS = "peak_hours"
    OFF_PEAK = "off_peak"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"
    VIRAL_CONTENT = "viral_content"
    DDOS_ATTACK = "ddos_attack"
    BOT_TRAFFIC = "bot_traffic"


@dataclass
class TrafficData:
    """Individual traffic data point"""
    timestamp: datetime
    source_ip: str
    user_agent: str
    request_method: str
    request_path: str
    response_status: int
    response_size: int
    response_time: float
    content_type: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = None
    device_type: Optional[str] = None


@dataclass
class ContentAnalytics:
    """Content-specific analytics"""
    content_id: str
    content_type: str
    view_count: int
    unique_viewers: int
    total_bandwidth: int
    avg_view_duration: float
    geographic_distribution: Dict[str, int]
    device_distribution: Dict[str, int]
    engagement_score: float
    monetization_potential: float


@dataclass
class UserBehaviorMetrics:
    """User behavior analytics"""
    user_id: str
    session_count: int
    total_duration: timedelta
    content_types_viewed: List[str]
    engagement_patterns: Dict[str, float]
    geographic_locations: List[str]
    device_fingerprint: str
    conversion_events: List[Dict[str, Any]]


class TrafficAnalyticsManager:
    """
    Traffic Analytics Manager for IA Influencer Agent Platform
    Provides comprehensive traffic analysis and optimization insights
    """
    
    def __init__(
        self,
        database_url: str,
        redis_url: str = "redis://localhost:6379",
        geoip_database_path: str = "/etc/geoip/GeoLite2-City.mmdb"
    ):
        self.database_url = database_url
        self.redis_url = redis_url
        self.geoip_database_path = geoip_database_path
        
        # Database connections
        self.engine = None
        self.session_factory = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # GeoIP database
        self.geoip_reader = None
        
        # Analytics storage
        self.traffic_buffer: List[TrafficData] = []
        self.real_time_metrics: Dict[str, Any] = {}
        self.analytics_cache: Dict[str, Any] = {}
        
        # Machine learning models for predictions
        self.traffic_prediction_model = None
        self.anomaly_detection_model = None
        
        # Configuration
        self.buffer_size = 10000
        self.flush_interval = 60  # seconds
        self.analytics_retention_days = 90
    
    async def initialize(self) -> bool:
        """Initialize traffic analytics manager"""
        try:
            logger.info("Initializing Traffic Analytics Manager...")
            
            # Initialize database connection
            self.engine = create_async_engine(self.database_url)
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialize Redis
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize GeoIP database
            await self._initialize_geoip()
            
            # Load ML models
            await self._load_prediction_models()
            
            # Start background tasks
            asyncio.create_task(self._buffer_flush_loop())
            asyncio.create_task(self._real_time_analytics_loop())
            asyncio.create_task(self._anomaly_detection_loop())
            
            logger.info("Traffic Analytics Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Traffic Analytics Manager: {e}")
            return False
    
    async def record_traffic(self, traffic_data: TrafficData) -> None:
        """Record traffic data for analysis"""
        try:
            # Enrich traffic data
            enriched_data = await self._enrich_traffic_data(traffic_data)
            
            # Add to buffer
            self.traffic_buffer.append(enriched_data)
            
            # Update real-time metrics
            await self._update_real_time_metrics(enriched_data)
            
            # Check for anomalies
            await self._check_traffic_anomalies(enriched_data)
            
            # Update Prometheus metrics
            traffic_requests_total.labels(
                method=enriched_data.request_method,
                status=str(enriched_data.response_status),
                path=enriched_data.request_path,
                country=enriched_data.country or "unknown"
            ).inc()
            
            traffic_bandwidth_bytes.labels(
                direction="outbound",
                content_type=enriched_data.content_type or "unknown"
            ).inc(enriched_data.response_size)
            
            # Flush buffer if full
            if len(self.traffic_buffer) >= self.buffer_size:
                await self._flush_traffic_buffer()
            
        except Exception as e:
            logger.error(f"Failed to record traffic data: {e}")
    
    async def get_traffic_analytics(
        self,
        start_time: datetime,
        end_time: datetime,
        metrics: List[AnalyticsMetric],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive traffic analytics"""
        try:
            analytics_result = {
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'metrics': {},
                'summary': {},
                'insights': []
            }
            
            # Generate analytics for each requested metric
            for metric in metrics:
                metric_data = await self._calculate_metric(metric, start_time, end_time, filters)
                analytics_result['metrics'][metric.value] = metric_data
            
            # Generate summary statistics
            analytics_result['summary'] = await self._generate_summary_stats(start_time, end_time)
            
            # Generate AI insights
            analytics_result['insights'] = await self._generate_ai_insights(analytics_result['metrics'])
            
            return analytics_result
            
        except Exception as e:
            logger.error(f"Failed to get traffic analytics: {e}")
            return {}
    
    async def get_content_performance(
        self,
        content_id: str,
        time_range: timedelta = timedelta(days=7)
    ) -> Optional[ContentAnalytics]:
        """Get detailed content performance analytics"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_range
            
            # Query content metrics from database
            async with self.session_factory() as session:
                # Get basic metrics
                view_metrics = await self._get_content_view_metrics(session, content_id, start_time, end_time)
                
                # Get geographic distribution
                geo_distribution = await self._get_content_geo_distribution(session, content_id, start_time, end_time)
                
                # Get device distribution
                device_distribution = await self._get_content_device_distribution(session, content_id, start_time, end_time)
                
                # Calculate engagement metrics
                engagement_score = await self._calculate_content_engagement(session, content_id, start_time, end_time)
                
                # Calculate monetization potential
                monetization_potential = await self._calculate_monetization_potential(session, content_id)
            
            # Create content analytics object
            content_analytics = ContentAnalytics(
                content_id=content_id,
                content_type=view_metrics.get('content_type', 'unknown'),
                view_count=view_metrics.get('view_count', 0),
                unique_viewers=view_metrics.get('unique_viewers', 0),
                total_bandwidth=view_metrics.get('total_bandwidth', 0),
                avg_view_duration=view_metrics.get('avg_view_duration', 0.0),
                geographic_distribution=geo_distribution,
                device_distribution=device_distribution,
                engagement_score=engagement_score,
                monetization_potential=monetization_potential
            )
            
            # Update content popularity metric
            content_popularity_score.labels(
                content_id=content_id,
                content_type=content_analytics.content_type
            ).set(engagement_score)
            
            return content_analytics
            
        except Exception as e:
            logger.error(f"Failed to get content performance: {e}")
            return None
    
    async def get_user_behavior_analysis(
        self,
        user_id: str,
        time_range: timedelta = timedelta(days=30)
    ) -> Optional[UserBehaviorMetrics]:
        """Get detailed user behavior analysis"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_range
            
            async with self.session_factory() as session:
                # Get user session data
                session_data = await self._get_user_session_data(session, user_id, start_time, end_time)
                
                # Get content viewing patterns
                content_patterns = await self._get_user_content_patterns(session, user_id, start_time, end_time)
                
                # Get engagement patterns
                engagement_patterns = await self._calculate_user_engagement_patterns(session, user_id, start_time, end_time)
                
                # Get geographic data
                geo_locations = await self._get_user_geographic_data(session, user_id, start_time, end_time)
                
                # Get device fingerprint
                device_fingerprint = await self._get_user_device_fingerprint(session, user_id)
                
                # Get conversion events
                conversion_events = await self._get_user_conversion_events(session, user_id, start_time, end_time)
            
            user_metrics = UserBehaviorMetrics(
                user_id=user_id,
                session_count=session_data.get('session_count', 0),
                total_duration=timedelta(seconds=session_data.get('total_duration_seconds', 0)),
                content_types_viewed=content_patterns.get('content_types', []),
                engagement_patterns=engagement_patterns,
                geographic_locations=geo_locations,
                device_fingerprint=device_fingerprint,
                conversion_events=conversion_events
            )
            
            return user_metrics
            
        except Exception as e:
            logger.error(f"Failed to get user behavior analysis: {e}")
            return None
    
    async def predict_traffic_patterns(
        self,
        prediction_horizon: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Predict traffic patterns using ML models"""
        try:
            if not self.traffic_prediction_model:
                logger.warning("Traffic prediction model not loaded")
                return {}
            
            # Get historical data for prediction
            historical_data = await self._get_historical_traffic_data(timedelta(days=30))
            
            # Prepare features for prediction
            features = await self._prepare_prediction_features(historical_data)
            
            # Generate predictions
            predictions = await self._generate_traffic_predictions(features, prediction_horizon)
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_prediction_confidence(predictions)
            
            prediction_result = {
                'prediction_horizon': prediction_horizon.total_seconds(),
                'predictions': predictions,
                'confidence_intervals': confidence_intervals,
                'model_accuracy': await self._get_model_accuracy(),
                'recommendations': await self._generate_traffic_recommendations(predictions)
            }
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Failed to predict traffic patterns: {e}")
            return {}
    
    async def detect_traffic_anomalies(
        self,
        time_range: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """Detect traffic anomalies in recent data"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_range
            
            # Get recent traffic data
            recent_data = await self._get_traffic_data_range(start_time, end_time)
            
            # Apply anomaly detection
            anomalies = []
            
            # Check for unusual traffic volumes
            volume_anomalies = await self._detect_volume_anomalies(recent_data)
            anomalies.extend(volume_anomalies)
            
            # Check for unusual geographic patterns
            geo_anomalies = await self._detect_geographic_anomalies(recent_data)
            anomalies.extend(geo_anomalies)
            
            # Check for suspicious user agent patterns
            ua_anomalies = await self._detect_user_agent_anomalies(recent_data)
            anomalies.extend(ua_anomalies)
            
            # Check for DDoS patterns
            ddos_anomalies = await self._detect_ddos_patterns(recent_data)
            anomalies.extend(ddos_anomalies)
            
            # Rank anomalies by severity
            ranked_anomalies = sorted(anomalies, key=lambda x: x.get('severity_score', 0), reverse=True)
            
            return ranked_anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect traffic anomalies: {e}")
            return []
    
    async def optimize_content_delivery(
        self,
        content_analytics: List[ContentAnalytics]
    ) -> Dict[str, Any]:
        """Generate content delivery optimization recommendations"""
        try:
            optimization_recommendations = {
                'caching_strategies': {},
                'geo_distribution': {},
                'bandwidth_optimization': {},
                'performance_improvements': [],
                'cost_optimizations': []
            }
            
            for content in content_analytics:
                # Analyze content performance
                if content.engagement_score > 0.8:  # High engagement content
                    # Recommend aggressive caching
                    optimization_recommendations['caching_strategies'][content.content_id] = {
                        'strategy': 'aggressive',
                        'ttl': 86400,  # 24 hours
                        'reason': 'High engagement content benefits from aggressive caching'
                    }
                    
                    # Recommend global distribution
                    optimization_recommendations['geo_distribution'][content.content_id] = {
                        'regions': list(content.geographic_distribution.keys()),
                        'priority': 'high',
                        'reason': 'Popular content should be globally distributed'
                    }
                
                elif content.view_count < 100:  # Low-traffic content
                    # Recommend conservative caching
                    optimization_recommendations['caching_strategies'][content.content_id] = {
                        'strategy': 'conservative',
                        'ttl': 3600,  # 1 hour
                        'reason': 'Low-traffic content needs fresh delivery'
                    }
                
                # Bandwidth optimization for large content
                if content.total_bandwidth > 1000000000:  # 1GB
                    optimization_recommendations['bandwidth_optimization'][content.content_id] = {
                        'compression': True,
                        'format_optimization': True,
                        'adaptive_quality': True,
                        'reason': 'Large content benefits from compression and adaptive delivery'
                    }
            
            # Generate general performance improvements
            optimization_recommendations['performance_improvements'] = [
                'Implement adaptive bitrate streaming for video content',
                'Use WebP format for images in supported browsers',
                'Enable Brotli compression for text-based content',
                'Implement HTTP/3 for improved performance',
                'Use service workers for content pre-caching'
            ]
            
            # Generate cost optimizations
            optimization_recommendations['cost_optimizations'] = [
                'Archive rarely accessed content to cheaper storage tiers',
                'Use regional edge caches for local content',
                'Implement intelligent purging based on content lifecycle',
                'Optimize origin server costs through better caching strategies'
            ]
            
            return optimization_recommendations
            
        except Exception as e:
            logger.error(f"Failed to optimize content delivery: {e}")
            return {}
    
    async def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        try:
            dashboard_data = {
                'current_traffic': {},
                'active_users': 0,
                'top_content': [],
                'geographic_distribution': {},
                'alerts': [],
                'performance_metrics': {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Get current traffic metrics
            dashboard_data['current_traffic'] = await self._get_current_traffic_metrics()
            
            # Get active user count
            dashboard_data['active_users'] = await self._get_active_user_count()
            
            # Get top content by current views
            dashboard_data['top_content'] = await self._get_top_content_current()
            
            # Get geographic distribution
            dashboard_data['geographic_distribution'] = await self._get_current_geographic_distribution()
            
            # Get current alerts
            dashboard_data['alerts'] = await self._get_current_alerts()
            
            # Get performance metrics
            dashboard_data['performance_metrics'] = await self._get_current_performance_metrics()
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get real-time dashboard data: {e}")
            return {}
    
    # Private methods
    
    async def _enrich_traffic_data(self, traffic_data: TrafficData) -> TrafficData:
        """Enrich traffic data with additional information"""
        try:
            # Parse user agent
            if traffic_data.user_agent:
                ua = parse_user_agent(traffic_data.user_agent)
                traffic_data.device_type = f"{ua.device.family}-{ua.os.family}"
            
            # Get geographic information
            if traffic_data.source_ip and self.geoip_reader:
                try:
                    response = self.geoip_reader.city(traffic_data.source_ip)
                    traffic_data.country = response.country.iso_code
                except geoip2.errors.AddressNotFoundError:
                    traffic_data.country = "unknown"
            
            return traffic_data
            
        except Exception as e:
            logger.error(f"Failed to enrich traffic data: {e}")
            return traffic_data
    
    async def _initialize_geoip(self) -> None:
        """Initialize GeoIP database"""
        try:
            self.geoip_reader = geoip2.database.Reader(self.geoip_database_path)
            logger.info("GeoIP database initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize GeoIP database: {e}")
            self.geoip_reader = None
    
    async def _flush_traffic_buffer(self) -> None:
        """Flush traffic buffer to database"""
        try:
            if not self.traffic_buffer:
                return
            
            async with self.session_factory() as session:
                # Batch insert traffic data
                await self._batch_insert_traffic_data(session, self.traffic_buffer)
                await session.commit()
            
            # Clear buffer
            self.traffic_buffer.clear()
            
            logger.debug(f"Flushed traffic buffer to database")
            
        except Exception as e:
            logger.error(f"Failed to flush traffic buffer: {e}")
    
    async def _buffer_flush_loop(self) -> None:
        """Background task to flush traffic buffer"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_traffic_buffer()
            except Exception as e:
                logger.error(f"Buffer flush loop error: {e}")
                await asyncio.sleep(self.flush_interval)
    
    async def _real_time_analytics_loop(self) -> None:
        """Real-time analytics processing loop"""
        while True:
            try:
                # Update real-time metrics
                await self._update_real_time_dashboard()
                
                # Process recent data for insights
                await self._process_real_time_insights()
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Real-time analytics loop error: {e}")
                await asyncio.sleep(10)
    
    async def _anomaly_detection_loop(self) -> None:
        """Anomaly detection loop"""
        while True:
            try:
                # Run anomaly detection every 5 minutes
                await asyncio.sleep(300)
                
                anomalies = await self.detect_traffic_anomalies()
                
                # Handle critical anomalies
                for anomaly in anomalies:
                    if anomaly.get('severity_score', 0) > 0.8:
                        await self._handle_critical_anomaly(anomaly)
                
            except Exception as e:
                logger.error(f"Anomaly detection loop error: {e}")
                await asyncio.sleep(300)
