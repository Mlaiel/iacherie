"""
Multimedia Converter for IA Influencer Agent Platform
Advanced multimedia format conversion, optimization, and processing

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import ffmpeg
from PIL import Image, ImageOps, ImageEnhance
import librosa
import soundfile as sf
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging
import asyncio
import subprocess
import tempfile
import shutil
import mimetypes
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import time
from datetime import datetime
import json
import os
import io
import base64

logger = logging.getLogger(__name__)


@dataclass
class ConversionParams:
    """Conversion parameters configuration"""
    format: str
    quality: Optional[Union[int, str]] = None
    resolution: Optional[Tuple[int, int]] = None
    bitrate: Optional[str] = None
    frame_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    preset: Optional[str] = None
    custom_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionResult:
    """Conversion operation result"""
    success: bool
    input_file: str
    output_file: Optional[str] = None
    original_size: int = 0
    converted_size: int = 0
    compression_ratio: float = 0.0
    processing_time: float = 0.0
    format_info: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""



        return {
            'success': self.success,
            'input_file': self.input_file,
            'output_file': self.output_file,
            'original_size': self.original_size,
            'converted_size': self.converted_size,
            'compression_ratio': self.compression_ratio,
            'processing_time': self.processing_time,
            'format_info': self.format_info,
            'error': self.error,
            'warnings': self.warnings
        }


@dataclass
class MediaInfo:
    """Media file information"""
    file_path: str
    media_type: str  # audio, video, image
    format: str
    duration: Optional[float] = None
    size: int = 0
    resolution: Optional[Tuple[int, int]] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AudioConverter:
    """Advanced audio format conversion and processing"""
    
    def __init__(self, quality_preset: str = "high"):
        self.quality_preset = quality_preset
        self.supported_formats = {
            'mp3': {'codec': 'libmp3lame', 'ext': '.mp3'},
            'wav': {'codec': 'pcm_s16le', 'ext': '.wav'},
            'flac': {'codec': 'flac', 'ext': '.flac'},
            'aac': {'codec': 'aac', 'ext': '.aac'},
            'ogg': {'codec': 'libvorbis', 'ext': '.ogg'},
            'm4a': {'codec': 'aac', 'ext': '.m4a'},
            'wma': {'codec': 'wmav2', 'ext': '.wma'},
            'aiff': {'codec': 'pcm_s16be', 'ext': '.aiff'},
            'opus': {'codec': 'libopus', 'ext': '.opus'}
        }
        
        self.quality_settings = {
            'low': {'bitrate': '96k', 'sample_rate': 22050},
            'medium': {'bitrate': '128k', 'sample_rate': 44100},
            'high': {'bitrate': '192k', 'sample_rate': 44100},
            'ultra': {'bitrate': '320k', 'sample_rate': 48000},
            'lossless': {'bitrate': None, 'sample_rate': 48000}
        }
    
    async def convert_audio(self, input_file: str, output_file: str,
                          params: ConversionParams) -> ConversionResult:
        """Convert audio file with specified parameters"""
        start_time = time.time()
        result = ConversionResult(
            success=False,
            input_file=input_file,
            output_file=output_file
        )
        
        try:
            # Get input file info
            input_path = Path(input_file)
            if not input_path.exists():
                result.error = f"Input file not found: {input_file}"
                return result
            
            result.original_size = input_path.stat().st_size
            
            # Get format settings
            format_info = self.supported_formats.get(params.format.lower())
            if not format_info:
                result.error = f"Unsupported audio format: {params.format}"
                return result
            
            # Build ffmpeg command
            input_stream = ffmpeg.input(input_file)
            
            # Apply audio processing options
            audio_options = self._build_audio_options(params)
            
            output_stream = ffmpeg.output(
                input_stream,
                output_file,
                acodec=format_info['codec'],
                **audio_options
            )
            
            # Execute conversion
            await self._execute_ffmpeg(output_stream)
            
            # Verify output file
            output_path = Path(output_file)
            if output_path.exists():
                result.success = True
                result.converted_size = output_path.stat().st_size
                result.compression_ratio = result.converted_size / result.original_size
                result.format_info = await self._get_audio_info(output_file)
            else:
                result.error = "Conversion failed - output file not created"
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            result.error = str(e)
        finally:
            result.processing_time = time.time() - start_time
        
        return result
    
    def _build_audio_options(self, params: ConversionParams) -> Dict[str, Any]:
        """Build ffmpeg audio options"""
        options = {}
        
        # Quality settings
        quality_settings = self.quality_settings.get(self.quality_preset, 
                                                    self.quality_settings['high'])
        
        # Bitrate
        if params.bitrate:
            options['audio_bitrate'] = params.bitrate
        elif quality_settings['bitrate']:
            options['audio_bitrate'] = quality_settings['bitrate']
        
        # Sample rate
        if params.sample_rate:
            options['ar'] = params.sample_rate
        elif quality_settings['sample_rate']:
            options['ar'] = quality_settings['sample_rate']
        
        # Channels
        if params.channels:
            options['ac'] = params.channels
        
        # Custom options
        options.update(params.custom_options)
        
        return options
    
    async def _execute_ffmpeg(self, stream) -> None:
        """Execute ffmpeg command asynchronously"""
        def run_ffmpeg():
            try:
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
            except ffmpeg.Error as e:
                logger.error(f"ffmpeg error: {e.stderr}")
                raise
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, run_ffmpeg)
    
    async def _get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """Get audio file information"""



        try:
            probe = ffmpeg.probe(file_path)
            
            audio_stream = None
            for stream in probe['streams']:
                if stream['codec_type'] == 'audio':
                    audio_stream = stream
                    break
            
            if audio_stream:
                return {
                    'codec': audio_stream.get('codec_name'),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'channels': audio_stream.get('channels', 0),
                    'duration': float(audio_stream.get('duration', 0)),
                    'bit_rate': int(audio_stream.get('bit_rate', 0))
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get audio info: {str(e)}")
            return {}
    
    async def batch_convert_audio(self, files: List[str], 
                                output_dir: str,
                                params: ConversionParams,
                                max_concurrent: int = 4) -> List[ConversionResult]:
        """Convert multiple audio files concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def convert_single_file(input_file: str) -> ConversionResult:
            async with semaphore:
                input_path = Path(input_file)
                output_file = os.path.join(
                    output_dir,
                    f"{input_path.stem}.{params.format}"
                )
                return await self.convert_audio(input_file, output_file, params)
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        tasks = [convert_single_file(file) for file in files]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def optimize_for_streaming(self, input_file: str, 
                                   output_file: str) -> ConversionResult:
        """Optimize audio for streaming"""
        params = ConversionParams(
            format='aac',
            bitrate='128k',
            sample_rate=44100,
            channels=2,
            custom_options={
                'movflags': '+faststart',
                'profile:a': 'aac_low'
            }
        )
        
        return await self.convert_audio(input_file, output_file, params)


