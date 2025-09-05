"""Core Multimedia Content Processors
Advanced processing for multi-format content with AI-powered analysis

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer, Backend Senior Engineer, ML Engineer, 
              Database Administrator, Security Expert, Microservices Architect,
              Multimedia Processing Specialist, DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.
"""

import asyncio
import logging
import io
import tempfile
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from abc import ABC, abstractmethod
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import cv2
import librosa
import soundfile as sf
from PIL import Image, ImageEnhance, ImageFilter, ExifTags
import ffmpeg
from moviepy import VideoFileClip
import speech_recognition as sr
from transformers import pipeline

from .formats import ContentFormat, AudioFormat, VideoFormat, ImageFormat, SupportedFormats
from ..core.exceptions import ProcessingError, UnsupportedFormatError
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ProcessingOptions:
    """
Processing configuration options"""
    quality: str = "high"  # low, medium, high, ultra, studio
    preserve_metadata: bool = True
    extract_thumbnails: bool = False
    generate_previews: bool = False
    apply_enhancements: bool = False
    optimize_for_web: bool = False
    enable_ai_analysis: bool = True
    max_processing_time: int = 300  # seconds
    temp_dir: Optional[Path] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result of content processing operation"""
    success: bool
    content_id: str
    original_format: ContentFormat
    processed_format: Optional[ContentFormat] = None
    file_path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    thumbnails: List[str] = field(default_factory=list)
    previews: List[str] = field(default_factory=list)
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ContentMetrics:
    """
Content quality and performance metrics"""
    file_size: int
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    quality_score: float = 0.0
    compression_ratio: float = 0.0
    processing_speed: float = 0.0
    memory_usage: int = 0
    ai_confidence: float = 0.0


class ContentProcessor(ABC):
    """
Abstract base class for content processors"""
    
    def __init__(self, options: Optional[ProcessingOptions] = None):
        self.options = options or ProcessingOptions()
        self.temp_dir = self.options.temp_dir or Path(tempfile.gettempdir())
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.metrics = ContentMetrics(file_size=0)
        
    @abstractmethod
    async def process(self, content_data: Union[bytes, str, Path], 
                     metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
Process content and return result"""
        pass
    
    @abstractmethod
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        try:
            logger.info(f"Executing supports_format")
            
            # Implementation for supports_format
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"supports_format completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"supports_format failed: {e}")
            raise
    def _generate_content_id(self, content_data: bytes) -> str:
        """
Generate unique content identifier"""
        return hashlib.sha256(content_data[:1024]).hexdigest()[:16]
    
    async def cleanup(self):
        """
Clean up resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)


class AudioProcessor(ContentProcessor):
    """
