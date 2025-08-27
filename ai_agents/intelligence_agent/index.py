#!/usr/bin/env python3
"""
Intelligence Agent Module - Main Entry Point

This module serves as the central entry point for the Intelligence Agent system,
providing a unified interface to all intelligence capabilities including decision making,
agent coordination, system optimization, learning, and predictive analytics.

Copyright © 2024 Fahed Mlaiel. All Rights Reserved.
This software is proprietary and confidential.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json
import os

# Core Intelligence Components
from .intelligence_agent import IntelligenceAgent, AgentStatus, AgentMetrics
from .decision_engine import DecisionEngine, DecisionType, DecisionResult
from .agent_coordinator import AgentCoordinator, WorkflowResult, CoordinationStrategy
from .system_optimizer import SystemOptimizer, OptimizationResult, OptimizationLevel
from .learning_engine import LearningEngine, LearningResult, ModelType
from .prediction_engine import PredictionEngine, PredictionResult, ForecastHorizon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('intelligence_agent.log')
    ]
)

logger = logging.getLogger(__name__)


class IntelligenceAgentFactory:
    """Factory class for creating and managing intelligence agent instances."""
    
    _instances: Dict[str, IntelligenceAgent] = {}
    _default_config: Dict[str, Any] = {
        'monitoring_interval': 30,
        'optimization_interval': 300,
        'learning_interval': 600,
        'prediction_interval': 1800,
        'alert_thresholds': {
            'cpu_usage': 80,
            'memory_usage': 85,
            'response_time': 2.0,
            'success_rate': 95,
            'error_rate': 5
        },
        'optimization_config': {
            'auto_scaling': True,
            'load_balancing': True,
            'resource_optimization': True,
            'performance_tuning': True
        },
        'learning_config': {
            'continuous_learning': True,
            'model_retraining': True,
            'pattern_recognition': True,
            'insight_generation': True
        },
        'prediction_config': {
            'time_series_forecasting': True,
            'trend_analysis': True,
            'anomaly_prediction': True,
            'scenario_planning': True
        }
    }
    
    @classmethod
    async def create_intelligence_agent(
        cls, 
        agent_id: str = "default",
        config: Optional[Dict[str, Any]] = None,
        components: Optional[List[str]] = None
    ) -> IntelligenceAgent:
        """
        Create a new intelligence agent instance with specified configuration.
        
        Args:
            agent_id: Unique identifier for the agent instance
            config: Optional configuration overrides
            components: List of components to initialize ['decision', 'coordinator', 'optimizer', 'learning', 'prediction']
        
        Returns:
            IntelligenceAgent: Fully configured and initialized intelligence agent
        """
        if agent_id in cls._instances:
            logger.info(f"Returning existing intelligence agent: {agent_id}")
            return cls._instances[agent_id]
        
        # Merge configurations
        final_config = cls._default_config.copy()
        if config:
            final_config.update(config)
        
        # Create intelligence agent
        intelligence_agent = IntelligenceAgent()
        
        try:
            # Initialize with configuration
            await intelligence_agent.initialize(final_config)
            
            # Initialize specified components
            if components is None:
                components = ['decision', 'coordinator', 'optimizer', 'learning', 'prediction']
            
            if 'decision' in components:
                decision_engine = DecisionEngine()
                await decision_engine.initialize()
                intelligence_agent.decision_engine = decision_engine
                logger.info("Decision engine initialized successfully")
            
            if 'coordinator' in components:
                agent_coordinator = AgentCoordinator()
                await agent_coordinator.initialize()
                intelligence_agent.agent_coordinator = agent_coordinator
                logger.info("Agent coordinator initialized successfully")
            
            if 'optimizer' in components:
                system_optimizer = SystemOptimizer()
                await system_optimizer.initialize()
                intelligence_agent.system_optimizer = system_optimizer
                logger.info("System optimizer initialized successfully")
            
            if 'learning' in components:
                learning_engine = LearningEngine()
                await learning_engine.initialize()
                intelligence_agent.learning_engine = learning_engine
                logger.info("Learning engine initialized successfully")
            
            if 'prediction' in components:
                prediction_engine = PredictionEngine()
                await prediction_engine.initialize()
                intelligence_agent.prediction_engine = prediction_engine
                logger.info("Prediction engine initialized successfully")
            
            # Store instance
            cls._instances[agent_id] = intelligence_agent
            
            logger.info(f"Intelligence agent '{agent_id}' created and initialized successfully")
            return intelligence_agent
            
        except Exception as e:
            logger.error(f"Failed to create intelligence agent '{agent_id}': {str(e)}")
            raise
    
    @classmethod
    def get_instance(cls, agent_id: str = "default") -> Optional[IntelligenceAgent]:
        """Get an existing intelligence agent instance."""
        return cls._instances.get(agent_id)
    
    @classmethod
    async def destroy_instance(cls, agent_id: str) -> bool:
        """Safely destroy an intelligence agent instance."""
        if agent_id in cls._instances:
            try:
                await cls._instances[agent_id].shutdown()
                del cls._instances[agent_id]
                logger.info(f"Intelligence agent '{agent_id}' destroyed successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to destroy intelligence agent '{agent_id}': {str(e)}")
                return False
        return False
    
    @classmethod
    def list_instances(cls) -> List[str]:
        """List all active intelligence agent instances."""
        return list(cls._instances.keys())


class IntelligenceServiceManager:
    """High-level service manager for intelligence operations."""
    
    def __init__(self, intelligence_agent: IntelligenceAgent):
        self.intelligence = intelligence_agent
        self.logger = logging.getLogger(f"{__name__}.ServiceManager")
    
    async def quick_start(self) -> Dict[str, Any]:
        """Quick start method to get the intelligence system up and running."""
        try:
            self.logger.info("Starting intelligence system quick start...")
            
            # Start monitoring
            await self.intelligence.start_monitoring()
            
            # Start optimization
            await self.intelligence.start_optimization()
            
            # Verify system health
            health_status = await self.intelligence.check_system_health()
            
            startup_info = {
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'system_health': health_status,
                'monitoring_active': True,
                'optimization_active': True,
                'components_loaded': [
                    'decision_engine',
                    'agent_coordinator',
                    'system_optimizer',
                    'learning_engine',
                    'prediction_engine'
                ]
            }
            
            self.logger.info("Intelligence system started successfully")
            return startup_info
            
        except Exception as e:
            self.logger.error(f"Failed to start intelligence system: {str(e)}")
            raise
    
    async def register_agents_bulk(self, agents_config: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Register multiple agents at once."""
        results = {}
        
        for agent_config in agents_config:
            try:
                await self.intelligence.register_agent(
                    agent_id=agent_config['agent_id'],
                    agent_type=agent_config['agent_type'],
                    capabilities=agent_config.get('capabilities', []),
                    max_concurrent_tasks=agent_config.get('max_concurrent_tasks', 5)
                )
                results[agent_config['agent_id']] = True
                self.logger.info(f"Agent {agent_config['agent_id']} registered successfully")
                
            except Exception as e:
                results[agent_config['agent_id']] = False
                self.logger.error(f"Failed to register agent {agent_config['agent_id']}: {str(e)}")
        
        return results
    
    async def execute_intelligence_workflow(
        self,
        workflow_name: str,
        workflow_steps: Dict[str, List[str]],
        priority: int = 1,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """Execute a complete intelligence workflow."""
        try:
            self.logger.info(f"Executing intelligence workflow: {workflow_name}")
            
            # Execute workflow through agent coordinator
            result = await self.intelligence.execute_workflow(
                workflow_definition=workflow_steps,
                priority=priority,
                context=context or {}
            )
            
            # Log results
            if result.success:
                self.logger.info(f"Workflow '{workflow_name}' completed successfully in {result.execution_time}s")
            else:
                self.logger.error(f"Workflow '{workflow_name}' failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute workflow '{workflow_name}': {str(e)}")
            raise
    
    async def generate_intelligence_report(self) -> Dict[str, Any]:
        """Generate comprehensive intelligence system report."""
        try:
            # Get system analytics
            analytics = await self.intelligence.get_intelligence_analytics()
            
            # Get individual component reports
            reports = {
                'system_overview': analytics,
                'timestamp': datetime.now().isoformat(),
                'report_version': '1.0.0'
            }
            
            # Add component-specific reports if available
            if hasattr(self.intelligence, 'decision_engine'):
                reports['decision_analytics'] = await self._get_decision_analytics()
            
            if hasattr(self.intelligence, 'agent_coordinator'):
                reports['coordination_analytics'] = await self._get_coordination_analytics()
            
            if hasattr(self.intelligence, 'system_optimizer'):
                reports['optimization_analytics'] = await self._get_optimization_analytics()
            
            if hasattr(self.intelligence, 'learning_engine'):
                reports['learning_analytics'] = await self._get_learning_analytics()
            
            if hasattr(self.intelligence, 'prediction_engine'):
                reports['prediction_analytics'] = await self._get_prediction_analytics()
            
            return reports
            
        except Exception as e:
            self.logger.error(f"Failed to generate intelligence report: {str(e)}")
            raise
    
    async def _get_decision_analytics(self) -> Dict[str, Any]:
        """Get decision engine analytics."""
        return await self.intelligence.decision_engine.get_decision_analytics()
    
    async def _get_coordination_analytics(self) -> Dict[str, Any]:
        """Get agent coordination analytics."""
        return await self.intelligence.agent_coordinator.get_coordination_analytics()
    
    async def _get_optimization_analytics(self) -> Dict[str, Any]:
        """Get system optimization analytics."""
        return await self.intelligence.system_optimizer.get_optimization_analytics()
    
    async def _get_learning_analytics(self) -> Dict[str, Any]:
        """Get learning engine analytics."""
        return await self.intelligence.learning_engine.get_learning_analytics()
    
    async def _get_prediction_analytics(self) -> Dict[str, Any]:
        """Get prediction engine analytics."""
        return await self.intelligence.prediction_engine.get_prediction_analytics()


# Convenience functions for common operations
async def create_intelligence_system(
    config: Optional[Dict[str, Any]] = None,
    agent_id: str = "default"
) -> IntelligenceAgent:
    """
    Convenience function to create and initialize a complete intelligence system.
    
    Args:
        config: Optional configuration dictionary
        agent_id: Unique identifier for the intelligence agent
    
    Returns:
        IntelligenceAgent: Fully initialized intelligence system
    """
    return await IntelligenceAgentFactory.create_intelligence_agent(
        agent_id=agent_id,
        config=config
    )


async def quick_start_intelligence(
    agents_config: Optional[List[Dict[str, Any]]] = None,
    system_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Quick start function to get an intelligence system running with pre-configured agents.
    
    Args:
        agents_config: List of agent configurations to register
        system_config: System configuration overrides
    
    Returns:
        Dict containing startup information and system status
    """
    # Create intelligence system
    intelligence = await create_intelligence_system(config=system_config)
    
    # Create service manager
    service_manager = IntelligenceServiceManager(intelligence)
    
    # Quick start the system
    startup_info = await service_manager.quick_start()
    
    # Register agents if provided
    if agents_config:
        agent_results = await service_manager.register_agents_bulk(agents_config)
        startup_info['agents_registered'] = agent_results
    
    return startup_info


async def execute_intelligence_decision(
    decision_type: str,
    context: Dict[str, Any],
    agent_id: str = "default"
) -> DecisionResult:
    """
    Convenience function to execute a single intelligence decision.
    
    Args:
        decision_type: Type of decision to make
        context: Decision context data
        agent_id: Intelligence agent to use
    
    Returns:
        DecisionResult: Result of the decision process
    """
    intelligence = IntelligenceAgentFactory.get_instance(agent_id)
    if not intelligence:
        raise ValueError(f"Intelligence agent '{agent_id}' not found")
    
    return await intelligence.make_decision(decision_type, context)


async def get_system_health_report(agent_id: str = "default") -> Dict[str, Any]:
    """
    Get comprehensive system health report.
    
    Args:
        agent_id: Intelligence agent to query
    
    Returns:
        Dict containing detailed system health information
    """
    intelligence = IntelligenceAgentFactory.get_instance(agent_id)
    if not intelligence:
        raise ValueError(f"Intelligence agent '{agent_id}' not found")
    
    service_manager = IntelligenceServiceManager(intelligence)
    return await service_manager.generate_intelligence_report()


# Main execution function
async def main():
    """Main function for running intelligence system as standalone application."""
    logger.info("Starting Intelligence Agent System...")
    
    try:
        # Load configuration if exists
        config_path = Path("config/intelligence_config.json")
        config = {}
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded from file")
        
        # Create and start intelligence system
        startup_info = await quick_start_intelligence(system_config=config)
        
        logger.info("Intelligence system started successfully")
        logger.info(f"System status: {json.dumps(startup_info, indent=2)}")
        
        # Keep the system running
        try:
            while True:
                await asyncio.sleep(60)  # Keep alive
                
        except KeyboardInterrupt:
            logger.info("Shutdown signal received, stopping intelligence system...")
            
            # Cleanup
            for agent_id in IntelligenceAgentFactory.list_instances():
                await IntelligenceAgentFactory.destroy_instance(agent_id)
            
            logger.info("Intelligence system stopped gracefully")
            
    except Exception as e:
        logger.error(f"Failed to start intelligence system: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    """Entry point when running as standalone application."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        sys.exit(1)


# Export all public interfaces
__all__ = [
    # Core Classes
    'IntelligenceAgent',
    'DecisionEngine',
    'AgentCoordinator',
    'SystemOptimizer',
    'LearningEngine',
    'PredictionEngine',
    
    # Factory and Management
    'IntelligenceAgentFactory',
    'IntelligenceServiceManager',
    
    # Data Types
    'AgentStatus',
    'AgentMetrics',
    'DecisionType',
    'DecisionResult',
    'WorkflowResult',
    'CoordinationStrategy',
    'OptimizationResult',
    'OptimizationLevel',
    'LearningResult',
    'ModelType',
    'PredictionResult',
    'ForecastHorizon',
    
    # Convenience Functions
    'create_intelligence_system',
    'quick_start_intelligence',
    'execute_intelligence_decision',
    'get_system_health_report',
    
    # Main Function
    'main'
]


# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "contact@fahed-mlaiel.com"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "Copyright © 2024 Fahed Mlaiel"

# Module metadata
__title__ = "Intelligence Agent System"
__description__ = "Advanced AI coordination, decision-making, optimization, learning, and predictive analytics system"
__url__ = "https://ia-influencer-agent.com"
__status__ = "Production"
