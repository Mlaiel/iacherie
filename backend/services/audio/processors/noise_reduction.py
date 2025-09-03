"""🧹 Noise Reduction - Advanced Audio Cleaning Engine

Sophisticated noise reduction and audio cleaning system for
professional audio enhancement and restoration.

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
import soundfile as sf
from scipy import signal
from scipy.ndimage import median_filter
# Optional noisereduce import
try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    nr = None
    NOISEREDUCE_AVAILABLE = False
from pathlib import Path

# Import from existing audio processing modules
try:
    from ....ai_engine.audio_processing.core import AudioProcessor
    from ....ai_engine.audio_processing.effects import EffectsProcessor
except ImportError:
    # Fallback if imports fail
    AudioProcessor = None
    EffectsProcessor = None

logger = logging.getLogger(__name__)


class NoiseType(Enum):
    """Types of noise that can be reduced"""
    BACKGROUND = "background"
    WIND = "wind"
    HISS = "hiss"
    HUM = "hum"
    CLICK = "click"
    CRACKLE = "crackle"
    RUMBLE = "rumble"
    BROADBAND = "broadband"
    TONAL = "tonal"


class ReductionLevel(Enum):
    """Noise reduction intensity levels"""
    LIGHT = "light"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    PRESERVE_QUALITY = "preserve_quality"


@dataclass
class NoiseReductionSettings:
    """Noise reduction configuration"""
    noise_type: NoiseType = NoiseType.BACKGROUND
    reduction_level: ReductionLevel = ReductionLevel.MODERATE
    preserve_speech: bool = True
    preserve_music: bool = True
    spectral_subtraction_factor: float = 2.0
    gate_threshold: float = 0.02
    smoothing_factor: float = 0.8


@dataclass
class NoiseReductionResult:
    """Noise reduction processing result"""
    cleaned_audio: np.ndarray
    original_noise_level: float
    final_noise_level: float
    noise_reduction_db: float
    processing_time: float
    settings_used: NoiseReductionSettings
    metadata: Dict[str, Any]


class NoiseReducer:
    """
    Advanced noise reduction and audio cleaning system.
    
    Provides multiple noise reduction algorithms optimized for different
    types of noise and audio content (speech, music, etc.).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the noise reducer.
        
        Args:
            config: Configuration dictionary for noise reduction parameters
        """
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 22050)
        self.hop_length = self.config.get('hop_length', 512)
        self.n_fft = self.config.get('n_fft', 2048)
        
        # Default settings
        self.default_settings = NoiseReductionSettings()
        
        logger.info("NoiseReducer initialized successfully")
    
    async def reduce_noise(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        settings: Optional[NoiseReductionSettings] = None,
        noise_sample: Optional[np.ndarray] = None
    ) -> NoiseReductionResult:
        """
        Perform noise reduction on audio data.
        
        Args:
            audio_data: Audio data to clean
            settings: Noise reduction settings
            noise_sample: Optional noise sample for better reduction
            
        Returns:
            NoiseReductionResult: Cleaned audio and processing information
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Load audio data
            audio_array, sr = self._load_audio(audio_data)
            settings = settings or self.default_settings
            
            # Analyze noise characteristics
            noise_profile = await self._analyze_noise(audio_array, sr, noise_sample)
            
            # Apply appropriate noise reduction algorithm
            cleaned_audio = await self._apply_noise_reduction(
                audio_array, sr, settings, noise_profile
            )
            
            # Calculate noise levels
            original_noise_level = await self._calculate_noise_level(audio_array, sr)
            final_noise_level = await self._calculate_noise_level(cleaned_audio, sr)
            noise_reduction_db = 20 * np.log10(original_noise_level / (final_noise_level + 1e-10))
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Create result
            result = NoiseReductionResult(
                cleaned_audio=cleaned_audio,
                original_noise_level=original_noise_level,
                final_noise_level=final_noise_level,
                noise_reduction_db=noise_reduction_db,
                processing_time=processing_time,
                settings_used=settings,
                metadata={
                    'original_duration': len(audio_array) / sr,
                    'sample_rate': sr,
                    'algorithm_version': '1.0',
                    'noise_type_detected': noise_profile.get('type', 'unknown')
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {e}")
            # Return original audio on failure
            processing_time = asyncio.get_event_loop().time() - start_time
            audio_array, sr = self._load_audio(audio_data)
            
            return NoiseReductionResult(
                cleaned_audio=audio_array,
                original_noise_level=0.0,
                final_noise_level=0.0,
                noise_reduction_db=0.0,
                processing_time=processing_time,
                settings_used=settings or self.default_settings,
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
    
    async def _analyze_noise(
        self,
        audio: np.ndarray,
        sr: int,
        noise_sample: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Analyze noise characteristics in the audio"""
        try:
            # Use provided noise sample or estimate from audio
            if noise_sample is not None:
                noise_profile = noise_sample
            else:
                # Estimate noise from quiet sections
                noise_profile = await self._estimate_noise_profile(audio, sr)
            
            # Analyze noise characteristics
            stft_noise = librosa.stft(noise_profile, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude_noise = np.abs(stft_noise)
            
            # Calculate noise statistics
            noise_mean = np.mean(magnitude_noise, axis=1)
            noise_std = np.std(magnitude_noise, axis=1)
            
            # Detect noise type based on spectral characteristics
            noise_type = await self._detect_noise_type(magnitude_noise, sr)
            
            return {
                'type': noise_type,
                'profile': noise_profile,
                'spectral_mean': noise_mean,
                'spectral_std': noise_std,
                'magnitude_spectrum': magnitude_noise
            }
            
        except Exception as e:
            logger.warning(f"Noise analysis failed: {e}")
            return {'type': NoiseType.BACKGROUND, 'profile': np.zeros(1024)}
    
    async def _estimate_noise_profile(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Estimate noise profile from quiet sections of audio"""
        try:
            # Calculate energy in overlapping windows
            window_size = int(0.1 * sr)  # 100ms windows
            hop_size = window_size // 2
            
            energies = []
            windows = []
            
            for i in range(0, len(audio) - window_size, hop_size):
                window = audio[i:i + window_size]
                energy = np.mean(window ** 2)
                energies.append(energy)
                windows.append(window)
            
            # Find quietest sections (bottom 20%)
            energies = np.array(energies)
            quiet_threshold = np.percentile(energies, 20)
            quiet_indices = np.where(energies <= quiet_threshold)[0]
            
            if len(quiet_indices) > 0:
                # Concatenate quiet sections
                quiet_audio = np.concatenate([windows[i] for i in quiet_indices])
                return quiet_audio[:min(len(quiet_audio), int(0.5 * sr))]  # Max 0.5 seconds
            else:
                # Fallback: use first 0.1 seconds
                return audio[:int(0.1 * sr)]
                
        except Exception as e:
            logger.warning(f"Noise profile estimation failed: {e}")
            return audio[:int(0.1 * sr)]
    
    async def _detect_noise_type(self, magnitude_spectrum: np.ndarray, sr: int) -> NoiseType:
        """Detect the type of noise based on spectral characteristics"""
        try:
            # Calculate spectral features
            mean_spectrum = np.mean(magnitude_spectrum, axis=1)
            spectral_centroid = np.sum(mean_spectrum * np.arange(len(mean_spectrum))) / np.sum(mean_spectrum)
            spectral_rolloff = np.percentile(mean_spectrum, 85)
            
            # Simple heuristics for noise type detection
            if spectral_centroid < len(mean_spectrum) * 0.1:
                return NoiseType.RUMBLE
            elif spectral_centroid > len(mean_spectrum) * 0.8:
                return NoiseType.HISS
            elif np.std(mean_spectrum) / np.mean(mean_spectrum) < 0.3:
                return NoiseType.HUM
            else:
                return NoiseType.BACKGROUND
                
        except Exception as e:
            logger.warning(f"Noise type detection failed: {e}")
            return NoiseType.BACKGROUND
    
    async def _apply_noise_reduction(
        self,
        audio: np.ndarray,
        sr: int,
        settings: NoiseReductionSettings,
        noise_profile: Dict[str, Any]
    ) -> np.ndarray:
        """Apply noise reduction algorithm"""
        try:
            cleaned_audio = audio.copy()
            
            # Apply different algorithms based on noise type and settings
            if settings.noise_type in [NoiseType.BACKGROUND, NoiseType.BROADBAND]:
                cleaned_audio = await self._spectral_subtraction(
                    cleaned_audio, sr, settings, noise_profile
                )
            
            if settings.noise_type in [NoiseType.HUM, NoiseType.TONAL]:
                cleaned_audio = await self._notch_filter(
                    cleaned_audio, sr, settings
                )
            
            if settings.noise_type in [NoiseType.CLICK, NoiseType.CRACKLE]:
                cleaned_audio = await self._impulse_noise_reduction(
                    cleaned_audio, sr, settings
                )
            
            if settings.noise_type == NoiseType.WIND:
                cleaned_audio = await self._wind_noise_reduction(
                    cleaned_audio, sr, settings
                )
            
            if settings.noise_type == NoiseType.RUMBLE:
                cleaned_audio = await self._high_pass_filter(
                    cleaned_audio, sr, settings
                )
            
            # Apply noise gate if needed
            if settings.gate_threshold > 0:
                cleaned_audio = await self._noise_gate(
                    cleaned_audio, sr, settings.gate_threshold
                )
            
            # Apply smoothing
            if settings.smoothing_factor > 0:
                cleaned_audio = await self._apply_smoothing(
                    cleaned_audio, settings.smoothing_factor
                )
            
            return cleaned_audio
            
        except Exception as e:
            logger.warning(f"Noise reduction application failed: {e}")
            return audio
    
    async def _spectral_subtraction(
        self,
        audio: np.ndarray,
        sr: int,
        settings: NoiseReductionSettings,
        noise_profile: Dict[str, Any]
    ) -> np.ndarray:
        """Apply spectral subtraction noise reduction"""
        try:
            # Compute STFT
            stft = librosa.stft(audio, hop_length=self.hop_length, n_fft=self.n_fft)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Get noise magnitude spectrum
            noise_magnitude = noise_profile.get('spectral_mean', np.mean(magnitude, axis=1))
            
            # Ensure noise_magnitude has correct shape
            if len(noise_magnitude) != magnitude.shape[0]:
                noise_magnitude = np.interp(
                    np.arange(magnitude.shape[0]),
                    np.arange(len(noise_magnitude)),
                    noise_magnitude
                )
            
            # Apply spectral subtraction
            alpha = settings.spectral_subtraction_factor
            
            # Broadcast noise_magnitude for subtraction
            noise_magnitude_broadcast = noise_magnitude[:, np.newaxis]
            
            # Spectral subtraction with over-subtraction factor
            magnitude_cleaned = magnitude - alpha * noise_magnitude_broadcast
            
            # Apply reduction level scaling
            if settings.reduction_level == ReductionLevel.LIGHT:
                magnitude_cleaned = 0.8 * magnitude + 0.2 * magnitude_cleaned
            elif settings.reduction_level == ReductionLevel.MODERATE:
                magnitude_cleaned = 0.5 * magnitude + 0.5 * magnitude_cleaned
            elif settings.reduction_level == ReductionLevel.PRESERVE_QUALITY:
                magnitude_cleaned = 0.7 * magnitude + 0.3 * magnitude_cleaned
            
            # Ensure magnitude doesn't go below a minimum (to avoid artifacts)
            magnitude_cleaned = np.maximum(magnitude_cleaned, 0.1 * magnitude)
            
            # Reconstruct audio
            stft_cleaned = magnitude_cleaned * np.exp(1j * phase)
            audio_cleaned = librosa.istft(
                stft_cleaned, 
                hop_length=self.hop_length, 
                length=len(audio)
            )
            
            return audio_cleaned
            
        except Exception as e:
            logger.warning(f"Spectral subtraction failed: {e}")
            return audio
    
    async def _notch_filter(
        self,
        audio: np.ndarray,
        sr: int,
        settings: NoiseReductionSettings
    ) -> np.ndarray:
        """Apply notch filter for tonal noise (hum, etc.)"""
        try:
            # Common hum frequencies
            hum_frequencies = [50, 60, 100, 120]  # Hz
            
            cleaned_audio = audio.copy()
            
            for freq in hum_frequencies:
                if freq < sr / 2:  # Nyquist limit
                    # Design notch filter
                    nyquist = sr / 2
                    low = (freq - 2) / nyquist
                    high = (freq + 2) / nyquist
                    
                    # Ensure valid frequency range
                    low = max(0.001, low)
                    high = min(0.999, high)
                    
                    if low < high:
                        b, a = signal.butter(2, [low, high], btype='bandstop')
                        cleaned_audio = signal.filtfilt(b, a, cleaned_audio)
            
            return cleaned_audio
            
        except Exception as e:
            logger.warning(f"Notch filter failed: {e}")
            return audio
    
    async def _impulse_noise_reduction(
        self,
        audio: np.ndarray,
        sr: int,
        settings: NoiseReductionSettings
    ) -> np.ndarray:
        """Reduce impulse noise (clicks, pops)"""
        try:
            # Detect impulses using median filter
            median_filtered = median_filter(audio, size=5)
            impulse_mask = np.abs(audio - median_filtered) > 0.1 * np.std(audio)
            
            # Replace impulses with interpolated values
            cleaned_audio = audio.copy()
            cleaned_audio[impulse_mask] = median_filtered[impulse_mask]
            
            return cleaned_audio
            
        except Exception as e:
            logger.warning(f"Impulse noise reduction failed: {e}")
            return audio
    
    async def _wind_noise_reduction(
        self,
        audio: np.ndarray,
        sr: int,
        settings: NoiseReductionSettings
    ) -> np.ndarray:
        """Reduce wind noise"""
        try:
            # Wind noise is typically low-frequency
            # Apply high-pass filter
            nyquist = sr / 2
            cutoff = 200 / nyquist  # 200 Hz cutoff
            
            b, a = signal.butter(4, cutoff, btype='high')
            cleaned_audio = signal.filtfilt(b, a, audio)
            
            return cleaned_audio
            
        except Exception as e:
            logger.warning(f"Wind noise reduction failed: {e}")
            return audio
    
    async def _high_pass_filter(
        self,
        audio: np.ndarray,
        sr: int,
        settings: NoiseReductionSettings
    ) -> np.ndarray:
        """Apply high-pass filter for rumble reduction"""
        try:
            nyquist = sr / 2
            cutoff = 80 / nyquist  # 80 Hz cutoff for rumble
            
            b, a = signal.butter(4, cutoff, btype='high')
            cleaned_audio = signal.filtfilt(b, a, audio)
            
            return cleaned_audio
            
        except Exception as e:
            logger.warning(f"High-pass filter failed: {e}")
            return audio
    
    async def _noise_gate(
        self,
        audio: np.ndarray,
        sr: int,
        threshold: float
    ) -> np.ndarray:
        """Apply noise gate to reduce quiet noise"""
        try:
            # Calculate RMS in windows
            window_size = int(0.01 * sr)  # 10ms windows
            hop_size = window_size // 2
            
            gated_audio = audio.copy()
            
            for i in range(0, len(audio) - window_size, hop_size):
                window = audio[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                
                if rms < threshold:
                    # Reduce gain in quiet sections
                    gated_audio[i:i + window_size] *= 0.1
            
            return gated_audio
            
        except Exception as e:
            logger.warning(f"Noise gate failed: {e}")
            return audio
    
    async def _apply_smoothing(
        self,
        audio: np.ndarray,
        smoothing_factor: float
    ) -> np.ndarray:
        """Apply smoothing to reduce processing artifacts"""
        try:
            # Simple moving average smoothing
            kernel_size = max(3, int(smoothing_factor * 10))
            kernel = np.ones(kernel_size) / kernel_size
            
            # Pad audio for convolution
            padded_audio = np.pad(audio, (kernel_size // 2, kernel_size // 2), mode='edge')
            smoothed_audio = np.convolve(padded_audio, kernel, mode='valid')
            
            return smoothed_audio[:len(audio)]
            
        except Exception as e:
            logger.warning(f"Smoothing failed: {e}")
            return audio
    
    async def _calculate_noise_level(self, audio: np.ndarray, sr: int) -> float:
        """Calculate overall noise level in audio"""
        try:
            # Use RMS of quiet sections as noise level estimate
            window_size = int(0.1 * sr)
            hop_size = window_size // 2
            
            energies = []
            
            for i in range(0, len(audio) - window_size, hop_size):
                window = audio[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                energies.append(rms)
            
            # Use 10th percentile as noise level
            if energies:
                return float(np.percentile(energies, 10))
            else:
                return float(np.sqrt(np.mean(audio ** 2)))
                
        except Exception as e:
            logger.warning(f"Noise level calculation failed: {e}")
            return 0.0