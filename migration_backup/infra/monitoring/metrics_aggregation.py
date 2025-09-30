# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade metrics aggregation system for Ainflue platform
# Supports multi-cloud metrics collection, aggregation, and analytics
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import asyncio
import logging
import json
import redis
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import boto3
import psycopg2
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
import aiohttp
import yaml
from pathlib import Path

class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AggregationType(Enum):
    """Aggregation type enumeration"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"
    COUNT = "count"

@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str]
    service: str
    namespace: str

@dataclass
class AggregatedMetric:
    """Aggregated metric result"""
    name: str
    aggregation_type: AggregationType
    value: float
    start_time: datetime
    end_time: datetime
    labels: Dict[str, str]
    sample_count: int

class MetricsAggregationEngine:
    """Enterprise metrics aggregation engine for Ainflue platform"""
    
    def __init__(self, config_path: str = "config/metrics_config.yaml"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.redis_client = self._setup_redis()
        self.prometheus_registry = CollectorRegistry()
        self.db_connection = self._setup_database()
        
        # Metrics for platform monitoring
        self.creator_metrics = {}
        self.content_metrics = {}
        self.ai_processing_metrics = {}
        self.monetization_metrics = {}
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load metrics aggregation configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for metrics aggregation"""
        return {
            "aggregation": {
                "window_size": "5m",
                "retention_period": "7d",
                "batch_size": 1000,
                "flush_interval": 30
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 2,
                "password": None
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "ainflue_metrics",
                "username": "metrics_user",
                "password": "secure_password"
            },
            "prometheus": {
                "pushgateway_url": "http://prometheus-pushgateway:9091",
                "job_name": "ainflue-metrics-aggregation"
            },
            "creator_economy": {
                "track_uploads": True,
                "track_ai_processing": True,
                "track_monetization": True,
                "track_collaboration": True
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for metrics aggregation"""
        logger = logging.getLogger("metrics_aggregation")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_redis(self) -> redis.Redis:
        """Setup Redis connection for metrics caching"""
        redis_config = self.config.get("redis", {})
        return redis.Redis(
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
            db=redis_config.get("db", 2),
            password=redis_config.get("password"),
            decode_responses=True
        )
    
    def _setup_database(self) -> psycopg2.connection:
        """Setup PostgreSQL connection for metrics storage"""
        db_config = self.config.get("database", {})
        return psycopg2.connect(
            host=db_config.get("host", "localhost"),
            port=db_config.get("port", 5432),
            database=db_config.get("database", "ainflue_metrics"),
            user=db_config.get("username", "metrics_user"),
            password=db_config.get("password", "secure_password")
        )
    
    async def aggregate_creator_metrics(self, creator_id: str, time_window: str) -> Dict[str, Any]:
        """Aggregate metrics for a specific creator"""
        try:
            metrics = {}
            
            # Content upload metrics
            metrics["content_uploads"] = await self._aggregate_content_uploads(creator_id, time_window)
            
            # AI processing metrics
            metrics["ai_processing"] = await self._aggregate_ai_processing(creator_id, time_window)
            
            # Monetization metrics
            metrics["monetization"] = await self._aggregate_monetization(creator_id, time_window)
            
            # Collaboration metrics
            metrics["collaborations"] = await self._aggregate_collaborations(creator_id, time_window)
            
            # SEO performance metrics
            metrics["seo_performance"] = await self._aggregate_seo_metrics(creator_id, time_window)
            
            self.logger.info(f"Aggregated metrics for creator {creator_id} over {time_window}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error aggregating creator metrics: {str(e)}")
            raise
    
    async def _aggregate_content_uploads(self, creator_id: str, time_window: str) -> Dict[str, Any]:
        """Aggregate content upload metrics"""
        query = """
        SELECT 
            COUNT(*) as total_uploads,
            AVG(file_size) as avg_file_size,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_uploads,
            AVG(processing_time) as avg_processing_time
        FROM content_uploads 
        WHERE creator_id = %s 
        AND created_at >= NOW() - INTERVAL %s
        """
        
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, (creator_id, time_window))
            result = cursor.fetchone()
            
            return {
                "total_uploads": result[0] or 0,
                "avg_file_size_mb": round((result[1] or 0) / 1024 / 1024, 2),
                "successful_uploads": result[2] or 0,
                "success_rate": round((result[2] or 0) / max(result[0] or 1, 1) * 100, 2),
                "avg_processing_time_seconds": round(result[3] or 0, 2)
            }
    
    async def _aggregate_ai_processing(self, creator_id: str, time_window: str) -> Dict[str, Any]:
        """Aggregate AI processing metrics"""
        query = """
        SELECT 
            COUNT(*) as total_ai_jobs,
            AVG(processing_time) as avg_processing_time,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_jobs,
            AVG(quality_score) as avg_quality_score,
            SUM(gpu_hours) as total_gpu_hours
        FROM ai_processing_jobs 
        WHERE creator_id = %s 
        AND created_at >= NOW() - INTERVAL %s
        """
        
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, (creator_id, time_window))
            result = cursor.fetchone()
            
            return {
                "total_ai_jobs": result[0] or 0,
                "avg_processing_time_minutes": round((result[1] or 0) / 60, 2),
                "completed_jobs": result[2] or 0,
                "completion_rate": round((result[2] or 0) / max(result[0] or 1, 1) * 100, 2),
                "avg_quality_score": round(result[3] or 0, 2),
                "total_gpu_hours": round(result[4] or 0, 2)
            }
    
    async def _aggregate_monetization(self, creator_id: str, time_window: str) -> Dict[str, Any]:
        """Aggregate monetization metrics"""
        query = """
        SELECT 
            SUM(revenue) as total_revenue,
            COUNT(DISTINCT transaction_id) as transaction_count,
            AVG(revenue) as avg_transaction_value,
            SUM(CASE WHEN revenue_type = 'subscription' THEN revenue ELSE 0 END) as subscription_revenue,
            SUM(CASE WHEN revenue_type = 'commission' THEN revenue ELSE 0 END) as commission_revenue
        FROM monetization_transactions 
        WHERE creator_id = %s 
        AND created_at >= NOW() - INTERVAL %s
        """
        
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, (creator_id, time_window))
            result = cursor.fetchone()
            
            return {
                "total_revenue_eur": round(result[0] or 0, 2),
                "transaction_count": result[1] or 0,
                "avg_transaction_value_eur": round(result[2] or 0, 2),
                "subscription_revenue_eur": round(result[3] or 0, 2),
                "commission_revenue_eur": round(result[4] or 0, 2)
            }
    
    async def _aggregate_collaborations(self, creator_id: str, time_window: str) -> Dict[str, Any]:
        """Aggregate collaboration metrics"""
        query = """
        SELECT 
            COUNT(*) as total_collaborations,
            COUNT(DISTINCT collaborator_id) as unique_collaborators,
            AVG(collaboration_rating) as avg_rating,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_collaborations
        FROM collaborations 
        WHERE (creator_id = %s OR collaborator_id = %s)
        AND created_at >= NOW() - INTERVAL %s
        """
        
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, (creator_id, creator_id, time_window))
            result = cursor.fetchone()
            
            return {
                "total_collaborations": result[0] or 0,
                "unique_collaborators": result[1] or 0,
                "avg_rating": round(result[2] or 0, 2),
                "completed_collaborations": result[3] or 0,
                "completion_rate": round((result[3] or 0) / max(result[0] or 1, 1) * 100, 2)
            }
    
    async def _aggregate_seo_metrics(self, creator_id: str, time_window: str) -> Dict[str, Any]:
        """Aggregate SEO performance metrics"""
        query = """
        SELECT 
            AVG(search_ranking) as avg_search_ranking,
            SUM(organic_clicks) as total_organic_clicks,
            SUM(impressions) as total_impressions,
            AVG(click_through_rate) as avg_ctr
        FROM seo_metrics 
        WHERE creator_id = %s 
        AND date >= NOW() - INTERVAL %s
        """
        
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, (creator_id, time_window))
            result = cursor.fetchone()
            
            return {
                "avg_search_ranking": round(result[0] or 0, 2),
                "total_organic_clicks": result[1] or 0,
                "total_impressions": result[2] or 0,
                "avg_click_through_rate": round(result[3] or 0, 4)
            }
    
    async def aggregate_platform_metrics(self, time_window: str) -> Dict[str, Any]:
        """Aggregate platform-wide metrics"""
        try:
            metrics = {}
            
            # Overall platform health
            metrics["platform_health"] = await self._aggregate_platform_health(time_window)
            
            # Content processing metrics
            metrics["content_processing"] = await self._aggregate_content_processing(time_window)
            
            # User engagement metrics
            metrics["user_engagement"] = await self._aggregate_user_engagement(time_window)
            
            # System performance metrics
            metrics["system_performance"] = await self._aggregate_system_performance(time_window)
            
            self.logger.info(f"Aggregated platform metrics over {time_window}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error aggregating platform metrics: {str(e)}")
            raise
    
    async def _aggregate_platform_health(self, time_window: str) -> Dict[str, Any]:
        """Aggregate platform health metrics"""
        return {
            "active_creators": await self._count_active_creators(time_window),
            "total_content_uploads": await self._count_content_uploads(time_window),
            "ai_processing_queue_size": await self._get_queue_size("ai_processing"),
            "system_uptime_percentage": await self._calculate_uptime(time_window),
            "error_rate_percentage": await self._calculate_error_rate(time_window)
        }
    
    async def real_time_metrics_stream(self) -> AsyncIterable[Dict[str, Any]]:
        """Stream real-time aggregated metrics"""
        while True:
            try:
                # Collect current metrics
                current_metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_sessions": await self._get_active_sessions(),
                    "upload_rate_per_minute": await self._get_upload_rate(),
                    "ai_processing_rate": await self._get_ai_processing_rate(),
                    "revenue_rate_per_hour": await self._get_revenue_rate(),
                    "system_resources": await self._get_system_resources()
                }
                
                yield current_metrics
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in real-time metrics stream: {str(e)}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def export_metrics_to_prometheus(self, metrics: Dict[str, Any]) -> bool:
        """Export aggregated metrics to Prometheus"""
        try:
            # Create Prometheus metrics
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    gauge = Gauge(f"ainflue_{metric_name}", f"Ainflue {metric_name}", 
                                 registry=self.prometheus_registry)
                    gauge.set(metric_value)
            
            # Push to Prometheus pushgateway
            prometheus_config = self.config.get("prometheus", {})
            pushgateway_url = prometheus_config.get("pushgateway_url")
            
            if pushgateway_url:
                from prometheus_client import push_to_gateway
                push_to_gateway(
                    pushgateway_url,
                    job=prometheus_config.get("job_name", "ainflue-metrics"),
                    registry=self.prometheus_registry
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics to Prometheus: {str(e)}")
            return False
    
    async def generate_analytics_report(self, creator_id: Optional[str] = None, 
                                      time_window: str = "24h") -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            if creator_id:
                metrics = await self.aggregate_creator_metrics(creator_id, time_window)
                report_type = "creator"
            else:
                metrics = await self.aggregate_platform_metrics(time_window)
                report_type = "platform"
            
            # Generate insights and recommendations
            insights = await self._generate_insights(metrics, report_type)
            
            report = {
                "report_id": f"{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "report_type": report_type,
                "creator_id": creator_id,
                "time_window": time_window,
                "generated_at": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "insights": insights,
                "recommendations": await self._generate_recommendations(metrics, report_type)
            }
            
            # Store report
            await self._store_analytics_report(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating analytics report: {str(e)}")
            raise
    
    def __del__(self):
        """Cleanup connections"""
        try:
            if hasattr(self, 'db_connection'):
                self.db_connection.close()
            if hasattr(self, 'redis_client'):
                self.redis_client.close()
        except:
            pass

# Usage example and testing
if __name__ == "__main__":
    async def main():
        # Initialize metrics aggregation engine
        engine = MetricsAggregationEngine()
        
        # Test creator metrics aggregation
        creator_metrics = await engine.aggregate_creator_metrics("creator_123", "24h")
        print("Creator Metrics:", json.dumps(creator_metrics, indent=2))
        
        # Test platform metrics aggregation
        platform_metrics = await engine.aggregate_platform_metrics("24h")
        print("Platform Metrics:", json.dumps(platform_metrics, indent=2))
        
        # Generate analytics report
        report = await engine.generate_analytics_report("creator_123", "7d")
        print("Analytics Report Generated:", report["report_id"])
    
    # Run the example
    asyncio.run(main())