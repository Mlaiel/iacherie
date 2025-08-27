"""
AI Platform Adapters - Enterprise AI Service Integration

This module provides comprehensive adapter infrastructure for integrating with
external AI platforms and services including OpenAI, Anthropic, Hugging Face,
and custom AI endpoints.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Features:
- Multi-provider AI model support (OpenAI, Anthropic, Hugging Face)
- Intelligent model selection and load balancing
- Cost optimization and usage tracking
- Response caching and quality validation
- Failover and redundancy management
- Real-time performance monitoring
"""

import asyncio
import logging
from abc import abstractmethod
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import aiohttp
import openai
import anthropic
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_adapter import (
    BasePlatformAdapter, PlatformType, AdapterStatus, AuthenticationType,
    AdapterCredentials, RateLimitConfig, AdapterError, PlatformError
)

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Supported AI service providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "hugging_face"
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    REPLICATE = "replicate"
    GOOGLE_PALM = "google_palm"
    CUSTOM = "custom"

class AIModelType(Enum):
    """AI model categories."""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    CHAT_COMPLETION = "chat_completion"
    EMBEDDINGS = "embeddings"
    IMAGE_GENERATION = "image_generation"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTENT_MODERATION = "content_moderation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"

@dataclass
class AIModelConfig:
    """Configuration for AI model usage."""
    provider: AIProvider
    model_name: str
    model_type: AIModelType
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    cost_per_token: float = 0.0
    quality_score: float = 0.8
    response_time_avg: float = 2.0
    is_available: bool = True

@dataclass
class AIRequest:
    """Standardized AI request structure."""
    prompt: str
    model_type: AIModelType
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIResponse:
    """Standardized AI response structure."""
    content: str
    provider: AIProvider
    model_name: str
    usage_tokens: int
    cost: float
    response_time: float
    quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

class BaseAIAdapter(BasePlatformAdapter):
    """Base class for AI platform adapters."""
    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(
            platform_name="ai_platform",
            platform_type=PlatformType.AI_PLATFORM,
            credentials=credentials,
            rate_limit_config=RateLimitConfig(
                requests_per_minute=60,
                burst_limit=10,
                rate_limit_window=60
            )
        )
        self.config = config
        self.models_config: Dict[str, AIModelConfig] = {}
        self.usage_tracker = {}
        self.cost_tracker = 0.0
        
    @abstractmethod
    async def generate_text(self, request: AIRequest) -> AIResponse:
        """Generate text using AI model."""
        pass
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """Chat completion using conversational AI."""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        pass
    
    async def estimate_cost(self, request: AIRequest) -> float:
        """Estimate cost for AI request."""
        model_config = self.models_config.get(request.model_type.value)
        if not model_config:
            return 0.0
        
        estimated_tokens = len(request.prompt.split()) * 1.3  # Rough estimation
        if request.max_tokens:
            estimated_tokens += request.max_tokens
        
        return estimated_tokens * model_config.cost_per_token
    
    async def track_usage(self, response: AIResponse):
        """Track usage statistics."""
        today = datetime.utcnow().date().isoformat()
        if today not in self.usage_tracker:
            self.usage_tracker[today] = {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0,
                'response_time_avg': 0.0
            }
        
        stats = self.usage_tracker[today]
        stats['requests'] += 1
        stats['tokens'] += response.usage_tokens
        stats['cost'] += response.cost
        stats['response_time_avg'] = (
            (stats['response_time_avg'] * (stats['requests'] - 1) + response.response_time) 
            / stats['requests']
        )

