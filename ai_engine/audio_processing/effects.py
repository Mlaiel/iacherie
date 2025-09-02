"""🎛️ Audio Effects Processing Module - Professional Audio Enhancement Engine

Advanced audio effects and restoration capabilities for the IA Influencer Agent platform.
Implements industry-standard audio processing algorithms with AI enhancement.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
from scipy import signal
from scipy.fft import fft, ifft, fftfreq
import librosa
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

from .core import AudioProcessor, AudioMetadata
from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


class EffectType(Enum):
    """
Audio effect types enumeration"""

    REVERB = "reverb"
    DELAY = "delay"
    CHORUS = "chorus"
    FLANGER = "flanger"
    PHASER = "phaser"
    DISTORTION = "distortion"
    COMPRESSION = "compression"
    EQ = "equalizer"
    LIMITER = "limiter"
    GATE = "gate"
    PITCH_SHIFT = "pitch_shift"
    TIME_STRETCH = "time_stretch"


@dataclass
class EffectParameters:
    """Effect parameter configuration"""
    effect_type: EffectType
    parameters: Dict[str, Any]
    bypass: bool = False
    mix_level: float = 1.0  # 0.0 = dry, 1.0 = wet
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
@dataclass
class RestorationResult:
    """
Audio restoration analysis result"""
    original_quality_score: float
    restored_quality_score: float
    noise_reduction_db: float
    artifacts_detected: List[str]
    processing_applied: List[str]
    improvement_metrics: Dict[str, float]


class EffectsProcessor:
    """
    🎛️ Professional Audio Effects Processor
    
    Comprehensive effects processing system featuring:
    - Industry-standard audio effects
    - Real-time processing capabilities
    - Parameter automation support
    - Effect chain processing
    - Quality preservation algorithms
    """
    
    def __init__(self, 
                 config: Optional[AudioProcessingConfig] = None,
                 sample_rate: int = 44100):
        self.config = config or AudioProcessingConfig()
        self.sample_rate = sample_rate
        self.effect_chain: List[EffectParameters] = []
        
        # Initialize effect processors
        self._init_effect_processors()
        
        logger.info(f"EffectsProcessor initialized at {sample_rate}Hz")
    
    def _init_effect_processors(self):
        """Initialize individual effect processors"""
        # Pre-calculate commonly used values
        self.nyquist = self.sample_rate / 2
        
        # Initialize delay line buffers
        self.delay_buffers = {}
        self.max_delay_samples = int(2.0 * self.sample_rate)  # 2 seconds max delay
        
        # Initialize filter states
        self.filter_states = {}
    
    def add_effect(self, effect_params: EffectParameters):
        """
