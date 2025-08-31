"""Content Processing Middleware Module
===================================

Enterprise-grade content processing middleware for crawler pipeline.
Implements multi-format processing, transformation, and enrichment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""import asyncio
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from pathlib import Path
import mimetypes
from pydantic import BaseModel, Field
import logging

# Processing libraries
import numpy as np
import pandas as pd
from PIL import Image
import cv2
import librosa
import nltk
from transformers import pipeline
import magic

from ...config.settings import get_settings
from ...utils.cache import CacheManager
from ...ai.models.protection_models import UniversalFingerprintEngine

settings = get_settings()
logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Supported content types"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""    VALIDATION = "validation"
    EXTRACTION = "extraction"
    TRANSFORMATION = "transformation"
    ENRICHMENT = "enrichment"
    FINGERPRINTING = "fingerprinting"
    OPTIMIZATION = "optimization"


class ProcessingStatus(str, Enum):
    """Processing status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ContentProcessingRequest(BaseModel):
    """Content processing request model"""    content_id: str = Field(description="Unique content identifier")
    content_type: ContentType = Field(description="Type of content")
    content_data: Union[str, bytes, Dict[str, Any]] = Field(description="Content data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    processing_options: Dict[str, Any] = Field(default_factory=dict, description="Processing options")
    quality_requirements: Dict[str, Any] = Field(default_factory=dict, description="Quality requirements")
    output_formats: List[str] = Field(default_factory=list, description="Desired output formats")


class ProcessingResult(BaseModel):
    """Content processing result model"""    content_id: str = Field(description="Content identifier")
    status: ProcessingStatus = Field(description="Processing status")
    processed_content: Optional[Dict[str, Any]] = Field(None, description="Processed content")
    fingerprint: Optional[str] = Field(None, description="Content fingerprint")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Enhanced metadata")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Quality metrics")
    processing_time: float = Field(description="Processing duration")
    stages_completed: List[ProcessingStage] = Field(default_factory=list, description="Completed stages")
    error: Optional[str] = Field(None, description="Error message if failed")


