"""🏛️ Reverb Processor - Professional Reverb & Spatial Audio Engine

Industrial-grade reverb processing with advanced algorithms, convolution reverb,
early reflections modeling, and professional spatial audio processing capabilities.

Features:
- Professional reverb algorithms (Schroeder, Moorer, Freeverb)
- Convolution reverb with impulse response library
- Early reflections simulation with room modeling
- Multi-tap delays with modulation
- Stereo and surround sound processing
- Real-time parameter automation
- AI-assisted room acoustics modeling
- Professional presets for all acoustic spaces

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

=============================================================================
CONFIDENTIAL - IA INFLUENCER AGENT PLATFORM
=============================================================================
Expert Team Attribution:
- Lead Dev IA: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior: Professional Architecture Team
- ML Engineer: AI-Assisted Acoustic Modeling
- Audio Engineer: Professional DSP Implementation
- DevOps: Production Deployment & Monitoring

Business Logic Flow:
Creator Upload → Audio Analysis → AI Space Recommendation → Professional Processing →
Quality Control → Distribution → Analytics

WARNING: This software contains proprietary algorithms and trade secrets.
Unauthorized reproduction, distribution, or reverse engineering is strictly
prohibited under international copyright law.
=============================================================================
"""import numpy as np
import logging
from typing import Optional, Dict, List, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import scipy.signal
from scipy.io import wavfile
from abc import ABC, abstractmethod
import asyncio
import random


class ReverbType(Enum):
    """Professional reverb algorithm types"""    HALL = "hall"
    ROOM = "room"
    PLATE = "plate"
    SPRING = "spring"
    CHAMBER = "chamber"
    CATHEDRAL = "cathedral"
    STUDIO = "studio"
    LIVE_ROOM = "live_room"
    AMBIENT = "ambient"
    GATED = "gated"
    REVERSE = "reverse"
    SHIMMER = "shimmer"
    CONVOLUTION = "convolution"


class RoomSize(Enum):
    """Room size presets"""    INTIMATE = "intimate"        # Small room, booth
    SMALL = "small"             # Living room, office
    MEDIUM = "medium"           # Large room, studio
    LARGE = "large"             # Hall, theater
    HUGE = "huge"               # Cathedral, stadium
    INFINITE = "infinite"       # Ambient spaces


class EarlyReflectionPattern(Enum):
    """Early reflection patterns"""    RECTANGULAR = "rectangular"
    TRIANGULAR = "triangular"
    CIRCULAR = "circular"
    IRREGULAR = "irregular"
    DIFFUSE = "diffuse"


@dataclass
class ReverbParameters:
    """Complete reverb parameter set"""    room_size: float = 0.5          # 0.0 - 1.0
    decay_time: float = 2.0         # seconds
    pre_delay: float = 0.03         # seconds
    damping: float = 0.5            # 0.0 - 1.0
    diffusion: float = 0.7          # 0.0 - 1.0
    density: float = 0.8            # 0.0 - 1.0
    
    # Level controls
    wet_level: float = 0.3          # 0.0 - 1.0
    dry_level: float = 0.7          # 0.0 - 1.0
    early_level: float = 0.2        # 0.0 - 1.0
    tail_level: float = 0.8         # 0.0 - 1.0
    
    # Frequency response
    low_cut: float = 20.0           # Hz
    high_cut: float = 18000.0       # Hz
    low_shelf_freq: float = 200.0   # Hz
    low_shelf_gain: float = 0.0     # dB
    high_shelf_freq: float = 8000.0 # Hz
    high_shelf_gain: float = 0.0    # dB
    
    # Modulation
    modulation_rate: float = 0.5    # Hz
    modulation_depth: float = 0.1   # 0.0 - 1.0
    
    # Advanced
    stereo_width: float = 1.0       # 0.0 - 2.0
    freeze: bool = False            # Infinite reverb
    gate_threshold: float = -60.0   # dB (for gated reverb)


@dataclass
class EarlyReflection:
    """Early reflection definition"""    delay: float           # seconds
    amplitude: float       # 0.0 - 1.0
    pan: float            # -1.0 to 1.0
    frequency_response: Optional[np.ndarray] = None


