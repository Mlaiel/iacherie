"""🎯 Quality Optimizer - Audio Quality Optimization Engine

Advanced audio quality optimization system for automatic audio enhancement,
quality improvement, and adaptive audio processing based on quality analysis.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np
import librosa
from scipy import signal, stats
from scipy.signal import butter, filtfilt, hilbert

from .standards import QualityProfile
from .metrics import QualityReport
from .validator import ValidationResult

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Audio optimization types"""    NOISE_REDUCTION = "noise_reduction"
    DYNAMIC_RANGE = "dynamic_range"
    FREQUENCY_BALANCE = "frequency_balance"
    LOUDNESS_NORMALIZATION = "loudness_normalization"
    STEREO_ENHANCEMENT = "stereo_enhancement"
    HARMONIC_CORRECTION = "harmonic_correction"
    TEMPORAL_SMOOTHING = "temporal_smoothing"
    PEAK_LIMITING = "peak_limiting"
    COMPRESSION = "compression"
    EQUALIZATION = "equalization"


class OptimizationLevel(Enum):
    """Optimization intensity levels"""    MINIMAL = "minimal"       # Light processing
    MODERATE = "moderate"     # Standard processing
    AGGRESSIVE = "aggressive" # Heavy processing
    MAXIMUM = "maximum"       # Maximum processing


@dataclass
class OptimizationResult:
    """Audio optimization result"""    optimization_type: OptimizationType
    level: OptimizationLevel
    success: bool
    quality_improvement: float
    processing_time: float
    parameters_used: Dict[str, Any] = field(default_factory=dict)
    before_metrics: Dict[str, float] = field(default_factory=dict)
    after_metrics: Dict[str, float] = field(default_factory=dict)
    message: str = ""
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationPlan:
    """Complete optimization plan"""    optimizations: List[OptimizationType]
    levels: Dict[OptimizationType, OptimizationLevel]
    target_metrics: Dict[str, float]
    estimated_improvement: float
    estimated_time: float
    priority_order: List[OptimizationType]
    created_at: datetime = field(default_factory=datetime.now)


