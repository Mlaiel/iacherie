"""
Service Companion IA - Virtual AI Companion
==========================================

Enterprise-grade virtual AI companion service providing personalized, 
natural conversation with long-term memory capabilities for content creators.

Features:
- Virtual Friend Interface (Ami virtuel)
- Natural Conversation Processing (Conversation naturelle) 
- Long-term Memory System (Mémoire à long terme)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger(__name__)


class CompanionPersonalityType(Enum):
    """Types of companion personalities"""
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    SUPPORTIVE = "supportive"
    MENTOR = "mentor"


class ConversationContext(Enum):
    """Context types for conversations"""
    CASUAL = "casual"
    BUSINESS = "business"
    CREATIVE_SESSION = "creative_session"
    PROBLEM_SOLVING = "problem_solving"
    EMOTIONAL_SUPPORT = "emotional_support"


@dataclass
class CompanionMemory:
    """Long-term memory structure for the companion"""
    user_id: str
    memories: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    personality_insights: Dict[str, Any] = field(default_factory=dict)
    important_dates: Dict[str, datetime] = field(default_factory=dict)
    goals_and_aspirations: List[str] = field(default_factory=list)
    last_interaction: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConversationSession:
    """Individual conversation session"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    context: ConversationContext = ConversationContext.CASUAL
    start_time: datetime = field(default_factory=datetime.now)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    companion_mood: str = "neutral"
    active: bool = True


@dataclass
class CompanionResponse:
    """Response from the companion"""
    content: str
    emotion: str = "neutral"
    personality_type: CompanionPersonalityType = CompanionPersonalityType.FRIENDLY
    memory_referenced: bool = False
    suggestions: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ICompanionService(ABC):
    """Interface for companion service"""
    
    @abstractmethod
    async def start_conversation(self, user_id: str, context: ConversationContext = ConversationContext.CASUAL) -> ConversationSession:
        """Start a new conversation session"""
        pass
    
    @abstractmethod
    async def process_message(self, session_id: str, message: str) -> CompanionResponse:
        """Process user message and generate companion response"""
        pass
    
    @abstractmethod
    async def get_memory(self, user_id: str) -> CompanionMemory:
        """Retrieve user's memory profile"""
        pass
    
    @abstractmethod
    async def update_memory(self, user_id: str, memory_update: Dict[str, Any]) -> bool:
        """Update user's memory with new information"""
        pass


