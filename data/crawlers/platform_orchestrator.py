"""Platform Orchestrator - Multi-Platform Coordination System
===========================================================

Enterprise-grade platform orchestration system for unified multi-platform coordination.
Implements intelligent load balancing, API quota management, and cross-platform aggregation.

ENTERPRISE ORCHESTRATION FEATURES:
- Unified multi-platform orchestration
- API quota management & cost optimization
- Intelligent load balancing
- Real-time health monitoring
- Advanced error recovery
- Cross-platform result correlation

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import threading
from abc import ABC, abstractmethod
import random
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PLATFORM ORCHESTRATION ENUMS AND DATACLASSES
# ============================================================================

class PlatformType(Enum):
    """Types of platforms for orchestration"""
    SOCIAL_MEDIA = "social_media"
    VIDEO_STREAMING = "video_streaming"
    MUSIC_AUDIO = "music_audio"
    E_COMMERCE = "e_commerce"
    NEWS_MEDIA = "news_media"
    PROFESSIONAL = "professional"
    GAMING = "gaming"
    CREATIVE = "creative"

class PlatformStatus(Enum):
    """Platform operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"

class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    PERFORMANCE_BASED = "performance_based"
    QUOTA_AWARE = "quota_aware"

class HealthCheckType(Enum):
    """Types of health checks"""
    BASIC_CONNECTIVITY = "basic_connectivity"
    API_AVAILABILITY = "api_availability"
    RATE_LIMIT_STATUS = "rate_limit_status"
    DATA_QUALITY = "data_quality"
    RESPONSE_TIME = "response_time"

@dataclass
class PlatformConfiguration:
    """Configuration for individual platforms"""
    platform_id: str
    platform_name: str
    platform_type: PlatformType
    base_url: str
    api_endpoints: Dict[str, str]
    authentication: Dict[str, Any]
    rate_limits: Dict[str, int]
    quotas: Dict[str, int]
    priority: int = 1
    weight: float = 1.0
    timeout: int = 30
    retry_attempts: int = 3
    circuit_breaker_enabled: bool = True
    health_check_interval: int = 300  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformMetrics:
    """Performance metrics for platforms"""
    platform_id: str
    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    requests_rate_limited: int = 0
    average_response_time: float = 0.0
    quota_remaining: Dict[str, int] = field(default_factory=dict)
    last_request_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_error_time: Optional[datetime] = None
    error_rate: float = 0.0
    availability: float = 1.0
    current_connections: int = 0

@dataclass
class OrchestrationTask:
    """Task for platform orchestration"""
    task_id: str
    platform_ids: List[str]
    operation: str
    parameters: Dict[str, Any]
    priority: int = 1
    timeout: int = 60
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    aggregation_strategy: str = "merge"
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None

@dataclass
class PlatformResponse:
    """Response from platform operation"""
    platform_id: str
    task_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    response_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# CORE ORCHESTRATION CLASSES
# ============================================================================

