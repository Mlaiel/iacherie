"""Conversation Localizer - Advanced Multilingual Conversation Management

Enterprise-grade conversation localization system providing real-time
message translation, response localization, and template management
for seamless multilingual content creator interactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE ⚠️
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import re
from collections import defaultdict

# Caching and storage
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

# Internal imports
from .language_manager import SupportedLanguage, LanguageManager
from .translation_engine import TranslationEngine, TranslationRequest, TranslationResult
from .cultural_adaptor import CulturalAdaptor, CulturalContext, AdaptationResult

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in conversations"""    USER_MESSAGE = "user_message"
    SYSTEM_RESPONSE = "system_response"
    NOTIFICATION = "notification"
    ERROR_MESSAGE = "error_message"
    GREETING = "greeting"
    FAREWELL = "farewell"
    CONFIRMATION = "confirmation"
    QUESTION = "question"
    INSTRUCTION = "instruction"
    FEEDBACK = "feedback"


class LocalizationLevel(Enum):
    """Levels of localization to apply"""    BASIC = "basic"          # Translation only
    STANDARD = "standard"    # Translation + basic cultural adaptation
    ADVANCED = "advanced"    # Full cultural adaptation + regional customization
    PREMIUM = "premium"      # Advanced + context-aware personalization


@dataclass
class ConversationContext:
    """Context information for conversation localization"""    user_id: str
    session_id: str
    conversation_id: str
    primary_language: SupportedLanguage
    target_language: SupportedLanguage
    cultural_context: Optional[CulturalContext] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    domain: str = "general"
    formality_level: str = "neutral"
    urgency_level: str = "normal"
    relationship_stage: str = "new"  # new, established, familiar
    preferred_style: str = "professional"
    localization_level: LocalizationLevel = LocalizationLevel.STANDARD
    context_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LocalizedMessage:
    """Localized message with metadata"""    original_text: str
    localized_text: str
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    message_type: MessageType
    localization_applied: List[str] = field(default_factory=list)
    cultural_adaptations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TemplateData:
    """Template data for localized responses"""    template_id: str
    template_category: str
    original_template: str
    localized_versions: Dict[str, str] = field(default_factory=dict)
    variables: List[str] = field(default_factory=list)
    context_requirements: List[str] = field(default_factory=list)
    cultural_variations: Dict[str, str] = field(default_factory=dict)
    usage_count: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MessageLocalizer:
    """Advanced message localization with context awareness"""    
    def __init__(
        self,
        translation_engine: TranslationEngine,
        cultural_adaptor: CulturalAdaptor,
        redis_client: aioredis.Redis
    ):
        self.translation_engine = translation_engine
        self.cultural_adaptor = cultural_adaptor
        self.redis_client = redis_client
        self.localization_stats = defaultdict(int)
        
        # Message type specific handling
        self.message_handlers = {
            MessageType.GREETING: self._handle_greeting_message,
            MessageType.FAREWELL: self._handle_farewell_message,
            MessageType.ERROR_MESSAGE: self._handle_error_message,
            MessageType.CONFIRMATION: self._handle_confirmation_message,
            MessageType.QUESTION: self._handle_question_message,
            MessageType.INSTRUCTION: self._handle_instruction_message,
            MessageType.FEEDBACK: self._handle_feedback_message
        }
    
    async def localize_message(
        self,
        message: str,
        message_type: MessageType,
        conversation_context: ConversationContext
    ) -> LocalizedMessage:
        """        Localize a message with full cultural adaptation
        """        start_time = datetime.now()
        
        try:
            # Check if localization is needed
            if conversation_context.primary_language == conversation_context.target_language:
                return LocalizedMessage(
                    original_text=message,
                    localized_text=message,
                    source_language=conversation_context.primary_language,
                    target_language=conversation_context.target_language,
                    message_type=message_type,
                    confidence_score=1.0,
                    processing_time=0.0
                )
            
            # Apply message type specific preprocessing
            preprocessed_message = await self._preprocess_message(
                message, 
                message_type, 
                conversation_context
            )
            
            # Perform translation
            translation_request = TranslationRequest(
                text=preprocessed_message,
                source_language=conversation_context.primary_language,
                target_language=conversation_context.target_language,
                domain=conversation_context.domain,
                formality=conversation_context.formality_level,
                tone=conversation_context.preferred_style,
                context=self._build_translation_context(conversation_context),
                user_id=conversation_context.user_id
            )
            
            translation_result = await self.translation_engine.translate(translation_request)
            
            localized_text = translation_result.translated_text
            adaptations_applied = []
            cultural_adaptations = []
            
            # Apply cultural adaptation if enabled
            if conversation_context.localization_level != LocalizationLevel.BASIC:
                adaptation_result = await self.cultural_adaptor.adapt_content(
                    localized_text,
                    conversation_context.target_language,
                    conversation_context.cultural_context.country_code if conversation_context.cultural_context else None,
                    context_type=conversation_context.domain
                )
                
                localized_text = adaptation_result.adapted_content
                cultural_adaptations = adaptation_result.adaptations_applied
            
            # Apply message type specific postprocessing
            localized_text, type_adaptations = await self._postprocess_message(
                localized_text,
                message_type,
                conversation_context
            )
            adaptations_applied.extend(type_adaptations)
            
            # Apply conversation context adaptations
            if conversation_context.localization_level in [LocalizationLevel.ADVANCED, LocalizationLevel.PREMIUM]:
                localized_text, context_adaptations = await self._apply_conversation_context(
                    localized_text,
                    conversation_context
                )
                adaptations_applied.extend(context_adaptations)
            
            # Calculate confidence score
            confidence_score = self._calculate_localization_confidence(
                translation_result,
                conversation_context
            )
            
            # Update statistics
            self.localization_stats[f"{message_type.value}_{conversation_context.target_language.value}"] += 1
            self.localization_stats["total_localizations"] += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return LocalizedMessage(
                original_text=message,
                localized_text=localized_text,
                source_language=conversation_context.primary_language,
                target_language=conversation_context.target_language,
                message_type=message_type,
                localization_applied=adaptations_applied,
                cultural_adaptations=cultural_adaptations,
                confidence_score=confidence_score,
                processing_time=processing_time,
                warnings=translation_result.warnings,
                metadata={
                    "localization_level": conversation_context.localization_level.value,
                    "domain": conversation_context.domain,
                    "translation_provider": translation_result.provider_used.value
                }
            )
            
        except Exception as e:
            logger.error(f"Message localization failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return LocalizedMessage(
                original_text=message,
                localized_text=message,  # Fallback to original
                source_language=conversation_context.primary_language,
                target_language=conversation_context.target_language,
                message_type=message_type,
                confidence_score=0.0,
                processing_time=processing_time,
                warnings=[f"Localization failed: {str(e)}"]
            )
    
    async def _preprocess_message(
        self,
        message: str,
        message_type: MessageType,
        context: ConversationContext
    ) -> str:
        """Preprocess message before translation"""        preprocessed = message
        
        # Handle message type specific preprocessing
        if message_type in self.message_handlers:
            preprocessed = await self.message_handlers[message_type](
                preprocessed, 
                context, 
                "preprocess"
            )
        
        # Clean and normalize text
        preprocessed = self._clean_message_text(preprocessed)
        
        return preprocessed
    
    async def _postprocess_message(
        self,
        message: str,
        message_type: MessageType,
        context: ConversationContext
    ) -> Tuple[str, List[str]]:
        """Postprocess message after translation"""        postprocessed = message
        adaptations = []
        
        # Handle message type specific postprocessing
        if message_type in self.message_handlers:
            postprocessed = await self.message_handlers[message_type](
                postprocessed, 
                context, 
                "postprocess"
            )
            adaptations.append(f"message_type_handling: {message_type.value}")
        
        return postprocessed, adaptations
    
    async def _apply_conversation_context(
        self,
        message: str,
        context: ConversationContext
    ) -> Tuple[str, List[str]]:
        """Apply conversation-specific context adaptations"""        adaptations = []
        adapted_message = message
        
        # Relationship stage adaptations
        if context.relationship_stage == "new":
            # Add more formal introductory elements
            if not any(greeting in adapted_message.lower() for greeting in ["hello", "hi", "dear"]):
                adapted_message = f"Hello, {adapted_message}"
                adaptations.append("context: added greeting for new relationship")
        
        elif context.relationship_stage == "familiar":
            # Use more casual tone
            adapted_message = re.sub(r"\bDear\b", "Hi", adapted_message)
            if "Dear" in message:
                adaptations.append("context: casual tone for familiar relationship")
        
        # Urgency level adaptations
        if context.urgency_level == "high":
            if not any(urgency in adapted_message.lower() for urgency in ["urgent", "important", "asap"]):
                adapted_message = f"[Important] {adapted_message}"
                adaptations.append("context: added urgency indicator")
        
        # Domain-specific adaptations
        if context.domain == "customer_support":
            if "problem" in adapted_message.lower():
                adapted_message = adapted_message.replace("problem", "issue")
                adaptations.append("context: customer support terminology")
        
        return adapted_message, adaptations
    
    def _build_translation_context(self, conversation_context: ConversationContext) -> str:
        """Build context string for translation"""        context_parts = []
        
        if conversation_context.domain != "general":
            context_parts.append(f"Domain: {conversation_context.domain}")
        
        if conversation_context.relationship_stage != "new":
            context_parts.append(f"Relationship: {conversation_context.relationship_stage}")
        
        if conversation_context.conversation_history:
            # Include recent context
            recent_messages = conversation_context.conversation_history[-3:]
            context_parts.append(f"Recent context: {len(recent_messages)} messages")
        
        return " | ".join(context_parts) if context_parts else None
    
    def _calculate_localization_confidence(
        self,
        translation_result: TranslationResult,
        context: ConversationContext
    ) -> float:
        """Calculate overall localization confidence"""        base_confidence = translation_result.confidence_score
        
        # Adjust based on localization level
        level_adjustment = {
            LocalizationLevel.BASIC: 0.0,
            LocalizationLevel.STANDARD: 0.1,
            LocalizationLevel.ADVANCED: 0.15,
            LocalizationLevel.PREMIUM: 0.2
        }
        
        confidence = base_confidence + level_adjustment.get(context.localization_level, 0.0)
        
        # Adjust based on cultural context availability
        if context.cultural_context:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _clean_message_text(self, text: str) -> str:
        """Clean and normalize message text"""        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize quotes
        text = re.sub(r'[""]', '"', text)
        text = re.sub(r'['']', "'", text)
        
        return text.strip()
    
    # Message type specific handlers
    async def _handle_greeting_message(
        self, 
        message: str, 
        context: ConversationContext, 
        phase: str
    ) -> str:
        """Handle greeting messages"""        if phase == "postprocess" and context.cultural_context:
            # Add culturally appropriate greetings
            if context.cultural_context.language == SupportedLanguage.JAPANESE:
                if "hello" in message.lower():
                    return message.replace("Hello", "こんにちは")
            elif context.cultural_context.language == SupportedLanguage.GERMAN:
                if "hello" in message.lower():
                    return message.replace("Hello", "Guten Tag")
        
        return message
    
    async def _handle_farewell_message(
        self, 
        message: str, 
        context: ConversationContext, 
        phase: str
    ) -> str:
        """Handle farewell messages"""        if phase == "postprocess" and context.cultural_context:
            # Add culturally appropriate farewells
            if context.cultural_context.formality_preference > 0.7:
                message = re.sub(r"\bbye\b", "goodbye", message, flags=re.IGNORECASE)
        
        return message
    
    async def _handle_error_message(
        self, 
        message: str, 
        context: ConversationContext, 
        phase: str
    ) -> str:
        """Handle error messages"""        if phase == "postprocess" and context.cultural_context:
            # Soften error messages for high-context cultures
            if context.cultural_context.directness_level < 0.4:
                message = re.sub(r"Error:", "We encountered an issue:", message)
                message = re.sub(r"Failed", "Was unable to complete", message)
        
        return message
    
    async def _handle_confirmation_message(
        self, 
        message: str, 
        context: ConversationContext, 
        phase: str
    ) -> str:
        """Handle confirmation messages"""        if phase == "postprocess" and context.cultural_context:
            # Adjust confirmation style based on culture
            if context.cultural_context.formality_preference > 0.7:
                message = re.sub(r"\bOK\b", "Confirmed", message)
                message = re.sub(r"\bSure\b", "Certainly", message)
        
        return message
    
    async def _handle_question_message(
        self, 
        message: str, 
        context: ConversationContext, 
        phase: str
    ) -> str:
        """Handle question messages"""        if phase == "postprocess" and context.cultural_context:
            # Soften questions for indirect cultures
            if context.cultural_context.directness_level < 0.4:
                if message.startswith("What"):
                    message = "Could you please tell me " + message[4:].lower()
                elif message.startswith("How"):
                    message = "I was wondering " + message.lower()
        
        return message
    
    async def _handle_instruction_message(
        self, 
        message: str, 
        context: ConversationContext, 
        phase: str
    ) -> str:
        """Handle instruction messages"""        if phase == "postprocess" and context.cultural_context:
            # Soften instructions for indirect cultures
            if context.cultural_context.directness_level < 0.4:
                message = re.sub(r"^You must", "Please", message)
                message = re.sub(r"^You should", "It would be helpful if you", message)
        
        return message
    
    async def _handle_feedback_message(
        self, 
        message: str, 
        context: ConversationContext, 
        phase: str
    ) -> str:
        """Handle feedback messages"""        if phase == "postprocess" and context.cultural_context:
            # Adjust feedback style based on culture
            if context.cultural_context.language == SupportedLanguage.JAPANESE:
                # Add appropriate honorifics and softening
                if "good" in message.lower():
                    message = message.replace("good", "very good")
        
        return message


