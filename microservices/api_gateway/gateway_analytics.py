"""
🔗 GATEWAY ANALYTICS SERVICE - ENTERPRISE MICROSERVICE
Analytics gateway for comprehensive API performance tracking and business intelligence.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import json
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import aioredis
import asyncpg

logger = logging.getLogger(__name__)

@dataclass
class APIMetrics:
    """API metrics data structure"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    user_id: Optional[str]
    api_key: Optional[str]
    timestamp: datetime
    
@dataclass
class AnalyticsConfig:
    """Analytics configuration"""
    retention_days: int = 90
    aggregation_intervals: List[str] = None
    metrics_export_interval: int = 60
    real_time_buffer_size: int = 10000
    redis_url: str = "redis://localhost:6379"
    postgres_url: str = "postgresql://localhost/ainflue"
    prometheus_port: int = 8000
    
    def __post_init__(self):
        if self.aggregation_intervals is None:
            self.aggregation_intervals = ["1m", "5m", "15m", "1h", "24h"]

class GatewayAnalytics:
    """
    🔗 Gateway Analytics Service
    
    Comprehensive API analytics and business intelligence for gateway traffic.
    Provides real-time metrics, historical analysis, and performance insights.
    """
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.redis = None
        self.postgres = None
        self.metrics_buffer = deque(maxlen=config.real_time_buffer_size)
        
        # Prometheus metrics
        self.request_counter = Counter('api_requests_total', 'Total API requests', 
                                     ['endpoint', 'method', 'status_code'])
        self.request_duration = Histogram('api_request_duration_seconds', 
                                        'API request duration', ['endpoint', 'method'])
        self.active_connections = Gauge('api_active_connections', 'Active API connections')
        self.error_rate = Gauge('api_error_rate', 'API error rate', ['endpoint'])
        
        # Analytics aggregates
        self.hourly_stats = defaultdict(lambda: defaultdict(list))
        self.daily_stats = defaultdict(lambda: defaultdict(list))
        self.endpoint_performance = defaultdict(list)
        
        # Real-time tracking
        self.active_requests = {}
        self.user_sessions = defaultdict(dict)
        
        self.running = False
        
    async def initialize(self):
        """Initialize analytics service"""
        try:
            # Initialize Redis connection
            self.redis = await aioredis.from_url(self.config.redis_url)
            
            # Initialize PostgreSQL connection
            self.postgres = await asyncpg.connect(self.config.postgres_url)
            
            # Create analytics tables if not exist
            await self._create_analytics_tables()
            
            # Start Prometheus metrics server
            start_http_server(self.config.prometheus_port)
            
            # Start background tasks
            asyncio.create_task(self._metrics_aggregation_task())
            asyncio.create_task(self._real_time_analytics_task())
            asyncio.create_task(self._cleanup_task())
            
            self.running = True
            logger.info("Gateway Analytics service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize gateway analytics: {e}")
            raise
            
    async def _create_analytics_tables(self):
        """Create analytics database tables"""
        create_metrics_table = """
        CREATE TABLE IF NOT EXISTS api_metrics (
            id SERIAL PRIMARY KEY,
            endpoint VARCHAR(255) NOT NULL,
            method VARCHAR(10) NOT NULL,
            status_code INTEGER NOT NULL,
            response_time FLOAT NOT NULL,
            request_size INTEGER,
            response_size INTEGER,
            user_id VARCHAR(255),
            api_key VARCHAR(255),
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        create_aggregated_metrics_table = """
        CREATE TABLE IF NOT EXISTS aggregated_metrics (
            id SERIAL PRIMARY KEY,
            endpoint VARCHAR(255) NOT NULL,
            interval_type VARCHAR(10) NOT NULL,
            interval_start TIMESTAMP WITH TIME ZONE NOT NULL,
            request_count INTEGER NOT NULL,
            avg_response_time FLOAT NOT NULL,
            error_count INTEGER NOT NULL,
            total_bytes INTEGER,
            unique_users INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(endpoint, interval_type, interval_start)
        );
        """
        
        create_indices = [
            "CREATE INDEX IF NOT EXISTS idx_api_metrics_timestamp ON api_metrics(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_api_metrics_endpoint ON api_metrics(endpoint);",
            "CREATE INDEX IF NOT EXISTS idx_api_metrics_user_id ON api_metrics(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_aggregated_metrics_endpoint_interval ON aggregated_metrics(endpoint, interval_type, interval_start);"
        ]
        
        await self.postgres.execute(create_metrics_table)
        await self.postgres.execute(create_aggregated_metrics_table)
        
        for index_sql in create_indices:
            await self.postgres.execute(index_sql)
            
    async def record_request_start(self, request_id: str, endpoint: str, method: str, 
                                 user_id: Optional[str] = None, api_key: Optional[str] = None):
        """Record the start of an API request"""
        self.active_requests[request_id] = {
            'endpoint': endpoint,
            'method': method,
            'user_id': user_id,
            'api_key': api_key,
            'start_time': time.time(),
            'timestamp': datetime.utcnow()
        }
        
        # Update active connections
        self.active_connections.set(len(self.active_requests))
        
        # Track user session
        if user_id:
            self.user_sessions[user_id]['last_request'] = datetime.utcnow()
            self.user_sessions[user_id]['total_requests'] = \
                self.user_sessions[user_id].get('total_requests', 0) + 1
                
    async def record_request_end(self, request_id: str, status_code: int, 
                               request_size: int = 0, response_size: int = 0):
        """Record the end of an API request"""
        if request_id not in self.active_requests:
            logger.warning(f"Request {request_id} not found in active requests")
            return
            
        request_data = self.active_requests.pop(request_id)
        response_time = time.time() - request_data['start_time']
        
        # Create metrics record
        metrics = APIMetrics(
            endpoint=request_data['endpoint'],
            method=request_data['method'],
            status_code=status_code,
            response_time=response_time,
            request_size=request_size,
            response_size=response_size,
            user_id=request_data['user_id'],
            api_key=request_data['api_key'],
            timestamp=request_data['timestamp']
        )
        
        # Add to buffer for real-time processing
        self.metrics_buffer.append(metrics)
        
        # Update Prometheus metrics
        self.request_counter.labels(
            endpoint=metrics.endpoint,
            method=metrics.method,
            status_code=metrics.status_code
        ).inc()
        
        self.request_duration.labels(
            endpoint=metrics.endpoint,
            method=metrics.method
        ).observe(response_time)
        
        # Update active connections
        self.active_connections.set(len(self.active_requests))
        
        # Store in database
        asyncio.create_task(self._store_metrics(metrics))
        
        # Update real-time analytics
        await self._update_real_time_analytics(metrics)
        
    async def _store_metrics(self, metrics: APIMetrics):
        """Store metrics in database"""
        try:
            insert_query = """
            INSERT INTO api_metrics (endpoint, method, status_code, response_time, 
                                   request_size, response_size, user_id, api_key, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """
            
            await self.postgres.execute(
                insert_query,
                metrics.endpoint, metrics.method, metrics.status_code,
                metrics.response_time, metrics.request_size, metrics.response_size,
                metrics.user_id, metrics.api_key, metrics.timestamp
            )
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            
    async def _update_real_time_analytics(self, metrics: APIMetrics):
        """Update real-time analytics data"""
        current_hour = metrics.timestamp.replace(minute=0, second=0, microsecond=0)
        current_day = metrics.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Update hourly stats
        hour_key = current_hour.isoformat()
        self.hourly_stats[metrics.endpoint][hour_key].append({
            'response_time': metrics.response_time,
            'status_code': metrics.status_code,
            'size': metrics.request_size + metrics.response_size
        })
        
        # Update daily stats
        day_key = current_day.isoformat()
        self.daily_stats[metrics.endpoint][day_key].append({
            'response_time': metrics.response_time,
            'status_code': metrics.status_code,
            'size': metrics.request_size + metrics.response_size
        })
        
        # Update endpoint performance tracking
        self.endpoint_performance[metrics.endpoint].append(metrics.response_time)
        
        # Keep only last 1000 response times per endpoint
        if len(self.endpoint_performance[metrics.endpoint]) > 1000:
            self.endpoint_performance[metrics.endpoint] = \
                self.endpoint_performance[metrics.endpoint][-1000:]
                
        # Calculate and update error rate
        endpoint_metrics = self.endpoint_performance[metrics.endpoint]
        if len(endpoint_metrics) >= 10:  # Minimum sample size
            recent_errors = sum(1 for _ in self.metrics_buffer 
                              if _.endpoint == metrics.endpoint and _.status_code >= 400)
            recent_total = sum(1 for _ in self.metrics_buffer 
                             if _.endpoint == metrics.endpoint)
            error_rate = recent_errors / recent_total if recent_total > 0 else 0
            self.error_rate.labels(endpoint=metrics.endpoint).set(error_rate)
            
    async def get_endpoint_analytics(self, endpoint: str, 
                                   start_time: Optional[datetime] = None,
                                   end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get analytics for a specific endpoint"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
            
        query = """
        SELECT 
            COUNT(*) as total_requests,
            AVG(response_time) as avg_response_time,
            MIN(response_time) as min_response_time,
            MAX(response_time) as max_response_time,
            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY response_time) as p50_response_time,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) as p95_response_time,
            PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time) as p99_response_time,
            COUNT(*) FILTER (WHERE status_code >= 400) as error_count,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(request_size + response_size) as total_bytes
        FROM api_metrics 
        WHERE endpoint = $1 AND timestamp BETWEEN $2 AND $3
        """
        
        result = await self.postgres.fetchrow(query, endpoint, start_time, end_time)
        
        analytics = {
            'endpoint': endpoint,
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'total_requests': result['total_requests'] or 0,
            'avg_response_time': float(result['avg_response_time'] or 0),
            'min_response_time': float(result['min_response_time'] or 0),
            'max_response_time': float(result['max_response_time'] or 0),
            'p50_response_time': float(result['p50_response_time'] or 0),
            'p95_response_time': float(result['p95_response_time'] or 0),
            'p99_response_time': float(result['p99_response_time'] or 0),
            'error_count': result['error_count'] or 0,
            'error_rate': (result['error_count'] or 0) / max(result['total_requests'] or 1, 1),
            'unique_users': result['unique_users'] or 0,
            'total_bytes': result['total_bytes'] or 0
        }
        
        return analytics
        
    async def get_top_endpoints(self, limit: int = 10, 
                              start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get top endpoints by request count"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
            
        query = """
        SELECT 
            endpoint,
            COUNT(*) as request_count,
            AVG(response_time) as avg_response_time,
            COUNT(*) FILTER (WHERE status_code >= 400) as error_count
        FROM api_metrics 
        WHERE timestamp >= $1
        GROUP BY endpoint
        ORDER BY request_count DESC
        LIMIT $2
        """
        
        results = await self.postgres.fetch(query, start_time, limit)
        
        top_endpoints = []
        for row in results:
            top_endpoints.append({
                'endpoint': row['endpoint'],
                'request_count': row['request_count'],
                'avg_response_time': float(row['avg_response_time']),
                'error_count': row['error_count'],
                'error_rate': row['error_count'] / row['request_count']
            })
            
        return top_endpoints
        
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics summary"""
        current_time = datetime.utcnow()
        last_minute = current_time - timedelta(minutes=1)
        
        # Filter recent metrics
        recent_metrics = [m for m in self.metrics_buffer 
                         if m.timestamp >= last_minute]
        
        if not recent_metrics:
            return {
                'requests_per_minute': 0,
                'avg_response_time': 0,
                'error_rate': 0,
                'active_connections': len(self.active_requests),
                'top_endpoints': []
            }
            
        # Calculate metrics
        requests_per_minute = len(recent_metrics)
        avg_response_time = statistics.mean([m.response_time for m in recent_metrics])
        error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
        error_rate = error_count / len(recent_metrics)
        
        # Top endpoints in last minute
        endpoint_counts = defaultdict(int)
        for metric in recent_metrics:
            endpoint_counts[metric.endpoint] += 1
            
        top_endpoints = sorted(endpoint_counts.items(), 
                             key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'requests_per_minute': requests_per_minute,
            'avg_response_time': avg_response_time,
            'error_rate': error_rate,
            'active_connections': len(self.active_requests),
            'top_endpoints': [{'endpoint': ep, 'count': count} 
                            for ep, count in top_endpoints]
        }
        
    async def _metrics_aggregation_task(self):
        """Background task for metrics aggregation"""
        while self.running:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(self.config.metrics_export_interval)
            except Exception as e:
                logger.error(f"Error in metrics aggregation task: {e}")
                await asyncio.sleep(10)
                
    async def _aggregate_metrics(self):
        """Aggregate metrics for different time intervals"""
        current_time = datetime.utcnow()
        
        for interval in self.config.aggregation_intervals:
            if interval == "1m":
                interval_start = current_time.replace(second=0, microsecond=0)
                interval_duration = timedelta(minutes=1)
            elif interval == "5m":
                interval_start = current_time.replace(minute=(current_time.minute // 5) * 5, 
                                                    second=0, microsecond=0)
                interval_duration = timedelta(minutes=5)
            elif interval == "15m":
                interval_start = current_time.replace(minute=(current_time.minute // 15) * 15, 
                                                    second=0, microsecond=0)
                interval_duration = timedelta(minutes=15)
            elif interval == "1h":
                interval_start = current_time.replace(minute=0, second=0, microsecond=0)
                interval_duration = timedelta(hours=1)
            elif interval == "24h":
                interval_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                interval_duration = timedelta(days=1)
            else:
                continue
                
            end_time = interval_start
            start_time = end_time - interval_duration
            
            # Aggregate metrics for this interval
            await self._create_aggregated_metrics(interval, start_time, end_time)
            
    async def _create_aggregated_metrics(self, interval_type: str, 
                                       start_time: datetime, end_time: datetime):
        """Create aggregated metrics for time interval"""
        query = """
        SELECT 
            endpoint,
            COUNT(*) as request_count,
            AVG(response_time) as avg_response_time,
            COUNT(*) FILTER (WHERE status_code >= 400) as error_count,
            SUM(request_size + response_size) as total_bytes,
            COUNT(DISTINCT user_id) as unique_users
        FROM api_metrics 
        WHERE timestamp >= $1 AND timestamp < $2
        GROUP BY endpoint
        """
        
        results = await self.postgres.fetch(query, start_time, end_time)
        
        for row in results:
            insert_query = """
            INSERT INTO aggregated_metrics 
            (endpoint, interval_type, interval_start, request_count, 
             avg_response_time, error_count, total_bytes, unique_users)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (endpoint, interval_type, interval_start) 
            DO UPDATE SET
                request_count = EXCLUDED.request_count,
                avg_response_time = EXCLUDED.avg_response_time,
                error_count = EXCLUDED.error_count,
                total_bytes = EXCLUDED.total_bytes,
                unique_users = EXCLUDED.unique_users
            """
            
            try:
                await self.postgres.execute(
                    insert_query,
                    row['endpoint'], interval_type, start_time,
                    row['request_count'], row['avg_response_time'],
                    row['error_count'], row['total_bytes'], row['unique_users']
                )
            except Exception as e:
                logger.error(f"Failed to insert aggregated metrics: {e}")
                
    async def _real_time_analytics_task(self):
        """Background task for real-time analytics updates"""
        while self.running:
            try:
                # Update real-time analytics in Redis
                metrics = await self.get_real_time_metrics()
                await self.redis.setex(
                    "gateway:analytics:realtime", 
                    30, 
                    json.dumps(metrics, default=str)
                )
                
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error in real-time analytics task: {e}")
                await asyncio.sleep(10)
                
    async def _cleanup_task(self):
        """Background task for data cleanup"""
        while self.running:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
                
                # Delete old metrics
                delete_query = "DELETE FROM api_metrics WHERE timestamp < $1"
                deleted_count = await self.postgres.execute(delete_query, cutoff_date)
                
                if deleted_count:
                    logger.info(f"Cleaned up {deleted_count} old metrics records")
                    
                # Clean up old user sessions
                current_time = datetime.utcnow()
                for user_id in list(self.user_sessions.keys()):
                    last_request = self.user_sessions[user_id].get('last_request')
                    if last_request and (current_time - last_request).days > 1:
                        del self.user_sessions[user_id]
                        
                await asyncio.sleep(3600)  # Run cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(3600)
                
    async def health_check(self) -> Dict[str, Any]:
        """Health check for analytics service"""
        try:
            # Check database connection
            await self.postgres.fetchval("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {e}"
            
        try:
            # Check Redis connection
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        return {
            'service': 'gateway_analytics',
            'status': 'healthy' if db_status == "healthy" and redis_status == "healthy" else 'unhealthy',
            'database': db_status,
            'redis': redis_status,
            'active_requests': len(self.active_requests),
            'buffer_size': len(self.metrics_buffer),
            'uptime': time.time() - (hasattr(self, 'start_time') and self.start_time or time.time())
        }
        
    async def shutdown(self):
        """Shutdown analytics service"""
        self.running = False
        
        if self.postgres:
            await self.postgres.close()
            
        if self.redis:
            await self.redis.close()
            
        logger.info("Gateway Analytics service shut down")

# Example usage
async def create_gateway_analytics():
    """Factory function to create gateway analytics service"""
    config = AnalyticsConfig(
        retention_days=90,
        aggregation_intervals=["1m", "5m", "15m", "1h", "24h"],
        metrics_export_interval=60,
        real_time_buffer_size=10000
    )
    
    analytics = GatewayAnalytics(config)
    await analytics.initialize()
    
    return analytics

if __name__ == "__main__":
    async def main():
        analytics = await create_gateway_analytics()
        
        # Example usage
        await analytics.record_request_start(
            "req_123", "/api/v1/creators", "GET", 
            user_id="user_456", api_key="key_789"
        )
        
        await asyncio.sleep(0.1)  # Simulate request processing
        
        await analytics.record_request_end("req_123", 200, 1024, 2048)
        
        # Get analytics
        endpoint_analytics = await analytics.get_endpoint_analytics("/api/v1/creators")
        print("Endpoint Analytics:", endpoint_analytics)
        
        real_time_metrics = await analytics.get_real_time_metrics()
        print("Real-time Metrics:", real_time_metrics)
        
        await analytics.shutdown()
        
    asyncio.run(main())