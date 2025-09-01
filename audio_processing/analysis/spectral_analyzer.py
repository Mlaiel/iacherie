"""🔍 Spectral Analyzer - Advanced Frequency Domain Audio Analysis

Professional spectral analysis engine providing comprehensive frequency domain
analysis, spectral feature extraction, and advanced signal processing capabilities.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import librosa
import scipy.signal
from scipy.fft import fft, fftfreq


class WindowType(Enum):
    """
Audio window types for spectral analysis"""

    HANN = "hann"
    HAMMING = "hamming"
    BLACKMAN = "blackman"
    KAISER = "kaiser"
    TUKEY = "tukey"


class SpectralFeatureType(Enum):
    """Types of spectral features to extract"""

    CENTROID = "spectral_centroid"
    ROLLOFF = "spectral_rolloff"
    BANDWIDTH = "spectral_bandwidth"
    CONTRAST = "spectral_contrast"
    FLATNESS = "spectral_flatness"
    FLUX = "spectral_flux"
    ENERGY = "spectral_energy"


@dataclass
class SpectralAnalysisResult:
    """Complete spectral analysis results"""
    sample_rate: int
    duration: float
    frequency_bins: np.ndarray
    magnitude_spectrum: np.ndarray
    phase_spectrum: np.ndarray
    power_spectrum: np.ndarray
    spectral_features: Dict[str, np.ndarray]
    peak_frequencies: List[Tuple[float, float]]  # (frequency, magnitude)
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    spectral_bandwidth: np.ndarray
    zero_crossing_rate: np.ndarray
    energy_distribution: Dict[str, float]
    harmonic_analysis: Dict[str, Any]
    noise_floor: float
    dynamic_range: float
    analysis_timestamp: float


class SpectralAnalyzer:
    """
    🎼 Professional Spectral Analysis Engine
    
    Advanced frequency domain analysis with comprehensive spectral feature
    extraction, peak detection, harmonic analysis, and noise characterization.
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 frame_size: int = 2048,
                 hop_length: int = 512,
                 window_type: WindowType = WindowType.HANN,
                 n_fft: Optional[int] = None):
        """
        Initialize spectral analyzer with advanced configuration
        
        Args:
            sample_rate: Audio sample rate
            frame_size: Analysis frame size
            hop_length: Hop length between frames
            window_type: Window function type
            n_fft: FFT size (defaults to frame_size)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.hop_length = hop_length
        self.window_type = window_type
        self.n_fft = n_fft or frame_size
        
        # Initialize analysis parameters
        self.nyquist_freq = sample_rate / 2
        self.freq_resolution = sample_rate / self.n_fft
        
        # Frequency band definitions for energy distribution
        self.frequency_bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mid': (250, 500),
            'mid': (500, 2000),
            'high_mid': (2000, 4000),
            'presence': (4000, 6000),
            'brilliance': (6000, 20000)
        }
        
        # Analysis window
        self.window = self._create_window()
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self.logger.info(f"SpectralAnalyzer initialized: {sample_rate}Hz, frame_size={frame_size}")
    
    def _create_window(self) -> np.ndarray:
        """Create analysis window function"""
        if self.window_type == WindowType.HANN:
            return np.hanning(self.frame_size)
        elif self.window_type == WindowType.HAMMING:
            return np.hamming(self.frame_size)
        elif self.window_type == WindowType.BLACKMAN:
            return np.blackman(self.frame_size)
        elif self.window_type == WindowType.KAISER:
            return np.kaiser(self.frame_size, beta=8.6)
        elif self.window_type == WindowType.TUKEY:
            return scipy.signal.windows.tukey(self.frame_size, alpha=0.5)
        else:
            return np.hanning(self.frame_size)
    
    async def analyze_spectrum(self, 
                             audio_data: np.ndarray,
                             normalize: bool = True) -> SpectralAnalysisResult:
        """
        Perform comprehensive spectral analysis
        
        Args:
            audio_data: Input audio signal
            normalize: Whether to normalize the input
            
        Returns:
            Complete spectral analysis results
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            if normalize:
                audio_data = audio_data / (np.max(np.abs(audio_data)) + 1e-10)
            
            # Basic analysis
            duration = len(audio_data) / self.sample_rate
            
            # Compute FFT-based analysis
            magnitude_spectrum, phase_spectrum, frequency_bins = await self._compute_fft_analysis(audio_data)
            power_spectrum = magnitude_spectrum ** 2
            
            # Extract spectral features in parallel
            tasks = [
                self._extract_spectral_features(audio_data),
                self._detect_peaks(magnitude_spectrum, frequency_bins),
                self._compute_energy_distribution(power_spectrum, frequency_bins),
                self._analyze_harmonics(audio_data),
                self._compute_noise_characteristics(magnitude_spectrum)
            ]
            
            results = await asyncio.gather(*tasks)
            spectral_features, peak_frequencies, energy_distribution, harmonic_analysis, (noise_floor, dynamic_range) = results
            
            # Create analysis result
            analysis_result = SpectralAnalysisResult(
                sample_rate=self.sample_rate,
                duration=duration,
                frequency_bins=frequency_bins,
                magnitude_spectrum=magnitude_spectrum,
                phase_spectrum=phase_spectrum,
                power_spectrum=power_spectrum,
                spectral_features=spectral_features,
                peak_frequencies=peak_frequencies,
                spectral_centroid=spectral_features.get('spectral_centroid', np.array([])),
                spectral_rolloff=spectral_features.get('spectral_rolloff', np.array([])),
                spectral_bandwidth=spectral_features.get('spectral_bandwidth', np.array([])),
                zero_crossing_rate=spectral_features.get('zero_crossing_rate', np.array([])),
                energy_distribution=energy_distribution,
                harmonic_analysis=harmonic_analysis,
                noise_floor=noise_floor,
                dynamic_range=dynamic_range,
                analysis_timestamp=start_time
            )
            
            self.logger.info(f"Spectral analysis completed in {asyncio.get_event_loop().time() - start_time:.3f}s")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Spectral analysis failed: {e}")
            raise
    
    async def _compute_fft_analysis(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute FFT-based spectral analysis"""
        def compute_fft():
            # Apply window
            windowed_audio = audio_data[:self.frame_size] * self.window if len(audio_data) >= self.frame_size else audio_data
            
            # Compute FFT
            fft_result = fft(windowed_audio, n=self.n_fft)
            
            # Extract magnitude and phase
            magnitude = np.abs(fft_result[:self.n_fft//2])
            phase = np.angle(fft_result[:self.n_fft//2])
            
            # Frequency bins
            freqs = fftfreq(self.n_fft, 1/self.sample_rate)[:self.n_fft//2]
            
            return magnitude, phase, freqs
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute_fft)
    
    async def _extract_spectral_features(self, audio_data: np.ndarray) -> Dict[str, np.ndarray]:
        """
Extract comprehensive spectral features"""
        def extract_features():
            features = {}
            
            # Spectral centroid
            features['spectral_centroid'] = librosa.feature.spectral_centroid(
                y=audio_data, sr=self.sample_rate, hop_length=self.hop_length)[0]
            
            # Spectral rolloff
            features['spectral_rolloff'] = librosa.feature.spectral_rolloff(
                y=audio_data, sr=self.sample_rate, hop_length=self.hop_length)[0]
            
            # Spectral bandwidth
            features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(
                y=audio_data, sr=self.sample_rate, hop_length=self.hop_length)[0]
            
            # Spectral contrast
            features['spectral_contrast'] = librosa.feature.spectral_contrast(
                y=audio_data, sr=self.sample_rate, hop_length=self.hop_length)
            
            # Spectral flatness
            features['spectral_flatness'] = librosa.feature.spectral_flatness(
                y=audio_data, hop_length=self.hop_length)[0]
            
            # Zero crossing rate
            features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(
                audio_data, hop_length=self.hop_length)[0]
            
            # RMS energy
            features['rms_energy'] = librosa.feature.rms(
                y=audio_data, hop_length=self.hop_length)[0]
            
            return features
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, extract_features)
    
    async def _detect_peaks(self, 
                          magnitude_spectrum: np.ndarray, 
                          frequency_bins: np.ndarray,
                          min_height_ratio: float = 0.1,
                          max_peaks: int = 20) -> List[Tuple[float, float]]:
        """
Detect spectral peaks"""
        def detect_peaks():
            # Find peaks
            threshold = np.max(magnitude_spectrum) * min_height_ratio
            peak_indices, _ = scipy.signal.find_peaks(magnitude_spectrum, height=threshold)
            
            # Sort by magnitude
            peak_magnitudes = magnitude_spectrum[peak_indices]
            sorted_indices = np.argsort(peak_magnitudes)[::-1]
            
            # Get top peaks
            top_peak_indices = peak_indices[sorted_indices[:max_peaks]]
            
            peaks = []
            for idx in top_peak_indices:
                if idx < len(frequency_bins):
                    freq = frequency_bins[idx]
                    magnitude = magnitude_spectrum[idx]
                    peaks.append((freq, magnitude))
            
            return peaks
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, detect_peaks)
    
    async def _compute_energy_distribution(self, 
                                         power_spectrum: np.ndarray, 
                                         frequency_bins: np.ndarray) -> Dict[str, float]:
        """
Compute energy distribution across frequency bands"""
        def compute_energy():
            total_energy = np.sum(power_spectrum)
            energy_distribution = {}
            
            for band_name, (low_freq, high_freq) in self.frequency_bands.items():
                # Find frequency indices for this band
                band_mask = (frequency_bins >= low_freq) & (frequency_bins <= high_freq)
                band_energy = np.sum(power_spectrum[band_mask])
                
                # Normalize by total energy
                energy_distribution[band_name] = float(band_energy / (total_energy + 1e-10))
            
            return energy_distribution
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute_energy)
    
    async def _analyze_harmonics(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """
Analyze harmonic content"""
        def analyze():
            harmonic_analysis = {}
            
            try:
                # Harmonic-percussive separation
                harmonic, percussive = librosa.effects.hpss(audio_data)
                
                # Harmonic ratio
                harmonic_energy = np.sum(harmonic ** 2)
                total_energy = np.sum(audio_data ** 2)
                harmonic_ratio = harmonic_energy / (total_energy + 1e-10)
                
                # Pitch detection
                f0, voiced_flag, voiced_probs = librosa.pyin(
                    audio_data, 
                    fmin=librosa.note_to_hz('C2'), 
                    fmax=librosa.note_to_hz('C7'),
                    sr=self.sample_rate
                )
                
                # Filter out unvoiced segments
                f0_clean = f0[voiced_flag]
                fundamental_freq = np.median(f0_clean) if len(f0_clean) > 0 else 0
                
                harmonic_analysis = {
                    'harmonic_ratio': float(harmonic_ratio),
                    'fundamental_frequency': float(fundamental_freq),
                    'voiced_segments_ratio': float(np.mean(voiced_flag)),
                    'pitch_stability': float(np.std(f0_clean)) if len(f0_clean) > 0 else 0
                }
                
            except Exception as e:
                self.logger.warning(f"Harmonic analysis failed: {e}")
                harmonic_analysis = {
                    'harmonic_ratio': 0.0,
                    'fundamental_frequency': 0.0,
                    'voiced_segments_ratio': 0.0,
                    'pitch_stability': 0.0
                }
            
            return harmonic_analysis
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    async def _compute_noise_characteristics(self, 
                                           magnitude_spectrum: np.ndarray) -> Tuple[float, float]:
        """Compute noise floor and dynamic range"""
        def compute_noise():
            # Noise floor estimation (10th percentile)
            noise_floor = np.percentile(magnitude_spectrum, 10)
            
            # Dynamic range (peak to noise floor ratio in dB)
            peak_magnitude = np.max(magnitude_spectrum)
            dynamic_range = 20 * np.log10((peak_magnitude + 1e-10) / (noise_floor + 1e-10))
            
            return float(noise_floor), float(dynamic_range)
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute_noise)
    
    def analyze_real_time_frame(self, frame: np.ndarray) -> Dict[str, float]:
        """
        Real-time spectral analysis for single frame
        Optimized for low-latency processing
        """
        try:
            # Apply window
            windowed_frame = frame * self.window[:len(frame)]
            
            # Compute FFT
            fft_result = fft(windowed_frame, n=self.n_fft)
            magnitude = np.abs(fft_result[:self.n_fft//2])
            
            # Compute basic features quickly
            spectral_centroid = np.sum(magnitude * np.arange(len(magnitude))) / (np.sum(magnitude) + 1e-10)
            spectral_centroid_hz = spectral_centroid * self.sample_rate / self.n_fft
            
            # RMS energy
            rms_energy = np.sqrt(np.mean(frame ** 2))
            
            # Peak frequency
            peak_bin = np.argmax(magnitude)
            peak_frequency = peak_bin * self.sample_rate / self.n_fft
            
            # Spectral flux (requires previous frame - simplified)
            spectral_flux = np.sum(np.diff(magnitude) ** 2)
            
            return {
                'spectral_centroid': float(spectral_centroid_hz),
                'rms_energy': float(rms_energy),
                'peak_frequency': float(peak_frequency),
                'spectral_flux': float(spectral_flux)
            }
            
        except Exception as e:
            self.logger.error(f"Real-time spectral analysis failed: {e}")
            return {
                'spectral_centroid': 0.0,
                'rms_energy': 0.0,
                'peak_frequency': 0.0,
                'spectral_flux': 0.0
            }
    
    def get_frequency_band_analysis(self, 
                                  power_spectrum: np.ndarray, 
                                  frequency_bins: np.ndarray) -> Dict[str, Dict[str, float]]:
        """Get detailed analysis for each frequency band"""
        band_analysis = {}
        
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            band_mask = (frequency_bins >= low_freq) & (frequency_bins <= high_freq)
            band_spectrum = power_spectrum[band_mask]
            
            if len(band_spectrum) > 0:
                band_analysis[band_name] = {
                    'energy': float(np.sum(band_spectrum)),
                    'peak_magnitude': float(np.max(band_spectrum)),
                    'average_magnitude': float(np.mean(band_spectrum)),
                    'frequency_range': f"{low_freq}-{high_freq}Hz"
                }
            else:
                band_analysis[band_name] = {
                    'energy': 0.0,
                    'peak_magnitude': 0.0,
                    'average_magnitude': 0.0,
                    'frequency_range': f"{low_freq}-{high_freq}Hz"
                }
        
        return band_analysis
    
    def __del__(self):
        """Cleanup thread pool"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
