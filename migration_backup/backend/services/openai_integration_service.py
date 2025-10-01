"""
OpenAI Integration Service for IA Chéries Platform
Provides secure and optimized access to OpenAI APIs
"""
import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import aiohttp
import openai
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from fastapi import HTTPException
from backend.config.openai_config import settings
from backend.security.auth_manager import get_api_key_hash
from backend.monitoring.openai_metrics import MetricsCollector

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIConfig(BaseModel):
    """OpenAI API Configuration"""
    api_key: str = Field(..., description="OpenAI API Key")
    model: str = Field(default="gpt-4o-mini", description="Default model to use")
    max_tokens: int = Field(default=2000, description="Maximum tokens per request")
    temperature: float = Field(default=0.7, description="Creativity temperature")
    base_url: str = Field(default="https://api.openai.com/v1", description="API base URL")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

class ChatMessage(BaseModel):
    """Chat message structure"""
    role: str = Field(..., description="Message role: system, user, assistant")
    content: str = Field(..., description="Message content")
    
class CompletionRequest(BaseModel):
    """Chat completion request"""
    messages: List[ChatMessage]
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = Field(default=False)
    
class ImageGenerationRequest(BaseModel):
    """Image generation request"""
    prompt: str = Field(..., description="Image description prompt")
    model: str = Field(default="dall-e-3", description="Image model to use")
    size: str = Field(default="1024x1024", description="Image size")
    quality: str = Field(default="standard", description="Image quality")
    n: int = Field(default=1, description="Number of images")

class AudioTranscriptionRequest(BaseModel):
    """Audio transcription request"""
    file_path: str = Field(..., description="Path to audio file")
    model: str = Field(default="whisper-1", description="Transcription model")
    language: Optional[str] = None
    response_format: str = Field(default="json", description="Response format")

class OpenAIService:
    """
    Enterprise-grade OpenAI API integration service
    Handles authentication, rate limiting, caching, and monitoring
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        self.metrics = MetricsCollector()
        self._usage_cache = {}
        
    def _load_config(self) -> OpenAIConfig:
        """Load OpenAI configuration from environment"""
        return OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI API health and connectivity"""
        try:
            models = await self.client.models.list()
            return {
                "status": "healthy",
                "api_accessible": True,
                "models_available": len(models.data),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def chat_completion(self, request: CompletionRequest) -> Dict[str, Any]:
        """
        Generate chat completion using OpenAI
        Enhanced with retry logic and usage tracking
        """
        try:
            start_time = datetime.now()
            
            # Prepare request parameters
            params = {
                "model": request.model or self.config.model,
                "messages": [msg.dict() for msg in request.messages],
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "stream": request.stream
            }
            
            # Make API call
            response = await self.client.chat.completions.create(**params)
            
            # Track metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "duration_seconds": duration
            }
            
            await self._track_usage("chat_completion", usage)
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": usage,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            await self.metrics.increment_counter("openai_errors", {"type": "chat_completion"})
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    
    async def generate_image(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        """Generate images using DALL-E"""
        try:
            start_time = datetime.now()
            
            response = await self.client.images.generate(
                model=request.model,
                prompt=request.prompt,
                size=request.size,
                quality=request.quality,
                n=request.n
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            images = [
                {
                    "url": img.url,
                    "revised_prompt": getattr(img, 'revised_prompt', None)
                }
                for img in response.data
            ]
            
            await self._track_usage("image_generation", {
                "model": request.model,
                "images_generated": len(images),
                "duration_seconds": duration
            })
            
            return {
                "success": True,
                "images": images,
                "model": request.model,
                "prompt": request.prompt
            }
            
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            await self.metrics.increment_counter("openai_errors", {"type": "image_generation"})
            raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")
    
    async def transcribe_audio(self, request: AudioTranscriptionRequest) -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        try:
            start_time = datetime.now()
            
            with open(request.file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model=request.model,
                    file=audio_file,
                    language=request.language,
                    response_format=request.response_format
                )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            await self._track_usage("audio_transcription", {
                "model": request.model,
                "file_size": os.path.getsize(request.file_path),
                "duration_seconds": duration
            })
            
            return {
                "success": True,
                "text": transcript.text,
                "model": request.model,
                "language": getattr(transcript, 'language', request.language)
            }
            
        except Exception as e:
            logger.error(f"Audio transcription error: {e}")
            await self.metrics.increment_counter("openai_errors", {"type": "transcription"})
            raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    
    async def get_embeddings(self, texts: List[str], model: str = "text-embedding-3-small") -> Dict[str, Any]:
        """Generate embeddings for text analysis"""
        try:
            start_time = datetime.now()
            
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            embeddings = [data.embedding for data in response.data]
            
            await self._track_usage("embeddings", {
                "model": model,
                "texts_processed": len(texts),
                "total_tokens": response.usage.total_tokens,
                "duration_seconds": duration
            })
            
            return {
                "success": True,
                "embeddings": embeddings,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Embeddings error: {e}")
            await self.metrics.increment_counter("openai_errors", {"type": "embeddings"})
            raise HTTPException(status_code=500, detail=f"Embeddings error: {str(e)}")
    
    async def _track_usage(self, operation: str, usage_data: Dict[str, Any]):
        """Track API usage for monitoring and billing"""
        timestamp = datetime.now().isoformat()
        
        usage_record = {
            "operation": operation,
            "timestamp": timestamp,
            **usage_data
        }
        
        # Store in cache for real-time monitoring
        if operation not in self._usage_cache:
            self._usage_cache[operation] = []
        
        self._usage_cache[operation].append(usage_record)
        
        # Keep only recent records (last 1000 per operation)
        if len(self._usage_cache[operation]) > 1000:
            self._usage_cache[operation] = self._usage_cache[operation][-1000:]
        
        # Send metrics to monitoring system
        await self.metrics.record_histogram(
            "openai_request_duration",
            usage_data.get("duration_seconds", 0),
            {"operation": operation}
        )
        
        if "total_tokens" in usage_data:
            await self.metrics.record_histogram(
                "openai_tokens_used",
                usage_data["total_tokens"],
                {"operation": operation}
            )
    
    async def get_usage_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get API usage statistics"""
        if operation and operation in self._usage_cache:
            records = self._usage_cache[operation]
        else:
            records = []
            for op_records in self._usage_cache.values():
                records.extend(op_records)
        
        if not records:
            return {"total_requests": 0, "operations": {}}
        
        # Calculate statistics
        total_requests = len(records)
        total_tokens = sum(r.get("total_tokens", 0) for r in records)
        avg_duration = sum(r.get("duration_seconds", 0) for r in records) / total_requests
        
        operations = {}
        for record in records:
            op = record["operation"]
            if op not in operations:
                operations[op] = {"count": 0, "tokens": 0, "duration": 0}
            
            operations[op]["count"] += 1
            operations[op]["tokens"] += record.get("total_tokens", 0)
            operations[op]["duration"] += record.get("duration_seconds", 0)
        
        # Calculate averages per operation
        for op_stats in operations.values():
            if op_stats["count"] > 0:
                op_stats["avg_duration"] = op_stats["duration"] / op_stats["count"]
                op_stats["avg_tokens"] = op_stats["tokens"] / op_stats["count"]
        
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "avg_duration_seconds": avg_duration,
            "operations": operations,
            "last_updated": datetime.now().isoformat()
        }

# Global service instance
openai_service = OpenAIService()

# Export for use in other modules
__all__ = [
    "OpenAIService",
    "openai_service",
    "CompletionRequest",
    "ChatMessage",
    "ImageGenerationRequest",
    "AudioTranscriptionRequest"
]