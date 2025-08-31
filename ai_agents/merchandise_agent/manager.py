"""Merchandise Manager"""

import logging
from typing import Dict, List, Optional, Any

from ..base import BaseAgent, AgentRequest, AgentResponse
from .core.merchandise_engine import MerchandiseEngine

logger = logging.getLogger(__name__)

class MerchandiseManager(BaseAgent):
    """Manager for merchandise operations"""
    
    def __init__(self, agent_id: str = "merchandise_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="merchandise",
            config=config
        )
        self.engine = MerchandiseEngine(config)
        
    async def _load_models_and_resources(self):
        await self.engine.start()
        logger.info("Merchandise resources loaded")
    
    def get_required_config_keys(self) -> List[str]:
        return ['product_providers']
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            action = request.action
            data = request.data
            
            if action == "create_product":
                result = await self.engine.create_product(data)
                return AgentResponse(success=True, data=result, message="Product created successfully")
            elif action == "get_products":
                result = await self.engine.get_products()
                return AgentResponse(success=True, data=result, message="Products retrieved successfully")
            else:
                return AgentResponse(success=False, error=f"Unknown action: {action}", error_code="UNKNOWN_ACTION")
                
        except Exception as e:
            logger.error(f"Merchandise processing failed: {e}")
            return AgentResponse(success=False, error=str(e), error_code="PROCESSING_ERROR")