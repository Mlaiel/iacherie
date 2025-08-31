"""Subscription Agent Manager

Manages subscription operations and recurring revenue models.
"""

import logging
from typing import Dict, List, Optional, Any

from ..base import BaseAgent, AgentRequest, AgentResponse
from .core.subscription_engine import SubscriptionEngine

logger = logging.getLogger(__name__)

class SubscriptionManager(BaseAgent):
    """Manager for subscription operations"""
    
    def __init__(self, agent_id: str = "subscription_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="subscription",
            config=config
        )
        self.engine = SubscriptionEngine(config)
        
    async def _load_models_and_resources(self):
        """Load subscription resources"""
        await self.engine.start()
        logger.info("Subscription resources loaded")
    
    def get_required_config_keys(self) -> List[str]:
        """Return required configuration keys"""
        return ['billing_provider', 'default_currency']
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process subscription requests"""
        try:
            action = request.action
            data = request.data
            
            if action == "create_subscription":
                result = await self.engine.create_subscription(
                    data.get('user_id'), 
                    data.get('plan_id')
                )
                return AgentResponse(
                    success=True,
                    data=result,
                    message="Subscription created successfully"
                )
            
            elif action == "process_billing":
                result = await self.engine.process_billing(data.get('subscription_id'))
                return AgentResponse(
                    success=True,
                    data=result,
                    message="Billing processed successfully"
                )
            
            elif action == "cancel_subscription":
                result = await self.engine.cancel_subscription(data.get('subscription_id'))
                return AgentResponse(
                    success=True,
                    data=result,
                    message="Subscription canceled successfully"
                )
            
            elif action == "get_analytics":
                result = await self.engine.get_subscription_analytics()
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
            logger.error(f"Subscription processing failed: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                error_code="PROCESSING_ERROR"
            )
    
    async def _custom_data_validation(self, data: Dict[str, Any]):
        """Validate subscription specific data"""
        action = data.get('action')
        if action == 'create_subscription':
            required_fields = ['user_id', 'plan_id']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
        elif action == 'process_billing':
            if 'subscription_id' not in data:
                raise ValueError("Missing required field: subscription_id")