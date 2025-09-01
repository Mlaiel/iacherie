"""Agent Manager - Ultra-Advanced Industrial Agent Orchestration System

Enterprise-grade management system for coordinating and optimizing all AI agents
in the IA-Influencer-Agent platform with load balancing, failover, and scaling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Type, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

from .base import BaseAgent, AgentRequest, AgentResponse, AgentStatus, AgentPriority
try:
    from ..core.config import settings
except ImportError:
    try:
        from core.config import settings
    except ImportError:
        # Fallback settings object
        settings = type('Settings', (), {
            'redis_url': 'redis://localhost:6379',
            'max_agents_per_type': 10,
            'agent_timeout': 300
        })()
try:
    from ..core.exceptions import AgentError, ResourceLimitError
except ImportError:
    try:
        from core.exceptions import AgentError, ResourceLimitError
    except ImportError:
        class AgentError(Exception): pass
        class ResourceLimitError(Exception): pass

try:
    from ..utils.load_balancer import LoadBalancer
except ImportError:
    LoadBalancer = None

try:
    from ..utils.health_checker import HealthChecker
except ImportError:
    HealthChecker = None

logger = logging.getLogger(__name__)

class PoolingStrategy(Enum):
    """
Agent pooling and scaling strategies"""

    FIXED_SIZE = "fixed_size"
    DYNAMIC_SCALING = "dynamic_scaling" 
    LOAD_BALANCED = "load_balanced"
    PRIORITY_BASED = "priority_based"

@dataclass
class AgentPool:
    """Pool configuration for agent instances"""
    agent_type: str
    min_instances: int = 1
    max_instances: int = 10
    current_instances: int = 0
    strategy: PoolingStrategy = PoolingStrategy.DYNAMIC_SCALING
    scale_up_threshold: float = 0.8  # CPU/Memory usage
    scale_down_threshold: float = 0.3
    health_check_interval: int = 30  # seconds
    agents: Dict[str, BaseAgent] = field(default_factory=dict)
    agent_class: Optional[Type[BaseAgent]] = None
    
@dataclass  
class RoutingRule:
    """
Request routing rules for load balancing"""
    condition: str  # Python expression
    target_agent_type: str
    priority_boost: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentManager:
    """
    Ultra-advanced agent orchestration system with enterprise capabilities:
    
    - Multi-agent coordination and load balancing
    - Dynamic scaling based on demand and resources
    - Health monitoring and failover mechanisms  
    - Request routing and priority management
    - Performance optimization and resource management
    - Multi-tenant isolation and security
    """
    
    def __init__(self):
        self.pools: Dict[str, AgentPool] = {}
        self.routing_rules: List[RoutingRule] = []
        
        # Initialize utilities (with fallbacks)
        if LoadBalancer is not None:
            self.load_balancer = LoadBalancer()
        else:
            self.load_balancer = None
            
        if HealthChecker is not None:
            self.health_checker = HealthChecker()
        else:
            self.health_checker = None
        
        # Manager state
        self.is_running = False
        self.shutdown_requested = False
        self.started_at = datetime.now(timezone.utc)
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        
        # Metrics and monitoring
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'requests_by_agent_type': {},
            'average_response_time': 0.0
        }
        
        logger.info("AgentManager initialized")
    
    async def start(self):
        """Start the agent manager and all background services"""
        if self.is_running:
            logger.warning("AgentManager already running")
            return
        
        logger.info("Starting AgentManager...")
        
        try:
            # Initialize agent pools
            await self._initialize_default_pools()
            
            # Start background tasks
            self._start_background_tasks()
            
            self.is_running = True
            logger.info("AgentManager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start AgentManager: {e}")
            await self.stop()
            raise
    
    async def _initialize_default_pools(self):
        """Initialize default agent pools based on configuration"""
        default_pools = [
            ("content_agent", 2, 5),
            ("protection_agent", 2, 4), 
            ("collaboration_agent", 1, 3),
            ("monetization_agent", 1, 3),
            ("seo_agent", 1, 4),
            ("distribution_agent", 1, 3),
            ("analytics_agent", 1, 2),
            ("moderation_agent", 1, 2),
            ("recommendation_agent", 1, 2),
            ("support_agent", 1, 2)
        ]
        
        for agent_type, min_instances, max_instances in default_pools:
            # Create empty pools; agent classes will be attached later by initialize_agent_system
            if agent_type not in self.pools:
                self.pools[agent_type] = AgentPool(
                    agent_type=agent_type,
                    min_instances=min_instances,
                    max_instances=max_instances,
                    strategy=PoolingStrategy.DYNAMIC_SCALING
                )
                logger.info(f"Registered empty agent pool: {agent_type} ({min_instances}-{max_instances} instances)")
    
    def _start_background_tasks(self):
        """Start background monitoring and management tasks"""
        tasks = [
            self._health_monitor_task(),
            self._scaling_monitor_task(),
            self._metrics_collector_task(),
            self._cleanup_task()
        ]
        
        for task_coro in tasks:
            task = asyncio.create_task(task_coro)
            self._background_tasks.append(task)
    
    async def register_agent_pool(
        self,
        agent_type: str,
        min_instances: int = 1,
        max_instances: int = 10,
        strategy: PoolingStrategy = PoolingStrategy.DYNAMIC_SCALING,
        agent_class: Optional[Type[BaseAgent]] = None
    ):
        """
Register a new agent pool with specified configuration"""
        if agent_type in self.pools:
            # Attach class and top up instances if pool already exists
            pool = self.pools[agent_type]
            pool.min_instances = min_instances or pool.min_instances
            pool.max_instances = max_instances or pool.max_instances
            pool.strategy = strategy or pool.strategy
            if agent_class is not None:
                pool.agent_class = agent_class
                # Create instances until min_instances is satisfied
                await self._ensure_min_instances(pool)
            logger.info(f"Updated existing pool: {agent_type} (instances: {pool.current_instances}/{pool.min_instances})")
            return

        pool = AgentPool(
            agent_type=agent_type,
            min_instances=min_instances,
            max_instances=max_instances,
            strategy=strategy,
            agent_class=agent_class
        )

        # Create initial agent instances if class provided
        if agent_class:
            await self._ensure_min_instances(pool)

        self.pools[agent_type] = pool
        logger.info(f"Registered agent pool: {agent_type} ({pool.current_instances}/{min_instances} started; max {max_instances})")

    async def _ensure_min_instances(self, pool: AgentPool):
        """Ensure a pool has at least min_instances running, creating as needed."""
        if pool.agent_class is None:
            return
        missing = max(0, pool.min_instances - pool.current_instances)
        for i in range(missing):
            agent_id = f"{pool.agent_type}_{pool.current_instances + i}_{uuid.uuid4().hex[:8]}"
            agent = pool.agent_class(agent_id=agent_id, agent_type=pool.agent_type)
            if await agent.initialize():
                pool.agents[agent_id] = agent
                pool.current_instances += 1
                logger.info(f"Created agent {agent_id}")
            else:
                logger.error(f"Failed to initialize agent {agent_id}")
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Route and process request through appropriate agent with load balancing
        """
        start_time = time.time()
        
        try:
            # Route request to appropriate agent type
            target_agent_type = await self._route_request(request)
            
            # Get available agent from pool
            agent = await self._get_available_agent(target_agent_type, request.priority)
            
            if not agent:
                raise ResourceLimitError(f"No available agents for type: {target_agent_type}")
            
            # Process request
            response = await agent.process_request(request)
            
            # Update statistics
            self._update_request_stats(target_agent_type, True, time.time() - start_time)
            
            return response
            
        except Exception as e:
            self._update_request_stats(
                request.metadata.get('target_agent_type', 'unknown'), 
                False, 
                time.time() - start_time
            )
            
            logger.error(f"Request processing failed: {e}")
            return AgentResponse(
                success=False,
                request_id=request.request_id,
                error=str(e),
                error_code="ROUTING_ERROR",
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _route_request(self, request: AgentRequest) -> str:
        """Route request to appropriate agent type using routing rules"""
        
        # Check routing rules
        for rule in self.routing_rules:
            try:
                # Evaluate routing condition
                context = {
                    'request': request,
                    'action': request.action,
                    'data': request.data,
                    'metadata': request.metadata,
                    'priority': request.priority
                }
                
                if eval(rule.condition, {"__builtins__": {}}, context):
                    # Apply priority boost if specified
                    if rule.priority_boost > 0:
                        request.priority = AgentPriority(
                            min(request.priority.value + rule.priority_boost, 5)
                        )
                    
                    return rule.target_agent_type
                    
            except Exception as e:
                logger.warning(f"Routing rule evaluation failed: {e}")
                continue
        
        # Default routing based on action
        return self._get_default_agent_type(request.action)
    
    def _get_default_agent_type(self, action: str) -> str:
        """Get default agent type based on action"""
        action_mappings = {
            # Content processing actions
            'analyze_content': 'content_agent',
            'process_upload': 'content_agent',
            'extract_metadata': 'content_agent',
            'optimize_content': 'content_agent',
            
            # Protection actions
            'generate_fingerprint': 'protection_agent',
            'detect_violation': 'protection_agent',
            'monitor_content': 'protection_agent',
            'enforce_rights': 'protection_agent',
            
            # Collaboration actions
            'match_creators': 'collaboration_agent',
            'analyze_compatibility': 'collaboration_agent',
            'manage_partnership': 'collaboration_agent',
            
            # Monetization actions
            'calculate_revenue': 'monetization_agent',
            'process_payment': 'monetization_agent',
            'track_earnings': 'monetization_agent',
            
            # SEO actions
            'optimize_seo': 'seo_agent',
            'generate_keywords': 'seo_agent',
            'analyze_trends': 'seo_agent',
            
            # Distribution actions
            'distribute_content': 'distribution_agent',
            'schedule_posts': 'distribution_agent',
            'manage_platforms': 'distribution_agent'
        }
        
        return action_mappings.get(action, 'content_agent')
    
    async def _get_available_agent(
        self, 
        agent_type: str, 
        priority: AgentPriority = AgentPriority.NORMAL
    ) -> Optional[BaseAgent]:
        """
Get available agent from pool using load balancing"""
        
        if agent_type not in self.pools:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
        
        pool = self.pools[agent_type]
        
        # Check if scaling is needed
        await self._check_pool_scaling(pool)
        
        # Get agents sorted by load and priority
        available_agents = [
            agent for agent in pool.agents.values()
            if agent.status == AgentStatus.ACTIVE
        ]
        
        if not available_agents:
            logger.warning(f"No available agents for type: {agent_type}")
            return None
        
        # Use load balancer to select best agent
        return self.load_balancer.select_agent(available_agents, priority)
    
    async def _check_pool_scaling(self, pool: AgentPool):
        """Check if agent pool needs scaling up or down"""
        if pool.strategy != PoolingStrategy.DYNAMIC_SCALING:
            return
        
        # Calculate average load across agents
        total_load = 0
        active_agents = 0
        
        for agent in pool.agents.values():
            if agent.status == AgentStatus.ACTIVE:
                health = await agent.get_health_status()
                cpu_usage = health.get('resource_usage', {}).get('cpu_percent', 0)
                memory_usage = health.get('resource_usage', {}).get('memory_percent', 0)
                load = max(cpu_usage, memory_usage) / 100.0
                total_load += load
                active_agents += 1
        
        if active_agents == 0:
            return
        
        average_load = total_load / active_agents
        
        # Scale up if load is high and we haven't reached max instances
        if (average_load > pool.scale_up_threshold and 
            pool.current_instances < pool.max_instances):
            await self._scale_up_pool(pool)
        
        # Scale down if load is low and we have more than min instances
        elif (average_load < pool.scale_down_threshold and 
              pool.current_instances > pool.min_instances):
            await self._scale_down_pool(pool)
    
    async def _scale_up_pool(self, pool: AgentPool):
        """
Scale up agent pool by adding new instance"""
        try:
            if pool.agent_class is None:
                logger.warning(f"Cannot scale up {pool.agent_type}: missing agent_class")
                return
            agent_id = f"{pool.agent_type}_{pool.current_instances}_{uuid.uuid4().hex[:8]}"
            agent = pool.agent_class(agent_id=agent_id, agent_type=pool.agent_type)
            if await agent.initialize():
                pool.agents[agent_id] = agent
                pool.current_instances += 1
                logger.info(f"Scaled up {pool.agent_type} pool: added {agent_id}")
            else:
                logger.error(f"Failed to initialize new agent {agent_id} during scale up")
        except Exception as e:
            logger.error(f"Failed to scale up {pool.agent_type} pool: {e}")
    
    async def _scale_down_pool(self, pool: AgentPool):
        """Scale down agent pool by removing underutilized instance"""
        try:
            # Find agent with lowest load
            min_load_agent = None
            min_load = float('inf')
            
            for agent in pool.agents.values():
                if agent.status == AgentStatus.ACTIVE:
                    health = await agent.get_health_status()
                    active_requests = health.get('active_requests', 0)
                    
                    if active_requests < min_load:
                        min_load = active_requests
                        min_load_agent = agent
            
            if min_load_agent and min_load == 0:
                # Gracefully shutdown the agent
                await min_load_agent.shutdown()
                del pool.agents[min_load_agent.agent_id]
                pool.current_instances -= 1
                
                logger.info(f"Scaled down {pool.agent_type} pool, removed {min_load_agent.agent_id}")
                
        except Exception as e:
            logger.error(f"Failed to scale down {pool.agent_type} pool: {e}")
    
    def add_routing_rule(self, condition: str, target_agent_type: str, priority_boost: int = 0):
        """Add custom routing rule"""
        rule = RoutingRule(
            condition=condition,
            target_agent_type=target_agent_type,
            priority_boost=priority_boost
        )
        self.routing_rules.append(rule)
        logger.info(f"Added routing rule: {condition} -> {target_agent_type}")
    
    def _update_request_stats(self, agent_type: str, success: bool, response_time: float):
        """Update request statistics"""
        self.request_stats['total_requests'] += 1
        
        if success:
            self.request_stats['successful_requests'] += 1
        else:
            self.request_stats['failed_requests'] += 1
        
        # Update average response time
        total = self.request_stats['total_requests']
        current_avg = self.request_stats['average_response_time']
        self.request_stats['average_response_time'] = (
            (current_avg * (total - 1) + response_time) / total
        )
        
        # Update per-agent-type stats
        if agent_type not in self.request_stats['requests_by_agent_type']:
            self.request_stats['requests_by_agent_type'][agent_type] = 0
        self.request_stats['requests_by_agent_type'][agent_type] += 1
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
Get comprehensive system status"""
        pool_status = {}
        
        for agent_type, pool in self.pools.items():
            agent_statuses = {}
            for agent_id, agent in pool.agents.items():
                health = await agent.get_health_status()
                agent_statuses[agent_id] = health
            
            pool_status[agent_type] = {
                'min_instances': pool.min_instances,
                'max_instances': pool.max_instances,
                'current_instances': pool.current_instances,
                'strategy': pool.strategy.value,
                'agents': agent_statuses
            }
        
        uptime = (datetime.now(timezone.utc) - self.started_at).total_seconds()
        
        return {
            'manager_status': 'running' if self.is_running else 'stopped',
            'uptime_seconds': uptime,
            'total_pools': len(self.pools),
            'total_agents': sum(len(pool.agents) for pool in self.pools.values()),
            'request_stats': self.request_stats,
            'pools': pool_status,
            'routing_rules': len(self.routing_rules)
        }
    
    # Background monitoring tasks
    async def _health_monitor_task(self):
        """
Background task for monitoring agent health"""
        while self.is_running and not self.shutdown_requested:
            try:
                for pool in self.pools.values():
                    for agent in pool.agents.values():
                        health = await agent.get_health_status()
                        
                        # Check for unhealthy agents
                        if health.get('status') == 'error':
                            logger.warning(f"Unhealthy agent detected: {agent.agent_id}; attempting recovery")
                            try:
                                # Attempt a soft restart: shutdown then re-initialize
                                await agent.shutdown()
                                if await agent.initialize():
                                    logger.info(f"Agent {agent.agent_id} recovered successfully")
                                else:
                                    logger.error(f"Agent {agent.agent_id} failed to recover; marking for replacement")
                                    # Replace with a new instance if pool has class info
                                    pool = self.pools.get(agent.agent_type)
                                    if pool and pool.agent_class:
                                        new_id = f"{pool.agent_type}_{pool.current_instances}_{uuid.uuid4().hex[:8]}"
                                        replacement = pool.agent_class(agent_id=new_id, agent_type=pool.agent_type)
                                        if await replacement.initialize():
                                            pool.agents[new_id] = replacement
                                            pool.current_instances += 1
                                            # Remove the faulty one
                                            del pool.agents[agent.agent_id]
                                            pool.current_instances = max(0, pool.current_instances - 1)
                                            logger.info(f"Replaced agent {agent.agent_id} with {new_id}")
                                        else:
                                            logger.error(f"Failed to initialize replacement for {agent.agent_id}")
                            except Exception as rex:
                                logger.error(f"Recovery failed for agent {agent.agent_id}: {rex}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _scaling_monitor_task(self):
        """Background task for monitoring scaling decisions"""
        while self.is_running and not self.shutdown_requested:
            try:
                for pool in self.pools.values():
                    await self._check_pool_scaling(pool)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scaling monitor error: {e}")
                await asyncio.sleep(120)
    
    async def _metrics_collector_task(self):
        """Background task for collecting and aggregating metrics"""
        while self.is_running and not self.shutdown_requested:
            try:
                # Collect and aggregate metrics from all agents; log summary
                aggregated = {"agents": 0, "active_requests": 0, "errors": 0}
                for pool in self.pools.values():
                    for agent in pool.agents.values():
                        health = await agent.get_health_status()
                        aggregated["agents"] += 1
                        aggregated["active_requests"] += health.get("active_requests", 0)
                        if health.get("status") == "error":
                            aggregated["errors"] += 1
                logger.debug(f"Metrics snapshot: {json.dumps(aggregated)}")
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(120)
    
    async def _cleanup_task(self):
        """Background task for cleanup operations"""
        while self.is_running and not self.shutdown_requested:
            try:
                # Remove shut down or errored agents with no active requests
                for pool in self.pools.values():
                    stale_ids = []
                    for agent_id, agent in pool.agents.items():
                        health = await agent.get_health_status()
                        if health.get("status") in {"shutdown", "error"} and health.get("active_requests", 0) == 0:
                            stale_ids.append(agent_id)
                    for aid in stale_ids:
                        del pool.agents[aid]
                        pool.current_instances = max(0, pool.current_instances - 1)
                        logger.info(f"Cleaned up agent {aid} from pool {pool.agent_type}")
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(600)
    
    async def stop(self):
        """Stop the agent manager and all agents"""
        if not self.is_running:
            logger.warning("AgentManager not running")
            return
        
        logger.info("Stopping AgentManager...")
        
        self.shutdown_requested = True
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Shutdown all agents
        for pool in self.pools.values():
            for agent in pool.agents.values():
                await agent.shutdown()
        
        self.is_running = False
        logger.info("AgentManager stopped successfully")

# Global agent manager instance
agent_manager = AgentManager()
