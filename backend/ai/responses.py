"""
Response Generation and Optimization Module
==========================================

Consolidated response generation functionality from conversational/response_generation/
and related modules. Provides advanced response generation, optimization, and personalization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import random
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import re

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """Types of responses that can be generated"""
    INFORMATIONAL = "informational"
    CONVERSATIONAL = "conversational"
    INSTRUCTIONAL = "instructional"
    CREATIVE = "creative"
    SUPPORTIVE = "supportive"
    BUSINESS_ADVICE = "business_advice"
    TECHNICAL_HELP = "technical_help"
    ENTERTAINMENT = "entertainment"
    PERSONALIZED = "personalized"
    MULTIMODAL = "multimodal"

class ResponseTone(Enum):
    """Response tone options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    EMPATHETIC = "empathetic"
    AUTHORITATIVE = "authoritative"
    HUMOROUS = "humorous"
    NEUTRAL = "neutral"

class PersonalizationLevel(Enum):
    """Levels of response personalization"""
    NONE = "none"
    BASIC = "basic"
    MODERATE = "moderate"
    HIGH = "high"
    MAXIMUM = "maximum"

class ResponseQuality(Enum):
    """Response quality levels"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"
    OUTSTANDING = "outstanding"

@dataclass
class ResponseContext:
    """Context for response generation"""
    user_id: str
    conversation_id: str
    user_message: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_profile: Optional[Dict[str, Any]] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    business_context: Optional[Dict[str, Any]] = None
    emotional_state: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResponseCandidate:
    """A candidate response with metadata"""
    content: str
    response_type: ResponseType
    tone: ResponseTone
    quality_score: float
    personalization_score: float
    relevance_score: float
    creativity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeneratedResponse:
    """Final generated response with all metadata"""
    content: str
    response_type: ResponseType
    tone: ResponseTone
    quality_metrics: Dict[str, float]
    personalization_level: PersonalizationLevel
    generation_time: float
    alternatives: List[ResponseCandidate] = field(default_factory=list)
    optimization_applied: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ResponseTemplate:
    """Template for response generation"""
    template_id: str
    name: str
    template_text: str
    response_type: ResponseType
    variables: List[str] = field(default_factory=list)
    tone_variants: Dict[ResponseTone, str] = field(default_factory=dict)
    usage_count: int = 0
    effectiveness_score: float = 0.0

class BaseResponseGenerator(ABC):
    """Base class for response generators"""
    
    @abstractmethod
    async def generate(self, context: ResponseContext) -> GeneratedResponse:
        """Generate response based on context"""
        pass
    
    @abstractmethod
    async def optimize_response(self, response: str, context: ResponseContext) -> str:
        """Optimize a response for the given context"""
        pass

class TemplateEngine:
    """Template-based response generation engine"""
    
    def __init__(self):
        self.templates: Dict[str, ResponseTemplate] = {}
        self.template_categories: Dict[ResponseType, List[str]] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default response templates"""
        default_templates = [
            ResponseTemplate(
                template_id="greeting_friendly",
                name="Friendly Greeting",
                template_text="Hi {user_name}! It's great to chat with you. How can I help you today?",
                response_type=ResponseType.CONVERSATIONAL,
                variables=["user_name"],
                tone_variants={
                    ResponseTone.CASUAL: "Hey {user_name}! What's up? How can I help?",
                    ResponseTone.PROFESSIONAL: "Hello {user_name}. How may I assist you today?",
                    ResponseTone.ENTHUSIASTIC: "Hi there {user_name}! I'm excited to help you today!"
                }
            ),
            ResponseTemplate(
                template_id="business_advice",
                name="Business Advice Template",
                template_text="Based on your {business_area} goals, I recommend {recommendation}. This approach has shown {success_rate}% effectiveness in similar cases.",
                response_type=ResponseType.BUSINESS_ADVICE,
                variables=["business_area", "recommendation", "success_rate"]
            ),
            ResponseTemplate(
                template_id="technical_help",
                name="Technical Help Template", 
                template_text="For {technical_issue}, the best solution is {solution}. Here are the steps: {steps}",
                response_type=ResponseType.TECHNICAL_HELP,
                variables=["technical_issue", "solution", "steps"]
            ),
            ResponseTemplate(
                template_id="creative_inspiration",
                name="Creative Inspiration Template",
                template_text="That's a fantastic {content_type} idea! To make it even more engaging, consider {creative_suggestion}. Your audience would love {specific_element}!",
                response_type=ResponseType.CREATIVE,
                variables=["content_type", "creative_suggestion", "specific_element"]
            )
        ]
        
        for template in default_templates:
            self.add_template(template)
    
    def add_template(self, template: ResponseTemplate):
        """Add a response template"""
        self.templates[template.template_id] = template
        
        # Add to category index
        if template.response_type not in self.template_categories:
            self.template_categories[template.response_type] = []
        self.template_categories[template.response_type].append(template.template_id)
    
    async def generate_from_template(self, template_id: str, variables: Dict[str, Any], 
                                   tone: ResponseTone = ResponseTone.NEUTRAL) -> str:
        """Generate response from template"""
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Choose appropriate template text based on tone
        if tone in template.tone_variants:
            template_text = template.tone_variants[tone]
        else:
            template_text = template.template_text
        
        # Replace variables
        response = template_text
        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            response = response.replace(placeholder, str(var_value))
        
        # Update usage statistics
        template.usage_count += 1
        
        return response
    
    async def find_best_template(self, response_type: ResponseType, context: ResponseContext) -> Optional[str]:
        """Find the best template for given type and context"""
        if response_type not in self.template_categories:
            return None
        
        templates = self.template_categories[response_type]
        if not templates:
            return None
        
        # Simple selection - return template with highest effectiveness score
        best_template = max(templates, key=lambda t: self.templates[t].effectiveness_score)
        return best_template

