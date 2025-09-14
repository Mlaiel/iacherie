"""🎛️ Audio Effects Module - Professional Audio Effects & Filters Enterprise

⚠️ AVERTISSEMENT LÉGAL STRICT - Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, vol ou reproduction sans autorisation écrite expresse est strictement
interdite et passible de poursuites judiciaires.

MODULES ENTERPRISE AUDIO EFFECTS:
🎛️ Suite Effets Professionnelle - Reverb/Delay/Modulation
🎨 Traitement Créatif - Distortion/Filtering/Dynamics  
🌐 Audio Spatial - 3D/Binaural/Surround processing
🎸 Émulation Vintage - Modeling hardware analogique
⚡ Traitement Temps Réel - Effets faible latence <5ms
🔗 Traitement Chaîne - Combinaisons multi-effets

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import scipy.signal as signal
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import logging
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import json
import time
from pathlib import Path
import soundfile as sf
from scipy.fft import fft, ifft, fftfreq
from scipy.interpolate import interp1d
import warnings
warnings.filterwarnings('ignore')


class EffectType(Enum):
    """🎛️ Audio Effect Types Enterprise"""
    # Core Effects
    EQUALIZER = "equalizer"
    COMPRESSOR = "compressor"
    LIMITER = "limiter"
    GATE = "gate"
    EXPANDER = "expander"
    
    # Time-based Effects
    REVERB = "reverb"
    DELAY = "delay"
    ECHO = "echo"
    
    # Modulation Effects
    CHORUS = "chorus"
    FLANGER = "flanger"
    PHASER = "phaser"
    TREMOLO = "tremolo"
    VIBRATO = "vibrato"
    
    # Creative Effects
    DISTORTION = "distortion"
    OVERDRIVE = "overdrive"
    BITCRUSHER = "bitcrusher"
    VOCODER = "vocoder"
    
    # Spatial Effects
    STEREO_WIDENER = "stereo_widener"
    BINAURAL = "binaural"
    SURROUND = "surround"
    PANNING = "panning"
    
    # Filter Effects
    LOWPASS = "lowpass"
    HIGHPASS = "highpass"
    BANDPASS = "bandpass"
    NOTCH = "notch"
    
    # Vintage Emulation
    TUBE = "tube"
    TAPE = "tape"
    VINYL = "vinyl"
    ANALOG_EQ = "analog_eq"


class QualityLevel(IntEnum):
    """🎯 Quality Levels for Effects Processing"""
    DRAFT = 1          # Fast processing, lower quality
    GOOD = 2           # Balanced quality/speed
    HIGH = 3           # High quality processing
    AUDIOPHILE = 4     # Maximum quality, slower processing
    REALTIME = 5       # Optimized for real-time processing


class ProcessingMode(Enum):
    """⚡ Processing Modes"""
    REALTIME = "realtime"      # <5ms latency
    BATCH = "batch"            # Offline processing
    STREAMING = "streaming"    # Continuous processing
    MULTICORE = "multicore"    # Parallel processing


@dataclass
class EffectParameters:
    """🎛️ Effect Parameter Container Enterprise"""
    effect_type: EffectType
    parameters: Dict[str, float]
    bypass: bool = False
    wet_dry_mix: float = 1.0   # 0.0 = dry, 1.0 = wet
    quality_level: QualityLevel = QualityLevel.HIGH
    processing_mode: ProcessingMode = ProcessingMode.BATCH
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EffectChain:
    """🔗 Effect Chain Configuration"""
    name: str
    effects: List[EffectParameters]
    parallel_processing: bool = False
    send_returns: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConvolutionIR:
    """🎵 Impulse Response for Convolution"""
    name: str
    impulse_response: np.ndarray
    sample_rate: int
    length_seconds: float
    category: str  # "reverb", "speaker", "amp", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VintageModelingParams:
    """🎸 Vintage Hardware Modeling Parameters"""
    model_type: str  # "tube", "tape", "vinyl", "analog_eq"
    saturation_amount: float = 0.3
    harmonic_enhancement: float = 0.2
    noise_floor: float = -60.0  # dB
    frequency_response_curve: Optional[Dict[str, float]] = None
    dynamic_response: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


class AudioEffectsEngine:
    """🎛️ Professional Audio Effects Engine Enterprise"""
    
    def __init__(self, sample_rate -> None: int = 44100, buffer_size -> None: int = 512,
                 quality_level -> None: QualityLevel = QualityLevel.HIGH) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.quality_level = quality_level
        
        # Initialize processors
        self.equalizer = EqualizerProcessor(sample_rate, quality_level)
        self.compressor = CompressorProcessor(sample_rate, quality_level)
        self.reverb = ReverbProcessor(sample_rate, quality_level)
        self.spatial = SpatialProcessor(sample_rate, quality_level)
        self.modulation = ModulationProcessor(sample_rate, quality_level)
        self.creative = CreativeProcessor(sample_rate, quality_level)
        self.vintage = VintageProcessor(sample_rate, quality_level)
        self.dynamics = DynamicsProcessor(sample_rate, quality_level)
        
        # Performance monitoring
        self.performance_metrics = {}
        self.processing_latency = []
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Real-time processing buffers
        self.realtime_buffers = {}
        
        self.logger.info(f"Audio Effects Engine initialized: {sample_rate}Hz, {quality_level.name}")
    
    async def process_effect_chain(self, audio_data: np.ndarray, 
                                  effect_chain: EffectChain) -> np.ndarray:
        """🔗 Process complete effect chain with parallel capabilities"""
        start_time = time.time()
        
        if effect_chain.parallel_processing:
            result = await self._process_parallel_chain(audio_data, effect_chain)
        else:
            result = await self._process_serial_chain(audio_data, effect_chain)
        
        # Track performance
        processing_time = time.time() - start_time
        self.processing_latency.append(processing_time)
        
        return result
    
    async def _process_serial_chain(self, audio_data: np.ndarray, 
                                   effect_chain: EffectChain) -> np.ndarray:
        """Process effects in series"""
        processed_audio = audio_data.copy()
        
        for effect_params in effect_chain.effects:
            if not effect_params.bypass:
                processed_audio = await self._apply_single_effect(processed_audio, effect_params)
        
        return processed_audio
    
    async def _process_parallel_chain(self, audio_data: np.ndarray, 
                                     effect_chain: EffectChain) -> np.ndarray:
        """Process compatible effects in parallel"""
        # Group effects by type for parallel processing
        parallel_groups = self._group_effects_for_parallel(effect_chain.effects)
        
        processed_audio = audio_data.copy()
        
        for group in parallel_groups:
            if len(group) == 1:
                # Single effect
                processed_audio = await self._apply_single_effect(processed_audio, group[0])
            else:
                # Parallel processing
                tasks = [self._apply_single_effect(processed_audio.copy(), effect) 
                        for effect in group]
                results = await asyncio.gather(*tasks)
                
                # Mix parallel results
                processed_audio = np.mean(results, axis=0)
        
        return processed_audio
    
    def _group_effects_for_parallel(self, effects: List[EffectParameters]) -> List[List[EffectParameters]]:
        """Group effects that can be processed in parallel"""
        # Simple grouping - effects of different types can often be parallelized
        groups = []
        current_group = []
        last_type = None
        
        for effect in effects:
            if (last_type is None or 
                effect.effect_type != last_type or 
                effect.processing_mode != ProcessingMode.MULTICORE):
                if current_group:
                    groups.append(current_group)
                current_group = [effect]
            else:
                current_group.append(effect)
            
            last_type = effect.effect_type
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    async def _apply_single_effect(self, audio_data: np.ndarray, 
                                  effect_params: EffectParameters) -> np.ndarray:
        """Apply single effect based on type"""
        try:
            # Route to appropriate processor
            if effect_params.effect_type == EffectType.EQUALIZER:
                result = self.equalizer.apply_eq(
                    audio_data, 
                    effect_params.parameters.get("bands", []),
                    analog_modeling=effect_params.parameters.get("analog_modeling", False)
                )
            
            elif effect_params.effect_type == EffectType.COMPRESSOR:
                result = self.compressor.apply_compression(
                    audio_data,
                    threshold=effect_params.parameters.get("threshold", -20.0),
                    ratio=effect_params.parameters.get("ratio", 4.0),
                    attack=effect_params.parameters.get("attack", 0.003),
                    release=effect_params.parameters.get("release", 0.1),
                    multiband=effect_params.parameters.get("multiband", False)
                )
            
            elif effect_params.effect_type == EffectType.REVERB:
                result = self.reverb.apply_reverb(
                    audio_data,
                    room_size=effect_params.parameters.get("room_size", 0.5),
                    damping=effect_params.parameters.get("damping", 0.5),
                    wet_level=effect_params.parameters.get("wet_level", 0.3),
                    reverb_type=effect_params.parameters.get("type", "hall")
                )
            
            elif effect_params.effect_type == EffectType.STEREO_WIDENER:
                result = self.spatial.apply_stereo_widening(
                    audio_data,
                    width=effect_params.parameters.get("width", 1.5)
                )
            
            elif effect_params.effect_type == EffectType.BINAURAL:
                result = self.spatial.apply_binaural_processing(
                    audio_data,
                    azimuth=effect_params.parameters.get("azimuth", 0),
                    elevation=effect_params.parameters.get("elevation", 0)
                )
            
            elif effect_params.effect_type == EffectType.CHORUS:
                result = self.modulation.apply_chorus(
                    audio_data,
                    rate=effect_params.parameters.get("rate", 1.0),
                    depth=effect_params.parameters.get("depth", 0.5),
                    voices=effect_params.parameters.get("voices", 3)
                )
            
            elif effect_params.effect_type == EffectType.DISTORTION:
                result = self.creative.apply_distortion(
                    audio_data,
                    drive=effect_params.parameters.get("drive", 2.0),
                    tone=effect_params.parameters.get("tone", 0.5),
                    type=effect_params.parameters.get("type", "tube")
                )
            
            elif effect_params.effect_type in [EffectType.TUBE, EffectType.TAPE, EffectType.VINYL]:
                result = self.vintage.apply_vintage_modeling(
                    audio_data,
                    model_type=effect_params.effect_type.value,
                    saturation=effect_params.parameters.get("saturation", 0.3),
                    harmonic_enhancement=effect_params.parameters.get("harmonic_enhancement", 0.2)
                )
            
            else:
                self.logger.warning(f"Unknown effect type: {effect_params.effect_type}")
                result = audio_data
            
            # Apply wet/dry mix
            if effect_params.wet_dry_mix < 1.0:
                result = (1 - effect_params.wet_dry_mix) * audio_data + effect_params.wet_dry_mix * result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error applying effect {effect_params.effect_type}: {e}")
            return audio_data
    
    def process_realtime(self, audio_buffer: np.ndarray, 
                        effect_chain: EffectChain) -> np.ndarray:
        """⚡ Process audio in real-time with <5ms latency"""
        if effect_chain.name not in self.realtime_buffers:
            self.realtime_buffers[effect_chain.name] = {
                'delay_line': np.zeros((1024, audio_buffer.shape[1] if len(audio_buffer.shape) > 1 else 1)),
                'index': 0
            }
        
        # Simplified real-time processing for low latency
        result = audio_buffer.copy()
        
        for effect_params in effect_chain.effects:
            if (not effect_params.bypass and 
                effect_params.processing_mode == ProcessingMode.REALTIME):
                result = self._apply_realtime_effect(result, effect_params)
        
        return result
    
    def _apply_realtime_effect(self, audio_data: np.ndarray, 
                              effect_params: EffectParameters) -> np.ndarray:
        """Apply effect optimized for real-time processing"""
        # Simplified implementations for real-time processing
        if effect_params.effect_type == EffectType.EQUALIZER:
            # Simple biquad EQ for real-time
            return self.equalizer._apply_realtime_eq(audio_data, effect_params.parameters)
        
        elif effect_params.effect_type == EffectType.COMPRESSOR:
            # Simple peak compressor for real-time
            return self.compressor._apply_realtime_compression(audio_data, effect_params.parameters)
        
        # Add more real-time optimized effects as needed
        return audio_data
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """📊 Get comprehensive performance metrics"""
        if not self.processing_latency:
            return {}
        
        metrics = {
            'processing_latency': {
                'avg_ms': np.mean(self.processing_latency) * 1000,
                'max_ms': np.max(self.processing_latency) * 1000,
                'min_ms': np.min(self.processing_latency) * 1000,
                'std_ms': np.std(self.processing_latency) * 1000
            },
            'realtime_capability': np.mean(self.processing_latency) < 0.005,  # <5ms
            'quality_level': self.quality_level.name,
            'sample_rate': self.sample_rate,
            'buffer_size': self.buffer_size
        }
        
        # Add processor-specific metrics
        metrics.update({
            'equalizer': self.equalizer.get_performance_stats(),
            'compressor': self.compressor.get_performance_stats() if hasattr(self.compressor, 'get_performance_stats') else {},
            'reverb': self.reverb.get_performance_stats() if hasattr(self.reverb, 'get_performance_stats') else {}
        })
        
        return metrics


# Import the existing processors
from .effects import (
    EqualizerProcessor, CompressorProcessor, ReverbProcessor,
    ChorusProcessor, DistortionProcessor, AudioMixer, MasteringProcessor
)


class SpatialProcessor:
    """🌐 Professional Spatial Audio Processing Enterprise"""
    
    def __init__(self, sample_rate -> None: int = 44100, quality_level -> None: QualityLevel = QualityLevel.HIGH) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.quality_level = quality_level
        
        # HRTF data for binaural processing
        self.hrtf_data = {}
        
        # Performance tracking
        self.processing_times = []
    
    def apply_stereo_widening(self, audio_data: np.ndarray, width: float = 1.5) -> np.ndarray:
        """🎧 Apply stereo widening effect"""
        if len(audio_data.shape) == 1 or audio_data.shape[1] == 1:
            # Mono to stereo with width
            mono_signal = audio_data[:, 0] if len(audio_data.shape) > 1 else audio_data
            stereo_data = np.column_stack([mono_signal, mono_signal])
        else:
            stereo_data = audio_data.copy()
        
        # Extract mid and side signals
        mid = (stereo_data[:, 0] + stereo_data[:, 1]) / 2
        side = (stereo_data[:, 0] - stereo_data[:, 1]) / 2
        
        # Apply width to side signal
        side_widened = side * width
        
        # Reconstruct stereo
        left = mid + side_widened
        right = mid - side_widened
        
        return np.column_stack([left, right])
    
    def apply_binaural_processing(self, audio_data: np.ndarray, azimuth: float = 0,
                                elevation: float = 0) -> np.ndarray:
        """🎧 Apply binaural processing for 3D audio"""
        start_time = time.time()
        
        if len(audio_data.shape) == 1:
            mono_signal = audio_data
        else:
            mono_signal = np.mean(audio_data, axis=1)
        
        # Simple HRTF simulation (placeholder for actual HRTF data)
        left_delay, right_delay = self._calculate_itd(azimuth)
        left_gain, right_gain = self._calculate_ild(azimuth, elevation)
        
        # Apply delays and gains
        left_channel = self._apply_delay(mono_signal * left_gain, left_delay)
        right_channel = self._apply_delay(mono_signal * right_gain, right_delay)
        
        result = np.column_stack([left_channel, right_channel])
        
        self.processing_times.append(time.time() - start_time)
        return result
    
    def _calculate_itd(self, azimuth: float) -> Tuple[int, int]:
        """Calculate Interaural Time Difference"""
        # Simplified ITD calculation
        head_radius = 0.0875  # meters
        sound_speed = 343  # m/s
        
        max_delay = head_radius / sound_speed
        delay_seconds = max_delay * np.sin(np.radians(azimuth))
        
        left_delay = int(max(0, -delay_seconds) * self.sample_rate)
        right_delay = int(max(0, delay_seconds) * self.sample_rate)
        
        return left_delay, right_delay
    
    def _calculate_ild(self, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate Interaural Level Difference"""
        # Simplified ILD calculation
        angle_rad = np.radians(abs(azimuth))
        
        if azimuth > 0:  # Sound from right
            left_gain = 1.0 - 0.3 * np.sin(angle_rad)
            right_gain = 1.0
        else:  # Sound from left
            left_gain = 1.0
            right_gain = 1.0 - 0.3 * np.sin(angle_rad)
        
        # Elevation effects (simplified)
        elevation_factor = 1.0 - 0.1 * abs(elevation) / 90
        left_gain *= elevation_factor
        right_gain *= elevation_factor
        
        return left_gain, right_gain
    
    def _apply_delay(self, signal: np.ndarray, delay_samples: int) -> np.ndarray:
        """Apply delay to signal"""
        if delay_samples <= 0:
            return signal
        
        delayed_signal = np.zeros(len(signal) + delay_samples)
        delayed_signal[delay_samples:] = signal
        
        return delayed_signal[:len(signal)]


