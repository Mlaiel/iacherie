"""
BrandSafety Manager - Ultra-Advanced Enterprise Management System

Brand Safety Agent - Automatic Brand Protection with comprehensive control, monitoring, and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from .core.brand_safety_engine import BrandSafetyEngine
from ..base import BaseAgent, AgentRequest, AgentResponse

try:
    from core.exceptions import ValidationError
except ImportError:
    class ValidationError(Exception):
        pass

try:
    from core.config import settings
except ImportError:
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()

logger = logging.getLogger(__name__)

@dataclass
class BrandSafetySystemStatus:
    """Overall brand_safety system status"""
    is_healthy: bool = True
    active_operations: int = 0
    system_load: float = 0.0
    operations_completed: int = 0
    last_updated: datetime = None

class BrandSafetyManager(BaseAgent):
    """
    Master BrandSafety Manager
    
    Unified interface providing:
        - Real-time content monitoring for brand safety
    - Automated risk assessment and alerts
    - Brand reputation tracking
    - Crisis prevention and management
    - Compliance verification
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = "brand_safety", config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id or f"brand_safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_type=agent_type,
            config=config
        )
        
        self.engine = BrandSafetyEngine(config)
        self.is_running = False
        self.operations_completed = 0
        
        logger.info("BrandSafetyManager initialized")

    async def _load_models_and_resources(self):
        """Load AI models and resources"""
        try:
            await self.engine.start()
            logger.info("BrandSafety models and resources loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load brand_safety resources: {e}")
            raise

    def get_required_config_keys(self) -> List[str]:
        """Return list of required configuration keys"""
        return [
            'processing_mode',
            'confidence_threshold',
            'max_concurrent_operations',
            'cache_ttl'
        ]

    async def start(self) -> None:
        """Start the system"""
        if self.is_running:
            logger.warning("BrandSafety system is already running")
            return
        
        try:
            logger.info("Starting BrandSafety System...")
            await self.engine.start()
            self.is_running = True
            logger.info("BrandSafety System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start brand_safety system: {e}")
            raise

    async def get_system_status(self) -> BrandSafetySystemStatus:
        """Get comprehensive system status"""
        try:
            return BrandSafetySystemStatus(
                is_healthy=self.is_running and self.engine.is_running,
                active_operations=len(self.engine._cache),
                system_load=0.0,
                operations_completed=self.operations_completed,
                last_updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return BrandSafetySystemStatus(is_healthy=False)

    async def shutdown(self) -> None:
        """Graceful shutdown"""
        if not self.is_running:
            logger.warning("BrandSafety system is not running")
            return
        
        try:
            logger.info("Shutting down BrandSafety System...")
            await self.engine.shutdown()
            self.is_running = False
            logger.info("BrandSafety System shut down successfully")
            
        except Exception as e:
            logger.error(f"Failed to shutdown brand_safety system: {e}")

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Main processing method implementing BaseAgent interface"""
        try:
            if not self.is_running:
                await self.start()
            
            action = request.action
            data = request.data
            
            result = await self.engine.process({
                'action': action,
                **data
            })
            
            self.operations_completed += 1
            
            return AgentResponse(
                success=True,
                request_id=request.request_id,
                data=result,
                message=f"BrandSafety operation '{action}' completed successfully",
                agent_type=self.agent_type,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"BrandSafety processing failed: {e}")
            return AgentResponse(
                success=False,
                request_id=request.request_id,
                error=str(e),
                error_code="BRAND_SAFETY_ERROR",
                agent_type=self.agent_type,
                timestamp=datetime.now()
            )