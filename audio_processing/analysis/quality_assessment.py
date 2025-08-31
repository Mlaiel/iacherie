"""✅ Audio Quality Assessment - Professional Audio Quality Analysis System

Advanced audio quality assessment engine providing comprehensive quality metrics,
distortion analysis, dynamic range measurement, and professional standards compliance.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
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
from scipy import stats


class QualityStandard(Enum):
    """Audio quality standards"""    BROADCAST = "broadcast"
    MASTERING = "mastering"
    STREAMING = "streaming"
    PODCAST = "podcast"
    MOBILE = "mobile"


class QualityGrade(Enum):
    """Quality grades"""    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class QualityMetrics:
    """Audio quality metrics"""    snr: float  # Signal-to-noise ratio (dB)
    thd: float  # Total harmonic distortion (%)
    dynamic_range: float  # Dynamic range (dB)
    peak_level: float  # Peak level (dBFS)
    rms_level: float  # RMS level (dBFS)
    lufs: float  # Loudness units relative to full scale
    true_peak: float  # True peak level (dBTP)
    crest_factor: float  # Crest factor (dB)
    stereo_correlation: float  # Stereo correlation
    phase_coherence: float  # Phase coherence
    frequency_response_deviation: float  # Frequency response deviation
    noise_floor: float  # Noise floor (dBFS)


@dataclass
class DistortionAnalysis:
    """Distortion analysis results"""    total_harmonic_distortion: float
    harmonic_distortion_spectrum: np.ndarray
    intermodulation_distortion: float
    clipping_percentage: float
    digital_artifacts: Dict[str, float]
    aliasing_level: float


@dataclass
class QualityAssessmentResult:
    """Complete quality assessment results"""    overall_grade: QualityGrade
    overall_score: float  # 0-100
    quality_metrics: QualityMetrics
    distortion_analysis: DistortionAnalysis
    compliance_report: Dict[str, bool]
    improvement_suggestions: List[str]
    technical_issues: List[str]
    mastering_recommendations: Dict[str, Any]
    streaming_readiness: Dict[str, float]  # Platform readiness scores


class AudioQualityAssessment:
    """    ✅ Professional Audio Quality Assessment Engine
    
    Comprehensive quality analysis with professional standards compliance,
    distortion detection, dynamic range analysis, and mastering recommendations.
    """    
    def __init__(self,
                 sample_rate: int = 44100,
                 quality_standard: QualityStandard = QualityStandard.MASTERING,
                 reference_level: float = -23.0):  # LUFS
        """        Initialize quality assessment engine
        
        Args:
            sample_rate: Audio sample rate
            quality_standard: Target quality standard
            reference_level: Reference loudness level (LUFS)
        """        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.quality_standard = quality_standard
        self.reference_level = reference_level
        
        # Quality thresholds for different standards
        self.quality_thresholds = {
            QualityStandard.BROADCAST: {
                'snr_min': 60.0,
                'thd_max': 0.1,
                'dynamic_range_min': 20.0,
                'peak_max': -1.0,
                'lufs_target': -23.0,
                'lufs_tolerance': 1.0
            },
            QualityStandard.MASTERING: {
                'snr_min': 80.0,
                'thd_max': 0.01,
                'dynamic_range_min': 14.0,
                'peak_max': -0.1,
                'lufs_target': -14.0,
                'lufs_tolerance': 1.0
            },
            QualityStandard.STREAMING: {
                'snr_min': 50.0,
                'thd_max': 0.5,
                'dynamic_range_min': 7.0,
                'peak_max': -1.0,
                'lufs_target': -14.0,
                'lufs_tolerance': 2.0
            },
            QualityStandard.PODCAST: {
                'snr_min': 40.0,
                'thd_max': 1.0,
                'dynamic_range_min': 10.0,
                'peak_max': -3.0,
                'lufs_target': -16.0,
                'lufs_tolerance': 2.0
            }
        }
        
        # Streaming platform requirements
        self.streaming_standards = {
            'spotify': {'lufs': -14.0, 'peak': -1.0, 'dynamic_range_min': 6.0},
            'apple_music': {'lufs': -16.0, 'peak': -1.0, 'dynamic_range_min': 7.0},
            'youtube': {'lufs': -14.0, 'peak': -1.0, 'dynamic_range_min': 5.0},
            'soundcloud': {'lufs': -14.0, 'peak': -1.0, 'dynamic_range_min': 6.0},
            'tidal': {'lufs': -14.0, 'peak': -1.0, 'dynamic_range_min': 8.0}
        }
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self.logger.info(f"AudioQualityAssessment initialized: {quality_standard.value} standard")
    
    async def assess_quality(self, 
                           audio_data: np.ndarray,
                           channels: int = 2) -> QualityAssessmentResult:
        """        Perform comprehensive audio quality assessment
        
        Args:
            audio_data: Input audio signal
            channels: Number of audio channels
            
        Returns:
            Complete quality assessment results
        """        try:
            self.logger.info("Starting quality assessment...")
            
            # Ensure proper format
            if audio_data.ndim == 1 and channels == 2:
                # Convert mono to stereo for analysis
                audio_data = np.column_stack([audio_data, audio_data])
            elif audio_data.ndim == 2 and channels == 1:
                # Convert stereo to mono
                audio_data = np.mean(audio_data, axis=1)
            
            # Parallel quality analysis
            tasks = [
                self._compute_quality_metrics(audio_data, channels),
                self._analyze_distortion(audio_data),
                self._analyze_loudness(audio_data),
                self._analyze_frequency_response(audio_data)
            ]
            
            results = await asyncio.gather(*tasks)
            basic_metrics, distortion_analysis, loudness_metrics, freq_response = results
            
            # Combine metrics
            quality_metrics = self._combine_metrics(basic_metrics, loudness_metrics, freq_response)
            
            # Assess compliance
            compliance_report = await self._assess_compliance(quality_metrics)
            
            # Generate recommendations
            improvement_suggestions = await self._generate_improvement_suggestions(quality_metrics, distortion_analysis)
            technical_issues = await self._identify_technical_issues(quality_metrics, distortion_analysis)
            mastering_recommendations = await self._generate_mastering_recommendations(quality_metrics)
            streaming_readiness = await self._assess_streaming_readiness(quality_metrics)
            
            # Calculate overall grade and score
            overall_score, overall_grade = await self._calculate_overall_quality(quality_metrics, distortion_analysis)
            
            # Create assessment result
            result = QualityAssessmentResult(
                overall_grade=overall_grade,
                overall_score=overall_score,
                quality_metrics=quality_metrics,
                distortion_analysis=distortion_analysis,
                compliance_report=compliance_report,
                improvement_suggestions=improvement_suggestions,
                technical_issues=technical_issues,
                mastering_recommendations=mastering_recommendations,
                streaming_readiness=streaming_readiness
            )
            
            self.logger.info(f"Quality assessment completed: {overall_grade.value} ({overall_score:.1f}/100)")
            return result
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            raise
    
    async def _compute_quality_metrics(self, 
                                     audio_data: np.ndarray, 
                                     channels: int) -> Dict[str, float]:
        """Compute basic quality metrics"""        def compute():
            metrics = {}
            
            # Handle mono/stereo
            if audio_data.ndim == 1:
                audio_mono = audio_data
                audio_stereo = None
            else:
                audio_mono = np.mean(audio_data, axis=1) if audio_data.ndim == 2 else audio_data
                audio_stereo = audio_data if audio_data.ndim == 2 else None
            
            # Peak level (dBFS)
            peak_linear = np.max(np.abs(audio_mono))
            peak_db = 20 * np.log10(peak_linear + 1e-10)
            metrics['peak_level'] = float(peak_db)
            
            # RMS level (dBFS)
            rms_linear = np.sqrt(np.mean(audio_mono ** 2))
            rms_db = 20 * np.log10(rms_linear + 1e-10)
            metrics['rms_level'] = float(rms_db)
            
            # Crest factor
            crest_factor = 20 * np.log10((peak_linear + 1e-10) / (rms_linear + 1e-10))
            metrics['crest_factor'] = float(crest_factor)
            
            # Dynamic range (simplified)
            percentile_95 = np.percentile(np.abs(audio_mono), 95)
            percentile_10 = np.percentile(np.abs(audio_mono), 10)
            dynamic_range = 20 * np.log10((percentile_95 + 1e-10) / (percentile_10 + 1e-10))
            metrics['dynamic_range'] = float(dynamic_range)
            
            # Noise floor
            noise_floor = 20 * np.log10(percentile_10 + 1e-10)
            metrics['noise_floor'] = float(noise_floor)
            
            # SNR
            signal_level = 20 * np.log10(rms_linear + 1e-10)
            snr = signal_level - noise_floor
            metrics['snr'] = float(snr)
            
            # Stereo correlation (if stereo)
            if audio_stereo is not None and audio_stereo.shape[1] >= 2:
                left = audio_stereo[:, 0]
                right = audio_stereo[:, 1]
                correlation = np.corrcoef(left, right)[0, 1]
                metrics['stereo_correlation'] = float(correlation if not np.isnan(correlation) else 0.0)
                
                # Phase coherence
                cross_correlation = np.correlate(left, right, mode='full')
                max_correlation = np.max(np.abs(cross_correlation))
                metrics['phase_coherence'] = float(max_correlation / (len(left) + 1e-10))
            else:
                metrics['stereo_correlation'] = 1.0  # Mono
                metrics['phase_coherence'] = 1.0
            
            return metrics
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, compute)
    
    async def _analyze_distortion(self, audio_data: np.ndarray) -> DistortionAnalysis:
        """Analyze various types of distortion"""        def analyze():
            # Convert to mono for analysis
            if audio_data.ndim == 2:
                mono_audio = np.mean(audio_data, axis=1)
            else:
                mono_audio = audio_data
            
            # THD analysis
            thd, harmonic_spectrum = self._compute_thd(mono_audio)
            
            # Clipping detection
            clipping_percentage = self._detect_clipping(mono_audio)
            
            # Digital artifacts detection
            digital_artifacts = self._detect_digital_artifacts(mono_audio)
            
            # Aliasing detection
            aliasing_level = self._detect_aliasing(mono_audio)
            
            # Intermodulation distortion (simplified)
            imd = self._compute_imd(mono_audio)
            
            return DistortionAnalysis(
                total_harmonic_distortion=thd,
                harmonic_distortion_spectrum=harmonic_spectrum,
                intermodulation_distortion=imd,
                clipping_percentage=clipping_percentage,
                digital_artifacts=digital_artifacts,
                aliasing_level=aliasing_level
            )
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    def _compute_thd(self, audio_data: np.ndarray) -> Tuple[float, np.ndarray]:
        """Compute total harmonic distortion"""        try:
            # FFT analysis
            fft_data = np.fft.fft(audio_data)
            magnitude = np.abs(fft_data[:len(fft_data)//2])
            
            # Find fundamental frequency
            fundamental_bin = np.argmax(magnitude[10:]) + 10  # Skip DC and low frequencies
            fundamental_magnitude = magnitude[fundamental_bin]
            
            # Find harmonics (2nd through 10th)
            harmonic_magnitudes = []
            for h in range(2, 11):
                harmonic_bin = fundamental_bin * h
                if harmonic_bin < len(magnitude):
                    harmonic_magnitudes.append(magnitude[harmonic_bin])
                else:
                    harmonic_magnitudes.append(0.0)
            
            # Calculate THD
            harmonics_power = np.sum(np.array(harmonic_magnitudes) ** 2)
            fundamental_power = fundamental_magnitude ** 2
            
            thd_ratio = np.sqrt(harmonics_power) / (fundamental_magnitude + 1e-10)
            thd_percentage = thd_ratio * 100
            
            return float(thd_percentage), np.array(harmonic_magnitudes)
            
        except Exception as e:
            self.logger.warning(f"THD computation failed: {e}")
            return 0.0, np.array([])
    
    def _detect_clipping(self, audio_data: np.ndarray) -> float:
        """Detect hard clipping"""        # Find samples at or near full scale
        threshold = 0.99  # 99% of full scale
        clipped_samples = np.sum(np.abs(audio_data) >= threshold)
        clipping_percentage = (clipped_samples / len(audio_data)) * 100
        
        return float(clipping_percentage)
    
    def _detect_digital_artifacts(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Detect various digital artifacts"""        artifacts = {}
        
        # Intersample peaks (simplified)
        upsampled = scipy.signal.resample(audio_data, len(audio_data) * 4)
        intersample_peaks = np.max(np.abs(upsampled))
        artifacts['intersample_peaks'] = float(20 * np.log10(intersample_peaks + 1e-10))
        
        # Digital noise (high frequency content)
        nyquist = self.sample_rate // 2
        high_freq_threshold = nyquist * 0.8
        
        fft_data = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
        magnitude = np.abs(fft_data)
        
        high_freq_mask = np.abs(freqs) > high_freq_threshold
        high_freq_energy = np.sum(magnitude[high_freq_mask] ** 2)
        total_energy = np.sum(magnitude ** 2)
        
        artifacts['digital_noise'] = float(high_freq_energy / (total_energy + 1e-10))
        
        return artifacts
    
    def _detect_aliasing(self, audio_data: np.ndarray) -> float:
        """Detect aliasing artifacts"""        # Simple aliasing detection based on high-frequency content
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        
        # Check energy near Nyquist frequency
        nyquist_region = magnitude[-len(magnitude)//10:]  # Top 10% of spectrum
        total_energy = np.sum(magnitude ** 2)
        nyquist_energy = np.sum(nyquist_region ** 2)
        
        aliasing_ratio = nyquist_energy / (total_energy + 1e-10)
        
        return float(aliasing_ratio)
    
    def _compute_imd(self, audio_data: np.ndarray) -> float:
        """Compute intermodulation distortion (simplified)"""        # This is a simplified IMD estimation
        # Real IMD would require injecting test tones
        
        # Use spectral analysis to estimate IMD products
        fft_data = np.fft.fft(audio_data)
        magnitude = np.abs(fft_data[:len(fft_data)//2])
        
        # Look for intermodulation products (simplified heuristic)
        peaks, _ = scipy.signal.find_peaks(magnitude, height=np.max(magnitude) * 0.1)
        
        if len(peaks) > 2:
            # Estimate IMD based on peak relationships
            imd_estimate = np.std(magnitude[peaks[2:]]) / (np.max(magnitude) + 1e-10)
        else:
            imd_estimate = 0.0
        
        return float(imd_estimate * 100)  # Convert to percentage
    
    async def _analyze_loudness(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Analyze loudness metrics (LUFS, True Peak)"""        def analyze():
            loudness_metrics = {}
            
            # Simplified LUFS calculation
            # Real implementation would use ITU-R BS.1770-4 standard
            rms = np.sqrt(np.mean(audio_data ** 2))
            lufs_approx = -0.691 + 10 * np.log10(rms + 1e-10)
            loudness_metrics['lufs'] = float(lufs_approx)
            
            # True peak calculation (simplified)
            # Real implementation would use ITU-R BS.1770-4 true peak measurement
            upsampled = scipy.signal.resample(audio_data, len(audio_data) * 4)
            true_peak_linear = np.max(np.abs(upsampled))
            true_peak_db = 20 * np.log10(true_peak_linear + 1e-10)
            loudness_metrics['true_peak'] = float(true_peak_db)
            
            return loudness_metrics
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    async def _analyze_frequency_response(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Analyze frequency response characteristics"""        def analyze():
            freq_metrics = {}
            
            # FFT analysis
            fft_data = np.fft.fft(audio_data)
            magnitude = np.abs(fft_data[:len(fft_data)//2])
            freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)[:len(magnitude)]
            
            # Frequency response deviation from flat
            # Divide spectrum into octave bands
            octave_bands = [
                (20, 40), (40, 80), (80, 160), (160, 320),
                (320, 640), (640, 1280), (1280, 2560),
                (2560, 5120), (5120, 10240), (10240, 20000)
            ]
            
            band_energies = []
            for low_freq, high_freq in octave_bands:
                band_mask = (freqs >= low_freq) & (freqs < high_freq)
                band_energy = np.sum(magnitude[band_mask] ** 2)
                band_energies.append(band_energy)
            
            # Calculate deviation from flat response
            if len(band_energies) > 0:
                mean_energy = np.mean(band_energies)
                deviation = np.std(band_energies) / (mean_energy + 1e-10)
            else:
                deviation = 0.0
            
            freq_metrics['frequency_response_deviation'] = float(deviation)
            
            return freq_metrics
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, analyze)
    
    def _combine_metrics(self, 
                        basic_metrics: Dict[str, float], 
                        loudness_metrics: Dict[str, float],
                        freq_metrics: Dict[str, float]) -> QualityMetrics:
        """Combine all metrics into QualityMetrics object"""        return QualityMetrics(
            snr=basic_metrics.get('snr', 0.0),
            thd=0.0,  # Will be filled from distortion analysis
            dynamic_range=basic_metrics.get('dynamic_range', 0.0),
            peak_level=basic_metrics.get('peak_level', 0.0),
            rms_level=basic_metrics.get('rms_level', 0.0),
            lufs=loudness_metrics.get('lufs', 0.0),
            true_peak=loudness_metrics.get('true_peak', 0.0),
            crest_factor=basic_metrics.get('crest_factor', 0.0),
            stereo_correlation=basic_metrics.get('stereo_correlation', 1.0),
            phase_coherence=basic_metrics.get('phase_coherence', 1.0),
            frequency_response_deviation=freq_metrics.get('frequency_response_deviation', 0.0),
            noise_floor=basic_metrics.get('noise_floor', -60.0)
        )
    
    async def _assess_compliance(self, metrics: QualityMetrics) -> Dict[str, bool]:
        """Assess compliance with quality standards"""        def assess():
            thresholds = self.quality_thresholds[self.quality_standard]
            
            compliance = {
                'snr_compliant': metrics.snr >= thresholds['snr_min'],
                'thd_compliant': metrics.thd <= thresholds['thd_max'],
                'dynamic_range_compliant': metrics.dynamic_range >= thresholds['dynamic_range_min'],
                'peak_level_compliant': metrics.peak_level <= thresholds['peak_max'],
                'loudness_compliant': abs(metrics.lufs - thresholds['lufs_target']) <= thresholds['lufs_tolerance']
            }
            
            return compliance
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, assess)
    
    async def _generate_improvement_suggestions(self, 
                                              metrics: QualityMetrics, 
                                              distortion: DistortionAnalysis) -> List[str]:
        """Generate improvement suggestions"""        def generate():
            suggestions = []
            
            if metrics.snr < 50:
                suggestions.append("Reduce background noise using noise reduction techniques")
            
            if distortion.total_harmonic_distortion > 1.0:
                suggestions.append("Check for overdriven preamps or converters causing distortion")
            
            if distortion.clipping_percentage > 0.1:
                suggestions.append("Reduce input levels to prevent digital clipping")
            
            if metrics.dynamic_range < 10:
                suggestions.append("Reduce compression to preserve dynamic range")
            
            if metrics.peak_level > -1.0:
                suggestions.append("Apply limiting to prevent intersample peaks")
            
            if abs(metrics.lufs - self.reference_level) > 2.0:
                suggestions.append(f"Adjust loudness to target {self.reference_level} LUFS")
            
            if metrics.frequency_response_deviation > 0.3:
                suggestions.append("Apply equalization to achieve flatter frequency response")
            
            return suggestions
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, generate)
    
    async def _identify_technical_issues(self, 
                                       metrics: QualityMetrics, 
                                       distortion: DistortionAnalysis) -> List[str]:
        """Identify technical issues"""        def identify():
            issues = []
            
            if distortion.clipping_percentage > 0.01:
                issues.append(f"Hard clipping detected in {distortion.clipping_percentage:.2f}% of samples")
            
            if distortion.total_harmonic_distortion > 5.0:
                issues.append("Excessive harmonic distortion detected")
            
            if metrics.stereo_correlation < -0.5:
                issues.append("Phase issues detected between stereo channels")
            
            if distortion.aliasing_level > 0.01:
                issues.append("Aliasing artifacts detected")
            
            if metrics.noise_floor > -40:
                issues.append("High noise floor detected")
            
            return issues
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, identify)
    
    async def _generate_mastering_recommendations(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Generate mastering recommendations"""        def generate():
            recommendations = {}
            
            # EQ recommendations
            if metrics.frequency_response_deviation > 0.2:
                recommendations['eq'] = "Apply corrective EQ to balance frequency response"
            
            # Compression recommendations
            if metrics.dynamic_range > 20:
                recommendations['compression'] = "Consider gentle compression to control dynamics"
            elif metrics.dynamic_range < 6:
                recommendations['compression'] = "Reduce compression to preserve dynamics"
            
            # Limiting recommendations
            if metrics.peak_level > -0.5:
                recommendations['limiting'] = "Apply brick-wall limiting at -0.1 dBFS"
            
            # Loudness recommendations
            target_lufs = self.quality_thresholds[self.quality_standard]['lufs_target']
            current_lufs = metrics.lufs
            
            if current_lufs < target_lufs - 1:
                recommendations['loudness'] = f"Increase loudness by {target_lufs - current_lufs:.1f} LU"
            elif current_lufs > target_lufs + 1:
                recommendations['loudness'] = f"Reduce loudness by {current_lufs - target_lufs:.1f} LU"
            
            return recommendations
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, generate)
    
    async def _assess_streaming_readiness(self, metrics: QualityMetrics) -> Dict[str, float]:
        """Assess readiness for streaming platforms"""        def assess():
            readiness_scores = {}
            
            for platform, standards in self.streaming_standards.items():
                score = 0.0
                
                # Loudness compliance
                lufs_diff = abs(metrics.lufs - standards['lufs'])
                lufs_score = max(0, 1 - lufs_diff / 3.0)  # 3 LU tolerance
                
                # Peak compliance
                peak_score = 1.0 if metrics.peak_level <= standards['peak'] else 0.5
                
                # Dynamic range compliance
                dr_score = 1.0 if metrics.dynamic_range >= standards['dynamic_range_min'] else 0.7
                
                # Overall score
                score = (lufs_score * 0.5 + peak_score * 0.3 + dr_score * 0.2) * 100
                
                readiness_scores[platform] = float(score)
            
            return readiness_scores
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, assess)
    
    async def _calculate_overall_quality(self, 
                                       metrics: QualityMetrics, 
                                       distortion: DistortionAnalysis) -> Tuple[float, QualityGrade]:
        """Calculate overall quality score and grade"""        def calculate():
            score_components = []
            
            # SNR score (0-25 points)
            snr_score = min(25, metrics.snr / 80 * 25)
            score_components.append(snr_score)
            
            # Distortion score (0-25 points)
            thd_score = max(0, 25 - distortion.total_harmonic_distortion * 2.5)
            score_components.append(thd_score)
            
            # Dynamic range score (0-20 points)
            dr_score = min(20, metrics.dynamic_range / 20 * 20)
            score_components.append(dr_score)
            
            # Peak level score (0-15 points)
            peak_score = 15 if metrics.peak_level <= -0.1 else max(0, 15 + metrics.peak_level * 3)
            score_components.append(peak_score)
            
            # Frequency response score (0-15 points)
            freq_score = max(0, 15 - metrics.frequency_response_deviation * 30)
            score_components.append(freq_score)
            
            # Total score
            total_score = sum(score_components)
            
            # Determine grade
            if total_score >= 90:
                grade = QualityGrade.EXCELLENT
            elif total_score >= 75:
                grade = QualityGrade.GOOD
            elif total_score >= 60:
                grade = QualityGrade.ACCEPTABLE
            elif total_score >= 40:
                grade = QualityGrade.POOR
            else:
                grade = QualityGrade.UNACCEPTABLE
            
            return float(total_score), grade
        
        return await asyncio.get_event_loop().run_in_executor(self.executor, calculate)
    
    def assess_real_time_quality(self, frame: np.ndarray) -> Dict[str, float]:
        """        Real-time quality assessment for single frame
        Optimized for low-latency processing
        """        try:
            # Basic quality metrics for current frame
            peak_level = 20 * np.log10(np.max(np.abs(frame)) + 1e-10)
            rms_level = 20 * np.log10(np.sqrt(np.mean(frame ** 2)) + 1e-10)
            
            # Simple clipping detection
            clipping = np.sum(np.abs(frame) >= 0.99) / len(frame)
            
            # Crest factor
            crest_factor = peak_level - rms_level
            
            return {
                'peak_level': float(peak_level),
                'rms_level': float(rms_level),
                'crest_factor': float(crest_factor),
                'clipping_percentage': float(clipping * 100),
                'quality_indicator': float(max(0, min(1, (60 + rms_level) / 60)))  # Simplified quality
            }
            
        except Exception as e:
            self.logger.error(f"Real-time quality assessment failed: {e}")
            return {
                'peak_level': -60.0,
                'rms_level': -60.0,
                'crest_factor': 0.0,
                'clipping_percentage': 0.0,
                'quality_indicator': 0.0
            }
    
    def __del__(self):
        """Cleanup thread pool"""        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
