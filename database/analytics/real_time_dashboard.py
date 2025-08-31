"""Real-Time Analytics Dashboard - IA Influencer Agent Platform

Live analytics dashboard with real-time metrics, alerts, and insights.
Provides instant visibility into content performance across all platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
"""
from typing import Dict, List, Optional, Tuple, Any, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
from uuid import UUID, uuid4
import time

import pandas as pd
import numpy as np
from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, Boolean, Text, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect
import redis
from typing_extensions import Literal

Base = declarative_base()


class DashboardWidget(Enum):
    """Available dashboard widgets"""
    REAL_TIME_METRICS = "real_time_metrics"
    PERFORMANCE_OVERVIEW = "performance_overview"
    PLATFORM_COMPARISON = "platform_comparison"
    TRENDING_CONTENT = "trending_content"
    AUDIENCE_INSIGHTS = "audience_insights"
    REVENUE_TRACKING = "revenue_tracking"
    ALERTS_PANEL = "alerts_panel"
    OPTIMIZATION_SUGGESTIONS = "optimization_suggestions"
    GROWTH_TRENDS = "growth_trends"
    COMPETITOR_ANALYSIS = "competitor_analysis"


class MetricTimeframe(Enum):
    """Time frames for analytics"""
    LIVE = "live"
    LAST_HOUR = "last_hour"
    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"
    LAST_90D = "last_90d"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"


@dataclass
class RealTimeMetric:
    """Real-time metric data structure"""
    metric_name: str
    current_value: Union[int, float]
    previous_value: Union[int, float]
    change_percentage: float
    trend_direction: Literal["up", "down", "stable"]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_change(self) -> float:
        """Calculate percentage change from previous value"""
        if self.previous_value == 0:
            return 100.0 if self.current_value > 0 else 0.0
        return ((self.current_value - self.previous_value) / self.previous_value) * 100


@dataclass
class DashboardAlert:
    """Dashboard alert data structure"""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    widget_type: DashboardWidget
    timestamp: datetime
    action_required: bool = False
    auto_dismiss: bool = True
    dismiss_after: int = 300  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "widget_type": self.widget_type.value,
            "timestamp": self.timestamp.isoformat(),
            "action_required": self.action_required,
            "auto_dismiss": self.auto_dismiss,
            "dismiss_after": self.dismiss_after
        }


class DashboardSession(Base):
    """Database model for dashboard sessions"""
    __tablename__ = "dashboard_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    session_token = Column(String, nullable=False, unique=True)
    
    # Dashboard configuration
    active_widgets = Column(JSON)
    widget_positions = Column(JSON)
    refresh_intervals = Column(JSON)
    filter_settings = Column(JSON)
    
    # Session metadata
    ip_address = Column(String)
    user_agent = Column(String)
    timezone = Column(String, default="UTC")
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)


