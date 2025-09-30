"""
🎯 Model Adapter - Multi-Model AI Integration System
=================================================

Enterprise-grade adapter for seamless integration with multiple AI models
(OpenAI, Anthropic, Google, Cohere) with intelligent routing and optimization.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - Backend Senior + ML Engineer + DevOps Expert
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import aiohttp
import asyncpg
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, validator
import tiktoken
import openai
import anthropic
import google.generativeai as genai
import cohere

from core.config import get_settings
from utils.exceptions import ModelError, ValidationError, RateLimitError
from monitoring.prompt_metrics import PromptMetricsCollector
from .cost_optimizer import CostOptimizer
from .security_validator import SecurityValidator

logger = logging.getLogger(__name__)
settings = get_settings()


class ModelProvider(Enum):
    """Supported AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    AZURE_OPENAI = "azure_openai"


class ModelCapability(Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    TEXT_COMPLETION = "text_completion"
    CHAT_COMPLETION = "chat_completion"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    MULTIMODAL = "multimodal"
    FUNCTION_CALLING = "function_calling"
    EMBEDDING = "embedding"


class ModelTier(Enum):
    """Model performance tiers"""
    PREMIUM = "premium"
    STANDARD = "standard"
    ECONOMY = "economy"
    EXPERIMENTAL = "experimental"


@dataclass
class ModelConfig:
    """Model configuration"""
    provider: ModelProvider
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 100000
    cost_per_1k_tokens: float = 0.002
    capabilities: List[ModelCapability] = field(default_factory=list)
    tier: ModelTier = ModelTier.STANDARD
    supports_streaming: bool = True
    supports_function_calling: bool = False
    context_window: int = 4096
    creator_economy_optimized: bool = False


@dataclass
class ModelResponse:
    """Standardized model response"""
    content: str
    provider: ModelProvider
    model: str
    usage: Dict[str, int]
    latency_ms: int
    cost: float
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    streaming: bool = False
    function_calls: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    safety_filtered: bool = False


class ModelRequest(BaseModel):
    """Model request structure"""
    prompt: str = Field(..., min_length=1, max_length=50000)
    model_preference: Optional[ModelProvider] = None
    specific_model: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    streaming: bool = False
    capabilities_required: List[ModelCapability] = Field(default_factory=list)
    creator_context: Dict[str, Any] = Field(default_factory=dict)
    priority: str = Field("normal", pattern="^(low|normal|high|critical)$")
    timeout: Optional[int] = Field(None, ge=1, le=300)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt content"""
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class BaseModelAdapter(ABC):
    """Base class for model adapters"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
        self.rate_limiter = {}
        self.last_request_time = {}
        self.request_count = 0
        self.token_count = 0
        self.cost_optimizer = CostOptimizer()
        self.security_validator = SecurityValidator()
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize model client"""
        pass
    
    @abstractmethod
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response from model"""
        pass
    
    @abstractmethod
    async def stream_generate(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Stream generate response from model"""
        pass
    
    async def check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old entries
        self.rate_limiter = {
            timestamp: count for timestamp, count in self.rate_limiter.items()
            if timestamp > minute_ago
        }
        
        # Count requests in last minute
        requests_last_minute = sum(self.rate_limiter.values())
        
        # Check RPM limit
        if requests_last_minute >= self.config.rate_limit_rpm:
            return False
        
        # Add current request
        self.rate_limiter[current_time] = 1
        return True
    
    async def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate request cost"""
        total_tokens = prompt_tokens + completion_tokens
        return (total_tokens / 1000) * self.config.cost_per_1k_tokens
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            # Fallback to approximate count
            return len(text.split()) * 1.3


class OpenAIAdapter(BaseModelAdapter):
    """OpenAI model adapter"""
    
    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        try:
            openai.api_key = self.config.api_key
            if self.config.base_url:
                openai.api_base = self.config.base_url
            
            # Test connection
            await openai.Model.alist()
            logger.info(f"OpenAI adapter initialized: {self.config.model_name}")
        
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI adapter: {e}")
            raise ModelError(f"OpenAI initialization failed: {e}")
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using OpenAI"""
        try:
            start_time = time.time()
            
            # Check rate limits
            if not await self.check_rate_limit():
                raise RateLimitError("Rate limit exceeded for OpenAI")
            
            # Security validation
            security_result = await self.security_validator.validate_prompt(request.prompt)
            if not security_result.is_safe:
                raise ValidationError(f"Prompt failed security validation: {security_result.issues}")
            
            # Prepare request
            openai_request = {
                "model": self.config.model_name,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "top_p": request.top_p or self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty
            }
            
            # Make request
            response = await openai.ChatCompletion.acreate(**openai_request)
            
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content
            usage = response.usage
            
            # Calculate cost
            cost = await self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)
            
            return ModelResponse(
                content=content,
                provider=ModelProvider.OPENAI,
                model=self.config.model_name,
                usage={
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                latency_ms=latency_ms,
                cost=cost,
                finish_reason=choice.finish_reason,
                metadata={"response_id": response.id}
            )
        
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise ModelError(f"OpenAI generation failed: {e}")
    
    async def stream_generate(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Stream generate response using OpenAI"""
        try:
            # Check rate limits
            if not await self.check_rate_limit():
                raise RateLimitError("Rate limit exceeded for OpenAI")
            
            # Prepare streaming request
            openai_request = {
                "model": self.config.model_name,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "stream": True
            }
            
            # Stream response
            stream = await openai.ChatCompletion.acreate(**openai_request)
            
            async for chunk in stream:
                if chunk.choices[0].delta.get("content"):
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise ModelError(f"OpenAI streaming failed: {e}")


class AnthropicAdapter(BaseModelAdapter):
    """Anthropic Claude model adapter"""
    
    async def initialize(self) -> None:
        """Initialize Anthropic client"""
        try:
            self.client = anthropic.AsyncAnthropic(api_key=self.config.api_key)
            logger.info(f"Anthropic adapter initialized: {self.config.model_name}")
        
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic adapter: {e}")
            raise ModelError(f"Anthropic initialization failed: {e}")
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using Anthropic Claude"""
        try:
            start_time = time.time()
            
            # Check rate limits
            if not await self.check_rate_limit():
                raise RateLimitError("Rate limit exceeded for Anthropic")
            
            # Make request
            response = await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                messages=[{"role": "user", "content": request.prompt}]
            )
            
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            # Extract response data
            content = response.content[0].text
            
            # Calculate tokens and cost
            prompt_tokens = self.count_tokens(request.prompt)
            completion_tokens = self.count_tokens(content)
            cost = await self.calculate_cost(prompt_tokens, completion_tokens)
            
            return ModelResponse(
                content=content,
                provider=ModelProvider.ANTHROPIC,
                model=self.config.model_name,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                latency_ms=latency_ms,
                cost=cost,
                finish_reason=response.stop_reason,
                metadata={"response_id": response.id}
            )
        
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise ModelError(f"Anthropic generation failed: {e}")
    
    async def stream_generate(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Stream generate response using Anthropic"""
        try:
            # Check rate limits
            if not await self.check_rate_limit():
                raise RateLimitError("Rate limit exceeded for Anthropic")
            
            # Stream response
            stream = await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                messages=[{"role": "user", "content": request.prompt}],
                stream=True
            )
            
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text
        
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise ModelError(f"Anthropic streaming failed: {e}")


class GoogleAdapter(BaseModelAdapter):
    """Google AI model adapter"""
    
    async def initialize(self) -> None:
        """Initialize Google client"""
        try:
            genai.configure(api_key=self.config.api_key)
            self.client = genai.GenerativeModel(self.config.model_name)
            logger.info(f"Google adapter initialized: {self.config.model_name}")
        
        except Exception as e:
            logger.error(f"Failed to initialize Google adapter: {e}")
            raise ModelError(f"Google initialization failed: {e}")
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using Google Gemini"""
        try:
            start_time = time.time()
            
            # Check rate limits
            if not await self.check_rate_limit():
                raise RateLimitError("Rate limit exceeded for Google")
            
            # Make request
            response = await self.client.generate_content_async(
                request.prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=request.max_tokens or self.config.max_tokens,
                    temperature=request.temperature or self.config.temperature,
                    top_p=request.top_p or self.config.top_p
                )
            )
            
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            # Extract response data
            content = response.text
            
            # Calculate tokens and cost
            prompt_tokens = self.count_tokens(request.prompt)
            completion_tokens = self.count_tokens(content)
            cost = await self.calculate_cost(prompt_tokens, completion_tokens)
            
            return ModelResponse(
                content=content,
                provider=ModelProvider.GOOGLE,
                model=self.config.model_name,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                latency_ms=latency_ms,
                cost=cost,
                finish_reason="completed",
                metadata={"safety_ratings": response.safety_ratings}
            )
        
        except Exception as e:
            logger.error(f"Google generation failed: {e}")
            raise ModelError(f"Google generation failed: {e}")
    
    async def stream_generate(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Stream generate response using Google"""
        try:
            # Check rate limits
            if not await self.check_rate_limit():
                raise RateLimitError("Rate limit exceeded for Google")
            
            # Stream response
            response = await self.client.generate_content_async(
                request.prompt,
                stream=True
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            logger.error(f"Google streaming failed: {e}")
            raise ModelError(f"Google streaming failed: {e}")


class CohereAdapter(BaseModelAdapter):
    """Cohere model adapter"""
    
    async def initialize(self) -> None:
        """Initialize Cohere client"""
        try:
            self.client = cohere.AsyncClient(api_key=self.config.api_key)
            logger.info(f"Cohere adapter initialized: {self.config.model_name}")
        
        except Exception as e:
            logger.error(f"Failed to initialize Cohere adapter: {e}")
            raise ModelError(f"Cohere initialization failed: {e}")
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response using Cohere"""
        try:
            start_time = time.time()
            
            # Check rate limits
            if not await self.check_rate_limit():
                raise RateLimitError("Rate limit exceeded for Cohere")
            
            # Make request
            response = await self.client.generate(
                model=self.config.model_name,
                prompt=request.prompt,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                p=request.top_p or self.config.top_p
            )
            
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            # Extract response data
            content = response.generations[0].text
            
            # Calculate tokens and cost
            prompt_tokens = self.count_tokens(request.prompt)
            completion_tokens = self.count_tokens(content)
            cost = await self.calculate_cost(prompt_tokens, completion_tokens)
            
            return ModelResponse(
                content=content,
                provider=ModelProvider.COHERE,
                model=self.config.model_name,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                latency_ms=latency_ms,
                cost=cost,
                finish_reason=response.generations[0].finish_reason,
                metadata={"generation_id": response.generations[0].id}
            )
        
        except Exception as e:
            logger.error(f"Cohere generation failed: {e}")
            raise ModelError(f"Cohere generation failed: {e}")
    
    async def stream_generate(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Stream generate response using Cohere"""
        try:
            # Check rate limits
            if not await self.check_rate_limit():
                raise RateLimitError("Rate limit exceeded for Cohere")
            
            # Stream response
            response = self.client.generate_stream(
                model=self.config.model_name,
                prompt=request.prompt,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            logger.error(f"Cohere streaming failed: {e}")
            raise ModelError(f"Cohere streaming failed: {e}")


class ModelAdapter:
    """
    🎯 Multi-Model AI Adapter System
    
    Enterprise-grade adapter providing:
    - Unified interface for multiple AI providers
    - Intelligent model routing and fallbacks
    - Cost optimization and rate limiting
    - Performance monitoring and caching
    - Creator economy optimizations
    - Security validation and compliance
    """
    
    def __init__(self):
        self.adapters: Dict[str, BaseModelAdapter] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.metrics_collector = PromptMetricsCollector()
        self.cost_optimizer = CostOptimizer()
        self.model_configs: Dict[str, ModelConfig] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize model adapter system"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=20
            )
            
            # Load model configurations
            await self._load_model_configs()
            
            # Initialize adapters
            await self._initialize_adapters()
            
            # Create database tables
            await self._create_tables()
            
            self._initialized = True
            logger.info("Model Adapter system initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Model Adapter: {e}")
            raise ModelError(f"Model Adapter initialization failed: {e}")
    
    async def _load_model_configs(self) -> None:
        """Load model configurations"""
        # Default model configurations
        self.model_configs = {
            "gpt-4": ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                api_key=settings.OPENAI_API_KEY,
                max_tokens=4096,
                cost_per_1k_tokens=0.03,
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT_COMPLETION,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.ANALYSIS
                ],
                tier=ModelTier.PREMIUM,
                creator_economy_optimized=True
            ),
            "gpt-3.5-turbo": ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                api_key=settings.OPENAI_API_KEY,
                max_tokens=4096,
                cost_per_1k_tokens=0.002,
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT_COMPLETION
                ],
                tier=ModelTier.STANDARD,
                creator_economy_optimized=True
            ),
            "claude-3": ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                api_key=settings.ANTHROPIC_API_KEY,
                max_tokens=4096,
                cost_per_1k_tokens=0.015,
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.ANALYSIS,
                    ModelCapability.CREATIVE_WRITING
                ],
                tier=ModelTier.PREMIUM,
                creator_economy_optimized=True
            ),
            "gemini-pro": ModelConfig(
                provider=ModelProvider.GOOGLE,
                model_name="gemini-pro",
                api_key=settings.GOOGLE_API_KEY,
                max_tokens=4096,
                cost_per_1k_tokens=0.00025,
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.MULTIMODAL
                ],
                tier=ModelTier.STANDARD,
                creator_economy_optimized=False
            ),
            "command": ModelConfig(
                provider=ModelProvider.COHERE,
                model_name="command",
                api_key=settings.COHERE_API_KEY,
                max_tokens=4096,
                cost_per_1k_tokens=0.001,
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.SUMMARIZATION
                ],
                tier=ModelTier.ECONOMY,
                creator_economy_optimized=False
            )
        }
    
    async def _initialize_adapters(self) -> None:
        """Initialize model adapters"""
        adapter_classes = {
            ModelProvider.OPENAI: OpenAIAdapter,
            ModelProvider.ANTHROPIC: AnthropicAdapter,
            ModelProvider.GOOGLE: GoogleAdapter,
            ModelProvider.COHERE: CohereAdapter
        }
        
        for model_name, config in self.model_configs.items():
            try:
                if config.provider in adapter_classes:
                    adapter_class = adapter_classes[config.provider]
                    adapter = adapter_class(config)
                    await adapter.initialize()
                    self.adapters[model_name] = adapter
                    logger.info(f"Initialized adapter for {model_name}")
            
            except Exception as e:
                logger.warning(f"Failed to initialize adapter for {model_name}: {e}")
    
    async def _create_tables(self) -> None:
        """Create database tables for model usage tracking"""
        create_model_usage_table = """
        CREATE TABLE IF NOT EXISTS model_usage (
            id SERIAL PRIMARY KEY,
            model_name VARCHAR(255) NOT NULL,
            provider VARCHAR(100) NOT NULL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            cost FLOAT,
            latency_ms INTEGER,
            success BOOLEAN DEFAULT TRUE,
            creator_context JSONB,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_model_performance_table = """
        CREATE TABLE IF NOT EXISTS model_performance (
            id SERIAL PRIMARY KEY,
            model_name VARCHAR(255) NOT NULL,
            avg_latency_ms FLOAT,
            success_rate FLOAT,
            avg_cost FLOAT,
            total_requests INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_model_usage_table)
            await conn.execute(create_model_performance_table)
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """
        Generate response using intelligent model routing
        
        Args:
            request: Model generation request
            
        Returns:
            Model response
        """
        try:
            # Select optimal model
            selected_model = await self._select_model(request)
            
            # Get adapter
            adapter = self.adapters.get(selected_model)
            if not adapter:
                raise ModelError(f"No adapter available for model: {selected_model}")
            
            # Generate response
            response = await adapter.generate(request)
            
            # Record usage metrics
            await self._record_usage(response, request.creator_context)
            
            # Cache response if appropriate
            await self._cache_response(request, response)
            
            logger.info(f"Generated response using {selected_model}")
            return response
        
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            # Try fallback model
            return await self._generate_with_fallback(request, str(e))
    
    async def stream_generate(
        self,
        request: ModelRequest
    ) -> AsyncGenerator[Tuple[str, ModelResponse], None]:
        """Stream generate response with intelligent routing"""
        try:
            # Select optimal model
            selected_model = await self._select_model(request)
            
            # Get adapter
            adapter = self.adapters.get(selected_model)
            if not adapter:
                raise ModelError(f"No adapter available for model: {selected_model}")
            
            # Stream response
            full_content = ""
            async for chunk in adapter.stream_generate(request):
                full_content += chunk
                yield chunk, None
            
            # Create final response object
            final_response = ModelResponse(
                content=full_content,
                provider=adapter.config.provider,
                model=selected_model,
                usage={"total_tokens": adapter.count_tokens(full_content)},
                latency_ms=0,
                cost=0.0,
                finish_reason="completed",
                streaming=True
            )
            
            # Record usage
            await self._record_usage(final_response, request.creator_context)
            
            yield "", final_response
        
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise ModelError(f"Streaming generation failed: {e}")
    
    async def _select_model(self, request: ModelRequest) -> str:
        """Select optimal model based on request parameters"""
        # Use specific model if requested
        if request.specific_model and request.specific_model in self.adapters:
            return request.specific_model
        
        # Filter by provider preference
        available_models = list(self.adapters.keys())
        if request.model_preference:
            available_models = [
                model for model in available_models
                if self.model_configs[model].provider == request.model_preference
            ]
        
        # Filter by capabilities
        if request.capabilities_required:
            filtered_models = []
            for model in available_models:
                config = self.model_configs[model]
                if all(cap in config.capabilities for cap in request.capabilities_required):
                    filtered_models.append(model)
            available_models = filtered_models
        
        # Filter by creator economy optimization
        if request.creator_context.get('creator_type'):
            creator_optimized = [
                model for model in available_models
                if self.model_configs[model].creator_economy_optimized
            ]
            if creator_optimized:
                available_models = creator_optimized
        
        # Select based on priority and performance
        if request.priority == "critical":
            # Use premium models for critical requests
            premium_models = [
                model for model in available_models
                if self.model_configs[model].tier == ModelTier.PREMIUM
            ]
            if premium_models:
                return premium_models[0]
        
        elif request.priority == "low":
            # Use economy models for low priority
            economy_models = [
                model for model in available_models
                if self.model_configs[model].tier == ModelTier.ECONOMY
            ]
            if economy_models:
                return economy_models[0]
        
        # Default to first available model
        if available_models:
            return available_models[0]
        
        # Fallback to first available adapter
        return list(self.adapters.keys())[0]
    
    async def _generate_with_fallback(
        self,
        request: ModelRequest,
        error_message: str
    ) -> ModelResponse:
        """Generate response using fallback model"""
        try:
            # Try cheaper/simpler models as fallbacks
            fallback_models = ["gpt-3.5-turbo", "command", "gemini-pro"]
            
            for model in fallback_models:
                if model in self.adapters:
                    try:
                        adapter = self.adapters[model]
                        response = await adapter.generate(request)
                        
                        # Add fallback metadata
                        response.metadata["fallback_used"] = True
                        response.metadata["original_error"] = error_message
                        
                        logger.warning(f"Used fallback model {model} due to error: {error_message}")
                        return response
                    
                    except Exception as fallback_error:
                        logger.warning(f"Fallback model {model} also failed: {fallback_error}")
                        continue
            
            raise ModelError(f"All models failed. Last error: {error_message}")
        
        except Exception as e:
            logger.error(f"Fallback generation failed: {e}")
            raise ModelError(f"All generation attempts failed: {e}")
    
    async def _record_usage(
        self,
        response: ModelResponse,
        creator_context: Dict[str, Any]
    ) -> None:
        """Record model usage metrics"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO model_usage 
                    (model_name, provider, prompt_tokens, completion_tokens, 
                     total_tokens, cost, latency_ms, creator_context)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, response.model, response.provider.value,
                    response.usage.get("prompt_tokens", 0),
                    response.usage.get("completion_tokens", 0),
                    response.usage.get("total_tokens", 0),
                    response.cost, response.latency_ms,
                    json.dumps(creator_context))
        
        except Exception as e:
            logger.warning(f"Failed to record usage metrics: {e}")
    
    async def _cache_response(
        self,
        request: ModelRequest,
        response: ModelResponse
    ) -> None:
        """Cache response for performance optimization"""
        try:
            # Create cache key
            cache_key = f"model_response:{hash(request.prompt)}"
            
            # Cache for 1 hour
            await self.redis_client.setex(
                cache_key,
                3600,
                json.dumps({
                    "content": response.content,
                    "model": response.model,
                    "cost": response.cost,
                    "cached_at": datetime.utcnow().isoformat()
                })
            )
        
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")
    
    async def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """Get performance metrics for a model"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        AVG(latency_ms) as avg_latency,
                        AVG(cost) as avg_cost,
                        COUNT(*) as total_requests,
                        COUNT(*) FILTER (WHERE success = true) as successful_requests
                    FROM model_usage 
                    WHERE model_name = $1 
                    AND used_at >= NOW() - INTERVAL '24 hours'
                """, model_name)
                
                if row:
                    success_rate = (row['successful_requests'] / row['total_requests']) if row['total_requests'] > 0 else 0
                    
                    return {
                        "model_name": model_name,
                        "avg_latency_ms": float(row['avg_latency'] or 0),
                        "avg_cost": float(row['avg_cost'] or 0),
                        "total_requests": row['total_requests'],
                        "success_rate": success_rate
                    }
                
                return {"model_name": model_name, "no_data": True}
        
        except Exception as e:
            logger.error(f"Failed to get model performance: {e}")
            return {"error": str(e)}
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their capabilities"""
        models = []
        for model_name, config in self.model_configs.items():
            if model_name in self.adapters:
                models.append({
                    "name": model_name,
                    "provider": config.provider.value,
                    "tier": config.tier.value,
                    "capabilities": [cap.value for cap in config.capabilities],
                    "cost_per_1k_tokens": config.cost_per_1k_tokens,
                    "max_tokens": config.max_tokens,
                    "creator_economy_optimized": config.creator_economy_optimized
                })
        
        return models
    
    async def cleanup(self) -> None:
        """Cleanup adapter resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            # Cleanup individual adapters
            for adapter in self.adapters.values():
                if hasattr(adapter, 'cleanup'):
                    await adapter.cleanup()
            
            logger.info("Model Adapter cleanup completed")
        
        except Exception as e:
            logger.error(f"Model Adapter cleanup failed: {e}")


# Global model adapter instance
model_adapter = ModelAdapter()