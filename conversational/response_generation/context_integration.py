"""Context Integration System - Advanced Conversational Context Management

Enterprise-grade context integration for intelligent response generation
with multi-layered context awareness and business logic integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
from datetime import datetime, timedelta
import uuid

from pydantic import BaseModel, Field, validator
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ...core.exceptions import ContextError, ValidationError
from ...core.cache import CacheManager
from ...core.monitoring import MetricsCollector
from ...core.database import DatabaseManager


class ContextType(Enum):
    """Context type enumeration"""    USER_PROFILE = "user_profile"
    CONVERSATION_HISTORY = "conversation_history"
    BUSINESS_CONTEXT = "business_context"
    PLATFORM_CONTEXT = "platform_context"
    CONTENT_CONTEXT = "content_context"
    TEMPORAL_CONTEXT = "temporal_context"
    EMOTIONAL_CONTEXT = "emotional_context"
    INTENT_CONTEXT = "intent_context"
    COLLABORATION_CONTEXT = "collaboration_context"
    MONETIZATION_CONTEXT = "monetization_context"


class ContextPriority(Enum):
    """Context priority levels"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class ContextScope(Enum):
    """Context scope enumeration"""    SESSION = "session"
    CONVERSATION = "conversation"
    USER = "user"
    GLOBAL = "global"
    TEMPORARY = "temporary"


class ConversationContext(BaseModel):
    """Comprehensive conversation context data structure"""    context_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    conversation_id: str
    
    # Core Context Data
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_intent: Optional[str] = None
    emotional_state: Optional[str] = None
    
    # Business Context
    business_objectives: List[str] = Field(default_factory=list)
    current_workflow_stage: Optional[str] = None
    monetization_focus: Optional[str] = None
    protection_concerns: List[str] = Field(default_factory=list)
    collaboration_interests: List[str] = Field(default_factory=list)
    
    # Content Context
    content_type: Optional[str] = None
    content_metadata: Dict[str, Any] = Field(default_factory=dict)
    platform_preferences: List[str] = Field(default_factory=list)
    quality_standards: Dict[str, Any] = Field(default_factory=dict)
    
    # Temporal Context
    conversation_start: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: datetime = Field(default_factory=datetime.utcnow)
    session_duration: Optional[float] = None
    interaction_frequency: Optional[float] = None
    
    # Performance Context
    response_effectiveness: Dict[str, float] = Field(default_factory=dict)
    user_satisfaction: Optional[float] = None
    engagement_level: Optional[float] = None
    
    # Dynamic Context
    current_priorities: Dict[str, float] = Field(default_factory=dict)
    active_contexts: List[ContextType] = Field(default_factory=list)
    context_weights: Dict[str, float] = Field(default_factory=dict)
    
    # Metadata
    context_version: str = "1.0"
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('user_id', 'session_id', 'conversation_id')
    def validate_ids(cls, v):
        if not v or len(v) < 5:
            raise ValueError("IDs must be valid and non-empty")
        return v


class ContextualMemory(BaseModel):
    """Contextual memory for intelligent context retention"""    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    context_type: ContextType
    content: Dict[str, Any]
    importance_score: float = Field(..., ge=0.0, le=1.0)
    recency_score: float = Field(..., ge=0.0, le=1.0)
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    access_count: int = Field(default=0, ge=0)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    
    def calculate_memory_strength(self) -> float:
        """Calculate overall memory strength"""        weights = {
            "importance": 0.4,
            "recency": 0.3,
            "relevance": 0.2,
            "access_frequency": 0.1
        }
        
        # Calculate access frequency score
        days_since_creation = (datetime.utcnow() - self.last_accessed).days + 1
        access_frequency_score = min(self.access_count / days_since_creation, 1.0)
        
        strength = (
            self.importance_score * weights["importance"] +
            self.recency_score * weights["recency"] +
            self.relevance_score * weights["relevance"] +
            access_frequency_score * weights["access_frequency"]
        )
        
        return min(strength, 1.0)


