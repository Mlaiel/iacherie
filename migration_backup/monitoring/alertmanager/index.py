#!/usr/bin/env python3
"""
AlertManager Enterprise Orchestrator - Main Entry Point
====================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - All Rights Reserved

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue - AI-Powered Creator Economy Platform
Module: AlertManager Enterprise Orchestrator
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path

# Third-party imports
try:
    import redis
    import prometheus_client
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from pydantic import BaseModel, Field
except ImportError as e:
    logging.error(f"Required dependencies not installed: {e}")
    raise

# Internal imports - will be implemented
from .intelligent_alert_routing_engine import IntelligentAlertRoutingEngine
from .creator_impact_severity_analyzer import CreatorImpactSeverityAnalyzer
from .alert_correlation_intelligence import AlertCorrelationIntelligence
from .notification_channel_orchestrator import NotificationChannelOrchestrator
from .escalation_workflow_manager import EscalationWorkflowManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels for Creator Economy"""
    EMERGENCY = "emergency"      # Platform-wide outage
    CRITICAL = "critical"        # Major Creator impact
    HIGH = "high"               # Creator tier issues
    WARNING = "warning"         # Performance degradation
    INFO = "info"               # Informational alerts
    DEBUG = "debug"             # Debug-level information


class CreatorTier(Enum):
    """Creator tier classification for prioritization"""
    PREMIUM = "premium"         # Top-tier creators (>100K followers)
    PROFESSIONAL = "professional"  # Mid-tier creators (10K-100K)
    EMERGING = "emerging"       # Growing creators (1K-10K)
    STARTER = "starter"         # New creators (<1K)


