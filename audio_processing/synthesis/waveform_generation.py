"""
 Waveform Generation Engine - Advanced DSP and Signal Synthesis

This module provides comprehensive waveform generation capabilities including
oscillators, synthesis algorithms, and advanced DSP techniques.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 LEGAL WARNING: Unauthorized use prohibited. Contact mlaiel@live.de for licensing.
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging
from abc import ABC, abstractmethod
from enum import Enum
import scipy.signal
import librosa
from scipy.signal import butter, filtfilt, hilbert
from scipy.interpolate import interp1d
import numba

logger = logging.getLogger(__name__)


class WaveformType(Enum):
    """Waveform types for oscillator generation."""
    SINE = "sine"
    COSINE = "cosine"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"
    TRIANGLE = "triangle"
    PULSE = "pulse"
    NOISE = "noise"
    CUSTOM = "custom"


class FilterType(Enum):
    """Filter types for synthesis."""
    LOWPASS = "lowpass"
    HIGHPASS = "highpass"
    BANDPASS = "bandpass"
    BANDSTOP = "bandstop"
    ALLPASS = "allpass"


@dataclass
class OscillatorConfig:
    """Configuration for oscillator generation."""
    sample_rate: int = 44100
    frequency: float = 440.0
    amplitude: float = 1.0
    phase: float = 0.0
    waveform: WaveformType = WaveformType.SINE
    
    # Pulse wave specific
    duty_cycle: float = 0.5
    
    # Noise specific
    noise_type: str = "white"  # white, pink, brown
    
    # Modulation
    fm_frequency: float = 0.0
    fm_depth: float = 0.0
    am_frequency: float = 0.0
    am_depth: float = 0.0
    
    # Anti-aliasing
    use_antialiasing: bool = True
    oversampling_factor: int = 4


@dataclass
class FilterConfig:
    """Configuration for filtering operations."""
    filter_type: FilterType = FilterType.LOWPASS
    cutoff_frequency: float = 1000.0
    resonance: float = 0.7
    order: int = 4
    
    # Bandpass/Bandstop specific
    high_frequency: Optional[float] = None
    
    # State variable filter
    use_nonlinear: bool = False
    drive: float = 1.0


class BaseOscillator(ABC):
    """Abstract base class for oscillators."""
    
    def __init__(self, config: OscillatorConfig):
        self.config = config
        self.phase_accumulator = config.phase
        self.sample_rate = config.sample_rate
        
    @abstractmethod
    def generate(self, num_samples: int) -> np.ndarray:
        """Generate waveform samples."""
        pass
        
    def set_frequency(self, frequency: float) -> None:
        """Set oscillator frequency."""
        self.config.frequency = frequency
        
    def set_amplitude(self, amplitude: float) -> None:
        """Set oscillator amplitude."""
        self.config.amplitude = amplitude
        
    def reset_phase(self, phase: float = 0.0) -> None:
        """Reset phase accumulator."""
        self.phase_accumulator = phase


class SineOscillator(BaseOscillator):
    """Sine wave oscillator with high precision."""
    
    def __init__(self, config: OscillatorConfig):
        super().__init__(config)
        
    def generate(self, num_samples: int) -> np.ndarray:
        """Generate sine wave samples."""
        # Calculate phase increment
        phase_increment = 2 * np.pi * self.config.frequency / self.sample_rate
        
        # Generate phase array
        phases = self.phase_accumulator + np.arange(num_samples) * phase_increment
        
        # Generate sine wave
        waveform = self.config.amplitude * np.sin(phases)
        
        # Apply modulation if specified
        if self.config.fm_frequency > 0:
            fm_phases = np.arange(num_samples) * 2 * np.pi * self.config.fm_frequency / self.sample_rate
            fm_modulation = self.config.fm_depth * np.sin(fm_phases)
            waveform = self.config.amplitude * np.sin(phases + fm_modulation)
            
        if self.config.am_frequency > 0:
            am_phases = np.arange(num_samples) * 2 * np.pi * self.config.am_frequency / self.sample_rate
            am_modulation = 1 + self.config.am_depth * np.sin(am_phases)
            waveform *= am_modulation
            
        # Update phase accumulator
        self.phase_accumulator = phases[-1] + phase_increment
        self.phase_accumulator %= 2 * np.pi
        
        return waveform.astype(np.float32)


class SquareOscillator(BaseOscillator):
    """Square wave oscillator with anti-aliasing."""
    
    def __init__(self, config: OscillatorConfig):
        super().__init__(config)
        self.blep_table = self._generate_blep_table() if config.use_antialiasing else None
        
    def _generate_blep_table(self, table_size: int = 4096) -> np.ndarray:
        """Generate Band-Limited Step (BLEP) table for anti-aliasing."""
        # Generate sinc function for band limiting
        x = np.linspace(-4, 4, table_size)
        sinc = np.sinc(x)
        
        # Integrate to get step response
        blep = np.cumsum(sinc)
        blep = blep / blep[-1]  # Normalize
        
        return blep.astype(np.float32)
        
    def generate(self, num_samples: int) -> np.ndarray:
        """Generate anti-aliased square wave."""
        phase_increment = self.config.frequency / self.sample_rate
        waveform = np.zeros(num_samples, dtype=np.float32)
        
        for i in range(num_samples):
            # Check for phase wrap and transitions
            prev_phase = self.phase_accumulator
            self.phase_accumulator += phase_increment
            
            if self.config.use_antialiasing and self.blep_table is not None:
                # Anti-aliased square wave using BLEP
                if prev_phase < self.config.duty_cycle <= self.phase_accumulator:
                    # Rising edge
                    waveform[i:] += self._apply_blep(i, num_samples, 2.0)
                elif prev_phase < 1.0 <= self.phase_accumulator:
                    # Falling edge
                    waveform[i:] += self._apply_blep(i, num_samples, -2.0)
                    
            # Basic square wave value
            if (self.phase_accumulator % 1.0) < self.config.duty_cycle:
                waveform[i] += self.config.amplitude
            else:
                waveform[i] -= self.config.amplitude
                
            # Handle phase wrap
            if self.phase_accumulator >= 1.0:
                self.phase_accumulator -= 1.0
                
        return waveform
        
    def _apply_blep(self, start_index: int, num_samples: int, amplitude: float) -> np.ndarray:
        """Apply BLEP correction."""
        blep_samples = min(len(self.blep_table), num_samples - start_index)
        correction = np.zeros(num_samples - start_index, dtype=np.float32)
        correction[:blep_samples] = amplitude * self.blep_table[:blep_samples]
        return correction


class SawtoothOscillator(BaseOscillator):
    """Sawtooth wave oscillator with anti-aliasing."""
    
    def __init__(self, config: OscillatorConfig):
        super().__init__(config)
        self.polyblep_enabled = config.use_antialiasing
        
    def generate(self, num_samples: int) -> np.ndarray:
        """Generate anti-aliased sawtooth wave."""
        phase_increment = self.config.frequency / self.sample_rate
        waveform = np.zeros(num_samples, dtype=np.float32)
        
        for i in range(num_samples):
            if self.polyblep_enabled:
                # PolyBLEP anti-aliased sawtooth
                waveform[i] = self._polyblep_sawtooth(phase_increment)
            else:
                # Naive sawtooth
                waveform[i] = self.config.amplitude * (2.0 * self.phase_accumulator - 1.0)
                
            self.phase_accumulator += phase_increment
            if self.phase_accumulator >= 1.0:
                self.phase_accumulator -= 1.0
                
        return waveform
        
    def _polyblep_sawtooth(self, phase_increment: float) -> float:
        """Generate PolyBLEP sawtooth sample."""
        value = 2.0 * self.phase_accumulator - 1.0
        
        # Apply PolyBLEP at discontinuity
        if self.phase_accumulator < phase_increment:
            t = self.phase_accumulator / phase_increment
            value -= self._polyblep(t)
            
        return self.config.amplitude * value
        
    def _polyblep(self, t: float) -> float:
        """PolyBLEP function for anti-aliasing."""
        if t < 1.0:
            return t + t - t * t - 1.0
        elif t < 2.0:
            t -= 1.0
            return t * t - t - t + 1.0
        else:
            return 0.0


class TriangleOscillator(BaseOscillator):
    """Triangle wave oscillator."""
    
    def __init__(self, config: OscillatorConfig):
        super().__init__(config)
        
    def generate(self, num_samples: int) -> np.ndarray:
        """Generate triangle wave."""
        phase_increment = self.config.frequency / self.sample_rate
        waveform = np.zeros(num_samples, dtype=np.float32)
        
        for i in range(num_samples):
            # Triangle wave from phase
            if self.phase_accumulator < 0.5:
                value = 4.0 * self.phase_accumulator - 1.0
            else:
                value = -4.0 * self.phase_accumulator + 3.0
                
            waveform[i] = self.config.amplitude * value
            
            self.phase_accumulator += phase_increment
            if self.phase_accumulator >= 1.0:
                self.phase_accumulator -= 1.0
                
        return waveform


class NoiseOscillator(BaseOscillator):
    """Noise generator with different color profiles."""
    
    def __init__(self, config: OscillatorConfig):
        super().__init__(config)
        self.noise_state = np.random.RandomState(42)  # Reproducible noise
        
    def generate(self, num_samples: int) -> np.ndarray:
        """Generate colored noise."""
        if self.config.noise_type == "white":
            return self._generate_white_noise(num_samples)
        elif self.config.noise_type == "pink":
            return self._generate_pink_noise(num_samples)
        elif self.config.noise_type == "brown":
            return self._generate_brown_noise(num_samples)
        else:
            return self._generate_white_noise(num_samples)
            
    def _generate_white_noise(self, num_samples: int) -> np.ndarray:
        """Generate white noise."""



        return self.config.amplitude * self.noise_state.randn(num_samples).astype(np.float32)
        
    def _generate_pink_noise(self, num_samples: int) -> np.ndarray:
        """Generate pink noise (1/f noise)."""
        # Simple pink noise approximation using filtering
        white = self.noise_state.randn(num_samples)
        
        # Apply 1/f shaping filter
        b, a = scipy.signal.butter(1, 0.5, 'low')
        pink = scipy.signal.filtfilt(b, a, white)
        
        return self.config.amplitude * pink.astype(np.float32)
        
    def _generate_brown_noise(self, num_samples: int) -> np.ndarray:
        """Generate brown noise (1/f² noise)."""
        # Brown noise as integrated white noise
        white = self.noise_state.randn(num_samples)
        brown = np.cumsum(white)
        
        # Normalize to prevent drift
        brown = brown - np.mean(brown)
        brown = brown / np.std(brown)
        
        return self.config.amplitude * brown.astype(np.float32)


class OscillatorEngine:
    """Multi-oscillator engine with mixing capabilities."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.oscillators: Dict[str, BaseOscillator] = {}
        self.mixing_levels: Dict[str, float] = {}
        
    def add_oscillator(self, name: str, oscillator: BaseOscillator, level: float = 1.0) -> None:
        """Add oscillator to engine."""
        self.oscillators[name] = oscillator
        self.mixing_levels[name] = level
        logger.info(f"Added oscillator: {name}")
        
    def remove_oscillator(self, name: str) -> None:
        """Remove oscillator from engine."""
        if name in self.oscillators:
            del self.oscillators[name]
            del self.mixing_levels[name]
            logger.info(f"Removed oscillator: {name}")
            
    def set_mixing_level(self, name: str, level: float) -> None:
        """Set mixing level for oscillator."""
        if name in self.mixing_levels:
            self.mixing_levels[name] = level
            
    def generate_mixed(self, num_samples: int) -> np.ndarray:
        """Generate mixed output from all oscillators."""
        if not self.oscillators:
            return np.zeros(num_samples, dtype=np.float32)
            
        # Generate from all oscillators
        mixed_output = np.zeros(num_samples, dtype=np.float32)
        
        for name, oscillator in self.oscillators.items():
            output = oscillator.generate(num_samples)
            mixed_output += output * self.mixing_levels[name]
            
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(mixed_output))
        if max_amplitude > 1.0:
            mixed_output /= max_amplitude
            
        return mixed_output


