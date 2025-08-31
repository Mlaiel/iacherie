"""Multi-Format Handler - IA Influencer Agent Platform
=================================================

Advanced handler for processing and managing multiple content formats (audio, video, image, text)
with format-specific optimization, conversion, and validation capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
import mimetypes
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

import aiofiles
import ffmpeg
import librosa
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
from moviepy.editor import VideoFileClip, AudioFileClip
import soundfile as sf

from ...core.config import get_settings
from ...core.exceptions import FormatHandlingError
from ...core.logging import get_logger
from ...utils.file_handler import FileHandler
from ...utils.validation import validate_content_format

logger = get_logger(__name__)
settings = get_settings()


class MultiFormatHandler:
    """Advanced multi-format content handler with conversion and optimization capabilities."""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.supported_conversions = {
            'audio': {
                'input_formats': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
                'output_formats': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
                'quality_presets': {
                    'high': {'bitrate': '320k', 'sample_rate': 48000},
                    'medium': {'bitrate': '192k', 'sample_rate': 44100},
                    'low': {'bitrate': '128k', 'sample_rate': 44100}
                }
            },
            'video': {
                'input_formats': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'],
                'output_formats': ['.mp4', '.webm', '.mov', '.avi'],
                'quality_presets': {
                    'high': {'resolution': '1920x1080', 'bitrate': '8000k', 'fps': 60},
                    'medium': {'resolution': '1280x720', 'bitrate': '4000k', 'fps': 30},
                    'low': {'resolution': '854x480', 'bitrate': '2000k', 'fps': 30}
                }
            },
            'image': {
                'input_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'],
                'output_formats': ['.jpg', '.png', '.webp', '.bmp'],
                'quality_presets': {
                    'high': {'quality': 95, 'max_dimension': 4096},
                    'medium': {'quality': 85, 'max_dimension': 2048},
                    'low': {'quality': 75, 'max_dimension': 1024}
                }
            },
            'text': {
                'input_formats': ['.txt', '.md', '.doc', '.docx', '.pdf', '.rtf'],
                'output_formats': ['.txt', '.md', '.pdf', '.html'],
                'encoding_options': ['utf-8', 'latin-1', 'cp1252']
            }
        }
        
        # Platform-specific requirements
        self.platform_specs = {
            'youtube': {
                'video': {'max_resolution': '3840x2160', 'max_duration': 43200, 'formats': ['.mp4', '.mov']},
                'audio': {'max_duration': 43200, 'formats': ['.mp3', '.wav'], 'max_bitrate': '320k'}
            },
            'instagram': {
                'video': {'max_resolution': '1920x1080', 'max_duration': 60, 'aspect_ratios': ['1:1', '4:5', '9:16']},
                'image': {'min_resolution': '320x320', 'max_resolution': '1080x1080', 'aspect_ratios': ['1:1', '4:5']},
                'audio': {'max_duration': 60, 'formats': ['.mp3', '.aac']}
            },
            'tiktok': {
                'video': {'resolution': '1080x1920', 'max_duration': 180, 'aspect_ratio': '9:16', 'formats': ['.mp4']},
                'audio': {'max_duration': 180, 'formats': ['.mp3', '.aac']}
            },
            'spotify': {
                'audio': {'formats': ['.mp3', '.flac', '.wav'], 'min_quality': '320k', 'sample_rate': 44100}
            },
            'twitter': {
                'video': {'max_resolution': '1920x1080', 'max_duration': 140, 'max_size': 512000000},
                'image': {'max_dimension': 4096, 'formats': ['.jpg', '.png', '.webp']},
                'audio': {'max_duration': 140, 'formats': ['.mp3', '.aac']}
            }
        }
    
    async def handle_format(
        self,
        file_path: Path,
        content_type: str,
        target_format: Optional[str] = None,
        quality_preset: str = 'medium',
        platform_optimization: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle and process content format with optional conversion and optimization.
        
        Args:
            file_path: Path to the content file
            content_type: Type of content (audio, video, image, text)
            target_format: Target format for conversion
            quality_preset: Quality preset (high, medium, low)
            platform_optimization: Platform to optimize for
            
        Returns:
            Processing results with file info and optimization data
        """
        try:
            # Validate input format
            await self._validate_input_format(file_path, content_type)
            
            # Get format info
            format_info = await self._analyze_format(file_path, content_type)
            
            # Determine if conversion is needed
            conversion_needed = self._needs_conversion(
                file_path, target_format, platform_optimization
            )
            
            result = {
                'original_format': format_info,
                'conversion_performed': conversion_needed,
                'output_files': [],
                'optimizations_applied': [],
                'platform_compliance': {}
            }
            
            if conversion_needed:
                # Perform format conversion
                converted_files = await self._convert_format(
                    file_path, content_type, target_format, quality_preset
                )
                result['output_files'].extend(converted_files)
                result['optimizations_applied'].append('format_conversion')
            
            # Apply platform-specific optimizations
            if platform_optimization:
                optimized_files = await self._optimize_for_platform(
                    file_path, content_type, platform_optimization, quality_preset
                )
                result['output_files'].extend(optimized_files)
                result['optimizations_applied'].append('platform_optimization')
                result['platform_compliance'] = await self._check_platform_compliance(
                    file_path, content_type, platform_optimization
                )
            
            # Generate format variants
            variants = await self._generate_format_variants(
                file_path, content_type, quality_preset
            )
            result['variants'] = variants
            result['optimizations_applied'].append('variant_generation')
            
            logger.info(f"Format handling completed for {file_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Format handling failed: {str(e)}")
            raise FormatHandlingError(f"Failed to handle format: {str(e)}")
    
    async def _validate_input_format(self, file_path: Path, content_type: str) -> None:
        """Validate input file format."""
        if not file_path.exists():
            raise FormatHandlingError("File does not exist")
        
        file_extension = file_path.suffix.lower()
        supported_formats = self.supported_conversions.get(content_type, {}).get('input_formats', [])
        
        if file_extension not in supported_formats:
            raise FormatHandlingError(f"Unsupported input format for {content_type}: {file_extension}")
    
    async def _analyze_format(self, file_path: Path, content_type: str) -> Dict[str, Any]:
        """Analyze content format and extract technical details."""
        format_info = {
            'file_extension': file_path.suffix.lower(),
            'file_size': file_path.stat().st_size,
            'mime_type': mimetypes.guess_type(str(file_path))[0]
        }
        
        if content_type == 'audio':
            format_info.update(await self._analyze_audio_format(file_path))
        elif content_type == 'video':
            format_info.update(await self._analyze_video_format(file_path))
        elif content_type == 'image':
            format_info.update(await self._analyze_image_format(file_path))
        elif content_type == 'text':
            format_info.update(await self._analyze_text_format(file_path))
        
        return format_info
    
    async def _analyze_audio_format(self, file_path: Path) -> Dict[str, Any]:
        """Analyze audio format details."""
        try:
            # Load audio info using librosa
            y, sr = librosa.load(str(file_path), sr=None)
            duration = len(y) / sr
            
            # Get additional format info using soundfile
            info = sf.info(str(file_path))
            
            return {
                'duration': float(duration),
                'sample_rate': int(sr),
                'channels': info.channels,
                'bit_depth': info.subtype_info,
                'format_name': info.format_info,
                'frame_count': info.frames,
                'codec': self._detect_audio_codec(file_path)
            }
        except Exception as e:
            logger.warning(f"Could not analyze audio format: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_video_format(self, file_path: Path) -> Dict[str, Any]:
        """Analyze video format details."""
        try:
            # Use ffprobe to get detailed video info
            probe = ffmpeg.probe(str(file_path))
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            format_info = probe.get('format', {})
            
            result = {
                'duration': float(format_info.get('duration', 0)),
                'video_codec': video_info.get('codec_name', 'unknown'),
                'resolution': f"{video_info.get('width', 0)}x{video_info.get('height', 0)}",
                'fps': eval(video_info.get('r_frame_rate', '0/1')),
                'aspect_ratio': float(video_info.get('width', 1)) / float(video_info.get('height', 1)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'container': format_info.get('format_name', 'unknown')
            }
            
            if audio_info:
                result['audio_codec'] = audio_info.get('codec_name', 'none')
                result['audio_sample_rate'] = int(audio_info.get('sample_rate', 0))
                result['audio_channels'] = int(audio_info.get('channels', 0))
            
            return result
        except Exception as e:
            logger.warning(f"Could not analyze video format: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_image_format(self, file_path: Path) -> Dict[str, Any]:
        """Analyze image format details."""
        try:
            with Image.open(file_path) as img:
                return {
                    'dimensions': f"{img.width}x{img.height}",
                    'color_mode': img.mode,
                    'format': img.format,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'dpi': img.info.get('dpi', (72, 72)),
                    'compression': getattr(img, 'compression', 'none'),
                    'color_profile': img.info.get('icc_profile') is not None
                }
        except Exception as e:
            logger.warning(f"Could not analyze image format: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_text_format(self, file_path: Path) -> Dict[str, Any]:
        """Analyze text format details."""
        try:
            # Try different encodings
            encoding = 'utf-8'
            content = ''
            
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    async with aiofiles.open(file_path, 'r', encoding=enc) as f:
                        content = await f.read()
                    encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
            
            return {
                'encoding': encoding,
                'character_count': len(content),
                'line_count': len(content.split('\n')),
                'word_count': len(content.split()),
                'language': self._detect_text_language(content),
                'has_special_chars': any(ord(char) > 127 for char in content)
            }
        except Exception as e:
            logger.warning(f"Could not analyze text format: {str(e)}")
            return {'error': str(e)}
    
    def _detect_audio_codec(self, file_path: Path) -> str:
        """Detect audio codec from file extension and content."""
        extension = file_path.suffix.lower()
        codec_map = {
            '.mp3': 'mp3',
            '.wav': 'pcm',
            '.flac': 'flac',
            '.aac': 'aac',
            '.ogg': 'vorbis',
            '.m4a': 'aac'
        }
        return codec_map.get(extension, 'unknown')
    
    def _detect_text_language(self, content: str) -> str:
        """Simple language detection for text content."""
        # Simplified detection based on common words
        common_words = {
            'english': ['the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that'],
            'french': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'en', 'avoir', 'que'],
            'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
            'spanish': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se']
        }
        
        words = content.lower().split()[:100]  # Check first 100 words
        if not words:
            return 'unknown'
        
        scores = {}
        for lang, common in common_words.items():
            score = sum(1 for word in words if word in common)
            scores[lang] = score
        
        return max(scores, key=scores.get) if scores else 'unknown'
    
    def _needs_conversion(
        self,
        file_path: Path,
        target_format: Optional[str],
        platform_optimization: Optional[str]
    ) -> bool:
        """Determine if format conversion is needed."""
        if target_format and file_path.suffix.lower() != target_format.lower():
            return True
        
        if platform_optimization:
            # Check if current format is supported by target platform
            current_format = file_path.suffix.lower()
            content_type = self._get_content_type_from_extension(current_format)
            
            platform_specs = self.platform_specs.get(platform_optimization, {})
            supported_formats = platform_specs.get(content_type, {}).get('formats', [])
            
            if supported_formats and current_format not in supported_formats:
                return True
        
        return False
    
    def _get_content_type_from_extension(self, extension: str) -> str:
        """Get content type from file extension."""
        for content_type, config in self.supported_conversions.items():
            if extension in config['input_formats']:
                return content_type
        return 'unknown'
    
    async def _convert_format(
        self,
        file_path: Path,
        content_type: str,
        target_format: str,
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Convert content to target format."""
        converted_files = []
        
        if content_type == 'audio':
            converted_files = await self._convert_audio(file_path, target_format, quality_preset)
        elif content_type == 'video':
            converted_files = await self._convert_video(file_path, target_format, quality_preset)
        elif content_type == 'image':
            converted_files = await self._convert_image(file_path, target_format, quality_preset)
        elif content_type == 'text':
            converted_files = await self._convert_text(file_path, target_format)
        
        return converted_files
    
    async def _convert_audio(
        self,
        file_path: Path,
        target_format: str,
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Convert audio to target format."""
        try:
            quality_settings = self.supported_conversions['audio']['quality_presets'][quality_preset]
            output_path = file_path.with_suffix(target_format)
            
            # Load audio
            y, sr = librosa.load(str(file_path), sr=quality_settings['sample_rate'])
            
            # Save in target format
            if target_format == '.mp3':
                # Use ffmpeg for MP3 encoding
                (
                    ffmpeg
                    .input(str(file_path))
                    .output(
                        str(output_path),
                        acodec='mp3',
                        audio_bitrate=quality_settings['bitrate'],
                        ar=quality_settings['sample_rate']
                    )
                    .overwrite_output()
                    .run()
                )
            else:
                # Use soundfile for other formats
                sf.write(str(output_path), y, quality_settings['sample_rate'])
            
            return [{
                'file_path': str(output_path),
                'format': target_format,
                'quality': quality_preset,
                'size': output_path.stat().st_size,
                'conversion_settings': quality_settings
            }]
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            raise FormatHandlingError(f"Audio conversion error: {str(e)}")
    
    async def _convert_video(
        self,
        file_path: Path,
        target_format: str,
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Convert video to target format."""
        try:
            quality_settings = self.supported_conversions['video']['quality_presets'][quality_preset]
            output_path = file_path.with_suffix(target_format)
            
            # Use ffmpeg for video conversion
            stream = ffmpeg.input(str(file_path))
            
            # Apply quality settings
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec='libx264' if target_format == '.mp4' else 'libvpx-vp9',
                video_bitrate=quality_settings['bitrate'],
                s=quality_settings['resolution'],
                r=quality_settings['fps'],
                acodec='aac' if target_format == '.mp4' else 'libvorbis'
            )
            
            ffmpeg.run(stream, overwrite_output=True)
            
            return [{
                'file_path': str(output_path),
                'format': target_format,
                'quality': quality_preset,
                'size': output_path.stat().st_size,
                'conversion_settings': quality_settings
            }]
            
        except Exception as e:
            logger.error(f"Video conversion failed: {str(e)}")
            raise FormatHandlingError(f"Video conversion error: {str(e)}")
    
    async def _convert_image(
        self,
        file_path: Path,
        target_format: str,
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Convert image to target format."""
        try:
            quality_settings = self.supported_conversions['image']['quality_presets'][quality_preset]
            output_path = file_path.with_suffix(target_format)
            
            with Image.open(file_path) as img:
                # Resize if needed
                max_dimension = quality_settings['max_dimension']
                if max(img.width, img.height) > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # Convert color mode if needed
                if target_format.lower() in ['.jpg', '.jpeg'] and img.mode in ['RGBA', 'LA']:
                    # Convert to RGB for JPEG
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img)
                    img = background
                
                # Save with quality settings
                save_kwargs = {}
                if target_format.lower() in ['.jpg', '.jpeg']:
                    save_kwargs['quality'] = quality_settings['quality']
                    save_kwargs['optimize'] = True
                elif target_format.lower() == '.webp':
                    save_kwargs['quality'] = quality_settings['quality']
                    save_kwargs['method'] = 6  # Best compression
                
                img.save(output_path, **save_kwargs)
            
            return [{
                'file_path': str(output_path),
                'format': target_format,
                'quality': quality_preset,
                'size': output_path.stat().st_size,
                'conversion_settings': quality_settings
            }]
            
        except Exception as e:
            logger.error(f"Image conversion failed: {str(e)}")
            raise FormatHandlingError(f"Image conversion error: {str(e)}")
    
    async def _convert_text(
        self,
        file_path: Path,
        target_format: str
    ) -> List[Dict[str, Any]]:
        """Convert text to target format."""
        try:
            output_path = file_path.with_suffix(target_format)
            
            # Read original content
            content = ''
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                        content = await f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            # Convert based on target format
            if target_format == '.md':
                # Convert to Markdown
                if file_path.suffix.lower() == '.txt':
                    # Simple text to markdown conversion
                    lines = content.split('\n')
                    markdown_content = '\n'.join(f"# {line}" if line and not line.startswith(' ') else line for line in lines)
                    content = markdown_content
                    
            elif target_format == '.html':
                # Convert to HTML
                content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{file_path.stem}</title>
    <meta charset="utf-8">
</head>
<body>
    <pre>{content}</pre>
</body>
</html>"""
            
            # Save converted content
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return [{
                'file_path': str(output_path),
                'format': target_format,
                'size': output_path.stat().st_size,
                'encoding': 'utf-8'
            }]
            
        except Exception as e:
            logger.error(f"Text conversion failed: {str(e)}")
            raise FormatHandlingError(f"Text conversion error: {str(e)}")
    
    async def _optimize_for_platform(
        self,
        file_path: Path,
        content_type: str,
        platform: str,
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Optimize content for specific platform requirements."""
        platform_specs = self.platform_specs.get(platform, {}).get(content_type, {})
        if not platform_specs:
            return []
        
        optimized_files = []
        
        if content_type == 'video':
            optimized_files = await self._optimize_video_for_platform(
                file_path, platform, platform_specs, quality_preset
            )
        elif content_type == 'audio':
            optimized_files = await self._optimize_audio_for_platform(
                file_path, platform, platform_specs, quality_preset
            )
        elif content_type == 'image':
            optimized_files = await self._optimize_image_for_platform(
                file_path, platform, platform_specs, quality_preset
            )
        
        return optimized_files
    
    async def _optimize_video_for_platform(
        self,
        file_path: Path,
        platform: str,
        specs: Dict[str, Any],
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Optimize video for platform-specific requirements."""
        optimized_files = []
        
        # Get current video info
        probe = ffmpeg.probe(str(file_path))
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        
        current_width = int(video_info.get('width', 0))
        current_height = int(video_info.get('height', 0))
        current_duration = float(probe['format'].get('duration', 0))
        
        # Check if optimization needed
        max_resolution = specs.get('max_resolution', '1920x1080')
        max_width, max_height = map(int, max_resolution.split('x'))
        max_duration = specs.get('max_duration', current_duration)
        
        if current_width > max_width or current_height > max_height or current_duration > max_duration:
            output_path = file_path.with_name(f"{file_path.stem}_{platform}_optimized{file_path.suffix}")
            
            # Calculate new dimensions maintaining aspect ratio
            aspect_ratio = current_width / current_height
            if current_width > max_width:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            elif current_height > max_height:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            else:
                new_width, new_height = current_width, current_height
            
            # Ensure dimensions are even (required for some codecs)
            new_width = new_width if new_width % 2 == 0 else new_width - 1
            new_height = new_height if new_height % 2 == 0 else new_height - 1
            
            # Build ffmpeg command
            input_stream = ffmpeg.input(str(file_path))
            
            # Trim duration if needed
            if current_duration > max_duration:
                input_stream = ffmpeg.input(str(file_path), t=max_duration)
            
            # Apply video processing
            output_stream = ffmpeg.output(
                input_stream,
                str(output_path),
                vcodec='libx264',
                s=f'{new_width}x{new_height}',
                preset='medium',
                crf=23,  # Good quality
                acodec='aac',
                audio_bitrate='128k'
            )
            
            ffmpeg.run(output_stream, overwrite_output=True)
            
            optimized_files.append({
                'file_path': str(output_path),
                'platform': platform,
                'optimization_type': 'platform_compliance',
                'original_resolution': f'{current_width}x{current_height}',
                'new_resolution': f'{new_width}x{new_height}',
                'original_duration': current_duration,
                'new_duration': min(current_duration, max_duration),
                'size': output_path.stat().st_size
            })
        
        # Generate aspect ratio variants if specified
        aspect_ratios = specs.get('aspect_ratios', [])
        for aspect_ratio in aspect_ratios:
            if ':' in aspect_ratio:
                width_ratio, height_ratio = map(int, aspect_ratio.split(':'))
                variant_file = await self._create_aspect_ratio_variant(
                    file_path, platform, width_ratio, height_ratio, quality_preset
                )
                if variant_file:
                    optimized_files.append(variant_file)
        
        return optimized_files
    
    async def _optimize_audio_for_platform(
        self,
        file_path: Path,
        platform: str,
        specs: Dict[str, Any],
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Optimize audio for platform-specific requirements."""
        optimized_files = []
        
        # Get current audio info
        info = sf.info(str(file_path))
        current_duration = info.duration
        max_duration = specs.get('max_duration', current_duration)
        
        if current_duration > max_duration:
            output_path = file_path.with_name(f"{file_path.stem}_{platform}_optimized{file_path.suffix}")
            
            # Trim audio to max duration
            y, sr = librosa.load(str(file_path), duration=max_duration)
            sf.write(str(output_path), y, sr)
            
            optimized_files.append({
                'file_path': str(output_path),
                'platform': platform,
                'optimization_type': 'duration_trim',
                'original_duration': current_duration,
                'new_duration': max_duration,
                'size': output_path.stat().st_size
            })
        
        return optimized_files
    
    async def _optimize_image_for_platform(
        self,
        file_path: Path,
        platform: str,
        specs: Dict[str, Any],
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Optimize image for platform-specific requirements."""
        optimized_files = []
        
        with Image.open(file_path) as img:
            current_width, current_height = img.size
            max_dimension = specs.get('max_dimension', max(current_width, current_height))
            
            # Resize if needed
            if max(current_width, current_height) > max_dimension:
                output_path = file_path.with_name(f"{file_path.stem}_{platform}_optimized{file_path.suffix}")
                
                # Calculate new dimensions
                if current_width > current_height:
                    new_width = max_dimension
                    new_height = int(current_height * max_dimension / current_width)
                else:
                    new_height = max_dimension
                    new_width = int(current_width * max_dimension / current_height)
                
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_img.save(output_path, quality=85, optimize=True)
                
                optimized_files.append({
                    'file_path': str(output_path),
                    'platform': platform,
                    'optimization_type': 'dimension_resize',
                    'original_dimensions': f'{current_width}x{current_height}',
                    'new_dimensions': f'{new_width}x{new_height}',
                    'size': output_path.stat().st_size
                })
            
            # Generate aspect ratio variants
            aspect_ratios = specs.get('aspect_ratios', [])
            for aspect_ratio in aspect_ratios:
                if ':' in aspect_ratio:
                    width_ratio, height_ratio = map(int, aspect_ratio.split(':'))
                    variant_file = await self._create_image_aspect_ratio_variant(
                        file_path, platform, width_ratio, height_ratio
                    )
                    if variant_file:
                        optimized_files.append(variant_file)
        
        return optimized_files
    
    async def _create_aspect_ratio_variant(
        self,
        file_path: Path,
        platform: str,
        width_ratio: int,
        height_ratio: int,
        quality_preset: str
    ) -> Optional[Dict[str, Any]]:
        """Create video variant with specific aspect ratio."""
        try:
            aspect_ratio_str = f"{width_ratio}_{height_ratio}"
            output_path = file_path.with_name(f"{file_path.stem}_{platform}_{aspect_ratio_str}{file_path.suffix}")
            
            # Get current video dimensions
            probe = ffmpeg.probe(str(file_path))
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            current_width = int(video_info.get('width', 0))
            current_height = int(video_info.get('height', 0))
            
            # Calculate new dimensions based on aspect ratio
            target_aspect = width_ratio / height_ratio
            current_aspect = current_width / current_height
            
            if current_aspect > target_aspect:
                # Crop width
                new_height = current_height
                new_width = int(current_height * target_aspect)
                x_offset = (current_width - new_width) // 2
                y_offset = 0
            else:
                # Crop height
                new_width = current_width
                new_height = int(current_width / target_aspect)
                x_offset = 0
                y_offset = (current_height - new_height) // 2
            
            # Ensure dimensions are even
            new_width = new_width if new_width % 2 == 0 else new_width - 1
            new_height = new_height if new_height % 2 == 0 else new_height - 1
            
            # Apply crop and resize
            (
                ffmpeg
                .input(str(file_path))
                .filter('crop', new_width, new_height, x_offset, y_offset)
                .output(str(output_path), vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run()
            )
            
            return {
                'file_path': str(output_path),
                'platform': platform,
                'optimization_type': 'aspect_ratio_variant',
                'aspect_ratio': f'{width_ratio}:{height_ratio}',
                'dimensions': f'{new_width}x{new_height}',
                'size': output_path.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"Failed to create aspect ratio variant: {str(e)}")
            return None
    
    async def _create_image_aspect_ratio_variant(
        self,
        file_path: Path,
        platform: str,
        width_ratio: int,
        height_ratio: int
    ) -> Optional[Dict[str, Any]]:
        """Create image variant with specific aspect ratio."""
        try:
            aspect_ratio_str = f"{width_ratio}_{height_ratio}"
            output_path = file_path.with_name(f"{file_path.stem}_{platform}_{aspect_ratio_str}{file_path.suffix}")
            
            with Image.open(file_path) as img:
                current_width, current_height = img.size
                target_aspect = width_ratio / height_ratio
                current_aspect = current_width / current_height
                
                if current_aspect > target_aspect:
                    # Crop width
                    new_width = int(current_height * target_aspect)
                    new_height = current_height
                    left = (current_width - new_width) // 2
                    top = 0
                    right = left + new_width
                    bottom = current_height
                else:
                    # Crop height
                    new_width = current_width
                    new_height = int(current_width / target_aspect)
                    left = 0
                    top = (current_height - new_height) // 2
                    right = current_width
                    bottom = top + new_height
                
                cropped_img = img.crop((left, top, right, bottom))
                cropped_img.save(output_path, quality=85, optimize=True)
                
                return {
                    'file_path': str(output_path),
                    'platform': platform,
                    'optimization_type': 'aspect_ratio_variant',
                    'aspect_ratio': f'{width_ratio}:{height_ratio}',
                    'dimensions': f'{new_width}x{new_height}',
                    'size': output_path.stat().st_size
                }
                
        except Exception as e:
            logger.error(f"Failed to create image aspect ratio variant: {str(e)}")
            return None
    
    async def _generate_format_variants(
        self,
        file_path: Path,
        content_type: str,
        quality_preset: str
    ) -> List[Dict[str, Any]]:
        """Generate multiple format variants for different use cases."""
        variants = []
        
        if content_type == 'audio':
            # Generate common audio variants
            for format_ext in ['.mp3', '.wav', '.aac']:
                if file_path.suffix.lower() != format_ext:
                    try:
                        variant_files = await self._convert_audio(file_path, format_ext, quality_preset)
                        variants.extend(variant_files)
                    except Exception as e:
                        logger.warning(f"Failed to create {format_ext} variant: {str(e)}")
        
        elif content_type == 'image':
            # Generate web-optimized variants
            for format_ext in ['.jpg', '.webp']:
                if file_path.suffix.lower() != format_ext:
                    try:
                        variant_files = await self._convert_image(file_path, format_ext, quality_preset)
                        variants.extend(variant_files)
                    except Exception as e:
                        logger.warning(f"Failed to create {format_ext} variant: {str(e)}")
        
        return variants
    
    async def _check_platform_compliance(
        self,
        file_path: Path,
        content_type: str,
        platform: str
    ) -> Dict[str, Any]:
        """Check if content meets platform requirements."""
        compliance = {
            'compliant': True,
            'issues': [],
            'recommendations': []
        }
        
        platform_specs = self.platform_specs.get(platform, {}).get(content_type, {})
        if not platform_specs:
            return compliance
        
        format_info = await self._analyze_format(file_path, content_type)
        
        # Check format compliance
        supported_formats = platform_specs.get('formats', [])
        if supported_formats and file_path.suffix.lower() not in supported_formats:
            compliance['compliant'] = False
            compliance['issues'].append(f"Format {file_path.suffix} not supported")
            compliance['recommendations'].append(f"Convert to one of: {', '.join(supported_formats)}")
        
        # Check size limits
        max_size = platform_specs.get('max_size')
        if max_size and format_info['file_size'] > max_size:
            compliance['compliant'] = False
            compliance['issues'].append("File size exceeds platform limit")
            compliance['recommendations'].append("Reduce file size through compression")
        
        # Content-specific checks
        if content_type == 'video':
            # Check duration
            max_duration = platform_specs.get('max_duration')
            duration = format_info.get('duration', 0)
            if max_duration and duration > max_duration:
                compliance['compliant'] = False
                compliance['issues'].append(f"Duration {duration}s exceeds limit of {max_duration}s")
                compliance['recommendations'].append("Trim video to fit platform requirements")
            
            # Check resolution
            max_resolution = platform_specs.get('max_resolution')
            if max_resolution:
                max_width, max_height = map(int, max_resolution.split('x'))
                current_resolution = format_info.get('resolution', '0x0')
                current_width, current_height = map(int, current_resolution.split('x'))
                
                if current_width > max_width or current_height > max_height:
                    compliance['compliant'] = False
                    compliance['issues'].append("Resolution exceeds platform limit")
                    compliance['recommendations'].append(f"Resize to max {max_resolution}")
        
        elif content_type == 'audio':
            # Check audio duration
            max_duration = platform_specs.get('max_duration')
            duration = format_info.get('duration', 0)
            if max_duration and duration > max_duration:
                compliance['compliant'] = False
                compliance['issues'].append(f"Duration {duration}s exceeds limit of {max_duration}s")
                compliance['recommendations'].append("Trim audio to fit platform requirements")
        
        elif content_type == 'image':
            # Check image dimensions
            max_dimension = platform_specs.get('max_dimension')
            if max_dimension:
                dimensions = format_info.get('dimensions', '0x0')
                width, height = map(int, dimensions.split('x'))
                
                if max(width, height) > max_dimension:
                    compliance['compliant'] = False
                    compliance['issues'].append("Image dimensions exceed platform limit")
                    compliance['recommendations'].append(f"Resize to max dimension {max_dimension}px")
        
        return compliance
    
    async def get_supported_formats(self, content_type: str) -> Dict[str, List[str]]:
        """Get supported input and output formats for content type."""
        return self.supported_conversions.get(content_type, {
            'input_formats': [],
            'output_formats': []
        })
    
    async def get_platform_requirements(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific requirements."""
        return self.platform_specs.get(platform, {})
    
    async def batch_convert(
        self,
        file_paths: List[Path],
        content_type: str,
        target_format: str,
        quality_preset: str = 'medium'
    ) -> List[Dict[str, Any]]:
        """Convert multiple files in batch."""
        results = []
        
        # Process files concurrently with limit
        semaphore = asyncio.Semaphore(3)  # Limit concurrent conversions
        
        async def convert_single(file_path: Path) -> Dict[str, Any]:
            async with semaphore:
                try:
                    result = await self.handle_format(
                        file_path, content_type, target_format, quality_preset
                    )
                    return {
                        'input_file': str(file_path),
                        'success': True,
                        'result': result
                    }
                except Exception as e:
                    return {
                        'input_file': str(file_path),
                        'success': False,
                        'error': str(e)
                    }
        
        tasks = [convert_single(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks)
        
        return results
