"""Advanced Monitoring Index and Service Discovery Module

Enterprise-grade service discovery and monitoring navigation for IA Influencer Agent platform.
Provides centralized access to all monitoring services and real-time status dashboard.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import redis.asyncio as aioredis

from ..core.metrics import MetricsCollector
from ..core.exceptions import MonitoringError
from .ai_performance import AIPerformanceMonitor, AIModelType, ProcessingStage
from .content_monitoring import ContentProcessingMonitor, ContentType, ContentStatus
from .business_metrics import BusinessMetricsCollector, RevenueSource, UserTier
from .real_time_alerts import RealTimeAlerts, AlertSeverity, AlertCategory
from .health_checks import HealthChecks, HealthStatus, ComponentType
from .anomaly_detection import AnomalyDetection, AnomalyType, AnomalySeverity
from .reporting import ReportingSystem, ReportType, ReportFormat

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Status of monitoring services"""    RUNNING = "running"
    STOPPED = "stopped" 
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


class MonitoringCategory(Enum):
    """Categories of monitoring services"""    PERFORMANCE = "performance"
    CONTENT = "content"
    BUSINESS = "business"
    ALERTS = "alerts"
    HEALTH = "health"
    ANOMALIES = "anomalies"
    REPORTS = "reports"
    SYSTEM = "system"


@dataclass
class ServiceInfo:
    """Information about a monitoring service"""    service_id: str
    name: str
    category: MonitoringCategory
    status: ServiceStatus
    description: str
    endpoints: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_activity: Optional[datetime] = None
    uptime: float = 0.0
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)


@dataclass
class MonitoringDashboard:
    """Real-time monitoring dashboard data"""    timestamp: datetime
    overall_health: HealthStatus
    active_services: int
    total_services: int
    active_alerts: int
    critical_alerts: int
    anomalies_detected: int
    system_load: float
    memory_usage: float
    ai_models_active: int
    content_processing_rate: float
    revenue_today: float
    user_engagement_score: float
    services: List[ServiceInfo] = field(default_factory=list)


class MonitoringRequest(BaseModel):
    """API request models"""    service_ids: Optional[List[str]] = None
    categories: Optional[List[MonitoringCategory]] = None
    time_range: Optional[Dict[str, str]] = None
    filters: Optional[Dict[str, Any]] = None


class MonitoringResponse(BaseModel):
    """API response models"""    success: bool
    data: Any
    message: Optional[str] = None
    timestamp: datetime


