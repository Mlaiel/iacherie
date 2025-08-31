"""Analytics Tracking - User, Content and Revenue Tracking Systems

Advanced tracking systems for comprehensive analytics of user behavior,
content performance, and revenue optimization for multi-format content creators.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, reproduction, or distribution is STRICTLY PROHIBITED.
Legal action will be taken against violators under German and international law.
Contact mlaiel@live.de for licensing inquiries.

Team Specialists:
- Lead IA Developer: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior Engineer: Advanced microservices architecture
- ML Engineer: Deep learning & analytics algorithms
- Database Administrator: High-performance data optimization
- Security Expert: Enterprise-grade protection systems
- Microservices Architect: Scalable distributed systems
- Audio Processing Specialist: Advanced audio AI algorithms
- DevOps Engineer: Production-ready infrastructure
- IA Prompt Engineer: Optimized AI model interactions
"""import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import uuid
import hashlib

from .exceptions import TrackingError, DataValidationError
from .collector import MetricPoint, MetricType, MetricScope

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of trackable events"""
    # User Events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTRATION = "user_registration"
    USER_PROFILE_UPDATE = "user_profile_update"
    USER_SUBSCRIPTION = "user_subscription"
    USER_CANCELLATION = "user_cancellation"
    
    # Content Events
    CONTENT_UPLOAD = "content_upload"
    CONTENT_VIEW = "content_view"
    CONTENT_LIKE = "content_like"
    CONTENT_SHARE = "content_share"
    CONTENT_COMMENT = "content_comment"
    CONTENT_DOWNLOAD = "content_download"
    CONTENT_REPORT = "content_report"
    
    # Revenue Events
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    COMMISSION_EARNED = "commission_earned"
    WITHDRAWAL_REQUEST = "withdrawal_request"
    
    # System Events
    API_REQUEST = "api_request"
    ERROR_OCCURRED = "error_occurred"
    FEATURE_USAGE = "feature_usage"


class SessionState(Enum):
    """User session states"""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    TERMINATED = "terminated"


@dataclass
class TrackingEvent:
    """Tracking event data structure"""
    event_id: str
    event_type: EventType
    user_id: Optional[str]
    session_id: Optional[str]
    timestamp: datetime
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'properties': self.properties,
            'metadata': self.metadata
        }


@dataclass
class UserSession:
    """User session tracking"""
    session_id: str
    user_id: str
    start_time: datetime
    last_activity: datetime
    state: SessionState = SessionState.ACTIVE
    events: List[TrackingEvent] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'state': self.state.value,
            'event_count': len(self.events),
            'duration_seconds': (self.last_activity - self.start_time).total_seconds(),
            'properties': self.properties
        }


class UserTracker:
    """
    Advanced user behavior tracking system.
    
    Tracks user activities, sessions, engagement patterns, and provides
    comprehensive analytics for user behavior optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Tracking storage
        self.active_sessions = {}
        self.user_events = defaultdict(deque)
        self.session_history = defaultdict(list)
        
        # Configuration
        self.session_timeout = self.config.get('session_timeout_minutes', 30)
        self.max_events_per_user = self.config.get('max_events_per_user', 10000)
        self.enable_realtime_tracking = self.config.get('enable_realtime_tracking', True)
        
        # Performance tracking
        self.tracking_stats = {
            'total_events': 0,
            'active_sessions': 0,
            'unique_users': 0,
            'last_activity': None
        }
    
    async def initialize(self) -> None:
        """Initialize user tracker"""
        try:
            self.logger.info("Initializing UserTracker...")
            
            # Start session cleanup task
            if self.enable_realtime_tracking:
                asyncio.create_task(self._session_cleanup_task())
            
            self.logger.info("UserTracker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize UserTracker: {str(e)}")
            raise TrackingError(f"Initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown user tracker"""
        try:
            self.logger.info("Shutting down UserTracker...")
            
            # Save active sessions
            await self._save_active_sessions()
            
            self.logger.info("UserTracker shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down UserTracker: {str(e)}")
            raise TrackingError(f"Shutdown failed: {str(e)}")
    
    async def track_activity(
        self,
        user_id: str,
        activity: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> str:
        """Track user activity"""
        try:
            # Generate event ID
            event_id = self._generate_event_id()
            
            # Determine event type
            event_type = self._determine_event_type(activity)
            
            # Get or create session
            if not session_id:
                session_id = await self._get_or_create_session(user_id)
            
            # Create tracking event
            event = TrackingEvent(
                event_id=event_id,
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now(),
                properties=activity,
                metadata={
                    'source': activity.get('source', 'unknown'),
                    'platform': activity.get('platform', 'web'),
                    'ip_address': activity.get('ip_address'),
                    'user_agent': activity.get('user_agent')
                }
            )
            
            # Store event
            await self._store_event(event)
            
            # Update session
            await self._update_session(session_id, event)
            
            # Update statistics
            self.tracking_stats['total_events'] += 1
            self.tracking_stats['last_activity'] = datetime.now()
            
            self.logger.debug(f"Tracked activity for user {user_id}: {event_type.value}")
            return event_id
            
        except Exception as e:
            self.logger.error(f"Error tracking user activity: {str(e)}")
            raise TrackingError(f"Activity tracking failed: {str(e)}")
    
    async def start_session(
        self,
        user_id: str,
        session_properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new user session"""
        try:
            session_id = self._generate_session_id(user_id)
            
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.now(),
                last_activity=datetime.now(),
                properties=session_properties or {}
            )
            
            self.active_sessions[session_id] = session
            self.tracking_stats['active_sessions'] = len(self.active_sessions)
            
            self.logger.info(f"Started session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error starting session: {str(e)}")
            raise TrackingError(f"Session start failed: {str(e)}")
    
    async def end_session(self, session_id: str) -> None:
        """End a user session"""
        try:
            session = self.active_sessions.get(session_id)
            if session:
                session.state = SessionState.TERMINATED
                session.last_activity = datetime.now()
                
                # Move to history
                self.session_history[session.user_id].append(session)
                del self.active_sessions[session_id]
                
                self.tracking_stats['active_sessions'] = len(self.active_sessions)
                
                self.logger.info(f"Ended session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Error ending session: {str(e)}")
            raise TrackingError(f"Session end failed: {str(e)}")
    
    async def get_user_analytics(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for a specific user"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=period_days)
            
            # Get user events in period
            user_events = [
                event for event in self.user_events[user_id]
                if start_time <= event.timestamp <= end_time
            ]
            
            # Get user sessions in period
            user_sessions = [
                session for session in self.session_history[user_id]
                if start_time <= session.start_time <= end_time
            ]
            
            # Calculate analytics
            analytics = {
                'user_id': user_id,
                'period_days': period_days,
                'event_analytics': await self._calculate_event_analytics(user_events),
                'session_analytics': await self._calculate_session_analytics(user_sessions),
                'engagement_metrics': await self._calculate_engagement_metrics(user_id, period_days),
                'behavior_patterns': await self._analyze_behavior_patterns(user_events),
                'generated_at': datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting user analytics: {str(e)}")
            raise TrackingError(f"User analytics failed: {str(e)}")
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time tracking metrics"""
        try:
            # Calculate active users (last 5 minutes)
            cutoff_time = datetime.now() - timedelta(minutes=5)
            recent_users = set()
            
            for session in self.active_sessions.values():
                if session.last_activity >= cutoff_time:
                    recent_users.add(session.user_id)
            
            # Calculate event rates
            recent_events = 0
            for user_events in self.user_events.values():
                for event in user_events:
                    if event.timestamp >= cutoff_time:
                        recent_events += 1
            
            return {
                'timestamp': datetime.now().isoformat(),
                'active_sessions': len(self.active_sessions),
                'active_users_5min': len(recent_users),
                'events_per_minute': recent_events / 5,
                'total_tracked_events': self.tracking_stats['total_events'],
                'total_unique_users': len(self.user_events),
                'average_session_duration': await self._calculate_average_session_duration()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting realtime metrics: {str(e)}")
            raise TrackingError(f"Realtime metrics failed: {str(e)}")
    
    async def get_user_segmentation(self) -> Dict[str, Any]:
        """Get user segmentation analysis"""
        try:
            segments = {
                'new_users': [],
                'active_users': [],
                'power_users': [],
                'inactive_users': []
            }
            
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for user_id, events in self.user_events.items():
                recent_events = [e for e in events if e.timestamp >= cutoff_time]
                event_count = len(recent_events)
                
                if event_count == 0:
                    segments['inactive_users'].append(user_id)
                elif event_count < 5:
                    segments['new_users'].append(user_id)
                elif event_count < 20:
                    segments['active_users'].append(user_id)
                else:
                    segments['power_users'].append(user_id)
            
            return {
                'segmentation_date': datetime.now().isoformat(),
                'segments': {
                    name: {'count': len(users), 'user_ids': users[:10]}  # Limit for privacy
                    for name, users in segments.items()
                },
                'total_users': len(self.user_events)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user segmentation: {str(e)}")
            raise TrackingError(f"User segmentation failed: {str(e)}")
    
    # Private Methods
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        return f"evt_{uuid.uuid4().hex[:16]}"
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate unique session ID"""
        timestamp = str(int(datetime.now().timestamp()))
        hash_input = f"{user_id}_{timestamp}_{uuid.uuid4().hex[:8]}"
        session_hash = hashlib.md5(hash_input.encode()).hexdigest()[:16]
        return f"ses_{session_hash}"
    
    def _determine_event_type(self, activity: Dict[str, Any]) -> EventType:
        """Determine event type from activity data"""
        action = activity.get('action', '').lower()
        
        # Map actions to event types
        action_mapping = {
            'login': EventType.USER_LOGIN,
            'logout': EventType.USER_LOGOUT,
            'register': EventType.USER_REGISTRATION,
            'upload': EventType.CONTENT_UPLOAD,
            'view': EventType.CONTENT_VIEW,
            'like': EventType.CONTENT_LIKE,
            'share': EventType.CONTENT_SHARE,
            'comment': EventType.CONTENT_COMMENT,
            'download': EventType.CONTENT_DOWNLOAD,
            'payment': EventType.PAYMENT_SUCCESS,
            'api_call': EventType.API_REQUEST
        }
        
        return action_mapping.get(action, EventType.FEATURE_USAGE)
    
    async def _get_or_create_session(self, user_id: str) -> str:
        """Get existing session or create new one"""
        # Find active session for user
        for session_id, session in self.active_sessions.items():
            if (session.user_id == user_id and 
                session.state == SessionState.ACTIVE and
                self._is_session_valid(session)):
                return session_id
        
        # Create new session
        return await self.start_session(user_id)
    
    def _is_session_valid(self, session: UserSession) -> bool:
        """Check if session is still valid"""
        timeout = timedelta(minutes=self.session_timeout)
        return datetime.now() - session.last_activity < timeout
    
    async def _store_event(self, event: TrackingEvent) -> None:
        """Store tracking event"""
        user_events = self.user_events[event.user_id]
        user_events.append(event)
        
        # Maintain size limit
        while len(user_events) > self.max_events_per_user:
            user_events.popleft()
    
    async def _update_session(self, session_id: str, event: TrackingEvent) -> None:
        """Update session with new event"""
        session = self.active_sessions.get(session_id)
        if session:
            session.last_activity = event.timestamp
            session.events.append(event)
    
    async def _calculate_event_analytics(
        self,
        events: List[TrackingEvent]
    ) -> Dict[str, Any]:
        """Calculate event analytics"""
        if not events:
            return {'total_events': 0}
        
        event_types = defaultdict(int)
        for event in events:
            event_types[event.event_type.value] += 1
        
        return {
            'total_events': len(events),
            'event_types': dict(event_types),
            'first_event': events[0].timestamp.isoformat() if events else None,
            'last_event': events[-1].timestamp.isoformat() if events else None,
            'events_per_day': len(events) / max(1, (events[-1].timestamp - events[0].timestamp).days or 1)
        }
    
    async def _calculate_session_analytics(
        self,
        sessions: List[UserSession]
    ) -> Dict[str, Any]:
        """Calculate session analytics"""
        if not sessions:
            return {'total_sessions': 0}
        
        durations = [
            (session.last_activity - session.start_time).total_seconds()
            for session in sessions
        ]
        
        return {
            'total_sessions': len(sessions),
            'average_duration_seconds': sum(durations) / len(durations),
            'total_session_time_seconds': sum(durations),
            'average_events_per_session': sum(len(s.events) for s in sessions) / len(sessions)
        }
    
    async def _calculate_engagement_metrics(
        self,
        user_id: str,
        period_days: int
    ) -> Dict[str, Any]:
        """Calculate user engagement metrics"""
        # Get recent events
        cutoff_time = datetime.now() - timedelta(days=period_days)
        recent_events = [
            event for event in self.user_events[user_id]
            if event.timestamp >= cutoff_time
        ]
        
        # Calculate engagement score
        engagement_weights = {
            EventType.CONTENT_VIEW: 1,
            EventType.CONTENT_LIKE: 2,
            EventType.CONTENT_SHARE: 3,
            EventType.CONTENT_COMMENT: 4,
            EventType.CONTENT_UPLOAD: 5
        }
        
        engagement_score = sum(
            engagement_weights.get(event.event_type, 1)
            for event in recent_events
        )
        
        return {
            'engagement_score': engagement_score,
            'daily_average_engagement': engagement_score / max(1, period_days),
            'activity_days': len(set(event.timestamp.date() for event in recent_events)),
            'engagement_level': self._classify_engagement_level(engagement_score, period_days)
        }
    
    def _classify_engagement_level(self, score: int, period_days: int) -> str:
        """Classify user engagement level"""
        daily_average = score / max(1, period_days)
        
        if daily_average >= 10:
            return 'high'
        elif daily_average >= 5:
            return 'medium'
        elif daily_average >= 1:
            return 'low'
        else:
            return 'inactive'
    
    async def _analyze_behavior_patterns(
        self,
        events: List[TrackingEvent]
    ) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        if not events:
            return {}
        
        # Analyze time patterns
        hour_activity = defaultdict(int)
        day_activity = defaultdict(int)
        
        for event in events:
            hour_activity[event.timestamp.hour] += 1
            day_activity[event.timestamp.weekday()] += 1
        
        # Find peak activity times
        peak_hour = max(hour_activity.items(), key=lambda x: x[1])[0] if hour_activity else None
        peak_day = max(day_activity.items(), key=lambda x: x[1])[0] if day_activity else None
        
        return {
            'peak_activity_hour': peak_hour,
            'peak_activity_day': peak_day,
            'activity_distribution': {
                'hours': dict(hour_activity),
                'days': dict(day_activity)
            },
            'behavior_consistency': self._calculate_behavior_consistency(events)
        }
    
    def _calculate_behavior_consistency(self, events: List[TrackingEvent]) -> float:
        """Calculate behavior consistency score"""
        if len(events) < 2:
            return 0.0
        
        # Calculate time intervals between events
        intervals = []
        for i in range(1, len(events)):
            interval = (events[i].timestamp - events[i-1].timestamp).total_seconds()
            intervals.append(interval)
        
        # Calculate consistency based on variance in intervals
        if not intervals:
            return 0.0
        
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        
        # Convert to consistency score (0-1)
        consistency = max(0, 1 - (variance / (mean_interval ** 2 + 1)))
        return consistency
    
    async def _calculate_average_session_duration(self) -> float:
        """Calculate average session duration"""
        if not self.active_sessions:
            return 0.0
        
        total_duration = 0
        valid_sessions = 0
        
        for session in self.active_sessions.values():
            duration = (session.last_activity - session.start_time).total_seconds()
            if duration > 0:
                total_duration += duration
                valid_sessions += 1
        
        return total_duration / max(1, valid_sessions)
    
    async def _session_cleanup_task(self) -> None:
        """Cleanup expired sessions"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if not self._is_session_valid(session):
                        expired_sessions.append(session_id)
                
                # Move expired sessions to history
                for session_id in expired_sessions:
                    session = self.active_sessions[session_id]
                    session.state = SessionState.EXPIRED
                    self.session_history[session.user_id].append(session)
                    del self.active_sessions[session_id]
                
                if expired_sessions:
                    self.tracking_stats['active_sessions'] = len(self.active_sessions)
                    self.logger.debug(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                # Run cleanup every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in session cleanup: {str(e)}")
                await asyncio.sleep(60)
    
    async def _save_active_sessions(self) -> None:
        """Save active sessions before shutdown"""
        for session in self.active_sessions.values():
            self.session_history[session.user_id].append(session)


class ContentTracker:
    """
    Advanced content performance tracking system.
    
    Tracks content interactions, performance metrics, engagement patterns,
    and provides analytics for content optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Content tracking storage
        self.content_metrics = defaultdict(dict)
        self.content_interactions = defaultdict(list)
        self.content_performance = defaultdict(dict)
        
        # Configuration
        self.tracking_window_days = self.config.get('tracking_window_days', 30)
        self.performance_update_interval = self.config.get('performance_update_interval', 300)
        
        # Performance tracking
        self.tracking_stats = {
            'tracked_content': 0,
            'total_interactions': 0,
            'last_update': None
        }
    
    async def initialize(self) -> None:
        """Initialize content tracker"""
        try:
            self.logger.info("Initializing ContentTracker...")
            
            # Start performance calculation task
            asyncio.create_task(self._performance_calculation_task())
            
            self.logger.info("ContentTracker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ContentTracker: {str(e)}")
            raise TrackingError(f"Initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown content tracker"""
        try:
            self.logger.info("Shutting down ContentTracker...")
            
            # Save content metrics
            await self._save_content_data()
            
            self.logger.info("ContentTracker shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down ContentTracker: {str(e)}")
            raise TrackingError(f"Shutdown failed: {str(e)}")
    
    async def track_performance(
        self,
        content_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """Track content performance metrics"""
        try:
            # Validate content ID
            if not content_id:
                raise ValueError("Content ID is required")
            
            # Store metrics with timestamp
            timestamped_metrics = {
                **metrics,
                'timestamp': datetime.now().isoformat(),
                'content_id': content_id
            }
            
            # Update content metrics
            self.content_metrics[content_id].update(timestamped_metrics)
            
            # Track interaction
            interaction = {
                'type': 'performance_update',
                'metrics': metrics,
                'timestamp': datetime.now()
            }
            self.content_interactions[content_id].append(interaction)
            
            # Update statistics
            self.tracking_stats['total_interactions'] += 1
            if content_id not in self.content_performance:
                self.tracking_stats['tracked_content'] += 1
            
            self.logger.debug(f"Tracked performance for content {content_id}")
            
        except Exception as e:
            self.logger.error(f"Error tracking content performance: {str(e)}")
            raise TrackingError(f"Content performance tracking failed: {str(e)}")
    
    async def track_interaction(
        self,
        content_id: str,
        interaction_type: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track content interaction"""
        try:
            interaction = {
                'type': interaction_type,
                'user_id': user_id,
                'properties': properties or {},
                'timestamp': datetime.now()
            }
            
            self.content_interactions[content_id].append(interaction)
            self.tracking_stats['total_interactions'] += 1
            
            # Update real-time metrics
            await self._update_content_metrics(content_id, interaction_type)
            
            self.logger.debug(f"Tracked interaction {interaction_type} for content {content_id}")
            
        except Exception as e:
            self.logger.error(f"Error tracking content interaction: {str(e)}")
            raise TrackingError(f"Content interaction tracking failed: {str(e)}")
    
    async def get_content_analytics(
        self,
        content_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for specific content"""
        try:
            cutoff_time = datetime.now() - timedelta(days=period_days)
            
            # Get interactions in period
            interactions = [
                interaction for interaction in self.content_interactions[content_id]
                if interaction['timestamp'] >= cutoff_time
            ]
            
            # Calculate analytics
            analytics = {
                'content_id': content_id,
                'period_days': period_days,
                'current_metrics': self.content_metrics.get(content_id, {}),
                'interaction_analytics': await self._calculate_interaction_analytics(interactions),
                'performance_analytics': await self._calculate_performance_analytics(content_id, period_days),
                'engagement_score': await self._calculate_engagement_score(content_id),
                'viral_potential': await self._calculate_viral_potential(content_id),
                'generated_at': datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting content analytics: {str(e)}")
            raise TrackingError(f"Content analytics failed: {str(e)}")
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time content metrics"""
        try:
            # Calculate recent activity (last 5 minutes)
            cutoff_time = datetime.now() - timedelta(minutes=5)
            recent_interactions = 0
            active_content = set()
            
            for content_id, interactions in self.content_interactions.items():
                for interaction in interactions:
                    if interaction['timestamp'] >= cutoff_time:
                        recent_interactions += 1
                        active_content.add(content_id)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_tracked_content': self.tracking_stats['tracked_content'],
                'total_interactions': self.tracking_stats['total_interactions'],
                'recent_interactions_5min': recent_interactions,
                'active_content_5min': len(active_content),
                'interactions_per_minute': recent_interactions / 5,
                'top_performing_content': await self._get_top_performing_content(5)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting realtime metrics: {str(e)}")
            raise TrackingError(f"Realtime metrics failed: {str(e)}")
    
    async def get_content_leaderboard(
        self,
        metric: str = "engagement_score",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get content leaderboard by metric"""
        try:
            content_scores = []
            
            for content_id in self.content_metrics.keys():
                if metric == "engagement_score":
                    score = await self._calculate_engagement_score(content_id)
                elif metric in self.content_metrics[content_id]:
                    score = self.content_metrics[content_id][metric]
                else:
                    score = 0
                
                content_scores.append({
                    'content_id': content_id,
                    'score': score,
                    'metrics': self.content_metrics[content_id]
                })
            
            # Sort by score
            content_scores.sort(key=lambda x: x['score'], reverse=True)
            
            return content_scores[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting content leaderboard: {str(e)}")
            raise TrackingError(f"Content leaderboard failed: {str(e)}")
    
    # Private Methods
    
    async def _update_content_metrics(
        self,
        content_id: str,
        interaction_type: str
    ) -> None:
        """Update content metrics based on interaction"""
        metrics = self.content_metrics[content_id]
        
        # Update interaction counts
        interaction_key = f"{interaction_type}_count"
        metrics[interaction_key] = metrics.get(interaction_key, 0) + 1
        
        # Update total interactions
        metrics['total_interactions'] = metrics.get('total_interactions', 0) + 1
        
        # Update last activity
        metrics['last_activity'] = datetime.now().isoformat()
    
    async def _calculate_interaction_analytics(
        self,
        interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate interaction analytics"""
        if not interactions:
            return {'total_interactions': 0}
        
        interaction_types = defaultdict(int)
        for interaction in interactions:
            interaction_types[interaction['type']] += 1
        
        return {
            'total_interactions': len(interactions),
            'interaction_types': dict(interaction_types),
            'unique_users': len(set(
                i['user_id'] for i in interactions 
                if i.get('user_id')
            )),
            'interactions_per_day': len(interactions) / max(1, 
                (interactions[-1]['timestamp'] - interactions[0]['timestamp']).days or 1
            )
        }
    
    async def _calculate_performance_analytics(
        self,
        content_id: str,
        period_days: int
    ) -> Dict[str, Any]:
        """Calculate performance analytics"""
        metrics = self.content_metrics.get(content_id, {})
        
        return {
            'views': metrics.get('views', 0),
            'likes': metrics.get('likes', 0),
            'shares': metrics.get('shares', 0),
            'comments': metrics.get('comments', 0),
            'downloads': metrics.get('downloads', 0),
            'quality_score': metrics.get('quality_score', 0),
            'performance_trend': await self._calculate_performance_trend(content_id)
        }
    
    async def _calculate_engagement_score(self, content_id: str) -> float:
        """Calculate engagement score for content"""
        metrics = self.content_metrics.get(content_id, {})
        
        # Weighted engagement calculation
        views = metrics.get('views', 0)
        likes = metrics.get('likes', 0)
        shares = metrics.get('shares', 0)
        comments = metrics.get('comments', 0)
        
        if views == 0:
            return 0.0
        
        # Calculate engagement rate
        engagement_rate = (likes + shares * 2 + comments * 3) / max(1, views)
        
        # Normalize to 0-100 scale
        return min(100, engagement_rate * 100)
    
    async def _calculate_viral_potential(self, content_id: str) -> float:
        """Calculate viral potential score"""
        metrics = self.content_metrics.get(content_id, {})
        interactions = self.content_interactions.get(content_id, [])
        
        # Calculate viral indicators
        shares = metrics.get('shares', 0)
        views = metrics.get('views', 0)
        
        if views == 0:
            return 0.0
        
        # Share rate as primary viral indicator
        share_rate = shares / views
        
        # Factor in growth rate
        recent_interactions = len([
            i for i in interactions 
            if (datetime.now() - i['timestamp']).days <= 1
        ])
        
        growth_factor = min(2.0, recent_interactions / max(1, len(interactions)))
        
        viral_score = share_rate * growth_factor * 100
        return min(100, viral_score)
    
    async def _calculate_performance_trend(self, content_id: str) -> str:
        """Calculate performance trend"""
        interactions = self.content_interactions.get(content_id, [])
        
        if len(interactions) < 5:
            return 'insufficient_data'
        
        # Get recent and older interactions
        recent_interactions = interactions[-3:]
        older_interactions = interactions[-6:-3] if len(interactions) >= 6 else []
        
        if not older_interactions:
            return 'new_content'
        
        recent_rate = len(recent_interactions) / 3
        older_rate = len(older_interactions) / 3
        
        if recent_rate > older_rate * 1.2:
            return 'trending_up'
        elif recent_rate < older_rate * 0.8:
            return 'trending_down'
        else:
            return 'stable'
    
    async def _get_top_performing_content(self, limit: int) -> List[Dict[str, Any]]:
        """Get top performing content"""
        content_scores = []
        
        for content_id in self.content_metrics.keys():
            score = await self._calculate_engagement_score(content_id)
            content_scores.append({
                'content_id': content_id,
                'engagement_score': score
            })
        
        content_scores.sort(key=lambda x: x['engagement_score'], reverse=True)
        return content_scores[:limit]
    
    async def _performance_calculation_task(self) -> None:
        """Background task for performance calculations"""
        while True:
            try:
                # Update performance metrics for all content
                for content_id in list(self.content_metrics.keys()):
                    await self._update_performance_calculations(content_id)
                
                self.tracking_stats['last_update'] = datetime.now()
                
                # Run every 5 minutes
                await asyncio.sleep(self.performance_update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in performance calculation task: {str(e)}")
                await asyncio.sleep(60)
    
    async def _update_performance_calculations(self, content_id: str) -> None:
        """Update performance calculations for content"""
        try:
            # Calculate and store derived metrics
            engagement_score = await self._calculate_engagement_score(content_id)
            viral_potential = await self._calculate_viral_potential(content_id)
            
            self.content_performance[content_id].update({
                'engagement_score': engagement_score,
                'viral_potential': viral_potential,
                'last_calculated': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error updating performance calculations: {str(e)}")
    
    async def _save_content_data(self) -> None:
        """Save content data before shutdown"""
        # Placeholder for data persistence
        pass


class RevenueTracker:
    """
    Advanced revenue tracking and analytics system.
    
    Tracks revenue events, calculates revenue metrics, analyzes revenue trends,
    and provides comprehensive financial analytics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Revenue tracking storage
        self.revenue_events = deque(maxlen=self.config.get('max_events', 100000))
        self.revenue_by_source = defaultdict(list)
        self.revenue_by_user = defaultdict(list)
        self.revenue_summary = defaultdict(float)
        
        # Configuration
        self.default_currency = self.config.get('default_currency', 'EUR')
        self.revenue_categories = self.config.get('revenue_categories', [
            'subscription', 'commission', 'advertising', 'premium', 'other'
        ])
        
        # Performance tracking
        self.tracking_stats = {
            'total_revenue_events': 0,
            'total_revenue_amount': 0.0,
            'last_revenue_event': None
        }
    
    async def initialize(self) -> None:
        """Initialize revenue tracker"""
        try:
            self.logger.info("Initializing RevenueTracker...")
            
            # Start revenue calculation task
            asyncio.create_task(self._revenue_calculation_task())
            
            self.logger.info("RevenueTracker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RevenueTracker: {str(e)}")
            raise TrackingError(f"Initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown revenue tracker"""
        try:
            self.logger.info("Shutting down RevenueTracker...")
            
            # Save revenue data
            await self._save_revenue_data()
            
            self.logger.info("RevenueTracker shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down RevenueTracker: {str(e)}")
            raise TrackingError(f"Shutdown failed: {str(e)}")
    
    async def track_event(
        self,
        event_type: str,
        amount: float,
        metadata: Dict[str, Any]
    ) -> str:
        """Track revenue event"""
        try:
            # Validate amount
            if amount < 0:
                raise ValueError("Revenue amount cannot be negative")
            
            # Generate event ID
            event_id = f"rev_{uuid.uuid4().hex[:16]}"
            
            # Create revenue event
            revenue_event = {
                'event_id': event_id,
                'event_type': event_type,
                'amount': amount,
                'currency': metadata.get('currency', self.default_currency),
                'source': metadata.get('source', 'unknown'),
                'user_id': metadata.get('user_id'),
                'content_id': metadata.get('content_id'),
                'timestamp': datetime.now(),
                'metadata': metadata
            }
            
            # Store event
            self.revenue_events.append(revenue_event)
            
            # Update categorized storage
            source = revenue_event['source']
            self.revenue_by_source[source].append(revenue_event)
            
            if revenue_event['user_id']:
                self.revenue_by_user[revenue_event['user_id']].append(revenue_event)
            
            # Update summary
            self.revenue_summary[source] += amount
            self.revenue_summary['total'] += amount
            
            # Update statistics
            self.tracking_stats['total_revenue_events'] += 1
            self.tracking_stats['total_revenue_amount'] += amount
            self.tracking_stats['last_revenue_event'] = datetime.now()
            
            self.logger.debug(f"Tracked revenue event: {event_type} - {amount} {revenue_event['currency']}")
            return event_id
            
        except Exception as e:
            self.logger.error(f"Error tracking revenue event: {str(e)}")
            raise TrackingError(f"Revenue event tracking failed: {str(e)}")
    
    async def get_revenue_analytics(
        self,
        period_days: int = 30,
        currency: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive revenue analytics"""
        try:
            cutoff_time = datetime.now() - timedelta(days=period_days)
            currency = currency or self.default_currency
            
            # Filter events by period and currency
            period_events = [
                event for event in self.revenue_events
                if (event['timestamp'] >= cutoff_time and 
                    event['currency'] == currency)
            ]
            
            # Calculate analytics
            analytics = {
                'period_days': period_days,
                'currency': currency,
                'revenue_summary': await self._calculate_revenue_summary(period_events),
                'revenue_by_source': await self._calculate_revenue_by_source(period_events),
                'revenue_trends': await self._calculate_revenue_trends(period_events),
                'top_revenue_users': await self._get_top_revenue_users(period_events, 10),
                'revenue_forecasts': await self._generate_revenue_forecasts(period_events),
                'generated_at': datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting revenue analytics: {str(e)}")
            raise TrackingError(f"Revenue analytics failed: {str(e)}")
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time revenue metrics"""
        try:
            # Calculate recent revenue (last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            recent_events = [
                event for event in self.revenue_events
                if event['timestamp'] >= cutoff_time
            ]
            
            recent_revenue = sum(event['amount'] for event in recent_events)
            
            # Calculate today's revenue
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_events = [
                event for event in self.revenue_events
                if event['timestamp'] >= today_start
            ]
            
            today_revenue = sum(event['amount'] for event in today_events)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_revenue_events': self.tracking_stats['total_revenue_events'],
                'total_revenue_amount': self.tracking_stats['total_revenue_amount'],
                'recent_revenue_1h': recent_revenue,
                'recent_events_1h': len(recent_events),
                'today_revenue': today_revenue,
                'today_events': len(today_events),
                'revenue_per_hour': recent_revenue,
                'average_event_value': (
                    self.tracking_stats['total_revenue_amount'] / 
                    max(1, self.tracking_stats['total_revenue_events'])
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error getting realtime revenue metrics: {str(e)}")
            raise TrackingError(f"Realtime revenue metrics failed: {str(e)}")
    
    # Private Methods
    
    async def _calculate_revenue_summary(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate revenue summary"""
        if not events:
            return {'total_revenue': 0, 'total_events': 0}
        
        total_revenue = sum(event['amount'] for event in events)
        event_types = defaultdict(float)
        
        for event in events:
            event_types[event['event_type']] += event['amount']
        
        return {
            'total_revenue': total_revenue,
            'total_events': len(events),
            'average_event_value': total_revenue / len(events),
            'revenue_by_event_type': dict(event_types),
            'period_start': events[0]['timestamp'].isoformat() if events else None,
            'period_end': events[-1]['timestamp'].isoformat() if events else None
        }
    
    async def _calculate_revenue_by_source(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate revenue breakdown by source"""
        source_revenue = defaultdict(float)
        source_events = defaultdict(int)
        
        for event in events:
            source = event['source']
            source_revenue[source] += event['amount']
            source_events[source] += 1
        
        return {
            'revenue_by_source': dict(source_revenue),
            'events_by_source': dict(source_events),
            'top_revenue_source': max(source_revenue.items(), key=lambda x: x[1])[0] if source_revenue else None
        }
    
    async def _calculate_revenue_trends(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate revenue trends"""
        if len(events) < 2:
            return {'trend': 'insufficient_data'}
        
        # Group by day
        daily_revenue = defaultdict(float)
        for event in events:
            day = event['timestamp'].date()
            daily_revenue[day] += event['amount']
        
        # Calculate trend
        sorted_days = sorted(daily_revenue.keys())
        if len(sorted_days) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_avg = sum(daily_revenue[day] for day in sorted_days[-3:]) / min(3, len(sorted_days))
        older_avg = sum(daily_revenue[day] for day in sorted_days[:-3]) / max(1, len(sorted_days) - 3)
        
        if recent_avg > older_avg * 1.1:
            trend = 'increasing'
        elif recent_avg < older_avg * 0.9:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'recent_average': recent_avg,
            'older_average': older_avg,
            'daily_revenue': {day.isoformat(): amount for day, amount in daily_revenue.items()}
        }
    
    async def _get_top_revenue_users(
        self,
        events: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get top revenue generating users"""
        user_revenue = defaultdict(float)
        user_events = defaultdict(int)
        
        for event in events:
            if event['user_id']:
                user_revenue[event['user_id']] += event['amount']
                user_events[event['user_id']] += 1
        
        # Sort by revenue
        top_users = sorted(
            user_revenue.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {
                'user_id': user_id,
                'total_revenue': revenue,
                'event_count': user_events[user_id],
                'average_per_event': revenue / user_events[user_id]
            }
            for user_id, revenue in top_users
        ]
    
    async def _generate_revenue_forecasts(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate revenue forecasts"""
        if len(events) < 7:
            return {'forecast': 'insufficient_data'}
        
        # Simple trend-based forecast
        daily_revenue = defaultdict(float)
        for event in events:
            day = event['timestamp'].date()
            daily_revenue[day] += event['amount']
        
        sorted_days = sorted(daily_revenue.keys())
        recent_days = sorted_days[-7:]  # Last 7 days
        
        if len(recent_days) < 7:
            return {'forecast': 'insufficient_data'}
        
        # Calculate average daily revenue
        avg_daily_revenue = sum(daily_revenue[day] for day in recent_days) / len(recent_days)
        
        # Simple forecast: project current average
        forecasts = []
        for i in range(1, 8):  # Next 7 days
            forecast_date = sorted_days[-1] + timedelta(days=i)
            forecasts.append({
                'date': forecast_date.isoformat(),
                'forecasted_revenue': avg_daily_revenue,
                'confidence': 0.7  # Simple confidence score
            })
        
        return {
            'forecast': 'generated',
            'method': 'moving_average',
            'forecasts': forecasts,
            'total_forecasted_revenue': avg_daily_revenue * 7
        }
    
    async def _revenue_calculation_task(self) -> None:
        """Background task for revenue calculations"""
        while True:
            try:
                # Update revenue summaries
                await self._update_revenue_summaries()
                
                # Run every 10 minutes
                await asyncio.sleep(600)
                
            except Exception as e:
                self.logger.error(f"Error in revenue calculation task: {str(e)}")
                await asyncio.sleep(60)
    
    async def _update_revenue_summaries(self) -> None:
        """Update revenue summaries"""
        try:
            # Recalculate summaries from recent events
            cutoff_time = datetime.now() - timedelta(hours=1)
            recent_events = [
                event for event in self.revenue_events
                if event['timestamp'] >= cutoff_time
            ]
            
            if recent_events:
                self.logger.debug(f"Updated revenue summaries with {len(recent_events)} recent events")
            
        except Exception as e:
            self.logger.error(f"Error updating revenue summaries: {str(e)}")
    
    async def _save_revenue_data(self) -> None:
        """Save revenue data before shutdown"""
        # Placeholder for data persistence
        pass
