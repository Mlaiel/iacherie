"""Content Tracker - Real-time Content Performance Tracking Engine
===============================================================

The ContentTracker monitors content performance, engagement metrics,
and monetization data across all platforms in real-time.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from ..cache.redis_client import RedisClient
from ..analytics.metrics_collector import MetricsCollector
from ..platforms.analytics_aggregator import AnalyticsAggregator


@dataclass
class TrackingMetrics:
    """Content tracking metrics container"""
    content_id: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    downloads: int = 0
    revenue: float = 0.0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    watch_time: int = 0  # in seconds
    retention_rate: float = 0.0


@dataclass
class TrackingConfig:
    """Content tracking configuration"""
    enable_real_time: bool = True
    tracking_interval: int = 300  # seconds
    metrics_to_track: List[str] = None
    alert_thresholds: Dict[str, float] = None
    platforms_to_monitor: List[str] = None


class ContentTracker:
    """
    Real-time Content Performance Tracking Engine
    
    Provides comprehensive tracking of content performance across
    multiple platforms with real-time analytics, alerts, and insights.
    
    Features:
    - Real-time metrics collection
    - Multi-platform analytics aggregation
    - Performance trend analysis
    - Automated alerts and notifications
    - Revenue tracking and reporting
    - Engagement optimization insights
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        redis_client: RedisClient,
        config: TrackingConfig = None
    ):
        self.db = db_session
        self.redis = redis_client
        self.config = config or TrackingConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize analytics components
        self.metrics_collector = MetricsCollector()
        self.analytics_aggregator = AnalyticsAggregator()
        
        # Tracking state
        self.active_tracking = {}
        self.tracking_tasks = {}

    async def start_tracking(
        self,
        content_id: str,
        platforms: List[str] = None,
        custom_config: TrackingConfig = None
    ) -> Dict[str, Any]:
        """
        Start tracking content performance
        
        Args:
            content_id: Content identifier
            platforms: Platforms to monitor
            custom_config: Custom tracking configuration
            
        Returns:
            Tracking initialization result
        """
        try:
            config = custom_config or self.config
            tracking_id = str(uuid.uuid4())
            
            self.logger.info(f"Starting tracking {tracking_id} for content {content_id}")
            
            # Initialize tracking state
            self.active_tracking[content_id] = {
                "tracking_id": tracking_id,
                "content_id": content_id,
                "platforms": platforms or ["youtube", "instagram", "tiktok", "spotify"],
                "config": config,
                "started_at": datetime.utcnow(),
                "last_update": datetime.utcnow(),
                "current_metrics": TrackingMetrics(content_id=content_id),
                "historical_data": []
            }
            
            # Start background tracking task
            if config.enable_real_time:
                task = asyncio.create_task(
                    self._background_tracking_loop(content_id, config)
                )
                self.tracking_tasks[content_id] = task
            
            # Initial metrics collection
            initial_metrics = await self._collect_current_metrics(content_id, platforms)
            
            # Cache initial state
            await self._cache_tracking_data(content_id, initial_metrics)
            
            return {
                "success": True,
                "tracking_id": tracking_id,
                "content_id": content_id,
                "platforms": platforms,
                "initial_metrics": self._serialize_metrics(initial_metrics),
                "tracking_started": True,
                "real_time_enabled": config.enable_real_time
            }
            
        except Exception as e:
            error_msg = f"Failed to start tracking: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id
            }

    async def _background_tracking_loop(
        self,
        content_id: str,
        config: TrackingConfig
    ) -> None:
        """
        Background loop for real-time tracking
        
        Args:
            content_id: Content identifier
            config: Tracking configuration
        """
        while content_id in self.active_tracking:
            try:
                # Collect current metrics
                platforms = self.active_tracking[content_id]["platforms"]
                current_metrics = await self._collect_current_metrics(content_id, platforms)
                
                # Update tracking state
                tracking_state = self.active_tracking[content_id]
                previous_metrics = tracking_state["current_metrics"]
                tracking_state["current_metrics"] = current_metrics
                tracking_state["last_update"] = datetime.utcnow()
                
                # Store historical data
                tracking_state["historical_data"].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": self._serialize_metrics(current_metrics)
                })
                
                # Keep only last 1000 data points
                if len(tracking_state["historical_data"]) > 1000:
                    tracking_state["historical_data"] = tracking_state["historical_data"][-1000:]
                
                # Cache updated data
                await self._cache_tracking_data(content_id, current_metrics)
                
                # Check for alerts
                await self._check_alert_thresholds(content_id, current_metrics, previous_metrics)
                
                # Save to database periodically
                if len(tracking_state["historical_data"]) % 10 == 0:  # Every 10 updates
                    await self._save_tracking_data(content_id, current_metrics)
                
                # Wait for next collection interval
                await asyncio.sleep(config.tracking_interval)
                
            except Exception as e:
                self.logger.error(f"Tracking loop error for {content_id}: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _collect_current_metrics(
        self,
        content_id: str,
        platforms: List[str]
    ) -> TrackingMetrics:
        """
        Collect current metrics from all platforms
        
        Args:
            content_id: Content identifier
            platforms: Platforms to collect from
            
        Returns:
            Aggregated metrics
        """
        try:
            platform_metrics = {}
            
            # Collect from each platform
            for platform in platforms:
                try:
                    metrics = await self.metrics_collector.collect_platform_metrics(
                        content_id, platform
                    )
                    platform_metrics[platform] = metrics
                except Exception as e:
                    self.logger.warning(f"Failed to collect metrics from {platform}: {str(e)}")
                    platform_metrics[platform] = {}
            
            # Aggregate metrics across platforms
            aggregated = await self.analytics_aggregator.aggregate_metrics(platform_metrics)
            
            return TrackingMetrics(
                content_id=content_id,
                views=aggregated.get("total_views", 0),
                likes=aggregated.get("total_likes", 0),
                shares=aggregated.get("total_shares", 0),
                comments=aggregated.get("total_comments", 0),
                downloads=aggregated.get("total_downloads", 0),
                revenue=aggregated.get("total_revenue", 0.0),
                engagement_rate=aggregated.get("engagement_rate", 0.0),
                reach=aggregated.get("total_reach", 0),
                impressions=aggregated.get("total_impressions", 0),
                click_through_rate=aggregated.get("ctr", 0.0),
                conversion_rate=aggregated.get("conversion_rate", 0.0),
                watch_time=aggregated.get("total_watch_time", 0),
                retention_rate=aggregated.get("retention_rate", 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics for {content_id}: {str(e)}")
            return TrackingMetrics(content_id=content_id)

    async def get_current_metrics(self, content_id: str) -> Dict[str, Any]:
        """
        Get current tracking metrics for content
        
        Args:
            content_id: Content identifier
            
        Returns:
            Current metrics and tracking status
        """
        try:
            # Check if content is being tracked
            if content_id not in self.active_tracking:
                return {
                    "success": False,
                    "error": "Content is not being tracked",
                    "content_id": content_id
                }
            
            tracking_state = self.active_tracking[content_id]
            current_metrics = tracking_state["current_metrics"]
            
            # Get trend analysis
            trend_analysis = await self._analyze_trends(content_id)
            
            return {
                "success": True,
                "content_id": content_id,
                "tracking_id": tracking_state["tracking_id"],
                "current_metrics": self._serialize_metrics(current_metrics),
                "last_updated": tracking_state["last_update"].isoformat(),
                "tracking_duration": (
                    datetime.utcnow() - tracking_state["started_at"]
                ).total_seconds(),
                "trend_analysis": trend_analysis,
                "is_tracking": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get metrics: {str(e)}",
                "content_id": content_id
            }

    async def get_historical_data(
        self,
        content_id: str,
        start_time: datetime = None,
        end_time: datetime = None,
        interval: str = "hour"
    ) -> Dict[str, Any]:
        """
        Get historical tracking data for content
        
        Args:
            content_id: Content identifier
            start_time: Start of time range
            end_time: End of time range
            interval: Data aggregation interval
            
        Returns:
            Historical metrics data
        """
        try:
            if content_id not in self.active_tracking:
                return {
                    "success": False,
                    "error": "Content is not being tracked",
                    "content_id": content_id
                }
            
            tracking_state = self.active_tracking[content_id]
            historical_data = tracking_state["historical_data"]
            
            # Filter by time range if specified
            if start_time or end_time:
                filtered_data = []
                for data_point in historical_data:
                    timestamp = datetime.fromisoformat(data_point["timestamp"])
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    filtered_data.append(data_point)
                historical_data = filtered_data
            
            # Aggregate by interval if needed
            if interval != "raw":
                historical_data = await self._aggregate_by_interval(historical_data, interval)
            
            return {
                "success": True,
                "content_id": content_id,
                "historical_data": historical_data,
                "data_points": len(historical_data),
                "time_range": {
                    "start": start_time.isoformat() if start_time else None,
                    "end": end_time.isoformat() if end_time else None
                },
                "interval": interval
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get historical data: {str(e)}",
                "content_id": content_id
            }

    async def _analyze_trends(self, content_id: str) -> Dict[str, Any]:
        """
        Analyze performance trends for content
        
        Args:
            content_id: Content identifier
            
        Returns:
            Trend analysis results
        """
        try:
            if content_id not in self.active_tracking:
                return {}
            
            historical_data = self.active_tracking[content_id]["historical_data"]
            
            if len(historical_data) < 2:
                return {"status": "insufficient_data"}
            
            # Calculate trends for key metrics
            recent_data = historical_data[-10:]  # Last 10 data points
            older_data = historical_data[-20:-10] if len(historical_data) >= 20 else historical_data[:-10]
            
            if not older_data:
                return {"status": "insufficient_data"}
            
            trends = {}
            metrics_to_analyze = ["views", "likes", "shares", "comments", "revenue", "engagement_rate"]
            
            for metric in metrics_to_analyze:
                recent_avg = self._calculate_average_metric(recent_data, metric)
                older_avg = self._calculate_average_metric(older_data, metric)
                
                if older_avg > 0:
                    change_percentage = ((recent_avg - older_avg) / older_avg) * 100
                    trends[metric] = {
                        "change_percentage": round(change_percentage, 2),
                        "trend": "increasing" if change_percentage > 5 else "decreasing" if change_percentage < -5 else "stable",
                        "recent_average": recent_avg,
                        "previous_average": older_avg
                    }
            
            return {
                "status": "success",
                "trends": trends,
                "analysis_period": {
                    "recent_points": len(recent_data),
                    "comparison_points": len(older_data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed for {content_id}: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _calculate_average_metric(self, data_points: List[Dict], metric: str) -> float:
        """Calculate average value for a metric across data points"""
        values = []
        for point in data_points:
            if "metrics" in point and metric in point["metrics"]:
                values.append(point["metrics"][metric])
        
        return sum(values) / len(values) if values else 0.0

    async def _check_alert_thresholds(
        self,
        content_id: str,
        current_metrics: TrackingMetrics,
        previous_metrics: TrackingMetrics
    ) -> None:
        """
        Check if any alert thresholds have been triggered
        
        Args:
            content_id: Content identifier
            current_metrics: Current performance metrics
            previous_metrics: Previous performance metrics
        """
        try:
            config = self.active_tracking[content_id]["config"]
            
            if not config.alert_thresholds:
                return
            
            alerts_triggered = []
            
            # Check each threshold
            for metric, threshold in config.alert_thresholds.items():
                current_value = getattr(current_metrics, metric, 0)
                previous_value = getattr(previous_metrics, metric, 0)
                
                # Check for sudden spikes or drops
                if previous_value > 0:
                    change_percentage = ((current_value - previous_value) / previous_value) * 100
                    
                    if abs(change_percentage) > threshold:
                        alerts_triggered.append({
                            "metric": metric,
                            "current_value": current_value,
                            "previous_value": previous_value,
                            "change_percentage": change_percentage,
                            "threshold": threshold,
                            "alert_type": "spike" if change_percentage > 0 else "drop"
                        })
            
            # Send alerts if any triggered
            if alerts_triggered:
                await self._send_alerts(content_id, alerts_triggered)
                
        except Exception as e:
            self.logger.error(f"Alert checking failed for {content_id}: {str(e)}")

    async def _send_alerts(self, content_id: str, alerts: List[Dict]) -> None:
        """Send alert notifications"""
        try:
            # Cache alerts for retrieval
            await self.redis.set(
                f"alerts:{content_id}",
                {
                    "content_id": content_id,
                    "alerts": alerts,
                    "timestamp": datetime.utcnow().isoformat()
                },
                expire=86400  # 24 hours
            )
            
            # Log alerts
            for alert in alerts:
                self.logger.warning(
                    f"Alert triggered for content {content_id}: "
                    f"{alert['metric']} changed by {alert['change_percentage']:.2f}% "
                    f"(threshold: {alert['threshold']}%)"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to send alerts for {content_id}: {str(e)}")

    async def stop_tracking(self, content_id: str) -> Dict[str, Any]:
        """
        Stop tracking content performance
        
        Args:
            content_id: Content identifier
            
        Returns:
            Stop tracking result
        """
        try:
            if content_id not in self.active_tracking:
                return {
                    "success": False,
                    "error": "Content is not being tracked",
                    "content_id": content_id
                }
            
            # Cancel background task
            if content_id in self.tracking_tasks:
                self.tracking_tasks[content_id].cancel()
                del self.tracking_tasks[content_id]
            
            # Get final metrics
            final_metrics = self.active_tracking[content_id]["current_metrics"]
            tracking_duration = (
                datetime.utcnow() - self.active_tracking[content_id]["started_at"]
            ).total_seconds()
            
            # Save final data
            await self._save_tracking_data(content_id, final_metrics)
            
            # Remove from active tracking
            del self.active_tracking[content_id]
            
            # Clear cache
            await self.redis.delete(f"tracking:{content_id}")
            
            return {
                "success": True,
                "content_id": content_id,
                "final_metrics": self._serialize_metrics(final_metrics),
                "tracking_duration": tracking_duration,
                "tracking_stopped": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stop tracking: {str(e)}",
                "content_id": content_id
            }

    async def _cache_tracking_data(self, content_id: str, metrics: TrackingMetrics) -> None:
        """Cache tracking data in Redis"""
        try:
            cache_data = {
                "content_id": content_id,
                "metrics": self._serialize_metrics(metrics),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            await self.redis.set(
                f"tracking:{content_id}",
                cache_data,
                expire=3600  # 1 hour
            )
            
        except Exception as e:
            self.logger.error(f"Failed to cache tracking data for {content_id}: {str(e)}")

    async def _save_tracking_data(self, content_id: str, metrics: TrackingMetrics) -> None:
        """Save tracking data to database"""
        try:
            # This would save to the actual database
            # Implementation would include proper database models
            pass
            
        except Exception as e:
            self.logger.error(f"Failed to save tracking data for {content_id}: {str(e)}")

    def _serialize_metrics(self, metrics: TrackingMetrics) -> Dict[str, Any]:
        """Convert metrics to serializable format"""
        return {
            "content_id": metrics.content_id,
            "views": metrics.views,
            "likes": metrics.likes,
            "shares": metrics.shares,
            "comments": metrics.comments,
            "downloads": metrics.downloads,
            "revenue": metrics.revenue,
            "engagement_rate": metrics.engagement_rate,
            "reach": metrics.reach,
            "impressions": metrics.impressions,
            "click_through_rate": metrics.click_through_rate,
            "conversion_rate": metrics.conversion_rate,
            "watch_time": metrics.watch_time,
            "retention_rate": metrics.retention_rate
        }

    async def track_content_deletion(self, content_id: str, user_id: int) -> None:
        """Track content deletion event"""
        try:
            # Stop tracking if active
            if content_id in self.active_tracking:
                await self.stop_tracking(content_id)
            
            # Log deletion event
            self.logger.info(f"Content {content_id} deleted by user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to track content deletion: {str(e)}")

    async def get_performance_summary(self, content_id: str) -> Dict[str, Any]:
        """
        Get comprehensive performance summary for content
        
        Args:
            content_id: Content identifier
            
        Returns:
            Performance summary with insights
        """
        try:
            current_metrics_result = await self.get_current_metrics(content_id)
            
            if not current_metrics_result["success"]:
                return current_metrics_result
            
            # Get trend analysis
            trends = await self._analyze_trends(content_id)
            
            # Calculate performance score
            performance_score = await self._calculate_performance_score(content_id)
            
            # Get platform breakdown
            platform_breakdown = await self._get_platform_breakdown(content_id)
            
            return {
                "success": True,
                "content_id": content_id,
                "current_metrics": current_metrics_result["current_metrics"],
                "trends": trends,
                "performance_score": performance_score,
                "platform_breakdown": platform_breakdown,
                "insights": await self._generate_performance_insights(content_id)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get performance summary: {str(e)}",
                "content_id": content_id
            }

    async def _calculate_performance_score(self, content_id: str) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            if content_id not in self.active_tracking:
                return 0.0
            
            metrics = self.active_tracking[content_id]["current_metrics"]
            
            # Weighted scoring based on different metrics
            scores = []
            
            # Engagement score (0-30 points)
            if metrics.engagement_rate > 0:
                engagement_score = min(30, metrics.engagement_rate * 10)
                scores.append(engagement_score)
            
            # Growth score (0-25 points)
            trends = await self._analyze_trends(content_id)
            if trends.get("status") == "success":
                positive_trends = sum(
                    1 for trend in trends["trends"].values()
                    if trend["trend"] == "increasing"
                )
                growth_score = (positive_trends / len(trends["trends"])) * 25
                scores.append(growth_score)
            
            # Revenue score (0-25 points)
            if metrics.revenue > 0:
                revenue_score = min(25, metrics.revenue / 100)  # $1 = 0.25 points
                scores.append(revenue_score)
            
            # Reach score (0-20 points)
            if metrics.reach > 0:
                reach_score = min(20, metrics.reach / 1000)  # 1000 reach = 1 point
                scores.append(reach_score)
            
            return sum(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Performance score calculation failed: {str(e)}")
            return 0.0

    async def _get_platform_breakdown(self, content_id: str) -> Dict[str, Any]:
        """Get performance breakdown by platform"""
        try:
            if content_id not in self.active_tracking:
                return {}
            
            platforms = self.active_tracking[content_id]["platforms"]
            breakdown = {}
            
            for platform in platforms:
                platform_metrics = await self.metrics_collector.collect_platform_metrics(
                    content_id, platform
                )
                breakdown[platform] = platform_metrics
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"Platform breakdown failed: {str(e)}")
            return {}

    async def _generate_performance_insights(self, content_id: str) -> List[str]:
        """Generate AI-powered performance insights"""
        try:
            insights = []
            
            if content_id not in self.active_tracking:
                return insights
            
            metrics = self.active_tracking[content_id]["current_metrics"]
            trends = await self._analyze_trends(content_id)
            
            # Engagement insights
            if metrics.engagement_rate < 0.02:  # Less than 2%
                insights.append("Low engagement rate detected. Consider improving content quality or posting time.")
            elif metrics.engagement_rate > 0.1:  # Greater than 10%
                insights.append("Excellent engagement rate! This content is performing very well.")
            
            # Growth insights
            if trends.get("status") == "success":
                declining_metrics = [
                    metric for metric, data in trends["trends"].items()
                    if data["trend"] == "decreasing"
                ]
                if declining_metrics:
                    insights.append(f"Declining performance in: {', '.join(declining_metrics)}. Consider content optimization.")
            
            # Revenue insights
            if metrics.revenue > 0:
                insights.append(f"Content is generating revenue: ${metrics.revenue:.2f}. Consider monetization optimization.")
            else:
                insights.append("No revenue detected. Consider enabling monetization features.")
            
            # Platform-specific insights
            platform_breakdown = await self._get_platform_breakdown(content_id)
            best_platform = max(
                platform_breakdown.items(),
                key=lambda x: x[1].get("total_views", 0),
                default=(None, {})
            )[0]
            
            if best_platform:
                insights.append(f"Best performing platform: {best_platform}. Consider focusing content strategy here.")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Insights generation failed: {str(e)}")
            return []

    async def _aggregate_by_interval(self, data_points: List[Dict], interval: str) -> List[Dict]:
        """Aggregate data points by time interval"""
        # Implementation for data aggregation by hour/day/week/month
        # This is a simplified version
        return data_points  # Return as-is for now
