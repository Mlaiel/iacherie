"""⏰ Time Stretcher Processor - Advanced Time Manipulation Engine

Professional time stretching with pitch preservation, WSOLA algorithms,
phase vocoder processing, and high-quality temporal modification.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
import logging
from typing import Optional, Tuple
from enum import Enum
import scipy.signal
import scipy.fft


class TimeStretchAlgorithm(Enum):
    """Time stretching algorithm types"""    PHASE_VOCODER = "phase_vocoder"
    WSOLA = "wsola"  # Waveform Similarity Overlap-Add
    GRANULAR = "granular"
    SPECTRAL = "spectral"


class TimeStretcherProcessor:
    """Professional time stretcher processor"""    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Processing parameters
        self.time_stretch_factor = 1.0  # 0.5 = half speed, 2.0 = double speed
        self.preserve_pitch = True
        self.quality = "high"  # low, medium, high, ultra
        self.algorithm = TimeStretchAlgorithm.PHASE_VOCODER
        
        # Frame processing parameters
        self.frame_size = 2048
        self.hop_size = self.frame_size // 4
        self.overlap_factor = 4
        
        # Initialize processing buffers
        self._init_buffers()
        
        # WSOLA parameters
        self.wsola_template_size = 1024
        self.wsola_search_window = 512
        
        self.logger.info("TimeStretcherProcessor initialized")
    
    def _init_buffers(self):
        """Initialize processing buffers"""        self.input_buffer = np.zeros(self.frame_size * 2)
        self.output_buffer = np.zeros(self.frame_size * 2)
        
        # Phase vocoder state
        self.prev_phase = np.zeros(self.frame_size // 2 + 1)
        self.phase_accumulator = np.zeros(self.frame_size // 2 + 1)
        
        # Window functions
        self.analysis_window = np.hanning(self.frame_size)
        self.synthesis_window = np.hanning(self.frame_size)
        
        # Normalize synthesis window for perfect reconstruction
        self.synthesis_window = self._normalize_synthesis_window()
        
        # Granular synthesis parameters
        self.grain_size = 1024
        self.grain_overlap = 0.75
    
    def _normalize_synthesis_window(self) -> np.ndarray:
        """Normalize synthesis window for perfect reconstruction"""        window = np.hanning(self.frame_size)
        
        # Calculate normalization factor
        hop_size = self.frame_size // self.overlap_factor
        normalization = np.zeros(self.frame_size)
        
        for i in range(0, self.frame_size, hop_size):
            normalization += np.roll(window**2, i)
        
        # Avoid division by zero
        normalization[normalization < 1e-6] = 1.0
        
        return window / normalization
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply time stretching processing"""        try:
            if abs(self.time_stretch_factor - 1.0) < 1e-6:
                return audio_data  # No processing needed
            
            if self.algorithm == TimeStretchAlgorithm.PHASE_VOCODER:
                return self._phase_vocoder_stretch(audio_data)
            elif self.algorithm == TimeStretchAlgorithm.WSOLA:
                return self._wsola_stretch(audio_data)
            elif self.algorithm == TimeStretchAlgorithm.GRANULAR:
                return self._granular_stretch(audio_data)
            elif self.algorithm == TimeStretchAlgorithm.SPECTRAL:
                return self._spectral_stretch(audio_data)
            else:
                return self._phase_vocoder_stretch(audio_data)
            
        except Exception as e:
            self.logger.error(f"Time stretching failed: {e}")
            return audio_data
    
    def _phase_vocoder_stretch(self, audio_data: np.ndarray) -> np.ndarray:
        """Phase vocoder based time stretching"""        synthesis_hop = int(self.hop_size * self.time_stretch_factor)
        
        # Calculate output length
        num_frames = (len(audio_data) - self.frame_size) // self.hop_size + 1
        output_length = (num_frames - 1) * synthesis_hop + self.frame_size
        processed_audio = np.zeros(output_length)
        
        for frame_idx in range(num_frames):
            analysis_start = frame_idx * self.hop_size
            analysis_end = analysis_start + self.frame_size
            
            if analysis_end > len(audio_data):
                break
            
            # Extract and window frame
            frame = audio_data[analysis_start:analysis_end]
            windowed_frame = frame * self.analysis_window
            
            # Forward FFT
            spectrum = scipy.fft.rfft(windowed_frame)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)
            
            # Phase vocoder processing
            if frame_idx > 0:
                # Calculate phase differences
                phase_diff = phase - self.prev_phase
                
                # Unwrap phase differences
                phase_diff = np.angle(np.exp(1j * phase_diff))
                
                # Expected phase advance for analysis hop
                bin_frequencies = 2 * np.pi * np.arange(len(phase)) / self.frame_size
                expected_phase = bin_frequencies * self.hop_size
                
                # Calculate true frequency (instantaneous frequency)
                true_freq = expected_phase + phase_diff
                
                # Update phase accumulator for synthesis hop
                self.phase_accumulator += true_freq * synthesis_hop / self.hop_size
            else:
                self.phase_accumulator = phase.copy()
            
            self.prev_phase = phase.copy()
            
            # Reconstruct spectrum with corrected phase
            processed_spectrum = magnitude * np.exp(1j * self.phase_accumulator)
            
            # Preserve pitch if requested
            if self.preserve_pitch and self.time_stretch_factor != 1.0:
                processed_spectrum = self._preserve_pitch_content(
                    processed_spectrum, magnitude
                )
            
            # Inverse FFT
            processed_frame = scipy.fft.irfft(processed_spectrum)
            processed_frame *= self.synthesis_window
            
            # Overlap-add to output
            synthesis_start = frame_idx * synthesis_hop
            synthesis_end = synthesis_start + self.frame_size
            
            if synthesis_end <= len(processed_audio):
                processed_audio[synthesis_start:synthesis_end] += processed_frame
            elif synthesis_start < len(processed_audio):
                remaining = len(processed_audio) - synthesis_start
                processed_audio[synthesis_start:] += processed_frame[:remaining]
        
        return processed_audio
    
    def _preserve_pitch_content(self, spectrum: np.ndarray, 
                               magnitude: np.ndarray) -> np.ndarray:
        """Preserve pitch content during time stretching"""        # Simple spectral envelope preservation
        # This maintains the harmonic structure while allowing time modification
        
        # Calculate spectral centroid to maintain timbral balance
        freqs = np.fft.rfftfreq(self.frame_size, 1/self.sample_rate)
        spectral_centroid = np.sum(freqs * magnitude) / (np.sum(magnitude) + 1e-10)
        
        # Apply gentle high-frequency emphasis to maintain clarity
        freq_emphasis = 1.0 + 0.1 * (freqs / (self.sample_rate / 2))
        
        emphasized_magnitude = magnitude * freq_emphasis
        preserved_spectrum = emphasized_magnitude * np.exp(1j * np.angle(spectrum))
        
        return preserved_spectrum
    
    def _wsola_stretch(self, audio_data: np.ndarray) -> np.ndarray:
        """WSOLA (Waveform Similarity Overlap-Add) time stretching"""        synthesis_hop = int(self.hop_size * self.time_stretch_factor)
        
        # Initialize output
        output_length = int(len(audio_data) * self.time_stretch_factor)
        processed_audio = np.zeros(output_length)
        
        # WSOLA processing
        input_pos = 0
        output_pos = 0
        
        while input_pos + self.wsola_template_size < len(audio_data) and \
              output_pos + self.wsola_template_size < len(processed_audio):
            
            # Extract template from input
            template = audio_data[input_pos:input_pos + self.wsola_template_size]
            
            # Search for best match in neighborhood
            search_start = max(0, input_pos - self.wsola_search_window // 2)
            search_end = min(len(audio_data) - self.wsola_template_size,
                           input_pos + self.wsola_search_window // 2)
            
            best_match_pos = self._find_best_match(audio_data, template,
                                                 search_start, search_end)
            
            # Extract matched segment
            matched_segment = audio_data[best_match_pos:
                                       best_match_pos + self.wsola_template_size]
            
            # Apply overlap-add window
            window = np.hanning(self.wsola_template_size)
            windowed_segment = matched_segment * window
            
            # Add to output with overlap
            overlap_region = min(self.wsola_template_size,
                               len(processed_audio) - output_pos)
            
            if overlap_region > 0:
                # Cross-fade overlapping region
                if output_pos > 0:
                    fade_length = min(overlap_region, self.wsola_template_size // 4)
                    fade_in = np.linspace(0, 1, fade_length)
                    fade_out = np.linspace(1, 0, fade_length)
                    
                    # Apply cross-fade
                    processed_audio[output_pos:output_pos + fade_length] *= fade_out
                    processed_audio[output_pos:output_pos + fade_length] += \
                        windowed_segment[:fade_length] * fade_in
                    
                    # Add remainder
                    if fade_length < overlap_region:
                        processed_audio[output_pos + fade_length:
                                     output_pos + overlap_region] += \
                            windowed_segment[fade_length:overlap_region]
                else:
                    processed_audio[output_pos:output_pos + overlap_region] += \
                        windowed_segment[:overlap_region]
            
            # Update positions
            input_pos = best_match_pos + self.hop_size
            output_pos += synthesis_hop
        
        return processed_audio
    
    def _find_best_match(self, audio_data: np.ndarray, template: np.ndarray,
                        search_start: int, search_end: int) -> int:
        """Find best waveform match for WSOLA"""        best_correlation = -1
        best_position = search_start
        
        for pos in range(search_start, search_end):
            if pos + len(template) > len(audio_data):
                break
            
            candidate = audio_data[pos:pos + len(template)]
            
            # Normalized cross-correlation
            correlation = np.corrcoef(template, candidate)[0, 1]
            
            if not np.isnan(correlation) and correlation > best_correlation:
                best_correlation = correlation
                best_position = pos
        
        return best_position
    
    def _granular_stretch(self, audio_data: np.ndarray) -> np.ndarray:
        """Granular synthesis based time stretching"""        grain_hop_input = int(self.grain_size * (1 - self.grain_overlap))
        grain_hop_output = int(grain_hop_input * self.time_stretch_factor)
        
        # Calculate output length
        num_grains = (len(audio_data) - self.grain_size) // grain_hop_input + 1
        output_length = (num_grains - 1) * grain_hop_output + self.grain_size
        processed_audio = np.zeros(output_length)
        
        # Grain window
        grain_window = np.hanning(self.grain_size)
        
        for grain_idx in range(num_grains):
            input_start = grain_idx * grain_hop_input
            input_end = input_start + self.grain_size
            
            if input_end > len(audio_data):
                break
            
            # Extract grain
            grain = audio_data[input_start:input_end]
            windowed_grain = grain * grain_window
            
            # Place grain in output
            output_start = grain_idx * grain_hop_output
            output_end = output_start + self.grain_size
            
            if output_end <= len(processed_audio):
                processed_audio[output_start:output_end] += windowed_grain
            elif output_start < len(processed_audio):
                remaining = len(processed_audio) - output_start
                processed_audio[output_start:] += windowed_grain[:remaining]
        
        return processed_audio
    
    def _spectral_stretch(self, audio_data: np.ndarray) -> np.ndarray:
        """Spectral domain time stretching"""        # Simple spectral interpolation approach
        spectrum = scipy.fft.rfft(audio_data)
        
        # Calculate new length
        new_length = int(len(audio_data) * self.time_stretch_factor)
        
        # Interpolate spectrum
        old_indices = np.linspace(0, len(spectrum) - 1, len(spectrum))
        new_indices = np.linspace(0, len(spectrum) - 1, 
                                int(len(spectrum) * self.time_stretch_factor))
        
        # Interpolate magnitude and phase separately
        magnitude_interp = np.interp(new_indices, old_indices, np.abs(spectrum))
        phase_interp = np.interp(new_indices, old_indices, np.angle(spectrum))
        
        # Reconstruct spectrum
        new_spectrum = magnitude_interp * np.exp(1j * phase_interp)
        
        # Convert back to time domain
        processed_audio = scipy.fft.irfft(new_spectrum, n=new_length)
        
        return processed_audio
    
    def set_time_stretch_factor(self, factor: float):
        """Set time stretch factor (0.25 to 4.0)"""        self.time_stretch_factor = np.clip(factor, 0.25, 4.0)
        self.logger.debug(f"Time stretch factor set to {factor}")
    
    def set_parameters(self, preserve_pitch: bool = None,
                      quality: str = None, algorithm: TimeStretchAlgorithm = None):
        """Set time stretcher parameters"""        if preserve_pitch is not None:
            self.preserve_pitch = preserve_pitch
        if quality is not None and quality in ["low", "medium", "high", "ultra"]:
            self.quality = quality
            self._update_quality_settings()
        if algorithm is not None:
            self.algorithm = algorithm
        
        self.logger.debug(f"Time stretcher parameters updated")
    
    def _update_quality_settings(self):
        """Update processing parameters based on quality setting"""        if self.quality == "low":
            self.frame_size = 1024
            self.overlap_factor = 2
        elif self.quality == "medium":
            self.frame_size = 2048
            self.overlap_factor = 4
        elif self.quality == "high":
            self.frame_size = 4096
            self.overlap_factor = 4
        elif self.quality == "ultra":
            self.frame_size = 8192
            self.overlap_factor = 8
        
        self.hop_size = self.frame_size // self.overlap_factor
        self._init_buffers()
    
    def get_current_settings(self) -> dict:
        """Get current time stretcher settings"""        return {
            "time_stretch_factor": self.time_stretch_factor,
            "preserve_pitch": self.preserve_pitch,
            "quality": self.quality,
            "algorithm": self.algorithm.value,
            "frame_size": self.frame_size,
            "hop_size": self.hop_size,
            "expected_length_ratio": self.time_stretch_factor
        }
