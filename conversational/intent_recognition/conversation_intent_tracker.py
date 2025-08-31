"""Conversation Intent Tracking System

Advanced session-aware intent tracking with conversation flow analysis,
context management, and multi-turn conversation understanding.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import logging
import json

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from .intent_classifier import IntentCategory, ClassificationResult
from .config import IntentRecognitionConfig
from .exceptions import ValidationError


@dataclass
class ConversationTurn:
    """Single turn in a conversation"""    turn_id: str
    user_input: str
    intent_result: ClassificationResult
    system_response: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Complete conversation context and state"""    session_id: str
    user_id: str
    conversation_stage: str = "initial"
    active_intent: Optional[IntentCategory] = None
    pending_actions: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    context_variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    @property
    def conversation_length(self) -> int:
        return len(self.conversation_history)
    
    @property
    def duration_minutes(self) -> float:
        return (self.last_activity - self.created_at).total_seconds() / 60
    
    def get_recent_intents(self, count: int = 5) -> List[IntentCategory]:
        """Get recent intents from conversation history"""        recent_turns = self.conversation_history[-count:] if self.conversation_history else []
        return [turn.intent_result.primary_intent for turn in recent_turns]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get condensed context summary"""        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'stage': self.conversation_stage,
            'active_intent': self.active_intent.value if self.active_intent else None,
            'turn_count': self.conversation_length,
            'duration_minutes': self.duration_minutes,
            'recent_intents': [intent.value for intent in self.get_recent_intents()],
            'pending_actions': self.pending_actions,
            'last_activity': self.last_activity.isoformat()
        }


class IntentSessionManager:
    """    Manages conversation sessions and state persistence
    
    Features:
    - Session lifecycle management
    - Context state persistence
    - Session timeout handling
    - User preference tracking
    """    
    def __init__(self, config: IntentRecognitionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Session storage (in production would use Redis/database)
        self.active_sessions: Dict[str, ConversationContext] = {}
        self.session_timeout = timedelta(hours=2)  # Session timeout
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self) -> None:
        """Start background task for session cleanup"""        asyncio.create_task(self._cleanup_expired_sessions())
    
    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                now = datetime.now()
                expired_sessions = []
                
                for session_id, context in self.active_sessions.items():
                    if now - context.last_activity > self.session_timeout:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self.close_session(session_id)
                
                if expired_sessions:
                    self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
            except Exception as e:
                self.logger.error(f"Session cleanup error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> ConversationContext:
        """Create new conversation session"""        if not session_id:
            session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"
        
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            context_variables=initial_context or {}
        )
        
        self.active_sessions[session_id] = context
        
        self.logger.info(f"Created session {session_id} for user {user_id}")
        return context
    
    async def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get existing conversation session"""        context = self.active_sessions.get(session_id)
        
        if context:
            # Update last activity
            context.last_activity = datetime.now()
        
        return context
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ConversationContext]:
        """Update session context"""        context = await self.get_session(session_id)
        
        if context:
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
                else:
                    context.context_variables[key] = value
            
            context.last_activity = datetime.now()
        
        return context
    
    async def close_session(self, session_id: str) -> bool:
        """Close and clean up session"""        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            
            # Save session data if needed (to database, etc.)
            await self._persist_session_data(context)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            self.logger.info(f"Closed session {session_id}")
            return True
        
        return False
    
    async def _persist_session_data(self, context: ConversationContext) -> None:
        """Persist session data for analytics"""        try:
            # In production, save to database for analytics
            session_data = {
                'session_id': context.session_id,
                'user_id': context.user_id,
                'duration_minutes': context.duration_minutes,
                'turn_count': context.conversation_length,
                'final_stage': context.conversation_stage,
                'intents_used': [intent.value for intent in context.get_recent_intents(100)],
                'created_at': context.created_at.isoformat(),
                'closed_at': datetime.now().isoformat()
            }
            
            self.logger.debug(f"Session data persisted: {session_data}")
            
        except Exception as e:
            self.logger.error(f"Failed to persist session data: {str(e)}")
    
    def get_active_session_count(self) -> int:
        """Get number of active sessions"""        return len(self.active_sessions)
    
    def get_user_sessions(self, user_id: str) -> List[ConversationContext]:
        """Get all active sessions for a user"""        return [
            context for context in self.active_sessions.values()
            if context.user_id == user_id
        ]


