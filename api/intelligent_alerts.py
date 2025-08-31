"""🚨 API Integration Example for Intelligent Alert System
======================================================

Example showing how to integrate the new intelligent alert system
with the existing Ainflue API infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel

# Import the intelligent alert system
from ..monitoring.alerts import (
    alert_coordinator,
    BusinessMetrics,
    TechnicalMetrics,
    ModelMetrics,
    SecurityEvent,
    AlertCategory,
    AlertSeverity,
    SystemHealthStatus,
    AIModelType,
    SecurityThreatLevel
)

# Create API router
router = APIRouter(prefix="/api/v1/alerts", tags=["Intelligent Alerts"])


# Pydantic models for API requests
class BusinessMetricsRequest(BaseModel):
    """Request model for business metrics"""    current_revenue: float
    previous_revenue: float
    daily_revenue: List[float]
    weekly_revenue: List[float]
    active_users: int
    new_users: int
    user_retention_rate: float
    avg_session_duration: float
    bounce_rate: float
    conversion_rate: float
    payment_success_rate: float
    content_uploads: int
    user_satisfaction_score: float
    support_tickets: int
    churn_rate: float


class TechnicalMetricsRequest(BaseModel):
    """Request model for technical metrics"""    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    service_availability: float
    api_response_time: float
    error_rate: float
    throughput: float
    security_threat_score: float
    failed_logins: int
    suspicious_activities: int
    blocked_ips: int
    security_events: List[Dict[str, Any]]
    service_name: str = "ainflue-api"
    environment: str = "production"
    region: str = "default"


class ModelMetricsRequest(BaseModel):
    """Request model for AI model metrics"""    model_id: str
    model_name: str
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    inference_latency_p50: float
    inference_latency_p95: float
    inference_latency_p99: float
    throughput: float
    error_rate: float
    data_drift_score: float
    concept_drift_score: float
    prediction_drift_score: float
    cpu_usage: float
    memory_usage: float
    gpu_utilization: float
    data_quality_score: float
    missing_values_ratio: float
    outlier_ratio: float
    prediction_confidence: float
    business_impact_score: float
    environment: str = "production"
    version: str = "1.0.0"


class SecurityEventRequest(BaseModel):
    """Request model for security events"""    event_type: str
    threat_level: str
    source_ip: str
    target_resource: str
    description: str
    metadata: Dict[str, Any]
    blocked: bool = False


# API Endpoints

@router.post("/evaluate/business")
async def evaluate_business_metrics(metrics: BusinessMetricsRequest):
    """    Evaluate business metrics and trigger alerts
    
    This endpoint processes business metrics such as revenue, user engagement,
    and payment processing to detect anomalies and trigger appropriate alerts.
    """    try:
        # Convert request to BusinessMetrics
        business_metrics = BusinessMetrics(
            timestamp=datetime.utcnow(),
            current_revenue=metrics.current_revenue,
            previous_revenue=metrics.previous_revenue,
            daily_revenue=metrics.daily_revenue,
            weekly_revenue=metrics.weekly_revenue,
            active_users=metrics.active_users,
            new_users=metrics.new_users,
            user_retention_rate=metrics.user_retention_rate,
            avg_session_duration=metrics.avg_session_duration,
            bounce_rate=metrics.bounce_rate,
            conversion_rate=metrics.conversion_rate,
            payment_success_rate=metrics.payment_success_rate,
            content_uploads=metrics.content_uploads,
            user_satisfaction_score=metrics.user_satisfaction_score,
            support_tickets=metrics.support_tickets,
            churn_rate=metrics.churn_rate
        )
        
        # Evaluate through alert coordinator
        result = await alert_coordinator.evaluate_all_metrics(business_metrics=business_metrics)
        
        return {
            "status": "success",
            "evaluation_timestamp": result.timestamp.isoformat(),
            "system_health": result.system_health.value,
            "alerts_triggered": result.total_active_alerts,
            "alerts_by_category": result.alerts_by_category,
            "business_health": result.business_health,
            "trending_issues": result.trending_issues,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating business metrics: {str(e)}")


@router.post("/evaluate/technical")
async def evaluate_technical_metrics(metrics: TechnicalMetricsRequest):
    """    Evaluate technical metrics and trigger alerts
    
    This endpoint processes infrastructure and security metrics to detect
    system issues, performance problems, and security threats.
    """    try:
        # Convert request to TechnicalMetrics
        technical_metrics = TechnicalMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage=metrics.cpu_usage,
            memory_usage=metrics.memory_usage,
            disk_usage=metrics.disk_usage,
            network_latency=metrics.network_latency,
            service_availability=metrics.service_availability,
            api_response_time=metrics.api_response_time,
            error_rate=metrics.error_rate,
            throughput=metrics.throughput,
            security_threat_score=metrics.security_threat_score,
            failed_logins=metrics.failed_logins,
            suspicious_activities=metrics.suspicious_activities,
            blocked_ips=metrics.blocked_ips,
            security_events=metrics.security_events,
            service_name=metrics.service_name,
            environment=metrics.environment,
            region=metrics.region
        )
        
        # Evaluate through alert coordinator
        result = await alert_coordinator.evaluate_all_metrics(technical_metrics=technical_metrics)
        
        return {
            "status": "success",
            "evaluation_timestamp": result.timestamp.isoformat(),
            "system_health": result.system_health.value,
            "alerts_triggered": result.total_active_alerts,
            "alerts_by_category": result.alerts_by_category,
            "technical_health": result.technical_health,
            "trending_issues": result.trending_issues,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating technical metrics: {str(e)}")


@router.post("/evaluate/ai")
async def evaluate_ai_metrics(metrics: List[ModelMetricsRequest]):
    """    Evaluate AI/ML model metrics and trigger alerts
    
    This endpoint processes AI model performance metrics to detect
    model drift, accuracy degradation, and operational issues.
    """    try:
        # Convert requests to ModelMetrics
        ai_metrics = []
        for metric_req in metrics:
            model_metrics = ModelMetrics(
                model_id=metric_req.model_id,
                model_name=metric_req.model_name,
                model_type=AIModelType(metric_req.model_type),
                timestamp=datetime.utcnow(),
                accuracy=metric_req.accuracy,
                precision=metric_req.precision,
                recall=metric_req.recall,
                f1_score=metric_req.f1_score,
                auc_roc=metric_req.auc_roc,
                inference_latency_p50=metric_req.inference_latency_p50,
                inference_latency_p95=metric_req.inference_latency_p95,
                inference_latency_p99=metric_req.inference_latency_p99,
                throughput=metric_req.throughput,
                error_rate=metric_req.error_rate,
                data_drift_score=metric_req.data_drift_score,
                concept_drift_score=metric_req.concept_drift_score,
                prediction_drift_score=metric_req.prediction_drift_score,
                cpu_usage=metric_req.cpu_usage,
                memory_usage=metric_req.memory_usage,
                gpu_utilization=metric_req.gpu_utilization,
                data_quality_score=metric_req.data_quality_score,
                missing_values_ratio=metric_req.missing_values_ratio,
                outlier_ratio=metric_req.outlier_ratio,
                prediction_confidence=metric_req.prediction_confidence,
                business_impact_score=metric_req.business_impact_score,
                environment=metric_req.environment,
                version=metric_req.version
            )
            ai_metrics.append(model_metrics)
        
        # Evaluate through alert coordinator
        result = await alert_coordinator.evaluate_all_metrics(ai_metrics=ai_metrics)
        
        return {
            "status": "success",
            "evaluation_timestamp": result.timestamp.isoformat(),
            "system_health": result.system_health.value,
            "alerts_triggered": result.total_active_alerts,
            "alerts_by_category": result.alerts_by_category,
            "ai_health": result.ai_health,
            "models_evaluated": len(ai_metrics),
            "trending_issues": result.trending_issues,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating AI metrics: {str(e)}")


@router.post("/evaluate/comprehensive")
async def evaluate_comprehensive_metrics(
    business_metrics: Optional[BusinessMetricsRequest] = None,
    technical_metrics: Optional[TechnicalMetricsRequest] = None,
    ai_metrics: Optional[List[ModelMetricsRequest]] = None
):
    """    Comprehensive evaluation across all metric categories
    
    This endpoint provides unified evaluation across business, technical,
    and AI metrics with cross-category correlation analysis.
    """    try:
        # Convert requests to metric objects
        business_data = None
        if business_metrics:
            business_data = BusinessMetrics(
                timestamp=datetime.utcnow(),
                current_revenue=business_metrics.current_revenue,
                previous_revenue=business_metrics.previous_revenue,
                daily_revenue=business_metrics.daily_revenue,
                weekly_revenue=business_metrics.weekly_revenue,
                active_users=business_metrics.active_users,
                new_users=business_metrics.new_users,
                user_retention_rate=business_metrics.user_retention_rate,
                avg_session_duration=business_metrics.avg_session_duration,
                bounce_rate=business_metrics.bounce_rate,
                conversion_rate=business_metrics.conversion_rate,
                payment_success_rate=business_metrics.payment_success_rate,
                content_uploads=business_metrics.content_uploads,
                user_satisfaction_score=business_metrics.user_satisfaction_score,
                support_tickets=business_metrics.support_tickets,
                churn_rate=business_metrics.churn_rate
            )
        
        technical_data = None
        if technical_metrics:
            technical_data = TechnicalMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=technical_metrics.cpu_usage,
                memory_usage=technical_metrics.memory_usage,
                disk_usage=technical_metrics.disk_usage,
                network_latency=technical_metrics.network_latency,
                service_availability=technical_metrics.service_availability,
                api_response_time=technical_metrics.api_response_time,
                error_rate=technical_metrics.error_rate,
                throughput=technical_metrics.throughput,
                security_threat_score=technical_metrics.security_threat_score,
                failed_logins=technical_metrics.failed_logins,
                suspicious_activities=technical_metrics.suspicious_activities,
                blocked_ips=technical_metrics.blocked_ips,
                security_events=technical_metrics.security_events,
                service_name=technical_metrics.service_name,
                environment=technical_metrics.environment,
                region=technical_metrics.region
            )
        
        ai_data = None
        if ai_metrics:
            ai_data = []
            for metric_req in ai_metrics:
                model_metrics = ModelMetrics(
                    model_id=metric_req.model_id,
                    model_name=metric_req.model_name,
                    model_type=AIModelType(metric_req.model_type),
                    timestamp=datetime.utcnow(),
                    accuracy=metric_req.accuracy,
                    precision=metric_req.precision,
                    recall=metric_req.recall,
                    f1_score=metric_req.f1_score,
                    auc_roc=metric_req.auc_roc,
                    inference_latency_p50=metric_req.inference_latency_p50,
                    inference_latency_p95=metric_req.inference_latency_p95,
                    inference_latency_p99=metric_req.inference_latency_p99,
                    throughput=metric_req.throughput,
                    error_rate=metric_req.error_rate,
                    data_drift_score=metric_req.data_drift_score,
                    concept_drift_score=metric_req.concept_drift_score,
                    prediction_drift_score=metric_req.prediction_drift_score,
                    cpu_usage=metric_req.cpu_usage,
                    memory_usage=metric_req.memory_usage,
                    gpu_utilization=metric_req.gpu_utilization,
                    data_quality_score=metric_req.data_quality_score,
                    missing_values_ratio=metric_req.missing_values_ratio,
                    outlier_ratio=metric_req.outlier_ratio,
                    prediction_confidence=metric_req.prediction_confidence,
                    business_impact_score=metric_req.business_impact_score,
                    environment=metric_req.environment,
                    version=metric_req.version
                )
                ai_data.append(model_metrics)
        
        # Comprehensive evaluation
        result = await alert_coordinator.evaluate_all_metrics(
            business_metrics=business_data,
            technical_metrics=technical_data,
            ai_metrics=ai_data
        )
        
        return {
            "status": "success",
            "evaluation_timestamp": result.timestamp.isoformat(),
            "system_health": result.system_health.value,
            "total_active_alerts": result.total_active_alerts,
            "alerts_by_category": result.alerts_by_category,
            "alerts_by_severity": result.alerts_by_severity,
            "subsystem_health": {
                "business": result.business_health,
                "technical": result.technical_health,
                "ai_ml": result.ai_health
            },
            "trending_issues": result.trending_issues,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in comprehensive evaluation: {str(e)}")


@router.post("/security/event")
async def process_security_event(event: SecurityEventRequest):
    """    Process a security event and trigger appropriate alerts
    
    This endpoint handles security events and triggers immediate
    security alerts based on threat level and event type.
    """    try:
        # Convert request to SecurityEvent
        security_event = SecurityEvent(
            event_id=f"sec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow(),
            event_type=event.event_type,
            threat_level=SecurityThreatLevel(event.threat_level),
            source_ip=event.source_ip,
            target_resource=event.target_resource,
            description=event.description,
            metadata=event.metadata,
            blocked=event.blocked
        )
        
        # Process through alert coordinator
        alerts = await alert_coordinator.process_security_event(security_event)
        
        return {
            "status": "success",
            "event_id": security_event.event_id,
            "alerts_triggered": len(alerts),
            "threat_level": event.threat_level,
            "action_taken": "blocked" if event.blocked else "monitored",
            "timestamp": security_event.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing security event: {str(e)}")


@router.get("/status")
async def get_comprehensive_status():
    """    Get comprehensive system status across all alert categories
    
    This endpoint provides a complete overview of system health,
    active alerts, trends, and recommendations.
    """    try:
        status = await alert_coordinator.get_comprehensive_status()
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")


@router.get("/alerts/active")
async def get_active_alerts(
    category: Optional[str] = None,
    severity: Optional[str] = None
):
    """    Get currently active alerts with optional filtering
    
    Filter by category (business, technical, ai_ml, security, infrastructure)
    and/or severity (emergency, critical, warning, info)
    """    try:
        # Parse filters
        category_filter = AlertCategory(category) if category else None
        severity_filter = AlertSeverity(severity) if severity else None
        
        # Get active alerts
        alerts = await alert_coordinator.get_active_alerts(category_filter, severity_filter)
        
        # Convert to response format
        alert_data = []
        for alert in alerts:
            alert_data.append({
                "alert_id": alert.alert_id,
                "category": alert.category.value,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "description": alert.description,
                "timestamp": alert.timestamp.isoformat(),
                "escalation_level": alert.escalation_level,
                "acknowledged": alert.acknowledged,
                "resolved": alert.resolved
            })
        
        return {
            "status": "success",
            "total_alerts": len(alert_data),
            "alerts": alert_data,
            "filters_applied": {
                "category": category,
                "severity": severity
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active alerts: {str(e)}")


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str):
    """    Acknowledge an active alert
    
    This stops the escalation process for the alert and marks it as acknowledged.
    """    try:
        result = await alert_coordinator.acknowledge_alert(alert_id, acknowledged_by)
        
        if result:
            return {
                "status": "success",
                "message": "Alert acknowledged successfully",
                "alert_id": alert_id,
                "acknowledged_by": acknowledged_by,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Alert not found or already acknowledged")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """    Resolve an active alert
    
    This marks the alert as resolved and removes it from active alerts.
    """    try:
        result = await alert_coordinator.resolve_alert(alert_id, auto_resolved=False)
        
        if result:
            return {
                "status": "success",
                "message": "Alert resolved successfully",
                "alert_id": alert_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Alert not found or already resolved")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving alert: {str(e)}")


@router.get("/health")
async def health_check():
    """    Health check endpoint for the intelligent alert system
    """    try:
        # Quick health check
        status = await alert_coordinator.get_comprehensive_status()
        
        return {
            "status": "healthy",
            "alert_system": status.get("coordinator_status", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Example usage in main API app:
"""from fastapi import FastAPI
from api.intelligent_alerts import router as alerts_router

app = FastAPI()
app.include_router(alerts_router)
"""