"""
🎸 Distortion Processor - Professional Distortion & Overdrive Engine

Advanced distortion effects with multiple algorithms, tube modeling,
waveshaping, harmonic generation, and professional gain staging.
Includes vintage amp modeling and modern high-gain processing.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Optional, Dict, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
import scipy.signal
import scipy.interpolate
import threading


class DistortionType(Enum):
    """Distortion algorithm types"""
    OVERDRIVE = "overdrive"
    HARD_CLIP = "hard_clip"
    SOFT_CLIP = "soft_clip"
    TUBE = "tube"
    FUZZ = "fuzz"
    WAVESHAPER = "waveshaper"
    BITCRUSH = "bitcrush"
    SATURATION = "saturation"
    ASYMMETRIC = "asymmetric"


class FilterType(Enum):
    """Pre/Post filter types"""
    NONE = "none"
    LOW_PASS = "low_pass"
    HIGH_PASS = "high_pass"
    BAND_PASS = "band_pass"
    NOTCH = "notch"
    SHELF = "shelf"


@dataclass
class DistortionParams:
    """Distortion processor parameters"""
    distortion_type: DistortionType = DistortionType.OVERDRIVE
    drive: float = 5.0  # Input gain (0-20 dB)
    amount: float = 0.5  # Distortion amount (0-1)
    tone: float = 0.5  # Tone control (0-1)
    output_level: float = 0.0  # Output level (-20 to +20 dB)
    mix: float = 1.0  # Dry/wet mix (0-1)
    
    # Advanced parameters
    bias: float = 0.0  # DC bias for asymmetric distortion
    harmonics: float = 0.0  # Harmonic enhancement
    pre_filter_type: FilterType = FilterType.NONE
    pre_filter_freq: float = 1000.0
    post_filter_type: FilterType = FilterType.NONE
    post_filter_freq: float = 5000.0
    
    # Tube modeling
    tube_warmth: float = 0.5  # Tube warmth (0-1)
    tube_compression: float = 0.3  # Tube compression (0-1)
    
    # Bitcrusher
    bit_depth: int = 16  # Bit depth (1-16)
    sample_rate_reduction: float = 1.0  # Sample rate factor (0.1-1.0)


class WaveShapers:
    """Collection of waveshaping functions"""
    
    @staticmethod
    def hard_clip(x: np.ndarray, threshold: float = 1.0) -> np.ndarray:
        """Hard clipping waveshaper"""
        return np.clip(x, -threshold, threshold)
    
    @staticmethod
    def soft_clip(x: np.ndarray, threshold: float = 1.0) -> np.ndarray:
        """Soft clipping using tanh"""
        return np.tanh(x / threshold) * threshold
    
    @staticmethod
    def overdrive(x: np.ndarray, gain: float = 2.0) -> np.ndarray:
        """Overdrive waveshaper"""
        return x / (1.0 + abs(x * gain))
    
    @staticmethod
    def tube_saturation(x: np.ndarray, warmth: float = 0.5, compression: float = 0.3) -> np.ndarray:
        """Tube saturation modeling"""
        # Apply compression
        compressed = x / (1.0 + abs(x) * compression)
        
        # Apply warmth (even harmonics)
        warmed = compressed + warmth * (compressed ** 2) * np.sign(compressed)
        
        # Soft limiting
        return np.tanh(warmed * 0.7)
    
    @staticmethod
    def fuzz(x: np.ndarray, intensity: float = 2.0) -> np.ndarray:
        """Fuzz distortion"""
        # Extreme clipping with some filtering
        clipped = np.clip(x * intensity, -0.7, 0.7)
        
        # Add some high-frequency content
        return clipped + 0.1 * np.sign(clipped) * (1 - abs(clipped))
    
    @staticmethod
    def asymmetric(x: np.ndarray, bias: float = 0.0) -> np.ndarray:
        """Asymmetric distortion"""
        positive = x + bias
        negative = x - bias
        
        # Different processing for positive and negative peaks
        result = np.where(x >= 0, 
                         np.tanh(positive * 1.5),
                         np.tanh(negative * 2.0))
        
        return result
    
    @staticmethod
    def waveshaper_cubic(x: np.ndarray, amount: float = 0.5) -> np.ndarray:
        """Cubic waveshaper"""
        return x - (amount / 3.0) * (x ** 3)
    
    @staticmethod
    def exponential(x: np.ndarray, factor: float = 2.0) -> np.ndarray:
        """Exponential waveshaper"""
        return np.sign(x) * (1 - np.exp(-abs(x) * factor))


class HarmonicGenerator:
    """Harmonic content generator"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.history = np.zeros(4)  # For derivative calculation
        
    def generate_harmonics(self, signal: np.ndarray, amount: float) -> np.ndarray:
        """Generate harmonic content"""
        if amount <= 0:
            return signal
        
        # Generate 2nd harmonic (even)
        second_harmonic = signal ** 2 * np.sign(signal)
        
        # Generate 3rd harmonic (odd)
        third_harmonic = signal ** 3
        
        # Combine harmonics
        harmonics = 0.6 * second_harmonic + 0.4 * third_harmonic
        
        # Mix with original
        return signal + amount * harmonics * 0.1
    
    def enhance_presence(self, signal: np.ndarray) -> np.ndarray:
        """Enhance presence and clarity"""
        # Simple high-frequency emphasis
        enhanced = signal + 0.1 * np.diff(signal, prepend=signal[0])
        return enhanced


