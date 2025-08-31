"""🔍 Content Analyzer - IA Influencer Agent Platform Enterprise
============================================================
Module: backend/data_management/storage/content_analyzer.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

Advanced content analysis with AI-powered insights
for influencer content optimization and protection.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Sécurité: Fahed Mlaiel
- Microservices: Fahed Mlaiel
- Audio Engineer: Fahed Mlaiel
- DevOps: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel
"""
from typing import Dict, List, Optional, Any, Union, Tuple, Set
import logging
import asyncio
import hashlib
import io
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ExifTags
import librosa
import mutagen
from mutagen.id3 import ID3NoHeaderError
import textstat
import langdetect
from collections import Counter
import tempfile
import subprocess
import json

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    UNKNOWN = "unknown"

class AnalysisLevel(Enum):
    """Analysis depth levels"""    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    AI_ENHANCED = "ai_enhanced"

class QualityLevel(Enum):
    """Content quality levels"""    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

class ContentRisk(Enum):
    """Content risk categories"""    SAFE = "safe"
    MODERATE = "moderate"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"
    FORBIDDEN = "forbidden"

@dataclass
class ContentFeatures:
    """Content feature extraction results"""    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    brightness: float = 0.0
    contrast: float = 0.0
    sharpness: float = 0.0
    noise_level: float = 0.0
    edge_density: float = 0.0
    texture_complexity: float = 0.0
    composition_score: float = 0.0

@dataclass
class AudioFeatures:
    """Audio feature extraction results"""    duration: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    bitrate: int = 0
    loudness: float = 0.0
    dynamic_range: float = 0.0
    spectral_centroid: float = 0.0
    spectral_rolloff: float = 0.0
    zero_crossing_rate: float = 0.0
    mfcc_features: List[float] = field(default_factory=list)
    tempo: float = 0.0
    key: str = ""
    mode: str = ""
    silence_ratio: float = 0.0

@dataclass
class TextFeatures:
    """Text feature extraction results"""    word_count: int = 0
    character_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    language: str = ""
    keyword_density: Dict[str, float] = field(default_factory=dict)
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    topics: List[str] = field(default_factory=list)
    named_entities: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class ContentAnalysis:
    """Complete content analysis results"""    content_id: str
    content_type: ContentType
    file_path: str
    file_size: int
    
    # Basic analysis
    mime_type: str = ""
    encoding: str = ""
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    
    # Quality assessment
    quality_level: QualityLevel = QualityLevel.AVERAGE
    quality_score: float = 0.0
    quality_issues: List[str] = field(default_factory=list)
    
    # Risk assessment
    risk_level: ContentRisk = ContentRisk.SAFE
    risk_score: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    
    # Content features
    content_features: Optional[ContentFeatures] = None
    audio_features: Optional[AudioFeatures] = None
    text_features: Optional[TextFeatures] = None
    
    # AI analysis
    ai_tags: List[str] = field(default_factory=list)
    ai_description: str = ""
    ai_confidence: float = 0.0
    similarity_hash: str = ""
    
    # Business insights
    engagement_potential: float = 0.0
    monetization_potential: float = 0.0
    virality_score: float = 0.0
    brand_safety_score: float = 0.0
    
    # Technical metadata
    technical_metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    analysis_level: AnalysisLevel = AnalysisLevel.STANDARD
    processing_time: float = 0.0

