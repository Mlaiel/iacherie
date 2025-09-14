try:
    import librosa
except ImportError:
    from ..validation_engines import _mock_librosa as librosa

#!/usr/bin/env python3
"""
Audio Quality Testing Module - Ainflue Quality Platform
=====================================================

Enterprise-grade audio quality testing and analysis system.
Demonstrates Audio Engineer + ML Engineer + Backend Senior expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import wave
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import numpy as np
import scipy.signal
from scipy.fftpack import fft, ifft
from scipy.io import wavfile
# librosa imported at top of file with fallback to mock
try:
    import matplotlib.pyplot as plt
except ImportError:
    # Mock matplotlib if not available
    class MockPlt:
        def figure(self, *args, **kwargs): pass
        def subplot(self, *args, **kwargs): pass
        def plot(self, *args, **kwargs): pass
        def title(self, *args, **kwargs): pass
        def xlabel(self, *args, **kwargs): pass
        def ylabel(self, *args, **kwargs): pass
        def show(self, *args, **kwargs): pass
        def savefig(self, *args, **kwargs): pass
    plt = MockPlt()

try:
    import soundfile as sf
except ImportError:
    sf = None

try:
    from pydub import AudioSegment
    from pydub.utils import which
except ImportError:
    AudioSegment = None
    which = None

import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AudioMetrics:
    """Audio quality metrics."""
    sample_rate: int
    duration_seconds: float
    channels: int
    bit_depth: int
    file_size_bytes: int
    peak_amplitude: float
    rms_level: float
    dynamic_range: float
    snr_db: float
    thd_percent: float
    frequency_response: Dict[str, float]
    spectral_centroid: float
    spectral_rolloff: float
    zero_crossing_rate: float
    tempo: Optional[float] = None


@dataclass
class AudioQualityResult:
    """Audio quality test result."""
    test_name: str
    file_path: str
    status: str  # 'passed', 'failed', 'warning', 'error'
    quality_score: float  # 0-100
    metrics: AudioMetrics
    issues_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AudioTestSuite:
    """Audio test suite configuration."""
    name: str
    input_directory: str
    output_directory: str
    test_categories: List[str] = field(default_factory=list)
    quality_thresholds: Dict[str, float] = field(default_factory=dict)
    supported_formats: List[str] = field(default_factory=lambda: ['wav', 'mp3', 'flac', 'aac', 'm4a'])
    max_file_size_mb: float = 100.0
    min_duration_seconds: float = 1.0
    max_duration_seconds: float = 3600.0


class AudioAnalyzer:
    """Core audio analysis engine."""
    
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3', '.flac', '.aac', '.m4a', '.ogg']
        
        # Quality thresholds
        self.quality_thresholds = {
            'min_sample_rate': 44100,
            'min_bit_depth': 16,
            'max_thd_percent': 1.0,
            'min_snr_db': 60.0,
            'min_dynamic_range': 20.0,
            'max_peak_amplitude': 0.95
        }
    
    async def analyze_audio_file(self, file_path: str) -> AudioMetrics:
        """Analyze audio file and extract quality metrics."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {file_path.suffix}")
        
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(str(file_path), sr=None, mono=False)
            
            # Handle stereo/mono
            if audio_data.ndim == 1:
                channels = 1
                mono_audio = audio_data
            else:
                channels = audio_data.shape[0]
                mono_audio = librosa.to_mono(audio_data)
            
            # Basic file information
            file_size = file_path.stat().st_size
            duration = len(mono_audio) / sample_rate
            
            # Determine bit depth
            bit_depth = await self._estimate_bit_depth(file_path)
            
            # Calculate audio metrics
            peak_amplitude = np.max(np.abs(mono_audio))
            rms_level = np.sqrt(np.mean(mono_audio ** 2))
            
            # Dynamic range analysis
            dynamic_range = await self._calculate_dynamic_range(mono_audio)
            
            # Signal-to-noise ratio
            snr_db = await self._calculate_snr(mono_audio)
            
            # Total harmonic distortion
            thd_percent = await self._calculate_thd(mono_audio, sample_rate)
            
            # Frequency response analysis
            frequency_response = await self._analyze_frequency_response(mono_audio, sample_rate)
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=mono_audio, sr=sample_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=mono_audio, sr=sample_rate))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(mono_audio))
            
            # Tempo detection (if musical content)
            try:
                tempo, _ = librosa.beat.beat_track(y=mono_audio, sr=sample_rate)
                tempo = float(tempo)
            except:
                tempo = None
            
            return AudioMetrics(
                sample_rate=sample_rate,
                duration_seconds=duration,
                channels=channels,
                bit_depth=bit_depth,
                file_size_bytes=file_size,
                peak_amplitude=peak_amplitude,
                rms_level=rms_level,
                dynamic_range=dynamic_range,
                snr_db=snr_db,
                thd_percent=thd_percent,
                frequency_response=frequency_response,
                spectral_centroid=spectral_centroid,
                spectral_rolloff=spectral_rolloff,
                zero_crossing_rate=zero_crossing_rate,
                tempo=tempo
            )
            
        except Exception as e:
            logger.error(f"Audio analysis failed for {file_path}: {e}")
            raise
    
    async def _estimate_bit_depth(self, file_path: Path) -> int:
        """Estimate bit depth of audio file."""
        try:
            # Try to get bit depth from file info
            info = sf.info(str(file_path))
            
            # Map subtype to bit depth
            subtype_map = {
                'PCM_16': 16,
                'PCM_24': 24,
                'PCM_32': 32,
                'FLOAT': 32,
                'DOUBLE': 64
            }
            
            return subtype_map.get(info.subtype, 16)
            
        except:
            # Fallback to default
            return 16
    
    async def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """Calculate dynamic range in dB."""
        try:
            # Calculate RMS in sliding windows
            window_size = len(audio_data) // 100  # 1% windows
            if window_size < 1024:
                window_size = min(1024, len(audio_data))
            
            rms_values = []
            for i in range(0, len(audio_data) - window_size, window_size):
                window = audio_data[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                if rms > 0:
                    rms_values.append(rms)
            
            if not rms_values:
                return 0.0
            
            # Dynamic range = max RMS - min RMS (in dB)
            max_rms = max(rms_values)
            min_rms = min(rms_values)
            
            if min_rms > 0:
                dynamic_range = 20 * np.log10(max_rms / min_rms)
            else:
                dynamic_range = 60.0  # Default high value
            
            return max(0.0, dynamic_range)
            
        except Exception as e:
            logger.warning(f"Dynamic range calculation failed: {e}")
            return 0.0
    
    async def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio."""
        try:
            # Estimate noise from silent segments
            # Find segments with low energy
            frame_size = 2048
            energy_threshold = 0.01 * np.max(np.abs(audio_data))
            
            noise_segments = []
            for i in range(0, len(audio_data) - frame_size, frame_size):
                frame = audio_data[i:i + frame_size]
                if np.max(np.abs(frame)) < energy_threshold:
                    noise_segments.extend(frame)
            
            if len(noise_segments) < 100:
                # Not enough quiet segments, estimate from full signal
                signal_power = np.mean(audio_data ** 2)
                noise_power = signal_power * 0.01  # Assume 1% noise
            else:
                noise_segments = np.array(noise_segments)
                signal_power = np.mean(audio_data ** 2)
                noise_power = np.mean(noise_segments ** 2)
            
            if noise_power > 0:
                snr_db = 10 * np.log10(signal_power / noise_power)
            else:
                snr_db = 80.0  # Very high SNR
            
            return max(0.0, snr_db)
            
        except Exception as e:
            logger.warning(f"SNR calculation failed: {e}")
            return 60.0  # Default good value
    
    async def _calculate_thd(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate Total Harmonic Distortion."""
        try:
            # Use FFT to analyze harmonics
            fft_size = min(8192, len(audio_data))
            if len(audio_data) < fft_size:
                audio_data = np.pad(audio_data, (0, fft_size - len(audio_data)))
            
            # Window the signal
            window = np.hanning(fft_size)
            windowed_signal = audio_data[:fft_size] * window
            
            # Compute FFT
            spectrum = np.abs(fft(windowed_signal))
            freqs = np.fft.fftfreq(fft_size, 1/sample_rate)
            
            # Find fundamental frequency (peak in spectrum)
            positive_freqs = freqs[:fft_size//2]
            positive_spectrum = spectrum[:fft_size//2]
            
            # Find peak in reasonable frequency range (80-2000 Hz)
            min_freq_idx = np.argmin(np.abs(positive_freqs - 80))
            max_freq_idx = np.argmin(np.abs(positive_freqs - 2000))
            
            search_spectrum = positive_spectrum[min_freq_idx:max_freq_idx]
            if len(search_spectrum) == 0:
                return 0.0
            
            fundamental_idx = min_freq_idx + np.argmax(search_spectrum)
            fundamental_freq = positive_freqs[fundamental_idx]
            fundamental_power = positive_spectrum[fundamental_idx] ** 2
            
            # Find harmonics
            harmonic_power = 0
            for harmonic in range(2, 6):  # 2nd to 5th harmonic
                harmonic_freq = fundamental_freq * harmonic
                if harmonic_freq >= sample_rate / 2:
                    break
                
                harmonic_idx = np.argmin(np.abs(positive_freqs - harmonic_freq))
                harmonic_power += positive_spectrum[harmonic_idx] ** 2
            
            # Calculate THD
            if fundamental_power > 0:
                thd = np.sqrt(harmonic_power / fundamental_power) * 100
            else:
                thd = 0.0
            
            return min(100.0, thd)
            
        except Exception as e:
            logger.warning(f"THD calculation failed: {e}")
            return 0.0
    
    async def _analyze_frequency_response(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze frequency response in different bands."""
        try:
            # Compute FFT
            fft_size = min(8192, len(audio_data))
            if len(audio_data) < fft_size:
                audio_data = np.pad(audio_data, (0, fft_size - len(audio_data)))
            
            spectrum = np.abs(fft(audio_data[:fft_size]))
            freqs = np.fft.fftfreq(fft_size, 1/sample_rate)
            
            # Define frequency bands
            bands = {
                'sub_bass': (20, 60),
                'bass': (60, 250),
                'low_mid': (250, 500),
                'mid': (500, 2000),
                'high_mid': (2000, 4000),
                'presence': (4000, 6000),
                'brilliance': (6000, 20000)
            }
            
            # Calculate energy in each band
            response = {}
            positive_freqs = freqs[:fft_size//2]
            positive_spectrum = spectrum[:fft_size//2]
            
            for band_name, (low_freq, high_freq) in bands.items():
                low_idx = np.argmin(np.abs(positive_freqs - low_freq))
                high_idx = np.argmin(np.abs(positive_freqs - high_freq))
                
                if high_idx > low_idx:
                    band_energy = np.mean(positive_spectrum[low_idx:high_idx] ** 2)
                    response[band_name] = float(20 * np.log10(band_energy + 1e-10))  # Convert to dB
                else:
                    response[band_name] = -60.0
            
            return response
            
        except Exception as e:
            logger.warning(f"Frequency response analysis failed: {e}")
            return {band: -60.0 for band in ['sub_bass', 'bass', 'low_mid', 'mid', 'high_mid', 'presence', 'brilliance']}


class AudioQualityTester:
    """Audio quality testing engine."""
    
    def __init__(self, test_suite: Optional[AudioTestSuite] = None):
        # Create default test suite if none provided
        if test_suite is None:
            self.test_suite = AudioTestSuite(
                name="default_audio_test_suite",
                input_directory="/tmp/audio_input",
                output_directory="/tmp/audio_output"
            )
        else:
            self.test_suite = test_suite
        self.analyzer = AudioAnalyzer()
        self.test_results: List[AudioQualityResult] = []
    
    async def run_quality_tests(self, file_path: str) -> AudioQualityResult:
        """Run comprehensive audio quality tests on a file."""
        start_time = time.time()
        
        result = AudioQualityResult(
            test_name="comprehensive_audio_quality",
            file_path=file_path,
            status="error",
            quality_score=0.0,
            metrics=None
        )
        
        try:
            # Analyze audio file
            metrics = await self.analyzer.analyze_audio_file(file_path)
            result.metrics = metrics
            
            # Run quality assessments
            issues = []
            recommendations = []
            quality_score = 100.0
            
            # Test sample rate
            if metrics.sample_rate < self.analyzer.quality_thresholds['min_sample_rate']:
                issues.append(f"Low sample rate: {metrics.sample_rate} Hz (minimum: {self.analyzer.quality_thresholds['min_sample_rate']} Hz)")
                recommendations.append("Use higher sample rate for better quality")
                quality_score -= 15
            
            # Test bit depth
            if metrics.bit_depth < self.analyzer.quality_thresholds['min_bit_depth']:
                issues.append(f"Low bit depth: {metrics.bit_depth} bits (minimum: {self.analyzer.quality_thresholds['min_bit_depth']} bits)")
                recommendations.append("Use higher bit depth to reduce quantization noise")
                quality_score -= 10
            
            # Test dynamic range
            if metrics.dynamic_range < self.analyzer.quality_thresholds['min_dynamic_range']:
                issues.append(f"Low dynamic range: {metrics.dynamic_range:.1f} dB (minimum: {self.analyzer.quality_thresholds['min_dynamic_range']} dB)")
                recommendations.append("Avoid over-compression to preserve dynamic range")
                quality_score -= 20
            
            # Test SNR
            if metrics.snr_db < self.analyzer.quality_thresholds['min_snr_db']:
                issues.append(f"Low signal-to-noise ratio: {metrics.snr_db:.1f} dB (minimum: {self.analyzer.quality_thresholds['min_snr_db']} dB)")
                recommendations.append("Use noise reduction techniques during recording")
                quality_score -= 15
            
            # Test THD
            if metrics.thd_percent > self.analyzer.quality_thresholds['max_thd_percent']:
                issues.append(f"High total harmonic distortion: {metrics.thd_percent:.2f}% (maximum: {self.analyzer.quality_thresholds['max_thd_percent']}%)")
                recommendations.append("Check audio equipment for distortion sources")
                quality_score -= 10
            
            # Test peak levels
            if metrics.peak_amplitude > self.analyzer.quality_thresholds['max_peak_amplitude']:
                issues.append(f"Potential clipping detected: peak amplitude {metrics.peak_amplitude:.3f} (maximum: {self.analyzer.quality_thresholds['max_peak_amplitude']})")
                recommendations.append("Reduce input levels to prevent clipping")
                quality_score -= 25
            
            # Test file size (basic validation)
            max_size_bytes = self.test_suite.max_file_size_mb * 1024 * 1024
            if metrics.file_size_bytes > max_size_bytes:
                issues.append(f"File size too large: {metrics.file_size_bytes / 1024 / 1024:.1f} MB (maximum: {self.test_suite.max_file_size_mb} MB)")
                recommendations.append("Consider using compression or lower quality settings")
                quality_score -= 5
            
            # Test duration
            if metrics.duration_seconds < self.test_suite.min_duration_seconds:
                issues.append(f"Duration too short: {metrics.duration_seconds:.1f}s (minimum: {self.test_suite.min_duration_seconds}s)")
                quality_score -= 5
            elif metrics.duration_seconds > self.test_suite.max_duration_seconds:
                issues.append(f"Duration too long: {metrics.duration_seconds:.1f}s (maximum: {self.test_suite.max_duration_seconds}s)")
                quality_score -= 5
            
            # Test frequency response balance
            freq_response = metrics.frequency_response
            if freq_response:
                # Check for extreme frequency imbalances
                mid_energy = freq_response.get('mid', -60)
                bass_energy = freq_response.get('bass', -60)
                treble_energy = freq_response.get('presence', -60)
                
                if abs(bass_energy - mid_energy) > 20:
                    issues.append(f"Significant bass imbalance: {bass_energy - mid_energy:.1f} dB difference from midrange")
                    recommendations.append("Check EQ settings and frequency balance")
                    quality_score -= 5
                
                if abs(treble_energy - mid_energy) > 15:
                    issues.append(f"Significant treble imbalance: {treble_energy - mid_energy:.1f} dB difference from midrange")
                    recommendations.append("Adjust high-frequency response")
                    quality_score -= 5
            
            # Determine overall status
            quality_score = max(0.0, quality_score)
            
            if quality_score >= 90:
                status = "passed"
            elif quality_score >= 70:
                status = "warning"
            else:
                status = "failed"
            
            result.status = status
            result.quality_score = quality_score
            result.issues_found = issues
            result.recommendations = recommendations
            
        except Exception as e:
            result.status = "error"
            result.issues_found = [f"Analysis error: {str(e)}"]
            logger.error(f"Audio quality test failed for {file_path}: {e}")
        
        result.processing_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def test_audio_conversion_quality(self, input_file: str, output_file: str, 
                                          conversion_params: Dict[str, Any]) -> AudioQualityResult:
        """Test quality after audio format conversion."""
        start_time = time.time()
        
        result = AudioQualityResult(
            test_name="audio_conversion_quality",
            file_path=output_file,
            status="error",
            quality_score=0.0,
            metrics=None
        )
        
        try:
            # Analyze original and converted files
            original_metrics = await self.analyzer.analyze_audio_file(input_file)
            converted_metrics = await self.analyzer.analyze_audio_file(output_file)
            
            result.metrics = converted_metrics
            
            # Compare quality metrics
            issues = []
            recommendations = []
            quality_score = 100.0
            
            # Sample rate comparison
            if converted_metrics.sample_rate < original_metrics.sample_rate:
                quality_loss = (original_metrics.sample_rate - converted_metrics.sample_rate) / original_metrics.sample_rate * 100
                issues.append(f"Sample rate reduced by {quality_loss:.1f}%")
                quality_score -= min(20, quality_loss)
            
            # Bit depth comparison
            if converted_metrics.bit_depth < original_metrics.bit_depth:
                issues.append(f"Bit depth reduced from {original_metrics.bit_depth} to {converted_metrics.bit_depth} bits")
                quality_score -= 10
            
            # Dynamic range comparison
            dr_loss = original_metrics.dynamic_range - converted_metrics.dynamic_range
            if dr_loss > 2.0:
                issues.append(f"Dynamic range reduced by {dr_loss:.1f} dB")
                quality_score -= min(15, dr_loss * 2)
            
            # SNR comparison
            snr_loss = original_metrics.snr_db - converted_metrics.snr_db
            if snr_loss > 3.0:
                issues.append(f"SNR reduced by {snr_loss:.1f} dB")
                quality_score -= min(10, snr_loss)
            
            # THD comparison
            thd_increase = converted_metrics.thd_percent - original_metrics.thd_percent
            if thd_increase > 0.1:
                issues.append(f"THD increased by {thd_increase:.2f}%")
                quality_score -= min(10, thd_increase * 10)
            
            # File size efficiency
            size_ratio = converted_metrics.file_size_bytes / original_metrics.file_size_bytes
            target_format = conversion_params.get('format', '').lower()
            
            if target_format in ['mp3', 'aac', 'ogg'] and size_ratio > 0.5:
                issues.append(f"Compression efficiency lower than expected: {size_ratio:.2f}")
                recommendations.append("Consider adjusting bitrate or quality settings")
            
            # Generate recommendations
            if issues:
                recommendations.extend([
                    "Review conversion parameters",
                    "Consider using higher quality settings",
                    "Verify source file quality before conversion"
                ])
            
            # Determine status
            quality_score = max(0.0, quality_score)
            
            if quality_score >= 85:
                status = "passed"
            elif quality_score >= 65:
                status = "warning"
            else:
                status = "failed"
            
            result.status = status
            result.quality_score = quality_score
            result.issues_found = issues
            result.recommendations = recommendations
            
        except Exception as e:
            result.status = "error"
            result.issues_found = [f"Conversion quality test error: {str(e)}"]
            logger.error(f"Audio conversion quality test failed: {e}")
        
        result.processing_time_ms = (time.time() - start_time) * 1000
        return result
    
    async def generate_audio_report(self, results: List[AudioQualityResult]) -> Dict[str, Any]:
        """Generate comprehensive audio quality report."""
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'total_files_tested': len(results),
                'passed': len([r for r in results if r.status == 'passed']),
                'warnings': len([r for r in results if r.status == 'warning']),
                'failed': len([r for r in results if r.status == 'failed']),
                'errors': len([r for r in results if r.status == 'error']),
                'average_quality_score': 0.0,
                'total_processing_time_ms': sum(r.processing_time_ms for r in results)
            },
            'test_results': [],
            'quality_statistics': {},
            'common_issues': {},
            'recommendations': []
        }
        
        # Calculate average quality score
        valid_results = [r for r in results if r.status != 'error']
        if valid_results:
            report['summary']['average_quality_score'] = sum(r.quality_score for r in valid_results) / len(valid_results)
        
        # Process each result
        for result in results:
            test_result = {
                'file_path': result.file_path,
                'test_name': result.test_name,
                'status': result.status,
                'quality_score': result.quality_score,
                'processing_time_ms': result.processing_time_ms,
                'issues_found': result.issues_found,
                'recommendations': result.recommendations
            }
            
            # Add metrics if available
            if result.metrics:
                test_result['metrics'] = {
                    'sample_rate': result.metrics.sample_rate,
                    'duration_seconds': result.metrics.duration_seconds,
                    'channels': result.metrics.channels,
                    'bit_depth': result.metrics.bit_depth,
                    'file_size_mb': result.metrics.file_size_bytes / 1024 / 1024,
                    'peak_amplitude': result.metrics.peak_amplitude,
                    'rms_level': result.metrics.rms_level,
                    'dynamic_range_db': result.metrics.dynamic_range,
                    'snr_db': result.metrics.snr_db,
                    'thd_percent': result.metrics.thd_percent,
                    'spectral_centroid': result.metrics.spectral_centroid,
                    'tempo_bpm': result.metrics.tempo
                }
            
            report['test_results'].append(test_result)
        
        # Calculate quality statistics
        if valid_results:
            metrics_list = [r.metrics for r in valid_results if r.metrics]
            if metrics_list:
                report['quality_statistics'] = {
                    'sample_rate': {
                        'avg': np.mean([m.sample_rate for m in metrics_list]),
                        'min': min(m.sample_rate for m in metrics_list),
                        'max': max(m.sample_rate for m in metrics_list)
                    },
                    'dynamic_range_db': {
                        'avg': np.mean([m.dynamic_range for m in metrics_list]),
                        'min': min(m.dynamic_range for m in metrics_list),
                        'max': max(m.dynamic_range for m in metrics_list)
                    },
                    'snr_db': {
                        'avg': np.mean([m.snr_db for m in metrics_list]),
                        'min': min(m.snr_db for m in metrics_list),
                        'max': max(m.snr_db for m in metrics_list)
                    },
                    'thd_percent': {
                        'avg': np.mean([m.thd_percent for m in metrics_list]),
                        'min': min(m.thd_percent for m in metrics_list),
                        'max': max(m.thd_percent for m in metrics_list)
                    }
                }
        
        # Analyze common issues
        all_issues = []
        for result in results:
            all_issues.extend(result.issues_found)
        
        issue_counts = {}
        for issue in all_issues:
            issue_type = issue.split(':')[0]  # Get issue type before colon
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        report['common_issues'] = dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Generate overall recommendations
        recommendations = []
        
        if report['summary']['failed'] > 0:
            recommendations.append(f"Address {report['summary']['failed']} failed audio quality tests")
        
        if 'Low sample rate' in issue_counts:
            recommendations.append("Consider using higher sample rates (48kHz or higher) for better quality")
        
        if 'Low dynamic range' in issue_counts:
            recommendations.append("Review audio processing chain to preserve dynamic range")
        
        if 'High total harmonic distortion' in issue_counts:
            recommendations.append("Check recording equipment and signal chain for distortion sources")
        
        if 'Potential clipping detected' in issue_counts:
            recommendations.append("Implement proper gain staging to prevent clipping")
        
        if not recommendations:
            recommendations.append("Audio quality meets all specified criteria")
        
        report['recommendations'] = recommendations
        
        return report


class AudioQualityOrchestrator:
    """
    Enterprise Audio Quality Testing Orchestration Engine
    ==================================================
    
    Comprehensive audio quality testing and analysis orchestration.
    Demonstrates Audio Engineer + ML Engineer + Backend Senior expertise.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.test_results: List[AudioQualityResult] = []
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load audio quality testing configuration."""
        default_config = {
            'test_suites': {},
            'global_settings': {
                'supported_formats': ['wav', 'mp3', 'flac', 'aac', 'm4a', 'ogg'],
                'max_parallel_tests': 4,
                'temp_directory': '/tmp/audio_quality_tests',
                'generate_visualizations': True
            },
            'quality_thresholds': {
                'min_sample_rate': 44100,
                'min_bit_depth': 16,
                'max_thd_percent': 1.0,
                'min_snr_db': 60.0,
                'min_dynamic_range': 20.0,
                'max_peak_amplitude': 0.95
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def run_audio_quality_tests(self, test_suite: AudioTestSuite) -> Dict[str, Any]:
        """Run audio quality tests for a test suite."""
        logger.info(f"Starting audio quality tests: {test_suite.name}")
        
        input_dir = Path(test_suite.input_directory)
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find audio files
        audio_files = []
        for format_ext in test_suite.supported_formats:
            audio_files.extend(input_dir.glob(f"*.{format_ext}"))
            audio_files.extend(input_dir.glob(f"*.{format_ext.upper()}"))
        
        logger.info(f"Found {len(audio_files)} audio files to test")
        
        # Create tester
        tester = AudioQualityTester(test_suite)
        
        # Run tests
        results = []
        semaphore = asyncio.Semaphore(self.config['global_settings']['max_parallel_tests'])
        
        async def test_file(file_path):
            async with semaphore:
                return await tester.run_quality_tests(str(file_path))
        
        # Execute tests in parallel
        tasks = [test_file(file_path) for file_path in audio_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, AudioQualityResult)]
        self.test_results.extend(valid_results)
        
        # Generate report
        report = await tester.generate_audio_report(valid_results)
        
        logger.info(f"Audio quality tests completed: {test_suite.name}")
        logger.info(f"  Total files: {len(valid_results)}")
        logger.info(f"  Passed: {report['summary']['passed']}")
        logger.info(f"  Warnings: {report['summary']['warnings']}")
        logger.info(f"  Failed: {report['summary']['failed']}")
        logger.info(f"  Average quality score: {report['summary']['average_quality_score']:.1f}")
        
        return report
    
    async def save_report(self, report: Dict[str, Any], output_path: str = "audio_quality_report.json"):
        """Save audio quality report to file."""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Audio quality report saved to: {output_path}")


# CLI Interface
async def main():
    """Main CLI interface for audio quality testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Audio Quality Testing Engine")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--input-dir", required=True, help="Input directory containing audio files")
    parser.add_argument("--output", default="audio_quality_report.json", help="Output report file")
    parser.add_argument("--formats", nargs='+', default=['wav', 'mp3', 'flac'], 
                       help="Audio formats to test")
    parser.add_argument("--max-size-mb", type=float, default=100.0, 
                       help="Maximum file size in MB")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize orchestrator
    orchestrator = AudioQualityOrchestrator(args.config)
    
    try:
        # Create test suite
        test_suite = AudioTestSuite(
            name="audio_quality_test",
            input_directory=args.input_dir,
            output_directory=str(Path(args.output).parent),
            supported_formats=args.formats,
            max_file_size_mb=args.max_size_mb
        )
        
        # Run tests
        report = await orchestrator.run_audio_quality_tests(test_suite)
        
        # Save report
        await orchestrator.save_report(report, args.output)
        
        # Print summary
        summary = report['summary']
        print(f"\n🎵 Audio Quality Test Results")
        print(f"{'='*50}")
        print(f"Files Tested: {summary['total_files_tested']}")
        print(f"Passed: {summary['passed']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Failed: {summary['failed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Average Quality Score: {summary['average_quality_score']:.1f}/100")
        
        if report['common_issues']:
            print(f"\n🚨 Common Issues:")
            for issue, count in list(report['common_issues'].items())[:3]:
                print(f"  - {issue}: {count} files")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations'][:3]:
                print(f"  - {rec}")
    
    except Exception as e:
        logger.error(f"Audio quality testing failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())