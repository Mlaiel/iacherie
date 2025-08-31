"""Health Checks Module Index - IA Influencer Agent Platform
Main entry point for comprehensive health monitoring system

This module serves as the central orchestrator for all health monitoring
components, providing unified access to health checking capabilities across
the entire IA Influencer Agent platform.

Key Features:
- Unified health monitoring API
- Real-time health status aggregation
- Automated alerting and notification
- Performance metrics collection and analysis
- Health trend monitoring and prediction
- Multi-dimensional health scoring
- SLA monitoring and compliance tracking

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
      Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

# Import all health checking components
from .core_health import CoreHealthChecker, HealthStatus, HealthCheckResult
from .database_health import DatabaseHealthChecker
from .ml_health import MLServiceHealthChecker
from .protection_health import ProtectionServiceHealthChecker
from .monetization_health import MonetizationHealthChecker
from .external_api_health import ExternalAPIHealthChecker
from .infrastructure_health import InfrastructureHealthChecker
from .comprehensive_health import ComprehensiveHealthChecker, PlatformHealthSummary
from .metrics_collector import HealthMetricsCollector
from .alerting_system import HealthAlertingSystem

# Module metadata
__title__ = "IA Influencer Agent Health Monitoring System"
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright © 2025 Fahed Mlaiel. All Rights Reserved."
__license__ = "Proprietary"

# Logging configuration
logger = logging.getLogger(__name__)


@dataclass
class HealthMonitoringConfig:
    """Configuration for health monitoring system"""    enabled: bool = True
    check_interval_seconds: int = 300  # 5 minutes
    comprehensive_check_interval_seconds: int = 900  # 15 minutes
    metrics_collection_enabled: bool = True
    alerting_enabled: bool = True
    
    # Subsystem configurations
    core_health_enabled: bool = True
    database_health_enabled: bool = True
    ml_health_enabled: bool = True
    protection_health_enabled: bool = True
    monetization_health_enabled: bool = True
    external_api_health_enabled: bool = True
    infrastructure_health_enabled: bool = True
    
    # Alert thresholds
    alert_thresholds: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "response_time_ms": 2000,
                "cpu_threshold": 75,
                "memory_threshold": 80,
                "disk_threshold": 85,
                "error_rate_threshold": 5.0,
                "success_rate_threshold": 95.0
            }


class HealthMonitoringOrchestrator:
    """    Central orchestrator for IA Influencer Agent health monitoring
    
    This class provides the main interface for health monitoring across
    the entire platform, coordinating all subsystem health checkers and
    providing unified health status reporting.
    """
    def __init__(self, config: Dict[str, Any], app=None, redis_client=None):
        """        Initialize health monitoring orchestrator
        
        Args:
            config: Platform configuration dictionary
            app: FastAPI application instance (optional)
            redis_client: Redis client for distributed state (optional)
        """        self.config = config
        self.app = app
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Parse health monitoring configuration
        health_config = config.get("health_checks", {})
        self.monitoring_config = HealthMonitoringConfig(**health_config)
        
        # Initialize health checking components
        self._initialize_health_checkers()
        
        # Health monitoring state
        self._is_running = False
        self._last_comprehensive_check = None
        self._monitoring_task = None

    def _initialize_health_checkers(self):
        """Initialize all health checking components"""        try:
            # Core health checker
            if self.monitoring_config.core_health_enabled and self.app:
                self.core_checker = CoreHealthChecker(self.app, self.config)
                self.logger.info("Core health checker initialized")
            else:
                self.core_checker = None
                self.logger.warning("Core health checker disabled or no app provided")
            
            # Database health checker
            if self.monitoring_config.database_health_enabled:
                self.database_checker = DatabaseHealthChecker(self.config)
                self.logger.info("Database health checker initialized")
            else:
                self.database_checker = None
                self.logger.warning("Database health checker disabled")
            
            # ML services health checker
            if self.monitoring_config.ml_health_enabled:
                self.ml_checker = MLServiceHealthChecker(self.config)
                self.logger.info("ML services health checker initialized")
            else:
                self.ml_checker = None
                self.logger.warning("ML services health checker disabled")
            
            # Protection services health checker
            if self.monitoring_config.protection_health_enabled:
                self.protection_checker = ProtectionServiceHealthChecker(self.config)
                self.logger.info("Protection services health checker initialized")
            else:
                self.protection_checker = None
                self.logger.warning("Protection services health checker disabled")
            
            # Monetization health checker
            if self.monitoring_config.monetization_health_enabled:
                self.monetization_checker = MonetizationHealthChecker(self.config)
                self.logger.info("Monetization health checker initialized")
            else:
                self.monetization_checker = None
                self.logger.warning("Monetization health checker disabled")
            
            # External API health checker
            if self.monitoring_config.external_api_health_enabled:
                self.external_api_checker = ExternalAPIHealthChecker(self.config)
                self.logger.info("External API health checker initialized")
            else:
                self.external_api_checker = None
                self.logger.warning("External API health checker disabled")
            
            # Infrastructure health checker
            if self.monitoring_config.infrastructure_health_enabled:
                self.infrastructure_checker = InfrastructureHealthChecker(self.config)
                self.logger.info("Infrastructure health checker initialized")
            else:
                self.infrastructure_checker = None
                self.logger.warning("Infrastructure health checker disabled")
            
            # Comprehensive health checker
            self.comprehensive_checker = ComprehensiveHealthChecker(self.config, self.app)
            self.logger.info("Comprehensive health checker initialized")
            
            # Metrics collector
            if self.monitoring_config.metrics_collection_enabled:
                self.metrics_collector = HealthMetricsCollector(self.config)
                self.logger.info("Health metrics collector initialized")
            else:
                self.metrics_collector = None
                self.logger.warning("Health metrics collection disabled")
            
            # Alerting system
            if self.monitoring_config.alerting_enabled:
                self.alerting_system = HealthAlertingSystem(self.config, self.redis_client)
                self.logger.info("Health alerting system initialized")
            else:
                self.alerting_system = None
                self.logger.warning("Health alerting system disabled")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize health checkers: {str(e)}")
            raise

    async def start_monitoring(self):
        """Start continuous health monitoring"""        if self._is_running:
            self.logger.warning("Health monitoring is already running")
            return
        
        self._is_running = True
        self.logger.info("Starting continuous health monitoring")
        
        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Log monitoring configuration
        self.logger.info(
            f"Health monitoring started with {self.monitoring_config.check_interval_seconds}s interval"
        )

    async def stop_monitoring(self):
        """Stop continuous health monitoring"""        if not self._is_running:
            self.logger.warning("Health monitoring is not running")
            return
        
        self._is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup resources
        await self._cleanup_resources()
        
        self.logger.info("Health monitoring stopped")

    async def _monitoring_loop(self):
        """Main health monitoring loop"""        last_comprehensive_check = datetime.utcnow()
        
        while self._is_running:
            try:
                current_time = datetime.utcnow()
                
                # Determine if comprehensive check is needed
                time_since_comprehensive = (current_time - last_comprehensive_check).total_seconds()
                need_comprehensive_check = (
                    time_since_comprehensive >= self.monitoring_config.comprehensive_check_interval_seconds
                )
                
                if need_comprehensive_check:
                    # Perform comprehensive health check
                    await self._perform_comprehensive_health_check()
                    last_comprehensive_check = current_time
                else:
                    # Perform quick health check
                    await self._perform_quick_health_check()
                
                # Wait for next check interval
                await asyncio.sleep(self.monitoring_config.check_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring loop error: {str(e)}")
                # Continue monitoring after error
                await asyncio.sleep(30)  # Wait 30 seconds before retrying

    async def _perform_comprehensive_health_check(self):
        """Perform comprehensive health check across all subsystems"""        try:
            self.logger.info("Performing comprehensive health check")
            
            # Execute comprehensive health check
            health_summary = await self.comprehensive_checker.perform_comprehensive_health_check()
            self._last_comprehensive_check = health_summary
            
            # Collect all health results for processing
            all_health_results = []
            for subsystem_name, subsystem_summary in health_summary.subsystem_summaries.items():
                # Extract health results from subsystem summary if available
                if hasattr(subsystem_summary, 'detailed_results'):
                    all_health_results.extend(subsystem_summary['detailed_results'])
            
            # Process metrics if enabled
            if self.metrics_collector:
                await self.metrics_collector.collect_health_metrics(all_health_results)
                
                # Cleanup old metrics
                await self.metrics_collector.cleanup_old_metrics()
            
            # Process alerts if enabled
            if self.alerting_system:
                await self.alerting_system.process_health_results(all_health_results)
            
            # Log health summary
            self.logger.info(
                f"Comprehensive health check completed. "
                f"Status: {health_summary.overall_status}, "
                f"Health: {health_summary.overall_health_percentage:.1f}%, "
                f"Services: {health_summary.healthy_services}/{health_summary.total_services}"
            )
            
        except Exception as e:
            self.logger.error(f"Comprehensive health check failed: {str(e)}")

    async def _perform_quick_health_check(self):
        """Perform quick health check of critical services"""        try:
            # Quick readiness check
            readiness_status = await self.comprehensive_checker.check_service_readiness()
            
            if readiness_status["readiness_status"] != "ready":
                self.logger.warning(f"Service readiness issue: {readiness_status['message']}")
                
                # If critical services are down, trigger alerts
                if self.alerting_system:
                    # Create critical health result for alerting
                    critical_result = HealthCheckResult(
                        service="platform_readiness",
                        status=HealthStatus.CRITICAL,
                        response_time_ms=readiness_status.get("check_duration_ms", 0),
                        timestamp=datetime.utcnow(),
                        details=readiness_status,
                        error_message=readiness_status.get("message")
                    )
                    
                    await self.alerting_system.process_health_results([critical_result])
            
        except Exception as e:
            self.logger.error(f"Quick health check failed: {str(e)}")

    async def get_current_health_status(self) -> Dict[str, Any]:
        """        Get current platform health status
        
        Returns:
            Dict[str, Any]: Current health status and metrics
        """        try:
            if self._last_comprehensive_check:
                # Return last comprehensive check results
                health_data = asdict(self._last_comprehensive_check)
                health_data["monitoring_status"] = "active" if self._is_running else "stopped"
                health_data["last_update"] = datetime.utcnow().isoformat()
                return health_data
            else:
                # Perform immediate health check if no cached results
                health_summary = await self.comprehensive_checker.perform_comprehensive_health_check()
                health_data = asdict(health_summary)
                health_data["monitoring_status"] = "active" if self._is_running else "stopped"
                health_data["last_update"] = datetime.utcnow().isoformat()
                return health_data
                
        except Exception as e:
            self.logger.error(f"Failed to get current health status: {str(e)}")
            return {
                "error": str(e),
                "monitoring_status": "error",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_subsystem_health(self, subsystem_name: str) -> Dict[str, Any]:
        """        Get detailed health information for specific subsystem
        
        Args:
            subsystem_name: Name of subsystem to check
            
        Returns:
            Dict[str, Any]: Detailed subsystem health information
        """        try:
            return await self.comprehensive_checker.get_subsystem_health(subsystem_name)
        except Exception as e:
            self.logger.error(f"Failed to get {subsystem_name} health: {str(e)}")
            return {
                "error": str(e),
                "subsystem": subsystem_name,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_health_metrics(self, time_range_hours: int = 1) -> Dict[str, Any]:
        """        Get health metrics summary
        
        Args:
            time_range_hours: Time range for metrics in hours
            
        Returns:
            Dict[str, Any]: Health metrics summary
        """        try:
            if self.metrics_collector:
                return await self.metrics_collector.get_metrics_summary(time_range_hours)
            else:
                return {
                    "error": "Metrics collection is disabled",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get health metrics: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_health_trends(self, service_name: str, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """        Get health trends for specific service and metric
        
        Args:
            service_name: Name of service
            metric_name: Name of metric
            hours: Number of hours to analyze
            
        Returns:
            Dict[str, Any]: Health trend analysis
        """        try:
            if self.metrics_collector:
                trend = await self.metrics_collector.analyze_health_trends(
                    service_name, metric_name, hours
                )
                return asdict(trend)
            else:
                return {
                    "error": "Metrics collection is disabled",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get health trends: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """        Get all active health alerts
        
        Returns:
            List[Dict[str, Any]]: List of active alerts
        """        try:
            if self.alerting_system:
                return await self.alerting_system.get_active_alerts()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Failed to get active alerts: {str(e)}")
            return []

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """        Acknowledge a health alert
        
        Args:
            alert_id: ID of alert to acknowledge
            acknowledged_by: User acknowledging the alert
            
        Returns:
            bool: True if alert was acknowledged successfully
        """        try:
            if self.alerting_system:
                return await self.alerting_system.acknowledge_alert(alert_id, acknowledged_by)
            else:
                return False
        except Exception as e:
            self.logger.error(f"Failed to acknowledge alert {alert_id}: {str(e)}")
            return False

    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """        Resolve a health alert
        
        Args:
            alert_id: ID of alert to resolve
            resolved_by: User/system resolving the alert
            
        Returns:
            bool: True if alert was resolved successfully
        """        try:
            if self.alerting_system:
                return await self.alerting_system.resolve_alert(alert_id, resolved_by)
            else:
                return False
        except Exception as e:
            self.logger.error(f"Failed to resolve alert {alert_id}: {str(e)}")
            return False

    async def export_prometheus_metrics(self) -> str:
        """        Export health metrics in Prometheus format
        
        Returns:
            str: Prometheus-formatted metrics
        """        try:
            if self.metrics_collector:
                return await self.metrics_collector.export_prometheus_metrics()
            else:
                return "# Metrics collection is disabled\n"
        except Exception as e:
            self.logger.error(f"Failed to export Prometheus metrics: {str(e)}")
            return f"# Error exporting metrics: {str(e)}\n"

    async def _cleanup_resources(self):
        """Clean up health monitoring resources"""        try:
            # Cleanup database connections
            if self.database_checker:
                await self.database_checker.cleanup_connections()
            
            # Cleanup alerting system
            if self.alerting_system:
                await self.alerting_system.cleanup_resources()
            
            # Cleanup comprehensive checker
            if self.comprehensive_checker:
                await self.comprehensive_checker.cleanup_resources()
            
            self.logger.info("Health monitoring resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up health monitoring resources: {str(e)}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get health monitoring system status"""        return {
            "monitoring_active": self._is_running,
            "monitoring_config": asdict(self.monitoring_config),
            "components_initialized": {
                "core_checker": self.core_checker is not None,
                "database_checker": self.database_checker is not None,
                "ml_checker": self.ml_checker is not None,
                "protection_checker": self.protection_checker is not None,
                "monetization_checker": self.monetization_checker is not None,
                "external_api_checker": self.external_api_checker is not None,
                "infrastructure_checker": self.infrastructure_checker is not None,
                "comprehensive_checker": self.comprehensive_checker is not None,
                "metrics_collector": self.metrics_collector is not None,
                "alerting_system": self.alerting_system is not None
            },
            "last_comprehensive_check": (
                self._last_comprehensive_check.last_check_timestamp 
                if self._last_comprehensive_check else None
            ),
            "module_version": __version__,
            "timestamp": datetime.utcnow().isoformat()
        }


