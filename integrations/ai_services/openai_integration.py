"""OpenAI API Integration
=======================

Comprehensive integration with OpenAI's API including GPT models, DALL-E, and Whisper.
Supports text generation, image creation, audio transcription, and embeddings.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import aiohttp
import base64
from datetime import datetime


class OpenAIModel(Enum):
    """OpenAI model enumeration"""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_VISION = "gpt-4-vision-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"
    WHISPER_1 = "whisper-1"
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"


@dataclass
class OpenAIConfig:
    """OpenAI configuration"""
    api_key: str
    organization_id: Optional[str] = None
    base_url: str = "https://api.openai.com/v1"
    timeout: int = 60
    max_retries: int = 3


@dataclass
class ChatMessage:
    """Chat message structure"""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


@dataclass
class ImageGenerationRequest:
    """Image generation request"""
    prompt: str
    model: OpenAIModel = OpenAIModel.DALL_E_3
    size: str = "1024x1024"
    quality: str = "standard"
    style: str = "vivid"
    n: int = 1


@dataclass
class AudioTranscriptionRequest:
    """Audio transcription request"""
    file_path: str
    model: OpenAIModel = OpenAIModel.WHISPER_1
    language: Optional[str] = None
    prompt: Optional[str] = None
    response_format: str = "json"
    temperature: float = 0


class OpenAIIntegration:
    """OpenAI API integration"""
    
    def __init__(self, config: OpenAIConfig, rate_limiter=None, cache_manager=None):
        """Initialize OpenAI integration
        
        Args:
            config: OpenAI configuration
            rate_limiter: Rate limiter instance
            cache_manager: Cache manager instance
        """
        self.config = config
        self.rate_limiter = rate_limiter
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        
        # Session for HTTP requests
        self.session = None
        
        # Usage tracking
        self.usage_stats = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "requests_count": 0,
            "images_generated": 0,
            "audio_transcribed": 0
        }
    
    async def initialize(self):
        """Initialize the integration"""
        try:
            # Create HTTP session
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Ainflue-OpenAI-Integration/1.0"
            }
            
            if self.config.organization_id:
                headers["OpenAI-Organization"] = self.config.organization_id
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
            
            # Test connection
            await self._test_connection()
            
            self.logger.info("OpenAI integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI integration: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the integration"""
        if self.session:
            await self.session.close()
        self.logger.info("OpenAI integration shutdown complete")
    
    async def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            async with self.session.get(f"{self.config.base_url}/models") as response:
                if response.status == 200:
                    self.logger.info("OpenAI API connection test successful")
                else:
                    raise Exception(f"API test failed with status: {response.status}")
        except Exception as e:
            self.logger.error(f"OpenAI API connection test failed: {e}")
            raise
    
    async def chat_completion(self, messages: List[ChatMessage], 
                            model: OpenAIModel = OpenAIModel.GPT_4_TURBO,
                            temperature: float = 0.7,
                            max_tokens: Optional[int] = None,
                            stream: bool = False,
                            **kwargs) -> Union[Dict[str, Any], AsyncGenerator]:
        """Create chat completion
        
        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            **kwargs: Additional parameters
            
        Returns:
            Union[Dict[str, Any], AsyncGenerator]: Response or stream
        """
        try:
            # Check rate limits
            if self.rate_limiter:
                allowed = await self.rate_limiter.allow_request("openai", rule_name="gpt4_requests")
                if not allowed:
                    raise Exception("Rate limit exceeded")
            
            # Prepare request
            request_data = {
                "model": model.value,
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                request_data["max_tokens"] = max_tokens
            
            # Add additional parameters
            request_data.update(kwargs)
            
            # Check cache for non-streaming requests
            cache_key = None
            if not stream and self.cache_manager:
                cache_key = f"openai:chat:{hash(json.dumps(request_data, sort_keys=True))}"
                cached_response = await self.cache_manager.get(cache_key)
                if cached_response:
                    return cached_response
            
            # Make request
            url = f"{self.config.base_url}/chat/completions"
            
            if stream:
                return self._stream_chat_completion(url, request_data)
            else:
                async with self.session.post(url, json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Update usage stats
                        if "usage" in result:
                            usage = result["usage"]
                            self.usage_stats["total_tokens"] += usage.get("total_tokens", 0)
                            self.usage_stats["prompt_tokens"] += usage.get("prompt_tokens", 0)
                            self.usage_stats["completion_tokens"] += usage.get("completion_tokens", 0)
                        
                        self.usage_stats["requests_count"] += 1
                        
                        # Cache response
                        if cache_key and self.cache_manager:
                            await self.cache_manager.set(cache_key, result, ttl=300)
                        
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"Chat completion error: {e}")
            raise
    
    async def _stream_chat_completion(self, url: str, request_data: Dict[str, Any]) -> AsyncGenerator:
        """Stream chat completion response
        
        Args:
            url: API URL
            request_data: Request data
            
        Yields:
            Dict[str, Any]: Streaming response chunks
        """
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            self.logger.error(f"Streaming chat completion error: {e}")
            raise
    
    async def generate_image(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        """Generate image using DALL-E
        
        Args:
            request: Image generation request
            
        Returns:
            Dict[str, Any]: Generated image data
        """
        try:
            # Check rate limits
            if self.rate_limiter:
                allowed = await self.rate_limiter.allow_request("openai", rule_name="dalle_requests")
                if not allowed:
                    raise Exception("Rate limit exceeded")
            
            # Prepare request
            request_data = {
                "model": request.model.value,
                "prompt": request.prompt,
                "size": request.size,
                "quality": request.quality,
                "n": request.n
            }
            
            if request.model == OpenAIModel.DALL_E_3:
                request_data["style"] = request.style
            
            # Check cache
            cache_key = None
            if self.cache_manager:
                cache_key = f"openai:image:{hash(json.dumps(request_data, sort_keys=True))}"
                cached_response = await self.cache_manager.get(cache_key)
                if cached_response:
                    return cached_response
            
            # Make request
            url = f"{self.config.base_url}/images/generations"
            
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Update usage stats
                    self.usage_stats["images_generated"] += request.n
                    self.usage_stats["requests_count"] += 1
                    
                    # Cache response
                    if cache_key and self.cache_manager:
                        await self.cache_manager.set(cache_key, result, ttl=3600)
                    
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Image generation error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Image generation error: {e}")
            raise
    
    async def transcribe_audio(self, request: AudioTranscriptionRequest) -> Dict[str, Any]:
        """Transcribe audio using Whisper
        
        Args:
            request: Audio transcription request
            
        Returns:
            Dict[str, Any]: Transcription result
        """
        try:
            # Check rate limits
            if self.rate_limiter:
                allowed = await self.rate_limiter.allow_request("openai", rule_name="whisper_requests")
                if not allowed:
                    raise Exception("Rate limit exceeded")
            
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('model', request.model.value)
            data.add_field('response_format', request.response_format)
            data.add_field('temperature', str(request.temperature))
            
            if request.language:
                data.add_field('language', request.language)
            
            if request.prompt:
                data.add_field('prompt', request.prompt)
            
            # Add file
            with open(request.file_path, 'rb') as f:
                data.add_field('file', f, filename=request.file_path.split('/')[-1])
                
                # Make request
                url = f"{self.config.base_url}/audio/transcriptions"
                
                # Temporarily remove Content-Type header for form data
                headers = self.session.headers.copy()
                if 'Content-Type' in headers:
                    del headers['Content-Type']
                
                async with self.session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Update usage stats
                        self.usage_stats["audio_transcribed"] += 1
                        self.usage_stats["requests_count"] += 1
                        
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(f"Audio transcription error: {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"Audio transcription error: {e}")
            raise
    
    async def create_embeddings(self, texts: Union[str, List[str]], 
                              model: OpenAIModel = OpenAIModel.TEXT_EMBEDDING_3_LARGE) -> Dict[str, Any]:
        """Create text embeddings
        
        Args:
            texts: Text or list of texts to embed
            model: Embedding model to use
            
        Returns:
            Dict[str, Any]: Embeddings data
        """
        try:
            # Check rate limits
            if self.rate_limiter:
                allowed = await self.rate_limiter.allow_request("openai", rule_name="embeddings_requests")
                if not allowed:
                    raise Exception("Rate limit exceeded")
            
            # Prepare request
            if isinstance(texts, str):
                texts = [texts]
            
            request_data = {
                "model": model.value,
                "input": texts
            }
            
            # Check cache
            cache_key = None
            if self.cache_manager:
                cache_key = f"openai:embeddings:{hash(json.dumps(request_data, sort_keys=True))}"
                cached_response = await self.cache_manager.get(cache_key)
                if cached_response:
                    return cached_response
            
            # Make request
            url = f"{self.config.base_url}/embeddings"
            
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Update usage stats
                    if "usage" in result:
                        usage = result["usage"]
                        self.usage_stats["total_tokens"] += usage.get("total_tokens", 0)
                    
                    self.usage_stats["requests_count"] += 1
                    
                    # Cache response
                    if cache_key and self.cache_manager:
                        await self.cache_manager.set(cache_key, result, ttl=3600)
                    
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Embeddings error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Embeddings error: {e}")
            raise
    
    async def text_to_speech(self, text: str, voice: str = "alloy", 
                           model: OpenAIModel = OpenAIModel.TTS_1,
                           response_format: str = "mp3",
                           speed: float = 1.0) -> bytes:
        """Convert text to speech
        
        Args:
            text: Text to convert
            voice: Voice to use
            model: TTS model
            response_format: Output format
            speed: Speech speed
            
        Returns:
            bytes: Audio data
        """
        try:
            # Check rate limits
            if self.rate_limiter:
                allowed = await self.rate_limiter.allow_request("openai", rule_name="tts_requests")
                if not allowed:
                    raise Exception("Rate limit exceeded")
            
            # Prepare request
            request_data = {
                "model": model.value,
                "input": text,
                "voice": voice,
                "response_format": response_format,
                "speed": speed
            }
            
            # Make request
            url = f"{self.config.base_url}/audio/speech"
            
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Update usage stats
                    self.usage_stats["requests_count"] += 1
                    
                    return audio_data
                else:
                    error_text = await response.text()
                    raise Exception(f"TTS error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            raise
    
    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content using OpenAI moderation
        
        Args:
            content: Content to moderate
            
        Returns:
            Dict[str, Any]: Moderation result
        """
        try:
            # Prepare request
            request_data = {
                "input": content
            }
            
            # Make request
            url = f"{self.config.base_url}/moderations"
            
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Update usage stats
                    self.usage_stats["requests_count"] += 1
                    
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Moderation error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Moderation error: {e}")
            raise
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models
        
        Returns:
            Dict[str, Any]: Available models
        """
        try:
            url = f"{self.config.base_url}/models"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"List models error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"List models error: {e}")
            raise
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics
        
        Returns:
            Dict[str, Any]: Usage statistics
        """
        stats = self.usage_stats.copy()
        stats["timestamp"] = datetime.utcnow().isoformat()
        return stats
    
    async def estimate_cost(self, model: OpenAIModel, tokens: int = 0, 
                          images: int = 0, audio_minutes: float = 0) -> Dict[str, float]:
        """Estimate cost for usage
        
        Args:
            model: Model used
            tokens: Number of tokens
            images: Number of images
            audio_minutes: Minutes of audio
            
        Returns:
            Dict[str, float]: Cost estimates
        """
        # Cost per 1K tokens (approximate, as of 2024)
        pricing = {
            OpenAIModel.GPT_4: {"input": 0.03, "output": 0.06},
            OpenAIModel.GPT_4_TURBO: {"input": 0.01, "output": 0.03},
            OpenAIModel.GPT_3_5_TURBO: {"input": 0.0015, "output": 0.002},
            OpenAIModel.DALL_E_3: {"per_image": 0.04},
            OpenAIModel.DALL_E_2: {"per_image": 0.02},
            OpenAIModel.WHISPER_1: {"per_minute": 0.006},
            OpenAIModel.TTS_1: {"per_1k_chars": 0.015},
            OpenAIModel.TEXT_EMBEDDING_3_LARGE: {"input": 0.00013},
        }
        
        cost_estimate = {
            "total_cost": 0.0,
            "breakdown": {}
        }
        
        if model in pricing:
            prices = pricing[model]
            
            if tokens > 0 and "input" in prices:
                token_cost = (tokens / 1000) * prices["input"]
                cost_estimate["breakdown"]["tokens"] = token_cost
                cost_estimate["total_cost"] += token_cost
            
            if images > 0 and "per_image" in prices:
                image_cost = images * prices["per_image"]
                cost_estimate["breakdown"]["images"] = image_cost
                cost_estimate["total_cost"] += image_cost
            
            if audio_minutes > 0 and "per_minute" in prices:
                audio_cost = audio_minutes * prices["per_minute"]
                cost_estimate["breakdown"]["audio"] = audio_cost
                cost_estimate["total_cost"] += audio_cost
        
        return cost_estimate


# Integration factory function
def create_openai_integration(api_key: str, organization_id: Optional[str] = None,
                            rate_limiter=None, cache_manager=None) -> OpenAIIntegration:
    """Create OpenAI integration instance
    
    Args:
        api_key: OpenAI API key
        organization_id: Optional organization ID
        rate_limiter: Rate limiter instance
        cache_manager: Cache manager instance
        
    Returns:
        OpenAIIntegration: Integration instance
    """
    config = OpenAIConfig(
        api_key=api_key,
        organization_id=organization_id
    )
    
    return OpenAIIntegration(config, rate_limiter, cache_manager)