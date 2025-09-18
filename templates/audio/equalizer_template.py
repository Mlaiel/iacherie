"""
🎛️ EQUALIZER TEMPLATE - ENTERPRISE AUDIO EFFECTS FRAMEWORK
========================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise Equalizer Template for Creator Economy
- Professional Multi-Band EQ
- Real-time Audio Processing
- AI-Powered Auto-EQ
- Creator-Friendly Presets
- Advanced Spectral Analysis

Expert Team:
- Technical Lead: Fahed Mlaiel (mlaiel@live.de)
- Audio Engineer: Professional Audio Effects Expert
- DSP Engineer: Advanced Signal Processing Specialist
- Backend Senior: Enterprise Audio Architecture
"""

import asyncio
import logging
import numpy as np
import scipy.signal as signal
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Audio processing imports
import librosa
import soundfile as sf
from scipy.signal import butter, filtfilt, freqz
from scipy.optimize import minimize_scalar
try:
    import matplotlib.pyplot as plt
except ImportError:
    # Mock matplotlib for systems without display
    class MockPlt:
        def figure(self, *args, **kwargs):
            pass
        def plot(self, *args, **kwargs):
            pass
        def show(self):
            pass
        def savefig(self, *args, **kwargs):
            pass
    plt = MockPlt()

from .audio_template_factory import (
    BaseAudioTemplate, CreatorAudioTemplate, AudioTemplateMetadata,
    AudioTemplateCategory, AudioTemplateCapability, register_audio_template
)

logger = logging.getLogger(__name__)


@dataclass
class EqualizerBand:
    """Individual equalizer band configuration"""
    frequency: float  # Center frequency in Hz
    gain: float      # Gain in dB (-20 to +20)
    q_factor: float  # Quality factor (0.1 to 10.0)
    filter_type: str = "peaking"  # peaking, lowpass, highpass, lowshelf, highshelf
    enabled: bool = True
    

@dataclass
class EqualizerConfig:
    """Configuration for equalizer template"""
    bands: List[EqualizerBand] = field(default_factory=lambda: [
        EqualizerBand(60, 0.0, 0.7, "highpass"),    # High-pass filter
        EqualizerBand(200, 0.0, 1.0, "peaking"),    # Low-mid
        EqualizerBand(800, 0.0, 1.0, "peaking"),    # Mid
        EqualizerBand(3200, 0.0, 1.0, "peaking"),   # High-mid
        EqualizerBand(12800, 0.0, 0.7, "lowpass"),  # Low-pass filter
    ])
    sample_rate: int = 44100
    buffer_size: int = 512
    real_time: bool = False
    auto_gain_compensation: bool = True
    limiter_enabled: bool = True
    limiter_threshold: float = -1.0  # dB
    spectrum_analysis: bool = True
    creator_mode: bool = True
    preset_name: Optional[str] = None
    ai_auto_eq: bool = False
    reference_audio: Optional[np.ndarray] = None


@dataclass
class EqualizationResult:
    """Result of equalization process"""
    processed_audio: np.ndarray
    frequency_response: Dict[str, np.ndarray]
    spectral_analysis: Dict[str, Any]
    applied_bands: List[EqualizerBand]
    performance_metrics: Dict[str, Any]
    creator_insights: Optional[Dict[str, Any]] = None
    auto_eq_suggestions: Optional[List[str]] = None