class OpenAIAdapter(BaseAIAdapter):
    """OpenAI API adapter implementation."""
    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(credentials, config)
        self.client = openai.AsyncOpenAI(api_key=credentials.api_key)
        self.models_config = {
            AIModelType.CHAT_COMPLETION.value: AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-4-turbo-preview",
                model_type=AIModelType.CHAT_COMPLETION,
                cost_per_token=0.00003,
                quality_score=0.95
            ),
            AIModelType.TEXT_GENERATION.value: AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                model_type=AIModelType.TEXT_GENERATION,
                cost_per_token=0.000002,
                quality_score=0.85
            ),
            AIModelType.EMBEDDINGS.value: AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name="text-embedding-ada-002",
                model_type=AIModelType.EMBEDDINGS,
                cost_per_token=0.0000001,
                quality_score=0.90
            )
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_text(self, request: AIRequest) -> AIResponse:
        """Generate text using OpenAI models."""
        start_time = datetime.utcnow()
        
        try:
            model_config = self.models_config[request.model_type.value]
            
            response = await self.client.completions.create(
                model=model_config.model_name,
                prompt=request.prompt,
                max_tokens=request.max_tokens or model_config.max_tokens,
                temperature=request.temperature or model_config.temperature,
                top_p=model_config.top_p,
                frequency_penalty=model_config.frequency_penalty,
                presence_penalty=model_config.presence_penalty
            )
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            ai_response = AIResponse(
                content=response.choices[0].text.strip(),
                provider=AIProvider.OPENAI,
                model_name=model_config.model_name,
                usage_tokens=response.usage.total_tokens,
                cost=response.usage.total_tokens * model_config.cost_per_token,
                response_time=response_time,
                quality_score=model_config.quality_score,
                metadata={
                    'finish_reason': response.choices[0].finish_reason,
                    'request_id': getattr(response, 'id', None)
                }
            )
            
            await self.track_usage(ai_response)
            return ai_response
            
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {str(e)}")
            raise PlatformError(f"OpenAI API error: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """Chat completion using OpenAI models."""
        start_time = datetime.utcnow()
        
        try:
            model_config = self.models_config[AIModelType.CHAT_COMPLETION.value]
            
            response = await self.client.chat.completions.create(
                model=model_config.model_name,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', model_config.max_tokens),
                temperature=kwargs.get('temperature', model_config.temperature),
                top_p=kwargs.get('top_p', model_config.top_p),
                frequency_penalty=kwargs.get('frequency_penalty', model_config.frequency_penalty),
                presence_penalty=kwargs.get('presence_penalty', model_config.presence_penalty)
            )
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            ai_response = AIResponse(
                content=response.choices[0].message.content,
                provider=AIProvider.OPENAI,
                model_name=model_config.model_name,
                usage_tokens=response.usage.total_tokens,
                cost=response.usage.total_tokens * model_config.cost_per_token,
                response_time=response_time,
                quality_score=model_config.quality_score,
                metadata={
                    'finish_reason': response.choices[0].finish_reason,
                    'request_id': response.id
                }
            )
            
            await self.track_usage(ai_response)
            return ai_response
            
        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {str(e)}")
            raise PlatformError(f"OpenAI API error: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI models."""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            
            return [embedding.embedding for embedding in response.data]
            
        except Exception as e:
            logger.error(f"OpenAI embeddings generation failed: {str(e)}")
            raise PlatformError(f"OpenAI API error: {str(e)}")

class AnthropicAdapter(BaseAIAdapter):
    """Anthropic Claude API adapter implementation."""
    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(credentials, config)
        self.client = anthropic.AsyncAnthropic(api_key=credentials.api_key)
        self.models_config = {
            AIModelType.CHAT_COMPLETION.value: AIModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-opus-20240229",
                model_type=AIModelType.CHAT_COMPLETION,
                cost_per_token=0.000015,
                quality_score=0.92
            ),
            AIModelType.TEXT_GENERATION.value: AIModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                model_type=AIModelType.TEXT_GENERATION,
                cost_per_token=0.000003,
                quality_score=0.88
            )
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_text(self, request: AIRequest) -> AIResponse:
        """Generate text using Anthropic models."""
        start_time = datetime.utcnow()
        
        try:
            model_config = self.models_config[request.model_type.value]
            
            response = await self.client.messages.create(
                model=model_config.model_name,
                max_tokens=request.max_tokens or model_config.max_tokens,
                temperature=request.temperature or model_config.temperature,
                messages=[
                    {"role": "user", "content": request.prompt}
                ]
            )
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            ai_response = AIResponse(
                content=response.content[0].text,
                provider=AIProvider.ANTHROPIC,
                model_name=model_config.model_name,
                usage_tokens=response.usage.input_tokens + response.usage.output_tokens,
                cost=(response.usage.input_tokens + response.usage.output_tokens) * model_config.cost_per_token,
                response_time=response_time,
                quality_score=model_config.quality_score,
                metadata={
                    'stop_reason': response.stop_reason,
                    'request_id': response.id
                }
            )
            
            await self.track_usage(ai_response)
            return ai_response
            
        except Exception as e:
            logger.error(f"Anthropic text generation failed: {str(e)}")
            raise PlatformError(f"Anthropic API error: {str(e)}")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """Chat completion using Anthropic models."""
        # Convert messages to Anthropic format
        anthropic_messages = []
        for msg in messages:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        start_time = datetime.utcnow()
        
        try:
            model_config = self.models_config[AIModelType.CHAT_COMPLETION.value]
            
            response = await self.client.messages.create(
                model=model_config.model_name,
                max_tokens=kwargs.get('max_tokens', model_config.max_tokens),
                temperature=kwargs.get('temperature', model_config.temperature),
                messages=anthropic_messages
            )
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            ai_response = AIResponse(
                content=response.content[0].text,
                provider=AIProvider.ANTHROPIC,
                model_name=model_config.model_name,
                usage_tokens=response.usage.input_tokens + response.usage.output_tokens,
                cost=(response.usage.input_tokens + response.usage.output_tokens) * model_config.cost_per_token,
                response_time=response_time,
                quality_score=model_config.quality_score,
                metadata={
                    'stop_reason': response.stop_reason,
                    'request_id': response.id
                }
            )
            
            await self.track_usage(ai_response)
            return ai_response
            
        except Exception as e:
            logger.error(f"Anthropic chat completion failed: {str(e)}")
            raise PlatformError(f"Anthropic API error: {str(e)}")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Anthropic doesn't provide embeddings API - fallback to other providers."""
        raise NotImplementedError("Anthropic doesn't provide embeddings API")

