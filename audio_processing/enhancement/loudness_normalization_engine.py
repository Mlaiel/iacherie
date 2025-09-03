"""🎚️ Loudness Normalization Engine - Professional Audio Normalization Service

Industrial-grade loudness normalization engine providing broadcast-standard 
loudness normalization and dynamic range optimization for professional content.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING & COPYRIGHT PROTECTION
=====================================
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, copying, modification, distribution, or commercialization
of this code WITHOUT explicit written permission is STRICTLY PROHIBITED
and will result in legal action under German and International copyright law.

For licensing inquiries: mlaiel@live.de

Team Expertise:
- Lead Developer AI & Machine Learning: Fahed Mlaiel
- Senior Backend Architecture: Advanced Python/FastAPI
- Audio Mastering Engineer: Professional Loudness Standards
- Broadcast Engineer: ITU-R & EBU Standards Implementation
- Database Administrator: PostgreSQL & Vector Databases
- Security Engineer: Enterprise Security & Authentication
- Microservices Architect: Scalable Distributed Systems
- DevOps Engineer: CI/CD & Cloud Infrastructure
- IA Prompt Engineer: Advanced AI Model Training
"""

import asyncio
import logging
import numpy as np
import scipy.signal
import librosa
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures
import time
import math

logger = logging.getLogger(__name__)


class LoudnessStandard(Enum):
    """Professional loudness standards."""
    EBU_R128 = "ebu_r128"                    # EBU R128 (-23 LUFS)
    ITU_R_BS1770 = "itu_r_bs1770"          # ITU-R BS.1770-4
    ATSC_A85 = "atsc_a85"                   # ATSC A/85 (-24 LUFS)
    CALM_ACT = "calm_act"                   # FCC CALM Act (-24 LUFS)
    NETFLIX = "netflix"                     # Netflix (-27 LUFS)
    SPOTIFY = "spotify"                     # Spotify (-14 LUFS)
    YOUTUBE = "youtube"                     # YouTube (-14 LUFS)
    BROADCAST_EU = "broadcast_eu"           # European Broadcasting (-23 LUFS)
    BROADCAST_US = "broadcast_us"           # US Broadcasting (-24 LUFS)
    STREAMING_HIGH = "streaming_high"       # High-quality streaming (-16 LUFS)
    STREAMING_STANDARD = "streaming_standard" # Standard streaming (-14 LUFS)


class DynamicRangeTarget(Enum):
    """Dynamic range optimization targets."""
    PRESERVE_ORIGINAL = "preserve_original"  # Maintain original dynamics
    BROADCAST_STANDARD = "broadcast_standard" # DR12-16 for broadcast
    STREAMING_OPTIMIZED = "streaming_optimized" # DR8-12 for streaming
    MASTERING_LOUD = "mastering_loud"       # DR6-10 for loud mastering
    PODCAST_SPEECH = "podcast_speech"       # DR4-8 for speech content
    MUSIC_DYNAMICS = "music_dynamics"       # DR10-20 for music


class ProcessingPrecision(Enum):
    """Audio processing precision levels."""
    FLOAT64_BROADCAST = "float64_broadcast"  # 64-bit for broadcast
    FLOAT32_PRODUCTION = "float32_production" # 32-bit for production
    INT24_PROFESSIONAL = "int24_professional" # 24-bit professional
    INT16_STANDARD = "int16_standard"        # 16-bit standard


@dataclass
class LoudnessMeter:
    """Professional loudness measurement results."""
    integrated_lufs: float          # Integrated loudness (LUFS)
    momentary_max_lufs: float      # Maximum momentary loudness
    short_term_max_lufs: float     # Maximum short-term loudness
    loudness_range_lu: float       # Loudness range (LU)
    true_peak_dbfs: float          # True peak level (dBFS)
    dynamic_range_db: float        # Dynamic range (dB)
    average_rms_db: float          # Average RMS level
    peak_to_average_ratio: float   # Peak to average ratio
    stereo_balance: float          # L/R balance (-1 to 1)
    compliance_status: Dict[str, bool] = field(default_factory=dict)


