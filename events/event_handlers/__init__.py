"""🚀 Event Handlers Enterprise Module - IA Influencer Agent Platform
================================================================
Module: events/event_handlers/__init__.py  
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 EVENT HANDLERS ENTERPRISE
Professional Event Processing System for comprehensive business logic
- Content upload orchestration and validation
- AI processing pipeline coordination  
- Content protection and copyright enforcement
- SEO optimization engine automation
- Collaboration matching and management
- Monetization revenue tracking
- Gamification rewards processing
- Distribution channel coordination
- Notification delivery management
- Security audit processing
- Performance analytics aggregation
"""

from typing import Dict, Type, List
import logging

from ..core.base_event_handler import BaseEventHandler

logger = logging.getLogger(__name__)

# Event handler registry for dynamic loading
EVENT_HANDLER_REGISTRY: Dict[str, Type[BaseEventHandler]] = {}

def register_handler(event_types -> None: List[str]) -> None:
    """Decorator to register event handlers for specific event types"""
    def decorator(handler_class -> None: Type[BaseEventHandler]) -> None:
        for event_type in event_types:
            EVENT_HANDLER_REGISTRY[event_type] = handler_class
        logger.info(f"Registered handler {handler_class.__name__} for events: {event_types}")
        return handler_class
    return decorator

def get_handler_for_event(event_type: str) -> Type[BaseEventHandler]:
    """Get the appropriate handler class for an event type"""
    return EVENT_HANDLER_REGISTRY.get(event_type)

def get_all_registered_handlers() -> Dict[str, Type[BaseEventHandler]]:
    """Get all registered event handlers"""
    return EVENT_HANDLER_REGISTRY.copy()

# Import handlers to trigger registration
try:
    from .content_upload_handler import *
    from .ai_processing_orchestrator import *
    from .content_protection_enforcer import *
    from .seo_optimization_engine import *
    from .collaboration_matching_processor import *
    from .monetization_revenue_tracker import *
    from .gamification_rewards_manager import *
    from .distribution_channel_coordinator import *
    from .notification_delivery_service import *
    from .security_audit_processor import *
    from .performance_analytics_aggregator import *
    
    logger.info("Event Handlers Enterprise Module loaded successfully")
    
except ImportError as e:
    logger.warning(f"Some event handlers not yet implemented: {e}")

__all__ = [
    'BaseEventHandler',
    'EVENT_HANDLER_REGISTRY',
    'register_handler',
    'get_handler_for_event',
    'get_all_registered_handlers'
]