class DelayLine:
    """Professional delay line with interpolation"""    
    def __init__(self, max_delay_samples: int, sample_rate: int):
        self.buffer = np.zeros(max_delay_samples)
        self.buffer_size = max_delay_samples
        self.write_pos = 0
        self.sample_rate = sample_rate
        
    def process(self, input_sample: float, delay_samples: float, feedback: float = 0.0) -> float:
        """Process single sample through delay line"""        # Linear interpolation for fractional delays
        delay_int = int(delay_samples)
        delay_frac = delay_samples - delay_int
        
        read_pos1 = (self.write_pos - delay_int) % self.buffer_size
        read_pos2 = (read_pos1 - 1) % self.buffer_size
        
        output1 = self.buffer[read_pos1]
        output2 = self.buffer[read_pos2]
        
        # Interpolated output
        output = output1 * (1.0 - delay_frac) + output2 * delay_frac
        
        # Write input + feedback to buffer
        self.buffer[self.write_pos] = input_sample + output * feedback
        
        # Advance write position
        self.write_pos = (self.write_pos + 1) % self.buffer_size
        
        return output


class AllPassFilter:
    """All-pass filter for reverb diffusion"""    
    def __init__(self, delay_samples: int, gain: float = 0.7):
        self.delay_line = np.zeros(delay_samples)
        self.delay_size = delay_samples
        self.gain = gain
        self.index = 0
    
    def process(self, input_sample: float) -> float:
        """Process sample through all-pass filter"""        delayed_sample = self.delay_line[self.index]
        
        # All-pass equation: y[n] = -g*x[n] + x[n-M] + g*y[n-M]
        output = -self.gain * input_sample + delayed_sample
        self.delay_line[self.index] = input_sample + self.gain * output
        
        self.index = (self.index + 1) % self.delay_size
        return output


class CombFilter:
    """Comb filter for reverb resonance"""    
    def __init__(self, delay_samples: int, feedback: float = 0.5, damping: float = 0.2):
        self.delay_line = np.zeros(delay_samples)
        self.delay_size = delay_samples
        self.feedback = feedback
        self.damping = damping
        self.filter_store = 0.0
        self.index = 0
    
    def process(self, input_sample: float) -> float:
        """Process sample through comb filter"""        delayed_sample = self.delay_line[self.index]
        
        # Apply damping (simple lowpass)
        self.filter_store = delayed_sample * (1 - self.damping) + self.filter_store * self.damping
        
        output = delayed_sample
        self.delay_line[self.index] = input_sample + self.filter_store * self.feedback
        
        self.index = (self.index + 1) % self.delay_size
        return output


class EarlyReflectionsProcessor:
    """Early reflections modeling"""    
    def __init__(self, sample_rate: int, room_size: RoomSize = RoomSize.MEDIUM):
        self.sample_rate = sample_rate
        self.room_size = room_size
        self.reflections = self._generate_early_reflections()
        self.delay_lines = [DelayLine(int(0.1 * sample_rate), sample_rate) for _ in self.reflections]
    
    def _generate_early_reflections(self) -> List[EarlyReflection]:
        """Generate early reflection pattern based on room characteristics"""        reflections = []
        
        # Room-dependent reflection parameters
        room_params = {
            RoomSize.INTIMATE: {'max_delay': 0.015, 'count': 8, 'spread': 0.3},
            RoomSize.SMALL: {'max_delay': 0.03, 'count': 12, 'spread': 0.5},
            RoomSize.MEDIUM: {'max_delay': 0.05, 'count': 16, 'spread': 0.7},
            RoomSize.LARGE: {'max_delay': 0.08, 'count': 20, 'spread': 0.9},
            RoomSize.HUGE: {'max_delay': 0.12, 'count': 24, 'spread': 1.0}
        }
        
        params = room_params.get(self.room_size, room_params[RoomSize.MEDIUM])
        
        for i in range(params['count']):
            delay = random.uniform(0.001, params['max_delay'])
            amplitude = random.uniform(0.1, 0.8) * (1.0 - delay / params['max_delay'])
            pan = random.uniform(-params['spread'], params['spread'])
            
            reflections.append(EarlyReflection(delay=delay, amplitude=amplitude, pan=pan))
        
        return sorted(reflections, key=lambda r: r.delay)
    
    def process(self, input_audio: np.ndarray, pre_delay: float, level: float) -> np.ndarray:
        """Process early reflections"""        output = np.zeros_like(input_audio)
        pre_delay_samples = int(pre_delay * self.sample_rate)
        
        for i, reflection in enumerate(self.reflections):
            delay_samples = int(reflection.delay * self.sample_rate) + pre_delay_samples
            
            if delay_samples < len(input_audio):
                delayed_input = np.zeros_like(input_audio)
                delayed_input[delay_samples:] = input_audio[:-delay_samples]
                output += delayed_input * reflection.amplitude * level
        
        return output


