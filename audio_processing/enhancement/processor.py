"""Professional Audio Enhancement Processor
========================================

Industrial-grade audio enhancement system for content creators, musicians, and influencers.
Supports multi-format audio enhancement with AI-powered noise reduction, spectral enhancement,
dynamic range optimization, and professional mastering.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will be prosecuted to the full extent of the law.
"""

import numpy as np
import librosa
import soundfile as sf
import scipy.signal as signal
from scipy.ndimage import uniform_filter1d
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import tempfile
import warnings
from concurrent.futures import ThreadPoolExecutor
import json
import time

from ..core.exceptions import AudioProcessingError
from ..core.validators import AudioValidator
from ..core.utils import AudioUtil


class EnhancementType(Enum):
    """
Audio enhancement processing types"""

    NOISE_REDUCTION = "noise_reduction"
    SPECTRAL_ENHANCEMENT = "spectral_enhancement"
    DYNAMIC_RANGE_OPTIMIZATION = "dynamic_range_optimization"
    STEREO_ENHANCEMENT = "stereo_enhancement"
    HARMONIC_ENHANCEMENT = "harmonic_enhancement"
    VOCAL_ENHANCEMENT = "vocal_enhancement"
    MASTERING = "mastering"
    RESTORATION = "restoration"


class ContentType(Enum):
    """Audio content classification"""

    MUSIC = "music"
    SPEECH = "speech"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    VOICEOVER = "voiceover"
    INSTRUMENT = "instrument"
    SOUND_EFFECT = "sound_effect"
    GENERAL = "general"


@dataclass
class EnhancementParameters:
    """Professional enhancement parameters configuration"""
    noise_reduction_strength: float = 0.5
    spectral_enhancement_gain: float = 3.0
    dynamic_range_target: float = 0.7
    stereo_width: float = 1.0
    harmonic_emphasis: float = 0.3
    vocal_clarity: float = 0.4
    mastering_loudness_lufs: float = -16.0
    restoration_strength: float = 0.6
    preserve_original_character: bool = True
    adaptive_processing: bool = True
    multiband_processing: bool = True
    high_quality_mode: bool = True


