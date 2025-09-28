"""
📊 Platform Analytics Service
Enterprise analytics and metrics collection service

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)


class PlatformAnalyticsService:
    """Platform Analytics Service for metrics collection and analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_cache: Dict[str, Any] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.logger.info("✅ PlatformAnalyticsService initialized")
    
    async def track_event(self, event_name: str, properties: Dict[str, Any]) -> bool:
        """Track an analytics event"""
        try:
            event = {
                "event_name": event_name,
                "properties": properties,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": properties.get("session_id", "unknown")
            }
            
            self.event_history.append(event)
            
            # Keep only last 10000 events
            if len(self.event_history) > 10000:
                self.event_history = self.event_history[-10000:]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to track event {event_name}: {str(e)}")
            return False
    
    async def get_metrics(self, metric_type: str, time_range: str = "24h") -> Dict[str, Any]:
        """Get platform metrics"""
        try:
            # Calculate time range
            now = datetime.utcnow()
            if time_range == "1h":
                start_time = now - timedelta(hours=1)
            elif time_range == "24h":
                start_time = now - timedelta(days=1)
            elif time_range == "7d":
                start_time = now - timedelta(days=7)
            else:
                start_time = now - timedelta(days=1)
            
            # Filter events in time range
            recent_events = [
                event for event in self.event_history
                if datetime.fromisoformat(event["timestamp"]) >= start_time
            ]
            
            metrics = {
                "total_events": len(recent_events),
                "unique_sessions": len(set(event["session_id"] for event in recent_events)),
                "time_range": time_range,
                "start_time": start_time.isoformat(),
                "end_time": now.isoformat(),
                "event_breakdown": {}
            }
            
            # Count events by type
            for event in recent_events:
                event_name = event["event_name"]
                metrics["event_breakdown"][event_name] = metrics["event_breakdown"].get(event_name, 0) + 1
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {str(e)}")
            return {"error": str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "PlatformAnalyticsService",
            "status": "healthy",
            "total_events": len(self.event_history),
            "cached_metrics": len(self.metrics_cache),
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['PlatformAnalyticsService']