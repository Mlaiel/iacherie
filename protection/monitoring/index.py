"""🔍 Content Protection Monitoring Index
=====================================

Main entry point and service orchestrator for the comprehensive content protection monitoring system.
Provides centralized access to all monitoring capabilities including real-time surveillance,
analytics, performance optimization, dashboard, and automated reporting.

Industrial Features:
- Unified API for all monitoring operations
- Enterprise-grade service orchestration
- Advanced configuration management
- Comprehensive error handling and logging
- Production-ready scalability and reliability

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.
Contact mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from enum import Enum

# FastAPI imports
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Core monitoring imports
from .realtime_monitor import RealTimeMonitor, MonitoringPriority, MonitoringMode
from .analytics import MonitoringAnalytics, AnalyticsTimeRange
from .performance_optimizer import PerformanceOptimizer, ResourceType
from .dashboard import DashboardController, DashboardLayout, TimeRange
from .reports import ReportGenerator, ReportFormat, ReportType, ReportFrequency
from .models import MonitoringSession, ViolationDetection, MonitoringAlert

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

class MonitoringIndexStatus(str, Enum):
    """Status of the monitoring index service."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class ServiceHealth(str, Enum):
    """Health status for individual services."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ServiceStatus:
    """Status information for a monitoring service."""
    name: str
    health: ServiceHealth
    uptime_seconds: float
    last_check: datetime
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None

class MonitoringRequest(BaseModel):
    """Request model for starting monitoring."""
    fingerprint_id: str
    user_id: int
    platforms: List[str]
    priority: str = "medium"
    custom_config: Optional[Dict[str, Any]] = None

class ReportRequest(BaseModel):
    """Request model for generating reports."""
    template_id: Optional[str] = None
    report_type: str = "detailed_analytics"
    time_range: str = "last_7_days"
    output_formats: List[str] = Field(default_factory=lambda: ["pdf", "json"])
    user_id: int
    custom_parameters: Optional[Dict[str, Any]] = None

class DashboardRequest(BaseModel):
    """Request model for dashboard operations."""
    user_id: int
    layout_type: Optional[str] = None
    widgets: Optional[List[Dict[str, Any]]] = None

class PerformanceOptimizationRequest(BaseModel):
    """Request model for performance optimization."""
    optimization_type: str = "auto"
    target_resources: Optional[List[str]] = None
    aggressive_mode: bool = False

class MonitoringIndex:
    """
    Central index and orchestrator for the complete monitoring system.
    
    This class provides a unified interface to all monitoring capabilities:
    - Real-time content monitoring and violation detection
    - Advanced analytics with ML-powered insights
    - Performance optimization and system tuning
    - Interactive dashboard with real-time streaming
    - Automated report generation and scheduling
    
    Features:
    - Enterprise-grade service orchestration
    - Comprehensive API for external integration
    - Advanced configuration and health monitoring
    - Production-ready error handling and logging
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the monitoring index.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._load_default_config()
        self.status = MonitoringIndexStatus.INITIALIZING
        self.start_time = datetime.utcnow()
        
        # Service instances
        self.realtime_monitor: Optional[RealTimeMonitor] = None
        self.analytics: Optional[MonitoringAnalytics] = None
        self.performance_optimizer: Optional[PerformanceOptimizer] = None
        self.dashboard: Optional[DashboardController] = None
        self.report_generator: Optional[ReportGenerator] = None
        
        # Service health tracking
        self.service_health: Dict[str, ServiceStatus] = {}
        
        # API app
        self.app: Optional[FastAPI] = None
        
        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("Monitoring Index initialized")

    async def initialize(self) -> bool:
        """
        Initialize all monitoring services and the API.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Content Protection Monitoring Index...")
            
            # Initialize core services
            await self._initialize_services()
            
            # Initialize FastAPI application
            await self._initialize_api()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.status = MonitoringIndexStatus.RUNNING
            logger.info("Monitoring Index initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Monitoring Index: {e}")
            self.status = MonitoringIndexStatus.ERROR
            return False

    async def _initialize_services(self) -> None:
        """Initialize all monitoring services."""
        try:
            # Initialize Analytics first (required by other services)
            logger.info("Initializing Analytics service...")
            self.analytics = MonitoringAnalytics(
                config=self.config.get('analytics', {}),
                redis_client=self.config.get('redis_client'),
                db_session=self.config.get('db_session')
            )
            await self.analytics.initialize()
            self._update_service_health('analytics', ServiceHealth.HEALTHY)
            
            # Initialize Performance Optimizer
            logger.info("Initializing Performance Optimizer...")
            self.performance_optimizer = PerformanceOptimizer(
                config=self.config.get('performance', {}),
                redis_client=self.config.get('redis_client'),
                db_session=self.config.get('db_session')
            )
            await self.performance_optimizer.initialize()
            self._update_service_health('performance_optimizer', ServiceHealth.HEALTHY)
            
            # Initialize Real-time Monitor
            logger.info("Initializing Real-time Monitor...")
            self.realtime_monitor = RealTimeMonitor(
                config=self.config.get('realtime_monitor', {}),
                redis_client=self.config.get('redis_client'),
                db_session=self.config.get('db_session')
            )
            await self.realtime_monitor.initialize()
            self._update_service_health('realtime_monitor', ServiceHealth.HEALTHY)
            
            # Initialize Dashboard Controller
            logger.info("Initializing Dashboard Controller...")
            self.dashboard = DashboardController(
                self.realtime_monitor,
                self.analytics,
                self.performance_optimizer
            )
            await self.dashboard.initialize()
            self._update_service_health('dashboard', ServiceHealth.HEALTHY)
            
            # Initialize Report Generator
            logger.info("Initializing Report Generator...")
            self.report_generator = ReportGenerator(
                config=self.config.get('reports', {}),
                analytics=self.analytics,
                performance_optimizer=self.performance_optimizer
            )
            await self.report_generator.initialize()
            self._update_service_health('report_generator', ServiceHealth.HEALTHY)
            
            logger.info("All monitoring services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    async def _initialize_api(self) -> None:
        """Initialize FastAPI application with all routes."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """FastAPI lifespan manager."""
            # Startup
            logger.info("Starting Monitoring API...")
            yield
            # Shutdown
            logger.info("Shutting down Monitoring API...")
            await self.shutdown()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="IA-Influencer Content Protection Monitoring API",
            description="Advanced monitoring system for content protection with real-time analytics",
            version="3.0.0",
            lifespan=lifespan
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get('cors_origins', ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_api_routes()
        
        logger.info("FastAPI application initialized")

    def _setup_api_routes(self) -> None:
        """Setup all API routes."""
        
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            """Get system health status."""
            return await self.get_system_health()
        
        # Service status endpoint
        @self.app.get("/status")
        async def system_status():
            """Get detailed system status."""
            return await self.get_system_status()
        
        # Start monitoring endpoint
        @self.app.post("/monitoring/start")
        async def start_monitoring(
            request: MonitoringRequest,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Start content monitoring for a fingerprint."""
            try:
                session_id = await self.start_content_monitoring(
                    fingerprint_id=request.fingerprint_id,
                    user_id=request.user_id,
                    platforms=request.platforms,
                    priority=request.priority,
                    custom_config=request.custom_config
                )
                return {"session_id": session_id, "status": "started"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Stop monitoring endpoint
        @self.app.post("/monitoring/stop/{session_id}")
        async def stop_monitoring(
            session_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Stop monitoring for a session."""
            try:
                success = await self.stop_content_monitoring(session_id)
                return {"session_id": session_id, "status": "stopped" if success else "failed"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Get monitoring sessions
        @self.app.get("/monitoring/sessions/{user_id}")
        async def get_monitoring_sessions(
            user_id: int,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get active monitoring sessions for a user."""
            try:
                sessions = await self.get_active_monitoring_sessions(user_id)
                return {"user_id": user_id, "sessions": sessions}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Dashboard data endpoint
        @self.app.get("/dashboard/{user_id}")
        async def get_dashboard_data(
            user_id: int,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get dashboard data for a user."""
            try:
                data = await self.get_dashboard_data(user_id)
                return data
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Generate report endpoint
        @self.app.post("/reports/generate")
        async def generate_report(
            request: ReportRequest,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Generate a monitoring report."""
            try:
                report = await self.generate_report(
                    template_id=request.template_id,
                    report_type=request.report_type,
                    time_range=request.time_range,
                    output_formats=request.output_formats,
                    user_id=request.user_id,
                    custom_parameters=request.custom_parameters
                )
                return report
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Download report endpoint
        @self.app.get("/reports/download/{report_id}/{format}")
        async def download_report(
            report_id: str,
            format: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Download a generated report."""
            try:
                file_path = await self.download_report(report_id, format)
                if file_path and file_path.exists():
                    return FileResponse(
                        path=str(file_path),
                        filename=f"{report_id}.{format}",
                        media_type='application/octet-stream'
                    )
                else:
                    raise HTTPException(status_code=404, detail="Report not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Performance optimization endpoint
        @self.app.post("/performance/optimize")
        async def optimize_performance(
            request: PerformanceOptimizationRequest,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Run system performance optimization."""
            try:
                result = await self.optimize_system_performance(
                    optimization_type=request.optimization_type,
                    target_resources=request.target_resources,
                    aggressive_mode=request.aggressive_mode
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Analytics endpoint
        @self.app.get("/analytics/{user_id}")
        async def get_analytics(
            user_id: int,
            time_range: str = "last_7_days",
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get analytics data for a user."""
            try:
                analytics_data = await self.get_analytics_data(user_id, time_range)
                return analytics_data
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # WebSocket endpoint for real-time updates
        @self.app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: int):
            """WebSocket endpoint for real-time monitoring updates."""
            try:
                await self.handle_websocket_connection(websocket, user_id)
            except Exception as e:
                logger.error(f"WebSocket error for user {user_id}: {e}")

    async def start_content_monitoring(
        self,
        fingerprint_id: str,
        user_id: int,
        platforms: List[str],
        priority: str = "medium",
        custom_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start monitoring for a content fingerprint.
        
        Args:
            fingerprint_id: Content fingerprint to monitor
            user_id: User ID owning the content
            platforms: List of platforms to monitor
            priority: Monitoring priority level
            custom_config: Optional custom configuration
            
        Returns:
            str: Monitoring session ID
        """
        if not self.realtime_monitor:
            raise RuntimeError("Real-time monitor not initialized")
        
        # Convert priority string to enum
        priority_map = {
            "critical": MonitoringPriority.CRITICAL,
            "high": MonitoringPriority.HIGH,
            "medium": MonitoringPriority.MEDIUM,
            "low": MonitoringPriority.LOW
        }
        priority_enum = priority_map.get(priority.lower(), MonitoringPriority.MEDIUM)
        
        session_id = await self.realtime_monitor.start_realtime_monitoring(
            fingerprint_id=fingerprint_id,
            user_id=user_id,
            platforms=platforms,
            priority=priority_enum,
            custom_config=custom_config
        )
        
        logger.info(f"Started monitoring session {session_id} for user {user_id}")
        return session_id

    async def stop_content_monitoring(self, session_id: str) -> bool:
        """
        Stop monitoring for a session.
        
        Args:
            session_id: Monitoring session ID to stop
            
        Returns:
            bool: True if successful
        """
        if not self.realtime_monitor:
            return False
        
        success = await self.realtime_monitor.stop_realtime_monitoring(session_id)
        
        if success:
            logger.info(f"Stopped monitoring session {session_id}")
        
        return success

    async def get_active_monitoring_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get active monitoring sessions for a user.
        
        Args:
            user_id: User ID to get sessions for
            
        Returns:
            List of active monitoring sessions
        """
        if not self.realtime_monitor:
            return []
        
        # Get active sessions from real-time monitor
        sessions = await self.realtime_monitor.get_active_sessions(user_id)
        return [session.dict() for session in sessions]

    async def get_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a user.
        
        Args:
            user_id: User ID to get dashboard data for
            
        Returns:
            Dict containing dashboard metrics and data
        """
        if not self.dashboard:
            return {}
        
        return await self.dashboard.get_dashboard_metrics(user_id)

    async def generate_report(
        self,
        template_id: Optional[str] = None,
        report_type: str = "detailed_analytics",
        time_range: str = "last_7_days",
        output_formats: List[str] = None,
        user_id: int = 0,
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a monitoring report.
        
        Args:
            template_id: Optional template ID
            report_type: Type of report to generate
            time_range: Time range for the report
            output_formats: List of output formats
            user_id: User ID generating the report
            custom_parameters: Optional custom parameters
            
        Returns:
            Dict containing report information
        """
        if not self.report_generator:
            return {}
        
        # Default output formats
        if not output_formats:
            output_formats = [ReportFormat.PDF, ReportFormat.JSON]
        else:
            output_formats = [ReportFormat(fmt.lower()) for fmt in output_formats]
        
        # Use default template if none provided
        if not template_id:
            template_id = f"default_{report_type}"
        
        generated_report = await self.report_generator.generate_report(
            template_id=template_id,
            output_formats=output_formats,
            custom_parameters=custom_parameters
        )
        
        return generated_report.dict()

    async def download_report(self, report_id: str, format_type: str) -> Optional[Path]:
        """
        Get download path for a generated report.
        
        Args:
            report_id: Report ID to download
            format_type: Format type to download
            
        Returns:
            Path to report file or None if not found
        """
        if not self.report_generator:
            return None
        
        return await self.report_generator.download_report(report_id, format_type)

    async def optimize_system_performance(
        self,
        optimization_type: str = "auto",
        target_resources: Optional[List[str]] = None,
        aggressive_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Run system performance optimization.
        
        Args:
            optimization_type: Type of optimization to run
            target_resources: Optional list of resources to target
            aggressive_mode: Whether to use aggressive optimization
            
        Returns:
            Dict containing optimization results
        """
        if not self.performance_optimizer:
            return {}
        
        if optimization_type == "auto":
            return await self.performance_optimizer.auto_optimize_system()
        else:
            # Custom optimization
            return await self.performance_optimizer.optimize_specific_resources(
                resources=target_resources or [],
                aggressive=aggressive_mode
            )

    async def get_analytics_data(
        self, 
        user_id: int, 
        time_range: str = "last_7_days"
    ) -> Dict[str, Any]:
        """
        Get analytics data for a user.
        
        Args:
            user_id: User ID to get analytics for
            time_range: Time range for analytics
            
        Returns:
            Dict containing analytics data
        """
        if not self.analytics:
            return {}
        
        # Convert time range to enum
        time_range_map = {
            "last_hour": AnalyticsTimeRange.LAST_HOUR,
            "last_6_hours": AnalyticsTimeRange.LAST_6_HOURS,
            "last_24_hours": AnalyticsTimeRange.LAST_24_HOURS,
            "last_7_days": AnalyticsTimeRange.LAST_7_DAYS,
            "last_30_days": AnalyticsTimeRange.LAST_30_DAYS,
            "last_90_days": AnalyticsTimeRange.LAST_90_DAYS
        }
        
        analytics_range = time_range_map.get(time_range, AnalyticsTimeRange.LAST_7_DAYS)
        
        # Get comprehensive analytics
        report = await self.analytics.generate_analytics_report(analytics_range, user_id=user_id)
        insights = await self.analytics.generate_insights(user_id=user_id)
        realtime_metrics = await self.analytics.get_realtime_metrics(user_id=user_id)
        
        return {
            "report": report.dict(),
            "insights": [insight.dict() for insight in insights],
            "realtime_metrics": realtime_metrics
        }

    async def handle_websocket_connection(self, websocket: WebSocket, user_id: int):
        """
        Handle WebSocket connection for real-time updates.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID for the connection
        """
        if not self.dashboard:
            await websocket.close(code=1000, reason="Dashboard not available")
            return
        
        # Use dashboard's WebSocket handler
        subscriptions = ["metrics", "alerts", "violations", "performance"]
        await self.dashboard.stream_realtime_data(websocket, user_id, subscriptions)

    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health status.
        
        Returns:
            Dict containing health information
        """
        overall_health = ServiceHealth.HEALTHY
        
        # Check individual service health
        for service_name, service_status in self.service_health.items():
            if service_status.health == ServiceHealth.UNHEALTHY:
                overall_health = ServiceHealth.UNHEALTHY
                break
            elif service_status.health == ServiceHealth.DEGRADED:
                overall_health = ServiceHealth.DEGRADED
        
        return {
            "overall_health": overall_health.value,
            "status": self.status.value,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "services": {
                name: {
                    "health": status.health.value,
                    "uptime_seconds": status.uptime_seconds,
                    "last_check": status.last_check.isoformat(),
                    "error_message": status.error_message
                }
                for name, status in self.service_health.items()
            }
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get detailed system status.
        
        Returns:
            Dict containing comprehensive status information
        """
        status = {
            "version": "3.0.0",
            "author": "Fahed Mlaiel",
            "copyright": "© 2025 Fahed Mlaiel. All rights reserved.",
            "status": self.status.value,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "services": {}
        }
        
        # Add service-specific status
        if self.realtime_monitor:
            realtime_metrics = await self.realtime_monitor.get_realtime_metrics()
            status["services"]["realtime_monitor"] = {
                "initialized": True,
                "metrics": realtime_metrics.dict()
            }
        
        if self.analytics:
            analytics_metrics = await self.analytics.get_realtime_metrics()
            status["services"]["analytics"] = {
                "initialized": True,
                "metrics": analytics_metrics
            }
        
        if self.performance_optimizer:
            performance_metrics = await self.performance_optimizer.monitor_system_performance()
            status["services"]["performance_optimizer"] = {
                "initialized": True,
                "metrics": {
                    resource_type.value: {
                        "usage": metrics.current_usage,
                        "efficiency": metrics.efficiency,
                        "trend": metrics.trend
                    }
                    for resource_type, metrics in performance_metrics.items()
                }
            }
        
        if self.dashboard:
            status["services"]["dashboard"] = {"initialized": True}
        
        if self.report_generator:
            report_stats = await self.report_generator.get_report_statistics()
            status["services"]["report_generator"] = {
                "initialized": True,
                "statistics": report_stats
            }
        
        return status

    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Background tasks started")

    async def _health_check_loop(self) -> None:
        """Background task for health monitoring."""
        try:
            while self.status == MonitoringIndexStatus.RUNNING:
                await self._check_service_health()
                await asyncio.sleep(60)  # Check every minute
        except asyncio.CancelledError:
            logger.debug("Health check loop cancelled")

    async def _cleanup_loop(self) -> None:
        """Background task for cleanup operations."""
        try:
            while self.status == MonitoringIndexStatus.RUNNING:
                await self._perform_cleanup()
                await asyncio.sleep(3600)  # Cleanup every hour
        except asyncio.CancelledError:
            logger.debug("Cleanup loop cancelled")

    async def _check_service_health(self) -> None:
        """Check health of all services."""
        try:
            services = {
                'realtime_monitor': self.realtime_monitor,
                'analytics': self.analytics,
                'performance_optimizer': self.performance_optimizer,
                'dashboard': self.dashboard,
                'report_generator': self.report_generator
            }
            
            for name, service in services.items():
                if service:
                    try:
                        # Basic health check
                        health = ServiceHealth.HEALTHY
                        if hasattr(service, 'health_check'):
                            health_result = await service.health_check()
                            health = ServiceHealth.HEALTHY if health_result else ServiceHealth.DEGRADED
                        
                        self._update_service_health(name, health)
                        
                    except Exception as e:
                        self._update_service_health(name, ServiceHealth.UNHEALTHY, str(e))
                        
        except Exception as e:
            logger.error(f"Health check failed: {e}")

    async def _perform_cleanup(self) -> None:
        """Perform cleanup operations."""
        try:
            # Cleanup old reports
            if self.report_generator:
                await self.report_generator.cleanup_old_reports(days_to_keep=30)
            
            # Additional cleanup operations can be added here
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def _update_service_health(
        self, 
        service_name: str, 
        health: ServiceHealth, 
        error_message: Optional[str] = None
    ) -> None:
        """Update service health status."""
        current_time = datetime.utcnow()
        
        if service_name in self.service_health:
            uptime = (current_time - (current_time - timedelta(seconds=self.service_health[service_name].uptime_seconds))).total_seconds()
        else:
            uptime = (current_time - self.start_time).total_seconds()
        
        self.service_health[service_name] = ServiceStatus(
            name=service_name,
            health=health,
            uptime_seconds=uptime,
            last_check=current_time,
            error_message=error_message
        )

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "cors_origins": ["*"],
            "analytics": {
                "trend_analysis_window_days": 30,
                "anomaly_detection_sensitivity": 0.1,
                "ml_model_retrain_interval_hours": 24
            },
            "performance": {
                "optimization_interval_seconds": 300,
                "metrics_collection_interval_seconds": 60,
                "resource_threshold_warning": 75.0
            },
            "realtime_monitor": {
                "max_concurrent_sessions": 1000,
                "alert_threshold_violations": 5
            },
            "reports": {
                "output_directory": "./reports",
                "cleanup_after_days": 30
            }
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown all services."""
        logger.info("Shutting down Monitoring Index...")
        self.status = MonitoringIndexStatus.STOPPING
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Shutdown services in reverse order
        services = [
            ('report_generator', self.report_generator),
            ('dashboard', self.dashboard),
            ('realtime_monitor', self.realtime_monitor),
            ('performance_optimizer', self.performance_optimizer),
            ('analytics', self.analytics)
        ]
        
        for name, service in services:
            if service and hasattr(service, 'shutdown'):
                try:
                    await service.shutdown()
                    logger.info(f"Shutdown {name}")
                except Exception as e:
                    logger.error(f"Error shutting down {name}: {e}")
        
        self.status = MonitoringIndexStatus.STOPPED
        logger.info("Monitoring Index shutdown complete")

# Global monitoring index instance
monitoring_index: Optional[MonitoringIndex] = None

def get_monitoring_index() -> MonitoringIndex:
    """Get the global monitoring index instance."""
    global monitoring_index
    if monitoring_index is None:
        monitoring_index = MonitoringIndex()
    return monitoring_index

async def initialize_monitoring_system(config: Optional[Dict[str, Any]] = None) -> MonitoringIndex:
    """
    Initialize the complete monitoring system.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        MonitoringIndex: Initialized monitoring index
    """
    global monitoring_index
    monitoring_index = MonitoringIndex(config)
    
    success = await monitoring_index.initialize()
    if not success:
        raise RuntimeError("Failed to initialize monitoring system")
    
    return monitoring_index

async def shutdown_monitoring_system():
    """Shutdown the monitoring system."""
    global monitoring_index
    if monitoring_index:
        await monitoring_index.shutdown()
        monitoring_index = None

# FastAPI app factory
def create_monitoring_app(config: Optional[Dict[str, Any]] = None) -> FastAPI:
    """
    Create and configure the monitoring FastAPI application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        FastAPI: Configured FastAPI application
    """
    index = MonitoringIndex(config)
    
    # Initialize on startup
    async def startup():
        await index.initialize()
    
    # Create app with startup event
    app = FastAPI(
        title="IA-Influencer Content Protection Monitoring",
        description="Advanced monitoring system for content protection",
        version="3.0.0",
        on_startup=[startup]
    )
    
    # Mount monitoring index app
    if index.app:
        app.mount("/", index.app)
    
    return app

# Legal notice and copyright
LEGAL_NOTICE = """⚖️ LEGAL WARNING ⚖️

This software is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).

PROPRIETARY SOFTWARE - ALL RIGHTS RESERVED

This code is protected under German and international copyright law. 
Unauthorized use, copying, distribution, modification, or reverse engineering 
is strictly prohibited and will result in immediate legal action.

For licensing inquiries, contact: mlaiel@live.de

© 2025 Fahed Mlaiel. All rights reserved.
"""# Export main classes and functions
__all__ = [
    "MonitoringIndex",
    "MonitoringIndexStatus",
    "ServiceHealth",
    "ServiceStatus",
    "MonitoringRequest",
    "ReportRequest",
    "DashboardRequest",
    "PerformanceOptimizationRequest",
    "get_monitoring_index",
    "initialize_monitoring_system",
    "shutdown_monitoring_system",
    "create_monitoring_app",
    "LEGAL_NOTICE"
]