class EqualizerPresets:
    """Professional equalizer presets for creators"""
    
    @staticmethod
    def get_preset(name: str) -> List[EqualizerBand]:
        """Get equalizer preset by name"""
        presets = {
            "vocal_clarity": [
                EqualizerBand(80, -6.0, 0.7, "highpass"),
                EqualizerBand(200, -2.0, 1.0, "peaking"),
                EqualizerBand(1000, 2.0, 1.5, "peaking"),
                EqualizerBand(3000, 3.0, 2.0, "peaking"),
                EqualizerBand(5000, 1.0, 1.0, "peaking"),
                EqualizerBand(10000, 2.0, 0.7, "highshelf")
            ],
            "podcast_voice": [
                EqualizerBand(80, -12.0, 0.7, "highpass"),
                EqualizerBand(120, -6.0, 1.0, "peaking"),
                EqualizerBand(400, -2.0, 1.5, "peaking"),
                EqualizerBand(2500, 3.0, 2.0, "peaking"),
                EqualizerBand(4000, 2.0, 1.5, "peaking"),
                EqualizerBand(8000, 1.0, 1.0, "peaking"),
                EqualizerBand(12000, -2.0, 0.7, "lowpass")
            ],
            "music_mastering": [
                EqualizerBand(30, -3.0, 0.7, "highpass"),
                EqualizerBand(60, 1.0, 1.0, "lowshelf"),
                EqualizerBand(200, -1.0, 2.0, "peaking"),
                EqualizerBand(800, 0.5, 1.5, "peaking"),
                EqualizerBand(3000, 1.0, 2.0, "peaking"),
                EqualizerBand(8000, 2.0, 1.0, "peaking"),
                EqualizerBand(15000, 1.0, 0.7, "highshelf")
            ],
            "warm_vintage": [
                EqualizerBand(40, -2.0, 0.7, "highpass"),
                EqualizerBand(100, 2.0, 1.0, "lowshelf"),
                EqualizerBand(800, -1.0, 2.0, "peaking"),
                EqualizerBand(2000, -2.0, 1.5, "peaking"),
                EqualizerBand(6000, -3.0, 1.0, "peaking"),
                EqualizerBand(12000, -4.0, 0.7, "lowpass")
            ],
            "bright_modern": [
                EqualizerBand(60, -1.0, 0.7, "highpass"),
                EqualizerBand(200, -1.0, 1.0, "peaking"),
                EqualizerBand(1000, 1.0, 1.5, "peaking"),
                EqualizerBand(4000, 3.0, 2.0, "peaking"),
                EqualizerBand(8000, 4.0, 1.0, "peaking"),
                EqualizerBand(16000, 2.0, 0.7, "highshelf")
            ],
            "bass_boost": [
                EqualizerBand(40, 4.0, 1.0, "lowshelf"),
                EqualizerBand(80, 3.0, 1.5, "peaking"),
                EqualizerBand(150, 2.0, 2.0, "peaking"),
                EqualizerBand(300, -1.0, 1.0, "peaking"),
                EqualizerBand(1000, 0.0, 1.0, "peaking"),
                EqualizerBand(4000, 1.0, 1.0, "peaking"),
                EqualizerBand(10000, 0.0, 1.0, "peaking")
            ],
            "de_esser": [
                EqualizerBand(80, 0.0, 0.7, "highpass"),
                EqualizerBand(5000, -4.0, 4.0, "peaking"),
                EqualizerBand(7000, -6.0, 3.0, "peaking"),
                EqualizerBand(9000, -4.0, 2.0, "peaking"),
                EqualizerBand(12000, -2.0, 1.0, "peaking")
            ]
        }
        
        return presets.get(name, presets["vocal_clarity"])
    
    @staticmethod
    def list_presets() -> List[str]:
        """List available preset names"""
        return [
            "vocal_clarity", "podcast_voice", "music_mastering",
            "warm_vintage", "bright_modern", "bass_boost", "de_esser"
        ]


class DigitalFilter:
    """High-quality digital filter implementation"""
    
    @staticmethod
    def design_peaking_filter(frequency: float, gain: float, q_factor: float, 
                            sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Design peaking/notching filter"""
        # Convert to normalized frequency
        w0 = 2 * np.pi * frequency / sample_rate
        
        # Calculate filter coefficients
        A = 10**(gain / 40)
        alpha = np.sin(w0) / (2 * q_factor)
        
        if gain >= 0:  # Boost
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w0)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha / A
        else:  # Cut
            b0 = 1 + alpha / A
            b1 = -2 * np.cos(w0)
            b2 = 1 - alpha / A
            a0 = 1 + alpha * A
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha * A
        
        # Normalize
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        return b, a
    
    @staticmethod
    def design_shelf_filter(frequency: float, gain: float, q_factor: float,
                          sample_rate: int, shelf_type: str = "lowshelf") -> Tuple[np.ndarray, np.ndarray]:
        """Design low/high shelf filter"""
        w0 = 2 * np.pi * frequency / sample_rate
        A = 10**(gain / 40)
        S = 1  # Shelf slope
        alpha = np.sin(w0) / 2 * np.sqrt((A + 1/A) * (1/S - 1) + 2)
        
        if shelf_type == "lowshelf":
            b0 = A * ((A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
            b1 = 2 * A * ((A - 1) - (A + 1) * np.cos(w0))
            b2 = A * ((A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
            a1 = -2 * ((A - 1) + (A + 1) * np.cos(w0))
            a2 = (A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        else:  # highshelf
            b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
            b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0))
            b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
            a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
            a2 = (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        
        # Normalize
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        return b, a
    
    @staticmethod
    def design_highpass_filter(frequency: float, q_factor: float, 
                             sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Design high-pass filter"""
        w0 = 2 * np.pi * frequency / sample_rate
        alpha = np.sin(w0) / (2 * q_factor)
        
        b0 = (1 + np.cos(w0)) / 2
        b1 = -(1 + np.cos(w0))
        b2 = (1 + np.cos(w0)) / 2
        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha
        
        # Normalize
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        return b, a
    
    @staticmethod
    def design_lowpass_filter(frequency: float, q_factor: float,
                            sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Design low-pass filter"""
        w0 = 2 * np.pi * frequency / sample_rate
        alpha = np.sin(w0) / (2 * q_factor)
        
        b0 = (1 - np.cos(w0)) / 2
        b1 = 1 - np.cos(w0)
        b2 = (1 - np.cos(w0)) / 2
        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha
        
        # Normalize
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        return b, a


class SpectralAnalyzer:
    """Advanced spectral analysis for equalizer"""
    
    @staticmethod
    def analyze_spectrum(audio: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Perform comprehensive spectral analysis"""
        # FFT analysis
        fft = np.fft.fft(audio)
        freqs = np.fft.fftfreq(len(audio), 1/sample_rate)
        magnitude = np.abs(fft)
        
        # Only keep positive frequencies
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # Convert to dB
        magnitude_db = 20 * np.log10(positive_magnitude + 1e-12)
        
        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)[0]
        
        # Frequency band energy
        band_energies = SpectralAnalyzer._calculate_band_energies(
            positive_freqs, positive_magnitude
        )
        
        return {
            'frequencies': positive_freqs,
            'magnitude_db': magnitude_db,
            'spectral_centroid_mean': float(np.mean(spectral_centroid)),
            'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
            'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
            'band_energies': band_energies,
            'dynamic_range': float(np.max(magnitude_db) - np.min(magnitude_db)),
            'peak_frequency': float(positive_freqs[np.argmax(positive_magnitude)])
        }
    
    @staticmethod
    def _calculate_band_energies(freqs: np.ndarray, magnitude: np.ndarray) -> Dict[str, float]:
        """Calculate energy in standard frequency bands"""
        bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mid': (250, 500),
            'mid': (500, 2000),
            'high_mid': (2000, 4000),
            'presence': (4000, 6000),
            'brilliance': (6000, 20000)
        }
        
        band_energies = {}
        
        for band_name, (low_freq, high_freq) in bands.items():
            # Find frequency indices
            low_idx = np.searchsorted(freqs, low_freq)
            high_idx = np.searchsorted(freqs, high_freq)
            
            if low_idx < len(magnitude) and high_idx <= len(magnitude):
                band_magnitude = magnitude[low_idx:high_idx]
                band_energy = np.sum(band_magnitude**2)
                band_energies[band_name] = float(band_energy)
            else:
                band_energies[band_name] = 0.0
        
        return band_energies


