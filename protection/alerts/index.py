"""Content Protection Alert System API Index
Created by: Fahed Mlaiel (mlaiel@live.de)

WARNING: This code is proprietary and confidential.
Unauthorized use, reproduction, or distribution is strictly prohibited.
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Main API endpoint aggregator for the alert system.
Provides centralized access to all alert-related services and operations.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from .manager import AlertManager, AlertManagerConfig, AlertProcessingResult, BulkOperationResult
from .notification_engine import NotificationEngine, NotificationChannel, DeliveryResult
from .escalation_engine import EscalationEngine, EscalationPolicy, EscalationAction
from .evidence_collector import EvidenceCollector, EvidenceType, CollectionMethod
from .dashboard_service import DashboardService, DashboardMetrics, RealTimeStats
from .ml_classifier import AlertMLClassifier, ClassificationModel, PredictionResult

from .alert_models import (
    ContentProtectionAlert,
    AlertSeverity,
    AlertStatus,
    AlertCategory,
    EscalationLevel,
    AlertEvidenceModel,
    AlertActionModel,
    NotificationPreferences,
    AlertDashboardMetrics,
    MLClassificationResult
)

from ...core.database import get_async_session
from ...core.security import verify_token, get_current_user
from ...core.config import settings
from ...core.cache import CacheManager
from ...core.metrics import MetricsCollector

logger = logging.getLogger(__name__)
security = HTTPBearer()

# API Models for requests/responses
class CreateAlertRequest(BaseModel):
    """Request model for creating new alerts."""    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    severity: AlertSeverity
    category: AlertCategory
    content_id: str = Field(..., min_length=1)
    content_owner: str = Field(..., min_length=1)
    content_type: str = Field(..., min_length=1)
    detection_method: str = Field(..., min_length=1)
    ai_model_version: str = Field(..., min_length=1)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    threat_actor: Optional[str] = None
    potential_loss: Optional[float] = None
    affected_users: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpdateAlertRequest(BaseModel):
    """Request model for updating alerts."""    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertSearchRequest(BaseModel):
    """Request model for searching alerts."""    severity: Optional[List[AlertSeverity]] = None
    status: Optional[List[AlertStatus]] = None
    category: Optional[List[AlertCategory]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    content_owner: Optional[str] = None
    source_platform: Optional[str] = None
    assigned_to: Optional[str] = None
    text_search: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")


class BulkAlertActionRequest(BaseModel):
    """Request model for bulk alert actions."""    alert_ids: List[str] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., regex="^(acknowledge|resolve|escalate|assign)$")
    actor: str = Field(..., min_length=1)
    resolution: Optional[str] = None
    assigned_to: Optional[str] = None
    escalation_level: Optional[EscalationLevel] = None
    notes: Optional[str] = None


class AlertResponse(BaseModel):
    """Response model for alert operations."""    success: bool
    alert: Optional[ContentProtectionAlert] = None
    message: str
    processing_time_ms: float
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class AlertListResponse(BaseModel):
    """Response model for alert list operations."""    alerts: List[ContentProtectionAlert]
    total_count: int
    page_count: int
    current_page: int
    filters_applied: Dict[str, Any]
    execution_time_ms: float


class AlertStatisticsResponse(BaseModel):
    """Response model for alert statistics."""    statistics: AlertDashboardMetrics
    trends: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    last_updated: datetime


# Alert System API Class
class AlertSystemAPI:
    """    Comprehensive API interface for the Content Protection Alert System.
    Provides enterprise-grade endpoints for alert management, monitoring, and analytics.
    """    
    def __init__(
        self,
        alert_manager: AlertManager,
        notification_engine: NotificationEngine,
        escalation_engine: EscalationEngine,
        evidence_collector: EvidenceCollector,
        dashboard_service: DashboardService,
        ml_classifier: AlertMLClassifier,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector
    ):
        self.alert_manager = alert_manager
        self.notification_engine = notification_engine
        self.escalation_engine = escalation_engine
        self.evidence_collector = evidence_collector
        self.dashboard_service = dashboard_service
        self.ml_classifier = ml_classifier
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        
        # Active WebSocket connections for real-time updates
        self.active_connections: Dict[str, WebSocket] = {}
        
        logger.info("Alert System API initialized")

    async def create_alert(
        self,
        request: CreateAlertRequest,
        background_tasks: BackgroundTasks,
        current_user: str = Depends(get_current_user)
    ) -> AlertResponse:
        """Create a new content protection alert."""        start_time = datetime.now(timezone.utc)
        
        try:
            # Create alert from request
            alert = ContentProtectionAlert(
                title=request.title,
                description=request.description,
                severity=request.severity,
                category=request.category,
                content_id=request.content_id,
                content_owner=request.content_owner,
                content_type=request.content_type,
                detection_method=request.detection_method,
                ai_model_version=request.ai_model_version,
                confidence_score=request.confidence_score,
                source_platform=request.source_platform,
                source_url=request.source_url,
                threat_actor=request.threat_actor,
                potential_loss=request.potential_loss,
                affected_users=request.affected_users
            )
            
            # Set metadata
            if request.metadata:
                alert.metadata = AlertMetadata(**request.metadata)
            
            # Process alert through manager
            result = await self.alert_manager.create_alert(alert)
            
            # Schedule background tasks
            background_tasks.add_task(self._handle_new_alert_background, alert.alert_id)
            
            # Send real-time notification
            await self._broadcast_alert_event("alert.created", alert.dict())
            
            # Calculate processing time
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return AlertResponse(
                success=True,
                alert=alert,
                message=f"Alert created successfully with ID: {alert.alert_id}",
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return AlertResponse(
                success=False,
                message="Failed to create alert",
                processing_time_ms=processing_time,
                errors=[str(e)]
            )

    async def get_alert(
        self,
        alert_id: str,
        current_user: str = Depends(get_current_user)
    ) -> AlertResponse:
        """Get a specific alert by ID."""        start_time = datetime.now(timezone.utc)
        
        try:
            alert = await self.alert_manager.get_alert(alert_id)
            
            if not alert:
                raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return AlertResponse(
                success=True,
                alert=alert,
                message="Alert retrieved successfully",
                processing_time_ms=processing_time
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get alert {alert_id}: {e}")
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return AlertResponse(
                success=False,
                message=f"Failed to retrieve alert: {alert_id}",
                processing_time_ms=processing_time,
                errors=[str(e)]
            )

    async def update_alert(
        self,
        alert_id: str,
        request: UpdateAlertRequest,
        background_tasks: BackgroundTasks,
        current_user: str = Depends(get_current_user)
    ) -> AlertResponse:
        """Update an existing alert."""        start_time = datetime.now(timezone.utc)
        
        try:
            # Get existing alert
            alert = await self.alert_manager.get_alert(alert_id)
            if not alert:
                raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")
            
            # Update fields
            update_made = False
            
            if request.status and request.status != alert.status:
                alert.status = request.status
                update_made = True
                
                # Handle specific status changes
                if request.status == AlertStatus.RESOLVED and request.resolution:
                    alert.resolve(request.resolution, current_user)
                elif request.status == AlertStatus.ACKNOWLEDGED:
                    await self.alert_manager.acknowledge_alert(alert_id, current_user)
            
            if request.assigned_to and request.assigned_to != alert.assigned_to:
                alert.assigned_to = request.assigned_to
                update_made = True
            
            if request.metadata:
                # Merge metadata
                current_metadata = alert.metadata.dict() if alert.metadata else {}
                current_metadata.update(request.metadata)
                alert.metadata = AlertMetadata(**current_metadata)
                update_made = True
            
            if not update_made:
                return AlertResponse(
                    success=True,
                    alert=alert,
                    message="No changes to update",
                    processing_time_ms=(datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                )
            
            # Save updated alert
            await self.alert_manager.update_alert(alert)
            
            # Add action record
            if request.notes:
                action = AlertActionModel(
                    action_type="update",
                    actor=current_user,
                    description=request.notes or "Alert updated"
                )
                alert.add_action(action)
            
            # Schedule background tasks
            background_tasks.add_task(self._handle_alert_update_background, alert_id)
            
            # Send real-time notification
            await self._broadcast_alert_event("alert.updated", alert.dict())
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return AlertResponse(
                success=True,
                alert=alert,
                message="Alert updated successfully",
                processing_time_ms=processing_time
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update alert {alert_id}: {e}")
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return AlertResponse(
                success=False,
                message=f"Failed to update alert: {alert_id}",
                processing_time_ms=processing_time,
                errors=[str(e)]
            )

    async def search_alerts(
        self,
        request: AlertSearchRequest,
        current_user: str = Depends(get_current_user)
    ) -> AlertListResponse:
        """Search alerts with filters and pagination."""        start_time = datetime.now(timezone.utc)
        
        try:
            # Build search filters
            filters = {}
            
            if request.severity:
                filters["severity"] = [s.value for s in request.severity]
            if request.status:
                filters["status"] = [s.value for s in request.status]
            if request.category:
                filters["category"] = [c.value for c in request.category]
            if request.date_from:
                filters["date_from"] = request.date_from
            if request.date_to:
                filters["date_to"] = request.date_to
            if request.content_owner:
                filters["content_owner"] = request.content_owner
            if request.source_platform:
                filters["source_platform"] = request.source_platform
            if request.assigned_to:
                filters["assigned_to"] = request.assigned_to
            if request.text_search:
                filters["text_search"] = request.text_search
            
            # Add pagination
            filters["limit"] = request.limit
            filters["offset"] = request.offset
            filters["sort_by"] = request.sort_by
            filters["sort_order"] = request.sort_order
            
            # Execute search
            alerts, total_count = await self.alert_manager.search_alerts(filters)
            
            # Calculate pagination info
            page_count = (total_count + request.limit - 1) // request.limit
            current_page = (request.offset // request.limit) + 1
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return AlertListResponse(
                alerts=alerts,
                total_count=total_count,
                page_count=page_count,
                current_page=current_page,
                filters_applied=filters,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Failed to search alerts: {e}")
            raise HTTPException(status_code=500, detail="Alert search failed")

    async def bulk_alert_actions(
        self,
        request: BulkAlertActionRequest,
        background_tasks: BackgroundTasks,
        current_user: str = Depends(get_current_user)
    ) -> BulkOperationResult:
        """Perform bulk actions on multiple alerts."""        try:
            if request.action == "acknowledge":
                result = await self.alert_manager.bulk_acknowledge_alerts(
                    request.alert_ids, request.actor
                )
            elif request.action == "resolve":
                if not request.resolution:
                    raise HTTPException(status_code=400, detail="Resolution required for resolve action")
                result = await self.alert_manager.bulk_resolve_alerts(
                    request.alert_ids, request.resolution, request.actor
                )
            elif request.action == "escalate":
                if not request.escalation_level:
                    raise HTTPException(status_code=400, detail="Escalation level required")
                # Implement bulk escalation
                result = await self._bulk_escalate_alerts(
                    request.alert_ids, request.escalation_level, request.notes or "Bulk escalation", request.actor
                )
            elif request.action == "assign":
                if not request.assigned_to:
                    raise HTTPException(status_code=400, detail="Assignee required for assign action")
                # Implement bulk assignment
                result = await self._bulk_assign_alerts(
                    request.alert_ids, request.assigned_to, request.actor
                )
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported action: {request.action}")
            
            # Schedule background notifications
            background_tasks.add_task(
                self._handle_bulk_action_background, 
                request.action, 
                result.successful_items
            )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to perform bulk action {request.action}: {e}")
            raise HTTPException(status_code=500, detail="Bulk operation failed")

    async def get_alert_statistics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        current_user: str = Depends(get_current_user)
    ) -> AlertStatisticsResponse:
        """Get comprehensive alert statistics and metrics."""        try:
            # Get basic statistics
            stats = await self.alert_manager.get_alert_statistics()
            
            # Get dashboard metrics
            dashboard_metrics = await self.dashboard_service.get_dashboard_metrics()
            
            # Get trend data
            trends = await self.dashboard_service.get_trend_analysis(date_from, date_to)
            
            # Get performance metrics
            performance = await self.dashboard_service.get_performance_metrics()
            
            return AlertStatisticsResponse(
                statistics=dashboard_metrics,
                trends=trends,
                performance_metrics=performance,
                last_updated=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Failed to get alert statistics: {e}")
            raise HTTPException(status_code=500, detail="Statistics retrieval failed")

    async def websocket_endpoint(self, websocket: WebSocket, user_id: str):
        """WebSocket endpoint for real-time alert updates."""        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                
                # Handle subscription management
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    # Handle subscription to specific alert types or categories
                    await self._handle_websocket_subscription(user_id, message)
                    
        except WebSocketDisconnect:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
            logger.info(f"WebSocket connection closed for user: {user_id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            if user_id in self.active_connections:
                del self.active_connections[user_id]

    # Background task handlers
    async def _handle_new_alert_background(self, alert_id: str):
        """Handle background tasks for new alerts."""        try:
            # Trigger ML classification
            alert = await self.alert_manager.get_alert(alert_id)
            if alert:
                classification = await self.ml_classifier.classify_alert(alert)
                
                # Update alert with ML insights
                if classification.predicted_class != alert.category.value:
                    # Consider reclassification if confidence is high
                    if classification.confidence_score > 0.8:
                        await self._suggest_reclassification(alert, classification)
                
                # Trigger evidence collection if needed
                if alert.source_url:
                    await self.evidence_collector.collect_evidence(alert)
                
                # Check for auto-escalation conditions
                await self.escalation_engine.check_escalation_triggers(alert)
        
        except Exception as e:
            logger.error(f"Background task failed for alert {alert_id}: {e}")

    async def _handle_alert_update_background(self, alert_id: str):
        """Handle background tasks for alert updates."""        try:
            # Update metrics
            await self.metrics_collector.record_alert_update(alert_id)
            
            # Check if escalation is needed
            alert = await self.alert_manager.get_alert(alert_id)
            if alert:
                await self.escalation_engine.evaluate_escalation(alert)
        
        except Exception as e:
            logger.error(f"Background update task failed for alert {alert_id}: {e}")

    async def _handle_bulk_action_background(self, action: str, alert_ids: List[str]):
        """Handle background tasks for bulk actions."""        try:
            # Update metrics for bulk operations
            await self.metrics_collector.record_bulk_operation(action, len(alert_ids))
            
            # Send notifications if needed
            if action in ["resolve", "escalate"]:
                await self._send_bulk_action_notifications(action, alert_ids)
        
        except Exception as e:
            logger.error(f"Background bulk action task failed: {e}")

    async def _broadcast_alert_event(self, event_type: str, alert_data: Dict[str, Any]):
        """Broadcast alert events to connected WebSocket clients."""        if not self.active_connections:
            return
        
        message = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": alert_data
        }
        
        # Send to all connected clients
        disconnected_clients = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message to {user_id}: {e}")
                disconnected_clients.append(user_id)
        
        # Clean up disconnected clients
        for user_id in disconnected_clients:
            del self.active_connections[user_id]

    async def _handle_websocket_subscription(self, user_id: str, message: Dict[str, Any]):
        """Handle WebSocket subscription management."""        # Implementation for subscription management
        # Users can subscribe to specific alert types, categories, or severity levels
        pass

    async def _suggest_reclassification(self, alert: ContentProtectionAlert, classification: MLClassificationResult):
        """Suggest alert reclassification based on ML analysis."""        # Implementation for ML-based reclassification suggestions
        pass

    async def _bulk_escalate_alerts(self, alert_ids: List[str], level: EscalationLevel, reason: str, actor: str) -> BulkOperationResult:
        """Perform bulk escalation of alerts."""        successful = []
        failed = []
        
        for alert_id in alert_ids:
            try:
                alert = await self.alert_manager.get_alert(alert_id)
                if alert:
                    alert.escalate(level, reason, actor)
                    await self.alert_manager.update_alert(alert)
                    successful.append(alert_id)
            except Exception as e:
                failed.append({"alert_id": alert_id, "error": str(e)})
        
        return BulkOperationResult(
            total_processed=len(alert_ids),
            successful_count=len(successful),
            failed_count=len(failed),
            successful_items=successful,
            failed_items=failed
        )

    async def _bulk_assign_alerts(self, alert_ids: List[str], assigned_to: str, actor: str) -> BulkOperationResult:
        """Perform bulk assignment of alerts."""        successful = []
        failed = []
        
        for alert_id in alert_ids:
            try:
                alert = await self.alert_manager.get_alert(alert_id)
                if alert:
                    alert.assigned_to = assigned_to
                    action = AlertActionModel(
                        action_type="assignment",
                        actor=actor,
                        description=f"Assigned to {assigned_to}"
                    )
                    alert.add_action(action)
                    await self.alert_manager.update_alert(alert)
                    successful.append(alert_id)
            except Exception as e:
                failed.append({"alert_id": alert_id, "error": str(e)})
        
        return BulkOperationResult(
            total_processed=len(alert_ids),
            successful_count=len(successful),
            failed_count=len(failed),
            successful_items=successful,
            failed_items=failed
        )

    async def _send_bulk_action_notifications(self, action: str, alert_ids: List[str]):
        """Send notifications for bulk actions."""        # Implementation for bulk action notifications
        pass


# FastAPI app instance and route registration
def create_alert_api_app(alert_system: AlertSystemAPI) -> FastAPI:
    """Create and configure the FastAPI application for the alert system."""    
    app = FastAPI(
        title="Content Protection Alert System API",
        description="Enterprise-grade alert management for content protection",
        version="2.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    @app.post("/alerts", response_model=AlertResponse)
    async def create_alert(
        request: CreateAlertRequest,
        background_tasks: BackgroundTasks,
        current_user: str = Depends(get_current_user)
    ):
        return await alert_system.create_alert(request, background_tasks, current_user)
    
    @app.get("/alerts/{alert_id}", response_model=AlertResponse)
    async def get_alert(
        alert_id: str,
        current_user: str = Depends(get_current_user)
    ):
        return await alert_system.get_alert(alert_id, current_user)
    
    @app.put("/alerts/{alert_id}", response_model=AlertResponse)
    async def update_alert(
        alert_id: str,
        request: UpdateAlertRequest,
        background_tasks: BackgroundTasks,
        current_user: str = Depends(get_current_user)
    ):
        return await alert_system.update_alert(alert_id, request, background_tasks, current_user)
    
    @app.post("/alerts/search", response_model=AlertListResponse)
    async def search_alerts(
        request: AlertSearchRequest,
        current_user: str = Depends(get_current_user)
    ):
        return await alert_system.search_alerts(request, current_user)
    
    @app.post("/alerts/bulk-actions", response_model=BulkOperationResult)
    async def bulk_alert_actions(
        request: BulkAlertActionRequest,
        background_tasks: BackgroundTasks,
        current_user: str = Depends(get_current_user)
    ):
        return await alert_system.bulk_alert_actions(request, background_tasks, current_user)
    
    @app.get("/alerts/statistics", response_model=AlertStatisticsResponse)
    async def get_alert_statistics(
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        current_user: str = Depends(get_current_user)
    ):
        return await alert_system.get_alert_statistics(date_from, date_to, current_user)
    
    @app.websocket("/ws/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        await alert_system.websocket_endpoint(websocket, user_id)
    
    return app


# Module export
__all__ = [
    "AlertSystemAPI",
    "CreateAlertRequest", 
    "UpdateAlertRequest",
    "AlertSearchRequest",
    "BulkAlertActionRequest",
    "AlertResponse",
    "AlertListResponse", 
    "AlertStatisticsResponse",
    "create_alert_api_app"
]
