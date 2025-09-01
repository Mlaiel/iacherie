"""Content Agent - Advanced Multi-Format Content Processing System

Core agent responsible for analyzing, processing, and optimizing content across multiple formats.
Integrates with AI models for intelligent content understanding and enhancement.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import hashlib
import mimetypes
from pathlib import Path

import aiofiles
import numpy as np
from PIL import Image
import librosa
import cv2
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import torchvision.transforms as transforms

from ..base import BaseAgent, AgentResponse
try:
    from core.exceptions import ContentProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ContentProcessingError, ValidationError = globals().get('ContentProcessingError, ValidationError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...security.file_validator import FileValidator
from ...utils.file_utils import FileUtils
from ...ml.content_models import ContentClassifier, QualityAssesssor

logger = logging.getLogger(__name__)

class ContentAgent(BaseAgent):
    """
    Advanced content processing agent with multi-format support and AI analysis.
    
    Capabilities:
    - Multi-format content analysis (audio, video, image, text)
    - AI-powered quality assessment
    - Metadata extraction and enrichment
    - Content optimization recommendations
    - Format conversion and standardization
    - Trend analysis and content scoring
    """
    
    def __init__(self, agent_id: str = "content_agent", config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
        
        # Initialize processors
        self.audio_processor = AudioContentProcessor()
        self.video_processor = VideoContentProcessor()
        self.image_processor = ImageContentProcessor()
        self.text_processor = TextContentProcessor()
        
        # Initialize AI models
        self.content_classifier = None
        self.quality_assessor = None
        self.sentiment_analyzer = None
        
        # File validator
        self.file_validator = FileValidator()
        
        # Supported formats
        self.supported_formats = {
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
            'image': ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.svg'],
            'text': ['.txt', '.md', '.html', '.json', '.xml', '.csv']
        }
        
    async def initialize(self):
        """Initialize AI models and processors"""
        try:
            # Initialize content classifier
            self.content_classifier = ContentClassifier()
            await self.content_classifier.load_model()
            
            # Initialize quality assessor
            self.quality_assessor = QualityAssesssor()
            await self.quality_assessor.load_model()
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Content Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Content Agent: {e}")
            raise ContentProcessingError(f"Initialization failed: {e}")
    
    async def process(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process content analysis request.
        
        Args:
            request: Dictionary containing:
                - content_path: Path to content file
                - content_type: Type of content (audio/video/image/text)
                - analysis_options: List of analysis types to perform
                - optimization_options: Optimization settings
                - metadata: Additional metadata
        
        Returns:
            AgentResponse with analysis results and recommendations
        """
        start_time = time.time()
        
        try:
            # Validate request
            if 'content_path' not in request:
                raise ValidationError("Content path is required")
            
            content_path = Path(request['content_path'])
            if not content_path.exists():
                raise ValidationError(f"Content file not found: {content_path}")
            
            # Validate file security
            security_check = await self.file_validator.validate_file(content_path)
            if not security_check['is_safe']:
                raise ValidationError(f"Security validation failed: {security_check['reason']}")
            
            # Determine content type
            content_type = request.get('content_type') or self._detect_content_type(content_path)
            
            # Process content based on type
            analysis_results = await self._process_content_by_type(
                content_path, 
                content_type,
                request.get('analysis_options', ['basic', 'quality', 'metadata']),
                request.get('optimization_options', {}),
                request.get('metadata', {})
            )
            
            execution_time = time.time() - start_time
            self.update_metrics(execution_time, True)
            
            return AgentResponse(
                success=True,
                data=analysis_results,
                message="Content analysis completed successfully",
                agent_type=self.agent_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_metrics(execution_time, False)
            
            logger.error(f"Content processing error: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                agent_type=self.agent_id,
                execution_time=execution_time
            )
    
    def _detect_content_type(self, file_path: Path) -> str:
        """Detect content type from file extension"""
        suffix = file_path.suffix.lower()
        
        for content_type, extensions in self.supported_formats.items():
            if suffix in extensions:
                return content_type
        
        # Use mimetypes as fallback
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith('audio/'):
                return 'audio'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('image/'):
                return 'image'
            elif mime_type.startswith('text/'):
                return 'text'
        
        return 'unknown'
    
    async def _process_content_by_type(
        self, 
        content_path: Path, 
        content_type: str,
        analysis_options: List[str],
        optimization_options: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Route content to appropriate processor based on type"""
        
        base_results = {
            'content_path': str(content_path),
            'content_type': content_type,
            'file_size': content_path.stat().st_size,
            'created_at': datetime.fromtimestamp(content_path.stat().st_ctime),
            'modified_at': datetime.fromtimestamp(content_path.stat().st_mtime),
            'file_hash': await self._calculate_file_hash(content_path),
            'analysis_timestamp': datetime.utcnow()
        }
        
        if content_type == 'audio':
            processor_results = await self.audio_processor.process(
                content_path, analysis_options, optimization_options, metadata
            )
        elif content_type == 'video':
            processor_results = await self.video_processor.process(
                content_path, analysis_options, optimization_options, metadata
            )
        elif content_type == 'image':
            processor_results = await self.image_processor.process(
                content_path, analysis_options, optimization_options, metadata
            )
        elif content_type == 'text':
            processor_results = await self.text_processor.process(
                content_path, analysis_options, optimization_options, metadata
            )
        else:
            raise ContentProcessingError(f"Unsupported content type: {content_type}")
        
        # Merge base results with processor-specific results
        base_results.update(processor_results)
        
        # Add AI analysis if requested
        if 'ai_analysis' in analysis_options:
            ai_results = await self._perform_ai_analysis(base_results, content_type)
            base_results['ai_analysis'] = ai_results
        
        # Generate recommendations
        if 'recommendations' in analysis_options:
            recommendations = await self._generate_recommendations(base_results)
            base_results['recommendations'] = recommendations
        
        return base_results
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _perform_ai_analysis(self, content_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """
Perform AI-powered analysis on content"""
        ai_results = {}
        
        try:
            # Content classification
            if self.content_classifier:
                classification = await self.content_classifier.classify(content_data)
                ai_results['classification'] = classification
            
            # Quality assessment
            if self.quality_assessor:
                quality_score = await self.quality_assessor.assess(content_data)
                ai_results['quality_score'] = quality_score
            
            # Sentiment analysis for text content
            if content_type == 'text' and 'text_content' in content_data:
                sentiment = self.sentiment_analyzer(content_data['text_content'][:512])
                ai_results['sentiment'] = sentiment[0]
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            ai_results['error'] = str(e)
        
        return ai_results
    
    async def _generate_recommendations(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization and improvement recommendations"""
        recommendations = {
            'optimization': [],
            'quality_improvements': [],
            'seo_suggestions': [],
            'format_suggestions': [],
            'metadata_enhancements': []
        }
        
        try:
            content_type = content_data['content_type']
            
            # Quality-based recommendations
            if 'quality_score' in content_data.get('ai_analysis', {}):
                quality_score = content_data['ai_analysis']['quality_score']
                if quality_score < 0.7:
                    recommendations['quality_improvements'].append(
                        "Consider improving content quality - current score is below optimal threshold"
                    )
            
            # Format-specific recommendations
            if content_type == 'audio':
                await self._add_audio_recommendations(content_data, recommendations)
            elif content_type == 'video':
                await self._add_video_recommendations(content_data, recommendations)
            elif content_type == 'image':
                await self._add_image_recommendations(content_data, recommendations)
            elif content_type == 'text':
                await self._add_text_recommendations(content_data, recommendations)
            
            # SEO recommendations
            if not content_data.get('metadata', {}).get('title'):
                recommendations['seo_suggestions'].append("Add a descriptive title for better SEO")
            
            if not content_data.get('metadata', {}).get('description'):
                recommendations['seo_suggestions'].append("Add a detailed description for better discoverability")
            
            if not content_data.get('metadata', {}).get('tags'):
                recommendations['seo_suggestions'].append("Add relevant tags/keywords for better categorization")
        
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            recommendations['error'] = str(e)
        
        return recommendations
    
    async def _add_audio_recommendations(self, content_data: Dict[str, Any], recommendations: Dict[str, Any]):
        """Add audio-specific recommendations"""
        audio_data = content_data.get('audio_analysis', {})
        
        if audio_data.get('sample_rate', 0) < 44100:
            recommendations['quality_improvements'].append("Consider using higher sample rate (44.1kHz or higher)")
        
        if audio_data.get('bit_depth', 0) < 16:
            recommendations['quality_improvements'].append("Consider using higher bit depth (16-bit or higher)")
        
        if audio_data.get('loudness', 0) < -23:
            recommendations['optimization'].append("Audio might be too quiet - consider normalization")
        
        if not audio_data.get('has_metadata'):
            recommendations['metadata_enhancements'].append("Add ID3 tags for better music library organization")
    
    async def _add_video_recommendations(self, content_data: Dict[str, Any], recommendations: Dict[str, Any]):
        """Add video-specific recommendations"""
        video_data = content_data.get('video_analysis', {})
        
        if video_data.get('resolution', [0, 0])[1] < 720:
            recommendations['quality_improvements'].append("Consider using HD resolution (720p or higher)")
        
        if video_data.get('fps', 0) < 24:
            recommendations['quality_improvements'].append("Consider using standard frame rate (24fps or higher)")
        
        if video_data.get('bitrate', 0) < 1000000:  # 1 Mbps
            recommendations['quality_improvements'].append("Consider higher bitrate for better quality")
        
        if not video_data.get('has_subtitles'):
            recommendations['metadata_enhancements'].append("Add subtitles for accessibility")
    
    async def _add_image_recommendations(self, content_data: Dict[str, Any], recommendations: Dict[str, Any]):
        """Add image-specific recommendations"""
        image_data = content_data.get('image_analysis', {})
        
        width, height = image_data.get('dimensions', [0, 0])
        if width < 1920 or height < 1080:
            recommendations['quality_improvements'].append("Consider using higher resolution for better quality")
        
        if image_data.get('dpi', 0) < 300:
            recommendations['format_suggestions'].append("For print use, consider 300 DPI or higher")
        
        if not image_data.get('has_exif'):
            recommendations['metadata_enhancements'].append("Add EXIF metadata for better organization")
    
    async def _add_text_recommendations(self, content_data: Dict[str, Any], recommendations: Dict[str, Any]):
        """Add text-specific recommendations"""
        text_data = content_data.get('text_analysis', {})
        
        word_count = text_data.get('word_count', 0)
        if word_count < 300:
            recommendations['seo_suggestions'].append("Consider expanding content - longer articles tend to rank better")
        
        if text_data.get('readability_score', 0) < 60:
            recommendations['quality_improvements'].append("Consider improving readability with simpler language")
        
        if not text_data.get('has_headings'):
            recommendations['seo_suggestions'].append("Add headings (H1, H2, etc.) for better structure")


class AudioContentProcessor:
    """Advanced audio content processing and analysis"""
    
    async def process(
        self, 
        file_path: Path, 
        analysis_options: List[str],
        optimization_options: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Process audio content with comprehensive analysis"""
        
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            
            results = {
                'audio_analysis': {
                    'duration': len(y) / sr,
                    'sample_rate': sr,
                    'channels': 1 if len(y.shape) == 1 else y.shape[0],
                    'samples': len(y),
                    'bit_depth': 16,  # Default, could be extracted from file
                    'format': file_path.suffix.lower(),
                    'file_size_mb': file_path.stat().st_size / (1024 * 1024)
                }
            }
            
            if 'detailed' in analysis_options:
                # Advanced audio analysis
                results['audio_analysis'].update(await self._detailed_audio_analysis(y, sr))
            
            if 'quality' in analysis_options:
                # Quality assessment
                results['audio_analysis']['quality_metrics'] = await self._assess_audio_quality(y, sr)
            
            if 'metadata' in analysis_options:
                # Extract metadata
                results['audio_analysis']['metadata'] = await self._extract_audio_metadata(file_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            raise ContentProcessingError(f"Audio processing failed: {e}")
    
    async def _detailed_audio_analysis(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Perform detailed audio analysis"""
        
        # Spectral analysis
        stft = librosa.stft(y)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        # Rhythm analysis
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Energy analysis
        rms_energy = librosa.feature.rms(y=y)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
        
        # MFCCs for timbral analysis
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        return {
            'tempo': float(tempo),
            'beats_count': len(beats),
            'spectral_centroid_mean': float(np.mean(spectral_centroids)),
            'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
            'rms_energy_mean': float(np.mean(rms_energy)),
            'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
            'mfccs_mean': np.mean(mfccs, axis=1).tolist(),
            'loudness': float(np.mean(librosa.amplitude_to_db(rms_energy))),
            'dynamic_range': float(np.max(rms_energy) - np.min(rms_energy))
        }
    
    async def _assess_audio_quality(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
Assess audio quality metrics"""
        
        # Signal-to-noise ratio estimation
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        
        # Estimate noise floor (bottom 10th percentile)
        noise_floor = np.percentile(magnitude, 10)
        signal_power = np.mean(magnitude)
        snr_estimate = 20 * np.log10(signal_power / noise_floor) if noise_floor > 0 else 100
        
        # Dynamic range
        rms = librosa.feature.rms(y=y)[0]
        dynamic_range = 20 * np.log10(np.max(rms) / np.min(rms)) if np.min(rms) > 0 else 0
        
        # Clipping detection
        clipping_ratio = np.sum(np.abs(y) > 0.99) / len(y)
        
        # Overall quality score (0-1)
        quality_score = min(1.0, (
            (min(snr_estimate / 40, 1.0) * 0.4) +  # SNR weight
            (min(dynamic_range / 40, 1.0) * 0.3) +  # Dynamic range weight
            ((1 - clipping_ratio) * 0.3)  # Anti-clipping weight
        ))
        
        return {
            'snr_estimate': float(snr_estimate),
            'dynamic_range': float(dynamic_range),
            'clipping_ratio': float(clipping_ratio),
            'quality_score': float(quality_score),
            'quality_rating': 'excellent' if quality_score > 0.8 else 
                            'good' if quality_score > 0.6 else 
                            'fair' if quality_score > 0.4 else 'poor'
        }
    
    async def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
Extract audio metadata"""
        try:
            import mutagen
            from mutagen.id3 import ID3NoHeaderError
            
            try:
                audio_file = mutagen.File(file_path)
                if audio_file is not None:
                    return {
                        'title': audio_file.get('TIT2', [''])[0] if audio_file.get('TIT2') else '',
                        'artist': audio_file.get('TPE1', [''])[0] if audio_file.get('TPE1') else '',
                        'album': audio_file.get('TALB', [''])[0] if audio_file.get('TALB') else '',
                        'date': audio_file.get('TDRC', [''])[0] if audio_file.get('TDRC') else '',
                        'genre': audio_file.get('TCON', [''])[0] if audio_file.get('TCON') else '',
                        'has_metadata': True
                    }
            except (ID3NoHeaderError, Exception):
                pass
            
            return {'has_metadata': False}
            
        except ImportError:
            logger.warning("Mutagen not available for metadata extraction")
            return {'has_metadata': False, 'error': 'Metadata extraction not available'}


class VideoContentProcessor:
    """Advanced video content processing and analysis"""
    
    async def process(
        self, 
        file_path: Path, 
        analysis_options: List[str],
        optimization_options: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Process video content with comprehensive analysis"""
        
        try:
            # Open video file
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                raise ContentProcessingError("Failed to open video file")
            
            # Get basic properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            results = {
                'video_analysis': {
                    'duration': duration,
                    'fps': fps,
                    'frame_count': frame_count,
                    'resolution': [width, height],
                    'aspect_ratio': width / height if height > 0 else 0,
                    'format': file_path.suffix.lower(),
                    'file_size_mb': file_path.stat().st_size / (1024 * 1024)
                }
            }
            
            if 'detailed' in analysis_options:
                results['video_analysis'].update(await self._detailed_video_analysis(cap, frame_count))
            
            if 'quality' in analysis_options:
                results['video_analysis']['quality_metrics'] = await self._assess_video_quality(cap, frame_count, fps)
            
            cap.release()
            
            if 'metadata' in analysis_options:
                results['video_analysis']['metadata'] = await self._extract_video_metadata(file_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Video processing error: {e}")
            raise ContentProcessingError(f"Video processing failed: {e}")
    
    async def _detailed_video_analysis(self, cap: cv2.VideoCapture, frame_count: int) -> Dict[str, Any]:
        """Perform detailed video analysis"""
        
        # Sample frames for analysis (max 30 frames)
        sample_indices = np.linspace(0, frame_count - 1, min(30, frame_count), dtype=int)
        
        brightness_values = []
        contrast_values = []
        motion_values = []
        prev_frame = None
        
        for i, frame_idx in enumerate(sample_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Brightness analysis
                brightness = np.mean(gray)
                brightness_values.append(brightness)
                
                # Contrast analysis
                contrast = np.std(gray)
                contrast_values.append(contrast)
                
                # Motion analysis
                if prev_frame is not None:
                    flow = cv2.calcOpticalFlowPyrLK(
                        prev_frame, gray, 
                        np.array([[100, 100]], dtype=np.float32).reshape(-1, 1, 2),
                        None
                    )[0]
                    if flow is not None:
                        motion = np.mean(np.abs(flow))
                        motion_values.append(motion)
                
                prev_frame = gray.copy()
        
        return {
            'brightness_mean': float(np.mean(brightness_values)),
            'brightness_std': float(np.std(brightness_values)),
            'contrast_mean': float(np.mean(contrast_values)),
            'contrast_std': float(np.std(contrast_values)),
            'motion_mean': float(np.mean(motion_values)) if motion_values else 0.0,
            'frames_analyzed': len(sample_indices)
        }
    
    async def _assess_video_quality(self, cap: cv2.VideoCapture, frame_count: int, fps: float) -> Dict[str, Any]:
        """
Assess video quality metrics"""
        
        # Resolution-based quality
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        resolution_quality = 1.0
        if height >= 2160:  # 4K
            resolution_quality = 1.0
        elif height >= 1080:  # HD
            resolution_quality = 0.9
        elif height >= 720:  # HD Ready
            resolution_quality = 0.7
        elif height >= 480:  # SD
            resolution_quality = 0.5
        else:
            resolution_quality = 0.3
        
        # Frame rate quality
        fps_quality = min(1.0, fps / 30.0) if fps > 0 else 0.0
        
        # Sample frame quality
        sample_count = min(10, frame_count)
        frame_qualities = []
        
        for i in range(sample_count):
            frame_idx = int(i * frame_count / sample_count)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                # Simple sharpness metric using Laplacian variance
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                frame_qualities.append(sharpness)
        
        avg_sharpness = np.mean(frame_qualities) if frame_qualities else 0
        sharpness_quality = min(1.0, avg_sharpness / 1000.0)  # Normalize
        
        # Overall quality score
        overall_quality = (resolution_quality * 0.4 + fps_quality * 0.3 + sharpness_quality * 0.3)
        
        return {
            'resolution_quality': resolution_quality,
            'fps_quality': fps_quality,
            'sharpness_quality': sharpness_quality,
            'average_sharpness': float(avg_sharpness),
            'overall_quality': float(overall_quality),
            'quality_rating': 'excellent' if overall_quality > 0.8 else 
                            'good' if overall_quality > 0.6 else 
                            'fair' if overall_quality > 0.4 else 'poor'
        }
    
    async def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
Extract video metadata"""
        try:
            import ffmpeg
            
            probe = ffmpeg.probe(str(file_path))
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            if video_stream:
                return {
                    'codec': video_stream.get('codec_name', ''),
                    'bitrate': int(video_stream.get('bit_rate', 0)) if video_stream.get('bit_rate') else 0,
                    'profile': video_stream.get('profile', ''),
                    'level': video_stream.get('level', ''),
                    'color_space': video_stream.get('color_space', ''),
                    'has_metadata': True
                }
            
            return {'has_metadata': False}
            
        except (ImportError, Exception) as e:
            logger.warning(f"Video metadata extraction failed: {e}")
            return {'has_metadata': False, 'error': str(e)}


class ImageContentProcessor:
    """Advanced image content processing and analysis"""
    
    async def process(
        self, 
        file_path: Path, 
        analysis_options: List[str],
        optimization_options: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Process image content with comprehensive analysis"""
        
        try:
            # Open image
            with Image.open(file_path) as img:
                width, height = img.size
                mode = img.mode
                format_name = img.format
                
                results = {
                    'image_analysis': {
                        'dimensions': [width, height],
                        'aspect_ratio': width / height if height > 0 else 0,
                        'mode': mode,
                        'format': format_name,
                        'file_size_mb': file_path.stat().st_size / (1024 * 1024)
                    }
                }
                
                if 'detailed' in analysis_options:
                    results['image_analysis'].update(await self._detailed_image_analysis(img))
                
                if 'quality' in analysis_options:
                    results['image_analysis']['quality_metrics'] = await self._assess_image_quality(img)
                
                if 'metadata' in analysis_options:
                    results['image_analysis']['metadata'] = await self._extract_image_metadata(img)
            
            return results
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise ContentProcessingError(f"Image processing failed: {e}")
    
    async def _detailed_image_analysis(self, img: Image.Image) -> Dict[str, Any]:
        """Perform detailed image analysis"""
        
        # Convert to numpy array for analysis
        img_array = np.array(img.convert('RGB'))
        
        # Color analysis
        mean_color = np.mean(img_array, axis=(0, 1))
        dominant_color = self._get_dominant_color(img_array)
        
        # Brightness and contrast
        gray = np.mean(img_array, axis=2)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Edge detection for sharpness
        from scipy import ndimage
        edges = ndimage.sobel(gray)
        sharpness = np.mean(edges)
        
        return {
            'mean_color': mean_color.tolist(),
            'dominant_color': dominant_color,
            'brightness': float(brightness),
            'contrast': float(contrast),
            'sharpness': float(sharpness),
            'color_channels': img_array.shape[2] if len(img_array.shape) > 2 else 1
        }
    
    def _get_dominant_color(self, img_array: np.ndarray) -> List[int]:
        """
Get dominant color using k-means clustering"""
        try:
            from sklearn.cluster import KMeans
            
            # Reshape for clustering
            pixels = img_array.reshape(-1, 3)
            
            # Sample pixels for performance
            if len(pixels) > 10000:
                indices = np.random.choice(len(pixels), 10000, replace=False)
                pixels = pixels[indices]
            
            # Perform k-means clustering
            kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            return kmeans.cluster_centers_[0].astype(int).tolist()
            
        except ImportError:
            # Fallback to mean color
            return np.mean(img_array, axis=(0, 1)).astype(int).tolist()
    
    async def _assess_image_quality(self, img: Image.Image) -> Dict[str, Any]:
        """
Assess image quality metrics"""
        
        width, height = img.size
        
        # Resolution quality
        pixel_count = width * height
        resolution_quality = min(1.0, pixel_count / (1920 * 1080))  # Normalize to HD
        
        # Aspect ratio quality (penalize extreme ratios)
        aspect_ratio = width / height if height > 0 else 1
        aspect_quality = 1.0 - min(0.5, abs(aspect_ratio - 16/9) / 10)  # Prefer 16:9
        
        # File format quality
        format_quality = 1.0
        if img.format in ['JPEG', 'PNG', 'WEBP']:
            format_quality = 1.0
        elif img.format in ['GIF', 'BMP']:
            format_quality = 0.8
        else:
            format_quality = 0.6
        
        # Overall quality
        overall_quality = (resolution_quality * 0.5 + aspect_quality * 0.3 + format_quality * 0.2)
        
        return {
            'resolution_quality': resolution_quality,
            'aspect_quality': aspect_quality,
            'format_quality': format_quality,
            'overall_quality': float(overall_quality),
            'quality_rating': 'excellent' if overall_quality > 0.8 else 
                            'good' if overall_quality > 0.6 else 
                            'fair' if overall_quality > 0.4 else 'poor'
        }
    
    async def _extract_image_metadata(self, img: Image.Image) -> Dict[str, Any]:
        """
Extract image EXIF metadata"""
        try:
            from PIL.ExifTags import TAGS
            
            exifdata = img.getexif()
            metadata = {}
            
            if exifdata:
                for tag_id in exifdata:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exifdata.get(tag_id)
                    
                    if isinstance(data, bytes):
                        try:
                            data = data.decode('utf-8')
                        except:
                            data = str(data)
                    
                    metadata[tag] = data
                
                return {
                    'has_exif': True,
                    'exif_data': metadata,
                    'camera_make': metadata.get('Make', ''),
                    'camera_model': metadata.get('Model', ''),
                    'datetime': metadata.get('DateTime', ''),
                    'dpi': img.info.get('dpi', (72, 72))[0]
                }
            
            return {
                'has_exif': False,
                'dpi': img.info.get('dpi', (72, 72))[0]
            }
            
        except Exception as e:
            logger.warning(f"EXIF extraction failed: {e}")
            return {'has_exif': False, 'error': str(e)}


class TextContentProcessor:
    """Advanced text content processing and analysis"""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
    
    async def initialize_models(self):
        """
Initialize NLP models"""
        try:
            from transformers import AutoTokenizer, AutoModel
            
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            
        except Exception as e:
            logger.warning(f"Failed to initialize NLP models: {e}")
    
    async def process(
        self, 
        file_path: Path, 
        analysis_options: List[str],
        optimization_options: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process text content with comprehensive analysis"""
        
        try:
            # Read text content
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = await f.read()
            
            results = {
                'text_analysis': {
                    'character_count': len(text_content),
                    'word_count': len(text_content.split()),
                    'line_count': len(text_content.splitlines()),
                    'paragraph_count': len([p for p in text_content.split('\n\n') if p.strip()]),
                    'format': file_path.suffix.lower(),
                    'file_size_mb': file_path.stat().st_size / (1024 * 1024),
                    'encoding': 'utf-8'
                },
                'text_content': text_content[:1000]  # First 1000 chars for preview
            }
            
            if 'detailed' in analysis_options:
                results['text_analysis'].update(await self._detailed_text_analysis(text_content))
            
            if 'quality' in analysis_options:
                results['text_analysis']['quality_metrics'] = await self._assess_text_quality(text_content)
            
            if 'seo' in analysis_options:
                results['text_analysis']['seo_metrics'] = await self._analyze_seo_factors(text_content)
            
            return results
            
        except Exception as e:
            logger.error(f"Text processing error: {e}")
            raise ContentProcessingError(f"Text processing failed: {e}")
    
    async def _detailed_text_analysis(self, text: str) -> Dict[str, Any]:
        """Perform detailed text analysis"""
        
        import re
        from collections import Counter
        
        # Sentence analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Word frequency analysis
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        most_common = word_freq.most_common(10)
        
        # Language detection
        language = await self._detect_language(text)
        
        # Structure analysis
        headings = len(re.findall(r'^#+\s', text, re.MULTILINE))  # Markdown headings
        links = len(re.findall(r'https?://[^\s]+', text))
        emails = len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        
        return {
            'sentence_count': len(sentences),
            'average_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'unique_words': len(set(words)),
            'vocabulary_richness': len(set(words)) / len(words) if words else 0,
            'most_common_words': most_common,
            'language': language,
            'has_headings': headings > 0,
            'heading_count': headings,
            'link_count': links,
            'email_count': emails
        }
    
    async def _detect_language(self, text: str) -> str:
        """
Detect text language"""
        try:
            from langdetect import detect
            return detect(text)
        except:
            return 'unknown'
    
    async def _assess_text_quality(self, text: str) -> Dict[str, Any]:
        """
Assess text quality metrics"""
        
        # Readability assessment using simple metrics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Flesch Reading Ease approximation
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (avg_word_length / 4.7))
        readability_score = max(0, min(100, readability_score))
        
        # Content density
        unique_words = len(set(word.lower() for word in words))
        content_density = unique_words / len(words) if words else 0
        
        # Overall quality score
        quality_factors = [
            min(1.0, len(words) / 300),  # Length factor (300+ words is good)
            min(1.0, readability_score / 60),  # Readability factor
            content_density,  # Vocabulary richness
            min(1.0, (20 - avg_sentence_length) / 20) if avg_sentence_length > 0 else 0  # Sentence length factor
        ]
        
        overall_quality = sum(quality_factors) / len(quality_factors)
        
        return {
            'readability_score': float(readability_score),
            'avg_sentence_length': float(avg_sentence_length),
            'avg_word_length': float(avg_word_length),
            'content_density': float(content_density),
            'overall_quality': float(overall_quality),
            'quality_rating': 'excellent' if overall_quality > 0.8 else 
                            'good' if overall_quality > 0.6 else 
                            'fair' if overall_quality > 0.4 else 'poor'
        }
    
    async def _analyze_seo_factors(self, text: str) -> Dict[str, Any]:
        """
Analyze SEO factors in text"""
        
        import re
        from collections import Counter
        
        # Keyword density analysis
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # Find potential keywords (words appearing 2+ times, longer than 3 chars)
        keywords = [word for word, count in word_freq.items() 
                   if count >= 2 and len(word) > 3 and word.isalpha()]
        
        # Structure analysis
        headings = re.findall(r'^#+\s(.+)$', text, re.MULTILINE)
        title = headings[0] if headings else ""
        
        # Meta description approximation (first 160 chars)
        meta_desc = text[:160].strip()
        if len(meta_desc) == 160:
            meta_desc = meta_desc.rsplit(' ', 1)[0] + "..."
        
        return {
            'word_count': len(words),
            'title': title,
            'meta_description': meta_desc,
            'potential_keywords': keywords[:10],  # Top 10
            'keyword_density': {word: (count / len(words)) * 100 
                               for word, count in word_freq.most_common(5)},
            'has_title': bool(title),
            'has_headings': len(headings) > 0,
            'heading_structure': len(headings),
            'seo_score': self._calculate_seo_score(words, headings, keywords)
        }
    
    def _calculate_seo_score(self, words: List[str], headings: List[str], keywords: List[str]) -> float:
        """Calculate basic SEO score"""
        score = 0
        
        # Length factor (300-2000 words is optimal)
        word_count = len(words)
        if 300 <= word_count <= 2000:
            score += 30
        elif word_count < 300:
            score += (word_count / 300) * 30
        else:
            score += 30 * (2000 / word_count)
        
        # Heading factor
        if headings:
            score += min(20, len(headings) * 5)
        
        # Keyword factor
        if keywords:
            score += min(30, len(keywords) * 3)
        
        # Structure factor
        if len(headings) > 1:
            score += 20
        
        return min(100, score)
