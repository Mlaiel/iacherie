"""🔐 Watermark Engine - Inaudible Audio Watermarking System

Advanced inaudible watermarking system for copyright protection,
content tracking, and ownership verification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
import librosa
import hashlib
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class WatermarkType(Enum):
    """Types of audio watermarks"""
    SPECTRAL_SPREAD = "spectral_spread"
    LSB_EMBEDDING = "lsb_embedding"
    PHASE_CODING = "phase_coding"
    ECHO_HIDING = "echo_hiding"
    FREQUENCY_MASKING = "frequency_masking"


class WatermarkStrength(Enum):
    """Watermark embedding strength levels"""
    SUBTLE = "subtle"
    MODERATE = "moderate"
    ROBUST = "robust"
    MAXIMUM = "maximum"


@dataclass
class WatermarkData:
    """Watermark payload data"""
    owner_id: str
    content_id: str
    timestamp: float
    metadata: Dict[str, Any]
    signature: Optional[str] = None


@dataclass
class WatermarkSettings:
    """Watermark embedding configuration"""
    watermark_type: WatermarkType = WatermarkType.SPECTRAL_SPREAD
    strength: WatermarkStrength = WatermarkStrength.MODERATE
    frequency_range: Tuple[float, float] = (1000.0, 8000.0)
    embedding_capacity: int = 256  # bits
    error_correction: bool = True
    imperceptibility_threshold: float = -40.0  # dB SNR


@dataclass
class WatermarkResult:
    """Watermark embedding/extraction result"""
    success: bool
    watermarked_audio: Optional[np.ndarray]
    extracted_data: Optional[WatermarkData]
    snr_db: float
    processing_time: float
    settings_used: WatermarkSettings
    metadata: Dict[str, Any]


class WatermarkEngine:
    """
    Advanced inaudible audio watermarking system.
    
    Provides robust, imperceptible watermarking for copyright protection
    and content tracking while maintaining audio quality.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the watermark engine.
        
        Args:
            config: Configuration dictionary for watermarking parameters
        """
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 44100)
        self.hop_length = self.config.get('hop_length', 512)
        self.n_fft = self.config.get('n_fft', 2048)
        
        # Watermark database (in production, would use persistent storage)
        self.watermark_db = {}
        
        logger.info("WatermarkEngine initialized successfully")
    
    async def embed_watermark(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        watermark_data: WatermarkData,
        settings: Optional[WatermarkSettings] = None
    ) -> WatermarkResult:
        """
        Embed inaudible watermark into audio.
        
        Args:
            audio_data: Original audio data
            watermark_data: Data to embed as watermark
            settings: Watermark embedding settings
            
        Returns:
            WatermarkResult: Watermarked audio and embedding information
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Load audio data
            audio_array, sr = self._load_audio(audio_data)
            settings = settings or WatermarkSettings()
            
            # Prepare watermark payload
            payload = await self._prepare_payload(watermark_data, settings)
            
            # Embed watermark based on type
            if settings.watermark_type == WatermarkType.SPECTRAL_SPREAD:
                watermarked_audio = await self._embed_spectral_spread(
                    audio_array, sr, payload, settings
                )
            elif settings.watermark_type == WatermarkType.LSB_EMBEDDING:
                watermarked_audio = await self._embed_lsb(
                    audio_array, sr, payload, settings
                )
            elif settings.watermark_type == WatermarkType.PHASE_CODING:
                watermarked_audio = await self._embed_phase_coding(
                    audio_array, sr, payload, settings
                )
            elif settings.watermark_type == WatermarkType.ECHO_HIDING:
                watermarked_audio = await self._embed_echo_hiding(
                    audio_array, sr, payload, settings
                )
            elif settings.watermark_type == WatermarkType.FREQUENCY_MASKING:
                watermarked_audio = await self._embed_frequency_masking(
                    audio_array, sr, payload, settings
                )
            else:
                raise ValueError(f"Unsupported watermark type: {settings.watermark_type}")
            
            # Calculate SNR
            snr_db = await self._calculate_snr(audio_array, watermarked_audio)
            
            # Store watermark info
            content_hash = self._calculate_audio_hash(audio_array)
            self.watermark_db[content_hash] = {
                'data': watermark_data,
                'settings': settings,
                'payload': payload
            }
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return WatermarkResult(
                success=True,
                watermarked_audio=watermarked_audio,
                extracted_data=None,
                snr_db=snr_db,
                processing_time=processing_time,
                settings_used=settings,
                metadata={
                    'content_hash': content_hash,
                    'payload_size': len(payload),
                    'audio_duration': len(audio_array) / sr
                }
            )
            
        except Exception as e:
            logger.error(f"Watermark embedding failed: {e}")
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return WatermarkResult(
                success=False,
                watermarked_audio=None,
                extracted_data=None,
                snr_db=0.0,
                processing_time=processing_time,
                settings_used=settings or WatermarkSettings(),
                metadata={'error': str(e)}
            )
    
    async def extract_watermark(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        settings: Optional[WatermarkSettings] = None
    ) -> WatermarkResult:
        """
        Extract watermark from audio.
        
        Args:
            audio_data: Watermarked audio data
            settings: Watermark extraction settings
            
        Returns:
            WatermarkResult: Extracted watermark data
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Load audio data
            audio_array, sr = self._load_audio(audio_data)
            settings = settings or WatermarkSettings()
            
            # Extract watermark based on type
            if settings.watermark_type == WatermarkType.SPECTRAL_SPREAD:
                extracted_payload = await self._extract_spectral_spread(
                    audio_array, sr, settings
                )
            elif settings.watermark_type == WatermarkType.LSB_EMBEDDING:
                extracted_payload = await self._extract_lsb(
                    audio_array, sr, settings
                )
            elif settings.watermark_type == WatermarkType.PHASE_CODING:
                extracted_payload = await self._extract_phase_coding(
                    audio_array, sr, settings
                )
            elif settings.watermark_type == WatermarkType.ECHO_HIDING:
                extracted_payload = await self._extract_echo_hiding(
                    audio_array, sr, settings
                )
            elif settings.watermark_type == WatermarkType.FREQUENCY_MASKING:
                extracted_payload = await self._extract_frequency_masking(
                    audio_array, sr, settings
                )
            else:
                raise ValueError(f"Unsupported watermark type: {settings.watermark_type}")
            
            # Decode payload
            watermark_data = await self._decode_payload(extracted_payload, settings)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return WatermarkResult(
                success=watermark_data is not None,
                watermarked_audio=None,
                extracted_data=watermark_data,
                snr_db=0.0,
                processing_time=processing_time,
                settings_used=settings,
                metadata={
                    'payload_size': len(extracted_payload) if extracted_payload else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Watermark extraction failed: {e}")
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return WatermarkResult(
                success=False,
                watermarked_audio=None,
                extracted_data=None,
                snr_db=0.0,
                processing_time=processing_time,
                settings_used=settings or WatermarkSettings(),
                metadata={'error': str(e)}
            )
    
    def _load_audio(self, audio_data: Union[np.ndarray, bytes, str, Path]) -> Tuple[np.ndarray, int]:
        """Load audio data into numpy array"""
        if isinstance(audio_data, np.ndarray):
            return audio_data, self.sample_rate
        elif isinstance(audio_data, (str, Path)):
            audio_array, sr = librosa.load(str(audio_data), sr=self.sample_rate)
            return audio_array, sr
        elif isinstance(audio_data, bytes):
            # Convert bytes to numpy array (simplified)
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            return audio_array, self.sample_rate
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
    
    async def _prepare_payload(
        self,
        watermark_data: WatermarkData,
        settings: WatermarkSettings
    ) -> np.ndarray:
        """Prepare watermark payload for embedding"""
        try:
            # Create payload dictionary
            payload_dict = {
                'owner_id': watermark_data.owner_id,
                'content_id': watermark_data.content_id,
                'timestamp': watermark_data.timestamp,
                'metadata': watermark_data.metadata
            }
            
            # Serialize to JSON and encode to bytes
            payload_json = json.dumps(payload_dict, sort_keys=True)
            payload_bytes = payload_json.encode('utf-8')
            
            # Add signature if not present
            if watermark_data.signature is None:
                signature = hashlib.sha256(payload_bytes).hexdigest()[:16]
                payload_dict['signature'] = signature
                payload_json = json.dumps(payload_dict, sort_keys=True)
                payload_bytes = payload_json.encode('utf-8')
            
            # Convert to binary array
            payload_bits = np.unpackbits(np.frombuffer(payload_bytes, dtype=np.uint8))
            
            # Truncate or pad to fit capacity
            if len(payload_bits) > settings.embedding_capacity:
                payload_bits = payload_bits[:settings.embedding_capacity]
            elif len(payload_bits) < settings.embedding_capacity:
                padding = np.zeros(settings.embedding_capacity - len(payload_bits), dtype=np.uint8)
                payload_bits = np.concatenate([payload_bits, padding])
            
            return payload_bits
            
        except Exception as e:
            logger.warning(f"Payload preparation failed: {e}")
            # Return empty payload
            return np.zeros(settings.embedding_capacity, dtype=np.uint8)
    
    async def _decode_payload(
        self,
        payload_bits: np.ndarray,
        settings: WatermarkSettings
    ) -> Optional[WatermarkData]:
        """Decode extracted payload bits"""
        try:
            if payload_bits is None or len(payload_bits) == 0:
                return None
            
            # Convert bits to bytes
            # Pad to byte boundary
            padding_needed = (8 - len(payload_bits) % 8) % 8
            if padding_needed > 0:
                payload_bits = np.concatenate([payload_bits, np.zeros(padding_needed, dtype=np.uint8)])
            
            payload_bytes = np.packbits(payload_bits).tobytes()
            
            # Try to decode JSON
            try:
                payload_str = payload_bytes.decode('utf-8').rstrip('\x00')
                payload_dict = json.loads(payload_str)
                
                # Verify signature
                temp_dict = payload_dict.copy()
                signature = temp_dict.pop('signature', None)
                temp_json = json.dumps(temp_dict, sort_keys=True)
                expected_signature = hashlib.sha256(temp_json.encode('utf-8')).hexdigest()[:16]
                
                if signature == expected_signature:
                    return WatermarkData(
                        owner_id=payload_dict['owner_id'],
                        content_id=payload_dict['content_id'],
                        timestamp=payload_dict['timestamp'],
                        metadata=payload_dict['metadata'],
                        signature=signature
                    )
                else:
                    logger.warning("Watermark signature verification failed")
                    return None
                    
            except (json.JSONDecodeError, UnicodeDecodeError, KeyError) as e:
                logger.warning(f"Payload decoding failed: {e}")
                return None
                
        except Exception as e:
            logger.warning(f"Payload decode failed: {e}")
            return None
    
    async def _embed_spectral_spread(
        self,
        audio: np.ndarray,
        sr: int,
        payload: np.ndarray,
        settings: WatermarkSettings
    ) -> np.ndarray:
        """Embed watermark using spectral spread spectrum method"""
        try:
            # Compute STFT
            stft = librosa.stft(audio, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Define frequency range for embedding
            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            freq_mask = (freqs >= settings.frequency_range[0]) & (freqs <= settings.frequency_range[1])
            freq_indices = np.where(freq_mask)[0]
            
            if len(freq_indices) == 0:
                return audio
            
            # Embed payload bits
            watermarked_magnitude = magnitude.copy()
            strength_factor = self._get_strength_factor(settings.strength)
            
            bit_index = 0
            for t in range(magnitude.shape[1]):
                if bit_index >= len(payload):
                    break
                
                # Select frequency bins for this time frame
                for f_idx in freq_indices[::max(1, len(freq_indices) // 32)]:  # Sparse embedding
                    if bit_index >= len(payload):
                        break
                    
                    bit_value = payload[bit_index]
                    
                    # Embed bit by modifying magnitude
                    if bit_value == 1:
                        watermarked_magnitude[f_idx, t] *= (1.0 + strength_factor)
                    else:
                        watermarked_magnitude[f_idx, t] *= (1.0 - strength_factor * 0.5)
                    
                    bit_index += 1
            
            # Reconstruct audio
            watermarked_stft = watermarked_magnitude * np.exp(1j * phase)
            watermarked_audio = librosa.istft(watermarked_stft, hop_length=self.hop_length, length=len(audio))
            
            return watermarked_audio
            
        except Exception as e:
            logger.warning(f"Spectral spread embedding failed: {e}")
            return audio
    
    async def _extract_spectral_spread(
        self,
        audio: np.ndarray,
        sr: int,
        settings: WatermarkSettings
    ) -> Optional[np.ndarray]:
        """Extract watermark using spectral spread spectrum method"""
        try:
            # This is a simplified extraction - in production would need original audio for comparison
            stft = librosa.stft(audio, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            
            # Define frequency range
            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            freq_mask = (freqs >= settings.frequency_range[0]) & (freqs <= settings.frequency_range[1])
            freq_indices = np.where(freq_mask)[0]
            
            if len(freq_indices) == 0:
                return None
            
            # Extract bits (simplified method)
            extracted_bits = []
            
            for t in range(magnitude.shape[1]):
                if len(extracted_bits) >= settings.embedding_capacity:
                    break
                
                for f_idx in freq_indices[::max(1, len(freq_indices) // 32)]:
                    if len(extracted_bits) >= settings.embedding_capacity:
                        break
                    
                    # Simple threshold-based detection
                    mag_value = magnitude[f_idx, t]
                    threshold = np.mean(magnitude[freq_indices, t])
                    
                    bit = 1 if mag_value > threshold else 0
                    extracted_bits.append(bit)
            
            return np.array(extracted_bits, dtype=np.uint8)
            
        except Exception as e:
            logger.warning(f"Spectral spread extraction failed: {e}")
            return None
    
    async def _embed_lsb(
        self,
        audio: np.ndarray,
        sr: int,
        payload: np.ndarray,
        settings: WatermarkSettings
    ) -> np.ndarray:
        """Embed watermark using LSB (Least Significant Bit) method"""
        try:
            # Convert audio to 16-bit integers
            audio_int = (audio * 32767).astype(np.int16)
            watermarked_audio_int = audio_int.copy()
            
            # Embed bits in LSB
            step_size = max(1, len(audio_int) // len(payload))
            
            for i, bit in enumerate(payload):
                sample_idx = i * step_size
                if sample_idx < len(watermarked_audio_int):
                    # Clear LSB and set to bit value
                    watermarked_audio_int[sample_idx] = (watermarked_audio_int[sample_idx] & 0xFFFE) | int(bit)
            
            # Convert back to float
            watermarked_audio = watermarked_audio_int.astype(np.float32) / 32767
            
            return watermarked_audio
            
        except Exception as e:
            logger.warning(f"LSB embedding failed: {e}")
            return audio
    
    async def _extract_lsb(
        self,
        audio: np.ndarray,
        sr: int,
        settings: WatermarkSettings
    ) -> Optional[np.ndarray]:
        """Extract watermark using LSB method"""
        try:
            # Convert audio to 16-bit integers
            audio_int = (audio * 32767).astype(np.int16)
            
            # Extract bits from LSB
            step_size = max(1, len(audio_int) // settings.embedding_capacity)
            extracted_bits = []
            
            for i in range(settings.embedding_capacity):
                sample_idx = i * step_size
                if sample_idx < len(audio_int):
                    bit = audio_int[sample_idx] & 1
                    extracted_bits.append(bit)
            
            return np.array(extracted_bits, dtype=np.uint8)
            
        except Exception as e:
            logger.warning(f"LSB extraction failed: {e}")
            return None
    
    async def _embed_phase_coding(
        self,
        audio: np.ndarray,
        sr: int,
        payload: np.ndarray,
        settings: WatermarkSettings
    ) -> np.ndarray:
        """Embed watermark using phase coding method"""
        try:
            # Compute STFT
            stft = librosa.stft(audio, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Modify phase to embed bits
            watermarked_phase = phase.copy()
            strength_factor = self._get_strength_factor(settings.strength) * np.pi / 4
            
            # Define frequency range
            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            freq_mask = (freqs >= settings.frequency_range[0]) & (freqs <= settings.frequency_range[1])
            freq_indices = np.where(freq_mask)[0]
            
            bit_index = 0
            for t in range(phase.shape[1]):
                if bit_index >= len(payload):
                    break
                
                for f_idx in freq_indices[::max(1, len(freq_indices) // 16)]:
                    if bit_index >= len(payload):
                        break
                    
                    bit_value = payload[bit_index]
                    
                    # Modify phase based on bit value
                    if bit_value == 1:
                        watermarked_phase[f_idx, t] += strength_factor
                    else:
                        watermarked_phase[f_idx, t] -= strength_factor
                    
                    bit_index += 1
            
            # Reconstruct audio
            watermarked_stft = magnitude * np.exp(1j * watermarked_phase)
            watermarked_audio = librosa.istft(watermarked_stft, hop_length=self.hop_length, length=len(audio))
            
            return watermarked_audio
            
        except Exception as e:
            logger.warning(f"Phase coding embedding failed: {e}")
            return audio
    
    async def _extract_phase_coding(
        self,
        audio: np.ndarray,
        sr: int,
        settings: WatermarkSettings
    ) -> Optional[np.ndarray]:
        """Extract watermark using phase coding method"""
        try:
            # This would require the original phase for comparison in a real implementation
            # Simplified extraction for demonstration
            stft = librosa.stft(audio, hop_length=self.hop_length, n_fft=self.n_fft)
            phase = np.angle(stft)
            
            # Define frequency range
            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            freq_mask = (freqs >= settings.frequency_range[0]) & (freqs <= settings.frequency_range[1])
            freq_indices = np.where(freq_mask)[0]
            
            # Extract bits based on phase patterns
            extracted_bits = []
            
            for t in range(phase.shape[1]):
                if len(extracted_bits) >= settings.embedding_capacity:
                    break
                
                for f_idx in freq_indices[::max(1, len(freq_indices) // 16)]:
                    if len(extracted_bits) >= settings.embedding_capacity:
                        break
                    
                    # Simple phase-based detection
                    phase_value = phase[f_idx, t]
                    bit = 1 if phase_value > 0 else 0
                    extracted_bits.append(bit)
            
            return np.array(extracted_bits, dtype=np.uint8)
            
        except Exception as e:
            logger.warning(f"Phase coding extraction failed: {e}")
            return None
    
    async def _embed_echo_hiding(
        self,
        audio: np.ndarray,
        sr: int,
        payload: np.ndarray,
        settings: WatermarkSettings
    ) -> np.ndarray:
        """Embed watermark using echo hiding method"""
        try:
            watermarked_audio = audio.copy()
            
            # Echo parameters
            delay_0 = int(0.001 * sr)  # 1ms delay for bit 0
            delay_1 = int(0.002 * sr)  # 2ms delay for bit 1
            echo_strength = self._get_strength_factor(settings.strength) * 0.1
            
            # Embed bits using echo
            samples_per_bit = len(audio) // len(payload)
            
            for i, bit in enumerate(payload):
                start_idx = i * samples_per_bit
                end_idx = min(start_idx + samples_per_bit, len(audio))
                
                if end_idx - start_idx > max(delay_0, delay_1):
                    delay = delay_1 if bit == 1 else delay_0
                    
                    # Add delayed echo
                    for j in range(start_idx + delay, end_idx):
                        if j - delay >= start_idx:
                            watermarked_audio[j] += echo_strength * audio[j - delay]
            
            return watermarked_audio
            
        except Exception as e:
            logger.warning(f"Echo hiding embedding failed: {e}")
            return audio
    
    async def _extract_echo_hiding(
        self,
        audio: np.ndarray,
        sr: int,
        settings: WatermarkSettings
    ) -> Optional[np.ndarray]:
        """Extract watermark using echo hiding method"""
        try:
            # This would require cepstral analysis or autocorrelation in a real implementation
            # Simplified extraction for demonstration
            delay_0 = int(0.001 * sr)  # 1ms
            delay_1 = int(0.002 * sr)  # 2ms
            
            extracted_bits = []
            samples_per_bit = len(audio) // settings.embedding_capacity
            
            for i in range(settings.embedding_capacity):
                start_idx = i * samples_per_bit
                end_idx = min(start_idx + samples_per_bit, len(audio))
                
                if end_idx - start_idx > max(delay_0, delay_1):
                    # Calculate autocorrelation at both delays
                    segment = audio[start_idx:end_idx]
                    
                    corr_0 = np.corrcoef(segment[:-delay_0], segment[delay_0:])[0, 1] if len(segment) > delay_0 else 0
                    corr_1 = np.corrcoef(segment[:-delay_1], segment[delay_1:])[0, 1] if len(segment) > delay_1 else 0
                    
                    # Choose bit based on stronger correlation
                    bit = 1 if corr_1 > corr_0 else 0
                    extracted_bits.append(bit)
            
            return np.array(extracted_bits, dtype=np.uint8)
            
        except Exception as e:
            logger.warning(f"Echo hiding extraction failed: {e}")
            return None
    
    async def _embed_frequency_masking(
        self,
        audio: np.ndarray,
        sr: int,
        payload: np.ndarray,
        settings: WatermarkSettings
    ) -> np.ndarray:
        """Embed watermark using frequency masking method"""
        try:
            # Similar to spectral spread but uses psychoacoustic masking
            stft = librosa.stft(audio, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Calculate masking threshold (simplified)
            masking_threshold = np.mean(magnitude, axis=1, keepdims=True) * 0.1
            
            # Embed in frequencies below masking threshold
            watermarked_magnitude = magnitude.copy()
            strength_factor = self._get_strength_factor(settings.strength)
            
            # Define frequency range
            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            freq_mask = (freqs >= settings.frequency_range[0]) & (freqs <= settings.frequency_range[1])
            freq_indices = np.where(freq_mask)[0]
            
            bit_index = 0
            for t in range(magnitude.shape[1]):
                if bit_index >= len(payload):
                    break
                
                for f_idx in freq_indices:
                    if bit_index >= len(payload):
                        break
                    
                    # Only embed if below masking threshold
                    if magnitude[f_idx, t] < masking_threshold[f_idx, 0] * 2:
                        bit_value = payload[bit_index]
                        
                        if bit_value == 1:
                            watermarked_magnitude[f_idx, t] += strength_factor * masking_threshold[f_idx, 0]
                        
                        bit_index += 1
            
            # Reconstruct audio
            watermarked_stft = watermarked_magnitude * np.exp(1j * phase)
            watermarked_audio = librosa.istft(watermarked_stft, hop_length=self.hop_length, length=len(audio))
            
            return watermarked_audio
            
        except Exception as e:
            logger.warning(f"Frequency masking embedding failed: {e}")
            return audio
    
    async def _extract_frequency_masking(
        self,
        audio: np.ndarray,
        sr: int,
        settings: WatermarkSettings
    ) -> Optional[np.ndarray]:
        """Extract watermark using frequency masking method"""
        try:
            # Simplified extraction - would need original for proper implementation
            stft = librosa.stft(audio, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            
            # Define frequency range
            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            freq_mask = (freqs >= settings.frequency_range[0]) & (freqs <= settings.frequency_range[1])
            freq_indices = np.where(freq_mask)[0]
            
            extracted_bits = []
            
            for t in range(magnitude.shape[1]):
                if len(extracted_bits) >= settings.embedding_capacity:
                    break
                
                for f_idx in freq_indices:
                    if len(extracted_bits) >= settings.embedding_capacity:
                        break
                    
                    # Simple threshold detection
                    mag_value = magnitude[f_idx, t]
                    threshold = np.mean(magnitude[freq_indices, t]) * 0.5
                    
                    bit = 1 if mag_value > threshold else 0
                    extracted_bits.append(bit)
            
            return np.array(extracted_bits, dtype=np.uint8)
            
        except Exception as e:
            logger.warning(f"Frequency masking extraction failed: {e}")
            return None
    
    def _get_strength_factor(self, strength: WatermarkStrength) -> float:
        """Get numerical strength factor"""
        strength_map = {
            WatermarkStrength.SUBTLE: 0.001,
            WatermarkStrength.MODERATE: 0.005,
            WatermarkStrength.ROBUST: 0.01,
            WatermarkStrength.MAXIMUM: 0.02
        }
        return strength_map.get(strength, 0.005)
    
    async def _calculate_snr(self, original: np.ndarray, watermarked: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio"""
        try:
            noise = watermarked - original
            signal_power = np.mean(original ** 2)
            noise_power = np.mean(noise ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                return float(snr)
            else:
                return float('inf')
                
        except Exception as e:
            logger.warning(f"SNR calculation failed: {e}")
            return 0.0
    
    def _calculate_audio_hash(self, audio: np.ndarray) -> str:
        """Calculate hash of audio data"""
        audio_bytes = audio.astype(np.float32).tobytes()
        return hashlib.sha256(audio_bytes).hexdigest()[:16]