class MemoryManager:
    """Manages long-term memory for the companion"""
    
    def __init__(self):
        self._memories: Dict[str, CompanionMemory] = {}
        self.logger = logging.getLogger(__name__ + ".MemoryManager")
    
    async def get_memory(self, user_id: str) -> CompanionMemory:
        """Retrieve or create user memory"""
        if user_id not in self._memories:
            self._memories[user_id] = CompanionMemory(user_id=user_id)
            self.logger.info(f"Created new memory profile for user {user_id}")
        
        return self._memories[user_id]
    
    async def update_memory(self, user_id: str, conversation_data: Dict[str, Any]) -> bool:
        """Update memory with conversation insights"""
        try:
            memory = await self.get_memory(user_id)
            
            # Extract important information from conversation
            if "preferences" in conversation_data:
                memory.preferences.update(conversation_data["preferences"])
            
            if "important_info" in conversation_data:
                memory.memories.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "conversation_insight",
                    "data": conversation_data["important_info"]
                })
            
            if "goals" in conversation_data:
                memory.goals_and_aspirations.extend(conversation_data["goals"])
            
            memory.last_interaction = datetime.now()
            
            self.logger.info(f"Updated memory for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update memory for user {user_id}: {e}")
            return False
    
    async def add_conversation_to_history(self, user_id: str, session: ConversationSession) -> bool:
        """Add conversation session to memory history"""
        try:
            memory = await self.get_memory(user_id)
            
            # Summarize conversation for memory
            conversation_summary = {
                "session_id": session.session_id,
                "timestamp": session.start_time.isoformat(),
                "context": session.context.value,
                "message_count": len(session.messages),
                "duration_minutes": (datetime.now() - session.start_time).total_seconds() / 60,
                "key_topics": self._extract_key_topics(session.messages)
            }
            
            memory.conversation_history.append(conversation_summary)
            
            # Keep only last 100 conversations in history
            if len(memory.conversation_history) > 100:
                memory.conversation_history = memory.conversation_history[-100:]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add conversation to history for user {user_id}: {e}")
            return False
    
    def _extract_key_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract key topics from conversation messages"""
        # Simple keyword extraction - could be enhanced with NLP
        topics = []
        keywords = ["music", "video", "content", "creative", "business", "goal", "project"]
        
        for message in messages:
            content = message.get("content", "").lower()
            for keyword in keywords:
                if keyword in content and keyword not in topics:
                    topics.append(keyword)
        
        return topics[:5]  # Return max 5 topics


class ConversationProcessor:
    """Processes natural conversations with context awareness"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".ConversationProcessor")
        self._conversation_templates = self._load_conversation_templates()
    
    def _load_conversation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load conversation templates for different contexts"""
        return {
            ConversationContext.CASUAL.value: {
                "greetings": [
                    "Hey there! How's your day going?",
                    "Hi! Great to see you again!",
                    "Hello! What's on your mind today?"
                ],
                "responses": {
                    "positive": "That's wonderful to hear! ",
                    "negative": "I understand, that sounds challenging. ",
                    "neutral": "I see, thanks for sharing that with me. "
                }
            },
            ConversationContext.BUSINESS.value: {
                "greetings": [
                    "Hello! Ready to tackle some business goals today?",
                    "Hi there! How can I help with your projects?",
                    "Good to see you! What are we working on?"
                ],
                "responses": {
                    "positive": "Excellent! That's great progress. ",
                    "negative": "Let's work through this challenge together. ",
                    "neutral": "I understand. Let me help you with that. "
                }
            },
            ConversationContext.CREATIVE_SESSION.value: {
                "greetings": [
                    "Hey creative soul! Ready to brainstorm?",
                    "Hi! Let's unleash some creativity today!",
                    "Hello artist! What inspiring ideas do you have?"
                ],
                "responses": {
                    "positive": "I love that creative energy! ",
                    "negative": "Creative blocks happen. Let's find inspiration together. ",
                    "neutral": "Interesting concept. Let's explore that further. "
                }
            }
        }
    
    async def generate_response(self, message: str, context: ConversationContext, 
                              memory: CompanionMemory, personality: CompanionPersonalityType) -> CompanionResponse:
        """Generate contextual response to user message"""
        try:
            # Analyze message sentiment (simplified)
            sentiment = self._analyze_sentiment(message)
            
            # Get appropriate response template
            templates = self._conversation_templates.get(context.value, {})
            response_templates = templates.get("responses", {})
            
            # Build response based on sentiment and memory
            base_response = response_templates.get(sentiment, "I hear you. ")
            
            # Add personalized content based on memory
            personalized_content = self._add_personalization(message, memory)
            
            # Generate suggestions based on context
            suggestions = self._generate_suggestions(message, context, memory)
            
            # Generate follow-up questions
            follow_ups = self._generate_follow_ups(message, context)
            
            full_response = base_response + personalized_content
            
            return CompanionResponse(
                content=full_response,
                emotion=sentiment,
                personality_type=personality,
                memory_referenced=len(memory.memories) > 0,
                suggestions=suggestions,
                follow_up_questions=follow_ups,
                metadata={
                    "context": context.value,
                    "sentiment": sentiment,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return CompanionResponse(
                content="I'm here to listen. Could you tell me more about what's on your mind?",
                emotion="neutral"
            )
    
    def _analyze_sentiment(self, message: str) -> str:
        """Simple sentiment analysis"""
        message_lower = message.lower()
        
        positive_words = ["good", "great", "awesome", "happy", "excited", "love", "amazing"]
        negative_words = ["bad", "terrible", "sad", "angry", "frustrated", "hate", "awful"]
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _add_personalization(self, message: str, memory: CompanionMemory) -> str:
        """Add personalized content based on user memory"""
        if not memory.memories:
            return "Tell me more about yourself so I can better understand you. "
        
        # Reference relevant memories (simplified)
        recent_memories = memory.memories[-3:] if len(memory.memories) > 3 else memory.memories
        
        if memory.goals_and_aspirations:
            return f"I remember you mentioned your goal of {memory.goals_and_aspirations[-1]}. "
        
        return "Based on our previous conversations, "
    
    def _generate_suggestions(self, message: str, context: ConversationContext, memory: CompanionMemory) -> List[str]:
        """Generate contextual suggestions"""
        suggestions = []
        
        if context == ConversationContext.BUSINESS:
            suggestions = [
                "Create a strategic plan for this goal",
                "Break this down into smaller actionable steps",
                "Set specific deadlines for key milestones"
            ]
        elif context == ConversationContext.CREATIVE_SESSION:
            suggestions = [
                "Try a different creative approach",
                "Gather inspiration from other creators",
                "Experiment with new techniques or tools"
            ]
        else:
            suggestions = [
                "Tell me more about how you're feeling",
                "What would make this situation better?",
                "Is there something I can help you with?"
            ]
        
        return suggestions[:3]
    
    def _generate_follow_ups(self, message: str, context: ConversationContext) -> List[str]:
        """Generate follow-up questions"""
        if context == ConversationContext.BUSINESS:
            return [
                "What's your timeline for this?",
                "What resources do you have available?",
                "What's the biggest challenge you're facing?"
            ]
        elif context == ConversationContext.CREATIVE_SESSION:
            return [
                "What style are you going for?",
                "Who's your target audience?",
                "What inspires you most about this project?"
            ]
        else:
            return [
                "How are you feeling about this?",
                "What would you like to focus on?",
                "Is there anything else on your mind?"
            ]


class CompanionService(ICompanionService):
    """Main companion service implementation"""
    
    def __init__(self, personality: CompanionPersonalityType = CompanionPersonalityType.FRIENDLY):
        self.personality = personality
        self.memory_manager = MemoryManager()
        self.conversation_processor = ConversationProcessor()
        self._active_sessions: Dict[str, ConversationSession] = {}
        self.logger = logging.getLogger(__name__ + ".CompanionService")
        
        self.logger.info(f"CompanionService initialized with {personality.value} personality")
    
    async def start_conversation(self, user_id: str, context: ConversationContext = ConversationContext.CASUAL) -> ConversationSession:
        """Start a new conversation session"""
        try:
            session = ConversationSession(
                user_id=user_id,
                context=context
            )
            
            self._active_sessions[session.session_id] = session
            
            # Get user memory to personalize greeting
            memory = await self.memory_manager.get_memory(user_id)
            
            # Generate personalized greeting
            greeting = await self._generate_greeting(context, memory)
            
            # Add greeting to session
            session.messages.append({
                "role": "companion",
                "content": greeting.content,
                "timestamp": datetime.now().isoformat(),
                "emotion": greeting.emotion
            })
            
            self.logger.info(f"Started conversation session {session.session_id} for user {user_id}")
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to start conversation for user {user_id}: {e}")
            raise
    
    async def process_message(self, session_id: str, message: str) -> CompanionResponse:
        """Process user message and generate companion response"""
        try:
            if session_id not in self._active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self._active_sessions[session_id]
            
            # Add user message to session
            session.messages.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get user memory
            memory = await self.memory_manager.get_memory(session.user_id)
            
            # Generate response
            response = await self.conversation_processor.generate_response(
                message, session.context, memory, self.personality
            )
            
            # Add companion response to session
            session.messages.append({
                "role": "companion",
                "content": response.content,
                "timestamp": datetime.now().isoformat(),
                "emotion": response.emotion,
                "suggestions": response.suggestions,
                "follow_ups": response.follow_up_questions
            })
            
            # Extract and update memory insights
            await self._update_memory_from_conversation(session.user_id, message, response)
            
            self.logger.info(f"Processed message in session {session_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to process message in session {session_id}: {e}")
            return CompanionResponse(
                content="I'm having trouble processing that right now. Could you try rephrasing?",
                emotion="confused"
            )
    
    async def get_memory(self, user_id: str) -> CompanionMemory:
        """Retrieve user's memory profile"""
        return await self.memory_manager.get_memory(user_id)
    
    async def update_memory(self, user_id: str, memory_update: Dict[str, Any]) -> bool:
        """Update user's memory with new information"""
        return await self.memory_manager.update_memory(user_id, memory_update)
    
    async def end_conversation(self, session_id: str) -> bool:
        """End conversation session and update memory"""
        try:
            if session_id not in self._active_sessions:
                return False
            
            session = self._active_sessions[session_id]
            session.active = False
            
            # Add conversation to long-term memory
            await self.memory_manager.add_conversation_to_history(session.user_id, session)
            
            # Remove from active sessions
            del self._active_sessions[session_id]
            
            self.logger.info(f"Ended conversation session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to end conversation session {session_id}: {e}")
            return False
    
    async def _generate_greeting(self, context: ConversationContext, memory: CompanionMemory) -> CompanionResponse:
        """Generate personalized greeting based on context and memory"""
        greetings = self.conversation_processor._conversation_templates.get(
            context.value, {}
        ).get("greetings", ["Hello! How can I help you today?"])
        
        # Choose greeting based on memory
        if memory.last_interaction:
            time_since_last = datetime.now() - memory.last_interaction
            if time_since_last.days > 7:
                greeting = "Welcome back! It's been a while. How have you been?"
            elif time_since_last.days > 1:
                greeting = "Good to see you again! How are things going?"
            else:
                greeting = greetings[0] if greetings else "Hi there!"
        else:
            greeting = "Hello! I'm excited to get to know you. What brings you here today?"
        
        return CompanionResponse(
            content=greeting,
            emotion="friendly",
            personality_type=self.personality
        )
    
    async def _update_memory_from_conversation(self, user_id: str, user_message: str, response: CompanionResponse) -> None:
        """Extract insights from conversation and update memory"""
        try:
            # Simple keyword extraction for preferences and goals
            insights = {}
            
            # Extract potential goals
            if any(word in user_message.lower() for word in ["want to", "goal", "plan to", "hoping to"]):
                insights["goals"] = [user_message.strip()]
            
            # Extract preferences
            if any(word in user_message.lower() for word in ["like", "love", "prefer", "enjoy"]):
                insights["preferences"] = {"recent_preference": user_message.strip()}
            
            # Extract important information
            if any(word in user_message.lower() for word in ["important", "remember", "significant"]):
                insights["important_info"] = user_message.strip()
            
            if insights:
                await self.memory_manager.update_memory(user_id, insights)
            
        except Exception as e:
            self.logger.error(f"Failed to update memory from conversation: {e}")