class ResponseLocalizer:
    """Specialized response localization for system responses"""    
    def __init__(
        self,
        message_localizer: MessageLocalizer,
        redis_client: aioredis.Redis
    ):
        self.message_localizer = message_localizer
        self.redis_client = redis_client
        self.response_cache = {}
        
    async def localize_response(
        self,
        response_content: str,
        response_type: str,
        conversation_context: ConversationContext,
        variables: Optional[Dict[str, Any]] = None
    ) -> LocalizedMessage:
        """Localize system response with variable substitution"""        try:
            # Substitute variables if provided
            if variables:
                response_content = await self._substitute_variables(
                    response_content,
                    variables,
                    conversation_context
                )
            
            # Determine message type from response type
            message_type = self._determine_message_type(response_type)
            
            # Localize using message localizer
            localized_message = await self.message_localizer.localize_message(
                response_content,
                message_type,
                conversation_context
            )
            
            # Apply response-specific enhancements
            enhanced_text = await self._enhance_response(
                localized_message.localized_text,
                response_type,
                conversation_context
            )
            
            localized_message.localized_text = enhanced_text
            
            return localized_message
            
        except Exception as e:
            logger.error(f"Response localization failed: {e}")
            # Return basic localized version
            return await self.message_localizer.localize_message(
                response_content,
                MessageType.SYSTEM_RESPONSE,
                conversation_context
            )
    
    async def _substitute_variables(
        self,
        content: str,
        variables: Dict[str, Any],
        context: ConversationContext
    ) -> str:
        """Substitute variables with localized values"""        substituted_content = content
        
        for var_name, value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in substituted_content:
                # Localize the value if needed
                localized_value = await self._localize_variable_value(
                    value,
                    var_name,
                    context
                )
                substituted_content = substituted_content.replace(
                    placeholder,
                    str(localized_value)
                )
        
        return substituted_content
    
    async def _localize_variable_value(
        self,
        value: Any,
        var_name: str,
        context: ConversationContext
    ) -> Any:
        """Localize individual variable values"""        if isinstance(value, datetime):
            # Localize datetime
            if context.cultural_context:
                return value.strftime(context.cultural_context.datetime_format)
            return value.strftime("%Y-%m-%d %H:%M")
        
        elif isinstance(value, (int, float)) and "amount" in var_name.lower():
            # Localize currency/number
            if context.cultural_context:
                if context.cultural_context.number_decimal_separator == ",":
                    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"{value:,.2f}"
        
        return value
    
    def _determine_message_type(self, response_type: str) -> MessageType:
        """Determine message type from response type"""        type_mapping = {
            "greeting": MessageType.GREETING,
            "farewell": MessageType.FAREWELL,
            "error": MessageType.ERROR_MESSAGE,
            "confirmation": MessageType.CONFIRMATION,
            "question": MessageType.QUESTION,
            "instruction": MessageType.INSTRUCTION,
            "feedback": MessageType.FEEDBACK,
            "notification": MessageType.NOTIFICATION
        }
        
        return type_mapping.get(response_type, MessageType.SYSTEM_RESPONSE)
    
    async def _enhance_response(
        self,
        response: str,
        response_type: str,
        context: ConversationContext
    ) -> str:
        """Apply response-type specific enhancements"""        enhanced = response
        
        if response_type == "success_confirmation":
            # Add positive reinforcement
            if context.cultural_context and context.cultural_context.indulgence > 0.7:
                enhanced = f"✓ {enhanced}"
        
        elif response_type == "error_message":
            # Add empathy for relationship-focused cultures
            if context.cultural_context and context.cultural_context.relationship_focus > 0.7:
                enhanced = f"We apologize for the inconvenience. {enhanced}"
        
        return enhanced


