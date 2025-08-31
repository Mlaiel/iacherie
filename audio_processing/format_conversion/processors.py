"""Audio Processing Chain - Professional Audio Processing Pipeline

Advanced audio processing pipeline with modular processors and effects chain management.
Provides professional-grade audio processing capabilities for format conversion.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import numpy as np
from scipy import signal
from scipy.signal import butter, filtfilt, hilbert
import librosa
from datetime import datetime

from ..core.config import AudioConfig
from ..core.exceptions import ProcessingError
from .models import ProcessingOptions, AudioBuffer
from .config import ProcessingConfig

logger = logging.getLogger(__name__)


class AudioProcessor(ABC):
    """    Abstract base class for audio processors
    
    Defines the interface for all audio processing components
    in the conversion pipeline.
    """    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize processor"""        self.name = name
        self.config = config or {}
        self.enabled = True
        self.bypass = False
        
    @abstractmethod
    async def process(self, 
                    audio_data: np.ndarray, 
                    sample_rate: int,
                    **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """        Process audio data
        
        Args:
            audio_data: Input audio data
            sample_rate: Audio sample rate
            **kwargs: Additional processing parameters
            
        Returns:
            Tuple of (processed_audio, processing_info)
        """        pass
    
    async def validate_input(self, audio_data: np.ndarray, sample_rate: int) -> bool:
        """Validate input parameters"""        if audio_data is None or len(audio_data) == 0:
            return False
        
        if sample_rate <= 0:
            return False
        
        return True
    
    def set_enabled(self, enabled: bool):
        """Enable/disable processor"""        self.enabled = enabled
    
    def set_bypass(self, bypass: bool):
        """Set bypass mode"""        self.bypass = bypass


class NormalizationProcessor(AudioProcessor):
    """    Audio Normalization Processor
    
    Provides multiple normalization algorithms including peak, RMS,
    and loudness-based normalization with professional standards compliance.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize normalization processor"""        super().__init__("Normalization", config)
        self.normalization_type = self.config.get('type', 'peak')  # peak, rms, lufs
        self.target_level = self.config.get('target_level', -3.0)  # dB
        self.headroom = self.config.get('headroom', 1.0)  # dB
        
    async def process(self, 
                    audio_data: np.ndarray, 
                    sample_rate: int,
                    **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process audio with normalization"""        if self.bypass or not self.enabled:
            return audio_data, {'bypassed': True}
        
        try:
            if not await self.validate_input(audio_data, sample_rate):
                raise ProcessingError("Invalid input for normalization")
            
            processing_info = {
                'processor': self.name,
                'type': self.normalization_type,
                'target_level': self.target_level
            }
            
            if self.normalization_type == 'peak':
                normalized_audio, norm_info = await self._peak_normalize(audio_data)
            elif self.normalization_type == 'rms':
                normalized_audio, norm_info = await self._rms_normalize(audio_data)
            elif self.normalization_type == 'lufs':
                normalized_audio, norm_info = await self._lufs_normalize(audio_data, sample_rate)
            else:
                normalized_audio, norm_info = await self._peak_normalize(audio_data)
            
            processing_info.update(norm_info)
            
            return normalized_audio, processing_info
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return audio_data, {'error': str(e)}
    
    async def _peak_normalize(self, audio_data: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Peak normalization"""        peak_level = np.max(np.abs(audio_data))
        if peak_level == 0:
            return audio_data, {'gain_applied': 0.0, 'original_peak': 0.0}
        
        # Convert target level from dB to linear
        target_linear = 10 ** (self.target_level / 20.0)
        gain = target_linear / peak_level
        
        normalized_audio = audio_data * gain
        
        info = {
            'gain_applied': 20 * np.log10(gain),
            'original_peak': 20 * np.log10(peak_level),
            'final_peak': self.target_level
        }
        
        return normalized_audio, info
    
    async def _rms_normalize(self, audio_data: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """RMS normalization"""        rms_level = np.sqrt(np.mean(audio_data ** 2))
        if rms_level == 0:
            return audio_data, {'gain_applied': 0.0, 'original_rms': -float('inf')}
        
        # Convert target level from dB to linear
        target_linear = 10 ** (self.target_level / 20.0)
        gain = target_linear / rms_level
        
        # Apply headroom limitation
        peak_after_gain = np.max(np.abs(audio_data)) * gain
        headroom_linear = 10 ** (-self.headroom / 20.0)
        
        if peak_after_gain > headroom_linear:
            gain = headroom_linear / np.max(np.abs(audio_data))
        
        normalized_audio = audio_data * gain
        
        info = {
            'gain_applied': 20 * np.log10(gain),
            'original_rms': 20 * np.log10(rms_level),
            'final_rms': 20 * np.log10(np.sqrt(np.mean(normalized_audio ** 2)))
        }
        
        return normalized_audio, info
    
    async def _lufs_normalize(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """LUFS (Loudness Units relative to Full Scale) normalization"""        # Simplified LUFS calculation - in production use pyloudnorm
        # This is a basic implementation
        
        # Apply K-weighting filter (simplified)
        # High-pass filter
        b_high, a_high = butter(4, 75.0 / (sample_rate / 2), 'high')
        filtered_audio = filtfilt(b_high, a_high, audio_data)
        
        # RLB weighting (simplified)
        mean_square = np.mean(filtered_audio ** 2)
        if mean_square == 0:
            return audio_data, {'gain_applied': 0.0, 'original_lufs': -float('inf')}
        
        # Convert to LUFS (approximation)
        lufs_level = -0.691 + 10 * np.log10(mean_square)
        
        # Calculate gain needed
        gain_db = self.target_level - lufs_level
        gain_linear = 10 ** (gain_db / 20.0)
        
        # Apply headroom check
        peak_after_gain = np.max(np.abs(audio_data)) * gain_linear
        if peak_after_gain > 10 ** (-self.headroom / 20.0):
            gain_linear = 10 ** (-self.headroom / 20.0) / np.max(np.abs(audio_data))
            gain_db = 20 * np.log10(gain_linear)
        
        normalized_audio = audio_data * gain_linear
        
        info = {
            'gain_applied': gain_db,
            'original_lufs': lufs_level,
            'target_lufs': self.target_level
        }
        
        return normalized_audio, info


class LimiterProcessor(AudioProcessor):
    """    Professional Audio Limiter
    
    Soft/hard limiting with lookahead and envelope following
    to prevent clipping and control peaks.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize limiter processor"""        super().__init__("Limiter", config)
        self.threshold = self.config.get('threshold', -0.1)  # dB
        self.release_time = self.config.get('release_time', 0.05)  # seconds
        self.lookahead = self.config.get('lookahead', 0.005)  # seconds
        self.soft_knee = self.config.get('soft_knee', True)
        
    async def process(self, 
                    audio_data: np.ndarray, 
                    sample_rate: int,
                    **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process audio with limiting"""        if self.bypass or not self.enabled:
            return audio_data, {'bypassed': True}
        
        try:
            if not await self.validate_input(audio_data, sample_rate):
                raise ProcessingError("Invalid input for limiter")
            
            threshold_linear = 10 ** (self.threshold / 20.0)
            release_samples = int(self.release_time * sample_rate)
            lookahead_samples = int(self.lookahead * sample_rate)
            
            # Add lookahead delay
            delayed_audio = np.concatenate([np.zeros(lookahead_samples), audio_data])
            
            # Peak detection with lookahead
            envelope = np.abs(delayed_audio)
            
            # Smooth envelope
            if release_samples > 0:
                # Simple exponential decay envelope follower
                smoothed_envelope = np.copy(envelope)
                for i in range(1, len(smoothed_envelope)):
                    if envelope[i] < smoothed_envelope[i-1]:
                        alpha = np.exp(-1.0 / release_samples)
                        smoothed_envelope[i] = alpha * smoothed_envelope[i-1] + (1-alpha) * envelope[i]
                    else:
                        smoothed_envelope[i] = envelope[i]
                envelope = smoothed_envelope
            
            # Calculate gain reduction
            gain = np.ones_like(envelope)
            over_threshold = envelope > threshold_linear
            
            if self.soft_knee:
                # Soft knee limiting
                knee_ratio = 0.5
                over_knee = envelope > (threshold_linear * knee_ratio)
                
                # Smooth transition
                knee_gain = (threshold_linear / envelope) ** 0.5
                gain[over_knee & ~over_threshold] = knee_gain[over_knee & ~over_threshold]
                gain[over_threshold] = threshold_linear / envelope[over_threshold]
            else:
                # Hard limiting
                gain[over_threshold] = threshold_linear / envelope[over_threshold]
            
            # Apply gain and remove lookahead delay
            limited_audio = (delayed_audio * gain)[lookahead_samples:]
            
            # Calculate statistics
            max_gain_reduction = np.min(gain)
            avg_gain_reduction = np.mean(gain[gain < 1.0]) if np.any(gain < 1.0) else 1.0
            
            processing_info = {
                'processor': self.name,
                'threshold_db': self.threshold,
                'max_gain_reduction_db': 20 * np.log10(max_gain_reduction) if max_gain_reduction > 0 else -60,
                'avg_gain_reduction_db': 20 * np.log10(avg_gain_reduction) if avg_gain_reduction > 0 else 0,
                'samples_limited': np.sum(gain < 1.0)
            }
            
            return limited_audio, processing_info
            
        except Exception as e:
            logger.error(f"Limiting failed: {e}")
            return audio_data, {'error': str(e)}


class EqualizerProcessor(AudioProcessor):
    """    Professional Multi-band Equalizer
    
    Parametric EQ with multiple bands, high/low-pass filters,
    and professional audio processing capabilities.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize equalizer processor"""        super().__init__("Equalizer", config)
        self.bands = self.config.get('bands', [])  # List of EQ bands
        self.high_pass_freq = self.config.get('high_pass_freq', None)
        self.low_pass_freq = self.config.get('low_pass_freq', None)
        
    async def process(self, 
                    audio_data: np.ndarray, 
                    sample_rate: int,
                    **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process audio with equalization"""        if self.bypass or not self.enabled:
            return audio_data, {'bypassed': True}
        
        try:
            if not await self.validate_input(audio_data, sample_rate):
                raise ProcessingError("Invalid input for equalizer")
            
            processed_audio = audio_data.copy()
            processing_info = {
                'processor': self.name,
                'bands_applied': [],
                'filters_applied': []
            }
            
            # Apply high-pass filter
            if self.high_pass_freq and self.high_pass_freq > 0:
                processed_audio = await self._apply_highpass(
                    processed_audio, sample_rate, self.high_pass_freq
                )
                processing_info['filters_applied'].append(f"High-pass: {self.high_pass_freq} Hz")
            
            # Apply low-pass filter
            if self.low_pass_freq and self.low_pass_freq < sample_rate / 2:
                processed_audio = await self._apply_lowpass(
                    processed_audio, sample_rate, self.low_pass_freq
                )
                processing_info['filters_applied'].append(f"Low-pass: {self.low_pass_freq} Hz")
            
            # Apply EQ bands
            for band in self.bands:
                if band.get('enabled', True):
                    processed_audio = await self._apply_eq_band(
                        processed_audio, sample_rate, band
                    )
                    processing_info['bands_applied'].append({
                        'frequency': band.get('frequency', 1000),
                        'gain': band.get('gain', 0),
                        'q': band.get('q', 1.0),
                        'type': band.get('type', 'peak')
                    })
            
            return processed_audio, processing_info
            
        except Exception as e:
            logger.error(f"Equalization failed: {e}")
            return audio_data, {'error': str(e)}
    
    async def _apply_highpass(self, 
                            audio_data: np.ndarray, 
                            sample_rate: int, 
                            freq: float) -> np.ndarray:
        """Apply high-pass filter"""        nyquist = sample_rate / 2
        normalized_freq = freq / nyquist
        
        if normalized_freq >= 1.0:
            return audio_data
        
        b, a = butter(4, normalized_freq, btype='high')
        return filtfilt(b, a, audio_data)
    
    async def _apply_lowpass(self, 
                           audio_data: np.ndarray, 
                           sample_rate: int, 
                           freq: float) -> np.ndarray:
        """Apply low-pass filter"""        nyquist = sample_rate / 2
        normalized_freq = freq / nyquist
        
        if normalized_freq >= 1.0:
            return audio_data
        
        b, a = butter(4, normalized_freq, btype='low')
        return filtfilt(b, a, audio_data)
    
    async def _apply_eq_band(self, 
                           audio_data: np.ndarray, 
                           sample_rate: int, 
                           band: Dict[str, Any]) -> np.ndarray:
        """Apply single EQ band"""        freq = band.get('frequency', 1000)
        gain = band.get('gain', 0)
        q = band.get('q', 1.0)
        eq_type = band.get('type', 'peak')
        
        if gain == 0:
            return audio_data
        
        nyquist = sample_rate / 2
        normalized_freq = freq / nyquist
        
        if normalized_freq >= 1.0 or normalized_freq <= 0:
            return audio_data
        
        # Calculate filter coefficients based on type
        if eq_type == 'peak':
            # Peaking EQ
            A = 10 ** (gain / 40)
            w0 = 2 * np.pi * normalized_freq
            cos_w0 = np.cos(w0)
            sin_w0 = np.sin(w0)
            alpha = sin_w0 / (2 * q)
            
            b0 = 1 + alpha * A
            b1 = -2 * cos_w0
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * cos_w0
            a2 = 1 - alpha / A
            
            b = np.array([b0, b1, b2]) / a0
            a = np.array([1, a1/a0, a2/a0])
            
        elif eq_type == 'shelf_low':
            # Low shelf
            A = 10 ** (gain / 40)
            w0 = 2 * np.pi * normalized_freq
            cos_w0 = np.cos(w0)
            sin_w0 = np.sin(w0)
            S = 1  # Shelf slope
            beta = np.sqrt(A) / q
            
            b0 = A * ((A + 1) - (A - 1) * cos_w0 + beta * sin_w0)
            b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
            b2 = A * ((A + 1) - (A - 1) * cos_w0 - beta * sin_w0)
            a0 = (A + 1) + (A - 1) * cos_w0 + beta * sin_w0
            a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
            a2 = (A + 1) + (A - 1) * cos_w0 - beta * sin_w0
            
            b = np.array([b0, b1, b2]) / a0
            a = np.array([1, a1/a0, a2/a0])
            
        elif eq_type == 'shelf_high':
            # High shelf
            A = 10 ** (gain / 40)
            w0 = 2 * np.pi * normalized_freq
            cos_w0 = np.cos(w0)
            sin_w0 = np.sin(w0)
            beta = np.sqrt(A) / q
            
            b0 = A * ((A + 1) + (A - 1) * cos_w0 + beta * sin_w0)
            b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
            b2 = A * ((A + 1) + (A - 1) * cos_w0 - beta * sin_w0)
            a0 = (A + 1) - (A - 1) * cos_w0 + beta * sin_w0
            a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
            a2 = (A + 1) - (A - 1) * cos_w0 - beta * sin_w0
            
            b = np.array([b0, b1, b2]) / a0
            a = np.array([1, a1/a0, a2/a0])
        else:
            return audio_data
        
        # Apply filter
        return signal.lfilter(b, a, audio_data)


class DitheringProcessor(AudioProcessor):
    """    Professional Dithering Processor
    
    Applies shaped dithering for bit-depth reduction with
    noise shaping and psychoacoustic optimization.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dithering processor"""        super().__init__("Dithering", config)
        self.target_bits = self.config.get('target_bits', 16)
        self.dither_type = self.config.get('type', 'triangular')  # triangular, rectangular, shaped
        self.noise_shaping = self.config.get('noise_shaping', True)
        
    async def process(self, 
                    audio_data: np.ndarray, 
                    sample_rate: int,
                    **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process audio with dithering"""        if self.bypass or not self.enabled:
            return audio_data, {'bypassed': True}
        
        try:
            if not await self.validate_input(audio_data, sample_rate):
                raise ProcessingError("Invalid input for dithering")
            
            # Calculate quantization level
            max_level = 2 ** (self.target_bits - 1)
            quantization_step = 2.0 / (2 ** self.target_bits)
            
            # Generate dither noise
            if self.dither_type == 'triangular':
                # Triangular PDF dither (TPDF)
                noise1 = np.random.uniform(-1, 1, audio_data.shape)
                noise2 = np.random.uniform(-1, 1, audio_data.shape)
                dither_noise = (noise1 + noise2) * quantization_step / 2
                
            elif self.dither_type == 'rectangular':
                # Rectangular PDF dither (RPDF)
                dither_noise = np.random.uniform(
                    -quantization_step/2, quantization_step/2, audio_data.shape
                )
                
            elif self.dither_type == 'shaped':
                # Noise-shaped dither
                dither_noise = await self._generate_shaped_dither(
                    audio_data.shape, sample_rate, quantization_step
                )
            else:
                dither_noise = np.zeros_like(audio_data)
            
            # Add dither and quantize
            dithered_audio = audio_data + dither_noise
            
            # Quantize to target bit depth
            quantized_audio = np.round(dithered_audio * max_level) / max_level
            
            # Clip to valid range
            quantized_audio = np.clip(quantized_audio, -1.0, 1.0 - quantization_step)
            
            processing_info = {
                'processor': self.name,
                'target_bits': self.target_bits,
                'dither_type': self.dither_type,
                'noise_shaping': self.noise_shaping,
                'quantization_step': quantization_step,
                'noise_floor_db': 20 * np.log10(quantization_step / 2)
            }
            
            return quantized_audio, processing_info
            
        except Exception as e:
            logger.error(f"Dithering failed: {e}")
            return audio_data, {'error': str(e)}
    
    async def _generate_shaped_dither(self, 
                                    shape: Tuple, 
                                    sample_rate: int, 
                                    quantization_step: float) -> np.ndarray:
        """Generate noise-shaped dither"""        # Simple first-order noise shaping
        # In production, use more sophisticated psychoacoustic models
        
        # Generate white noise
        white_noise = np.random.uniform(-1, 1, shape) * quantization_step / 2
        
        # Apply simple high-pass shaping (pushes noise to higher frequencies)
        if len(shape) > 1:
            # Stereo processing
            shaped_noise = np.zeros_like(white_noise)
            for ch in range(shape[1]):
                channel_noise = white_noise[:, ch]
                # Simple first-order difference (high-pass)
                shaped_channel = np.zeros_like(channel_noise)
                shaped_channel[1:] = channel_noise[1:] - 0.5 * channel_noise[:-1]
                shaped_channel[0] = channel_noise[0]
                shaped_noise[:, ch] = shaped_channel
        else:
            # Mono processing
            shaped_noise = np.zeros_like(white_noise)
            shaped_noise[1:] = white_noise[1:] - 0.5 * white_noise[:-1]
            shaped_noise[0] = white_noise[0]
        
        return shaped_noise * 0.5  # Reduce level for shaped noise


class ProcessorChain:
    """    Professional Audio Processing Chain
    
    Manages a sequence of audio processors with sophisticated routing,
    parallel processing, and real-time parameter adjustment capabilities.
    """    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """Initialize processing chain"""        self.config = config or ProcessingConfig()
        self.processors: List[AudioProcessor] = []
        self.processing_history: List[Dict[str, Any]] = []
        self.parallel_enabled = False
        self.max_workers = 4
        
    def add_processor(self, processor: AudioProcessor, position: Optional[int] = None):
        """Add processor to chain"""        if position is None:
            self.processors.append(processor)
        else:
            self.processors.insert(position, processor)
        
        logger.info(f"Added processor {processor.name} to chain")
    
    def remove_processor(self, processor_name: str) -> bool:
        """Remove processor from chain"""        for i, processor in enumerate(self.processors):
            if processor.name == processor_name:
                removed = self.processors.pop(i)
                logger.info(f"Removed processor {removed.name} from chain")
                return True
        return False
    
    def get_processor(self, processor_name: str) -> Optional[AudioProcessor]:
        """Get processor by name"""        for processor in self.processors:
            if processor.name == processor_name:
                return processor
        return None
    
    def reorder_processors(self, processor_names: List[str]):
        """Reorder processors in chain"""        new_order = []
        
        for name in processor_names:
            processor = self.get_processor(name)
            if processor:
                new_order.append(processor)
        
        # Add any remaining processors
        for processor in self.processors:
            if processor not in new_order:
                new_order.append(processor)
        
        self.processors = new_order
        logger.info(f"Reordered processors: {[p.name for p in self.processors]}")
    
    async def process_audio(self, 
                          audio_data: np.ndarray, 
                          sample_rate: int,
                          processing_options: Optional[ProcessingOptions] = None) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """        Process audio through the entire chain
        
        Args:
            audio_data: Input audio data
            sample_rate: Audio sample rate
            processing_options: Processing options and parameters
            
        Returns:
            Tuple of (processed_audio, processing_info_list)
        """        if not self.processors:
            return audio_data, []
        
        try:
            current_audio = audio_data.copy()
            processing_info_list = []
            
            start_time = datetime.now()
            
            # Process through each processor in sequence
            for i, processor in enumerate(self.processors):
                if not processor.enabled:
                    continue
                
                processor_start = datetime.now()
                
                try:
                    processed_audio, processor_info = await processor.process(
                        current_audio, sample_rate
                    )
                    
                    current_audio = processed_audio
                    
                    # Add timing information
                    processor_info['processing_time'] = (
                        datetime.now() - processor_start
                    ).total_seconds()
                    processor_info['processor_index'] = i
                    
                    processing_info_list.append(processor_info)
                    
                except Exception as e:
                    logger.error(f"Processor {processor.name} failed: {e}")
                    processor_info = {
                        'processor': processor.name,
                        'error': str(e),
                        'processor_index': i
                    }
                    processing_info_list.append(processor_info)
                    
                    # Continue with original audio if processor fails
                    # This ensures the chain doesn't break completely
            
            # Calculate total processing time
            total_processing_time = (datetime.now() - start_time).total_seconds()
            
            # Add chain-level information
            chain_info = {
                'total_processing_time': total_processing_time,
                'processors_executed': len([info for info in processing_info_list if 'error' not in info]),
                'processors_failed': len([info for info in processing_info_list if 'error' in info]),
                'chain_length': len(self.processors)
            }
            
            processing_info_list.append(chain_info)
            
            # Store in history
            self.processing_history.append({
                'timestamp': datetime.now().isoformat(),
                'input_shape': audio_data.shape,
                'output_shape': current_audio.shape,
                'sample_rate': sample_rate,
                'processing_info': processing_info_list
            })
            
            # Limit history size
            if len(self.processing_history) > 100:
                self.processing_history = self.processing_history[-100:]
            
            return current_audio, processing_info_list
            
        except Exception as e:
            logger.error(f"Processing chain failed: {e}")
            return audio_data, [{'error': f"Chain processing failed: {e}"}]
    
    def create_standard_chain(self, chain_type: str = "default") -> None:
        """Create standard processing chain"""        self.processors.clear()
        
        if chain_type == "mastering":
            # Professional mastering chain
            self.add_processor(EqualizerProcessor({
                'high_pass_freq': 30,
                'bands': [
                    {'frequency': 100, 'gain': 0, 'q': 0.7, 'type': 'shelf_low'},
                    {'frequency': 3000, 'gain': 0, 'q': 1.0, 'type': 'peak'},
                    {'frequency': 10000, 'gain': 0, 'q': 0.7, 'type': 'shelf_high'}
                ]
            }))
            self.add_processor(LimiterProcessor({
                'threshold': -0.1,
                'release_time': 0.05,
                'soft_knee': True
            }))
            self.add_processor(NormalizationProcessor({
                'type': 'lufs',
                'target_level': -14.0
            }))
            
        elif chain_type == "broadcast":
            # Broadcast-ready chain
            self.add_processor(EqualizerProcessor({
                'high_pass_freq': 40,
                'low_pass_freq': 18000
            }))
            self.add_processor(LimiterProcessor({
                'threshold': -1.0,
                'release_time': 0.1,
                'soft_knee': True
            }))
            self.add_processor(NormalizationProcessor({
                'type': 'lufs',
                'target_level': -23.0
            }))
            
        elif chain_type == "streaming":
            # Streaming optimization chain
            self.add_processor(NormalizationProcessor({
                'type': 'lufs',
                'target_level': -14.0
            }))
            self.add_processor(LimiterProcessor({
                'threshold': -0.5,
                'release_time': 0.03,
                'soft_knee': True
            }))
            
        else:
            # Default chain
            self.add_processor(NormalizationProcessor({
                'type': 'peak',
                'target_level': -3.0
            }))
            self.add_processor(LimiterProcessor({
                'threshold': -0.1,
                'release_time': 0.05
            }))
    
    def get_chain_status(self) -> Dict[str, Any]:
        """Get current chain status and statistics"""        return {
            'total_processors': len(self.processors),
            'enabled_processors': len([p for p in self.processors if p.enabled]),
            'bypassed_processors': len([p for p in self.processors if p.bypass]),
            'processor_names': [p.name for p in self.processors],
            'processing_history_length': len(self.processing_history),
            'parallel_enabled': self.parallel_enabled
        }


class EffectsProcessor(AudioProcessor):
    """    Advanced Audio Effects Processor
    
    Provides creative audio effects including reverb, delay, chorus,
    and other time-based and spectral effects.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize effects processor"""        super().__init__("Effects", config)
        self.effect_type = self.config.get('type', 'none')
        self.effect_params = self.config.get('params', {})
        
    async def process(self, 
                    audio_data: np.ndarray, 
                    sample_rate: int,
                    **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process audio with effects"""        if self.bypass or not self.enabled or self.effect_type == 'none':
            return audio_data, {'bypassed': True}
        
        try:
            if not await self.validate_input(audio_data, sample_rate):
                raise ProcessingError("Invalid input for effects processor")
            
            if self.effect_type == 'reverb':
                return await self._apply_reverb(audio_data, sample_rate)
            elif self.effect_type == 'delay':
                return await self._apply_delay(audio_data, sample_rate)
            elif self.effect_type == 'chorus':
                return await self._apply_chorus(audio_data, sample_rate)
            else:
                return audio_data, {'effect': 'unknown'}
                
        except Exception as e:
            logger.error(f"Effects processing failed: {e}")
            return audio_data, {'error': str(e)}
    
    async def _apply_reverb(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply simple reverb effect"""        room_size = self.effect_params.get('room_size', 0.5)
        decay_time = self.effect_params.get('decay_time', 1.0)
        wet_level = self.effect_params.get('wet_level', 0.3)
        
        # Simple feedback delay network reverb
        delay_times = [0.03, 0.05, 0.07, 0.11]  # seconds
        feedback_gains = [0.6 * room_size] * 4
        
        reverb_audio = audio_data.copy()
        
        for delay_time, feedback in zip(delay_times, feedback_gains):
            delay_samples = int(delay_time * sample_rate)
            if delay_samples > 0:
                # Create delayed version with feedback
                delayed = np.zeros_like(audio_data)
                delayed[delay_samples:] = audio_data[:-delay_samples] * feedback
                reverb_audio += delayed
        
        # Mix wet and dry signals
        output_audio = (1 - wet_level) * audio_data + wet_level * reverb_audio
        
        return output_audio, {
            'processor': self.name,
            'effect': 'reverb',
            'room_size': room_size,
            'decay_time': decay_time,
            'wet_level': wet_level
        }
    
    async def _apply_delay(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply delay effect"""        delay_time = self.effect_params.get('delay_time', 0.25)  # seconds
        feedback = self.effect_params.get('feedback', 0.3)
        wet_level = self.effect_params.get('wet_level', 0.3)
        
        delay_samples = int(delay_time * sample_rate)
        
        if delay_samples <= 0 or delay_samples >= len(audio_data):
            return audio_data, {'effect': 'delay', 'error': 'invalid_delay_time'}
        
        # Create delay line
        delayed_audio = np.zeros_like(audio_data)
        delayed_audio[delay_samples:] = audio_data[:-delay_samples] * feedback
        
        # Simple feedback (be careful with stability)
        if feedback > 0:
            for i in range(delay_samples, len(delayed_audio)):
                if i + delay_samples < len(delayed_audio):
                    delayed_audio[i] += delayed_audio[i - delay_samples] * feedback * 0.5
        
        # Mix wet and dry
        output_audio = (1 - wet_level) * audio_data + wet_level * delayed_audio
        
        return output_audio, {
            'processor': self.name,
            'effect': 'delay',
            'delay_time': delay_time,
            'feedback': feedback,
            'wet_level': wet_level
        }
    
    async def _apply_chorus(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply chorus effect"""        rate = self.effect_params.get('rate', 1.0)  # Hz
        depth = self.effect_params.get('depth', 0.005)  # seconds
        wet_level = self.effect_params.get('wet_level', 0.5)
        
        # Generate LFO for modulation
        t = np.arange(len(audio_data)) / sample_rate
        lfo = np.sin(2 * np.pi * rate * t)
        
        # Create time-varying delay
        base_delay_samples = int(0.01 * sample_rate)  # 10ms base delay
        max_delay_samples = int(depth * sample_rate)
        
        chorus_audio = np.zeros_like(audio_data)
        
        for i in range(len(audio_data)):
            delay_variation = int(lfo[i] * max_delay_samples)
            delay_samples = base_delay_samples + delay_variation
            
            if i >= delay_samples and delay_samples > 0:
                chorus_audio[i] = audio_data[i - delay_samples]
        
        # Mix with original
        output_audio = (1 - wet_level) * audio_data + wet_level * chorus_audio
        
        return output_audio, {
            'processor': self.name,
            'effect': 'chorus',
            'rate': rate,
            'depth': depth,
            'wet_level': wet_level
        }


# Export main classes
__all__ = [
    'ProcessorChain',
    'AudioProcessor',
    'EffectsProcessor',
    'NormalizationProcessor',
    'LimiterProcessor',
    'EqualizerProcessor',
    'DitheringProcessor'
]
