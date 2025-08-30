"""
Content Validator - Multi-Format Content Validation Engine
==========================================================

Enterprise-grade content validation system supporting audio, video, image, text,
and multimedia content types with comprehensive quality checks and business rule validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

🔒 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 🔒
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is STRICTLY PROHIBITED and will be prosecuted under international copyright law.

Business Logic: Content upload → Format detection → Technical validation → 
Business rule validation → Quality scoring → Enhancement recommendations
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import mimetypes
from pathlib import Path
import tempfile
import os

# Media processing libraries
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageStat
    import librosa
    import soundfile as sf
    from moviepy.editor import VideoFileClip
    HAS_MEDIA_LIBS = True
except ImportError:
    HAS_MEDIA_LIBS = False

# Text processing libraries
import re
from textstat import flesch_reading_ease, flesch_kincaid_grade
import nltk
from langdetect import detect
import spacy


class ValidationLevel(Enum):
    """Validation intensity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    ENTERPRISE = "enterprise"


class ContentFormat(Enum):
    """Supported content formats"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MULTIMEDIA = "multimedia"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Content validation result structure"""
    format: ContentFormat
    is_valid: bool
    score: float
    technical_checks: Dict[str, Any]
    business_checks: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    issues: List[Dict[str, Any]]
    warnings: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class ContentValidator:
    """
    Enterprise content validation engine for multi-format content quality assessment.
    
    Provides comprehensive validation including technical specifications, business rules,
    quality metrics, and platform-specific requirements for creator content.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Validation thresholds
        self.audio_thresholds = {
            'min_sample_rate': 22050,
            'max_sample_rate': 192000,
            'min_bitrate': 128,
            'max_bitrate': 320,
            'min_duration': 5.0,
            'max_duration': 600.0,
            'min_rms_db': -60.0,
            'max_rms_db': -6.0,
            'max_peak_db': -0.1,
            'min_dynamic_range': 6.0,
            'max_silence_percentage': 0.15
        }
        
        self.video_thresholds = {
            'min_resolution': (480, 360),
            'max_resolution': (7680, 4320),  # 8K
            'min_fps': 15.0,
            'max_fps': 120.0,
            'min_bitrate': 500,  # kbps
            'max_bitrate': 50000,  # kbps
            'min_duration': 1.0,
            'max_duration': 3600.0,  # 1 hour
            'max_file_size': 2 * 1024 * 1024 * 1024,  # 2GB
            'supported_codecs': ['h264', 'h265', 'vp9', 'av1']
        }
        
        self.image_thresholds = {
            'min_resolution': (300, 300),
            'max_resolution': (8192, 8192),
            'min_dpi': 72,
            'recommended_dpi': 300,
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'supported_formats': ['JPEG', 'PNG', 'WEBP', 'TIFF'],
            'min_quality_score': 0.7,
            'max_compression_ratio': 0.95
        }
        
        self.text_thresholds = {
            'min_length': 10,
            'max_length': 50000,
            'min_readability_score': 30.0,
            'max_readability_score': 100.0,
            'min_grade_level': 1.0,
            'max_grade_level': 18.0,
            'max_spam_score': 0.3,
            'min_uniqueness_score': 0.8
        }
        
        # Platform-specific requirements
        self.platform_requirements = {
            'spotify': {
                'audio': {
                    'min_sample_rate': 44100,
                    'preferred_format': 'WAV',
                    'max_loudness_lufs': -14.0,
                    'min_duration': 30.0
                }
            },
            'youtube': {
                'video': {
                    'recommended_resolution': (1920, 1080),
                    'max_duration': 43200,  # 12 hours
                    'supported_formats': ['MP4', 'MOV', 'AVI', 'WMV']
                },
                'audio': {
                    'preferred_codec': 'AAC',
                    'recommended_bitrate': 128
                }
            },
            'instagram': {
                'image': {
                    'aspect_ratios': [(1, 1), (4, 5), (9, 16)],
                    'max_resolution': (1080, 1080),
                    'preferred_format': 'JPEG'
                },
                'video': {
                    'max_duration': 60.0,
                    'aspect_ratios': [(1, 1), (4, 5), (9, 16)]
                }
            },
            'tiktok': {
                'video': {
                    'preferred_aspect_ratio': (9, 16),
                    'max_duration': 180.0,
                    'min_resolution': (540, 960)
                }
            }
        }
        
        self.audio_thresholds = {
            'recommended_sample_rate': 44100,
            'min_bitrate': 128,
            'recommended_bitrate': 320,
            'max_duration': 3600,  # 1 hour
            'min_duration': 1,     # 1 second
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'supported_formats': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        }
        
        self.video_thresholds = {
            'min_resolution': (480, 360),
            'recommended_resolution': (1920, 1080),
            'min_fps': 15,
            'recommended_fps': 30,
            'max_duration': 7200,  # 2 hours
            'min_duration': 1,     # 1 second
            'max_file_size': 2 * 1024 * 1024 * 1024,  # 2GB
            'supported_formats': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        }
        
        self.image_thresholds = {
            'min_resolution': (400, 300),
            'recommended_resolution': (1920, 1080),
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'min_file_size': 1024,  # 1KB
            'supported_formats': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        }
        
        self.text_thresholds = {
            'min_length': 10,
            'max_length': 50000,
            'min_reading_ease': 30,
            'recommended_reading_ease': 60,
            'min_words': 5,
            'max_words': 10000
        }
        
        # Load NLP models if available
        self._load_nlp_models()
        
        self.logger.info("ContentValidator initialized successfully")
    
    def _load_nlp_models(self):
        """Load NLP models for text validation."""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Load spacy model for advanced text analysis
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("Spacy English model not found. Text analysis will be limited.")
                self.nlp = None
                
        except Exception as e:
            self.logger.warning(f"Failed to load NLP models: {str(e)}")
            self.nlp = None
    
    async def validate_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        requirements: Optional[Dict[str, Any]] = None,
        validation_level: str = "standard"
    ) -> ValidationResult:
        """
        Validate content based on type and requirements.
        
        Args:
            content_data: Content data to validate
            content_type: Type of content (audio, video, image, text, etc.)
            requirements: Optional custom validation requirements
            validation_level: Validation intensity level
            
        Returns:
            ValidationResult: Comprehensive validation results
        """
        try:
            self.logger.info(f"Starting content validation - Type: {content_type}, Level: {validation_level}")
            
            # Detect content format
            content_format = self._detect_content_format(content_data, content_type)
            
            # Initialize validation result
            result = ValidationResult(
                format=content_format,
                is_valid=True,
                score=1.0,
                technical_checks={},
                business_checks={},
                quality_metrics={},
                issues=[],
                warnings=[],
                recommendations=[],
                metadata={}
            )
            
            # Apply validation based on content format
            if content_format == ContentFormat.AUDIO:
                await self._validate_audio_content(content_data, result, requirements, validation_level)
            elif content_format == ContentFormat.VIDEO:
                await self._validate_video_content(content_data, result, requirements, validation_level)
            elif content_format == ContentFormat.IMAGE:
                await self._validate_image_content(content_data, result, requirements, validation_level)
            elif content_format == ContentFormat.TEXT:
                await self._validate_text_content(content_data, result, requirements, validation_level)
            elif content_format == ContentFormat.DOCUMENT:
                await self._validate_document_content(content_data, result, requirements, validation_level)
            elif content_format == ContentFormat.MULTIMEDIA:
                await self._validate_multimedia_content(content_data, result, requirements, validation_level)
            else:
                result.is_valid = False
                result.score = 0.0
                result.issues.append({
                    'type': 'error',
                    'message': f"Unsupported content format: {content_format.value}"
                })
            
            # Apply business rule validation
            await self._validate_business_rules(content_data, result, requirements)
            
            # Calculate final validation score
            result.score = self._calculate_validation_score(result)
            result.is_valid = result.score >= 0.6  # Minimum threshold for validity
            
            self.logger.info(f"Content validation completed - Score: {result.score:.3f}, Valid: {result.is_valid}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during content validation: {str(e)}")
            return ValidationResult(
                format=ContentFormat.UNKNOWN,
                is_valid=False,
                score=0.0,
                technical_checks={},
                business_checks={},
                quality_metrics={},
                issues=[{'type': 'error', 'message': f"Validation error: {str(e)}"}],
                warnings=[],
                recommendations=[],
                metadata={}
            )
    
    def _detect_content_format(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str
    ) -> ContentFormat:
        """Detect content format from data and type hint."""
        # Direct type mapping
        type_mapping = {
            'audio': ContentFormat.AUDIO,
            'video': ContentFormat.VIDEO,
            'image': ContentFormat.IMAGE,
            'text': ContentFormat.TEXT,
            'document': ContentFormat.DOCUMENT,
            'multimedia': ContentFormat.MULTIMEDIA
        }
        
        if content_type.lower() in type_mapping:
            return type_mapping[content_type.lower()]
        
        # Content-based detection
        if isinstance(content_data, str):
            if len(content_data) > 0:
                return ContentFormat.TEXT
        elif isinstance(content_data, bytes):
            # Basic magic number detection
            if content_data.startswith(b'\xff\xfb') or content_data.startswith(b'ID3'):
                return ContentFormat.AUDIO
            elif content_data.startswith(b'\x00\x00\x00\x20ftypmp4'):
                return ContentFormat.VIDEO
            elif content_data.startswith(b'\xff\xd8\xff') or content_data.startswith(b'\x89PNG'):
                return ContentFormat.IMAGE
        elif isinstance(content_data, dict):
            if 'type' in content_data:
                return self._detect_content_format(content_data.get('data', b''), content_data['type'])
        
        return ContentFormat.UNKNOWN
    
    async def _validate_audio_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        result: ValidationResult,
        requirements: Optional[Dict[str, Any]],
        validation_level: str
    ):
        """Validate audio content technical and quality specifications."""
        if not HAS_MEDIA_LIBS:
            result.warnings.append("Media processing libraries not available - limited audio validation")
            return
        
        try:
            # Get audio file path
            audio_path = self._get_file_path(content_data)
            if not audio_path:
                result.issues.append({'type': 'error', 'message': 'Cannot access audio file'})
                return
            
            # Load audio file
            try:
                audio_data, sample_rate = librosa.load(audio_path, sr=None)
                duration = len(audio_data) / sample_rate
            except Exception as e:
                result.issues.append({'type': 'error', 'message': f'Cannot load audio file: {str(e)}'})
                return
            
            # Technical validation
            technical_checks = {}
            
            # Sample rate validation
            if sample_rate < self.audio_thresholds['min_sample_rate']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Sample rate too low: {sample_rate}Hz (minimum: {self.audio_thresholds["min_sample_rate"]}Hz)'
                })
            elif sample_rate < self.audio_thresholds['recommended_sample_rate']:
                result.warnings.append(f'Sample rate below recommended: {sample_rate}Hz')
            
            technical_checks['sample_rate'] = sample_rate
            technical_checks['sample_rate_valid'] = sample_rate >= self.audio_thresholds['min_sample_rate']
            
            # Duration validation
            if duration < self.audio_thresholds['min_duration']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Audio too short: {duration:.2f}s (minimum: {self.audio_thresholds["min_duration"]}s)'
                })
            elif duration > self.audio_thresholds['max_duration']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Audio too long: {duration:.2f}s (maximum: {self.audio_thresholds["max_duration"]}s)'
                })
            
            technical_checks['duration'] = duration
            technical_checks['duration_valid'] = (
                self.audio_thresholds['min_duration'] <= duration <= self.audio_thresholds['max_duration']
            )
            
            # File size validation
            file_size = os.path.getsize(audio_path)
            if file_size > self.audio_thresholds['max_file_size']:
                result.issues.append({
                    'type': 'error',
                    'message': f'File size too large: {file_size / (1024*1024):.1f}MB'
                })
            
            technical_checks['file_size'] = file_size
            technical_checks['file_size_valid'] = file_size <= self.audio_thresholds['max_file_size']
            
            # Quality metrics (if comprehensive validation)
            quality_metrics = {}
            if validation_level in ['comprehensive', 'enterprise']:
                # RMS energy analysis
                rms = librosa.feature.rms(y=audio_data)
                quality_metrics['rms_energy'] = float(np.mean(rms))
                
                # Spectral centroid (brightness)
                spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
                quality_metrics['spectral_centroid'] = float(np.mean(spectral_centroid))
                
                # Zero crossing rate (indication of noisiness)
                zcr = librosa.feature.zero_crossing_rate(audio_data)
                quality_metrics['zero_crossing_rate'] = float(np.mean(zcr))
                
                # Signal-to-noise estimation
                signal_power = np.mean(audio_data ** 2)
                noise_floor = np.percentile(np.abs(audio_data), 10)
                snr_estimate = 10 * np.log10(signal_power / (noise_floor ** 2 + 1e-10))
                quality_metrics['snr_estimate'] = float(snr_estimate)
                
                # Quality warnings based on metrics
                if quality_metrics['rms_energy'] < 0.01:
                    result.warnings.append('Audio signal appears very quiet')
                elif quality_metrics['rms_energy'] > 0.5:
                    result.warnings.append('Audio signal may be too loud or clipped')
                
                if quality_metrics['snr_estimate'] < 20:
                    result.warnings.append('Poor signal-to-noise ratio detected')
            
            result.technical_checks.update(technical_checks)
            result.quality_metrics.update(quality_metrics)
            
            # Format validation
            file_ext = Path(audio_path).suffix.lower()
            if file_ext not in self.audio_thresholds['supported_formats']:
                result.warnings.append(f'Uncommon audio format: {file_ext}')
            
            result.metadata.update({
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[0],
                'file_size': file_size,
                'format': file_ext
            })
            
        except Exception as e:
            result.issues.append({'type': 'error', 'message': f'Audio validation error: {str(e)}'})
    
    async def _validate_video_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        result: ValidationResult,
        requirements: Optional[Dict[str, Any]],
        validation_level: str
    ):
        """Validate video content technical and quality specifications."""
        if not HAS_MEDIA_LIBS:
            result.warnings.append("Media processing libraries not available - limited video validation")
            return
        
        try:
            # Get video file path
            video_path = self._get_file_path(content_data)
            if not video_path:
                result.issues.append({'type': 'error', 'message': 'Cannot access video file'})
                return
            
            # Load video file
            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    result.issues.append({'type': 'error', 'message': 'Cannot open video file'})
                    return
                
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
            except Exception as e:
                result.issues.append({'type': 'error', 'message': f'Cannot analyze video file: {str(e)}'})
                return
            finally:
                if 'cap' in locals():
                    cap.release()
            
            # Technical validation
            technical_checks = {}
            
            # Resolution validation
            min_width, min_height = self.video_thresholds['min_resolution']
            if width < min_width or height < min_height:
                result.issues.append({
                    'type': 'error',
                    'message': f'Resolution too low: {width}x{height} (minimum: {min_width}x{min_height})'
                })
            
            rec_width, rec_height = self.video_thresholds['recommended_resolution']
            if width < rec_width or height < rec_height:
                result.warnings.append(f'Resolution below recommended: {width}x{height}')
            
            technical_checks['resolution'] = (width, height)
            technical_checks['resolution_valid'] = width >= min_width and height >= min_height
            
            # FPS validation
            if fps < self.video_thresholds['min_fps']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Frame rate too low: {fps:.1f}fps (minimum: {self.video_thresholds["min_fps"]}fps)'
                })
            elif fps < self.video_thresholds['recommended_fps']:
                result.warnings.append(f'Frame rate below recommended: {fps:.1f}fps')
            
            technical_checks['fps'] = fps
            technical_checks['fps_valid'] = fps >= self.video_thresholds['min_fps']
            
            # Duration validation
            if duration < self.video_thresholds['min_duration']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Video too short: {duration:.2f}s (minimum: {self.video_thresholds["min_duration"]}s)'
                })
            elif duration > self.video_thresholds['max_duration']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Video too long: {duration:.2f}s (maximum: {self.video_thresholds["max_duration"]}s)'
                })
            
            technical_checks['duration'] = duration
            technical_checks['duration_valid'] = (
                self.video_thresholds['min_duration'] <= duration <= self.video_thresholds['max_duration']
            )
            
            # File size validation
            file_size = os.path.getsize(video_path)
            if file_size > self.video_thresholds['max_file_size']:
                result.issues.append({
                    'type': 'error',
                    'message': f'File size too large: {file_size / (1024*1024*1024):.1f}GB'
                })
            
            technical_checks['file_size'] = file_size
            technical_checks['file_size_valid'] = file_size <= self.video_thresholds['max_file_size']
            
            # Quality metrics (if comprehensive validation)
            quality_metrics = {}
            if validation_level in ['comprehensive', 'enterprise']:
                # Sample frames for quality analysis
                cap = cv2.VideoCapture(video_path)
                sample_frames = []
                frame_interval = max(1, int(frame_count / 10))  # Sample 10 frames
                
                for i in range(0, int(frame_count), frame_interval):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if ret:
                        sample_frames.append(frame)
                    if len(sample_frames) >= 10:
                        break
                
                cap.release()
                
                if sample_frames:
                    # Sharpness analysis
                    sharpness_scores = []
                    brightness_scores = []
                    
                    for frame in sample_frames:
                        # Sharpness (Laplacian variance)
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                        sharpness_scores.append(sharpness)
                        
                        # Brightness
                        brightness = np.mean(gray)
                        brightness_scores.append(brightness)
                    
                    quality_metrics['avg_sharpness'] = float(np.mean(sharpness_scores))
                    quality_metrics['avg_brightness'] = float(np.mean(brightness_scores))
                    quality_metrics['brightness_consistency'] = float(np.std(brightness_scores))
                    
                    # Quality warnings
                    if quality_metrics['avg_sharpness'] < 100:
                        result.warnings.append('Video appears blurry or lacks sharpness')
                    
                    if quality_metrics['avg_brightness'] < 50:
                        result.warnings.append('Video appears too dark')
                    elif quality_metrics['avg_brightness'] > 200:
                        result.warnings.append('Video appears overexposed')
            
            result.technical_checks.update(technical_checks)
            result.quality_metrics.update(quality_metrics)
            
            # Format validation
            file_ext = Path(video_path).suffix.lower()
            if file_ext not in self.video_thresholds['supported_formats']:
                result.warnings.append(f'Uncommon video format: {file_ext}')
            
            result.metadata.update({
                'duration': duration,
                'resolution': (width, height),
                'fps': fps,
                'frame_count': frame_count,
                'file_size': file_size,
                'format': file_ext
            })
            
        except Exception as e:
            result.issues.append({'type': 'error', 'message': f'Video validation error: {str(e)}'})
    
    async def _validate_image_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        result: ValidationResult,
        requirements: Optional[Dict[str, Any]],
        validation_level: str
    ):
        """Validate image content technical and quality specifications."""
        try:
            # Get image file path or data
            if isinstance(content_data, bytes):
                # Create temporary file for bytes data
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(content_data)
                    image_path = tmp_file.name
            else:
                image_path = self._get_file_path(content_data)
            
            if not image_path:
                result.issues.append({'type': 'error', 'message': 'Cannot access image file'})
                return
            
            # Load image
            try:
                image = Image.open(image_path)
                width, height = image.size
                format_name = image.format
                mode = image.mode
                
            except Exception as e:
                result.issues.append({'type': 'error', 'message': f'Cannot load image file: {str(e)}'})
                return
            
            # Technical validation
            technical_checks = {}
            
            # Resolution validation
            min_width, min_height = self.image_thresholds['min_resolution']
            if width < min_width or height < min_height:
                result.issues.append({
                    'type': 'error',
                    'message': f'Resolution too low: {width}x{height} (minimum: {min_width}x{min_height})'
                })
            
            rec_width, rec_height = self.image_thresholds['recommended_resolution']
            if width < rec_width or height < rec_height:
                result.warnings.append(f'Resolution below recommended: {width}x{height}')
            
            technical_checks['resolution'] = (width, height)
            technical_checks['resolution_valid'] = width >= min_width and height >= min_height
            
            # File size validation
            file_size = os.path.getsize(image_path)
            if file_size > self.image_thresholds['max_file_size']:
                result.issues.append({
                    'type': 'error',
                    'message': f'File size too large: {file_size / (1024*1024):.1f}MB'
                })
            elif file_size < self.image_thresholds['min_file_size']:
                result.warnings.append(f'File size very small: {file_size}B')
            
            technical_checks['file_size'] = file_size
            technical_checks['file_size_valid'] = (
                self.image_thresholds['min_file_size'] <= file_size <= self.image_thresholds['max_file_size']
            )
            
            # Quality metrics (if comprehensive validation)
            quality_metrics = {}
            if validation_level in ['comprehensive', 'enterprise']:
                try:
                    # Convert to numpy array for analysis
                    img_array = np.array(image)
                    
                    if len(img_array.shape) == 3:  # Color image
                        # Sharpness analysis using Laplacian variance
                        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                        quality_metrics['sharpness'] = float(sharpness)
                        
                        # Color analysis
                        color_std = np.std(img_array, axis=(0, 1))
                        quality_metrics['color_variance'] = float(np.mean(color_std))
                        
                        # Brightness analysis
                        brightness = np.mean(gray)
                        quality_metrics['brightness'] = float(brightness)
                        
                    elif len(img_array.shape) == 2:  # Grayscale image
                        sharpness = cv2.Laplacian(img_array, cv2.CV_64F).var()
                        quality_metrics['sharpness'] = float(sharpness)
                        
                        brightness = np.mean(img_array)
                        quality_metrics['brightness'] = float(brightness)
                    
                    # Aspect ratio analysis
                    aspect_ratio = width / height
                    quality_metrics['aspect_ratio'] = aspect_ratio
                    
                    # Common aspect ratios
                    standard_ratios = [16/9, 4/3, 1/1, 3/2, 2/3, 9/16]
                    closest_ratio = min(standard_ratios, key=lambda r: abs(r - aspect_ratio))
                    ratio_difference = abs(aspect_ratio - closest_ratio)
                    
                    if ratio_difference > 0.1:
                        result.warnings.append(f'Unusual aspect ratio: {aspect_ratio:.2f}')
                    
                    # Quality warnings
                    if 'sharpness' in quality_metrics and quality_metrics['sharpness'] < 100:
                        result.warnings.append('Image appears blurry or lacks sharpness')
                    
                    if 'brightness' in quality_metrics:
                        if quality_metrics['brightness'] < 50:
                            result.warnings.append('Image appears too dark')
                        elif quality_metrics['brightness'] > 200:
                            result.warnings.append('Image appears overexposed')
                    
                except Exception as e:
                    result.warnings.append(f'Could not perform advanced quality analysis: {str(e)}')
            
            result.technical_checks.update(technical_checks)
            result.quality_metrics.update(quality_metrics)
            
            # Format validation
            file_ext = Path(image_path).suffix.lower()
            if file_ext not in self.image_thresholds['supported_formats']:
                result.warnings.append(f'Uncommon image format: {file_ext}')
            
            result.metadata.update({
                'resolution': (width, height),
                'file_size': file_size,
                'format': format_name,
                'mode': mode,
                'extension': file_ext
            })
            
            # Clean up temporary file if created
            if isinstance(content_data, bytes) and os.path.exists(image_path):
                os.unlink(image_path)
            
        except Exception as e:
            result.issues.append({'type': 'error', 'message': f'Image validation error: {str(e)}'})
    
    async def _validate_text_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        result: ValidationResult,
        requirements: Optional[Dict[str, Any]],
        validation_level: str
    ):
        """Validate text content quality, readability, and compliance."""
        try:
            # Extract text content
            if isinstance(content_data, str):
                text = content_data
            elif isinstance(content_data, bytes):
                text = content_data.decode('utf-8', errors='ignore')
            elif isinstance(content_data, dict):
                text = content_data.get('text', '') or content_data.get('content', '')
            else:
                text = str(content_data)
            
            # Basic text metrics
            text_length = len(text)
            word_count = len(text.split())
            sentence_count = text.count('.') + text.count('!') + text.count('?')
            paragraph_count = text.count('\n\n') + 1
            
            # Technical validation
            technical_checks = {}
            
            # Length validation
            if text_length < self.text_thresholds['min_length']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Text too short: {text_length} characters (minimum: {self.text_thresholds["min_length"]})'
                })
            elif text_length > self.text_thresholds['max_length']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Text too long: {text_length} characters (maximum: {self.text_thresholds["max_length"]})'
                })
            
            technical_checks['length'] = text_length
            technical_checks['length_valid'] = (
                self.text_thresholds['min_length'] <= text_length <= self.text_thresholds['max_length']
            )
            
            # Word count validation
            if word_count < self.text_thresholds['min_words']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Too few words: {word_count} (minimum: {self.text_thresholds["min_words"]})'
                })
            elif word_count > self.text_thresholds['max_words']:
                result.issues.append({
                    'type': 'error',
                    'message': f'Too many words: {word_count} (maximum: {self.text_thresholds["max_words"]})'
                })
            
            technical_checks['word_count'] = word_count
            technical_checks['word_count_valid'] = (
                self.text_thresholds['min_words'] <= word_count <= self.text_thresholds['max_words']
            )
            
            # Quality metrics
            quality_metrics = {}
            
            try:
                # Readability analysis
                reading_ease = flesch_reading_ease(text)
                reading_grade = flesch_kincaid_grade(text)
                
                quality_metrics['reading_ease'] = reading_ease
                quality_metrics['reading_grade'] = reading_grade
                
                if reading_ease < self.text_thresholds['min_reading_ease']:
                    result.warnings.append(f'Text may be difficult to read (score: {reading_ease:.1f})')
                elif reading_ease < self.text_thresholds['recommended_reading_ease']:
                    result.warnings.append(f'Text readability could be improved (score: {reading_ease:.1f})')
                
            except Exception as e:
                result.warnings.append(f'Could not calculate readability metrics: {str(e)}')
            
            # Language detection
            try:
                language = detect(text)
                quality_metrics['language'] = language
                
                if language != 'en':
                    result.warnings.append(f'Non-English content detected: {language}')
            except Exception:
                quality_metrics['language'] = 'unknown'
            
            # Advanced text analysis (if comprehensive validation)
            if validation_level in ['comprehensive', 'enterprise'] and self.nlp:
                try:
                    # Spacy analysis
                    doc = self.nlp(text[:1000000])  # Limit to 1M chars for performance
                    
                    # Entity recognition
                    entities = [(ent.text, ent.label_) for ent in doc.ents]
                    quality_metrics['entities'] = entities[:20]  # Limit entities
                    
                    # Sentiment analysis (basic)
                    positive_words = sum(1 for token in doc if token.sentiment > 0)
                    negative_words = sum(1 for token in doc if token.sentiment < 0)
                    sentiment_ratio = positive_words / (negative_words + 1)
                    quality_metrics['sentiment_ratio'] = sentiment_ratio
                    
                    # Grammar and style checks
                    grammar_issues = []
                    
                    # Check for excessive repetition
                    words = [token.lemma_.lower() for token in doc if token.is_alpha]
                    word_freq = {}
                    for word in words:
                        word_freq[word] = word_freq.get(word, 0) + 1
                    
                    repeated_words = [word for word, freq in word_freq.items() 
                                    if freq > len(words) * 0.05 and len(word) > 3]
                    
                    if repeated_words:
                        grammar_issues.append(f"Excessive repetition detected: {', '.join(repeated_words[:5])}")
                    
                    # Check sentence length variation
                    sentence_lengths = [len(sent.text.split()) for sent in doc.sents]
                    if sentence_lengths:
                        avg_length = np.mean(sentence_lengths)
                        length_std = np.std(sentence_lengths)
                        
                        if length_std < 3:
                            grammar_issues.append("Sentences lack length variation")
                        
                        if avg_length > 25:
                            grammar_issues.append("Average sentence length too long")
                    
                    quality_metrics['grammar_issues'] = grammar_issues
                    
                    if grammar_issues:
                        result.warnings.extend(grammar_issues)
                    
                except Exception as e:
                    result.warnings.append(f'Advanced text analysis failed: {str(e)}')
            
            # Basic formatting checks
            formatting_issues = []
            
            # Check for proper capitalization
            if not text[0].isupper() and text[0].isalpha():
                formatting_issues.append("Text should start with capital letter")
            
            # Check for multiple spaces
            if '  ' in text:
                formatting_issues.append("Multiple consecutive spaces found")
            
            # Check for proper punctuation
            if not any(text.endswith(p) for p in '.!?'):
                formatting_issues.append("Text should end with proper punctuation")
            
            quality_metrics['formatting_issues'] = formatting_issues
            
            if formatting_issues:
                result.warnings.extend(formatting_issues)
            
            result.technical_checks.update(technical_checks)
            result.quality_metrics.update(quality_metrics)
            
            result.metadata.update({
                'length': text_length,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'paragraph_count': paragraph_count,
                'language': quality_metrics.get('language', 'unknown')
            })
            
        except Exception as e:
            result.issues.append({'type': 'error', 'message': f'Text validation error: {str(e)}'})
    
    async def _validate_document_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        result: ValidationResult,
        requirements: Optional[Dict[str, Any]],
        validation_level: str
    ):
        """Validate document content (PDF, Word, etc.)."""
        # Document validation would require additional libraries like PyPDF2, python-docx
        result.warnings.append("Document validation not fully implemented - performing basic checks")
        
        # Basic file validation
        if isinstance(content_data, bytes):
            file_size = len(content_data)
            result.metadata['file_size'] = file_size
            
            # Basic format detection
            if content_data.startswith(b'%PDF'):
                result.metadata['format'] = 'PDF'
            elif content_data.startswith(b'PK'):
                result.metadata['format'] = 'Office Document'
            else:
                result.metadata['format'] = 'Unknown'
        
        result.technical_checks['format_detected'] = True
    
    async def _validate_multimedia_content(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        result: ValidationResult,
        requirements: Optional[Dict[str, Any]],
        validation_level: str
    ):
        """Validate multimedia content (combinations of different formats)."""
        if isinstance(content_data, dict):
            # Validate each component separately
            for component_type, component_data in content_data.items():
                if component_type in ['audio', 'video', 'image', 'text']:
                    component_result = await self.validate_content(
                        component_data, component_type, requirements, validation_level
                    )
                    
                    # Merge results
                    result.technical_checks[f'{component_type}_validation'] = component_result.technical_checks
                    result.quality_metrics[f'{component_type}_metrics'] = component_result.quality_metrics
                    result.issues.extend([
                        {**issue, 'component': component_type} for issue in component_result.issues
                    ])
                    result.warnings.extend([
                        f'{component_type}: {warning}' for warning in component_result.warnings
                    ])
        else:
            result.warnings.append("Multimedia content format not recognized")
    
    async def _validate_business_rules(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        result: ValidationResult,
        requirements: Optional[Dict[str, Any]]
    ):
        """Validate content against business rules and platform requirements."""
        business_checks = {}
        
        # Platform-specific requirements
        if requirements:
            # SEO requirements
            if 'seo' in requirements:
                seo_reqs = requirements['seo']
                if 'min_keywords' in seo_reqs and result.format == ContentFormat.TEXT:
                    # Basic keyword density check
                    text = str(content_data) if not isinstance(content_data, str) else content_data
                    keywords = seo_reqs.get('keywords', [])
                    
                    keyword_density = {}
                    for keyword in keywords:
                        count = text.lower().count(keyword.lower())
                        density = count / len(text.split()) if text.split() else 0
                        keyword_density[keyword] = density
                    
                    business_checks['seo_keyword_density'] = keyword_density
                    
                    # Check minimum keyword presence
                    min_density = seo_reqs.get('min_density', 0.01)
                    missing_keywords = [k for k, d in keyword_density.items() if d < min_density]
                    
                    if missing_keywords:
                        result.warnings.append(f'Low keyword density for: {", ".join(missing_keywords)}')
            
            # Content protection requirements
            if 'protection' in requirements:
                protection_reqs = requirements['protection']
                
                # Check for watermark compatibility
                if result.format in [ContentFormat.IMAGE, ContentFormat.VIDEO]:
                    if protection_reqs.get('watermark_required', False):
                        business_checks['watermark_compatible'] = True
                        result.recommendations.append('Consider adding digital watermark for protection')
                
                # Check for metadata preservation
                if protection_reqs.get('metadata_preservation', True):
                    business_checks['metadata_preserved'] = True
            
            # Monetization requirements
            if 'monetization' in requirements:
                monetization_reqs = requirements['monetization']
                
                # Check content quality for monetization eligibility
                min_quality = monetization_reqs.get('min_quality_score', 0.7)
                if result.score < min_quality:
                    result.warnings.append(f'Content quality below monetization threshold: {result.score:.3f}')
                
                business_checks['monetization_eligible'] = result.score >= min_quality
        
        # General business rules
        business_checks['platform_compatible'] = len(result.issues) == 0
        business_checks['quality_acceptable'] = result.score >= 0.6
        
        result.business_checks.update(business_checks)
    
    def _get_file_path(self, content_data: Union[bytes, str, Dict[str, Any]]) -> Optional[str]:
        """Extract file path from content data."""
        if isinstance(content_data, str) and os.path.exists(content_data):
            return content_data
        elif isinstance(content_data, dict):
            return content_data.get('file_path') or content_data.get('path')
        return None
    
    def _calculate_validation_score(self, result: ValidationResult) -> float:
        """Calculate overall validation score from all checks."""
        scores = []
        
        # Technical checks score
        if result.technical_checks:
            valid_checks = sum(1 for check in result.technical_checks.values() 
                             if isinstance(check, bool) and check)
            total_checks = sum(1 for check in result.technical_checks.values() 
                             if isinstance(check, bool))
            
            if total_checks > 0:
                scores.append(valid_checks / total_checks)
        
        # Quality metrics score (normalized)
        if result.quality_metrics:
            quality_score = 0.8  # Default good quality
            
            # Adjust based on specific quality indicators
            if result.format == ContentFormat.AUDIO:
                if 'snr_estimate' in result.quality_metrics:
                    snr = result.quality_metrics['snr_estimate']
                    quality_score = min(1.0, max(0.3, (snr + 20) / 40))
            elif result.format == ContentFormat.VIDEO:
                if 'avg_sharpness' in result.quality_metrics:
                    sharpness = result.quality_metrics['avg_sharpness']
                    quality_score = min(1.0, max(0.3, sharpness / 500))
            elif result.format == ContentFormat.IMAGE:
                if 'sharpness' in result.quality_metrics:
                    sharpness = result.quality_metrics['sharpness']
                    quality_score = min(1.0, max(0.3, sharpness / 500))
            elif result.format == ContentFormat.TEXT:
                if 'reading_ease' in result.quality_metrics:
                    ease = result.quality_metrics['reading_ease']
                    quality_score = min(1.0, max(0.3, ease / 100))
            
            scores.append(quality_score)
        
        # Business checks score
        if result.business_checks:
            valid_business = sum(1 for check in result.business_checks.values() 
                               if isinstance(check, bool) and check)
            total_business = sum(1 for check in result.business_checks.values() 
                               if isinstance(check, bool))
            
            if total_business > 0:
                scores.append(valid_business / total_business)
        
        # Penalty for critical issues
        critical_issues = sum(1 for issue in result.issues if issue.get('type') == 'error')
        issue_penalty = min(0.5, critical_issues * 0.1)
        
        # Calculate final score
        if scores:
            base_score = sum(scores) / len(scores)
        else:
            base_score = 0.5  # Default neutral score
        
        final_score = max(0.0, base_score - issue_penalty)
        
        return round(final_score, 3)


class AudioQualityValidator:
    """
    Specialized audio quality validator for music creators and audio content.
    
    Performs advanced audio analysis including spectral analysis, loudness measurement,
    dynamic range analysis, and platform-specific audio quality checks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.AudioQualityValidator")
        
        # Audio quality thresholds
        self.quality_thresholds = {
            'min_snr_db': 20.0,
            'max_thd_percent': 5.0,
            'min_frequency_range': 50.0,  # Hz
            'max_frequency_range': 20000.0,  # Hz
            'min_dynamic_range': 6.0,  # dB
            'target_loudness_lufs': -23.0,
            'max_peak_db': -1.0,
            'min_stereo_width': 0.3
        }
    
    async def validate_audio_quality(
        self,
        audio_data: Union[bytes, str],
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive audio quality analysis."""
        if not HAS_MEDIA_LIBS:
            return {'error': 'Audio processing libraries not available'}
        
        try:
            # Load audio file
            if isinstance(audio_data, str):
                y, sr = librosa.load(audio_data, sr=None)
            else:
                # Handle bytes data
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                y, sr = librosa.load(tmp_path, sr=None)
                os.unlink(tmp_path)
            
            quality_metrics = {}
            
            # Basic audio properties
            duration = len(y) / sr
            quality_metrics['duration_seconds'] = duration
            quality_metrics['sample_rate'] = sr
            quality_metrics['channels'] = 1 if y.ndim == 1 else y.shape[0]
            
            # RMS and peak analysis
            rms = librosa.feature.rms(y=y)[0]
            rms_db = 20 * np.log10(np.mean(rms) + 1e-10)
            peak_db = 20 * np.log10(np.max(np.abs(y)) + 1e-10)
            
            quality_metrics['rms_db'] = float(rms_db)
            quality_metrics['peak_db'] = float(peak_db)
            quality_metrics['dynamic_range_db'] = float(peak_db - rms_db)
            
            # Signal-to-noise ratio estimation
            # Use spectral subtraction approach
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            noise_floor = np.percentile(magnitude, 10)
            signal_peak = np.percentile(magnitude, 90)
            snr_estimate = 20 * np.log10((signal_peak + 1e-10) / (noise_floor + 1e-10))
            quality_metrics['snr_estimate'] = float(snr_estimate)
            
            # Frequency analysis
            fft = np.fft.fft(y)
            freqs = np.fft.fftfreq(len(fft), 1/sr)
            magnitude_spectrum = np.abs(fft)
            
            # Find frequency range with significant energy
            energy_threshold = np.max(magnitude_spectrum) * 0.01
            significant_freqs = freqs[magnitude_spectrum > energy_threshold]
            
            if len(significant_freqs) > 0:
                freq_min = np.min(np.abs(significant_freqs))
                freq_max = np.max(np.abs(significant_freqs))
                quality_metrics['frequency_range_min'] = float(freq_min)
                quality_metrics['frequency_range_max'] = float(freq_max)
                quality_metrics['frequency_bandwidth'] = float(freq_max - freq_min)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            quality_metrics['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            quality_metrics['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            quality_metrics['zero_crossing_rate_mean'] = float(np.mean(zero_crossing_rate))
            
            # Silence detection
            silence_threshold = np.max(np.abs(y)) * 0.01
            silence_frames = np.abs(y) < silence_threshold
            silence_percentage = np.sum(silence_frames) / len(y)
            quality_metrics['silence_percentage'] = float(silence_percentage)
            
            # Clipping detection
            clipping_threshold = 0.99
            clipped_samples = np.abs(y) >= clipping_threshold
            clipping_percentage = np.sum(clipped_samples) / len(y)
            quality_metrics['clipping_percentage'] = float(clipping_percentage)
            
            # Audio quality score calculation
            quality_score = self._calculate_audio_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = quality_score
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Audio quality validation failed: {str(e)}")
            return {'error': f'Audio validation failed: {str(e)}'}
    
    def _calculate_audio_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall audio quality score based on multiple factors."""
        score_components = []
        
        # SNR score (0-1)
        if 'snr_estimate' in metrics:
            snr = metrics['snr_estimate']
            snr_score = min(1.0, max(0.0, (snr - 10) / 40))  # 10-50 dB range
            score_components.append(snr_score * 0.3)
        
        # Dynamic range score (0-1)
        if 'dynamic_range_db' in metrics:
            dr = metrics['dynamic_range_db']
            dr_score = min(1.0, max(0.0, (dr - 6) / 30))  # 6-36 dB range
            score_components.append(dr_score * 0.2)
        
        # Frequency bandwidth score (0-1)
        if 'frequency_bandwidth' in metrics:
            bandwidth = metrics['frequency_bandwidth']
            bandwidth_score = min(1.0, max(0.0, (bandwidth - 1000) / 19000))  # 1-20 kHz range
            score_components.append(bandwidth_score * 0.2)
        
        # Clipping penalty
        if 'clipping_percentage' in metrics:
            clipping = metrics['clipping_percentage']
            clipping_penalty = min(1.0, clipping * 10)  # Heavy penalty for clipping
            score_components.append((1.0 - clipping_penalty) * 0.15)
        
        # Silence penalty
        if 'silence_percentage' in metrics:
            silence = metrics['silence_percentage']
            silence_penalty = min(1.0, max(0.0, (silence - 0.05) * 5))  # Penalty for >5% silence
            score_components.append((1.0 - silence_penalty) * 0.15)
        
        return sum(score_components) if score_components else 0.5


class VideoQualityValidator:
    """
    Specialized video quality validator for content creators.
    
    Performs advanced video analysis including resolution assessment, frame rate analysis,
    motion detection, color grading evaluation, and platform-specific video quality checks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.VideoQualityValidator")
        
        # Video quality thresholds
        self.quality_thresholds = {
            'min_sharpness': 100.0,
            'max_noise_variance': 1000.0,
            'min_contrast_ratio': 2.0,
            'max_motion_blur_threshold': 50.0,
            'min_color_depth': 8,
            'target_aspect_ratios': [(16, 9), (4, 3), (1, 1), (9, 16)]
        }
    
    async def validate_video_quality(
        self,
        video_data: Union[bytes, str],
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive video quality analysis."""
        if not HAS_MEDIA_LIBS:
            return {'error': 'Video processing libraries not available'}
        
        try:
            # Load video file
            if isinstance(video_data, str):
                video_path = video_data
            else:
                # Handle bytes data
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                    tmp_file.write(video_data)
                    video_path = tmp_file.name
            
            # Open video with OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {'error': 'Could not open video file'}
            
            quality_metrics = {}
            
            # Basic video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            quality_metrics.update({
                'resolution_width': width,
                'resolution_height': height,
                'frame_count': frame_count,
                'fps': fps,
                'duration_seconds': duration,
                'aspect_ratio': width / height if height > 0 else 0
            })
            
            # Sample frames for analysis (max 30 frames)
            sample_frames = min(30, frame_count)
            frame_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
            
            sharpness_scores = []
            noise_variances = []
            brightness_values = []
            contrast_values = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Sharpness assessment using Laplacian variance
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                sharpness_scores.append(laplacian_var)
                
                # Noise estimation using local variance
                blur_kernel = cv2.GaussianBlur(gray, (5, 5), 0)
                noise = cv2.subtract(gray, blur_kernel)
                noise_variance = np.var(noise)
                noise_variances.append(noise_variance)
                
                # Brightness and contrast
                brightness = np.mean(gray)
                contrast = np.std(gray)
                brightness_values.append(brightness)
                contrast_values.append(contrast)
            
            cap.release()
            
            # Calculate quality metrics
            if sharpness_scores:
                quality_metrics['avg_sharpness'] = float(np.mean(sharpness_scores))
                quality_metrics['min_sharpness'] = float(np.min(sharpness_scores))
                quality_metrics['sharpness_std'] = float(np.std(sharpness_scores))
            
            if noise_variances:
                quality_metrics['avg_noise_variance'] = float(np.mean(noise_variances))
                quality_metrics['max_noise_variance'] = float(np.max(noise_variances))
            
            if brightness_values:
                quality_metrics['avg_brightness'] = float(np.mean(brightness_values))
                quality_metrics['brightness_std'] = float(np.std(brightness_values))
            
            if contrast_values:
                quality_metrics['avg_contrast'] = float(np.mean(contrast_values))
                quality_metrics['contrast_std'] = float(np.std(contrast_values))
            
            # Video codec and format information
            try:
                video_clip = VideoFileClip(video_path)
                quality_metrics['video_codec'] = video_clip.filename
                quality_metrics['has_audio'] = video_clip.audio is not None
                video_clip.close()
            except Exception as e:
                self.logger.warning(f"Could not extract codec info: {str(e)}")
            
            # Clean up temporary file
            if isinstance(video_data, bytes) and os.path.exists(video_path):
                os.unlink(video_path)
            
            # Calculate overall quality score
            quality_score = self._calculate_video_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = quality_score
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Video quality validation failed: {str(e)}")
            return {'error': f'Video validation failed: {str(e)}'}
    
    def _calculate_video_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall video quality score based on multiple factors."""
        score_components = []
        
        # Sharpness score (0-1)
        if 'avg_sharpness' in metrics:
            sharpness = metrics['avg_sharpness']
            sharpness_score = min(1.0, max(0.0, (sharpness - 50) / 450))  # 50-500 range
            score_components.append(sharpness_score * 0.4)
        
        # Noise score (0-1, lower noise is better)
        if 'avg_noise_variance' in metrics:
            noise = metrics['avg_noise_variance']
            noise_score = max(0.0, 1.0 - (noise / 1000))  # Penalty for high noise
            score_components.append(noise_score * 0.3)
        
        # Contrast score (0-1)
        if 'avg_contrast' in metrics:
            contrast = metrics['avg_contrast']
            contrast_score = min(1.0, max(0.0, (contrast - 10) / 80))  # 10-90 range
            score_components.append(contrast_score * 0.2)
        
        # Resolution score (0-1)
        if 'resolution_width' in metrics and 'resolution_height' in metrics:
            width = metrics['resolution_width']
            height = metrics['resolution_height']
            pixel_count = width * height
            
            # Score based on resolution (480p to 4K)
            resolution_score = min(1.0, max(0.0, (pixel_count - 345600) / 8294400))  # 480p to 4K
            score_components.append(resolution_score * 0.1)
        
        return sum(score_components) if score_components else 0.5


class ImageQualityValidator:
    """
    Specialized image quality validator for photographers and visual content creators.
    
    Performs advanced image analysis including sharpness assessment, color analysis,
    composition evaluation, and platform-specific image quality checks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.ImageQualityValidator")
        
        # Image quality thresholds
        self.quality_thresholds = {
            'min_sharpness': 50.0,
            'max_noise_level': 0.1,
            'min_contrast': 20.0,
            'max_blur_variance': 100.0,
            'min_color_depth': 8,
            'target_aspect_ratios': [(1, 1), (4, 3), (16, 9), (3, 4), (9, 16)]
        }
    
    async def validate_image_quality(
        self,
        image_data: Union[bytes, str],
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive image quality analysis."""
        if not HAS_MEDIA_LIBS:
            return {'error': 'Image processing libraries not available'}
        
        try:
            # Load image
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
                pil_image = Image.open(image_data)
            else:
                # Handle bytes data
                image_array = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                pil_image = Image.open(io.BytesIO(image_data))
            
            if image is None:
                return {'error': 'Could not load image'}
            
            quality_metrics = {}
            
            # Basic image properties
            height, width, channels = image.shape
            quality_metrics.update({
                'width': width,
                'height': height,
                'channels': channels,
                'aspect_ratio': width / height,
                'pixel_count': width * height,
                'file_format': pil_image.format,
                'color_mode': pil_image.mode
            })
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness assessment using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness'] = float(laplacian_var)
            
            # Noise estimation
            noise_estimate = cv2.fastNlDenoising(gray)
            noise_level = np.mean(np.abs(gray.astype(float) - noise_estimate.astype(float))) / 255.0
            quality_metrics['noise_level'] = float(noise_level)
            
            # Contrast analysis
            contrast = np.std(gray)
            quality_metrics['contrast'] = float(contrast)
            
            # Brightness analysis
            brightness = np.mean(gray)
            quality_metrics['brightness'] = float(brightness)
            
            # Color analysis (if color image)
            if channels == 3:
                # Color histogram analysis
                hist_b = cv2.calcHist([image], [0], None, [256], [0, 256])
                hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
                hist_r = cv2.calcHist([image], [2], None, [256], [0, 256])
                
                # Color distribution metrics
                color_variance = np.var([np.var(hist_b), np.var(hist_g), np.var(hist_r)])
                quality_metrics['color_variance'] = float(color_variance)
                
                # Dominant colors
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                dominant_color = np.mean(image_rgb.reshape(-1, 3), axis=0)
                quality_metrics['dominant_color'] = dominant_color.tolist()
            
            # Blur detection using variance of Laplacian
            blur_variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['blur_variance'] = float(blur_variance)
            
            # Edge density (composition metric)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            quality_metrics['edge_density'] = float(edge_density)
            
            # EXIF data extraction (if available)
            try:
                exif_data = {}
                if hasattr(pil_image, '_getexif') and pil_image._getexif():
                    exif = pil_image._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                
                quality_metrics['exif_available'] = len(exif_data) > 0
                if 'DateTime' in exif_data:
                    quality_metrics['has_timestamp'] = True
                if 'Make' in exif_data or 'Model' in exif_data:
                    quality_metrics['camera_info_available'] = True
                    
            except Exception as e:
                self.logger.debug(f"EXIF extraction failed: {str(e)}")
                quality_metrics['exif_available'] = False
            
            # Calculate overall quality score
            quality_score = self._calculate_image_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = quality_score
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Image quality validation failed: {str(e)}")
            return {'error': f'Image validation failed: {str(e)}'}
    
    def _calculate_image_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall image quality score based on multiple factors."""
        score_components = []
        
        # Sharpness score (0-1)
        if 'sharpness' in metrics:
            sharpness = metrics['sharpness']
            sharpness_score = min(1.0, max(0.0, (sharpness - 10) / 490))  # 10-500 range
            score_components.append(sharpness_score * 0.4)
        
        # Noise score (0-1, lower noise is better)
        if 'noise_level' in metrics:
            noise = metrics['noise_level']
            noise_score = max(0.0, 1.0 - (noise * 10))  # Penalty for high noise
            score_components.append(noise_score * 0.3)
        
        # Contrast score (0-1)
        if 'contrast' in metrics:
            contrast = metrics['contrast']
            contrast_score = min(1.0, max(0.0, (contrast - 10) / 80))  # 10-90 range
            score_components.append(contrast_score * 0.2)
        
        # Resolution score (0-1)
        if 'pixel_count' in metrics:
            pixel_count = metrics['pixel_count']
            # Score based on resolution (VGA to 4K)
            resolution_score = min(1.0, max(0.0, (pixel_count - 307200) / 8294400))  # VGA to 4K
            score_components.append(resolution_score * 0.1)
        
        return sum(score_components) if score_components else 0.5


class TextQualityValidator:
    """
    Specialized text quality validator for bloggers and content writers.
    
    Performs advanced text analysis including readability assessment, SEO optimization,
    language detection, sentiment analysis, and content uniqueness verification.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.TextQualityValidator")
        
        # Text quality thresholds
        self.quality_thresholds = {
            'min_readability_score': 30.0,
            'max_readability_score': 90.0,
            'min_grade_level': 6.0,
            'max_grade_level': 12.0,
            'min_sentence_variety': 0.3,
            'max_passive_voice_ratio': 0.3,
            'min_keyword_density': 0.005,
            'max_keyword_density': 0.03
        }
        
        # Load NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
            self.logger.warning("spaCy English model not found. Some features will be limited.")
    
    async def validate_text_quality(
        self,
        text_data: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive text quality analysis."""
        try:
            quality_metrics = {}
            
            # Basic text properties
            word_count = len(text_data.split())
            sentence_count = len(re.split(r'[.!?]+', text_data))
            paragraph_count = len(text_data.split('\n\n'))
            character_count = len(text_data)
            
            quality_metrics.update({
                'word_count': word_count,
                'sentence_count': sentence_count,
                'paragraph_count': paragraph_count,
                'character_count': character_count,
                'avg_words_per_sentence': word_count / max(sentence_count, 1),
                'avg_sentences_per_paragraph': sentence_count / max(paragraph_count, 1)
            })
            
            # Readability scores
            try:
                reading_ease = flesch_reading_ease(text_data)
                grade_level = flesch_kincaid_grade(text_data)
                
                quality_metrics.update({
                    'reading_ease': reading_ease,
                    'grade_level': grade_level
                })
            except Exception as e:
                self.logger.warning(f"Readability calculation failed: {str(e)}")
            
            # Language detection
            try:
                detected_language = detect(text_data)
                quality_metrics['detected_language'] = detected_language
            except Exception as e:
                self.logger.warning(f"Language detection failed: {str(e)}")
                quality_metrics['detected_language'] = 'unknown'
            
            # Advanced NLP analysis (if spaCy is available)
            if self.nlp and len(text_data) > 10:
                try:
                    doc = self.nlp(text_data)
                    
                    # Sentence variety (different sentence structures)
                    sentence_structures = []
                    for sent in doc.sents:
                        pos_pattern = ' '.join([token.pos_ for token in sent if not token.is_space])
                        sentence_structures.append(pos_pattern)
                    
                    unique_structures = len(set(sentence_structures))
                    sentence_variety = unique_structures / max(len(sentence_structures), 1)
                    quality_metrics['sentence_variety'] = sentence_variety
                    
                    # Passive voice detection
                    passive_count = 0
                    total_sentences = 0
                    
                    for sent in doc.sents:
                        total_sentences += 1
                        # Simple passive voice detection
                        has_be_verb = any(token.lemma_ in ['be', 'am', 'is', 'are', 'was', 'were'] for token in sent)
                        has_past_participle = any(token.tag_ == 'VBN' for token in sent)
                        
                        if has_be_verb and has_past_participle:
                            passive_count += 1
                    
                    passive_voice_ratio = passive_count / max(total_sentences, 1)
                    quality_metrics['passive_voice_ratio'] = passive_voice_ratio
                    
                    # Named entity recognition
                    entities = [(ent.text, ent.label_) for ent in doc.ents]
                    quality_metrics['named_entities_count'] = len(entities)
                    quality_metrics['has_named_entities'] = len(entities) > 0
                    
                except Exception as e:
                    self.logger.warning(f"NLP analysis failed: {str(e)}")
            
            # SEO analysis (if requirements provided)
            if requirements and 'seo' in requirements:
                seo_metrics = self._analyze_seo_quality(text_data, requirements['seo'])
                quality_metrics.update(seo_metrics)
            
            # Content uniqueness estimation (basic)
            unique_words = len(set(text_data.lower().split()))
            total_words = len(text_data.split())
            lexical_diversity = unique_words / max(total_words, 1)
            quality_metrics['lexical_diversity'] = lexical_diversity
            
            # Calculate overall quality score
            quality_score = self._calculate_text_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = quality_score
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Text quality validation failed: {str(e)}")
            return {'error': f'Text validation failed: {str(e)}'}
    
    def _analyze_seo_quality(self, text: str, seo_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze SEO quality factors."""
        seo_metrics = {}
        
        # Keyword density analysis
        keywords = seo_requirements.get('keywords', [])
        text_lower = text.lower()
        
        for keyword in keywords:
            keyword_count = text_lower.count(keyword.lower())
            keyword_density = keyword_count / max(len(text.split()), 1)
            seo_metrics[f'keyword_density_{keyword}'] = keyword_density
        
        # Title and heading analysis (if provided)
        if 'title' in seo_requirements:
            title = seo_requirements['title']
            title_in_content = title.lower() in text_lower
            seo_metrics['title_in_content'] = title_in_content
        
        # Meta description compatibility
        if len(text) > 160:
            first_paragraph = text.split('\n')[0]
            if len(first_paragraph) <= 160:
                seo_metrics['meta_description_ready'] = True
            else:
                seo_metrics['meta_description_ready'] = False
        
        return seo_metrics
    
    def _calculate_text_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall text quality score based on multiple factors."""
        score_components = []
        
        # Readability score (0-1)
        if 'reading_ease' in metrics:
            reading_ease = metrics['reading_ease']
            # Normalize to 0-1 (target range 30-90)
            readability_score = min(1.0, max(0.0, (reading_ease - 30) / 60))
            score_components.append(readability_score * 0.3)
        
        # Grade level appropriateness (0-1)
        if 'grade_level' in metrics:
            grade_level = metrics['grade_level']
            # Target grade level 6-12
            grade_score = max(0.0, 1.0 - abs(grade_level - 9) / 9)  # Target grade 9
            score_components.append(grade_score * 0.2)
        
        # Sentence variety (0-1)
        if 'sentence_variety' in metrics:
            variety = metrics['sentence_variety']
            variety_score = min(1.0, variety / 0.5)  # Target 50% variety
            score_components.append(variety_score * 0.2)
        
        # Passive voice penalty
        if 'passive_voice_ratio' in metrics:
            passive_ratio = metrics['passive_voice_ratio']
            passive_score = max(0.0, 1.0 - (passive_ratio / 0.3))  # Penalty for >30% passive
            score_components.append(passive_score * 0.15)
        
        # Lexical diversity (0-1)
        if 'lexical_diversity' in metrics:
            diversity = metrics['lexical_diversity']
            diversity_score = min(1.0, diversity / 0.7)  # Target 70% diversity
            score_components.append(diversity_score * 0.15)
        
        return sum(score_components) if score_components else 0.5
