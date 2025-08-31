"""🎵 Pitch Shifter Processor - Professional Pitch Manipulation Engine

Advanced pitch shifting with multiple algorithms including phase vocoder,
PSOLA, granular synthesis, formant preservation, and real-time modulation.
Supports both musical and voice processing applications.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
import logging
from typing import Optional, Tuple, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
import scipy.signal
import scipy.fft
import scipy.interpolate
import threading


class PitchShiftAlgorithm(Enum):
    """Pitch shifting algorithm types"""
    PHASE_VOCODER = "phase_vocoder"
    PSOLA = "psola"
    GRANULAR = "granular"
    SPECTRAL = "spectral"
    HARMONIC = "harmonic"


class WindowType(Enum):
    """Window function types"""
    HANNING = "hanning"
    HAMMING = "hamming"
    BLACKMAN = "blackman"
    KAISER = "kaiser"


@dataclass
class PitchShiftParams:
    """Pitch shifter parameters"""
    algorithm: PitchShiftAlgorithm = PitchShiftAlgorithm.PHASE_VOCODER
    pitch_shift_cents: float = 0.0  # -1200 to +1200 cents
    formant_shift: float = 0.0  # -12 to +12 semitones
    preserve_formants: bool = True
    time_stretch_ratio: float = 1.0  # 0.5 to 2.0
    window_size: int = 2048
    hop_size: int = 512
    window_type: WindowType = WindowType.HANNING
    overlap_factor: float = 4.0
    
    # Quality settings
    quality_mode: str = "balanced"  # "fast", "balanced", "high"
    anti_aliasing: bool = True
    
    # Modulation
    pitch_modulation_rate: float = 0.0  # Hz
    pitch_modulation_depth: float = 0.0  # cents
    
    # Mix
    dry_level: float = 0.0
    wet_level: float = 1.0


class PhaseVocoder:
    """Phase vocoder for high-quality pitch shifting"""
    
    def __init__(self, frame_size: int, hop_size: int, sample_rate: int):
        self.frame_size = frame_size
        self.hop_size = hop_size
        self.sample_rate = sample_rate
        
        # Analysis and synthesis windows
        self.analysis_window = np.hanning(frame_size)
        self.synthesis_window = np.hanning(frame_size)
        
        # Overlap-add buffers
        self.input_buffer = np.zeros(frame_size * 2)
        self.output_buffer = np.zeros(frame_size * 2)
        
        # Phase accumulator
        self.phase_accumulator = np.zeros(frame_size // 2 + 1)
        self.previous_phase = np.zeros(frame_size // 2 + 1)
        
        # Frequency bins
        self.freq_bins = np.fft.fftfreq(frame_size, 1/sample_rate)[:frame_size//2 + 1]
        
    def process_frame(self, input_frame: np.ndarray, pitch_factor: float) -> np.ndarray:
        """Process single frame with phase vocoder"""
        # Apply analysis window
        windowed = input_frame * self.analysis_window
        
        # FFT analysis
        spectrum = np.fft.fft(windowed)
        magnitude = np.abs(spectrum[:self.frame_size // 2 + 1])
        phase = np.angle(spectrum[:self.frame_size // 2 + 1])
        
        # Phase unwrapping and modification
        phase_diff = phase - self.previous_phase
        phase_diff = np.unwrap(phase_diff)
        
        # Calculate instantaneous frequency
        inst_freq = self.freq_bins + phase_diff * self.sample_rate / (2 * np.pi * self.hop_size)
        
        # Pitch shift the frequencies
        shifted_freq = inst_freq * pitch_factor
        
        # Update phase accumulator
        self.phase_accumulator += shifted_freq * 2 * np.pi * self.hop_size / self.sample_rate
        
        # Reconstruct spectrum
        shifted_spectrum = magnitude * np.exp(1j * self.phase_accumulator)
        
        # Create full spectrum (mirrored for real IFFT)
        full_spectrum = np.zeros(self.frame_size, dtype=complex)
        full_spectrum[:self.frame_size // 2 + 1] = shifted_spectrum
        full_spectrum[self.frame_size // 2 + 1:] = np.conj(shifted_spectrum[1:self.frame_size // 2][::-1])
        
        # IFFT synthesis
        output_frame = np.real(np.fft.ifft(full_spectrum))
        
        # Apply synthesis window
        output_frame *= self.synthesis_window
        
        # Store previous phase
        self.previous_phase = phase
        
        return output_frame


class PSOLAProcessor:
    """Pitch Synchronous Overlap and Add processor"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.pitch_marks = []
        self.grain_size = 2048
        self.overlap_factor = 0.5
        
    def detect_pitch_marks(self, signal: np.ndarray, 
                          min_pitch: float = 80.0, 
                          max_pitch: float = 400.0) -> List[int]:
        """Detect pitch marks using autocorrelation"""
        pitch_marks = []
        
        # Calculate correlation window size
        min_period = int(self.sample_rate / max_pitch)
        max_period = int(self.sample_rate / min_pitch)
        
        # Process in overlapping frames
        frame_size = max_period * 2
        hop_size = frame_size // 4
        
        for i in range(0, len(signal) - frame_size, hop_size):
            frame = signal[i:i + frame_size]
            
            # Autocorrelation
            correlation = np.correlate(frame, frame, mode='full')
            correlation = correlation[len(correlation)//2:]
            
            # Find peak in valid pitch range
            valid_range = correlation[min_period:max_period]
            if len(valid_range) > 0:
                peak_idx = np.argmax(valid_range) + min_period
                pitch_marks.append(i + peak_idx)
        
        return pitch_marks
    
    def shift_pitch(self, signal: np.ndarray, pitch_factor: float) -> np.ndarray:
        """Apply PSOLA pitch shifting"""
        if pitch_factor == 1.0:
            return signal
        
        # Detect pitch marks
        self.pitch_marks = self.detect_pitch_marks(signal)
        
        if len(self.pitch_marks) < 2:
            return signal  # Not enough pitch marks
        
        # Calculate new timing
        output_length = int(len(signal) / pitch_factor)
        output = np.zeros(output_length)
        
        # Overlap-add grains at new positions
        for i in range(len(self.pitch_marks) - 1):
            # Extract grain
            start = max(0, self.pitch_marks[i] - self.grain_size // 2)
            end = min(len(signal), self.pitch_marks[i] + self.grain_size // 2)
            grain = signal[start:end]
            
            # Apply window
            window = np.hanning(len(grain))
            windowed_grain = grain * window
            
            # Calculate output position
            output_pos = int(self.pitch_marks[i] / pitch_factor)
            
            # Add grain to output
            out_start = max(0, output_pos - len(windowed_grain) // 2)
            out_end = min(len(output), out_start + len(windowed_grain))
            
            if out_end > out_start:
                grain_start = max(0, -out_start + output_pos - len(windowed_grain) // 2)
                grain_end = grain_start + (out_end - out_start)
                
                if grain_end <= len(windowed_grain):
                    output[out_start:out_end] += windowed_grain[grain_start:grain_end]
        
        return output


class GranularProcessor:
    """Granular synthesis-based pitch shifter"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.grain_size = 1024
        self.grain_overlap = 0.75
        self.grains_buffer = []
        
    def create_grain(self, signal: np.ndarray, position: int, 
                    size: int, pitch_factor: float) -> np.ndarray:
        """Create a single grain"""
        # Extract grain
        start = max(0, position - size // 2)
        end = min(len(signal), start + size)
        grain = signal[start:end]
        
        # Pad if necessary
        if len(grain) < size:
            grain = np.pad(grain, (0, size - len(grain)))
        
        # Apply window
        window = np.hanning(size)
        windowed_grain = grain * window
        
        # Pitch shift using resampling
        if pitch_factor != 1.0:
            # Simple resampling for granular approach
            new_length = int(len(windowed_grain) / pitch_factor)
            indices = np.linspace(0, len(windowed_grain) - 1, new_length)
            windowed_grain = np.interp(indices, np.arange(len(windowed_grain)), windowed_grain)
        
        return windowed_grain
    
    def process(self, signal: np.ndarray, pitch_factor: float) -> np.ndarray:
        """Process signal with granular synthesis"""
        output_length = int(len(signal) / pitch_factor)
        output = np.zeros(output_length)
        
        # Calculate grain spacing
        grain_advance = int(self.grain_size * (1 - self.grain_overlap))
        
        # Generate grains
        for pos in range(0, len(signal) - self.grain_size, grain_advance):
            grain = self.create_grain(signal, pos, self.grain_size, pitch_factor)
            
            # Calculate output position
            output_pos = int(pos / pitch_factor)
            
            # Add grain to output
            end_pos = min(len(output), output_pos + len(grain))
            if output_pos < len(output) and end_pos > output_pos:
                output[output_pos:end_pos] += grain[:end_pos - output_pos]
        
        return output


class FormantPreserver:
    """Formant preservation for natural voice processing"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.envelope_follower = None
        
    def extract_spectral_envelope(self, spectrum: np.ndarray, 
                                 decimation_factor: int = 8) -> np.ndarray:
        """Extract spectral envelope using cepstral analysis"""
        # Convert to log magnitude
        log_magnitude = np.log(np.abs(spectrum) + 1e-10)
        
        # Real cepstrum
        cepstrum = np.fft.ifft(log_magnitude).real
        
        # Keep only low quefrency components (formant info)
        liftered_cepstrum = cepstrum.copy()
        liftered_cepstrum[len(cepstrum)//decimation_factor:] = 0
        
        # Back to frequency domain
        envelope = np.exp(np.fft.fft(liftered_cepstrum).real)
        
        return envelope[:len(spectrum)]
    
    def preserve_formants(self, original_spectrum: np.ndarray, 
                         shifted_spectrum: np.ndarray) -> np.ndarray:
        """Apply formant preservation"""
        # Extract envelopes
        original_envelope = self.extract_spectral_envelope(original_spectrum)
        shifted_envelope = self.extract_spectral_envelope(shifted_spectrum)
        
        # Calculate correction
        correction = original_envelope / (shifted_envelope + 1e-10)
        
        # Apply correction
        preserved_spectrum = shifted_spectrum * correction
        
        return preserved_spectrum


class PitchShifterProcessor:
    """Professional pitch shifter with multiple algorithms"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Initialize parameters
        self.params = PitchShiftParams()
        
        # Processing components
        self._init_processors()
        
        # State management
        self.processing_lock = threading.Lock()
        self.processed_samples = 0
        
        # LFO for pitch modulation
        self.lfo_phase = 0.0
        
    def _init_processors(self):
        """Initialize processing components"""
        try:
            self.phase_vocoder = PhaseVocoder(
                self.params.window_size,
                self.params.hop_size,
                self.sample_rate
            )
            self.psola_processor = PSOLAProcessor(self.sample_rate)
            self.granular_processor = GranularProcessor(self.sample_rate)
            self.formant_preserver = FormantPreserver(self.sample_rate)
            
            # Processing buffers
            self.input_buffer = np.zeros(self.params.window_size * 2)
            self.output_buffer = np.zeros(self.params.window_size * 2)
            
            self.logger.info(f"Pitch shifter initialized with {self.params.algorithm.value} algorithm")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pitch shifter: {e}")
            raise
    
    def update_parameters(self, **kwargs):
        """Update pitch shifter parameters"""
        for key, value in kwargs.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
                self.logger.debug(f"Updated parameter {key} = {value}")
        
        # Reinitialize if needed
        if any(key in kwargs for key in ['algorithm', 'window_size', 'hop_size']):
            self._init_processors()
    
    def cents_to_ratio(self, cents: float) -> float:
        """Convert cents to frequency ratio"""
        return 2.0 ** (cents / 1200.0)
    
    def generate_pitch_modulation(self) -> float:
        """Generate LFO modulation for pitch"""
        if self.params.pitch_modulation_rate <= 0:
            return 0.0
        
        # Generate sine LFO
        lfo_value = np.sin(self.lfo_phase)
        
        # Advance phase
        self.lfo_phase += 2 * np.pi * self.params.pitch_modulation_rate / self.sample_rate
        if self.lfo_phase >= 2 * np.pi:
            self.lfo_phase -= 2 * np.pi
        
        return lfo_value * self.params.pitch_modulation_depth
    
    def process_buffer(self, audio_buffer: np.ndarray) -> np.ndarray:
        """Process audio buffer with pitch shifting"""
        with self.processing_lock:
            try:
                # Calculate pitch shift ratio including modulation
                base_cents = self.params.pitch_shift_cents
                modulation_cents = self.generate_pitch_modulation()
                total_cents = base_cents + modulation_cents
                pitch_ratio = self.cents_to_ratio(total_cents)
                
                # Store dry signal
                dry_signal = audio_buffer.copy()
                
                # Select algorithm and process
                if self.params.algorithm == PitchShiftAlgorithm.PHASE_VOCODER:
                    shifted = self._process_phase_vocoder(audio_buffer, pitch_ratio)
                
                elif self.params.algorithm == PitchShiftAlgorithm.PSOLA:
                    shifted = self.psola_processor.shift_pitch(audio_buffer, pitch_ratio)
                
                elif self.params.algorithm == PitchShiftAlgorithm.GRANULAR:
                    shifted = self.granular_processor.process(audio_buffer, pitch_ratio)
                
                elif self.params.algorithm == PitchShiftAlgorithm.SPECTRAL:
                    shifted = self._process_spectral(audio_buffer, pitch_ratio)
                
                elif self.params.algorithm == PitchShiftAlgorithm.HARMONIC:
                    shifted = self._process_harmonic(audio_buffer, pitch_ratio)
                
                else:
                    shifted = audio_buffer
                
                # Ensure output length matches input
                if len(shifted) != len(audio_buffer):
                    # Resample to match original length
                    indices = np.linspace(0, len(shifted) - 1, len(audio_buffer))
                    shifted = np.interp(indices, np.arange(len(shifted)), shifted)
                
                # Mix dry and wet signals
                output = dry_signal * self.params.dry_level + shifted * self.params.wet_level
                
                self.processed_samples += len(output)
                
                return output
                
            except Exception as e:
                self.logger.error(f"Buffer processing failed: {e}")
                return audio_buffer
    
    def _process_phase_vocoder(self, signal: np.ndarray, pitch_ratio: float) -> np.ndarray:
        """Process with phase vocoder"""
        output = np.zeros_like(signal)
        
        # Process in overlapping frames
        hop_out = int(self.params.hop_size * pitch_ratio)
        
        for i in range(0, len(signal) - self.params.window_size, self.params.hop_size):
            frame = signal[i:i + self.params.window_size]
            processed_frame = self.phase_vocoder.process_frame(frame, pitch_ratio)
            
            # Overlap-add
            start_out = int(i * pitch_ratio)
            end_out = start_out + self.params.window_size
            
            if end_out <= len(output):
                output[start_out:end_out] += processed_frame
        
        return output
    
    def _process_spectral(self, signal: np.ndarray, pitch_ratio: float) -> np.ndarray:
        """Process with spectral interpolation"""
        # FFT-based pitch shifting
        spectrum = np.fft.fft(signal)
        magnitude = np.abs(spectrum)
        phase = np.angle(spectrum)
        
        # Create new frequency bins
        new_bins = np.arange(len(spectrum)) / pitch_ratio
        
        # Interpolate magnitude spectrum
        shifted_magnitude = np.interp(
            np.arange(len(spectrum)),
            new_bins,
            magnitude,
            left=0, right=0
        )
        
        # Reconstruct spectrum
        shifted_spectrum = shifted_magnitude * np.exp(1j * phase)
        
        # IFFT
        output = np.real(np.fft.ifft(shifted_spectrum))
        
        # Apply formant preservation if enabled
        if self.params.preserve_formants:
            original_spectrum = np.fft.fft(signal)
            output_spectrum = np.fft.fft(output)
            preserved_spectrum = self.formant_preserver.preserve_formants(
                original_spectrum, output_spectrum
            )
            output = np.real(np.fft.ifft(preserved_spectrum))
        
        return output
    
    def _process_harmonic(self, signal: np.ndarray, pitch_ratio: float) -> np.ndarray:
        """Process with harmonic analysis/synthesis"""
        # Analyze harmonics
        spectrum = np.fft.fft(signal)
        magnitude = np.abs(spectrum)
        phase = np.angle(spectrum)
        
        # Find harmonic peaks
        peaks, _ = scipy.signal.find_peaks(magnitude, height=np.max(magnitude) * 0.1)
        
        # Shift harmonic frequencies
        shifted_spectrum = np.zeros_like(spectrum)
        
        for peak in peaks:
            new_peak = int(peak * pitch_ratio)
            if new_peak < len(shifted_spectrum):
                # Copy harmonic content
                shifted_spectrum[new_peak] = spectrum[peak]
        
        # IFFT
        output = np.real(np.fft.ifft(shifted_spectrum))
        
        return output
    
    def create_preset(self, name: str) -> Dict[str, Any]:
        """Create pitch shifter presets"""
        presets = {
            'octave_up': {
                'algorithm': PitchShiftAlgorithm.PHASE_VOCODER,
                'pitch_shift_cents': 1200.0,
                'preserve_formants': False,
                'quality_mode': 'high',
                'wet_level': 1.0,
                'dry_level': 0.0
            },
            'octave_down': {
                'algorithm': PitchShiftAlgorithm.PHASE_VOCODER,
                'pitch_shift_cents': -1200.0,
                'preserve_formants': False,
                'quality_mode': 'high',
                'wet_level': 1.0,
                'dry_level': 0.0
            },
            'fifth_up': {
                'algorithm': PitchShiftAlgorithm.SPECTRAL,
                'pitch_shift_cents': 700.0,
                'preserve_formants': True,
                'quality_mode': 'balanced',
                'wet_level': 0.8,
                'dry_level': 0.5
            },
            'voice_male_to_female': {
                'algorithm': PitchShiftAlgorithm.PSOLA,
                'pitch_shift_cents': 600.0,
                'formant_shift': 3.0,
                'preserve_formants': True,
                'quality_mode': 'high',
                'wet_level': 1.0,
                'dry_level': 0.0
            },
            'voice_female_to_male': {
                'algorithm': PitchShiftAlgorithm.PSOLA,
                'pitch_shift_cents': -400.0,
                'formant_shift': -2.0,
                'preserve_formants': True,
                'quality_mode': 'high',
                'wet_level': 1.0,
                'dry_level': 0.0
            },
            'chipmunk': {
                'algorithm': PitchShiftAlgorithm.GRANULAR,
                'pitch_shift_cents': 800.0,
                'time_stretch_ratio': 1.2,
                'preserve_formants': False,
                'quality_mode': 'fast',
                'wet_level': 1.0,
                'dry_level': 0.0
            },
            'chorus_harmony': {
                'algorithm': PitchShiftAlgorithm.HARMONIC,
                'pitch_shift_cents': 400.0,
                'preserve_formants': True,
                'pitch_modulation_rate': 0.5,
                'pitch_modulation_depth': 20.0,
                'wet_level': 0.6,
                'dry_level': 0.8
            },
            'subtle_correction': {
                'algorithm': PitchShiftAlgorithm.SPECTRAL,
                'pitch_shift_cents': 0.0,
                'preserve_formants': True,
                'pitch_modulation_rate': 0.0,
                'quality_mode': 'high',
                'wet_level': 1.0,
                'dry_level': 0.0
            }
        }
        
        return presets.get(name, presets['subtle_correction'])
    
    def apply_preset(self, name: str):
        """Apply a preset to the processor"""
        preset = self.create_preset(name)
        
        # Update parameters from preset
        for key, value in preset.items():
            if hasattr(self.params, key):
                if key == 'algorithm':
                    setattr(self.params, key, PitchShiftAlgorithm(value))
                else:
                    setattr(self.params, key, value)
        
        self.update_parameters()
        self.logger.info(f"Applied preset: {name}")
    
    def analyze_pitch(self, signal: np.ndarray, 
                     frame_size: int = 2048) -> Dict[str, float]:
        """Analyze pitch characteristics of input signal"""
        try:
            # Autocorrelation-based pitch detection
            correlation = np.correlate(signal, signal, mode='full')
            correlation = correlation[len(correlation)//2:]
            
            # Find fundamental frequency
            min_period = int(self.sample_rate / 800)  # Max 800 Hz
            max_period = int(self.sample_rate / 80)   # Min 80 Hz
            
            valid_correlation = correlation[min_period:max_period]
            if len(valid_correlation) > 0:
                fundamental_period = np.argmax(valid_correlation) + min_period
                fundamental_freq = self.sample_rate / fundamental_period
            else:
                fundamental_freq = 0.0
            
            # Calculate pitch confidence
            max_corr = np.max(valid_correlation) if len(valid_correlation) > 0 else 0
            mean_corr = np.mean(correlation[min_period:max_period*2])
            confidence = max_corr / (mean_corr + 1e-10)
            
            # Spectral analysis for harmonics
            spectrum = np.abs(np.fft.fft(signal[:frame_size]))
            spectral_peak = np.argmax(spectrum[:frame_size//2])
            spectral_freq = spectral_peak * self.sample_rate / frame_size
            
            return {
                'fundamental_frequency': fundamental_freq,
                'spectral_peak_frequency': spectral_freq,
                'pitch_confidence': min(confidence, 1.0),
                'is_voiced': confidence > 0.3
            }
            
        except Exception as e:
            self.logger.error(f"Pitch analysis failed: {e}")
            return {'fundamental_frequency': 0.0, 'pitch_confidence': 0.0}
    
    def auto_tune(self, signal: np.ndarray, 
                  target_notes: List[float] = None) -> np.ndarray:
        """Automatic pitch correction to nearest musical note"""
        if target_notes is None:
            # Standard 12-TET chromatic scale (A4 = 440Hz)
            target_notes = [440.0 * (2 ** (i/12)) for i in range(-9, 3)]  # C4 to B4
        
        # Analyze current pitch
        pitch_info = self.analyze_pitch(signal)
        
        if not pitch_info['is_voiced'] or pitch_info['fundamental_frequency'] <= 0:
            return signal  # Not a tonal signal
        
        current_freq = pitch_info['fundamental_frequency']
        
        # Find nearest target note
        distances = [abs(current_freq - target) for target in target_notes]
        nearest_note = target_notes[np.argmin(distances)]
        
        # Calculate required pitch shift
        pitch_ratio = nearest_note / current_freq
        cents_shift = 1200 * np.log2(pitch_ratio)
        
        # Apply correction if significant
        if abs(cents_shift) > 5.0:  # Only correct if more than 5 cents off
            original_cents = self.params.pitch_shift_cents
            self.params.pitch_shift_cents = cents_shift
            
            corrected = self.process_buffer(signal)
            
            # Restore original setting
            self.params.pitch_shift_cents = original_cents
            
            self.logger.info(f"Auto-tuned: {current_freq:.1f}Hz -> {nearest_note:.1f}Hz ({cents_shift:+.1f} cents)")
            return corrected
        
        return signal
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get current processor information"""
        return {
            'algorithm': self.params.algorithm.value,
            'pitch_shift_cents': self.params.pitch_shift_cents,
            'formant_shift': self.params.formant_shift,
            'preserve_formants': self.params.preserve_formants,
            'time_stretch_ratio': self.params.time_stretch_ratio,
            'window_size': self.params.window_size,
            'hop_size': self.params.hop_size,
            'window_type': self.params.window_type.value,
            'quality_mode': self.params.quality_mode,
            'pitch_modulation_rate': self.params.pitch_modulation_rate,
            'pitch_modulation_depth': self.params.pitch_modulation_depth,
            'dry_level': self.params.dry_level,
            'wet_level': self.params.wet_level,
            'sample_rate': self.sample_rate,
            'processed_samples': self.processed_samples,
            'lfo_phase': self.lfo_phase
        }
    
    def reset(self):
        """Reset processor state"""
        # Reset phase vocoder
        self.phase_vocoder.phase_accumulator.fill(0)
        self.phase_vocoder.previous_phase.fill(0)
        self.phase_vocoder.input_buffer.fill(0)
        self.phase_vocoder.output_buffer.fill(0)
        
        # Reset LFO
        self.lfo_phase = 0.0
        
        # Clear buffers
        self.input_buffer.fill(0)
        self.output_buffer.fill(0)
        
        # Reset counters
        self.processed_samples = 0
        
        self.logger.info("Pitch shifter processor reset")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'processing_lock'):
            with self.processing_lock:
                pass  # Ensure any ongoing processing completes
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Processing parameters
        self.pitch_shift_cents = 0  # -1200 to +1200 cents
        self.formant_preserve = True
        self.time_stretch_compensation = True
        self.algorithm = PitchShiftAlgorithm.PHASE_VOCODER
        
        # Frame processing parameters
        self.frame_size = 2048
        self.hop_size = self.frame_size // 4
        self.overlap_factor = 4
        
        # Initialize processing buffers
        self._init_buffers()
        
        # PSOLA parameters
        self.pitch_marks = []
        self.target_pitch_marks = []
        
        self.logger.info("PitchShifterProcessor initialized")
    
    def _init_buffers(self):
        """Initialize processing buffers"""
        self.input_buffer = np.zeros(self.frame_size * 2)
        self.output_buffer = np.zeros(self.frame_size * 2)
        
        # Phase vocoder state
        self.prev_phase = np.zeros(self.frame_size // 2 + 1)
        self.phase_accumulator = np.zeros(self.frame_size // 2 + 1)
        
        # Window function
        self.window = np.hanning(self.frame_size)
        
        # Granular synthesis parameters
        self.grain_size = 1024
        self.grain_overlap = 0.75
        self.grain_window = np.hanning(self.grain_size)
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply pitch shifting processing"""
        try:
            if self.pitch_shift_cents == 0:
                return audio_data  # No processing needed
            
            if self.algorithm == PitchShiftAlgorithm.PHASE_VOCODER:
                return self._phase_vocoder_shift(audio_data)
            elif self.algorithm == PitchShiftAlgorithm.PSOLA:
                return self._psola_shift(audio_data)
            elif self.algorithm == PitchShiftAlgorithm.GRANULAR:
                return self._granular_shift(audio_data)
            elif self.algorithm == PitchShiftAlgorithm.SPECTRAL:
                return self._spectral_shift(audio_data)
            else:
                return self._phase_vocoder_shift(audio_data)
            
        except Exception as e:
            self.logger.error(f"Pitch shifting failed: {e}")
            return audio_data
    
    def _phase_vocoder_shift(self, audio_data: np.ndarray) -> np.ndarray:
        """Phase vocoder based pitch shifting"""
        pitch_factor = 2**(self.pitch_shift_cents / 1200.0)
        
        # Calculate time stretch factor for pitch compensation
        if self.time_stretch_compensation:
            time_stretch_factor = 1.0 / pitch_factor
        else:
            time_stretch_factor = 1.0
        
        # Phase vocoder processing
        num_frames = (len(audio_data) - self.frame_size) // self.hop_size + 1
        output_length = int(len(audio_data) * time_stretch_factor)
        processed_audio = np.zeros(output_length)
        
        output_hop = int(self.hop_size * time_stretch_factor)
        
        for frame_idx in range(num_frames):
            start_idx = frame_idx * self.hop_size
            end_idx = start_idx + self.frame_size
            
            if end_idx > len(audio_data):
                break
            
            # Extract and window frame
            frame = audio_data[start_idx:end_idx]
            windowed_frame = frame * self.window
            
            # Forward FFT
            spectrum = scipy.fft.rfft(windowed_frame)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)
            
            # Phase vocoder processing
            if frame_idx > 0:
                phase_diff = phase - self.prev_phase
                
                # Unwrap phase differences
                phase_diff = np.angle(np.exp(1j * phase_diff))
                
                # Expected phase advance
                expected_phase = (2 * np.pi * self.hop_size * 
                                np.arange(len(phase)) / self.frame_size)
                
                # True frequency (deviation from expected)
                true_freq = expected_phase + phase_diff
                
                # Scale frequency for pitch shifting
                shifted_freq = true_freq * pitch_factor
                
                # Update phase accumulator
                self.phase_accumulator += shifted_freq * output_hop / self.hop_size
            
            self.prev_phase = phase.copy()
            
            # Reconstruct spectrum with shifted frequency
            if frame_idx > 0:
                shifted_spectrum = magnitude * np.exp(1j * self.phase_accumulator)
            else:
                shifted_spectrum = spectrum
                self.phase_accumulator = phase.copy()
            
            # Formant preservation (optional)
            if self.formant_preserve:
                shifted_spectrum = self._preserve_formants(
                    shifted_spectrum, magnitude, pitch_factor
                )
            
            # Inverse FFT
            processed_frame = scipy.fft.irfft(shifted_spectrum)
            processed_frame *= self.window
            
            # Overlap-add to output
            output_start = frame_idx * output_hop
            output_end = output_start + self.frame_size
            
            if output_end <= len(processed_audio):
                processed_audio[output_start:output_end] += processed_frame
            elif output_start < len(processed_audio):
                remaining = len(processed_audio) - output_start
                processed_audio[output_start:] += processed_frame[:remaining]
        
        return processed_audio
    
    def _preserve_formants(self, shifted_spectrum: np.ndarray, 
                          original_magnitude: np.ndarray,
                          pitch_factor: float) -> np.ndarray:
        """Preserve formant structure during pitch shifting"""
        # Simple formant preservation by spectral envelope warping
        freqs = np.fft.rfftfreq(self.frame_size, 1/self.sample_rate)
        
        # Calculate original spectral envelope (formants)
        envelope = self._calculate_spectral_envelope(original_magnitude, freqs)
        
        # Warp envelope for new pitch
        warped_envelope = self._warp_spectral_envelope(envelope, freqs, pitch_factor)
        
        # Apply warped envelope to shifted spectrum
        magnitude_shifted = np.abs(shifted_spectrum)
        phase_shifted = np.angle(shifted_spectrum)
        
        # Blend original formant structure
        formant_factor = 0.7  # Strength of formant preservation
        final_magnitude = (magnitude_shifted * (1 - formant_factor) + 
                          warped_envelope * formant_factor)
        
        return final_magnitude * np.exp(1j * phase_shifted)
    
    def _calculate_spectral_envelope(self, magnitude: np.ndarray, 
                                   freqs: np.ndarray) -> np.ndarray:
        """Calculate spectral envelope (formant structure)"""
        # Use cepstral analysis for envelope extraction
        log_magnitude = np.log(magnitude + 1e-10)
        
        # Cepstral analysis
        cepstrum = scipy.fft.rfft(log_magnitude)
        
        # Lifter to extract envelope (remove fine harmonic structure)
        lifter_cutoff = 50  # Keep low quefrency components
        cepstrum[lifter_cutoff:] = 0
        
        # Back to frequency domain
        envelope = np.exp(scipy.fft.irfft(cepstrum, len(magnitude)))
        
        return envelope
    
    def _warp_spectral_envelope(self, envelope: np.ndarray, 
                               freqs: np.ndarray, pitch_factor: float) -> np.ndarray:
        """Warp spectral envelope for formant preservation"""
        # Scale frequency axis by inverse of pitch factor to preserve formants
        formant_factor = 1.0 / pitch_factor
        warped_freqs = freqs * formant_factor
        
        # Interpolate envelope at warped frequencies
        warped_envelope = np.interp(freqs, warped_freqs, envelope)
        
        return warped_envelope
    
    def _psola_shift(self, audio_data: np.ndarray) -> np.ndarray:
        """PSOLA (Pitch Synchronous Overlap-Add) pitch shifting"""
        # Simplified PSOLA implementation
        # This would typically require pitch tracking first
        
        pitch_factor = 2**(self.pitch_shift_cents / 1200.0)
        
        # Estimate pitch period (simplified)
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find pitch period
        min_period = int(0.002 * self.sample_rate)  # 2ms minimum
        max_period = int(0.02 * self.sample_rate)   # 20ms maximum
        
        if len(autocorr) > max_period:
            pitch_period = np.argmax(autocorr[min_period:max_period]) + min_period
        else:
            pitch_period = min_period
        
        # PSOLA processing
        output_period = int(pitch_period / pitch_factor)
        processed_audio = []
        
        i = 0
        while i + pitch_period < len(audio_data):
            # Extract pitch period
            grain = audio_data[i:i + pitch_period]
            
            # Apply window
            windowed_grain = grain * np.hanning(len(grain))
            
            # Resample grain for pitch shifting
            if pitch_factor != 1.0:
                # Simple resampling (would use better interpolation in practice)
                new_length = int(len(grain) / pitch_factor)
                if new_length > 0:
                    resampled_grain = np.interp(
                        np.linspace(0, len(grain)-1, new_length),
                        np.arange(len(grain)),
                        windowed_grain
                    )
                else:
                    resampled_grain = windowed_grain
            else:
                resampled_grain = windowed_grain
            
            processed_audio.extend(resampled_grain)
            i += output_period
        
        return np.array(processed_audio)
    
    def _granular_shift(self, audio_data: np.ndarray) -> np.ndarray:
        """Granular synthesis based pitch shifting"""
        pitch_factor = 2**(self.pitch_shift_cents / 1200.0)
        
        grain_hop = int(self.grain_size * (1 - self.grain_overlap))
        output_hop = int(grain_hop * pitch_factor)
        
        processed_audio = []
        
        i = 0
        while i + self.grain_size < len(audio_data):
            # Extract grain
            grain = audio_data[i:i + self.grain_size]
            windowed_grain = grain * self.grain_window
            
            # Pitch shift grain by resampling
            if pitch_factor != 1.0:
                # Time-domain resampling
                new_length = int(self.grain_size / pitch_factor)
                if new_length > 0:
                    shifted_grain = np.interp(
                        np.linspace(0, self.grain_size-1, new_length),
                        np.arange(self.grain_size),
                        windowed_grain
                    )
                else:
                    shifted_grain = windowed_grain
            else:
                shifted_grain = windowed_grain
            
            # Add to output with appropriate spacing
            if len(processed_audio) < len(shifted_grain):
                processed_audio.extend([0] * (len(shifted_grain) - len(processed_audio)))
            
            # Overlap-add
            start_pos = min(len(processed_audio) - len(shifted_grain), 0)
            if start_pos >= 0:
                for j, sample in enumerate(shifted_grain):
                    if start_pos + j < len(processed_audio):
                        processed_audio[start_pos + j] += sample
                    else:
                        processed_audio.append(sample)
            
            i += grain_hop
        
        return np.array(processed_audio)
    
    def _spectral_shift(self, audio_data: np.ndarray) -> np.ndarray:
        """Spectral domain pitch shifting"""
        pitch_factor = 2**(self.pitch_shift_cents / 1200.0)
        
        # Process entire signal in frequency domain
        spectrum = scipy.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1/self.sample_rate)
        
        # Shift spectrum
        shifted_freqs = freqs * pitch_factor
        
        # Interpolate spectrum to new frequency grid
        shifted_spectrum = np.interp(freqs, shifted_freqs, np.abs(spectrum))
        phase_spectrum = np.interp(freqs, shifted_freqs, np.angle(spectrum))
        
        # Reconstruct complex spectrum
        new_spectrum = shifted_spectrum * np.exp(1j * phase_spectrum)
        
        # Convert back to time domain
        processed_audio = scipy.fft.irfft(new_spectrum)
        
        return processed_audio
    
    def set_pitch_shift(self, cents: float):
        """Set pitch shift in cents (-1200 to +1200)"""
        self.pitch_shift_cents = np.clip(cents, -1200, 1200)
        self.logger.debug(f"Pitch shift set to {cents} cents")
    
    def set_parameters(self, formant_preserve: bool = None,
                      time_stretch_compensation: bool = None,
                      algorithm: PitchShiftAlgorithm = None):
        """Set pitch shifter parameters"""
        if formant_preserve is not None:
            self.formant_preserve = formant_preserve
        if time_stretch_compensation is not None:
            self.time_stretch_compensation = time_stretch_compensation
        if algorithm is not None:
            self.algorithm = algorithm
        
        self.logger.debug(f"Pitch shifter parameters updated")
    
    def get_current_settings(self) -> dict:
        """Get current pitch shifter settings"""
        return {
            "pitch_shift_cents": self.pitch_shift_cents,
            "pitch_shift_semitones": self.pitch_shift_cents / 100,
            "pitch_factor": 2**(self.pitch_shift_cents / 1200.0),
            "formant_preserve": self.formant_preserve,
            "time_stretch_compensation": self.time_stretch_compensation,
            "algorithm": self.algorithm.value
        }