class TemplateLocalizer:
    """Advanced template localization with caching"""    
    def __init__(self, redis_client: aioredis.Redis, db_session: AsyncSession):
        self.redis_client = redis_client
        self.db_session = db_session
        self.template_cache = {}
        
    async def localize_template(
        self,
        template_id: str,
        target_language: SupportedLanguage,
        variables: Optional[Dict[str, Any]] = None,
        cultural_context: Optional[CulturalContext] = None
    ) -> str:
        """Localize template with variables and cultural adaptation"""        try:
            # Get localized template
            localized_template = await self._get_localized_template(
                template_id,
                target_language
            )
            
            if not localized_template:
                logger.warning(f"Template {template_id} not found for {target_language.value}")
                return ""
            
            # Substitute variables
            if variables:
                localized_template = await self._substitute_template_variables(
                    localized_template,
                    variables,
                    cultural_context
                )
            
            # Apply cultural adaptations
            if cultural_context:
                # This would apply template-specific cultural adaptations
                pass
            
            return localized_template
            
        except Exception as e:
            logger.error(f"Template localization failed: {e}")
            return ""
    
    async def _get_localized_template(
        self,
        template_id: str,
        target_language: SupportedLanguage
    ) -> Optional[str]:
        """Get localized template from cache or database"""        cache_key = f"template:{template_id}:{target_language.value}"
        
        # Check cache
        cached_template = await self.redis_client.get(cache_key)
        if cached_template:
            return cached_template.decode('utf-8')
        
        # Load from database with professional implementation
        try:
            # Query database for localized template
            async with self.session_factory() as session:
                query = """                    SELECT localized_content 
                    FROM conversation_templates 
                    WHERE template_id = $1 AND language_code = $2 AND is_active = true
                    ORDER BY version DESC 
                    LIMIT 1
                """                result = await session.execute(query, [template_id, target_language.value])
                row = result.fetchone()
                
                if row:
                    template_content = row[0]
                    # Cache for future use
                    await self.redis_client.setex(
                        cache_key, 
                        3600,  # 1 hour cache
                        template_content.encode('utf-8')
                    )
                    return template_content
                    
        except Exception as e:
            logger.warning(f"Database template lookup failed: {e}")
            
        # Fallback: generate template using translation engine
        default_template = await self._generate_fallback_template(template_id, target_language)
        if default_template:
            await self.redis_client.setex(cache_key, 1800, default_template.encode('utf-8'))
            
        return default_template
    
    async def _substitute_template_variables(
        self,
        template: str,
        variables: Dict[str, Any],
        cultural_context: Optional[CulturalContext]
    ) -> str:
        """Substitute variables in template with cultural formatting"""        substituted = template
        
        for var_name, value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in substituted:
                # Format value according to cultural context
                formatted_value = await self._format_template_value(
                    value,
                    var_name,
                    cultural_context
                )
                substituted = substituted.replace(placeholder, str(formatted_value))
        
        return substituted
    
    async def _format_template_value(
        self,
        value: Any,
        var_name: str,
        cultural_context: Optional[CulturalContext]
    ) -> str:
        """Format template value according to cultural context"""        if isinstance(value, datetime) and cultural_context:
            return value.strftime(cultural_context.datetime_format)
        elif isinstance(value, (int, float)) and "amount" in var_name and cultural_context:
            return f"{cultural_context.currency_symbol}{value:,.2f}"
        
        return str(value)


