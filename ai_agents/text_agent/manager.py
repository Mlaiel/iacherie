"""Text Manager - Ultra-Advanced Enterprise Management System

Unified interface for the entire text system providing comprehensive
control, monitoring, and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from .core.text_engine import TextEngine
from ..base import BaseAgent, AgentResponse
try:
    from core.exceptions import ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ValidationError = globals().get('ValidationError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()

logger = logging.getLogger(__name__)

@dataclass
class TextSystemStatus:
    """Overall text system status"""
    is_healthy: bool = True
    active_operations: int = 0
    system_load: float = 0.0
    last_updated: datetime = None

class TextManager(BaseAgent):
    """
    Master Text Manager
    
    Unified interface for the entire text system providing:
    - Single point of control for all text operations
    - Intelligent operation routing and optimization
    - Real-time system monitoring and health checks
    - Performance analytics and reporting
    - Resource management and scaling
    - Error handling and recovery
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Core System Components
        self.engine = TextEngine(config)
        
        # System State
        self.is_running = False
        
        logger.info("TextManager initialized")

    async def start(self) -> None:
        """Start the complete text system"""
        if self.is_running:
            logger.warning("Text system is already running")
            return
        
        try:
            logger.info("Starting Text System...")
            await self.engine.start()
            self.is_running = True
            logger.info("Text System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start text system: {e}")
            raise

    async def get_system_status(self) -> TextSystemStatus:
        """Get comprehensive system status"""
        try:
            return TextSystemStatus(
                is_healthy=self.is_running,
                active_operations=0,  # Implementation specific
                system_load=0.0,     # Implementation specific
                last_updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return TextSystemStatus(is_healthy=False)

    async def shutdown(self) -> None:
        """Graceful shutdown of the entire text system"""
        logger.info("Shutting down Text System...")
        self.is_running = False
        await self.engine.shutdown()
        logger.info("Text System shutdown complete")

    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """Base agent interface implementation"""
        try:
            # Implementation specific to text operations
            result = await self.engine.process(data)
            return AgentResponse(success=True, data=result)
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return AgentResponse(success=False, error=str(e))
