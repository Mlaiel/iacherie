"""🎵 Chorus Processor - Professional Modulation & Chorus Effects Engine

Advanced chorus, flanger, and modulation effects with multi-voice processing,
sophisticated LFO control, interpolation algorithms, and stereo width control.
Includes vintage and modern algorithm implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import scipy.interpolate
import scipy.signal
import threading


class ModulationType(Enum):
    """
Modulation waveform types"""

    SINE = "sine"
    TRIANGLE = "triangle"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"
    RANDOM = "random"
    STEPPED = "stepped"


class ChorusMode(Enum):
    """Chorus processing modes"""

    CHORUS = "chorus"
    FLANGER = "flanger"
    VIBRATO = "vibrato"
    PHASER = "phaser"
    ENSEMBLE = "ensemble"
    VINTAGE = "vintage"


class InterpolationType(Enum):
    """Delay line interpolation types"""

    LINEAR = "linear"
    CUBIC = "cubic"
    HERMITE = "hermite"
    LAGRANGE = "lagrange"


@dataclass
class ChorusVoice:
    """Individual chorus voice parameters"""
    delay_ms: float = 10.0  # Base delay in milliseconds
    depth_ms: float = 2.0   # Modulation depth in milliseconds
    rate_hz: float = 1.0    # LFO rate in Hz
    phase_deg: float = 0.0  # LFO phase in degrees
    feedback: float = 0.0   # Feedback amount (-1 to 1)
    pan: float = 0.0        # Stereo panning (-1 to 1)
    level: float = 0.5      # Voice level (0 to 1)
    modulation_type: ModulationType = ModulationType.SINE


@dataclass
class ChorusParams:
    """
Chorus processor parameters"""
    mode: ChorusMode = ChorusMode.CHORUS
    voices: List[ChorusVoice] = None
    dry_level: float = 0.5
    wet_level: float = 0.5
    stereo_width: float = 1.0
    mix: float = 0.5
    interpolation: InterpolationType = InterpolationType.CUBIC
    high_cut_hz: float = 8000.0
    low_cut_hz: float = 100.0
    
    def __post_init__(self):
        if self.voices is None:
            self.voices = [
                ChorusVoice(delay_ms=12.0, depth_ms=3.0, rate_hz=0.8, phase_deg=0.0),
                ChorusVoice(delay_ms=18.0, depth_ms=2.5, rate_hz=1.2, phase_deg=120.0),
                ChorusVoice(delay_ms=25.0, depth_ms=2.0, rate_hz=0.9, phase_deg=240.0)
            ]


class DelayLine:
    """
Professional delay line with multiple interpolation methods"""
    
    def __init__(self, max_delay_samples: int, interpolation: InterpolationType = InterpolationType.CUBIC):
        self.max_delay = max_delay_samples
        self.buffer = np.zeros(max_delay_samples + 16)  # Extra space for interpolation
        self.write_pos = 0
        self.interpolation = interpolation
        
    def write(self, sample: float):
        """
Write sample to delay line"""
        self.buffer[self.write_pos] = sample
        self.write_pos = (self.write_pos + 1) % self.max_delay
    
    def read(self, delay_samples: float) -> float:
        """
Read from delay line with interpolation"""
        # Calculate read position
        read_pos = self.write_pos - delay_samples
        if read_pos < 0:
            read_pos += self.max_delay
        
        # Get integer and fractional parts
        int_pos = int(read_pos)
        frac = read_pos - int_pos
        
        if self.interpolation == InterpolationType.LINEAR:
            return self._linear_interpolate(int_pos, frac)
        elif self.interpolation == InterpolationType.CUBIC:
            return self._cubic_interpolate(int_pos, frac)
        elif self.interpolation == InterpolationType.HERMITE:
            return self._hermite_interpolate(int_pos, frac)
        elif self.interpolation == InterpolationType.LAGRANGE:
            return self._lagrange_interpolate(int_pos, frac)
        else:
            return self.buffer[int_pos % self.max_delay]
    
    def _linear_interpolate(self, pos: int, frac: float) -> float:
        """
Linear interpolation"""
        sample1 = self.buffer[pos % self.max_delay]
        sample2 = self.buffer[(pos + 1) % self.max_delay]
        return sample1 + frac * (sample2 - sample1)
    
    def _cubic_interpolate(self, pos: int, frac: float) -> float:
        """