class PersonalizedResponseGenerator(BaseResponseGenerator):
    """Advanced personalized response generator"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.personalization_cache: Dict[str, Dict[str, Any]] = {}
        self.response_history: Dict[str, List[str]] = {}
    
    async def generate(self, context: ResponseContext) -> GeneratedResponse:
        """Generate personalized response"""
        start_time = datetime.now()
        
        # Analyze user preferences and context
        user_preferences = await self._analyze_user_preferences(context)
        
        # Determine response type based on context
        response_type = await self._determine_response_type(context)
        
        # Determine appropriate tone
        tone = await self._determine_tone(context, user_preferences)
        
        # Generate multiple response candidates
        candidates = await self._generate_candidates(context, response_type, tone)
        
        # Select best candidate
        best_candidate = await self._select_best_candidate(candidates, context)
        
        # Apply optimization
        optimized_content = await self.optimize_response(best_candidate.content, context)
        
        # Calculate quality metrics
        quality_metrics = await self._calculate_quality_metrics(optimized_content, context)
        
        # Determine personalization level
        personalization_level = await self._assess_personalization_level(context, user_preferences)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Store response in history
        if context.user_id not in self.response_history:
            self.response_history[context.user_id] = []
        self.response_history[context.user_id].append(optimized_content)
        
        return GeneratedResponse(
            content=optimized_content,
            response_type=response_type,
            tone=tone,
            quality_metrics=quality_metrics,
            personalization_level=personalization_level,
            generation_time=generation_time,
            alternatives=candidates,
            optimization_applied=["personalization", "tone_adjustment", "quality_enhancement"]
        )
    
    async def optimize_response(self, response: str, context: ResponseContext) -> str:
        """Optimize response for better quality and personalization"""
        optimized = response
        
        # Apply user name personalization
        if context.user_profile and "name" in context.user_profile:
            user_name = context.user_profile["name"]
            if "{user_name}" in optimized:
                optimized = optimized.replace("{user_name}", user_name)
            elif not any(name.lower() in optimized.lower() for name in [user_name]):
                # Add user name if not present
                optimized = f"Hi {user_name}! {optimized}"
        
        # Apply platform-specific optimization
        if context.platform:
            optimized = await self._optimize_for_platform(optimized, context.platform)
        
        # Apply business context optimization
        if context.business_context:
            optimized = await self._optimize_for_business_context(optimized, context.business_context)
        
        # Apply length optimization
        optimized = await self._optimize_length(optimized, context)
        
        return optimized
    
    async def _analyze_user_preferences(self, context: ResponseContext) -> Dict[str, Any]:
        """Analyze user preferences from context and history"""
        user_id = context.user_id
        
        # Use cached preferences if available
        if user_id in self.personalization_cache:
            return self.personalization_cache[user_id]
        
        preferences = {
            "preferred_tone": ResponseTone.FRIENDLY,
            "response_length_preference": "medium",
            "topics_of_interest": [],
            "communication_style": "balanced",
            "expertise_level": "intermediate"
        }
        
        # Analyze user profile
        if context.user_profile:
            preferences.update(context.user_profile.get("preferences", {}))
        
        # Analyze conversation history
        if context.conversation_history:
            preferences = await self._analyze_conversation_patterns(context.conversation_history, preferences)
        
        # Cache preferences
        self.personalization_cache[user_id] = preferences
        
        return preferences
    
    async def _determine_response_type(self, context: ResponseContext) -> ResponseType:
        """Determine appropriate response type based on context"""
        message = context.user_message.lower()
        
        # Keyword-based classification
        if any(word in message for word in ["how to", "tutorial", "learn", "teach", "explain"]):
            return ResponseType.INSTRUCTIONAL
        elif any(word in message for word in ["business", "strategy", "marketing", "monetize"]):
            return ResponseType.BUSINESS_ADVICE
        elif any(word in message for word in ["technical", "error", "bug", "fix", "code"]):
            return ResponseType.TECHNICAL_HELP
        elif any(word in message for word in ["creative", "idea", "inspiration", "artistic"]):
            return ResponseType.CREATIVE
        elif any(word in message for word in ["sad", "stressed", "worried", "anxious"]):
            return ResponseType.SUPPORTIVE
        elif any(word in message for word in ["fun", "joke", "entertaining", "funny"]):
            return ResponseType.ENTERTAINMENT
        else:
            return ResponseType.CONVERSATIONAL
    
    async def _determine_tone(self, context: ResponseContext, preferences: Dict[str, Any]) -> ResponseTone:
        """Determine appropriate response tone"""
        # Check user preferences
        preferred_tone = preferences.get("preferred_tone")
        if preferred_tone and isinstance(preferred_tone, ResponseTone):
            return preferred_tone
        
        # Check emotional state
        if context.emotional_state:
            if context.emotional_state == "stressed":
                return ResponseTone.EMPATHETIC
            elif context.emotional_state == "excited":
                return ResponseTone.ENTHUSIASTIC
        
        # Check business context
        if context.business_context:
            return ResponseTone.PROFESSIONAL
        
        # Default to friendly
        return ResponseTone.FRIENDLY
    
    async def _generate_candidates(self, context: ResponseContext, response_type: ResponseType, 
                                 tone: ResponseTone) -> List[ResponseCandidate]:
        """Generate multiple response candidates"""
        candidates = []
        
        # Template-based generation
        template_id = await self.template_engine.find_best_template(response_type, context)
        if template_id:
            variables = await self._extract_template_variables(context)
            template_response = await self.template_engine.generate_from_template(
                template_id, variables, tone
            )
            candidates.append(ResponseCandidate(
                content=template_response,
                response_type=response_type,
                tone=tone,
                quality_score=0.8,
                personalization_score=0.7,
                relevance_score=0.85,
                creativity_score=0.6
            ))
        
        # Rule-based generation
        rule_based_response = await self._generate_rule_based_response(context, response_type, tone)
        if rule_based_response:
            candidates.append(ResponseCandidate(
                content=rule_based_response,
                response_type=response_type,
                tone=tone,
                quality_score=0.75,
                personalization_score=0.6,
                relevance_score=0.8,
                creativity_score=0.7
            ))
        
        # Creative generation
        creative_response = await self._generate_creative_response(context, response_type, tone)
        if creative_response:
            candidates.append(ResponseCandidate(
                content=creative_response,
                response_type=response_type,
                tone=tone,
                quality_score=0.7,
                personalization_score=0.8,
                relevance_score=0.75,
                creativity_score=0.9
            ))
        
        return candidates
    
    async def _extract_template_variables(self, context: ResponseContext) -> Dict[str, Any]:
        """Extract variables for template filling"""
        variables = {}
        
        # User information
        if context.user_profile:
            variables["user_name"] = context.user_profile.get("name", "there")
        
        # Business context
        if context.business_context:
            variables["business_area"] = context.business_context.get("focus_area", "business")
        
        # Platform information
        if context.platform:
            variables["platform"] = context.platform
        
        # Content type
        if context.content_type:
            variables["content_type"] = context.content_type
        
        return variables
    
    async def _generate_rule_based_response(self, context: ResponseContext, 
                                          response_type: ResponseType, tone: ResponseTone) -> Optional[str]:
        """Generate response using rule-based approach"""
        message = context.user_message.lower()
        
        # Question responses
        if "?" in context.user_message:
            if response_type == ResponseType.BUSINESS_ADVICE:
                return "That's a great business question! Based on current market trends, I'd suggest focusing on authentic engagement and building genuine relationships with your audience."
            elif response_type == ResponseType.TECHNICAL_HELP:
                return "I understand you need technical assistance. Let me help you troubleshoot this step by step."
            else:
                return "That's an interesting question! Let me share some insights that might help."
        
        # Greeting responses
        if any(greeting in message for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            if tone == ResponseTone.PROFESSIONAL:
                return "Hello! I'm pleased to assist you today. How may I help with your content creation goals?"
            elif tone == ResponseTone.CASUAL:
                return "Hey there! What's on your mind today?"
            else:
                return "Hi! Great to see you. What can I help you with?"
        
        return None
    
    async def _generate_creative_response(self, context: ResponseContext,
                                        response_type: ResponseType, tone: ResponseTone) -> Optional[str]:
        """Generate creative, original response"""
        # This would typically use more advanced NLP models
        # For now, we'll create rule-based creative responses
        
        if response_type == ResponseType.CREATIVE:
            creative_elements = [
                "That sparks so many creative possibilities!",
                "I love how you're thinking outside the box!",
                "Your creative vision is inspiring!",
                "This could be the start of something amazing!"
            ]
            return random.choice(creative_elements)
        
        elif response_type == ResponseType.SUPPORTIVE:
            supportive_elements = [
                "I'm here to support you through this.",
                "You're taking all the right steps.",
                "Your dedication to improvement is admirable.",
                "Every challenge is an opportunity to grow."
            ]
            return random.choice(supportive_elements)
        
        return None
    
    async def _select_best_candidate(self, candidates: List[ResponseCandidate], 
                                   context: ResponseContext) -> ResponseCandidate:
        """Select the best response candidate"""
        if not candidates:
            # Fallback response
            return ResponseCandidate(
                content="I'd be happy to help! Could you tell me more about what you're looking for?",
                response_type=ResponseType.CONVERSATIONAL,
                tone=ResponseTone.FRIENDLY,
                quality_score=0.6,
                personalization_score=0.3,
                relevance_score=0.5,
                creativity_score=0.4
            )
        
        # Score candidates based on multiple factors
        def score_candidate(candidate: ResponseCandidate) -> float:
            return (
                candidate.quality_score * 0.3 +
                candidate.personalization_score * 0.25 +
                candidate.relevance_score * 0.3 +
                candidate.creativity_score * 0.15
            )
        
        return max(candidates, key=score_candidate)
    
    async def _calculate_quality_metrics(self, response: str, context: ResponseContext) -> Dict[str, float]:
        """Calculate quality metrics for response"""
        metrics = {
            "length_appropriateness": await self._assess_length_appropriateness(response, context),
            "relevance": await self._assess_relevance(response, context),
            "coherence": await self._assess_coherence(response),
            "personalization": await self._assess_personalization(response, context),
            "engagement_potential": await self._assess_engagement_potential(response),
            "overall_quality": 0.0
        }
        
        # Calculate overall quality as weighted average
        weights = {
            "length_appropriateness": 0.15,
            "relevance": 0.25,
            "coherence": 0.20,
            "personalization": 0.20,
            "engagement_potential": 0.20
        }
        
        metrics["overall_quality"] = sum(
            metrics[metric] * weight for metric, weight in weights.items()
        )
        
        return metrics
    
    async def _assess_length_appropriateness(self, response: str, context: ResponseContext) -> float:
        """Assess if response length is appropriate"""
        word_count = len(response.split())
        
        # Ideal range: 10-50 words for most responses
        if 10 <= word_count <= 50:
            return 1.0
        elif 5 <= word_count < 10 or 50 < word_count <= 100:
            return 0.8
        elif word_count < 5 or word_count > 100:
            return 0.5
        else:
            return 0.3
    
    async def _assess_relevance(self, response: str, context: ResponseContext) -> float:
        """Assess relevance of response to user message"""
        # Simple keyword overlap assessment
        user_words = set(context.user_message.lower().split())
        response_words = set(response.lower().split())
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        user_words -= stop_words
        response_words -= stop_words
        
        if not user_words:
            return 0.7  # Neutral score if no content words
        
        overlap = len(user_words.intersection(response_words))
        relevance = overlap / len(user_words)
        
        return min(1.0, relevance + 0.5)  # Boost score as exact keyword matching is limited
    
    async def _assess_coherence(self, response: str) -> float:
        """Assess coherence and flow of response"""
        # Simple coherence assessment based on structure
        sentences = response.split('.')
        if len(sentences) < 2:
            return 0.9  # Single sentence is coherent
        
        # Check for logical connectors
        connectors = ["however", "therefore", "also", "furthermore", "additionally", "meanwhile"]
        has_connectors = any(connector in response.lower() for connector in connectors)
        
        # Basic structural coherence
        base_score = 0.8
        if has_connectors:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    async def _assess_personalization(self, response: str, context: ResponseContext) -> float:
        """Assess level of personalization in response"""
        personalization_score = 0.0
        
        # Check for user name usage
        if context.user_profile and "name" in context.user_profile:
            user_name = context.user_profile["name"]
            if user_name.lower() in response.lower():
                personalization_score += 0.3
        
        # Check for context-specific references
        if context.platform and context.platform.lower() in response.lower():
            personalization_score += 0.2
        
        if context.content_type and context.content_type.lower() in response.lower():
            personalization_score += 0.2
        
        # Check for conversation history references
        if context.conversation_history and len(context.conversation_history) > 0:
            # Simple check for continuity
            personalization_score += 0.3
        
        return min(1.0, personalization_score)
    
    async def _assess_engagement_potential(self, response: str) -> float:
        """Assess potential for user engagement"""
        engagement_score = 0.5  # Base score
        
        # Check for questions (encourage interaction)
        if "?" in response:
            engagement_score += 0.2
        
        # Check for enthusiasm markers
        enthusiasm_markers = ["!", "great", "awesome", "exciting", "amazing", "fantastic"]
        if any(marker in response.lower() for marker in enthusiasm_markers):
            engagement_score += 0.2
        
        # Check for actionable suggestions
        action_words = ["try", "consider", "check out", "explore", "discover"]
        if any(word in response.lower() for word in action_words):
            engagement_score += 0.1
        
        return min(1.0, engagement_score)
    
    async def _assess_personalization_level(self, context: ResponseContext, 
                                          preferences: Dict[str, Any]) -> PersonalizationLevel:
        """Assess the level of personalization achieved"""
        score = 0
        
        # User profile usage
        if context.user_profile:
            score += 1
        
        # Conversation history usage
        if context.conversation_history:
            score += 1
        
        # Platform-specific optimization
        if context.platform:
            score += 1
        
        # Business context usage
        if context.business_context:
            score += 1
        
        # Emotional state consideration
        if context.emotional_state:
            score += 1
        
        if score >= 4:
            return PersonalizationLevel.MAXIMUM
        elif score >= 3:
            return PersonalizationLevel.HIGH
        elif score >= 2:
            return PersonalizationLevel.MODERATE
        elif score >= 1:
            return PersonalizationLevel.BASIC
        else:
            return PersonalizationLevel.NONE
    
    async def _optimize_for_platform(self, response: str, platform: str) -> str:
        """Optimize response for specific platform"""
        platform_lower = platform.lower()
        
        if platform_lower == "twitter":
            # Keep it concise for Twitter
            if len(response) > 200:
                response = response[:197] + "..."
        elif platform_lower == "linkedin":
            # More professional tone for LinkedIn
            response = response.replace("Hey!", "Hello").replace("awesome", "excellent")
        elif platform_lower == "instagram":
            # Add some visual elements suggestion
            if "content" in response.lower():
                response += " Consider adding eye-catching visuals!"
        
        return response
    
    async def _optimize_for_business_context(self, response: str, business_context: Dict[str, Any]) -> str:
        """Optimize response for business context"""
        industry = business_context.get("industry", "")
        focus_area = business_context.get("focus_area", "")
        
        if industry:
            # Add industry-specific insights
            response = f"In the {industry} space, {response.lower()}"
        
        return response
    
    async def _optimize_length(self, response: str, context: ResponseContext) -> str:
        """Optimize response length based on context"""
        preferences = context.preferences.get("response_length_preference", "medium")
        
        words = response.split()
        
        if preferences == "short" and len(words) > 30:
            # Truncate to key points
            response = " ".join(words[:25]) + "..."
        elif preferences == "long" and len(words) < 20:
            # Add elaboration
            response += " I'd be happy to provide more detailed guidance if you'd like!"
        
        return response
    
    async def _analyze_conversation_patterns(self, history: List[Dict[str, Any]], 
                                           preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation history to update preferences"""
        # Analyze response lengths user seems to prefer
        response_lengths = [len(msg.get("content", "").split()) for msg in history if "content" in msg]
        if response_lengths:
            avg_length = sum(response_lengths) / len(response_lengths)
            if avg_length < 15:
                preferences["response_length_preference"] = "short"
            elif avg_length > 40:
                preferences["response_length_preference"] = "long"
            else:
                preferences["response_length_preference"] = "medium"
        
        return preferences