class FilterBank:
    """Multi-mode filter bank"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.filter_states = {}
        
    def process(self, signal: np.ndarray, filter_type: FilterType, 
               frequency: float, q: float = 0.707) -> np.ndarray:
        """Process signal with specified filter"""
        if filter_type == FilterType.NONE:
            return signal
        
        try:
            nyquist = self.sample_rate / 2
            norm_freq = frequency / nyquist
            
            # Ensure frequency is within valid range
            norm_freq = np.clip(norm_freq, 0.01, 0.99)
            
            if filter_type == FilterType.LOW_PASS:
                b, a = scipy.signal.butter(2, norm_freq, 'low')
            elif filter_type == FilterType.HIGH_PASS:
                b, a = scipy.signal.butter(2, norm_freq, 'high')
            elif filter_type == FilterType.BAND_PASS:
                low = norm_freq * 0.8
                high = norm_freq * 1.2
                b, a = scipy.signal.butter(2, [low, high], 'band')
            elif filter_type == FilterType.NOTCH:
                low = norm_freq * 0.9
                high = norm_freq * 1.1
                b, a = scipy.signal.butter(2, [low, high], 'bandstop')
            else:
                return signal  # Unknown filter type
            
            # Apply filter
            filtered = scipy.signal.lfilter(b, a, signal)
            return filtered
            
        except Exception as e:
            logging.warning(f"Filter processing failed: {e}")
            return signal


class BitCrusher:
    """Bit crushing and sample rate reduction"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.accumulator = 0.0
        self.counter = 0
        self.held_sample = 0.0
        
    def process(self, signal: np.ndarray, bit_depth: int, 
               rate_factor: float) -> np.ndarray:
        """Apply bit crushing and sample rate reduction"""
        # Bit depth reduction
        if bit_depth < 16:
            levels = 2 ** bit_depth
            quantized = np.round(signal * levels) / levels
        else:
            quantized = signal
        
        # Sample rate reduction
        if rate_factor < 1.0:
            output = np.zeros_like(signal)
            samples_per_hold = int(1.0 / rate_factor)
            
            for i in range(len(signal)):
                self.counter += 1
                
                if self.counter >= samples_per_hold:
                    self.held_sample = quantized[i]
                    self.counter = 0
                
                output[i] = self.held_sample
            
            return output
        
        return quantized