Cubic interpolation"""
        y0 = self.buffer[(pos - 1) % self.max_delay]
        y1 = self.buffer[pos % self.max_delay]
        y2 = self.buffer[(pos + 1) % self.max_delay]
        y3 = self.buffer[(pos + 2) % self.max_delay]
        
        a0 = y3 - y2 - y0 + y1
        a1 = y0 - y1 - a0
        a2 = y2 - y0
        a3 = y1
        
        return a0 * frac**3 + a1 * frac**2 + a2 * frac + a3
    
    def _hermite_interpolate(self, pos: int, frac: float) -> float:
        """
Hermite interpolation"""
        y0 = self.buffer[(pos - 1) % self.max_delay]
        y1 = self.buffer[pos % self.max_delay]
        y2 = self.buffer[(pos + 1) % self.max_delay]
        y3 = self.buffer[(pos + 2) % self.max_delay]
        
        c0 = y1
        c1 = 0.5 * (y2 - y0)
        c2 = y0 - 2.5 * y1 + 2 * y2 - 0.5 * y3
        c3 = 0.5 * (y3 - y0) + 1.5 * (y1 - y2)
        
        return ((c3 * frac + c2) * frac + c1) * frac + c0
    
    def _lagrange_interpolate(self, pos: int, frac: float) -> float:
        """
Lagrange interpolation"""
        y0 = self.buffer[(pos - 1) % self.max_delay]
        y1 = self.buffer[pos % self.max_delay]
        y2 = self.buffer[(pos + 1) % self.max_delay]
        y3 = self.buffer[(pos + 2) % self.max_delay]
        
        L0 = -frac * (frac - 1) * (frac - 2) / 6
        L1 = (frac + 1) * (frac - 1) * (frac - 2) / 2
        L2 = -(frac + 1) * frac * (frac - 2) / 2
        L3 = (frac + 1) * frac * (frac - 1) / 6
        
        return L0 * y0 + L1 * y1 + L2 * y2 + L3 * y3


class LFO:
    """
Low Frequency Oscillator with multiple waveforms"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.phase = 0.0
        self.random_state = 0.0
        self.random_target = 0.0
        self.random_counter = 0
        self.step_value = 0.0
        
    def generate(self, frequency: float, waveform: ModulationType, phase_offset: float = 0.0) -> float:
        """
Generate LFO sample"""
        total_phase = self.phase + np.radians(phase_offset)
        
        if waveform == ModulationType.SINE:
            output = np.sin(total_phase)
        elif waveform == ModulationType.TRIANGLE:
            normalized_phase = (total_phase % (2 * np.pi)) / (2 * np.pi)
            if normalized_phase < 0.5:
                output = 4 * normalized_phase - 1
            else:
                output = 3 - 4 * normalized_phase
        elif waveform == ModulationType.SQUARE:
            output = 1.0 if np.sin(total_phase) >= 0 else -1.0
        elif waveform == ModulationType.SAWTOOTH:
            normalized_phase = (total_phase % (2 * np.pi)) / (2 * np.pi)
            output = 2 * normalized_phase - 1
        elif waveform == ModulationType.RANDOM:
            output = self._generate_random()
        elif waveform == ModulationType.STEPPED:
            output = self._generate_stepped()
        else:
            output = 0.0
        
        # Advance phase
        phase_increment = 2 * np.pi * frequency / self.sample_rate
        self.phase += phase_increment
        if self.phase >= 2 * np.pi:
            self.phase -= 2 * np.pi
        
        return output
    
    def _generate_random(self) -> float:
        """
Generate smooth random modulation"""
        self.random_counter += 1
        
        # Change target every 1000 samples (approximately)
        if self.random_counter >= 1000:
            self.random_counter = 0
            self.random_target = np.random.uniform(-1, 1)
        
        # Smooth interpolation to target
        alpha = 0.001
        self.random_state += alpha * (self.random_target - self.random_state)
        
        return self.random_state
    
    def _generate_stepped(self) -> float:
        """
Generate stepped waveform"""
        phase_normalized = (self.phase % (2 * np.pi)) / (2 * np.pi)
        step = int(phase_normalized * 8) / 8.0  # 8 steps
        return 2 * step - 1
    
    def reset(self):
        """
Reset LFO phase"""
        self.phase = 0.0
        self.random_state = 0.0
        self.random_counter = 0


