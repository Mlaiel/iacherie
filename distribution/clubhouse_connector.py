"""
Clubhouse Audio Platform Connector for Ainflue Distribution
Provides enterprise-grade integration with Clubhouse audio social platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import numpy as np
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)


class ClubhouseRoomStatus(str, Enum):
    """Clubhouse room status enumeration"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"
    CANCELLED = "cancelled"


class ClubhousePrivacyLevel(str, Enum):
    """Clubhouse room privacy levels"""
    OPEN = "open"
    SOCIAL = "social"
    CLOSED = "closed"


@dataclass
class ClubhouseCredentials:
    """Clubhouse API credentials"""
    api_key: str
    api_secret: str
    user_id: str
    device_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ClubhouseRoom(BaseModel):
    """Clubhouse room model"""
    room_id: str = Field(..., description="Unique room identifier")
    title: str = Field(..., description="Room title")
    description: Optional[str] = Field(None, description="Room description")
    topic: str = Field(..., description="Room topic/category")
    language: str = Field(default="en", description="Room language")
    privacy_level: ClubhousePrivacyLevel = Field(default=ClubhousePrivacyLevel.OPEN)
    start_time: datetime = Field(..., description="Scheduled start time")
    estimated_duration: int = Field(default=60, description="Duration in minutes")
    max_participants: int = Field(default=8000, description="Maximum participants")
    status: ClubhouseRoomStatus = Field(default=ClubhouseRoomStatus.SCHEDULED)
    
    @validator('start_time')
    def validate_start_time(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class ClubhouseMetrics(BaseModel):
    """Clubhouse room performance metrics"""
    room_id: str
    peak_listeners: int = 0
    total_listeners: int = 0
    speakers_count: int = 0
    duration_minutes: int = 0
    engagement_score: float = 0.0
    shares_count: int = 0
    follows_gained: int = 0
    recording_views: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClubhouseConnector:
    """
    Advanced Clubhouse connector for audio content distribution
    Features: Room scheduling, live streaming, analytics, community building
    """
    
    def __init__(self, credentials: ClubhouseCredentials):
        self.credentials = credentials
        self.base_url = "https://api.clubhouseapi.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits = {
            'requests_per_minute': 60,
            'rooms_per_day': 10,
            'follows_per_hour': 100
        }
        self.current_requests = 0
        self.last_reset = datetime.now(timezone.utc)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def initialize(self) -> bool:
        """Initialize Clubhouse connector"""
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.credentials.access_token}',
                    'User-Agent': 'Ainflue-Distribution/3.0',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Verify authentication
            if await self._verify_auth():
                logger.info("Clubhouse connector initialized successfully")
                return True
            else:
                logger.error("Clubhouse authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Clubhouse connector: {e}")
            return False
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def _verify_auth(self) -> bool:
        """Verify authentication credentials"""
        try:
            async with self.session.get(f"{self.base_url}/me") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Auth verification failed: {e}")
            return False
            
    async def _check_rate_limits(self) -> bool:
        """Check and enforce rate limits"""
        now = datetime.now(timezone.utc)
        if (now - self.last_reset).total_seconds() >= 60:
            self.current_requests = 0
            self.last_reset = now
            
        if self.current_requests >= self.rate_limits['requests_per_minute']:
            logger.warning("Rate limit exceeded, waiting...")
            await asyncio.sleep(60)
            self.current_requests = 0
            
        self.current_requests += 1
        return True
        
    async def schedule_room(self, room_data: ClubhouseRoom) -> Dict[str, Any]:
        """
        Schedule a Clubhouse room
        
        Args:
            room_data: Room configuration
            
        Returns:
            Room creation response with room_id
        """
        await self._check_rate_limits()
        
        try:
            payload = {
                'title': room_data.title,
                'description': room_data.description,
                'topic': room_data.topic,
                'language': room_data.language,
                'privacy_level': room_data.privacy_level.value,
                'start_time': room_data.start_time.isoformat(),
                'estimated_duration': room_data.estimated_duration,
                'max_participants': room_data.max_participants
            }
            
            async with self.session.post(
                f"{self.base_url}/rooms",
                json=payload
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Room scheduled successfully: {result.get('room_id')}")
                    return {
                        'success': True,
                        'room_id': result.get('room_id'),
                        'room_url': result.get('room_url'),
                        'scheduled_time': room_data.start_time.isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to schedule room: {error_text}")
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            logger.error(f"Room scheduling error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def start_room(self, room_id: str) -> Dict[str, Any]:
        """
        Start a scheduled Clubhouse room
        
        Args:
            room_id: Room identifier
            
        Returns:
            Room start response
        """
        await self._check_rate_limits()
        
        try:
            async with self.session.post(
                f"{self.base_url}/rooms/{room_id}/start"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Room started successfully: {room_id}")
                    return {
                        'success': True,
                        'room_id': room_id,
                        'live_url': result.get('live_url'),
                        'started_at': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to start room: {error_text}")
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            logger.error(f"Room start error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def end_room(self, room_id: str) -> Dict[str, Any]:
        """
        End a live Clubhouse room
        
        Args:
            room_id: Room identifier
            
        Returns:
            Room end response with analytics
        """
        await self._check_rate_limits()
        
        try:
            async with self.session.post(
                f"{self.base_url}/rooms/{room_id}/end"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Room ended successfully: {room_id}")
                    return {
                        'success': True,
                        'room_id': room_id,
                        'ended_at': datetime.now(timezone.utc).isoformat(),
                        'final_metrics': result.get('metrics', {})
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to end room: {error_text}")
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            logger.error(f"Room end error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def get_room_metrics(self, room_id: str) -> ClubhouseMetrics:
        """
        Get comprehensive room analytics
        
        Args:
            room_id: Room identifier
            
        Returns:
            Room metrics and analytics
        """
        await self._check_rate_limits()
        
        try:
            async with self.session.get(
                f"{self.base_url}/rooms/{room_id}/analytics"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Calculate engagement score
                    engagement_score = self._calculate_engagement_score(data)
                    
                    return ClubhouseMetrics(
                        room_id=room_id,
                        peak_listeners=data.get('peak_listeners', 0),
                        total_listeners=data.get('total_listeners', 0),
                        speakers_count=data.get('speakers_count', 0),
                        duration_minutes=data.get('duration_minutes', 0),
                        engagement_score=engagement_score,
                        shares_count=data.get('shares_count', 0),
                        follows_gained=data.get('follows_gained', 0),
                        recording_views=data.get('recording_views', 0)
                    )
                else:
                    logger.error(f"Failed to get metrics for room {room_id}")
                    return ClubhouseMetrics(room_id=room_id)
                    
        except Exception as e:
            logger.error(f"Metrics retrieval error: {e}")
            return ClubhouseMetrics(room_id=room_id)
            
    def _calculate_engagement_score(self, metrics_data: Dict[str, Any]) -> float:
        """Calculate engagement score using multiple factors"""
        try:
            peak_listeners = metrics_data.get('peak_listeners', 0)
            total_listeners = metrics_data.get('total_listeners', 0)
            duration = metrics_data.get('duration_minutes', 0)
            shares = metrics_data.get('shares_count', 0)
            follows = metrics_data.get('follows_gained', 0)
            
            if peak_listeners == 0 or duration == 0:
                return 0.0
                
            # Engagement factors
            retention_rate = min(total_listeners / peak_listeners if peak_listeners > 0 else 0, 1.0)
            share_rate = shares / peak_listeners if peak_listeners > 0 else 0
            follow_rate = follows / peak_listeners if peak_listeners > 0 else 0
            duration_factor = min(duration / 60, 1.0)  # Normalize to 1 hour
            
            # Weighted engagement score
            engagement_score = (
                retention_rate * 0.4 +
                share_rate * 0.3 +
                follow_rate * 0.2 +
                duration_factor * 0.1
            )
            
            return round(engagement_score * 100, 2)  # Convert to percentage
            
        except Exception as e:
            logger.error(f"Engagement calculation error: {e}")
            return 0.0
            
    async def invite_speakers(self, room_id: str, user_ids: List[str]) -> Dict[str, Any]:
        """
        Invite users as speakers to a room
        
        Args:
            room_id: Room identifier
            user_ids: List of user IDs to invite
            
        Returns:
            Invitation results
        """
        await self._check_rate_limits()
        
        try:
            payload = {'user_ids': user_ids}
            
            async with self.session.post(
                f"{self.base_url}/rooms/{room_id}/invite-speakers",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Speakers invited to room {room_id}: {len(user_ids)}")
                    return {
                        'success': True,
                        'invited_count': len(user_ids),
                        'invitations': result.get('invitations', [])
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to invite speakers: {error_text}")
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            logger.error(f"Speaker invitation error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """
        Get trending topics on Clubhouse
        
        Returns:
            List of trending topics with metrics
        """
        await self._check_rate_limits()
        
        try:
            async with self.session.get(
                f"{self.base_url}/topics/trending"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('topics', [])
                else:
                    logger.error("Failed to get trending topics")
                    return []
                    
        except Exception as e:
            logger.error(f"Trending topics error: {e}")
            return []
            
    async def search_rooms(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for rooms on Clubhouse
        
        Args:
            query: Search query
            filters: Optional search filters
            
        Returns:
            List of matching rooms
        """
        await self._check_rate_limits()
        
        try:
            params = {'q': query}
            if filters:
                params.update(filters)
                
            async with self.session.get(
                f"{self.base_url}/search/rooms",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('rooms', [])
                else:
                    logger.error(f"Room search failed: {query}")
                    return []
                    
        except Exception as e:
            logger.error(f"Room search error: {e}")
            return []


class ClubhouseDistributionManager:
    """
    High-level manager for Clubhouse distribution strategies
    Handles content planning, audience targeting, and performance optimization
    """
    
    def __init__(self, connector: ClubhouseConnector):
        self.connector = connector
        self.performance_history: List[ClubhouseMetrics] = []
        
    async def plan_content_series(self, 
                                 topic: str, 
                                 target_audience: Dict[str, Any],
                                 frequency: str = "weekly") -> List[ClubhouseRoom]:
        """
        Plan a content series based on topic and audience
        
        Args:
            topic: Main topic/theme
            target_audience: Audience targeting parameters
            frequency: Content frequency (daily, weekly, bi-weekly)
            
        Returns:
            List of planned rooms
        """
        try:
            # Get trending topics related to the main topic
            trending = await self.connector.get_trending_topics()
            related_topics = [t for t in trending if topic.lower() in t.get('name', '').lower()]
            
            # Generate content calendar
            rooms = []
            base_time = datetime.now(timezone.utc)
            
            frequency_days = {'daily': 1, 'weekly': 7, 'bi-weekly': 14}.get(frequency, 7)
            
            for i in range(4):  # Plan 4 sessions
                room_time = base_time + timedelta(days=i * frequency_days)
                
                # Use trending topic if available
                room_topic = related_topics[i % len(related_topics)]['name'] if related_topics else topic
                
                room = ClubhouseRoom(
                    room_id=f"planned_{i+1}",
                    title=f"{room_topic} - Session {i+1}",
                    description=f"Deep dive into {room_topic} with industry experts",
                    topic=room_topic,
                    language=target_audience.get('language', 'en'),
                    start_time=room_time,
                    estimated_duration=target_audience.get('preferred_duration', 60)
                )
                
                rooms.append(room)
                
            logger.info(f"Planned {len(rooms)} rooms for topic: {topic}")
            return rooms
            
        except Exception as e:
            logger.error(f"Content planning error: {e}")
            return []
            
    async def optimize_room_timing(self, base_time: datetime, target_audience: Dict[str, Any]) -> datetime:
        """
        Optimize room timing based on audience data and historical performance
        
        Args:
            base_time: Preferred base time
            target_audience: Audience preferences and demographics
            
        Returns:
            Optimized timing
        """
        try:
            # Analyze historical performance
            if self.performance_history:
                best_hours = [m.timestamp.hour for m in self.performance_history 
                             if m.engagement_score > 70]
                
                if best_hours:
                    optimal_hour = max(set(best_hours), key=best_hours.count)
                    optimized_time = base_time.replace(hour=optimal_hour, minute=0, second=0)
                    logger.info(f"Optimized timing to {optimal_hour}:00 based on history")
                    return optimized_time
                    
            # Use audience timezone preferences
            audience_tz = target_audience.get('timezone', 'UTC')
            preferred_hour = target_audience.get('preferred_hour', 19)  # 7 PM default
            
            optimized_time = base_time.replace(hour=preferred_hour, minute=0, second=0)
            logger.info(f"Set timing to {preferred_hour}:00 for timezone {audience_tz}")
            return optimized_time
            
        except Exception as e:
            logger.error(f"Timing optimization error: {e}")
            return base_time
            
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """
        Analyze performance trends from historical data
        
        Returns:
            Performance insights and recommendations
        """
        if not self.performance_history:
            return {'message': 'No performance data available'}
            
        try:
            metrics = self.performance_history
            
            # Calculate averages
            avg_engagement = np.mean([m.engagement_score for m in metrics])
            avg_peak_listeners = np.mean([m.peak_listeners for m in metrics])
            avg_duration = np.mean([m.duration_minutes for m in metrics])
            
            # Find best performing times
            hour_performance = {}
            for metric in metrics:
                hour = metric.timestamp.hour
                if hour not in hour_performance:
                    hour_performance[hour] = []
                hour_performance[hour].append(metric.engagement_score)
                
            best_hour = max(hour_performance.items(), 
                           key=lambda x: np.mean(x[1]))[0] if hour_performance else None
            
            # Performance trend
            recent_metrics = metrics[-5:] if len(metrics) >= 5 else metrics
            trend = "improving" if len(recent_metrics) > 1 and \
                   recent_metrics[-1].engagement_score > recent_metrics[0].engagement_score else "stable"
                   
            return {
                'total_rooms': len(metrics),
                'average_engagement': round(avg_engagement, 2),
                'average_peak_listeners': int(avg_peak_listeners),
                'average_duration_minutes': int(avg_duration),
                'best_hour': best_hour,
                'performance_trend': trend,
                'recommendations': self._generate_recommendations(avg_engagement, avg_peak_listeners)
            }
            
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            return {'error': str(e)}
            
    def _generate_recommendations(self, avg_engagement: float, avg_peak_listeners: float) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if avg_engagement < 50:
            recommendations.append("Consider more interactive content and speaker diversity")
            recommendations.append("Improve room descriptions and titles for better discovery")
            
        if avg_peak_listeners < 100:
            recommendations.append("Increase promotion before rooms start")
            recommendations.append("Collaborate with other creators for cross-promotion")
            
        if avg_engagement > 80:
            recommendations.append("Great engagement! Consider increasing room frequency")
            
        return recommendations


# Export main classes
__all__ = [
    'ClubhouseConnector',
    'ClubhouseDistributionManager', 
    'ClubhouseRoom',
    'ClubhouseMetrics',
    'ClubhouseCredentials',
    'ClubhouseRoomStatus',
    'ClubhousePrivacyLevel'
]