@dataclass
class NormalizationRequest:
    """Professional normalization request specification."""
    audio_data: Union[np.ndarray, bytes, str]
    sample_rate: int = 44100
    target_standard: LoudnessStandard = LoudnessStandard.EBU_R128
    dynamic_range_target: DynamicRangeTarget = DynamicRangeTarget.BROADCAST_STANDARD
    precision: ProcessingPrecision = ProcessingPrecision.FLOAT32_PRODUCTION
    true_peak_limit_dbfs: float = -1.0
    enable_peak_limiting: bool = True
    enable_dynamic_range_control: bool = True
    preserve_stereo_image: bool = True
    apply_dithering: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NormalizationResult:
    """Professional normalization result with detailed analysis."""
    normalized_audio: np.ndarray
    original_loudness: LoudnessMeter
    normalized_loudness: LoudnessMeter
    processing_gain_db: float
    peak_reduction_db: float
    dynamic_range_change_db: float
    sample_rate: int
    processing_time: float
    compliance_report: Dict[str, Any]
    quality_metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


class LoudnessNormalizationEngine:
    """Industrial-grade loudness normalization engine.
    
    Provides professional loudness normalization following international
    broadcasting standards with enterprise-level precision and compliance.
    """
    
    def __init__(
        self,
        precision: ProcessingPrecision = ProcessingPrecision.FLOAT32_PRODUCTION,
        max_concurrent_jobs: int = 4,
        enable_advanced_metering: bool = True,
        cache_analysis: bool = True
    ):
        """Initialize the professional normalization engine.
        
        Args:
            precision: Audio processing precision level
            max_concurrent_jobs: Maximum concurrent normalization jobs
            enable_advanced_metering: Enable advanced loudness metering
            cache_analysis: Whether to cache loudness analysis
        """
        self.precision = precision
        self.max_concurrent_jobs = max_concurrent_jobs
        self.enable_advanced_metering = enable_advanced_metering
        self.cache_analysis = cache_analysis
        
        # Analysis cache for performance
        self._analysis_cache: Dict[str, LoudnessMeter] = {}
        
        # Processing statistics
        self.stats = {
            "total_normalizations": 0,
            "total_processing_time": 0.0,
            "average_gain_applied": 0.0,
            "compliance_rate": 0.0
        }
        
        # Thread pool for concurrent processing
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent_jobs
        )
        
        # Loudness standard specifications
        self.standard_specs = {
            LoudnessStandard.EBU_R128: {"target_lufs": -23.0, "max_true_peak": -1.0, "max_range": 20.0},
            LoudnessStandard.ITU_R_BS1770: {"target_lufs": -23.0, "max_true_peak": -1.0, "max_range": 20.0},
            LoudnessStandard.ATSC_A85: {"target_lufs": -24.0, "max_true_peak": -2.0, "max_range": 20.0},
            LoudnessStandard.CALM_ACT: {"target_lufs": -24.0, "max_true_peak": -2.0, "max_range": 20.0},
            LoudnessStandard.NETFLIX: {"target_lufs": -27.0, "max_true_peak": -2.0, "max_range": 18.0},
            LoudnessStandard.SPOTIFY: {"target_lufs": -14.0, "max_true_peak": -1.0, "max_range": 15.0},
            LoudnessStandard.YOUTUBE: {"target_lufs": -14.0, "max_true_peak": -1.0, "max_range": 15.0},
            LoudnessStandard.BROADCAST_EU: {"target_lufs": -23.0, "max_true_peak": -1.0, "max_range": 20.0},
            LoudnessStandard.BROADCAST_US: {"target_lufs": -24.0, "max_true_peak": -2.0, "max_range": 20.0},
            LoudnessStandard.STREAMING_HIGH: {"target_lufs": -16.0, "max_true_peak": -1.0, "max_range": 12.0},
            LoudnessStandard.STREAMING_STANDARD: {"target_lufs": -14.0, "max_true_peak": -1.0, "max_range": 10.0}
        }
        
        logger.info(f"LoudnessNormalizationEngine initialized with {precision.value} precision")
    
    async def normalize_audio(self, request: NormalizationRequest) -> NormalizationResult:
        """Perform professional loudness normalization.
        
        Args:
            request: Normalization request with specifications
            
        Returns:
            NormalizationResult with normalized audio and detailed analysis
        """
        start_time = time.time()
        
        try:
            # Validate and preprocess input
            audio_data, sr = await self._preprocess_audio(
                request.audio_data, request.sample_rate
            )
            
            # Measure original loudness
            original_loudness = await self._measure_loudness(audio_data, sr)
            
            # Calculate normalization parameters
            normalization_params = await self._calculate_normalization_params(
                original_loudness, request
            )
            
            # Apply normalization processing
            normalized_audio = await self._apply_normalization(
                audio_data, sr, normalization_params, request
            )
            
            # Measure normalized loudness
            normalized_loudness = await self._measure_loudness(normalized_audio, sr)
            
            # Generate compliance report
            compliance_report = await self._generate_compliance_report(
                normalized_loudness, request.target_standard
            )
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                audio_data, normalized_audio, original_loudness, normalized_loudness
            )
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(normalization_params, compliance_report, processing_time)
            
            result = NormalizationResult(
                normalized_audio=normalized_audio,
                original_loudness=original_loudness,
                normalized_loudness=normalized_loudness,
                processing_gain_db=normalization_params["gain_db"],
                peak_reduction_db=normalization_params.get("peak_reduction_db", 0.0),
                dynamic_range_change_db=(
                    normalized_loudness.dynamic_range_db - original_loudness.dynamic_range_db
                ),
                sample_rate=sr,
                processing_time=processing_time,
                compliance_report=compliance_report,
                quality_metrics=quality_metrics,
                metadata={
                    "target_standard": request.target_standard.value,
                    "dynamic_range_target": request.dynamic_range_target.value,
                    "precision": request.precision.value,
                    "processing_chain": normalization_params.get("processing_chain", [])
                }
            )
            
            logger.info(
                f"Normalization completed in {processing_time:.2f}s: "
                f"{original_loudness.integrated_lufs:.1f} → {normalized_loudness.integrated_lufs:.1f} LUFS"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            raise RuntimeError(f"Audio normalization failed: {str(e)}")
    
    async def _preprocess_audio(
        self, audio_input: Union[np.ndarray, bytes, str], target_sr: int
    ) -> Tuple[np.ndarray, int]:
        """Preprocess input audio for optimal normalization."""
        
        def preprocess():
            if isinstance(audio_input, str):
                # Load from file path with high precision
                audio_data, sr = librosa.load(audio_input, sr=None, mono=False, dtype=np.float64)
            elif isinstance(audio_input, bytes):
                import soundfile as sf
                from io import BytesIO
                audio_data, sr = sf.read(BytesIO(audio_input), dtype=np.float64)
                if audio_data.ndim == 2:
                    audio_data = audio_data.T
            elif isinstance(audio_input, np.ndarray):
                audio_data = audio_input.astype(np.float64)
                sr = target_sr
            else:
                raise ValueError(f"Unsupported audio input type: {type(audio_input)}")
            
            # Ensure stereo for professional processing
            if audio_data.ndim == 1:
                audio_data = np.stack([audio_data, audio_data])
            elif audio_data.ndim == 2 and audio_data.shape[0] == 1:
                audio_data = np.stack([audio_data[0], audio_data[0]])
            
            # Resample if needed with high-quality resampling
            if sr != target_sr:
                if audio_data.ndim == 1:
                    audio_data = librosa.resample(
                        audio_data, orig_sr=sr, target_sr=target_sr, res_type='kaiser_best'
                    )
                else:
                    audio_data = np.array([
                        librosa.resample(
                            channel, orig_sr=sr, target_sr=target_sr, res_type='kaiser_best'
                        )
                        for channel in audio_data
                    ])
                sr = target_sr
            
            return audio_data, sr
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, preprocess
        )
    
    async def _measure_loudness(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> LoudnessMeter:
        """Comprehensive loudness measurement following ITU-R BS.1770-4."""
        
        def measure():
            # Ensure stereo
            if audio_data.ndim == 1:
                stereo_audio = np.stack([audio_data, audio_data])
            else:
                stereo_audio = audio_data
            
            # Apply K-weighting filter (ITU-R BS.1770-4)
            k_weighted = self._apply_k_weighting(stereo_audio, sample_rate)
            
            # Calculate integrated loudness (LUFS)
            integrated_lufs = self._calculate_integrated_loudness(k_weighted, sample_rate)
            
            # Calculate momentary loudness (400ms sliding window)
            momentary_lufs = self._calculate_momentary_loudness(k_weighted, sample_rate)
            momentary_max = np.max(momentary_lufs) if len(momentary_lufs) > 0 else -np.inf
            
            # Calculate short-term loudness (3s sliding window)
            short_term_lufs = self._calculate_short_term_loudness(k_weighted, sample_rate)
            short_term_max = np.max(short_term_lufs) if len(short_term_lufs) > 0 else -np.inf
            
            # Calculate loudness range (LU)
            loudness_range = self._calculate_loudness_range(short_term_lufs)
            
            # Calculate true peak using 4x oversampling
            true_peak_dbfs = self._calculate_true_peak(stereo_audio, sample_rate)
            
            # Calculate dynamic range
            dynamic_range = self._calculate_dynamic_range(stereo_audio)
            
            # Calculate RMS levels
            avg_rms = self._calculate_average_rms(stereo_audio)
            
            # Calculate peak-to-average ratio
            peak_to_avg = true_peak_dbfs - avg_rms
            
            # Calculate stereo balance
            stereo_balance = self._calculate_stereo_balance(stereo_audio)
            
            return LoudnessMeter(
                integrated_lufs=integrated_lufs,
                momentary_max_lufs=momentary_max,
                short_term_max_lufs=short_term_max,
                loudness_range_lu=loudness_range,
                true_peak_dbfs=true_peak_dbfs,
                dynamic_range_db=dynamic_range,
                average_rms_db=avg_rms,
                peak_to_average_ratio=peak_to_avg,
                stereo_balance=stereo_balance
            )
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, measure
        )
    
    def _apply_k_weighting(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply K-weighting filter according to ITU-R BS.1770-4."""
        # High-pass filter (HPF): 2nd order Butterworth at 38 Hz
        sos_hpf = scipy.signal.butter(2, 38, btype='highpass', fs=sample_rate, output='sos')
        
        # High-frequency shelf filter: +4 dB above 1.5 kHz
        # Approximation using peaking filter
        sos_hf = scipy.signal.iirpeak(1500, 1500/sample_rate*2, fs=sample_rate)
        
        # Apply filters to each channel
        filtered = np.zeros_like(audio)
        for ch in range(audio.shape[0]):
            # Apply high-pass filter
            filtered[ch] = scipy.signal.sosfilt(sos_hpf, audio[ch])
            # Apply high-frequency shelf (simplified)
            filtered[ch] = scipy.signal.filtfilt(sos_hf[0], sos_hf[1], filtered[ch])
        
        return filtered
    
    def _calculate_integrated_loudness(self, k_weighted: np.ndarray, sample_rate: int) -> float:
        """Calculate integrated loudness over entire signal."""
        # Gate implementation according to ITU-R BS.1770-4
        block_size = int(0.4 * sample_rate)  # 400ms blocks
        overlap = int(0.3 * sample_rate)     # 75% overlap
        
        loudness_blocks = []
        
        for start in range(0, len(k_weighted[0]) - block_size + 1, block_size - overlap):
            block = k_weighted[:, start:start + block_size]
            
            # Calculate mean square for each channel
            ms_l = np.mean(block[0] ** 2)
            ms_r = np.mean(block[1] ** 2)
            
            # Loudness calculation with channel weighting
            loudness = -0.691 + 10 * np.log10(ms_l + ms_r)
            loudness_blocks.append(loudness)
        
        if not loudness_blocks:
            return -np.inf
        
        # Apply gating
        loudness_blocks = np.array(loudness_blocks)
        
        # Absolute gate at -70 LUFS
        valid_blocks = loudness_blocks[loudness_blocks > -70]
        
        if len(valid_blocks) == 0:
            return -np.inf
        
        # Relative gate at -10 LU below mean
        mean_loudness = np.mean(valid_blocks)
        relative_gate = mean_loudness - 10
        final_blocks = valid_blocks[valid_blocks > relative_gate]
        
        if len(final_blocks) == 0:
            return mean_loudness
        
        return np.mean(final_blocks)
    
    def _calculate_momentary_loudness(self, k_weighted: np.ndarray, sample_rate: int) -> np.ndarray:
        """Calculate momentary loudness (400ms sliding window)."""
        block_size = int(0.4 * sample_rate)
        hop_size = int(0.1 * sample_rate)  # 100ms hop
        
        momentary_values = []
        
        for start in range(0, len(k_weighted[0]) - block_size + 1, hop_size):
            block = k_weighted[:, start:start + block_size]
            ms_l = np.mean(block[0] ** 2)
            ms_r = np.mean(block[1] ** 2)
            loudness = -0.691 + 10 * np.log10(ms_l + ms_r + 1e-10)
            momentary_values.append(loudness)
        
        return np.array(momentary_values)
    
    def _calculate_short_term_loudness(self, k_weighted: np.ndarray, sample_rate: int) -> np.ndarray:
        """Calculate short-term loudness (3s sliding window)."""
        block_size = int(3.0 * sample_rate)
        hop_size = int(0.1 * sample_rate)  # 100ms hop
        
        short_term_values = []
        
        for start in range(0, len(k_weighted[0]) - block_size + 1, hop_size):
            block = k_weighted[:, start:start + block_size]
            ms_l = np.mean(block[0] ** 2)
            ms_r = np.mean(block[1] ** 2)
            loudness = -0.691 + 10 * np.log10(ms_l + ms_r + 1e-10)
            short_term_values.append(loudness)
        
        return np.array(short_term_values)
    
    def _calculate_loudness_range(self, short_term_lufs: np.ndarray) -> float:
        """Calculate loudness range (difference between 95th and 10th percentiles)."""
        if len(short_term_lufs) == 0:
            return 0.0
        
        # Remove values below absolute gate
        valid_values = short_term_lufs[short_term_lufs > -70]
        
        if len(valid_values) < 2:
            return 0.0
        
        p95 = np.percentile(valid_values, 95)
        p10 = np.percentile(valid_values, 10)
        
        return p95 - p10
    
    def _calculate_true_peak(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate true peak using 4x oversampling."""
        # Upsample by 4x using zero-padding in frequency domain
        upsampled = []
        
        for ch in range(audio.shape[0]):
            # FFT
            fft_signal = np.fft.fft(audio[ch])
            
            # Zero-pad in frequency domain (4x upsampling)
            upsampled_fft = np.zeros(len(fft_signal) * 4, dtype=complex)
            half_len = len(fft_signal) // 2
            upsampled_fft[:half_len] = fft_signal[:half_len]
            upsampled_fft[-half_len:] = fft_signal[-half_len:]
            
            # IFFT to get upsampled signal
            upsampled_signal = np.fft.ifft(upsampled_fft).real * 4
            upsampled.append(upsampled_signal)
        
        # Find maximum absolute value across all channels
        max_peak = 0.0
        for ch_signal in upsampled:
            ch_peak = np.max(np.abs(ch_signal))
            max_peak = max(max_peak, ch_peak)
        
        # Convert to dBFS
        if max_peak > 0:
            return 20 * np.log10(max_peak)
        else:
            return -np.inf
    
    def _calculate_dynamic_range(self, audio: np.ndarray) -> float:
        """Calculate dynamic range using EBU Tech 3342 method."""
        # Use RMS-based measurement
        if audio.ndim == 1:
            signal = audio
        else:
            signal = np.mean(audio, axis=0)
        
        # Calculate RMS in sliding windows
        window_size = int(len(signal) * 0.05)  # 5% of signal length
        hop_size = window_size // 4
        
        rms_values = []
        for start in range(0, len(signal) - window_size + 1, hop_size):
            window = signal[start:start + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            if rms > 0:
                rms_values.append(20 * np.log10(rms))
        
        if len(rms_values) < 2:
            return 0.0
        
        # Dynamic range = difference between 95th and 10th percentiles
        rms_values = np.array(rms_values)
        dr = np.percentile(rms_values, 95) - np.percentile(rms_values, 10)
        
        return max(0.0, dr)
    
    def _calculate_average_rms(self, audio: np.ndarray) -> float:
        """Calculate average RMS level in dBFS."""
        if audio.ndim == 1:
            rms = np.sqrt(np.mean(audio ** 2))
        else:
            rms = np.sqrt(np.mean(audio ** 2))
        
        if rms > 0:
            return 20 * np.log10(rms)
        else:
            return -np.inf
    
    def _calculate_stereo_balance(self, audio: np.ndarray) -> float:
        """Calculate stereo balance (-1 = left, 0 = center, 1 = right)."""
        if audio.ndim == 1:
            return 0.0
        
        left_energy = np.mean(audio[0] ** 2)
        right_energy = np.mean(audio[1] ** 2)
        total_energy = left_energy + right_energy
        
        if total_energy > 0:
            return (right_energy - left_energy) / total_energy
        else:
            return 0.0
    
    async def _calculate_normalization_params(
        self, loudness: LoudnessMeter, request: NormalizationRequest
    ) -> Dict[str, Any]:
        """Calculate normalization parameters based on target standard."""
        
        def calculate():
            target_spec = self.standard_specs[request.target_standard]
            target_lufs = target_spec["target_lufs"]
            
            # Calculate required gain
            gain_db = target_lufs - loudness.integrated_lufs
            
            # Check if peak limiting is needed
            predicted_peak = loudness.true_peak_dbfs + gain_db
            peak_limit = request.true_peak_limit_dbfs
            peak_reduction_db = 0.0
            
            if predicted_peak > peak_limit:
                peak_reduction_db = predicted_peak - peak_limit
                gain_db -= peak_reduction_db
            
            # Dynamic range control parameters
            dr_params = self._calculate_dynamic_range_params(
                loudness, request.dynamic_range_target
            )
            
            return {
                "gain_db": gain_db,
                "peak_reduction_db": peak_reduction_db,
                "target_lufs": target_lufs,
                "dynamic_range_params": dr_params,
                "processing_chain": [
                    "gain_adjustment",
                    "peak_limiting" if request.enable_peak_limiting else None,
                    "dynamic_range_control" if request.enable_dynamic_range_control else None
                ]
            }
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, calculate
        )
    
    def _calculate_dynamic_range_params(
        self, loudness: LoudnessMeter, dr_target: DynamicRangeTarget
    ) -> Dict[str, Any]:
        """Calculate dynamic range control parameters."""
        
        target_ranges = {
            DynamicRangeTarget.PRESERVE_ORIGINAL: None,
            DynamicRangeTarget.BROADCAST_STANDARD: (12, 16),
            DynamicRangeTarget.STREAMING_OPTIMIZED: (8, 12),
            DynamicRangeTarget.MASTERING_LOUD: (6, 10),
            DynamicRangeTarget.PODCAST_SPEECH: (4, 8),
            DynamicRangeTarget.MUSIC_DYNAMICS: (10, 20)
        }
        
        target_range = target_ranges.get(dr_target)
        
        if target_range is None:
            return {"apply_control": False}
        
        min_dr, max_dr = target_range
        current_dr = loudness.dynamic_range_db
        
        if min_dr <= current_dr <= max_dr:
            return {"apply_control": False}
        
        # Calculate compression parameters
        if current_dr > max_dr:
            # Need compression
            ratio = current_dr / max_dr
            threshold = -12.0  # dBFS
            attack = 5.0      # ms
            release = 50.0    # ms
        else:
            # Need expansion (rare)
            ratio = 1.0 / (current_dr / min_dr)
            threshold = -24.0
            attack = 1.0
            release = 100.0
        
        return {
            "apply_control": True,
            "compression_ratio": ratio,
            "threshold_dbfs": threshold,
            "attack_ms": attack,
            "release_ms": release
        }
    
    async def _apply_normalization(
        self, 
        audio: np.ndarray, 
        sample_rate: int, 
        params: Dict[str, Any], 
        request: NormalizationRequest
    ) -> np.ndarray:
        """Apply normalization processing chain."""
        
        def process():
            processed_audio = audio.copy()
            
            # Apply gain adjustment
            gain_linear = 10 ** (params["gain_db"] / 20)
            processed_audio *= gain_linear
            
            # Apply dynamic range control if needed
            if (request.enable_dynamic_range_control and 
                params["dynamic_range_params"].get("apply_control", False)):
                processed_audio = self._apply_dynamic_range_control(
                    processed_audio, sample_rate, params["dynamic_range_params"]
                )
            
            # Apply peak limiting if needed
            if request.enable_peak_limiting and params["peak_reduction_db"] > 0:
                processed_audio = self._apply_peak_limiting(
                    processed_audio, sample_rate, request.true_peak_limit_dbfs
                )
            
            # Apply dithering for reduced bit depths
            if request.apply_dithering and request.precision in [
                ProcessingPrecision.INT24_PROFESSIONAL, 
                ProcessingPrecision.INT16_STANDARD
            ]:
                processed_audio = self._apply_dithering(processed_audio, request.precision)
            
            return processed_audio
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, process
        )
    
    def _apply_dynamic_range_control(
        self, audio: np.ndarray, sample_rate: int, params: Dict[str, Any]
    ) -> np.ndarray:
        """Apply dynamic range control (compression/expansion)."""
        
        # Simple compressor implementation
        ratio = params["compression_ratio"]
        threshold_db = params["threshold_dbfs"]
        threshold_linear = 10 ** (threshold_db / 20)
        
        # Attack/release time constants
        attack_samples = int(params["attack_ms"] * sample_rate / 1000)
        release_samples = int(params["release_ms"] * sample_rate / 1000)
        
        # Process each channel
        processed = np.zeros_like(audio)
        
        for ch in range(audio.shape[0]):
            channel = audio[ch]
            
            # Envelope detection
            envelope = np.abs(channel)
            
            # Smooth envelope
            smoothed_env = np.zeros_like(envelope)
            smoothed_env[0] = envelope[0]
            
            for i in range(1, len(envelope)):
                if envelope[i] > smoothed_env[i-1]:
                    # Attack
                    alpha = 1 - np.exp(-1 / attack_samples)
                else:
                    # Release
                    alpha = 1 - np.exp(-1 / release_samples)
                
                smoothed_env[i] = (alpha * envelope[i] + 
                                 (1 - alpha) * smoothed_env[i-1])
            
            # Calculate gain reduction
            gain_reduction = np.ones_like(smoothed_env)
            over_threshold = smoothed_env > threshold_linear
            
            if np.any(over_threshold):
                gain_reduction[over_threshold] = (
                    (smoothed_env[over_threshold] / threshold_linear) ** 
                    ((1 / ratio) - 1)
                )
            
            # Apply gain reduction
            processed[ch] = channel * gain_reduction
        
        return processed
    
    def _apply_peak_limiting(
        self, audio: np.ndarray, sample_rate: int, limit_dbfs: float
    ) -> np.ndarray:
        """Apply professional peak limiting."""
        
        limit_linear = 10 ** (limit_dbfs / 20)
        
        # Look-ahead limiter parameters
        lookahead_ms = 5.0
        lookahead_samples = int(lookahead_ms * sample_rate / 1000)
        
        processed = np.zeros_like(audio)
        
        for ch in range(audio.shape[0]):
            channel = audio[ch]
            
            # Simple brick-wall limiter with soft-knee
            limited = np.tanh(channel / limit_linear) * limit_linear
            
            processed[ch] = limited
        
        return processed
    
    def _apply_dithering(
        self, audio: np.ndarray, precision: ProcessingPrecision
    ) -> np.ndarray:
        """Apply professional dithering for bit depth reduction."""
        
        if precision == ProcessingPrecision.INT24_PROFESSIONAL:
            # 24-bit dithering
            bit_depth = 24
        elif precision == ProcessingPrecision.INT16_STANDARD:
            # 16-bit dithering
            bit_depth = 16
        else:
            return audio
        
        # Calculate quantization level
        max_val = 2 ** (bit_depth - 1) - 1
        quantization_step = 1.0 / max_val
        
        # Apply triangular dithering
        dither_amplitude = quantization_step
        dither_noise = np.random.triangular(
            -dither_amplitude, 0, dither_amplitude, audio.shape
        )
        
        # Add dither and quantize
        dithered = audio + dither_noise
        quantized = np.round(dithered * max_val) / max_val
        
        return quantized
    
    async def _generate_compliance_report(
        self, loudness: LoudnessMeter, standard: LoudnessStandard
    ) -> Dict[str, Any]:
        """Generate detailed compliance report."""
        
        def generate():
            spec = self.standard_specs[standard]
            
            # Check compliance criteria
            lufs_compliant = abs(loudness.integrated_lufs - spec["target_lufs"]) <= 1.0
            peak_compliant = loudness.true_peak_dbfs <= spec["max_true_peak"]
            range_compliant = loudness.loudness_range_lu <= spec["max_range"]
            
            overall_compliant = lufs_compliant and peak_compliant and range_compliant
            
            return {
                "standard": standard.value,
                "overall_compliant": overall_compliant,
                "compliance_details": {
                    "target_lufs": spec["target_lufs"],
                    "measured_lufs": loudness.integrated_lufs,
                    "lufs_compliant": lufs_compliant,
                    "lufs_deviation": loudness.integrated_lufs - spec["target_lufs"],
                    
                    "max_true_peak": spec["max_true_peak"],
                    "measured_true_peak": loudness.true_peak_dbfs,
                    "peak_compliant": peak_compliant,
                    "peak_headroom": spec["max_true_peak"] - loudness.true_peak_dbfs,
                    
                    "max_range": spec["max_range"],
                    "measured_range": loudness.loudness_range_lu,
                    "range_compliant": range_compliant
                },
                "quality_grade": self._calculate_quality_grade(
                    lufs_compliant, peak_compliant, range_compliant
                )
            }
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, generate
        )
    
    def _calculate_quality_grade(
        self, lufs_ok: bool, peak_ok: bool, range_ok: bool
    ) -> str:
        """Calculate quality grade based on compliance."""
        
        score = sum([lufs_ok, peak_ok, range_ok])
        
        if score == 3:
            return "A+ (Fully Compliant)"
        elif score == 2:
            return "B+ (Minor Issues)"
        elif score == 1:
            return "C (Major Issues)"
        else:
            return "F (Non-Compliant)"
    
    async def _calculate_quality_metrics(
        self, 
        original: np.ndarray, 
        normalized: np.ndarray,
        original_loudness: LoudnessMeter,
        normalized_loudness: LoudnessMeter
    ) -> Dict[str, float]:
        """Calculate quality metrics for normalization."""
        
        def calculate():
            # Ensure same length
            min_len = min(len(original[0]), len(normalized[0]))
            orig_trim = original[:, :min_len]
            norm_trim = normalized[:, :min_len]
            
            # Signal-to-noise ratio
            diff = orig_trim - norm_trim
            signal_power = np.mean(orig_trim ** 2)
            noise_power = np.mean(diff ** 2)
            
            if noise_power > 0:
                snr_db = 10 * np.log10(signal_power / noise_power)
            else:
                snr_db = 100.0
            
            # Loudness accuracy
            lufs_accuracy = 1.0 - min(1.0, abs(normalized_loudness.integrated_lufs + 23) / 10)
            
            # Dynamic preservation
            dr_preservation = 1.0 - min(1.0, abs(
                normalized_loudness.dynamic_range_db - original_loudness.dynamic_range_db
            ) / original_loudness.dynamic_range_db)
            
            # Stereo preservation  
            stereo_preservation = 1.0 - abs(
                normalized_loudness.stereo_balance - original_loudness.stereo_balance
            )
            
            return {
                "snr_db": float(snr_db),
                "lufs_accuracy": float(lufs_accuracy),
                "dynamic_range_preservation": float(dr_preservation),
                "stereo_preservation": float(stereo_preservation),
                "overall_quality": float((lufs_accuracy + dr_preservation + stereo_preservation) / 3)
            }
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, calculate
        )
    
    def _update_stats(
        self, params: Dict[str, Any], compliance: Dict[str, Any], processing_time: float
    ):
        """Update engine statistics."""
        self.stats["total_normalizations"] += 1
        self.stats["total_processing_time"] += processing_time
        
        # Update average gain
        current_avg_gain = self.stats["average_gain_applied"]
        total_jobs = self.stats["total_normalizations"]
        new_avg_gain = (
            (current_avg_gain * (total_jobs - 1) + params["gain_db"]) / total_jobs
        )
        self.stats["average_gain_applied"] = new_avg_gain
        
        # Update compliance rate
        current_compliance_rate = self.stats["compliance_rate"]
        compliance_score = 1.0 if compliance["overall_compliant"] else 0.0
        new_compliance_rate = (
            (current_compliance_rate * (total_jobs - 1) + compliance_score) / total_jobs
        )
        self.stats["compliance_rate"] = new_compliance_rate
    
    async def batch_normalize(
        self, requests: List[NormalizationRequest]
    ) -> List[NormalizationResult]:
        """Process multiple normalization requests concurrently."""
        
        batch_size = min(self.max_concurrent_jobs, len(requests))
        results = []
        
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.normalize_audio(req) for req in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch normalization failed: {result}")
                    results.append(None)
                else:
                    results.append(result)
        
        return [r for r in results if r is not None]
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine performance statistics."""
        return {
            **self.stats,
            "precision": self.precision.value,
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "supported_standards": list(self.standard_specs.keys())
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            self.executor.shutdown(wait=True)
            logger.info("LoudnessNormalizationEngine cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Convenience functions for direct usage
async def normalize_loudness(
    audio_input: Union[np.ndarray, bytes, str],
    sample_rate: int = 44100,
    target_standard: LoudnessStandard = LoudnessStandard.EBU_R128,
    dynamic_range_target: DynamicRangeTarget = DynamicRangeTarget.BROADCAST_STANDARD
) -> NormalizationResult:
    """Professional loudness normalization function.
    
    Args:
        audio_input: Audio data (array, bytes, or file path)
        sample_rate: Target sample rate
        target_standard: Target loudness standard
        dynamic_range_target: Dynamic range optimization target
        
    Returns:
        NormalizationResult with normalized audio and analysis
    """
    engine = LoudnessNormalizationEngine()
    try:
        request = NormalizationRequest(
            audio_data=audio_input,
            sample_rate=sample_rate,
            target_standard=target_standard,
            dynamic_range_target=dynamic_range_target
        )
        return await engine.normalize_audio(request)
    finally:
        await engine.cleanup()


def create_normalization_engine(**kwargs) -> LoudnessNormalizationEngine:
    """Create a configured normalization engine instance."""
    return LoudnessNormalizationEngine(**kwargs)