class WavetableSynthesizer:
    """Wavetable synthesis engine with interpolation."""
    
    def __init__(self, sample_rate: int = 44100, table_size: int = 2048):
        self.sample_rate = sample_rate
        self.table_size = table_size
        self.wavetables: Dict[str, np.ndarray] = {}
        self.phase_accumulator = 0.0
        
        # Generate default wavetables
        self._generate_default_tables()
        
    def _generate_default_tables(self) -> None:
        """Generate default wavetable collection."""
        # Basic waveforms
        x = np.linspace(0, 2 * np.pi, self.table_size, endpoint=False)
        
        self.wavetables['sine'] = np.sin(x)
        self.wavetables['square'] = np.sign(np.sin(x))
        self.wavetables['sawtooth'] = 2 * (x / (2 * np.pi)) - 1
        self.wavetables['triangle'] = 2 * np.abs(2 * (x / (2 * np.pi)) - 1) - 1
        
        # Harmonic series
        for n in range(2, 9):
            harmonic_name = f"harmonic_{n}"
            harmonic_wave = np.zeros(self.table_size)
            for h in range(1, n + 1):
                harmonic_wave += np.sin(h * x) / h
            self.wavetables[harmonic_name] = harmonic_wave / np.max(np.abs(harmonic_wave))
            
        logger.info(f"Generated {len(self.wavetables)} default wavetables")
        
    def add_wavetable(self, name: str, waveform: np.ndarray) -> None:
        """Add custom wavetable."""
        # Resample to table size if necessary
        if len(waveform) != self.table_size:
            x_old = np.linspace(0, 1, len(waveform))
            x_new = np.linspace(0, 1, self.table_size)
            interpolator = interp1d(x_old, waveform, kind='cubic')
            waveform = interpolator(x_new)
            
        # Normalize
        waveform = waveform / np.max(np.abs(waveform))
        self.wavetables[name] = waveform.astype(np.float32)
        
        logger.info(f"Added wavetable: {name}")
        
    def synthesize(self, frequency: float, num_samples: int, 
                  wavetable: str = 'sine') -> np.ndarray:
        """Synthesize audio using wavetable."""
        if wavetable not in self.wavetables:
            logger.warning(f"Wavetable {wavetable} not found, using sine")
            wavetable = 'sine'
            
        table = self.wavetables[wavetable]
        phase_increment = frequency * self.table_size / self.sample_rate
        
        output = np.zeros(num_samples, dtype=np.float32)
        
        for i in range(num_samples):
            # Linear interpolation in wavetable
            index = self.phase_accumulator
            int_index = int(index) % self.table_size
            frac = index - int_index
            
            # Interpolate between adjacent samples
            sample1 = table[int_index]
            sample2 = table[(int_index + 1) % self.table_size]
            output[i] = sample1 + frac * (sample2 - sample1)
            
            # Update phase
            self.phase_accumulator += phase_increment
            if self.phase_accumulator >= self.table_size:
                self.phase_accumulator -= self.table_size
                
        return output
        
    def morphing_synthesis(self, frequency: float, num_samples: int,
                          wavetable1: str, wavetable2: str, 
                          morph_amount: float) -> np.ndarray:
        """Synthesize with morphing between two wavetables."""
        if wavetable1 not in self.wavetables or wavetable2 not in self.wavetables:
            return self.synthesize(frequency, num_samples)
            
        table1 = self.wavetables[wavetable1]
        table2 = self.wavetables[wavetable2]
        
        # Morph wavetables
        morphed_table = (1 - morph_amount) * table1 + morph_amount * table2
        
        # Temporarily add morphed table
        temp_name = f"_morph_{int(morph_amount * 1000)}"
        self.wavetables[temp_name] = morphed_table
        
        # Synthesize
        result = self.synthesize(frequency, num_samples, temp_name)
        
        # Clean up
        del self.wavetables[temp_name]
        
        return result