class ModulationProcessor:
    """🌊 Advanced Modulation Effects Processor"""
    
    def __init__(self, sample_rate -> None: int = 44100, quality_level -> None: QualityLevel = QualityLevel.HIGH) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.quality_level = quality_level
        
        # LFO generators
        self.lfo_phase = 0.0
        self.processing_times = []
    
    def apply_chorus(self, audio_data: np.ndarray, rate: float = 1.0, 
                    depth: float = 0.5, voices: int = 3) -> np.ndarray:
        """🎵 Apply advanced chorus with multiple voices"""
        start_time = time.time()
        
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        chorus_output = audio_data.copy()
        
        # Create multiple delayed voices
        for voice in range(voices):
            base_delay = 0.02 + voice * 0.01  # 20ms + 10ms per voice
            max_delay = base_delay + 0.01  # 10ms modulation range
            
            # Create LFO for this voice with slight phase offset
            phase_offset = voice * (2 * np.pi / voices)
            lfo = np.sin(2 * np.pi * rate * np.arange(len(audio_data)) / self.sample_rate + phase_offset)
            
            # Calculate delay modulation
            delay_samples = (base_delay + depth * 0.01 * lfo) * self.sample_rate
            delay_samples = delay_samples.astype(int)
            
            # Apply modulated delay
            delayed_voice = self._apply_variable_delay(audio_data, delay_samples)
            
            # Mix with slight panning for each voice
            pan = (voice - voices/2) / voices
            left_gain = np.sqrt((1 - pan) / 2) if pan <= 0 else np.sqrt((1 - pan) / 2)
            right_gain = np.sqrt((1 + pan) / 2) if pan >= 0 else np.sqrt((1 + pan) / 2)
            
            if audio_data.shape[1] >= 2:
                chorus_output[:, 0] += delayed_voice[:, 0] * left_gain * 0.3
                chorus_output[:, 1] += delayed_voice[:, 1] * right_gain * 0.3
            else:
                chorus_output += delayed_voice * 0.3
        
        self.processing_times.append(time.time() - start_time)
        return chorus_output
    
    def apply_flanger(self, audio_data: np.ndarray, rate: float = 0.5, 
                     depth: float = 0.8, feedback: float = 0.7) -> np.ndarray:
        """🌊 Apply flanger effect"""
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        # Create LFO
        lfo = np.sin(2 * np.pi * rate * np.arange(len(audio_data)) / self.sample_rate)
        
        # Calculate delay (shorter range than chorus)
        base_delay = 0.002  # 2ms
        max_delay = 0.005   # 5ms
        delay_samples = (base_delay + depth * (max_delay - base_delay) * (lfo + 1) / 2) * self.sample_rate
        delay_samples = delay_samples.astype(int)
        
        # Apply variable delay with feedback
        delayed_signal = self._apply_variable_delay(audio_data, delay_samples)
        
        # Add feedback
        if feedback > 0:
            for i in range(1, len(delayed_signal)):
                delayed_signal[i] += delayed_signal[i-1] * feedback * 0.1
        
        # Mix with original
        flanger_output = audio_data + delayed_signal * 0.5
        
        return flanger_output
    
    def apply_phaser(self, audio_data: np.ndarray, rate: float = 0.5, 
                    depth: float = 0.6, stages: int = 6) -> np.ndarray:
        """🌀 Apply phaser effect using all-pass filters"""
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        # Create LFO
        lfo = np.sin(2 * np.pi * rate * np.arange(len(audio_data)) / self.sample_rate)
        
        # Base frequency for all-pass filters
        base_freq = 1000  # Hz
        mod_range = 2000  # Hz
        
        phased_output = audio_data.copy()
        
        for channel in range(audio_data.shape[1]):
            signal_to_process = audio_data[:, channel]
            
            # Apply cascaded all-pass filters
            for stage in range(stages):
                # Calculate modulated frequency
                mod_freq = base_freq + depth * mod_range * lfo
                mod_freq = np.clip(mod_freq, 100, self.sample_rate/2 - 1000)
                
                # Apply all-pass filter (simplified)
                signal_to_process = self._apply_modulated_allpass(signal_to_process, mod_freq)
            
            phased_output[:, channel] = signal_to_process
        
        # Mix with original
        result = 0.7 * audio_data + 0.3 * phased_output
        
        return result
    
    def _apply_variable_delay(self, audio_data: np.ndarray, delay_samples: np.ndarray) -> np.ndarray:
        """Apply variable delay using interpolation"""
        delayed_output = np.zeros_like(audio_data)
        
        for channel in range(audio_data.shape[1]):
            signal = audio_data[:, channel]
            
            for i in range(len(signal)):
                delay = min(int(delay_samples[i]), i)
                if delay > 0:
                    delayed_output[i, channel] = signal[i - delay]
                else:
                    delayed_output[i, channel] = signal[i]
        
        return delayed_output
    
    def _apply_modulated_allpass(self, signal: np.ndarray, mod_freq: np.ndarray) -> np.ndarray:
        """Apply modulated all-pass filter"""
        # Simplified all-pass filter implementation
        # In practice, this would use proper digital filter design
        output = signal.copy()
        
        # Simple delay-based all-pass approximation
        for i in range(1, len(signal)):
            freq = mod_freq[i] if isinstance(mod_freq, np.ndarray) else mod_freq
            delay_factor = 1000.0 / max(freq, 100)  # Simplified relationship
            
            if i > int(delay_factor):
                output[i] = signal[i] + 0.7 * signal[i - int(delay_factor)]
        
        return output


