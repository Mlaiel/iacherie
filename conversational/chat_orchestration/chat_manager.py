"""
Chat Manager - Enterprise conversational AI orchestration engine
================================================================

Manages complex multi-turn conversations across different creator types (musicians, 
bloggers, photographers, influencers, comedians) with integrated content protection 
and monetization capabilities. Provides advanced session management, context tracking,
and AI-powered response generation with creator-specific optimizations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are proprietary intellectual property of Fahed Mlaiel.
Unauthorized copying, modification, distribution, or use without explicit written
permission is strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

from backend.core.database import DatabaseManager
from backend.core.cache import CacheManager
from backend.core.config import settings
from backend.security.auth import SecurityManager
from backend.ai.models import ConversationalAI
from backend.content_protection.fingerprinting import ContentProtectionService
from backend.business.monetization import MonetizationEngine
from backend.monitoring.analytics import AnalyticsTracker
from backend.integrations.platform_apis import PlatformAPIManager

from .conversation_router import ConversationRouter
from .message_processor import MessageProcessor
from .session_controller import SessionController
from .response_generator import ResponseGenerator
from .context_analyzer import ContextAnalyzer
from .intent_classifier import IntentClassifier
from .chat_analytics import ChatAnalytics


class ChatStatus(Enum):
    """Chat session status enumeration with extended states"""
    ACTIVE = "active"
    PAUSED = "paused" 
    ENDED = "ended"
    ERROR = "error"
    WAITING_USER = "waiting_user"
    PROCESSING = "processing"
    PROTECTION_ALERT = "protection_alert"
    MONETIZATION_OPPORTUNITY = "monetization_opportunity"
    COLLABORATION_MATCHING = "collaboration_matching"
    CONTENT_ANALYSIS = "content_analysis"


class CreatorType(Enum):
    """Supported creator types with specialized handling"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    MULTI_FORMAT = "multi_format"
    AGENCY = "agency"
    BRAND = "brand"


class ConversationPriority(Enum):
    """Conversation priority levels for resource allocation"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class MessageSentiment(Enum):
    """Message sentiment classification"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONCERNED = "concerned"


@dataclass
class CreatorProfile:
    """Extended creator profile with specialized attributes"""
    creator_type: CreatorType
    specializations: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    content_categories: List[str] = field(default_factory=list)
    protection_level: str = "standard"
    monetization_preferences: Dict[str, Any] = field(default_factory=dict)
    collaboration_interests: List[str] = field(default_factory=list)
    language_preferences: List[str] = field(default_factory=lambda: ["en"])
    timezone: str = "UTC"
    subscription_tier: str = "basic"


@dataclass
class ConversationMetrics:
    """Real-time conversation performance metrics"""
    message_count: int = 0
    avg_response_time: float = 0.0
    sentiment_scores: Dict[str, float] = field(default_factory=dict)
    intent_distribution: Dict[str, int] = field(default_factory=dict)
    protection_alerts: int = 0
    monetization_opportunities: int = 0
    user_satisfaction: float = 0.0
    engagement_score: float = 0.0


@dataclass
class ChatSession:
    """Enhanced chat session data structure with comprehensive tracking"""
    session_id: str
    user_id: str
    creator_profile: CreatorProfile
    status: ChatStatus
    priority: ConversationPriority
    context: Dict[str, Any]
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    metrics: ConversationMetrics
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    expires_at: Optional[datetime] = None
    security_flags: List[str] = field(default_factory=list)
    active_workflows: List[str] = field(default_factory=list)
    content_fingerprints: List[str] = field(default_factory=list)