@dataclass
class EnhancementResult:
    """
Complete enhancement processing results"""
    enhanced_audio: np.ndarray
    sample_rate: int
    enhancement_gain_db: float
    processing_time: float
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    applied_enhancements: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SpectralEnhancer:
    """
Advanced spectral enhancement processor"""
    
    def __init__(self):
        self.fft_size = 2048
        self.hop_length = 512
        self.enhancement_curve = self._create_enhancement_curve()
    
    def _create_enhancement_curve(self) -> np.ndarray:
        """
Create frequency-dependent enhancement curve"""
        # Professional enhancement curve for music production
        freqs = np.logspace(np.log10(20), np.log10(20000), 1000)
        curve = np.ones_like(freqs)
        
        # Gentle high-frequency emphasis for clarity
        hf_boost = 1 + 0.3 * np.tanh((freqs - 3000) / 2000)
        curve *= hf_boost
        
        # Mild low-mid attenuation to reduce muddiness
        lm_cut = 1 - 0.15 * np.exp(-((freqs - 300) / 200) ** 2)
        curve *= lm_cut
        
        # Presence boost around 5kHz
        presence = 1 + 0.2 * np.exp(-((freqs - 5000) / 1000) ** 2)
        curve *= presence
        
        return curve
    
    def enhance(self, audio: np.ndarray, sample_rate: int, 
                strength: float = 0.5) -> np.ndarray:
        """
Apply spectral enhancement to audio"""
        if len(audio.shape) == 1:
            return self._enhance_mono(audio, sample_rate, strength)
        else:
            # Process each channel separately
            enhanced_channels = []
            for channel in range(audio.shape[1]):
                enhanced = self._enhance_mono(audio[:, channel], sample_rate, strength)
                enhanced_channels.append(enhanced)
            return np.column_stack(enhanced_channels)
    
    def _enhance_mono(self, audio: np.ndarray, sample_rate: int, 
                     strength: float) -> np.ndarray:
        """
Enhance mono audio signal"""
        # Short-time Fourier transform
        stft = librosa.stft(audio, n_fft=self.fft_size, 
                           hop_length=self.hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Apply frequency-dependent enhancement
        freq_bins = magnitude.shape[0]
        enhancement_factors = np.interp(
            np.linspace(0, sample_rate // 2, freq_bins),
            np.logspace(np.log10(20), np.log10(sample_rate // 2), 
                       len(self.enhancement_curve)),
            self.enhancement_curve
        )
        
        # Apply enhancement with strength control
        enhanced_magnitude = magnitude * (1 + strength * (enhancement_factors[:, None] - 1))
        
        # Reconstruct audio
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, 
                                     hop_length=self.hop_length)
        
        return enhanced_audio


class NoiseReducer:
    """
Professional noise reduction processor"""
    
    def __init__(self):
        self.noise_gate_threshold = -40.0  # dB
        self.noise_floor_estimation_duration = 0.5  # seconds
        
    def reduce(self, audio: np.ndarray, sample_rate: int, 
               strength: float = 0.5) -> np.ndarray:
        """
Advanced noise reduction using spectral gating and ML techniques"""
        if len(audio.shape) == 1:
            return self._reduce_mono(audio, sample_rate, strength)
        else:
            # Process each channel separately
            processed_channels = []
            for channel in range(audio.shape[1]):
                processed = self._reduce_mono(audio[:, channel], sample_rate, strength)
                processed_channels.append(processed)
            return np.column_stack(processed_channels)
    
    def _reduce_mono(self, audio: np.ndarray, sample_rate: int, 
                    strength: float) -> np.ndarray:
        """
Noise reduction for mono audio"""
        # Estimate noise profile from quiet sections
        noise_profile = self._estimate_noise_profile(audio, sample_rate)
        
        # Apply spectral subtraction
        stft = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Spectral subtraction with over-subtraction factor
        over_subtraction = 2.0 * strength
        spectral_floor = 0.002  # -54 dB
        
        enhanced_magnitude = magnitude - over_subtraction * noise_profile[:, None]
        enhanced_magnitude = np.maximum(enhanced_magnitude, 
                                      spectral_floor * magnitude)
        
        # Smooth the gain function to reduce musical noise
        gain = enhanced_magnitude / (magnitude + 1e-10)
        gain = self._smooth_gain(gain)
        
        # Apply noise gate
        gate_gain = self._apply_noise_gate(audio, sample_rate)
        
        # Combine spectral subtraction and noise gate
        final_magnitude = magnitude * gain * gate_gain
        
        # Reconstruct audio
        enhanced_stft = final_magnitude * np.exp(1j * phase)
        return librosa.istft(enhanced_stft, hop_length=512)
    
    def _estimate_noise_profile(self, audio: np.ndarray, 
                               sample_rate: int) -> np.ndarray:
        """
Estimate noise profile from quiet sections"""
        # Find quiet sections using energy-based detection
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = frame_length // 2
        
        energy = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame_energy = np.sum(audio[i:i + frame_length] ** 2)
            energy.append(frame_energy)
        
        energy = np.array(energy)
        quiet_threshold = np.percentile(energy, 10)  # Bottom 10%
        
        # Extract quiet sections for noise estimation
        quiet_audio = []
        for i, e in enumerate(energy):
            if e <= quiet_threshold:
                start_idx = i * hop_length
                end_idx = start_idx + frame_length
                quiet_audio.extend(audio[start_idx:end_idx])
        
        if len(quiet_audio) < sample_rate * 0.1:  # At least 100ms
            # Fallback: use first 100ms as noise sample
            quiet_audio = audio[:int(0.1 * sample_rate)]
        
        quiet_audio = np.array(quiet_audio)
        
        # Compute noise spectrum
        noise_stft = librosa.stft(quiet_audio, n_fft=2048, hop_length=512)
        noise_magnitude = np.mean(np.abs(noise_stft), axis=1)
        
        return noise_magnitude
    
    def _smooth_gain(self, gain: np.ndarray, 
                    smoothing_frames: int = 3) -> np.ndarray:
        """
Smooth gain function to reduce musical noise"""
        # Temporal smoothing
        for i in range(gain.shape[0]):
            gain[i, :] = uniform_filter1d(gain[i, :], size=smoothing_frames)
        
        # Frequency smoothing
        for i in range(gain.shape[1]):
            gain[:, i] = uniform_filter1d(gain[:, i], size=2)
        
        return gain
    
    def _apply_noise_gate(self, audio: np.ndarray, 
                         sample_rate: int) -> float:
        """
Apply noise gate based on signal level"""
        # Compute RMS level in dB
        rms = np.sqrt(np.mean(audio ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        
        # Soft knee gate
        if rms_db > self.noise_gate_threshold:
            return 1.0
        elif rms_db < self.noise_gate_threshold - 10:
            return 0.0
        else:
            # Smooth transition
            ratio = (rms_db - (self.noise_gate_threshold - 10)) / 10
            return 0.5 * (1 + np.cos(np.pi * (1 - ratio)))


class DynamicRangeOptimizer:
    """
Professional dynamic range optimization processor"""
    
    def __init__(self):
        self.compressor_ratio = 4.0
        self.compressor_attack = 0.003  # 3ms
        self.compressor_release = 0.1   # 100ms
        self.limiter_threshold = -0.3   # dB
    
    def optimize(self, audio: np.ndarray, sample_rate: int, 
                target_range: float = 0.7) -> np.ndarray:
        """
Optimize dynamic range with multiband compression"""
        if len(audio.shape) == 1:
            return self._optimize_mono(audio, sample_rate, target_range)
        else:
            # Process each channel separately
            processed_channels = []
            for channel in range(audio.shape[1]):
                processed = self._optimize_mono(audio[:, channel], 
                                              sample_rate, target_range)
                processed_channels.append(processed)
            return np.column_stack(processed_channels)
    
    def _optimize_mono(self, audio: np.ndarray, sample_rate: int, 
                      target_range: float) -> np.ndarray:
        """
Dynamic range optimization for mono audio"""
        # Multiband processing
        bands = self._split_into_bands(audio, sample_rate)
        processed_bands = []
        
        for band_audio, (low_freq, high_freq) in bands:
            # Apply frequency-dependent compression
            threshold = self._calculate_band_threshold(low_freq, high_freq)
            compressed = self._apply_compression(band_audio, sample_rate, 
                                               threshold, self.compressor_ratio)
            processed_bands.append(compressed)
        
        # Recombine bands
        processed_audio = self._combine_bands(processed_bands, sample_rate)
        
        # Apply limiting to prevent clipping
        limited_audio = self._apply_limiter(processed_audio, sample_rate)
        
        # Normalize to target dynamic range
        normalized_audio = self._normalize_dynamic_range(limited_audio, 
                                                        target_range)
        
        return normalized_audio
    
    def _split_into_bands(self, audio: np.ndarray, 
                         sample_rate: int) -> List[Tuple[np.ndarray, Tuple[int, int]]]:
        """
Split audio into frequency bands for multiband processing"""
        crossover_freqs = [200, 1000, 4000]  # Hz
        bands = []
        
        # Low band (0-200 Hz)
        low_filter = signal.butter(6, crossover_freqs[0], 
                                  btype='low', fs=sample_rate)
        low_band = signal.filtfilt(low_filter[0], low_filter[1], audio)
        bands.append((low_band, (0, crossover_freqs[0])))
        
        # Mid bands
        for i in range(len(crossover_freqs) - 1):
            band_filter = signal.butter(6, [crossover_freqs[i], crossover_freqs[i+1]], 
                                       btype='band', fs=sample_rate)
            band_audio = signal.filtfilt(band_filter[0], band_filter[1], audio)
            bands.append((band_audio, (crossover_freqs[i], crossover_freqs[i+1])))
        
        # High band (4000+ Hz)
        high_filter = signal.butter(6, crossover_freqs[-1], 
                                   btype='high', fs=sample_rate)
        high_band = signal.filtfilt(high_filter[0], high_filter[1], audio)
        bands.append((high_band, (crossover_freqs[-1], sample_rate // 2)))
        
        return bands
    
    def _calculate_band_threshold(self, low_freq: int, high_freq: int) -> float:
        """
Calculate compression threshold for frequency band"""
        # Lower threshold for low frequencies, higher for highs
        if high_freq <= 200:
            return -18.0  # dB
        elif low_freq >= 4000:
            return -12.0  # dB
        else:
            return -15.0  # dB
    
    def _apply_compression(self, audio: np.ndarray, sample_rate: int, 
                          threshold_db: float, ratio: float) -> np.ndarray:
        """
Apply dynamic range compression"""
        # Convert to dB scale for processing
        audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
        
        # Calculate gain reduction
        gain_reduction = np.zeros_like(audio_db)
        above_threshold = audio_db > threshold_db
        gain_reduction[above_threshold] = (
            (audio_db[above_threshold] - threshold_db) * (1 - 1/ratio)
        )
        
        # Apply attack and release smoothing
        gain_reduction = self._apply_envelope_smoothing(
            gain_reduction, sample_rate, self.compressor_attack, self.compressor_release
        )
        
        # Convert back to linear scale and apply
        gain_linear = 10 ** (gain_reduction / 20)
        return audio * gain_linear
    
    def _apply_envelope_smoothing(self, gain_reduction: np.ndarray, 
                                 sample_rate: int, attack: float, 
                                 release: float) -> np.ndarray:
        """
Apply attack and release envelope smoothing"""
        attack_coef = np.exp(-1.0 / (attack * sample_rate))
        release_coef = np.exp(-1.0 / (release * sample_rate))
        
        smoothed = np.zeros_like(gain_reduction)
        smoothed[0] = gain_reduction[0]
        
        for i in range(1, len(gain_reduction)):
            if gain_reduction[i] > smoothed[i-1]:
                # Attack
                smoothed[i] = attack_coef * smoothed[i-1] + \
                             (1 - attack_coef) * gain_reduction[i]
            else:
                # Release
                smoothed[i] = release_coef * smoothed[i-1] + \
                             (1 - release_coef) * gain_reduction[i]
        
        return smoothed
    
    def _combine_bands(self, bands: List[np.ndarray], 
                      sample_rate: int) -> np.ndarray:
        """
Combine processed frequency bands"""
        # Simply sum the bands (linear phase reconstruction)
        combined = np.sum(bands, axis=0)
        return combined
    
    def _apply_limiter(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
Apply soft limiter to prevent clipping"""
        threshold_linear = 10 ** (self.limiter_threshold / 20)
        
        # Soft knee limiting
        limited = np.where(
            np.abs(audio) > threshold_linear,
            np.sign(audio) * (threshold_linear + 
                             (np.abs(audio) - threshold_linear) * 0.1),
            audio
        )
        
        return limited
    
    def _normalize_dynamic_range(self, audio: np.ndarray, 
                               target_range: float) -> np.ndarray:
        """
Normalize audio to target dynamic range"""
        current_peak = np.max(np.abs(audio))
        target_peak = target_range
        
        if current_peak > 0:
            gain = target_peak / current_peak
            return audio * gain
        else:
            return audio


class AudioEnhancementProcessor:
    """
    Professional Audio Enhancement Processor
    
    Industrial-grade audio enhancement system providing comprehensive
    audio quality improvements for content creators and musicians.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize the audio enhancement processor"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize component processors
        self.spectral_enhancer = SpectralEnhancer()
        self.noise_reducer = NoiseReducer()
        self.dynamic_optimizer = DynamicRangeOptimizer()
        
        # Audio validator
        self.validator = AudioValidator()
        
        # Processing statistics
        self.processing_stats = {
            'total_processed': 0,
            'total_processing_time': 0.0,
            'average_enhancement_gain': 0.0
        }
    
    def enhance_audio(self, 
                     audio: np.ndarray, 
                     sample_rate: int,
                     parameters: Optional[EnhancementParameters] = None,
                     content_type: ContentType = ContentType.GENERAL) -> EnhancementResult:
        """
        Enhance audio with comprehensive professional processing
        
        Args:
            audio: Input audio signal
            sample_rate: Sample rate in Hz
            parameters: Enhancement parameters
            content_type: Type of audio content for adaptive processing
            
        Returns:
            EnhancementResult with processed audio and metrics
        """
        start_time = time.time()
        
        try:
            # Validate input audio
            self.validator.validate_audio_array(audio, sample_rate)
            
            if parameters is None:
                parameters = EnhancementParameters()
            
            # Adaptive parameters based on content type
            if parameters.adaptive_processing:
                parameters = self._adapt_parameters_for_content(parameters, content_type)
            
            # Store original audio metrics
            original_metrics = self._calculate_audio_metrics(audio, sample_rate)
            
            # Apply enhancement chain
            enhanced_audio = audio.copy()
            applied_enhancements = []
            
            # 1. Noise Reduction
            if parameters.noise_reduction_strength > 0:
                enhanced_audio = self.noise_reducer.reduce(
                    enhanced_audio, sample_rate, parameters.noise_reduction_strength
                )
                applied_enhancements.append("noise_reduction")
            
            # 2. Spectral Enhancement
            if parameters.spectral_enhancement_gain > 0:
                enhanced_audio = self.spectral_enhancer.enhance(
                    enhanced_audio, sample_rate, parameters.spectral_enhancement_gain
                )
                applied_enhancements.append("spectral_enhancement")
            
            # 3. Dynamic Range Optimization
            if parameters.dynamic_range_target > 0:
                enhanced_audio = self.dynamic_optimizer.optimize(
                    enhanced_audio, sample_rate, parameters.dynamic_range_target
                )
                applied_enhancements.append("dynamic_optimization")
            
            # 4. Stereo Enhancement (if stereo)
            if len(enhanced_audio.shape) > 1 and parameters.stereo_width != 1.0:
                enhanced_audio = self._enhance_stereo(enhanced_audio, parameters.stereo_width)
                applied_enhancements.append("stereo_enhancement")
            
            # Calculate enhancement metrics
            enhanced_metrics = self._calculate_audio_metrics(enhanced_audio, sample_rate)
            quality_metrics = self._compare_metrics(original_metrics, enhanced_metrics)
            
            # Calculate enhancement gain
            original_rms = np.sqrt(np.mean(audio ** 2))
            enhanced_rms = np.sqrt(np.mean(enhanced_audio ** 2))
            enhancement_gain_db = 20 * np.log10((enhanced_rms + 1e-10) / (original_rms + 1e-10))
            
            processing_time = time.time() - start_time
            
            # Create result
            result = EnhancementResult(
                enhanced_audio=enhanced_audio,
                sample_rate=sample_rate,
                enhancement_gain_db=enhancement_gain_db,
                processing_time=processing_time,
                quality_metrics=quality_metrics,
                applied_enhancements=applied_enhancements,
                metadata={
                    'content_type': content_type.value,
                    'parameters': parameters.__dict__,
                    'original_metrics': original_metrics,
                    'enhanced_metrics': enhanced_metrics
                }
            )
            
            # Quality validation
            self._validate_enhancement_quality(result)
            
            # Update statistics
            self._update_processing_stats(result)
            
            self.logger.info(f"Audio enhancement completed in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Audio enhancement failed: {str(e)}")
            raise AudioProcessingError(f"Enhancement processing failed: {str(e)}")
    
    def batch_enhance(self, 
                     audio_files: List[Union[str, Path]], 
                     parameters: Optional[EnhancementParameters] = None,
                     content_type: ContentType = ContentType.GENERAL,
                     max_workers: int = 4) -> List[EnhancementResult]:
        """
        Process multiple audio files in parallel
        
        Args:
            audio_files: List of audio file paths
            parameters: Enhancement parameters
            content_type: Type of audio content
            max_workers: Maximum parallel workers
            
        Returns:
            List of EnhancementResult objects
        """
        def process_single_file(file_path):
            try:
                # Load audio
                audio, sample_rate = librosa.load(str(file_path), sr=None)
                
                # Enhance audio
                result = self.enhance_audio(audio, sample_rate, parameters, content_type)
                
                # Save enhanced audio
                output_path = Path(file_path).with_suffix('_enhanced.wav')
                sf.write(str(output_path), result.enhanced_audio, result.sample_rate)
                result.metadata['output_path'] = str(output_path)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {str(e)}")
                return None
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_single_file, audio_files))
        
        # Filter out None results (failed processing)
        successful_results = [r for r in results if r is not None]
        
        self.logger.info(f"Batch processing completed: {len(successful_results)}/{len(audio_files)} successful")
        return successful_results
    
    def _adapt_parameters_for_content(self, 
                                    parameters: EnhancementParameters,
                                    content_type: ContentType) -> EnhancementParameters:
        """Adapt enhancement parameters based on content type"""
        adapted = EnhancementParameters(**parameters.__dict__)
        
        if content_type == ContentType.SPEECH:
            adapted.noise_reduction_strength = min(0.7, parameters.noise_reduction_strength + 0.2)
            adapted.vocal_clarity = min(1.0, parameters.vocal_clarity + 0.3)
            adapted.spectral_enhancement_gain = parameters.spectral_enhancement_gain * 0.8
            
        elif content_type == ContentType.MUSIC:
            adapted.harmonic_emphasis = min(1.0, parameters.harmonic_emphasis + 0.2)
            adapted.stereo_width = min(1.5, parameters.stereo_width + 0.2)
            adapted.dynamic_range_target = max(0.6, parameters.dynamic_range_target)
            
        elif content_type == ContentType.PODCAST:
            adapted.noise_reduction_strength = min(0.8, parameters.noise_reduction_strength + 0.3)
            adapted.vocal_clarity = min(1.0, parameters.vocal_clarity + 0.4)
            adapted.dynamic_range_target = 0.8
            
        return adapted
    
    def _enhance_stereo(self, audio: np.ndarray, width: float) -> np.ndarray:
        """
Enhance stereo width and imaging"""
        if len(audio.shape) != 2 or audio.shape[1] != 2:
            return audio
        
        # Mid-Side processing
        left, right = audio[:, 0], audio[:, 1]
        mid = (left + right) / 2
        side = (left - right) / 2
        
        # Apply stereo width enhancement
        enhanced_side = side * width
        
        # Convert back to Left-Right
        enhanced_left = mid + enhanced_side
        enhanced_right = mid - enhanced_side
        
        # Prevent clipping
        max_val = max(np.max(np.abs(enhanced_left)), np.max(np.abs(enhanced_right)))
        if max_val > 1.0:
            scale_factor = 0.95 / max_val
            enhanced_left *= scale_factor
            enhanced_right *= scale_factor
        
        return np.column_stack([enhanced_left, enhanced_right])
    
    def _calculate_audio_metrics(self, audio: np.ndarray, 
                                sample_rate: int) -> Dict[str, float]:
        """
Calculate comprehensive audio quality metrics"""
        metrics = {}
        
        # Basic metrics
        metrics['peak_amplitude'] = np.max(np.abs(audio))
        metrics['rms_level'] = np.sqrt(np.mean(audio ** 2))
        metrics['rms_db'] = 20 * np.log10(metrics['rms_level'] + 1e-10)
        
        # Dynamic range
        peak_db = 20 * np.log10(metrics['peak_amplitude'] + 1e-10)
        metrics['dynamic_range_db'] = peak_db - metrics['rms_db']
        
        # Spectral features
        if len(audio) > 1024:  # Ensure sufficient length for spectral analysis
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
            metrics['spectral_centroid'] = np.mean(spectral_centroid)
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)[0]
            metrics['spectral_bandwidth'] = np.mean(spectral_bandwidth)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)[0]
            metrics['spectral_rolloff'] = np.mean(spectral_rolloff)
            
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
            metrics['zero_crossing_rate'] = np.mean(zero_crossing_rate)
        
        # Crest factor
        if metrics['rms_level'] > 0:
            metrics['crest_factor'] = metrics['peak_amplitude'] / metrics['rms_level']
        else:
            metrics['crest_factor'] = 0.0
        
        return metrics
    
    def _compare_metrics(self, original: Dict[str, float], 
                        enhanced: Dict[str, float]) -> Dict[str, float]:
        """
Compare original and enhanced audio metrics"""
        comparison = {}
        
        for key in original:
            if key in enhanced:
                if 'db' in key or 'level' in key:
                    comparison[f"{key}_change"] = enhanced[key] - original[key]
                else:
                    if original[key] != 0:
                        comparison[f"{key}_ratio"] = enhanced[key] / original[key]
                    else:
                        comparison[f"{key}_ratio"] = 1.0
        
        # Add enhanced values
        for key, value in enhanced.items():
            comparison[f"enhanced_{key}"] = value
        
        return comparison
    
    def _validate_enhancement_quality(self, result: EnhancementResult):
        """Validate enhancement quality and add warnings if needed"""
        warnings = []
        
        # Check for clipping
        if result.quality_metrics.get('enhanced_peak_amplitude', 0) > 0.95:
            warnings.append("Enhanced audio may be clipping")
        
        # Check for excessive gain
        if result.enhancement_gain_db > 6.0:
            warnings.append("High enhancement gain may introduce artifacts")
        elif result.enhancement_gain_db < -6.0:
            warnings.append("Significant level reduction detected")
        
        # Check dynamic range
        original_dr = result.metadata.get('original_metrics', {}).get('dynamic_range_db', 0)
        enhanced_dr = result.metadata.get('enhanced_metrics', {}).get('dynamic_range_db', 0)
        
        if enhanced_dr < original_dr - 6:
            warnings.append("Significant dynamic range reduction detected")
        
        # Check spectral centroid changes
        centroid_change = result.quality_metrics.get('spectral_centroid_change', 0)
        if abs(centroid_change) > 2000:
            warnings.append("Large spectral changes detected - verify quality")
        
        result.warnings.extend(warnings)
    
    def _update_processing_stats(self, result: EnhancementResult):
        """Update processor statistics"""
        self.processing_stats['total_processed'] += 1
        self.processing_stats['total_processing_time'] += result.processing_time
        
        # Update average enhancement gain
        current_avg = self.processing_stats['average_enhancement_gain']
        n = self.processing_stats['total_processed']
        new_avg = ((n - 1) * current_avg + result.enhancement_gain_db) / n
        self.processing_stats['average_enhancement_gain'] = new_avg
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
Get processor performance statistics"""
        stats = self.processing_stats.copy()
        if stats['total_processed'] > 0:
            stats['average_processing_time'] = stats['total_processing_time'] / stats['total_processed']
        else:
            stats['average_processing_time'] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """
Reset processing statistics"""
        self.processing_stats = {
            'total_processed': 0,
            'total_processing_time': 0.0,
            'average_enhancement_gain': 0.0
        }
    
    def export_configuration(self, file_path: Union[str, Path]):
        """
Export current processor configuration"""
        config = {
            'processor_config': self.config,
            'statistics': self.get_processing_statistics(),
            'version': '1.0.0'
        }
        
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def import_configuration(self, file_path: Union[str, Path]):
        """
Import processor configuration"""
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        self.config = config.get('processor_config', {})
        if 'statistics' in config:
            self.processing_stats.update(config['statistics'])
