"""
AI Agents Module Index

Entry point and configuration for the AI Agents system in the IA Influencer platform.
Provides centralized initialization, configuration management, and system health monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from . import (
    AIAgentsOrchestrator,
    AgentRegistry,
    AgentCommunicationHub,
    WorkflowEngine,
    TaskManager,
    ContentCreatorAgent,
    SocialMediaManagerAgent,
    EngagementSpecialistAgent,
    AnalyticsAgent,
    AudioSpecialistAgent,
    AgentConfiguration,
    AgentCapability
)

logger = logging.getLogger(__name__)


class AIAgentsSystem:
    """
    Central system for managing all AI agents
    
    Features:
    - Centralized agent initialization
    - System health monitoring
    - Configuration management
    - Performance analytics
    - Error handling and recovery
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.initialized = False
        self.startup_time = datetime.utcnow()
        
        # Core components
        self.registry: Optional[AgentRegistry] = None
        self.communication_hub: Optional[AgentCommunicationHub] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.task_manager: Optional[TaskManager] = None
        self.orchestrator: Optional[AIAgentsOrchestrator] = None
        
        # Agent instances
        self.agents: Dict[str, Any] = {}
        
        # System monitoring
        self.health_status = "initializing"
        self.performance_metrics = {}
        self.error_log = []
    
    async def initialize(self) -> bool:
        """Initialize the complete AI agents system"""
        try:
            logger.info("Initializing AI Agents System...")
            
            # Initialize core components
            await self._initialize_core_components()
            
            # Initialize and register agents
            await self._initialize_agents()
            
            # Start system monitoring
            await self._start_monitoring()
            
            # Validate system health
            if await self._validate_system_health():
                self.initialized = True
                self.health_status = "healthy"
                logger.info("AI Agents System initialized successfully")
                return True
            else:
                self.health_status = "unhealthy"
                logger.error("AI Agents System health validation failed")
                return False
                
        except Exception as e:
            self.health_status = "error"
            error_msg = f"Failed to initialize AI Agents System: {str(e)}"
            logger.error(error_msg)
            self.error_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": "error",
                "message": error_msg,
                "component": "system_initialization"
            })
            return False
    
    async def _initialize_core_components(self) -> None:
        """Initialize core system components"""
        # Agent registry
        self.registry = AgentRegistry()
        
        # Communication hub
        self.communication_hub = AgentCommunicationHub()
        await self.communication_hub.initialize()
        
        # Workflow engine
        self.workflow_engine = WorkflowEngine(self.communication_hub, self.registry)
        await self.workflow_engine.initialize()
        
        # Task manager
        self.task_manager = TaskManager(self.registry, self.communication_hub)
        await self.task_manager.initialize()
        
        # Orchestrator
        self.orchestrator = AIAgentsOrchestrator()
        # Note: Orchestrator initialization would be called here if it has an initialize method
        
        logger.info("Core components initialized")
    
    async def _initialize_agents(self) -> None:
        """Initialize and register all AI agents"""
        agent_configs = self._get_agent_configurations()
        
        for agent_type, config in agent_configs.items():
            try:
                agent = await self._create_agent(agent_type, config)
                if agent:
                    await agent.initialize()
                    self.registry.register_agent(agent)
                    await self.communication_hub.register_agent(agent.agent_id)
                    self.agents[agent_type] = agent
                    logger.info(f"Agent {agent_type} initialized and registered")
                
            except Exception as e:
                error_msg = f"Failed to initialize agent {agent_type}: {str(e)}"
                logger.error(error_msg)
                self.error_log.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "error",
                    "message": error_msg,
                    "component": f"agent_{agent_type}"
                })
    
    async def _create_agent(self, agent_type: str, config: Dict[str, Any]) -> Optional[Any]:
        """Create an agent instance based on type"""
        agent_classes = {
            "content_creator": ContentCreatorAgent,
            "social_media_manager": SocialMediaManagerAgent,
            "engagement_specialist": EngagementSpecialistAgent,
            "analytics": AnalyticsAgent,
            "audio_specialist": AudioSpecialistAgent
        }
        
        agent_class = agent_classes.get(agent_type)
        if not agent_class:
            logger.warning(f"Unknown agent type: {agent_type}")
            return None
        
        # Create agent configuration
        agent_config = AgentConfiguration(
            agent_id=config.get("agent_id", f"{agent_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            agent_name=config.get("agent_name", agent_type.replace("_", " ").title()),
            capabilities=set(AgentCapability(cap) for cap in config.get("capabilities", [])),
            max_concurrent_tasks=config.get("max_concurrent_tasks", 5),
            default_timeout=config.get("default_timeout", 300),
            custom_settings=config.get("custom_settings", {})
        )
        
        return agent_class(agent_config)
    
    def _get_agent_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Get agent configurations from config or defaults"""
        default_configs = {
            "content_creator": {
                "agent_id": "content_creator_001",
                "agent_name": "Content Creator Agent",
                "capabilities": [
                    "text_generation",
                    "image_generation", 
                    "audio_generation",
                    "video_generation",
                    "music_composition",
                    "content_optimization"
                ],
                "max_concurrent_tasks": 3,
                "default_timeout": 600
            },
            "social_media_manager": {
                "agent_id": "social_media_001",
                "agent_name": "Social Media Manager",
                "capabilities": [
                    "platform_posting",
                    "engagement_management",
                    "hashtag_optimization",
                    "cross_platform_sync",
                    "audience_analysis"
                ],
                "max_concurrent_tasks": 10,
                "default_timeout": 300
            },
            "engagement_specialist": {
                "agent_id": "engagement_001", 
                "agent_name": "Engagement Specialist",
                "capabilities": [
                    "engagement_management",
                    "audience_analysis",
                    "sentiment_analysis",
                    "conversational_ai",
                    "real_time_processing"
                ],
                "max_concurrent_tasks": 15,
                "default_timeout": 180
            },
            "analytics": {
                "agent_id": "analytics_001",
                "agent_name": "Analytics Agent",
                "capabilities": [
                    "performance_analysis",
                    "audience_analysis", 
                    "trend_analysis",
                    "data_processing",
                    "real_time_processing"
                ],
                "max_concurrent_tasks": 5,
                "default_timeout": 900
            },
            "audio_specialist": {
                "agent_id": "audio_001",
                "agent_name": "Audio Specialist",
                "capabilities": [
                    "audio_generation",
                    "content_fingerprinting",
                    "copyright_detection",
                    "data_processing",
                    "real_time_processing"
                ],
                "max_concurrent_tasks": 3,
                "default_timeout": 1200
            }
        }
        
        # Merge with user config
        user_configs = self.config.get("agents", {})
        for agent_type, user_config in user_configs.items():
            if agent_type in default_configs:
                default_configs[agent_type].update(user_config)
            else:
                default_configs[agent_type] = user_config
        
        return default_configs
    
    async def _start_monitoring(self) -> None:
        """Start system monitoring tasks"""
        asyncio.create_task(self._health_monitor())
        asyncio.create_task(self._performance_monitor())
        asyncio.create_task(self._error_monitor())
    
    async def _health_monitor(self) -> None:
        """Monitor system health"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Check component health
                component_health = {}
                
                if self.communication_hub:
                    component_health["communication"] = "healthy"
                
                if self.workflow_engine:
                    component_health["workflow"] = "healthy"
                    
                if self.task_manager:
                    stats = await self.task_manager.get_system_statistics()
                    component_health["task_manager"] = "healthy" if stats["system_load"] < 0.9 else "overloaded"
                
                # Check agent health
                for agent_type, agent in self.agents.items():
                    health = await agent.get_health_status()
                    component_health[f"agent_{agent_type}"] = health["status"]
                
                # Update overall health
                unhealthy_components = [k for k, v in component_health.items() if v != "healthy"]
                if not unhealthy_components:
                    self.health_status = "healthy"
                elif len(unhealthy_components) < len(component_health) / 2:
                    self.health_status = "degraded"
                else:
                    self.health_status = "unhealthy"
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
    
    async def _performance_monitor(self) -> None:
        """Monitor system performance"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Collect performance metrics
                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds()
                }
                
                if self.task_manager:
                    task_stats = await self.task_manager.get_system_statistics()
                    metrics.update(task_stats)
                
                # Agent metrics
                agent_metrics = {}
                for agent_type, agent in self.agents.items():
                    health = await agent.get_health_status()
                    agent_metrics[agent_type] = health["metrics"]
                
                metrics["agents"] = agent_metrics
                self.performance_metrics[datetime.utcnow().isoformat()] = metrics
                
                # Keep only last 24 hours of metrics
                cutoff_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                self.performance_metrics = {
                    k: v for k, v in self.performance_metrics.items()
                    if datetime.fromisoformat(k) >= cutoff_time
                }
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {str(e)}")
    
    async def _error_monitor(self) -> None:
        """Monitor and log system errors"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Collect error logs from components
                # This would integrate with the logging system to capture errors
                
                # Keep only last 1000 errors
                if len(self.error_log) > 1000:
                    self.error_log = self.error_log[-1000:]
                
            except Exception as e:
                logger.error(f"Error monitoring error: {str(e)}")
    
    async def _validate_system_health(self) -> bool:
        """Validate that all critical components are healthy"""
        try:
            # Check core components
            if not all([self.registry, self.communication_hub, self.workflow_engine, self.task_manager]):
                return False
            
            # Check minimum required agents
            required_agents = ["content_creator", "social_media_manager", "analytics"]
            for agent_type in required_agents:
                if agent_type not in self.agents:
                    logger.error(f"Required agent {agent_type} not initialized")
                    return False
            
            # Test basic functionality
            # This would include basic health checks for each component
            
            return True
            
        except Exception as e:
            logger.error(f"System health validation error: {str(e)}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_statuses = {}
        for agent_type, agent in self.agents.items():
            agent_statuses[agent_type] = await agent.get_health_status()
        
        return {
            "system_health": self.health_status,
            "initialized": self.initialized,
            "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds(),
            "agents": agent_statuses,
            "performance_metrics": self.performance_metrics,
            "error_count": len(self.error_log),
            "recent_errors": self.error_log[-10:] if self.error_log else []
        }
    
    async def shutdown(self) -> None:
        """Graceful system shutdown"""
        logger.info("Shutting down AI Agents System...")
        
        try:
            # Shutdown agents
            for agent in self.agents.values():
                await agent.shutdown()
            
            # Shutdown core components
            if self.task_manager:
                await self.task_manager.shutdown() if hasattr(self.task_manager, 'shutdown') else None
            
            if self.workflow_engine:
                await self.workflow_engine.shutdown() if hasattr(self.workflow_engine, 'shutdown') else None
            
            if self.communication_hub:
                await self.communication_hub.shutdown()
            
            self.health_status = "shutdown"
            logger.info("AI Agents System shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during system shutdown: {str(e)}")


# Global system instance
_system_instance: Optional[AIAgentsSystem] = None


async def initialize_system(config: Dict[str, Any] = None) -> AIAgentsSystem:
    """Initialize the global AI agents system"""
    global _system_instance
    
    if _system_instance is None:
        _system_instance = AIAgentsSystem(config)
        await _system_instance.initialize()
    
    return _system_instance


def get_system() -> Optional[AIAgentsSystem]:
    """Get the global system instance"""
    return _system_instance


async def shutdown_system() -> None:
    """Shutdown the global system"""
    global _system_instance
    
    if _system_instance:
        await _system_instance.shutdown()
        _system_instance = None