class GranularSynthesis:
    """Granular synthesis engine for texture generation."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.grain_size = 1024
        self.overlap_factor = 0.5
        self.grain_density = 20.0  # grains per second
        
    def synthesize_texture(self, source_audio: np.ndarray, duration: float,
                          pitch_shift: float = 1.0, time_stretch: float = 1.0,
                          grain_size_var: float = 0.1) -> np.ndarray:
        """Generate granular synthesis texture."""
        num_output_samples = int(duration * self.sample_rate)
        output = np.zeros(num_output_samples, dtype=np.float32)
        
        # Calculate grain parameters
        grains_per_sample = self.grain_density / self.sample_rate
        grain_spacing = int(self.sample_rate / self.grain_density)
        
        # Generate grains
        current_pos = 0
        source_pos = 0.0
        
        while current_pos < num_output_samples:
            # Variable grain size
            current_grain_size = int(self.grain_size * (1 + grain_size_var * (np.random.random() - 0.5)))
            
            # Extract grain from source
            grain = self._extract_grain(source_audio, source_pos, current_grain_size)
            
            # Apply pitch shifting
            if pitch_shift != 1.0:
                grain = self._pitch_shift_grain(grain, pitch_shift)
                
            # Apply window
            window = self._grain_window(len(grain))
            grain = grain * window
            
            # Add to output
            end_pos = min(current_pos + len(grain), num_output_samples)
            actual_length = end_pos - current_pos
            output[current_pos:end_pos] += grain[:actual_length]
            
            # Update positions
            current_pos += grain_spacing
            source_pos += len(grain) * time_stretch / self.sample_rate
            
            # Wrap source position
            if source_pos >= len(source_audio) / self.sample_rate:
                source_pos = 0.0
                
        return output
        
    def _extract_grain(self, source: np.ndarray, position: float, size: int) -> np.ndarray:
        """Extract grain from source audio."""
        start_sample = int(position * self.sample_rate)
        end_sample = min(start_sample + size, len(source))
        
        if start_sample >= len(source):
            return np.zeros(size, dtype=np.float32)
            
        grain = source[start_sample:end_sample].copy()
        
        # Pad if necessary
        if len(grain) < size:
            padding = np.zeros(size - len(grain), dtype=np.float32)
            grain = np.concatenate([grain, padding])
            
        return grain
        
    def _pitch_shift_grain(self, grain: np.ndarray, shift: float) -> np.ndarray:
        """Apply pitch shifting to grain."""
        if shift == 1.0:
            return grain
            
        # Simple pitch shifting using resampling
        # For better quality, would use phase vocoder or similar
        new_length = int(len(grain) / shift)
        if new_length > 0:
            indices = np.linspace(0, len(grain) - 1, new_length)
            shifted = np.interp(indices, np.arange(len(grain)), grain)
            return shifted.astype(np.float32)
        else:
            return grain
            
    def _grain_window(self, size: int) -> np.ndarray:
        """Generate grain window function."""
        # Hanning window
        return np.hanning(size).astype(np.float32)


class FM_Synthesizer:
    """Frequency Modulation synthesis engine."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # FM parameters
        self.carrier_freq = 440.0
        self.modulator_freq = 200.0
        self.modulation_index = 2.0
        self.amplitude = 1.0
        
        # Phase accumulators
        self.carrier_phase = 0.0
        self.modulator_phase = 0.0
        
    def set_parameters(self, carrier_freq: float, modulator_freq: float,
                      modulation_index: float, amplitude: float = 1.0) -> None:
        """Set FM synthesis parameters."""
        self.carrier_freq = carrier_freq
        self.modulator_freq = modulator_freq
        self.modulation_index = modulation_index
        self.amplitude = amplitude
        
    def synthesize(self, num_samples: int) -> np.ndarray:
        """Generate FM synthesis audio."""
        output = np.zeros(num_samples, dtype=np.float32)
        
        # Phase increments
        carrier_increment = 2 * np.pi * self.carrier_freq / self.sample_rate
        modulator_increment = 2 * np.pi * self.modulator_freq / self.sample_rate
        
        for i in range(num_samples):
            # Modulator signal
            modulator_signal = np.sin(self.modulator_phase)
            
            # FM synthesis
            carrier_instantaneous_freq = self.carrier_freq + self.modulation_index * modulator_signal
            carrier_phase_increment = 2 * np.pi * carrier_instantaneous_freq / self.sample_rate
            
            # Carrier signal
            output[i] = self.amplitude * np.sin(self.carrier_phase)
            
            # Update phases
            self.carrier_phase += carrier_phase_increment
            self.modulator_phase += modulator_increment
            
            # Wrap phases
            if self.carrier_phase >= 2 * np.pi:
                self.carrier_phase -= 2 * np.pi
            if self.modulator_phase >= 2 * np.pi:
                self.modulator_phase -= 2 * np.pi
                
        return output


