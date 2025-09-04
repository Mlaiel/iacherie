"""🎛️ Audio Effects Module - Professional Audio Effects & Filters

Advanced audio effects processing including EQ, compression, reverb, chorus, and creative effects
for the IA Influencer Agent platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import scipy.signal as signal
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging


class EffectType(Enum):
    """Audio effect types"""
    EQUALIZER = "equalizer"
    COMPRESSOR = "compressor"
    REVERB = "reverb"
    DELAY = "delay"
    CHORUS = "chorus"
    DISTORTION = "distortion"
    FILTER = "filter"


@dataclass
class EffectParameters:
    """Effect parameter container"""
    effect_type: EffectType
    parameters: Dict[str, float]
    bypass: bool = False


class EqualizerProcessor:
    """🎚️ Professional Parametric Equalizer"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
    
    def apply_eq(self, audio_data: np.ndarray, bands: List[Dict[str, float]]) -> np.ndarray:
        """Apply parametric EQ with multiple bands"""
        processed_audio = audio_data.copy()
        
        for band in bands:
            freq = band.get("frequency", 1000)
            gain = band.get("gain", 0)  # dB
            q = band.get("q", 1.0)
            
            if gain != 0:
                processed_audio = self._apply_eq_band(processed_audio, freq, gain, q)
        
        return processed_audio
    
    def _apply_eq_band(self, audio_data: np.ndarray, freq: float, gain_db: float, q: float) -> np.ndarray:
        """Apply single EQ band"""
        nyquist = self.sample_rate / 2
        w0 = 2 * np.pi * freq / self.sample_rate
        alpha = np.sin(w0) / (2 * q)
        A = 10 ** (gain_db / 40)
        
        # Bell filter coefficients
        b0 = 1 + alpha * A
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / A
        
        # Normalize
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1/a0, a2/a0])
        
        return signal.lfilter(b, a, audio_data)


class CompressorProcessor:
    """🗜️ Professional Dynamic Range Compressor"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
    
    def apply_compression(self, audio_data: np.ndarray, 
                         threshold: float = 0.7, 
                         ratio: float = 4.0,
                         attack: float = 0.003,
                         release: float = 0.1) -> np.ndarray:
        """Apply dynamic range compression"""
        # Calculate envelope
        envelope = np.abs(audio_data)
        
        # Smooth envelope with attack/release
        attack_samples = int(attack * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        
        smoothed_envelope = self._smooth_envelope(envelope, attack_samples, release_samples)
        
        # Calculate gain reduction
        gain_reduction = np.ones_like(smoothed_envelope)
        above_threshold = smoothed_envelope > threshold
        
        if np.any(above_threshold):
            excess = smoothed_envelope[above_threshold] - threshold
            compressed_excess = excess / ratio
            gain_reduction[above_threshold] = (threshold + compressed_excess) / smoothed_envelope[above_threshold]
        
        return audio_data * gain_reduction
    
    def _smooth_envelope(self, envelope: np.ndarray, attack_samples: int, release_samples: int) -> np.ndarray:
        """Smooth envelope with attack/release times"""
        smoothed = np.zeros_like(envelope)
        smoothed[0] = envelope[0]
        
        for i in range(1, len(envelope)):
            if envelope[i] > smoothed[i-1]:
                # Attack
                alpha = 1.0 - np.exp(-1.0 / attack_samples)
            else:
                # Release
                alpha = 1.0 - np.exp(-1.0 / release_samples)
            
            smoothed[i] = alpha * envelope[i] + (1 - alpha) * smoothed[i-1]
        
        return smoothed


class ReverbProcessor:
    """🏛️ Professional Reverb Engine"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
    
    def apply_reverb(self, audio_data: np.ndarray, 
                    room_size: float = 0.5,
                    damping: float = 0.3,
                    wet_level: float = 0.3) -> np.ndarray:
        """Apply reverb effect"""
        # Create impulse response for reverb
        reverb_length = int(room_size * 2.0 * self.sample_rate)
        impulse_response = self._create_reverb_impulse(reverb_length, damping)
        
        # Convolve with audio
        reverb_signal = signal.convolve(audio_data, impulse_response, mode='same')
        
        # Mix wet and dry signals
        dry_level = 1.0 - wet_level
        return audio_data * dry_level + reverb_signal * wet_level
    
    def _create_reverb_impulse(self, length: int, damping: float) -> np.ndarray:
        """Create reverb impulse response"""
        # Simple exponentially decaying noise
        decay = np.exp(-np.arange(length) * damping / self.sample_rate)
        noise = np.random.normal(0, 1, length)
        
        # Apply decay envelope
        impulse = noise * decay
        
        # Normalize
        impulse /= np.max(np.abs(impulse))
        
        return impulse


