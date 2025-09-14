"""
Metrics Aggregation Service
==========================

Enterprise-grade metrics aggregation service for comprehensive system monitoring.
Collects, processes, and analyzes metrics from all microservices.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"

class MetricLevel(Enum):
    """Metric importance levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricsAggregationService:
    """
    Enterprise Metrics Aggregation Service
    
    Provides comprehensive metrics collection, aggregation, and analysis
    for enterprise-grade monitoring and observability.
    """
    
    def __init__(self):
        self.metrics_store = {}
        self.aggregated_metrics = {}
        self.metric_definitions = {}
        self.retention_policies = {}
        self.is_active = False
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize metrics aggregation service"""
        try:
            logger.info("Initializing Metrics Aggregation Service...")
            
            # Setup metric definitions
            await self._setup_metric_definitions()
            
            # Setup retention policies
            await self._setup_retention_policies()
            
            # Start aggregation loop
            asyncio.create_task(self._aggregation_loop())
            
            self.is_active = True
            
            return {
                "status": "success",
                "service": "metrics_aggregation",
                "metric_types": len(self.metric_definitions)
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics aggregation service: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _setup_metric_definitions(self):
        """Setup standard metric definitions"""
        self.metric_definitions = {
            # Performance metrics
            "request_duration": {
                "type": MetricType.HISTOGRAM,
                "description": "HTTP request duration in milliseconds",
                "labels": ["method", "endpoint", "status_code"],
                "unit": "milliseconds"
            },
            "request_count": {
                "type": MetricType.COUNTER,
                "description": "Total number of HTTP requests",
                "labels": ["method", "endpoint", "status_code"],
                "unit": "requests"
            },
            "active_connections": {
                "type": MetricType.GAUGE,
                "description": "Number of active connections",
                "labels": ["service", "type"],
                "unit": "connections"
            },
            
            # Business metrics
            "creator_registrations": {
                "type": MetricType.COUNTER,
                "description": "Number of creator registrations",
                "labels": ["platform", "tier"],
                "unit": "registrations"
            },
            "content_uploads": {
                "type": MetricType.COUNTER,
                "description": "Number of content uploads",
                "labels": ["content_type", "platform"],
                "unit": "uploads"
            },
            "revenue_generated": {
                "type": MetricType.COUNTER,
                "description": "Revenue generated in USD",
                "labels": ["platform", "payment_method"],
                "unit": "usd"
            },
            
            # System metrics
            "cpu_usage": {
                "type": MetricType.GAUGE,
                "description": "CPU usage percentage",
                "labels": ["service", "instance"],
                "unit": "percentage"
            },
            "memory_usage": {
                "type": MetricType.GAUGE,
                "description": "Memory usage in MB",
                "labels": ["service", "instance"],
                "unit": "megabytes"
            },
            "error_rate": {
                "type": MetricType.GAUGE,
                "description": "Error rate percentage",
                "labels": ["service", "error_type"],
                "unit": "percentage"
            }
        }
    
    async def _setup_retention_policies(self):
        """Setup data retention policies"""
        self.retention_policies = {
            "raw_metrics": timedelta(days=7),      # Raw metrics for 7 days
            "hourly_aggregates": timedelta(days=30),  # Hourly aggregates for 30 days
            "daily_aggregates": timedelta(days=365),  # Daily aggregates for 1 year
            "monthly_aggregates": timedelta(days=1825)  # Monthly aggregates for 5 years
        }
    
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Record a new metric"""
        try:
            if metric_name not in self.metric_definitions:
                return {"status": "error", "error": "Unknown metric"}
            
            metric_timestamp = timestamp or datetime.utcnow()
            metric_labels = labels or {}
            
            # Create metric key
            metric_key = self._create_metric_key(metric_name, metric_labels)
            
            # Store metric
            if metric_key not in self.metrics_store:
                self.metrics_store[metric_key] = []
            
            metric_data = {
                "timestamp": metric_timestamp.isoformat(),
                "value": value,
                "labels": metric_labels
            }
            
            self.metrics_store[metric_key].append(metric_data)
            
            # Apply retention policy
            await self._apply_retention_policy(metric_key)
            
            return {
                "status": "success",
                "metric_name": metric_name,
                "recorded_at": metric_timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            return {"status": "error", "error": str(e)}
    
    def _create_metric_key(self, metric_name: str, labels: Dict[str, str]) -> str:
        """Create unique metric key"""
        labels_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric_name}{{labels_str}}" if labels_str else metric_name
    
    async def _apply_retention_policy(self, metric_key: str):
        """Apply retention policy to metric data"""
        if metric_key not in self.metrics_store:
            return
        
        retention_cutoff = datetime.utcnow() - self.retention_policies["raw_metrics"]
        
        # Remove old data points
        self.metrics_store[metric_key] = [
            metric for metric in self.metrics_store[metric_key]
            if datetime.fromisoformat(metric["timestamp"]) > retention_cutoff
        ]
        
        # Remove empty metric keys
        if not self.metrics_store[metric_key]:
            del self.metrics_store[metric_key]
    
    async def _aggregation_loop(self):
        """Continuous aggregation loop"""
        while self.is_active:
            try:
                await self._perform_aggregation()
                await asyncio.sleep(60)  # Aggregate every minute
                
            except Exception as e:
                logger.error(f"Error in aggregation loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _perform_aggregation(self):
        """Perform metric aggregation"""
        current_time = datetime.utcnow()
        
        # Aggregate by hour
        for metric_key, metric_data in self.metrics_store.items():
            if not metric_data:
                continue
            
            # Group by hour
            hourly_buckets = {}
            for data_point in metric_data:
                timestamp = datetime.fromisoformat(data_point["timestamp"])
                hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
                
                if hour_key not in hourly_buckets:
                    hourly_buckets[hour_key] = []
                
                hourly_buckets[hour_key].append(data_point["value"])
            
            # Calculate aggregates for each hour
            for hour_key, values in hourly_buckets.items():
                aggregate_key = f"{metric_key}:hourly:{hour_key.isoformat()}"
                
                aggregate_data = {
                    "timestamp": hour_key.isoformat(),
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "percentiles": await self._calculate_percentiles(values)
                }
                
                self.aggregated_metrics[aggregate_key] = aggregate_data
    
    async def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentiles for values"""
        sorted_values = sorted(values)
        length = len(sorted_values)
        
        if length == 0:
            return {}
        
        percentiles = {}
        for p in [50, 90, 95, 99]:
            index = int((p / 100) * (length - 1))
            percentiles[f"p{p}"] = sorted_values[index]
        
        return percentiles
    
    async def query_metrics(
        self,
        metric_name: str,
        labels: Optional[Dict[str, str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        aggregation: str = "raw"
    ) -> Dict[str, Any]:
        """Query metrics with optional filtering and aggregation"""
        try:
            end_time = end_time or datetime.utcnow()
            start_time = start_time or (end_time - timedelta(hours=1))
            
            # Create metric key
            metric_key = self._create_metric_key(metric_name, labels or {})
            
            if aggregation == "raw":
                # Return raw metrics
                if metric_key not in self.metrics_store:
                    return {"status": "success", "data": [], "count": 0}
                
                # Filter by time range
                filtered_data = [
                    metric for metric in self.metrics_store[metric_key]
                    if start_time <= datetime.fromisoformat(metric["timestamp"]) <= end_time
                ]
                
                return {
                    "status": "success",
                    "metric_name": metric_name,
                    "labels": labels,
                    "data": filtered_data,
                    "count": len(filtered_data),
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    }
                }
            
            else:
                # Return aggregated metrics
                aggregated_data = []
                
                for agg_key, agg_data in self.aggregated_metrics.items():
                    if agg_key.startswith(f"{metric_key}:{aggregation}"):
                        agg_timestamp = datetime.fromisoformat(agg_data["timestamp"])
                        if start_time <= agg_timestamp <= end_time:
                            aggregated_data.append(agg_data)
                
                return {
                    "status": "success",
                    "metric_name": metric_name,
                    "labels": labels,
                    "aggregation": aggregation,
                    "data": aggregated_data,
                    "count": len(aggregated_data),
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    }
                }
            
        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        try:
            if metric_name not in self.metric_definitions:
                return {"status": "error", "error": "Unknown metric"}
            
            # Find all metrics matching the name
            matching_metrics = []
            for key, data_points in self.metrics_store.items():
                if key.startswith(metric_name):
                    matching_metrics.extend([dp["value"] for dp in data_points])
            
            if not matching_metrics:
                return {
                    "status": "success",
                    "metric_name": metric_name,
                    "summary": "No data available"
                }
            
            summary = {
                "count": len(matching_metrics),
                "sum": sum(matching_metrics),
                "avg": sum(matching_metrics) / len(matching_metrics),
                "min": min(matching_metrics),
                "max": max(matching_metrics),
                "percentiles": await self._calculate_percentiles(matching_metrics)
            }
            
            return {
                "status": "success",
                "metric_name": metric_name,
                "definition": self.metric_definitions[metric_name],
                "summary": summary,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get metric summary: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get metrics aggregation service metrics"""
        total_metrics = sum(len(data) for data in self.metrics_store.values())
        
        return {
            "service": "metrics_aggregation",
            "metrics": {
                "total_metric_points": total_metrics,
                "unique_metrics": len(self.metrics_store),
                "metric_definitions": len(self.metric_definitions),
                "aggregated_metrics": len(self.aggregated_metrics),
                "retention_policies": len(self.retention_policies),
                "aggregation_enabled": self.is_active
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "metrics_aggregation",
            "status": "healthy" if self.is_active else "inactive",
            "storage_size": len(self.metrics_store),
            "aggregation_active": self.is_active,
            "last_check": datetime.utcnow().isoformat()
        }