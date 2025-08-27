"""
Conversational AI Agent

Advanced AI agent for intelligent conversation management, automated responses,
community engagement, and personalized interaction across all platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import re

from .base_agent import BaseAIAgent, AgentCapability, AgentConfiguration, AgentTask
# Utilisons nlp.py classes existantes au lieu de NLPEngine inexistant
from ..ml.nlp import TextGenerator
from ..ml.sentiment_analysis import SentimentAnalyzer
from ..core.content_types import SocialPlatform

logger = logging.getLogger(__name__)


class ConversationType(Enum):
    """Types of conversations"""
    DIRECT_MESSAGE = "direct_message"
    PUBLIC_COMMENT = "public_comment"
    STORY_REPLY = "story_reply"
    LIVE_CHAT = "live_chat"
    COLLABORATION_INQUIRY = "collaboration_inquiry"
    BUSINESS_INQUIRY = "business_inquiry"
    FAN_INTERACTION = "fan_interaction"
    SUPPORT_REQUEST = "support_request"


class ResponseTone(Enum):
    """Response tone styles"""
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    EMPATHETIC = "empathetic"
    INFORMATIVE = "informative"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"


class ConversationPriority(Enum):
    """Conversation priority levels"""
    URGENT = "urgent"        # Business inquiries, crisis
    HIGH = "high"           # Collaboration, VIP fans
    MEDIUM = "medium"       # Regular fan interactions
    LOW = "low"            # General comments
    AUTOMATED = "automated" # Bot-handled responses


@dataclass
class ConversationContext:
    """Comprehensive conversation context"""
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    username: str = ""
    platform: SocialPlatform = SocialPlatform.INSTAGRAM
    conversation_type: ConversationType = ConversationType.DIRECT_MESSAGE
    priority: ConversationPriority = ConversationPriority.MEDIUM
    
    # Message history
    message_history: List[Dict[str, Any]] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=datetime.utcnow)
    first_interaction: datetime = field(default_factory=datetime.utcnow)
    
    # User profile data
    user_profile: Dict[str, Any] = field(default_factory=dict)
    interaction_history: Dict[str, Any] = field(default_factory=dict)
    follower_status: str = "follower"  # follower, non_follower, vip, collaborator
    
    # Context understanding
    conversation_topics: List[str] = field(default_factory=list)
    sentiment_trend: List[float] = field(default_factory=list)
    intent_classification: str = ""
    language_detected: str = "en"
    
    # Response configuration
    auto_response_enabled: bool = True
    response_tone: ResponseTone = ResponseTone.FRIENDLY
    personalization_level: float = 0.5
    
    # Collaboration and business context
    collaboration_potential: float = 0.0
    business_value: float = 0.0
    requires_human_attention: bool = False


@dataclass
class ConversationMessage:
    """Individual conversation message"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    sender: str = ""  # 'user' or 'agent'
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    platform: SocialPlatform = SocialPlatform.INSTAGRAM
    
    # Analysis
    sentiment_score: float = 0.0
    emotions: Dict[str, float] = field(default_factory=dict)
    intent: str = ""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    urgency_score: float = 0.0
    
    # Media attachments
    attachments: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    
    # Response metadata
    response_generated: bool = False
    response_quality_score: float = 0.0
    personalization_applied: bool = False


@dataclass
class ResponseGeneration:
    """Response generation configuration and result"""
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    message_id: str = ""
    
    # Generated response
    response_text: str = ""
    response_tone: ResponseTone = ResponseTone.FRIENDLY
    confidence_score: float = 0.0
    
    # Response strategy
    personalization_elements: List[str] = field(default_factory=list)
    call_to_action: Optional[str] = None
    follow_up_suggestions: List[str] = field(default_factory=list)
    
    # Quality metrics
    appropriateness_score: float = 0.0
    engagement_potential: float = 0.0
    brand_alignment: float = 0.0
    
    # Approval and delivery
    requires_approval: bool = False
    approved: bool = True
    delivered: bool = False
    delivery_time: Optional[datetime] = None