# Convenience functions for direct module usage
def create_health_monitor(config: Dict[str, Any], app=None, redis_client=None) -> HealthMonitoringOrchestrator:
    """    Create health monitoring orchestrator with configuration
    
    Args:
        config: Platform configuration
        app: FastAPI application instance (optional)
        redis_client: Redis client (optional)
        
    Returns:
        HealthMonitoringOrchestrator: Configured health monitor
    """    return HealthMonitoringOrchestrator(config, app, redis_client)


async def quick_health_check(config: Dict[str, Any], app=None) -> Dict[str, Any]:
    """    Perform quick health check without full monitoring setup
    
    Args:
        config: Platform configuration
        app: FastAPI application instance (optional)
        
    Returns:
        Dict[str, Any]: Quick health check results
    """    try:
        checker = ComprehensiveHealthChecker(config, app)
        return await checker.check_service_readiness()
    except Exception as e:
        logger.error(f"Quick health check failed: {str(e)}")
        return {
            "readiness_status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def comprehensive_health_check(config: Dict[str, Any], app=None) -> Dict[str, Any]:
    """    Perform comprehensive health check without full monitoring setup
    
    Args:
        config: Platform configuration
        app: FastAPI application instance (optional)
        
    Returns:
        Dict[str, Any]: Comprehensive health check results
    """    try:
        checker = ComprehensiveHealthChecker(config, app)
        summary = await checker.perform_comprehensive_health_check()
        return asdict(summary)
    except Exception as e:
        logger.error(f"Comprehensive health check failed: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Module exports
__all__ = [
    # Main orchestrator
    "HealthMonitoringOrchestrator",
    "HealthMonitoringConfig",
    
    # Individual health checkers
    "CoreHealthChecker",
    "DatabaseHealthChecker", 
    "MLServiceHealthChecker",
    "ProtectionServiceHealthChecker",
    "MonetizationHealthChecker",
    "ExternalAPIHealthChecker",
    "InfrastructureHealthChecker",
    "ComprehensiveHealthChecker",
    
    # Support systems
    "HealthMetricsCollector",
    "HealthAlertingSystem",
    
    # Data structures
    "HealthStatus",
    "HealthCheckResult",
    "PlatformHealthSummary",
    
    # Convenience functions
    "create_health_monitor",
    "quick_health_check",
    "comprehensive_health_check",
    
    # Module metadata
    "__version__",
    "__author__",
    "__email__"
]


"""Professional Health Monitoring System Implementation Notes:

This index module serves as the central orchestrator for the IA Influencer Agent
health monitoring system, providing:

1. Unified Health Monitoring:
   - Single entry point for all health checks
   - Coordinated execution across subsystems
   - Consistent health status reporting

2. Enterprise Features:
   - Continuous monitoring with configurable intervals
   - Real-time alerting and notification
   - Comprehensive metrics collection and analysis
   - Health trend analysis and prediction

3. Production-Ready Capabilities:
   - Robust error handling and recovery
   - Resource cleanup and management
   - Configurable monitoring intervals
   - Professional logging and diagnostics

4. Integration Support:
   - FastAPI application integration
   - Redis-based distributed state
   - Prometheus metrics export
   - REST API endpoints ready

5. Platform Coverage:
   - Core application health
   - Database systems health
   - ML/AI services health  
   - Content protection health
   - Monetization systems health
   - External API integrations health
   - Infrastructure components health

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
      Microservices + Audio + DevOps + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. All Rights Reserved.
"""