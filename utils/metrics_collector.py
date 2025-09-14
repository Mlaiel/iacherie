"""
Metrics Collector - DevOps Expert Implementation
===============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade metrics collection for monitoring and observability.
"""

import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

# Optional dependency
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """Structured metric data"""
    name: str
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


class MetricsCollector:
    """
    Enterprise-grade metrics collection system
    Implements DevOps best practices for monitoring
    """
    
    def __init__(self, collection_interval -> None: int = 30) -> None:
        """Initialize metrics collector"""
        self.collection_interval = collection_interval
        self.metrics_buffer: List[MetricData] = []
        self.collectors = {}
        self.is_running = False
        self.last_collection = None
        
        # System metrics tracking
        self.system_metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'network_io': {'bytes_sent': 0, 'bytes_recv': 0}
        }
        
        # Business metrics tracking
        self.business_metrics = {
            'active_users': 0,
            'content_uploads': 0,
            'ai_processing_requests': 0,
            'api_requests': 0,
            'error_rate': 0.0
        }
        
        logger.info("MetricsCollector initialized")
    
    def collect_system_metrics(self) -> List[MetricData]:
        """Collect system-level metrics"""
        metrics = []
        timestamp = datetime.now()
        
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available, skipping system metrics")
            return metrics
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(MetricData(
                name="system.cpu.usage",
                value=cpu_percent,
                timestamp=timestamp,
                unit="percent"
            ))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.append(MetricData(
                name="system.memory.usage",
                value=memory.percent,
                timestamp=timestamp,
                unit="percent"
            ))
            
            metrics.append(MetricData(
                name="system.memory.available",
                value=memory.available,
                timestamp=timestamp,
                unit="bytes"
            ))
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            metrics.append(MetricData(
                name="system.disk.usage",
                value=disk_percent,
                timestamp=timestamp,
                unit="percent"
            ))
            
            # Network metrics
            network = psutil.net_io_counters()
            metrics.append(MetricData(
                name="system.network.bytes_sent",
                value=network.bytes_sent,
                timestamp=timestamp,
                unit="bytes"
            ))
            
            metrics.append(MetricData(
                name="system.network.bytes_recv",
                value=network.bytes_recv,
                timestamp=timestamp,
                unit="bytes"
            ))
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
        
        return metrics
    
    def collect_application_metrics(self) -> List[MetricData]:
        """Collect application-specific metrics"""
        metrics = []
        timestamp = datetime.now()
        
        # Add business logic metrics
        for metric_name, value in self.business_metrics.items():
            metrics.append(MetricData(
                name=f"app.{metric_name}",
                value=value,
                timestamp=timestamp,
                tags={"service": "ainflue"}
            ))
        
        return metrics
    
    def record_metric(self, name -> None: str, value -> None: Union[int, float], 
                     tags -> None: Optional[Dict[str, str]] = None, unit -> None: str = "") -> None:
        """Record a custom metric"""
        metric = MetricData(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            unit=unit
        )
        self.metrics_buffer.append(metric)
        logger.debug(f"Recorded metric: {name}={value}")
    
    def increment_counter(self, name -> None: str, tags -> None: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric"""
        # In a real implementation, this would use a proper counter
        self.record_metric(name, 1, tags, "count")
    
    def set_gauge(self, name -> None: str, value -> None: Union[int, float], 
                  tags -> None: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric"""
        self.record_metric(name, value, tags, "gauge")
    
    async def start_collection(self) -> None:
        """Start automatic metrics collection"""
        self.is_running = True
        logger.info("Starting metrics collection")
        
        while self.is_running:
            try:
                # Collect all metrics
                system_metrics = self.collect_system_metrics()
                app_metrics = self.collect_application_metrics()
                
                # Add to buffer
                self.metrics_buffer.extend(system_metrics)
                self.metrics_buffer.extend(app_metrics)
                
                self.last_collection = datetime.now()
                
                # Trim buffer if too large
                if len(self.metrics_buffer) > 10000:
                    self.metrics_buffer = self.metrics_buffer[-5000:]
                
                logger.debug(f"Collected {len(system_metrics + app_metrics)} metrics")
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
            
            await asyncio.sleep(self.collection_interval)
    
    def stop_collection(self) -> None:
        """Stop metrics collection"""
        self.is_running = False
        logger.info("Stopped metrics collection")
    
    def get_metrics(self, since: Optional[datetime] = None) -> List[MetricData]:
        """Get collected metrics"""
        if since is None:
            return self.metrics_buffer.copy()
        
        return [m for m in self.metrics_buffer if m.timestamp >= since]
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format"""
        if format_type == "json":
            metrics_data = []
            for metric in self.metrics_buffer:
                metrics_data.append({
                    "name": metric.name,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "tags": metric.tags,
                    "unit": metric.unit
                })
            return json.dumps(metrics_data, indent=2)
        
        elif format_type == "prometheus":
            # Basic Prometheus format
            lines = []
            for metric in self.metrics_buffer:
                metric_line = f"{metric.name} {metric.value}"
                if metric.tags:
                    tag_str = ",".join([f'{k}="{v}"' for k, v in metric.tags.items()])
                    metric_line = f"{metric.name}{{{tag_str}}} {metric.value}"
                lines.append(metric_line)
            return "\n".join(lines)
        
        return ""
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health-related metrics for monitoring"""
        recent_metrics = self.get_metrics(since=datetime.now() - timedelta(minutes=5))
        
        health_data = {
            "collector_status": "running" if self.is_running else "stopped",
            "last_collection": self.last_collection.isoformat() if self.last_collection else None,
            "metrics_count": len(self.metrics_buffer),
            "recent_metrics_count": len(recent_metrics),
            "collection_interval": self.collection_interval
        }
        
        # Add latest system metrics
        if recent_metrics:
            latest_by_name = {}
            for metric in reversed(recent_metrics):
                if metric.name not in latest_by_name:
                    latest_by_name[metric.name] = metric.value
            
            health_data["latest_metrics"] = latest_by_name
        
        return health_data


# Global instance for easy access
metrics_collector = MetricsCollector()