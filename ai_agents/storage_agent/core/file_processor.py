"""File Processor - Advanced Multi-Format File Processing Engine

Enterprise-grade file processing system supporting audio, video, image, and document
processing with intelligent format conversion, compression, and quality optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This file processing technology is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist: Fahed Mlaiel  
- Database Administrator & Security Expert: Fahed Mlaiel
- Microservices Architect & DevOps Engineer: Fahed Mlaiel
- AI Prompt Engineer & Content Protection Specialist: Fahed Mlaiel
"""
import asyncio
import logging
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import mimetypes
import hashlib

# Audio processing
import librosa
import soundfile as sf
import pydub
from pydub import AudioSegment

# Video processing
import cv2
import ffmpeg

# Image processing
from PIL import Image, ImageEnhance, ImageFilter
import pillow_heif

# Document processing
import PyPDF2
import docx2txt
from odf import text, teletype
from odf.opendocument import load

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ProcessingError, ValidationError, UnsupportedFormatError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProcessingError, ValidationError, UnsupportedFormatError = globals().get('ProcessingError, ValidationError, UnsupportedFormatError', Exception)
from ...monitoring.metrics import MetricsCollector
from ...utils.compression_utils import CompressionManager

logger = logging.getLogger(__name__)

class ProcessingType(str, Enum):
    """File processing types"""
    AUDIO_CONVERSION = "audio_conversion"
    VIDEO_CONVERSION = "video_conversion"
    IMAGE_OPTIMIZATION = "image_optimization"
    DOCUMENT_EXTRACTION = "document_extraction"
    COMPRESSION = "compression"
    FORMAT_VALIDATION = "format_validation"

