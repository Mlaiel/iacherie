"""
Time Series Database Configuration Module for IA-Influencer Agent Platform
=========================================================================

Professional time series database configuration for analytics, monitoring,
content performance tracking, and revenue analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import aioredis
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd

logger = logging.getLogger(__name__)


class TimeSeriesDBType(Enum):
    """Supported time series database types"""
    INFLUXDB = "influxdb"
    PROMETHEUS = "prometheus"
    TIMESCALE = "timescale"
    REDIS_TIMESERIES = "redis_timeseries"


class MetricType(Enum):
    """Metric types for different business domains"""
    CONTENT_PERFORMANCE = "content_performance"
    REVENUE_ANALYTICS = "revenue_analytics"
    PLATFORM_METRICS = "platform_metrics"
    PROTECTION_ALERTS = "protection_alerts"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_PERFORMANCE = "system_performance"


class AggregationType(Enum):
    """Data aggregation types"""
    SUM = "sum"
    AVERAGE = "avg"
    COUNT = "count"
    MAX = "max"
    MIN = "min"
    PERCENTILE = "percentile"
    DERIVATIVE = "derivative"


@dataclass
class TimeSeriesCredentials:
    """Time series database authentication"""
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    organization: Optional[str] = None
    bucket: Optional[str] = None
    url: str = "http://localhost:8086"


@dataclass
class RetentionPolicy:
    """Data retention configuration"""
    raw_data_retention: str = "30d"  # Raw data retention
    hourly_aggregation_retention: str = "90d"  # Hourly aggregates
    daily_aggregation_retention: str = "1y"  # Daily aggregates
    monthly_aggregation_retention: str = "5y"  # Monthly aggregates
    auto_downsampling: bool = True
    compression_enabled: bool = True


@dataclass
class MetricDefinition:
    """Definition of time series metric"""
    name: str
    metric_type: MetricType
    tags: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    retention_policy: str = "default"
    aggregation_functions: List[AggregationType] = field(default_factory=list)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class TimeSeriesConfig:
    """Professional time series database configuration"""
    # Database configuration
    db_type: TimeSeriesDBType = TimeSeriesDBType.INFLUXDB
    credentials: TimeSeriesCredentials = field(default_factory=TimeSeriesCredentials)
    
    # Connection settings
    connection_pool_size: int = 10
    connection_timeout: int = 10
    read_timeout: int = 30
    write_timeout: int = 10
    max_retries: int = 3
    retry_interval: int = 5
    
    # Write configuration
    batch_size: int = 1000
    flush_interval: int = 10000  # milliseconds
    precision: str = "ms"  # Timestamp precision
    write_consistency: str = "one"
    
    # Query configuration
    default_query_timeout: int = 30
    max_series_per_query: int = 10000
    chunk_size: int = 10000
    
    # Retention policies
    retention_policies: Dict[str, RetentionPolicy] = field(
        default_factory=lambda: {
            "default": RetentionPolicy(),
            "high_frequency": RetentionPolicy(
                raw_data_retention="7d",
                hourly_aggregation_retention="30d",
                daily_aggregation_retention="180d"
            ),
            "analytics": RetentionPolicy(
                raw_data_retention="90d",
                hourly_aggregation_retention="1y",
                daily_aggregation_retention="3y"
            )
        }
    )
    
    # Metric definitions for IA-Influencer business logic
    metric_definitions: Dict[str, MetricDefinition] = field(
        default_factory=lambda: {
            "content_views": MetricDefinition(
                name="content_views",
                metric_type=MetricType.CONTENT_PERFORMANCE,
                tags=["user_id", "content_id", "platform", "content_type"],
                fields=["view_count", "unique_views", "watch_time"],
                aggregation_functions=[AggregationType.SUM, AggregationType.COUNT]
            ),
            "revenue_tracking": MetricDefinition(
                name="revenue_tracking",
                metric_type=MetricType.REVENUE_ANALYTICS,
                tags=["user_id", "platform", "revenue_type", "currency"],
                fields=["amount", "commission", "net_amount"],
                aggregation_functions=[AggregationType.SUM, AggregationType.AVERAGE],
                alert_thresholds={"daily_drop_percentage": 0.2}
            ),
            "protection_violations": MetricDefinition(
                name="protection_violations",
                metric_type=MetricType.PROTECTION_ALERTS,
                tags=["content_id", "platform", "violation_type", "severity"],
                fields=["violation_count", "similarity_score", "confidence"],
                aggregation_functions=[AggregationType.COUNT, AggregationType.MAX],
                alert_thresholds={"high_similarity": 0.9}
            ),
            "platform_engagement": MetricDefinition(
                name="platform_engagement", 
                metric_type=MetricType.USER_ENGAGEMENT,
                tags=["user_id", "platform", "engagement_type"],
                fields=["likes", "shares", "comments", "saves"],
                aggregation_functions=[AggregationType.SUM, AggregationType.AVERAGE]
            ),
            "system_performance": MetricDefinition(
                name="system_performance",
                metric_type=MetricType.SYSTEM_PERFORMANCE,
                tags=["service", "endpoint", "method"],
                fields=["response_time", "error_rate", "throughput"],
                aggregation_functions=[AggregationType.AVERAGE, AggregationType.PERCENTILE],
                alert_thresholds={"response_time_p95": 2000, "error_rate": 0.05}
            )
        }
    )
    
    # Alerting configuration
    alerting_enabled: bool = True
    alert_evaluation_interval: int = 60  # seconds
    alert_notification_channels: List[str] = field(default_factory=list)
    
    # Performance optimization
    enable_compression: bool = True
    enable_caching: bool = True
    cache_size_mb: int = 256
    parallel_queries: bool = True
    max_concurrent_queries: int = 20


class TimeSeriesManager:
    """Professional time series database manager"""
    
    def __init__(self, config: TimeSeriesConfig):
        self.config = config
        self.client = None
        self.write_api = None
        self.query_api = None
        self._connection_pool = None
        
    async def initialize(self) -> bool:
        """Initialize time series database connection"""
        try:
            if self.config.db_type == TimeSeriesDBType.INFLUXDB:
                await self._initialize_influxdb()
            elif self.config.db_type == TimeSeriesDBType.REDIS_TIMESERIES:
                await self._initialize_redis_timeseries()
            else:
                logger.warning(f"Database type {self.config.db_type} not fully implemented")
                return False
                
            logger.info(f"Time series database initialized: {self.config.db_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize time series database: {e}")
            return False
            
    async def _initialize_influxdb(self):
        """Initialize InfluxDB connection"""
        self.client = InfluxDBClient(
            url=self.config.credentials.url,
            token=self.config.credentials.token,
            org=self.config.credentials.organization
        )
        
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        
        # Verify connection
        health = self.client.health()
        if health.status != "pass":
            raise ConnectionError("InfluxDB health check failed")
            
    async def _initialize_redis_timeseries(self):
        """Initialize Redis TimeSeries connection"""
        self._connection_pool = aioredis.ConnectionPool.from_url(
            self.config.credentials.url,
            max_connections=self.config.connection_pool_size
        )
        self.client = aioredis.Redis(connection_pool=self._connection_pool)
        
    async def write_metrics(
        self,
        metric_name: str,
        tags: Dict[str, str],
        fields: Dict[str, Union[int, float]],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Write metrics to time series database"""
        try:
            if not timestamp:
                timestamp = datetime.utcnow()
                
            if self.config.db_type == TimeSeriesDBType.INFLUXDB:
                return await self._write_influxdb_metrics(
                    metric_name, tags, fields, timestamp
                )
            elif self.config.db_type == TimeSeriesDBType.REDIS_TIMESERIES:
                return await self._write_redis_metrics(
                    metric_name, tags, fields, timestamp
                )
            else:
                logger.warning(f"Write not implemented for {self.config.db_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing metrics: {e}")
            return False
            
    async def _write_influxdb_metrics(
        self,
        metric_name: str,
        tags: Dict[str, str],
        fields: Dict[str, Union[int, float]],
        timestamp: datetime
    ) -> bool:
        """Write metrics to InfluxDB"""
        try:
            point = Point(metric_name)
            
            # Add tags
            for key, value in tags.items():
                point = point.tag(key, value)
                
            # Add fields
            for key, value in fields.items():
                point = point.field(key, value)
                
            # Set timestamp
            point = point.time(timestamp)
            
            # Write to database
            self.write_api.write(
                bucket=self.config.credentials.bucket,
                record=point
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}")
            return False
            
    async def _write_redis_metrics(
        self,
        metric_name: str,
        tags: Dict[str, str],
        fields: Dict[str, Union[int, float]],
        timestamp: datetime
    ) -> bool:
        """Write metrics to Redis TimeSeries"""
        try:
            timestamp_ms = int(timestamp.timestamp() * 1000)
            
            for field_name, value in fields.items():
                # Create time series key
                key_parts = [metric_name, field_name]
                for tag_key, tag_value in sorted(tags.items()):
                    key_parts.append(f"{tag_key}_{tag_value}")
                    
                ts_key = ":".join(key_parts)
                
                # Add data point
                await self.client.ts().add(ts_key, timestamp_ms, value)
                
            return True
            
        except Exception as e:
            logger.error(f"Error writing to Redis TimeSeries: {e}")
            return False
            
    async def query_metrics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        tags: Optional[Dict[str, str]] = None,
        aggregation: Optional[AggregationType] = None,
        interval: str = "1m"
    ) -> pd.DataFrame:
        """Query metrics from time series database"""
        try:
            if self.config.db_type == TimeSeriesDBType.INFLUXDB:
                return await self._query_influxdb_metrics(
                    metric_name, start_time, end_time, tags, aggregation, interval
                )
            elif self.config.db_type == TimeSeriesDBType.REDIS_TIMESERIES:
                return await self._query_redis_metrics(
                    metric_name, start_time, end_time, tags, aggregation, interval
                )
            else:
                logger.warning(f"Query not implemented for {self.config.db_type}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error querying metrics: {e}")
            return pd.DataFrame()
            
    async def _query_influxdb_metrics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        tags: Optional[Dict[str, str]],
        aggregation: Optional[AggregationType],
        interval: str
    ) -> pd.DataFrame:
        """Query metrics from InfluxDB"""
        try:
            # Build Flux query
            query_parts = [
                f'from(bucket: "{self.config.credentials.bucket}")',
                f'|> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})',
                f'|> filter(fn: (r) => r._measurement == "{metric_name}")'
            ]
            
            # Add tag filters
            if tags:
                for key, value in tags.items():
                    query_parts.append(f'|> filter(fn: (r) => r.{key} == "{value}")')
                    
            # Add aggregation
            if aggregation:
                if aggregation == AggregationType.SUM:
                    query_parts.append(f'|> aggregateWindow(every: {interval}, fn: sum)')
                elif aggregation == AggregationType.AVERAGE:
                    query_parts.append(f'|> aggregateWindow(every: {interval}, fn: mean)')
                elif aggregation == AggregationType.COUNT:
                    query_parts.append(f'|> aggregateWindow(every: {interval}, fn: count)')
                elif aggregation == AggregationType.MAX:
                    query_parts.append(f'|> aggregateWindow(every: {interval}, fn: max)')
                elif aggregation == AggregationType.MIN:
                    query_parts.append(f'|> aggregateWindow(every: {interval}, fn: min)')
                    
            query = '\n  '.join(query_parts)
            
            # Execute query
            result = self.query_api.query_data_frame(query)
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying InfluxDB: {e}")
            return pd.DataFrame()
            
    async def _query_redis_metrics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        tags: Optional[Dict[str, str]],
        aggregation: Optional[AggregationType],
        interval: str
    ) -> pd.DataFrame:
        """Query metrics from Redis TimeSeries"""
        # Redis TimeSeries query implementation
        # This would require Redis TimeSeries specific query logic
        logger.info("Redis TimeSeries query not fully implemented")
        return pd.DataFrame()
        
    async def get_content_performance_metrics(
        self,
        content_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive content performance metrics"""
        try:
            # Query multiple metrics for content performance
            views_df = await self.query_metrics(
                "content_views",
                start_time,
                end_time,
                tags={"content_id": content_id},
                aggregation=AggregationType.SUM,
                interval="1h"
            )
            
            engagement_df = await self.query_metrics(
                "platform_engagement",
                start_time,
                end_time,
                tags={"content_id": content_id},
                aggregation=AggregationType.SUM,
                interval="1h"
            )
            
            revenue_df = await self.query_metrics(
                "revenue_tracking", 
                start_time,
                end_time,
                tags={"content_id": content_id},
                aggregation=AggregationType.SUM,
                interval="1h"
            )
            
            # Combine metrics
            return {
                "content_id": content_id,
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "views": views_df.to_dict('records') if not views_df.empty else [],
                "engagement": engagement_df.to_dict('records') if not engagement_df.empty else [],
                "revenue": revenue_df.to_dict('records') if not revenue_df.empty else [],
                "summary": {
                    "total_views": views_df['view_count'].sum() if not views_df.empty else 0,
                    "total_engagement": engagement_df['likes'].sum() if not engagement_df.empty else 0,
                    "total_revenue": revenue_df['amount'].sum() if not revenue_df.empty else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting content performance metrics: {e}")
            return {"error": str(e)}
            
    async def get_protection_analytics(
        self,
        start_time: datetime,
        end_time: datetime,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get content protection analytics"""
        try:
            tags = {}
            if user_id:
                tags["user_id"] = user_id
                
            violations_df = await self.query_metrics(
                "protection_violations",
                start_time,
                end_time,
                tags=tags,
                aggregation=AggregationType.COUNT,
                interval="1h"
            )
            
            return {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "violations": violations_df.to_dict('records') if not violations_df.empty else [],
                "summary": {
                    "total_violations": len(violations_df) if not violations_df.empty else 0,
                    "high_confidence_violations": len(
                        violations_df[violations_df.get('confidence', 0) > 0.9]
                    ) if not violations_df.empty else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting protection analytics: {e}")
            return {"error": str(e)}
            
    async def close(self):
        """Close database connections"""
        try:
            if self.client:
                if hasattr(self.client, 'close'):
                    self.client.close()
                    
            if self._connection_pool:
                await self._connection_pool.disconnect()
                
            logger.info("Time series database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing time series database: {e}")


def create_timeseries_config(
    environment: str = "development",
    custom_settings: Optional[Dict[str, Any]] = None
) -> TimeSeriesConfig:
    """Factory function to create time series configuration"""
    
    # Environment-specific defaults
    config_defaults = {
        "development": {
            "db_type": TimeSeriesDBType.INFLUXDB,
            "batch_size": 100,
            "flush_interval": 5000,
            "alerting_enabled": False
        },
        "staging": {
            "db_type": TimeSeriesDBType.INFLUXDB,
            "batch_size": 500,
            "flush_interval": 10000,
            "alerting_enabled": True
        },
        "production": {
            "db_type": TimeSeriesDBType.INFLUXDB,
            "batch_size": 1000,
            "flush_interval": 10000,
            "alerting_enabled": True,
            "enable_compression": True,
            "enable_caching": True
        }
    }
    
    defaults = config_defaults.get(environment, config_defaults["development"])
    
    # Merge with custom settings
    if custom_settings:
        defaults.update(custom_settings)
    
    # Create credentials from environment
    credentials = TimeSeriesCredentials(
        url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
        token=os.getenv("INFLUXDB_TOKEN"),
        organization=os.getenv("INFLUXDB_ORG", "ia-influencer"),
        bucket=os.getenv("INFLUXDB_BUCKET", f"metrics_{environment}")
    )
    
    defaults["credentials"] = credentials
    
    return TimeSeriesConfig(**defaults)
