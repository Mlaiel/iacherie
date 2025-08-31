"""Chat Orchestration Index - Main Entry Point
===========================================

Point d'entrée principal pour le système d'orchestration de conversation
de la plateforme IA Influencer Agent. Ce module centralise l'accès à tous
les composants d'orchestration de conversation pour créateurs multi-format.

Features:
- Point d'entrée unifié pour tous les composants d'orchestration
- Factory pattern pour l'initialisation des services
- Configuration centralisée et gestion des dépendances
- Interface simplifiée pour l'intégration avec d'autres modules
- Monitoring et logging centralisé des composants
- Gestion des erreurs et fallback automatique

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are proprietary intellectual property of Fahed Mlaiel.
Unauthorized copying, modification, distribution, or use without explicit written
permission is strictly prohibited and will result in legal action.
"""
import asyncio
import logging
from typing import Dict, Optional, Any, Type
from dataclasses import dataclass
from enum import Enum

# Import all main orchestration components
from .chat_manager_enriched import EnterpriseConversationOrchestrator
from .message_processor_enriched import EnterpriseMessageProcessor
from .response_generator_enriched import EnterpriseResponseGenerator
from .intent_classifier_enriched import EnterpriseIntentClassifier
from .context_analyzer_enriched import EnterpriseContextAnalyzer
from .conversation_router_enriched import EnterpriseConversationRouter
from .session_controller_enriched import EnterpriseSessionController
from .chat_analytics_enriched import EnterpriseChatAnalytics

# Import additional enterprise modules
from .content_fingerprinting_engine import ContentFingerprintingEngine
from .content_protection_monitor import ContentProtectionMonitor
from .monetization_orchestrator import MonetizationOrchestrator
from .surveillance_monitor import SurveillanceMonitor
from .realtime_creator_analytics import RealtimeCreatorAnalytics

# Import configuration and utilities
from backend.core.config import settings
from backend.database.connection import DatabaseManager
from backend.utils.redis_client import RedisClient
from backend.security.encryption import EncryptionService


class OrchestrationComponentType(Enum):
    """Types of orchestration components"""
    CHAT_MANAGER = "chat_manager"
    MESSAGE_PROCESSOR = "message_processor"
    RESPONSE_GENERATOR = "response_generator"
    INTENT_CLASSIFIER = "intent_classifier"
    CONTEXT_ANALYZER = "context_analyzer"
    CONVERSATION_ROUTER = "conversation_router"
    SESSION_CONTROLLER = "session_controller"
    CHAT_ANALYTICS = "chat_analytics"
    CONTENT_FINGERPRINTING = "content_fingerprinting"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION_ORCHESTRATOR = "monetization_orchestrator"
    SURVEILLANCE_MONITOR = "surveillance_monitor"
    REALTIME_ANALYTICS = "realtime_analytics"


