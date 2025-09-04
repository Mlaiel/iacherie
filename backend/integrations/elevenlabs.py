"""ElevenLabs Integration - Advanced Voice Synthesis
==================================================

Professional ElevenLabs API integration for high-quality voice synthesis,
voice cloning, and speech generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import io

logger = logging.getLogger(__name__)


class ElevenLabsModel(str, Enum):
    """ElevenLabs voice models."""
    ELEVEN_MULTILINGUAL_V2 = "eleven_multilingual_v2"
    ELEVEN_MULTILINGUAL_V1 = "eleven_multilingual_v1"
    ELEVEN_MONOLINGUAL_V1 = "eleven_monolingual_v1"
    ELEVEN_ENGLISH_V1 = "eleven_english_v1"


class VoiceCategory(str, Enum):
    """Voice categories."""
    PREMADE = "premade"
    CLONED = "cloned"
    PROFESSIONAL = "professional"
    INSTANT = "instant"


@dataclass
class Voice:
    """ElevenLabs voice configuration."""
    voice_id: str
    name: str
    category: VoiceCategory
    description: Optional[str] = None
    preview_url: Optional[str] = None
    available_for_tiers: List[str] = None
    settings: Optional[Dict[str, Any]] = None


@dataclass
class VoiceSettings:
    """Voice synthesis settings."""
    stability: float = 0.75
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True


@dataclass
class SpeechSynthesisResult:
    """Speech synthesis result."""
    audio_data: bytes
    voice_id: str
    text: str
    model: str
    voice_settings: VoiceSettings
    duration_ms: int
    characters_used: int
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class VoiceCloneResult:
    """Voice cloning result."""
    voice_id: str
    name: str
    status: str
    description: Optional[str]
    created_at: datetime
    metadata: Dict[str, Any]


class ElevenLabsIntegration:
    """Professional ElevenLabs API integration."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.elevenlabs.io/v1",
        timeout: int = 60
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Usage tracking
        self.character_count = 0
        self.request_count = 0
        self.synthesis_history: List[Dict[str, Any]] = []
        
        logger.info("ElevenLabs integration initialized")
    
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
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "Ainflue/1.0"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_voices(self) -> List[Voice]:
        """Get available voices."""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/voices") as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"ElevenLabs API error: {error_data}")
                
                result = await response.json()
                voices = []
                
                for voice_data in result.get("voices", []):
                    voice = Voice(
                        voice_id=voice_data["voice_id"],
                        name=voice_data["name"],
                        category=VoiceCategory(voice_data.get("category", "premade")),
                        description=voice_data.get("description"),
                        preview_url=voice_data.get("preview_url"),
                        available_for_tiers=voice_data.get("available_for_tiers", []),
                        settings=voice_data.get("settings")
                    )
                    voices.append(voice)
                
                logger.info(f"Retrieved {len(voices)} voices")
                return voices
        
        except Exception as e:
            logger.error(f"Failed to get voices: {e}")
            raise
    
    async def synthesize_speech(
        self,
        text: str,
        voice_id: str,
        model: ElevenLabsModel = ElevenLabsModel.ELEVEN_MULTILINGUAL_V2,
        voice_settings: Optional[VoiceSettings] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SpeechSynthesisResult:
        """Synthesize speech from text."""
        await self._ensure_session()
        
        if voice_settings is None:
            voice_settings = VoiceSettings()
        
        data = {
            "text": text,
            "model_id": model.value,
            "voice_settings": {
                "stability": voice_settings.stability,
                "similarity_boost": voice_settings.similarity_boost,
                "style": voice_settings.style,
                "use_speaker_boost": voice_settings.use_speaker_boost
            }
        }
        
        try:
            start_time = datetime.now()
            
            async with self.session.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"ElevenLabs TTS error: {error_data}")
                
                audio_data = await response.read()
                end_time = datetime.now()
                
                # Calculate duration (approximate based on text length)
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Track usage
                self.character_count += len(text)
                self.request_count += 1
                
                result = SpeechSynthesisResult(
                    audio_data=audio_data,
                    voice_id=voice_id,
                    text=text,
                    model=model.value,
                    voice_settings=voice_settings,
                    duration_ms=duration_ms,
                    characters_used=len(text),
                    created_at=start_time,
                    metadata=metadata or {}
                )
                
                self._add_to_history("speech_synthesis", {
                    "voice_id": voice_id,
                    "text_length": len(text),
                    "model": model.value
                }, result, metadata)
                
                logger.info(f"Speech synthesized: {len(text)} characters, {len(audio_data)} bytes")
                return result
        
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise
    
    async def clone_voice(
        self,
        name: str,
        description: str,
        files: List[bytes],
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VoiceCloneResult:
        """Clone a voice from audio samples."""
        await self._ensure_session()
        
        # Prepare form data
        form_data = aiohttp.FormData()
        form_data.add_field('name', name)
        form_data.add_field('description', description)
        
        if labels:
            form_data.add_field('labels', json.dumps(labels))
        
        # Add audio files
        for i, file_data in enumerate(files):
            form_data.add_field(
                'files',
                io.BytesIO(file_data),
                filename=f'sample_{i}.wav',
                content_type='audio/wav'
            )
        
        try:
            # Temporarily update headers for form data
            original_headers = self.session.headers.copy()
            del self.session.headers['Content-Type']
            
            async with self.session.post(
                f"{self.base_url}/voices/add",
                data=form_data
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"ElevenLabs voice cloning error: {error_data}")
                
                result = await response.json()
                
                voice_clone = VoiceCloneResult(
                    voice_id=result["voice_id"],
                    name=name,
                    status="created",
                    description=description,
                    created_at=datetime.now(),
                    metadata=metadata or {}
                )
                
                self.request_count += 1
                self._add_to_history("voice_clone", {
                    "name": name,
                    "sample_count": len(files)
                }, voice_clone, metadata)
                
                logger.info(f"Voice cloned successfully: {voice_clone.voice_id}")
                return voice_clone
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            raise
        finally:
            # Restore original headers
            self.session.headers.update(original_headers)
    
    async def get_voice_details(self, voice_id: str) -> Voice:
        """Get detailed information about a specific voice."""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/voices/{voice_id}") as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"ElevenLabs API error: {error_data}")
                
                voice_data = await response.json()
                
                voice = Voice(
                    voice_id=voice_data["voice_id"],
                    name=voice_data["name"],
                    category=VoiceCategory(voice_data.get("category", "premade")),
                    description=voice_data.get("description"),
                    preview_url=voice_data.get("preview_url"),
                    available_for_tiers=voice_data.get("available_for_tiers", []),
                    settings=voice_data.get("settings")
                )
                
                logger.info(f"Voice details retrieved: {voice_id}")
                return voice
        
        except Exception as e:
            logger.error(f"Failed to get voice details: {e}")
            raise
    
    async def delete_voice(self, voice_id: str) -> bool:
        """Delete a cloned voice."""
        await self._ensure_session()
        
        try:
            async with self.session.delete(f"{self.base_url}/voices/{voice_id}") as response:
                if response.status not in [200, 204]:
                    error_data = await response.json()
                    raise Exception(f"ElevenLabs API error: {error_data}")
                
                self.request_count += 1
                self._add_to_history("voice_delete", {"voice_id": voice_id}, {"deleted": True}, None)
                
                logger.info(f"Voice deleted: {voice_id}")
                return True
        
        except Exception as e:
            logger.error(f"Failed to delete voice: {e}")
            raise
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get user account information and usage."""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/user") as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"ElevenLabs API error: {error_data}")
                
                user_info = await response.json()
                logger.info("User info retrieved")
                return user_info
        
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise
    
    async def get_usage_history(self, start_unix: Optional[int] = None, end_unix: Optional[int] = None) -> Dict[str, Any]:
        """Get usage history within date range."""
        await self._ensure_session()
        
        params = {}
        if start_unix:
            params['start_unix'] = start_unix
        if end_unix:
            params['end_unix'] = end_unix
        
        try:
            async with self.session.get(f"{self.base_url}/user/usage", params=params) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"ElevenLabs API error: {error_data}")
                
                usage_data = await response.json()
                logger.info("Usage history retrieved")
                return usage_data
        
        except Exception as e:
            logger.error(f"Failed to get usage history: {e}")
            raise
    
    async def stream_speech(
        self,
        text: str,
        voice_id: str,
        model: ElevenLabsModel = ElevenLabsModel.ELEVEN_MULTILINGUAL_V2,
        voice_settings: Optional[VoiceSettings] = None,
        chunk_size: int = 8192
    ) -> AsyncGenerator[bytes, None]:
        """Stream speech synthesis for real-time playback."""
        await self._ensure_session()
        
        if voice_settings is None:
            voice_settings = VoiceSettings()
        
        data = {
            "text": text,
            "model_id": model.value,
            "voice_settings": {
                "stability": voice_settings.stability,
                "similarity_boost": voice_settings.similarity_boost,
                "style": voice_settings.style,
                "use_speaker_boost": voice_settings.use_speaker_boost
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/text-to-speech/{voice_id}/stream",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"ElevenLabs streaming error: {error_data}")
                
                async for chunk in response.content.iter_chunked(chunk_size):
                    yield chunk
                
                # Track usage
                self.character_count += len(text)
                self.request_count += 1
                
                self._add_to_history("stream_synthesis", {
                    "voice_id": voice_id,
                    "text_length": len(text),
                    "model": model.value
                }, {"streaming": True}, None)
        
        except Exception as e:
            logger.error(f"Streaming synthesis failed: {e}")
            raise
    
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
        
        self.synthesis_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.synthesis_history) > 100:
            self.synthesis_history = self.synthesis_history[-100:]
    
    def _summarize_response(self, response_data: Any) -> Dict[str, Any]:
        """Create summary of response data."""
        if isinstance(response_data, SpeechSynthesisResult):
            return {
                "type": "speech_synthesis",
                "characters_used": response_data.characters_used,
                "audio_size": len(response_data.audio_data),
                "duration_ms": response_data.duration_ms
            }
        elif isinstance(response_data, VoiceCloneResult):
            return {
                "type": "voice_clone",
                "voice_id": response_data.voice_id,
                "status": response_data.status
            }
        elif isinstance(response_data, dict):
            return {
                "type": "generic",
                "keys": list(response_data.keys())
            }
        else:
            return {"type": "unknown"}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get local usage statistics."""
        return {
            "total_requests": self.request_count,
            "total_characters": self.character_count,
            "recent_operations": len(self.synthesis_history),
            "operations_by_type": self._get_operations_breakdown()
        }
    
    def _get_operations_breakdown(self) -> Dict[str, int]:
        """Get breakdown of operations by type."""
        breakdown = {}
        for entry in self.synthesis_history:
            operation = entry["operation"]
            breakdown[operation] = breakdown.get(operation, 0) + 1
        return breakdown


# Utility functions
async def create_elevenlabs_integration(api_key: str) -> ElevenLabsIntegration:
    """Create and initialize ElevenLabs integration."""
    integration = ElevenLabsIntegration(api_key=api_key)
    await integration._ensure_session()
    return integration


async def quick_speech_synthesis(
    text: str,
    voice_id: str,
    api_key: str,
    model: ElevenLabsModel = ElevenLabsModel.ELEVEN_MULTILINGUAL_V2
) -> bytes:
    """Quick speech synthesis utility."""
    async with ElevenLabsIntegration(api_key) as elevenlabs:
        result = await elevenlabs.synthesize_speech(
            text=text,
            voice_id=voice_id,
            model=model
        )
        return result.audio_data


async def get_default_voice_id(api_key: str) -> str:
    """Get a default voice ID for quick usage."""
    async with ElevenLabsIntegration(api_key) as elevenlabs:
        voices = await elevenlabs.get_voices()
        if voices:
            # Return first available premade voice
            for voice in voices:
                if voice.category == VoiceCategory.PREMADE:
                    return voice.voice_id
            # If no premade voice, return first voice
            return voices[0].voice_id
        else:
            raise Exception("No voices available")


if __name__ == "__main__":
    # Example usage
    async def main():
        import os
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            print("Please set ELEVENLABS_API_KEY environment variable")
            return
        
        async with ElevenLabsIntegration(api_key) as elevenlabs:
            # Test get voices
            voices = await elevenlabs.get_voices()
            print(f"Available voices: {len(voices)}")
            
            if voices:
                # Test speech synthesis
                voice_id = voices[0].voice_id
                result = await elevenlabs.synthesize_speech(
                    text="Hello, this is a test of ElevenLabs integration.",
                    voice_id=voice_id
                )
                print(f"Synthesized {len(result.audio_data)} bytes of audio")
                
                # Test usage stats
                stats = elevenlabs.get_usage_stats()
                print(f"Usage stats: {stats}")
    
    asyncio.run(main())