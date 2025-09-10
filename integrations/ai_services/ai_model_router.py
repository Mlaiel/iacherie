"""AI Model Router - Intelligent AI Service Selection and Routing System
====================================================================

Advanced AI model selection and routing system that intelligently chooses
the best AI service based on requirements, cost, performance, and availability.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import random
from collections import defaultdict, deque

import aiohttp
import aioredis
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)


class AIServiceType(Enum):
    """AI service categories."""
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTENT_MODERATION = "content_moderation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    CODE_GENERATION = "code_generation"


class ModelCapability(Enum):
    """Model capability levels."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class RoutingStrategy(Enum):
    """AI model routing strategies."""
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"
    BALANCED = "balanced"
    FAILOVER = "failover"
    LOAD_BALANCED = "load_balanced"


@dataclass
class AIProvider:
    """AI service provider configuration."""
    name: str
    service_type: AIServiceType
    endpoint_url: str
    api_key: str
    model_id: str
    capability: ModelCapability
    cost_per_request: float
    cost_per_token: float
    max_tokens: int
    avg_latency_ms: float
    availability: float
    rate_limit_requests: int
    rate_limit_tokens: int
    quality_score: float
    supports_streaming: bool = False
    supports_batch: bool = False
    region: str = "global"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteRequest:
    """AI routing request configuration."""
    service_type: AIServiceType
    prompt: str
    strategy: RoutingStrategy = RoutingStrategy.BALANCED
    max_cost: Optional[float] = None
    max_latency_ms: Optional[int] = None
    min_quality: Optional[float] = None
    required_capability: Optional[ModelCapability] = None
    user_id: Optional[str] = None
    priority: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteResponse:
    """AI routing response."""
    provider: AIProvider
    estimated_cost: float
    estimated_latency_ms: float
    confidence_score: float
    fallback_providers: List[AIProvider]
    routing_reason: str
    request_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AIModelRouter:
    """Advanced AI model routing and selection system."""
    
    def __init__(self, redis_url: str = None):
        self.providers: Dict[str, Dict[AIServiceType, List[AIProvider]]] = defaultdict(lambda: defaultdict(list))
        self.performance_cache = {}
        self.cost_cache = {}
        self.redis_client = None
        self.redis_url = redis_url
        
        # Metrics
        self.routing_counter = Counter('ai_routing_requests_total', 'Total AI routing requests', ['provider', 'service_type'])
        self.latency_histogram = Histogram('ai_routing_latency_seconds', 'AI routing latency', ['provider', 'service_type'])
        self.cost_gauge = Gauge('ai_routing_cost_total', 'Total AI routing costs', ['provider', 'service_type'])
        self.quality_gauge = Gauge('ai_routing_quality_score', 'AI routing quality scores', ['provider', 'service_type'])
        
        # Load balancing state
        self.provider_loads: Dict[str, int] = defaultdict(int)
        self.provider_health: Dict[str, bool] = defaultdict(lambda: True)
        self.last_health_check: Dict[str, datetime] = {}
        
        # Performance tracking
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.cost_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Initialize default providers
        self._initialize_default_providers()
    
    async def initialize(self):
        """Initialize the AI model router."""
        try:
            if self.redis_url:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)
            
            # Start health check task
            asyncio.create_task(self._health_check_loop())
            
            logger.info("AI model router initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI model router: {str(e)}")
            raise
    
    def _initialize_default_providers(self):
        """Initialize default AI service providers."""
        # OpenAI providers
        openai_text = AIProvider(
            name="openai",
            service_type=AIServiceType.TEXT_GENERATION,
            endpoint_url="https://api.openai.com/v1/chat/completions",
            api_key="",
            model_id="gpt-4-turbo-preview",
            capability=ModelCapability.PREMIUM,
            cost_per_request=0.01,
            cost_per_token=0.00003,
            max_tokens=128000,
            avg_latency_ms=2000,
            availability=0.99,
            rate_limit_requests=3500,
            rate_limit_tokens=90000,
            quality_score=0.95,
            supports_streaming=True,
            supports_batch=True
        )
        
        openai_image = AIProvider(
            name="openai",
            service_type=AIServiceType.IMAGE_GENERATION,
            endpoint_url="https://api.openai.com/v1/images/generations",
            api_key="",
            model_id="dall-e-3",
            capability=ModelCapability.PREMIUM,
            cost_per_request=0.04,
            cost_per_token=0.0,
            max_tokens=0,
            avg_latency_ms=30000,
            availability=0.98,
            rate_limit_requests=50,
            rate_limit_tokens=0,
            quality_score=0.92,
            supports_streaming=False,
            supports_batch=False
        )
        
        # Anthropic providers
        anthropic_text = AIProvider(
            name="anthropic",
            service_type=AIServiceType.TEXT_GENERATION,
            endpoint_url="https://api.anthropic.com/v1/messages",
            api_key="",
            model_id="claude-3-opus-20240229",
            capability=ModelCapability.PREMIUM,
            cost_per_request=0.015,
            cost_per_token=0.000075,
            max_tokens=200000,
            avg_latency_ms=2500,
            availability=0.97,
            rate_limit_requests=1000,
            rate_limit_tokens=40000,
            quality_score=0.96,
            supports_streaming=True,
            supports_batch=False
        )
        
        # Cohere providers
        cohere_text = AIProvider(
            name="cohere",
            service_type=AIServiceType.TEXT_GENERATION,
            endpoint_url="https://api.cohere.ai/v1/generate",
            api_key="",
            model_id="command",
            capability=ModelCapability.STANDARD,
            cost_per_request=0.0025,
            cost_per_token=0.000015,
            max_tokens=4096,
            avg_latency_ms=1500,
            availability=0.95,
            rate_limit_requests=10000,
            rate_limit_tokens=1000000,
            quality_score=0.85,
            supports_streaming=True,
            supports_batch=True
        )
        
        # Stability AI providers
        stability_image = AIProvider(
            name="stability",
            service_type=AIServiceType.IMAGE_GENERATION,
            endpoint_url="https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            api_key="",
            model_id="stable-diffusion-xl-1024-v1-0",
            capability=ModelCapability.ADVANCED,
            cost_per_request=0.02,
            cost_per_token=0.0,
            max_tokens=0,
            avg_latency_ms=15000,
            availability=0.94,
            rate_limit_requests=150,
            rate_limit_tokens=0,
            quality_score=0.88,
            supports_streaming=False,
            supports_batch=True
        )
        
        # ElevenLabs providers
        elevenlabs_tts = AIProvider(
            name="elevenlabs",
            service_type=AIServiceType.TEXT_TO_SPEECH,
            endpoint_url="https://api.elevenlabs.io/v1/text-to-speech",
            api_key="",
            model_id="eleven_monolingual_v1",
            capability=ModelCapability.PREMIUM,
            cost_per_request=0.006,
            cost_per_token=0.0,
            max_tokens=5000,
            avg_latency_ms=8000,
            availability=0.96,
            rate_limit_requests=200,
            rate_limit_tokens=0,
            quality_score=0.93,
            supports_streaming=True,
            supports_batch=False
        )
        
        # Register providers
        self.register_provider(openai_text)
        self.register_provider(openai_image)
        self.register_provider(anthropic_text)
        self.register_provider(cohere_text)
        self.register_provider(stability_image)
        self.register_provider(elevenlabs_tts)
    
    def register_provider(self, provider: AIProvider):
        """Register a new AI service provider."""
        try:
            self.providers[provider.name][provider.service_type].append(provider)
            self.provider_health[f"{provider.name}_{provider.service_type.value}"] = True
            
            logger.info(f"Registered AI provider: {provider.name} for {provider.service_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to register provider {provider.name}: {str(e)}")
            raise
    
    async def route_request(self, request: RouteRequest) -> RouteResponse:
        """Route AI request to best available provider."""
        start_time = time.time()
        request_id = hashlib.md5(f"{request.prompt}_{request.service_type.value}_{time.time()}".encode()).hexdigest()
        
        try:
            # Get available providers for service type
            available_providers = []
            for provider_name, services in self.providers.items():
                if request.service_type in services:
                    for provider in services[request.service_type]:
                        health_key = f"{provider.name}_{provider.service_type.value}"
                        if self.provider_health.get(health_key, True):
                            available_providers.append(provider)
            
            if not available_providers:
                raise ValueError(f"No available providers for {request.service_type.value}")
            
            # Filter by requirements
            filtered_providers = self._filter_providers(available_providers, request)
            
            if not filtered_providers:
                raise ValueError(f"No providers meet requirements for {request.service_type.value}")
            
            # Score and rank providers
            scored_providers = await self._score_providers(filtered_providers, request)
            
            # Select best provider based on strategy
            selected_provider = self._select_provider(scored_providers, request.strategy)
            
            # Get fallback providers
            fallback_providers = [p[0] for p in scored_providers[1:6]]  # Top 5 alternatives
            
            # Calculate estimates
            estimated_cost = self._calculate_cost(selected_provider, request)
            estimated_latency = self._estimate_latency(selected_provider, request)
            confidence_score = scored_providers[0][1]
            
            # Update metrics
            self.routing_counter.labels(
                provider=selected_provider.name,
                service_type=selected_provider.service_type.value
            ).inc()
            
            processing_time = time.time() - start_time
            self.latency_histogram.labels(
                provider=selected_provider.name,
                service_type=selected_provider.service_type.value
            ).observe(processing_time)
            
            # Update load tracking
            provider_key = f"{selected_provider.name}_{selected_provider.service_type.value}"
            self.provider_loads[provider_key] += 1
            
            return RouteResponse(
                provider=selected_provider,
                estimated_cost=estimated_cost,
                estimated_latency_ms=estimated_latency,
                confidence_score=confidence_score,
                fallback_providers=fallback_providers,
                routing_reason=f"Selected based on {request.strategy.value} strategy",
                request_id=request_id
            )
            
        except Exception as e:
            logger.error(f"Failed to route AI request: {str(e)}")
            raise
    
    def _filter_providers(self, providers: List[AIProvider], request: RouteRequest) -> List[AIProvider]:
        """Filter providers based on request requirements."""
        filtered = []
        
        for provider in providers:
            # Check cost constraint
            if request.max_cost is not None:
                estimated_cost = self._calculate_cost(provider, request)
                if estimated_cost > request.max_cost:
                    continue
            
            # Check latency constraint
            if request.max_latency_ms is not None:
                if provider.avg_latency_ms > request.max_latency_ms:
                    continue
            
            # Check quality constraint
            if request.min_quality is not None:
                if provider.quality_score < request.min_quality:
                    continue
            
            # Check capability constraint
            if request.required_capability is not None:
                capability_order = [
                    ModelCapability.BASIC,
                    ModelCapability.STANDARD,
                    ModelCapability.ADVANCED,
                    ModelCapability.PREMIUM,
                    ModelCapability.ENTERPRISE
                ]
                if capability_order.index(provider.capability) < capability_order.index(request.required_capability):
                    continue
            
            filtered.append(provider)
        
        return filtered
    
    async def _score_providers(self, providers: List[AIProvider], request: RouteRequest) -> List[Tuple[AIProvider, float]]:
        """Score providers based on multiple criteria."""
        scored_providers = []
        
        for provider in providers:
            score = 0.0
            
            # Performance score (latency-based)
            latency_score = max(0, 1 - (provider.avg_latency_ms / 30000))  # 30s max
            
            # Cost score (lower is better)
            estimated_cost = self._calculate_cost(provider, request)
            cost_score = max(0, 1 - (estimated_cost / 1.0))  # $1 max
            
            # Quality score
            quality_score = provider.quality_score
            
            # Availability score
            availability_score = provider.availability
            
            # Load balancing score (prefer less loaded providers)
            provider_key = f"{provider.name}_{provider.service_type.value}"
            current_load = self.provider_loads.get(provider_key, 0)
            load_score = max(0, 1 - (current_load / 100))  # 100 max load
            
            # Strategy-based weighting
            if request.strategy == RoutingStrategy.COST_OPTIMIZED:
                score = cost_score * 0.6 + quality_score * 0.2 + availability_score * 0.1 + load_score * 0.1
            elif request.strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
                score = quality_score * 0.5 + availability_score * 0.3 + latency_score * 0.2
            elif request.strategy == RoutingStrategy.LATENCY_OPTIMIZED:
                score = latency_score * 0.6 + availability_score * 0.3 + load_score * 0.1
            elif request.strategy == RoutingStrategy.QUALITY_OPTIMIZED:
                score = quality_score * 0.7 + availability_score * 0.2 + latency_score * 0.1
            elif request.strategy == RoutingStrategy.LOAD_BALANCED:
                score = load_score * 0.4 + availability_score * 0.3 + quality_score * 0.3
            else:  # BALANCED
                score = (latency_score + cost_score + quality_score + availability_score + load_score) / 5
            
            scored_providers.append((provider, score))
        
        # Sort by score (descending)
        scored_providers.sort(key=lambda x: x[1], reverse=True)
        
        return scored_providers
    
    def _select_provider(self, scored_providers: List[Tuple[AIProvider, float]], strategy: RoutingStrategy) -> AIProvider:
        """Select provider based on strategy."""
        if strategy == RoutingStrategy.FAILOVER:
            # Select first available healthy provider
            for provider, score in scored_providers:
                provider_key = f"{provider.name}_{provider.service_type.value}"
                if self.provider_health.get(provider_key, True):
                    return provider
        
        # For all other strategies, return the highest scored provider
        return scored_providers[0][0]
    
    def _calculate_cost(self, provider: AIProvider, request: RouteRequest) -> float:
        """Calculate estimated cost for request."""
        # Simple token estimation (replace with actual tokenizer)
        estimated_tokens = len(request.prompt.split()) * 1.3  # Rough estimate
        
        cost = provider.cost_per_request + (estimated_tokens * provider.cost_per_token)
        return round(cost, 6)
    
    def _estimate_latency(self, provider: AIProvider, request: RouteRequest) -> float:
        """Estimate latency for request."""
        base_latency = provider.avg_latency_ms
        
        # Adjust based on prompt length
        prompt_factor = len(request.prompt) / 1000  # Per 1000 chars
        adjusted_latency = base_latency * (1 + prompt_factor * 0.1)
        
        return round(adjusted_latency, 2)
    
    async def _health_check_loop(self):
        """Continuous health check for providers."""
        while True:
            try:
                await self._check_provider_health()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_provider_health(self):
        """Check health of all providers."""
        for provider_name, services in self.providers.items():
            for service_type, providers in services.items():
                for provider in providers:
                    provider_key = f"{provider.name}_{provider.service_type.value}"
                    
                    try:
                        # Simple health check (replace with actual API call)
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                provider.endpoint_url.replace("/chat/completions", "/models"),
                                timeout=aiohttp.ClientTimeout(total=10),
                                headers={"Authorization": f"Bearer {provider.api_key}"} if provider.api_key else {}
                            ) as response:
                                self.provider_health[provider_key] = response.status == 200
                    
                    except Exception:
                        self.provider_health[provider_key] = False
                    
                    self.last_health_check[provider_key] = datetime.utcnow()
    
    async def get_provider_statistics(self) -> Dict[str, Any]:
        """Get comprehensive provider statistics."""
        stats = {
            "total_providers": sum(len(services) for services in self.providers.values() for services in services.values()),
            "healthy_providers": sum(1 for health in self.provider_health.values() if health),
            "provider_details": {},
            "service_types": {},
            "load_distribution": dict(self.provider_loads),
            "cost_savings": 0.0,
            "performance_metrics": {}
        }
        
        # Provider details
        for provider_name, services in self.providers.items():
            for service_type, providers in services.items():
                for provider in providers:
                    provider_key = f"{provider.name}_{provider.service_type.value}"
                    stats["provider_details"][provider_key] = {
                        "name": provider.name,
                        "service_type": provider.service_type.value,
                        "capability": provider.capability.value,
                        "quality_score": provider.quality_score,
                        "availability": provider.availability,
                        "avg_latency_ms": provider.avg_latency_ms,
                        "cost_per_request": provider.cost_per_request,
                        "healthy": self.provider_health.get(provider_key, True),
                        "current_load": self.provider_loads.get(provider_key, 0)
                    }
        
        # Service type distribution
        for provider_name, services in self.providers.items():
            for service_type in services.keys():
                service_name = service_type.value
                if service_name not in stats["service_types"]:
                    stats["service_types"][service_name] = 0
                stats["service_types"][service_name] += len(services[service_type])
        
        return stats
    
    async def update_provider_performance(self, provider_name: str, service_type: AIServiceType, 
                                        actual_latency: float, actual_cost: float, quality_rating: float):
        """Update provider performance metrics based on actual usage."""
        provider_key = f"{provider_name}_{service_type.value}"
        
        # Update performance history
        self.performance_history[provider_key].append({
            "timestamp": datetime.utcnow(),
            "latency": actual_latency,
            "cost": actual_cost,
            "quality": quality_rating
        })
        
        # Update cost history
        self.cost_history[provider_key].append(actual_cost)
        
        # Update provider metrics
        for providers_dict in self.providers.values():
            if service_type in providers_dict:
                for provider in providers_dict[service_type]:
                    if provider.name == provider_name:
                        # Update with exponential moving average
                        alpha = 0.1  # Learning rate
                        provider.avg_latency_ms = (1 - alpha) * provider.avg_latency_ms + alpha * actual_latency
                        provider.quality_score = (1 - alpha) * provider.quality_score + alpha * quality_rating
                        break
        
        # Update metrics
        self.cost_gauge.labels(
            provider=provider_name,
            service_type=service_type.value
        ).set(actual_cost)
        
        self.quality_gauge.labels(
            provider=provider_name,
            service_type=service_type.value
        ).set(quality_rating)
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.redis_client:
                self.redis_client.close()
                await self.redis_client.wait_closed()
            
            logger.info("AI model router cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup AI model router: {str(e)}")