class MultiModalResponseGenerator(BaseResponseGenerator):
    """Generator for multi-modal responses (text + other media suggestions)"""
    
    def __init__(self):
        self.personalized_generator = PersonalizedResponseGenerator()
    
    async def generate(self, context: ResponseContext) -> GeneratedResponse:
        """Generate multi-modal response"""
        # Generate base text response
        base_response = await self.personalized_generator.generate(context)
        
        # Add multi-modal suggestions
        media_suggestions = await self._generate_media_suggestions(context, base_response.content)
        
        # Enhance content with media references
        enhanced_content = await self._enhance_with_media_suggestions(base_response.content, media_suggestions)
        
        # Update metadata
        base_response.content = enhanced_content
        base_response.response_type = ResponseType.MULTIMODAL
        base_response.optimization_applied.append("multimodal_enhancement")
        
        # Add media suggestions to metadata
        if not base_response.alternatives:
            base_response.alternatives = []
        
        for suggestion in media_suggestions:
            base_response.alternatives.append(ResponseCandidate(
                content=suggestion["description"],
                response_type=ResponseType.MULTIMODAL,
                tone=base_response.tone,
                quality_score=0.8,
                personalization_score=0.7,
                relevance_score=0.9,
                creativity_score=0.85,
                metadata={"media_type": suggestion["type"], "media_suggestion": suggestion["suggestion"]}
            ))
        
        return base_response
    
    async def optimize_response(self, response: str, context: ResponseContext) -> str:
        """Optimize response with multi-modal considerations"""
        # First apply standard optimization
        optimized = await self.personalized_generator.optimize_response(response, context)
        
        # Add media integration suggestions
        if context.content_type:
            if context.content_type.lower() in ["video", "youtube"]:
                optimized += " 📹 This would work great as a video tutorial!"
            elif context.content_type.lower() in ["podcast", "audio"]:
                optimized += " 🎙️ Consider turning this into a podcast episode!"
            elif context.content_type.lower() in ["blog", "article"]:
                optimized += " 📝 This could be expanded into a comprehensive blog post!"
        
        return optimized
    
    async def _generate_media_suggestions(self, context: ResponseContext, text_response: str) -> List[Dict[str, Any]]:
        """Generate media suggestions to complement text response"""
        suggestions = []
        
        # Analyze content for media opportunities
        if any(word in text_response.lower() for word in ["visual", "show", "demonstrate", "example"]):
            suggestions.append({
                "type": "image",
                "suggestion": "Create an infographic or visual diagram",
                "description": "A visual representation would enhance this explanation"
            })
        
        if any(word in text_response.lower() for word in ["step", "process", "how to", "tutorial"]):
            suggestions.append({
                "type": "video",
                "suggestion": "Record a step-by-step video tutorial",
                "description": "A video walkthrough would be very helpful here"
            })
        
        if any(word in text_response.lower() for word in ["story", "experience", "journey"]):
            suggestions.append({
                "type": "audio",
                "suggestion": "Share this as a personal story in audio format",
                "description": "Your personal narrative would be engaging as audio content"
            })
        
        return suggestions
    
    async def _enhance_with_media_suggestions(self, content: str, suggestions: List[Dict[str, Any]]) -> str:
        """Enhance text content with subtle media suggestions"""
        if not suggestions:
            return content
        
        # Add subtle suggestions at the end
        if len(suggestions) == 1:
            content += f" ✨ Pro tip: {suggestions[0]['description']}!"
        elif len(suggestions) > 1:
            content += " ✨ You could also enhance this with visuals or video content!"
        
        return content