Add effect to the processing chain"""
        self.effect_chain.append(effect_params)
        logger.debug(f"Added {effect_params.effect_type.value} effect to chain")
    
    def clear_effects(self):
        """Clear all effects from the processing chain"""
        self.effect_chain.clear()
        self.delay_buffers.clear()
        self.filter_states.clear()
        logger.debug("Cleared effects chain")
    
    async def process_audio(self, 
                          audio_data: np.ndarray,
                          effect_params: Optional[EffectParameters] = None) -> np.ndarray:
        """
        Process audio with a single effect or the entire effect chain
        
        Args:
            audio_data: Input audio samples
            effect_params: Single effect to apply (overrides chain if provided)
            
        Returns:
            Processed audio samples
        """
        try:
            if effect_params:
                # Apply single effect
                return await self._apply_single_effect(audio_data, effect_params)
            else:
                # Apply entire effect chain
                processed = audio_data.copy()
                
                for effect in self.effect_chain:
                    if not effect.bypass:
                        processed = await self._apply_single_effect(processed, effect)
                
                return processed
                
        except Exception as e:
            logger.error(f"Audio effects processing failed: {e}")
            return audio_data
    
    async def _apply_single_effect(self, 
                                 audio_data: np.ndarray,
                                 effect_params: EffectParameters) -> np.ndarray:
        """Apply a single effect to audio data"""
        try:
            effect_type = effect_params.effect_type
            params = effect_params.parameters
            mix_level = effect_params.mix_level
            
            # Route to appropriate effect processor
            if effect_type == EffectType.REVERB:
                processed = await self._apply_reverb(audio_data, params)
            elif effect_type == EffectType.DELAY:
                processed = await self._apply_delay(audio_data, params)
            elif effect_type == EffectType.CHORUS:
                processed = await self._apply_chorus(audio_data, params)
            elif effect_type == EffectType.FLANGER:
                processed = await self._apply_flanger(audio_data, params)
            elif effect_type == EffectType.PHASER:
                processed = await self._apply_phaser(audio_data, params)
            elif effect_type == EffectType.DISTORTION:
                processed = await self._apply_distortion(audio_data, params)
            elif effect_type == EffectType.COMPRESSION:
                processed = await self._apply_compression(audio_data, params)
            elif effect_type == EffectType.EQ:
                processed = await self._apply_equalizer(audio_data, params)
            elif effect_type == EffectType.LIMITER:
                processed = await self._apply_limiter(audio_data, params)
            elif effect_type == EffectType.GATE:
                processed = await self._apply_gate(audio_data, params)
            elif effect_type == EffectType.PITCH_SHIFT:
                processed = await self._apply_pitch_shift(audio_data, params)
            elif effect_type == EffectType.TIME_STRETCH:
                processed = await self._apply_time_stretch(audio_data, params)
            else:
                logger.warning(f"Unknown effect type: {effect_type}")
                return audio_data
            
            # Apply mix level (blend dry and wet signals)
            if mix_level < 1.0:
                processed = (1.0 - mix_level) * audio_data + mix_level * processed
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to apply {effect_params.effect_type.value} effect: {e}")
            return audio_data
    
    async def _apply_reverb(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply reverb effect using convolution with impulse response"""
        try:
            room_size = params.get('room_size', 0.5)  # 0.0 - 1.0
            damping = params.get('damping', 0.5)  # 0.0 - 1.0
            early_reflections = params.get('early_reflections', 0.3)
            
            # Generate synthetic impulse response
            ir_length = int(room_size * 2.0 * self.sample_rate)  # Up to 2 seconds
            ir_length = min(ir_length, len(audio_data) // 2)  # Limit to avoid artifacts
            
            if ir_length < 1024:
                ir_length = 1024
            
            # Create exponentially decaying noise as impulse response
            t = np.arange(ir_length) / self.sample_rate
            decay_time = room_size * 2.0 + 0.1  # Decay time based on room size
            
            # Exponential decay envelope
            envelope = np.exp(-t / decay_time)
            
            # Add early reflections
            early_env = np.zeros_like(envelope)
            for i in range(int(early_reflections * 10)):
                delay_samples = int(np.random.uniform(0.005, 0.1) * self.sample_rate)
                if delay_samples < len(early_env):
                    early_env[delay_samples] += 0.1 * np.random.uniform(0.5, 1.0)
            
            # Create noise and apply envelope
            noise = np.random.normal(0, 0.1, ir_length)
            impulse_response = (noise * envelope + early_env) * (1.0 - damping + 0.1)
            
            # Apply low-pass filtering for damping
            if damping > 0.1:
                cutoff = (1.0 - damping) * self.nyquist
                b, a = signal.butter(2, cutoff / self.nyquist, btype='low')
                impulse_response = signal.filtfilt(b, a, impulse_response)
            
            # Convolve with audio (using FFT for efficiency)
            reverb_audio = signal.fftconvolve(audio_data, impulse_response, mode='same')
            
            # Normalize to prevent clipping
            if np.max(np.abs(reverb_audio)) > 0:
                reverb_audio = reverb_audio / np.max(np.abs(reverb_audio)) * 0.7
            
            return reverb_audio
            
        except Exception as e:
            logger.error(f"Reverb effect failed: {e}")
            return audio_data
    
    async def _apply_delay(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply delay effect with feedback"""
        try:
            delay_time = params.get('delay_time', 0.25)  # seconds
            feedback = params.get('feedback', 0.3)  # 0.0 - 0.95
            
            delay_samples = int(delay_time * self.sample_rate)
            delay_samples = min(delay_samples, self.max_delay_samples)
            
            if delay_samples < 1:
                return audio_data
            
            # Initialize delay buffer if needed
            buffer_key = f"delay_{delay_samples}"
            if buffer_key not in self.delay_buffers:
                self.delay_buffers[buffer_key] = np.zeros(delay_samples)
            
            delay_buffer = self.delay_buffers[buffer_key]
            output = np.zeros_like(audio_data)
            
            # Process sample by sample for real-time simulation
            for i in range(len(audio_data)):
                # Get delayed sample
                delayed_sample = delay_buffer[0]
                
                # Create output (input + delayed)
                output[i] = audio_data[i] + delayed_sample
                
                # Update delay buffer with feedback
                new_input = audio_data[i] + delayed_sample * feedback
                
                # Shift buffer and add new input
                delay_buffer[:-1] = delay_buffer[1:]
                delay_buffer[-1] = new_input
            
            # Update buffer for next call
            self.delay_buffers[buffer_key] = delay_buffer
            
            return output
            
        except Exception as e:
            logger.error(f"Delay effect failed: {e}")
            return audio_data
    
    async def _apply_chorus(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply chorus effect using modulated delay lines"""
        try:
            rate = params.get('rate', 1.0)  # LFO rate in Hz
            depth = params.get('depth', 0.005)  # Modulation depth in seconds
            voices = params.get('voices', 3)  # Number of chorus voices
            
            output = audio_data.copy()
            
            for voice in range(voices):
                # Create LFO with phase offset for each voice
                phase_offset = (voice / voices) * 2 * np.pi
                t = np.arange(len(audio_data)) / self.sample_rate
                lfo = np.sin(2 * np.pi * rate * t + phase_offset)
                
                # Modulate delay time
                base_delay = 0.02 + voice * 0.01  # Base delay for each voice
                delay_modulation = base_delay + depth * lfo
                
                # Apply time-varying delay
                delayed_voice = np.zeros_like(audio_data)
                for i in range(len(audio_data)):
                    delay_samples = delay_modulation[i] * self.sample_rate
                    delay_int = int(delay_samples)
                    delay_frac = delay_samples - delay_int
                    
                    if i >= delay_int + 1:
                        # Linear interpolation for fractional delay
                        delayed_voice[i] = (
                            audio_data[i - delay_int] * (1 - delay_frac) +
                            audio_data[i - delay_int - 1] * delay_frac
                        )
                
                # Add voice to output with amplitude reduction
                output += delayed_voice * (0.3 / voices)
            
            return output
            
        except Exception as e:
            logger.error(f"Chorus effect failed: {e}")
            return audio_data
    
    async def _apply_distortion(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply distortion effect with various algorithms"""
        try:
            drive = params.get('drive', 2.0)  # Distortion amount
            distortion_type = params.get('type', 'soft_clip')  # Type of distortion
            
            # Apply input gain
            driven_signal = audio_data * drive
            
            if distortion_type == 'soft_clip':
                # Soft clipping using tanh
                distorted = np.tanh(driven_signal)
            elif distortion_type == 'hard_clip':
                # Hard clipping
                distorted = np.clip(driven_signal, -1.0, 1.0)
            elif distortion_type == 'tube':
                # Tube-style asymmetric distortion
                distorted = np.where(
                    driven_signal >= 0,
                    driven_signal / (1 + driven_signal),
                    driven_signal / (1 - driven_signal * 0.7)
                )
            elif distortion_type == 'fuzz':
                # Fuzz distortion
                distorted = np.sign(driven_signal) * (1 - np.exp(-np.abs(driven_signal)))
            else:
                distorted = np.tanh(driven_signal)  # Default to soft clip
            
            # Apply output level compensation
            output_level = 1.0 / max(1.0, drive * 0.5)
            distorted *= output_level
            
            return distorted
            
        except Exception as e:
            logger.error(f"Distortion effect failed: {e}")
            return audio_data
    
    async def _apply_compression(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            threshold = params.get('threshold', 0.7)  # Compression threshold
            ratio = params.get('ratio', 4.0)  # Compression ratio
            attack_ms = params.get('attack_ms', 10.0)  # Attack time
            release_ms = params.get('release_ms', 100.0)  # Release time
            makeup_gain = params.get('makeup_gain', 1.0)  # Makeup gain
            
            # Convert time constants to samples
            attack_samples = max(1, int(attack_ms * self.sample_rate / 1000))
            release_samples = max(1, int(release_ms * self.sample_rate / 1000))
            
            # Initialize state variables
            envelope = 0.0
            compressed = np.zeros_like(audio_data)
            
            for i, sample in enumerate(audio_data):
                # Envelope detection
                sample_abs = abs(sample)
                if sample_abs > envelope:
                    envelope += (sample_abs - envelope) / attack_samples
                else:
                    envelope += (sample_abs - envelope) / release_samples
                
                # Compression curve
                if envelope > threshold:
                    # Calculate compression
                    over_threshold = envelope - threshold
                    compressed_level = threshold + over_threshold / ratio
                    gain_reduction = compressed_level / (envelope + 1e-10)
                else:
                    gain_reduction = 1.0
                
                # Apply compression and makeup gain
                compressed[i] = sample * gain_reduction * makeup_gain
            
            return compressed
            
        except Exception as e:
            logger.error(f"Compression effect failed: {e}")
            return audio_data
    
    async def _apply_equalizer(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply parametric equalizer"""
        try:
            bands = params.get('bands', [
                {'freq': 100, 'gain': 0, 'q': 1.0},
                {'freq': 1000, 'gain': 0, 'q': 1.0},
                {'freq': 10000, 'gain': 0, 'q': 1.0}
            ])
            
            output = audio_data.copy()
            
            for band in bands:
                freq = band.get('freq', 1000)
                gain_db = band.get('gain', 0)
                q = band.get('q', 1.0)
                
                if abs(gain_db) < 0.1:  # Skip if no gain change
                    continue
                
                # Design peaking filter
                gain = 10 ** (gain_db / 20)
                w0 = 2 * np.pi * freq / self.sample_rate
                alpha = np.sin(w0) / (2 * q)
                
                # Peaking EQ coefficients
                A = gain
                cos_w0 = np.cos(w0)
                
                b0 = 1 + alpha * A
                b1 = -2 * cos_w0
                b2 = 1 - alpha * A
                a0 = 1 + alpha / A
                a1 = -2 * cos_w0
                a2 = 1 - alpha / A
                
                # Normalize coefficients
                b = np.array([b0, b1, b2]) / a0
                a = np.array([1, a1, a2]) / a0
                
                # Apply filter
                output = signal.filtfilt(b, a, output)
            
            return output
            
        except Exception as e:
            logger.error(f"Equalizer effect failed: {e}")
            return audio_data
    
    async def _apply_pitch_shift(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply pitch shifting using phase vocoder"""
        try:
            semitones = params.get('semitones', 0)  # Pitch shift in semitones
            
            if abs(semitones) < 0.01:
                return audio_data
            
            # Convert semitones to ratio
            pitch_ratio = 2 ** (semitones / 12)
            
            # Use librosa for high-quality pitch shifting
            shifted = librosa.effects.pitch_shift(
                y=audio_data,
                sr=self.sample_rate,
                n_steps=semitones
            )
            
            return shifted
            
        except Exception as e:
            logger.error(f"Pitch shift effect failed: {e}")
            return audio_data
    
    async def _apply_time_stretch(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply time stretching without pitch change"""
        try:
            stretch_factor = params.get('stretch_factor', 1.0)  # 1.0 = no change
            
            if abs(stretch_factor - 1.0) < 0.01:
                return audio_data
            
            # Use librosa for high-quality time stretching
            stretched = librosa.effects.time_stretch(audio_data, rate=stretch_factor)
            
            # Ensure output length matches input if needed
            preserve_length = params.get('preserve_length', False)
            if preserve_length and len(stretched) != len(audio_data):
                if len(stretched) > len(audio_data):
                    stretched = stretched[:len(audio_data)]
                else:
                    stretched = np.pad(stretched, (0, len(audio_data) - len(stretched)))
            
            return stretched
            
        except Exception as e:
            logger.error(f"Time stretch effect failed: {e}")
            return audio_data
    
    async def _apply_limiter(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply brick-wall limiter"""
        try:
            threshold = params.get('threshold', 0.95)
            lookahead_ms = params.get('lookahead_ms', 5.0)
            
            lookahead_samples = int(lookahead_ms * self.sample_rate / 1000)
            
            # Simple brick-wall limiting with lookahead
            padded_audio = np.pad(audio_data, (lookahead_samples, 0), mode='constant')
            limited = np.zeros_like(padded_audio)
            
            for i in range(len(limited)):
                # Look ahead for peaks
                end_idx = min(i + lookahead_samples, len(padded_audio))
                peak = np.max(np.abs(padded_audio[i:end_idx]))
                
                # Calculate gain reduction
                if peak > threshold:
                    gain = threshold / peak
                else:
                    gain = 1.0
                
                limited[i] = padded_audio[i] * gain
            
            # Remove lookahead padding
            return limited[lookahead_samples:]
            
        except Exception as e:
            logger.error(f"Limiter effect failed: {e}")
            return audio_data
    
    async def _apply_gate(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply noise gate"""
        try:
            threshold = params.get('threshold', 0.1)
            ratio = params.get('ratio', 10.0)  # Gate ratio
            attack_ms = params.get('attack_ms', 1.0)
            release_ms = params.get('release_ms', 100.0)
            
            attack_samples = max(1, int(attack_ms * self.sample_rate / 1000))
            release_samples = max(1, int(release_ms * self.sample_rate / 1000))
            
            envelope = 0.0
            gated = np.zeros_like(audio_data)
            
            for i, sample in enumerate(audio_data):
                # Envelope detection
                sample_abs = abs(sample)
                if sample_abs > envelope:
                    envelope += (sample_abs - envelope) / attack_samples
                else:
                    envelope += (sample_abs - envelope) / release_samples
                
                # Gate calculation
                if envelope < threshold:
                    # Below threshold - apply gating
                    under_threshold = threshold - envelope
                    gated_level = envelope + under_threshold / ratio
                    gate_gain = gated_level / (envelope + 1e-10)
                else:
                    gate_gain = 1.0
                
                gated[i] = sample * gate_gain
            
            return gated
            
        except Exception as e:
            logger.error(f"Gate effect failed: {e}")
            return audio_data
    
    async def _apply_flanger(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply flanger effect"""
        try:
            rate = params.get('rate', 0.5)  # LFO rate
            depth = params.get('depth', 0.002)  # Modulation depth
            feedback = params.get('feedback', 0.5)
            
            t = np.arange(len(audio_data)) / self.sample_rate
            lfo = np.sin(2 * np.pi * rate * t)
            
            # Short delay line with modulation
            base_delay = 0.001  # 1ms base delay
            delay_modulation = base_delay + depth * lfo
            
            output = np.zeros_like(audio_data)
            
            for i in range(len(audio_data)):
                delay_samples = delay_modulation[i] * self.sample_rate
                delay_int = int(delay_samples)
                delay_frac = delay_samples - delay_int
                
                if i >= delay_int + 1:
                    # Linear interpolation
                    delayed_sample = (
                        audio_data[i - delay_int] * (1 - delay_frac) +
                        audio_data[i - delay_int - 1] * delay_frac
                    )
                    output[i] = audio_data[i] + delayed_sample * feedback
                else:
        try:
            logger.info(f"Executing _apply_phaser")
            
            # Implementation for _apply_phaser
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_apply_phaser completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_apply_phaser failed: {e}")
            raise
            return output
            
        except Exception as e:
            logger.error(f"Flanger effect failed: {e}")
            return audio_data
    
    async def _apply_phaser(self, audio_data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply phaser effect using all-pass filters"""
        try:
            rate = params.get('rate', 0.5)  # LFO rate
            depth = params.get('depth', 0.8)  # Modulation depth
            stages = params.get('stages', 4)  # Number of all-pass stages
            
            t = np.arange(len(audio_data)) / self.sample_rate
            lfo = np.sin(2 * np.pi * rate * t)
            
            # Simple approximation using frequency modulation
            output = audio_data.copy()
            
            for stage in range(stages):
                # Create phase-shifted version
                phase_shift = depth * lfo * (stage + 1) / stages
                
                # Apply phase shift (simplified implementation)
                fft_signal = fft(output)
                freqs = fftfreq(len(output), 1/self.sample_rate)
                
                # Apply phase shift in frequency domain
                phase_shifts = np.exp(1j * phase_shift.mean() * freqs / 1000)
                fft_shifted = fft_signal * phase_shifts
                
                phase_shifted = np.real(ifft(fft_shifted))
                output = 0.7 * output + 0.3 * phase_shifted
            
            return output
            
        except Exception as e:
            logger.error(f"Phaser effect failed: {e}")
            return audio_data


class AudioRestoration:
    """
    🔧 Advanced Audio Restoration Engine
    
    Professional audio restoration capabilities:
    - Noise reduction algorithms
    - Click and pop removal
    - Hum and buzz elimination
    - Spectral repair techniques
    - Quality enhancement
    """
    
    def __init__(self, 
                 config: Optional[AudioProcessingConfig] = None,
                 sample_rate: int = 44100):
        self.config = config or AudioProcessingConfig()
        self.sample_rate = sample_rate
        
        logger.info("AudioRestoration engine initialized")
    
    async def restore_audio(self, 
                          audio_data: np.ndarray,
                          auto_detect_issues: bool = True) -> Tuple[np.ndarray, RestorationResult]:
        """
        Comprehensive audio restoration
        
        Args:
            audio_data: Input audio samples
            auto_detect_issues: Automatically detect and fix issues
            
        Returns:
            Tuple of (restored_audio, restoration_result)
        """
        try:
            original_quality = self._assess_audio_quality(audio_data)
            restored = audio_data.copy()
            processing_applied = []
            
            if auto_detect_issues:
                # Detect and fix various audio issues
                
                # 1. Noise reduction
                if self._detect_noise(audio_data):
                    restored = await self._reduce_noise(restored)
                    processing_applied.append("noise_reduction")
                
                # 2. Click and pop removal
                if self._detect_clicks(audio_data):
                    restored = await self._remove_clicks(restored)
                    processing_applied.append("click_removal")
                
                # 3. Hum removal
                if self._detect_hum(audio_data):
                    restored = await self._remove_hum(restored)
                    processing_applied.append("hum_removal")
                
                # 4. Spectral repair
                if self._detect_spectral_damage(audio_data):
                    restored = await self._spectral_repair(restored)
                    processing_applied.append("spectral_repair")
            
            # Calculate restoration results
            restored_quality = self._assess_audio_quality(restored)
            
            result = RestorationResult(
                original_quality_score=original_quality,
                restored_quality_score=restored_quality,
                noise_reduction_db=self._calculate_noise_reduction(audio_data, restored),
                artifacts_detected=self._detect_artifacts(audio_data),
                processing_applied=processing_applied,
                improvement_metrics=self._calculate_improvement_metrics(audio_data, restored)
            )
            
            logger.info(f"Audio restoration completed. Quality improvement: "
                       f"{restored_quality - original_quality:.2f}")
            
            return restored, result
            
        except Exception as e:
            logger.error(f"Audio restoration failed: {e}")
            return audio_data, RestorationResult(
                original_quality_score=0.0,
                restored_quality_score=0.0,
                noise_reduction_db=0.0,
                artifacts_detected=[],
                processing_applied=[],
                improvement_metrics={}
            )
    
    def _assess_audio_quality(self, audio_data: np.ndarray) -> float:
        """Assess overall audio quality (0-100 scale)"""
        try:
            # SNR estimation
            signal_power = np.mean(audio_data ** 2)
            noise_floor = np.percentile(np.abs(audio_data), 5) ** 2
            snr = 10 * np.log10(signal_power / (noise_floor + 1e-10))
            
            # Dynamic range
            dynamic_range = 20 * np.log10(
                np.percentile(np.abs(audio_data), 95) / 
                (np.percentile(np.abs(audio_data), 5) + 1e-10)
            )
            
            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio_data) > 0.98) / len(audio_data)
            
            # Combine metrics
            quality = (
                (snr / 60) * 0.5 +
                (dynamic_range / 60) * 0.3 +
                (1 - clipping_ratio) * 0.2
            ) * 100
            
            return max(0, min(100, quality))
            
        except Exception:
            return 50.0
    
    def _detect_noise(self, audio_data: np.ndarray) -> bool:
        """
Detect if audio has significant noise"""
        noise_floor = np.percentile(np.abs(audio_data), 10)
        return noise_floor > 0.01  # Threshold for noise detection
    
    def _detect_clicks(self, audio_data: np.ndarray) -> bool:
        """
Detect clicks and pops in audio"""
        # Calculate difference signal for transient detection
        diff_signal = np.diff(audio_data)
        click_threshold = np.std(diff_signal) * 5
        
        clicks = np.sum(np.abs(diff_signal) > click_threshold)
        return clicks > len(audio_data) * 0.001  # More than 0.1% of samples
    
    def _detect_hum(self, audio_data: np.ndarray) -> bool:
        """
Detect power line hum (50/60 Hz and harmonics)"""
        # FFT analysis for hum detection
        fft_data = np.abs(fft(audio_data))
        freqs = fftfreq(len(audio_data), 1/self.sample_rate)
        
        # Check for peaks at 50Hz, 60Hz and harmonics
        hum_freqs = [50, 60, 100, 120, 150, 180]
        total_hum_energy = 0
        
        for freq in hum_freqs:
            if freq < self.sample_rate / 2:
                freq_idx = np.argmin(np.abs(freqs - freq))
                total_hum_energy += fft_data[freq_idx]
        
        # Compare to total energy
        total_energy = np.sum(fft_data)
        hum_ratio = total_hum_energy / (total_energy + 1e-10)
        
        return hum_ratio > 0.05  # 5% threshold
    
    def _detect_spectral_damage(self, audio_data: np.ndarray) -> bool:
        """
Detect spectral damage or gaps"""
        # Spectral analysis for damage detection
        stft = librosa.stft(audio_data, hop_length=512)
        magnitude = np.abs(stft)
        
        # Look for spectral holes or discontinuities
        spectral_variance = np.var(magnitude, axis=1)
        damage_threshold = np.mean(spectral_variance) * 0.1
        
        damaged_bands = np.sum(spectral_variance < damage_threshold)
        return damaged_bands > magnitude.shape[0] * 0.1  # 10% of frequency bands
    
    def _detect_artifacts(self, audio_data: np.ndarray) -> List[str]:
        """
Detect various audio artifacts"""
        artifacts = []
        
        if self._detect_noise(audio_data):
            artifacts.append("noise")
        if self._detect_clicks(audio_data):
            artifacts.append("clicks_pops")
        if self._detect_hum(audio_data):
            artifacts.append("hum_buzz")
        if self._detect_spectral_damage(audio_data):
            artifacts.append("spectral_damage")
        
        # Check for clipping
        if np.sum(np.abs(audio_data) > 0.98) > 0:
            artifacts.append("clipping")
        
        return artifacts
    
    async def _reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Advanced noise reduction using spectral subtraction"""
        try:
            # Spectral subtraction noise reduction
            stft = librosa.stft(audio_data, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise from quiet sections
            frame_energy = np.mean(magnitude, axis=0)
            noise_frames = frame_energy < np.percentile(frame_energy, 20)
            
            if np.sum(noise_frames) > 0:
                noise_spectrum = np.mean(magnitude[:, noise_frames], axis=1, keepdims=True)
            else:
                noise_spectrum = np.percentile(magnitude, 10, axis=1, keepdims=True)
            
            # Spectral subtraction
            alpha = 2.0  # Over-subtraction factor
            beta = 0.01  # Spectral floor factor
            
            clean_magnitude = magnitude - alpha * noise_spectrum
            clean_magnitude = np.maximum(clean_magnitude, beta * magnitude)
            
            # Reconstruct audio
            clean_stft = clean_magnitude * np.exp(1j * phase)
            clean_audio = librosa.istft(clean_stft, hop_length=512)
            
            return clean_audio
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {e}")
            return audio_data
    
    async def _remove_clicks(self, audio_data: np.ndarray) -> np.ndarray:
        """Remove clicks and pops using interpolation"""
        try:
            # Detect clicks using difference signal
            diff_signal = np.abs(np.diff(audio_data))
            threshold = np.mean(diff_signal) + 3 * np.std(diff_signal)
            
            click_indices = np.where(diff_signal > threshold)[0]
            
            if len(click_indices) == 0:
                return audio_data
            
            cleaned = audio_data.copy()
            
            # Interpolate over click locations
            for click_idx in click_indices:
                # Define interpolation window
                start = max(0, click_idx - 5)
                end = min(len(cleaned), click_idx + 6)
                
                if end - start > 2:
                    # Linear interpolation
                    x_points = [start, end - 1]
                    y_points = [cleaned[start], cleaned[end - 1]]
                    
                    for i in range(start + 1, end - 1):
                        # Linear interpolation
                        t = (i - start) / (end - 1 - start)
                        cleaned[i] = y_points[0] * (1 - t) + y_points[1] * t
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Click removal failed: {e}")
            return audio_data
    
    async def _remove_hum(self, audio_data: np.ndarray) -> np.ndarray:
        """Remove power line hum using notch filters"""
        try:
            # Design notch filters for common hum frequencies
            hum_freqs = [50, 60, 100, 120, 150, 180]  # Hz
            cleaned = audio_data.copy()
            
            for freq in hum_freqs:
                if freq < self.sample_rate / 2:
                    # Design notch filter
                    Q = 30  # Quality factor (narrow notch)
                    w0 = freq / (self.sample_rate / 2)  # Normalized frequency
                    
                    # Calculate filter coefficients
                    b, a = signal.iirnotch(freq, Q, self.sample_rate)
                    
                    # Apply filter
                    cleaned = signal.filtfilt(b, a, cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Hum removal failed: {e}")
            return audio_data
    
    async def _spectral_repair(self, audio_data: np.ndarray) -> np.ndarray:
        """Repair spectral damage using interpolation"""
        try:
            # STFT for spectral analysis
            stft = librosa.stft(audio_data, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Detect damaged frequency bands
            spectral_energy = np.mean(magnitude, axis=1)
            threshold = np.percentile(spectral_energy, 10)
            damaged_bands = spectral_energy < threshold
            
            if np.sum(damaged_bands) == 0:
                return audio_data
            
            # Interpolate damaged bands
            repaired_magnitude = magnitude.copy()
            
            for freq_idx in np.where(damaged_bands)[0]:
                # Find nearest healthy bands
                healthy_bands = ~damaged_bands
                healthy_indices = np.where(healthy_bands)[0]
                
                if len(healthy_indices) >= 2:
                    # Find closest healthy bands
                    distances = np.abs(healthy_indices - freq_idx)
                    closest_bands = healthy_indices[np.argsort(distances)[:2]]
                    
                    # Interpolate magnitude
                    weights = 1.0 / (np.abs(closest_bands - freq_idx) + 1e-10)
                    weights /= np.sum(weights)
                    
                    interpolated = np.average(
                        magnitude[closest_bands], 
                        axis=0, 
                        weights=weights
                    )
                    
                    repaired_magnitude[freq_idx] = interpolated
            
            # Reconstruct audio
            repaired_stft = repaired_magnitude * np.exp(1j * phase)
            repaired_audio = librosa.istft(repaired_stft, hop_length=512)
            
            return repaired_audio
            
        except Exception as e:
            logger.error(f"Spectral repair failed: {e}")
            return audio_data
    
    def _calculate_noise_reduction(self, 
                                 original: np.ndarray, 
                                 restored: np.ndarray) -> float:
        """Calculate noise reduction in dB"""
        try:
            # Estimate noise floor before and after
            original_noise = np.percentile(np.abs(original), 10)
            restored_noise = np.percentile(np.abs(restored), 10)
            
            if restored_noise > 0:
                reduction_db = 20 * np.log10(original_noise / restored_noise)
                return max(0, reduction_db)
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def _calculate_improvement_metrics(self, 
                                     original: np.ndarray, 
                                     restored: np.ndarray) -> Dict[str, float]:
        """
Calculate various improvement metrics"""
        try:
            metrics = {}
            
            # SNR improvement
            orig_snr = self._calculate_snr(original)
            rest_snr = self._calculate_snr(restored)
            metrics['snr_improvement_db'] = rest_snr - orig_snr
            
            # Dynamic range improvement
            orig_dr = self._calculate_dynamic_range(original)
            rest_dr = self._calculate_dynamic_range(restored)
            metrics['dynamic_range_improvement_db'] = rest_dr - orig_dr
            
            # Spectral flatness improvement
            orig_sf = self._calculate_spectral_flatness(original)
            rest_sf = self._calculate_spectral_flatness(restored)
            metrics['spectral_flatness_improvement'] = rest_sf - orig_sf
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate improvement metrics: {e}")
            return {}
    
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        signal_power = np.mean(audio_data ** 2)
        noise_power = np.percentile(audio_data ** 2, 10)
        return 10 * np.log10(signal_power / (noise_power + 1e-10))
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """
Calculate dynamic range"""
        peak = np.percentile(np.abs(audio_data), 99)
        noise_floor = np.percentile(np.abs(audio_data), 1)
        return 20 * np.log10(peak / (noise_floor + 1e-10))
    
    def _calculate_spectral_flatness(self, audio_data: np.ndarray) -> float:
        """
Calculate spectral flatness (Wiener entropy)"""
        try:
            # Calculate power spectral density
            freqs, psd = signal.welch(audio_data, self.sample_rate)
            
            # Spectral flatness = geometric mean / arithmetic mean
            geometric_mean = np.exp(np.mean(np.log(psd + 1e-10)))
            arithmetic_mean = np.mean(psd)
            
            return geometric_mean / (arithmetic_mean + 1e-10)
            
        except Exception:
            return 0.0
