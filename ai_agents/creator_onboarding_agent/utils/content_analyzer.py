"""Content Analyzer - Advanced Multi-Format Content Analysis System

Enterprise-grade content analysis with AI-powered quality assessment,
optimization recommendations, and intelligent categorization.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import mimetypes
import io

import numpy as np
import librosa
import cv2
from PIL import Image, ExifTags
import torch
from transformers import pipeline, AutoTokenizer, AutoModel
import spacy
from textstat import flesch_reading_ease, automated_readability_index

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ContentAnalysisError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ContentAnalysisError, ValidationError = globals().get('ContentAnalysisError, ValidationError', Exception)
from ...ml.content_models import ContentClassifier, QualityAnalyzer
from ...ml.audio_analyzer import AudioAnalyzer
from ...ml.image_analyzer import ImageAnalyzer
from ...ml.text_analyzer import TextAnalyzer
from ...utils.file_utils import FileUtils
from ...security.content_validator import ContentValidator

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """
Supported content types for analysis"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    UNKNOWN = "unknown"

class QualityLevel(Enum):
    """Content quality assessment levels"""

    POOR = "poor"           # 0.0 - 0.3
    FAIR = "fair"           # 0.3 - 0.5
    GOOD = "good"           # 0.5 - 0.7
    EXCELLENT = "excellent" # 0.7 - 0.9
    EXCEPTIONAL = "exceptional"  # 0.9 - 1.0

@dataclass
class ContentMetadata:
    """Comprehensive content metadata structure"""
    file_name: str
    file_size: int
    file_type: str
    mime_type: str
    checksum: str
    duration: Optional[float] = None  # For audio/video
    dimensions: Optional[Tuple[int, int]] = None  # For image/video
    resolution: Optional[str] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    camera_info: Dict[str, Any] = field(default_factory=dict)
    encoding_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentAnalysis:
    """
Comprehensive content analysis results"""
    content_id: str
    content_type: ContentType
    metadata: ContentMetadata
    
    # Quality Metrics
    overall_quality_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.FAIR
    technical_quality: Dict[str, float] = field(default_factory=dict)
    aesthetic_quality: Dict[str, float] = field(default_factory=dict)
    
    # Content Classification
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    
    # AI-Generated Insights
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    sentiment_score: float = 0.0
    complexity_score: float = 0.0
    originality_score: float = 0.0
    
    # Optimization Recommendations
    optimization_suggestions: List[str] = field(default_factory=list)
    seo_recommendations: List[str] = field(default_factory=list)
    engagement_predictions: Dict[str, float] = field(default_factory=dict)
    
    # Rights and Compliance
    copyright_flags: List[str] = field(default_factory=list)
    content_warnings: List[str] = field(default_factory=list)
    platform_suitability: Dict[str, bool] = field(default_factory=dict)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    analysis_version: str = "2.1.0"
    processing_time: float = 0.0

