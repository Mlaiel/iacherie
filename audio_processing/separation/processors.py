"""
Professional audio processors for separation pipeline operations.

This module provides high-performance audio processing components for
preprocessing, postprocessing, and quality analysis of separated audio stems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - Unauthorized use strictly prohibited
License: Proprietary - Contact for licensing

 WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or modification is strictly
prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import torch
import librosa
import soundfile as sf
from scipy import signal
import pyloudnorm as pyln

from ...core.config import get_settings
from ...core.exceptions import AudioProcessingError
from ...utils.logging import get_logger
from .core import SeparationQuality, OutputFormat

logger = get_logger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for audio processing operations."""
    sample_rate: int = 44100
    bit_depth: int = 24
    channels: int = 2
    block_size: int = 4096
    overlap_factor: float = 0.25
    normalization_target: float = -23.0  # LUFS
    dynamic_range: float = 14.0  # LU
    enable_dithering: bool = True
    quality_threshold: float = 0.7


@dataclass 
class ProcessingResult:
    """Result container for processing operations."""
    processed_audio: np.ndarray
    quality_metrics: Dict[str, float]
    processing_time: float
    metadata: Dict[str, Any]


class BaseProcessor(ABC):
    """Abstract base class for audio processors."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    @abstractmethod
    async def process(self, audio: np.ndarray, **kwargs) -> ProcessingResult:
        """Process audio data."""
        pass
    
    def validate_audio_input(self, audio: np.ndarray) -> None:
        """Validate input audio format."""
        if not isinstance(audio, np.ndarray):
            raise AudioProcessingError("Audio must be numpy array")
        
        if audio.size == 0:
            raise AudioProcessingError("Audio cannot be empty")
        
        if np.isnan(audio).any() or np.isinf(audio).any():
            raise AudioProcessingError("Audio contains invalid values")
    
    def cleanup(self) -> None:
        """Clean up processor resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)


