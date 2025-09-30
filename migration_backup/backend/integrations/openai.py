"""OpenAI Integration - Advanced AI Content Generation
======================================================

Professional OpenAI API integration for content generation, 
text processing, and AI-powered features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp

logger = logging.getLogger(__name__)


class OpenAIModel(str, Enum):
    """OpenAI model types."""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"
    WHISPER_1 = "whisper-1"
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"


class OpenAIRole(str, Enum):
    """Chat completion roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


@dataclass
class OpenAIMessage:
    """OpenAI chat message."""
    role: OpenAIRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None


@dataclass
class OpenAICompletion:
    """OpenAI completion response."""
    id: str
    model: str
    content: str
    finish_reason: str
    usage: Dict[str, int]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class OpenAIImageGeneration:
    """OpenAI image generation response."""
    id: str
    url: str
    revised_prompt: Optional[str]
    created_at: datetime
    metadata: Dict[str, Any]


class OpenAIIntegration:
    """Professional OpenAI API integration."""
    
    def __init__(
        self,
        api_key: str,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60
    ):
        self.api_key = api_key
        self.organization_id = organization_id
        self.project_id = project_id
        self.base_url = base_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Request tracking
        self.total_requests = 0
        self.total_tokens = 0
        self.request_history: List[Dict[str, Any]] = []
        
        logger.info("OpenAI integration initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Ainflue/1.0"
            }
            
            if self.organization_id:
                headers["OpenAI-Organization"] = self.organization_id
            
            if self.project_id:
                headers["OpenAI-Project"] = self.project_id
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def chat_completion(
        self,
        messages: List[OpenAIMessage],
        model: OpenAIModel = OpenAIModel.GPT_4_TURBO,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        functions: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Union[OpenAICompletion, AsyncGenerator[str, None]]:
        """Generate chat completion."""
        await self._ensure_session()
        
        # Prepare request data
        data = {
            "model": model.value,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    **({"name": msg.name} if msg.name else {}),
                    **({"function_call": msg.function_call} if msg.function_call else {})
                }
                for msg in messages
            ],
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        if functions:
            data["functions"] = functions
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"OpenAI API error: {error_data}")
                
                if stream:
                    return self._handle_stream_response(response)
                else:
                    result = await response.json()
                    return self._parse_completion_response(result, metadata)
        
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        model: OpenAIModel = OpenAIModel.DALL_E_3,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        response_format: str = "url",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[OpenAIImageGeneration]:
        """Generate images using DALL-E."""
        await self._ensure_session()
        
        data = {
            "model": model.value,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n,
            "response_format": response_format
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/images/generations",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"OpenAI Image API error: {error_data}")
                
                result = await response.json()
                return self._parse_image_response(result, metadata)
        
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
    
    async def transcribe_audio(
        self,
        audio_file: bytes,
        filename: str = "audio.mp3",
        model: OpenAIModel = OpenAIModel.WHISPER_1,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transcribe audio using Whisper."""
        await self._ensure_session()
        
        # Prepare form data
        form_data = aiohttp.FormData()
        form_data.add_field('file', audio_file, filename=filename)
        form_data.add_field('model', model.value)
        form_data.add_field('response_format', response_format)
        form_data.add_field('temperature', str(temperature))
        
        if language:
            form_data.add_field('language', language)
        
        if prompt:
            form_data.add_field('prompt', prompt)
        
        try:
            async with self.session.post(
                f"{self.base_url}/audio/transcriptions",
                data=form_data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"OpenAI Transcription API error: {error_data}")
                
                result = await response.json()
                
                # Track usage
                self.total_requests += 1
                self._add_to_history("transcription", {"filename": filename}, result, metadata)
                
                return result
        
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise
    
    async def text_to_speech(
        self,
        text: str,
        model: OpenAIModel = OpenAIModel.TTS_1,
        voice: str = "alloy",
        response_format: str = "mp3",
        speed: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Convert text to speech."""
        await self._ensure_session()
        
        data = {
            "model": model.value,
            "input": text,
            "voice": voice,
            "response_format": response_format,
            "speed": speed
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/audio/speech",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"OpenAI TTS API error: {error_data}")
                
                audio_data = await response.read()
                
                # Track usage
                self.total_requests += 1
                self._add_to_history("tts", {"voice": voice, "text_length": len(text)}, 
                                   {"audio_size": len(audio_data)}, metadata)
                
                return audio_data
        
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            raise
    
    async def get_embeddings(
        self,
        input_text: Union[str, List[str]],
        model: str = "text-embedding-ada-002",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[List[float]]:
        """Get text embeddings."""
        await self._ensure_session()
        
        data = {
            "model": model,
            "input": input_text
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/embeddings",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"OpenAI Embeddings API error: {error_data}")
                
                result = await response.json()
                
                # Track usage
                self.total_requests += 1
                self.total_tokens += result.get("usage", {}).get("total_tokens", 0)
                
                embeddings = [item["embedding"] for item in result["data"]]
                
                self._add_to_history("embeddings", {"input_length": len(input_text)}, 
                                   {"embedding_count": len(embeddings)}, metadata)
                
                return embeddings
        
        except Exception as e:
            logger.error(f"Embeddings generation failed: {e}")
            raise
    
    async def _handle_stream_response(self, response) -> AsyncGenerator[str, None]:
        """Handle streaming response."""
        async for line in response.content:
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and data['choices']:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                    except json.JSONDecodeError:
                        continue
    
    def _parse_completion_response(
        self,
        response: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> OpenAICompletion:
        """Parse completion response."""
        choice = response["choices"][0]
        usage = response.get("usage", {})
        
        # Track usage
        self.total_requests += 1
        self.total_tokens += usage.get("total_tokens", 0)
        
        completion = OpenAICompletion(
            id=response["id"],
            model=response["model"],
            content=choice["message"]["content"],
            finish_reason=choice["finish_reason"],
            usage=usage,
            created_at=datetime.fromtimestamp(response["created"]),
            metadata=metadata or {}
        )
        
        self._add_to_history("completion", {"model": response["model"]}, completion, metadata)
        
        return completion
    
    def _parse_image_response(
        self,
        response: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[OpenAIImageGeneration]:
        """Parse image generation response."""
        images = []
        
        for i, image_data in enumerate(response["data"]):
            image = OpenAIImageGeneration(
                id=f"{response.get('created', int(datetime.now().timestamp()))}_{i}",
                url=image_data["url"],
                revised_prompt=image_data.get("revised_prompt"),
                created_at=datetime.now(),
                metadata=metadata or {}
            )
            images.append(image)
        
        self.total_requests += 1
        self._add_to_history("image_generation", {"count": len(images)}, images, metadata)
        
        return images
    
    def _add_to_history(
        self,
        operation: str,
        request_data: Dict[str, Any],
        response_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add operation to history."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "request": request_data,
            "response_summary": self._summarize_response(response_data),
            "metadata": metadata or {}
        }
        
        self.request_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.request_history) > 100:
            self.request_history = self.request_history[-100:]
    
    def _summarize_response(self, response_data: Any) -> Dict[str, Any]:
        """Create summary of response data."""
        if isinstance(response_data, OpenAICompletion):
            return {
                "type": "completion",
                "tokens_used": response_data.usage.get("total_tokens", 0),
                "finish_reason": response_data.finish_reason
            }
        elif isinstance(response_data, list) and response_data and isinstance(response_data[0], OpenAIImageGeneration):
            return {
                "type": "image_generation",
                "images_generated": len(response_data)
            }
        elif isinstance(response_data, dict):
            return {
                "type": "generic",
                "keys": list(response_data.keys())
            }
        else:
            return {"type": "unknown"}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "recent_operations": len(self.request_history),
            "operations_by_type": self._get_operations_breakdown()
        }
    
    def _get_operations_breakdown(self) -> Dict[str, int]:
        """Get breakdown of operations by type."""
        breakdown = {}
        for entry in self.request_history:
            operation = entry["operation"]
            breakdown[operation] = breakdown.get(operation, 0) + 1
        return breakdown


# Utility functions
async def create_openai_integration(
    api_key: str,
    organization_id: Optional[str] = None,
    project_id: Optional[str] = None
) -> OpenAIIntegration:
    """Create and initialize OpenAI integration."""
    integration = OpenAIIntegration(
        api_key=api_key,
        organization_id=organization_id,
        project_id=project_id
    )
    await integration._ensure_session()
    return integration


async def generate_content_with_openai(
    prompt: str,
    api_key: str,
    model: OpenAIModel = OpenAIModel.GPT_4_TURBO,
    max_tokens: Optional[int] = None
) -> str:
    """Quick content generation utility."""
    async with OpenAIIntegration(api_key) as openai:
        messages = [OpenAIMessage(role=OpenAIRole.USER, content=prompt)]
        completion = await openai.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens
        )
        return completion.content


if __name__ == "__main__":
    # Example usage
    async def main():
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Please set OPENAI_API_KEY environment variable")
            return
        
        async with OpenAIIntegration(api_key) as openai:
            # Test chat completion
            messages = [
                OpenAIMessage(role=OpenAIRole.USER, content="Hello, how are you?")
            ]
            completion = await openai.chat_completion(messages)
            print(f"Response: {completion.content}")
            
            # Test usage stats
            stats = openai.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())