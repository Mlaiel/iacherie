"""Response Engine - Core Response Generation System

Advanced enterprise-grade response generation engine for IA Influencer Agent
with multi-modal support, contextual intelligence, and business optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import time
from datetime import datetime

from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
import uuid

from ...core.exceptions import ResponseGenerationError, ValidationError
from ...core.security import SecurityManager
from ...core.monitoring import MetricsCollector, PerformanceTracker
from ...core.cache import CacheManager


class ResponseType(Enum):
    """Response type enumeration for classification"""
    TEXT = "text"
    AUDIO = "audio"
    VISUAL = "visual"
    MULTIMODAL = "multimodal"
    GUIDANCE = "guidance"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    CONFIRMATION = "confirmation"


class ResponsePriority(Enum):
    """Response priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class ResponseContext(BaseModel):
    """Response context data structure"""
    user_id: str
    session_id: str
    conversation_id: str
    user_type: str = "content_creator"
    content_format: Optional[str] = None
    platform_context: Optional[str] = None
    business_context: Optional[str] = None
    emotional_state: Optional[str] = None
    language_preference: str = "en"
    personalization_profile: Dict[str, Any] = Field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_intent: Optional[str] = None
    urgency_level: ResponsePriority = ResponsePriority.MEDIUM
    
    @validator('user_id', 'session_id', 'conversation_id')
    def validate_ids(cls, v):
        if not v or len(v) < 5:
            raise ValueError("IDs must be valid and non-empty")
        return v