class AudioOptimizer:
    """    🎯 Base Audio Optimizer
    
    Abstract base class for audio optimization algorithms
    """    
    def __init__(self, optimization_type: OptimizationType):
        self.optimization_type = optimization_type
        self.processing_count = 0
        self.success_count = 0
        self.total_improvement = 0.0
        self.total_processing_time = 0.0
    
    async def optimize(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        level: OptimizationLevel = OptimizationLevel.MODERATE,
        target_metrics: Optional[Dict[str, float]] = None
    ) -> Tuple[np.ndarray, OptimizationResult]:
        """Optimize audio data"""        start_time = datetime.now()
        
        try:
            # Calculate before metrics
            before_metrics = self._calculate_metrics(audio_data, sample_rate)
            
            # Apply optimization
            optimized_audio = await self._apply_optimization(
                audio_data, sample_rate, level, target_metrics
            )
            
            # Calculate after metrics
            after_metrics = self._calculate_metrics(optimized_audio, sample_rate)
            
            # Calculate improvement
            improvement = self._calculate_improvement(before_metrics, after_metrics)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = OptimizationResult(
                optimization_type=self.optimization_type,
                level=level,
                success=True,
                quality_improvement=improvement,
                processing_time=processing_time,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                message=f"Optimization successful: {improvement:.1%} improvement"
            )
            
            # Update statistics
            self.processing_count += 1
            self.success_count += 1
            self.total_improvement += improvement
            self.total_processing_time += processing_time
            
            return optimized_audio, result
            
        except Exception as e:
            logger.error(f"Optimization {self.optimization_type.value} failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = OptimizationResult(
                optimization_type=self.optimization_type,
                level=level,
                success=False,
                quality_improvement=0.0,
                processing_time=processing_time,
                message=f"Optimization failed: {str(e)}"
            )
            
            self.processing_count += 1
            return audio_data, result
    
    async def _apply_optimization(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        level: OptimizationLevel,
        target_metrics: Optional[Dict[str, float]]
    ) -> np.ndarray:
        """Apply specific optimization (to be implemented by subclasses)"""        # Default implementation providing basic audio optimization
        logging.warning(f"Audio optimization not implemented for {self.__class__.__name__}")
        
        # Apply basic normalization as default optimization
        if len(audio_data) > 0:
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                return audio_data * 0.9 / max_val
        
        return audio_data
    
    def _calculate_metrics(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Calculate basic audio metrics"""        metrics = {}
        
        # RMS level
        metrics['rms_level'] = float(np.sqrt(np.mean(audio_data ** 2)))
        
        # Peak level
        metrics['peak_level'] = float(np.max(np.abs(audio_data)))
        
        # Dynamic range (simple estimate)
        if len(audio_data) > 1000:
            window_size = min(len(audio_data) // 10, 4096)
            rms_values = []
            for i in range(0, len(audio_data) - window_size, window_size):
                window_rms = np.sqrt(np.mean(audio_data[i:i+window_size] ** 2))
                if window_rms > 1e-10:
                    rms_values.append(window_rms)
            
            if len(rms_values) > 1:
                metrics['dynamic_range'] = float(20 * np.log10(np.max(rms_values) / (np.min(rms_values) + 1e-10)))
            else:
                metrics['dynamic_range'] = 0.0
        else:
            metrics['dynamic_range'] = 0.0
        
        # Spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        metrics['spectral_centroid'] = float(np.mean(spectral_centroids))
        
        return metrics
    
    def _calculate_improvement(
        self,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float]
    ) -> float:
        """Calculate overall quality improvement"""        # Simple improvement calculation based on key metrics
        improvements = []
        
        # Dynamic range improvement (higher is better)
        if 'dynamic_range' in before_metrics and 'dynamic_range' in after_metrics:
            dr_before = before_metrics['dynamic_range']
            dr_after = after_metrics['dynamic_range']
            if dr_before > 0:
                improvements.append((dr_after - dr_before) / dr_before)
        
        # RMS level consistency (depends on optimization type)
        if 'rms_level' in before_metrics and 'rms_level' in after_metrics:
            rms_before = before_metrics['rms_level']
            rms_after = after_metrics['rms_level']
            if rms_before > 0:
                # For most optimizations, we want to maintain or slightly improve RMS
                rms_change = abs(rms_after - rms_before) / rms_before
                improvements.append(-rms_change)  # Negative because less change is better
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get optimizer statistics"""        return {
            'optimization_type': self.optimization_type.value,
            'processing_count': self.processing_count,
            'success_count': self.success_count,
            'success_rate': self.success_count / max(self.processing_count, 1),
            'average_improvement': self.total_improvement / max(self.success_count, 1),
            'average_processing_time': self.total_processing_time / max(self.processing_count, 1)
        }


class NoiseReductionOptimizer(AudioOptimizer):
    """Noise reduction optimizer"""    
    def __init__(self):
        super().__init__(OptimizationType.NOISE_REDUCTION)
    
    async def _apply_optimization(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        level: OptimizationLevel,
        target_metrics: Optional[Dict[str, float]]
    ) -> np.ndarray:
        """Apply noise reduction"""        
        # Spectral subtraction-based noise reduction
        
        # Parameters based on optimization level
        if level == OptimizationLevel.MINIMAL:
            noise_factor = 1.5
            smoothing_factor = 0.7
        elif level == OptimizationLevel.MODERATE:
            noise_factor = 2.0
            smoothing_factor = 0.8
        elif level == OptimizationLevel.AGGRESSIVE:
            noise_factor = 2.5
            smoothing_factor = 0.9
        else:  # MAXIMUM
            noise_factor = 3.0
            smoothing_factor = 0.95
        
        # Estimate noise from initial silence
        noise_duration = min(len(audio_data) // 10, sample_rate // 2)  # Up to 0.5 seconds
        noise_sample = audio_data[:noise_duration]
        
        # FFT-based spectral subtraction
        n_fft = 2048
        hop_length = n_fft // 4
        
        # STFT
        stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise spectrum
        noise_stft = librosa.stft(noise_sample, n_fft=n_fft, hop_length=hop_length)
        noise_magnitude = np.mean(np.abs(noise_stft), axis=1, keepdims=True)
        
        # Spectral subtraction
        cleaned_magnitude = magnitude - noise_factor * noise_magnitude
        
        # Prevent over-subtraction
        cleaned_magnitude = np.maximum(cleaned_magnitude, magnitude * (1 - smoothing_factor))
        
        # Reconstruct signal
        cleaned_stft = cleaned_magnitude * np.exp(1j * phase)
        cleaned_audio = librosa.istft(cleaned_stft, hop_length=hop_length)
        
        # Ensure same length as input
        if len(cleaned_audio) > len(audio_data):
            cleaned_audio = cleaned_audio[:len(audio_data)]
        elif len(cleaned_audio) < len(audio_data):
            cleaned_audio = np.pad(cleaned_audio, (0, len(audio_data) - len(cleaned_audio)))
        
        return cleaned_audio


class DynamicRangeOptimizer(AudioOptimizer):
    """Dynamic range optimizer"""    
    def __init__(self):
        super().__init__(OptimizationType.DYNAMIC_RANGE)
    
    async def _apply_optimization(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        level: OptimizationLevel,
        target_metrics: Optional[Dict[str, float]]
    ) -> np.ndarray:
        """Apply dynamic range optimization"""        
        # Multi-band compressor/expander
        
        # Parameters based on level
        if level == OptimizationLevel.MINIMAL:
            ratio = 2.0
            threshold = -20
            attack = 0.005
            release = 0.1
        elif level == OptimizationLevel.MODERATE:
            ratio = 3.0
            threshold = -18
            attack = 0.003
            release = 0.08
        elif level == OptimizationLevel.AGGRESSIVE:
            ratio = 4.0
            threshold = -16
            attack = 0.002
            release = 0.06
        else:  # MAXIMUM
            ratio = 6.0
            threshold = -14
            attack = 0.001
            release = 0.04
        
        # Simple dynamic range processing
        processed_audio = self._apply_compression(
            audio_data, sample_rate, threshold, ratio, attack, release
        )
        
        return processed_audio
    
    def _apply_compression(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        threshold: float,
        ratio: float,
        attack: float,
        release: float
    ) -> np.ndarray:
        """Apply dynamic range compression"""        
        # Convert threshold to linear
        threshold_linear = 10 ** (threshold / 20)
        
        # Envelope following
        envelope = np.abs(audio_data)
        
        # Smooth envelope
        attack_samples = int(attack * sample_rate)
        release_samples = int(release * sample_rate)
        
        smoothed_envelope = np.zeros_like(envelope)
        smoothed_envelope[0] = envelope[0]
        
        for i in range(1, len(envelope)):
            if envelope[i] > smoothed_envelope[i-1]:
                # Attack
                alpha = 1.0 - np.exp(-1.0 / max(attack_samples, 1))
            else:
                # Release
                alpha = 1.0 - np.exp(-1.0 / max(release_samples, 1))
            
            smoothed_envelope[i] = alpha * envelope[i] + (1 - alpha) * smoothed_envelope[i-1]
        
        # Calculate gain reduction
        gain_reduction = np.ones_like(smoothed_envelope)
        above_threshold = smoothed_envelope > threshold_linear
        
        if np.any(above_threshold):
            excess = smoothed_envelope[above_threshold] / threshold_linear
            compressed_excess = np.power(excess, 1.0 / ratio)
            gain_reduction[above_threshold] = compressed_excess * threshold_linear / smoothed_envelope[above_threshold]
        
        # Apply gain reduction
        compressed_audio = audio_data * gain_reduction
        
        return compressed_audio


class FrequencyBalanceOptimizer(AudioOptimizer):
    """Frequency balance optimizer"""    
    def __init__(self):
        super().__init__(OptimizationType.FREQUENCY_BALANCE)
    
    async def _apply_optimization(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        level: OptimizationLevel,
        target_metrics: Optional[Dict[str, float]]
    ) -> np.ndarray:
        """Apply frequency balance optimization"""        
        # Multi-band EQ optimization
        
        # Analyze frequency content
        n_fft = 2048
        freqs = np.fft.fftfreq(n_fft, 1/sample_rate)[:n_fft//2]
        
        # Calculate current spectrum
        fft = np.fft.fft(audio_data[:n_fft] if len(audio_data) >= n_fft else np.pad(audio_data, (0, n_fft - len(audio_data))))
        magnitude = np.abs(fft[:n_fft//2])
        
        # Define frequency bands
        bands = {
            'low': (20, 250),
            'mid_low': (250, 1000),
            'mid': (1000, 4000),
            'mid_high': (4000, 8000),
            'high': (8000, sample_rate//2)
        }
        
        # Calculate band powers
        band_powers = {}
        for band_name, (low_freq, high_freq) in bands.items():
            band_mask = (freqs >= low_freq) & (freqs <= high_freq)
            band_powers[band_name] = np.sum(magnitude[band_mask] ** 2)
        
        # Target balance (adjustable)
        target_balance = {
            'low': 0.25,
            'mid_low': 0.30,
            'mid': 0.25,
            'mid_high': 0.15,
            'high': 0.05
        }
        
        # Calculate adjustments needed
        total_power = sum(band_powers.values())
        if total_power > 0:
            current_balance = {name: power / total_power for name, power in band_powers.items()}
            
            # Design EQ curve
            eq_curve = self._design_eq_curve(freqs, current_balance, target_balance, level)
            
            # Apply EQ
            balanced_audio = self._apply_frequency_eq(audio_data, sample_rate, eq_curve, freqs)
            
            return balanced_audio
        
        return audio_data
    
    def _design_eq_curve(
        self,
        freqs: np.ndarray,
        current_balance: Dict[str, float],
        target_balance: Dict[str, float],
        level: OptimizationLevel
    ) -> np.ndarray:
        """Design EQ curve to balance frequencies"""        
        # Calculate adjustment factors
        adjustments = {}
        for band in current_balance:
            if current_balance[band] > 0:
                adjustment = target_balance[band] / current_balance[band]
                # Limit adjustment based on level
                max_adjustment = {
                    OptimizationLevel.MINIMAL: 2.0,
                    OptimizationLevel.MODERATE: 3.0,
                    OptimizationLevel.AGGRESSIVE: 4.0,
                    OptimizationLevel.MAXIMUM: 6.0
                }[level]
                
                adjustments[band] = np.clip(adjustment, 1/max_adjustment, max_adjustment)
            else:
                adjustments[band] = 1.0
        
        # Create EQ curve
        eq_curve = np.ones_like(freqs)
        
        bands = {
            'low': (20, 250),
            'mid_low': (250, 1000),
            'mid': (1000, 4000),
            'mid_high': (4000, 8000),
            'high': (8000, freqs[-1])
        }
        
        for band_name, (low_freq, high_freq) in bands.items():
            band_mask = (freqs >= low_freq) & (freqs <= high_freq)
            eq_curve[band_mask] *= adjustments[band_name]
        
        return eq_curve
    
    def _apply_frequency_eq(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        eq_curve: np.ndarray,
        freqs: np.ndarray
    ) -> np.ndarray:
        """Apply frequency domain EQ"""        
        # FFT
        n_fft = len(eq_curve) * 2
        audio_fft = np.fft.fft(audio_data, n_fft)
        
        # Apply EQ curve (symmetric for negative frequencies)
        eq_full = np.concatenate([eq_curve, eq_curve[::-1]])
        equalized_fft = audio_fft * eq_full
        
        # IFFT
        equalized_audio = np.fft.ifft(equalized_fft).real
        
        # Trim to original length
        return equalized_audio[:len(audio_data)]


class LoudnessNormalizationOptimizer(AudioOptimizer):
    """Loudness normalization optimizer"""    
    def __init__(self):
        super().__init__(OptimizationType.LOUDNESS_NORMALIZATION)
    
    async def _apply_optimization(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        level: OptimizationLevel,
        target_metrics: Optional[Dict[str, float]]
    ) -> np.ndarray:
        """Apply loudness normalization"""        
        # Target loudness based on level or metrics
        if target_metrics and 'target_lufs' in target_metrics:
            target_lufs = target_metrics['target_lufs']
        else:
            target_lufs = -14.0  # Default Spotify loudness
        
        try:
            # Try to use pyloudnorm if available
            import pyloudnorm as pyln
            
            meter = pyln.Meter(sample_rate)
            current_loudness = meter.integrated_loudness(audio_data)
            
            if not np.isfinite(current_loudness):
                # Fallback to RMS-based normalization
                return self._rms_normalize(audio_data, target_lufs)
            
            # Calculate gain adjustment
            loudness_difference = target_lufs - current_loudness
            gain_linear = 10 ** (loudness_difference / 20)
            
            # Apply normalization
            normalized_audio = audio_data * gain_linear
            
            # Peak limiting to prevent clipping
            peak = np.max(np.abs(normalized_audio))
            if peak > 0.95:  # Leave some headroom
                normalized_audio = normalized_audio * (0.95 / peak)
            
            return normalized_audio
            
        except ImportError:
            # Fallback to RMS-based normalization
            return self._rms_normalize(audio_data, target_lufs)
    
    def _rms_normalize(self, audio_data: np.ndarray, target_lufs: float) -> np.ndarray:
        """RMS-based loudness normalization fallback"""        
        # Convert LUFS to approximate RMS (rough conversion)
        target_rms_db = target_lufs + 6  # Approximate conversion
        target_rms_linear = 10 ** (target_rms_db / 20)
        
        # Calculate current RMS
        current_rms = np.sqrt(np.mean(audio_data ** 2))
        
        if current_rms > 1e-10:
            # Calculate gain
            gain = target_rms_linear / current_rms
            
            # Apply gain with peak limiting
            normalized_audio = audio_data * gain
            peak = np.max(np.abs(normalized_audio))
            
            if peak > 0.95:
                normalized_audio = normalized_audio * (0.95 / peak)
            
            return normalized_audio
        
        return audio_data


class QualityOptimizer:
    """    🎯 Professional Quality Optimizer
    
    Complete audio quality optimization system:
    - Multi-stage optimization pipeline
    - Adaptive optimization strategies
    - Quality-driven optimization planning
    - Performance monitoring and analytics
    """    
    def __init__(self):
        self.optimizers: Dict[OptimizationType, AudioOptimizer] = {}
        self.optimization_history = []
        
        # Initialize optimizers
        self._initialize_optimizers()
        
        logger.info(f"QualityOptimizer initialized with {len(self.optimizers)} optimizers")
    
    def _initialize_optimizers(self):
        """Initialize audio optimizers"""        self.optimizers[OptimizationType.NOISE_REDUCTION] = NoiseReductionOptimizer()
        self.optimizers[OptimizationType.DYNAMIC_RANGE] = DynamicRangeOptimizer()
        self.optimizers[OptimizationType.FREQUENCY_BALANCE] = FrequencyBalanceOptimizer()
        self.optimizers[OptimizationType.LOUDNESS_NORMALIZATION] = LoudnessNormalizationOptimizer()
    
    async def optimize_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        quality_profile: QualityProfile,
        quality_report: QualityReport
    ) -> np.ndarray:
        """Optimize audio based on quality assessment"""        
        start_time = datetime.now()
        
        # Generate optimization plan
        plan = self._generate_optimization_plan(quality_report, quality_profile)
        
        current_audio = audio_data.copy()
        optimization_results = []
        
        # Apply optimizations in priority order
        for optimization_type in plan.priority_order:
            if optimization_type in self.optimizers:
                level = plan.levels[optimization_type]
                target_metrics = {}
                
                # Extract relevant target metrics
                if optimization_type == OptimizationType.LOUDNESS_NORMALIZATION:
                    if 'target_lufs' in quality_profile.requirements:
                        target_metrics['target_lufs'] = quality_profile.requirements['target_lufs']
                
                try:
                    optimizer = self.optimizers[optimization_type]
                    optimized_audio, result = await optimizer.optimize(
                        current_audio, sample_rate, level, target_metrics
                    )
                    
                    if result.success and result.quality_improvement > 0:
                        current_audio = optimized_audio
                        optimization_results.append(result)
                        logger.info(f"Applied {optimization_type.value}: {result.quality_improvement:.1%} improvement")
                    else:
                        logger.warning(f"Optimization {optimization_type.value} did not improve quality")
                
                except Exception as e:
                    logger.error(f"Optimization {optimization_type.value} failed: {e}")
                    continue
        
        # Record optimization history
        total_time = (datetime.now() - start_time).total_seconds()
        
        self.optimization_history.append({
            'timestamp': start_time,
            'plan': plan,
            'results': optimization_results,
            'total_improvement': sum(r.quality_improvement for r in optimization_results),
            'processing_time': total_time,
            'success': len(optimization_results) > 0
        })
        
        logger.info(f"Audio optimization completed in {total_time:.2f}s with {len(optimization_results)} optimizations applied")
        
        return current_audio
    
    def _generate_optimization_plan(
        self,
        quality_report: QualityReport,
        quality_profile: QualityProfile
    ) -> OptimizationPlan:
        """Generate optimization plan based on quality issues"""        
        optimizations = []
        levels = {}
        priority_order = []
        
        # Analyze quality issues from validation results
        issues = self._analyze_quality_issues(quality_report)
        
        # Plan optimizations based on issues
        for issue, severity in issues.items():
            optimization_type = self._map_issue_to_optimization(issue)
            if optimization_type:
                optimizations.append(optimization_type)
                levels[optimization_type] = self._determine_optimization_level(severity, quality_profile)
        
        # Determine priority order
        priority_order = self._prioritize_optimizations(optimizations, issues)
        
        # Calculate target metrics
        target_metrics = self._extract_target_metrics(quality_profile)
        
        # Estimate improvement and time
        estimated_improvement = self._estimate_improvement(optimizations, levels)
        estimated_time = self._estimate_processing_time(optimizations, levels)
        
        return OptimizationPlan(
            optimizations=optimizations,
            levels=levels,
            target_metrics=target_metrics,
            estimated_improvement=estimated_improvement,
            estimated_time=estimated_time,
            priority_order=priority_order
        )
    
    def _analyze_quality_issues(self, quality_report: QualityReport) -> Dict[str, float]:
        """Analyze quality issues from report"""        issues = {}
        
        # Check validation results
        for validation in quality_report.validation_results:
            if hasattr(validation, 'passed') and not validation.passed:
                test_name = getattr(validation, 'test_name', 'unknown')
                severity = 1.0  # Default severity
                
                # Map severity based on validation score
                if hasattr(validation, 'score'):
                    severity = 1.0 - validation.score
                
                issues[test_name] = severity
        
        # Check metric scores
        for score in quality_report.metrics.scores:
            if not score.passed and score.threshold is not None:
                severity = abs(score.value - score.threshold) / max(score.threshold, 0.001)
                issues[score.name] = min(severity, 1.0)
        
        return issues
    
    def _map_issue_to_optimization(self, issue: str) -> Optional[OptimizationType]:
        """Map quality issue to optimization type"""        
        issue_mapping = {
            'snr': OptimizationType.NOISE_REDUCTION,
            'noise_level': OptimizationType.NOISE_REDUCTION,
            'dynamic_range': OptimizationType.DYNAMIC_RANGE,
            'frequency_balance': OptimizationType.FREQUENCY_BALANCE,
            'loudness': OptimizationType.LOUDNESS_NORMALIZATION,
            'loudness_quality': OptimizationType.LOUDNESS_NORMALIZATION,
            'clipping': OptimizationType.PEAK_LIMITING,
            'peak_level': OptimizationType.PEAK_LIMITING
        }
        
        return issue_mapping.get(issue)
    
    def _determine_optimization_level(
        self,
        severity: float,
        quality_profile: QualityProfile
    ) -> OptimizationLevel:
        """Determine optimization level based on issue severity"""        
        # Base level on quality profile
        base_level = {
            'basic': OptimizationLevel.MINIMAL,
            'standard': OptimizationLevel.MODERATE,
            'high': OptimizationLevel.AGGRESSIVE,
            'premium': OptimizationLevel.MAXIMUM,
            'mastered': OptimizationLevel.MAXIMUM
        }.get(quality_profile.quality_level.value, OptimizationLevel.MODERATE)
        
        # Adjust based on severity
        if severity > 0.8:
            return OptimizationLevel.MAXIMUM
        elif severity > 0.6:
            return OptimizationLevel.AGGRESSIVE
        elif severity > 0.3:
            return OptimizationLevel.MODERATE
        else:
            return OptimizationLevel.MINIMAL
    
    def _prioritize_optimizations(
        self,
        optimizations: List[OptimizationType],
        issues: Dict[str, float]
    ) -> List[OptimizationType]:
        """Prioritize optimizations based on impact and dependencies"""        
        # Priority order based on typical processing pipeline
        priority_map = {
            OptimizationType.NOISE_REDUCTION: 1,
            OptimizationType.FREQUENCY_BALANCE: 2,
            OptimizationType.DYNAMIC_RANGE: 3,
            OptimizationType.LOUDNESS_NORMALIZATION: 4,
            OptimizationType.PEAK_LIMITING: 5,
            OptimizationType.STEREO_ENHANCEMENT: 6
        }
        
        # Sort by priority, with severity as secondary factor
        def priority_key(opt_type):
            base_priority = priority_map.get(opt_type, 10)
            # Find corresponding issue severity
            issue_severity = 0.0
            for issue, severity in issues.items():
                if self._map_issue_to_optimization(issue) == opt_type:
                    issue_severity = max(issue_severity, severity)
            
            # Lower number = higher priority
            return base_priority - issue_severity
        
        return sorted(optimizations, key=priority_key)
    
    def _extract_target_metrics(self, quality_profile: QualityProfile) -> Dict[str, float]:
        """Extract target metrics from quality profile"""        target_metrics = {}
        
        requirements = quality_profile.requirements
        
        if 'target_lufs' in requirements:
            target_metrics['target_lufs'] = requirements['target_lufs']
        
        if 'min_dynamic_range' in requirements:
            target_metrics['min_dynamic_range'] = requirements['min_dynamic_range']
        
        if 'min_snr' in requirements:
            target_metrics['min_snr'] = requirements['min_snr']
        
        return target_metrics
    
    def _estimate_improvement(
        self,
        optimizations: List[OptimizationType],
        levels: Dict[OptimizationType, OptimizationLevel]
    ) -> float:
        """Estimate quality improvement from optimizations"""        
        # Base improvement estimates per optimization type
        base_improvements = {
            OptimizationType.NOISE_REDUCTION: 0.15,
            OptimizationType.DYNAMIC_RANGE: 0.10,
            OptimizationType.FREQUENCY_BALANCE: 0.12,
            OptimizationType.LOUDNESS_NORMALIZATION: 0.08,
            OptimizationType.PEAK_LIMITING: 0.05
        }
        
        # Level multipliers
        level_multipliers = {
            OptimizationLevel.MINIMAL: 0.5,
            OptimizationLevel.MODERATE: 1.0,
            OptimizationLevel.AGGRESSIVE: 1.5,
            OptimizationLevel.MAXIMUM: 2.0
        }
        
        total_improvement = 0.0
        
        for opt_type in optimizations:
            base_imp = base_improvements.get(opt_type, 0.05)
            level_mult = level_multipliers.get(levels.get(opt_type, OptimizationLevel.MODERATE), 1.0)
            total_improvement += base_imp * level_mult
        
        # Diminishing returns for multiple optimizations
        return min(total_improvement * 0.8, 0.6)  # Cap at 60% improvement
    
    def _estimate_processing_time(
        self,
        optimizations: List[OptimizationType],
        levels: Dict[OptimizationType, OptimizationLevel]
    ) -> float:
        """Estimate total processing time"""        
        # Base processing times (seconds per minute of audio)
        base_times = {
            OptimizationType.NOISE_REDUCTION: 2.0,
            OptimizationType.DYNAMIC_RANGE: 0.5,
            OptimizationType.FREQUENCY_BALANCE: 1.0,
            OptimizationType.LOUDNESS_NORMALIZATION: 0.2,
            OptimizationType.PEAK_LIMITING: 0.1
        }
        
        # Level multipliers
        level_multipliers = {
            OptimizationLevel.MINIMAL: 0.5,
            OptimizationLevel.MODERATE: 1.0,
            OptimizationLevel.AGGRESSIVE: 2.0,
            OptimizationLevel.MAXIMUM: 3.0
        }
        
        total_time = 0.0
        
        for opt_type in optimizations:
            base_time = base_times.get(opt_type, 0.5)
            level_mult = level_multipliers.get(levels.get(opt_type, OptimizationLevel.MODERATE), 1.0)
            total_time += base_time * level_mult
        
        return total_time
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization performance statistics"""        
        if not self.optimization_history:
            return {'no_data': True}
        
        total_optimizations = len(self.optimization_history)
        successful_optimizations = len([h for h in self.optimization_history if h['success']])
        
        total_improvement = sum(h['total_improvement'] for h in self.optimization_history)
        total_time = sum(h['processing_time'] for h in self.optimization_history)
        
        # Optimizer-specific statistics
        optimizer_stats = {}
        for opt_type, optimizer in self.optimizers.items():
            optimizer_stats[opt_type.value] = optimizer.get_statistics()
        
        return {
            'total_optimizations': total_optimizations,
            'successful_optimizations': successful_optimizations,
            'success_rate': successful_optimizations / max(total_optimizations, 1),
            'average_improvement': total_improvement / max(successful_optimizations, 1),
            'average_processing_time': total_time / max(total_optimizations, 1),
            'optimizer_statistics': optimizer_stats
        }
    
    def add_custom_optimizer(self, optimizer: AudioOptimizer):
        """Add custom optimizer"""        self.optimizers[optimizer.optimization_type] = optimizer
        logger.info(f"Added custom optimizer: {optimizer.optimization_type.value}")
    
    def get_optimization_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get optimization history"""        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            h for h in self.optimization_history 
            if h['timestamp'] >= cutoff_time
        ]