class HuggingFaceAdapter(BaseAIAdapter):
    """Hugging Face API adapter implementation."""
    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(credentials, config)
        self.api_token = credentials.api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.models_config = {
            AIModelType.TEXT_GENERATION.value: AIModelConfig(
                provider=AIProvider.HUGGING_FACE,
                model_name="microsoft/DialoGPT-large",
                model_type=AIModelType.TEXT_GENERATION,
                cost_per_token=0.000001,  # Free tier
                quality_score=0.75
            ),
            AIModelType.EMBEDDINGS.value: AIModelConfig(
                provider=AIProvider.HUGGING_FACE,
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_type=AIModelType.EMBEDDINGS,
                cost_per_token=0.0,  # Free tier
                quality_score=0.80
            ),
            AIModelType.SENTIMENT_ANALYSIS.value: AIModelConfig(
                provider=AIProvider.HUGGING_FACE,
                model_name="cardiffnlp/twitter-roberta-base-sentiment-latest",
                model_type=AIModelType.SENTIMENT_ANALYSIS,
                cost_per_token=0.0,  # Free tier
                quality_score=0.85
            )
        }
    
    async def generate_text(self, request: AIRequest) -> AIResponse:
        """Generate text using Hugging Face models."""
        start_time = datetime.utcnow()
        
        try:
            model_config = self.models_config[request.model_type.value]
            
            headers = {"Authorization": f"Bearer {self.api_token}"}
            payload = {
                "inputs": request.prompt,
                "parameters": {
                    "max_length": request.max_tokens or model_config.max_tokens,
                    "temperature": request.temperature or model_config.temperature,
                    "return_full_text": False
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{model_config.model_name}",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_time = (datetime.utcnow() - start_time).total_seconds()
                        
                        ai_response = AIResponse(
                            content=result[0]["generated_text"],
                            provider=AIProvider.HUGGING_FACE,
                            model_name=model_config.model_name,
                            usage_tokens=len(request.prompt.split()) + len(result[0]["generated_text"].split()),
                            cost=0.0,  # Free tier
                            response_time=response_time,
                            quality_score=model_config.quality_score
                        )
                        
                        await self.track_usage(ai_response)
                        return ai_response
                    else:
                        error_text = await response.text()
                        raise PlatformError(f"Hugging Face API error: {error_text}")
            
        except Exception as e:
            logger.error(f"Hugging Face text generation failed: {str(e)}")
            raise PlatformError(f"Hugging Face API error: {str(e)}")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> AIResponse:
        """Chat completion using Hugging Face models."""
        # Convert messages to a single prompt
        prompt = ""
        for msg in messages:
            prompt += f"{msg['role']}: {msg['content']}\n"
        
        request = AIRequest(
            prompt=prompt,
            model_type=AIModelType.TEXT_GENERATION,
            max_tokens=kwargs.get('max_tokens'),
            temperature=kwargs.get('temperature')
        )
        
        return await self.generate_text(request)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Hugging Face models."""
        try:
            model_config = self.models_config[AIModelType.EMBEDDINGS.value]
            
            headers = {"Authorization": f"Bearer {self.api_token}"}
            
            embeddings = []
            for text in texts:
                payload = {"inputs": text}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/{model_config.model_name}",
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            embeddings.append(result)
                        else:
                            error_text = await response.text()
                            raise PlatformError(f"Hugging Face API error: {error_text}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Hugging Face embeddings generation failed: {str(e)}")
            raise PlatformError(f"Hugging Face API error: {str(e)}")

class AIAdapterFactory:
    """Factory for creating AI platform adapters."""
    
    _adapters = {
        AIProvider.OPENAI: OpenAIAdapter,
        AIProvider.ANTHROPIC: AnthropicAdapter,
        AIProvider.HUGGING_FACE: HuggingFaceAdapter
    }
    
    @classmethod
    def create_adapter(
        cls, 
        provider: AIProvider, 
        credentials: AdapterCredentials, 
        config: Dict[str, Any]
    ) -> BaseAIAdapter:
        """Create an AI adapter instance."""
        adapter_class = cls._adapters.get(provider)
        if not adapter_class:
            raise ValueError(f"Unsupported AI provider: {provider}")
        
        return adapter_class(credentials, config)
    
    @classmethod
    def get_supported_providers(cls) -> List[AIProvider]:
        """Get list of supported AI providers."""
        return list(cls._adapters.keys())

class AIAdapterManager:
    """Manager for AI adapter instances and intelligent routing."""
    
    def __init__(self):
        self.adapters: Dict[AIProvider, BaseAIAdapter] = {}
        self.default_provider = AIProvider.OPENAI
        self.fallback_providers = [AIProvider.ANTHROPIC, AIProvider.HUGGING_FACE]
    
    def register_adapter(self, provider: AIProvider, adapter: BaseAIAdapter):
        """Register an AI adapter."""
        self.adapters[provider] = adapter
        logger.info(f"Registered AI adapter for provider: {provider.value}")
    
    async def select_best_provider(self, request: AIRequest) -> AIProvider:
        """Select the best provider based on request requirements and current load."""
        # Check if specific provider is requested
        if hasattr(request, 'preferred_provider') and request.preferred_provider in self.adapters:
            return request.preferred_provider
        
        # Check availability and performance metrics
        available_providers = []
        for provider, adapter in self.adapters.items():
            if adapter.status == AdapterStatus.ACTIVE:
                model_config = adapter.models_config.get(request.model_type.value)
                if model_config and model_config.is_available:
                    available_providers.append((provider, model_config.quality_score, model_config.cost_per_token))
        
        if not available_providers:
            raise PlatformError("No available AI providers for request")
        
        # Sort by quality score (descending) and cost (ascending)
        available_providers.sort(key=lambda x: (x[1], -x[2]), reverse=True)
        
        return available_providers[0][0]
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process AI request with intelligent provider selection and fallback."""
        provider = await self.select_best_provider(request)
        
        try:
            adapter = self.adapters[provider]
            if request.model_type == AIModelType.CHAT_COMPLETION:
                # Convert request to messages format if needed
                messages = [{"role": "user", "content": request.prompt}]
                return await adapter.chat_completion(messages, max_tokens=request.max_tokens, temperature=request.temperature)
            else:
                return await adapter.generate_text(request)
                
        except Exception as e:
            logger.warning(f"Primary provider {provider.value} failed: {str(e)}")
            
            # Try fallback providers
            for fallback_provider in self.fallback_providers:
                if fallback_provider in self.adapters and fallback_provider != provider:
                    try:
                        adapter = self.adapters[fallback_provider]
                        if request.model_type == AIModelType.CHAT_COMPLETION:
                            messages = [{"role": "user", "content": request.prompt}]
                            return await adapter.chat_completion(messages, max_tokens=request.max_tokens, temperature=request.temperature)
                        else:
                            return await adapter.generate_text(request)
                    except Exception as fallback_error:
                        logger.warning(f"Fallback provider {fallback_provider.value} failed: {str(fallback_error)}")
                        continue
            
            # If all providers failed
            raise PlatformError(f"All AI providers failed for request: {str(e)}")
    
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics across all providers."""
        stats = {}
        for provider, adapter in self.adapters.items():
            stats[provider.value] = {
                'usage_tracker': adapter.usage_tracker,
                'cost_tracker': adapter.cost_tracker,
                'status': adapter.status.value,
                'models': list(adapter.models_config.keys())
            }
        return stats

# Export all classes and functions
__all__ = [
    'AIProvider', 'AIModelType', 'AIModelConfig', 'AIRequest', 'AIResponse',
    'BaseAIAdapter', 'OpenAIAdapter', 'AnthropicAdapter', 'HuggingFaceAdapter',
    'AIAdapterFactory', 'AIAdapterManager'
]
