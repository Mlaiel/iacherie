"""Audio Enhancement - Advanced Audio Enhancement and Processing
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive audio enhancement capabilities.
"""import logging
import numpy as np
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EnhancementType(Enum):
    """Types of audio enhancement"""    NOISE_REDUCTION = "noise_reduction"
    DYNAMIC_RANGE = "dynamic_range"
    SPECTRAL_ENHANCE = "spectral_enhance"
    VOCAL_ENHANCE = "vocal_enhance"
    BASS_BOOST = "bass_boost"
    TREBLE_BOOST = "treble_boost"
    STEREO_WIDENING = "stereo_widening"
    HARMONIC_ENHANCE = "harmonic_enhance"
    CLARITY_BOOST = "clarity_boost"
    WARMTH_ENHANCE = "warmth_enhance"

class QualityLevel(Enum):
    """Enhancement quality levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class EnhancementSettings:
    """Enhancement configuration"""    enhancement_type: EnhancementType
    strength: float = 0.5  # 0.0 to 1.0
    quality_level: QualityLevel = QualityLevel.MEDIUM
    preserve_dynamics: bool = True
    auto_gain: bool = True
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnhancementResult:
    """Audio enhancement result"""    enhanced_audio: np.ndarray
    original_audio: np.ndarray
    settings_used: EnhancementSettings
    processing_time: float
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    enhancement_gain_db: float = 0.0
    frequency_response: Optional[Dict[str, float]] = None
    success: bool = True
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

class AudioEnhancer:
    """Advanced audio enhancement engine"""    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Enhancement parameters
        self.frame_size = 2048
        self.hop_length = 512
        self.overlap_ratio = 0.75
        
        # Quality presets
        self.quality_presets = {
            QualityLevel.LOW: {'fft_size': 1024, 'precision': 'float32'},
            QualityLevel.MEDIUM: {'fft_size': 2048, 'precision': 'float64'},
            QualityLevel.HIGH: {'fft_size': 4096, 'precision': 'float64'},
            QualityLevel.ULTRA: {'fft_size': 8192, 'precision': 'float64'}
        }
        
        self.logger.info("AudioEnhancer initialized successfully")
    
    def enhance(self, audio_data: np.ndarray, settings: EnhancementSettings) -> EnhancementResult:
        """Enhance audio with specified settings"""        start_time = time.time()
        
        try:
            original_audio = audio_data.copy()
            
            # Route to specific enhancement method
            if settings.enhancement_type == EnhancementType.NOISE_REDUCTION:
                enhanced_audio = self._reduce_noise(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.DYNAMIC_RANGE:
                enhanced_audio = self._enhance_dynamics(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.SPECTRAL_ENHANCE:
                enhanced_audio = self._enhance_spectrum(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.VOCAL_ENHANCE:
                enhanced_audio = self._enhance_vocals(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.BASS_BOOST:
                enhanced_audio = self._boost_bass(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.TREBLE_BOOST:
                enhanced_audio = self._boost_treble(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.STEREO_WIDENING:
                enhanced_audio = self._widen_stereo(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.HARMONIC_ENHANCE:
                enhanced_audio = self._enhance_harmonics(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.CLARITY_BOOST:
                enhanced_audio = self._boost_clarity(audio_data, settings)
            elif settings.enhancement_type == EnhancementType.WARMTH_ENHANCE:
                enhanced_audio = self._enhance_warmth(audio_data, settings)
            else:
                enhanced_audio = audio_data
            
            # Apply auto-gain if enabled
            if settings.auto_gain:
                enhanced_audio = self._apply_auto_gain(enhanced_audio, original_audio)
            
            # Ensure no clipping
            enhanced_audio = self._prevent_clipping(enhanced_audio)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(original_audio, enhanced_audio)
            
            # Calculate enhancement gain
            gain_db = self._calculate_enhancement_gain(original_audio, enhanced_audio)
            
            # Analyze frequency response
            freq_response = self._analyze_frequency_response(original_audio, enhanced_audio)
            
            processing_time = time.time() - start_time
            
            result = EnhancementResult(
                enhanced_audio=enhanced_audio,
                original_audio=original_audio,
                settings_used=settings,
                processing_time=processing_time,
                quality_metrics=quality_metrics,
                enhancement_gain_db=gain_db,
                frequency_response=freq_response,
                success=True,
                warnings=[]
            )
            
            # Check for potential issues
            self._check_enhancement_quality(result)
            
            self.logger.info(f"Audio enhancement completed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Audio enhancement failed: {e}")
            return EnhancementResult(
                enhanced_audio=audio_data,
                original_audio=audio_data,
                settings_used=settings,
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def _reduce_noise(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Reduce noise using spectral subtraction technique"""        try:
            strength = settings.strength
            
            # Simple noise reduction: spectral subtraction approach
            # In real implementation, would use more sophisticated algorithms
            
            # Apply gentle low-pass filtering for noise reduction
            # This is a simplified approach
            
            # Calculate noise floor (estimate from quieter sections)
            noise_floor = np.percentile(np.abs(audio_data), 10) * strength
            
            # Reduce components below noise floor
            enhanced = np.where(np.abs(audio_data) < noise_floor, 
                              audio_data * (1 - strength * 0.5), 
                              audio_data)
            
            return enhanced.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Noise reduction failed: {e}")
            return audio_data
    
    def _enhance_dynamics(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Enhance dynamic range"""        try:
            strength = settings.strength
            
            # Multi-band dynamic range enhancement
            # Expand quiet passages, compress loud passages
            
            # Calculate RMS and peak values
            rms = np.sqrt(np.mean(audio_data ** 2))
            peak = np.max(np.abs(audio_data))
            
            if rms == 0 or peak == 0:
                return audio_data
            
            # Dynamic range expansion for quiet signals
            threshold = rms * 0.5
            expansion_ratio = 1.0 + strength * 0.5
            
            enhanced = np.where(np.abs(audio_data) < threshold,
                              np.sign(audio_data) * (np.abs(audio_data) ** expansion_ratio),
                              audio_data)
            
            # Gentle compression for loud signals
            compression_threshold = peak * 0.8
            compression_ratio = 1.0 - strength * 0.2
            
            enhanced = np.where(np.abs(enhanced) > compression_threshold,
                              np.sign(enhanced) * (compression_threshold + 
                                                 (np.abs(enhanced) - compression_threshold) * compression_ratio),
                              enhanced)
            
            return enhanced.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Dynamic range enhancement failed: {e}")
            return audio_data
    
    def _enhance_spectrum(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Enhance spectral content"""        try:
            strength = settings.strength
            
            # FFT-based spectral enhancement
            fft_size = self.quality_presets[settings.quality_level]['fft_size']
            
            # Perform FFT
            fft_data = np.fft.fft(audio_data, n=fft_size)
            magnitude = np.abs(fft_data)
            phase = np.angle(fft_data)
            
            # Enhance spectral peaks
            # Find prominent frequencies and boost them slightly
            median_magnitude = np.median(magnitude)
            enhancement_factor = 1.0 + strength * 0.3
            
            enhanced_magnitude = np.where(magnitude > median_magnitude * 1.5,
                                        magnitude * enhancement_factor,
                                        magnitude)
            
            # Reconstruct signal
            enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_audio = np.real(np.fft.ifft(enhanced_fft))[:len(audio_data)]
            
            return enhanced_audio.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Spectral enhancement failed: {e}")
            return audio_data
    
    def _enhance_vocals(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Enhance vocal frequencies"""        try:
            strength = settings.strength
            
            # Vocal frequency range enhancement (roughly 300Hz - 3kHz)
            # This is a simplified implementation
            
            # Apply gentle boost to mid frequencies
            vocal_boost = 1.0 + strength * 0.4
            
            # Simple frequency-domain processing
            fft_data = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
            
            # Create vocal frequency mask
            vocal_mask = (np.abs(freqs) >= 300) & (np.abs(freqs) <= 3000)
            
            # Apply boost to vocal frequencies
            enhanced_fft = fft_data.copy()
            enhanced_fft[vocal_mask] *= vocal_boost
            
            enhanced_audio = np.real(np.fft.ifft(enhanced_fft))
            
            return enhanced_audio.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Vocal enhancement failed: {e}")
            return audio_data
    
    def _boost_bass(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Boost bass frequencies"""        try:
            strength = settings.strength
            bass_boost = 1.0 + strength * 0.6
            
            # Bass frequency range (roughly 20Hz - 250Hz)
            fft_data = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
            
            # Create bass frequency mask
            bass_mask = (np.abs(freqs) >= 20) & (np.abs(freqs) <= 250)
            
            # Apply bass boost
            enhanced_fft = fft_data.copy()
            enhanced_fft[bass_mask] *= bass_boost
            
            enhanced_audio = np.real(np.fft.ifft(enhanced_fft))
            
            return enhanced_audio.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Bass boost failed: {e}")
            return audio_data
    
    def _boost_treble(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Boost treble frequencies"""        try:
            strength = settings.strength
            treble_boost = 1.0 + strength * 0.5
            
            # Treble frequency range (roughly 4kHz - 20kHz)
            fft_data = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
            
            # Create treble frequency mask
            treble_mask = (np.abs(freqs) >= 4000) & (np.abs(freqs) <= 20000)
            
            # Apply treble boost
            enhanced_fft = fft_data.copy()
            enhanced_fft[treble_mask] *= treble_boost
            
            enhanced_audio = np.real(np.fft.ifft(enhanced_fft))
            
            return enhanced_audio.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Treble boost failed: {e}")
            return audio_data
    
    def _widen_stereo(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Widen stereo image (for stereo audio)"""        try:
            # For mono audio, just return original
            if len(audio_data.shape) == 1:
                return audio_data
            
            strength = settings.strength
            
            # Stereo widening using mid-side processing
            if audio_data.shape[1] >= 2:  # Stereo
                left = audio_data[:, 0]
                right = audio_data[:, 1]
                
                # Convert to mid-side
                mid = (left + right) / 2
                side = (left - right) / 2
                
                # Enhance side signal for widening
                enhanced_side = side * (1.0 + strength)
                
                # Convert back to left-right
                enhanced_left = mid + enhanced_side
                enhanced_right = mid - enhanced_side
                
                enhanced_audio = np.column_stack((enhanced_left, enhanced_right))
                return enhanced_audio.astype(audio_data.dtype)
            
            return audio_data
            
        except Exception as e:
            self.logger.error(f"Stereo widening failed: {e}")
            return audio_data
    
    def _enhance_harmonics(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Enhance harmonic content"""        try:
            strength = settings.strength
            
            # Harmonic enhancement using gentle saturation
            # Add subtle harmonic distortion
            
            # Soft clipping/saturation
            drive = strength * 2.0
            enhanced = np.tanh(audio_data * drive) / drive if drive > 0 else audio_data
            
            # Mix with original
            mix_ratio = 0.3 * strength
            enhanced_audio = audio_data * (1 - mix_ratio) + enhanced * mix_ratio
            
            return enhanced_audio.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Harmonic enhancement failed: {e}")
            return audio_data
    
    def _boost_clarity(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Boost audio clarity"""        try:
            strength = settings.strength
            
            # Clarity boost through mid-frequency enhancement
            # and gentle high-frequency emphasis
            
            fft_data = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
            
            # Boost presence frequencies (1kHz - 8kHz)
            presence_mask = (np.abs(freqs) >= 1000) & (np.abs(freqs) <= 8000)
            clarity_boost = 1.0 + strength * 0.3
            
            enhanced_fft = fft_data.copy()
            enhanced_fft[presence_mask] *= clarity_boost
            
            enhanced_audio = np.real(np.fft.ifft(enhanced_fft))
            
            return enhanced_audio.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Clarity boost failed: {e}")
            return audio_data
    
    def _enhance_warmth(self, audio_data: np.ndarray, settings: EnhancementSettings) -> np.ndarray:
        """Enhance warmth (analog-like character)"""        try:
            strength = settings.strength
            
            # Warmth enhancement through:
            # 1. Gentle low-mid boost
            # 2. Subtle harmonic saturation
            # 3. Soft high-frequency roll-off
            
            fft_data = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
            
            # Low-mid boost (200Hz - 2kHz)
            warmth_mask = (np.abs(freqs) >= 200) & (np.abs(freqs) <= 2000)
            warmth_boost = 1.0 + strength * 0.25
            
            # High-frequency gentle roll-off (above 10kHz)
            rolloff_mask = np.abs(freqs) > 10000
            rolloff_factor = 1.0 - strength * 0.15
            
            enhanced_fft = fft_data.copy()
            enhanced_fft[warmth_mask] *= warmth_boost
            enhanced_fft[rolloff_mask] *= rolloff_factor
            
            enhanced_audio = np.real(np.fft.ifft(enhanced_fft))
            
            # Add subtle saturation
            saturation = strength * 0.1
            if saturation > 0:
                enhanced_audio = np.tanh(enhanced_audio * (1 + saturation)) / (1 + saturation)
            
            return enhanced_audio.astype(audio_data.dtype)
            
        except Exception as e:
            self.logger.error(f"Warmth enhancement failed: {e}")
            return audio_data
    
    def _apply_auto_gain(self, enhanced_audio: np.ndarray, original_audio: np.ndarray) -> np.ndarray:
        """Apply automatic gain compensation"""        try:
            original_rms = np.sqrt(np.mean(original_audio ** 2))
            enhanced_rms = np.sqrt(np.mean(enhanced_audio ** 2))
            
            if enhanced_rms > 0 and original_rms > 0:
                gain_compensation = original_rms / enhanced_rms
                # Limit gain compensation to reasonable range
                gain_compensation = np.clip(gain_compensation, 0.5, 2.0)
                return enhanced_audio * gain_compensation
            
            return enhanced_audio
            
        except Exception as e:
            self.logger.error(f"Auto-gain failed: {e}")
            return enhanced_audio
    
    def _prevent_clipping(self, audio_data: np.ndarray) -> np.ndarray:
        """Prevent digital clipping"""        try:
            max_val = np.max(np.abs(audio_data))
            if max_val > 0.95:  # Leave some headroom
                return audio_data * (0.95 / max_val)
            return audio_data
            
        except Exception:
            return audio_data
    
    def _calculate_quality_metrics(self, original: np.ndarray, enhanced: np.ndarray) -> Dict[str, float]:
        """Calculate enhancement quality metrics"""        try:
            metrics = {}
            
            # RMS levels
            original_rms = np.sqrt(np.mean(original ** 2))
            enhanced_rms = np.sqrt(np.mean(enhanced ** 2))
            
            metrics['original_rms'] = float(original_rms)
            metrics['enhanced_rms'] = float(enhanced_rms)
            
            # Peak levels
            metrics['original_peak'] = float(np.max(np.abs(original)))
            metrics['enhanced_peak'] = float(np.max(np.abs(enhanced)))
            
            # Dynamic range
            if original_rms > 0:
                metrics['original_dynamic_range'] = float(20 * np.log10(np.max(np.abs(original)) / original_rms))
            else:
                metrics['original_dynamic_range'] = 0.0
                
            if enhanced_rms > 0:
                metrics['enhanced_dynamic_range'] = float(20 * np.log10(np.max(np.abs(enhanced)) / enhanced_rms))
            else:
                metrics['enhanced_dynamic_range'] = 0.0
            
            # Spectral centroid comparison
            original_centroid = self._calculate_spectral_centroid(original)
            enhanced_centroid = self._calculate_spectral_centroid(enhanced)
            
            metrics['original_spectral_centroid'] = original_centroid
            metrics['enhanced_spectral_centroid'] = enhanced_centroid
            metrics['spectral_centroid_change'] = enhanced_centroid - original_centroid
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Quality metrics calculation failed: {e}")
            return {}
    
    def _calculate_spectral_centroid(self, audio_data: np.ndarray) -> float:
        """Calculate spectral centroid"""        try:
            fft = np.fft.fft(audio_data[:8192])  # Use first 8192 samples
            magnitude = np.abs(fft[:4096])  # First half (positive frequencies)
            
            if np.sum(magnitude) == 0:
                return 0.0
            
            freqs = np.arange(len(magnitude))
            centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
            
            # Convert to Hz (roughly)
            centroid_hz = centroid * self.sample_rate / (2 * len(magnitude))
            
            return float(centroid_hz)
            
        except Exception:
            return 0.0
    
    def _calculate_enhancement_gain(self, original: np.ndarray, enhanced: np.ndarray) -> float:
        """Calculate overall enhancement gain in dB"""        try:
            original_rms = np.sqrt(np.mean(original ** 2))
            enhanced_rms = np.sqrt(np.mean(enhanced ** 2))
            
            if original_rms > 0 and enhanced_rms > 0:
                gain_db = 20 * np.log10(enhanced_rms / original_rms)
                return float(gain_db)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _analyze_frequency_response(self, original: np.ndarray, enhanced: np.ndarray) -> Dict[str, float]:
        """Analyze frequency response changes"""        try:
            # Calculate frequency response in different bands
            bands = {
                'sub_bass': (20, 60),
                'bass': (60, 250),
                'low_mid': (250, 500),
                'mid': (500, 2000),
                'high_mid': (2000, 4000),
                'presence': (4000, 6000),
                'brilliance': (6000, 20000)
            }
            
            response = {}
            
            # Simple frequency analysis using FFT
            original_fft = np.fft.fft(original[:8192])
            enhanced_fft = np.fft.fft(enhanced[:8192])
            
            freqs = np.fft.fftfreq(len(original_fft), 1/self.sample_rate)
            
            for band_name, (low_freq, high_freq) in bands.items():
                # Find frequency bins in this band
                band_mask = (np.abs(freqs) >= low_freq) & (np.abs(freqs) <= high_freq)
                
                if np.any(band_mask):
                    original_energy = np.mean(np.abs(original_fft[band_mask])**2)
                    enhanced_energy = np.mean(np.abs(enhanced_fft[band_mask])**2)
                    
                    if original_energy > 0:
                        gain_db = 10 * np.log10(enhanced_energy / original_energy)
                        response[band_name] = float(gain_db)
                    else:
                        response[band_name] = 0.0
                else:
                    response[band_name] = 0.0
            
            return response
            
        except Exception as e:
            self.logger.error(f"Frequency response analysis failed: {e}")
            return {}
    
    def _check_enhancement_quality(self, result: EnhancementResult):
        """Check for potential enhancement quality issues"""        try:
            warnings = []
            
            # Check for clipping
            if result.quality_metrics.get('enhanced_peak', 0) > 0.95:
                warnings.append("Enhanced audio may be clipping")
            
            # Check for excessive gain
            if result.enhancement_gain_db > 6.0:
                warnings.append("High enhancement gain may introduce artifacts")
            elif result.enhancement_gain_db < -6.0:
                warnings.append("Significant level reduction detected")
            
            # Check dynamic range
            original_dr = result.quality_metrics.get('original_dynamic_range', 0)
            enhanced_dr = result.quality_metrics.get('enhanced_dynamic_range', 0)
            
            if enhanced_dr < original_dr - 6:
                warnings.append("Significant dynamic range reduction detected")
            
            # Check spectral centroid changes
            centroid_change = result.quality_metrics.get('spectral_centroid_change', 0)
            if abs(centroid_change) > 2000:
                warnings.append("Large spectral changes detected - verify quality")
            
            result.warnings.extend(warnings)
            
        except Exception as e:
            self.logger.error(f"Quality check failed: {e}")
    
    def batch_enhance(self, audio_files: List[np.ndarray], 
                     settings: EnhancementSettings) -> List[EnhancementResult]:
        """Enhance multiple audio files with same settings"""        results = []
        
        for i, audio_data in enumerate(audio_files):
            self.logger.info(f"Processing file {i+1}/{len(audio_files)}")
            result = self.enhance(audio_data, settings)
            results.append(result)
        
        return results
    
    def create_enhancement_preset(self, name: str, enhancement_type: EnhancementType,
                                strength: float, quality_level: QualityLevel = QualityLevel.MEDIUM,
                                **kwargs) -> EnhancementSettings:
        """Create an enhancement preset"""        return EnhancementSettings(
            enhancement_type=enhancement_type,
            strength=strength,
            quality_level=quality_level,
            custom_parameters=kwargs
        )

# Export main classes
__all__ = [
    'AudioEnhancer',
    'EnhancementSettings',
    'EnhancementResult',
    'EnhancementType',
    'QualityLevel'
]

logger.info("Audio enhancement module loaded successfully")