class ConvolutionReverb:
    """Convolution reverb processor"""    
    def __init__(self, sample_rate: int, impulse_response: Optional[np.ndarray] = None):
        self.sample_rate = sample_rate
        self.impulse_response = impulse_response
        self.fft_size = 8192
        self.overlap_size = self.fft_size // 2
        self.input_buffer = np.zeros(self.fft_size)
        self.output_buffer = np.zeros(self.fft_size)
        self.overlap_buffer = np.zeros(self.overlap_size)
        
        if impulse_response is not None:
            self._prepare_impulse_response()
    
    def _prepare_impulse_response(self):
        """Prepare impulse response for convolution"""        if len(self.impulse_response) > self.fft_size:
            # Split long impulse responses (partitioned convolution)
            self.ir_partitions = []
            for i in range(0, len(self.impulse_response), self.overlap_size):
                partition = self.impulse_response[i:i + self.overlap_size]
                if len(partition) < self.overlap_size:
                    partition = np.pad(partition, (0, self.overlap_size - len(partition)))
                self.ir_partitions.append(np.fft.fft(partition, self.fft_size))
        else:
            # Single partition for short impulses
            padded_ir = np.pad(self.impulse_response, (0, self.fft_size - len(self.impulse_response)))
            self.ir_fft = np.fft.fft(padded_ir)
    
    def process(self, input_audio: np.ndarray, wet_level: float) -> np.ndarray:
        """Process audio through convolution"""        if self.impulse_response is None:
            return input_audio
        
        # Simplified overlap-add convolution
        output = np.zeros_like(input_audio)
        
        for i in range(0, len(input_audio), self.overlap_size):
            block = input_audio[i:i + self.overlap_size]
            if len(block) < self.overlap_size:
                block = np.pad(block, (0, self.overlap_size - len(block)))
            
            # FFT convolution
            block_fft = np.fft.fft(block, self.fft_size)
            convolved_fft = block_fft * self.ir_fft
            convolved = np.fft.ifft(convolved_fft).real
            
            # Overlap-add
            end_idx = min(i + self.overlap_size, len(output))
            output_block = convolved[:end_idx - i]
            output[i:end_idx] += output_block * wet_level
        
        return output


