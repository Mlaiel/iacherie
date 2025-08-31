"""Contextual Intent Processing and Enhancement

Advanced context-aware intent processing system that enhances intent recognition
through conversation context, user profile, and environmental factors.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict, deque

from .config import IntentRecognitionConfig
from .exceptions import ContextProcessingError

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context information"""    CONVERSATION = "conversation"
    USER_PROFILE = "user_profile"
    TEMPORAL = "temporal"
    ENVIRONMENTAL = "environmental"
    BUSINESS = "business"
    CREATIVE = "creative"


class ContextualWeight(Enum):
    """Context weighting categories"""    CRITICAL = 1.0
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.3
    MINIMAL = 0.1


@dataclass
class ConversationContext:
    """Conversation-specific context information"""    
    # Message history
    message_history: List[Dict[str, Any]] = field(default_factory=list)
    turn_count: int = 0
    conversation_duration: timedelta = field(default_factory=lambda: timedelta(0))
    
    # Topic tracking
    current_topic: Optional[str] = None
    topic_history: List[str] = field(default_factory=list)
    topic_shifts: int = 0
    
    # Intent patterns
    previous_intents: deque = field(default_factory=lambda: deque(maxlen=10))
    intent_patterns: Dict[str, int] = field(default_factory=dict)
    
    # Emotional context
    sentiment_trajectory: List[float] = field(default_factory=list)
    emotional_state: str = "neutral"
    urgency_level: float = 0.0


@dataclass
class UserProfileContext:
    """User profile and preference context"""    
    # Creator profile
    creator_type: str = "unknown"  # musician, influencer, photographer, etc.
    experience_level: str = "intermediate"
    preferred_genres: List[str] = field(default_factory=list)
    
    # Platform presence
    platforms: List[str] = field(default_factory=list)
    follower_count: Dict[str, int] = field(default_factory=dict)
    engagement_rates: Dict[str, float] = field(default_factory=dict)
    
    # Preferences
    communication_style: str = "professional"
    language_preference: str = "en"
    timezone: str = "UTC"
    
    # Behavioral patterns
    typical_session_duration: timedelta = field(default_factory=lambda: timedelta(minutes=15))
    peak_activity_hours: List[int] = field(default_factory=list)
    preferred_content_types: List[str] = field(default_factory=list)


@dataclass
class TemporalContext:
    """Time-based context information"""    
    # Current timing
    current_time: datetime = field(default_factory=datetime.now)
    day_of_week: int = 0
    hour_of_day: int = 0
    
    # Seasonal patterns
    season: str = "unknown"
    is_holiday_season: bool = False
    is_weekend: bool = False
    
    # Business timing
    is_business_hours: bool = True
    time_since_last_session: timedelta = field(default_factory=lambda: timedelta(0))
    
    # Content timing
    optimal_posting_time: bool = False
    trending_period: bool = False


@dataclass
class BusinessContext:
    """Business and monetization context"""    
    # Current projects
    active_projects: List[Dict[str, Any]] = field(default_factory=list)
    project_deadlines: List[datetime] = field(default_factory=list)
    
    # Monetization status
    revenue_streams: List[str] = field(default_factory=list)
    current_campaigns: List[str] = field(default_factory=list)
    protection_active: bool = False
    
    # Collaboration
    pending_collaborations: List[str] = field(default_factory=list)
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Goals and priorities
    monthly_goals: Dict[str, Any] = field(default_factory=dict)
    priority_metrics: List[str] = field(default_factory=list)


@dataclass
class ContextualEnhancement:
    """Context-based intent enhancement result"""    
    # Enhanced intent
    enhanced_intent: str
    confidence_boost: float
    context_factors: Dict[str, float]
    
    # Explanations
    enhancement_reasoning: List[str] = field(default_factory=list)
    context_warnings: List[str] = field(default_factory=list)
    
    # Alternative interpretations
    alternative_intents: List[Tuple[str, float]] = field(default_factory=list)
    contextual_ambiguities: List[str] = field(default_factory=list)


