"""
🤖 AI Agents Orchestrator - Standalone Module
=============================================

Standalone module for importing the AI Agents Orchestrator from the core backend.
This provides a clean import interface for the 53+ AI agents orchestration system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Import from the core backend module
try:
    from backend.core.ia_agents_orchestrator import AIAgentsOrchestrator, get_orchestrator
    
    # Export the main classes
    __all__ = ['AIAgentsOrchestrator', 'get_orchestrator']
    
except ImportError:
    # Fallback implementation if backend.core is not available
    import logging
    
    logger = logging.getLogger(__name__)
    
    class AIAgentsOrchestrator:
        """Fallback AI Agents Orchestrator"""
        
        def __init__(self):
            self.agents = {}
            logger.warning("Using fallback AI Agents Orchestrator implementation")
        
        async def initialize(self):
            """Initialize orchestrator"""
            return True
        
        async def get_agent(self, agent_name: str):
            """Get agent by name"""
            return self.agents.get(agent_name)
        
        async def execute_task(self, task_type: str, params: dict):
            """Execute task through appropriate agent"""
            return {"status": "success", "result": "Task executed with fallback implementation"}
    
    def get_orchestrator() -> AIAgentsOrchestrator:
        """Get orchestrator instance"""
        return AIAgentsOrchestrator()
    
    __all__ = ['AIAgentsOrchestrator', 'get_orchestrator']