class AM_Synthesizer:
    """Amplitude Modulation synthesis engine."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # AM parameters
        self.carrier_freq = 440.0
        self.modulator_freq = 10.0
        self.modulation_depth = 0.5
        self.amplitude = 1.0
        
        # Phase accumulators
        self.carrier_phase = 0.0
        self.modulator_phase = 0.0
        
    def set_parameters(self, carrier_freq: float, modulator_freq: float,
                      modulation_depth: float, amplitude: float = 1.0) -> None:
        """Set AM synthesis parameters."""
        self.carrier_freq = carrier_freq
        self.modulator_freq = modulator_freq
        self.modulation_depth = modulation_depth
        self.amplitude = amplitude
        
    def synthesize(self, num_samples: int) -> np.ndarray:
        """Generate AM synthesis audio."""
        # Phase increments
        carrier_increment = 2 * np.pi * self.carrier_freq / self.sample_rate
        modulator_increment = 2 * np.pi * self.modulator_freq / self.sample_rate
        
        # Generate phase arrays
        carrier_phases = self.carrier_phase + np.arange(num_samples) * carrier_increment
        modulator_phases = self.modulator_phase + np.arange(num_samples) * modulator_increment
        
        # Generate signals
        carrier_signal = np.sin(carrier_phases)
        modulator_signal = np.sin(modulator_phases)
        
        # AM synthesis
        output = self.amplitude * carrier_signal * (1 + self.modulation_depth * modulator_signal)
        
        # Update phases
        self.carrier_phase = carrier_phases[-1] + carrier_increment
        self.modulator_phase = modulator_phases[-1] + modulator_increment
        
        # Wrap phases
        self.carrier_phase %= 2 * np.pi
        self.modulator_phase %= 2 * np.pi
        
        return output.astype(np.float32)


class SubtractiveSynthesis:
    """Subtractive synthesis engine with filters and envelopes."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # Oscillator
        self.oscillator = SineOscillator(OscillatorConfig(sample_rate=sample_rate))
        
        # Filter
        self.filter = StateVariableFilter(FilterConfig())
        
        # Envelope
        self.envelope = ADSREnvelope(sample_rate)
        
    def synthesize_note(self, frequency: float, duration: float,
                       velocity: float = 1.0) -> np.ndarray:
        """Synthesize note using subtractive synthesis."""
        num_samples = int(duration * self.sample_rate)
        
        # Set oscillator frequency
        self.oscillator.set_frequency(frequency)
        self.oscillator.set_amplitude(velocity)
        
        # Generate oscillator signal
        raw_signal = self.oscillator.generate(num_samples)
        
        # Apply filter
        filtered_signal = self.filter.process(raw_signal)
        
        # Apply envelope
        envelope_signal = self.envelope.generate(duration)
        synthesized = filtered_signal * envelope_signal
        
        return synthesized


