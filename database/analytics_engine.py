"""📊 Analytics Engine - Real-time Analytics & Business Intelligence
====================================================================
Module: database/analytics_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Real-time Analytics & Monitoring - Production-Ready
Responsibility: Advanced analytics, monitoring and business intelligence

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This analytics engine provides comprehensive analytics for:
- Real-time database analytics and monitoring
- Query performance analysis and optimization
- Business intelligence data aggregation
- Creator workflow analytics
- Revenue tracking and monetization analytics
- Platform usage and engagement metrics
"""

import os
import json
import time
import logging
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

# Optional imports for production features
try:
    import sqlalchemy
    from sqlalchemy import text, func, and_, or_, desc, asc
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    sqlalchemy = None

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Configure logging
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Analytics metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class AnalyticsEvent(Enum):
    """Analytics event type enumeration"""
    USER_CREATED = "user_created"
    USER_LOGIN = "user_login"
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_VIEWED = "content_viewed"
    CONTENT_SHARED = "content_shared"
    REVENUE_GENERATED = "revenue_generated"
    QUERY_EXECUTED = "query_executed"
    ERROR_OCCURRED = "error_occurred"

@dataclass
class Metric:
    """Represents an analytics metric"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    tags: Dict[str, str]
    timestamp: datetime.datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'tags': self.tags,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class AnalyticsResult:
    """Analytics query result"""
    query_name: str
    data: Any
    metadata: Dict[str, Any]
    timestamp: datetime.datetime
    execution_time_ms: float

@dataclass
class PerformanceMetrics:
    """Database performance metrics"""
    query_count: int
    avg_query_time: float
    slow_queries: int
    connection_count: int
    cache_hit_ratio: float
    error_rate: float
    timestamp: datetime.datetime

class AnalyticsEngine:
    """Real-time analytics and business intelligence engine"""
    
    def __init__(self, connection=None, redis_client=None, cache_ttl: int = 3600):
        self.connection = connection
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.query_cache: Dict[str, Any] = {}
        self.performance_history: deque = deque(maxlen=1000)
        self.event_handlers: Dict[AnalyticsEvent, List[Callable]] = defaultdict(list)
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._lock = threading.Lock()
        self._initialize_analytics()
    
    def _initialize_analytics(self):
        """Initialize analytics system"""
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # Create analytics tables if they don't exist
                self._create_analytics_tables()
            
            # Initialize Redis connection if available
            if REDIS_AVAILABLE and not self.redis_client:
                try:
                    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                    self.redis_client.ping()  # Test connection
                    logger.info("Redis connection established for analytics")
                except Exception as e:
                    logger.warning(f"Failed to connect to Redis: {e}")
                    self.redis_client = None
            
            logger.info("Analytics engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics engine: {e}")
    
    def _create_analytics_tables(self):
        """Create analytics tracking tables"""
        try:
            # Analytics events table
            create_events_table = """
            CREATE TABLE IF NOT EXISTS analytics_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                event_data JSON,
                user_id INTEGER,
                session_id VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON
            )
            """
            
            # Analytics metrics table
            create_metrics_table = """
            CREATE TABLE IF NOT EXISTS analytics_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value DECIMAL(15,4) NOT NULL,
                metric_type VARCHAR(50) NOT NULL,
                tags JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Performance metrics table
            create_performance_table = """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id SERIAL PRIMARY KEY,
                query_count INTEGER DEFAULT 0,
                avg_query_time DECIMAL(10,4) DEFAULT 0,
                slow_queries INTEGER DEFAULT 0,
                connection_count INTEGER DEFAULT 0,
                cache_hit_ratio DECIMAL(5,4) DEFAULT 0,
                error_rate DECIMAL(5,4) DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Revenue analytics table
            create_revenue_table = """
            CREATE TABLE IF NOT EXISTS revenue_analytics (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                content_id INTEGER,
                amount DECIMAL(10,2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                revenue_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON
            )
            """
            
            self.connection.execute(text(create_events_table))
            self.connection.execute(text(create_metrics_table))
            self.connection.execute(text(create_performance_table))
            self.connection.execute(text(create_revenue_table))
            self.connection.commit()
            
            logger.info("Analytics tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create analytics tables: {e}")
    
    def track_event(self, event_type: AnalyticsEvent, event_data: Dict[str, Any], 
                   user_id: int = None, session_id: str = None, metadata: Dict[str, Any] = None):
        """Track an analytics event"""
        try:
            timestamp = datetime.datetime.utcnow()
            
            # Store in memory
            with self._lock:
                event_record = {
                    'event_type': event_type.value,
                    'event_data': event_data,
                    'user_id': user_id,
                    'session_id': session_id,
                    'timestamp': timestamp,
                    'metadata': metadata or {}
                }
                
                if 'events' not in self.metrics:
                    self.metrics['events'] = []
                self.metrics['events'].append(event_record)
            
            # Store in database (async)
            if SQLALCHEMY_AVAILABLE and self.connection:
                self._executor.submit(self._store_event_db, event_type, event_data, user_id, session_id, metadata, timestamp)
            
            # Store in Redis cache
            if self.redis_client:
                self._executor.submit(self._store_event_redis, event_type, event_data, user_id, session_id, metadata, timestamp)
            
            # Trigger event handlers
            for handler in self.event_handlers.get(event_type, []):
                try:
                    handler(event_type, event_data, user_id, session_id, metadata)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
            
            logger.debug(f"Tracked event: {event_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to track event {event_type}: {e}")
    
    def _store_event_db(self, event_type: AnalyticsEvent, event_data: Dict[str, Any], 
                       user_id: int, session_id: str, metadata: Dict[str, Any], timestamp: datetime.datetime):
        """Store event in database"""
        try:
            sql = """
            INSERT INTO analytics_events (event_type, event_data, user_id, session_id, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            self.connection.execute(text(sql), (
                event_type.value,
                json.dumps(event_data),
                user_id,
                session_id,
                timestamp,
                json.dumps(metadata or {})
            ))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to store event in database: {e}")
    
    def _store_event_redis(self, event_type: AnalyticsEvent, event_data: Dict[str, Any], 
                          user_id: int, session_id: str, metadata: Dict[str, Any], timestamp: datetime.datetime):
        """Store event in Redis"""
        try:
            event_key = f"analytics:events:{event_type.value}:{timestamp.strftime('%Y%m%d%H')}"
            event_record = {
                'event_data': json.dumps(event_data),
                'user_id': user_id,
                'session_id': session_id,
                'timestamp': timestamp.isoformat(),
                'metadata': json.dumps(metadata or {})
            }
            
            self.redis_client.lpush(event_key, json.dumps(event_record))
            self.redis_client.expire(event_key, 86400)  # Expire after 24 hours
            
        except Exception as e:
            logger.error(f"Failed to store event in Redis: {e}")
    
    def record_metric(self, name: str, value: Union[int, float], 
                     metric_type: MetricType = MetricType.GAUGE, 
                     tags: Dict[str, str] = None):
        """Record a metric"""
        try:
            timestamp = datetime.datetime.utcnow()
            metric = Metric(
                name=name,
                value=value,
                metric_type=metric_type,
                tags=tags or {},
                timestamp=timestamp
            )
            
            # Store in memory
            with self._lock:
                self.metrics[name].append(metric)
                # Keep only last 1000 metrics per name
                if len(self.metrics[name]) > 1000:
                    self.metrics[name] = self.metrics[name][-1000:]
            
            # Store in database (async)
            if SQLALCHEMY_AVAILABLE and self.connection:
                self._executor.submit(self._store_metric_db, metric)
            
            # Store in Redis
            if self.redis_client:
                self._executor.submit(self._store_metric_redis, metric)
            
            logger.debug(f"Recorded metric: {name} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to record metric {name}: {e}")
    
    def _store_metric_db(self, metric: Metric):
        """Store metric in database"""
        try:
            sql = """
            INSERT INTO analytics_metrics (metric_name, metric_value, metric_type, tags, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """
            self.connection.execute(text(sql), (
                metric.name,
                metric.value,
                metric.metric_type.value,
                json.dumps(metric.tags),
                metric.timestamp
            ))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to store metric in database: {e}")
    
    def _store_metric_redis(self, metric: Metric):
        """Store metric in Redis"""
        try:
            metric_key = f"analytics:metrics:{metric.name}:{metric.timestamp.strftime('%Y%m%d%H%M')}"
            self.redis_client.setex(metric_key, 3600, json.dumps(metric.to_dict()))
        except Exception as e:
            logger.error(f"Failed to store metric in Redis: {e}")
    
    def get_creator_analytics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics for a creator"""
        try:
            cache_key = f"creator_analytics_{user_id}_{days}"
            
            # Check cache first
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            start_time = time.time()
            end_date = datetime.datetime.utcnow()
            start_date = end_date - datetime.timedelta(days=days)
            
            analytics = {
                'user_id': user_id,
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_views': 0,
                'total_shares': 0,
                'total_revenue': 0.0,
                'content_count': 0,
                'avg_engagement_rate': 0.0,
                'top_content': [],
                'revenue_breakdown': {},
                'daily_stats': {},
                'performance_trends': {}
            }
            
            if SQLALCHEMY_AVAILABLE and self.connection:
                # Get content statistics
                content_stats = self._get_creator_content_stats(user_id, start_date, end_date)
                analytics.update(content_stats)
                
                # Get revenue analytics
                revenue_stats = self._get_creator_revenue_stats(user_id, start_date, end_date)
                analytics.update(revenue_stats)
                
                # Get engagement analytics
                engagement_stats = self._get_creator_engagement_stats(user_id, start_date, end_date)
                analytics.update(engagement_stats)
            else:
                # Fallback to in-memory data
                analytics = self._get_creator_analytics_memory(user_id, start_date, end_date)
            
            execution_time = (time.time() - start_time) * 1000
            analytics['execution_time_ms'] = execution_time
            
            # Cache result
            self._cache_result(cache_key, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get creator analytics for user {user_id}: {e}")
            return {'error': str(e)}
    
    def _get_creator_content_stats(self, user_id: int, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict[str, Any]:
        """Get creator content statistics from database"""
        try:
            # Content count and views
            content_query = """
            SELECT 
                COUNT(*) as content_count,
                COALESCE(SUM(CAST(event_data->>'views' AS INTEGER)), 0) as total_views
            FROM analytics_events ae
            WHERE ae.user_id = ? 
            AND ae.event_type = 'content_uploaded'
            AND ae.timestamp BETWEEN ? AND ?
            """
            
            result = self.connection.execute(text(content_query), (user_id, start_date, end_date)).fetchone()
            
            return {
                'content_count': result.content_count if result else 0,
                'total_views': result.total_views if result else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get content stats: {e}")
            return {'content_count': 0, 'total_views': 0}
    
    def _get_creator_revenue_stats(self, user_id: int, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict[str, Any]:
        """Get creator revenue statistics from database"""
        try:
            # Total revenue
            revenue_query = """
            SELECT 
                COALESCE(SUM(amount), 0) as total_revenue,
                COUNT(*) as transaction_count,
                revenue_type,
                currency
            FROM revenue_analytics
            WHERE user_id = ? 
            AND timestamp BETWEEN ? AND ?
            GROUP BY revenue_type, currency
            """
            
            results = self.connection.execute(text(revenue_query), (user_id, start_date, end_date)).fetchall()
            
            total_revenue = 0.0
            revenue_breakdown = {}
            transaction_count = 0
            
            for result in results:
                total_revenue += float(result.total_revenue)
                transaction_count += result.transaction_count
                revenue_breakdown[result.revenue_type] = {
                    'amount': float(result.total_revenue),
                    'currency': result.currency,
                    'transaction_count': result.transaction_count
                }
            
            return {
                'total_revenue': total_revenue,
                'transaction_count': transaction_count,
                'revenue_breakdown': revenue_breakdown
            }
            
        except Exception as e:
            logger.error(f"Failed to get revenue stats: {e}")
            return {'total_revenue': 0.0, 'transaction_count': 0, 'revenue_breakdown': {}}
    
    def _get_creator_engagement_stats(self, user_id: int, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict[str, Any]:
        """Get creator engagement statistics from database"""
        try:
            # Engagement metrics
            engagement_query = """
            SELECT 
                event_type,
                COUNT(*) as event_count,
                CAST(event_data->>'engagement_score' AS DECIMAL) as avg_engagement
            FROM analytics_events
            WHERE user_id = ? 
            AND event_type IN ('content_viewed', 'content_shared')
            AND timestamp BETWEEN ? AND ?
            GROUP BY event_type
            """
            
            results = self.connection.execute(text(engagement_query), (user_id, start_date, end_date)).fetchall()
            
            total_shares = 0
            avg_engagement = 0.0
            
            for result in results:
                if result.event_type == 'content_shared':
                    total_shares = result.event_count
                if result.avg_engagement:
                    avg_engagement = float(result.avg_engagement)
            
            return {
                'total_shares': total_shares,
                'avg_engagement_rate': avg_engagement
            }
            
        except Exception as e:
            logger.error(f"Failed to get engagement stats: {e}")
            return {'total_shares': 0, 'avg_engagement_rate': 0.0}
    
    def _get_creator_analytics_memory(self, user_id: int, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict[str, Any]:
        """Get creator analytics from in-memory data"""
        analytics = {
            'user_id': user_id,
            'total_views': 0,
            'total_shares': 0,
            'total_revenue': 0.0,
            'content_count': 0,
            'avg_engagement_rate': 0.0
        }
        
        # Process events from memory
        events = self.metrics.get('events', [])
        for event in events:
            if (event.get('user_id') == user_id and 
                start_date <= event.get('timestamp', datetime.datetime.min) <= end_date):
                
                event_type = event.get('event_type')
                event_data = event.get('event_data', {})
                
                if event_type == 'content_uploaded':
                    analytics['content_count'] += 1
                elif event_type == 'content_viewed':
                    analytics['total_views'] += event_data.get('views', 1)
                elif event_type == 'content_shared':
                    analytics['total_shares'] += 1
                elif event_type == 'revenue_generated':
                    analytics['total_revenue'] += event_data.get('amount', 0.0)
        
        return analytics
    
    def get_platform_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get platform-wide metrics"""
        try:
            cache_key = f"platform_metrics_{days}"
            
            # Check cache first
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            start_time = time.time()
            end_date = datetime.datetime.utcnow()
            start_date = end_date - datetime.timedelta(days=days)
            
            metrics = {
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'active_creators': 0,
                'total_users': 0,
                'total_content': 0,
                'total_views': 0,
                'total_revenue': 0.0,
                'avg_query_time': 0.0,
                'system_health': 'unknown'
            }
            
            if SQLALCHEMY_AVAILABLE and self.connection:
                metrics.update(self._get_platform_metrics_db(start_date, end_date))
            else:
                metrics.update(self._get_platform_metrics_memory(start_date, end_date))
            
            execution_time = (time.time() - start_time) * 1000
            metrics['execution_time_ms'] = execution_time
            
            # Cache result
            self._cache_result(cache_key, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get platform metrics: {e}")
            return {'error': str(e)}
    
    def _get_platform_metrics_db(self, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict[str, Any]:
        """Get platform metrics from database"""
        try:
            # Active creators
            creators_query = """
            SELECT COUNT(DISTINCT user_id) as active_creators
            FROM analytics_events
            WHERE event_type = 'content_uploaded'
            AND timestamp BETWEEN ? AND ?
            """
            
            creators_result = self.connection.execute(text(creators_query), (start_date, end_date)).fetchone()
            active_creators = creators_result.active_creators if creators_result else 0
            
            # Total content and views
            content_query = """
            SELECT 
                COUNT(*) as total_content,
                COALESCE(SUM(CAST(event_data->>'views' AS INTEGER)), 0) as total_views
            FROM analytics_events
            WHERE event_type IN ('content_uploaded', 'content_viewed')
            AND timestamp BETWEEN ? AND ?
            """
            
            content_result = self.connection.execute(text(content_query), (start_date, end_date)).fetchone()
            total_content = content_result.total_content if content_result else 0
            total_views = content_result.total_views if content_result else 0
            
            # Total revenue
            revenue_query = """
            SELECT COALESCE(SUM(amount), 0) as total_revenue
            FROM revenue_analytics
            WHERE timestamp BETWEEN ? AND ?
            """
            
            revenue_result = self.connection.execute(text(revenue_query), (start_date, end_date)).fetchone()
            total_revenue = float(revenue_result.total_revenue) if revenue_result else 0.0
            
            return {
                'active_creators': active_creators,
                'total_content': total_content,
                'total_views': total_views,
                'total_revenue': total_revenue
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform metrics from DB: {e}")
            return {}
    
    def _get_platform_metrics_memory(self, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict[str, Any]:
        """Get platform metrics from in-memory data"""
        active_creators = set()
        total_content = 0
        total_views = 0
        total_revenue = 0.0
        
        events = self.metrics.get('events', [])
        for event in events:
            if start_date <= event.get('timestamp', datetime.datetime.min) <= end_date:
                event_type = event.get('event_type')
                event_data = event.get('event_data', {})
                user_id = event.get('user_id')
                
                if event_type == 'content_uploaded' and user_id:
                    active_creators.add(user_id)
                    total_content += 1
                elif event_type == 'content_viewed':
                    total_views += event_data.get('views', 1)
                elif event_type == 'revenue_generated':
                    total_revenue += event_data.get('amount', 0.0)
        
        return {
            'active_creators': len(active_creators),
            'total_content': total_content,
            'total_views': total_views,
            'total_revenue': total_revenue
        }
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current database performance metrics"""
        try:
            timestamp = datetime.datetime.utcnow()
            
            # Get metrics from memory first
            query_times = [m.value for m in self.metrics.get('query_time', []) 
                          if (timestamp - m.timestamp).seconds < 300]  # Last 5 minutes
            
            avg_query_time = sum(query_times) / len(query_times) if query_times else 0.0
            slow_queries = len([t for t in query_times if t > 1000])  # > 1 second
            
            # Get cache metrics
            cache_hits = len([m for m in self.metrics.get('cache_hit', []) 
                             if (timestamp - m.timestamp).seconds < 300])
            cache_misses = len([m for m in self.metrics.get('cache_miss', []) 
                               if (timestamp - m.timestamp).seconds < 300])
            
            cache_hit_ratio = cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0.0
            
            # Get error rate
            errors = len([m for m in self.metrics.get('error', []) 
                         if (timestamp - m.timestamp).seconds < 300])
            total_operations = len(query_times) + errors
            error_rate = errors / total_operations if total_operations > 0 else 0.0
            
            performance = PerformanceMetrics(
                query_count=len(query_times),
                avg_query_time=avg_query_time,
                slow_queries=slow_queries,
                connection_count=self._get_connection_count(),
                cache_hit_ratio=cache_hit_ratio,
                error_rate=error_rate,
                timestamp=timestamp
            )
            
            # Store performance metrics
            self.performance_history.append(performance)
            
            # Store in database
            if SQLALCHEMY_AVAILABLE and self.connection:
                self._executor.submit(self._store_performance_metrics, performance)
            
            return performance
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return PerformanceMetrics(0, 0.0, 0, 0, 0.0, 1.0, datetime.datetime.utcnow())
    
    def _get_connection_count(self) -> int:
        """Get current database connection count"""
        try:
            if SQLALCHEMY_AVAILABLE and self.connection:
                # This is database-specific, here's a PostgreSQL example
                result = self.connection.execute(text("SELECT count(*) FROM pg_stat_activity")).fetchone()
                return result[0] if result else 0
            return 1  # Fallback
        except Exception:
            return 1
    
    def _store_performance_metrics(self, metrics: PerformanceMetrics):
        """Store performance metrics in database"""
        try:
            sql = """
            INSERT INTO performance_metrics 
            (query_count, avg_query_time, slow_queries, connection_count, cache_hit_ratio, error_rate, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.connection.execute(text(sql), (
                metrics.query_count,
                metrics.avg_query_time,
                metrics.slow_queries,
                metrics.connection_count,
                metrics.cache_hit_ratio,
                metrics.error_rate,
                metrics.timestamp
            ))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to store performance metrics: {e}")
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached analytics result"""
        try:
            # Check in-memory cache first
            if cache_key in self.query_cache:
                cached_data, timestamp = self.query_cache[cache_key]
                if (datetime.datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                    return cached_data
                else:
                    del self.query_cache[cache_key]
            
            # Check Redis cache
            if self.redis_client:
                cached_result = self.redis_client.get(f"analytics:cache:{cache_key}")
                if cached_result:
                    return json.loads(cached_result)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached result: {e}")
            return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache analytics result"""
        try:
            # Cache in memory
            self.query_cache[cache_key] = (result, datetime.datetime.utcnow())
            
            # Cache in Redis
            if self.redis_client:
                self.redis_client.setex(
                    f"analytics:cache:{cache_key}", 
                    self.cache_ttl, 
                    json.dumps(result)
                )
            
        except Exception as e:
            logger.error(f"Failed to cache result: {e}")
    
    def add_event_handler(self, event_type: AnalyticsEvent, handler: Callable):
        """Add an event handler"""
        self.event_handlers[event_type].append(handler)
        logger.info(f"Added event handler for {event_type.value}")
    
    def remove_event_handler(self, event_type: AnalyticsEvent, handler: Callable):
        """Remove an event handler"""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.info(f"Removed event handler for {event_type.value}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        return {
            'total_metrics': sum(len(metrics) for metrics in self.metrics.values()),
            'total_events': len(self.metrics.get('events', [])),
            'performance_history_size': len(self.performance_history),
            'cache_size': len(self.query_cache),
            'event_handlers': {event.value: len(handlers) for event, handlers in self.event_handlers.items()},
            'redis_available': self.redis_client is not None,
            'sqlalchemy_available': SQLALCHEMY_AVAILABLE,
            'last_performance_check': self.performance_history[-1].timestamp.isoformat() if self.performance_history else None
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform analytics engine health check"""
        try:
            health = {
                'status': 'healthy',
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'components': {}
            }
            
            # Check database connection
            if SQLALCHEMY_AVAILABLE and self.connection:
                try:
                    self.connection.execute(text("SELECT 1")).fetchone()
                    health['components']['database'] = 'healthy'
                except Exception as e:
                    health['components']['database'] = f'unhealthy: {e}'
                    health['status'] = 'degraded'
            else:
                health['components']['database'] = 'not_configured'
            
            # Check Redis connection
            if self.redis_client:
                try:
                    self.redis_client.ping()
                    health['components']['redis'] = 'healthy'
                except Exception as e:
                    health['components']['redis'] = f'unhealthy: {e}'
                    health['status'] = 'degraded'
            else:
                health['components']['redis'] = 'not_configured'
            
            # Check performance
            current_performance = self.get_performance_metrics()
            if current_performance.error_rate > 0.1:  # > 10% error rate
                health['components']['performance'] = 'degraded'
                health['status'] = 'degraded'
            else:
                health['components']['performance'] = 'healthy'
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.datetime.utcnow().isoformat()
            }
    
    def cleanup(self):
        """Cleanup analytics engine resources"""
        try:
            self._executor.shutdown(wait=True)
            if self.redis_client:
                self.redis_client.close()
            logger.info("Analytics engine cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global analytics engine instance
_analytics_engine = None

def get_analytics_engine(connection=None, redis_client=None) -> AnalyticsEngine:
    """Get the global analytics engine"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine(connection, redis_client)
    return _analytics_engine

def track_analytics_event(event_type: AnalyticsEvent, event_data: Dict[str, Any], 
                         user_id: int = None, session_id: str = None, metadata: Dict[str, Any] = None):
    """Track an analytics event"""
    engine = get_analytics_engine()
    engine.track_event(event_type, event_data, user_id, session_id, metadata)

def record_analytics_metric(name: str, value: Union[int, float], 
                           metric_type: MetricType = MetricType.GAUGE, 
                           tags: Dict[str, str] = None):
    """Record an analytics metric"""
    engine = get_analytics_engine()
    engine.record_metric(name, value, metric_type, tags)

def get_creator_analytics_summary(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Get creator analytics summary"""
    engine = get_analytics_engine()
    return engine.get_creator_analytics(user_id, days)

def get_platform_analytics_summary(days: int = 7) -> Dict[str, Any]:
    """Get platform analytics summary"""
    engine = get_analytics_engine()
    return engine.get_platform_metrics(days)

def get_performance_summary() -> PerformanceMetrics:
    """Get database performance summary"""
    engine = get_analytics_engine()
    return engine.get_performance_metrics()

# Convenience functions for common analytics operations
def process_content_ai(content_id: int) -> Dict[str, Any]:
    """Process content with AI and return metadata (mock implementation)"""
    # This would integrate with actual AI processing in production
    ai_metadata = {
        'content_id': content_id,
        'processed_at': datetime.datetime.utcnow().isoformat(),
        'ai_tags': ['entertainment', 'video', 'high_quality'],
        'sentiment_score': 0.8,
        'engagement_prediction': 0.75,
        'monetization_score': 0.6
    }
    
    # Track the AI processing event
    track_analytics_event(
        AnalyticsEvent.QUERY_EXECUTED,
        {'operation': 'ai_processing', 'content_id': content_id, 'result': 'success'},
        metadata={'ai_metadata': ai_metadata}
    )
    
    return ai_metadata

def track_query_performance(query_name: str, execution_time_ms: float, success: bool = True):
    """Track database query performance"""
    record_analytics_metric('query_time', execution_time_ms, MetricType.TIMER, {'query': query_name})
    
    if success:
        record_analytics_metric('query_success', 1, MetricType.COUNTER, {'query': query_name})
    else:
        record_analytics_metric('query_error', 1, MetricType.COUNTER, {'query': query_name})

def benchmark_analytics_performance() -> Dict[str, Any]:
    """Benchmark analytics engine performance"""
    start_time = time.time()
    
    # Test metric recording
    for i in range(100):
        record_analytics_metric(f'test_metric_{i}', i, MetricType.GAUGE)
    
    metric_time = time.time() - start_time
    
    # Test event tracking
    start_time = time.time()
    for i in range(100):
        track_analytics_event(
            AnalyticsEvent.CONTENT_VIEWED,
            {'content_id': i, 'views': 1},
            user_id=i % 10
        )
    
    event_time = time.time() - start_time
    
    return {
        'metrics_per_second': 100 / metric_time,
        'events_per_second': 100 / event_time,
        'total_benchmark_time': metric_time + event_time
    }