class CreativeProcessor:
    """🎨 Creative Audio Effects Processor"""
    
    def __init__(self, sample_rate -> None: int = 44100, quality_level -> None: QualityLevel = QualityLevel.HIGH) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.quality_level = quality_level
        self.processing_times = []
    
    def apply_distortion(self, audio_data: np.ndarray, drive: float = 2.0, 
                        tone: float = 0.5, type: str = "tube") -> np.ndarray:
        """🎸 Apply various types of distortion"""
        start_time = time.time()
        
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        distorted_output = audio_data.copy()
        
        if type == "tube":
            distorted_output = self._apply_tube_distortion(distorted_output, drive, tone)
        elif type == "transistor":
            distorted_output = self._apply_transistor_distortion(distorted_output, drive, tone)
        elif type == "digital":
            distorted_output = self._apply_digital_distortion(distorted_output, drive, tone)
        elif type == "fuzz":
            distorted_output = self._apply_fuzz_distortion(distorted_output, drive, tone)
        
        self.processing_times.append(time.time() - start_time)
        return distorted_output
    
    def _apply_tube_distortion(self, audio_data: np.ndarray, drive: float, tone: float) -> np.ndarray:
        """Apply tube-style soft saturation"""
        # Soft saturation curve
        gained_signal = audio_data * drive
        
        # Tube-style asymmetric saturation
        positive_mask = gained_signal > 0
        negative_mask = gained_signal < 0
        
        result = gained_signal.copy()
        result[positive_mask] = np.tanh(gained_signal[positive_mask] * 0.8)
        result[negative_mask] = np.tanh(gained_signal[negative_mask] * 1.2) * 0.9
        
        # Apply tone control
        result = self._apply_tone_control(result, tone)
        
        return result / drive
    
    def _apply_transistor_distortion(self, audio_data: np.ndarray, drive: float, tone: float) -> np.ndarray:
        """Apply transistor-style hard clipping"""
        gained_signal = audio_data * drive
        
        # Hard clipping with slight rounding
        threshold = 0.7
        clipped_signal = np.clip(gained_signal, -threshold, threshold)
        
        # Add some softness to the clipping
        mask = np.abs(gained_signal) > threshold
        clipped_signal[mask] = np.sign(gained_signal[mask]) * (threshold + 
                              0.1 * np.tanh((np.abs(gained_signal[mask]) - threshold) * 5))
        
        # Apply tone control
        result = self._apply_tone_control(clipped_signal, tone)
        
        return result / drive
    
    def _apply_digital_distortion(self, audio_data: np.ndarray, drive: float, tone: float) -> np.ndarray:
        """Apply digital distortion (bit crushing effect)"""
        gained_signal = audio_data * drive
        
        # Bit reduction
        bit_depth = max(1, 16 - int(drive * 4))  # Reduce bits based on drive
        max_val = 2 ** (bit_depth - 1)
        
        # Quantize signal
        quantized = np.round(gained_signal * max_val) / max_val
        
        # Apply tone control
        result = self._apply_tone_control(quantized, tone)
        
        return result / drive
    
    def _apply_fuzz_distortion(self, audio_data: np.ndarray, drive: float, tone: float) -> np.ndarray:
        """Apply fuzz-style heavy distortion"""
        gained_signal = audio_data * drive
        
        # Extreme saturation
        fuzzed_signal = np.sign(gained_signal) * (1 - np.exp(-np.abs(gained_signal) * 3))
        
        # Add some harmonic content
        fuzzed_signal += 0.1 * np.sin(gained_signal * 6.28 * 2)  # 2nd harmonic
        fuzzed_signal += 0.05 * np.sin(gained_signal * 6.28 * 3)  # 3rd harmonic
        
        # Apply tone control
        result = self._apply_tone_control(fuzzed_signal, tone)
        
        return result / drive
    
    def _apply_tone_control(self, audio_data: np.ndarray, tone: float) -> np.ndarray:
        """Apply simple tone control"""
        if abs(tone - 0.5) < 0.01:
            return audio_data
        
        result = audio_data.copy()
        
        for channel in range(audio_data.shape[1]):
            if tone > 0.5:
                # Emphasize highs
                cutoff = 1000 + (tone - 0.5) * 8000
                sos = signal.butter(2, cutoff, 'highpass', fs=self.sample_rate, output='sos')
                high_passed = signal.sosfilt(sos, audio_data[:, channel])
                result[:, channel] = (1 - (tone - 0.5)) * audio_data[:, channel] + (tone - 0.5) * high_passed
            else:
                # Emphasize lows
                cutoff = 8000 - (0.5 - tone) * 6000
                sos = signal.butter(2, cutoff, 'lowpass', fs=self.sample_rate, output='sos')
                low_passed = signal.sosfilt(sos, audio_data[:, channel])
                result[:, channel] = tone * audio_data[:, channel] + (0.5 - tone) * low_passed
        
        return result
    
    def apply_bitcrusher(self, audio_data: np.ndarray, bit_depth: int = 8, 
                        sample_rate_reduction: float = 1.0) -> np.ndarray:
        """🔩 Apply bit crushing effect"""
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        # Bit depth reduction
        max_val = 2 ** (bit_depth - 1)
        quantized = np.round(audio_data * max_val) / max_val
        
        # Sample rate reduction
        if sample_rate_reduction > 1:
            reduced_length = int(len(audio_data) / sample_rate_reduction)
            downsampled = signal.resample(quantized, reduced_length, axis=0)
            result = signal.resample(downsampled, len(audio_data), axis=0)
        else:
            result = quantized
        
        return result