class AdditiveSynthesis:
    """Additive synthesis engine with harmonic control."""
    
    def __init__(self, sample_rate: int = 44100, num_harmonics: int = 16):
        self.sample_rate = sample_rate
        self.num_harmonics = num_harmonics
        
        # Harmonic oscillators
        self.harmonics = []
        for i in range(num_harmonics):
            config = OscillatorConfig(sample_rate=sample_rate)
            self.harmonics.append(SineOscillator(config))
            
        # Harmonic amplitudes
        self.harmonic_amplitudes = np.ones(num_harmonics) / num_harmonics
        
    def set_harmonic_series(self, fundamental: float, amplitudes: List[float]) -> None:
        """Set harmonic series parameters."""
        num_amps = min(len(amplitudes), self.num_harmonics)
        
        for i in range(num_amps):
            self.harmonics[i].set_frequency(fundamental * (i + 1))
            self.harmonic_amplitudes[i] = amplitudes[i]
            
        # Zero out remaining harmonics
        for i in range(num_amps, self.num_harmonics):
            self.harmonic_amplitudes[i] = 0.0
            
    def synthesize(self, num_samples: int) -> np.ndarray:
        """Generate additive synthesis audio."""
        output = np.zeros(num_samples, dtype=np.float32)
        
        for i, oscillator in enumerate(self.harmonics):
            if self.harmonic_amplitudes[i] > 0:
                oscillator.set_amplitude(self.harmonic_amplitudes[i])
                harmonic_signal = oscillator.generate(num_samples)
                output += harmonic_signal
                
        return output