class AudioProcessor(BaseProcessor):
    """Main audio processor for separation pipeline."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self.loudness_meter = pyln.Meter(self.config.sample_rate)
        self.filters = self._initialize_filters()
        
    def _initialize_filters(self) -> Dict[str, Any]:
        """Initialize audio filters."""



        return {
            "highpass": signal.butter(4, 20, btype='high', fs=self.config.sample_rate),
            "lowpass": signal.butter(4, 20000, btype='low', fs=self.config.sample_rate),
            "notch": signal.iirnotch(50, 30, fs=self.config.sample_rate),  # Power line noise
            "deesser": signal.butter(6, [5000, 8000], btype='band', fs=self.config.sample_rate)
        }
    
    async def process(self, audio: np.ndarray, 
                     operations: Optional[List[str]] = None) -> ProcessingResult:
        """Process audio with specified operations."""
        self.validate_audio_input(audio)
        start_time = asyncio.get_event_loop().time()
        
        operations = operations or ["normalize", "denoise", "enhance"]
        
        try:
            processed_audio = audio.copy()
            quality_metrics = {}
            metadata = {"operations": operations}
            
            # Apply processing operations
            for operation in operations:
                if operation == "normalize":
                    processed_audio = await self._normalize_audio(processed_audio)
                elif operation == "denoise":
                    processed_audio = await self._denoise_audio(processed_audio)
                elif operation == "enhance":
                    processed_audio = await self._enhance_audio(processed_audio)
                elif operation == "filter":
                    processed_audio = await self._filter_audio(processed_audio)
                elif operation == "dynamics":
                    processed_audio = await self._process_dynamics(processed_audio)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                original=audio,
                processed=processed_audio
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                processed_audio=processed_audio,
                quality_metrics=quality_metrics,
                processing_time=processing_time,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            raise AudioProcessingError(f"Processing error: {str(e)}")
    
    async def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio levels using loudness standards."""



        try:
            # Convert to proper format for loudness measurement
            if audio.ndim == 1:
                audio_2d = audio.reshape(-1, 1)
            else:
                audio_2d = audio
            
            # Measure current loudness
            current_loudness = self.loudness_meter.integrated_loudness(audio_2d)
            
            if current_loudness < -70.0:  # Very quiet signal
                logger.warning("Input audio is very quiet, applying basic normalization")
                peak = np.max(np.abs(audio))
                if peak > 0:
                    return audio / peak * 0.7
                return audio
            
            # Calculate required gain
            target_loudness = self.config.normalization_target
            gain_db = target_loudness - current_loudness
            gain_linear = 10 ** (gain_db / 20)
            
            # Apply gain with limiting
            normalized = audio * gain_linear
            peak = np.max(np.abs(normalized))
            
            if peak > 0.95:  # Apply limiting if clipping would occur
                normalized = normalized / peak * 0.95
            
            return normalized
            
        except Exception as e:
            logger.warning(f"Loudness normalization failed, using peak normalization: {str(e)}")
            # Fallback to peak normalization
            peak = np.max(np.abs(audio))
            if peak > 0:
                return audio / peak * 0.7
            return audio
    
    async def _denoise_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply advanced noise reduction."""



        try:
            # Spectral subtraction denoising
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor
            noise_floor = np.percentile(magnitude, 10, axis=1, keepdims=True)
            
            # Create noise suppression mask
            snr = magnitude / (noise_floor + 1e-10)
            suppression_factor = np.minimum(1.0, np.maximum(0.1, (snr - 1.5) / 3.0))
            
            # Apply suppression
            denoised_magnitude = magnitude * suppression_factor
            denoised_stft = denoised_magnitude * np.exp(1j * phase)
            
            # Reconstruct audio
            denoised_audio = librosa.istft(denoised_stft, hop_length=512)
            
            return denoised_audio
            
        except Exception as e:
            logger.error(f"Denoising failed: {str(e)}")
            return audio  # Return original if denoising fails
    
    async def _enhance_audio(self, audio: np.ndarray) -> np.ndarray:
        """Enhance audio quality and clarity."""



        try:
            # Multi-band enhancement
            enhanced_audio = audio.copy()
            
            # Enhance mid frequencies (presence)
            mid_freq_enhanced = self._apply_eq_band(
                enhanced_audio, 
                center_freq=2000, 
                gain_db=2.0, 
                q_factor=0.7
            )
            
            # Gentle high-frequency enhancement
            high_freq_enhanced = self._apply_eq_band(
                mid_freq_enhanced,
                center_freq=8000,
                gain_db=1.5,
                q_factor=0.5
            )
            
            # Subtle compression for consistency
            compressed = self._apply_soft_compression(high_freq_enhanced, ratio=2.0, threshold=-12.0)
            
            return compressed
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {str(e)}")
            return audio
    
    async def _filter_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply frequency filtering."""



        try:
            filtered_audio = audio.copy()
            
            # High-pass filter (remove DC and low rumble)
            sos_hp = self.filters["highpass"]
            filtered_audio = signal.sosfilt(sos_hp, filtered_audio)
            
            # Low-pass filter (remove high-frequency noise)
            sos_lp = self.filters["lowpass"]  
            filtered_audio = signal.sosfilt(sos_lp, filtered_audio)
            
            # Notch filter for power line interference
            sos_notch = self.filters["notch"]
            filtered_audio = signal.sosfilt(sos_notch, filtered_audio)
            
            return filtered_audio
            
        except Exception as e:
            logger.error(f"Filtering failed: {str(e)}")
            return audio
    
    async def _process_dynamics(self, audio: np.ndarray) -> np.ndarray:
        """Process audio dynamics with compression and limiting."""



        try:
            # Multi-band dynamics processing
            processed_audio = self._apply_multiband_compression(audio)
            
            # Final limiter to prevent clipping
            limited_audio = self._apply_limiter(processed_audio, threshold=-1.0)
            
            return limited_audio
            
        except Exception as e:
            logger.error(f"Dynamics processing failed: {str(e)}")
            return audio
    
    def _apply_eq_band(self, audio: np.ndarray, center_freq: float, 
                       gain_db: float, q_factor: float) -> np.ndarray:
        """Apply parametric EQ to specific frequency band."""



        try:
            # Design parametric filter
            w0 = 2 * np.pi * center_freq / self.config.sample_rate
            alpha = np.sin(w0) / (2 * q_factor)
            A = 10 ** (gain_db / 40)
            
            # Calculate filter coefficients
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w0)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha / A
            
            # Normalize coefficients
            b = np.array([b0, b1, b2]) / a0
            a = np.array([1, a1, a2]) / a0
            
            # Apply filter
            filtered = signal.filtfilt(b, a, audio)
            return filtered
            
        except Exception as e:
            logger.error(f"EQ band processing failed: {str(e)}")
            return audio
    
    def _apply_soft_compression(self, audio: np.ndarray, ratio: float, threshold: float) -> np.ndarray:
        """Apply soft compression to audio."""



        try:
            # Convert to dB
            threshold_linear = 10 ** (threshold / 20)
            
            # Find samples above threshold
            above_threshold = np.abs(audio) > threshold_linear
            
            # Apply compression ratio
            compressed = audio.copy()
            compressed[above_threshold] = (
                np.sign(compressed[above_threshold]) * 
                threshold_linear * 
                (np.abs(compressed[above_threshold]) / threshold_linear) ** (1 / ratio)
            )
            
            return compressed
            
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}")
            return audio
    
    def _apply_multiband_compression(self, audio: np.ndarray) -> np.ndarray:
        """Apply multiband compression."""



        try:
            # Split into frequency bands
            low_cutoff = 250
            high_cutoff = 2000
            
            # Design crossover filters
            sos_low = signal.butter(4, low_cutoff, btype='low', fs=self.config.sample_rate)
            sos_mid = signal.butter(4, [low_cutoff, high_cutoff], btype='band', fs=self.config.sample_rate)
            sos_high = signal.butter(4, high_cutoff, btype='high', fs=self.config.sample_rate)
            
            # Split signal
            low_band = signal.sosfilt(sos_low, audio)
            mid_band = signal.sosfilt(sos_mid, audio)  
            high_band = signal.sosfilt(sos_high, audio)
            
            # Apply different compression to each band
            low_compressed = self._apply_soft_compression(low_band, ratio=3.0, threshold=-15.0)
            mid_compressed = self._apply_soft_compression(mid_band, ratio=2.5, threshold=-12.0)
            high_compressed = self._apply_soft_compression(high_band, ratio=2.0, threshold=-10.0)
            
            # Recombine bands
            compressed_audio = low_compressed + mid_compressed + high_compressed
            
            return compressed_audio
            
        except Exception as e:
            logger.error(f"Multiband compression failed: {str(e)}")
            return audio
    
    def _apply_limiter(self, audio: np.ndarray, threshold: float) -> np.ndarray:
        """Apply brick-wall limiter."""



        try:
            threshold_linear = 10 ** (threshold / 20)
            
            # Hard limiting
            limited = np.clip(audio, -threshold_linear, threshold_linear)
            
            return limited
            
        except Exception as e:
            logger.error(f"Limiting failed: {str(e)}")
            return audio
    
    async def _calculate_quality_metrics(self, original: np.ndarray, 
                                       processed: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive quality metrics."""



        try:
            metrics = {}
            
            # Align arrays
            min_len = min(len(original), len(processed))
            orig_aligned = original[:min_len]
            proc_aligned = processed[:min_len]
            
            # Signal-to-Noise Ratio
            signal_power = np.mean(orig_aligned ** 2)
            noise_power = np.mean((orig_aligned - proc_aligned) ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                metrics["snr_db"] = float(snr)
            else:
                metrics["snr_db"] = 100.0
            
            # Total Harmonic Distortion + Noise
            thd_plus_n = self._calculate_thd_n(proc_aligned)
            metrics["thd_plus_n_percent"] = thd_plus_n
            
            # Dynamic Range
            dynamic_range = self._calculate_dynamic_range(proc_aligned)
            metrics["dynamic_range_db"] = dynamic_range
            
            # Loudness metrics
            try:
                if proc_aligned.ndim == 1:
                    loudness_audio = proc_aligned.reshape(-1, 1)
                else:
                    loudness_audio = proc_aligned
                    
                integrated_loudness = self.loudness_meter.integrated_loudness(loudness_audio)
                metrics["integrated_loudness_lufs"] = float(integrated_loudness)
            except:
                metrics["integrated_loudness_lufs"] = -23.0
            
            # Frequency response flatness
            freq_flatness = self._calculate_frequency_flatness(proc_aligned)
            metrics["frequency_flatness"] = freq_flatness
            
            # Overall quality score
            quality_score = self._calculate_overall_quality(metrics)
            metrics["overall_quality"] = quality_score
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {str(e)}")
            return {"overall_quality": 0.5}  # Default fallback
    
    def _calculate_thd_n(self, audio: np.ndarray) -> float:
        """Calculate Total Harmonic Distortion + Noise."""



        try:
            # Generate 1kHz test tone reference
            duration = len(audio) / self.config.sample_rate
            t = np.linspace(0, duration, len(audio))
            test_tone = np.sin(2 * np.pi * 1000 * t)
            
            # Calculate correlation with fundamental
            correlation = np.corrcoef(audio, test_tone)[0, 1]
            
            # Estimate THD+N from correlation
            thd_n = (1 - abs(correlation)) * 100
            return min(100.0, max(0.0, thd_n))
            
        except:
            return 5.0  # Default value
    
    def _calculate_dynamic_range(self, audio: np.ndarray) -> float:
        """Calculate dynamic range."""



        try:
            # Calculate RMS over sliding windows
            window_size = int(0.1 * self.config.sample_rate)  # 100ms windows
            rms_values = []
            
            for i in range(0, len(audio) - window_size, window_size // 2):
                window = audio[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                if rms > 0:
                    rms_values.append(20 * np.log10(rms))
            
            if len(rms_values) > 0:
                dynamic_range = max(rms_values) - min(rms_values)
                return max(0.0, dynamic_range)
            
            return 0.0
            
        except:
            return 20.0  # Default value
    
    def _calculate_frequency_flatness(self, audio: np.ndarray) -> float:
        """Calculate frequency response flatness."""



        try:
            # Compute power spectral density
            freqs, psd = signal.welch(audio, fs=self.config.sample_rate, nperseg=2048)
            
            # Focus on audible range (20Hz - 20kHz)
            audible_mask = (freqs >= 20) & (freqs <= 20000)
            audible_psd = psd[audible_mask]
            
            if len(audible_psd) > 0:
                # Calculate flatness as inverse of standard deviation
                psd_db = 10 * np.log10(audible_psd + 1e-10)
                flatness = 1 / (1 + np.std(psd_db) / 10)  # Normalize
                return max(0.0, min(1.0, flatness))
            
            return 0.5
            
        except:
            return 0.5
    
    def _calculate_overall_quality(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from individual metrics."""



        try:
            # Normalize and weight different metrics
            snr_score = min(1.0, max(0.0, (metrics.get("snr_db", 0) + 10) / 50))
            thd_score = max(0.0, 1.0 - metrics.get("thd_plus_n_percent", 0) / 100)
            dynamic_score = min(1.0, metrics.get("dynamic_range_db", 0) / 30)
            freq_score = metrics.get("frequency_flatness", 0.5)
            
            # Weighted combination
            overall = (
                0.3 * snr_score +
                0.25 * thd_score +
                0.25 * dynamic_score +
                0.2 * freq_score
            )
            
            return max(0.0, min(1.0, overall))
            
        except:
            return 0.5


class StemProcessor(BaseProcessor):
    """Specialized processor for separated audio stems."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self.stem_profiles = self._load_stem_profiles()
    
    def _load_stem_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load processing profiles for different stem types."""



        return {
            "vocals": {
                "eq_curve": [(100, -2), (500, 1), (2000, 3), (8000, 2)],
                "compression": {"ratio": 3.0, "threshold": -15.0},
                "deesser": {"frequency": 6000, "threshold": -20.0}
            },
            "drums": {
                "eq_curve": [(60, 2), (200, -1), (5000, 3), (10000, 1)],
                "compression": {"ratio": 4.0, "threshold": -12.0},
                "gate": {"threshold": -40.0, "ratio": 10.0}
            },
            "bass": {
                "eq_curve": [(40, 1), (100, 2), (300, -1)],
                "compression": {"ratio": 3.5, "threshold": -18.0},
                "saturation": {"amount": 0.1}
            },
            "instruments": {
                "eq_curve": [(200, -1), (1000, 1), (4000, 2)],
                "compression": {"ratio": 2.5, "threshold": -10.0},
                "reverb": {"room_size": 0.3, "damping": 0.5}
            }
        }
    
    async def process(self, stems: Dict[str, np.ndarray], 
                     stem_types: Optional[List[str]] = None) -> Dict[str, ProcessingResult]:
        """Process multiple stems according to their types."""
        results = {}
        
        for stem_name, stem_audio in stems.items():
            if stem_types and stem_name not in stem_types:
                continue
                
            try:
                # Determine stem type and apply appropriate processing
                stem_type = self._identify_stem_type(stem_name)
                processed_result = await self._process_stem(stem_audio, stem_type)
                results[stem_name] = processed_result
                
            except Exception as e:
                logger.error(f"Failed to process stem {stem_name}: {str(e)}")
                # Provide fallback result
                results[stem_name] = ProcessingResult(
                    processed_audio=stem_audio,
                    quality_metrics={"overall_quality": 0.0},
                    processing_time=0.0,
                    metadata={"error": str(e)}
                )
        
        return results
    
    def _identify_stem_type(self, stem_name: str) -> str:
        """Identify stem type from name."""
        stem_name_lower = stem_name.lower()
        
        if any(keyword in stem_name_lower for keyword in ["vocal", "voice", "singer"]):
            return "vocals"
        elif any(keyword in stem_name_lower for keyword in ["drum", "kick", "snare", "hihat"]):
            return "drums"  
        elif any(keyword in stem_name_lower for keyword in ["bass", "sub"]):
            return "bass"
        else:
            return "instruments"
    
    async def _process_stem(self, audio: np.ndarray, stem_type: str) -> ProcessingResult:
        """Process individual stem according to its type."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            profile = self.stem_profiles.get(stem_type, self.stem_profiles["instruments"])
            processed_audio = audio.copy()
            
            # Apply stem-specific processing
            if "eq_curve" in profile:
                processed_audio = self._apply_eq_curve(processed_audio, profile["eq_curve"])
            
            if "compression" in profile:
                processed_audio = self._apply_compression(
                    processed_audio,
                    **profile["compression"]
                )
            
            if "deesser" in profile and stem_type == "vocals":
                processed_audio = self._apply_deesser(processed_audio, **profile["deesser"])
            
            if "gate" in profile and stem_type == "drums":
                processed_audio = self._apply_gate(processed_audio, **profile["gate"])
            
            if "saturation" in profile and stem_type == "bass":
                processed_audio = self._apply_saturation(processed_audio, **profile["saturation"])
            
            # Calculate quality metrics
            quality_metrics = self._calculate_stem_quality(audio, processed_audio, stem_type)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                processed_audio=processed_audio,
                quality_metrics=quality_metrics,
                processing_time=processing_time,
                metadata={"stem_type": stem_type, "profile_applied": True}
            )
            
        except Exception as e:
            logger.error(f"Stem processing failed: {str(e)}")
            raise AudioProcessingError(f"Stem processing error: {str(e)}")
    
    def _apply_eq_curve(self, audio: np.ndarray, eq_curve: List[Tuple[float, float]]) -> np.ndarray:
        """Apply EQ curve to audio."""



        try:
            processed = audio.copy()
            
            for freq, gain_db in eq_curve:
                # Apply parametric EQ for each frequency/gain pair
                w0 = 2 * np.pi * freq / self.config.sample_rate
                alpha = np.sin(w0) / (2 * 0.7)  # Q factor of 0.7
                A = 10 ** (gain_db / 40)
                
                # Bell filter coefficients
                b0 = 1 + alpha * A
                b1 = -2 * np.cos(w0) 
                b2 = 1 - alpha * A
                a0 = 1 + alpha / A
                a1 = -2 * np.cos(w0)
                a2 = 1 - alpha / A
                
                # Normalize and apply
                b = np.array([b0, b1, b2]) / a0
                a = np.array([1, a1, a2]) / a0
                
                processed = signal.filtfilt(b, a, processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"EQ curve application failed: {str(e)}")
            return audio
    
    def _apply_compression(self, audio: np.ndarray, ratio: float, threshold: float) -> np.ndarray:
        """Apply compression with attack/release characteristics."""



        try:
            threshold_linear = 10 ** (threshold / 20)
            
            # Envelope following
            envelope = self._calculate_envelope(audio)
            
            # Apply compression curve
            compressed_envelope = np.where(
                envelope > threshold_linear,
                threshold_linear * (envelope / threshold_linear) ** (1 / ratio),
                envelope
            )
            
            # Calculate gain reduction
            gain_reduction = np.where(
                envelope > 0,
                compressed_envelope / envelope,
                1.0
            )
            
            # Apply gain reduction
            compressed = audio * gain_reduction
            
            return compressed
            
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}")
            return audio
    
    def _calculate_envelope(self, audio: np.ndarray) -> np.ndarray:
        """Calculate audio envelope for dynamics processing."""



        try:
            # Hilbert transform for envelope detection
            analytic_signal = signal.hilbert(audio)
            envelope = np.abs(analytic_signal)
            
            # Smooth envelope
            envelope = signal.savgol_filter(envelope, 51, 3)
            
            return envelope
            
        except Exception as e:
            logger.error(f"Envelope calculation failed: {str(e)}")
            return np.abs(audio)
    
    def _apply_deesser(self, audio: np.ndarray, frequency: float, threshold: float) -> np.ndarray:
        """Apply de-esser for vocal processing."""



        try:
            # Create band-pass filter for sibilant frequencies
            sos = signal.butter(4, [frequency * 0.7, frequency * 1.5], 
                              btype='band', fs=self.config.sample_rate)
            
            # Extract sibilant content
            sibilant = signal.sosfilt(sos, audio)
            
            # Detect sibilance level
            envelope = self._calculate_envelope(sibilant)
            threshold_linear = 10 ** (threshold / 20)
            
            # Create gain reduction curve
            reduction = np.where(
                envelope > threshold_linear,
                threshold_linear / envelope,
                1.0
            )
            
            # Apply reduction only to sibilant frequencies
            reduced_sibilant = sibilant * reduction
            
            # Reconstruct audio
            deessed = audio - sibilant + reduced_sibilant
            
            return deessed
            
        except Exception as e:
            logger.error(f"De-essing failed: {str(e)}")
            return audio
    
    def _apply_gate(self, audio: np.ndarray, threshold: float, ratio: float) -> np.ndarray:
        """Apply noise gate for drums."""



        try:
            threshold_linear = 10 ** (threshold / 20)
            envelope = self._calculate_envelope(audio)
            
            # Create gate curve
            gate_curve = np.where(
                envelope > threshold_linear,
                1.0,
                (envelope / threshold_linear) ** (1 / ratio)
            )
            
            # Apply gating
            gated = audio * gate_curve
            
            return gated
            
        except Exception as e:
            logger.error(f"Gating failed: {str(e)}")
            return audio
    
    def _apply_saturation(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Apply harmonic saturation for bass."""



        try:
            # Soft clipping saturation
            drive = 1 + amount * 5  # Scale amount
            saturated = np.tanh(audio * drive) / drive
            
            # Blend with original
            result = (1 - amount) * audio + amount * saturated
            
            return result
            
        except Exception as e:
            logger.error(f"Saturation failed: {str(e)}")
            return audio
    
    def _calculate_stem_quality(self, original: np.ndarray, processed: np.ndarray, 
                               stem_type: str) -> Dict[str, float]:
        """Calculate quality metrics specific to stem type."""



        try:
            metrics = {}
            
            # Common metrics
            snr = self._calculate_snr(original, processed)
            metrics["snr_db"] = snr
            
            # Stem-specific metrics
            if stem_type == "vocals":
                clarity = self._calculate_vocal_clarity(processed)
                metrics["vocal_clarity"] = clarity
                
            elif stem_type == "drums":
                punch = self._calculate_drum_punch(processed)
                metrics["drum_punch"] = punch
                
            elif stem_type == "bass":
                tightness = self._calculate_bass_tightness(processed)
                metrics["bass_tightness"] = tightness
            
            # Overall quality
            metrics["overall_quality"] = min(1.0, max(0.0, (snr + 20) / 40))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality calculation failed: {str(e)}")
            return {"overall_quality": 0.5}
    
    def _calculate_snr(self, original: np.ndarray, processed: np.ndarray) -> float:
        """Calculate signal-to-noise ratio."""



        try:
            min_len = min(len(original), len(processed))
            orig = original[:min_len]
            proc = processed[:min_len]
            
            signal_power = np.mean(orig ** 2)
            noise_power = np.mean((orig - proc) ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                return float(snr)
            
            return 100.0  # Perfect case
            
        except:
            return 20.0  # Default
    
    def _calculate_vocal_clarity(self, audio: np.ndarray) -> float:
        """Calculate vocal clarity metric."""



        try:
            # Focus on presence frequencies (2-5 kHz)
            sos = signal.butter(4, [2000, 5000], btype='band', fs=self.config.sample_rate)
            presence = signal.sosfilt(sos, audio)
            
            presence_energy = np.mean(presence ** 2)
            total_energy = np.mean(audio ** 2)
            
            if total_energy > 0:
                clarity = presence_energy / total_energy
                return min(1.0, clarity * 3)  # Scale appropriately
            
            return 0.5
            
        except:
            return 0.5
    
    def _calculate_drum_punch(self, audio: np.ndarray) -> float:
        """Calculate drum punch metric."""



        try:
            # Analyze transient content
            diff = np.diff(audio)
            transient_energy = np.mean(diff ** 2)
            total_energy = np.mean(audio ** 2)
            
            if total_energy > 0:
                punch = transient_energy / total_energy
                return min(1.0, punch * 10)  # Scale appropriately
            
            return 0.5
            
        except:
            return 0.5
    
    def _calculate_bass_tightness(self, audio: np.ndarray) -> float:
        """Calculate bass tightness metric."""



        try:
            # Focus on low frequencies
            sos = signal.butter(4, 150, btype='low', fs=self.config.sample_rate)
            bass = signal.sosfilt(sos, audio)
            
            # Calculate phase coherence
            analytic = signal.hilbert(bass)
            phase = np.angle(analytic)
            phase_diff = np.diff(phase)
            
            # Unwrap phase and calculate stability
            phase_unwrapped = np.unwrap(phase_diff)
            phase_variance = np.var(phase_unwrapped)
            
            tightness = max(0.0, 1.0 - phase_variance / (np.pi ** 2))
            return min(1.0, tightness)
            
        except:
            return 0.5


class QualityAnalyzer(BaseProcessor):
    """Advanced quality analyzer for separated audio."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self.analysis_bands = self._setup_analysis_bands()
        
    def _setup_analysis_bands(self) -> List[Tuple[float, float]]:
        """Setup frequency bands for analysis."""



        return [
            (20, 60),      # Sub-bass
            (60, 250),     # Bass
            (250, 500),    # Low-mid
            (500, 2000),   # Mid
            (2000, 4000),  # Upper-mid
            (4000, 8000),  # Presence
            (8000, 16000), # Brilliance
            (16000, 22050) # Air
        ]
    
    async def process(self, stems: Dict[str, np.ndarray], 
                     reference: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Perform comprehensive quality analysis."""
        analysis_results = {}
        
        for stem_name, stem_audio in stems.items():
            try:
                stem_analysis = await self._analyze_stem_quality(stem_audio, stem_name)
                analysis_results[stem_name] = stem_analysis
                
            except Exception as e:
                logger.error(f"Quality analysis failed for {stem_name}: {str(e)}")
                analysis_results[stem_name] = {
                    "overall_score": 0.0,
                    "error": str(e)
                }
        
        # Overall separation quality
        if reference is not None:
            overall_quality = await self._analyze_separation_quality(stems, reference)
            analysis_results["separation_quality"] = overall_quality
        
        return analysis_results
    
    async def _analyze_stem_quality(self, audio: np.ndarray, stem_name: str) -> Dict[str, Any]:
        """Analyze quality of individual stem."""



        try:
            results = {
                "frequency_analysis": self._analyze_frequency_content(audio),
                "dynamics_analysis": self._analyze_dynamics(audio),
                "spectral_analysis": self._analyze_spectral_characteristics(audio),
                "artifacts_analysis": self._detect_artifacts(audio),
                "temporal_analysis": self._analyze_temporal_characteristics(audio)
            }
            
            # Calculate overall score
            results["overall_score"] = self._calculate_stem_score(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Stem quality analysis failed: {str(e)}")
            return {"overall_score": 0.0, "error": str(e)}
    
    def _analyze_frequency_content(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze frequency content distribution."""



        try:
            # Calculate power spectral density
            freqs, psd = signal.welch(audio, fs=self.config.sample_rate, nperseg=2048)
            
            band_energies = {}
            total_energy = np.sum(psd)
            
            for i, (low, high) in enumerate(self.analysis_bands):
                band_mask = (freqs >= low) & (freqs < high)
                band_energy = np.sum(psd[band_mask])
                
                if total_energy > 0:
                    band_energies[f"band_{i+1}_{low}_{high}Hz"] = band_energy / total_energy
                else:
                    band_energies[f"band_{i+1}_{low}_{high}Hz"] = 0.0
            
            # Calculate spectral centroid and spread
            spectral_centroid = np.sum(freqs * psd) / total_energy if total_energy > 0 else 0
            spectral_spread = np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * psd) / total_energy) if total_energy > 0 else 0
            
            return {
                **band_energies,
                "spectral_centroid_hz": float(spectral_centroid),
                "spectral_spread_hz": float(spectral_spread),
                "frequency_flatness": self._calculate_spectral_flatness(psd)
            }
            
        except Exception as e:
            logger.error(f"Frequency analysis failed: {str(e)}")
            return {}
    
    def _analyze_dynamics(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze dynamic characteristics."""



        try:
            # RMS and peak analysis
            rms = np.sqrt(np.mean(audio ** 2))
            peak = np.max(np.abs(audio))
            crest_factor = peak / rms if rms > 0 else 0
            
            # Dynamic range over time
            window_size = int(0.1 * self.config.sample_rate)
            rms_windows = []
            
            for i in range(0, len(audio) - window_size, window_size // 2):
                window_rms = np.sqrt(np.mean(audio[i:i + window_size] ** 2))
                if window_rms > 0:
                    rms_windows.append(20 * np.log10(window_rms))
            
            dynamic_range = max(rms_windows) - min(rms_windows) if rms_windows else 0
            
            # Loudness analysis
            try:
                if audio.ndim == 1:
                    loudness_audio = audio.reshape(-1, 1)
                else:
                    loudness_audio = audio
                    
                integrated_loudness = self.loudness_meter.integrated_loudness(loudness_audio)
                momentary_loudness = self._calculate_momentary_loudness(loudness_audio)
            except:
                integrated_loudness = -23.0
                momentary_loudness = -23.0
            
            return {
                "rms_db": 20 * np.log10(rms) if rms > 0 else -100,
                "peak_db": 20 * np.log10(peak) if peak > 0 else -100,
                "crest_factor_db": 20 * np.log10(crest_factor) if crest_factor > 0 else -100,
                "dynamic_range_db": dynamic_range,
                "integrated_loudness_lufs": float(integrated_loudness),
                "momentary_loudness_lufs": float(momentary_loudness)
            }
            
        except Exception as e:
            logger.error(f"Dynamics analysis failed: {str(e)}")
            return {}
    
    def _analyze_spectral_characteristics(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze spectral characteristics."""



        try:
            # STFT analysis
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            
            # Spectral features
            spectral_rolloff = librosa.feature.spectral_rolloff(S=magnitude ** 2, sr=self.config.sample_rate)
            spectral_flux = np.mean(np.diff(magnitude, axis=1) ** 2)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)
            
            # Harmonic-percussive separation
            harmonic, percussive = librosa.effects.hpss(audio)
            harmonic_ratio = np.mean(harmonic ** 2) / np.mean(audio ** 2) if np.mean(audio ** 2) > 0 else 0
            
            return {
                "spectral_rolloff_hz": float(np.mean(spectral_rolloff)),
                "spectral_flux": float(spectral_flux),
                "zero_crossing_rate": float(np.mean(zero_crossing_rate)),
                "harmonic_ratio": float(harmonic_ratio),
                "percussive_ratio": float(1 - harmonic_ratio)
            }
            
        except Exception as e:
            logger.error(f"Spectral analysis failed: {str(e)}")
            return {}
    
    def _detect_artifacts(self, audio: np.ndarray) -> Dict[str, float]:
        """Detect processing artifacts."""



        try:
            artifacts = {}
            
            # Clipping detection
            clipping_ratio = np.mean(np.abs(audio) > 0.95)
            artifacts["clipping_ratio"] = float(clipping_ratio)
            
            # Aliasing detection (high frequency content analysis)
            nyquist = self.config.sample_rate / 2
            high_freq_threshold = 0.8 * nyquist
            
            freqs, psd = signal.welch(audio, fs=self.config.sample_rate, nperseg=2048)
            high_freq_mask = freqs > high_freq_threshold
            high_freq_energy = np.sum(psd[high_freq_mask])
            total_energy = np.sum(psd)
            
            aliasing_indicator = high_freq_energy / total_energy if total_energy > 0 else 0
            artifacts["aliasing_indicator"] = float(aliasing_indicator)
            
            # DC offset detection
            dc_offset = np.abs(np.mean(audio))
            artifacts["dc_offset"] = float(dc_offset)
            
            # Sudden level changes (potential clicks/pops)
            diff = np.abs(np.diff(audio))
            click_threshold = np.percentile(diff, 99.9)
            click_count = np.sum(diff > click_threshold)
            artifacts["click_density"] = float(click_count / len(audio))
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Artifact detection failed: {str(e)}")
            return {}
    
    def _analyze_temporal_characteristics(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze temporal characteristics."""



        try:
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=audio, sr=self.config.sample_rate)
            onset_density = len(onset_frames) / (len(audio) / self.config.sample_rate)
            
            # Tempo analysis
            try:
                tempo, _ = librosa.beat.beat_track(y=audio, sr=self.config.sample_rate)
                tempo = float(tempo)
            except:
                tempo = 0.0
            
            # Autocorrelation for periodicity
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr) // 2:]
            
            # Find periodicity strength
            if len(autocorr) > 1:
                periodicity = np.max(autocorr[1:]) / autocorr[0] if autocorr[0] > 0 else 0
            else:
                periodicity = 0
            
            return {
                "onset_density": float(onset_density),
                "estimated_tempo_bpm": tempo,
                "periodicity_strength": float(periodicity)
            }
            
        except Exception as e:
            logger.error(f"Temporal analysis failed: {str(e)}")
            return {}
    
    def _calculate_spectral_flatness(self, psd: np.ndarray) -> float:
        """Calculate spectral flatness (Wiener entropy)."""



        try:
            # Avoid log(0) issues
            psd_safe = psd + 1e-10
            
            # Geometric and arithmetic means
            geometric_mean = np.exp(np.mean(np.log(psd_safe)))
            arithmetic_mean = np.mean(psd_safe)
            
            if arithmetic_mean > 0:
                flatness = geometric_mean / arithmetic_mean
                return float(flatness)
            
            return 0.0
            
        except:
            return 0.0
    
    def _calculate_momentary_loudness(self, audio: np.ndarray) -> float:
        """Calculate momentary loudness."""



        try:
            # Use 400ms window for momentary loudness
            window_samples = int(0.4 * self.config.sample_rate)
            
            if len(audio) < window_samples:
                return self.loudness_meter.integrated_loudness(audio)
            
            # Take center portion
            start_idx = (len(audio) - window_samples) // 2
            window_audio = audio[start_idx:start_idx + window_samples]
            
            momentary = self.loudness_meter.integrated_loudness(window_audio)
            return momentary
            
        except:
            return -23.0  # Default LUFS value
    
    def _calculate_stem_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall stem quality score."""



        try:
            scores = []
            
            # Frequency analysis score
            freq_analysis = analysis_results.get("frequency_analysis", {})
            if "frequency_flatness" in freq_analysis:
                freq_score = freq_analysis["frequency_flatness"]
                scores.append(freq_score * 0.25)
            
            # Dynamics score
            dynamics = analysis_results.get("dynamics_analysis", {})
            if "dynamic_range_db" in dynamics:
                dynamic_range = dynamics["dynamic_range_db"]
                dynamic_score = min(1.0, max(0.0, dynamic_range / 30))
                scores.append(dynamic_score * 0.25)
            
            # Artifact score (inverted - fewer artifacts = better)
            artifacts = analysis_results.get("artifacts_analysis", {})
            artifact_score = 1.0
            if "clipping_ratio" in artifacts:
                artifact_score *= (1.0 - artifacts["clipping_ratio"])
            if "aliasing_indicator" in artifacts:
                artifact_score *= (1.0 - min(1.0, artifacts["aliasing_indicator"] * 10))
            scores.append(artifact_score * 0.3)
            
            # Spectral characteristics score
            spectral = analysis_results.get("spectral_analysis", {})
            if "harmonic_ratio" in spectral:
                # Balanced harmonic/percussive content is good
                balance = 1.0 - abs(spectral["harmonic_ratio"] - 0.5) * 2
                scores.append(balance * 0.2)
            
            # Calculate weighted average
            if scores:
                total_score = sum(scores)
                return max(0.0, min(1.0, total_score))
            
            return 0.5  # Default score
            
        except Exception as e:
            logger.error(f"Score calculation failed: {str(e)}")
            return 0.5
    
    async def _analyze_separation_quality(self, stems: Dict[str, np.ndarray], 
                                        reference: np.ndarray) -> Dict[str, float]:
        """Analyze overall separation quality."""



        try:
            # Reconstruct sum from stems
            reconstructed = np.zeros_like(reference)
            for stem_audio in stems.values():
                if len(stem_audio) == len(reconstructed):
                    reconstructed += stem_audio
                else:
                    # Handle length mismatch
                    min_len = min(len(stem_audio), len(reconstructed))
                    reconstructed[:min_len] += stem_audio[:min_len]
            
            # Calculate reconstruction metrics
            reconstruction_error = np.mean((reference - reconstructed) ** 2)
            reference_power = np.mean(reference ** 2)
            
            if reference_power > 0:
                reconstruction_snr = 10 * np.log10(reference_power / (reconstruction_error + 1e-10))
            else:
                reconstruction_snr = 0
            
            # Cross-contamination analysis
            contamination_scores = {}
            stem_names = list(stems.keys())
            
            for i, stem1_name in enumerate(stem_names):
                for j, stem2_name in enumerate(stem_names[i+1:], i+1):
                    stem1 = stems[stem1_name]
                    stem2 = stems[stem2_name]
                    
                    # Calculate cross-correlation
                    min_len = min(len(stem1), len(stem2))
                    correlation = np.corrcoef(stem1[:min_len], stem2[:min_len])[0, 1]
                    
                    if not np.isnan(correlation):
                        contamination_scores[f"{stem1_name}_{stem2_name}_correlation"] = abs(correlation)
            
            # Overall separation quality
            reconstruction_score = max(0, min(1, (reconstruction_snr + 10) / 40))
            contamination_score = 1.0 - np.mean(list(contamination_scores.values())) if contamination_scores else 1.0
            
            overall_quality = 0.6 * reconstruction_score + 0.4 * contamination_score
            
            return {
                "reconstruction_snr_db": float(reconstruction_snr),
                "reconstruction_score": float(reconstruction_score),
                "contamination_score": float(contamination_score),
                "cross_contamination": contamination_scores,
                "overall_separation_quality": float(overall_quality)
            }
            
        except Exception as e:
            logger.error(f"Separation quality analysis failed: {str(e)}")
            return {"overall_separation_quality": 0.0, "error": str(e)}
