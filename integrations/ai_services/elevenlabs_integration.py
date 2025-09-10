"""ElevenLabs Integration - Advanced Voice Synthesis and Cloning
============================================================

Comprehensive integration with ElevenLabs API for voice synthesis, voice cloning,
speech-to-speech, and advanced audio generation capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import base64
import uuid
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import io

import aiohttp
import aiofiles

logger = logging.getLogger(__name__)

class VoiceModel(Enum):
    """ElevenLabs voice model types."""
    ELEVEN_MULTILINGUAL_V2 = "eleven_multilingual_v2"
    ELEVEN_MULTILINGUAL_V1 = "eleven_multilingual_v1"
    ELEVEN_MONOLINGUAL_V1 = "eleven_monolingual_v1"
    ELEVEN_TURBO_V2 = "eleven_turbo_v2"
    ELEVEN_FLASH_V2 = "eleven_flash_v2"

class VoiceCategory(Enum):
    """Voice categories."""
    PREMADE = "premade"
    CLONED = "cloned"
    PROFESSIONAL = "professional"
    GENERATED = "generated"

class OutputFormat(Enum):
    """Audio output formats."""
    MP3_22050_32 = "mp3_22050_32"
    MP3_44100_32 = "mp3_44100_32"
    MP3_44100_64 = "mp3_44100_64"
    MP3_44100_96 = "mp3_44100_96"
    MP3_44100_128 = "mp3_44100_128"
    MP3_44100_192 = "mp3_44100_192"
    PCM_16000 = "pcm_16000"
    PCM_22050 = "pcm_22050"
    PCM_24000 = "pcm_24000"
    PCM_44100 = "pcm_44100"
    ULAW_8000 = "ulaw_8000"

@dataclass
class ElevenLabsRequest:
    """ElevenLabs API request."""
    text: str
    voice_id: str
    model_id: VoiceModel = VoiceModel.ELEVEN_MULTILINGUAL_V2
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Voice settings
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True
    
    # Output settings
    output_format: OutputFormat = OutputFormat.MP3_44100_128
    optimize_streaming_latency: int = 0
    
    # Voice cloning (for custom voices)
    voice_samples: List[str] = field(default_factory=list)  # Base64 encoded audio
    voice_name: Optional[str] = None
    voice_description: Optional[str] = None
    
    # Speech-to-speech settings
    source_audio: Optional[str] = None  # Base64 encoded
    
    # Advanced options
    pronunciation_dictionary_locators: List[Dict[str, str]] = field(default_factory=list)
    
    # Request metadata
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ElevenLabsResponse:
    """ElevenLabs API response."""
    request_id: str
    voice_id: str
    model_id: VoiceModel
    
    # Generated audio
    audio: Optional[str] = None  # Base64 encoded
    audio_url: Optional[str] = None
    
    # Voice information
    voice_name: Optional[str] = None
    voice_category: Optional[VoiceCategory] = None
    
    # Generation metadata
    characters: int = 0
    character_cost: float = 0.0
    
    # Performance metrics
    latency_ms: Optional[float] = None
    cost_estimate: Optional[float] = None
    
    # Error handling
    error: Optional[str] = None
    error_code: Optional[str] = None
    error_details: Dict[str, Any] = field(default_factory=dict)
    
    # Response metadata
    response_metadata: Dict[str, Any] = field(default_factory=dict)
    
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Voice:
    """Voice information."""
    voice_id: str
    name: str
    category: VoiceCategory
    description: str = ""
    preview_url: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    settings: Dict[str, float] = field(default_factory=dict)
    sharing: Dict[str, Any] = field(default_factory=dict)
    
    # Voice characteristics
    gender: Optional[str] = None
    age: Optional[str] = None
    accent: Optional[str] = None
    language: Optional[str] = None
    use_case: Optional[str] = None

@dataclass
class ElevenLabsConfiguration:
    """ElevenLabs integration configuration."""
    # Authentication
    api_key: str
    api_base: str = "https://api.elevenlabs.io"
    api_version: str = "v1"
    
    # Default settings
    default_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel
    default_model: VoiceModel = VoiceModel.ELEVEN_MULTILINGUAL_V2
    default_stability: float = 0.5
    default_similarity_boost: float = 0.75
    default_output_format: OutputFormat = OutputFormat.MP3_44100_128
    
    # Rate limiting
    requests_per_minute: int = 20
    characters_per_month: int = 10000
    max_concurrent_requests: int = 5
    
    # Performance settings
    timeout_seconds: int = 60
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Cost management
    monthly_budget_usd: Optional[float] = None
    cost_per_character: float = 0.0003  # Approximate cost
    cost_alerts_enabled: bool = True
    
    # Output settings
    save_generated_audio: bool = True
    output_directory: str = "/tmp/elevenlabs_outputs"
    
    # Voice library
    enable_voice_library: bool = True
    auto_detect_voice: bool = False

class ElevenLabsIntegration:
    """Comprehensive ElevenLabs voice synthesis integration."""
    
    def __init__(self, config: ElevenLabsConfiguration):
        self.config = config
        self.session = None
        
        # Voice library
        self.voices: Dict[str, Voice] = {}
        self.voice_library_loaded = False
        
        # Usage tracking
        self.request_count = 0
        self.characters_used = 0
        self.cost_tracking = 0.0
        self.last_reset = datetime.utcnow()
        
        # Performance monitoring
        self.response_times = []
        self.error_count = 0
        
        # Rate limiting
        self.request_semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self.last_request_time = 0
        
        logger.info("ElevenLabs Integration initialized")

    async def initialize(self) -> None:
        """Initialize ElevenLabs integration."""
        try:
            # Setup HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds),
                headers={
                    'xi-api-key': self.config.api_key,
                    'User-Agent': 'Ainflue-ElevenLabs/1.0',
                    'Accept': 'application/json'
                }
            )
            
            # Create output directory
            import os
            os.makedirs(self.config.output_directory, exist_ok=True)
            
            # Load voice library
            if self.config.enable_voice_library:
                await self._load_voice_library()
                
            # Test API connection
            await self._test_connection()
            
            logger.info("ElevenLabs integration initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs integration: {e}")
            raise

    async def _test_connection(self) -> None:
        """Test API connection."""
        try:
            url = f"{self.config.api_base}/{self.config.api_version}/user"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    character_count = data.get('subscription', {}).get('character_count', 0)
                    character_limit = data.get('subscription', {}).get('character_limit', 0)
                    logger.info(f"Connected to ElevenLabs - Characters: {character_count}/{character_limit}")
                else:
                    raise Exception(f"API test failed: {response.status}")
                    
        except Exception as e:
            logger.warning(f"API connection test failed: {e}")

    async def _load_voice_library(self) -> None:
        """Load available voices."""
        try:
            url = f"{self.config.api_base}/{self.config.api_version}/voices"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for voice_data in data.get('voices', []):
                        voice = Voice(
                            voice_id=voice_data['voice_id'],
                            name=voice_data['name'],
                            category=VoiceCategory(voice_data.get('category', 'premade')),
                            description=voice_data.get('description', ''),
                            preview_url=voice_data.get('preview_url'),
                            labels=voice_data.get('labels', {}),
                            settings=voice_data.get('settings', {}),
                            sharing=voice_data.get('sharing', {})
                        )
                        
                        # Extract characteristics from labels
                        labels = voice.labels
                        voice.gender = labels.get('gender')
                        voice.age = labels.get('age')
                        voice.accent = labels.get('accent')
                        voice.language = labels.get('language')
                        voice.use_case = labels.get('use case')
                        
                        self.voices[voice.voice_id] = voice
                        
                    self.voice_library_loaded = True
                    logger.info(f"Loaded {len(self.voices)} voices")
                    
        except Exception as e:
            logger.error(f"Failed to load voice library: {e}")

    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: Optional[VoiceModel] = None,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None,
        style: Optional[float] = None,
        output_format: Optional[OutputFormat] = None,
        **kwargs
    ) -> ElevenLabsResponse:
        """Synthesize speech from text."""
        request = ElevenLabsRequest(
            text=text,
            voice_id=voice_id or self.config.default_voice_id,
            model_id=model_id or self.config.default_model,
            stability=stability if stability is not None else self.config.default_stability,
            similarity_boost=similarity_boost if similarity_boost is not None else self.config.default_similarity_boost,
            style=style if style is not None else 0.0,
            output_format=output_format or self.config.default_output_format,
            parameters=kwargs
        )
        
        return await self._execute_synthesis_request(request)

    async def clone_voice(
        self,
        voice_name: str,
        voice_samples: List[str],  # Base64 encoded audio samples
        description: str = "",
        **kwargs
    ) -> ElevenLabsResponse:
        """Clone a voice from audio samples."""
        request = ElevenLabsRequest(
            text="",  # Not used for voice cloning
            voice_id="",  # Will be generated
            voice_samples=voice_samples,
            voice_name=voice_name,
            voice_description=description,
            parameters=kwargs
        )
        
        return await self._execute_voice_clone_request(request)

    async def speech_to_speech(
        self,
        source_audio: str,  # Base64 encoded
        target_voice_id: str,
        model_id: Optional[VoiceModel] = None,
        **kwargs
    ) -> ElevenLabsResponse:
        """Convert speech from one voice to another."""
        request = ElevenLabsRequest(
            text="",  # Not used for speech-to-speech
            voice_id=target_voice_id,
            model_id=model_id or self.config.default_model,
            source_audio=source_audio,
            parameters=kwargs
        )
        
        return await self._execute_speech_to_speech_request(request)

    async def stream_synthesis(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: Optional[VoiceModel] = None,
        **kwargs
    ) -> AsyncGenerator[bytes, None]:
        """Stream synthesized speech in real-time."""
        request = ElevenLabsRequest(
            text=text,
            voice_id=voice_id or self.config.default_voice_id,
            model_id=model_id or self.config.default_model,
            optimize_streaming_latency=4,  # Maximum optimization for streaming
            parameters=kwargs
        )
        
        async for chunk in self._execute_streaming_request(request):
            yield chunk

    async def _execute_synthesis_request(self, request: ElevenLabsRequest) -> ElevenLabsResponse:
        """Execute text-to-speech synthesis request."""
        start_time = time.time()
        
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                url = f"{self.config.api_base}/{self.config.api_version}/text-to-speech/{request.voice_id}"
                
                # Prepare request payload
                payload = {
                    "text": request.text,
                    "model_id": request.model_id.value,
                    "voice_settings": {
                        "stability": request.stability,
                        "similarity_boost": request.similarity_boost,
                        "style": request.style,
                        "use_speaker_boost": request.use_speaker_boost
                    }
                }
                
                # Add pronunciation dictionary if provided
                if request.pronunciation_dictionary_locators:
                    payload["pronunciation_dictionary_locators"] = request.pronunciation_dictionary_locators
                
                # Set output format
                params = {}
                if request.output_format != OutputFormat.MP3_44100_128:
                    params["output_format"] = request.output_format.value
                if request.optimize_streaming_latency > 0:
                    params["optimize_streaming_latency"] = request.optimize_streaming_latency
                
                # Execute request
                async with self.session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        # Read audio data
                        audio_data = await response.read()
                        audio_b64 = base64.b64encode(audio_data).decode()
                        
                        # Save audio if configured
                        if self.config.save_generated_audio:
                            await self._save_audio(audio_data, request.request_id)
                        
                        # Calculate cost
                        character_count = len(request.text)
                        cost = character_count * self.config.cost_per_character
                        
                        result = ElevenLabsResponse(
                            request_id=request.request_id,
                            voice_id=request.voice_id,
                            model_id=request.model_id,
                            audio=audio_b64,
                            voice_name=self.voices.get(request.voice_id, Voice("", "", VoiceCategory.PREMADE)).name,
                            characters=character_count,
                            character_cost=cost,
                            latency_ms=(time.time() - start_time) * 1000,
                            cost_estimate=cost
                        )
                        
                        # Update usage tracking
                        await self._update_usage_tracking(request, result)
                        
                        return result
                        
                    else:
                        error_text = await response.text()
                        raise Exception(f"Synthesis failed: {response.status} - {error_text}")
                        
        except Exception as e:
            self.error_count += 1
            logger.error(f"ElevenLabs synthesis failed: {e}")
            
            return ElevenLabsResponse(
                request_id=request.request_id,
                voice_id=request.voice_id,
                model_id=request.model_id,
                error=str(e),
                error_code="synthesis_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    async def _execute_voice_clone_request(self, request: ElevenLabsRequest) -> ElevenLabsResponse:
        """Execute voice cloning request."""
        start_time = time.time()
        
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                url = f"{self.config.api_base}/{self.config.api_version}/voices/add"
                
                # Prepare form data
                data = aiohttp.FormData()
                data.add_field('name', request.voice_name or f"Cloned Voice {request.request_id}")
                
                if request.voice_description:
                    data.add_field('description', request.voice_description)
                
                # Add audio samples
                for i, sample_b64 in enumerate(request.voice_samples):
                    sample_data = base64.b64decode(sample_b64)
                    data.add_field('files', io.BytesIO(sample_data), 
                                 filename=f'sample_{i}.wav', content_type='audio/wav')
                
                # Execute request
                async with self.session.post(url, data=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        voice_id = response_data.get('voice_id')
                        
                        # Add to voice library
                        if voice_id:
                            new_voice = Voice(
                                voice_id=voice_id,
                                name=request.voice_name or f"Cloned Voice {request.request_id}",
                                category=VoiceCategory.CLONED,
                                description=request.voice_description or ""
                            )
                            self.voices[voice_id] = new_voice
                        
                        return ElevenLabsResponse(
                            request_id=request.request_id,
                            voice_id=voice_id or "",
                            model_id=request.model_id,
                            voice_name=request.voice_name,
                            voice_category=VoiceCategory.CLONED,
                            latency_ms=(time.time() - start_time) * 1000,
                            response_metadata=response_data
                        )
                        
                    else:
                        error_text = await response.text()
                        raise Exception(f"Voice cloning failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return ElevenLabsResponse(
                request_id=request.request_id,
                voice_id="",
                model_id=request.model_id,
                error=str(e),
                error_code="voice_clone_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    async def _execute_speech_to_speech_request(self, request: ElevenLabsRequest) -> ElevenLabsResponse:
        """Execute speech-to-speech conversion request."""
        start_time = time.time()
        
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                url = f"{self.config.api_base}/{self.config.api_version}/speech-to-speech/{request.voice_id}"
                
                # Prepare form data
                data = aiohttp.FormData()
                data.add_field('model_id', request.model_id.value)
                
                # Add voice settings
                data.add_field('voice_settings', json.dumps({
                    "stability": request.stability,
                    "similarity_boost": request.similarity_boost,
                    "style": request.style
                }))
                
                # Add source audio
                if request.source_audio:
                    audio_data = base64.b64decode(request.source_audio)
                    data.add_field('audio', io.BytesIO(audio_data), 
                                 filename='source.wav', content_type='audio/wav')
                
                # Execute request
                async with self.session.post(url, data=data) as response:
                    if response.status == 200:
                        # Read audio data
                        audio_data = await response.read()
                        audio_b64 = base64.b64encode(audio_data).decode()
                        
                        # Save audio if configured
                        if self.config.save_generated_audio:
                            await self._save_audio(audio_data, request.request_id)
                        
                        return ElevenLabsResponse(
                            request_id=request.request_id,
                            voice_id=request.voice_id,
                            model_id=request.model_id,
                            audio=audio_b64,
                            voice_name=self.voices.get(request.voice_id, Voice("", "", VoiceCategory.PREMADE)).name,
                            latency_ms=(time.time() - start_time) * 1000
                        )
                        
                    else:
                        error_text = await response.text()
                        raise Exception(f"Speech-to-speech failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Speech-to-speech failed: {e}")
            return ElevenLabsResponse(
                request_id=request.request_id,
                voice_id=request.voice_id,
                model_id=request.model_id,
                error=str(e),
                error_code="speech_to_speech_error",
                latency_ms=(time.time() - start_time) * 1000
            )

    async def _execute_streaming_request(self, request: ElevenLabsRequest) -> AsyncGenerator[bytes, None]:
        """Execute streaming synthesis request."""
        try:
            async with self.request_semaphore:
                await self._check_rate_limits()
                
                url = f"{self.config.api_base}/{self.config.api_version}/text-to-speech/{request.voice_id}/stream"
                
                payload = {
                    "text": request.text,
                    "model_id": request.model_id.value,
                    "voice_settings": {
                        "stability": request.stability,
                        "similarity_boost": request.similarity_boost,
                        "style": request.style
                    }
                }
                
                params = {
                    "optimize_streaming_latency": request.optimize_streaming_latency,
                    "output_format": request.output_format.value
                }
                
                async with self.session.post(url, json=payload, params=params) as response:
                    if response.status == 200:
                        async for chunk in response.content.iter_chunked(8192):
                            yield chunk
                    else:
                        error_text = await response.text()
                        raise Exception(f"Streaming failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Streaming synthesis failed: {e}")

    async def _save_audio(self, audio_data: bytes, request_id: str) -> None:
        """Save generated audio to disk."""
        try:
            filename = f"{request_id}.mp3"
            filepath = f"{self.config.output_directory}/{filename}"
            
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(audio_data)
                
            logger.info(f"Saved generated audio: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")

    async def _check_rate_limits(self) -> None:
        """Check and enforce rate limits."""
        now = time.time()
        
        # Enforce minimum time between requests
        min_interval = 60.0 / self.config.requests_per_minute
        time_since_last = now - self.last_request_time
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
            
        self.last_request_time = time.time()

    async def _update_usage_tracking(
        self,
        request: ElevenLabsRequest,
        response: ElevenLabsResponse
    ) -> None:
        """Update usage tracking and cost estimation."""
        self.request_count += 1
        self.characters_used += response.characters
        
        if response.cost_estimate:
            self.cost_tracking += response.cost_estimate
            
        # Monitor performance
        if response.latency_ms:
            self.response_times.append(response.latency_ms)
            if len(self.response_times) > 100:
                self.response_times.pop(0)
                
        # Check budget alerts
        if (self.config.monthly_budget_usd and 
            self.cost_tracking > self.config.monthly_budget_usd * 0.8):
            logger.warning(f"Approaching monthly budget limit: ${self.cost_tracking:.2f}")

    async def get_voices(self, refresh: bool = False) -> List[Voice]:
        """Get available voices."""
        if refresh or not self.voice_library_loaded:
            await self._load_voice_library()
        
        return list(self.voices.values())

    async def find_voice(
        self,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        age: Optional[str] = None,
        accent: Optional[str] = None,
        language: Optional[str] = None,
        use_case: Optional[str] = None
    ) -> List[Voice]:
        """Find voices matching criteria."""
        results = []
        
        for voice in self.voices.values():
            if name and name.lower() not in voice.name.lower():
                continue
            if gender and voice.gender != gender:
                continue
            if age and voice.age != age:
                continue
            if accent and voice.accent != accent:
                continue
            if language and voice.language != language:
                continue
            if use_case and voice.use_case != use_case:
                continue
                
            results.append(voice)
            
        return results

    async def get_user_info(self) -> Dict[str, Any]:
        """Get user subscription information."""
        try:
            url = f"{self.config.api_base}/{self.config.api_version}/user"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to get user info: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {"error": str(e)}

    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "request_count": self.request_count,
            "characters_used": self.characters_used,
            "cost_tracking": self.cost_tracking,
            "error_count": self.error_count,
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "voices_available": len(self.voices),
            "last_reset": self.last_reset.isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        health = {
            "status": "healthy",
            "api_connection": "unknown",
            "voice_library_loaded": self.voice_library_loaded,
            "usage": await self.get_usage_statistics(),
            "issues": []
        }
        
        try:
            # Test API connection
            user_info = await self.get_user_info()
            if 'error' not in user_info:
                health["api_connection"] = "connected"
                subscription = user_info.get('subscription', {})
                health["character_count"] = subscription.get('character_count', 0)
                health["character_limit"] = subscription.get('character_limit', 0)
            else:
                health["api_connection"] = "failed"
                health["issues"].append("API connection failed")
                health["status"] = "degraded"
                
        except Exception as e:
            health["issues"].append(f"Health check error: {e}")
            health["status"] = "unhealthy"
            
        return health

    async def shutdown(self) -> None:
        """Shutdown ElevenLabs integration."""
        logger.info("Shutting down ElevenLabs integration...")
        
        if self.session:
            await self.session.close()
            
        logger.info("ElevenLabs integration shutdown completed")

    def __repr__(self) -> str:
        return f"ElevenLabsIntegration(requests={self.request_count}, characters={self.characters_used})"


# Export main classes
__all__ = [
    "ElevenLabsIntegration",
    "ElevenLabsConfiguration",
    "ElevenLabsRequest",
    "ElevenLabsResponse",
    "Voice",
    "VoiceModel",
    "VoiceCategory",
    "OutputFormat"
]