class ChorusProcessor:
    """🎵 Professional Chorus Effect"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
    
    def apply_chorus(self, audio_data: np.ndarray,
                    rate: float = 1.5,
                    depth: float = 0.002,
                    mix: float = 0.5) -> np.ndarray:
        """Apply chorus effect"""
        # Create LFO for modulation
        lfo_samples = len(audio_data)
        lfo = np.sin(2 * np.pi * rate * np.arange(lfo_samples) / self.sample_rate)
        
        # Create variable delay
        base_delay = int(0.02 * self.sample_rate)  # 20ms base delay
        mod_delay = lfo * depth * self.sample_rate
        
        # Apply modulated delay
        delayed_signal = np.zeros_like(audio_data)
        
        for i in range(len(audio_data)):
            delay_samples = int(base_delay + mod_delay[i])
            if i >= delay_samples:
                delayed_signal[i] = audio_data[i - delay_samples]
        
        # Mix original and delayed signals
        return audio_data * (1 - mix) + delayed_signal * mix


class DistortionProcessor:
    """🔥 Professional Distortion & Saturation"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def apply_distortion(self, audio_data: np.ndarray,
                        drive: float = 2.0,
                        type: str = "soft") -> np.ndarray:
        """Apply distortion effect"""
        if type == "soft":
            return self._soft_clipping(audio_data, drive)
        elif type == "hard":
            return self._hard_clipping(audio_data, drive)
        elif type == "tube":
            return self._tube_saturation(audio_data, drive)
        else:
            return self._soft_clipping(audio_data, drive)
    
    def _soft_clipping(self, audio_data: np.ndarray, drive: float) -> np.ndarray:
        """Soft clipping distortion"""
        gained_signal = audio_data * drive
        return np.tanh(gained_signal) / drive
    
    def _hard_clipping(self, audio_data: np.ndarray, drive: float) -> np.ndarray:
        """Hard clipping distortion"""
        gained_signal = audio_data * drive
        clipped = np.clip(gained_signal, -1.0, 1.0)
        return clipped / drive
    
    def _tube_saturation(self, audio_data: np.ndarray, drive: float) -> np.ndarray:
        """Tube-style saturation"""
        gained_signal = audio_data * drive
        # Asymmetric saturation
        positive_mask = gained_signal > 0
        negative_mask = gained_signal <= 0
        
        result = np.zeros_like(gained_signal)
        result[positive_mask] = np.tanh(gained_signal[positive_mask] * 0.7)
        result[negative_mask] = np.tanh(gained_signal[negative_mask] * 1.2)
        
        return result / drive


class AudioMixer:
    """🎛️ Professional Audio Mixing Console"""
    
    def __init__(self, num_channels: int = 8):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.num_channels = num_channels
        self.channel_levels = np.ones(num_channels)
        self.channel_pans = np.zeros(num_channels)  # -1 to 1
    
    def mix_channels(self, channel_audios: List[np.ndarray]) -> np.ndarray:
        """Mix multiple audio channels"""
        if not channel_audios:
            return np.array([])
        
        # Ensure all channels have same length
        max_length = max(len(audio) for audio in channel_audios)
        mixed_audio = np.zeros(max_length)
        
        for i, audio in enumerate(channel_audios[:self.num_channels]):
            if len(audio) < max_length:
                # Pad shorter audio
                padded_audio = np.pad(audio, (0, max_length - len(audio)), mode='constant')
            else:
                padded_audio = audio[:max_length]
            
            # Apply level and pan
            level = self.channel_levels[i] if i < len(self.channel_levels) else 1.0
            mixed_audio += padded_audio * level
        
        # Normalize to prevent clipping
        max_level = np.max(np.abs(mixed_audio))
        if max_level > 1.0:
            mixed_audio /= max_level
        
        return mixed_audio
    
    def set_channel_level(self, channel: int, level: float):
        """Set level for specific channel"""
        if 0 <= channel < self.num_channels:
            self.channel_levels[channel] = level


class MasteringProcessor:
    """🎯 Professional Mastering Chain"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Initialize processors
        self.eq = EqualizerProcessor(sample_rate)
        self.compressor = CompressorProcessor(sample_rate)
    
    def master_audio(self, audio_data: np.ndarray,
                    target_lufs: float = -14.0,
                    eq_settings: Optional[List[Dict[str, float]]] = None) -> np.ndarray:
        """Apply mastering chain"""
        processed = audio_data.copy()
        
        # EQ
        if eq_settings:
            processed = self.eq.apply_eq(processed, eq_settings)
        
        # Compression
        processed = self.compressor.apply_compression(processed, threshold=0.7, ratio=3.0)
        
        # Limiting and loudness normalization
        processed = self._apply_limiting(processed, target_lufs)
        
        return processed
    
    def _apply_limiting(self, audio_data: np.ndarray, target_lufs: float) -> np.ndarray:
        """Apply limiting and loudness normalization"""
        # Measure current loudness (simplified)
        current_rms = np.sqrt(np.mean(audio_data ** 2))
        target_rms = 10 ** (target_lufs / 20)
        
        # Calculate gain
        gain = target_rms / (current_rms + 1e-10)
        
        # Apply gain with limiting
        gained_audio = audio_data * gain
        limited_audio = np.tanh(gained_audio * 0.95) * 0.95
        
        return limited_audio


__all__ = [
    'EqualizerProcessor', 'CompressorProcessor', 'ReverbProcessor', 
    'ChorusProcessor', 'DistortionProcessor', 'AudioMixer', 'MasteringProcessor'
]