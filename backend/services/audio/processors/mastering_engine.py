"""🎚️ Mastering Engine - Automated Audio Mastering System

Professional automated mastering system for optimal audio quality,
loudness normalization, and dynamic range optimization.

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
from pathlib import Path

logger = logging.getLogger(__name__)


class MasteringStyle(Enum):
    """Mastering style presets"""
    TRANSPARENT = "transparent"
    WARM = "warm"
    MODERN = "modern"
    VINTAGE = "vintage"
    AGGRESSIVE = "aggressive"
    BROADCAST = "broadcast"
    STREAMING = "streaming"


class MasteringTarget(Enum):
    """Target platform/format for mastering"""
    CD = "cd"
    STREAMING = "streaming"
    VINYL = "vinyl"
    RADIO = "radio"
    PODCAST = "podcast"
    CUSTOM = "custom"


@dataclass
class MasteringSettings:
    """Mastering configuration settings"""
    style: MasteringStyle = MasteringStyle.MODERN
    target: MasteringTarget = MasteringTarget.STREAMING
    target_lufs: float = -14.0  # Loudness Units Full Scale
    target_peak: float = -1.0   # Peak level in dB
    dynamic_range_target: float = 8.0  # DR target
    stereo_width: float = 1.0   # Stereo width factor
    bass_enhancement: float = 0.0  # Bass boost in dB
    presence_boost: float = 0.0    # Presence boost in dB
    use_limiting: bool = True
    use_compression: bool = True
    use_eq: bool = True
    use_stereo_enhancement: bool = False


@dataclass
class MasteringResult:
    """Mastering processing result"""
    mastered_audio: np.ndarray
    original_lufs: float
    final_lufs: float
    original_peak: float
    final_peak: float
    dynamic_range: float
    processing_chain: List[str]
    processing_time: float
    settings_used: MasteringSettings
    metadata: Dict[str, Any]


class MasteringEngine:
    """
    Professional automated mastering system.
    
    Provides comprehensive audio mastering with EQ, compression,
    limiting, and loudness optimization for various target platforms.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the mastering engine.
        
        Args:
            config: Configuration dictionary for mastering parameters
        """
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 44100)
        
        # Mastering presets
        self.presets = self._initialize_presets()
        
        logger.info("MasteringEngine initialized successfully")
    
    def _initialize_presets(self) -> Dict[MasteringTarget, MasteringSettings]:
        """Initialize mastering presets for different targets"""
        return {
            MasteringTarget.STREAMING: MasteringSettings(
                style=MasteringStyle.MODERN,
                target=MasteringTarget.STREAMING,
                target_lufs=-14.0,
                target_peak=-1.0,
                dynamic_range_target=8.0,
                use_limiting=True,
                use_compression=True,
                use_eq=True
            ),
            MasteringTarget.CD: MasteringSettings(
                style=MasteringStyle.TRANSPARENT,
                target=MasteringTarget.CD,
                target_lufs=-12.0,
                target_peak=-0.1,
                dynamic_range_target=10.0,
                use_limiting=True,
                use_compression=False,
                use_eq=True
            ),
            MasteringTarget.RADIO: MasteringSettings(
                style=MasteringStyle.AGGRESSIVE,
                target=MasteringTarget.RADIO,
                target_lufs=-16.0,
                target_peak=-1.0,
                dynamic_range_target=6.0,
                use_limiting=True,
                use_compression=True,
                use_eq=True,
                presence_boost=2.0
            ),
            MasteringTarget.PODCAST: MasteringSettings(
                style=MasteringStyle.BROADCAST,
                target=MasteringTarget.PODCAST,
                target_lufs=-18.0,
                target_peak=-3.0,
                dynamic_range_target=12.0,
                use_limiting=True,
                use_compression=True,
                use_eq=True
            )
        }
    
    async def master_audio(
        self,
        audio_data: Union[np.ndarray, bytes, str, Path],
        settings: Optional[MasteringSettings] = None,
        target: Optional[MasteringTarget] = None
    ) -> MasteringResult:
        """
        Perform automated mastering on audio data.
        
        Args:
            audio_data: Audio data to master
            settings: Custom mastering settings
            target: Target platform (overrides settings if provided)
            
        Returns:
            MasteringResult: Mastered audio and processing information
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Load audio data
            audio_array, sr = self._load_audio(audio_data)
            
            # Determine settings
            if target:
                settings = self.presets.get(target, self.presets[MasteringTarget.STREAMING])
            elif settings is None:
                settings = self.presets[MasteringTarget.STREAMING]
            
            # Analyze original audio
            original_lufs = await self._calculate_lufs(audio_array, sr)
            original_peak = await self._calculate_peak(audio_array)
            
            # Initialize processing chain
            processing_chain = []
            mastered_audio = audio_array.copy()
            
            # Apply mastering chain
            if settings.use_eq:
                mastered_audio = await self._apply_eq(mastered_audio, sr, settings)
                processing_chain.append("EQ")
            
            if settings.use_compression:
                mastered_audio = await self._apply_compression(mastered_audio, sr, settings)
                processing_chain.append("Compression")
            
            if settings.use_stereo_enhancement:
                mastered_audio = await self._apply_stereo_enhancement(mastered_audio, settings)
                processing_chain.append("Stereo Enhancement")
            
            # Loudness normalization
            mastered_audio = await self._normalize_loudness(mastered_audio, sr, settings)
            processing_chain.append("Loudness Normalization")
            
            if settings.use_limiting:
                mastered_audio = await self._apply_limiting(mastered_audio, sr, settings)
                processing_chain.append("Limiting")
            
            # Final analysis
            final_lufs = await self._calculate_lufs(mastered_audio, sr)
            final_peak = await self._calculate_peak(mastered_audio)
            dynamic_range = await self._calculate_dynamic_range(mastered_audio, sr)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Create result
            result = MasteringResult(
                mastered_audio=mastered_audio,
                original_lufs=original_lufs,
                final_lufs=final_lufs,
                original_peak=original_peak,
                final_peak=final_peak,
                dynamic_range=dynamic_range,
                processing_chain=processing_chain,
                processing_time=processing_time,
                settings_used=settings,
                metadata={
                    'original_duration': len(audio_array) / sr,
                    'sample_rate': sr,
                    'channels': 1 if audio_array.ndim == 1 else 2,
                    'algorithm_version': '1.0'
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Audio mastering failed: {e}")
            # Return original audio on failure
            processing_time = asyncio.get_event_loop().time() - start_time
            audio_array, sr = self._load_audio(audio_data)
            
            return MasteringResult(
                mastered_audio=audio_array,
                original_lufs=0.0,
                final_lufs=0.0,
                original_peak=0.0,
                final_peak=0.0,
                dynamic_range=0.0,
                processing_chain=[],
                processing_time=processing_time,
                settings_used=settings or MasteringSettings(),
                metadata={'error': str(e)}
            )
    
    def _load_audio(self, audio_data: Union[np.ndarray, bytes, str, Path]) -> Tuple[np.ndarray, int]:
        """Load audio data into numpy array"""
        if isinstance(audio_data, np.ndarray):
            return audio_data, self.sample_rate
        elif isinstance(audio_data, (str, Path)):
            audio_array, sr = librosa.load(str(audio_data), sr=self.sample_rate, mono=False)
            return audio_array, sr
        elif isinstance(audio_data, bytes):
            # Convert bytes to numpy array (simplified)
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            return audio_array, self.sample_rate
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
    
    async def _apply_eq(
        self,
        audio: np.ndarray,
        sr: int,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Apply EQ based on mastering style"""
        try:
            if audio.ndim == 1:
                return await self._apply_eq_mono(audio, sr, settings)
            else:
                # Process stereo channels
                left = await self._apply_eq_mono(audio[0], sr, settings)
                right = await self._apply_eq_mono(audio[1], sr, settings)
                return np.array([left, right])
                
        except Exception as e:
            logger.warning(f"EQ application failed: {e}")
            return audio
    
    async def _apply_eq_mono(
        self,
        audio: np.ndarray,
        sr: int,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Apply EQ to mono audio"""
        try:
            eq_audio = audio.copy()
            
            # Bass enhancement
            if settings.bass_enhancement != 0:
                eq_audio = await self._apply_bass_shelf(eq_audio, sr, settings.bass_enhancement)
            
            # Presence boost
            if settings.presence_boost != 0:
                eq_audio = await self._apply_presence_boost(eq_audio, sr, settings.presence_boost)
            
            # Style-specific EQ
            if settings.style == MasteringStyle.WARM:
                eq_audio = await self._apply_warm_eq(eq_audio, sr)
            elif settings.style == MasteringStyle.MODERN:
                eq_audio = await self._apply_modern_eq(eq_audio, sr)
            elif settings.style == MasteringStyle.VINTAGE:
                eq_audio = await self._apply_vintage_eq(eq_audio, sr)
            elif settings.style == MasteringStyle.AGGRESSIVE:
                eq_audio = await self._apply_aggressive_eq(eq_audio, sr)
            
            return eq_audio
            
        except Exception as e:
            logger.warning(f"Mono EQ failed: {e}")
            return audio
    
    async def _apply_bass_shelf(self, audio: np.ndarray, sr: int, gain_db: float) -> np.ndarray:
        """Apply bass shelf filter"""
        try:
            # Design low shelf filter
            freq = 100  # 100 Hz
            gain = 10 ** (gain_db / 20)
            
            # Simple implementation - would use more sophisticated filter in production
            nyquist = sr / 2
            normalized_freq = freq / nyquist
            
            # Create filter coefficients
            b, a = signal.butter(2, normalized_freq, btype='low')
            
            # Apply filter with gain
            filtered = signal.filtfilt(b, a, audio)
            return audio + (gain - 1) * filtered
            
        except Exception as e:
            logger.warning(f"Bass shelf failed: {e}")
            return audio
    
    async def _apply_presence_boost(self, audio: np.ndarray, sr: int, gain_db: float) -> np.ndarray:
        """Apply presence boost around 3-5 kHz"""
        try:
            # Design bell filter for presence
            center_freq = 4000  # 4 kHz
            q_factor = 2.0
            gain = 10 ** (gain_db / 20)
            
            nyquist = sr / 2
            normalized_freq = center_freq / nyquist
            
            if normalized_freq < 1.0:
                # Create bandpass filter
                low = max(0.001, (center_freq - 500) / nyquist)
                high = min(0.999, (center_freq + 500) / nyquist)
                
                b, a = signal.butter(2, [low, high], btype='band')
                filtered = signal.filtfilt(b, a, audio)
                return audio + (gain - 1) * filtered
            
            return audio
            
        except Exception as e:
            logger.warning(f"Presence boost failed: {e}")
            return audio
    
    async def _apply_warm_eq(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply warm mastering EQ curve"""
        try:
            # Gentle bass boost and slight high-frequency roll-off
            warm_audio = audio.copy()
            
            # Boost around 100-200 Hz
            warm_audio = await self._apply_bass_shelf(warm_audio, sr, 1.5)
            
            # Slight high-frequency roll-off above 10 kHz
            nyquist = sr / 2
            cutoff = min(0.8, 10000 / nyquist)
            
            b, a = signal.butter(2, cutoff, btype='low')
            filtered_highs = signal.filtfilt(b, a, audio)
            
            # Blend original and filtered
            warm_audio = 0.7 * warm_audio + 0.3 * filtered_highs
            
            return warm_audio
            
        except Exception as e:
            logger.warning(f"Warm EQ failed: {e}")
            return audio
    
    async def _apply_modern_eq(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply modern mastering EQ curve"""
        try:
            # Enhanced clarity and punch
            modern_audio = audio.copy()
            
            # Slight presence boost
            modern_audio = await self._apply_presence_boost(modern_audio, sr, 1.0)
            
            # Air enhancement above 10 kHz
            nyquist = sr / 2
            if 10000 / nyquist < 1.0:
                b, a = signal.butter(2, 10000 / nyquist, btype='high')
                air = signal.filtfilt(b, a, audio)
                modern_audio = modern_audio + 0.1 * air
            
            return modern_audio
            
        except Exception as e:
            logger.warning(f"Modern EQ failed: {e}")
            return audio
    
    async def _apply_vintage_eq(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply vintage mastering EQ curve"""
        try:
            # Classic analog-style curve
            vintage_audio = audio.copy()
            
            # Gentle bass warmth
            vintage_audio = await self._apply_bass_shelf(vintage_audio, sr, 2.0)
            
            # Smooth high-frequency roll-off
            nyquist = sr / 2
            cutoff = min(0.75, 8000 / nyquist)
            
            b, a = signal.butter(1, cutoff, btype='low')
            vintage_audio = signal.filtfilt(b, a, vintage_audio)
            
            return vintage_audio
            
        except Exception as e:
            logger.warning(f"Vintage EQ failed: {e}")
            return audio
    
    async def _apply_aggressive_eq(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply aggressive mastering EQ curve"""
        try:
            # Enhanced punch and clarity
            aggressive_audio = audio.copy()
            
            # Strong presence boost
            aggressive_audio = await self._apply_presence_boost(aggressive_audio, sr, 2.5)
            
            # Bass tightening (slight cut around 50-80 Hz)
            nyquist = sr / 2
            low = max(0.001, 50 / nyquist)
            high = min(0.999, 80 / nyquist)
            
            if low < high:
                b, a = signal.butter(2, [low, high], btype='bandstop')
                bass_cut = signal.filtfilt(b, a, audio)
                aggressive_audio = 0.8 * aggressive_audio + 0.2 * bass_cut
            
            return aggressive_audio
            
        except Exception as e:
            logger.warning(f"Aggressive EQ failed: {e}")
            return audio
    
    async def _apply_compression(
        self,
        audio: np.ndarray,
        sr: int,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            if audio.ndim == 1:
                return await self._compress_mono(audio, sr, settings)
            else:
                # Process stereo channels with linked compression
                stereo_compressed = await self._compress_stereo(audio, sr, settings)
                return stereo_compressed
                
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return audio
    
    async def _compress_mono(
        self,
        audio: np.ndarray,
        sr: int,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Apply compression to mono audio"""
        try:
            # Compression parameters based on style
            if settings.style == MasteringStyle.AGGRESSIVE:
                threshold = 0.3
                ratio = 4.0
                attack_time = 0.003  # 3ms
                release_time = 0.1   # 100ms
            elif settings.style == MasteringStyle.BROADCAST:
                threshold = 0.4
                ratio = 3.0
                attack_time = 0.005
                release_time = 0.2
            else:
                threshold = 0.5
                ratio = 2.5
                attack_time = 0.01
                release_time = 0.3
            
            # Simple compression implementation
            compressed = audio.copy()
            envelope = np.abs(audio)
            
            # Smooth envelope
            attack_samples = int(attack_time * sr)
            release_samples = int(release_time * sr)
            
            gain_reduction = np.ones_like(envelope)
            
            for i in range(1, len(envelope)):
                if envelope[i] > threshold:
                    # Calculate required gain reduction
                    overshoot = envelope[i] / threshold
                    target_gain = 1.0 / (1.0 + (overshoot - 1.0) * (ratio - 1.0) / ratio)
                    
                    # Apply attack/release smoothing
                    if gain_reduction[i-1] > target_gain:
                        # Attack
                        gain_reduction[i] = target_gain + (gain_reduction[i-1] - target_gain) * np.exp(-1.0 / attack_samples)
                    else:
                        # Release
                        gain_reduction[i] = target_gain + (gain_reduction[i-1] - target_gain) * np.exp(-1.0 / release_samples)
                else:
                    # Release towards 1.0
                    gain_reduction[i] = 1.0 + (gain_reduction[i-1] - 1.0) * np.exp(-1.0 / release_samples)
            
            compressed = audio * gain_reduction
            
            return compressed
            
        except Exception as e:
            logger.warning(f"Mono compression failed: {e}")
            return audio
    
    async def _compress_stereo(
        self,
        audio: np.ndarray,
        sr: int,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Apply stereo-linked compression"""
        try:
            # Use max of both channels for detection
            left, right = audio[0], audio[1]
            detection_signal = np.maximum(np.abs(left), np.abs(right))
            
            # Apply compression based on detection signal
            compressed_left = await self._apply_compression_with_sidechain(left, detection_signal, sr, settings)
            compressed_right = await self._apply_compression_with_sidechain(right, detection_signal, sr, settings)
            
            return np.array([compressed_left, compressed_right])
            
        except Exception as e:
            logger.warning(f"Stereo compression failed: {e}")
            return audio
    
    async def _apply_compression_with_sidechain(
        self,
        audio: np.ndarray,
        sidechain: np.ndarray,
        sr: int,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Apply compression using sidechain signal for detection"""
        try:
            # Simplified compression with sidechain
            threshold = 0.5
            ratio = 2.5
            
            gain_reduction = np.ones_like(audio)
            
            for i in range(len(sidechain)):
                if sidechain[i] > threshold:
                    overshoot = sidechain[i] / threshold
                    gain_reduction[i] = 1.0 / (1.0 + (overshoot - 1.0) * (ratio - 1.0) / ratio)
            
            return audio * gain_reduction
            
        except Exception as e:
            logger.warning(f"Sidechain compression failed: {e}")
            return audio
    
    async def _apply_stereo_enhancement(
        self,
        audio: np.ndarray,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Apply stereo width enhancement"""
        try:
            if audio.ndim == 1:
                return audio  # No stereo enhancement for mono
            
            left, right = audio[0], audio[1]
            
            # M/S processing
            mid = (left + right) / 2
            side = (left - right) / 2
            
            # Enhance side signal
            enhanced_side = side * settings.stereo_width
            
            # Convert back to L/R
            enhanced_left = mid + enhanced_side
            enhanced_right = mid - enhanced_side
            
            return np.array([enhanced_left, enhanced_right])
            
        except Exception as e:
            logger.warning(f"Stereo enhancement failed: {e}")
            return audio
    
    async def _normalize_loudness(
        self,
        audio: np.ndarray,
        sr: int,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Normalize audio to target LUFS"""
        try:
            current_lufs = await self._calculate_lufs(audio, sr)
            
            if current_lufs != 0:
                # Calculate required gain
                gain_db = settings.target_lufs - current_lufs
                gain_linear = 10 ** (gain_db / 20)
                
                # Apply gain
                normalized = audio * gain_linear
                return normalized
            
            return audio
            
        except Exception as e:
            logger.warning(f"Loudness normalization failed: {e}")
            return audio
    
    async def _apply_limiting(
        self,
        audio: np.ndarray,
        sr: int,
        settings: MasteringSettings
    ) -> np.ndarray:
        """Apply peak limiting"""
        try:
            target_peak_linear = 10 ** (settings.target_peak / 20)
            
            # Simple hard limiting
            limited = np.clip(audio, -target_peak_linear, target_peak_linear)
            
            # Soft limiting for more natural sound
            over_threshold = np.abs(audio) > target_peak_linear
            soft_limited = audio.copy()
            
            # Apply soft compression to peaks
            soft_limited[over_threshold] = np.sign(audio[over_threshold]) * (
                target_peak_linear + (np.abs(audio[over_threshold]) - target_peak_linear) * 0.1
            )
            
            return soft_limited
            
        except Exception as e:
            logger.warning(f"Limiting failed: {e}")
            return audio
    
    async def _calculate_lufs(self, audio: np.ndarray, sr: int) -> float:
        """Calculate integrated loudness in LUFS"""
        try:
            # Simplified LUFS calculation
            # In production, would use proper ITU-R BS.1770 implementation
            
            if audio.ndim == 1:
                # Mono
                rms = np.sqrt(np.mean(audio ** 2))
            else:
                # Stereo
                left_rms = np.sqrt(np.mean(audio[0] ** 2))
                right_rms = np.sqrt(np.mean(audio[1] ** 2))
                rms = np.sqrt((left_rms ** 2 + right_rms ** 2) / 2)
            
            if rms > 0:
                lufs = -0.691 + 10 * np.log10(rms ** 2)
                return float(lufs)
            else:
                return -80.0  # Very quiet
                
        except Exception as e:
            logger.warning(f"LUFS calculation failed: {e}")
            return -23.0  # Default value
    
    async def _calculate_peak(self, audio: np.ndarray) -> float:
        """Calculate peak level in dB"""
        try:
            peak_linear = np.max(np.abs(audio))
            if peak_linear > 0:
                peak_db = 20 * np.log10(peak_linear)
                return float(peak_db)
            else:
                return -80.0
                
        except Exception as e:
            logger.warning(f"Peak calculation failed: {e}")
            return 0.0
    
    async def _calculate_dynamic_range(self, audio: np.ndarray, sr: int) -> float:
        """Calculate dynamic range"""
        try:
            # Calculate RMS in windows
            window_size = int(0.3 * sr)  # 300ms windows
            hop_size = window_size // 2
            
            rms_values = []
            
            for i in range(0, len(audio) - window_size, hop_size):
                if audio.ndim == 1:
                    window = audio[i:i + window_size]
                    rms = np.sqrt(np.mean(window ** 2))
                else:
                    window_left = audio[0, i:i + window_size]
                    window_right = audio[1, i:i + window_size]
                    rms = np.sqrt((np.mean(window_left ** 2) + np.mean(window_right ** 2)) / 2)
                
                if rms > 0:
                    rms_values.append(rms)
            
            if len(rms_values) >= 2:
                # Dynamic range as difference between 95th and 10th percentile
                high_percentile = np.percentile(rms_values, 95)
                low_percentile = np.percentile(rms_values, 10)
                
                if low_percentile > 0:
                    dr = 20 * np.log10(high_percentile / low_percentile)
                    return float(dr)
            
            return 6.0  # Default DR value
            
        except Exception as e:
            logger.warning(f"Dynamic range calculation failed: {e}")
            return 6.0