class SpectralSynthesis:
    """Spectral synthesis using FFT manipulation."""
    
    def __init__(self, sample_rate: int = 44100, fft_size: int = 2048):
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.hop_size = fft_size // 4
        
        # Spectral bins
        self.freqs = np.fft.fftfreq(fft_size, 1/sample_rate)[:fft_size//2 + 1]
        
    def synthesize_spectrum(self, spectrum: np.ndarray, num_frames: int) -> np.ndarray:
        """Synthesize audio from spectral representation."""
        if len(spectrum) != len(self.freqs):
            raise ValueError("Spectrum size must match FFT bins")
            
        # Generate audio using overlap-add
        total_samples = (num_frames - 1) * self.hop_size + self.fft_size
        output = np.zeros(total_samples, dtype=np.float32)
        window = np.hanning(self.fft_size)
        
        for frame in range(num_frames):
            # Create complex spectrum (magnitude with random phase)
            phases = np.random.uniform(0, 2*np.pi, len(spectrum))
            complex_spectrum = spectrum * np.exp(1j * phases)
            
            # Mirror for real FFT
            complex_spectrum_full = np.concatenate([
                complex_spectrum[:-1],
                np.conj(complex_spectrum[-2:0:-1])
            ])
            
            # IFFT to time domain
            time_frame = np.real(np.fft.ifft(complex_spectrum_full))
            
            # Apply window and overlap-add
            windowed_frame = time_frame * window
            start_idx = frame * self.hop_size
            output[start_idx:start_idx + self.fft_size] += windowed_frame
            
        return output
        
    def spectral_filter(self, audio: np.ndarray, filter_func: Callable) -> np.ndarray:
        """Apply spectral filtering to audio."""
        # STFT
        hop_length = self.hop_size
        stft = librosa.stft(audio, n_fft=self.fft_size, hop_length=hop_length)
        
        # Apply filter function to magnitude spectrum
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        filtered_magnitude = filter_func(magnitude, self.freqs[:, np.newaxis])
        
        # Reconstruct
        filtered_stft = filtered_magnitude * np.exp(1j * phase)
        return librosa.istft(filtered_stft, hop_length=hop_length)


class StateVariableFilter:
    """State variable filter implementation."""
    
    def __init__(self, config: FilterConfig):
        self.config = config
        self.sample_rate = 44100  # Default, should be set
        
        # Filter state
        self.z1 = 0.0
        self.z2 = 0.0
        
        # Update coefficients
        self._update_coefficients()
        
    def _update_coefficients(self) -> None:
        """Update filter coefficients."""
        # Calculate filter coefficients
        f = 2 * np.sin(np.pi * self.config.cutoff_frequency / self.sample_rate)
        q = self.config.resonance
        
        self.f = f
        self.q = q
        
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio through state variable filter."""
        output = np.zeros_like(audio)
        
        for i, sample in enumerate(audio):
            # State variable filter equations
            low = self.z2 + self.f * self.z1
            high = sample - low - self.q * self.z1
            band = self.f * high + self.z1
            notch = high + low
            
            # Update state
            self.z1 = band
            self.z2 = low
            
            # Select output based on filter type
            if self.config.filter_type == FilterType.LOWPASS:
                output[i] = low
            elif self.config.filter_type == FilterType.HIGHPASS:
                output[i] = high
            elif self.config.filter_type == FilterType.BANDPASS:
                output[i] = band
            elif self.config.filter_type == FilterType.BANDSTOP:
                output[i] = notch
            else:
                output[i] = sample
                
        return output


class ADSREnvelope:
    """ADSR envelope generator."""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # ADSR parameters (in seconds)
        self.attack = 0.1
        self.decay = 0.2
        self.sustain = 0.7
        self.release = 0.5
        
    def set_parameters(self, attack: float, decay: float, 
                      sustain: float, release: float) -> None:
        """Set ADSR parameters."""
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        
    def generate(self, duration: float) -> np.ndarray:
        """Generate ADSR envelope."""
        num_samples = int(duration * self.sample_rate)
        envelope = np.zeros(num_samples, dtype=np.float32)
        
        # Calculate phase lengths
        attack_samples = int(self.attack * self.sample_rate)
        decay_samples = int(self.decay * self.sample_rate)
        release_samples = int(self.release * self.sample_rate)
        sustain_samples = max(0, num_samples - attack_samples - decay_samples - release_samples)
        
        idx = 0
        
        # Attack phase
        if attack_samples > 0 and idx < num_samples:
            end_idx = min(idx + attack_samples, num_samples)
            envelope[idx:end_idx] = np.linspace(0, 1, end_idx - idx)
            idx = end_idx
            
        # Decay phase
        if decay_samples > 0 and idx < num_samples:
            end_idx = min(idx + decay_samples, num_samples)
            envelope[idx:end_idx] = np.linspace(1, self.sustain, end_idx - idx)
            idx = end_idx
            
        # Sustain phase
        if sustain_samples > 0 and idx < num_samples:
            end_idx = min(idx + sustain_samples, num_samples)
            envelope[idx:end_idx] = self.sustain
            idx = end_idx
            
        # Release phase
        if release_samples > 0 and idx < num_samples:
            start_level = envelope[idx - 1] if idx > 0 else self.sustain
            envelope[idx:] = np.linspace(start_level, 0, num_samples - idx)
            
        return envelope


# Factory functions
def create_oscillator(waveform_type: WaveformType, config: OscillatorConfig = None) -> BaseOscillator:
    """Factory function to create oscillators."""
    if config is None:
        config = OscillatorConfig()
        
    oscillators = {
        WaveformType.SINE: SineOscillator,
        WaveformType.SQUARE: SquareOscillator,
        WaveformType.SAWTOOTH: SawtoothOscillator,
        WaveformType.TRIANGLE: TriangleOscillator,
        WaveformType.NOISE: NoiseOscillator
    }
    
    if waveform_type not in oscillators:
        logger.warning(f"Unknown waveform type: {waveform_type}, using sine")
        waveform_type = WaveformType.SINE
        
    return oscillators[waveform_type](config)