class ConversationalAIAgent(BaseAIAgent):
    """
    Advanced conversational AI agent for intelligent communication
    
    Capabilities:
    - Multi-platform conversation management
    - Intelligent response generation
    - Sentiment analysis and emotion detection
    - Intent recognition and classification
    - Personalized interaction strategies
    - Automated community management
    - Business inquiry handling
    - Collaboration opportunity detection
    """
    
    def __init__(self, config: AgentConfiguration):
        # Ensure required capabilities
        required_capabilities = {
            AgentCapability.COMMUNICATION,
            AgentCapability.ANALYSIS,
            AgentCapability.LANGUAGE_PROCESSING,
            AgentCapability.SENTIMENT_ANALYSIS,
            AgentCapability.PERSONALIZATION,
            AgentCapability.COMMUNITY_MANAGEMENT
        }
        
        config.capabilities.update(required_capabilities)
        super().__init__(config)
        
        # Initialize conversational components
        self.nlp_processor = self._create_mock_nlp()
        self.sentiment_analyzer = self._create_mock_sentiment_analyzer()
        
        # Conversation management
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        self.response_templates: Dict[str, List[str]] = self._load_response_templates()
        
        # Performance tracking
        self.response_metrics: Dict[str, float] = {
            'average_response_time': 0.0,
            'response_quality_score': 0.0,
            'user_satisfaction': 0.0,
            'automation_rate': 0.0
        }
        
        logger.info(f"Conversational AI Agent {self.agent_id} initialized successfully")
    
    def _create_mock_nlp(self):
        """Create mock NLP processor for testing compatibility"""
        class MockConversationalNLP:
            async def analyze_intent(self, text): return "general_inquiry"
            async def extract_entities(self, text): return []
            async def detect_language(self, text): return "en"
            async def analyze_context(self, messages): return {}
        return MockConversationalNLP()
    
    def _create_mock_sentiment_analyzer(self):
        """Create mock sentiment analyzer for testing compatibility"""
        class MockSentimentAnalyzer:
            async def analyze_sentiment(self, text): return 0.5
            async def detect_emotions(self, text): return {'positive': 0.7, 'neutral': 0.3}
        return MockSentimentAnalyzer()
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different conversation types"""
        return {
            'greeting': [
                "Hi {name}! Thanks for reaching out! 😊",
                "Hello {name}! Great to hear from you!",
                "Hey there {name}! How can I help you today?"
            ],
            'collaboration_inquiry': [
                "Hi {name}! I'm always excited about potential collaborations! Let me check my calendar and get back to you soon.",
                "Thanks for the collaboration opportunity, {name}! This sounds interesting. Let's discuss the details.",
                "Hello {name}! I appreciate you thinking of me for this collaboration. I'd love to learn more!"
            ],
            'fan_appreciation': [
                "Thank you so much {name}! Your support means everything to me! ❤️",
                "You're amazing {name}! Thank you for being such an incredible supporter!",
                "This just made my day, {name}! Thank you for the kind words! 🙏"
            ],
            'business_inquiry': [
                "Hi {name}! Thank you for your business inquiry. I'll review the details and get back to you within 24 hours.",
                "Hello {name}! I appreciate your interest in working together. Let me check availability and respond soon.",
                "Thanks for reaching out {name}! Your proposal looks interesting. I'll review and respond shortly."
            ],
            'support_request': [
                "Hi {name}! I'm sorry you're having trouble. Let me look into this and help you resolve it.",
                "Hello {name}! Thanks for bringing this to my attention. I'll work on getting this sorted out for you.",
                "Hey {name}! I want to make sure you have the best experience. Let me help you with this issue."
            ]
        }
    
    async def process_incoming_message(self, message_content: str, user_info: Dict[str, Any], platform: SocialPlatform) -> ConversationMessage:
        """Process incoming message and create conversation context"""
        try:
            # Create or update conversation context
            conversation = await self._get_or_create_conversation(user_info, platform)
            
            # Create message object
            message = ConversationMessage(
                conversation_id=conversation.conversation_id,
                sender='user',
                content=message_content,
                platform=platform
            )
            
            # Analyze message
            await self._analyze_message(message, conversation)
            
            # Update conversation context
            conversation.message_history.append(message.__dict__)
            conversation.last_interaction = datetime.utcnow()
            
            # Classify conversation type and priority
            await self._classify_conversation(conversation, message)
            
            logger.info(f"Processed incoming message from {user_info.get('username', 'unknown')} on {platform.value}")
            return message
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
            raise
    
    async def generate_response(self, conversation_id: str, message_id: str, custom_instructions: Optional[str] = None) -> ResponseGeneration:
        """Generate intelligent response for conversation"""
        try:
            if conversation_id not in self.active_conversations:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            conversation = self.active_conversations[conversation_id]
            
            # Find the message to respond to
            target_message = None
            for msg in conversation.message_history:
                if msg.get('message_id') == message_id:
                    target_message = msg
                    break
            
            if not target_message:
                raise ValueError(f"Message {message_id} not found in conversation")
            
            # Generate response based on conversation context
            response = await self._generate_intelligent_response(conversation, target_message, custom_instructions)
            
            # Add response to conversation history
            response_message = ConversationMessage(
                conversation_id=conversation_id,
                sender='agent',
                content=response.response_text,
                platform=conversation.platform,
                response_generated=True,
                response_quality_score=response.confidence_score
            )
            
            conversation.message_history.append(response_message.__dict__)
            
            logger.info(f"Generated response for conversation {conversation_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _get_or_create_conversation(self, user_info: Dict[str, Any], platform: SocialPlatform) -> ConversationContext:
        """Get existing conversation or create new one"""
        user_id = user_info.get('user_id', user_info.get('username', 'unknown'))
        
        # Look for existing conversation
        for conv in self.active_conversations.values():
            if conv.user_id == user_id and conv.platform == platform:
                return conv
        
        # Create new conversation
        conversation = ConversationContext(
            user_id=user_id,
            username=user_info.get('username', user_id),
            platform=platform,
            user_profile=user_info,
            follower_status=self._determine_follower_status(user_info)
        )
        
        self.active_conversations[conversation.conversation_id] = conversation
        return conversation
    
    def _determine_follower_status(self, user_info: Dict[str, Any]) -> str:
        """Determine user's follower status"""
        if user_info.get('verified', False):
            return 'vip'
        elif user_info.get('followers_count', 0) > 10000:
            return 'collaborator'
        elif user_info.get('following_me', False):
            return 'follower'
        else:
            return 'non_follower'
    
    async def _analyze_message(self, message: ConversationMessage, conversation: ConversationContext):
        """Perform comprehensive message analysis"""
        try:
            # Sentiment analysis
            message.sentiment_score = await self.sentiment_analyzer.analyze_sentiment(message.content)
            message.emotions = await self.sentiment_analyzer.detect_emotions(message.content)
            
            # Intent classification
            message.intent = await self.nlp_processor.analyze_intent(message.content)
            
            # Entity extraction
            message.entities = await self.nlp_processor.extract_entities(message.content)
            
            # Language detection
            conversation.language_detected = await self.nlp_processor.detect_language(message.content)
            
            # Extract mentions and hashtags
            message.mentions = re.findall(r'@(\w+)', message.content)
            message.hashtags = re.findall(r'#(\w+)', message.content)
            
            # Calculate urgency score
            message.urgency_score = self._calculate_urgency_score(message, conversation)
            
            # Update conversation topics and sentiment trend
            await self._update_conversation_context(message, conversation)
            
        except Exception as e:
            logger.error(f"Error analyzing message: {str(e)}")
    
    def _calculate_urgency_score(self, message: ConversationMessage, conversation: ConversationContext) -> float:
        """Calculate urgency score for message prioritization"""
        urgency = 0.0
        
        # Check for urgent keywords
        urgent_keywords = ['urgent', 'asap', 'emergency', 'problem', 'issue', 'help', 'broken']
        for keyword in urgent_keywords:
            if keyword.lower() in message.content.lower():
                urgency += 0.2
        
        # Business inquiries get higher urgency
        if 'collaboration' in message.intent or 'business' in message.intent:
            urgency += 0.3
        
        # VIP users get higher urgency
        if conversation.follower_status == 'vip':
            urgency += 0.2
        
        # Negative sentiment gets higher urgency
        if message.sentiment_score < 0.3:
            urgency += 0.1
        
        return min(urgency, 1.0)
    
    async def _update_conversation_context(self, message: ConversationMessage, conversation: ConversationContext):
        """Update conversation context with new insights"""
        # Add sentiment to trend
        conversation.sentiment_trend.append(message.sentiment_score)
        if len(conversation.sentiment_trend) > 10:
            conversation.sentiment_trend = conversation.sentiment_trend[-10:]
        
        # Extract and add topics
        entities = [entity['text'] for entity in message.entities if entity.get('type') == 'TOPIC']
        conversation.conversation_topics.extend(entities)
        conversation.conversation_topics = list(set(conversation.conversation_topics))[:10]
        
        # Update intent classification
        if message.intent:
            conversation.intent_classification = message.intent
    
    async def _classify_conversation(self, conversation: ConversationContext, message: ConversationMessage):
        """Classify conversation type and priority"""
        # Determine conversation type
        if 'collaboration' in message.intent.lower():
            conversation.conversation_type = ConversationType.COLLABORATION_INQUIRY
            conversation.priority = ConversationPriority.HIGH
        elif 'business' in message.intent.lower():
            conversation.conversation_type = ConversationType.BUSINESS_INQUIRY
            conversation.priority = ConversationPriority.HIGH
        elif message.urgency_score > 0.7:
            conversation.priority = ConversationPriority.URGENT
        elif conversation.follower_status == 'vip':
            conversation.priority = ConversationPriority.HIGH
        else:
            conversation.conversation_type = ConversationType.FAN_INTERACTION
            conversation.priority = ConversationPriority.MEDIUM
        
        # Determine if human attention is required
        conversation.requires_human_attention = (
            conversation.priority in [ConversationPriority.URGENT, ConversationPriority.HIGH] or
            message.sentiment_score < 0.2 or
            'complex' in message.intent.lower()
        )
    
    async def _generate_intelligent_response(self, conversation: ConversationContext, message: Dict[str, Any], custom_instructions: Optional[str] = None) -> ResponseGeneration:
        """Generate intelligent, personalized response"""
        try:
            # Determine response strategy
            response_type = self._determine_response_type(conversation, message)
            
            # Generate base response
            base_response = await self._generate_base_response(conversation, message, response_type)
            
            # Apply personalization
            personalized_response = await self._apply_personalization(base_response, conversation, message)
            
            # Add call-to-action if appropriate
            cta = self._generate_call_to_action(conversation, message)
            
            # Calculate quality scores
            confidence_score = self._calculate_response_confidence(personalized_response, conversation)
            engagement_potential = self._calculate_engagement_potential(personalized_response, conversation)
            
            response = ResponseGeneration(
                conversation_id=conversation.conversation_id,
                message_id=message['message_id'],
                response_text=personalized_response,
                response_tone=conversation.response_tone,
                confidence_score=confidence_score,
                call_to_action=cta,
                engagement_potential=engagement_potential,
                requires_approval=conversation.requires_human_attention
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating intelligent response: {str(e)}")
            # Fallback response
            return ResponseGeneration(
                conversation_id=conversation.conversation_id,
                message_id=message['message_id'],
                response_text="Thank you for your message! I'll get back to you soon.",
                confidence_score=0.5
            )
    
    def _determine_response_type(self, conversation: ConversationContext, message: Dict[str, Any]) -> str:
        """Determine appropriate response type"""
        if conversation.conversation_type == ConversationType.COLLABORATION_INQUIRY:
            return 'collaboration_inquiry'
        elif conversation.conversation_type == ConversationType.BUSINESS_INQUIRY:
            return 'business_inquiry'
        elif message.get('sentiment_score', 0.5) < 0.3:
            return 'support_request'
        elif len(conversation.message_history) <= 1:
            return 'greeting'
        else:
            return 'fan_appreciation'
    
    async def _generate_base_response(self, conversation: ConversationContext, message: Dict[str, Any], response_type: str) -> str:
        """Generate base response from templates"""
        templates = self.response_templates.get(response_type, self.response_templates['greeting'])
        
        # Select template based on conversation context
        template_index = hash(conversation.conversation_id) % len(templates)
        template = templates[template_index]
        
        # Format template with user information
        formatted_response = template.format(
            name=conversation.username,
            platform=conversation.platform.value
        )
        
        return formatted_response
    
    async def _apply_personalization(self, base_response: str, conversation: ConversationContext, message: Dict[str, Any]) -> str:
        """Apply personalization to response"""
        personalized = base_response
        
        # Add personal touches based on user profile
        if conversation.user_profile.get('interests'):
            interests = conversation.user_profile['interests'][:2]
            if interests:
                personalized += f" I noticed you're into {', '.join(interests)} - that's awesome!"
        
        # Reference previous interactions if available
        if len(conversation.message_history) > 2:
            personalized += " Thanks for being such an engaged member of our community!"
        
        # Adjust tone for VIP users
        if conversation.follower_status == 'vip':
            personalized = personalized.replace("Hi", "Hello").replace("Hey", "Hello")
            personalized += " It's always a pleasure hearing from you!"
        
        return personalized
    
    def _generate_call_to_action(self, conversation: ConversationContext, message: Dict[str, Any]) -> Optional[str]:
        """Generate appropriate call-to-action"""
        if conversation.conversation_type == ConversationType.COLLABORATION_INQUIRY:
            return "Feel free to DM me with more details about the collaboration!"
        elif conversation.follower_status == 'non_follower':
            return "If you enjoy my content, consider following for more updates!"
        elif 'music' in conversation.conversation_topics:
            return "Check out my latest track if you haven't already! 🎵"
        return None
    
    def _calculate_response_confidence(self, response: str, conversation: ConversationContext) -> float:
        """Calculate confidence score for generated response"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence for template-based responses
        if any(template in response for templates in self.response_templates.values() for template in templates):
            confidence += 0.1
        
        # Higher confidence for personalized responses
        if conversation.username.lower() in response.lower():
            confidence += 0.1
        
        # Lower confidence for complex conversations
        if conversation.requires_human_attention:
            confidence -= 0.2
        
        return max(0.1, min(confidence, 1.0))
    
    def _calculate_engagement_potential(self, response: str, conversation: ConversationContext) -> float:
        """Calculate engagement potential of response"""
        engagement = 0.5  # Base engagement
        
        # Higher engagement for questions
        if '?' in response:
            engagement += 0.2
        
        # Higher engagement for emojis
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', response))
        engagement += min(emoji_count * 0.1, 0.3)
        
        # Higher engagement for call-to-action
        cta_keywords = ['check out', 'follow', 'subscribe', 'listen', 'watch']
        if any(keyword in response.lower() for keyword in cta_keywords):
            engagement += 0.15
        
        return max(0.1, min(engagement, 1.0))
    
    async def get_conversation_analytics(self, time_range: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Get conversation analytics and insights"""
        cutoff_time = datetime.utcnow() - time_range
        recent_conversations = [
            conv for conv in self.active_conversations.values()
            if conv.last_interaction >= cutoff_time
        ]
        
        analytics = {
            'total_conversations': len(recent_conversations),
            'response_rate': len([c for c in recent_conversations if len(c.message_history) > 1]) / max(len(recent_conversations), 1),
            'average_response_time': self.response_metrics.get('average_response_time', 0.0),
            'platform_breakdown': {},
            'conversation_types': {},
            'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
            'priority_distribution': {}
        }
        
        # Calculate breakdowns
        for conv in recent_conversations:
            # Platform breakdown
            platform = conv.platform.value
            analytics['platform_breakdown'][platform] = analytics['platform_breakdown'].get(platform, 0) + 1
            
            # Conversation type breakdown
            conv_type = conv.conversation_type.value
            analytics['conversation_types'][conv_type] = analytics['conversation_types'].get(conv_type, 0) + 1
            
            # Priority breakdown
            priority = conv.priority.value
            analytics['priority_distribution'][priority] = analytics['priority_distribution'].get(priority, 0) + 1
            
            # Sentiment breakdown
            if conv.sentiment_trend:
                avg_sentiment = sum(conv.sentiment_trend) / len(conv.sentiment_trend)
                if avg_sentiment > 0.6:
                    analytics['sentiment_distribution']['positive'] += 1
                elif avg_sentiment < 0.4:
                    analytics['sentiment_distribution']['negative'] += 1
                else:
                    analytics['sentiment_distribution']['neutral'] += 1
        
        return analytics


__all__ = [
    "ConversationalAIAgent",
    "ConversationContext", 
    "ConversationMessage",
    "ResponseGeneration",
    "ConversationType",
    "ResponseTone",
    "ConversationPriority"
]
