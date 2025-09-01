"""Index - Professional Audio Format Conversion Module Index

Central index providing streamlined access to all audio format conversion
functionality with professional-grade interfaces and convenience methods.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION ⚠️

THIS SOFTWARE IS PROTECTED BY INTERNATIONAL COPYRIGHT AND INTELLECTUAL PROPERTY LAWS.
UNAUTHORIZED COPYING, MODIFICATION, DISTRIBUTION, OR USE IS STRICTLY PROHIBITED AND
CONSTITUTES CRIMINAL INTELLECTUAL PROPERTY THEFT. VIOLATIONS WILL BE PROSECUTED TO
THE FULL EXTENT OF THE LAW.

ALL RIGHTS RESERVED. PROPRIETARY AND CONFIDENTIAL.
"""

import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime

# Core conversion components
from .converter import AudioFormatConverter
from .quality import QualityController, QualityOptimizer
from .metadata import MetadataManager
from .formats import FormatRegistry
from .processors import ProcessorChain
from .config import ConversionConfig, DEFAULT_CONFIG
from .utils import ConversionUtils, FileUtils, CompressionUtils, ValidationUtils

# Data models and types
from .models import (
    AudioFormat, QualityLevel, ConversionRequest, ConversionResult,
    BatchConversionRequest, BatchConversionResult, AudioBuffer,
    FormatSpecification, QualityMetrics
)

logger = logging.getLogger(__name__)