class ResponseRequest(BaseModel):
    """Response generation request structure"""
    context: ResponseContext
    input_text: str = Field(..., min_length=1, max_length=10000)
    response_type: ResponseType = ResponseType.TEXT
    target_length: Optional[int] = None
    style_preferences: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GeneratedResponse(BaseModel):
    """Generated response data structure"""
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    response_type: ResponseType
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generation_time: float
    context_relevance: float = Field(..., ge=0.0, le=1.0)
    personalization_score: float = Field(..., ge=0.0, le=1.0)
    business_alignment: float = Field(..., ge=0.0, le=1.0)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)
    follow_up_actions: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResponseValidator:
    """Advanced response validation and quality assurance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_manager = SecurityManager()
        self.metrics = MetricsCollector()
    
    async def validate_response(
        self, 
        response: str, 
        context: ResponseContext,
        response_type: ResponseType
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Comprehensive response validation
        
        Returns:
            Tuple[bool, Dict]: (is_valid, validation_details)
        """
        try:
            validation_results = {
                "security_check": await self._security_validation(response),
                "content_quality": await self._content_quality_check(response, context),
                "business_alignment": await self._business_alignment_check(response, context),
                "personalization_fit": await self._personalization_validation(response, context),
                "length_validation": self._length_validation(response, response_type),
                "language_validation": await self._language_validation(response, context.language_preference)
            }
            
            overall_score = sum(validation_results.values()) / len(validation_results)
            is_valid = overall_score >= 0.7  # 70% threshold
            
            validation_details = {
                "overall_score": overall_score,
                "individual_scores": validation_results,
                "recommendations": await self._generate_improvement_recommendations(validation_results)
            }
            
            await self.metrics.track_validation(is_valid, overall_score)
            return is_valid, validation_details
            
        except Exception as e:
            self.logger.error(f"Response validation failed: {str(e)}")
            return False, {"error": str(e)}
    
    async def _security_validation(self, response: str) -> float:
        """Security validation for response content"""
        try:
            security_checks = await self.security_manager.validate_content(response)
            return security_checks.get("safety_score", 0.0)
        except Exception:
            return 0.0
    
    async def _content_quality_check(self, response: str, context: ResponseContext) -> float:
        """Content quality assessment"""
        quality_factors = {
            "coherence": self._assess_coherence(response),
            "relevance": self._assess_relevance(response, context),
            "clarity": self._assess_clarity(response),
            "completeness": self._assess_completeness(response, context)
        }
        return sum(quality_factors.values()) / len(quality_factors)
    
    async def _business_alignment_check(self, response: str, context: ResponseContext) -> float:
        """Business logic alignment validation"""
        # Check alignment with content creator workflow
        business_keywords = {
            "monetization": ["revenue", "income", "monetize", "earnings"],
            "protection": ["protect", "copyright", "rights", "security"],
            "collaboration": ["collaborate", "network", "partner", "team"],
            "platform": ["spotify", "youtube", "instagram", "tiktok"]
        }
        
        response_lower = response.lower()
        alignment_score = 0.0
        
        if context.business_context:
            relevant_keywords = business_keywords.get(context.business_context, [])
            matches = sum(1 for keyword in relevant_keywords if keyword in response_lower)
            alignment_score = min(matches / max(len(relevant_keywords), 1), 1.0)
        
        return alignment_score
    
    async def _personalization_validation(self, response: str, context: ResponseContext) -> float:
        """Personalization fit assessment"""
        profile = context.personalization_profile
        if not profile:
            return 0.5  # Neutral score if no profile
        
        # Assess response personalization based on user preferences
        personalization_factors = {
            "tone_match": self._assess_tone_match(response, profile.get("preferred_tone", "professional")),
            "complexity_match": self._assess_complexity_match(response, profile.get("complexity_level", "medium")),
            "format_preference": self._assess_format_preference(response, profile.get("response_format", "detailed"))
        }
        
        return sum(personalization_factors.values()) / len(personalization_factors)
    
    def _length_validation(self, response: str, response_type: ResponseType) -> float:
        """Response length validation based on type"""
        length = len(response)
        
        optimal_ranges = {
            ResponseType.TEXT: (50, 500),
            ResponseType.GUIDANCE: (100, 800),
            ResponseType.RECOMMENDATION: (80, 400),
            ResponseType.ALERT: (20, 200),
            ResponseType.CONFIRMATION: (10, 100)
        }
        
        min_len, max_len = optimal_ranges.get(response_type, (50, 500))
        
        if min_len <= length <= max_len:
            return 1.0
        elif length < min_len:
            return max(0.3, length / min_len)
        else:
            return max(0.3, max_len / length)
    
    async def _language_validation(self, response: str, language: str) -> float:
        """Language quality and consistency validation"""
        # Simplified language validation - in production, use proper NLP tools
        if language == "en":
            return 1.0 if response.isascii() else 0.8
        return 0.9  # Assume good quality for other languages
    
    def _assess_coherence(self, response: str) -> float:
        """Assess response coherence"""
        sentences = response.split('.')
        if len(sentences) < 2:
            return 0.8
        
        # Simple coherence check based on sentence structure
        coherence_score = 1.0
        for sentence in sentences:
            if len(sentence.strip()) < 5:
                coherence_score -= 0.1
        
        return max(0.0, coherence_score)
    
    def _assess_relevance(self, response: str, context: ResponseContext) -> float:
        """Assess response relevance to context"""
        if not context.current_intent:
            return 0.5
        
        intent_keywords = {
            "help": ["help", "assist", "support", "guide"],
            "information": ["information", "data", "details", "explain"],
            "action": ["action", "do", "perform", "execute"],
            "recommendation": ["recommend", "suggest", "advise", "propose"]
        }
        
        response_lower = response.lower()
        relevant_keywords = intent_keywords.get(context.current_intent, [])
        
        if not relevant_keywords:
            return 0.7
        
        matches = sum(1 for keyword in relevant_keywords if keyword in response_lower)
        return min(matches / len(relevant_keywords), 1.0)
    
    def _assess_clarity(self, response: str) -> float:
        """Assess response clarity"""
        # Simple clarity metrics
        avg_sentence_length = len(response.split()) / max(len(response.split('.')), 1)
        
        if 10 <= avg_sentence_length <= 25:
            return 1.0
        elif avg_sentence_length < 10:
            return 0.8
        else:
            return max(0.4, 25 / avg_sentence_length)
    
    def _assess_completeness(self, response: str, context: ResponseContext) -> float:
        """Assess response completeness"""
        # Check if response addresses the main points
        if len(response.split()) < 10:
            return 0.5
        
        return 0.9 if len(response.split()) >= 20 else 0.7
    
    def _assess_tone_match(self, response: str, preferred_tone: str) -> float:
        """Assess tone matching with user preferences"""
        tone_indicators = {
            "professional": ["professional", "business", "formal", "enterprise"],
            "casual": ["casual", "friendly", "relaxed", "informal"],
            "technical": ["technical", "advanced", "detailed", "specific"],
            "encouraging": ["great", "excellent", "amazing", "wonderful"]
        }
        
        response_lower = response.lower()
        indicators = tone_indicators.get(preferred_tone, [])
        
        matches = sum(1 for indicator in indicators if indicator in response_lower)
        return min(matches / max(len(indicators), 1), 1.0) if indicators else 0.5
    
    def _assess_complexity_match(self, response: str, complexity_level: str) -> float:
        """Assess complexity level matching"""
        word_count = len(response.split())
        
        complexity_ranges = {
            "simple": (10, 50),
            "medium": (30, 150),
            "advanced": (80, 300),
            "expert": (100, 500)
        }
        
        min_words, max_words = complexity_ranges.get(complexity_level, (30, 150))
        
        if min_words <= word_count <= max_words:
            return 1.0
        elif word_count < min_words:
            return max(0.4, word_count / min_words)
        else:
            return max(0.4, max_words / word_count)
    
    def _assess_format_preference(self, response: str, format_preference: str) -> float:
        """Assess format preference matching"""
        format_characteristics = {
            "bullet_points": ["•", "-", "*", "1.", "2."],
            "paragraphs": [". ", "\n\n"],
            "detailed": ["specifically", "detailed", "comprehensive"],
            "concise": ["brief", "quick", "summary"]
        }
        
        characteristics = format_characteristics.get(format_preference, [])
        matches = sum(1 for char in characteristics if char in response)
        
        return min(matches / max(len(characteristics), 1), 1.0) if characteristics else 0.7
    
    async def _generate_improvement_recommendations(self, validation_results: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on validation results"""
        recommendations = []
        
        for aspect, score in validation_results.items():
            if score < 0.6:
                if aspect == "security_check":
                    recommendations.append("Enhance content security and safety measures")
                elif aspect == "content_quality":
                    recommendations.append("Improve content coherence and clarity")
                elif aspect == "business_alignment":
                    recommendations.append("Better align response with business objectives")
                elif aspect == "personalization_fit":
                    recommendations.append("Enhance personalization based on user preferences")
                elif aspect == "length_validation":
                    recommendations.append("Adjust response length to optimal range")
                elif aspect == "language_validation":
                    recommendations.append("Improve language quality and consistency")
        
        return recommendations


class ResponseOptimizer:
    """Advanced response optimization engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = CacheManager()
        self.metrics = MetricsCollector()
    
    async def optimize_response(
        self, 
        response: str, 
        context: ResponseContext,
        optimization_goals: Dict[str, float]
    ) -> str:
        """
        Optimize response based on goals and context
        
        Args:
            response: Original response text
            context: Response context
            optimization_goals: Target scores for different aspects
            
        Returns:
            Optimized response text
        """
        try:
            optimization_steps = [
                self._optimize_for_personalization,
                self._optimize_for_business_alignment,
                self._optimize_for_clarity,
                self._optimize_for_engagement,
                self._optimize_for_length
            ]
            
            optimized_response = response
            
            for optimization_step in optimization_steps:
                optimized_response = await optimization_step(
                    optimized_response, 
                    context, 
                    optimization_goals
                )
            
            await self.metrics.track_optimization(response, optimized_response)
            return optimized_response
            
        except Exception as e:
            self.logger.error(f"Response optimization failed: {str(e)}")
            return response  # Return original if optimization fails
    
    async def _optimize_for_personalization(
        self, 
        response: str, 
        context: ResponseContext,
        goals: Dict[str, float]
    ) -> str:
        """Optimize response for personalization"""
        profile = context.personalization_profile
        if not profile:
            return response
        
        # Apply personalization optimizations
        optimizations = []
        
        # Tone optimization
        preferred_tone = profile.get("preferred_tone", "professional")
        if preferred_tone == "casual":
            optimizations.append(self._apply_casual_tone)
        elif preferred_tone == "technical":
            optimizations.append(self._apply_technical_tone)
        
        # Apply optimizations
        optimized = response
        for optimization in optimizations:
            optimized = optimization(optimized)
        
        return optimized
    
    async def _optimize_for_business_alignment(
        self, 
        response: str, 
        context: ResponseContext,
        goals: Dict[str, float]
    ) -> str:
        """Optimize response for business alignment"""
        if not context.business_context:
            return response
        
        business_enhancements = {
            "monetization": " This can help increase your revenue streams.",
            "protection": " This protects your intellectual property.",
            "collaboration": " This opens new collaboration opportunities.",
            "platform": " This optimizes your platform presence."
        }
        
        enhancement = business_enhancements.get(context.business_context, "")
        return response + enhancement
    
    async def _optimize_for_clarity(self, response: str, context: ResponseContext, goals: Dict[str, float]) -> str:
        """Optimize response for clarity"""
        # Simplify complex sentences
        sentences = response.split('.')
        clear_sentences = []
        
        for sentence in sentences:
            if len(sentence.split()) > 30:  # Long sentence
                # Split into shorter sentences (simplified approach)
                parts = sentence.split(',')
                if len(parts) > 2:
                    clear_sentences.extend([part.strip() + '.' for part in parts[:2]])
                    clear_sentences.append(', '.join(parts[2:]) + '.')
                else:
                    clear_sentences.append(sentence + '.')
            else:
                clear_sentences.append(sentence + '.')
        
        return ' '.join(clear_sentences).replace('..', '.')
    
    async def _optimize_for_engagement(self, response: str, context: ResponseContext, goals: Dict[str, float]) -> str:
        """Optimize response for engagement"""
        engagement_phrases = [
            "Here's what I recommend:",
            "Let me help you with that:",
            "This is particularly important for your content:",
            "Based on your creator profile:"
        ]
        
        # Add engaging opening if response doesn't have one
        if not any(phrase in response for phrase in engagement_phrases):
            creator_type = context.user_type.replace('_', ' ')
            engaging_start = f"As a {creator_type}, "
            return engaging_start + response.lower()
        
        return response
    
    async def _optimize_for_length(self, response: str, context: ResponseContext, goals: Dict[str, float]) -> str:
        """Optimize response length"""
        target_length = goals.get("target_length", 200)
        current_length = len(response)
        
        if current_length > target_length * 1.5:
            # Truncate while preserving meaning
            sentences = response.split('.')
            truncated = []
            current_len = 0
            
            for sentence in sentences:
                if current_len + len(sentence) < target_length:
                    truncated.append(sentence)
                    current_len += len(sentence)
                else:
                    break
            
            return '.'.join(truncated) + '.'
        elif current_length < target_length * 0.5:
            # Expand with helpful information
            expansion = " Would you like me to provide more specific guidance on this topic?"
            return response + expansion
        
        return response
    
    def _apply_casual_tone(self, response: str) -> str:
        """Apply casual tone modifications"""
        casual_replacements = {
            "You should": "You might want to",
            "It is recommended": "I'd suggest",
            "Furthermore": "Also",
            "Therefore": "So",
            "Additionally": "Plus"
        }
        
        modified = response
        for formal, casual in casual_replacements.items():
            modified = modified.replace(formal, casual)
        
        return modified
    
    def _apply_technical_tone(self, response: str) -> str:
        """Apply technical tone modifications"""
        technical_enhancements = {
            "use": "utilize",
            "help": "facilitate",
            "make": "generate",
            "get": "obtain",
            "show": "demonstrate"
        }
        
        modified = response
        for simple, technical in technical_enhancements.items():
            modified = modified.replace(f" {simple} ", f" {technical} ")
        
        return modified


class ResponseEngine:
    """Core response generation engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = ResponseValidator()
        self.optimizer = ResponseOptimizer()
        self.cache = CacheManager()
        self.metrics = MetricsCollector()
        self.performance_tracker = PerformanceTracker()
    
    async def generate_response(self, request: ResponseRequest) -> GeneratedResponse:
        """
        Generate optimized response based on request
        
        Args:
            request: Response generation request
            
        Returns:
            Generated response with metadata
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = await self.cache.get(cache_key)
            
            if cached_response:
                await self.metrics.track_cache_hit()
                return GeneratedResponse.parse_obj(cached_response)
            
            # Generate base response
            base_response = await self._generate_base_response(request)
            
            # Validate response
            is_valid, validation_details = await self.validator.validate_response(
                base_response, 
                request.context,
                request.response_type
            )
            
            if not is_valid:
                # Attempt regeneration with improvements
                base_response = await self._regenerate_improved_response(
                    request, 
                    validation_details
                )
            
            # Optimize response
            optimization_goals = self._extract_optimization_goals(request)
            optimized_response = await self.optimizer.optimize_response(
                base_response,
                request.context,
                optimization_goals
            )
            
            # Create final response object
            generation_time = time.time() - start_time
            
            response = GeneratedResponse(
                text=optimized_response,
                response_type=request.response_type,
                confidence_score=validation_details.get("overall_score", 0.8),
                generation_time=generation_time,
                context_relevance=validation_details.get("individual_scores", {}).get("content_quality", 0.8),
                personalization_score=validation_details.get("individual_scores", {}).get("personalization_fit", 0.8),
                business_alignment=validation_details.get("individual_scores", {}).get("business_alignment", 0.8),
                quality_metrics=validation_details.get("individual_scores", {}),
                suggestions=validation_details.get("recommendations", []),
                follow_up_actions=await self._generate_follow_up_actions(request.context),
                metadata={
                    "validation_details": validation_details,
                    "optimization_applied": True,
                    "generation_method": "neural_enhanced",
                    "cache_status": "miss"
                }
            )
            
            # Cache the response
            await self.cache.set(cache_key, response.dict(), expire=3600)
            
            # Track metrics
            await self.metrics.track_response_generation(response)
            await self.performance_tracker.record_generation_time(generation_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {str(e)}")
            raise ResponseGenerationError(f"Failed to generate response: {str(e)}")
    
    async def _generate_base_response(self, request: ResponseRequest) -> str:
        """Generate base response using multiple strategies"""
        strategies = [
            self._neural_generation_strategy,
            self._template_based_strategy,
            self._rule_based_strategy
        ]
        
        # Try strategies in order of preference
        for strategy in strategies:
            try:
                response = await strategy(request)
                if response and len(response.strip()) > 10:
                    return response
            except Exception as e:
                self.logger.warning(f"Strategy failed: {str(e)}")
                continue
        
        # Fallback response
        return await self._fallback_response(request)
    
    async def _neural_generation_strategy(self, request: ResponseRequest) -> str:
        """Neural network-based response generation"""
        # Placeholder for neural generation - would integrate with actual AI models
        prompt = self._construct_neural_prompt(request)
        
        # Simulate neural generation (replace with actual model)
        context = request.context
        input_text = request.input_text
        
        if "help" in input_text.lower():
            if context.user_type == "musician":
                return f"I can help you with your music creation and distribution. Based on your profile, I recommend focusing on {context.content_format or 'audio'} optimization and platform-specific strategies for better reach and monetization."
            elif context.user_type == "influencer":
                return f"As an influencer, I can guide you through content optimization, audience engagement strategies, and monetization opportunities across platforms like {context.platform_context or 'social media'}."
            else:
                return f"I'm here to help you optimize your content creation workflow, protect your intellectual property, and maximize your revenue potential as a {context.user_type.replace('_', ' ')}."
        
        elif "monetization" in input_text.lower() or "revenue" in input_text.lower():
            return f"Let me help you unlock your revenue potential. For {context.user_type.replace('_', ' ')}s, the key monetization strategies include platform-specific optimization, content protection, and strategic collaborations. I can guide you through setting up revenue streams and tracking performance."
        
        elif "protection" in input_text.lower() or "copyright" in input_text.lower():
            return f"Content protection is crucial for your intellectual property. I can help you implement fingerprinting technology, monitor unauthorized usage, and set up automated protection systems for your {context.content_format or 'content'}."
        
        else:
            return f"I understand you're looking for guidance with your {context.content_format or 'content'} creation. As your AI assistant, I can help you optimize workflows, enhance protection, improve monetization, and facilitate collaborations. What specific area would you like to focus on?"
    
    async def _template_based_strategy(self, request: ResponseRequest) -> str:
        """Template-based response generation"""
        templates = {
            "help_request": "I'm here to assist you with {topic}. Based on your {user_type} profile, I recommend {recommendation}. Would you like specific guidance on {area}?",
            "information_request": "Here's what you need to know about {topic}: {information}. This is particularly relevant for {user_type}s working with {content_format}.",
            "monetization_inquiry": "For monetization optimization, I suggest focusing on {strategy}. This can increase your revenue by {benefit}. Let me walk you through the process.",
            "protection_concern": "To protect your {content_format}, I recommend implementing {protection_method}. This will safeguard your intellectual property and ensure proper attribution."
        }
        
        # Select appropriate template based on context
        template_key = self._select_template(request)
        template = templates.get(template_key, templates["help_request"])
        
        # Fill template with context data
        return self._fill_template(template, request)
    
    async def _rule_based_strategy(self, request: ResponseRequest) -> str:
        """Rule-based response generation"""
        input_lower = request.input_text.lower()
        context = request.context
        
        # Business logic rules
        if any(word in input_lower for word in ["upload", "content", "create"]):
            return f"For content upload and creation, I recommend following our optimized workflow: 1) Prepare your {context.content_format or 'content'}, 2) Apply protection fingerprinting, 3) Optimize for SEO, 4) Distribute across platforms, 5) Monitor performance and revenue."
        
        elif any(word in input_lower for word in ["collaborate", "partner", "team"]):
            return f"Collaboration opportunities are key for {context.user_type.replace('_', ' ')}s. I can help you find suitable partners, negotiate terms, and manage collaborative projects. Our platform facilitates secure collaborations with proper revenue sharing."
        
        elif any(word in input_lower for word in ["analytics", "performance", "metrics"]):
            return f"Analytics and performance tracking are essential for optimizing your {context.content_format or 'content'} strategy. I can provide insights on engagement rates, revenue trends, and audience behavior across platforms."
        
        return "I'm ready to help you with your content creation journey. Please let me know what specific area you'd like assistance with."
    
    async def _fallback_response(self, request: ResponseRequest) -> str:
        """Fallback response when other strategies fail"""
        return f"I'm here to help you as a {request.context.user_type.replace('_', ' ')}. While I process your request, please know that I can assist with content creation, protection, monetization, and collaboration strategies. How can I best support your goals today?"
    
    def _construct_neural_prompt(self, request: ResponseRequest) -> str:
        """Construct prompt for neural generation"""
        context = request.context
        prompt_parts = [
            f"You are an AI assistant for {context.user_type.replace('_', ' ')}s.",
            f"User input: {request.input_text}",
            f"Content format: {context.content_format or 'mixed'}",
            f"Platform context: {context.platform_context or 'multi-platform'}",
            f"Business context: {context.business_context or 'general'}",
            "Generate a helpful, personalized response."
        ]
        return " ".join(prompt_parts)
    
    def _select_template(self, request: ResponseRequest) -> str:
        """Select appropriate template based on request analysis"""
        input_lower = request.input_text.lower()
        
        if any(word in input_lower for word in ["help", "assist", "guide"]):
            return "help_request"
        elif any(word in input_lower for word in ["what", "how", "explain", "tell"]):
            return "information_request"
        elif any(word in input_lower for word in ["money", "revenue", "monetize", "earn"]):
            return "monetization_inquiry"
        elif any(word in input_lower for word in ["protect", "copyright", "secure", "safety"]):
            return "protection_concern"
        else:
            return "help_request"
    
    def _fill_template(self, template: str, request: ResponseRequest) -> str:
        """Fill template with contextual information"""
        context = request.context
        
        replacements = {
            "{topic}": self._extract_topic(request.input_text),
            "{user_type}": context.user_type.replace('_', ' '),
            "{content_format}": context.content_format or "content",
            "{platform_context}": context.platform_context or "various platforms",
            "{recommendation}": self._generate_recommendation(context),
            "{area}": self._suggest_focus_area(context),
            "{information}": "relevant insights and strategies",
            "{strategy}": self._suggest_monetization_strategy(context),
            "{benefit}": "optimizing your revenue streams",
            "{protection_method}": "AI-powered fingerprinting and monitoring"
        }
        
        filled_template = template
        for placeholder, value in replacements.items():
            filled_template = filled_template.replace(placeholder, value)
        
        return filled_template
    
    def _extract_topic(self, input_text: str) -> str:
        """Extract main topic from input text"""
        topics = {
            "monetization": ["money", "revenue", "monetize", "earn", "income"],
            "protection": ["protect", "copyright", "secure", "safety", "rights"],
            "collaboration": ["collaborate", "partner", "team", "work together"],
            "analytics": ["analytics", "performance", "metrics", "data", "insights"],
            "upload": ["upload", "publish", "share", "post", "distribute"]
        }
        
        input_lower = input_text.lower()
        for topic, keywords in topics.items():
            if any(keyword in input_lower for keyword in keywords):
                return topic
        
        return "content optimization"
    
    def _generate_recommendation(self, context: ResponseContext) -> str:
        """Generate context-specific recommendation"""
        recommendations = {
            "musician": "focusing on audio quality optimization and multi-platform distribution",
            "influencer": "enhancing content engagement and brand collaboration opportunities",
            "photographer": "protecting image rights and optimizing visual content monetization",
            "comedian": "developing content series and audience building strategies",
            "blogger": "improving SEO optimization and reader engagement tactics"
        }
        
        return recommendations.get(context.user_type, "optimizing your content workflow and protection strategies")
    
    def _suggest_focus_area(self, context: ResponseContext) -> str:
        """Suggest focus area based on context"""
        if context.business_context:
            return context.business_context
        elif context.content_format:
            return f"{context.content_format} optimization"
        else:
            return "workflow optimization"
    
    def _suggest_monetization_strategy(self, context: ResponseContext) -> str:
        """Suggest monetization strategy based on user type"""
        strategies = {
            "musician": "streaming optimization, licensing, and live performance promotion",
            "influencer": "brand partnerships, sponsored content, and affiliate marketing",
            "photographer": "stock licensing, client acquisition, and print sales",
            "comedian": "content series, merchandise, and live show promotion",
            "blogger": "ad revenue optimization, affiliate marketing, and premium content"
        }
        
        return strategies.get(context.user_type, "platform-specific optimization and audience monetization")
    
    async def _regenerate_improved_response(
        self, 
        request: ResponseRequest, 
        validation_details: Dict[str, Any]
    ) -> str:
        """Regenerate response with improvements based on validation feedback"""
        improvements = validation_details.get("recommendations", [])
        
        # Apply specific improvements
        improved_request = request.copy(deep=True)
        
        # Adjust request based on validation feedback
        if "Enhance personalization" in str(improvements):
            improved_request.style_preferences["personalization_weight"] = 1.5
        
        if "Better align response with business objectives" in str(improvements):
            improved_request.style_preferences["business_focus"] = True
        
        if "Improve content coherence and clarity" in str(improvements):
            improved_request.style_preferences["clarity_focus"] = True
        
        # Generate improved response
        return await self._generate_base_response(improved_request)
    
    def _extract_optimization_goals(self, request: ResponseRequest) -> Dict[str, float]:
        """Extract optimization goals from request"""
        goals = {
            "personalization": 0.8,
            "business_alignment": 0.7,
            "clarity": 0.9,
            "engagement": 0.8,
            "target_length": request.target_length or 200
        }
        
        # Adjust goals based on request specifics
        if request.context.urgency_level == ResponsePriority.CRITICAL:
            goals["clarity"] = 1.0
            goals["target_length"] = min(goals["target_length"], 150)
        
        return goals
    
    async def _generate_follow_up_actions(self, context: ResponseContext) -> List[Dict[str, Any]]:
        """Generate relevant follow-up actions"""
        actions = []
        
        # Business context-based actions
        if context.business_context == "monetization":
            actions.append({
                "action": "setup_revenue_tracking",
                "description": "Set up automated revenue tracking",
                "priority": "medium"
            })
        
        elif context.business_context == "protection":
            actions.append({
                "action": "enable_content_protection",
                "description": "Enable AI-powered content protection",
                "priority": "high"
            })
        
        # User type-based actions
        if context.user_type == "musician":
            actions.append({
                "action": "optimize_audio_distribution",
                "description": "Optimize audio for multi-platform distribution",
                "priority": "medium"
            })
        
        # General actions
        actions.append({
            "action": "review_analytics",
            "description": "Review your content performance analytics",
            "priority": "low"
        })
        
        return actions
    
    def _generate_cache_key(self, request: ResponseRequest) -> str:
        """Generate cache key for request"""
        key_components = [
            request.input_text[:100],  # First 100 chars of input
            request.context.user_type,
            request.context.content_format or "none",
            request.context.business_context or "none",
            str(request.response_type.value),
            request.context.language_preference
        ]
        
        return f"response:{hash('|'.join(key_components))}"


class ResponseOrchestrator:
    """High-level response orchestration and coordination"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.response_engine = ResponseEngine()
        self.metrics = MetricsCollector()
    
    async def process_conversation_request(
        self, 
        user_input: str,
        user_id: str,
        session_id: str,
        conversation_id: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> GeneratedResponse:
        """
        Process a complete conversation request with context building
        
        Args:
            user_input: User's input text
            user_id: User identifier
            session_id: Session identifier
            conversation_id: Conversation identifier
            additional_context: Additional context information
            
        Returns:
            Generated response
        """
        try:
            # Build comprehensive context
            context = await self._build_conversation_context(
                user_id, session_id, conversation_id, additional_context
            )
            
            # Create response request
            request = ResponseRequest(
                context=context,
                input_text=user_input,
                response_type=await self._determine_response_type(user_input, context),
                target_length=await self._determine_target_length(context),
                style_preferences=await self._determine_style_preferences(context),
                constraints=await self._determine_constraints(context),
                metadata={"orchestrator_version": "1.0"}
            )
            
            # Generate response
            response = await self.response_engine.generate_response(request)
            
            # Post-process and enhance
            enhanced_response = await self._enhance_response(response, context)
            
            # Track conversation metrics
            await self.metrics.track_conversation_interaction(
                user_id, session_id, user_input, enhanced_response.text
            )
            
            return enhanced_response
            
        except Exception as e:
            self.logger.error(f"Conversation request processing failed: {str(e)}")
            raise ResponseGenerationError(f"Failed to process conversation request: {str(e)}")
    
    async def _build_conversation_context(
        self,
        user_id: str,
        session_id: str, 
        conversation_id: str,
        additional_context: Optional[Dict[str, Any]]
    ) -> ResponseContext:
        """Build comprehensive conversation context"""
        
        # Get user profile (placeholder - would fetch from database)
        user_profile = await self._get_user_profile(user_id)
        
        # Get conversation history
        conversation_history = await self._get_conversation_history(conversation_id)
        
        # Build context
        context = ResponseContext(
            user_id=user_id,
            session_id=session_id,
            conversation_id=conversation_id,
            user_type=user_profile.get("user_type", "content_creator"),
            content_format=user_profile.get("primary_content_format"),
            platform_context=user_profile.get("primary_platform"),
            business_context=additional_context.get("business_context") if additional_context else None,
            emotional_state=additional_context.get("emotional_state") if additional_context else None,
            language_preference=user_profile.get("language_preference", "en"),
            personalization_profile=user_profile.get("personalization_profile", {}),
            conversation_history=conversation_history,
            current_intent=additional_context.get("detected_intent") if additional_context else None,
            urgency_level=ResponsePriority(additional_context.get("urgency_level", "medium")) if additional_context else ResponsePriority.MEDIUM
        )
        
        return context
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile from database"""
        # Placeholder implementation - would fetch from actual database
        return {
            "user_type": "musician",
            "primary_content_format": "audio",
            "primary_platform": "spotify",
            "language_preference": "en",
            "personalization_profile": {
                "preferred_tone": "professional",
                "complexity_level": "medium",
                "response_format": "detailed"
            }
        }
    
    async def _get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history from database"""
        # Placeholder implementation - would fetch from actual database
        return []
    
    async def _determine_response_type(self, user_input: str, context: ResponseContext) -> ResponseType:
        """Determine appropriate response type"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["alert", "warning", "urgent", "critical"]):
            return ResponseType.ALERT
        elif any(word in input_lower for word in ["recommend", "suggest", "advice", "should"]):
            return ResponseType.RECOMMENDATION
        elif any(word in input_lower for word in ["guide", "help", "how to", "tutorial"]):
            return ResponseType.GUIDANCE
        elif any(word in input_lower for word in ["confirm", "yes", "no", "agree"]):
            return ResponseType.CONFIRMATION
        else:
            return ResponseType.TEXT
    
    async def _determine_target_length(self, context: ResponseContext) -> int:
        """Determine target response length"""
        if context.urgency_level == ResponsePriority.CRITICAL:
            return 100
        elif context.urgency_level == ResponsePriority.HIGH:
            return 150
        else:
            complexity = context.personalization_profile.get("complexity_level", "medium")
            return {"simple": 100, "medium": 200, "advanced": 300, "expert": 400}.get(complexity, 200)
    
    async def _determine_style_preferences(self, context: ResponseContext) -> Dict[str, Any]:
        """Determine style preferences from context"""
        profile = context.personalization_profile
        return {
            "tone": profile.get("preferred_tone", "professional"),
            "complexity": profile.get("complexity_level", "medium"),
            "format": profile.get("response_format", "detailed"),
            "personalization_weight": 1.0,
            "business_focus": bool(context.business_context),
            "clarity_focus": True
        }
    
    async def _determine_constraints(self, context: ResponseContext) -> Dict[str, Any]:
        """Determine response constraints"""
        constraints = {
            "max_length": 1000,
            "min_length": 20,
            "language": context.language_preference,
            "content_safety": True
        }
        
        if context.urgency_level == ResponsePriority.CRITICAL:
            constraints["max_length"] = 200
            constraints["response_time_limit"] = 1.0  # seconds
        
        return constraints
    
    async def _enhance_response(self, response: GeneratedResponse, context: ResponseContext) -> GeneratedResponse:
        """Enhance response with additional features"""
        # Add context-specific enhancements
        enhanced_text = response.text
        
        # Add personalized greeting if appropriate
        if not any(greeting in enhanced_text.lower() for greeting in ["hello", "hi", "welcome"]):
            user_type = context.user_type.replace('_', ' ')
            enhanced_text = f"Hello! As your AI assistant for {user_type}s, {enhanced_text.lower()}"
        
        # Add call-to-action based on business context
        if context.business_context and not enhanced_text.endswith('?'):
            cta_map = {
                "monetization": " Would you like me to help you set up revenue tracking?",
                "protection": " Shall I guide you through enabling content protection?",
                "collaboration": " Would you like to explore collaboration opportunities?",
                "platform": " Should we optimize your platform-specific strategy?"
            }
            cta = cta_map.get(context.business_context, "")
            enhanced_text += cta
        
        # Update response object
        response.text = enhanced_text
        response.metadata["enhanced"] = True
        response.metadata["enhancement_applied"] = ["personalized_greeting", "business_cta"]
        
        return response


# Export main classes
__all__ = [
    "ResponseEngine",
    "ResponseOrchestrator", 
    "ResponseGenerator",
    "ResponseValidator",
    "ResponseOptimizer",
    "ResponseType",
    "ResponsePriority",
    "ResponseContext",
    "ResponseRequest", 
    "GeneratedResponse"
]