class DistortionProcessor:
    """Professional distortion processor with multiple algorithms"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Initialize parameters
        self.params = DistortionParams()
        
        # Processing components
        self._init_components()
        
        # State management
        self.processing_lock = threading.Lock()
        self.processed_samples = 0
        
    def _init_components(self):
        """Initialize processing components"""
        try:
            self.wave_shapers = WaveShapers()
            self.harmonic_generator = HarmonicGenerator(self.sample_rate)
            self.filter_bank = FilterBank(self.sample_rate)
            self.bit_crusher = BitCrusher(self.sample_rate)
            
            # Input/output gain stages
            self.input_gain = 1.0
            self.output_gain = 1.0
            
            self.logger.info("Distortion processor components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize distortion components: {e}")
            raise
    
    def update_parameters(self, **kwargs):
        """Update distortion parameters"""
        for key, value in kwargs.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
                self.logger.debug(f"Updated parameter {key} = {value}")
        
        # Update gain stages
        self.input_gain = 10 ** (self.params.drive / 20)  # dB to linear
        self.output_gain = 10 ** (self.params.output_level / 20)
    
    def process_sample(self, sample: float) -> float:
        """Process single audio sample"""
        try:
            # Store dry signal
            dry_sample = sample
            
            # Apply input gain
            gained_sample = sample * self.input_gain
            
            # Apply pre-filter
            if self.params.pre_filter_type != FilterType.NONE:
                gained_sample = self.filter_bank.process(
                    np.array([gained_sample]),
                    self.params.pre_filter_type,
                    self.params.pre_filter_freq
                )[0]
            
            # Apply distortion based on type
            if self.params.distortion_type == DistortionType.HARD_CLIP:
                distorted = self.wave_shapers.hard_clip(
                    np.array([gained_sample]), self.params.amount
                )[0]
                
            elif self.params.distortion_type == DistortionType.SOFT_CLIP:
                distorted = self.wave_shapers.soft_clip(
                    np.array([gained_sample]), self.params.amount + 0.1
                )[0]
                
            elif self.params.distortion_type == DistortionType.OVERDRIVE:
                distorted = self.wave_shapers.overdrive(
                    np.array([gained_sample]), self.params.amount * 5 + 1
                )[0]
                
            elif self.params.distortion_type == DistortionType.TUBE:
                distorted = self.wave_shapers.tube_saturation(
                    np.array([gained_sample]),
                    self.params.tube_warmth,
                    self.params.tube_compression
                )[0]
                
            elif self.params.distortion_type == DistortionType.FUZZ:
                distorted = self.wave_shapers.fuzz(
                    np.array([gained_sample]), self.params.amount * 3 + 1
                )[0]
                
            elif self.params.distortion_type == DistortionType.ASYMMETRIC:
                distorted = self.wave_shapers.asymmetric(
                    np.array([gained_sample]), self.params.bias
                )[0]
                
            elif self.params.distortion_type == DistortionType.WAVESHAPER:
                distorted = self.wave_shapers.waveshaper_cubic(
                    np.array([gained_sample]), self.params.amount
                )[0]
                
            elif self.params.distortion_type == DistortionType.SATURATION:
                distorted = np.tanh(gained_sample * (self.params.amount * 2 + 0.1))
                
            else:
                distorted = gained_sample
            
            # Add harmonics if enabled
            if self.params.harmonics > 0:
                distorted = self.harmonic_generator.generate_harmonics(
                    np.array([distorted]), self.params.harmonics
                )[0]
            
            # Apply post-filter
            if self.params.post_filter_type != FilterType.NONE:
                distorted = self.filter_bank.process(
                    np.array([distorted]),
                    self.params.post_filter_type,
                    self.params.post_filter_freq
                )[0]
            
            # Apply tone control (simple high-frequency roll-off)
            tone_factor = 1.0 - self.params.tone
            if tone_factor > 0:
                # Simple tone control implementation
                distorted *= (1.0 - tone_factor * 0.3)
            
            # Apply output gain
            distorted *= self.output_gain
            
            # Mix dry and wet
            output = dry_sample * (1 - self.params.mix) + distorted * self.params.mix
            
            self.processed_samples += 1
            
            return output
            
        except Exception as e:
            self.logger.error(f"Sample processing failed: {e}")
            return sample
    
    def process_buffer(self, audio_buffer: np.ndarray) -> np.ndarray:
        """Process audio buffer"""
        with self.processing_lock:
            try:
                if audio_buffer.ndim == 1:
                    # Mono processing
                    output = np.zeros_like(audio_buffer)
                    
                    # Special handling for bitcrush mode
                    if self.params.distortion_type == DistortionType.BITCRUSH:
                        # Apply input gain
                        gained = audio_buffer * self.input_gain
                        
                        # Apply bit crushing
                        crushed = self.bit_crusher.process(
                            gained, self.params.bit_depth, self.params.sample_rate_reduction
                        )
                        
                        # Apply output gain and mix
                        output = audio_buffer * (1 - self.params.mix) + \
                                crushed * self.output_gain * self.params.mix
                    else:
                        # Process sample by sample for other modes
                        for i in range(len(audio_buffer)):
                            output[i] = self.process_sample(audio_buffer[i])
                    
                elif audio_buffer.ndim == 2:
                    # Stereo processing
                    output = np.zeros_like(audio_buffer)
                    
                    for channel in range(audio_buffer.shape[1]):
                        if self.params.distortion_type == DistortionType.BITCRUSH:
                            # Apply input gain
                            gained = audio_buffer[:, channel] * self.input_gain
                            
                            # Apply bit crushing
                            crushed = self.bit_crusher.process(
                                gained, self.params.bit_depth, self.params.sample_rate_reduction
                            )
                            
                            # Apply output gain and mix
                            output[:, channel] = audio_buffer[:, channel] * (1 - self.params.mix) + \
                                               crushed * self.output_gain * self.params.mix
                        else:
                            # Process sample by sample
                            for i in range(len(audio_buffer)):
                                output[i, channel] = self.process_sample(audio_buffer[i, channel])
                
                else:
                    raise ValueError("Unsupported audio buffer dimensions")
                
                self.logger.debug(f"Processed buffer of {len(audio_buffer)} samples")
                return output
                
            except Exception as e:
                self.logger.error(f"Buffer processing failed: {e}")
                return audio_buffer
    
    def create_preset(self, name: str) -> Dict[str, Any]:
        """Create distortion presets"""
        presets = {
            'mild_overdrive': {
                'distortion_type': DistortionType.OVERDRIVE,
                'drive': 3.0,
                'amount': 0.3,
                'tone': 0.6,
                'output_level': -2.0,
                'mix': 1.0
            },
            'heavy_overdrive': {
                'distortion_type': DistortionType.OVERDRIVE,
                'drive': 8.0,
                'amount': 0.7,
                'tone': 0.4,
                'output_level': -4.0,
                'harmonics': 0.2,
                'mix': 1.0
            },
            'tube_warmth': {
                'distortion_type': DistortionType.TUBE,
                'drive': 4.0,
                'tube_warmth': 0.7,
                'tube_compression': 0.4,
                'tone': 0.7,
                'harmonics': 0.3,
                'post_filter_type': FilterType.LOW_PASS,
                'post_filter_freq': 6000.0,
                'mix': 1.0
            },
            'fuzz_face': {
                'distortion_type': DistortionType.FUZZ,
                'drive': 10.0,
                'amount': 0.8,
                'tone': 0.3,
                'output_level': -6.0,
                'pre_filter_type': FilterType.HIGH_PASS,
                'pre_filter_freq': 200.0,
                'mix': 1.0
            },
            'digital_crush': {
                'distortion_type': DistortionType.BITCRUSH,
                'drive': 2.0,
                'bit_depth': 8,
                'sample_rate_reduction': 0.5,
                'tone': 0.5,
                'output_level': -3.0,
                'mix': 0.7
            },
            'asymmetric_clip': {
                'distortion_type': DistortionType.ASYMMETRIC,
                'drive': 6.0,
                'bias': 0.2,
                'amount': 0.6,
                'harmonics': 0.1,
                'tone': 0.5,
                'mix': 1.0
            },
            'vintage_saturation': {
                'distortion_type': DistortionType.SATURATION,
                'drive': 5.0,
                'amount': 0.4,
                'harmonics': 0.4,
                'tube_warmth': 0.6,
                'post_filter_type': FilterType.SHELF,
                'post_filter_freq': 3000.0,
                'tone': 0.8,
                'mix': 1.0
            }
        }
        
        return presets.get(name, presets['mild_overdrive'])
    
    def apply_preset(self, name: str):
        """Apply a preset to the processor"""
        preset = self.create_preset(name)
        
        # Update parameters from preset
        for key, value in preset.items():
            if hasattr(self.params, key):
                if key == 'distortion_type':
                    setattr(self.params, key, DistortionType(value))
                elif key.endswith('_type') and 'filter' in key:
                    setattr(self.params, key, FilterType(value))
                else:
                    setattr(self.params, key, value)
        
        # Update gain stages
        self.update_parameters()
        
        self.logger.info(f"Applied preset: {name}")
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get current processor information"""
        return {
            'distortion_type': self.params.distortion_type.value,
            'drive': self.params.drive,
            'amount': self.params.amount,
            'tone': self.params.tone,
            'output_level': self.params.output_level,
            'mix': self.params.mix,
            'bias': self.params.bias,
            'harmonics': self.params.harmonics,
            'tube_warmth': self.params.tube_warmth,
            'tube_compression': self.params.tube_compression,
            'bit_depth': self.params.bit_depth,
            'sample_rate_reduction': self.params.sample_rate_reduction,
            'pre_filter_type': self.params.pre_filter_type.value,
            'pre_filter_freq': self.params.pre_filter_freq,
            'post_filter_type': self.params.post_filter_type.value,
            'post_filter_freq': self.params.post_filter_freq,
            'sample_rate': self.sample_rate,
            'processed_samples': self.processed_samples,
            'input_gain_db': self.params.drive,
            'output_gain_db': self.params.output_level
        }
    
    def analyze_signal_characteristics(self, signal: np.ndarray) -> Dict[str, float]:
        """Analyze input signal characteristics for automatic parameter suggestion"""
        # Peak analysis
        peak_level = np.max(np.abs(signal))
        rms_level = np.sqrt(np.mean(signal ** 2))
        crest_factor = peak_level / (rms_level + 1e-10)
        
        # Spectral analysis
        fft = np.fft.fft(signal[:min(2048, len(signal))])
        magnitude = np.abs(fft[:len(fft)//2])
        
        # Spectral centroid
        freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)[:len(fft)//2]
        spectral_centroid = np.sum(magnitude * freqs) / (np.sum(magnitude) + 1e-10)
        
        # High frequency content
        high_freq_energy = np.sum(magnitude[len(magnitude)//2:]) / (np.sum(magnitude) + 1e-10)
        
        return {
            'peak_level': peak_level,
            'rms_level': rms_level,
            'crest_factor': crest_factor,
            'spectral_centroid': spectral_centroid,
            'high_freq_energy': high_freq_energy
        }
    
    def suggest_parameters(self, signal_analysis: Dict[str, float]) -> Dict[str, Any]:
        """Suggest optimal parameters based on signal analysis"""
        suggestions = {}
        
        # Adjust drive based on input level
        if signal_analysis['rms_level'] < 0.1:
            suggestions['drive'] = 8.0  # Boost quiet signals
        elif signal_analysis['rms_level'] > 0.5:
            suggestions['drive'] = 2.0  # Reduce drive for hot signals
        else:
            suggestions['drive'] = 5.0
        
        # Adjust amount based on crest factor
        if signal_analysis['crest_factor'] > 3.0:
            suggestions['amount'] = 0.3  # Less distortion for dynamic signals
        else:
            suggestions['amount'] = 0.6  # More distortion for compressed signals
        
        # Adjust tone based on spectral content
        if signal_analysis['spectral_centroid'] > 2000:
            suggestions['tone'] = 0.7  # Reduce high frequencies for bright signals
        else:
            suggestions['tone'] = 0.4  # Enhance high frequencies for dark signals
        
        # Suggest distortion type based on characteristics
        if signal_analysis['high_freq_energy'] > 0.3:
            suggestions['distortion_type'] = DistortionType.TUBE
        elif signal_analysis['crest_factor'] < 2.0:
            suggestions['distortion_type'] = DistortionType.SATURATION
        else:
            suggestions['distortion_type'] = DistortionType.OVERDRIVE
        
        return suggestions
    
    def auto_adjust(self, signal: np.ndarray):
        """Automatically adjust parameters based on input signal"""
        analysis = self.analyze_signal_characteristics(signal)
        suggestions = self.suggest_parameters(analysis)
        
        # Apply suggestions
        for param, value in suggestions.items():
            if hasattr(self.params, param):
                setattr(self.params, param, value)
        
        self.update_parameters()
        
        self.logger.info("Auto-adjusted parameters based on signal analysis")
    
    def reset(self):
        """Reset processor state"""
        # Reset bit crusher state
        self.bit_crusher.accumulator = 0.0
        self.bit_crusher.counter = 0
        self.bit_crusher.held_sample = 0.0
        
        # Reset harmonic generator
        self.harmonic_generator.history.fill(0)
        
        # Reset counters
        self.processed_samples = 0
        
        self.logger.info("Distortion processor reset")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'processing_lock'):
            with self.processing_lock:
                pass  # Ensure any ongoing processing completes
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Distortion parameters
        self.drive = 5.0  # input gain
        self.level = 0.5  # output level
        self.tone = 0.5  # tone control
        self.distortion_type = DistortionType.OVERDRIVE
        self.wet_level = 1.0
        self.dry_level = 0.0
        
        # Pre/post filters
        self._init_filters()
        
        # Tube modeling parameters
        self.tube_bias = 0.0
        self.tube_warmth = 0.5
        
        self.logger.info("DistortionProcessor initialized")
    
    def _init_filters(self):
        """Initialize pre and post filters"""
        # High-pass filter for pre-emphasis
        self.pre_hp_b, self.pre_hp_a = scipy.signal.butter(
            1, 100 / (self.sample_rate / 2), 'highpass'
        )
        
        # Low-pass filter for post-processing
        self.post_lp_b, self.post_lp_a = scipy.signal.butter(
            2, 8000 / (self.sample_rate / 2), 'lowpass'
        )
        
        # Tone control filter
        self.tone_b, self.tone_a = scipy.signal.butter(
            1, 1000 / (self.sample_rate / 2), 'lowpass'
        )
        
        # Initialize filter states
        self.pre_hp_zi = scipy.signal.lfilter_zi(self.pre_hp_b, self.pre_hp_a)
        self.post_lp_zi = scipy.signal.lfilter_zi(self.post_lp_b, self.post_lp_a)
        self.tone_zi = scipy.signal.lfilter_zi(self.tone_b, self.tone_a)
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply distortion processing"""
        try:
            # Apply input gain
            boosted_audio = audio_data * self.drive
            
            # Pre-filter (optional high-pass for clarity)
            if self.distortion_type in [DistortionType.OVERDRIVE, DistortionType.TUBE]:
                filtered_audio, self.pre_hp_zi = scipy.signal.lfilter(
                    self.pre_hp_b, self.pre_hp_a, boosted_audio, zi=self.pre_hp_zi
                )
            else:
                filtered_audio = boosted_audio
            
            # Apply distortion
            distorted_audio = self._apply_distortion(filtered_audio)
            
            # Apply tone control
            toned_audio = self._apply_tone_control(distorted_audio)
            
            # Post-filter (anti-aliasing)
            processed_audio, self.post_lp_zi = scipy.signal.lfilter(
                self.post_lp_b, self.post_lp_a, toned_audio, zi=self.post_lp_zi
            )
            
            # Apply output level and mix
            processed_audio *= self.level
            final_audio = (self.dry_level * audio_data + 
                          self.wet_level * processed_audio)
            
            self.logger.debug("Distortion processing completed")
            return final_audio
            
        except Exception as e:
            self.logger.error(f"Distortion processing failed: {e}")
            return audio_data
    
    def _apply_distortion(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply distortion algorithm based on type"""
        if self.distortion_type == DistortionType.OVERDRIVE:
            return self._overdrive(audio_data)
        elif self.distortion_type == DistortionType.HARD_CLIP:
            return self._hard_clip(audio_data)
        elif self.distortion_type == DistortionType.SOFT_CLIP:
            return self._soft_clip(audio_data)
        elif self.distortion_type == DistortionType.TUBE:
            return self._tube_distortion(audio_data)
        elif self.distortion_type == DistortionType.FUZZ:
            return self._fuzz_distortion(audio_data)
        elif self.distortion_type == DistortionType.WAVESHAPER:
            return self._waveshaper(audio_data)
        else:
            return self._overdrive(audio_data)
    
    def _overdrive(self, audio_data: np.ndarray) -> np.ndarray:
        """Smooth overdrive distortion"""
        return np.tanh(audio_data)
    
    def _hard_clip(self, audio_data: np.ndarray) -> np.ndarray:
        """Hard clipping distortion"""
        return np.clip(audio_data, -1.0, 1.0)
    
    def _soft_clip(self, audio_data: np.ndarray) -> np.ndarray:
        """Soft clipping distortion"""
        # Cubic soft clipping
        abs_x = np.abs(audio_data)
        sign_x = np.sign(audio_data)
        
        # Soft clip function
        clipped = np.where(
            abs_x <= 2/3,
            audio_data,
            sign_x * (1 - (2 - 3*abs_x)**2 / 3)
        )
        
        return np.where(abs_x > 1.0, sign_x, clipped)
    
    def _tube_distortion(self, audio_data: np.ndarray) -> np.ndarray:
        """Tube-style distortion with bias and warmth"""
        # Add tube bias
        biased_audio = audio_data + self.tube_bias
        
        # Asymmetric tube distortion
        positive = biased_audio >= 0
        negative = ~positive
        
        result = np.zeros_like(audio_data)
        
        # Positive half-cycle (more compression)
        pos_data = biased_audio[positive]
        result[positive] = np.tanh(pos_data * (1 + self.tube_warmth))
        
        # Negative half-cycle (less compression)
        neg_data = biased_audio[negative]
        result[negative] = np.tanh(neg_data * (1 + self.tube_warmth * 0.7))
        
        return result * 0.8  # Reduce level slightly
    
    def _fuzz_distortion(self, audio_data: np.ndarray) -> np.ndarray:
        """Fuzz-style distortion with square-wave-like characteristics"""
        # Heavy saturation followed by smoothing
        heavily_distorted = np.tanh(audio_data * 10)
        
        # Add some square-wave character
        square_component = np.sign(audio_data) * 0.3
        
        return heavily_distorted * 0.7 + square_component
    
    def _waveshaper(self, audio_data: np.ndarray) -> np.ndarray:
        """Custom waveshaping distortion"""
        # Polynomial waveshaping
        x = audio_data
        shaped = x + 0.3 * x**3 - 0.1 * x**5
        
        # Normalize to prevent excessive gain
        max_val = np.max(np.abs(shaped))
        if max_val > 1.0:
            shaped /= max_val
        
        return shaped
    
    def _apply_tone_control(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply tone control (simple high/low frequency balance)"""
        if self.tone == 0.5:
            return audio_data  # No tone adjustment
        
        # Low-pass for dark tone, high-pass for bright tone
        if self.tone < 0.5:
            # Darker tone - low-pass filter
            cutoff = 1000 + (self.tone * 4000)  # 1kHz to 3kHz
            b, a = scipy.signal.butter(1, cutoff / (self.sample_rate / 2), 'lowpass')
        else:
            # Brighter tone - high-pass filter
            cutoff = 200 + ((self.tone - 0.5) * 800)  # 200Hz to 600Hz
            b, a = scipy.signal.butter(1, cutoff / (self.sample_rate / 2), 'highpass')
        
        filtered_audio, self.tone_zi = scipy.signal.lfilter(
            b, a, audio_data, zi=self.tone_zi
        )
        
        # Mix with original based on tone setting
        mix_amount = abs(self.tone - 0.5) * 2
        return audio_data * (1 - mix_amount) + filtered_audio * mix_amount
    
    def set_parameters(self, drive: float = None, level: float = None,
                      tone: float = None, distortion_type: DistortionType = None):
        """Set distortion parameters"""
        if drive is not None:
            self.drive = max(0.1, min(20.0, drive))
        if level is not None:
            self.level = np.clip(level, 0.0, 1.0)
        if tone is not None:
            self.tone = np.clip(tone, 0.0, 1.0)
        if distortion_type is not None:
            self.distortion_type = distortion_type
        
        self.logger.debug(f"Distortion parameters updated")
    
    def get_frequency_response(self, frequencies: np.ndarray) -> np.ndarray:
        """Get frequency response of current distortion settings"""
        # Generate test signal
        test_signal = np.sin(2 * np.pi * frequencies[:, np.newaxis] * 
                           np.linspace(0, 1, self.sample_rate))
        
        # Apply distortion to each frequency
        responses = []
        for freq_signal in test_signal:
            processed = self.process(freq_signal * 0.5)  # Moderate level
            rms_original = np.sqrt(np.mean(freq_signal**2))
            rms_processed = np.sqrt(np.mean(processed**2))
            responses.append(rms_processed / rms_original if rms_original > 0 else 0)
        
        return np.array(responses)
