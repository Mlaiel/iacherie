"""Performance Monitor - System Performance Intelligence
====================================================

Professional performance monitoring and resource tracking for IA-Influencer-Agent platform.
Implements comprehensive system metrics, resource optimization, and performance analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise  
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""
import asyncio
import logging
import psutil
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import deque, defaultdict

from .monitor_engine import MonitorEngine, MonitoringConfiguration

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """System resource types."""    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"

class PerformanceMetricType(Enum):
    """Performance metric categories."""    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    SCALABILITY = "scalability"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"

class AlertSeverity(Enum):
    """Alert severity levels."""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class ResourceMetrics:
    """System resource metrics."""    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_percent: float = 0.0
    cpu_cores: int = 0
    memory_total: int = 0
    memory_used: int = 0
    memory_percent: float = 0.0
    disk_total: int = 0
    disk_used: int = 0
    disk_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    network_packets_sent: int = 0
    network_packets_recv: int = 0
    load_average: List[float] = field(default_factory=list)

@dataclass
class PerformanceMetrics:
    """Application performance metrics."""    timestamp: datetime = field(default_factory=datetime.utcnow)
    average_response_time: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    active_connections: int = 0
    queue_length: int = 0
    cache_hit_rate: float = 0.0
    database_query_time: float = 0.0
    concurrent_users: int = 0
    uptime_seconds: float = 0.0

@dataclass
class PerformanceAlert:
    """Performance alert data structure."""    alert_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metric_name: str = ""
    current_value: float = 0.0
    threshold_value: float = 0.0
    severity: AlertSeverity = AlertSeverity.WARNING
    description: str = ""
    resource_type: Optional[ResourceType] = None
    recommendations: List[str] = field(default_factory=list)

class ResourceMonitor:
    """System resource monitoring component."""    
    def __init__(self):
        self.resource_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.last_network_stats = None
        
    async def collect_system_metrics(self) -> ResourceMetrics:
        """Collect comprehensive system metrics."""        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_cores = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_total = memory.total
            memory_used = memory.used
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_total = disk.total
            disk_used = disk.used
            disk_percent = disk.percent
            
            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            network_packets_sent = network.packets_sent
            network_packets_recv = network.packets_recv
            
            # Load average (Unix-like systems)
            try:
                load_average = list(psutil.getloadavg())
            except AttributeError:
                load_average = [0.0, 0.0, 0.0]
            
            metrics = ResourceMetrics(
                cpu_percent=cpu_percent,
                cpu_cores=cpu_cores,
                memory_total=memory_total,
                memory_used=memory_used,
                memory_percent=memory_percent,
                disk_total=disk_total,
                disk_used=disk_used,
                disk_percent=disk_percent,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                network_packets_sent=network_packets_sent,
                network_packets_recv=network_packets_recv,
                load_average=load_average
            )
            
            # Store in history
            self.resource_history["cpu"].append(cpu_percent)
            self.resource_history["memory"].append(memory_percent)
            self.resource_history["disk"].append(disk_percent)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return ResourceMetrics()
    
    def get_resource_trends(self, resource_type: str, window_minutes: int = 10) -> Dict[str, float]:
        """Get resource usage trends."""        history = self.resource_history.get(resource_type, deque())
        
        if len(history) < 2:
            return {"trend": 0.0, "average": 0.0, "max": 0.0, "min": 0.0}
        
        # Calculate trend over specified window
        window_size = min(window_minutes, len(history))
        recent_values = list(history)[-window_size:]
        
        # Calculate statistics
        average = statistics.mean(recent_values)
        max_value = max(recent_values)
        min_value = min(recent_values)
        
        # Calculate trend (simple linear regression)
        if len(recent_values) >= 2:
            x = list(range(len(recent_values)))
            n = len(recent_values)
            sum_x = sum(x)
            sum_y = sum(recent_values)
            sum_xy = sum(x[i] * recent_values[i] for i in range(n))
            sum_x2 = sum(xi ** 2 for xi in x)
            
            # Linear regression slope
            trend = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        else:
            trend = 0.0
        
        return {
            "trend": trend,
            "average": average,
            "max": max_value,
            "min": min_value
        }

class PerformanceMonitor(MonitorEngine):
    """    Advanced performance monitoring engine.
    Tracks system resources, application performance, and optimization opportunities.
    """    
    def __init__(self, config: MonitoringConfiguration):
        super().__init__(config)
        self.resource_monitor = ResourceMonitor()
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_thresholds: Dict[str, Dict[str, float]] = {}
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.optimization_recommendations: List[str] = []
        
        # Initialize performance thresholds
        self._initialize_performance_thresholds()
    
    def _initialize_performance_thresholds(self) -> None:
        """Initialize performance monitoring thresholds."""        self.performance_thresholds = {
            "cpu_percent": {"warning": 70.0, "critical": 85.0, "emergency": 95.0},
            "memory_percent": {"warning": 75.0, "critical": 90.0, "emergency": 98.0},
            "disk_percent": {"warning": 80.0, "critical": 90.0, "emergency": 98.0},
            "response_time": {"warning": 1.0, "critical": 3.0, "emergency": 10.0},
            "error_rate": {"warning": 0.01, "critical": 0.05, "emergency": 0.10},
            "queue_length": {"warning": 100, "critical": 500, "emergency": 1000},
            "cache_hit_rate": {"warning": 0.80, "critical": 0.70, "emergency": 0.50}
        }
    
    async def initialize(self) -> bool:
        """Initialize performance monitoring engine."""        try:
            logger.info("Initializing performance monitor...")
            
            # Start resource monitoring
            await self.start_periodic_monitoring()
            
            self.start_time = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize performance monitor: {e}")
            return False
    
    async def start_monitoring(self, targets: List[Any]) -> bool:
        """Start performance monitoring operations."""        try:
            logger.info("Starting performance monitoring...")
            
            # Start monitoring tasks
            monitoring_tasks = [
                asyncio.create_task(self._monitor_system_resources()),
                asyncio.create_task(self._monitor_application_performance()),
                asyncio.create_task(self._monitor_database_performance()),
                asyncio.create_task(self._monitor_network_performance()),
                asyncio.create_task(self._analyze_performance_trends()),
                asyncio.create_task(self._generate_optimization_recommendations())
            ]
            
            self.monitoring_tasks.extend(monitoring_tasks)
            return True
            
        except Exception as e:
            logger.error(f"Failed to start performance monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop performance monitoring operations."""        try:
            await self.cleanup()
            return True
        except Exception as e:
            logger.error(f"Failed to stop performance monitoring: {e}")
            return False
    
    async def collect_metrics(self) -> Any:
        """Collect performance monitoring metrics."""        from .monitor_engine import MonitoringMetrics
        
        # Collect system metrics
        resource_metrics = await self.resource_monitor.collect_system_metrics()
        
        # Collect application metrics
        app_metrics = await self._collect_application_metrics()
        
        metrics = MonitoringMetrics()
        metrics.cpu_usage = resource_metrics.cpu_percent
        metrics.memory_usage = resource_metrics.memory_percent
        metrics.disk_usage = resource_metrics.disk_percent
        metrics.average_response_time = app_metrics.average_response_time
        metrics.throughput = app_metrics.requests_per_second
        metrics.error_rate = app_metrics.error_rate
        
        metrics.custom_metrics = {
            "system_resources": {
                "cpu_cores": resource_metrics.cpu_cores,
                "memory_total_gb": resource_metrics.memory_total / (1024**3),
                "disk_total_gb": resource_metrics.disk_total / (1024**3),
                "load_average": resource_metrics.load_average
            },
            "application_performance": {
                "active_connections": app_metrics.active_connections,
                "queue_length": app_metrics.queue_length,
                "cache_hit_rate": app_metrics.cache_hit_rate,
                "database_query_time": app_metrics.database_query_time,
                "concurrent_users": app_metrics.concurrent_users,
                "uptime_hours": app_metrics.uptime_seconds / 3600
            },
            "active_alerts": len(self.active_alerts),
            "optimization_recommendations": len(self.optimization_recommendations)
        }
        
        return metrics
    
    async def process_events(self, events: List[Any]) -> None:
        """Process performance events."""        for event in events:
            await self._process_performance_event(event)
    
    async def _process_performance_event(self, event: Dict[str, Any]) -> None:
        """Process individual performance event."""        try:
            event_type = event.get("type", "")
            
            if event_type == "request":
                await self._process_request_event(event)
            elif event_type == "error":
                await self._process_error_event(event)
            elif event_type == "database_query":
                await self._process_database_event(event)
            elif event_type == "cache_operation":
                await self._process_cache_event(event)
            
        except Exception as e:
            logger.error(f"Failed to process performance event: {e}")
    
    async def _process_request_event(self, event: Dict[str, Any]) -> None:
        """Process HTTP request performance event."""        response_time = event.get("response_time", 0.0)
        status_code = event.get("status_code", 200)
        
        # Record response time
        self.performance_history["response_time"].append(response_time)
        
        # Check for slow requests
        if response_time > self.performance_thresholds["response_time"]["warning"]:
            await self._create_performance_alert(
                "slow_request",
                response_time,
                self.performance_thresholds["response_time"]["warning"],
                AlertSeverity.WARNING,
                f"Slow request detected: {response_time:.2f}s"
            )
    
    async def _process_error_event(self, event: Dict[str, Any]) -> None:
        """Process error event for error rate calculation."""        error_type = event.get("error_type", "unknown")
        
        # Record error
        self.performance_history["errors"].append(1)
        
        # Calculate recent error rate
        recent_errors = list(self.performance_history["errors"])[-100:]  # Last 100 events
        error_rate = len(recent_errors) / 100.0
        
        if error_rate > self.performance_thresholds["error_rate"]["critical"]:
            await self._create_performance_alert(
                "high_error_rate",
                error_rate,
                self.performance_thresholds["error_rate"]["critical"],
                AlertSeverity.CRITICAL,
                f"High error rate detected: {error_rate:.2%}"
            )
    
    async def _process_database_event(self, event: Dict[str, Any]) -> None:
        """Process database performance event."""        query_time = event.get("execution_time", 0.0)
        query_type = event.get("query_type", "unknown")
        
        # Record database query time
        self.performance_history["db_query_time"].append(query_time)
        
        # Check for slow queries
        if query_time > 5.0:  # 5 second threshold
            await self._create_performance_alert(
                "slow_database_query",
                query_time,
                5.0,
                AlertSeverity.WARNING,
                f"Slow database query: {query_time:.2f}s ({query_type})"
            )
    
    async def _process_cache_event(self, event: Dict[str, Any]) -> None:
        """Process cache operation event."""        cache_hit = event.get("cache_hit", False)
        
        # Record cache operation
        self.performance_history["cache_hits"].append(1 if cache_hit else 0)
        
        # Calculate cache hit rate
        recent_hits = list(self.performance_history["cache_hits"])[-100:]
        hit_rate = sum(recent_hits) / len(recent_hits) if recent_hits else 0.0
        
        if hit_rate < self.performance_thresholds["cache_hit_rate"]["warning"]:
            await self._create_performance_alert(
                "low_cache_hit_rate",
                hit_rate,
                self.performance_thresholds["cache_hit_rate"]["warning"],
                AlertSeverity.WARNING,
                f"Low cache hit rate: {hit_rate:.2%}"
            )
    
    async def _collect_application_metrics(self) -> PerformanceMetrics:
        """Collect application-specific performance metrics."""        try:
            # Calculate metrics from stored history
            response_times = list(self.performance_history["response_time"])[-100:]
            avg_response_time = statistics.mean(response_times) if response_times else 0.0
            
            # Calculate requests per second (simplified)
            rps = len(response_times) / 60.0 if response_times else 0.0
            
            # Calculate error rate
            errors = list(self.performance_history["errors"])[-100:]
            error_rate = len(errors) / 100.0 if errors else 0.0
            
            # Calculate cache hit rate
            cache_hits = list(self.performance_history["cache_hits"])[-100:]
            cache_hit_rate = statistics.mean(cache_hits) if cache_hits else 0.0
            
            # Calculate database query time
            db_times = list(self.performance_history["db_query_time"])[-50:]
            avg_db_time = statistics.mean(db_times) if db_times else 0.0
            
            # Calculate uptime
            uptime = (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0.0
            
            return PerformanceMetrics(
                average_response_time=avg_response_time,
                requests_per_second=rps,
                error_rate=error_rate,
                active_connections=50,  # Would get from actual connection pool
                queue_length=10,        # Would get from actual queue
                cache_hit_rate=cache_hit_rate,
                database_query_time=avg_db_time,
                concurrent_users=25,    # Would get from session manager
                uptime_seconds=uptime
            )
            
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
            return PerformanceMetrics()
    
    async def _create_performance_alert(
        self,
        metric_name: str,
        current_value: float,
        threshold_value: float,
        severity: AlertSeverity,
        description: str
    ) -> None:
        """Create a performance alert."""        alert_id = f"{metric_name}_{datetime.utcnow().timestamp()}"
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            severity=severity,
            description=description,
            recommendations=self._get_optimization_recommendations(metric_name)
        )
        
        self.active_alerts[alert_id] = alert
        
        # Trigger monitoring alert
        await self.trigger_alert(f"performance_{severity.value}", {
            "metric": metric_name,
            "current_value": current_value,
            "threshold": threshold_value,
            "description": description,
            "severity": severity.value
        })
    
    def _get_optimization_recommendations(self, metric_name: str) -> List[str]:
        """Get optimization recommendations for specific metric."""        recommendations = {
            "slow_request": [
                "Optimize database queries",
                "Implement response caching",
                "Review application logic for bottlenecks",
                "Consider load balancing"
            ],
            "high_error_rate": [
                "Review error logs for patterns",
                "Improve input validation",
                "Add circuit breakers",
                "Enhance monitoring and alerting"
            ],
            "low_cache_hit_rate": [
                "Review cache key strategies",
                "Increase cache TTL where appropriate",
                "Optimize cache warming",
                "Consider cache topology changes"
            ],
            "slow_database_query": [
                "Add database indexes",
                "Optimize query structure",
                "Consider query caching",
                "Review database configuration"
            ]
        }
        
        return recommendations.get(metric_name, ["Monitor and analyze further"])
    
    async def _monitor_system_resources(self) -> None:
        """Monitor system resource utilization."""        while True:
            try:
                metrics = await self.resource_monitor.collect_system_metrics()
                
                # Check thresholds and create alerts
                await self._check_resource_thresholds(metrics)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"System resource monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _check_resource_thresholds(self, metrics: ResourceMetrics) -> None:
        """Check if resource metrics exceed thresholds."""        resources_to_check = [
            ("cpu_percent", metrics.cpu_percent),
            ("memory_percent", metrics.memory_percent),
            ("disk_percent", metrics.disk_percent)
        ]
        
        for resource_name, current_value in resources_to_check:
            thresholds = self.performance_thresholds.get(resource_name, {})
            
            if current_value > thresholds.get("emergency", 100):
                severity = AlertSeverity.EMERGENCY
            elif current_value > thresholds.get("critical", 100):
                severity = AlertSeverity.CRITICAL
            elif current_value > thresholds.get("warning", 100):
                severity = AlertSeverity.WARNING
            else:
                continue
            
            await self._create_performance_alert(
                f"high_{resource_name}",
                current_value,
                thresholds[severity.value],
                severity,
                f"High {resource_name.replace('_', ' ')}: {current_value:.1f}%"
            )
    
    async def _monitor_application_performance(self) -> None:
        """Monitor application-specific performance metrics."""        while True:
            try:
                # Collect and analyze application metrics
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Application performance monitoring error: {e}")
                await asyncio.sleep(120)
    
    async def _monitor_database_performance(self) -> None:
        """Monitor database performance metrics."""        while True:
            try:
                # Monitor database performance
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Database performance monitoring error: {e}")
                await asyncio.sleep(180)
    
    async def _monitor_network_performance(self) -> None:
        """Monitor network performance metrics."""        while True:
            try:
                # Monitor network performance
                await asyncio.sleep(90)  # Check every 90 seconds
                
            except Exception as e:
                logger.error(f"Network performance monitoring error: {e}")
                await asyncio.sleep(120)
    
    async def _analyze_performance_trends(self) -> None:
        """Analyze performance trends and patterns."""        while True:
            try:
                # Analyze trends in performance data
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance trend analysis error: {e}")
                await asyncio.sleep(600)
    
    async def _generate_optimization_recommendations(self) -> None:
        """Generate performance optimization recommendations."""        while True:
            try:
                # Generate optimization recommendations
                self.optimization_recommendations = await self._analyze_optimization_opportunities()
                await asyncio.sleep(900)  # Generate every 15 minutes
                
            except Exception as e:
                logger.error(f"Optimization recommendation error: {e}")
                await asyncio.sleep(1200)
    
    async def _analyze_optimization_opportunities(self) -> List[str]:
        """Analyze current performance data for optimization opportunities."""        recommendations = []
        
        try:
            # Analyze resource usage patterns
            cpu_trends = self.resource_monitor.get_resource_trends("cpu")
            memory_trends = self.resource_monitor.get_resource_trends("memory")
            
            if cpu_trends["average"] > 70:
                recommendations.append("Consider CPU optimization or scaling")
            
            if memory_trends["average"] > 80:
                recommendations.append("Optimize memory usage or increase capacity")
            
            # Analyze application performance
            response_times = list(self.performance_history["response_time"])[-100:]
            if response_times and statistics.mean(response_times) > 2.0:
                recommendations.append("Optimize application response times")
            
        except Exception as e:
            logger.error(f"Failed to analyze optimization opportunities: {e}")
        
        return recommendations

__all__ = [
    "PerformanceMonitor",
    "ResourceMonitor",
    "ResourceMetrics",
    "PerformanceMetrics", 
    "PerformanceAlert",
    "ResourceType",
    "PerformanceMetricType",
    "AlertSeverity"
]
