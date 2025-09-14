"""
Communication Analytics Service
==============================

Advanced analytics service for communication patterns and engagement metrics.
Provides insights into creator communication effectiveness and user engagement.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class AnalyticsMetric(Enum):
    """Communication analytics metrics"""
    MESSAGE_VOLUME = "message_volume"
    RESPONSE_TIME = "response_time"
    ENGAGEMENT_RATE = "engagement_rate"
    CHANNEL_EFFECTIVENESS = "channel_effectiveness"
    USER_SATISFACTION = "user_satisfaction"

class TimeFrame(Enum):
    """Time frame for analytics"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class CommunicationAnalytics:
    """
    Communication Analytics Service
    
    Provides comprehensive analytics for communication patterns,
    engagement metrics, and optimization insights.
    """
    
    def __init__(self):
        self.analytics_data = {}
        self.engagement_metrics = {}
        self.channel_performance = {}
        self.user_behavior = {}
        self.is_active = False
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize communication analytics service"""
        try:
            logger.info("Initializing Communication Analytics Service...")
            
            # Setup analytics collection
            await self._setup_analytics_collection()
            
            # Start analytics processing
            asyncio.create_task(self._analytics_processing_loop())
            
            self.is_active = True
            
            return {
                "status": "success",
                "service": "communication_analytics",
                "metrics_tracked": len(AnalyticsMetric)
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize communication analytics: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _setup_analytics_collection(self):
        """Setup analytics data collection"""
        # Initialize metric storage
        for metric in AnalyticsMetric:
            self.analytics_data[metric.value] = {}
            
        # Initialize channel performance tracking
        self.channel_performance = {
            "email": {"sent": 0, "opened": 0, "clicked": 0, "bounced": 0},
            "push": {"sent": 0, "delivered": 0, "opened": 0, "clicked": 0},
            "chat": {"messages": 0, "responses": 0, "avg_response_time": 0},
            "video": {"calls": 0, "duration": 0, "quality_score": 0},
            "sms": {"sent": 0, "delivered": 0, "replied": 0}
        }
    
    async def track_communication_event(
        self,
        event_type: str,
        channel: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track a communication event"""
        try:
            event_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "channel": channel,
                "user_id": user_id,
                "metadata": metadata or {}
            }
            
            # Update channel performance
            if channel in self.channel_performance:
                await self._update_channel_performance(channel, event_type, metadata)
            
            # Update user behavior
            await self._update_user_behavior(user_id, event_type, channel)
            
            # Store event for analytics
            await self._store_analytics_event(event_data)
            
            return {
                "status": "success",
                "event_tracked": event_type,
                "channel": channel
            }
            
        except Exception as e:
            logger.error(f"Failed to track communication event: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _update_channel_performance(
        self,
        channel: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]]
    ):
        """Update channel performance metrics"""
        if channel not in self.channel_performance:
            return
        
        perf = self.channel_performance[channel]
        
        if event_type == "sent":
            perf["sent"] += 1
        elif event_type == "delivered":
            perf["delivered"] += 1
        elif event_type == "opened":
            perf["opened"] += 1
        elif event_type == "clicked":
            perf["clicked"] += 1
        elif event_type == "bounced":
            perf["bounced"] += 1
        elif event_type == "response" and metadata:
            perf["responses"] += 1
            if "response_time" in metadata:
                # Update average response time
                current_avg = perf.get("avg_response_time", 0)
                response_count = perf.get("responses", 1)
                new_avg = ((current_avg * (response_count - 1)) + metadata["response_time"]) / response_count
                perf["avg_response_time"] = new_avg
    
    async def _update_user_behavior(self, user_id: str, event_type: str, channel: str):
        """Update user behavior analytics"""
        if user_id not in self.user_behavior:
            self.user_behavior[user_id] = {
                "total_interactions": 0,
                "channels_used": set(),
                "last_activity": None,
                "response_patterns": {}
            }
        
        user_data = self.user_behavior[user_id]
        user_data["total_interactions"] += 1
        user_data["channels_used"].add(channel)
        user_data["last_activity"] = datetime.utcnow().isoformat()
        
        # Track response patterns
        if event_type not in user_data["response_patterns"]:
            user_data["response_patterns"][event_type] = 0
        user_data["response_patterns"][event_type] += 1
    
    async def _store_analytics_event(self, event_data: Dict[str, Any]):
        """Store analytics event for processing"""
        timestamp = event_data["timestamp"]
        hour_key = timestamp[:13]  # YYYY-MM-DDTHH
        
        # Store in hourly buckets for efficient processing
        if hour_key not in self.analytics_data:
            self.analytics_data[hour_key] = []
        
        self.analytics_data[hour_key].append(event_data)
    
    async def _analytics_processing_loop(self):
        """Continuous analytics processing loop"""
        while self.is_active:
            try:
                await self._process_analytics_data()
                await asyncio.sleep(300)  # Process every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in analytics processing loop: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _process_analytics_data(self):
        """Process accumulated analytics data"""
        current_time = datetime.utcnow()
        
        # Process hourly data that's at least 1 hour old
        for hour_key, events in list(self.analytics_data.items()):
            hour_time = datetime.fromisoformat(hour_key + ":00:00")
            
            if current_time - hour_time >= timedelta(hours=1):
                await self._aggregate_hourly_data(hour_key, events)
                # Remove processed data
                del self.analytics_data[hour_key]
    
    async def _aggregate_hourly_data(self, hour_key: str, events: List[Dict[str, Any]]):
        """Aggregate hourly analytics data"""
        aggregated = {
            "hour": hour_key,
            "total_events": len(events),
            "channels": {},
            "event_types": {},
            "unique_users": set()
        }
        
        for event in events:
            # Channel breakdown
            channel = event["channel"]
            if channel not in aggregated["channels"]:
                aggregated["channels"][channel] = 0
            aggregated["channels"][channel] += 1
            
            # Event type breakdown
            event_type = event["event_type"]
            if event_type not in aggregated["event_types"]:
                aggregated["event_types"][event_type] = 0
            aggregated["event_types"][event_type] += 1
            
            # Unique users
            aggregated["unique_users"].add(event["user_id"])
        
        # Convert set to count for storage
        aggregated["unique_users"] = len(aggregated["unique_users"])
        
        # Store aggregated data
        self.engagement_metrics[hour_key] = aggregated
    
    async def get_engagement_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        time_frame: TimeFrame = TimeFrame.DAILY
    ) -> Dict[str, Any]:
        """Generate engagement analytics report"""
        try:
            end_time = end_time or datetime.utcnow()
            start_time = start_time or (end_time - timedelta(days=7))
            
            # Filter data by time range
            filtered_data = []
            for hour_key, data in self.engagement_metrics.items():
                hour_time = datetime.fromisoformat(hour_key + ":00:00")
                if start_time <= hour_time <= end_time:
                    filtered_data.append(data)
            
            if not filtered_data:
                return {
                    "status": "success",
                    "report": {"message": "No data available for the specified time range"}
                }
            
            # Aggregate data based on time frame
            aggregated_report = await self._aggregate_by_timeframe(filtered_data, time_frame)
            
            return {
                "status": "success",
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "time_frame": time_frame.value,
                "report": aggregated_report
            }
            
        except Exception as e:
            logger.error(f"Failed to generate engagement report: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _aggregate_by_timeframe(
        self,
        data: List[Dict[str, Any]],
        time_frame: TimeFrame
    ) -> Dict[str, Any]:
        """Aggregate data by specified time frame"""
        total_events = sum(d["total_events"] for d in data)
        total_unique_users = len(set().union(*[d.get("unique_users", []) for d in data]))
        
        # Channel performance
        channel_totals = {}
        for d in data:
            for channel, count in d.get("channels", {}).items():
                channel_totals[channel] = channel_totals.get(channel, 0) + count
        
        # Event type distribution
        event_type_totals = {}
        for d in data:
            for event_type, count in d.get("event_types", {}).items():
                event_type_totals[event_type] = event_type_totals.get(event_type, 0) + count
        
        return {
            "summary": {
                "total_events": total_events,
                "unique_users": total_unique_users,
                "avg_events_per_user": total_events / total_unique_users if total_unique_users > 0 else 0,
                "data_points": len(data)
            },
            "channel_performance": channel_totals,
            "event_distribution": event_type_totals,
            "trends": await self._calculate_trends(data)
        }
    
    async def _calculate_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trends from time series data"""
        if len(data) < 2:
            return {"message": "Insufficient data for trend analysis"}
        
        # Sort by hour
        sorted_data = sorted(data, key=lambda x: x["hour"])
        
        # Calculate growth rates
        first_period = sorted_data[:len(sorted_data)//2]
        second_period = sorted_data[len(sorted_data)//2:]
        
        first_avg = sum(d["total_events"] for d in first_period) / len(first_period)
        second_avg = sum(d["total_events"] for d in second_period) / len(second_period)
        
        growth_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        return {
            "growth_rate_percent": round(growth_rate, 2),
            "trend_direction": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable",
            "first_period_avg": round(first_avg, 2),
            "second_period_avg": round(second_avg, 2)
        }
    
    async def get_channel_performance(self) -> Dict[str, Any]:
        """Get channel performance analytics"""
        try:
            performance_report = {}
            
            for channel, metrics in self.channel_performance.items():
                # Calculate performance ratios
                sent = metrics.get("sent", 0)
                delivered = metrics.get("delivered", 0)
                opened = metrics.get("opened", 0)
                clicked = metrics.get("clicked", 0)
                
                performance_report[channel] = {
                    "metrics": metrics,
                    "performance": {
                        "delivery_rate": (delivered / sent * 100) if sent > 0 else 0,
                        "open_rate": (opened / delivered * 100) if delivered > 0 else 0,
                        "click_rate": (clicked / opened * 100) if opened > 0 else 0,
                        "engagement_score": await self._calculate_engagement_score(metrics)
                    }
                }
            
            return {
                "status": "success",
                "channel_performance": performance_report,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get channel performance: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _calculate_engagement_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate engagement score for a channel"""
        # Simplified engagement score calculation
        sent = metrics.get("sent", 0)
        opened = metrics.get("opened", 0)
        clicked = metrics.get("clicked", 0)
        responses = metrics.get("responses", 0)
        
        if sent == 0:
            return 0
        
        # Weighted engagement score
        score = (
            (opened / sent * 0.3) +
            (clicked / sent * 0.4) +
            (responses / sent * 0.3)
        ) * 100
        
        return round(score, 2)
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get communication insights for a specific user"""
        try:
            if user_id not in self.user_behavior:
                return {
                    "status": "success",
                    "user_id": user_id,
                    "insights": {"message": "No communication data available for this user"}
                }
            
            user_data = self.user_behavior[user_id]
            
            # Convert set to list for JSON serialization
            channels_used = list(user_data["channels_used"])
            
            insights = {
                "summary": {
                    "total_interactions": user_data["total_interactions"],
                    "channels_used": channels_used,
                    "preferred_channel": max(channels_used, key=lambda c: sum(
                        1 for pattern in user_data["response_patterns"].items()
                        if c in pattern[0]
                    )) if channels_used else None,
                    "last_activity": user_data["last_activity"]
                },
                "response_patterns": user_data["response_patterns"],
                "engagement_level": await self._calculate_user_engagement_level(user_data)
            }
            
            return {
                "status": "success",
                "user_id": user_id,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Failed to get user insights: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _calculate_user_engagement_level(self, user_data: Dict[str, Any]) -> str:
        """Calculate user engagement level"""
        total_interactions = user_data["total_interactions"]
        channels_count = len(user_data["channels_used"])
        
        if total_interactions >= 100 and channels_count >= 3:
            return "high"
        elif total_interactions >= 25 and channels_count >= 2:
            return "medium"
        elif total_interactions >= 5:
            return "low"
        else:
            return "minimal"
    
    async def get_service_analytics(self) -> Dict[str, Any]:
        """Get communication analytics service metrics"""
        return {
            "service": "communication_analytics",
            "metrics": {
                "tracked_channels": len(self.channel_performance),
                "total_users_tracked": len(self.user_behavior),
                "analytics_data_points": sum(len(events) for events in self.analytics_data.values()),
                "engagement_metrics": len(self.engagement_metrics),
                "active_processing": self.is_active
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "communication_analytics",
            "status": "healthy" if self.is_active else "inactive",
            "data_processing": self.is_active,
            "last_check": datetime.utcnow().isoformat()
        }