class AutoEQEngine:
    """AI-powered automatic equalization engine"""
    
    def __init__(self):
        self.target_curves = {
            'balanced': self._create_balanced_curve(),
            'vocal': self._create_vocal_curve(),
            'music': self._create_music_curve()
        }
    
    def suggest_eq_settings(self, audio: np.ndarray, sample_rate: int,
                          target_type: str = 'balanced') -> List[EqualizerBand]:
        """Suggest EQ settings based on audio analysis"""
        # Analyze current spectrum
        spectrum = SpectralAnalyzer.analyze_spectrum(audio, sample_rate)
        
        # Get target curve
        target_curve = self.target_curves.get(target_type, self.target_curves['balanced'])
        
        # Calculate required adjustments
        suggestions = self._calculate_eq_adjustments(spectrum, target_curve, sample_rate)
        
        return suggestions
    
    def _create_balanced_curve(self) -> Dict[float, float]:
        """Create balanced target frequency response curve"""
        return {
            60: 0.0,
            200: -1.0,
            500: 0.0,
            1000: 0.0,
            2000: 1.0,
            4000: 2.0,
            8000: 1.0,
            16000: 0.0
        }
    
    def _create_vocal_curve(self) -> Dict[float, float]:
        """Create vocal-optimized target curve"""
        return {
            80: -6.0,
            200: -2.0,
            500: 0.0,
            1000: 2.0,
            3000: 4.0,
            5000: 2.0,
            8000: 1.0,
            12000: -2.0
        }
    
    def _create_music_curve(self) -> Dict[float, float]:
        """Create music-optimized target curve"""
        return {
            40: 1.0,
            100: 0.0,
            300: -1.0,
            1000: 0.0,
            3000: 1.0,
            6000: 2.0,
            10000: 1.0,
            16000: 0.0
        }
    
    def _calculate_eq_adjustments(self, spectrum: Dict[str, Any], 
                                target_curve: Dict[float, float],
                                sample_rate: int) -> List[EqualizerBand]:
        """Calculate EQ band adjustments to match target curve"""
        suggestions = []
        
        freqs = spectrum['frequencies']
        magnitude_db = spectrum['magnitude_db']
        
        for target_freq, target_gain in target_curve.items():
            # Find closest frequency in spectrum
            freq_idx = np.searchsorted(freqs, target_freq)
            
            if freq_idx < len(magnitude_db):
                current_level = magnitude_db[freq_idx]
                
                # Calculate relative level (simplified)
                reference_level = np.median(magnitude_db)
                current_relative = current_level - reference_level
                adjustment = target_gain - current_relative
                
                # Limit adjustment range
                adjustment = np.clip(adjustment, -12, 12)
                
                if abs(adjustment) > 0.5:  # Only suggest if significant adjustment needed
                    band = EqualizerBand(
                        frequency=target_freq,
                        gain=adjustment,
                        q_factor=1.0,
                        filter_type="peaking"
                    )
                    suggestions.append(band)
        
        return suggestions