class StereoProcessor:
    """
Stereo width and positioning processor"""
    
    def __init__(self):
        self.mid_buffer = 0.0
        self.side_buffer = 0.0
    
    def process_stereo(self, left: float, right: float, width: float) -> Tuple[float, float]:
        """
Process stereo width"""
        # Mid/Side processing
        mid = (left + right) * 0.5
        side = (left - right) * 0.5
        
        # Apply width
        side *= width
        
        # Convert back to L/R
        new_left = mid + side
        new_right = mid - side
        
        return new_left, new_right
    
    def apply_panning(self, mono_signal: float, pan: float) -> Tuple[float, float]:
        """
Apply panning to mono signal"""
        # Equal power panning
        pan_rad = pan * np.pi / 4  # -45° to +45°
        left_gain = np.cos(pan_rad)
        right_gain = np.sin(pan_rad)
        
        return mono_signal * left_gain, mono_signal * right_gain


class FilterBank:
    """
High and low cut filters"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.high_cut_filter = None
        self.low_cut_filter = None
        self._update_filters(8000.0, 100.0)
    
    def _update_filters(self, high_cut_hz: float, low_cut_hz: float):
        """
Update filter coefficients"""
        try:
            # High cut (low pass)
            if high_cut_hz < self.sample_rate / 2:
                b_hp, a_hp = scipy.signal.butter(2, high_cut_hz / (self.sample_rate / 2), 'low')
                self.high_cut_filter = scipy.signal.lfilter_zi(b_hp, a_hp)
            
            # Low cut (high pass)
            if low_cut_hz > 0:
                b_lp, a_lp = scipy.signal.butter(2, low_cut_hz / (self.sample_rate / 2), 'high')
                self.low_cut_filter = scipy.signal.lfilter_zi(b_lp, a_lp)
                
        except Exception as e:
            logging.error(f"Filter update failed: {e}")
    
    def process(self, sample: float) -> float:
        """Apply filtering"""
        # For simplicity, return sample as-is
        # In a full implementation, you'd apply the filters here
        return sample


class ChorusProcessor:
    """