class ContextualEnhancer:
    """Context-based intent enhancement engine"""    
    def __init__(self, config: IntentRecognitionConfig):
        self.config = config
        self.context_weights = self._initialize_context_weights()
        self.enhancement_rules = self._load_enhancement_rules()
        self.pattern_matchers = self._initialize_pattern_matchers()
    
    def _initialize_context_weights(self) -> Dict[ContextType, float]:
        """Initialize context type weights"""        return {
            ContextType.CONVERSATION: 0.9,
            ContextType.USER_PROFILE: 0.8,
            ContextType.TEMPORAL: 0.6,
            ContextType.BUSINESS: 0.85,
            ContextType.CREATIVE: 0.75,
            ContextType.ENVIRONMENTAL: 0.4
        }
    
    def _load_enhancement_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load context-based enhancement rules"""        return {
            "music_creation": [
                {
                    "condition": "previous_intent == 'upload_audio'",
                    "enhancement": "intent_specificity += 0.3",
                    "reasoning": "Following upload pattern"
                },
                {
                    "condition": "user_type == 'musician' AND time_of_day in peak_hours",
                    "enhancement": "confidence += 0.2",
                    "reasoning": "Musician during creative hours"
                }
            ],
            "content_protection": [
                {
                    "condition": "protection_active == False AND revenue_streams > 0",
                    "enhancement": "priority += 0.4",
                    "reasoning": "Unprotected monetized content"
                }
            ],
            "collaboration": [
                {
                    "condition": "pending_collaborations > 0",
                    "enhancement": "relevance += 0.3",
                    "reasoning": "Active collaboration context"
                }
            ]
        }
    
    def _initialize_pattern_matchers(self) -> Dict[str, re.Pattern]:
        """Initialize pattern matching rules"""        return {
            "urgency_indicators": re.compile(r'\b(urgent|asap|quickly|now|immediately|deadline)\b', re.IGNORECASE),
            "creative_workflow": re.compile(r'\b(create|upload|edit|mix|master|publish|share)\b', re.IGNORECASE),
            "business_terms": re.compile(r'\b(revenue|monetize|earnings|collaboration|brand|sponsor)\b', re.IGNORECASE),
            "protection_terms": re.compile(r'\b(protect|copyright|steal|unauthorized|rights|dmca)\b', re.IGNORECASE),
            "platform_mentions": re.compile(r'\b(spotify|instagram|youtube|tiktok|soundcloud)\b', re.IGNORECASE)
        }
    
    def enhance_intent(
        self,
        base_intent: str,
        base_confidence: float,
        conversation_context: ConversationContext,
        user_context: UserProfileContext,
        temporal_context: TemporalContext,
        business_context: Optional[BusinessContext] = None,
        message_text: Optional[str] = None
    ) -> ContextualEnhancement:
        """        Enhance intent recognition using comprehensive context
        
        Args:
            base_intent: Original detected intent
            base_confidence: Original confidence score
            conversation_context: Conversation history and patterns
            user_context: User profile and preferences
            temporal_context: Time-based context
            business_context: Business and monetization context
            message_text: Current message text
            
        Returns:
            ContextualEnhancement: Enhanced intent with context analysis
        """        try:
            enhancement_factors = {}
            reasoning = []
            warnings = []
            alternatives = []
            
            # Analyze conversation context
            conv_enhancement = self._analyze_conversation_context(
                base_intent, conversation_context, message_text
            )
            enhancement_factors['conversation'] = conv_enhancement['factor']
            reasoning.extend(conv_enhancement['reasoning'])
            
            # Analyze user profile context
            profile_enhancement = self._analyze_user_profile_context(
                base_intent, user_context
            )
            enhancement_factors['user_profile'] = profile_enhancement['factor']
            reasoning.extend(profile_enhancement['reasoning'])
            
            # Analyze temporal context
            temporal_enhancement = self._analyze_temporal_context(
                base_intent, temporal_context, user_context
            )
            enhancement_factors['temporal'] = temporal_enhancement['factor']
            reasoning.extend(temporal_enhancement['reasoning'])
            
            # Analyze business context if available
            if business_context:
                business_enhancement = self._analyze_business_context(
                    base_intent, business_context
                )
                enhancement_factors['business'] = business_enhancement['factor']
                reasoning.extend(business_enhancement['reasoning'])
            
            # Calculate overall enhancement
            confidence_boost = self._calculate_confidence_boost(enhancement_factors)
            enhanced_intent = self._refine_intent(base_intent, enhancement_factors)
            
            # Detect potential ambiguities
            ambiguities = self._detect_contextual_ambiguities(
                base_intent, enhancement_factors, message_text
            )
            
            # Generate alternative interpretations
            alternatives = self._generate_alternative_intents(
                base_intent, enhancement_factors, conversation_context
            )
            
            # Generate warnings
            warnings = self._generate_context_warnings(
                enhancement_factors, temporal_context, business_context
            )
            
            return ContextualEnhancement(
                enhanced_intent=enhanced_intent,
                confidence_boost=confidence_boost,
                context_factors=enhancement_factors,
                enhancement_reasoning=reasoning,
                context_warnings=warnings,
                alternative_intents=alternatives,
                contextual_ambiguities=ambiguities
            )
            
        except Exception as e:
            logger.error(f"Context enhancement failed: {e}")
            raise ContextProcessingError(f"Enhancement failed: {e}")
    
    def _analyze_conversation_context(
        self,
        intent: str,
        context: ConversationContext,
        message_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze conversation-specific context factors"""        factors = []
        reasoning = []
        enhancement_factor = 0.0
        
        try:
            # Analyze intent patterns
            if intent in context.intent_patterns:
                frequency = context.intent_patterns[intent]
                if frequency > 3:
                    enhancement_factor += 0.2
                    reasoning.append(f"Frequent intent pattern ({frequency} times)")
            
            # Analyze previous intent sequence
            if len(context.previous_intents) > 0:
                last_intent = context.previous_intents[-1]
                
                # Intent flow patterns
                flow_patterns = {
                    ("upload_content", "protect_content"): 0.3,
                    ("create_music", "upload_audio"): 0.25,
                    ("analyze_performance", "optimize_content"): 0.2,
                    ("collaboration_request", "set_collaboration"): 0.35
                }
                
                pattern_key = (last_intent, intent)
                if pattern_key in flow_patterns:
                    boost = flow_patterns[pattern_key]
                    enhancement_factor += boost
                    reasoning.append(f"Intent flow pattern: {last_intent} → {intent}")
            
            # Analyze conversation length and engagement
            if context.turn_count > 5:
                enhancement_factor += 0.1
                reasoning.append("Extended conversation context")
            
            # Analyze sentiment trajectory
            if len(context.sentiment_trajectory) > 0:
                recent_sentiment = context.sentiment_trajectory[-1]
                if recent_sentiment < -0.5 and intent in ["get_help", "support_request"]:
                    enhancement_factor += 0.3
                    reasoning.append("Negative sentiment supports help intent")
            
            # Analyze urgency indicators in message
            if message_text:
                urgency_match = self.pattern_matchers["urgency_indicators"].search(message_text)
                if urgency_match:
                    if intent in ["support_request", "urgent_action"]:
                        enhancement_factor += 0.4
                        reasoning.append("Urgency indicators detected")
                    else:
                        enhancement_factor += 0.1
                        reasoning.append("General urgency context")
            
        except Exception as e:
            logger.warning(f"Conversation context analysis failed: {e}")
        
        return {
            "factor": min(1.0, enhancement_factor),
            "reasoning": reasoning
        }
    
    def _analyze_user_profile_context(
        self,
        intent: str,
        context: UserProfileContext
    ) -> Dict[str, Any]:
        """Analyze user profile context factors"""        enhancement_factor = 0.0
        reasoning = []
        
        try:
            # Creator type alignment
            creator_intent_alignment = {
                "musician": ["create_music", "upload_audio", "analyze_streams", "protect_music"],
                "influencer": ["create_content", "analyze_engagement", "collaboration", "brand_partnership"],
                "photographer": ["upload_image", "protect_image", "portfolio_management"],
                "blogger": ["create_text", "seo_optimization", "content_strategy"]
            }
            
            if context.creator_type in creator_intent_alignment:
                aligned_intents = creator_intent_alignment[context.creator_type]
                if intent in aligned_intents:
                    enhancement_factor += 0.3
                    reasoning.append(f"Intent aligned with {context.creator_type} profile")
            
            # Experience level considerations
            if context.experience_level == "beginner":
                if intent in ["get_help", "tutorial_request", "basic_setup"]:
                    enhancement_factor += 0.2
                    reasoning.append("Beginner-appropriate intent")
            elif context.experience_level == "expert":
                if intent in ["advanced_analytics", "api_access", "custom_integration"]:
                    enhancement_factor += 0.2
                    reasoning.append("Expert-level intent")
            
            # Platform-specific enhancement
            if context.platforms:
                platform_intents = {
                    "spotify": ["upload_audio", "analyze_streams", "playlist_optimization"],
                    "instagram": ["upload_image", "story_creation", "reels_optimization"],
                    "youtube": ["upload_video", "analytics_review", "monetization_setup"]
                }
                
                for platform in context.platforms:
                    if platform in platform_intents and intent in platform_intents[platform]:
                        enhancement_factor += 0.15
                        reasoning.append(f"Intent relevant to {platform} platform")
            
            # Engagement level considerations
            if context.engagement_rates:
                avg_engagement = sum(context.engagement_rates.values()) / len(context.engagement_rates.values())
                if avg_engagement > 0.05 and intent in ["content_strategy", "optimization"]:
                    enhancement_factor += 0.1
                    reasoning.append("High engagement supports optimization intent")
            
        except Exception as e:
            logger.warning(f"User profile context analysis failed: {e}")
        
        return {
            "factor": min(1.0, enhancement_factor),
            "reasoning": reasoning
        }
    
    def _analyze_temporal_context(
        self,
        intent: str,
        temporal_context: TemporalContext,
        user_context: UserProfileContext
    ) -> Dict[str, Any]:
        """Analyze time-based context factors"""        enhancement_factor = 0.0
        reasoning = []
        
        try:
            # Peak activity hours
            if user_context.peak_activity_hours and temporal_context.hour_of_day in user_context.peak_activity_hours:
                enhancement_factor += 0.15
                reasoning.append("During user's peak activity hours")
            
            # Business hours alignment
            business_hour_intents = ["collaboration", "support_request", "business_inquiry"]
            if temporal_context.is_business_hours and intent in business_hour_intents:
                enhancement_factor += 0.1
                reasoning.append("Business intent during business hours")
            
            # Weekend/leisure time patterns
            leisure_intents = ["create_content", "explore_features", "casual_browsing"]
            if temporal_context.is_weekend and intent in leisure_intents:
                enhancement_factor += 0.1
                reasoning.append("Leisure intent during weekend")
            
            # Trending periods
            if temporal_context.trending_period:
                trending_intents = ["upload_content", "publish_content", "social_media_post"]
                if intent in trending_intents:
                    enhancement_factor += 0.2
                    reasoning.append("Content publication during trending period")
            
            # Time since last session
            if temporal_context.time_since_last_session > timedelta(days=7):
                if intent in ["catch_up", "review_analytics", "check_updates"]:
                    enhancement_factor += 0.25
                    reasoning.append("Returning user after extended absence")
            
        except Exception as e:
            logger.warning(f"Temporal context analysis failed: {e}")
        
        return {
            "factor": min(1.0, enhancement_factor),
            "reasoning": reasoning
        }
    
    def _analyze_business_context(
        self,
        intent: str,
        context: BusinessContext
    ) -> Dict[str, Any]:
        """Analyze business and monetization context"""        enhancement_factor = 0.0
        reasoning = []
        
        try:
            # Active projects relevance
            if context.active_projects:
                project_related_intents = ["project_management", "deadline_tracking", "collaboration"]
                if intent in project_related_intents:
                    enhancement_factor += 0.2
                    reasoning.append("Intent relevant to active projects")
            
            # Monetization status
            if context.revenue_streams:
                monetization_intents = ["revenue_analytics", "payment_tracking", "tax_reporting"]
                if intent in monetization_intents:
                    enhancement_factor += 0.3
                    reasoning.append("Monetization-related intent for earning creator")
            
            # Protection status
            if not context.protection_active and context.revenue_streams:
                protection_intents = ["content_protection", "copyright_setup", "rights_management"]
                if intent in protection_intents:
                    enhancement_factor += 0.4
                    reasoning.append("Critical: Unprotected monetized content")
            
            # Pending collaborations
            if context.pending_collaborations:
                collaboration_intents = ["collaboration_management", "partner_communication", "contract_review"]
                if intent in collaboration_intents:
                    enhancement_factor += 0.25
                    reasoning.append("Active collaboration context")
            
            # Goal alignment
            if context.monthly_goals:
                for goal_type, goal_data in context.monthly_goals.items():
                    if goal_type in intent or intent in str(goal_data):
                        enhancement_factor += 0.15
                        reasoning.append(f"Intent aligned with monthly goal: {goal_type}")
            
        except Exception as e:
            logger.warning(f"Business context analysis failed: {e}")
        
        return {
            "factor": min(1.0, enhancement_factor),
            "reasoning": reasoning
        }
    
    def _calculate_confidence_boost(self, enhancement_factors: Dict[str, float]) -> float:
        """Calculate overall confidence boost from context factors"""        weighted_boost = 0.0
        total_weight = 0.0
        
        for context_type_str, factor in enhancement_factors.items():
            try:
                # Map string to enum
                context_type = ContextType(context_type_str)
                weight = self.context_weights.get(context_type, 0.5)
                
                weighted_boost += factor * weight
                total_weight += weight
                
            except (ValueError, KeyError):
                # Handle unknown context types
                weighted_boost += factor * 0.5
                total_weight += 0.5
        
        if total_weight > 0:
            return min(0.5, weighted_boost / total_weight)  # Cap at 0.5 boost
        else:
            return 0.0
    
    def _refine_intent(self, base_intent: str, enhancement_factors: Dict[str, float]) -> str:
        """Refine intent based on context analysis"""        # For now, return the base intent
        # Future enhancement: use context to suggest more specific intents
        
        # Apply intent refinement rules
        refinement_rules = {
            "create_content": {
                "conversation": lambda f: "create_music" if f > 0.3 else "create_content",
                "user_profile": lambda f: "create_advanced_content" if f > 0.4 else "create_content"
            }
        }
        
        if base_intent in refinement_rules:
            rules = refinement_rules[base_intent]
            for context_type, rule_func in rules.items():
                if context_type in enhancement_factors:
                    factor = enhancement_factors[context_type]
                    refined = rule_func(factor)
                    if refined != base_intent:
                        return refined
        
        return base_intent
    
    def _detect_contextual_ambiguities(
        self,
        intent: str,
        enhancement_factors: Dict[str, float],
        message_text: Optional[str] = None
    ) -> List[str]:
        """Detect potential ambiguities in context interpretation"""        ambiguities = []
        
        # Check for conflicting context signals
        if 'conversation' in enhancement_factors and 'temporal' in enhancement_factors:
            conv_factor = enhancement_factors['conversation']
            temp_factor = enhancement_factors['temporal']
            
            if abs(conv_factor - temp_factor) > 0.4:
                ambiguities.append("Conflicting conversation and temporal context signals")
        
        # Check for pattern inconsistencies
        if message_text:
            creative_patterns = len(self.pattern_matchers["creative_workflow"].findall(message_text))
            business_patterns = len(self.pattern_matchers["business_terms"].findall(message_text))
            
            if creative_patterns > 0 and business_patterns > 0:
                ambiguities.append("Mixed creative and business context in message")
        
        return ambiguities
    
    def _generate_alternative_intents(
        self,
        base_intent: str,
        enhancement_factors: Dict[str, float],
        conversation_context: ConversationContext
    ) -> List[Tuple[str, float]]:
        """Generate alternative intent interpretations"""        alternatives = []
        
        # Generate alternatives based on context strength
        intent_alternatives = {
            "upload_content": [
                ("upload_audio", 0.8),
                ("upload_video", 0.6),
                ("upload_image", 0.5)
            ],
            "create_content": [
                ("create_music", 0.7),
                ("create_video", 0.6),
                ("create_social_post", 0.5)
            ],
            "protect_content": [
                ("copyright_registration", 0.8),
                ("content_monitoring", 0.7),
                ("rights_management", 0.6)
            ]
        }
        
        if base_intent in intent_alternatives:
            base_alternatives = intent_alternatives[base_intent]
            
            # Adjust probabilities based on context
            for alt_intent, base_prob in base_alternatives:
                # Apply context-based adjustments
                context_adjustment = sum(enhancement_factors.values()) / len(enhancement_factors)
                adjusted_prob = base_prob * (1 + context_adjustment * 0.3)
                
                alternatives.append((alt_intent, min(1.0, adjusted_prob)))
        
        return alternatives
    
    def _generate_context_warnings(
        self,
        enhancement_factors: Dict[str, float],
        temporal_context: TemporalContext,
        business_context: Optional[BusinessContext] = None
    ) -> List[str]:
        """Generate context-based warnings and recommendations"""        warnings = []
        
        # Low context confidence warning
        if all(factor < 0.2 for factor in enhancement_factors.values()):
            warnings.append("Low context confidence - consider requesting clarification")
        
        # Business hours warning
        if not temporal_context.is_business_hours:
            warnings.append("Outside business hours - response time may be delayed")
        
        # Protection warnings
        if business_context and business_context.revenue_streams and not business_context.protection_active:
            warnings.append("CRITICAL: Monetized content without protection - immediate action recommended")
        
        # Project deadline warnings
        if business_context and business_context.project_deadlines:
            now = datetime.now()
            for deadline in business_context.project_deadlines:
                if deadline - now < timedelta(days=3):
                    warnings.append(f"Project deadline approaching: {deadline.strftime('%Y-%m-%d')}")
        
        return warnings


