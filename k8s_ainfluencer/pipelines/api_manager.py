"""IA Influencer Agent - Pipeline API Management System
Enterprise-Grade REST API for Pipeline Operations and Management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive REST API endpoints for pipeline management, monitoring,
and control, enabling integration with external systems and web interfaces.

Features:
- RESTful API for pipeline operations
- Real-time pipeline status and monitoring
- Security and authentication integration
- Webhook support for external notifications
- Comprehensive API documentation

WARNING: This code is proprietary and confidential. Any unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action under German and international law.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, Path as PathParam
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, StreamingResponse
    from pydantic import BaseModel, Field, validator
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from . import Environment, PipelineType, PipelineConfig, PipelineStatus
from .pipeline_manager import AdvancedPipelineManager, PipelineExecution
from .config_manager import PipelineConfigManager
from .notification_manager import NotificationManager
from .monitoring_manager import PipelineMonitoringManager
from .security_manager import PipelineSecurityManager

# Pydantic models for API requests/responses
class PipelineConfigRequest(BaseModel):
    """
Pipeline configuration request model"""
    name: str = Field(..., description="Pipeline name")
    environment: str = Field(..., description="Target environment")
    pipeline_type: str = Field(..., description="Pipeline type")
    steps: List[str] = Field(..., description="Pipeline steps")
    timeout: Optional[int] = Field(3600, description="Timeout in seconds")
    retry_count: Optional[int] = Field(3, description="Number of retries")
    parallel_execution: Optional[bool] = Field(False, description="Enable parallel execution")
    notifications: Optional[Dict[str, Any]] = Field({}, description="Notification settings")
    
    @validator('environment')
    def validate_environment(cls, v):
        try:
            Environment(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid environment: {v}")
            
    @validator('pipeline_type')
    def validate_pipeline_type(cls, v):
        try:
            PipelineType(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid pipeline type: {v}")

class PipelineExecutionRequest(BaseModel):
    """Pipeline execution request model"""
    pipeline_id: str = Field(..., description="Pipeline identifier")
    context: Optional[Dict[str, Any]] = Field({}, description="Execution context")
    
class PipelineStatusResponse(BaseModel):
    """Pipeline status response model"""
    execution_id: str
    pipeline_name: str
    environment: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[str] = None
    
class PipelineListResponse(BaseModel):
    """
Pipeline list response model"""
    pipelines: List[Dict[str, Any]]
    total_count: int
    
class SecurityScanRequest(BaseModel):
    """
Security scan request model"""
    project_path: str = Field(..., description="Project path to scan")
    image_name: Optional[str] = Field(None, description="Container image name")
    policy_name: str = Field("development", description="Security policy name")

class MetricsRequest(BaseModel):
    """Metrics request model"""
    pipeline_name: Optional[str] = None
    environment: Optional[str] = None
    hours: int = Field(24, description="Time range in hours")

# Authentication handler
security = HTTPBearer() if FASTAPI_AVAILABLE else None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate API authentication"""
    # In production, implement proper JWT validation
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"user_id": "api_user", "token": credentials.credentials}