# A/B Testing Response Engine
class ABTestingResponseEngine:
    """Engine for A/B testing different response strategies"""
    
    def __init__(self):
        self.generators = {
            "personalized": PersonalizedResponseGenerator(),
            "multimodal": MultiModalResponseGenerator()
        }
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.active_tests: Dict[str, Dict[str, Any]] = {}
    
    async def generate_test_responses(self, context: ResponseContext, test_variants: List[str]) -> Dict[str, GeneratedResponse]:
        """Generate responses for A/B testing"""
        responses = {}
        
        for variant in test_variants:
            if variant in self.generators:
                generator = self.generators[variant]
                response = await generator.generate(context)
                responses[variant] = response
        
        return responses
    
    async def record_test_result(self, test_id: str, variant: str, user_feedback: Dict[str, Any]):
        """Record A/B test result"""
        if test_id not in self.test_results:
            self.test_results[test_id] = {}
        
        if variant not in self.test_results[test_id]:
            self.test_results[test_id][variant] = []
        
        self.test_results[test_id][variant].append({
            "feedback": user_feedback,
            "timestamp": datetime.now()
        })
    
    async def get_test_analytics(self, test_id: str) -> Dict[str, Any]:
        """Get analytics for A/B test"""
        if test_id not in self.test_results:
            return {"error": "Test not found"}
        
        analytics = {}
        test_data = self.test_results[test_id]
        
        for variant, results in test_data.items():
            if results:
                satisfaction_scores = [r["feedback"].get("satisfaction", 0) for r in results]
                analytics[variant] = {
                    "total_responses": len(results),
                    "average_satisfaction": sum(satisfaction_scores) / len(satisfaction_scores),
                    "engagement_rate": sum(1 for r in results if r["feedback"].get("engaged", False)) / len(results)
                }
        
        return analytics

# Factory functions
def create_personalized_response_generator() -> PersonalizedResponseGenerator:
    """Create personalized response generator"""
    return PersonalizedResponseGenerator()

def create_template_engine() -> TemplateEngine:
    """Create template engine"""
    return TemplateEngine()

def create_multimodal_response_generator() -> MultiModalResponseGenerator:
    """Create multimodal response generator"""
    return MultiModalResponseGenerator()

def create_ab_testing_response_engine() -> ABTestingResponseEngine:
    """Create A/B testing response engine"""
    return ABTestingResponseEngine()

# Export all classes and functions
__all__ = [
    # Core classes
    "PersonalizedResponseGenerator",
    "TemplateEngine",
    "MultiModalResponseGenerator", 
    "ABTestingResponseEngine",
    "BaseResponseGenerator",
    
    # Data structures
    "ResponseContext",
    "ResponseCandidate",
    "GeneratedResponse",
    "ResponseTemplate",
    "ResponseType",
    "ResponseTone",
    "PersonalizationLevel",
    "ResponseQuality",
    
    # Factory functions
    "create_personalized_response_generator",
    "create_template_engine",
    "create_multimodal_response_generator",
    "create_ab_testing_response_engine"
]