Professional audio content processor"""
    
    def __init__(self, options: Optional[ProcessingOptions] = None):
        super().__init__(options)
        self.supported_formats = {fmt.value for fmt in AudioFormat}
        self.speech_recognizer = sr.Recognizer()
        
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """
Check if processor supports audio format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.AUDIO
        return format_type.lower() in self.supported_formats
    
    async def process(self, content_data: Union[bytes, str, Path], 
                     metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
Process audio content with advanced analysis"""
        start_time = datetime.now()
        
        try:
            # Handle input data
            if isinstance(content_data, (str, Path)):
                audio_path = Path(content_data)
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
            else:
                audio_data = content_data
                audio_path = self._create_temp_file(audio_data, '.wav')
            
            content_id = self._generate_content_id(audio_data)
            
            # Load and analyze audio
            audio_array, sample_rate = librosa.load(str(audio_path), sr=None)
            duration = len(audio_array) / sample_rate
            
            result = ProcessingResult(
                success=True,
                content_id=content_id,
                original_format=ContentFormat.AUDIO
            )
            
            # Extract metadata
            result.metadata = await self._extract_audio_metadata(audio_array, sample_rate, audio_path)
            
            # Generate thumbnails (waveform visualization)
            if self.options.extract_thumbnails:
                result.thumbnails = await self._generate_audio_thumbnails(audio_array, sample_rate)
            
            # AI Analysis
            if self.options.enable_ai_analysis:
                result.ai_analysis = await self._analyze_audio_content(audio_array, sample_rate)
            
            # Apply enhancements
            if self.options.apply_enhancements:
                enhanced_audio = await self._enhance_audio(audio_array, sample_rate)
                enhanced_path = self._create_temp_file(enhanced_audio.tobytes(), '.wav')
                result.file_path = enhanced_path
            else:
                result.file_path = audio_path
                
            # Update metrics
            self.metrics.file_size = len(audio_data)
            self.metrics.duration = duration
            self.metrics.processing_speed = len(audio_data) / (datetime.now() - start_time).total_seconds()
            
            result.processing_time = (datetime.now() - start_time).total_seconds()
            return result
            
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                content_id=content_id if 'content_id' in locals() else "unknown",
                original_format=ContentFormat.AUDIO,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _extract_audio_metadata(self, audio: np.ndarray, sr: int, path: Path) -> Dict[str, Any]:
        """Extract comprehensive audio metadata"""
        metadata = {
            'sample_rate': sr,
            'duration': len(audio) / sr,
            'channels': 1 if audio.ndim == 1 else audio.shape[0],
            'bit_depth': 32,  # librosa loads as float32
            'file_size': path.stat().st_size if path.exists() else 0,
        }
        
        # Audio features
        features = await asyncio.get_event_loop().run_in_executor(
            self.executor, self._compute_audio_features, audio, sr
        )
        metadata.update(features)
        
        return metadata
    
    def _compute_audio_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
Compute audio signal features"""
        features = {}
        
        try:
            # Spectral features
            features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)))
            features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr)))
            features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
            
            # Rhythm and tempo
            tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
            features['tempo'] = float(tempo)
            features['beat_count'] = len(beats)
            
            # Energy and loudness
            features['rms_energy'] = float(np.mean(librosa.feature.rms(y=audio)))
            features['loudness'] = float(20 * np.log10(np.mean(np.abs(audio)) + 1e-10))
            
            # Harmonic features
            harmonic, percussive = librosa.effects.hpss(audio)
            features['harmonic_ratio'] = float(np.mean(np.abs(harmonic)) / (np.mean(np.abs(audio)) + 1e-10))
            features['percussive_ratio'] = float(np.mean(np.abs(percussive)) / (np.mean(np.abs(audio)) + 1e-10))
            
            # MFCC coefficients
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfcc, axis=1).tolist()
            features['mfcc_std'] = np.std(mfcc, axis=1).tolist()
            
        except Exception as e:
            logger.warning(f"Feature extraction failed: {str(e)}")
            
        return features
    
    async def _generate_audio_thumbnails(self, audio: np.ndarray, sr: int) -> List[str]:
        """Generate audio waveform visualization thumbnails"""
        thumbnails = []
        
        try:
            import matplotlib.pyplot as plt
            
            # Waveform thumbnail
            plt.figure(figsize=(10, 3))
            plt.plot(np.linspace(0, len(audio)/sr, len(audio)), audio)
            plt.title('Waveform')
            plt.xlabel('Time (s)')
            plt.ylabel('Amplitude')
            
            waveform_path = self.temp_dir / f"waveform_{self._generate_content_id(audio.tobytes())}.png"
            plt.savefig(waveform_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            thumbnails.append(str(waveform_path))
            
            # Spectrogram thumbnail
            plt.figure(figsize=(10, 6))
            D = librosa.stft(audio)
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram')
            
            spectrogram_path = self.temp_dir / f"spectrogram_{self._generate_content_id(audio.tobytes())}.png"
            plt.savefig(spectrogram_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            thumbnails.append(str(spectrogram_path))
            
        except Exception as e:
            logger.warning(f"Thumbnail generation failed: {str(e)}")
            
        return thumbnails
    
    async def _analyze_audio_content(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """AI-powered audio content analysis"""
        analysis = {
            'content_type': 'audio',
            'ai_confidence': 0.0,
            'detected_features': []
        }
        
        try:
            # Genre classification (simplified)
            features = self._compute_audio_features(audio, sr)
            
            if features.get('tempo', 0) > 120 and features.get('percussive_ratio', 0) > 0.3:
                analysis['detected_features'].append('electronic/dance')
                analysis['ai_confidence'] = 0.75
            elif features.get('harmonic_ratio', 0) > 0.6:
                analysis['detected_features'].append('melodic/harmonic')
                analysis['ai_confidence'] = 0.70
            elif features.get('loudness', -60) > -20:
                analysis['detected_features'].append('high_energy')
                analysis['ai_confidence'] = 0.65
            
            # Speech detection
            if self._detect_speech(audio, sr):
                analysis['detected_features'].append('speech')
                analysis['ai_confidence'] = max(analysis['ai_confidence'], 0.80)
            
            # Music/speech classification
            if features.get('spectral_centroid', 0) > 2000:
                analysis['content_classification'] = 'music'
            else:
                analysis['content_classification'] = 'speech_or_ambient'
                
        except Exception as e:
            logger.warning(f"AI analysis failed: {str(e)}")
            analysis['error'] = str(e)
            
        return analysis
    
    def _detect_speech(self, audio: np.ndarray, sr: int) -> bool:
        """Detect if audio contains speech"""
        try:
            # Simple speech detection using spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
            zcr = librosa.feature.zero_crossing_rate(audio)
            
            # Speech typically has lower spectral centroid and higher ZCR
            avg_centroid = np.mean(spectral_centroid)
            avg_zcr = np.mean(zcr)
            
            return avg_centroid < 3000 and avg_zcr > 0.1
            
        except:
            return False
    
    async def _enhance_audio(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
Apply audio enhancements"""
        try:
            # Noise reduction
            enhanced = librosa.effects.preemphasis(audio)
            
            # Normalize
            enhanced = librosa.util.normalize(enhanced)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Audio enhancement failed: {str(e)}")
            return audio
    
    def _create_temp_file(self, data: bytes, extension: str) -> Path:
        """Create temporary file with data"""
        temp_file = self.temp_dir / f"temp_{hashlib.md5(data).hexdigest()}{extension}"
        with open(temp_file, 'wb') as f:
            f.write(data)
        return temp_file


class VideoProcessor(ContentProcessor):
    """Professional video content processor"""
    
    def __init__(self, options: Optional[ProcessingOptions] = None):
        super().__init__(options)
        self.supported_formats = {fmt.value for fmt in VideoFormat}
        
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """
Check if processor supports video format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.VIDEO
        return format_type.lower() in self.supported_formats
    
    async def process(self, content_data: Union[bytes, str, Path], 
                     metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
Process video content with advanced analysis"""
        start_time = datetime.now()
        
        try:
            # Handle input data
            if isinstance(content_data, (str, Path)):
                video_path = Path(content_data)
                with open(video_path, 'rb') as f:
                    video_data = f.read()
            else:
                video_data = content_data
                video_path = self._create_temp_file(video_data, '.mp4')
            
            content_id = self._generate_content_id(video_data)
            
            result = ProcessingResult(
                success=True,
                content_id=content_id,
                original_format=ContentFormat.VIDEO,
                file_path=video_path
            )
            
            # Load video for analysis
            video_clip = VideoFileClip(str(video_path))
            
            # Extract metadata
            result.metadata = await self._extract_video_metadata(video_clip, video_path)
            
            # Generate thumbnails
            if self.options.extract_thumbnails:
                result.thumbnails = await self._generate_video_thumbnails(video_clip)
            
            # AI Analysis
            if self.options.enable_ai_analysis:
                result.ai_analysis = await self._analyze_video_content(video_clip)
            
            # Apply enhancements
            if self.options.apply_enhancements:
                enhanced_path = await self._enhance_video(video_clip)
                result.file_path = enhanced_path
            
            # Update metrics
            self.metrics.file_size = len(video_data)
            self.metrics.duration = video_clip.duration
            self.metrics.dimensions = (int(video_clip.w), int(video_clip.h))
            
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Clean up
            video_clip.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                content_id=content_id if 'content_id' in locals() else "unknown",
                original_format=ContentFormat.VIDEO,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _extract_video_metadata(self, video: VideoFileClip, path: Path) -> Dict[str, Any]:
        """Extract comprehensive video metadata"""
        metadata = {
            'duration': video.duration,
            'fps': video.fps,
            'width': int(video.w),
            'height': int(video.h),
            'aspect_ratio': video.w / video.h,
            'file_size': path.stat().st_size if path.exists() else 0,
            'has_audio': video.audio is not None
        }
        
        # Additional video analysis
        analysis = await asyncio.get_event_loop().run_in_executor(
            self.executor, self._analyze_video_properties, video
        )
        metadata.update(analysis)
        
        return metadata
    
    def _analyze_video_properties(self, video: VideoFileClip) -> Dict[str, Any]:
        """
Analyze video technical properties"""
        properties = {}
        
        try:
            # Sample frames for analysis
            sample_times = [video.duration * 0.1, video.duration * 0.5, video.duration * 0.9]
            frames = [video.get_frame(t) for t in sample_times if t < video.duration]
            
            if frames:
                # Color analysis
                avg_frame = np.mean(frames, axis=0)
                properties['avg_brightness'] = float(np.mean(avg_frame))
                properties['color_variance'] = float(np.var(avg_frame))
                
                # Scene complexity
                properties['scene_complexity'] = self._calculate_scene_complexity(frames)
                
                # Motion estimation
                if len(frames) > 1:
                    properties['motion_estimate'] = self._estimate_motion(frames)
                
        except Exception as e:
            logger.warning(f"Video property analysis failed: {str(e)}")
            
        return properties
    
    def _calculate_scene_complexity(self, frames: List[np.ndarray]) -> float:
        """Calculate scene complexity based on edge density"""
        try:
            complexities = []
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                complexity = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                complexities.append(complexity)
            return float(np.mean(complexities))
        except:
            return 0.0
    
    def _estimate_motion(self, frames: List[np.ndarray]) -> float:
        """
Estimate motion between frames"""
        try:
            if len(frames) < 2:
                return 0.0
                
            motion_scores = []
            for i in range(1, len(frames)):
                diff = cv2.absdiff(
                    cv2.cvtColor(frames[i-1], cv2.COLOR_RGB2GRAY),
                    cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
                )
                motion_score = np.sum(diff > 30) / (diff.shape[0] * diff.shape[1])
                motion_scores.append(motion_score)
                
            return float(np.mean(motion_scores))
        except:
            return 0.0
    
    async def _generate_video_thumbnails(self, video: VideoFileClip) -> List[str]:
        """
Generate video frame thumbnails"""
        thumbnails = []
        
        try:
            # Extract key frames
            thumbnail_times = [
                video.duration * 0.1,
                video.duration * 0.5,
                video.duration * 0.9
            ]
            
            for i, time_point in enumerate(thumbnail_times):
                if time_point < video.duration:
                    frame = video.get_frame(time_point)
                    frame_image = Image.fromarray(frame)
                    
                    # Resize for thumbnail
                    frame_image.thumbnail((320, 180), Image.Resampling.LANCZOS)
                    
                    thumbnail_path = self.temp_dir / f"video_thumb_{i}_{self._generate_content_id(frame.tobytes())}.jpg"
                    frame_image.save(thumbnail_path, 'JPEG', quality=85)
                    thumbnails.append(str(thumbnail_path))
                    
        except Exception as e:
            logger.warning(f"Video thumbnail generation failed: {str(e)}")
            
        return thumbnails
    
    async def _analyze_video_content(self, video: VideoFileClip) -> Dict[str, Any]:
        """AI-powered video content analysis"""
        analysis = {
            'content_type': 'video',
            'ai_confidence': 0.0,
            'detected_features': [],
            'scene_analysis': {}
        }
        
        try:
            # Scene detection
            sample_frame = video.get_frame(video.duration / 2)
            scene_features = self._analyze_scene_content(sample_frame)
            analysis['scene_analysis'] = scene_features
            
            # Motion analysis
            if video.duration > 2:
                motion_analysis = await self._analyze_motion_patterns(video)
                analysis['motion_analysis'] = motion_analysis
            
            # Audio analysis if present
            if video.audio is not None:
                audio_analysis = await self._analyze_video_audio(video)
                analysis['audio_analysis'] = audio_analysis
                
            analysis['ai_confidence'] = 0.75
            
        except Exception as e:
            logger.warning(f"Video AI analysis failed: {str(e)}")
            analysis['error'] = str(e)
            
        return analysis
    
    def _analyze_scene_content(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze scene content in a frame"""
        features = {}
        
        try:
            # Color analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            features['dominant_hue'] = float(np.mean(hsv[:, :, 0]))
            features['saturation'] = float(np.mean(hsv[:, :, 1]))
            features['brightness'] = float(np.mean(hsv[:, :, 2]))
            
            # Edge detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            features['edge_density'] = float(np.sum(edges > 0) / (edges.shape[0] * edges.shape[1]))
            
            # Simple object detection (contours)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            features['object_count'] = len([c for c in contours if cv2.contourArea(c) > 100])
            
        except Exception as e:
            logger.warning(f"Scene analysis failed: {str(e)}")
            
        return features
    
    async def _analyze_motion_patterns(self, video: VideoFileClip) -> Dict[str, Any]:
        """Analyze motion patterns in video"""
        motion_data = {
            'motion_intensity': 0.0,
            'scene_changes': 0,
            'camera_movement': 'static'
        }
        
        try:
            # Sample frames for motion analysis
            sample_times = np.linspace(0, video.duration * 0.9, min(10, int(video.duration)))
            frames = [video.get_frame(t) for t in sample_times]
            
            if len(frames) > 1:
                motion_scores = []
                for i in range(1, len(frames)):
                    motion_score = self._calculate_frame_motion(frames[i-1], frames[i])
                    motion_scores.append(motion_score)
                
                motion_data['motion_intensity'] = float(np.mean(motion_scores))
                motion_data['scene_changes'] = len([s for s in motion_scores if s > 0.3])
                
                if motion_data['motion_intensity'] > 0.5:
                    motion_data['camera_movement'] = 'dynamic'
                elif motion_data['motion_intensity'] > 0.2:
                    motion_data['camera_movement'] = 'moderate'
                    
        except Exception as e:
            logger.warning(f"Motion analysis failed: {str(e)}")
            
        return motion_data
    
    def _calculate_frame_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate motion between two frames"""
        try:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
            
            diff = cv2.absdiff(gray1, gray2)
            motion_score = np.sum(diff > 30) / (diff.shape[0] * diff.shape[1])
            
            return float(motion_score)
        except:
            return 0.0
    
    async def _analyze_video_audio(self, video: VideoFileClip) -> Dict[str, Any]:
        """
Analyze audio track of video"""
        audio_analysis = {}
        
        try:
            if video.audio is not None:
                # Extract audio array
                audio_array = video.audio.to_soundarray()
                if audio_array.ndim > 1:
                    audio_array = np.mean(audio_array, axis=1)
                
                # Basic audio features
                audio_analysis['has_audio'] = True
                audio_analysis['audio_duration'] = video.audio.duration
                audio_analysis['audio_loudness'] = float(20 * np.log10(np.mean(np.abs(audio_array)) + 1e-10))
                
                # Detect silence
                silence_threshold = -40  # dB
                audio_analysis['has_silence'] = audio_analysis['audio_loudness'] < silence_threshold
                
        except Exception as e:
            logger.warning(f"Video audio analysis failed: {str(e)}")
            audio_analysis = {'has_audio': False, 'error': str(e)}
            
        return audio_analysis
    
    async def _enhance_video(self, video: VideoFileClip) -> Path:
        """Apply video enhancements"""
        try:
            # Simple enhancement: adjust contrast and brightness
            enhanced_path = self.temp_dir / f"enhanced_{self._generate_content_id(str(video).encode())}.mp4"
            
            # Use ffmpeg for enhancement
            (
                ffmpeg
                .input(str(video.filename))
                .filter('eq', contrast=1.1, brightness=0.05)
                .output(str(enhanced_path))
                .overwrite_output()
                .run(quiet=True)
            )
            
            return enhanced_path
            
        except Exception as e:
            logger.warning(f"Video enhancement failed: {str(e)}")
            return Path(video.filename)
    
    def _create_temp_file(self, data: bytes, extension: str) -> Path:
        """Create temporary file with data"""
        temp_file = self.temp_dir / f"temp_{hashlib.md5(data).hexdigest()}{extension}"
        with open(temp_file, 'wb') as f:
            f.write(data)
        return temp_file


class ImageProcessor(ContentProcessor):
    """Professional image content processor"""
    
    def __init__(self, options: Optional[ProcessingOptions] = None):
        super().__init__(options)
        self.supported_formats = {fmt.value for fmt in ImageFormat}
        
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """
Check if processor supports image format"""
        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.IMAGE
        return format_type.lower() in self.supported_formats
    
    async def process(self, content_data: Union[bytes, str, Path], 
                     metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
Process image content with advanced analysis"""
        start_time = datetime.now()
        
        try:
            # Handle input data
            if isinstance(content_data, (str, Path)):
                image_path = Path(content_data)
                with open(image_path, 'rb') as f:
                    image_data = f.read()
            else:
                image_data = content_data
                image_path = self._create_temp_file(image_data, '.jpg')
            
            content_id = self._generate_content_id(image_data)
            
            result = ProcessingResult(
                success=True,
                content_id=content_id,
                original_format=ContentFormat.IMAGE,
                file_path=image_path
            )
            
            # Load image
            with Image.open(io.BytesIO(image_data)) as img:
                # Extract metadata
                result.metadata = await self._extract_image_metadata(img, image_path)
                
                # Generate thumbnails
                if self.options.extract_thumbnails:
                    result.thumbnails = await self._generate_image_thumbnails(img)
                
                # AI Analysis
                if self.options.enable_ai_analysis:
                    result.ai_analysis = await self._analyze_image_content(img)
                
                # Apply enhancements
                if self.options.apply_enhancements:
                    enhanced_img = await self._enhance_image(img)
                    enhanced_path = self._save_enhanced_image(enhanced_img)
                    result.file_path = enhanced_path
            
            # Update metrics
            self.metrics.file_size = len(image_data)
            self.metrics.dimensions = (result.metadata.get('width', 0), result.metadata.get('height', 0))
            
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
    
    async def _extract_image_metadata(self, image: Image.Image) -> Dict[str, Any]:
        """Extract metadata from an image"""
        metadata = {}
        
        try:
            # Basic metadata
            metadata.update({
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height
            })
            
        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")
        
        # Image analysis
        analysis = await asyncio.get_event_loop().run_in_executor(
            self.executor, self._analyze_image_properties, image
        )
        metadata.update(analysis)
        
        return metadata
    
    def _analyze_image_properties(self, image: Image.Image) -> Dict[str, Any]:
        """
Analyze image technical properties"""
        properties = {}
        
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image.convert('RGB'))
            
            # Color analysis
            properties['avg_brightness'] = float(np.mean(img_array))
            properties['color_variance'] = float(np.var(img_array))
            
            # Color distribution
            r_channel = img_array[:, :, 0]
            g_channel = img_array[:, :, 1]
            b_channel = img_array[:, :, 2]
            
            properties['red_dominance'] = float(np.mean(r_channel) / (np.mean(img_array) + 1e-10))
            properties['green_dominance'] = float(np.mean(g_channel) / (np.mean(img_array) + 1e-10))
            properties['blue_dominance'] = float(np.mean(b_channel) / (np.mean(img_array) + 1e-10))
            
            # Edge analysis
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            properties['edge_density'] = float(np.sum(edges > 0) / (edges.shape[0] * edges.shape[1]))
            
            # Texture analysis
            properties['texture_complexity'] = self._calculate_texture_complexity(gray)
            
            # Quality assessment
            properties['quality_score'] = self._assess_image_quality(img_array)
            
        except Exception as e:
            logger.warning(f"Image property analysis failed: {str(e)}")
            
        return properties
    
    def _calculate_texture_complexity(self, gray_image: np.ndarray) -> float:
        """Calculate texture complexity using local binary patterns"""
        try:
            # Simplified texture analysis using gradient magnitude
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            return float(np.std(gradient_magnitude))
        except:
            return 0.0
    
    def _assess_image_quality(self, img_array: np.ndarray) -> float:
        """
Assess image quality using multiple metrics"""
        try:
            # Simple quality metrics
            sharpness = self._calculate_sharpness(img_array)
            noise_level = self._estimate_noise_level(img_array)
            contrast = self._calculate_contrast(img_array)
            
            # Combine metrics (0-1 scale)
            quality_score = (sharpness * 0.4 + (1 - noise_level) * 0.3 + contrast * 0.3)
            return float(np.clip(quality_score, 0, 1))
            
        except:
            return 0.5  # Default medium quality
    
    def _calculate_sharpness(self, img_array: np.ndarray) -> float:
        """
Calculate image sharpness using Laplacian variance"""
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            
            # Normalize to 0-1 scale
            return float(np.clip(sharpness / 1000, 0, 1))
        except:
            return 0.5
    
    def _estimate_noise_level(self, img_array: np.ndarray) -> float:
        """
Estimate noise level in image"""
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Use high-pass filter to estimate noise
            kernel = np.array([[-1, -1, -1],
                             [-1,  8, -1],
                             [-1, -1, -1]])
            
            filtered = cv2.filter2D(gray, cv2.CV_64F, kernel)
            noise_estimate = np.std(filtered)
            
            # Normalize to 0-1 scale
            return float(np.clip(noise_estimate / 50, 0, 1))
        except:
            return 0.3
    
    def _calculate_contrast(self, img_array: np.ndarray) -> float:
        """
Calculate image contrast"""
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            contrast = gray.std()
            
            # Normalize to 0-1 scale
            return float(np.clip(contrast / 128, 0, 1))
        except:
            return 0.5
    
    async def _generate_image_thumbnails(self, image: Image.Image) -> List[str]:
        """
Generate image thumbnails in different sizes"""
        thumbnails = []
        
        try:
            thumbnail_sizes = [(150, 150), (300, 300), (600, 400)]
            
            for i, size in enumerate(thumbnail_sizes):
                thumbnail = image.copy()
                thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
                
                thumbnail_path = self.temp_dir / f"thumb_{i}_{self._generate_content_id(str(image).encode())}.jpg"
                thumbnail.save(thumbnail_path, 'JPEG', quality=85)
                thumbnails.append(str(thumbnail_path))
                
        except Exception as e:
            logger.warning(f"Image thumbnail generation failed: {str(e)}")
            
        return thumbnails
    
    async def _analyze_image_content(self, image: Image.Image) -> Dict[str, Any]:
        """AI-powered image content analysis"""
        analysis = {
            'content_type': 'image',
            'ai_confidence': 0.0,
            'detected_features': [],
            'color_analysis': {},
            'composition_analysis': {}
        }
        
        try:
            img_array = np.array(image.convert('RGB'))
            
            # Color analysis
            analysis['color_analysis'] = self._analyze_colors(img_array)
            
            # Composition analysis
            analysis['composition_analysis'] = self._analyze_composition(img_array)
            
            # Object detection (simplified)
            objects = await self._detect_objects(img_array)
            analysis['detected_objects'] = objects
            
            # Scene classification (simplified)
            scene_type = self._classify_scene(img_array)
            analysis['scene_classification'] = scene_type
            
            analysis['ai_confidence'] = 0.70
            
        except Exception as e:
            logger.warning(f"Image AI analysis failed: {str(e)}")
            analysis['error'] = str(e)
            
        return analysis
    
    def _analyze_colors(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze color composition"""
        color_info = {}
        
        try:
            # Color histogram
            colors = img_array.reshape(-1, 3)
            
            # Dominant colors (simplified K-means)
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(colors)
            
            dominant_colors = kmeans.cluster_centers_.astype(int).tolist()
            color_info['dominant_colors'] = dominant_colors
            
            # Color temperature estimation
            avg_color = np.mean(colors, axis=0)
            if avg_color[2] > avg_color[0]:  # More blue than red
                color_info['temperature'] = 'cool'
            elif avg_color[0] > avg_color[2]:  # More red than blue
                color_info['temperature'] = 'warm'
            else:
                color_info['temperature'] = 'neutral'
                
            # Saturation analysis
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            avg_saturation = np.mean(hsv[:, :, 1])
            color_info['saturation_level'] = 'high' if avg_saturation > 150 else 'medium' if avg_saturation > 80 else 'low'
            
        except Exception as e:
            logger.warning(f"Color analysis failed: {str(e)}")
            
        return color_info
    
    def _analyze_composition(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze image composition"""
        composition = {}
        
        try:
            h, w = img_array.shape[:2]
            
            # Rule of thirds analysis
            third_h, third_w = h // 3, w // 3
            
            # Calculate interest points near rule of thirds intersections
            interest_points = []
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
            
            if corners is not None:
                for corner in corners:
                    x, y = corner.ravel()
                    # Check if corner is near rule of thirds lines
                    near_third = (abs(x - third_w) < 50 or abs(x - 2*third_w) < 50 or
                                abs(y - third_h) < 50 or abs(y - 2*third_h) < 50)
                    if near_third:
                        interest_points.append([float(x), float(y)])
                        
            composition['rule_of_thirds_points'] = len(interest_points)
            composition['total_interest_points'] = len(corners) if corners is not None else 0
            
            # Symmetry analysis
            left_half = gray[:, :w//2]
            right_half = cv2.flip(gray[:, w//2:], 1)
            
            if left_half.shape == right_half.shape:
                symmetry_score = cv2.matchTemplate(left_half, right_half, cv2.TM_CCOEFF_NORMED)[0, 0]
                composition['horizontal_symmetry'] = float(symmetry_score)
            
        except Exception as e:
            logger.warning(f"Composition analysis failed: {str(e)}")
            
        return composition
    
    async def _detect_objects(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Simplified object detection"""
        objects = []
        
        try:
            # Simple contour-based object detection
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours[:10]):  # Limit to top 10
                area = cv2.contourArea(contour)
                if area > 1000:  # Filter small objects
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        'id': i,
                        'bbox': [int(x), int(y), int(w), int(h)],
                        'area': float(area),
                        'confidence': 0.6
                    })
                    
        except Exception as e:
            logger.warning(f"Object detection failed: {str(e)}")
            
        return objects
    
    def _classify_scene(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Simplified scene classification"""
        scene_info = {
            'type': 'unknown',
            'confidence': 0.0
        }
        
        try:
            # Simple heuristics for scene classification
            avg_brightness = np.mean(img_array)
            edge_density = self._calculate_edge_density(img_array)
            color_variance = np.var(img_array)
            
            if avg_brightness < 80:
                scene_info['type'] = 'dark/night'
                scene_info['confidence'] = 0.7
            elif avg_brightness > 200:
                scene_info['type'] = 'bright/outdoor'
                scene_info['confidence'] = 0.7
            elif edge_density > 0.1:
                scene_info['type'] = 'detailed/complex'
                scene_info['confidence'] = 0.6
            elif color_variance < 1000:
                scene_info['type'] = 'simple/minimal'
                scene_info['confidence'] = 0.6
            else:
                scene_info['type'] = 'general'
                scene_info['confidence'] = 0.5
                
        except Exception as e:
            logger.warning(f"Scene classification failed: {str(e)}")
            
        return scene_info
    
    def _calculate_edge_density(self, img_array: np.ndarray) -> float:
        """Calculate edge density in image"""
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            return float(np.sum(edges > 0) / (edges.shape[0] * edges.shape[1]))
        except:
            return 0.0
    
    async def _enhance_image(self, image: Image.Image) -> Image.Image:
        """
Apply image enhancements"""
        try:
            enhanced = image.copy()
            
            # Auto-adjust contrast
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.1)
            
            # Auto-adjust color
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(1.05)
            
            # Auto-adjust sharpness
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.1)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Image enhancement failed: {str(e)}")
            return image
    
    def _save_enhanced_image(self, image: Image.Image) -> Path:
        """Save enhanced image to temporary file"""
        enhanced_path = self.temp_dir / f"enhanced_{self._generate_content_id(str(image).encode())}.jpg"
        image.save(enhanced_path, 'JPEG', quality=95)
        return enhanced_path
    
    def _create_temp_file(self, data: bytes, extension: str) -> Path:
        """Create temporary file with data"""
        temp_file = self.temp_dir / f"temp_{hashlib.md5(data).hexdigest()}{extension}"
        with open(temp_file, 'wb') as f:
            f.write(data)
        return temp_file


class MultimediaProcessor:
    """Unified multimedia processor for all content types"""
    
    def __init__(self, options: Optional[ProcessingOptions] = None):
        self.options = options or ProcessingOptions()
        self.processors = {
            ContentFormat.AUDIO: AudioProcessor(options),
            ContentFormat.VIDEO: VideoProcessor(options),
            ContentFormat.IMAGE: ImageProcessor(options)
        }
        
    async def process(self, content_data: Union[bytes, str, Path], 
                     content_type: Optional[Union[str, ContentFormat]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
Process multimedia content automatically detecting type"""
        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = await self._detect_content_type(content_data)
        
        if isinstance(content_type, str):
            content_type = ContentFormat(content_type.lower())
        
        # Get appropriate processor
        processor = self.processors.get(content_type)
        if processor is None:
            raise UnsupportedFormatError(f"Unsupported content type: {content_type}")
        
        # Process content
        return await processor.process(content_data, metadata)
    
    async def _detect_content_type(self, content_data: Union[bytes, str, Path]) -> ContentFormat:
        """Auto-detect content type from data or filename"""
        
        if isinstance(content_data, (str, Path)):
            # Detect from file extension
            extension = Path(content_data).suffix.lower().lstrip('.')
            format_enum = SupportedFormats.get_format_by_extension(extension)
            
            if format_enum:
                if isinstance(format_enum, AudioFormat):
                    return ContentFormat.AUDIO
                elif isinstance(format_enum, VideoFormat):
                    return ContentFormat.VIDEO
                elif isinstance(format_enum, ImageFormat):
                    return ContentFormat.IMAGE
        
        elif isinstance(content_data, bytes):
            # Detect from magic bytes
            if content_data.startswith(b'\xff\xfb') or content_data.startswith(b'\x49\x44\x33'):
                return ContentFormat.AUDIO
            elif content_data.startswith(b'\x00\x00\x00\x18ftypmp4') or content_data.startswith(b'\x00\x00\x00\x20ftypMP4'):
                return ContentFormat.VIDEO
            elif content_data.startswith(b'\xff\xd8\xff') or content_data.startswith(b'\x89PNG'):
                return ContentFormat.IMAGE
        
        # Default fallback
        raise UnsupportedFormatError("Unable to detect content type")
    
    def get_supported_formats(self) -> Dict[ContentFormat, List[str]]:
        """Get all supported formats by content type"""
        return {
            ContentFormat.AUDIO: [fmt.value for fmt in AudioFormat],
            ContentFormat.VIDEO: [fmt.value for fmt in VideoFormat],
            ContentFormat.IMAGE: [fmt.value for fmt in ImageFormat]
        }
    
    async def cleanup(self):
        """
Clean up all processors"""
        for processor in self.processors.values():
            await processor.cleanup()
