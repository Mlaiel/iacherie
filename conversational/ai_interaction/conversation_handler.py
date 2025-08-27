"""
Conversation Handler Module
=========================

Advanced conversation flow management for AI interactions.
Handles complex conversation states, context management, and flow control.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from backend.core.exceptions import ConversationError, ValidationError
from backend.core.database import get_async_db
from backend.core.cache import CacheManager
from backend.conversational.context_tracking import ContextTracker
from backend.conversational.session_management import SessionManager

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Conversation state types"""
    IDLE = "idle"
    ACTIVE = "active"
    WAITING_INPUT = "waiting_input"
    PROCESSING = "processing"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"


class ConversationMode(Enum):
    """Conversation interaction modes"""
    FREE_FORM = "free_form"
    GUIDED = "guided"
    STRUCTURED = "structured"
    INTERVIEW = "interview"
    ONBOARDING = "onboarding"
    TROUBLESHOOTING = "troubleshooting"


class MessageType(Enum):
    """Types of conversation messages"""
    USER_MESSAGE = "user_message"
    AI_RESPONSE = "ai_response"
    SYSTEM_MESSAGE = "system_message"
    ACTION_REQUIRED = "action_required"
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"


@dataclass
class ConversationMessage:
    """Individual conversation message"""
    message_id: str
    message_type: MessageType
    content: str
    sender: str  # "user" or "ai" or "system"
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class ConversationFlow:
    """Conversation flow configuration"""
    flow_id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]
    current_step: int = 0
    completion_criteria: Dict[str, Any] = field(default_factory=dict)
    branching_logic: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """Complete conversation session data"""
    session_id: str
    user_id: str
    creator_type: str
    state: ConversationState
    mode: ConversationMode
    messages: List[ConversationMessage]
    context_data: Dict[str, Any]
    current_flow: Optional[ConversationFlow] = None
    goals: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationHandler:
    """
    Advanced Conversation Flow Management System
    
    Manages complex conversation states, flow control, and context awareness
    for intelligent AI interactions with content creators.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.context_tracker = ContextTracker()
        self.session_manager = SessionManager()
        self._active_conversations = {}
        self._conversation_flows = {}
        self._message_handlers = {}
        
    async def initialize(self) -> None:
        """Initialize the conversation handler"""
        try:
            await self.context_tracker.initialize()
            await self.session_manager.initialize()
            await self._load_conversation_flows()
            await self._register_message_handlers()
            logger.info("Conversation Handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Conversation Handler: {e}")
            raise ConversationError(f"Initialization failed: {e}")
    
    async def start_conversation(
        self,
        user_id: str,
        creator_type: str,
        mode: str = "free_form",
        initial_context: Optional[Dict] = None,
        flow_id: Optional[str] = None
    ) -> str:
        """
        Start a new conversation session
        
        Args:
            user_id: User identifier
            creator_type: Type of content creator
            mode: Conversation mode
            initial_context: Initial context data
            flow_id: Specific conversation flow to follow
            
        Returns:
            Session ID for the new conversation
        """
        try:
            session_id = f"conv_{user_id}_{datetime.now().timestamp()}"
            
            # Load conversation flow if specified
            conversation_flow = None
            if flow_id:
                conversation_flow = await self._load_conversation_flow(flow_id)
            
            # Create conversation session
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                creator_type=creator_type,
                state=ConversationState.ACTIVE,
                mode=ConversationMode(mode),
                messages=[],
                context_data=initial_context or {},
                current_flow=conversation_flow
            )
            
            # Store active conversation
            self._active_conversations[session_id] = session
            
            # Cache session
            await self._cache_conversation_session(session)
            
            # Initialize context tracking
            await self.context_tracker.initialize_conversation_context(
                session_id, user_id, creator_type
            )
            
            # Send welcome message if in guided mode
            if session.mode in [ConversationMode.GUIDED, ConversationMode.STRUCTURED]:
                await self._send_welcome_message(session)
            
            logger.info(f"Started conversation {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise ConversationError(f"Conversation start failed: {e}")
    
    async def process_message(
        self,
        session_id: str,
        message_content: str,
        message_type: str = "user_message",
        attachments: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process incoming conversation message
        
        Args:
            session_id: Conversation session ID
            message_content: Message content
            message_type: Type of message
            attachments: Optional message attachments
            metadata: Optional message metadata
            
        Returns:
            Processing result with AI response
        """
        try:
            # Get conversation session
            session = await self._get_conversation_session(session_id)
            if not session:
                raise ConversationError("Invalid session ID")
            
            # Validate message
            await self._validate_message(message_content, session)
            
            # Create message object
            message = ConversationMessage(
                message_id=f"msg_{datetime.now().timestamp()}",
                message_type=MessageType(message_type),
                content=message_content,
                sender="user",
                timestamp=datetime.now(),
                metadata=metadata or {},
                attachments=attachments or []
            )
            
            # Add to session messages
            session.messages.append(message)
            session.last_activity = datetime.now()
            
            # Update conversation state
            session.state = ConversationState.PROCESSING
            
            # Process message based on conversation mode
            processing_result = await self._process_message_by_mode(session, message)
            
            # Generate AI response
            ai_response = await self._generate_ai_response(session, message, processing_result)
            
            # Add AI response to messages
            ai_message = ConversationMessage(
                message_id=f"msg_{datetime.now().timestamp()}",
                message_type=MessageType.AI_RESPONSE,
                content=ai_response["content"],
                sender="ai",
                timestamp=datetime.now(),
                metadata=ai_response.get("metadata", {})
            )
            
            session.messages.append(ai_message)
            
            # Update conversation state
            session.state = ConversationState.ACTIVE
            
            # Update context tracking
            await self.context_tracker.update_conversation_context(
                session_id, message_content, ai_response["content"]
            )
            
            # Cache updated session
            await self._cache_conversation_session(session)
            
            # Prepare response
            response = {
                "session_id": session_id,
                "ai_response": ai_response["content"],
                "conversation_state": session.state.value,
                "message_id": ai_message.message_id,
                "suggestions": ai_response.get("suggestions", []),
                "next_actions": ai_response.get("next_actions", []),
                "flow_progress": self._get_flow_progress(session),
                "metadata": ai_response.get("metadata", {})
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            raise ConversationError(f"Message processing failed: {e}")
    
    async def handle_conversation_flow(
        self,
        session_id: str,
        flow_action: str,
        action_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Handle conversation flow actions
        
        Args:
            session_id: Conversation session ID
            flow_action: Flow action to execute
            action_data: Optional action data
            
        Returns:
            Flow handling result
        """
        try:
            session = await self._get_conversation_session(session_id)
            if not session or not session.current_flow:
                raise ConversationError("No active conversation flow")
            
            # Process flow action
            flow_result = await self._process_flow_action(
                session, flow_action, action_data
            )
            
            # Update session with flow changes
            await self._update_session_with_flow_result(session, flow_result)
            
            # Cache updated session
            await self._cache_conversation_session(session)
            
            return {
                "session_id": session_id,
                "flow_action": flow_action,
                "flow_result": flow_result,
                "current_step": session.current_flow.current_step,
                "flow_progress": self._get_flow_progress(session),
                "next_step_required": flow_result.get("next_step_required", False)
            }
            
        except Exception as e:
            logger.error(f"Flow handling failed: {e}")
            raise ConversationError(f"Flow handling failed: {e}")
    
    async def get_conversation_summary(
        self,
        session_id: str,
        summary_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Get conversation summary and insights
        
        Args:
            session_id: Conversation session ID
            summary_type: Type of summary to generate
            
        Returns:
            Conversation summary with insights
        """
        try:
            session = await self._get_conversation_session(session_id)
            if not session:
                raise ConversationError("Invalid session ID")
            
            # Generate summary based on type
            if summary_type == "comprehensive":
                summary = await self._generate_comprehensive_summary(session)
            elif summary_type == "brief":
                summary = await self._generate_brief_summary(session)
            elif summary_type == "insights":
                summary = await self._generate_insights_summary(session)
            else:
                summary = await self._generate_basic_summary(session)
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise ConversationError(f"Summary generation failed: {e}")
    
    async def pause_conversation(self, session_id: str) -> bool:
        """
        Pause an active conversation
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            Success status
        """
        try:
            session = await self._get_conversation_session(session_id)
            if not session:
                return False
            
            session.state = ConversationState.PAUSED
            session.last_activity = datetime.now()
            
            await self._cache_conversation_session(session)
            
            logger.info(f"Paused conversation {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause conversation: {e}")
            return False
    
    async def resume_conversation(self, session_id: str) -> bool:
        """
        Resume a paused conversation
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            Success status
        """
        try:
            session = await self._get_conversation_session(session_id)
            if not session or session.state != ConversationState.PAUSED:
                return False
            
            session.state = ConversationState.ACTIVE
            session.last_activity = datetime.now()
            
            await self._cache_conversation_session(session)
            
            logger.info(f"Resumed conversation {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume conversation: {e}")
            return False
    
    async def end_conversation(
        self,
        session_id: str,
        reason: str = "user_request"
    ) -> Dict[str, Any]:
        """
        End a conversation session
        
        Args:
            session_id: Conversation session ID
            reason: Reason for ending conversation
            
        Returns:
            Conversation end summary
        """
        try:
            session = await self._get_conversation_session(session_id)
            if not session:
                raise ConversationError("Invalid session ID")
            
            # Generate final summary
            final_summary = await self._generate_final_summary(session, reason)
            
            # Update session state
            session.state = ConversationState.ENDED
            session.metadata["end_reason"] = reason
            session.metadata["ended_at"] = datetime.now().isoformat()
            
            # Save final session state
            await self._save_final_session_state(session)
            
            # Clean up active conversation
            if session_id in self._active_conversations:
                del self._active_conversations[session_id]
            
            # Clean up context tracking
            await self.context_tracker.cleanup_conversation_context(session_id)
            
            logger.info(f"Ended conversation {session_id}")
            return final_summary
            
        except Exception as e:
            logger.error(f"Failed to end conversation: {e}")
            raise ConversationError(f"Conversation end failed: {e}")
    
    async def get_conversation_metrics(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get conversation performance metrics
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            Conversation metrics and analytics
        """
        try:
            session = await self._get_conversation_session(session_id)
            if not session:
                raise ConversationError("Invalid session ID")
            
            # Calculate metrics
            duration = (session.last_activity - session.started_at).total_seconds()
            message_count = len(session.messages)
            user_messages = [m for m in session.messages if m.sender == "user"]
            ai_messages = [m for m in session.messages if m.sender == "ai"]
            
            metrics = {
                "session_id": session_id,
                "duration_seconds": duration,
                "total_messages": message_count,
                "user_messages": len(user_messages),
                "ai_messages": len(ai_messages),
                "conversation_state": session.state.value,
                "conversation_mode": session.mode.value,
                "flow_completion": self._calculate_flow_completion(session),
                "engagement_score": await self._calculate_engagement_score(session),
                "satisfaction_indicators": await self._analyze_satisfaction_indicators(session)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            raise ConversationError(f"Metrics calculation failed: {e}")
    
    # Private helper methods
    async def _get_conversation_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get conversation session from cache or memory"""
        if session_id in self._active_conversations:
            return self._active_conversations[session_id]
        
        # Try to load from cache
        cached_session = await self.cache_manager.get(f"conversation:{session_id}")
        if cached_session:
            session = await self._deserialize_session(cached_session)
            self._active_conversations[session_id] = session
            return session
        
        return None
    
    async def _validate_message(self, message_content: str, session: ConversationSession) -> None:
        """Validate incoming message"""
        if not message_content or len(message_content.strip()) == 0:
            raise ValidationError("Message content cannot be empty")
        
        if len(message_content) > 10000:
            raise ValidationError("Message too long (max 10000 characters)")
        
        if session.state == ConversationState.ENDED:
            raise ValidationError("Cannot send message to ended conversation")
    
    async def _process_message_by_mode(
        self,
        session: ConversationSession,
        message: ConversationMessage
    ) -> Dict[str, Any]:
        """Process message based on conversation mode"""
        if session.mode == ConversationMode.FREE_FORM:
            return await self._process_free_form_message(session, message)
        elif session.mode == ConversationMode.GUIDED:
            return await self._process_guided_message(session, message)
        elif session.mode == ConversationMode.STRUCTURED:
            return await self._process_structured_message(session, message)
        elif session.mode == ConversationMode.INTERVIEW:
            return await self._process_interview_message(session, message)
        elif session.mode == ConversationMode.ONBOARDING:
            return await self._process_onboarding_message(session, message)
        else:
            return await self._process_default_message(session, message)
    
    async def _generate_ai_response(
        self,
        session: ConversationSession,
        user_message: ConversationMessage,
        processing_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI response for conversation"""
        try:
            # Prepare response context
            response_context = {
                "session_data": {
                    "user_id": session.user_id,
                    "creator_type": session.creator_type,
                    "conversation_mode": session.mode.value,
                    "conversation_history": [
                        {"sender": m.sender, "content": m.content} 
                        for m in session.messages[-10:]  # Last 10 messages
                    ]
                },
                "user_message": user_message.content,
                "processing_result": processing_result,
                "context_data": session.context_data
            }
            
            # Use appropriate handler based on message type or conversation mode
            if session.mode == ConversationMode.STRUCTURED and session.current_flow:
                response = await self._generate_structured_response(response_context, session)
            else:
                response = await self._generate_conversational_response(response_context)
            
            return response
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return {
                "content": "I understand your message. How can I help you further?",
                "metadata": {"error": str(e)},
                "suggestions": [],
                "next_actions": []
            }
    
    async def _cache_conversation_session(self, session: ConversationSession) -> None:
        """Cache conversation session"""
        try:
            cache_key = f"conversation:{session.session_id}"
            serialized_session = await self._serialize_session(session)
            await self.cache_manager.set(cache_key, serialized_session, expire=3600)
        except Exception as e:
            logger.error(f"Session caching failed: {e}")
    
    async def _serialize_session(self, session: ConversationSession) -> Dict[str, Any]:
        """Serialize session for caching"""
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "creator_type": session.creator_type,
            "state": session.state.value,
            "mode": session.mode.value,
            "messages": [
                {
                    "message_id": m.message_id,
                    "message_type": m.message_type.value,
                    "content": m.content,
                    "sender": m.sender,
                    "timestamp": m.timestamp.isoformat(),
                    "metadata": m.metadata
                }
                for m in session.messages
            ],
            "context_data": session.context_data,
            "goals": session.goals,
            "preferences": session.preferences,
            "started_at": session.started_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "metadata": session.metadata
        }
    
    async def _deserialize_session(self, session_data: Dict[str, Any]) -> ConversationSession:
        """Deserialize session from cache"""
        messages = []
        for msg_data in session_data.get("messages", []):
            message = ConversationMessage(
                message_id=msg_data["message_id"],
                message_type=MessageType(msg_data["message_type"]),
                content=msg_data["content"],
                sender=msg_data["sender"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                metadata=msg_data.get("metadata", {})
            )
            messages.append(message)
        
        return ConversationSession(
            session_id=session_data["session_id"],
            user_id=session_data["user_id"],
            creator_type=session_data["creator_type"],
            state=ConversationState(session_data["state"]),
            mode=ConversationMode(session_data["mode"]),
            messages=messages,
            context_data=session_data.get("context_data", {}),
            goals=session_data.get("goals", []),
            preferences=session_data.get("preferences", {}),
            started_at=datetime.fromisoformat(session_data["started_at"]),
            last_activity=datetime.fromisoformat(session_data["last_activity"]),
            metadata=session_data.get("metadata", {})
        )
    
    # Message processing methods for different modes
    async def _process_free_form_message(
        self, 
        session: ConversationSession, 
        message: ConversationMessage
    ) -> Dict[str, Any]:
        """Process free-form conversation message"""
        return {
            "processing_type": "free_form",
            "intent_analysis": await self._analyze_message_intent(message.content),
            "context_update": await self._update_conversation_context(session, message)
        }
    
    async def _process_guided_message(
        self, 
        session: ConversationSession, 
        message: ConversationMessage
    ) -> Dict[str, Any]:
        """Process guided conversation message"""
        return {
            "processing_type": "guided",
            "guidance_step": await self._determine_guidance_step(session, message),
            "next_guidance": await self._prepare_next_guidance(session, message)
        }
    
    async def _process_structured_message(
        self, 
        session: ConversationSession, 
        message: ConversationMessage
    ) -> Dict[str, Any]:
        """Process structured conversation message"""
        return {
            "processing_type": "structured",
            "flow_validation": await self._validate_flow_input(session, message),
            "flow_progression": await self._progress_conversation_flow(session, message)
        }
    
    # Additional helper methods
    async def _load_conversation_flows(self) -> None:
        """Load predefined conversation flows"""
        self._conversation_flows = {
            "onboarding": ConversationFlow(
                flow_id="onboarding",
                name="Creator Onboarding",
                description="Onboarding flow for new content creators",
                steps=[
                    {"step": "welcome", "type": "introduction"},
                    {"step": "creator_type", "type": "selection"},
                    {"step": "goals", "type": "input"},
                    {"step": "preferences", "type": "configuration"},
                    {"step": "completion", "type": "summary"}
                ]
            ),
            "content_analysis": ConversationFlow(
                flow_id="content_analysis", 
                name="Content Analysis Session",
                description="Guided content analysis and optimization",
                steps=[
                    {"step": "content_upload", "type": "file_input"},
                    {"step": "analysis_options", "type": "selection"},
                    {"step": "analysis_results", "type": "presentation"},
                    {"step": "optimization_suggestions", "type": "recommendations"},
                    {"step": "action_plan", "type": "planning"}
                ]
            )
        }
    
    async def _register_message_handlers(self) -> None:
        """Register message handlers for different types"""
        self._message_handlers = {
            MessageType.USER_MESSAGE: self._handle_user_message,
            MessageType.ACTION_REQUIRED: self._handle_action_required,
            MessageType.CLARIFICATION: self._handle_clarification_request,
            MessageType.CONFIRMATION: self._handle_confirmation_request
        }
    
    def _get_flow_progress(self, session: ConversationSession) -> Dict[str, Any]:
        """Get conversation flow progress"""
        if not session.current_flow:
            return {"has_flow": False}
        
        total_steps = len(session.current_flow.steps)
        current_step = session.current_flow.current_step
        
        return {
            "has_flow": True,
            "flow_name": session.current_flow.name,
            "current_step": current_step,
            "total_steps": total_steps,
            "progress_percentage": (current_step / total_steps) * 100 if total_steps > 0 else 0,
            "next_step": session.current_flow.steps[current_step] if current_step < total_steps else None
        }