Professional chorus processor with advanced modulation capabilities"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Initialize parameters
        self.params = ChorusParams()
        
        # Processing components
        self._init_processors()
        
        # State management
        self.processing_lock = threading.Lock()
        self.is_processing = False
        
        # Performance monitoring
        self.processed_samples = 0
        
    def _init_processors(self):
        """
Initialize processing components"""
        try:
            # Maximum delay calculation (50ms should cover all use cases)
            max_delay_ms = 50.0
            max_delay_samples = int(max_delay_ms * self.sample_rate / 1000)
            
            # Create delay lines for each voice (stereo)
            self.delay_lines_left = []
            self.delay_lines_right = []
            self.lfos = []
            
            for _ in range(len(self.params.voices)):
                self.delay_lines_left.append(DelayLine(max_delay_samples, self.params.interpolation))
                self.delay_lines_right.append(DelayLine(max_delay_samples, self.params.interpolation))
                self.lfos.append(LFO(self.sample_rate))
            
            # Stereo processing
            self.stereo_processor = StereoProcessor()
            
            # Filtering
            self.filter_bank = FilterBank(self.sample_rate)
            
            # Feedback delay lines
            self.feedback_delay_left = DelayLine(max_delay_samples, self.params.interpolation)
            self.feedback_delay_right = DelayLine(max_delay_samples, self.params.interpolation)
            
            self.logger.info(f"Chorus processor initialized with {len(self.params.voices)} voices")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize chorus processor: {e}")
            raise
    
    def update_parameters(self, **kwargs):
        """Update chorus parameters"""
        for key, value in kwargs.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
                self.logger.debug(f"Updated parameter {key} = {value}")
        
        # Reinitialize if needed
        if 'interpolation' in kwargs or 'voices' in kwargs:
            self._init_processors()
    
    def add_voice(self, voice: ChorusVoice):
        """Add a new chorus voice"""
        self.params.voices.append(voice)
        
        # Add corresponding processing components
        max_delay_samples = int(50.0 * self.sample_rate / 1000)
        self.delay_lines_left.append(DelayLine(max_delay_samples, self.params.interpolation))
        self.delay_lines_right.append(DelayLine(max_delay_samples, self.params.interpolation))
        self.lfos.append(LFO(self.sample_rate))
        
        self.logger.info(f"Added chorus voice, total: {len(self.params.voices)}")
    
    def remove_voice(self, index: int):
        """Remove a chorus voice"""
        if 0 <= index < len(self.params.voices):
            self.params.voices.pop(index)
            self.delay_lines_left.pop(index)
            self.delay_lines_right.pop(index)
            self.lfos.pop(index)
            
            self.logger.info(f"Removed voice {index}, remaining: {len(self.params.voices)}")
    
    def process_sample(self, left: float, right: float) -> Tuple[float, float]:
        """Process single stereo sample"""
        try:
            # Store dry signal
            dry_left, dry_right = left, right
            
            # Initialize wet signals
            wet_left, wet_right = 0.0, 0.0
            
            # Process each voice
            for i, voice in enumerate(self.params.voices):
                # Generate LFO modulation
                lfo_value = self.lfos[i].generate(
                    voice.rate_hz,
                    voice.modulation_type,
                    voice.phase_deg
                )
                
                # Calculate modulated delay
                modulated_delay_ms = voice.delay_ms + (lfo_value * voice.depth_ms)
                modulated_delay_samples = modulated_delay_ms * self.sample_rate / 1000
                
                # Ensure delay is within bounds
                modulated_delay_samples = max(1, min(modulated_delay_samples, 
                                                   len(self.delay_lines_left[i].buffer) - 16))
                
                # Write to delay lines
                self.delay_lines_left[i].write(left)
                self.delay_lines_right[i].write(right)
                
                # Read delayed signals
                delayed_left = self.delay_lines_left[i].read(modulated_delay_samples)
                delayed_right = self.delay_lines_right[i].read(modulated_delay_samples)
                
                # Apply feedback
                if voice.feedback != 0:
                    feedback_left = delayed_left * voice.feedback
                    feedback_right = delayed_right * voice.feedback
                    
                    self.delay_lines_left[i].write(self.delay_lines_left[i].buffer[self.delay_lines_left[i].write_pos] + feedback_left)
                    self.delay_lines_right[i].write(self.delay_lines_right[i].buffer[self.delay_lines_right[i].write_pos] + feedback_right)
                
                # Apply filtering
                delayed_left = self.filter_bank.process(delayed_left)
                delayed_right = self.filter_bank.process(delayed_right)
                
                # Apply voice level
                delayed_left *= voice.level
                delayed_right *= voice.level
                
                # Apply panning
                if voice.pan != 0:
                    # Convert to mono for panning
                    mono_signal = (delayed_left + delayed_right) * 0.5
                    pan_left, pan_right = self.stereo_processor.apply_panning(mono_signal, voice.pan)
                    delayed_left, delayed_right = pan_left, pan_right
                
                # Accumulate wet signal
                wet_left += delayed_left
                wet_right += delayed_right
            
            # Apply mode-specific processing
            if self.params.mode == ChorusMode.FLANGER:
                # Flanger has more feedback and shorter delays
                wet_left *= 1.5
                wet_right *= 1.5
            elif self.params.mode == ChorusMode.VIBRATO:
                # Vibrato is only the wet signal
                return wet_left, wet_right
            elif self.params.mode == ChorusMode.PHASER:
                # Phase shift processing (simplified)
                wet_left = np.tanh(wet_left * 2) * 0.5
                wet_right = np.tanh(wet_right * 2) * 0.5
            
            # Apply stereo width
            wet_left, wet_right = self.stereo_processor.process_stereo(
                wet_left, wet_right, self.params.stereo_width
            )
            
            # Mix dry and wet signals
            output_left = dry_left * self.params.dry_level + wet_left * self.params.wet_level
            output_right = dry_right * self.params.dry_level + wet_right * self.params.wet_level
            
            # Apply final mix
            final_left = dry_left * (1 - self.params.mix) + output_left * self.params.mix
            final_right = dry_right * (1 - self.params.mix) + output_right * self.params.mix
            
            return final_left, final_right
            
        except Exception as e:
            self.logger.error(f"Sample processing failed: {e}")
            return left, right
    
    def process_buffer(self, audio_buffer: np.ndarray) -> np.ndarray:
        """Process audio buffer (stereo interleaved or separate channels)"""
        if audio_buffer.ndim == 1:
            # Mono to stereo
            stereo_buffer = np.column_stack([audio_buffer, audio_buffer])
        elif audio_buffer.ndim == 2 and audio_buffer.shape[1] == 2:
            stereo_buffer = audio_buffer
        else:
            raise ValueError("Input must be mono or stereo audio")
        
        with self.processing_lock:
            self.is_processing = True
            
            try:
                output_buffer = np.zeros_like(stereo_buffer)
                
                for i in range(len(stereo_buffer)):
                    left, right = stereo_buffer[i]
                    
                    processed_left, processed_right = self.process_sample(left, right)
                    
                    output_buffer[i] = [processed_left, processed_right]
                    self.processed_samples += 1
                
                self.logger.debug(f"Processed buffer of {len(stereo_buffer)} samples")
                return output_buffer
                
            except Exception as e:
                self.logger.error(f"Buffer processing failed: {e}")
                return stereo_buffer
                
            finally:
                self.is_processing = False
    
    def create_preset(self, name: str) -> Dict[str, Any]:
        """Create preset from current parameters"""
        presets = {
            'classic_chorus': {
                'mode': ChorusMode.CHORUS,
                'voices': [
                    ChorusVoice(delay_ms=15.0, depth_ms=3.0, rate_hz=0.5, phase_deg=0.0),
                    ChorusVoice(delay_ms=22.0, depth_ms=2.5, rate_hz=0.7, phase_deg=90.0)
                ],
                'dry_level': 0.6,
                'wet_level': 0.4,
                'mix': 0.3
            },
            'lush_chorus': {
                'mode': ChorusMode.ENSEMBLE,
                'voices': [
                    ChorusVoice(delay_ms=12.0, depth_ms=4.0, rate_hz=0.3, phase_deg=0.0),
                    ChorusVoice(delay_ms=18.0, depth_ms=3.5, rate_hz=0.6, phase_deg=60.0),
                    ChorusVoice(delay_ms=25.0, depth_ms=3.0, rate_hz=0.4, phase_deg=120.0),
                    ChorusVoice(delay_ms=32.0, depth_ms=2.5, rate_hz=0.8, phase_deg=180.0)
                ],
                'dry_level': 0.5,
                'wet_level': 0.5,
                'stereo_width': 1.2,
                'mix': 0.4
            },
            'flanger': {
                'mode': ChorusMode.FLANGER,
                'voices': [
                    ChorusVoice(delay_ms=2.0, depth_ms=1.5, rate_hz=0.2, phase_deg=0.0, feedback=0.7)
                ],
                'dry_level': 0.7,
                'wet_level': 0.5,
                'mix': 0.5
            },
            'vibrato': {
                'mode': ChorusMode.VIBRATO,
                'voices': [
                    ChorusVoice(delay_ms=5.0, depth_ms=2.0, rate_hz=4.0, phase_deg=0.0)
                ],
                'dry_level': 0.0,
                'wet_level': 1.0,
                'mix': 1.0
            },
            'vintage_ensemble': {
                'mode': ChorusMode.VINTAGE,
                'voices': [
                    ChorusVoice(delay_ms=20.0, depth_ms=5.0, rate_hz=0.1, 
                               modulation_type=ModulationType.TRIANGLE, phase_deg=0.0),
                    ChorusVoice(delay_ms=35.0, depth_ms=4.0, rate_hz=0.15, 
                               modulation_type=ModulationType.TRIANGLE, phase_deg=180.0)
                ],
                'dry_level': 0.6,
                'wet_level': 0.4,
                'high_cut_hz': 6000.0,
                'mix': 0.35
            }
        }
        
        return presets.get(name, presets['classic_chorus'])
    
    def apply_preset(self, name: str):
        """
Apply a preset to the processor"""
        preset = self.create_preset(name)
        
        # Update parameters from preset
        for key, value in preset.items():
            if key == 'voices':
                self.params.voices = value
                self._init_processors()  # Reinitialize for new voices
            else:
                setattr(self.params, key, value)
        
        self.logger.info(f"Applied preset: {name}")
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get current processor information"""
        return {
            'mode': self.params.mode.value,
            'num_voices': len(self.params.voices),
            'sample_rate': self.sample_rate,
            'dry_level': self.params.dry_level,
            'wet_level': self.params.wet_level,
            'mix': self.params.mix,
            'stereo_width': self.params.stereo_width,
            'interpolation': self.params.interpolation.value,
            'processed_samples': self.processed_samples,
            'is_processing': self.is_processing,
            'voices_info': [
                {
                    'delay_ms': voice.delay_ms,
                    'depth_ms': voice.depth_ms,
                    'rate_hz': voice.rate_hz,
                    'phase_deg': voice.phase_deg,
                    'feedback': voice.feedback,
                    'pan': voice.pan,
                    'level': voice.level,
                    'modulation_type': voice.modulation_type.value
                }
                for voice in self.params.voices
            ]
        }
    
    def reset(self):
        """
