"""
🎵 AUDIO STUDIO - Real AI Audio Generation
==========================================
Uses intelligent API orchestrator + ElevenLabs/OpenAI
Author: Fahed Mlaiel
"""

import logging
import time
from typing import Dict, Any, Optional
from backend.core.backend_api_orchestrator import (
    BackendAPIOrchestrator,
    ContentType,
    QualityLevel
)

logger = logging.getLogger(__name__)


class AudioStudio:
    """Real audio generation using intelligent API selection"""
    
    def __init__(self):
        self.orchestrator = BackendAPIOrchestrator()
        self._openai_client = None
        self._elevenlabs_client = None
        
    async def _get_openai_client(self):
        """Get OpenAI client lazily"""
        if not self._openai_client:
            from backend.integrations.openai import OpenAIIntegration
            self._openai_client = OpenAIIntegration()
        return self._openai_client
    
    async def text_to_speech(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
        quality: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate audio from text using TTS
        Priority: Internal Models (FREE) → External APIs (PAID)
        """
        
        try:
            logger.info(f"🎵 TTS Request: {text[:50]}... (voice: {voice}, lang: {language})")
            
            # ✅ PRIORITY 1: Try INTERNAL Coqui TTS (FREE)
            try:
                from TTS.api import TTS
                import numpy as np
                import io
                import base64
                from scipy.io import wavfile
                
                logger.info("🎵 Using Coqui TTS (Internal FREE model)")
                
                # Initialize Coqui TTS (multi-language support)
                if language.startswith('fr'):
                    model_name = "tts_models/fr/css10/vits"  # French
                elif language.startswith('es'):
                    model_name = "tts_models/es/css10/vits"  # Spanish
                elif language.startswith('de'):
                    model_name = "tts_models/de/thorsten/vits"  # German
                else:
                    model_name = "tts_models/en/ljspeech/tacotron2-DDC"  # English
                
                tts = TTS(model_name=model_name)
                
                # Generate audio to file
                output_path = f"/tmp/tts_output_{int(time.time())}.wav"
                tts.tts_to_file(text=text, file_path=output_path)
                
                # Read and encode audio
                with open(output_path, 'rb') as f:
                    audio_bytes = f.read()
                
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                # Cleanup
                import os
                os.remove(output_path)
                
                return {
                    'status': 'completed',
                    'result': {
                        'audio': audio_b64,
                        'format': 'wav',
                        'model': model_name,
                        'duration': len(audio_bytes) / 44100  # Approximate
                    },
                    'api_used': 'coqui-tts-internal',
                    'cost': 0.0  # FREE!
                }
                
            except Exception as e:
                logger.warning(f"Coqui TTS failed: {e}, trying external APIs...")
            
            # ✅ PRIORITY 2: Try external APIs (PAID fallback)
            quality_level = QualityLevel.PREMIUM if quality == "high" else QualityLevel.STANDARD
            
            selected_api = self.orchestrator.select_best_api(
                content_type=ContentType.AUDIO,
                quality=quality_level,
                use_case='tts'
            )
            
            logger.info(f"🎵 Fallback to external API: {selected_api}")
            
            if selected_api == 'elevenlabs' and self.orchestrator.is_api_available('elevenlabs'):
                try:
                    from backend.integrations.elevenlabs import ElevenLabsIntegration
                    client = ElevenLabsIntegration()
                    result = await client.text_to_speech(text=text, voice=voice)
                    
                    return {
                        'status': 'completed',
                        'result': {
                            'audio_url': result.get('audio_url'),
                            'duration': result.get('duration', 0)
                        },
                        'api_used': 'elevenlabs',
                        'cost': self.orchestrator.estimate_cost('elevenlabs', quality_level)
                    }
                except Exception as e:
                    logger.warning(f"ElevenLabs failed: {e}")
            
            # Fallback to OpenAI TTS
            if selected_api == 'openai-tts' or True:  # Always try if others fail
                try:
                    client = await self._get_openai_client()
                    result = await client.text_to_speech(text=text, voice=voice)
                    
                    return {
                        'status': 'completed',
                        'result': {
                            'audio_url': result.get('url'),
                            'audio': result.get('data')
                        },
                        'api_used': 'openai-tts',
                        'cost': self.orchestrator.estimate_cost('openai-tts', quality_level)
                    }
                except Exception as e:
                    logger.error(f"OpenAI TTS failed: {e}")
            
            # ✅ FINAL FALLBACK: Simple gTTS (FREE)
            logger.info("Using gTTS as final fallback")
            from gtts import gTTS
            import io
            import base64
            
            tts = gTTS(text=text, lang=language[:2])
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            audio_b64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            
            return {
                'status': 'completed',
                'result': {
                    'audio': audio_b64,
                    'format': 'mp3',
                    'model': 'gtts'
                },
                'api_used': 'gtts-fallback',
                'cost': 0.0  # FREE!
            }
                
        except Exception as e:
            logger.error(f"All TTS methods failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def clone_voice(self, audio_data: bytes, filename: str) -> Dict[str, Any]:
        """Clone voice from audio sample"""
        return {
            'voice_id': f"voice_{int(time.time())}",
            'status': 'completed',
            'message': 'Voice cloning coming soon'
        }
    
    async def list_voices(self) -> Dict[str, Any]:
        """List available voices"""
        return {
            'voices': [
                {'id': 'alloy', 'name': 'Alloy', 'provider': 'openai'},
                {'id': 'echo', 'name': 'Echo', 'provider': 'openai'},
                {'id': 'fable', 'name': 'Fable', 'provider': 'openai'},
                {'id': 'onyx', 'name': 'Onyx', 'provider': 'openai'},
                {'id': 'nova', 'name': 'Nova', 'provider': 'openai'},
                {'id': 'shimmer', 'name': 'Shimmer', 'provider': 'openai'},
            ]
        }
    
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio using Whisper"""
        try:
            client = await self._get_openai_client()
            result = await client.transcribe_audio(
                audio_file=audio_data,
                language=language
            )
            return {
                'status': 'completed',
                'result': result
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def enhance(self, audio_data: bytes) -> Dict[str, Any]:
        """Enhance audio quality"""
        return {
            'status': 'completed',
            'message': 'Audio enhancement coming soon'
        }
    
    async def mix(self, tracks: list) -> Dict[str, Any]:
        """Mix multiple audio tracks"""
        return {
            'status': 'completed',
            'message': 'Audio mixing coming soon'
        }
    
    async def analyze(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze audio content"""
        return {
            'status': 'completed',
            'analysis': {
                'duration': 0,
                'format': 'unknown',
                'sample_rate': 0
            },
            'message': 'Analysis feature coming soon'
        }
