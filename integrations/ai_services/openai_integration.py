"""OpenAI Integration - Comprehensive OpenAI API Integration
========================================================

Enterprise-grade OpenAI API integration supporting all models, features,
and advanced functionality for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, AsyncGenerator, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import base64
from io import BytesIO

import openai
import httpx
from PIL import Image
import tiktoken


class OpenAIModel(Enum):
    """OpenAI model types."""
    # GPT Models
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_4_32K = "gpt-4-32k"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_3_5_TURBO_16K = "gpt-3.5-turbo-16k"
    
    # DALL-E Models
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"
    
    # Whisper Models
    WHISPER_1 = "whisper-1"
    
    # TTS Models
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"
    
    # Embedding Models
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    
    # Moderation Models
    TEXT_MODERATION_LATEST = "text-moderation-latest"
    TEXT_MODERATION_STABLE = "text-moderation-stable"


class OpenAIImageSize(Enum):
    """DALL-E image sizes."""
    SMALL = "256x256"
    MEDIUM = "512x512"
    LARGE = "1024x1024"
    HD_PORTRAIT = "1024x1792"
    HD_LANDSCAPE = "1792x1024"


class OpenAIImageQuality(Enum):
    """DALL-E image quality."""
    STANDARD = "standard"
    HD = "hd"


class TTSVoice(Enum):
    """Text-to-speech voices."""
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"


class TTSResponseFormat(Enum):
    """TTS response formats."""
    MP3 = "mp3"
    OPUS = "opus"
    AAC = "aac"
    FLAC = "flac"


@dataclass
class OpenAIRequest:
    """OpenAI API request configuration."""
    id: str
    model: OpenAIModel
    prompt: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    max_tokens: Optional[int] = None
    temperature: float = 1.0
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[Union[str, List[str]]] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OpenAIResponse:
    """OpenAI API response."""
    id: str
    request_id: str
    model: str
    content: Any
    usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    error: Optional[str] = None


class OpenAIIntegration:
    """Comprehensive OpenAI API integration."""
    
    def __init__(
        self,
        api_key -> None: str,
        organization_id -> None: Optional[str] = None,
        config -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        self.api_key = api_key
        self.organization_id = organization_id
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            organization=organization_id
        )
        
        # Rate limiting and usage tracking
        self.request_count = 0
        self.token_usage = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
        
        # Model capabilities cache
        self.model_capabilities = {}
        
        # Request history for analysis
        self.request_history: List[OpenAIResponse] = []
        self.max_history = self.config.get('max_history', 1000)
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'model_usage': {},
            'cost_tracking': {
                'total_cost': 0.0,
                'cost_by_model': {}
            }
        }
        
        # Initialize tokenizer for cost calculation
        self.tokenizers = {}
        
    async def initialize(self) -> None:
        """Initialize the OpenAI integration."""
        # Load model capabilities
        await self._load_model_capabilities()
        
        # Initialize tokenizers
        self._setup_tokenizers()
        
        self.logger.info("OpenAI integration initialized")
    
    def _setup_tokenizers(self) -> None:
        """Setup tokenizers for different models."""
        try:
            self.tokenizers = {
                'gpt-4': tiktoken.encoding_for_model("gpt-4"),
                'gpt-3.5-turbo': tiktoken.encoding_for_model("gpt-3.5-turbo"),
                'text-embedding-ada-002': tiktoken.encoding_for_model("text-embedding-ada-002")
            }
        except Exception as e:
            self.logger.warning(f"Failed to setup tokenizers: {e}")
    
    async def _load_model_capabilities(self) -> None:
        """Load available models and their capabilities."""
        try:
            models = await self.client.models.list()
            self.model_capabilities = {
                model.id: {
                    'id': model.id,
                    'object': model.object,
                    'created': model.created,
                    'owned_by': model.owned_by
                }
                for model in models.data
            }
            self.logger.info(f"Loaded {len(self.model_capabilities)} OpenAI models")
        except Exception as e:
            self.logger.error(f"Failed to load model capabilities: {e}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: OpenAIModel = OpenAIModel.GPT_4_TURBO,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> Union[OpenAIResponse, AsyncGenerator[OpenAIResponse, None]]:
        """Generate chat completion."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Prepare request parameters
            params = {
                'model': model.value,
                'messages': messages,
                'temperature': temperature,
                'stream': stream
            }
            
            if max_tokens:
                params['max_tokens'] = max_tokens
            if tools:
                params['tools'] = tools
            if tool_choice:
                params['tool_choice'] = tool_choice
            
            # Add additional parameters
            params.update(kwargs)
            
            # Calculate input tokens
            input_tokens = self._count_tokens(str(messages), model.value)
            
            # Make API request
            if stream:
                return self._handle_streaming_response(
                    request_id, model, start_time, input_tokens, params
                )
            else:
                response = await self.client.chat.completions.create(**params)
                
                # Process response
                processing_time = (datetime.now() - start_time).total_seconds()
                
                openai_response = OpenAIResponse(
                    id=response.id,
                    request_id=request_id,
                    model=response.model,
                    content=response.choices[0].message.content,
                    usage={
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    processing_time=processing_time
                )
                
                # Update metrics
                await self._update_metrics(openai_response, True)
                
                return openai_response
                
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Chat completion failed: {e}")
            return error_response
    
    async def _handle_streaming_response(
        self,
        request_id: str,
        model: OpenAIModel,
        start_time: datetime,
        input_tokens: int,
        params: Dict[str, Any]
    ) -> AsyncGenerator[OpenAIResponse, None]:
        """Handle streaming chat completion response."""
        try:
            stream = await self.client.chat.completions.create(**params)
            content_chunks = []
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    content_chunks.append(content)
                    
                    # Yield partial response
                    yield OpenAIResponse(
                        id=chunk.id,
                        request_id=request_id,
                        model=chunk.model,
                        content=content,
                        metadata={'partial': True}
                    )
            
            # Final response with complete content
            complete_content = ''.join(content_chunks)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            final_response = OpenAIResponse(
                id=chunk.id,
                request_id=request_id,
                model=chunk.model,
                content=complete_content,
                usage={
                    'prompt_tokens': input_tokens,
                    'completion_tokens': self._count_tokens(complete_content, model.value),
                    'total_tokens': input_tokens + self._count_tokens(complete_content, model.value)
                },
                processing_time=processing_time,
                metadata={'partial': False, 'streaming': True}
            )
            
            await self._update_metrics(final_response, True)
            yield final_response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            yield error_response
    
    async def generate_image(
        self,
        prompt: str,
        model: OpenAIModel = OpenAIModel.DALL_E_3,
        size: OpenAIImageSize = OpenAIImageSize.LARGE,
        quality: OpenAIImageQuality = OpenAIImageQuality.STANDARD,
        n: int = 1,
        style: Optional[str] = None
    ) -> OpenAIResponse:
        """Generate image using DALL-E."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Prepare request parameters
            params = {
                'model': model.value,
                'prompt': prompt,
                'size': size.value,
                'quality': quality.value,
                'n': n
            }
            
            if style:
                params['style'] = style
            
            # Make API request
            response = await self.client.images.generate(**params)
            
            # Process response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            images = []
            for image_data in response.data:
                image_info = {
                    'url': image_data.url,
                    'revised_prompt': getattr(image_data, 'revised_prompt', None)
                }
                images.append(image_info)
            
            openai_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=images,
                metadata={
                    'prompt': prompt,
                    'size': size.value,
                    'quality': quality.value,
                    'n': n
                },
                processing_time=processing_time
            )
            
            await self._update_metrics(openai_response, True)
            return openai_response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Image generation failed: {e}")
            return error_response
    
    async def transcribe_audio(
        self,
        audio_file: bytes,
        filename: str,
        model: OpenAIModel = OpenAIModel.WHISPER_1,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0
    ) -> OpenAIResponse:
        """Transcribe audio using Whisper."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Prepare audio file
            audio_buffer = BytesIO(audio_file)
            audio_buffer.name = filename
            
            # Prepare request parameters
            params = {
                'model': model.value,
                'file': audio_buffer,
                'response_format': response_format,
                'temperature': temperature
            }
            
            if language:
                params['language'] = language
            if prompt:
                params['prompt'] = prompt
            
            # Make API request
            response = await self.client.audio.transcriptions.create(**params)
            
            # Process response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            openai_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=response.text if hasattr(response, 'text') else response,
                metadata={
                    'filename': filename,
                    'language': language,
                    'response_format': response_format
                },
                processing_time=processing_time
            )
            
            await self._update_metrics(openai_response, True)
            return openai_response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Audio transcription failed: {e}")
            return error_response
    
    async def text_to_speech(
        self,
        text: str,
        voice: TTSVoice = TTSVoice.ALLOY,
        model: OpenAIModel = OpenAIModel.TTS_1,
        response_format: TTSResponseFormat = TTSResponseFormat.MP3,
        speed: float = 1.0
    ) -> OpenAIResponse:
        """Convert text to speech."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Make API request
            response = await self.client.audio.speech.create(
                model=model.value,
                voice=voice.value,
                input=text,
                response_format=response_format.value,
                speed=speed
            )
            
            # Process response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Get audio content
            audio_content = await response.aread()
            
            openai_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=audio_content,
                metadata={
                    'text': text,
                    'voice': voice.value,
                    'response_format': response_format.value,
                    'speed': speed,
                    'content_type': f'audio/{response_format.value}'
                },
                processing_time=processing_time
            )
            
            await self._update_metrics(openai_response, True)
            return openai_response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Text-to-speech failed: {e}")
            return error_response
    
    async def create_embeddings(
        self,
        text: Union[str, List[str]],
        model: OpenAIModel = OpenAIModel.TEXT_EMBEDDING_3_SMALL,
        dimensions: Optional[int] = None
    ) -> OpenAIResponse:
        """Create text embeddings."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Prepare request parameters
            params = {
                'model': model.value,
                'input': text
            }
            
            if dimensions:
                params['dimensions'] = dimensions
            
            # Make API request
            response = await self.client.embeddings.create(**params)
            
            # Process response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            embeddings = [data.embedding for data in response.data]
            
            openai_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=response.model,
                content=embeddings,
                usage={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                metadata={
                    'input_type': 'list' if isinstance(text, list) else 'string',
                    'input_count': len(text) if isinstance(text, list) else 1,
                    'dimensions': dimensions
                },
                processing_time=processing_time
            )
            
            await self._update_metrics(openai_response, True)
            return openai_response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Embedding creation failed: {e}")
            return error_response
    
    async def moderate_content(
        self,
        text: str,
        model: OpenAIModel = OpenAIModel.TEXT_MODERATION_LATEST
    ) -> OpenAIResponse:
        """Moderate content for policy violations."""
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Make API request
            response = await self.client.moderations.create(
                input=text,
                model=model.value
            )
            
            # Process response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            moderation_result = response.results[0]
            
            openai_response = OpenAIResponse(
                id=response.id,
                request_id=request_id,
                model=response.model,
                content={
                    'flagged': moderation_result.flagged,
                    'categories': dict(moderation_result.categories),
                    'category_scores': dict(moderation_result.category_scores)
                },
                metadata={'input_text': text},
                processing_time=processing_time
            )
            
            await self._update_metrics(openai_response, True)
            return openai_response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_response = OpenAIResponse(
                id=str(uuid.uuid4()),
                request_id=request_id,
                model=model.value,
                content=None,
                error=str(e),
                processing_time=processing_time
            )
            
            await self._update_metrics(error_response, False)
            self.logger.error(f"Content moderation failed: {e}")
            return error_response
    
    def _count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for a specific model."""
        try:
            # Get appropriate tokenizer
            encoding = None
            if 'gpt-4' in model:
                encoding = self.tokenizers.get('gpt-4')
            elif 'gpt-3.5' in model:
                encoding = self.tokenizers.get('gpt-3.5-turbo')
            elif 'embedding' in model:
                encoding = self.tokenizers.get('text-embedding-ada-002')
            
            if encoding:
                return len(encoding.encode(text))
            else:
                # Fallback estimation
                return len(text.split()) * 1.3
        except Exception:
            # Fallback estimation
            return len(text.split()) * 1.3
    
    async def _update_metrics(self, response -> None: OpenAIResponse, success -> None: bool) -> None:
        """Update integration metrics."""
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
            
            # Update token usage
            if response.usage:
                self.token_usage['prompt_tokens'] += response.usage.get('prompt_tokens', 0)
                self.token_usage['completion_tokens'] += response.usage.get('completion_tokens', 0)
                self.token_usage['total_tokens'] += response.usage.get('total_tokens', 0)
            
            # Update model usage
            if response.model not in self.metrics['model_usage']:
                self.metrics['model_usage'][response.model] = 0
            self.metrics['model_usage'][response.model] += 1
            
        else:
            self.metrics['failed_requests'] += 1
        
        # Update average response time
        total_requests = self.metrics['total_requests']
        current_avg = self.metrics['average_response_time']
        self.metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + response.processing_time) / total_requests
        )
        
        # Add to history (keep limited history)
        self.request_history.append(response)
        if len(self.request_history) > self.max_history:
            self.request_history.pop(0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics."""
        return {
            'requests': {
                'total': self.metrics['total_requests'],
                'successful': self.metrics['successful_requests'],
                'failed': self.metrics['failed_requests'],
                'success_rate': (
                    self.metrics['successful_requests'] / max(self.metrics['total_requests'], 1)
                ) * 100
            },
            'performance': {
                'average_response_time': self.metrics['average_response_time']
            },
            'usage': {
                'token_usage': self.token_usage,
                'model_usage': self.metrics['model_usage']
            },
            'costs': self.metrics['cost_tracking']
        }
    
    def get_request_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent request history."""
        recent_history = self.request_history[-limit:]
        return [
            {
                'id': req.id,
                'request_id': req.request_id,
                'model': req.model,
                'processing_time': req.processing_time,
                'success': req.error is None,
                'error': req.error,
                'created_at': req.created_at.isoformat()
            }
            for req in recent_history
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of OpenAI integration."""
        try:
            # Simple API call to check connectivity
            models = await self.client.models.list()
            
            return {
                'status': 'healthy',
                'api_accessible': True,
                'models_available': len(models.data),
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'api_accessible': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }


# Example usage
if __name__ == "__main__":
    async def main() -> None:
        # Initialize OpenAI integration
        openai_integration = OpenAIIntegration(
            api_key="your-openai-api-key"
        )
        
        await openai_integration.initialize()
        
        # Test chat completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
        
        response = await openai_integration.chat_completion(
            messages=messages,
            model=OpenAIModel.GPT_4_TURBO,
            max_tokens=100
        )
        
        print(f"Response: {response.content}")
        print(f"Usage: {response.usage}")
        
        # Get metrics
        metrics = openai_integration.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")
    
    # asyncio.run(main())