class ConversationIntentTracker(BaseService):
    """    Advanced conversation intent tracking with flow analysis
    
    Features:
    - Multi-turn conversation understanding
    - Intent flow pattern recognition
    - Context-aware intent enhancement
    - Conversation state management
    - Intent transition analysis
    """    
    def __init__(self, config: IntentRecognitionConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Session management
        self.session_manager = IntentSessionManager(config)
        
        # Intent flow patterns
        self.intent_flows = self._load_intent_flow_patterns()
        
        # Conversation analysis
        self.conversation_analyzer = ConversationFlowAnalyzer()
    
    def _load_intent_flow_patterns(self) -> Dict[str, Any]:
        """Load common intent flow patterns"""        return {
            'content_creation_flow': [
                IntentCategory.CONTENT_UPLOAD,
                IntentCategory.CONTENT_ENHANCE,
                IntentCategory.PROTECTION_FINGERPRINT,
                IntentCategory.MONETIZATION_LICENSE
            ],
            'protection_setup_flow': [
                IntentCategory.PROTECTION_FINGERPRINT,
                IntentCategory.PROTECTION_MONITOR,
                IntentCategory.PROTECTION_CONFIGURE
            ],
            'analytics_deep_dive': [
                IntentCategory.ANALYTICS_PERFORMANCE,
                IntentCategory.ANALYTICS_AUDIENCE,
                IntentCategory.ANALYTICS_TRENDS,
                IntentCategory.ANALYTICS_FORECAST
            ],
            'collaboration_setup': [
                IntentCategory.COLLABORATION_INVITE,
                IntentCategory.COLLABORATION_PERMISSION,
                IntentCategory.COLLABORATION_WORKFLOW
            ]
        }
    
    async def track_intent_in_conversation(
        self,
        user_input: str,
        intent_result: ClassificationResult,
        user_id: str,
        session_id: Optional[str] = None,
        system_response: Optional[str] = None
    ) -> ConversationContext:
        """        Track intent within conversation context
        
        Args:
            user_input: User's input text
            intent_result: Classification result from intent classifier
            user_id: User identifier
            session_id: Optional session identifier
            system_response: Optional system response
            
        Returns:
            Updated conversation context
        """        try:
            # Get or create session
            if session_id:
                context = await self.session_manager.get_session(session_id)
                if not context:
                    context = await self.session_manager.create_session(user_id, session_id)
            else:
                # Create new session
                context = await self.session_manager.create_session(user_id)
            
            # Create conversation turn
            turn = ConversationTurn(
                turn_id=f"turn_{len(context.conversation_history) + 1}",
                user_input=user_input,
                intent_result=intent_result,
                system_response=system_response
            )
            
            # Add to conversation history
            context.conversation_history.append(turn)
            
            # Analyze conversation flow
            await self._analyze_conversation_flow(context, intent_result)
            
            # Update conversation stage
            await self._update_conversation_stage(context, intent_result)
            
            # Extract and update context variables
            await self._extract_context_variables(context, user_input, intent_result)
            
            # Update active intent
            context.active_intent = intent_result.primary_intent
            context.last_activity = datetime.now()
            
            return context
            
        except Exception as e:
            self.logger.error(f"Intent tracking failed: {str(e)}")
            raise ValidationError(f"Failed to track intent in conversation: {str(e)}")
    
    async def _analyze_conversation_flow(
        self,
        context: ConversationContext,
        current_intent: ClassificationResult
    ) -> None:
        """Analyze conversation flow patterns"""        try:
            recent_intents = context.get_recent_intents(5)
            
            # Check for recognized flow patterns
            for flow_name, flow_pattern in self.intent_flows.items():
                if self._matches_flow_pattern(recent_intents, flow_pattern):
                    context.context_variables['detected_flow'] = flow_name
                    context.context_variables['flow_progress'] = len(recent_intents) / len(flow_pattern)
                    break
            
            # Analyze intent transitions
            if len(recent_intents) >= 2:
                transition = f"{recent_intents[-2].value} -> {recent_intents[-1].value}"
                context.context_variables['last_transition'] = transition
                
                # Track common transitions for learning
                if 'transitions' not in context.context_variables:
                    context.context_variables['transitions'] = []
                context.context_variables['transitions'].append(transition)
            
        except Exception as e:
            self.logger.warning(f"Conversation flow analysis failed: {str(e)}")
    
    def _matches_flow_pattern(
        self,
        recent_intents: List[IntentCategory],
        flow_pattern: List[IntentCategory]
    ) -> bool:
        """Check if recent intents match a flow pattern"""        if len(recent_intents) < 2:
            return False
        
        # Check if recent intents are a subsequence of the flow pattern
        for i in range(len(flow_pattern) - len(recent_intents) + 1):
            if flow_pattern[i:i + len(recent_intents)] == recent_intents:
                return True
        
        return False
    
    async def _update_conversation_stage(
        self,
        context: ConversationContext,
        intent_result: ClassificationResult
    ) -> None:
        """Update conversation stage based on current intent"""        try:
            current_intent = intent_result.primary_intent
            
            # Define stage transitions
            stage_mapping = {
                IntentCategory.HELP_SUPPORT: "onboarding",
                IntentCategory.CONTENT_UPLOAD: "content_creation",
                IntentCategory.PROTECTION_FINGERPRINT: "protection_setup",
                IntentCategory.MONETIZATION_LICENSE: "monetization_setup",
                IntentCategory.COLLABORATION_INVITE: "collaboration_setup",
                IntentCategory.ANALYTICS_PERFORMANCE: "analytics_exploration"
            }
            
            new_stage = stage_mapping.get(current_intent)
            if new_stage and new_stage != context.conversation_stage:
                context.context_variables['previous_stage'] = context.conversation_stage
                context.conversation_stage = new_stage
                
                self.logger.debug(f"Conversation stage changed to: {new_stage}")
            
        except Exception as e:
            self.logger.warning(f"Stage update failed: {str(e)}")
    
    async def _extract_context_variables(
        self,
        context: ConversationContext,
        user_input: str,
        intent_result: ClassificationResult
    ) -> None:
        """Extract relevant context variables from user input and intent"""        try:
            # Extract entities from intent parameters
            if intent_result.intent_parameters:
                entities = intent_result.intent_parameters.get('entities', {})
                
                # Update context with extracted entities
                for entity_type, entity_value in entities.items():
                    if entity_value:
                        context.context_variables[f'last_{entity_type}'] = entity_value
            
            # Extract platform mentions
            platform_mentions = self._extract_platform_mentions(user_input)
            if platform_mentions:
                context.context_variables['platforms_mentioned'] = platform_mentions
            
            # Extract content type mentions
            content_types = self._extract_content_types(user_input)
            if content_types:
                context.context_variables['content_types_mentioned'] = content_types
            
            # Update user preferences based on repeated patterns
            await self._update_user_preferences(context, intent_result)
            
        except Exception as e:
            self.logger.warning(f"Context variable extraction failed: {str(e)}")
    
    def _extract_platform_mentions(self, text: str) -> List[str]:
        """Extract platform mentions from text"""        import re
        platforms = ['spotify', 'youtube', 'instagram', 'tiktok', 'soundcloud', 'bandcamp']
        found_platforms = []
        
        for platform in platforms:
            if re.search(rf'\b{platform}\b', text.lower()):
                found_platforms.append(platform)
        
        return found_platforms
    
    def _extract_content_types(self, text: str) -> List[str]:
        """Extract content type mentions from text"""        import re
        content_types = ['song', 'track', 'album', 'playlist', 'video', 'photo', 'post', 'story']
        found_types = []
        
        for content_type in content_types:
            if re.search(rf'\b{content_type}\b', text.lower()):
                found_types.append(content_type)
        
        return found_types
    
    async def _update_user_preferences(
        self,
        context: ConversationContext,
        intent_result: ClassificationResult
    ) -> None:
        """Update user preferences based on conversation patterns"""        try:
            intent = intent_result.primary_intent
            
            # Track intent frequency
            if 'intent_frequency' not in context.user_preferences:
                context.user_preferences['intent_frequency'] = {}
            
            intent_freq = context.user_preferences['intent_frequency']
            intent_freq[intent.value] = intent_freq.get(intent.value, 0) + 1
            
            # Determine primary user interests
            most_used_intents = sorted(
                intent_freq.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            context.user_preferences['primary_interests'] = [
                intent for intent, count in most_used_intents
            ]
            
        except Exception as e:
            self.logger.warning(f"User preference update failed: {str(e)}")
    
    async def get_conversation_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get current conversation context"""        return await self.session_manager.get_session(session_id)
    
    async def get_enhanced_context_for_intent(
        self,
        session_id: str,
        current_intent: IntentCategory
    ) -> Dict[str, Any]:
        """        Get enhanced context for intent classification
        
        Args:
            session_id: Session identifier
            current_intent: Current intent being processed
            
        Returns:
            Enhanced context dictionary
        """        try:
            context = await self.get_conversation_context(session_id)
            
            if not context:
                return {}
            
            enhanced_context = {
                'previous_intent': None,
                'conversation_stage': context.conversation_stage,
                'user_type': self._determine_user_type(context),
                'session_length': context.conversation_length,
                'flow_context': context.context_variables.get('detected_flow'),
                'recent_intents': [intent.value for intent in context.get_recent_intents(3)],
                'pending_actions': context.pending_actions,
                'user_preferences': context.user_preferences,
                'platforms_used': context.context_variables.get('platforms_mentioned', []),
                'content_types': context.context_variables.get('content_types_mentioned', [])
            }
            
            # Add previous intent if available
            recent_intents = context.get_recent_intents(2)
            if len(recent_intents) >= 2:
                enhanced_context['previous_intent'] = recent_intents[-2].value
            
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"Enhanced context generation failed: {str(e)}")
            return {}
    
    def _determine_user_type(self, context: ConversationContext) -> str:
        """Determine user type based on conversation patterns"""        try:
            intent_freq = context.user_preferences.get('intent_frequency', {})
            
            # Analyze intent patterns to determine user type
            content_creation = sum(
                intent_freq.get(intent, 0) for intent in [
                    'content_upload', 'content_edit', 'content_enhance', 'content_generate'
                ]
            )
            
            protection_usage = sum(
                intent_freq.get(intent, 0) for intent in [
                    'protection_fingerprint', 'protection_monitor', 'protection_report'
                ]
            )
            
            monetization_usage = sum(
                intent_freq.get(intent, 0) for intent in [
                    'monetization_track', 'monetization_license', 'monetization_payout'
                ]
            )
            
            analytics_usage = sum(
                intent_freq.get(intent, 0) for intent in [
                    'analytics_performance', 'analytics_audience', 'analytics_trends'
                ]
            )
            
            # Determine primary user type
            usage_scores = {
                'content_creator': content_creation,
                'rights_protector': protection_usage,
                'revenue_optimizer': monetization_usage,
                'data_analyst': analytics_usage
            }
            
            if max(usage_scores.values()) == 0:
                return 'new_user'
            
            return max(usage_scores.items(), key=lambda x: x[1])[0]
            
        except Exception as e:
            self.logger.warning(f"User type determination failed: {str(e)}")
            return 'unknown'
    
    async def predict_next_intent(
        self,
        session_id: str,
        confidence_threshold: float = 0.6
    ) -> Optional[Tuple[IntentCategory, float]]:
        """        Predict likely next intent based on conversation flow
        
        Args:
            session_id: Session identifier
            confidence_threshold: Minimum confidence for prediction
            
        Returns:
            Tuple of (predicted_intent, confidence) or None
        """        try:
            context = await self.get_conversation_context(session_id)
            if not context or context.conversation_length == 0:
                return None
            
            recent_intents = context.get_recent_intents(3)
            current_intent = recent_intents[-1] if recent_intents else None
            
            if not current_intent:
                return None
            
            # Check flow patterns for prediction
            for flow_name, flow_pattern in self.intent_flows.items():
                try:
                    current_index = flow_pattern.index(current_intent)
                    if current_index < len(flow_pattern) - 1:
                        next_intent = flow_pattern[current_index + 1]
                        confidence = 0.7  # Base confidence for flow prediction
                        
                        # Adjust confidence based on flow progress
                        flow_progress = context.context_variables.get('flow_progress', 0)
                        confidence += flow_progress * 0.2
                        
                        if confidence >= confidence_threshold:
                            return next_intent, confidence
                
                except ValueError:
                    # Current intent not in this flow
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Next intent prediction failed: {str(e)}")
            return None
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive conversation summary"""        try:
            context = await self.get_conversation_context(session_id)
            if not context:
                return {}
            
            intent_distribution = {}
            for turn in context.conversation_history:
                intent = turn.intent_result.primary_intent.value
                intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
            
            return {
                'session_info': context.get_context_summary(),
                'intent_distribution': intent_distribution,
                'user_type': self._determine_user_type(context),
                'conversation_flow': context.context_variables.get('detected_flow'),
                'key_topics': {
                    'platforms': context.context_variables.get('platforms_mentioned', []),
                    'content_types': context.context_variables.get('content_types_mentioned', [])
                },
                'engagement_metrics': {
                    'turns_per_minute': context.conversation_length / max(context.duration_minutes, 1),
                    'avg_confidence': self._calculate_avg_confidence(context),
                    'completion_rate': self._calculate_completion_rate(context)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Conversation summary generation failed: {str(e)}")
            return {}
    
    def _calculate_avg_confidence(self, context: ConversationContext) -> float:
        """Calculate average confidence across conversation"""        if not context.conversation_history:
            return 0.0
        
        total_confidence = sum(
            turn.intent_result.confidence.primary_score
            for turn in context.conversation_history
        )
        
        return total_confidence / len(context.conversation_history)
    
    def _calculate_completion_rate(self, context: ConversationContext) -> float:
        """Calculate conversation completion rate"""        # Simple heuristic: longer conversations with flow completion = higher rate
        base_rate = min(context.conversation_length / 10, 0.8)  # Max 80% for length
        
        # Bonus for detected flow completion
        if context.context_variables.get('flow_progress', 0) > 0.8:
            base_rate += 0.2
        
        return min(base_rate, 1.0)


class ConversationFlowAnalyzer:
    """Analyzes conversation flows and patterns"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.flow_patterns = {}
    
    def analyze_conversation_patterns(
        self,
        conversations: List[ConversationContext]
    ) -> Dict[str, Any]:
        """Analyze patterns across multiple conversations"""        # Implementation for analyzing conversation patterns
        # This would be used for improving intent flow predictions
        pass
