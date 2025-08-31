"""
Spectral Analysis Configuration Module for IA-Influencer Agent Platform
======================================================================

Professional spectral analysis configuration for advanced audio processing.
Supports frequency domain analysis, spectral features extraction, and audio intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
 STRICT COPYRIGHT WARNING 
This code and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
import numpy as np
from math import pi, log2, sqrt

logger = logging.getLogger(__name__)


class WindowFunction(Enum):
    """Window functions for spectral analysis"""
    HANN = "hann"
    HAMMING = "hamming"
    BLACKMAN = "blackman"
    BARTLETT = "bartlett"
    KAISER = "kaiser"
    TUKEY = "tukey"
    GAUSSIAN = "gaussian"
    RECTANGULAR = "rectangular"


class SpectralFeatureType(Enum):
    """Types of spectral features"""
    CENTROID = "spectral_centroid"
    BANDWIDTH = "spectral_bandwidth"
    ROLLOFF = "spectral_rolloff"
    CONTRAST = "spectral_contrast"
    FLATNESS = "spectral_flatness"
    FLUX = "spectral_flux"
    KURTOSIS = "spectral_kurtosis"
    SKEWNESS = "spectral_skewness"
    ENTROPY = "spectral_entropy"
    SPREAD = "spectral_spread"
    SLOPE = "spectral_slope"
    DECREASE = "spectral_decrease"


class FrequencyScale(Enum):
    """Frequency scaling methods"""
    LINEAR = "linear"
    MEL = "mel"
    BARK = "bark"
    ERB = "erb"
    LOG = "log"
    CHROMA = "chroma"


class AnalysisMode(Enum):
    """Spectral analysis modes"""
    MAGNITUDE = "magnitude"
    POWER = "power"
    PHASE = "phase"
    COMPLEX = "complex"
    LOG_MAGNITUDE = "log_magnitude"
    DB_MAGNITUDE = "db_magnitude"


class FrequencyBandType(Enum):
    """Frequency band types"""
    OCTAVE = "octave"
    THIRD_OCTAVE = "third_octave"
    BARK = "bark"
    MEL = "mel"
    CUSTOM = "custom"


@dataclass
class SpectralParameters:
    """Core spectral analysis parameters"""
    n_fft: int = 2048
    hop_length: int = 512
    window_function: WindowFunction = WindowFunction.HANN
    window_length: Optional[int] = None
    overlap_ratio: float = 0.75
    zero_padding_factor: int = 1
    preemphasis_coefficient: float = 0.0
    center_frames: bool = True
    pad_mode: str = "constant"


@dataclass
class FrequencyAnalysisConfig:
    """Frequency domain analysis configuration"""
    min_frequency: float = 20.0
    max_frequency: float = 20000.0
    frequency_resolution: float = 10.0
    frequency_scale: FrequencyScale = FrequencyScale.LINEAR
    frequency_bins: Optional[int] = None
    logarithmic_scale: bool = False
    octave_bands: bool = False
    custom_bands: Optional[List[Tuple[float, float]]] = None


@dataclass
class MelSpectrogramConfig:
    """Mel-spectrogram specific configuration"""
    n_mels: int = 128
    fmin: float = 0.0
    fmax: Optional[float] = None
    htk: bool = False
    norm: Optional[str] = "slaney"
    mel_scale: str = "htk"


@dataclass
class ChromaConfig:
    """Chromagram analysis configuration"""
    n_chroma: int = 12
    tuning: float = 0.0
    norm: Optional[str] = "L2"
    base_c: bool = True
    chroma_mode: str = "stft"


@dataclass
class CQTConfig:
    """Constant-Q Transform configuration"""
    hop_length: int = 512
    fmin: float = 32.7  # C1
    n_bins: int = 84    # 7 octaves
    bins_per_octave: int = 12
    tuning: float = 0.0
    filter_scale: float = 1.0
    norm: Optional[str] = "L2"
    sparsity: float = 0.01


@dataclass
class SpectralFeatureConfig:
    """Spectral feature extraction configuration"""
    enabled_features: List[SpectralFeatureType] = field(default_factory=lambda: [
        SpectralFeatureType.CENTROID,
        SpectralFeatureType.BANDWIDTH,
        SpectralFeatureType.ROLLOFF,
        SpectralFeatureType.CONTRAST
    ])
    centroid_percentile: float = 0.85
    rolloff_percentile: float = 0.85
    contrast_fmin: float = 200.0
    contrast_n_bands: int = 6
    flatness_power_threshold: float = 1e-10


class SpectralAnalysisConfig:
    """
    Comprehensive spectral analysis configuration manager
    
    Manages all aspects of frequency domain audio analysis including
    STFT, mel-spectrograms, chromagrams, and spectral features.
    """
    
    def __init__(self):
        """Initialize spectral analysis configuration"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core parameters
        self.spectral_params = SpectralParameters()
        self.frequency_config = FrequencyAnalysisConfig()
        self.feature_config = SpectralFeatureConfig()
        
        # Specialized configurations
        self.mel_config = MelSpectrogramConfig()
        self.chroma_config = ChromaConfig()
        self.cqt_config = CQTConfig()
        
        # Analysis modes and strategies
        self._analysis_mode = AnalysisMode.MAGNITUDE
        self._frequency_band_type = FrequencyBandType.OCTAVE
        
        # Precomputed frequency bands
        self._frequency_bands = self._initialize_frequency_bands()
        
        # Window function coefficients cache
        self._window_cache = {}
        
        # Analysis profiles for different use cases
        self._analysis_profiles = self._initialize_analysis_profiles()
        
        self.logger.info("SpectralAnalysisConfig initialized successfully")
    
    def _initialize_frequency_bands(self) -> Dict[FrequencyBandType, List[Tuple[float, float]]]:
        """Initialize standard frequency bands"""
        bands = {}
        
        # Octave bands (ISO 266)
        octave_centers = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        octave_bands = []
        for center in octave_centers:
            lower = center / sqrt(2)
            upper = center * sqrt(2)
            octave_bands.append((lower, upper))
        bands[FrequencyBandType.OCTAVE] = octave_bands
        
        # Third-octave bands
        third_octave_centers = []
        for octave_center in [125, 250, 500, 1000, 2000, 4000, 8000]:
            third_octave_centers.extend([
                octave_center / pow(2, 1/3),
                octave_center,
                octave_center * pow(2, 1/3)
            ])
        
        third_octave_bands = []
        for center in third_octave_centers:
            lower = center / pow(2, 1/6)
            upper = center * pow(2, 1/6)
            third_octave_bands.append((lower, upper))
        bands[FrequencyBandType.THIRD_OCTAVE] = third_octave_bands
        
        # Bark bands (Zwicker & Terhardt, 1980)
        bark_bands = [
            (0, 100), (100, 200), (200, 300), (300, 400), (400, 510),
            (510, 630), (630, 770), (770, 920), (920, 1080), (1080, 1270),
            (1270, 1480), (1480, 1720), (1720, 2000), (2000, 2320), (2320, 2700),
            (2700, 3150), (3150, 3700), (3700, 4400), (4400, 5300), (5300, 6400),
            (6400, 7700), (7700, 9500), (9500, 12000), (12000, 15500)
        ]
        bands[FrequencyBandType.BARK] = bark_bands
        
        # Mel bands (approximate)
        mel_bands = []
        for i in range(40):  # 40 mel bands
            mel_low = i * 1000 / 40
            mel_high = (i + 1) * 1000 / 40
            freq_low = 700 * (pow(10, mel_low / 2595) - 1)
            freq_high = 700 * (pow(10, mel_high / 2595) - 1)
            mel_bands.append((freq_low, freq_high))
        bands[FrequencyBandType.MEL] = mel_bands
        
        return bands
    
    def _initialize_analysis_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize analysis profiles for different use cases"""



        return {
            "music_analysis": {
                "description": "Optimized for music analysis",
                "spectral_params": {
                    "n_fft": 2048,
                    "hop_length": 512,
                    "window_function": WindowFunction.HANN,
                    "overlap_ratio": 0.75
                },
                "frequency_config": {
                    "min_frequency": 20.0,
                    "max_frequency": 20000.0,
                    "frequency_scale": FrequencyScale.MEL,
                    "octave_bands": True
                },
                "features": [
                    SpectralFeatureType.CENTROID,
                    SpectralFeatureType.BANDWIDTH,
                    SpectralFeatureType.ROLLOFF,
                    SpectralFeatureType.CONTRAST,
                    SpectralFeatureType.FLATNESS
                ],
                "mel_config": {"n_mels": 128},
                "chroma_config": {"n_chroma": 12}
            },
            "speech_analysis": {
                "description": "Optimized for speech analysis",
                "spectral_params": {
                    "n_fft": 1024,
                    "hop_length": 256,
                    "window_function": WindowFunction.HAMMING,
                    "preemphasis_coefficient": 0.97
                },
                "frequency_config": {
                    "min_frequency": 80.0,
                    "max_frequency": 8000.0,
                    "frequency_scale": FrequencyScale.MEL
                },
                "features": [
                    SpectralFeatureType.CENTROID,
                    SpectralFeatureType.BANDWIDTH,
                    SpectralFeatureType.ENTROPY,
                    SpectralFeatureType.FLUX
                ],
                "mel_config": {"n_mels": 40, "fmin": 80.0, "fmax": 8000.0}
            },
            "instrument_analysis": {
                "description": "Optimized for instrument analysis",
                "spectral_params": {
                    "n_fft": 4096,
                    "hop_length": 1024,
                    "window_function": WindowFunction.BLACKMAN,
                    "zero_padding_factor": 2
                },
                "frequency_config": {
                    "min_frequency": 50.0,
                    "max_frequency": 16000.0,
                    "frequency_scale": FrequencyScale.LOG,
                    "logarithmic_scale": True
                },
                "features": [
                    SpectralFeatureType.CENTROID,
                    SpectralFeatureType.SPREAD,
                    SpectralFeatureType.SKEWNESS,
                    SpectralFeatureType.KURTOSIS,
                    SpectralFeatureType.DECREASE
                ],
                "cqt_config": {"n_bins": 96, "bins_per_octave": 12}
            },
            "real_time": {
                "description": "Optimized for real-time processing",
                "spectral_params": {
                    "n_fft": 512,
                    "hop_length": 256,
                    "window_function": WindowFunction.HANN,
                    "overlap_ratio": 0.5
                },
                "frequency_config": {
                    "min_frequency": 20.0,
                    "max_frequency": 11025.0,
                    "frequency_scale": FrequencyScale.LINEAR
                },
                "features": [
                    SpectralFeatureType.CENTROID,
                    SpectralFeatureType.ROLLOFF
                ],
                "mel_config": {"n_mels": 64}
            },
            "broadcast_analysis": {
                "description": "Optimized for broadcast content analysis",
                "spectral_params": {
                    "n_fft": 2048,
                    "hop_length": 441,  # 10ms at 44.1kHz
                    "window_function": WindowFunction.KAISER,
                    "overlap_ratio": 0.8
                },
                "frequency_config": {
                    "min_frequency": 20.0,
                    "max_frequency": 20000.0,
                    "frequency_scale": FrequencyScale.BARK,
                    "octave_bands": False
                },
                "features": [
                    SpectralFeatureType.CENTROID,
                    SpectralFeatureType.BANDWIDTH,
                    SpectralFeatureType.ROLLOFF,
                    SpectralFeatureType.CONTRAST,
                    SpectralFeatureType.FLATNESS,
                    SpectralFeatureType.ENTROPY
                ]
            }
        }
    
    def get_window_function(self, 
                           window_type: WindowFunction,
                           window_length: int,
                           **kwargs) -> np.ndarray:
        """
        Get window function coefficients with caching
        
        Args:
            window_type: Type of window function
            window_length: Length of the window
            **kwargs: Additional window parameters
            
        Returns:
            Window function coefficients
        """
        cache_key = f"{window_type.value}_{window_length}_{str(sorted(kwargs.items()))}"
        
        if cache_key in self._window_cache:
            return self._window_cache[cache_key]
        
        try:
            if window_type == WindowFunction.HANN:
                window = np.hanning(window_length)
            elif window_type == WindowFunction.HAMMING:
                window = np.hamming(window_length)
            elif window_type == WindowFunction.BLACKMAN:
                window = np.blackman(window_length)
            elif window_type == WindowFunction.BARTLETT:
                window = np.bartlett(window_length)
            elif window_type == WindowFunction.KAISER:
                beta = kwargs.get('beta', 8.6)
                window = np.kaiser(window_length, beta)
            elif window_type == WindowFunction.TUKEY:
                alpha = kwargs.get('alpha', 0.5)
                window = self._tukey_window(window_length, alpha)
            elif window_type == WindowFunction.GAUSSIAN:
                std = kwargs.get('std', window_length / 7)
                window = self._gaussian_window(window_length, std)
            elif window_type == WindowFunction.RECTANGULAR:
                window = np.ones(window_length)
            else:
                self.logger.warning(f"Unknown window type: {window_type}, using Hann")
                window = np.hanning(window_length)
            
            # Cache the result
            self._window_cache[cache_key] = window
            return window
            
        except Exception as e:
            self.logger.error(f"Window function generation failed: {e}")
            return np.hanning(window_length)
    
    def _tukey_window(self, window_length: int, alpha: float) -> np.ndarray:
        """Generate Tukey (tapered cosine) window"""
        if alpha >= 1.0:
            return np.hanning(window_length)
        elif alpha <= 0.0:
            return np.ones(window_length)
        
        n = np.arange(window_length)
        width = int(alpha * (window_length - 1) / 2)
        
        window = np.ones(window_length)
        
        # Left taper
        left_indices = n[:width + 1]
        window[:width + 1] = 0.5 * (1 + np.cos(pi * (2 * left_indices / alpha / (window_length - 1) - 1)))
        
        # Right taper
        right_indices = n[window_length - width - 1:]
        window[window_length - width - 1:] = 0.5 * (1 + np.cos(pi * (2 * (window_length - 1 - right_indices) / alpha / (window_length - 1) - 1)))
        
        return window
    
    def _gaussian_window(self, window_length: int, std: float) -> np.ndarray:
        """Generate Gaussian window"""
        n = np.arange(window_length) - (window_length - 1) / 2
        return np.exp(-0.5 * (n / std) ** 2)
    
    def get_frequency_bands(self, band_type: FrequencyBandType) -> List[Tuple[float, float]]:
        """
        Get frequency bands for specified type
        
        Args:
            band_type: Type of frequency bands
            
        Returns:
            List of (lower_freq, upper_freq) tuples
        """



        return self._frequency_bands.get(band_type, [])
    
    def create_custom_frequency_bands(self, 
                                    min_freq: float,
                                    max_freq: float,
                                    num_bands: int,
                                    scale: FrequencyScale = FrequencyScale.LINEAR) -> List[Tuple[float, float]]:
        """
        Create custom frequency bands
        
        Args:
            min_freq: Minimum frequency
            max_freq: Maximum frequency
            num_bands: Number of frequency bands
            scale: Frequency scaling
            
        Returns:
            List of frequency bands
        """



        try:
            if scale == FrequencyScale.LINEAR:
                frequencies = np.linspace(min_freq, max_freq, num_bands + 1)
            elif scale == FrequencyScale.LOG:
                log_min = np.log10(max(min_freq, 1.0))
                log_max = np.log10(max_freq)
                frequencies = np.logspace(log_min, log_max, num_bands + 1)
            elif scale == FrequencyScale.MEL:
                mel_min = self._hz_to_mel(min_freq)
                mel_max = self._hz_to_mel(max_freq)
                mel_freqs = np.linspace(mel_min, mel_max, num_bands + 1)
                frequencies = self._mel_to_hz(mel_freqs)
            elif scale == FrequencyScale.BARK:
                bark_min = self._hz_to_bark(min_freq)
                bark_max = self._hz_to_bark(max_freq)
                bark_freqs = np.linspace(bark_min, bark_max, num_bands + 1)
                frequencies = self._bark_to_hz(bark_freqs)
            else:
                frequencies = np.linspace(min_freq, max_freq, num_bands + 1)
            
            bands = []
            for i in range(num_bands):
                bands.append((frequencies[i], frequencies[i + 1]))
            
            return bands
            
        except Exception as e:
            self.logger.error(f"Custom band creation failed: {e}")
            return [(min_freq, max_freq)]
    
    def _hz_to_mel(self, hz: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert frequency in Hz to mel scale"""



        return 2595.0 * np.log10(1.0 + hz / 700.0)
    
    def _mel_to_hz(self, mel: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert mel scale to frequency in Hz"""



        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)
    
    def _hz_to_bark(self, hz: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert frequency in Hz to Bark scale"""



        return 13.0 * np.arctan(0.00076 * hz) + 3.5 * np.arctan((hz / 7500.0) ** 2)
    
    def _bark_to_hz(self, bark: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert Bark scale to frequency in Hz (approximation)"""



        return 600.0 * np.sinh(bark / 4.0)
    
    def get_analysis_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Get predefined analysis profile
        
        Args:
            profile_name: Name of the analysis profile
            
        Returns:
            Analysis profile configuration
        """



        return self._analysis_profiles.get(profile_name, {})
    
    def apply_analysis_profile(self, profile_name: str) -> bool:
        """
        Apply predefined analysis profile
        
        Args:
            profile_name: Name of the analysis profile
            
        Returns:
            Success status
        """



        try:
            profile = self.get_analysis_profile(profile_name)
            if not profile:
                self.logger.error(f"Unknown analysis profile: {profile_name}")
                return False
            
            # Apply spectral parameters
            if "spectral_params" in profile:
                params = profile["spectral_params"]
                for key, value in params.items():
                    if key == "window_function" and isinstance(value, str):
                        value = WindowFunction(value)
                    if hasattr(self.spectral_params, key):
                        setattr(self.spectral_params, key, value)
            
            # Apply frequency configuration
            if "frequency_config" in profile:
                freq_config = profile["frequency_config"]
                for key, value in freq_config.items():
                    if key == "frequency_scale" and isinstance(value, str):
                        value = FrequencyScale(value)
                    if hasattr(self.frequency_config, key):
                        setattr(self.frequency_config, key, value)
            
            # Apply feature configuration
            if "features" in profile:
                features = profile["features"]
                if isinstance(features[0], str):
                    features = [SpectralFeatureType(f) for f in features]
                self.feature_config.enabled_features = features
            
            # Apply specialized configurations
            if "mel_config" in profile:
                for key, value in profile["mel_config"].items():
                    if hasattr(self.mel_config, key):
                        setattr(self.mel_config, key, value)
            
            if "chroma_config" in profile:
                for key, value in profile["chroma_config"].items():
                    if hasattr(self.chroma_config, key):
                        setattr(self.chroma_config, key, value)
            
            if "cqt_config" in profile:
                for key, value in profile["cqt_config"].items():
                    if hasattr(self.cqt_config, key):
                        setattr(self.cqt_config, key, value)
            
            self.logger.info(f"Applied analysis profile: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply analysis profile: {e}")
            return False
    
    def calculate_optimal_parameters(self, 
                                   sample_rate: int,
                                   target_frequency_resolution: Optional[float] = None,
                                   target_time_resolution: Optional[float] = None,
                                   min_frequency: float = 20.0,
                                   max_frequency: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculate optimal analysis parameters based on requirements
        
        Args:
            sample_rate: Audio sample rate
            target_frequency_resolution: Target frequency resolution in Hz
            target_time_resolution: Target time resolution in seconds
            min_frequency: Minimum frequency of interest
            max_frequency: Maximum frequency of interest
            
        Returns:
            Optimal parameters
        """



        try:
            if max_frequency is None:
                max_frequency = sample_rate / 2
            
            # Calculate optimal FFT size
            if target_frequency_resolution:
                n_fft = int(2 ** np.ceil(np.log2(sample_rate / target_frequency_resolution)))
            elif target_time_resolution:
                n_fft = int(2 ** np.ceil(np.log2(sample_rate * target_time_resolution)))
            else:
                # Default based on frequency range
                frequency_range = max_frequency - min_frequency
                n_fft = max(512, int(2 ** np.ceil(np.log2(sample_rate / (frequency_range / 100)))))
            
            # Limit FFT size to reasonable bounds
            n_fft = max(256, min(n_fft, 16384))
            
            # Calculate hop length for desired overlap
            overlap_ratio = 0.75
            hop_length = int(n_fft * (1 - overlap_ratio))
            
            # Ensure hop length is power of 2 or has small prime factors
            hop_length = self._optimize_hop_length(hop_length)
            
            # Calculate actual resolutions
            frequency_resolution = sample_rate / n_fft
            time_resolution = hop_length / sample_rate
            
            # Recommend window function based on use case
            if target_frequency_resolution and target_frequency_resolution < 10:
                window_function = WindowFunction.BLACKMAN  # Better frequency resolution
            elif target_time_resolution and target_time_resolution < 0.01:
                window_function = WindowFunction.HANN  # Good time-frequency tradeoff
            else:
                window_function = WindowFunction.HANN  # Default
            
            return {
                "recommended_n_fft": n_fft,
                "recommended_hop_length": hop_length,
                "recommended_window": window_function,
                "actual_frequency_resolution": frequency_resolution,
                "actual_time_resolution": time_resolution,
                "frequency_bins": n_fft // 2 + 1,
                "nyquist_frequency": sample_rate / 2,
                "analysis_bandwidth": max_frequency - min_frequency,
                "memory_estimate_mb": self._estimate_memory_usage(n_fft, hop_length, sample_rate)
            }
            
        except Exception as e:
            self.logger.error(f"Parameter optimization failed: {e}")
            return {"error": str(e)}
    
    def _optimize_hop_length(self, hop_length: int) -> int:
        """Optimize hop length for efficient processing"""
        # Prefer powers of 2 or products of small primes
        candidates = []
        
        # Powers of 2
        for power in range(6, 12):  # 64 to 2048
            candidates.append(2 ** power)
        
        # Products of small primes
        for a in [1, 2, 3, 4, 5, 6, 8]:
            for b in [1, 3, 5, 7, 9, 11]:
                for c in [1, 2, 4, 8]:
                    candidate = a * b * c * 8  # Base factor of 8
                    if 64 <= candidate <= 2048:
                        candidates.append(candidate)
        
        # Find closest candidate
        candidates = sorted(set(candidates))
        closest = min(candidates, key=lambda x: abs(x - hop_length))
        
        return closest
    
    def _estimate_memory_usage(self, n_fft: int, hop_length: int, sample_rate: int) -> float:
        """Estimate memory usage for spectral analysis"""
        # Complex FFT output: n_fft/2 + 1 complex values
        fft_memory = (n_fft // 2 + 1) * 8 * 2  # 8 bytes per float, complex
        
        # Window function
        window_memory = n_fft * 8
        
        # Input buffer
        buffer_memory = n_fft * 8
        
        # Processing buffers (3x for safety)
        processing_memory = (fft_memory + window_memory + buffer_memory) * 3
        
        # Convert to MB
        total_memory_mb = processing_memory / (1024 * 1024)
        
        return round(total_memory_mb, 2)
    
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """
        Validate current spectral analysis parameters
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        is_valid = True
        
        try:
            # Validate FFT size
            if self.spectral_params.n_fft <= 0 or (self.spectral_params.n_fft & (self.spectral_params.n_fft - 1)) != 0:
                if self.spectral_params.n_fft <= 0:
                    errors.append("n_fft must be positive")
                else:
                    errors.append("n_fft should be a power of 2 for optimal performance")
                is_valid = False
            
            # Validate hop length
            if self.spectral_params.hop_length <= 0:
                errors.append("hop_length must be positive")
                is_valid = False
            elif self.spectral_params.hop_length >= self.spectral_params.n_fft:
                errors.append("hop_length should be less than n_fft")
                is_valid = False
            
            # Validate overlap ratio
            if not (0.0 <= self.spectral_params.overlap_ratio <= 1.0):
                errors.append("overlap_ratio must be between 0 and 1")
                is_valid = False
            
            # Validate frequency range
            if self.frequency_config.min_frequency >= self.frequency_config.max_frequency:
                errors.append("min_frequency must be less than max_frequency")
                is_valid = False
            
            if self.frequency_config.min_frequency < 0:
                errors.append("min_frequency cannot be negative")
                is_valid = False
            
            # Validate mel configuration
            if self.mel_config.n_mels <= 0:
                errors.append("n_mels must be positive")
                is_valid = False
            
            if self.mel_config.fmin < 0:
                errors.append("mel fmin cannot be negative")
                is_valid = False
            
            # Validate chroma configuration
            if self.chroma_config.n_chroma <= 0 or self.chroma_config.n_chroma > 24:
                errors.append("n_chroma must be between 1 and 24")
                is_valid = False
            
            # Validate CQT configuration
            if self.cqt_config.bins_per_octave <= 0:
                errors.append("bins_per_octave must be positive")
                is_valid = False
            
            if self.cqt_config.fmin <= 0:
                errors.append("CQT fmin must be positive")
                is_valid = False
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            is_valid = False
        
        return is_valid, errors
    
    def get_feature_extraction_config(self) -> Dict[str, Any]:
        """
        Get configuration for spectral feature extraction
        
        Returns:
            Feature extraction configuration
        """



        return {
            "enabled_features": [feature.value for feature in self.feature_config.enabled_features],
            "centroid_percentile": self.feature_config.centroid_percentile,
            "rolloff_percentile": self.feature_config.rolloff_percentile,
            "contrast_fmin": self.feature_config.contrast_fmin,
            "contrast_n_bands": self.feature_config.contrast_n_bands,
            "flatness_power_threshold": self.feature_config.flatness_power_threshold,
            "spectral_params": {
                "n_fft": self.spectral_params.n_fft,
                "hop_length": self.spectral_params.hop_length,
                "window_function": self.spectral_params.window_function.value,
                "window_length": self.spectral_params.window_length or self.spectral_params.n_fft
            }
        }
    
    def create_analysis_config(self, 
                             use_case: str,
                             sample_rate: int,
                             performance_priority: bool = False) -> Dict[str, Any]:
        """
        Create complete spectral analysis configuration
        
        Args:
            use_case: Analysis use case
            sample_rate: Audio sample rate
            performance_priority: Prioritize performance over quality
            
        Returns:
            Complete analysis configuration
        """



        try:
            # Apply appropriate profile
            if use_case in self._analysis_profiles:
                self.apply_analysis_profile(use_case)
            elif "music" in use_case.lower():
                self.apply_analysis_profile("music_analysis")
            elif "speech" in use_case.lower():
                self.apply_analysis_profile("speech_analysis")
            elif "real" in use_case.lower() and "time" in use_case.lower():
                self.apply_analysis_profile("real_time")
            else:
                self.apply_analysis_profile("music_analysis")  # Default
            
            # Adjust for performance priority
            if performance_priority:
                self.spectral_params.n_fft = min(self.spectral_params.n_fft, 1024)
                self.spectral_params.hop_length = max(self.spectral_params.hop_length, 256)
                self.mel_config.n_mels = min(self.mel_config.n_mels, 64)
            
            # Calculate optimal parameters
            optimal_params = self.calculate_optimal_parameters(
                sample_rate,
                min_frequency=self.frequency_config.min_frequency,
                max_frequency=self.frequency_config.max_frequency
            )
            
            return {
                "use_case": use_case,
                "sample_rate": sample_rate,
                "spectral_params": {
                    "n_fft": self.spectral_params.n_fft,
                    "hop_length": self.spectral_params.hop_length,
                    "window_function": self.spectral_params.window_function.value,
                    "window_length": self.spectral_params.window_length,
                    "overlap_ratio": self.spectral_params.overlap_ratio,
                    "zero_padding_factor": self.spectral_params.zero_padding_factor,
                    "preemphasis_coefficient": self.spectral_params.preemphasis_coefficient
                },
                "frequency_config": {
                    "min_frequency": self.frequency_config.min_frequency,
                    "max_frequency": self.frequency_config.max_frequency,
                    "frequency_scale": self.frequency_config.frequency_scale.value,
                    "frequency_bins": optimal_params.get("frequency_bins", 1025),
                    "frequency_resolution": optimal_params.get("actual_frequency_resolution", 21.5)
                },
                "mel_config": {
                    "n_mels": self.mel_config.n_mels,
                    "fmin": self.mel_config.fmin,
                    "fmax": self.mel_config.fmax or sample_rate / 2,
                    "norm": self.mel_config.norm
                },
                "chroma_config": {
                    "n_chroma": self.chroma_config.n_chroma,
                    "tuning": self.chroma_config.tuning,
                    "norm": self.chroma_config.norm
                },
                "cqt_config": {
                    "hop_length": self.cqt_config.hop_length,
                    "fmin": self.cqt_config.fmin,
                    "n_bins": self.cqt_config.n_bins,
                    "bins_per_octave": self.cqt_config.bins_per_octave
                },
                "feature_config": self.get_feature_extraction_config(),
                "analysis_mode": self._analysis_mode.value,
                "frequency_band_type": self._frequency_band_type.value,
                "optimal_params": optimal_params
            }
            
        except Exception as e:
            self.logger.error(f"Analysis config creation failed: {e}")
            return {"error": str(e)}
    
    def export_config(self) -> Dict[str, Any]:
        """Export complete spectral analysis configuration"""



        try:
            return {
                "spectral_params": {
                    "n_fft": self.spectral_params.n_fft,
                    "hop_length": self.spectral_params.hop_length,
                    "window_function": self.spectral_params.window_function.value,
                    "window_length": self.spectral_params.window_length,
                    "overlap_ratio": self.spectral_params.overlap_ratio,
                    "zero_padding_factor": self.spectral_params.zero_padding_factor,
                    "preemphasis_coefficient": self.spectral_params.preemphasis_coefficient,
                    "center_frames": self.spectral_params.center_frames,
                    "pad_mode": self.spectral_params.pad_mode
                },
                "frequency_config": {
                    "min_frequency": self.frequency_config.min_frequency,
                    "max_frequency": self.frequency_config.max_frequency,
                    "frequency_resolution": self.frequency_config.frequency_resolution,
                    "frequency_scale": self.frequency_config.frequency_scale.value,
                    "frequency_bins": self.frequency_config.frequency_bins,
                    "logarithmic_scale": self.frequency_config.logarithmic_scale,
                    "octave_bands": self.frequency_config.octave_bands
                },
                "mel_config": {
                    "n_mels": self.mel_config.n_mels,
                    "fmin": self.mel_config.fmin,
                    "fmax": self.mel_config.fmax,
                    "htk": self.mel_config.htk,
                    "norm": self.mel_config.norm,
                    "mel_scale": self.mel_config.mel_scale
                },
                "chroma_config": {
                    "n_chroma": self.chroma_config.n_chroma,
                    "tuning": self.chroma_config.tuning,
                    "norm": self.chroma_config.norm,
                    "base_c": self.chroma_config.base_c,
                    "chroma_mode": self.chroma_config.chroma_mode
                },
                "cqt_config": {
                    "hop_length": self.cqt_config.hop_length,
                    "fmin": self.cqt_config.fmin,
                    "n_bins": self.cqt_config.n_bins,
                    "bins_per_octave": self.cqt_config.bins_per_octave,
                    "tuning": self.cqt_config.tuning,
                    "filter_scale": self.cqt_config.filter_scale,
                    "norm": self.cqt_config.norm,
                    "sparsity": self.cqt_config.sparsity
                },
                "feature_config": {
                    "enabled_features": [feature.value for feature in self.feature_config.enabled_features],
                    "centroid_percentile": self.feature_config.centroid_percentile,
                    "rolloff_percentile": self.feature_config.rolloff_percentile,
                    "contrast_fmin": self.feature_config.contrast_fmin,
                    "contrast_n_bands": self.feature_config.contrast_n_bands,
                    "flatness_power_threshold": self.feature_config.flatness_power_threshold
                },
                "analysis_mode": self._analysis_mode.value,
                "frequency_band_type": self._frequency_band_type.value,
                "analysis_profiles": self._analysis_profiles
            }
        except Exception as e:
            self.logger.error(f"Config export failed: {e}")
            return {}
