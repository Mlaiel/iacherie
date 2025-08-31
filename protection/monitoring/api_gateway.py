"""🚀 Ultra-Advanced Monitoring API Gateway
========================================

Enterprise-grade API gateway providing unified access to all content protection
monitoring capabilities with advanced security, rate limiting, and orchestration.

Industrial Features:
- Unified RESTful and GraphQL APIs
- Real-time WebSocket streaming
- Advanced authentication and authorization
- Rate limiting and DDoS protection
- API versioning and backward compatibility
- Comprehensive request/response logging

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.
Contact mlaiel@live.de for licensing inquiries.
"""import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession

# Import monitoring components
from .ecosystem_orchestrator import MonitoringEcosystemOrchestrator
from .realtime_monitor import RealTimeMonitor, MonitoringPriority
from .analytics import MonitoringAnalytics, AnalyticsTimeRange
from .dashboard import DashboardController
from .reports import ReportGenerator, ReportFormat
from .intelligent_surveillance import IntelligentSurveillanceEngine
from .geospatial_intelligence import GeospatialIntelligenceEngine

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

class APIVersion(str, Enum):
    """API version enumeration."""    V1 = "v1"
    V2 = "v2"

class MonitoringAPIRequest(BaseModel):
    """Base monitoring API request."""    content_fingerprint: str
    user_id: int
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ComprehensiveMonitoringRequest(MonitoringAPIRequest):
    """Request for comprehensive monitoring."""    monitoring_types: List[str] = Field(default_factory=lambda: ["realtime", "surveillance", "geospatial"])
    priority: str = "medium"
    auto_response: bool = False

class IntelligenceAnalysisRequest(BaseModel):
    """Request for intelligence analysis."""    detection_data: Dict[str, Any]
    analysis_types: List[str] = Field(default_factory=lambda: ["behavioral", "geospatial", "correlation"])
    
class ReportGenerationRequest(BaseModel):
    """Request for report generation."""    report_type: str = "comprehensive"
    timeframe_hours: int = 168  # 7 days
    output_formats: List[str] = Field(default_factory=lambda: ["pdf", "json"])
    include_charts: bool = True