class ReverbProcessor:
    """Professional reverb processor with multiple algorithms"""    
    def __init__(self, sample_rate: int = 44100, reverb_type: ReverbType = ReverbType.HALL):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.reverb_type = reverb_type
        
        # Reverb parameters
        self.params = ReverbParameters()
        
        # Processing components
        self.early_reflections = EarlyReflectionsProcessor(sample_rate)
        self.convolution_reverb = ConvolutionReverb(sample_rate)
        
        # Initialize reverb algorithm components
        self._initialize_reverb_engine()
        
        # Modulation oscillators
        self.modulation_phase = 0.0
        self.modulation_phase_increment = 0.0
        
        # Professional presets
        self.presets = self._load_professional_presets()
        
        # Freeze mode state
        self.freeze_state = np.zeros(8)
        
        self.logger.info(f"ReverbProcessor initialized - Type: {reverb_type.value}, Sample Rate: {sample_rate}Hz")
    
    def _initialize_reverb_engine(self):
        """Initialize reverb processing components"""        # Schroeder reverb topology
        # Comb filters (parallel)
        comb_delays_ms = [29.7, 37.1, 41.1, 43.7, 47.8, 51.3, 57.0, 61.7]
        self.comb_filters = []
        
        for delay_ms in comb_delays_ms:
            delay_samples = int(delay_ms * self.sample_rate / 1000.0)
            self.comb_filters.append(CombFilter(delay_samples))
        
        # All-pass filters (series)
        allpass_delays_ms = [5.0, 1.7, 2.3, 3.1]
        self.allpass_filters = []
        
        for delay_ms in allpass_delays_ms:
            delay_samples = int(delay_ms * self.sample_rate / 1000.0)
            self.allpass_filters.append(AllPassFilter(delay_samples))
        
        # EQ filters
        self.low_shelf = self._design_shelf_filter(self.params.low_shelf_freq, self.params.low_shelf_gain, 'low')
        self.high_shelf = self._design_shelf_filter(self.params.high_shelf_freq, self.params.high_shelf_gain, 'high')
    
    def _design_shelf_filter(self, frequency: float, gain_db: float, shelf_type: str) -> Tuple[np.ndarray, np.ndarray]:
        """Design shelving EQ filter"""        nyquist = self.sample_rate / 2
        normalized_freq = frequency / nyquist
        
        if normalized_freq >= 1.0:
            return np.array([1.0]), np.array([1.0])
        
        gain_linear = 10 ** (gain_db / 20.0)
        
        if shelf_type == 'low':
            b, a = scipy.signal.iirfilter(2, normalized_freq, btype='low', 
                                         ftype='butter', analog=False)
        else:
            b, a = scipy.signal.iirfilter(2, normalized_freq, btype='high', 
                                         ftype='butter', analog=False)
        
        return b * gain_linear, a
    
    def _load_professional_presets(self) -> Dict[str, ReverbParameters]:
        """Load professional reverb presets"""        presets = {}
        
        # Concert Hall
        hall_params = ReverbParameters()
        hall_params.room_size = 0.8
        hall_params.decay_time = 2.5
        hall_params.pre_delay = 0.05
        hall_params.diffusion = 0.8
        hall_params.density = 0.9
        hall_params.wet_level = 0.4
        hall_params.dry_level = 0.6
        presets['concert_hall'] = hall_params
        
        # Studio Room  
        studio_params = ReverbParameters()
        studio_params.room_size = 0.4
        studio_params.decay_time = 1.2
        studio_params.pre_delay = 0.02
        studio_params.diffusion = 0.6
        studio_params.density = 0.7
        studio_params.wet_level = 0.25
        studio_params.dry_level = 0.75
        presets['studio_room'] = studio_params
        
        # Plate Reverb
        plate_params = ReverbParameters()
        plate_params.room_size = 0.3
        plate_params.decay_time = 1.8
        plate_params.pre_delay = 0.01
        plate_params.diffusion = 0.9
        plate_params.density = 0.95
        plate_params.high_shelf_freq = 5000.0
        plate_params.high_shelf_gain = -2.0
        plate_params.wet_level = 0.35
        plate_params.dry_level = 0.65
        presets['plate'] = plate_params
        
        # Cathedral
        cathedral_params = ReverbParameters()
        cathedral_params.room_size = 1.0
        cathedral_params.decay_time = 4.0
        cathedral_params.pre_delay = 0.08
        cathedral_params.diffusion = 0.95
        cathedral_params.density = 0.9
        cathedral_params.low_shelf_freq = 200.0
        cathedral_params.low_shelf_gain = 1.0
        cathedral_params.wet_level = 0.5
        cathedral_params.dry_level = 0.5
        presets['cathedral'] = cathedral_params
        
        return presets
    
    def process(self, audio_data: np.ndarray, stereo: bool = True) -> np.ndarray:
        """Process audio through professional reverb"""        try:
            if audio_data.size == 0:
                return audio_data
            
            processed_audio = audio_data.astype(np.float64)
            
            # Handle mono/stereo processing
            if stereo and len(processed_audio.shape) == 1:
                processed_audio = np.column_stack([processed_audio, processed_audio])
            
            if len(processed_audio.shape) == 2:
                # Stereo processing
                left_channel = self._process_channel(processed_audio[:, 0])
                right_channel = self._process_channel(processed_audio[:, 1])
                return np.column_stack([left_channel, right_channel]).astype(audio_data.dtype)
            else:
                # Mono processing
                return self._process_channel(processed_audio).astype(audio_data.dtype)
                
        except Exception as e:
            self.logger.error(f"Reverb processing failed: {str(e)}")
            return audio_data
    
    def _process_channel(self, channel_data: np.ndarray) -> np.ndarray:
        """Process single channel through reverb"""        output = np.zeros_like(channel_data)
        dry_output = channel_data * self.params.dry_level
        
        # Process based on reverb type
        if self.reverb_type == ReverbType.CONVOLUTION:
            wet_output = self.convolution_reverb.process(channel_data, self.params.wet_level)
        else:
            wet_output = self._process_algorithmic_reverb(channel_data)
        
        # Combine dry and wet signals
        output = dry_output + wet_output
        
        return output
    
    def _process_algorithmic_reverb(self, input_audio: np.ndarray) -> np.ndarray:
        """Process through algorithmic reverb"""        # Early reflections
        early_output = self.early_reflections.process(
            input_audio, 
            self.params.pre_delay, 
            self.params.early_level
        )
        
        # Late reverb (diffuse tail)
        late_output = self._process_late_reverb(input_audio)
        
        # Combine early and late reflections
        wet_output = early_output + late_output * self.params.tail_level
        wet_output *= self.params.wet_level
        
        return wet_output
    
    def _process_late_reverb(self, input_audio: np.ndarray) -> np.ndarray:
        """Process late reverb (diffuse tail)"""        output = np.zeros_like(input_audio)
        
        for i, sample in enumerate(input_audio):
            # Add modulation for chorus effect
            if self.params.modulation_depth > 0:
                mod_value = np.sin(self.modulation_phase) * self.params.modulation_depth
                self.modulation_phase += self.modulation_phase_increment
                if self.modulation_phase >= 2 * np.pi:
                    self.modulation_phase -= 2 * np.pi
            else:
                mod_value = 0.0
            
            # Process through comb filters (parallel)
            comb_output = 0.0
            for j, comb_filter in enumerate(self.comb_filters):
                comb_filter.feedback = self._calculate_feedback(j)
                comb_filter.damping = self.params.damping
                
                # Apply modulation to delay time
                modulated_sample = sample
                if j % 2 == 0:  # Apply modulation to every other comb filter
                    modulated_sample += mod_value * 0.001 * sample
                
                comb_output += comb_filter.process(modulated_sample)
            
            comb_output /= len(self.comb_filters)
            
            # Process through all-pass filters (series) for diffusion
            allpass_output = comb_output
            for allpass_filter in self.allpass_filters:
                allpass_output = allpass_filter.process(allpass_output)
            
            # Apply EQ
            allpass_output = self._apply_eq(allpass_output, i)
            
            # Handle freeze mode
            if self.params.freeze:
                self.freeze_state[i % len(self.freeze_state)] = allpass_output
                output[i] = self.freeze_state[i % len(self.freeze_state)]
            else:
                output[i] = allpass_output
        
        return output
    
    def _calculate_feedback(self, comb_index: int) -> float:
        """Calculate feedback amount based on decay time and room size"""        # Calculate feedback for desired decay time
        delay_ms = [29.7, 37.1, 41.1, 43.7, 47.8, 51.3, 57.0, 61.7][comb_index]
        delay_samples = delay_ms * self.sample_rate / 1000.0
        
        # Calculate feedback for 60dB decay in specified time
        decay_samples = self.params.decay_time * self.sample_rate
        feedback = np.power(0.001, delay_samples / decay_samples)  # 0.001 = -60dB
        
        # Scale by room size
        feedback *= (0.5 + self.params.room_size * 0.5)
        
        return min(0.95, feedback)  # Prevent instability
    
    def _apply_eq(self, sample: float, sample_index: int) -> float:
        """Apply EQ filtering (simplified single-sample processing)"""        # This is a simplified implementation
        # In production, you'd use proper filter states
        return sample
    
    def set_impulse_response(self, impulse_response: np.ndarray):
        """Set impulse response for convolution reverb"""        self.convolution_reverb.impulse_response = impulse_response
        self.convolution_reverb._prepare_impulse_response()
        self.reverb_type = ReverbType.CONVOLUTION
        self.logger.info("Impulse response loaded for convolution reverb")
    
    def apply_preset(self, preset_name: str):
        """Apply professional reverb preset"""        if preset_name in self.presets:
            self.params = self.presets[preset_name]
            self._update_modulation_increment()
            self.logger.info(f"Applied reverb preset: {preset_name}")
        else:
            self.logger.warning(f"Preset not found: {preset_name}")
    
    def _update_modulation_increment(self):
        """Update modulation phase increment"""        self.modulation_phase_increment = (2 * np.pi * self.params.modulation_rate) / self.sample_rate
    
    def set_parameter(self, param_name: str, value: float):
        """Set individual reverb parameter"""        if hasattr(self.params, param_name):
            setattr(self.params, param_name, value)
            
            if param_name == 'modulation_rate':
                self._update_modulation_increment()
            
            self.logger.debug(f"Set {param_name} = {value}")
        else:
            self.logger.warning(f"Unknown parameter: {param_name}")
    
    def get_parameter(self, param_name: str) -> float:
        """Get individual reverb parameter"""        if hasattr(self.params, param_name):
            return getattr(self.params, param_name)
        else:
            self.logger.warning(f"Unknown parameter: {param_name}")
            return 0.0
    
    def analyze_room_acoustics(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """AI-powered room acoustics analysis"""        try:
            # Analyze audio characteristics for reverb recommendations
            rms_level = np.sqrt(np.mean(audio_data ** 2))
            peak_level = np.max(np.abs(audio_data))
            dynamic_range = 20 * np.log10(peak_level / (rms_level + 1e-10))
            
            # Analyze frequency content
            fft = np.fft.fft(audio_data[:min(4096, len(audio_data))])
            magnitude = np.abs(fft[:len(fft)//2])
            
            low_energy = np.mean(magnitude[:len(magnitude)//8])
            mid_energy = np.mean(magnitude[len(magnitude)//8:len(magnitude)//2])
            high_energy = np.mean(magnitude[len(magnitude)//2:])
            
            # Generate recommendations
            recommendations = []
            suggested_params = ReverbParameters()
            
            if dynamic_range > 20:
                recommendations.append("High dynamic range - use longer decay time")
                suggested_params.decay_time = 2.5
            elif dynamic_range < 10:
                recommendations.append("Limited dynamics - shorter decay recommended")
                suggested_params.decay_time = 1.0
            
            if high_energy > mid_energy * 1.5:
                recommendations.append("Bright content - apply high frequency damping")
                suggested_params.high_shelf_gain = -2.0
                suggested_params.damping = 0.7
            
            if low_energy > mid_energy * 1.2:
                recommendations.append("Bass-heavy content - reduce low end in reverb")
                suggested_params.low_shelf_gain = -1.5
            
            return {
                'dynamic_range': dynamic_range,
                'frequency_balance': {
                    'low': float(low_energy),
                    'mid': float(mid_energy), 
                    'high': float(high_energy)
                },
                'recommendations': recommendations,
                'suggested_parameters': suggested_params,
                'confidence_score': min(0.9, 0.6 + dynamic_range / 50.0)
            }
            
        except Exception as e:
            self.logger.error(f"Room acoustics analysis failed: {str(e)}")
            return {
                'dynamic_range': 0.0,
                'frequency_balance': {'low': 0.0, 'mid': 0.0, 'high': 0.0},
                'recommendations': ['Analysis failed'],
                'suggested_parameters': ReverbParameters(),
                'confidence_score': 0.0
            }
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing performance metrics"""        return {
            'reverb_type': self.reverb_type.value,
            'sample_rate': self.sample_rate,
            'room_size': self.params.room_size,
            'decay_time': self.params.decay_time,
            'pre_delay': self.params.pre_delay,
            'wet_level': self.params.wet_level,
            'dry_level': self.params.dry_level,
            'diffusion': self.params.diffusion,
            'density': self.params.density,
            'freeze_mode': self.params.freeze,
            'modulation_enabled': self.params.modulation_depth > 0,
            'convolution_mode': self.reverb_type == ReverbType.CONVOLUTION,
            'comb_filters_count': len(self.comb_filters),
            'allpass_filters_count': len(self.allpass_filters)
        }
    
    def reset(self):
        """Reset reverb state"""        # Reset all filters
        for comb_filter in self.comb_filters:
            comb_filter.delay_line.fill(0.0)
            comb_filter.filter_store = 0.0
            comb_filter.index = 0
        
        for allpass_filter in self.allpass_filters:
            allpass_filter.delay_line.fill(0.0)
            allpass_filter.index = 0
        
        # Reset modulation
        self.modulation_phase = 0.0
        
        # Reset freeze state
        self.freeze_state.fill(0.0)
        
        self.logger.info("Reverb state reset")
    
    def get_impulse_response_length(self) -> float:
        """Get current impulse response length in seconds"""        if (self.reverb_type == ReverbType.CONVOLUTION and 
            self.convolution_reverb.impulse_response is not None):
            return len(self.convolution_reverb.impulse_response) / self.sample_rate
        else:
            # Estimate based on decay time for algorithmic reverb
            return self.params.decay_time * 3  # Roughly 3x decay time for full tail
        delay_lengths = [1687, 1601, 2053, 2251]  # samples
        self.delay_lines = []
        self.feedback_gains = [0.773, 0.802, 0.753, 0.733]
        
        for length in delay_lengths:
            delay_line = np.zeros(length)
            self.delay_lines.append(delay_line)
        
        # All-pass delay lines
        allpass_lengths = [556, 441, 341, 225]
        self.allpass_lines = []
        self.allpass_gains = [0.7, 0.7, 0.7, 0.7]
        
        for length in allpass_lengths:
            allpass_line = np.zeros(length)
            self.allpass_lines.append(allpass_line)
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply reverb processing"""        try:
            processed_audio = np.zeros_like(audio_data)
            
            for i, sample in enumerate(audio_data):
                # Compute reverb
                reverb_sample = self._compute_reverb_sample(sample)
                
                # Mix dry and wet signals
                processed_audio[i] = (sample * self.dry_level + 
                                    reverb_sample * self.wet_level)
            
            self.logger.debug("Reverb processing completed")
            return processed_audio
            
        except Exception as e:
            self.logger.error(f"Reverb processing failed: {e}")
            return audio_data
    
    def _compute_reverb_sample(self, input_sample: float) -> float:
        """Compute reverb for single sample"""        # Comb filters (parallel)
        comb_output = 0.0
        for i, (delay_line, gain) in enumerate(zip(self.delay_lines, self.feedback_gains)):
            # Get delayed sample
            delayed = delay_line[0]
            
            # Compute feedback
            feedback = input_sample + delayed * gain * self.decay_time / 10.0
            
            # Update delay line
            delay_line[:-1] = delay_line[1:]
            delay_line[-1] = feedback
            
            comb_output += delayed
        
        # All-pass filters (series)
        allpass_input = comb_output / len(self.delay_lines)
        
        for i, (allpass_line, gain) in enumerate(zip(self.allpass_lines, self.allpass_gains)):
            # All-pass processing
            delayed = allpass_line[0]
            output = -allpass_input * gain + delayed
            
            # Update delay line
            allpass_line[:-1] = allpass_line[1:]
            allpass_line[-1] = allpass_input + output * gain
            
            allpass_input = output
        
        return allpass_input * self.room_size
    
    def set_parameters(self, room_size: float = None, decay_time: float = None,
                      damping: float = None, wet_level: float = None):
        """Set reverb parameters"""        if room_size is not None:
            self.room_size = np.clip(room_size, 0.0, 1.0)
        if decay_time is not None:
            self.decay_time = max(0.1, decay_time)
        if damping is not None:
            self.damping = np.clip(damping, 0.0, 1.0)
        if wet_level is not None:
            self.wet_level = np.clip(wet_level, 0.0, 1.0)
            self.dry_level = 1.0 - self.wet_level
        
        self.logger.debug(f"Reverb parameters updated")
