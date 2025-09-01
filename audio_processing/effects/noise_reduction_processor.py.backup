"""🔇 Noise Reduction Processor - Professional Noise Suppression Engine

Professional-grade noise reduction with spectral gating, Wiener filtering,
adaptive algorithms, multi-band processing, and AI-assisted noise profiling.
Supports real-time processing with multiple algorithm implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
import logging
from typing import Optional, Tuple, Dict, List, Any
from enum import Enum
from dataclasses import dataclass
import scipy.signal
import scipy.fft
from concurrent.futures import ThreadPoolExecutor
import threading


class NoiseReductionType(Enum):
    """Noise reduction algorithm types"""
    SPECTRAL_GATE = "spectral_gate"
    WIENER_FILTER = "wiener_filter"
    ADAPTIVE = "adaptive"
    MULTI_BAND = "multi_band"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"


class NoiseType(Enum):
    """Common noise types"""
    BROADBAND = "broadband"
    NARROWBAND = "narrowband"
    IMPULSIVE = "impulsive"
    PERIODIC = "periodic"
    AMBIENT = "ambient"
    ELECTRICAL = "electrical"
    ROOM_TONE = "room_tone"


@dataclass
class NoiseProfile:
    """Noise profile data structure"""
    frequency_response: np.ndarray
    magnitude_profile: np.ndarray
    phase_profile: np.ndarray
    noise_type: NoiseType
    confidence: float
    frame_size: int
    sample_rate: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'frequency_response': self.frequency_response.tolist(),
            'magnitude_profile': self.magnitude_profile.tolist(),
            'phase_profile': self.phase_profile.tolist(),
            'noise_type': self.noise_type.value,
            'confidence': self.confidence,
            'frame_size': self.frame_size,
            'sample_rate': self.sample_rate
        }


@dataclass
class NoiseReductionParams:
    """Noise reduction parameters"""
    algorithm: NoiseReductionType = NoiseReductionType.SPECTRAL_GATE
    reduction_amount: float = 12.0  # dB
    noise_floor_offset: float = 6.0  # dB above noise floor
    attack_time: float = 0.01  # seconds
    release_time: float = 0.1  # seconds
    sensitivity: float = 0.5  # 0.0 to 1.0
    preserve_transients: bool = True
    adaptive_learning: bool = True
    smoothing_factor: float = 0.8


class SpectralGate:
    """Professional spectral gating noise reduction"""
    
    def __init__(self, frame_size: int, sample_rate: int):
        self.frame_size = frame_size
        self.sample_rate = sample_rate
        self.gate_history = np.zeros(frame_size // 2 + 1)
        self.smoothing_factor = 0.8
        
    def process(self, magnitude_spectrum: np.ndarray, noise_profile: np.ndarray,
                reduction_amount: float, noise_floor_offset: float) -> np.ndarray:
        """Apply spectral gating"""
        # Calculate gate threshold
        gate_threshold = noise_profile * np.power(10, noise_floor_offset / 20)
        
        # Calculate gate function
        gate = np.minimum(1.0, magnitude_spectrum / (gate_threshold + 1e-10))
        gate = np.power(gate, reduction_amount / 20)
        
        # Smooth gate over time
        self.gate_history = self.smoothing_factor * self.gate_history + \
                           (1 - self.smoothing_factor) * gate
        
        return self.gate_history


class WienerFilter:
    """Wiener filter for noise reduction"""
    
    def __init__(self, frame_size: int, sample_rate: int):
        self.frame_size = frame_size
        self.sample_rate = sample_rate
        self.signal_power_history = np.zeros(frame_size // 2 + 1)
        self.noise_power_history = np.zeros(frame_size // 2 + 1)
        self.alpha = 0.95  # smoothing factor
        
    def process(self, magnitude_spectrum: np.ndarray, noise_profile: np.ndarray,
                signal_estimation: Optional[np.ndarray] = None) -> np.ndarray:
        """Apply Wiener filtering"""
        # Update signal power estimation
        signal_power = magnitude_spectrum ** 2
        self.signal_power_history = self.alpha * self.signal_power_history + \
                                   (1 - self.alpha) * signal_power
        
        # Update noise power estimation
        noise_power = noise_profile ** 2
        self.noise_power_history = self.alpha * self.noise_power_history + \
                                  (1 - self.alpha) * noise_power
        
        # Calculate Wiener filter
        snr = self.signal_power_history / (self.noise_power_history + 1e-10)
        wiener_gain = snr / (snr + 1)
        
        # Apply smoothing to prevent artifacts
        wiener_gain = np.maximum(wiener_gain, 0.1)  # Minimum gain
        
        return wiener_gain


class AdaptiveNoiseReducer:
    """Adaptive noise reduction with learning capabilities"""
    
    def __init__(self, frame_size: int, sample_rate: int):
        self.frame_size = frame_size
        self.sample_rate = sample_rate
        self.adaptation_rate = 0.01
        self.noise_estimate = np.zeros(frame_size // 2 + 1)
        self.signal_estimate = np.zeros(frame_size // 2 + 1)
        self.vad_threshold = 0.1  # Voice activity detection
        
    def voice_activity_detection(self, magnitude_spectrum: np.ndarray) -> bool:
        """Simple voice activity detection"""
        energy = np.sum(magnitude_spectrum ** 2)
        noise_energy = np.sum(self.noise_estimate ** 2)
        return energy > noise_energy * (1 + self.vad_threshold)
    
    def adapt_noise_profile(self, magnitude_spectrum: np.ndarray):
        """Adapt noise profile based on current frame"""
        if not self.voice_activity_detection(magnitude_spectrum):
            # Update noise estimate during non-speech periods
            self.noise_estimate = (1 - self.adaptation_rate) * self.noise_estimate + \
                                 self.adaptation_rate * magnitude_spectrum
        else:
            # Update signal estimate during speech periods
            self.signal_estimate = (1 - self.adaptation_rate) * self.signal_estimate + \
                                  self.adaptation_rate * magnitude_spectrum
    
    def process(self, magnitude_spectrum: np.ndarray) -> np.ndarray:
        """Process with adaptive algorithm"""
        self.adapt_noise_profile(magnitude_spectrum)
        
        # Calculate adaptive gain
        snr = (self.signal_estimate + 1e-10) / (self.noise_estimate + 1e-10)
        gain = np.minimum(1.0, snr / (snr + 1))
        
        # Apply minimum gain to prevent over-suppression
        gain = np.maximum(gain, 0.1)
        
        return gain


class MultiBandNoiseReducer:
    """Multi-band noise reduction processor"""
    
    def __init__(self, frame_size: int, sample_rate: int, num_bands: int = 8):
        self.frame_size = frame_size
        self.sample_rate = sample_rate
        self.num_bands = num_bands
        
        # Create band limits
        nyquist = sample_rate / 2
        self.band_edges = np.logspace(np.log10(20), np.log10(nyquist), num_bands + 1)
        self.band_indices = self._calculate_band_indices()
        
        # Initialize per-band processors
        self.band_gates = [SpectralGate(frame_size, sample_rate) for _ in range(num_bands)]
        
    def _calculate_band_indices(self) -> List[Tuple[int, int]]:
        """Calculate frequency bin indices for each band"""
        indices = []
        freq_bins = np.fft.fftfreq(self.frame_size, 1/self.sample_rate)[:self.frame_size//2 + 1]
        
        for i in range(self.num_bands):
            start_freq = self.band_edges[i]
            end_freq = self.band_edges[i + 1]
            start_idx = np.argmin(np.abs(freq_bins - start_freq))
            end_idx = np.argmin(np.abs(freq_bins - end_freq))
            indices.append((start_idx, end_idx))
        
        return indices
    
    def process(self, magnitude_spectrum: np.ndarray, noise_profile: np.ndarray,
                params: NoiseReductionParams) -> np.ndarray:
        """Process with multi-band approach"""
        gain = np.ones_like(magnitude_spectrum)
        
        for band_idx, (start_idx, end_idx) in enumerate(self.band_indices):
            if end_idx > start_idx:
                # Extract band
                band_magnitude = magnitude_spectrum[start_idx:end_idx]
                band_noise = noise_profile[start_idx:end_idx]
                
                # Process band
                band_gain = self.band_gates[band_idx].process(
                    band_magnitude, band_noise,
                    params.reduction_amount, params.noise_floor_offset
                )
                
                # Apply to full spectrum
                gain[start_idx:end_idx] = band_gain
        
        return gain


class NoiseAnalyzer:
    """AI-assisted noise analysis and profiling"""
    
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.analysis_history = []
        self.max_history = 100
        
    def analyze_noise_characteristics(self, magnitude_spectrum: np.ndarray) -> Dict[str, float]:
        """Analyze noise characteristics"""
        # Spectral features
        spectral_centroid = np.sum(magnitude_spectrum * np.arange(len(magnitude_spectrum))) / \
                           (np.sum(magnitude_spectrum) + 1e-10)
        spectral_spread = np.sqrt(np.sum(magnitude_spectrum * 
                                        (np.arange(len(magnitude_spectrum)) - spectral_centroid)**2) / \
                                 (np.sum(magnitude_spectrum) + 1e-10))
        spectral_flatness = scipy.stats.gmean(magnitude_spectrum + 1e-10) / \
                           (np.mean(magnitude_spectrum) + 1e-10)
        
        # Temporal features
        energy = np.sum(magnitude_spectrum ** 2)
        
        return {
            'spectral_centroid': spectral_centroid,
            'spectral_spread': spectral_spread,
            'spectral_flatness': spectral_flatness,
            'energy': energy
        }
    
    def classify_noise_type(self, features: Dict[str, float]) -> NoiseType:
        """Classify noise type based on features"""
        if features['spectral_flatness'] > 0.8:
            return NoiseType.BROADBAND
        elif features['spectral_spread'] < 100:
            return NoiseType.NARROWBAND
        elif features['energy'] > 1000:
            return NoiseType.IMPULSIVE
        else:
            return NoiseType.AMBIENT
    
    def recommend_parameters(self, noise_type: NoiseType) -> NoiseReductionParams:
        """Recommend optimal parameters based on noise type"""
        params = NoiseReductionParams()
        
        if noise_type == NoiseType.BROADBAND:
            params.algorithm = NoiseReductionType.WIENER_FILTER
            params.reduction_amount = 15.0
            params.sensitivity = 0.7
        elif noise_type == NoiseType.NARROWBAND:
            params.algorithm = NoiseReductionType.SPECTRAL_GATE
            params.reduction_amount = 20.0
            params.sensitivity = 0.9
        elif noise_type == NoiseType.IMPULSIVE:
            params.algorithm = NoiseReductionType.ADAPTIVE
            params.reduction_amount = 8.0
            params.attack_time = 0.001
            params.sensitivity = 0.3
        
        return params


class NoiseReductionProcessor:
    """Professional noise reduction processor with multiple algorithms"""
    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Processing parameters
        self.frame_size = 2048
        self.hop_size = self.frame_size // 4
        self.params = NoiseReductionParams()
        
        # Initialize processing components
        self._init_processors()
        
        # Noise profile management
        self.noise_profile: Optional[NoiseProfile] = None
        self.noise_profile_learned = False
        self.learning_frames = 0
        self.min_learning_frames = 50
        
        # Processing buffers
        self.overlap_buffer = np.zeros(self.frame_size)
        self.window = np.hanning(self.frame_size)
        
        # Real-time processing
        self.processing_lock = threading.Lock()
        self.is_processing = False
        
    def _init_processors(self):
        """Initialize processing components"""
        try:
            self.spectral_gate = SpectralGate(self.frame_size, self.sample_rate)
            self.wiener_filter = WienerFilter(self.frame_size, self.sample_rate)
            self.adaptive_reducer = AdaptiveNoiseReducer(self.frame_size, self.sample_rate)
            self.multiband_reducer = MultiBandNoiseReducer(self.frame_size, self.sample_rate)
            self.noise_analyzer = NoiseAnalyzer(self.sample_rate)
            
            self.logger.info("Noise reduction processors initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize noise reduction processors: {e}")
            raise
    
    def learn_noise_profile(self, audio_data: np.ndarray, 
                           noise_start: float = 0.0, 
                           noise_duration: float = 1.0) -> NoiseProfile:
        """Learn noise profile from audio segment"""
        try:
            # Extract noise segment
            start_sample = int(noise_start * self.sample_rate)
            duration_samples = int(noise_duration * self.sample_rate)
            noise_segment = audio_data[start_sample:start_sample + duration_samples]
            
            # Process in frames to build profile
            magnitude_accumulator = np.zeros(self.frame_size // 2 + 1)
            phase_accumulator = np.zeros(self.frame_size // 2 + 1, dtype=complex)
            frame_count = 0
            
            for i in range(0, len(noise_segment) - self.frame_size, self.hop_size):
                frame = noise_segment[i:i + self.frame_size] * self.window
                
                # FFT analysis
                spectrum = np.fft.fft(frame)
                magnitude = np.abs(spectrum[:self.frame_size // 2 + 1])
                phase = spectrum[:self.frame_size // 2 + 1]
                
                magnitude_accumulator += magnitude
                phase_accumulator += phase
                frame_count += 1
            
            if frame_count == 0:
                raise ValueError("No frames available for noise profiling")
            
            # Average the accumulated data
            avg_magnitude = magnitude_accumulator / frame_count
            avg_phase = phase_accumulator / frame_count
            
            # Analyze noise characteristics
            features = self.noise_analyzer.analyze_noise_characteristics(avg_magnitude)
            noise_type = self.noise_analyzer.classify_noise_type(features)
            
            # Calculate confidence based on consistency
            confidence = min(1.0, frame_count / self.min_learning_frames)
            
            # Create frequency response
            freq_bins = np.fft.fftfreq(self.frame_size, 1/self.sample_rate)[:self.frame_size//2 + 1]
            
            profile = NoiseProfile(
                frequency_response=freq_bins,
                magnitude_profile=avg_magnitude,
                phase_profile=np.angle(avg_phase),
                noise_type=noise_type,
                confidence=confidence,
                frame_size=self.frame_size,
                sample_rate=self.sample_rate
            )
            
            self.noise_profile = profile
            self.noise_profile_learned = True
            
            # Update parameters based on noise type
            self.params = self.noise_analyzer.recommend_parameters(noise_type)
            
            self.logger.info(f"Learned noise profile: type={noise_type.value}, confidence={confidence:.2f}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to learn noise profile: {e}")
            raise
    
    def update_parameters(self, **kwargs):
        """Update processing parameters"""
        for key, value in kwargs.items():
            if hasattr(self.params, key):
                setattr(self.params, key, value)
                self.logger.debug(f"Updated parameter {key} = {value}")
    
    def process_frame(self, audio_frame: np.ndarray) -> np.ndarray:
        """Process single audio frame"""
        if self.noise_profile is None:
            self.logger.warning("No noise profile available, returning original frame")
            return audio_frame
        
        try:
            # Apply window
            windowed_frame = audio_frame * self.window
            
            # FFT analysis
            spectrum = np.fft.fft(windowed_frame)
            magnitude = np.abs(spectrum[:self.frame_size // 2 + 1])
            phase = np.angle(spectrum[:self.frame_size // 2 + 1])
            
            # Select algorithm
            if self.params.algorithm == NoiseReductionType.SPECTRAL_GATE:
                gain = self.spectral_gate.process(
                    magnitude, 
                    self.noise_profile.magnitude_profile,
                    self.params.reduction_amount,
                    self.params.noise_floor_offset
                )
            
            elif self.params.algorithm == NoiseReductionType.WIENER_FILTER:
                gain = self.wiener_filter.process(
                    magnitude,
                    self.noise_profile.magnitude_profile
                )
            
            elif self.params.algorithm == NoiseReductionType.ADAPTIVE:
                gain = self.adaptive_reducer.process(magnitude)
            
            elif self.params.algorithm == NoiseReductionType.MULTI_BAND:
                gain = self.multiband_reducer.process(
                    magnitude,
                    self.noise_profile.magnitude_profile,
                    self.params
                )
            
            elif self.params.algorithm == NoiseReductionType.ENSEMBLE:
                # Combine multiple algorithms
                gate_gain = self.spectral_gate.process(
                    magnitude, self.noise_profile.magnitude_profile,
                    self.params.reduction_amount, self.params.noise_floor_offset
                )
                wiener_gain = self.wiener_filter.process(
                    magnitude, self.noise_profile.magnitude_profile
                )
                adaptive_gain = self.adaptive_reducer.process(magnitude)
                
                # Weighted average
                gain = (0.4 * gate_gain + 0.4 * wiener_gain + 0.2 * adaptive_gain)
            
            else:
                gain = np.ones_like(magnitude)
            
            # Apply gain with smoothing
            processed_magnitude = magnitude * gain
            
            # Reconstruct spectrum
            processed_spectrum = np.zeros(self.frame_size, dtype=complex)
            processed_spectrum[:self.frame_size // 2 + 1] = processed_magnitude * np.exp(1j * phase)
            processed_spectrum[self.frame_size // 2 + 1:] = np.conj(processed_spectrum[1:self.frame_size // 2][::-1])
            
            # IFFT
            processed_frame = np.real(np.fft.ifft(processed_spectrum))
            
            # Apply window again for overlap-add
            processed_frame *= self.window
            
            return processed_frame
            
        except Exception as e:
            self.logger.error(f"Frame processing failed: {e}")
            return audio_frame
    
    def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Process complete audio with overlap-add"""
        if not self.noise_profile_learned:
            self.logger.warning("No noise profile learned, attempting auto-learn from first second")
            self.learn_noise_profile(audio_data, 0.0, min(1.0, len(audio_data)/self.sample_rate))
        
        with self.processing_lock:
            self.is_processing = True
            
            try:
                # Prepare output buffer
                output = np.zeros_like(audio_data)
                
                # Process with overlap-add
                for i in range(0, len(audio_data) - self.frame_size, self.hop_size):
                    # Extract frame
                    frame = audio_data[i:i + self.frame_size]
                    
                    # Process frame
                    processed_frame = self.process_frame(frame)
                    
                    # Overlap-add
                    output[i:i + self.frame_size] += processed_frame
                
                self.logger.info(f"Processed {len(audio_data)} samples with {self.params.algorithm.value}")
                return output
                
            except Exception as e:
                self.logger.error(f"Audio processing failed: {e}")
                return audio_data
                
            finally:
                self.is_processing = False
    
    def process_realtime(self, audio_frame: np.ndarray) -> np.ndarray:
        """Real-time processing with minimal latency"""
        if self.processing_lock.locked():
            return audio_frame  # Skip if busy
        
        try:
            with self.processing_lock:
                # Add to overlap buffer
                self.overlap_buffer[:-len(audio_frame)] = self.overlap_buffer[len(audio_frame):]
                self.overlap_buffer[-len(audio_frame):] = audio_frame
                
                # Process if we have enough data
                if len(audio_frame) == self.hop_size:
                    processed_frame = self.process_frame(self.overlap_buffer)
                    return processed_frame[-self.hop_size:]
                
                return audio_frame
                
        except Exception as e:
            self.logger.error(f"Real-time processing failed: {e}")
            return audio_frame
    
    def get_noise_reduction_info(self) -> Dict[str, Any]:
        """Get current noise reduction information"""
        info = {
            'algorithm': self.params.algorithm.value,
            'reduction_amount': self.params.reduction_amount,
            'noise_floor_offset': self.params.noise_floor_offset,
            'frame_size': self.frame_size,
            'hop_size': self.hop_size,
            'sample_rate': self.sample_rate,
            'is_processing': self.is_processing,
            'noise_profile_learned': self.noise_profile_learned
        }
        
        if self.noise_profile:
            info['noise_profile'] = {
                'noise_type': self.noise_profile.noise_type.value,
                'confidence': self.noise_profile.confidence,
                'frequency_range': f"{self.noise_profile.frequency_response[0]:.1f} - {self.noise_profile.frequency_response[-1]:.1f} Hz"
            }
        
        return info
    
    def save_noise_profile(self, filepath: str):
        """Save noise profile to file"""
        if self.noise_profile is None:
            raise ValueError("No noise profile to save")
        
        try:
            import json
            with open(filepath, 'w') as f:
                json.dump(self.noise_profile.to_dict(), f, indent=2)
            self.logger.info(f"Noise profile saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save noise profile: {e}")
            raise
    
    def load_noise_profile(self, filepath: str):
        """Load noise profile from file"""
        try:
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.noise_profile = NoiseProfile(
                frequency_response=np.array(data['frequency_response']),
                magnitude_profile=np.array(data['magnitude_profile']),
                phase_profile=np.array(data['phase_profile']),
                noise_type=NoiseType(data['noise_type']),
                confidence=data['confidence'],
                frame_size=data['frame_size'],
                sample_rate=data['sample_rate']
            )
            
            self.noise_profile_learned = True
            self.logger.info(f"Noise profile loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to load noise profile: {e}")
            raise
    
    def reset(self):
        """Reset processor state"""
        self.noise_profile = None
        self.noise_profile_learned = False
        self.learning_frames = 0
        self.overlap_buffer.fill(0)
        
        # Reset algorithm states
        self._init_processors()
        
        self.logger.info("Noise reduction processor reset")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'processing_lock'):
            with self.processing_lock:
                pass  # Ensure any ongoing processing completes
        self.adaptation_rate = 0.01
        
        self.logger.info("NoiseReductionProcessor initialized")
    
    def _init_buffers(self):
        """Initialize processing buffers"""
        self.input_buffer = np.zeros(self.frame_size * 2)
        self.output_buffer = np.zeros(self.frame_size * 2)
        self.overlap_buffer = np.zeros(self.frame_size)
        
        # Window function
        self.window = np.hanning(self.frame_size)
        
        # Smoothing coefficients for gain calculation
        self.attack_coeff = np.exp(-1.0 / (self.attack_time * self.sample_rate))
        self.release_coeff = np.exp(-1.0 / (self.release_time * self.sample_rate))
        
        # Previous gain values for smoothing
        self.prev_gains = np.ones(self.frame_size // 2 + 1)
    
    def learn_noise_profile(self, noise_sample: np.ndarray) -> bool:
        """Learn noise profile from noise-only audio sample"""
        try:
            if len(noise_sample) < self.frame_size:
                self.logger.warning("Noise sample too short for reliable profiling")
                return False
            
            # Process in frames to build noise profile
            num_frames = len(noise_sample) // self.hop_size - 3
            noise_spectrum_sum = np.zeros(self.frame_size // 2 + 1)
            frame_count = 0
            
            for i in range(num_frames):
                start_idx = i * self.hop_size
                frame = noise_sample[start_idx:start_idx + self.frame_size]
                
                if len(frame) < self.frame_size:
                    frame = np.pad(frame, (0, self.frame_size - len(frame)))
                
                # Apply window and compute spectrum
                windowed_frame = frame * self.window
                spectrum = np.abs(scipy.fft.rfft(windowed_frame))
                
                noise_spectrum_sum += spectrum**2
                frame_count += 1
            
            if frame_count > 0:
                # Average noise spectrum (power)
                self.noise_profile = noise_spectrum_sum / frame_count
                self.noise_profile_learned = True
                
                self.logger.info(f"Noise profile learned from {frame_count} frames")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to learn noise profile: {e}")
            return False
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply noise reduction processing"""
        try:
            if not self.noise_profile_learned:
                self.logger.warning("No noise profile available, using adaptive mode")
                return self._adaptive_noise_reduction(audio_data)
            
            if self.algorithm == NoiseReductionType.SPECTRAL_GATE:
                return self._spectral_gate_reduction(audio_data)
            elif self.algorithm == NoiseReductionType.WIENER_FILTER:
                return self._wiener_filter_reduction(audio_data)
            elif self.algorithm == NoiseReductionType.ADAPTIVE:
                return self._adaptive_noise_reduction(audio_data)
            elif self.algorithm == NoiseReductionType.MULTI_BAND:
                return self._multiband_noise_reduction(audio_data)
            else:
                return self._spectral_gate_reduction(audio_data)
            
        except Exception as e:
            self.logger.error(f"Noise reduction processing failed: {e}")
            return audio_data
    
    def _spectral_gate_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Spectral gating noise reduction"""
        processed_audio = np.zeros_like(audio_data)
        
        # Process in overlapping frames
        num_frames = (len(audio_data) - self.frame_size) // self.hop_size + 1
        
        for frame_idx in range(num_frames):
            start_idx = frame_idx * self.hop_size
            end_idx = start_idx + self.frame_size
            
            if end_idx > len(audio_data):
                break
            
            # Extract frame
            frame = audio_data[start_idx:end_idx]
            windowed_frame = frame * self.window
            
            # Compute spectrum
            spectrum = scipy.fft.rfft(windowed_frame)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)
            
            # Calculate noise gate
            power_spectrum = magnitude**2
            
            # Threshold based on noise profile
            threshold = (self.noise_profile * 
                        10**(self.noise_floor_offset / 10))
            
            # Calculate gain reduction
            gain = np.ones_like(magnitude)
            below_threshold = power_spectrum < threshold
            
            if np.any(below_threshold):
                reduction_linear = 10**(-self.reduction_amount / 20)
                gain[below_threshold] = reduction_linear
            
            # Smooth gain changes
            gain = self._smooth_gains(gain)
            
            # Apply gain
            processed_spectrum = magnitude * gain * np.exp(1j * phase)
            
            # Convert back to time domain
            processed_frame = scipy.fft.irfft(processed_spectrum)
            processed_frame *= self.window
            
            # Overlap-add
            if frame_idx == 0:
                processed_audio[start_idx:end_idx] += processed_frame
            else:
                processed_audio[start_idx:start_idx + self.hop_size] += processed_frame[:self.hop_size]
                if end_idx <= len(processed_audio):
                    processed_audio[start_idx + self.hop_size:end_idx] += processed_frame[self.hop_size:]
        
        return processed_audio
    
    def _wiener_filter_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Wiener filter based noise reduction"""
        processed_audio = np.zeros_like(audio_data)
        num_frames = (len(audio_data) - self.frame_size) // self.hop_size + 1
        
        for frame_idx in range(num_frames):
            start_idx = frame_idx * self.hop_size
            end_idx = start_idx + self.frame_size
            
            if end_idx > len(audio_data):
                break
            
            frame = audio_data[start_idx:end_idx]
            windowed_frame = frame * self.window
            
            spectrum = scipy.fft.rfft(windowed_frame)
            power_spectrum = np.abs(spectrum)**2
            
            # Wiener filter gain
            snr_estimate = power_spectrum / (self.noise_profile + 1e-10)
            wiener_gain = snr_estimate / (snr_estimate + 1.0)
            
            # Smooth gain
            wiener_gain = self._smooth_gains(wiener_gain)
            
            # Apply filter
            processed_spectrum = spectrum * wiener_gain
            processed_frame = scipy.fft.irfft(processed_spectrum)
            processed_frame *= self.window
            
            # Overlap-add
            if frame_idx == 0:
                processed_audio[start_idx:end_idx] += processed_frame
            else:
                processed_audio[start_idx:start_idx + self.hop_size] += processed_frame[:self.hop_size]
                if end_idx <= len(processed_audio):
                    processed_audio[start_idx + self.hop_size:end_idx] += processed_frame[self.hop_size:]
        
        return processed_audio
    
    def _adaptive_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Adaptive noise reduction without prior noise profile"""
        processed_audio = np.zeros_like(audio_data)
        num_frames = (len(audio_data) - self.frame_size) // self.hop_size + 1
        
        # Initialize adaptive noise estimate
        if self.noise_profile is None:
            self.noise_profile = np.ones(self.frame_size // 2 + 1) * 1e-6
        
        for frame_idx in range(num_frames):
            start_idx = frame_idx * self.hop_size
            end_idx = start_idx + self.frame_size
            
            if end_idx > len(audio_data):
                break
            
            frame = audio_data[start_idx:end_idx]
            windowed_frame = frame * self.window
            
            spectrum = scipy.fft.rfft(windowed_frame)
            power_spectrum = np.abs(spectrum)**2
            
            # Adaptive noise estimation
            # Update noise profile in quiet regions
            noise_update_mask = power_spectrum < (self.noise_profile * 3)
            
            self.noise_profile[noise_update_mask] = (
                (1 - self.adaptation_rate) * self.noise_profile[noise_update_mask] +
                self.adaptation_rate * power_spectrum[noise_update_mask]
            )
            
            # Calculate adaptive gain
            snr_estimate = power_spectrum / (self.noise_profile + 1e-10)
            adaptive_gain = np.minimum(1.0, np.maximum(0.1, snr_estimate / (snr_estimate + 1)))
            
            # Smooth and apply gain
            adaptive_gain = self._smooth_gains(adaptive_gain)
            processed_spectrum = spectrum * adaptive_gain
            
            processed_frame = scipy.fft.irfft(processed_spectrum)
            processed_frame *= self.window
            
            # Overlap-add
            if frame_idx == 0:
                processed_audio[start_idx:end_idx] += processed_frame
            else:
                processed_audio[start_idx:start_idx + self.hop_size] += processed_frame[:self.hop_size]
                if end_idx <= len(processed_audio):
                    processed_audio[start_idx + self.hop_size:end_idx] += processed_frame[self.hop_size:]
        
        return processed_audio
    
    def _multiband_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Multi-band noise reduction with frequency-dependent processing"""
        # Define frequency bands
        band_edges = [0, 200, 1000, 4000, 8000, self.sample_rate // 2]
        
        # Apply different reduction amounts per band
        band_reductions = [15, 12, 8, 10, 12]  # dB
        
        processed_audio = np.zeros_like(audio_data)
        num_frames = (len(audio_data) - self.frame_size) // self.hop_size + 1
        
        # Frequency bins
        freqs = np.fft.rfftfreq(self.frame_size, 1/self.sample_rate)
        
        for frame_idx in range(num_frames):
            start_idx = frame_idx * self.hop_size
            end_idx = start_idx + self.frame_size
            
            if end_idx > len(audio_data):
                break
            
            frame = audio_data[start_idx:end_idx]
            windowed_frame = frame * self.window
            
            spectrum = scipy.fft.rfft(windowed_frame)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)
            power_spectrum = magnitude**2
            
            # Calculate band-specific gains
            gain = np.ones_like(magnitude)
            
            for i in range(len(band_edges) - 1):
                # Find frequency bins in this band
                band_mask = (freqs >= band_edges[i]) & (freqs < band_edges[i+1])
                
                if np.any(band_mask):
                    # Threshold for this band
                    band_noise = self.noise_profile[band_mask]
                    threshold = band_noise * 10**(self.noise_floor_offset / 10)
                    
                    # Noise gate for this band
                    below_threshold = power_spectrum[band_mask] < threshold
                    if np.any(below_threshold):
                        reduction_linear = 10**(-band_reductions[i] / 20)
                        gain[band_mask][below_threshold] = reduction_linear
            
            # Smooth and apply gain
            gain = self._smooth_gains(gain)
            processed_spectrum = magnitude * gain * np.exp(1j * phase)
            
            processed_frame = scipy.fft.irfft(processed_spectrum)
            processed_frame *= self.window
            
            # Overlap-add
            if frame_idx == 0:
                processed_audio[start_idx:end_idx] += processed_frame
            else:
                processed_audio[start_idx:start_idx + self.hop_size] += processed_frame[:self.hop_size]
                if end_idx <= len(processed_audio):
                    processed_audio[start_idx + self.hop_size:end_idx] += processed_frame[self.hop_size:]
        
        return processed_audio
    
    def _smooth_gains(self, gains: np.ndarray) -> np.ndarray:
        """Smooth gain changes to avoid artifacts"""
        smoothed_gains = np.zeros_like(gains)
        
        for i in range(len(gains)):
            if gains[i] < self.prev_gains[i]:
                # Attack (gain reduction)
                smoothed_gains[i] = (self.attack_coeff * self.prev_gains[i] + 
                                   (1 - self.attack_coeff) * gains[i])
            else:
                # Release (gain recovery)
                smoothed_gains[i] = (self.release_coeff * self.prev_gains[i] + 
                                   (1 - self.release_coeff) * gains[i])
        
        self.prev_gains = smoothed_gains.copy()
        return smoothed_gains
    
    def set_parameters(self, reduction_amount: float = None,
                      noise_floor_offset: float = None,
                      attack_time: float = None, release_time: float = None):
        """Set noise reduction parameters"""
        if reduction_amount is not None:
            self.reduction_amount = max(0.0, min(40.0, reduction_amount))
        if noise_floor_offset is not None:
            self.noise_floor_offset = max(0.0, min(20.0, noise_floor_offset))
        if attack_time is not None:
            self.attack_time = max(0.001, min(1.0, attack_time))
            self.attack_coeff = np.exp(-1.0 / (self.attack_time * self.sample_rate))
        if release_time is not None:
            self.release_time = max(0.01, min(5.0, release_time))
            self.release_coeff = np.exp(-1.0 / (self.release_time * self.sample_rate))
        
        self.logger.debug(f"Noise reduction parameters updated")
    
    def get_noise_profile_stats(self) -> dict:
        """Get statistics about the current noise profile"""
        if self.noise_profile is None:
            return {"status": "No noise profile available"}
        
        freqs = np.fft.rfftfreq(self.frame_size, 1/self.sample_rate)
        
        return {
            "status": "Active",
            "profile_length": len(self.noise_profile),
            "frequency_range": f"{freqs[0]:.1f} - {freqs[-1]:.1f} Hz",
            "noise_floor_db": 10 * np.log10(np.mean(self.noise_profile) + 1e-10),
            "peak_noise_freq": freqs[np.argmax(self.noise_profile)]
        }
