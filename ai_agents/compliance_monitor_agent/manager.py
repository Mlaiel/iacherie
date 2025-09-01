"""
ComplianceMonitor Manager - Ultra-Advanced Enterprise Management System

Compliance Monitor Agent - Legal and Regulatory Surveillance with comprehensive control, monitoring, and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from .core.compliance_monitor_engine import ComplianceMonitorEngine
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
class ComplianceMonitorSystemStatus:
    """Overall compliance_monitor system status"""
    is_healthy: bool = True
    active_operations: int = 0
    system_load: float = 0.0
    operations_completed: int = 0
    last_updated: datetime = None

class ComplianceMonitorManager(BaseAgent):
    """
    Master ComplianceMonitor Manager
    
    Unified interface providing:
        - Automated legal compliance checking
    - Regulatory requirement monitoring
    - Risk assessment and mitigation
    - Documentation and audit trails
    - Multi-jurisdiction compliance support
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = "compliance_monitor", config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id or f"compliance_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_type=agent_type,
            config=config
        )
        
        self.engine = ComplianceMonitorEngine(config)
        self.is_running = False
        self.operations_completed = 0
        
        logger.info("ComplianceMonitorManager initialized")

    async def _load_models_and_resources(self):
        """Load AI models and resources"""
        try:
            await self.engine.start()
            logger.info("ComplianceMonitor models and resources loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load compliance_monitor resources: {e}")
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
            logger.warning("ComplianceMonitor system is already running")
            return
        
        try:
            logger.info("Starting ComplianceMonitor System...")
            await self.engine.start()
            self.is_running = True
            logger.info("ComplianceMonitor System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start compliance_monitor system: {e}")
            raise

    async def get_system_status(self) -> ComplianceMonitorSystemStatus:
        """Get comprehensive system status"""
        try:
            return ComplianceMonitorSystemStatus(
                is_healthy=self.is_running and self.engine.is_running,
                active_operations=len(self.engine._cache),
                system_load=0.0,
                operations_completed=self.operations_completed,
                last_updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return ComplianceMonitorSystemStatus(is_healthy=False)

    async def shutdown(self) -> None:
        """Graceful shutdown"""
        if not self.is_running:
            logger.warning("ComplianceMonitor system is not running")
            return
        
        try:
            logger.info("Shutting down ComplianceMonitor System...")
            await self.engine.shutdown()
            self.is_running = False
            logger.info("ComplianceMonitor System shut down successfully")
            
        except Exception as e:
            logger.error(f"Failed to shutdown compliance_monitor system: {e}")

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
                message=f"ComplianceMonitor operation '{action}' completed successfully",
                agent_type=self.agent_type,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"ComplianceMonitor processing failed: {e}")
            return AgentResponse(
                success=False,
                request_id=request.request_id,
                error=str(e),
                error_code="COMPLIANCE_MONITOR_ERROR",
                agent_type=self.agent_type,
                timestamp=datetime.now()
            )