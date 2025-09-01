"""
AudienceAnalyzer Manager - Ultra-Advanced Enterprise Management System

Audience Analyzer Agent - Deep Audience Intelligence with comprehensive control, monitoring, and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from .core.audience_analyzer_engine import AudienceAnalyzerEngine
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
class AudienceAnalyzerSystemStatus:
    """Overall audience_analyzer system status"""
    is_healthy: bool = True
    active_operations: int = 0
    system_load: float = 0.0
    operations_completed: int = 0
    last_updated: datetime = None

class AudienceAnalyzerManager(BaseAgent):
    """
    Master AudienceAnalyzer Manager
    
    Unified interface providing:
        - Advanced audience segmentation and profiling
    - Behavioral pattern analysis
    - Engagement optimization recommendations
    - Demographic and psychographic insights
    - Cross-platform audience mapping
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = "audience_analyzer", config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id or f"audience_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_type=agent_type,
            config=config
        )
        
        self.engine = AudienceAnalyzerEngine(config)
        self.is_running = False
        self.operations_completed = 0
        
        logger.info("AudienceAnalyzerManager initialized")

    async def _load_models_and_resources(self):
        """Load AI models and resources"""
        try:
            await self.engine.start()
            logger.info("AudienceAnalyzer models and resources loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load audience_analyzer resources: {e}")
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
            logger.warning("AudienceAnalyzer system is already running")
            return
        
        try:
            logger.info("Starting AudienceAnalyzer System...")
            await self.engine.start()
            self.is_running = True
            logger.info("AudienceAnalyzer System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start audience_analyzer system: {e}")
            raise

    async def get_system_status(self) -> AudienceAnalyzerSystemStatus:
        """Get comprehensive system status"""
        try:
            return AudienceAnalyzerSystemStatus(
                is_healthy=self.is_running and self.engine.is_running,
                active_operations=len(self.engine._cache),
                system_load=0.0,
                operations_completed=self.operations_completed,
                last_updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return AudienceAnalyzerSystemStatus(is_healthy=False)

    async def shutdown(self) -> None:
        """Graceful shutdown"""
        if not self.is_running:
            logger.warning("AudienceAnalyzer system is not running")
            return
        
        try:
            logger.info("Shutting down AudienceAnalyzer System...")
            await self.engine.shutdown()
            self.is_running = False
            logger.info("AudienceAnalyzer System shut down successfully")
            
        except Exception as e:
            logger.error(f"Failed to shutdown audience_analyzer system: {e}")

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
                message=f"AudienceAnalyzer operation '{action}' completed successfully",
                agent_type=self.agent_type,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"AudienceAnalyzer processing failed: {e}")
            return AgentResponse(
                success=False,
                request_id=request.request_id,
                error=str(e),
                error_code="AUDIENCE_ANALYZER_ERROR",
                agent_type=self.agent_type,
                timestamp=datetime.now()
            )