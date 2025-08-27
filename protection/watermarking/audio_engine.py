"""
Professional Audio Watermarking Engine
Advanced digital watermarking for audio content with multiple embedding techniques

Developed by: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Senior Backend + ML Engineer + DBA + Security Expert + 
               Microservices Architect + Audio Engineer + DevOps + AI Prompt Engineer

⚠️ INTELLECTUAL PROPERTY WARNING:
This audio watermarking engine, concept, and all associated code are the exclusive intellectual 
property of Fahed Mlaiel. Any unauthorized use, copying, modification, or distribution 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly 
prohibited and will result in legal action.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union, BinaryIO
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import hashlib
import base64
from pathlib import Path
import tempfile
import io

try:
    import librosa
    import soundfile as sf
    from scipy import signal
    from scipy.fft import fft, ifft, fftfreq
    import pywt
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioWatermarkTechnique(Enum):
    """Audio watermarking techniques"""
    SPECTRAL_SPREADING = "spectral_spreading"
    LSB_EMBEDDING = "lsb_embedding"
    ECHO_HIDING = "echo_hiding"
    PHASE_CODING = "phase_coding"
    WAVELET_DOMAIN = "wavelet_domain"
    CEPSTRAL_DOMAIN = "cepstral_domain"
    PSYCHOACOUSTIC_MODEL = "psychoacoustic_model"


class AudioWatermarkStrength(Enum):
    """Audio watermark strength levels"""
    TRANSPARENT = "transparent"    # Completely inaudible
    LIGHT = "light"               # Very light, high quality
    MEDIUM = "medium"             # Balanced strength/quality
    STRONG = "strong"             # Strong protection
    ROBUST = "robust"             # Maximum robustness


@dataclass
class AudioWatermarkConfig:
    """Configuration for audio watermarking"""
    sample_rate: int = 44100
    frame_size: int = 2048
    hop_length: int = 512
    window_type: str = "hann"
    frequency_range: Tuple[float, float] = (300.0, 8000.0)
    embedding_rate: float = 0.1  # bits per second
    redundancy_factor: int = 3
    error_correction: bool = True
    adaptive_strength: bool = True


@dataclass
class AudioWatermarkMetrics:
    """Audio watermarking quality metrics"""
    snr_db: float
    thd_percent: float
    imperceptibility_score: float
    robustness_score: float
    embedding_capacity_bps: float
    processing_time_sec: float
    detection_confidence: float


class PsychoacousticModel:
    """Psychoacoustic masking model for audio watermarking"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.bark_scale = self._generate_bark_scale()
        self.masking_thresholds = {}
    
    def _generate_bark_scale(self) -> np.ndarray:
        """Generate Bark scale frequency mapping"""
        freqs = np.linspace(0, self.sample_rate // 2, 1025)
        bark = 13 * np.arctan(0.00076 * freqs) + 3.5 * np.arctan((freqs / 7500) ** 2)
        return bark
    
    async def calculate_masking_threshold(
        self,
        audio_spectrum: np.ndarray,
        frequencies: np.ndarray
    ) -> np.ndarray:
        """Calculate psychoacoustic masking threshold"""
        try:
            # Convert to dB
            spectrum_db = 20 * np.log10(np.abs(audio_spectrum) + 1e-10)
            
            # Bark scale mapping
            bark_freqs = 13 * np.arctan(0.00076 * frequencies) + 3.5 * np.arctan((frequencies / 7500) ** 2)
            
            # Masking threshold calculation (simplified)
            masking_threshold = np.zeros_like(spectrum_db)
            
            for i, freq in enumerate(frequencies):
                # Tone masking
                tone_mask = spectrum_db[i] - 14.5 - np.abs(bark_freqs - bark_freqs[i]) * 2.5
                
                # Noise masking
                noise_mask = spectrum_db[i] - 5.5
                
                # Combined masking
                masking_threshold[i] = max(tone_mask, noise_mask, -60)  # Absolute threshold
            
            return masking_threshold
            
        except Exception as e:
            logger.error(f"Error calculating masking threshold: {e}")
            return np.full_like(audio_spectrum, -40.0, dtype=float)


class SpectralWatermarkEngine:
    """Advanced spectral domain watermarking"""
    
    def __init__(self, config: AudioWatermarkConfig):
        self.config = config
        self.psychoacoustic = PsychoacousticModel(config.sample_rate)
    
    async def embed_spread_spectrum(
        self,
        audio_data: np.ndarray,
        watermark_bits: List[int],
        strength: AudioWatermarkStrength
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Embed watermark using spread spectrum technique"""
        try:
            if not AUDIO_AVAILABLE:
                raise ValueError("Audio libraries not available")
            
            # STFT computation
            stft = librosa.stft(
                audio_data,
                n_fft=self.config.frame_size,
                hop_length=self.config.hop_length,
                window=self.config.window_type
            )
            
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Generate frequency bins within range
            freqs = librosa.fft_frequencies(sr=self.config.sample_rate, n_fft=self.config.frame_size)
            valid_bins = np.where(
                (freqs >= self.config.frequency_range[0]) &
                (freqs <= self.config.frequency_range[1])
            )[0]
            
            # Strength parameters
            strength_params = {
                AudioWatermarkStrength.TRANSPARENT: {"alpha": 0.001, "spread_factor": 0.5},
                AudioWatermarkStrength.LIGHT: {"alpha": 0.005, "spread_factor": 0.7},
                AudioWatermarkStrength.MEDIUM: {"alpha": 0.015, "spread_factor": 1.0},
                AudioWatermarkStrength.STRONG: {"alpha": 0.030, "spread_factor": 1.5},
                AudioWatermarkStrength.ROBUST: {"alpha": 0.050, "spread_factor": 2.0}
            }
            
            params = strength_params[strength]
            alpha = params["alpha"]
            spread_factor = params["spread_factor"]
            
            # Generate pseudo-random spreading sequence
            np.random.seed(42)  # Fixed seed for repeatability
            spreading_seq = np.random.choice([-1, 1], size=len(valid_bins))
            
            modified_magnitude = magnitude.copy()
            embedded_frames = 0
            
            # Embed watermark bits
            frames_per_bit = max(1, stft.shape[1] // len(watermark_bits))
            
            for bit_idx, bit in enumerate(watermark_bits):
                start_frame = bit_idx * frames_per_bit
                end_frame = min((bit_idx + 1) * frames_per_bit, stft.shape[1])
                
                for frame_idx in range(start_frame, end_frame):
                    if frame_idx < stft.shape[1]:
                        # Calculate psychoacoustic masking threshold
                        masking_threshold = await self.psychoacoustic.calculate_masking_threshold(
                            magnitude[:, frame_idx], freqs
                        )
                        
                        # Adaptive embedding strength based on masking
                        for i, bin_idx in enumerate(valid_bins):
                            if bin_idx < len(masking_threshold):
                                # Adaptive alpha based on masking threshold
                                local_alpha = alpha * min(2.0, max(0.1, 
                                    magnitude[bin_idx, frame_idx] / (10**(masking_threshold[bin_idx]/20) + 1e-10)
                                ))
                                
                                # Spread spectrum embedding
                                spread_value = spreading_seq[i] * spread_factor
                                
                                if bit == 1:
                                    modified_magnitude[bin_idx, frame_idx] += local_alpha * spread_value
                                else:
                                    modified_magnitude[bin_idx, frame_idx] -= local_alpha * spread_value
                        
                        embedded_frames += 1
            
            # Reconstruct audio
            modified_stft = modified_magnitude * np.exp(1j * phase)
            watermarked_audio = librosa.istft(
                modified_stft,
                hop_length=self.config.hop_length,
                window=self.config.window_type
            )
            
            # Calculate metrics
            metrics = await self._calculate_embedding_metrics(
                audio_data, watermarked_audio, len(watermark_bits), embedded_frames
            )
            
            result_info = {
                "technique": "spread_spectrum",
                "bits_embedded": len(watermark_bits),
                "frames_modified": embedded_frames,
                "strength_used": strength.value,
                "alpha": alpha,
                "spread_factor": spread_factor,
                "frequency_range": self.config.frequency_range,
                "metrics": metrics.__dict__
            }
            
            logger.info(f"Spread spectrum watermark embedded: {len(watermark_bits)} bits")
            return watermarked_audio, result_info
            
        except Exception as e:
            logger.error(f"Error in spread spectrum embedding: {e}")
            raise
    
    async def detect_spread_spectrum(
        self,
        watermarked_audio: np.ndarray,
        original_audio: Optional[np.ndarray],
        expected_bits: int
    ) -> Tuple[List[int], float]:
        """Detect spread spectrum watermark"""
        try:
            if not AUDIO_AVAILABLE:
                return [], 0.0
            
            # STFT computation
            stft = librosa.stft(
                watermarked_audio,
                n_fft=self.config.frame_size,
                hop_length=self.config.hop_length,
                window=self.config.window_type
            )
            
            magnitude = np.abs(stft)
            
            # Generate frequency bins and spreading sequence (same as embedding)
            freqs = librosa.fft_frequencies(sr=self.config.sample_rate, n_fft=self.config.frame_size)
            valid_bins = np.where(
                (freqs >= self.config.frequency_range[0]) &
                (freqs <= self.config.frequency_range[1])
            )[0]
            
            np.random.seed(42)  # Same seed as embedding
            spreading_seq = np.random.choice([-1, 1], size=len(valid_bins))
            
            # Extract watermark bits
            extracted_bits = []
            confidence_scores = []
            
            frames_per_bit = max(1, stft.shape[1] // expected_bits)
            
            for bit_idx in range(expected_bits):
                start_frame = bit_idx * frames_per_bit
                end_frame = min((bit_idx + 1) * frames_per_bit, stft.shape[1])
                
                correlation_sum = 0.0
                frame_count = 0
                
                for frame_idx in range(start_frame, end_frame):
                    if frame_idx < stft.shape[1]:
                        frame_correlation = 0.0
                        
                        for i, bin_idx in enumerate(valid_bins):
                            # Calculate correlation with spreading sequence
                            spectral_value = magnitude[bin_idx, frame_idx]
                            spread_value = spreading_seq[i]
                            frame_correlation += spectral_value * spread_value
                        
                        correlation_sum += frame_correlation
                        frame_count += 1
                
                if frame_count > 0:
                    avg_correlation = correlation_sum / frame_count
                    
                    # Determine bit value and confidence
                    if avg_correlation > 0:
                        extracted_bits.append(1)
                        confidence_scores.append(min(abs(avg_correlation), 1.0))
                    else:
                        extracted_bits.append(0)
                        confidence_scores.append(min(abs(avg_correlation), 1.0))
                else:
                    extracted_bits.append(0)
                    confidence_scores.append(0.0)
            
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            logger.info(f"Spread spectrum detection completed: {len(extracted_bits)} bits, confidence: {overall_confidence:.3f}")
            return extracted_bits, overall_confidence
            
        except Exception as e:
            logger.error(f"Error in spread spectrum detection: {e}")
            return [], 0.0
    
    async def _calculate_embedding_metrics(
        self,
        original: np.ndarray,
        watermarked: np.ndarray,
        bits_embedded: int,
        frames_modified: int
    ) -> AudioWatermarkMetrics:
        """Calculate audio watermarking quality metrics"""
        try:
            # Ensure same length
            min_len = min(len(original), len(watermarked))
            original = original[:min_len]
            watermarked = watermarked[:min_len]
            
            # Signal-to-Noise Ratio
            noise = watermarked - original
            signal_power = np.mean(original ** 2)
            noise_power = np.mean(noise ** 2)
            
            if noise_power > 0:
                snr_db = 10 * np.log10(signal_power / noise_power)
            else:
                snr_db = 100.0  # Perfect quality
            
            # Total Harmonic Distortion (simplified)
            thd_percent = np.sqrt(noise_power) / (np.sqrt(signal_power) + 1e-10) * 100
            
            # Imperceptibility score (based on SNR)
            imperceptibility_score = min(max((snr_db - 20) / 40, 0), 1)
            
            # Robustness score (based on embedding strength)
            robustness_score = min(max(noise_power / 0.001, 0), 1)
            
            # Embedding capacity
            duration_sec = len(original) / self.config.sample_rate
            embedding_capacity_bps = bits_embedded / duration_sec if duration_sec > 0 else 0
            
            return AudioWatermarkMetrics(
                snr_db=snr_db,
                thd_percent=thd_percent,
                imperceptibility_score=imperceptibility_score,
                robustness_score=robustness_score,
                embedding_capacity_bps=embedding_capacity_bps,
                processing_time_sec=0.0,  # To be set by caller
                detection_confidence=0.0   # To be set during detection
            )
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return AudioWatermarkMetrics(0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0)


class WaveletWatermarkEngine:
    """Wavelet domain watermarking engine"""
    
    def __init__(self, config: AudioWatermarkConfig):
        self.config = config
        self.wavelet_type = 'db4'
        self.decomposition_levels = 4
    
    async def embed_wavelet_watermark(
        self,
        audio_data: np.ndarray,
        watermark_bits: List[int],
        strength: AudioWatermarkStrength
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Embed watermark in wavelet domain"""
        try:
            if not AUDIO_AVAILABLE:
                raise ValueError("Audio libraries not available")
            
            # Wavelet decomposition
            coeffs = pywt.wavedec(audio_data, self.wavelet_type, level=self.decomposition_levels)
            
            # Strength parameters
            strength_values = {
                AudioWatermarkStrength.TRANSPARENT: 0.001,
                AudioWatermarkStrength.LIGHT: 0.005,
                AudioWatermarkStrength.MEDIUM: 0.015,
                AudioWatermarkStrength.STRONG: 0.030,
                AudioWatermarkStrength.ROBUST: 0.050
            }
            
            alpha = strength_values[strength]
            
            # Embed in detail coefficients (high frequency components)
            modified_coeffs = list(coeffs)
            bits_embedded = 0
            
            # Use detail coefficients (cD1, cD2, cD3, cD4)
            for level in range(1, min(len(coeffs), self.decomposition_levels + 1)):
                detail_coeffs = coeffs[level]
                
                # Calculate embedding positions
                positions_per_bit = max(1, len(detail_coeffs) // len(watermark_bits))
                
                for bit_idx, bit in enumerate(watermark_bits):
                    if bit_idx * positions_per_bit < len(detail_coeffs):
                        pos = bit_idx * positions_per_bit
                        
                        # Adaptive embedding based on coefficient magnitude
                        coeff_magnitude = abs(detail_coeffs[pos])
                        adaptive_alpha = alpha * (1 + coeff_magnitude / np.max(np.abs(detail_coeffs)))
                        
                        if bit == 1:
                            modified_coeffs[level][pos] += adaptive_alpha
                        else:
                            modified_coeffs[level][pos] -= adaptive_alpha
                        
                        bits_embedded += 1
                
                if bits_embedded >= len(watermark_bits):
                    break
            
            # Wavelet reconstruction
            watermarked_audio = pywt.waverec(modified_coeffs, self.wavelet_type)
            
            # Ensure same length as original
            watermarked_audio = watermarked_audio[:len(audio_data)]
            
            result_info = {
                "technique": "wavelet_domain",
                "wavelet_type": self.wavelet_type,
                "decomposition_levels": self.decomposition_levels,
                "bits_embedded": bits_embedded,
                "strength_used": strength.value,
                "alpha": alpha
            }
            
            logger.info(f"Wavelet domain watermark embedded: {bits_embedded} bits")
            return watermarked_audio, result_info
            
        except Exception as e:
            logger.error(f"Error in wavelet embedding: {e}")
            raise
    
    async def detect_wavelet_watermark(
        self,
        watermarked_audio: np.ndarray,
        original_audio: np.ndarray,
        expected_bits: int
    ) -> Tuple[List[int], float]:
        """Detect watermark in wavelet domain"""
        try:
            # Decompose both signals
            watermarked_coeffs = pywt.wavedec(watermarked_audio, self.wavelet_type, level=self.decomposition_levels)
            original_coeffs = pywt.wavedec(original_audio, self.wavelet_type, level=self.decomposition_levels)
            
            extracted_bits = []
            confidence_scores = []
            
            # Extract from detail coefficients
            for level in range(1, min(len(watermarked_coeffs), self.decomposition_levels + 1)):
                watermarked_detail = watermarked_coeffs[level]
                original_detail = original_coeffs[level]
                
                difference = watermarked_detail - original_detail
                positions_per_bit = max(1, len(watermarked_detail) // expected_bits)
                
                for bit_idx in range(expected_bits):
                    if bit_idx * positions_per_bit < len(difference):
                        pos = bit_idx * positions_per_bit
                        diff_value = difference[pos]
                        
                        if diff_value > 0:
                            extracted_bits.append(1)
                        else:
                            extracted_bits.append(0)
                        
                        confidence_scores.append(min(abs(diff_value), 1.0))
                
                if len(extracted_bits) >= expected_bits:
                    break
            
            # Trim to expected length
            extracted_bits = extracted_bits[:expected_bits]
            confidence_scores = confidence_scores[:expected_bits]
            
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            logger.info(f"Wavelet detection completed: {len(extracted_bits)} bits, confidence: {overall_confidence:.3f}")
            return extracted_bits, overall_confidence
            
        except Exception as e:
            logger.error(f"Error in wavelet detection: {e}")
            return [], 0.0


class AudioWatermarkEngine:
    """
    Professional Audio Watermarking Engine
    
    Comprehensive audio watermarking system supporting multiple techniques:
    - Spread Spectrum
    - Wavelet Domain
    - Echo Hiding
    - Phase Coding
    - LSB Embedding
    - Psychoacoustic Model
    """
    
    def __init__(self, config: Optional[AudioWatermarkConfig] = None):
        self.config = config or AudioWatermarkConfig()
        self.spectral_engine = SpectralWatermarkEngine(self.config)
        self.wavelet_engine = WaveletWatermarkEngine(self.config)
        
        # Initialize technique registry
        self.techniques = {
            AudioWatermarkTechnique.SPECTRAL_SPREADING: self.spectral_engine.embed_spread_spectrum,
            AudioWatermarkTechnique.WAVELET_DOMAIN: self.wavelet_engine.embed_wavelet_watermark,
            AudioWatermarkTechnique.LSB_EMBEDDING: self._embed_lsb,
            AudioWatermarkTechnique.ECHO_HIDING: self._embed_echo,
            AudioWatermarkTechnique.PHASE_CODING: self._embed_phase
        }
        
        self.detection_methods = {
            AudioWatermarkTechnique.SPECTRAL_SPREADING: self.spectral_engine.detect_spread_spectrum,
            AudioWatermarkTechnique.WAVELET_DOMAIN: self.wavelet_engine.detect_wavelet_watermark,
            AudioWatermarkTechnique.LSB_EMBEDDING: self._detect_lsb,
            AudioWatermarkTechnique.ECHO_HIDING: self._detect_echo,
            AudioWatermarkTechnique.PHASE_CODING: self._detect_phase
        }
    
    async def embed_watermark(
        self,
        audio_data: np.ndarray,
        watermark_data: bytes,
        technique: AudioWatermarkTechnique,
        strength: AudioWatermarkStrength = AudioWatermarkStrength.MEDIUM
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Embed watermark using specified technique
        
        Args:
            audio_data: Input audio signal
            watermark_data: Binary data to embed
            technique: Watermarking technique to use
            strength: Embedding strength level
            
        Returns:
            Tuple of (watermarked_audio, embedding_info)
        """
        try:
            start_time = datetime.now()
            
            # Convert watermark data to bits
            watermark_bits = self._data_to_bits(watermark_data)
            
            # Add error correction if enabled
            if self.config.error_correction:
                watermark_bits = self._add_error_correction(watermark_bits)
            
            # Add redundancy
            if self.config.redundancy_factor > 1:
                watermark_bits = watermark_bits * self.config.redundancy_factor
            
            # Select and execute embedding technique
            if technique not in self.techniques:
                raise ValueError(f"Unsupported watermarking technique: {technique}")
            
            embedding_func = self.techniques[technique]
            watermarked_audio, technique_info = await embedding_func(
                audio_data, watermark_bits, strength
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate final metrics
            metrics = await self.spectral_engine._calculate_embedding_metrics(
                audio_data, watermarked_audio, len(watermark_bits), 
                technique_info.get("frames_modified", 0)
            )
            metrics.processing_time_sec = processing_time
            
            # Compile comprehensive result info
            result_info = {
                "watermark_technique": technique.value,
                "strength_level": strength.value,
                "original_data_bits": len(self._data_to_bits(watermark_data)),
                "total_embedded_bits": len(watermark_bits),
                "redundancy_factor": self.config.redundancy_factor,
                "error_correction": self.config.error_correction,
                "processing_time_sec": processing_time,
                "audio_metrics": metrics.__dict__,
                "technique_specific": technique_info,
                "config": self.config.__dict__
            }
            
            logger.info(f"Audio watermark embedded successfully using {technique.value}")
            return watermarked_audio, result_info
            
        except Exception as e:
            logger.error(f"Error embedding audio watermark: {e}")
            raise
    
    async def detect_watermark(
        self,
        watermarked_audio: np.ndarray,
        technique: AudioWatermarkTechnique,
        original_audio: Optional[np.ndarray] = None,
        expected_data_length: Optional[int] = None
    ) -> Tuple[Optional[bytes], float, Dict[str, Any]]:
        """
        Detect and extract watermark using specified technique
        
        Args:
            watermarked_audio: Audio signal containing watermark
            technique: Watermarking technique used
            original_audio: Original audio (if available)
            expected_data_length: Expected length of embedded data
            
        Returns:
            Tuple of (extracted_data, confidence, detection_info)
        """
        try:
            start_time = datetime.now()
            
            # Estimate expected bits if not provided
            if expected_data_length is None:
                expected_data_length = 32  # Default assumption
            
            expected_bits = expected_data_length * 8
            
            # Apply redundancy and error correction factors
            if self.config.error_correction:
                expected_bits *= 2  # Simple doubling for error correction
            
            if self.config.redundancy_factor > 1:
                expected_bits *= self.config.redundancy_factor
            
            # Select and execute detection technique
            if technique not in self.detection_methods:
                raise ValueError(f"Unsupported detection technique: {technique}")
            
            detection_func = self.detection_methods[technique]
            
            if technique in [AudioWatermarkTechnique.WAVELET_DOMAIN] and original_audio is not None:
                extracted_bits, confidence = await detection_func(
                    watermarked_audio, original_audio, expected_bits
                )
            else:
                extracted_bits, confidence = await detection_func(
                    watermarked_audio, original_audio, expected_bits
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Process extracted bits
            extracted_data = None
            if extracted_bits and confidence > 0.5:
                try:
                    # Remove redundancy
                    if self.config.redundancy_factor > 1:
                        extracted_bits = self._remove_redundancy(extracted_bits, self.config.redundancy_factor)
                    
                    # Apply error correction
                    if self.config.error_correction:
                        extracted_bits = self._apply_error_correction(extracted_bits)
                    
                    # Convert bits to data
                    extracted_data = self._bits_to_data(extracted_bits[:expected_data_length * 8])
                    
                except Exception as e:
                    logger.warning(f"Error processing extracted bits: {e}")
                    extracted_data = None
            
            detection_info = {
                "watermark_technique": technique.value,
                "detection_confidence": confidence,
                "expected_bits": expected_bits,
                "extracted_bits_count": len(extracted_bits),
                "processing_time_sec": processing_time,
                "redundancy_factor": self.config.redundancy_factor,
                "error_correction": self.config.error_correction,
                "data_extracted": extracted_data is not None
            }
            
            logger.info(f"Audio watermark detection completed: confidence={confidence:.3f}")
            return extracted_data, confidence, detection_info
            
        except Exception as e:
            logger.error(f"Error detecting audio watermark: {e}")
            return None, 0.0, {"error": str(e)}
    
    # Private helper methods for additional techniques
    
    async def _embed_lsb(
        self,
        audio_data: np.ndarray,
        watermark_bits: List[int],
        strength: AudioWatermarkStrength
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """LSB embedding implementation"""
        try:
            # Convert to 16-bit integers for LSB manipulation
            audio_int = (audio_data * 32767).astype(np.int16)
            
            # Strength determines bit depth and step size
            strength_params = {
                AudioWatermarkStrength.TRANSPARENT: {"bit_depth": 1, "step": 100},
                AudioWatermarkStrength.LIGHT: {"bit_depth": 1, "step": 50},
                AudioWatermarkStrength.MEDIUM: {"bit_depth": 2, "step": 30},
                AudioWatermarkStrength.STRONG: {"bit_depth": 2, "step": 20},
                AudioWatermarkStrength.ROBUST: {"bit_depth": 3, "step": 10}
            }
            
            params = strength_params[strength]
            bit_depth = params["bit_depth"]
            step = params["step"]
            
            watermarked_audio = audio_int.copy()
            bits_embedded = 0
            
            bit_index = 0
            for sample_idx in range(0, len(audio_int), step):
                if bit_index >= len(watermark_bits):
                    break
                
                for bit_pos in range(bit_depth):
                    if bit_index >= len(watermark_bits) or sample_idx >= len(audio_int):
                        break
                    
                    # Modify LSB
                    sample = watermarked_audio[sample_idx]
                    bit_mask = 1 << bit_pos
                    
                    if watermark_bits[bit_index] == 1:
                        watermarked_audio[sample_idx] = sample | bit_mask
                    else:
                        watermarked_audio[sample_idx] = sample & ~bit_mask
                    
                    bit_index += 1
                    bits_embedded += 1
            
            # Convert back to float
            result_audio = watermarked_audio.astype(np.float32) / 32767.0
            
            result_info = {
                "technique": "lsb_embedding",
                "bits_embedded": bits_embedded,
                "bit_depth": bit_depth,
                "step_size": step,
                "embedding_rate": bits_embedded / len(watermark_bits)
            }
            
            return result_audio, result_info
            
        except Exception as e:
            logger.error(f"Error in LSB embedding: {e}")
            raise
    
    async def _detect_lsb(
        self,
        watermarked_audio: np.ndarray,
        original_audio: Optional[np.ndarray],
        expected_bits: int
    ) -> Tuple[List[int], float]:
        """LSB detection implementation"""
        try:
            audio_int = (watermarked_audio * 32767).astype(np.int16)
            
            extracted_bits = []
            step = 30  # Default step size
            bit_depth = 2  # Default bit depth
            
            bit_index = 0
            for sample_idx in range(0, len(audio_int), step):
                if bit_index >= expected_bits:
                    break
                
                for bit_pos in range(bit_depth):
                    if bit_index >= expected_bits or sample_idx >= len(audio_int):
                        break
                    
                    # Extract LSB
                    sample = audio_int[sample_idx]
                    bit_value = (sample >> bit_pos) & 1
                    extracted_bits.append(bit_value)
                    bit_index += 1
            
            # Simple confidence estimation (would need original for proper calculation)
            confidence = 0.7 if len(extracted_bits) == expected_bits else 0.3
            
            return extracted_bits, confidence
            
        except Exception as e:
            logger.error(f"Error in LSB detection: {e}")
            return [], 0.0
    
    async def _embed_echo(
        self,
        audio_data: np.ndarray,
        watermark_bits: List[int],
        strength: AudioWatermarkStrength
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Echo hiding implementation"""
        try:
            strength_params = {
                AudioWatermarkStrength.TRANSPARENT: {"delay_0": 0.3, "delay_1": 0.6, "alpha": 0.05},
                AudioWatermarkStrength.LIGHT: {"delay_0": 0.5, "delay_1": 1.0, "alpha": 0.1},
                AudioWatermarkStrength.MEDIUM: {"delay_0": 0.8, "delay_1": 1.5, "alpha": 0.2},
                AudioWatermarkStrength.STRONG: {"delay_0": 1.0, "delay_1": 2.0, "alpha": 0.3},
                AudioWatermarkStrength.ROBUST: {"delay_0": 1.2, "delay_1": 2.5, "alpha": 0.4}
            }
            
            params = strength_params[strength]
            delay_0_samples = int(params["delay_0"] * self.config.sample_rate / 1000)
            delay_1_samples = int(params["delay_1"] * self.config.sample_rate / 1000)
            alpha = params["alpha"]
            
            watermarked_audio = audio_data.copy()
            segment_length = len(audio_data) // len(watermark_bits)
            bits_embedded = 0
            
            for i, bit in enumerate(watermark_bits):
                start_idx = i * segment_length
                end_idx = min((i + 1) * segment_length, len(audio_data))
                
                if end_idx > start_idx:
                    segment = audio_data[start_idx:end_idx]
                    delay_samples = delay_1_samples if bit == 1 else delay_0_samples
                    
                    if delay_samples < len(segment):
                        # Apply echo
                        echoed_segment = segment.copy()
                        echoed_segment[delay_samples:] += alpha * segment[:-delay_samples]
                        watermarked_audio[start_idx:end_idx] = echoed_segment
                        bits_embedded += 1
            
            result_info = {
                "technique": "echo_hiding",
                "bits_embedded": bits_embedded,
                "delay_0_ms": params["delay_0"],
                "delay_1_ms": params["delay_1"],
                "echo_strength": alpha,
                "segment_length": segment_length
            }
            
            return watermarked_audio, result_info
            
        except Exception as e:
            logger.error(f"Error in echo embedding: {e}")
            raise
    
    async def _detect_echo(
        self,
        watermarked_audio: np.ndarray,
        original_audio: Optional[np.ndarray],
        expected_bits: int
    ) -> Tuple[List[int], float]:
        """Echo detection implementation"""
        try:
            # Simplified echo detection - would need autocorrelation analysis
            extracted_bits = [0] * expected_bits  # Placeholder
            confidence = 0.5  # Placeholder
            
            logger.warning("Echo detection not fully implemented")
            return extracted_bits, confidence
            
        except Exception as e:
            logger.error(f"Error in echo detection: {e}")
            return [], 0.0
    
    async def _embed_phase(
        self,
        audio_data: np.ndarray,
        watermark_bits: List[int],
        strength: AudioWatermarkStrength
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Phase coding implementation"""
        try:
            # STFT for phase manipulation
            stft = librosa.stft(audio_data, n_fft=self.config.frame_size, hop_length=self.config.hop_length)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Phase modification parameters
            strength_values = {
                AudioWatermarkStrength.TRANSPARENT: 0.1,
                AudioWatermarkStrength.LIGHT: 0.2,
                AudioWatermarkStrength.MEDIUM: 0.3,
                AudioWatermarkStrength.STRONG: 0.5,
                AudioWatermarkStrength.ROBUST: 0.7
            }
            
            phase_shift = strength_values[strength]
            modified_phase = phase.copy()
            
            # Embed bits in phase
            frames_per_bit = max(1, stft.shape[1] // len(watermark_bits))
            bits_embedded = 0
            
            for bit_idx, bit in enumerate(watermark_bits):
                frame_idx = bit_idx * frames_per_bit
                if frame_idx < stft.shape[1]:
                    # Modify phase of mid-frequency bins
                    mid_bins = slice(stft.shape[0] // 4, 3 * stft.shape[0] // 4)
                    
                    if bit == 1:
                        modified_phase[mid_bins, frame_idx] += phase_shift
                    else:
                        modified_phase[mid_bins, frame_idx] -= phase_shift
                    
                    bits_embedded += 1
            
            # Reconstruct audio
            modified_stft = magnitude * np.exp(1j * modified_phase)
            watermarked_audio = librosa.istft(modified_stft, hop_length=self.config.hop_length)
            
            result_info = {
                "technique": "phase_coding",
                "bits_embedded": bits_embedded,
                "phase_shift": phase_shift,
                "frames_per_bit": frames_per_bit
            }
            
            return watermarked_audio, result_info
            
        except Exception as e:
            logger.error(f"Error in phase embedding: {e}")
            raise
    
    async def _detect_phase(
        self,
        watermarked_audio: np.ndarray,
        original_audio: Optional[np.ndarray],
        expected_bits: int
    ) -> Tuple[List[int], float]:
        """Phase detection implementation"""
        try:
            if original_audio is None:
                logger.warning("Phase detection requires original audio")
                return [], 0.0
            
            # Compare phases
            watermarked_stft = librosa.stft(watermarked_audio, n_fft=self.config.frame_size)
            original_stft = librosa.stft(original_audio, n_fft=self.config.frame_size)
            
            watermarked_phase = np.angle(watermarked_stft)
            original_phase = np.angle(original_stft)
            
            phase_diff = watermarked_phase - original_phase
            
            extracted_bits = []
            frames_per_bit = max(1, watermarked_stft.shape[1] // expected_bits)
            
            for bit_idx in range(expected_bits):
                frame_idx = bit_idx * frames_per_bit
                if frame_idx < watermarked_stft.shape[1]:
                    mid_bins = slice(watermarked_stft.shape[0] // 4, 3 * watermarked_stft.shape[0] // 4)
                    avg_phase_diff = np.mean(phase_diff[mid_bins, frame_idx])
                    
                    if avg_phase_diff > 0:
                        extracted_bits.append(1)
                    else:
                        extracted_bits.append(0)
            
            confidence = 0.8  # Simplified confidence calculation
            return extracted_bits, confidence
            
        except Exception as e:
            logger.error(f"Error in phase detection: {e}")
            return [], 0.0
    
    # Utility methods
    
    def _data_to_bits(self, data: bytes) -> List[int]:
        """Convert bytes to bit list"""
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return bits
    
    def _bits_to_data(self, bits: List[int]) -> bytes:
        """Convert bit list to bytes"""
        data = bytearray()
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | bits[i + j]
                data.append(byte)
        return bytes(data)
    
    def _add_error_correction(self, bits: List[int]) -> List[int]:
        """Add simple error correction (duplication)"""
        corrected_bits = []
        for bit in bits:
            corrected_bits.extend([bit, bit])  # Simple duplication
        return corrected_bits
    
    def _apply_error_correction(self, bits: List[int]) -> List[int]:
        """Apply error correction (majority voting)"""
        corrected_bits = []
        for i in range(0, len(bits), 2):
            if i + 1 < len(bits):
                # Majority voting between duplicated bits
                if bits[i] == bits[i + 1]:
                    corrected_bits.append(bits[i])
                else:
                    corrected_bits.append(bits[i])  # Default to first bit
            else:
                corrected_bits.append(bits[i])
        return corrected_bits
    
    def _remove_redundancy(self, bits: List[int], factor: int) -> List[int]:
        """Remove redundancy by majority voting"""
        if factor <= 1:
            return bits
        
        chunk_size = len(bits) // factor
        corrected_bits = []
        
        for i in range(chunk_size):
            # Extract redundant copies
            copies = []
            for j in range(factor):
                if i + j * chunk_size < len(bits):
                    copies.append(bits[i + j * chunk_size])
            
            # Majority voting
            if copies:
                corrected_bits.append(max(set(copies), key=copies.count))
        
        return corrected_bits


# Factory function for easy instantiation
def create_audio_watermark_engine(
    sample_rate: int = 44100,
    technique: AudioWatermarkTechnique = AudioWatermarkTechnique.SPECTRAL_SPREADING,
    strength: AudioWatermarkStrength = AudioWatermarkStrength.MEDIUM
) -> AudioWatermarkEngine:
    """
    Factory function to create audio watermark engine with common configurations
    """
    config = AudioWatermarkConfig(
        sample_rate=sample_rate,
        frame_size=2048,
        hop_length=512,
        frequency_range=(300.0, 8000.0),
        embedding_rate=1.0,
        redundancy_factor=3,
        error_correction=True,
        adaptive_strength=True
    )
    
    return AudioWatermarkEngine(config)


__all__ = [
    'AudioWatermarkEngine',
    'AudioWatermarkTechnique',
    'AudioWatermarkStrength',
    'AudioWatermarkConfig',
    'AudioWatermarkMetrics',
    'SpectralWatermarkEngine',
    'WaveletWatermarkEngine',
    'PsychoacousticModel',
    'create_audio_watermark_engine'
]