class VintageProcessor:
    """🎸 Vintage Hardware Modeling Processor"""
    
    def __init__(self, sample_rate -> None: int = 44100, quality_level -> None: QualityLevel = QualityLevel.HIGH) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.quality_level = quality_level
        self.processing_times = []
        
        # Load vintage modeling curves
        self._init_vintage_curves()
    
    def _init_vintage_curves(self) -> None:
        """Initialize vintage modeling curves"""
        # Frequency response curves for different vintage equipment
        self.vintage_curves = {
            'tube': {
                'low_shelf': {'freq': 100, 'gain': 0.5},
                'high_shelf': {'freq': 8000, 'gain': -0.3},
                'presence': {'freq': 3000, 'gain': 0.8, 'q': 1.5}
            },
            'tape': {
                'low_shelf': {'freq': 50, 'gain': 0.3},
                'high_roll': {'freq': 15000, 'gain': -1.5},
                'wow_flutter': {'rate': 0.2, 'depth': 0.1}
            },
            'vinyl': {
                'rumble': {'freq': 30, 'gain': -6},
                'high_roll': {'freq': 12000, 'gain': -2},
                'crackle_level': 0.02
            }
        }
    
    def apply_vintage_modeling(self, audio_data: np.ndarray, model_type: str = "tube",
                              saturation: float = 0.3, harmonic_enhancement: float = 0.2) -> np.ndarray:
        """🎸 Apply vintage hardware modeling"""
        start_time = time.time()
        
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        if model_type == "tube":
            result = self._apply_tube_modeling(audio_data, saturation, harmonic_enhancement)
        elif model_type == "tape":
            result = self._apply_tape_modeling(audio_data, saturation, harmonic_enhancement)
        elif model_type == "vinyl":
            result = self._apply_vinyl_modeling(audio_data, saturation, harmonic_enhancement)
        else:
            result = audio_data
        
        self.processing_times.append(time.time() - start_time)
        return result
    
    def _apply_tube_modeling(self, audio_data: np.ndarray, saturation: float, 
                           harmonic_enhancement: float) -> np.ndarray:
        """Apply tube amplifier modeling"""
        result = audio_data.copy()
        
        # Apply frequency response curve
        curve = self.vintage_curves['tube']
        
        for channel in range(audio_data.shape[1]):
            signal = audio_data[:, channel]
            
            # Low shelf boost
            sos_low = signal.butter(2, curve['low_shelf']['freq'], 'highpass', 
                                  fs=self.sample_rate, output='sos')
            low_boosted = signal.sosfilt(sos_low, signal) * curve['low_shelf']['gain']
            
            # High shelf cut
            sos_high = signal.butter(2, curve['high_shelf']['freq'], 'lowpass', 
                                   fs=self.sample_rate, output='sos')
            high_cut = signal.sosfilt(sos_high, signal) * abs(curve['high_shelf']['gain'])
            
            # Presence boost
            # Simplified peaking filter
            w = 2 * np.pi * curve['presence']['freq'] / self.sample_rate
            Q = curve['presence']['q']
            A = 10 ** (curve['presence']['gain'] / 40)
            alpha = np.sin(w) / (2 * Q)
            
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w)
            a2 = 1 - alpha / A
            
            b = np.array([b0, b1, b2]) / a0
            a = np.array([1, a1/a0, a2/a0])
            
            presence_boosted = signal.lfilter(b, a, signal)
            
            # Combine frequency shaping
            shaped_signal = signal + low_boosted * 0.3 - high_cut * 0.3 + presence_boosted * 0.2
            
            # Apply tube saturation
            saturated_signal = self._apply_tube_saturation(shaped_signal, saturation)
            
            # Add harmonic enhancement
            if harmonic_enhancement > 0:
                saturated_signal = self._add_tube_harmonics(saturated_signal, harmonic_enhancement)
            
            result[:, channel] = saturated_signal
        
        return result
    
    def _apply_tube_saturation(self, signal: np.ndarray, amount: float) -> np.ndarray:
        """Apply tube-style soft saturation"""
        # Asymmetric saturation characteristic of tubes
        positive_mask = signal > 0
        negative_mask = signal < 0
        
        saturated = signal.copy()
        
        # Positive half - softer saturation
        saturated[positive_mask] = np.tanh(signal[positive_mask] * (1 + amount)) / (1 + amount)
        
        # Negative half - slightly harder saturation
        saturated[negative_mask] = np.tanh(signal[negative_mask] * (1 + amount * 1.2)) / (1 + amount * 1.2)
        
        return saturated
    
    def _add_tube_harmonics(self, signal: np.ndarray, amount: float) -> np.ndarray:
        """Add harmonic content characteristic of tubes"""
        # Even harmonics (2nd, 4th) are more prominent in tubes
        harmonics = signal.copy()
        
        # 2nd harmonic
        harmonics += amount * 0.1 * np.sin(signal * 2 * np.pi)
        
        # 3rd harmonic (smaller amount)
        harmonics += amount * 0.05 * np.sin(signal * 3 * np.pi)
        
        # 4th harmonic
        harmonics += amount * 0.03 * np.sin(signal * 4 * np.pi)
        
        return harmonics
    
    def _apply_tape_modeling(self, audio_data: np.ndarray, saturation: float,
                           harmonic_enhancement: float) -> np.ndarray:
        """Apply tape machine modeling"""
        result = audio_data.copy()
        
        curve = self.vintage_curves['tape']
        
        for channel in range(audio_data.shape[1]):
            signal = audio_data[:, channel]
            
            # Tape frequency response
            # Low shelf boost
            sos_low = signal.butter(2, curve['low_shelf']['freq'], 'highpass', 
                                  fs=self.sample_rate, output='sos')
            low_boosted = signal.sosfilt(sos_low, signal) * curve['low_shelf']['gain']
            
            # High frequency roll-off
            sos_high = signal.butter(2, curve['high_roll']['freq'], 'lowpass', 
                                   fs=self.sample_rate, output='sos')
            high_rolled = signal.sosfilt(sos_high, signal)
            
            # Combine frequency shaping
            shaped_signal = signal + low_boosted * 0.3
            shaped_signal = high_rolled * 0.7 + shaped_signal * 0.3
            
            # Apply tape saturation (different from tube)
            saturated_signal = self._apply_tape_saturation(shaped_signal, saturation)
            
            # Add wow and flutter
            if 'wow_flutter' in curve:
                saturated_signal = self._add_wow_flutter(saturated_signal, 
                                                       curve['wow_flutter']['rate'],
                                                       curve['wow_flutter']['depth'])
            
            result[:, channel] = saturated_signal
        
        return result
    
    def _apply_tape_saturation(self, signal: np.ndarray, amount: float) -> np.ndarray:
        """Apply tape-style saturation"""
        # Tape has a more symmetric saturation than tubes
        saturated = np.tanh(signal * (1 + amount * 2)) / (1 + amount * 2)
        
        # Add some compression effect
        compressed = self._simple_compressor(saturated, threshold=0.7, ratio=2.0)
        
        return compressed
    
    def _add_wow_flutter(self, signal: np.ndarray, rate: float, depth: float) -> np.ndarray:
        """Add wow and flutter effects"""
        # Create modulation LFO
        lfo = np.sin(2 * np.pi * rate * np.arange(len(signal)) / self.sample_rate)
        
        # Apply pitch modulation (simplified)
        modulated_signal = signal.copy()
        
        for i in range(1, len(signal)):
            mod_amount = depth * lfo[i] * 0.01  # Small pitch variations
            delay_samples = int(mod_amount * self.sample_rate / 100)  # Convert to delay
            
            if i + delay_samples < len(signal) and delay_samples > 0:
                modulated_signal[i] = signal[i + delay_samples]
            elif i + delay_samples >= 0 and delay_samples < 0:
                modulated_signal[i] = signal[i + delay_samples]
        
        return modulated_signal
    
    def _apply_vinyl_modeling(self, audio_data: np.ndarray, saturation: float,
                            harmonic_enhancement: float) -> np.ndarray:
        """Apply vinyl record modeling"""
        result = audio_data.copy()
        
        curve = self.vintage_curves['vinyl']
        
        for channel in range(audio_data.shape[1]):
            signal = audio_data[:, channel]
            
            # Vinyl frequency response
            # Rumble filter
            sos_rumble = signal.butter(4, curve['rumble']['freq'], 'highpass', 
                                     fs=self.sample_rate, output='sos')
            rumble_filtered = signal.sosfilt(sos_rumble, signal)
            
            # High frequency roll-off
            sos_high = signal.butter(2, curve['high_roll']['freq'], 'lowpass', 
                                   fs=self.sample_rate, output='sos')
            high_rolled = signal.sosfilt(sos_high, rumble_filtered)
            
            # Add vinyl crackle and pop
            crackle = self._generate_vinyl_crackle(len(signal), curve['crackle_level'])
            
            result[:, channel] = high_rolled + crackle
        
        return result
    
    def _generate_vinyl_crackle(self, length: int, level: float) -> np.ndarray:
        """Generate vinyl crackle and pop noise"""
        # Generate random noise for crackle
        noise = np.random.normal(0, level, length)
        
        # Filter noise to typical crackle frequency range
        sos_crackle = signal.butter(2, [2000, 8000], 'bandpass', 
                                  fs=self.sample_rate, output='sos')
        filtered_noise = signal.sosfilt(sos_crackle, noise)
        
        # Add occasional pops
        pop_probability = 0.0001  # Very low probability
        pops = np.random.random(length) < pop_probability
        pop_signal = pops * np.random.normal(0, level * 10, length)
        
        return filtered_noise + pop_signal
    
    def _simple_compressor(self, signal: np.ndarray, threshold: float, ratio: float) -> np.ndarray:
        """Simple compressor for modeling"""
        compressed = signal.copy()
        
        for i in range(len(signal)):
            if abs(signal[i]) > threshold:
                excess = abs(signal[i]) - threshold
                compressed[i] = np.sign(signal[i]) * (threshold + excess / ratio)
        
        return compressed