class ContextualIntentProcessor:
    """    Main contextual intent processing system
    
    Orchestrates context gathering, analysis, and intent enhancement
    """    
    def __init__(self, config: IntentRecognitionConfig):
        self.config = config
        self.enhancer = ContextualEnhancer(config)
        self.context_cache = {}
        self.session_contexts = {}
    
    def process_intent_with_context(
        self,
        intent: str,
        confidence: float,
        session_id: str,
        user_id: str,
        message_text: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> ContextualEnhancement:
        """        Process intent with full contextual enhancement
        
        Args:
            intent: Detected intent
            confidence: Base confidence score
            session_id: Conversation session ID
            user_id: User identifier
            message_text: Original message text
            additional_context: Additional context information
            
        Returns:
            ContextualEnhancement: Enhanced intent with context analysis
        """        try:
            # Gather context information
            conversation_context = self._gather_conversation_context(session_id)
            user_context = self._gather_user_context(user_id)
            temporal_context = self._gather_temporal_context()
            business_context = self._gather_business_context(user_id)
            
            # Update conversation context with current message
            self._update_conversation_context(
                session_id, intent, message_text, conversation_context
            )
            
            # Apply contextual enhancement
            enhancement = self.enhancer.enhance_intent(
                base_intent=intent,
                base_confidence=confidence,
                conversation_context=conversation_context,
                user_context=user_context,
                temporal_context=temporal_context,
                business_context=business_context,
                message_text=message_text
            )
            
            # Store enhanced context for future use
            self._store_session_context(session_id, {
                'intent': enhancement.enhanced_intent,
                'confidence': confidence + enhancement.confidence_boost,
                'context_factors': enhancement.context_factors,
                'timestamp': datetime.now()
            })
            
            return enhancement
            
        except Exception as e:
            logger.error(f"Contextual intent processing failed: {e}")
            raise ContextProcessingError(f"Processing failed: {e}")
    
    def _gather_conversation_context(self, session_id: str) -> ConversationContext:
        """Gather conversation-specific context"""        # Implementation would fetch from conversation history storage
        # For now, return default context
        return ConversationContext()
    
    def _gather_user_context(self, user_id: str) -> UserProfileContext:
        """Gather user profile context"""        # Implementation would fetch from user profile database
        # For now, return default context
        return UserProfileContext()
    
    def _gather_temporal_context(self) -> TemporalContext:
        """Gather current temporal context"""        now = datetime.now()
        return TemporalContext(
            current_time=now,
            day_of_week=now.weekday(),
            hour_of_day=now.hour,
            is_weekend=now.weekday() >= 5,
            is_business_hours=9 <= now.hour <= 17
        )
    
    def _gather_business_context(self, user_id: str) -> Optional[BusinessContext]:
        """Gather business and monetization context"""        # Implementation would fetch from business data storage
        # For now, return None
        return None
    
    def _update_conversation_context(
        self,
        session_id: str,
        intent: str,
        message_text: str,
        context: ConversationContext
    ):
        """Update conversation context with current interaction"""        context.turn_count += 1
        context.previous_intents.append(intent)
        
        if intent in context.intent_patterns:
            context.intent_patterns[intent] += 1
        else:
            context.intent_patterns[intent] = 1
        
        # Add message to history
        context.message_history.append({
            'text': message_text,
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        })
    
    def _store_session_context(self, session_id: str, context_data: Dict[str, Any]):
        """Store session context for future reference"""        self.session_contexts[session_id] = context_data
    
    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of current session context"""        return self.session_contexts.get(session_id, {})
    
    def clear_session_context(self, session_id: str):
        """Clear stored context for a session"""        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