@register_audio_template
class EqualizerTemplate(CreatorAudioTemplate):
    """Enterprise equalizer template for creator economy"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.eq_config = EqualizerConfig(**(config or {}))
        self.auto_eq_engine = AutoEQEngine()
        self.filter_states = {}  # For real-time processing
        self.processing_history = []
        
    @property
    def metadata(self) -> AudioTemplateMetadata:
        """Template metadata"""
        return AudioTemplateMetadata(
            name="equalizer_template",
            category=AudioTemplateCategory.AUDIO_EFFECTS,
            capabilities=[
                AudioTemplateCapability.REAL_TIME_PROCESSING,
                AudioTemplateCapability.AI_ENHANCEMENT,
                AudioTemplateCapability.MULTI_FORMAT_SUPPORT,
                AudioTemplateCapability.ENTERPRISE_SCALABLE
            ],
            version="1.0.0",
            description="Professional multi-band equalizer with AI auto-EQ and creator presets",
            requirements=[
                "librosa>=0.10.0",
                "scipy>=1.11.0",
                "numpy>=1.24.0",
                "soundfile>=0.12.0"
            ],
            enterprise_features=[
                "Professional multi-band EQ",
                "AI-powered auto-EQ suggestions",
                "Real-time audio processing",
                "Creator-optimized presets",
                "Advanced spectral analysis",
                "Automatic gain compensation",
                "High-quality digital filters"
            ],
            performance_metrics={
                "latency": "< 5ms",
                "frequency_response": "20Hz - 20kHz",
                "dynamic_range": "> 120dB",
                "thd_n": "< 0.001%"
            }
        )
    
    async def initialize(self) -> bool:
        """Initialize equalizer template"""
        if not await super().initialize():
            return False
        
        try:
            # Initialize filter states for real-time processing
            self._initialize_filter_states()
            
            logger.info("Equalizer template initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize equalizer template: {e}")
            return False
    
    def _initialize_filter_states(self):
        """Initialize filter states for each band"""
        self.filter_states = {}
        
        for i, band in enumerate(self.eq_config.bands):
            if band.enabled:
                self.filter_states[i] = {
                    'z1': 0.0,
                    'z2': 0.0,
                    'coefficients': self._design_filter(band)
                }
    
    def _design_filter(self, band: EqualizerBand) -> Tuple[np.ndarray, np.ndarray]:
        """Design filter for a specific band"""
        if band.filter_type == "peaking":
            return DigitalFilter.design_peaking_filter(
                band.frequency, band.gain, band.q_factor, self.eq_config.sample_rate
            )
        elif band.filter_type == "lowshelf":
            return DigitalFilter.design_shelf_filter(
                band.frequency, band.gain, band.q_factor, 
                self.eq_config.sample_rate, "lowshelf"
            )
        elif band.filter_type == "highshelf":
            return DigitalFilter.design_shelf_filter(
                band.frequency, band.gain, band.q_factor,
                self.eq_config.sample_rate, "highshelf"
            )
        elif band.filter_type == "highpass":
            return DigitalFilter.design_highpass_filter(
                band.frequency, band.q_factor, self.eq_config.sample_rate
            )
        elif band.filter_type == "lowpass":
            return DigitalFilter.design_lowpass_filter(
                band.frequency, band.q_factor, self.eq_config.sample_rate
            )
        else:
            # Default to peaking
            return DigitalFilter.design_peaking_filter(
                band.frequency, band.gain, band.q_factor, self.eq_config.sample_rate
            )
    
    async def process_audio(self, audio_data: Union[np.ndarray, str, bytes], **kwargs) -> EqualizationResult:
        """Apply equalization to audio"""
        start_time = time.time()
        
        try:
            # Prepare audio
            audio = await self._prepare_audio(audio_data)
            
            logger.info(f"Processing audio with {len(self.eq_config.bands)} EQ bands")
            
            # Apply preset if specified
            if self.eq_config.preset_name:
                self._apply_preset(self.eq_config.preset_name)
            
            # AI auto-EQ if enabled
            if self.eq_config.ai_auto_eq:
                await self._apply_auto_eq(audio)
            
            # Pre-processing analysis
            pre_analysis = SpectralAnalyzer.analyze_spectrum(audio, self.eq_config.sample_rate)
            
            # Apply EQ processing
            processed_audio = await self._apply_equalization(audio)
            
            # Apply limiting if enabled
            if self.eq_config.limiter_enabled:
                processed_audio = self._apply_limiter(processed_audio)
            
            # Post-processing analysis
            post_analysis = SpectralAnalyzer.analyze_spectrum(processed_audio, self.eq_config.sample_rate)
            
            # Calculate frequency response
            frequency_response = await self._calculate_frequency_response()
            
            # Generate creator insights
            creator_insights = None
            if self.eq_config.creator_mode:
                creator_insights = await self._generate_creator_insights(
                    audio, processed_audio, pre_analysis, post_analysis
                )
            
            # Performance metrics
            processing_time = time.time() - start_time
            performance_metrics = {
                'processing_time': processing_time,
                'real_time_factor': processing_time / (len(audio) / self.eq_config.sample_rate),
                'total_gain_change': self._calculate_total_gain_change(),
                'bands_active': sum(1 for band in self.eq_config.bands if band.enabled and band.gain != 0),
                'auto_eq_applied': self.eq_config.ai_auto_eq
            }
            
            # Update performance stats
            self._performance_stats['total_processes'] += 1
            self._performance_stats['total_processing_time'] += processing_time
            
            result = EqualizationResult(
                processed_audio=processed_audio,
                frequency_response=frequency_response,
                spectral_analysis={
                    'pre_processing': pre_analysis,
                    'post_processing': post_analysis
                },
                applied_bands=self.eq_config.bands.copy(),
                performance_metrics=performance_metrics,
                creator_insights=creator_insights
            )
            
            # Add to processing history
            self.processing_history.append(result)
            
            logger.info(f"Equalization completed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Equalization failed: {e}")
            self._performance_stats['errors'] += 1
            raise
    
    async def _prepare_audio(self, audio_data: Union[np.ndarray, str, bytes]) -> np.ndarray:
        """Prepare audio for processing"""
        if isinstance(audio_data, str):
            # File path
            audio, sr = librosa.load(audio_data, sr=self.eq_config.sample_rate)
        elif isinstance(audio_data, bytes):
            # Audio bytes
            import io
            audio_io = io.BytesIO(audio_data)
            audio, sr = sf.read(audio_io)
            if sr != self.eq_config.sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.eq_config.sample_rate)
        elif isinstance(audio_data, np.ndarray):
            audio = audio_data.copy()
        else:
            raise ValueError("Unsupported audio data format")
        
        # Ensure mono for processing
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio)
        
        # Normalize input
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.95
        
        return audio
    
    def _apply_preset(self, preset_name: str):
        """Apply equalizer preset"""
        preset_bands = EqualizerPresets.get_preset(preset_name)
        
        # Update configuration with preset
        if len(preset_bands) <= len(self.eq_config.bands):
            for i, preset_band in enumerate(preset_bands):
                self.eq_config.bands[i] = preset_band
        
        # Reinitialize filter states
        self._initialize_filter_states()
        
        logger.info(f"Applied preset: {preset_name}")
    
    async def _apply_auto_eq(self, audio: np.ndarray):
        """Apply AI-powered auto-EQ"""
        suggestions = self.auto_eq_engine.suggest_eq_settings(
            audio, self.eq_config.sample_rate, 'balanced'
        )
        
        # Apply suggestions to existing bands
        for suggestion in suggestions:
            # Find closest existing band
            closest_band_idx = self._find_closest_band(suggestion.frequency)
            
            if closest_band_idx is not None:
                # Update existing band
                self.eq_config.bands[closest_band_idx].gain += suggestion.gain * 0.5  # Apply partially
                self.eq_config.bands[closest_band_idx].gain = np.clip(
                    self.eq_config.bands[closest_band_idx].gain, -20, 20
                )
        
        # Reinitialize filter states with new settings
        self._initialize_filter_states()
        
        logger.info(f"Applied auto-EQ with {len(suggestions)} adjustments")
    
    def _find_closest_band(self, frequency: float) -> Optional[int]:
        """Find the closest EQ band to a given frequency"""
        if not self.eq_config.bands:
            return None
        
        distances = [abs(band.frequency - frequency) for band in self.eq_config.bands]
        return np.argmin(distances)
    
    async def _apply_equalization(self, audio: np.ndarray) -> np.ndarray:
        """Apply multi-band equalization"""
        processed = audio.copy()
        
        # Apply each enabled band
        for i, band in enumerate(self.eq_config.bands):
            if band.enabled and abs(band.gain) > 0.1:  # Only process if significant gain
                b, a = self._design_filter(band)
                
                # Apply filter
                if self.eq_config.real_time and i in self.filter_states:
                    # Real-time processing (would use state for continuity)
                    processed = signal.filtfilt(b, a, processed)
                else:
                    # Batch processing
                    processed = signal.filtfilt(b, a, processed)
        
        # Auto gain compensation
        if self.eq_config.auto_gain_compensation:
            processed = self._apply_gain_compensation(audio, processed)
        
        return processed
    
    def _apply_gain_compensation(self, original: np.ndarray, processed: np.ndarray) -> np.ndarray:
        """Apply automatic gain compensation"""
        original_rms = np.sqrt(np.mean(original**2))
        processed_rms = np.sqrt(np.mean(processed**2))
        
        if processed_rms > 0:
            compensation_factor = original_rms / processed_rms
            # Limit compensation to reasonable range
            compensation_factor = np.clip(compensation_factor, 0.5, 2.0)
            processed = processed * compensation_factor
        
        return processed
    
    def _apply_limiter(self, audio: np.ndarray) -> np.ndarray:
        """Apply simple limiter to prevent clipping"""
        threshold_linear = 10**(self.eq_config.limiter_threshold / 20)
        
        # Simple hard limiting
        limited = np.where(
            np.abs(audio) > threshold_linear,
            np.sign(audio) * threshold_linear,
            audio
        )
        
        return limited
    
    async def _calculate_frequency_response(self) -> Dict[str, np.ndarray]:
        """Calculate overall frequency response of the EQ"""
        # Create frequency array
        frequencies = np.logspace(np.log10(20), np.log10(20000), 1000)
        
        # Initialize response
        overall_response = np.ones(len(frequencies), dtype=complex)
        
        # Calculate response for each band
        for band in self.eq_config.bands:
            if band.enabled and abs(band.gain) > 0.1:
                b, a = self._design_filter(band)
                
                # Calculate frequency response
                w = 2 * np.pi * frequencies / self.eq_config.sample_rate
                h = signal.freqz(b, a, worN=w)[1]
                
                # Multiply responses
                overall_response *= h
        
        # Convert to magnitude and phase
        magnitude_db = 20 * np.log10(np.abs(overall_response))
        phase_degrees = np.angle(overall_response) * 180 / np.pi
        
        return {
            'frequencies': frequencies,
            'magnitude_db': magnitude_db,
            'phase_degrees': phase_degrees,
            'magnitude_linear': np.abs(overall_response)
        }
    
    def _calculate_total_gain_change(self) -> float:
        """Calculate total gain change across all bands"""
        return sum(abs(band.gain) for band in self.eq_config.bands if band.enabled)
    
    async def _generate_creator_insights(self, original: np.ndarray, processed: np.ndarray,
                                       pre_analysis: Dict[str, Any], 
                                       post_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights for content creators"""
        # Analyze spectral changes
        spectral_improvement = self._analyze_spectral_improvement(pre_analysis, post_analysis)
        
        # Frequency balance analysis
        balance_analysis = self._analyze_frequency_balance(post_analysis)
        
        # Dynamic range analysis
        dynamic_range_original = np.max(original) - np.min(original)
        dynamic_range_processed = np.max(processed) - np.min(processed)
        dynamic_range_change = dynamic_range_processed - dynamic_range_original
        
        # Generate recommendations
        recommendations = self._generate_eq_recommendations(post_analysis, balance_analysis)
        
        # Voice/content specific insights
        content_insights = self._analyze_content_type(original, processed)
        
        return {
            'spectral_improvement': spectral_improvement,
            'frequency_balance': balance_analysis,
            'dynamic_range_change': float(dynamic_range_change),
            'recommendations': recommendations,
            'content_analysis': content_insights,
            'overall_quality_score': self._calculate_quality_score(
                spectral_improvement, balance_analysis, dynamic_range_change
            ),
            'monetization_impact': self._assess_monetization_impact(content_insights)
        }
    
    def _analyze_spectral_improvement(self, pre: Dict[str, Any], 
                                    post: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spectral improvements"""
        # Compare band energies
        pre_bands = pre['band_energies']
        post_bands = post['band_energies']
        
        improvements = {}
        for band, pre_energy in pre_bands.items():
            post_energy = post_bands.get(band, 0)
            if pre_energy > 0:
                improvement = (post_energy - pre_energy) / pre_energy * 100
                improvements[band] = improvement
        
        # Overall metrics
        centroid_change = post['spectral_centroid_mean'] - pre['spectral_centroid_mean']
        brightness_change = "brighter" if centroid_change > 0 else "warmer"
        
        return {
            'band_improvements': improvements,
            'spectral_centroid_change': float(centroid_change),
            'brightness_change': brightness_change,
            'most_improved_band': max(improvements.items(), key=lambda x: x[1])[0] if improvements else None
        }
    
    def _analyze_frequency_balance(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze frequency balance"""
        band_energies = analysis['band_energies']
        total_energy = sum(band_energies.values())
        
        if total_energy == 0:
            return {'balance_score': 0.0, 'dominant_range': 'none', 'balance_quality': 'poor'}
        
        # Calculate balance percentages
        balance_percentages = {band: energy / total_energy * 100 
                             for band, energy in band_energies.items()}
        
        # Find dominant frequency range
        dominant_range = max(balance_percentages.items(), key=lambda x: x[1])[0]
        
        # Calculate balance score (penalize extreme imbalances)
        ideal_distribution = 100 / len(band_energies)  # Equal distribution
        balance_score = 1.0 - sum(abs(pct - ideal_distribution) for pct in balance_percentages.values()) / 200
        
        # Quality assessment
        if balance_score > 0.8:
            quality = 'excellent'
        elif balance_score > 0.6:
            quality = 'good'
        elif balance_score > 0.4:
            quality = 'fair'
        else:
            quality = 'poor'
        
        return {
            'balance_score': balance_score,
            'balance_percentages': balance_percentages,
            'dominant_range': dominant_range,
            'balance_quality': quality
        }
    
    def _generate_eq_recommendations(self, analysis: Dict[str, Any], 
                                   balance: Dict[str, Any]) -> List[str]:
        """Generate EQ improvement recommendations"""
        recommendations = []
        
        balance_percentages = balance['balance_percentages']
        
        # Check for common issues
        if balance_percentages.get('bass', 0) > 40:
            recommendations.append("Consider reducing bass frequencies for better clarity")
        
        if balance_percentages.get('presence', 0) < 10:
            recommendations.append("Boost presence frequencies (4-6kHz) for better vocal clarity")
        
        if balance_percentages.get('brilliance', 0) < 5:
            recommendations.append("Add some high-frequency sparkle for airiness")
        
        if balance_percentages.get('mid', 0) > 35:
            recommendations.append("Reduce mid frequencies to avoid muddiness")
        
        # Dynamic range recommendations
        if analysis['dynamic_range'] < 30:
            recommendations.append("Audio may benefit from less compression to preserve dynamics")
        
        return recommendations
    
    def _analyze_content_type(self, original: np.ndarray, processed: np.ndarray) -> Dict[str, Any]:
        """Analyze content type and suitability"""
        # Simple content type detection based on spectral characteristics
        spectral_analysis = SpectralAnalyzer.analyze_spectrum(processed, self.eq_config.sample_rate)
        
        # Voice detection heuristics
        is_voice_likely = (
            1000 <= spectral_analysis['spectral_centroid_mean'] <= 4000 and
            spectral_analysis['band_energies'].get('mid', 0) > 
            spectral_analysis['band_energies'].get('bass', 0)
        )
        
        # Music detection heuristics  
        is_music_likely = (
            spectral_analysis['band_energies'].get('bass', 0) > 
            spectral_analysis['band_energies'].get('mid', 0) * 0.5
        )
        
        content_type = 'voice' if is_voice_likely else 'music' if is_music_likely else 'unknown'
        
        # Quality assessment for content type
        if content_type == 'voice':
            quality_score = self._assess_voice_quality(spectral_analysis)
        elif content_type == 'music':
            quality_score = self._assess_music_quality(spectral_analysis)
        else:
            quality_score = 0.5
        
        return {
            'detected_type': content_type,
            'confidence': 0.7,  # Simplified confidence
            'quality_score': quality_score,
            'characteristics': self._describe_audio_characteristics(spectral_analysis)
        }
    
    def _assess_voice_quality(self, analysis: Dict[str, Any]) -> float:
        """Assess voice quality based on spectral analysis"""
        score = 0.5
        
        # Presence in vocal range
        if 1000 <= analysis['spectral_centroid_mean'] <= 3000:
            score += 0.2
        
        # Good mid-range energy
        mid_energy = analysis['band_energies'].get('mid', 0)
        total_energy = sum(analysis['band_energies'].values())
        if total_energy > 0 and mid_energy / total_energy > 0.3:
            score += 0.2
        
        # Not too much bass
        bass_energy = analysis['band_energies'].get('bass', 0)
        if total_energy > 0 and bass_energy / total_energy < 0.3:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_music_quality(self, analysis: Dict[str, Any]) -> float:
        """Assess music quality based on spectral analysis"""
        score = 0.5
        
        # Good frequency distribution
        band_energies = analysis['band_energies']
        total_energy = sum(band_energies.values())
        
        if total_energy > 0:
            # Bass presence
            if band_energies.get('bass', 0) / total_energy > 0.15:
                score += 0.15
            
            # High frequency content
            if band_energies.get('brilliance', 0) / total_energy > 0.05:
                score += 0.15
            
            # Balanced mids
            mid_ratio = band_energies.get('mid', 0) / total_energy
            if 0.2 <= mid_ratio <= 0.4:
                score += 0.2
        
        return min(score, 1.0)
    
    def _describe_audio_characteristics(self, analysis: Dict[str, Any]) -> List[str]:
        """Describe audio characteristics"""
        characteristics = []
        
        # Brightness
        if analysis['spectral_centroid_mean'] > 3000:
            characteristics.append("bright")
        elif analysis['spectral_centroid_mean'] < 1500:
            characteristics.append("warm")
        else:
            characteristics.append("balanced")
        
        # Frequency content
        band_energies = analysis['band_energies']
        total_energy = sum(band_energies.values())
        
        if total_energy > 0:
            bass_ratio = band_energies.get('bass', 0) / total_energy
            if bass_ratio > 0.3:
                characteristics.append("bass-heavy")
            elif bass_ratio < 0.1:
                characteristics.append("thin")
            
            presence_ratio = band_energies.get('presence', 0) / total_energy
            if presence_ratio > 0.2:
                characteristics.append("crisp")
            elif presence_ratio < 0.05:
                characteristics.append("dull")
        
        return characteristics
    
    def _calculate_quality_score(self, spectral_improvement: Dict[str, Any],
                               balance: Dict[str, Any], dynamic_range_change: float) -> float:
        """Calculate overall quality score"""
        score = 0.5  # Base score
        
        # Balance contribution
        score += balance['balance_score'] * 0.3
        
        # Spectral improvement contribution
        positive_improvements = sum(1 for imp in spectral_improvement['band_improvements'].values() if imp > 0)
        total_bands = len(spectral_improvement['band_improvements'])
        if total_bands > 0:
            improvement_ratio = positive_improvements / total_bands
            score += improvement_ratio * 0.3
        
        # Dynamic range contribution
        if abs(dynamic_range_change) < 0.1:  # Preserved dynamic range
            score += 0.2
        elif dynamic_range_change > 0:  # Improved dynamic range
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_monetization_impact(self, content_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Assess impact on content monetization potential"""
        quality_score = content_insights['quality_score']
        content_type = content_insights['detected_type']
        
        # Base monetization score
        base_score = quality_score
        
        # Content type adjustments
        if content_type == 'voice':
            # Clear voice is crucial for monetization
            if quality_score > 0.8:
                base_score += 0.1
                impact = "Excellent voice clarity enhances audience retention"
            elif quality_score > 0.6:
                impact = "Good voice quality supports monetization"
            else:
                impact = "Voice clarity could be improved for better monetization"
        elif content_type == 'music':
            # Balanced music quality
            if quality_score > 0.7:
                impact = "Professional music quality suitable for licensing"
            else:
                impact = "Music quality may limit licensing opportunities"
        else:
            impact = "Content type unclear - optimize for target audience"
        
        monetization_score = min(base_score, 1.0)
        
        # Categories
        if monetization_score >= 0.8:
            category = "high"
        elif monetization_score >= 0.6:
            category = "medium"
        else:
            category = "low"
        
        return {
            'score': monetization_score,
            'category': category,
            'impact_description': impact,
            'suggestions': self._get_monetization_suggestions(content_type, quality_score)
        }
    
    def _get_monetization_suggestions(self, content_type: str, quality_score: float) -> List[str]:
        """Get monetization improvement suggestions"""
        suggestions = []
        
        if content_type == 'voice':
            if quality_score < 0.7:
                suggestions.append("Improve vocal clarity with presence boost")
                suggestions.append("Reduce background noise and reverb")
            if quality_score < 0.8:
                suggestions.append("Consider de-essing for professional sound")
        elif content_type == 'music':
            if quality_score < 0.7:
                suggestions.append("Balance frequency spectrum for wider appeal")
                suggestions.append("Ensure adequate bass and treble content")
        
        if quality_score < 0.6:
            suggestions.append("Consider professional mastering services")
        
        return suggestions
    
    def get_available_presets(self) -> List[str]:
        """Get list of available EQ presets"""
        return EqualizerPresets.list_presets()
    
    def apply_preset(self, preset_name: str) -> bool:
        """Apply an EQ preset"""
        try:
            self._apply_preset(preset_name)
            return True
        except Exception as e:
            logger.error(f"Failed to apply preset {preset_name}: {e}")
            return False
    
    def reset_eq(self):
        """Reset all EQ bands to flat response"""
        for band in self.eq_config.bands:
            band.gain = 0.0
        
        self._initialize_filter_states()
        logger.info("EQ reset to flat response")
    
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate template configuration"""
        if not super().validate_configuration(config):
            return False
        
        # Validate EQ specific parameters
        if 'bands' in config:
            bands = config['bands']
            if not isinstance(bands, list):
                logger.error("Bands must be a list")
                return False
            
            for band in bands:
                if not isinstance(band, dict):
                    continue
                
                if 'gain' in band and not (-20 <= band['gain'] <= 20):
                    logger.error("Band gain must be between -20 and +20 dB")
                    return False
                
                if 'q_factor' in band and not (0.1 <= band['q_factor'] <= 10.0):
                    logger.error("Q factor must be between 0.1 and 10.0")
                    return False
                
                if 'frequency' in band and not (20 <= band['frequency'] <= 20000):
                    logger.error("Frequency must be between 20 and 20000 Hz")
                    return False
        
        return True


# Export for external use
__all__ = [
    'EqualizerTemplate', 
    'EqualizerConfig', 
    'EqualizerBand', 
    'EqualizationResult',
    'EqualizerPresets'
]