class ImageAnalyzer:
    """Advanced image content analysis"""    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
    
    async def analyze_image(self, file_path: str, analysis_level: AnalysisLevel = AnalysisLevel.STANDARD) -> ContentFeatures:
        """Analyze image content and extract features"""        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                # Try with PIL for unsupported formats
                pil_image = Image.open(file_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            features = ContentFeatures()
            
            # Basic features
            features.brightness = self._calculate_brightness(image)
            features.contrast = self._calculate_contrast(image)
            features.sharpness = self._calculate_sharpness(image)
            features.noise_level = self._calculate_noise_level(image)
            
            if analysis_level in [AnalysisLevel.DETAILED, AnalysisLevel.AI_ENHANCED]:
                # Advanced features
                features.dominant_colors = self._extract_dominant_colors(image)
                features.edge_density = self._calculate_edge_density(image)
                features.texture_complexity = self._calculate_texture_complexity(image)
                features.composition_score = self._analyze_composition(image)
            
            return features
            
        except Exception as e:
            logger.error(f"Image analysis error for {file_path}: {str(e)}")
            return ContentFeatures()
    
    def _calculate_brightness(self, image: np.ndarray) -> float:
        """Calculate image brightness"""        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return float(np.mean(gray) / 255.0)
    
    def _calculate_contrast(self, image: np.ndarray) -> float:
        """Calculate image contrast using standard deviation"""        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return float(np.std(gray) / 255.0)
    
    def _calculate_sharpness(self, image: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(np.var(laplacian) / 10000.0)  # Normalized
    
    def _calculate_noise_level(self, image: np.ndarray) -> float:
        """Estimate noise level in image"""        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use Gaussian blur difference to estimate noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = np.abs(gray.astype(float) - blurred.astype(float))
        
        return float(np.mean(noise) / 255.0)
    
    def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using K-means clustering"""        try:
            # Reshape image data
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # Apply K-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert to integers and return
            centers = np.uint8(centers)
            dominant_colors = [tuple(map(int, color)) for color in centers]
            
            return dominant_colors
            
        except Exception as e:
            logger.error(f"Color extraction error: {str(e)}")
            return []
    
    def _calculate_edge_density(self, image: np.ndarray) -> float:
        """Calculate edge density using Canny edge detection"""        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.shape[0] * edges.shape[1]
        
        return float(edge_pixels / total_pixels)
    
    def _calculate_texture_complexity(self, image: np.ndarray) -> float:
        """Calculate texture complexity using Local Binary Pattern"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Simplified texture analysis using variance of local patches
            h, w = gray.shape
            patch_size = 8
            complexities = []
            
            for i in range(0, h - patch_size, patch_size):
                for j in range(0, w - patch_size, patch_size):
                    patch = gray[i:i+patch_size, j:j+patch_size]
                    complexities.append(np.var(patch))
            
            return float(np.mean(complexities) / 10000.0)  # Normalized
            
        except Exception as e:
            logger.error(f"Texture analysis error: {str(e)}")
            return 0.0
    
    def _analyze_composition(self, image: np.ndarray) -> float:
        """Analyze image composition using rule of thirds and other principles"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # Rule of thirds analysis
            third_h, third_w = h // 3, w // 3
            
            # Check for interest points near rule of thirds intersections
            interest_points = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
            
            if interest_points is None:
                return 0.5
            
            composition_score = 0.0
            rule_of_thirds_points = [
                (third_w, third_h), (2 * third_w, third_h),
                (third_w, 2 * third_h), (2 * third_w, 2 * third_h)
            ]
            
            # Score based on proximity to rule of thirds points
            for point in interest_points:
                x, y = point.ravel()
                min_distance = min([
                    np.sqrt((x - rx)**2 + (y - ry)**2)
                    for rx, ry in rule_of_thirds_points
                ])
                
                # Closer to rule of thirds points = higher score
                score_contribution = max(0, 1 - (min_distance / (w * 0.1)))
                composition_score += score_contribution
            
            # Normalize by number of points
            composition_score = composition_score / len(interest_points) if len(interest_points) > 0 else 0.5
            
            return min(1.0, composition_score)
            
        except Exception as e:
            logger.error(f"Composition analysis error: {str(e)}")
            return 0.5

class AudioAnalyzer:
    """Advanced audio content analysis"""    
    def __init__(self):
        self.supported_formats = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    
    async def analyze_audio(self, file_path: str, analysis_level: AnalysisLevel = AnalysisLevel.STANDARD) -> AudioFeatures:
        """Analyze audio content and extract features"""        try:
            features = AudioFeatures()
            
            # Load audio metadata
            audio_file = mutagen.File(file_path)
            if audio_file:
                features.duration = audio_file.info.length
                features.bitrate = getattr(audio_file.info, 'bitrate', 0)
            
            # Load audio data with librosa
            y, sr = librosa.load(file_path, sr=None)
            features.sample_rate = sr
            features.channels = 1 if len(y.shape) == 1 else y.shape[0]
            
            # Basic features
            features.loudness = self._calculate_loudness(y)
            features.dynamic_range = self._calculate_dynamic_range(y)
            features.silence_ratio = self._calculate_silence_ratio(y)
            
            if analysis_level in [AnalysisLevel.DETAILED, AnalysisLevel.AI_ENHANCED]:
                # Advanced features
                features.spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
                features.spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
                features.zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(y)))
                
                # MFCC features
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                features.mfcc_features = [float(x) for x in np.mean(mfccs, axis=1)]
                
                # Tempo and key detection
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                features.tempo = float(tempo)
                
                # Simplified key detection (would use more advanced methods in production)
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                key_profiles = self._get_key_profiles()
                correlations = [np.corrcoef(np.mean(chroma, axis=1), profile)[0, 1] for profile in key_profiles]
                key_index = np.argmax(correlations)
                features.key = self._index_to_key(key_index)
            
            return features
            
        except Exception as e:
            logger.error(f"Audio analysis error for {file_path}: {str(e)}")
            return AudioFeatures()
    
    def _calculate_loudness(self, y: np.ndarray) -> float:
        """Calculate audio loudness (RMS)"""        rms = librosa.feature.rms(y=y)
        return float(np.mean(rms))
    
    def _calculate_dynamic_range(self, y: np.ndarray) -> float:
        """Calculate dynamic range"""        return float(np.max(y) - np.min(y))
    
    def _calculate_silence_ratio(self, y: np.ndarray, threshold: float = 0.01) -> float:
        """Calculate ratio of silence in audio"""        silent_samples = np.sum(np.abs(y) < threshold)
        return float(silent_samples / len(y))
    
    def _get_key_profiles(self) -> List[np.ndarray]:
        """Get major key profiles for key detection"""        # Simplified key profiles (Krumhansl-Schmuckler)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        
        # Generate all 12 major key profiles
        profiles = []
        for i in range(12):
            profiles.append(np.roll(major_profile, i))
        
        return profiles
    
    def _index_to_key(self, index: int) -> str:
        """Convert key index to key name"""        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return keys[index] + " Major"

class TextAnalyzer:
    """Advanced text content analysis"""    
    def __init__(self):
        self.supported_formats = {'.txt', '.md', '.json', '.xml', '.html'}
        self.stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        ])
    
    async def analyze_text(self, text: str, analysis_level: AnalysisLevel = AnalysisLevel.STANDARD) -> TextFeatures:
        """Analyze text content and extract features"""        try:
            features = TextFeatures()
            
            # Basic statistics
            features.word_count = len(text.split())
            features.character_count = len(text)
            features.sentence_count = len(re.split(r'[.!?]+', text))
            features.paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # Readability
            features.readability_score = textstat.flesch_reading_ease(text)
            
            # Language detection
            try:
                features.language = langdetect.detect(text)
            except:
                features.language = "unknown"
            
            if analysis_level in [AnalysisLevel.DETAILED, AnalysisLevel.AI_ENHANCED]:
                # Keyword analysis
                features.keyword_density = self._calculate_keyword_density(text)
                
                # Basic sentiment analysis (simplified)
                features.sentiment_score = self._analyze_sentiment(text)
                
                # Topic extraction (simplified)
                features.topics = self._extract_topics(text)
                
                # Named entity recognition (simplified)
                features.named_entities = self._extract_named_entities(text)
                
                # Emotion analysis (simplified)
                features.emotion_scores = self._analyze_emotions(text)
            
            return features
            
        except Exception as e:
            logger.error(f"Text analysis error: {str(e)}")
            return TextFeatures()
    
    def _calculate_keyword_density(self, text: str, top_n: int = 10) -> Dict[str, float]:
        """Calculate keyword density"""        words = re.findall(r'\b\w+\b', text.lower())
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        word_counts = Counter(words)
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        # Calculate density for top N words
        densities = {}
        for word, count in word_counts.most_common(top_n):
            densities[word] = count / total_words
        
        return densities
    
    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis using word lists"""        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
            'sad', 'angry', 'disappointed', 'frustrated', 'annoyed'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.0  # Neutral
        
        return (positive_count - negative_count) / total_sentiment_words
    
    def _extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """Extract topics using keyword frequency"""        # Simplified topic extraction
        words = re.findall(r'\b\w+\b', text.lower())
        words = [word for word in words if word not in self.stop_words and len(word) > 3]
        
        word_counts = Counter(words)
        topics = [word for word, _ in word_counts.most_common(max_topics)]
        
        return topics
    
    def _extract_named_entities(self, text: str) -> List[Dict[str, str]]:
        """Simple named entity recognition"""        entities = []
        
        # Simple patterns for basic entity types
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b',
            'hashtag': r'#\w+',
            'mention': r'@\w+'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append({
                    'text': match,
                    'type': entity_type,
                    'confidence': 0.8  # Simplified confidence
                })
        
        return entities
    
    def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Simple emotion analysis using word lists"""        emotion_words = {
            'joy': {'happy', 'joy', 'excited', 'thrilled', 'delighted', 'cheerful'},
            'anger': {'angry', 'furious', 'mad', 'irritated', 'annoyed', 'rage'},
            'sadness': {'sad', 'depressed', 'melancholy', 'grief', 'sorrow', 'crying'},
            'fear': {'afraid', 'scared', 'terrified', 'anxious', 'worried', 'nervous'},
            'surprise': {'surprised', 'amazed', 'astonished', 'shocked', 'stunned'},
            'disgust': {'disgusted', 'revolted', 'repulsed', 'sick', 'nauseous'}
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        emotion_scores = {}
        
        for emotion, emotion_set in emotion_words.items():
            count = sum(1 for word in words if word in emotion_set)
            emotion_scores[emotion] = count / len(words) if words else 0.0
        
        return emotion_scores

class ContentAnalyzer:
    """    Comprehensive content analysis system.
    
    Features:
    - Multi-format content analysis
    - AI-powered insights
    - Quality assessment
    - Risk evaluation
    - Business metrics calculation
    - Performance optimization
    - Content fingerprinting
    - Similarity detection
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content analyzer"""        self.config = config or {}
        
        # Specialized analyzers
        self.image_analyzer = ImageAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.text_analyzer = TextAnalyzer()
        
        # Content type detection
        self.mime_types = {
            # Images
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
            '.gif': 'image/gif', '.bmp': 'image/bmp', '.tiff': 'image/tiff',
            '.webp': 'image/webp',
            
            # Audio
            '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.flac': 'audio/flac',
            '.aac': 'audio/aac', '.ogg': 'audio/ogg', '.m4a': 'audio/mp4',
            
            # Video
            '.mp4': 'video/mp4', '.avi': 'video/avi', '.mov': 'video/quicktime',
            '.wmv': 'video/x-ms-wmv', '.flv': 'video/x-flv', '.webm': 'video/webm',
            
            # Text
            '.txt': 'text/plain', '.md': 'text/markdown', '.json': 'application/json',
            '.xml': 'application/xml', '.html': 'text/html', '.css': 'text/css',
            
            # Documents
            '.pdf': 'application/pdf', '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        # Quality assessment weights
        self.quality_weights = {
            'technical_quality': 0.4,
            'content_relevance': 0.3,
            'engagement_potential': 0.2,
            'brand_safety': 0.1
        }
        
        # Risk assessment factors
        self.risk_factors = {
            'explicit_content': 0.3,
            'copyright_risk': 0.25,
            'brand_risk': 0.2,
            'legal_risk': 0.15,
            'reputation_risk': 0.1
        }
        
        logger.info("ContentAnalyzer initialized")
    
    async def analyze_content(
        self,
        file_path: str,
        content_id: Optional[str] = None,
        analysis_level: AnalysisLevel = AnalysisLevel.STANDARD
    ) -> ContentAnalysis:
        """        Perform comprehensive content analysis.
        
        Args:
            file_path: Path to content file
            content_id: Unique content identifier
            analysis_level: Depth of analysis to perform
            
        Returns:
            ContentAnalysis: Complete analysis results
        """        start_time = datetime.now()
        
        if not content_id:
            content_id = hashlib.sha256(file_path.encode()).hexdigest()[:16]
        
        try:
            # Initialize analysis
            analysis = ContentAnalysis(
                content_id=content_id,
                content_type=self._detect_content_type(file_path),
                file_path=file_path,
                file_size=Path(file_path).stat().st_size,
                analysis_level=analysis_level
            )
            
            # Basic file analysis
            await self._analyze_file_basics(analysis)
            
            # Content-specific analysis
            if analysis.content_type == ContentType.IMAGE:
                analysis.content_features = await self.image_analyzer.analyze_image(file_path, analysis_level)
            elif analysis.content_type == ContentType.AUDIO:
                analysis.audio_features = await self.audio_analyzer.analyze_audio(file_path, analysis_level)
            elif analysis.content_type == ContentType.TEXT:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
                analysis.text_features = await self.text_analyzer.analyze_text(text_content, analysis_level)
            
            # Quality assessment
            await self._assess_quality(analysis)
            
            # Risk assessment
            await self._assess_risk(analysis)
            
            # Business metrics
            await self._calculate_business_metrics(analysis)
            
            # Content fingerprinting
            analysis.similarity_hash = await self._generate_similarity_hash(file_path, analysis.content_type)
            
            # AI-enhanced analysis
            if analysis_level == AnalysisLevel.AI_ENHANCED:
                await self._ai_enhanced_analysis(analysis)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            analysis.processing_time = processing_time
            
            logger.info(f"Content analysis completed for {content_id} in {processing_time:.2f}s")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Content analysis failed for {file_path}: {str(e)}")
            
            # Return minimal analysis on error
            analysis = ContentAnalysis(
                content_id=content_id,
                content_type=ContentType.UNKNOWN,
                file_path=file_path,
                file_size=0,
                analysis_level=analysis_level
            )
            analysis.processing_time = (datetime.now() - start_time).total_seconds()
            
            return analysis
    
    def _detect_content_type(self, file_path: str) -> ContentType:
        """Detect content type from file extension"""        extension = Path(file_path).suffix.lower()
        
        if extension in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}:
            return ContentType.IMAGE
        elif extension in {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}:
            return ContentType.AUDIO
        elif extension in {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'}:
            return ContentType.VIDEO
        elif extension in {'.txt', '.md', '.json', '.xml', '.html', '.css'}:
            return ContentType.TEXT
        elif extension in {'.pdf', '.doc', '.docx'}:
            return ContentType.DOCUMENT
        else:
            return ContentType.UNKNOWN
    
    async def _analyze_file_basics(self, analysis: ContentAnalysis):
        """Analyze basic file properties"""        try:
            file_path = Path(analysis.file_path)
            stat = file_path.stat()
            
            # File metadata
            analysis.mime_type = self.mime_types.get(file_path.suffix.lower(), 'application/octet-stream')
            analysis.creation_date = datetime.fromtimestamp(stat.st_ctime)
            analysis.modification_date = datetime.fromtimestamp(stat.st_mtime)
            
            # Technical metadata
            analysis.technical_metadata = {
                'file_extension': file_path.suffix.lower(),
                'file_name': file_path.name,
                'file_size_mb': analysis.file_size / (1024 * 1024),
                'creation_timestamp': stat.st_ctime,
                'modification_timestamp': stat.st_mtime
            }
            
        except Exception as e:
            logger.error(f"File basics analysis error: {str(e)}")
    
    async def _assess_quality(self, analysis: ContentAnalysis):
        """Assess content quality"""        try:
            quality_scores = {}
            
            # Technical quality
            technical_score = await self._assess_technical_quality(analysis)
            quality_scores['technical_quality'] = technical_score
            
            # Content relevance
            relevance_score = await self._assess_content_relevance(analysis)
            quality_scores['content_relevance'] = relevance_score
            
            # Engagement potential
            engagement_score = await self._assess_engagement_potential(analysis)
            quality_scores['engagement_potential'] = engagement_score
            
            # Brand safety
            brand_safety_score = await self._assess_brand_safety(analysis)
            quality_scores['brand_safety'] = brand_safety_score
            
            # Calculate weighted overall score
            overall_score = sum(
                score * self.quality_weights[metric]
                for metric, score in quality_scores.items()
            )
            
            analysis.quality_score = overall_score
            analysis.quality_level = self._score_to_quality_level(overall_score)
            
            # Identify quality issues
            analysis.quality_issues = self._identify_quality_issues(analysis, quality_scores)
            
        except Exception as e:
            logger.error(f"Quality assessment error: {str(e)}")
            analysis.quality_score = 0.5
            analysis.quality_level = QualityLevel.AVERAGE
    
    async def _assess_technical_quality(self, analysis: ContentAnalysis) -> float:
        """Assess technical quality of content"""        score = 0.5  # Default neutral score
        
        try:
            if analysis.content_type == ContentType.IMAGE and analysis.content_features:
                features = analysis.content_features
                
                # Image quality factors
                brightness_score = 1.0 - abs(features.brightness - 0.5) * 2  # Optimal around 0.5
                contrast_score = min(1.0, features.contrast * 2)  # Higher contrast is better
                sharpness_score = min(1.0, features.sharpness)
                noise_score = 1.0 - features.noise_level  # Lower noise is better
                
                score = (brightness_score + contrast_score + sharpness_score + noise_score) / 4
                
            elif analysis.content_type == ContentType.AUDIO and analysis.audio_features:
                features = analysis.audio_features
                
                # Audio quality factors
                bitrate_score = min(1.0, features.bitrate / 320.0) if features.bitrate > 0 else 0.5
                dynamic_range_score = min(1.0, features.dynamic_range / 2.0)
                silence_score = 1.0 - features.silence_ratio  # Less silence is better
                
                score = (bitrate_score + dynamic_range_score + silence_score) / 3
                
            elif analysis.content_type == ContentType.TEXT and analysis.text_features:
                features = analysis.text_features
                
                # Text quality factors
                length_score = min(1.0, features.word_count / 1000.0)  # Longer is generally better
                readability_score = min(1.0, features.readability_score / 100.0)
                
                score = (length_score + readability_score) / 2
            
        except Exception as e:
            logger.error(f"Technical quality assessment error: {str(e)}")
        
        return max(0.0, min(1.0, score))
    
    async def _assess_content_relevance(self, analysis: ContentAnalysis) -> float:
        """Assess content relevance for influencer marketing"""        score = 0.5  # Default neutral score
        
        try:
            # Content type relevance
            type_scores = {
                ContentType.IMAGE: 0.9,  # Highly relevant for social media
                ContentType.VIDEO: 1.0,  # Most relevant
                ContentType.AUDIO: 0.7,  # Relevant for podcasts
                ContentType.TEXT: 0.6,   # Moderately relevant
                ContentType.DOCUMENT: 0.3,  # Less relevant
                ContentType.UNKNOWN: 0.1
            }
            
            score = type_scores.get(analysis.content_type, 0.5)
            
            # Adjust based on content features
            if analysis.content_type == ContentType.TEXT and analysis.text_features:
                features = analysis.text_features
                
                # Social media relevant keywords
                social_keywords = {'instagram', 'facebook', 'twitter', 'tiktok', 'youtube', 'influencer'}
                keyword_relevance = sum(
                    features.keyword_density.get(keyword, 0)
                    for keyword in social_keywords
                )
                
                score += keyword_relevance * 0.2  # Boost for social media relevance
            
        except Exception as e:
            logger.error(f"Content relevance assessment error: {str(e)}")
        
        return max(0.0, min(1.0, score))
    
    async def _assess_engagement_potential(self, analysis: ContentAnalysis) -> float:
        """Assess potential for user engagement"""        score = 0.5  # Default neutral score
        
        try:
            if analysis.content_type == ContentType.IMAGE and analysis.content_features:
                features = analysis.content_features
                
                # Visual appeal factors
                composition_score = features.composition_score
                color_diversity = len(features.dominant_colors) / 5.0  # Normalized
                contrast_score = min(1.0, features.contrast * 2)
                
                score = (composition_score + color_diversity + contrast_score) / 3
                
            elif analysis.content_type == ContentType.TEXT and analysis.text_features:
                features = analysis.text_features
                
                # Engagement factors for text
                emotion_intensity = sum(features.emotion_scores.values())
                readability_factor = 1.0 - abs(features.readability_score - 60) / 100.0  # Optimal around 60
                
                score = (emotion_intensity + readability_factor) / 2
                
            elif analysis.content_type == ContentType.AUDIO and analysis.audio_features:
                features = analysis.audio_features
                
                # Audio engagement factors
                tempo_engagement = 1.0 if 120 <= features.tempo <= 140 else 0.7  # Optimal tempo range
                dynamic_score = min(1.0, features.dynamic_range)
                
                score = (tempo_engagement + dynamic_score) / 2
            
        except Exception as e:
            logger.error(f"Engagement assessment error: {str(e)}")
        
        return max(0.0, min(1.0, score))
    
    async def _assess_brand_safety(self, analysis: ContentAnalysis) -> float:
        """Assess brand safety score"""        score = 0.8  # Default safe score
        
        try:
            # File size check (extremely large files might be suspicious)
            if analysis.file_size > 100 * 1024 * 1024:  # 100MB
                score -= 0.1
            
            # Content type safety
            if analysis.content_type == ContentType.UNKNOWN:
                score -= 0.3
            
            # Text content safety
            if analysis.content_type == ContentType.TEXT and analysis.text_features:
                features = analysis.text_features
                
                # Check for potentially problematic content
                risky_keywords = {
                    'violence', 'hate', 'discrimination', 'illegal', 'drugs',
                    'gambling', 'adult', 'explicit', 'controversial'
                }
                
                risk_density = sum(
                    features.keyword_density.get(keyword, 0)
                    for keyword in risky_keywords
                )
                
                score -= risk_density * 2  # Reduce score based on risky content
                
                # Extremely negative sentiment is risky
                if features.sentiment_score < -0.7:
                    score -= 0.2
            
        except Exception as e:
            logger.error(f"Brand safety assessment error: {str(e)}")
        
        return max(0.0, min(1.0, score))
    
    def _score_to_quality_level(self, score: float) -> QualityLevel:
        """Convert quality score to quality level"""        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.7:
            return QualityLevel.GOOD
        elif score >= 0.5:
            return QualityLevel.AVERAGE
        elif score >= 0.3:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _identify_quality_issues(self, analysis: ContentAnalysis, quality_scores: Dict[str, float]) -> List[str]:
        """Identify specific quality issues"""        issues = []
        
        # Check each quality metric
        if quality_scores.get('technical_quality', 0.5) < 0.5:
            issues.append("Low technical quality detected")
        
        if quality_scores.get('content_relevance', 0.5) < 0.4:
            issues.append("Content may not be relevant for influencer marketing")
        
        if quality_scores.get('engagement_potential', 0.5) < 0.4:
            issues.append("Low engagement potential")
        
        if quality_scores.get('brand_safety', 0.8) < 0.7:
            issues.append("Potential brand safety concerns")
        
        # Content-specific issues
        if analysis.content_type == ContentType.IMAGE and analysis.content_features:
            features = analysis.content_features
            
            if features.brightness < 0.2:
                issues.append("Image is too dark")
            elif features.brightness > 0.8:
                issues.append("Image is too bright")
            
            if features.contrast < 0.2:
                issues.append("Low contrast")
            
            if features.noise_level > 0.3:
                issues.append("High noise level")
        
        elif analysis.content_type == ContentType.AUDIO and analysis.audio_features:
            features = analysis.audio_features
            
            if features.bitrate > 0 and features.bitrate < 128:
                issues.append("Low audio bitrate")
            
            if features.silence_ratio > 0.5:
                issues.append("High silence ratio")
        
        return issues
    
    async def _assess_risk(self, analysis: ContentAnalysis):
        """Assess content risk factors"""        try:
            risk_scores = {}
            
            # Basic risk assessment
            risk_scores['explicit_content'] = await self._assess_explicit_content_risk(analysis)
            risk_scores['copyright_risk'] = await self._assess_copyright_risk(analysis)
            risk_scores['brand_risk'] = await self._assess_brand_risk(analysis)
            risk_scores['legal_risk'] = await self._assess_legal_risk(analysis)
            risk_scores['reputation_risk'] = await self._assess_reputation_risk(analysis)
            
            # Calculate weighted overall risk score
            overall_risk = sum(
                score * self.risk_factors[factor]
                for factor, score in risk_scores.items()
            )
            
            analysis.risk_score = overall_risk
            analysis.risk_level = self._score_to_risk_level(overall_risk)
            
            # Identify specific risk factors
            analysis.risk_factors = self._identify_risk_factors(risk_scores)
            
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}")
            analysis.risk_score = 0.2
            analysis.risk_level = ContentRisk.SAFE
    
    async def _assess_explicit_content_risk(self, analysis: ContentAnalysis) -> float:
        """Assess explicit content risk"""        risk = 0.1  # Default low risk
        
        try:
            # Text-based explicit content detection
            if analysis.content_type == ContentType.TEXT and analysis.text_features:
                explicit_keywords = {
                    'adult', 'explicit', 'sexual', 'nude', 'porn', 'xxx',
                    'mature', 'nsfw', '18+', 'adult-only'
                }
                
                explicit_density = sum(
                    analysis.text_features.keyword_density.get(keyword, 0)
                    for keyword in explicit_keywords
                )
                
                risk += explicit_density * 5  # High multiplier for explicit content
            
            # File size anomalies (very large files might contain explicit content)
            if analysis.file_size > 500 * 1024 * 1024:  # 500MB
                risk += 0.1
            
        except Exception as e:
            logger.error(f"Explicit content risk assessment error: {str(e)}")
        
        return max(0.0, min(1.0, risk))
    
    async def _assess_copyright_risk(self, analysis: ContentAnalysis) -> float:
        """Assess copyright risk"""        risk = 0.1  # Default low risk
        
        try:
            # Check for copyright-related metadata
            if analysis.content_type in [ContentType.IMAGE, ContentType.AUDIO]:
                # High-quality content might be copyrighted
                if analysis.quality_score > 0.8:
                    risk += 0.2
            
            # Check text for copyright terms
            if analysis.content_type == ContentType.TEXT and analysis.text_features:
                copyright_terms = {
                    'copyright', '©', 'all rights reserved', 'trademark',
                    'proprietary', 'licensed', 'copyrighted'
                }
                
                copyright_density = sum(
                    analysis.text_features.keyword_density.get(term, 0)
                    for term in copyright_terms
                )
                
                risk += copyright_density * 2
            
        except Exception as e:
            logger.error(f"Copyright risk assessment error: {str(e)}")
        
        return max(0.0, min(1.0, risk))
    
    async def _assess_brand_risk(self, analysis: ContentAnalysis) -> float:
        """Assess brand risk"""        risk = 0.1  # Default low risk
        
        try:
            # Inverse of brand safety score
            brand_safety = await self._assess_brand_safety(analysis)
            risk = 1.0 - brand_safety
            
        except Exception as e:
            logger.error(f"Brand risk assessment error: {str(e)}")
        
        return max(0.0, min(1.0, risk))
    
    async def _assess_legal_risk(self, analysis: ContentAnalysis) -> float:
        """Assess legal risk"""        risk = 0.1  # Default low risk
        
        try:
            # Check for legal terms in text
            if analysis.content_type == ContentType.TEXT and analysis.text_features:
                legal_risk_terms = {
                    'illegal', 'lawsuit', 'litigation', 'defamation',
                    'slander', 'libel', 'violation', 'infringement'
                }
                
                legal_density = sum(
                    analysis.text_features.keyword_density.get(term, 0)
                    for term in legal_risk_terms
                )
                
                risk += legal_density * 3
            
        except Exception as e:
            logger.error(f"Legal risk assessment error: {str(e)}")
        
        return max(0.0, min(1.0, risk))
    
    async def _assess_reputation_risk(self, analysis: ContentAnalysis) -> float:
        """Assess reputation risk"""        risk = 0.1  # Default low risk
        
        try:
            # Negative sentiment can be reputation risk
            if analysis.content_type == ContentType.TEXT and analysis.text_features:
                if analysis.text_features.sentiment_score < -0.5:
                    risk += 0.3
                
                # Check for controversial topics
                controversial_terms = {
                    'scandal', 'controversy', 'criticized', 'backlash',
                    'problematic', 'offensive', 'inappropriate'
                }
                
                controversy_density = sum(
                    analysis.text_features.keyword_density.get(term, 0)
                    for term in controversial_terms
                )
                
                risk += controversy_density * 2
            
        except Exception as e:
            logger.error(f"Reputation risk assessment error: {str(e)}")
        
        return max(0.0, min(1.0, risk))
    
    def _score_to_risk_level(self, score: float) -> ContentRisk:
        """Convert risk score to risk level"""        if score >= 0.8:
            return ContentRisk.FORBIDDEN
        elif score >= 0.6:
            return ContentRisk.RESTRICTED
        elif score >= 0.4:
            return ContentRisk.SENSITIVE
        elif score >= 0.2:
            return ContentRisk.MODERATE
        else:
            return ContentRisk.SAFE
    
    def _identify_risk_factors(self, risk_scores: Dict[str, float]) -> List[str]:
        """Identify specific risk factors"""        factors = []
        
        threshold = 0.3  # Risk threshold
        
        if risk_scores.get('explicit_content', 0) > threshold:
            factors.append("Potential explicit content detected")
        
        if risk_scores.get('copyright_risk', 0) > threshold:
            factors.append("Potential copyright issues")
        
        if risk_scores.get('brand_risk', 0) > threshold:
            factors.append("Brand safety concerns")
        
        if risk_scores.get('legal_risk', 0) > threshold:
            factors.append("Potential legal issues")
        
        if risk_scores.get('reputation_risk', 0) > threshold:
            factors.append("Reputation risk factors")
        
        return factors
    
    async def _calculate_business_metrics(self, analysis: ContentAnalysis):
        """Calculate business-relevant metrics"""        try:
            # Engagement potential (already calculated in quality assessment)
            engagement_score = await self._assess_engagement_potential(analysis)
            analysis.engagement_potential = engagement_score
            
            # Monetization potential
            monetization_score = await self._calculate_monetization_potential(analysis)
            analysis.monetization_potential = monetization_score
            
            # Virality score
            virality_score = await self._calculate_virality_score(analysis)
            analysis.virality_score = virality_score
            
            # Brand safety score (already calculated)
            brand_safety_score = await self._assess_brand_safety(analysis)
            analysis.brand_safety_score = brand_safety_score
            
        except Exception as e:
            logger.error(f"Business metrics calculation error: {str(e)}")
    
    async def _calculate_monetization_potential(self, analysis: ContentAnalysis) -> float:
        """Calculate monetization potential"""        score = 0.5  # Default neutral score
        
        try:
            # Content type monetization potential
            type_scores = {
                ContentType.VIDEO: 1.0,   # Highest monetization potential
                ContentType.IMAGE: 0.8,   # High potential for sponsorships
                ContentType.AUDIO: 0.6,   # Podcast sponsorships
                ContentType.TEXT: 0.4,    # Blog monetization
                ContentType.DOCUMENT: 0.2,
                ContentType.UNKNOWN: 0.1
            }
            
            base_score = type_scores.get(analysis.content_type, 0.5)
            
            # Quality multiplier
            quality_multiplier = 1.0 + (analysis.quality_score - 0.5)  # 0.5 to 1.5 range
            
            # Brand safety multiplier
            brand_safety_multiplier = analysis.brand_safety_score
            
            score = base_score * quality_multiplier * brand_safety_multiplier
            
        except Exception as e:
            logger.error(f"Monetization potential calculation error: {str(e)}")
        
        return max(0.0, min(1.0, score))
    
    async def _calculate_virality_score(self, analysis: ContentAnalysis) -> float:
        """Calculate virality potential score"""        score = 0.5  # Default neutral score
        
        try:
            # Engagement is key for virality
            engagement_factor = analysis.engagement_potential
            
            # Content type virality potential
            type_multipliers = {
                ContentType.VIDEO: 1.2,   # Videos have highest viral potential
                ContentType.IMAGE: 1.0,
                ContentType.AUDIO: 0.8,
                ContentType.TEXT: 0.6,
                ContentType.DOCUMENT: 0.3,
                ContentType.UNKNOWN: 0.1
            }
            
            type_multiplier = type_multipliers.get(analysis.content_type, 1.0)
            
            # Quality factor
            quality_factor = analysis.quality_score
            
            # Emotional content tends to be more viral
            emotional_factor = 1.0
            if analysis.text_features:
                emotional_intensity = sum(analysis.text_features.emotion_scores.values())
                emotional_factor = 1.0 + min(0.5, emotional_intensity)  # Max 1.5 multiplier
            
            score = engagement_factor * type_multiplier * quality_factor * emotional_factor
            
        except Exception as e:
            logger.error(f"Virality score calculation error: {str(e)}")
        
        return max(0.0, min(1.0, score))
    
    async def _generate_similarity_hash(self, file_path: str, content_type: ContentType) -> str:
        """Generate similarity hash for content deduplication"""        try:
            if content_type == ContentType.IMAGE:
                # Use perceptual hashing for images
                image = Image.open(file_path)
                # Simplified perceptual hash (would use more advanced methods in production)
                image_resized = image.resize((8, 8), Image.Resampling.LANCZOS)
                image_gray = image_resized.convert('L')
                pixels = list(image_gray.getdata())
                avg_pixel = sum(pixels) / len(pixels)
                
                # Create binary hash
                hash_bits = [1 if pixel > avg_pixel else 0 for pixel in pixels]
                hash_string = ''.join(map(str, hash_bits))
                
                return hashlib.sha256(hash_string.encode()).hexdigest()[:32]
            
            elif content_type == ContentType.AUDIO:
                # Use audio fingerprinting
                y, sr = librosa.load(file_path, duration=30, sr=22050)  # First 30 seconds
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                mfcc_hash = hashlib.sha256(mfcc.tobytes()).hexdigest()[:32]
                
                return mfcc_hash
            
            elif content_type == ContentType.TEXT:
                # Use content-based hashing for text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Normalize text (remove whitespace, lowercase)
                normalized = re.sub(r'\s+', ' ', content.lower().strip())
                content_hash = hashlib.sha256(normalized.encode()).hexdigest()[:32]
                
                return content_hash
            
            else:
                # Fallback to file hash
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                return hashlib.sha256(file_content).hexdigest()[:32]
            
        except Exception as e:
            logger.error(f"Similarity hash generation error: {str(e)}")
            return hashlib.sha256(file_path.encode()).hexdigest()[:32]
    
    async def _ai_enhanced_analysis(self, analysis: ContentAnalysis):
        """Perform AI-enhanced analysis (placeholder for future AI integration)"""        try:
            # Placeholder for AI-powered analysis
            # In production, this would integrate with ML models for:
            # - Object detection in images
            # - Speech recognition in audio
            # - Natural language understanding in text
            # - Content classification
            # - Automated tagging
            
            # Mock AI analysis results
            analysis.ai_tags = self._generate_mock_ai_tags(analysis)
            analysis.ai_description = self._generate_mock_ai_description(analysis)
            analysis.ai_confidence = 0.85  # Mock confidence score
            
        except Exception as e:
            logger.error(f"AI enhanced analysis error: {str(e)}")
    
    def _generate_mock_ai_tags(self, analysis: ContentAnalysis) -> List[str]:
        """Generate mock AI tags based on content analysis"""        tags = []
        
        # Base tags on content type
        if analysis.content_type == ContentType.IMAGE:
            tags.extend(['visual_content', 'image'])
            if analysis.content_features:
                if analysis.content_features.brightness > 0.7:
                    tags.append('bright')
                if analysis.content_features.brightness < 0.3:
                    tags.append('dark')
                if analysis.content_features.contrast > 0.6:
                    tags.append('high_contrast')
        
        elif analysis.content_type == ContentType.AUDIO:
            tags.extend(['audio_content', 'sound'])
            if analysis.audio_features:
                if analysis.audio_features.tempo > 120:
                    tags.append('upbeat')
                if analysis.audio_features.tempo < 80:
                    tags.append('slow')
        
        elif analysis.content_type == ContentType.TEXT:
            tags.extend(['text_content', 'written'])
            if analysis.text_features:
                if analysis.text_features.sentiment_score > 0.3:
                    tags.append('positive')
                if analysis.text_features.sentiment_score < -0.3:
                    tags.append('negative')
        
        # Quality-based tags
        if analysis.quality_level == QualityLevel.EXCELLENT:
            tags.append('high_quality')
        elif analysis.quality_level == QualityLevel.POOR:
            tags.append('low_quality')
        
        # Business-relevant tags
        if analysis.engagement_potential > 0.7:
            tags.append('engaging')
        if analysis.monetization_potential > 0.7:
            tags.append('monetizable')
        if analysis.virality_score > 0.7:
            tags.append('viral_potential')
        
        return tags
    
    def _generate_mock_ai_description(self, analysis: ContentAnalysis) -> str:
        """Generate mock AI description"""        descriptions = {
            ContentType.IMAGE: f"Image content with {analysis.quality_level.value} quality",
            ContentType.AUDIO: f"Audio content with {analysis.quality_level.value} quality",
            ContentType.VIDEO: f"Video content with {analysis.quality_level.value} quality",
            ContentType.TEXT: f"Text content with {analysis.quality_level.value} quality",
            ContentType.DOCUMENT: f"Document with {analysis.quality_level.value} quality",
            ContentType.UNKNOWN: "Unknown content type"
        }
        
        base_description = descriptions.get(analysis.content_type, "Content")
        
        # Add business insights
        if analysis.engagement_potential > 0.7:
            base_description += " with high engagement potential"
        
        if analysis.risk_level != ContentRisk.SAFE:
            base_description += f" (risk level: {analysis.risk_level.value})"
        
        return base_description

# Export main classes
__all__ = [
    'ContentAnalyzer',
    'ContentAnalysis',
    'ContentType',
    'AnalysisLevel',
    'QualityLevel',
    'ContentRisk',
    'ContentFeatures',
    'AudioFeatures',
    'TextFeatures',
    'ImageAnalyzer',
    'AudioAnalyzer',
    'TextAnalyzer'
]