class ChatManager:
    """
    Enterprise-grade chat orchestration manager handling multi-format creator conversations
    with integrated AI protection, monetization, and advanced analytics capabilities.
    
    Features:
    - Multi-tenant session management with creator specialization
    - Real-time content protection monitoring
    - Automated monetization opportunity detection  
    - Advanced context tracking and memory management
    - Creator-specific AI response optimization
    - Cross-platform collaboration matching
    - Comprehensive analytics and performance monitoring
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        cache_manager: CacheManager,
        security_manager: SecurityManager,
        ai_engine: ConversationalAI,
        protection_service: ContentProtectionService,
        monetization_engine: MonetizationEngine,
        analytics_tracker: AnalyticsTracker,
        platform_api_manager: PlatformAPIManager
    ):
        self.db = db_manager
        self.cache = cache_manager
        self.security = security_manager
        self.ai_engine = ai_engine
        self.protection = protection_service
        self.monetization = monetization_engine
        self.analytics_tracker = analytics_tracker
        self.platform_apis = platform_api_manager
        
        # Initialize orchestration components
        self.router = ConversationRouter(self.ai_engine, self.cache, self.protection)
        self.processor = MessageProcessor(self.protection, self.security, self.analytics_tracker)
        self.session_controller = SessionController(self.db, self.cache, self.security)
        self.response_generator = ResponseGenerator(
            self.ai_engine, 
            self.monetization, 
            self.platform_apis
        )
        self.context_analyzer = ContextAnalyzer(self.ai_engine, self.protection)
        self.intent_classifier = IntentClassifier(self.ai_engine, self.analytics_tracker)
        self.analytics = ChatAnalytics(self.db, self.analytics_tracker)
        
        # Session management
        self.active_sessions: Dict[str, ChatSession] = {}
        self.session_locks: Dict[str, asyncio.Lock] = {}
        
        # Performance monitoring
        self.performance_metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "avg_session_duration": 0.0,
            "message_throughput": 0.0,
            "error_rate": 0.0
        }
        
        # Configuration
        self.max_concurrent_sessions = settings.get("chat.max_concurrent_sessions", 1000)
        self.session_timeout = settings.get("chat.session_timeout_hours", 24)
        self.message_rate_limit = settings.get("chat.message_rate_limit", 100)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize background tasks
        self._setup_background_tasks()
    
    def _setup_background_tasks(self) -> None:
        """Setup background tasks for session cleanup and monitoring"""
        asyncio.create_task(self._session_cleanup_task())
        asyncio.create_task(self._performance_monitoring_task())
        asyncio.create_task(self._protection_monitoring_task())
    
    async def _session_cleanup_task(self) -> None:
        """Background task to cleanup expired sessions"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if (session.expires_at and current_time > session.expires_at) or \
                       (current_time - session.last_activity).total_seconds() > 3600:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self.end_session(session_id, "expired")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Session cleanup error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _performance_monitoring_task(self) -> None:
        """Background task to monitor and update performance metrics"""
        while True:
            try:
                self.performance_metrics["active_sessions"] = len(self.active_sessions)
                
                # Calculate average session duration
                if self.active_sessions:
                    total_duration = sum(
                        (datetime.utcnow() - session.created_at).total_seconds()
                        for session in self.active_sessions.values()
                    )
                    self.performance_metrics["avg_session_duration"] = total_duration / len(self.active_sessions)
                
                # Track metrics in analytics
                await self.analytics_tracker.track_metrics(
                    "chat_manager_performance",
                    self.performance_metrics
                )
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _protection_monitoring_task(self) -> None:
        """Background task to monitor content protection across all sessions"""
        while True:
            try:
                for session in self.active_sessions.values():
                    if session.status == ChatStatus.ACTIVE:
                        # Check for protection alerts
                        protection_status = await self.protection.check_session_protection(
                            session.session_id
                        )
                        
                        if protection_status.get("alert_level") == "high":
                            session.status = ChatStatus.PROTECTION_ALERT
                            session.security_flags.append("high_risk_content_detected")
                            
                            # Notify session about protection concern
                            await self._send_protection_alert(session)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Protection monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def create_session(
        self,
        user_id: str,
        creator_profile: CreatorProfile,
        initial_context: Optional[Dict[str, Any]] = None,
        priority: ConversationPriority = ConversationPriority.NORMAL,
        expires_in_hours: Optional[int] = None
    ) -> ChatSession:
        
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, ChatSession] = {}
        
    async def create_session(
        self,
        user_id: str,
        creator_type: CreatorType,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """
        Create new chat session with creator-specific configuration
        
        Args:
            user_id: Authenticated user identifier
            creator_type: Type of content creator
            initial_context: Optional session context
            
        Returns:
            ChatSession: New chat session instance
        """
        try:
            # Validate user and get profile
            user_profile = await self.security.get_user_profile(user_id)
            if not user_profile:
                raise ValueError(f"Invalid user_id: {user_id}")
            
            # Generate unique session ID
            session_id = await self._generate_session_id(user_id)
            
            # Initialize session context based on creator type
            context = await self._initialize_creator_context(
                creator_type, 
                user_profile, 
                initial_context or {}
            )
            
            # Create session object
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                creator_type=creator_type,
                status=ChatStatus.ACTIVE,
                context=context,
                messages=[],
                metadata={
                    "user_profile": user_profile,
                    "creation_method": "api",
                    "ip_address": context.get("ip_address"),
                    "user_agent": context.get("user_agent")
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            # Store session in database and cache
            await self.session_controller.save_session(session)
            
            # Track session creation analytics
            await self.analytics.track_session_created(session)
            
            # Add to active sessions
            self.active_sessions[session_id] = session
            
            self.logger.info(f"Created chat session {session_id} for user {user_id}")
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create chat session: {str(e)}")
            raise
    
    async def process_message(
        self,
        session_id: str,
        message_content: str,
        message_type: str = "text",
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process incoming message and generate AI response
        
        Args:
            session_id: Active session identifier
            message_content: User message content
            message_type: Type of message (text, audio, image, etc.)
            attachments: Optional file attachments
            
        Returns:
            Dict containing AI response and session updates
        """
        try:
            # Get active session
            session = await self._get_active_session(session_id)
            if not session:
                raise ValueError(f"Invalid or expired session: {session_id}")
            
            # Update session status
            session.status = ChatStatus.PROCESSING
            session.updated_at = datetime.utcnow()
            
            # Process and validate message
            processed_message = await self.processor.process_message(
                message_content=message_content,
                message_type=message_type,
                attachments=attachments,
                user_id=session.user_id,
                session_context=session.context
            )
            
            # Analyze context and intent
            context_analysis = await self.context_analyzer.analyze_context(
                session.messages,
                processed_message,
                session.creator_type
            )
            
            intent_classification = await self.intent_classifier.classify_intent(
                processed_message,
                context_analysis,
                session.creator_type
            )
            
            # Route conversation based on intent and creator type
            routing_decision = await self.router.route_conversation(
                intent_classification,
                context_analysis,
                session
            )
            
            # Generate AI response
            ai_response = await self.response_generator.generate_response(
                routing_decision,
                session,
                processed_message,
                context_analysis
            )
            
            # Update session with new message and response
            session.messages.append({
                "id": len(session.messages) + 1,
                "type": "user",
                "content": message_content,
                "processed_content": processed_message,
                "timestamp": datetime.utcnow().isoformat(),
                "attachments": attachments,
                "intent": intent_classification,
                "context_analysis": context_analysis
            })
            
            session.messages.append({
                "id": len(session.messages) + 1,
                "type": "assistant",
                "content": ai_response["content"],
                "timestamp": datetime.utcnow().isoformat(),
                "routing_decision": routing_decision,
                "confidence": ai_response.get("confidence", 0.95),
                "suggestions": ai_response.get("suggestions", [])
            })
            
            # Update session context
            session.context.update(context_analysis.get("updated_context", {}))
            session.status = ChatStatus.WAITING_USER
            session.updated_at = datetime.utcnow()
            
            # Save updated session
            await self.session_controller.update_session(session)
            
            # Track message analytics
            await self.analytics.track_message_processed(
                session_id,
                intent_classification,
                ai_response.get("confidence", 0.95)
            )
            
            return {
                "session_id": session_id,
                "response": ai_response["content"],
                "confidence": ai_response.get("confidence", 0.95),
                "suggestions": ai_response.get("suggestions", []),
                "context_updates": context_analysis.get("updated_context", {}),
                "routing_info": routing_decision,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process message in session {session_id}: {str(e)}")
            # Update session status to error
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = ChatStatus.ERROR
            raise
    
    async def end_session(self, session_id: str, reason: str = "user_requested") -> bool:
        """
        End chat session and cleanup resources
        
        Args:
            session_id: Session to terminate
            reason: Termination reason
            
        Returns:
            bool: Success status
        """
        try:
            session = await self._get_active_session(session_id)
            if not session:
                return False
            
            # Update session status
            session.status = ChatStatus.ENDED
            session.updated_at = datetime.utcnow()
            session.metadata["end_reason"] = reason
            
            # Save final session state
            await self.session_controller.update_session(session)
            
            # Track session end analytics
            await self.analytics.track_session_ended(session, reason)
            
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Cleanup cache
            await self.cache.delete(f"chat_session:{session_id}")
            
            self.logger.info(f"Ended chat session {session_id}, reason: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to end session {session_id}: {str(e)}")
            return False
    
    async def get_session_history(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve session conversation history
        
        Args:
            session_id: Target session
            limit: Maximum messages to return
            offset: Message offset for pagination
            
        Returns:
            Dict containing session history and metadata
        """
        try:
            session = await self.session_controller.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            # Paginate messages
            total_messages = len(session.messages)
            start_idx = max(0, offset)
            end_idx = min(total_messages, offset + limit)
            paginated_messages = session.messages[start_idx:end_idx]
            
            return {
                "session_id": session_id,
                "creator_type": session.creator_type.value,
                "status": session.status.value,
                "total_messages": total_messages,
                "messages": paginated_messages,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": end_idx < total_messages
                },
                "metadata": {
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "duration_minutes": self._calculate_session_duration(session)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session history {session_id}: {str(e)}")
            raise
    
    async def get_active_sessions(
        self,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of active chat sessions
        
        Args:
            user_id: Optional filter by user
            
        Returns:
            List of active session summaries
        """
        try:
            sessions = []
            for session in self.active_sessions.values():
                if user_id and session.user_id != user_id:
                    continue
                
                sessions.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "creator_type": session.creator_type.value,
                    "status": session.status.value,
                    "message_count": len(session.messages),
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "expires_at": session.expires_at.isoformat() if session.expires_at else None
                })
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get active sessions: {str(e)}")
            raise
    
    async def _generate_session_id(self, user_id: str) -> str:
        """Generate unique session identifier"""
        import uuid
        timestamp = int(datetime.utcnow().timestamp())
        unique_id = str(uuid.uuid4())[:8]
        return f"chat_{user_id}_{timestamp}_{unique_id}"
    
    async def _get_active_session(self, session_id: str) -> Optional[ChatSession]:
        """Get active session from cache or database"""
        # Check active sessions first
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            # Check if session is still valid
            if session.expires_at and datetime.utcnow() > session.expires_at:
                await self.end_session(session_id, "expired")
                return None
            return session
        
        # Try to load from database
        session = await self.session_controller.get_session(session_id)
        if session and session.status == ChatStatus.ACTIVE:
            self.active_sessions[session_id] = session
            return session
        
        return None
    
    async def _initialize_creator_context(
        self,
        creator_type: CreatorType,
        user_profile: Dict[str, Any],
        initial_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize creator-specific session context"""
        base_context = {
            "creator_type": creator_type.value,
            "user_preferences": user_profile.get("preferences", {}),
            "content_categories": user_profile.get("content_categories", []),
            "monetization_enabled": user_profile.get("monetization_enabled", False),
            "protection_level": user_profile.get("protection_level", "standard"),
            "language": user_profile.get("language", "en"),
            "timezone": user_profile.get("timezone", "UTC")
        }
        
        # Creator-specific context initialization
        if creator_type == CreatorType.MUSICIAN:
            base_context.update({
                "music_genres": user_profile.get("music_genres", []),
                "spotify_connected": user_profile.get("spotify_connected", False),
                "collaboration_open": user_profile.get("collaboration_open", False),
                "audio_analysis_enabled": True
            })
        elif creator_type == CreatorType.BLOGGER:
            base_context.update({
                "blog_topics": user_profile.get("blog_topics", []),
                "seo_optimization": user_profile.get("seo_optimization", True),
                "content_calendar": user_profile.get("content_calendar", {}),
                "text_analysis_enabled": True
            })
        elif creator_type == CreatorType.PHOTOGRAPHER:
            base_context.update({
                "photography_styles": user_profile.get("photography_styles", []),
                "portfolio_connected": user_profile.get("portfolio_connected", False),
                "licensing_enabled": user_profile.get("licensing_enabled", True),
                "image_analysis_enabled": True
            })
        elif creator_type == CreatorType.INFLUENCER:
            base_context.update({
                "social_platforms": user_profile.get("social_platforms", []),
                "audience_demographics": user_profile.get("audience_demographics", {}),
                "brand_partnerships": user_profile.get("brand_partnerships", []),
                "multi_format_enabled": True
            })
        elif creator_type == CreatorType.COMEDIAN:
            base_context.update({
                "comedy_styles": user_profile.get("comedy_styles", []),
                "performance_venues": user_profile.get("performance_venues", []),
                "video_content_enabled": user_profile.get("video_content_enabled", True),
                "audio_video_analysis_enabled": True
            })
        
        # Merge with initial context
        base_context.update(initial_context)
        return base_context
    
    def _calculate_session_duration(self, session: ChatSession) -> float:
        """Calculate session duration in minutes"""
        duration = session.updated_at - session.created_at
        return round(duration.total_seconds() / 60, 2)
    
    async def cleanup_expired_sessions(self) -> int:
        """Cleanup expired sessions - called by background task"""
        cleaned_count = 0
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.expires_at and datetime.utcnow() > session.expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.end_session(session_id, "expired")
            cleaned_count += 1
        
        self.logger.info(f"Cleaned up {cleaned_count} expired chat sessions")
        return cleaned_count