class AudioFormat(str, Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"

class VideoFormat(str, Enum):
    """Supported video formats"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    WMV = "wmv"

class ImageFormat(str, Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    SVG = "svg"

@dataclass
class ProcessingOptions:
    """File processing configuration options"""
    compression_level: int = 5  # 1-9, higher = more compression
    quality: int = 85  # 1-100, higher = better quality
    format_conversion: bool = True
    progressive_enhancement: bool = True
    preserve_metadata: bool = True
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    bitrate: Optional[str] = None  # e.g., "320k", "128k"
    sample_rate: Optional[int] = None  # e.g., 44100, 48000
    channels: Optional[int] = None  # 1 = mono, 2 = stereo

@dataclass
class ProcessingResult:
    """File processing result"""
    success: bool
    input_path: str
    output_path: str
    processing_type: ProcessingType
    original_format: str
    target_format: str
    original_size: int
    final_size: int
    compression_ratio: float
    processing_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None

class FileProcessor:
    """
    Enterprise file processing engine with support for audio, video, image,
    and document processing with intelligent format conversion and optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        
        # Initialize components
        self.metrics = MetricsCollector('file_processor')
        self.compression_manager = CompressionManager()
        
        # Supported MIME type mappings
        self.format_mappings = {
            # Audio formats
            'audio/mpeg': AudioFormat.MP3,
            'audio/wav': AudioFormat.WAV,
            'audio/flac': AudioFormat.FLAC,
            'audio/aac': AudioFormat.AAC,
            'audio/ogg': AudioFormat.OGG,
            'audio/x-m4a': AudioFormat.M4A,
            
            # Video formats
            'video/mp4': VideoFormat.MP4,
            'video/avi': VideoFormat.AVI,
            'video/quicktime': VideoFormat.MOV,
            'video/x-matroska': VideoFormat.MKV,
            'video/webm': VideoFormat.WEBM,
            'video/x-flv': VideoFormat.FLV,
            
            # Image formats
            'image/jpeg': ImageFormat.JPEG,
            'image/png': ImageFormat.PNG,
            'image/webp': ImageFormat.WEBP,
            'image/gif': ImageFormat.GIF,
            'image/bmp': ImageFormat.BMP,
            'image/tiff': ImageFormat.TIFF,
            'image/svg+xml': ImageFormat.SVG
        }
        
        # Processing statistics
        self.stats = {
            'total_files_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'total_bytes_processed': 0,
            'total_bytes_saved': 0,
            'average_compression_ratio': 0.0,
            'processing_by_type': {ptype: 0 for ptype in ProcessingType},
            'format_conversions': {}
        }
        
        # Temporary directory for processing
        self.temp_dir = Path(self.config.get('temp_dir', tempfile.gettempdir())) / 'file_processor'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("FileProcessor initialized successfully")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default processing configuration"""
        return {
            'temp_dir': '/tmp/file_processing',
            'max_workers': 4,
            'chunk_size': 64 * 1024,
            'quality_presets': {
                'high': {'quality': 95, 'compression_level': 3},
                'medium': {'quality': 85, 'compression_level': 5},
                'low': {'quality': 70, 'compression_level': 7}
            },
            'format_priorities': {
                'audio': [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG],
                'video': [VideoFormat.MP4, VideoFormat.WEBM, VideoFormat.AVI],
                'image': [ImageFormat.WEBP, ImageFormat.JPEG, ImageFormat.PNG]
            },
            'ffmpeg_path': shutil.which('ffmpeg'),
            'ffprobe_path': shutil.which('ffprobe')
        }
    
    async def process_file(
        self,
        input_path: Union[str, Path],
        file_category: str,
        options: ProcessingOptions
    ) -> ProcessingResult:
        """
        Process file with intelligent format detection and optimization
        
        Args:
            input_path: Path to input file
            file_category: Category of file (audio, video, image, etc.)
            options: Processing configuration options
            
        Returns:
            ProcessingResult with processing details
        """
        start_time = datetime.utcnow()
        input_path = Path(input_path)
        
        try:
            # Validate input file
            if not input_path.exists():
                raise ValidationError(f"Input file not found: {input_path}")
            
            original_size = input_path.stat().st_size
            original_format = self._detect_file_format(input_path)
            
            # Determine processing type
            processing_type = self._determine_processing_type(file_category, options)
            
            # Generate output path
            output_path = await self._generate_output_path(
                input_path, file_category, options
            )
            
            # Process file based on category
            if file_category.lower() == 'audio':
                result = await self._process_audio(input_path, output_path, options)
            
            elif file_category.lower() == 'video':
                result = await self._process_video(input_path, output_path, options)
            
            elif file_category.lower() == 'image':
                result = await self._process_image(input_path, output_path, options)
            
            elif file_category.lower() in ['text', 'document']:
                result = await self._process_document(input_path, output_path, options)
            
            else:
                # Generic file processing (compression only)
                result = await self._process_generic(input_path, output_path, options)
            
            # Calculate final metrics
            final_size = Path(result.output_path).stat().st_size if Path(result.output_path).exists() else original_size
            compression_ratio = final_size / original_size if original_size > 0 else 1.0
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract metadata
            metadata = await self._extract_metadata(result.output_path, file_category)
            
            # Update result
            result.original_size = original_size
            result.final_size = final_size
            result.compression_ratio = compression_ratio
            result.processing_time = processing_time
            result.metadata = metadata
            
            # Update statistics
            await self._update_statistics(result, processing_type)
            
            # Record metrics
            self.metrics.record_processing_time(processing_time)
            self.metrics.increment_counter('files_processed_success')
            self.metrics.record_gauge('compression_ratio', compression_ratio)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.metrics.increment_counter('files_processed_failure')
            
            logger.error(f"File processing failed for {input_path}: {e}")
            
            return ProcessingResult(
                success=False,
                input_path=str(input_path),
                output_path="",
                processing_type=ProcessingType.FORMAT_VALIDATION,
                original_format=original_format,
                target_format="",
                original_size=original_size if 'original_size' in locals() else 0,
                final_size=0,
                compression_ratio=1.0,
                processing_time=processing_time,
                metadata={},
                error=str(e)
            )
    
    async def batch_process_files(
        self,
        file_paths: List[Union[str, Path]],
        file_categories: List[str],
        options: ProcessingOptions,
        max_workers: Optional[int] = None
    ) -> List[ProcessingResult]:
        """
        Process multiple files concurrently
        
        Args:
            file_paths: List of file paths
            file_categories: List of file categories
            options: Processing options
            max_workers: Maximum concurrent workers
            
        Returns:
            List of processing results
        """
        max_workers = max_workers or self.config.get('max_workers', 4)
        
        if len(file_paths) != len(file_categories):
            raise ValueError("file_paths and file_categories must have same length")
        
        # Create semaphore for concurrent processing
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_single(file_path: Union[str, Path], category: str) -> ProcessingResult:
            async with semaphore:
                return await self.process_file(file_path, category, options)
        
        # Create tasks
        tasks = [
            process_single(file_path, category)
            for file_path, category in zip(file_paths, file_categories)
        ]
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ProcessingResult(
                    success=False,
                    input_path=str(file_paths[i]),
                    output_path="",
                    processing_type=ProcessingType.FORMAT_VALIDATION,
                    original_format="",
                    target_format="",
                    original_size=0,
                    final_size=0,
                    compression_ratio=1.0,
                    processing_time=0.0,
                    metadata={},
                    error=str(result)
                ))
            else:
                final_results.append(result)
        
        logger.info(f"Batch processed {len(file_paths)} files")
        return final_results
    
    async def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get comprehensive file information and metadata
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise ValidationError(f"File not found: {file_path}")
            
            # Basic file info
            stat_info = file_path.stat()
            mime_type = mimetypes.guess_type(str(file_path))[0]
            
            info = {
                'path': str(file_path),
                'name': file_path.name,
                'extension': file_path.suffix.lower(),
                'size': stat_info.st_size,
                'mime_type': mime_type,
                'created_time': datetime.fromtimestamp(stat_info.st_ctime),
                'modified_time': datetime.fromtimestamp(stat_info.st_mtime),
                'checksum': await self._calculate_checksum(file_path)
            }
            
            # Category-specific metadata
            category = self._determine_file_category(mime_type)
            
            if category == 'audio':
                info['audio_metadata'] = await self._get_audio_metadata(file_path)
            elif category == 'video':
                info['video_metadata'] = await self._get_video_metadata(file_path)
            elif category == 'image':
                info['image_metadata'] = await self._get_image_metadata(file_path)
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            raise ProcessingError(f"File info extraction failed: {e}")
    
    # Audio processing methods
    
    async def _process_audio(
        self,
        input_path: Path,
        output_path: Path,
        options: ProcessingOptions
    ) -> ProcessingResult:
        """Process audio file with format conversion and optimization"""
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(str(input_path), sr=options.sample_rate)
            
            # Apply audio processing
            if options.channels and options.channels == 1:
                # Convert to mono
                if len(audio_data.shape) > 1:
                    audio_data = librosa.to_mono(audio_data)
            
            # Determine target format
            target_format = self._get_best_audio_format(input_path.suffix, options)
            output_path = output_path.with_suffix(f'.{target_format}')
            
            # Export processed audio
            if target_format == AudioFormat.MP3:
                audio_segment = AudioSegment(
                    audio_data.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=audio_data.dtype.itemsize,
                    channels=1 if len(audio_data.shape) == 1 else audio_data.shape[0]
                )
                
                bitrate = options.bitrate or "320k"
                audio_segment.export(
                    str(output_path),
                    format="mp3",
                    bitrate=bitrate
                )
            
            elif target_format == AudioFormat.WAV:
                sf.write(str(output_path), audio_data, sample_rate)
            
            elif target_format == AudioFormat.FLAC:
                sf.write(str(output_path), audio_data, sample_rate, format='FLAC')
            
            else:
                # Use pydub for other formats
                audio_segment = AudioSegment.from_file(str(input_path))
                audio_segment.export(str(output_path), format=target_format)
            
            return ProcessingResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                processing_type=ProcessingType.AUDIO_CONVERSION,
                original_format=input_path.suffix[1:],
                target_format=target_format,
                original_size=0,  # Will be filled later
                final_size=0,     # Will be filled later
                compression_ratio=0.0,  # Will be filled later
                processing_time=0.0,    # Will be filled later
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            raise ProcessingError(f"Audio processing failed: {e}")
    
    async def _process_video(
        self,
        input_path: Path,
        output_path: Path,
        options: ProcessingOptions
    ) -> ProcessingResult:
        """Process video file with format conversion and optimization"""
        try:
            # Determine target format
            target_format = self._get_best_video_format(input_path.suffix, options)
            output_path = output_path.with_suffix(f'.{target_format}')
            
            # Build ffmpeg command
            input_stream = ffmpeg.input(str(input_path))
            
            # Apply video processing options
            video_options = {}
            
            if options.max_width or options.max_height:
                width = options.max_width or -1
                height = options.max_height or -1
                video_options['vf'] = f'scale={width}:{height}'
            
            if options.bitrate:
                video_options['b:v'] = options.bitrate
            
            # Quality settings
            if target_format == VideoFormat.MP4:
                video_options['c:v'] = 'libx264'
                video_options['crf'] = str(int((100 - options.quality) * 0.3))
                video_options['preset'] = 'medium'
            
            elif target_format == VideoFormat.WEBM:
                video_options['c:v'] = 'libvpx-vp9'
                video_options['b:v'] = options.bitrate or '1M'
            
            # Execute conversion
            output_stream = ffmpeg.output(input_stream, str(output_path), **video_options)
            
            await asyncio.create_subprocess_exec(
                *ffmpeg.compile(output_stream),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            return ProcessingResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                processing_type=ProcessingType.VIDEO_CONVERSION,
                original_format=input_path.suffix[1:],
                target_format=target_format,
                original_size=0,
                final_size=0,
                compression_ratio=0.0,
                processing_time=0.0,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            raise ProcessingError(f"Video processing failed: {e}")
    
    async def _process_image(
        self,
        input_path: Path,
        output_path: Path,
        options: ProcessingOptions
    ) -> ProcessingResult:
        """Process image with optimization and format conversion"""
        try:
            # Open image
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    if img.mode == 'P' and 'transparency' in img.info:
                        img = img.convert('RGBA')
                    else:
                        img = img.convert('RGB')
                
                # Apply size constraints
                if options.max_width or options.max_height:
                    img.thumbnail(
                        (options.max_width or img.width, options.max_height or img.height),
                        Image.Resampling.LANCZOS
                    )
                
                # Apply enhancement
                if options.progressive_enhancement:
                    # Enhance sharpness slightly
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.1)
                    
                    # Enhance contrast slightly
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.05)
                
                # Determine target format
                target_format = self._get_best_image_format(input_path.suffix, options)
                output_path = output_path.with_suffix(f'.{target_format.lower()}')
                
                # Save with optimization
                save_options = {
                    'optimize': True,
                    'quality': options.quality
                }
                
                if target_format.upper() == 'JPEG':
                    save_options['progressive'] = options.progressive_enhancement
                
                elif target_format.upper() == 'PNG':
                    save_options['compress_level'] = options.compression_level
                
                elif target_format.upper() == 'WEBP':
                    save_options['method'] = 6  # Best compression
                    save_options['lossless'] = options.quality >= 95
                
                img.save(output_path, target_format.upper(), **save_options)
            
            return ProcessingResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                processing_type=ProcessingType.IMAGE_OPTIMIZATION,
                original_format=input_path.suffix[1:],
                target_format=target_format,
                original_size=0,
                final_size=0,
                compression_ratio=0.0,
                processing_time=0.0,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise ProcessingError(f"Image processing failed: {e}")
    
    async def _process_document(
        self,
        input_path: Path,
        output_path: Path,
        options: ProcessingOptions
    ) -> ProcessingResult:
        """Process document with text extraction and optimization"""
        try:
            # Extract text content based on format
            text_content = ""
            original_format = input_path.suffix.lower()
            
            if original_format == '.pdf':
                with open(input_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text()
            
            elif original_format in ['.docx', '.doc']:
                text_content = docx2txt.process(str(input_path))
            
            elif original_format == '.odt':
                doc = load(str(input_path))
                text_elements = doc.getElementsByType(text.P)
                text_content = '\n'.join(teletype.extractText(element) for element in text_elements)
            
            else:
                # Plain text file
                with open(input_path, 'r', encoding='utf-8') as file:
                    text_content = file.read()
            
            # Save processed text
            target_format = 'txt'
            output_path = output_path.with_suffix('.txt')
            
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text_content)
            
            # Optional: Create compressed version
            if options.compression_level > 5:
                compressed_path = str(output_path) + '.gz'
                await self.compression_manager.compress_file(str(output_path), compressed_path)
                output_path = Path(compressed_path)
            
            return ProcessingResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                processing_type=ProcessingType.DOCUMENT_EXTRACTION,
                original_format=original_format[1:],
                target_format=target_format,
                original_size=0,
                final_size=0,
                compression_ratio=0.0,
                processing_time=0.0,
                metadata={'text_length': len(text_content)}
            )
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise ProcessingError(f"Document processing failed: {e}")
    
    async def _process_generic(
        self,
        input_path: Path,
        output_path: Path,
        options: ProcessingOptions
    ) -> ProcessingResult:
        """Generic file processing (compression only)"""
        try:
            if options.compression_level > 0:
                # Compress file
                await self.compression_manager.compress_file(
                    str(input_path),
                    str(output_path),
                    compression_level=options.compression_level
                )
            else:
                # Just copy file
                shutil.copy2(input_path, output_path)
            
            return ProcessingResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path),
                processing_type=ProcessingType.COMPRESSION,
                original_format=input_path.suffix[1:],
                target_format=output_path.suffix[1:],
                original_size=0,
                final_size=0,
                compression_ratio=0.0,
                processing_time=0.0,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Generic file processing failed: {e}")
            raise ProcessingError(f"Generic file processing failed: {e}")
    
    # Metadata extraction methods
    
    async def _get_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio metadata"""
        try:
            y, sr = librosa.load(str(file_path), sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Use pydub for additional metadata
            audio = AudioSegment.from_file(str(file_path))
            
            return {
                'duration': duration,
                'sample_rate': sr,
                'channels': audio.channels,
                'frame_rate': audio.frame_rate,
                'frame_count': len(y),
                'bit_depth': audio.sample_width * 8,
                'format': file_path.suffix[1:].upper()
            }
            
        except Exception as e:
            logger.warning(f"Audio metadata extraction failed: {e}")
            return {}
    
    async def _get_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract video metadata"""
        try:
            # Use OpenCV for basic info
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                return {}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration,
                'aspect_ratio': width / height if height > 0 else 0,
                'format': file_path.suffix[1:].upper()
            }
            
        except Exception as e:
            logger.warning(f"Video metadata extraction failed: {e}")
            return {}
    
    async def _get_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image metadata"""
        try:
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'color_count': len(img.getcolors(maxcolors=256*256*256)) if img.mode == 'P' else None,
                    'dpi': img.info.get('dpi', (72, 72))
                }
                
        except Exception as e:
            logger.warning(f"Image metadata extraction failed: {e}")
            return {}
    
    # Utility methods
    
    def _detect_file_format(self, file_path: Path) -> str:
        """Detect file format from path and content"""
        return file_path.suffix[1:].lower() if file_path.suffix else ""
    
    def _determine_file_category(self, mime_type: Optional[str]) -> str:
        """Determine file category from MIME type"""
        if not mime_type:
            return "unknown"
        
        if mime_type.startswith('audio/'):
            return "audio"
        elif mime_type.startswith('video/'):
            return "video"
        elif mime_type.startswith('image/'):
            return "image"
        elif mime_type.startswith('text/') or mime_type in ['application/pdf', 'application/msword']:
            return "document"
        else:
            return "unknown"
    
    def _determine_processing_type(self, file_category: str, options: ProcessingOptions) -> ProcessingType:
        """Determine processing type based on category and options"""
        if file_category == "audio":
            return ProcessingType.AUDIO_CONVERSION
        elif file_category == "video":
            return ProcessingType.VIDEO_CONVERSION
        elif file_category == "image":
            return ProcessingType.IMAGE_OPTIMIZATION
        elif file_category in ["text", "document"]:
            return ProcessingType.DOCUMENT_EXTRACTION
        else:
            return ProcessingType.COMPRESSION
    
    def _get_best_audio_format(self, current_extension: str, options: ProcessingOptions) -> str:
        """Get best audio format for optimization"""
        priorities = self.config['format_priorities']['audio']
        
        # If current format is already optimal, keep it
        current_format = current_extension[1:].lower()
        if current_format in [f.value for f in priorities[:2]]:
            return current_format
        
        # Return highest priority format
        return priorities[0].value
    
    def _get_best_video_format(self, current_extension: str, options: ProcessingOptions) -> str:
        """Get best video format for optimization"""
        priorities = self.config['format_priorities']['video']
        
        current_format = current_extension[1:].lower()
        if current_format in [f.value for f in priorities[:2]]:
            return current_format
        
        return priorities[0].value
    
    def _get_best_image_format(self, current_extension: str, options: ProcessingOptions) -> str:
        """Get best image format for optimization"""
        priorities = self.config['format_priorities']['image']
        
        current_format = current_extension[1:].lower()
        
        # For transparency, prefer PNG
        if current_format in ['png', 'gif'] and options.preserve_metadata:
            return 'png'
        
        # For high quality, prefer original or WebP
        if options.quality >= 90:
            return current_format if current_format in ['webp', 'png'] else 'webp'
        
        return priorities[0].value
    
    async def _generate_output_path(
        self,
        input_path: Path,
        file_category: str,
        options: ProcessingOptions
    ) -> Path:
        """Generate output path for processed file"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        output_name = f"{input_path.stem}_processed_{timestamp}"
        
        # Extension will be determined during processing
        output_path = self.temp_dir / f"{output_name}.tmp"
        
        return output_path
    
    async def _extract_metadata(self, file_path: str, category: str) -> Dict[str, Any]:
        """Extract comprehensive file metadata"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {}
            
            metadata = {
                'processed_at': datetime.utcnow().isoformat(),
                'processor_version': '1.0.0'
            }
            
            if category == 'audio':
                metadata.update(await self._get_audio_metadata(path))
            elif category == 'video':
                metadata.update(await self._get_video_metadata(path))
            elif category == 'image':
                metadata.update(await self._get_image_metadata(path))
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {}
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _update_statistics(self, result: ProcessingResult, processing_type: ProcessingType):
        """Update processing statistics"""
        self.stats['total_files_processed'] += 1
        self.stats['processing_by_type'][processing_type] += 1
        
        if result.success:
            self.stats['successful_processing'] += 1
            self.stats['total_bytes_processed'] += result.original_size
            self.stats['total_bytes_saved'] += result.original_size - result.final_size
            
            # Update average compression ratio
            total_successful = self.stats['successful_processing']
            current_avg = self.stats['average_compression_ratio']
            self.stats['average_compression_ratio'] = (
                (current_avg * (total_successful - 1) + result.compression_ratio) / total_successful
            )
            
            # Track format conversions
            conversion_key = f"{result.original_format}_to_{result.target_format}"
            self.stats['format_conversions'][conversion_key] = (
                self.stats['format_conversions'].get(conversion_key, 0) + 1
            )
        else:
            self.stats['failed_processing'] += 1
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return {
            'statistics': self.stats.copy(),
            'supported_formats': {
                'audio': [f.value for f in AudioFormat],
                'video': [f.value for f in VideoFormat],
                'image': [f.value for f in ImageFormat]
            },
            'configuration': self.config
        }
    
    async def cleanup(self):
        """Cleanup processor resources"""
        try:
            # Clean temporary files older than 1 hour
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            
            for temp_file in self.temp_dir.glob('*'):
                if temp_file.is_file():
                    file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        temp_file.unlink()
            
            logger.info("FileProcessor cleanup completed")
            
        except Exception as e:
            logger.error(f"FileProcessor cleanup failed: {e}")