# Global AI model router instance
ai_router = AIModelRouter()


async def route_ai_request(request: RouteRequest) -> RouteResponse:
    """Route AI request using global router."""
    return await ai_router.route_request(request)


async def get_best_provider(service_type: AIServiceType, strategy: RoutingStrategy = RoutingStrategy.BALANCED) -> Optional[AIProvider]:
    """Get best provider for service type."""
    try:
        request = RouteRequest(
            service_type=service_type,
            prompt="test",
            strategy=strategy
        )
        
        response = await ai_router.route_request(request)
        return response.provider
        
    except Exception as e:
        logger.error(f"Failed to get best provider: {str(e)}")
        return None


# Example usage
async def main():
    """Example usage of AI model router."""
    await ai_router.initialize()
    
    # Text generation request
    text_request = RouteRequest(
        service_type=AIServiceType.TEXT_GENERATION,
        prompt="Generate a creative story about AI and creativity",
        strategy=RoutingStrategy.QUALITY_OPTIMIZED,
        max_cost=0.05
    )
    
    response = await ai_router.route_request(text_request)
    print(f"Selected provider: {response.provider.name}")
    print(f"Estimated cost: ${response.estimated_cost}")
    print(f"Estimated latency: {response.estimated_latency_ms}ms")
    print(f"Confidence score: {response.confidence_score}")
    
    # Get statistics
    stats = await ai_router.get_provider_statistics()
    print(f"Total providers: {stats['total_providers']}")
    print(f"Healthy providers: {stats['healthy_providers']}")


if __name__ == "__main__":
    asyncio.run(main())