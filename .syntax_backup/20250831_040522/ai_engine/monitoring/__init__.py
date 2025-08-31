"""Monitoring Integration Hub

Central integration point for all monitoring components in the IA Influencer Agent platform.
Provides unified API and orchestration for comprehensive system observability.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from ..core.metrics import MetricsCollector, MetricEntry, MetricType
from ..core.exceptions import MonitoringError
from .ai_performance import AIPerformanceMonitor
from .content_monitoring import ContentProcessingMonitor
from .business_metrics import BusinessMetricsCollector
from .real_time_alerts import RealTimeAlerts
from .health_checks import HealthChecks
from .anomaly_detection import AnomalyDetection
from .reporting import ReportingSystem, ReportType, ReportFormat

logger = logging.getLogger(__name__)


class MonitoringServiceStatus(Enum):
    """Status of monitoring services"""    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class MonitoringLevel(Enum):
    """Monitoring detail levels"""    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    DEBUG = "debug"


@dataclass
class MonitoringConfig:
    """Configuration for the monitoring system"""    level: MonitoringLevel = MonitoringLevel.STANDARD
    ai_monitoring_enabled: bool = True
    content_monitoring_enabled: bool = True
    business_monitoring_enabled: bool = True
    health_monitoring_enabled: bool = True
    anomaly_detection_enabled: bool = True
    reporting_enabled: bool = True
    alerts_enabled: bool = True
    
    # Service-specific configurations
    ai_config: Dict[str, Any] = field(default_factory=dict)
    content_config: Dict[str, Any] = field(default_factory=dict)
    business_config: Dict[str, Any] = field(default_factory=dict)
    health_config: Dict[str, Any] = field(default_factory=dict)
    anomaly_config: Dict[str, Any] = field(default_factory=dict)
    reporting_config: Dict[str, Any] = field(default_factory=dict)
    alerts_config: Dict[str, Any] = field(default_factory=dict)
    
    # Global settings
    metrics_retention_days: int = 30
    alert_cooldown_minutes: int = 15
    health_check_interval_seconds: int = 60
    anomaly_detection_interval_seconds: int = 300
    auto_restart_failed_services: bool = True
    data_export_enabled: bool = False
    data_export_path: Optional[str] = None


@dataclass
class ServiceHealth:
    """Health status of a monitoring service"""    service_name: str
    status: MonitoringServiceStatus
    last_update: datetime
    error_message: Optional[str] = None
    restart_count: int = 0
    uptime_seconds: float = 0.0
    metrics_collected: int = 0
    alerts_triggered: int = 0


@dataclass
class MonitoringSnapshot:
    """Complete monitoring system snapshot"""    timestamp: datetime
    overall_status: MonitoringServiceStatus
    services: Dict[str, ServiceHealth]
    system_metrics: Dict[str, Any]
    active_alerts: List[Dict[str, Any]]
    recent_anomalies: List[Dict[str, Any]]
    performance_summary: Dict[str, Any]


class MonitoringHub:
    """    Monitoring Integration Hub
    
    Central orchestration and management system for all monitoring components
    in the IA Influencer Agent platform. Provides unified API, health management,
    and comprehensive observability across AI, content, business, and system metrics.
    """    
    def __init__(
        self,
        config: Optional[MonitoringConfig] = None,
        data_dir: Optional[Path] = None
    ):
        self.config = config or MonitoringConfig()
        self.data_dir = data_dir or Path("/tmp/monitoring_hub")
        self.data_dir.mkdir(exist_ok=True)
        
        # Core monitoring services
        self.ai_monitor: Optional[AIPerformanceMonitor] = None
        self.content_monitor: Optional[ContentProcessingMonitor] = None
        self.business_metrics: Optional[BusinessMetricsCollector] = None
        self.alerts_system: Optional[RealTimeAlerts] = None
        self.health_checks: Optional[HealthChecks] = None
        self.anomaly_detection: Optional[AnomalyDetection] = None
        self.reporting_system: Optional[ReportingSystem] = None
        
        # Hub state
        self.status = MonitoringServiceStatus.STOPPED
        self.services_health: Dict[str, ServiceHealth] = {}
        self.startup_time: Optional[datetime] = None
        self.metrics_collector = MetricsCollector()
        
        # Background tasks
        self._monitor_tasks: List[asyncio.Task] = []
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._anomaly_monitor_task: Optional[asyncio.Task] = None
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Initialize services based on configuration
        self._initialize_services()

    def _initialize_services(self):
        """Initialize monitoring services based on configuration"""        try:
            # Initialize basic services without external dependencies
            from .real_time_alerts import RealTimeAlerts
            from .health_checks import HealthChecks
            
            self.alerts_system = RealTimeAlerts()
            self.health_checks = HealthChecks()
            
            # Only initialize advanced services if dependencies are available
            try:
                from .anomaly_detection import AnomalyDetection
                self.anomaly_detection = AnomalyDetection()
            except ImportError:
                pass
                
        except Exception as e:
            # Graceful degradation - log but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Some monitoring services could not be initialized: {e}")


# Global monitoring hub instance
monitoring_hub = MonitoringHub()

# Re-export compatibility components
from ..core.metrics import (
    MetricsCollector,
    MetricEntry,
    MetricType,
    TimerContext,
    metrics_collector
)

from ..core.performance import (
    PerformanceMonitor,
    PerformanceMetrics,
    performance_monitor
)

# Export monitoring components
from .ai_performance import AIPerformanceMonitor
from .content_monitoring import ContentProcessingMonitor
from .business_metrics import BusinessMetricsCollector
from .real_time_alerts import RealTimeAlerts
from .health_checks import HealthChecks
from .anomaly_detection import AnomalyDetection
from .reporting import ReportingSystem

__all__ = [
    # Hub components
    "MonitoringHub",
    "MonitoringConfig", 
    "MonitoringLevel",
    "MonitoringServiceStatus",
    "ServiceHealth",
    "MonitoringSnapshot",
    "monitoring_hub",
    
    # Individual monitoring services
    "AIPerformanceMonitor",
    "ContentProcessingMonitor", 
    "BusinessMetricsCollector",
    "RealTimeAlerts",
    "HealthChecks",
    "AnomalyDetection",
    "ReportingSystem",
    
    # Compatibility exports
    "MetricsCollector",
    "MetricEntry",
    "MetricType", 
    "TimerContext",
    "metrics_collector",
    "PerformanceMonitor",
    "PerformanceMetrics",
    "performance_monitor"
]