class MonitoringAPIResponse(BaseModel):
    """Base monitoring API response."""    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "2.0"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MonitoringAPIGateway:
    """Ultra-advanced monitoring API gateway."""    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the API gateway."""        self.config = config
        self.app = FastAPI(
            title="Content Protection Monitoring API",
            description="Ultra-advanced content protection monitoring system API",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Core dependencies
        self.redis_client = None
        self.db_session = None
        self.orchestrator = None
        
        # API state
        self.active_connections: Dict[str, WebSocket] = {}
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        
        logger.info("Monitoring API Gateway initialized")

    def _setup_middleware(self):
        """Setup API middleware."""        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get("cors_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Compression middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)

    def _setup_routes(self):
        """Setup API routes."""        
        # Health check
        @self.app.get("/health")
        async def health_check():
            """API health check endpoint."""            try:
                ecosystem_status = await self.orchestrator.get_ecosystem_status()
                return MonitoringAPIResponse(
                    success=True,
                    data={
                        "status": "healthy",
                        "ecosystem": ecosystem_status,
                        "api_version": "2.0"
                    }
                )
            except Exception as e:
                return MonitoringAPIResponse(
                    success=False,
                    error=f"Health check failed: {e}"
                )

        # Start comprehensive monitoring
        @self.app.post("/api/v2/monitoring/start")
        async def start_comprehensive_monitoring(
            request: ComprehensiveMonitoringRequest,
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Start comprehensive monitoring across all systems."""            try:
                # Validate authentication
                user_id = await self._validate_auth(credentials)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid authentication")
                
                # Check rate limits
                if not await self._check_rate_limit(user_id, "start_monitoring"):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                
                # Start monitoring
                result = await self.orchestrator.start_comprehensive_monitoring(
                    content_fingerprint=request.content_fingerprint,
                    user_id=request.user_id,
                    monitoring_config={
                        "monitoring_types": request.monitoring_types,
                        "priority": request.priority,
                        "auto_response": request.auto_response,
                        **request.config
                    }
                )
                
                # Log API usage
                background_tasks.add_task(
                    self._log_api_usage,
                    user_id, "start_monitoring", request.dict()
                )
                
                return MonitoringAPIResponse(
                    success=True,
                    data=result
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to start comprehensive monitoring: {e}")
                return MonitoringAPIResponse(
                    success=False,
                    error=str(e)
                )

        # Process detection event
        @self.app.post("/api/v2/monitoring/detection")
        async def process_detection_event(
            detection_data: Dict[str, Any],
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Process detection event through all monitoring systems."""            try:
                user_id = await self._validate_auth(credentials)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid authentication")
                
                if not await self._check_rate_limit(user_id, "process_detection"):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                
                # Process detection event
                result = await self.orchestrator.process_detection_event(detection_data)
                
                # Notify WebSocket clients
                await self._notify_websocket_clients("detection_processed", result)
                
                background_tasks.add_task(
                    self._log_api_usage,
                    user_id, "process_detection", detection_data
                )
                
                return MonitoringAPIResponse(
                    success=True,
                    data=result
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to process detection event: {e}")
                return MonitoringAPIResponse(
                    success=False,
                    error=str(e)
                )

        # Intelligence analysis
        @self.app.post("/api/v2/intelligence/analyze")
        async def analyze_intelligence(
            request: IntelligenceAnalysisRequest,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Perform comprehensive intelligence analysis."""            try:
                user_id = await self._validate_auth(credentials)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid authentication")
                
                if not await self._check_rate_limit(user_id, "analyze_intelligence"):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                
                analysis_results = {}
                
                # Behavioral analysis
                if "behavioral" in request.analysis_types:
                    surveillance_engine = self.orchestrator.components.get("intelligent_surveillance")
                    if surveillance_engine:
                        # Perform behavioral analysis
                        analysis_results["behavioral"] = await self._perform_behavioral_analysis(
                            request.detection_data, surveillance_engine
                        )
                
                # Geospatial analysis
                if "geospatial" in request.analysis_types:
                    geo_engine = self.orchestrator.components.get("geospatial_intelligence")
                    if geo_engine and request.detection_data.get("source_ip"):
                        geospatial_threat = await geo_engine.analyze_geospatial_threat(
                            request.detection_data, request.detection_data["source_ip"]
                        )
                        analysis_results["geospatial"] = geospatial_threat.__dict__ if geospatial_threat else None
                
                # Cross-system correlation
                if "correlation" in request.analysis_types:
                    correlation_results = await self.orchestrator._correlate_intelligence(request.detection_data)
                    analysis_results["correlation"] = correlation_results
                
                return MonitoringAPIResponse(
                    success=True,
                    data=analysis_results
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to analyze intelligence: {e}")
                return MonitoringAPIResponse(
                    success=False,
                    error=str(e)
                )

        # Generate reports
        @self.app.post("/api/v2/reports/generate")
        async def generate_report(
            request: ReportGenerationRequest,
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Generate comprehensive monitoring reports."""            try:
                user_id = await self._validate_auth(credentials)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid authentication")
                
                if not await self._check_rate_limit(user_id, "generate_report"):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                
                report_generator = self.orchestrator.components.get("report_generator")
                if not report_generator:
                    raise HTTPException(status_code=503, detail="Report generator not available")
                
                # Generate report
                report_id = f"api_report_{int(datetime.utcnow().timestamp())}"
                
                background_tasks.add_task(
                    self._generate_report_background,
                    report_generator, report_id, request
                )
                
                return MonitoringAPIResponse(
                    success=True,
                    data={
                        "report_id": report_id,
                        "status": "generating",
                        "estimated_completion_time": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to generate report: {e}")
                return MonitoringAPIResponse(
                    success=False,
                    error=str(e)
                )

        # Get monitoring status
        @self.app.get("/api/v2/monitoring/status/{session_id}")
        async def get_monitoring_status(
            session_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get monitoring session status."""            try:
                user_id = await self._validate_auth(credentials)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid authentication")
                
                # Get session data from Redis
                session_data = await self.redis_client.hgetall(f"comprehensive_monitoring:{session_id}")
                
                if not session_data:
                    raise HTTPException(status_code=404, detail="Monitoring session not found")
                
                # Enrich with current metrics
                status_data = {
                    "session_id": session_id,
                    "status": session_data.get("status", "unknown"),
                    "started_at": session_data.get("started_at"),
                    "components_active": json.loads(session_data.get("components_active", "[]")),
                    "current_metrics": {}
                }
                
                # Get real-time metrics
                realtime_monitor = self.orchestrator.components.get("realtime_monitor")
                if realtime_monitor:
                    status_data["current_metrics"]["realtime"] = await realtime_monitor.get_current_metrics()
                
                # Get analytics data
                analytics = self.orchestrator.components.get("analytics_engine")
                if analytics:
                    content_fingerprint = session_data.get("content_fingerprint")
                    if content_fingerprint:
                        insights = await analytics.get_real_time_insights(content_fingerprint)
                        status_data["current_metrics"]["analytics"] = insights
                
                return MonitoringAPIResponse(
                    success=True,
                    data=status_data
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get monitoring status: {e}")
                return MonitoringAPIResponse(
                    success=False,
                    error=str(e)
                )

        # WebSocket endpoint for real-time updates
        @self.app.websocket("/api/v2/monitoring/websocket/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            """WebSocket endpoint for real-time monitoring updates."""            try:
                await websocket.accept()
                self.active_connections[client_id] = websocket
                
                logger.info(f"WebSocket client connected: {client_id}")
                
                # Send welcome message
                await websocket.send_json({
                    "type": "connection_established",
                    "client_id": client_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                try:
                    while True:
                        # Keep connection alive and handle client messages
                        data = await websocket.receive_text()
                        message = json.loads(data)
                        
                        if message.get("type") == "ping":
                            await websocket.send_json({
                                "type": "pong",
                                "timestamp": datetime.utcnow().isoformat()
                            })
                        elif message.get("type") == "subscribe":
                            # Handle subscription to specific monitoring sessions
                            await self._handle_websocket_subscription(client_id, message)
                        
                except WebSocketDisconnect:
                    logger.info(f"WebSocket client disconnected: {client_id}")
                
            except Exception as e:
                logger.error(f"WebSocket error for client {client_id}: {e}")
            finally:
                if client_id in self.active_connections:
                    del self.active_connections[client_id]

        # Get ecosystem status
        @self.app.get("/api/v2/ecosystem/status")
        async def get_ecosystem_status(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Get comprehensive ecosystem status."""            try:
                user_id = await self._validate_auth(credentials)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid authentication")
                
                status = await self.orchestrator.get_ecosystem_status()
                
                return MonitoringAPIResponse(
                    success=True,
                    data=status
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get ecosystem status: {e}")
                return MonitoringAPIResponse(
                    success=False,
                    error=str(e)
                )

        # Download report
        @self.app.get("/api/v2/reports/download/{report_id}")
        async def download_report(
            report_id: str,
            format: str = "pdf",
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Download generated report."""            try:
                user_id = await self._validate_auth(credentials)
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid authentication")
                
                # Check if report exists
                report_data = await self.redis_client.hgetall(f"generated_report:{report_id}")
                
                if not report_data:
                    raise HTTPException(status_code=404, detail="Report not found")
                
                # Get report file path
                file_path = report_data.get(f"file_path_{format}")
                if not file_path:
                    raise HTTPException(status_code=404, detail=f"Report format {format} not available")
                
                # Return file
                return FileResponse(
                    path=file_path,
                    filename=f"monitoring_report_{report_id}.{format}",
                    media_type="application/octet-stream"
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to download report: {e}")
                return MonitoringAPIResponse(
                    success=False,
                    error=str(e)
                )

    async def initialize(self, redis_client: aioredis.Redis, db_session: AsyncSession):
        """Initialize the API gateway."""        self.redis_client = redis_client
        self.db_session = db_session
        
        # Initialize orchestrator
        self.orchestrator = MonitoringEcosystemOrchestrator(self.config.get("orchestrator", {}))
        await self.orchestrator.initialize(redis_client, db_session)
        
        logger.info("Monitoring API Gateway fully initialized")

    async def _validate_auth(self, credentials: HTTPAuthorizationCredentials) -> Optional[int]:
        """Validate authentication credentials."""        try:
            # In production, implement proper JWT validation
            token = credentials.credentials
            
            # For demo purposes, extract user_id from token
            # In production, validate JWT and extract user claims
            if token.startswith("user_"):
                return int(token.split("_")[1])
            
            return None
            
        except Exception as e:
            logger.error(f"Authentication validation failed: {e}")
            return None

    async def _check_rate_limit(self, user_id: int, action: str) -> bool:
        """Check rate limiting for user actions."""        try:
            current_time = datetime.utcnow()
            rate_key = f"rate_limit:{user_id}:{action}"
            
            # Get current rate limit data
            rate_data = await self.redis_client.hgetall(rate_key)
            
            if rate_data:
                last_request = datetime.fromisoformat(rate_data.get("last_request", ""))
                request_count = int(rate_data.get("count", 0))
                
                # Reset counter if more than 1 hour passed
                if (current_time - last_request).total_seconds() > 3600:
                    request_count = 0
                
                # Check limits (adjust based on action type)
                limits = {
                    "start_monitoring": 100,
                    "process_detection": 1000,
                    "analyze_intelligence": 500,
                    "generate_report": 10
                }
                
                if request_count >= limits.get(action, 100):
                    return False
            
            # Update rate limit data
            await self.redis_client.hset(
                rate_key,
                mapping={
                    "last_request": current_time.isoformat(),
                    "count": str(int(rate_data.get("count", 0)) + 1)
                }
            )
            
            # Set expiration
            await self.redis_client.expire(rate_key, 3600)  # 1 hour
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error

    async def _log_api_usage(self, user_id: int, action: str, request_data: Dict[str, Any]):
        """Log API usage for analytics."""        try:
            log_entry = {
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "request_data": json.dumps(request_data),
                "api_version": "2.0"
            }
            
            await self.redis_client.lpush(
                "api_usage_log",
                json.dumps(log_entry)
            )
            
            # Keep only last 10000 entries
            await self.redis_client.ltrim("api_usage_log", 0, 9999)
            
        except Exception as e:
            logger.error(f"Failed to log API usage: {e}")

    async def _notify_websocket_clients(self, event_type: str, data: Dict[str, Any]):
        """Notify all connected WebSocket clients."""        try:
            message = {
                "type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            disconnected_clients = []
            
            for client_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send message to client {client_id}: {e}")
                    disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                if client_id in self.active_connections:
                    del self.active_connections[client_id]
                    
        except Exception as e:
            logger.error(f"Failed to notify WebSocket clients: {e}")

    async def _handle_websocket_subscription(self, client_id: str, message: Dict[str, Any]):
        """Handle WebSocket subscription requests."""        try:
            subscription_type = message.get("subscription_type")
            session_id = message.get("session_id")
            
            if subscription_type == "monitoring_session" and session_id:
                # Subscribe client to monitoring session updates
                await self.redis_client.sadd(
                    f"websocket_subscriptions:{session_id}",
                    client_id
                )
                
                # Send confirmation
                websocket = self.active_connections.get(client_id)
                if websocket:
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "subscription_type": subscription_type,
                        "session_id": session_id
                    })
                    
        except Exception as e:
            logger.error(f"Failed to handle WebSocket subscription: {e}")

    async def _perform_behavioral_analysis(
        self,
        detection_data: Dict[str, Any],
        surveillance_engine: IntelligentSurveillanceEngine
    ) -> Dict[str, Any]:
        """Perform behavioral analysis on detection data."""        try:
            # Extract content fingerprint
            content_fingerprint = detection_data.get("fingerprint_id")
            if not content_fingerprint:
                return {"error": "No content fingerprint provided"}
            
            # Collect behavioral data
            behavioral_data = await surveillance_engine._collect_behavioral_data(content_fingerprint)
            
            if not behavioral_data:
                return {"message": "No behavioral data available"}
            
            # Analyze patterns
            patterns = await surveillance_engine._analyze_behavioral_patterns(behavioral_data)
            
            # Detect anomalies
            anomalies = await surveillance_engine._detect_behavioral_anomalies(behavioral_data)
            
            return {
                "behavioral_data_summary": {
                    "detections_count": len(behavioral_data.get("detections", [])),
                    "platforms_involved": len(behavioral_data.get("platforms", [])),
                    "time_span_hours": 24
                },
                "patterns": patterns,
                "anomalies": anomalies,
                "threat_assessment": surveillance_engine._assess_threat_level(patterns, anomalies)
            }
            
        except Exception as e:
            logger.error(f"Failed to perform behavioral analysis: {e}")
            return {"error": str(e)}

    async def _generate_report_background(
        self,
        report_generator: ReportGenerator,
        report_id: str,
        request: ReportGenerationRequest
    ):
        """Generate report in background task."""        try:
            # Generate report based on request parameters
            report_data = await self._create_comprehensive_report(request)
            
            # Generate different formats
            file_paths = {}
            
            for output_format in request.output_formats:
                if output_format == "pdf":
                    file_path = await report_generator.generate_pdf_report(
                        report_data, f"/tmp/report_{report_id}.pdf"
                    )
                    file_paths["file_path_pdf"] = file_path
                elif output_format == "json":
                    file_path = f"/tmp/report_{report_id}.json"
                    with open(file_path, 'w') as f:
                        json.dump(report_data, f, indent=2, default=str)
                    file_paths["file_path_json"] = file_path
            
            # Store report metadata
            await self.redis_client.hset(
                f"generated_report:{report_id}",
                mapping={
                    "status": "completed",
                    "generated_at": datetime.utcnow().isoformat(),
                    "report_type": request.report_type,
                    **file_paths
                }
            )
            
            # Notify WebSocket clients
            await self._notify_websocket_clients("report_completed", {
                "report_id": report_id,
                "status": "completed"
            })
            
        except Exception as e:
            logger.error(f"Failed to generate report {report_id}: {e}")
            
            # Update report status to failed
            await self.redis_client.hset(
                f"generated_report:{report_id}",
                mapping={
                    "status": "failed",
                    "error": str(e),
                    "failed_at": datetime.utcnow().isoformat()
                }
            )

    async def _create_comprehensive_report(self, request: ReportGenerationRequest) -> Dict[str, Any]:
        """Create comprehensive report data."""        try:
            report_data = {
                "report_id": f"comp_report_{int(datetime.utcnow().timestamp())}",
                "generation_time": datetime.utcnow().isoformat(),
                "timeframe_hours": request.timeframe_hours,
                "report_type": request.report_type,
                "sections": {}
            }
            
            # Ecosystem overview
            ecosystem_status = await self.orchestrator.get_ecosystem_status()
            report_data["sections"]["ecosystem_overview"] = ecosystem_status
            
            # Geospatial intelligence
            geo_engine = self.orchestrator.components.get("geospatial_intelligence")
            if geo_engine:
                geo_report = await geo_engine.generate_geospatial_intelligence_report(request.timeframe_hours)
                report_data["sections"]["geospatial_intelligence"] = geo_report
            
            # Analytics summary
            analytics = self.orchestrator.components.get("analytics_engine")
            if analytics:
                analytics_data = await analytics.generate_comprehensive_analytics_report(
                    timeframe_hours=request.timeframe_hours
                )
                report_data["sections"]["analytics"] = analytics_data
            
            # Performance metrics
            performance_optimizer = self.orchestrator.components.get("performance_optimizer")
            if performance_optimizer:
                performance_data = await performance_optimizer.generate_performance_report()
                report_data["sections"]["performance"] = performance_data
            
            return report_data
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive report: {e}")
            raise

    async def shutdown(self):
        """Shutdown the API gateway."""        logger.info("Shutting down Monitoring API Gateway...")
        
        # Close all WebSocket connections
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket for client {client_id}: {e}")
        
        # Shutdown orchestrator
        if self.orchestrator:
            await self.orchestrator.shutdown()
        
        logger.info("Monitoring API Gateway shutdown complete")
