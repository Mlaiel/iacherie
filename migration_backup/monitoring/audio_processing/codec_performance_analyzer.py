"""
Ainflue Platform - Codec Performance Analyzer
=============================================

Advanced performance analysis for audio codecs including encoding/decoding
efficiency, quality metrics, compression ratios, and optimization
recommendations for different audio processing scenarios.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class CodecType(Enum):
    """Supported audio codec types."""
    MP3_LAME = "mp3_lame"
    MP3_CBR = "mp3_cbr"
    MP3_VBR = "mp3_vbr"
    AAC_LC = "aac_lc"
    AAC_HE = "aac_he"
    AAC_HEv2 = "aac_hev2"
    FLAC = "flac"
    OPUS = "opus"
    VORBIS = "vorbis"
    WAV_PCM = "wav_pcm"
    ALAC = "alac"
    WMA = "wma"
    AC3 = "ac3"
    DTS = "dts"

class QualityProfile(Enum):
    """Audio quality profiles for encoding."""
    PHONE_QUALITY = "phone_quality"          # 8kHz, mono, low bitrate
    FM_RADIO = "fm_radio"                    # 44.1kHz, stereo, medium bitrate
    CD_QUALITY = "cd_quality"                # 44.1kHz, 16-bit, stereo
    STUDIO_QUALITY = "studio_quality"        # 48kHz+, 24-bit, stereo/multichannel
    ARCHIVE_QUALITY = "archive_quality"      # Lossless, highest quality
    STREAMING_LOW = "streaming_low"          # Optimized for low bandwidth
    STREAMING_HIGH = "streaming_high"        # Optimized for high bandwidth

class PerformanceMetric(Enum):
    """Performance metrics for codec analysis."""
    ENCODING_SPEED = "encoding_speed"
    DECODING_SPEED = "decoding_speed"
    COMPRESSION_RATIO = "compression_ratio"
    QUALITY_SCORE = "quality_score"
    CPU_EFFICIENCY = "cpu_efficiency"
    MEMORY_USAGE = "memory_usage"
    COMPATIBILITY = "compatibility"
    LATENCY = "latency"

@dataclass
class CodecPerformanceTest:
    """Individual codec performance test result."""
    test_id: str
    codec_type: CodecType
    quality_profile: QualityProfile
    input_file_size_mb: float
    output_file_size_mb: float
    encoding_time_ms: float
    decoding_time_ms: float
    cpu_usage_percent: float
    memory_peak_mb: float
    quality_score: float
    compression_ratio: float
    bitrate_kbps: int
    sample_rate_hz: int
    bit_depth: int
    channels: int
    audio_duration_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CodecBenchmark:
    """Comprehensive codec benchmark results."""
    benchmark_id: str
    codec_type: CodecType
    test_results: List[CodecPerformanceTest]
    average_encoding_speed_realtime: float
    average_decoding_speed_realtime: float
    average_compression_ratio: float
    average_quality_score: float
    cpu_efficiency_score: float
    memory_efficiency_score: float
    overall_performance_score: float
    recommended_use_cases: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class CodecPerformanceAnalyzer:
    """
    Enterprise codec performance analysis system.
    
    Features:
    - Comprehensive codec benchmarking
    - Quality vs compression analysis
    - Encoding/decoding speed optimization
    - Resource utilization monitoring
    - Use case recommendation engine
    - Performance trend analysis
    - Optimization strategy suggestions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.performance_tests: deque = deque(maxlen=10000)
        self.benchmarks: List[CodecBenchmark] = []
        self.codec_profiles = self._initialize_codec_profiles()
        self.quality_baselines = self._initialize_quality_baselines()
        
        logger.info("Codec Performance Analyzer initialized")
    
    def _initialize_codec_profiles(self) -> Dict[CodecType, Dict[str, Any]]:
        """Initialize codec-specific performance profiles."""
        return {
            CodecType.MP3_LAME: {
                'typical_compression_ratio': 10.0,
                'quality_range': (0.7, 0.95),
                'encoding_complexity': 'medium',
                'decoding_complexity': 'low',
                'streaming_friendly': True,
                'lossless': False
            },
            CodecType.AAC_LC: {
                'typical_compression_ratio': 12.0,
                'quality_range': (0.75, 0.96),
                'encoding_complexity': 'medium',
                'decoding_complexity': 'low',
                'streaming_friendly': True,
                'lossless': False
            },
            CodecType.FLAC: {
                'typical_compression_ratio': 2.0,
                'quality_range': (1.0, 1.0),
                'encoding_complexity': 'high',
                'decoding_complexity': 'medium',
                'streaming_friendly': False,
                'lossless': True
            },
            CodecType.OPUS: {
                'typical_compression_ratio': 15.0,
                'quality_range': (0.80, 0.98),
                'encoding_complexity': 'high',
                'decoding_complexity': 'medium',
                'streaming_friendly': True,
                'lossless': False
            },
            CodecType.VORBIS: {
                'typical_compression_ratio': 11.0,
                'quality_range': (0.75, 0.95),
                'encoding_complexity': 'high',
                'decoding_complexity': 'medium',
                'streaming_friendly': True,
                'lossless': False
            }
        }
    
    def _initialize_quality_baselines(self) -> Dict[QualityProfile, Dict[str, Any]]:
        """Initialize quality baselines for different profiles."""
        return {
            QualityProfile.PHONE_QUALITY: {
                'target_quality_score': 0.6,
                'max_bitrate_kbps': 32,
                'target_compression_ratio': 20.0
            },
            QualityProfile.FM_RADIO: {
                'target_quality_score': 0.8,
                'max_bitrate_kbps': 128,
                'target_compression_ratio': 12.0
            },
            QualityProfile.CD_QUALITY: {
                'target_quality_score': 0.9,
                'max_bitrate_kbps': 320,
                'target_compression_ratio': 5.0
            },
            QualityProfile.STUDIO_QUALITY: {
                'target_quality_score': 0.95,
                'max_bitrate_kbps': 1000,
                'target_compression_ratio': 3.0
            },
            QualityProfile.ARCHIVE_QUALITY: {
                'target_quality_score': 1.0,
                'max_bitrate_kbps': 9999,  # Lossless
                'target_compression_ratio': 2.0
            }
        }
    
    async def run_codec_performance_test(self, codec_type: CodecType,
                                       quality_profile: QualityProfile,
                                       audio_file_path: str,
                                       audio_duration_seconds: float,
                                       input_file_size_mb: float) -> str:
        """Run a comprehensive performance test for a specific codec."""
        test_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Simulate codec performance testing
            test_result = await self._simulate_codec_test(
                test_id, codec_type, quality_profile, 
                audio_duration_seconds, input_file_size_mb
            )
            
            self.performance_tests.append(test_result)
            
            # Analyze performance metrics
            await self._analyze_test_performance(test_result)
            
            logger.info(f"Codec test completed: {test_id} "
                       f"({codec_type.value}, {quality_profile.value})")
            
        except Exception as e:
            logger.error(f"Codec test failed: {test_id} - {e}")
            raise
        
        return test_id
    
    async def _simulate_codec_test(self, test_id: str, codec_type: CodecType,
                                 quality_profile: QualityProfile,
                                 audio_duration_seconds: float,
                                 input_file_size_mb: float) -> CodecPerformanceTest:
        """Simulate codec performance testing (in production, would use actual codecs)."""
        # Simulate encoding/decoding time based on codec complexity
        codec_profile = self.codec_profiles.get(codec_type, {})
        quality_baseline = self.quality_baselines.get(quality_profile, {})
        
        # Simulate encoding performance
        encoding_complexity_factor = {
            'low': 0.5, 'medium': 1.0, 'high': 2.0
        }.get(codec_profile.get('encoding_complexity', 'medium'), 1.0)
        
        base_encoding_time = audio_duration_seconds * 1000 * encoding_complexity_factor
        encoding_time_ms = base_encoding_time * (0.8 + 0.4 * hash(test_id) % 1000 / 1000)
        
        # Simulate decoding performance
        decoding_complexity_factor = {
            'low': 0.1, 'medium': 0.3, 'high': 0.5
        }.get(codec_profile.get('decoding_complexity', 'medium'), 0.3)
        
        decoding_time_ms = audio_duration_seconds * 1000 * decoding_complexity_factor
        
        # Simulate compression and quality
        target_compression = quality_baseline.get('target_compression_ratio', 10.0)
        compression_ratio = target_compression * (0.8 + 0.4 * hash(test_id + 'comp') % 1000 / 1000)
        output_file_size_mb = input_file_size_mb / compression_ratio
        
        # Simulate quality score
        target_quality = quality_baseline.get('target_quality_score', 0.85)
        quality_score = min(1.0, target_quality + (hash(test_id + 'qual') % 100 - 50) / 1000)
        
        # Simulate resource usage
        cpu_usage = 30 + encoding_complexity_factor * 40 + (hash(test_id + 'cpu') % 20)
        memory_peak_mb = 50 + input_file_size_mb * 2 + encoding_complexity_factor * 100
        
        # Calculate bitrate
        bitrate_kbps = int((output_file_size_mb * 8 * 1024) / audio_duration_seconds)
        
        # Simulate audio properties
        sample_rate_hz = {
            QualityProfile.PHONE_QUALITY: 8000,
            QualityProfile.FM_RADIO: 44100,
            QualityProfile.CD_QUALITY: 44100,
            QualityProfile.STUDIO_QUALITY: 48000,
            QualityProfile.ARCHIVE_QUALITY: 96000
        }.get(quality_profile, 44100)
        
        bit_depth = {
            QualityProfile.PHONE_QUALITY: 8,
            QualityProfile.FM_RADIO: 16,
            QualityProfile.CD_QUALITY: 16,
            QualityProfile.STUDIO_QUALITY: 24,
            QualityProfile.ARCHIVE_QUALITY: 24
        }.get(quality_profile, 16)
        
        # Add some processing delay to simulate real work
        await asyncio.sleep(0.01)
        
        return CodecPerformanceTest(
            test_id=test_id,
            codec_type=codec_type,
            quality_profile=quality_profile,
            input_file_size_mb=input_file_size_mb,
            output_file_size_mb=output_file_size_mb,
            encoding_time_ms=encoding_time_ms,
            decoding_time_ms=decoding_time_ms,
            cpu_usage_percent=cpu_usage,
            memory_peak_mb=memory_peak_mb,
            quality_score=quality_score,
            compression_ratio=compression_ratio,
            bitrate_kbps=bitrate_kbps,
            sample_rate_hz=sample_rate_hz,
            bit_depth=bit_depth,
            channels=2,  # Assume stereo
            audio_duration_seconds=audio_duration_seconds,
            metadata={
                'encoder_settings': f'{codec_type.value}_optimized',
                'test_environment': 'production_simulation'
            }
        )
    
    async def _analyze_test_performance(self, test_result: CodecPerformanceTest):
        """Analyze individual test performance and flag issues."""
        # Check encoding speed (should be faster than real-time for most use cases)
        realtime_factor = test_result.encoding_time_ms / (test_result.audio_duration_seconds * 1000)
        
        if realtime_factor > 1.0:
            logger.warning(f"Slow encoding detected: {realtime_factor:.2f}x realtime "
                          f"for {test_result.codec_type.value}")
        
        # Check quality vs compression trade-off
        expected_quality = self.quality_baselines.get(
            test_result.quality_profile, {}
        ).get('target_quality_score', 0.85)
        
        if test_result.quality_score < expected_quality * 0.9:
            logger.warning(f"Low quality detected: {test_result.quality_score:.3f} "
                          f"(expected: {expected_quality:.3f}) for {test_result.codec_type.value}")
        
        # Check resource usage
        if test_result.cpu_usage_percent > 90:
            logger.warning(f"High CPU usage: {test_result.cpu_usage_percent:.1f}% "
                          f"for {test_result.codec_type.value}")
        
        if test_result.memory_peak_mb > 1000:
            logger.warning(f"High memory usage: {test_result.memory_peak_mb:.1f}MB "
                          f"for {test_result.codec_type.value}")
    
    async def run_codec_benchmark(self, codec_type: CodecType, 
                                test_cases: List[Dict[str, Any]]) -> str:
        """Run comprehensive benchmark for a codec across multiple test cases."""
        benchmark_id = str(uuid.uuid4())
        test_results = []
        
        for test_case in test_cases:
            test_id = await self.run_codec_performance_test(
                codec_type=codec_type,
                quality_profile=test_case['quality_profile'],
                audio_file_path=test_case.get('audio_file_path', 'test.wav'),
                audio_duration_seconds=test_case['audio_duration_seconds'],
                input_file_size_mb=test_case['input_file_size_mb']
            )
            
            # Find the test result
            test_result = next(
                (t for t in self.performance_tests if t.test_id == test_id), None
            )
            if test_result:
                test_results.append(test_result)
        
        # Calculate benchmark metrics
        benchmark = await self._calculate_benchmark_metrics(
            benchmark_id, codec_type, test_results
        )
        
        self.benchmarks.append(benchmark)
        
        logger.info(f"Codec benchmark completed: {benchmark_id} "
                   f"({codec_type.value}, {len(test_results)} tests)")
        
        return benchmark_id
    
    async def _calculate_benchmark_metrics(self, benchmark_id: str, 
                                         codec_type: CodecType,
                                         test_results: List[CodecPerformanceTest]) -> CodecBenchmark:
        """Calculate comprehensive benchmark metrics."""
        if not test_results:
            raise ValueError("No test results available for benchmark calculation")
        
        # Calculate average performance metrics
        encoding_speeds = []
        decoding_speeds = []
        compression_ratios = []
        quality_scores = []
        cpu_usages = []
        memory_usages = []
        
        for test in test_results:
            # Calculate real-time factors
            encoding_realtime_factor = (test.audio_duration_seconds * 1000) / test.encoding_time_ms
            decoding_realtime_factor = (test.audio_duration_seconds * 1000) / test.decoding_time_ms
            
            encoding_speeds.append(encoding_realtime_factor)
            decoding_speeds.append(decoding_realtime_factor)
            compression_ratios.append(test.compression_ratio)
            quality_scores.append(test.quality_score)
            cpu_usages.append(test.cpu_usage_percent)
            memory_usages.append(test.memory_peak_mb)
        
        # Calculate efficiency scores
        cpu_efficiency_score = max(0, min(1, (100 - statistics.mean(cpu_usages)) / 100))
        memory_efficiency_score = max(0, min(1, (1000 - statistics.mean(memory_usages)) / 1000))
        
        # Calculate overall performance score
        speed_score = min(1, statistics.mean(encoding_speeds) / 2)  # 2x realtime = perfect
        quality_score = statistics.mean(quality_scores)
        compression_score = min(1, statistics.mean(compression_ratios) / 20)  # 20:1 = perfect
        
        overall_performance_score = (
            speed_score * 0.3 + 
            quality_score * 0.4 + 
            compression_score * 0.2 + 
            cpu_efficiency_score * 0.1
        )
        
        # Generate use case recommendations
        recommended_use_cases = self._generate_use_case_recommendations(
            codec_type, statistics.mean(encoding_speeds), statistics.mean(quality_scores),
            statistics.mean(compression_ratios), cpu_efficiency_score
        )
        
        return CodecBenchmark(
            benchmark_id=benchmark_id,
            codec_type=codec_type,
            test_results=test_results,
            average_encoding_speed_realtime=statistics.mean(encoding_speeds),
            average_decoding_speed_realtime=statistics.mean(decoding_speeds),
            average_compression_ratio=statistics.mean(compression_ratios),
            average_quality_score=statistics.mean(quality_scores),
            cpu_efficiency_score=cpu_efficiency_score,
            memory_efficiency_score=memory_efficiency_score,
            overall_performance_score=overall_performance_score,
            recommended_use_cases=recommended_use_cases
        )
    
    def _generate_use_case_recommendations(self, codec_type: CodecType,
                                         encoding_speed: float, quality_score: float,
                                         compression_ratio: float, 
                                         cpu_efficiency: float) -> List[str]:
        """Generate use case recommendations based on codec performance."""
        recommendations = []
        
        # Speed-based recommendations
        if encoding_speed >= 10:
            recommendations.append("Real-time streaming applications")
            recommendations.append("Live broadcasting")
        elif encoding_speed >= 2:
            recommendations.append("Interactive applications")
            recommendations.append("Podcast processing")
        
        # Quality-based recommendations
        if quality_score >= 0.95:
            recommendations.append("Professional audio production")
            recommendations.append("Archival storage")
        elif quality_score >= 0.85:
            recommendations.append("High-quality streaming")
            recommendations.append("Music distribution")
        elif quality_score >= 0.7:
            recommendations.append("Voice communications")
            recommendations.append("Audiobooks")
        
        # Compression-based recommendations
        if compression_ratio >= 15:
            recommendations.append("Bandwidth-limited scenarios")
            recommendations.append("Mobile applications")
        elif compression_ratio >= 10:
            recommendations.append("Web streaming")
            recommendations.append("General audio distribution")
        
        # Efficiency-based recommendations
        if cpu_efficiency >= 0.8:
            recommendations.append("High-volume processing")
            recommendations.append("Battery-powered devices")
        
        # Codec-specific recommendations
        if codec_type == CodecType.FLAC:
            recommendations.append("Lossless archival")
            recommendations.append("Audio mastering")
        elif codec_type == CodecType.OPUS:
            recommendations.append("VoIP applications")
            recommendations.append("Gaming audio")
        elif codec_type in [CodecType.MP3_LAME, CodecType.AAC_LC]:
            recommendations.append("Universal compatibility")
            recommendations.append("Consumer audio devices")
        
        return list(set(recommendations))  # Remove duplicates
    
    def get_codec_comparison(self, codec_types: List[CodecType],
                           quality_profile: QualityProfile) -> Dict[str, Any]:
        """Compare multiple codecs for a specific quality profile."""
        comparison_data = {}
        
        for codec_type in codec_types:
            # Find recent test results for this codec and quality profile
            relevant_tests = [
                test for test in self.performance_tests
                if (test.codec_type == codec_type and 
                    test.quality_profile == quality_profile)
            ]
            
            if relevant_tests:
                # Use most recent test or average if multiple
                if len(relevant_tests) == 1:
                    test = relevant_tests[0]
                else:
                    # Calculate averages
                    test = self._average_test_results(relevant_tests)
                
                comparison_data[codec_type.value] = {
                    'encoding_speed_realtime': (test.audio_duration_seconds * 1000) / test.encoding_time_ms,
                    'decoding_speed_realtime': (test.audio_duration_seconds * 1000) / test.decoding_time_ms,
                    'quality_score': test.quality_score,
                    'compression_ratio': test.compression_ratio,
                    'bitrate_kbps': test.bitrate_kbps,
                    'cpu_usage_percent': test.cpu_usage_percent,
                    'memory_peak_mb': test.memory_peak_mb,
                    'file_size_reduction_percent': (1 - 1/test.compression_ratio) * 100
                }
        
        # Find best performer in each category
        if comparison_data:
            best_performers = {
                'fastest_encoding': max(comparison_data.items(), 
                                      key=lambda x: x[1]['encoding_speed_realtime']),
                'fastest_decoding': max(comparison_data.items(), 
                                      key=lambda x: x[1]['decoding_speed_realtime']),
                'highest_quality': max(comparison_data.items(), 
                                     key=lambda x: x[1]['quality_score']),
                'best_compression': max(comparison_data.items(), 
                                      key=lambda x: x[1]['compression_ratio']),
                'most_cpu_efficient': min(comparison_data.items(), 
                                        key=lambda x: x[1]['cpu_usage_percent']),
                'most_memory_efficient': min(comparison_data.items(), 
                                           key=lambda x: x[1]['memory_peak_mb'])
            }
        else:
            best_performers = {}
        
        return {
            'quality_profile': quality_profile.value,
            'codec_comparison': comparison_data,
            'best_performers': {k: v[0] for k, v in best_performers.items()},
            'comparison_timestamp': datetime.utcnow().isoformat()
        }
    
    def _average_test_results(self, test_results: List[CodecPerformanceTest]) -> CodecPerformanceTest:
        """Calculate average of multiple test results."""
        if not test_results:
            raise ValueError("No test results to average")
        
        # Use first test as template and average numerical values
        template = test_results[0]
        
        avg_test = CodecPerformanceTest(
            test_id=f"avg_{template.codec_type.value}",
            codec_type=template.codec_type,
            quality_profile=template.quality_profile,
            input_file_size_mb=statistics.mean([t.input_file_size_mb for t in test_results]),
            output_file_size_mb=statistics.mean([t.output_file_size_mb for t in test_results]),
            encoding_time_ms=statistics.mean([t.encoding_time_ms for t in test_results]),
            decoding_time_ms=statistics.mean([t.decoding_time_ms for t in test_results]),
            cpu_usage_percent=statistics.mean([t.cpu_usage_percent for t in test_results]),
            memory_peak_mb=statistics.mean([t.memory_peak_mb for t in test_results]),
            quality_score=statistics.mean([t.quality_score for t in test_results]),
            compression_ratio=statistics.mean([t.compression_ratio for t in test_results]),
            bitrate_kbps=int(statistics.mean([t.bitrate_kbps for t in test_results])),
            sample_rate_hz=template.sample_rate_hz,
            bit_depth=template.bit_depth,
            channels=template.channels,
            audio_duration_seconds=statistics.mean([t.audio_duration_seconds for t in test_results])
        )
        
        return avg_test
    
    def get_performance_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive codec performance statistics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_tests = [
            test for test in self.performance_tests
            if test.timestamp >= cutoff_time
        ]
        
        if not recent_tests:
            return {"message": f"No codec tests in last {hours} hours"}
        
        # Group by codec type
        codec_stats = {}
        for codec_type in CodecType:
            codec_tests = [t for t in recent_tests if t.codec_type == codec_type]
            if codec_tests:
                avg_encoding_speed = statistics.mean([
                    (t.audio_duration_seconds * 1000) / t.encoding_time_ms for t in codec_tests
                ])
                avg_quality = statistics.mean([t.quality_score for t in codec_tests])
                avg_compression = statistics.mean([t.compression_ratio for t in codec_tests])
                
                codec_stats[codec_type.value] = {
                    'test_count': len(codec_tests),
                    'avg_encoding_speed_realtime': avg_encoding_speed,
                    'avg_quality_score': avg_quality,
                    'avg_compression_ratio': avg_compression,
                    'avg_cpu_usage': statistics.mean([t.cpu_usage_percent for t in codec_tests]),
                    'avg_memory_usage_mb': statistics.mean([t.memory_peak_mb for t in codec_tests])
                }
        
        return {
            'period_hours': hours,
            'total_tests': len(recent_tests),
            'codec_statistics': codec_stats,
            'overall_averages': {
                'encoding_speed_realtime': statistics.mean([
                    (t.audio_duration_seconds * 1000) / t.encoding_time_ms for t in recent_tests
                ]),
                'quality_score': statistics.mean([t.quality_score for t in recent_tests]),
                'compression_ratio': statistics.mean([t.compression_ratio for t in recent_tests]),
                'cpu_usage_percent': statistics.mean([t.cpu_usage_percent for t in recent_tests])
            }
        }

# Global codec performance analyzer instance
codec_performance_analyzer = CodecPerformanceAnalyzer()

# Export main components
__all__ = [
    'CodecPerformanceAnalyzer',
    'CodecPerformanceTest',
    'CodecBenchmark',
    'CodecType',
    'QualityProfile',
    'PerformanceMetric',
    'codec_performance_analyzer'
]