# Factory function for creating companion service
async def create_companion_service(personality: CompanionPersonalityType = CompanionPersonalityType.FRIENDLY) -> CompanionService:
    """Create and initialize companion service"""
    service = CompanionService(personality)
    logger.info(f"Created companion service with {personality.value} personality")
    return service


# Convenience functions for different personality types
async def create_friendly_companion() -> CompanionService:
    """Create friendly companion"""
    return await create_companion_service(CompanionPersonalityType.FRIENDLY)


async def create_professional_companion() -> CompanionService:
    """Create professional companion"""
    return await create_companion_service(CompanionPersonalityType.PROFESSIONAL)


async def create_creative_companion() -> CompanionService:
    """Create creative companion"""
    return await create_companion_service(CompanionPersonalityType.CREATIVE)


async def create_mentor_companion() -> CompanionService:
    """Create mentor companion"""
    return await create_companion_service(CompanionPersonalityType.MENTOR)


# Main exports
__all__ = [
    "CompanionService",
    "ICompanionService", 
    "CompanionPersonalityType",
    "ConversationContext",
    "CompanionMemory",
    "ConversationSession",
    "CompanionResponse",
    "create_companion_service",
    "create_friendly_companion",
    "create_professional_companion",
    "create_creative_companion",
    "create_mentor_companion"
]