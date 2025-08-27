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
        # This would update the user's risk profile in the database
        pass
    except Exception as e:
        logger.error(f"Failed to update user risk profile for {user_id}: {str(e)}")

async def _send_fraud_alert(analysis_id: str, user_id: str, analysis_result: Dict[str, Any], risk_level: RiskLevel):
    """Send fraud alert to security team"""
    try:
        # This would send alerts via email, Slack, or other notification systems
        pass
    except Exception as e:
        logger.error(f"Failed to send fraud alert for {analysis_id}: {str(e)}")

async def _update_detection_models(analysis_result: Dict[str, Any]):
    """Update fraud detection models with new patterns"""
    try:
        # This would update ML models with new fraud patterns
        pass
    except Exception as e:
        logger.error(f"Failed to update detection models: {str(e)}")

async def _archive_analysis_results(analysis_id: str, user_id: str, analysis_result: Dict[str, Any]):
    """Archive analysis results for future reference"""
    try:
        # This would archive results to long-term storage
        pass
    except Exception as e:
        logger.error(f"Failed to archive analysis results for {analysis_id}: {str(e)}")

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
