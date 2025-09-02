"""Content Processing Engine - IA Influencer Agent Platform
=======================================================

Core engine for processing multi-format content (audio, video, image, text) with AI-powered
analysis, optimization, and intelligent metadata extraction for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from uuid import UUID, uuid4

import aiofiles
import cv2
import librosa
import numpy as np
import torch
from PIL import Image
from moviepy.editor import VideoFileClip
from mutagen import File as MutagenFile
from transformers import pipeline

from ...core.config import get_settings
from ...core.database import get_database
from ...core.exceptions import ContentProcessingError
from ...core.logging import get_logger
from ...models.content import ContentModel, ProcessingStatus
from ...security.encryption import encrypt_sensitive_data
from ...utils.file_handler import FileHandler
from ...utils.validation import validate_file_size, validate_file_type

logger = get_logger(__name__)
settings = get_settings()


class ContentProcessingEngine:
    """
Advanced multi-format content processing engine with AI capabilities."""
    
    def __init__(self):
        self.db = get_database()
        self.file_handler = FileHandler()
        self.supported_formats = {
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.svg'],
            'text': ['.txt', '.md', '.doc', '.docx', '.pdf', '.rtf']
        }
        self.max_file_sizes = {
            'audio': 500 * 1024 * 1024,  # 500MB
            'video': 2 * 1024 * 1024 * 1024,  # 2GB
            'image': 50 * 1024 * 1024,  # 50MB
            'text': 10 * 1024 * 1024  # 10MB
        }
        
    async def process_content(
        self,
        file_path: Path,
        user_id: UUID,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process uploaded content with comprehensive analysis and AI enhancement.
        
        Args:
            file_path: Path to the uploaded content file
            user_id: ID of the content creator
            content_type: Type of content (audio, video, image, text)
            metadata: Additional metadata provided by user
            
        Returns:
            Processing results with content ID and analysis data
        """
        try:
            # Validate file
            await self._validate_content_file(file_path, content_type)
            
            # Create content record
            content_id = uuid4()
            content_record = await self._create_content_record(
                content_id, user_id, file_path, content_type, metadata
            )
            
            # Process based on content type
            processing_result = await self._process_by_type(
                file_path, content_type, content_id
            )
            
            # Update content record with results
            await self._update_content_record(content_id, processing_result)
            
            # Generate AI insights
            ai_insights = await self._generate_ai_insights(
                file_path, content_type, processing_result
            )
            
            # Prepare response
            response = {
                'content_id': str(content_id),
                'status': 'processed',
                'content_type': content_type,
                'file_info': processing_result.get('file_info', {}),
                'technical_analysis': processing_result.get('technical_analysis', {}),
                'ai_insights': ai_insights,
                'processing_timestamp': datetime.utcnow().isoformat(),
                'recommendations': await self._generate_recommendations(
                    content_type, processing_result, ai_insights
                )
            }
            
            logger.info(f"Content processed successfully: {content_id}")
            return response
            
        except Exception as e:
            logger.error(f"Content processing failed: {str(e)}")
            raise ContentProcessingError(f"Failed to process content: {str(e)}")
    
    async def _validate_content_file(self, file_path: Path, content_type: str) -> None:
        """Validate content file format and size."""
        if not file_path.exists():
            raise ContentProcessingError("File does not exist")
            
        file_extension = file_path.suffix.lower()
        if file_extension not in self.supported_formats.get(content_type, []):
            raise ContentProcessingError(f"Unsupported {content_type} format: {file_extension}")
            
        file_size = file_path.stat().st_size
        max_size = self.max_file_sizes.get(content_type, 100 * 1024 * 1024)
        if file_size > max_size:
            raise ContentProcessingError(f"File too large. Max size: {max_size} bytes")
    
    async def _create_content_record(
        self,
        content_id: UUID,
        user_id: UUID,
        file_path: Path,
        content_type: str,
        metadata: Optional[Dict[str, Any]]
    ) -> ContentModel:
        """Create initial content record in database."""
        content_data = {
            'id': content_id,
            'user_id': user_id,
            'filename': file_path.name,
            'content_type': content_type,
            'file_size': file_path.stat().st_size,
            'mime_type': mimetypes.guess_type(str(file_path))[0],
            'status': ProcessingStatus.PROCESSING,
            'metadata': metadata or {},
            'created_at': datetime.utcnow()
        }
        
        return await self.db.content.create(content_data)
    
    async def _process_by_type(
        self,
        file_path: Path,
        content_type: str,
        content_id: UUID
    ) -> Dict[str, Any]:
        """
Process content based on its type."""
        processors = {
            'audio': self._process_audio,
            'video': self._process_video,
            'image': self._process_image,
            'text': self._process_text
        }
        
        processor = processors.get(content_type)
        if not processor:
            raise ContentProcessingError(f"No processor for content type: {content_type}")
            
        return await processor(file_path, content_id)
    
    async def _process_audio(self, file_path: Path, content_id: UUID) -> Dict[str, Any]:
        """Process audio content with advanced analysis."""
        try:
            # Load audio file
            y, sr = librosa.load(str(file_path), sr=None)
            duration = len(y) / sr
            
            # Extract metadata using mutagen
            audio_file = MutagenFile(str(file_path))
            metadata = {}
            if audio_file:
                metadata = {
                    'title': audio_file.get('TIT2', [''])[0] if audio_file.get('TIT2') else '',
                    'artist': audio_file.get('TPE1', [''])[0] if audio_file.get('TPE1') else '',
                    'album': audio_file.get('TALB', [''])[0] if audio_file.get('TALB') else '',
                    'genre': audio_file.get('TCON', [''])[0] if audio_file.get('TCON') else '',
                    'year': audio_file.get('TDRC', [''])[0] if audio_file.get('TDRC') else ''
                }
            
            # Technical analysis
            technical_analysis = {
                'duration': float(duration),
                'sample_rate': int(sr),
                'channels': 1 if len(y.shape) == 1 else y.shape[0],
                'bit_depth': 'unknown',  # Would need more detailed analysis
                'dynamic_range': float(np.max(y) - np.min(y)),
                'rms_energy': float(np.sqrt(np.mean(y**2))),
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                'tempo': float(librosa.tempo(y=y, sr=sr)[0]),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y)))
            }
            
            # Audio quality assessment
            quality_metrics = {
                'loudness_lufs': self._calculate_loudness(y, sr),
                'peak_level': float(np.max(np.abs(y))),
                'stereo_width': self._calculate_stereo_width(y),
                'frequency_balance': self._analyze_frequency_balance(y, sr)
            }
            
            return {
                'file_info': {
                    'duration': duration,
                    'format': file_path.suffix.lower(),
                    'size': file_path.stat().st_size
                },
                'metadata': metadata,
                'technical_analysis': technical_analysis,
                'quality_metrics': quality_metrics
            }
            
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            raise ContentProcessingError(f"Audio processing error: {str(e)}")
    
    async def _process_video(self, file_path: Path, content_id: UUID) -> Dict[str, Any]:
        """Process video content with comprehensive analysis."""
        try:
            # Load video file
            clip = VideoFileClip(str(file_path))
            duration = clip.duration
            fps = clip.fps
            resolution = (clip.w, clip.h)
            
            # Extract first frame for thumbnail
            frame = clip.get_frame(0)
            thumbnail_path = f"thumbnails/{content_id}_thumb.jpg"
            
            # Technical analysis
            technical_analysis = {
                'duration': float(duration),
                'fps': float(fps),
                'resolution': f"{resolution[0]}x{resolution[1]}",
                'aspect_ratio': float(resolution[0] / resolution[1]),
                'video_codec': 'unknown',  # Would need ffprobe integration
                'audio_codec': 'unknown',
                'bitrate': 'unknown'
            }
            
            # Video quality analysis
            quality_metrics = {
                'sharpness': self._calculate_video_sharpness(frame),
                'brightness': float(np.mean(frame)),
                'contrast': float(np.std(frame)),
                'color_distribution': self._analyze_color_distribution(frame),
                'motion_intensity': self._calculate_motion_intensity(clip)
            }
            
            # Scene detection
            scene_analysis = {
                'scene_changes': self._detect_scene_changes(clip),
                'dominant_colors': self._extract_dominant_colors(frame),
                'lighting_conditions': self._analyze_lighting(frame)
            }
            
            clip.close()
            
            return {
                'file_info': {
                    'duration': duration,
                    'format': file_path.suffix.lower(),
                    'size': file_path.stat().st_size,
                    'thumbnail': thumbnail_path
                },
                'technical_analysis': technical_analysis,
                'quality_metrics': quality_metrics,
                'scene_analysis': scene_analysis
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            raise ContentProcessingError(f"Video processing error: {str(e)}")
    
    async def _process_image(self, file_path: Path, content_id: UUID) -> Dict[str, Any]:
        """Process image content with AI-powered analysis."""
        try:
            # Load image
            image = Image.open(file_path)
            width, height = image.size
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Technical analysis
            technical_analysis = {
                'dimensions': f"{width}x{height}",
                'aspect_ratio': float(width / height),
                'color_mode': image.mode,
                'channels': len(img_array.shape),
                'file_format': image.format,
                'compression': getattr(image, 'compression', 'unknown')
            }
            
            # Image quality metrics
            quality_metrics = {
                'sharpness': self._calculate_image_sharpness(img_array),
                'brightness': float(np.mean(img_array)),
                'contrast': float(np.std(img_array)),
                'saturation': self._calculate_saturation(img_array),
                'noise_level': self._estimate_noise_level(img_array)
            }
            
            # Color analysis
            color_analysis = {
                'dominant_colors': self._extract_image_dominant_colors(img_array),
                'color_harmony': self._analyze_color_harmony(img_array),
                'temperature': self._calculate_color_temperature(img_array),
                'histogram': self._generate_color_histogram(img_array)
            }
            
            # Composition analysis
            composition_analysis = {
                'rule_of_thirds': self._check_rule_of_thirds(img_array),
                'symmetry': self._analyze_symmetry(img_array),
                'leading_lines': self._detect_leading_lines(img_array),
                'focal_points': self._identify_focal_points(img_array)
            }
            
            return {
                'file_info': {
                    'dimensions': f"{width}x{height}",
                    'format': file_path.suffix.lower(),
                    'size': file_path.stat().st_size
                },
                'technical_analysis': technical_analysis,
                'quality_metrics': quality_metrics,
                'color_analysis': color_analysis,
                'composition_analysis': composition_analysis
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise ContentProcessingError(f"Image processing error: {str(e)}")
    
    async def _process_text(self, file_path: Path, content_id: UUID) -> Dict[str, Any]:
        """Process text content with NLP analysis."""
        try:
            # Read text content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                text_content = await file.read()
            
            # Basic text statistics
            words = text_content.split()
            sentences = text_content.split('.')
            paragraphs = text_content.split('\n\n')
            
            # Technical analysis
            technical_analysis = {
                'character_count': len(text_content),
                'word_count': len(words),
                'sentence_count': len(sentences),
                'paragraph_count': len(paragraphs),
                'average_words_per_sentence': len(words) / len(sentences) if sentences else 0,
                'reading_time_minutes': len(words) / 200  # Average reading speed
            }
            
            # Language analysis using transformers
            sentiment_pipeline = pipeline("sentiment-analysis")
            sentiment_result = sentiment_pipeline(text_content[:512])  # Limit for model
            
            # Readability analysis
            readability_metrics = {
                'flesch_reading_ease': self._calculate_flesch_score(text_content),
                'average_sentence_length': len(words) / len(sentences) if sentences else 0,
                'complex_words_ratio': self._calculate_complex_words_ratio(words),
                'passive_voice_ratio': self._detect_passive_voice_ratio(text_content)
            }
            
            # Content analysis
            content_analysis = {
                'sentiment': sentiment_result[0] if sentiment_result else {'label': 'NEUTRAL', 'score': 0.5},
                'key_phrases': self._extract_key_phrases(text_content),
                'topics': self._identify_topics(text_content),
                'entities': self._extract_named_entities(text_content),
                'language': self._detect_language(text_content)
            }
            
            return {
                'file_info': {
                    'size': file_path.stat().st_size,
                    'format': file_path.suffix.lower(),
                    'encoding': 'utf-8'
                },
                'technical_analysis': technical_analysis,
                'readability_metrics': readability_metrics,
                'content_analysis': content_analysis
            }
            
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            raise ContentProcessingError(f"Text processing error: {str(e)}")
    
    # Audio analysis helper methods
    def _calculate_loudness(self, y: np.ndarray, sr: int) -> float:
        """Calculate LUFS loudness."""
        return float(-23.0 + 20 * np.log10(np.sqrt(np.mean(y**2)) + 1e-10))
    
    def _calculate_stereo_width(self, y: np.ndarray) -> float:
        """
Calculate stereo width if stereo audio."""
        if len(y.shape) > 1:
            correlation = np.corrcoef(y[0], y[1])[0, 1]
            return float(1.0 - abs(correlation))
        return 0.0
    
    def _analyze_frequency_balance(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
Analyze frequency balance across spectrum."""
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        freqs = librosa.fft_frequencies(sr=sr)
        
        # Define frequency bands
        low_band = np.where((freqs >= 20) & (freqs <= 250))[0]
        mid_band = np.where((freqs >= 250) & (freqs <= 4000))[0]
        high_band = np.where((freqs >= 4000) & (freqs <= 20000))[0]
        
        return {
            'low_energy': float(np.mean(magnitude[low_band])),
            'mid_energy': float(np.mean(magnitude[mid_band])),
            'high_energy': float(np.mean(magnitude[high_band]))
        }
    
    # Video analysis helper methods
    def _calculate_video_sharpness(self, frame: np.ndarray) -> float:
        """
Calculate video frame sharpness."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(laplacian.var())
    
    def _analyze_color_distribution(self, frame: np.ndarray) -> Dict[str, float]:
        """
Analyze color distribution in video frame."""
        return {
            'red_mean': float(np.mean(frame[:, :, 0])),
            'green_mean': float(np.mean(frame[:, :, 1])),
            'blue_mean': float(np.mean(frame[:, :, 2])),
            'color_variance': float(np.var(frame))
        }
    
    def _calculate_motion_intensity(self, clip) -> float:
        """
Calculate motion intensity in video."""
        # Simplified motion calculation
        frames = [clip.get_frame(t) for t in np.linspace(0, min(clip.duration, 10), 10)]
        motion_scores = []
        
        for i in range(1, len(frames)):
            diff = np.mean(np.abs(frames[i] - frames[i-1]))
            motion_scores.append(diff)
        
        return float(np.mean(motion_scores)) if motion_scores else 0.0
    
    def _detect_scene_changes(self, clip) -> List[float]:
        """
Detect scene changes in video."""
        # Simplified scene detection
        timestamps = []
        prev_frame = None
        
        for t in np.linspace(0, min(clip.duration, 60), 30):  # Sample 30 points
            frame = clip.get_frame(t)
            if prev_frame is not None:
                diff = np.mean(np.abs(frame - prev_frame))
                if diff > 50:  # Threshold for scene change
                    timestamps.append(float(t))
            prev_frame = frame
            
        return timestamps
    
    def _extract_dominant_colors(self, frame: np.ndarray) -> List[List[int]]:
        """
Extract dominant colors from frame."""
        from sklearn.cluster import KMeans
        
        pixels = frame.reshape(-1, 3)
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(pixels)
        
        return [color.astype(int).tolist() for color in kmeans.cluster_centers_]
    
    def _analyze_lighting(self, frame: np.ndarray) -> Dict[str, float]:
        """
Analyze lighting conditions in frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        return {
            'brightness': float(np.mean(gray)),
            'contrast': float(np.std(gray)),
            'dynamic_range': float(np.max(gray) - np.min(gray)),
            'exposure_quality': float(np.mean(gray) / 255.0)
        }
    
    # Image analysis helper methods
    def _calculate_image_sharpness(self, img_array: np.ndarray) -> float:
        """
Calculate image sharpness using Laplacian variance."""
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(laplacian.var())
    
    def _calculate_saturation(self, img_array: np.ndarray) -> float:
        """
Calculate image saturation."""
        if len(img_array.shape) == 3:
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            return float(np.mean(hsv[:, :, 1]))
        return 0.0
    
    def _estimate_noise_level(self, img_array: np.ndarray) -> float:
        """
Estimate noise level in image."""
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Use Laplacian to estimate noise
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(np.std(laplacian))
    
    def _extract_image_dominant_colors(self, img_array: np.ndarray) -> List[List[int]]:
        """
Extract dominant colors from image."""
        from sklearn.cluster import KMeans
        
        pixels = img_array.reshape(-1, 3) if len(img_array.shape) == 3 else img_array.reshape(-1, 1)
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(pixels)
        
        return [color.astype(int).tolist() for color in kmeans.cluster_centers_]
    
    def _analyze_color_harmony(self, img_array: np.ndarray) -> Dict[str, float]:
        """
Analyze color harmony in image."""
        if len(img_array.shape) == 3:
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            hue_std = float(np.std(hsv[:, :, 0]))
            sat_mean = float(np.mean(hsv[:, :, 1]))
            val_mean = float(np.mean(hsv[:, :, 2]))
            
            return {
                'hue_harmony': 1.0 / (1.0 + hue_std / 180.0),
                'saturation_balance': sat_mean / 255.0,
                'brightness_balance': val_mean / 255.0
            }
        return {'harmony_score': 0.0}
    
    def _calculate_color_temperature(self, img_array: np.ndarray) -> float:
        """
Calculate color temperature of image."""
        if len(img_array.shape) == 3:
            r_mean = np.mean(img_array[:, :, 0])
            b_mean = np.mean(img_array[:, :, 2])
            
            # Simplified color temperature calculation
            ratio = b_mean / (r_mean + 1e-10)
            temperature = 6500 - (ratio - 1) * 1000  # Approximate mapping
            return float(np.clip(temperature, 2000, 10000))
        return 6500.0  # Neutral temperature
    
    def _generate_color_histogram(self, img_array: np.ndarray) -> Dict[str, List[int]]:
        """
Generate color histogram."""
        if len(img_array.shape) == 3:
            hist_r = cv2.calcHist([img_array], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img_array], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([img_array], [2], None, [256], [0, 256])
            
            return {
                'red': hist_r.flatten().astype(int).tolist(),
                'green': hist_g.flatten().astype(int).tolist(),
                'blue': hist_b.flatten().astype(int).tolist()
            }
        else:
            hist = cv2.calcHist([img_array], [0], None, [256], [0, 256])
            return {'grayscale': hist.flatten().astype(int).tolist()}
    
    def _check_rule_of_thirds(self, img_array: np.ndarray) -> Dict[str, float]:
        """
Check rule of thirds composition."""
        h, w = img_array.shape[:2]
        
        # Define rule of thirds lines
        third_h = h // 3
        third_w = w // 3
        
        # Analyze intersection points
        intersections = [
            (third_w, third_h), (2 * third_w, third_h),
            (third_w, 2 * third_h), (2 * third_w, 2 * third_h)
        ]
        
        # Calculate interest at intersection points
        interest_scores = []
        for x, y in intersections:
            if len(img_array.shape) == 3:
                region = img_array[max(0, y-10):min(h, y+10), max(0, x-10):min(w, x+10)]
                interest = float(np.std(region))
            else:
                region = img_array[max(0, y-10):min(h, y+10), max(0, x-10):min(w, x+10)]
                interest = float(np.std(region))
            interest_scores.append(interest)
        
        return {
            'rule_of_thirds_score': float(np.mean(interest_scores)),
            'intersection_interests': interest_scores
        }
    
    def _analyze_symmetry(self, img_array: np.ndarray) -> Dict[str, float]:
        """
Analyze image symmetry."""
        h, w = img_array.shape[:2]
        
        # Horizontal symmetry
        left_half = img_array[:, :w//2]
        right_half = np.fliplr(img_array[:, w//2:])
        min_w = min(left_half.shape[1], right_half.shape[1])
        h_symmetry = float(np.mean(np.abs(left_half[:, :min_w] - right_half[:, :min_w])))
        
        # Vertical symmetry
        top_half = img_array[:h//2, :]
        bottom_half = np.flipud(img_array[h//2:, :])
        min_h = min(top_half.shape[0], bottom_half.shape[0])
        v_symmetry = float(np.mean(np.abs(top_half[:min_h, :] - bottom_half[:min_h, :])))
        
        return {
            'horizontal_symmetry': 1.0 / (1.0 + h_symmetry / 255.0),
            'vertical_symmetry': 1.0 / (1.0 + v_symmetry / 255.0)
        }
    
    def _detect_leading_lines(self, img_array: np.ndarray) -> Dict[str, int]:
        """
Detect leading lines in image."""
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Line detection using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        line_count = len(lines) if lines is not None else 0
        
        return {
            'line_count': line_count,
            'line_density': float(line_count / (gray.shape[0] * gray.shape[1]) * 10000)
        }
    
    def _identify_focal_points(self, img_array: np.ndarray) -> List[Dict[str, int]]:
        """
Identify focal points in image."""
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Use Harris corner detection for focal points
        corners = cv2.cornerHarris(gray, 2, 3, 0.04)
        corners = cv2.dilate(corners, None)
        
        # Get corner locations
        focal_points = []
        corner_threshold = 0.01 * corners.max()
        locations = np.where(corners > corner_threshold)
        
        for i in range(min(10, len(locations[0]))):  # Limit to top 10
            y, x = locations[0][i], locations[1][i]
            focal_points.append({'x': int(x), 'y': int(y), 'strength': float(corners[y, x])})
        
        return focal_points
    
    # Text analysis helper methods
    def _calculate_flesch_score(self, text: str) -> float:
        """
Calculate Flesch Reading Ease score."""
        words = text.split()
        sentences = text.split('.')
        syllables = sum(self._count_syllables(word) for word in words)
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, word: str) -> int:
        """
Count syllables in a word."""
        vowels = 'aeiouyAEIOUY'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _calculate_complex_words_ratio(self, words: List[str]) -> float:
        """
Calculate ratio of complex words (3+ syllables)."""
        if not words:
            return 0.0
        
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        return complex_words / len(words)
    
    def _detect_passive_voice_ratio(self, text: str) -> float:
        try:
            logger.info(f"Executing _detect_passive_voice_ratio")
            
            # Implementation for _detect_passive_voice_ratio
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_detect_passive_voice_ratio completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_detect_passive_voice_ratio failed: {e}")
            raise
    def _extract_key_phrases(self, text: str) -> List[str]:
        """
Extract key phrases from text."""
        # Simplified key phrase extraction
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Get most frequent words as key phrases
        from collections import Counter
        word_counts = Counter(filtered_words)
        
        return [word for word, count in word_counts.most_common(10)]
    
    def _identify_topics(self, text: str) -> List[str]:
        """
Identify main topics in text."""
        # Simplified topic identification
        key_phrases = self._extract_key_phrases(text)
        
        # Group related phrases (simplified)
        topics = []
        for phrase in key_phrases[:5]:  # Top 5 as topics
            topics.append(phrase.title())
        
        return topics
    
    def _extract_named_entities(self, text: str) -> List[Dict[str, str]]:
        """
Extract named entities from text."""
        # Simplified named entity extraction
        import re
        
        entities = []
        
        # Simple patterns for common entities
        patterns = {
            'PERSON': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'URL': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'DATE': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append({'text': match, 'label': entity_type})
        
        return entities
    
    def _detect_language(self, text: str) -> str:
        """
Detect text language."""
        # Simplified language detection
        common_words = {
            'english': ['the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that'],
            'french': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
            'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
            'spanish': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se']
        }
        
        words = text.lower().split()
        if not words:
            return 'unknown'
        
        language_scores = {}
        for lang, common in common_words.items():
            score = sum(1 for word in words[:100] if word in common)  # Check first 100 words
            language_scores[lang] = score
        
        return max(language_scores, key=language_scores.get) if language_scores else 'unknown'
    
    async def _generate_ai_insights(
        self,
        file_path: Path,
        content_type: str,
        processing_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Generate AI-powered insights for the content."""
        insights = {
            'optimization_suggestions': [],
            'platform_recommendations': [],
            'engagement_predictions': {},
            'seo_recommendations': [],
            'monetization_potential': {}
        }
        
        # Generate content-type specific insights
        if content_type == 'audio':
            insights.update(await self._generate_audio_insights(processing_result))
        elif content_type == 'video':
            insights.update(await self._generate_video_insights(processing_result))
        elif content_type == 'image':
            insights.update(await self._generate_image_insights(processing_result))
        elif content_type == 'text':
            insights.update(await self._generate_text_insights(processing_result))
        
        return insights
    
    async def _generate_audio_insights(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """
Generate AI insights for audio content."""
        technical = processing_result.get('technical_analysis', {})
        quality = processing_result.get('quality_metrics', {})
        
        insights = {
            'optimization_suggestions': [],
            'platform_recommendations': [],
            'quality_score': 0.0
        }
        
        # Quality assessment
        quality_factors = []
        
        # Loudness check
        loudness = quality.get('loudness_lufs', -23)
        if loudness < -35:
            insights['optimization_suggestions'].append("Consider increasing overall loudness for better streaming quality")
            quality_factors.append(0.6)
        elif loudness > -14:
            insights['optimization_suggestions'].append("Consider reducing loudness to prevent clipping on streaming platforms")
            quality_factors.append(0.7)
        else:
            quality_factors.append(0.9)
        
        # Dynamic range check
        dynamic_range = technical.get('dynamic_range', 0)
        if dynamic_range < 0.1:
            insights['optimization_suggestions'].append("Audio appears heavily compressed, consider preserving more dynamics")
            quality_factors.append(0.5)
        else:
            quality_factors.append(0.8)
        
        # Platform recommendations based on technical specs
        duration = technical.get('duration', 0)
        if duration <= 30:
            insights['platform_recommendations'].extend(['TikTok', 'Instagram Reels', 'YouTube Shorts'])
        elif duration <= 180:
            insights['platform_recommendations'].extend(['Instagram', 'Twitter', 'Facebook'])
        else:
            insights['platform_recommendations'].extend(['Spotify', 'YouTube', 'SoundCloud'])
        
        insights['quality_score'] = sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
        
        return insights
    
    async def _generate_video_insights(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights for video content."""
        technical = processing_result.get('technical_analysis', {})
        quality = processing_result.get('quality_metrics', {})
        
        insights = {
            'optimization_suggestions': [],
            'platform_recommendations': [],
            'quality_score': 0.0
        }
        
        quality_factors = []
        
        # Resolution check
        resolution = technical.get('resolution', '0x0')
        width, height = map(int, resolution.split('x'))
        
        if width >= 1920 and height >= 1080:
            quality_factors.append(0.9)
            insights['platform_recommendations'].extend(['YouTube', 'Vimeo'])
        elif width >= 1280 and height >= 720:
            quality_factors.append(0.7)
            insights['platform_recommendations'].extend(['Instagram', 'Facebook'])
        else:
            quality_factors.append(0.5)
            insights['optimization_suggestions'].append("Consider increasing resolution for better quality")
        
        # Aspect ratio optimization
        aspect_ratio = technical.get('aspect_ratio', 1.0)
        if 0.5 <= aspect_ratio <= 0.6:  # Vertical
            insights['platform_recommendations'].extend(['TikTok', 'Instagram Stories', 'YouTube Shorts'])
        elif 1.7 <= aspect_ratio <= 1.8:  # Horizontal
            insights['platform_recommendations'].extend(['YouTube', 'Facebook', 'LinkedIn'])
        elif 0.9 <= aspect_ratio <= 1.1:  # Square
            insights['platform_recommendations'].extend(['Instagram Feed', 'Facebook', 'Twitter'])
        
        # Duration recommendations
        duration = technical.get('duration', 0)
        if duration <= 15:
            insights['platform_recommendations'].extend(['TikTok', 'Instagram Reels'])
        elif duration <= 60:
            insights['platform_recommendations'].extend(['YouTube Shorts', 'Twitter'])
        elif duration <= 600:  # 10 minutes
            insights['platform_recommendations'].extend(['YouTube', 'Instagram TV'])
        
        # Motion analysis
        motion = quality.get('motion_intensity', 0)
        if motion > 50:
            insights['optimization_suggestions'].append("High motion detected - consider stabilization")
            quality_factors.append(0.6)
        else:
            quality_factors.append(0.8)
        
        insights['quality_score'] = sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
        
        return insights
    
    async def _generate_image_insights(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights for image content."""
        technical = processing_result.get('technical_analysis', {})
        quality = processing_result.get('quality_metrics', {})
        composition = processing_result.get('composition_analysis', {})
        
        insights = {
            'optimization_suggestions': [],
            'platform_recommendations': [],
            'quality_score': 0.0
        }
        
        quality_factors = []
        
        # Resolution check
        dimensions = technical.get('dimensions', '0x0')
        width, height = map(int, dimensions.split('x'))
        
        if width >= 1920 or height >= 1920:
            quality_factors.append(0.9)
            insights['platform_recommendations'].extend(['Instagram', 'Pinterest', 'Facebook'])
        elif width >= 1080 or height >= 1080:
            quality_factors.append(0.7)
        else:
            quality_factors.append(0.5)
            insights['optimization_suggestions'].append("Consider higher resolution for better quality")
        
        # Aspect ratio optimization
        aspect_ratio = technical.get('aspect_ratio', 1.0)
        if 0.8 <= aspect_ratio <= 1.25:  # Square-ish
            insights['platform_recommendations'].extend(['Instagram Feed', 'Facebook'])
        elif aspect_ratio > 1.3:  # Landscape
            insights['platform_recommendations'].extend(['Facebook Cover', 'LinkedIn Banner', 'Twitter Header'])
        elif aspect_ratio < 0.8:  # Portrait
            insights['platform_recommendations'].extend(['Instagram Stories', 'Pinterest'])
        
        # Composition quality
        rule_of_thirds = composition.get('rule_of_thirds_score', 0)
        if rule_of_thirds > 100:
            quality_factors.append(0.8)
        else:
            insights['optimization_suggestions'].append("Consider rule of thirds for better composition")
            quality_factors.append(0.6)
        
        # Color analysis
        brightness = quality.get('brightness', 128)
        if brightness < 50:
            insights['optimization_suggestions'].append("Image appears too dark - consider brightening")
            quality_factors.append(0.6)
        elif brightness > 200:
            insights['optimization_suggestions'].append("Image appears overexposed - consider darkening")
            quality_factors.append(0.6)
        else:
            quality_factors.append(0.8)
        
        # Sharpness check
        sharpness = quality.get('sharpness', 0)
        if sharpness < 100:
            insights['optimization_suggestions'].append("Image appears soft - consider sharpening")
            quality_factors.append(0.6)
        else:
            quality_factors.append(0.8)
        
        insights['quality_score'] = sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
        
        return insights
    
    async def _generate_text_insights(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights for text content."""
        technical = processing_result.get('technical_analysis', {})
        readability = processing_result.get('readability_metrics', {})
        content_analysis = processing_result.get('content_analysis', {})
        
        insights = {
            'optimization_suggestions': [],
            'platform_recommendations': [],
            'readability_score': 0.0
        }
        
        # Readability assessment
        flesch_score = readability.get('flesch_reading_ease', 50)
        if flesch_score >= 80:
            insights['readability_score'] = 0.9
            insights['platform_recommendations'].extend(['Twitter', 'Instagram', 'TikTok'])
        elif flesch_score >= 60:
            insights['readability_score'] = 0.7
            insights['platform_recommendations'].extend(['Facebook', 'LinkedIn', 'Medium'])
        else:
            insights['readability_score'] = 0.5
            insights['optimization_suggestions'].append("Consider simplifying language for better readability")
            insights['platform_recommendations'].extend(['LinkedIn', 'Medium', 'Blog'])
        
        # Length recommendations
        word_count = technical.get('word_count', 0)
        if word_count <= 50:
            insights['platform_recommendations'].extend(['Twitter', 'Instagram Caption'])
        elif word_count <= 300:
            insights['platform_recommendations'].extend(['Facebook', 'LinkedIn Post'])
        elif word_count <= 1000:
            insights['platform_recommendations'].extend(['Medium', 'Blog Post'])
        else:
            insights['platform_recommendations'].extend(['Blog', 'Long-form Content'])
        
        # Sentiment analysis
        sentiment = content_analysis.get('sentiment', {})
        sentiment_label = sentiment.get('label', 'NEUTRAL')
        if sentiment_label == 'POSITIVE':
            insights['platform_recommendations'].extend(['Instagram', 'Facebook', 'LinkedIn'])
        elif sentiment_label == 'NEGATIVE':
            insights['optimization_suggestions'].append("Consider balancing negative tone with constructive elements")
        
        # Complex words check
        complex_ratio = readability.get('complex_words_ratio', 0)
        if complex_ratio > 0.3:
            insights['optimization_suggestions'].append("Consider reducing complex words for broader audience")
        
        return insights
    
    async def _generate_recommendations(
        self,
        content_type: str,
        processing_result: Dict[str, Any],
        ai_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive recommendations for content optimization."""
        recommendations = {
            'immediate_actions': [],
            'platform_strategy': {},
            'seo_optimization': [],
            'monetization_tips': [],
            'collaboration_opportunities': []
        }
        
        # Extract optimization suggestions
        recommendations['immediate_actions'] = ai_insights.get('optimization_suggestions', [])
        
        # Platform-specific strategies
        platforms = ai_insights.get('platform_recommendations', [])
        for platform in platforms:
            recommendations['platform_strategy'][platform] = self._get_platform_strategy(
                platform, content_type, processing_result
            )
        
        # SEO recommendations
        recommendations['seo_optimization'] = self._generate_seo_recommendations(
            content_type, processing_result
        )
        
        # Monetization suggestions
        recommendations['monetization_tips'] = self._generate_monetization_tips(
            content_type, ai_insights
        )
        
        # Collaboration opportunities
        recommendations['collaboration_opportunities'] = self._suggest_collaborations(
            content_type, processing_result
        )
        
        return recommendations
    
    def _get_platform_strategy(
        self,
        platform: str,
        content_type: str,
        processing_result: Dict[str, Any]
    ) -> Dict[str, str]:
        """
Get platform-specific optimization strategy."""
        strategies = {
            'YouTube': {
                'audio': 'Focus on high-quality audio, create engaging thumbnails, optimize for 10+ minute duration',
                'video': 'Use compelling thumbnails, optimize for retention, include end screens',
                'image': 'Create video slideshows, add background music, use storytelling',
                'text': 'Convert to video format with text animations and voiceover'
            },
            'Instagram': {
                'audio': 'Create audiogram videos, use trending sounds, optimize for Reels',
                'video': 'Use square or vertical format, add captions, use trending hashtags',
                'image': 'Use high contrast, consistent aesthetics, engage with stories',
                'text': 'Create quote graphics, carousel posts, engaging captions'
            },
            'TikTok': {
                'audio': 'Create short clips, trending sounds, vertical video format',
                'video': 'Vertical format, quick cuts, trending effects, first 3 seconds crucial',
                'image': 'Convert to video with transitions, add trending audio',
                'text': 'Text overlays on video, trending sounds, visual storytelling'
            },
            'Spotify': {
                'audio': 'High-quality mastering, proper metadata, playlist pitching',
                'video': 'Canvas videos, podcast format, behind-the-scenes content',
                'image': 'Album artwork, podcast covers, consistent branding',
                'text': 'Podcast scripts, song lyrics, show descriptions'
            }
        }
        
        return strategies.get(platform, {}).get(content_type, 'Optimize for platform-specific requirements')
    
    def _generate_seo_recommendations(
        self,
        content_type: str,
        processing_result: Dict[str, Any]
    ) -> List[str]:
        """
Generate SEO optimization recommendations."""
        seo_tips = [
            'Use descriptive, keyword-rich filenames',
            'Add relevant tags and metadata',
            'Create compelling titles and descriptions',
            'Use consistent branding across platforms'
        ]
        
        # Content-type specific SEO
        if content_type == 'audio':
            seo_tips.extend([
                'Include genre and mood tags',
                'Add timestamp descriptions for longer content',
                'Use music-specific keywords'
            ])
        elif content_type == 'video':
            seo_tips.extend([
                'Add closed captions for accessibility',
                'Use video chapters for longer content',
                'Optimize thumbnail for click-through rate'
            ])
        elif content_type == 'image':
            seo_tips.extend([
                'Use alt text for accessibility',
                'Optimize file size for fast loading',
                'Include location data if relevant'
            ])
        elif content_type == 'text':
            seo_tips.extend([
                'Use header structure (H1, H2, H3)',
                'Include relevant keywords naturally',
                'Add internal and external links'
            ])
        
        return seo_tips
    
    def _generate_monetization_tips(
        self,
        content_type: str,
        ai_insights: Dict[str, Any]
    ) -> List[str]:
        """
Generate monetization recommendations."""
        tips = [
            'Set up content fingerprinting for copyright protection',
            'Consider licensing opportunities',
            'Explore brand partnership possibilities',
            'Enable platform monetization features'
        ]
        
        quality_score = ai_insights.get('quality_score', 0.5)
        if quality_score > 0.8:
            tips.extend([
                'High-quality content detected - suitable for premium licensing',
                'Consider offering exclusive content to subscribers',
                'Explore direct sales opportunities'
            ])
        
        # Content-specific monetization
        if content_type == 'audio':
            tips.extend([
                'Submit to music libraries and sync agencies',
                'Consider NFT opportunities for unique pieces',
                'Explore podcast sponsorship opportunities'
            ])
        elif content_type == 'video':
            tips.extend([
                'Enable YouTube monetization',
                'Consider brand integrations and sponsorships',
                'Explore video licensing for commercial use'
            ])
        elif content_type == 'image':
            tips.extend([
                'List on stock photography platforms',
                'Offer prints and merchandise',
                'License for commercial use'
            ])
        
        return tips
    
    def _suggest_collaborations(
        self,
        content_type: str,
        processing_result: Dict[str, Any]
    ) -> List[str]:
        """
Suggest collaboration opportunities."""
        collaborations = [
            'Connect with creators in similar niches',
            'Participate in content challenges',
            'Cross-promote with complementary creators'
        ]
        
        # Content-specific collaborations
        if content_type == 'audio':
            collaborations.extend([
                'Collaborate with vocalists or instrumentalists',
                'Remix exchanges with other producers',
                'Podcast guest appearances'
            ])
        elif content_type == 'video':
            collaborations.extend([
                'Guest appearances in each other\'s videos',
                'Collaborative series or challenges',
                'Cross-platform content sharing'
            ])
        elif content_type == 'image':
            collaborations.extend([
                'Photography collaborations with models/brands',
                'Art collaborations and exhibitions',
                'Social media takeovers'
            ])
        elif content_type == 'text':
            collaborations.extend([
                'Guest writing opportunities',
                'Collaborative articles or series',
                'Interview-based content'
            ])
        
        return collaborations
    
    async def _update_content_record(
        self,
        content_id: UUID,
        processing_result: Dict[str, Any]
    ) -> None:
        """
Update content record with processing results."""
        update_data = {
            'status': ProcessingStatus.COMPLETED,
            'technical_analysis': processing_result.get('technical_analysis', {}),
            'quality_metrics': processing_result.get('quality_metrics', {}),
            'processed_at': datetime.utcnow()
        }
        
        await self.db.content.update(content_id, update_data)
    
    async def get_processing_status(self, content_id: UUID) -> Dict[str, Any]:
        """
Get processing status for content."""
        content = await self.db.content.get_by_id(content_id)
        if not content:
            raise ContentProcessingError("Content not found")
        
        return {
            'content_id': str(content_id),
            'status': content.status.value,
            'progress': 100 if content.status == ProcessingStatus.COMPLETED else 50,
            'created_at': content.created_at.isoformat(),
            'processed_at': content.processed_at.isoformat() if content.processed_at else None
        }
    
    async def reprocess_content(
        self,
        content_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Reprocess existing content with updated algorithms."""
        content = await self.db.content.get_by_id(content_id)
        if not content:
            raise ContentProcessingError("Content not found")
        
        if content.user_id != user_id:
            raise ContentProcessingError("Unauthorized access to content")
        
        # Get original file path (would need proper storage implementation)
        file_path = Path(f"storage/{content.filename}")
        
        return await self.process_content(
            file_path, user_id, content.content_type, content.metadata
        )