class ContentAnalyzer:
    """
    Advanced multi-format content analysis system with AI-powered insights.
    
    Core Capabilities:
    - Multi-format content analysis (audio, video, image, text)
    - Quality assessment with technical and aesthetic metrics
    - Intelligent content categorization and tagging
    - SEO optimization recommendations
    - Engagement prediction and optimization
    - Copyright and compliance checking
    - Platform-specific optimization suggestions
    - Real-time processing with batch support
    """
    
    def __init__(self):
        self.content_classifier = ContentClassifier()
        self.quality_analyzer = QualityAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.text_analyzer = TextAnalyzer()
        self.file_utils = FileUtils()
        self.content_validator = ContentValidator()
        
        # Initialize AI models
        self._initialize_ai_models()
        
        logger.info("ContentAnalyzer initialized successfully")
    
    def _initialize_ai_models(self):
        """Initialize AI models for content analysis."""
        try:
            # Text analysis models
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Image classification model
            self.image_classifier = pipeline(
                "image-classification",
                model="google/vit-base-patch16-224"
            )
            
            # Load spaCy for advanced text processing
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, using basic text processing")
                self.nlp = None
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
            # Initialize with fallback models
            self._initialize_fallback_models()
    
    def _initialize_fallback_models(self):
        """Initialize fallback models if primary models fail."""
        self.sentiment_analyzer = None
        self.image_classifier = None
        self.nlp = None
        logger.warning("Using fallback content analysis models")
    
    async def analyze_content(self, content: Union[str, bytes, Dict[str, Any]], 
                            creator_type: str = None,
                            analysis_options: Dict[str, bool] = None) -> ContentAnalysis:
        """
        Perform comprehensive content analysis with AI-powered insights.
        """
        start_time = datetime.utcnow()
        
        try:
            # Determine content type and prepare data
            content_type, processed_content = await self._prepare_content(content)
            
            # Extract metadata
            metadata = await self._extract_metadata(processed_content, content_type)
            
            # Create analysis object
            analysis = ContentAnalysis(
                content_id=hashlib.md5(str(processed_content).encode()).hexdigest()[:12],
                content_type=content_type,
                metadata=metadata
            )
            
            # Set analysis options
            options = analysis_options or {}
            default_options = {
                'quality_analysis': True,
                'categorization': True,
                'optimization': True,
                'compliance_check': True,
                'seo_analysis': True
            }
            options = {**default_options, **options}
            
            # Perform type-specific analysis
            if content_type == ContentType.AUDIO:
                await self._analyze_audio_content(analysis, processed_content, options)
            elif content_type == ContentType.IMAGE:
                await self._analyze_image_content(analysis, processed_content, options)
            elif content_type == ContentType.VIDEO:
                await self._analyze_video_content(analysis, processed_content, options)
            elif content_type == ContentType.TEXT:
                await self._analyze_text_content(analysis, processed_content, options)
            else:
                await self._analyze_generic_content(analysis, processed_content, options)
            
            # Generate overall quality score
            await self._calculate_overall_quality(analysis)
            
            # Generate optimization recommendations
            if options.get('optimization', True):
                await self._generate_optimization_recommendations(analysis, creator_type)
            
            # Perform compliance checks
            if options.get('compliance_check', True):
                await self._perform_compliance_checks(analysis)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            analysis.processing_time = processing_time
            
            logger.info(f"Content analysis completed in {processing_time:.2f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            raise ContentAnalysisError(f"Content analysis failed: {str(e)}")
    
    async def batch_analyze(self, content_items: List[Any], 
                          creator_type: str = None,
                          concurrent_limit: int = 5) -> List[ContentAnalysis]:
        """
        Perform batch content analysis with concurrency control.
        """
        try:
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            async def analyze_single(content_item):
                async with semaphore:
                    return await self.analyze_content(content_item, creator_type)
            
            # Process all items concurrently
            tasks = [analyze_single(item) for item in content_items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing item {i}: {str(result)}")
                else:
                    valid_results.append(result)
            
            logger.info(f"Batch analysis completed: {len(valid_results)}/{len(content_items)} successful")
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            raise ContentAnalysisError(f"Batch analysis failed: {str(e)}")
    
    async def _prepare_content(self, content: Union[str, bytes, Dict[str, Any]]) -> Tuple[ContentType, Any]:
        """Prepare and validate content for analysis."""
        try:
            # Handle different input types
            if isinstance(content, dict):
                # Content object with metadata
                content_data = content.get('data') or content.get('content')
                content_type_hint = content.get('type')
                file_path = content.get('file_path')
                
                if file_path:
                    # Load from file
                    with open(file_path, 'rb') as f:
                        content_data = f.read()
                    content_type = self._detect_content_type(file_path, content_data)
                elif content_type_hint:
                    content_type = ContentType(content_type_hint)
                else:
                    content_type = self._detect_content_type_from_data(content_data)
                
                return content_type, content_data
            
            elif isinstance(content, str):
                # Text content or file path
                if len(content) < 500 and ('/' in content or '\\' in content):
                    # Likely a file path
                    try:
                        with open(content, 'rb') as f:
                            content_data = f.read()
                        content_type = self._detect_content_type(content, content_data)
                        return content_type, content_data
                    except FileNotFoundError:
                        # Treat as text
                        return ContentType.TEXT, content
                else:
                    # Text content
                    return ContentType.TEXT, content
            
            elif isinstance(content, bytes):
                # Binary content
                content_type = self._detect_content_type_from_data(content)
                return content_type, content
            
            else:
                raise ValidationError(f"Unsupported content type: {type(content)}")
                
        except Exception as e:
            logger.error(f"Error preparing content: {str(e)}")
            raise ValidationError(f"Content preparation failed: {str(e)}")
    
    def _detect_content_type(self, file_path: str, content_data: bytes = None) -> ContentType:
        """Detect content type from file path and data."""
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type:
            if mime_type.startswith('audio/'):
                return ContentType.AUDIO
            elif mime_type.startswith('video/'):
                return ContentType.VIDEO
            elif mime_type.startswith('image/'):
                return ContentType.IMAGE
            elif mime_type.startswith('text/'):
                return ContentType.TEXT
            elif mime_type in ['application/pdf', 'application/msword']:
                return ContentType.DOCUMENT
        
        # Fallback to extension-based detection
        extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
        
        audio_extensions = ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg']
        video_extensions = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
        text_extensions = ['txt', 'md', 'html', 'csv', 'json', 'xml']
        document_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx']
        
        if extension in audio_extensions:
            return ContentType.AUDIO
        elif extension in video_extensions:
            return ContentType.VIDEO
        elif extension in image_extensions:
            return ContentType.IMAGE
        elif extension in text_extensions:
            return ContentType.TEXT
        elif extension in document_extensions:
            return ContentType.DOCUMENT
        
        return ContentType.UNKNOWN
    
    def _detect_content_type_from_data(self, content_data: Any) -> ContentType:
        """
Detect content type from data analysis."""
        if isinstance(content_data, str):
            return ContentType.TEXT
        elif isinstance(content_data, bytes):
            # Check magic bytes for common formats
            if content_data.startswith(b'\xff\xfb') or content_data.startswith(b'ID3'):
                return ContentType.AUDIO
            elif content_data.startswith(b'\x89PNG'):
                return ContentType.IMAGE
            elif content_data.startswith(b'\xff\xd8\xff'):
                return ContentType.IMAGE
            elif content_data.startswith(b'GIF8'):
                return ContentType.IMAGE
            elif b'ftypmp4' in content_data[:50]:
                return ContentType.VIDEO
        
        return ContentType.UNKNOWN
    
    async def _extract_metadata(self, content_data: Any, content_type: ContentType) -> ContentMetadata:
        """
Extract comprehensive metadata from content."""
        metadata = ContentMetadata(
            file_name="unknown",
            file_size=len(content_data) if isinstance(content_data, bytes) else len(str(content_data)),
            file_type=content_type.value,
            mime_type="application/octet-stream",
            checksum=hashlib.md5(str(content_data).encode() if isinstance(content_data, str) else content_data).hexdigest()
        )
        
        try:
            if content_type == ContentType.IMAGE and isinstance(content_data, bytes):
                # Extract image metadata
                image = Image.open(io.BytesIO(content_data))
                metadata.dimensions = image.size
                metadata.resolution = f"{image.size[0]}x{image.size[1]}"
                
                # Extract EXIF data
                if hasattr(image, '_getexif') and image._getexif():
                    exif = image._getexif()
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        metadata.camera_info[tag] = str(value)
            
            elif content_type == ContentType.AUDIO and isinstance(content_data, bytes):
                # Extract audio metadata
                try:
                    audio_data = io.BytesIO(content_data)
                    y, sr = librosa.load(audio_data, sr=None)
                    metadata.duration = len(y) / sr
                    metadata.sample_rate = sr
                except Exception:
                    pass
            
        except Exception as e:
            logger.warning(f"Could not extract detailed metadata: {str(e)}")
        
        return metadata
    
    async def _analyze_audio_content(self, analysis: ContentAnalysis, 
                                   content_data: bytes, options: Dict[str, bool]) -> None:
        """Analyze audio content with specialized metrics."""
        try:
            # Load audio data
            audio_io = io.BytesIO(content_data)
            y, sr = librosa.load(audio_io, sr=None)
            
            # Technical quality analysis
            analysis.technical_quality.update({
                'signal_to_noise_ratio': self._calculate_snr(y),
                'dynamic_range': self._calculate_dynamic_range(y),
                'frequency_balance': self._analyze_frequency_balance(y, sr),
                'clipping_detection': self._detect_clipping(y),
                'silence_ratio': self._calculate_silence_ratio(y)
            })
            
            # Musical analysis
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            analysis.tags.extend([
                f"tempo_{int(tempo)}bpm",
                f"energy_{self._calculate_energy_level(y)}",
                f"brightness_{np.mean(spectral_centroid):.1f}"
            ])
            
            # Genre classification (simplified)
            genre = await self._classify_audio_genre(y, sr)
            if genre:
                analysis.genres.append(genre)
            
            # Generate audio-specific recommendations
            if analysis.technical_quality['signal_to_noise_ratio'] < 0.7:
                analysis.optimization_suggestions.append("Reduce background noise and improve recording environment")
            
            if analysis.technical_quality['clipping_detection'] > 0.1:
                analysis.optimization_suggestions.append("Reduce input gain to prevent audio clipping")
            
        except Exception as e:
            logger.error(f"Error analyzing audio content: {str(e)}")
            analysis.content_warnings.append("Audio analysis partially failed")
    
    async def _analyze_image_content(self, analysis: ContentAnalysis, 
                                   content_data: bytes, options: Dict[str, bool]) -> None:
        """Analyze image content with computer vision."""
        try:
            # Load image
            image = Image.open(io.BytesIO(content_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Technical quality analysis
            img_array = np.array(image)
            
            analysis.technical_quality.update({
                'resolution_score': self._score_resolution(image.size),
                'sharpness_score': self._calculate_sharpness(img_array),
                'brightness_score': self._analyze_brightness(img_array),
                'contrast_score': self._analyze_contrast(img_array),
                'color_balance': self._analyze_color_balance(img_array)
            })
            
            # Use AI for image classification if available
            if self.image_classifier:
                try:
                    classifications = self.image_classifier(image, top_k=5)
                    for cls in classifications:
                        if cls['score'] > 0.1:
                            analysis.categories.append(cls['label'])
                            if cls['score'] > 0.3:
                                analysis.tags.append(cls['label'].lower().replace(' ', '_'))
                except Exception:
                    logger.warning("Image classification failed, using fallback")
            
            # Aesthetic analysis
            analysis.aesthetic_quality.update({
                'composition_score': self._analyze_composition(img_array),
                'color_harmony': self._analyze_color_harmony(img_array),
                'visual_balance': self._analyze_visual_balance(img_array)
            })
            
            # Generate image-specific recommendations
            if analysis.technical_quality['sharpness_score'] < 0.6:
                analysis.optimization_suggestions.append("Improve image sharpness and focus")
            
            if analysis.technical_quality['brightness_score'] < 0.4:
                analysis.optimization_suggestions.append("Adjust exposure and lighting")
            
        except Exception as e:
            logger.error(f"Error analyzing image content: {str(e)}")
            analysis.content_warnings.append("Image analysis partially failed")
    
    async def _analyze_video_content(self, analysis: ContentAnalysis, 
                                   content_data: bytes, options: Dict[str, bool]) -> None:
        """Analyze video content with frame-by-frame analysis."""
        try:
            # For now, treat as image analysis of first frame
            # In production, this would include temporal analysis
            
            # Extract first frame for analysis
            temp_file = io.BytesIO(content_data)
            cap = cv2.VideoCapture()
            
            # Basic video properties
            analysis.tags.append("video_content")
            analysis.categories.append("video")
            
            # Placeholder video-specific analysis
            analysis.technical_quality.update({
                'video_quality': 0.7,  # Placeholder
                'audio_sync': 0.9,     # Placeholder
                'frame_rate': 30,      # Placeholder
                'compression_quality': 0.8  # Placeholder
            })
            
            analysis.optimization_suggestions.append("Optimize video compression for web delivery")
            
        except Exception as e:
            logger.error(f"Error analyzing video content: {str(e)}")
            analysis.content_warnings.append("Video analysis partially failed")
    
    async def _analyze_text_content(self, analysis: ContentAnalysis, 
                                  content_data: str, options: Dict[str, bool]) -> None:
        """Analyze text content with NLP and readability metrics."""
        try:
            text = content_data.strip()
            
            # Basic text metrics
            word_count = len(text.split())
            char_count = len(text)
            sentence_count = text.count('.') + text.count('!') + text.count('?')
            
            analysis.tags.extend([
                f"words_{word_count}",
                f"sentences_{sentence_count}",
                f"length_{self._categorize_text_length(word_count)}"
            ])
            
            # Readability analysis
            try:
                flesch_score = flesch_reading_ease(text)
                ari_score = automated_readability_index(text)
                
                analysis.technical_quality.update({
                    'readability_flesch': flesch_score / 100,  # Normalize to 0-1
                    'readability_ari': max(0, min(1, (20 - ari_score) / 20)),  # Normalize
                    'complexity_score': self._calculate_text_complexity(text)
                })
                
                # Readability recommendations
                if flesch_score < 60:
                    analysis.optimization_suggestions.append("Simplify language for better readability")
                
            except Exception:
                logger.warning("Readability analysis failed")
            
            # Sentiment analysis
            if self.sentiment_analyzer:
                try:
                    sentiment_result = self.sentiment_analyzer(text[:512])  # Limit for model
                    sentiment_label = sentiment_result[0]['label'].lower()
                    sentiment_score = sentiment_result[0]['score']
                    
                    # Convert to -1 to 1 scale
                    if 'positive' in sentiment_label:
                        analysis.sentiment_score = sentiment_score
                    elif 'negative' in sentiment_label:
                        analysis.sentiment_score = -sentiment_score
                    else:
                        analysis.sentiment_score = 0.0
                    
                    analysis.tags.append(f"sentiment_{sentiment_label}")
                    
                except Exception:
                    logger.warning("Sentiment analysis failed")
            
            # Keyword extraction using spaCy
            if self.nlp:
                try:
                    doc = self.nlp(text)
                    
                    # Extract entities
                    entities = [ent.text.lower() for ent in doc.ents if len(ent.text) > 2]
                    analysis.keywords.extend(entities[:10])  # Top 10
                    
                    # Extract noun phrases as themes
                    themes = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 3]
                    analysis.themes.extend(themes[:10])  # Top 10
                    
                except Exception:
                    logger.warning("NLP analysis failed")
            
            # SEO recommendations
            if options.get('seo_analysis', True):
                analysis.seo_recommendations.extend([
                    "Add relevant keywords naturally throughout the text",
                    "Include engaging headings and subheadings",
                    "Optimize text length for your target platform"
                ])
            
        except Exception as e:
            logger.error(f"Error analyzing text content: {str(e)}")
            analysis.content_warnings.append("Text analysis partially failed")
    
    async def _analyze_generic_content(self, analysis: ContentAnalysis, 
                                     content_data: Any, options: Dict[str, bool]) -> None:
        """Analyze generic/unknown content types."""
        analysis.tags.append("unknown_format")
        analysis.categories.append("generic")
        analysis.optimization_suggestions.append("Consider converting to a more standard format for better analysis")
    
    async def _calculate_overall_quality(self, analysis: ContentAnalysis) -> None:
        """Calculate overall quality score from technical and aesthetic metrics."""
        technical_scores = list(analysis.technical_quality.values())
        aesthetic_scores = list(analysis.aesthetic_quality.values())
        
        all_scores = technical_scores + aesthetic_scores
        
        if all_scores:
            # Weight technical quality more heavily
            technical_weight = 0.7
            aesthetic_weight = 0.3
            
            avg_technical = sum(technical_scores) / len(technical_scores) if technical_scores else 0.5
            avg_aesthetic = sum(aesthetic_scores) / len(aesthetic_scores) if aesthetic_scores else 0.5
            
            analysis.overall_quality_score = (
                avg_technical * technical_weight + 
                avg_aesthetic * aesthetic_weight
            )
        else:
            analysis.overall_quality_score = 0.5  # Default
        
        # Determine quality level
        score = analysis.overall_quality_score
        if score >= 0.9:
            analysis.quality_level = QualityLevel.EXCEPTIONAL
        elif score >= 0.7:
            analysis.quality_level = QualityLevel.EXCELLENT
        elif score >= 0.5:
            analysis.quality_level = QualityLevel.GOOD
        elif score >= 0.3:
            analysis.quality_level = QualityLevel.FAIR
        else:
            analysis.quality_level = QualityLevel.POOR
    
    async def _generate_optimization_recommendations(self, analysis: ContentAnalysis, 
                                                   creator_type: str = None) -> None:
        """
Generate intelligent optimization recommendations."""
        recommendations = analysis.optimization_suggestions.copy()
        
        # Quality-based recommendations
        if analysis.overall_quality_score < 0.6:
            recommendations.append("Focus on improving overall content quality")
        
        # Type-specific recommendations
        if creator_type == 'musician' and analysis.content_type == ContentType.AUDIO:
            if analysis.technical_quality.get('dynamic_range', 1.0) < 0.5:
                recommendations.append("Increase dynamic range for more engaging audio")
        
        elif creator_type == 'photographer' and analysis.content_type == ContentType.IMAGE:
            if analysis.technical_quality.get('composition_score', 1.0) < 0.6:
                recommendations.append("Apply rule of thirds and other composition techniques")
        
        # Platform-specific recommendations
        analysis.platform_suitability.update({
            'instagram': analysis.content_type in [ContentType.IMAGE, ContentType.VIDEO],
            'youtube': analysis.content_type in [ContentType.VIDEO, ContentType.AUDIO],
            'spotify': analysis.content_type == ContentType.AUDIO,
            'tiktok': analysis.content_type == ContentType.VIDEO,
            'blog': analysis.content_type in [ContentType.TEXT, ContentType.IMAGE]
        })
        
        # Engagement predictions (simplified)
        base_engagement = analysis.overall_quality_score * 0.1
        analysis.engagement_predictions = {
            'instagram': base_engagement * 1.2 if analysis.content_type == ContentType.IMAGE else base_engagement * 0.8,
            'youtube': base_engagement * 1.5 if analysis.content_type == ContentType.VIDEO else base_engagement * 0.6,
            'tiktok': base_engagement * 2.0 if analysis.content_type == ContentType.VIDEO else base_engagement * 0.3
        }
        
        analysis.optimization_suggestions = list(set(recommendations))  # Remove duplicates
    
    async def _perform_compliance_checks(self, analysis: ContentAnalysis) -> None:
        """Perform content compliance and safety checks."""
        # Basic compliance checks
        content_warnings = []
        
        # Check for potential copyright issues (simplified)
        if 'music' in analysis.tags and analysis.content_type == ContentType.AUDIO:
            if analysis.originality_score < 0.7:
                analysis.copyright_flags.append("Potential similarity to existing music detected")
        
        # Content safety checks (placeholder)
        if analysis.sentiment_score < -0.8:
            content_warnings.append("Very negative sentiment detected")
        
        analysis.content_warnings.extend(content_warnings)
    
    # Helper methods for various calculations
    def _calculate_snr(self, audio_data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio for audio."""
        try:
            # Simple SNR calculation
            signal_power = np.mean(audio_data ** 2)
            noise_power = np.var(audio_data) * 0.1  # Simplified
            snr = signal_power / (noise_power + 1e-10)
            return min(1.0, snr / 100)  # Normalize
        except:
            return 0.5
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """
Calculate dynamic range of audio."""
        try:
            peak = np.max(np.abs(audio_data))
            rms = np.sqrt(np.mean(audio_data ** 2))
            dynamic_range = peak / (rms + 1e-10)
            return min(1.0, dynamic_range / 10)  # Normalize
        except:
            return 0.5
    
    def _analyze_frequency_balance(self, audio_data: np.ndarray, sr: int) -> float:
        """
Analyze frequency balance in audio."""
        try:
            # Simple frequency balance analysis
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(fft), 1/sr)
            
            # Analyze low, mid, high frequency content
            low_energy = np.mean(np.abs(fft[(freqs > 20) & (freqs < 250)]))
            mid_energy = np.mean(np.abs(fft[(freqs > 250) & (freqs < 4000)]))
            high_energy = np.mean(np.abs(fft[(freqs > 4000) & (freqs < 20000)]))
            
            # Calculate balance score
            total_energy = low_energy + mid_energy + high_energy + 1e-10
            balance_score = 1.0 - np.std([low_energy, mid_energy, high_energy]) / total_energy
            
            return max(0.0, min(1.0, balance_score))
        except:
            return 0.5
    
    def _detect_clipping(self, audio_data: np.ndarray) -> float:
        """
Detect audio clipping."""
        try:
            threshold = 0.99
            clipped_samples = np.sum(np.abs(audio_data) >= threshold)
            clipping_ratio = clipped_samples / len(audio_data)
            return clipping_ratio
        except:
            return 0.0
    
    def _calculate_silence_ratio(self, audio_data: np.ndarray) -> float:
        """
Calculate silence ratio in audio."""
        try:
            threshold = 0.01
            silent_samples = np.sum(np.abs(audio_data) < threshold)
            silence_ratio = silent_samples / len(audio_data)
            return silence_ratio
        except:
            return 0.0
    
    def _calculate_energy_level(self, audio_data: np.ndarray) -> str:
        """
Calculate energy level category."""
        try:
            energy = np.mean(audio_data ** 2)
            if energy > 0.1:
                return "high"
            elif energy > 0.01:
                return "medium"
            else:
                return "low"
        except:
            return "unknown"
    
    async def _classify_audio_genre(self, audio_data: np.ndarray, sr: int) -> str:
        """Classify audio genre (simplified)."""
        try:
            # Extract basic features for genre classification
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))
            
            # Simple rule-based classification
            if tempo > 140 and spectral_centroid > 2000:
                return "electronic"
            elif tempo > 120:
                return "pop"
            elif spectral_centroid < 1000:
                return "classical"
            else:
                return "acoustic"
        except:
            return "unknown"
    
    def _score_resolution(self, dimensions: Tuple[int, int]) -> float:
        """Score image resolution quality."""
        width, height = dimensions
        total_pixels = width * height
        
        # Resolution quality thresholds
        if total_pixels >= 8000000:  # 8MP+
            return 1.0
        elif total_pixels >= 2000000:  # 2MP+
            return 0.8
        elif total_pixels >= 1000000:  # 1MP+
            return 0.6
        elif total_pixels >= 500000:   # 0.5MP+
            return 0.4
        else:
            return 0.2
    
    def _calculate_sharpness(self, img_array: np.ndarray) -> float:
        """
Calculate image sharpness using Laplacian variance."""
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(img_array.shape) == 3 else img_array
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            # Normalize to 0-1 range
            return min(1.0, laplacian_var / 1000)
        except:
            return 0.5
    
    def _analyze_brightness(self, img_array: np.ndarray) -> float:
        """
Analyze image brightness."""
        try:
            # Convert to grayscale and calculate mean brightness
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            brightness = np.mean(gray) / 255.0
            
            # Optimal brightness is around 0.4-0.6
            if 0.4 <= brightness <= 0.6:
                return 1.0
            elif 0.2 <= brightness <= 0.8:
                return 0.8
            else:
                return 0.4
        except:
            return 0.5
    
    def _analyze_contrast(self, img_array: np.ndarray) -> float:
        """
Analyze image contrast."""
        try:
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            contrast = np.std(gray) / 255.0
            return min(1.0, contrast * 4)  # Scale appropriately
        except:
            return 0.5
    
    def _analyze_color_balance(self, img_array: np.ndarray) -> float:
        """
Analyze color balance in image."""
        try:
            if len(img_array.shape) != 3:
                return 1.0  # Grayscale images are balanced by definition
            
            # Calculate mean values for each channel
            r_mean = np.mean(img_array[:, :, 0])
            g_mean = np.mean(img_array[:, :, 1])
            b_mean = np.mean(img_array[:, :, 2])
            
            # Calculate color balance score
            color_diff = np.std([r_mean, g_mean, b_mean])
            balance_score = max(0.0, 1.0 - color_diff / 128)
            
            return balance_score
        except:
            return 0.5
    
    def _analyze_composition(self, img_array: np.ndarray) -> float:
        """
Analyze image composition (simplified)."""
        # Placeholder implementation - would use more sophisticated analysis
        return 0.7
    
    def _analyze_color_harmony(self, img_array: np.ndarray) -> float:
        """
Analyze color harmony in image."""
        # Placeholder implementation - would use color theory analysis
        return 0.6
    
    def _analyze_visual_balance(self, img_array: np.ndarray) -> float:
        """
Analyze visual balance in image."""
        # Placeholder implementation - would use visual weight analysis
        return 0.6
    
    def _categorize_text_length(self, word_count: int) -> str:
        """
Categorize text length."""
        if word_count < 50:
            return "short"
        elif word_count < 300:
            return "medium"
        elif word_count < 1000:
            return "long"
        else:
            return "very_long"
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score."""
        try:
            # Simple complexity metrics
            avg_word_length = np.mean([len(word) for word in text.split()])
            sentence_length = len(text.split()) / (text.count('.') + text.count('!') + text.count('?') + 1)
            
            # Normalize to 0-1
            word_complexity = min(1.0, (avg_word_length - 3) / 7)  # 3-10 char words
            sentence_complexity = min(1.0, (sentence_length - 5) / 20)  # 5-25 words per sentence
            
            return (word_complexity + sentence_complexity) / 2
        except:
            return 0.5