class PipelineAPIManager:
    """
    Advanced Pipeline API Management System
    
    Provides enterprise-grade REST API for pipeline operations with:
    - Complete CRUD operations for pipelines
    - Real-time execution monitoring
    - Security scanning integration
    - Metrics and analytics endpoints
    - Webhook and notification management
    """
    
    def __init__(self, 
                 pipeline_manager: AdvancedPipelineManager,
                 config_manager: PipelineConfigManager,
                 notification_manager: NotificationManager,
                 monitoring_manager: PipelineMonitoringManager,
                 security_manager: PipelineSecurityManager,
                 host: str = "0.0.0.0",
                 port: int = 8080):
        
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI is required for API functionality")
            
        self.pipeline_manager = pipeline_manager
        self.config_manager = config_manager
        self.notification_manager = notification_manager
        self.monitoring_manager = monitoring_manager
        self.security_manager = security_manager
        
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="IA Influencer Agent - Pipeline API",
            description="Enterprise-Grade Pipeline Management API",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
        
    def _register_routes(self):
        """Register all API routes"""
        
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
            
        # Pipeline management endpoints
        @self.app.post("/api/v1/pipelines/register")
        async def register_pipeline(
            request: PipelineConfigRequest,
            current_user: dict = Depends(get_current_user)
        ):
            """Register a new pipeline configuration"""
            try:
                config = PipelineConfig(
                    name=request.name,
                    environment=Environment(request.environment),
                    pipeline_type=PipelineType(request.pipeline_type),
                    steps=request.steps,
                    timeout=request.timeout,
                    retry_count=request.retry_count,
                    parallel_execution=request.parallel_execution,
                    notifications=request.notifications
                )
                
                pipeline_id = self.pipeline_manager.register_pipeline(config)
                
                return {
                    "pipeline_id": pipeline_id,
                    "status": "registered",
                    "message": f"Pipeline {request.name} registered successfully"
                }
                
            except Exception as e:
                self.logger.error(f"Failed to register pipeline: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
                
        @self.app.get("/api/v1/pipelines")
        async def list_pipelines(
            environment: Optional[str] = Query(None),
            pipeline_type: Optional[str] = Query(None),
            current_user: dict = Depends(get_current_user)
        ) -> PipelineListResponse:
            """List all registered pipelines"""
            try:
                pipelines = []
                for pipeline_id, config in self.pipeline_manager.registered_pipelines.items():
                    if environment and config.environment.value != environment:
                        continue
                    if pipeline_type and config.pipeline_type.value != pipeline_type:
                        continue
                        
                    pipelines.append({
                        "pipeline_id": pipeline_id,
                        "name": config.name,
                        "environment": config.environment.value,
                        "pipeline_type": config.pipeline_type.value,
                        "steps": config.steps,
                        "timeout": config.timeout,
                        "parallel_execution": config.parallel_execution
                    })
                    
                return PipelineListResponse(
                    pipelines=pipelines,
                    total_count=len(pipelines)
                )
                
            except Exception as e:
                self.logger.error(f"Failed to list pipelines: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.post("/api/v1/pipelines/execute")
        async def execute_pipeline(
            request: PipelineExecutionRequest,
            background_tasks: BackgroundTasks,
            current_user: dict = Depends(get_current_user)
        ):
            """Execute a pipeline"""
            try:
                execution_id = await self.pipeline_manager.execute_pipeline(
                    request.pipeline_id,
                    request.context
                )
                
                return {
                    "execution_id": execution_id,
                    "status": "started",
                    "message": f"Pipeline execution {execution_id} started"
                }
                
            except Exception as e:
                self.logger.error(f"Failed to execute pipeline: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))
                
        @self.app.get("/api/v1/pipelines/executions/{execution_id}")
        async def get_execution_status(
            execution_id: str = PathParam(...),
            current_user: dict = Depends(get_current_user)
        ) -> PipelineStatusResponse:
            """Get pipeline execution status"""
            try:
                details = self.pipeline_manager.get_execution_details(execution_id)
                if not details:
                    raise HTTPException(status_code=404, detail="Execution not found")
                    
                return PipelineStatusResponse(
                    execution_id=details["execution_id"],
                    pipeline_name=details["config"]["name"],
                    environment=details["config"]["environment"],
                    status=details["status"],
                    start_time=details["start_time"],
                    end_time=details["end_time"],
                    duration=details["duration"]
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get execution status: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/v1/pipelines/executions/{execution_id}/details")
        async def get_execution_details(
            execution_id: str = PathParam(...),
            current_user: dict = Depends(get_current_user)
        ):
            """Get detailed pipeline execution information"""
            try:
                details = self.pipeline_manager.get_execution_details(execution_id)
                if not details:
                    raise HTTPException(status_code=404, detail="Execution not found")
                    
                return details
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get execution details: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.delete("/api/v1/pipelines/executions/{execution_id}")
        async def cancel_pipeline_execution(
            execution_id: str = PathParam(...),
            current_user: dict = Depends(get_current_user)
        ):
            """Cancel a running pipeline execution"""
            try:
                success = await self.pipeline_manager.cancel_pipeline(execution_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Execution not found or already completed")
                    
                return {
                    "execution_id": execution_id,
                    "status": "cancelled",
                    "message": "Pipeline execution cancelled successfully"
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to cancel pipeline: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/v1/pipelines/active")
        async def list_active_pipelines(
            current_user: dict = Depends(get_current_user)
        ):
            """List all currently active pipeline executions"""
            try:
                active_pipelines = self.pipeline_manager.list_active_pipelines()
                
                pipeline_details = []
                for execution_id in active_pipelines:
                    details = self.pipeline_manager.get_execution_details(execution_id)
                    if details:
                        pipeline_details.append({
                            "execution_id": execution_id,
                            "pipeline_name": details["config"]["name"],
                            "environment": details["config"]["environment"],
                            "status": details["status"],
                            "start_time": details["start_time"]
                        })
                        
                return {
                    "active_pipelines": pipeline_details,
                    "count": len(pipeline_details)
                }
                
            except Exception as e:
                self.logger.error(f"Failed to list active pipelines: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        # Configuration management endpoints
        @self.app.get("/api/v1/config/templates")
        async def list_templates(
            current_user: dict = Depends(get_current_user)
        ):
            """List all available pipeline templates"""
            try:
                templates = self.config_manager.list_templates()
                template_details = []
                
                for template_name in templates:
                    info = self.config_manager.get_template_info(template_name)
                    if info:
                        template_details.append(info)
                        
                return {
                    "templates": template_details,
                    "count": len(template_details)
                }
                
            except Exception as e:
                self.logger.error(f"Failed to list templates: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/v1/config/environments")
        async def list_environments(
            current_user: dict = Depends(get_current_user)
        ):
            """List all configured environments"""
            try:
                environments = self.config_manager.list_environments()
                environment_details = []
                
                for env_name in environments:
                    info = self.config_manager.get_environment_info(env_name)
                    if info:
                        environment_details.append(info)
                        
                return {
                    "environments": environment_details,
                    "count": len(environment_details)
                }
                
            except Exception as e:
                self.logger.error(f"Failed to list environments: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        # Security endpoints
        @self.app.post("/api/v1/security/scan")
        async def run_security_scan(
            request: SecurityScanRequest,
            background_tasks: BackgroundTasks,
            current_user: dict = Depends(get_current_user)
        ):
            """Run comprehensive security scan"""
            try:
                project_path = Path(request.project_path)
                if not project_path.exists():
                    raise HTTPException(status_code=400, detail="Project path does not exist")
                    
                # Run scan in background
                scan_task = asyncio.create_task(
                    self.security_manager.run_comprehensive_security_scan(
                        project_path,
                        request.image_name,
                        request.policy_name
                    )
                )
                
                scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                return {
                    "scan_id": scan_id,
                    "status": "started",
                    "message": "Security scan started",
                    "project_path": str(project_path),
                    "image_name": request.image_name,
                    "policy_name": request.policy_name
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to start security scan: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/v1/security/report")
        async def get_security_report(
            environment: str = Query("all"),
            days: int = Query(30),
            current_user: dict = Depends(get_current_user)
        ):
            """Get security report"""
            try:
                report = self.security_manager.generate_security_report(environment, days)
                return report
                
            except Exception as e:
                self.logger.error(f"Failed to generate security report: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        # Metrics and monitoring endpoints
        @self.app.get("/api/v1/metrics/pipeline")
        async def get_pipeline_metrics(
            request: MetricsRequest = Depends(),
            current_user: dict = Depends(get_current_user)
        ):
            """Get pipeline metrics and analytics"""
            try:
                if request.pipeline_name and request.environment:
                    analytics = self.monitoring_manager.get_pipeline_analytics(
                        request.pipeline_name,
                        request.environment,
                        request.hours
                    )
                    return analytics
                else:
                    # Return general metrics
                    return {
                        "message": "Provide pipeline_name and environment for specific analytics"
                    }
                    
            except Exception as e:
                self.logger.error(f"Failed to get pipeline metrics: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/v1/metrics/alerts")
        async def get_active_alerts(
            current_user: dict = Depends(get_current_user)
        ):
            """Get active alerts"""
            try:
                alerts = self.monitoring_manager.check_alerts()
                return {
                    "alerts": alerts,
                    "count": len(alerts),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Failed to get alerts: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        # Stream endpoints for real-time updates
        @self.app.get("/api/v1/stream/executions/{execution_id}")
        async def stream_execution_logs(
            execution_id: str = PathParam(...),
            current_user: dict = Depends(get_current_user)
        ):
            """Stream real-time execution logs"""
            async def generate_logs():
                while True:
                    details = self.pipeline_manager.get_execution_details(execution_id)
                    if details:
                        yield f"data: {json.dumps(details)}\n\n"
                        
                        if details["status"] in ["success", "failed", "cancelled"]:
                            break
                            
                    await asyncio.sleep(1)
                    
            return StreamingResponse(
                generate_logs(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
            
        # Administrative endpoints
        @self.app.post("/api/v1/admin/cleanup")
        async def cleanup_old_data(
            retention_days: int = Query(30),
            current_user: dict = Depends(get_current_user)
        ):
            """Clean up old pipeline data"""
            try:
                self.monitoring_manager.cleanup_old_data(retention_days)
                
                return {
                    "status": "completed",
                    "message": f"Cleaned up data older than {retention_days} days",
                    "retention_days": retention_days
                }
                
            except Exception as e:
                self.logger.error(f"Failed to cleanup old data: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/v1/admin/stats")
        async def get_system_stats(
            current_user: dict = Depends(get_current_user)
        ):
            """Get system statistics"""
            try:
                active_pipelines = len(self.pipeline_manager.list_active_pipelines())
                registered_pipelines = len(self.pipeline_manager.registered_pipelines)
                
                return {
                    "active_pipelines": active_pipelines,
                    "registered_pipelines": registered_pipelines,
                    "total_executions": len(self.pipeline_manager.execution_history),
                    "system_uptime": "N/A",  # Implement if needed
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Failed to get system stats: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
    def run_server(self):
        """Run the API server"""
        self.logger.info(f"Starting Pipeline API server on {self.host}:{self.port}")
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        
    def get_app(self):
        """Get FastAPI application instance"""
        return self.app

# API server factory function
def create_api_server(
    pipeline_manager: AdvancedPipelineManager,
    config_manager: PipelineConfigManager,
    notification_manager: NotificationManager,
    monitoring_manager: PipelineMonitoringManager,
    security_manager: PipelineSecurityManager,
    host: str = "0.0.0.0",
    port: int = 8080
) -> PipelineAPIManager:
    """Create and configure Pipeline API server"""
    return PipelineAPIManager(
        pipeline_manager=pipeline_manager,
        config_manager=config_manager,
        notification_manager=notification_manager,
        monitoring_manager=monitoring_manager,
        security_manager=security_manager,
        host=host,
        port=port
    )
