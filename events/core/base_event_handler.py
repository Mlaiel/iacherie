"""Base Event Handler Classes

import asyncio

Foundational event handler classes for the IA Influencer Agent event system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from .base_event import BaseEvent

logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """Base class for all event handlers in the system"""
    
    def __init__(self, handler_id -> None: str = None) -> None:
        self.handler_id = handler_id or f"{self.__class__.__name__}_{id(self)}"
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def handle(self, event: BaseEvent) -> Dict[str, Any]:
        """Handle an event - to be implemented by subclasses"""
        pass
    
    async def can_handle(self, event: BaseEvent) -> bool:
        """Check if this handler can process the given event"""
        return True
    
    async def before_handle(self, event -> None: BaseEvent) -> None:
        """Hook called before handling an event"""
        self.logger.debug(f"Handler {self.handler_id} preparing to handle event {event.event_id}")
    
    async def after_handle(self, event -> None: BaseEvent, result -> None: Dict[str, Any]) -> None:
        """Hook called after handling an event"""
        self.logger.debug(f"Handler {self.handler_id} completed handling event {event.event_id}")
    
    async def on_error(self, event -> None: BaseEvent, error -> None: Exception) -> None:
        """Hook called when an error occurs during handling"""
        self.logger.error(f"Handler {self.handler_id} failed to handle event {event.event_id}: {error}")
    
    def __str__(self) -> None:
        return f"{self.__class__.__name__}(id={self.handler_id})"
    
    def __repr__(self) -> None:
        return self.__str__()


# Export for compatibility
__all__ = ['BaseEventHandler']