"""
Content Extractors Module
Author: Fahed Mlaiel <mlaiel@live.de>

Advanced content extraction systems for multi-format media processing
with AI-powered metadata analysis and intelligent feature detection.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from pathlib import Path
import mimetypes
import hashlib
import json

# Audio processing
import librosa
import soundfile as sf
from mutagen import File as MutagenFile
import essentia.standard as es

# Video processing
import cv2
import ffmpeg
from moviepy.editor import VideoFileClip

# Image processing
from PIL import Image, ExifTags
import numpy as np

# Text processing
import nltk
from transformers import pipeline, AutoTokenizer, AutoModel
import spacy

# AI/ML
import torch
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer

from ..core.exceptions import ExtractionError, UnsupportedFormatError
from ..core.metrics import MetricsCollector
from ..core.config import ExtractionConfig
from ..utils.decorators import monitor_performance, cache_result
from ..utils.file_handler import FileHandler


class MultiFormatExtractor:
    """
    Advanced multi-format content extractor supporting audio, video, image,
    and text content with intelligent metadata analysis and feature extraction.
    """
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("multi_format_extractor")
        self.file_handler = FileHandler()
        
        # Initialize format-specific extractors
        self.extractors = {
            'audio': AudioFeatureExtractor(config),
            'video': VideoFeatureExtractor(config),
            'image': ImageFeatureExtractor(config),
            'text': TextFeatureExtractor(config)
        }
        
        # Load AI models for enhanced extraction
        self._load_ai_models()
    
    def _load_ai_models(self):
        """Load AI models for advanced feature extraction."""
        self.ai_models = {}
        
        try:
            # Audio analysis models
            if self.config.enable_ai_audio:
                self.ai_models['audio_classifier'] = None  # Load pre-trained audio classifier
                self.ai_models['music_analyzer'] = None    # Load music analysis model
            
            # Visual analysis models
            if self.config.enable_ai_vision:
                self.ai_models['object_detector'] = None   # Load object detection model
                self.ai_models['scene_classifier'] = None  # Load scene classification model
                self.ai_models['face_detector'] = None     # Load face detection model
            
            # Text analysis models
            if self.config.enable_ai_nlp:
                self.ai_models['sentiment_analyzer'] = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                ) if self.config.load_transformers else None
                
                self.ai_models['entity_extractor'] = spacy.load("en_core_web_sm") if spacy.util.is_package("en_core_web_sm") else None
                
        except Exception as e:
            self.logger.warning(f"Failed to load some AI models: {e}")
    
    @monitor_performance
    async def extract_complete_metadata(
        self,
        file_path: str,
        content_type: str,
        extraction_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from content file.
        
        Args:
            file_path: Path to content file
            content_type: Type of content (audio, video, image, text)
            extraction_options: Additional extraction options
            
        Returns:
            Dict containing comprehensive metadata
        """
        options = extraction_options or {}
        
        metadata = {
            'file_info': await self._extract_file_metadata(file_path),
            'content_type': content_type,
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'technical_metadata': {},
            'content_features': {},
            'ai_analysis': {},
            'quality_metrics': {}
        }
        
        try:
            # Get format-specific extractor
            extractor = self.extractors.get(content_type)
            if not extractor:
                raise UnsupportedFormatError(f"Unsupported content type: {content_type}")
            
            # Extract technical metadata
            metadata['technical_metadata'] = await extractor.extract_technical_metadata(
                file_path, options
            )
            
            # Extract content features
            metadata['content_features'] = await extractor.extract_content_features(
                file_path, options
            )
            
            # AI-powered analysis
            if options.get('enable_ai_analysis', True):
                metadata['ai_analysis'] = await self._extract_ai_analysis(
                    file_path, content_type, options
                )
            
            # Quality assessment
            if options.get('assess_quality', True):
                metadata['quality_metrics'] = await extractor.assess_quality(
                    file_path, options
                )
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed for {file_path}: {e}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract basic file metadata."""



        try:
            file_stat = Path(file_path).stat()
            
            return {
                'filename': Path(file_path).name,
                'file_size': file_stat.st_size,
                'file_size_mb': file_stat.st_size / (1024 * 1024),
                'created_time': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'file_extension': Path(file_path).suffix.lower(),
                'mime_type': mimetypes.guess_type(file_path)[0],
                'file_hash': self._calculate_file_hash(file_path)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract file metadata: {e}")
            return {'error': str(e)}
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""



        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "hash_calculation_failed"
    
    async def _extract_ai_analysis(
        self,
        file_path: str,
        content_type: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract AI-powered analysis."""
        ai_analysis = {}
        
        try:
            if content_type == 'audio':
                ai_analysis = await self._analyze_audio_with_ai(file_path, options)
            elif content_type == 'video':
                ai_analysis = await self._analyze_video_with_ai(file_path, options)
            elif content_type == 'image':
                ai_analysis = await self._analyze_image_with_ai(file_path, options)
            elif content_type == 'text':
                ai_analysis = await self._analyze_text_with_ai(file_path, options)
                
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            ai_analysis['error'] = str(e)
        
        return ai_analysis
    
    async def _analyze_audio_with_ai(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered audio analysis."""
        analysis = {}
        
        try:
            # Load audio
            y, sr = librosa.load(file_path)
            
            # Music analysis
            analysis['music_analysis'] = {
                'tempo': float(librosa.beat.tempo(y=y, sr=sr)[0]),
                'key': 'unknown',  # Would use more sophisticated analysis
                'mood': 'unknown',  # Would use pre-trained mood classifier
                'genre': 'unknown',  # Would use genre classification model
                'energy_level': float(np.mean(librosa.feature.rms(y=y))),
                'spectral_features': {
                    'brightness': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                    'roughness': float(np.std(librosa.feature.spectral_rolloff(y=y, sr=sr))),
                    'harmonicity': 0.5  # Placeholder
                }
            }
            
            # Identify instruments (placeholder)
            analysis['instrument_detection'] = {
                'instruments': [],  # Would use instrument classification
                'confidence_scores': []
            }
            
            # Voice analysis
            analysis['voice_analysis'] = {
                'has_vocals': False,  # Would use vocal detection
                'speaker_count': 0,   # Would use speaker diarization
                'language': 'unknown' # Would use language detection
            }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_video_with_ai(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered video analysis."""
        analysis = {}
        
        try:
            cap = cv2.VideoCapture(file_path)
            
            # Sample frames for analysis
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(10, total_frames)  # Analyze up to 10 frames
            frame_step = max(1, total_frames // sample_frames)
            
            scenes = []
            objects = []
            faces = []
            
            for i in range(0, total_frames, frame_step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Scene classification (placeholder)
                scene_info = {
                    'frame_number': i,
                    'timestamp': i / cap.get(cv2.CAP_PROP_FPS),
                    'scene_type': 'unknown',  # Would use scene classifier
                    'confidence': 0.0
                }
                scenes.append(scene_info)
                
                # Object detection (placeholder)
                # Would use YOLO or similar model
                
                # Face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                detected_faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(detected_faces) > 0:
                    faces.append({
                        'frame_number': i,
                        'face_count': len(detected_faces),
                        'faces': [{'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)} 
                                for (x, y, w, h) in detected_faces]
                    })
            
            cap.release()
            
            analysis['scene_analysis'] = {
                'scenes': scenes,
                'dominant_scenes': [],  # Would aggregate scene types
                'scene_changes': len(scenes)
            }
            
            analysis['object_detection'] = {
                'objects': objects,
                'object_categories': [],  # Would list detected object types
                'object_density': 0.0
            }
            
            analysis['face_analysis'] = {
                'frames_with_faces': faces,
                'total_faces_detected': sum(f['face_count'] for f in faces),
                'average_faces_per_frame': sum(f['face_count'] for f in faces) / len(faces) if faces else 0
            }
            
            # Motion analysis
            analysis['motion_analysis'] = {
                'motion_intensity': 'medium',  # Would calculate optical flow
                'camera_movement': 'static',   # Would detect camera motion
                'action_scenes': []            # Would detect high-motion scenes
            }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_image_with_ai(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered image analysis."""
        analysis = {}
        
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Object detection (placeholder)
            analysis['object_detection'] = {
                'objects': [],  # Would use YOLO or similar
                'main_subject': 'unknown',
                'confidence_scores': []
            }
            
            # Scene classification (placeholder)
            analysis['scene_classification'] = {
                'scene_type': 'unknown',  # Indoor, outdoor, portrait, landscape, etc.
                'environment': 'unknown',  # Beach, city, nature, etc.
                'time_of_day': 'unknown',  # Morning, afternoon, evening, night
                'weather': 'unknown'       # Sunny, cloudy, rainy, etc.
            }
            
            # Face analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            analysis['face_analysis'] = {
                'face_count': len(faces),
                'faces': [{'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)} 
                         for (x, y, w, h) in faces],
                'is_portrait': len(faces) > 0 and len(faces) <= 3  # Simple heuristic
            }
            
            # Color analysis
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Dominant colors (simplified)
            pixels = image_rgb.reshape(-1, 3)
            from sklearn.cluster import KMeans
            
            # Use KMeans to find dominant colors
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_.astype(int)
            percentages = np.bincount(kmeans.labels_) / len(kmeans.labels_)
            
            dominant_colors = []
            for i, (color, percentage) in enumerate(zip(colors, percentages)):
                dominant_colors.append({
                    'color_rgb': color.tolist(),
                    'percentage': float(percentage),
                    'color_name': self._rgb_to_color_name(color)
                })
            
            # Sort by percentage
            dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
            
            analysis['color_analysis'] = {
                'dominant_colors': dominant_colors[:3],  # Top 3 colors
                'color_palette': [c['color_rgb'] for c in dominant_colors],
                'color_harmony': 'unknown',  # Would analyze color relationships
                'brightness_level': float(np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))),
                'contrast_level': float(np.std(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
            }
            
            # Composition analysis
            height, width = image.shape[:2]
            analysis['composition_analysis'] = {
                'aspect_ratio': width / height,
                'rule_of_thirds': self._analyze_rule_of_thirds(image),
                'symmetry': self._analyze_symmetry(image),
                'leading_lines': False,  # Would use line detection
                'depth_of_field': 'unknown'  # Would analyze blur/focus
            }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_text_with_ai(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered text analysis."""
        analysis = {}
        
        try:
            # Read text content
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Basic text statistics
            words = text.split()
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            analysis['text_statistics'] = {
                'word_count': len(words),
                'character_count': len(text),
                'sentence_count': len(sentences),
                'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
                'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
                'average_sentence_length': len(words) / len(sentences) if sentences else 0
            }
            
            # Language detection (simplified)
            analysis['language_analysis'] = {
                'detected_language': 'en',  # Would use language detection
                'confidence': 0.9,
                'alternative_languages': []
            }
            
            # Sentiment analysis
            if self.ai_models.get('sentiment_analyzer'):
                try:
                    # Analyze text in chunks for long texts
                    chunk_size = 500
                    sentiments = []
                    
                    for i in range(0, len(text), chunk_size):
                        chunk = text[i:i + chunk_size]
                        if chunk.strip():
                            result = self.ai_models['sentiment_analyzer'](chunk)
                            sentiments.append(result)
                    
                    # Aggregate sentiment
                    if sentiments:
                        avg_sentiment = {
                            'NEGATIVE': np.mean([s[0]['score'] for s in sentiments if s[0]['label'] == 'NEGATIVE']),
                            'NEUTRAL': np.mean([s[0]['score'] for s in sentiments if s[0]['label'] == 'NEUTRAL']),
                            'POSITIVE': np.mean([s[0]['score'] for s in sentiments if s[0]['label'] == 'POSITIVE'])
                        }
                        
                        # Find dominant sentiment
                        dominant_sentiment = max(avg_sentiment.items(), key=lambda x: x[1])
                        
                        analysis['sentiment_analysis'] = {
                            'overall_sentiment': dominant_sentiment[0].lower(),
                            'confidence': float(dominant_sentiment[1]),
                            'sentiment_distribution': avg_sentiment,
                            'sentiment_chunks': len(sentiments)
                        }
                
                except Exception as e:
                    analysis['sentiment_analysis'] = {'error': str(e)}
            
            # Named Entity Recognition
            if self.ai_models.get('entity_extractor'):
                try:
                    doc = self.ai_models['entity_extractor'](text[:10000])  # Limit for performance
                    
                    entities = []
                    for ent in doc.ents:
                        entities.append({
                            'text': ent.text,
                            'label': ent.label_,
                            'description': spacy.explain(ent.label_),
                            'start': ent.start_char,
                            'end': ent.end_char
                        })
                    
                    # Categorize entities
                    entity_categories = {}
                    for entity in entities:
                        label = entity['label']
                        if label not in entity_categories:
                            entity_categories[label] = []
                        entity_categories[label].append(entity['text'])
                    
                    analysis['entity_recognition'] = {
                        'entities': entities,
                        'entity_categories': entity_categories,
                        'entity_count': len(entities),
                        'unique_entity_types': len(entity_categories)
                    }
                
                except Exception as e:
                    analysis['entity_recognition'] = {'error': str(e)}
            
            # Topic analysis (simplified)
            analysis['topic_analysis'] = {
                'main_topics': [],  # Would use topic modeling
                'keywords': self._extract_keywords(text),
                'content_category': 'unknown',  # Would classify content type
                'expertise_level': 'unknown'    # Would assess complexity
            }
            
            # Readability analysis
            analysis['readability'] = {
                'flesch_reading_ease': self._calculate_flesch_score(text),
                'reading_level': 'unknown',  # Would calculate grade level
                'complexity_score': len(set(words)) / len(words) if words else 0  # Lexical diversity
            }
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _rgb_to_color_name(self, rgb: np.ndarray) -> str:
        """Convert RGB values to approximate color name."""
        r, g, b = rgb
        
        # Simple color name mapping
        if r > 200 and g > 200 and b > 200:
            return "white"
        elif r < 50 and g < 50 and b < 50:
            return "black"
        elif r > g and r > b:
            return "red"
        elif g > r and g > b:
            return "green"
        elif b > r and b > g:
            return "blue"
        elif r > 150 and g > 150 and b < 100:
            return "yellow"
        elif r > 150 and g < 100 and b > 150:
            return "purple"
        elif r < 100 and g > 150 and b > 150:
            return "cyan"
        else:
            return "mixed"
    
    def _analyze_rule_of_thirds(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze if image follows rule of thirds."""
        height, width = image.shape[:2]
        
        # Rule of thirds grid points
        third_width = width // 3
        third_height = height // 3
        
        # Check for high contrast areas near intersection points
        intersections = [
            (third_width, third_height),
            (2 * third_width, third_height),
            (third_width, 2 * third_height),
            (2 * third_width, 2 * third_height)
        ]
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate gradient magnitude to find points of interest
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Check activity near intersection points
        roi_size = 50  # Region of interest size around intersection
        intersection_scores = []
        
        for x, y in intersections:
            x1, y1 = max(0, x - roi_size), max(0, y - roi_size)
            x2, y2 = min(width, x + roi_size), min(height, y + roi_size)
            
            roi = gradient_magnitude[y1:y2, x1:x2]
            score = np.mean(roi) if roi.size > 0 else 0
            intersection_scores.append(score)
        
        avg_intersection_score = np.mean(intersection_scores)
        overall_score = np.mean(gradient_magnitude)
        
        rule_of_thirds_ratio = avg_intersection_score / overall_score if overall_score > 0 else 0
        
        return {
            'follows_rule_of_thirds': rule_of_thirds_ratio > 1.2,  # Arbitrary threshold
            'strength': float(rule_of_thirds_ratio),
            'intersection_scores': [float(s) for s in intersection_scores]
        }
    
    def _analyze_symmetry(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze symmetry in image."""
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Horizontal symmetry
        top_half = gray[:height//2, :]
        bottom_half = gray[height//2:, :]
        bottom_half_flipped = np.flipud(bottom_half)
        
        # Resize to match if different sizes
        min_height = min(top_half.shape[0], bottom_half_flipped.shape[0])
        top_half_resized = top_half[:min_height, :]
        bottom_half_resized = bottom_half_flipped[:min_height, :]
        
        horizontal_diff = np.mean(np.abs(top_half_resized.astype(float) - bottom_half_resized.astype(float)))
        
        # Vertical symmetry
        left_half = gray[:, :width//2]
        right_half = gray[:, width//2:]
        right_half_flipped = np.fliplr(right_half)
        
        # Resize to match if different sizes
        min_width = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half_resized = left_half[:, :min_width]
        right_half_resized = right_half_flipped[:, :min_width]
        
        vertical_diff = np.mean(np.abs(left_half_resized.astype(float) - right_half_resized.astype(float)))
        
        # Normalize differences (0 = perfect symmetry, higher = less symmetric)
        max_possible_diff = 255.0
        horizontal_symmetry = 1.0 - (horizontal_diff / max_possible_diff)
        vertical_symmetry = 1.0 - (vertical_diff / max_possible_diff)
        
        return {
            'horizontal_symmetry': float(horizontal_symmetry),
            'vertical_symmetry': float(vertical_symmetry),
            'overall_symmetry': float((horizontal_symmetry + vertical_symmetry) / 2),
            'is_symmetric': horizontal_symmetry > 0.8 or vertical_symmetry > 0.8
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using TF-IDF."""



        try:
            # Simple keyword extraction using word frequency
            words = text.lower().split()
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            
            # Filter words
            filtered_words = [word.strip('.,!?;:"()[]{}') for word in words 
                            if word.strip('.,!?;:"()[]{}').lower() not in stop_words 
                            and len(word.strip('.,!?;:"()[]{}')) > 2]
            
            # Count frequency
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and return top 10
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, freq in sorted_words[:10]]
            
            return keywords
            
        except Exception:
            return []
    
    def _calculate_flesch_score(self, text: str) -> float:
        """Calculate Flesch Reading Ease score."""



        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            words = text.split()
            syllables = sum(self._count_syllables(word) for word in words)
            
            if len(sentences) == 0 or len(words) == 0:
                return 0.0
            
            # Flesch Reading Ease formula
            score = 206.835 - (1.015 * len(words) / len(sentences)) - (84.6 * syllables / len(words))
            return max(0.0, min(100.0, score))  # Clamp between 0 and 100
            
        except Exception:
            return 50.0  # Default middle score
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower().strip('.,!?;:"()[]{}')
        if len(word) <= 3:
            return 1
        
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)


class AudioFeatureExtractor:
    """Specialized audio feature extraction with advanced signal processing."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def extract_technical_metadata(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical audio metadata."""



        try:
            # Load audio file
            y, sr = librosa.load(file_path)
            duration = len(y) / sr
            
            # Get file metadata using mutagen
            audio_file = MutagenFile(file_path)
            metadata = {}
            
            if audio_file is not None:
                metadata = {
                    'format': audio_file.mime[0] if audio_file.mime else 'unknown',
                    'bitrate': getattr(audio_file.info, 'bitrate', 0),
                    'channels': getattr(audio_file.info, 'channels', 0),
                    'length': getattr(audio_file.info, 'length', duration)
                }
            
            return {
                'sample_rate': int(sr),
                'duration': float(duration),
                'channels': 1 if len(y.shape) == 1 else y.shape[0],
                'samples': len(y),
                'file_metadata': metadata,
                'audio_format': Path(file_path).suffix.lower()[1:],
                'dynamic_range': float(np.max(y) - np.min(y)),
                'rms_level': float(np.sqrt(np.mean(y**2))),
                'peak_level': float(np.max(np.abs(y)))
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def extract_content_features(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract advanced audio content features."""



        try:
            y, sr = librosa.load(file_path)
            
            # Comprehensive feature extraction
            features = {}
            
            # Spectral features
            features['spectral'] = {
                'centroid': librosa.feature.spectral_centroid(y=y, sr=sr),
                'bandwidth': librosa.feature.spectral_bandwidth(y=y, sr=sr),
                'rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr),
                'flatness': librosa.feature.spectral_flatness(y=y),
                'contrast': librosa.feature.spectral_contrast(y=y, sr=sr)
            }
            
            # Convert to statistics
            spectral_stats = {}
            for feature_name, feature_data in features['spectral'].items():
                spectral_stats[feature_name] = {
                    'mean': float(np.mean(feature_data)),
                    'std': float(np.std(feature_data)),
                    'min': float(np.min(feature_data)),
                    'max': float(np.max(feature_data))
                }
            
            # Rhythmic features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            features['rhythm'] = {
                'tempo': float(tempo),
                'beat_count': len(beats),
                'beat_strength': float(np.mean(librosa.util.normalize(librosa.onset.onset_strength(y=y, sr=sr)))),
                'rhythm_regularity': self._calculate_rhythm_regularity(beats)
            }
            
            # Harmonic features
            features['harmony'] = {
                'chroma': librosa.feature.chroma_stft(y=y, sr=sr),
                'tonnetz': librosa.feature.tonnetz(y=y, sr=sr),
                'harmonic_ratio': self._calculate_harmonic_ratio(y, sr)
            }
            
            # Convert chroma and tonnetz to statistics
            features['harmony']['chroma_stats'] = {
                'mean': np.mean(features['harmony']['chroma'], axis=1).tolist(),
                'std': np.std(features['harmony']['chroma'], axis=1).tolist()
            }
            
            features['harmony']['tonnetz_stats'] = {
                'mean': np.mean(features['harmony']['tonnetz'], axis=1).tolist(),
                'std': np.std(features['harmony']['tonnetz'], axis=1).tolist()
            }
            
            # Remove raw arrays to save space
            del features['harmony']['chroma']
            del features['harmony']['tonnetz']
            
            # MFCCs for timbral characteristics
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            features['timbre'] = {
                'mfcc_stats': {
                    'mean': np.mean(mfccs, axis=1).tolist(),
                    'std': np.std(mfccs, axis=1).tolist()
                },
                'zero_crossing_rate': {
                    'mean': float(np.mean(librosa.feature.zero_crossing_rate(y))),
                    'std': float(np.std(librosa.feature.zero_crossing_rate(y)))
                }
            }
            
            # Energy and loudness features
            features['energy'] = {
                'rms_energy': librosa.feature.rms(y=y),
                'energy_distribution': self._analyze_energy_distribution(y),
                'dynamic_range': float(np.max(y) - np.min(y))
            }
            
            # Convert RMS to statistics
            features['energy']['rms_stats'] = {
                'mean': float(np.mean(features['energy']['rms_energy'])),
                'std': float(np.std(features['energy']['rms_energy'])),
                'min': float(np.min(features['energy']['rms_energy'])),
                'max': float(np.max(features['energy']['rms_energy']))
            }
            del features['energy']['rms_energy']
            
            return {
                'spectral_features': spectral_stats,
                'rhythmic_features': features['rhythm'],
                'harmonic_features': features['harmony'],
                'timbral_features': features['timbre'],
                'energy_features': features['energy']
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def assess_quality(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Assess audio quality metrics."""



        try:
            y, sr = librosa.load(file_path)
            
            quality_metrics = {}
            
            # Signal-to-noise ratio estimation
            quality_metrics['snr_estimate'] = self._estimate_snr(y)
            
            # Clipping detection
            clipping_threshold = 0.99
            clipped_samples = np.sum(np.abs(y) > clipping_threshold)
            quality_metrics['clipping'] = {
                'clipped_samples': int(clipped_samples),
                'clipping_percentage': float(clipped_samples / len(y) * 100),
                'has_clipping': clipped_samples > 0
            }
            
            # Dynamic range assessment
            quality_metrics['dynamic_range'] = {
                'range_db': float(20 * np.log10(np.max(np.abs(y)) / (np.mean(np.abs(y)) + 1e-10))),
                'rms_level': float(np.sqrt(np.mean(y**2))),
                'peak_level': float(np.max(np.abs(y)))
            }
            
            # Frequency response analysis
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            freq_response = np.mean(magnitude, axis=1)
            
            quality_metrics['frequency_response'] = {
                'low_freq_energy': float(np.sum(freq_response[:len(freq_response)//4])),
                'mid_freq_energy': float(np.sum(freq_response[len(freq_response)//4:3*len(freq_response)//4])),
                'high_freq_energy': float(np.sum(freq_response[3*len(freq_response)//4:])),
                'spectral_balance': self._assess_spectral_balance(freq_response)
            }
            
            # Overall quality score
            quality_score = self._calculate_overall_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = quality_score
            
            return quality_metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_rhythm_regularity(self, beats: np.ndarray) -> float:
        """Calculate rhythm regularity from beat positions."""
        if len(beats) < 3:
            return 0.0
        
        # Calculate intervals between beats
        intervals = np.diff(beats)
        
        # Calculate coefficient of variation (std/mean)
        if np.mean(intervals) > 0:
            cv = np.std(intervals) / np.mean(intervals)
            # Convert to regularity score (lower CV = higher regularity)
            regularity = 1.0 / (1.0 + cv)
        else:
            regularity = 0.0
        
        return float(regularity)
    
    def _calculate_harmonic_ratio(self, y: np.ndarray, sr: int) -> float:
        """Calculate harmonic to percussive ratio."""



        try:
            # Separate harmonic and percussive components
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            
            # Calculate energy in each component
            harmonic_energy = np.sum(y_harmonic**2)
            percussive_energy = np.sum(y_percussive**2)
            
            # Calculate ratio
            if percussive_energy > 0:
                ratio = harmonic_energy / percussive_energy
            else:
                ratio = float('inf')
            
            return float(ratio)
            
        except Exception:
            return 1.0
    
    def _analyze_energy_distribution(self, y: np.ndarray) -> Dict[str, float]:
        """Analyze energy distribution across the audio."""
        # Divide audio into segments
        segment_length = len(y) // 10  # 10 segments
        if segment_length == 0:
            return {'uniformity': 0.0, 'peak_position': 0.0}
        
        segment_energies = []
        for i in range(0, len(y), segment_length):
            segment = y[i:i + segment_length]
            energy = np.sum(segment**2)
            segment_energies.append(energy)
        
        segment_energies = np.array(segment_energies)
        
        # Calculate uniformity (inverse of coefficient of variation)
        if np.mean(segment_energies) > 0:
            cv = np.std(segment_energies) / np.mean(segment_energies)
            uniformity = 1.0 / (1.0 + cv)
        else:
            uniformity = 0.0
        
        # Find position of peak energy
        peak_position = float(np.argmax(segment_energies) / len(segment_energies))
        
        return {
            'uniformity': float(uniformity),
            'peak_position': peak_position,
            'energy_variance': float(np.var(segment_energies))
        }
    
    def _estimate_snr(self, y: np.ndarray) -> float:
        """Estimate signal-to-noise ratio."""



        try:
            # Simple SNR estimation using spectral analysis
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            
            # Estimate noise floor (bottom 10th percentile)
            noise_floor = np.percentile(magnitude, 10)
            
            # Estimate signal level (90th percentile)
            signal_level = np.percentile(magnitude, 90)
            
            # Calculate SNR in dB
            if noise_floor > 0:
                snr_db = 20 * np.log10(signal_level / noise_floor)
            else:
                snr_db = float('inf')
            
            return float(snr_db)
            
        except Exception:
            return 20.0  # Default reasonable SNR
    
    def _assess_spectral_balance(self, freq_response: np.ndarray) -> Dict[str, float]:
        """Assess spectral balance across frequency bands."""
        total_energy = np.sum(freq_response)
        
        if total_energy == 0:
            return {'bass': 0.0, 'midrange': 0.0, 'treble': 0.0, 'balance_score': 0.0}
        
        # Divide into frequency bands
        n_bins = len(freq_response)
        bass_bins = n_bins // 4
        treble_start = 3 * n_bins // 4
        
        bass_energy = np.sum(freq_response[:bass_bins]) / total_energy
        midrange_energy = np.sum(freq_response[bass_bins:treble_start]) / total_energy
        treble_energy = np.sum(freq_response[treble_start:]) / total_energy
        
        # Calculate balance score (how evenly distributed)
        energies = [bass_energy, midrange_energy, treble_energy]
        ideal_distribution = 1.0 / 3  # Equal distribution
        
        deviations = [abs(e - ideal_distribution) for e in energies]
        balance_score = 1.0 - np.mean(deviations)
        
        return {
            'bass': float(bass_energy),
            'midrange': float(midrange_energy),
            'treble': float(treble_energy),
            'balance_score': float(balance_score)
        }
    
    def _calculate_overall_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score from individual metrics."""
        score = 100.0  # Start with perfect score
        
        # Penalize clipping
        if quality_metrics.get('clipping', {}).get('has_clipping', False):
            clipping_penalty = quality_metrics['clipping']['clipping_percentage'] * 2
            score -= min(clipping_penalty, 30)  # Max 30 point penalty
        
        # Assess dynamic range
        dr_score = quality_metrics.get('dynamic_range', {}).get('range_db', 0)
        if dr_score < 10:  # Very low dynamic range
            score -= (10 - dr_score) * 2
        
        # Assess SNR
        snr = quality_metrics.get('snr_estimate', 20)
        if snr < 20:  # Poor SNR
            score -= (20 - snr)
        
        # Assess spectral balance
        balance_score = quality_metrics.get('frequency_response', {}).get('spectral_balance', {}).get('balance_score', 0.5)
        score += (balance_score - 0.5) * 20  # Bonus for good balance
        
        return max(0.0, min(100.0, score))


class VideoFeatureExtractor:
    """Specialized video feature extraction with computer vision analysis."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def extract_technical_metadata(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical video metadata."""



        try:
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Get codec information
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            
            cap.release()
            
            # Get file size
            file_size = Path(file_path).stat().st_size
            
            return {
                'resolution': f"{width}x{height}",
                'width': width,
                'height': height,
                'fps': float(fps),
                'frame_count': frame_count,
                'duration': float(duration),
                'codec': codec,
                'file_size': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'bitrate_estimate': (file_size * 8) / duration if duration > 0 else 0,
                'aspect_ratio': width / height if height > 0 else 0,
                'pixel_count': width * height
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def extract_content_features(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract video content features using computer vision."""



        try:
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Sample frames for analysis (max 30 frames)
            sample_count = min(30, total_frames)
            frame_step = max(1, total_frames // sample_count)
            
            features = {
                'visual_features': [],
                'motion_features': [],
                'color_features': [],
                'composition_features': []
            }
            
            prev_frame = None
            
            for i in range(0, total_frames, frame_step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extract frame features
                frame_features = self._extract_frame_features(frame, i, fps)
                features['visual_features'].append(frame_features)
                
                # Motion analysis
                if prev_frame is not None:
                    motion_features = self._extract_motion_features(prev_frame, frame)
                    features['motion_features'].append(motion_features)
                
                # Color analysis
                color_features = self._extract_color_features(frame)
                features['color_features'].append(color_features)
                
                # Composition analysis
                composition_features = self._extract_composition_features(frame)
                features['composition_features'].append(composition_features)
                
                prev_frame = frame.copy()
            
            cap.release()
            
            # Aggregate features
            aggregated_features = self._aggregate_video_features(features)
            
            return aggregated_features
            
        except Exception as e:
            return {'error': str(e)}
    
    async def assess_quality(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Assess video quality metrics."""



        try:
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            quality_metrics = {}
            
            # Sample frames for quality assessment
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_count = min(10, total_frames)
            frame_step = max(1, total_frames // sample_count)
            
            sharpness_scores = []
            brightness_scores = []
            contrast_scores = []
            noise_scores = []
            
            for i in range(0, total_frames, frame_step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Sharpness (Laplacian variance)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                sharpness_scores.append(sharpness)
                
                # Brightness
                brightness = gray.mean()
                brightness_scores.append(brightness)
                
                # Contrast
                contrast = gray.std()
                contrast_scores.append(contrast)
                
                # Noise estimation (using local variance)
                noise = self._estimate_frame_noise(gray)
                noise_scores.append(noise)
            
            cap.release()
            
            # Calculate quality metrics
            quality_metrics['sharpness'] = {
                'mean': float(np.mean(sharpness_scores)),
                'std': float(np.std(sharpness_scores)),
                'min': float(np.min(sharpness_scores)),
                'max': float(np.max(sharpness_scores))
            }
            
            quality_metrics['brightness'] = {
                'mean': float(np.mean(brightness_scores)),
                'std': float(np.std(brightness_scores)),
                'min': float(np.min(brightness_scores)),
                'max': float(np.max(brightness_scores))
            }
            
            quality_metrics['contrast'] = {
                'mean': float(np.mean(contrast_scores)),
                'std': float(np.std(contrast_scores)),
                'min': float(np.min(contrast_scores)),
                'max': float(np.max(contrast_scores))
            }
            
            quality_metrics['noise'] = {
                'mean': float(np.mean(noise_scores)),
                'std': float(np.std(noise_scores)),
                'min': float(np.min(noise_scores)),
                'max': float(np.max(noise_scores))
            }
            
            # Overall quality score
            quality_score = self._calculate_video_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = quality_score
            
            return quality_metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_frame_features(self, frame: np.ndarray, frame_number: int, fps: float) -> Dict[str, Any]:
        """Extract features from a single frame."""
        height, width = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (width * height)
        
        # Texture analysis using Local Binary Pattern
        try:
            from skimage.feature import local_binary_pattern
            lbp = local_binary_pattern(gray, 8, 1, method='uniform')
            texture_variance = np.var(lbp)
        except ImportError:
            texture_variance = np.var(gray)  # Fallback
        
        return {
            'frame_number': frame_number,
            'timestamp': frame_number / fps,
            'edge_density': float(edge_density),
            'texture_variance': float(texture_variance),
            'brightness': float(gray.mean()),
            'contrast': float(gray.std())
        }
    
    def _extract_motion_features(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> Dict[str, Any]:
        """Extract motion features between consecutive frames."""
        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowPyrLK(
            prev_gray, curr_gray, None, None,
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        
        # Calculate motion magnitude
        if flow[0] is not None and flow[1] is not None:
            good_points = flow[1].ravel() == 1
            if np.any(good_points):
                motion_vectors = flow[0][good_points] - flow[0][good_points]  # This would be calculated properly
                motion_magnitude = np.mean(np.linalg.norm(motion_vectors, axis=1)) if len(motion_vectors) > 0 else 0
            else:
                motion_magnitude = 0
        else:
            motion_magnitude = 0
        
        # Frame difference for global motion
        frame_diff = cv2.absdiff(prev_gray, curr_gray)
        global_motion = np.mean(frame_diff)
        
        return {
            'motion_magnitude': float(motion_magnitude),
            'global_motion': float(global_motion),
            'motion_density': float(np.sum(frame_diff > 30) / frame_diff.size)
        }
    
    def _extract_color_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extract color features from frame."""
        # Convert to different color spaces
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Color statistics
        bgr_mean = np.mean(frame, axis=(0, 1))
        bgr_std = np.std(frame, axis=(0, 1))
        
        hsv_mean = np.mean(hsv, axis=(0, 1))
        hsv_std = np.std(hsv, axis=(0, 1))
        
        # Color histogram
        hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])
        
        # Color diversity (number of unique colors)
        unique_colors = len(np.unique(frame.reshape(-1, frame.shape[-1]), axis=0))
        total_pixels = frame.shape[0] * frame.shape[1]
        color_diversity = unique_colors / total_pixels
        
        return {
            'bgr_mean': bgr_mean.tolist(),
            'bgr_std': bgr_std.tolist(),
            'hsv_mean': hsv_mean.tolist(),
            'hsv_std': hsv_std.tolist(),
            'color_diversity': float(color_diversity),
            'histogram_peaks': {
                'blue': int(np.argmax(hist_b)),
                'green': int(np.argmax(hist_g)),
                'red': int(np.argmax(hist_r))
            }
        }
    
    def _extract_composition_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extract composition features from frame."""
        height, width = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Rule of thirds analysis
        third_w, third_h = width // 3, height // 3
        
        # Interest points near rule of thirds intersections
        intersections = [
            (third_w, third_h), (2 * third_w, third_h),
            (third_w, 2 * third_h), (2 * third_w, 2 * third_h)
        ]
        
        # Calculate gradient to find points of interest
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Check activity near intersections
        roi_size = 30
        intersection_scores = []
        
        for x, y in intersections:
            x1, y1 = max(0, x - roi_size), max(0, y - roi_size)
            x2, y2 = min(width, x + roi_size), min(height, y + roi_size)
            
            roi = gradient_magnitude[y1:y2, x1:x2]
            score = np.mean(roi) if roi.size > 0 else 0
            intersection_scores.append(score)
        
        return {
            'rule_of_thirds_score': float(np.mean(intersection_scores)),
            'overall_activity': float(np.mean(gradient_magnitude)),
            'center_activity': float(np.mean(gradient_magnitude[height//4:3*height//4, width//4:3*width//4])),
            'edge_activity': float(np.mean([
                np.mean(gradient_magnitude[:height//4, :]),  # Top
                np.mean(gradient_magnitude[3*height//4:, :]),  # Bottom
                np.mean(gradient_magnitude[:, :width//4]),  # Left
                np.mean(gradient_magnitude[:, 3*width//4:])  # Right
            ]))
        }
    
    def _estimate_frame_noise(self, gray_frame: np.ndarray) -> float:
        """Estimate noise level in frame."""
        # Use Laplacian to estimate noise
        laplacian = cv2.Laplacian(gray_frame, cv2.CV_64F)
        noise_estimate = np.var(laplacian)
        return float(noise_estimate)
    
    def _aggregate_video_features(self, features: Dict[str, List]) -> Dict[str, Any]:
        """Aggregate frame-level features into video-level features."""
        aggregated = {}
        
        # Aggregate visual features
        if features['visual_features']:
            visual_data = {
                'edge_density': [f['edge_density'] for f in features['visual_features']],
                'texture_variance': [f['texture_variance'] for f in features['visual_features']],
                'brightness': [f['brightness'] for f in features['visual_features']],
                'contrast': [f['contrast'] for f in features['visual_features']]
            }
            
            aggregated['visual'] = {}
            for metric, values in visual_data.items():
                aggregated['visual'][metric] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }
        
        # Aggregate motion features
        if features['motion_features']:
            motion_data = {
                'motion_magnitude': [f['motion_magnitude'] for f in features['motion_features']],
                'global_motion': [f['global_motion'] for f in features['motion_features']],
                'motion_density': [f['motion_density'] for f in features['motion_features']]
            }
            
            aggregated['motion'] = {}
            for metric, values in motion_data.items():
                aggregated['motion'][metric] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }
        
        # Aggregate color features
        if features['color_features']:
            # Average color statistics
            bgr_means = [f['bgr_mean'] for f in features['color_features']]
            hsv_means = [f['hsv_mean'] for f in features['color_features']]
            
            aggregated['color'] = {
                'average_bgr': np.mean(bgr_means, axis=0).tolist(),
                'average_hsv': np.mean(hsv_means, axis=0).tolist(),
                'color_diversity': {
                    'mean': float(np.mean([f['color_diversity'] for f in features['color_features']])),
                    'std': float(np.std([f['color_diversity'] for f in features['color_features']]))
                }
            }
        
        # Aggregate composition features
        if features['composition_features']:
            composition_data = {
                'rule_of_thirds_score': [f['rule_of_thirds_score'] for f in features['composition_features']],
                'overall_activity': [f['overall_activity'] for f in features['composition_features']],
                'center_activity': [f['center_activity'] for f in features['composition_features']],
                'edge_activity': [f['edge_activity'] for f in features['composition_features']]
            }
            
            aggregated['composition'] = {}
            for metric, values in composition_data.items():
                aggregated['composition'][metric] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }
        
        return aggregated
    
    def _calculate_video_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall video quality score."""
        score = 100.0
        
        # Sharpness assessment
        sharpness = quality_metrics.get('sharpness', {}).get('mean', 0)
        if sharpness < 100:  # Low sharpness threshold
            score -= (100 - sharpness) * 0.2
        
        # Brightness assessment (optimal range: 100-150)
        brightness = quality_metrics.get('brightness', {}).get('mean', 127)
        if brightness < 50 or brightness > 200:
            score -= abs(brightness - 127) * 0.1
        
        # Contrast assessment
        contrast = quality_metrics.get('contrast', {}).get('mean', 0)
        if contrast < 20:  # Low contrast
            score -= (20 - contrast) * 2
        
        # Noise assessment
        noise = quality_metrics.get('noise', {}).get('mean', 0)
        if noise > 1000:  # High noise
            score -= (noise - 1000) * 0.01
        
        return max(0.0, min(100.0, score))


class ImageFeatureExtractor:
    """Specialized image feature extraction with computer vision analysis."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def extract_technical_metadata(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical image metadata."""



        try:
            with Image.open(file_path) as img:
                # Basic image properties
                width, height = img.size
                format_name = img.format
                mode = img.mode
                
                # EXIF data extraction
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    for tag, value in exif.items():
                        if tag in ExifTags.TAGS:
                            tag_name = ExifTags.TAGS[tag]
                            exif_data[tag_name] = str(value)
                
                # File information
                file_size = Path(file_path).stat().st_size
                
                # Color space information
                color_channels = len(img.getbands()) if hasattr(img, 'getbands') else 1
                
                return {
                    'resolution': f"{width}x{height}",
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'mode': mode,
                    'color_channels': color_channels,
                    'file_size': file_size,
                    'file_size_mb': file_size / (1024 * 1024),
                    'aspect_ratio': width / height if height > 0 else 0,
                    'pixel_count': width * height,
                    'bits_per_pixel': self._estimate_bits_per_pixel(mode),
                    'exif_data': exif_data
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    async def extract_content_features(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract image content features using computer vision."""



        try:
            # Load image with OpenCV for analysis
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not load image")
            
            features = {}
            
            # Color features
            features['color'] = await self._extract_color_features(image)
            
            # Texture features
            features['texture'] = await self._extract_texture_features(image)
            
            # Shape and edge features
            features['shape'] = await self._extract_shape_features(image)
            
            # Composition features
            features['composition'] = await self._extract_composition_features(image)
            
            # Statistical features
            features['statistics'] = await self._extract_statistical_features(image)
            
            return features
            
        except Exception as e:
            return {'error': str(e)}
    
    async def assess_quality(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Assess image quality metrics."""



        try:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not load image")
            
            quality_metrics = {}
            
            # Convert to grayscale for some analyses
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness assessment (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness'] = float(sharpness)
            
            # Brightness assessment
            brightness = gray.mean()
            quality_metrics['brightness'] = float(brightness)
            
            # Contrast assessment
            contrast = gray.std()
            quality_metrics['contrast'] = float(contrast)
            
            # Noise estimation
            noise_estimate = self._estimate_noise(gray)
            quality_metrics['noise_estimate'] = noise_estimate
            
            # Color saturation (for color images)
            if len(image.shape) == 3:
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                saturation = hsv[:, :, 1].mean()
                quality_metrics['saturation'] = float(saturation)
            
            # Exposure assessment
            exposure_quality = self._assess_exposure(gray)
            quality_metrics['exposure'] = exposure_quality
            
            # Compression artifacts detection
            compression_score = self._detect_compression_artifacts(gray)
            quality_metrics['compression_artifacts'] = compression_score
            
            # Overall quality score
            overall_score = self._calculate_image_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = overall_score
            
            return quality_metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _estimate_bits_per_pixel(self, mode: str) -> int:
        """Estimate bits per pixel based on image mode."""
        mode_bits = {
            '1': 1,      # 1-bit pixels, black and white
            'L': 8,      # 8-bit pixels, black and white
            'P': 8,      # 8-bit pixels, mapped to any other mode using a color palette
            'RGB': 24,   # 3x8-bit pixels, true color
            'RGBA': 32,  # 4x8-bit pixels, true color with transparency mask
            'CMYK': 32,  # 4x8-bit pixels, color separation
            'YCbCr': 24, # 3x8-bit pixels, color video format
            'LAB': 24,   # 3x8-bit pixels, the L*a*b* color space
            'HSV': 24    # 3x8-bit pixels, Hue, Saturation, Value color space
        }
        return mode_bits.get(mode, 8)
    
    async def _extract_color_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract comprehensive color features."""
        # Convert to different color spaces
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Basic color statistics
        color_stats = {
            'bgr_mean': np.mean(image, axis=(0, 1)).tolist(),
            'bgr_std': np.std(image, axis=(0, 1)).tolist(),
            'hsv_mean': np.mean(hsv, axis=(0, 1)).tolist(),
            'hsv_std': np.std(hsv, axis=(0, 1)).tolist(),
            'lab_mean': np.mean(lab, axis=(0, 1)).tolist(),
            'lab_std': np.std(lab, axis=(0, 1)).tolist()
        }
        
        # Dominant colors using K-means clustering
        pixels = image.reshape(-1, 3)
        
        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            percentages = np.bincount(labels) / len(labels)
            
            dominant_colors = []
            for i, (color, percentage) in enumerate(zip(colors, percentages)):
                dominant_colors.append({
                    'color_bgr': color.tolist(),
                    'percentage': float(percentage),
                    'color_name': self._color_name_from_bgr(color)
                })
            
            # Sort by percentage
            dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
            color_stats['dominant_colors'] = dominant_colors
            
        except ImportError:
            color_stats['dominant_colors'] = []
        
        # Color harmony analysis
        color_stats['harmony'] = self._analyze_color_harmony(hsv)
        
        # Color temperature estimation
        color_stats['color_temperature'] = self._estimate_color_temperature(image)
        
        return color_stats
    
    def _calculate_image_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall image quality score."""
        score = 100.0
        
        # Sharpness assessment
        sharpness = quality_metrics.get('sharpness', 0)
        if sharpness < 100:
            score -= (100 - sharpness) * 0.3
        
        # Brightness assessment (optimal range: 100-150)
        brightness = quality_metrics.get('brightness', 127)
        brightness_penalty = abs(brightness - 127.5) * 0.2
        score -= brightness_penalty
        
        # Contrast assessment
        contrast = quality_metrics.get('contrast', 0)
        if contrast < 30:
            score -= (30 - contrast) * 1.5
        
        # Noise assessment
        noise = quality_metrics.get('noise_estimate', {}).get('estimated_noise_level', 0)
        if noise > 50:
            score -= (noise - 50) * 0.5
        
        # Exposure assessment
        exposure = quality_metrics.get('exposure', {})
        if exposure.get('shadows_clipped') or exposure.get('highlights_clipped'):
            score -= 15
        
        # Compression artifacts
        compression = quality_metrics.get('compression_artifacts', {})
        artifact_score = compression.get('blocking_artifact_score', 0)
        if artifact_score > 1.0:
            score -= (artifact_score - 1.0) * 10
        
        return max(0.0, min(100.0, score))


class TextFeatureExtractor:
    """Specialized text feature extraction with NLP and linguistic analysis."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize NLP tools
        self._initialize_nlp_tools()
    
    def _initialize_nlp_tools(self):
        """Initialize NLP processing tools."""



        try:
            import spacy
            # Try to load a language model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Fallback to blank model if no model is installed
                self.nlp = spacy.blank("en")
                self.logger.warning("spaCy language model not found, using blank model")
        except ImportError:
            self.nlp = None
            self.logger.warning("spaCy not available, some features will be limited")
    
    async def extract_technical_metadata(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical text metadata."""



        try:
            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Basic text properties
            char_count = len(text)
            word_count = len(text.split())
            line_count = text.count('\n') + 1
            
            # File information
            file_size = Path(file_path).stat().st_size
            
            # Encoding detection
            try:
                import chardet
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                encoding_info = chardet.detect(raw_data)
            except ImportError:
                encoding_info = {'encoding': 'unknown', 'confidence': 0.0}
            
            # Language detection
            language_info = await self._detect_language(text[:1000])  # First 1000 chars
            
            return {
                'character_count': char_count,
                'word_count': word_count,
                'line_count': line_count,
                'paragraph_count': text.count('\n\n') + 1,
                'sentence_count': self._count_sentences(text),
                'file_size': file_size,
                'file_size_kb': file_size / 1024,
                'encoding': encoding_info,
                'language': language_info,
                'avg_word_length': sum(len(word) for word in text.split()) / word_count if word_count > 0 else 0,
                'avg_sentence_length': word_count / max(1, self._count_sentences(text))
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def extract_content_features(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text content features using NLP."""



        try:
            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            features = {}
            
            # Linguistic features
            features['linguistic'] = await self._extract_linguistic_features(text)
            
            # Semantic features
            features['semantic'] = await self._extract_semantic_features(text)
            
            # Stylistic features
            features['stylistic'] = await self._extract_stylistic_features(text)
            
            # Readability features
            features['readability'] = await self._extract_readability_features(text)
            
            # Statistical features
            features['statistics'] = await self._extract_text_statistics(text)
            
            return features
            
        except Exception as e:
            return {'error': str(e)}
    
    async def assess_quality(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Assess text quality metrics."""



        try:
            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            quality_metrics = {}
            
            # Grammar and spelling assessment
            grammar_score = await self._assess_grammar_quality(text)
            quality_metrics['grammar'] = grammar_score
            
            # Readability assessment
            readability_score = await self._assess_readability(text)
            quality_metrics['readability'] = readability_score
            
            # Coherence assessment
            coherence_score = await self._assess_coherence(text)
            quality_metrics['coherence'] = coherence_score
            
            # Vocabulary richness
            vocabulary_score = await self._assess_vocabulary_richness(text)
            quality_metrics['vocabulary_richness'] = vocabulary_score
            
            # Completeness assessment
            completeness_score = await self._assess_completeness(text)
            quality_metrics['completeness'] = completeness_score
            
            # Overall quality score
            overall_score = self._calculate_text_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = overall_score
            
            return quality_metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        if self.nlp:
            doc = self.nlp(text)
            return len(list(doc.sents))
        else:
            # Simple fallback method
            sentence_endings = text.count('.') + text.count('!') + text.count('?')
            return max(1, sentence_endings)
    
    async def _detect_language(self, text_sample: str) -> Dict[str, Any]:
        """Detect text language."""



        try:
            from langdetect import detect, detect_langs
            
            detected_lang = detect(text_sample)
            lang_probabilities = detect_langs(text_sample)
            
            return {
                'detected_language': detected_lang,
                'confidence': float(lang_probabilities[0].prob) if lang_probabilities else 0.0,
                'all_probabilities': [(lang.lang, float(lang.prob)) for lang in lang_probabilities[:3]]
            }
        except ImportError:
            return {'detected_language': 'unknown', 'confidence': 0.0, 'all_probabilities': []}
        except Exception:
            return {'detected_language': 'unknown', 'confidence': 0.0, 'all_probabilities': []}
    
    async def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features from text."""
        features = {}
        
        if self.nlp:
            # Process with spaCy
            doc = self.nlp(text[:100000])  # Limit for performance
            
            # Part-of-speech statistics
            pos_counts = {}
            for token in doc:
                if not token.is_space and not token.is_punct:
                    pos = token.pos_
                    pos_counts[pos] = pos_counts.get(pos, 0) + 1
            
            features['pos_distribution'] = pos_counts
            
            # Named entities
            entities = {}
            for ent in doc.ents:
                label = ent.label_
                entities[label] = entities.get(label, 0) + 1
            
            features['named_entities'] = entities
            
            # Dependency parsing features
            dep_relations = {}
            for token in doc:
                dep = token.dep_
                dep_relations[dep] = dep_relations.get(dep, 0) + 1
            
            features['dependency_relations'] = dep_relations
            
        else:
            # Basic features without spaCy
            words = text.split()
            features['word_frequency'] = self._get_word_frequency(words)
            features['capitalized_words'] = sum(1 for word in words if word and word[0].isupper())
        
        return features
    
    async def _extract_semantic_features(self, text: str) -> Dict[str, Any]:
        """Extract semantic features from text."""
        features = {}
        
        # Topic modeling (simplified)
        features['topic_keywords'] = await self._extract_topic_keywords(text)
        
        # Sentiment analysis (basic)
        features['sentiment'] = await self._analyze_sentiment(text)
        
        # Semantic density
        features['semantic_density'] = await self._calculate_semantic_density(text)
        
        return features
    
    async def _extract_stylistic_features(self, text: str) -> Dict[str, Any]:
        """Extract stylistic features from text."""
        features = {}
        
        words = text.split()
        sentences = text.split('.')
        
        # Lexical diversity
        unique_words = set(word.lower().strip('.,!?;:"()[]') for word in words if word)
        features['lexical_diversity'] = len(unique_words) / len(words) if words else 0
        
        # Average sentence length variation
        sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]
        if sentence_lengths:
            features['sentence_length_variance'] = float(np.var(sentence_lengths))
            features['avg_sentence_length'] = float(np.mean(sentence_lengths))
        
        # Punctuation usage
        punct_chars = '.,!?;:"()[]'
        punct_count = sum(text.count(char) for char in punct_chars)
        features['punctuation_density'] = punct_count / len(text) if text else 0
        
        # Formality indicators
        features['formality_score'] = await self._assess_formality(text)
        
        return features
    
    async def _extract_readability_features(self, text: str) -> Dict[str, Any]:
        """Extract readability features."""
        features = {}
        
        words = text.split()
        sentences = self._count_sentences(text)
        
        # Flesch Reading Ease (simplified)
        if words and sentences > 0:
            avg_sentence_length = len(words) / sentences
            avg_syllables = sum(self._count_syllables(word) for word in words) / len(words)
            
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
            features['flesch_reading_ease'] = max(0, min(100, flesch_score))
            
            # Flesch-Kincaid Grade Level
            grade_level = (0.39 * avg_sentence_length) + (11.8 * avg_syllables) - 15.59
            features['flesch_kincaid_grade'] = max(0, grade_level)
        
        # Automated Readability Index (ARI)
        if words and sentences > 0:
            chars = len([c for c in text if c.isalnum()])
            ari = 4.71 * (chars / len(words)) + 0.5 * (len(words) / sentences) - 21.43
            features['automated_readability_index'] = max(0, ari)
        
        return features
    
    async def _extract_text_statistics(self, text: str) -> Dict[str, Any]:
        """Extract statistical features from text."""
        stats = {}
        
        words = text.split()
        chars = list(text)
        
        # Character statistics
        stats['character_distribution'] = {
            'letters': sum(1 for c in chars if c.isalpha()),
            'digits': sum(1 for c in chars if c.isdigit()),
            'spaces': sum(1 for c in chars if c.isspace()),
            'punctuation': sum(1 for c in chars if not c.isalnum() and not c.isspace())
        }
        
        # Word length distribution
        word_lengths = [len(word.strip('.,!?;:"()[]')) for word in words if word]
        if word_lengths:
            stats['word_length'] = {
                'mean': float(np.mean(word_lengths)),
                'std': float(np.std(word_lengths)),
                'min': int(np.min(word_lengths)),
                'max': int(np.max(word_lengths)),
                'median': float(np.median(word_lengths))
            }
        
        # Vocabulary richness
        unique_words = set(word.lower().strip('.,!?;:"()[]') for word in words if word)
        stats['vocabulary_richness'] = {
            'type_token_ratio': len(unique_words) / len(words) if words else 0,
            'unique_words': len(unique_words),
            'total_words': len(words)
        }
        
        return stats
    
    def _get_word_frequency(self, words: List[str]) -> Dict[str, int]:
        """Get word frequency distribution."""
        word_freq = {}
        for word in words:
            clean_word = word.lower().strip('.,!?;:"()[]')
            if clean_word:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Return top 20 most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_words[:20])
    
    async def _extract_topic_keywords(self, text: str) -> List[str]:
        """Extract topic keywords from text."""



        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Simple TF-IDF based keyword extraction
            sentences = text.split('.')
            if len(sentences) < 2:
                return []
            
            vectorizer = TfidfVectorizer(max_features=10, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top keywords
            scores = tfidf_matrix.sum(axis=0).A1
            keywords = [(feature_names[i], scores[i]) for i in scores.argsort()[-10:][::-1]]
            
            return [keyword for keyword, score in keywords if score > 0]
            
        except ImportError:
            # Fallback: simple frequency-based keywords
            words = text.lower().split()
            word_freq = {}
            
            # Filter common words and get frequency
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
            
            for word in words:
                clean_word = word.strip('.,!?;:"()[]')
                if len(clean_word) > 3 and clean_word not in common_words:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            # Return top 10 keywords
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:10]]
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""



        try:
            from textblob import TextBlob
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment_label = 'positive'
            elif polarity < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            return {
                'polarity': float(polarity),
                'subjectivity': float(subjectivity),
                'sentiment_label': sentiment_label
            }
            
        except ImportError:
            # Simple rule-based fallback
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting']
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if any(pos in word for pos in positive_words))
            negative_count = sum(1 for word in words if any(neg in word for neg in negative_words))
            
            if positive_count > negative_count:
                sentiment_label = 'positive'
                polarity = 0.5
            elif negative_count > positive_count:
                sentiment_label = 'negative'
                polarity = -0.5
            else:
                sentiment_label = 'neutral'
                polarity = 0.0
            
            return {
                'polarity': polarity,
                'subjectivity': 0.5,
                'sentiment_label': sentiment_label
            }
    
    async def _calculate_semantic_density(self, text: str) -> float:
        """Calculate semantic density of text."""
        words = text.split()
        if not words:
            return 0.0
        
        # Simple measure: ratio of content words to total words
        content_words = 0
        function_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'would', 'could', 'should'}
        
        for word in words:
            clean_word = word.lower().strip('.,!?;:"()[]')
            if clean_word and clean_word not in function_words:
                content_words += 1
        
        return content_words / len(words)
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (approximate)."""
        word = word.lower().strip('.,!?;:"()[]')
        if not word:
            return 0
        
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    async def _assess_grammar_quality(self, text: str) -> Dict[str, Any]:
        """Assess grammar quality of text."""



        try:
            import language_tool_python
            
            tool = language_tool_python.LanguageTool('en-US')
            matches = tool.check(text[:5000])  # Limit for performance
            
            error_count = len(matches)
            word_count = len(text.split())
            
            # Calculate error rate
            error_rate = error_count / word_count if word_count > 0 else 0
            
            # Categorize errors
            error_types = {}
            for match in matches:
                category = match.category
                error_types[category] = error_types.get(category, 0) + 1
            
            grammar_score = max(0, 100 - (error_rate * 100))
            
            return {
                'grammar_score': float(grammar_score),
                'error_count': error_count,
                'error_rate': float(error_rate),
                'error_types': error_types
            }
            
        except ImportError:
            # Simple fallback: check for basic patterns
            word_count = len(text.split())
            
            # Very basic checks
            issues = 0
            
            # Check for repeated words
            words = text.lower().split()
            for i in range(len(words) - 1):
                if words[i] == words[i + 1]:
                    issues += 1
            
            # Check for missing capitalization at sentence start
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and not sentence[0].isupper():
                    issues += 1
            
            error_rate = issues / word_count if word_count > 0 else 0
            grammar_score = max(0, 100 - (error_rate * 50))
            
            return {
                'grammar_score': float(grammar_score),
                'error_count': issues,
                'error_rate': float(error_rate),
                'error_types': {'basic_issues': issues}
            }
    
    async def _assess_readability(self, text: str) -> Dict[str, Any]:
        """Assess readability of text."""
        readability_features = await self._extract_readability_features(text)
        
        # Average the readability scores
        scores = []
        if 'flesch_reading_ease' in readability_features:
            scores.append(readability_features['flesch_reading_ease'])
        
        if 'automated_readability_index' in readability_features:
            # Convert ARI to 0-100 scale (inverse, lower ARI = higher readability)
            ari_score = max(0, 100 - readability_features['automated_readability_index'] * 5)
            scores.append(ari_score)
        
        overall_readability = sum(scores) / len(scores) if scores else 50
        
        return {
            'overall_readability_score': float(overall_readability),
            'individual_scores': readability_features
        }
    
    async def _assess_coherence(self, text: str) -> Dict[str, Any]:
        """Assess coherence and cohesion of text."""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return {'coherence_score': 50.0, 'metrics': {}}
        
        # Simple coherence measures
        coherence_metrics = {}
        
        # Lexical cohesion: repeated words across sentences
        all_words = set()
        sentence_words = []
        
        for sentence in sentences:
            words = set(word.lower().strip('.,!?;:"()[]') for word in sentence.split() if word)
            sentence_words.append(words)
            all_words.update(words)
        
        # Calculate overlap between adjacent sentences
        overlaps = []
        for i in range(len(sentence_words) - 1):
            overlap = len(sentence_words[i] & sentence_words[i + 1])
            total_unique = len(sentence_words[i] | sentence_words[i + 1])
            overlap_ratio = overlap / total_unique if total_unique > 0 else 0
            overlaps.append(overlap_ratio)
        
        coherence_metrics['lexical_cohesion'] = float(np.mean(overlaps)) if overlaps else 0
        
        # Sentence length consistency
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        length_variance = np.var(sentence_lengths) if sentence_lengths else 0
        consistency_score = max(0, 1 - (length_variance / 100))  # Normalize
        coherence_metrics['length_consistency'] = float(consistency_score)
        
        # Overall coherence score
        coherence_score = (coherence_metrics['lexical_cohesion'] * 0.7 + 
                          coherence_metrics['length_consistency'] * 0.3) * 100
        
        return {
            'coherence_score': float(coherence_score),
            'metrics': coherence_metrics
        }
    
    async def _assess_vocabulary_richness(self, text: str) -> Dict[str, Any]:
        """Assess vocabulary richness and diversity."""
        words = [word.lower().strip('.,!?;:"()[]') for word in text.split() if word]
        
        if not words:
            return {'richness_score': 0.0, 'metrics': {}}
        
        unique_words = set(words)
        
        # Type-token ratio
        ttr = len(unique_words) / len(words)
        
        # Vocabulary sophistication (approximate)
        long_words = [word for word in unique_words if len(word) > 6]
        sophistication = len(long_words) / len(unique_words)
        
        # Lexical diversity using word frequency distribution
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Calculate entropy of word distribution
        total_words = len(words)
        entropy = -sum((freq / total_words) * np.log2(freq / total_words) 
                      for freq in word_freq.values())
        
        # Normalize entropy (approximate)
        max_entropy = np.log2(len(unique_words)) if unique_words else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Overall richness score
        richness_score = (ttr * 0.4 + sophistication * 0.3 + normalized_entropy * 0.3) * 100
        
        return {
            'richness_score': float(richness_score),
            'metrics': {
                'type_token_ratio': float(ttr),
                'vocabulary_sophistication': float(sophistication),
                'lexical_diversity': float(normalized_entropy),
                'unique_words': len(unique_words),
                'total_words': len(words)
            }
        }
    
    async def _assess_completeness(self, text: str) -> Dict[str, Any]:
        """Assess completeness of text content."""
        # Simple completeness heuristics
        completeness_metrics = {}
        
        # Check for proper structure
        has_introduction = bool(text[:200].strip())  # First 200 chars as intro
        has_conclusion = bool(text[-200:].strip())   # Last 200 chars as conclusion
        
        completeness_metrics['has_introduction'] = has_introduction
        completeness_metrics['has_conclusion'] = has_conclusion
        
        # Check for balanced content
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) >= 3:
            # Check if content is evenly distributed
            sentence_lengths = [len(sentence.split()) for sentence in sentences]
            length_variance = np.var(sentence_lengths)
            balanced_content = length_variance < 50  # Arbitrary threshold
        else:
            balanced_content = False
        
        completeness_metrics['balanced_content'] = balanced_content
        
        # Check for sufficient detail
        word_count = len(text.split())
        sufficient_length = word_count >= 50  # Minimum word count
        
        completeness_metrics['sufficient_length'] = sufficient_length
        
        # Calculate overall completeness score
        score_components = [
            has_introduction,
            has_conclusion,
            balanced_content,
            sufficient_length
        ]
        
        completeness_score = (sum(score_components) / len(score_components)) * 100
        
        return {
            'completeness_score': float(completeness_score),
            'metrics': completeness_metrics
        }
    
    async def _assess_formality(self, text: str) -> float:
        """Assess formality level of text."""
        # Simple formality indicators
        formal_indicators = ['therefore', 'furthermore', 'consequently', 'moreover', 'nevertheless', 'however']
        informal_indicators = ["don't", "can't", "won't", "it's", "that's", 'really', 'very', 'pretty', 'quite']
        
        words = text.lower().split()
        
        formal_count = sum(1 for word in words if any(indicator in word for indicator in formal_indicators))
        informal_count = sum(1 for word in words if any(indicator in word for indicator in informal_indicators))
        
        total_indicators = formal_count + informal_count
        
        if total_indicators == 0:
            return 0.5  # Neutral
        
        formality_ratio = formal_count / total_indicators
        return formality_ratio
    
    def _calculate_text_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall text quality score."""
        score = 100.0
        
        # Grammar quality (30% weight)
        grammar = quality_metrics.get('grammar', {})
        grammar_score = grammar.get('grammar_score', 75)
        score = score * 0.7 + grammar_score * 0.3
        
        # Readability (25% weight)
        readability = quality_metrics.get('readability', {})
        readability_score = readability.get('overall_readability_score', 75)
        score = score * 0.75 + readability_score * 0.25
        
        # Coherence (20% weight)
        coherence = quality_metrics.get('coherence', {})
        coherence_score = coherence.get('coherence_score', 75)
        score = score * 0.8 + coherence_score * 0.2
        
        # Vocabulary richness (15% weight)
        vocabulary = quality_metrics.get('vocabulary_richness', {})
        vocabulary_score = vocabulary.get('richness_score', 75)
        score = score * 0.85 + vocabulary_score * 0.15
        
        # Completeness (10% weight)
        completeness = quality_metrics.get('completeness', {})
        completeness_score = completeness.get('completeness_score', 75)
        score = score * 0.9 + completeness_score * 0.1
        
        return max(0.0, min(100.0, score))


class MultiFormatExtractor:
    """Multi-format content extractor supporting audio, video, image, and text files."""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("multi_format_extractor")
        self.file_handler = FileHandler()
        
        # Initialize format-specific extractors
        self.extractors = {
            'audio': AudioExtractor(config),
            'video': VideoExtractor(config),
            'image': ImageExtractor(config),
            'text': TextExtractor(config)
        }
        
        # Supported format mappings
        self.format_mappings = self._build_format_mappings()
    
    def _build_format_mappings(self) -> Dict[str, str]:
        """Build mapping from file extensions to content types."""



        return {
            # Audio formats
            '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio', '.aac': 'audio',
            '.ogg': 'audio', '.m4a': 'audio', '.wma': 'audio',
            
            # Video formats
            '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.mkv': 'video',
            '.wmv': 'video', '.flv': 'video', '.webm': 'video',
            
            # Image formats
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image',
            '.bmp': 'image', '.tiff': 'image', '.webp': 'image', '.svg': 'image',
            
            # Text formats
            '.txt': 'text', '.md': 'text', '.html': 'text', '.xml': 'text',
            '.json': 'text', '.csv': 'text', '.rtf': 'text'
        }
    
    @monitor_performance
    async def extract_content(
        self,
        source_path: Union[str, Path],
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract content from file with automatic format detection.
        
        Args:
            source_path: Path to content file
            content_type: Optional content type override
            
        Returns:
            Extracted content data with metadata
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise ExtractionError(f"Source file not found: {source_path}")
        
        # Detect content type if not provided
        if not content_type:
            content_type = await self._detect_content_type(source_path)
        
        if content_type not in self.extractors:
            raise UnsupportedFormatError(f"Unsupported content type: {content_type}")
        
        # Extract using appropriate extractor
        extractor = self.extractors[content_type]
        
        extraction_start = datetime.utcnow()
        
        try:
            extracted_data = await extractor.extract(source_path)
            
            # Add common metadata
            extracted_data.update({
                'source_path': str(source_path),
                'content_type': content_type,
                'file_size': source_path.stat().st_size,
                'extraction_timestamp': extraction_start.isoformat(),
                'extraction_duration_ms': (
                    datetime.utcnow() - extraction_start
                ).total_seconds() * 1000
            })
            
            self.metrics.increment('successful_extractions')
            self.metrics.histogram(
                f'extraction_duration_{content_type}',
                extracted_data['extraction_duration_ms']
            )
            
            return extracted_data
            
        except Exception as e:
            self.metrics.increment('failed_extractions')
            self.logger.error(f"Extraction failed for {source_path}: {e}")
            raise ExtractionError(f"Content extraction failed: {e}")
    
    async def _detect_content_type(self, file_path: Path) -> str:
        """Detect content type from file extension and MIME type."""
        
        # Check file extension
        extension = file_path.suffix.lower()
        if extension in self.format_mappings:
            detected_type = self.format_mappings[extension]
            
            # Verify with MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type:
                mime_category = mime_type.split('/')[0]
                if mime_category in ['audio', 'video', 'image', 'text']:
                    if mime_category == detected_type:
                        return detected_type
            
            return detected_type
        
        # Fallback to MIME type detection
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            mime_category = mime_type.split('/')[0]
            if mime_category in ['audio', 'video', 'image', 'text']:
                return mime_category
        
        raise UnsupportedFormatError(f"Cannot detect content type for: {file_path}")
    
    @cache_result(ttl=3600)
    async def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported formats by content type."""
        
        supported = {}
        for extension, content_type in self.format_mappings.items():
            if content_type not in supported:
                supported[content_type] = []
            supported[content_type].append(extension)
        
        return supported


class MetadataExtractor:
    """
    Comprehensive metadata extraction for all content types
    with AI-powered analysis and semantic understanding.
    """
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("metadata_extractor")
        
        # Initialize AI models for metadata analysis
        self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models for metadata analysis."""
        
        # Text analysis models
        self.text_classifier = pipeline("text-classification", 
                                       model="cardiffnlp/twitter-roberta-base-emotion")
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        
        # Image analysis models
        self.image_classifier = pipeline("image-classification", 
                                        model="google/vit-base-patch16-224")
        
        # Audio analysis models (using pre-trained models)
        # Note: In production, load actual pre-trained models
        
    @monitor_performance
    async def extract_metadata(
        self,
        content_path: Union[str, Path],
        content_type: str
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from content.
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            
        Returns:
            Comprehensive metadata dictionary
        """
        
        content_path = Path(content_path)
        
        # Extract basic file metadata
        basic_metadata = await self._extract_basic_metadata(content_path)
        
        # Extract content-specific metadata
        content_metadata = await self._extract_content_metadata(content_path, content_type)
        
        # Extract AI-powered semantic metadata
        semantic_metadata = await self._extract_semantic_metadata(content_path, content_type)
        
        # Combine all metadata
        complete_metadata = {
            **basic_metadata,
            **content_metadata,
            **semantic_metadata,
            'metadata_extraction_timestamp': datetime.utcnow().isoformat(),
            'extractor_version': '2.0.0'
        }
        
        return complete_metadata
    
    async def _extract_basic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic file system metadata."""
        
        stat = file_path.stat()
        
        return {
            'filename': file_path.name,
            'file_extension': file_path.suffix.lower(),
            'file_size_bytes': stat.st_size,
            'created_timestamp': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'file_hash_md5': await self._calculate_file_hash(file_path, 'md5'),
            'file_hash_sha256': await self._calculate_file_hash(file_path, 'sha256')
        }
    
    async def _calculate_file_hash(self, file_path: Path, algorithm: str) -> str:
        """Calculate file hash using specified algorithm."""
        
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    async def _extract_content_metadata(
        self,
        file_path: Path,
        content_type: str
    ) -> Dict[str, Any]:
        """Extract content-type specific metadata."""
        
        if content_type == 'audio':
            return await self._extract_audio_metadata(file_path)
        elif content_type == 'video':
            return await self._extract_video_metadata(file_path)
        elif content_type == 'image':
            return await self._extract_image_metadata(file_path)
        elif content_type == 'text':
            return await self._extract_text_metadata(file_path)
        else:
            return {}
    
    async def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio-specific metadata."""
        
        metadata = {}
        
        try:
            # Extract using mutagen for ID3 tags
            audio_file = MutagenFile(file_path)
            if audio_file:
                metadata.update({
                    'title': str(audio_file.get('TIT2', [''])[0]) if audio_file.get('TIT2') else '',
                    'artist': str(audio_file.get('TPE1', [''])[0]) if audio_file.get('TPE1') else '',
                    'album': str(audio_file.get('TALB', [''])[0]) if audio_file.get('TALB') else '',
                    'genre': str(audio_file.get('TCON', [''])[0]) if audio_file.get('TCON') else '',
                    'year': str(audio_file.get('TDRC', [''])[0]) if audio_file.get('TDRC') else '',
                    'duration_seconds': audio_file.info.length if hasattr(audio_file, 'info') else 0
                })
            
            # Extract using librosa for audio features
            y, sr = librosa.load(file_path, sr=None)
            
            metadata.update({
                'sample_rate': sr,
                'duration_librosa': len(y) / sr,
                'channels': 1 if y.ndim == 1 else y.shape[0],
                'rms_energy': float(np.mean(librosa.feature.rms(y=y))),
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y)))
            })
            
        except Exception as e:
            self.logger.error(f"Audio metadata extraction error: {e}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract video-specific metadata."""
        
        metadata = {}
        
        try:
            # Extract using OpenCV
            cap = cv2.VideoCapture(str(file_path))
            
            if cap.isOpened():
                metadata.update({
                    'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'fps': cap.get(cv2.CAP_PROP_FPS),
                    'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                    'duration_seconds': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
                })
                
                cap.release()
            
            # Extract using ffmpeg-python for additional metadata
            probe = ffmpeg.probe(str(file_path))
            
            for stream in probe['streams']:
                if stream['codec_type'] == 'video':
                    metadata.update({
                        'codec': stream.get('codec_name', ''),
                        'bit_rate': stream.get('bit_rate', ''),
                        'avg_frame_rate': stream.get('avg_frame_rate', ''),
                        'pixel_format': stream.get('pix_fmt', '')
                    })
                    break
            
        except Exception as e:
            self.logger.error(f"Video metadata extraction error: {e}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image-specific metadata."""
        
        metadata = {}
        
        try:
            with Image.open(file_path) as img:
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                })
                
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    exif_data = {}
                    
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                    
                    metadata['exif'] = exif_data
                
                # Calculate image statistics
                img_array = np.array(img.convert('RGB'))
                metadata.update({
                    'mean_brightness': float(np.mean(img_array)),
                    'std_brightness': float(np.std(img_array)),
                    'dominant_colors': self._extract_dominant_colors(img_array)
                })
                
        except Exception as e:
            self.logger.error(f"Image metadata extraction error: {e}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _extract_dominant_colors(self, img_array: np.ndarray, k: int = 5) -> List[List[int]]:
        """Extract dominant colors from image using K-means clustering."""



        
        try:
            from sklearn.cluster import KMeans
            
            # Reshape image to list of pixels
            pixels = img_array.reshape(-1, 3)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get dominant colors
            colors = kmeans.cluster_centers_.astype(int)
            
            return colors.tolist()
            
        except Exception:
            return []
    
    async def _extract_text_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract text-specific metadata."""
        
        metadata = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
            
            # Basic text statistics
            words = text_content.split()
            sentences = text_content.split('.')
            
            metadata.update({
                'character_count': len(text_content),
                'word_count': len(words),
                'sentence_count': len(sentences),
                'paragraph_count': len(text_content.split('\n\n')),
                'average_word_length': np.mean([len(word) for word in words]) if words else 0,
                'language_detected': self._detect_language(text_content)
            })
            
            # Extract keywords using TF-IDF
            if words:
                tfidf = TfidfVectorizer(max_features=10, stop_words='english')
                try:
                    tfidf_matrix = tfidf.fit_transform([text_content])
                    feature_names = tfidf.get_feature_names_out()
                    metadata['keywords'] = feature_names.tolist()
                except:
                    metadata['keywords'] = []
            
        except Exception as e:
            self.logger.error(f"Text metadata extraction error: {e}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text content."""



        
        try:
            from langdetect import detect
            return detect(text)
        except:
            return 'unknown'
    
    async def _extract_semantic_metadata(
        self,
        file_path: Path,
        content_type: str
    ) -> Dict[str, Any]:
        """Extract AI-powered semantic metadata."""
        
        semantic_data = {}
        
        try:
            if content_type == 'text':
                semantic_data = await self._analyze_text_semantics(file_path)
            elif content_type == 'image':
                semantic_data = await self._analyze_image_semantics(file_path)
            elif content_type == 'audio':
                semantic_data = await self._analyze_audio_semantics(file_path)
            elif content_type == 'video':
                semantic_data = await self._analyze_video_semantics(file_path)
                
        except Exception as e:
            self.logger.error(f"Semantic analysis error for {content_type}: {e}")
            semantic_data['semantic_error'] = str(e)
        
        return semantic_data
    
    async def _analyze_text_semantics(self, file_path: Path) -> Dict[str, Any]:
        """Analyze text content for semantic meaning."""
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        if not text.strip():
            return {}
        
        # Sentiment analysis
        sentiment_result = self.sentiment_analyzer(text[:512])  # Limit for model
        
        # Emotion analysis
        emotion_result = self.text_classifier(text[:512])
        
        return {
            'sentiment': sentiment_result[0] if sentiment_result else {},
            'emotion': emotion_result[0] if emotion_result else {},
            'semantic_tags': self._extract_semantic_tags(text)
        }
    
    def _extract_semantic_tags(self, text: str) -> List[str]:
        """Extract semantic tags from text using NLP."""



        
        try:
            # Use spaCy for named entity recognition
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text[:1000])  # Limit text length
            
            tags = []
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT', 'WORK_OF_ART']:
                    tags.append(ent.text.lower())
            
            return list(set(tags))[:10]  # Return top 10 unique tags
            
        except Exception:
            return []
    
    async def _analyze_image_semantics(self, file_path: Path) -> Dict[str, Any]:
        """Analyze image content for semantic meaning."""



        
        try:
            # Image classification
            image = Image.open(file_path).convert('RGB')
            classification_result = self.image_classifier(image)
            
            return {
                'objects_detected': classification_result[:5],  # Top 5 predictions
                'scene_type': self._classify_scene_type(classification_result)
            }
            
        except Exception as e:
            return {'analysis_error': str(e)}
    
    def _classify_scene_type(self, classification_result: List[Dict]) -> str:
        """Classify scene type based on detected objects."""
        
        # Simple scene classification based on detected objects
        outdoor_keywords = ['mountain', 'tree', 'sky', 'beach', 'field']
        indoor_keywords = ['room', 'furniture', 'kitchen', 'bedroom']
        
        detected_labels = [item['label'].lower() for item in classification_result]
        
        outdoor_score = sum(1 for label in detected_labels if any(kw in label for kw in outdoor_keywords))
        indoor_score = sum(1 for label in detected_labels if any(kw in label for kw in indoor_keywords))
        
        if outdoor_score > indoor_score:
            return 'outdoor'
        elif indoor_score > 0:
            return 'indoor'
        else:
            return 'unknown'


class FeatureExtractor:
    """
    Advanced feature extraction for machine learning and AI processing
    with content-specific feature engineering and optimization.
    """
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.feature_extractors = {}
        self._initialize_feature_extractors()
    
    def _initialize_feature_extractors(self):
        """Initialize specialized feature extractors."""
        
        self.feature_extractors = {
            'audio': AudioFeatureExtractor(),
            'video': VideoFeatureExtractor(),
            'image': ImageFeatureExtractor(),
            'text': TextFeatureExtractor()
        }
    
    @monitor_performance
    async def extract_features(
        self,
        content_data: Dict[str, Any],
        feature_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract comprehensive features for ML/AI processing.
        
        Args:
            content_data: Content data with metadata
            feature_config: Feature extraction configuration
            
        Returns:
            Extracted features dictionary
        """
        
        content_type = content_data.get('type')
        if content_type not in self.feature_extractors:
            raise ExtractionError(f"No feature extractor for {content_type}")
        
        extractor = self.feature_extractors[content_type]
        
        # Extract features using specialized extractor
        features = await extractor.extract_features(content_data, feature_config)
        
        # Add common feature metadata
        features['feature_extraction_metadata'] = {
            'extracted_at': datetime.utcnow().isoformat(),
            'extractor_version': extractor.version,
            'feature_count': len([k for k in features.keys() if not k.endswith('_metadata')])
        }
        
        return features


class ContentExtractor:
    """
    Unified content extractor orchestrating all extraction processes
    with intelligent caching and optimization strategies.
    """
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("content_extractor")
        
        # Initialize component extractors
        self.multi_format_extractor = MultiFormatExtractor(config)
        self.metadata_extractor = MetadataExtractor(config)
        self.feature_extractor = FeatureExtractor(config)
        
        # Setup caching
        self.cache_enabled = config.enable_caching
        self.cache_ttl = config.cache_ttl
    
    @monitor_performance
    @cache_result(ttl=3600)
    async def extract_complete_content(
        self,
        source_path: Union[str, Path],
        extraction_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform complete content extraction including data, metadata, and features.
        
        Args:
            source_path: Path to content file
            extraction_options: Optional extraction configuration
            
        Returns:
            Complete extraction results
        """
        
        extraction_options = extraction_options or {}
        
        # Extract basic content
        content_data = await self.multi_format_extractor.extract_content(source_path)
        
        # Extract comprehensive metadata
        if extraction_options.get('extract_metadata', True):
            metadata = await self.metadata_extractor.extract_metadata(
                source_path,
                content_data['content_type']
            )
            content_data['metadata'] = metadata
        
        # Extract features for ML/AI
        if extraction_options.get('extract_features', False):
            features = await self.feature_extractor.extract_features(
                content_data,
                extraction_options.get('feature_config', {})
            )
            content_data['features'] = features
        
        # Add extraction summary
        content_data['extraction_summary'] = {
            'complete_extraction_timestamp': datetime.utcnow().isoformat(),
            'extraction_components': [
                'content_data',
                'metadata' if extraction_options.get('extract_metadata', True) else None,
                'features' if extraction_options.get('extract_features', False) else None
            ],
            'total_extraction_time_ms': content_data.get('extraction_duration_ms', 0)
        }
        
        return content_data