class DynamicsProcessor:
    """🎛️ Advanced Dynamics Processing"""
    
    def __init__(self, sample_rate -> None: int = 44100, quality_level -> None: QualityLevel = QualityLevel.HIGH) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.quality_level = quality_level
        self.processing_times = []
    
    def apply_gate(self, audio_data: np.ndarray, threshold: float = -40.0,
                  attack: float = 0.001, release: float = 0.1) -> np.ndarray:
        """🚪 Apply noise gate"""
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        # Convert threshold to linear
        threshold_linear = 10 ** (threshold / 20)
        
        # Calculate envelope
        envelope = self._calculate_envelope(audio_data, attack, release)
        
        # Apply gating
        gate_signal = envelope > threshold_linear
        gate_signal = gate_signal.astype(float)
        
        # Smooth gate transitions
        gate_signal = self._smooth_gate(gate_signal, attack, release)
        
        # Apply gate
        result = audio_data * gate_signal.reshape(-1, 1)
        
        return result
    
    def apply_expander(self, audio_data: np.ndarray, threshold: float = -30.0,
                      ratio: float = 2.0, attack: float = 0.003, release: float = 0.1) -> np.ndarray:
        """📈 Apply expander"""
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(-1, 1)
        
        # Convert threshold to linear
        threshold_linear = 10 ** (threshold / 20)
        
        # Calculate envelope
        envelope = self._calculate_envelope(audio_data, attack, release)
        
        # Calculate expansion
        expansion_gain = np.ones_like(envelope)
        below_threshold = envelope < threshold_linear
        
        # Apply expansion ratio below threshold
        expansion_gain[below_threshold] = (envelope[below_threshold] / threshold_linear) ** (1/ratio - 1)
        
        # Apply expansion
        result = audio_data * expansion_gain.reshape(-1, 1)
        
        return result
    
    def _calculate_envelope(self, audio_data: np.ndarray, attack: float, release: float) -> np.ndarray:
        """Calculate RMS envelope"""
        # RMS calculation with attack/release
        rms_window = int(0.01 * self.sample_rate)  # 10ms window
        envelope = np.zeros(audio_data.shape[0])
        
        # Calculate RMS
        for i in range(audio_data.shape[0]):
            start_idx = max(0, i - rms_window // 2)
            end_idx = min(audio_data.shape[0], i + rms_window // 2)
            window_data = audio_data[start_idx:end_idx]
            envelope[i] = np.sqrt(np.mean(np.sum(window_data ** 2, axis=1)))
        
        # Apply attack/release smoothing
        smoothed_envelope = np.zeros_like(envelope)
        attack_coeff = np.exp(-1.0 / (attack * self.sample_rate))
        release_coeff = np.exp(-1.0 / (release * self.sample_rate))
        
        for i in range(1, len(envelope)):
            if envelope[i] > smoothed_envelope[i-1]:
                # Attack
                smoothed_envelope[i] = envelope[i] + (smoothed_envelope[i-1] - envelope[i]) * attack_coeff
            else:
                # Release
                smoothed_envelope[i] = envelope[i] + (smoothed_envelope[i-1] - envelope[i]) * release_coeff
        
        return smoothed_envelope
    
    def _smooth_gate(self, gate_signal: np.ndarray, attack: float, release: float) -> np.ndarray:
        """Smooth gate transitions"""
        smoothed_gate = np.zeros_like(gate_signal)
        attack_coeff = np.exp(-1.0 / (attack * self.sample_rate))
        release_coeff = np.exp(-1.0 / (release * self.sample_rate))
        
        for i in range(1, len(gate_signal)):
            target = gate_signal[i]
            if target > smoothed_gate[i-1]:
                # Opening
                smoothed_gate[i] = target + (smoothed_gate[i-1] - target) * attack_coeff
            else:
                # Closing
                smoothed_gate[i] = target + (smoothed_gate[i-1] - target) * release_coeff
        
        return smoothed_gate


# Export all classes
__all__ = [
    # Core Classes
    'AudioEffectsEngine', 'EffectType', 'QualityLevel', 'ProcessingMode',
    'EffectParameters', 'EffectChain', 'ConvolutionIR', 'VintageModelingParams',
    
    # Processor Classes
    'EqualizerProcessor', 'CompressorProcessor', 'ReverbProcessor',
    'SpatialProcessor', 'ModulationProcessor', 'CreativeProcessor',
    'VintageProcessor', 'DynamicsProcessor',
    
    # Legacy Classes (for compatibility)
    'ChorusProcessor', 'DistortionProcessor', 'AudioMixer', 'MasteringProcessor'
]