class PlatformOrchestrator:
    """Main platform orchestration system"""
    
    def __init__(self) -> None:
        self.platforms: Dict[str, PlatformConfiguration] = {}
        self.platform_metrics: Dict[str, PlatformMetrics] = {}
        self.platform_status: Dict[str, PlatformStatus] = {}
        self.load_balancer = CrawlerLoadBalancer()
        self.quota_manager = ApiQuotaManager()
        self.health_monitor = PlatformHealthMonitor()
        self.error_recovery = ErrorRecoveryEngine()
        self.result_aggregator = ResultAggregationEngine()
        
        self.active_tasks: Dict[str, OrchestrationTask] = {}
        self.task_results: Dict[str, List[PlatformResponse]] = {}
        self.orchestration_stats: Dict[str, Any] = {}
        self._orchestrator_running = False
        
        logger.info("PlatformOrchestrator initialized")
    
    async def initialize(self) -> None:
        """Initialize the platform orchestration system"""
        try:
            await self.load_balancer.initialize()
            await self.quota_manager.initialize()
            await self.health_monitor.initialize()
            await self.error_recovery.initialize()
            await self.result_aggregator.initialize()
            
            # Load default platform configurations
            await self._load_default_platforms()
            
            # Start orchestration loops
            await self._start_orchestration_loops()
            
            self._orchestrator_running = True
            logger.info("Platform orchestration system fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize platform orchestrator: {e}")
            raise
    
    async def register_platform(self, platform_config: PlatformConfiguration) -> bool:
        """Register a new platform for orchestration"""
        try:
            platform_id = platform_config.platform_id
            
            # Validate configuration
            if not await self._validate_platform_config(platform_config):
                logger.error(f"Invalid platform configuration for {platform_id}")
                return False
            
            # Register platform
            self.platforms[platform_id] = platform_config
            self.platform_metrics[platform_id] = PlatformMetrics(platform_id=platform_id)
            self.platform_status[platform_id] = PlatformStatus.ACTIVE
            
            # Register with subsystems
            await self.load_balancer.register_platform(platform_config)
            await self.quota_manager.register_platform(platform_config)
            await self.health_monitor.register_platform(platform_config)
            
            logger.info(f"Registered platform {platform_id} ({platform_config.platform_name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register platform {platform_config.platform_id}: {e}")
            return False
    
    async def execute_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute orchestrated task across multiple platforms"""
        try:
            task_id = task.task_id
            self.active_tasks[task_id] = task
            self.task_results[task_id] = []
            
            start_time = time.time()
            
            # Select optimal platforms for the task
            selected_platforms = await self._select_platforms_for_task(task)
            
            if not selected_platforms:
                raise ValueError("No suitable platforms available for task")
            
            # Execute task on selected platforms
            platform_responses = await self._execute_on_platforms(task, selected_platforms)
            
            # Store responses
            self.task_results[task_id] = platform_responses
            
            # Aggregate results
            aggregated_result = await self.result_aggregator.aggregate_responses(
                platform_responses, task.aggregation_strategy
            )
            
            # Calculate execution metrics
            execution_time = time.time() - start_time
            success_count = sum(1 for r in platform_responses if r.success)
            
            # Prepare final result
            result = {
                'task_id': task_id,
                'success': success_count > 0,
                'platforms_executed': len(platform_responses),
                'platforms_successful': success_count,
                'execution_time': execution_time,
                'aggregated_data': aggregated_result,
                'platform_responses': platform_responses,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Update orchestration statistics
            await self._update_orchestration_stats(task, result)
            
            # Cleanup
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            logger.info(f"Task {task_id} completed: {success_count}/{len(platform_responses)} platforms successful")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute task {task.task_id}: {e}")
            # Cleanup on error
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            raise
    
    async def get_platform_status(self, platform_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of platforms"""
        try:
            if platform_id:
                if platform_id not in self.platforms:
                    raise ValueError(f"Platform {platform_id} not found")
                
                config = self.platforms[platform_id]
                metrics = self.platform_metrics[platform_id]
                status = self.platform_status[platform_id]
                
                return {
                    'platform_id': platform_id,
                    'platform_name': config.platform_name,
                    'platform_type': config.platform_type.value,
                    'status': status.value,
                    'metrics': {
                        'requests_total': metrics.requests_total,
                        'success_rate': self._calculate_success_rate(metrics),
                        'error_rate': metrics.error_rate,
                        'average_response_time': metrics.average_response_time,
                        'availability': metrics.availability,
                        'current_connections': metrics.current_connections,
                        'quota_remaining': metrics.quota_remaining
                    },
                    'last_activity': metrics.last_request_time.isoformat() if metrics.last_request_time else None
                }
            else:
                # Return status for all platforms
                all_status = {}
                for pid in self.platforms:
                    platform_status = await self.get_platform_status(pid)
                    all_status[pid] = platform_status
                
                return {
                    'total_platforms': len(self.platforms),
                    'active_platforms': len([p for p in self.platform_status.values() if p == PlatformStatus.ACTIVE]),
                    'platforms': all_status,
                    'orchestration_stats': self.orchestration_stats,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get platform status: {e}")
            return {'error': str(e)}
    
    async def _load_default_platforms(self) -> None:
        """Load default platform configurations"""
        try:
            default_platforms = [
                PlatformConfiguration(
                    platform_id="youtube_api",
                    platform_name="YouTube Data API",
                    platform_type=PlatformType.VIDEO_STREAMING,
                    base_url="https://www.googleapis.com/youtube/v3",
                    api_endpoints={
                        "search": "/search",
                        "videos": "/videos",
                        "channels": "/channels"
                    },
                    authentication={"type": "api_key", "header": "Authorization"},
                    rate_limits={"requests_per_day": 10000, "requests_per_second": 100},
                    quotas={"daily_quota": 10000, "current_usage": 0},
                    priority=1,
                    weight=1.0
                ),
                PlatformConfiguration(
                    platform_id="instagram_graph",
                    platform_name="Instagram Graph API",
                    platform_type=PlatformType.SOCIAL_MEDIA,
                    base_url="https://graph.instagram.com",
                    api_endpoints={
                        "media": "/me/media",
                        "user": "/me",
                        "insights": "/insights"
                    },
                    authentication={"type": "oauth", "token_type": "bearer"},
                    rate_limits={"requests_per_hour": 200, "requests_per_second": 5},
                    quotas={"hourly_quota": 200, "current_usage": 0},
                    priority=2,
                    weight=0.8
                ),
                PlatformConfiguration(
                    platform_id="twitter_api_v2",
                    platform_name="Twitter API v2",
                    platform_type=PlatformType.SOCIAL_MEDIA,
                    base_url="https://api.twitter.com/2",
                    api_endpoints={
                        "tweets": "/tweets",
                        "users": "/users",
                        "search": "/tweets/search/recent"
                    },
                    authentication={"type": "bearer_token", "header": "Authorization"},
                    rate_limits={"requests_per_15min": 300, "requests_per_second": 50},
                    quotas={"monthly_quota": 500000, "current_usage": 0},
                    priority=1,
                    weight=0.9
                )
            ]
            
            for platform_config in default_platforms:
                await self.register_platform(platform_config)
            
            logger.info(f"Loaded {len(default_platforms)} default platforms")
            
        except Exception as e:
            logger.error(f"Failed to load default platforms: {e}")
    
    async def _validate_platform_config(self, config: PlatformConfiguration) -> bool:
        """Validate platform configuration"""
        try:
            # Check required fields
            if not all([config.platform_id, config.platform_name, config.base_url]):
                return False
            
            # Check API endpoints
            if not config.api_endpoints:
                return False
            
            # Check authentication
            if not config.authentication or 'type' not in config.authentication:
                return False
            
            # Check rate limits
            if not config.rate_limits:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate platform config: {e}")
            return False
    
    async def _select_platforms_for_task(self, task: OrchestrationTask) -> List[str]:
        """Select optimal platforms for task execution"""
        try:
            # Start with requested platforms
            requested_platforms = task.platform_ids if task.platform_ids else list(self.platforms.keys())
            
            # Filter by availability and status
            available_platforms = []
            for platform_id in requested_platforms:
                if (platform_id in self.platforms and 
                    self.platform_status.get(platform_id) == PlatformStatus.ACTIVE):
                    
                    # Check quota availability
                    if await self.quota_manager.has_quota_available(platform_id):
                        available_platforms.append(platform_id)
            
            # Apply load balancing strategy
            selected_platforms = await self.load_balancer.select_platforms(
                available_platforms, task.operation
            )
            
            logger.info(f"Selected {len(selected_platforms)} platforms for task {task.task_id}")
            return selected_platforms
            
        except Exception as e:
            logger.error(f"Failed to select platforms for task: {e}")
            return []
    
    async def _execute_on_platforms(
        self,
        task: OrchestrationTask,
        platform_ids: List[str]
    ) -> List[PlatformResponse]:
        """Execute task on selected platforms"""
        try:
            responses = []
            
            # Create tasks for each platform
            platform_tasks = []
            for platform_id in platform_ids:
                platform_task = asyncio.create_task(
                    self._execute_on_single_platform(task, platform_id)
                )
                platform_tasks.append(platform_task)
            
            # Wait for all tasks to complete (with timeout)
            try:
                responses = await asyncio.wait_for(
                    asyncio.gather(*platform_tasks, return_exceptions=True),
                    timeout=task.timeout
                )
                
                # Filter out exceptions
                valid_responses = []
                for response in responses:
                    if isinstance(response, PlatformResponse):
                        valid_responses.append(response)
                    elif isinstance(response, Exception):
                        logger.error(f"Platform execution failed: {response}")
                
                responses = valid_responses
                
            except asyncio.TimeoutError:
                logger.warning(f"Task {task.task_id} timed out after {task.timeout}s")
                # Cancel remaining tasks
                for task_obj in platform_tasks:
                    if not task_obj.done():
                        task_obj.cancel()
                
                # Collect completed responses
                responses = [
                    task_obj.result() for task_obj in platform_tasks 
                    if task_obj.done() and not task_obj.cancelled()
                ]
            
            return responses
            
        except Exception as e:
            logger.error(f"Failed to execute on platforms: {e}")
            return []
    
    async def _execute_on_single_platform(
        self,
        task: OrchestrationTask,
        platform_id: str
    ) -> PlatformResponse:
        """Execute task on a single platform"""
        try:
            start_time = time.time()
            
            # Get platform configuration
            config = self.platforms[platform_id]
            metrics = self.platform_metrics[platform_id]
            
            # Check quota before execution
            if not await self.quota_manager.consume_quota(platform_id, 1):
                return PlatformResponse(
                    platform_id=platform_id,
                    task_id=task.task_id,
                    success=False,
                    error="Quota exceeded",
                    response_time=0.0
                )
            
            # Update metrics
            metrics.requests_total += 1
            metrics.current_connections += 1
            metrics.last_request_time = datetime.utcnow()
            
            try:
                # Simulate platform API call (placeholder)
                result = await self._make_platform_api_call(config, task.operation, task.parameters)
                
                # Calculate response time
                response_time = time.time() - start_time
                
                # Update metrics
                metrics.requests_successful += 1
                metrics.last_success_time = datetime.utcnow()
                metrics.average_response_time = (
                    (metrics.average_response_time * (metrics.requests_total - 1) + response_time) /
                    metrics.requests_total
                )
                
                return PlatformResponse(
                    platform_id=platform_id,
                    task_id=task.task_id,
                    success=True,
                    data=result,
                    response_time=response_time
                )
                
            except Exception as e:
                # Handle platform-specific errors
                response_time = time.time() - start_time
                metrics.requests_failed += 1
                metrics.last_error_time = datetime.utcnow()
                metrics.error_rate = metrics.requests_failed / metrics.requests_total
                
                # Apply error recovery if needed
                await self.error_recovery.handle_platform_error(platform_id, str(e))
                
                return PlatformResponse(
                    platform_id=platform_id,
                    task_id=task.task_id,
                    success=False,
                    error=str(e),
                    response_time=response_time
                )
                
            finally:
                metrics.current_connections = max(0, metrics.current_connections - 1)
                
        except Exception as e:
            logger.error(f"Failed to execute on platform {platform_id}: {e}")
            return PlatformResponse(
                platform_id=platform_id,
                task_id=task.task_id,
                success=False,
                error=str(e),
                response_time=0.0
            )
    
    async def _make_platform_api_call(
        self,
        config: PlatformConfiguration,
        operation: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """Make API call to platform (placeholder implementation)"""
        try:
            # Placeholder API call - in production would use actual HTTP client
            await asyncio.sleep(random.uniform(0.1, 1.0))  # Simulate API response time
            
            # Simulate different responses based on operation
            if operation == "search":
                return {
                    "results": [
                        {"id": f"item_{i}", "title": f"Sample Item {i}", "platform": config.platform_name}
                        for i in range(random.randint(1, 10))
                    ],
                    "total": random.randint(10, 1000),
                    "platform": config.platform_name
                }
            elif operation == "get_content":
                return {
                    "content": {
                        "id": parameters.get("content_id", "unknown"),
                        "data": f"Sample content from {config.platform_name}",
                        "metadata": {"platform": config.platform_name, "retrieved_at": datetime.utcnow().isoformat()}
                    }
                }
            else:
                return {
                    "operation": operation,
                    "parameters": parameters,
                    "platform": config.platform_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"API call failed for {config.platform_name}: {e}")
            raise
    
    async def _start_orchestration_loops(self) -> None:
        """Start background orchestration loops"""
        try:
            # Start health monitoring
            asyncio.create_task(self._health_monitoring_loop())
            
            # Start metrics collection
            asyncio.create_task(self._metrics_collection_loop())
            
            # Start quota management
            asyncio.create_task(self._quota_management_loop())
            
            logger.info("Orchestration background loops started")
            
        except Exception as e:
            logger.error(f"Failed to start orchestration loops: {e}")
    
    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring loop"""
        while self._orchestrator_running:
            try:
                for platform_id in self.platforms:
                    await self.health_monitor.check_platform_health(platform_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while self._orchestrator_running:
            try:
                await self._update_platform_availability()
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(15)
    
    async def _quota_management_loop(self) -> None:
        """Background quota management loop"""
        while self._orchestrator_running:
            try:
                await self.quota_manager.refresh_quotas()
                await asyncio.sleep(300)  # Refresh every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in quota management loop: {e}")
                await asyncio.sleep(60)
    
    async def _update_platform_availability(self) -> None:
        """Update platform availability metrics"""
        try:
            for platform_id, metrics in self.platform_metrics.items():
                # Calculate availability based on success rate and recent activity
                total_requests = metrics.requests_total
                if total_requests > 0:
                    success_rate = metrics.requests_successful / total_requests
                    
                    # Factor in recent activity
                    if metrics.last_request_time:
                        time_since_last = (datetime.utcnow() - metrics.last_request_time).total_seconds()
                        recency_factor = max(0.5, 1.0 - (time_since_last / 3600))  # Decay over 1 hour
                        availability = success_rate * recency_factor
                    else:
                        availability = success_rate
                    
                    metrics.availability = min(1.0, max(0.0, availability))
                
        except Exception as e:
            logger.error(f"Failed to update platform availability: {e}")
    
    async def _update_orchestration_stats(self, task: OrchestrationTask, result: Dict[str, Any]) -> None:
        """Update orchestration statistics"""
        try:
            if not hasattr(self, 'orchestration_stats') or not self.orchestration_stats:
                self.orchestration_stats = {
                    'total_tasks': 0,
                    'successful_tasks': 0,
                    'failed_tasks': 0,
                    'average_execution_time': 0.0,
                    'platform_usage': {},
                    'operation_stats': {}
                }
            
            stats = self.orchestration_stats
            
            # Update task counts
            stats['total_tasks'] += 1
            if result['success']:
                stats['successful_tasks'] += 1
            else:
                stats['failed_tasks'] += 1
            
            # Update execution time
            execution_time = result['execution_time']
            stats['average_execution_time'] = (
                (stats['average_execution_time'] * (stats['total_tasks'] - 1) + execution_time) /
                stats['total_tasks']
            )
            
            # Update platform usage
            for response in result['platform_responses']:
                platform_id = response.platform_id
                if platform_id not in stats['platform_usage']:
                    stats['platform_usage'][platform_id] = 0
                stats['platform_usage'][platform_id] += 1
            
            # Update operation stats
            operation = task.operation
            if operation not in stats['operation_stats']:
                stats['operation_stats'][operation] = {'count': 0, 'success_rate': 0.0}
            
            op_stats = stats['operation_stats'][operation]
            op_stats['count'] += 1
            
            # Update operation success rate
            operation_successes = 1 if result['success'] else 0
            op_stats['success_rate'] = (
                (op_stats['success_rate'] * (op_stats['count'] - 1) + operation_successes) /
                op_stats['count']
            )
            
        except Exception as e:
            logger.error(f"Failed to update orchestration stats: {e}")
    
    def _calculate_success_rate(self, metrics: PlatformMetrics) -> float:
        """Calculate success rate for platform metrics"""
        if metrics.requests_total == 0:
            return 0.0
        return (metrics.requests_successful / metrics.requests_total) * 100

class ApiQuotaManager:
    """Advanced API quota management and optimization"""
    
    def __init__(self) -> None:
        self.quota_configs: Dict[str, Dict] = {}
        self.quota_usage: Dict[str, Dict] = {}
        self.quota_forecasts: Dict[str, Dict] = {}
        self.cost_tracking: Dict[str, float] = {}
        
    async def initialize(self) -> None:
        """Initialize quota management system"""
        try:
            logger.info("ApiQuotaManager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize quota manager: {e}")
            raise
    
    async def register_platform(self, config: PlatformConfiguration) -> None:
        """Register platform for quota management"""
        try:
            platform_id = config.platform_id
            
            self.quota_configs[platform_id] = {
                'quotas': config.quotas,
                'rate_limits': config.rate_limits,
                'cost_per_request': config.metadata.get('cost_per_request', 0.0),
                'priority': config.priority
            }
            
            self.quota_usage[platform_id] = {
                'current_usage': 0,
                'daily_usage': 0,
                'hourly_usage': 0,
                'reset_times': {
                    'daily': datetime.utcnow() + timedelta(days=1),
                    'hourly': datetime.utcnow() + timedelta(hours=1)
                }
            }
            
            self.cost_tracking[platform_id] = 0.0
            
            logger.info(f"Registered quota management for platform {platform_id}")
            
        except Exception as e:
            logger.error(f"Failed to register platform quota: {e}")
    
    async def has_quota_available(self, platform_id: str, amount: int = 1) -> bool:
        """Check if quota is available for platform"""
        try:
            if platform_id not in self.quota_configs:
                return False
            
            config = self.quota_configs[platform_id]
            usage = self.quota_usage[platform_id]
            
            # Check daily quota
            daily_limit = config['quotas'].get('daily_quota', float('inf'))
            if usage['daily_usage'] + amount > daily_limit:
                return False
            
            # Check hourly quota
            hourly_limit = config['quotas'].get('hourly_quota', float('inf'))
            if usage['hourly_usage'] + amount > hourly_limit:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check quota availability: {e}")
            return False
    
    async def consume_quota(self, platform_id: str, amount: int = 1) -> bool:
        """Consume quota for platform"""
        try:
            if not await self.has_quota_available(platform_id, amount):
                return False
            
            usage = self.quota_usage[platform_id]
            config = self.quota_configs[platform_id]
            
            # Consume quota
            usage['current_usage'] += amount
            usage['daily_usage'] += amount
            usage['hourly_usage'] += amount
            
            # Update cost tracking
            cost_per_request = config.get('cost_per_request', 0.0)
            self.cost_tracking[platform_id] += cost_per_request * amount
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to consume quota: {e}")
            return False
    
    async def refresh_quotas(self) -> None:
        """Refresh quotas based on time periods"""
        try:
            current_time = datetime.utcnow()
            
            for platform_id, usage in self.quota_usage.items():
                reset_times = usage['reset_times']
                
                # Reset daily quota
                if current_time >= reset_times['daily']:
                    usage['daily_usage'] = 0
                    reset_times['daily'] = current_time + timedelta(days=1)
                
                # Reset hourly quota
                if current_time >= reset_times['hourly']:
                    usage['hourly_usage'] = 0
                    reset_times['hourly'] = current_time + timedelta(hours=1)
            
        except Exception as e:
            logger.error(f"Failed to refresh quotas: {e}")
    
    async def get_quota_status(self, platform_id: str) -> Dict[str, Any]:
        """Get current quota status for platform"""
        try:
            if platform_id not in self.quota_configs:
                return {'error': 'Platform not found'}
            
            config = self.quota_configs[platform_id]
            usage = self.quota_usage[platform_id]
            
            daily_limit = config['quotas'].get('daily_quota', 0)
            hourly_limit = config['quotas'].get('hourly_quota', 0)
            
            return {
                'platform_id': platform_id,
                'daily_quota': {
                    'limit': daily_limit,
                    'used': usage['daily_usage'],
                    'remaining': max(0, daily_limit - usage['daily_usage']),
                    'percentage_used': (usage['daily_usage'] / daily_limit * 100) if daily_limit > 0 else 0
                },
                'hourly_quota': {
                    'limit': hourly_limit,
                    'used': usage['hourly_usage'],
                    'remaining': max(0, hourly_limit - usage['hourly_usage']),
                    'percentage_used': (usage['hourly_usage'] / hourly_limit * 100) if hourly_limit > 0 else 0
                },
                'total_cost': self.cost_tracking.get(platform_id, 0.0),
                'next_reset': {
                    'daily': usage['reset_times']['daily'].isoformat(),
                    'hourly': usage['reset_times']['hourly'].isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get quota status: {e}")
            return {'error': str(e)}

class CrawlerLoadBalancer:
    """Intelligent load balancing for crawler distribution"""
    
    def __init__(self) -> None:
        self.strategies: Dict[LoadBalancingStrategy, Callable] = {}
        self.platform_weights: Dict[str, float] = {}
        self.current_strategy = LoadBalancingStrategy.PERFORMANCE_BASED
        
    async def initialize(self) -> None:
        """Initialize load balancing strategies"""
        try:
            self.strategies = {
                LoadBalancingStrategy.ROUND_ROBIN: self._round_robin_selection,
                LoadBalancingStrategy.WEIGHTED: self._weighted_selection,
                LoadBalancingStrategy.LEAST_CONNECTIONS: self._least_connections_selection,
                LoadBalancingStrategy.PERFORMANCE_BASED: self._performance_based_selection,
                LoadBalancingStrategy.QUOTA_AWARE: self._quota_aware_selection
            }
            
            logger.info("CrawlerLoadBalancer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize load balancer: {e}")
            raise
    
    async def register_platform(self, config: PlatformConfiguration) -> None:
        """Register platform for load balancing"""
        try:
            self.platform_weights[config.platform_id] = config.weight
            
        except Exception as e:
            logger.error(f"Failed to register platform for load balancing: {e}")
    
    async def select_platforms(
        self,
        available_platforms: List[str],
        operation: str,
        max_platforms: Optional[int] = None
    ) -> List[str]:
        """Select platforms using current strategy"""
        try:
            if not available_platforms:
                return []
            
            # Apply load balancing strategy
            strategy_func = self.strategies.get(self.current_strategy)
            if not strategy_func:
                # Fallback to round robin
                strategy_func = self.strategies[LoadBalancingStrategy.ROUND_ROBIN]
            
            selected = await strategy_func(available_platforms, operation)
            
            # Limit number of platforms if specified
            if max_platforms and len(selected) > max_platforms:
                selected = selected[:max_platforms]
            
            return selected
            
        except Exception as e:
            logger.error(f"Failed to select platforms: {e}")
            return available_platforms[:1] if available_platforms else []
    
    async def _round_robin_selection(self, platforms: List[str], operation: str) -> List[str]:
        """Round robin platform selection"""
        # Simple round robin - in production would maintain state
        return platforms
    
    async def _weighted_selection(self, platforms: List[str], operation: str) -> List[str]:
        """Weighted platform selection based on platform weights"""
        try:
            # Sort by weight (highest first)
            weighted_platforms = sorted(
                platforms,
                key=lambda p: self.platform_weights.get(p, 1.0),
                reverse=True
            )
            return weighted_platforms
            
        except Exception as e:
            logger.error(f"Failed to perform weighted selection: {e}")
            return platforms
    
    async def _least_connections_selection(self, platforms: List[str], operation: str) -> List[str]:
        """Select platforms with least current connections"""
        # Placeholder - would access actual connection counts
        return platforms
    
    async def _performance_based_selection(self, platforms: List[str], operation: str) -> List[str]:
        """Select platforms based on performance metrics"""
        # Placeholder - would use actual performance metrics
        return platforms
    
    async def _quota_aware_selection(self, platforms: List[str], operation: str) -> List[str]:
        """Select platforms based on quota availability"""
        # Placeholder - would consider quota remaining
        return platforms

class PlatformHealthMonitor:
    """Advanced platform health monitoring system"""
    
    def __init__(self) -> None:
        self.health_checks: Dict[str, Dict] = {}
        self.health_history: Dict[str, List] = {}
        
    async def initialize(self) -> None:
        """Initialize health monitoring system"""
        try:
            logger.info("PlatformHealthMonitor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize health monitor: {e}")
            raise
    
    async def register_platform(self, config: PlatformConfiguration) -> None:
        """Register platform for health monitoring"""
        try:
            platform_id = config.platform_id
            
            self.health_checks[platform_id] = {
                'last_check': None,
                'status': 'unknown',
                'response_time': 0.0,
                'error_count': 0,
                'consecutive_failures': 0
            }
            
            self.health_history[platform_id] = []
            
        except Exception as e:
            logger.error(f"Failed to register platform for health monitoring: {e}")
    
    async def check_platform_health(self, platform_id: str) -> Dict[str, Any]:
        """Perform health check for platform"""
        try:
            if platform_id not in self.health_checks:
                return {'error': 'Platform not registered'}
            
            start_time = time.time()
            
            # Perform health check (placeholder)
            is_healthy = await self._perform_health_check(platform_id)
            
            response_time = time.time() - start_time
            
            # Update health status
            health_status = self.health_checks[platform_id]
            health_status['last_check'] = datetime.utcnow()
            health_status['response_time'] = response_time
            
            if is_healthy:
                health_status['status'] = 'healthy'
                health_status['consecutive_failures'] = 0
            else:
                health_status['status'] = 'unhealthy'
                health_status['error_count'] += 1
                health_status['consecutive_failures'] += 1
            
            # Store in history
            health_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'status': health_status['status'],
                'response_time': response_time,
                'healthy': is_healthy
            }
            
            self.health_history[platform_id].append(health_record)
            
            # Keep only last 100 records
            if len(self.health_history[platform_id]) > 100:
                self.health_history[platform_id] = self.health_history[platform_id][-100:]
            
            return {
                'platform_id': platform_id,
                'healthy': is_healthy,
                'response_time': response_time,
                'status': health_status['status'],
                'consecutive_failures': health_status['consecutive_failures']
            }
            
        except Exception as e:
            logger.error(f"Failed to check platform health: {e}")
            return {'error': str(e)}
    
    async def _perform_health_check(self, platform_id: str) -> bool:
        """Perform actual health check (placeholder)"""
        try:
            # Placeholder health check - would make actual API call
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Simulate occasional failures
            return random.random() > 0.05  # 5% failure rate
            
        except Exception as e:
            logger.error(f"Health check failed for {platform_id}: {e}")
            return False

class ErrorRecoveryEngine:
    """Advanced error recovery and circuit breaker system"""
    
    def __init__(self) -> None:
        self.circuit_breakers: Dict[str, Dict] = {}
        self.error_patterns: Dict[str, List] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        
    async def initialize(self) -> None:
        """Initialize error recovery system"""
        try:
            self.recovery_strategies = {
                'rate_limit': self._handle_rate_limit_error,
                'timeout': self._handle_timeout_error,
                'authentication': self._handle_auth_error,
                'quota_exceeded': self._handle_quota_error,
                'server_error': self._handle_server_error
            }
            
            logger.info("ErrorRecoveryEngine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize error recovery engine: {e}")
            raise
    
    async def handle_platform_error(self, platform_id: str, error: str) -> None:
        """Handle platform error and apply recovery strategy"""
        try:
            # Classify error type
            error_type = self._classify_error(error)
            
            # Store error pattern
            if platform_id not in self.error_patterns:
                self.error_patterns[platform_id] = []
            
            self.error_patterns[platform_id].append({
                'timestamp': datetime.utcnow(),
                'error': error,
                'type': error_type
            })
            
            # Keep only recent errors
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            self.error_patterns[platform_id] = [
                e for e in self.error_patterns[platform_id]
                if e['timestamp'] > cutoff_time
            ]
            
            # Apply recovery strategy
            recovery_func = self.recovery_strategies.get(error_type)
            if recovery_func:
                await recovery_func(platform_id, error)
            
            # Update circuit breaker
            await self._update_circuit_breaker(platform_id, error_type)
            
        except Exception as e:
            logger.error(f"Failed to handle platform error: {e}")
    
    def _classify_error(self, error: str) -> str:
        """Classify error type"""
        error_lower = error.lower()
        
        if 'rate limit' in error_lower or 'too many requests' in error_lower:
            return 'rate_limit'
        elif 'timeout' in error_lower:
            return 'timeout'
        elif 'authentication' in error_lower or 'unauthorized' in error_lower:
            return 'authentication'
        elif 'quota' in error_lower or 'limit exceeded' in error_lower:
            return 'quota_exceeded'
        elif '5' in error_lower[:1]:  # 5xx errors
            return 'server_error'
        else:
            return 'unknown'
    
    async def _handle_rate_limit_error(self, platform_id: str, error: str) -> None:
        """Handle rate limit errors"""
        logger.warning(f"Rate limit error for {platform_id}: {error}")
        # Implement backoff strategy
    
    async def _handle_timeout_error(self, platform_id: str, error: str) -> None:
        """Handle timeout errors"""
        logger.warning(f"Timeout error for {platform_id}: {error}")
        # Implement retry with increased timeout
    
    async def _handle_auth_error(self, platform_id: str, error: str) -> None:
        """Handle authentication errors"""
        logger.error(f"Authentication error for {platform_id}: {error}")
        # Implement token refresh
    
    async def _handle_quota_error(self, platform_id: str, error: str) -> None:
        """Handle quota exceeded errors"""
        logger.warning(f"Quota error for {platform_id}: {error}")
        # Implement quota management
    
    async def _handle_server_error(self, platform_id: str, error: str) -> None:
        """Handle server errors"""
        logger.warning(f"Server error for {platform_id}: {error}")
        # Implement exponential backoff
    
    async def _update_circuit_breaker(self, platform_id: str, error_type: str) -> None:
        """Update circuit breaker state"""
        try:
            if platform_id not in self.circuit_breakers:
                self.circuit_breakers[platform_id] = {
                    'state': 'closed',  # closed, open, half_open
                    'failure_count': 0,
                    'last_failure': None,
                    'failure_threshold': 5,
                    'recovery_timeout': 300  # seconds
                }
            
            breaker = self.circuit_breakers[platform_id]
            breaker['failure_count'] += 1
            breaker['last_failure'] = datetime.utcnow()
            
            # Open circuit if threshold exceeded
            if breaker['failure_count'] >= breaker['failure_threshold']:
                breaker['state'] = 'open'
                logger.warning(f"Circuit breaker opened for platform {platform_id}")
            
        except Exception as e:
            logger.error(f"Failed to update circuit breaker: {e}")

class ResultAggregationEngine:
    """Advanced result aggregation and merging system"""
    
    def __init__(self) -> None:
        self.aggregation_strategies: Dict[str, Callable] = {}
        
    async def initialize(self) -> None:
        """Initialize result aggregation system"""
        try:
            self.aggregation_strategies = {
                'merge': self._merge_results,
                'union': self._union_results,
                'intersection': self._intersection_results,
                'weighted_average': self._weighted_average_results,
                'best_quality': self._best_quality_results,
                'consensus': self._consensus_results
            }
            
            logger.info("ResultAggregationEngine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize result aggregator: {e}")
            raise
    
    async def aggregate_responses(
        self,
        responses: List[PlatformResponse],
        strategy: str = "merge"
    ) -> Dict[str, Any]:
        """Aggregate responses using specified strategy"""
        try:
            if not responses:
                return {}
            
            # Filter successful responses
            successful_responses = [r for r in responses if r.success and r.data]
            
            if not successful_responses:
                return {'error': 'No successful responses to aggregate'}
            
            # Apply aggregation strategy
            aggregation_func = self.aggregation_strategies.get(strategy, self._merge_results)
            result = await aggregation_func(successful_responses)
            
            # Add aggregation metadata
            result['_aggregation'] = {
                'strategy': strategy,
                'total_responses': len(responses),
                'successful_responses': len(successful_responses),
                'platforms': [r.platform_id for r in successful_responses],
                'aggregated_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to aggregate responses: {e}")
            return {'error': str(e)}
    
    async def _merge_results(self, responses: List[PlatformResponse]) -> Dict[str, Any]:
        """Merge results from multiple platforms"""
        try:
            merged = {
                'data': [],
                'platforms': {},
                'total_items': 0
            }
            
            for response in responses:
                platform_id = response.platform_id
                data = response.data
                
                # Add platform-specific data
                merged['platforms'][platform_id] = {
                    'response_time': response.response_time,
                    'timestamp': response.timestamp.isoformat(),
                    'item_count': 0
                }
                
                # Merge data based on structure
                if isinstance(data, dict):
                    if 'results' in data:
                        items = data['results']
                        merged['data'].extend(items)
                        merged['platforms'][platform_id]['item_count'] = len(items)
                        merged['total_items'] += len(items)
                    else:
                        merged['data'].append({
                            'platform': platform_id,
                            'data': data
                        })
                        merged['platforms'][platform_id]['item_count'] = 1
                        merged['total_items'] += 1
                elif isinstance(data, list):
                    merged['data'].extend(data)
                    merged['platforms'][platform_id]['item_count'] = len(data)
                    merged['total_items'] += len(data)
            
            return merged
            
        except Exception as e:
            logger.error(f"Failed to merge results: {e}")
            return {}
    
    async def _union_results(self, responses: List[PlatformResponse]) -> Dict[str, Any]:
        """Create union of results (remove duplicates)"""
        try:
            merged = await self._merge_results(responses)
            
            # Remove duplicates based on ID or content
            unique_items = []
            seen_ids = set()
            
            for item in merged.get('data', []):
                item_id = None
                
                if isinstance(item, dict):
                    item_id = item.get('id') or item.get('content_id') or str(item)
                else:
                    item_id = str(item)
                
                if item_id not in seen_ids:
                    unique_items.append(item)
                    seen_ids.add(item_id)
            
            merged['data'] = unique_items
            merged['total_items'] = len(unique_items)
            merged['duplicates_removed'] = len(merged.get('data', [])) - len(unique_items)
            
            return merged
            
        except Exception as e:
            logger.error(f"Failed to create union of results: {e}")
            return {}
    
    async def _intersection_results(self, responses: List[PlatformResponse]) -> Dict[str, Any]:
        """Find intersection of results (common items)"""
        try:
            if len(responses) < 2:
                return await self._merge_results(responses)
            
            # Get items from first response
            first_response = responses[0]
            if not first_response.data:
                return {}
            
            first_items = first_response.data.get('results', []) if isinstance(first_response.data, dict) else first_response.data
            
            # Find common items across all responses
            common_items = []
            
            for item in first_items:
                is_common = True
                item_id = item.get('id') if isinstance(item, dict) else str(item)
                
                # Check if item exists in all other responses
                for response in responses[1:]:
                    response_data = response.data
                    response_items = response_data.get('results', []) if isinstance(response_data, dict) else response_data
                    
                    # Check if item exists in this response
                    found = False
                    for resp_item in response_items:
                        resp_item_id = resp_item.get('id') if isinstance(resp_item, dict) else str(resp_item)
                        if resp_item_id == item_id:
                            found = True
                            break
                    
                    if not found:
                        is_common = False
                        break
                
                if is_common:
                    common_items.append(item)
            
            return {
                'data': common_items,
                'total_items': len(common_items),
                'platforms': [r.platform_id for r in responses],
                'intersection_of': len(responses)
            }
            
        except Exception as e:
            logger.error(f"Failed to find intersection of results: {e}")
            return {}
    
    async def _weighted_average_results(self, responses: List[PlatformResponse]) -> Dict[str, Any]:
        """Calculate weighted average of numerical results"""
        try:
            # Placeholder for weighted average calculation
            return await self._merge_results(responses)
            
        except Exception as e:
            logger.error(f"Failed to calculate weighted average: {e}")
            return {}
    
    async def _best_quality_results(self, responses: List[PlatformResponse]) -> Dict[str, Any]:
        """Select best quality results based on response time and data completeness"""
        try:
            if not responses:
                return {}
            
            # Score responses based on quality metrics
            scored_responses = []
            
            for response in responses:
                score = 0.0
                
                # Response time score (lower is better)
                if response.response_time > 0:
                    time_score = max(0, 10 - response.response_time)  # 10 second baseline
                    score += time_score * 0.3
                
                # Data completeness score
                if response.data:
                    if isinstance(response.data, dict):
                        data_size = len(str(response.data))
                        completeness_score = min(10, data_size / 100)  # Normalize by size
                        score += completeness_score * 0.7
                    elif isinstance(response.data, list):
                        completeness_score = min(10, len(response.data))
                        score += completeness_score * 0.7
                
                scored_responses.append((score, response))
            
            # Select highest scoring response
            best_response = max(scored_responses, key=lambda x: x[0])[1]
            
            return {
                'data': best_response.data,
                'selected_platform': best_response.platform_id,
                'quality_score': max(scored_responses, key=lambda x: x[0])[0],
                'response_time': best_response.response_time,
                'selection_criteria': 'best_quality'
            }
            
        except Exception as e:
            logger.error(f"Failed to select best quality results: {e}")
            return await self._merge_results(responses)
    
    async def _consensus_results(self, responses: List[PlatformResponse]) -> Dict[str, Any]:
        """Find consensus among results from multiple platforms"""
        try:
            # Placeholder for consensus algorithm
            return await self._merge_results(responses)
            
        except Exception as e:
            logger.error(f"Failed to find consensus: {e}")
            return {}

# ============================================================================
# UTILITY FUNCTIONS AND EXPORTS
# ============================================================================

async def create_platform_orchestrator() -> PlatformOrchestrator:
    """Factory function to create and initialize platform orchestrator"""
    try:
        orchestrator = PlatformOrchestrator()
        await orchestrator.initialize()
        return orchestrator
        
    except Exception as e:
        logger.error(f"Failed to create platform orchestrator: {e}")
        raise

def create_orchestration_task(
    task_id: str,
    operation: str,
    platform_ids: Optional[List[str]] = None,
    **kwargs
) -> OrchestrationTask:
    """Utility function to create orchestration task"""
    return OrchestrationTask(
        task_id=task_id,
        platform_ids=platform_ids or [],
        operation=operation,
        parameters=kwargs.get('parameters', {}),
        priority=kwargs.get('priority', 1),
        timeout=kwargs.get('timeout', 60),
        aggregation_strategy=kwargs.get('aggregation_strategy', 'merge')
    )

def generate_task_id() -> str:
    """Generate unique task ID"""
    return f"task_{uuid.uuid4().hex[:12]}_{int(time.time())}"

# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Main Classes
    'PlatformOrchestrator',
    'ApiQuotaManager',
    'CrawlerLoadBalancer',
    'PlatformHealthMonitor',
    'ErrorRecoveryEngine',
    'ResultAggregationEngine',
    
    # Configuration Classes
    'PlatformConfiguration',
    'PlatformMetrics',
    'OrchestrationTask',
    'PlatformResponse',
    
    # Enums
    'PlatformType',
    'PlatformStatus',
    'LoadBalancingStrategy',
    'HealthCheckType',
    
    # Utility Functions
    'create_platform_orchestrator',
    'create_orchestration_task',
    'generate_task_id'
]

if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        # Create and initialize orchestrator
        orchestrator = await create_platform_orchestrator()
        
        # Create orchestration task
        task = create_orchestration_task(
            task_id=generate_task_id(),
            operation="search",
            platform_ids=["youtube_api", "twitter_api_v2"],
            parameters={"query": "sample search", "limit": 10},
            aggregation_strategy="merge"
        )
        
        # Execute task
        result = await orchestrator.execute_task(task)
        
        print(f"Task completed: {result['success']}")
        print(f"Platforms executed: {result['platforms_executed']}")
        print(f"Execution time: {result['execution_time']:.2f}s")
        
        # Get platform status
        status = await orchestrator.get_platform_status()
        print(f"Total platforms: {status['total_platforms']}")
        print(f"Active platforms: {status['active_platforms']}")
    
    # Run example
    asyncio.run(main())