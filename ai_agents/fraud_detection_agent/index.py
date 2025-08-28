"""
Fraud Detection Agent - Main Entry Point and API Interface

Central index file providing unified API access to all fraud detection
capabilities with enterprise-grade routing and request handling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import redis.asyncio as aioredis
from sqlalchemy.orm import Session

from .core import FraudDetectionAgent
from .behavioral_analyzer import BehaviorAnalyzer
from .pattern_detector import PatternDetector
from .revenue_validator import RevenueValidator
from .deepfake_detector import DeepfakeDetector
from .anomaly_engine import AnomalyDetectionEngine
from .threat_intelligence import ThreatIntelligenceEngine

from ...core.config import get_settings
from ...core.database import get_db_session, get_redis_client
from ...core.security import verify_api_token, get_current_user
from ...core.monitoring import MetricsCollector
from ...core.exceptions import (
    FraudDetectionError,
    BehaviorAnalysisError,
    PatternDetectionError,
    RevenueValidationError,
    DeepfakeDetectionError,
    AnomalyDetectionError,
    ThreatIntelligenceError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()
settings = get_settings()

# FastAPI application
app = FastAPI(
    title="IA-Influencer Fraud Detection API",
    description="Advanced fraud detection system with multi-layered security analysis",
    version="1.0.0",
    docs_url="/fraud/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/fraud/redoc" if settings.ENVIRONMENT == "development" else None,
    openapi_url="/fraud/openapi.json" if settings.ENVIRONMENT == "development" else None
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global instances
fraud_detection_agent: Optional[FraudDetectionAgent] = None
metrics_collector = MetricsCollector("fraud_detection")

class AnalysisType(str, Enum):
    """Types of fraud analysis available"""
    COMPREHENSIVE = "comprehensive"
    BEHAVIORAL = "behavioral"
    PATTERN = "pattern"
    REVENUE = "revenue"
    DEEPFAKE = "deepfake"
    ANOMALY = "anomaly"
    THREAT_INTELLIGENCE = "threat_intelligence"

class RiskLevel(str, Enum):
    """Risk assessment levels"""
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"

# Request/Response Models
class GeolocationData(BaseModel):
    """Geolocation information"""
    ip_address: str = Field(..., description="IP address of the user")
    country_code: Optional[str] = Field(None, description="ISO country code")
    country: Optional[str] = Field(None, description="Country name")
    city: Optional[str] = Field(None, description="City name")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    timezone: Optional[str] = Field(None, description="Timezone identifier")

class SessionData(BaseModel):
    """User session information"""
    ip_address: str = Field(..., description="User IP address")
    user_agent: str = Field(..., description="User agent string")
    geolocation: GeolocationData = Field(..., description="Geolocation data")
    device_fingerprint: str = Field(..., description="Device fingerprint hash")
    session_id: Optional[str] = Field(None, description="Session identifier")
    referrer: Optional[str] = Field(None, description="HTTP referrer")

class ContentData(BaseModel):
    """Content information for deepfake analysis"""
    content_type: str = Field(..., description="Type of content (video, audio, image, text)")
    content_url: Optional[str] = Field(None, description="URL to content")
    content_base64: Optional[str] = Field(None, description="Base64 encoded content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ['video', 'audio', 'image', 'text']
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of: {allowed_types}')
        return v

class TransactionData(BaseModel):
    """Financial transaction information"""
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code (ISO 4217)")
    payment_method: str = Field(..., description="Payment method used")
    transaction_id: Optional[str] = Field(None, description="Transaction identifier")
    merchant_id: Optional[str] = Field(None, description="Merchant identifier")
    timestamp: Optional[datetime] = Field(None, description="Transaction timestamp")

class BehavioralData(BaseModel):
    """Behavioral analysis data"""
    mouse_movements: Optional[List[Dict[str, float]]] = Field(None, description="Mouse movement data")
    keystrokes: Optional[List[Dict[str, Any]]] = Field(None, description="Keystroke timing data")
    scroll_patterns: Optional[List[Dict[str, float]]] = Field(None, description="Scroll behavior data")
    click_patterns: Optional[List[Dict[str, Any]]] = Field(None, description="Click behavior data")
    session_duration: Optional[int] = Field(None, description="Session duration in seconds")

class FraudAnalysisRequest(BaseModel):
    """Comprehensive fraud analysis request"""
    user_id: str = Field(..., description="Unique user identifier")
    analysis_type: AnalysisType = Field(AnalysisType.COMPREHENSIVE, description="Type of analysis to perform")
    session_data: SessionData = Field(..., description="User session information")
    content_data: Optional[ContentData] = Field(None, description="Content for analysis")
    transaction_data: Optional[TransactionData] = Field(None, description="Transaction information")
    behavioral_data: Optional[BehavioralData] = Field(None, description="Behavioral analysis data")
    platform: str = Field(..., description="Platform name (instagram, tiktok, youtube, etc.)")
    additional_context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")

class FraudIndicator(BaseModel):
    """Individual fraud indicator"""
    indicator_type: str = Field(..., description="Type of fraud indicator")
    severity: str = Field(..., description="Severity level (LOW, MEDIUM, HIGH, CRITICAL)")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    description: str = Field(..., description="Human-readable description")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting evidence")
    recommended_action: Optional[str] = Field(None, description="Recommended action")

class FraudAnalysisResponse(BaseModel):
    """Comprehensive fraud analysis response"""
    user_id: str = Field(..., description="User identifier")
    analysis_id: str = Field(..., description="Unique analysis identifier")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    fraud_score: float = Field(..., description="Overall fraud score (0.0 to 1.0)")
    risk_level: RiskLevel = Field(..., description="Risk assessment level")
    fraud_indicators: List[FraudIndicator] = Field(..., description="List of detected fraud indicators")
    analysis_details: Dict[str, Any] = Field(..., description="Detailed analysis results")
    recommended_actions: List[str] = Field(..., description="Recommended security actions")
    processing_time_ms: int = Field(..., description="Analysis processing time in milliseconds")

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Service version")
    components: Dict[str, str] = Field(..., description="Component status")

@app.on_event("startup")
async def startup_event():
    """Initialize fraud detection system on startup"""
    global fraud_detection_agent
    
    try:
        # Initialize Redis client
        redis_client = await get_redis_client()
        
        # Initialize database session
        db_session = get_db_session()
        
        # Initialize fraud detection agent
        fraud_detection_agent = FraudDetectionAgent(
            redis_client=redis_client,
            db_session=db_session
        )
        
        # Initialize metrics collection
        await metrics_collector.initialize()
        
        logger.info("Fraud Detection System initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Fraud Detection System: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global fraud_detection_agent
    
    try:
        if fraud_detection_agent:
            await fraud_detection_agent.cleanup()
            
        await metrics_collector.cleanup()
        
        logger.info("Fraud Detection System shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# Health check endpoint
@app.get("/fraud/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        components = {
            "fraud_agent": "healthy" if fraud_detection_agent else "unhealthy",
            "redis": "healthy",  # Would check actual Redis connection
            "database": "healthy",  # Would check actual DB connection
            "metrics": "healthy" if metrics_collector else "unhealthy"
        }
        
        overall_status = "healthy" if all(status == "healthy" for status in components.values()) else "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now(),
            version="1.0.0",
            components=components
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Main fraud analysis endpoint
@app.post("/fraud/analyze", response_model=FraudAnalysisResponse)
async def analyze_fraud(
    request: FraudAnalysisRequest,
    background_tasks: BackgroundTasks,
    token: HTTPAuthorizationCredentials = Depends(security),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Comprehensive fraud analysis endpoint
    
    Performs multi-layered fraud detection analysis including:
    - Behavioral pattern analysis
    - Known fraud pattern detection
    - Financial transaction validation
    - AI-generated content detection
    - Statistical anomaly detection
    - Threat intelligence assessment
    """
    if not fraud_detection_agent:
        raise HTTPException(status_code=503, detail="Fraud detection service unavailable")
    
    start_time = datetime.now()
    analysis_id = f"fraud_analysis_{request.user_id}_{int(start_time.timestamp())}"
    
    try:
        # Verify API token
        await verify_api_token(token.credentials)
        
        # Log analysis request
        logger.info(f"Starting fraud analysis {analysis_id} for user {request.user_id}")
        
        # Record metrics
        await metrics_collector.increment("fraud_analysis_requests", 
                                         tags={"platform": request.platform, "analysis_type": request.analysis_type})
        
        # Prepare analysis data
        session_dict = request.session_data.dict()
        content_dict = request.content_data.dict() if request.content_data else None
        transaction_dict = request.transaction_data.dict() if request.transaction_data else None
        behavioral_dict = request.behavioral_data.dict() if request.behavioral_data else None
        
        # Perform fraud analysis based on type
        if request.analysis_type == AnalysisType.COMPREHENSIVE:
            analysis_result = await fraud_detection_agent.analyze_fraud_comprehensive(
                user_id=request.user_id,
                session_data=session_dict,
                content_data=content_dict,
                transaction_data=transaction_dict,
                behavioral_data=behavioral_dict,
                platform=request.platform,
                additional_context=request.additional_context
            )
        elif request.analysis_type == AnalysisType.BEHAVIORAL:
            analysis_result = await fraud_detection_agent.behavioral_analyzer.analyze_behavior(
                user_id=request.user_id,
                behavioral_data=behavioral_dict or session_dict
            )
        elif request.analysis_type == AnalysisType.PATTERN:
            analysis_result = await fraud_detection_agent.pattern_detector.detect_patterns(
                user_id=request.user_id,
                session_data=session_dict,
                platform=request.platform
            )
        elif request.analysis_type == AnalysisType.REVENUE:
            if not transaction_dict:
                raise HTTPException(status_code=400, detail="Transaction data required for revenue analysis")
            analysis_result = await fraud_detection_agent.revenue_validator.validate_revenue(
                user_id=request.user_id,
                revenue_data=transaction_dict,
                platform=request.platform
            )
        elif request.analysis_type == AnalysisType.DEEPFAKE:
            if not content_dict:
                raise HTTPException(status_code=400, detail="Content data required for deepfake analysis")
            analysis_result = await fraud_detection_agent.deepfake_detector.analyze_content(
                content_data=content_dict
            )
        elif request.analysis_type == AnalysisType.ANOMALY:
            analysis_result = await fraud_detection_agent.anomaly_engine.detect_anomalies(
                user_id=request.user_id,
                data_points=session_dict,
                platform=request.platform
            )
        elif request.analysis_type == AnalysisType.THREAT_INTELLIGENCE:
            analysis_result = await fraud_detection_agent.threat_intelligence.analyze_threats(
                user_id=request.user_id,
                geolocation=session_dict.get('geolocation', {}),
                device_fingerprint=session_dict.get('device_fingerprint', ''),
                platform=request.platform,
                additional_context=request.additional_context
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
            
        # Calculate processing time
        end_time = datetime.now()
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Convert analysis result to response format
        fraud_indicators = []
        for indicator in analysis_result.get('fraud_indicators', []):
            fraud_indicators.append(FraudIndicator(
                indicator_type=indicator.get('type', 'unknown'),
                severity=indicator.get('severity', 'LOW'),
                confidence=indicator.get('confidence', 0.0),
                description=indicator.get('description', 'No description available'),
                evidence=indicator.get('evidence', {}),
                recommended_action=indicator.get('recommended_action')
            ))
            
        # Determine risk level
        fraud_score = analysis_result.get('fraud_score', 0.0)
        if fraud_score >= 0.8:
            risk_level = RiskLevel.RED
        elif fraud_score >= 0.6:
            risk_level = RiskLevel.ORANGE
        elif fraud_score >= 0.4:
            risk_level = RiskLevel.YELLOW
        else:
            risk_level = RiskLevel.GREEN
            
        response = FraudAnalysisResponse(
            user_id=request.user_id,
            analysis_id=analysis_id,
            timestamp=end_time,
            fraud_score=fraud_score,
            risk_level=risk_level,
            fraud_indicators=fraud_indicators,
            analysis_details=analysis_result,
            recommended_actions=analysis_result.get('recommended_actions', []),
            processing_time_ms=processing_time_ms
        )
        
        # Log successful analysis
        logger.info(f"Fraud analysis {analysis_id} completed: score={fraud_score:.3f}, risk={risk_level}, time={processing_time_ms}ms")
        
        # Record success metrics
        await metrics_collector.increment("fraud_analysis_success", 
                                         tags={"platform": request.platform, "risk_level": risk_level})
        await metrics_collector.histogram("fraud_analysis_duration", processing_time_ms,
                                         tags={"platform": request.platform})
        
        # Schedule background tasks
        background_tasks.add_task(
            _post_analysis_tasks,
            analysis_id=analysis_id,
            user_id=request.user_id,
            analysis_result=analysis_result,
            risk_level=risk_level
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fraud analysis {analysis_id} failed: {str(e)}")
        
        # Record error metrics
        await metrics_collector.increment("fraud_analysis_errors", 
                                         tags={"platform": request.platform, "error_type": type(e).__name__})
        
        raise HTTPException(status_code=500, detail=f"Fraud analysis failed: {str(e)}")

# Batch analysis endpoint
@app.post("/fraud/analyze/batch")
async def analyze_fraud_batch(
    requests: List[FraudAnalysisRequest],
    background_tasks: BackgroundTasks,
    token: HTTPAuthorizationCredentials = Depends(security),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Batch fraud analysis endpoint for processing multiple requests
    """
    if not fraud_detection_agent:
        raise HTTPException(status_code=503, detail="Fraud detection service unavailable")
        
    if len(requests) > 100:  # Limit batch size
        raise HTTPException(status_code=400, detail="Batch size exceeds maximum limit of 100")
    
    try:
        # Verify API token
        await verify_api_token(token.credentials)
        
        # Process requests in parallel
        batch_tasks = []
        for request in requests:
            task = analyze_fraud_single(request)
            batch_tasks.append(task)
            
        results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    'request_index': i,
                    'user_id': requests[i].user_id,
                    'error': str(result)
                })
            else:
                successful_results.append(result)
                
        return {
            'batch_id': f"batch_{int(datetime.now().timestamp())}",
            'total_requests': len(requests),
            'successful_analyses': len(successful_results),
            'failed_analyses': len(failed_results),
            'results': successful_results,
            'errors': failed_results
        }
        
    except Exception as e:
        logger.error(f"Batch fraud analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

async def analyze_fraud_single(request: FraudAnalysisRequest) -> Dict[str, Any]:
    """Process a single fraud analysis request (internal helper)"""
    try:
        # Similar logic to main analyze_fraud endpoint but simplified for batch processing
        session_dict = request.session_data.dict()
        
        analysis_result = await fraud_detection_agent.analyze_fraud_comprehensive(
            user_id=request.user_id,
            session_data=session_dict,
            content_data=request.content_data.dict() if request.content_data else None,
            transaction_data=request.transaction_data.dict() if request.transaction_data else None,
            behavioral_data=request.behavioral_data.dict() if request.behavioral_data else None,
            platform=request.platform,
            additional_context=request.additional_context
        )
        
        return {
            'user_id': request.user_id,
            'fraud_score': analysis_result.get('fraud_score', 0.0),
            'risk_level': analysis_result.get('risk_level', 'GREEN'),
            'indicators_count': len(analysis_result.get('fraud_indicators', [])),
            'processing_status': 'success'
        }
        
    except Exception as e:
        logger.error(f"Single fraud analysis failed for user {request.user_id}: {str(e)}")
        raise

# Statistics endpoint
@app.get("/fraud/statistics")
async def get_fraud_statistics(
    days: int = 7,
    token: HTTPAuthorizationCredentials = Depends(security),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get fraud detection statistics"""
    try:
        await verify_api_token(token.credentials)
        
        # Get statistics from various components
        stats = {
            'period_days': days,
            'timestamp': datetime.now(),
            'behavioral_stats': await fraud_detection_agent.behavioral_analyzer.get_statistics(days),
            'pattern_stats': await fraud_detection_agent.pattern_detector.get_statistics(days),
            'revenue_stats': await fraud_detection_agent.revenue_validator.get_statistics(days),
            'deepfake_stats': await fraud_detection_agent.deepfake_detector.get_statistics(days),
            'anomaly_stats': await fraud_detection_agent.anomaly_engine.get_statistics(days),
            'threat_stats': await fraud_detection_agent.threat_intelligence.get_threat_statistics(days)
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get fraud statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

async def _post_analysis_tasks(
    analysis_id: str,
    user_id: str,
    analysis_result: Dict[str, Any],
    risk_level: RiskLevel
):
    """Background tasks to run after fraud analysis"""
    try:
        # Update user risk profile
        await _update_user_risk_profile(user_id, analysis_result, risk_level)
        
        # Send alerts for high-risk cases
        if risk_level in [RiskLevel.RED, RiskLevel.ORANGE]:
            await _send_fraud_alert(analysis_id, user_id, analysis_result, risk_level)
            
        # Update fraud detection models with new data
        await _update_detection_models(analysis_result)
        
        # Archive analysis results
        await _archive_analysis_results(analysis_id, user_id, analysis_result)
        
    except Exception as e:
        logger.error(f"Post-analysis tasks failed for {analysis_id}: {str(e)}")

async def _update_user_risk_profile(user_id: str, analysis_result: Dict[str, Any], risk_level: RiskLevel):
    """Update user risk profile based on analysis"""
    try:
        logger.info(f"Updating risk profile for user {user_id} with risk level {risk_level.value}")
        
        # Extract risk factors from analysis
        risk_factors = analysis_result.get('risk_factors', {})
        risk_score = analysis_result.get('risk_score', 0.0)
        
        # Build risk profile update
        risk_profile_update = {
            "user_id": user_id,
            "current_risk_level": risk_level.value,
            "risk_score": risk_score,
            "last_assessment": datetime.utcnow().isoformat(),
            "risk_factors": {
                "behavioral_anomalies": risk_factors.get('behavioral_anomalies', 0.0),
                "transaction_patterns": risk_factors.get('transaction_patterns', 0.0),
                "engagement_metrics": risk_factors.get('engagement_metrics', 0.0),
                "content_violations": risk_factors.get('content_violations', 0.0),
                "account_age_factor": risk_factors.get('account_age_factor', 0.0)
            },
            "history": {
                "total_assessments": risk_factors.get('total_assessments', 1),
                "trend": "increasing" if risk_score > 0.5 else "stable" if risk_score > 0.3 else "decreasing",
                "previous_risk_level": risk_factors.get('previous_risk_level', 'low')
            },
            "recommendations": _generate_risk_mitigation_recommendations(risk_level, risk_factors),
            "next_assessment_due": (datetime.utcnow() + timedelta(
                days=1 if risk_level == RiskLevel.CRITICAL else
                     3 if risk_level == RiskLevel.HIGH else
                     7 if risk_level == RiskLevel.MEDIUM else 30
            )).isoformat()
        }
        
        # Simulate database update
        logger.debug(f"Risk profile update data: {json.dumps(risk_profile_update, indent=2)}")
        
        # In a real implementation, this would update the database:
        # await db.execute(
        #     "UPDATE user_risk_profiles SET risk_data = $1, updated_at = $2 WHERE user_id = $3",
        #     json.dumps(risk_profile_update), datetime.utcnow(), user_id
        # )
        
        logger.info(f"Successfully updated risk profile for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to update user risk profile for {user_id}: {str(e)}")
        raise

def _generate_risk_mitigation_recommendations(risk_level: RiskLevel, risk_factors: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on risk level and factors"""
    recommendations = []
    
    if risk_level == RiskLevel.CRITICAL:
        recommendations.extend([
            "Immediately suspend account pending investigation",
            "Escalate to security team for manual review",
            "Block all financial transactions",
            "Require identity verification"
        ])
    elif risk_level == RiskLevel.HIGH:
        recommendations.extend([
            "Require additional authentication for sensitive actions",
            "Limit transaction amounts temporarily",
            "Increase monitoring frequency",
            "Flag for manual review within 24 hours"
        ])
    elif risk_level == RiskLevel.MEDIUM:
        recommendations.extend([
            "Enable enhanced monitoring for 30 days",
            "Require email verification for account changes",
            "Implement transaction velocity limits"
        ])
    else:  # LOW
        recommendations.extend([
            "Continue standard monitoring",
            "Schedule next assessment in 30 days"
        ])
    
    # Add specific recommendations based on risk factors
    if risk_factors.get('behavioral_anomalies', 0) > 0.7:
        recommendations.append("Investigate unusual login patterns and device usage")
    
    if risk_factors.get('content_violations', 0) > 0.5:
        recommendations.append("Review content upload history for policy violations")
    
    return recommendations

async def _send_fraud_alert(analysis_id: str, user_id: str, analysis_result: Dict[str, Any], risk_level: RiskLevel):
    """Send fraud alert to security team"""
    try:
        logger.info(f"Sending fraud alert for analysis {analysis_id}, user {user_id}, risk level {risk_level.value}")
        
        # Prepare alert data
        alert_data = {
            "alert_id": f"fraud_alert_{analysis_id}",
            "analysis_id": analysis_id,
            "user_id": user_id,
            "risk_level": risk_level.value,
            "risk_score": analysis_result.get('risk_score', 0.0),
            "detected_at": datetime.utcnow().isoformat(),
            "priority": "critical" if risk_level == RiskLevel.CRITICAL else
                      "high" if risk_level == RiskLevel.HIGH else
                      "medium" if risk_level == RiskLevel.MEDIUM else "low",
            "summary": _generate_alert_summary(analysis_result, risk_level),
            "risk_factors": analysis_result.get('risk_factors', {}),
            "recommended_actions": _generate_risk_mitigation_recommendations(risk_level, analysis_result.get('risk_factors', {})),
            "investigation_urls": {
                "user_dashboard": f"/admin/users/{user_id}",
                "analysis_details": f"/security/fraud-analysis/{analysis_id}",
                "risk_history": f"/security/risk-history/{user_id}"
            }
        }
        
        # Determine alert channels based on risk level
        alert_channels = []
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            alert_channels.extend(["email", "slack", "dashboard", "sms"])
        elif risk_level == RiskLevel.MEDIUM:
            alert_channels.extend(["email", "dashboard"])
        else:
            alert_channels.append("dashboard")
        
        # Send alerts through different channels
        for channel in alert_channels:
            try:
                if channel == "email":
                    await _send_email_alert(alert_data)
                elif channel == "slack":
                    await _send_slack_alert(alert_data)
                elif channel == "sms":
                    await _send_sms_alert(alert_data)
                elif channel == "dashboard":
                    await _create_dashboard_alert(alert_data)
                    
                logger.debug(f"Alert sent via {channel} for analysis {analysis_id}")
                
            except Exception as channel_error:
                logger.error(f"Failed to send alert via {channel}: {str(channel_error)}")
        
        # Log alert for audit trail
        await _log_fraud_alert(alert_data)
        
        logger.info(f"Successfully sent fraud alert for analysis {analysis_id}")
        
    except Exception as e:
        logger.error(f"Failed to send fraud alert for {analysis_id}: {str(e)}")
        raise

def _generate_alert_summary(analysis_result: Dict[str, Any], risk_level: RiskLevel) -> str:
    """Generate human-readable alert summary"""
    risk_score = analysis_result.get('risk_score', 0.0)
    primary_factors = []
    
    risk_factors = analysis_result.get('risk_factors', {})
    
    if risk_factors.get('behavioral_anomalies', 0) > 0.7:
        primary_factors.append("unusual behavior patterns")
    
    if risk_factors.get('transaction_patterns', 0) > 0.7:
        primary_factors.append("suspicious transaction activity")
    
    if risk_factors.get('content_violations', 0) > 0.7:
        primary_factors.append("content policy violations")
    
    if risk_factors.get('engagement_metrics', 0) > 0.7:
        primary_factors.append("abnormal engagement patterns")
    
    factors_text = ", ".join(primary_factors) if primary_factors else "multiple indicators"
    
    if risk_level == RiskLevel.CRITICAL:
        return f"CRITICAL fraud risk detected (score: {risk_score:.2f}). Immediate action required due to {factors_text}."
    elif risk_level == RiskLevel.HIGH:
        return f"HIGH fraud risk detected (score: {risk_score:.2f}). Investigation needed for {factors_text}."
    elif risk_level == RiskLevel.MEDIUM:
        return f"MEDIUM fraud risk detected (score: {risk_score:.2f}). Monitoring recommended for {factors_text}."
    else:
        return f"LOW fraud risk detected (score: {risk_score:.2f}). Standard monitoring continues."

async def _send_email_alert(alert_data: Dict[str, Any]):
    """Send email alert to security team"""
    # Simulate email sending
    logger.debug(f"Email alert sent for {alert_data['alert_id']}")

async def _send_slack_alert(alert_data: Dict[str, Any]):
    """Send Slack alert to security channel"""
    # Simulate Slack notification
    logger.debug(f"Slack alert sent for {alert_data['alert_id']}")

async def _send_sms_alert(alert_data: Dict[str, Any]):
    """Send SMS alert for critical cases"""
    # Simulate SMS sending
    logger.debug(f"SMS alert sent for {alert_data['alert_id']}")

async def _create_dashboard_alert(alert_data: Dict[str, Any]):
    """Create dashboard alert notification"""
    # Simulate dashboard notification creation
    logger.debug(f"Dashboard alert created for {alert_data['alert_id']}")

async def _log_fraud_alert(alert_data: Dict[str, Any]):
    """Log fraud alert for audit trail"""
    # Simulate audit log entry
    logger.debug(f"Fraud alert logged: {alert_data['alert_id']}")

async def _update_detection_models(analysis_result: Dict[str, Any]):
    """Update fraud detection models with new patterns"""
    try:
        logger.info("Updating fraud detection models with new patterns")
        
        # Extract patterns from analysis
        risk_factors = analysis_result.get('risk_factors', {})
        patterns = analysis_result.get('detected_patterns', {})
        
        # Model update data
        model_updates = {
            "behavioral_model": {
                "new_anomaly_patterns": patterns.get('behavioral_anomalies', []),
                "weight_adjustments": {
                    "login_frequency": risk_factors.get('behavioral_anomalies', 0) * 0.1,
                    "device_switching": risk_factors.get('device_anomalies', 0) * 0.15,
                    "session_duration": risk_factors.get('session_anomalies', 0) * 0.08
                }
            },
            "transaction_model": {
                "new_fraud_patterns": patterns.get('transaction_anomalies', []),
                "risk_thresholds": {
                    "velocity_limit": max(0.1, risk_factors.get('transaction_patterns', 0) * 0.2),
                    "amount_deviation": risk_factors.get('amount_anomalies', 0) * 0.25,
                    "frequency_threshold": risk_factors.get('frequency_anomalies', 0) * 0.3
                }
            },
            "content_model": {
                "violation_patterns": patterns.get('content_violations', []),
                "content_risk_weights": {
                    "spam_indicators": risk_factors.get('content_violations', 0) * 0.2,
                    "quality_degradation": risk_factors.get('quality_issues', 0) * 0.15,
                    "policy_violations": risk_factors.get('policy_violations', 0) * 0.3
                }
            },
            "ensemble_model": {
                "feature_importance_updates": {
                    "behavioral_weight": 0.3 + (risk_factors.get('behavioral_anomalies', 0) * 0.1),
                    "transaction_weight": 0.25 + (risk_factors.get('transaction_patterns', 0) * 0.1),
                    "content_weight": 0.2 + (risk_factors.get('content_violations', 0) * 0.1),
                    "engagement_weight": 0.15 + (risk_factors.get('engagement_metrics', 0) * 0.05),
                    "temporal_weight": 0.1
                }
            }
        }
        
        # Simulate model retraining trigger
        should_retrain = (
            analysis_result.get('risk_score', 0) > 0.8 or  # High risk case
            len(patterns.get('new_fraud_indicators', [])) > 5  # Many new patterns
        )
        
        if should_retrain:
            logger.info("Triggering model retraining due to significant new patterns")
            await _trigger_model_retraining(model_updates)
        else:
            logger.info("Applying incremental model updates")
            await _apply_incremental_updates(model_updates)
        
        # Update model metadata
        model_metadata = {
            "last_update": datetime.utcnow().isoformat(),
            "update_source": "fraud_analysis",
            "patterns_incorporated": len(patterns),
            "confidence_adjustment": min(0.1, analysis_result.get('risk_score', 0) * 0.05),
            "next_full_retrain_due": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        # Simulate model registry update
        logger.debug(f"Model updates applied: {json.dumps(model_updates, indent=2)}")
        logger.info("Successfully updated fraud detection models")
        
    except Exception as e:
        logger.error(f"Failed to update detection models: {str(e)}")
        raise

async def _trigger_model_retraining(model_updates: Dict[str, Any]):
    """Trigger full model retraining with new patterns"""
    logger.info("Initiating full model retraining process")
    
    # Simulate ML pipeline trigger
    training_job = {
        "job_id": f"fraud_retrain_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "job_type": "full_retrain",
        "priority": "high",
        "model_updates": model_updates,
        "estimated_duration": "2-4 hours",
        "data_window": "last_90_days"
    }
    
    logger.info(f"Model retraining job queued: {training_job['job_id']}")

async def _apply_incremental_updates(model_updates: Dict[str, Any]):
    """Apply incremental updates to existing models"""
    logger.info("Applying incremental model updates")
    
    # Simulate incremental learning
    for model_name, updates in model_updates.items():
        logger.debug(f"Updating {model_name} with incremental changes")
        
    logger.info("Incremental model updates completed")

async def _archive_analysis_results(analysis_id: str, user_id: str, analysis_result: Dict[str, Any]):
    """Archive analysis results for future reference"""
    try:
        logger.info(f"Archiving analysis results for {analysis_id}")
        
        # Prepare archive data
        archive_data = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "archived_at": datetime.utcnow().isoformat(),
            "analysis_data": {
                "risk_score": analysis_result.get('risk_score', 0.0),
                "risk_level": analysis_result.get('risk_level', 'unknown'),
                "confidence": analysis_result.get('confidence', 0.0),
                "risk_factors": analysis_result.get('risk_factors', {}),
                "detected_patterns": analysis_result.get('detected_patterns', {}),
                "analysis_duration": analysis_result.get('analysis_duration', 0),
                "models_used": analysis_result.get('models_used', [])
            },
            "metadata": {
                "analysis_version": "1.0",
                "archive_format": "json",
                "compression": "gzip",
                "retention_period": "7_years",  # Compliance requirement
                "access_level": "security_team_only",
                "encryption": "aes256"
            },
            "audit_trail": {
                "created_by": "fraud_detection_agent",
                "purpose": "fraud_investigation_archive", 
                "compliance_tags": ["fraud_detection", "risk_assessment", "user_analysis"],
                "data_classification": "confidential"
            }
        }
        
        # Determine archive storage location based on risk level
        risk_level = analysis_result.get('risk_level', 'low')
        if risk_level in ['critical', 'high']:
            storage_tier = "hot_storage"  # Immediate access
            retention_policy = "immediate_access_7_years"
        elif risk_level == 'medium':
            storage_tier = "warm_storage"  # Fast access
            retention_policy = "fast_access_7_years"
        else:
            storage_tier = "cold_storage"  # Archive access
            retention_policy = "archive_access_7_years"
        
        archive_data["storage"] = {
            "tier": storage_tier,
            "retention_policy": retention_policy,
            "backup_locations": ["primary_datacenter", "backup_datacenter"],
            "replication_factor": 3 if risk_level in ['critical', 'high'] else 2
        }
        
        # Create archive record
        archive_record = {
            "archive_id": f"fraud_archive_{analysis_id}",
            "original_analysis_id": analysis_id,
            "user_id": user_id,
            "storage_path": f"/fraud_archives/{datetime.utcnow().year}/{datetime.utcnow().month:02d}/{analysis_id}.json.gz",
            "size_bytes": len(json.dumps(archive_data).encode('utf-8')),
            "checksum": _calculate_checksum(archive_data),
            "archived_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7*365)).isoformat(),  # 7 years
            "status": "archived",
            "access_count": 0,
            "last_accessed": None
        }
        
        # Simulate storage operations
        logger.debug(f"Archive data prepared for {analysis_id}: {storage_tier}")
        
        # In a real implementation, this would:
        # 1. Compress and encrypt the data
        # 2. Store in distributed storage system
        # 3. Create metadata records in archive database
        # 4. Set up automated retention policies
        # 5. Configure compliance monitoring
        
        # Simulate database storage
        # await archive_db.execute(
        #     "INSERT INTO fraud_analysis_archives (archive_id, data, metadata) VALUES ($1, $2, $3)",
        #     archive_record["archive_id"], 
        #     json.dumps(archive_data),
        #     json.dumps(archive_record)
        # )
        
        # Update analysis record with archive reference
        analysis_update = {
            "archived": True,
            "archive_id": archive_record["archive_id"],
            "archive_location": archive_record["storage_path"],
            "archived_at": archive_record["archived_at"]
        }
        
        logger.info(f"Successfully archived analysis results for {analysis_id}")
        logger.debug(f"Archive location: {archive_record['storage_path']}")
        
        return archive_record["archive_id"]
        
    except Exception as e:
        logger.error(f"Failed to archive analysis results for {analysis_id}: {str(e)}")
        raise

def _calculate_checksum(data: Dict[str, Any]) -> str:
    """Calculate checksum for data integrity verification"""
    import hashlib
    data_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

# Development/debug endpoints (only available in development)
if settings.ENVIRONMENT == "development":
    
    @app.get("/fraud/debug/models")
    async def debug_models():
        """Debug endpoint to check model status"""
        return {
            "behavioral_model": await fraud_detection_agent.behavioral_analyzer.get_model_status(),
            "pattern_model": await fraud_detection_agent.pattern_detector.get_model_status(),
            "deepfake_model": await fraud_detection_agent.deepfake_detector.get_model_status(),
            "anomaly_model": await fraud_detection_agent.anomaly_engine.get_model_status()
        }
    
    @app.post("/fraud/debug/simulate")
    async def debug_simulate_fraud(fraud_type: str = "behavioral"):
        """Debug endpoint to simulate fraud scenarios"""
        try:
            # Simulate different types of fraud for testing
            simulation_data = {
                "behavioral": {
                    "user_id": "debug_user_001",
                    "fraud_score": 0.85,
                    "indicators": ["unusual_typing_pattern", "device_inconsistency"]
                },
                "deepfake": {
                    "content_type": "video",
                    "fraud_score": 0.92,
                    "indicators": ["facial_inconsistency", "temporal_artifacts"]
                },
                "revenue": {
                    "transaction_amount": 1000.0,
                    "fraud_score": 0.78,
                    "indicators": ["amount_manipulation", "frequency_abuse"]
                }
            }
            
            return simulation_data.get(fraud_type, {"error": "Unknown fraud type"})
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

# Main entry point
def main():
    """Main entry point for running the fraud detection service"""
    uvicorn.run(
        "index:app",
        host=settings.HOST,
        port=settings.FRAUD_DETECTION_PORT,
        log_level="info",
        reload=settings.ENVIRONMENT == "development"
    )

if __name__ == "__main__":
    main()
