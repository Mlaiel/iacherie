"""
Multi-Format Content Processor
=============================

Professional multi-format content processing engine for IA Influencer Agent platform.
Handles comprehensive processing of audio, video, image, and text content with
advanced AI-powered optimization and format conversion.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  INTELLECTUAL PROPERTY WARNING 
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import mimetypes
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import uuid
import hashlib
import tempfile
import os

import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import librosa
import soundfile as sf
import ffmpeg
from pydub import AudioSegment
import fitz  # PyMuPDF
import pytesseract
from transformers import pipeline
import magic

from ..processors.audio_processor import AudioProcessor
from ..processors.video_processor import VideoProcessor  
from ..processors.image_processor import ImageProcessor
from ..processors.text_processor import TextProcessor
from ...core.exceptions import ProcessingError, ValidationError


class ProcessingQuality(Enum):
    """Content processing quality levels"""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"


class OutputFormat(Enum):
    """Supported output formats"""
    ORIGINAL = "original"
    OPTIMIZED = "optimized"
    COMPRESSED = "compressed"
    TRANSCODED = "transcoded"


@dataclass
class ProcessingOptions:
    """Content processing configuration options"""
    quality: ProcessingQuality = ProcessingQuality.STANDARD
    output_format: OutputFormat = OutputFormat.OPTIMIZED
    enable_ai_enhancement: bool = True
    enable_compression: bool = True
    enable_thumbnails: bool = True
    enable_transcription: bool = False
    enable_translation: bool = False
    target_languages: List[str] = None
    watermark_enabled: bool = False
    watermark_text: str = ""
    custom_parameters: Dict[str, Any] = None


@dataclass
class ProcessingResult:
    """Content processing result"""
    success: bool
    original_data: bytes
    processed_data: bytes
    thumbnails: Dict[str, bytes]
    metadata: Dict[str, Any]
    quality_metrics: Dict[str, float]
    processing_time: float
    file_size_reduction: float
    warnings: List[str]
    errors: List[str]
    ai_enhancements: List[str]


class MultiFormatProcessor:
    """
    Professional multi-format content processor for IA Influencer Agent platform.
    
    Provides comprehensive content processing capabilities including:
    - Multi-format support (audio, video, image, text)
    - AI-powered enhancement and optimization
    - Format conversion and transcoding
    - Quality assessment and metrics
    - Thumbnail and preview generation
    - Metadata extraction and enrichment
    """
    
    def __init__(self):
        """Initialize MultiFormatProcessor with specialized processors."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized processors
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
        
        # Initialize AI models
        self._init_ai_models()
        
        # Processing configurations
        self.supported_formats = {
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
            'text': ['.txt', '.md', '.html', '.pdf', '.docx', '.rtf', '.json', '.xml']
        }
        
        # Quality presets
        self.quality_presets = {
            ProcessingQuality.DRAFT: {
                'audio_bitrate': 64,
                'video_bitrate': 500,
                'image_quality': 60,
                'compression_level': 8
            },
            ProcessingQuality.STANDARD: {
                'audio_bitrate': 128,
                'video_bitrate': 1000,
                'image_quality': 80,
                'compression_level': 6
            },
            ProcessingQuality.HIGH: {
                'audio_bitrate': 256,
                'video_bitrate': 2000,
                'image_quality': 90,
                'compression_level': 4
            },
            ProcessingQuality.ULTRA: {
                'audio_bitrate': 320,
                'video_bitrate': 4000,
                'image_quality': 95,
                'compression_level': 2
            }
        }
    
    def _init_ai_models(self):
        """Initialize AI models for content enhancement"""



        try:
            # Image enhancement models
            self.image_enhancer = pipeline(
                "image-classification",
                model="microsoft/resnet-50",
                device=-1  # CPU
            )
            
            # Text analysis models
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            self.text_summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
            # Audio analysis would use librosa and custom models
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"AI model initialization failed: {str(e)}")
            # Set fallback None values
            self.image_enhancer = None
            self.sentiment_analyzer = None
            self.text_summarizer = None
    
    async def process_content(self, file_data: Union[bytes, BinaryIO], 
                            filename: str, content_type: str = None,
                            options: ProcessingOptions = None) -> ProcessingResult:
        """
        Process content with comprehensive multi-format support.
        
        Args:
            file_data: Content file data
            filename: Original filename
            content_type: Content type (auto-detected if None)
            options: Processing configuration options
            
        Returns:
            Processing result with enhanced content and metadata
        """
        start_time = datetime.utcnow()
        processing_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Starting content processing: {processing_id}")
            
            if options is None:
                options = ProcessingOptions()
            
            # Convert file data to bytes if needed
            if hasattr(file_data, 'read'):
                file_bytes = file_data.read()
                file_data.seek(0)  # Reset position
            else:
                file_bytes = file_data
            
            # Auto-detect content type if not provided
            if content_type is None:
                content_type = await self._detect_content_type(file_bytes, filename)
            
            # Select appropriate processor and process content
            if content_type == 'audio':
                result = await self._process_audio_content(file_bytes, filename, options)
            elif content_type == 'video':
                result = await self._process_video_content(file_bytes, filename, options)
            elif content_type == 'image':
                result = await self._process_image_content(file_bytes, filename, options)
            elif content_type == 'text':
                result = await self._process_text_content(file_bytes, filename, options)
            else:
                raise ProcessingError(f"Unsupported content type: {content_type}")
            
            # Calculate processing metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            original_size = len(file_bytes)
            processed_size = len(result.processed_data)
            size_reduction = ((original_size - processed_size) / original_size) * 100
            
            # Update result with metrics
            result.processing_time = processing_time
            result.file_size_reduction = size_reduction
            result.metadata.update({
                'processing_id': processing_id,
                'original_size': original_size,
                'processed_size': processed_size,
                'content_type': content_type,
                'processing_quality': options.quality.value,
                'processing_timestamp': start_time.isoformat()
            })
            
            self.logger.info(f"Content processing completed: {processing_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {processing_id} - {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                original_data=file_bytes if 'file_bytes' in locals() else b'',
                processed_data=b'',
                thumbnails={},
                metadata={'error': str(e), 'processing_id': processing_id},
                quality_metrics={},
                processing_time=processing_time,
                file_size_reduction=0,
                warnings=[],
                errors=[str(e)],
                ai_enhancements=[]
            )
    
    async def batch_process_content(self, content_items: List[Tuple[Union[bytes, BinaryIO], str, str]], 
                                  options: ProcessingOptions = None) -> List[ProcessingResult]:
        """
        Process multiple content items in batch.
        
        Args:
            content_items: List of (file_data, filename, content_type) tuples
            options: Processing configuration options
            
        Returns:
            List of processing results
        """



        try:
            self.logger.info(f"Starting batch processing of {len(content_items)} items")
            
            # Process items concurrently with limited concurrency
            semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent processes
            
            async def process_single(item):
                async with semaphore:
                    file_data, filename, content_type = item
                    return await self.process_content(file_data, filename, content_type, options)
            
            tasks = [process_single(item) for item in content_items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Batch processing error for item {i}: {str(result)}")
                    processed_results.append(ProcessingResult(
                        success=False,
                        original_data=b'',
                        processed_data=b'',
                        thumbnails={},
                        metadata={'error': str(result)},
                        quality_metrics={},
                        processing_time=0,
                        file_size_reduction=0,
                        warnings=[],
                        errors=[str(result)],
                        ai_enhancements=[]
                    ))
                else:
                    processed_results.append(result)
            
            self.logger.info(f"Batch processing completed: {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            raise
    
    async def _detect_content_type(self, file_data: bytes, filename: str) -> str:
        """Auto-detect content type from file data and filename"""



        try:
            # Use python-magic for MIME type detection
            mime_type = magic.from_buffer(file_data, mime=True)
            
            # Map MIME types to content types
            if mime_type.startswith('audio/'):
                return 'audio'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('image/'):
                return 'image'
            elif mime_type.startswith('text/') or mime_type == 'application/pdf':
                return 'text'
            
            # Fallback to file extension
            file_ext = Path(filename).suffix.lower()
            for content_type, extensions in self.supported_formats.items():
                if file_ext in extensions:
                    return content_type
            
            # Default to text for unknown types
            return 'text'
            
        except Exception as e:
            self.logger.warning(f"Content type detection failed: {str(e)}")
            # Fallback to extension-based detection
            file_ext = Path(filename).suffix.lower()
            for content_type, extensions in self.supported_formats.items():
                if file_ext in extensions:
                    return content_type
            return 'text'
    
    async def _process_audio_content(self, file_data: bytes, filename: str, 
                                   options: ProcessingOptions) -> ProcessingResult:
        """Process audio content with enhancement and optimization"""



        try:
            warnings = []
            errors = []
            ai_enhancements = []
            thumbnails = {}
            
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            try:
                # Load audio using librosa
                audio_data, sample_rate = librosa.load(temp_path, sr=None)
                
                # Extract basic metadata
                metadata = {
                    'duration': float(len(audio_data) / sample_rate),
                    'sample_rate': int(sample_rate),
                    'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                    'format': Path(filename).suffix.lower(),
                    'mime_type': mimetypes.guess_type(filename)[0]
                }
                
                # AI-powered audio enhancement
                if options.enable_ai_enhancement:
                    try:
                        # Noise reduction
                        audio_data = self._reduce_noise(audio_data, sample_rate)
                        ai_enhancements.append("noise_reduction")
                        
                        # Dynamic range compression
                        audio_data = self._compress_dynamic_range(audio_data)
                        ai_enhancements.append("dynamic_range_compression")
                        
                        # Audio normalization
                        audio_data = librosa.util.normalize(audio_data)
                        ai_enhancements.append("normalization")
                        
                    except Exception as e:
                        warnings.append(f"AI enhancement failed: {str(e)}")
                
                # Audio analysis and feature extraction
                quality_metrics = await self._analyze_audio_quality(audio_data, sample_rate)
                
                # Generate audio visualization thumbnails
                if options.enable_thumbnails:
                    try:
                        thumbnails['waveform'] = await self._generate_waveform_thumbnail(audio_data, sample_rate)
                        thumbnails['spectrogram'] = await self._generate_spectrogram_thumbnail(audio_data, sample_rate)
                    except Exception as e:
                        warnings.append(f"Thumbnail generation failed: {str(e)}")
                
                # Process based on quality settings
                quality_preset = self.quality_presets[options.quality]
                
                if options.output_format == OutputFormat.OPTIMIZED:
                    # Convert to optimal format (MP3 with specified bitrate)
                    audio_segment = AudioSegment.from_file(temp_path)
                    
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as output_file:
                        audio_segment.export(
                            output_file.name,
                            format="mp3",
                            bitrate=f"{quality_preset['audio_bitrate']}k"
                        )
                        
                        with open(output_file.name, 'rb') as f:
                            processed_data = f.read()
                        
                        os.unlink(output_file.name)
                        
                        metadata['output_format'] = 'mp3'
                        metadata['bitrate'] = quality_preset['audio_bitrate']
                else:
                    # Keep original format
                    processed_data = file_data
                
                return ProcessingResult(
                    success=True,
                    original_data=file_data,
                    processed_data=processed_data,
                    thumbnails=thumbnails,
                    metadata=metadata,
                    quality_metrics=quality_metrics,
                    processing_time=0,  # Will be set by caller
                    file_size_reduction=0,  # Will be calculated by caller
                    warnings=warnings,
                    errors=errors,
                    ai_enhancements=ai_enhancements
                )
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            self.logger.error(f"Audio processing failed: {str(e)}")
            raise ProcessingError(f"Audio processing failed: {str(e)}")
    
    async def _process_video_content(self, file_data: bytes, filename: str, 
                                   options: ProcessingOptions) -> ProcessingResult:
        """Process video content with enhancement and optimization"""



        try:
            warnings = []
            errors = []
            ai_enhancements = []
            thumbnails = {}
            
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            try:
                # Extract video metadata using ffmpeg
                probe = ffmpeg.probe(temp_path)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
                
                metadata = {
                    'duration': float(probe['format']['duration']),
                    'width': int(video_stream['width']) if video_stream else 0,
                    'height': int(video_stream['height']) if video_stream else 0,
                    'fps': eval(video_stream['r_frame_rate']) if video_stream else 0,
                    'video_codec': video_stream['codec_name'] if video_stream else None,
                    'audio_codec': audio_stream['codec_name'] if audio_stream else None,
                    'format': Path(filename).suffix.lower(),
                    'mime_type': mimetypes.guess_type(filename)[0],
                    'has_audio': audio_stream is not None
                }
                
                # Generate video thumbnails
                if options.enable_thumbnails:
                    try:
                        thumbnails['preview'] = await self._generate_video_thumbnail(temp_path, metadata)
                        if metadata['duration'] > 10:
                            thumbnails['timeline'] = await self._generate_video_timeline(temp_path, metadata)
                    except Exception as e:
                        warnings.append(f"Video thumbnail generation failed: {str(e)}")
                
                # Video quality analysis
                quality_metrics = await self._analyze_video_quality(temp_path, metadata)
                
                # Process based on options
                if options.output_format == OutputFormat.OPTIMIZED:
                    # Optimize video using ffmpeg
                    quality_preset = self.quality_presets[options.quality]
                    
                    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as output_file:
                        (
                            ffmpeg
                            .input(temp_path)
                            .output(
                                output_file.name,
                                vcodec='libx264',
                                acodec='aac',
                                vb=f"{quality_preset['video_bitrate']}k",
                                ab='128k',
                                preset='medium'
                            )
                            .overwrite_output()
                            .run(quiet=True)
                        )
                        
                        with open(output_file.name, 'rb') as f:
                            processed_data = f.read()
                        
                        os.unlink(output_file.name)
                        
                        metadata['output_format'] = 'mp4'
                        metadata['video_bitrate'] = quality_preset['video_bitrate']
                        ai_enhancements.append("video_optimization")
                else:
                    processed_data = file_data
                
                return ProcessingResult(
                    success=True,
                    original_data=file_data,
                    processed_data=processed_data,
                    thumbnails=thumbnails,
                    metadata=metadata,
                    quality_metrics=quality_metrics,
                    processing_time=0,
                    file_size_reduction=0,
                    warnings=warnings,
                    errors=errors,
                    ai_enhancements=ai_enhancements
                )
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            self.logger.error(f"Video processing failed: {str(e)}")
            raise ProcessingError(f"Video processing failed: {str(e)}")
    
    async def _process_image_content(self, file_data: bytes, filename: str, 
                                   options: ProcessingOptions) -> ProcessingResult:
        """Process image content with enhancement and optimization"""



        try:
            warnings = []
            errors = []
            ai_enhancements = []
            thumbnails = {}
            
            # Load image using PIL
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(file_data)
                temp_file.flush()
                
                image = Image.open(temp_file.name)
                
                # Extract image metadata
                metadata = {
                    'width': image.width,
                    'height': image.height,
                    'mode': image.mode,
                    'format': image.format or Path(filename).suffix.upper().strip('.'),
                    'mime_type': mimetypes.guess_type(filename)[0],
                    'has_transparency': image.mode in ['RGBA', 'LA', 'P']
                }
                
                # AI-powered image enhancement
                if options.enable_ai_enhancement:
                    try:
                        # Auto color correction
                        enhancer = ImageEnhance.Color(image)
                        image = enhancer.enhance(1.1)
                        ai_enhancements.append("color_enhancement")
                        
                        # Sharpness enhancement
                        enhancer = ImageEnhance.Sharpness(image)
                        image = enhancer.enhance(1.1)
                        ai_enhancements.append("sharpness_enhancement")
                        
                        # Contrast enhancement
                        enhancer = ImageEnhance.Contrast(image)
                        image = enhancer.enhance(1.05)
                        ai_enhancements.append("contrast_enhancement")
                        
                    except Exception as e:
                        warnings.append(f"AI enhancement failed: {str(e)}")
                
                # Generate thumbnails
                if options.enable_thumbnails:
                    try:
                        # Standard thumbnail sizes
                        thumbnail_sizes = [(150, 150), (300, 300), (600, 600)]
                        for size in thumbnail_sizes:
                            thumb = image.copy()
                            thumb.thumbnail(size, Image.Resampling.LANCZOS)
                            
                            with tempfile.BytesIO() as thumb_buffer:
                                thumb.save(thumb_buffer, format='JPEG', quality=85)
                                thumbnails[f"thumb_{size[0]}x{size[1]}"] = thumb_buffer.getvalue()
                                
                    except Exception as e:
                        warnings.append(f"Thumbnail generation failed: {str(e)}")
                
                # Image quality analysis
                quality_metrics = await self._analyze_image_quality(image)
                
                # Process based on options
                if options.output_format == OutputFormat.OPTIMIZED:
                    quality_preset = self.quality_presets[options.quality]
                    
                    # Convert to optimal format
                    if image.mode in ['RGBA', 'LA']:
                        # Keep PNG for images with transparency
                        output_format = 'PNG'
                        save_kwargs = {'optimize': True}
                    else:
                        # Convert to JPEG for better compression
                        output_format = 'JPEG'
                        save_kwargs = {
                            'quality': quality_preset['image_quality'],
                            'optimize': True
                        }
                        # Convert to RGB if needed
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                    
                    with tempfile.BytesIO() as output_buffer:
                        image.save(output_buffer, format=output_format, **save_kwargs)
                        processed_data = output_buffer.getvalue()
                    
                    metadata['output_format'] = output_format.lower()
                    metadata['compression_quality'] = quality_preset['image_quality']
                    ai_enhancements.append("format_optimization")
                else:
                    processed_data = file_data
                
                return ProcessingResult(
                    success=True,
                    original_data=file_data,
                    processed_data=processed_data,
                    thumbnails=thumbnails,
                    metadata=metadata,
                    quality_metrics=quality_metrics,
                    processing_time=0,
                    file_size_reduction=0,
                    warnings=warnings,
                    errors=errors,
                    ai_enhancements=ai_enhancements
                )
                
        except Exception as e:
            self.logger.error(f"Image processing failed: {str(e)}")
            raise ProcessingError(f"Image processing failed: {str(e)}")
    
    async def _process_text_content(self, file_data: bytes, filename: str, 
                                  options: ProcessingOptions) -> ProcessingResult:
        """Process text content with NLP analysis and enhancement"""



        try:
            warnings = []
            errors = []
            ai_enhancements = []
            thumbnails = {}
            
            # Extract text content
            file_ext = Path(filename).suffix.lower()
            
            if file_ext == '.pdf':
                text_content = await self._extract_pdf_text(file_data)
            elif file_ext in ['.docx']:
                text_content = await self._extract_docx_text(file_data)
            else:
                # Plain text files
                try:
                    text_content = file_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text_content = file_data.decode('latin-1')
                    except UnicodeDecodeError:
                        text_content = file_data.decode('utf-8', errors='ignore')
                        warnings.append("Text encoding issues detected")
            
            # Extract basic metadata
            metadata = {
                'character_count': len(text_content),
                'word_count': len(text_content.split()),
                'line_count': len(text_content.split('\n')),
                'language': 'auto-detect',  # Would use language detection
                'format': file_ext,
                'mime_type': mimetypes.guess_type(filename)[0],
                'encoding': 'utf-8'
            }
            
            # AI-powered text analysis
            if options.enable_ai_enhancement and self.sentiment_analyzer:
                try:
                    # Sentiment analysis
                    if len(text_content) > 0 and len(text_content) < 10000:  # Limit for API
                        sentiment_result = self.sentiment_analyzer(text_content[:512])
                        metadata['sentiment'] = sentiment_result[0]['label']
                        metadata['sentiment_score'] = sentiment_result[0]['score']
                        ai_enhancements.append("sentiment_analysis")
                    
                    # Text summarization for longer texts
                    if len(text_content) > 100 and self.text_summarizer:
                        try:
                            summary = self.text_summarizer(text_content[:1024], max_length=150, min_length=50)
                            metadata['ai_summary'] = summary[0]['summary_text']
                            ai_enhancements.append("text_summarization")
                        except Exception as e:
                            warnings.append(f"Text summarization failed: {str(e)}")
                    
                except Exception as e:
                    warnings.append(f"AI text analysis failed: {str(e)}")
            
            # Text quality analysis
            quality_metrics = await self._analyze_text_quality(text_content)
            
            # Generate text preview thumbnail (word cloud or preview image)
            if options.enable_thumbnails:
                try:
                    thumbnails['preview'] = await self._generate_text_preview(text_content)
                except Exception as e:
                    warnings.append(f"Text preview generation failed: {str(e)}")
            
            # Process text (cleaning, formatting)
            processed_text = text_content
            if options.enable_ai_enhancement:
                # Basic text cleaning
                processed_text = self._clean_text(text_content)
                ai_enhancements.append("text_cleaning")
            
            # Convert back to bytes
            processed_data = processed_text.encode('utf-8')
            
            return ProcessingResult(
                success=True,
                original_data=file_data,
                processed_data=processed_data,
                thumbnails=thumbnails,
                metadata=metadata,
                quality_metrics=quality_metrics,
                processing_time=0,
                file_size_reduction=0,
                warnings=warnings,
                errors=errors,
                ai_enhancements=ai_enhancements
            )
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            raise ProcessingError(f"Text processing failed: {str(e)}")
    
    # Helper methods for content processing
    
    def _reduce_noise(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply noise reduction to audio"""



        try:
            # Simple spectral subtraction noise reduction
            # This is a basic implementation - in production, use more sophisticated methods
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise from first 0.5 seconds
            noise_frame_count = int(0.5 * sample_rate / 512)
            noise_spectrum = np.mean(magnitude[:, :noise_frame_count], axis=1, keepdims=True)
            
            # Spectral subtraction
            alpha = 2.0  # Over-subtraction factor
            cleaned_magnitude = magnitude - alpha * noise_spectrum
            cleaned_magnitude = np.maximum(cleaned_magnitude, 0.1 * magnitude)
            
            # Reconstruct audio
            cleaned_stft = cleaned_magnitude * np.exp(1j * phase)
            cleaned_audio = librosa.istft(cleaned_stft)
            
            return cleaned_audio
            
        except Exception:
            # Fallback to original audio if noise reduction fails
            return audio_data
    
    def _compress_dynamic_range(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply dynamic range compression"""



        try:
            # Simple compression using numpy
            threshold = 0.7
            ratio = 4.0
            
            # Find samples above threshold
            above_threshold = np.abs(audio_data) > threshold
            
            # Apply compression
            compressed = audio_data.copy()
            compressed[above_threshold] = (
                np.sign(audio_data[above_threshold]) * 
                (threshold + (np.abs(audio_data[above_threshold]) - threshold) / ratio)
            )
            
            return compressed
            
        except Exception:
            return audio_data
    
    async def _generate_waveform_thumbnail(self, audio_data: np.ndarray, sample_rate: int) -> bytes:
        """Generate waveform visualization thumbnail"""



        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            
            plt.figure(figsize=(10, 4))
            
            # Downsample for visualization
            downsample_factor = max(1, len(audio_data) // 2000)
            audio_downsampled = audio_data[::downsample_factor]
            time_axis = np.arange(len(audio_downsampled)) * downsample_factor / sample_rate
            
            plt.plot(time_axis, audio_downsampled, linewidth=0.5)
            plt.xlabel('Time (s)')
            plt.ylabel('Amplitude')
            plt.title('Waveform')
            plt.tight_layout()
            
            # Save to bytes
            with tempfile.BytesIO() as img_buffer:
                plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                return img_buffer.getvalue()
                
        except Exception as e:
            self.logger.warning(f"Waveform generation failed: {str(e)}")
            return b''
    
    async def _generate_spectrogram_thumbnail(self, audio_data: np.ndarray, sample_rate: int) -> bytes:
        """Generate spectrogram visualization thumbnail"""



        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            plt.figure(figsize=(10, 6))
            
            # Generate spectrogram
            stft = librosa.stft(audio_data)
            db_spectrogram = librosa.amplitude_to_db(np.abs(stft))
            
            librosa.display.specshow(
                db_spectrogram, 
                sr=sample_rate, 
                x_axis='time', 
                y_axis='hz',
                cmap='viridis'
            )
            
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram')
            plt.tight_layout()
            
            with tempfile.BytesIO() as img_buffer:
                plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                return img_buffer.getvalue()
                
        except Exception as e:
            self.logger.warning(f"Spectrogram generation failed: {str(e)}")
            return b''
    
    async def _generate_video_thumbnail(self, video_path: str, metadata: Dict) -> bytes:
        """Generate video thumbnail from middle frame"""



        try:
            # Extract frame from middle of video
            duration = metadata.get('duration', 10)
            timestamp = duration / 2
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as thumb_file:
                (
                    ffmpeg
                    .input(video_path, ss=timestamp)
                    .output(thumb_file.name, vframes=1, format='image2', vcodec='mjpeg')
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                with open(thumb_file.name, 'rb') as f:
                    thumbnail_data = f.read()
                
                os.unlink(thumb_file.name)
                return thumbnail_data
                
        except Exception as e:
            self.logger.warning(f"Video thumbnail generation failed: {str(e)}")
            return b''
    
    async def _generate_video_timeline(self, video_path: str, metadata: Dict) -> bytes:
        """Generate video timeline with multiple frames"""



        try:
            duration = metadata.get('duration', 10)
            frame_count = min(10, int(duration))
            
            frames = []
            for i in range(frame_count):
                timestamp = (duration / frame_count) * i
                
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as frame_file:
                    (
                        ffmpeg
                        .input(video_path, ss=timestamp)
                        .output(frame_file.name, vframes=1, format='image2', vcodec='mjpeg')
                        .overwrite_output()
                        .run(quiet=True)
                    )
                    
                    frame_img = Image.open(frame_file.name)
                    frame_img.thumbnail((150, 100), Image.Resampling.LANCZOS)
                    frames.append(frame_img)
                    
                    os.unlink(frame_file.name)
            
            # Create timeline image
            if frames:
                timeline_width = len(frames) * 150
                timeline_height = 100
                timeline = Image.new('RGB', (timeline_width, timeline_height), 'white')
                
                for i, frame in enumerate(frames):
                    timeline.paste(frame, (i * 150, 0))
                
                with tempfile.BytesIO() as timeline_buffer:
                    timeline.save(timeline_buffer, format='JPEG', quality=85)
                    return timeline_buffer.getvalue()
            
            return b''
            
        except Exception as e:
            self.logger.warning(f"Video timeline generation failed: {str(e)}")
            return b''
    
    async def _generate_text_preview(self, text_content: str) -> bytes:
        """Generate text preview image"""



        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            # Create simple text preview
            preview_text = text_content[:500] + "..." if len(text_content) > 500 else text_content
            
            plt.figure(figsize=(8, 6))
            plt.text(0.05, 0.95, preview_text, transform=plt.gca().transAxes, 
                    fontsize=10, verticalalignment='top', wrap=True)
            plt.axis('off')
            plt.tight_layout()
            
            with tempfile.BytesIO() as img_buffer:
                plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                return img_buffer.getvalue()
                
        except Exception as e:
            self.logger.warning(f"Text preview generation failed: {str(e)}")
            return b''
    
    async def _extract_pdf_text(self, pdf_data: bytes) -> str:
        """Extract text from PDF using PyMuPDF"""



        try:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            text_content = ""
            
            for page in doc:
                text_content += page.get_text()
            
            doc.close()
            return text_content
            
        except Exception as e:
            self.logger.warning(f"PDF text extraction failed: {str(e)}")
            return "PDF text extraction failed"
    
    async def _extract_docx_text(self, docx_data: bytes) -> str:
        """Extract text from DOCX file"""



        try:
            import docx
            
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(docx_data)
                temp_file.flush()
                
                doc = docx.Document(temp_file.name)
                text_content = ""
                
                for paragraph in doc.paragraphs:
                    text_content += paragraph.text + "\n"
                
                return text_content
                
        except Exception as e:
            self.logger.warning(f"DOCX text extraction failed: {str(e)}")
            return "DOCX text extraction failed"
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""



        try:
            import re
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove non-printable characters
            text = ''.join(char for char in text if char.isprintable() or char.isspace())
            
            # Normalize line endings
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            
            return text.strip()
            
        except Exception:
            return text
    
    async def _analyze_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze audio quality metrics"""



        try:
            metrics = {}
            
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio_data ** 2)
            noise_power = np.var(audio_data[:int(0.1 * sample_rate)])  # First 0.1s as noise
            snr = 10 * np.log10(signal_power / max(noise_power, 1e-10))
            metrics['snr_db'] = float(snr)
            
            # Dynamic range
            dynamic_range = np.max(np.abs(audio_data)) - np.min(np.abs(audio_data))
            metrics['dynamic_range'] = float(dynamic_range)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            metrics['zero_crossing_rate'] = float(np.mean(zcr))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            metrics['spectral_centroid'] = float(np.mean(spectral_centroids))
            
            # Overall quality score (0-100)
            quality_score = min(100, max(0, (snr + 20) * 2))  # Simple heuristic
            metrics['quality_score'] = quality_score
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Audio quality analysis failed: {str(e)}")
            return {'quality_score': 50.0}
    
    async def _analyze_video_quality(self, video_path: str, metadata: Dict) -> Dict[str, float]:
        """Analyze video quality metrics"""



        try:
            metrics = {}
            
            # Extract basic quality metrics from metadata
            width = metadata.get('width', 0)
            height = metadata.get('height', 0)
            fps = metadata.get('fps', 0)
            
            # Resolution quality score
            total_pixels = width * height
            if total_pixels >= 1920 * 1080:
                resolution_score = 100
            elif total_pixels >= 1280 * 720:
                resolution_score = 80
            elif total_pixels >= 854 * 480:
                resolution_score = 60
            else:
                resolution_score = 40
            
            metrics['resolution_score'] = resolution_score
            
            # Frame rate quality
            if fps >= 60:
                fps_score = 100
            elif fps >= 30:
                fps_score = 80
            elif fps >= 24:
                fps_score = 60
            else:
                fps_score = 40
            
            metrics['fps_score'] = fps_score
            
            # Overall quality score
            quality_score = (resolution_score + fps_score) / 2
            metrics['quality_score'] = quality_score
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Video quality analysis failed: {str(e)}")
            return {'quality_score': 50.0}
    
    async def _analyze_image_quality(self, image: Image.Image) -> Dict[str, float]:
        """Analyze image quality metrics"""



        try:
            metrics = {}
            
            # Resolution quality
            total_pixels = image.width * image.height
            if total_pixels >= 2000 * 2000:
                resolution_score = 100
            elif total_pixels >= 1000 * 1000:
                resolution_score = 80
            elif total_pixels >= 500 * 500:
                resolution_score = 60
            else:
                resolution_score = 40
            
            metrics['resolution_score'] = resolution_score
            
            # Color depth
            if image.mode == 'RGB':
                color_score = 100
            elif image.mode in ['RGBA', 'LA']:
                color_score = 90
            elif image.mode == 'L':
                color_score = 70
            else:
                color_score = 50
            
            metrics['color_score'] = color_score
            
            # Sharpness estimation (using Laplacian variance)
            if image.mode != 'L':
                gray_image = image.convert('L')
            else:
                gray_image = image
            
            # Convert to numpy array for analysis
            img_array = np.array(gray_image)
            laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
            sharpness_score = min(100, max(0, laplacian_var / 100))  # Normalize
            
            metrics['sharpness_score'] = sharpness_score
            
            # Overall quality score
            quality_score = (resolution_score + color_score + sharpness_score) / 3
            metrics['quality_score'] = quality_score
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Image quality analysis failed: {str(e)}")
            return {'quality_score': 50.0}
    
    async def _analyze_text_quality(self, text_content: str) -> Dict[str, float]:
        """Analyze text quality metrics"""



        try:
            metrics = {}
            
            # Basic text statistics
            word_count = len(text_content.split())
            char_count = len(text_content)
            sentence_count = len([s for s in text_content.split('.') if s.strip()])
            
            # Readability metrics
            avg_words_per_sentence = word_count / max(sentence_count, 1)
            avg_chars_per_word = char_count / max(word_count, 1)
            
            # Quality scoring
            if word_count > 100:
                length_score = 100
            elif word_count > 50:
                length_score = 80
            elif word_count > 10:
                length_score = 60
            else:
                length_score = 40
            
            # Readability score (simple heuristic)
            if 10 <= avg_words_per_sentence <= 20 and 4 <= avg_chars_per_word <= 6:
                readability_score = 100
            else:
                readability_score = max(50, 100 - abs(avg_words_per_sentence - 15) * 2)
            
            metrics['length_score'] = length_score
            metrics['readability_score'] = readability_score
            metrics['avg_words_per_sentence'] = avg_words_per_sentence
            metrics['avg_chars_per_word'] = avg_chars_per_word
            
            # Overall quality score
            quality_score = (length_score + readability_score) / 2
            metrics['quality_score'] = quality_score
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Text quality analysis failed: {str(e)}")
            return {'quality_score': 50.0}
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get all supported formats by content type"""



        return self.supported_formats.copy()
    
    def get_quality_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get quality presets configuration"""



        return {preset.value: config for preset, config in self.quality_presets.items()}