class DashboardMetrics(Base):
    """Database model for dashboard metrics cache"""
    __tablename__ = "dashboard_metrics_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    metric_type = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    
    # Metric data
    metric_value = Column(Float)
    metric_data = Column(JSON)
    calculation_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Cache metadata
    cache_key = Column(String, unique=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class RealTimeDashboard:
    """
    Real-time analytics dashboard with live updates, alerts, and insights.
    Provides WebSocket-based real-time data streaming to frontend.
    """
    
    def __init__(self, db_session: Session, redis_client: Optional[redis.Redis] = None):
        self.db_session = db_session
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.alert_manager = AlertManager(self.redis_client)
        
    async def connect_user(self, user_id: str, websocket: WebSocket, session_config: Dict[str, Any] = None) -> str:
        """Connect user to real-time dashboard"""
        await websocket.accept()
        
        # Generate session token
        session_token = str(uuid4())
        
        # Store connection
        self.active_connections[session_token] = websocket
        
        # Initialize user session
        self.user_sessions[session_token] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow(),
            "widgets": session_config.get("widgets", list(DashboardWidget)),
            "refresh_intervals": session_config.get("refresh_intervals", {}),
            "filters": session_config.get("filters", {})
        }
        
        # Save session to database
        await self._save_session_to_db(user_id, session_token, session_config)
        
        # Send initial dashboard data
        await self._send_initial_dashboard_data(session_token)
        
        # Start real-time updates
        asyncio.create_task(self._start_real_time_updates(session_token))
        
        return session_token
    
    async def disconnect_user(self, session_token: str):
        """Disconnect user from dashboard"""
        if session_token in self.active_connections:
            del self.active_connections[session_token]
        
        if session_token in self.user_sessions:
            # Update session in database
            await self._update_session_status(session_token, False)
            del self.user_sessions[session_token]
    
    async def _save_session_to_db(self, user_id: str, session_token: str, config: Dict[str, Any]):
        """Save dashboard session to database"""
        try:
            session = DashboardSession(
                user_id=user_id,
                session_token=session_token,
                active_widgets=config.get("widgets", []),
                widget_positions=config.get("positions", {}),
                refresh_intervals=config.get("refresh_intervals", {}),
                filter_settings=config.get("filters", {}),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            self.db_session.add(session)
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            print(f"Failed to save dashboard session: {e}")
    
    async def _update_session_status(self, session_token: str, is_active: bool):
        """Update session status in database"""
        try:
            session = self.db_session.query(DashboardSession).filter(
                DashboardSession.session_token == session_token
            ).first()
            
            if session:
                session.is_active = is_active
                session.last_activity = datetime.utcnow()
                self.db_session.commit()
                
        except Exception as e:
            self.db_session.rollback()
            print(f"Failed to update session status: {e}")
    
    async def _send_initial_dashboard_data(self, session_token: str):
        """Send initial dashboard data to connected user"""
        try:
            session_info = self.user_sessions.get(session_token)
            if not session_info:
                return
            
            user_id = session_info["user_id"]
            active_widgets = session_info["widgets"]
            
            dashboard_data = {
                "type": "initial_data",
                "timestamp": datetime.utcnow().isoformat(),
                "widgets": {}
            }
            
            # Load data for each active widget
            for widget in active_widgets:
                if isinstance(widget, str):
                    widget = DashboardWidget(widget)
                
                widget_data = await self._get_widget_data(user_id, widget)
                dashboard_data["widgets"][widget.value] = widget_data
            
            await self._send_to_user(session_token, dashboard_data)
            
        except Exception as e:
            print(f"Failed to send initial dashboard data: {e}")
    
    async def _get_widget_data(self, user_id: str, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for specific dashboard widget"""
        try:
            if widget == DashboardWidget.REAL_TIME_METRICS:
                return await self._get_real_time_metrics(user_id)
            elif widget == DashboardWidget.PERFORMANCE_OVERVIEW:
                return await self._get_performance_overview(user_id)
            elif widget == DashboardWidget.PLATFORM_COMPARISON:
                return await self._get_platform_comparison(user_id)
            elif widget == DashboardWidget.TRENDING_CONTENT:
                return await self._get_trending_content(user_id)
            elif widget == DashboardWidget.AUDIENCE_INSIGHTS:
                return await self._get_audience_insights(user_id)
            elif widget == DashboardWidget.REVENUE_TRACKING:
                return await self._get_revenue_tracking(user_id)
            elif widget == DashboardWidget.ALERTS_PANEL:
                return await self._get_alerts_panel(user_id)
            elif widget == DashboardWidget.OPTIMIZATION_SUGGESTIONS:
                return await self._get_optimization_suggestions(user_id)
            elif widget == DashboardWidget.GROWTH_TRENDS:
                return await self._get_growth_trends(user_id)
            elif widget == DashboardWidget.COMPETITOR_ANALYSIS:
                return await self._get_competitor_analysis(user_id)
            else:
                return {"error": f"Unknown widget: {widget.value}"}
                
        except Exception as e:
            return {"error": f"Failed to load widget data: {str(e)}"}
    
    async def _get_real_time_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get real-time metrics for dashboard"""
        # Check cache first
        cache_key = f"real_time_metrics:{user_id}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        # Calculate real-time metrics
        current_time = datetime.utcnow()
        metrics = {}
        
        # Mock real-time data (would be replaced with actual data sources)
        base_metrics = {
            "total_views": 125000,
            "total_likes": 8900,
            "total_shares": 1200,
            "total_comments": 450,
            "engagement_rate": 8.5,
            "active_followers": 25600,
            "revenue_today": 156.80
        }
        
        # Add real-time fluctuations
        for metric_name, base_value in base_metrics.items():
            fluctuation = np.random.uniform(-0.05, 0.05)  # ±5% fluctuation
            current_value = base_value * (1 + fluctuation)
            previous_value = base_value * (1 + np.random.uniform(-0.05, 0.05))
            
            real_time_metric = RealTimeMetric(
                metric_name=metric_name,
                current_value=current_value,
                previous_value=previous_value,
                change_percentage=((current_value - previous_value) / previous_value) * 100,
                trend_direction="up" if current_value > previous_value else "down"
            )
            
            metrics[metric_name] = {
                "current_value": round(current_value, 2),
                "change_percentage": round(real_time_metric.change_percentage, 2),
                "trend_direction": real_time_metric.trend_direction,
                "timestamp": real_time_metric.timestamp.isoformat()
            }
        
        # Cache for 30 seconds
        self.redis_client.setex(cache_key, 30, json.dumps(metrics))
        
        return {
            "widget_type": "real_time_metrics",
            "data": metrics,
            "last_updated": current_time.isoformat(),
            "update_interval": 30
        }
    
    async def _get_performance_overview(self, user_id: str) -> Dict[str, Any]:
        """Get performance overview for last 24 hours"""
        # This would query actual analytics data
        return {
            "widget_type": "performance_overview",
            "data": {
                "period": "last_24h",
                "total_content_pieces": 12,
                "best_performing_platform": "Instagram",
                "avg_engagement_rate": 7.2,
                "total_reach": 89000,
                "growth_rate": 12.5
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_platform_comparison(self, user_id: str) -> Dict[str, Any]:
        """Get platform comparison data"""
        return {
            "widget_type": "platform_comparison",
            "data": {
                "platforms": {
                    "instagram": {
                        "followers": 15600,
                        "engagement_rate": 8.2,
                        "avg_views": 2100,
                        "revenue": 45.80
                    },
                    "youtube": {
                        "subscribers": 8900,
                        "engagement_rate": 6.8,
                        "avg_views": 15000,
                        "revenue": 89.20
                    },
                    "tiktok": {
                        "followers": 23400,
                        "engagement_rate": 12.1,
                        "avg_views": 8500,
                        "revenue": 21.00
                    }
                }
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_trending_content(self, user_id: str) -> Dict[str, Any]:
        """Get trending content data"""
        return {
            "widget_type": "trending_content",
            "data": {
                "trending_posts": [
                    {
                        "content_id": "post_123",
                        "title": "Amazing Music Production Tips",
                        "platform": "youtube",
                        "views": 45000,
                        "engagement_rate": 15.2,
                        "trend_score": 89
                    },
                    {
                        "content_id": "post_124",
                        "title": "Behind the Scenes Studio",
                        "platform": "instagram",
                        "views": 12000,
                        "engagement_rate": 18.5,
                        "trend_score": 76
                    }
                ]
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_audience_insights(self, user_id: str) -> Dict[str, Any]:
        """Get audience insights data"""
        return {
            "widget_type": "audience_insights",
            "data": {
                "demographics": {
                    "age_groups": {
                        "18-24": 35,
                        "25-34": 45,
                        "35-44": 15,
                        "45+": 5
                    },
                    "top_countries": ["US", "UK", "Germany", "France", "Canada"],
                    "peak_activity_hours": [18, 19, 20, 21]
                },
                "interests": ["music", "technology", "entertainment", "lifestyle"]
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_revenue_tracking(self, user_id: str) -> Dict[str, Any]:
        """Get revenue tracking data"""
        return {
            "widget_type": "revenue_tracking",
            "data": {
                "daily_revenue": 156.80,
                "monthly_revenue": 3420.50,
                "revenue_sources": {
                    "sponsorships": 60,
                    "affiliate": 25,
                    "merchandise": 10,
                    "donations": 5
                },
                "revenue_trend": "up",
                "growth_percentage": 18.5
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_alerts_panel(self, user_id: str) -> Dict[str, Any]:
        """Get active alerts for user"""
        alerts = await self.alert_manager.get_user_alerts(user_id)
        
        return {
            "widget_type": "alerts_panel",
            "data": {
                "active_alerts": [alert.to_dict() for alert in alerts],
                "alert_count": len(alerts),
                "critical_count": len([a for a in alerts if a.severity == AlertSeverity.CRITICAL]),
                "warning_count": len([a for a in alerts if a.severity == AlertSeverity.WARNING])
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_optimization_suggestions(self, user_id: str) -> Dict[str, Any]:
        """Get optimization suggestions"""
        return {
            "widget_type": "optimization_suggestions",
            "data": {
                "suggestions": [
                    {
                        "title": "Optimize posting time",
                        "description": "Post at 7 PM for 15% higher engagement",
                        "priority": "high",
                        "estimated_impact": "15% engagement increase"
                    },
                    {
                        "title": "Improve video thumbnails",
                        "description": "Custom thumbnails increase click-through by 20%",
                        "priority": "medium",
                        "estimated_impact": "20% CTR increase"
                    }
                ]
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_growth_trends(self, user_id: str) -> Dict[str, Any]:
        """Get growth trends data"""
        return {
            "widget_type": "growth_trends",
            "data": {
                "follower_growth": {
                    "7_days": 125,
                    "30_days": 890,
                    "growth_rate": 12.5
                },
                "engagement_growth": {
                    "7_days": 8.2,
                    "30_days": 15.6,
                    "growth_rate": 18.3
                },
                "trend_direction": "upward",
                "key_milestones": [
                    {"date": "2025-08-20", "event": "Reached 10K followers"},
                    {"date": "2025-08-15", "event": "Best performing video"}
                ]
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _get_competitor_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get competitor analysis data"""
        return {
            "widget_type": "competitor_analysis",
            "data": {
                "position_ranking": 3,
                "performance_vs_competitors": {
                    "engagement_rate": "+15%",
                    "posting_frequency": "-10%",
                    "content_quality": "+8%"
                },
                "opportunities": [
                    "Increase posting frequency to match top performers",
                    "Leverage trending hashtags more effectively"
                ]
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _start_real_time_updates(self, session_token: str):
        """Start real-time updates for connected user"""
        try:
            session_info = self.user_sessions.get(session_token)
            if not session_info:
                return
            
            user_id = session_info["user_id"]
            
            while session_token in self.active_connections:
                try:
                    # Send real-time metric updates
                    real_time_data = await self._get_real_time_metrics(user_id)
                    
                    update_message = {
                        "type": "real_time_update",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": real_time_data
                    }
                    
                    await self._send_to_user(session_token, update_message)
                    
                    # Check for new alerts
                    await self._check_and_send_alerts(session_token, user_id)
                    
                    # Wait for next update (30 seconds)
                    await asyncio.sleep(30)
                    
                except WebSocketDisconnect:
                    await self.disconnect_user(session_token)
                    break
                except Exception as e:
                    print(f"Error in real-time updates: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            print(f"Failed to start real-time updates: {e}")
    
    async def _check_and_send_alerts(self, session_token: str, user_id: str):
        """Check for new alerts and send to user"""
        try:
            new_alerts = await self.alert_manager.get_new_alerts(user_id)
            
            if new_alerts:
                alert_message = {
                    "type": "new_alerts",
                    "timestamp": datetime.utcnow().isoformat(),
                    "alerts": [alert.to_dict() for alert in new_alerts]
                }
                
                await self._send_to_user(session_token, alert_message)
                
        except Exception as e:
            print(f"Failed to check alerts: {e}")
    
    async def _send_to_user(self, session_token: str, message: Dict[str, Any]):
        """Send message to specific user via WebSocket"""
        if session_token in self.active_connections:
            try:
                websocket = self.active_connections[session_token]
                await websocket.send_text(json.dumps(message))
                
                # Update last activity
                if session_token in self.user_sessions:
                    self.user_sessions[session_token]["last_ping"] = datetime.utcnow()
                    
            except WebSocketDisconnect:
                await self.disconnect_user(session_token)
            except Exception as e:
                print(f"Failed to send message to user: {e}")
    
    async def broadcast_to_all_users(self, message: Dict[str, Any]):
        """Broadcast message to all connected users"""
        disconnected_sessions = []
        
        for session_token, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected_sessions.append(session_token)
            except Exception as e:
                print(f"Failed to broadcast to session {session_token}: {e}")
                disconnected_sessions.append(session_token)
        
        # Clean up disconnected sessions
        for session_token in disconnected_sessions:
            await self.disconnect_user(session_token)
    
    async def update_widget_configuration(self, session_token: str, widget_config: Dict[str, Any]) -> bool:
        """Update widget configuration for user session"""
        try:
            if session_token not in self.user_sessions:
                return False
            
            # Update session configuration
            self.user_sessions[session_token].update(widget_config)
            
            # Update database
            session = self.db_session.query(DashboardSession).filter(
                DashboardSession.session_token == session_token
            ).first()
            
            if session:
                session.active_widgets = widget_config.get("widgets", session.active_widgets)
                session.widget_positions = widget_config.get("positions", session.widget_positions)
                session.refresh_intervals = widget_config.get("refresh_intervals", session.refresh_intervals)
                session.filter_settings = widget_config.get("filters", session.filter_settings)
                
                self.db_session.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db_session.rollback()
            print(f"Failed to update widget configuration: {e}")
            return False


class AlertManager:
    """Manages dashboard alerts and notifications"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.alert_cache_ttl = 3600  # 1 hour
    
    async def create_alert(self, user_id: str, alert: DashboardAlert) -> bool:
        """Create new alert for user"""
        try:
            alert_key = f"alerts:{user_id}:{alert.id}"
            alert_data = json.dumps(alert.to_dict())
            
            # Store alert in Redis
            self.redis_client.setex(alert_key, self.alert_cache_ttl, alert_data)
            
            # Add to user's alert list
            user_alerts_key = f"user_alerts:{user_id}"
            self.redis_client.lpush(user_alerts_key, alert.id)
            self.redis_client.expire(user_alerts_key, self.alert_cache_ttl)
            
            return True
            
        except Exception as e:
            print(f"Failed to create alert: {e}")
            return False
    
    async def get_user_alerts(self, user_id: str) -> List[DashboardAlert]:
        """Get all active alerts for user"""
        try:
            user_alerts_key = f"user_alerts:{user_id}"
            alert_ids = self.redis_client.lrange(user_alerts_key, 0, -1)
            
            alerts = []
            for alert_id in alert_ids:
                alert_key = f"alerts:{user_id}:{alert_id.decode()}"
                alert_data = self.redis_client.get(alert_key)
                
                if alert_data:
                    alert_dict = json.loads(alert_data)
                    alert = DashboardAlert(
                        id=alert_dict["id"],
                        title=alert_dict["title"],
                        message=alert_dict["message"],
                        severity=AlertSeverity(alert_dict["severity"]),
                        widget_type=DashboardWidget(alert_dict["widget_type"]),
                        timestamp=datetime.fromisoformat(alert_dict["timestamp"]),
                        action_required=alert_dict["action_required"],
                        auto_dismiss=alert_dict["auto_dismiss"],
                        dismiss_after=alert_dict["dismiss_after"]
                    )
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            print(f"Failed to get user alerts: {e}")
            return []
    
    async def get_new_alerts(self, user_id: str, since: datetime = None) -> List[DashboardAlert]:
        """Get new alerts since last check"""
        if since is None:
            since = datetime.utcnow() - timedelta(minutes=5)
        
        all_alerts = await self.get_user_alerts(user_id)
        new_alerts = [alert for alert in all_alerts if alert.timestamp > since]
        
        return new_alerts
    
    async def dismiss_alert(self, user_id: str, alert_id: str) -> bool:
        """Dismiss specific alert"""
        try:
            alert_key = f"alerts:{user_id}:{alert_id}"
            user_alerts_key = f"user_alerts:{user_id}"
            
            # Remove from Redis
            self.redis_client.delete(alert_key)
            self.redis_client.lrem(user_alerts_key, 0, alert_id)
            
            return True
            
        except Exception as e:
            print(f"Failed to dismiss alert: {e}")
            return False


# Export main classes and utilities
__all__ = [
    "RealTimeDashboard",
    "AlertManager", 
    "DashboardAlert",
    "RealTimeMetric",
    "DashboardSession",
    "DashboardMetrics",
    "DashboardWidget",
    "MetricTimeframe",
    "AlertSeverity"
]
