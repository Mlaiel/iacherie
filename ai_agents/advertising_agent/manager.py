"""Advertising Agent Manager

Manages intelligent advertising monetization operations.
"""

import logging
from typing import Dict, List, Optional, Any

from ..base import BaseAgent, AgentRequest, AgentResponse
from .core.advertising_engine import AdvertisingEngine

logger = logging.getLogger(__name__)

class AdvertisingManager(BaseAgent):
    """Manager for advertising operations"""
    
    def __init__(self, agent_id: str = "advertising_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="advertising",
            config=config
        )
        self.engine = AdvertisingEngine(config)
        
    async def _load_models_and_resources(self):
        """Load advertising resources"""
        await self.engine.start()
        logger.info("Advertising resources loaded")
    
    def get_required_config_keys(self) -> List[str]:
        """Return required configuration keys"""
        return ['ad_providers', 'optimization_strategy']
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process advertising requests"""
        try:
            action = request.action
            data = request.data
            
            if action == "optimize_placement":
                result = await self.engine.optimize_ad_placement(data)
                return AgentResponse(
                    success=True,
                    data=result,
                    message="Ad placement optimized successfully"
                )
            
            elif action == "create_campaign":
                result = await self.engine.create_campaign(data)
                return AgentResponse(
                    success=True,
                    data=result,
                    message="Campaign created successfully"
                )
            
            elif action == "get_analytics":
                result = await self.engine.get_performance_analytics()
                return AgentResponse(
                    success=True,
                    data=result,
                    message="Analytics retrieved successfully"
                )
            
            else:
                return AgentResponse(
                    success=False,
                    error=f"Unknown action: {action}",
                    error_code="UNKNOWN_ACTION"
                )
                
        except Exception as e:
            logger.error(f"Advertising processing failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                error_code="PROCESSING_ERROR"
            )
    
    async def _custom_data_validation(self, data: Dict[str, Any]):
        """Validate advertising specific data"""
        action = data.get('action')
        if action == 'optimize_placement':
            required_fields = ['content_data']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
        elif action == 'create_campaign':
            required_fields = ['advertiser_id', 'budget']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")