@dataclass
class OrchestrationConfiguration:
    """Configuration for orchestration components"""
    enable_real_time_processing: bool = True
    enable_content_protection: bool = True
    enable_monetization: bool = True
    enable_analytics: bool = True
    enable_surveillance: bool = True
    max_concurrent_sessions: int = 1000
    redis_enabled: bool = True
    encryption_enabled: bool = True
    debug_mode: bool = False
    
    # Component-specific configurations
    chat_manager_config: Dict[str, Any] = None
    message_processor_config: Dict[str, Any] = None
    response_generator_config: Dict[str, Any] = None
    intent_classifier_config: Dict[str, Any] = None
    context_analyzer_config: Dict[str, Any] = None
    router_config: Dict[str, Any] = None
    session_controller_config: Dict[str, Any] = None
    analytics_config: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default configurations"""
        if self.chat_manager_config is None:
            self.chat_manager_config = {}
        if self.message_processor_config is None:
            self.message_processor_config = {}
        if self.response_generator_config is None:
            self.response_generator_config = {}
        if self.intent_classifier_config is None:
            self.intent_classifier_config = {}
        if self.context_analyzer_config is None:
            self.context_analyzer_config = {}
        if self.router_config is None:
            self.router_config = {}
        if self.session_controller_config is None:
            self.session_controller_config = {}
        if self.analytics_config is None:
            self.analytics_config = {}


class ChatOrchestrationFactory:
    """
    Factory class for creating and managing chat orchestration components.
    
    This factory provides centralized creation and configuration of all
    orchestration components with proper dependency injection and
    lifecycle management.
    """
    
    def __init__(
        self,
        config: Optional[OrchestrationConfiguration] = None,
        database_manager: Optional[DatabaseManager] = None,
        redis_client: Optional[RedisClient] = None,
        encryption_service: Optional[EncryptionService] = None
    ):
        self.config = config or OrchestrationConfiguration()
        self.database_manager = database_manager
        self.redis_client = redis_client
        self.encryption_service = encryption_service
        
        # Component instances cache
        self._components: Dict[OrchestrationComponentType, Any] = {}
        self._initialized = False
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if self.config.debug_mode else logging.INFO)
    
    async def initialize(self) -> None:
        """Initialize the orchestration factory and core dependencies"""
        
        if self._initialized:
            return
        
        try:
            # Initialize database connection if not provided
            if self.database_manager is None:
                self.database_manager = DatabaseManager()
                await self.database_manager.initialize()
            
            # Initialize Redis client if enabled and not provided
            if self.config.redis_enabled and self.redis_client is None:
                self.redis_client = RedisClient()
                await self.redis_client.initialize()
            
            # Initialize encryption service if enabled and not provided
            if self.config.encryption_enabled and self.encryption_service is None:
                self.encryption_service = EncryptionService()
                await self.encryption_service.initialize()
            
            self._initialized = True
            self.logger.info("Chat orchestration factory initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestration factory: {str(e)}")
            raise
    
    async def get_component(
        self,
        component_type: OrchestrationComponentType,
        **kwargs
    ) -> Any:
        """
        Get or create an orchestration component
        
        Args:
            component_type: Type of component to get/create
            **kwargs: Additional configuration for component creation
            
        Returns:
            Initialized component instance
        """
        
        if not self._initialized:
            await self.initialize()
        
        # Return cached component if exists
        if component_type in self._components:
            return self._components[component_type]
        
        # Create component based on type
        component = await self._create_component(component_type, **kwargs)
        
        # Cache the component
        self._components[component_type] = component
        
        return component
    
    async def _create_component(
        self,
        component_type: OrchestrationComponentType,
        **kwargs
    ) -> Any:
        """Create a specific orchestration component"""
        
        try:
            if component_type == OrchestrationComponentType.CHAT_MANAGER:
                return await self._create_chat_manager(**kwargs)
            
            elif component_type == OrchestrationComponentType.MESSAGE_PROCESSOR:
                return await self._create_message_processor(**kwargs)
            
            elif component_type == OrchestrationComponentType.RESPONSE_GENERATOR:
                return await self._create_response_generator(**kwargs)
            
            elif component_type == OrchestrationComponentType.INTENT_CLASSIFIER:
                return await self._create_intent_classifier(**kwargs)
            
            elif component_type == OrchestrationComponentType.CONTEXT_ANALYZER:
                return await self._create_context_analyzer(**kwargs)
            
            elif component_type == OrchestrationComponentType.CONVERSATION_ROUTER:
                return await self._create_conversation_router(**kwargs)
            
            elif component_type == OrchestrationComponentType.SESSION_CONTROLLER:
                return await self._create_session_controller(**kwargs)
            
            elif component_type == OrchestrationComponentType.CHAT_ANALYTICS:
                return await self._create_chat_analytics(**kwargs)
            
            elif component_type == OrchestrationComponentType.CONTENT_FINGERPRINTING:
                return await self._create_content_fingerprinting(**kwargs)
            
            elif component_type == OrchestrationComponentType.CONTENT_PROTECTION:
                return await self._create_content_protection(**kwargs)
            
            elif component_type == OrchestrationComponentType.MONETIZATION_ORCHESTRATOR:
                return await self._create_monetization_orchestrator(**kwargs)
            
            elif component_type == OrchestrationComponentType.SURVEILLANCE_MONITOR:
                return await self._create_surveillance_monitor(**kwargs)
            
            elif component_type == OrchestrationComponentType.REALTIME_ANALYTICS:
                return await self._create_realtime_analytics(**kwargs)
            
            else:
                raise ValueError(f"Unknown component type: {component_type}")
        
        except Exception as e:
            self.logger.error(f"Failed to create component {component_type}: {str(e)}")
            raise
    
    async def _create_chat_manager(self, **kwargs) -> EnterpriseConversationOrchestrator:
        """Create chat manager component"""
        
        # Get required dependencies
        message_processor = await self.get_component(OrchestrationComponentType.MESSAGE_PROCESSOR)
        response_generator = await self.get_component(OrchestrationComponentType.RESPONSE_GENERATOR)
        intent_classifier = await self.get_component(OrchestrationComponentType.INTENT_CLASSIFIER)
        context_analyzer = await self.get_component(OrchestrationComponentType.CONTEXT_ANALYZER)
        session_controller = await self.get_component(OrchestrationComponentType.SESSION_CONTROLLER)
        
        return EnterpriseConversationOrchestrator(
            message_processor=message_processor,
            response_generator=response_generator,
            intent_classifier=intent_classifier,
            context_analyzer=context_analyzer,
            session_controller=session_controller,
            **self.config.chat_manager_config,
            **kwargs
        )
    
    async def _create_message_processor(self, **kwargs) -> EnterpriseMessageProcessor:
        """Create message processor component"""
        
        return EnterpriseMessageProcessor(
            redis_client=self.redis_client,
            **self.config.message_processor_config,
            **kwargs
        )
    
    async def _create_response_generator(self, **kwargs) -> EnterpriseResponseGenerator:
        """Create response generator component"""
        
        return EnterpriseResponseGenerator(
            **self.config.response_generator_config,
            **kwargs
        )
    
    async def _create_intent_classifier(self, **kwargs) -> EnterpriseIntentClassifier:
        """Create intent classifier component"""
        
        return EnterpriseIntentClassifier(
            **self.config.intent_classifier_config,
            **kwargs
        )
    
    async def _create_context_analyzer(self, **kwargs) -> EnterpriseContextAnalyzer:
        """Create context analyzer component"""
        
        return EnterpriseContextAnalyzer(
            **self.config.context_analyzer_config,
            **kwargs
        )
    
    async def _create_conversation_router(self, **kwargs) -> EnterpriseConversationRouter:
        """Create conversation router component"""
        
        return EnterpriseConversationRouter(
            **self.config.router_config,
            **kwargs
        )
    
    async def _create_session_controller(self, **kwargs) -> EnterpriseSessionController:
        """Create session controller component"""
        
        return EnterpriseSessionController(
            session_store=self.database_manager.get_session_store(),
            encryption_service=self.encryption_service,
            redis_client=self.redis_client,
            **self.config.session_controller_config,
            **kwargs
        )
    
    async def _create_chat_analytics(self, **kwargs) -> EnterpriseChatAnalytics:
        """Create chat analytics component"""
        
        return EnterpriseChatAnalytics(
            analytics_store=self.database_manager.get_analytics_store(),
            **self.config.analytics_config,
            **kwargs
        )
    
    async def _create_content_fingerprinting(self, **kwargs) -> ContentFingerprintingEngine:
        """Create content fingerprinting component"""
        
        return ContentFingerprintingEngine(
            database_manager=self.database_manager,
            redis_client=self.redis_client,
            **kwargs
        )
    
    async def _create_content_protection(self, **kwargs) -> ContentProtectionMonitor:
        """Create content protection component"""
        
        fingerprinting_engine = await self.get_component(OrchestrationComponentType.CONTENT_FINGERPRINTING)
        
        return ContentProtectionMonitor(
            fingerprinting_engine=fingerprinting_engine,
            database_manager=self.database_manager,
            **kwargs
        )
    
    async def _create_monetization_orchestrator(self, **kwargs) -> MonetizationOrchestrator:
        """Create monetization orchestrator component"""
        
        return MonetizationOrchestrator(
            database_manager=self.database_manager,
            redis_client=self.redis_client,
            **kwargs
        )
    
    async def _create_surveillance_monitor(self, **kwargs) -> SurveillanceMonitor:
        """Create surveillance monitor component"""
        
        return SurveillanceMonitor(
            database_manager=self.database_manager,
            redis_client=self.redis_client,
            **kwargs
        )
    
    async def _create_realtime_analytics(self, **kwargs) -> RealtimeCreatorAnalytics:
        """Create realtime analytics component"""
        
        return RealtimeCreatorAnalytics(
            database_manager=self.database_manager,
            redis_client=self.redis_client,
            **kwargs
        )
    
    async def get_complete_orchestration_suite(self) -> Dict[str, Any]:
        """
        Get a complete suite of all orchestration components
        
        Returns:
            Dict containing all initialized orchestration components
        """
        
        suite = {}
        
        # Core orchestration components
        suite['chat_manager'] = await self.get_component(OrchestrationComponentType.CHAT_MANAGER)
        suite['message_processor'] = await self.get_component(OrchestrationComponentType.MESSAGE_PROCESSOR)
        suite['response_generator'] = await self.get_component(OrchestrationComponentType.RESPONSE_GENERATOR)
        suite['intent_classifier'] = await self.get_component(OrchestrationComponentType.INTENT_CLASSIFIER)
        suite['context_analyzer'] = await self.get_component(OrchestrationComponentType.CONTEXT_ANALYZER)
        suite['conversation_router'] = await self.get_component(OrchestrationComponentType.CONVERSATION_ROUTER)
        suite['session_controller'] = await self.get_component(OrchestrationComponentType.SESSION_CONTROLLER)
        suite['chat_analytics'] = await self.get_component(OrchestrationComponentType.CHAT_ANALYTICS)
        
        # Advanced enterprise components
        if self.config.enable_content_protection:
            suite['content_fingerprinting'] = await self.get_component(OrchestrationComponentType.CONTENT_FINGERPRINTING)
            suite['content_protection'] = await self.get_component(OrchestrationComponentType.CONTENT_PROTECTION)
        
        if self.config.enable_monetization:
            suite['monetization_orchestrator'] = await self.get_component(OrchestrationComponentType.MONETIZATION_ORCHESTRATOR)
        
        if self.config.enable_surveillance:
            suite['surveillance_monitor'] = await self.get_component(OrchestrationComponentType.SURVEILLANCE_MONITOR)
        
        if self.config.enable_analytics:
            suite['realtime_analytics'] = await self.get_component(OrchestrationComponentType.REALTIME_ANALYTICS)
        
        return suite
    
    async def shutdown(self) -> None:
        """Shutdown all components and cleanup resources"""
        
        try:
            # Shutdown all components
            for component_type, component in self._components.items():
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
            
            # Cleanup database connections
            if self.database_manager:
                await self.database_manager.close()
            
            # Cleanup Redis connections
            if self.redis_client:
                await self.redis_client.close()
            
            # Clear component cache
            self._components.clear()
            self._initialized = False
            
            self.logger.info("Chat orchestration factory shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during factory shutdown: {str(e)}")
            raise


# Global factory instance
_orchestration_factory: Optional[ChatOrchestrationFactory] = None


async def get_orchestration_factory(
    config: Optional[OrchestrationConfiguration] = None
) -> ChatOrchestrationFactory:
    """
    Get the global orchestration factory instance
    
    Args:
        config: Optional configuration for factory initialization
        
    Returns:
        ChatOrchestrationFactory instance
    """
    
    global _orchestration_factory
    
    if _orchestration_factory is None:
        _orchestration_factory = ChatOrchestrationFactory(config)
        await _orchestration_factory.initialize()
    
    return _orchestration_factory


async def get_chat_manager(
    config: Optional[OrchestrationConfiguration] = None,
    **kwargs
) -> EnterpriseConversationOrchestrator:
    """
    Quick access to chat manager component
    
    Args:
        config: Optional configuration
        **kwargs: Additional component configuration
        
    Returns:
        EnterpriseConversationOrchestrator instance
    """
    
    factory = await get_orchestration_factory(config)
    return await factory.get_component(OrchestrationComponentType.CHAT_MANAGER, **kwargs)


async def get_message_processor(
    config: Optional[OrchestrationConfiguration] = None,
    **kwargs
) -> EnterpriseMessageProcessor:
    """
    Quick access to message processor component
    
    Args:
        config: Optional configuration
        **kwargs: Additional component configuration
        
    Returns:
        EnterpriseMessageProcessor instance
    """
    
    factory = await get_orchestration_factory(config)
    return await factory.get_component(OrchestrationComponentType.MESSAGE_PROCESSOR, **kwargs)


async def get_response_generator(
    config: Optional[OrchestrationConfiguration] = None,
    **kwargs
) -> EnterpriseResponseGenerator:
    """
    Quick access to response generator component
    
    Args:
        config: Optional configuration
        **kwargs: Additional component configuration
        
    Returns:
        EnterpriseResponseGenerator instance
    """
    
    factory = await get_orchestration_factory(config)
    return await factory.get_component(OrchestrationComponentType.RESPONSE_GENERATOR, **kwargs)


async def get_complete_orchestration_suite(
    config: Optional[OrchestrationConfiguration] = None
) -> Dict[str, Any]:
    """
    Get complete orchestration suite with all components
    
    Args:
        config: Optional configuration
        
    Returns:
        Dict containing all orchestration components
    """
    
    factory = await get_orchestration_factory(config)
    return await factory.get_complete_orchestration_suite()


# Convenience exports for direct imports
__all__ = [
    # Main factory
    'ChatOrchestrationFactory',
    'OrchestrationConfiguration',
    'OrchestrationComponentType',
    
    # Factory functions
    'get_orchestration_factory',
    'get_chat_manager',
    'get_message_processor', 
    'get_response_generator',
    'get_complete_orchestration_suite',
    
    # Core components
    'EnterpriseConversationOrchestrator',
    'EnterpriseMessageProcessor',
    'EnterpriseResponseGenerator',
    'EnterpriseIntentClassifier',
    'EnterpriseContextAnalyzer',
    'EnterpriseConversationRouter',
    'EnterpriseSessionController',
    'EnterpriseChatAnalytics',
    
    # Advanced components
    'ContentFingerprintingEngine',
    'ContentProtectionMonitor',
    'MonetizationOrchestrator',
    'SurveillanceMonitor',
    'RealtimeCreatorAnalytics'
]


# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Unauthorized use prohibited"