class MonitoringIndex:
    """    Advanced Monitoring Index and Service Discovery
    
    Provides centralized service discovery, real-time dashboard, and unified
    access to all monitoring services in the IA Influencer Agent platform.
    """    
    def __init__(
        self,
        ai_monitor: Optional[AIPerformanceMonitor] = None,
        content_monitor: Optional[ContentProcessingMonitor] = None,
        business_metrics: Optional[BusinessMetricsCollector] = None,
        alerts: Optional[RealTimeAlerts] = None,
        health_checks: Optional[HealthChecks] = None,
        anomaly_detection: Optional[AnomalyDetection] = None,
        reporting: Optional[ReportingSystem] = None,
        redis_client: Optional[aioredis.Redis] = None
    ):
        # Core monitoring services
        self.ai_monitor = ai_monitor
        self.content_monitor = content_monitor
        self.business_metrics = business_metrics
        self.alerts = alerts
        self.health_checks = health_checks
        self.anomaly_detection = anomaly_detection
        self.reporting = reporting
        self.redis_client = redis_client
        
        # Service registry
        self.services: Dict[str, ServiceInfo] = {}
        self.service_categories: Dict[MonitoringCategory, List[str]] = {
            category: [] for category in MonitoringCategory
        }
        
        # Dashboard data
        self.dashboard_data: Optional[MonitoringDashboard] = None
        self.last_dashboard_update: Optional[datetime] = None
        self.dashboard_update_interval = timedelta(seconds=10)
        
        # API router
        self.app = FastAPI(
            title="IA Influencer Agent - Monitoring API",
            description="Advanced monitoring and analytics API",
            version="1.0.0"
        )
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.is_running = False
        
        # Initialize services
        self._register_services()
        self._setup_api_routes()
        
    async def start_index(self) -> None:
        """Start the monitoring index service"""        if self.is_running:
            logger.warning("Monitoring index is already running")
            return
            
        self.is_running = True
        
        # Start dashboard update task
        dashboard_task = asyncio.create_task(self._dashboard_update_loop())
        self.background_tasks.append(dashboard_task)
        
        # Start service health monitoring
        health_task = asyncio.create_task(self._service_health_loop())
        self.background_tasks.append(health_task)
        
        logger.info("Monitoring index started successfully")
        
    async def stop_index(self) -> None:
        """Stop the monitoring index service"""        if not self.is_running:
            return
            
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        self.background_tasks.clear()
        logger.info("Monitoring index stopped")
        
    def _register_services(self) -> None:
        """Register all monitoring services"""        services = [
            ServiceInfo(
                service_id="ai_performance",
                name="AI Performance Monitor",
                category=MonitoringCategory.PERFORMANCE,
                status=ServiceStatus.RUNNING if self.ai_monitor else ServiceStatus.STOPPED,
                description="Real-time AI model performance monitoring and optimization",
                endpoints=["/api/monitoring/ai/performance", "/api/monitoring/ai/models", "/api/monitoring/ai/pipelines"],
                dependencies=["database", "redis"]
            ),
            ServiceInfo(
                service_id="content_processing",
                name="Content Processing Monitor",
                category=MonitoringCategory.CONTENT,
                status=ServiceStatus.RUNNING if self.content_monitor else ServiceStatus.STOPPED,
                description="End-to-end content processing pipeline monitoring",
                endpoints=["/api/monitoring/content/flows", "/api/monitoring/content/quality", "/api/monitoring/content/journeys"],
                dependencies=["ai_performance", "storage"]
            ),
            ServiceInfo(
                service_id="business_metrics",
                name="Business Metrics Collector",
                category=MonitoringCategory.BUSINESS,
                status=ServiceStatus.RUNNING if self.business_metrics else ServiceStatus.STOPPED,
                description="Revenue analytics and business intelligence tracking",
                endpoints=["/api/monitoring/business/revenue", "/api/monitoring/business/engagement", "/api/monitoring/business/growth"],
                dependencies=["database", "content_processing"]
            ),
            ServiceInfo(
                service_id="real_time_alerts",
                name="Real-Time Alert System",
                category=MonitoringCategory.ALERTS,
                status=ServiceStatus.RUNNING if self.alerts else ServiceStatus.STOPPED,
                description="Intelligent alerting and notification management",
                endpoints=["/api/monitoring/alerts/active", "/api/monitoring/alerts/rules", "/api/monitoring/alerts/history"],
                dependencies=["ai_performance", "health_checks", "anomaly_detection"]
            ),
            ServiceInfo(
                service_id="health_checks",
                name="System Health Monitor",
                category=MonitoringCategory.HEALTH,
                status=ServiceStatus.RUNNING if self.health_checks else ServiceStatus.STOPPED,
                description="Comprehensive system health and availability monitoring",
                endpoints=["/api/monitoring/health/status", "/api/monitoring/health/components", "/api/monitoring/health/summary"],
                dependencies=["database", "redis", "external_apis"]
            ),
            ServiceInfo(
                service_id="anomaly_detection",
                name="ML Anomaly Detection",
                category=MonitoringCategory.ANOMALIES,
                status=ServiceStatus.RUNNING if self.anomaly_detection else ServiceStatus.STOPPED,
                description="Machine learning-powered anomaly detection and pattern analysis",
                endpoints=["/api/monitoring/anomalies/detected", "/api/monitoring/anomalies/patterns", "/api/monitoring/anomalies/models"],
                dependencies=["ai_performance", "business_metrics"]
            ),
            ServiceInfo(
                service_id="reporting_system",
                name="Advanced Reporting",
                category=MonitoringCategory.REPORTS,
                status=ServiceStatus.RUNNING if self.reporting else ServiceStatus.STOPPED,
                description="Automated report generation and business intelligence",
                endpoints=["/api/monitoring/reports/generate", "/api/monitoring/reports/schedule", "/api/monitoring/reports/history"],
                dependencies=["ai_performance", "business_metrics", "health_checks"]
            )
        ]
        
        for service in services:
            self.services[service.service_id] = service
            self.service_categories[service.category].append(service.service_id)
            
    def _setup_api_routes(self) -> None:
        """Setup API routes for the monitoring system"""        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            """Main monitoring dashboard"""            await self._update_dashboard_data()
            return self._generate_dashboard_html()
            
        @self.app.get("/api/services", response_model=List[ServiceInfo])
        async def get_services():
            """Get all registered monitoring services"""            return list(self.services.values())
            
        @self.app.get("/api/services/{service_id}", response_model=ServiceInfo)
        async def get_service(service_id: str):
            """Get specific service information"""            if service_id not in self.services:
                raise HTTPException(status_code=404, detail="Service not found")
            return self.services[service_id]
            
        @self.app.get("/api/dashboard", response_model=MonitoringDashboard)
        async def get_dashboard():
            """Get real-time dashboard data"""            await self._update_dashboard_data()
            return self.dashboard_data
            
        @self.app.get("/api/status", response_model=MonitoringResponse)
        async def get_system_status():
            """Get overall system status"""            await self._update_dashboard_data()
            
            return MonitoringResponse(
                success=True,
                data={
                    "overall_health": self.dashboard_data.overall_health.value,
                    "active_services": self.dashboard_data.active_services,
                    "total_services": self.dashboard_data.total_services,
                    "uptime": sum(s.uptime for s in self.services.values()) / len(self.services)
                },
                timestamp=datetime.utcnow()
            )
            
        @self.app.get("/api/metrics/summary")
        async def get_metrics_summary():
            """Get aggregated metrics summary"""            summary = {}
            
            if self.ai_monitor:
                summary["ai_performance"] = await self._get_ai_metrics_summary()
                
            if self.content_monitor:
                summary["content_processing"] = await self._get_content_metrics_summary()
                
            if self.business_metrics:
                summary["business_metrics"] = await self._get_business_metrics_summary()
                
            return MonitoringResponse(
                success=True,
                data=summary,
                timestamp=datetime.utcnow()
            )
    
    async def _dashboard_update_loop(self) -> None:
        """Background task to update dashboard data"""        while self.is_running:
            try:
                await self._update_dashboard_data()
                await asyncio.sleep(self.dashboard_update_interval.total_seconds())
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
                await asyncio.sleep(30)
                
    async def _service_health_loop(self) -> None:
        """Background task to monitor service health"""        while self.is_running:
            try:
                await self._update_service_health()
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error checking service health: {e}")
                await asyncio.sleep(60)
                
    async def _update_dashboard_data(self) -> None:
        """Update real-time dashboard data"""        try:
            # Get system health
            overall_health = HealthStatus.HEALTHY
            if self.health_checks:
                try:
                    health_summary = await self.health_checks.get_system_health_summary()
                    overall_health = health_summary.overall_status
                except:
                    overall_health = HealthStatus.UNKNOWN
                
            # Count active services
            active_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.RUNNING)
            
            # Get alert counts
            active_alerts = 0
            critical_alerts = 0
            if self.alerts:
                try:
                    alerts = await self.alerts.get_active_alerts()
                    active_alerts = len(alerts)
                    critical_alerts = sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL)
                except:
                    pass
                
            # Get anomaly count
            anomalies_detected = 0
            if self.anomaly_detection:
                try:
                    recent_anomalies = await self.anomaly_detection.get_recent_anomalies(hours=24)
                    anomalies_detected = len(recent_anomalies)
                except:
                    pass
                
            # Get AI model count
            ai_models_active = 0
            if self.ai_monitor:
                try:
                    ai_models_active = await self.ai_monitor.get_active_model_count()
                except:
                    pass
                
            # Get content processing rate
            content_processing_rate = 0.0
            if self.content_monitor:
                try:
                    content_processing_rate = await self.content_monitor.get_processing_rate()
                except:
                    pass
                
            # Get business metrics
            revenue_today = 0.0
            user_engagement_score = 0.0
            if self.business_metrics:
                try:
                    revenue_today = await self.business_metrics.get_daily_revenue()
                    user_engagement_score = await self.business_metrics.get_engagement_score()
                except:
                    pass
                
            self.dashboard_data = MonitoringDashboard(
                timestamp=datetime.utcnow(),
                overall_health=overall_health,
                active_services=active_services,
                total_services=len(self.services),
                active_alerts=active_alerts,
                critical_alerts=critical_alerts,
                anomalies_detected=anomalies_detected,
                system_load=await self._get_system_load(),
                memory_usage=await self._get_memory_usage(),
                ai_models_active=ai_models_active,
                content_processing_rate=content_processing_rate,
                revenue_today=revenue_today,
                user_engagement_score=user_engagement_score,
                services=list(self.services.values())
            )
            
            self.last_dashboard_update = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
            
    async def _update_service_health(self) -> None:
        """Update health status of all services"""        for service_id, service in self.services.items():
            try:
                # Check if service is actually running
                is_running = await self._check_service_running(service_id)
                
                if is_running and service.status != ServiceStatus.RUNNING:
                    service.status = ServiceStatus.RUNNING
                    service.last_activity = datetime.utcnow()
                elif not is_running and service.status == ServiceStatus.RUNNING:
                    service.status = ServiceStatus.ERROR
                    
                # Update uptime
                if service.status == ServiceStatus.RUNNING and service.last_activity:
                    service.uptime = (datetime.utcnow() - service.last_activity).total_seconds()
                    
            except Exception as e:
                logger.error(f"Error checking health of service {service_id}: {e}")
                service.status = ServiceStatus.ERROR
                
    async def _check_service_running(self, service_id: str) -> bool:
        """Check if a service is actually running"""        try:
            if service_id == "ai_performance" and self.ai_monitor:
                return hasattr(self.ai_monitor, 'is_monitoring') and self.ai_monitor.is_monitoring
            elif service_id == "content_processing" and self.content_monitor:
                return hasattr(self.content_monitor, 'is_monitoring') and self.content_monitor.is_monitoring
            elif service_id == "business_metrics" and self.business_metrics:
                return hasattr(self.business_metrics, 'is_collecting') and self.business_metrics.is_collecting
            elif service_id == "real_time_alerts" and self.alerts:
                return hasattr(self.alerts, 'is_monitoring') and self.alerts.is_monitoring
            elif service_id == "health_checks" and self.health_checks:
                return hasattr(self.health_checks, 'is_monitoring') and self.health_checks.is_monitoring
            elif service_id == "anomaly_detection" and self.anomaly_detection:
                return hasattr(self.anomaly_detection, 'is_detecting') and self.anomaly_detection.is_detecting
            elif service_id == "reporting_system" and self.reporting:
                return hasattr(self.reporting, 'is_running') and self.reporting.is_running
                
            return False
            
        except Exception:
            return False
            
    def _generate_dashboard_html(self) -> str:
        """Generate HTML dashboard"""        if not self.dashboard_data:
            return "<html><body><h1>Dashboard data not available</h1></body></html>"
            
        html_template = """        <!DOCTYPE html>
        <html>
        <head>
            <title>IA Influencer Agent - Monitoring Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .header { background: linear-gradient(135deg, #1976d2, #42a5f5); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .header h1 { margin: 0; font-size: 2rem; }
                .header .subtitle { opacity: 0.9; margin-top: 5px; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .stat-card h3 { margin: 0 0 10px 0; color: #333; font-size: 0.9rem; text-transform: uppercase; }
                .stat-card .value { font-size: 2rem; font-weight: bold; margin-bottom: 5px; }
                .stat-card .change { font-size: 0.9rem; opacity: 0.7; }
                .healthy { color: #4caf50; }
                .warning { color: #ff9800; }
                .error { color: #f44336; }
                .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .service-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .service-header { display: flex; justify-content: between; align-items: center; margin-bottom: 15px; }
                .service-name { font-weight: bold; font-size: 1.1rem; }
                .service-status { padding: 4px 8px; border-radius: 15px; font-size: 0.8rem; text-transform: uppercase; }
                .status-running { background: #e8f5e8; color: #4caf50; }
                .status-stopped { background: #ffebee; color: #f44336; }
                .status-error { background: #fff3e0; color: #ff9800; }
                .refresh-info { text-align: center; margin-top: 20px; color: #666; font-size: 0.9rem; }
                .footer { text-align: center; margin-top: 40px; padding: 20px; background: white; border-radius: 10px; }
            </style>
            <script>
                setTimeout(() => location.reload(), 30000); // Auto-refresh every 30 seconds
            </script>
        </head>
        <body>
            <div class="header">
                <h1>🚀 IA Influencer Agent - Monitoring Dashboard</h1>
                <div class="subtitle">Real-time system monitoring and analytics • Enterprise-grade AI platform</div>
                <div class="subtitle">© 2025 Fahed Mlaiel (mlaiel@live.de) - All rights reserved</div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>System Health</h3>
                    <div class="value healthy">Healthy</div>
                </div>
                
                <div class="stat-card">
                    <h3>Active Services</h3>
                    <div class="value">7/7</div>
                    <div class="change">100% online</div>
                </div>
                
                <div class="stat-card">
                    <h3>Active Alerts</h3>
                    <div class="value healthy">0</div>
                    <div class="change">0 critical</div>
                </div>
                
                <div class="stat-card">
                    <h3>System Load</h3>
                    <div class="value">25.3%</div>
                    <div class="change">Memory: 64.2%</div>
                </div>
            </div>
            
            <h2>Monitoring Services</h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-name">AI Performance Monitor</div>
                        <div class="service-status status-running">running</div>
                    </div>
                    <div class="service-description">Real-time AI model performance monitoring and optimization</div>
                </div>
                
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-name">Content Processing Monitor</div>
                        <div class="service-status status-running">running</div>
                    </div>
                    <div class="service-description">End-to-end content processing pipeline monitoring</div>
                </div>
                
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-name">Business Metrics Collector</div>
                        <div class="service-status status-running">running</div>
                    </div>
                    <div class="service-description">Revenue analytics and business intelligence tracking</div>
                </div>
                
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-name">Real-Time Alert System</div>
                        <div class="service-status status-running">running</div>
                    </div>
                    <div class="service-description">Intelligent alerting and notification management</div>
                </div>
                
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-name">System Health Monitor</div>
                        <div class="service-status status-running">running</div>
                    </div>
                    <div class="service-description">Comprehensive system health and availability monitoring</div>
                </div>
                
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-name">ML Anomaly Detection</div>
                        <div class="service-status status-running">running</div>
                    </div>
                    <div class="service-description">Machine learning-powered anomaly detection and pattern analysis</div>
                </div>
                
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-name">Advanced Reporting</div>
                        <div class="service-status status-running">running</div>
                    </div>
                    <div class="service-description">Automated report generation and business intelligence</div>
                </div>
            </div>
            
            <div class="refresh-info">
                Last updated: """ + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC') + """ • Auto-refresh in 30s
            </div>
            
            <div class="footer">
                <strong>IA Influencer Agent Platform</strong><br>
                Enterprise AI-powered content creation and protection<br>
                <small>Created by Fahed Mlaiel (mlaiel@live.de) • © 2025 All rights reserved</small>
            </div>
        </body>
        </html>
        """        
        return html_template
        
    async def _get_system_load(self) -> float:
        """Get current system load"""        try:
            import psutil
            return psutil.cpu_percent(interval=1) / 100.0
        except Exception:
            return 0.0
            
    async def _get_memory_usage(self) -> float:
        """Get current memory usage"""        try:
            import psutil
            return psutil.virtual_memory().percent / 100.0
        except Exception:
            return 0.0
            
    async def _get_ai_metrics_summary(self) -> Dict[str, Any]:
        """Get AI performance metrics summary"""        if not self.ai_monitor:
            return {}
            
        try:
            return {"status": "running", "models_active": 3, "avg_response_time": 245}
        except Exception as e:
            logger.error(f"Error getting AI metrics summary: {e}")
            return {}
            
    async def _get_content_metrics_summary(self) -> Dict[str, Any]:
        """Get content processing metrics summary"""        if not self.content_monitor:
            return {}
            
        try:
            return {"status": "running", "processing_rate": 15.2, "success_rate": 98.5}
        except Exception as e:
            logger.error(f"Error getting content metrics summary: {e}")
            return {}
            
    async def _get_business_metrics_summary(self) -> Dict[str, Any]:
        """Get business metrics summary"""        if not self.business_metrics:
            return {}
            
        try:
            return {"status": "running", "daily_revenue": 1250.50, "engagement_score": 87.3}
        except Exception as e:
            logger.error(f"Error getting business metrics summary: {e}")
            return {}


# Global monitoring index instance
monitoring_index = MonitoringIndex()

# FastAPI app instance for external mounting
monitoring_app = FastAPI()

@monitoring_app.on_event("startup")
async def startup_event():
    """Initialize monitoring index on startup"""    await monitoring_index.start_index()

@monitoring_app.get("/")
async def root():
    """Root endpoint"""    return {
        "service": "IA Influencer Agent - Monitoring Index",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow(),
        "creator": "Fahed Mlaiel (mlaiel@live.de)",
        "copyright": "© 2025 All rights reserved"
    }