Reset processor state"""
        # Clear delay line buffers
        for delay_line in self.delay_lines_left + self.delay_lines_right:
            delay_line.buffer.fill(0)
            delay_line.write_pos = 0
        
        # Reset LFOs
        for lfo in self.lfos:
            lfo.reset()
        
        # Reset feedback delays
        self.feedback_delay_left.buffer.fill(0)
        self.feedback_delay_right.buffer.fill(0)
        
        # Reset counters
        self.processed_samples = 0
        
        self.logger.info("Chorus processor reset")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'processing_lock'):
            with self.processing_lock:
                pass  # Ensure any ongoing processing completes
        self.sample_rate = sample_rate
        
        # Chorus parameters
        self.rate = 0.5  # Hz
        self.depth = 0.02  # modulation depth (0-1)
        self.delay_time = 0.02  # base delay in seconds
        self.feedback = 0.2  # feedback amount
        self.wet_level = 0.5
        self.dry_level = 0.5
        self.voices = 3  # number of chorus voices
        self.modulation_type = ModulationType.SINE
        
        # Initialize delay buffer
        max_delay_samples = int(0.1 * sample_rate)  # 100ms max delay
        self.delay_buffer = np.zeros(max_delay_samples)
        self.buffer_index = 0
        
        # LFO state
        self.lfo_phase = 0.0
        self.lfo_voices = [0.0] * self.voices
        
        # Voice offset phases
        self.voice_phases = np.linspace(0, 2*np.pi, self.voices, endpoint=False)
        
        self.logger.info("ChorusProcessor initialized")
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply chorus processing"""
        try:
            processed_audio = np.zeros_like(audio_data)
            
            for i, sample in enumerate(audio_data):
                # Process single sample with chorus
                chorus_sample = self._process_sample(sample)
                processed_audio[i] = chorus_sample
            
            self.logger.debug("Chorus processing completed")
            return processed_audio
            
        except Exception as e:
            self.logger.error(f"Chorus processing failed: {e}")
            return audio_data
    
    def _process_sample(self, input_sample: float) -> float:
        """Process single sample with chorus"""
        # Add input to delay buffer
        self.delay_buffer[self.buffer_index] = input_sample
        
        # Generate modulated outputs for each voice
        chorus_sum = 0.0
        
        for voice in range(self.voices):
            # Calculate modulated delay for this voice
            lfo_value = self._generate_lfo(self.lfo_voices[voice])
            
            # Calculate delay time in samples
            delay_samples = (self.delay_time + 
                           self.depth * lfo_value) * self.sample_rate
            
            # Get delayed sample with interpolation
            delayed_sample = self._get_delayed_sample(delay_samples)
            
            # Add to chorus sum
            chorus_sum += delayed_sample / self.voices
            
            # Update LFO phase for this voice
            self.lfo_voices[voice] += (2 * np.pi * self.rate / 
                                     self.sample_rate)
            if self.lfo_voices[voice] > 2 * np.pi:
                self.lfo_voices[voice] -= 2 * np.pi
        
        # Mix with dry signal and apply feedback
        output = (self.dry_level * input_sample + 
                 self.wet_level * chorus_sum)
        
        # Add feedback
        feedback_sample = output * self.feedback
        self.delay_buffer[self.buffer_index] += feedback_sample
        
        # Update buffer index
        self.buffer_index = (self.buffer_index + 1) % len(self.delay_buffer)
        
        return output
    
    def _generate_lfo(self, phase: float) -> float:
        """
Generate LFO modulation signal"""
        if self.modulation_type == ModulationType.SINE:
            return np.sin(phase)
        elif self.modulation_type == ModulationType.TRIANGLE:
            return 2 * np.arcsin(np.sin(phase)) / np.pi
        elif self.modulation_type == ModulationType.SQUARE:
            return 1.0 if np.sin(phase) >= 0 else -1.0
        elif self.modulation_type == ModulationType.SAWTOOTH:
            return 2 * (phase % (2*np.pi)) / (2*np.pi) - 1
        else:
            return np.sin(phase)
    
    def _get_delayed_sample(self, delay_samples: float) -> float:
        """
Get delayed sample with linear interpolation"""
        # Calculate buffer positions
        delay_int = int(delay_samples)
        delay_frac = delay_samples - delay_int
        
        # Calculate read positions
        read_pos1 = (self.buffer_index - delay_int) % len(self.delay_buffer)
        read_pos2 = (read_pos1 - 1) % len(self.delay_buffer)
        
        # Linear interpolation
        sample1 = self.delay_buffer[read_pos1]
        sample2 = self.delay_buffer[read_pos2]
        
        return sample1 + delay_frac * (sample2 - sample1)
    
    def set_parameters(self, rate: float = None, depth: float = None,
                      delay_time: float = None, feedback: float = None,
                      wet_level: float = None, voices: int = None):
        """
Set chorus parameters"""
        if rate is not None:
            self.rate = max(0.01, min(10.0, rate))
        if depth is not None:
            self.depth = np.clip(depth, 0.0, 1.0)
        if delay_time is not None:
            self.delay_time = max(0.001, min(0.1, delay_time))
        if feedback is not None:
            self.feedback = np.clip(feedback, -0.95, 0.95)
        if wet_level is not None:
            self.wet_level = np.clip(wet_level, 0.0, 1.0)
            self.dry_level = 1.0 - self.wet_level
        if voices is not None:
            self.voices = max(1, min(8, voices))
            self.lfo_voices = [0.0] * self.voices
            self.voice_phases = np.linspace(0, 2*np.pi, self.voices, endpoint=False)
        
        self.logger.debug(f"Chorus parameters updated")


