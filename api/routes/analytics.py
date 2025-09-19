#!/usr/bin/env python3
"""
Real-time Analytics Endpoints - Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Role: Backend Senior + Lead Dev IA
Purpose: Enterprise real-time analytics and metrics API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.websockets import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class MetricData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    value: float
    unit: str
    trend: str = Field(..., regex="^(up|down|stable)$")
    change: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class AnalyticsMetrics(BaseModel):
    views: int = 0
    unique_views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    watch_time_seconds: int = 0
    click_through_rate: float = 0.0
    bounce_rate: float = 0.0

class DemographicsData(BaseModel):
    age_groups: Dict[str, float] = {}
    gender: Dict[str, float] = {}
    top_countries: List[Dict[str, Any]] = []

class RevenueData(BaseModel):
    ad_revenue: float = 0.0
    subscription_revenue: float = 0.0
    merchandise_revenue: float = 0.0
    sponsorship_revenue: float = 0.0

class AnalyticsData(BaseModel):
    content_id: str
    date: str
    metrics: AnalyticsMetrics
    demographics: DemographicsData
    revenue: RevenueData

class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Router setup
router = APIRouter(prefix="/analytics", tags=["analytics"])

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.metrics_subscribers: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.metrics_subscribers:
            self.metrics_subscribers.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_metrics(self, data: List[MetricData]):
        if self.metrics_subscribers:
            message = {
                "type": "metrics_update",
                "data": [metric.dict() for metric in data],
                "timestamp": datetime.now().isoformat()
            }
            
            disconnected = []
            for connection in self.metrics_subscribers:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn)

manager = ConnectionManager()

# Mock data generator for demonstration
def generate_mock_metrics() -> List[MetricData]:
    """Generate mock real-time metrics"""
    import random
    
    base_time = time.time()
    
    metrics = [
        MetricData(
            name="views",
            value=random.randint(1000, 50000),
            unit="count",
            trend=random.choice(["up", "down", "stable"]),
            change=random.uniform(-10.0, 15.0)
        ),
        MetricData(
            name="revenue",
            value=round(random.uniform(100, 5000), 2),
            unit="USD",
            trend=random.choice(["up", "down", "stable"]),
            change=random.uniform(-20.0, 25.0)
        ),
        MetricData(
            name="protection",
            value=random.randint(85, 100),
            unit="percent",
            trend="stable",
            change=random.uniform(-2.0, 2.0)
        ),
        MetricData(
            name="alerts",
            value=random.randint(0, 5),
            unit="count",
            trend=random.choice(["up", "down", "stable"]),
            change=random.uniform(-50.0, 100.0)
        ),
        MetricData(
            name="engagement_rate",
            value=round(random.uniform(0.05, 0.25), 4),
            unit="percent",
            trend=random.choice(["up", "down", "stable"]),
            change=random.uniform(-15.0, 20.0)
        )
    ]
    
    return metrics

def generate_mock_analytics(content_id: str = None, days: int = 30) -> List[AnalyticsData]:
    """Generate mock analytics data"""
    import random
    from datetime import date, timedelta
    
    analytics = []
    start_date = date.today() - timedelta(days=days)
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Simulate growth trends
        base_views = random.randint(500, 5000) * (1 + i * 0.02)
        
        analytics_data = AnalyticsData(
            content_id=content_id or str(uuid.uuid4()),
            date=current_date.isoformat(),
            metrics=AnalyticsMetrics(
                views=int(base_views),
                unique_views=int(base_views * random.uniform(0.6, 0.9)),
                likes=int(base_views * random.uniform(0.05, 0.2)),
                comments=int(base_views * random.uniform(0.01, 0.08)),
                shares=int(base_views * random.uniform(0.005, 0.05)),
                watch_time_seconds=int(base_views * random.uniform(30, 180)),
                click_through_rate=round(random.uniform(0.02, 0.12), 4),
                bounce_rate=round(random.uniform(0.3, 0.8), 4)
            ),
            demographics=DemographicsData(
                age_groups={
                    "18-24": round(random.uniform(0.1, 0.4), 2),
                    "25-34": round(random.uniform(0.2, 0.5), 2),
                    "35-44": round(random.uniform(0.1, 0.3), 2),
                    "45-54": round(random.uniform(0.05, 0.2), 2),
                    "55+": round(random.uniform(0.02, 0.15), 2)
                },
                gender={
                    "male": round(random.uniform(0.3, 0.7), 2),
                    "female": round(random.uniform(0.3, 0.7), 2),
                    "other": round(random.uniform(0.01, 0.05), 2)
                },
                top_countries=[
                    {"country": "United States", "percentage": round(random.uniform(0.2, 0.5), 2)},
                    {"country": "United Kingdom", "percentage": round(random.uniform(0.1, 0.3), 2)},
                    {"country": "Canada", "percentage": round(random.uniform(0.05, 0.2), 2)},
                    {"country": "Germany", "percentage": round(random.uniform(0.05, 0.15), 2)},
                    {"country": "France", "percentage": round(random.uniform(0.03, 0.12), 2)}
                ]
            ),
            revenue=RevenueData(
                ad_revenue=round(base_views * random.uniform(0.001, 0.01), 2),
                subscription_revenue=round(random.uniform(0, 50), 2),
                merchandise_revenue=round(random.uniform(0, 100), 2),
                sponsorship_revenue=round(random.uniform(0, 200), 2)
            )
        )
        
        analytics.append(analytics_data)
    
    return analytics

# Background task for metrics updates
async def metrics_updater():
    """Background task to update metrics every few seconds"""
    while True:
        try:
            metrics = generate_mock_metrics()
            await manager.broadcast_metrics(metrics)
            await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error in metrics updater: {e}")
            await asyncio.sleep(10)

# Start background task
asyncio.create_task(metrics_updater())

# REST Endpoints
@router.get("/metrics/live", response_model=ApiResponse)
async def get_live_metrics():
    """Get current live metrics"""
    try:
        metrics = generate_mock_metrics()
        return ApiResponse(
            success=True,
            data=[metric.dict() for metric in metrics],
            message="Live metrics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting live metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/metrics/{metric_id}", response_model=ApiResponse)
async def get_metric(
    metric_id: str,
    time_range: str = Query("24h", regex="^(1h|6h|12h|24h|7d|30d)$")
):
    """Get specific metric with time range"""
    try:
        # Generate mock historical data based on time range
        metrics = generate_mock_metrics()
        metric = next((m for m in metrics if m.name == metric_id), None)
        
        if not metric:
            raise HTTPException(status_code=404, detail=f"Metric {metric_id} not found")
        
        return ApiResponse(
            success=True,
            data=metric.dict(),
            message=f"Metric {metric_id} retrieved for {time_range}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metric {metric_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dashboard", response_model=ApiResponse)
async def get_dashboard_analytics(
    content_id: Optional[str] = Query(None),
    date_range: Optional[str] = Query("30d", regex="^(7d|30d|90d|1y)$")
):
    """Get dashboard analytics data"""
    try:
        # Parse date range
        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = days_map.get(date_range, 30)
        
        analytics = generate_mock_analytics(content_id, days)
        
        return ApiResponse(
            success=True,
            data=[analytics_data.dict() for analytics_data in analytics],
            message=f"Dashboard analytics retrieved for {date_range}"
        )
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/summary", response_model=ApiResponse)
async def get_analytics_summary():
    """Get analytics summary with key performance indicators"""
    try:
        metrics = generate_mock_metrics()
        analytics = generate_mock_analytics(days=7)  # Last 7 days
        
        # Calculate summary
        total_views = sum(day.metrics.views for day in analytics)
        total_revenue = sum(
            day.revenue.ad_revenue + 
            day.revenue.subscription_revenue + 
            day.revenue.merchandise_revenue + 
            day.revenue.sponsorship_revenue 
            for day in analytics
        )
        avg_engagement = sum(day.metrics.click_through_rate for day in analytics) / len(analytics)
        
        summary = {
            "total_views": total_views,
            "total_revenue": round(total_revenue, 2),
            "average_engagement_rate": round(avg_engagement, 4),
            "active_content_items": len(analytics),
            "live_metrics": [metric.dict() for metric in metrics],
            "period": "last_7_days"
        }
        
        return ApiResponse(
            success=True,
            data=summary,
            message="Analytics summary retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# WebSocket Endpoints
@router.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await manager.connect(websocket)
    manager.metrics_subscribers.append(websocket)
    
    try:
        # Send initial metrics
        initial_metrics = generate_mock_metrics()
        await websocket.send_text(json.dumps({
            "type": "initial_metrics",
            "data": [metric.dict() for metric in initial_metrics],
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive
        while True:
            try:
                # Wait for client messages (for heartbeat, auth, etc.)
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

@router.websocket("/ws/dashboards/{dashboard_type}")
async def websocket_dashboard(websocket: WebSocket, dashboard_type: str):
    """WebSocket endpoint for dashboard-specific updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial dashboard data
        analytics = generate_mock_analytics(days=7)
        await websocket.send_text(json.dumps({
            "type": "dashboard_update",
            "dashboard_type": dashboard_type,
            "data": [item.dict() for item in analytics],
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                await websocket.receive_text()
                # Send updated data every 30 seconds
                await asyncio.sleep(30)
                
                updated_analytics = generate_mock_analytics(days=1)  # Latest day
                await websocket.send_text(json.dumps({
                    "type": "dashboard_update",
                    "dashboard_type": dashboard_type,
                    "data": [item.dict() for item in updated_analytics],
                    "timestamp": datetime.now().isoformat()
                }))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Dashboard WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

# Health check endpoint
@router.get("/health", response_model=ApiResponse)
async def analytics_health():
    """Health check for analytics service"""
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "active_connections": len(manager.active_connections),
            "metrics_subscribers": len(manager.metrics_subscribers),
            "timestamp": datetime.now().isoformat()
        },
        message="Analytics service is healthy"
    )