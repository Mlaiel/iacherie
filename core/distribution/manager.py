"""Distribution Manager - Core Distribution Orchestration
======================================================

Main orchestrator for content distribution across multiple platforms.
Handles distribution workflows, platform coordination, and business logic.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from ..events.event_emitter import EventEmitter
from ..validation.validator import ContentValidator
from ..security.access_control import AccessController


class DistributionStrategy(Enum):
    """Distribution strategy types."""    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    OPTIMIZED = "optimized"
    WATERFALL = "waterfall"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"


class DistributionPriority(Enum):
    """Distribution priority levels."""    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class DistributionRequest:
    """Distribution request data structure."""    request_id: UUID = field(default_factory=uuid4)
    content_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    platforms: List[str] = field(default_factory=list)
    strategy: DistributionStrategy = DistributionStrategy.PARALLEL
    priority: DistributionPriority = DistributionPriority.NORMAL
    schedule_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_adaptations: Dict[str, Dict] = field(default_factory=dict)
    targeting_options: Dict[str, Any] = field(default_factory=dict)
    monetization_settings: Dict[str, Any] = field(default_factory=dict)
    compliance_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class DistributionResult:
    """Distribution result data structure."""    request_id: UUID
    success: bool
    platform_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    total_platforms: int = 0
    successful_platforms: int = 0
    failed_platforms: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    analytics_data: Dict[str, Any] = field(default_factory=dict)


class DistributionManager:
    """    Core Distribution Manager
    
    Orchestrates content distribution across multiple platforms with advanced
    features including scheduling, optimization, and analytics integration.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize distribution manager."""        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.event_emitter = EventEmitter()
        
        # Core components
        self.validator = ContentValidator()
        self.access_controller = AccessController()
        
        # Distribution state
        self.active_distributions: Dict[UUID, DistributionRequest] = {}
        self.distribution_queue: List[DistributionRequest] = []
        self.completed_distributions: Dict[UUID, DistributionResult] = {}
        
        # Platform configuration
        self.platform_configs: Dict[str, Dict[str, Any]] = {}
        self.platform_limits: Dict[str, Dict[str, Any]] = {}
        self.platform_adapters: Dict[str, Any] = {}
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_distributions': 0,
            'failed_distributions': 0,
            'average_execution_time': 0.0,
            'platform_success_rates': {},
            'queue_size': 0,
            'active_distributions': 0
        }
        
        # System state
        self.is_initialized = False
        self.is_running = False
        self.max_concurrent_distributions = config.get('max_concurrent_distributions', 10)
        self.queue_processor_interval = config.get('queue_processor_interval', 5.0)
        
    async def initialize(self) -> bool:
        """        Initialize the distribution manager.
        
        Returns:
            bool: True if initialization successful
        """        try:
            self.logger.info("Initializing Distribution Manager")
            
            # Initialize core components
            await self.validator.initialize()
            await self.access_controller.initialize()
            
            # Load platform configurations
            await self._load_platform_configurations()
            
            # Initialize platform adapters
            await self._initialize_platform_adapters()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            self.is_running = True
            
            self.logger.info("Distribution Manager initialized successfully")
            
            # Emit initialization event
            await self.event_emitter.emit('distribution_manager_initialized', {
                'timestamp': datetime.utcnow(),
                'config': self.config
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Distribution Manager: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """        Gracefully shutdown the distribution manager.
        
        Returns:
            bool: True if shutdown successful
        """        try:
            self.logger.info("Shutting down Distribution Manager")
            self.is_running = False
            
            # Wait for active distributions to complete
            if self.active_distributions:
                self.logger.info(f"Waiting for {len(self.active_distributions)} active distributions to complete")
                timeout = 60  # 60 seconds timeout
                start_time = datetime.utcnow()
                
                while self.active_distributions and (datetime.utcnow() - start_time).seconds < timeout:
                    await asyncio.sleep(1)
                
                if self.active_distributions:
                    self.logger.warning(f"Force stopping {len(self.active_distributions)} remaining distributions")
            
            # Shutdown platform adapters
            await self._shutdown_platform_adapters()
            
            # Clear state
            self.active_distributions.clear()
            self.distribution_queue.clear()
            
            self.is_initialized = False
            
            self.logger.info("Distribution Manager shutdown complete")
            
            # Emit shutdown event
            await self.event_emitter.emit('distribution_manager_shutdown', {
                'timestamp': datetime.utcnow()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during Distribution Manager shutdown: {e}")
            return False
    
    async def distribute_content(
        self,
        content_id: UUID,
        platforms: List[str],
        user_id: Optional[UUID] = None,
        strategy: DistributionStrategy = DistributionStrategy.PARALLEL,
        priority: DistributionPriority = DistributionPriority.NORMAL,
        schedule_time: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> DistributionResult:
        """        Distribute content to specified platforms.
        
        Args:
            content_id: Unique identifier for content
            platforms: List of target platforms
            user_id: User requesting distribution
            strategy: Distribution strategy to use
            priority: Distribution priority
            schedule_time: Optional scheduled distribution time
            metadata: Additional distribution metadata
            **kwargs: Additional options
            
        Returns:
            DistributionResult: Results of distribution operation
        """        if not self.is_initialized:
            raise RuntimeError("Distribution Manager not initialized")
        
        # Create distribution request
        request = DistributionRequest(
            content_id=content_id,
            user_id=user_id or uuid4(),
            platforms=platforms,
            strategy=strategy,
            priority=priority,
            schedule_time=schedule_time,
            metadata=metadata or {},
            **kwargs
        )
        
        self.logger.info(f"Received distribution request {request.request_id} for content {content_id}")
        
        try:
            # Validate request
            await self._validate_distribution_request(request)
            
            # Check access permissions
            if user_id:
                await self._check_distribution_permissions(user_id, request)
            
            # Update metrics
            self.metrics['total_requests'] += 1
            
            # Handle immediate vs scheduled distribution
            if schedule_time and schedule_time > datetime.utcnow():
                return await self._schedule_distribution(request)
            else:
                return await self._execute_distribution(request)
                
        except Exception as e:
            self.logger.error(f"Distribution failed for request {request.request_id}: {e}")
            
            # Create error result
            result = DistributionResult(
                request_id=request.request_id,
                success=False,
                total_platforms=len(platforms),
                successful_platforms=0,
                failed_platforms=len(platforms),
                errors=[str(e)],
                completed_at=datetime.utcnow()
            )
            
            # Update metrics
            self.metrics['failed_distributions'] += 1
            
            return result
    
    async def _validate_distribution_request(self, request: DistributionRequest) -> None:
        """Validate distribution request."""        # Validate content exists and is accessible
        content_valid = await self.validator.validate_content_exists(request.content_id)
        if not content_valid:
            raise ValueError(f"Content {request.content_id} not found or not accessible")
        
        # Validate platforms
        invalid_platforms = [p for p in request.platforms if p not in self.platform_configs]
        if invalid_platforms:
            raise ValueError(f"Invalid platforms: {invalid_platforms}")
        
        # Validate content format compatibility
        for platform in request.platforms:
            compatible = await self.validator.validate_platform_compatibility(
                request.content_id, platform
            )
            if not compatible:
                raise ValueError(f"Content {request.content_id} not compatible with platform {platform}")
    
    async def _check_distribution_permissions(self, user_id: UUID, request: DistributionRequest) -> None:
        """Check user permissions for distribution."""        # Check basic distribution permission
        has_permission = await self.access_controller.check_permission(
            user_id, 'content.distribute', request.content_id
        )
        if not has_permission:
            raise PermissionError(f"User {user_id} not authorized to distribute content {request.content_id}")
        
        # Check platform-specific permissions
        for platform in request.platforms:
            platform_permission = await self.access_controller.check_permission(
                user_id, f'platform.{platform}.publish'
            )
            if not platform_permission:
                raise PermissionError(f"User {user_id} not authorized for platform {platform}")
    
    async def _schedule_distribution(self, request: DistributionRequest) -> DistributionResult:
        """Schedule distribution for future execution."""        self.logger.info(f"Scheduling distribution {request.request_id} for {request.schedule_time}")
        
        # Add to queue with priority ordering
        self.distribution_queue.append(request)
        self.distribution_queue.sort(key=lambda r: (r.priority.value, r.schedule_time or datetime.min))
        
        # Update metrics
        self.metrics['queue_size'] = len(self.distribution_queue)
        
        # Emit scheduled event
        await self.event_emitter.emit('distribution_scheduled', {
            'request_id': request.request_id,
            'content_id': request.content_id,
            'platforms': request.platforms,
            'schedule_time': request.schedule_time
        })
        
        # Return immediate acknowledgment
        return DistributionResult(
            request_id=request.request_id,
            success=True,
            total_platforms=len(request.platforms),
            successful_platforms=0,  # Will be updated when executed
            failed_platforms=0,
            started_at=datetime.utcnow(),
            analytics_data={'status': 'scheduled', 'schedule_time': request.schedule_time}
        )
    
    async def _execute_distribution(self, request: DistributionRequest) -> DistributionResult:
        """Execute distribution immediately."""        start_time = datetime.utcnow()
        execution_start = asyncio.get_event_loop().time()
        
        self.logger.info(f"Executing distribution {request.request_id}")
        
        # Add to active distributions
        self.active_distributions[request.request_id] = request
        self.metrics['active_distributions'] = len(self.active_distributions)
        
        try:
            # Emit distribution started event
            await self.event_emitter.emit('distribution_started', {
                'request_id': request.request_id,
                'content_id': request.content_id,
                'platforms': request.platforms,
                'strategy': request.strategy.value
            })
            
            # Execute based on strategy
            if request.strategy == DistributionStrategy.PARALLEL:
                platform_results = await self._execute_parallel_distribution(request)
            elif request.strategy == DistributionStrategy.WATERFALL:
                platform_results = await self._execute_waterfall_distribution(request)
            elif request.strategy == DistributionStrategy.OPTIMIZED:
                platform_results = await self._execute_optimized_distribution(request)
            else:
                platform_results = await self._execute_parallel_distribution(request)
            
            # Calculate results
            successful_platforms = sum(1 for result in platform_results.values() if result.get('success', False))
            failed_platforms = len(request.platforms) - successful_platforms
            
            execution_time = asyncio.get_event_loop().time() - execution_start
            
            result = DistributionResult(
                request_id=request.request_id,
                success=successful_platforms > 0,
                platform_results=platform_results,
                total_platforms=len(request.platforms),
                successful_platforms=successful_platforms,
                failed_platforms=failed_platforms,
                execution_time=execution_time,
                started_at=start_time,
                completed_at=datetime.utcnow()
            )
            
            # Update metrics
            if result.success:
                self.metrics['successful_distributions'] += 1
            else:
                self.metrics['failed_distributions'] += 1
            
            # Update average execution time
            total_distributions = self.metrics['successful_distributions'] + self.metrics['failed_distributions']
            self.metrics['average_execution_time'] = (
                (self.metrics['average_execution_time'] * (total_distributions - 1) + execution_time) 
                / total_distributions
            )
            
            # Store completed distribution
            self.completed_distributions[request.request_id] = result
            
            # Emit completion event
            await self.event_emitter.emit('distribution_completed', {
                'request_id': request.request_id,
                'success': result.success,
                'execution_time': execution_time,
                'platform_results': platform_results
            })
            
            self.logger.info(f"Distribution {request.request_id} completed: {successful_platforms}/{len(request.platforms)} platforms successful")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Distribution execution failed: {e}")
            
            result = DistributionResult(
                request_id=request.request_id,
                success=False,
                total_platforms=len(request.platforms),
                successful_platforms=0,
                failed_platforms=len(request.platforms),
                errors=[str(e)],
                execution_time=asyncio.get_event_loop().time() - execution_start,
                started_at=start_time,
                completed_at=datetime.utcnow()
            )
            
            self.metrics['failed_distributions'] += 1
            
            await self.event_emitter.emit('distribution_failed', {
                'request_id': request.request_id,
                'error': str(e)
            })
            
            return result
            
        finally:
            # Remove from active distributions
            self.active_distributions.pop(request.request_id, None)
            self.metrics['active_distributions'] = len(self.active_distributions)
    
    async def _execute_parallel_distribution(self, request: DistributionRequest) -> Dict[str, Dict[str, Any]]:
        """Execute distribution to all platforms in parallel."""        tasks = []
        
        for platform in request.platforms:
            task = self._distribute_to_platform(request, platform)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        platform_results = {}
        for i, platform in enumerate(request.platforms):
            if isinstance(results[i], Exception):
                platform_results[platform] = {
                    'success': False,
                    'error': str(results[i])
                }
            else:
                platform_results[platform] = results[i]
        
        return platform_results
    
    async def _execute_waterfall_distribution(self, request: DistributionRequest) -> Dict[str, Dict[str, Any]]:
        """Execute distribution to platforms sequentially."""        platform_results = {}
        
        for platform in request.platforms:
            try:
                result = await self._distribute_to_platform(request, platform)
                platform_results[platform] = result
                
                # If distribution fails and it's a critical platform, stop
                if not result.get('success', False) and self._is_critical_platform(platform):
                    self.logger.warning(f"Critical platform {platform} failed, stopping waterfall distribution")
                    break
                    
            except Exception as e:
                platform_results[platform] = {
                    'success': False,
                    'error': str(e)
                }
                
                if self._is_critical_platform(platform):
                    break
        
        return platform_results
    
    async def _execute_optimized_distribution(self, request: DistributionRequest) -> Dict[str, Dict[str, Any]]:
        """Execute distribution with optimization strategy."""        # Sort platforms by success rate and audience compatibility
        optimized_platforms = await self._optimize_platform_order(request)
        
        platform_results = {}
        
        for platform in optimized_platforms:
            try:
                result = await self._distribute_to_platform(request, platform)
                platform_results[platform] = result
                
                # Analyze result and adjust strategy if needed
                await self._analyze_distribution_result(platform, result)
                
            except Exception as e:
                platform_results[platform] = {
                    'success': False,
                    'error': str(e)
                }
        
        return platform_results
    
    async def _distribute_to_platform(self, request: DistributionRequest, platform: str) -> Dict[str, Any]:
        """Distribute content to a specific platform."""        adapter = self.platform_adapters.get(platform)
        if not adapter:
            raise ValueError(f"No adapter available for platform: {platform}")
        
        # Get platform-specific content adaptation
        content_adaptation = request.content_adaptations.get(platform, {})
        
        # Apply rate limiting
        await self._apply_rate_limiting(platform)
        
        # Execute platform distribution
        result = await adapter.distribute_content(
            content_id=request.content_id,
            adaptation=content_adaptation,
            metadata=request.metadata,
            targeting=request.targeting_options.get(platform, {}),
            monetization=request.monetization_settings.get(platform, {})
        )
        
        return result
    
    async def _load_platform_configurations(self) -> None:
        """Load platform configurations."""        # This would typically load from database or configuration files
        self.platform_configs = {
            'youtube': {
                'name': 'YouTube',
                'api_version': 'v3',
                'rate_limit': 10000,  # per day
                'supported_formats': ['video', 'audio'],
                'max_file_size': 128 * 1024 * 1024 * 1024,  # 128GB
                'required_fields': ['title', 'description']
            },
            'instagram': {
                'name': 'Instagram',
                'api_version': 'v17.0',
                'rate_limit': 200,  # per hour
                'supported_formats': ['image', 'video'],
                'max_file_size': 4 * 1024 * 1024 * 1024,  # 4GB
                'required_fields': ['caption']
            },
            'tiktok': {
                'name': 'TikTok',
                'api_version': 'v1',
                'rate_limit': 100,  # per hour
                'supported_formats': ['video'],
                'max_file_size': 2 * 1024 * 1024 * 1024,  # 2GB
                'required_fields': ['title']
            },
            'spotify': {
                'name': 'Spotify',
                'api_version': 'v1',
                'rate_limit': 1000,  # per hour
                'supported_formats': ['audio'],
                'max_file_size': 200 * 1024 * 1024,  # 200MB
                'required_fields': ['title', 'artist', 'album']
            },
            'facebook': {
                'name': 'Facebook',
                'api_version': 'v18.0',
                'rate_limit': 200,  # per hour
                'supported_formats': ['image', 'video', 'text'],
                'max_file_size': 10 * 1024 * 1024 * 1024,  # 10GB
                'required_fields': ['message']
            },
            'twitter': {
                'name': 'Twitter/X',
                'api_version': 'v2',
                'rate_limit': 300,  # per 15 minutes
                'supported_formats': ['image', 'video', 'text'],
                'max_file_size': 512 * 1024 * 1024,  # 512MB
                'required_fields': ['text']
            }
        }
    
    async def _initialize_platform_adapters(self) -> None:
        """Initialize platform adapters."""        # This would initialize actual platform adapters
        # For now, we'll create mock adapters
        for platform in self.platform_configs:
            # In real implementation, this would import and initialize actual adapters
            self.platform_adapters[platform] = type('MockAdapter', (), {
                'distribute_content': self._mock_platform_distribution
            })()
    
    async def _mock_platform_distribution(self, **kwargs) -> Dict[str, Any]:
        """Mock platform distribution for testing."""        await asyncio.sleep(0.1)  # Simulate API call
        return {
            'success': True,
            'platform_id': f"mock_{uuid4()}",
            'url': f"https://mock-platform.com/content/{uuid4()}",
            'published_at': datetime.utcnow().isoformat()
        }
    
    async def _shutdown_platform_adapters(self) -> None:
        """Shutdown platform adapters."""        for platform, adapter in self.platform_adapters.items():
            if hasattr(adapter, 'shutdown'):
                try:
                    await adapter.shutdown()
                except Exception as e:
                    self.logger.error(f"Error shutting down {platform} adapter: {e}")
    
    async def _start_background_tasks(self) -> None:
        """Start background processing tasks."""        # Start queue processor
        asyncio.create_task(self._process_distribution_queue())
        
        # Start metrics collector
        asyncio.create_task(self._collect_metrics())
    
    async def _process_distribution_queue(self) -> None:
        """Process scheduled distributions."""        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                # Find distributions ready for execution
                ready_distributions = [
                    req for req in self.distribution_queue
                    if req.schedule_time and req.schedule_time <= current_time
                ]
                
                # Execute ready distributions
                for request in ready_distributions:
                    if len(self.active_distributions) < self.max_concurrent_distributions:
                        self.distribution_queue.remove(request)
                        asyncio.create_task(self._execute_distribution(request))
                    else:
                        break  # Wait for capacity
                
                # Update queue size metric
                self.metrics['queue_size'] = len(self.distribution_queue)
                
                await asyncio.sleep(self.queue_processor_interval)
                
            except Exception as e:
                self.logger.error(f"Error in queue processor: {e}")
                await asyncio.sleep(self.queue_processor_interval)
    
    async def _collect_metrics(self) -> None:
        """Collect performance metrics."""        while self.is_running:
            try:
                # Update platform success rates
                for platform in self.platform_configs:
                    success_rate = await self._calculate_platform_success_rate(platform)
                    self.metrics['platform_success_rates'][platform] = success_rate
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(60)
    
    async def _calculate_platform_success_rate(self, platform: str) -> float:
        """Calculate success rate for a platform."""        # This would analyze historical data
        # For now, return a mock value
        return 0.95  # 95% success rate
    
    async def _apply_rate_limiting(self, platform: str) -> None:
        """Apply rate limiting for platform."""        # This would implement actual rate limiting logic
        # For now, just add a small delay
        await asyncio.sleep(0.01)
    
    async def _optimize_platform_order(self, request: DistributionRequest) -> List[str]:
        """Optimize platform order for distribution."""        # This would implement optimization logic based on:
        # - Platform success rates
        # - Audience compatibility
        # - Content type compatibility
        # - Current platform load
        
        # For now, return platforms sorted by success rate
        platform_scores = {}
        for platform in request.platforms:
            success_rate = self.metrics['platform_success_rates'].get(platform, 0.5)
            platform_scores[platform] = success_rate
        
        return sorted(request.platforms, key=lambda p: platform_scores.get(p, 0), reverse=True)
    
    async def _analyze_distribution_result(self, platform: str, result: Dict[str, Any]) -> None:
        """Analyze distribution result for optimization."""        # This would analyze results and update optimization parameters
        pass
    
    def _is_critical_platform(self, platform: str) -> bool:
        """Check if platform is critical for distribution."""        critical_platforms = self.config.get('critical_platforms', ['youtube', 'spotify'])
        return platform in critical_platforms
    
    def get_distribution_status(self, request_id: UUID) -> Optional[Dict[str, Any]]:
        """Get status of a distribution request."""        # Check active distributions
        if request_id in self.active_distributions:
            request = self.active_distributions[request_id]
            return {
                'status': 'active',
                'request': request,
                'started_at': request.created_at
            }
        
        # Check completed distributions
        if request_id in self.completed_distributions:
            result = self.completed_distributions[request_id]
            return {
                'status': 'completed',
                'result': result
            }
        
        # Check queued distributions
        for request in self.distribution_queue:
            if request.request_id == request_id:
                return {
                    'status': 'queued',
                    'request': request,
                    'position': self.distribution_queue.index(request)
                }
        
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""        return {
            **self.metrics,
            'timestamp': datetime.utcnow().isoformat(),
            'system_status': {
                'initialized': self.is_initialized,
                'running': self.is_running,
                'active_distributions': len(self.active_distributions),
                'queue_size': len(self.distribution_queue),
                'completed_distributions': len(self.completed_distributions)
            }
        }
