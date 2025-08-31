"""Audio Enhancement Module - Main Index & Entry Point
==================================================

Professional audio enhancement system main entry point providing unified access
to all enhancement capabilities, simplified interfaces, and factory methods
for creating enhancement processors, analyzers, and pipelines.

This index module serves as the primary interface for the audio enhancement
system, offering both simple quick-start methods and advanced configuration
options for professional audio processing workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will be prosecuted to the full extent of the law.
"""
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import numpy as np

# Import all core components
from .processor import (
    AudioEnhancementProcessor,
    EnhancementParameters,
    EnhancementResult,
    ContentType,
    EnhancementType
)
from .realtime import (
    RealTimeEnhancer,
    RealTimeConfig,
    ProcessingMode,
    LatencyMetrics
)
from .quality_analyzer import (
    AudioQualityAnalyzer,
    QualityMetrics,
    QualityLevel,
    ComparisonResult
)
from .config_manager import (
    EnhancementConfigManager,
    EnhancementPreset,
    PresetCategory
)
from .pipeline import (
    AudioEnhancementPipeline,
    PipelineConfig,
    PipelineMode,
    ProcessingTask,
    PipelineResult
)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Professional Audio Enhancement System"


class AudioEnhancementSystem:
    """    Audio Enhancement System - Main Entry Point
    
    Unified interface for professional audio enhancement providing
    simplified access to all enhancement capabilities while maintaining
    full control over advanced features.
    """    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """        Initialize the audio enhancement system
        
        Args:
            config_dir: Optional configuration directory path
        """        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.processor = AudioEnhancementProcessor()
        self.quality_analyzer = AudioQualityAnalyzer()
        self.config_manager = EnhancementConfigManager(config_dir)
        self.pipeline = AudioEnhancementPipeline(config_dir=config_dir)
        
        # Real-time processor (created on demand)
        self.realtime_processor: Optional[RealTimeEnhancer] = None
        
        # System statistics
        self.processing_stats = {
            'total_enhancements': 0,
            'total_processing_time': 0.0,
            'average_quality_improvement': 0.0
        }
        
        self.logger.info("Audio Enhancement System initialized")
    
    def enhance_audio_simple(self,
                            audio: np.ndarray,
                            sample_rate: int,
                            content_type: str = "general",
                            quality: str = "balanced") -> Dict[str, Any]:
        """        Simple audio enhancement with minimal configuration
        
        Args:
            audio: Input audio signal
            sample_rate: Sample rate in Hz
            content_type: Content type ("music", "speech", "podcast", "general")
            quality: Quality mode ("fast", "balanced", "high_quality")
            
        Returns:
            Dictionary with enhanced audio and basic metrics
        """        try:
            # Map string parameters to enums
            content_enum = self._map_content_type(content_type)
            
            # Get appropriate preset
            preset = self._get_preset_for_quality(quality, content_enum)
            
            # Enhance audio
            result = self.processor.enhance_audio(
                audio, sample_rate, preset.parameters, content_enum
            )
            
            # Update statistics
            self._update_stats(result)
            
            return {
                'enhanced_audio': result.enhanced_audio,
                'sample_rate': sample_rate,
                'enhancement_gain_db': result.enhancement_gain_db,
                'processing_time': result.processing_time,
                'applied_enhancements': result.applied_enhancements,
                'warnings': result.warnings,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Simple enhancement failed: {str(e)}")
            return {
                'enhanced_audio': audio,  # Return original on error
                'sample_rate': sample_rate,
                'success': False,
                'error': str(e)
            }
    
    def enhance_audio_advanced(self,
                              audio: np.ndarray,
                              sample_rate: int,
                              preset_name: Optional[str] = None,
                              custom_parameters: Optional[EnhancementParameters] = None,
                              enable_quality_analysis: bool = True,
                              multi_pass: bool = False) -> Dict[str, Any]:
        """        Advanced audio enhancement with full control and analysis
        
        Args:
            audio: Input audio signal
            sample_rate: Sample rate in Hz
            preset_name: Name of enhancement preset to use
            custom_parameters: Custom enhancement parameters
            enable_quality_analysis: Enable comprehensive quality analysis
            multi_pass: Enable multi-pass processing for best quality
            
        Returns:
            Dictionary with comprehensive enhancement results
        """        try:
            # Configure pipeline
            pipeline_config = PipelineConfig(
                mode=PipelineMode.MULTI_PASS if multi_pass else PipelineMode.SINGLE_PASS,
                enable_quality_validation=enable_quality_analysis,
                max_passes=3 if multi_pass else 1
            )
            
            # Create temporary pipeline for this request
            temp_pipeline = AudioEnhancementPipeline(pipeline_config)
            
            # Process audio
            result = temp_pipeline.process_audio(
                audio=audio,
                sample_rate=sample_rate,
                preset_name=preset_name,
                custom_parameters=custom_parameters
            )
            
            # Update statistics
            if result.enhancement_result:
                self._update_stats(result.enhancement_result)
            
            # Format comprehensive response
            response = {
                'success': result.success,
                'processing_time': result.processing_time,
                'passes_completed': result.passes_completed
            }
            
            if result.enhancement_result:
                response.update({
                    'enhanced_audio': result.enhancement_result.enhanced_audio,
                    'sample_rate': sample_rate,
                    'enhancement_gain_db': result.enhancement_result.enhancement_gain_db,
                    'applied_enhancements': result.enhancement_result.applied_enhancements,
                    'warnings': result.enhancement_result.warnings + result.warnings
                })
            
            if result.quality_metrics:
                response['quality_metrics'] = {
                    'overall_score': result.quality_metrics.overall_quality_score,
                    'quality_level': result.quality_metrics.quality_level.value,
                    'snr_db': result.quality_metrics.snr_db,
                    'dynamic_range_db': result.quality_metrics.dynamic_range_db,
                    'thd_percent': result.quality_metrics.thd_percent
                }
            
            if result.comparison_result:
                response['improvement_analysis'] = {
                    'overall_improvement': result.comparison_result.overall_improvement,
                    'recommendation': result.comparison_result.recommendation,
                    'improvements': result.comparison_result.improvement_scores,
                    'degradations': result.comparison_result.degradation_scores
                }
            
            if not result.success:
                response['error'] = result.error_message
            
            return response
            
        except Exception as e:
            self.logger.error(f"Advanced enhancement failed: {str(e)}")
            return {
                'enhanced_audio': audio,
                'sample_rate': sample_rate,
                'success': False,
                'error': str(e)
            }
    
    def analyze_audio_quality(self,
                             audio: np.ndarray,
                             sample_rate: int,
                             detailed: bool = True) -> Dict[str, Any]:
        """        Analyze audio quality with comprehensive metrics
        
        Args:
            audio: Input audio signal
            sample_rate: Sample rate in Hz
            detailed: Enable detailed psychoacoustic analysis
            
        Returns:
            Dictionary with quality metrics and analysis
        """        try:
            metrics = self.quality_analyzer.analyze_quality(
                audio, sample_rate, detailed=detailed
            )
            
            return {
                'success': True,
                'overall_score': metrics.overall_quality_score,
                'quality_level': metrics.quality_level.value,
                'basic_metrics': {
                    'peak_amplitude': metrics.peak_amplitude,
                    'rms_db': metrics.rms_db,
                    'dynamic_range_db': metrics.dynamic_range_db,
                    'snr_db': metrics.snr_db,
                    'thd_percent': metrics.thd_percent
                },
                'spectral_metrics': {
                    'spectral_centroid': metrics.spectral_centroid,
                    'spectral_bandwidth': metrics.spectral_bandwidth,
                    'spectral_flatness': metrics.spectral_flatness
                },
                'temporal_metrics': {
                    'zero_crossing_rate': metrics.zero_crossing_rate,
                    'onset_density': metrics.onset_density
                },
                'warnings': self._generate_quality_warnings(metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def compare_audio_quality(self,
                             original_audio: np.ndarray,
                             enhanced_audio: np.ndarray,
                             sample_rate: int) -> Dict[str, Any]:
        """        Compare quality between original and enhanced audio
        
        Args:
            original_audio: Original audio signal
            enhanced_audio: Enhanced audio signal
            sample_rate: Sample rate in Hz
            
        Returns:
            Dictionary with comparison results
        """        try:
            comparison = self.quality_analyzer.compare_quality(
                original_audio, enhanced_audio, sample_rate
            )
            
            return {
                'success': True,
                'overall_improvement': comparison.overall_improvement,
                'recommendation': comparison.recommendation,
                'original_quality': {
                    'score': comparison.reference_metrics.overall_quality_score,
                    'level': comparison.reference_metrics.quality_level.value
                },
                'enhanced_quality': {
                    'score': comparison.test_metrics.overall_quality_score,
                    'level': comparison.test_metrics.quality_level.value
                },
                'improvements': comparison.improvement_scores,
                'degradations': comparison.degradation_scores,
                'warnings': comparison.warnings
            }
            
        except Exception as e:
            self.logger.error(f"Quality comparison failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_realtime_enhancement(self,
                                  buffer_size: int = 512,
                                  sample_rate: int = 44100,
                                  channels: int = 2,
                                  mode: str = "balanced") -> bool:
        """        Start real-time audio enhancement
        
        Args:
            buffer_size: Audio buffer size in samples
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            mode: Processing mode ("low_latency", "balanced", "high_quality")
            
        Returns:
            True if real-time processing started successfully
        """        try:
            processing_mode = self._map_processing_mode(mode)
            
            config = RealTimeConfig(
                buffer_size=buffer_size,
                sample_rate=sample_rate,
                channels=channels,
                processing_mode=processing_mode
            )
            
            self.realtime_processor = RealTimeEnhancer(config)
            success = self.realtime_processor.start_processing()
            
            if success:
                self.logger.info(f"Real-time enhancement started: {mode} mode")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to start real-time enhancement: {str(e)}")
            return False
    
    def stop_realtime_enhancement(self):
        """Stop real-time audio enhancement"""        if self.realtime_processor:
            self.realtime_processor.stop_processing()
            self.realtime_processor = None
            self.logger.info("Real-time enhancement stopped")
    
    def process_realtime_chunk(self, audio_chunk: np.ndarray) -> bool:
        """        Process audio chunk in real-time
        
        Args:
            audio_chunk: Audio data chunk to process
            
        Returns:
            True if chunk was processed successfully
        """        if not self.realtime_processor:
            return False
        
        return self.realtime_processor.process_audio_chunk(audio_chunk)
    
    def get_realtime_output(self, num_samples: int) -> Optional[np.ndarray]:
        """        Get processed real-time audio output
        
        Args:
            num_samples: Number of samples to retrieve
            
        Returns:
            Processed audio data or None if not available
        """        if not self.realtime_processor:
            return None
        
        return self.realtime_processor.get_processed_audio(num_samples)
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time processing performance metrics"""        if not self.realtime_processor:
            return {'status': 'not_running'}
        
        metrics = self.realtime_processor.get_latency_metrics()
        performance = self.realtime_processor.get_performance_summary()
        
        return {
            'status': 'running',
            'latency_ms': metrics.total_latency_ms,
            'cpu_usage_percent': metrics.cpu_usage_percent,
            'buffer_underruns': metrics.buffer_underruns,
            'buffer_overruns': metrics.buffer_overruns,
            'performance_summary': performance
        }
    
    def list_presets(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """        List available enhancement presets
        
        Args:
            category: Optional category filter
            
        Returns:
            List of preset information dictionaries
        """        try:
            category_enum = None
            if category:
                category_enum = PresetCategory(category.lower())
            
            preset_names = self.config_manager.list_presets(category_enum)
            presets_info = []
            
            for name in preset_names:
                preset = self.config_manager.get_preset(name)
                if preset:
                    presets_info.append({
                        'name': preset.name,
                        'category': preset.category.value,
                        'description': preset.description,
                        'target_quality': preset.target_quality.value,
                        'content_types': [ct.value for ct in preset.content_types],
                        'use_cases': preset.use_cases
                    })
            
            return presets_info
            
        except Exception as e:
            self.logger.error(f"Failed to list presets: {str(e)}")
            return []
    
    def get_preset_info(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """        Get detailed information about a specific preset
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset information dictionary or None
        """        try:
            preset = self.config_manager.get_preset(preset_name)
            if not preset:
                return None
            
            return {
                'name': preset.name,
                'category': preset.category.value,
                'description': preset.description,
                'target_quality': preset.target_quality.value,
                'content_types': [ct.value for ct in preset.content_types],
                'use_cases': preset.use_cases,
                'parameters': {
                    'noise_reduction_strength': preset.parameters.noise_reduction_strength,
                    'spectral_enhancement_gain': preset.parameters.spectral_enhancement_gain,
                    'dynamic_range_target': preset.parameters.dynamic_range_target,
                    'stereo_width': preset.parameters.stereo_width,
                    'vocal_clarity': preset.parameters.vocal_clarity,
                    'mastering_loudness_lufs': preset.parameters.mastering_loudness_lufs
                },
                'version': preset.version,
                'author': preset.author
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get preset info: {str(e)}")
            return None
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""        pipeline_stats = self.pipeline.get_pipeline_statistics()
        processor_stats = self.processor.get_processing_statistics()
        preset_stats = self.config_manager.get_preset_statistics()
        
        return {
            'system_stats': self.processing_stats,
            'pipeline_stats': pipeline_stats,
            'processor_stats': processor_stats,
            'preset_stats': preset_stats,
            'realtime_status': self.get_realtime_metrics()
        }
    
    def _map_content_type(self, content_type: str) -> ContentType:
        """Map string content type to enum"""        mapping = {
            'music': ContentType.MUSIC,
            'speech': ContentType.SPEECH,
            'podcast': ContentType.PODCAST,
            'audiobook': ContentType.AUDIOBOOK,
            'voiceover': ContentType.VOICEOVER,
            'instrument': ContentType.INSTRUMENT,
            'sound_effect': ContentType.SOUND_EFFECT,
            'general': ContentType.GENERAL
        }
        return mapping.get(content_type.lower(), ContentType.GENERAL)
    
    def _map_processing_mode(self, mode: str) -> ProcessingMode:
        """Map string processing mode to enum"""        mapping = {
            'low_latency': ProcessingMode.LOW_LATENCY,
            'balanced': ProcessingMode.BALANCED,
            'high_quality': ProcessingMode.HIGH_QUALITY,
            'ultra_quality': ProcessingMode.ULTRA_QUALITY
        }
        return mapping.get(mode.lower(), ProcessingMode.BALANCED)
    
    def _get_preset_for_quality(self, quality: str, content_type: ContentType) -> EnhancementPreset:
        """Get appropriate preset for quality level and content type"""        quality_mapping = {
            'fast': QualityLevel.FAIR,
            'balanced': QualityLevel.GOOD,
            'high_quality': QualityLevel.EXCELLENT
        }
        
        target_quality = quality_mapping.get(quality.lower(), QualityLevel.GOOD)
        
        # Try to get preset for content type and quality
        preset = self.config_manager.get_preset_for_content(content_type, target_quality)
        
        # Fallback to default preset
        if not preset:
            presets = self.config_manager.list_presets()
            if presets:
                preset = self.config_manager.get_preset(presets[0])
        
        # Ultimate fallback - create basic preset
        if not preset:
            from . import DEFAULT_MUSIC_PARAMETERS
            preset = EnhancementPreset(
                name="Default",
                category=PresetCategory.CUSTOM,
                description="Default enhancement preset",
                parameters=DEFAULT_MUSIC_PARAMETERS,
                target_quality=target_quality,
                content_types=[content_type]
            )
        
        return preset
    
    def _generate_quality_warnings(self, metrics: QualityMetrics) -> List[str]:
        """Generate quality-based warnings"""        warnings = []
        
        if metrics.clipping_factor > 0.001:
            warnings.append(f"Audio clipping detected ({metrics.clipping_factor*100:.2f}%)")
        
        if metrics.snr_db < 20:
            warnings.append("Low signal-to-noise ratio detected")
        
        if metrics.dynamic_range_db < 6:
            warnings.append("Very limited dynamic range")
        
        if metrics.thd_percent > 3.0:
            warnings.append("High distortion levels detected")
        
        if metrics.overall_quality_score < 50:
            warnings.append("Overall audio quality is below acceptable standards")
        
        return warnings
    
    def _update_stats(self, result: EnhancementResult):
        """Update system processing statistics"""        self.processing_stats['total_enhancements'] += 1
        self.processing_stats['total_processing_time'] += result.processing_time
        
        # Update average quality improvement if available
        if hasattr(result, 'quality_improvement'):
            current_avg = self.processing_stats['average_quality_improvement']
            count = self.processing_stats['total_enhancements']
            new_avg = ((count - 1) * current_avg + getattr(result, 'quality_improvement', 0)) / count
            self.processing_stats['average_quality_improvement'] = new_avg


# Factory functions for easy instantiation
def create_enhancement_system(config_dir: Optional[Union[str, Path]] = None) -> AudioEnhancementSystem:
    """Create a new audio enhancement system instance"""    return AudioEnhancementSystem(config_dir)


def enhance_audio_quick(audio: np.ndarray, 
                       sample_rate: int,
                       content_type: str = "general",
                       quality: str = "balanced") -> Dict[str, Any]:
    """    Quick audio enhancement with minimal setup
    
    Args:
        audio: Input audio signal
        sample_rate: Sample rate in Hz
        content_type: Content type ("music", "speech", "podcast", "general")
        quality: Quality mode ("fast", "balanced", "high_quality")
        
    Returns:
        Dictionary with enhanced audio and basic metrics
    """    system = create_enhancement_system()
    return system.enhance_audio_simple(audio, sample_rate, content_type, quality)


def analyze_audio_quick(audio: np.ndarray, 
                       sample_rate: int) -> Dict[str, Any]:
    """    Quick audio quality analysis
    
    Args:
        audio: Input audio signal
        sample_rate: Sample rate in Hz
        
    Returns:
        Dictionary with quality metrics
    """    system = create_enhancement_system()
    return system.analyze_audio_quality(audio, sample_rate, detailed=False)


# Module-level convenience functions
def get_version() -> str:
    """Get module version"""    return __version__


def get_author() -> str:
    """Get module author"""    return __author__


def get_supported_formats() -> List[str]:
    """Get list of supported audio formats"""    return [
        "WAV", "FLAC", "MP3", "AAC", "OGG", "M4A", "WMA",
        "AIFF", "AU", "CAF", "RF64", "BWF"
    ]


def get_supported_sample_rates() -> Tuple[int, int]:
    """Get supported sample rate range"""    return (8000, 192000)  # 8 kHz to 192 kHz


def get_supported_bit_depths() -> List[int]:
    """Get supported bit depths"""    return [16, 24, 32]


def get_processing_modes() -> List[str]:
    """Get available processing modes"""    return ["low_latency", "balanced", "high_quality", "ultra_quality"]


def get_content_types() -> List[str]:
    """Get supported content types"""    return ["music", "speech", "podcast", "audiobook", "voiceover", 
           "instrument", "sound_effect", "general"]


def get_quality_levels() -> List[str]:
    """Get available quality levels"""    return ["fast", "balanced", "high_quality"]


# System information
SYSTEM_INFO = {
    'name': 'Audio Enhancement System',
    'version': __version__,
    'author': __author__,
    'description': __description__,
    'capabilities': [
        'Professional audio enhancement',
        'Real-time processing',
        'Quality analysis and metrics',
        'Intelligent configuration management',
        'Multi-pass processing pipelines',
        'Psychoacoustic analysis',
        'Content-adaptive processing'
    ],
    'supported_formats': get_supported_formats(),
    'sample_rate_range': get_supported_sample_rates(),
    'bit_depths': get_supported_bit_depths(),
    'processing_modes': get_processing_modes(),
    'content_types': get_content_types(),
    'quality_levels': get_quality_levels()
}


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""    return SYSTEM_INFO.copy()


# Export main classes and functions
__all__ = [
    # Main system class
    'AudioEnhancementSystem',
    
    # Factory functions
    'create_enhancement_system',
    'enhance_audio_quick',
    'analyze_audio_quick',
    
    # Information functions
    'get_version',
    'get_author', 
    'get_system_info',
    'get_supported_formats',
    'get_supported_sample_rates',
    'get_supported_bit_depths',
    'get_processing_modes',
    'get_content_types',
    'get_quality_levels',
    
    # Core components (re-exported)
    'AudioEnhancementProcessor',
    'RealTimeEnhancer',
    'AudioQualityAnalyzer',
    'EnhancementConfigManager',
    'AudioEnhancementPipeline',
    
    # Configuration classes
    'EnhancementParameters',
    'RealTimeConfig',
    'PipelineConfig',
    
    # Result classes
    'EnhancementResult',
    'QualityMetrics',
    'PipelineResult',
    
    # Enums
    'ContentType',
    'ProcessingMode',
    'QualityLevel',
    'PresetCategory',
    'PipelineMode',
    
    # System info
    'SYSTEM_INFO'
]
