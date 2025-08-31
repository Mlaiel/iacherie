"""
Real-time Analytics API Endpoints
FastAPI endpoints for advanced revenue analytics dashboard.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import asyncio
import logging
from pydantic import BaseModel, Field

from analytics.advanced_revenue_analytics import (
    AdvancedRevenueAnalytics,
    RealTimeMetrics,
    ContentAttribution,
    MLPrediction,
    PricingRecommendation
)

logger = logging.getLogger(__name__)

# Initialize analytics engine
analytics_engine = AdvancedRevenueAnalytics()

# Pydantic models for API
class RealTimeMetricsRequest(BaseModel):
    platform: str = Field(..., description="Platform name")
    content_id: str = Field(..., description="Content ID")
    views: int = Field(default=0, description="Number of views")
    revenue: float = Field(default=0.0, description="Revenue amount")
    engagement_rate: float = Field(default=0.0, description="Engagement rate")
    conversion_rate: float = Field(default=0.0, description="Conversion rate")
    geographic_data: Dict[str, int] = Field(default_factory=dict, description="Geographic distribution")
    demographic_data: Dict[str, Any] = Field(default_factory=dict, description="Demographic data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaxComplianceRequest(BaseModel):
    revenue_data: Dict[str, float] = Field(..., description="Revenue by country")
    creator_country: str = Field(..., description="Creator's country")
    content_id: str = Field(..., description="Content ID")


class PricingOptimizationRequest(BaseModel):
    content_id: str = Field(..., description="Content ID")
    platform: str = Field(..., description="Platform name")
    current_price: float = Field(..., description="Current price")


class AnalyticsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {str(e)}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()

# Create FastAPI router
def create_analytics_router():
    """Create analytics router with all endpoints"""
    
    from fastapi import APIRouter
    router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
    
    @router.post("/realtime/track", response_model=AnalyticsResponse)
    async def track_realtime_analytics(request: RealTimeMetricsRequest):
        """Track real-time analytics metrics"""
        try:
            success = await analytics_engine.track_real_time_analytics(
                platform=request.platform,
                content_id=request.content_id,
                metrics={
                    'views': request.views,
                    'revenue': request.revenue,
                    'engagement_rate': request.engagement_rate,
                    'conversion_rate': request.conversion_rate,
                    'geographic_data': request.geographic_data,
                    'demographic_data': request.demographic_data,
                    'metadata': request.metadata
                }
            )
            
            if success:
                # Broadcast to WebSocket clients
                await manager.broadcast(json.dumps({
                    'type': 'realtime_update',
                    'content_id': request.content_id,
                    'platform': request.platform,
                    'revenue': request.revenue,
                    'views': request.views,
                    'timestamp': datetime.now().isoformat()
                }))
            
            return AnalyticsResponse(
                success=success,
                data={'tracked': success},
                message="Real-time analytics tracked successfully" if success else "Failed to track analytics"
            )
            
        except Exception as e:
            logger.error(f"Error in track_realtime_analytics: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/attribution/{content_id}", response_model=AnalyticsResponse)
    async def get_content_attribution(
        content_id: str,
        time_window_days: int = Query(default=30, ge=1, le=365, description="Time window in days")
    ):
        """Get content-specific revenue attribution"""
        try:
            attribution = await analytics_engine.calculate_content_attribution(
                content_id=content_id,
                time_window_days=time_window_days
            )
            
            return AnalyticsResponse(
                success=True,
                data={
                    'content_id': attribution.content_id,
                    'total_revenue': attribution.total_revenue,
                    'platform_breakdown': attribution.platform_breakdown,
                    'attribution_confidence': attribution.attribution_confidence,
                    'content_type': attribution.content_type,
                    'title': attribution.title,
                    'creator_id': attribution.creator_id,
                    'time_series_revenue': attribution.time_series_revenue[:50],  # Limit for API response
                    'last_updated': attribution.last_updated.isoformat()
                },
                message="Content attribution calculated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in get_content_attribution: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/prediction/{content_id}", response_model=AnalyticsResponse)
    async def get_ml_revenue_prediction(
        content_id: str,
        prediction_horizon_days: int = Query(default=30, ge=1, le=365, description="Prediction horizon in days")
    ):
        """Get ML-based revenue prediction"""
        try:
            prediction = await analytics_engine.predict_revenue_ml_advanced(
                content_id=content_id,
                prediction_horizon_days=prediction_horizon_days
            )
            
            return AnalyticsResponse(
                success=True,
                data={
                    'content_id': prediction.content_id,
                    'predicted_revenue': prediction.predicted_revenue,
                    'confidence_interval': prediction.confidence_interval,
                    'prediction_horizon_days': prediction.prediction_horizon_days,
                    'model_accuracy': prediction.model_accuracy,
                    'feature_importance': prediction.feature_importance,
                    'generated_at': prediction.generated_at.isoformat()
                },
                message="ML revenue prediction generated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in get_ml_revenue_prediction: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/pricing/optimize", response_model=AnalyticsResponse)
    async def optimize_pricing(request: PricingOptimizationRequest):
        """Get dynamic pricing optimization recommendation"""
        try:
            recommendation = await analytics_engine.optimize_dynamic_pricing(
                content_id=request.content_id,
                platform=request.platform,
                current_price=request.current_price
            )
            
            return AnalyticsResponse(
                success=True,
                data={
                    'content_id': recommendation.content_id,
                    'platform': recommendation.platform,
                    'current_price': recommendation.current_price,
                    'recommended_price': recommendation.recommended_price,
                    'expected_revenue_lift': recommendation.expected_revenue_lift,
                    'confidence_score': recommendation.confidence_score,
                    'price_elasticity': recommendation.price_elasticity,
                    'market_conditions': recommendation.market_conditions,
                    'generated_at': recommendation.generated_at.isoformat()
                },
                message="Pricing optimization recommendation generated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in optimize_pricing: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/tax/compliance", response_model=AnalyticsResponse)
    async def calculate_tax_compliance(request: TaxComplianceRequest):
        """Calculate international tax compliance for 67 countries"""
        try:
            compliance_report = await analytics_engine.calculate_international_tax_compliance(
                revenue_data=request.revenue_data,
                creator_country=request.creator_country,
                content_id=request.content_id
            )
            
            return AnalyticsResponse(
                success=True,
                data=compliance_report,
                message="Tax compliance calculated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in calculate_tax_compliance: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/dashboard/{creator_id}", response_model=AnalyticsResponse)
    async def get_realtime_dashboard(
        creator_id: str,
        time_range_hours: int = Query(default=24, ge=1, le=168, description="Time range in hours")
    ):
        """Get comprehensive real-time dashboard data"""
        try:
            dashboard_data = await analytics_engine.get_real_time_dashboard_data(
                creator_id=creator_id,
                time_range_hours=time_range_hours
            )
            
            return AnalyticsResponse(
                success=True,
                data=dashboard_data,
                message="Dashboard data retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in get_realtime_dashboard: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/platforms/summary", response_model=AnalyticsResponse)
    async def get_platform_summary():
        """Get cross-platform analytics summary"""
        try:
            # Aggregate data across all platforms
            platform_summary = {}
            total_revenue = 0.0
            total_views = 0
            
            # Process real-time buffer
            for buffer_key, metrics_list in analytics_engine.real_time_buffer.items():
                platform = buffer_key.split('_')[-1]
                
                if platform not in platform_summary:
                    platform_summary[platform] = {
                        'revenue': 0.0,
                        'views': 0,
                        'content_count': 0,
                        'avg_engagement': 0.0,
                        'engagement_sum': 0.0,
                        'metrics_count': 0
                    }
                
                platform_data = platform_summary[platform]
                
                for metric in metrics_list:
                    # Only consider recent data (last 24 hours)
                    if metric.timestamp >= datetime.now() - timedelta(hours=24):
                        platform_data['revenue'] += metric.revenue
                        platform_data['views'] += metric.views
                        platform_data['engagement_sum'] += metric.engagement_rate
                        platform_data['metrics_count'] += 1
                        
                        total_revenue += metric.revenue
                        total_views += metric.views
                
                # Calculate averages
                if platform_data['metrics_count'] > 0:
                    platform_data['avg_engagement'] = platform_data['engagement_sum'] / platform_data['metrics_count']
                
                # Clean up temporary fields
                del platform_data['engagement_sum']
                del platform_data['metrics_count']
            
            return AnalyticsResponse(
                success=True,
                data={
                    'platform_breakdown': platform_summary,
                    'total_revenue': total_revenue,
                    'total_views': total_views,
                    'platform_count': len(platform_summary),
                    'generated_at': datetime.now().isoformat()
                },
                message="Platform summary generated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in get_platform_summary: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.websocket("/ws/realtime/{creator_id}")
    async def websocket_realtime_analytics(websocket: WebSocket, creator_id: str):
        """WebSocket endpoint for real-time analytics updates"""
        await manager.connect(websocket)
        try:
            while True:
                # Send periodic updates
                dashboard_data = await analytics_engine.get_real_time_dashboard_data(
                    creator_id=creator_id,
                    time_range_hours=1  # Last hour data
                )
                
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'dashboard_update',
                        'creator_id': creator_id,
                        'data': dashboard_data,
                        'timestamp': datetime.now().isoformat()
                    }),
                    websocket
                )
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info(f"WebSocket disconnected for creator {creator_id}")
        except Exception as e:
            logger.error(f"WebSocket error for creator {creator_id}: {str(e)}")
            manager.disconnect(websocket)
    
    return router


# Health check endpoint
def create_health_router():
    """Create health check router"""
    
    from fastapi import APIRouter
    router = APIRouter(prefix="/api/v1/health", tags=["health"])
    
    @router.get("/")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "advanced_revenue_analytics",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    @router.get("/analytics")
    async def analytics_health():
        """Analytics engine health check"""
        try:
            # Test basic functionality
            buffer_size = sum(len(metrics) for metrics in analytics_engine.real_time_buffer.values())
            
            return {
                "status": "healthy",
                "analytics_engine": "operational",
                "buffer_size": buffer_size,
                "active_connections": len(manager.active_connections),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    return router


# Main FastAPI application factory
def create_analytics_app():
    """Create complete FastAPI application with analytics"""
    
    app = FastAPI(
        title="Advanced Revenue Analytics API",
        description="Real-time analytics with ML predictions, dynamic pricing, and international tax compliance",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(create_analytics_router())
    app.include_router(create_health_router())
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Advanced Revenue Analytics API",
            "version": "1.0.0",
            "endpoints": {
                "docs": "/docs",
                "health": "/api/v1/health",
                "analytics": "/api/v1/analytics"
            }
        }
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info("Advanced Revenue Analytics API starting up...")
        # Initialize analytics engine
        logger.info("Analytics engine initialized")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Advanced Revenue Analytics API shutting down...")
        # Close WebSocket connections
        for connection in manager.active_connections:
            await connection.close()
    
    return app


# For running the application
if __name__ == "__main__":
    import uvicorn
    app = create_analytics_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)