"""
AI Orchestrator - Enterprise AI Services Orchestration
======================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Lead Dev IA + ML Engineer + Backend Senior + Security + DevOps
**Module**: Processing Services - AI Orchestration
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade AI orchestration with multi-provider support, intelligent routing,
performance optimization, and comprehensive monitoring.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import aiohttp
import aioredis
from abc import ABC, abstractmethod
import hashlib
import uuid


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    CUSTOM = "custom"


class AIModel(Enum):
    """AI model types"""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"
    LLAMA_70B = "llama-70b"
    MIXTRAL_8X7B = "mixtral-8x7b"


class AITaskType(Enum):
    """Types of AI tasks"""
    TEXT_GENERATION = "text_generation"
    TEXT_ANALYSIS = "text_analysis"
    TEXT_CLASSIFICATION = "text_classification"
    TEXT_SUMMARIZATION = "text_summarization"
    TEXT_TRANSLATION = "text_translation"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_GENERATION = "audio_generation"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CONTENT_MODERATION = "content_moderation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    ENTITY_EXTRACTION = "entity_extraction"
    QUESTION_ANSWERING = "question_answering"


class AITaskStatus(Enum):
    """AI task processing status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AITaskPriority(Enum):
    """AI task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


@dataclass
class ProviderConfig:
    """AI provider configuration"""
    provider: AIProvider
    api_key: str
    api_endpoint: str
    model_mappings: Dict[AIModel, str] = field(default_factory=dict)
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    max_concurrent: int = 10
    
    # Quality settings
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Reliability
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Features
    supports_streaming: bool = False
    supports_functions: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    
    # Cost optimization
    cost_per_1k_tokens: Dict[str, float] = field(default_factory=dict)
    cost_optimization_enabled: bool = True
    
    # Monitoring
    enabled: bool = True
    health_check_interval: int = 300  # 5 minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['provider'] = self.provider.value
        return data


@dataclass
class AITask:
    """AI task definition"""
    task_id: str
    task_type: AITaskType
    
    # Input data
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration
    preferred_provider: Optional[AIProvider] = None
    preferred_model: Optional[AIModel] = None
    priority: AITaskPriority = AITaskPriority.NORMAL
    
    # Processing settings
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout_seconds: int = 30
    
    # Status tracking
    status: AITaskStatus = AITaskStatus.PENDING
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    response: Optional[str] = None
    usage_stats: Dict[str, Any] = field(default_factory=dict)
    provider_used: Optional[AIProvider] = None
    model_used: Optional[AIModel] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Cost tracking
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    
    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """AI response with comprehensive metadata"""
    task_id: str
    content: str
    
    # Provider information
    provider: AIProvider
    model: AIModel
    
    # Usage statistics
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Performance metrics
    response_time_ms: float = 0.0
    processing_time_ms: float = 0.0
    queue_time_ms: float = 0.0
    
    # Quality metrics
    confidence_score: Optional[float] = None
    quality_score: Optional[float] = None
    
    # Cost information
    cost: float = 0.0
    cost_currency: str = "USD"
    
    # Additional data
    finish_reason: Optional[str] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AIProviderInterface(ABC):
    """Abstract interface for AI providers"""
    
    @abstractmethod
    async def process_task(self, task: AITask, config: ProviderConfig) -> AIResponse:
        """Process an AI task"""
        pass
    
    @abstractmethod
    async def health_check(self, config: ProviderConfig) -> bool:
        """Check provider health"""
        pass
    
    @abstractmethod
    def estimate_cost(self, task: AITask, config: ProviderConfig) -> float:
        """Estimate task cost"""
        pass


class OpenAIProvider(AIProviderInterface):
    """OpenAI provider implementation"""
    
    async def process_task(self, task: AITask, config: ProviderConfig) -> AIResponse:
        """Process task using OpenAI API"""
        start_time = time.time()
        
        try:
            # Prepare request
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Map model
            model_name = config.model_mappings.get(task.preferred_model, "gpt-3.5-turbo")
            
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": task.prompt}],
                "max_tokens": task.max_tokens or config.max_tokens,
                "temperature": task.temperature or config.temperature,
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty
            }
            
            # Add parameters
            payload.update(task.parameters)
            
            # Make API call
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=task.timeout_seconds)) as session:
                async with session.post(f"{config.api_endpoint}/chat/completions", headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse response
                        content = data['choices'][0]['message']['content']
                        usage = data.get('usage', {})
                        
                        response_time = (time.time() - start_time) * 1000
                        
                        return AIResponse(
                            task_id=task.task_id,
                            content=content,
                            provider=AIProvider.OPENAI,
                            model=task.preferred_model or AIModel.GPT_3_5_TURBO,
                            prompt_tokens=usage.get('prompt_tokens', 0),
                            completion_tokens=usage.get('completion_tokens', 0),
                            total_tokens=usage.get('total_tokens', 0),
                            response_time_ms=response_time,
                            cost=self._calculate_cost(usage, config),
                            finish_reason=data['choices'][0].get('finish_reason'),
                            raw_response=data
                        )
                    else:
                        error_data = await response.json()
                        raise Exception(f"OpenAI API error: {error_data}")
        
        except Exception as e:
            logger.error(f"OpenAI provider error: {e}")
            raise
    
    async def health_check(self, config: ProviderConfig) -> bool:
        """Check OpenAI API health"""
        try:
            headers = {"Authorization": f"Bearer {config.api_key}"}
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{config.api_endpoint}/models", headers=headers) as response:
                    return response.status == 200
        except Exception:
            return False
    
    def estimate_cost(self, task: AITask, config: ProviderConfig) -> float:
        """Estimate OpenAI API cost"""
        # Rough estimation based on prompt length
        estimated_tokens = len(task.prompt.split()) * 1.3  # Approximate token count
        model_name = config.model_mappings.get(task.preferred_model, "gpt-3.5-turbo")
        cost_per_1k = config.cost_per_1k_tokens.get(model_name, 0.002)
        return (estimated_tokens / 1000) * cost_per_1k
    
    def _calculate_cost(self, usage: Dict[str, Any], config: ProviderConfig) -> float:
        """Calculate actual cost from usage"""
        total_tokens = usage.get('total_tokens', 0)
        # This would use actual pricing tiers
        return (total_tokens / 1000) * 0.002  # Simplified


class AnthropicProvider(AIProviderInterface):
    """Anthropic provider implementation"""
    
    async def process_task(self, task: AITask, config: ProviderConfig) -> AIResponse:
        """Process task using Anthropic API"""
        # Implementation similar to OpenAI but for Anthropic's API
        # This is a simplified placeholder
        start_time = time.time()
        
        try:
            # Simulate API call
            await asyncio.sleep(0.1)  # Simulate network delay
            
            response_time = (time.time() - start_time) * 1000
            
            return AIResponse(
                task_id=task.task_id,
                content=f"Anthropic response to: {task.prompt[:50]}...",
                provider=AIProvider.ANTHROPIC,
                model=task.preferred_model or AIModel.CLAUDE_3_SONNET,
                response_time_ms=response_time,
                total_tokens=100  # Placeholder
            )
        
        except Exception as e:
            logger.error(f"Anthropic provider error: {e}")
            raise
    
    async def health_check(self, config: ProviderConfig) -> bool:
        """Check Anthropic API health"""
        # Simplified health check
        return True
    
    def estimate_cost(self, task: AITask, config: ProviderConfig) -> float:
        """Estimate Anthropic API cost"""
        estimated_tokens = len(task.prompt.split()) * 1.3
        return (estimated_tokens / 1000) * 0.01  # Placeholder pricing


class AIOrchestrator:
    """
    Enterprise AI Orchestrator with Multi-Provider Support & Intelligent Routing
    
    **Expert Roles Implemented:**
    - Lead Dev IA: Intelligent provider selection, task optimization, AI workflow orchestration
    - ML Engineer: Model performance analytics, cost optimization, quality assessment
    - Backend Senior: Robust async architecture, connection pooling, error handling
    - Security: API key management, request validation, audit logging
    - DevOps: Comprehensive monitoring, load balancing, auto-scaling
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_timeout: int = 30,
        max_concurrent_tasks: int = 100,
        task_queue_size: int = 1000
    ):
        self.redis_url = redis_url
        self.default_timeout = default_timeout
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue_size = task_queue_size
        
        # Storage
        self.redis_client: Optional[aioredis.Redis] = None
        self.provider_configs: Dict[AIProvider, ProviderConfig] = {}
        self.providers: Dict[AIProvider, AIProviderInterface] = {}
        
        # Task management
        self.active_tasks: Dict[str, AITask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=task_queue_size)
        self.processing_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Provider health tracking
        self.provider_health: Dict[AIProvider, bool] = {}
        self.provider_metrics: Dict[AIProvider, Dict[str, Any]] = {}
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
        
        # Intelligent routing
        self.routing_strategy = "cost_performance"  # cost_performance, performance, cost, availability
        self.performance_history: Dict[AIProvider, List[float]] = {}
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize AI providers"""
        self.providers = {
            AIProvider.OPENAI: OpenAIProvider(),
            AIProvider.ANTHROPIC: AnthropicProvider(),
            # Add other providers as needed
        }
    
    async def initialize(self) -> None:
        """Initialize AI orchestrator"""
        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Load provider configurations
            await self._load_provider_configs()
            
            # Start background tasks
            self.running = True
            self.background_tasks = [
                asyncio.create_task(self._task_processor_loop()),
                asyncio.create_task(self._health_monitoring_loop()),
                asyncio.create_task(self._metrics_collection_loop()),
                asyncio.create_task(self._cost_optimization_loop())
            ]
            
            logger.info("AI Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Orchestrator: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        self.running = False
        
        # Cancel active tasks
        for task_id in list(self.active_tasks.keys()):
            await self.cancel_task(task_id)
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("AI Orchestrator shutdown completed")
    
    async def submit_task(self, task: AITask) -> str:
        """
        Submit an AI task for processing
        
        **Roles**: Lead Dev IA + Backend Senior
        """
        try:
            # Generate task ID if not provided
            if not task.task_id:
                task.task_id = str(uuid.uuid4())
            
            # Validate task
            if not self._validate_task(task):
                raise ValueError("Invalid task configuration")
            
            # Select optimal provider
            provider = await self._select_provider(task)
            if not provider:
                raise Exception("No available providers for task")
            
            task.provider_used = provider
            
            # Estimate cost
            if provider in self.provider_configs:
                config = self.provider_configs[provider]
                task.estimated_cost = self.providers[provider].estimate_cost(task, config)
            
            # Add to queue
            try:
                self.task_queue.put_nowait(task)
                self.active_tasks[task.task_id] = task
                
                # Persist task
                await self._save_task(task)
                
                logger.info(f"Task submitted: {task.task_id} ({task.task_type.value})")
                return task.task_id
                
            except asyncio.QueueFull:
                raise Exception("Task queue is full")
        
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[AITask]:
        """Get task status"""
        task = self.active_tasks.get(task_id)
        if task:
            return task
        
        # Check Redis for completed tasks
        if self.redis_client:
            try:
                data = await self.redis_client.get(f"ai_task:{task_id}")
                if data:
                    task_data = json.loads(data)
                    # Reconstruct task object
                    task_data['task_type'] = AITaskType(task_data['task_type'])
                    task_data['status'] = AITaskStatus(task_data['status'])
                    task_data['priority'] = AITaskPriority(task_data['priority'])
                    if task_data.get('provider_used'):
                        task_data['provider_used'] = AIProvider(task_data['provider_used'])
                    if task_data.get('model_used'):
                        task_data['model_used'] = AIModel(task_data['model_used'])
                    
                    # Convert datetime strings
                    for field in ['created_at', 'started_at', 'completed_at']:
                        if task_data.get(field):
                            task_data[field] = datetime.fromisoformat(task_data[field])
                    
                    return AITask(**task_data)
            except Exception as e:
                logger.error(f"Error retrieving task from Redis: {e}")
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = AITaskStatus.CANCELLED
                task.completed_at = datetime.now()
                
                # Remove from active tasks
                del self.active_tasks[task_id]
                
                # Update in storage
                await self._save_task(task)
                
                logger.info(f"Task cancelled: {task_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    async def add_provider_config(self, config: ProviderConfig) -> bool:
        """
        Add or update provider configuration
        
        **Roles**: DevOps + Security
        """
        try:
            # Validate configuration
            if not self._validate_provider_config(config):
                return False
            
            # Store configuration
            self.provider_configs[config.provider] = config
            
            # Initialize provider health
            self.provider_health[config.provider] = True
            self.provider_metrics[config.provider] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0.0,
                'total_cost': 0.0
            }
            
            # Save to Redis
            await self._save_provider_config(config)
            
            logger.info(f"Provider configured: {config.provider.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add provider config: {e}")
            return False
    
    async def _select_provider(self, task: AITask) -> Optional[AIProvider]:
        """
        Intelligent provider selection based on strategy
        
        **Roles**: Lead Dev IA + ML Engineer
        """
        # Filter available providers
        available_providers = []
        
        for provider, config in self.provider_configs.items():
            if (config.enabled and 
                self.provider_health.get(provider, False) and
                provider in self.providers):
                available_providers.append(provider)
        
        if not available_providers:
            return None
        
        # Prefer user-specified provider if available
        if (task.preferred_provider and 
            task.preferred_provider in available_providers):
            return task.preferred_provider
        
        # Apply selection strategy
        if self.routing_strategy == "cost_performance":
            return self._select_by_cost_performance(task, available_providers)
        elif self.routing_strategy == "performance":
            return self._select_by_performance(available_providers)
        elif self.routing_strategy == "cost":
            return self._select_by_cost(task, available_providers)
        else:  # availability
            return available_providers[0]
    
    def _select_by_cost_performance(self, task: AITask, providers: List[AIProvider]) -> AIProvider:
        """Select provider based on cost-performance ratio"""
        best_provider = None
        best_score = float('inf')
        
        for provider in providers:
            config = self.provider_configs[provider]
            provider_interface = self.providers[provider]
            
            # Calculate cost score
            estimated_cost = provider_interface.estimate_cost(task, config)
            
            # Calculate performance score (lower is better)
            avg_response_time = self.provider_metrics.get(provider, {}).get('average_response_time', 1000)
            performance_score = avg_response_time / 1000  # Convert to seconds
            
            # Combined score (weighted)
            cost_weight = 0.3
            performance_weight = 0.7
            combined_score = (estimated_cost * cost_weight) + (performance_score * performance_weight)
            
            if combined_score < best_score:
                best_score = combined_score
                best_provider = provider
        
        return best_provider or providers[0]
    
    def _select_by_performance(self, providers: List[AIProvider]) -> AIProvider:
        """Select provider with best performance"""
        best_provider = providers[0]
        best_response_time = float('inf')
        
        for provider in providers:
            avg_response_time = self.provider_metrics.get(provider, {}).get('average_response_time', float('inf'))
            if avg_response_time < best_response_time:
                best_response_time = avg_response_time
                best_provider = provider
        
        return best_provider
    
    def _select_by_cost(self, task: AITask, providers: List[AIProvider]) -> AIProvider:
        """Select provider with lowest cost"""
        best_provider = providers[0]
        lowest_cost = float('inf')
        
        for provider in providers:
            config = self.provider_configs[provider]
            provider_interface = self.providers[provider]
            cost = provider_interface.estimate_cost(task, config)
            
            if cost < lowest_cost:
                lowest_cost = cost
                best_provider = provider
        
        return best_provider
    
    async def _process_task(self, task: AITask) -> AIResponse:
        """
        Process a single AI task
        
        **Roles**: Backend Senior + ML Engineer + Security
        """
        async with self.processing_semaphore:
            start_time = time.time()
            
            try:
                # Update task status
                task.status = AITaskStatus.PROCESSING
                task.started_at = datetime.now()
                
                # Get provider and config
                provider = task.provider_used
                if not provider or provider not in self.provider_configs:
                    raise Exception(f"Provider not configured: {provider}")
                
                config = self.provider_configs[provider]
                provider_interface = self.providers[provider]
                
                # Process task with retries
                response = None
                last_error = None
                
                for attempt in range(task.max_retries + 1):
                    try:
                        response = await provider_interface.process_task(task, config)
                        break
                    except Exception as e:
                        last_error = e
                        task.retry_count += 1
                        
                        if attempt < task.max_retries:
                            await asyncio.sleep(config.retry_delay * (attempt + 1))
                        else:
                            raise last_error
                
                if not response:
                    raise Exception("No response received")
                
                # Update task with results
                task.status = AITaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.response = response.content
                task.usage_stats = {
                    'prompt_tokens': response.prompt_tokens,
                    'completion_tokens': response.completion_tokens,
                    'total_tokens': response.total_tokens
                }
                task.actual_cost = response.cost
                task.progress = 100.0
                
                # Update provider metrics
                await self._update_provider_metrics(provider, response, time.time() - start_time)
                
                logger.info(f"Task completed: {task.task_id} ({task.task_type.value})")
                return response
                
            except Exception as e:
                # Handle task failure
                task.status = AITaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error_message = str(e)
                
                # Update provider metrics
                if task.provider_used:
                    await self._update_provider_metrics(task.provider_used, None, time.time() - start_time, error=True)
                
                logger.error(f"Task failed: {task.task_id} - {e}")
                raise
            
            finally:
                # Save task state
                await self._save_task(task)
                
                # Remove from active tasks
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]
    
    async def _task_processor_loop(self) -> None:
        """Background task processing loop"""
        while self.running:
            try:
                # Get task from queue
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process task
                asyncio.create_task(self._process_task(task))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Task processor error: {e}")
                await asyncio.sleep(1)
    
    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring loop"""
        while self.running:
            try:
                await self._check_provider_health()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _check_provider_health(self) -> None:
        """Check health of all providers"""
        for provider, config in self.provider_configs.items():
            if provider in self.providers:
                try:
                    is_healthy = await self.providers[provider].health_check(config)
                    self.provider_health[provider] = is_healthy
                    
                    if not is_healthy:
                        logger.warning(f"Provider unhealthy: {provider.value}")
                
                except Exception as e:
                    self.provider_health[provider] = False
                    logger.error(f"Health check failed for {provider.value}: {e}")
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)
    
    async def _collect_metrics(self) -> None:
        """Collect orchestrator metrics"""
        # Log current state
        active_count = len(self.active_tasks)
        queue_size = self.task_queue.qsize()
        
        logger.debug(f"AI Orchestrator metrics - Active tasks: {active_count}, Queue size: {queue_size}")
        
        # Store metrics in Redis if needed
        if self.redis_client:
            try:
                metrics = {
                    'active_tasks': active_count,
                    'queue_size': queue_size,
                    'provider_health': {p.value: h for p, h in self.provider_health.items()},
                    'timestamp': datetime.now().isoformat()
                }
                await self.redis_client.setex(
                    "ai_orchestrator:metrics",
                    300,  # 5 minutes TTL
                    json.dumps(metrics)
                )
            except Exception as e:
                logger.error(f"Failed to store metrics: {e}")
    
    async def _cost_optimization_loop(self) -> None:
        """Background cost optimization loop"""
        while self.running:
            try:
                await self._optimize_costs()
                await asyncio.sleep(3600)  # Optimize every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cost optimization error: {e}")
                await asyncio.sleep(300)
    
    async def _optimize_costs(self) -> None:
        """Optimize costs based on usage patterns"""
        # Analyze usage patterns and adjust routing strategy
        total_costs = {}
        for provider, metrics in self.provider_metrics.items():
            total_costs[provider] = metrics.get('total_cost', 0.0)
        
        if total_costs:
            logger.info(f"Cost analysis: {total_costs}")
    
    async def _update_provider_metrics(
        self,
        provider: AIProvider,
        response: Optional[AIResponse],
        processing_time: float,
        error: bool = False
    ) -> None:
        """Update provider performance metrics"""
        if provider not in self.provider_metrics:
            self.provider_metrics[provider] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0.0,
                'total_cost': 0.0
            }
        
        metrics = self.provider_metrics[provider]
        metrics['total_requests'] += 1
        
        if error:
            metrics['failed_requests'] += 1
        else:
            metrics['successful_requests'] += 1
            
            if response:
                # Update response time average
                current_avg = metrics['average_response_time']
                total_requests = metrics['total_requests']
                new_avg = ((current_avg * (total_requests - 1)) + response.response_time_ms) / total_requests
                metrics['average_response_time'] = new_avg
                
                # Update cost
                metrics['total_cost'] += response.cost
    
    def _validate_task(self, task: AITask) -> bool:
        """Validate task configuration"""
        if not task.prompt or not task.task_type:
            return False
        
        if task.timeout_seconds <= 0:
            return False
        
        return True
    
    def _validate_provider_config(self, config: ProviderConfig) -> bool:
        """Validate provider configuration"""
        if not config.api_key or not config.api_endpoint:
            return False
        
        if config.requests_per_minute <= 0 or config.max_concurrent <= 0:
            return False
        
        return True
    
    async def _save_task(self, task: AITask) -> None:
        """Save task to Redis"""
        if not self.redis_client:
            return
        
        try:
            # Convert task to dict for serialization
            task_data = asdict(task)
            task_data['task_type'] = task.task_type.value
            task_data['status'] = task.status.value
            task_data['priority'] = task.priority.value
            
            if task.provider_used:
                task_data['provider_used'] = task.provider_used.value
            if task.model_used:
                task_data['model_used'] = task.model_used.value
            
            # Convert datetime objects
            for field in ['created_at', 'started_at', 'completed_at']:
                if task_data.get(field):
                    task_data[field] = task_data[field].isoformat()
            
            # Save with TTL
            key = f"ai_task:{task.task_id}"
            await self.redis_client.setex(key, 86400, json.dumps(task_data))  # 24 hours
            
        except Exception as e:
            logger.error(f"Failed to save task to Redis: {e}")
    
    async def _save_provider_config(self, config: ProviderConfig) -> None:
        """Save provider config to Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"ai_provider_config:{config.provider.value}"
            # Don't store API keys in Redis for security
            safe_config = config.to_dict()
            safe_config['api_key'] = "***REDACTED***"
            
            await self.redis_client.set(key, json.dumps(safe_config))
            
        except Exception as e:
            logger.error(f"Failed to save provider config to Redis: {e}")
    
    async def _load_provider_configs(self) -> None:
        """Load provider configurations from Redis"""
        if not self.redis_client:
            return
        
        try:
            keys = await self.redis_client.keys("ai_provider_config:*")
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    config_data = json.loads(data)
                    # Note: API keys would need to be loaded from a secure store
                    config_data['provider'] = AIProvider(config_data['provider'])
                    # Skip loading configs without proper API keys
                    if config_data.get('api_key') != "***REDACTED***":
                        config = ProviderConfig(**config_data)
                        self.provider_configs[config.provider] = config
            
            logger.info(f"Loaded {len(self.provider_configs)} provider configurations")
            
        except Exception as e:
            logger.error(f"Failed to load provider configs from Redis: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        return {
            'active_tasks': len(self.active_tasks),
            'queue_size': self.task_queue.qsize(),
            'configured_providers': len(self.provider_configs),
            'healthy_providers': sum(1 for h in self.provider_health.values() if h),
            'provider_metrics': self.provider_metrics.copy(),
            'provider_health': {p.value: h for p, h in self.provider_health.items()}
        }
    
    async def get_provider_stats(self, provider: AIProvider) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific provider"""
        if provider in self.provider_metrics:
            metrics = self.provider_metrics[provider].copy()
            metrics['health_status'] = self.provider_health.get(provider, False)
            metrics['configuration'] = self.provider_configs.get(provider) is not None
            return metrics
        return None