class VideoConverter:
    """Advanced video format conversion and processing"""
    
    def __init__(self, hardware_acceleration: bool = True):
        self.hardware_acceleration = hardware_acceleration
        self.supported_formats = {
            'mp4': {'codec': 'libx264', 'ext': '.mp4'},
            'avi': {'codec': 'libx264', 'ext': '.avi'},
            'mov': {'codec': 'libx264', 'ext': '.mov'},
            'mkv': {'codec': 'libx264', 'ext': '.mkv'},
            'webm': {'codec': 'libvpx-vp9', 'ext': '.webm'},
            'flv': {'codec': 'libx264', 'ext': '.flv'},
            'wmv': {'codec': 'wmv2', 'ext': '.wmv'},
            '3gp': {'codec': 'libx264', 'ext': '.3gp'},
            'ogv': {'codec': 'libtheora', 'ext': '.ogv'}
        }
        
        self.quality_presets = {
            'ultrafast': 'ultrafast',
            'superfast': 'superfast',
            'veryfast': 'veryfast',
            'faster': 'faster',
            'fast': 'fast',
            'medium': 'medium',
            'slow': 'slow',
            'slower': 'slower',
            'veryslow': 'veryslow'
        }
        
        self.resolution_presets = {
            '4k': (3840, 2160),
            '1080p': (1920, 1080),
            '720p': (1280, 720),
            '480p': (854, 480),
            '360p': (640, 360),
            '240p': (426, 240)
        }
    
    async def convert_video(self, input_file: str, output_file: str,
                          params: ConversionParams) -> ConversionResult:
        """Convert video file with specified parameters"""
        start_time = time.time()
        result = ConversionResult(
            success=False,
            input_file=input_file,
            output_file=output_file
        )
        
        try:
            # Get input file info
            input_path = Path(input_file)
            if not input_path.exists():
                result.error = f"Input file not found: {input_file}"
                return result
            
            result.original_size = input_path.stat().st_size
            
            # Get format settings
            format_info = self.supported_formats.get(params.format.lower())
            if not format_info:
                result.error = f"Unsupported video format: {params.format}"
                return result
            
            # Build ffmpeg command
            input_stream = ffmpeg.input(input_file)
            
            # Apply video processing options
            video_options = self._build_video_options(params)
            
            output_stream = ffmpeg.output(
                input_stream,
                output_file,
                vcodec=format_info['codec'],
                **video_options
            )
            
            # Execute conversion
            await self._execute_ffmpeg(output_stream)
            
            # Verify output file
            output_path = Path(output_file)
            if output_path.exists():
                result.success = True
                result.converted_size = output_path.stat().st_size
                result.compression_ratio = result.converted_size / result.original_size
                result.format_info = await self._get_video_info(output_file)
            else:
                result.error = "Conversion failed - output file not created"
            
        except Exception as e:
            logger.error(f"Video conversion failed: {str(e)}")
            result.error = str(e)
        finally:
            result.processing_time = time.time() - start_time
        
        return result
    
    def _build_video_options(self, params: ConversionParams) -> Dict[str, Any]:
        """Build ffmpeg video options"""
        options = {}
        
        # Resolution
        if params.resolution:
            options['s'] = f"{params.resolution[0]}x{params.resolution[1]}"
        
        # Frame rate
        if params.frame_rate:
            options['r'] = params.frame_rate
        
        # Bitrate
        if params.bitrate:
            options['video_bitrate'] = params.bitrate
        
        # Preset (encoding speed vs compression)
        if params.preset and params.preset in self.quality_presets:
            options['preset'] = params.preset
        else:
            options['preset'] = 'medium'
        
        # Hardware acceleration
        if self.hardware_acceleration:
            options['hwaccel'] = 'auto'
        
        # Custom options
        options.update(params.custom_options)
        
        return options
    
    async def _execute_ffmpeg(self, stream) -> None:
        """Execute ffmpeg command asynchronously"""
        def run_ffmpeg():
            try:
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
            except ffmpeg.Error as e:
                logger.error(f"ffmpeg error: {e.stderr}")
                raise
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, run_ffmpeg)
    
    async def _get_video_info(self, file_path: str) -> Dict[str, Any]:
        """Get video file information"""



        try:
            probe = ffmpeg.probe(file_path)
            
            video_stream = None
            audio_stream = None
            
            for stream in probe['streams']:
                if stream['codec_type'] == 'video' and not video_stream:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and not audio_stream:
                    audio_stream = stream
            
            info = {}
            
            if video_stream:
                info.update({
                    'video_codec': video_stream.get('codec_name'),
                    'width': video_stream.get('width', 0),
                    'height': video_stream.get('height', 0),
                    'frame_rate': eval(video_stream.get('r_frame_rate', '0/1')),
                    'duration': float(video_stream.get('duration', 0)),
                    'bit_rate': int(video_stream.get('bit_rate', 0))
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream.get('codec_name'),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'channels': audio_stream.get('channels', 0)
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            return {}
    
    async def create_thumbnail(self, video_file: str, thumbnail_file: str,
                             timestamp: float = 1.0, size: Tuple[int, int] = (320, 240)) -> bool:
        """Create video thumbnail"""



        try:
            input_stream = ffmpeg.input(video_file, ss=timestamp)
            output_stream = ffmpeg.output(
                input_stream,
                thumbnail_file,
                vframes=1,
                s=f"{size[0]}x{size[1]}",
                format='image2'
            )
            
            await self._execute_ffmpeg(output_stream)
            return Path(thumbnail_file).exists()
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {str(e)}")
            return False
    
    async def extract_audio(self, video_file: str, audio_file: str,
                          format: str = 'mp3') -> ConversionResult:
        """Extract audio track from video"""
        start_time = time.time()
        result = ConversionResult(
            success=False,
            input_file=video_file,
            output_file=audio_file
        )
        
        try:
            input_stream = ffmpeg.input(video_file)
            output_stream = ffmpeg.output(
                input_stream,
                audio_file,
                acodec='libmp3lame' if format == 'mp3' else 'copy',
                vn=None  # No video
            )
            
            await self._execute_ffmpeg(output_stream)
            
            output_path = Path(audio_file)
            if output_path.exists():
                result.success = True
                result.converted_size = output_path.stat().st_size
                result.processing_time = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Audio extraction failed: {str(e)}")
            result.error = str(e)
        
        return result


class ImageConverter:
    """Advanced image format conversion and processing"""
    
    def __init__(self):
        self.supported_formats = {
            'jpeg': 'JPEG',
            'jpg': 'JPEG',
            'png': 'PNG',
            'gif': 'GIF',
            'bmp': 'BMP',
            'tiff': 'TIFF',
            'webp': 'WEBP',
            'ico': 'ICO',
            'tga': 'TGA',
            'svg': 'SVG'
        }
        
        self.quality_settings = {
            'low': 60,
            'medium': 80,
            'high': 90,
            'ultra': 95
        }
    
    async def convert_image(self, input_file: str, output_file: str,
                          params: ConversionParams) -> ConversionResult:
        """Convert image file with specified parameters"""
        start_time = time.time()
        result = ConversionResult(
            success=False,
            input_file=input_file,
            output_file=output_file
        )
        
        try:
            # Get input file info
            input_path = Path(input_file)
            if not input_path.exists():
                result.error = f"Input file not found: {input_file}"
                return result
            
            result.original_size = input_path.stat().st_size
            
            # Open and process image
            with Image.open(input_file) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P') and params.format.lower() in ['jpeg', 'jpg']:
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize if specified
                if params.resolution:
                    img = img.resize(params.resolution, Image.Resampling.LANCZOS)
                
                # Apply quality settings
                save_options = {}
                if params.quality:
                    if isinstance(params.quality, str):
                        quality_value = self.quality_settings.get(params.quality, 80)
                    else:
                        quality_value = params.quality
                    
                    if params.format.lower() in ['jpeg', 'jpg']:
                        save_options['quality'] = quality_value
                        save_options['optimize'] = True
                    elif params.format.lower() == 'webp':
                        save_options['quality'] = quality_value
                
                # Add custom options
                save_options.update(params.custom_options)
                
                # Ensure output directory exists
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                
                # Save converted image
                pil_format = self.supported_formats.get(params.format.lower())
                if pil_format:
                    img.save(output_file, format=pil_format, **save_options)
                else:
                    result.error = f"Unsupported image format: {params.format}"
                    return result
            
            # Verify output file
            output_path = Path(output_file)
            if output_path.exists():
                result.success = True
                result.converted_size = output_path.stat().st_size
                result.compression_ratio = result.converted_size / result.original_size
                result.format_info = self._get_image_info(output_file)
            else:
                result.error = "Conversion failed - output file not created"
            
        except Exception as e:
            logger.error(f"Image conversion failed: {str(e)}")
            result.error = str(e)
        finally:
            result.processing_time = time.time() - start_time
        
        return result
    
    def _get_image_info(self, file_path: str) -> Dict[str, Any]:
        """Get image file information"""



        try:
            with Image.open(file_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'width': img.width,
                    'height': img.height,
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P')
                }
        except Exception as e:
            logger.error(f"Failed to get image info: {str(e)}")
            return {}
    
    async def batch_resize_images(self, input_dir: str, output_dir: str,
                                size: Tuple[int, int], 
                                format: str = 'jpeg',
                                quality: int = 80) -> List[ConversionResult]:
        """Batch resize images in directory"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find image files
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(input_path.glob(ext))
            image_files.extend(input_path.glob(ext.upper()))
        
        results = []
        
        for image_file in image_files:
            output_file = output_path / f"{image_file.stem}.{format}"
            
            params = ConversionParams(
                format=format,
                resolution=size,
                quality=quality
            )
            
            result = await self.convert_image(str(image_file), str(output_file), params)
            results.append(result)
        
        return results
    
    async def create_progressive_jpeg(self, input_file: str, 
                                    output_file: str, quality: int = 80) -> ConversionResult:
        """Create progressive JPEG for web optimization"""
        params = ConversionParams(
            format='jpeg',
            quality=quality,
            custom_options={
                'progressive': True,
                'optimize': True
            }
        )
        
        return await self.convert_image(input_file, output_file, params)


class MultimediaConverter:
    """Main multimedia converter combining all format converters"""
    
    def __init__(self, temp_dir: Optional[str] = None,
                 cleanup_temp: bool = True):
        self.audio_converter = AudioConverter()
        self.video_converter = VideoConverter()
        self.image_converter = ImageConverter()
        
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.cleanup_temp = cleanup_temp
        self.conversion_history = []
        
        # Create temp directory if it doesn't exist
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
    
    async def convert_file(self, input_file: str, output_file: str,
                          params: ConversionParams) -> ConversionResult:
        """Convert file based on detected media type"""
        media_type = self._detect_media_type(input_file)
        
        if media_type == 'audio':
            return await self.audio_converter.convert_audio(input_file, output_file, params)
        elif media_type == 'video':
            return await self.video_converter.convert_video(input_file, output_file, params)
        elif media_type == 'image':
            return await self.image_converter.convert_image(input_file, output_file, params)
        else:
            return ConversionResult(
                success=False,
                input_file=input_file,
                error=f"Unsupported media type: {media_type}"
            )
    
    def _detect_media_type(self, file_path: str) -> str:
        """Detect media type from file extension or content"""
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type:
            if mime_type.startswith('audio/'):
                return 'audio'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('image/'):
                return 'image'
        
        # Fallback to extension-based detection
        ext = Path(file_path).suffix.lower()
        
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.3gp']
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico']
        
        if ext in audio_extensions:
            return 'audio'
        elif ext in video_extensions:
            return 'video'
        elif ext in image_extensions:
            return 'image'
        else:
            return 'unknown'
    
    async def get_media_info(self, file_path: str) -> MediaInfo:
        """Get comprehensive media file information"""
        media_type = self._detect_media_type(file_path)
        file_path_obj = Path(file_path)
        
        info = MediaInfo(
            file_path=file_path,
            media_type=media_type,
            format=file_path_obj.suffix.lower().lstrip('.'),
            size=file_path_obj.stat().st_size if file_path_obj.exists() else 0
        )
        
        try:
            if media_type == 'audio':
                # Use librosa for audio analysis
                y, sr = librosa.load(file_path, sr=None)
                info.duration = len(y) / sr
                info.sample_rate = sr
                info.channels = 1 if len(y.shape) == 1 else y.shape[1]
                
            elif media_type == 'video':
                # Use ffmpeg for video analysis
                probe = ffmpeg.probe(file_path)
                for stream in probe['streams']:
                    if stream['codec_type'] == 'video':
                        info.resolution = (stream.get('width', 0), stream.get('height', 0))
                        info.frame_rate = eval(stream.get('r_frame_rate', '0/1'))
                        info.duration = float(stream.get('duration', 0))
                        info.codec = stream.get('codec_name')
                        info.bit_rate = int(stream.get('bit_rate', 0))
                        break
                        
            elif media_type == 'image':
                # Use PIL for image analysis
                with Image.open(file_path) as img:
                    info.resolution = (img.width, img.height)
                    info.codec = img.format
                    info.metadata = {
                        'mode': img.mode,
                        'has_transparency': img.mode in ('RGBA', 'LA', 'P')
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get media info for {file_path}: {str(e)}")
            info.metadata['error'] = str(e)
        
        return info
    
    async def batch_convert(self, input_files: List[str], 
                          output_dir: str,
                          conversion_settings: Dict[str, ConversionParams],
                          max_concurrent: int = 4) -> Dict[str, List[ConversionResult]]:
        """Batch convert multiple files with different settings per media type"""
        # Group files by media type
        files_by_type = {'audio': [], 'video': [], 'image': []}
        
        for file in input_files:
            media_type = self._detect_media_type(file)
            if media_type in files_by_type:
                files_by_type[media_type].append(file)
        
        results = {}
        
        # Convert each media type
        for media_type, files in files_by_type.items():
            if not files or media_type not in conversion_settings:
                continue
            
            params = conversion_settings[media_type]
            
            if media_type == 'audio':
                results[media_type] = await self.audio_converter.batch_convert_audio(
                    files, output_dir, params, max_concurrent
                )
            elif media_type == 'video':
                # Video batch conversion
                semaphore = asyncio.Semaphore(max_concurrent)
                
                async def convert_video_file(input_file: str) -> ConversionResult:
                    async with semaphore:
                        input_path = Path(input_file)
                        output_file = os.path.join(
                            output_dir,
                            f"{input_path.stem}.{params.format}"
                        )
                        return await self.video_converter.convert_video(
                            input_file, output_file, params
                        )
                
                tasks = [convert_video_file(file) for file in files]
                results[media_type] = await asyncio.gather(*tasks)
                
            elif media_type == 'image':
                # Image batch conversion
                semaphore = asyncio.Semaphore(max_concurrent)
                
                async def convert_image_file(input_file: str) -> ConversionResult:
                    async with semaphore:
                        input_path = Path(input_file)
                        output_file = os.path.join(
                            output_dir,
                            f"{input_path.stem}.{params.format}"
                        )
                        return await self.image_converter.convert_image(
                            input_file, output_file, params
                        )
                
                tasks = [convert_image_file(file) for file in files]
                results[media_type] = await asyncio.gather(*tasks)
        
        # Store conversion history
        for media_type, type_results in results.items():
            self.conversion_history.extend(type_results)
        
        return results
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        if not self.conversion_history:
            return {'total_conversions': 0}
        
        successful_conversions = [r for r in self.conversion_history if r.success]
        failed_conversions = [r for r in self.conversion_history if not r.success]
        
        total_original_size = sum(r.original_size for r in successful_conversions)
        total_converted_size = sum(r.converted_size for r in successful_conversions)
        total_processing_time = sum(r.processing_time for r in self.conversion_history)
        
        return {
            'total_conversions': len(self.conversion_history),
            'successful_conversions': len(successful_conversions),
            'failed_conversions': len(failed_conversions),
            'total_original_size_bytes': total_original_size,
            'total_converted_size_bytes': total_converted_size,
            'overall_compression_ratio': total_converted_size / total_original_size if total_original_size > 0 else 0,
            'total_processing_time_seconds': total_processing_time,
            'average_processing_time': total_processing_time / len(self.conversion_history) if self.conversion_history else 0
        }
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.cleanup_temp:
            temp_path = Path(self.temp_dir)
            for file in temp_path.glob('*'):
                try:
                    if file.is_file():
                        file.unlink()
                    elif file.is_dir():
                        shutil.rmtree(file)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {file}: {str(e)}")


class StreamingOptimizer:
    """Optimize multimedia files for streaming"""
    
    def __init__(self, converter: MultimediaConverter):
        self.converter = converter
        
        # Streaming optimization presets
        self.streaming_presets = {
            'audio': {
                'low': ConversionParams(format='aac', bitrate='64k', sample_rate=22050),
                'medium': ConversionParams(format='aac', bitrate='128k', sample_rate=44100),
                'high': ConversionParams(format='aac', bitrate='192k', sample_rate=44100),
                'lossless': ConversionParams(format='flac', sample_rate=48000)
            },
            'video': {
                'mobile': ConversionParams(
                    format='mp4', 
                    resolution=(480, 270),
                    bitrate='500k',
                    frame_rate=24,
                    preset='fast'
                ),
                'sd': ConversionParams(
                    format='mp4',
                    resolution=(854, 480),
                    bitrate='1000k',
                    frame_rate=30,
                    preset='medium'
                ),
                'hd': ConversionParams(
                    format='mp4',
                    resolution=(1280, 720),
                    bitrate='2500k',
                    frame_rate=30,
                    preset='medium'
                ),
                'full_hd': ConversionParams(
                    format='mp4',
                    resolution=(1920, 1080),
                    bitrate='5000k',
                    frame_rate=30,
                    preset='slow'
                )
            }
        }
    
    async def optimize_for_streaming(self, input_file: str, output_dir: str,
                                   quality: str = 'medium') -> List[ConversionResult]:
        """Optimize file for streaming with multiple quality levels"""
        media_type = self.converter._detect_media_type(input_file)
        
        if media_type not in self.streaming_presets:
            return []
        
        results = []
        input_path = Path(input_file)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert to all quality levels if 'all' specified, otherwise just the requested quality
        if quality == 'all':
            qualities = list(self.streaming_presets[media_type].keys())
        else:
            qualities = [quality] if quality in self.streaming_presets[media_type] else ['medium']
        
        for qual in qualities:
            params = self.streaming_presets[media_type][qual]
            
            # Add streaming optimization options
            if media_type == 'video':
                params.custom_options.update({
                    'movflags': '+faststart',  # Enable fast start for web streaming
                    'profile:v': 'main',      # H.264 main profile for compatibility
                    'level': '3.1'            # H.264 level for broad compatibility
                })
            
            output_file = output_path / f"{input_path.stem}_{qual}.{params.format}"
            
            result = await self.converter.convert_file(
                str(input_file), str(output_file), params
            )
            results.append(result)
        
        return results
    
    async def create_adaptive_streaming_set(self, input_file: str, 
                                          output_dir: str) -> Dict[str, Any]:
        """Create complete adaptive streaming set (multiple bitrates/resolutions)"""
        media_type = self.converter._detect_media_type(input_file)
        
        if media_type != 'video':
            return {'error': 'Adaptive streaming only supported for video files'}
        
        # Create multiple quality levels
        results = await self.optimize_for_streaming(input_file, output_dir, 'all')
        
        # Generate manifest/playlist files
        manifest_data = {
            'source_file': input_file,
            'variants': []
        }
        
        for result in results:
            if result.success:
                manifest_data['variants'].append({
                    'file': result.output_file,
                    'resolution': result.format_info.get('resolution', 'unknown'),
                    'bitrate': result.format_info.get('bit_rate', 0),
                    'size_bytes': result.converted_size
                })
        
        # Save manifest
        manifest_file = Path(output_dir) / 'streaming_manifest.json'
        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        return {
            'success': True,
            'manifest_file': str(manifest_file),
            'variants': len(manifest_data['variants']),
            'results': results
        }


class ConversionError(Exception):
    """Custom exception for conversion errors"""
    pass
