"""Format Converter - Universal format conversion for IA Influencer Agent Platform
===============================================================================

Professional format conversion utilities handling multi-format content
transformation workflows for creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import time

logger = logging.getLogger(__name__)


class ConversionType(Enum):
    """
Types of format conversion."""

    AUDIO_TO_AUDIO = "audio_to_audio"
    VIDEO_TO_VIDEO = "video_to_video"
    IMAGE_TO_IMAGE = "image_to_image"
    TEXT_TO_TEXT = "text_to_text"
    AUDIO_TO_VIDEO = "audio_to_video"
    VIDEO_TO_AUDIO = "video_to_audio"
    IMAGE_TO_VIDEO = "image_to_video"
    DOCUMENT_TO_TEXT = "document_to_text"


@dataclass
class ConversionRule:
    """Format conversion rule definition."""
    source_format: str
    target_format: str
    conversion_type: ConversionType
    transformer_class: str
    quality_mapping: Dict[str, Any]
    supported_options: List[str]
    default_settings: Dict[str, Any]


@dataclass
class ConversionRequest:
    """
Format conversion request."""
    input_path: str
    output_path: Optional[str] = None
    source_format: Optional[str] = None
    target_format: str = "mp3"
    quality: str = "high"
    options: Optional[Dict[str, Any]] = None


class FormatConverter:
    """
    Universal format converter for the IA Influencer Agent Platform.
    
    Provides intelligent format conversion routing and optimization
    for creator content workflows.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize format converter.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        
        # Initialize conversion rules
        self.conversion_rules = self._init_conversion_rules()
        
        # Format compatibility matrix
        self.compatibility_matrix = self._build_compatibility_matrix()
        
        # Quality mappings
        self.quality_mappings = self._init_quality_mappings()
        
        logger.info("FormatConverter initialized")
    
    def _init_conversion_rules(self) -> Dict[str, ConversionRule]:
        """Initialize format conversion rules."""
        rules = {}
        
        # Audio conversions
        audio_formats = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']
        for source in audio_formats:
            for target in audio_formats:
                if source != target:
                    rule_key = f"{source}_to_{target}"
                    rules[rule_key] = ConversionRule(
                        source_format=source,
                        target_format=target,
                        conversion_type=ConversionType.AUDIO_TO_AUDIO,
                        transformer_class="AudioTransformer",
                        quality_mapping={
                            "low": {"bitrate": 128},
                            "medium": {"bitrate": 192},
                            "high": {"bitrate": 256},
                            "lossless": {"bitrate": None}
                        },
                        supported_options=[
                            "bitrate", "sample_rate", "channels", "normalize",
                            "noise_reduction", "enhance_bass", "enhance_treble"
                        ],
                        default_settings={"bitrate": 192, "sample_rate": 44100}
                    )
        
        # Video conversions
        video_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv']
        for source in video_formats:
            for target in video_formats:
                if source != target:
                    rule_key = f"{source}_to_{target}"
                    rules[rule_key] = ConversionRule(
                        source_format=source,
                        target_format=target,
                        conversion_type=ConversionType.VIDEO_TO_VIDEO,
                        transformer_class="VideoTransformer",
                        quality_mapping={
                            "low": {"width": 854, "height": 480, "bitrate": 1000},
                            "medium": {"width": 1280, "height": 720, "bitrate": 2500},
                            "high": {"width": 1920, "height": 1080, "bitrate": 5000},
                            "ultra": {"width": 2560, "height": 1440, "bitrate": 10000}
                        },
                        supported_options=[
                            "width", "height", "fps", "bitrate", "codec", "preset",
                            "stabilize", "denoise", "enhance_colors"
                        ],
                        default_settings={"width": 1280, "height": 720, "fps": 30}
                    )
        
        # Image conversions
        image_formats = ['jpg', 'png', 'webp', 'gif', 'bmp', 'tiff']
        for source in image_formats:
            for target in image_formats:
                if source != target:
                    rule_key = f"{source}_to_{target}"
                    rules[rule_key] = ConversionRule(
                        source_format=source,
                        target_format=target,
                        conversion_type=ConversionType.IMAGE_TO_IMAGE,
                        transformer_class="ImageTransformer",
                        quality_mapping={
                            "low": {"compression": 60},
                            "medium": {"compression": 80},
                            "high": {"compression": 95},
                            "lossless": {"compression": 100}
                        },
                        supported_options=[
                            "width", "height", "compression", "optimize", "progressive",
                            "enhance_brightness", "enhance_contrast", "noise_reduction"
                        ],
                        default_settings={"compression": 85, "optimize": True}
                    )
        
        # Text conversions
        text_formats = ['txt', 'json', 'xml', 'html', 'md', 'csv']
        for source in text_formats:
            for target in text_formats:
                if source != target:
                    rule_key = f"{source}_to_{target}"
                    rules[rule_key] = ConversionRule(
                        source_format=source,
                        target_format=target,
                        conversion_type=ConversionType.TEXT_TO_TEXT,
                        transformer_class="TextTransformer",
                        quality_mapping={
                            "low": {"compression": "basic"},
                            "medium": {"compression": "standard"},
                            "high": {"compression": "enhanced"}
                        },
                        supported_options=[
                            "encoding", "remove_html", "normalize_unicode",
                            "extract_keywords", "sentiment_analysis"
                        ],
                        default_settings={"encoding": "utf-8"}
                    )
        
        # Cross-format conversions
        # Video to audio
        for video_fmt in video_formats:
            for audio_fmt in audio_formats:
                rule_key = f"{video_fmt}_to_{audio_fmt}"
                rules[rule_key] = ConversionRule(
                    source_format=video_fmt,
                    target_format=audio_fmt,
                    conversion_type=ConversionType.VIDEO_TO_AUDIO,
                    transformer_class="VideoTransformer",
                    quality_mapping={
                        "low": {"audio_bitrate": 128},
                        "medium": {"audio_bitrate": 192},
                        "high": {"audio_bitrate": 256}
                    },
                    supported_options=["audio_bitrate", "sample_rate", "channels"],
                    default_settings={"audio_bitrate": 192}
                )
        
        return rules
    
    def _build_compatibility_matrix(self) -> Dict[str, List[str]]:
        """Build format compatibility matrix."""
        return {
            # Audio formats
            'mp3': ['wav', 'flac', 'aac', 'ogg', 'm4a'],
            'wav': ['mp3', 'flac', 'aac', 'ogg'],
            'flac': ['mp3', 'wav', 'aac', 'ogg'],
            'aac': ['mp3', 'wav', 'flac', 'ogg', 'm4a'],
            'ogg': ['mp3', 'wav', 'flac', 'aac'],
            'm4a': ['mp3', 'wav', 'aac'],
            
            # Video formats
            'mp4': ['avi', 'mov', 'mkv', 'webm'],
            'avi': ['mp4', 'mov', 'mkv'],
            'mov': ['mp4', 'avi', 'mkv'],
            'mkv': ['mp4', 'avi', 'mov', 'webm'],
            'webm': ['mp4', 'mkv'],
            'wmv': ['mp4', 'avi'],
            
            # Image formats
            'jpg': ['png', 'webp', 'bmp', 'tiff'],
            'png': ['jpg', 'webp', 'gif', 'bmp', 'tiff'],
            'webp': ['jpg', 'png', 'gif'],
            'gif': ['png', 'webp'],
            'bmp': ['jpg', 'png', 'tiff'],
            'tiff': ['jpg', 'png', 'bmp'],
            
            # Text formats
            'txt': ['json', 'xml', 'html', 'md', 'csv'],
            'json': ['txt', 'xml', 'yaml', 'csv'],
            'xml': ['txt', 'json', 'html'],
            'html': ['txt', 'xml', 'md'],
            'md': ['txt', 'html'],
            'csv': ['txt', 'json', 'xml']
        }
    
    def _init_quality_mappings(self) -> Dict[str, Dict[str, Any]]:
        """
Initialize quality mappings for different content types."""
        return {
            'audio': {
                'low': {'bitrate': 128, 'sample_rate': 44100},
                'medium': {'bitrate': 192, 'sample_rate': 44100},
                'high': {'bitrate': 256, 'sample_rate': 44100},
                'lossless': {'bitrate': None, 'sample_rate': 48000}
            },
            'video': {
                'low': {'width': 854, 'height': 480, 'bitrate': 1000, 'fps': 24},
                'medium': {'width': 1280, 'height': 720, 'bitrate': 2500, 'fps': 30},
                'high': {'width': 1920, 'height': 1080, 'bitrate': 5000, 'fps': 30},
                'ultra': {'width': 3840, 'height': 2160, 'bitrate': 15000, 'fps': 30}
            },
            'image': {
                'low': {'compression': 60, 'max_dimension': 1024},
                'medium': {'compression': 80, 'max_dimension': 1920},
                'high': {'compression': 95, 'max_dimension': 3840},
                'lossless': {'compression': 100, 'max_dimension': None}
            }
        }
    
    async def convert(
        self,
        input_path: str,
        target_format: str,
        output_path: Optional[str] = None,
        quality: str = "high",
        **options
    ) -> Dict[str, Any]:
        """
        Convert file to target format.
        
        Args:
            input_path: Input file path
            target_format: Target format
            output_path: Output file path (optional)
            quality: Quality level
            **options: Additional conversion options
            
        Returns:
            Conversion result
        """
        try:
            # Detect source format
            source_format = self._detect_format(input_path)
            if not source_format:
                raise ValueError(f"Cannot detect format for file: {input_path}")
            
            # Create conversion request
            request = ConversionRequest(
                input_path=input_path,
                output_path=output_path,
                source_format=source_format,
                target_format=target_format,
                quality=quality,
                options=options
            )
            
            # Validate conversion
            validation = await self._validate_conversion(request)
            if not validation['valid']:
                raise ValueError(f"Invalid conversion: {validation['reason']}")
            
            # Get conversion rule
            rule = self._get_conversion_rule(source_format, target_format)
            if not rule:
                raise ValueError(f"No conversion rule for {source_format} to {target_format}")
            
            # Perform conversion
            result = await self._perform_conversion(request, rule)
            
            return result
            
        except Exception as e:
            logger.error(f"Format conversion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_path': input_path,
                'target_format': target_format
            }
    
    async def batch_convert(
        self,
        file_paths: List[str],
        target_format: str,
        output_dir: Optional[str] = None,
        quality: str = "high",
        **options
    ) -> List[Dict[str, Any]]:
        """
        Convert multiple files in batch.
        
        Args:
            file_paths: List of input file paths
            target_format: Target format
            output_dir: Output directory
            quality: Quality level
            **options: Additional conversion options
            
        Returns:
            List of conversion results
        """
        results = []
        
        for file_path in file_paths:
            try:
                # Generate output path
                input_file = Path(file_path)
                if output_dir:
                    output_path = Path(output_dir) / f"{input_file.stem}.{target_format}"
                else:
                    output_path = input_file.parent / f"{input_file.stem}_converted.{target_format}"
                
                # Convert file
                result = await self.convert(
                    input_path=file_path,
                    target_format=target_format,
                    output_path=str(output_path),
                    quality=quality,
                    **options
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Batch conversion failed for {file_path}: {str(e)}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'input_path': file_path,
                    'target_format': target_format
                })
        
        return results
    
    def get_supported_conversions(self, source_format: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get supported format conversions.
        
        Args:
            source_format: Source format (optional, returns all if None)
            
        Returns:
            Dictionary of supported conversions
        """
        if source_format:
            return {source_format: self.compatibility_matrix.get(source_format, [])}
        else:
            return self.compatibility_matrix.copy()
    
    def get_conversion_info(self, source_format: str, target_format: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific conversion.
        
        Args:
            source_format: Source format
            target_format: Target format
            
        Returns:
            Conversion information
        """
        rule = self._get_conversion_rule(source_format, target_format)
        if not rule:
            return None
        
        return {
            'source_format': rule.source_format,
            'target_format': rule.target_format,
            'conversion_type': rule.conversion_type.value,
            'transformer_class': rule.transformer_class,
            'quality_levels': list(rule.quality_mapping.keys()),
            'supported_options': rule.supported_options,
            'default_settings': rule.default_settings
        }
    
    def suggest_optimal_format(
        self,
        source_format: str,
        use_case: str = "general",
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suggest optimal target format based on use case.
        
        Args:
            source_format: Source format
            use_case: Use case (web, mobile, archive, streaming, etc.)
            constraints: Constraints (file_size, quality, compatibility)
            
        Returns:
            Format recommendation
        """
        constraints = constraints or {}
        
        # Use case recommendations
        recommendations = {
            'web': {
                'audio': {'format': 'mp3', 'quality': 'medium'},
                'video': {'format': 'mp4', 'quality': 'medium'},
                'image': {'format': 'webp', 'quality': 'high'}
            },
            'mobile': {
                'audio': {'format': 'aac', 'quality': 'medium'},
                'video': {'format': 'mp4', 'quality': 'medium'},
                'image': {'format': 'webp', 'quality': 'medium'}
            },
            'archive': {
                'audio': {'format': 'flac', 'quality': 'lossless'},
                'video': {'format': 'mkv', 'quality': 'high'},
                'image': {'format': 'png', 'quality': 'lossless'}
            },
            'streaming': {
                'audio': {'format': 'ogg', 'quality': 'high'},
                'video': {'format': 'webm', 'quality': 'high'},
                'image': {'format': 'webp', 'quality': 'high'}
            }
        }
        
        # Determine content type
        content_type = self._determine_content_type(source_format)
        
        # Get recommendation for use case
        use_case_rec = recommendations.get(use_case, recommendations['general'])
        base_rec = use_case_rec.get(content_type, {'format': source_format, 'quality': 'high'})
        
        # Apply constraints
        final_rec = base_rec.copy()
        
        if constraints.get('max_file_size'):
            # Adjust quality for file size constraints
            if final_rec['quality'] in ['lossless', 'ultra']:
                final_rec['quality'] = 'high'
            elif final_rec['quality'] == 'high':
                final_rec['quality'] = 'medium'
        
        if constraints.get('compatibility_required'):
            # Use most compatible formats
            compatible_formats = {
                'audio': 'mp3',
                'video': 'mp4',
                'image': 'jpg'
            }
            final_rec['format'] = compatible_formats.get(content_type, final_rec['format'])
        
        return {
            'recommended_format': final_rec['format'],
            'recommended_quality': final_rec['quality'],
            'content_type': content_type,
            'use_case': use_case,
            'reasoning': f"Optimized for {use_case} use case",
            'conversion_available': self._is_conversion_available(source_format, final_rec['format'])
        }
    
    def _detect_format(self, file_path: str) -> Optional[str]:
        """Detect file format from path."""
        try:
            path = Path(file_path)
            extension = path.suffix.lower().lstrip('.')
            
            # Map common extensions
            format_mapping = {
                'jpeg': 'jpg',
                'mpeg': 'mpg',
                'tiff': 'tif'
            }
            
            return format_mapping.get(extension, extension)
            
        except Exception as e:
            logger.error(f"Format detection failed: {str(e)}")
            return None
    
    def _determine_content_type(self, format: str) -> str:
        """Determine content type from format."""
        audio_formats = {'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma'}
        video_formats = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv', 'flv'}
        image_formats = {'jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'svg'}
        text_formats = {'txt', 'json', 'xml', 'html', 'md', 'csv', 'yaml'}
        
        if format in audio_formats:
            return 'audio'
        elif format in video_formats:
            return 'video'
        elif format in image_formats:
            return 'image'
        elif format in text_formats:
            return 'text'
        else:
            return 'unknown'
    
    def _get_conversion_rule(self, source_format: str, target_format: str) -> Optional[ConversionRule]:
        """
Get conversion rule for format pair."""
        rule_key = f"{source_format}_to_{target_format}"
        return self.conversion_rules.get(rule_key)
    
    def _is_conversion_available(self, source_format: str, target_format: str) -> bool:
        """Check if conversion is available."""
        return self._get_conversion_rule(source_format, target_format) is not None
    
    async def _validate_conversion(self, request: ConversionRequest) -> Dict[str, Any]:
        """
Validate conversion request."""
        try:
            # Check if file exists
            if not Path(request.input_path).exists():
                return {'valid': False, 'reason': 'Input file does not exist'}
            
            # Check if conversion is supported
            if not self._is_conversion_available(request.source_format, request.target_format):
                return {'valid': False, 'reason': f'Conversion from {request.source_format} to {request.target_format} not supported'}
            
            # Check quality level
            rule = self._get_conversion_rule(request.source_format, request.target_format)
            if rule and request.quality not in rule.quality_mapping:
                return {'valid': False, 'reason': f'Quality level {request.quality} not supported'}
            
            return {'valid': True, 'reason': 'Conversion is valid'}
            
        except Exception as e:
            return {'valid': False, 'reason': str(e)}
    
    async def _perform_conversion(
        self,
        request: ConversionRequest,
        rule: ConversionRule
    ) -> Dict[str, Any]:
        """
Perform the actual conversion."""
        try:
            start_time = time.time()
            
            # Import appropriate transformer
            if rule.transformer_class == "AudioTransformer":
                from .audio_transformer import AudioTransformer
                transformer = AudioTransformer()
            elif rule.transformer_class == "VideoTransformer":
                from .video_transformer import VideoTransformer
                transformer = VideoTransformer()
            elif rule.transformer_class == "ImageTransformer":
                from .image_transformer import ImageTransformer
                transformer = ImageTransformer()
            elif rule.transformer_class == "TextTransformer":
                from .text_transformer import TextTransformer
                transformer = TextTransformer()
            else:
                raise ValueError(f"Unknown transformer class: {rule.transformer_class}")
            
            # Prepare conversion settings
            quality_settings = rule.quality_mapping.get(request.quality, {})
            conversion_options = {**rule.default_settings, **quality_settings}
            
            if request.options:
                conversion_options.update(request.options)
            
            # Generate output path if not provided
            if not request.output_path:
                input_path = Path(request.input_path)
                request.output_path = str(input_path.parent / f"{input_path.stem}.{request.target_format}")
            
            # Perform conversion using transformer
            result = await transformer.convert(
                input_path=request.input_path,
                output_path=request.output_path,
                format=request.target_format,
                quality=request.quality,
                **conversion_options
            )
            
            processing_time = time.time() - start_time
            
            if result:
                return {
                    'success': True,
                    'input_path': request.input_path,
                    'output_path': request.output_path,
                    'source_format': request.source_format,
                    'target_format': request.target_format,
                    'quality': request.quality,
                    'processing_time': processing_time,
                    'conversion_type': rule.conversion_type.value,
                    'settings_used': conversion_options
                }
            else:
                return {
                    'success': False,
                    'error': 'Conversion failed',
                    'input_path': request.input_path,
                    'target_format': request.target_format
                }
            
        except Exception as e:
            logger.error(f"Conversion execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_path': request.input_path,
                'target_format': request.target_format
            }


class MultiFormatConverter:
    """Multi-format converter with advanced routing."""
    
    def __init__(self, converter: Optional[FormatConverter] = None):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def convert_multiple_formats(
        self,
        input_path: str,
        target_formats: List[str],
        output_dir: Optional[str] = None,
        quality: str = "high"
    ) -> List[Dict[str, Any]]:
        """Convert single file to multiple formats."""
        results = []
        
        for target_format in target_formats:
            try:
                # Generate output path
                input_file = Path(input_path)
                if output_dir:
                    output_path = Path(output_dir) / f"{input_file.stem}.{target_format}"
                else:
                    output_path = input_file.parent / f"{input_file.stem}.{target_format}"
                
                # Convert
                result = await self.converter.convert(
                    input_path=input_path,
                    target_format=target_format,
                    output_path=str(output_path),
                    quality=quality
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Multi-format conversion failed for {target_format}: {str(e)}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'target_format': target_format
                })
        
        return results


class ConversionManager:
    """High-level conversion management interface."""
    
    def __init__(self, converter: Optional[FormatConverter] = None):
        self.converter = converter or FormatConverter()
        self.conversion_history = []
    
    async def smart_convert(
        self,
        input_path: str,
        use_case: str = "web",
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Smart conversion based on use case and constraints."""
        try:
            # Detect source format
            source_format = self.converter._detect_format(input_path)
            
            # Get optimal format suggestion
            suggestion = self.converter.suggest_optimal_format(
                source_format=source_format,
                use_case=use_case,
                constraints=constraints
            )
            
            # Perform conversion if needed
            if suggestion['recommended_format'] != source_format:
                result = await self.converter.convert(
                    input_path=input_path,
                    target_format=suggestion['recommended_format'],
                    quality=suggestion['recommended_quality']
                )
                
                # Add suggestion info to result
                result['suggestion'] = suggestion
                
                # Record conversion
                self.conversion_history.append(result)
                
                return result
            else:
                return {
                    'success': True,
                    'message': 'No conversion needed',
                    'input_path': input_path,
                    'suggestion': suggestion
                }
                
        except Exception as e:
            logger.error(f"Smart conversion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_path': input_path
            }
    
    def get_conversion_history(self) -> List[Dict[str, Any]]:
        """Get conversion history."""
        return self.conversion_history.copy()
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """
Get conversion statistics."""
        if not self.conversion_history:
            return {'total_conversions': 0}
        
        successful = [c for c in self.conversion_history if c.get('success')]
        failed = [c for c in self.conversion_history if not c.get('success')]
        
        total_time = sum(c.get('processing_time', 0) for c in successful)
        avg_time = total_time / len(successful) if successful else 0
        
        format_counts = {}
        for conversion in successful:
            target_format = conversion.get('target_format')
            if target_format:
                format_counts[target_format] = format_counts.get(target_format, 0) + 1
        
        return {
            'total_conversions': len(self.conversion_history),
            'successful_conversions': len(successful),
            'failed_conversions': len(failed),
            'success_rate': len(successful) / len(self.conversion_history) if self.conversion_history else 0,
            'average_processing_time': avg_time,
            'total_processing_time': total_time,
            'most_popular_formats': sorted(format_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