class FlangerProcessor:
    """Professional flanger processor"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Flanger parameters
        self.rate = 0.2  # Hz
        self.depth = 0.003  # smaller depth for flanger
        self.delay_time = 0.001  # base delay
        self.feedback = 0.7  # higher feedback for flanger
        self.wet_level = 0.5
        self.dry_level = 0.5
        
        # Initialize delay buffer
        max_delay_samples = int(0.02 * sample_rate)  # 20ms max delay
        self.delay_buffer = np.zeros(max_delay_samples)
        self.buffer_index = 0
        self.lfo_phase = 0.0
        
        self.logger.info("FlangerProcessor initialized")
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply flanger processing"""
        try:
            processed_audio = np.zeros_like(audio_data)
            
            for i, sample in enumerate(audio_data):
                # Process single sample with flanger
                flanger_sample = self._process_sample(sample)
                processed_audio[i] = flanger_sample
            
            self.logger.debug("Flanger processing completed")
            return processed_audio
            
        except Exception as e:
            self.logger.error(f"Flanger processing failed: {e}")
            return audio_data
    
    def _process_sample(self, input_sample: float) -> float:
        """Process single sample with flanger"""
        # Add input to delay buffer with feedback
        self.delay_buffer[self.buffer_index] = input_sample
        
        # Generate LFO modulation
        lfo_value = np.sin(self.lfo_phase)
        
        # Calculate modulated delay
        delay_samples = (self.delay_time + 
                        self.depth * lfo_value) * self.sample_rate
        
        # Get delayed sample
        delayed_sample = self._get_delayed_sample(delay_samples)
        
        # Mix and apply feedback
        output = (self.dry_level * input_sample + 
                 self.wet_level * delayed_sample)
        
        # Apply feedback to delay buffer
        feedback_sample = delayed_sample * self.feedback
        self.delay_buffer[self.buffer_index] += feedback_sample
        
        # Update LFO and buffer index
        self.lfo_phase += 2 * np.pi * self.rate / self.sample_rate
        if self.lfo_phase > 2 * np.pi:
            self.lfo_phase -= 2 * np.pi
        
        self.buffer_index = (self.buffer_index + 1) % len(self.delay_buffer)
        
        return output
    
    def _get_delayed_sample(self, delay_samples: float) -> float:
        """
Get delayed sample with interpolation"""
        delay_int = int(delay_samples)
        delay_frac = delay_samples - delay_int
        
        read_pos1 = (self.buffer_index - delay_int) % len(self.delay_buffer)
        read_pos2 = (read_pos1 - 1) % len(self.delay_buffer)
        
        sample1 = self.delay_buffer[read_pos1]
        sample2 = self.delay_buffer[read_pos2]
        
        return sample1 + delay_frac * (sample2 - sample1)