class ConversationContextIntegrator:
    """Advanced context integration and management system"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = CacheManager()
        self.metrics = MetricsCollector()
        self.db = DatabaseManager()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.memory_store: Dict[str, List[ContextualMemory]] = {}
    
    async def integrate_conversation_context(
        self,
        user_id: str,
        session_id: str,
        conversation_id: str,
        current_input: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> ConversationContext:
        """        Integrate comprehensive conversation context
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            conversation_id: Conversation identifier
            current_input: Current user input
            additional_context: Additional context data
            
        Returns:
            Integrated conversation context
        """        try:
            # Get or create base context
            context = await self._get_or_create_context(user_id, session_id, conversation_id)
            
            # Update with current interaction
            await self._update_current_interaction(context, current_input, additional_context)
            
            # Integrate multi-layered context
            await self._integrate_user_profile_context(context)
            await self._integrate_conversation_history_context(context)
            await self._integrate_business_context(context)
            await self._integrate_temporal_context(context)
            await self._integrate_emotional_context(context, current_input)
            await self._integrate_intent_context(context, current_input)
            
            # Calculate context priorities and weights
            await self._calculate_context_priorities(context)
            await self._calculate_context_weights(context)
            
            # Store updated context
            await self._store_context(context)
            
            # Track metrics
            await self.metrics.track_context_integration(context.context_id, len(context.active_contexts))
            
            return context
            
        except Exception as e:
            self.logger.error(f"Context integration failed: {str(e)}")
            raise ContextError(f"Failed to integrate conversation context: {str(e)}")
    
    async def _get_or_create_context(
        self,
        user_id: str,
        session_id: str,
        conversation_id: str
    ) -> ConversationContext:
        """Get existing context or create new one"""        
        # Try to get from cache first
        cache_key = f"context:{conversation_id}"
        cached_context = await self.cache.get(cache_key)
        
        if cached_context:
            context = ConversationContext.parse_obj(cached_context)
            context.last_interaction = datetime.utcnow()
            return context
        
        # Try to get from database
        stored_context = await self._load_context_from_db(conversation_id)
        if stored_context:
            return stored_context
        
        # Create new context
        context = ConversationContext(
            user_id=user_id,
            session_id=session_id,
            conversation_id=conversation_id,
            active_contexts=[ContextType.USER_PROFILE, ContextType.CONVERSATION_HISTORY]
        )
        
        return context
    
    async def _update_current_interaction(
        self,
        context: ConversationContext,
        current_input: str,
        additional_context: Optional[Dict[str, Any]]
    ):
        """Update context with current interaction data"""        
        # Add to conversation history
        interaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_input": current_input,
            "input_length": len(current_input),
            "interaction_type": "user_message"
        }
        
        if additional_context:
            interaction.update(additional_context)
        
        context.conversation_history.append(interaction)
        
        # Limit history size (keep last 50 interactions)
        if len(context.conversation_history) > 50:
            context.conversation_history = context.conversation_history[-50:]
        
        # Update temporal data
        context.last_interaction = datetime.utcnow()
        context.session_duration = (context.last_interaction - context.conversation_start).total_seconds()
        
        # Calculate interaction frequency
        if len(context.conversation_history) > 1:
            time_diffs = []
            for i in range(1, len(context.conversation_history)):
                prev_time = datetime.fromisoformat(context.conversation_history[i-1]["timestamp"])
                curr_time = datetime.fromisoformat(context.conversation_history[i]["timestamp"])
                time_diffs.append((curr_time - prev_time).total_seconds())
            
            context.interaction_frequency = sum(time_diffs) / len(time_diffs) if time_diffs else 0
    
    async def _integrate_user_profile_context(self, context: ConversationContext):
        """Integrate user profile context"""        try:
            # Load user profile from database
            user_profile = await self._load_user_profile(context.user_id)
            
            if user_profile:
                context.user_profile = user_profile
                
                # Extract relevant business context
                context.business_objectives = user_profile.get("business_objectives", [])
                context.monetization_focus = user_profile.get("monetization_focus")
                context.protection_concerns = user_profile.get("protection_concerns", [])
                context.collaboration_interests = user_profile.get("collaboration_interests", [])
                
                # Extract content preferences
                context.content_type = user_profile.get("primary_content_type")
                context.platform_preferences = user_profile.get("platform_preferences", [])
                context.quality_standards = user_profile.get("quality_standards", {})
                
                # Add to active contexts
                if ContextType.USER_PROFILE not in context.active_contexts:
                    context.active_contexts.append(ContextType.USER_PROFILE)
        
        except Exception as e:
            self.logger.warning(f"Failed to integrate user profile context: {str(e)}")
    
    async def _integrate_conversation_history_context(self, context: ConversationContext):
        """Integrate conversation history context for pattern recognition"""        try:
            if len(context.conversation_history) < 2:
                return
            
            # Analyze conversation patterns
            conversation_analysis = await self._analyze_conversation_patterns(context.conversation_history)
            
            # Update context based on patterns
            context.current_priorities.update(conversation_analysis.get("topic_priorities", {}))
            
            # Detect recurring themes
            recurring_themes = conversation_analysis.get("recurring_themes", [])
            if recurring_themes:
                context.business_objectives.extend(recurring_themes)
                context.business_objectives = list(set(context.business_objectives))  # Remove duplicates
            
            # Update emotional progression
            emotional_progression = conversation_analysis.get("emotional_progression", [])
            if emotional_progression:
                context.emotional_state = emotional_progression[-1]  # Latest emotional state
            
            # Add to active contexts
            if ContextType.CONVERSATION_HISTORY not in context.active_contexts:
                context.active_contexts.append(ContextType.CONVERSATION_HISTORY)
        
        except Exception as e:
            self.logger.warning(f"Failed to integrate conversation history context: {str(e)}")
    
    async def _integrate_business_context(self, context: ConversationContext):
        """Integrate business logic context"""        try:
            # Determine current workflow stage
            workflow_stage = await self._determine_workflow_stage(context)
            context.current_workflow_stage = workflow_stage
            
            # Map workflow stage to business priorities
            workflow_priorities = {
                "onboarding": {"help": 0.9, "guidance": 0.8, "welcome": 0.7},
                "content_creation": {"creation": 0.9, "optimization": 0.8, "guidance": 0.7},
                "protection_setup": {"protection": 0.9, "security": 0.8, "guidance": 0.6},
                "monetization_planning": {"monetization": 0.9, "revenue": 0.8, "strategy": 0.7},
                "collaboration_seeking": {"collaboration": 0.9, "networking": 0.8, "partnerships": 0.7},
                "performance_analysis": {"analytics": 0.9, "optimization": 0.8, "insights": 0.7}
            }
            
            stage_priorities = workflow_priorities.get(workflow_stage, {})
            context.current_priorities.update(stage_priorities)
            
            # Add business context type
            if ContextType.BUSINESS_CONTEXT not in context.active_contexts:
                context.active_contexts.append(ContextType.BUSINESS_CONTEXT)
        
        except Exception as e:
            self.logger.warning(f"Failed to integrate business context: {str(e)}")
    
    async def _integrate_temporal_context(self, context: ConversationContext):
        """Integrate temporal context for time-aware responses"""        try:
            current_time = datetime.utcnow()
            
            # Time-based context factors
            temporal_factors = {
                "time_of_day": self._get_time_of_day_context(current_time),
                "day_of_week": self._get_day_of_week_context(current_time),
                "session_length": self._get_session_length_context(context.session_duration),
                "conversation_pace": self._get_conversation_pace_context(context.interaction_frequency)
            }
            
            # Update priorities based on temporal factors
            if temporal_factors["session_length"] == "long":
                context.current_priorities["summary"] = 0.7
                context.current_priorities["conclusion"] = 0.6
            
            if temporal_factors["conversation_pace"] == "fast":
                context.current_priorities["concise"] = 0.8
                context.current_priorities["direct"] = 0.7
            
            # Store temporal metadata
            context.content_metadata.update(temporal_factors)
            
            # Add temporal context type
            if ContextType.TEMPORAL_CONTEXT not in context.active_contexts:
                context.active_contexts.append(ContextType.TEMPORAL_CONTEXT)
        
        except Exception as e:
            self.logger.warning(f"Failed to integrate temporal context: {str(e)}")
    
    async def _integrate_emotional_context(self, context: ConversationContext, current_input: str):
        """Integrate emotional context analysis"""        try:
            # Analyze emotional state from current input
            emotional_analysis = await self._analyze_emotional_state(current_input)
            
            context.emotional_state = emotional_analysis.get("primary_emotion", "neutral")
            emotional_intensity = emotional_analysis.get("intensity", 0.5)
            
            # Adjust priorities based on emotional state
            emotion_priorities = {
                "frustrated": {"help": 0.9, "clarification": 0.8, "patience": 0.7},
                "excited": {"enthusiasm": 0.8, "encouragement": 0.7, "celebration": 0.6},
                "confused": {"clarification": 0.9, "guidance": 0.8, "explanation": 0.7},
                "satisfied": {"confirmation": 0.7, "next_steps": 0.6, "expansion": 0.5},
                "concerned": {"reassurance": 0.8, "guidance": 0.7, "support": 0.6}
            }
            
            emotion_specific_priorities = emotion_priorities.get(context.emotional_state, {})
            
            # Apply intensity weighting
            for priority, value in emotion_specific_priorities.items():
                context.current_priorities[priority] = value * emotional_intensity
            
            # Add emotional context type
            if ContextType.EMOTIONAL_CONTEXT not in context.active_contexts:
                context.active_contexts.append(ContextType.EMOTIONAL_CONTEXT)
        
        except Exception as e:
            self.logger.warning(f"Failed to integrate emotional context: {str(e)}")
    
    async def _integrate_intent_context(self, context: ConversationContext, current_input: str):
        """Integrate intent recognition context"""        try:
            # Detect current intent
            intent_analysis = await self._detect_user_intent(current_input, context)
            
            context.current_intent = intent_analysis.get("primary_intent")
            intent_confidence = intent_analysis.get("confidence", 0.5)
            
            # Map intents to priorities
            intent_priorities = {
                "help_request": {"help": 0.9, "guidance": 0.8},
                "information_seeking": {"information": 0.9, "explanation": 0.8},
                "problem_solving": {"solution": 0.9, "troubleshooting": 0.8},
                "feature_inquiry": {"features": 0.9, "capabilities": 0.8},
                "monetization_inquiry": {"monetization": 0.9, "revenue": 0.8},
                "protection_concern": {"protection": 0.9, "security": 0.8},
                "collaboration_interest": {"collaboration": 0.9, "networking": 0.7},
                "feedback_provision": {"acknowledgment": 0.8, "response": 0.7}
            }
            
            intent_specific_priorities = intent_priorities.get(context.current_intent, {})
            
            # Apply confidence weighting
            for priority, value in intent_specific_priorities.items():
                context.current_priorities[priority] = value * intent_confidence
            
            # Add intent context type
            if ContextType.INTENT_CONTEXT not in context.active_contexts:
                context.active_contexts.append(ContextType.INTENT_CONTEXT)
        
        except Exception as e:
            self.logger.warning(f"Failed to integrate intent context: {str(e)}")
    
    async def _calculate_context_priorities(self, context: ConversationContext):
        """Calculate dynamic context priorities"""        try:
            # Normalize priorities to sum to 1.0
            total_priority = sum(context.current_priorities.values())
            
            if total_priority > 0:
                for key in context.current_priorities:
                    context.current_priorities[key] = context.current_priorities[key] / total_priority
            
            # Ensure minimum priorities for core functions
            core_priorities = {
                "help": 0.1,
                "guidance": 0.1,
                "response_quality": 0.1
            }
            
            for core_key, min_value in core_priorities.items():
                if context.current_priorities.get(core_key, 0) < min_value:
                    context.current_priorities[core_key] = min_value
            
            # Re-normalize after adding core priorities
            total_priority = sum(context.current_priorities.values())
            if total_priority > 1.0:
                for key in context.current_priorities:
                    context.current_priorities[key] = context.current_priorities[key] / total_priority
        
        except Exception as e:
            self.logger.warning(f"Failed to calculate context priorities: {str(e)}")
    
    async def _calculate_context_weights(self, context: ConversationContext):
        """Calculate context type weights for response generation"""        try:
            base_weights = {
                ContextType.USER_PROFILE: 0.25,
                ContextType.CONVERSATION_HISTORY: 0.20,
                ContextType.BUSINESS_CONTEXT: 0.20,
                ContextType.INTENT_CONTEXT: 0.15,
                ContextType.EMOTIONAL_CONTEXT: 0.10,
                ContextType.TEMPORAL_CONTEXT: 0.05,
                ContextType.PLATFORM_CONTEXT: 0.05
            }
            
            # Adjust weights based on active contexts
            active_weight_sum = sum(
                base_weights.get(ctx_type, 0) 
                for ctx_type in context.active_contexts
            )
            
            if active_weight_sum > 0:
                for ctx_type in context.active_contexts:
                    weight = base_weights.get(ctx_type, 0) / active_weight_sum
                    context.context_weights[ctx_type.value] = weight
            
            # Boost weights based on conversation stage
            if context.current_workflow_stage == "onboarding":
                context.context_weights["user_profile"] = context.context_weights.get("user_profile", 0) * 1.5
            elif context.current_workflow_stage == "monetization_planning":
                context.context_weights["business_context"] = context.context_weights.get("business_context", 0) * 1.3
            
            # Emotional state weight adjustment
            if context.emotional_state in ["frustrated", "confused", "concerned"]:
                context.context_weights["emotional_context"] = context.context_weights.get("emotional_context", 0) * 2.0
        
        except Exception as e:
            self.logger.warning(f"Failed to calculate context weights: {str(e)}")
    
    async def _analyze_conversation_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation history for patterns"""        try:
            if len(history) < 2:
                return {}
            
            # Extract text content
            texts = [item.get("user_input", "") for item in history if item.get("user_input")]
            
            if not texts:
                return {}
            
            # Topic analysis using TF-IDF
            try:
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                feature_names = self.vectorizer.get_feature_names_out()
                
                # Get most frequent topics
                topic_scores = tfidf_matrix.sum(axis=0).A1
                top_topic_indices = topic_scores.argsort()[-10:][::-1]
                top_topics = [feature_names[i] for i in top_topic_indices]
                
                # Map topics to business priorities
                topic_priorities = {}
                business_keywords = {
                    "monetization": ["money", "revenue", "income", "earn", "profit", "monetize"],
                    "protection": ["protect", "copyright", "secure", "safety", "rights", "theft"],
                    "collaboration": ["collaborate", "partner", "team", "together", "joint"],
                    "platform": ["spotify", "youtube", "instagram", "platform", "social"],
                    "content": ["content", "create", "video", "audio", "music", "photo"]
                }
                
                for business_area, keywords in business_keywords.items():
                    score = sum(1 for topic in top_topics if any(keyword in topic for keyword in keywords))
                    if score > 0:
                        topic_priorities[business_area] = score / len(top_topics)
                
                return {
                    "topic_priorities": topic_priorities,
                    "recurring_themes": top_topics[:5],
                    "conversation_focus": max(topic_priorities.items(), key=lambda x: x[1])[0] if topic_priorities else "general"
                }
            
            except Exception as vectorizer_error:
                self.logger.warning(f"TF-IDF analysis failed: {str(vectorizer_error)}")
                return {"analysis_method": "fallback", "topic_priorities": {"general": 1.0}}
        
        except Exception as e:
            self.logger.warning(f"Conversation pattern analysis failed: {str(e)}")
            return {}
    
    async def _determine_workflow_stage(self, context: ConversationContext) -> str:
        """Determine current workflow stage based on context"""        try:
            # Analyze user profile completeness
            profile_completeness = len(context.user_profile) / 10.0  # Assume 10 key fields
            
            # Analyze conversation history for stage indicators
            history_text = " ".join([
                item.get("user_input", "") 
                for item in context.conversation_history[-10:]  # Last 10 interactions
            ]).lower()
            
            stage_indicators = {
                "onboarding": ["welcome", "start", "begin", "new", "setup", "first time"],
                "content_creation": ["create", "upload", "content", "make", "produce", "record"],
                "protection_setup": ["protect", "copyright", "secure", "fingerprint", "rights"],
                "monetization_planning": ["money", "revenue", "monetize", "earn", "income", "profit"],
                "collaboration_seeking": ["collaborate", "partner", "team", "work together", "join"],
                "performance_analysis": ["analytics", "performance", "metrics", "data", "results", "stats"]
            }
            
            stage_scores = {}
            for stage, indicators in stage_indicators.items():
                score = sum(1 for indicator in indicators if indicator in history_text)
                if score > 0:
                    stage_scores[stage] = score
            
            # Combine with profile-based stage detection
            if profile_completeness < 0.3:
                stage_scores["onboarding"] = stage_scores.get("onboarding", 0) + 5
            
            # Return stage with highest score
            if stage_scores:
                return max(stage_scores.items(), key=lambda x: x[1])[0]
            else:
                return "content_creation"  # Default stage
        
        except Exception as e:
            self.logger.warning(f"Workflow stage determination failed: {str(e)}")
            return "content_creation"
    
    def _get_time_of_day_context(self, current_time: datetime) -> str:
        """Get time of day context"""        hour = current_time.hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _get_day_of_week_context(self, current_time: datetime) -> str:
        """Get day of week context"""        weekday = current_time.weekday()
        
        if weekday < 5:
            return "weekday"
        else:
            return "weekend"
    
    def _get_session_length_context(self, session_duration: Optional[float]) -> str:
        """Get session length context"""        if not session_duration:
            return "new"
        
        if session_duration < 300:  # 5 minutes
            return "short"
        elif session_duration < 1800:  # 30 minutes
            return "medium"
        else:
            return "long"
    
    def _get_conversation_pace_context(self, interaction_frequency: Optional[float]) -> str:
        """Get conversation pace context"""        if not interaction_frequency:
            return "unknown"
        
        if interaction_frequency < 30:  # Less than 30 seconds between messages
            return "fast"
        elif interaction_frequency < 120:  # Less than 2 minutes
            return "moderate"
        else:
            return "slow"
    
    async def _analyze_emotional_state(self, text: str) -> Dict[str, Any]:
        """Analyze emotional state from text (simplified implementation)"""        try:
            text_lower = text.lower()
            
            # Simple emotion detection based on keywords
            emotion_keywords = {
                "frustrated": ["frustrated", "annoying", "difficult", "hard", "stuck", "problem", "issue"],
                "excited": ["excited", "great", "awesome", "amazing", "fantastic", "love", "excellent"],
                "confused": ["confused", "unclear", "don't understand", "what", "how", "help"],
                "satisfied": ["good", "thanks", "perfect", "satisfied", "happy", "pleased"],
                "concerned": ["worried", "concerned", "problem", "issue", "trouble", "security"]
            }
            
            emotion_scores = {}
            for emotion, keywords in emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    emotion_scores[emotion] = score / len(keywords)
            
            if emotion_scores:
                primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
                return {
                    "primary_emotion": primary_emotion[0],
                    "intensity": min(primary_emotion[1], 1.0),
                    "all_emotions": emotion_scores
                }
            else:
                return {"primary_emotion": "neutral", "intensity": 0.5}
        
        except Exception as e:
            self.logger.warning(f"Emotional analysis failed: {str(e)}")
            return {"primary_emotion": "neutral", "intensity": 0.5}
    
    async def _detect_user_intent(self, text: str, context: ConversationContext) -> Dict[str, Any]:
        """Detect user intent from text and context"""        try:
            text_lower = text.lower()
            
            # Intent detection patterns
            intent_patterns = {
                "help_request": ["help", "assist", "guide", "support", "how do", "can you"],
                "information_seeking": ["what", "explain", "tell me", "information", "details", "about"],
                "problem_solving": ["problem", "issue", "trouble", "not working", "error", "fix"],
                "feature_inquiry": ["feature", "function", "capability", "can it", "does it", "available"],
                "monetization_inquiry": ["money", "revenue", "monetize", "earn", "income", "profit", "pay"],
                "protection_concern": ["protect", "copyright", "secure", "safety", "theft", "unauthorized"],
                "collaboration_interest": ["collaborate", "partner", "team", "work with", "join", "together"],
                "feedback_provision": ["good", "bad", "feedback", "suggestion", "improvement", "better"]
            }
            
            intent_scores = {}
            for intent, patterns in intent_patterns.items():
                score = sum(1 for pattern in patterns if pattern in text_lower)
                if score > 0:
                    intent_scores[intent] = score / len(patterns)
            
            # Context-based intent boosting
            if context.current_workflow_stage == "monetization_planning":
                intent_scores["monetization_inquiry"] = intent_scores.get("monetization_inquiry", 0) + 0.3
            elif context.current_workflow_stage == "protection_setup":
                intent_scores["protection_concern"] = intent_scores.get("protection_concern", 0) + 0.3
            
            if intent_scores:
                primary_intent = max(intent_scores.items(), key=lambda x: x[1])
                return {
                    "primary_intent": primary_intent[0],
                    "confidence": min(primary_intent[1], 1.0),
                    "all_intents": intent_scores
                }
            else:
                return {"primary_intent": "help_request", "confidence": 0.5}
        
        except Exception as e:
            self.logger.warning(f"Intent detection failed: {str(e)}")
            return {"primary_intent": "help_request", "confidence": 0.5}
    
    async def _load_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user profile from database"""        try:
            # Placeholder implementation - would fetch from actual database
            # For now, return a mock profile
            return {
                "user_type": "musician",
                "primary_content_type": "audio",
                "platform_preferences": ["spotify", "youtube", "soundcloud"],
                "business_objectives": ["monetization", "protection", "growth"],
                "monetization_focus": "streaming_revenue",
                "protection_concerns": ["unauthorized_usage", "copyright_infringement"],
                "collaboration_interests": ["cross_genre", "remixes", "features"],
                "quality_standards": {"audio_quality": "high", "metadata_completeness": "full"},
                "experience_level": "intermediate",
                "monthly_uploads": 3,
                "preferred_communication_style": "professional"
            }
        except Exception as e:
            self.logger.warning(f"Failed to load user profile: {str(e)}")
            return None
    
    async def _load_context_from_db(self, conversation_id: str) -> Optional[ConversationContext]:
        """Load context from database"""        try:
            # Placeholder implementation - would fetch from actual database
            return None
        except Exception as e:
            self.logger.warning(f"Failed to load context from database: {str(e)}")
            return None
    
    async def _store_context(self, context: ConversationContext):
        """Store context to cache and database"""        try:
            # Update timestamp
            context.last_updated = datetime.utcnow()
            
            # Store in cache
            cache_key = f"context:{context.conversation_id}"
            await self.cache.set(cache_key, context.dict(), expire=3600)  # 1 hour
            
            # Store in database (async)
            # await self.db.store_context(context)
            
        except Exception as e:
            self.logger.warning(f"Failed to store context: {str(e)}")


class ContextAwareResponseEngine:
    """Context-aware response generation engine"""    
    def __init__(self, context_integrator: ConversationContextIntegrator):
        self.context_integrator = context_integrator
        self.logger = logging.getLogger(__name__)
        self.cache = CacheManager()
        self.metrics = MetricsCollector()
    
    async def generate_context_aware_response(
        self,
        user_input: str,
        user_id: str,
        session_id: str,
        conversation_id: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Generate response with full context awareness
        
        Args:
            user_input: User's input text
            user_id: User identifier
            session_id: Session identifier
            conversation_id: Conversation identifier
            additional_context: Additional context data
            
        Returns:
            Context-aware response with metadata
        """        try:
            # Integrate conversation context
            context = await self.context_integrator.integrate_conversation_context(
                user_id, session_id, conversation_id, user_input, additional_context
            )
            
            # Generate context-aware response data
            response_data = {
                "context_summary": self._generate_context_summary(context),
                "response_guidance": self._generate_response_guidance(context),
                "personalization_hints": self._generate_personalization_hints(context),
                "business_priorities": context.current_priorities,
                "context_weights": context.context_weights,
                "emotional_tone": self._determine_response_tone(context),
                "suggested_length": self._determine_response_length(context),
                "follow_up_suggestions": await self._generate_follow_up_suggestions(context),
                "context_metadata": {
                    "active_contexts": [ctx.value for ctx in context.active_contexts],
                    "workflow_stage": context.current_workflow_stage,
                    "emotional_state": context.emotional_state,
                    "current_intent": context.current_intent,
                    "session_duration": context.session_duration,
                    "interaction_count": len(context.conversation_history)
                }
            }
            
            # Track context usage metrics
            await self.metrics.track_context_usage(context.context_id, response_data)
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Context-aware response generation failed: {str(e)}")
            return {"error": str(e), "fallback": True}
    
    def _generate_context_summary(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate comprehensive context summary"""        return {
            "user_profile_summary": {
                "user_type": context.user_profile.get("user_type", "content_creator"),
                "experience_level": context.user_profile.get("experience_level", "intermediate"),
                "primary_focus": context.monetization_focus or "content_creation"
            },
            "conversation_summary": {
                "total_interactions": len(context.conversation_history),
                "session_duration_minutes": round((context.session_duration or 0) / 60, 1),
                "primary_topics": list(context.current_priorities.keys())[:3],
                "conversation_pace": self._get_conversation_pace_context(context.interaction_frequency)
            },
            "business_summary": {
                "current_stage": context.current_workflow_stage,
                "objectives": context.business_objectives[:3],
                "top_priority": max(context.current_priorities.items(), key=lambda x: x[1])[0] if context.current_priorities else "general"
            }
        }
    
    def _generate_response_guidance(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate response guidance based on context"""        guidance = {
            "primary_focus": max(context.current_priorities.items(), key=lambda x: x[1])[0] if context.current_priorities else "help",
            "tone_guidance": self._determine_response_tone(context),
            "length_guidance": self._determine_response_length(context),
            "structure_guidance": self._determine_response_structure(context),
            "content_guidance": self._determine_content_guidance(context)
        }
        
        return guidance
    
    def _generate_personalization_hints(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate personalization hints for response customization"""        hints = {
            "user_preferences": {
                "communication_style": context.user_profile.get("preferred_communication_style", "professional"),
                "detail_level": context.user_profile.get("detail_preference", "medium"),
                "example_preference": context.user_profile.get("example_preference", "practical")
            },
            "context_specific": {
                "mention_user_type": True,
                "reference_content_type": bool(context.content_type),
                "include_platform_specific": bool(context.platform_preferences),
                "address_business_goals": bool(context.business_objectives)
            },
            "emotional_adaptation": {
                "current_emotion": context.emotional_state,
                "supportive_tone": context.emotional_state in ["frustrated", "confused", "concerned"],
                "encouraging_tone": context.emotional_state in ["excited", "motivated"],
                "professional_tone": context.emotional_state in ["neutral", "satisfied"]
            }
        }
        
        return hints
    
    def _determine_response_tone(self, context: ConversationContext) -> str:
        """Determine appropriate response tone"""        emotional_state = context.emotional_state
        user_style = context.user_profile.get("preferred_communication_style", "professional")
        
        # Emotional state takes priority
        if emotional_state == "frustrated":
            return "patient_supportive"
        elif emotional_state == "excited":
            return "enthusiastic_encouraging"
        elif emotional_state == "confused":
            return "clear_explanatory"
        elif emotional_state == "concerned":
            return "reassuring_professional"
        
        # Fall back to user preference
        if user_style == "casual":
            return "friendly_casual"
        elif user_style == "formal":
            return "professional_formal"
        else:
            return "professional_friendly"
    
    def _determine_response_length(self, context: ConversationContext) -> str:
        """Determine appropriate response length"""        factors = {
            "session_length": self._get_session_length_context(context.session_duration),
            "conversation_pace": self._get_conversation_pace_context(context.interaction_frequency),
            "complexity": context.user_profile.get("detail_preference", "medium"),
            "intent": context.current_intent
        }
        
        # Fast-paced conversations need shorter responses
        if factors["conversation_pace"] == "fast":
            return "concise"
        
        # Long sessions might benefit from summaries
        if factors["session_length"] == "long":
            return "comprehensive"
        
        # Intent-based length decisions
        if factors["intent"] in ["help_request", "problem_solving"]:
            return "detailed"
        elif factors["intent"] in ["confirmation", "feedback_provision"]:
            return "brief"
        
        # Default to medium
        return "medium"
    
    def _determine_response_structure(self, context: ConversationContext) -> str:
        """Determine appropriate response structure"""        if context.current_intent == "help_request":
            return "step_by_step"
        elif context.current_intent == "information_seeking":
            return "explanatory"
        elif context.current_workflow_stage == "onboarding":
            return "welcome_guided"
        elif context.emotional_state == "confused":
            return "clarifying"
        else:
            return "conversational"
    
    def _determine_content_guidance(self, context: ConversationContext) -> Dict[str, Any]:
        """Determine content guidance for response"""        guidance = {
            "include_examples": context.user_profile.get("example_preference", "practical") == "practical",
            "technical_depth": context.user_profile.get("experience_level", "intermediate"),
            "business_context": context.current_workflow_stage,
            "platform_mentions": context.platform_preferences[:2] if context.platform_preferences else [],
            "content_type_focus": context.content_type
        }
        
        return guidance
    
    async def _generate_follow_up_suggestions(self, context: ConversationContext) -> List[str]:
        """Generate contextual follow-up suggestions"""        suggestions = []
        
        # Stage-based suggestions
        stage_suggestions = {
            "onboarding": [
                "Would you like me to help you set up your content protection?",
                "Shall we explore monetization strategies for your content type?",
                "Would you like guidance on platform optimization?"
            ],
            "content_creation": [
                "Would you like tips for optimizing your content quality?",
                "Shall we discuss distribution strategies?",
                "Would you like to explore collaboration opportunities?"
            ],
            "monetization_planning": [
                "Would you like to set up revenue tracking?",
                "Shall we explore additional monetization channels?",
                "Would you like help with pricing strategies?"
            ],
            "protection_setup": [
                "Would you like to enable automated monitoring?",
                "Shall we set up copyright protection?",
                "Would you like guidance on content licensing?"
            ]
        }
        
        stage = context.current_workflow_stage
        if stage in stage_suggestions:
            suggestions.extend(stage_suggestions[stage])
        
        # Intent-based suggestions
        if context.current_intent == "information_seeking":
            suggestions.append("Would you like more detailed information on any specific aspect?")
        elif context.current_intent == "problem_solving":
            suggestions.append("Would you like me to help you implement this solution?")
        
        # Limit to top 3 suggestions
        return suggestions[:3]
    
    def _get_conversation_pace_context(self, interaction_frequency: Optional[float]) -> str:
        """Get conversation pace context (reused from integrator)"""        if not interaction_frequency:
            return "unknown"
        
        if interaction_frequency < 30:
            return "fast"
        elif interaction_frequency < 120:
            return "moderate"
        else:
            return "slow"
    
    def _get_session_length_context(self, session_duration: Optional[float]) -> str:
        """Get session length context (reused from integrator)"""        if not session_duration:
            return "new"
        
        if session_duration < 300:
            return "short"
        elif session_duration < 1800:
            return "medium"
        else:
            return "long"


class ResponseContextManager:
    """High-level context management for response generation"""    
    def __init__(self):
        self.context_integrator = ConversationContextIntegrator()
        self.context_engine = ContextAwareResponseEngine(self.context_integrator)
        self.logger = logging.getLogger(__name__)
    
    async def get_response_context(
        self,
        user_input: str,
        user_id: str,
        session_id: str,
        conversation_id: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive response context for generation"""        return await self.context_engine.generate_context_aware_response(
            user_input, user_id, session_id, conversation_id, additional_context
        )
    
    async def update_context_feedback(
        self,
        conversation_id: str,
        response_effectiveness: float,
        user_satisfaction: Optional[float] = None
    ):
        """Update context with response feedback"""        try:
            # Load current context
            cache_key = f"context:{conversation_id}"
            cached_context = await self.context_integrator.cache.get(cache_key)
            
            if cached_context:
                context = ConversationContext.parse_obj(cached_context)
                
                # Update effectiveness metrics
                context.response_effectiveness["latest"] = response_effectiveness
                if user_satisfaction:
                    context.user_satisfaction = user_satisfaction
                
                # Store updated context
                await self.context_integrator._store_context(context)
                
        except Exception as e:
            self.logger.warning(f"Failed to update context feedback: {str(e)}")


class ContextualIntelligence:
    """Advanced contextual intelligence for response optimization"""    
    def __init__(self):
        self.context_manager = ResponseContextManager()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()
    
    async def analyze_context_patterns(
        self,
        user_id: str,
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze user context patterns over time"""        try:
            # This would analyze patterns from stored contexts
            # Placeholder implementation
            analysis = {
                "conversation_patterns": {
                    "average_session_length": 15.5,
                    "common_topics": ["monetization", "protection", "collaboration"],
                    "peak_activity_hours": [10, 14, 20],
                    "emotional_trends": {"neutral": 0.6, "excited": 0.3, "confused": 0.1}
                },
                "workflow_progression": {
                    "current_stage": "monetization_planning", 
                    "completed_stages": ["onboarding", "content_creation"],
                    "next_recommended_stage": "collaboration_seeking"
                },
                "optimization_opportunities": [
                    "Increase response personalization",
                    "Focus on monetization strategies",
                    "Improve technical guidance clarity"
                ]
            }
            
            await self.metrics.track_context_analysis(user_id, analysis)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Context pattern analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_context_weights(
        self,
        conversation_id: str,
        performance_feedback: Dict[str, float]
    ) -> Dict[str, float]:
        """Optimize context weights based on performance feedback"""        try:
            # Load current context
            cache_key = f"context:{conversation_id}"
            cached_context = await self.context_manager.context_integrator.cache.get(cache_key)
            
            if not cached_context:
                return {}
            
            context = ConversationContext.parse_obj(cached_context)
            current_weights = context.context_weights
            
            # Optimize weights based on feedback
            optimized_weights = {}
            for context_type, weight in current_weights.items():
                feedback_score = performance_feedback.get(context_type, 0.5)
                
                # Adjust weight based on performance
                if feedback_score > 0.7:
                    optimized_weights[context_type] = min(weight * 1.1, 1.0)
                elif feedback_score < 0.3:
                    optimized_weights[context_type] = max(weight * 0.9, 0.1)
                else:
                    optimized_weights[context_type] = weight
            
            # Normalize weights
            total_weight = sum(optimized_weights.values())
            if total_weight > 0:
                optimized_weights = {
                    k: v / total_weight 
                    for k, v in optimized_weights.items()
                }
            
            return optimized_weights
            
        except Exception as e:
            self.logger.error(f"Context weight optimization failed: {str(e)}")
            return {}


# Export main classes
__all__ = [
    "ConversationContextIntegrator",
    "ContextualResponseGenerator", 
    "ContextAwareResponseEngine",
    "ResponseContextManager",
    "ContextualIntelligence",
    "ConversationContext",
    "ContextualMemory",
    "ContextType",
    "ContextPriority",
    "ContextScope"
]