class AudioProcessor:
    """Advanced audio content processor"""    
    def __init__(self):
        self.supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
        
    async def process(self, content_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio content"""        try:
            # Load audio data
            audio_array, sample_rate = await self.load_audio(content_data)
            
            # Extract features
            features = await self.extract_audio_features(audio_array, sample_rate)
            
            # Enhance metadata
            enhanced_metadata = await self.enhance_audio_metadata(features, metadata)
            
            # Generate fingerprint
            fingerprint = await self.generate_audio_fingerprint(audio_array, sample_rate)
            
            return {
                "features": features,
                "metadata": enhanced_metadata,
                "fingerprint": fingerprint,
                "quality_metrics": await self.calculate_audio_quality(audio_array, sample_rate)
            }
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            raise
    
    async def load_audio(self, content_data: bytes) -> Tuple[np.ndarray, int]:
        """Load audio from bytes"""        import io
        import tempfile
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(content_data)
            temp_path = temp_file.name
        
        try:
            # Load with librosa
            audio_array, sample_rate = librosa.load(temp_path, sr=None)
            return audio_array, sample_rate
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    async def extract_audio_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract comprehensive audio features"""        features = {}
        
        # Basic features
        features['duration'] = len(audio) / sr
        features['sample_rate'] = sr
        features['channels'] = 1 if audio.ndim == 1 else audio.shape[1]
        
        # Spectral features
        features['mfcc'] = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13).tolist()
        features['chroma'] = librosa.feature.chroma(y=audio, sr=sr).tolist()
        features['spectral_centroid'] = librosa.feature.spectral_centroid(y=audio, sr=sr).tolist()
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(y=audio, sr=sr).tolist()
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(y=audio, sr=sr).tolist()
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(audio).tolist()
        
        # Rhythm features
        tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
        features['tempo'] = float(tempo)
        features['beats'] = beats.tolist()
        
        # Energy features
        features['rms_energy'] = librosa.feature.rms(y=audio).tolist()
        
        return features
    
    async def enhance_audio_metadata(self, features: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance audio metadata with extracted features"""        enhanced = metadata.copy()
        
        # Add technical metadata
        enhanced.update({
            'duration_seconds': features['duration'],
            'sample_rate_hz': features['sample_rate'],
            'estimated_tempo_bpm': features['tempo'],
            'audio_fingerprint_type': 'chromaprint',
            'feature_extraction_timestamp': datetime.utcnow().isoformat()
        })
        
        # Classify genre based on features (simplified)
        genre_score = await self.classify_audio_genre(features)
        enhanced['estimated_genre'] = genre_score
        
        return enhanced
    
    async def classify_audio_genre(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Simple genre classification based on features"""        # Simplified genre classification logic
        tempo = features.get('tempo', 120)
        
        scores = {}
        if tempo > 140:
            scores['electronic'] = 0.8
            scores['dance'] = 0.7
        elif tempo > 120:
            scores['pop'] = 0.6
            scores['rock'] = 0.5
        else:
            scores['classical'] = 0.7
            scores['ambient'] = 0.6
        
        return scores
    
    async def generate_audio_fingerprint(self, audio: np.ndarray, sr: int) -> str:
        """Generate audio fingerprint"""        # Use chromaprint for audio fingerprinting
        import chromaprint
        
        # Convert to int16 format expected by chromaprint
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Generate fingerprint
        fingerprint = chromaprint.encode(audio_int16, sr)
        
        return fingerprint
    
    async def calculate_audio_quality(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Calculate audio quality metrics"""        metrics = {}
        
        # Signal-to-noise ratio estimation
        signal_power = np.mean(audio ** 2)
        noise_floor = np.percentile(np.abs(audio), 10) ** 2
        snr = 10 * np.log10(signal_power / max(noise_floor, 1e-10))
        metrics['snr_db'] = float(snr)
        
        # Dynamic range
        dynamic_range = 20 * np.log10(np.max(np.abs(audio)) / max(np.mean(np.abs(audio)), 1e-10))
        metrics['dynamic_range_db'] = float(dynamic_range)
        
        # Clipping detection
        clipping_ratio = np.sum(np.abs(audio) > 0.99) / len(audio)
        metrics['clipping_ratio'] = float(clipping_ratio)
        
        # Overall quality score (0-1)
        quality_score = min(1.0, (snr / 40 + (1 - clipping_ratio) + dynamic_range / 60) / 3)
        metrics['quality_score'] = float(quality_score)
        
        return metrics


class VideoProcessor:
    """Advanced video content processor"""    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
    async def process(self, content_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process video content"""        try:
            # Load video
            frames, fps, duration = await self.load_video(content_data)
            
            # Extract features
            features = await self.extract_video_features(frames, fps)
            
            # Enhance metadata
            enhanced_metadata = await self.enhance_video_metadata(features, metadata)
            
            # Generate fingerprint
            fingerprint = await self.generate_video_fingerprint(frames)
            
            return {
                "features": features,
                "metadata": enhanced_metadata,
                "fingerprint": fingerprint,
                "quality_metrics": await self.calculate_video_quality(frames)
            }
            
        except Exception as e:
            logger.error(f"Video processing error: {e}")
            raise
    
    async def load_video(self, content_data: bytes) -> Tuple[List[np.ndarray], float, float]:
        """Load video from bytes"""        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(content_data)
            temp_path = temp_file.name
        
        try:
            cap = cv2.VideoCapture(temp_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            frames = []
            frame_skip = max(1, int(fps))  # Sample 1 frame per second
            
            for i in range(0, frame_count, frame_skip):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                
                if len(frames) >= 30:  # Limit to 30 frames for processing
                    break
            
            cap.release()
            return frames, fps, duration
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    async def extract_video_features(self, frames: List[np.ndarray], fps: float) -> Dict[str, Any]:
        """Extract comprehensive video features"""        features = {}
        
        if not frames:
            return features
        
        # Basic video properties
        height, width = frames[0].shape[:2]
        features['width'] = width
        features['height'] = height
        features['fps'] = fps
        features['frame_count'] = len(frames)
        
        # Color analysis
        color_features = await self.analyze_colors(frames)
        features.update(color_features)
        
        # Motion analysis
        motion_features = await self.analyze_motion(frames)
        features.update(motion_features)
        
        # Scene detection
        scene_features = await self.detect_scenes(frames)
        features.update(scene_features)
        
        return features
    
    async def analyze_colors(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze color characteristics"""        color_features = {}
        
        all_pixels = []
        for frame in frames[:10]:  # Analyze first 10 frames
            pixels = frame.reshape(-1, 3)
            all_pixels.append(pixels)
        
        if all_pixels:
            combined_pixels = np.concatenate(all_pixels, axis=0)
            
            # Color statistics
            color_features['mean_rgb'] = np.mean(combined_pixels, axis=0).tolist()
            color_features['std_rgb'] = np.std(combined_pixels, axis=0).tolist()
            
            # Dominant colors (simplified)
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=5, random_state=42)
            kmeans.fit(combined_pixels[::100])  # Sample for efficiency
            color_features['dominant_colors'] = kmeans.cluster_centers_.tolist()
        
        return color_features
    
    async def analyze_motion(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze motion characteristics"""        motion_features = {}
        
        if len(frames) < 2:
            return motion_features
        
        motion_magnitudes = []
        for i in range(1, len(frames)):
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
            
            # Calculate motion magnitude
            if flow[0] is not None:
                motion_magnitude = np.mean(np.sqrt(flow[0][:, :, 0]**2 + flow[0][:, :, 1]**2))
                motion_magnitudes.append(motion_magnitude)
        
        if motion_magnitudes:
            motion_features['average_motion'] = float(np.mean(motion_magnitudes))
            motion_features['motion_variance'] = float(np.var(motion_magnitudes))
        
        return motion_features
    
    async def detect_scenes(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Detect scene changes"""        scene_features = {}
        
        if len(frames) < 2:
            return scene_features
        
        scene_changes = []
        for i in range(1, len(frames)):
            # Simple scene change detection using histogram comparison
            hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            if correlation < 0.7:  # Threshold for scene change
                scene_changes.append(i)
        
        scene_features['scene_changes'] = scene_changes
        scene_features['scene_count'] = len(scene_changes) + 1
        
        return scene_features
    
    async def enhance_video_metadata(self, features: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance video metadata"""        enhanced = metadata.copy()
        
        enhanced.update({
            'video_width': features.get('width'),
            'video_height': features.get('height'),
            'video_fps': features.get('fps'),
            'estimated_scene_count': features.get('scene_count'),
            'motion_level': 'high' if features.get('average_motion', 0) > 10 else 'low',
            'video_fingerprint_type': 'perceptual_hash'
        })
        
        return enhanced
    
    async def generate_video_fingerprint(self, frames: List[np.ndarray]) -> str:
        """Generate video fingerprint"""        if not frames:
            return ""
        
        # Use perceptual hashing for key frames
        fingerprints = []
        for frame in frames[::5]:  # Every 5th frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (8, 8))
            avg = resized.mean()
            binary = (resized > avg).flatten()
            fingerprint = ''.join(['1' if x else '0' for x in binary])
            fingerprints.append(fingerprint)
        
        # Combine fingerprints
        combined = ''.join(fingerprints)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def calculate_video_quality(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Calculate video quality metrics"""        metrics = {}
        
        if not frames:
            return metrics
        
        # Sharpness (Laplacian variance)
        sharpness_scores = []
        for frame in frames[:10]:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_scores.append(laplacian_var)
        
        metrics['average_sharpness'] = float(np.mean(sharpness_scores))
        
        # Brightness analysis
        brightness_scores = []
        for frame in frames[:10]:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness_scores.append(np.mean(gray))
        
        metrics['average_brightness'] = float(np.mean(brightness_scores))
        metrics['brightness_variance'] = float(np.var(brightness_scores))
        
        # Overall quality score
        normalized_sharpness = min(1.0, metrics['average_sharpness'] / 1000)
        normalized_brightness = 1.0 - abs(metrics['average_brightness'] - 128) / 128
        quality_score = (normalized_sharpness + normalized_brightness) / 2
        metrics['quality_score'] = float(quality_score)
        
        return metrics


class ImageProcessor:
    """Advanced image content processor"""    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
    async def process(self, content_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process image content"""        try:
            # Load image
            image = await self.load_image(content_data)
            
            # Extract features
            features = await self.extract_image_features(image)
            
            # Enhance metadata
            enhanced_metadata = await self.enhance_image_metadata(features, metadata)
            
            # Generate fingerprint
            fingerprint = await self.generate_image_fingerprint(image)
            
            return {
                "features": features,
                "metadata": enhanced_metadata,
                "fingerprint": fingerprint,
                "quality_metrics": await self.calculate_image_quality(image)
            }
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise
    
    async def load_image(self, content_data: bytes) -> Image.Image:
        """Load image from bytes"""        from io import BytesIO
        return Image.open(BytesIO(content_data))
    
    async def extract_image_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract comprehensive image features"""        features = {}
        
        # Basic properties
        features['width'], features['height'] = image.size
        features['mode'] = image.mode
        features['format'] = image.format
        
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        # Color analysis
        if len(img_array.shape) == 3:  # Color image
            features['color_channels'] = img_array.shape[2]
            features['mean_rgb'] = np.mean(img_array, axis=(0, 1)).tolist()
            features['std_rgb'] = np.std(img_array, axis=(0, 1)).tolist()
        else:  # Grayscale
            features['color_channels'] = 1
            features['mean_brightness'] = float(np.mean(img_array))
            features['std_brightness'] = float(np.std(img_array))
        
        # Texture analysis
        texture_features = await self.analyze_texture(img_array)
        features.update(texture_features)
        
        # Edge detection
        edge_features = await self.analyze_edges(img_array)
        features.update(edge_features)
        
        return features
    
    async def analyze_texture(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze image texture characteristics"""        texture_features = {}
        
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Local Binary Pattern (simplified)
        from skimage import feature
        lbp = feature.local_binary_pattern(gray, 8, 1, method='uniform')
        texture_features['lbp_histogram'] = np.histogram(lbp, bins=10)[0].tolist()
        
        # Contrast
        texture_features['contrast'] = float(np.std(gray))
        
        return texture_features
    
    async def analyze_edges(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze edge characteristics"""        edge_features = {}
        
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        edge_features['edge_density'] = float(edge_density)
        
        return edge_features
    
    async def enhance_image_metadata(self, features: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance image metadata"""        enhanced = metadata.copy()
        
        enhanced.update({
            'image_width': features.get('width'),
            'image_height': features.get('height'),
            'image_mode': features.get('mode'),
            'image_format': features.get('format'),
            'color_channels': features.get('color_channels'),
            'edge_density': features.get('edge_density'),
            'image_fingerprint_type': 'perceptual_hash'
        })
        
        return enhanced
    
    async def generate_image_fingerprint(self, image: Image.Image) -> str:
        """Generate image fingerprint using perceptual hash"""        import imagehash
        
        # Generate multiple hash types for robustness
        phash = str(imagehash.phash(image))
        dhash = str(imagehash.dhash(image))
        whash = str(imagehash.whash(image))
        
        # Combine hashes
        combined = f"{phash}:{dhash}:{whash}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def calculate_image_quality(self, image: Image.Image) -> Dict[str, float]:
        """Calculate image quality metrics"""        metrics = {}
        
        img_array = np.array(image)
        
        # Sharpness (Laplacian variance)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics['sharpness'] = float(laplacian_var)
        
        # Noise estimation (simplified)
        noise_level = np.std(gray - cv2.GaussianBlur(gray, (5, 5), 0))
        metrics['noise_level'] = float(noise_level)
        
        # Overall quality score
        normalized_sharpness = min(1.0, laplacian_var / 1000)
        normalized_noise = max(0.0, 1.0 - noise_level / 50)
        quality_score = (normalized_sharpness + normalized_noise) / 2
        metrics['quality_score'] = float(quality_score)
        
        return metrics


class TextProcessor:
    """Advanced text content processor"""    
    def __init__(self):
        self.supported_formats = ['.txt', '.md', '.html', '.xml', '.json']
        
        # Initialize NLP models
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.summarizer = pipeline("summarization")
        
    async def process(self, content_data: Union[str, bytes], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process text content"""        try:
            # Convert to string if bytes
            if isinstance(content_data, bytes):
                text = content_data.decode('utf-8', errors='ignore')
            else:
                text = content_data
            
            # Extract features
            features = await self.extract_text_features(text)
            
            # Enhance metadata
            enhanced_metadata = await self.enhance_text_metadata(features, metadata)
            
            # Generate fingerprint
            fingerprint = await self.generate_text_fingerprint(text)
            
            return {
                "features": features,
                "metadata": enhanced_metadata,
                "fingerprint": fingerprint,
                "quality_metrics": await self.calculate_text_quality(text)
            }
            
        except Exception as e:
            logger.error(f"Text processing error: {e}")
            raise
    
    async def extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive text features"""        features = {}
        
        # Basic statistics
        features['character_count'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = text.count('.') + text.count('!') + text.count('?')
        features['paragraph_count'] = text.count('\n\n') + 1
        
        # Language detection
        language = await self.detect_language(text)
        features['detected_language'] = language
        
        # Sentiment analysis
        sentiment = await self.analyze_sentiment(text)
        features['sentiment'] = sentiment
        
        # Keywords extraction
        keywords = await self.extract_keywords(text)
        features['keywords'] = keywords
        
        # Readability metrics
        readability = await self.calculate_readability(text)
        features['readability'] = readability
        
        return features
    
    async def detect_language(self, text: str) -> str:
        """Detect text language"""        try:
            from langdetect import detect
            return detect(text)
        except:
            return "unknown"
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment"""        try:
            # Truncate text for efficiency
            truncated_text = text[:512]
            result = self.sentiment_analyzer(truncated_text)
            return result[0] if result else {"label": "NEUTRAL", "score": 0.5}
        except:
            return {"label": "NEUTRAL", "score": 0.5}
    
    async def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
            
            # Simple keyword extraction using TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=20,
                stop_words=list(ENGLISH_STOP_WORDS),
                ngram_range=(1, 2)
            )
            
            # Split text into sentences for TF-IDF
            sentences = text.split('.')
            if len(sentences) < 2:
                return []
            
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top keywords
            scores = tfidf_matrix.sum(axis=0).A1
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [kw[0] for kw in keyword_scores[:10]]
            
        except:
            return []
    
    async def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics"""        readability = {}
        
        words = text.split()
        sentences = text.count('.') + text.count('!') + text.count('?')
        
        if sentences == 0 or len(words) == 0:
            return readability
        
        # Average words per sentence
        avg_words_per_sentence = len(words) / sentences
        readability['avg_words_per_sentence'] = avg_words_per_sentence
        
        # Average syllables per word (simplified)
        total_syllables = sum(self.count_syllables(word) for word in words)
        avg_syllables_per_word = total_syllables / len(words)
        readability['avg_syllables_per_word'] = avg_syllables_per_word
        
        # Flesch Reading Ease (simplified)
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        readability['flesch_reading_ease'] = max(0, min(100, flesch_score))
        
        return readability
    
    def count_syllables(self, word: str) -> int:
        """Simple syllable counting"""        vowels = 'aeiouy'
        count = 0
        previous_was_vowel = False
        
        for char in word.lower():
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent e
        if word.lower().endswith('e'):
            count -= 1
        
        return max(1, count)
    
    async def enhance_text_metadata(self, features: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance text metadata"""        enhanced = metadata.copy()
        
        enhanced.update({
            'text_word_count': features.get('word_count'),
            'text_character_count': features.get('character_count'),
            'detected_language': features.get('detected_language'),
            'sentiment_label': features.get('sentiment', {}).get('label'),
            'sentiment_score': features.get('sentiment', {}).get('score'),
            'readability_score': features.get('readability', {}).get('flesch_reading_ease'),
            'text_fingerprint_type': 'semantic_hash'
        })
        
        return enhanced
    
    async def generate_text_fingerprint(self, text: str) -> str:
        """Generate text fingerprint using semantic analysis"""        # Simple semantic hash based on word frequencies
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Create fingerprint from most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_words = [word for word, freq in sorted_words[:50]]
        fingerprint_string = ''.join(sorted(top_words))
        
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    async def calculate_text_quality(self, text: str) -> Dict[str, float]:
        """Calculate text quality metrics"""        metrics = {}
        
        # Basic completeness check
        word_count = len(text.split())
        char_count = len(text)
        
        # Length quality (optimal range)
        if word_count < 10:
            length_quality = word_count / 10
        elif word_count > 10000:
            length_quality = max(0.1, 1.0 - (word_count - 10000) / 50000)
        else:
            length_quality = 1.0
        
        metrics['length_quality'] = length_quality
        
        # Character diversity
        unique_chars = len(set(text.lower()))
        char_diversity = min(1.0, unique_chars / 26)  # Normalized by alphabet size
        metrics['character_diversity'] = char_diversity
        
        # Sentence structure quality
        sentences = text.count('.') + text.count('!') + text.count('?')
        if sentences > 0:
            avg_sentence_length = word_count / sentences
            sentence_quality = 1.0 if 10 <= avg_sentence_length <= 25 else 0.5
        else:
            sentence_quality = 0.1
        
        metrics['sentence_structure_quality'] = sentence_quality
        
        # Overall quality score
        overall_quality = (length_quality + char_diversity + sentence_quality) / 3
        metrics['quality_score'] = overall_quality
        
        return metrics


class ContentProcessingMiddleware:
    """Main content processing middleware orchestrator"""    
    def __init__(self):
        self.cache = CacheManager()
        self.fingerprint_engine = UniversalFingerprintEngine()
        
        # Initialize processors
        self.processors = {
            ContentType.AUDIO: AudioProcessor(),
            ContentType.VIDEO: VideoProcessor(),
            ContentType.IMAGE: ImageProcessor(),
            ContentType.TEXT: TextProcessor()
        }
        
    async def process_content(self, request: ContentProcessingRequest) -> ProcessingResult:
        """Main content processing method"""        start_time = time.time()
        stages_completed = []
        
        try:
            # Stage 1: Validation
            await self.validate_content(request)
            stages_completed.append(ProcessingStage.VALIDATION)
            
            # Stage 2: Content Type Detection
            detected_type = await self.detect_content_type(request)
            if detected_type != request.content_type:
                logger.warning(f"Content type mismatch: expected {request.content_type}, detected {detected_type}")
            stages_completed.append(ProcessingStage.EXTRACTION)
            
            # Stage 3: Processing
            processor = self.processors.get(request.content_type)
            if not processor:
                raise ValueError(f"No processor available for content type: {request.content_type}")
            
            processing_result = await processor.process(request.content_data, request.metadata)
            stages_completed.append(ProcessingStage.TRANSFORMATION)
            
            # Stage 4: Enrichment
            enriched_metadata = await self.enrich_metadata(processing_result, request)
            stages_completed.append(ProcessingStage.ENRICHMENT)
            
            # Stage 5: Fingerprinting
            enhanced_fingerprint = await self.enhance_fingerprint(processing_result, request)
            stages_completed.append(ProcessingStage.FINGERPRINTING)
            
            # Stage 6: Optimization
            optimized_result = await self.optimize_result(processing_result, request)
            stages_completed.append(ProcessingStage.OPTIMIZATION)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                content_id=request.content_id,
                status=ProcessingStatus.COMPLETED,
                processed_content=optimized_result,
                fingerprint=enhanced_fingerprint,
                metadata=enriched_metadata,
                quality_metrics=processing_result.get('quality_metrics', {}),
                processing_time=processing_time,
                stages_completed=stages_completed
            )
            
        except Exception as e:
            logger.error(f"Content processing failed for {request.content_id}: {e}")
            
            return ProcessingResult(
                content_id=request.content_id,
                status=ProcessingStatus.FAILED,
                processing_time=time.time() - start_time,
                stages_completed=stages_completed,
                error=str(e)
            )
    
    async def validate_content(self, request: ContentProcessingRequest):
        """Validate content before processing"""        # Check content size
        if isinstance(request.content_data, bytes):
            size = len(request.content_data)
        elif isinstance(request.content_data, str):
            size = len(request.content_data.encode())
        else:
            size = len(str(request.content_data))
        
        max_sizes = {
            ContentType.AUDIO: 100 * 1024 * 1024,  # 100MB
            ContentType.VIDEO: 500 * 1024 * 1024,  # 500MB
            ContentType.IMAGE: 50 * 1024 * 1024,   # 50MB
            ContentType.TEXT: 10 * 1024 * 1024,    # 10MB
            ContentType.DOCUMENT: 100 * 1024 * 1024  # 100MB
        }
        
        max_size = max_sizes.get(request.content_type, 10 * 1024 * 1024)
        if size > max_size:
            raise ValueError(f"Content too large: {size} bytes, max: {max_size} bytes")
        
        # Validate content type
        if request.content_type not in [ContentType.AUDIO, ContentType.VIDEO, 
                                       ContentType.IMAGE, ContentType.TEXT]:
            raise ValueError(f"Unsupported content type: {request.content_type}")
    
    async def detect_content_type(self, request: ContentProcessingRequest) -> ContentType:
        """Detect actual content type"""        if isinstance(request.content_data, bytes):
            # Use python-magic for MIME type detection
            mime_type = magic.from_buffer(request.content_data, mime=True)
            
            if mime_type.startswith('audio/'):
                return ContentType.AUDIO
            elif mime_type.startswith('video/'):
                return ContentType.VIDEO
            elif mime_type.startswith('image/'):
                return ContentType.IMAGE
            elif mime_type.startswith('text/'):
                return ContentType.TEXT
        
        # Fallback to provided type
        return request.content_type
    
    async def enrich_metadata(self, processing_result: Dict[str, Any], 
                            request: ContentProcessingRequest) -> Dict[str, Any]:
        """Enrich metadata with additional information"""        enriched = processing_result.get('metadata', {}).copy()
        
        # Add processing metadata
        enriched.update({
            'processing_timestamp': datetime.utcnow().isoformat(),
            'processing_version': '1.0',
            'content_id': request.content_id,
            'original_content_type': request.content_type.value,
            'processing_options': request.processing_options
        })
        
        return enriched
    
    async def enhance_fingerprint(self, processing_result: Dict[str, Any], 
                                request: ContentProcessingRequest) -> str:
        """Enhance fingerprint with additional security measures"""        original_fingerprint = processing_result.get('fingerprint', '')
        
        # Add content ID and timestamp for uniqueness
        enhanced_data = {
            'original_fingerprint': original_fingerprint,
            'content_id': request.content_id,
            'timestamp': datetime.utcnow().isoformat(),
            'content_type': request.content_type.value
        }
        
        enhanced_string = json.dumps(enhanced_data, sort_keys=True)
        return hashlib.sha256(enhanced_string.encode()).hexdigest()
    
    async def optimize_result(self, processing_result: Dict[str, Any], 
                            request: ContentProcessingRequest) -> Dict[str, Any]:
        """Optimize processing result for storage and transmission"""        optimized = processing_result.copy()
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        optimized = convert_numpy(optimized)
        
        # Compress large feature arrays if needed
        features = optimized.get('features', {})
        for key, value in features.items():
            if isinstance(value, list) and len(value) > 1000:
                # Sample large arrays
                sampled = value[::len(value)//100] if len(value) > 100 else value
                features[f'{key}_sampled'] = sampled
                del features[key]
        
        return optimized


# Factory function for dependency injection
def get_content_processing_middleware() -> ContentProcessingMiddleware:
    """Get content processing middleware instance"""    return ContentProcessingMiddleware()


# Utility functions
async def process_content(content_data: Union[str, bytes], content_type: ContentType, 
                         content_id: str = None, metadata: Dict[str, Any] = None) -> ProcessingResult:
    """Convenience function for content processing"""    if content_id is None:
        content_id = hashlib.md5(str(content_data).encode()).hexdigest()
    
    if metadata is None:
        metadata = {}
    
    middleware = get_content_processing_middleware()
    request = ContentProcessingRequest(
        content_id=content_id,
        content_type=content_type,
        content_data=content_data,
        metadata=metadata
    )
    
    return await middleware.process_content(request)