@dataclass
class ConversionStatistics:
    """
    Conversion operation statistics
    
    Comprehensive statistics for conversion operations including
    performance metrics, quality analysis, and operational data.
    """
    total_conversions: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    total_input_size: int = 0
    total_output_size: int = 0
    compression_ratio: float = 1.0
    quality_scores: List[float] = None
    average_quality_score: float = 0.0
    format_distribution: Dict[str, int] = None
    error_distribution: Dict[str, int] = None
    
    def __post_init__(self):
        if self.quality_scores is None:
            self.quality_scores = []
        if self.format_distribution is None:
            self.format_distribution = {}
        if self.error_distribution is None:
            self.error_distribution = {}
    
    def calculate_averages(self):
        """
Calculate average metrics"""
        if self.total_conversions > 0:
            self.average_processing_time = self.total_processing_time / self.total_conversions
        
        if self.quality_scores:
            self.average_quality_score = sum(self.quality_scores) / len(self.quality_scores)
        
        if self.total_input_size > 0:
            self.compression_ratio = self.total_input_size / max(self.total_output_size, 1)
    
    @property
    def success_rate(self) -> float:
        """
Calculate success rate percentage"""
        if self.total_conversions == 0:
            return 0.0
        return (self.successful_conversions / self.total_conversions) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert statistics to dictionary"""
        return {
            'total_conversions': self.total_conversions,
            'successful_conversions': self.successful_conversions,
            'failed_conversions': self.failed_conversions,
            'success_rate': self.success_rate,
            'total_processing_time': self.total_processing_time,
            'average_processing_time': self.average_processing_time,
            'total_input_size': self.total_input_size,
            'total_output_size': self.total_output_size,
            'compression_ratio': self.compression_ratio,
            'average_quality_score': self.average_quality_score,
            'format_distribution': self.format_distribution.copy(),
            'error_distribution': self.error_distribution.copy()
        }


class AudioConversionIndex:
    """
    Professional Audio Conversion Index
    
    Central facade providing streamlined access to all audio format conversion
    functionality with comprehensive session management, statistics tracking,
    and professional-grade operational interfaces.
    """
    
    def __init__(self, config: Optional[ConversionConfig] = None):
        """
        Initialize Audio Conversion Index
        
        Args:
            config: Configuration object (uses DEFAULT_CONFIG if None)
        """
        self.config = config or DEFAULT_CONFIG
        self.session_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.statistics = ConversionStatistics()
        
        # Initialize core components
        self.converter = AudioFormatConverter(config=self.config)
        self.quality_controller = QualityController()
        self.quality_optimizer = QualityOptimizer()
        self.metadata_manager = MetadataManager()
        self.format_registry = FormatRegistry()
        
        # Thread pool for parallel operations
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_worker_threads)
        
        logger.info(f"AudioConversionIndex initialized - Session: {self.session_id}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
Context manager exit with cleanup"""
        self.cleanup()
    
    async def __aenter__(self):
        """
Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit with cleanup"""
        await self.cleanup_async()
    
    # ========================================
    # SINGLE FILE CONVERSION METHODS
    # ========================================
    
    async def convert_file_async(self, 
                               source_path: Union[str, Path],
                               target_path: Union[str, Path],
                               target_format: AudioFormat,
                               quality_level: QualityLevel = QualityLevel.HIGH,
                               processing_options: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """
        Convert single audio file asynchronously
        
        Args:
            source_path: Path to source audio file
            target_path: Path for converted output file
            target_format: Target audio format
            quality_level: Quality level for conversion
            processing_options: Additional processing options
            
        Returns:
            ConversionResult with operation details
        """
        start_time = datetime.now()
        
        try:
            # Create conversion request
            request = ConversionRequest(
                source_path=Path(source_path),
                target_path=Path(target_path),
                target_format=target_format,
                quality_level=quality_level,
                processing_options=processing_options or {}
            )
            
            # Perform conversion
            result = await self.converter.convert_async(request)
            
            # Update statistics
            self._update_statistics(result, start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"File conversion failed: {e}")
            
            # Create error result
            result = ConversionResult(
                source_path=Path(source_path),
                target_path=Path(target_path),
                target_format=target_format,
                success=False,
                error_message=str(e)
            )
            
            self._update_statistics(result, start_time)
            return result
    
    def convert_file(self, 
                    source_path: Union[str, Path],
                    target_path: Union[str, Path],
                    target_format: AudioFormat,
                    quality_level: QualityLevel = QualityLevel.HIGH,
                    processing_options: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """
        Convert single audio file synchronously
        
        Args:
            source_path: Path to source audio file
            target_path: Path for converted output file
            target_format: Target audio format
            quality_level: Quality level for conversion
            processing_options: Additional processing options
            
        Returns:
            ConversionResult with operation details
        """
        return asyncio.run(self.convert_file_async(
            source_path, target_path, target_format, quality_level, processing_options
        ))
    
    # ========================================
    # BATCH CONVERSION METHODS
    # ========================================
    
    async def convert_batch_async(self,
                                source_files: List[Union[str, Path]],
                                target_directory: Union[str, Path],
                                target_format: AudioFormat,
                                quality_level: QualityLevel = QualityLevel.HIGH,
                                parallel_processing: bool = True,
                                preserve_structure: bool = False) -> BatchConversionResult:
        """
        Convert multiple audio files asynchronously
        
        Args:
            source_files: List of source file paths
            target_directory: Directory for converted files
            target_format: Target audio format
            quality_level: Quality level for conversion
            parallel_processing: Whether to process files in parallel
            preserve_structure: Whether to preserve directory structure
            
        Returns:
            BatchConversionResult with all operation details
        """
        start_time = datetime.now()
        target_dir = Path(target_directory)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        conversion_tasks = []
        results = []
        
        for source_file in source_files:
            source_path = Path(source_file)
            
            # Determine target path
            if preserve_structure:
                # Maintain relative directory structure
                relative_path = source_path.parent
                target_path = target_dir / relative_path / f"{source_path.stem}.{target_format.value}"
            else:
                # Flat structure in target directory
                target_path = target_dir / f"{source_path.stem}.{target_format.value}"
            
            # Create target directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            if parallel_processing:
                # Add to parallel task list
                task = self.convert_file_async(
                    source_path, target_path, target_format, quality_level
                )
                conversion_tasks.append(task)
            else:
                # Process sequentially
                result = await self.convert_file_async(
                    source_path, target_path, target_format, quality_level
                )
                results.append(result)
        
        # Execute parallel tasks if enabled
        if parallel_processing and conversion_tasks:
            results = await asyncio.gather(*conversion_tasks, return_exceptions=True)
            
            # Handle exceptions in results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    source_path = Path(source_files[i])
                    target_path = target_dir / f"{source_path.stem}.{target_format.value}"
                    
                    error_result = ConversionResult(
                        source_path=source_path,
                        target_path=target_path,
                        target_format=target_format,
                        success=False,
                        error_message=str(result)
                    )
                    results[i] = error_result
        
        # Create batch result
        processing_time = (datetime.now() - start_time).total_seconds()
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        batch_result = BatchConversionResult(
            total_files=len(source_files),
            successful_conversions=len(successful_results),
            failed_conversions=len(failed_results),
            results=results,
            processing_time=processing_time,
            target_directory=target_dir
        )
        
        logger.info(f"Batch conversion completed: {len(successful_results)}/{len(source_files)} successful")
        return batch_result
    
    def convert_batch(self,
                     source_files: List[Union[str, Path]],
                     target_directory: Union[str, Path],
                     target_format: AudioFormat,
                     quality_level: QualityLevel = QualityLevel.HIGH,
                     parallel_processing: bool = True,
                     preserve_structure: bool = False) -> BatchConversionResult:
        """
        Convert multiple audio files synchronously
        
        Args:
            source_files: List of source file paths
            target_directory: Directory for converted files
            target_format: Target audio format
            quality_level: Quality level for conversion
            parallel_processing: Whether to process files in parallel
            preserve_structure: Whether to preserve directory structure
            
        Returns:
            BatchConversionResult with all operation details
        """
        return asyncio.run(self.convert_batch_async(
            source_files, target_directory, target_format, 
            quality_level, parallel_processing, preserve_structure
        ))
    
    # ========================================
    # DIRECTORY CONVERSION METHODS
    # ========================================
    
    async def convert_directory_async(self,
                                    source_directory: Union[str, Path],
                                    target_directory: Union[str, Path],
                                    target_format: AudioFormat,
                                    quality_level: QualityLevel = QualityLevel.HIGH,
                                    recursive: bool = True,
                                    file_patterns: Optional[List[str]] = None) -> BatchConversionResult:
        """
        Convert all audio files in a directory asynchronously
        
        Args:
            source_directory: Source directory path
            target_directory: Target directory path
            target_format: Target audio format
            quality_level: Quality level for conversion
            recursive: Whether to search subdirectories
            file_patterns: File pattern filters (e.g., ['*.wav', '*.flac'])
            
        Returns:
            BatchConversionResult with all operation details
        """
        source_dir = Path(source_directory)
        
        if not source_dir.exists() or not source_dir.is_dir():
            raise ValueError(f"Source directory does not exist: {source_directory}")
        
        # Find audio files
        audio_files = []
        patterns = file_patterns or ['*.wav', '*.flac', '*.mp3', '*.aac', '*.ogg', '*.opus', '*.aiff', '*.m4a']
        
        for pattern in patterns:
            if recursive:
                audio_files.extend(source_dir.rglob(pattern))
            else:
                audio_files.extend(source_dir.glob(pattern))
        
        # Remove duplicates and sort
        audio_files = sorted(list(set(audio_files)))
        
        logger.info(f"Found {len(audio_files)} audio files in {source_directory}")
        
        # Convert batch with structure preservation
        return await self.convert_batch_async(
            audio_files, target_directory, target_format, 
            quality_level, parallel_processing=True, preserve_structure=True
        )
    
    def convert_directory(self,
                         source_directory: Union[str, Path],
                         target_directory: Union[str, Path],
                         target_format: AudioFormat,
                         quality_level: QualityLevel = QualityLevel.HIGH,
                         recursive: bool = True,
                         file_patterns: Optional[List[str]] = None) -> BatchConversionResult:
        """
        Convert all audio files in a directory synchronously
        
        Args:
            source_directory: Source directory path
            target_directory: Target directory path
            target_format: Target audio format
            quality_level: Quality level for conversion
            recursive: Whether to search subdirectories
            file_patterns: File pattern filters (e.g., ['*.wav', '*.flac'])
            
        Returns:
            BatchConversionResult with all operation details
        """
        return asyncio.run(self.convert_directory_async(
            source_directory, target_directory, target_format,
            quality_level, recursive, file_patterns
        ))
    
    # ========================================
    # QUALITY ANALYSIS METHODS
    # ========================================
    
    async def analyze_quality_async(self, file_path: Union[str, Path]) -> QualityMetrics:
        """
        Analyze audio quality asynchronously
        
        Args:
            file_path: Path to audio file
            
        Returns:
            QualityMetrics with detailed analysis
        """
        return await self.quality_controller.analyze_quality_async(Path(file_path))
    
    def analyze_quality(self, file_path: Union[str, Path]) -> QualityMetrics:
        """
        Analyze audio quality synchronously
        
        Args:
            file_path: Path to audio file
            
        Returns:
            QualityMetrics with detailed analysis
        """
        return asyncio.run(self.analyze_quality_async(file_path))
    
    def get_quality_recommendations(self, 
                                  source_path: Union[str, Path],
                                  target_format: AudioFormat) -> List[str]:
        """
        Get quality optimization recommendations
        
        Args:
            source_path: Path to source audio file
            target_format: Target format for conversion
            
        Returns:
            List of quality recommendations
        """
        try:
            # Analyze source quality
            quality_metrics = self.analyze_quality(source_path)
            
            # Get format profile
            format_profile = self.config.get_format_profile(target_format)
            if not format_profile:
                return ["Format not supported"]
            
            recommendations = []
            
            # Dynamic range recommendations
            if quality_metrics.dynamic_range > 40:
                recommendations.append("High dynamic range detected - use lossless format for best quality")
            elif quality_metrics.dynamic_range < 20:
                recommendations.append("Low dynamic range - lossy compression acceptable")
            
            # Frequency content recommendations
            if quality_metrics.frequency_range > 20000:
                recommendations.append("Full frequency spectrum - avoid aggressive compression")
            
            # Format-specific recommendations
            if target_format == AudioFormat.MP3 and quality_metrics.overall_score > 0.9:
                recommendations.append("Consider using 320kbps VBR for high-quality source")
            elif target_format in [AudioFormat.AAC, AudioFormat.OGG] and quality_metrics.overall_score > 0.85:
                recommendations.append("Use high bitrate settings to preserve quality")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Quality recommendation failed: {e}")
            return [f"Quality analysis failed: {e}"]
    
    # ========================================
    # FORMAT AND COMPATIBILITY METHODS
    # ========================================
    
    def get_supported_formats(self) -> List[AudioFormat]:
        """Get list of all supported audio formats"""
        return list(AudioFormat)
    
    def detect_format(self, file_path: Union[str, Path]) -> Optional[AudioFormat]:
        """
        Detect audio format from file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Detected AudioFormat or None if detection fails
        """
        return ConversionUtils.detect_audio_format(Path(file_path))
    
    def validate_conversion(self, 
                          source_path: Union[str, Path],
                          target_format: AudioFormat) -> Dict[str, Any]:
        """
        Validate conversion compatibility
        
        Args:
            source_path: Path to source audio file
            target_format: Target audio format
            
        Returns:
            Validation result with compatibility info and warnings
        """
        try:
            # Get source specifications
            source_specs = ConversionUtils.get_audio_specs(Path(source_path))
            source_format = source_specs.get('format')
            
            if not source_format:
                return {
                    'valid': False,
                    'error': 'Could not detect source format',
                    'warnings': [],
                    'recommendations': []
                }
            
            # Validate compatibility
            validation = ConversionUtils.validate_conversion_compatibility(
                source_format, target_format, source_specs
            )
            
            return {
                'valid': validation['compatible'],
                'quality_loss_expected': validation['quality_loss_expected'],
                'estimated_quality_retention': validation['estimated_quality_retention'],
                'warnings': validation['warnings'],
                'recommendations': validation['recommendations']
            }
            
        except Exception as e:
            logger.error(f"Conversion validation failed: {e}")
            return {
                'valid': False,
                'error': str(e),
                'warnings': [],
                'recommendations': []
            }
    
    # ========================================
    # STATISTICS AND MONITORING METHODS
    # ========================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current session statistics"""
        self.statistics.calculate_averages()
        return self.statistics.to_dict()
    
    def reset_statistics(self):
        """
Reset session statistics"""
        self.statistics = ConversionStatistics()
        logger.info("Statistics reset")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            'session_id': self.session_id,
            'config': self.config.to_dict(),
            'statistics': self.get_statistics()
        }
    
    # ========================================
    # UTILITY AND MAINTENANCE METHODS
    # ========================================
    
    def cleanup_temp_files(self) -> int:
        """
        Clean up temporary files
        
        Returns:
            Number of files cleaned up
        """
        if not self.config.temp_directory:
            return 0
        
        temp_dir = Path(self.config.temp_directory)
        if not temp_dir.exists():
            return 0
        
        cleaned_count = 0
        temp_prefix = self.config.temp_file_prefix
        
        try:
            for temp_file in temp_dir.glob(f"{temp_prefix}*"):
                if temp_file.is_file():
                    if self.config.secure_delete_temp:
                        FileUtils.safe_remove(temp_file, secure_delete=True)
                    else:
                        temp_file.unlink()
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Temp file cleanup failed: {e}")
            return cleaned_count
    
    def validate_configuration(self) -> List[str]:
        """
        Validate current configuration
        
        Returns:
            List of configuration issues (empty if valid)
        """
        return self.config.validate_configuration()
    
    def cleanup(self):
        """
Cleanup resources synchronously"""
        try:
            # Cleanup temporary files if configured
            if self.config.clean_temp_files:
                self.cleanup_temp_files()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info(f"AudioConversionIndex cleanup completed - Session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def cleanup_async(self):
        """Cleanup resources asynchronously"""
        try:
            # Cleanup temporary files if configured
            if self.config.clean_temp_files:
                self.cleanup_temp_files()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info(f"AudioConversionIndex async cleanup completed - Session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Async cleanup failed: {e}")
    
    def _update_statistics(self, result: ConversionResult, start_time: datetime):
        """Update session statistics with conversion result"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.statistics.total_conversions += 1
        self.statistics.total_processing_time += processing_time
        
        if result.success:
            self.statistics.successful_conversions += 1
            
            # Update file sizes if available
            if result.source_file_size:
                self.statistics.total_input_size += result.source_file_size
            
            if result.target_file_size:
                self.statistics.total_output_size += result.target_file_size
            
            # Update quality scores
            if result.quality_metrics:
                self.statistics.quality_scores.append(result.quality_metrics.overall_score)
            
            # Update format distribution
            format_name = result.target_format.value
            self.statistics.format_distribution[format_name] = \
                self.statistics.format_distribution.get(format_name, 0) + 1
        
        else:
            self.statistics.failed_conversions += 1
            
            # Update error distribution
            error_type = result.error_code or "unknown_error"
            self.statistics.error_distribution[error_type] = \
                self.statistics.error_distribution.get(error_type, 0) + 1


# ========================================
# CONVENIENCE FACTORY FUNCTIONS
# ========================================

def create_converter(config: Optional[ConversionConfig] = None) -> AudioConversionIndex:
    """
    Factory function to create AudioConversionIndex instance
    
    Args:
        config: Configuration object (uses DEFAULT_CONFIG if None)
        
    Returns:
        Configured AudioConversionIndex instance
    """
    return AudioConversionIndex(config)


def quick_convert(source_path: Union[str, Path],
                 target_path: Union[str, Path],
                 target_format: AudioFormat,
                 quality_level: QualityLevel = QualityLevel.HIGH) -> ConversionResult:
    """
    Quick single file conversion function
    
    Args:
        source_path: Path to source audio file
        target_path: Path for converted output file
        target_format: Target audio format
        quality_level: Quality level for conversion
        
    Returns:
        ConversionResult with operation details
    """
    with AudioConversionIndex() as converter:
        return converter.convert_file(source_path, target_path, target_format, quality_level)


def quick_batch_convert(source_files: List[Union[str, Path]],
                       target_directory: Union[str, Path],
                       target_format: AudioFormat,
                       quality_level: QualityLevel = QualityLevel.HIGH) -> BatchConversionResult:
    """
    Quick batch conversion function
    
    Args:
        source_files: List of source file paths
        target_directory: Directory for converted files
        target_format: Target audio format
        quality_level: Quality level for conversion
        
    Returns:
        BatchConversionResult with all operation details
    """
    with AudioConversionIndex() as converter:
        return converter.convert_batch(source_files, target_directory, target_format, quality_level)


def quick_directory_convert(source_directory: Union[str, Path],
                           target_directory: Union[str, Path],
                           target_format: AudioFormat,
                           quality_level: QualityLevel = QualityLevel.HIGH) -> BatchConversionResult:
    """
    Quick directory conversion function
    
    Args:
        source_directory: Source directory path
        target_directory: Target directory path
        target_format: Target audio format
        quality_level: Quality level for conversion
        
    Returns:
        BatchConversionResult with all operation details
    """
    with AudioConversionIndex() as converter:
        return converter.convert_directory(source_directory, target_directory, target_format, quality_level)


# Export all public interfaces
__all__ = [
    # Main index class
    'AudioConversionIndex',
    
    # Statistics and data classes
    'ConversionStatistics',
    
    # Factory and convenience functions
    'create_converter',
    'quick_convert',
    'quick_batch_convert', 
    'quick_directory_convert',
    
    # Re-exported core components
    'AudioFormatConverter',
    'QualityController',
    'MetadataManager',
    'FormatRegistry',
    'ProcessorChain',
    
    # Re-exported models and enums
    'AudioFormat',
    'QualityLevel',
    'ConversionRequest',
    'ConversionResult',
    'BatchConversionRequest',
    'BatchConversionResult',
    'QualityMetrics',
    
    # Configuration
    'ConversionConfig',
    'DEFAULT_CONFIG'
]