@dataclass
class AlertContext:
    """Enhanced alert context for Creator Economy"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    source_service: str
    creator_id: Optional[str] = None
    creator_tier: Optional[CreatorTier] = None
    business_impact: float = 0.0  # 0-1 scale
    revenue_impact: float = 0.0   # Estimated revenue impact
    user_count_affected: int = 0
    geographic_scope: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationResult:
    """Result of notification dispatch"""
    channel: str
    success: bool
    delivery_time: datetime
    error_message: Optional[str] = None
    retry_count: int = 0


class AlertManagerOrchestrator:
    """
    Enterprise AlertManager Orchestrator for Creator Economy
    
    Coordinates all alerting components with ML-powered intelligence,
    Creator-specific prioritization, and multi-channel notifications.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AlertManager orchestrator"""
        self.config = self._load_configuration(config_path)
        self.redis_client = self._initialize_redis()
        self.metrics = self._initialize_metrics()
        
        # Initialize core engines
        try:
            self.routing_engine = IntelligentAlertRoutingEngine(self.config)
            self.severity_analyzer = CreatorImpactSeverityAnalyzer(self.config)
            self.correlation_engine = AlertCorrelationIntelligence(self.config)
            self.notification_orchestrator = NotificationChannelOrchestrator(self.config)
            self.escalation_manager = EscalationWorkflowManager(self.config)
            
            logger.info("AlertManager Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AlertManager components: {e}")
            raise
    
    def _load_configuration(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load AlertManager configuration"""
        default_config = {
            "redis": {
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "db": int(os.getenv("REDIS_DB", "0"))
            },
            "alerting": {
                "max_concurrent_alerts": 1000,
                "correlation_window_seconds": 300,
                "escalation_timeout_seconds": 900,
                "creator_tier_sla": {
                    "premium": 60,      # 1 minute SLA
                    "professional": 300,  # 5 minutes SLA
                    "emerging": 900,    # 15 minutes SLA
                    "starter": 1800     # 30 minutes SLA
                }
            },
            "channels": {
                "slack": {
                    "enabled": True,
                    "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                    "channels": {
                        "critical": "#critical-alerts",
                        "high": "#high-priority",
                        "warning": "#monitoring",
                        "info": "#info-alerts"
                    }
                },
                "email": {
                    "enabled": True,
                    "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
                    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                    "sender": os.getenv("ALERT_SENDER_EMAIL", "alerts@ainflue.com")
                },
                "sms": {
                    "enabled": True,
                    "provider": "twilio",
                    "api_key": os.getenv("TWILIO_API_KEY")
                },
                "pagerduty": {
                    "enabled": True,
                    "api_key": os.getenv("PAGERDUTY_API_KEY"),
                    "service_key": os.getenv("PAGERDUTY_SERVICE_KEY")
                }
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                default_config.update(custom_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_redis(self) -> redis.Redis:
        """Initialize Redis connection for state management"""
        try:
            redis_config = self.config["redis"]
            client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            client.ping()
            logger.info("Redis connection established successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            # Return mock client for development
            return None
    
    def _initialize_metrics(self) -> Dict[str, Any]:
        """Initialize Prometheus metrics"""
        return {
            "alerts_total": prometheus_client.Counter(
                "alertmanager_alerts_total",
                "Total number of alerts processed",
                ["severity", "creator_tier", "source_service"]
            ),
            "alert_processing_duration": prometheus_client.Histogram(
                "alertmanager_processing_duration_seconds",
                "Time spent processing alerts",
                ["severity", "creator_tier"]
            ),
            "notification_delivery_duration": prometheus_client.Histogram(
                "alertmanager_notification_delivery_seconds",
                "Time to deliver notifications",
                ["channel", "severity"]
            ),
            "escalation_events": prometheus_client.Counter(
                "alertmanager_escalations_total",
                "Total number of escalation events",
                ["creator_tier", "severity"]
            )
        }
    
    async def process_alert(
        self,
        alert_data: Dict[str, Any],
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Dict[str, Any]:
        """
        Main alert processing pipeline
        
        Args:
            alert_data: Raw alert data from monitoring systems
            background_tasks: FastAPI background tasks for async processing
            
        Returns:
            Processing result with routing decisions and notification status
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Parse and validate alert data
            alert_context = self._parse_alert_data(alert_data)
            
            # Step 2: Analyze Creator impact and determine severity
            enhanced_context = await self.severity_analyzer.analyze_creator_impact(alert_context)
            
            # Step 3: Check for alert correlation
            correlation_result = await self.correlation_engine.correlate_alert(enhanced_context)
            
            # Step 4: Apply intelligent routing
            routing_decision = await self.routing_engine.route_alert(
                enhanced_context, correlation_result
            )
            
            # Step 5: Dispatch notifications
            notification_results = await self.notification_orchestrator.dispatch_notifications(
                enhanced_context, routing_decision
            )
            
            # Step 6: Set up escalation if needed
            if routing_decision.requires_escalation:
                await self.escalation_manager.schedule_escalation(
                    enhanced_context, routing_decision
                )
            
            # Step 7: Store alert state
            await self._store_alert_state(enhanced_context, routing_decision, notification_results)
            
            # Update metrics
            processing_duration = (datetime.now() - start_time).total_seconds()
            self.metrics["alert_processing_duration"].labels(
                severity=enhanced_context.severity.value,
                creator_tier=enhanced_context.creator_tier.value if enhanced_context.creator_tier else "unknown"
            ).observe(processing_duration)
            
            self.metrics["alerts_total"].labels(
                severity=enhanced_context.severity.value,
                creator_tier=enhanced_context.creator_tier.value if enhanced_context.creator_tier else "unknown",
                source_service=enhanced_context.source_service
            ).inc()
            
            logger.info(
                f"Alert processed successfully: {alert_context.alert_id} "
                f"in {processing_duration:.2f}s"
            )
            
            return {
                "status": "success",
                "alert_id": alert_context.alert_id,
                "severity": enhanced_context.severity.value,
                "creator_tier": enhanced_context.creator_tier.value if enhanced_context.creator_tier else None,
                "routing_decision": routing_decision.to_dict(),
                "notification_results": [result.__dict__ for result in notification_results],
                "processing_time_seconds": processing_duration,
                "correlation_id": correlation_result.correlation_id if correlation_result else None
            }
            
        except Exception as e:
            logger.error(f"Failed to process alert: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "alert_id": alert_data.get("alert_id", "unknown"),
                "processing_time_seconds": (datetime.now() - start_time).total_seconds()
            }
    
    def _parse_alert_data(self, alert_data: Dict[str, Any]) -> AlertContext:
        """Parse raw alert data into structured AlertContext"""
        try:
            # Extract basic alert information
            alert_id = alert_data.get("alert_id", f"alert_{datetime.now().timestamp()}")
            timestamp = datetime.fromisoformat(alert_data.get("timestamp", datetime.now().isoformat()))
            
            # Parse severity
            severity_str = alert_data.get("severity", "info").lower()
            severity = AlertSeverity(severity_str) if severity_str in [s.value for s in AlertSeverity] else AlertSeverity.INFO
            
            # Extract service information
            source_service = alert_data.get("service", alert_data.get("source", "unknown"))
            
            # Parse Creator-specific information
            creator_id = alert_data.get("creator_id")
            creator_tier_str = alert_data.get("creator_tier")
            creator_tier = None
            if creator_tier_str:
                try:
                    creator_tier = CreatorTier(creator_tier_str.lower())
                except ValueError:
                    logger.warning(f"Unknown creator tier: {creator_tier_str}")
            
            # Extract impact metrics
            business_impact = float(alert_data.get("business_impact", 0.0))
            revenue_impact = float(alert_data.get("revenue_impact", 0.0))
            user_count_affected = int(alert_data.get("users_affected", 0))
            
            # Parse geographic scope
            geographic_scope = alert_data.get("geographic_scope", [])
            if isinstance(geographic_scope, str):
                geographic_scope = [geographic_scope]
            
            # Extract additional metadata
            metadata = alert_data.get("metadata", {})
            
            return AlertContext(
                alert_id=alert_id,
                timestamp=timestamp,
                severity=severity,
                source_service=source_service,
                creator_id=creator_id,
                creator_tier=creator_tier,
                business_impact=business_impact,
                revenue_impact=revenue_impact,
                user_count_affected=user_count_affected,
                geographic_scope=geographic_scope,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to parse alert data: {e}")
            # Return minimal context for error cases
            return AlertContext(
                alert_id=alert_data.get("alert_id", f"alert_{datetime.now().timestamp()}"),
                timestamp=datetime.now(),
                severity=AlertSeverity.INFO,
                source_service="unknown"
            )
    
    async def _store_alert_state(
        self,
        alert_context: AlertContext,
        routing_decision: Any,
        notification_results: List[NotificationResult]
    ) -> None:
        """Store alert state in Redis for tracking and analytics"""
        if not self.redis_client:
            return
        
        try:
            state_data = {
                "alert_id": alert_context.alert_id,
                "timestamp": alert_context.timestamp.isoformat(),
                "severity": alert_context.severity.value,
                "source_service": alert_context.source_service,
                "creator_id": alert_context.creator_id,
                "creator_tier": alert_context.creator_tier.value if alert_context.creator_tier else None,
                "business_impact": alert_context.business_impact,
                "revenue_impact": alert_context.revenue_impact,
                "user_count_affected": alert_context.user_count_affected,
                "geographic_scope": alert_context.geographic_scope,
                "routing_decision": routing_decision.to_dict() if hasattr(routing_decision, 'to_dict') else str(routing_decision),
                "notification_results": [result.__dict__ for result in notification_results],
                "status": "processed",
                "created_at": datetime.now().isoformat()
            }
            
            # Store in Redis with expiration
            key = f"alert:{alert_context.alert_id}"
            await self.redis_client.setex(
                key,
                timedelta(days=30).total_seconds(),  # 30 days retention
                json.dumps(state_data)
            )
            
            # Also add to timeline for analytics
            timeline_key = f"alert_timeline:{datetime.now().strftime('%Y-%m-%d')}"
            await self.redis_client.lpush(timeline_key, alert_context.alert_id)
            await self.redis_client.expire(timeline_key, timedelta(days=90).total_seconds())
            
        except Exception as e:
            logger.error(f"Failed to store alert state: {e}")
    
    async def get_alert_status(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve alert status and processing history"""
        if not self.redis_client:
            return None
        
        try:
            key = f"alert:{alert_id}"
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve alert status: {e}")
            return None
    
    async def get_alert_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get alerting metrics and analytics"""
        try:
            # This would integrate with the analytics engine
            # For now, return basic metrics
            return {
                "total_alerts_processed": 0,
                "alerts_by_severity": {},
                "alerts_by_creator_tier": {},
                "average_processing_time": 0.0,
                "notification_success_rate": 0.0,
                "escalation_rate": 0.0
            }
        except Exception as e:
            logger.error(f"Failed to get alert metrics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for AlertManager"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check Redis connection
        try:
            if self.redis_client:
                await self.redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            else:
                health_status["components"]["redis"] = "unavailable"
        except Exception as e:
            health_status["components"]["redis"] = f"unhealthy: {e}"
            health_status["status"] = "degraded"
        
        # Check core engines
        engines = [
            ("routing_engine", self.routing_engine),
            ("severity_analyzer", self.severity_analyzer),
            ("correlation_engine", self.correlation_engine),
            ("notification_orchestrator", self.notification_orchestrator),
            ("escalation_manager", self.escalation_manager)
        ]
        
        for engine_name, engine in engines:
            try:
                if hasattr(engine, 'health_check'):
                    engine_health = await engine.health_check()
                    health_status["components"][engine_name] = engine_health
                else:
                    health_status["components"][engine_name] = "available"
            except Exception as e:
                health_status["components"][engine_name] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
        
        return health_status


# FastAPI integration for webhook endpoints
def create_alertmanager_app(orchestrator: AlertManagerOrchestrator) -> FastAPI:
    """Create FastAPI application with AlertManager endpoints"""
    app = FastAPI(
        title="AlertManager Enterprise API",
        description="AI-Powered Creator Economy Alerting System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    @app.post("/webhook/alert")
    async def webhook_alert(alert_data: Dict[str, Any], background_tasks: BackgroundTasks):
        """Webhook endpoint for receiving alerts"""
        result = await orchestrator.process_alert(alert_data, background_tasks)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    
    @app.get("/alert/{alert_id}/status")
    async def get_alert_status(alert_id: str):
        """Get status of specific alert"""
        status = await orchestrator.get_alert_status(alert_id)
        if not status:
            raise HTTPException(status_code=404, detail="Alert not found")
        return status
    
    @app.get("/metrics")
    async def get_metrics(time_range: str = "24h"):
        """Get alerting metrics"""
        return await orchestrator.get_alert_metrics(time_range)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return await orchestrator.health_check()
    
    return app


# Factory function for easy instantiation
def create_alert_manager(config_path: Optional[str] = None) -> AlertManagerOrchestrator:
    """Factory function to create AlertManager instance"""
    return AlertManagerOrchestrator(config_path)


if __name__ == "__main__":
    # CLI entry point for testing
    import uvicorn
    
    orchestrator = create_alert_manager()
    app = create_alertmanager_app(orchestrator)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )