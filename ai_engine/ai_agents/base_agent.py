"""
Base AI Agent Framework

Foundation classes and interfaces for all AI agents in the IA Influencer platform.
Provides standardized capabilities, status management, and communication protocols.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable, Set
from dataclasses import dataclass, field, asdict
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Standardized agent capabilities"""
    # Content Creation
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    MUSIC_COMPOSITION = "music_composition"
    
    # Content Analysis
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TREND_ANALYSIS = "trend_analysis"
    AUDIENCE_ANALYSIS = "audience_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    CONTENT_OPTIMIZATION = "content_optimization"
    
    # Social Media Management
    PLATFORM_POSTING = "platform_posting"
    ENGAGEMENT_MANAGEMENT = "engagement_management"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    CROSS_PLATFORM_SYNC = "cross_platform_sync"
    
    # Content Protection
    COPYRIGHT_DETECTION = "copyright_detection"
    CONTENT_FINGERPRINTING = "content_fingerprinting"
    RIGHTS_MANAGEMENT = "rights_management"
    PIRACY_MONITORING = "piracy_monitoring"
    
    # Collaboration & Networking
    CREATOR_MATCHING = "creator_matching"
    COLLABORATION_COORDINATION = "collaboration_coordination"
    NETWORK_ANALYSIS = "network_analysis"
    
    # Monetization
    REVENUE_OPTIMIZATION = "revenue_optimization"
    PRICING_STRATEGY = "pricing_strategy"
    SPONSORSHIP_MATCHING = "sponsorship_matching"
    
    # Communication
    NATURAL_LANGUAGE_PROCESSING = "natural_language_processing"
    MULTILINGUAL_SUPPORT = "multilingual_support"
    CONVERSATIONAL_AI = "conversational_ai"
    
    # Technical
    API_INTEGRATION = "api_integration"
    DATA_PROCESSING = "data_processing"
    REAL_TIME_PROCESSING = "real_time_processing"
    BATCH_PROCESSING = "batch_processing"


class AgentStatus(Enum):
    """Agent lifecycle status"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    SHUTDOWN = "shutdown"


class AgentPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class AgentMetrics:
    """Performance metrics for agents"""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0
    last_activity: Optional[datetime] = None
    uptime_hours: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    throughput_per_minute: float = 0.0
    error_rate: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_tasks == 0:
            return 0.0
        return (self.successful_tasks / self.total_tasks) * 100


@dataclass
class AgentTask:
    """Task definition for agents"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    priority: AgentPriority = AgentPriority.MEDIUM
    context: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate task duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if task has expired"""
        if not self.timeout_seconds:
            return False
        if not self.started_at:
            return False
        return datetime.now(timezone.utc) > self.started_at + timedelta(seconds=self.timeout_seconds)


@dataclass
class AgentConfiguration:
    """Agent configuration settings"""
    agent_id: str
    agent_name: str
    capabilities: Set[AgentCapability]
    max_concurrent_tasks: int = 5
    default_timeout: int = 300  # seconds
    retry_strategy: str = "exponential_backoff"
    memory_limit_mb: int = 1024
    cpu_limit_percent: int = 80
    enable_monitoring: bool = True
    enable_logging: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class BaseAIAgent(ABC):
    """
    Base class for all AI agents in the IA Influencer platform
    
    Provides:
    - Standardized lifecycle management
    - Task execution framework
    - Performance monitoring
    - Error handling and recovery
    - Communication protocols
    """
    
    def __init__(self, config: AgentConfiguration):
        self.config = config
        self.agent_id = config.agent_id
        self.agent_name = config.agent_name
        self.capabilities = config.capabilities
        
        self.status = AgentStatus.INITIALIZING
        self.metrics = AgentMetrics()
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.shutdown_event = asyncio.Event()
        
        self._startup_time = datetime.now(timezone.utc)
        self._last_heartbeat = datetime.now(timezone.utc)
        self._task_semaphore = asyncio.Semaphore(config.max_concurrent_tasks)
        
        # Initialize logging
        self.logger = logging.getLogger(f"agent.{self.agent_name}")
        
    async def initialize(self) -> bool:
        """Initialize the agent"""
        try:
            self.logger.info(f"Initializing agent {self.agent_name}")
            
            # Custom initialization
            await self._custom_initialize()
            
            # Start background tasks
            asyncio.create_task(self._task_processor())
            asyncio.create_task(self._heartbeat_monitor())
            asyncio.create_task(self._metrics_collector())
            
            self.status = AgentStatus.READY
            self.logger.info(f"Agent {self.agent_name} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent {self.agent_name}: {str(e)}")
            self.status = AgentStatus.ERROR
            return False
    
    @abstractmethod
    async def _custom_initialize(self) -> None:
        """Custom initialization logic for specific agents"""
        pass
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task with proper error handling and metrics"""
        task.started_at = datetime.now(timezone.utc)
        self.active_tasks[task.task_id] = task
        
        try:
            async with self._task_semaphore:
                self.status = AgentStatus.PROCESSING
                self.logger.info(f"Executing task {task.task_id} of type {task.task_type}")
                
                # Execute the actual task
                result = await self._execute_task_impl(task)
                
                task.result = result
                task.completed_at = datetime.now(timezone.utc)
                
                # Update metrics
                self.metrics.successful_tasks += 1
                self.metrics.total_tasks += 1
                self._update_response_time(task)
                
                self.logger.info(f"Task {task.task_id} completed successfully")
                return result
                
        except asyncio.TimeoutError:
            self.logger.error(f"Task {task.task_id} timed out")
            task.error = "Task timeout"
            self.metrics.failed_tasks += 1
            self.metrics.total_tasks += 1
            raise
            
        except Exception as e:
            self.logger.error(f"Task {task.task_id} failed: {str(e)}")
            task.error = str(e)
            self.metrics.failed_tasks += 1
            self.metrics.total_tasks += 1
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                self.logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count})")
                await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                return await self.execute_task(task)
            
            raise
            
        finally:
            # Cleanup
            self.active_tasks.pop(task.task_id, None)
            self.status = AgentStatus.READY if not self.active_tasks else AgentStatus.BUSY
    
    @abstractmethod
    async def _execute_task_impl(self, task: AgentTask) -> Dict[str, Any]:
        """Implementation of task execution - must be overridden by subclasses"""
        pass
    
    async def can_handle_task(self, task_type: str, context: Dict[str, Any]) -> bool:
        """Check if agent can handle a specific task"""
        # Base implementation - can be overridden
        return True
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get agent health and status information"""
        uptime = datetime.now(timezone.utc) - self._startup_time
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "metrics": asdict(self.metrics),
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "uptime_seconds": uptime.total_seconds(),
            "last_heartbeat": self._last_heartbeat.isoformat(),
            "memory_usage_mb": self.metrics.memory_usage_mb,
            "cpu_usage_percent": self.metrics.cpu_usage_percent
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the agent"""
        self.logger.info(f"Shutting down agent {self.agent_name}")
        self.status = AgentStatus.SHUTDOWN
        self.shutdown_event.set()
        
        # Wait for active tasks to complete (with timeout)
        timeout = 30  # seconds
        start_time = datetime.now(timezone.utc)
        
        while self.active_tasks and (datetime.now(timezone.utc) - start_time).total_seconds() < timeout:
            await asyncio.sleep(1)
        
        # Force shutdown if tasks still running
        if self.active_tasks:
            self.logger.warning(f"Force shutting down with {len(self.active_tasks)} active tasks")
        
        await self._custom_shutdown()
        self.status = AgentStatus.OFFLINE
        self.logger.info(f"Agent {self.agent_name} shutdown complete")
    
    async def _custom_shutdown(self) -> None:
        """Custom shutdown logic for specific agents"""
        pass
    
    async def _task_processor(self) -> None:
        """Background task processor"""
        while not self.shutdown_event.is_set():
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Execute task asynchronously
                asyncio.create_task(self.execute_task(task))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in task processor: {str(e)}")
    
    async def _heartbeat_monitor(self) -> None:
        """Background heartbeat monitor"""
        while not self.shutdown_event.is_set():
            self._last_heartbeat = datetime.now(timezone.utc)
            self.metrics.last_activity = self._last_heartbeat
            
            # Update uptime
            uptime = self._last_heartbeat - self._startup_time
            self.metrics.uptime_hours = uptime.total_seconds() / 3600
            
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
    
    async def _metrics_collector(self) -> None:
        """Background metrics collection"""
        while not self.shutdown_event.is_set():
            try:
                # Update throughput
                if self.metrics.total_tasks > 0:
                    uptime_minutes = self.metrics.uptime_hours * 60
                    self.metrics.throughput_per_minute = self.metrics.total_tasks / max(uptime_minutes, 1)
                
                # Update error rate
                if self.metrics.total_tasks > 0:
                    self.metrics.error_rate = (self.metrics.failed_tasks / self.metrics.total_tasks) * 100
                
                # TODO: Collect system metrics (memory, CPU)
                # This would require psutil or similar system monitoring library
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {str(e)}")
            
            await asyncio.sleep(60)  # Collect metrics every minute
    
    def _update_response_time(self, task: AgentTask) -> None:
        """Update average response time"""
        if task.duration:
            duration_seconds = task.duration.total_seconds()
            
            # Moving average calculation
            if self.metrics.average_response_time == 0:
                self.metrics.average_response_time = duration_seconds
            else:
                # Simple moving average with weight towards recent tasks
                weight = 0.1  # 10% weight for new value
                self.metrics.average_response_time = (
                    (1 - weight) * self.metrics.average_response_time + 
                    weight * duration_seconds
                )
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.agent_name}, status={self.status.value})>"


@asynccontextmanager
async def agent_lifecycle(agent: BaseAIAgent):
    """Context manager for agent lifecycle management"""
    try:
        # Initialize agent
        success = await agent.initialize()
        if not success:
            raise RuntimeError(f"Failed to initialize agent {agent.agent_name}")
        
        yield agent
        
    finally:
        # Cleanup
        await agent.shutdown()


class AgentRegistry:
    """Registry for managing multiple agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAIAgent] = {}
        self.capabilities_map: Dict[AgentCapability, List[str]] = {}
    
    def register_agent(self, agent: BaseAIAgent) -> None:
        """Register an agent in the registry"""
        self.agents[agent.agent_id] = agent
        
        # Update capabilities map
        for capability in agent.capabilities:
            if capability not in self.capabilities_map:
                self.capabilities_map[capability] = []
            self.capabilities_map[capability].append(agent.agent_id)
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the registry"""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            
            # Update capabilities map
            for capability in agent.capabilities:
                if capability in self.capabilities_map:
                    self.capabilities_map[capability].remove(agent_id)
                    if not self.capabilities_map[capability]:
                        del self.capabilities_map[capability]
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAIAgent]:
        """Get all agents that have a specific capability"""
        agent_ids = self.capabilities_map.get(capability, [])
        return [self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents]
    
    def get_available_agents(self) -> List[BaseAIAgent]:
        """Get all agents that are ready to handle tasks"""
        return [
            agent for agent in self.agents.values() 
            if agent.status in [AgentStatus.READY, AgentStatus.BUSY]
        ]
    
    async def shutdown_all(self) -> None:
        """Shutdown all registered agents"""
        shutdown_tasks = [agent.shutdown() for agent in self.agents.values()]
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        self.agents.clear()
        self.capabilities_map.clear()