class LocalizedResponseGenerator:
    """High-level localized response generation"""    
    def __init__(
        self,
        message_localizer: MessageLocalizer,
        response_localizer: ResponseLocalizer,
        template_localizer: TemplateLocalizer
    ):
        self.message_localizer = message_localizer
        self.response_localizer = response_localizer
        self.template_localizer = template_localizer
    
    async def generate_localized_response(
        self,
        response_template_id: Optional[str],
        content: str,
        conversation_context: ConversationContext,
        variables: Optional[Dict[str, Any]] = None
    ) -> LocalizedMessage:
        """Generate complete localized response"""        try:
            # Use template if provided
            if response_template_id:
                template_content = await self.template_localizer.localize_template(
                    response_template_id,
                    conversation_context.target_language,
                    variables,
                    conversation_context.cultural_context
                )
                if template_content:
                    content = template_content
            
            # Localize the response
            localized_response = await self.response_localizer.localize_response(
                content,
                "system_response",
                conversation_context,
                variables
            )
            
            return localized_response
            
        except Exception as e:
            logger.error(f"Localized response generation failed: {e}")
            # Fallback to basic message localization
            return await self.message_localizer.localize_message(
                content,
                MessageType.SYSTEM_RESPONSE,
                conversation_context
            )


class ConversationLocalizer:
    """Master conversation localization orchestrator"""    
    def __init__(
        self,
        language_manager: LanguageManager,
        translation_engine: TranslationEngine,
        cultural_adaptor: CulturalAdaptor,
        redis_client: aioredis.Redis,
        db_session: AsyncSession
    ):
        self.language_manager = language_manager
        self.translation_engine = translation_engine
        self.cultural_adaptor = cultural_adaptor
        self.redis_client = redis_client
        self.db_session = db_session
        
        # Initialize sub-components
        self.message_localizer = MessageLocalizer(
            translation_engine,
            cultural_adaptor,
            redis_client
        )
        
        self.response_localizer = ResponseLocalizer(
            self.message_localizer,
            redis_client
        )
        
        self.template_localizer = TemplateLocalizer(
            redis_client,
            db_session
        )
        
        self.response_generator = LocalizedResponseGenerator(
            self.message_localizer,
            self.response_localizer,
            self.template_localizer
        )
    
    async def create_conversation_context(
        self,
        user_id: str,
        session_id: str,
        conversation_id: str,
        target_language: SupportedLanguage,
        **kwargs
    ) -> ConversationContext:
        """Create comprehensive conversation context"""        try:
            # Get user language context
            user_context = await self.language_manager.get_user_language_context(user_id)
            
            # Get cultural context
            cultural_context = None
            if user_context.get("profile"):
                profile = user_context["profile"]
                cultural_context = await self.cultural_adaptor._get_cultural_context(
                    target_language,
                    profile.country_code
                )
            
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                conversation_id=conversation_id,
                primary_language=user_context.get("profile", {}).get("primary_language", SupportedLanguage.ENGLISH),
                target_language=target_language,
                cultural_context=cultural_context
            )
            
            # Apply additional parameters
            for key, value in kwargs.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to create conversation context: {e}")
            # Return basic context
            return ConversationContext(
                user_id=user_id,
                session_id=session_id,
                conversation_id=conversation_id,
                primary_language=SupportedLanguage.ENGLISH,
                target_language=target_language
            )
    
    async def _generate_fallback_template(self, template_id: str, target_language: SupportedLanguage) -> Optional[str]:
        """Generate fallback template when database lookup fails."""        try:
            # Define common templates for content creators
            default_templates = {
                "welcome_creator": "Welcome to IA Influencer Agent! How can I help you create amazing content today?",
                "content_protection": "Your content is now protected with our advanced AI fingerprinting technology.",
                "collaboration_match": "We found potential collaboration opportunities for your content!",
                "monetization_update": "Your content has generated new revenue opportunities.",
                "music_recommendation": "Based on your style, here are some music creation suggestions.",
                "seo_optimization": "Your content has been optimized for better discoverability.",
                "analytics_summary": "Here's your content performance summary.",
                "rights_protection": "Your intellectual property rights are being monitored and protected."
            }
            
            base_template = default_templates.get(template_id, "Hello! How can I assist you today?")
            
            # Use translation engine for localization
            if hasattr(self, 'translation_engine'):
                from .translation_engine import TranslationRequest
                
                request = TranslationRequest(
                    text=base_template,
                    source_language=SupportedLanguage.ENGLISH,
                    target_language=target_language,
                    context="content_creator_communication"
                )
                
                result = await self.translation_engine.translate(request)
                return result.translated_text
                
            return base_template
            
        except Exception as e:
            logger.error(f"Fallback template generation failed: {e}")
            return "Hello! How can I help you?"

    async def process_conversation_turn(
        self,
        user_message: str,
        system_response: str,
        conversation_context: ConversationContext
    ) -> Tuple[LocalizedMessage, LocalizedMessage]:
        """Process a complete conversation turn"""        try:
            # Localize user message (if needed)
            localized_user_message = await self.message_localizer.localize_message(
                user_message,
                MessageType.USER_MESSAGE,
                conversation_context
            )
            
            # Localize system response
            localized_system_response = await self.response_localizer.localize_response(
                system_response,
                "system_response",
                conversation_context
            )
            
            # Update conversation history
            conversation_context.conversation_history.append({
                "user_message": localized_user_message,
                "system_response": localized_system_response,
                "timestamp": datetime.now(timezone.utc)
            })
            
            return localized_user_message, localized_system_response
            
        except Exception as e:
            logger.error(f"Conversation turn processing failed: {e}")
            raise
    
    async def get_localization_statistics(self) -> Dict[str, Any]:
        """Get comprehensive localization statistics"""        return {
            "message_localizer_stats": dict(self.message_localizer.localization_stats),
            "cultural_adaptor_stats": dict(self.cultural_adaptor.adaptation_stats),
            "translation_stats": await self.translation_engine.get_translation_statistics()
        }
