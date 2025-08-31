"""
Real-Time Trending Keywords System

This module provides real-time trending keyword detection and analysis
with automated monitoring and alerting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta
import websockets
from collections import deque, defaultdict
import threading
import time

logger = logging.getLogger(__name__)


class TrendSource(Enum):
    """Sources for trending data"""
    GOOGLE_TRENDS = "google_trends"
    TWITTER_API = "twitter_api"
    REDDIT_API = "reddit_api"
    YOUTUBE_TRENDING = "youtube_trending"
    SOCIAL_MENTIONS = "social_mentions"
    NEWS_API = "news_api"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RealTimeTrendData:
    """Real-time trend data point"""
    keyword: str
    source: TrendSource
    volume: int
    growth_rate: float
    velocity: float
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class TrendAlert:
    """Trend alert configuration and data"""
    keyword_pattern: str
    threshold_type: str  # "volume", "growth_rate", "velocity"
    threshold_value: float
    severity: AlertSeverity
    callback: Optional[Callable] = None
    active: bool = True
    last_triggered: Optional[datetime] = None


@dataclass
class TrendingOpportunity:
    """Real-time trending opportunity"""
    keyword: str
    opportunity_score: float
    current_volume: int
    growth_rate: float
    velocity: float
    predicted_peak: datetime
    confidence: float
    related_keywords: List[str]
    sources: List[TrendSource]
    action_recommendations: List[str]


class RealTimeTrendingSystem:
    """
    Real-time trending keywords detection and monitoring system
    with automated alerts and opportunity identification.
    """
    
    def __init__(self, update_interval: int = 60):
        """
        Initialize the real-time trending system.
        
        Args:
            update_interval: Update interval in seconds
        """
        self.update_interval = update_interval
        self.trend_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1440))  # 24 hours of minute data
        self.alerts: List[TrendAlert] = []
        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.websocket_connections: Set = set()
        
        # Initialize trend sources
        self.trend_sources = {
            TrendSource.GOOGLE_TRENDS: self._get_google_trends_data,
            TrendSource.TWITTER_API: self._get_twitter_trends_data,
            TrendSource.REDDIT_API: self._get_reddit_trends_data,
            TrendSource.YOUTUBE_TRENDING: self._get_youtube_trends_data,
            TrendSource.NEWS_API: self._get_news_trends_data
        }
    
    def start_monitoring(self, keywords: List[str] = None):
        """Start real-time monitoring of trending keywords"""
        
        if self.is_monitoring:
            logger.warning("Monitoring is already active")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(keywords,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Started real-time trending keywords monitoring")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logger.info("Stopped real-time trending keywords monitoring")
    
    def add_alert(self, alert: TrendAlert):
        """Add a trend alert"""
        self.alerts.append(alert)
        logger.info(f"Added trend alert for pattern: {alert.keyword_pattern}")
    
    def remove_alert(self, keyword_pattern: str):
        """Remove trend alerts for a keyword pattern"""
        self.alerts = [alert for alert in self.alerts if alert.keyword_pattern != keyword_pattern]
        logger.info(f"Removed trend alerts for pattern: {keyword_pattern}")
    
    def subscribe_to_keyword(self, keyword: str, callback: Callable):
        """Subscribe to real-time updates for a specific keyword"""
        self.callbacks[keyword].append(callback)
        logger.info(f"Added callback for keyword: {keyword}")
    
    def get_current_trends(self, limit: int = 50) -> List[RealTimeTrendData]:
        """Get current trending keywords"""
        
        current_trends = []
        current_time = datetime.now()
        
        for keyword, data_points in self.trend_data.items():
            if data_points:
                latest_point = data_points[-1]
                
                # Only include recent data (within last 5 minutes)
                if (current_time - latest_point.timestamp).total_seconds() <= 300:
                    current_trends.append(latest_point)
        
        # Sort by growth rate and volume
        current_trends.sort(
            key=lambda x: (x.growth_rate * x.volume),
            reverse=True
        )
        
        return current_trends[:limit]
    
    def get_trending_opportunities(self, min_opportunity_score: float = 70.0) -> List[TrendingOpportunity]:
        """Identify trending opportunities in real-time"""
        
        opportunities = []
        current_trends = self.get_current_trends(100)
        
        for trend in current_trends:
            opportunity_score = self._calculate_real_time_opportunity_score(trend)
            
            if opportunity_score >= min_opportunity_score:
                # Predict peak time
                predicted_peak = self._predict_trend_peak(trend.keyword)
                
                # Get related keywords
                related_keywords = self._get_related_trending_keywords(trend.keyword)
                
                # Generate action recommendations
                action_recommendations = self._generate_action_recommendations(trend)
                
                opportunity = TrendingOpportunity(
                    keyword=trend.keyword,
                    opportunity_score=opportunity_score,
                    current_volume=trend.volume,
                    growth_rate=trend.growth_rate,
                    velocity=trend.velocity,
                    predicted_peak=predicted_peak,
                    confidence=self._calculate_trend_confidence(trend.keyword),
                    related_keywords=related_keywords,
                    sources=[trend.source],
                    action_recommendations=action_recommendations
                )
                
                opportunities.append(opportunity)
        
        return sorted(opportunities, key=lambda x: x.opportunity_score, reverse=True)
    
    def get_keyword_trend_history(self, keyword: str, hours: int = 24) -> List[RealTimeTrendData]:
        """Get trend history for a specific keyword"""
        
        if keyword not in self.trend_data:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = []
        
        for data_point in self.trend_data[keyword]:
            if data_point.timestamp >= cutoff_time:
                history.append(data_point)
        
        return history
    
    def _monitoring_loop(self, keywords: List[str] = None):
        """Main monitoring loop"""
        
        while self.is_monitoring:
            try:
                # Collect data from all sources
                asyncio.run(self._collect_trending_data(keywords))
                
                # Process alerts
                self._process_alerts()
                
                # Broadcast updates via WebSocket
                asyncio.run(self._broadcast_updates())
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Short delay before retrying
    
    async def _collect_trending_data(self, keywords: List[str] = None):
        """Collect trending data from all sources"""
        
        tasks = []
        
        for source, collector in self.trend_sources.items():
            task = asyncio.create_task(collector(keywords))
            tasks.append(task)
        
        # Wait for all collectors to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                source = list(self.trend_sources.keys())[i]
                logger.error(f"Error collecting from {source.value}: {str(result)}")
            elif result:
                self._process_trend_data(result)
    
    def _process_trend_data(self, trend_data: List[RealTimeTrendData]):
        """Process and store trending data"""
        
        for data_point in trend_data:
            # Store data point
            self.trend_data[data_point.keyword].append(data_point)
            
            # Calculate growth rate and velocity if we have historical data
            if len(self.trend_data[data_point.keyword]) > 1:
                data_point.growth_rate = self._calculate_growth_rate(data_point.keyword)
                data_point.velocity = self._calculate_velocity(data_point.keyword)
            
            # Trigger callbacks
            if data_point.keyword in self.callbacks:
                for callback in self.callbacks[data_point.keyword]:
                    try:
                        callback(data_point)
                    except Exception as e:
                        logger.error(f"Error in callback for {data_point.keyword}: {str(e)}")
    
    def _process_alerts(self):
        """Process trend alerts"""
        
        current_time = datetime.now()
        
        for alert in self.alerts:
            if not alert.active:
                continue
            
            # Skip if recently triggered (avoid spam)
            if (alert.last_triggered and 
                (current_time - alert.last_triggered).total_seconds() < 300):  # 5 minutes cooldown
                continue
            
            # Find matching keywords
            matching_keywords = self._find_matching_keywords(alert.keyword_pattern)
            
            for keyword in matching_keywords:
                if self._check_alert_threshold(keyword, alert):
                    self._trigger_alert(keyword, alert)
                    alert.last_triggered = current_time
    
    def _find_matching_keywords(self, pattern: str) -> List[str]:
        """Find keywords matching the alert pattern"""
        
        matching = []
        pattern_lower = pattern.lower()
        
        for keyword in self.trend_data.keys():
            if pattern_lower in keyword.lower() or keyword.lower() in pattern_lower:
                matching.append(keyword)
        
        return matching
    
    def _check_alert_threshold(self, keyword: str, alert: TrendAlert) -> bool:
        """Check if keyword meets alert threshold"""
        
        if keyword not in self.trend_data or not self.trend_data[keyword]:
            return False
        
        latest_data = self.trend_data[keyword][-1]
        
        if alert.threshold_type == "volume":
            return latest_data.volume >= alert.threshold_value
        elif alert.threshold_type == "growth_rate":
            return latest_data.growth_rate >= alert.threshold_value
        elif alert.threshold_type == "velocity":
            return latest_data.velocity >= alert.threshold_value
        
        return False
    
    def _trigger_alert(self, keyword: str, alert: TrendAlert):
        """Trigger a trend alert"""
        
        logger.info(f"TREND ALERT: {alert.severity.value.upper()} - {keyword} triggered {alert.threshold_type} threshold")
        
        if alert.callback:
            try:
                alert.callback(keyword, alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {str(e)}")
    
    async def _broadcast_updates(self):
        """Broadcast updates via WebSocket"""
        
        if not self.websocket_connections:
            return
        
        # Get recent updates
        recent_trends = self.get_current_trends(20)
        opportunities = self.get_trending_opportunities(60.0)
        
        update_data = {
            "timestamp": datetime.now().isoformat(),
            "trending_keywords": [
                {
                    "keyword": trend.keyword,
                    "volume": trend.volume,
                    "growth_rate": trend.growth_rate,
                    "source": trend.source.value
                }
                for trend in recent_trends
            ],
            "opportunities": [
                {
                    "keyword": opp.keyword,
                    "opportunity_score": opp.opportunity_score,
                    "growth_rate": opp.growth_rate,
                    "predicted_peak": opp.predicted_peak.isoformat()
                }
                for opp in opportunities[:10]
            ]
        }
        
        # Broadcast to all connected WebSocket clients
        message = json.dumps(update_data)
        disconnected = set()
        
        for websocket in self.websocket_connections:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {str(e)}")
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.websocket_connections -= disconnected
    
    def _calculate_growth_rate(self, keyword: str) -> float:
        """Calculate growth rate for a keyword"""
        
        data_points = self.trend_data[keyword]
        
        if len(data_points) < 2:
            return 0.0
        
        current_volume = data_points[-1].volume
        previous_volume = data_points[-2].volume
        
        if previous_volume == 0:
            return 100.0 if current_volume > 0 else 0.0
        
        growth_rate = ((current_volume - previous_volume) / previous_volume) * 100
        return round(growth_rate, 2)
    
    def _calculate_velocity(self, keyword: str) -> float:
        """Calculate velocity (rate of change) for a keyword"""
        
        data_points = self.trend_data[keyword]
        
        if len(data_points) < 3:
            return 0.0
        
        # Calculate average change over last 3 data points
        volumes = [dp.volume for dp in list(data_points)[-3:]]
        changes = [volumes[i] - volumes[i-1] for i in range(1, len(volumes))]
        
        avg_change = sum(changes) / len(changes)
        return round(avg_change, 2)
    
    def _calculate_real_time_opportunity_score(self, trend: RealTimeTrendData) -> float:
        """Calculate real-time opportunity score"""
        
        # Base score from volume (0-40 points)
        volume_score = min(40, trend.volume / 1000)
        
        # Growth rate score (0-35 points)
        growth_score = min(35, trend.growth_rate / 2)
        
        # Velocity score (0-15 points)
        velocity_score = min(15, abs(trend.velocity) / 100)
        
        # Recency bonus (0-10 points)
        time_diff = (datetime.now() - trend.timestamp).total_seconds()
        recency_score = max(0, 10 - (time_diff / 60))  # Decrease over 10 minutes
        
        total_score = volume_score + growth_score + velocity_score + recency_score
        return round(min(100, total_score), 2)
    
    def _predict_trend_peak(self, keyword: str) -> datetime:
        """Predict when a trend will peak"""
        
        data_points = list(self.trend_data[keyword])
        
        if len(data_points) < 3:
            # Default prediction: 2 hours from now
            return datetime.now() + timedelta(hours=2)
        
        # Simple prediction based on growth rate deceleration
        recent_points = data_points[-3:]
        growth_rates = []
        
        for i in range(1, len(recent_points)):
            prev_vol = recent_points[i-1].volume
            curr_vol = recent_points[i].volume
            
            if prev_vol > 0:
                growth_rate = (curr_vol - prev_vol) / prev_vol
                growth_rates.append(growth_rate)
        
        if growth_rates and len(growth_rates) > 1:
            # If growth is decelerating, predict peak sooner
            if growth_rates[-1] < growth_rates[-2]:
                hours_to_peak = 1
            else:
                hours_to_peak = 4
        else:
            hours_to_peak = 3
        
        return datetime.now() + timedelta(hours=hours_to_peak)
    
    def _get_related_trending_keywords(self, keyword: str) -> List[str]:
        """Get related trending keywords"""
        
        related = []
        keyword_words = set(keyword.lower().split())
        
        for other_keyword in self.trend_data.keys():
            if other_keyword != keyword:
                other_words = set(other_keyword.lower().split())
                
                # Check for word overlap
                if keyword_words.intersection(other_words):
                    related.append(other_keyword)
        
        return related[:5]  # Top 5 related
    
    def _generate_action_recommendations(self, trend: RealTimeTrendData) -> List[str]:
        """Generate action recommendations for a trend"""
        
        recommendations = []
        
        if trend.growth_rate > 100:
            recommendations.append("URGENT: Create content immediately to capitalize on viral trend")
        elif trend.growth_rate > 50:
            recommendations.append("HIGH PRIORITY: Develop content within 2 hours")
        elif trend.growth_rate > 20:
            recommendations.append("MEDIUM PRIORITY: Plan content for next 6 hours")
        
        if trend.volume > 10000:
            recommendations.append("High volume opportunity: Consider paid promotion")
        
        if trend.velocity > 500:
            recommendations.append("Fast-moving trend: Focus on real-time engagement")
        
        return recommendations
    
    def _calculate_trend_confidence(self, keyword: str) -> float:
        """Calculate confidence level for trend prediction"""
        
        data_points = list(self.trend_data[keyword])
        
        if len(data_points) < 3:
            return 0.5  # Low confidence with limited data
        
        # Higher confidence with more consistent growth
        recent_points = data_points[-5:]
        volumes = [dp.volume for dp in recent_points]
        
        # Check for consistent growth
        growing_points = sum(1 for i in range(1, len(volumes)) if volumes[i] > volumes[i-1])
        consistency_ratio = growing_points / (len(volumes) - 1) if len(volumes) > 1 else 0
        
        # Base confidence from data availability
        data_confidence = min(1.0, len(data_points) / 10)
        
        # Combine factors
        confidence = (consistency_ratio * 0.6) + (data_confidence * 0.4)
        return round(confidence, 2)
    
    # API Data Collection Methods (Simulated)
    async def _get_google_trends_data(self, keywords: List[str] = None) -> List[RealTimeTrendData]:
        """Get trending data from Google Trends (simulated)"""
        
        trending_data = []
        
        # Simulate Google Trends data
        simulated_trends = [
            "artificial intelligence", "cryptocurrency", "climate change",
            "remote work", "electric vehicles", "space exploration",
            "machine learning", "sustainable energy", "digital transformation"
        ]
        
        for trend in simulated_trends[:5]:
            volume = 5000 + (hash(trend + str(datetime.now().minute)) % 10000)
            
            trending_data.append(RealTimeTrendData(
                keyword=trend,
                source=TrendSource.GOOGLE_TRENDS,
                volume=volume,
                growth_rate=0.0,  # Will be calculated later
                velocity=0.0,     # Will be calculated later
                timestamp=datetime.now(),
                metadata={"region": "worldwide", "category": "all"}
            ))
        
        return trending_data
    
    async def _get_twitter_trends_data(self, keywords: List[str] = None) -> List[RealTimeTrendData]:
        """Get trending data from Twitter API (simulated)"""
        
        trending_data = []
        
        # Simulate Twitter trending data
        simulated_trends = [
            "breaking news", "viral video", "trending hashtag",
            "social media", "live event", "celebrity news"
        ]
        
        for trend in simulated_trends[:3]:
            volume = 8000 + (hash(trend + str(datetime.now().minute)) % 15000)
            
            trending_data.append(RealTimeTrendData(
                keyword=trend,
                source=TrendSource.TWITTER_API,
                volume=volume,
                growth_rate=0.0,
                velocity=0.0,
                timestamp=datetime.now(),
                metadata={"platform": "twitter", "tweet_count": volume}
            ))
        
        return trending_data
    
    async def _get_reddit_trends_data(self, keywords: List[str] = None) -> List[RealTimeTrendData]:
        """Get trending data from Reddit API (simulated)"""
        
        trending_data = []
        
        simulated_trends = [
            "reddit discussion", "community update", "popular meme",
            "ask reddit", "today i learned"
        ]
        
        for trend in simulated_trends[:2]:
            volume = 3000 + (hash(trend + str(datetime.now().minute)) % 8000)
            
            trending_data.append(RealTimeTrendData(
                keyword=trend,
                source=TrendSource.REDDIT_API,
                volume=volume,
                growth_rate=0.0,
                velocity=0.0,
                timestamp=datetime.now(),
                metadata={"platform": "reddit", "upvotes": volume}
            ))
        
        return trending_data
    
    async def _get_youtube_trends_data(self, keywords: List[str] = None) -> List[RealTimeTrendData]:
        """Get trending data from YouTube (simulated)"""
        
        trending_data = []
        
        simulated_trends = [
            "youtube video", "music video", "tutorial",
            "gaming stream", "product review"
        ]
        
        for trend in simulated_trends[:2]:
            volume = 4000 + (hash(trend + str(datetime.now().minute)) % 12000)
            
            trending_data.append(RealTimeTrendData(
                keyword=trend,
                source=TrendSource.YOUTUBE_TRENDING,
                volume=volume,
                growth_rate=0.0,
                velocity=0.0,
                timestamp=datetime.now(),
                metadata={"platform": "youtube", "views": volume * 10}
            ))
        
        return trending_data
    
    async def _get_news_trends_data(self, keywords: List[str] = None) -> List[RealTimeTrendData]:
        """Get trending data from News APIs (simulated)"""
        
        trending_data = []
        
        simulated_trends = [
            "breaking news", "world event", "technology news",
            "business update", "scientific discovery"
        ]
        
        for trend in simulated_trends[:2]:
            volume = 2000 + (hash(trend + str(datetime.now().minute)) % 6000)
            
            trending_data.append(RealTimeTrendData(
                keyword=trend,
                source=TrendSource.NEWS_API,
                volume=volume,
                growth_rate=0.0,
                velocity=0.0,
                timestamp=datetime.now(),
                metadata={"platform": "news", "articles": volume // 10}
            ))
        
        return trending_data


# WebSocket handler for real-time updates
async def handle_websocket_connection(websocket, path, trending_system: RealTimeTrendingSystem):
    """Handle WebSocket connections for real-time updates"""
    
    trending_system.websocket_connections.add(websocket)
    logger.info("New WebSocket connection established")
    
    try:
        # Send initial data
        current_trends = trending_system.get_current_trends(20)
        opportunities = trending_system.get_trending_opportunities(60.0)
        
        initial_data = {
            "type": "initial",
            "timestamp": datetime.now().isoformat(),
            "trending_keywords": [
                {
                    "keyword": trend.keyword,
                    "volume": trend.volume,
                    "growth_rate": trend.growth_rate,
                    "source": trend.source.value
                }
                for trend in current_trends
            ],
            "opportunities": [
                {
                    "keyword": opp.keyword,
                    "opportunity_score": opp.opportunity_score,
                    "growth_rate": opp.growth_rate
                }
                for opp in opportunities[:10]
            ]
        }
        
        await websocket.send(json.dumps(initial_data))
        
        # Keep connection alive
        await websocket.wait_closed()
        
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        trending_system.websocket_connections.discard(websocket)
        logger.info("WebSocket connection closed")


# Export for module usage
__all__ = [
    "RealTimeTrendingSystem",
    "TrendSource",
    "AlertSeverity",
    "RealTimeTrendData",
    "TrendAlert",
    "TrendingOpportunity",
    "handle_websocket_connection"
]